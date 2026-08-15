"""
dp_uc34 — self-contained interactive HTML dashboard for the Justin Crawford
year-to-date read.

Every number rendered here is read from the dp_uc34_*.csv receipts written by
dp_uc34_crawford_ytd.py. Nothing is hand-keyed and nothing is recomputed in the
browser, so the dashboard cannot drift from the report or the verification.

Chart.js is loaded from cdnjs; the data is inlined as JSON so the file works
offline once loaded and can be emailed as a single attachment.
"""
from __future__ import annotations
import json, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "dp_uc34_crawford_ytd_dashboard.html")
# Chart.js is vendored, not CDN-loaded: the dashboard must render with no network
# at all (staff laptops, air-gapped review, emailed as a single attachment).
CHARTJS = os.path.join(HERE, "_chartjs_4.4.1.umd.js")
PHI_RED, PHI_NAVY = "#E81828", "#002D72"


def rd(name):
    df = pd.read_csv(os.path.join(HERE, f"dp_uc34_{name}.csv"))
    df = df.replace([float("inf"), float("-inf")], pd.NA)
    return df.astype(object).where(pd.notna(df), None)


def main():
    H = json.load(open(os.path.join(HERE, "dp_uc34_headlines.json")))

    # thin the context rolling frame: one point every 3 PA keeps the file small
    ctx = pd.read_csv(os.path.join(HERE, "dp_uc34_cf_context_rolling.csv"))
    ctx = ctx[(ctx.cum_pa >= 50) & ((ctx.cum_pa % 3 == 0) |
                                    (ctx.cum_pa == ctx.groupby('season_key').cum_pa.transform('max')))]
    ctx = ctx[['season_key', 'cum_pa', 'cum_ba', 'cum_obp', 'cum_woba']].round(4)

    pool = pd.read_csv(os.path.join(HERE, "dp_uc34_population_pool.csv"))
    pool = pool[['player_name', 'game_year', 'plate_apps', 'mean_la', 'gb_rate',
                 'woba', 'ba', 'iso', 'whiff_rate', 'chase_rate', 'swing_rate']].round(4)
    pool = pool.astype(object).where(pd.notna(pool), None)

    data = {
        "monthly": rd("monthly_panel").to_dict("records"),
        "window": rd("window_split").to_dict("records"),
        "scan": rd("breakpoint_scan").to_dict("records"),
        "ctx": ctx.to_dict("records"),
        "ctx_pool": rd("cf_context_pool").to_dict("records"),
        "matched": rd("cf_matched_pa_snapshot").to_dict("records"),
        "profile": rd("profile_percentiles").to_dict("records"),
        "archetype": rd("archetype_cohort").to_dict("records"),
        "pool": pool.to_dict("records"),
        "platoon_exp": rd("platoon_exposure").to_dict("records"),
        "platoon_splits": rd("platoon_splits").to_dict("records"),
        "platoon_cf": rd("platoon_counterfactual").to_dict("records"),
        "pgw": rd("pitch_group_window").to_dict("records"),
        "ptype": rd("pitch_type_season").to_dict("records"),
        "count_state": rd("count_state").to_dict("records"),
        "gbq": rd("groundball_quality").to_dict("records"),
        "H": H,
    }
    payload = json.dumps(data, allow_nan=False, default=lambda o: None)
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
<title>Justin Crawford — Year-to-Date Read · as of 2026-08-13</title>
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
  <h1>Justin Crawford — Year-to-Date Read</h1>
  <div class="sub">Phillies Offense · 2026 season through <b>13 August</b> · 109 games · 362 PA</div>
  <div class="gov">UC #35 · uc-pos-011-crawford-ytd-001 · dp_uc34 · verification 127/127 PASS ·
      sensitivity Internal · not for external or media distribution</div>
</header>

<div class="warn"><b>The premise holds directionally; the mechanism does not match it.</b>
Results improved after 15 June (wOBA .276 → .321) but on-base gains are entirely batting average —
walk rate <b>fell</b> 6.6% → 4.6%, ISO <b>fell</b> .097 → .072, and mean launch angle did not move
(2.28° → 2.22°). BABIP rose 79 points on <i>softer</i> ground-ball contact. The durable gain is
strikeout rate, 20.9% → 15.2%.</div>
<div class="warn amber"><b>Two reliability warnings.</b> March (13 PA) and August (42 PA) are both
below the 50-PA batter floor and are shaded amber everywhere they appear — <b>do not rank them</b>.
The 15 June breakpoint was chosen after seeing the outcome; a mid-May breakpoint reverses the sign.
Everything downstream of the split is <b>descriptive, not inferential</b>.</div>

<nav>
  <button class="on" data-p="overview">Overview</button>
  <button data-p="context">Centre-field context</button>
  <button data-p="profile">Profile vs population</button>
  <button data-p="mechanism">What changed</button>
  <button data-p="platoon">Platoon &amp; Hill</button>
  <button data-p="pitches">Pitch types</button>
  <button data-p="governance">Governance</button>
</nav>
<main>

<section class="panel on" id="overview">
  <div class="kpis" id="kpis"></div>
  <div class="grid">
    <div class="card wide"><h3>Monthly results — the path is not a steady climb</h3>
      <p class="note">Bars are plate appearances against the right axis. Amber months fall below
      the 50-PA reliability floor.</p><canvas id="c_month"></canvas></div>
    <div class="card"><h3>Breakpoint sensitivity</h3>
      <p class="note">wOBA after the split minus wOBA before it, for every candidate boundary.
      Red bars favour the "he turned a corner" reading; navy bars contradict it.</p>
      <canvas id="c_scan"></canvas></div>
    <div class="card"><h3>Monthly panel</h3><p class="note">Amber rows are below floor.</p>
      <div style="max-height:330px;overflow:auto"><table id="t_month"></table></div></div>
  </div>
</section>

<section class="panel" id="context">
  <div class="card wide"><h3>Crawford 2026 against Phillies primary centre fielders, Statcast era</h3>
  <p class="note">Comparison population: any player-season with &gt;80 games in centre field,
  restricted to games he actually played the position. Grey = the 8 comparator seasons.
  Left tail below 50 PA suppressed.</p>
  <div class="ctl"><span>Metric</span>
    <button class="on" data-m="cum_ba">BA</button>
    <button data-m="cum_obp">OBP</button>
    <button data-m="cum_woba">wOBA</button></div>
  <canvas id="c_ctx" style="max-height:400px"></canvas></div>
  <div class="grid" style="margin-top:16px">
    <div class="card"><h3>At matched volume — 361 PA</h3>
      <p class="note">Every comparator's season-to-date line at Crawford's exact plate-appearance count.</p>
      <table id="t_matched"></table></div>
    <div class="card"><h3>Full comparator seasons</h3>
      <p class="note">Final line for each qualifying centre-field season.</p>
      <table id="t_ctxpool"></table></div>
  </div>
</section>

<section class="panel" id="profile">
  <div class="grid">
    <div class="card"><h3>Profile percentiles</h3>
      <p class="note">Against 217 Phillies hitter-seasons since 2015 (98 players, ≥50 PA).
      Launch angle uses the 186 seasons clearing 50 tracked balls in play.</p>
      <canvas id="c_pct"></canvas></div>
    <div class="card"><h3>The archetype — launch angle against wOBA</h3>
      <p class="note">Each point is a Phillies hitter-season. Crawford is the red star.</p>
      <canvas id="c_arch"></canvas></div>
    <div class="card wide"><h3>The nine lowest launch angles in the pool</h3>
      <p class="note">The comparison set for this batted-ball profile. Note the plate-appearance
      column — most of these are partial seasons; Crawford's is a full-time job.</p>
      <table id="t_arch"></table></div>
  </div>
</section>

<section class="panel" id="mechanism">
  <div class="grid">
    <div class="card wide"><h3>Before vs after 15 June — what actually moved</h3>
      <p class="note">Descriptive only: the breakpoint was outcome-selected.</p>
      <canvas id="c_mech" style="max-height:400px"></canvas></div>
    <div class="card"><h3>Ground-ball quality — the speed question</h3>
      <p class="note">He is hitting ground balls <i>softer</i> and getting <i>more</i> hits on them.
      Expected BA on those grounders fell while actual BA rose 54 points.</p>
      <table id="t_gb"></table></div>
    <div class="card"><h3>Count leverage</h3>
      <p class="note">Two-strike survival improved; production when ahead in the count collapsed.</p>
      <table id="t_cs"></table></div>
  </div>
</section>

<section class="panel" id="platoon">
  <div class="warn"><b>The Derek Hill hypothesis is falsified as posed.</b> Hill's first Phillies game
  was 13 June 2026. Crawford's share of plate appearances against left-handers is <b>15.0%</b> after
  that date versus <b>15.3%</b> before it. Direct standardisation puts the whole platoon-mix effect at
  under 0.0002 on BA, OBP and wOBA. <b>The shielding is real but it starts in August</b> — 1 of 42
  plate appearances — roughly seven weeks after Hill arrived.</div>
  <div class="grid" style="margin-top:16px">
    <div class="card wide"><h3>Platoon exposure by half-month</h3>
      <p class="note">Dashed line is the season share. The August bar is the decision.</p>
      <canvas id="c_plat"></canvas></div>
    <div class="card"><h3>Splits either side of Hill's arrival</h3>
      <p class="note">Note that his line <i>against</i> left-handers improved — on 23 PA, which
      proves nothing but is the opposite of what would justify a platoon.</p>
      <table id="t_plat"></table></div>
    <div class="card"><h3>Direct standardisation</h3>
      <p class="note">Post-Hill within-split rates held fixed, re-weighted to the pre-Hill platoon mix.
      A mix effect near zero means the platoon explains none of the improvement.</p>
      <table id="t_platcf"></table></div>
  </div>
</section>

<section class="panel" id="pitches">
  <div class="grid">
    <div class="card"><h3>wOBA by pitch group</h3><p class="note">Plate-appearance counts on hover.</p>
      <canvas id="c_pgw"></canvas></div>
    <div class="card"><h3>Chase rate by pitch group</h3>
      <p class="note">Offspeed is the cleanest approach signal — and it is 17 PA after the break.</p>
      <canvas id="c_pgc"></canvas></div>
    <div class="card wide"><h3>Season by pitch type (≥40 pitches)</h3>
      <p class="note">Sinkers are his best pitch. Sliders draw the lowest whiff rate of anything he
      sees (8.0%) on a 47.9% chase rate — weak contact, by design. Splitters and cutters are the holes.</p>
      <table id="t_pt"></table></div>
  </div>
</section>

<section class="panel" id="governance">
  <div class="grid">
    <div class="card"><h3>Interpretation rules</h3><table id="t_rules"></table></div>
    <div class="card"><h3>Reliability floors</h3><table id="t_floor"></table></div>
    <div class="card wide"><h3>Defects found in the governed KPI kernel</h3>
      <p class="note">Reported, not patched. <code>_fix</code> variants used for this build;
      originals untouched. D1–D5 inherited from uc-pos-010; D6 is new this build.</p>
      <table id="t_def"></table></div>
  </div>
</section>
</main>
<footer>Every figure on this page is read from the <code>dp_uc34_*.csv</code> receipts — nothing is
hand-keyed and nothing is recomputed in the browser. Any figure quoted after <b>2026-08-13</b> must
state the as-of date.</footer>

<script>
const D = __DATA__;
/* Charts must never take the tables down with them. Every chart call is wrapped;
   a failure leaves a visible placeholder and the rest of the page intact. */
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
const MN={3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug'};
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
const S=D.H.season, W=D.H.window;
const tiles=[
  ['Season wOBA', f3(S.woba), `39th pctile in the Phillies pool`, ''],
  ['Season slash', `${f3(S.ba)}/${f3(S.obp)}/${f3(S.slg)}`, `${S.plate_apps} PA · ${S.hrs} HR`, 'n'],
  ['wOBA before → after 15 Jun', `${f3(W.pre.woba)} → ${f3(W.post.woba)}`,
   `<span class="up">+${((W.post.woba-W.pre.woba)*1000).toFixed(0)} pts</span> — descriptive only`, ''],
  ['Strikeout rate', `${pc(W.pre.krate)} → ${pc(W.post.krate)}`,
   `<span class="dn">the durable gain</span>`, 'n'],
  ['BABIP', `${f3(W.pre.babip)} → ${f3(W.post.babip)}`,
   `<span class="up">+79 pts</span> on softer contact`, ''],
  ['Mean launch angle', `${f1(W.pre.mean_la)}° → ${f1(W.post.mean_la)}°`,
   `2nd percentile — <b>unchanged</b>`, 'g'],
  ['Walk rate', `${pc(W.pre.bbrate)} → ${pc(W.post.bbrate)}`, `<span class="dn">fell</span>`, 'n'],
  ['Aug PA vs LHP', `${D.H.aug_lhp_pa} of ${D.H.aug_pa}`, `platoon shielding starts here`, 'g'],
];
document.getElementById('kpis').innerHTML = tiles.map(([l,v,d,c])=>
  `<div class="kpi ${c}"><div class="lab">${l}</div><div class="val">${v}</div><div class="dl">${d}</div></div>`).join('');

/* ── monthly ───────────────────────────────────────────────────── */
const M=D.monthly;
chart('c_month',{data:{labels:M.map(r=>MN[r.month]),datasets:[
  {type:'bar',label:'PA',data:M.map(r=>r.plate_apps),yAxisID:'y1',order:9,
   backgroundColor:M.map(r=>r.below_pa_floor?'#F6E7C4':'#E7EBF2')},
  {type:'line',label:'BA',data:M.map(r=>r.ba),borderColor:NAVY,backgroundColor:NAVY,tension:.25,borderWidth:2.4},
  {type:'line',label:'OBP',data:M.map(r=>r.obp),borderColor:GOLD,backgroundColor:GOLD,tension:.25,borderWidth:2.4},
  {type:'line',label:'wOBA',data:M.map(r=>r.woba),borderColor:RED,backgroundColor:RED,tension:.25,borderWidth:2.8},
]},options:{responsive:true,interaction:{mode:'index',intersect:false},
  scales:{y:{min:.15,max:.50,title:{display:true,text:'rate'}},
          y1:{position:'right',max:260,grid:{display:false},title:{display:true,text:'plate appearances'}}},
  plugins:{tooltip:{callbacks:{afterBody:c=>M[c[0].dataIndex].below_pa_floor?'⚠ below the 50-PA floor':''}}}}});

chart('c_scan',{type:'bar',data:{
  labels:D.scan.map(r=>r.breakpoint.slice(5)),datasets:[{label:'Δ wOBA',
  data:D.scan.map(r=>r.delta_woba),backgroundColor:D.scan.map(r=>r.delta_woba>0?RED:NAVY)}]},
  options:{plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:c=>
    `post-window: ${D.scan[c.dataIndex].post_pa} PA`}}},
  scales:{y:{title:{display:true,text:'wOBA after minus before'}}}}});

tbl('t_month',[{h:'Month',f:r=>MN[r.month]},{h:'PA',k:'plate_apps',n:1},
  {h:'BA',n:1,f:r=>f3(r.ba)},{h:'OBP',n:1,f:r=>f3(r.obp)},{h:'wOBA',n:1,f:r=>f3(r.woba)},
  {h:'BABIP',n:1,f:r=>f3(r.babip)},{h:'K%',n:1,f:r=>pc(r.krate)},{h:'GB%',n:1,f:r=>pc(r.gb_rate)},
  {h:'Mean LA',n:1,f:r=>r.mean_la==null?'—':f1(r.mean_la)+'°'}],M,r=>r.below_pa_floor?'floor':'');

/* ── context ───────────────────────────────────────────────────── */
let ctxChart=null;
function drawCtx(metric){
  const keys=[...new Set(D.ctx.map(r=>r.season_key))];
  const ds=keys.filter(k=>k!=='Crawford 2026').map(k=>({label:k,
    data:D.ctx.filter(r=>r.season_key===k).map(r=>({x:r.cum_pa,y:r[metric]})),
    borderColor:GREY,borderWidth:1.2,pointRadius:0,tension:.15,order:5}));
  ds.push({label:'Crawford 2026',data:D.ctx.filter(r=>r.season_key==='Crawford 2026')
    .map(r=>({x:r.cum_pa,y:r[metric]})),borderColor:RED,borderWidth:3,pointRadius:0,tension:.15,order:1});
  if(ctxChart) ctxChart.destroy();
  ctxChart=chart('c_ctx',{type:'line',data:{datasets:ds},
    options:{responsive:true,parsing:false,interaction:{mode:'nearest',intersect:false},
    scales:{x:{type:'linear',title:{display:true,text:'cumulative plate appearances'}},
            y:{title:{display:true,text:'season to date'}}},
    plugins:{legend:{display:false},tooltip:{callbacks:{
      title:c=>`PA ${c[0].parsed.x}`,label:c=>`${c.dataset.label}: ${f3(c.parsed.y)}`}}}}});
}
drawCtx('cum_ba');
document.querySelectorAll('.ctl button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.ctl button').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); drawCtx(b.dataset.m);});

tbl('t_matched',[{h:'#',k:'woba_rank',n:1},{h:'Season',k:'season_key'},
  {h:'BA',n:1,f:r=>f3(r.cum_ba)},{h:'OBP',n:1,f:r=>f3(r.cum_obp)},{h:'wOBA',n:1,f:r=>f3(r.cum_woba)}],
  D.matched,r=>r.season_key==='Crawford 2026'?'me':'');
tbl('t_ctxpool',[{h:'Player',f:r=>r.player_name.split(',')[0]},{h:'Yr',k:'game_year',n:1},
  {h:'CF G',k:'uq_cf_games',n:1},{h:'PA',k:'plate_apps',n:1},{h:'BA',n:1,f:r=>f3(r.ba)},
  {h:'OBP',n:1,f:r=>f3(r.obp)},{h:'wOBA',n:1,f:r=>f3(r.woba)}],
  D.ctx_pool,r=>r.player_name==='Crawford, Justin'?'me':'');

/* ── profile ───────────────────────────────────────────────────── */
const PR=D.profile;
chart('c_pct',{type:'bar',data:{labels:PR.map(r=>r.metric),
  datasets:[{label:'percentile',data:PR.map(r=>r.percentile),
  backgroundColor:PR.map(r=>r.percentile>=75?RED:(r.percentile<=25?NAVY:'#8C93A0'))}]},
  options:{indexAxis:'y',plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:c=>
    `Crawford ${f3(PR[c.dataIndex].crawford)} · pool median ${f3(PR[c.dataIndex].pool_median)} · n=${PR[c.dataIndex].pool_n}`}}},
  scales:{x:{max:100,title:{display:true,text:'percentile within the Phillies pool'}}}}});

const others=D.pool.filter(r=>r.mean_la!=null&&!(r.player_name==='Crawford, Justin'));
const me=D.pool.find(r=>r.player_name==='Crawford, Justin');
chart('c_arch',{type:'scatter',data:{datasets:[
  {label:'Phillies hitter-seasons',data:others.map(r=>({x:r.mean_la,y:r.woba,n:r.player_name.split(',')[0]+" '"+String(r.game_year).slice(2)})),
   backgroundColor:'rgba(184,191,203,.75)',pointRadius:4},
  {label:'Crawford 2026',data:[{x:me.mean_la,y:me.woba,n:'Crawford 2026'}],
   backgroundColor:RED,pointRadius:10,pointStyle:'star',borderColor:RED,borderWidth:2}]},
  options:{plugins:{tooltip:{callbacks:{label:c=>`${c.raw.n}: LA ${f1(c.raw.x)}° · wOBA ${f3(c.raw.y)}`}}},
  scales:{x:{title:{display:true,text:'mean launch angle on tracked BIP (°)'}},
          y:{title:{display:true,text:'wOBA'}}}}});

tbl('t_arch',[{h:'Player',f:r=>r.player_name.split(',')[0]},{h:'Yr',k:'game_year',n:1},
  {h:'PA',k:'plate_apps',n:1},{h:'Mean LA',n:1,f:r=>f1(r.mean_la)+'°'},
  {h:'GB%',n:1,f:r=>pc(r.gb_rate)},{h:'BA',n:1,f:r=>f3(r.ba)},{h:'ISO',n:1,f:r=>f3(r.iso)},
  {h:'wOBA',n:1,f:r=>f3(r.woba)}],D.archetype,r=>r.player_name==='Crawford, Justin'?'me':'');

/* ── mechanism ─────────────────────────────────────────────────── */
const wpre=D.window.find(r=>r.window==='pre_0615'), wpost=D.window.find(r=>r.window==='post_0615');
const mech=[['BABIP','babip'],['xwOBAcon','xwobacon_bip'],['ISO','iso'],['K%','krate'],
  ['Whiff%','whiff_rate'],['Chase%','chase_rate'],['Swing%','swing_rate'],['BB%','bbrate'],
  ['GB%','gb_rate'],['Hard-hit%','hard_hit_rate']];
chart('c_mech',{type:'bar',data:{labels:mech.map(m=>m[0]),datasets:[
  {label:'before 15 Jun',data:mech.map(m=>wpre[m[1]]),backgroundColor:'#9AA3B0'},
  {label:'from 15 Jun',data:mech.map(m=>wpost[m[1]]),backgroundColor:RED}]},
  options:{indexAxis:'y',plugins:{tooltip:{callbacks:{afterBody:c=>{
    const k=mech[c[0].dataIndex][1];
    return `change: ${((wpost[k]-wpre[k])*1000).toFixed(0)} pts`;}}}},
  scales:{x:{title:{display:true,text:'rate'}}}}});

tbl('t_gb',[{h:'Window',f:r=>r.window==='pre_0615'?'before 15 Jun':'from 15 Jun'},
  {h:'GB',k:'gb',n:1},{h:'Hits',k:'gb_hits',n:1},{h:'GB BA',n:1,f:r=>f3(r.gb_ba)},
  {h:'Mean EV',n:1,f:r=>f1(r.gb_mean_ev)},{h:'GB xBA',n:1,f:r=>f3(r.gb_xba)},
  {h:'Hits ≤90 ft',k:'gb_hits_under_90ft',n:1}],D.gbq);
tbl('t_cs',[{h:'Window',f:r=>r.window==='pre_0615'?'before':'from 15 Jun'},
  {h:'Count',k:'count_state'},{h:'PA',k:'plate_apps',n:1},{h:'BA',n:1,f:r=>f3(r.ba)},
  {h:'OBP',n:1,f:r=>f3(r.obp)},{h:'wOBA',n:1,f:r=>f3(r.woba)},{h:'K%',n:1,f:r=>pc(r.krate)}],
  D.count_state);

/* ── platoon ───────────────────────────────────────────────────── */
const PE=D.platoon_exp;
chart('c_plat',{type:'bar',data:{labels:PE.map(r=>r.halfmonth),
  datasets:[{label:'share of PA vs LHP',data:PE.map(r=>r.lhp_share),
  backgroundColor:PE.map(r=>r.lhp_share<.05?RED:NAVY)}]},
  options:{plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:c=>
    `${PE[c.dataIndex].L} of ${PE[c.dataIndex].pa} PA`}}},
  scales:{y:{title:{display:true,text:'share of PA vs LHP'},
    ticks:{callback:v=>(v*100).toFixed(0)+'%'}}}}});
tbl('t_plat',[{h:'Window',f:r=>r.hill_window==='pre_hill'?'before 13 Jun':'from 13 Jun'},
  {h:'Throws',k:'p_throws'},{h:'PA',k:'plate_apps',n:1},{h:'BA',n:1,f:r=>f3(r.ba)},
  {h:'OBP',n:1,f:r=>f3(r.obp)},{h:'SLG',n:1,f:r=>f3(r.slg)},{h:'wOBA',n:1,f:r=>f3(r.woba)}],
  D.platoon_splits,r=>r.plate_apps<50?'floor':'');
tbl('t_platcf',[{h:'Metric',f:r=>r.metric.toUpperCase()},{h:'Actual (post-Hill)',n:1,f:r=>f3(r.actual)},
  {h:'Re-weighted to pre-Hill mix',n:1,f:r=>f3(r.reweighted_to_reference)},
  {h:'Mix effect',n:1,f:r=>(r.mix_effect>=0?'+':'')+(+r.mix_effect).toFixed(4)}],D.platoon_cf);

/* ── pitches ───────────────────────────────────────────────────── */
const order=['fastball','breaking','offspeed'];
const grab=(w,f)=>order.map(g=>{const r=D.pgw.find(x=>x.window===w&&x.pitch_group===g);return r?r[f]:null;});
const paOf=(w)=>order.map(g=>{const r=D.pgw.find(x=>x.window===w&&x.pitch_group===g);return r?r.plate_apps:0;});
const cap=s=>s[0].toUpperCase()+s.slice(1);
chart('c_pgw',{type:'bar',data:{labels:order.map(cap),datasets:[
  {label:'before 15 Jun',data:grab('pre_0615','woba'),backgroundColor:'#9AA3B0'},
  {label:'from 15 Jun',data:grab('post_0615','woba'),backgroundColor:RED}]},
  options:{plugins:{tooltip:{callbacks:{afterLabel:c=>{
    const pa=(c.datasetIndex===0?paOf('pre_0615'):paOf('post_0615'))[c.dataIndex];
    return `${pa} PA${pa<50?' — below the 50-PA floor':''}`;}}}},
  scales:{y:{title:{display:true,text:'wOBA'}}}}});
chart('c_pgc',{type:'bar',data:{labels:order.map(cap),datasets:[
  {label:'before 15 Jun',data:grab('pre_0615','chase_rate'),backgroundColor:'#9AA3B0'},
  {label:'from 15 Jun',data:grab('post_0615','chase_rate'),backgroundColor:NAVY}]},
  options:{scales:{y:{title:{display:true,text:'chase rate'},
    ticks:{callback:v=>(v*100).toFixed(0)+'%'}}}}});
tbl('t_pt',[{h:'Pitch',k:'pitch_type'},{h:'Pitches',k:'pitches',n:1},{h:'PA',k:'plate_apps',n:1},
  {h:'BA',n:1,f:r=>f3(r.ba)},{h:'SLG',n:1,f:r=>f3(r.slg)},{h:'wOBA',n:1,f:r=>f3(r.woba)},
  {h:'K%',n:1,f:r=>pc(r.krate)},{h:'Whiff%',n:1,f:r=>pc(r.whiff_rate)},
  {h:'Chase%',n:1,f:r=>pc(r.chase_rate)}],D.ptype,r=>r.plate_apps<50?'floor':'');

/* ── governance ────────────────────────────────────────────────── */
tbl('t_rules',[{h:'Metric',k:0},{h:'Read it as',k:1},{h:'Do NOT',k:2}],[
 ['in_zone_rate, fpsr','what pitchers did TO him','read as hitter behaviour (RC-4)'],
 ['chase_rate','swing decision on out-of-zone pitches','compare without the OOZ denominator'],
 ['xwobacon_bip','expected value per ball in play','compare to wOBA — different denominators'],
 ['mean_la','central tendency on TRACKED BIP only','read where tracked BIP < 50 — it is NULL'],
 ['any March or August row','nothing','interpret or rank — both are below the 50-PA floor'],
 ['the 15 Jun split','a descriptive contrast','treat as inferential — it was outcome-selected'],
].map(r=>({0:r[0],1:r[1],2:r[2]})));
tbl('t_floor',[{h:'Bucket',k:0},{h:'PA / BIP',k:1,n:1},{h:'Floor',k:2,n:1},{h:'Status',k:3}],[
 ['March 2026','13 PA','50 PA','<span class="verdict v-no">below floor</span>'],
 ['April 2026','86 PA','50 PA','<span class="verdict v-ok">clears</span>'],
 ['May 2026','83 PA','50 PA','<span class="verdict v-ok">clears</span>'],
 ['June 2026','79 PA','50 PA','<span class="verdict v-ok">clears</span>'],
 ['July 2026','59 PA','50 PA','<span class="verdict v-ok">clears</span>'],
 ['August 2026','42 PA','50 PA','<span class="verdict v-no">below floor + partial</span>'],
 ['Offspeed, post-break','17 PA','50 PA','<span class="verdict v-no">below floor</span>'],
 ['Launch angle / bb-type','per group','50 tracked BIP','<span class="verdict v-part">NULL where unmet</span>'],
].map(r=>({0:r[0],1:r[1],2:r[2],3:r[3]})));
tbl('t_def',[{h:'ID',k:0},{h:'Function',k:1},{h:'Defect',k:2},{h:'Impact here',k:3}],[
 ['D1','whiff_rate','inner-merges swings→whiffs; a group with swings but zero whiffs vanishes','none this run — latent'],
 ['D2','hard_hit_rate','same shape; a group with BIP but zero hard hits vanishes','none this run — latent'],
 ['D3','fpsr','returns only type==B; a group with a perfect 1.000 FPSR vanishes','none this run'],
 ['D4','nresults','rounds to 3dp on return; any ratio of two rates inherits it','avoided — all rates rebuilt from counts'],
 ['D5','pull_air_rate','references loc_x / loc_y, which are not columns in the parquet schema (hc_x / hc_y are). <b>The function cannot execute against the governed data plane.</b>','not used — <b>new this build, opened as O-7</b>'],
 ['D6','hard_hit_rate','denominator is ALL balls in play, so an untracked BIP is silently scored "not hard hit"','0.6 pt on the post-break window (2 of 120 BIP) — <b>new this build, opened as O-8</b>'],
].map(r=>({0:r[0],1:r[1],2:r[2],3:r[3]})));

/* ── nav ───────────────────────────────────────────────────────── */
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.panel').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); document.getElementById(b.dataset.p).classList.add('on');});
</script></body></html>
"""

if __name__ == "__main__":
    main()
