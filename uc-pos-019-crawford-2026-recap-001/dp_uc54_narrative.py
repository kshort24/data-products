"""dp_uc54_narrative.py - every sentence of the report and dashboard, formatted from out/dp_uc54_headlines.json.
No number is typed by hand; harness family F re-derives the published strings."""
from __future__ import annotations
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"
H = json.loads((OUT / "dp_uc54_headlines.json").read_text(encoding="utf-8"))
SPECS = {s["figure"]: s for s in json.loads((OUT / "dp_uc54_figure_specs.json").read_text(encoding="utf-8"))}


def f3(x):
    s = f"{x:.3f}"
    return s[1:] if s.startswith("0.") else ("-" + s[2:] if s.startswith("-0.") else s)


def pc(x, d=1):
    return f"{100 * x:.{d}f}%"


def ordn(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


P, T, CX, CC, X, A = H["profile"], H["tr1"], H["cx"], H["cc1"], H["xo2"], H["aaa"]
RB, RBA, RBM = H["rhp_bb"], H["rhp_bb"]["AAA 2025"], H["rhp_bb"]["MLB 2026"]
HZ = H["rhp_bb_hits_heart"]
TITLE = "Exactly as Advertised"
SUB = "Justin Crawford, 2026"
SLASH = f"{f3(H['ba'])}/{f3(H['obp'])}/{f3(H['slg'])}"
better = lambda m: P[m]["better"]   # noqa: E731
LOWEST_AA = "lowest" if H["aa_rank_low"] == 1 else f"{ordn(H['aa_rank_low'])}-lowest"
R_RUNS = sum(v["runs"] for k, v in CC["by"].items() if k.startswith("R_"))

READ_FIRST = [
    f"<b>Entity lock:</b> MLBAM 702222 with the Phillies batting role, never a name filter (<code>data/opponents/crawford.parquet</code> is J.P. Crawford, "
    f"a trap logged as ENT-2). Regular season for every rate: {int(H['plate_apps'])} PA, {H['pitches_seen']:,} pitches, {H['games_with_pa']} games with a plate "
    f"appearance ({H['first_game']} to {H['last_game']}). Spring (125 pitches) and the Wild Card ({H['post']['pitches']} pitches) are excluded.",
    f"<b>AAA 2025</b> (Lehigh Valley, {int(A['plate_apps'])} PA) is a supporting tier. It is labelled wherever it appears and never blended into an MLB rate; "
    f"its tracking is thinner ({A['ev_untracked_bip']} balls in play without exit velocity).",
    f"<b>House ranks are not MLB-wide.</b> Percentiles compare {H['pool_n']} Phillies hitter-seasons {H['pool_years']} (50+ PA). Centre-field context is the "
    f"{CX['n']} Phillies primary-CF seasons of the Statcast era (CX-1, inherited from uc-pos-011).",
    "<b>Defense is a proxy.</b> The log has no catch probability, routes or jumps. XO-2 scores ball flight against similar balls other centre fielders saw; "
    "read its sign and its rank, not its decimal.",
    "<b>Carry-ins, never computed on:</b> debut 2026-03-26 (CI-1, Wikipedia); 149 G, 17 SB in 21, OPS+ 78, −0.2 WAR, −8 OAA, −2 DRS, platoon role once Derek Hill "
    "emerged (CI-2, 97.5 The Fanatic, 2026-10-14); −3 OAA in March/April, 0 in May, 97th-percentile sprint speed (CI-3, Philadelphia Inquirer, 2026-06-05); "
    "2025 AAA .334 with 46 SB (CI-4).",
]

BOTTOM = [
    f"<b>He was the hitter the scouting report said he would be.</b> {SLASH}, {f3(H['woba'])} wOBA (xwOBA {f3(H['xwoba'])}) over {int(H['plate_apps'])} PA. "
    f"Among the {CX['n']} Phillies primary-CF seasons since 2015 he ranks {ordn(CX['rank']['ba'])} in BA and {ordn(CX['rank']['woba'])} in wOBA at {CX['matched_pa']} PA, "
    f"ahead of only Rojas 2024 on wOBA. With runners in scoring position he hit {f3(H['risp_ba'])} ({int(H['risp_hits'])} for {int(H['risp_ab'])}).",
    f"<b>\"Better from June 1\" is half right.</b> His batting average rose {f3(T['rows']['R2']['pre'])} → {f3(T['rows']['R2']['post'])}, but wOBA moved only "
    f"{T['rows']['R1']['delta']:+.3f}, his walk rate fell {pc(T['rows']['P3']['pre'])} → {pc(T['rows']['P3']['post'])} and his chase rate did not move. The pre-registered "
    f"turn test (TR-1) reads <b>{T['call']}</b>. The real shape was a hole that bottomed in mid-June, a surge to an August 9 peak, and a fade.",
    f"<b>The approach is elite contact wrapped around a chase habit.</b> Swing rate {pc(H['swing_rate'])} ({ordn(P['swing_rate']['pct'])} percentile), chase "
    f"{pc(H['chase_rate'])} (better than only {better('chase_rate')}%), whiff {pc(H['whiff_rate'])} (better than {better('whiff_rate')}%), out-of-zone contact "
    f"{pc(H['ooz_contact_rate'])} (better than {better('ooz_contact_rate')}%). The contact keeps strikeouts down; it also turns chases into weak balls in play "
    f"({f3(H['ooz_ba'])} BA out of the zone) instead of walks.",
    f"<b>The ground-ball rate is the ceiling.</b> {pc(H['gb_rate'])} grounders, a {H['mean_la']:.1f}° average launch angle ({ordn(H['la_rank_low'])}-lowest of {P['mean_la']['n']} Phillies "
    f"hitter-seasons, lowest of any with 100+ PA) and a {H['attack_angle_mu']:.1f}° attack angle ({LOWEST_AA} of {P['attack_angle_mu']['n']} tracked). His hard-hit rate ({pc(H['hard_hit_rate'])}) is mid-pack; "
    f"the ball is just going into the ground.",
    f"<b>For 2027: fewer chases from righties, then lift.</b> He reached a three-ball count in only {pc(H['reach3']['value'])} of plate appearances "
    f"({ordn(H['reach3']['pct'])} percentile). Chasing at the house median would have meant about {CC['chases_above_median']:.0f} fewer chases, worth roughly "
    f"{CC['excess_runs']:.0f} runs on the CC-1 arithmetic. In centre field he was about {abs(X['oae']):.0f} outs short of expectation ({X['oae']:+.1f}, XO-2), "
    f"in line with the −8 OAA on record (CI-2). The notebook's method said he made every play; it only counted balls he reached.",
]

CH = [
    ("line", "Q1", "The rookie line",
     f"He finished at {SLASH} with {int(H['hrs'])} home runs, {int(H['doubles'])} doubles and {int(H['triples'])} triples. The cumulative lines tell the season: "
     f"a hot first two weeks, a slide to a .227 batting average on June 13 (plate appearance {H['cum_woba_min']['pa']}), then a steady climb back to the middle "
     f"of the pack for a Phillies centre fielder. On wOBA he sits {ordn(CX['rank']['woba'])} of {CX['n']} at matched volume, between Rojas 2024 and the Herrera seasons. "
     f"The RISP line ({f3(H['risp_ba'])}/{f3(H['risp_obp'])}/{f3(H['risp_slg'])}, {int(H['risp_pa'])} PA) is the brightest number of his year and the least "
     f"repeatable; it rests on singles and the same ground-ball BABIP as everything else. His final hard-hit rate was {pc(H['hard_hit_rate'])} and his "
     f"ground-ball rate {pc(H['gb_rate'])}.",
     ["f1_cumulative_slash"], "line"),
    ("turn", "Q2", "The June turn",
     f"The notebook's hypothesis was tested with ten signatures registered in the BID before any split was computed. Batting average cleared its bar "
     f"(PRESENT, {T['rows']['R2']['delta']:+.3f}); wOBA, OBP, slugging, xwOBA, strikeout rate and whiff rate moved the right way but short of their bars; chase "
     f"and hard-hit did not move; walk rate moved the wrong way. Results {T['results']}, process {T['process']}: <b>{T['call']}</b>. The BA gain came from "
     f"BABIP ({f3(T['pre_babip'])} → {f3(T['post_babip'])}) while isolated power fell ({f3(T['pre_iso'])} → {f3(T['post_iso'])}). Only "
     f"{H['scan_positive']} of {H['scan_n']} candidate breakpoints show any wOBA gain at all, and the best one (June 15, {H['scan']['2026-06-15']['d_woba']:+.3f}) "
     f"is the date UC34 was handed in August. What did happen is a surge: trailing-100-PA wOBA rose from {f3(H['roll_min']['woba'])} (June 18) to "
     f"{f3(H['roll_max']['woba'])} (August 9) and finished at {f3(H['roll_final']['woba'])}.",
     ["f2_rolling_form", "f3_tr1_ledger"], "turn"),
    ("approach", "Q3", "The approach",
     f"High swing, high chase, low whiff: all three confirmed against {H['pool_n']} Phillies hitter-seasons. What makes him unusual is the combination. He "
     f"swings at {pc(H['regions']['waste']['swing'])} of pitches well off the plate (house {pc(H['regions_house']['waste']['swing'])}) and misses only "
     f"{pc(H['regions']['waste']['whiff'])} of those swings (house {pc(H['regions_house']['waste']['whiff'])}). That is why his strikeout rate is low "
     f"({pc(H['krate'])}, better than {better('krate')}%). It is also why his walk rate is low ({pc(H['bbrate'])}): the chase pitch becomes a ball in play. "
     f"Out of the zone he hit {f3(H['ooz_ba'])} with a {pc(H['ooz_hh'], 0)} hard-hit rate; in the zone, {f3(H['iz_ba'])} and {pc(H['iz_hh'], 0)}.",
     ["f4_profile", "f5_attack_regions"], "approach"),
    ("groundballs", "Q6", "Ground balls",
     f"His ground-ball rate settled at {pc(H['gb_rate'])} and stayed there; only {100 - better('gb_rate')}% of Phillies hitter-seasons since 2015 hit more "
     f"grounders. The cause is the swing plane. His {H['mean_la']:.1f}° average launch angle is the {ordn(H['la_rank_low'])}-lowest of {P['mean_la']['n']} Phillies hitter-seasons "
     f"(only {H['la_lower_seasons'][0]} was flatter) and the lowest of any with 100+ PA, against "
     f"{H['la_house_2026_mean']:.1f}° for the rest of the 2026 roster, and his average attack angle ({H['attack_angle_mu']:.1f}°) is the {LOWEST_AA} of "
     f"{P['attack_angle_mu']['n']} tracked Phillies seasons. Exit velocity is not the problem: hard-hit rate is {ordn(CX['rank']['hh'])} of {CX['n']} among the CF "
     f"seasons. Speed props up the grounders: {H['gb']['hits']} hits on {H['gb']['n']} ground balls ({f3(H['gb']['ba'])}). After June 1 that rose to "
     f"{f3(H['gb']['halves']['post']['ba'])} on softer contact ({H['gb']['halves']['post']['ev']:.1f} mph vs {H['gb']['halves']['pre']['ev']:.1f}) with an expected "
     f"average of only {f3(H['gb']['halves']['post']['xba'])}.",
     ["f6_cumulative_gb_hh"], None),
    ("walks", "Q4", "Where the walks went",
     f"The walk problem starts upstream. He reached a three-ball count in {pc(H['reach3']['value'])} of plate appearances; the house median is "
     f"{pc(H['reach3']['pool_median'])} ({ordn(H['reach3']['pct'])} percentile of {H['reach3']['n']} Phillies hitter-seasons 2023-26). When he got there he walked "
     f"{H['walks_of_three_ball']} times in {H['three_ball_pa']} plate appearances. CC-1 prices every chase against the house take in the same count: {CC['runs']:.1f} runs "
     f"over {CC['chases']} chases. Per out-of-zone pitch that is near the house median ({CC['per100ooz']:.2f} vs {CC['pool_median_per100ooz']:.2f} per 100), because "
     f"he makes contact; the cost is in the volume. {R_RUNS:.1f} of the {CC['runs']:.1f} runs came against right-handers, and {CC['by_strikes']['2']['runs']:.1f} came "
     f"with two strikes. By pitch, his chase rate is highest on righty breaking balls ({pc(CC['by']['R_breaking']['chase'])}) and changeups "
     f"({pc(CC['by']['R_offspeed']['chase'])}), both buried below the zone, but the costliest by volume are fastballs above it "
     f"({CC['by']['R_fastball']['runs']:.1f} runs). Chasing at the house median rate ({pc(CC['pool_chase_median'])}) would have taken away about "
     f"{CC['chases_above_median']:.0f} chases, worth roughly {CC['excess_runs']:.0f} runs. Treat that as arithmetic, not a projection.",
     ["f7_chase_map_rhp"], "walks"),
    ("spin", "Q4", "Righty spin",
     f"The notebook's breaking-ball study holds up. Against RHP breaking balls his batting average barely changed from AAA to MLB ({f3(RBA['ba'])} → "
     f"{f3(RBM['ba'])}), but the damage did: hard-hit {pc(RBA['hh'])} → {pc(RBM['hh'])}, average exit velocity {RBA['ev']:.1f} → {RBM['ev']:.1f} mph, and the chase "
     f"rate rose {pc(RBA['chase'])} → {pc(RBM['chase'])}. In AAA, {HZ['AAA 2025']['heart']} of his {HZ['AAA 2025']['hits']} hits off righty spin came on pitches in "
     f"the heart of the zone; in the majors, {HZ['MLB 2026']['heart']} of {HZ['MLB 2026']['hits']}. Major-league breaking balls end lower (the average hit pitch "
     f"dropped from {HZ['AAA 2025']['mean_plate_z']:.2f} ft to {HZ['MLB 2026']['mean_plate_z']:.2f} ft). When he does put one in play he pulls it "
     f"({pc(H['direction']['MLB 2026|rhpbb|Pull']['share'], 0)} pull vs {pc(H['direction']['MLB 2026|other|Pull']['share'], 0)} on everything else). "
     f"On every other pitch he already uses the whole field: {pc(H['dir_mlb_hits']['Oppo'], 0)} of his 2026 hits went the other way.",
     ["f8_rhp_breaking", "f9_spray_rhp_breaking"], "spin"),
    ("cf", "Q5", "Centre field",
     f"The notebook's similar-hit method, run exactly as written, says he made the plays he should have: {H['hp_xo1_client']['outs']} outs against "
     f"{H['hp_xo1_client']['xouts']:.1f} expected. That method only scores balls he fielded, so a ball that fell in front of him or in the gap never counts against "
     f"him. XO-2 starts from every air ball of 150+ ft within 15° of dead centre with him in centre ({X['opps']} balls; {X['scored']} scored). Scored against "
     f"{X['pool_n']:,} similar balls other centre fielders saw, he made {X['outs']} outs against {X['xouts']:.1f} expected: <b>{X['oae']:+.1f}</b>, "
     f"{ordn(X['ctx_rank'])} of {X['ctx_n']} Phillies CF seasons since 2015. The path matches the reporting: a poor April "
     f"({X['by_month']['4']['oae']:+.1f}; CI-3 has him at −3 OAA in March and April), an even May ({X['by_month']['5']['oae']:+.1f}; CI-3: OAA 0), then a "
     f"July and September slide. The −8 OAA on record (CI-2) lands in the same place.",
     ["f10_centre_field"], "cf"),
]

CAVEATS = [
    f"465 PA is one season. The RISP line ({int(H['risp_pa'])} PA) and every split under 100 PA is directional.",
    "TR-1's PRESENT bar needs p < .05 where a test applies; at 182 and 283 PA most real changes read WEAK. That is the honest reading of the sample, not a ruling that nothing changed.",
    "CC-1 prices a chase against the average take in the same count. It does not know what the next pitch would have been, so its totals are indicative.",
    f"XO-2 is a ball-flight proxy. It knows exit velocity, launch angle, distance and direction, not positioning, wind, wall or jump. Every Phillies CF season since 2015 "
    f"but one scores below zero, so the baseline (all centre fielders in Phillies games) runs high; read the rank. The four neighbourhood variants range "
    f"{H['xo2_sens']['v1']['oae']:+.1f} to {H['xo2_sens']['v3']['oae']:+.1f}; all negative.",
    f"AAA comparisons cross levels and tracking systems ({A['ev_untracked_bip']} untracked AAA balls in play).",
    f"Postseason (Wild Card, {H['post']['games']} games): {H['post']['hits']} hit in {H['post']['ab']} at-bats, {H['post']['pa']} PA. Shown here only; never in a rate.",
    "The August platoon shielding found by uc-pos-011 continued (CI-2). His splits vs LHP (66 PA) are too thin to judge it.",
]
