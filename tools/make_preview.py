#!/usr/bin/env python3
"""Copy dist/ to a preview folder with relative paths (for the Claude artifact preview).
Usage: python3 tools/make_preview.py <out_dir>"""
import os, re, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
out = sys.argv[1]
shutil.rmtree(out, ignore_errors=True)
shutil.copytree(DIST, out)
for dp, _, fs in os.walk(out):
    for f in fs:
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(dp, out)
        pre = "" if rel == "." else "../" * (rel.count(os.sep) + 1)
        def fix(m):
            attr, url = m.group(1), m.group(2)
            path, _, frag = url.partition("#")
            if path.endswith("/"):
                path += "index.html"
            return f'{attr}="{pre}{path.lstrip("/")}{("#" + frag) if frag else ""}"'
        with open(p) as fh:
            s = fh.read()
        s = re.sub(r'(href|src|srcset)="(/(?!/)[^"]*)"', fix, s)
        with open(p, "w") as fh:
            fh.write(s)
css = os.path.join(out, "assets", "site.css")
with open(css) as fh:
    s = fh.read()
s = s.replace('url("/assets/fonts/', 'url("fonts/')
with open(css, "w") as fh:
    fh.write(s)
assert len(s) > 10000, "site.css looks empty"
print("preview ready:", out, len(s), "bytes of CSS")
