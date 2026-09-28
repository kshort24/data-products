"""
dp_uc49_verification.py — independent harness for UC #49 / uc-pps-034.

Different code path from the build: it does NOT import dp_uc49_kernel, dp_uc48_kernel or dp_uc44_kernel for any
computation (only to hash them). It re-reads the parquet data plane with pyarrow, rebuilds the career frame by its own
dedup, recomputes every headline and then checks the receipts, the report prose and the dashboard against it.

Families:  A lineage · B career frame · C context & percentiles · D Labor Day · E season arc, game scores, postseason,
           October card · F published numbers (report + dashboard) · G carry-in discipline
Run:  PYTHONPATH=/tmp/pyl MLB_DATA_ROOT=<MLB> PKG_DIR=<control-plane folder> python3 dp_uc49_verification.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(os.environ.get("MLB_DATA_ROOT", Path(__file__).resolve().parent))
OUT = ROOT / "out"
PKG = Path(os.environ.get("PKG_DIR", ROOT))
ID = 666200
LOG = []


def chk(fam, name, ok, observed="", expected=""):
    LOG.append(dict(family=fam, check=name, result="PASS" if bool(ok) else "FAIL", observed=str(observed)[:160],
                    expected=str(expected)[:160]))


def close(a, b, tol=1e-3):
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol


sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()   # noqa: E731
H = json.loads((OUT / "dp_uc49_headlines.json").read_text())
Rc = lambda n: pd.read_csv(OUT / f"dp_uc49_{n}.csv")                 # noqa: E731

# ---------------------------------------------------------------- A · lineage
chk("A", "dp_uc44_kernel sha256 pinned", sha(ROOT / "dp_uc44_kernel.py").startswith("a2c119096db2"))
chk("A", "dp_uc48_kernel sha256 pinned", sha(ROOT / "dp_uc48_kernel.py").startswith("0f63857a1032"))
k49 = sha(ROOT / "dp_uc49_kernel.py")
chk("A", "dp_uc49_kernel present and hashed", len(k49) == 64, k49[:12])
chk("A", "anchor 2026-09-26", H["anchor"] == "2026-09-26", H["anchor"])
chk("A", "DQ scorecard has 0 FAIL", (Rc("dq_scorecard").result != "FAIL").all(), Rc("dq_scorecard").result.value_counts().to_dict())

# ---------------------------------------------------------------- B · career frame, rebuilt independently
KEY = ["game_pk", "at_bat_number", "pitch_number"]
NEED = KEY + ["pitcher", "game_year", "game_type", "game_date", "events", "description", "zone", "balls", "strikes",
              "pitch_type", "release_speed", "n_thruorder_pitcher", "stand", "inning", "bat_score", "post_bat_score",
              "batter", "des", "phillies_role", "player_name", "pfx_x", "plate_x", "plate_z", "type", "home_team"]


def rd(f):
    have = set(pq.read_schema(f).names)
    return pd.read_parquet(f, columns=[c for c in NEED if c in have])


ph = pd.concat([rd(ROOT / "data" / "phillies" / f"phils_{y}.parquet") for y in range(2015, 2027)], ignore_index=True)
chk("B", "Phillies log max regular-season date == anchor",
    str(ph[(ph.game_type == "R") & (ph.game_year == 2026)].game_date.max())[:10] == H["anchor"])
parts = [ph[ph.pitcher == ID].assign(_p=np.where(ph[ph.pitcher == ID].phillies_role == "pitching", 0, 3))]
files = sorted((ROOT / "data" / "opponents").glob("*.parquet"))
hitfiles = []
for f in files:
    d = pd.read_parquet(f, columns=["pitcher"])
    if (d.pitcher == ID).any():
        hitfiles.append(f.name)
        x = rd(f)
        parts.append(x[x.pitcher == ID].assign(_p=1 if f.name == "luzardo.parquet" else 2))
chk("B", "id scan: 21 opponent files hold his pitches", len(hitfiles) == H["opp_files_with_subject"] == 21, len(hitfiles))
raw = pd.concat(parts, ignore_index=True)
allf = raw.sort_values("_p").drop_duplicates(KEY)
L = allf[allf.game_type == "R"].copy()
LP = allf[allf.game_type.isin(["F", "D", "L", "W"])].copy()
chk("B", "career regular-season pitches == 14,426", len(L) == H["career_pitches"] == 14426, len(L))
chk("B", "duplicates removed across sources == 1,188", len(raw[raw.game_type == "R"]) - len(L) == H["dup_removed"], len(raw[raw.game_type == 'R']) - len(L))
chk("B", "postseason pitches == 380 in 6 games", len(LP) == 380 and LP.game_pk.nunique() == 6, (len(LP), LP.game_pk.nunique()))
chk("B", "no rows added by batter-keyed files beyond PHI+FILE", (allf[allf._p == 2].shape[0]) == 0, allf[allf._p == 2].shape[0])
chk("B", "throws L on every row (pfx_x of FF > 0 in 2026)", L[(L.game_year == 2026) & (L.pitch_type == "FF")].pfx_x.mean() > 0)
chk("B", "2026: 29 games, 2,860 pitches, last 2026-09-07", L[L.game_year == 2026].game_pk.nunique() == 29 and
    (L.game_year == 2026).sum() == 2860 and str(L[L.game_year == 2026].game_date.max())[:10] == "2026-09-07")

SW = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WH = ["foul_tip", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]


def rates(d):
    pa = (~d.events.fillna("NA").isin(["NA", "pickoff_1b"])).sum()
    k = d.events.isin(["strikeout", "strikeout_double_play"]).sum()
    bb = (d.events == "walk").sum()
    sw = d.description.isin(SW).sum(); wh = d.description.isin(WH).sum()
    ooz = (d.zone > 9).sum(); ch = ((d.zone > 9) & d.description.isin(SW)).sum()
    tr = d.zone.notna().sum(); iz = d.zone.between(1, 9).sum()
    return dict(pa=int(pa), k=int(k), bb=int(bb), krate=k / pa, bbrate=bb / pa, whiff=wh / sw, chase=ch / ooz, inzone=iz / tr,
                sw=int(sw), wh=int(wh), ooz=int(ooz), ch=int(ch), games=d.game_pk.nunique())


RG = Rc("recap_governed").set_index("game_year")
for y in range(2019, 2027):
    r = rates(L[L.game_year == y])
    g = RG.loc[y]
    chk("B", f"{y} PA", r["pa"] == g.plate_apps, r["pa"], g.plate_apps)
    chk("B", f"{y} K rate", close(r["krate"], g.krate, 6e-4), round(r["krate"], 4), g.krate)
    chk("B", f"{y} BB rate", close(r["bbrate"], g.bbrate, 6e-4), round(r["bbrate"], 4), g.bbrate)
    chk("B", f"{y} whiff", close(r["whiff"], g.whiff_rate, 6e-4), round(r["whiff"], 4), g.whiff_rate)
    chk("B", f"{y} chase", close(r["chase"], g.chase_rate, 6e-4), round(r["chase"], 4), g.chase_rate)
    chk("B", f"{y} in-zone (tracked)", close(r["inzone"], g.in_zone_rate, 6e-4), round(r["inzone"], 4), g.in_zone_rate)
r25, r26 = rates(L[L.game_year == 2025]), rates(L[L.game_year == 2026])
chk("B", "2026 in-zone is lowest since 2021, not career-lowest", r26["inzone"] > rates(L[L.game_year == 2021])["inzone"] and
    all(r26["inzone"] < rates(L[L.game_year == y])["inzone"] for y in (2019, 2020, 2022, 2023, 2024, 2025)))
chk("B", "2026 chase is a career high", all(r26["chase"] > rates(L[L.game_year == y])["chase"] for y in range(2019, 2026)))


def pz(x1, n1, x2, n2):
    from math import erf, sqrt
    p = (x1 + x2) / (n1 + n2); se = sqrt(p * (1 - p) * (1 / n1 + 1 / n2)); z = (x1 / n1 - x2 / n2) / se
    return 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))


chk("B", "in-zone p (2025 v 2026) ≈ 0.002", close(pz(r26['inzone'] * L[(L.game_year == 2026)].zone.notna().sum(), L[(L.game_year == 2026)].zone.notna().sum(),
                                                   r25['inzone'] * L[(L.game_year == 2025)].zone.notna().sum(), L[(L.game_year == 2025)].zone.notna().sum()), 0.002, 1e-3))
chk("B", "chase p ≈ 0.057", close(pz(r26['ch'], r26['ooz'], r25['ch'], r25['ooz']), 0.057, 1.5e-3))
chk("B", "K p ≈ 0.44", close(pz(r26['k'], r26['pa'], r25['k'], r25['pa']), 0.442, 2e-3))
# client frame (O-26): name filter over nphl with global keep-first dedup
keys = []
for i, f in enumerate(files):
    k = pd.read_parquet(f, columns=KEY + ["player_name"]); k["_i"] = i; keys.append(k)
allk = pd.concat(keys, ignore_index=True)
allk["_first"] = ~allk.duplicated(KEY, keep="first")
nm = allk[allk.player_name == "Luzardo, Jesús"]
chk("B", "O-26: nphl name rows lost to keep-first dedup == 230", int((~nm._first).sum()) == H["nphl_lost_to_dedup"] == 230, int((~nm._first).sum()))
cl_post = int(nm[nm._first].merge(allf[allf.game_type != "R"][KEY], on=KEY).shape[0]) + int(((ph.player_name == "Luzardo, Jesús") &
          (ph.phillies_role == "pitching") & ph.game_type.isin(["F", "D", "L", "W"])).sum())
chk("B", "client frame carries 380 postseason pitches", cl_post == H["client_postseason_pitches_total"] == 380, cl_post)
# BS-1 / uc-pps-033 V-3 resolution
bw = allk[allk.player_name == "Bowlan, Jonathan"]
lhv = pd.read_parquet(ROOT / "data" / "opponents" / "lhvp26.parquet", columns=["pitcher", "game_date", "game_pk"])
chk("B", "V-3: Bowlan has 16 AAA pitches in lhvp26 (one game, 2026-04-26)", ((lhv.pitcher == 680742).sum() == 16) and
    lhv[lhv.pitcher == 680742].game_pk.nunique() == 1 and str(lhv[lhv.pitcher == 680742].game_date.iat[0])[:10] == "2026-04-26")
V3 = Rc("bs1_bowlan_v3_resolution")
chk("B", "V-3: client-frame Bowlan 2026 = 60 G, wOBA .269", V3.games.iat[1] == 60 and close(V3.woba.iat[1], 0.269, 5e-4), V3.to_dict("records"))

# ---------------------------------------------------------------- C · context population & percentiles
pp = ph[(ph.phillies_role == "pitching") & (ph.game_type == "R")].copy()
pp["_sw"] = pp.description.isin(SW); pp["_wh"] = pp.description.isin(WH); pp["_ooz"] = pp.zone > 9; pp["_ch"] = pp._ooz & pp._sw
g = pp.groupby(["pitcher", "game_year"], as_index=False).agg(n=("pitch_type", "size"), sw=("_sw", "sum"), wh=("_wh", "sum"),
                                                            ooz=("_ooz", "sum"), ch=("_ch", "sum"))
g["whiff"] = g.wh / g.sw; g["chase"] = g.ch / g.ooz
cx = g[g.n >= 150].reset_index(drop=True)
me = cx[(cx.pitcher == ID) & (cx.game_year == 2026)].iloc[0]
chk("C", "CX-1 n == 259", len(cx) == 259, len(cx))
chk("C", "chase rank #28", int((cx.chase > me.chase).sum() + 1) == 28, int((cx.chase > me.chase).sum() + 1))
chk("C", "whiff rank #31", int((cx.whiff > me.whiff).sum() + 1) == 31, int((cx.whiff > me.whiff).sum() + 1))
dom = cx[(cx.chase > me.chase) & (cx.whiff > me.whiff)]
chk("C", "dominated by 10", len(dom) == 10, len(dom))
chk("C", "none of the 10 has a starter's workload (<2,000 pitches)", (dom.n < 2000).all(), dom.n.max())
mu = (cx.chase.mean(), cx.whiff.mean())
chk("C", "plus/plus quadrant holds 76", int(((cx.chase >= mu[0]) & (cx.whiff >= mu[1])).sum()) == 76)
s = cx[cx.n >= 2000]
chk("C", "starter workloads n == 41", len(s) == 41, len(s))
chk("C", "starter workloads: whiff #1", int((s.whiff > me.whiff).sum()) == 0)
chk("C", "starter workloads: chase #8", int((s.chase > me.chase).sum() + 1) == 8)
chk("C", "next whiff among starters is Wheeler 2025 at 31.5%", close(s.sort_values("whiff", ascending=False).whiff.iat[1], 0.315, 6e-4))
for cut in (1500, 2500):   # sensitivity of the declared cut (report caveat)
    sc = cx[cx.n >= cut]
    chk("C", f"sensitivity: at >= {cut} pitches Luzardo 2026 is still #1 in whiff among {len(sc)}",
        int((sc.whiff > me.whiff).sum()) == 0, f"n={len(sc)}, rank={int((sc.whiff > me.whiff).sum()) + 1}")
lh = pp[pp.p_throws == "L"] if "p_throws" in pp else None
KP = Rc("house_percentiles").set_index("column")
chk("C", "KP-1 K rate 89th pct, rank 21/198, staff #3", KP.loc["krate", "percentile"] == 89 and KP.loc["krate", "rank"] == 21 and KP.loc["krate", "n"] == 198 and KP.loc["krate", "staff_rank_2026"] == 3)
chk("C", "KP-1 whiff 86th, staff #2", KP.loc["whiff_rate", "percentile"] == 86 and KP.loc["whiff_rate", "staff_rank_2026"] == 2)
chk("C", "KP-1 chase 87th; wOBA 80th", KP.loc["chase_rate", "percentile"] == 87 and KP.loc["woba", "percentile"] == 80)
CM = H["cmd26"]
chk("C", "command: expected BB 9.2%, actual 7.1%, residual −2.0 pts", close(CM["expected"], 0.092, 6e-4) and close(CM["bb"], 0.071, 6e-4) and close(CM["residual"], -0.020, 6e-4))
chk("C", "command residual better than 79% of LHP seasons", CM["residual_pctile"] == 79)

# ---------------------------------------------------------------- D · Labor Day
G = L[L.game_pk == 823415].sort_values(["at_bat_number", "pitch_number"])
chk("D", "109 pitches", len(G) == 109)
chk("D", "2 H, 1 BB, 12 K, 1 HBP", G.events.isin(["single", "double", "triple", "home_run"]).sum() == 2 and (G.events == "walk").sum() == 1 and
    (G.events == "strikeout").sum() == 12 and (G.events == "hit_by_pitch").sum() == 1)
chk("D", "30 batters", G.at_bat_number.nunique() == 30)
chk("D", "23 whiffs = 22 swinging strikes + 1 foul tip", G.description.isin(WH).sum() == 23 and
    G.description.isin(["swinging_strike", "swinging_strike_blocked"]).sum() == 22 and (G.description == "foul_tip").sum() == 1)
chk("D", "28 chases on 61 out-of-zone (45.9%)", ((G.zone > 9) & G.description.isin(SW)).sum() == 28 and (G.zone > 9).sum() == 61)
chk("D", "42 CSW (38.5%)", (G.description.isin(WH) | (G.description == "called_strike")).sum() == 42)
ff = G[G.pitch_type == "FF"]
chk("D", "FF avg 96.3, 9th 97.4, max 98.1", close(ff.release_speed.mean(), 96.306, 1e-3) and close(ff[ff.inning == 9].release_speed.mean(), 97.433, 1e-3) and ff.release_speed.max() == 98.1)
pi = G.groupby("inning").size()
chk("D", "innings took 8 to 17 pitches", pi.min() == 8 and pi.max() == 17, pi.to_dict())
chk("D", "ATL scored 0 on his watch", G.post_bat_score.max() == 0)
bat = ph[(ph.game_pk == 823415) & (ph.phillies_role == "batting")]
chk("D", "PHI scored 1; the run is a Schwarber HR in the 8th", bat.post_bat_score.max() == 1 and
    ((bat.events == "home_run") & (bat.inning == 8) & bat.des.str.contains("Schwarber")).sum() == 1)
rh = G[G.stand == "R"]
chg = rh[rh.pitch_type == "CH"].groupby("n_thruorder_pitcher").size().to_dict()
tot = rh.groupby("n_thruorder_pitcher").size().to_dict()
chk("D", "RHB changeups by time through: 2/19, 8/23, 2/21, 1/7", chg == {1: 2, 2: 8, 3: 2, 4: 1} and tot == {1: 19, 2: 23, 3: 21, 4: 7}, (chg, tot))
chk("D", "RHB four-seams third time through: 11", ((rh.n_thruorder_pitcher == 3) & (rh.pitch_type == "FF")).sum() == 11)
chk("D", "24 first-pitch strikes of 30 (type != 'B')", (G[G.pitch_number == 1].type != "B").sum() == 24)

# ---------------------------------------------------------------- E · season arc, game scores, postseason, October card
OUTS = {'field_out': 1, 'strikeout': 1, 'force_out': 1, 'sac_fly': 1, 'sac_bunt': 1, 'fielders_choice_out': 1, 'grounded_into_double_play': 2,
        'double_play': 2, 'strikeout_double_play': 2, 'sac_fly_double_play': 2, 'sac_bunt_double_play': 2, 'triple_play': 3,
        'caught_stealing_2b': 1, 'caught_stealing_3b': 1, 'caught_stealing_home': 1, 'pickoff_1b': 1, 'pickoff_2b': 1, 'pickoff_3b': 1,
        'pickoff_caught_stealing_2b': 1, 'pickoff_caught_stealing_3b': 1, 'pickoff_caught_stealing_home': 1, 'other_out': 1}


def gscore(d):
    d = d.copy(); d["_o"] = d.events.map(OUTS).fillna(0)
    pa = d.groupby(["game_pk", "at_bat_number"], as_index=False).agg(r0=("bat_score", "min"), r1=("post_bat_score", "max"))
    runs = (pa.r1 - pa.r0).groupby(pa.game_pk).sum().rename("r")
    g = d.groupby("game_pk").agg(date=("game_date", "first"), outs=("_o", "sum"), inn0=("inning", "min"),
                                 k=("events", lambda s: s.isin(["strikeout", "strikeout_double_play"]).sum()),
                                 bb=("events", lambda s: (s == "walk").sum()), h=("events", lambda s: s.isin(["single", "double", "triple", "home_run"]).sum()),
                                 hr=("events", lambda s: (s == "home_run").sum())).join(runs)
    g["gs"] = 40 + 2 * g.outs + g.k - 2 * g.bb - 2 * g.h - 3 * g.r - 6 * g.hr
    return g


GS = gscore(L)
st = GS[GS.inn0 == 1]
chk("E", "150 career starts, 166 games", len(st) == 150 and len(GS) == 166, (len(st), len(GS)))
chk("E", "Labor Day GS 100, #1; next best 86 (2026-04-28)", st.loc[823415, "gs"] == 100 and st.gs.nlargest(2).iat[1] == 86 and
    str(st.sort_values("gs").iloc[-2].date)[:10] == "2026-04-28")
chk("E", "only 27-out game; next most 24", (GS.outs == 27).sum() == 1 and GS[GS.index != 823415].outs.max() == 24)
chk("E", "career K high 13", GS.k.max() == 13)
L26 = L[L.game_year == 2026]
g26 = GS.loc[L26.game_pk.unique()]
first = g26[pd.to_datetime(g26.date) < "2026-07-13"]; second = g26[pd.to_datetime(g26.date) >= "2026-07-13"]
chk("E", "first half 19 starts, 46 R / 325 outs (3.82)", len(first) == 19 and first.r.sum() == 46 and first.outs.sum() == 325)
chk("E", "second half 10 starts, 14 R / 202 outs (1.87)", len(second) == 10 and second.r.sum() == 14 and second.outs.sum() == 202)
aug = g26[pd.to_datetime(g26.date).dt.month == 8]
chk("E", "August 5 starts, 7 R / 101 outs", len(aug) == 5 and aug.r.sum() == 7 and aug.outs.sum() == 101)
ra = rates(L26[pd.to_datetime(L26.game_date).dt.month == 8])
chk("E", "August K 34.6% (133 PA)", ra["pa"] == 133 and close(ra["krate"], 0.346, 6e-4))
rs = rates(L26[pd.to_datetime(L26.game_date) >= "2026-07-13"])
chk("E", "second half K 32.1%, BB 6.4% (265 PA)", rs["pa"] == 265 and close(rs["krate"], 0.321, 6e-4) and close(rs["bbrate"], 0.064, 6e-4))
pc = L26.groupby("game_pk").size()
chk("E", "pitch counts 86–110, SD 6.2; Labor Day 109 is second-highest", pc.min() == 86 and pc.max() == 110 and close(pc.std(), 6.219, 1e-3) and (pc > 109).sum() == 1)
sea = L26[(L26.game_pk.isin(g26[pd.to_datetime(g26.date) == "2026-08-26"].index)) & (L26.pitch_type == "FF")]
chk("E", "8/26 FF avg 95.4; 7.0 IP 1 H 0 R", close(sea.release_speed.mean(), 95.44, 5e-3) and g26[pd.to_datetime(g26.date) == "2026-08-26"].iloc[0][["outs", "h", "r"]].tolist() == [21, 1, 0])
d_ = L26.sort_values(["game_pk", "at_bat_number", "pitch_number"]).copy(); d_["po"] = d_.groupby("game_pk").cumcount() + 1
f15 = d_[(d_.po <= 15) & (d_.pitch_type == "FF")].groupby("game_pk").release_speed.mean()
chk("E", "first-15 FF: median 97.0, p25 96.2, Labor Day 96.9; one start with none (6/23)",
    close(f15.median(), 97.006, 2e-3) and close(f15.quantile(.25), 96.219, 2e-3) and close(f15.loc[823415], 96.867, 2e-3) and len(f15) == 28)
PG = gscore(LP)
chk("E", "postseason: 6 games, 66 outs, 10 R", len(PG) == 6 and PG.outs.sum() == 66 and PG.r.sum() == 10)
p25 = PG[pd.to_datetime(PG.date).dt.year == 2025]
chk("E", "2025 NLDS: 23 outs, 0 R", p25.outs.sum() == 23 and p25.r.sum() == 0)
p23 = PG[pd.to_datetime(PG.date).dt.year == 2023].iloc[0]
chk("E", "2023 Wild Card at PHI: 11 outs, 8 H, 3 R", [p23.outs, p23.h, p23.r] == [11, 8, 3] and
    (LP[LP.game_pk == p23.name].home_team == "PHI").all() if "home_team" in LP else [p23.outs, p23.h, p23.r] == [11, 8, 3])
card = Rc("october_card").set_index("signature")
chk("E", "OC bars: 96.2 mph / 29.2% / 12.0 / 10.7%", close(card.loc["OC-A", "bar"], 96.219, 2e-3) and close(card.loc["OC-B", "bar"], 0.292, 6e-4)
    and close(card.loc["OC-C", "bar"], 12.0, 1e-6) and close(card.loc["OC-D", "bar"], 0.107, 6e-4))
bt = Rc("october_card_backtest_2026")
chk("E", "backtest 21 on / 7 off / 1 incomplete", (bt.verdict == "ON-SCRIPT").sum() == 21 and (bt.verdict == "OFF-SCRIPT").sum() == 7 and (bt.verdict == "INCOMPLETE").sum() == 1)
on, off = bt[bt.verdict == "ON-SCRIPT"], bt[bt.verdict == "OFF-SCRIPT"]
chk("E", "backtest: off-script allowed fewer runs (2.34 vs 3.13 per 27)", close(27 * off.r.sum() / off.outs.sum(), 2.339, 2e-3) and close(27 * on.r.sum() / on.outs.sum(), 3.126, 2e-3))
hist = Rc("october_card_postseason_history")
chk("E", "postseason history 5 on-script, 1 off (2020-10-07)", (hist.verdict == "ON-SCRIPT").sum() == 5 and hist[hist.verdict == "OFF-SCRIPT"].game_date.iat[0] == "2020-10-07")
rep = Rc("parent_reproduction")
chk("E", "uc-pps-017 reproduction 4/4", rep.match.all())
tto = L26.groupby("n_thruorder_pitcher")
chk("E", "TTO PA 262 / 262 / 197", [rates(L26[L26.n_thruorder_pitcher == i])["pa"] for i in (1, 2, 3)] == [262, 262, 197])

# ---------------------------------------------------------------- F · published numbers (report + dashboard)
md = (PKG / "dp_uc49_luzardo_2026_recap_report.md") if (PKG / "dp_uc49_luzardo_2026_recap_report.md").exists() else ROOT / "dp_uc49_luzardo_2026_recap_report.md"
rp = md.read_text(encoding="utf-8")
db = (ROOT / "dp_uc49_luzardo_2026_dashboard.html").read_text(encoding="utf-8")
pc_ = lambda x: f"{100 * x:.1f}%"   # noqa: E731
REPORT = [
    ("2026 K rate", pc_(r26["krate"])), ("2026 BB rate", pc_(r26["bbrate"])), ("2026 whiff", pc_(r26["whiff"])),
    ("2026 chase", pc_(r26["chase"])), ("2026 in-zone", pc_(r26["inzone"])), ("2025 in-zone", pc_(r25["inzone"])),
    ("2025 K", pc_(r25["krate"])), ("2025 BB", pc_(r25["bbrate"])), ("K counts", f"216 of 759"), ("K counts 26", "221 of 730"),
    ("expected BB", "9.2%"), ("residual pct", "79%"), ("chase rank", "#28"), ("whiff rank", "#31"), ("n 259", "259"),
    ("starters 41", "41"), ("next whiff", "31.5%"), ("dominated 10", "**10**"), ("LHP chase #7", "chase #7"), ("LHP whiff #9", "whiff #9"),
    ("plus/plus 76", "76 seasons"), ("89th", "89th house percentile"), ("#21 of 198", "#21 of 198"), ("86th", "86th"), ("87th", "87th"),
    ("80th", "80th"), ("first-half r27", "3.82"), ("second-half r27", "1.87"), ("second-half K", "32.1%"), ("second-half wOBA", ".239"),
    ("Aug K", "34.6%"), ("Aug runs", "7 / 101"), ("TTO1", ".197 (262 PA)"), ("TTO2", ".333 (262)"), ("TTO3", ".305 (197)"),
    ("GS 100", "100, #1 of 150 career starts"), ("next GS", "86"), ("K high", "(13)"), ("27-out", "27-out"), ("next most 24", "next most: 24"),
    ("LD chase", "28 of his 61"), ("LD 45.9", "45.9%"), ("LD CSW", "42 of his 109"), ("LD 38.5", "38.5%"), ("LD ff", "96.3"),
    ("LD 9th", "97.4"), ("LD max", "98.1"), ("LD whiffs", "23 whiffs"), ("CH 2 of 19", "2 changeups in 19"), ("CH 8 in 23", "**8 in 23**"),
    ("FF 11 of 21", "11 of 21"), ("first15 LD", "**96.9 mph**"), ("first15 med", "median of 97.0"), ("p25", "96.2"),
    ("SEA", "95.4 mph"), ("SEA15", "95.7"), ("post", "Six games, 94 batters, 66 outs, 10 runs"), ("OC-B bar", "29.2%"),
    ("OC-D bar", "10.7%"), ("OC-C bar", "12.0"), ("backtest", "21 on-script, 7 off-script and 1 incomplete"), ("bt r27", "(2.34 per 27 outs against 3.13)"),
    ("O-26", "230 regular-season pitches"), ("post 380", "380 postseason pitches"), ("dups", "1,188 duplicates removed"),
    ("spring", "165 spring-training rows"), ("sweeper 38.2", "38.2%"), ("sweeper whiff", "47.6%"), ("LHB ST", "48.4%"), ("LHB whiff", "55.7%"),
    ("FF share", "34.1% → 26.2%"), ("SI share", "10.0% → 17.3%"), ("repro", "4/4"), ("pitch band", "86 to 110 pitches"), ("SD", "6.2"),
    ("p in-zone", "p = 0.002"), ("p chase", "p = 0.057"), ("FPS", "67.2%"), ("FPS26", "62.6%"),
]
for name, sstr in REPORT:
    chk("F", f"report states {name}: '{sstr}'", sstr in rp)
DASH = [pc_(r26["krate"]), pc_(r26["chase"]), "#28 of 259", "#1 of 150 career starts", "89th house percentile", "3.82", "1.87",
        "7 runs in 101 outs", "23 whiffs", "28 chases on 61", "97.4", "96.9 mph", "95.4 mph", "2.34 vs 3.13", "missed more bats than any Phillies starter"]
for sstr in DASH:
    chk("F", f"dashboard states '{sstr}'", sstr in db)
chk("F", "report makes no 'lowest of his career' in-zone claim", "lowest of his career" not in rp and "lowest of his career" not in db)
chk("F", "report makes no MLB-wide rank claim", "MLB-wide" in rp and "in MLB" not in rp.replace("not MLB-wide", ""))

# ---------------------------------------------------------------- G · carry-in discipline
fm = Rc("freshness_manifest")
for kw in ("Caba", "135M", "All-Star", "Schwarber", "IL 9/15", "Game 162"):
    chk("G", f"carry-in logged in freshness manifest: {kw}", fm.note.str.contains(kw, regex=False).any())
chk("G", "ERA appears only as a carry-in", "2.87" in rp and "ERA is not computed" in db and "is not ERA" in rp)
chk("G", "no injury inference language", not any(w in rp.lower() for w in ("because of the shoulder", "fatigue caused", "injury caused")))
chk("G", "report says the shoulder is not modeled", "not modeled, inferred or predicted" in rp)

V = pd.DataFrame(LOG)
V.to_csv(OUT / "dp_uc49_verification_log.csv", index=False)
fams = V.groupby("family").result.apply(lambda s: f"{(s == 'PASS').sum()}/{len(s)}").to_dict()
print(json.dumps(dict(total=f"{(V.result == 'PASS').sum()}/{len(V)}", families=fams), indent=1))
if (V.result == "FAIL").any():
    print(V[V.result == "FAIL"].to_string())
    sys.exit(1)
