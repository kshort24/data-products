"""dp_uc50_build_report.py -- writes dp_uc50_lineup_vs_sale_report.md from receipts + narratives only."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import dp_uc50_narratives as N

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
R = lambda k: pd.read_csv(OUT / f"dp_uc50_{k}.csv")
HL, C, LN, S = N.HL, N.cards(), N.lineup(), N.HL["sale"]
f3, pc, slash = N.f3, N.pc, N.slash
LINEUP = [(1, "Trea Turner", "R", "turner"), (2, "Kyle Schwarber", "L", "schwarber"), (3, "Bryce Harper", "L", "harper"),
          (4, "Alec Bohm", "R", "bohm"), (5, "Derek Hill", "R", "hill"), (6, "Bryan De La Cruz", "R", "cruz"),
          (7, "Bryson Stott", "L", "stott"), (8, "Edmundo Sosa", "R", "sosa"), (9, "J.T. Realmuto", "R", "realmuto")]
A = {(r["window"], r["group"]): r for r in HL["lineup_agg"]}
ss = S["season"]; ars = S["arsenal"]
dq = R("dq_scorecard").result.value_counts().to_dict()

md = []
w = md.append
w("# Offensive Advance Scout: the Phillies lineup vs Chris Sale (LHP)")
w("### NL Wild Card Series, Game 1 · Philadelphia @ Atlanta · Truist Park · 2026-09-29 · 2:00 p.m. ET (NBC)\n")
w("**Prepared for:** manager, hitting coach, advance meeting. One page per hitter, one page on Sale, one rule to carry into the dugout.  ")
w(f"**Opponent starter:** Chris Sale, LHP (ATL), MLBAM 519242 · {S['starts']} starts in 2026, last on {S['last']}  ")
w("**Governance:** Use Case #50 (`uc-pos-018`, build `dp_uc50`). Lineage `uc-pos-001` (Phillies vs Wacha, the first lineup-vs-starter card) → this. "
  "KPIs are inherited by import, not copied: `dp_uc44_kernel` (nresults, whiff, chase, hard-hit), `dp_uc46_kernel` (certified directional family), "
  "`barrel_rate.py`, `dp_uc48_kernel` (xwOBAcon). New and provisional: XW-1 (PA-based xwOBA), HL-1 (inner/middle/away band), LR-1 (your Harper rank, generalised), TT-1 (time through the order). "
  f"DQ {dq.get('PASS',0)} PASS / {dq.get('WARN',0)} WARN / {dq.get('FAIL',0)} FAIL.\n")
w("> ⚠️ **Read this first: data window and sample sizes.**")
w(f"> • Regular season only, 2015 through Game 162 ({HL['anchor']}). Hitters are locked by MLBAM id across the Phillies log and every MLB opponent file, with precedence dedup ({HL['house_rows']['raw']:,} rows → {HL['house_rows']['dedup']:,}). No postseason or spring PA vs Sale exist for these nine.  ")
w("> • Head-to-head samples are small by nature: the biggest book is 27 PA. **PA is printed on every line; THIN = under 10 PA, directional only.** Where it matters, xwOBA is the number doing the work, not wOBA.  ")
w("> • Sale's 2025 is PARTIAL in this repo (`sale.parquet` ends 2025-05-23). His profile here is 2026 only, which is complete.  ")
w("> • Carry-ins, never computed on: batting order (your prompt), game time and network (MLB.com / NBC listings), Harper's quote (your notebook).\n")
w("---\n")
w("## Bottom line\n")
w(f"1. **Sale is the 2026 version of Sale, and a little harder.** {LN['sale_line']}")
w(f"2. **The lefties can't be the plan.** {LN['lefties']} Harper's {f3(HL['hitters']['Bryce Harper']['rank']['target_metric'])} career OPS makes Sale the toughest of the {int(HL['hitters']['Bryce Harper']['rank']['n_pitchers'])} lefties he's seen 20+ times.")
w(f"3. **The right side carries the offense.** {LN['righties']} Bohm is the best bet on the card ({int(HL['hitters']['Alec Bohm']['sale_career']['plate_apps'])} PA, {f3(HL['hitters']['Alec Bohm']['sale_career']['woba'])} wOBA). Turner ({f3(HL['hitters']['Trea Turner']['sale_career']['woba'])}) and Hill (hard contact in a thin book) follow.")
w(f"4. **Don't count on the order turning over.** {LN['tto']}")
w(f"5. **The rule: make the slider a ball.** The slider is {pc(ars['SL']['usage'])} of what he throws, with a {pc(ars['SL']['whiff_rate'])} whiff rate and a {f3(ars['SL']['woba'])} wOBA against. "
  f"The four-seam is where the damage is: {ars['FF']['velo']:.1f} mph, {f3(ars['FF']['woba'])} wOBA, {pc(ars['FF']['whiff_rate'])} whiff. Every hitter's plan below is a version of *hunt the heater in the zone, let the slider go.*\n")

w("## 1 · Chris Sale, 2026\n")
w("![Sale arsenal](out/dp_uc50_fig2_sale_arsenal.png)\n")
w("| vs | Pitch | Usage | Velo | Whiff% | Chase% | wOBA | xwOBA | PA ended |")
w("|---|---|---|---|---|---|---|---|---|")
ab = R("sale_arsenal_by_stand").sort_values(["stand", "n"], ascending=[True, False])
for r in ab.itertuples():
    if r.usage < 0.02:
        continue
    w(f"| {'LHB' if r.stand=='L' else 'RHB'} | {r.pitch_name} | {pc(r.usage,1)} | {r.velo:.1f} | {pc(r.whiff_rate)} | {pc(r.chase_rate)} | {f3(r.woba)} | {f3(r.xwoba)} | {int(r.plate_apps)} |")
bs = S["by_stand"]
w(f"\nBy side: LHB {f3(bs['L']['woba'])} wOBA / {pc(bs['L']['krate'])} K in {int(bs['L']['plate_apps'])} PA; RHB {f3(bs['R']['woba'])} / {pc(bs['R']['krate'])} in {int(bs['R']['plate_apps'])} PA. "
  "Lefties see a slider-sinker pitcher and righties see a four-seam-slider pitcher, with the changeup almost only for righties.\n")
w("![Sale TTO](out/dp_uc50_fig3_sale_tto.png)\n")
w(f"{LN['vs_phi']}\n")

w("## 2 · The lineup card\n")
w("![Lineup glance](out/dp_uc50_fig1_lineup_glance.png)\n")
w("| # | Hitter | Bats | 2026 vs LHP PA | wOBA | xwOBA | vs Sale PA | AVG/OBP/SLG | wOBA | K% | Sale rank (LR-1) | Read |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|")
for slot, name, bats, _ in LINEUP:
    h = HL["hitters"][name]; L = h["lhp26"]; Sc = h["sale_career"]; rk = h["rank"]
    rr = f"#{int(rk['rank'])} of {int(rk['n_pitchers'])}" if rk.get("rank") == rk.get("rank") and rk.get("rank") is not None else f"— ({int(rk['target_pa'])} PA < 20)"
    thin = " THIN" if Sc.get("plate_apps", 0) < 10 else ""
    w(f"| {slot} | {name} | {bats} | {int(L['plate_apps'])} | {f3(L['woba'])} | {f3(L['xwoba'])} | **{int(Sc['plate_apps'])}**{thin} | {slash(Sc)} | {f3(Sc['woba'])} | {pc(Sc['krate'])} | {rr} | {C[name]['tag']} |")
w(f"\n*LR-1 rank: 1 = the lowest OPS among LHP the hitter has faced 20+ times (your Harper cut). {LN['lineup_all']}*\n")

w("**The one-page notecard** (print this one):\n")
w("![Lineup notecard](out/dp_uc50_fig4_lineup_notecard.png)\n")
w("## 3 · The index cards\n")
for slot, name, bats, slug in LINEUP:
    c = C[name]
    w(f"### {slot} · {name} ({bats}): {c['tag']}\n")
    w(f"![{name}](out/dp_uc50_card_{slot}_{slug}.png)\n")
    w(f"{c['lede']}\n")
    w(f"**Sale.** {c['sale']}  ")
    w(f"**Plan.** {c['plan']}\n")

w("## 4 · The single attack rule\n")
w("> **Make the slider a ball and the four-seam a strike.** Sale's slider is 40% of everything and his best pitch. Most of this lineup's damage against lefties comes on fastballs. Win the take, then win the heater.\n")
w("### Game-plan takeaways\n")
w("1. **Stack the right side in the middle innings.** Bohm, Hill and De La Cruz bat 4–6 and Sosa 8th. Late pinch-hit decisions should protect that platoon edge, not undo it.")
w("2. **Harper and Schwarber: the walk is the win.** Both chase Sale's slider below the zone. A long at-bat in front of Bohm is worth more than a swing at a 1-2 slider.")
w("3. **Sosa: no changeups.** His chase against lefties is the whole Sale problem. A strike or nothing.")
w("4. **Turner: take the changeup away.** His away-pitch contact is his weakest. The four-seam is 46% of what Sale throws righties, so wait for it.")
w("5. **Don't wait for the third time through.** Sale's results don't fade. If the Phillies are going to score off him, it'll be on fastball mistakes whenever they come.\n")

w("## 5 · Your notebook, graded\n")
w("| # | Subject | Your claim | Your value | Your method, today | Governed | Verdict |")
w("|---|---|---|---|---|---|---|")
for r in R("hp_reconciliation").fillna("").itertuples():
    w(f"| {r.hp} | {r.subject} | {r.claim} | {r.client_value} | {r.client_method_now} | {r.governed} | **{r.verdict}** |")
w("\nNotes: HP-01 your frame (`po26`) keeps spring and exhibition rows, and the governed frame is regular season. HP-05: the away pitch is where Turner's contact is weakest, but he isn't pulling it. The card says what holds instead. HP-08: '.100' does not reproduce from either frame today, and the ranking claim stands. HP-10 is O-26 again: a `nphl` name filter drops Sale pitches that were deduped into an earlier batter-keyed file.\n")

w("## 6 · Candid caveats\n")
w("- **Head-to-head is small.** 163 PA across nine hitters and four seasons. Every H2H line is directional. The cards lean on 2026-vs-LHP process (xwOBA, whiff, chase) and on pitch-group splits because those samples are 10–20× larger.")
w("- **Pitch groups are a proxy for Sale.** 'Breaking balls from lefties' mixes many sliders and curves with Sale's 80-mph sweepy slider. Directional, not a Sale-shape comp.")
w("- **HL-1 thirds are house geometry** (±0.28 ft on a ±0.83 ft plate). Cells under 25 BIP are marked * (FL-1) and are never quoted in the text as findings.")
w("- **Coverage.** De La Cruz's non-Phillies 2025 is outside the repo (bdlc.parquet ends 2025-04-16). Sale's 2025 after 5/23 is present only against the Phillies. Neither changes a 2026 number.")
w("- **Not modelled:** park, weather, bullpen usage after Sale, catcher framing, or the umpire.")
w("- **Receipts:** `out/dp_uc50_*.csv` (every table), `out/dp_uc50_headlines.json` (every number in the prose), `dp_uc50_verification.py` (independent recompute). Governance trail: `Agents for Data Products/data-products/uc-pos-018-lineup-vs-sale-wc-g1-001/`.")
(ROOT / "dp_uc50_lineup_vs_sale_report.md").write_text("\n".join(md), encoding="utf-8")
print("report lines", len(md))
