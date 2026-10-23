"""dp_uc56_hp.py - HP family: the client's notebook claims, reproduced on the CLIENT's frame with the client's functions
(K44 = Baseball Functions verbatim; barrel_rate.py; `inds` by IX-1 extraction), then graded against the governed build
(headlines.json). Writes out/dp_uc56_hp_*.csv and adds H['hp'] to headlines.json."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc56_kernel as K  # noqa: E402
from barrel_rate import barrel_rate  # noqa: E402  (pinned in K56 PIN)

K44, OUT, P = K.K44, K.OUT, K.P
H = json.loads((OUT / f"{P}headlines.json").read_text(encoding="utf-8"))
_cwd = os.getcwd()
os.chdir(K.MLB)                                            # IX-1 extract reads the notebook from the data-plane root
inds = K.K51.extract("Baseball Functions.ipynb", ["inds"])["inds"]
os.chdir(_cwd)

ph = K.load_house()
pos = ph[ph.phillies_role == "batting"]
pn, gy = K.SUBJECT_NAME, 2026
df = K.client_frame(pos, pn)                               # nphl + pos, no game_type filter (SRC-4, SRC-5)
df = K44.apply_woba_weights(df) if hasattr(K44, "apply_woba_weights") else df
src = df.groupby(["_src", "game_year", "game_type"]).size().rename("pitches").reset_index()
src.to_csv(OUT / f"{P}hp_client_frame_sources.csv", index=False)


def client_block(level, df):
    """The notebook's merge chain, verbatim (suffixes included; pull_air_rate stays commented out as in the notebook)."""
    z = K44.nresults(level, df
                     ).merge(K44.hard_hit_rate(level, df), on=level, how="left", suffixes=("", "_hh")
                             ).merge(K44.chase_rate(level, df), on=level, how="left", suffixes=("", "_cr")
                                     ).merge(K44.whiff_rate(level, df), on=level, how="left", suffixes=("", "_wr")
                                             ).merge(barrel_rate(level, df), on=level, how="left", suffixes=("", "_br")
                                                     ).merge(inds(level, df), on=level, how="left", suffixes=("", "_inds")
                                                             ).merge(K44.nresults(level, df[df.zone > 9]), on=level, how="left", suffixes=("", "_ooz")
                                                                     ).merge(K44.whiff_rate(level, df[df.zone > 9]), on=level, how="left", suffixes=("", "_ooz"))
    z["contact_rate"] = 1 - z.whiff_rate
    z["contact_rate_ooz"] = 1 - z.whiff_rate_ooz
    z["swing_rate"] = z.swings / z.pitches
    return z


level = ["player_name", "game_year", "stand"]
KPIS = ["pitches", "plate_apps", "ba", "obp", "slg", "ops", "woba", "bbrate", "krate", "swing_rate", "contact_rate", "chase_rate",
        "whiff_rate", "hard_hit_rate", "barrel_rate", "ev_mu", "contact_rate_ooz", "ba_ooz"]
z = client_block(level, df)
z1 = z[z.game_year > gy - 5][level + [k for k in KPIS if k in z.columns]].round(3)
z1.to_csv(OUT / f"{P}hp_reproduction_by_year.csv", index=False)
missing = [k for k in KPIS if k not in z.columns]
c = z1.set_index("game_year")

# the client's scatter frame: pos[pos.stand == 'R'], every game type, game_year > gy-5, every hitter-season (no PA floor)
dfc = pos[pos.stand == "R"]
zc = client_block(level, dfc)
zc = zc[zc.game_year > gy - 5]
zc.to_csv(OUT / f"{P}hp_reproduction_rhb_scatter.csv", index=False)
r_client = float(np.corrcoef(zc.swing_rate.astype(float), zc.woba.astype(float))[0, 1])
zc50 = zc[zc.plate_apps >= 50]
r_client50 = float(np.corrcoef(zc50.swing_rate.astype(float), zc50.woba.astype(float))[0, 1])

S, F, Pc = H["season"], K.f3, (lambda x: f"{100 * x:.1f}%")
T, PG, PB = H["tr1"], H["pg"], H["pg_base"]
rk = H["rhb_rank"]
rows = [
    ("HP-01", "2026 top-line 'should be below his results from prior years with the Phillies'",
     f"wOBA 2026 {F(c.loc[2026, 'woba'])} vs 2025 {F(c.loc[2025, 'woba'])} (client frame, incl. spring + WC)",
     f"wOBA {F(S['2026']['woba'])} (4th of 2023-26), OPS {F(S['2026']['ops'])}, OBP {F(S['2026']['obp'])}; but xwOBA {F(S['2026']['xwoba'])} is his best Phillies season",
     "SUPPORTED (results)", "Results were his worst full Phillies season; the expected line was his best. A results-down year, not a skills-down year."),
    ("HP-02", "Cumulative wOBA/OPS 'highlighting 2026 as a down year overall'",
     "client frame: n/a (the notebook drew no cumulative chart)",
     f"2026 last of 2023-26 at {int(100 * H['cum_2026_last_of_4_share'])}% of 50-PA checkpoints (wOBA and OPS, 50-250 PA)",
     "SUPPORTED", "The 2026 line never rose above any prior full Phillies season at any checkpoint."),
    ("HP-03", "'An uptick in performance throughout the year'",
     "client frame: n/a", f"TR-1 at the break ({H['asb_first_game_2026']}): wOBA {F(T['rows']['R1']['pre'])} -> {F(T['rows']['R1']['post'])}, "
     f"xwOBA {F(T['rows']['P1']['pre'])} -> {F(T['rows']['P1']['post'])}; call {T['call']}; ER-1: no 2026 change point",
     "RESULTS ONLY", "Results turned; process did not (xwOBA, K%, hard-hit and whiff all moved the wrong way). The first half was unlucky, the second half less so."),
    ("HP-04", "'A high-chase and high-contact guy'",
     f"chase {Pc(c.loc[2026, 'chase_rate'])}, contact {Pc(c.loc[2026, 'contact_rate'])}, OOZ contact {Pc(c.loc[2026, 'contact_rate_ooz'])} (client frame)",
     f"chase {Pc(S['2026']['chase_rate'])} = highest of {rk['2026']['chase']['n']} Phillies RHB seasons 2022-26; contact {Pc(S['2026']['contact_rate'])} "
     f"({rk['2026']['contact']['percentile']}th pct); OOZ contact {Pc(S['2026']['ooz_contact_rate'])} ({rk['2026']['ooz_contact']['percentile']}th pct)",
     "PARTLY", "High chase, yes - the highest in the pool. High contact only out of the zone; overall contact is below the RHB median."),
    ("HP-05", "OOZ contact and OOZ BA - 'are those sustainable?'",
     f"OOZ BA {F(c.loc[2026, 'ba_ooz'])} (client frame)" if "ba_ooz" in c.columns else "client ba_ooz: column absent (merge suffix)",
     f"OZ-1 2026: OZ-BA {F(S['2026']['oz_ba'])} vs OZ-xBA {F(S['2026']['oz_xba'])} -> {S['2026']['oz_call']}; OOZ contact above RHB median "
     f"({Pc(H['rhb_ooz_contact_median'])}); CC-1 {H['cc1']['2026']['per100']:.1f} runs per 100 chases vs RHB median {H['cc1_rhb_median_per100']:.1f}",
     "SUSTAINABLE", "His out-of-zone damage is earned (it ran slightly cold in 2026). Each chase costs less than a typical RHB's; he just chases far more often."),
    ("HP-06", "'Has he fallen off against velocity'",
     "client frame: not computed in this notebook",
     f"95+ fastballs 2026: wOBA {F(PG['fastball 95+|2026']['woba'])} vs {F(PB['fastball 95+']['woba'])} (2023-25); xwOBA {F(PG['fastball 95+|2026']['xwoba'])} vs "
     f"{F(PB['fastball 95+']['xwoba'])}; whiff {Pc(PG['fastball 95+|2026']['whiff'])} vs {Pc(PB['fastball 95+']['whiff'])} (p={PB['fastball 95+']['whiff_p_vs_2026']:.2f})",
     "NOT SUPPORTED (process)", f"Results against 95+ fell; whiffs fell too and xwOBA matched his pooled 2023-25 line, though it sits below 2024-25 ({F(PG['fastball 95+|2024']['xwoba'])}, {F(PG['fastball 95+|2025']['xwoba'])}): a watch item. 43 PA."),
    ("HP-07", "'Previously strong against breaking balls but not so much now'",
     "client frame: not computed in this notebook",
     f"breaking 2023-25: wOBA {F(PB['breaking']['woba'])}, whiff {Pc(PB['breaking']['whiff'])}; 2026: xwOBA {F(PG['breaking|2026']['xwoba'])}, whiff {Pc(PG['breaking|2026']['whiff'])}",
     "CONTRADICTED", "He was never strong against breaking balls, and 2026 was his best expected year against them. Offspeed is where he swings and misses "
     f"(whiff {Pc(PG['offspeed|2026']['whiff'])}, chase {Pc(PG['offspeed|2026']['chase'])})."),
    ("HP-08", "'Edmundo swung the bat and had high wOBAs among Phillies RHB'",
     f"client scatter: {len(zc)} RHB-seasons (no PA floor, every game type)",
     "swing-rate pct by season: " + ", ".join(f"{y} {rk[y]['swing']['percentile']}" for y in sorted(rk)) + "; wOBA pct: " +
     ", ".join(f"{y} {rk[y]['woba']['percentile']}" for y in sorted(rk)) + f" (n={rk['2026']['woba']['n']})",
     "PARTLY", "He always swung (top quartile every season). His wOBA was above the RHB median only in 2022 (59 PA) and 2025."),
    ("HP-09", "'The Phillies put a premium on right handed hitters who swing the bat'",
     f"client scatter r = {r_client:.2f} (all rows); {r_client50:.2f} at >=50 PA",
     f"house pool (RHB 2022-26, >=50 PA, n={H['hp09_corr']['n']}): r = {H['hp09_corr']['r']:.2f}; PA-weighted {H['hp09_corr']['r_pa_weighted']:.2f}",
     "NOT VISIBLE IN OUTCOMES", "A preference can't be graded from the log; the outcome link it implies is weak in this pool."),
    ("HP-10", "'Reliable bench player going back to 2022 ... a true positive force'",
     "client frame: n/a",
     f"Phillies 2022-26: {H['phi_career']['pa']} PA, {F(H['phi_career']['ba'])}/{F(H['phi_career']['obp'])}/{F(H['phi_career']['slg'])}, wOBA {F(H['phi_career']['woba'])} "
     f"= {H['tenure_board']['woba_rank']} of {H['tenure_board']['n']} Phillies with >=800 PA ({H['tenure_board']['rhb_woba_rank']} of {H['tenure_board']['rhb_n']} RHB)",
     "SUPPORTED", "Carry-in bWAR 0.8 / 0.6 / 2.2 / 2.3 / 1.0 (CI-4); four positions in 2026."),
    ("HP-11", "'The Phillies should not pay him like an everyday player'",
     "client frame: n/a",
     f"vs RHP wOBA {F(H['platoon']['R|base']['woba'])} (2023-25), {F(H['platoon']['R|2026']['woba'])} (2026) vs RHB pool {F(H['rhb_platoon_woba']['R'])}; "
     f"BB% {Pc(S['2026']['bbrate'])} ({H['card_better']['2026']['bbrate']:.0f}th pct); WA-1 walkaway ${H['wa1']['ceiling']:.1f}M AAV, {H['wa1']['term']} (DF {H['wa1']['df_count']}/6)",
     "SUPPORTED", "He crushes lefties and is a below-average bat against righties, with almost no walks. That is a bench/platoon profile."),
]
g = pd.DataFrame(rows, columns=["hp", "claim", "client_frame", "governed", "grade", "note"])
g.to_csv(OUT / f"{P}hp_grades.csv", index=False)
H["hp"] = {r.hp: dict(claim=r.claim, client=r.client_frame, governed=r.governed, grade=r.grade, note=r.note) for r in g.itertuples()}
H["hp_client"] = dict(r=r_client, r50=r_client50, n=int(len(zc)), missing=missing,
                      woba26=float(c.loc[2026, "woba"]), ev_mu26=float(c.loc[2026, "ev_mu"]), pa26=int(c.loc[2026, "plate_apps"]),
                      sources={f"{r._1}|{r.game_year}|{r.game_type}": int(r.pitches) for r in src.itertuples()})
(OUT / f"{P}headlines.json").write_text(json.dumps(H, indent=1), encoding="utf-8")
print(g[["hp", "grade"]].to_string(index=False)); print("missing", missing); print(z1.to_string())
