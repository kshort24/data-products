"""Render the UC#32 reader report to a Phillies-branded PDF.

markdown -> HTML -> weasyprint, per the pitcher-scouting-report skill recipe.
Figures in out/ are embedded via base_url. Not pypdf/reportlab — the reports
are markdown-native.
"""
import os
import re
import markdown
from weasyprint import HTML

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "dp_uc31_arraez_acquisition_read_report.md")
PDF = os.path.join(HERE, "dp_uc31_arraez_acquisition_read_report.pdf")

PHI_RED, PHI_NAVY = "#E81828", "#002D72"

FIGURES = {
    "## 2. Underlying indicators — what the results are standing on": [
        ("out/dp_uc31_fig3_woba_vs_xwoba.png",
         "Fig 1 — Results (wOBA) against deserved contact (xwOBA), 2019–2026. "
         "2026 is the first season the two separate materially."),
    ],
    "## 3. Two strikes — the skill that will change your dugout": [
        ("out/dp_uc31_fig1_two_strike_survival.png",
         "Fig 2 — Two-Strike Survival Rate (AR-1). Share of two-strike plate appearances "
         "not ending in a strikeout, Arraez against every 2026 Phillies regular."),
    ],
    "## 4. Where the slug comes from — pitch group and handedness": [
        ("out/dp_uc31_fig2_damage_group_hand.png",
         "Fig 3 — Actual slugging against deserved contact quality by pitch group and "
         "pitcher hand (AR-3). Only fastballs from right-handers show results the "
         "contact supports."),
    ],
    "## 5. Runners in scoring position": [
        ("out/dp_uc31_fig4_spcr_benchmark.png",
         "Fig 4 — Scoring-Position Conversion Rate (AR-4). Runners in scoring position "
         "at plate-appearance start who scored, 2026."),
    ],
    "### 6.3 The answer": [
        ("out/dp_uc31_fig5_slot_decision.png",
         "Fig 5 — Left: the two forces that cancel — RISP share rises down the order "
         "while plate appearances fall. Right: projected run contribution by slot "
         "(AR-6); circled points are the slots under discussion."),
    ],
    "### 6.4 Why second, and why it is not about Arraez": [
        ("out/dp_uc31_fig6_table_setting_supply.png",
         "Fig 6 — Baserunners Arraez would supply above each slot's 2026 incumbent "
         "(AR-7). The largest gaps sit where the incumbents got on base least — the "
         "cleanup spot and the bottom third."),
        ("out/dp_uc31_fig7_table_setting_cashed.png",
         "Fig 7 — The other half of AR-7: runners he supplies that the next two slots "
         "would be expected to drive in. Upper bound. This is the measure that favours "
         "batting him second or third rather than leading off."),
    ],
}

CSS = f"""
@page {{ size: letter; margin: 0.62in 0.6in 0.72in 0.6in;
        @bottom-center {{ content: "Luis Arraez — Acquisition Read · uc-pos-008 / dp_uc31 · "
                                   "built 2026-08-04 · Internal — Restricted · page "
                                   counter(page) " of " counter(pages);
                          font-size: 7.2pt; color: #8C8C8C;
                          font-family: 'DejaVu Sans', Helvetica, sans-serif; }} }}
body {{ font-family: 'DejaVu Sans', Helvetica, Arial, sans-serif; font-size: 9.1pt;
       line-height: 1.44; color: #1a1a1a; }}
h1 {{ color: {PHI_RED}; font-size: 19pt; margin: 0 0 2px 0; line-height: 1.15;
     border-bottom: 3px solid {PHI_RED}; padding-bottom: 6px; }}
h2 {{ color: {PHI_NAVY}; font-size: 13pt; margin: 20px 0 7px 0;
     border-bottom: 1.6px solid {PHI_RED}; padding-bottom: 3px;
     page-break-after: avoid; }}
h3 {{ color: {PHI_NAVY}; font-size: 10.4pt; margin: 6px 0 12px 0; font-style: italic; }}
h3.sub, h3:not(:first-of-type) {{ font-style: normal; margin: 14px 0 5px 0;
     font-size: 10.6pt; font-weight: bold; page-break-after: avoid; }}
h4 {{ color: {PHI_NAVY}; font-size: 10pt; margin: 13px 0 4px 0; page-break-after: avoid; }}
p {{ margin: 6px 0; }}
strong {{ color: {PHI_NAVY}; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0 12px 0;
        font-size: 7.7pt; page-break-inside: avoid; }}
th {{ background: {PHI_NAVY}; color: white; padding: 5px 6px; text-align: left;
     font-weight: bold; font-size: 7.5pt; }}
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
.formula {{ background: #f3f5f8; border-left: 3px solid {PHI_NAVY}; padding: 8px 12px;
           margin: 10px 0; font-family: 'DejaVu Sans Mono', monospace; font-size: 8pt; }}
"""


def main():
    md_text = open(MD, encoding="utf-8").read()

    # the one LaTeX block renders as plain monospace — weasyprint has no mathjax
    md_text = md_text.replace(
        "$$\\text{SPRC}(h,s)=\\Big[\\sum_{c}W(s,c)\\cdot \\text{RE24/PA}(h,c)\\Big]"
        "\\times \\text{PA/g}(s)\\times 162$$",
        '<div class="formula">SPRC(h, s) &nbsp;=&nbsp; '
        '[ &Sigma;<sub>c</sub> &nbsp; W(s, c) &times; RE24/PA(h, c) ] '
        '&nbsp;&times;&nbsp; PA_per_game(s) &nbsp;&times;&nbsp; 162</div>')
    md_text = re.sub(r"\$W\(s,c\)\$", "<code>W(s,c)</code>", md_text)

    for anchor, figs in FIGURES.items():
        block = "".join(
            f'\n\n<figure><img src="{src}" /><figcaption>{cap}</figcaption></figure>\n\n'
            for src, cap in figs)
        idx = md_text.find(anchor)
        if idx == -1:
            print(f"  [warn] anchor not found, figure not placed: {anchor}")
            continue
        nxt = min([p for p in (md_text.find("\n## ", idx + 4),
                               md_text.find("\n### ", idx + 4)) if p != -1] or [len(md_text)])
        md_text = md_text[:nxt] + block + md_text[nxt:]

    html = markdown.markdown(md_text, extensions=["tables", "fenced_code", "md_in_html"])
    html = html.replace("<h1>", '<h1 style="text-align:left">', 1)
    doc = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html}</body></html>"
    HTML(string=doc, base_url=HERE).write_pdf(PDF)
    print(f"PDF written: {PDF}  ({os.path.getsize(PDF)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
