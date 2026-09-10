"""dp_uc42_build_dashboard.py — receipts -> one self-contained HTML dashboard.

Vendored Chart.js (MIT, v4.4.1), inlined — never a CDN, per the repo's
standing "vendor-don't-CDN dashboard rule" (uc-pos-011). The vendored copy is
reused verbatim from uc-pos-014-turner-2026-recency-001/_chartjs_4.4.1.umd.js
(same file, not re-fetched) rather than downloaded again.
"""
import json
import pandas as pd

full = pd.read_csv('kpi_directional_by_zone_year.csv')

with open('chartjs_inline.txt') as f:
    CHARTJS = f.read()

years = sorted(full.game_year.unique().tolist())
outside = full[full.zone == 'outside'].sort_values('game_year')
inzone = full[full.zone == 'in_zone'].sort_values('game_year')

data_js = {
    'years': years,
    'outside': {
        'pull': outside.pull_rate.round(4).tolist(),
        'oppo': outside.oppo_rate.round(4).tolist(),
        'n': outside.n_bip.tolist(),
    },
    'in_zone': {
        'pull': inzone.pull_rate.round(4).tolist(),
        'oppo': inzone.oppo_rate.round(4).tolist(),
        'n': inzone.n_bip.tolist(),
    },
}

table_rows = []
for _, r in full[full.zone.isin(['outside', 'in_zone'])].sort_values(['zone', 'game_year']).iterrows():
    table_rows.append(
        f"<tr><td>{int(r.game_year)}</td><td>{'Outside zone' if r.zone=='outside' else 'In zone'}</td>"
        f"<td>{int(r.n_bip)}</td><td>{int(r.pull_n)} ({r.pull_rate:.1%})</td>"
        f"<td>{int(r.oppo_n)} ({r.oppo_rate:.1%})</td><td>{int(r.straight_n)} ({r.straight_rate:.1%})</td></tr>"
    )
table_html = "\n".join(table_rows)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Trea Turner — Whole-Field Directional Tendency</title>
<style>
  :root {{ --navy:#002D72; --red:#E81828; --grey:#555; --bg:#F7F8FA; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, Arial, sans-serif; margin:0; background:var(--bg); color:#1a1a1a; }}
  header {{ background:var(--navy); color:white; padding:22px 32px; }}
  header h1 {{ margin:0 0 4px 0; font-size:22px; }}
  header .meta {{ font-size:12.5px; opacity:0.85; }}
  .wrap {{ max-width:1100px; margin:0 auto; padding:24px 32px 60px; }}
  .verdict {{ background:white; border-left:5px solid var(--navy); padding:16px 20px; border-radius:4px;
              box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom:24px; font-size:14.5px; line-height:1.5;}}
  .cards {{ display:flex; gap:16px; flex-wrap:wrap; margin-bottom:28px; }}
  .card {{ background:white; border-radius:6px; padding:16px 18px; flex:1; min-width:220px;
           box-shadow:0 1px 3px rgba(0,0,0,0.08); }}
  .card .label {{ font-size:12px; color:var(--grey); text-transform:uppercase; letter-spacing:0.03em; }}
  .card .value {{ font-size:26px; font-weight:700; color:var(--navy); margin-top:4px; }}
  .card .sub {{ font-size:12px; color:var(--grey); margin-top:4px; }}
  h2 {{ color:var(--navy); font-size:17px; border-bottom:2px solid #eee; padding-bottom:6px; margin-top:36px; }}
  .chart-box {{ background:white; border-radius:6px; padding:18px; box-shadow:0 1px 3px rgba(0,0,0,0.08); }}
  .toggle {{ display:flex; gap:8px; margin-bottom:14px; }}
  .toggle button {{ background:#eef0f4; border:none; padding:8px 16px; border-radius:20px; cursor:pointer;
                     font-size:13px; color:var(--navy); font-weight:600; }}
  .toggle button.active {{ background:var(--navy); color:white; }}
  table {{ width:100%; border-collapse:collapse; background:white; font-size:13px; margin-top:8px; }}
  th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid #eee; }}
  th {{ background:var(--navy); color:white; font-weight:600; }}
  tr:nth-child(even) {{ background:#fafbfc; }}
  footer {{ font-size:11.5px; color:var(--grey); margin-top:36px; line-height:1.6; }}
  .tag {{ display:inline-block; background:#eef0f4; color:var(--navy); font-size:11px; padding:2px 8px;
          border-radius:10px; margin-right:6px; font-weight:600; }}
</style>
</head>
<body>
<header>
  <h1>Trea Turner — Whole-Field Directional Tendency</h1>
  <div class="meta">uc-pos-016-turner-whole-field-directional-001 &middot; UC #42 &middot; dp_uc42 &middot;
  data as of 2026-09-09 &middot; <span class="tag">READY-CONDITIONAL</span> <span class="tag">diagnostic-only</span></div>
</header>
<div class="wrap">

  <div class="verdict">
    <b>Verdict:</b> the premise — Turner pulling outside-zone pitches too often in 2026 — is <b>not supported</b>
    by the data (2026 outside-zone pull rate 39%, n=71, vs. pooled 2023–25 43%, n=240; z=-0.58). The real
    directional shift runs the <b>opposite</b> way and lives <b>in-zone</b>: pull rate down to 40% (from 48%
    pooled, z=-2.52), oppo rate up to 35% (from 30% pooled, z=+2.04).
  </div>

  <div class="cards">
    <div class="card"><div class="label">Outside-zone pull rate, 2026</div><div class="value">39%</div>
      <div class="sub">vs. 43% pooled 2023-25 (z=-0.58, n.s.)</div></div>
    <div class="card"><div class="label">In-zone pull rate, 2026</div><div class="value">40%</div>
      <div class="sub">vs. 48% pooled 2023-25 (z=-2.52)</div></div>
    <div class="card"><div class="label">In-zone oppo rate, 2026</div><div class="value">35%</div>
      <div class="sub">vs. 30% pooled 2023-25 (z=+2.04)</div></div>
    <div class="card"><div class="label">Total BIP analyzed</div><div class="value">1,832</div>
      <div class="sub">Regular season, 2023-2026</div></div>
  </div>

  <h2>Pull vs. oppo rate by season</h2>
  <div class="toggle">
    <button id="btn-outside" class="active" onclick="showZone('outside')">Outside-zone pitches</button>
    <button id="btn-inzone" onclick="showZone('in_zone')">In-zone pitches</button>
  </div>
  <div class="chart-box"><canvas id="mainChart" height="90"></canvas></div>

  <h2>Underlying counts</h2>
  <table>
    <thead><tr><th>Season</th><th>Zone</th><th>BIP</th><th>Pull</th><th>Oppo</th><th>Straightaway</th></tr></thead>
    <tbody>
    {table_html}
    </tbody>
  </table>

  <h2>Full whole-field visual</h2>
  <p style="font-size:13px;color:var(--grey);">The facet-grid spray chart (hit_direction &times; game_year &times;
  p_throws, with a fixed baseball-size marker and a locked Navy/Red p_throws color map) ships as
  <code>out/dp_uc42_fig1_facet_grid.png</code> alongside this dashboard and in the PDF report — a static image
  reproduces more faithfully than a from-scratch interactive scatter would in this diagnostic-tier build.</p>

  <footer>
    <b>Scope:</b> diagnostic-tier build, one subject, one narrow question. Governed <code>hit_direction</code>
    (Baseball Functions.ipynb cell 56) and <code>derive_loc</code> (dp_uc40_kernel.py PA-L1) reused verbatim;
    entity locked on MLBAM id 607208; <code>p_throws</code> color map and marker size locked per Kellen's
    corrections; new <code>sort_rank</code> built handedness-correct from scratch (no prior version found in
    the repo — see report &sect;2). Spot-verification 33/33 PASS. Chart.js v4.4.1 (MIT) vendored inline —
    no network required to view this file.
  </footer>
</div>

<script>
{CHARTJS}
</script>
<script>
const DATA = {json.dumps(data_js)};
let currentZone = 'outside';
let chart;

function buildChart(zone) {{
  const ctx = document.getElementById('mainChart').getContext('2d');
  const d = DATA[zone];
  if (chart) chart.destroy();
  chart = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: DATA.years,
      datasets: [
        {{ label: 'Pull rate', data: d.pull, backgroundColor: '#002D72' }},
        {{ label: 'Oppo rate', data: d.oppo, backgroundColor: '#E81828' }},
      ]
    }},
    options: {{
      responsive: true,
      plugins: {{
        legend: {{ position: 'top' }},
        tooltip: {{
          callbacks: {{
            afterLabel: function(ctx) {{
              return 'n = ' + d.n[ctx.dataIndex] + ' BIP';
            }}
          }}
        }}
      }},
      scales: {{
        y: {{ beginAtZero: true, max: 0.6, ticks: {{ callback: v => (v*100).toFixed(0)+'%' }} }}
      }}
    }}
  }});
}}

function showZone(zone) {{
  currentZone = zone;
  document.getElementById('btn-outside').classList.toggle('active', zone==='outside');
  document.getElementById('btn-inzone').classList.toggle('active', zone==='in_zone');
  buildChart(zone);
}}

buildChart('outside');
</script>
</body>
</html>
"""

with open('dp_uc42_turner_whole_field_dashboard.html', 'w') as f:
    f.write(html)
print('wrote dp_uc42_turner_whole_field_dashboard.html', len(html), 'bytes')
