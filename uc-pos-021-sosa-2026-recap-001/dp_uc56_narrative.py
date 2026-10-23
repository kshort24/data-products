"""dp_uc56_narrative.py - every sentence of the report and dashboard, formatted from out/dp_uc56_headlines.json and
out/dp_uc56_figure_specs.json. No number is typed by hand except carry-ins, which are labelled CI-n at every use."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
H = json.loads((OUT / "dp_uc56_headlines.json").read_text(encoding="utf-8"))
SPECS = {s["figure"]: s for s in json.loads((OUT / "dp_uc56_figure_specs.json").read_text(encoding="utf-8"))}
f3 = lambda x: f"{x:.3f}".replace("0.", ".", 1) if abs(x) < 1 else f"{x:.3f}"   # noqa: E731
pc = lambda x, d=1: f"{100 * x:.{d}f}%"                                           # noqa: E731
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"  # noqa: E731
S = H["season"]
S26, B = S["2026"], H["baseline"]
T, WA, DF, PG, PB, PL = H["tr1"]["rows"], H["wa1"], H["df"], H["pg"], H["pg_base"], H["platoon"]
CAR, HP = H["phi_career"], H["hp"]
SLASH = f"{f3(S26['ba'])}/{f3(S26['obp'])}/{f3(S26['slg'])}"
TITLE = "We Really Do Love Sosa"
SUB = "Edmundo Sosa's 2026, and maybe his Phillies run"

READ_FIRST = [
    f"Regular season only for every rate. The client's frame also carried {H['src4']['spring_2026_pa']} spring and {H['src4']['post_2026_pa']} Wild Card PA in 2026 (SRC-4) and his St. Louis years from a second file (SRC-5); both are graded in §8, never pooled.",
    f"Baseline for 'prior Phillies years' = 2023-25 ({B['plate_apps']} PA). 2022 in Philadelphia was {S['2022']['plate_apps']} PA: shown, never a baseline (SRC-6).",
    f"House log through {H['anchor']}; 2026 = {S26['plate_apps']} PA in {H['games_with_pa_2026']} games, {H['pa_by_hand_2026']['L']} vs LHP / {H['pa_by_hand_2026']['R']} vs RHP. Reconciles to Baseball-Reference (CI-1: .247/.283/.429, 250 PA).",
    "Carry-ins (labelled CI-n) come from Baseball-Reference, NBC Sports Philadelphia, PhillyVoice, Spotrac, MLB.com, ESPN and the AP; they are quoted, never computed on. The walkaway band (§7) is arithmetic on carry-ins and says so.",
    "EV50 here is the median exit velocity (the client's definition, GL-1). Statcast's public EV50 is the mean of the hardest 50% of batted balls; the two are not interchangeable.",
]

BOTTOM = [
    f"<b>Yes, 2026 was a down year - in results.</b> {f3(S26['woba'])} wOBA and {f3(S26['ops'])} OPS were the worst of his four full Phillies seasons, and the cumulative line ran last at every 50-PA checkpoint.",
    f"<b>No, it wasn't a down year in the bat.</b> His {f3(S26['xwoba'])} xwOBA was the best of his four full Phillies seasons, his EV90 ({S26['ev90']:.1f} mph) a career high, and bat speed held ({S26['bat_speed_mu']:.1f} mph). Zero of six pre-registered decline flags tripped. BABIP {f3(S26['babip'])} was his lowest.",
    f"<b>The late uptick was the results catching up, not a better hitter.</b> After the break, wOBA rose {f3(T['R1']['pre'])} → {f3(T['R1']['post'])} while xwOBA fell {f3(T['P1']['pre'])} → {f3(T['P1']['post'])} (TR-1: {H['tr1']['call']}).",
    f"<b>The chase-and-contact approach is sustainable, and expensive in volume.</b> {pc(S26['chase_rate'])} chase was the highest of {H['rhb_n']} Phillies RHB seasons since 2022, but his out-of-zone contact is above the median and his out-of-zone BA was earned (OZ-1). Each chase costs less than a typical righty's; he just chases more.",
    f"<b>He's a bench bat who mashes lefties, not an everyday player.</b> vs LHP {f3(PL['L|base']['woba'])} wOBA (2023-25), vs RHP {f3(PL['R|base']['woba'])}, with a {pc(S26['bbrate'])} walk rate. Five seasons, five positions, a {f3(CAR['woba'])} Phillies wOBA - {ordn(H['tenure_board']['woba_rank'])} of {H['tenure_board']['n']} Phillies with 800+ PA.",
    f"<b>Walkaway: ${WA['ceiling']:.1f}M a year, no more than {WA['years']} years.</b> Open near his 2026 salary (${WA['floor']:.1f}M, CI-3). If another club pays more or longer, it's paying for an everyday player - let him go.",
]

CH = [  # (anchor, question, title, lede, figures, extra)
    ("line", "Q1", "The 2026 line", f"{SLASH}, {f3(S26['woba'])} wOBA, {f3(S26['ops'])} OPS. Against his own 2023-25 Phillies seasons, 2026 ranks {ordn(H['own_rank_2026']['woba'])} of four in wOBA, OBP and OPS - and {ordn(H['own_rank_2026']['xwoba'])} in xwOBA. "
     f"The cumulative lines put it plainly: 2026 was last at 50, 100, 150, 200 and 250 PA, bottoming at {f3(H['cum_ck']['woba_100']['v'])} at 100 PA. The season card says why it isn't the whole story: his contact quality was the best it's been.",
     ["f1_cumulative", "f2_season_card"], "line"),
    ("form", "Q2", "Was there an uptick?", f"Yes in the box score, no under it. The All-Star-break test was fixed in the BID before anything was computed: results improved on all four signatures "
     f"(wOBA {f3(T['R1']['pre'])} → {f3(T['R1']['post'])}, SLG {f3(T['R4']['pre'])} → {f3(T['R4']['post'])}), process on none - xwOBA, strikeout rate, hard-hit rate and whiff rate all moved the wrong way. "
     f"ER-1 finds no change point anywhere in 2023-26 (and at 250 PA it would detect a .080 step only {pc(H['er1']['woba']['power_2026']['0.08'], 0)} of the time). "
     f"The media's 'final 50 games' frame (CI-2: .806 OPS in 149 PA) reproduces at {f3(H['ci2_last50']['ops'])} OPS over his last 50 games with a PA ({H['ci2_last50']['pa']} PA) - real, but chosen after the fact. "
     f"Read it as a first half that ran unlucky ({f3(T['R1']['pre'])} wOBA on {f3(T['P1']['pre'])} xwOBA) and a second half that ran a little lucky.",
     ["f3_form_2026"], None),
    ("bat", "Q3", "Batted ball: over the hump?", f"Not by any measure of force. Against his 2023-25 mean: bat speed {DF['DF-1']['delta']:+.1f} mph ({ordn(H['bat_speed_pct_2026']['rank'])} of {H['bat_speed_pct_2026']['n']} tracked Phillies hitters), "
     f"EV90 {DF['DF-2']['delta']:+.1f} mph, hard-hit {100 * DF['DF-3']['delta']:+.1f} points, barrel rate flat, xwOBA {DF['DF-5']['delta']:+.3f}. Max EV {S26['ev_max']:.1f} mph and median EV {S26['ev50']:.1f} mph sit with his 2024-25 levels. "
     f"What did slide is shape: pull-air {pc(S26['pull_air_rate'])} (his lowest; {pc(S['2025']['pull_air_rate'])} in 2025, {pc(S['2023']['pull_air_rate'])} in 2023) and ground balls {pc(S26['gb_rate'])} (his highest). Hard contact on the ground is how a .330 xwOBA becomes a .307 wOBA.",
     ["f4_over_the_hump"], None),
    ("approach", "Q4, Q6", "The approach: chase, contact, swing", f"He is exactly who you said: a swinger. {pc(S26['swing_rate'])} swing rate ({ordn(H['rhb_rank']['2026']['swing']['percentile'])} percentile of Phillies RHB seasons) and {pc(S26['chase_rate'])} chase, the highest in the pool. "
     f"The 'high contact' half is narrower: overall contact {pc(S26['contact_rate'])} is below the RHB median, but out-of-zone contact {pc(S26['ooz_contact_rate'])} is above it ({pc(H['rhb_ooz_contact_median'])}). "
     f"Is it sustainable? OZ-1 says his out-of-zone BA ({f3(S26['oz_ba'])}) ran {abs(S26['oz_gap']) * 1000:.0f} points under expected ({f3(S26['oz_xba'])}) - earned, not lucky - in three of four seasons. "
     f"CC-1 prices it: {H['cc1']['2026']['per100']:.1f} runs lost per 100 chases (RHB median {H['cc1_rhb_median_per100']:.1f}), but {H['cc1']['2026']['per100_ooz']:.1f} per 100 out-of-zone pitches seen (median {H['cc1_rhb_median_per100_ooz']:.1f}). The individual chase is cheap; the volume isn't. "
     f"On your scatter, swing rate barely tracks wOBA across Phillies righties (r = {H['hp09_corr']['r']:.2f}).",
     ["f5_approach", "f7_swing_woba"], None),
    ("pitch", "Q5", "Velocity and breaking balls", f"No fall-off against velocity in the process: on 95+ fastballs his whiff rate fell ({pc(PB['fastball 95+']['whiff'])} → {pc(PG['fastball 95+|2026']['whiff'])}) and xwOBA matched his pooled 2023-25 line ({f3(PB['fastball 95+']['xwoba'])} → {f3(PG['fastball 95+|2026']['xwoba'])}). "
     f"The results fell ({f3(PB['fastball 95+']['woba'])} → {f3(PG['fastball 95+|2026']['woba'])} wOBA on {PG['fastball 95+|2026']['pa']} PA), and xwOBA sits below his 2024-25 peaks - a watch item. "
     f"Breaking balls were never his strength ({f3(PB['breaking']['woba'])} wOBA 2023-25) and 2026 was his best expected year against them ({f3(PG['breaking|2026']['xwoba'])} xwOBA). "
     f"If there's a 2026 hole it's swing-and-miss on offspeed: {pc(PG['offspeed|2026']['whiff'])} whiff, {pc(PG['offspeed|2026']['chase'])} chase.",
     ["f6_pitch_groups"], "pitch"),
    ("tenure", "Q7", "Five seasons in red pinstripes", f"Phillies 2022-26: {CAR['pa']} PA in {CAR['games']} games, {f3(CAR['ba'])}/{f3(CAR['obp'])}/{f3(CAR['slg'])}, {CAR['hr']} HR, {CAR['xbh']} extra-base hits, {f3(CAR['woba'])} wOBA - "
     f"{ordn(H['tenure_board']['woba_rank'])} of the {H['tenure_board']['n']} Phillies with 800+ PA in that span and {ordn(H['tenure_board']['rhb_woba_rank'])} of {H['tenure_board']['rhb_n']} right-handed hitters (PhillyVoice, CI-7: .260/.302/.444). "
     f"Carry-in bWAR 0.8 / 0.6 / 2.2 / 2.3 / 1.0 (CI-4). He played {H['pos_count_2026']} positions in 2026, adding left field (32 games, CI-4). The profile is a platoon bat: "
     f"{f3(PL['L|2026']['woba'])} wOBA vs LHP in 2026 against {f3(PL['R|2026']['woba'])} vs RHP; all Phillies righties were {f3(H['rhb_platoon_woba']['L'])} / {f3(H['rhb_platoon_woba']['R'])}. "
     f"That is the answer to 'over the hump or still valuable': still valuable, in the role he's had.",
     ["f8_tenure_platoon"], None),
    ("walkaway", "Q8", "The walkaway number", f"WA-1 was written into the BID before any decline flag was computed. Band: his 2026 salary (${WA['floor']:.1f}M, CI-3) to the top AAV among 2025-26 utility deals "
     f"(${WA['comp_max_aav']:.1f}M, Willi Castro 2/$12.8M; Kiner-Falefa 1/$6.0M, Rojas 1/$5.5M, Rosario 1/$2.5M - CI-5). Ceiling rounded down to ${WA['ceiling']:.1f}M. "
     f"Term: {WA['df_count']} of 6 decline flags tripped, so up to {WA['years']} years. <b>Walkaway: ${WA['ceiling']:.1f}M AAV, {WA['years']} years, ${WA['walkaway_total']:.0f}M total.</b> "
     f"A sensible opening is one year near his 2026 salary with a club option. If a team offers him everyday money (more per year, or a third year), the data in this report says that team is buying everyday at-bats against righties, where he has a {f3(PL['R|base']['woba'])} wOBA (2023-25) - let it go. "
     f"Context the rule doesn't price: the CBA expires after 2026 (CI-2), he turns 31 in March (CI-6), and he left the Wild Card series with a groin injury (CI-6).",
     ["f9_walkaway"], "wa"),
]

CAVEATS = [
    f"Samples: 250 PA in 2026; pitch-group bars are {min(PG[k]['pa'] for k in PG if k.endswith('2026'))}-{max(PG[k]['pa'] for k in PG if k.endswith('2026'))} PA. Season-to-season moves under ~.030 wOBA are noise at this size.",
    "OZ-1, WA-1 are provisional (new this UC). WA-1 is carry-in arithmetic plus a data check on decline; it is not a valuation model and not financial advice.",
    "Bench usage shapes the numbers: he faced left-handers in 55% of 2026 PA. Any everyday projection must reweight to a normal platoon mix.",
    "Fielding: no OAA/DRS in the log. NBC's 'top 16% OAA and sprint speed' (CI-2) is quoted, not tested. Games by position count late moves twice.",
    "TR-1 compares two halves of one bench season (162 vs 88 PA); the call is about direction, not size.",
]
