"""dp_uc47_build_pdf.py — Markdown -> HTML -> weasyprint, Phillies-branded (house PDF path, from dp_uc44)."""
import base64, re
from pathlib import Path
import markdown
from weasyprint import HTML, CSS

HERE = Path(__file__).parent
SRC = HERE / 'dp_uc47_elite_ff_archetype_gap_report.md'
DEST = HERE / 'dp_uc47_elite_ff_archetype_gap_report.pdf'
RED, NAVY, BLUE = '#E81828', '#002D72', '#284898'

md = SRC.read_text(encoding='utf-8')
def embed(m):
    alt, rel = m.group(1), m.group(2)
    p = HERE / rel
    if not p.exists():
        raise FileNotFoundError(f'figure referenced by the report is missing: {rel}')
    return f'![{alt}](data:image/png;base64,{base64.b64encode(p.read_bytes()).decode()})'
md = re.sub(r'!\[([^\]]*)\]\((out/[^)]+\.png)\)', embed, md)
html = markdown.markdown(md, extensions=['tables', 'attr_list', 'sane_lists', 'fenced_code'])
CSSTXT = f"""
@page {{ size: Letter; margin: 14mm 13mm 15mm 13mm;
  @bottom-center {{ content: "uc-pps-032 · dp_uc47 · v1.0.0 · Elite RHP Four-Seam Archetype Gap · data through 2026-09-20 · page " counter(page) " of " counter(pages);
                    font-family: Helvetica, Arial, sans-serif; font-size: 7pt; color: #888; }} }}
body {{ font-family: Helvetica, Arial, sans-serif; font-size: 9pt; line-height: 1.5; color: #1b1b1b; }}
h1 {{ color: {NAVY}; font-size: 19pt; margin: 0 0 1mm 0; }}
h3 {{ color: {BLUE}; font-size: 10.5pt; margin: 0 0 3mm 0; border-bottom: 3px solid {RED}; padding-bottom: 2mm; font-weight: 600; }}
h2 {{ color: {NAVY}; font-size: 13pt; margin: 7mm 0 2mm 0; border-bottom: 1px solid {RED}; padding-bottom: 1mm; page-break-after: avoid; }}
p {{ margin: 0 0 2.4mm 0; }}
strong {{ color: #000; }}
blockquote {{ background: #FFF4F5; border-left: 4px solid {RED}; margin: 3mm 0; padding: 2.6mm 3.4mm; font-size: 8.3pt; color: #3a2326; page-break-inside: avoid; }}
blockquote p {{ margin: 0 0 1.6mm 0; }} blockquote ul {{ margin: 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 2.6mm 0 3.6mm 0; font-size: 7.6pt; page-break-inside: avoid; }}
th {{ background: {NAVY}; color: #fff; text-align: left; padding: 1.4mm 1.8mm; font-weight: 600; }}
td {{ border-bottom: 1px solid #e3e6ec; padding: 1.2mm 1.8mm; vertical-align: top; }}
tr:nth-child(even) td {{ background: #f7f8fa; }}
img {{ width: 100%; margin: 2.5mm 0 1mm 0; page-break-inside: avoid; }}
code {{ font-family: "DejaVu Sans Mono", monospace; font-size: 7.4pt; background: #f1f3f6; padding: 0.4mm 0.8mm; border-radius: 2px; color: #333; }}
em {{ color: #4a4a4a; }}
hr {{ border: 0; border-top: 1px solid #dde1e8; margin: 5mm 0; }}
ul, ol {{ margin: 0 0 2.6mm 0; padding-left: 5mm; }} li {{ margin-bottom: 1.1mm; }}
"""
HTML(string=f'<html><head><meta charset="utf-8"></head><body>{html}</body></html>', base_url=str(HERE)).write_pdf(DEST, stylesheets=[CSS(string=CSSTXT)])
print(f'PDF -> {DEST.name}  ({DEST.stat().st_size/1024:.0f} KB)')
