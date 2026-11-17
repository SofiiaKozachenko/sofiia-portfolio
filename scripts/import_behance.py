#!/usr/bin/env python3
"""Import an owner's public Behance projects into self-contained local HTML cases.
Requires Python >=3.12 and `python3 -m pip install behance-dl==0.3.0`.
Only handles public Behance gallery URLs, no tokens or private data.
"""
from __future__ import annotations
import argparse, datetime, json, os, re, shutil, subprocess, sys, tempfile, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'behance'; COVERS=ROOT/'assets'/'covers'; CONTENT=ROOT/'content'
KNOWN={
'exowave':('257379719','https://www.behance.net/gallery/257379719/ExoWave-Cosmetology-brand'),
'lumus':('250232993','https://www.behance.net/gallery/250232993/LUMUS-Designer-eyewear-brand'),
'woody-the-wizard':('238164279','https://www.behance.net/gallery/238164279/Woody-the-Wizard-Energy-Drink-Design'),
'bean-road':('227566159','https://www.behance.net/gallery/227566159/Coffee-shop-Bean-Road'),
'formiture':('181287549','https://www.behance.net/gallery/181287549/Formiture-E-commerce'),
}
DEFAULT_COVERS={
'exowave':'https://mir-s3-cdn-cf.behance.net/projects/808/a6aa6d257379719.Y3JvcCwxMDQwLDgxNCwxODgsMjMx.png',
'lumus':'https://mir-s3-cdn-cf.behance.net/projects/808/b9faee250232993.Y3JvcCwzMzY3LDI2MzQsMCww.png',
'woody-the-wizard':'https://mir-s3-cdn-cf.behance.net/projects/808/3ec395238164279.Y3JvcCwzMzY3LDI2MzQsMCww.png',
'bean-road':'https://mir-s3-cdn-cf.behance.net/projects/808/417f5e227566159.Y3JvcCwzODM1LDMwMDAsODUsMA.png',
'formiture':'https://mir-s3-cdn-cf.behance.net/projects/808/011888181287549.Y3JvcCwxNDAyLDEwOTYsMCwyNw.png',
}
def valid_url(url):
    p=urllib.parse.urlparse(url)
    if p.scheme!='https' or p.hostname not in ('www.behance.net','behance.net'):
        raise ValueError('Public HTTPS links to behance.net only')
    m=re.match(r'^/gallery/(\d{5,12})(?:/[^/]*)?/?$',p.path)
    if not m: raise ValueError('Expected https://www.behance.net/gallery/PROJECT_ID/TITLE')
    return m.group(1)
def slugify(name):
    name=re.sub('[^a-z0-9-]+','-',name.lower()).strip('-')
    if not re.fullmatch('[a-z0-9][a-z0-9-]{1,70}',name):raise ValueError('Use a simple English slug, e.g. new-brand')
    return name

def read_json(path,default):
    if not path.exists():return default
    try:return json.loads(path.read_text(encoding='utf-8'))
    except (ValueError,OSError):return default

def write_js(name,var,data):
    temp=CONTENT/(name+'.tmp')
    temp.write_text(f'window.{var} = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
    temp.replace(CONTENT/name)

def cover_candidates(obj):
    """Get cover candidates, not gallery images, from Behance's own project payload."""
    found=[]
    def walk(value,key='',depth=0):
        if depth>15:return
        if isinstance(value,dict):
            for k,v in value.items(): walk(v,str(k),depth+1)
        elif isinstance(value,list):
            for v in value: walk(v,key,depth+1)
        elif isinstance(value,str):
            u=value.replace('\\/','/')
            p=urllib.parse.urlparse(u)
            if p.scheme!='https' or not p.hostname or not p.hostname.endswith('.behance.net'):
                return
            if not any(ext in p.path.lower() for ext in ('.png','.jpg','.jpeg','.webp')):return
            key_l=key.lower()
            if '/projects/' not in p.path and not any(k in key_l for k in ('cover','thumb')):return
            score=0
            if 'cover' in key_l or 'covers' in key_l:score+=400
            if 'image' in key_l or 'source' in key_l:score+=100
            for size in (3840,2800,2024,1920,1600,1400,1200,808,404):
                if f'/{size}/' in u or f'max_{size}' in u: score+=int(size/10);break
            found.append((score,u))
    walk(obj)
    return [url for _,url in sorted(set(found),reverse=True)]

def image_dimensions(data):
    try:
        from PIL import Image
        import io
        with Image.open(io.BytesIO(data)) as im:
            im.verify()
        with Image.open(io.BytesIO(data)) as im:
            return im.size
    except Exception:return (0,0)

def get_cover(slug,project):
    """Save a real Behance cover, picking the highest-resolution original crop available."""
    candidates=cover_candidates(project)
    if slug in DEFAULT_COVERS:
        base=DEFAULT_COVERS[slug]
        # The 808 variant is only a thumbnail. Prefer actual large crop if CDN provides it.
        for size in ('max_2800','max_2024','1400','max_1200','808'):
            candidates.append(base.replace('/projects/808/',f'/projects/{size}/'))
    COVERS.mkdir(parents=True,exist_ok=True)
    best=None
    for url in dict.fromkeys(candidates[:28]):
        p=urllib.parse.urlparse(url)
        if not(p.hostname and p.hostname.endswith('.behance.net')):continue
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/*'})
            with urllib.request.urlopen(req,timeout=18) as resp:
                if not resp.headers.get('Content-Type','').startswith('image/'):continue
                data=resp.read(18*1024*1024)
            if len(data)<10000:continue
            if data.startswith(b'\xff\xd8\xff'):ext='.jpg'
            elif data.startswith(b'\x89PNG'):ext='.png'
            elif data.startswith(b'RIFF') and b'WEBP' in data[:16]:ext='.webp'
            else:continue
            w,h=image_dimensions(data)
            if w<700 or h<380: continue
            score=(w*h, len(data))
            if best is None or score>best[0]:best=(score,ext,data)
            if w>=2800:break
        except Exception:continue
    if not best:return ''
    _,ext,data=best
    filepath=COVERS/(slug+ext)
    filepath.write_bytes(data)
    for previous in COVERS.glob(slug+'.*'):
        if previous!=filepath:previous.unlink()
    return 'assets/covers/'+filepath.name

def importer_command():
    exe=shutil.which('behance-dl')
    if exe:return [exe]
    exe=ROOT/'.venv'/'bin'/'behance-dl'
    if exe.exists():return [str(exe)]
    raise RuntimeError('behance-dl is not installed. Run: python3.12 -m pip install behance-dl==0.3.0')

def import_one(url,slug,title=None,category='branding',expected_owner=None):
    gallery_id=valid_url(url); slug=slugify(slug)
    if category not in ('branding','digital','packaging'): category='branding'
    OUT.mkdir(parents=True,exist_ok=True); CONTENT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='behance_import_') as temp:
        command=importer_command()+[url,'-o',str(temp),'--workers','4']
        process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=480)
        if process.returncode:
            raise RuntimeError('Importer returned '+str(process.returncode)+': '+process.stdout[-900:])
        matches=[p for p in Path(temp).iterdir() if p.is_dir() and p.name.startswith(gallery_id+'_')]
        if not matches:raise RuntimeError('Downloaded gallery folder was not found. '+process.stdout[-700:])
        source=matches[0]
        pages=list(source.glob('*.html'))
        if not pages:raise RuntimeError('The downloaded project has no self-contained HTML page')
        if len(pages)>1:pages.sort(key=lambda p:p.name)
        project=read_json(source/'project.json',{})
        if expected_owner:
            info=project.get('project',project) if isinstance(project,dict) else {}
            owners=info.get('owners',info.get('owner',[])) if isinstance(info,dict) else []
            if isinstance(owners,dict):owners=[owners]
            confirmed=False
            for owner in owners if isinstance(owners,list) else []:
                if not isinstance(owner,dict):continue
                username=str(owner.get('username','')).lower()
                path=str(owner.get('url','')).rstrip('/').lower()
                if username==expected_owner.lower() or path.endswith('/'+expected_owner.lower()):
                    confirmed=True;break
            if not confirmed:raise RuntimeError('Unverified author: refusing to import a discovered third-party project')
        dest=OUT/slug
        backup=OUT/(slug+'.previous')
        if backup.exists():shutil.rmtree(backup)
        if dest.exists():dest.rename(backup)
        try:
            shutil.copytree(source,dest)
        except Exception:
            if backup.exists():backup.rename(dest)
            raise
        if backup.exists():shutil.rmtree(backup)
        manifest=read_json(CONTENT/'behance-imports.json',{})
        existing=manifest.get(slug,{})
        cover=get_cover(slug,project) or existing.get('cover','')
        manifest[slug]={
            'id':gallery_id,'url':url,'page':f'assets/behance/{slug}/{pages[0].name}',
            'cover':cover,'importedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        (CONTENT/'behance-imports.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
        write_js('behance-imports.js','BEHANCE_IMPORTS',manifest)
        if slug not in KNOWN:
            customs=read_json(CONTENT/'custom-projects.json',[])
            display=(title or (project.get('name') if isinstance(project,dict) else None) or (project.get('title') if isinstance(project,dict) else None) or slug.replace('-',' ').title()).strip()[:100]
            new={'slug':slug,'title':display,'subtitle':'Imported from Behance','category':category,'type':category.upper(),'year':str(datetime.datetime.now().year),'palette':'blue','image':cover,'behance':url}
            customs=[p for p in customs if p.get('slug')!=slug]+[new]
            (CONTENT/'custom-projects.json').write_text(json.dumps(customs,ensure_ascii=False,indent=2),encoding='utf-8')
            write_js('custom-projects.js','EXTRA_PROJECTS',customs)
        return {'slug':slug,'title':title or slug,'id':gallery_id,'page':manifest[slug]['page'],'cover':cover,'count':len(list(dest.iterdir()))}

def main():
    parser=argparse.ArgumentParser(description='Import original Behance portfolio case studies as full self-contained HTML')
    parser.add_argument('--all',action='store_true',help='Import the original five published Behance cases')
    parser.add_argument('--url',help='Behance gallery HTTPS URL')
    parser.add_argument('--slug',help='English URL slug')
    parser.add_argument('--title',help='Display title for new projects')
    parser.add_argument('--category',default='branding',choices=['branding','digital','packaging'])
    args=parser.parse_args()
    if args.all:
        errors=[]
        for slug,(id,url) in KNOWN.items():
            try:print(json.dumps(import_one(url,slug),ensure_ascii=False),flush=True)
            except Exception as e:errors.append(f'{slug}: {e}');print(errors[-1],file=sys.stderr)
        if errors:raise SystemExit('Some imports failed:\n'+'\n'.join(errors))
    elif args.url and args.slug:
        print(json.dumps(import_one(args.url,args.slug,args.title,args.category),ensure_ascii=False))
    else:parser.error('Specify --all or --url URL --slug NAME')
if __name__=='__main__':main()
