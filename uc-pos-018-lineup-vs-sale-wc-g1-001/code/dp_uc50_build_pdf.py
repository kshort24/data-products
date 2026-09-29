"""dp_uc50_build_pdf.py -- markdown -> HTML -> weasyprint (house recipe, pitcher-scouting-report skill §5).
Run from the directory holding dp_uc50_lineup_vs_sale_report.md and out/ (base_url='.' embeds the PNGs).
Needs pango (weasyprint); on the laptop VM this step runs in the cloud render sandbox on receipts."""
import pathlib
import sys

import markdown
from weasyprint import HTML

HERE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SRC = HERE / "dp_uc50_lineup_vs_sale_report.md"
DST = HERE / "dp_uc50_lineup_vs_sale_report.pdf"

CSS = """
@page { size: Letter; margin: 0.55in 0.55in 0.6in 0.55in;
        @bottom-right { content: "uc-pos-018 · dp_uc50 · page " counter(page); font: 8pt 'Liberation Sans', Arial; color: #8C8C8C; } }
body { font-family: 'Liberation Sans', Arial, sans-serif; font-size: 9.6pt; color: #1A1A1A; line-height: 1.38; }
h1 { color: #002D72; font-size: 19pt; margin: 0 0 2pt 0; border-bottom: 3px solid #E81828; padding-bottom: 4pt; }
h2 { color: #002D72; font-size: 13.5pt; margin-top: 16pt; border-bottom: 1.5px solid #E81828; padding-bottom: 2pt; page-break-after: avoid; }
h3 { color: #002D72; font-size: 11pt; margin: 12pt 0 4pt 0; page-break-after: avoid; }
blockquote { background: #FFF4F4; border-left: 4px solid #E81828; margin: 8pt 0; padding: 6pt 10pt; }
table { border-collapse: collapse; width: 100%; font-size: 8pt; margin: 6pt 0; page-break-inside: avoid; }
th { background: #002D72; color: white; padding: 3pt 4pt; text-align: left; }
td { border-bottom: 1px solid #D9D9D9; padding: 3pt 4pt; vertical-align: top; }
tr:nth-child(even) td { background: #F4F6FA; }
img { width: 100%; margin: 4pt 0; page-break-inside: avoid; }
code { font-size: 8.5pt; background: #F3F3F3; padding: 0 2pt; }
strong { color: #002D72; }
"""

body = markdown.markdown(SRC.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
# one index card per page section: break before each hitter's h3 inside section 3
body = body.replace("<h3>1 · ", '<h3 style="page-break-before: always">1 · ')
for n in range(2, 10):
    body = body.replace(f"<h3>{n} · ", f'<h3 style="page-break-before: always">{n} · ')
html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
HTML(string=html, base_url=str(HERE)).write_pdf(DST)
print(DST, DST.stat().st_size)
