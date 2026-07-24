"""One-page persona action card (PDF) for uc-pps-021 (dp_uc25).
Landscape Letter, 4 persona columns (Nola / Catcher / Manager / Coach-Analyst),
each action traced to an indicator. Headline numbers pulled from receipts.
Usage: python dp_uc25_build_persona_card.py [MLB_ROOT]"""
import sys, pathlib
import pandas as pd
from weasyprint import HTML

MLB = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
OUT = MLB / "out"

tr = pd.read_csv(OUT / "dp_uc25_nola_season_trend.csv").set_index("game_year")
ps = pd.read_csv(OUT / "dp_uc25_process_by_stand_2026.csv").set_index("stand")
rc = pd.read_csv(OUT / "dp_uc25_recency_split.csv")
last3 = rc[rc.segment.str.startswith("last-3")].iloc[0]
r26 = tr.loc[2026]; L = ps.loc["L"]; R = ps.loc["R"]

kpis = [
    ("2026 wOBA", f"{r26.woba:.3f}", f"career worst · SLG {r26.slg:.3f} · HR {r26.hr_rate:.1%}"),
    ("vs-LHB walk rate", f"{L.bb_rate:.1%}", f"the leak · only {R.bb_rate:.1%} vs RHB"),
    ("xwOBAcon L / R", f"{L.xwobacon:.3f} / {R.xwobacon:.3f}", "contact identical by side"),
    ("last 3 starts", f"{last3.woba:.3f}", "7/05 KC: 7 IP · 0 BB · 0 HR · 7 K"),
]

def col(title, tag, items):
    lis = "".join(f"<li><b>{a}</b><br><span class='ev'>{b}</span></li>" for a, b in items)
    return f"<div class='p'><div class='ph'>{title}<span>{tag}</span></div><ul>{lis}</ul></div>"

nola = col("Aaron Nola", "on the mound", [
    ("Throw strike one to the lefties.", "58.8% first-pitch strikes vs LHB vs 73.5% vs RHB — the 10.7% lefty walk rate starts right here."),
    ("Finish with the curve & change, not the heater.", "Knuckle curve 42.5% whiff, changeup 26.9% vs LHB; the 4-seam misses only 13.8% and gets lifted."),
    ("Keep the fastball down.", "Air-ball 59.7% and HR 5.1% are both career highs — every bit of the new damage is in the air.")])
catcher = col("Catcher — Realmuto / Marchan", "the sequence", [
    ("Two-strike target below the zone.", "Putaway to LHB just 18.6%; the finish pitch is never a 4-seam middle. Stubbs out — set the breaker down."),
    ("Feed the changeup to lefties.", "26.9% whiff, up from ~16% at UC8 — it is a real weapon now; pair it with the curve as the finish."),
    ("Pitch Betts & Ohtani backward.", "Betts .465 wOBA / 2 HR / 23 PA; Ohtani .450 xwOBAcon / 9 PA — the two bats with real danger signal.")])
mgr = col("Manager", "the call", [
    ("Hook by matchup, not pitch count.", "Leash ~95–100, but the trigger is the 3rd time through the lefty top — where June and the 7/16 (3 HR) damage clustered."),
    ("Have a lefty warm for the L-pocket.", "Five Dodgers stand left; the late-game lever is the Ohtani / Freeman / Muncy stretch."),
    ("Trust the profile on the no-book bats.", "Tucker & Pages are 8 PA each — plan on scouting, not on a tiny H2H line.")])
coach = col("Pitching coach / analyst", "the prep", [
    ("It isn't the zone — don't coach the ump.", "Edge rate .370 = career norm; the OOZ called-strike drop is a decade glide, not a 2026 ABS cliff."),
    ("It isn't the stuff — velo is flat.", "4-seam 92.3, no decline; K% steady 23.8%. This is command & shape, not arm strength."),
    ("Reinforce the change; watch the air ball.", "Changeup whiff 16%->27% vs LHB is the build-on; ground-ball rate a career-low 40.3% is the watch.")])

kpihtml = "".join(f"<div class='k'><div class='kv'>{v}</div><div class='kl'>{l}</div><div class='kd'>{d}</div></div>"
                  for l, v, d in kpis)

CSS = """
@page{size:Letter landscape;margin:1.0cm 1.1cm;}
body{font-family:-apple-system,'Segoe UI',Arial,sans-serif;color:#1a1a1a;margin:0;}
.hdr{border-bottom:3px solid #E81828;padding-bottom:6px;margin-bottom:9px;}
.hdr h1{color:#002D72;font-size:18pt;margin:0;} .hdr p{margin:2px 0 0;font-size:8.4pt;color:#55606e;}
.kstrip{display:flex;gap:9px;margin:9px 0 11px;}
.k{flex:1;background:#f5f6f8;border-top:3px solid #002D72;border-radius:6px;padding:6px 9px;}
.k:nth-child(2){border-top-color:#E81828;} .kv{font-size:14pt;font-weight:700;color:#002D72;} .k:nth-child(2) .kv{color:#E81828;}
.kl{font-size:7.6pt;color:#55606e;text-transform:uppercase;letter-spacing:.3px;} .kd{font-size:7.8pt;margin-top:1px;}
.cols{display:flex;gap:9px;} .p{flex:1;border:1px solid #e6e8ec;border-radius:7px;overflow:hidden;}
.ph{background:#002D72;color:#fff;padding:6px 9px;font-size:10.5pt;font-weight:700;display:flex;justify-content:space-between;align-items:baseline;}
.ph span{font-size:7pt;font-weight:400;opacity:.85;text-transform:uppercase;letter-spacing:.4px;}
ul{list-style:none;margin:0;padding:8px 10px;} li{margin:0 0 8px;font-size:8.8pt;line-height:1.3;}
li b{color:#002D72;} .ev{font-size:7.8pt;color:#55606e;}
.foot{margin-top:9px;font-size:7.4pt;color:#8C8C8C;text-align:center;border-top:1px solid #D9D9D9;padding-top:5px;}
"""
body = f"""
<div class='hdr'><h1>Aaron Nola vs the Dodgers — What Each Person Can Do</h1>
<p>dp_uc25 · uc-pps-021 · CBP · 2026-07-22 · fresh through his last start 7/16. The line is down (.358 wOBA, career worst), but the stuff and velo are fine — it's a lefty free-pass and air-ball problem, both self-correctable. Each action traces to an indicator; small H2H samples flagged in the full report.</p></div>
<div class='kstrip'>{kpihtml}</div>
<div class='cols'>{nola}{catcher}{mgr}{coach}</div>
<div class='foot'>Matchup scope = 7 named hitters, not a posted lineup — confirm the card before first pitch. Full report + governance: dp_uc25_nola_vs_dodgers_report.pdf · verification dp_uc25_verification.py · public Statcast data, entity-locked pitcher==605400.</div>
"""
out = MLB / "dp_uc25_nola_vs_dodgers_persona_card.pdf"
HTML(string=f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>").write_pdf(str(out))
print("wrote", out, out.stat().st_size, "bytes")
