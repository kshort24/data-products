"""
dp_uc28 — PDF renderer for the Painter return read.

Markdown -> HTML (markdown lib, tables extension) -> weasyprint, with the
house Phillies CSS: navy #002D72 headers, red #E81828 rules and accents,
branded table headers, blockquote warning box. Not pypdf/reportlab -- the
reports in this repo are markdown-native.

Run from the repo root so that base_url='.' resolves out/*.png figures.
"""
from __future__ import annotations
import os
import re
import markdown
from weasyprint import HTML

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "dp_uc28_painter_vs_orioles_report.md")
PDF = os.path.join(HERE, "dp_uc28_painter_vs_orioles_report.pdf")

PHI_RED, PHI_NAVY = "#E81828", "#002D72"

CSS = f"""
@page {{
    size: Letter;
    margin: 0.7in 0.65in 0.8in 0.65in;
    @bottom-center {{
        content: "Andrew Painter — Return Read · PHI @ BAL 2026-07-31 · UC #29 / uc-pps-023 / dp_uc28 · page " counter(page) " of " counter(pages);
        font-family: 'DejaVu Sans', sans-serif; font-size: 7pt; color: #8C8C8C;
    }}
}}
body {{
    font-family: 'DejaVu Sans', Helvetica, Arial, sans-serif;
    font-size: 9.1pt; line-height: 1.42; color: #1a1a1a;
}}
h1 {{
    color: {PHI_NAVY}; font-size: 19pt; margin: 0 0 2pt 0; line-height: 1.15;
    border-bottom: 3px solid {PHI_RED}; padding-bottom: 5pt;
}}
h3 {{ color: {PHI_RED}; font-size: 10.5pt; margin: 4pt 0 9pt 0; font-weight: normal; }}
h2 {{
    color: {PHI_NAVY}; font-size: 13pt; margin: 17pt 0 6pt 0;
    border-bottom: 1.5px solid {PHI_RED}; padding-bottom: 3pt;
    page-break-after: avoid;
}}
h2 + p, h2 + table, h2 + ul, h2 + ol {{ page-break-before: avoid; }}
h3 + p, h3 + table {{ page-break-before: avoid; }}
p {{ margin: 5pt 0; }}
strong {{ color: {PHI_NAVY}; }}
hr {{ border: none; border-top: 1px solid #D9D9D9; margin: 12pt 0; }}
blockquote {{
    background: #F4F6FA; border-left: 4px solid {PHI_RED};
    margin: 10pt 0; padding: 8pt 11pt; font-size: 8.4pt; line-height: 1.45;
    page-break-inside: avoid;
}}
blockquote p {{ margin: 2pt 0; }}
blockquote strong {{ color: {PHI_RED}; }}
table {{
    border-collapse: collapse; width: 100%; margin: 8pt 0 10pt 0;
    font-size: 7.9pt; page-break-inside: avoid;
}}
th {{
    background: {PHI_NAVY}; color: #ffffff; text-align: left;
    padding: 4.5pt 5pt; font-size: 7.7pt; font-weight: bold;
    border: 1px solid {PHI_NAVY};
}}
td {{ padding: 3.4pt 5pt; border: 1px solid #DDE2EA; vertical-align: top; }}
tbody tr:nth-child(even) td {{ background: #F7F9FC; }}
td strong {{ color: {PHI_RED}; }}
ol, ul {{ margin: 5pt 0 5pt 0; padding-left: 17pt; }}
li {{ margin: 3.5pt 0; }}
img {{ max-width: 100%; margin: 9pt 0; page-break-inside: avoid; }}
em {{ color: #55606E; }}
code {{ background: #F0F2F6; padding: 0.5pt 2.5pt; font-size: 7.8pt;
        font-family: 'DejaVu Sans Mono', monospace; }}
"""


def main():
    with open(MD, encoding="utf-8") as fh:
        text = fh.read()

    body = markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list"])

    # Keep each figure with the paragraph that introduces it.
    body = body.replace("<p><img", '<p class="fig"><img')

    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
    HTML(string=html, base_url=HERE).write_pdf(PDF)
    size = os.path.getsize(PDF)
    n_img = len(re.findall(r"<img", body))
    n_tbl = len(re.findall(r"<table", body))
    print(f"wrote {PDF}  ({size/1024:.0f} KB, {n_tbl} tables, {n_img} figures)")


if __name__ == "__main__":
    main()
