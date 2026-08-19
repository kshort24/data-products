"""
dp_uc35 — PDF renderer for the Nola–Alcantara showdown read.

Markdown -> HTML (markdown lib, tables extension) -> weasyprint, with the
house Phillies CSS: navy #002D72 headers, red #E81828 rules and accents,
branded table headers, blockquote warning box. Follows dp_uc34_build_pdf.py.

Run from this directory so base_url resolves the out/dp_uc35_fig*.png figures.
"""
from __future__ import annotations
import os, re
import markdown
from weasyprint import HTML

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "dp_uc35_nola_alcantara_report.md")
PDF = os.path.join(HERE, "dp_uc35_nola_alcantara_report.pdf")

PHI_RED, PHI_NAVY = "#E81828", "#002D72"

CSS = f"""
@page {{
    size: Letter; margin: 0.7in 0.6in 0.8in 0.6in;
    @bottom-center {{
        content: "Nola vs Alcantara — Showdown Read · as of 2026-08-17 · UC #36 / uc-pos-012 / dp_uc35 · page " counter(page) " of " counter(pages);
        font-family: 'DejaVu Sans', sans-serif; font-size: 7pt; color: #8C8C8C;
    }}
}}
body {{ font-family: 'DejaVu Sans', Helvetica, Arial, sans-serif;
        font-size: 9.1pt; line-height: 1.42; color: #1a1a1a; }}
h1 {{ color: {PHI_NAVY}; font-size: 19pt; margin: 0 0 2pt 0; line-height: 1.15;
      border-bottom: 3px solid {PHI_RED}; padding-bottom: 5pt; }}
h3 {{ color: {PHI_RED}; font-size: 9.6pt; margin: 4pt 0 9pt 0; font-weight: normal; }}
h2 {{ color: {PHI_NAVY}; font-size: 13pt; margin: 17pt 0 6pt 0;
      border-bottom: 1.5px solid {PHI_RED}; padding-bottom: 3pt; page-break-after: avoid; }}
h2 + p, h2 + table, h2 + ul, h2 + ol, h2 + h3 {{ page-break-before: avoid; }}
h3 + p, h3 + table {{ page-break-before: avoid; }}
p {{ margin: 5pt 0; }}
strong {{ color: {PHI_NAVY}; }}
hr {{ border: none; border-top: 1px solid #D9D9D9; margin: 12pt 0; }}
blockquote {{ background: #F4F6FA; border-left: 4px solid {PHI_RED};
   margin: 10pt 0; padding: 8pt 11pt; font-size: 8.4pt; line-height: 1.45;
   page-break-inside: avoid; }}
blockquote p {{ margin: 2pt 0; }}
blockquote strong {{ color: {PHI_RED}; }}
table {{ border-collapse: collapse; width: 100%; margin: 8pt 0 10pt 0;
   font-size: 7.6pt; page-break-inside: avoid; }}
th {{ background: {PHI_NAVY}; color: #ffffff; text-align: left; padding: 4.5pt 5pt;
   font-size: 7.4pt; font-weight: bold; border: 1px solid {PHI_NAVY}; }}
td {{ padding: 3.2pt 5pt; border: 1px solid #DDE2EA; vertical-align: top; }}
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
    body = body.replace("<p><img", '<p class="fig"><img')
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
    HTML(string=html, base_url=HERE).write_pdf(PDF)
    print(f"wrote {PDF}  ({os.path.getsize(PDF)/1024:.0f} KB, "
          f"{len(re.findall(r'<table', body))} tables, {len(re.findall(r'<img', body))} figures)")


if __name__ == "__main__":
    main()
