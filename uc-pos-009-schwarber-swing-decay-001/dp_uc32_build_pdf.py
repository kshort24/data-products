"""Render the UC#33 reader report to a Phillies-branded PDF.

markdown -> HTML -> weasyprint, per the pitcher-scouting-report skill recipe.
Figures in out/ are embedded via base_url. Not pypdf/reportlab — the reports
are markdown-native.
"""
import os
import re

import markdown
from weasyprint import HTML

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "dp_uc32_schwarber_swing_decay_report.md")
PDF = os.path.join(HERE, "dp_uc32_schwarber_swing_decay_report.pdf")

PHI_RED, PHI_NAVY, PHI_LIGHT = "#E81828", "#002D72", "#7A99C2"

CSS = f"""
@page {{
  size: Letter;
  margin: 20mm 16mm 18mm 16mm;
  @top-left  {{ content: "Kyle Schwarber — The State of the Swing";
                font-size: 7.5pt; color: #8a94a6; font-family: Helvetica, Arial, sans-serif; }}
  @top-right {{ content: "uc-pos-009 · dp_uc32 · 2026-08-07";
                font-size: 7.5pt; color: #8a94a6; font-family: Helvetica, Arial, sans-serif; }}
  @bottom-right {{ content: counter(page) " / " counter(pages);
                   font-size: 8pt; color: #8a94a6; font-family: Helvetica, Arial, sans-serif; }}
  @bottom-left {{ content: "Internal — Restricted";
                  font-size: 7.5pt; color: {PHI_RED}; font-family: Helvetica, Arial, sans-serif; }}
}}
body {{ font-family: Helvetica, Arial, sans-serif; font-size: 9.4pt; line-height: 1.5;
        color: #1f2933; }}
h1 {{ color: {PHI_NAVY}; font-size: 21pt; margin: 0 0 2mm 0; letter-spacing: -0.4px;
      border-bottom: 3px solid {PHI_RED}; padding-bottom: 3mm; }}
h2 {{ color: {PHI_NAVY}; font-size: 13pt; margin: 9mm 0 3mm 0;
      border-left: 4px solid {PHI_RED}; padding-left: 3mm; page-break-after: avoid; }}
h3 {{ color: {PHI_NAVY}; font-size: 10.5pt; margin: 6mm 0 2mm 0; page-break-after: avoid; }}
p  {{ margin: 0 0 2.6mm 0; }}
strong {{ color: {PHI_NAVY}; }}
em {{ color: #5b6472; }}
hr {{ border: 0; border-top: 1px solid #e3e7ec; margin: 6mm 0; }}
blockquote {{ background: #fff4f4; border-left: 4px solid {PHI_RED};
              margin: 4mm 0; padding: 3mm 4mm; font-size: 9pt; color: #4a5260; }}
blockquote p {{ margin: 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 3mm 0 4mm 0;
         font-size: 8.2pt; page-break-inside: avoid; }}
th {{ background: {PHI_NAVY}; color: #fff; text-align: left; padding: 2mm 2.2mm;
      font-weight: 600; font-size: 7.8pt; }}
td {{ padding: 1.6mm 2.2mm; border-bottom: 1px solid #eceff3; }}
tr:nth-child(even) td {{ background: #fafbfc; }}
img {{ max-width: 100%; margin: 3mm 0 1mm 0; page-break-inside: avoid; }}
code {{ background: #f2f4f7; padding: 0.4mm 1.2mm; border-radius: 2px;
        font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; color: {PHI_NAVY}; }}
ul, ol {{ margin: 0 0 3mm 0; padding-left: 5mm; }}
li {{ margin-bottom: 1.2mm; }}
h2 + p em, p > em:only-child {{ color: #8a94a6; font-size: 8.2pt; }}
"""


def main() -> None:
    src = open(MD, encoding="utf-8").read()

    # The masthead block (everything before the first ---) gets a panel treatment.
    html_body = markdown.markdown(
        src, extensions=["tables", "attr_list", "sane_lists", "nl2br"]
    )
    # Small-sample and caveat emphasis: bold-italic runs become inline warnings.
    html_body = re.sub(
        r"<em><strong>(.*?)</strong></em>",
        rf'<span style="color:{PHI_RED};font-weight:600">\1</span>',
        html_body,
    )
    html_body = re.sub(
        r"<strong><em>(.*?)</em></strong>",
        rf'<span style="color:{PHI_RED};font-weight:600">\1</span>',
        html_body,
    )

    doc = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    HTML(string=doc, base_url=HERE).write_pdf(PDF)
    print(f"[pdf] wrote {PDF} ({os.path.getsize(PDF)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
