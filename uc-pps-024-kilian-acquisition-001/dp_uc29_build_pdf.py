"""
Render dp_uc29_kilian_acquisition_read_report.md -> branded PDF.

Markdown -> HTML (markdown, tables ext) -> weasyprint, per the house recipe.
base_url is set to this folder so out/*.png figures embed.
"""
import os
import pathlib
import markdown
from weasyprint import HTML

HERE = pathlib.Path(__file__).parent
SRC = HERE / "dp_uc29_kilian_acquisition_read_report.md"
DST = HERE / "dp_uc29_kilian_acquisition_read_report.pdf"

PHI_RED, PHI_NAVY, PHI_GRAY = "#E81828", "#002D72", "#8C8C8C"

CSS = f"""
@page {{
  size: Letter;
  margin: 0.62in 0.6in 0.72in 0.6in;
  @bottom-center {{
    content: "Caleb Kilian — Acquisition Read · uc-pps-024 / dp_uc29 · page " counter(page) " of " counter(pages);
    font-family: Georgia, serif; font-size: 7.6pt; color: {PHI_GRAY};
  }}
}}
body {{ font-family: Georgia, 'Times New Roman', serif; font-size: 9.6pt;
        line-height: 1.46; color: #1a1a1a; }}
h1 {{ color: {PHI_NAVY}; font-size: 21pt; margin: 0 0 2px 0;
      border-bottom: 3.5px solid {PHI_RED}; padding-bottom: 7px; }}
h2 {{ color: {PHI_NAVY}; font-size: 13.5pt; margin: 20px 0 7px 0;
      border-bottom: 1.6px solid {PHI_RED}; padding-bottom: 3px;
      page-break-after: avoid; }}
h3 {{ color: {PHI_NAVY}; font-size: 10.8pt; margin: 14px 0 5px 0;
      page-break-after: avoid; }}
h3:first-of-type {{ color: {PHI_GRAY}; font-size: 10.2pt; font-style: italic;
                    margin-top: 3px; }}
p {{ margin: 6px 0; }}
strong {{ color: {PHI_NAVY}; }}
em {{ color: #444; }}
hr {{ border: none; border-top: 1px solid #ddd; margin: 16px 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0 13px 0;
         font-size: 8.5pt; page-break-inside: avoid; }}
th {{ background: {PHI_NAVY}; color: #fff; text-align: left;
      padding: 5px 6px; font-weight: bold; font-size: 8.2pt; }}
td {{ padding: 4px 6px; border-bottom: 1px solid #e6e6e6; }}
tr:nth-child(even) td {{ background: #f7f8fa; }}
blockquote {{ background: #fdf3f4; border-left: 4.5px solid {PHI_RED};
              margin: 12px 0; padding: 9px 13px; font-size: 8.9pt;
              page-break-inside: avoid; }}
blockquote p {{ margin: 3px 0; }}
img {{ max-width: 100%; margin: 9px 0; page-break-inside: avoid; }}
ol, ul {{ margin: 6px 0 6px 0; padding-left: 20px; }}
li {{ margin: 4px 0; }}
code {{ font-family: Consolas, monospace; font-size: 8.4pt;
        background: #f0f1f3; padding: 1px 3px; border-radius: 2px; }}
"""


def main():
    md_text = SRC.read_text(encoding="utf-8")
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
    HTML(string=html, base_url=str(HERE)).write_pdf(str(DST))
    print(f"wrote {DST}  ({os.path.getsize(DST)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
