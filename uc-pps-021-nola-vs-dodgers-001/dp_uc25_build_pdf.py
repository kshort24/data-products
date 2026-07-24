"""Branded PDF builder for uc-pps-021 (dp_uc25) — markdown -> HTML -> weasyprint.
Phillies CSS (navy headers, red rules, warning blockquote); figures are embedded
inline in the report markdown (![](out/...png)) and resolve via base_url.
Usage: python dp_uc25_build_pdf.py [MLB_ROOT]"""
import sys, pathlib
import markdown
from weasyprint import HTML

MLB = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
STEM = "dp_uc25_nola_vs_dodgers"
md_text = (MLB / f"{STEM}_report.md").read_text(encoding="utf-8")
body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

CSS = """
@page { size: Letter; margin: 1.6cm 1.7cm 1.7cm 1.7cm;
  @bottom-center { content: "dp_uc25 · uc-pps-021 · Aaron Nola vs LAD 2026-07-22 · confidential — internal advance"; font-size: 7pt; color: #8C8C8C; }
  @bottom-right { content: "p. " counter(page); font-size: 7.5pt; color: #8C8C8C; } }
body { font-family: -apple-system, 'Segoe UI', Arial, sans-serif; font-size: 9.6pt; line-height: 1.45; color: #1a1a1a; }
h1 { color: #002D72; font-size: 19pt; margin: 0 0 2pt 0; border-bottom: 3px solid #E81828; padding-bottom: 5pt; }
h2 { color: #002D72; font-size: 13pt; margin: 15pt 0 5pt 0; border-left: 5px solid #E81828; padding-left: 7pt; }
h3 { color: #002D72; font-size: 10.5pt; margin: 9pt 0 3pt 0; }
p { margin: 4pt 0; }
strong { color: #002D72; }
a { color: #E81828; text-decoration: none; }
hr { border: none; border-top: 1.5px solid #E81828; margin: 10pt 0; }
table { border-collapse: collapse; width: 100%; margin: 7pt 0; font-size: 8.2pt; }
th { background: #002D72; color: #fff; padding: 4pt 5pt; text-align: left; font-weight: 600; border: 1px solid #002D72; }
td { padding: 3pt 5pt; border: 1px solid #D9D9D9; }
tr:nth-child(even) td { background: #F5F6F8; }
blockquote { background: #FBF7E7; border-left: 5px solid #E81828; margin: 8pt 0; padding: 7pt 11pt;
  font-size: 8.6pt; color: #33291a; border-radius: 0 3px 3px 0; }
blockquote strong { color: #B01020; }
img { width: 100%; max-width: 100%; border: 1px solid #E6E8EC; border-radius: 4px; margin: 6pt 0;
  page-break-inside: avoid; }
figure { margin: 9pt 0; text-align: center; page-break-inside: avoid; }
figcaption { font-size: 7.8pt; color: #55606e; margin-top: 3pt; text-align: left; font-style: italic; }
ol, ul { margin: 4pt 0 4pt 0; padding-left: 16pt; }
li { margin: 2.5pt 0; }
em { color: #55606e; }
code { background: #F0F1F4; padding: 0 3px; border-radius: 2px; font-size: 8pt; }
"""

out_pdf = MLB / f"{STEM}_report.pdf"
html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
HTML(string=html, base_url=str(MLB.resolve())).write_pdf(str(out_pdf))
print("wrote", out_pdf, out_pdf.stat().st_size, "bytes")
