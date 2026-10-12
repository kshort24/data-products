"""
dp_uc51_verification.py — independent harness for UC #51 / uc-pps-035 ("Still Zack Wheeler").

Different code path from the build: it imports NO dp_uc* kernel for computation (kernels are only hashed). It re-reads the
parquet data plane with pyarrow, rebuilds the frame by its own filters, re-implements every KPI from its definition
(house PA/wOBA rule, XW-1, ER-1 geometry, JR-1 swing list, OU-2 outs, OC-1 quantiles) and then checks the receipts,
the report prose and the dashboard against what it recomputed.

Families:  A lineage · B frame & sources · C season rates (2020-2026) · D the slide, outs, games · E context, swing timing,
           platoon, card, parent reproduction · F published numbers (report + dashboard) · G carry-in discipline
Run:  PYTHONPATH=/tmp/pyl MLB_DATA_ROOT=<MLB> python3 dp_uc51_verification.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy.stats import norm, ttest_ind

ROOT = Path(os.environ.get("MLB_DATA_ROOT", Path(__file__).resolve().parent))
OUT = ROOT / "out"
ID = 554430
LOG = []


def chk(fam, name, ok, observed="", expected=""):
    LOG.append(dict(family=fam, check=name, result="PASS" if bool(ok) else "FAIL", observed=str(observed)[:160],
                    expected=str(expected)[:160]))


def close(a, b, tol=1e-3):
    return a is not None and b is not None and not (isinstance(a, float) and np.isnan(a)) and abs(float(a) - float(b)) <= tol


sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()   # noqa: E731
H = json.loads((OUT / "dp_uc51_headlines.json").read_text())
Rc = lambda n: pd.read_csv(OUT / f"dp_uc51_{n}.csv")                 # noqa: E731
pct = lambda x, d=1: f"{100 * x:.{d}f}%"                             # noqa: E731
f3 = lambda x: f"{x:.3f}".lstrip("0")                                 # noqa: E731

# ---------------------------------------------------------------- A · lineage
PINS = {"dp_uc49_kernel.py": "a4ad5191a653", "dp_uc50_kernel.py": "8084cb172d0c", "dp_uc48_kernel.py": "0f63857a1032",
        "dp_uc44_kernel.py": "a2c119096db2", "barrel_rate.py": "6282f090394a"}
for f, h in PINS.items():
    chk("A", f"{f} sha256 pinned", sha(ROOT / f).startswith(h), sha(ROOT / f)[:12], h)


def seg_sha(file, name):
    p = ROOT / file
    if p.suffix == ".ipynb":
        srcs = ["".join(c["source"]) for c in json.loads(p.read_text(encoding="utf-8"))["cells"] if c["cell_type"] == "code"]
    else:
        srcs = [p.read_text(encoding="utf-8")]
    for s in srcs:
        try:
            t = ast.parse(s)
        except SyntaxError:
            continue
        for n in t.body:
            if (isinstance(n, ast.FunctionDef) and n.name == name) or (isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == name):
                return hashlib.sha256(ast.get_source_segment(s, n).encode()).hexdigest()


pins = Rc("lineage_pins")
for r in pins[pins.mechanism.str.startswith("IX-1")].itertuples():
    chk("A", f"IX-1 segment {r.file}:{r.object} re-hashed independently", seg_sha(r.file, r.object) == r.sha256, r.sha256[:12])
chk("A", "anchor == Game 162 (2026-09-27)", H["anchor"] == "2026-09-27", H["anchor"])
dqs = Rc("dq_scorecard")
chk("A", "DQ scorecard has 0 FAIL", (dqs.result != "FAIL").all(), dqs.result.value_counts().to_dict())

# ---------------------------------------------------------------- B · frame, rebuilt independently
KEY = ["game_pk", "at_bat_number", "pitch_number"]
NEED = KEY + ["pitcher", "player_name", "game_year", "game_type", "game_date", "events", "description", "zone", "plate_x", "plate_z",
              "sz_top", "sz_bot", "type", "launch_speed", "launch_speed_angle", "bb_type", "estimated_woba_using_speedangle",
              "woba_value", "woba_denom", "pitch_type", "release_speed", "release_pos_x", "release_pos_z", "release_extension",
              "stand", "inning", "outs_when_up", "bat_score", "post_bat_score", "phillies_role", "home_team", "away_team",
              "intercept_ball_minus_batter_pos_x_inches", "batter", "des", "pfx_x"]


def rd(f):
    have = set(pq.read_schema(f).names)
    return pd.read_parquet(f, columns=[c for c in NEED if c in have])


ph = pd.concat([rd(ROOT / "data" / "phillies" / f"phils_{y}.parquet") for y in range(2015, 2027)], ignore_index=True)
W = pd.read_csv(ROOT / "wOBA and FIP Constants.csv")
wcols = ["wBB", "wHBP", "w1B", "w2B", "w3B", "wHR"]
ph = ph.merge(W[["Season"] + wcols], left_on="game_year", right_on="Season", how="left")
chk("B", "Phillies log max regular-season date == anchor", str(ph[(ph.game_type == "R") & (ph.game_year == 2026)].game_date.max())[:10] == H["anchor"])
PPS = ph[(ph.phillies_role == "pitching") & (ph.game_type == "R")]
L = PPS[(PPS.pitcher == ID) & PPS.game_year.between(2020, 2026)].drop_duplicates(KEY).copy()
L26 = L[L.game_year == 2026].copy()
chk("B", "2026 regular-season pitches", len(L26) == H["pitches_2026"] == 2649, len(L26))
chk("B", "2026 games == 28", L26.game_pk.nunique() == 28, L26.game_pk.nunique())
chk("B", "2026 window 4/25 .. 9/27", (str(L26.game_date.min())[:10], str(L26.game_date.max())[:10]) == ("2026-04-25", "2026-09-27"))
chk("B", "Phillies-era frame size == recap receipt", len(L) == int(Rc("recap_governed").query("era == 'PHI'").pitches.sum()), len(L))
opp = sorted((ROOT / "data" / "opponents").glob("*.parquet"))
hit = [f for f in opp if (pd.read_parquet(f, columns=["pitcher"]).pitcher == ID).any()]
chk("B", "id scan: 24 opponent files hold his pitches", len(hit) == H["opp_files_with_subject"] == 24, len(hit))
lhv = pd.read_parquet(ROOT / "data/opponents/lhvp26.parquet", columns=["pitcher", "game_pk", "game_type", "home_team", "away_team"])
lhv = lhv[lhv.pitcher == ID]
chk("B", "MI-1: lhvp26 holds 148 Wheeler rows in 3 games, all tagged 'R'", len(lhv) == 148 and lhv.game_pk.nunique() == 3 and (lhv.game_type == "R").all(),
    f"{len(lhv)} rows, {lhv.game_pk.nunique()} games")
chk("B", "MI-1 receipt matches (148 excluded)", int(Rc("milb_rows_excluded").rows.sum()) == 148)
k49src = (ROOT / "dp_uc49_kernel.py").read_text(encoding="utf-8")
chk("B", "NM-1: CF-2 stamps SUBJECT_NAME (Luzardo) on every frame it builds (static check)",
    "df['player_name'] = SUBJECT_NAME" in k49src and 'SUBJECT_NAME = "Luzardo, Jesús"' in k49src)
kf = ph[(ph.phillies_role == "pitching") & ~ph.game_type.isin(["S", "E"]) & (ph.player_name == "Wheeler, Zack")].drop_duplicates(KEY)
post_by = kf[kf.game_type != "R"].groupby("game_year").size()
chk("B", "client frame = governed + postseason rows (1,065)", len(kf) == len(L) + int(post_by.sum()) and int(post_by.sum()) == 1065,
    f"{len(kf)} = {len(L)} + {int(post_by.sum())}")

# ---------------------------------------------------------------- C · season rates, re-implemented
SW_ALL = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
SW_JR = ["foul", "foul_tip", "hit_into_play", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WH = ["foul_tip", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
BALL = 2.94 / 12.0


def rates(d):
    ev = d.events.fillna("NA")
    pa = int((~ev.isin(["NA", "pickoff_1b"])).sum())
    k = int(ev.isin(["strikeout", "strikeout_double_play"]).sum()); bb = int((ev == "walk").sum())
    wsum = sum(d.loc[ev == e, w].sum() for e, w in [("walk", "wBB"), ("hit_by_pitch", "wHBP"), ("single", "w1B"), ("double", "w2B"),
                                                     ("triple", "w3B"), ("home_run", "wHR")])
    p = d[d.woba_denom.fillna(0) > 0]
    xn = np.where((p.type == "X") & p.estimated_woba_using_speedangle.notna(), p.estimated_woba_using_speedangle, p.woba_value.fillna(0))
    x = d[d.type == "X"]
    tr = d.zone.notna(); ooz = d.zone > 9
    loc = d.dropna(subset=["plate_x", "plate_z", "sz_top", "sz_bot"])
    dx = np.maximum(np.abs(loc.plate_x) - 0.83, 0); dz = np.maximum.reduce([loc.sz_bot - loc.plate_z, loc.plate_z - loc.sz_top, np.zeros(len(loc))])
    inside = (dx == 0) & (dz == 0)
    din = np.minimum.reduce([0.83 - np.abs(loc.plate_x), loc.plate_z - loc.sz_bot, loc.sz_top - loc.plate_z])
    dist = np.where(inside, din, np.sqrt(dx ** 2 + dz ** 2))
    sw = d[d.description.isin(SW_JR) & d.intercept_ball_minus_batter_pos_x_inches.notna()]
    swings = int(d.description.isin(SW_ALL).sum())
    return dict(pa=pa, k=k, bb=bb, krate=k / pa, bbrate=bb / pa, woba=wsum / pa, xwoba=xn.sum() / p.woba_denom.sum(),
                in_zone=d.zone.between(1, 9).sum() / tr.sum(), chase=(ooz & d.description.isin(SW_ALL)).sum() / ooz.sum(),
                edge=(dist <= BALL).mean(), hh=(x.launch_speed >= 95).sum() / len(x), barrel=(x.launch_speed_angle == 6).sum() / len(x),
                ld=(x.bb_type == "line_drive").sum() / len(x), whiff=d.description.isin(WH).sum() / swings,
                tied=(sw.intercept_ball_minus_batter_pos_x_inches < 32.5).mean() if len(sw) else np.nan, tracked_sw=len(sw),
                velo=d[d.pitch_type == "FF"].release_speed.mean(), bip=len(x), walks=bb)


RG = Rc("recap_governed").query("era == 'PHI'").set_index("game_year")
REC = {}
for y in range(2020, 2027):
    r = rates(L[L.game_year == y]); REC[y] = r; g = RG.loc[y]
    for c, gc in [("pa", "plate_apps"), ("krate", "krate"), ("bbrate", "bbrate"), ("woba", "woba"), ("xwoba", "xwoba"), ("in_zone", "in_zone_rate"),
                  ("chase", "chase_rate"), ("edge", "edge_rate"), ("hh", "hard_hit_rate"), ("barrel", "barrel_rate"), ("ld", "line_drive_rate"),
                  ("whiff", "whiff_rate"), ("velo", "ff_velo")]:
        tol = 0.5 if c == "pa" else (0.051 if c == "velo" else 0.0015)
        chk("C", f"{y} {c}", close(r[c], g[gc], tol), round(float(r[c]), 4), round(float(g[gc]), 4))
    if y >= 2025:
        chk("C", f"{y} tied-up (JR-1 re-implemented)", close(r["tied"], g.jam_rate, 0.0015), round(r["tied"], 4), g.jam_rate)
r26 = REC[2026]
chk("C", "2026 BB rate is the highest of the seven Phillies seasons", r26["bbrate"] > max(REC[y]["bbrate"] for y in range(2020, 2026)))
chk("C", "2026 in-zone is the lowest, chase the highest, FF velo the lowest of the seven",
    r26["in_zone"] < min(REC[y]["in_zone"] for y in range(2020, 2026)) and r26["chase"] > max(REC[y]["chase"] for y in range(2020, 2026))
    and r26["velo"] < min(REC[y]["velo"] for y in range(2020, 2026)))
chk("C", "xwOBA 2026 == client's Savant .263 (3 dp)", round(r26["xwoba"], 3) == 0.263, round(r26["xwoba"], 4))
chk("C", "2026 K == 193, BB == 47 (carry-in)", r26["k"] == 193 and r26["bb"] == 47)


def z2(x1, n1, x2, n2):
    p = (x1 + x2) / (n1 + n2); se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)); z = (x1 / n1 - x2 / n2) / se
    return z, 2 * (1 - norm.cdf(abs(z)))


base = L[L.game_year.between(2021, 2025)]
rb = rates(base)
iz_n = lambda d: (int(d.zone.between(1, 9).sum()), int(d.zone.notna().sum()))  # noqa: E731
_, p_iz = z2(*iz_n(L26), *iz_n(base))
chk("C", "in-zone 2026 vs 2021-25 p < .001", p_iz < .001 and close(H["tests"]["In-zone (tracked) · 2026 vs 2021-25"]["r2"], rb["in_zone"], 0.0005), p_iz)
_, p_bb = z2(r26["bb"], r26["pa"], rb["bb"], rb["pa"])
chk("C", "BB 2026 vs 2021-25 p", close(p_bb, H["tests"]["BB per PA · 2026 vs 2021-25"]["p"], 0.0015), round(p_bb, 4))
for nm, col in [("Hard-hit per BIP", "hh"), ("Barrel per BIP", "barrel"), ("Line drive per BIP", "ld")]:
    x1 = round(r26[col] * r26["bip"]); x2 = round(rb[col] * rb["bip"])
    _, pp = z2(x1, r26["bip"], x2, rb["bip"])
    chk("C", f"{nm} 2026 vs 2021-25 p > .4 (noise)", pp > .4 and close(pp, H["tests"][f"{nm} · 2026 vs 2021-25"]["p"], 0.002), round(pp, 3))

# ---------------------------------------------------------------- D · outs, the slide, games
DEF = ph[(ph.phillies_role == "pitching") & ~ph.game_type.isin(["S", "E"])].drop_duplicates(KEY).sort_values(["game_pk", "at_bat_number", "pitch_number"])
pa = DEF.groupby(["game_pk", "at_bat_number"], as_index=False).head(1)[["game_pk", "game_date", "game_type", "inning", "at_bat_number", "outs_when_up", "pitcher"]].copy()
pa["nxt"] = pa.groupby(["game_pk", "inning"]).outs_when_up.shift(-1)
pa["outs"] = pa.nxt.fillna(3) - pa.outs_when_up
lastev = DEF[DEF.events.notna()].groupby(["game_pk", "at_bat_number"]).events.last()
OUTEV = {"field_out": 1, "strikeout": 1, "force_out": 1, "sac_fly": 1, "sac_bunt": 1, "fielders_choice_out": 1, "grounded_into_double_play": 2,
         "double_play": 2, "strikeout_double_play": 2, "sac_fly_double_play": 2, "triple_play": 3, "other_out": 1}
islast = pa.groupby("game_pk").at_bat_number.transform("max") == pa.at_bat_number
pa.loc[islast, "outs"] = np.minimum(3 - pa.loc[islast, "outs_when_up"],
                                    pa.loc[islast].set_index(["game_pk", "at_bat_number"]).index.map(lambda k: OUTEV.get(lastev.get(k, ""), 0)).values)
wpa = pa[(pa.pitcher == ID) & (pa.game_type == "R") & (pa.game_date.astype(str).str[:4] == "2026")]
outs26 = int(wpa.outs.sum())
chk("D", "OU-2 re-implemented: 486 outs (= 162.0 IP carry-in)", outs26 == 486 == H["carry"]["outs"], outs26)
runs = L26.groupby(["game_pk", "at_bat_number"]).agg(a=("bat_score", "min"), b=("post_bat_score", "max"))
runs_g = (runs.b - runs.a).groupby(level=0).sum()
og = wpa.groupby("game_pk").outs.sum()
gd = L26.groupby("game_pk").game_date.first().astype(str).str[:10].sort_values()
post = gd[gd >= "2026-07-13"]
wins = [(post.iloc[i], post.iloc[i + 5], 27 * runs_g[post.index[i:i + 6]].sum() / og[post.index[i:i + 6]].sum()) for i in range(len(post) - 5)]
match = [w for w in wins if abs(w[2] - 8.51) < .005]
chk("D", "exactly one six-start post-break window reconciles to 8.51, and it is 7/27-8/24", len(match) == 1 and match[0][:2] == ("2026-07-27", "2026-08-24"), match)
stretch = gd[(gd >= "2026-07-27") & (gd <= "2026-08-24")].index
S, Rr = L26[L26.game_pk.isin(stretch)], L26[~L26.game_pk.isin(stretch)]
rs, rr = rates(S), rates(Rr)
_, p_sbb = z2(rs["bb"], rs["pa"], rr["bb"], rr["pa"])
chk("D", "slide BB 13.4% vs 5.9%, p = .004", close(rs["bbrate"], 0.134, 0.0006) and close(rr["bbrate"], 0.059, 0.0006) and close(p_sbb, H["stretch_tests"]["BB per PA"]["p"], 0.0015),
    f"{rs['bbrate']:.4f} / {rr['bbrate']:.4f} / p {p_sbb:.4f}")
chk("D", "slide K not different (p > .2)", z2(rs["k"], rs["pa"], rr["k"], rr["pa"])[1] > .2)
fin = gd[gd >= "2026-08-30"].index
rf = rates(L26[L26.game_pk.isin(fin)])
chk("D", "finish BB 6.2%, 1.67 runs per 27 outs", close(rf["bbrate"], H["periods"]["finish"]["bbrate"], 0.0006)
    and close(27 * runs_g[fin].sum() / og[fin].sum(), 1.673, 0.002), f"{rf['bbrate']:.4f}")


def misses(d):
    d = d.dropna(subset=["plate_x", "plate_z", "sz_top", "sz_bot"])
    dx = np.maximum(np.abs(d.plate_x) - 0.83, 0); dz = np.maximum.reduce([d.sz_bot - d.plate_z, d.plate_z - d.sz_top, np.zeros(len(d))])
    cm = np.sqrt(dx ** 2 + dz ** 2) > 2 * BALL
    arm = cm & (dx >= dz) & (d.plate_x < 0)        # RHP arm side = third-base side (plate_x < 0, catcher's view)
    return int(cm.sum()), int(arm.sum()), len(d)


cs, as_, _ = misses(S); cr, ar, _ = misses(Rr)
_, p_arm = z2(as_, cs, ar, cr)
chk("D", "arm-side share of clear misses 25.5% vs 17.8%, p = .033", close(as_ / cs, 0.255, 0.0006) and close(ar / cr, 0.178, 0.0006) and close(p_arm, 0.033, 0.0015),
    f"{as_}/{cs} vs {ar}/{cr}, p {p_arm:.4f}")
ff = L26[L26.pitch_type == "FF"].groupby("game_pk").agg(x=("release_pos_x", "mean"), z=("release_pos_z", "mean"))
tx = ttest_ind(ff.loc[ff.index.isin(stretch), "x"], ff.loc[~ff.index.isin(stretch), "x"], equal_var=False).pvalue
tz = ttest_ind(ff.loc[ff.index.isin(stretch), "z"], ff.loc[~ff.index.isin(stretch), "z"], equal_var=False).pvalue
chk("D", "release point did not move (Welch p > .2 on x and height)", tx > .2 and tz > .2 and close(tx, H["stretch_tests"]["FF release x (ft)"]["p"], .002), f"{tx:.3f} / {tz:.3f}")
g162 = gd[gd == "2026-09-27"].index[0]
chk("D", "Game 162: 6.0 IP, 1 run on watch", og[g162] == 18 and runs_g[g162] == 1)
wcp = pa[(pa.pitcher == ID) & (pa.game_pk == 849844)]
wcl = DEF[(DEF.pitcher == ID) & (DEF.game_pk == 849844)]
wr = wcl.groupby("at_bat_number").agg(a=("bat_score", "min"), b=("post_bat_score", "max"))
hrd = wcl[wcl.events == "home_run"].des.iloc[0] if (wcl.events == "home_run").any() else ""
chk("D", "WC G3: 4.0 IP, 2 runs, Albies HR in the 4th, 68 pitches", int(wcp.outs.sum()) == 12 and int((wr.b - wr.a).sum()) == 2 and "Albies" in hrd
    and int(wcl[wcl.events == "home_run"].inning.iloc[0]) == 4 and len(wcl) == 68)

# ---------------------------------------------------------------- E · context, swing timing, platoon, card, parent
def ctx(d):
    out = []
    for (p, y), g in d.groupby(["pitcher", "game_year"]):
        if len(g) < 2000:
            continue
        r = rates(g)
        out.append(dict(pitcher=p, y=y, xwoba=r["xwoba"], kbb=r["krate"] - r["bbrate"]))
    return pd.DataFrame(out)


CX = ctx(PPS)
CX["rk"] = CX.xwoba.rank(method="min").astype(int)
w = CX[(CX.pitcher == ID) & (CX.y == 2026)].iloc[0]
chk("E", "starter workloads n = 41; Wheeler 2026 xwOBA #6", len(CX) == 41 and int(w.rk) == 6, f"n {len(CX)}, rank {int(w.rk)}")
chk("E", "6 of the top-10 starter xwOBA seasons are Wheeler's", int(((CX.pitcher == ID) & (CX.rk <= 10)).sum()) == 6)
chk("E", "K-BB #6 of 41", int((CX.kbb > w.kbb).sum() + 1) == H["ctx_sw"]["rank_k_minus_bb"] == 6)
JP = []
pp = PPS[PPS.game_year >= 2025]
for (p, y), g in pp.groupby(["pitcher", "game_year"]):
    sw = g[g.description.isin(SW_JR) & g.intercept_ball_minus_batter_pos_x_inches.notna()]
    if len(sw) >= 50:
        JP.append(dict(pitcher=p, y=y, n=len(sw), t=(sw.intercept_ball_minus_batter_pos_x_inches < 32.5).mean()))
JP = pd.DataFrame(JP)
wj = JP[(JP.pitcher == ID) & (JP.y == 2026)].iloc[0]
big = JP[JP.n >= 500]
chk("E", "tied-up population: #11 of 45; #6 of 14 with >= 500 swings",
    len(JP) == 45 and int((JP.t > wj.t).sum() + 1) == 11 and len(big) == 14 and int((big.t > wj.t).sum() + 1) == 6)
si = L26[(L26.pitch_type == "SI") & (L26.stand == "R") & L26.description.isin(SW_JR) & (L26.intercept_ball_minus_batter_pos_x_inches < 32.5)]
chk("E", "sinker vs RHB tied up: 124 swings, 55 in play, 14 hits", len(si) == 124 and (si.type == "X").sum() == 55
    and si.events.isin(["single", "double", "triple", "home_run"]).sum() == 14)
rl, rR = rates(L26[L26.stand == "L"]), rates(L26[L26.stand == "R"])
xl = round(rl["hh"] * rl["bip"]); xr = round(rR["hh"] * rR["bip"])
chk("E", "platoon: wOBA L .304 / R .242; hard-hit p < .01", close(rl["woba"], .304, .0006) and close(rR["woba"], .242, .0006)
    and z2(xl, rl["bip"], xr, rR["bip"])[1] < .01)


def sig(d):
    rows = []
    for gp, g in d.sort_values(["game_pk", "at_bat_number", "pitch_number"]).groupby("game_pk"):
        first = g.head(15); ffv = first[first.pitch_type == "FF"].release_speed.mean()
        ooz = g.zone > 9; ev = g.events.fillna("NA"); pa_ = (~ev.isin(["NA", "pickoff_1b"])).sum()
        rows.append(dict(game_pk=gp, A=ffv, B=(ooz & g.description.isin(SW_ALL)).sum() / ooz.sum(),
                         C=100 * g.description.isin(WH).sum() / len(g), D=(ev == "walk").sum() / pa_))
    return pd.DataFrame(rows)


S26 = sig(L26)
bars = dict(A=S26.A.quantile(.25), B=S26.B.quantile(.25), C=S26.C.quantile(.25), D=S26.D.quantile(.75))
card = Rc("still_wheeler_card").set_index("signature")
chk("E", "card bars recomputed (OC-1 quantiles of 2026 starts)", all(close(bars[k], card.loc[f"OC-{k}", "bar"], 1e-6) for k in "ABCD"), {k: round(v, 3) for k, v in bars.items()})
hold = (S26.A >= bars["A"]).astype(int) + (S26.B >= bars["B"]) + (S26.C >= bars["C"]) + (S26.D <= bars["D"])
on = S26.game_pk[hold >= 3]
chk("E", "backtest: 20 on-script / 8 off; on-script runs per 27 outs 2.16",
    len(on) == 20 and close(27 * runs_g[on].sum() / og[on].sum(), H["card"]["on_r27"], 0.002), f"{len(on)} on")
chk("E", "finish 6/6 on-script", set(fin) <= set(on))
fh = L26[L26.game_date.astype(str) < "2026-07-13"]
rfh = rates(fh)
chk("E", "parent uc-pps-020: 15 starts, wOBA .246, K 30.4%, BB 6.2%, chase 36.2%", fh.game_pk.nunique() == 15 and close(rfh["woba"], .246, .0006)
    and close(rfh["krate"], .304, .0006) and close(rfh["bbrate"], .062, .0006) and close(rfh["chase"], .362, .0006))

# ---------------------------------------------------------------- F · published numbers
rep = (ROOT / "dp_uc51_wheeler_2026_recap_report.md").read_text(encoding="utf-8")
dash = (ROOT / "dp_uc51_wheeler_2026_dashboard.html").read_text(encoding="utf-8")
dash_txt = re.sub(r"<script.*?</script>", " ", dash, flags=re.S)
STR = {
    "xwOBA .263": f3(r26["xwoba"]), "BB 7.3%": pct(r26["bbrate"]), "in-zone 42.1%": pct(r26["in_zone"]), "chase 36.2%": pct(r26["chase"]),
    "edge 36.0%": pct(r26["edge"]), "tied-up 32.0%": pct(r26["tied"]), "slide BB 13.4%": pct(rs["bbrate"]), "rest BB 5.9%": pct(rr["bbrate"]),
    "finish BB 6.2%": pct(rf["bbrate"]), "slide p 0.004": f"{p_sbb:.3f}", "arm 25.5%": pct(as_ / cs), "arm 17.8%": pct(ar / cr),
    "arm p 0.033": f"{p_arm:.3f}", "IP 162.0": "162.0", "rank #6 of 41": "#6 of 41", "FF 95.2": f"{r26['velo']:.1f}",
    "hh L 41.9%": pct(rl["hh"]), "hh R 25.7%": pct(rR["hh"]), "wOBA L .304": f3(rl["woba"]), "wOBA R .242": f3(rR["woba"]),
    "on r27 2.16": f"{27 * runs_g[on].sum() / og[on].sum():.2f}", "8.51": "8.51", "1.67": "1.67", "#11 of 45": "#11 of 45",
    "OU-1 480": "480", "MI-1 148": "148",
}
for k, s in STR.items():
    chk("F", f"report states {k}", s in rep, s)
for k in ["xwOBA .263", "BB 7.3%", "in-zone 42.1%", "chase 36.2%", "slide BB 13.4%", "finish BB 6.2%", "IP 162.0", "rank #6 of 41", "8.51", "1.67", "wOBA L .304", "MI-1 148"]:
    chk("F", f"dashboard states {k}", STR[k] in dash_txt, STR[k])
specs = json.loads((OUT / "dp_uc51_figure_specs.json").read_text())
chk("F", "13 figures shipped with brand checks passing", len(specs) == 13 and Rc("brand_compliance").drop(columns=["figure", "off_palette"]).all().all())
for bad in ["lowest of his career", "MLB-best", "best in baseball", "league-leading", "highest of his career"]:
    chk("F", f"banned phrase absent: '{bad}'", bad not in rep.lower() and bad not in dash_txt.lower())
hp = Rc("hp_reconciliation")
chk("F", "18 HP rows, each with a verdict", len(hp) == 18 and hp.verdict.notna().all())

# ---------------------------------------------------------------- G · carry-in discipline
man = Rc("freshness_manifest")
mtxt = " ".join(man.note.astype(str))
for kw in ["thoracic", "$126M", "3.00 ERA", "8.51", "Albies", "42.4", "Game 162"]:
    chk("G", f"freshness manifest carries the carry-in '{kw}'", kw in mtxt)
chk("G", "ERA appears only as a carry-in (3.00 / 8.51), never computed", "ERA" in rep and not re.search(r"ERA (?:of|was) (?!3\.00|8\.51)\d", rep))
for bad in ["because of the surgery", "due to his injury", "injury caused", "the clot caused", "fatigue caused", "was hurt"]:
    chk("G", f"no causal injury language: '{bad}'", bad not in rep.lower() and bad not in dash_txt.lower())
chk("G", "the glove claim is always tagged as reported (carry-in) in both products",
    all(("carry-in" in s or "Reporting" in s or "reported" in s.lower() or "Reported" in s) for s in re.findall(r"[^.]*glove[^.]*\.", rep + dash_txt)
        if "cannot" not in s and "not in the data" not in s and "does not show" not in s and "(Inquirer)" not in s))

LG = pd.DataFrame(LOG)
LG.to_csv(OUT / "dp_uc51_verification_log.csv", index=False)
print(LG.groupby(["family", "result"]).size().unstack(fill_value=0))
print("TOTAL", f"{int((LG.result == 'PASS').sum())}/{len(LG)}")
fails = LG[LG.result == "FAIL"]
if len(fails):
    print(fails.to_string())
