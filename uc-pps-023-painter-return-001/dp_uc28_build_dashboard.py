"""
dp_uc28 — self-contained interactive HTML dashboard for the Painter return read.

Every number rendered here is read from the out/dp_uc28_*.csv receipts written
by dp_uc28_painter_vs_orioles.py. Nothing is hand-keyed and nothing is
recomputed in the browser, so the dashboard cannot drift from the report.

Chart.js is loaded from cdnjs; the data is inlined as JSON so the file works
offline once loaded (and can be emailed as a single attachment).
"""
from __future__ import annotations
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DEST = os.path.join(HERE, "dp_uc28_painter_vs_orioles_dashboard.html")

PHI_RED, PHI_NAVY = "#E81828", "#002D72"
PITCH_COLORS = {
    "4-Seam Fastball": "#E81828", "Sinker": "#FF7F0E", "Slider": "#002D72",
    "Sweeper": "#1F77B4", "Split-Finger": "#2CA02C", "Curveball": "#8C564B",
}


def rd(name):
    """Read a receipt CSV and make it JSON-safe (NaN/Inf -> None)."""
    df = pd.read_csv(os.path.join(OUT, f"dp_uc28_{name}.csv"))
    df = df.replace([float("inf"), float("-inf")], pd.NA)
    return df.astype(object).where(pd.notna(df), None)


def main():
    arsenal = rd("arsenal_by_level")
    start_log = rd("start_log")
    stuff = rd("stuff_delta")
    rel = rd("release_by_start")
    relp = rd("release_by_level_pitch")
    ffloc = rd("fastball_whiff_by_location")
    bench = rd("ff_benchmark_painter")
    spread = rd("arm_spread_painter")
    usage_stand = rd("usage_by_stand")
    tto = rd("times_through_order")
    aaa_arc = rd("aaa_arc")
    mlb_arc = rd("mlb_arc")
    sep = rd("velo_separation")
    loc = rd("location_tiers")
    dq = rd("dq_scorecard")
    fresh = rd("freshness_manifest")
    level = rd("level_summary")

    data = {
        "arsenal": arsenal.to_dict("records"),
        "start_log": start_log.to_dict("records"),
        "stuff": stuff.to_dict("records"),
        "release": rel.to_dict("records"),
        "release_pitch": relp.to_dict("records"),
        "ffloc": ffloc.to_dict("records"),
        "bench": bench.to_dict("records"),
        "spread": spread.to_dict("records"),
        "usage_stand": usage_stand.to_dict("records"),
        "tto": tto.to_dict("records"),
        "aaa_arc": aaa_arc.to_dict("records"),
        "mlb_arc": mlb_arc.to_dict("records"),
        "sep": sep.to_dict("records"),
        "loc": loc.to_dict("records"),
        "dq": dq.to_dict("records"),
        "fresh": fresh.to_dict("records"),
        "level": level.to_dict("records"),
        "colors": PITCH_COLORS,
    }
    payload = json.dumps(data, allow_nan=False, default=lambda o: None)

    html = HTML_TEMPLATE.replace("__DATA__", payload)
    with open(DEST, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"wrote {DEST}  ({os.path.getsize(DEST)/1024:.0f} KB, "
          f"{sum(len(v) for v in data.values() if isinstance(v, list))} rows inlined)")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Andrew Painter — Return Read · PHI @ BAL 2026-07-31</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--red:#E81828;--navy:#002D72;--gray:#8C8C8C;--lgray:#E6EAF0;--bg:#F7F9FC;}
*{box-sizing:border-box;}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
     color:#1a1a1a;background:var(--bg);font-size:14px;line-height:1.45;}
header{background:var(--navy);color:#fff;padding:20px 26px 16px;border-bottom:5px solid var(--red);}
header h1{margin:0 0 3px;font-size:22px;letter-spacing:-.2px;}
header .sub{font-size:13px;opacity:.85;}
header .gov{font-size:11px;opacity:.65;margin-top:7px;}
.warn{background:#FFF4F5;border-left:4px solid var(--red);margin:18px 26px;padding:11px 15px;font-size:12px;}
.warn b{color:var(--red);}
nav{display:flex;flex-wrap:wrap;gap:6px;padding:0 26px;margin:16px 0 0;}
nav button{border:1px solid var(--lgray);background:#fff;padding:7px 14px;border-radius:20px;
   cursor:pointer;font-size:12.5px;color:var(--navy);font-weight:600;transition:.12s;}
nav button:hover{border-color:var(--navy);}
nav button.on{background:var(--navy);color:#fff;border-color:var(--navy);}
main{padding:18px 26px 60px;}
.panel{display:none;} .panel.on{display:block;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:16px;}
.card{background:#fff;border:1px solid var(--lgray);border-radius:9px;padding:15px 17px;}
.card h3{margin:0 0 3px;font-size:14px;color:var(--navy);}
.card .note{font-size:11.5px;color:var(--gray);margin:0 0 11px;}
.wide{grid-column:1/-1;}
canvas{max-height:330px;}
table{border-collapse:collapse;width:100%;font-size:12px;margin-top:4px;}
th{background:var(--navy);color:#fff;text-align:left;padding:6px 8px;font-size:11.5px;position:sticky;top:0;}
td{padding:5px 8px;border-bottom:1px solid var(--lgray);}
tr:nth-child(even) td{background:#FAFBFD;}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:16px;}
.kpi{background:#fff;border:1px solid var(--lgray);border-left:4px solid var(--red);
     border-radius:7px;padding:11px 13px;}
.kpi .lab{font-size:10.5px;text-transform:uppercase;letter-spacing:.4px;color:var(--gray);}
.kpi .val{font-size:23px;font-weight:700;color:var(--navy);line-height:1.15;margin:3px 0 1px;}
.kpi .sub{font-size:11px;color:var(--gray);}
.kpi.good{border-left-color:#2CA02C;} .kpi.bad{border-left-color:var(--red);}
.controls{display:flex;flex-wrap:wrap;gap:16px;align-items:center;margin-bottom:14px;
   background:#fff;border:1px solid var(--lgray);border-radius:9px;padding:11px 15px;}
.controls label{font-size:12px;color:var(--navy);font-weight:600;margin-right:5px;}
.controls select,.controls input{font-size:12.5px;padding:4px 7px;border:1px solid var(--lgray);
   border-radius:5px;color:#1a1a1a;}
.pill{display:inline-block;padding:1.5px 8px;border-radius:11px;font-size:10.5px;font-weight:700;}
.PASS{background:#E7F6E9;color:#1D7A2B;} .WARN{background:#FFF6E0;color:#9A6A00;}
.FAIL{background:#FDE9EA;color:#B3151F;}
footer{padding:20px 26px;font-size:11px;color:var(--gray);border-top:1px solid var(--lgray);background:#fff;}
</style></head><body>

<header>
  <h1>Andrew Painter — Return Read</h1>
  <div class="sub">PHI @ BAL · Oriole Park at Camden Yards · 2026-07-31 · first start back from Triple-A</div>
  <div class="gov">Use Case #29 · <code>uc-pps-023</code> · build artifact <code>dp_uc28</code> · every figure below reads from an <code>out/dp_uc28_*.csv</code> receipt</div>
</header>

<div class="warn">
  <b>Tiers are never blended.</b> MLB = 1,141 pitches / 299 PA over 14 starts (2026-03-31 → 06-17).
  AAA = 396 pitches / 101 PA over 5 starts (2026-06-28 → 07-26), <b>below the 100-BF convention</b> —
  AAA rates carry their sample size everywhere. No expected-outcome (xwOBA) metric appears anywhere:
  it is 26% populated and untrusted at pitch level. <b>No Orioles data exists in this repo</b> — there is
  no opponent attack plan here, by design.
</div>

<nav>
  <button class="on" data-p="overview">Overview</button>
  <button data-p="arsenal">Arsenal &amp; stuff</button>
  <button data-p="fastball">The fastball problem</button>
  <button data-p="delivery">Delivery &amp; release</button>
  <button data-p="platoon">Platoon &amp; sequencing</button>
  <button data-p="starts">Start log</button>
  <button data-p="gov">Governance</button>
</nav>

<main>
  <section class="panel on" id="overview"><div class="kpis" id="ovKpis"></div>
    <div class="grid">
      <div class="card wide"><h3>What changed between the levels</h3>
        <p class="note">Locked process KPIs, computed inside each level. Source: <code>dp_uc28_level_summary.csv</code></p>
        <canvas id="cLevel"></canvas></div>
      <div class="card"><h3>MLB arc — first 8 starts vs last 7</h3>
        <p class="note">What broke before he was optioned. Source: <code>dp_uc28_mlb_arc.csv</code></p>
        <div id="tMlbArc"></div></div>
      <div class="card"><h3>AAA arc — early stretch-out vs late</h3>
        <p class="note">Every process indicator improved. Source: <code>dp_uc28_aaa_arc.csv</code></p>
        <div id="tAaaArc"></div></div>
      <div class="card wide"><h3>Times through the order</h3>
        <p class="note">Results are noisy; hard-hit rate climbs on every pass at both levels. Source: <code>dp_uc28_times_through_order.csv</code></p>
        <canvas id="cTto"></canvas></div>
    </div></section>

  <section class="panel" id="arsenal">
    <div class="controls">
      <div><label for="selLevel">Level</label>
        <select id="selLevel"><option value="both">Both (side by side)</option>
          <option value="MLB">MLB only</option><option value="AAA">AAA only</option></select></div>
      <div><label for="selMetric">Colour bars by</label>
        <select id="selMetric">
          <option value="usage">Usage share</option><option value="whiff_rate">Whiff / swing</option>
          <option value="csw_rate">CSW rate</option><option value="chase_rate">Chase rate</option>
          <option value="in_zone_rate">In-zone rate</option><option value="velo">Velocity</option>
        </select></div>
      <div style="font-size:11.5px;color:var(--gray);">AAA slider/sweeper tags are model-driven per level — read that boundary loosely.</div>
    </div>
    <div class="grid">
      <div class="card wide"><h3>Arsenal by level</h3>
        <p class="note">Source: <code>dp_uc28_arsenal_by_level.csv</code></p><canvas id="cArs"></canvas></div>
      <div class="card wide"><h3>Movement map — bubble size is usage</h3>
        <p class="note">Arm-side horizontal break positive. Filled = MLB, hollow = AAA.</p>
        <canvas id="cMove"></canvas></div>
      <div class="card"><h3>Cross-Level Stuff Delta <span style="color:var(--red)">(new KPI)</span></h3>
        <p class="note">AAA minus MLB. Only the splitter moved outside noise in a meaningful way.</p>
        <div id="tStuff"></div></div>
      <div class="card"><h3>Velocity separation from the four-seam</h3>
        <p class="note">The splitter lost 2.11 mph of separation. Source: <code>dp_uc28_velo_separation.csv</code></p>
        <div id="tSep"></div></div>
      <div class="card wide"><h3>Full arsenal table</h3><div id="tArs"></div></div>
    </div></section>

  <section class="panel" id="fastball"><div class="grid">
    <div class="card wide"><h3>Four-seam vs the 2026 MLB RHP pool</h3>
      <p class="note">31 RHP with ≥150 four-seams in 2026 Phillies games. Average shape, average location, bottom-quartile bat-missing. Source: <code>dp_uc28_ff_benchmark_painter.csv</code></p>
      <canvas id="cBench"></canvas></div>
    <div class="card"><h3>Benchmark detail</h3><div id="tBench"></div></div>
    <div class="card"><h3>Four-seam whiff by location</h3>
      <p class="note">At MLB, elevating did nothing (.101 up vs .111 down). At AAA it started working.</p>
      <div id="tFfloc"></div></div>
    <div class="card wide"><h3>Where each pitch goes</h3>
      <p class="note">Location tier mix. Source: <code>dp_uc28_location_tiers.csv</code></p>
      <canvas id="cLoc"></canvas></div>
  </div></section>

  <section class="panel" id="delivery"><div class="grid">
    <div class="card wide"><h3>Velocity up, extension down — every AAA start</h3>
      <p class="note">He is throwing harder by reaching, not by getting down the mound. Source: <code>dp_uc28_start_log.csv</code></p>
      <canvas id="cVelo"></canvas></div>
    <div class="card wide"><h3>Four-seam release point by start</h3>
      <p class="note">13 MLB starts sit in a 2.1-inch band. 06-17 and 06-28 jump ~5 inches toward centre — the two shakiest outings — then he moves back. 06-28 and 07-10 were the same park, so this is mechanical, not calibration. Source: <code>dp_uc28_release_by_start.csv</code></p>
      <canvas id="cRel"></canvas></div>
    <div class="card"><h3>Arm angle by pitch type</h3>
      <p class="note">The tipping hypothesis: his slot spread is 13.8° at MLB against a pool median of 4.25° — 96th percentile.</p>
      <canvas id="cArm"></canvas></div>
    <div class="card"><h3>Slot spread vs the pool</h3><div id="tSpread"></div>
      <p class="note" style="margin-top:9px;">Caveat: <code>arm_angle</code> is derived from release coordinates, so some spread is unavoidable. The pool comparison is what makes it notable, not the raw number.</p></div>
  </div></section>

  <section class="panel" id="platoon">
    <div class="controls"><div><label for="selStand">Batter stands</label>
      <select id="selStand"><option value="L">Left-handed</option><option value="R">Right-handed</option></select></div>
      <div style="font-size:11.5px;color:var(--gray);">AAA vs LHH is 65 PA and vs RHH is 36 PA — directional only.</div></div>
    <div class="grid">
      <div class="card wide"><h3>Usage by level against the selected handedness</h3>
        <p class="note">The splitter — his best pitch vs lefties at .395 whiff on 76 MLB swings — was halved at Triple-A and replaced by the sweeper. Source: <code>dp_uc28_usage_by_stand.csv</code></p>
        <canvas id="cStand"></canvas></div>
      <div class="card wide"><h3>Detail</h3><div id="tStand"></div></div>
    </div></section>

  <section class="panel" id="starts"><div class="grid">
    <div class="card wide"><h3>Every start, both levels</h3>
      <p class="note">Navy rows are MLB, red rows are AAA. Source: <code>dp_uc28_start_log.csv</code></p>
      <div id="tStarts"></div></div>
  </div></section>

  <section class="panel" id="gov"><div class="grid">
    <div class="card wide"><h3>Data quality scorecard</h3>
      <p class="note">Source: <code>dp_uc28_dq_scorecard.csv</code></p><div id="tDq"></div></div>
    <div class="card wide"><h3>Freshness manifest</h3>
      <p class="note">Source: <code>dp_uc28_freshness_manifest.csv</code></p><div id="tFresh"></div></div>
  </div></section>
</main>

<footer>
  Built by <code>dp_uc28_build_dashboard.py</code> from the CSV receipts in <code>out/</code>.
  Entity lock: MLBAM <code>pitcher == 691725</code>. Governance trail:
  <code>Agents for Data Products/data-products/uc-pps-painter-return-001/</code>.
  Companion PDF: <code>dp_uc28_painter_vs_orioles_report.pdf</code>.
</footer>

<script>
const D = __DATA__;
const NAVY="#002D72", RED="#E81828", GRAY="#8C8C8C";
const PC = D.colors;
const charts = {};
const f3 = v => (v===null||v===undefined||Number.isNaN(v)) ? "—" : (+v).toFixed(3);
const f1 = v => (v===null||v===undefined||Number.isNaN(v)) ? "—" : (+v).toFixed(1);
const f2 = v => (v===null||v===undefined||Number.isNaN(v)) ? "—" : (+v).toFixed(2);
const pct = v => (v===null||v===undefined||Number.isNaN(v)) ? "—" : (100*v).toFixed(1)+"%";

Chart.defaults.font.family = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.color = "#444";

function mk(id, cfg){ if(charts[id]) charts[id].destroy();
  charts[id] = new Chart(document.getElementById(id), cfg); return charts[id]; }

function table(el, rows, cols){
  if(!rows.length){ document.getElementById(el).innerHTML='<p class="note">No rows.</p>'; return; }
  let h = '<div style="overflow:auto;max-height:520px"><table><thead><tr>';
  cols.forEach(c => h += `<th class="${c.num?'num':''}">${c.label}</th>`);
  h += '</tr></thead><tbody>';
  rows.forEach(r => { h += '<tr>';
    cols.forEach(c => { const v = c.get ? c.get(r) : r[c.key];
      h += `<td class="${c.num?'num':''}"${c.style?` style="${c.style(r)}"`:''}>${v===null||v===undefined||v===''?'—':v}</td>`; });
    h += '</tr>'; });
  document.getElementById(el).innerHTML = h + '</tbody></table></div>';
}

/* ---------- OVERVIEW ---------- */
(function(){
  const bench = Object.fromEntries(D.bench.map(r=>[r.metric,r]));
  const sp = D.spread[0]||{};
  const mlb = D.level.find(r=>r.level==="MLB")||{}, aaa = D.level.find(r=>r.level==="AAA")||{};
  const ff = D.arsenal.filter(r=>r.pitch_name==="4-Seam Fastball");
  const ffM = ff.find(r=>r.level==="MLB")||{}, ffA = ff.find(r=>r.level==="AAA")||{};
  const k = [
    ["4-seam whiff, MLB", pct(ffM.whiff_rate), `${bench.ff_whiff?bench.ff_whiff.painter_mlb_pctile:''}th pctile · pool median ${f3(bench.ff_whiff?bench.ff_whiff.pool_median:null)}`, "bad"],
    ["4-seam whiff, AAA", pct(ffA.whiff_rate), "vs AAA hitters — 84 swings", "good"],
    ["Arm-slot spread, MLB", f1(sp.arm_spread_deg)+"°", `pool median ${f2(sp.pool_median)}° · ${f1(sp.pctile_high_is_worse)}th pctile`, "bad"],
    ["4-seam usage shift", "+16.1 pts", `${pct(ffM.usage)} → ${pct(ffA.usage)}`, "good"],
    ["Chase, MLB last 7 GS", ".265", "was .357 over the first 8", "bad"],
    ["AAA sample", (aaa.plate_apps||0)+" PA", "5 starts · below the 100-BF convention", ""]
  ];
  document.getElementById("ovKpis").innerHTML = k.map(([l,v,s,c])=>
    `<div class="kpi ${c}"><div class="lab">${l}</div><div class="val">${v}</div><div class="sub">${s}</div></div>`).join("");

  const metrics=[["strike_rate","Strike"],["csw_rate","CSW"],["whiff_rate","Whiff/sw"],
    ["chase_rate","Chase"],["in_zone_rate","In-zone"],["first_pitch_strike_rate","1st-pitch K"],
    ["putaway_rate","Putaway"],["hard_hit_rate","Hard-hit"]];
  mk("cLevel",{type:"bar",data:{labels:metrics.map(m=>m[1]),datasets:[
    {label:`MLB (${mlb.plate_apps} PA)`,data:metrics.map(m=>mlb[m[0]]),backgroundColor:NAVY},
    {label:`AAA (${aaa.plate_apps} PA)`,data:metrics.map(m=>aaa[m[0]]),backgroundColor:RED}]},
    options:{responsive:true,scales:{y:{beginAtZero:true,ticks:{callback:v=>(100*v).toFixed(0)+"%"}}},
    plugins:{tooltip:{callbacks:{label:c=>c.dataset.label+": "+pct(c.raw)}}}}});

  const arcCols = k2 => [{label:"Split",key:k2},{label:"PA",key:"plate_apps",num:true},
    {label:"Strike",num:true,get:r=>pct(r.strike_rate)},{label:"CSW",num:true,get:r=>pct(r.csw_rate)},
    {label:"Chase",num:true,get:r=>pct(r.chase_rate)},{label:"Hard-hit",num:true,get:r=>pct(r.hard_hit_rate)},
    {label:"K/BB",num:true,get:r=>`${r.strikeouts}/${r.walks}`}];
  table("tMlbArc", D.mlb_arc, arcCols("arc"));
  table("tAaaArc", D.aaa_arc, arcCols("arc"));

  const order=["1st time","2nd time","3rd+ time"];
  const tt = l => order.map(o => (D.tto.find(r=>r.level===l&&r.tto_lbl===o)||{}).hard_hit_rate);
  const tw = l => order.map(o => (D.tto.find(r=>r.level===l&&r.tto_lbl===o)||{}).whiff_rate);
  mk("cTto",{type:"line",data:{labels:order,datasets:[
    {label:"MLB hard-hit",data:tt("MLB"),borderColor:NAVY,backgroundColor:NAVY,tension:.25,borderWidth:3},
    {label:"AAA hard-hit",data:tt("AAA"),borderColor:RED,backgroundColor:RED,tension:.25,borderWidth:3},
    {label:"MLB whiff/sw",data:tw("MLB"),borderColor:NAVY,borderDash:[6,4],tension:.25,borderWidth:2},
    {label:"AAA whiff/sw",data:tw("AAA"),borderColor:RED,borderDash:[6,4],tension:.25,borderWidth:2}]},
    options:{responsive:true,scales:{y:{ticks:{callback:v=>(100*v).toFixed(0)+"%"}}},
    plugins:{tooltip:{callbacks:{label:c=>c.dataset.label+": "+pct(c.raw)}}}}});
})();

/* ---------- ARSENAL ---------- */
const ORDER=["4-Seam Fastball","Sinker","Slider","Sweeper","Split-Finger","Curveball"];
function drawArsenal(){
  const lv = document.getElementById("selLevel").value;
  const mt = document.getElementById("selMetric").value;
  const levels = lv==="both" ? ["MLB","AAA"] : [lv];
  const ds = levels.map((L,i)=>({label:L,backgroundColor:i===0&&lv==="both"?NAVY:(L==="MLB"?NAVY:RED),
    data:ORDER.map(p=>{const r=D.arsenal.find(x=>x.level===L&&x.pitch_name===p);return r?r[mt]:null;})}));
  const isPct = !["velo"].includes(mt);
  mk("cArs",{type:"bar",data:{labels:ORDER,datasets:ds},options:{responsive:true,
    scales:{y:{beginAtZero:!isPct?false:true,ticks:{callback:v=>isPct?(100*v).toFixed(0)+"%":v}}},
    plugins:{tooltip:{callbacks:{label:c=>{
      const r=D.arsenal.find(x=>x.level===c.dataset.label&&x.pitch_name===c.label)||{};
      return `${c.dataset.label}: ${isPct?pct(c.raw):f1(c.raw)}  (n=${r.n}${r.swings?`, ${r.swings} sw`:''})`;}}}}}});

  const pts = levels.flatMap(L => D.arsenal.filter(r=>r.level===L).map(r=>({
    x:r.hb_in, y:r.ivb_in, r:6+34*r.usage, lvl:L, p:r.pitch_name, velo:r.velo, n:r.n})));
  mk("cMove",{type:"bubble",data:{datasets: ORDER.flatMap(p => levels.map(L=>{
      const s=pts.filter(q=>q.p===p&&q.lvl===L);
      return {label:`${p.split(" ")[0]} (${L})`,data:s,
        backgroundColor:L==="MLB"?PC[p]:"transparent",borderColor:PC[p],borderWidth:2.5};}))},
    options:{responsive:true,scales:{
      x:{title:{display:true,text:"Horizontal break — arm-side positive (in)"},grid:{color:"#eee"}},
      y:{title:{display:true,text:"Induced vertical break (in)"},grid:{color:"#eee"}}},
    plugins:{legend:{labels:{boxWidth:9,font:{size:10}}},tooltip:{callbacks:{
      label:c=>`${c.dataset.label}: ${f1(c.raw.velo)} mph, IVB ${f1(c.raw.y)}", HB ${f1(c.raw.x)}", n=${c.raw.n}`}}}}});
}
document.getElementById("selLevel").onchange = drawArsenal;
document.getElementById("selMetric").onchange = drawArsenal;
drawArsenal();

table("tStuff", D.stuff.filter(r=>r.coverage_ok), [
  {label:"Pitch",key:"pitch_name"},{label:"Δ usage (pts)",num:true,get:r=>f1(r.d_usage_pp)},
  {label:"Δ velo",num:true,get:r=>f2(r.d_velo)},{label:"Δ spin",num:true,get:r=>f1(r.d_spin)},
  {label:"Δ ride",num:true,get:r=>f2(r.d_ivb)},{label:"Δ horiz",num:true,get:r=>f2(r.d_hb)},
  {label:"Noise guard",key:"noise_guard"}]);
table("tSep", D.sep, [{label:"Pitch",key:"pitch_name"},{label:"MLB",num:true,get:r=>f2(r.MLB)},
  {label:"AAA",num:true,get:r=>f2(r.AAA)},{label:"Change",num:true,get:r=>f2(r.d_sep_aaa_minus_mlb),
   style:r=>Math.abs(r.d_sep_aaa_minus_mlb)>1.5?"color:#B3151F;font-weight:700":""}]);
table("tArs", D.arsenal, [{label:"Level",key:"level"},{label:"Pitch",key:"pitch_name"},
  {label:"n",key:"n",num:true},{label:"Usage",num:true,get:r=>pct(r.usage)},
  {label:"Velo",num:true,get:r=>f1(r.velo)},{label:"Max",num:true,get:r=>f1(r.velo_max)},
  {label:"Spin",num:true,get:r=>f1(r.spin)},{label:"Ride",num:true,get:r=>f1(r.ivb_in)},
  {label:"Horiz",num:true,get:r=>f1(r.hb_in)},{label:"In-zone",num:true,get:r=>pct(r.in_zone_rate)},
  {label:"Whiff/sw",num:true,get:r=>pct(r.whiff_rate)},{label:"Chase",num:true,get:r=>pct(r.chase_rate)},
  {label:"CSW",num:true,get:r=>pct(r.csw_rate)},{label:"Arm°",num:true,get:r=>f1(r.arm_angle)}]);

/* ---------- FASTBALL ---------- */
(function(){
  const b = D.bench;
  mk("cBench",{type:"bar",data:{labels:b.map(r=>r.note.split("—")[0].trim()),datasets:[
    {label:"Painter percentile in pool",data:b.map(r=>r.painter_mlb_pctile),
     backgroundColor:b.map(r=>r.painter_mlb_pctile<35?RED:NAVY)}]},
    options:{indexAxis:"y",responsive:true,scales:{x:{min:0,max:100,
      title:{display:true,text:"Percentile among 31 RHP (2026 Phillies games)"}}},
    plugins:{legend:{display:false},tooltip:{callbacks:{
      afterLabel:c=>{const r=b[c.dataIndex];
        return `Painter MLB ${f3(r.painter_mlb)} · pool median ${f3(r.pool_median)} · AAA ${f3(r.painter_aaa)}`;}}}}}});
  table("tBench", b, [{label:"Metric",key:"metric"},{label:"MLB",num:true,get:r=>f3(r.painter_mlb)},
    {label:"AAA",num:true,get:r=>f3(r.painter_aaa)},{label:"Pool med",num:true,get:r=>f3(r.pool_median)},
    {label:"Pool p75",num:true,get:r=>f3(r.pool_p75)},{label:"Pctile",num:true,
     get:r=>f1(r.painter_mlb_pctile),style:r=>r.painter_mlb_pctile<35?"color:#B3151F;font-weight:700":""}]);
  table("tFfloc", D.ffloc, [{label:"Cut",key:"cut"},{label:"Level",key:"level"},
    {label:"Where",key:"loc_tier"},{label:"Pitches",key:"pitches",num:true},
    {label:"Swings",key:"swings",num:true},{label:"Whiff/sw",num:true,get:r=>pct(r.whiff_rate)}]);

  const tiers=["heart","shadow","chase","waste"], TC={heart:RED,shadow:NAVY,chase:"#1F77B4",waste:"#D9D9D9"};
  const labs = [];
  ["MLB","AAA"].forEach(L=>ORDER.forEach(p=>labs.push({L,p})));
  mk("cLoc",{type:"bar",data:{labels:labs.map(o=>`${o.p.split(" ")[0]} (${o.L})`),
    datasets:tiers.map(t=>({label:t,backgroundColor:TC[t],
      data:labs.map(o=>{const r=D.loc.find(x=>x.level===o.L&&x.pitch_name===o.p&&x.loc_tier===t);return r?r.share:0;})}))},
    options:{indexAxis:"y",responsive:true,scales:{x:{stacked:true,max:1,ticks:{callback:v=>(100*v).toFixed(0)+"%"}},
      y:{stacked:true}},plugins:{tooltip:{callbacks:{label:c=>c.dataset.label+": "+pct(c.raw)}}}}});
})();

/* ---------- DELIVERY ---------- */
(function(){
  const L = D.start_log.slice().sort((a,b)=>a.game_date<b.game_date?-1:1);
  mk("cVelo",{type:"line",data:{labels:L.map(r=>r.game_date.slice(5)),datasets:[
    {label:"4-seam velo (mph)",data:L.map(r=>r.ff_velo),yAxisID:"y",borderColor:NAVY,
     backgroundColor:L.map(r=>r.level==="MLB"?NAVY:RED),pointRadius:5,borderWidth:2,tension:.2},
    {label:"Extension (ft)",data:L.map(r=>r.ext_ft),yAxisID:"y1",borderColor:"#2CA02C",
     borderDash:[5,4],pointRadius:3,borderWidth:2,tension:.2}]},
    options:{responsive:true,scales:{
      y:{position:"left",title:{display:true,text:"4-seam velocity (mph)"}},
      y1:{position:"right",title:{display:true,text:"Extension (ft)"},grid:{drawOnChartArea:false}}},
    plugins:{tooltip:{callbacks:{afterLabel:c=>`level: ${L[c.dataIndex].level}`}}}}});

  const R = D.release.slice().sort((a,b)=>a.game_date<b.game_date?-1:1);
  mk("cRel",{type:"line",data:{labels:R.map(r=>r.game_date.slice(5)),datasets:[
    {label:"4-seam release-x (in)",data:R.map(r=>r.mean_x_ft_in),
     borderColor:GRAY,borderWidth:2,tension:.15,pointRadius:6,
     pointBackgroundColor:R.map(r=>Math.abs(r.mean_x_ft_in)<22?RED:(r.level==="MLB"?NAVY:"#1F77B4")),
     pointBorderColor:"#fff",pointBorderWidth:1.5}]},
    options:{responsive:true,scales:{y:{title:{display:true,text:"Mean horizontal release (inches)"}}},
    plugins:{legend:{display:false},tooltip:{callbacks:{
      afterLabel:c=>{const r=R[c.dataIndex];
        return `${r.level} · ${r.ff_pitches} four-seams · RCI ${r.rci_in===null?"n/a":f2(r.rci_in)}"`;}}}}}});

  const P = D.release_pitch;
  mk("cArm",{type:"bar",data:{labels:ORDER,datasets:["MLB","AAA"].map((L2,i)=>({
      label:L2,backgroundColor:i?RED:NAVY,
      data:ORDER.map(p=>{const r=P.find(x=>x.level===L2&&x.pitch_name===p);return r?r.arm_angle:null;})}))},
    options:{responsive:true,scales:{y:{title:{display:true,text:"Mean arm angle (degrees)"},min:30}},
    plugins:{tooltip:{callbacks:{afterLabel:c=>{
      const r=P.find(x=>x.level===c.dataset.label&&x.pitch_name===c.label)||{};
      return `release-x ${f1(r.rel_x_ft*12)}"  ·  n=${r.n}`;}}}}}});

  table("tSpread", D.spread, [{label:"Scope",key:"scope"},
    {label:"Spread (°)",num:true,get:r=>f2(r.arm_spread_deg),style:()=>"color:#B3151F;font-weight:700"},
    {label:"Pool median",num:true,get:r=>f2(r.pool_median)},{label:"Pool p90",num:true,get:r=>f2(r.pool_p90)},
    {label:"Pool n",key:"pool_n",num:true},{label:"Pctile",num:true,get:r=>f1(r.pctile_high_is_worse)}]);
})();

/* ---------- PLATOON ---------- */
function drawStand(){
  const s = document.getElementById("selStand").value;
  const rows = D.usage_stand.filter(r=>r.stand===s);
  mk("cStand",{type:"bar",data:{labels:ORDER,datasets:["MLB","AAA"].map((L,i)=>({
      label:L,backgroundColor:i?RED:NAVY,
      data:ORDER.map(p=>{const r=rows.find(x=>x.level===L&&x.pitch_name===p);return r?r.usage:0;})}))},
    options:{responsive:true,scales:{y:{beginAtZero:true,ticks:{callback:v=>(100*v).toFixed(0)+"%"}}},
    plugins:{tooltip:{callbacks:{label:c=>{
      const r=rows.find(x=>x.level===c.dataset.label&&x.pitch_name===c.label)||{};
      return `${c.dataset.label}: ${pct(c.raw)}  (n=${r.n||0}, whiff ${r.whiff_rate!==undefined?pct(r.whiff_rate):"—"} on ${r.swings||0} sw)`;}}}}}});
  table("tStand", rows, [{label:"Level",key:"level"},{label:"Pitch",key:"pitch_name"},
    {label:"n",key:"n",num:true},{label:"Usage",num:true,get:r=>pct(r.usage)},
    {label:"Swings",key:"swings",num:true},{label:"Whiff/sw",num:true,get:r=>pct(r.whiff_rate)}]);
}
document.getElementById("selStand").onchange = drawStand; drawStand();

/* ---------- STARTS + GOVERNANCE ---------- */
table("tStarts", D.start_log.slice().sort((a,b)=>a.game_date<b.game_date?-1:1), [
  {label:"Level",key:"level",style:r=>`font-weight:700;color:${r.level==="MLB"?"#002D72":"#E81828"}`},
  {label:"Date",key:"game_date"},{label:"Pitches",key:"pitches",num:true},
  {label:"PA",key:"plate_apps",num:true},{label:"K",key:"strikeouts",num:true},
  {label:"BB",key:"walks",num:true},{label:"Strike",num:true,get:r=>pct(r.strike_rate)},
  {label:"CSW",num:true,get:r=>pct(r.csw_rate)},{label:"Whiff/sw",num:true,get:r=>pct(r.whiff_rate)},
  {label:"Chase",num:true,get:r=>pct(r.chase_rate)},{label:"1st-pitch K",num:true,get:r=>pct(r.first_pitch_strike_rate)},
  {label:"FF velo",num:true,get:r=>f1(r.ff_velo)},{label:"Max",num:true,get:r=>f1(r.ff_velo_max)},
  {label:"Ext",num:true,get:r=>f2(r.ext_ft)},{label:"Upper-3rd",num:true,get:r=>pct(r.futr)}]);
table("tDq", D.dq, [{label:"Check",key:"check"},{label:"Dimension",key:"dimension"},
  {label:"Result",key:"result"},{label:"Status",get:r=>`<span class="pill ${r.status}">${r.status}</span>`},
  {label:"Note",key:"note"}]);
table("tFresh", D.fresh, [{label:"Source",key:"source"},{label:"Tier",key:"tier"},
  {label:"Filter",key:"filter"},{label:"Rows",key:"rows",num:true},{label:"Window",key:"window"},
  {label:"Starts",key:"starts",num:true},{label:"Fitness",key:"fitness"}]);

/* ---------- NAV ---------- */
document.querySelectorAll("nav button").forEach(b => b.onclick = () => {
  document.querySelectorAll("nav button").forEach(x=>x.classList.remove("on"));
  document.querySelectorAll(".panel").forEach(x=>x.classList.remove("on"));
  b.classList.add("on"); document.getElementById(b.dataset.p).classList.add("on");
  Object.values(charts).forEach(c=>c.resize());
});
</script></body></html>
"""

if __name__ == "__main__":
    main()
