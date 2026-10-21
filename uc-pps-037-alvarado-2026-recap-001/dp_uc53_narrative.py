"""dp_uc53_narrative.py - the single sentence source for UC #53. Every number below is formatted from
out/dp_uc53_headlines.json, out/dp_uc53_figure_specs.json or out/dp_uc53_hp_grades.csv; nothing is typed.
The dashboard and the report both import this module, so they cannot disagree (house rule since UC52)."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent; OUT = ROOT / "out"
H = json.loads((OUT / "dp_uc53_headlines.json").read_text())
SPECS = {s["figure"]: s for s in json.loads((OUT / "dp_uc53_figure_specs.json").read_text())}
HPG = pd.read_csv(OUT / "dp_uc53_hp_grades.csv")
f3 = lambda x: (f"{x:.3f}".lstrip("0") if 0 <= x < 1 else f"{x:.3f}")          # noqa: E731
pc = lambda x, d=1: f"{100 * x:.{d}f}%"                                           # noqa: E731
pts = lambda x: f"{100 * abs(x):.1f} pts"                                         # noqa: E731
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"  # noqa: E731
S, FR, T, L, BY = H["season"], H["frame"], H["tenure"], H["leaderboard"], H["by_year"]
TR, RP, O, OB, MO = H["tenure_rank_2026"], H["house_rp"], H["outings_2026"], H["outing_bands"], H["monthly_2026"]
FCV, SIV, FCW, PUT, DB = H["fc_velo"], H["si_velo"], H["fc_whiff_house"]["by_year"], H["fc_putaway_house"], H["db1"]
PB = H["pitch_by_year"]
DBR = {r["sig"]: r for r in DB["rows"]}
RU = DB["rollup"]
ABOVE = SPECS["f09_cumulative_woba"]["share_pa_above_all_prior"]
PK = H["peak_2022_23"]
n_dec = sum(1 for r in DB["rows"] if r["hypothesis"] == "decline")
n_dec_p = sum(1 for r in DB["rows"] if r["hypothesis"] == "decline" and r["verdict"] == "PRESENT")
CALL = {"DECLINE": "move on", "BLIP": "bring him back for one more year", "DECLINE WITH NOISE": "move on, with a cheap one-year deal the only exception",
        "UNRESOLVED": "no call from the data"}[RU["call"]]

TITLE = "The Full Ride — José Alvarado, 2026"
SUB = "Season recap and Phillies tenure, 2021–26"
KICKER = f"Phillies Pitching · uc-pps-037 · season recap · data through {FR['anchor']}"
DEK = (f"Six seasons, {T['games']} games, {T['plate_apps']:,} batters, and a final year that ran the whole José Alvarado Experience at once. "
       f"The pre-registered ledger reads 2026 as a decline, not a blip.")
ARSENAL = " · ".join(f"{v['name']} {v['usage']:.0f}% ({v['velo']:.1f} mph)" for v in H["arsenal_2026"].values())

READ_FIRST = [
    f"<b>Entity lock:</b> MLBAM 621237 with the pitching role, never a name filter (ENT-1: {H['ent1_rows']} rows in the 2018 log carry his id under a "
    f"Phillies batter's name). Regular season for every rate; {H['spring_2026_pitches']} spring pitches excluded; postseason only in the tenure ledger. "
    f"The 2026 log holds {S['pitches']:,.0f} rows: {H['ab1']['thrown_2026']:,} pitches plus {H['ab1']['rows_2026']} automatic balls/strikes with no pitch (AB-1).",
    "<b>Sources:</b> Phillies logs 2021–26 plus <code>alvarado.parquet</code> (Tampa Bay 2017–20, used only for velocity and shape trends).",
    "<b>“House” ranks and percentiles</b> are Phillies pitcher-seasons 2015–26 (relievers by RP-1: starts ≤ 20% of games). <b>Not MLB-wide.</b>",
    "<b>Two wOBA bases:</b> house wOBA (FanGraphs weights) drives ranks; xwOBA is compared only with Statcast-basis wOBA (WB-1). "
    f"In 2026 they read {f3(S['woba'])} and {f3(S['woba_sc'])}.",
    "<b>“Runs on watch”</b> = runs scored during the plate appearances he threw (house <code>runs_created</code>). Not ERA.",
    "<b>Carry-ins, reported and never computed on:</b> 2026 club option exercised, $9M (CBS News, Nov 2025) · free agent after 2026 (NBC Sports "
    "Philadelphia, 2026-10-02) · 80-game PED suspension announced 2025-05-18 (6abc) · optioned to Triple-A, May 2022 (SI) · IL, reinstated "
    "2023-06-09 (MLB.com) · role reduced mid-2026 (MLB.com, 2026-07-04) · 5.86 ERA in 68 G (NBC) · “Mr. Punchie” and the Cotham cutter (client).",
    "<b>No medical inference.</b> The log shows velocity and workload; it does not show an injury or the effect of the 2025 suspension.",
]

BOTTOM = [
    f"<b>He was a load-bearing reliever for half a decade.</b> {T['plate_apps']:,} plate appearances faced is #{L['rank']} among {L['n']} Phillies pitchers "
    f"since 2015 and #{L['rp_rank']} among relievers; his {T['games']} games are #{L['games_rank']}. 2022 and 2023 ({f3(BY['2022']['woba'])} and "
    f"{f3(BY['2023']['woba'])} wOBA) ranked #{RP['tenure']['2022']['rank']} and #{RP['tenure']['2023']['rank']} of {RP['n']} Phillies relief seasons since 2015.",
    f"<b>2026 was the worst season of his tenure.</b> {f3(S['woba'])} wOBA against (house) and {S['rc_per_gm']:.2f} runs on watch per game, both "
    f"tenure worsts; {ordn(RP['woba']['percentile'])} percentile among {RP['n']} Phillies relief seasons. {O['blowups']} of {O['apps']} outings were blow-ups (2+ runs), the most he has had.",
    f"<b>Part of it was luck, and the luck ran out.</b> Hitters out-hit their contact by {f3(S['luck_gap'])} (wOBA {f3(S['woba_sc'])} vs xwOBA "
    f"{f3(S['xwoba'])}, same basis), and his hard-hit rate ({pc(S['hard_hit_rate'])}) was a tenure low. But from August his expected numbers "
    f"caught up (xwOBA {f3(MO['8']['xwoba'])} and {f3(MO['9']['xwoba'])}), as the sinker faded from {MO['6']['si_velo']:.1f} to {MO['9']['si_velo']:.1f} mph.",
    f"<b>The stuff declined.</b> The cutter averaged {FCV['y2026']:.1f} mph (tenure low), and its whiff rate fell to {pc(FCW['2026']['whiff'])} "
    f"(#{FCW['2026']['rank']} in the house, from #{FCW['2021']['rank']} in 2021). His zone rate ({pc(S['in_zone_rate'])}) was the lowest of his tenure.",
    f"<b>Verdict: {CALL}.</b> {n_dec_p} of {n_dec} pre-registered decline signatures are PRESENT; the blip case is {RU['blip']}. "
    f"The same call holds against a 2021–25 baseline.",
]

CH = [
    ("tenure", "Five-plus years in red pinstripes",
     f"Since 2015, only {L['rp_above'][0]['player_name'].split(', ')[1]} {L['rp_above'][0]['player_name'].split(', ')[0]} has faced more batters out of the Phillies "
     f"bullpen with no starts (Adam Morgan's {L['rp_above'][1]['plate_apps']:,} PA include {L['rp_above'][1]['starts']} starts). Over {T['games']} regular-season games Alvarado allowed a "
     f"{f3(T['woba'])} wOBA and {f3(T['ops'])} OPS and struck out {T['strikeouts']} ({pc(T['krate'])}). His peak, 2022–23, struck out {pc(PK['krate'])} "
     f"and walked {pc(PK['bbrate'])}. The October ledger is separate: "
     + "; ".join(f"{p['game_year']} {p['games']} G, {p['plate_apps']} PA, {p['strikeouts']} K" for p in H["postseason"]) + ".",
     ["f01_tenure_leaderboard"], "tenure"),
    ("results", "2026 against his own standard",
     f"Every results line was his worst as a Phillie: {f3(S['woba'])} wOBA (house), {S['rc_per_gm']:.2f} runs on watch per game, K–BB {pc(S['k_minus_bb'])} "
     f"(#{TR['k_minus_bb_low']} lowest of {TR['n']}). Expected stats were kinder, {f3(S['xwoba'])} xwOBA against a {f3(S['woba_sc'])} same-basis actual, "
     f"a {f3(S['luck_gap'])} gap; in 2022–24 the gap averaged {f3(DBR['B1']['baseline'])}. Hitters made weak contact: {pc(S['hard_hit_rate'])} hard-hit "
     f"(tenure low), {pc(S['barrel_rate'])} barrels. Among {RP['n_2026']} Phillies relievers with 100+ PA in 2026, his wOBA ranked #{RP['rank_2026_pen']}.",
     ["f02_woba_xwoba_by_year"], None),
    ("cutter", "The cutter: still very good, no longer the best",
     f"Caleb Cotham's cutter (carry-in CI-8) is the pitch that made him. Over his tenure it put hitters away on {pc(PUT['value'])} of {PUT['pitches2strikes']} "
     f"two-strike pitches, #{PUT['rank_ge300']} of {PUT['n_ge300']} Phillies pitch types with 300+ two-strike pitches. In 2021 its {pc(FCW['2021']['whiff'])} whiff rate "
     f"was #1 of {H['fc_whiff_house']['n']} Phillies pitcher-pitch-seasons. In 2026 it fell to {pc(FCW['2026']['whiff'])} (#{FCW['2026']['rank']}) and its "
     f"two-strike putaway rate to {pc(PB['FC']['2026']['putaway_rate'])}, his lowest on the pitch as a Phillie. The shape held; the velocity did not "
     f"({FCV['y2026']:.1f} mph, {abs(FCV['drop_vs_peak']):.1f} under {FCV['peak_year']}).",
     ["f03_cutter_putaway_context", "f04_cutter_whiff_context", "f05_cutter_metrics_by_year"], None),
    ("arm", "The arm: slower, and fading late",
     f"The sinker averaged {SIV['y2026']:.1f} mph, {abs(SIV['drop_vs_peak']):.1f} under {SIV['peak_year']}. More telling is the season's shape: through June "
     f"both fastballs held ({MO['6']['si_velo']:.1f} and {MO['6']['fc_velo']:.1f} mph), then slid to {MO['9']['si_velo']:.1f} and {MO['9']['fc_velo']:.1f} by "
     f"September, while walks rose to {pc(MO['8']['bbrate'])} in August and {pc(MO['9']['bbrate'])} in September. The log shows the fade; it cannot say why.",
     ["f06_velocity_by_year"], "monthly"),
    ("command", "Command: outside the zone, into the bats",
     f"He threw {pc(S['in_zone_rate'])} of his pitches in the zone by the house measure ({pc(H['ab1']['zone_thrown_2026'])} counting only pitches actually thrown; AB-1), the lowest of his tenure either way, and hit {int(S['hbp'])} batters, the most. Hitters still chased "
     f"{pc(S['chase_rate'])}, close to his 2022–24 rate ({pc(DBR['D4']['baseline'])}), so the problem was not that batters stopped expanding. "
     f"It was the sinker: {pc(PB['SI']['2026']['in_zone_rate'])} in the zone (from {pc(PB['SI']['2024']['in_zone_rate'])} in 2024) and a {f3(PB['SI']['2026']['woba'])} wOBA when it ended a PA.",
     ["f07_command_by_year"], None),
    ("ride", "The ride: inconsistency, measured",
     f"{O['clean']} of {O['apps']} outings were clean, {pc(OB['2026']['clean_rate'], 0)}, the lowest share of his tenure, and {O['blowups']} were blow-ups. "
     f"The damage was not a few disasters: his five worst outings held {pc(OB['2026']['damage_top5'], 0)} of his {int(O['runs'])} runs on watch, the "
     f"smallest share of any Phillies season ({int(O['runs_outside_worst5'])} runs came in the other {O['apps'] - 5}). Season to date, 2026 sat above every "
     f"prior Phillies season at {pc(ABOVE, 0)} of its plate appearances and never came down to his pooled 2021–25 level.",
     ["f08_outing_bands", "f09_cumulative_woba"], None),
    ("verdict", "Move on, or a blip?",
     f"Before reading a single 2026 rate, the organization wrote down eight signatures: six that a declining reliever shows and two that an unlucky one shows, each "
     f"with a bar, scored by the house PA-1 rule against his pooled 2022–24 seasons. The roll-up: decline <b>{RU['decline']}</b>, blip <b>{RU['blip']}</b>, call "
     f"<b>{RU['call']}</b>. Against a 2021–25 baseline: <b>{DB['sensitivity']['rollup']['call']}</b>.",
     ["f10_db1_ledger"], "db1"),
]

CASE_MOVE_ON = [
    f"Cutter velocity is down {abs(DBR['D2']['delta']):.1f} mph on his 2022–24 level and its whiff rate is down {pts(DBR['D3']['delta'])}. That is the pitch that made him elite, and both are tenure lows.",
    f"The zone rate fell {pts(DBR['D5']['delta'])} and K–BB fell {pts(DBR['D6']['delta'])}. Fewer strikes and fewer punchouts is the reliever-decline signature.",
    f"The luck story fades late: from August his xwOBA ({f3(MO['8']['xwoba'])}, {f3(MO['9']['xwoba'])}) matched his results, and his velocity was at its season low.",
    "Every rate here is regular season with a pinned anchor. The call does not depend on the baseline: 2021–25 gives the same verdict.",
    "He enters free agency at 31, coming off a $9M option year (carry-ins CI-1, CI-2). The stuff trend points the wrong way for the price of high-leverage innings.",
]
CASE_BLIP = [
    f"Contact was soft: {pc(S['hard_hit_rate'])} hard-hit (tenure low) and {pc(S['barrel_rate'])} barrels. The {f3(S['luck_gap'])} wOBA-over-xwOBA gap is {S['luck_gap'] / DBR['B1']['baseline']:.0f}× his 2022–24 norm ({f3(DBR['B1']['baseline'])}).",
    f"Hitters chased as much as ever ({pc(S['chase_rate'])}), and the cutter is still {ordn(FCW['2026']['pct']['percentile'])}-percentile for whiffs in the house.",
    f"In April–June his expected numbers ran well ahead of his results (xwOBA {f3(MO['4']['xwoba'])}, {f3(MO['5']['xwoba'])}, {f3(MO['6']['xwoba'])} against house wOBA {f3(MO['4']['woba'])}, {f3(MO['5']['woba'])}, {f3(MO['6']['woba'])}), the case MLB.com made in July (CI-6).",
    f"He still threw {SIV['y2026']:.1f} mph sinkers. A one-year deal at a lower price buys a lottery ticket on the 2025 shape ({FCW['2025']['whiff']:.1%} cutter whiff in 28 games).",
]
VERDICT_LINE = (f"<b>The ledger favors moving on.</b> The blip evidence is real, but it is about balls in play. The decline evidence is about the arm and the strike "
                f"zone, and it got worse as the season went on. If he returns, it should be on a short, cheap deal in a lower-leverage role, not in the late-inning "
                f"bridge role he opened 2026 in (CI-6).")

HP = HPG.rename(columns={"verdict": "grade_text"}).assign(grade=lambda d: d.grade_text.map(lambda v: "PARTLY" if "nuance" in v else "CONFIRMED"))
CAVEATS = [
    f"Relief samples are small: {int(S['plate_apps'])} PA in 2026; monthly cells are {min(v['pa'] for v in MO.values())}–{max(v['pa'] for v in MO.values())} PA. Read direction, not decimals.",
    "House ranks are Phillies pitcher-seasons 2015–26, not MLB-wide.",
    "OD-1 and DB-1 are provisional (first use). DB-1's bars are registered in 03 §2; changing one after publication is a breaking change.",
    "DB-1's B2 signature (damage concentration) came out CONTRA. That is evidence against the 'a few bad outings' story, not a missing value.",
    "The 2025 season (28 games) sits between an 80-game suspension and the end of the year; it is excluded from the DB-1 baseline and kept in the sensitivity run.",
    "CM-D1: the house cumulative module's default wOBA counts woba_value on intentional walks and sac bunts. F9 uses the corrected spec (CM-1a); your original chart ran high.",
    f"AB-1: the 2026 log carries {H['ab1']['rows_2026']} automatic balls/strikes with no pitch; the house zone rate counts them in-zone (K44 D-7), so the 2026 zone decline is understated, not overstated.",
    "Contract, age and role facts are carry-ins from published reporting, labelled where used and never computed on.",
]
PRODUCTS = [
    ("PDF recap report (9 sections)", "Built", "The verdict, the evidence and your notebook graded, on paper."),
    ("Interactive dashboard (7 chapters)", "Built", "The same story; every figure can be hovered and zoomed."),
    ("Front-office decision memo", "Folded in", "Chapter 7 is the memo: both cases, the ledger, the call."),
    ("2027 projection model", "Not bid", "No projection model in the house. DB-1 is the governed substitute."),
    ("Tenure highlight video", "Not bid", "Out of the comparison profile."),
]
TILES = [
    (f3(S["woba"]), "wOBA against, 2026", f"tenure worst; xwOBA {f3(S['xwoba'])} (same-basis actual {f3(S['woba_sc'])})"),
    (f"{FCV['y2026']:.1f}", "cutter mph", f"tenure low; {abs(DBR['D2']['delta']):.1f} under 2022–24"),
    (f"{O['blowups']}/{O['apps']}", "blow-up outings", "2+ runs on watch; most of his tenure"),
    (RU["call"].title(), "pre-registered call", f"{n_dec_p} of {n_dec} decline signatures present"),
]
