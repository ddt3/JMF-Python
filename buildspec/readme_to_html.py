#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert Tools/README.md to a styled HTML file for inclusion in the release zip."""
import sys
import markdown
from pathlib import Path

src = Path(__file__).resolve().parent.parent / 'Tools' / 'README.md'
dst = Path(__file__).resolve().parent / 'dist' / 'JMF-Tools-README.html'

md = src.read_text(encoding='utf-8')
body = markdown.markdown(md, extensions=['tables'])

css = (
    'body{font-family:sans-serif;max-width:900px;margin:2em auto;padding:0 1em}'
    'table{border-collapse:collapse;width:100%}'
    'th,td{border:1px solid #ccc;padding:6px 10px}'
    'th{background:#f0f0f0}'
    'code{background:#f4f4f4;padding:2px 4px;border-radius:3px}'
    'pre{background:#f4f4f4;padding:1em;overflow-x:auto}'
)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>JMF Tools</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""

dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(html, encoding='utf-8')
print(f"[OK] Written: {dst}")
