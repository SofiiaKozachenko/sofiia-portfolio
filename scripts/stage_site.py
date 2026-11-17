#!/usr/bin/env python3
"""Create static-only dist/ with all imported originals and no build scripts."""
from __future__ import annotations
from pathlib import Path
import shutil
from build_site import ROOT,validate

def main():
    validate(strict=True)
    dist=ROOT/'dist'
    if dist.exists():shutil.rmtree(dist)
    dist.mkdir()
    for filename in ('index.html','styles.css','app.js','.nojekyll'):
        shutil.copy2(ROOT/filename,dist/filename)
    for d in ('assets','content'):
        shutil.copytree(ROOT/d,dist/d,ignore=shutil.ignore_patterns('*.json','*.tmp','*.previous','*.pyc','__pycache__'))
    # Content from the Sanity starter is inert and carries no credentials in the site bundle.
    for f in (dist/'content').iterdir():
        if f.name not in ('projects.js','custom-projects.js','behance-imports.js','case-pages.js','sanity-config.js'):
            f.unlink()
    print('Staged',sum(p.stat().st_size for p in dist.rglob('*') if p.is_file()),'bytes')

if __name__=='__main__':main()
