"""dp_uc56_build_pdf.py - markdown -> HTML -> PDF (weasyprint). Shell carried from dp_uc55_build_pdf.py.
Fails if a referenced figure is missing, a section is lost in rendering (RQ-2), or the page cap is exceeded."""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
NAME = "dp_uc56_sosa_2026_recap_report"
PAGE_CAP = 8
md = (ROOT / f"{NAME}.md").read_text(encoding="utf-8")
for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", md):
    assert (ROOT / img).exists(), f"missing figure {img}"
body = markdown.markdown(md, extensions=["tables"])


class _T(HTMLParser):
    def __init__(self):
        super().__init__()
        self.t = []

    def handle_data(self, d):
        self.t.append(d)


_p = _T()
_p.feed(body)
_txt = " ".join(_p.t)
_heads = [ln[3:].strip() for ln in md.splitlines() if ln.startswith("## ")] + ["Candid caveats", "Three things for 2027"]
assert all(h in _txt for h in _heads), f"rendered text lost sections: {[h for h in _heads if h not in _txt]}"
CSS = """@page{size:Letter;margin:0.5in 0.55in 0.6in;@bottom-right{content:"uc-pos-021 · dp_uc56 v1.0.0 · page " counter(page) " of " counter(pages);font:7.5pt Arial;color:#6b7080}}
body{font-family:Arial,Helvetica,sans-serif;font-size:9pt;line-height:1.32;color:#1b1b1b}
h1{color:#002D72;font-size:22pt;margin:0;border-top:5px solid #E81828;padding-top:6px}h3{margin:2px 0 8px;color:#4a4f5c;font-size:10.5pt;font-weight:normal}
h2{color:#002D72;font-size:13pt;margin:12px 0 4px;page-break-after:avoid}
blockquote{margin:6px 0;padding:6px 10px;background:#fff4f5;border-left:3px solid #E81828;font-size:8.4pt}blockquote ul{margin:2px 0;padding-left:14px}
img{width:100%;max-height:3.6in;object-fit:contain;margin:2px 0 0}p em{color:#5b6170;font-size:8pt}
table{border-collapse:collapse;width:100%;font-size:7.9pt;margin:4px 0}th{background:#002D72;color:#fff;text-align:left;padding:3px 5px}
td{border-bottom:1px solid #e3e6ec;padding:3px 5px;vertical-align:top}li{margin:2px 0}code{font-size:8.2pt}"""
html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
doc = HTML(string=html, base_url=str(ROOT)).render()
n = len(doc.pages)
assert n <= PAGE_CAP, f"page cap exceeded: {n} pages"
doc.write_pdf(ROOT / f"{NAME}.pdf")
print("pdf pages:", n)
