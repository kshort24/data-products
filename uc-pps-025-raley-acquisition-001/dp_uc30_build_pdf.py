"""Render the UC#31 reader report to a Phillies-branded PDF.

markdown -> HTML -> weasyprint, per the pitcher-scouting-report skill recipe.
Figures in out/ are embedded via base_url. Not pypdf/reportlab — the reports
are markdown-native.
"""
import os
import re
import markdown
from weasyprint import HTML

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "dp_uc30_raley_acquisition_read_report.md")
PDF = os.path.join(HERE, "dp_uc30_raley_acquisition_read_report.pdf")

PHI_RED, PHI_NAVY = "#E81828", "#002D72"

FIGURES = {
    "## The signature: where the ball comes from": [
        ("out/dp_uc30_fig1_release_benchmark.png",
         "Fig 1 — Release-point benchmark: Raley against every Phillies LHP, 2015–2026."),
    ],
    "## The arsenal": [
        ("out/dp_uc30_fig2_arsenal_movement.png",
         "Fig 2 — Arsenal movement, pre-TJ vs post-TJ. The curveball and four-seamer are gone; "
         "the sweeper has risen ~2.3 in in induced vertical break."),
    ],
    "## The approach, by batter hand": [
        ("out/dp_uc30_fig3_platoon_process.png",
         "Fig 3 — Usage vs whiff rate by pitch and batter hand, post-TJ."),
        ("out/dp_uc30_fig4_location_by_hand.png",
         "Fig 4 — Location by batter hand. The sweeper finishes off the plate to LHH "
         "and inside the zone to RHH."),
    ],
    "## For the manager — how to use him": [
        ("out/dp_uc30_fig5_deployment.png",
         "Fig 5 — Deployment, workload and the post-TJ velocity / CSW trend."),
    ],
}

CSS = f"""
@page {{ size: letter; margin: 0.62in 0.6in 0.72in 0.6in;
        @bottom-center {{ content: "Brooks Raley — Acquisition Read · uc-pps-025 / dp_uc30 · "
                                   "built 2026-08-04 · page " counter(page) " of " counter(pages);
                          font-size: 7.4pt; color: #8C8C8C;
                          font-family: 'DejaVu Sans', Helvetica, sans-serif; }} }}
body {{ font-family: 'DejaVu Sans', Helvetica, Arial, sans-serif; font-size: 9.1pt;
       line-height: 1.44; color: #1a1a1a; }}
h1 {{ color: {PHI_RED}; font-size: 19pt; margin: 0 0 2px 0; line-height: 1.15;
     border-bottom: 3px solid {PHI_RED}; padding-bottom: 6px; }}
h3 {{ color: {PHI_NAVY}; font-size: 10.4pt; font-weight: normal; margin: 6px 0 12px 0;
     font-style: italic; }}
h2 {{ color: {PHI_NAVY}; font-size: 13pt; margin: 20px 0 7px 0;
     border-bottom: 1.6px solid {PHI_RED}; padding-bottom: 3px;
     page-break-after: avoid; }}
h3.sub, h3:not(:first-of-type) {{ font-style: normal; }}
h4 {{ color: {PHI_NAVY}; font-size: 10pt; margin: 13px 0 4px 0; page-break-after: avoid; }}
p {{ margin: 6px 0; }}
strong {{ color: {PHI_NAVY}; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0 12px 0;
        font-size: 7.9pt; page-break-inside: avoid; }}
th {{ background: {PHI_NAVY}; color: white; padding: 5px 6px; text-align: left;
     font-weight: bold; font-size: 7.7pt; }}
td {{ padding: 4px 6px; border-bottom: 0.5px solid #d8d8d8; }}
tr:nth-child(even) td {{ background: #f6f7f9; }}
blockquote {{ background: #fdf1f2; border-left: 4px solid {PHI_RED};
             margin: 12px 0; padding: 9px 13px; font-size: 8.5pt;
             page-break-inside: avoid; }}
blockquote p {{ margin: 4px 0; }}
ul, ol {{ margin: 6px 0 6px 0; padding-left: 20px; }}
li {{ margin: 3px 0; }}
hr {{ border: none; border-top: 1px solid #d8d8d8; margin: 16px 0; }}
code {{ background: #eef0f3; padding: 1px 4px; font-size: 8pt;
       font-family: 'DejaVu Sans Mono', monospace; }}
figure {{ margin: 12px 0 16px 0; page-break-inside: avoid; text-align: center; }}
figure img {{ width: 100%; max-width: 100%; }}
figcaption {{ font-size: 7.6pt; color: #555; font-style: italic;
             margin-top: 4px; text-align: left; }}
em {{ color: #444; }}
"""


def main():
    md_text = open(MD, encoding="utf-8").read()

    # inject figures directly ahead of the section they illustrate
    for anchor, figs in FIGURES.items():
        block = "".join(
            f'\n\n<figure><img src="{src}" /><figcaption>{cap}</figcaption></figure>\n\n'
            for src, cap in figs)
        idx = md_text.find(anchor)
        if idx == -1:
            print(f"  [warn] anchor not found, figure not placed: {anchor}")
            continue
        end = md_text.find("\n## ", idx + 4)
        end = len(md_text) if end == -1 else end
        md_text = md_text[:end] + block + md_text[end:]

    html = markdown.markdown(md_text, extensions=["tables", "fenced_code", "md_in_html"])
    # the header block reads better centred
    html = html.replace("<h1>", '<h1 style="text-align:left">', 1)
    doc = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html}</body></html>"
    HTML(string=doc, base_url=HERE).write_pdf(PDF)
    size = os.path.getsize(PDF) / 1024
    print(f"PDF written: {PDF}  ({size:.0f} KB)")


if __name__ == "__main__":
    main()
