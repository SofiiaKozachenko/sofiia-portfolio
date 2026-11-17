#!/usr/bin/env python3
"""Automatic build: sync source-owned Behance project galleries before deploying.

The resulting site is purely static. Visitors neither install nor import anything.
A failed sync intentionally fails the deployment instead of publishing blank galleries.
"""
from __future__ import annotations
import argparse,json,os,re,sys,urllib.request,urllib.parse
from pathlib import Path
from import_behance import ROOT, KNOWN, import_one, read_json
from optimize_cases import build as build_optimized_cases

SOURCE_CONFIG=ROOT/'content'/'sources.json'


def source_projects():
    sources=[dict(slug=slug,url=url,id=pid) for slug,(pid,url) in KNOWN.items()]
    data=read_json(SOURCE_CONFIG,{})
    for p in data.get('additional',[]):
        if not isinstance(p,dict) or not p.get('url') or not p.get('slug'):continue
        if p['slug'] in (item['slug'] for item in sources):continue
        sources.append(p)
    return sources


def discover_profile_projects(username='sofiiakozachenko'):
    """Best effort only. If profile markup changes, the curated source list still works."""
    url=f'https://www.behance.net/{username}/projects'
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; PortfolioSync/1.0)'})
    with urllib.request.urlopen(req,timeout=25) as response:
        html=response.read(8_000_000).decode('utf-8','replace')
    pattern=r'(?:https?://(?:www\.)?behance\.net)?/gallery/(\d{7,12})/([a-zA-Z0-9-]{2,100})'
    links=[]; seen=set()
    # Browsers receive URLs in both escaped and unescaped state payloads.
    cleaned=html.replace('\\/','/').replace('\\u002F','/').replace('\\u002f','/')
    for mid,slug in re.findall(pattern,cleaned):
        if mid in seen:continue
        seen.add(mid)
        links.append((mid,f'https://www.behance.net/gallery/{mid}/{slug}'))
    return links[:50]


def owner_confirmed(project_json_path,username='sofiiakozachenko'):
    """For automatically discovered works, require explicit matching author metadata."""
    payload=read_json(project_json_path,{})
    project=payload.get('project',payload) if isinstance(payload,dict) else {}
    if not isinstance(project,dict):return False
    owners=project.get('owners',project.get('owner',[]))
    if isinstance(owners,dict):owners=[owners]
    if not isinstance(owners,list):return False
    for owner in owners:
        if isinstance(owner,dict) and any(str(owner.get(key,'')).lower()==username for key in ('username','url','name')):
            return True
        if isinstance(owner,dict) and str(owner.get('url','')).rstrip('/').lower().endswith('/'+username):return True
    return False


def validate(strict=True):
    projects=source_projects()
    manifest=read_json(ROOT/'content'/'behance-imports.json',{})
    problems=[]
    optimized_js=ROOT/'content'/'case-pages.js'
    native_text=optimized_js.read_text(encoding='utf-8') if optimized_js.exists() else ''
    for p in projects:
        slug=p['slug'];item=manifest.get(slug,{})
        if not (native_text and f'"{slug}"' in native_text):problems.append(f'{slug}: missing optimized gallery')
        if slug=='bean-road' and 'player.vimeo.com/video/1090989010' not in native_text:problems.append('Bean Road: missing original Vimeo player')
        if not item:problems.append(f'{slug}: missing imported record');continue
        page=ROOT/item.get('page','')
        if not page.is_file() or page.stat().st_size<1000:problems.append(f'{slug}: missing actual case HTML');continue
        case_dir=ROOT/'assets'/'behance'/slug
        images=[x for x in case_dir.rglob('*') if x.is_file() and x.suffix.lower() in ('.jpg','.jpeg','.png','.webp','.gif','.avif') and x.stat().st_size>9000]
        if not images:problems.append(f'{slug}: no local images in imported case');continue
        cover=ROOT/item.get('cover','')
        if not cover.is_file() or cover.stat().st_size<10000:problems.append(f'{slug}: no local high-quality cover')
    if problems:
        print('PRE-PUBLISH VALIDATION FAILED:',*problems,sep='\n - ',file=sys.stderr)
        if strict:raise SystemExit(1)
    else:print(f'Validated {len(projects)} complete locally hosted case studies.')
    return not problems


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--discover',action='store_true',help='Best-effort new public works from profile; verify ownership')
    args=parser.parse_args()
    if args.check_only:validate();return
    failures=[]
    sources=source_projects()
    for p in sources:
        try:
            result=import_one(p['url'],p['slug'],p.get('title'),p.get('category','branding'))
            print('IMPORTED',json.dumps(result,ensure_ascii=False),flush=True)
        except Exception as exc:
            failures.append(f"{p['slug']}: {exc}")
            print('FAILED',failures[-1],file=sys.stderr,flush=True)
    if args.discover and not failures:
        try:
            # Discovery is safe by default: inspect own-profile links and import only verified owners.
            known_ids={str(p.get('id') or re.search(r'/gallery/(\d+)',p['url']).group(1)) for p in sources}
            for pid,url in discover_profile_projects():
                if pid in known_ids:continue
                slug=f'project-{pid}'
                result=import_one(url,slug,'New Behance project','branding',expected_owner='sofiiakozachenko')
                print('DISCOVERED',json.dumps(result,ensure_ascii=False),flush=True)
        except Exception as exc:
            print('Optional new-project discovery unavailable:',exc,file=sys.stderr)
    if failures:
        raise SystemExit('Sync incomplete; preserving previous published website.\n'+'\n'.join(failures))
    build_optimized_cases()
    validate(strict=True)

if __name__=='__main__':main()
