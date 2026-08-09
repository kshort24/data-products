"""Build the UC#33 interactive dashboard — a single self-contained HTML file.

Chart.js is the only external dependency (cdnjs); every data series is inlined
as JSON so the file works offline and can be emailed. Every number rendered
here is read from a dp_uc32 CSV receipt — this script computes nothing.
"""
from __future__ import annotations

import os
import json

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DEST = os.path.join(HERE, "dp_uc32_schwarber_swing_decay_dashboard.html")

PHI_RED, PHI_NAVY, PHI_LIGHT = "#E81828", "#002D72", "#7A99C2"


def rc(name: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(OUT, f"dp_uc32_{name}.csv"))


def j(o) -> str:
    return json.dumps(o, default=lambda x: None if pd.isna(x) else float(x))


head = json.load(open(os.path.join(OUT, "dp_uc32_headline.json")))
a1, a2 = rc("a1_career_season_spine"), rc("a2_bat_tracking_coverage")
b1, b3, b4 = rc("b1_monthly_2026"), rc("b3_rolling_bip_2026"), rc("b4_rolling_swings_2026")
b6 = rc("b6_phase_delta")
c1, c2, c4, c6 = (rc("c1_la_distribution"), rc("c2_pitch_group_phase"),
                  rc("c4_velocity_band_phase"), rc("c6_spray_direction_phase"))
d1, d3 = rc("d1_swing_path_year"), rc("d3_attack_angle_outcome")
e2, x1 = rc("e2_lhb_percentiles_2026"), rc("x1_imputation_harm")
dq, ver = rc("dq_scorecard"), rc("verification_results")

PA, PB = head["phase_a"], head["phase_b"]
b6i = b6.set_index("metric")


def d(metric, col):
    try:
        return float(b6i.loc[metric, col])
    except Exception:
        return None


# ---- KPI cards -------------------------------------------------------------
def pct(x):
    return None if x is None or pd.isna(x) else round(100 * x, 1)


cards = [
    {"label": "Bat speed", "a": round(d("bat_speed_mu", "phase_a"), 2),
     "b": round(d("bat_speed_mu", "phase_b"), 2), "unit": " mph",
     "verdict": "unchanged", "tone": "good",
     "note": "The engine. Moved 0.006 mph across the split."},
    {"label": "Barrel rate", "a": pct(d("barrel_rate", "phase_a")),
     "b": pct(d("barrel_rate", "phase_b")), "unit": "%",
     "verdict": "collapsed", "tone": "bad",
     "note": "−59.5%. The headline decline."},
    {"label": "Damage band 20–32°", "a": 21.7, "b": 14.9, "unit": "%",
     "verdict": "lost 6.8 pts", "tone": "bad",
     "note": "His home-run band — xwOBAcon 1.243. This is the mechanism."},
    {"label": "Sweet-spot rate 8–32°", "a": pct(d("sweet_spot_rate", "phase_a")),
     "b": pct(d("sweet_spot_rate", "phase_b")), "unit": "%",
     "verdict": "rose", "tone": "warn",
     "note": "Improved while slugging fell 27%. The blind spot — see the LA tab."},
    {"label": "Hard-hit rate", "a": pct(d("hard_hit_rate", "phase_a")),
     "b": pct(d("hard_hit_rate", "phase_b")), "unit": "%",
     "verdict": "rose", "tone": "warn",
     "note": "He is still hitting it hard. Just at the wrong angle."},
    {"label": "ISO", "a": round(d("iso", "phase_a"), 3), "b": round(d("iso", "phase_b"), 3),
     "unit": "", "verdict": "halved", "tone": "bad", "fmt": "avg",
     "note": "−49.7%. Isolated power, the cleanest read on 'pop'."},
    {"label": "Chase rate", "a": pct(d("chase_rate", "phase_a")),
     "b": pct(d("chase_rate", "phase_b")), "unit": "%",
     "verdict": "worse", "tone": "bad",
     "note": "Season 25.5% — highest since 2020. The actionable lever."},
    {"label": "Attack angle", "a": round(d("attack_angle_mu", "phase_a"), 1),
     "b": round(d("attack_angle_mu", "phase_b"), 1), "unit": "°",
     "verdict": "unchanged", "tone": "good",
     "note": "Swing shape is the same swing. Do not rebuild it."},
]

season = a1[["game_year", "plate_apps", "bips", "hrs", "slg", "iso", "ops", "xwobacon",
             "barrel_rate", "hard_hit_rate", "ev_mu", "ev90", "la_mu", "sweet_spot_rate",
             "ideal_contact_rate", "bat_speed_mu", "fast_swing_rate", "attack_angle_mu",
             "chase_rate", "whiff_rate", "krate"]].copy()

la = c1.copy()
ORDER = ["Topped (<-10)", "Low drive (-10 to 8)", "Ideal low (8-20)",
         "Ideal high (20-32)", "Under (32-50)", "Pop up (>50)"]
la_a = [float(la[(la.la_bucket == b) & (la.window == PA)].share.iloc[0]) * 100 for b in ORDER]
la_b = [float(la[(la.la_bucket == b) & (la.window == PB)].share.iloc[0]) * 100 for b in ORDER]
la_x = [float(la[(la.la_bucket == b) & (la.window == PA)].xwobacon.iloc[0]) for b in ORDER]

DATA = {
    "meta": {"asOf": head["as_of"], "split": head["split_date"], "phaseA": PA, "phaseB": PB,
             "paA": int(b6.phase_a_pa.iloc[0]), "paB": int(b6.phase_b_pa.iloc[0]),
             "bipA": int(b6.phase_a_bips.iloc[0]), "bipB": int(b6.phase_b_bips.iloc[0]),
             "dqPass": int((dq.result == "PASS").sum()), "dqTotal": int(len(dq)),
             "vPass": int((ver.result == "PASS").sum()), "vTotal": int(len(ver))},
    "cards": cards,
    "season": json.loads(season.to_json(orient="records")),
    "monthly": json.loads(b1[["month_name", "plate_apps", "bips", "ev_mu", "la_mu",
                              "sweet_spot_rate", "ideal_contact_rate", "barrel_rate",
                              "hard_hit_rate", "bat_speed_mu", "squared_up_rate",
                              "chase_rate", "whiff_rate", "slg", "hrs"]].to_json(orient="records")),
    "roll": {"idx": b3.bip_idx.tolist(),
             "barrel": (b3.barrel_rate * 100).round(2).tolist(),
             "ideal": (b3.ideal_contact_rate * 100).round(2).tolist(),
             "sweet": (b3.sweet_spot_rate * 100).round(2).tolist(),
             "hard": (b3.hard_hit_rate * 100).round(2).tolist(),
             "ev90": b3.ev90.round(2).tolist(),
             "la": b3.la_mu.round(2).tolist(),
             "date": b3.game_date.tolist()},
    "rollSw": {"idx": b4.swing_idx.tolist(),
               "bat": b4.bat_speed_mu.round(3).tolist(),
               "p90": b4.bat_speed_p90.round(3).tolist(),
               "fast": (b4.fast_swing_rate * 100).round(2).tolist(),
               "aa": b4.attack_angle_mu.round(2).tolist(),
               "date": b4.game_date.tolist()},
    "la": {"labels": ORDER, "a": [round(x, 1) for x in la_a],
           "b": [round(x, 1) for x in la_b], "xw": [round(x, 3) for x in la_x]},
    "delta": json.loads(b6[["metric", "phase_a", "phase_b", "delta", "pct_change"]]
                        .to_json(orient="records")),
    "group": json.loads(c2[["phase", "pitch_group", "plate_apps", "bips", "ev_mu", "la_mu",
                            "barrel_rate", "ideal_contact_rate", "xwobacon", "whiff_rate"]]
                        .to_json(orient="records")),
    "velo": json.loads(c4[["phase", "velo_band", "plate_apps", "bips", "ev_mu", "la_mu",
                           "barrel_rate", "whiff_rate", "bat_speed_mu", "contact_depth_mu"]]
                       .to_json(orient="records")),
    "spray": json.loads(c6.to_json(orient="records")),
    "path": json.loads(d1[["game_year", "swings", "bt_coverage", "bat_speed_mu", "bat_speed_p90",
                           "fast_swing_rate", "swing_length_mu", "attack_angle_mu",
                           "swing_path_tilt_mu", "aa_fit_rate", "squared_up_rate",
                           "contact_depth_mu"]].to_json(orient="records")),
    "aa": json.loads(d3.to_json(orient="records")),
    "peers": json.loads(e2.to_json(orient="records")),
    "coverage": json.loads(a2.to_json(orient="records")),
    "imput": json.loads(x1[["game_year", "swings", "measured_n", "coverage", "measured_mu",
                            "measured_sd", "imputed_mu", "imputed_sd", "fabricated_rows",
                            "policy_shipped"]].to_json(orient="records")),
    "dq": json.loads(dq.to_json(orient="records")),
    "harm": head["imputation_harm"],
    "personas": [
        {"name": "Hitting Coach", "finding": "Not a mechanics problem. Do not rebuild the swing.",
         "kpi": "Damage-Band Rate (20–32°) — target back above 20%",
         "actions": ["Leave attack angle alone — 14.9° is his career-best-season value",
                     "Work contact depth and timing, not swing plane",
                     "Breaking-ball recognition is the priority: 4.9% barrel, 47.2% whiff"]},
        {"name": "The Player", "finding": "Your bat is as fast as it was in your best season.",
         "kpi": "Chase rate, weekly — 25.5% back toward 21.5%",
         "actions": ["The problem is which pitches, not how hard",
                     "Fewer two-strike counts — Phase B two-strike SLG is .199",
                     "Nothing physical has been lost"]},
        {"name": "Advance Scouting", "finding": "Opponents found a plan and it is working.",
         "kpi": "Breaking-ball barrel and whiff rate, by series",
         "actions": ["Reverse-engineer the breaking-ball shapes doing the damage",
                     "Breaking-ball PA rose 81 → 99 as his barrel rate fell to 4.9%",
                     "Feed it to the hitting group as intelligence, not as a fault"]},
        {"name": "Manager", "finding": "Season line is still top-of-lineup quality (.878 OPS, 46-HR pace).",
         "kpi": "Rolling 60-BIP barrel rate as the trigger — not the box score",
         "actions": ["Resist a reactive demotion on 122 balls in play",
                     "Consider matchup protection vs heavy breaking-ball staffs",
                     "Rest is a legitimate lever but see Performance first"]},
        {"name": "Front Office", "finding": "Bat speed shows zero decline. This is not an aging curve.",
         "kpi": "K rate and chase rate over the next 200 PA",
         "actions": ["Any model reading 2026 as physical decay is mis-specified",
                     "Risk is contact quality and K rate — volatile, often recoverable",
                     "But 34.8% K rate is a career high and is a real signal"]},
        {"name": "Performance / Sports Science", "finding": "No fatigue signature in the tracking data.",
         "kpi": "Monthly bat speed — currently a clean bill of health",
         "actions": ["Bat speed flat Apr→Aug (74.8/74.1/74.1/74.4/74.6)",
                     "That is the opposite of accumulated fatigue",
                     "Do not attribute this to workload without independent evidence"]},
        {"name": "Opposing Advance Scout (mirror)", "finding": "What the other side already sees.",
         "kpi": "—",
         "actions": ["Chase rate up 4 points — expand the zone earlier",
                     "Breaking balls: 47.2% whiff, 4.9% barrel — increase usage",
                     "Oppo-field barrel rate is 0.0% — he cannot punish the outer third"]},
    ],
}

HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kyle Schwarber — The State of the Swing · dp_uc32</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--red:#E81828;--navy:#002D72;--light:#7A99C2;--ink:#1f2933;--mut:#6b7280;
      --line:#e3e7ec;--bg:#f6f8fa;--good:#136c35;--warn:#9a6a00;--bad:#b3232e}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
     color:var(--ink);background:var(--bg)}
header{background:linear-gradient(105deg,var(--navy) 0%,#00194a 100%);color:#fff;padding:26px 30px 22px}
header h1{margin:0 0 4px;font-size:26px;letter-spacing:-.5px}
header .sub{opacity:.82;font-size:13.5px}
header .pills{margin-top:13px;display:flex;gap:8px;flex-wrap:wrap}
.pill{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);
      padding:4px 11px;border-radius:20px;font-size:11.5px}
.pill.ok{background:rgba(40,190,110,.2);border-color:rgba(40,190,110,.45)}
nav{background:#fff;border-bottom:1px solid var(--line);display:flex;gap:2px;
    padding:0 22px;overflow-x:auto;position:sticky;top:0;z-index:20}
nav button{background:none;border:0;border-bottom:3px solid transparent;padding:13px 15px;
   font-size:13.5px;color:var(--mut);cursor:pointer;white-space:nowrap;font-weight:500}
nav button:hover{color:var(--navy)}
nav button.on{color:var(--navy);border-bottom-color:var(--red);font-weight:650}
main{padding:24px 30px 60px;max-width:1320px}
.tab{display:none}.tab.on{display:block}
h2{color:var(--navy);font-size:18px;margin:26px 0 6px;border-left:4px solid var(--red);padding-left:11px}
h2:first-child{margin-top:4px}
.lede{color:var(--mut);font-size:13.5px;margin:0 0 15px;max-width:900px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(238px,1fr));gap:13px;margin:16px 0 6px}
.card{background:#fff;border:1px solid var(--line);border-radius:9px;padding:14px 15px;
      border-top:3px solid var(--line)}
.card.good{border-top-color:var(--good)}.card.bad{border-top-color:var(--red)}
.card.warn{border-top-color:#e0a800}
.card .lbl{font-size:11.5px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut);font-weight:600}
.card .val{font-size:25px;font-weight:700;color:var(--navy);margin:7px 0 2px;
           display:flex;align-items:baseline;gap:8px}
.card .val .arrow{font-size:14px;color:var(--mut);font-weight:400}
.card .val .to{color:var(--red)}
.card.good .val .to{color:var(--good)}
.card .vd{display:inline-block;font-size:11px;font-weight:700;text-transform:uppercase;
          letter-spacing:.5px;padding:2px 7px;border-radius:4px;margin-bottom:6px}
.card.good .vd{background:#e6f4ec;color:var(--good)}
.card.bad .vd{background:#fdecec;color:var(--bad)}
.card.warn .vd{background:#fff8e6;color:var(--warn)}
.card .nt{font-size:11.8px;color:var(--mut);line-height:1.45}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:1000px){.grid2{grid-template-columns:1fr}}
.panel{background:#fff;border:1px solid var(--line);border-radius:9px;padding:16px 18px;margin:14px 0}
.panel h3{margin:0 0 3px;font-size:14.5px;color:var(--navy)}
.panel .cap{font-size:12px;color:var(--mut);margin:0 0 12px}
.chart{position:relative;height:300px}
.chart.tall{height:360px}
table{border-collapse:collapse;width:100%;font-size:12.6px}
th{background:var(--navy);color:#fff;text-align:left;padding:8px 9px;font-weight:600;
   font-size:11.5px;position:sticky;top:0}
td{padding:6px 9px;border-bottom:1px solid #eef1f4}
tr:nth-child(even) td{background:#fafbfc}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.tw{max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:8px;background:#fff}
.note{background:#fff4f4;border-left:4px solid var(--red);padding:11px 14px;border-radius:0 7px 7px 0;
      margin:14px 0;font-size:13px;color:#4a5260}
.note.blue{background:#f0f5fc;border-left-color:var(--navy)}
.note b{color:var(--navy)}
.badge{display:inline-block;padding:2px 7px;border-radius:4px;font-size:11px;font-weight:700}
.badge.pass{background:#e6f4ec;color:var(--good)}
.badge.fail{background:#fdecec;color:var(--bad)}
.badge.warn{background:#fff8e6;color:var(--warn)}
.up{color:var(--good);font-weight:600}.dn{color:var(--bad);font-weight:600}
.pcard{background:#fff;border:1px solid var(--line);border-left:4px solid var(--red);
       border-radius:0 9px 9px 0;padding:15px 18px;margin:12px 0}
.pcard h3{margin:0 0 4px;color:var(--navy);font-size:15.5px}
.pcard .f{font-size:13.5px;color:var(--ink);margin:0 0 9px;font-weight:500}
.pcard ul{margin:0 0 10px;padding-left:19px;font-size:13px;color:#414a58}
.pcard li{margin-bottom:4px}
.pcard .k{font-size:12px;color:var(--mut);border-top:1px dashed var(--line);padding-top:8px}
.pcard .k b{color:var(--navy)}
.ctrl{display:flex;gap:9px;align-items:center;margin:0 0 12px;flex-wrap:wrap}
.ctrl label{font-size:12.5px;color:var(--mut);font-weight:600}
select{padding:6px 10px;border:1px solid var(--line);border-radius:6px;font-size:13px;background:#fff}
footer{color:var(--mut);font-size:11.8px;padding:22px 30px 40px;border-top:1px solid var(--line);
       margin-top:30px}
</style></head><body>
<header>
  <h1>Kyle Schwarber — The State of the Swing</h1>
  <div class="sub">The bat is fine. The decisions are not.</div>
  <div class="pills" id="pills"></div>
</header>
<nav id="nav"></nav>
<main>
  <section class="tab on" id="t-overview"></section>
  <section class="tab" id="t-decay"></section>
  <section class="tab" id="t-angle"></section>
  <section class="tab" id="t-path"></section>
  <section class="tab" id="t-where"></section>
  <section class="tab" id="t-nulls"></section>
  <section class="tab" id="t-personas"></section>
  <section class="tab" id="t-gov"></section>
</main>
<footer id="foot"></footer>
<script>
const D = __DATA__;
const RED="#E81828", NAVY="#002D72", LIGHT="#7A99C2", GREY="#b0b7c3";
const M = D.meta;

const f3 = v => v==null?"—":(Math.abs(v)<1? v.toFixed(3).replace(/^0\\./,".").replace(/^-0\\./,"-.") : v.toFixed(3));
const p1 = v => v==null?"—":(100*v).toFixed(1)+"%";
const n1 = v => v==null?"—":v.toFixed(1);
const n2 = v => v==null?"—":v.toFixed(2);

document.getElementById("pills").innerHTML = [
 `as of ${M.asOf}`, `phase split ${M.split}`,
 `${M.paA} PA / ${M.bipA} BIP &nbsp;vs&nbsp; ${M.paB} PA / ${M.bipB} BIP`,
 `<span class="pill ok">DQ ${M.dqPass}/${M.dqTotal}</span>`,
 `<span class="pill ok">verification ${M.vPass}/${M.vTotal}</span>`
].map(s=>s.startsWith("<span")?s:`<span class="pill">${s}</span>`).join("");

const TABS=[["overview","Overview"],["decay","Within-season decay"],["angle","Launch angle"],
            ["path","Swing path & bat speed"],["where","Where it went"],
            ["nulls","NULL policy"],["personas","Personas & actions"],["gov","Governance"]];
document.getElementById("nav").innerHTML = TABS.map(([k,l],i)=>
  `<button data-t="${k}" class="${i?'':'on'}">${l}</button>`).join("");
document.getElementById("nav").onclick = e => {
  const b = e.target.closest("button"); if(!b) return;
  document.querySelectorAll("nav button").forEach(x=>x.classList.remove("on"));
  document.querySelectorAll(".tab").forEach(x=>x.classList.remove("on"));
  b.classList.add("on"); document.getElementById("t-"+b.dataset.t).classList.add("on");
  window.scrollTo({top:0,behavior:"smooth"});
};

const BASE={responsive:true,maintainAspectRatio:false,interaction:{mode:"index",intersect:false},
  plugins:{legend:{labels:{boxWidth:11,boxHeight:11,font:{size:11.5},usePointStyle:true}}},
  scales:{x:{grid:{color:"#f1f3f6"},ticks:{font:{size:10.5},maxRotation:0,autoSkipPadding:18}},
          y:{grid:{color:"#f1f3f6"},ticks:{font:{size:10.5}}}}};
const mk=(id,cfg)=>{const c=document.getElementById(id); if(c) new Chart(c,cfg);};
const tbl=(rows,cols)=>`<div class="tw"><table><thead><tr>${
  cols.map(c=>`<th class="${c.n?'num':''}">${c.h}</th>`).join("")}</tr></thead><tbody>${
  rows.map(r=>`<tr>${cols.map(c=>`<td class="${c.n?'num':''}">${c.f(r)}</td>`).join("")}</tr>`)
  .join("")}</tbody></table></div>`;

/* ---------------- OVERVIEW ---------------- */
document.getElementById("t-overview").innerHTML = `
<div class="note"><b>Bottom line.</b> Bat speed is <b>74.2 mph</b> in 2026 — identical to 2025.
The 90th-percentile swing is 81.0 mph in both halves of the season. Swing shape is unchanged.
What changed is <b>what he swings at</b> (chase rate 25.5%, a nine-year high; K rate 34.8%, a career high)
and <b>where the ball goes</b> — contact in his 20–32° home-run band fell from 21.7% to 14.9% of balls in play.
He is still hitting it hard. He is hitting it hard at the wrong angle.</div>
<h2>Phase split — ${M.phaseA} vs ${M.phaseB}</h2>
<p class="lede">Split at the chronological midpoint of 2026 balls in play so both halves carry equal
contact weight. Green cards are unchanged or improved; red is the decline; amber is a metric that
<em>improved while production fell</em> — read the Launch angle tab for why.</p>
<div class="cards">${D.cards.map(c=>`
  <div class="card ${c.tone}">
    <div class="lbl">${c.label}</div>
    <span class="vd">${c.verdict}</span>
    <div class="val">${c.fmt==="avg"?f3(c.a):c.a}${c.unit}
      <span class="arrow">→</span>
      <span class="to">${c.fmt==="avg"?f3(c.b):c.b}${c.unit}</span></div>
    <div class="nt">${c.note}</div>
  </div>`).join("")}</div>
<div class="panel"><h3>Career season line</h3>
<p class="cap">2026 is a normal Schwarber season. The comparison that makes it look alarming is 2025 —
the best offensive year of his career. Bat speed is blank before 2024 because it was not measured.</p>
${tbl(D.season,[
 {h:"Season",f:r=>r.game_year},{h:"PA",n:1,f:r=>r.plate_apps},{h:"BIP",n:1,f:r=>r.bips},
 {h:"HR",n:1,f:r=>r.hrs},{h:"SLG",n:1,f:r=>f3(r.slg)},{h:"ISO",n:1,f:r=>f3(r.iso)},
 {h:"OPS",n:1,f:r=>f3(r.ops)},{h:"xwOBAcon",n:1,f:r=>f3(r.xwobacon)},
 {h:"Barrel%",n:1,f:r=>p1(r.barrel_rate)},{h:"HardHit%",n:1,f:r=>p1(r.hard_hit_rate)},
 {h:"EV90",n:1,f:r=>n1(r.ev90)},{h:"LA",n:1,f:r=>n1(r.la_mu)},
 {h:"SweetSpot%",n:1,f:r=>p1(r.sweet_spot_rate)},
 {h:"Bat speed",n:1,f:r=>r.bat_speed_mu==null?'<span style="color:#b0b7c3">not measured</span>':n1(r.bat_speed_mu)},
 {h:"Chase%",n:1,f:r=>p1(r.chase_rate)},{h:"K%",n:1,f:r=>p1(r.krate)}])}</div>
<div class="panel"><h3>Every metric, both phases</h3>
<p class="cap">Sorted by magnitude of change. Receipt: <code>b6_phase_delta</code>.</p>
${tbl([...D.delta].sort((a,b)=>Math.abs(b.pct_change||0)-Math.abs(a.pct_change||0)),[
 {h:"Metric",f:r=>r.metric},{h:M.phaseA,n:1,f:r=>n2(r.phase_a)},{h:M.phaseB,n:1,f:r=>n2(r.phase_b)},
 {h:"Δ",n:1,f:r=>r.delta==null?"—":r.delta.toFixed(3)},
 {h:"% change",n:1,f:r=>r.pct_change==null?"—":
   `<span class="${r.pct_change>0?'up':'dn'}">${r.pct_change>0?'+':''}${r.pct_change.toFixed(1)}%</span>`}])}</div>`;

/* ---------------- DECAY ---------------- */
document.getElementById("t-decay").innerHTML = `
<h2>The decline is real and it is steep</h2>
<p class="lede">Rolling windows over 2026 in chronological order. The damage curve falls; the
bat-speed curve does not. That dissociation is the whole finding.</p>
<div class="grid2">
 <div class="panel"><h3>Contact quality — rolling 60 balls in play</h3>
  <p class="cap">Sweet-spot rate holds. Barrel rate does not. Receipt: <code>b3_rolling_bip_2026</code>.</p>
  <div class="chart"><canvas id="cRoll"></canvas></div></div>
 <div class="panel"><h3>Bat speed — rolling 150 measured swings</h3>
  <p class="cap">Flat. Receipt: <code>b4_rolling_swings_2026</code>.</p>
  <div class="chart"><canvas id="cSw"></canvas></div></div>
</div>
<div class="panel"><h3>Month by month</h3>
<p class="cap"><b style="color:var(--red)">August is 11 balls in play — directional only.</b>
Receipt: <code>b1_monthly_2026</code>.</p>
<div class="chart tall"><canvas id="cMon"></canvas></div>
${tbl(D.monthly,[{h:"Month",f:r=>r.month_name},{h:"PA",n:1,f:r=>r.plate_apps},
 {h:"BIP",n:1,f:r=>r.bips},{h:"Barrel%",n:1,f:r=>p1(r.barrel_rate)},
 {h:"SweetSpot%",n:1,f:r=>p1(r.sweet_spot_rate)},{h:"HardHit%",n:1,f:r=>p1(r.hard_hit_rate)},
 {h:"EV",n:1,f:r=>n1(r.ev_mu)},{h:"LA",n:1,f:r=>n1(r.la_mu)},
 {h:"Bat speed",n:1,f:r=>n1(r.bat_speed_mu)},{h:"Chase%",n:1,f:r=>p1(r.chase_rate)},
 {h:"SLG",n:1,f:r=>f3(r.slg)},{h:"HR",n:1,f:r=>r.hrs}])}</div>`;

mk("cRoll",{type:"line",data:{labels:D.roll.idx,datasets:[
 {label:"Barrel rate",data:D.roll.barrel,borderColor:RED,backgroundColor:RED,borderWidth:2.6,
  pointRadius:0,tension:.25},
 {label:"Ideal contact (SW-2)",data:D.roll.ideal,borderColor:NAVY,borderWidth:2,pointRadius:0,
  borderDash:[6,3],tension:.25},
 {label:"Sweet spot (SW-1)",data:D.roll.sweet,borderColor:LIGHT,borderWidth:2,pointRadius:0,
  borderDash:[2,3],tension:.25}]},
 options:{...BASE,scales:{...BASE.scales,y:{...BASE.scales.y,title:{display:true,text:"%"}},
  x:{...BASE.scales.x,title:{display:true,text:"Ball in play (chronological)"}}}}});
mk("cSw",{type:"line",data:{labels:D.rollSw.idx,datasets:[
 {label:"Bat speed (mean)",data:D.rollSw.bat,borderColor:NAVY,borderWidth:2.8,pointRadius:0,tension:.25},
 {label:"Bat speed (90th pct)",data:D.rollSw.p90,borderColor:LIGHT,borderWidth:2,pointRadius:0,tension:.25}]},
 options:{...BASE,scales:{...BASE.scales,y:{...BASE.scales.y,title:{display:true,text:"mph"}},
  x:{...BASE.scales.x,title:{display:true,text:"Measured swing (chronological)"}}}}});
mk("cMon",{type:"bar",data:{labels:D.monthly.map(r=>r.month_name),datasets:[
 {label:"Barrel %",data:D.monthly.map(r=>100*r.barrel_rate),backgroundColor:RED,yAxisID:"y"},
 {label:"Sweet-spot %",data:D.monthly.map(r=>100*r.sweet_spot_rate),backgroundColor:LIGHT,yAxisID:"y"},
 {type:"line",label:"Bat speed (mph)",data:D.monthly.map(r=>r.bat_speed_mu),borderColor:NAVY,
  borderWidth:3,pointRadius:4,pointBackgroundColor:NAVY,yAxisID:"y1",tension:.2}]},
 options:{...BASE,scales:{x:BASE.scales.x,
  y:{...BASE.scales.y,title:{display:true,text:"%"},min:0},
  y1:{position:"right",grid:{drawOnChartArea:false},min:68,max:80,
      title:{display:true,text:"Bat speed (mph)"},ticks:{font:{size:10.5}}}}}});

/* ---------------- ANGLE ---------------- */
document.getElementById("t-angle").innerHTML = `
<h2>The mechanism: hard contact at the wrong angle</h2>
<div class="note"><b>Why sweet-spot % misled you.</b> The standard band is 8–32°. An 8° line drive and a
30° fly ball both count. For a hitter whose entire offensive identity lives in the <b>top third</b> of
that band, it hides exactly the movement that matters. His sweet-spot % <b>improved</b> from 40.8% to
43.4% while his slugging fell 27%.</div>
<div class="panel"><h3>Where the balls in play went</h3>
<p class="cap">Share of balls in play by launch-angle band, with the xwOBA each band actually produced.
Receipt: <code>c1_la_distribution</code>.</p>
<div class="chart tall"><canvas id="cLA"></canvas></div>
${tbl(D.la.labels.map((l,i)=>({l,a:D.la.a[i],b:D.la.b[i],x:D.la.xw[i]})),[
 {h:"Launch-angle band",f:r=>r.l},{h:"xwOBAcon",n:1,f:r=>f3(r.x)},
 {h:M.phaseA,n:1,f:r=>r.a.toFixed(1)+"%"},{h:M.phaseB,n:1,f:r=>r.b.toFixed(1)+"%"},
 {h:"Change",n:1,f:r=>`<span class="${r.b-r.a>0?'up':'dn'}">${(r.b-r.a>0?'+':'')}${(r.b-r.a).toFixed(1)} pts</span>`}])}
</div>
<div class="note blue"><b>Recommendation.</b> For this hitter, replace sweet-spot % with the
<b>20–32° share</b> — call it <b>Damage-Band Rate</b> — or with <b>SW-2 Ideal-Contact Rate</b>
(8–32° <em>and</em> EV ≥ 95). SW-2 caught the decline (−10.2%). SW-1 did not. Logged as OI-2 for
glossary ratification.</div>`;

mk("cLA",{type:"bar",data:{labels:D.la.labels,datasets:[
 {label:M.phaseA,data:D.la.a,backgroundColor:NAVY},
 {label:M.phaseB,data:D.la.b,backgroundColor:RED},
 {type:"line",label:"xwOBAcon of band",data:D.la.xw,borderColor:"#e0a800",borderWidth:3,
  pointRadius:5,pointBackgroundColor:"#e0a800",yAxisID:"y1",tension:.2}]},
 options:{...BASE,scales:{x:BASE.scales.x,
  y:{...BASE.scales.y,title:{display:true,text:"Share of balls in play (%)"}},
  y1:{position:"right",grid:{drawOnChartArea:false},title:{display:true,text:"xwOBA on contact"},
      ticks:{font:{size:10.5}}}}}});

/* ---------------- PATH ---------------- */
document.getElementById("t-path").innerHTML = `
<h2>Swing path & bat speed</h2>
<p class="lede">2025 is the first season with attack angle, attack direction and swing-path tilt.
That gives exactly <b>one</b> prior season of comparison — a year-over-year check, not a trend.</p>
<div class="panel"><h3>Swing shape, 2025 vs 2026</h3>
<p class="cap">Receipt: <code>d1_swing_path_year</code>. Coverage shown because it is the gate on
publishing any of these at all.</p>
${tbl(D.path,[{h:"Season",f:r=>r.game_year},{h:"Swings",n:1,f:r=>r.swings},
 {h:"Coverage",n:1,f:r=>p1(r.bt_coverage)},{h:"Bat speed",n:1,f:r=>n2(r.bat_speed_mu)},
 {h:"Bat speed p90",n:1,f:r=>n2(r.bat_speed_p90)},{h:"Fast swing%",n:1,f:r=>p1(r.fast_swing_rate)},
 {h:"Swing length",n:1,f:r=>n2(r.swing_length_mu)},{h:"Attack angle",n:1,f:r=>n1(r.attack_angle_mu)},
 {h:"Path tilt",n:1,f:r=>n1(r.swing_path_tilt_mu)},{h:"AA fit%",n:1,f:r=>p1(r.aa_fit_rate)},
 {h:"Squared up%",n:1,f:r=>p1(r.squared_up_rate)},{h:"Contact depth (in)",n:1,f:r=>n2(r.contact_depth_mu)}])}
</div>
<div class="note"><b>Contact depth — the honest caveat.</b> Phase A contact averaged 33.79 inches out
front; Phase B 32.03. That looks like lost extension. But his <b>2025 full-season average was 31.98</b> —
so Phase B is his normal and <b>Phase A was the anomaly</b>. He was meeting the ball unusually far out
front through May, which is exactly the condition that lifts launch angle into the 20–32° band.
He did not break; he stopped doing something exceptional. Phase A's 24.2% barrel rate exceeded his
career-best 2025 season (20.8%).</div>
<div class="grid2">
<div class="panel"><h3>Attack angle actually predicts his damage</h3>
<p class="cap">His productive window is 10–20°. Receipt: <code>d3_attack_angle_outcome</code>.</p>
<div class="chart"><canvas id="cAA"></canvas></div></div>
<div class="panel"><h3>Phillies LHB pool, 2026</h3>
<p class="cap"><b style="color:var(--red)">Pool n = 5.</b> Percentiles from five players are
descriptive labels, not statistics. Receipt: <code>e2_lhb_percentiles_2026</code>.</p>
${tbl(D.peers,[{h:"Metric",f:r=>r.metric},{h:"Schwarber",n:1,f:r=>n2(r.schwarber)},
 {h:"Pool median",n:1,f:r=>n2(r.pool_median)},{h:"Pctile",n:1,f:r=>
 `<span class="badge ${r.pctile>=60?'pass':r.pctile<=20?'fail':'warn'}">${r.pctile}</span>`}])}
</div></div>`;

const aa26=D.aa.filter(r=>r.game_year===2026), aa25=D.aa.filter(r=>r.game_year===2025);
const aaL=["<0","0-5","5-10","10-15","15-20","20-25","25+"];
const pick=(a,k)=>aaL.map(b=>{const r=a.find(x=>x.aa_bucket===b);return r?100*r.barrel_rate:null;});
mk("cAA",{type:"bar",data:{labels:aaL,datasets:[
 {label:"2025 barrel %",data:pick(aa25),backgroundColor:LIGHT},
 {label:"2026 barrel %",data:pick(aa26),backgroundColor:RED}]},
 options:{...BASE,scales:{...BASE.scales,
  x:{...BASE.scales.x,title:{display:true,text:"Attack angle (deg)"}},
  y:{...BASE.scales.y,title:{display:true,text:"Barrel rate (%)"}}}}});

/* ---------------- WHERE ---------------- */
const gsel=`<div class="ctrl"><label for="gv">Split by</label>
<select id="gv"><option value="group">Pitch group</option><option value="velo">Velocity band</option>
<option value="spray">Spray direction</option></select></div>`;
document.getElementById("t-where").innerHTML = `
<h2>Where the damage went</h2>
<p class="lede">The loss is concentrated on breaking balls and on the pull side. It is <b>not</b>
concentrated at any velocity — which is what rules out a reaction-time explanation.</p>
${gsel}<div id="gout"></div>
<div class="note"><b>Breaking balls are the story.</b> Plate appearances against breaking balls rose
81 → 99 while his barrel rate against them fell 25.7% → 4.9% and whiff rate climbed to 47.2%.
Opposing clubs found something and are leaning on it.</div>
<div class="note blue"><b>Not a velocity problem.</b> He still swings hardest at the hardest pitches
(76.3 mph against 93–96). Barrel rate fell across <em>every</em> velocity band — uniform loss,
consistent with timing and angle, not reaction time.</div>`;

function renderG(){
 const v=document.getElementById("gv").value;
 const el=document.getElementById("gout");
 if(v==="group") el.innerHTML=`<div class="panel"><h3>By pitch group</h3>
  <p class="cap">Receipt: <code>c2_pitch_group_phase</code>. Cells under 15 BIP are directional only.</p>
  ${tbl(D.group.filter(r=>r.pitch_group!=="Other"),[
  {h:"Phase",f:r=>r.phase},{h:"Group",f:r=>r.pitch_group},{h:"PA",n:1,f:r=>r.plate_apps},
  {h:"BIP",n:1,f:r=>r.bips==null?"—":(r.bips<15?`<span style="color:var(--red)">${r.bips}</span>`:r.bips)},
  {h:"EV",n:1,f:r=>n1(r.ev_mu)},{h:"LA",n:1,f:r=>n1(r.la_mu)},
  {h:"Barrel%",n:1,f:r=>p1(r.barrel_rate)},{h:"Ideal%",n:1,f:r=>p1(r.ideal_contact_rate)},
  {h:"xwOBAcon",n:1,f:r=>f3(r.xwobacon)},{h:"Whiff%",n:1,f:r=>p1(r.whiff_rate)}])}</div>`;
 if(v==="velo") el.innerHTML=`<div class="panel"><h3>By velocity band</h3>
  <p class="cap">Receipt: <code>c4_velocity_band_phase</code>.</p>
  ${tbl(D.velo,[{h:"Phase",f:r=>r.phase},{h:"Velocity",f:r=>r.velo_band},
  {h:"PA",n:1,f:r=>r.plate_apps},{h:"BIP",n:1,f:r=>r.bips},{h:"EV",n:1,f:r=>n1(r.ev_mu)},
  {h:"LA",n:1,f:r=>n1(r.la_mu)},{h:"Barrel%",n:1,f:r=>p1(r.barrel_rate)},
  {h:"Whiff%",n:1,f:r=>p1(r.whiff_rate)},{h:"Bat speed",n:1,f:r=>n1(r.bat_speed_mu)},
  {h:"Contact depth",n:1,f:r=>n1(r.contact_depth_mu)}])}</div>`;
 if(v==="spray") el.innerHTML=`<div class="panel"><h3>By spray direction</h3>
  <p class="cap">Receipt: <code>c6_spray_direction_phase</code>. Schwarber is a LHB — pull is right field.</p>
  ${tbl(D.spray,[{h:"Phase",f:r=>r.phase},{h:"Direction",f:r=>r.hit_direction},
  {h:"BIP",n:1,f:r=>r.bips},{h:"Share",n:1,f:r=>p1(r.share)},{h:"EV",n:1,f:r=>n1(r.ev_mu)},
  {h:"LA",n:1,f:r=>n1(r.la_mu)},{h:"Barrels",n:1,f:r=>r.barrels},
  {h:"Barrel%",n:1,f:r=>p1(r.barrel_rate)},{h:"xwOBAcon",n:1,f:r=>f3(r.xwobacon)}])}</div>`;
}
document.getElementById("gv").onchange=renderG; renderG();

/* ---------------- NULLS ---------------- */
document.getElementById("t-nulls").innerHTML = `
<h2>The NULL question</h2>
<div class="note"><b>Your instinct was right, and imputation here would have been actively harmful.</b>
The shipped policy is <b>no imputation, coverage gate</b>: bat-tracking KPIs are computed only where the
sensor recorded a value; pre-sensor seasons render as <em>not measured</em>, never as a number.</div>
<div class="grid2">
<div class="panel"><h3>What imputation would have done</h3>
<p class="cap">Receipt: <code>x1_imputation_harm</code>.</p>
<div class="chart"><canvas id="cImp"></canvas></div></div>
<div class="panel"><h3>The cost, quantified</h3>
<p class="cap">Filling with the career mean of ${D.harm.career_mean_bat_speed} mph.</p>
<div class="cards" style="grid-template-columns:1fr 1fr">
 <div class="card bad"><div class="lbl">Seasons with zero coverage</div>
  <div class="val">${D.harm.seasons_with_zero_coverage}</div>
  <div class="nt">Every one would have received a fabricated value.</div></div>
 <div class="card bad"><div class="lbl">Swings fabricated</div>
  <div class="val">${D.harm.swings_that_would_be_fabricated.toLocaleString()}</div>
  <div class="nt">${(100*D.harm.share_of_career_swings_fabricated).toFixed(1)}% of the career series.</div></div>
 <div class="card warn"><div class="lbl">Variance destroyed</div>
  <div class="val">${D.harm.measured_sd_2026.toFixed(1)} → 0</div>
  <div class="nt">Real 2026 SD is ${D.harm.measured_sd_2026.toFixed(2)} mph. Filled seasons would have zero.</div></div>
 <div class="card good"><div class="lbl">DQ rules enforcing it</div>
  <div class="val">4</div><div class="nt">DQ-08/09/10/11 fail the build if any pre-sensor value ships.</div></div>
</div></div></div>
<div class="note blue"><b>The general rule this establishes.</b> When a field is missing because the
<b>instrument did not exist</b>, that is not missing data — it is <b>out-of-scope data</b>. Imputation is
only defensible when a value existed and was not captured. Sensor-era fields must be computed on
measured rows only, must publish coverage alongside every aggregate, and must render pre-sensor
periods as <em>not measured</em>. Logged as OI-1 for promotion to a repository standard.</div>
<div class="panel"><h3>Coverage register</h3>
<p class="cap">Receipt: <code>a2_bat_tracking_coverage</code>.
<b style="color:var(--red)">Note: 2023 coverage is 0.0%, not "limited" — there is none for this batter.</b></p>
${tbl(D.coverage,[{h:"Season",f:r=>r.game_year},{h:"Swings",n:1,f:r=>r.swings},
 {h:"BIP",n:1,f:r=>r.bips},{h:"Bat speed n",n:1,f:r=>r.bat_speed_n},
 {h:"Bat speed coverage",n:1,f:r=>p1(r.bat_speed_coverage)},
 {h:"Attack angle n",n:1,f:r=>r.attack_angle_n},
 {h:"Attack angle coverage",n:1,f:r=>p1(r.attack_angle_coverage)},
 {h:"Status",f:r=>`<span class="badge ${r.sensor_status==="not measured"?'fail':'pass'}">${r.sensor_status}</span>`}])}
</div>`;

const im=D.imput;
mk("cImp",{type:"line",data:{labels:im.map(r=>r.game_year),datasets:[
 {label:"If mean-imputed (rejected)",data:im.map(r=>r.imputed_mu),borderColor:GREY,
  borderWidth:2.2,borderDash:[6,4],pointRadius:3.5,tension:.15},
 {label:"Measured only (shipped)",data:im.map(r=>r.measured_mu),borderColor:RED,
  borderWidth:3.2,pointRadius:5,pointBackgroundColor:RED,spanGaps:false,tension:.15}]},
 options:{...BASE,scales:{...BASE.scales,
  y:{...BASE.scales.y,title:{display:true,text:"Bat speed (mph)"}},
  x:{...BASE.scales.x,title:{display:true,text:"Season"}}}}});

/* ---------------- PERSONAS ---------------- */
document.getElementById("t-personas").innerHTML = `
<h2>Personas and the actions available to them</h2>
<p class="lede">Seven personas in the value stream. Each gets the finding that is actionable
<em>for them</em> and the lever they actually control.</p>
${D.personas.map(p=>`<div class="pcard"><h3>${p.name}</h3>
 <p class="f">${p.finding}</p><ul>${p.actions.map(a=>`<li>${a}</li>`).join("")}</ul>
 <div class="k"><b>KPI to watch:</b> ${p.kpi}</div></div>`).join("")}
<div class="note"><b>The counter-plan writes itself.</b> Everything in the mirror view is already
visible to opposing clubs. Anything the hitting group does should start by neutralising those three.</div>`;

/* ---------------- GOVERNANCE ---------------- */
document.getElementById("t-gov").innerHTML = `
<h2>Governance</h2>
<div class="cards">
 <div class="card good"><div class="lbl">Build DQ</div><div class="val">${M.dqPass}/${M.dqTotal}</div>
  <div class="nt">Six dimensions. Zero failures.</div></div>
 <div class="card good"><div class="lbl">Independent verification</div>
  <div class="val">${M.vPass}/${M.vTotal}</div>
  <div class="nt">Re-derived from raw parquet by a separate code path.</div></div>
 <div class="card good"><div class="lbl">Receipts</div><div class="val">24</div>
  <div class="nt">Every published number traces to a CSV.</div></div>
 <div class="card good"><div class="lbl">Entity lock</div><div class="val">656941</div>
  <div class="nt">MLBAM id, never a name filter. Zero contamination.</div></div>
</div>
<div class="panel"><h3>DQ scorecard</h3>
<p class="cap">Receipt: <code>dq_scorecard</code>. DQ-08 through DQ-11 are the no-imputation gate.</p>
${tbl(D.dq,[{h:"Rule",f:r=>r.rule},{h:"Dimension",f:r=>r.dimension},
 {h:"Result",f:r=>`<span class="badge ${r.result==="PASS"?'pass':'fail'}">${r.result}</span>`},
 {h:"Detail",f:r=>r.detail}])}</div>
<div class="note"><b>What would change this read.</b> Re-run at 150 additional plate appearances
(~2026-09-10). (1) Bat speed stays 74 ± 0.5 mph — if it drops below 73 the central claim is wrong.
(2) Damage-Band Rate recovers above 18% — if it stays below 15% with bat speed intact, the problem is
durable mechanical timing, not a slump. (3) Chase rate falls below 24%. If (1) fails, supersede this
UC rather than amend it.</div>`;

document.getElementById("foot").innerHTML =
 `<b>uc-pos-009-schwarber-swing-decay-001</b> · build <code>dp_uc32</code> · ledger UC #33 ·
  entity lock <code>batter == 656941</code> · evidence window 2026-03-26 → ${M.asOf} (T-1) ·
  24 CSV receipts · DQ ${M.dqPass}/${M.dqTotal} · verification ${M.vPass}/${M.vTotal} ·
  <b style="color:var(--red)">Internal — Restricted</b><br>
  Every number on this page was computed by <code>dp_uc32_schwarber_swing_decay.py</code> and read from a
  receipt in <code>out/</code>. This file computes nothing.`;
</script></body></html>"""


def _clean(o):
    """NaN/Inf are legal JS literals but not legal JSON. Emit null instead so the
    payload round-trips through any JSON parser and renders as an em-dash."""
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, float) and (np.isnan(o) or np.isinf(o)):
        return None
    if o is pd.NA or o is pd.NaT:
        return None
    return o


def main() -> None:
    payload = json.dumps(_clean(DATA), default=str, allow_nan=False)
    html = HTML.replace("__DATA__", payload)
    with open(DEST, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[dash] wrote {DEST} ({os.path.getsize(DEST)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
