"""dp_uc53_hp.py - UC #53 HP family. Reproduces each client claim on the CLIENT's frame (pps = every Phillies
pitching row 2015-26, all game types, keyed by player_name) with the client's own functions (K44, CM-1 default),
then sets it beside the governed value from headlines.json. Never overwrites either. Writes out/dp_uc53_hp_grades.csv
and the 'hp' block of headlines.json."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc53_kernel as K

P = lambda n: K.OUT / f"dp_uc53_{n}"
H = json.load(open(P("headlines.json")))
pps = K.load_phils_cols(years=range(2015, 2027), role="pitching", regular_only=False, cols=K.HOUSE_COLS)
pn = K.SUBJECT_NAME
ja = pps[pps.player_name == pn]
assert ja.pitcher.eq(K.SUBJECT_ID).all(), "client name filter picked up another pitcher"
gt = ja.game_type.value_counts().to_dict()
R = []
FY = ("2021", "2022", "2024", "2026")
def row(hp, claim, client, governed, verdict, note):
    R.append(dict(hp=hp, claim=claim, client_method=client, governed=governed, verdict=verdict, note=note))

# HP-01 leaderboard
lb = K.nresults("player_name", pps).sort_values("plate_apps", ascending=False).reset_index(drop=True)
c_rank = int(lb.index[lb.player_name == pn][0] + 1)
L = H["leaderboard"]
row("HP-01", "14th-most PA for the Phillies since 2015; only Neris (full-time RP) has more", f"#{c_rank} ({int(lb.plate_apps[c_rank-1])} PA, all game types)",
    f"#{L['rank']} of {L['n']} ({L['pa']} PA, regular season); RP-1t relievers above: " + ", ".join(f"{r['player_name']} ({r['plate_apps']}, {r['starts']} starts)" for r in L["rp_above"]),
    "Supported (one nuance)", "Rank holds on both frames. Adam Morgan also ranks above him and classifies as a reliever (36 starts in 199 games, under the 20% RP-1 line); Neris is the only one above him with zero starts.")
# HP-02 tenure totals
t = K.nresults("player_name", ja).iloc[0]; T = H["tenure"]
row("HP-02", ".300 wOBA, .668 OPS, 399 strikeouts as a Phillie", f"{t.woba:.3f} / {t.ops:.3f} / {int(t.strikeouts)} K",
    f"{T['woba']:.3f} / {T['ops']:.3f} / {T['strikeouts']} K (regular season)", "Supported (frame restated)",
    f"The client frame folds in {sum(v for k, v in gt.items() if k in K.POSTSEASON_TYPES)} postseason and {gt.get('S', 0)} spring pitches; postseason and spring add {int(t.strikeouts) - T['strikeouts']} K.")
# HP-03 / HP-04
by = K.nresults(["player_name", "game_year"], ja).set_index("game_year")
best = by[by.index >= 2021].woba.nsmallest(2).index.tolist()
row("HP-03", "Best seasons 2022 and 2023; 2023 excellent; 'must have missed time with injury'", f"lowest wOBA: {best} ({by.woba[best[0]]:.3f}, {by.woba[best[1]]:.3f})",
    f"2022 {H['by_year']['2022']['woba']:.3f}, 2023 {H['by_year']['2023']['woba']:.3f} (tenure ranks 1-2); 2023 = {H['outing_bands']['2023']['apps']} games",
    "Supported; injury not inferred", f"The log shows {H['outing_bands']['2023']['apps']} regular-season games in 2023 vs {min(H['outing_bands'][y]['apps'] for y in FY)}-{max(H['outing_bands'][y]['apps'] for y in FY)} in his other full Phillies seasons. Carry-in CI-5 (IL, reinstated 2023-06-09) is reported, not inferred.")
pk = ja[ja.game_year.isin([2022, 2023])]; r = K.nresults("player_name", pk).iloc[0]; PK = H["peak_2022_23"]
row("HP-04", "2022-23: ~35% K, <10% BB, BA just above .200", f"K {r.krate:.1%} / BB {r.bbrate:.1%} / BA {r.ba:.3f}",
    f"K {PK['krate']:.1%} / BB {PK['bbrate']:.1%} (regular season)", "Supported (understated on the regular season)", f"~35% holds on the client frame ({r.krate:.1%}); regular season alone it was {PK['krate']:.1%}.")
# HP-05 cutter, tenure
fc = ja[(ja.pitch_type == "FC") & (ja.game_year >= 2021)]
lv = ["player_name", "pitch_type"]
z = K.nresults(lv, fc).merge(K.putaway_rate(lv, fc), on=lv, how="left", suffixes=("", "_par")).merge(K.whiff_rate(lv, fc), on=lv, how="left").merge(
    K.chase_rate(lv, fc), on=lv, how="left", suffixes=("", "_cr")).iloc[0]
fcg = H["pitch_by_year"]["FC"]
row("HP-05", "Cutter: 28% zone, 38% chase (~1,400 OOZ), ~52% K, 48% whiff, 26% putaway", f"zone {z.in_zone_rate:.1%}, chase {z.chase_rate:.1%} ({int(z.ooz)} OOZ), K {z.krate:.1%}, whiff {z.whiff_rate:.1%}, putaway {z.putaway_rate:.1%}",
    (lambda G: f"zone {G['in_zone']:.1%}, chase {G['chase']:.1%} ({G['ooz']} OOZ), K {G['krate']:.1%}, whiff {G['whiff']:.1%}, putaway {G['putaway']:.1%} (regular season)")(H["fc_tenure"]), "Supported",
    f"Every figure reproduces, including ~1,400 out-of-zone cutters ({int(z.ooz)}). 52% K is K per PA ending on a cutter.")
# HP-06 putaway context (client population)
zc = K.nresults(lv, pps).merge(K.putaway_rate(lv, pps), on=lv, how="left", suffixes=("", "_par"))
zc = zc[zc.pitches2strikes > 19]; me = zc[(zc.player_name == pn) & (zc.pitch_type == "FC")].iloc[0]
c6 = int((zc.putaway_rate > me.putaway_rate).sum() + 1); G6 = H["fc_putaway_house"]
row("HP-06", "Cutter putaway is elite among Phillies pitcher x pitch combos (>=20 two-strike pitches)", f"{me.putaway_rate:.1%}, #{c6} of {len(zc)}",
    f"{G6['value']:.1%}, #{G6['rank']} of {G6['n']} ({G6['pct']['percentile']}th pct) on {G6['pitches2strikes']} two-strike pitches", "Supported (top decile, not top)",
    f"Of the {G6['rank'] - 1} combos above him, the most two-strike pitches any has is {G6['above_max_p2s']}; he threw {G6['pitches2strikes']}. Among combos with 300+ two-strike pitches he ranks #{G6['rank_ge300']} of {G6['n_ge300']}.")
# HP-07 velocity
v = fc.groupby("game_year").release_speed.median()
row("HP-07", "Cutter velocity trending down", " -> ".join(f"{y}: {x:.1f}" for y, x in v.items()),
    f"2026 mean {H['fc_velo']['y2026']:.1f} mph, tenure low; peak {H['fc_velo']['peak']:.1f} ({H['fc_velo']['peak_year']})", "Supported", "Down in four of five year-over-year steps since 2021.")
# HP-08 / HP-09 whiff
lv3 = ["player_name", "pitch_type", "game_year"]
w = K.nresults(lv3, pps)[lv3 + ["pitches"]].merge(K.whiff_rate(lv3, pps), on=lv3, how="left")
w = w[w.pitches > 49]; mw = w[(w.player_name == pn) & (w.pitch_type == "FC")].set_index("game_year").whiff_rate
W = H["fc_whiff_house"]["by_year"]
row("HP-08", "2026 cutter whiff 'fell off a cliff'; hline drawn at 0.39", f"2026 {mw[2026]:.3f} (hline hard-coded 0.39)", f"2026 {W['2026']['whiff']:.3f}, down from {W['2025']['whiff']:.3f} (2025) and {W['2022']['whiff']:.3f} (2022)",
    "Supported; DEF-1 hard-code happens to be right", "The value is now computed and printed, not typed.")
row("HP-09", "Cutter went from among the most elite swing-and-miss pitches to 'just very good'", f"2021 rank {int((w.whiff_rate > mw[2021]).sum() + 1)}, 2026 rank {int((w.whiff_rate > mw[2026]).sum() + 1)} of {len(w)}",
    f"2021 #{W['2021']['rank']}, 2022 #{W['2022']['rank']}, 2026 #{W['2026']['rank']} of {H['fc_whiff_house']['n']} ({W['2026']['pct']['percentile']}th pct)", "Supported", "Still 88th percentile of Phillies pitcher x pitch seasons.")
# HP-10 cumulative
cfc = K.cumulative_frame(ja, "woba").groupby("game_year").value.last()
C = H["cumulative"]
row("HP-10", "2026 'remarkably inconsistent, sometimes reliable' (cumulative wOBA-against chart)", f"2026 final {cfc[2026]:.3f} (module default)",
    f"2026 final {C['final']['2026']:.3f} (CM-1a, = WB-1); clean outings {H['outings_2026']['clean']}/{H['outings_2026']['apps']}, blow-ups {H['outings_2026']['blowups']}",
    "Supported (chart restated: CM-D1)", f"The module's wOBA counts woba_value on {C['cm_d1_rows']} tenure PA ends with woba_denom 0 (IBB, sac bunt), so {sum(C['final_module_default'][y] > C['final'][y] + 1e-12 for y in C['final'])} of {len(C['final'])} season lines ran high.")
g = pd.DataFrame(R); g.to_csv(P("hp_grades.csv"), index=False)
H["hp"] = dict(rows=R, client_frame_game_types={k: int(v) for k, v in gt.items()}, client_cum_final={int(k): float(x) for k, x in cfc.items()})
json.dump(H, open(P("headlines.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(g[["hp", "client_method", "verdict"]].to_string())
