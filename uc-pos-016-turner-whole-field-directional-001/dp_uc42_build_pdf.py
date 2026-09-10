"""dp_uc42_build_pdf.py — report markdown + figures -> branded PDF via reportlab.

weasyprint (the house HTML->PDF tool for other UCs in this repo) is not
installed in this sandbox and PyPI is not reachable to install it (egress
blocked — see 04_engineering_build.md environment notes). reportlab is
available and network-free, so this build uses it directly instead of the
usual markdown->HTML->weasyprint path. Disclosed as an environment
substitution, not a silent deviation.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 Table, TableStyle, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

NAVY = colors.HexColor('#002D72')
RED = colors.HexColor('#E81828')
GREY = colors.HexColor('#555555')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle('H1c', parent=styles['Heading1'], textColor=NAVY, fontSize=18, spaceAfter=6))
styles.add(ParagraphStyle('H2c', parent=styles['Heading2'], textColor=NAVY, fontSize=13, spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle('Meta', parent=styles['Normal'], textColor=GREY, fontSize=9, spaceAfter=3))
styles.add(ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8))
styles.add(ParagraphStyle('Verdict', parent=styles['Normal'], fontSize=10.5, leading=15, spaceAfter=10,
                          backColor=colors.HexColor('#F2F4F8'), borderPadding=8))

doc = SimpleDocTemplate('dp_uc42_turner_whole_field_report.pdf', pagesize=letter,
                         topMargin=0.7*inch, bottomMargin=0.7*inch,
                         leftMargin=0.75*inch, rightMargin=0.75*inch)

story = []
story.append(Paragraph('Trea Turner — Whole-Field Directional Tendency', styles['H1c']))
story.append(Paragraph('uc-pos-016-turner-whole-field-directional-001 &middot; UC #42 &middot; dp_uc42 &middot; Phillies Offense (pos) value stream', styles['Meta']))
story.append(Paragraph('Requested and delivered 2026-09-10 &middot; data as of 2026-09-09 &middot; Human DPO: Kellen Short', styles['Meta']))
story.append(Paragraph('<b>Status: READY-CONDITIONAL (diagnostic-only tier) &middot; spot-verification 33/33 PASS</b>', styles['Meta']))
story.append(Spacer(1, 10))

story.append(Paragraph('1 &middot; Verdict, before any explanation', styles['H2c']))
verdict_rows = [
    ['Question', 'Answer'],
    ['Is Turner pulling outside-zone pitches too\noften in 2026, drifting from 2023-2025?',
     'No. 2026 outside-zone pull rate (39%, n=71) is flat-to-lower than\n'
     'pooled 2023-25 (43%, n=240); z = -0.58, not distinguishable from noise.'],
    ['Is there a real directional drift anywhere?',
     'Yes - but the opposite direction, and in-zone, not out-of-zone.\n'
     'In-zone pull rate 40% (2026) vs 48% pooled (z=-2.52); oppo 35% vs 30% (z=+2.04).'],
    ['Lock this as a formal KPI, or ship as a\ndiagnostic?',
     'Diagnostic-only, provisional (WF-1, WF-2). Sample sizes on the\n'
     'outside-zone slice are too small to lock a KPI around a null result.'],
]
t = Table(verdict_rows, colWidths=[2.3*inch, 4.0*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7F8FA')]),
    ('LEFTPADDING', (0,0), (-1,-1), 6), ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(t)
story.append(Spacer(1, 8))
story.append(Paragraph(
    '<b>The premise, tested against the data rather than assumed, does not survive contact with the '
    'data as stated.</b> The 2026 directional shift is real by the repo\'s own uncertainty-band convention '
    '(|z| &ge; 2.5 for the in-zone pull-rate move), but it is a smaller-sample, in-zone story, not the '
    'outside-zone story the working theory named.', styles['Verdict']))

story.append(Paragraph('2 &middot; Scope and intake note', styles['H2c']))
story.append(Paragraph(
    'Kellen\'s working theory: Turner is pulling too many outside-zone pitches in 2026 rather than serving '
    'them the other way, a drift from 2023-2025 Phillies-era behavior. He asked the data-product-owner to '
    'lead the narrative against the data, not confirm the premise. The two files he said he was attaching '
    '(his working markdown and a photo of a hand sketch) did not reach this session - checked the connected '
    'folders, the upload area, and both repos\' data-products directories. His prompt text was detailed enough '
    'to build from directly and is treated as the intake document of record. The one place this matters is '
    '<b>sort_rank</b>: invoked as pre-existing with a known RHB-only bug, but not found anywhere in the repo '
    '(only <i>hit_direction</i> is). This build ships a new, handedness-correct sort_rank rather than guess at '
    'undocumented prior logic (see &sect;4).', styles['Body']))

story.append(Paragraph('3 &middot; Data position', styles['H2c']))
data_rows = [
    ['Check', 'Result'],
    ['Source', 'data/phillies/phils_{2023..2026}.parquet - repo governed cache, on-disk contract of get_phillies_data()'],
    ['Freshness', 'phils_2026.parquet covers through 2026-09-09'],
    ['Entity lock', 'batter == 607208 (confirmed twice before in this repo)'],
    ['Grain', 'Pitch-level -> balls in play, Turner only, regular season (game_type==\'R\')'],
    ['Coordinate source', 'hc_x/hc_y -> loc_x/loc_y via governed derive_loc(), inherited verbatim from dp_uc40_kernel.py'],
    ['hit_direction', 'Governed, stand-aware +/-4.7-slope classification, verbatim from Baseball Functions.ipynb cell 56'],
    ['Zone convention', 'Governed in_zone(): zone<10; NULL-zone rows excluded from both populations'],
    ['Handedness', 'Turner is 100% stand==\'R\' in this dataset; L-branch implemented, not exercised'],
    ['Volume', '1,832 regular-season BIP, 2023-2026 (490 / 408 / 484 / 450)'],
]
t2 = Table(data_rows, colWidths=[1.4*inch, 4.9*inch])
t2.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTSIZE', (0,0), (-1,-1), 8), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')), ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7F8FA')]),
    ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
]))
story.append(t2)

story.append(PageBreak())
story.append(Paragraph('4 &middot; Whole-field directional map', styles['H2c']))
story.append(Image('fig1_facet_grid.png', width=6.5*inch, height=6.5*inch*(2210/1870)))
story.append(Spacer(1, 10))
story.append(Paragraph('5 &middot; Pull vs. oppo, by season and zone', styles['H2c']))
story.append(Image('fig2_pull_oppo_trend.png', width=6.5*inch, height=6.5*inch*(4.6/11)))

story.append(PageBreak())
story.append(Paragraph('6 &middot; The finding', styles['H2c']))
story.append(Paragraph(
    'Restricting to balls in play off pitches outside the strike zone - the exact population the working '
    'theory is about - Turner\'s 2026 pull rate (39.4%, 28-for-71) is not distinguishable from his pooled '
    '2023-2025 rate (43.3%, 104-for-240; pooled z = -0.58) and his oppo rate is essentially flat (35.2% vs '
    '34.6%, z = +0.10). There is no outside-zone pull drift in the data, in either direction, at this sample size.',
    styles['Body']))
story.append(Paragraph(
    'The real movement is on balls in play off pitches <b>in</b> the zone: pull rate 40.1% in 2026 vs. 47.5% '
    'pooled 2023-2025 (z = -2.52) and oppo rate 35.1% vs. 29.5% (z = +2.04) - both clear this repo\'s moderate '
    'uncertainty band (|z| &ge; 2.5 / &ge; 1.5, the ST-1 convention). 2026 is the lowest pull-rate, highest '
    'oppo-rate season of the four on in-zone contact, and the shift is not monotonic (2024 was his most '
    'pull-heavy in-zone season of the window) - 2026 is the outlier year, not the end of a steady trend.',
    styles['Body']))
story.append(Paragraph(
    'Two honest caveats. First, the outside-zone test is underpowered (71 BIP in 2026, 240 pooled) - a true '
    'effect of the hypothesized size could exist without clearing significance at this n. Second, the share of '
    'Turner\'s BIP coming from outside-zone pitches has trended down across the window (20.2% -&gt; 17.2% -&gt; '
    '14.7% -&gt; 15.8%): he is making contact with fewer outside pitches to test the premise on, not more.',
    styles['Body']))
story.append(Paragraph(
    '<b>Bottom line:</b> the working theory, read literally, is not supported. This organization\'s '
    'falsify-before-describe standard says this ships as a negative finding, not a softened directional hint. '
    'The more defensible story is a smaller-sample in-zone shift toward the opposite of the hypothesis - more '
    'oppo, less pull - worth tracking with more plate appearances rather than treating as settled.',
    styles['Body']))

story.append(Paragraph('7 &middot; Open decisions resolved at this layer', styles['H2c']))
story.append(Paragraph(
    '<b>1. Static facet grid vs. animated frame (Kellen\'s call to confirm).</b> Ships the static facet grid - '
    'hit_direction (columns) x game_year (rows), colored by p_throws - matching the sketch description and the '
    'existing run-spray-chart-60 skill\'s faceting pattern already in production. An animated-frame-on-season '
    'version is a natural follow-on if preferred after seeing this. <b>Flagged for confirmation, not defaulted.</b>',
    styles['Body']))
story.append(Paragraph(
    '<b>2. Formal KPI vs. diagnostic-only.</b> Ships diagnostic-only with two provisional candidates '
    '(WF-1 oppo_rate_ooz, WF-2 pull_rate_ooz). Locking a KPI around a metric that just returned a null result, '
    'on an under-100-BIP-per-year population, is premature.', styles['Body']))
story.append(Paragraph(
    '<b>3. Ledger ID.</b> uc-pos-016 / UC #42 / dp_uc42 - verified against the ledger index and the '
    'data-products/ directory listing at build time; no collision found.', styles['Body']))

story.append(Paragraph('8 &middot; Scope disclosure', styles['H2c']))
story.append(Paragraph(
    'Diagnostic-tier build: one subject, one narrow question, a 33-check spot-verification harness rather than '
    'an exhaustive independent-recompute harness (c.f. 711 checks on the uc-pos-014 season review). That scope '
    'reduction is priced explicitly in the BID, not hidden. Certification: READY-CONDITIONAL.',
    styles['Body']))

doc.build(story)
print('wrote dp_uc42_turner_whole_field_report.pdf')
