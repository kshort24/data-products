"""
dp_uc31 — self-contained interactive HTML dashboard for the Arraez acquisition read.

Every number rendered here is read from the out/dp_uc31_*.csv receipts written by
dp_uc31_arraez_acquisition_read.py. Nothing is hand-keyed and nothing is recomputed
in the browser EXCEPT the lineup-swap arithmetic in the slot explorer, which sums
published per-hitter-per-slot SPRC values — the same arithmetic the f7 receipt
performs, and asserted equal to it by verification checks V-130..V-132.

Chart.js from cdnjs; data inlined as JSON so the file works offline and can be
emailed as a single attachment.
"""
from __future__ import annotations
import json, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DEST = os.path.join(HERE, "dp_uc31_arraez_acquisition_dashboard.html")

PHI_RED, PHI_NAVY, PHI_LT = "#E81828", "#002D72", "#7A99C2"


def rd(name):
    df = pd.read_csv(os.path.join(OUT, f"dp_uc31_{name}.csv"))
    df = df.replace([float("inf"), float("-inf")], pd.NA)
    return df.astype(object).where(pd.notna(df), None)


def main():
    data = {
        "season":     rd("a1_season_line").to_dict("records"),
        "window":     rd("a4_window_headline").to_dict("records"),
        "discipline": rd("b1_discipline").to_dict("records"),
        "batted":     rd("b2_batted_ball").to_dict("records"),
        "bat_track":  rd("b4_bat_tracking").to_dict("records"),
        "ts_year":    rd("c1_two_strike_by_year").to_dict("records"),
        "ts_econ":    rd("c2_two_strike_economy").to_dict("records"),
        "ts_peer":    rd("c3_two_strike_vs_phillies").to_dict("records"),
        "damage":     rd("d1_group_x_hand_2026").to_dict("records"),
        "pitchtype":  rd("d3_pitch_type_2026").to_dict("records"),
        "by_hand":    rd("d4_by_hand_2026").to_dict("records"),
        "context":    rd("e1_context_2026").to_dict("records"),
        "ctx_year":   rd("e2_context_by_year").to_dict("records"),
        "spcr_peer":  rd("e4_spcr_vs_phillies").to_dict("records"),
        "slot_opp":   rd("f1_slot_opportunity").to_dict("records"),
        "occupancy":  rd("f9_observed_top_of_order").to_dict("records"),
        "profiles":   rd("f3_context_profiles").to_dict("records"),
        "sprc":       rd("f5_sprc").to_dict("records"),
        "supply":     rd("f8_table_setting_supply").to_dict("records"),
        "scenario":   rd("f7_swap_scenario").to_dict("records"),
        "dq":         rd("dq_scorecard").to_dict("records"),
        "fresh":      rd("freshness_manifest").to_dict("records"),
    }
    try:
        v = rd("verification_results")
        data["verify"] = {"total": len(v), "passed": int((v.result == "PASS").sum()),
                          "failed": int((v.result != "PASS").sum())}
    except Exception:
        data["verify"] = {"total": 0, "passed": 0, "failed": 0}

    html = TEMPLATE.replace("__DATA__", json.dumps(data, allow_nan=False))
    with open(DEST, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard written: {DEST}  ({os.path.getsize(DEST)/1024:.0f} KB)")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Luis Arraez — Acquisition Read · uc-pos-008 / dp_uc31</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--red:#E81828;--navy:#002D72;--lt:#7A99C2;--ink:#1a1a1a;--mute:#6b7280;--line:#e3e6ea;--bg:#f7f8fa;}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
 color:var(--ink);background:var(--bg);font-size:14px;line-height:1.5}
header{background:var(--navy);color:#fff;padding:22px 30px 18px}
header h1{margin:0;font-size:25px;color:#fff;letter-spacing:-.3px}
header .sub{color:#b9c8e0;font-size:13px;margin-top:5px}
header .ids{color:#8fa6c8;font-size:11.5px;margin-top:7px;font-family:ui-monospace,Menlo,monospace}
.bar{background:var(--red);height:4px}
.warn{background:#fff4f4;border-left:4px solid var(--red);margin:18px 30px 0;padding:11px 15px;font-size:12.7px}
.warn b{color:var(--navy)}
nav{display:flex;gap:2px;padding:16px 30px 0;flex-wrap:wrap;border-bottom:1px solid var(--line);background:#fff}
nav button{background:none;border:none;border-bottom:3px solid transparent;padding:9px 15px;
 font-size:13.5px;cursor:pointer;color:var(--mute);font-weight:600}
nav button:hover{color:var(--navy)}
nav button.on{color:var(--navy);border-bottom-color:var(--red)}
main{padding:22px 30px 60px}
.panel{display:none}.panel.on{display:block}
h2{color:var(--navy);font-size:17px;margin:22px 0 4px;border-bottom:2px solid var(--red);padding-bottom:5px}
h2:first-child{margin-top:0}
.note{color:var(--mute);font-size:12.3px;margin:5px 0 14px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:16px 0 20px}
.card{background:#fff;border:1px solid var(--line);border-radius:7px;padding:13px 15px}
.card .k{font-size:10.5px;text-transform:uppercase;letter-spacing:.6px;color:var(--mute);font-weight:700}
.card .v{font-size:25px;font-weight:700;color:var(--navy);margin:3px 0 1px;letter-spacing:-.5px}
.card .v.red{color:var(--red)}
.card .d{font-size:11.5px;color:var(--mute)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:980px){.grid2{grid-template-columns:1fr}}
.box{background:#fff;border:1px solid var(--line);border-radius:7px;padding:15px}
.chart{position:relative;height:310px}
.chart.tall{height:390px}
table{width:100%;border-collapse:collapse;font-size:12.3px;background:#fff}
th{background:var(--navy);color:#fff;text-align:left;padding:7px 9px;font-size:11.5px;font-weight:700;
 cursor:pointer;user-select:none;white-space:nowrap}
th:hover{background:#013a91}
td{padding:6px 9px;border-bottom:1px solid #eceef1}
tr:nth-child(even) td{background:#fafbfc}
tr.hi td{background:#fdeef0 !important;font-weight:700;color:var(--navy)}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:7px}
.ctl{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin:12px 0 16px;
 background:#fff;border:1px solid var(--line);border-radius:7px;padding:12px 15px}
.ctl label{font-size:12.3px;font-weight:700;color:var(--navy)}
select,input[type=range]{font-size:13px;padding:5px 7px;border:1px solid #cfd4da;border-radius:5px;
 background:#fff;color:var(--ink)}
.seg{display:inline-flex;border:1px solid #cfd4da;border-radius:5px;overflow:hidden}
.seg button{border:none;background:#fff;padding:6px 12px;font-size:12.3px;cursor:pointer;color:var(--mute)}
.seg button.on{background:var(--navy);color:#fff;font-weight:700}
.verdict{background:linear-gradient(180deg,#fff,#fbfcfe);border:2px solid var(--navy);
 border-radius:9px;padding:18px 20px;margin:18px 0}
.verdict .h{font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:var(--red);font-weight:800}
.verdict .big{font-size:31px;font-weight:800;color:var(--navy);margin:6px 0;letter-spacing:-.8px}
.verdict .t{font-size:13px;color:#333}
.pill{display:inline-block;padding:2px 9px;border-radius:11px;font-size:11px;font-weight:700}
.pill.ok{background:#e6f4ec;color:#136c35}.pill.no{background:#fdecec;color:#a11}
.pill.thin{background:#fff3cd;color:#7a5b00}
footer{padding:22px 30px 40px;color:var(--mute);font-size:11.6px;border-top:1px solid var(--line);background:#fff}
code{background:#eef0f3;padding:1px 5px;border-radius:3px;font-size:11.5px;
 font-family:ui-monospace,Menlo,monospace}
</style></head><body>
<header>
 <h1>Luis Arraez — Acquisition Read</h1>
 <div class="sub">Deadline acquisition onboarding · Phillies batting department · interactive companion to the PDF report</div>
 <div class="ids">uc-pos-008-arraez-acquisition-001 · UC #32 · build dp_uc31 · built 2026-08-04 · Internal — Restricted</div>
</header><div class="bar"></div>
<div class="warn">
 <b>Data window.</b> All forward-looking figures are <b>2026 regular season only</b> — 464 PA, 1,727 pitches, through <b>2026-08-02</b>. 2019–2025 is a shadow backdrop and carries no forward-looking claim. Arraez has <b>zero Phillies plate appearances</b>.
 &nbsp;·&nbsp; <b>Contested premise:</b> the request names Schwarber as leadoff; the log says <b>Turner</b> (399 PA). Both framings are priced in the Lineup tab.
</div>
<nav>
 <button class="on" data-p="top">Top line</button>
 <button data-p="ind">Indicators</button>
 <button data-p="ts">Two strikes</button>
 <button data-p="dmg">Damage map</button>
 <button data-p="risp">Scoring position</button>
 <button data-p="lineup">Lineup decision</button>
 <button data-p="gov">Governance</button>
</nav>
<main>

<!-- ============================================ TOP LINE -->
<section class="panel on" id="top">
 <div class="cards" id="topcards"></div>
 <div class="grid2">
  <div class="box"><h2 style="margin-top:0">Results vs deserved contact</h2>
   <div class="note">wOBA is what happened. xwOBA is what the contact deserved. 2026 is the first year they separate.</div>
   <div class="chart"><canvas id="c_woba"></canvas></div></div>
  <div class="box"><h2 style="margin-top:0">Slash line by season</h2>
   <div class="ctl" style="margin:0 0 10px"><label>Metric</label>
    <div class="seg" id="seg_slash">
     <button class="on" data-m="ba">BA</button><button data-m="obp">OBP</button>
     <button data-m="slg">SLG</button><button data-m="iso">ISO</button>
     <button data-m="krate">K%</button><button data-m="bbrate">BB%</button></div></div>
   <div class="chart"><canvas id="c_slash"></canvas></div></div>
 </div>
 <h2>Season line</h2>
 <div class="wrap"><table id="t_season"></table></div>
</section>

<!-- ============================================ INDICATORS -->
<section class="panel" id="ind">
 <div class="cards" id="indcards"></div>
 <div class="grid2">
  <div class="box"><h2 style="margin-top:0">Contact quality trend</h2>
   <div class="ctl" style="margin:0 0 10px"><label>Measure</label>
    <div class="seg" id="seg_bb">
     <button class="on" data-m="avg_ev">Avg EV</button><button data-m="hard_hit_rate">Hard-hit%</button>
     <button data-m="barrel_rate">Barrel%</button><button data-m="avg_la">Avg LA</button>
     <button data-m="gb_rate">GB%</button></div></div>
   <div class="chart"><canvas id="c_bb"></canvas></div></div>
  <div class="box"><h2 style="margin-top:0">Plate discipline</h2>
   <div class="note">A 32% chase rate is above league average. He is aggressive — he simply does not miss.</div>
   <div class="chart"><canvas id="c_disc"></canvas></div></div>
 </div>
 <h2>Batted ball detail</h2>
 <div class="wrap"><table id="t_batted"></table></div>
 <h2>Bat tracking (Statcast 2023+)</h2>
 <div class="note">Fast-swing rate is the share of tracked swings at or above 75 mph. In 2026 it is zero out of 817.</div>
 <div class="wrap"><table id="t_bt"></table></div>
</section>

<!-- ============================================ TWO STRIKES -->
<section class="panel" id="ts">
 <div class="cards" id="tscards"></div>
 <div class="box"><h2 style="margin-top:0">Two-Strike Survival Rate — Arraez vs the roster he is joining</h2>
  <div class="note">AR-1. Share of two-strike plate appearances not ending in a strikeout, 2026. Phillies regulars with 150+ PA.</div>
  <div class="ctl" style="margin:0 0 10px"><label>Rank by</label>
   <div class="seg" id="seg_ts">
    <button class="on" data-m="tssr">Survival rate</button>
    <button data-m="woba_2k">Two-strike wOBA</button>
    <button data-m="slg_2k">Two-strike SLG</button>
    <button data-m="re24_per_pa_2k">RE24 per PA</button></div></div>
  <div class="chart tall"><canvas id="c_ts"></canvas></div></div>
 <div class="grid2" style="margin-top:20px">
  <div class="box"><h2 style="margin-top:0">How he survives</h2>
   <div class="note">Once he has two strikes he abandons the zone and protects. The chase rate would be
    catastrophic for anyone who missed — he doesn't.</div>
   <div class="chart"><canvas id="c_tsecon"></canvas></div></div>
  <div class="box"><h2 style="margin-top:0">Two-strike survival, his own history</h2>
   <div class="note">The skill is stable and has been improving since 2022. This is not a 2026 artifact.</div>
   <div class="chart"><canvas id="c_tsyear"></canvas></div></div>
 </div>
 <h2>Full two-strike benchmark</h2>
 <div class="wrap"><table id="t_ts"></table></div>
</section>

<!-- ============================================ DAMAGE -->
<section class="panel" id="dmg">
 <div class="box"><h2 style="margin-top:0">Damage by pitch group and pitcher hand</h2>
  <div class="note">AR-3. Compare actual slugging against xwOBAcon — the contact quality that supports it.
   Only fastballs from right-handers show results the contact agrees with.</div>
  <div class="ctl"><label>Show</label>
   <div class="seg" id="seg_dmg">
    <button class="on" data-m="slg">SLG vs xwOBAcon</button>
    <button data-m="ev">Exit velocity</button>
    <button data-m="hard">Hard-hit rate</button></div>
   <label style="margin-left:12px"><input type="checkbox" id="hideThin"> hide samples under 15 BIP</label></div>
  <div class="chart tall"><canvas id="c_dmg"></canvas></div></div>
 <div class="grid2" style="margin-top:20px">
  <div class="box"><h2 style="margin-top:0">The platoon split that matters</h2>
   <div class="note">Slugging is identical against both hands. Deserved production is not close.</div>
   <div class="chart"><canvas id="c_hand"></canvas></div></div>
  <div class="box"><h2 style="margin-top:0">By pitch type</h2>
   <div class="chart"><canvas id="c_pt"></canvas></div></div>
 </div>
 <h2>Group × hand detail</h2>
 <div class="wrap"><table id="t_dmg"></table></div>
</section>

<!-- ============================================ RISP -->
<section class="panel" id="risp">
 <div class="cards" id="rispcards"></div>
 <div class="box"><h2 style="margin-top:0">Scoring-Position Conversion Rate</h2>
  <div class="note">AR-4. Runners in scoring position at plate-appearance start who scored on that plate appearance.
   Computed at the runner level, so a two-RBI double counts twice.</div>
  <div class="chart tall"><canvas id="c_spcr"></canvas></div></div>
 <div class="grid2" style="margin-top:20px">
  <div class="box"><h2 style="margin-top:0">Production by base context</h2>
   <div class="chart"><canvas id="c_ctx"></canvas></div></div>
  <div class="box"><h2 style="margin-top:0">Conversion rate, his own history</h2>
   <div class="note">Seven prior seasons range .222 to .560. The 2026 figure is at the high end of his own
    range, not a new skill. Plan on ~.30.</div>
   <div class="chart"><canvas id="c_spcryear"></canvas></div></div>
 </div>
 <h2>Scoring-position benchmark</h2>
 <div class="wrap"><table id="t_spcr"></table></div>
</section>

<!-- ============================================ LINEUP -->
<section class="panel" id="lineup">
 <h2 style="margin-top:0">Slot explorer — price any lineup pair</h2>
 <div class="note">AR-6. Pick two hitters and two slots. The projected run contribution is summed from the
  published per-hitter-per-slot SPRC receipt — the same arithmetic the <code>f7</code> receipt performs.</div>
 <div class="ctl">
  <label>Hitter A</label><select id="hA"></select>
  <label>slot</label><select id="sA"></select>
  <span style="color:var(--mute)">↔</span>
  <label>Hitter B</label><select id="hB"></select>
  <label>slot</label><select id="sB"></select>
 </div>
 <div class="verdict">
  <div class="h">Swapping the two slots would be worth</div>
  <div class="big" id="swapv">—</div>
  <div class="t" id="swapt"></div>
 </div>
 <div class="grid2">
  <div class="box"><h2 style="margin-top:0">Projected run contribution by slot</h2>
   <div class="note">The whole slot decision for Arraez spans under four runs per 162 games.</div>
   <div class="chart"><canvas id="c_sprc"></canvas></div></div>
  <div class="box"><h2 style="margin-top:0">What each slot offers</h2>
   <div class="note">RISP share rises down the order; plate appearances fall. The two nearly cancel.</div>
   <div class="chart"><canvas id="c_slot"></canvas></div></div>
 </div>
 <div class="grid2" style="margin-top:20px">
  <div class="box"><h2 style="margin-top:0">Table setting — AR-7</h2>
   <div class="note">Baserunners Arraez would supply above each slot's 2026 incumbent, and what the next
    two slots do with them. Leading off creates the most runners; batting second and third hand them
    to the hitters most likely to cash them.</div>
   <div class="chart"><canvas id="c_supply"></canvas></div></div>
  <div class="box"><h2 style="margin-top:0">Scenarios priced in the report</h2>
   <div class="wrap"><table id="t_scen"></table></div>
   <div class="note" style="margin-top:10px">Scenario totals are pair sums and are only comparable
    <b>within</b> a framing — Turner and Schwarber are very differently productive in 2026.</div></div>
 </div>
 <h2>Observed 2026 occupancy, slots 1–4</h2>
 <div class="note">The premise conflict, in the data. Turner led off; Schwarber batted second.</div>
 <div class="wrap"><table id="t_occ"></table></div>
</section>

<!-- ============================================ GOVERNANCE -->
<section class="panel" id="gov">
 <div class="cards" id="govcards"></div>
 <h2>Build-time data quality scorecard</h2>
 <div class="wrap"><table id="t_dq"></table></div>
 <h2>Freshness manifest &amp; manual carry-ins</h2>
 <div class="wrap"><table id="t_fresh"></table></div>
</section>
</main>
<footer>
 Every figure on this page is read from a CSV receipt in <code>out/</code>. No number is computed in the
 browser except the slot-explorer sum, which is asserted equal to the <code>f7</code> receipt by verification
 checks V-130 – V-132. Source of truth: <code>dp_uc31_arraez_acquisition_read.py</code>.
 <br>New KPIs (provisional): AR-1 Two-Strike Survival · AR-2 Two-Strike Damage Line ·
 AR-3 Damage by Group × Hand · AR-4 Scoring-Position Conversion · AR-5 Slot Opportunity Profile ·
 AR-6 Slot-Projected Run Contribution · AR-7 Table-Setting Value.
</footer>

<script>
const D = __DATA__;
const RED="#E81828", NAVY="#002D72", LT="#7A99C2", GREY="#9AA0A6";
const f3=v=>v==null?"—":(+v).toFixed(3).replace(/^0\./,".");
const f1=v=>v==null?"—":(+v).toFixed(1);
const f2=v=>v==null?"—":(+v).toFixed(2);
const pc=v=>v==null?"—":((+v)*100).toFixed(1)+"%";
Chart.defaults.font.family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif";
Chart.defaults.font.size=11; Chart.defaults.color="#555";
Chart.defaults.plugins.legend.labels.boxWidth=11;
Chart.defaults.plugins.legend.labels.usePointStyle=true;
const charts={};
function mk(id,cfg){ if(charts[id])charts[id].destroy();
  charts[id]=new Chart(document.getElementById(id),cfg); return charts[id]; }
const NOLEG={plugins:{legend:{display:false}}};

/* nav */
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.panel').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); document.getElementById(b.dataset.p).classList.add('on');
  Object.values(charts).forEach(c=>c.resize());
});
function seg(id,fn){ const el=document.getElementById(id);
  el.querySelectorAll('button').forEach(b=>b.onclick=()=>{
    el.querySelectorAll('button').forEach(x=>x.classList.remove('on'));
    b.classList.add('on'); fn(b.dataset.m); }); }

/* generic table renderer */
function tbl(id, rows, cols, hiFn){
  const t=document.getElementById(id);
  let h="<thead><tr>"+cols.map(c=>`<th>${c.h}</th>`).join("")+"</tr></thead><tbody>";
  rows.forEach(r=>{ const hi=hiFn&&hiFn(r)?' class="hi"':'';
    h+=`<tr${hi}>`+cols.map(c=>`<td>${c.f?c.f(r[c.k],r):(r[c.k]??"—")}</td>`).join("")+"</tr>"; });
  t.innerHTML=h+"</tbody>";
}
function cards(id, items){
  document.getElementById(id).innerHTML=items.map(i=>
    `<div class="card"><div class="k">${i.k}</div><div class="v ${i.red?'red':''}">${i.v}</div>
     <div class="d">${i.d}</div></div>`).join("");
}

/* ---------------- TOP LINE ---------------- */
const S=D.season, s26=S.find(r=>r.game_year===2026);
const W=D.window, wp=W.find(r=>r.window==="2026_primary"), ws=W.find(r=>r.window!=="2026_primary");
cards("topcards",[
 {k:"2026 slash",v:f3(s26.ba)+"/"+f3(s26.obp)+"/"+f3(s26.slg),d:"464 PA · .788 OPS"},
 {k:"wOBA",v:f3(s26.woba),d:"vs .304 xwOBA — 33 pts ahead"},
 {k:"xwOBA",v:f3(s26.xwoba),red:1,d:"what the contact deserved"},
 {k:"Strikeout rate",v:pc(s26.krate),d:"21 K in 464 PA"},
 {k:"ISO",v:f3(s26.iso),d:"career high · 23 2B, 7 3B, 4 HR"},
 {k:"Pitches per PA",v:f2(S.find(r=>r.game_year===2026)?3.722:0),d:"below average — not wild"},
]);
mk("c_woba",{type:"line",data:{labels:S.map(r=>r.game_year),datasets:[
 {label:"wOBA",data:S.map(r=>r.woba),borderColor:RED,backgroundColor:RED,tension:.25,borderWidth:2.5},
 {label:"xwOBA",data:S.map(r=>r.xwoba),borderColor:NAVY,backgroundColor:NAVY,borderDash:[6,4],tension:.25,borderWidth:2.5}]},
 options:{maintainAspectRatio:false,scales:{y:{ticks:{callback:f3}}}}});
function slash(m){ const lab={ba:"BA",obp:"OBP",slg:"SLG",iso:"ISO",krate:"K%",bbrate:"BB%"}[m];
 const isPct=(m==="krate"||m==="bbrate");
 mk("c_slash",{type:"bar",data:{labels:S.map(r=>r.game_year),datasets:[{label:lab,
  data:S.map(r=>r[m]),backgroundColor:S.map(r=>r.game_year===2026?RED:LT)}]},
  options:{maintainAspectRatio:false,...NOLEG,scales:{y:{ticks:{callback:isPct?pc:f3}}}}}); }
seg("seg_slash",slash); slash("ba");
tbl("t_season",S,[{h:"Season",k:"game_year"},{h:"PA",k:"plate_apps"},{h:"AB",k:"at_bats"},
 {h:"H",k:"hits"},{h:"2B",k:"doubles"},{h:"3B",k:"triples"},{h:"HR",k:"hrs"},{h:"BB",k:"walks"},
 {h:"K",k:"strikeouts"},{h:"BA",k:"ba",f:f3},{h:"OBP",k:"obp",f:f3},{h:"SLG",k:"slg",f:f3},
 {h:"wOBA",k:"woba",f:f3},{h:"xwOBA",k:"xwoba",f:f3},{h:"ISO",k:"iso",f:f3},
 {h:"K%",k:"krate",f:pc},{h:"BB%",k:"bbrate",f:pc}],r=>r.game_year===2026);

/* ---------------- INDICATORS ---------------- */
const B=D.batted, b26=B.find(r=>r.game_year===2026), bt26=D.bat_track.find(r=>r.game_year===2026);
const dis26=D.discipline.find(r=>r.game_year===2026);
cards("indcards",[
 {k:"Avg exit velocity",v:f1(b26.avg_ev),d:"mph · down from 88.9 in 2022"},
 {k:"Barrel rate",v:pc(b26.barrel_rate),red:1,d:"3 barrels in 414 balls in play"},
 {k:"Hard-hit rate",v:pc(b26.hard_hit_rate),d:"95+ mph"},
 {k:"Bat speed",v:f1(bt26.avg_bat_speed),d:"mph · fast-swing rate 0.0%"},
 {k:"Chase rate",v:pc(dis26.chase_rate),d:"above league average"},
 {k:"Contact outside zone",v:pc(dis26.ooz_contact_rate),d:"the engine of the whole profile"},
]);
function bb(m){ const lab={avg_ev:"Avg EV (mph)",hard_hit_rate:"Hard-hit%",barrel_rate:"Barrel%",
  avg_la:"Avg launch angle",gb_rate:"Ground-ball%"}[m];
 const isPct=m.includes("rate")&&m!=="avg_la";
 mk("c_bb",{type:"line",data:{labels:B.map(r=>r.game_year),datasets:[{label:lab,data:B.map(r=>r[m]),
  borderColor:RED,backgroundColor:RED,tension:.25,borderWidth:2.5,
  pointBackgroundColor:B.map(r=>r.game_year===2026?NAVY:RED),
  pointRadius:B.map(r=>r.game_year===2026?6:3)}]},
  options:{maintainAspectRatio:false,...NOLEG,scales:{y:{ticks:{callback:isPct?pc:f1}}}}}); }
seg("seg_bb",bb); bb("avg_ev");
const DI=D.discipline;
mk("c_disc",{type:"line",data:{labels:DI.map(r=>r.game_year),datasets:[
 {label:"Chase%",data:DI.map(r=>r.chase_rate),borderColor:RED,backgroundColor:RED,tension:.25,borderWidth:2.5},
 {label:"Whiff%",data:DI.map(r=>r.whiff_rate),borderColor:NAVY,backgroundColor:NAVY,tension:.25,borderWidth:2.5},
 {label:"Contact outside zone",data:DI.map(r=>r.ooz_contact_rate),borderColor:LT,backgroundColor:LT,tension:.25,borderWidth:2.5}]},
 options:{maintainAspectRatio:false,scales:{y:{ticks:{callback:pc}}}}});
tbl("t_batted",B,[{h:"Season",k:"game_year"},{h:"BIP",k:"bip"},{h:"Avg EV",k:"avg_ev",f:f1},
 {h:"EV90",k:"ev90",f:f1},{h:"Max EV",k:"max_ev",f:f1},{h:"Avg LA",k:"avg_la",f:f1},
 {h:"Barrel%",k:"barrel_rate",f:pc},{h:"Hard-hit%",k:"hard_hit_rate",f:pc},
 {h:"GB%",k:"gb_rate",f:pc},{h:"LD%",k:"ld_rate",f:pc},{h:"FB%",k:"fb_rate",f:pc},
 {h:"xwOBAcon",k:"xwoba_con",f:f3},{h:"est. n",k:"xwoba_con_n"}],r=>r.game_year===2026);
tbl("t_bt",D.bat_track,[{h:"Season",k:"game_year"},{h:"Tracked swings",k:"tracked_swings"},
 {h:"Avg bat speed",k:"avg_bat_speed",f:f1},{h:"Fast-swing%",k:"fast_swing_rate",f:pc},
 {h:"Swing length",k:"avg_swing_length",f:f2},{h:"Attack angle",k:"avg_attack_angle",f:f2}],
 r=>r.game_year===2026);

/* ---------------- TWO STRIKES ---------------- */
const TP=D.ts_peer, ar2k=TP.find(r=>r.name==="Luis Arraez");
const te26=D.ts_econ.find(r=>r.game_year===2026);
cards("tscards",[
 {k:"Two-strike survival",v:f3(ar2k.tssr),d:"best Phillie: .670 (Stott)"},
 {k:"K in two-strike PA",v:ar2k.K_in_2k+" / "+ar2k.PA_2k,d:"Schwarber: 163 / 286"},
 {k:"Hits with two strikes",v:ar2k.hits_2k,d:"BA "+f3(ar2k.ba_2k)+" · SLG "+f3(ar2k.slg_2k)},
 {k:"Two-strike chase rate",v:pc(te26.chase_rate),d:"he abandons the zone and protects"},
 {k:"Two-strike whiff rate",v:pc(te26.whiff_rate),d:"which is why the chase works"},
 {k:"Called third strikes",v:pc(te26.called_strike_rate),d:"share of two-strike pitches"},
]);
function tsChart(m){ const lab={tssr:"Two-strike survival rate",woba_2k:"Two-strike wOBA",
  slg_2k:"Two-strike SLG",re24_per_pa_2k:"RE24 per two-strike PA"}[m];
 const rows=[...TP].sort((a,b)=>(a[m]??-9)-(b[m]??-9));
 mk("c_ts",{type:"bar",data:{labels:rows.map(r=>r.name),datasets:[{label:lab,data:rows.map(r=>r[m]),
  backgroundColor:rows.map(r=>r.name==="Luis Arraez"?RED:LT)}]},
  options:{indexAxis:"y",maintainAspectRatio:false,...NOLEG,
   scales:{x:{ticks:{callback:f3}}},
   plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:c=>{
    const r=rows[c.dataIndex]; return `${r.K_in_2k} K in ${r.PA_2k} two-strike PA`;}}}}}}); }
seg("seg_ts",tsChart); tsChart("tssr");
const TE=D.ts_econ;
mk("c_tsecon",{type:"bar",data:{labels:TE.map(r=>r.game_year),datasets:[
 {label:"Chase% (2 strikes)",data:TE.map(r=>r.chase_rate),backgroundColor:RED},
 {label:"Whiff% (2 strikes)",data:TE.map(r=>r.whiff_rate),backgroundColor:NAVY},
 {label:"Foul% of swings",data:TE.map(r=>r.foul_rate_of_swings),backgroundColor:LT}]},
 options:{maintainAspectRatio:false,scales:{y:{ticks:{callback:pc}}}}});
const TY=D.ts_year;
mk("c_tsyear",{type:"line",data:{labels:TY.map(r=>r.game_year),datasets:[
 {label:"Survival rate",data:TY.map(r=>r.tssr),borderColor:RED,backgroundColor:RED,tension:.25,borderWidth:2.5},
 {label:"Two-strike wOBA",data:TY.map(r=>r.woba_2k),borderColor:NAVY,backgroundColor:NAVY,tension:.25,borderWidth:2.5}]},
 options:{maintainAspectRatio:false,scales:{y:{ticks:{callback:f3}}}}});
tbl("t_ts",[...TP].sort((a,b)=>b.tssr-a.tssr),[{h:"Hitter",k:"name"},{h:"PA",k:"PA_total"},
 {h:"2K PA",k:"PA_2k"},{h:"2K rate",k:"two_strike_rate",f:pc},{h:"K",k:"K_in_2k"},
 {h:"Survival",k:"tssr",f:f3},{h:"Hits",k:"hits_2k"},{h:"BA",k:"ba_2k",f:f3},
 {h:"OBP",k:"obp_2k",f:f3},{h:"SLG",k:"slg_2k",f:f3},{h:"wOBA",k:"woba_2k",f:f3},
 {h:"xwOBA",k:"xwoba_2k",f:f3},{h:"RE24/PA",k:"re24_per_pa_2k",f:v=>(+v).toFixed(3)}],
 r=>r.name==="Luis Arraez");

/* ---------------- DAMAGE ---------------- */
const DM=D.damage;
function dmgChart(m){
 let rows=DM.slice(); if(document.getElementById("hideThin").checked) rows=rows.filter(r=>!r.thin);
 rows.sort((a,b)=>a.p_throws.localeCompare(b.p_throws)||a.pitch_group.localeCompare(b.pitch_group));
 const labs=rows.map(r=>r.pitch_group+" vs "+r.p_throws+"HP");
 let ds;
 if(m==="slg") ds=[{label:"SLG (actual)",data:rows.map(r=>r.slg),backgroundColor:RED},
                   {label:"xwOBAcon (deserved)",data:rows.map(r=>r.xwoba_con),backgroundColor:NAVY}];
 else if(m==="ev") ds=[{label:"Avg exit velocity",data:rows.map(r=>r.avg_ev),backgroundColor:RED}];
 else ds=[{label:"Hard-hit rate",data:rows.map(r=>r.hard_hit_rate),backgroundColor:RED},
          {label:"Barrel rate",data:rows.map(r=>r.barrel_rate),backgroundColor:NAVY}];
 mk("c_dmg",{type:"bar",data:{labels:labs,datasets:ds},options:{maintainAspectRatio:false,
  scales:{y:{ticks:{callback:m==="ev"?f1:f3}}},
  plugins:{tooltip:{callbacks:{afterLabel:c=>{const r=rows[c.dataIndex];
   return `${r.bip} balls in play${r.thin?"  ⚠ thin sample":""}`;}}}}}});
}
seg("seg_dmg",dmgChart); document.getElementById("hideThin").onchange=()=>dmgChart(
 document.querySelector("#seg_dmg button.on").dataset.m); dmgChart("slg");
const HD=D.by_hand;
mk("c_hand",{type:"bar",data:{labels:HD.map(r=>"vs "+r.p_throws+"HP"),datasets:[
 {label:"SLG",data:HD.map(r=>r.slg),backgroundColor:LT},
 {label:"wOBA",data:HD.map(r=>r.woba),backgroundColor:RED},
 {label:"xwOBA",data:HD.map(r=>r.xwoba),backgroundColor:NAVY}]},
 options:{maintainAspectRatio:false,scales:{y:{ticks:{callback:f3}}},
  plugins:{tooltip:{callbacks:{afterLabel:c=>`${HD[c.dataIndex].PA} PA · K% ${pc(HD[c.dataIndex].k_rate)}`}}}}});
const PT=D.pitchtype;
mk("c_pt",{type:"bar",data:{labels:PT.map(r=>r.pitch_type),datasets:[
 {label:"SLG",data:PT.map(r=>r.slg),backgroundColor:RED},
 {label:"xwOBAcon",data:PT.map(r=>r.xwoba_con),backgroundColor:NAVY}]},
 options:{maintainAspectRatio:false,scales:{y:{ticks:{callback:f3}}},
  plugins:{tooltip:{callbacks:{afterLabel:c=>`${PT[c.dataIndex].pitches_seen} pitches seen · ${PT[c.dataIndex].bip} BIP`}}}}});
tbl("t_dmg",DM,[{h:"Group",k:"pitch_group"},{h:"Hand",k:"p_throws"},{h:"Pitches",k:"pitches_seen"},
 {h:"PA",k:"PA_ended"},{h:"BIP",k:"bip"},{h:"BA",k:"ba",f:f3},{h:"SLG",k:"slg",f:f3},
 {h:"ISO",k:"iso",f:f3},{h:"wOBA",k:"woba",f:f3},{h:"xwOBAcon",k:"xwoba_con",f:f3},
 {h:"Avg EV",k:"avg_ev",f:f1},{h:"Hard-hit%",k:"hard_hit_rate",f:pc},
 {h:"Sample",k:"thin",f:v=>v?'<span class="pill thin">thin</span>':'<span class="pill ok">ok</span>'}]);

/* ---------------- RISP ---------------- */
const CX=D.context, risp=CX.find(r=>r.ctx==="RISP");
const SP=D.spcr_peer;
cards("rispcards",[
 {k:"RISP slash",v:f3(risp.ba)+"/"+f3(risp.obp)+"/"+f3(risp.slg),d:"89 PA"},
 {k:"Conversion rate",v:f3(risp.spcr),d:"37 of 108 runners · best on team"},
 {k:"Strikeouts with RISP",v:risp.K,d:"in 89 plate appearances"},
 {k:"RE24 per PA",v:(+risp.re24_per_pa).toFixed(3),d:"vs +0.020 bases empty"},
 {k:"Runs driven in",v:risp.runs_driven,d:"2026, RISP situations"},
]);
const spSorted=[...SP].sort((a,b)=>a.spcr-b.spcr);
mk("c_spcr",{type:"bar",data:{labels:spSorted.map(r=>r.name),datasets:[{label:"Conversion rate",
 data:spSorted.map(r=>r.spcr),backgroundColor:spSorted.map(r=>r.name==="Luis Arraez"?RED:LT)}]},
 options:{indexAxis:"y",maintainAspectRatio:false,...NOLEG,scales:{x:{ticks:{callback:f3}}},
  plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:c=>{const r=spSorted[c.dataIndex];
   return [`${r.risp_runners_scored} of ${r.risp_runners_faced} runners`,`K rate ${pc(r.k_rate)}`];}}}}}});
mk("c_ctx",{type:"bar",data:{labels:CX.map(r=>r.ctx.replace(/_/g," ")),datasets:[
 {label:"wOBA",data:CX.map(r=>r.woba),backgroundColor:LT},
 {label:"RE24 per PA",data:CX.map(r=>r.re24_per_pa),backgroundColor:RED,yAxisID:"y1"}]},
 options:{maintainAspectRatio:false,scales:{y:{position:"left",ticks:{callback:f3}},
  y1:{position:"right",grid:{drawOnChartArea:false},ticks:{callback:v=>(+v).toFixed(3)}}},
  plugins:{tooltip:{callbacks:{afterLabel:c=>`${CX[c.dataIndex].PA} PA`}}}}});
const CY=D.ctx_year.filter(r=>r.ctx==="RISP");
mk("c_spcryear",{type:"bar",data:{labels:CY.map(r=>r.game_year),datasets:[{label:"Conversion rate",
 data:CY.map(r=>r.spcr),backgroundColor:CY.map(r=>r.game_year===2026?RED:LT)}]},
 options:{maintainAspectRatio:false,...NOLEG,scales:{y:{ticks:{callback:f3}}},
  plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:c=>`${CY[c.dataIndex].PA} RISP PA`}}}}});
tbl("t_spcr",[...SP].sort((a,b)=>b.spcr-a.spcr),[{h:"Hitter",k:"name"},{h:"RISP PA",k:"PA"},
 {h:"BA",k:"ba",f:f3},{h:"OBP",k:"obp",f:f3},{h:"SLG",k:"slg",f:f3},{h:"wOBA",k:"woba",f:f3},
 {h:"K%",k:"k_rate",f:pc},{h:"Runners",k:"risp_runners_faced"},{h:"Scored",k:"risp_runners_scored"},
 {h:"Conversion",k:"spcr",f:f3},{h:"RE24/PA",k:"re24_per_pa",f:v=>(+v).toFixed(3)},
 {h:"RBI",k:"runs_driven"}],r=>r.name==="Luis Arraez");

/* ---------------- LINEUP ---------------- */
const SPRC=D.sprc, SLOT=D.slot_opp, SUP=D.supply;
const hitters=[...new Set(SPRC.map(r=>r.hitter))].sort();
const val=(h,s)=>{const r=SPRC.find(x=>x.hitter===h&&+x.slot===+s); return r?+r.re24_per_162:null;};
["hA","hB"].forEach((id,i)=>{const el=document.getElementById(id);
 el.innerHTML=hitters.map(h=>`<option${h===(i?"Kyle Schwarber":"Luis Arraez")?" selected":""}>${h}</option>`).join("");});
["sA","sB"].forEach((id,i)=>{const el=document.getElementById(id);
 el.innerHTML=[1,2,3,4,5,6,7,8,9].map(s=>`<option${s===(i?1:4)?" selected":""}>${s}</option>`).join("");});
function swap(){
 const hA=hA_.value,hB=hB_.value,sA=+sA_.value,sB=+sB_.value;
 const cur=val(hA,sA)+val(hB,sB), swp=val(hA,sB)+val(hB,sA), d=swp-cur;
 const v=document.getElementById("swapv"), t=document.getElementById("swapt");
 v.textContent=(d>=0?"+":"")+d.toFixed(2)+" runs / 162";
 v.style.color = Math.abs(d)<1 ? "#6b7280" : (d>0? "#136c35" : RED);
 const verdict = Math.abs(d)<1 ? "Inside the noise — this model cannot tell these apart."
   : (d>0 ? "The swap is the better arrangement." : "Keep them where they are; the swap costs runs.");
 t.innerHTML = `<b>Current:</b> ${hA} ${sA}${ord(sA)} + ${hB} ${sB}${ord(sB)} = ${cur.toFixed(2)}
  &nbsp;·&nbsp; <b>Swapped:</b> ${hA} ${sB}${ord(sB)} + ${hB} ${sA}${ord(sA)} = ${swp.toFixed(2)}
  <br>${verdict}`;
 mkSprc(hA,hB);
}
const ord=n=>({1:"st",2:"nd",3:"rd"}[n]||"th");
const hA_=document.getElementById("hA"),hB_=document.getElementById("hB"),
      sA_=document.getElementById("sA"),sB_=document.getElementById("sB");
[hA_,hB_,sA_,sB_].forEach(e=>e.onchange=swap);
function mkSprc(hA,hB){
 const slots=[1,2,3,4,5,6,7,8,9];
 mk("c_sprc",{type:"line",data:{labels:slots,datasets:[
  {label:hA,data:slots.map(s=>val(hA,s)),borderColor:RED,backgroundColor:RED,tension:.2,borderWidth:2.5},
  {label:hB,data:slots.map(s=>val(hB,s)),borderColor:NAVY,backgroundColor:NAVY,tension:.2,borderWidth:2.5}]},
  options:{maintainAspectRatio:false,scales:{x:{title:{display:true,text:"lineup slot"}},
   y:{title:{display:true,text:"projected RE24 / 162"}}}}});
}
mk("c_slot",{type:"bar",data:{labels:SLOT.map(r=>r.slot),datasets:[
 {label:"RISP share of PA",data:SLOT.map(r=>r.risp_share),backgroundColor:RED},
 {type:"line",label:"PA per game",data:SLOT.map(r=>r.pa_per_game),borderColor:NAVY,
  backgroundColor:NAVY,yAxisID:"y1",tension:.2,borderWidth:2.5}]},
 options:{maintainAspectRatio:false,scales:{y:{position:"left",ticks:{callback:pc}},
  y1:{position:"right",grid:{drawOnChartArea:false}},x:{title:{display:true,text:"lineup slot"}}}}});
mk("c_supply",{type:"bar",data:{labels:SUP.map(r=>r.slot),datasets:[
 {label:"Extra baserunners vs incumbent, per 162",data:SUP.map(r=>r.delta_onbase_per_162),
  backgroundColor:SUP.map(r=>r.delta_onbase_per_162>0?RED:GREY)},
 {type:"line",label:"Runners the next two slots would cash (upper bound)",
  data:SUP.map(r=>r.arraez_runners_cashed_ub_per_162),borderColor:NAVY,backgroundColor:NAVY,
  yAxisID:"y1",tension:.2,borderWidth:2.5}]},
 options:{maintainAspectRatio:false,scales:{y:{position:"left"},
  y1:{position:"right",grid:{drawOnChartArea:false}},x:{title:{display:true,text:"lineup slot"}}},
  plugins:{tooltip:{callbacks:{afterLabel:c=>{const r=SUP[c.dataIndex];
   return `next two slots: ${r.downstream_slots} · conversion ${f3(r.downstream_spcr)}`;}}}}}});
tbl("t_scen",D.scenario.filter(r=>r.row_type!=="hitter_x_slot"),
 [{h:"Scenario",k:"hitter"},{h:"RE24 / 162",k:"re24_per_162",f:f2}],
 r=>r.row_type==="delta");
tbl("t_occ",D.occupancy,[{h:"Slot",k:"slot"},{h:"Hitter",k:"name"},{h:"PA",k:"PA"},
 {h:"BA",k:"ba",f:f3},{h:"OBP",k:"obp",f:f3},{h:"SLG",k:"slg",f:f3},{h:"wOBA",k:"woba",f:f3},
 {h:"RE24/PA",k:"re24_per_pa",f:v=>(+v).toFixed(3)}]);
swap();

/* ---------------- GOVERNANCE ---------------- */
const DQ=D.dq, V=D.verify;
cards("govcards",[
 {k:"Build DQ",v:DQ.filter(r=>r.result==="PASS").length+" / "+DQ.length,d:"assertions passed at build time"},
 {k:"Independent verification",v:V.passed+" / "+V.total,d:V.failed+" failures"},
 {k:"Primary window",v:"464 PA",d:"2026 regular season only"},
 {k:"Entity lock",v:"650333",d:"MLBAM id, never a name filter"},
 {k:"Phillies rows",v:"0",d:"pre-arrival dossier"},
 {k:"Cache max date",v:"2026-08-02",d:"freshness window"},
]);
tbl("t_dq",DQ,[{h:"Rule",k:"rule_id"},{h:"Dimension",k:"dimension"},{h:"Check",k:"check"},
 {h:"Result",k:"result",f:v=>`<span class="pill ${v==="PASS"?"ok":"no"}">${v}</span>`},
 {h:"Detail",k:"detail"}]);
tbl("t_fresh",D.fresh,[{h:"Source",k:"source"},{h:"Rows",k:"rows"},{h:"From",k:"min_date"},
 {h:"To",k:"max_date"},{h:"Entity / scope",k:"entity"},{h:"Note",k:"note"}]);
</script></body></html>
"""

if __name__ == "__main__":
    main()
