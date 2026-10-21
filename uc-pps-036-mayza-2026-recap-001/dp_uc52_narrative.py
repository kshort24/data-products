"""dp_uc52_narrative.py — every published sentence for UC #52, formatted from out/dp_uc52_headlines.json and
out/dp_uc52_hp_grades.csv. The report builder and the dashboard builder both import this; neither types a number."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

OUT = Path(__file__).resolve().parent / "out"
H = json.loads((OUT / "dp_uc52_headlines.json").read_text())
HP = pd.read_csv(OUT / "dp_uc52_hp_grades.csv")
SPECS = pd.read_csv(OUT / "dp_uc52_figure_specs.csv").set_index("figure").to_dict("index")

TITLE = "The Sheriff of the Phillies Bullpen"
SUB = "Tim Mayza's 2026 season recap"
f3 = lambda x: (f"{x:.3f}".lstrip("0") if abs(x) < 1 else f"{x:.3f}")          # noqa: E731
pc = lambda x, d=1: f"{100 * x:.{d}f}%"                                           # noqa: E731
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"  # noqa: E731
S, CR, CP, HL = H["season"], H["career_rank"], H["career_prior"], H["house_lhp_rp"]
PL, W, D, BS, Q, B, A, SH = H["platoon"], H["weapons"], H["delivery"], H["bullet_slider"], H["quick_ab"], H["barrel_context"], H["arsenal"], H["shapes"]
NS = CR["n_seasons"]
FR = H["frame"]
PS = H["postseason"][0] if H["postseason"] else None

# word-form claims are asserted against the receipts (harness family F re-checks them independently)
assert CR["woba_low"] == 3 and CR["ops_low"] == 3 and NS == 9, "DEK/BOTTOM say third-best of nine"
assert S["xwoba"] < S["woba_sc"] and PL["R"]["xwoba"] > PL["R"]["woba_sc"] and PL["L"]["xwoba"] < PL["L"]["woba_sc"], "same-basis luck claims"
assert CR["hh_high"] == 2, "BOTTOM says second only to his rookie year"
assert CR["quick_ab_high"] == NS, "BOTTOM says lowest of his career"
assert [r["player_name"].startswith("Alvarado") for r in HL["best_woba"][1:3]] == [True, True], "comps lede says Alvarado #2 and #3"
assert D["comps"][0]["player_name"].startswith("S") and D["comps"][0]["game_year"] == 2021, "Sánchez 2021 nearest"
assert W["SL_vs_R"]["plate_x"] < 0 and W["SL_vs_R"]["plate_z"] < 1.6, "slider vs RHB: low and in (3B side, catcher view)"
_pas = [W[k]["pa"] for k in ("SI_vs_L", "SI_vs_R", "SL_vs_L", "SL_vs_R")]
assert (min(_pas), max(_pas)) == (35, 81), "weapons lede says 35 to 81 PA"
assert (min(PL["L"]["plate_apps"], PL["R"]["plate_apps"]) >= 35 and max(PL["L"]["plate_apps"], PL["R"]["plate_apps"]) == 156)

KICKER = f"Pitching · uc-pps-036 · season recap · data through {FR['anchor']}"
DEK = (f"Mayza threw strikes and kept runners off. His {f3(S['woba'])} wOBA allowed was the third-best of his nine seasons, and luck "
       f"did not carry it: on Statcast's basis he allowed {f3(S['woba_sc'])} against a {f3(S['xwoba'])} expectation. "
       f"The warning sign is louder contact, mostly from right-handed hitters.")
ARSENAL = " · ".join(f"{v['name']} {pc(v['usage'], 0)}" for v in A.values())

TILES = [
    (f3(S["woba"]), "wOBA allowed", f"{ordn(CR['woba_low'])}-best of his {NS} seasons"),
    (f3(S["xwoba"]), "xwOBA allowed", f"vs {f3(S['woba_sc'])} actual on the same basis: no luck premium"),
    (pc(S["bbrate"]), "Walk rate", f"#{HL['bbrate']['rank']} of {HL['n']} Phillies LHP relief seasons"),
    (pc(Q["rate"]), "Quick-AB rate", f"{ordn(Q['house']['percentile'])} percentile of Phillies pitcher-seasons"),
]

READ_FIRST = [
    f"<b>Entity lock:</b> MLBAM 641835 (Tim Mayza, LHP), never a name filter. Regular season only: {int(S['pitches']):,} pitches, "
    f"{int(S['plate_apps'])} PA, {int(S['games'])} games, {FR['first']} to {FR['last']}.",
    "<b>Sources:</b> Phillies Statcast logs (2025-26) and his own pitcher file (Toronto, New York, Pittsburgh, 2017-25), de-duplicated by pitch key. No 2020 rows.",
    (f"<b>Two wOBA bases.</b> House wOBA ({f3(S['woba'])}: FanGraphs weights over every PA, errors count as outs) is used for ranks. "
     f"xwOBA is only ever compared with Statcast-basis wOBA ({f3(S['woba_sc'])}: Statcast's own weights and denominator)."),
    "<b>House ranks</b> compare Phillies pitcher-seasons from 2015 to 2026. They are not MLB-wide.",
    "<b>Runs on watch</b> = runs that scored during the plate appearances he pitched. It is not ERA.",
    (f"<b>Postseason</b> stays in its own ledger: {PS['pitches']} pitches, {PS['plate_apps']} PA on {PS['game_date']}, no runs on watch."
     if PS else "<b>Postseason:</b> none."),
    "<b>Carry-ins, never computed on:</b> claimed off waivers from Pittsburgh on 2025-08-31 (MLB Trade Rumors); later re-signed to a "
    "major-league deal (MLBTR headline; date not verified); his 2027 status is not verified. \"The Sheriff\" and #37 are from the client.",
]

BOTTOM = [
    (f"<b>The results were real.</b> {f3(S['woba'])} wOBA and {f3(S['ops'])} OPS allowed, both {ordn(CR['woba_low'])}-best of his {NS} seasons. "
     f"His xwOBA of {f3(S['xwoba'])} sits below the {f3(S['woba_sc'])} he allowed on the same Statcast basis, so he did not need luck. Among {HL['n']} Phillies LHP relief seasons "
     f"since 2015 (100+ PA) he ranks #{HL['woba']['rank']} in wOBA; the median is {f3(HL['median_woba'])}."),
    (f"<b>He avoided traffic by throwing strikes, not by finishing faster.</b> Walk rate {pc(S['bbrate'])} "
     f"(#{HL['bbrate']['rank']} of {HL['n']} Phillies LHP relief seasons), OBP allowed {f3(S['obp'])}. His quick-AB rate of {pc(Q['rate'])} "
     f"beat the house median ({pc(Q['house_median'])}) but was the lowest of his career, by a hair."),
    (f"<b>The contact is the risk.</b> Hard-hit rate {pc(S['hard_hit_rate'])}, second only to his rookie year. Right-handed hitters "
     f"barrelled {pc(PL['R']['barrel_rate'])} of balls and carried a {f3(PL['R']['xwoba'])} xwOBA, above the {f3(PL['R']['woba_sc'])} they produced on the same basis."),
    (f"<b>The delivery is the story.</b> A high, tight slot and {D['ext']:.2f} ft of extension ({ordn(D['ext_pct']['pct_below'])} percentile "
     f"of Phillies LHP seasons) sell a sinker that runs less than most and a {BS['velo']:.1f} mph bullet slider. "
     f"His nearest delivery comps are Cristopher Sánchez (2021) and José Alvarado (2026)."),
]

CH = [  # (anchor, title, lede, [figure keys], extra_table_key)
    ("results", "Results: his third-best season",
     f"He allowed a {f3(S['woba'])} wOBA over {int(S['plate_apps'])} PA. K% {pc(S['krate'])}, BB% {pc(S['bbrate'])} and HR% {pc(S['hr_rate'])} all "
     f"sit inside his own career range. {int(S['runs_created'])} runs scored on his watch across {int(S['games'])} games "
     f"({S['rc_per_gm']:.2f} per game, #{HL['rc_per_gm']['rank']} of {HL['n']} Phillies LHP relief seasons).",
     ["f01_career_woba"], "house"),
    ("contact", "Contact: louder, but priced in",
     f"Batters hit the ball harder than in any season since 2017 and lifted it more (average launch angle {S['la_mu']:.1f}°). "
     f"Barrels stayed moderate ({pc(S['barrel_rate'])}, {ordn(CR['barrel_low'])}-lowest of {NS}). A barrel-only line through {B['n']} Phillies LHP "
     f"seasons expects {f3(B['woba_fit'])} on the house basis, and he allowed {f3(S['woba'])}. xwOBA, which also counts his strikeouts and walks, "
     f"expects {f3(S['xwoba'])} against the {f3(S['woba_sc'])} he allowed on Statcast's basis. Either way, the results were not borrowed.",
     ["f02_contact_by_year", "f03_barrel_woba_house"], None),
    ("platoon", "Platoon: lefties are his, righties are the risk",
     f"Lefties managed a {f3(PL['L']['woba'])} wOBA with a {pc(PL['L']['barrel_rate'])} barrel rate, and their contact deserved even less "
     f"({f3(PL['L']['xwoba'])} expected against {f3(PL['L']['woba_sc'])} actual on Statcast's basis). "
     f"Righties struck out more ({pc(PL['R']['krate'])}) and walked more ({pc(PL['R']['bbrate'])}), but they also barrelled {pc(PL['R']['barrel_rate'])} and "
     f"hit {pc(PL['R']['hard_hit_rate'], 0)} of balls hard. Their {f3(PL['R']['xwoba'])} xwOBA is higher than the {f3(PL['R']['woba_sc'])} they produced on the same basis.",
     ["f04_pitch_map"], "platoon"),
    ("stuff", "Stuff and delivery: higher, tighter, longer",
     f"Arsenal: {ARSENAL}. The four-seam has {A['FF']['ivb_in']:.1f} in of ride ({ordn(SH['FF']['ivb_pct_below'])} percentile of Phillies LHP four-seamers). "
     f"The sinker runs {A['SI']['hb_in']:.1f} in, less than {100 - SH['SI']['absHB_pct_below']}% of house LHP sinkers. Released {D['rel_z']:.2f} ft high "
     f"({ordn(D['rel_z_pct']['pct_below'])} percentile) and {D['rel_x']:.2f} ft wide ({ordn(D['rel_x_pct']['pct_below'])} percentile, narrower than most), "
     f"with {D['ext']:.2f} ft of extension. Arm angle {D['arm_angle_2026']:.0f}° (tracked on {pc(D['arm_angle_cov'], 0)} of 2026 pitches). "
     "Mound position is not in Statcast, so the data cannot separate slot from rubber position.",
     ["f05_arsenal_movement", "f06_release_extension"], None),
    ("slider", "The bullet slider",
     f"His slider averages {BS['velo']:.1f} mph with {abs(BS['hb_in']):.1f} in of horizontal and {abs(BS['ivb_in']):.1f} in of vertical break, which makes it a bullet "
     f"(BS-1: both under 4 in). That is uncommon, not unique: {BS['n_bullet_others']} of {BS['n_pop']} other Phillies LHP slider seasons qualify, "
     f"most of them Cristopher Sánchez's. Mayza's is among the hardest ({ordn(SH['SL']['velo_pct_below'])} percentile for velocity).",
     ["f07_slider_shapes"], None),
    ("weapons", "Weapons by side",
     f"Against lefties the sinker did the work: {pc(W['SI_vs_L']['usage'], 0)} usage, {f3(W['SI_vs_L']['woba'])} wOBA on PAs it ended. "
     f"Against righties the slider did: {pc(W['SL_vs_R']['whiff'], 0)} whiffs and a {f3(W['SL_vs_R']['woba'])} wOBA, thrown low and in on their back foot. "
     f"The slider to lefties was the soft spot ({pc(W['SL_vs_L']['whiff'], 0)} whiffs, {f3(W['SL_vs_L']['woba'])} wOBA). These cells hold 35 to 81 PA each.",
     ["f08_weapons"], None),
    ("quick", "The Mayza Success Rate, revisited",
     f"QA-1 counts a plate appearance as a win when he reaches two strikes, or gets a ground ball, within the first three pitches. "
     f"In 2026 that happened in {pc(Q['rate'])} of {Q['pas']} PA ({pc(Q['two_k'])} reached two strikes, {pc(Q['gb'])} ended on an early grounder). "
     f"The notebook version returned about 40% because it read the count before each pitch, so it only credited two strikes within two pitches. "
     f"Both are reported; the notebook's figure is graded in the appendix.",
     ["f09_quick_ab_rate"], None),
    ("comps", "Who throws like him?",
     f"DS-1 measures distance across release side and height, extension, and primary-fastball velocity, run and ride over {D['n_pop']} Phillies LHP seasons. "
     f"The nearest is Cristopher Sánchez's 2021. José Alvarado's 2026 ranks "
     f"#{D['alvarado']['rank']}, so 'Alvarado lite' holds for the delivery. It does not hold for the results: Alvarado's 2022 and 2023 rank "
     f"#2 and #3 in the house relief wOBA table, and Mayza's 2026 ranks #{HL['woba']['rank']}.",
     ["f10_comps"], None),
]

CAVEATS = [
    f"Relief samples are small: {int(S['plate_apps'])} PA for the season and 35 to 156 PA in each split. Read direction, not decimals.",
    "House populations are Phillies pitchers only. A Phillies-relative rank is not an MLB rank.",
    f"Career seasons 2017 and 2025 are short (<400 pitches). 2025 combines Pittsburgh and his September with the Phillies.",
    "QA-1, BS-1 and DS-1 are new and provisional. Their thresholds were written down before any results were computed.",
    "The 2027 roster question is out of scope. His contract status is an unverified carry-in.",
]

PRODUCTS = [
    ("Recap report (PDF)", "Built", "The narrative and the graded notebook, nine sections."),
    ("Interactive dashboard", "Built", "Eight chapters with hover, the same receipts, light and dark."),
    ("One-page persona card", "Deferred", "Priced at ~35k tokens in the BID, not built."),
    ("2027 projection", "Not bid", "No house projection model, and his status is unverified."),
    ("Video clips", "Not bid", "Outside the comparison profile."),
]
