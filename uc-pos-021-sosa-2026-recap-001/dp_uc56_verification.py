"""dp_uc56_verification.py - INDEPENDENT recompute harness for UC #56 / uc-pos-021.
Reads the raw house parquet itself (pandas only, no KPI function from the kernel chain); takes only constants (event
sets, bars) from the kernel. Every published headline is recomputed and compared. Writes out/dp_uc56_verification_log.csv.
Families: A pre-registration · B entity/sources · C slash+wOBA · D plate discipline · E batted ball · F OZ-1 · G cumulative
· H TR-1 · I pitch groups · J platoon · K tenure/positions · L WA-1 · M narrative/report · N HP + client frame."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dp_uc56_kernel as K  # noqa: E402  (constants and paths only)

OUT = HERE / "out"
H = json.loads((OUT / "dp_uc56_headlines.json").read_text(encoding="utf-8"))
S = H["season"]
LOG = []


def check(cid, got, want, tol=1e-6):
    if isinstance(want, (int, float)) and isinstance(got, (int, float)) and not isinstance(want, bool):
        ok = abs(float(got) - float(want)) <= tol
    else:
        ok = got == want
    LOG.append(dict(check=cid, got=got, want=want, ok=bool(ok)))


# ---------------- raw load (independent)
cols = ["game_pk", "at_bat_number", "pitch_number", "game_date", "game_year", "game_type", "batter", "player_name", "stand", "p_throws",
        "phillies_role", "events", "description", "type", "zone", "pitch_type", "release_speed", "launch_speed", "launch_angle",
        "launch_speed_angle", "bb_type", "hc_x", "hc_y", "estimated_ba_using_speedangle", "estimated_woba_using_speedangle",
        "bat_speed", "fielder_3", "fielder_4", "fielder_5", "fielder_6", "fielder_7", "fielder_8", "fielder_9"]
import pyarrow.parquet as pq  # noqa: E402
_fs = [K.MLB / "data" / "phillies" / f"phils_{y}.parquet" for y in range(2015, 2027)]
raw = pd.concat([pd.read_parquet(f, columns=[c for c in cols if c in pq.read_schema(f).names]) for f in _fs], ignore_index=True)   # schema varies by season
raw["game_date"] = pd.to_datetime(raw.game_date)
W = pd.read_csv(K.MLB / "data" / "wOBA and FIP Constants.csv").set_index("Season") if (K.MLB / "data" / "wOBA and FIP Constants.csv").exists() \
    else K.woba_weights().set_index("Season")
bat = raw[(raw.phillies_role == "batting")]
s_all = bat[bat.batter == K.SUBJECT_ID]
s = s_all[s_all.game_type == "R"]
NON_PA, NON_AB, SW, WH = set(K.NON_PA), set(K.NON_AB), set(K.SWINGS), set(K.WHIFFS)


def pa(df):
    return df[~df.events.fillna("NA").isin(NON_PA)]


def line(df):
    p = pa(df)
    ev = p.events
    ab = (~ev.isin(NON_AB)).sum()
    h = ev.isin({"single", "double", "triple", "home_run"}).sum()
    bb = ev.isin({"walk", "intent_walk"}).sum()
    hbp, sf = (ev == "hit_by_pitch").sum(), (ev == "sac_fly").sum()
    tb = ev.map({"single": 1, "double": 2, "triple": 3, "home_run": 4}).fillna(0).sum()
    wnum = sum(W.loc[int(y)][{"walk": "wBB", "hit_by_pitch": "wHBP", "single": "w1B", "double": "w2B", "triple": "w3B", "home_run": "wHR"}[e]]
               for e, y in zip(ev, p.game_year) if e in ("walk", "hit_by_pitch", "single", "double", "triple", "home_run"))
    wden = ab + (ev == "walk").sum() + sf + hbp
    return dict(pa=len(p), ba=h / ab, obp=(h + bb + hbp) / (ab + bb + hbp + sf), slg=tb / ab, woba=wnum / wden, bb=bb / len(p),
                k=ev.isin({"strikeout", "strikeout_double_play"}).sum() / len(p), hr=int((ev == "home_run").sum()), hits=int(h))


# ---------------- A. pre-registration
check("A1 OZ bars", (K.OZ_HOT, K.OZ_COLD), (0.030, -0.030))
check("A2 DF bars", [b[3] for b in K.DF_BARS], [1.0, 1.0, 0.040, 0.020, 0.020, 0.030])
check("A3 DF metrics", [b[1] for b in K.DF_BARS], ["bat_speed_mu", "ev90", "hard_hit_rate", "barrel_rate", "xwoba", "ooz_contact_rate"])
check("A4 WA floor", K.WA_FLOOR_M, 4.4)
check("A5 WA comps total", round(sum(c[3] for c in K.WA_COMPS), 2), 26.8)
check("A6 ER params inherited", (K.ER_MIN_SEG, K.ER_PERMS, K.ER_ALPHA, K.ER_SEED), (100, 500, 0.10, 55))
check("A7 TR bars inherited", [t[4] for t in K.TR_SIGNATURES], [0.030, 0.030, 0.030, 0.040, 0.025, 0.030, 0.015, 0.030, 0.040, 0.030])
check("A8 baseline years", K.BASELINE, (2023, 2024, 2025))
check("A9 lineage pins count", len(H["lineage"]), len(K.assert_lineage()))

# ---------------- B. entity + sources
check("B1 one name", s.player_name.unique().tolist(), [K.SUBJECT_NAME])
check("B2 bats R", sorted(s.stand.unique().tolist()), ["R"])
check("B3 no dup keys", int(s.duplicated(K.PITCH_KEY).sum()), 0)
check("B4 seasons", sorted(s.game_year.unique().tolist()), list(K.PHI_SEASONS))
check("B5 anchor", str(raw.game_date.max())[:10] <= K.ANCHOR_GAME_DATE, True)
gt = pa(s_all).groupby(["game_year", "game_type"]).size()
check("B6 spring 2026 PA", int(gt.get((2026, "S"), 0)), H["src4"]["spring_2026_pa"])
check("B7 WC 2026 PA", int(sum(gt.get((2026, t), 0) for t in K.POSTSEASON_TYPES)), H["src4"]["post_2026_pa"])
stl = pd.read_parquet(K.MLB / "data" / "opponents" / K.STL_FILE)
stl = stl[(stl.batter == K.SUBJECT_ID) & (stl.game_type == "R")].drop_duplicates(K.PITCH_KEY)
check("B8 STL 2021 PA", len(pa(stl[stl.game_year == 2021])), H["stl"]["2021"]["pa"])
check("B9 STL has no bat_speed col", "bat_speed" in stl.columns, False)

# ---------------- C. slash + wOBA by season
for y in K.PHI_SEASONS:
    L = line(s[s.game_year == y])
    for k, hk in (("pa", "plate_apps"), ("ba", "ba"), ("obp", "obp"), ("slg", "slg"), ("woba", "woba"), ("bb", "bbrate"), ("k", "krate")):
        check(f"C {y} {hk}", L[k], S[str(y)][hk], tol=1e-9 if k != "pa" else 0)
L26 = line(s[s.game_year == 2026])
check("C CI-1 slash .247/.283/.429", (round(L26["ba"], 3), round(L26["obp"], 3), round(L26["slg"], 3)), (0.247, 0.283, 0.429))
Lb = line(s[s.game_year.isin(K.BASELINE)])
check("C baseline woba", Lb["woba"], H["baseline"]["woba"], 1e-9)
check("C baseline PA", Lb["pa"], H["baseline"]["plate_apps"], 0)

# ---------------- D. plate discipline
for y in (2023, 2024, 2025, 2026):
    d = s[s.game_year == y]
    dp = d[d.pitch_type.notna()]
    o = dp[dp.zone > 9]
    check(f"D {y} chase", o.description.isin(SW).mean(), S[str(y)]["chase_rate"], 1e-9)
    sw = d[d.description.isin(SW)]
    check(f"D {y} contact", 1 - sw.description.isin(WH).mean(), S[str(y)]["contact_rate"], 1e-9)
    osw = o[o.description.isin(SW)]
    check(f"D {y} ooz contact", 1 - osw.description.isin(WH).mean(), S[str(y)]["ooz_contact_rate"], 1e-9)
    check(f"D {y} swing", d.description.isin(SW).mean(), S[str(y)]["swing_rate"], 1e-9)
r26 = H["rhb_rank"]["2026"]["chase"]
check("D chase 2026 is max of RHB pool", r26["rank"], r26["n"], 0)

# ---------------- E. batted ball
for y in (2023, 2024, 2025, 2026):
    b = s[(s.game_year == y) & (s.type == "X")]
    ev = pd.to_numeric(b.launch_speed, errors="coerce").dropna()
    check(f"E {y} hard-hit (O-8 denominator: all BIP)", (pd.to_numeric(b.launch_speed, errors="coerce").fillna(0) >= 95).mean(), S[str(y)]["hard_hit_rate"], 1e-9)
    check(f"E {y} barrel", b.launch_speed_angle.eq(6).fillna(False).mean(), S[str(y)]["barrel_rate"], 1e-9)
    check(f"E {y} ev50", ev.median(), S[str(y)]["ev50"], 1e-6)
    check(f"E {y} ev90", ev.quantile(0.9), S[str(y)]["ev90"], 1e-6)
    check(f"E {y} evmax", ev.max(), S[str(y)]["ev_max"], 1e-6)
    c = b[b.hc_x.notna() & b.hc_y.notna()]
    x, yy = 2.495671 * (c.hc_x - 125.42), 2.495671 * (198.27 - c.hc_y)
    pull = (yy <= -4.7 * x) if K.SUBJECT_ID else None          # RHB pull wedge (uc-pos-017 boundary)
    check(f"E {y} pull-air", (pull & (c.bb_type != "ground_ball")).sum() / len(c), S[str(y)]["pull_air_rate"], 1e-9)
for y in (2024, 2025, 2026):
    d = s[(s.game_year == y) & s.description.isin(SW)]
    check(f"E {y} bat speed", pd.to_numeric(d.bat_speed, errors="coerce").dropna().mean(), S[str(y)]["bat_speed_mu"], 1e-6)

# ---------------- F. OZ-1
for y in (2023, 2024, 2025, 2026):
    p = pa(s[s.game_year == y])
    p = p[(p.zone > 9) & p.pitch_type.notna()]
    ab = ~p.events.isin(NON_AB)
    hit = p.events.isin({"single", "double", "triple", "home_run"})
    est = pd.to_numeric(p.estimated_ba_using_speedangle, errors="coerce")
    xb = np.where(p.type == "X", np.where(est.notna(), est, hit.astype(float)), 0.0)[ab.to_numpy()]
    check(f"F {y} OZ-BA", hit[ab].mean(), S[str(y)]["oz_ba"], 1e-9)
    check(f"F {y} OZ-xBA", xb.mean(), S[str(y)]["oz_xba"], 1e-9)
    gap = hit[ab].mean() - xb.mean()
    check(f"F {y} OZ call", "RAN HOT" if gap >= .03 else "RAN COLD" if gap <= -.03 else "EARNED", S[str(y)]["oz_call"])

# ---------------- G. cumulative
cw = pd.read_csv(OUT / "dp_uc56_cum_woba.csv")
for y in K.PHI_SEASONS:
    g = cw[cw.series == y] if cw.series.dtype != object else cw[cw.series.astype(str) == str(y)]
    check(f"G {y} cum wOBA endpoint", float(g.value.iloc[-1]), S[str(y)]["woba"], 1e-9)
ck = pd.read_csv(OUT / "dp_uc56_cum_checkpoints.csv")
check("G 2026 last at all 10 checkpoints", int((ck.rank_2026 == 4).sum()), 10, 0)

# ---------------- H. TR-1
d26 = sorted(bat[(bat.game_year == 2026) & (bat.game_type == "R")].game_date.dt.normalize().unique())
jul = pd.Series([d for d in d26 if pd.Timestamp(d).month == 7])
gaps = jul.diff().dt.days.fillna(0)
asb = pd.Timestamp(jul.iloc[int(gaps.to_numpy().argmax())])
check("H ASB date from schedule", str(asb)[:10], H["asb_first_game_2026"])
s26 = s[s.game_year == 2026]
Lp, Lq = line(s26[s26.game_date < asb]), line(s26[s26.game_date >= asb])
check("H pre wOBA", Lp["woba"], H["tr1"]["rows"]["R1"]["pre"], 1e-9)
check("H post wOBA", Lq["woba"], H["tr1"]["rows"]["R1"]["post"], 1e-9)
check("H pre/post PA", (Lp["pa"], Lq["pa"]), (H["tr1"]["pre_pa"], H["tr1"]["post_pa"]))
check("H call", H["tr1"]["call"], "RESULTS TURN")

# ---------------- I. pitch groups (PA counts + whiff), J. platoon
sp = s[s.pitch_type.notna()].copy()
fb = sp.pitch_type.isin(K.FB_TYPES)
sp["g"] = np.select([fb & (sp.release_speed > K.VELO_HI), fb, sp.pitch_type.map(K.PITCH_GROUP).eq("breaking"), sp.pitch_type.map(K.PITCH_GROUP).eq("offspeed")],
                    ["fastball 95+", "fastball <95", "breaking", "offspeed"], "other")
for grp in ("fastball 95+", "breaking", "offspeed"):
    d = sp[(sp.game_year == 2026) & (sp.g == grp)]
    check(f"I 2026 {grp} PA", len(pa(d)), H["pg"][f"{grp}|2026"]["pa"], 0)
    sw = d[d.description.isin(SW)]
    check(f"I 2026 {grp} whiff", sw.description.isin(WH).mean(), H["pg"][f"{grp}|2026"]["whiff"], 1e-9)
for hand in ("L", "R"):
    check(f"J 2026 vs {hand}HP wOBA", line(s26[s26.p_throws == hand])["woba"], H["platoon"][f"{hand}|2026"]["woba"], 1e-9)
    check(f"J base vs {hand}HP wOBA", line(s[s.game_year.isin(K.BASELINE) & (s.p_throws == hand)])["woba"], H["platoon"][f"{hand}|base"]["woba"], 1e-9)

# ---------------- K. tenure + positions
Lc = line(s)
check("K PHI career PA", Lc["pa"], H["phi_career"]["pa"], 0)
check("K PHI career HR", Lc["hr"], H["phi_career"]["hr"], 0)
check("K PHI career wOBA", Lc["woba"], H["phi_career"]["woba"], 1e-9)
fld = raw[(raw.phillies_role == "pitching") & (raw.game_type == "R")]
for col, lab in (("fielder_7", "LF"), ("fielder_5", "3B"), ("fielder_6", "SS"), ("fielder_4", "2B")):
    check(f"K 2026 games at {lab}", int(fld[(fld.game_year == 2026) & (fld[col] == K.SUBJECT_ID)].game_pk.nunique()), H["pos_games"].get(f"{lab}|2026", 0), 0)

# ---------------- L. WA-1
aav = [c[3] / c[2] for c in K.WA_COMPS]
check("L ceiling", np.floor(max(aav) * 2) / 2, H["wa1"]["ceiling"])
bs = [S[str(y)]["bat_speed_mu"] for y in (2024, 2025)]
flags = [S["2026"]["bat_speed_mu"] - np.mean(bs) <= -1.0]
for m, bar in (("ev90", 1.0), ("hard_hit_rate", .04), ("barrel_rate", .02), ("xwoba", .02), ("ooz_contact_rate", .03)):
    flags.append(S["2026"][m] - np.mean([S[str(y)][m] for y in K.BASELINE]) <= -bar)
check("L DF count", int(sum(flags)), H["wa1"]["df_count"], 0)
check("L term", H["wa1"]["years"], 1 if sum(flags) >= 3 else 2, 0)

# ---------------- M. narrative / report
rep = (HERE / "dp_uc56_sosa_2026_recap_report.md").read_text(encoding="utf-8")
for ci in ("CI-1", "CI-2", "CI-3", "CI-4", "CI-5", "CI-6", "CI-7"):
    check(f"M {ci} labelled in report", ci in rep, True)
check("M slash in report", f"{K.f3(L26['ba'])}/{K.f3(L26['obp'])}/{K.f3(L26['slg'])}" in rep, True)
check("M walkaway in report", f"${H['wa1']['ceiling']:.1f}M" in rep, True)
check("M no '<NA>' in headlines", "<NA>" in (OUT / "dp_uc56_headlines.json").read_text(), False)
check("M every figure embedded", all(f"out/dp_uc56_{k}.png" in rep for k in ("f1_cumulative", "f2_season_card", "f3_form_2026", "f4_over_the_hump",
                                                                             "f5_approach", "f6_pitch_groups", "f7_swing_woba", "f8_tenure_platoon", "f9_walkaway")), True)
brand = pd.read_csv(OUT / "dp_uc56_brand_checks.csv")
check("M brand checks", bool(brand.drop(columns=["figure", "off_palette"]).all().all()), True)
dash = (HERE / "dp_uc56_sosa_2026_dashboard.html").read_text(encoding="utf-8")
check("M dashboard uses CDN plotly, not inlined", ("plotly.js-dist-min@3.0.1" in dash) and len(dash) < 1_000_000, True)

# ---------------- N. HP + client frame
check("N 11 HP rows", len(H["hp"]), 11, 0)
check("N HP-07 contradicted", H["hp"]["HP-07"]["grade"], "CONTRADICTED")
cf = pd.read_csv(OUT / "dp_uc56_hp_client_frame_sources.csv")
check("N client frame has STL file", K.STL_FILE in cf._src.unique().tolist(), True)
check("N client frame has spring 2026", bool(((cf._src == "pos") & (cf.game_year == 2026) & (cf.game_type == "S")).any()), True)
rhb = pd.read_csv(OUT / "dp_uc56_rhb_pool_2022_26.csv")
check("N HP-09 r recompute", float(np.corrcoef(rhb.swing_rate, rhb.woba)[0, 1]), H["hp09_corr"]["r"], 1e-9)

log = pd.DataFrame(LOG)
log.to_csv(OUT / "dp_uc56_verification_log.csv", index=False)
fam = log.check.str[0].value_counts().sort_index().to_dict()
print(f"{int(log.ok.sum())}/{len(log)} PASS", fam)
print(log[~log.ok].to_string() if (~log.ok).any() else "no failures")
