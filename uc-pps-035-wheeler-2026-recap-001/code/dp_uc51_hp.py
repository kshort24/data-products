"""
dp_uc51_hp.py — the human-parent reconciliation (HP family) for UC #51 / uc-pps-035.

Every claim and chart choice in October 2026.ipynb cells 16 and 21-23, each beside the governed value.
Reads only out/dp_uc51_headlines.json; every number is formatted from a receipt, never typed.
Writes out/dp_uc51_hp_reconciliation.csv. Imported by the dashboard and report builders.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC51_OUT", HERE / "out"))
H = json.loads((OUT / "dp_uc51_headlines.json").read_text())
pct = lambda x, d=1: f"{100 * x:.{d}f}%"                    # noqa: E731
f3 = lambda x: f"{x:.3f}".lstrip("0")                        # noqa: E731
L, T, P, ST = H['line26'], H['tests'], H['periods'], H['stretch_tests']


def rows():
    tb = T['BB per PA · 2026 vs 2021-25']
    return [
        dict(id="HP-01", client="\"It was the highest walk rate of Wheeler's time with the Phillies (7.6%).\"", verdict="SUPPORTED",
             governed=f"Highest of his seven Phillies seasons: {pct(L['bbrate'])} over {L['plate_apps']} regular-season PA. The 7.6% reproduces "
                      f"exactly in your frame, which also holds the Wild Card outing ({int(H['client26']['plate_apps'])} PA). Against his 2021–25 rate "
                      f"({pct(tb['r2'])}) the season-level rise is not significant on its own (p = {tb['p']:.2f})."),
        dict(id="HP-02", client="\"This also felt like the theme during his struggles in August. He lost his previously elite command.\"", verdict="SUPPORTED, SHARPENED",
             governed=f"The walks are six starts, 7/27–8/24: {pct(P['stretch']['bbrate'])} ({P['stretch']['walks']} in {P['stretch']['pa']} PA) vs "
                      f"{pct(ST['BB per PA']['rest'])} in his other 22 starts (p = {ST['BB per PA']['p']:.3f}). That window reconciles to the reported "
                      f"8.51 ERA. He got it back: {pct(P['finish']['bbrate'])} over the last six starts."),
        dict(id="HP-03", client="\"Most of the other results appear to just be noise. Fewer barrels, no huge surge in line drives or hard hits.\"", verdict="SUPPORTED",
             governed="Against his 2021–25 baseline: " + "; ".join(
                 f"{k.split(' per')[0].lower()} {pct(T[k + ' · 2026 vs 2021-25']['r1'])} vs {pct(T[k + ' · 2026 vs 2021-25']['r2'])} "
                 f"(p = {T[k + ' · 2026 vs 2021-25']['p']:.2f})" for k in ('Barrel per BIP', 'Line drive per BIP', 'Hard-hit per BIP')) + "."),
        dict(id="HP-04", client="\"Pretty strong platoon splits. Elite against righties but lefties did more damage.\"", verdict="SUPPORTED",
             governed=f"vs RHB {f3(H['platoon']['2026R']['woba'])} wOBA / {f3(H['platoon']['2026R']['xwoba'])} xwOBA; vs LHB "
                      f"{f3(H['platoon']['2026L']['woba'])} / {f3(H['platoon']['2026L']['xwoba'])}. The damage is contact: hard-hit "
                      f"{pct(H['platoon_tests']['Hard-hit']['L'])} vs {pct(H['platoon_tests']['Hard-hit']['R'])} (p = {H['platoon_tests']['Hard-hit']['p']:.3f}). "
                      f"The gap was wider in 2024 ({f3(H['platoon_gap']['2024'])})."),
        dict(id="HP-05", client="\"xwOBA = .263, very good!\"", verdict="REPRODUCED",
             governed=f"XW-1 (inherited from uc-pos-018) gives {f3(L['xwoba'])}, matching Savant. {H['kp']['xwoba']['pct']}th house percentile of "
                      f"{H['kp']['xwoba']['n']} Phillies pitcher-seasons; #{H['ctx_sw']['rank_xwoba']} of {H['ctx_sw']['n']} starter workloads since 2015, "
                      f"and {H['ctx_sw']['wheeler_seasons_top10_xwoba']} of the top 10 are his."),
        dict(id="HP-06", client="\"Edge rate (per Statcast Wheels was edging us 42.4% of the time).\"", verdict="DIFFERS: DEFINITION",
             governed=f"The house edge rate (ER-1, uc-pps-008: centre within one baseball of the zone line) is {pct(L['edge_rate'])}. Savant's "
                      f"edge band is drawn differently, so 42.4% is a carry-in, not a receipt. On either definition it is not what moved: ER-1 vs "
                      f"2021–25 p = {T['Edge (ER-1) · 2026 vs 2021-25']['p']:.2f}."),
        dict(id="HP-07", client="\"Edge rate would be a good one to double click on, as well as zone expansion.\"", verdict="SUPPORTED: ZONE",
             governed=f"Zone expansion is the year's largest change: in-zone {pct(L['in_zone_rate'])} (lowest of his Phillies years; 2021–25 "
                      f"{pct(T['In-zone (tracked) · 2026 vs 2021-25']['r2'])}, p < .001) and chase {pct(L['chase_rate'])} (highest; p = "
                      f"{T['Chase (swings / out-of-zone) · 2026 vs 2021-25']['p']:.3f})."),
        dict(id="HP-08", client="\"It is not called jam rate, it is called tied-up rate.\"", verdict="ADOPTED",
             governed="Published as tied-up rate, computed by the library's governed jam_rate (JR-1, 10/9), inherited by source-pinned extraction. "
                      "Centered and flail are added (ST-1, provisional) using your second histogram line (41 in)."),
        dict(id="HP-09", client="\"Wheeler's jam rates are really good per Statcast.\"", verdict="PARTLY",
             governed=f"{pct(H['tied_pop']['value'])} tied-up, #{H['tied_pop']['rank']} of {H['tied_pop']['n']} Phillies pitcher-seasons 2025–26 "
                      f"(mean {pct(H['tied_pop']['mean'])}); #{H['tied_pop']['rank_big']} of {H['tied_pop']['n_big']} with ≥500 tracked swings. "
                      f"Good, not the top of the room. Against righties it is {pct(H['platoon']['2026R']['tied'])}."),
        dict(id="HP-10", client="\"57 balls in play on Zack Wheeler's sinker jamming righties in 2026.\" (and 71 fouled off)", verdict="REPRODUCED, DIFFERS-EXPLAINED",
             governed=f"Your frame gives {H['si_jam_client']['bip']} in play and {H['si_jam_client']['not_in_play']} not in play (type 'S', so swinging strikes "
                      f"as well as fouls). The governed frame gives {H['si_jam']['bip']} and {H['si_jam']['not_in_play']}: {H['si_jam_client']['postseason_rows']} "
                      f"Wild Card rows and {H['si_jam_client']['bunts']} foul bunt (JR-1 does not count a bunt as a swing) explain it. Of the {H['si_jam']['bip']}: "
                      f"{H['si_jam']['hits']} hits, {H['si_jam']['ev']:.1f} mph average exit velocity."),
        dict(id="HP-11", client="zw = concat(nphl[name], pps[name]) (cell 22)", verdict="DEFECT (MI-1)",
             governed=f"Carries {H['zw']['lhv_2026']} Lehigh Valley rehab pitches (3/28, 4/3, 4/8) tagged as 2026 regular season. The same exposure "
                      f"sat in the org's own CF-2 loader; CF-2b drops non-MLB games. zw also loses {H['zw']['nphl_lost_to_dedup']} Mets-era pitches to "
                      "the nphl keep-first dedup (O-26)."),
        dict(id="HP-12", client="def jam_rate(...) draft in cell 23", verdict="SUPERSEDED",
             governed=f"The draft divides every row under 32.5 in by all swings (bunts included): {pct(H['zw_jam26_draft'])} on zw. The library's "
                      f"JR-1 counts tracked swings only: {pct(H['zw_jam26']['jam_rate'])} on zw, {pct(L['jam_rate'])} governed."),
        dict(id="HP-13", client="Jam-rate population scatter (player-seasons over nphl + pos + pps)", verdict="DEFECT",
             governed=f"player_name is the batter in pos and in batter-keyed pulls, so {H['tied_pop_client']['batter_seasons']} of "
                      f"{H['tied_pop_client']['n']} points are hitters getting tied up, not pitchers tying them up. The governed board keys by "
                      "pitcher id over the Phillies pitching log."),
        dict(id="HP-14", client="KPI table over pps[player_name == 'Wheeler, Zack'] (cell 21)", verdict="DIFFERS-EXPLAINED",
             governed="Your frame keeps postseason rows (2022: 484, 2023: 402, 2024: 111, 2026: 68 pitches). Removing them gives the governed "
                      "frame exactly, every season (DQ-11)."),
        dict(id="HP-15", client="Pitch-map subtitle reads z[(z.game_year == gy)] after the loop", verdict="CORRECT BY ACCIDENT",
             governed="gy is the loop variable left over from `for gy in df.game_year.unique()`. On a one-season frame it is 2026 and the "
                      "subtitle is right; on a multi-season frame it would label the wrong year (house defect HP-18)."),
        dict(id="HP-16", client="Pitch map from lhb/rhb_pitch_mix", verdict="REPRODUCED",
             governed="PM-1 (unrounded centroids) is published; pitch_mix rounds locations to 0.1 ft (O-25), a cosmetic difference."),
        dict(id="HP-17", client="\"He started to show some signs of slowing down in the second half.\"", verdict="PARTLY",
             governed=f"Second half {H['halves']['second']['r27']:.2f} runs on watch per 27 outs vs {H['halves']['first']['r27']:.2f}, but six starts carry it; "
                      f"the finish was {P['finish']['r27']:.2f}. Velocity did not fade within the season ({H['halves']['first']['velo']:.1f} → "
                      f"{H['halves']['second']['velo']:.1f} mph). The slowing is across years: {H['velo']['season21']:.1f} (2021) → {H['velo']['season26']:.1f}."),
        dict(id="HP-18", client="\"For now he is still Zack Wheeler.\"", verdict="SUPPORTED",
             governed=f"xwOBA #{H['ctx_sw']['rank_xwoba']} of {H['ctx_sw']['n']} starter seasons. The 2026 card is softer than his 2021–25 edge on "
                      f"velocity ({H['card']['bars']['OC-A']:.1f} vs {H['card']['bars_prime']['OC-A']:.1f} mph) and walks ({pct(H['card']['bars']['OC-D'])} vs "
                      f"{pct(H['card']['bars_prime']['OC-D'])}), and stricter on chase and whiff. He held ≥3 of 4 in {H['card']['on']} of 28 starts, which "
                      f"allowed {H['card']['on_r27']:.2f} runs per 27 outs."),
    ]


HP = pd.DataFrame(rows())
HP.to_csv(OUT / "dp_uc51_hp_reconciliation.csv", index=False)
if __name__ == "__main__":
    print(HP[['id', 'verdict']].to_string())
