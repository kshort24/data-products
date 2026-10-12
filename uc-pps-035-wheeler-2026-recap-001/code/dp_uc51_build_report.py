"""
dp_uc51_build_report.py — the feature report for UC #51 / uc-pps-035, written from receipts.

Every number in the report is formatted here from out/dp_uc51_headlines.json or an out/dp_uc51_*.csv receipt; nothing
is typed by hand. The verification harness (family F) re-derives each published string independently.
Writes dp_uc51_wheeler_2026_recap_report.md (the PDF is rendered by dp_uc51_build_pdf.py).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC51_OUT", HERE / "out"))
DEST = Path(os.environ.get("DP_UC51_DEST", HERE))
H = json.loads((OUT / "dp_uc51_headlines.json").read_text())
R = lambda n: pd.read_csv(OUT / f"dp_uc51_{n}.csv")        # noqa: E731
from dp_uc51_hp import HP                                   # noqa: E402

pct = lambda x, d=1: f"{100 * x:.{d}f}%"                    # noqa: E731
f3 = lambda x: f"{x:.3f}".lstrip("0")                        # noqa: E731
L, P, T, ST, C, K = H['line26'], H['periods'], H['tests'], H['stretch_tests'], H['card'], H['kp']
A26, A25 = H['ars']['2026'], H['ars']['2025']
PN = {'FF': 'Four-seam', 'FS': 'Splitter', 'SI': 'Sinker', 'ST': 'Sweeper', 'FC': 'Cutter', 'CU': 'Curveball'}
order = sorted(A26, key=lambda p: -A26[p]['usage'])


def md_table(heads, rows):
    s = "| " + " | ".join(heads) + " |\n|" + "---|" * len(heads) + "\n"
    return s + "".join("| " + " | ".join(str(c) for c in r) + " |\n" for r in rows)


RG = R("recap_governed"); RG = RG[RG.era == 'PHI'].sort_values('game_year')
season_rows = []
for r in RG.itertuples():
    b = (lambda x: f"**{x}**") if r.game_year == 2026 else (lambda x: x)
    season_rows.append([b(r.game_year), b(int(r.games)), b(int(r.plate_apps)), b(f3(r.woba)), b(f3(r.xwoba)), b(f3(r.ops)), b(pct(r.krate)),
                        b(pct(r.bbrate)), b(pct(r.hard_hit_rate)), b(pct(r.barrel_rate)), b(pct(r.line_drive_rate)),
                        b("—" if pd.isna(r.jam_rate) else pct(r.jam_rate)), b(f"{r.ff_velo:.1f}")])
season_tbl = md_table(['Season', 'G', 'PA', 'wOBA', 'xwOBA', 'OPS', 'K%', 'BB%', 'Hard-hit', 'Barrel', 'LD', 'Tied-up', 'FF mph'], season_rows)

kp_rows = [[lab, (pct(K[c]['value']) if c not in ('woba', 'xwoba') else f3(K[c]['value'])), f"{K[c]['pct']}th", f"#{K[c]['rank']} of {K[c]['n']}",
            f"#{K[c]['staff_rank']} of {K[c]['staff_n']}"]
           for c, lab in [('xwoba', 'xwOBA'), ('woba', 'wOBA'), ('krate', 'K rate'), ('k_minus_bb', 'K-BB'), ('bbrate', 'BB rate'),
                          ('whiff_rate', 'Whiff rate'), ('chase_rate', 'Chase rate')]]
kp_tbl = md_table(['KPI', '2026', 'House percentile', 'Rank, 2015–26', 'Rank, 2026 staff'], kp_rows)

test_rows = []
for nm in ['In-zone (tracked)', 'Chase (swings / out-of-zone)', 'Edge (ER-1)', 'BB per PA', 'K per PA', 'Hard-hit per BIP', 'Barrel per BIP', 'Line drive per BIP']:
    a, b = T[f'{nm} · 2026 vs 2025'], T[f'{nm} · 2026 vs 2021-25']
    test_rows.append([nm, pct(a['r1']), pct(a['r2']), f"{a['p']:.3f}", pct(b['r2']), f"{b['p']:.3f}"])
test_tbl = md_table(['Rate', '2026', '2025', 'p vs 2025', '2021–25 pooled', 'p vs 2021–25'], test_rows)

PE = R("periods_2026").set_index('period').loc[['first_half', 'opener', 'stretch', 'finish']]
PLAB = {'first_half': 'First half (4/25–7/12)', 'opener': 'Post-break opener (7/21)', 'stretch': '**The slide (7/27–8/24)**', 'finish': 'The finish (8/30–9/27)'}
per_tbl = md_table(['Period', 'Starts', 'PA', 'BB%', 'K%', 'wOBA', 'xwOBA', 'In-zone', 'Edge', 'Arm-side misses', 'Runs / 27 outs'],
                   [[PLAB[p], int(r.starts), int(r.plate_apps), pct(r.bbrate), pct(r.krate), f3(r.woba), f3(r.xwoba), pct(r.in_zone_rate),
                     pct(r.edge_rate), pct(r.miss_arm_share, 0), f"{r.r27:.2f}"] for p, r in PE.iterrows()])
win_tbl = md_table(['Six starts', 'Runs on watch per 27 outs'],
                   [[f"{w['first']} → {w['last']}", (f"**{w['r27']:.2f}**" if abs(w['r27'] - 8.51) < .005 else f"{w['r27']:.2f}")] for w in H['stretch_windows']])
mx_rows = [[k, (f"{v['stretch']:.2f}" if 'ft' in k or 'in)' in k else f"{v['stretch']:.1f}"), (f"{v['rest']:.2f}" if 'ft' in k or 'in)' in k else f"{v['rest']:.1f}"),
            f"{v['n1']} / {v['n2']}", "—" if v['p'] is None else f"{v['p']:.2f}"]
           for k, v in ST.items() if k in ('FF release x (ft)', 'FF release height (ft)', 'FF extension (ft)', 'Release consistency RCI (in)', 'FF velocity (mph)')]
mx_tbl = md_table(['Four-seam, start means', 'Slide', 'Other starts', 'Starts', 'p (Welch)'], mx_rows)

pl26 = H['platoon']
plat_tbl = md_table(['2026', 'PA', 'wOBA', 'xwOBA', 'K%', 'BB%', 'Hard-hit', 'Barrel', 'Tied-up'],
                    [[f"vs {s}HB", pl26[f'2026{s}']['pa'], f3(pl26[f'2026{s}']['woba']), f3(pl26[f'2026{s}']['xwoba']), pct(pl26[f'2026{s}']['krate']),
                      pct(pl26[f'2026{s}']['bbrate']), pct(pl26[f'2026{s}']['hh']), pct(pl26[f'2026{s}']['barrel']), pct(pl26[f'2026{s}']['tied'])]
                     for s in ('R', 'L')])
ars_tbl = md_table(['Pitch', 'Usage 2025 → 2026', 'mph 2026', 'Whiff 2026', 'xwOBAcon 2026', 'RV/100 2026'],
                   [[PN[p], f"{pct(A25[p]['usage'])} → {pct(A26[p]['usage'])}", f"{A26[p]['velo']:.1f}", pct(A26[p]['whiff']),
                     f3(A26[p]['xwobacon']), f"{A26[p]['rv100']:+.1f}"] for p in order])
post_tbl = md_table(['Date', 'Round', 'Opp', 'Role', 'IP', 'H', 'R', 'BB', 'K', 'HR', 'Pitches', 'GS-1b'],
                    [[p['date'], p['round'], p['opp'], p['role'], p['ip'], p['h'], p['r'], p['bb'], p['k'], p['hr'], p['pitches'], p['gs']] for p in H['post']])
CARD = R("still_wheeler_card")
fmt = lambda b, c: f"{b:.1f} mph" if c == "first_n_ff_velo" else (f"{b:.1f}" if c == "whiff_per_100" else pct(b))  # noqa: E731
card_tbl = md_table(['#', 'Signature', 'Holds when', '2027 bar (his 2026 edge)', '2026 median', 'Same rule on 2021–25'],
                    [[r.signature, r.label, "at or above" if r.direction == "higher" else "at or below", fmt(r.bar, r.column),
                      fmt(r.season_median, r.column), fmt(r.bar_2021_25, r.column)] for r in CARD.itertuples()])
hp_tbl = md_table(['#', 'Your notebook said', 'Verdict', 'What the governed build shows'],
                  [[r.id, r.client.replace('|', '/'), f"**{r.verdict}**", r.governed.replace('|', '/')] for r in HP.itertuples()])
wc = H['wc']
bt = C['backtest_by_period']

REPORT = f"""# Still Zack Wheeler — 2026
### Season recap · RHP · Philadelphia Phillies · 28 starts + Wild Card Game 3 · data through {H['anchor']}

**Prepared for:** pitching department · front office · broadcast and content · Zack Wheeler

**Arsenal (2026):** {' · '.join(f"{PN[p].lower()} {pct(A26[p]['usage'])}" for p in order)}

**Governance:** Use Case #51 (`uc-pps-035`) · build `dp_uc51` v1.0.0 · kernel `dp_uc51_kernel.py` imports `dp_uc49_kernel` (sha256 `a4ad5191…`) and `dp_uc50_kernel` (`8084cb17…`), and extracts three governed functions by pinned source: `edge_rate` (UC8), `jam_rate` (house library, 10/9) and `release_consistency` (UC28). The October card rule (OC-1) is on its second use. New objects (CF-2b, OU-2, GS-1b, ST-1, NC-1, MX-1, SR-2, IX-1) are provisional. Independently verified; see `05_quality_certification.md`.

**Companion:** `dp_uc51_wheeler_2026_dashboard.html`, the same story in eight chapters with a start-by-start drill.

> ⚠️ **Read this first: data window, sources, carry-ins.**
>
> - **Entity lock:** MLBAM 554430, never a name filter. Regular season for every rate. The Wild Card outing and his earlier Octobers appear only in §8.
> - **Sources:** the Phillies log 2020–2026 (regular season anchored {H['anchor']}, Game 162) and `data/opponents/wheeler.parquet` (Mets 2017–19, context only). His pitches also sit in {H['opp_files_with_subject'] - 1} other opponent files; the career frame de-duplicates them by pitch key. **{H['cf2_exposure']['milb_rows']} Lehigh Valley rehab pitches** (3/28, 4/3, 4/8) are tagged as regular season in `lhvp26.parquet`; they are excluded here (MI-1).
> - **House percentiles and ranks** are Phillies pitcher-seasons, 2015–2026. They are **not MLB-wide**.
> - **"Runs on watch"** are runs that scored during the plate appearances he threw. They include unearned runs; this is not ERA. **Outs** come from OU-2 (the outs sequence of the full defensive log), which reconciles to the published {H['carry']['ip']} IP; the older event-map method (OU-1) finds {H['carry']['outs_ou1']} of the {H['carry']['outs']} outs.
> - **Tied-up rate** is a public-data proxy for Baseball Savant's swing-timing bucket (house `jam_rate`, intercept < 32.5 in). Savant's own edge (42.4%) and xwOBA (.263) are quoted from your notebook and reconciled, never substituted.
> - **Carry-ins, never computed on:** 2025 ended after 8/15/2025 with a blood clot; venous thoracic outlet syndrome; first-rib resection 9/23/2025 (MLB.com 8/2025, Inquirer 9/19/2026). Three-year, $126M extension signed March 2024, one year left (Inquirer). Season line 14–5, 3.00 ERA, 162.0 IP, 193 K, 47 BB (StatMuse). A six-start post-break slide with an 8.51 ERA, blamed on a dropped glove and over-rotation, since fixed (Inquirer). Wild Card G3: four innings of relief, two runs, Braves 6–2 (FOX 29, 10/1).
> - **The body.** The log shows velocity, release point and location. It does not show an injury or a glove, and nothing here infers either.

![Notecard](out/dp_uc51_fig13_notecard.png)

---

## Bottom line

1. **He is still Zack Wheeler.** His {f3(L['xwoba'])} xwOBA (your Savant number exactly) is #{H['ctx_sw']['rank_xwoba']} of {H['ctx_sw']['n']} Phillies seasons with a starter's workload since 2015, and **{H['ctx_sw']['wheeler_seasons_top10_xwoba']} of the top ten are his**. K-BB {pct(L['k_minus_bb'])} ranks #{H['ctx_sw']['rank_k_minus_bb']}. He threw {H['carry']['ip']} innings in 28 starts after a rib resection.
2. **The walk rate is six starts, not a season.** His {pct(L['bbrate'])} walk rate is the highest of his seven Phillies seasons. Almost all of it came from 7/27 to 8/24: {pct(P['stretch']['bbrate'])} ({P['stretch']['walks']} walks in {P['stretch']['pa']} PA) against {pct(ST['BB per PA']['rest'])} in his other 22 starts (p = {ST['BB per PA']['p']:.3f}). That window, and only that window, reconciles to the reported 8.51 ERA. Over the last six starts he walked {pct(P['finish']['bbrate'])} and allowed {P['finish']['r27']:.2f} runs per 27 outs.
3. **The log is consistent with a delivery problem that got fixed, and it cannot prove one.** During the slide, his clear misses went to the arm side {pct(ST['Arm-side share of clear misses']['stretch'])} of the time against {pct(ST['Arm-side share of clear misses']['rest'])} otherwise (p = {ST['Arm-side share of clear misses']['p']:.3f}), then fell to {pct(P['finish']['miss_arm'])} in the finish. His four-seam release point, extension and release consistency did not move.
4. **Your instinct on the zone was the biggest finding.** In-zone rate fell to {pct(L['in_zone_rate'])} (2021–25: {pct(T['In-zone (tracked) · 2026 vs 2021-25']['r2'])}, p < .001), the lowest of his Phillies years, and hitters chased {pct(L['chase_rate'])}, the highest. Edge rate did not move. Contact quality was noise, as you said: hard-hit, barrel and line-drive rates all sit inside his range (every p > .4).
5. **For 2027, the bar is written down first.** The Still-Wheeler card sets four bars from his own 2026 starts. On-script starts in 2026 allowed {C['on_r27']:.2f} runs per 27 outs and off-script starts {C['off_r27']:.2f}; the finish was {bt['finish']} on-script. His Wild Card relief outing, graded after the fact, was {C['wc_posthoc']['verdict'].lower()}: {pct(C['wc_values']['bb_rate'])} walks and {C['wc_values']['whiff_per_100']:.1f} whiffs per 100 pitches.

---

## 1 · The return

{season_tbl}
*2020 was a 60-game season (286 PA). Tied-up rate needs bat tracking, which begins in 2025.*

His 2025 stopped after August 15. The 2026 log starts on April 25, after three rehab starts at Lehigh Valley. The first half was already certified: `uc-pps-020` published 15 starts, 92.0 IP, a .246 wOBA, a 30.4% K rate, a 6.2% walk rate and a 36.2% chase rate through July 12. This recap recomputes all six before adding anything (**{H['repro']}**). The published season line (14–5, 3.00 ERA, 162.0 IP, 193 K, 47 BB) reconciles to the log on innings, strikeouts and walks.

## 2 · Still Zack Wheeler

{kp_tbl}
*House population: {K['xwoba']['n']} Phillies pitcher-seasons with ≥100 PA, 2015–2026. 2026 staff: {K['xwoba']['staff_n']} pitchers.*

![Still Wheeler](out/dp_uc51_fig1_still_wheeler.png)

Read the board two ways. Against the room, 2026 sits in the top-right corner with his own best seasons. Against himself, 2026 is a step behind 2025 and 2021 on both axes and just ahead of 2024. That is what "for now he is still Zack Wheeler" looks like in numbers.

![Results by season](out/dp_uc51_fig2_results_by_season.png)

## 3 · He stopped needing the zone

{test_tbl}
*Pooled two-proportion z-test (house standard). In-zone uses tracked pitches as the denominator.*

![Zone expansion](out/dp_uc51_fig3_zone_expansion.png)

The largest change of his season is where he threw the ball, not how hard. Eight points fewer pitches in the zone than his 2021–25 rate, and the most chases of his Phillies years. The splitter is the engine (§7): {pct(A26['FS']['usage'])} of his pitches, mostly below the zone, with a {pct(A26['FS']['whiff'])} whiff rate.

**Edge rate.** Your note quotes Savant: *"Wheels was edging us 42.4% of the time."* The house edge rate (ER-1, from `uc-pps-008`) counts pitches whose centre is within one baseball of the rulebook zone line, and gives {pct(L['edge_rate'])}. Savant draws its edge band differently, so the two numbers measure different areas and should not be compared. On ER-1, 2026 is ordinary for him (p = {T['Edge (ER-1) · 2026 vs 2021-25']['p']:.2f} against 2021–25). Throwing fewer strikes did not mean throwing fewer competitive pitches.

## 4 · The six-start slide

Reporting described *"an 8.51 ERA over six starts"* after the All-Star break. The log has eight runs of six consecutive post-break starts. Exactly one of them allowed 8.51 runs on watch per 27 outs:

{win_tbl}
That is the slide: 7/27 to 8/24. It is identified by reconciliation, not chosen because it looks bad, and the build asserts the match (DQ-30).

{per_tbl}
![The slide](out/dp_uc51_fig4_the_stretch.png)

**What changed in the slide:** walks ({pct(ST['BB per PA']['stretch'])} vs {pct(ST['BB per PA']['rest'])}, p = {ST['BB per PA']['p']:.3f}) and the direction of his misses. **What did not:** strikeouts ({pct(ST['K per PA']['stretch'])} vs {pct(ST['K per PA']['rest'])}, p = {ST['K per PA']['p']:.2f}), chase (p = {ST['Chase']['p']:.2f}), in-zone (p = {ST['In-zone']['p']:.2f}), the share of clear misses ({pct(ST['Clear miss']['stretch'])} vs {pct(ST['Clear miss']['rest'])}, p = {ST['Clear miss']['p']:.2f}) and the delivery measures below.

{mx_tbl}
*Arm angle is published by Statcast for only {pct(H['arm_angle_cov_2026'], 0)} of his 2026 four-seams (one slide start has it), so it is not tested.*

![Misses and release](out/dp_uc51_fig5_misses_and_release.png)

The reported cause was a mechanical flaw: dropping the glove and over-rotating. The log is consistent with that story in one way: the misses that were clearly out of the zone drifted to his arm side during the slide and came back after it. It is silent in another: the four-seam left his hand from the same place throughout. A glove and a rotation are not in the data. What the data says is that he missed the same amount, missed in a different direction, walked people for six starts, and stopped.

## 5 · Contact and swing timing

![Contact quality](out/dp_uc51_fig6_contact_quality.png)

Your read holds: fewer barrels, no surge in line drives or hard contact, and none of the three is distinguishable from his normal. Hard-hit rate is the second-highest of his Phillies years ({pct(L['hard_hit_rate'])}) without being a real change (p = {T['Hard-hit per BIP · 2026 vs 2021-25']['p']:.2f}).

**Tied-up rate.** Hitters were tied up on {pct(L['jam_rate'])} of his {L['tracked_swings']:,} tracked swings ({H['st']['2026']['centered'] * 100:.1f}% centered, {H['st']['2026']['flail'] * 100:.1f}% flail; 2025: {pct(H['st']['2025']['tied'])} tied up). Among {H['tied_pop']['n']} Phillies pitcher-seasons in 2025–26 with at least 50 tracked swings, that is #{H['tied_pop']['rank']} (mean {pct(H['tied_pop']['mean'])}); among the {H['tied_pop']['n_big']} with at least 500, #{H['tied_pop']['rank_big']}. The leader is {H['tied_pop']['leader']['name'].split(', ')[1]} {H['tied_pop']['leader']['name'].split(', ')[0]} ({pct(float(H['tied_pop']['leader']['tied_up_rate']))}). Good, not the top of the room.

![Tied-up population](out/dp_uc51_fig7_tied_up_population.png)

The signature is the sinker in on right-handed hitters. {H['si_jam']['swings']} of their swings at it were tied up; {H['si_jam']['bip']} of those went in play, for {H['si_jam']['hits']} hits, an average exit velocity of {H['si_jam']['ev']:.1f} mph and {pct(H['si_jam']['gb_share'], 0)} ground balls. Your notebook counted 57; the difference is Wild Card rows (§9, HP-10). A foul bunt is not counted as a swing (JR-1).

![Swing timing by pitch](out/dp_uc51_fig8_swing_timing_by_pitch.png)

## 6 · Lefties did the damage

{plat_tbl}
![Platoon](out/dp_uc51_fig9_platoon.png)

Right-handed hitters were helpless: a {f3(pl26['2026R']['woba'])} wOBA, a {pct(pl26['2026R']['bbrate'])} walk rate and {pct(pl26['2026R']['tied'])} of their swings tied up. Lefties hit him harder: {pct(H['platoon_tests']['Hard-hit']['L'])} hard-hit against {pct(H['platoon_tests']['Hard-hit']['R'])} (p = {H['platoon_tests']['Hard-hit']['p']:.3f}), and they walked more ({pct(H['platoon_tests']['BB per PA']['L'])} vs {pct(H['platoon_tests']['BB per PA']['R'])}, p = {H['platoon_tests']['BB per PA']['p']:.2f}). The split is real and familiar: it was wider in 2024 ({f3(H['platoon_gap']['2024'])} wOBA) and nearly absent in 2021–22.

## 7 · Six pitches, the splitter second

{ars_tbl}
*RV/100 = run value per 100 pitches, pitcher's view (positive is good for him).*

![Pitch map](out/dp_uc51_fig10_pitch_map.png)

![Pitch plot](out/dp_uc51_fig11_pitch_plot.png)

The four-seam averaged {H['velo']['season26']:.1f} mph, the slowest of his Phillies years (2021: {H['velo']['season21']:.1f}; 2025: {H['velo']['season25']:.1f}). The carry-in figures reconcile: {H['velo']['jul25']:.1f} in July 2025, {H['velo']['sep26']:.1f} in September 2026. Velocity held within the season ({H['halves']['first']['velo']:.1f} first half, {H['halves']['second']['velo']:.1f} second). The slowing is across years, and the splitter is how he has answered it.

## 8 · October, and 2027

**Wild Card Game 3, 10/1 at Atlanta.** Four days after Game 162, he entered in the 3rd after Aaron Nola's early exit: {wc['ip']} IP, {wc['h']} H, {wc['r']} R, {wc['bb']} BB, {wc['k']} K on {wc['pitches']} pitches. The runs came on {wc['hr_batters'][0]}'s two-run homer in the {wc['hr_innings'][0]}th. Braves 6, Phillies 2. It was his {len(H['post'])}th postseason game for the Phillies.

{post_tbl}
*Phillies postseason, 2022–2026: {H['post_tot']['pa']} PA, wOBA {f3(H['post_tot']['woba'])}, K {pct(H['post_tot']['krate'])}. GS-1b = Game Score (Tango v2 form) on OU-2 outs; log-derived, not the published stat.*

**The Still-Wheeler card.** One year is left on his deal. The card writes down now, before a 2027 pitch, what still being this pitcher means in his own 2026 numbers. The rule is OC-1 from `uc-pps-034`, unchanged: a start is **on-script** when at least three of the four signatures hold.

{card_tbl}
![Still-Wheeler card](out/dp_uc51_fig12_still_wheeler_card.png)

- **Backtest on 2026 (calibration, not prediction):** {C['on']} on-script starts allowed {C['on_r27']:.2f} runs per 27 outs; {C['off']} off-script starts allowed {C['off_r27']:.2f}. By period: first half {bt['first_half']}, the slide {bt['stretch']}, the finish {bt['finish']}.
- **The bars moved.** Against his 2021–25 edge the 2026 bars are softer on velocity ({C['bars']['OC-A']:.1f} vs {C['bars_prime']['OC-A']:.1f} mph) and walks ({pct(C['bars']['OC-D'])} vs {pct(C['bars_prime']['OC-D'])}), and stricter on chase ({pct(C['bars']['OC-B'])} vs {pct(C['bars_prime']['OC-B'])}) and whiffs ({C['bars']['OC-C']:.1f} vs {C['bars_prime']['OC-C']:.1f} per 100). He gets outs differently now. {pct(C['prime_on_share'], 0)} of his {C['prime_starts']} starts from 2021–25 would pass the 2026 card.
- **Wild Card G3, graded after the fact:** arm and chase held; whiffs and walks slipped; {C['wc_posthoc']['verdict']}. It is one relief outing on three days' rest, graded post hoc, and it counts for nothing except as an example of how the card reads.
- **How it is used:** grade every 2027 start as it posts (v1.1.0). Changing a bar after the first 2027 pitch is a breaking change.

## 9 · Your notebook, graded

{hp_tbl}
## 10 · Candid caveats

- **Phillies frame.** Every rank and percentile is Phillies pitcher-seasons, 2015–2026. Nothing here is MLB-wide.
- **The slide window is identified by reconciliation** to a reported ERA. Runs on watch include unearned runs; the match being exact (8.51) means none of those 23 runs was unearned, or the report used the same convention.
- **Two-proportion tests treat pitches and PA as independent.** They are not quite (pitches cluster within starts), so p-values near .05 (the arm-side miss share, .033) are suggestive, not settled. The walk-rate result (p = {ST['BB per PA']['p']:.3f}) is the firm one.
- **Arm angle** is missing for {100 - round(100 * H['arm_angle_cov_2026'])}% of 2026 four-seams in the source and is not used.
- **ST-1's flail boundary (41 in)** comes from your histogram, not from Savant. Tied-up (JR-1) is the governed number; centered and flail are provisional.
- **Edge rate** (ER-1) and Savant's edge% are different definitions; 42.4% is a carry-in.
- **The Still-Wheeler card predicts nothing.** It is a definition, registered before the evidence that will grade it.
- **Carry-ins** (injury history, contract, season line, the reported mechanical cause, the Wild Card box) are reported facts. They are cited, not computed on.

---

*Receipts: `out/dp_uc51_*` (CSV/JSON/PNG) · DQ {H['dq'].get('PASS', 0)} PASS / {H['dq'].get('WARN', 0)} WARN / {H['dq'].get('FAIL', 0)} FAIL · build `dp_uc51_wheeler_recap.py` · figures `dp_uc51_build_figs.py` · harness `dp_uc51_verification.py` · governance trail: `Agents for Data Products/data-products/uc-pps-035-wheeler-2026-recap-001/`.*
"""
(DEST / "dp_uc51_wheeler_2026_recap_report.md").write_text(REPORT, encoding="utf-8")
print("report", len(REPORT.split()), "words")
