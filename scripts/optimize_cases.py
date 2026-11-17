#!/usr/bin/env python3
"""Make fast, native, responsive, *original-order* Behance galleries.

We keep original downloaded full-resolution files unchanged and generate adaptive
high-quality WebP renditions. The browser requests only a suitable rendition for
images near the viewport, rather than loading all PNGs in one tall iframe.
Vimeo embeds use the original video ID and unlisted-video hash when present.
"""
from __future__ import annotations
import html, json, re, urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets' / 'behance'
CONTENT = ROOT / 'content'
IMAGE_SIZES = (960, 1920, 2880)
WEBP_QUALITY = 92


def reencode(original: Path) -> tuple[list[tuple[int, str]], tuple[int, int]]:
    """Preserve source pixels in original PNG while creating retina-ready renditions."""
    with Image.open(original) as source:
        image = ImageOps.exif_transpose(source)
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
        if image.mode == 'RGBA' and image.getchannel('A').getextrema() == (255, 255):
            image = image.convert('RGB')
        width, height = image.size
        if width <= 0 or height <= 0:
            raise ValueError(f'Invalid dimensions: {original}')
        outputs = []
        destination = original.parent / 'optimized'
        destination.mkdir(exist_ok=True)
        chosen = []
        for target in IMAGE_SIZES:
            size = min(width, target)
            if chosen and size - chosen[-1] < .1 * size:
                chosen[-1] = size
            elif size not in chosen:
                chosen.append(size)
        for target_width in chosen:
            path = destination / f'{original.stem}-{target_width}.webp'
            if not path.exists() or path.stat().st_size < 100:
                resized = image if target_width == width else image.resize(
                    (target_width, max(1, round(height * target_width / width))), Image.Resampling.LANCZOS
                )
                resized.save(path, 'WEBP', quality=WEBP_QUALITY, method=2, exact=True)
            outputs.append((target_width, path.relative_to(ROOT).as_posix()))
    return outputs, (width, height)


def clean_embed(url: str) -> str | None:
    """Keep only the trusted, exact Vimeo player with the source's unlisted hash."""
    url = html.unescape(url)
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.netloc != 'player.vimeo.com':
        return None
    if not re.fullmatch(r'/video/\d{4,13}', parsed.path):
        return None
    args = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=False))
    allowed = {'h': args['h']} if re.fullmatch(r'[0-9a-fA-F]{6,32}', args.get('h', '')) else {}
    allowed.update({'autoplay':'1','loop':'1','muted':'1','controls':'1','playsinline':'1','title':'0','byline':'0','portrait':'0'})
    return urllib.parse.urlunsplit(('https','player.vimeo.com',parsed.path,urllib.parse.urlencode(allowed),''))


def optimize_project(slug: str, page: Path, rendered_index: dict) -> dict:
    source = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
    main = source.find('main')
    if not main:
        raise ValueError(f'No original presentation modules in {page}')
    body_bg = '#fff'
    original_styles = source.find('style')
    if original_styles:
        match = re.search(r'body\s*\{[^}]*background\s*:\s*(#[\da-fA-F]{3,8})', original_styles.get_text(), re.S)
        if match:
            body_bg = match.group(1)

    blocks = []
    original_count = 0
    has_video = False
    index = 0

    def image_html(tag) -> str:
        nonlocal original_count, index
        src = tag.get('src', '')
        if not src or '/' in Path(src).name or Path(src).suffix.lower() not in ('.png','.jpg','.jpeg','.webp','.gif'):
            raise ValueError(f'Unsupported source image: {src}')
        original = page.parent / Path(src).name
        if not original.is_file():
            raise FileNotFoundError(original)
        if str(original) not in rendered_index:
            rendered_index[str(original)] = reencode(original)
        options, (width, height) = rendered_index[str(original)]
        srcset = ', '.join(f'{html.escape(asset,quote=True)} {pixels}w' for pixels, asset in options)
        default_src = min(options, key=lambda option: abs(option[0] - 1920))[1]
        alt = f'{slug.replace("-", " ")} — visual {index + 1}'
        original_count += 1
        index += 1
        loading = 'eager' if index == 1 else 'lazy'
        priority = 'high' if index == 1 else 'auto'
        return (
            f'<a class="case-zoom" href="{html.escape(original.relative_to(ROOT).as_posix(),quote=True)}" '
            f'data-zoom aria-label="View original image in full resolution">'
            f'<img src="{html.escape(default_src,quote=True)}" srcset="{srcset}" '
            f'sizes="(max-width:1400px) 100vw, 1400px" width="{width}" height="{height}" '
            f'alt="{html.escape(alt,quote=True)}" loading="{loading}" fetchpriority="{priority}" '
            f'decoding="async"></a>'
        )

    for module in main.find_all(recursive=False):
        classes = module.get('class') or []
        if 'slide' in classes:
            img = module.find('img')
            if img:
                blocks.append(f'<figure class="case-slide">{image_html(img)}</figure>')
        elif 'row' in classes:
            imgs = module.find_all('img')
            if imgs:
                blocks.append('<div class="case-image-row">'+''.join(image_html(img) for img in imgs)+'</div>')
        elif 'embed' in classes:
            a = module.find('a', href=True)
            url = clean_embed(a['href']) if a else None
            if url:
                has_video = True
                blocks.append(
                    '<div class="case-video">'
                    f'<iframe title="{html.escape(slug)} — video" src="{html.escape(url,quote=True)}" '
                    'loading="lazy" referrerpolicy="strict-origin-when-cross-origin" '
                    'allow="autoplay; fullscreen; picture-in-picture; encrypted-media" allowfullscreen></iframe>'
                    '</div>'
                )
        elif 'text' in classes:
            txt = module.get_text('\n', strip=True)
            if txt:
                blocks.append(f'<div class="case-original-text">{html.escape(txt)}</div>')
        elif 'caption' in classes:
            txt = module.get_text(' ', strip=True)
            if txt:
                blocks.append(f'<div class="case-original-caption">{html.escape(txt)}</div>')
    if original_count < 1:
        raise ValueError(f'No source images found for {slug}')
    if slug == 'bean-road' and not has_video:
        raise ValueError('Bean Road original Vimeo video is missing')

    return {
        'background': body_bg,
        'html': ''.join(blocks),
        'imageCount': original_count,
        'hasVideo': has_video,
        'source': 'behance-archive',
    }


def build() -> dict:
    manifest_path = CONTENT / 'behance-imports.json'
    data = json.loads(manifest_path.read_text())
    results = {}
    processed = {}
    for slug, entry in data.items():
        p = ROOT / entry['page']
        if p.is_file():
            results[slug] = optimize_project(slug, p, processed)
    CONTENT.mkdir(exist_ok=True)
    (CONTENT / 'case-pages.js').write_text(
        'window.PORTFOLIO_CASE_PAGES = '+json.dumps(results, ensure_ascii=False, separators=(',',':'))+';\n',
        encoding='utf-8',
    )
    print('Optimized',len(results),'case studies:',sum(x['imageCount'] for x in results.values()),'images;',
          sum(x['hasVideo'] for x in results.values()),'video(s).', flush=True)
    return results


if __name__ == '__main__':
    build()
