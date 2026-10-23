"""dp_uc54_build_pdf.py — markdown -> HTML -> PDF (weasyprint). Fails if a referenced figure is missing or the page cap is exceeded."""
from __future__ import annotations
import re
from pathlib import Path
import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
md = (ROOT / "dp_uc54_crawford_2026_recap_report.md").read_text(encoding="utf-8")
for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", md):
    assert (ROOT / img).exists(), f"missing figure {img}"
body = markdown.markdown(md, extensions=["tables"])
# guard (defect RQ-2): a stray '<' in published text can open a phantom tag that swallows the rest of the report
from html.parser import HTMLParser
class _T(HTMLParser):
    def __init__(self): super().__init__(); self.t = []
    def handle_data(self, d): self.t.append(d)
_p = _T(); _p.feed(body); _txt = " ".join(_p.t)
_heads = [l[3:].strip() for l in md.splitlines() if l.startswith("## ")] + ["Candid caveats"]
assert all(h in _txt for h in _heads), f"rendered text lost sections: {[h for h in _heads if h not in _txt]}"
CSS = """@page{size:Letter;margin:0.5in 0.55in 0.6in;@bottom-right{content:"uc-pos-019 · dp_uc54 v1.0.0 · page " counter(page) " of " counter(pages);font:7.5pt Arial;color:#6b7080}}
body{font-family:Arial,Helvetica,sans-serif;font-size:9.4pt;line-height:1.38;color:#1b1b1b}
h1{color:#002D72;font-size:22pt;margin:0;border-top:5px solid #E81828;padding-top:6px}h3{margin:2px 0 8px;color:#4a4f5c;font-size:10.5pt;font-weight:normal}
h2{color:#002D72;font-size:13pt;margin:12px 0 4px;page-break-after:avoid}
blockquote{margin:6px 0;padding:6px 10px;background:#fff4f5;border-left:3px solid #E81828;font-size:8.6pt}blockquote ul{margin:2px 0;padding-left:14px}
img{width:100%;margin:2px 0 0}p em{color:#5b6170;font-size:8pt}
table{border-collapse:collapse;width:100%;font-size:8pt;margin:4px 0}th{background:#002D72;color:#fff;text-align:left;padding:3px 5px}
td{border-bottom:1px solid #e3e6ec;padding:3px 5px;vertical-align:top}li{margin:2px 0}code{font-size:8.4pt}"""
html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
doc = HTML(string=html, base_url=str(ROOT)).render()
n = len(doc.pages)
assert n <= 10, f"page cap exceeded: {n} pages"
doc.write_pdf(ROOT / "dp_uc54_crawford_2026_recap_report.pdf")
print("pdf pages:", n)
