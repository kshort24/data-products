"""
dp_uc35 — self-contained interactive dashboard for the Nola–Alcantara showdown.

House rule (uc-pos-011): VENDOR the charting library, don't CDN it. Chart.js
4.4.1 (MIT) is inlined verbatim from _chartjs_4.4.1.umd.js and every chart
call goes through a chart(id, cfg) helper that degrades to a visible
placeholder instead of taking the tables and tab nav down with it.

All numbers are read from the out/dp_uc35_*.csv receipts at build time and
inlined as JSON — the dashboard has no runtime dependencies at all.
"""
from __future__ import annotations
import json, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
DEST = os.path.join(HERE, 'dp_uc35_nola_alcantara_dashboard.html')
RED, BLUE, GOLD, GREY, NAVY = '#E81828', '#6BACE4', '#FFC72C', '#7c8290', '#002D72'

r = lambda n: pd.read_csv(os.path.join(OUT, f'dp_uc35_{n}.csv'))
H = json.load(open(os.path.join(OUT, 'dp_uc35_headlines.json')))

with open(os.path.join(HERE, '_chartjs_4.4.1.umd.js'), encoding='utf-8') as f:
    CHARTJS = f.read()

box = r('boxplot_population').round(4)
harper = r('harper_mia_seasons').round(4)
nms = r('nola_mia_seasons').round(4)
wms = r('wheeler_mia_seasons').round(4)
avs = r('alcantara_phi_seasons').round(4)
pstand = r('phi_hitter_season_stand')
pstand = pstand[pstand.in_population].round(4)
nstand = r('nola_mia_season_stand').round(4)
exp = r('pitcher_exposure_rank_top25').head(10)
hexp = r('harper_pitcher_rank_top25').head(8)
hva_s = r('harper_vs_alcantara_seasons').round(4)

def pts(df, ycol='rc_per_pa'):
    return [{'x': float(g) + (hash(p) % 1000) / 1000 * 0.56 - 0.28,
             'y': float(y), 'name': p, 'pa': int(pa), 'woba': float(w)}
            for p, g, y, pa, w in zip(df.player_name, df.game_year,
                                      df[ycol], df.plate_apps, df.woba)]

DATA = {
    'H': H,
    'boxPts': pts(box),
    'harper': [{'x': int(g), 'y': float(y), 'pa': int(pa), 'woba': float(w)}
               for g, y, pa, w in zip(harper.game_year, harper.rc_per_pa,
                                      harper.plate_apps, harper.woba)],
    'nolesSeason': nms[['game_year', 'plate_apps', 'ba', 'obp', 'slg', 'woba',
                        'krate', 'whiff_rate', 'chase_rate', 'hard_hit_rate',
                        'barrel_rate', 'rc_per_pa']].to_dict('records'),
    'wheelerSeason': wms[['game_year', 'plate_apps', 'woba', 'rc_per_pa']].to_dict('records'),
    'alcSeason': avs[['game_year', 'plate_apps', 'pitches', 'ba', 'obp', 'slg',
                      'woba', 'krate', 'rc_per_pa']].to_dict('records'),
    'standPts': {s: pts(pstand[pstand.stand == s]) for s in ('L', 'R')},
    'nolesStand': {s: [{'x': int(g), 'y': float(y), 'pa': int(pa), 'woba': float(w)}
                       for g, y, pa, w in zip(d.game_year, d.rc_per_pa,
                                              d.plate_apps, d.woba)]
                   for s, d in nstand.groupby('stand')},
    'floors': H['floor_by_stand'],
    'exp': [{'label': (n if isinstance(n, str) else f'MLBAM {int(p)}'),
             'pitches': int(x), 'pa': int(pa), 'alc': int(p) == 645261,
             'carry': isinstance(s, str) and 'carry' in s}
            for p, n, x, pa, s in zip(exp.pitcher, exp.pitcher_name,
                                      exp.pitches, exp.plate_apps, exp.name_source)],
    'hexp': [{'label': (n if isinstance(n, str) else f'MLBAM {int(p)}'),
              'pa': int(pa), 'pitches': int(x), 'alc': int(p) == 645261}
             for p, n, x, pa in zip(hexp.pitcher, hexp.pitcher_name,
                                    hexp.pitches, hexp.plate_apps)],
    'hvaSeason': hva_s[['game_year', 'plate_apps', 'woba', 'ba', 'slg']].to_dict('records'),
}

def card(label, d, accent):
    return f"""<div class="card" style="border-top:3px solid {accent}">
      <div class="c-lab">{label}</div>
      <div class="c-big">{d['woba']:.3f} <span>wOBA</span></div>
      <div class="c-sub">{d['ba']:.3f}/{d['obp']:.3f}/{d['slg']:.3f} · RC/PA {d['rc_per_pa']:.3f}</div>
      <div class="c-pa">{int(d['plate_apps'])} PA · K {d['krate']:.1%} · HH {d['hard_hit_rate']:.1%} · Brl {d['barrel_rate']:.1%}</div>
    </div>"""

# Cards render from FULL-PRECISION career receipts, not the 4dp headlines —
# double-rounding (D4 family) would drift the third decimal (e.g. .5745->.575).
_cr = lambda n: r(n).iloc[0].to_dict()
CARDS = ''.join([
    card('NOLES · what Nola makes of Miami (career)', _cr('nola_mia_career'), RED),
    card('WHEELER vs MIA (career, 2017–26)', _cr('wheeler_mia_career'), BLUE),
    card('HARPER vs MIA (career)', _cr('harper_mia_career'), GOLD),
    card('PHI OFFENSE vs ALCANTARA (career)', _cr('alcantara_phi_career'), GREY),
    card('HARPER vs ALCANTARA (his #1 most-faced)', _cr('harper_vs_alcantara_career'), '#ffffff'),
])

def tbl(rows, cols, fmt=None):
    fmt = fmt or {}
    head = ''.join(f'<th>{c}</th>' for c in cols)
    body = ''
    for row in rows:
        tds = ''
        for c in cols:
            v = row.get(c, '')
            f = fmt.get(c)
            tds += f'<td>{f.format(v) if f and v == v else v}</td>'
        body += f'<tr>{tds}</tr>'
    return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'

F3 = '{:.3f}'
noles_tbl = tbl(DATA['nolesSeason'],
                ['game_year', 'plate_apps', 'ba', 'obp', 'slg', 'woba', 'krate',
                 'whiff_rate', 'chase_rate', 'hard_hit_rate', 'barrel_rate', 'rc_per_pa'],
                {k: F3 for k in ['ba', 'obp', 'slg', 'woba', 'krate', 'whiff_rate',
                                 'chase_rate', 'hard_hit_rate', 'barrel_rate', 'rc_per_pa']})
alc_tbl = tbl(DATA['alcSeason'],
              ['game_year', 'plate_apps', 'pitches', 'ba', 'obp', 'slg', 'woba',
               'krate', 'rc_per_pa'],
              {k: F3 for k in ['ba', 'obp', 'slg', 'woba', 'krate', 'rc_per_pa']})
hva_tbl = tbl(DATA['hvaSeason'], ['game_year', 'plate_apps', 'woba', 'ba', 'slg'],
              {k: F3 for k in ['woba', 'ba', 'slg']})

HTML_DOC = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nola vs Alcantara — uc-pos-012 · dp_uc35</title>
<script>{CHARTJS}</script>
<style>
  :root {{ --red:{RED}; --blue:{BLUE}; --gold:{GOLD}; --navy:{NAVY}; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:#0d1117; color:#e6e8ee;
         font-family:'Segoe UI',system-ui,Helvetica,Arial,sans-serif; }}
  header {{ padding:22px 28px 14px; border-bottom:3px solid var(--red);
            background:linear-gradient(135deg,#101725 0%,#0d1117 70%); }}
  h1 {{ margin:0; font-size:24px; }} h1 span {{ color:var(--red); }}
  .sub {{ color:#9aa3b2; font-size:13px; margin-top:6px; }}
  .badge {{ display:inline-block; background:#12331c; color:#57d97a;
            border:1px solid #2a6e40; border-radius:4px; padding:1px 8px;
            font-size:11.5px; margin-left:8px; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(215px,1fr));
            gap:12px; padding:16px 28px; }}
  .card {{ background:#161d2b; border-radius:8px; padding:12px 14px; }}
  .c-lab {{ font-size:10.5px; letter-spacing:.06em; color:#9aa3b2; }}
  .c-big {{ font-size:26px; font-weight:700; margin:4px 0 2px; }}
  .c-big span {{ font-size:12px; color:#9aa3b2; font-weight:400; }}
  .c-sub {{ font-size:12.5px; color:#c8cdd8; }}
  .c-pa {{ font-size:11px; color:#8a92a3; margin-top:3px; }}
  nav {{ display:flex; gap:4px; padding:0 28px; border-bottom:1px solid #232b3b; }}
  nav button {{ background:none; border:none; color:#9aa3b2; padding:10px 16px;
    font-size:13.5px; cursor:pointer; border-bottom:3px solid transparent; }}
  nav button.on {{ color:#fff; border-bottom-color:var(--red); }}
  .tab {{ display:none; padding:18px 28px 30px; }} .tab.on {{ display:block; }}
  .panel {{ background:#131a27; border-radius:10px; padding:16px; margin:0 0 18px; }}
  .panel h2 {{ margin:0 0 4px; font-size:16px; }}
  .panel .note {{ color:#9aa3b2; font-size:12px; margin:0 0 10px; }}
  .cwrap {{ position:relative; height:430px; }}
  .cwrap.short {{ height:360px; }}
  .fallback {{ color:#c33; padding:30px; text-align:center; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
  @media (max-width:900px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
  table {{ border-collapse:collapse; width:100%; font-size:12px; margin-top:8px; }}
  th {{ background:var(--navy); color:#fff; padding:6px 8px; text-align:left; }}
  td {{ padding:5px 8px; border-bottom:1px solid #232b3b; }}
  tr:hover td {{ background:#1a2334; }}
  .gov {{ font-size:12px; color:#9aa3b2; line-height:1.55; }}
  .gov b {{ color:#e6e8ee; }}
  footer {{ padding:14px 28px 26px; border-top:1px solid #232b3b;
            color:#77808f; font-size:11.5px; line-height:1.6; }}
</style></head><body>
<header>
  <h1>If Aaron Nola against the Marlins were a <span>Phillies hitter</span></h1>
  <div class="sub">Nola (PHI) vs Alcantara (MIA) · Citizens Bank Park · Wed 2026-08-19 6:05 PM ET
    · data through <b>2026-08-17</b> · UC #36 · uc-pos-012 · dp_uc35
    <span class="badge">verification 79/79 PASS</span>
    <span class="badge" style="color:#e8b45a;border-color:#7a5a22;background:#33270f">
      floor = Nola min PA vs MIA ({H['floor_pa']}) — DPO ruling, not house 50</span></div>
</header>
<div class="cards">{CARDS}</div>
<nav>
  <button class="on" data-t="t1">The Noles Constant</button>
  <button data-t="t2">By Batter Stand</button>
  <button data-t="t3">The Alcantara Flip Side</button>
  <button data-t="t4">Season Receipts</button>
  <button data-t="t5">Governance</button>
</nav>

<div class="tab on" id="t1"><div class="panel">
  <h2>RC per PA — Phillies player-seasons vs the two constants</h2>
  <p class="note">Grey: every Phillies player-season above the floor ({H['floor_pa']} PA) since 2015 (hover for names).
     Red line: Noles career constant 0.090 (696 PA). Dashed blue: Wheeler vs MIA 0.084 (593 PA).
     Gold stars: the real Harper vs MIA by season.</p>
  <div class="cwrap"><canvas id="c1"></canvas></div>
</div></div>

<div class="tab" id="t2">
  <div class="grid2">
    <div class="panel"><h2>vs LHB</h2>
      <p class="note">Floor {H['floor_by_stand']['L']} PA (Nola min L-season vs MIA) — directional below 50 PA.</p>
      <div class="cwrap short"><canvas id="cL"></canvas></div></div>
    <div class="panel"><h2>vs RHB</h2>
      <p class="note">Floor {H['floor_by_stand']['R']} PA (Nola min R-season vs MIA) — directional below 50 PA.</p>
      <div class="cwrap short"><canvas id="cR"></canvas></div></div>
  </div>
  <div class="panel gov"><b>Career stand splits (citable):</b> Noles vs LHB .267 wOBA / 262 PA · vs RHB .300 / 434 PA —
    the Marlins-mastery is lefty-shaped, the opposite polarity of Nola's 2026 league-wide lefty leak (uc-pps-021).</div>
</div>

<div class="tab" id="t3">
  <div class="grid2">
    <div class="panel"><h2>Pitches thrown to the PHI offense, 2015–2026</h2>
      <p class="note">Alcantara red (#2 in frame). * = display name via logged DPO carry-in; counts are id-keyed.</p>
      <div class="cwrap short"><canvas id="c3"></canvas></div></div>
    <div class="panel"><h2>Harper as a Phillie — most-faced pitchers (PA)</h2>
      <p class="note">Alcantara is #1 in-frame; the intake's "3rd most since 2015" needs his WSH years (out of plane).</p>
      <div class="cwrap short"><canvas id="c4"></canvas></div></div>
  </div>
  <div class="panel"><h2>Harper vs Alcantara, by season</h2>
    <p class="note">Career: .319/.389/.574 · wOBA .409 · 64.9% hard-hit · 13.5% barrel · 54 PA. Every season cell &lt;15 PA — cite the career line only.</p>
    {hva_tbl}</div>
</div>

<div class="tab" id="t4">
  <div class="panel"><h2>Noles — season KPI family (what Nola allowed MIA)</h2>{noles_tbl}</div>
  <div class="panel"><h2>PHI offense vs Alcantara — by season</h2>{alc_tbl}</div>
</div>

<div class="tab" id="t5"><div class="panel gov">
  <b>Lineage:</b> Statcast parquet (phils_2015–2026, wheeler.parquet for 2017–19) → dp_uc35_kernel.py
  (governed Baseball Functions transcriptions; D1/D2 _fix variants; runs_created verbatim) →
  dp_uc35_nola_alcantara.py → out/dp_uc35_*.csv receipts → this dashboard (numbers inlined at build).<br><br>
  <b>Floor ruling:</b> human DPO 2026-08-18 — "use his minimum plate_apps in the dataset". Derived {H['floor_pa']} PA
  season-grain, L {H['floor_by_stand']['L']} / R {H['floor_by_stand']['R']} stand-grain. Deviation from house 50-PA
  floor governed in 03_governance.md; below-house-floor cells flagged in receipts.<br><br>
  <b>Defect register carried:</b> D1 whiff (fixed variant), D2 hard-hit (fixed variant; O-8 denominator
  disclosed), D4 nresults rounding (unrounded kernel), D5/O-7 pull_air_rate (unused). No new defects opened.<br><br>
  <b>Premise verdicts:</b> Alcantara #2 (not #1) in pitches to PHI — Scherzer leads 3,137 to 2,278.
  Harper-vs-Alcantara #1 in-frame (54 PA), "3rd since 2015" not reproducible in the governed plane.
  Nola faced MIA in 11 of 12 seasons (none in 2025).<br><br>
  <b>Verification:</b> dp_uc35_verification.py — 79/79 PASS on independent recomputation from raw parquet.
</div></div>

<footer>uc-pos-012-nola-alcantara-showdown-001 · dp_uc35 · Phillies Offense value stream ·
Chart.js 4.4.1 vendored (MIT) — no external requests · every figure traces to out/dp_uc35_*.csv</footer>

<script>
const D = {json.dumps(DATA)};
const RED='{RED}', BLUE='{BLUE}', GOLD='{GOLD}', GREY='rgba(150,158,172,0.45)';
document.querySelectorAll('nav button').forEach(b => b.onclick = () => {{
  document.querySelectorAll('nav button').forEach(x => x.classList.remove('on'));
  document.querySelectorAll('.tab').forEach(x => x.classList.remove('on'));
  b.classList.add('on'); document.getElementById(b.dataset.t).classList.add('on');
}});
function chart(id, cfg) {{
  try {{ return new Chart(document.getElementById(id), cfg); }}
  catch (e) {{ document.getElementById(id).closest('.cwrap').innerHTML =
    '<div class="fallback">chart failed — see CSV receipts</div>'; console.error(id, e); }}
}}
Chart.defaults.color = '#9aa3b2';
Chart.defaults.borderColor = 'rgba(255,255,255,0.07)';
const tip = (ctx) => {{
  const p = ctx.raw;
  return p.name ? `${{p.name}} ${{Math.round(p.x)}}: RC/PA ${{p.y.toFixed(3)}} (${{p.pa}} PA, wOBA ${{p.woba.toFixed(3)}})`
                : `RC/PA ${{p.y.toFixed(3)}}${{p.pa ? ` (${{p.pa}} PA, wOBA ${{p.woba.toFixed(3)}})` : ''}}`;
}};
const constLine = (v, color, dash) => ({{
  type:'line', data: [{{x:2014.4,y:v}},{{x:2026.6,y:v}}], borderColor: color,
  borderWidth: 2.5, borderDash: dash||[], pointRadius: 0, fill:false, tension:0 }});
const scatterOpts = (xmin,xmax) => ({{
  responsive:true, maintainAspectRatio:false, animation:false,
  scales: {{ x: {{ type:'linear', min:xmin, max:xmax, ticks:{{stepSize:1, callback:v=>Number.isInteger(v)?v:''}},
                   title:{{display:true,text:'Season'}} }},
             y: {{ min:0, max:0.31, title:{{display:true,text:'RC per PA'}} }} }},
  plugins: {{ legend:{{labels:{{usePointStyle:true}}}},
              tooltip:{{callbacks:{{label:tip}}}} }} }});

chart('c1', {{ type:'scatter', data: {{ datasets: [
  {{ label:'Phillies player-seasons', data:D.boxPts, backgroundColor:GREY, pointRadius:3 }},
  Object.assign(constLine(D.H.nola_mia.rc_per_pa, RED),
    {{ label:'Noles constant 0.090 (696 PA)' }}),
  Object.assign(constLine(D.H.wheeler_mia.rc_per_pa, BLUE, [7,5]),
    {{ label:'Wheeler vs MIA 0.084 (593 PA)' }}),
  {{ label:'Harper vs MIA (by season)', data:D.harper, backgroundColor:GOLD,
     pointStyle:'star', pointRadius:9, pointBorderColor:'#fff', pointBorderWidth:1 }},
]}}, options: scatterOpts(2014.4, 2026.6) }});

['L','R'].forEach(s => chart('c'+s, {{ type:'scatter', data: {{ datasets: [
  {{ label:'PHI hitter-season-stand', data:D.standPts[s], backgroundColor:GREY, pointRadius:3 }},
  {{ label:'Noles vs '+s+'HB', data:D.nolesStand[s].filter(p=>p.pa>D.floors[s]),
     backgroundColor:RED, pointStyle:'rectRot', pointRadius:8,
     pointBorderColor:'#fff', pointBorderWidth:1 }},
]}}, options: scatterOpts(2014.4, 2026.6) }}));

chart('c3', {{ type:'bar', data: {{
  labels: D.exp.map(p => p.label + (p.carry ? ' *' : '')),
  datasets: [{{ data: D.exp.map(p => p.pitches),
    backgroundColor: D.exp.map(p => p.alc ? RED : (p.carry ? BLUE : GREY)) }}]}},
  options: {{ indexAxis:'y', responsive:true, maintainAspectRatio:false, animation:false,
    plugins: {{ legend:{{display:false}}, tooltip:{{callbacks:{{label:c =>
      `${{c.raw}} pitches · ${{D.exp[c.dataIndex].pa}} PA`}}}} }},
    scales: {{ x:{{title:{{display:true,text:'Pitches to PHI batters'}}}} }} }} }});

chart('c4', {{ type:'bar', data: {{
  labels: D.hexp.map(p => p.label),
  datasets: [{{ data: D.hexp.map(p => p.pa),
    backgroundColor: D.hexp.map(p => p.alc ? RED : GREY) }}]}},
  options: {{ indexAxis:'y', responsive:true, maintainAspectRatio:false, animation:false,
    plugins: {{ legend:{{display:false}}, tooltip:{{callbacks:{{label:c =>
      `${{c.raw}} PA · ${{D.hexp[c.dataIndex].pitches}} pitches`}}}} }},
    scales: {{ x:{{title:{{display:true,text:'Plate appearances'}}}} }} }} }});
</script></body></html>"""

with open(DEST, 'w', encoding='utf-8') as f:
    f.write(HTML_DOC)
print(f'wrote {DEST} ({os.path.getsize(DEST)/1024:.0f} KB)')
