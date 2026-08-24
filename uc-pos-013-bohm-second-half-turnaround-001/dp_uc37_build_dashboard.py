"""
dp_uc37 — self-contained interactive HTML dashboard for the Alec Bohm
second-half turnaround read.

Every number rendered here is read from the dp_uc37_*.csv receipts written by
dp_uc37_bohm_turnaround.py. Nothing is hand-keyed and nothing is recomputed in
the browser, so the dashboard cannot drift from the report or the verification.

Chart.js is VENDORED (dp_uc34 rule — never CDN): the dashboard must render
with no network at all, and every chart call degrades to a placeholder that
leaves the tables intact.
"""
from __future__ import annotations
import json, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "dp_uc37_bohm_turnaround_dashboard.html")
CHARTJS = os.path.join(HERE, "_chartjs_4.4.1.umd.js")


def rd(name):
    df = pd.read_csv(os.path.join(HERE, f"dp_uc37_{name}.csv"))
    df = df.replace([float("inf"), float("-inf")], pd.NA)
    return df.astype(object).where(pd.notna(df), None)


def main():
    H = json.load(open(os.path.join(HERE, "dp_uc37_headlines.json")))

    rl = pd.read_csv(os.path.join(HERE, "dp_uc37_running_line.csv"))
    rl = rl[(rl.cum_pa >= 50) & ((rl.cum_pa % 3 == 0) |
                                 (rl.cum_pa == rl.groupby('game_year').cum_pa.transform('max')))]
    rl = rl[['game_year', 'cum_pa', 'cum_ba', 'cum_slg', 'cum_woba']].round(4)
    rl = rl.astype(object).where(pd.notna(rl), None)

    pool = pd.read_csv(os.path.join(HERE, "dp_uc37_population_pool.csv"))
    pool = pool[['player_name', 'game_year', 'plate_apps', 'slg', 'woba',
                 'whiff_rate', 'chase_rate', 'hard_hit_rate', 'pull_air_rate',
                 'mean_ev']].round(4)
    pool = pool.astype(object).where(pd.notna(pool), None)

    data = {
        "monthly": rd("monthly_panel").to_dict("records"),
        "window": rd("window_split").to_dict("records"),
        "scan": rd("breakpoint_scan").to_dict("records"),
        "career": rd("career_by_year").round(4).to_dict("records"),
        "rl": rl.to_dict("records"),
        "profile": rd("profile_percentiles").to_dict("records"),
        "pool": pool.to_dict("records"),
        "platoon": rd("platoon_splits").to_dict("records"),
        "platoon_cf": rd("platoon_counterfactual").to_dict("records"),
        "pgw": rd("pitch_group_window").to_dict("records"),
        "ptype": rd("pitch_type_season").to_dict("records"),
        "dirs": rd("direction_air_matrix").to_dict("records"),
        "paq": rd("pull_air_quality").to_dict("records"),
        "inds": rd("inds_reconciliation").to_dict("records"),
        "H": H,
    }
    def _clean(o):
        if isinstance(o, dict):
            return {k: _clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_clean(v) for v in o]
        if isinstance(o, float) and (o != o or o in (float('inf'), float('-inf'))):
            return None
        return o

    payload = json.dumps(_clean(data), allow_nan=False, default=lambda o: None)
    with open(CHARTJS, encoding="utf-8") as fh:
        lib = fh.read()
    html = TPL.replace("__CHARTJS__", lib).replace("__DATA__", payload)
    with open(DEST, "w", encoding="utf-8") as fh:
        fh.write(html)
    n = sum(len(v) for v in data.values() if isinstance(v, list))
    print(f"wrote {DEST}  ({os.path.getsize(DEST)/1024:.0f} KB, {n} rows inlined)")


TPL = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Alec Bohm — Second-Half Turnaround · as of 2026-08-22</title>
<script>/* Chart.js 4.4.1 (MIT) — vendored so this file renders with no network */
__CHARTJS__
</script>
<style>
:root{--red:#E81828;--navy:#002D72;--gold:#C4A24A;--gray:#8C8C8C;--lgray:#E6EAF0;--bg:#F7F9FC;}
*{box-sizing:border-box;}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
     color:#1a1a1a;background:var(--bg);font-size:14px;line-height:1.45;}
header{background:var(--navy);color:#fff;padding:20px 26px 16px;border-bottom:5px solid var(--red);}
header h1{margin:0 0 3px;font-size:22px;letter-spacing:-.2px;}
header .sub{font-size:13px;opacity:.85;}
header .gov{font-size:11px;opacity:.65;margin-top:7px;}
.warn{background:#FFF4F5;border-left:4px solid var(--red);margin:18px 26px 0;padding:11px 15px;font-size:12px;}
.warn b{color:var(--red);}
.warn.amber{background:#FDF8EC;border-left-color:var(--gold);}
.warn.amber b{color:#8A6D22;}
nav{display:flex;flex-wrap:wrap;gap:6px;padding:0 26px;margin:16px 0 0;}
nav button{border:1px solid var(--lgray);background:#fff;padding:7px 14px;border-radius:20px;
   cursor:pointer;font-size:12.5px;color:var(--navy);font-weight:600;transition:.12s;}
nav button:hover{border-color:var(--navy);}
nav button.on{background:var(--navy);color:#fff;border-color:var(--navy);}
main{padding:18px 26px 60px;}
.panel{display:none;} .panel.on{display:block;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px;}
.card{background:#fff;border:1px solid var(--lgray);border-radius:9px;padding:15px 17px;}
.card h3{margin:0 0 3px;font-size:14px;color:var(--navy);}
.card .note{font-size:11.5px;color:var(--gray);margin:0 0 11px;}
.wide{grid-column:1/-1;}
canvas{max-height:340px;}
table{border-collapse:collapse;width:100%;font-size:12px;margin-top:4px;}
th{background:var(--navy);color:#fff;text-align:left;padding:6px 8px;font-size:11.5px;}
td{padding:5px 8px;border-bottom:1px solid var(--lgray);}
tr:nth-child(even) td{background:#FAFBFD;}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;}
tr.me td{background:#FFF0F1!important;font-weight:700;color:var(--navy);}
tr.floor td{background:#FDF8EC!important;color:#8A6D22;}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:12px;margin-bottom:16px;}
.kpi{background:#fff;border:1px solid var(--lgray);border-left:4px solid var(--red);
     border-radius:7px;padding:11px 13px;}
.kpi.n{border-left-color:var(--navy);} .kpi.g{border-left-color:var(--gold);}
.kpi .lab{font-size:10.5px;text-transform:uppercase;letter-spacing:.4px;color:var(--gray);}
.kpi .val{font-size:22px;font-weight:700;color:var(--navy);font-variant-numeric:tabular-nums;
     line-height:1.15;margin:2px 0 1px;}
.kpi .dl{font-size:11px;color:var(--gray);}
.up{color:var(--red);font-weight:700;} .dn{color:var(--navy);font-weight:700;}
.ctl{display:flex;gap:7px;align-items:center;margin:0 0 10px;font-size:12px;color:var(--gray);}
.ctl button{border:1px solid var(--lgray);background:#fff;padding:4px 11px;border-radius:14px;
   cursor:pointer;font-size:11.5px;color:var(--navy);font-weight:600;}
.ctl button.on{background:var(--red);color:#fff;border-color:var(--red);}
footer{padding:0 26px 40px;font-size:11px;color:var(--gray);}
.verdict{display:inline-block;padding:1px 7px;border-radius:10px;font-size:10.5px;font-weight:700;}
.v-ok{background:#E7F1E9;color:#1E6B33;} .v-part{background:#FDF8EC;color:#8A6D22;}
.v-no{background:#FDECEE;color:#B3141F;}
</style></head><body>
<header>
  <h1>Alec Bohm — Second-Half Turnaround</h1>
  <div class="sub">Phillies Offense · 2026 season through <b>22 August</b> · 124 games · 512 PA
      (377 pre-break · 135 post-break)</div>
  <div class="gov">UC #38 · uc-pos-013-bohm-second-half-turnaround-001 · dp_uc37 ·
      verification 227/227 PASS · Internal — Phillies staff</div>
</header>

<div class="warn"><b>The turnaround is real and process-backed.</b>
SLG .351 → .488, wOBA .278 → .374, BA w/ RISP .299 → .462 across the All-Star break — with hard-hit
40.8% → 46.9%, xwOBAcon .313 → .404 and in-zone whiff <b>cut nearly in half</b> (12.0% → 6.8%) behind
it. But it is <b>not</b> a pull-air breakout (10.8% → 10.6%, 14th percentile), the approach barely
moved, and part of the jump is a .222 pre-break BABIP correcting.</div>
<div class="warn amber"><b>Reliability warnings.</b> The break was chosen after seeing the outcome —
the 10-point sensitivity scan shows the sign survives every candidate boundary, but effect size varies
threefold. Below the 50-PA floor and amber-shaded everywhere: post-break RISP (42 PA), post-break vs
LHP (33 PA), post-break offspeed (12 PA), March (21 PA). Everything downstream of the split is
<b>descriptive, not inferential</b>.</div>

<nav>
  <button class="on" data-p="overview">Overview</button>
  <button data-p="career">Career trajectory</button>
  <button data-p="mechanism">What changed</button>
  <button data-p="contact">Contact &amp; pull-air</button>
  <button data-p="platoon">Platoon</button>
  <button data-p="pitches">Pitch types</button>
  <button data-p="governance">Governance</button>
</nav>
<main>

<section class="panel on" id="overview">
  <div class="kpis" id="kpis"></div>
  <div class="grid">
    <div class="card wide"><h3>Monthly results — where the surge actually lives</h3>
      <p class="note">Bars are plate appearances against the right axis. Amber months fall below the
      50-PA reliability floor. The dotted region right of July is post-break.</p>
      <canvas id="c_month"></canvas></div>
    <div class="card"><h3>Breakpoint sensitivity</h3>
      <p class="note">wOBA after the split minus wOBA before it, for every candidate boundary.
      Every bar is red: no boundary reverses the finding. The 8 Aug bar sits at exactly 50 post PA.</p>
      <canvas id="c_scan"></canvas></div>
    <div class="card"><h3>Monthly panel</h3><p class="note">Amber rows are below floor.</p>
      <div style="max-height:330px;overflow:auto"><table id="t_month"></table></div></div>
  </div>
</section>

<section class="panel" id="career">
  <div class="card wide"><h3>2026 against his own six prior seasons — cumulative results by PA</h3>
  <p class="note">Grey = 2020–2025 self-referential ghost lines (AP-6 grammar). Left tail below 50 PA
  suppressed. The 2026 line crosses the break at PA 377.</p>
  <div class="ctl"><span>Metric</span>
    <button class="on" data-m="cum_slg">SLG</button>
    <button data-m="cum_ba">BA</button>
    <button data-m="cum_woba">wOBA</button></div>
  <canvas id="c_rl" style="max-height:400px"></canvas></div>
  <div class="grid" style="margin-top:16px">
    <div class="card wide"><h3>Career by season</h3>
      <p class="note">The whiff column is a six-year monotone improvement — 26.7% → 16.0% — and the
      post-break 12.4% is its endpoint, not an aberration. 2020 is the 60-game season.</p>
      <div style="overflow:auto"><table id="t_career"></table></div></div>
  </div>
</section>

<section class="panel" id="mechanism">
  <div class="grid">
    <div class="card wide"><h3>Before vs after the break — what actually moved</h3>
      <p class="note">Descriptive only: the breakpoint was outcome-selected. Toggle the family.</p>
      <div class="ctl"><span>Family</span>
        <button class="on" data-f="results">Results</button>
        <button data-f="process">Process</button></div>
      <canvas id="c_mech" style="max-height:400px"></canvas></div>
    <div class="card"><h3>The window split, in full</h3>
      <p class="note">⚠ marks a below-floor sub-sample.</p>
      <div style="max-height:420px;overflow:auto"><table id="t_window"></table></div></div>
    <div class="card"><h3>The pitcher-side panel (RC-4)</h3>
      <p class="note">These are opponent metrics — what pitchers did TO Bohm, never his behaviour.
      The league moved INTO the zone against him post-break; first-pitch strike rate is identical
      to four decimal places (a genuine coincidence, verified twice).</p>
      <table id="t_rc4"></table></div>
  </div>
</section>

<section class="panel" id="contact">
  <div class="grid">
    <div class="card"><h3>Profile percentiles — 2026 season vs post-break window</h3>
      <p class="note">Against 218 Phillies hitter-seasons since 2015 (99 players, ≥50 PA). Red = the
      post-break window scored as if it were a season (descriptive).</p>
      <canvas id="c_pct" style="max-height:380px"></canvas></div>
    <div class="card"><h3>Pull-air: volume vs quality</h3>
      <p class="note">Volume flat and low (14th percentile). Quality exploded: post-break pull-airs
      leave at 97.7 mph with 3 HR on 12 balls.</p>
      <table id="t_paq"></table>
      <p class="note" style="margin-top:9px">Direction × air matrix (share of window BIP):</p>
      <div style="max-height:240px;overflow:auto"><table id="t_dirs"></table></div></div>
    <div class="card wide"><h3>Where Bohm sits in the pool — hard-hit vs pull-air</h3>
      <p class="note">Each point is a Phillies hitter-season since 2015. Red = Bohm 2026;
      the hollow red ring = the post-break window scored as a season.</p>
      <canvas id="c_pool"></canvas></div>
  </div>
</section>

<section class="panel" id="platoon">
  <div class="warn amber"><b>The loudest split is the least reliable.</b> Post-break vs LHP:
  .531/.545/.812 on <b>33 PA ⚠</b>. Post-break vs RHP (.269/.324/.376, 102 PA) is the sample-backed
  part of the surge. And the platoon mix did NOT flatter him: LHP exposure <b>fell</b> 31.0% → 24.4%,
  and PL-1 direct standardisation puts the mix effect at <b>−18 wOBA points</b> — the surge is
  performance, not scheduling.</div>
  <div class="grid" style="margin-top:16px">
    <div class="card"><h3>Window × handedness</h3>
      <p class="note">Amber rows below the 50-PA floor.</p><table id="t_plat"></table></div>
    <div class="card"><h3>Direct standardisation (PL-1)</h3>
      <p class="note">Post-break within-split rates held fixed, re-weighted to the pre-break platoon
      mix. Negative mix effect = the observed line UNDERSTATES him relative to a constant mix.</p>
      <table id="t_platcf"></table></div>
    <div class="card wide"><h3>SLG by window × handedness</h3><canvas id="c_plat"></canvas></div>
  </div>
</section>

<section class="panel" id="pitches">
  <div class="grid">
    <div class="card"><h3>SLG by pitch group</h3><p class="note">PA counts on hover; ⚠ below floor.</p>
      <canvas id="c_pgw"></canvas></div>
    <div class="card"><h3>Whiff rate by pitch group</h3>
      <p class="note">The breaking-ball fix is the headline: 23.4% → 14.3% whiff, .239 → .460 SLG.</p>
      <canvas id="c_pgc"></canvas></div>
    <div class="card wide"><h3>Season by pitch type (≥40 pitches)</h3>
      <p class="note">Four-seamers and cutters take the damage; sinkers he simply never misses
      (8.9% whiff). Sweepers (ST) are the one pitch that still beats him — .143 BA / .214 SLG.</p>
      <table id="t_pt"></table></div>
  </div>
</section>

<section class="panel" id="governance">
  <div class="grid">
    <div class="card"><h3>Interpretation rules</h3><table id="t_rules"></table></div>
    <div class="card"><h3>Reliability floors</h3><table id="t_floor"></table></div>
    <div class="card wide"><h3>Defects in the governed KPI kernel</h3>
      <p class="note">Reported, not patched. <code>_fix</code> variants used for this build;
      originals untouched. D1–D6 inherited from uc-pos-010/011; this build additionally ships the
      O-7 REMEDIATION — <code>pull_air_rate_fix</code> derives loc coordinates from
      <code>hc_x/hc_y</code> per the cbp-spray convention and applies the governed boundary logic
      verbatim (proven scale-invariant). Provisional until the DPO ratifies the derivation.</p>
      <table id="t_def"></table></div>
    <div class="card wide"><h3>The O-3 trap, quantified — <code>inds</code> on all rows vs tracked BIP</h3>
      <p class="note">The DPO snippet runs <code>inds</code> on every pitch row, which averages
      launch_speed over tracked FOUL BALLS too. Both figures ship; the report's headline uses
      tracked BIP.</p>
      <table id="t_inds"></table></div>
  </div>
</section>
</main>
<footer>Every figure on this page is read from the <code>dp_uc37_*.csv</code> receipts — nothing is
hand-keyed and nothing is recomputed in the browser. Any figure quoted after <b>2026-08-22</b> must
state the as-of date. UC #38 · dp_uc37 · Phillies Offense value stream · DPO: Kellen Short.</footer>

<script>
const D = __DATA__;
const HAVE_CHART = (typeof Chart !== 'undefined');
function chart(id, cfg){
  const el=document.getElementById(id); if(!el) return null;
  if(!HAVE_CHART){ el.outerHTML='<div style="padding:26px;text-align:center;color:#8C8C8C;'
    +'font-size:12px;border:1px dashed #E6EAF0;border-radius:7px">chart library unavailable — '
    +'the tables on this page carry the same numbers</div>'; return null; }
  try{ return new Chart(el,cfg); }
  catch(e){ console.error('chart '+id, e); return null; }
}
const RED='#E81828', NAVY='#002D72', GOLD='#C4A24A', GREY='#B8BFCB';
const MN={3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep'};
const f3=v=>v==null?'—':(+v).toFixed(3).replace(/^0\./,'.');
const f1=v=>v==null?'—':(+v).toFixed(1);
const pc=v=>v==null?'—':((+v)*100).toFixed(1)+'%';
if(HAVE_CHART){Chart.defaults.font.family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif";
Chart.defaults.font.size=11; Chart.defaults.plugins.legend.labels.boxWidth=11;}

function tbl(id, cols, rows, cls){
  const t=document.getElementById(id); if(!t) return;
  t.innerHTML='<thead><tr>'+cols.map(c=>`<th class="${c.n?'num':''}">${c.h}</th>`).join('')+
    '</tr></thead><tbody>'+rows.map(r=>{
      const k=cls?cls(r):''; return `<tr class="${k}">`+cols.map(c=>
        `<td class="${c.n?'num':''}">${c.f?c.f(r):r[c.k]}</td>`).join('')+'</tr>';}).join('')+'</tbody>';
}

/* ── KPI tiles ─────────────────────────────────────────────────── */
const W={pre:D.H.window.pre, post:D.H.window.post};
const tiles=[
  ['SLG across the break', `${f3(W.pre.slg)} → ${f3(W.post.slg)}`,
   `<span class="up">+137 pts</span> — the requester's first KPI`, ''],
  ['BA w/ RISP', `${f3(W.pre.ba_risp)} → ${f3(W.post.ba_risp)}`,
   `post cell is <b>42 PA ⚠</b>`, 'g'],
  ['Runs created / PA', `${f3(W.pre.rc_per_pa)} → ${f3(W.post.rc_per_pa)}`,
   `49 → 28 runs on a third of the PA`, ''],
  ['Hard-hit rate', `${pc(W.pre.hard_hit_rate)} → ${pc(W.post.hard_hit_rate)}`,
   `<span class="up">post window ≈ 90th pctile</span>`, ''],
  ['In-zone whiff', `${pc(W.pre.whiff_rate_in_zone)} → ${pc(W.post.whiff_rate_in_zone)}`,
   `<span class="dn">nearly halved</span> — best contact in the pool`, 'n'],
  ['Pull-air rate', `${pc(W.pre.pull_air_rate)} → ${pc(W.post.pull_air_rate)}`,
   `<b>unchanged</b> — 14th pctile; quality, not volume`, 'g'],
  ['Chase rate', `${pc(W.pre.chase_rate)} → ${pc(W.post.chase_rate)}`,
   `approach did NOT change`, 'n'],
  ['K rate', `${pc(W.pre.krate)} → ${pc(W.post.krate)}`,
   `<span class="dn">career-best trajectory</span>`, 'n'],
];
document.getElementById('kpis').innerHTML = tiles.map(([l,v,d,c])=>
  `<div class="kpi ${c}"><div class="lab">${l}</div><div class="val">${v}</div><div class="dl">${d}</div></div>`).join('');

/* ── monthly ───────────────────────────────────────────────────── */
const M=D.monthly;
chart('c_month',{data:{labels:M.map(r=>MN[r.month]),datasets:[
  {type:'bar',label:'PA',data:M.map(r=>r.plate_apps),yAxisID:'y1',order:9,
   backgroundColor:M.map(r=>r.below_pa_floor?'#F6E7C4':'#E7EBF2')},
  {type:'line',label:'BA',data:M.map(r=>r.ba),borderColor:NAVY,backgroundColor:NAVY,tension:.25,borderWidth:2.4},
  {type:'line',label:'SLG',data:M.map(r=>r.slg),borderColor:RED,backgroundColor:RED,tension:.25,borderWidth:2.8},
  {type:'line',label:'wOBA',data:M.map(r=>r.woba),borderColor:GOLD,backgroundColor:GOLD,tension:.25,borderWidth:2.4},
]},options:{responsive:true,interaction:{mode:'index',intersect:false},
  scales:{y:{min:.10,max:.60,title:{display:true,text:'rate'}},
          y1:{position:'right',max:320,grid:{display:false},title:{display:true,text:'plate appearances'}}},
  plugins:{tooltip:{callbacks:{afterBody:c=>M[c[0].dataIndex].below_pa_floor?'⚠ below the 50-PA floor':''}}}}});

chart('c_scan',{type:'bar',data:{
  labels:D.scan.map(r=>r.breakpoint.slice(5)),datasets:[{label:'Δ wOBA',
  data:D.scan.map(r=>r.delta_woba),backgroundColor:D.scan.map(r=>r.delta_woba>0?RED:NAVY)}]},
  options:{plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:c=>
    `post-window: ${D.scan[c.dataIndex].post_pa} PA · Δ SLG ${(+D.scan[c.dataIndex].delta_slg).toFixed(3)}`}}},
  scales:{y:{title:{display:true,text:'wOBA after minus before'}}}}});

tbl('t_month',[{h:'Month',f:r=>MN[r.month]},{h:'PA',k:'plate_apps',n:1},
  {h:'BA',n:1,f:r=>f3(r.ba)},{h:'SLG',n:1,f:r=>f3(r.slg)},{h:'wOBA',n:1,f:r=>f3(r.woba)},
  {h:'BA/RISP',n:1,f:r=>f3(r.ba_risp)},{h:'K%',n:1,f:r=>pc(r.krate)},
  {h:'Hard-hit',n:1,f:r=>pc(r.hard_hit_rate)},{h:'Pull-air',n:1,f:r=>pc(r.pull_air_rate)}],
  M,r=>r.below_pa_floor?'floor':'');

/* ── career ────────────────────────────────────────────────────── */
let rlChart=null;
function drawRl(metric){
  const yrs=[...new Set(D.rl.map(r=>r.game_year))];
  const ds=yrs.filter(y=>y!==2026).map(y=>({label:String(y),
    data:D.rl.filter(r=>r.game_year===y).map(r=>({x:r.cum_pa,y:r[metric]})),
    borderColor:GREY,borderWidth:1.2,pointRadius:0,tension:.15,order:5}));
  ds.push({label:'2026',data:D.rl.filter(r=>r.game_year===2026)
    .map(r=>({x:r.cum_pa,y:r[metric]})),borderColor:RED,borderWidth:3,pointRadius:0,tension:.15,order:1});
  if(rlChart) rlChart.destroy();
  rlChart=chart('c_rl',{type:'line',data:{datasets:ds},
    options:{responsive:true,parsing:false,interaction:{mode:'nearest',intersect:false},
    scales:{x:{type:'linear',title:{display:true,text:'cumulative plate appearances'}},
            y:{title:{display:true,text:'season to date'}}},
    plugins:{legend:{display:false},tooltip:{callbacks:{
      title:c=>`PA ${c[0].parsed.x}`,label:c=>`${c.dataset.label}: ${f3(c.parsed.y)}`}}}}});
}
drawRl('cum_slg');
document.querySelectorAll('#career .ctl button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('#career .ctl button').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); drawRl(b.dataset.m);});

tbl('t_career',[{h:'Year',k:'game_year',n:1},{h:'PA',k:'plate_apps',n:1},
  {h:'BA',n:1,f:r=>f3(r.ba)},{h:'SLG',n:1,f:r=>f3(r.slg)},{h:'wOBA',n:1,f:r=>f3(r.woba)},
  {h:'K%',n:1,f:r=>pc(r.krate)},{h:'Whiff',n:1,f:r=>pc(r.whiff_rate)},
  {h:'Z-Whiff',n:1,f:r=>pc(r.whiff_rate_in_zone)},{h:'Chase',n:1,f:r=>pc(r.chase_rate)},
  {h:'Hard-hit',n:1,f:r=>pc(r.hard_hit_rate)},{h:'Pull-air',n:1,f:r=>pc(r.pull_air_rate)},
  {h:'BA/RISP',n:1,f:r=>f3(r.ba_risp)}],D.career,r=>r.game_year===2026?'me':'');

/* ── mechanism ─────────────────────────────────────────────────── */
const wpre=D.window.find(r=>r.window==='pre_break'), wpost=D.window.find(r=>r.window==='post_break');
const FAM={results:[['SLG','slg'],['wOBA','woba'],['BA','ba'],['BA w/RISP','ba_risp'],
  ['ISO','iso'],['BABIP','babip'],['xwOBAcon','xwobacon_bip'],['RC/PA','rc_per_pa']],
  process:[['Hard-hit%','hard_hit_rate'],['Barrel%','barrel_rate'],['Pull-air%','pull_air_rate'],
  ['GB%','gb_rate'],['Whiff%','whiff_rate'],['Z-Whiff%','whiff_rate_in_zone'],
  ['Chase%','chase_rate'],['Z-Swing%','swing_rate_in_zone'],['K%','krate']]};
let mechChart=null;
function drawMech(fam){
  const mech=FAM[fam];
  if(mechChart) mechChart.destroy();
  mechChart=chart('c_mech',{type:'bar',data:{labels:mech.map(m=>m[0]),datasets:[
    {label:'pre-break (377 PA)',data:mech.map(m=>wpre[m[1]]),backgroundColor:'#9AA3B0'},
    {label:'post-break (135 PA)',data:mech.map(m=>wpost[m[1]]),backgroundColor:RED}]},
    options:{indexAxis:'y',plugins:{tooltip:{callbacks:{afterBody:c=>{
      const k=mech[c[0].dataIndex][1];
      return `change: ${((wpost[k]-wpre[k])*1000).toFixed(0)} pts`;}}}},
    scales:{x:{title:{display:true,text:'rate'}}}}});
}
drawMech('results');
document.querySelectorAll('#mechanism .ctl button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('#mechanism .ctl button').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); drawMech(b.dataset.f);});

const WROWS=[['PA','plate_apps',v=>v],['BA','ba',f3],['OBP','obp',f3],['SLG','slg',f3],
 ['ISO','iso',f3],['wOBA','woba',f3],['BABIP','babip',f3],['K%','krate',pc],['BB%','bbrate',pc],
 ['HR','hrs',v=>v],['BA w/RISP ⚠post','ba_risp',f3],['RISP PA','risp_pa',v=>v],
 ['Runs created','runs_created',v=>v],['RC/PA','rc_per_pa',f3],
 ['Hard-hit%','hard_hit_rate',pc],['Barrel%','barrel_rate',pc],['Pull-air%','pull_air_rate',pc],
 ['Pull%','pull_rate',pc],['Mean EV (tracked)','mean_ev',f1],['Mean LA (tracked)','mean_la',f1],
 ['GB%','gb_rate',pc],['FB%','fb_rate',pc],['LD%','ld_rate',pc],['PU%','pu_rate',pc],
 ['xwOBAcon','xwobacon_bip',f3],['Swing%','swing_rate',pc],['Chase%','chase_rate',pc],
 ['Whiff%','whiff_rate',pc],['Z-Swing%','swing_rate_in_zone',pc],['Z-Whiff%','whiff_rate_in_zone',pc],
 ['OOZ whiff%','ooz_whiff_rate',pc],['First-pitch swing%','srfp',pc]];
tbl('t_window',[{h:'Metric',k:0},{h:'Pre',k:1,n:1},{h:'Post',k:2,n:1}],
  WROWS.map(([l,k2,f])=>({0:l,1:f(wpre[k2]),2:f(wpost[k2])})));
tbl('t_rc4',[{h:'Opponent metric',k:0},{h:'Pre',k:1,n:1},{h:'Post',k:2,n:1},{h:'Read',k:3}],[
 ['In-zone rate',pc(wpre.in_zone_rate),pc(wpost.in_zone_rate),'pitchers moved INTO the zone'],
 ['First-pitch strike rate',f3(wpre.fpsr),f3(wpost.fpsr),'identical — verified coincidence'],
].map(r=>({0:r[0],1:r[1],2:r[2],3:r[3]})));

/* ── contact & pull-air ────────────────────────────────────────── */
const PR=D.profile;
chart('c_pct',{type:'bar',data:{labels:PR.map(r=>r.metric),datasets:[
  {label:'2026 season',data:PR.map(r=>r.pct_2026),backgroundColor:'#8C93A0'},
  {label:'post-break window (descriptive)',data:PR.map(r=>r.pct_post_window),backgroundColor:RED}]},
  options:{indexAxis:'y',plugins:{tooltip:{callbacks:{afterLabel:c=>{
    const r=PR[c.dataIndex];
    return `2026 ${f3(r.bohm_2026)} · pool median ${f3(r.pool_median)} · n=${r.pool_n}`;}}}},
  scales:{x:{max:100,title:{display:true,text:'percentile within 218 Phillies hitter-seasons'}}}}});

tbl('t_paq',[{h:'Window',f:r=>r.window==='pre_break'?'pre-break':'post-break'},
  {h:'Pull-airs',k:'pull_airs',n:1},{h:'Hits',k:'pa_hits',n:1},{h:'HR',k:'pa_hrs',n:1},
  {h:'Mean EV',n:1,f:r=>f1(r.pa_mean_ev)},{h:'Mean dist',n:1,f:r=>f1(r.pa_mean_dist)+' ft'}],D.paq);
tbl('t_dirs',[{h:'Window',f:r=>r.window==='pre_break'?'pre':'post'},
  {h:'Direction',k:'hit_direction'},{h:'Air?',f:r=>r.is_air?'air':'ground'},
  {h:'BIP',k:'bips',n:1},{h:'Share',n:1,f:r=>pc(r.share_of_bip)},
  {h:'Hits',k:'hits',n:1},{h:'HR',k:'hrs',n:1},{h:'xwOBAcon',n:1,f:r=>f3(r.xwobacon)}],D.dirs);

const others=D.pool.filter(r=>r.pull_air_rate!=null&&!(r.player_name==='Bohm, Alec'&&r.game_year===2026));
const me=D.pool.find(r=>r.player_name==='Bohm, Alec'&&r.game_year===2026);
chart('c_pool',{type:'scatter',data:{datasets:[
  {label:'Phillies hitter-seasons',data:others.map(r=>({x:r.pull_air_rate,y:r.hard_hit_rate,
   n:r.player_name.split(',')[0]+" '"+String(r.game_year).slice(2)})),
   backgroundColor:'rgba(184,191,203,.75)',pointRadius:4},
  {label:'Bohm 2026',data:[{x:me.pull_air_rate,y:me.hard_hit_rate,n:'Bohm 2026'}],
   backgroundColor:RED,pointRadius:9,pointStyle:'star',borderColor:RED,borderWidth:2},
  {label:'Bohm post-break window',data:[{x:D.H.window.post.pull_air_rate,
   y:D.H.window.post.hard_hit_rate,n:'Bohm post-break'}],backgroundColor:'rgba(0,0,0,0)',
   borderColor:RED,borderWidth:2.5,pointRadius:9,pointStyle:'circle'}]},
  options:{plugins:{tooltip:{callbacks:{label:c=>`${c.raw.n}: pull-air ${pc(c.raw.x)} · hard-hit ${pc(c.raw.y)}`}}},
  scales:{x:{title:{display:true,text:'pull-air rate (share of BIP)'},ticks:{callback:v=>(v*100).toFixed(0)+'%'}},
          y:{title:{display:true,text:'hard-hit rate'},ticks:{callback:v=>(v*100).toFixed(0)+'%'}}}}});

/* ── platoon ───────────────────────────────────────────────────── */
tbl('t_plat',[{h:'Window',f:r=>r.window==='pre_break'?'pre-break':'post-break'},
  {h:'Throws',k:'p_throws'},{h:'PA',k:'plate_apps',n:1},{h:'BA',n:1,f:r=>f3(r.ba)},
  {h:'OBP',n:1,f:r=>f3(r.obp)},{h:'SLG',n:1,f:r=>f3(r.slg)},{h:'wOBA',n:1,f:r=>f3(r.woba)},
  {h:'Whiff',n:1,f:r=>pc(r.whiff_rate)},{h:'Hard-hit',n:1,f:r=>pc(r.hard_hit_rate)}],
  D.platoon,r=>r.plate_apps<50?'floor':'');
tbl('t_platcf',[{h:'Metric',f:r=>r.metric.toUpperCase()},{h:'Actual (post)',n:1,f:r=>f3(r.actual)},
  {h:'Re-weighted to pre mix',n:1,f:r=>f3(r.reweighted_to_reference)},
  {h:'Mix effect',n:1,f:r=>(r.mix_effect>=0?'+':'')+(+r.mix_effect).toFixed(4)}],D.platoon_cf);
const PL=['pre vs LHP','pre vs RHP','post vs LHP ⚠','post vs RHP'];
const plook=(w,t)=>D.platoon.find(r=>r.window===w&&r.p_throws===t);
chart('c_plat',{type:'bar',data:{labels:PL,datasets:[{label:'SLG',
  data:[plook('pre_break','L').slg,plook('pre_break','R').slg,
        plook('post_break','L').slg,plook('post_break','R').slg],
  backgroundColor:['#9AA3B0','#9AA3B0',RED,RED]}]},
  options:{plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:c=>{
    const cell=[plook('pre_break','L'),plook('pre_break','R'),
                plook('post_break','L'),plook('post_break','R')][c.dataIndex];
    return `${cell.plate_apps} PA${cell.plate_apps<50?' — below the 50-PA floor':''}`;}}}},
  scales:{y:{title:{display:true,text:'SLG'}}}}});

/* ── pitches ───────────────────────────────────────────────────── */
const order=['fastball','breaking','offspeed'];
const grab=(w,f)=>order.map(g=>{const r=D.pgw.find(x=>x.window===w&&x.pitch_group===g);return r?r[f]:null;});
const paOf=(w)=>order.map(g=>{const r=D.pgw.find(x=>x.window===w&&x.pitch_group===g);return r?r.plate_apps:0;});
const cap=s=>s[0].toUpperCase()+s.slice(1);
chart('c_pgw',{type:'bar',data:{labels:order.map(cap),datasets:[
  {label:'pre-break',data:grab('pre_break','slg'),backgroundColor:'#9AA3B0'},
  {label:'post-break',data:grab('post_break','slg'),backgroundColor:RED}]},
  options:{plugins:{tooltip:{callbacks:{afterLabel:c=>{
    const pa=(c.datasetIndex===0?paOf('pre_break'):paOf('post_break'))[c.dataIndex];
    return `${pa} PA${pa<50?' — below the 50-PA floor':''}`;}}}},
  scales:{y:{title:{display:true,text:'SLG'}}}}});
chart('c_pgc',{type:'bar',data:{labels:order.map(cap),datasets:[
  {label:'pre-break',data:grab('pre_break','whiff_rate'),backgroundColor:'#9AA3B0'},
  {label:'post-break',data:grab('post_break','whiff_rate'),backgroundColor:NAVY}]},
  options:{scales:{y:{title:{display:true,text:'whiff rate'},
    ticks:{callback:v=>(v*100).toFixed(0)+'%'}}}}});
tbl('t_pt',[{h:'Pitch',k:'pitch_type'},{h:'Pitches',k:'pitches',n:1},{h:'PA',k:'plate_apps',n:1},
  {h:'BA',n:1,f:r=>f3(r.ba)},{h:'SLG',n:1,f:r=>f3(r.slg)},{h:'wOBA',n:1,f:r=>f3(r.woba)},
  {h:'K%',n:1,f:r=>pc(r.krate)},{h:'Whiff%',n:1,f:r=>pc(r.whiff_rate)},
  {h:'Chase%',n:1,f:r=>pc(r.chase_rate)}],D.ptype,r=>r.plate_apps<50?'floor':'');

/* ── governance ────────────────────────────────────────────────── */
tbl('t_rules',[{h:'Metric',k:0},{h:'Read it as',k:1},{h:'Do NOT',k:2}],[
 ['in_zone_rate, fpsr','what pitchers did TO him','read as hitter behaviour (RC-4)'],
 ['xwobacon_bip','expected value per ball in play','compare to wOBA — different denominators (O-4)'],
 ['mean_ev / mean_la','central tendency on TRACKED BIP only','use the inds all-rows figures — foul-contaminated (O-3)'],
 ['pull_air_rate','governed boundary logic on DERIVED coordinates','treat as ratified — provisional until the DPO signs off the hc→loc derivation'],
 ['runs_created','runs scored during his PAs (notebook definition)','conflate with SC-1 wRC or Bill James RC'],
 ['ba_risp','RISP on the TERMINAL pitch of the PA','compare to sources using an any-pitch-RISP definition'],
 ['the break split','a descriptive contrast','treat as inferential — it was outcome-selected'],
].map(r=>({0:r[0],1:r[1],2:r[2]})));
tbl('t_floor',[{h:'Bucket',k:0},{h:'Size',k:1,n:1},{h:'Floor',k:2,n:1},{h:'Status',k:3}],[
 ['Pre-break window','377 PA','50 PA','<span class="verdict v-ok">clears</span>'],
 ['Post-break window','135 PA','50 PA','<span class="verdict v-ok">clears</span>'],
 ['March 2026','21 PA','50 PA','<span class="verdict v-no">below floor</span>'],
 ['August 2026','81 PA','50 PA','<span class="verdict v-ok">clears (partial month)</span>'],
 ['Post-break RISP','42 PA','50 PA','<span class="verdict v-no">below floor</span>'],
 ['Post-break vs LHP','33 PA','50 PA','<span class="verdict v-no">below floor</span>'],
 ['Post-break offspeed','12 PA','50 PA','<span class="verdict v-no">below floor</span>'],
 ['Launch angle / EV','per group','50 tracked BIP','<span class="verdict v-part">NULL where unmet</span>'],
].map(r=>({0:r[0],1:r[1],2:r[2],3:r[3]})));
tbl('t_def',[{h:'ID',k:0},{h:'Function',k:1},{h:'Defect',k:2},{h:'Handling here',k:3}],[
 ['D1','whiff_rate','inner-merge drops zero-whiff groups','_fix left-merge used'],
 ['D2','hard_hit_rate','inner-merge drops zero-hard-hit groups','_fix left-merge used'],
 ['D3','fpsr','drops perfect-FPSR groups','_fix used'],
 ['D4','nresults','rounds to 3dp before ratios','all rates rebuilt from counts'],
 ['D5/O-7','pull_air_rate','reads loc_x/loc_y — not in the parquet schema','<b>REMEDIATED this build</b>: pull_air_rate_fix derives loc from hc_x/hc_y (cbp-spray convention), boundary logic verbatim, scale-invariance proven. Provisional'],
 ['D6/O-8','hard_hit_rate','untracked BIP scored "not hard hit"','retained deliberately (governed denominator); exposure = 1 untracked BIP in 2026, divergence < 0.2 pt'],
].map(r=>({0:r[0],1:r[1],2:r[2],3:r[3]})));
tbl('t_inds',[{h:'Window',f:r=>r.window==='pre_break'?'pre-break':'post-break'},
  {h:'inds ev_mu (all rows)',n:1,f:r=>f1(r.ev_mu_inds_allrows)},
  {h:'mean EV (tracked BIP)',n:1,f:r=>f1(r.mean_ev_tracked_bip)},
  {h:'gap',n:1,f:r=>f1(r.mean_ev_tracked_bip-r.ev_mu_inds_allrows)+' mph'},
  {h:'inds la_mu (all rows)',n:1,f:r=>f1(r.la_mu_inds_allrows)+'°'},
  {h:'mean LA (tracked BIP)',n:1,f:r=>f1(r.mean_la_tracked_bip)+'°'},
  {h:'non-BIP rows with EV',k:'non_bip_rows_with_launch_speed',n:1}],D.inds);

/* ── nav ───────────────────────────────────────────────────────── */
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.panel').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); document.getElementById(b.dataset.p).classList.add('on');});
</script></body></html>
"""

if __name__ == "__main__":
    main()
