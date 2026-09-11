"""
dp_uc42a_build_dashboard.py — assembles the v1.1.0 interactive dashboard.
============================================================================
Single self-contained HTML file. Nothing is fetched at render time: no CDN,
no external stylesheet, no font download, no runtime data call. That is the
repo's vendor-don't-CDN dashboard rule (uc-pos-011), and it is also what lets
this file survive being emailed, opened offline, or archived next to the
report it belongs to.

Reads out/dp_uc42a_payload.json (written by dp_uc42a_build.py) and inlines it
as a JSON literal, so the page and the CSV receipts in out/ are the same
numbers by construction.

Charts are hand-drawn SVG on purpose rather than a charting library: a spray
chart on field coordinates, a plate-side pitch map with the governed zone
grid, and a cross-highlight link between them are not shapes any library
ships. It also sidesteps O-19 (the Chart.js merge() defect that silently
deletes tick callbacks repo-wide).

Usage:  python dp_uc42a_build_dashboard.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
TPL = os.path.join(HERE, 'tpl')
TITLE = 'Trea Turner — Whole-Field Directional Tendency (dp_uc42a v1.1.0)'


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def assemble(standalone=True):
    payload = read(os.path.join(OUT, 'dp_uc42a_payload.json'))
    css = read(os.path.join(TPL, 'style.css'))
    body = read(os.path.join(TPL, 'body.html'))
    app = read(os.path.join(TPL, 'app.js'))
    head = (
        f'<title>{TITLE}</title>\n<style>\n{css}\n</style>\n'
        if not standalone else
        f'<meta charset="utf-8">\n'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<title>{TITLE}</title>\n<style>\n{css}\n</style>\n'
    )
    guts = (body + '\n<script>window.__UC42A__=' + payload + ';</script>\n'
            + '<script>\n' + app + '\n</script>\n')
    if standalone:
        return ('<!doctype html>\n<html lang="en">\n<head>\n' + head
                + '</head>\n<body>\n' + guts + '</body>\n</html>\n')
    return head + guts


def main():
    p = os.path.join(OUT, '..', 'dp_uc42a_turner_whole_field_dashboard.html')
    with open(os.path.abspath(p), 'w', encoding='utf-8') as f:
        f.write(assemble(standalone=True))
    q = os.path.join(OUT, 'dp_uc42a_dashboard_fragment.html')
    with open(q, 'w', encoding='utf-8') as f:
        f.write(assemble(standalone=False))
    print('wrote', os.path.abspath(p), os.path.getsize(os.path.abspath(p)), 'bytes')
    print('wrote', q, os.path.getsize(q), 'bytes')


if __name__ == '__main__':
    main()
