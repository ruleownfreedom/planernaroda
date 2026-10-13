#!/usr/bin/env python3
"""Рисует иконки веб-приложения из иконки темы «Сталь и хром» (APP_ICONS.steel в HTML).
    python3 tools/render_icons.py index.html     (нужен Playwright с Chromium)"""
import json, pathlib, re, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
html = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
icons = json.loads(re.search(r'var APP_ICONS = (\{.*?\});\n', html).group(1))
ic = icons['steel']
paths = ''.join('<path d="%s" fill="%s"%s/>' % (p[1], p[0], '' if p[2] == 1 else ' fill-opacity="%s"' % p[2]) for p in ic['s'])
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="18 18 72 72"><rect x="18" y="18" width="72" height="72" fill="%s"/>'
       '<g transform="translate(54 57) scale(%s) translate(-54 -57)">%s</g></svg>') % (ic['bg'], ic['k'], paths)
(ROOT / 'icon.svg').write_text(svg, encoding='utf-8')
with sync_playwright() as p:
    b = p.chromium.launch()
    for size, name in ((180, 'apple-touch-icon.png'), (192, 'icon-192.png'), (512, 'icon-512.png')):
        pg = b.new_page(viewport={'width': size, 'height': size})
        pg.set_content('<html><body style="margin:0">' + svg.replace('<svg ', '<svg width="%d" height="%d" ' % (size, size)) + '</body></html>')
        pg.screenshot(path=str(ROOT / name), omit_background=False)
        pg.close()
    b.close()
print('ok')
