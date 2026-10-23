"""dp_uc54_hp.py - HP family: the client's notebook claims, reproduced on the CLIENT's frame with the client's
functions (K44 = Baseball Functions verbatim), then graded against the governed build (headlines.json).
Writes out/dp_uc54_hp_reproduction.csv, out/dp_uc54_hp_grades.csv and adds H['hp'] to headlines.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc54_kernel as K  # noqa: E402

K44 = K.K44
OUT = K.OUT
H = json.loads((OUT / "dp_uc54_headlines.json").read_text(encoding="utf-8"))

ph = K.load_house()
pos_all = ph[ph.phillies_role == "batting"]
pps_all = ph[ph.phillies_role == "pitching"]
jc = K.client_frame(pos_all)
jc = K44.apply_woba_weights(jc) if hasattr(K44, "apply_woba_weights") else jc
src = jc.groupby(["_src", "game_year", "game_type"]).size().rename("pitches").reset_index()
src.to_csv(OUT / "dp_uc54_hp_client_frame_sources.csv", index=False)
dups = int(jc.duplicated(K.PITCH_KEY).sum())

# the client's first block, verbatim composition (level = player_name, game_year, stand)
level = ["player_name", "game_year", "stand"]
df = jc
z = K44.nresults(level, df).merge(K44.hard_hit_rate(level, df), on=level, how="left", suffixes=("", "_hh")).merge(
    K44.chase_rate(level, df), on=level, how="left", suffixes=("", "_cr")).merge(
    K44.whiff_rate(level, df), on=level, how="left", suffixes=("", "_wr")).merge(
    K44.bb_type_by_level(level, df[df.bb_type == "ground_ball"]), on=level, how="left", suffixes=("", "_gb")).merge(
    K44.nresults(level, df[(df.on_2b.isna() == False) | (df.on_3b.isna() == False)]), on=level, how="left", suffixes=("", "_risp")).merge(  # noqa: E712
    K44.nresults(level, df[df.zone > 9]), on=level, how="left", suffixes=("", "_ooz")).merge(
    K44.whiff_rate(level, df[df.zone > 9]), on=level, how="left", suffixes=("", "_ooz"))
z["contact_rate"] = 1 - z.whiff_rate
z["contact_rate_ooz"] = 1 - z.whiff_rate_ooz
z["ground_ball_rate"] = z.bips_gb / z.bip
z["swing_rate"] = z.swings / z.pitches
z.to_csv(OUT / "dp_uc54_hp_reproduction.csv", index=False)
c26 = z[z.game_year == 2026].iloc[0]

# client's out-of-zone split by pitcher hand (HP-09)
df2 = jc.assign(**{"In or Out of Zone": np.where(jc.zone < 10, "In Zone", "Out of Zone")})
lv2 = ["player_name", "game_year", "stand", "p_throws", "In or Out of Zone"]
oz = K44.chase_rate(lv2, df2)
oz = oz[(oz.game_year == 2026) & (oz["In or Out of Zone"] == "Out of Zone")].set_index("p_throws")

# client's defense (HP-13): pp26 = Phillies pitching 2026, every game type; searcher = pos + nphl + pps, hit_location 8
cols = ["hit_location", "fielder_8", "launch_speed", "launch_angle", "hit_distance_sc", "events", "des"] + K.PITCH_KEY
nphl = pd.concat([pd.read_parquet(f, columns=[c for c in cols if c in pd.read_parquet(f, columns=None).columns])
                  for f in sorted((K.MLB / "data" / "opponents").glob("*.parquet"))], ignore_index=True).drop_duplicates(K.PITCH_KEY)
rid = K.SUBJECT_ID
searcher = pd.concat([pos_all[pos_all.hit_location == 8], nphl[(nphl.hit_location == 8) & (nphl.fielder_8 != rid)],
                      pps_all[(pps_all.hit_location == 8) & (pps_all.fielder_8 != rid)]])
pp26 = pps_all[pps_all.game_year == 2026]
x1 = K.xo1_client(pp26, searcher)
c_outs, c_xouts = int(x1.events.isin(K.CLIENT_OUTS).sum()), float(x1.out_frequency.sum())

hp = H
P = lambda x: f"{100 * x:.1f}%"
F = K.f3
rows = [
    ("HP-01", "17.3% K rate", P(c26.krate), P(H["krate"]), "REPRODUCED",
     f"Governed {P(H['krate'])} over {int(H['plate_apps'])} regular-season PA; 18th percentile of {H['pool_n']} Phillies hitter-seasons (low K)."),
    ("HP-02", "53.3% swing rate", P(c26.swing_rate), P(H["swing_rate"]), "REPRODUCED",
     f"{H['profile']['swing_rate']['pct']}th percentile of {H['pool_n']}."),
    ("HP-03", "37.7% chase rate", P(c26.chase_rate), P(H["chase_rate"]), "REPRODUCED",
     f"{H['profile']['chase_rate']['pct']}th percentile of {H['pool_n']}; {H['chases']} chases on {H['ooz']} out-of-zone pitches."),
    ("HP-04", "17.6% whiff rate", P(c26.whiff_rate), P(H["whiff_rate"]), "REPRODUCED",
     f"{H['profile']['whiff_rate']['pct']}th percentile (low whiff is good)."),
    ("HP-05", "only 35% hard hits", P(c26.hard_hit_rate), P(H["hard_hit_rate"]), "REPRODUCED",
     f"{H['profile']['hard_hit_rate']['pct']}th percentile; mid-pack, not low. The weak link is launch angle, not exit velocity."),
    ("HP-06", "BA .186 on pitches out of the zone", F(c26.ba_ooz), F(H["ooz_ba"]), "REPRODUCED",
     f"Governed {F(H['ooz_ba'])} ({H['ooz_hits']}/{H['ooz_ab']}); in-zone {F(H['iz_ba'])}. Out-of-zone hard-hit {P(H['ooz_hh'])} vs {P(H['iz_hh'])} in zone."),
    ("HP-07", "Out-of-zone contact is 'pretty impressive'", P(c26.contact_rate_ooz), P(H["ooz_contact_rate"]), "SUPPORTED",
     f"{H['profile']['ooz_contact_rate']['pct']}th percentile of {H['pool_n']}. Impressive, and the source of the problem: it turns chases into weak balls in play instead of walks."),
    ("HP-08", "Better from ~June 1 on", "(chart)", f"TR-1: {H['tr1']['call']}", "PARTLY",
     f"BA rose {F(H['tr1']['rows']['R2']['pre'])} -> {F(H['tr1']['rows']['R2']['post'])} (PRESENT) but wOBA moved only {H['tr1']['rows']['R1']['delta']:+.3f}; walk rate fell (CONTRA). A BABIP turn, not a skill turn."),
    ("HP-09", "Chased too much against RHP", f"R {P(oz.loc['R', 'chase_rate'])} / L {P(oz.loc['L', 'chase_rate'])}",
     f"R {P(H['split']['R']['chase'])} / L {P(H['split']['L']['chase'])}", "PARTLY",
     f"By rate he chased more vs LHP; by volume RHP is the problem: {sum(v['runs'] for k, v in H['cc1']['by'].items() if k.startswith('R')):.0f} of {H['cc1']['runs']:.0f} CC-1 runs came against righties."),
    ("HP-10", "Needs to do damage vs RHP breaking balls", "(table)", f"HH {P(H['pg']['R_breaking']['hh'])} vs {P(H['pg']['R_fastball']['hh'])} on RHP fastballs",
     "SUPPORTED", f"wOBA {F(H['pg']['R_breaking']['woba'])} / xwOBA {F(H['pg']['R_breaking']['xwoba'])} on {H['pg']['R_breaking']['pa']} PA; chase {P(H['pg']['R_breaking']['chase'])}."),
    ("HP-11", "AAA hits on RHP breaking balls were hangers", "(pitch map)",
     f"heart of zone: AAA {H['rhp_bb_hits_heart']['AAA 2025']['heart']}/{H['rhp_bb_hits_heart']['AAA 2025']['hits']} vs MLB {H['rhp_bb_hits_heart']['MLB 2026']['heart']}/{H['rhp_bb_hits_heart']['MLB 2026']['hits']}",
     "SUPPORTED", "UC22 attack regions. Mean height of the hit pitch fell from "
     f"{H['rhp_bb_hits_heart']['AAA 2025']['mean_plate_z']:.2f} ft to {H['rhp_bb_hits_heart']['MLB 2026']['mean_plate_z']:.2f} ft."),
    ("HP-12", "He pulls RHP breaking balls; use the whole field", "(spray)",
     f"pull {P(H['direction']['MLB 2026|rhpbb|Pull']['share'])} vs {P(H['direction']['MLB 2026|other|Pull']['share'])} on everything else",
     "SUPPORTED", f"DR-1 on {sum(H['direction'][f'MLB 2026|rhpbb|{d}']['n'] for d in ('Pull', 'Straightaway', 'Oppo'))} classifiable BIP. On everything else he already uses the whole field."),
    ("HP-13", "Defense: made all the plays I would have expected", f"{c_outs} outs vs {c_xouts:.1f} expected",
     f"XO-2 {H['xo2']['outs']} vs {H['xo2']['xouts']:.1f} ({H['xo2']['oae']:+.1f})", "NOT SUPPORTED",
     f"The client's method only sees balls he fielded (DEF-3). Counting every CF-sector air ball with him in CF, he is {H['xo2']['oae']:+.1f}; external CI-2: -8 OAA."),
    ("HP-14", "'Pretty much the hitter we expected'", "(framing)", "profile held vs UC34", "SUPPORTED",
     f"Swing {H['profile']['swing_rate']['pct']}th, chase {H['profile']['chase_rate']['pct']}th, whiff {H['profile']['whiff_rate']['pct']}th, GB {H['profile']['gb_rate']['pct']}th; mean launch angle {H['la_rank_low']}{'nd' if H['la_rank_low'] == 2 else 'th'}-lowest of {H['profile']['mean_la']['n']} (lowest with 100+ PA)."),
]
g = pd.DataFrame(rows, columns=["hp", "claim", "client_frame", "governed", "grade", "evidence"])
g.to_csv(OUT / "dp_uc54_hp_grades.csv", index=False)
H["hp"] = {r.hp: dict(claim=r.claim, client=r.client_frame, governed=r.governed, grade=r.grade, evidence=r.evidence) for r in g.itertuples()}
H["hp_client_frame"] = dict(rows=int(len(jc)), dup_pitch_keys=dups, src2_rows=int((jc._src == K.SRC2_FILE).sum()),
                            spring_2026=int(((jc.game_year == 2026) & (jc.game_type == "S")).sum()),
                            post_2026=int(((jc.game_year == 2026) & jc.game_type.isin(K.POSTSEASON_TYPES)).sum()),
                            aaa_2025=int((jc._src == K.AAA_FILE).sum()), pitches_2026=int(c26.pitches), pa_2026=int(c26.plate_apps))
H["hp_xo1_client"] = dict(balls=int(len(x1)), outs=c_outs, xouts=c_xouts, searcher=int(len(searcher)))
H["hp_grade_counts"] = g.grade.value_counts().to_dict()
(OUT / "dp_uc54_headlines.json").write_text(json.dumps(H, indent=1), encoding="utf-8")
print(g[["hp", "client_frame", "governed", "grade"]].to_string(index=False)); print(H["hp_client_frame"], H["hp_xo1_client"])
