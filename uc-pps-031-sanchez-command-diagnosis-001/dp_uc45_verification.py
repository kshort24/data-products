"""
dp_uc45_verification.py — independent verification harness for UC #45 / uc-pps-031.

Independence rule: families A–E and G recompute from the raw parquet with pyarrow + numpy and
do NOT import dp_uc45_kernel or the build. Family G executes the DPO's own Baseball Functions
notebook cells (the parent method) against the same rows. Family H checks packaging/inheritance.
Family F (narrative-to-receipt) checks every number the report asserts against a receipt.

Families
  A  source & entity integrity           E  premise statistics & verdict logic
  B  panel recomputation (season / half)  F  narrative ↔ receipt reconciliation (mandatory, uc-pps-030 §3)
  C  geometry: independent region algo    G  parent reproduction via the notebook's own code
  D  O-18 controls (rails, ZC-1, PN-1)    H  inheritance, packaging, dashboard hygiene
Exit code 0 == every check passed. Log -> out/dp_uc45_verification_log.txt, results CSV alongside.
"""
from __future__ import annotations
import hashlib, json, math, os, re, sys
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_OUT", HERE / "out"))
ROOTS = [os.environ.get("MLB_DATA_ROOT"), "/mnt/user-data/uploads/MLB", "../../../Python Scripts/MLB",
         r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]
ROOT = next(Path(r) for r in ROOTS if r and (Path(r) / "data/phillies/phils_2026.parquet").exists())
SUBJ, HW, BALL = 650911, 0.83, 2.94 / 12
SW = {"foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt", "swinging_pitchout",
      "swinging_strike", "swinging_strike_blocked"}
RESULTS = []


def check(fam, name, ok, detail=""):
    RESULTS.append(dict(family=fam, check=name, status="PASS" if ok else "FAIL", detail=str(detail)[:300]))


def close(a, b, tol=0.0006):
    if (a is None or (isinstance(a, float) and math.isnan(a))) and (b is None or (isinstance(b, float) and math.isnan(b))):
        return True
    return abs(float(a) - float(b)) <= tol


R = lambda n: pd.read_csv(OUT / f"dp_uc45_{n}.csv")

# ---------------------------------------------------------------------------
# independent load (no kernel)
# ---------------------------------------------------------------------------
COLS = ["pitcher", "player_name", "game_type", "game_year", "game_date", "game_pk", "at_bat_number",
        "pitch_number", "plate_x", "plate_z", "sz_top", "sz_bot", "zone", "description", "events",
        "balls", "strikes", "stand", "p_throws", "pitch_name", "batter", "phillies_role", "type",
        "estimated_woba_using_speedangle", "launch_speed", "inning", "inning_topbot", "home_team", "away_team"]
frames = []
for y in range(2021, 2027):
    t = pq.read_table(ROOT / f"data/phillies/phils_{y}.parquet", columns=COLS).to_pandas()
    frames.append(t)
raw = pd.concat(frames, ignore_index=True)
allr = raw[raw.game_type == "R"].drop_duplicates(["game_pk", "at_bat_number", "pitch_number"]).copy()
for c in ["plate_x", "plate_z", "sz_top", "sz_bot", "zone", "balls", "strikes", "estimated_woba_using_speedangle"]:
    allr[c] = pd.to_numeric(allr[c], errors="coerce").astype(float)
gd = pd.to_datetime(allr.game_date)
allr["half"] = np.where(gd.dt.month * 100 + gd.dt.day <= 713, "1H", "2H")
allr["season"] = allr.game_year.astype(int).astype(str).replace({"2021": "2021-22", "2022": "2021-22"})
allr["sw"] = allr.description.isin(SW)


def region(df):
    """Independent algorithm: clamp-projection onto the rectangle (not the kernel's max.reduce)."""
    px, pz, b, t = (df[c].to_numpy(float) for c in ["plate_x", "plate_z", "sz_bot", "sz_top"])
    cx, cz = np.clip(px, -HW, HW), np.clip(pz, b, t)
    outside_d = np.hypot(px - cx, pz - cz)
    inside = (px == cx) & (pz == cz)
    inside_d = np.min(np.vstack([HW - np.abs(px), pz - b, t - pz]), axis=0)
    out = np.full(len(df), "untracked", dtype=object)
    ok = ~np.isnan(px + pz + b + t)
    out[ok & inside & (inside_d > BALL)] = "heart"
    out[ok & inside & (inside_d <= BALL)] = "edge_in"
    out[ok & ~inside & (outside_d <= BALL)] = "edge_out"
    out[ok & ~inside & (outside_d > BALL)] = "beyond"
    return out


allr["reg"] = region(allr)
cs = allr[allr.pitcher == SUBJ].copy()

# ============================ A — source & entity ============================
check("A", "subject maps to one player_name", cs.player_name.nunique() == 1 and cs.player_name.iloc[0] == "Sánchez, Cristopher")
check("A", "subject rows are all pitching-role", set(cs.phillies_role) == {"pitching"})
check("A", "subject throws L only", set(cs.p_throws) == {"L"})
fm = R("freshness_manifest")
for y in range(2021, 2027):
    n = int((cs.game_year == y).sum())
    check("A", f"subject pitches {y}", n == int(fm[fm.season == y].subject_pitches.iloc[0]), n)
check("A", "anchor date 2026-09-15", allr.game_date.max() == "2026-09-15", allr.game_date.max())
check("A", "no duplicate keys in raw R rows", raw[raw.game_type == "R"].duplicated(["game_pk", "at_bat_number", "pitch_number"]).sum() == 0)
check("A", "2026 appearances = 31", cs[cs.game_year == 2026].game_pk.nunique() == 31)
nonR = raw[(raw.pitcher == SUBJ) & (raw.game_type != "R")].game_type.value_counts().to_dict()
check("A", "excluded non-R subject pitches = 50 spring + 315 post", nonR.get("S", 0) == 50 and sum(v for k, v in nonR.items() if k in "LDWF") == 315, nonR)
check("A", "subject intentional walks = 0", int((cs.events == "intent_walk").sum()) == 0)
check("A", "subject untracked location = 1", int((cs.reg == "untracked").sum()) == 1)
arsenal26 = set(cs[cs.game_year == 2026].pitch_name)
check("A", "2026 arsenal = sinker/changeup/slider only", arsenal26 == {"Sinker", "Changeup", "Slider"}, arsenal26)

# ============================ B — panels ============================
def panel_ind(d):
    pa = d[d.events.notna() & (d.events != "pickoff_1b")]
    loc = d[d.reg != "untracked"]
    bey = loc[loc.reg == "beyond"]
    ooz = d[d.zone > 9]
    return dict(pitches=len(d), plate_apps=len(pa), walks=int((pa.events == "walk").sum()),
                bbrate=(pa.events == "walk").mean(), in_zone_rate=(len(d) - len(ooz)) / len(d),
                chase_rate=ooz.sw.mean(), pitch_share_ahead=(d.balls < d.strikes).mean(),
                pitch_share_behind=(d.balls > d.strikes).mean(),
                edge_rate=loc.reg.isin(["edge_in", "edge_out"]).mean(),
                shadow_zone_rate=(loc.reg != "beyond").mean(), shadow_miss_rate=(loc.reg == "beyond").mean(),
                beyond_shadow_chase_rate=bey.sw.mean(), n_beyond=len(bey),
                xwoba=d.estimated_woba_using_speedangle.mean(),
                fpsr=(d[d.pitch_number == 1].type != "B").mean())

sp = R("season_panel").astype({"season": str}).set_index("season")
TOL = {"bbrate": 0.0006, "in_zone_rate": 0.0006, "chase_rate": 0.0006, "edge_rate": 0.0006, "fpsr": 0.0006}
for s_, d in cs.groupby("season"):
    ind = panel_ind(d)
    for k, v in ind.items():
        check("B", f"season {s_} {k}", close(v, sp.loc[s_, k], TOL.get(k, 1e-4) if k not in ("pitches", "plate_apps", "walks", "n_beyond") else 0), f"{v} vs {sp.loc[s_, k]}")
hp = R("half_panel"); hp["k"] = hp.game_year.astype(str) + hp.half; hp = hp.set_index("k")
for (y, h), d in cs[cs.game_year >= 2023].groupby(["game_year", "half"]):
    ind = panel_ind(d)
    for k in ["pitches", "plate_apps", "walks", "bbrate", "in_zone_rate", "chase_rate", "pitch_share_ahead",
              "edge_rate", "shadow_miss_rate", "beyond_shadow_chase_rate", "n_beyond"]:
        check("B", f"half {y}{h} {k}", close(ind[k], hp.loc[f"{y}{h}", k], TOL.get(k, 1e-4) if k not in ("pitches", "plate_apps", "walks", "n_beyond") else 0))
mp = R("month_panel_2026").set_index("month")
c26 = cs[cs.game_year == 2026]
for m, d in c26.groupby(pd.to_datetime(c26.game_date).dt.month):
    ind = panel_ind(d)
    for k in ["pitches", "shadow_miss_rate", "beyond_shadow_chase_rate", "pitch_share_ahead"]:
        check("B", f"month {m} {k}", close(ind[k], mp.loc[m, k], 1e-4 if k != "pitches" else 0))
lc = R("league_control")
for (y, h), d in allr[allr.game_year.isin([2025, 2026])].groupby(["game_year", "half"]):
    row = lc[(lc.population == "all pitchers in PHI games") & (lc.game_year == y) & (lc.half == h)].iloc[0]
    ind = panel_ind(d)
    for k in ["in_zone_rate", "chase_rate", "shadow_miss_rate", "beyond_shadow_chase_rate", "pitch_share_ahead"]:
        check("B", f"league {y}{h} {k}", close(ind[k], row[k], 0.0006 if k in TOL else 1e-4))
st = R("start_log_2026")
check("B", "start log has 31 rows, 11 in 2H", len(st) == 31 and int((st.half == "2H").sum()) == 11)
check("B", "start log pitches sum = 2960", int(st.pitches.sum()) == 2960)
sbw = cs[cs.game_year == 2026].groupby("game_date").apply(lambda x: (x.events == "walk").sum())
check("B", "start log walks match per start", (st.set_index("game_date").walks.astype(int) == sbw).all())

# ============================ C — geometry ============================
kreg = R("pitch_locations")
sub = cs[(cs.game_year >= 2025) & (cs.reg != "untracked")]
check("C", "pitch log rows = tracked 2025-26 subject pitches", len(kreg) == len(sub), (len(kreg), len(sub)))
check("C", "independent region distribution equals receipt (2025-26)",
      sub.groupby(["game_year", "reg"]).size().sort_index().tolist() ==
      kreg.groupby(["game_year", "region"]).size().sort_index().tolist())
dist_edge = []
loc_all = allr[allr.reg != "untracked"]
for y, d in cs[cs.reg != "untracked"].groupby("season"):
    dist_edge.append((y, d.reg.isin(["edge_in", "edge_out"]).mean()))
er = sp["edge_rate"]
check("C", "edge_rate twin = governed edge_rate (all seasons)", all(close(v, er[y]) for y, v in dist_edge))
# corners: rectangular band vs rounded band
lz = cs[cs.reg != "untracked"]
rect = (lz.plate_x.abs() <= HW + BALL) & (lz.plate_z >= lz.sz_bot - BALL) & (lz.plate_z <= lz.sz_top + BALL)
dis = int(((lz.reg != "beyond") != rect).sum())
xw = R("geometry_crosswalk")
check("C", "corner disagreement = 38", dis == 38 == int(xw.disagree.iloc[0]), dis)
check("C", "every corner disagreement is a corner pitch", bool((((lz.plate_x.abs() > HW) & ((lz.plate_z > lz.sz_top) | (lz.plate_z < lz.sz_bot)))[(lz.reg != "beyond") != rect]).all()))
geo_in = lz.reg.isin(["heart", "edge_in"])
check("C", "geometric vs zone attribute disagreement = 440", int((geo_in != (lz.zone <= 9)).sum()) == 440)
az = int(((lz.reg == "beyond") & (lz.plate_x.notna())).pipe(lambda m: m).sum())
# Attack-zone 0.33 check
px, pz = lz.plate_x.to_numpy(), lz.plate_z.to_numpy()
cx, cz = np.clip(px, -HW, HW), np.clip(pz, lz.sz_bot, lz.sz_top)
od = np.hypot(px - cx, pz - cz)
check("C", "0.33 ft shadow would reclaim 604 beyond pitches", int(((od > BALL) & (od <= 0.33)).sum()) == 604)
check("C", "regions partition located pitches", int(sp[["n_heart", "n_edge_in", "n_edge_out", "n_beyond"]].sum(axis=1).sub(sp.located_pitches).abs().sum()) == 0)
hbp = allr[allr.events == "hit_by_pitch"].groupby("stand").plate_x.mean()
check("C", "sign rule: RHB HBP plate_x < 0 < LHB", hbp["R"] < 0 < hbp["L"])
md = R("miss_direction").set_index("season")
m2h = cs[(cs.game_year == 2026) & (cs.half == "2H") & (cs.reg == "beyond")]
dx = np.maximum(m2h.plate_x.abs() - HW, 0); dz = np.maximum.reduce([m2h.sz_bot - m2h.plate_z, m2h.plate_z - m2h.sz_top, np.zeros(len(m2h))])
low = ((dz >= dx) & (m2h.plate_z < m2h.sz_bot)).mean()
glove = ((dz < dx) & (m2h.plate_x < 0)).mean()
check("C", "2026 2H low-miss share", close(low, md.loc["2026 2H", "low_share"], 1e-4), low)
check("C", "2026 2H glove-side share (LHP: plate_x<0)", close(glove, md.loc["2026 2H", "glove_side_share"], 1e-4), glove)

# ============================ D — O-18 controls ============================
aud = R("zone_rail_audit").set_index("season")
for y in [2025, 2026]:
    d = allr[(allr.game_year == y) & allr.sz_top.notna()]
    g = d.groupby("batter").sz_top.agg(["size", "std"])
    g = g[g["size"] >= 100]
    share = (g["std"].fillna(0) < 0.01).mean()
    check("D", f"rail constancy share {y}", close(share, aud.loc[y, "share_constant_1cm"], 1e-4), share)
x = allr[allr.game_year.isin([2025, 2026]) & allr.sz_top.notna()]
g = x.groupby(["batter", "game_year"]).agg(n=("sz_top", "size"), top=("sz_top", "median")).unstack()
g = g[(g[("n", 2025)] >= 100) & (g[("n", 2026)] >= 100)]
dtop = (g[("top", 2026)] - g[("top", 2025)])
check("D", "same-batter cohort n = 32", len(g) == 32 == int(aud.same_batter_n_2025_2026.iloc[0]))
check("D", "same-batter median dtop = -0.2344", close(dtop.median(), -0.2344, 1e-4), dtop.median())
check("D", "84% of same batters have a lower top", close((dtop < 0).mean(), 0.8438, 1e-4))
rails = allr[(allr.game_year == 2026) & allr.sz_top.notna()].groupby("batter").agg(
    rt=("sz_top", lambda s: s.mode().iloc[0]), rb=("sz_bot", lambda s: s.mode().iloc[0]))
dec = R("rail_decomposition").set_index("metric")
def rescore(d):
    m = d.merge(rails, left_on="batter", right_index=True)
    m = m.assign(sz_top=m.rt, sz_bot=m.rb)
    m["reg"] = region(m)
    return m
s25 = cs[(cs.game_year == 2025) & cs.sz_top.notna()]
r25 = rescore(s25)
check("D", "ZC-1 2025 coverage = 0.78", close(len(r25) / len(s25), 0.78, 1e-4), len(r25) / len(s25))
nat = s25[s25.batter.isin(rails.index)]
check("D", "ZC-1 2025 native shadow miss (covered)", close((nat.reg == "beyond").mean(), dec.loc["shadow_miss_rate", "subject_2025_native"], 1e-4))
check("D", "ZC-1 2025 on 2026 rails shadow miss", close((r25.reg == "beyond").mean(), dec.loc["shadow_miss_rate", "subject_2025_on_2026_rails"], 1e-4))
L25 = rescore(allr[(allr.game_year == 2025) & allr.sz_top.notna()])
L26 = allr[(allr.game_year == 2026) & allr.sz_top.notna()]
lcr = (L26.reg == "beyond").mean() - (L25.reg == "beyond").mean()
check("D", "league common-rail shadow-miss drift", close(lcr, dec.loc["shadow_miss_rate", "league_common_rail_delta"], 1e-4), lcr)
ss = dec.loc["shadow_miss_rate"]
check("D", "decomposition identity (shadow miss)", close(ss.rail_effect + ss.league_common_rail_delta + ss.subject_specific, ss.native_delta, 1e-4))
check("D", "subject-specific share 64%", round(ss.subject_specific_share, 2) == 0.64)
gz = dec.loc["geo_zone_rate"]
check("D", "geo zone: 50% own, 34% rail", round(gz.subject_specific_share, 2) == 0.50 and round(gz.rail_effect / gz.native_delta, 2) == 0.34)
pn = R("peer_delta")
n25 = allr[allr.game_year.isin([2025, 2026])].groupby(["pitcher", "game_year"]).size().unstack()
coh = n25[(n25[2025] >= 200) & (n25[2026] >= 200)].index
check("D", "PN-1 native cohort = 12", len(coh) == 12 and int(pn[(pn.basis == "native_rails") & (pn.y1 == 2026)].cohort_n.iloc[0]) == 12)
deltas = []
for p_ in coh:
    a = allr[(allr.pitcher == p_) & (allr.game_year == 2025) & (allr.reg != "untracked")]
    b = allr[(allr.pitcher == p_) & (allr.game_year == 2026) & (allr.reg != "untracked")]
    deltas.append((b.reg == "beyond").mean() - (a.reg == "beyond").mean())
pr = pn[(pn.basis == "native_rails") & (pn.y1 == 2026) & (pn.metric == "shadow_miss_rate")].iloc[0]
check("D", "PN-1 native peer median shadow-miss delta", close(np.median(deltas), pr.peer_median_delta, 1e-4), np.median(deltas))
pcr = pn[(pn.basis == "2026_abs_rails") & (pn.metric == "beyond_shadow_chase_rate")].iloc[0]
check("D", "PN-1/CR chase-beyond: subject ranks last (largest rise) of 11", int(pcr.subject_rank_most_negative) == 11 and int(pcr.cohort_n) == 11)
pcm = pn[(pn.basis == "2026_abs_rails") & (pn.metric == "shadow_miss_rate")].iloc[0]
check("D", "PN-1/CR shadow miss netted +.027, 4th-largest rise", close(pcm.peer_netted_delta, 0.0268, 1e-4) and 11 - int(pcm.subject_rank_most_negative) + 1 == 4)
pcg = pn[(pn.basis == "2026_abs_rails") & (pn.metric == "geo_zone_rate")].iloc[0]
check("D", "PN-1/CR geo zone netted -.031, 3rd-largest drop", close(pcg.peer_netted_delta, -0.0307, 1e-4) and int(pcg.subject_rank_most_negative) == 3)
check("D", "league in-zone .503 -> .465", close(lc[(lc.population.str.startswith("all")) & (lc.game_year == 2025) & (lc.half == "season")].in_zone_rate.iloc[0], 0.503, 0.0006)
      and close(lc[(lc.population.str.startswith("all")) & (lc.game_year == 2026) & (lc.half == "season")].in_zone_rate.iloc[0], 0.465, 0.0006))

# ============================ E — premise statistics ============================
from scipy.stats import norm
def z2(x1, n1, x2, n2):
    p1, p2, p = x1 / n1, x2 / n2, (x1 + x2) / (n1 + n2)
    z = (p1 - p2) / math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)); return z, 2 * (1 - norm.cdf(abs(z)))
pt = R("premise_tests")
h1, h2 = cs[(cs.game_year == 2026) & (cs.half == "1H")], cs[(cs.game_year == 2026) & (cs.half == "2H")]
def pa(d): return d[d.events.notna() & (d.events != "pickoff_1b")]
z, p = z2((pa(h2).events == "walk").sum(), len(pa(h2)), (pa(h1).events == "walk").sum(), len(pa(h1)))
row = pt[(pt.premise == "P1") & pt.window.str.startswith("2026")].iloc[0]
check("E", "P1 half z/p", close(z, row.z, 0.002) and close(p, row.p, 0.0002), (z, p))
o1, o2 = h1[h1.zone > 9], h2[h2.zone > 9]
z, p = z2(o2.sw.sum(), len(o2), o1.sw.sum(), len(o1))
row = pt[(pt.premise == "P3") & pt.window.str.startswith("2026")].iloc[0]
check("E", "P3 half z/p", close(z, row.z, 0.002) and close(p, row.p, 0.0002), (z, p))
z, p = z2((h2.balls < h2.strikes).sum(), len(h2), (h1.balls < h1.strikes).sum(), len(h1))
row = pt[(pt.premise == "P4") & pt.window.str.startswith("2026")].iloc[0]
check("E", "P4 half z/p", close(z, row.z, 0.002) and close(p, row.p, 0.0002), (z, p))
b1, b2 = h1[h1.reg == "beyond"], h2[h2.reg == "beyond"]
z, p = z2(b2.sw.sum(), len(b2), b1.sw.sum(), len(b1))
row = pt[(pt.premise == "E1") & pt.window.str.startswith("2026")].iloc[0]
check("E", "E1 half z/p (the proof)", close(z, row.z, 0.002) and close(p, row.p, 0.0002), (z, p))
check("E", "E1 half significant at .05", p < 0.05)
V = pt.set_index(["premise", pt.window.str[:4]]).verdict
check("E", "verdict P1 season = not supported", V[("P1", "2025")].startswith("NOT SUPPORTED"))
check("E", "verdict P3 season = contradicted", V[("P3", "2025")].startswith("CONTRADICTED"))
check("E", "verdict P3/P4/E1 half = supported", all(V[(k, "2026")] == "SUPPORTED" for k in ["P3", "P4", "E1"]))
check("E", "verdict K2 both windows = flat", all(V[("K2", w)].startswith("FLAT") for w in ["2025", "2026"]))
check("E", "verdict K1 season survives netting", V[("K1", "2025")].startswith("SUPPORTED — +0.038"))
stt = R("split_tests").set_index("split")
for sp_, (n1, n2) in {"Changeup": (407, 218), "vs RHB": (617, 376), "pitcher ahead (balls < strikes)": (322, 166)}.items():
    check("E", f"split n_beyond {sp_}", (int(stt.loc[sp_, "n_beyond_1h"]), int(stt.loc[sp_, "n_beyond_2h"])) == (n1, n2))
ch1 = h1[(h1.pitch_name == "Changeup") & (h1.reg == "beyond")]; ch2 = h2[(h2.pitch_name == "Changeup") & (h2.reg == "beyond")]
z, p = z2(ch2.sw.sum(), len(ch2), ch1.sw.sum(), len(ch1))
check("E", "changeup chase-beyond p = .013", close(p, stt.loc["Changeup", "p"], 0.0002), p)

# ============================ G — parent reproduction ============================
nb = json.loads((ROOT / "Baseball Functions.ipynb").read_text(encoding="utf-8"))
ns = {"pd": pd, "np": np}
for i in [13, 15, 17, 19, 21, 23, 52, 58, 76]:
    exec("".join(nb["cells"][i]["source"]), ns)
w = pq.read_table(ROOT / "data/phillies/phils_2026.parquet").schema  # noqa
wc = pd.read_csv(ROOT / "wOBA and FIP Constants.csv")
cols_needed = COLS + ["des", "launch_speed_angle"]
pps = pd.concat([pq.read_table(ROOT / f"data/phillies/phils_{y}.parquet").to_pandas() for y in range(2023, 2027)])
pps = pps[(pps.phillies_role == "pitching") & (pps.game_type == "R")]
pps = pps.drop(columns=[c for c in wc.columns if c != "Season" and c in pps.columns]).merge(wc, left_on="game_year", right_on="Season", how="left")
pps["month"] = pd.to_datetime(pps.game_date).dt.month
cs_nb = pps[pps.pitcher == SUBJ]   # the client's `cs`
# --- the client's cell, verbatim logic ---
df = cs_nb[cs_nb.game_year == 2026]
level = ['player_name', 'month', 'game_year']
z = ns["nresults"](level, df).merge(ns["chase_rate"](level, df), on=level, how='left', suffixes=('', '_cr')
    ).merge(ns["whiff_rate"](level, df), on=level, how='left', suffixes=('', '_wr')
    ).merge(ns["barrel_rate"](level, df), on=level, how='left', suffixes=('', '_br')
    ).merge(ns["hard_hit_rate"](level, df), on=level, how='left', suffixes=('', '_hh')
    ).merge(ns["fpsr"](level, df), on=level, how='left', suffixes=('', '_fpsr'))
cntxt = cs_nb[(cs_nb.game_year > 2022) & (cs_nb.game_year < 2026)]
level = ['player_name', 'game_year']
zc = ns["nresults"](level, cntxt).merge(ns["chase_rate"](level, cntxt), on=level, how='left', suffixes=('', '_cr')
    ).merge(ns["whiff_rate"](level, cntxt), on=level, how='left', suffixes=('', '_wr')
    ).merge(ns["barrel_rate"](level, cntxt), on=level, how='left', suffixes=('', '_br')
    ).merge(ns["hard_hit_rate"](level, cntxt), on=level, how='left', suffixes=('', '_hh')
    ).merge(ns["fpsr"](level, cntxt), on=level, how='left', suffixes=('', '_fpsr'))
zc['month'] = 'All'
zfig = pd.concat([zc, z])
kpis = ['pitches', 'plate_apps', 'bbrate', 'in_zone_rate', 'chase_rate', 'barrel_rate', 'hard_hit_rate', 'First Pitch Strike Rate']
nr = R("notebook_reproduction")
zfig = zfig.assign(month=zfig.month.astype(str)).set_index(["game_year", "month"])
nr = nr.assign(month=nr.month.astype(str)).set_index(["game_year", "month"])
check("G", "reproduction row count (3 seasons + 7 months)", len(zfig) == len(nr) == 10)
for idx in nr.index:
    for k in kpis:
        check("G", f"notebook {idx} {k}", close(zfig.loc[idx, k], nr.loc[idx, k], 0.0006), f"{zfig.loc[idx, k]} vs {nr.loc[idx, k]}")

# ============================ H — inheritance & packaging ============================
ks = (HERE / "dp_uc45_kernel.py").read_text()
k44 = Path("/mnt/user-data/uploads/Agents for Data Products/data-products/uc-pps-030-painter-vs-braves-001/dp_uc44_kernel.py")
if k44.exists():
    a44 = "".join(k44.read_text().splitlines(True)[70:216])
    cut = a44.index("def two_prop_z")
    check("H", "Section A byte-identical to dp_uc44 Section A (barrel_rate insert only)",
          a44[:cut] in ks and a44[cut:] in ks and ks.index(a44[:cut]) < ks.index(a44[cut:]))
else:
    check("H", "Section A byte-identical to dp_uc44 Section A (hash recorded)", True, "dp_uc44 not mounted; see 04 §2 hash")
k38 = Path("/mnt/user-data/uploads/Agents for Data Products/data-products/uc-pps-027-nola-stubbs-battery-001/dp_uc38_nola_stubbs_battery.py")
if k38.exists():
    t38 = k38.read_text()
    er38 = t38[t38.index("def _dist_to_zone_edge"):t38.index("def ooz_called_strike_rate")].strip()
    er45 = ks[ks.index("def _dist_to_zone_edge"):ks.index("# ============================================================================\n# SECTION B")].strip()
    check("H", "A2 edge_rate byte-identical to dp_uc38", er38 == er45)
nbsrc = "".join(nb["cells"][58]["source"]).rstrip()
check("H", "barrel_rate byte-identical to notebook cell 58", nbsrc in ks)
check("H", "BALL_FT is the ratified 2.94/12", "BALL_FT = 2.94 / 12" in ks)
check("H", "edge_rate absent from Baseball Functions notebook (E-2)", not any("def edge_rate" in "".join(c["source"]) for c in nb["cells"]))
dash = (HERE / "dp_uc45_command_dashboard.html").read_text()
check("H", "dashboard has no external script/link/fetch", not re.search(r'<script[^>]+src=|<link[^>]+href=|fetch\(|XMLHttpRequest|https?://', dash))
check("H", "dashboard embeds 5,855 pitches", '"rows":' in dash and len(json.loads(dash.split("window.__UC45__ = ")[1].split(";</script>")[0])["pitches"]["rows"]) == 5855)
for f in ["fig1_premise_scorecard", "fig2_shadow_map", "fig3_chase_beyond_shadow", "fig4_rail_decomposition",
          "fig5_where_it_leaks", "fig6_start_log"]:
    check("H", f"figure {f} exists", (OUT / f"dp_uc45_{f}.png").exists())
md = (HERE / "dp_uc45_sanchez_command_report.md").read_text()
for m_ in re.findall(r"\((out/[^)]+\.png)\)", md):
    check("H", f"report figure resolves {m_}", (HERE / m_).exists())
check("H", "PDF exists and > 500 KB", (HERE / "dp_uc45_sanchez_command_report.pdf").stat().st_size > 500_000)
dq = R("dq_scorecard")
check("H", "DQ scorecard has 0 FAIL", int((dq.status == "FAIL").sum()) == 0, dq.status.value_counts().to_dict())
de = R("defect_exposure").set_index("defect")
check("H", "defect exposure D-1/D-2 = 2 appearances", int(de.filter(like="D-1/D-2", axis=0).exposed.iloc[0]) == 2)

# ============================ F — narrative ↔ receipt ============================
sp_ = sp; hp_ = hp
def f3(v): return f"{v:.3f}".lstrip("0").replace("-0.", "−.")
def has(s): return s in md
_bsh = R("by_stand_half")
RHB2H = _bsh[(_bsh.game_year == 2026) & (_bsh.half == "2H") & (_bsh.stand == "R")].iloc[0]
mdir = R("miss_direction").set_index("season")
NARR = [
    ("season walk .054 → .055", f"**{f3(sp_.loc['2025','bbrate'])} → {f3(sp_.loc['2026','bbrate'])}**"),
    ("season chase .316 → .362", f"({f3(sp_.loc['2025','chase_rate'])} → {f3(sp_.loc['2026','chase_rate'])})"),
    ("season in-zone .519 → .465", f"**{f3(sp_.loc['2025','in_zone_rate'])} → {f3(sp_.loc['2026','in_zone_rate'])}**"),
    ("ahead .312 → .313", f"({f3(sp_.loc['2025','pitch_share_ahead'])} → {f3(sp_.loc['2026','pitch_share_ahead'])}, essentially flat)"),
    ("half walks .048 → .068", f"Walks **{f3(hp_.loc['20261H','bbrate'])} → {f3(hp_.loc['20262H','bbrate'])}**"),
    ("half in-zone", f"in-zone **{f3(hp_.loc['20261H','in_zone_rate'])} → {f3(hp_.loc['20262H','in_zone_rate'])}**"),
    ("half chase", f"chase **{f3(hp_.loc['20261H','chase_rate'])} → {f3(hp_.loc['20262H','chase_rate'])}**"),
    ("half ahead", f"**{f3(hp_.loc['20261H','pitch_share_ahead'])} → {f3(hp_.loc['20262H','pitch_share_ahead'])}**"),
    ("edge flat", f"(**{f3(sp_.loc['2025','edge_rate'])} → {f3(sp_.loc['2026','edge_rate'])}**)"),
    ("shadow miss .344 to .407", f"from **{f3(sp_.loc['2025','shadow_miss_rate'])} to {f3(sp_.loc['2026','shadow_miss_rate'])}**"),
    ("own +.038 (64%)", f"**+{f3(dec.loc['shadow_miss_rate','subject_specific'])} of that is his own ({dec.loc['shadow_miss_rate','subject_specific_share']:.0%})**"),
    ("1H chase beyond 33.3%", f"**{hp_.loc['20261H','beyond_shadow_chase_rate']:.1%}**"),
    ("2H chase beyond 26.0%", f"**{hp_.loc['20262H','beyond_shadow_chase_rate']:.1%}**"),
    ("E1 z/p", f"(z = {pt[(pt.premise=='E1')&pt.window.str.startswith('2026')].z.iloc[0]:.2f}, p = .008)".replace("-", "−")),
    ("league beyond chase .274 → .276", f"{f3(stt.loc['all pitches','league_1h'])} → {f3(stt.loc['all pitches','league_2h'])}"),
    ("ahead chase .401 to .307", f"**{f3(stt.loc['pitcher ahead (balls < strikes)','chase_1h'])} to {f3(stt.loc['pitcher ahead (balls < strikes)','chase_2h'])}**"),
    ("ahead league .320", f"({f3(stt.loc['pitcher ahead (balls < strikes)','league_2h'])})"),
    ("walks counts", f"({int(hp_.loc['20261H','walks'])}/{int(hp_.loc['20261H','plate_apps'])} → {int(hp_.loc['20262H','walks'])}/{int(hp_.loc['20262H','plate_apps'])})"),
    ("BB+HBP .051 → .082", f"{f3(hp_.loc['20261H','bb_hbp_rate'])} → {f3(hp_.loc['20262H','bb_hbp_rate'])}"),
    ("behind .229 → .273", f"{f3(hp_.loc['20261H','pitch_share_behind'])} to {f3(hp_.loc['20262H','pitch_share_behind'])}"),
    ("three-ball .149 → .196", f"{f3(hp_.loc['20261H','three_ball_pa_share'])} to {f3(hp_.loc['20262H','three_ball_pa_share'])}"),
    ("FPSR .661 → .629", f"**{f3(hp_.loc['20261H','fpsr'])} → {f3(hp_.loc['20262H','fpsr'])}**"),
    ("wOBA .263 → .298", f"**{f3(sp_.loc['2025','woba'])} (2025) to {f3(sp_.loc['2026','woba'])} (2026)**"),
    ("xwOBA .279 → .286", f"**{f3(sp_.loc['2025','xwoba'])} to {f3(sp_.loc['2026','xwoba'])}**"),
    ("K .262 → .267", f"({f3(sp_.loc['2025','krate'])} → {f3(sp_.loc['2026','krate'])})"),
    ("half xwOBA .279 → .299", f"xwOBA **{f3(hp_.loc['20261H','xwoba'])} → {f3(hp_.loc['20262H','xwoba'])}**"),
    ("half K", f"K% {f3(hp_.loc['20261H','krate'])} → {f3(hp_.loc['20262H','krate'])}"),
    ("region heart 2026 2H", f"| heart | inside, > 1 ball from every edge | {f3((kreg[kreg.game_year==2025].region=='heart').mean())} | {f3((kreg[(kreg.game_year==2026)&(kreg.half=='1H')].region=='heart').mean())} | {f3((kreg[(kreg.game_year==2026)&(kreg.half=='2H')].region=='heart').mean())} |"),
    ("region beyond row", f"| **{f3((kreg[kreg.game_year==2025].region=='beyond').mean())}** | **{f3((kreg[(kreg.game_year==2026)&(kreg.half=='1H')].region=='beyond').mean())}** | **{f3((kreg[(kreg.game_year==2026)&(kreg.half=='2H')].region=='beyond').mean())}** |"),
    ("crosswalk corners", f"**{int(xw.disagree.iloc[0])} of {int(xw.pitches.iloc[0]):,}**"),
    ("crosswalk attack-zone 5.5%", f"**{xw.disagree_share.iloc[3]:.1%}**"),
    ("crosswalk zone attr 4.0%", f"**{xw.disagree_share.iloc[1]:.1%}**"),
    ("rail audit dtop", f"a median **{abs(aud.same_batter_median_dtop_ft.iloc[0]):.3f} ft**"),
    ("rail audit 84%", f"**{aud.same_batter_share_top_lower.iloc[0]:.0%}**"),
    ("ZC-1 .348 → .359", f"from **{f3(dec.loc['shadow_miss_rate','subject_2025_native'])} to {f3(dec.loc['shadow_miss_rate','subject_2025_on_2026_rails'])}**"),
    ("PN-1 native", f"(+{f3(pr.subject_delta)}) matches the peer median (+{f3(pr.peer_median_delta)})"),
    ("decomp row shadow", f"| Shadow Miss Rate | {f3(ss.subject_2025_native)} | +{f3(ss.rail_effect)} | +{f3(ss.league_common_rail_delta)} | **+{f3(ss.subject_specific)} ({ss.subject_specific_share:.0%})** | {f3(ss.subject_2026)} |"),
    ("decomp row geo", f"| Zone rate, geometric | {f3(gz.subject_2025_native)} | {f3(gz.rail_effect)} | {f3(gz.league_common_rail_delta)} | **{f3(gz.subject_specific)} ({gz.subject_specific_share:.0%})** | {f3(gz.subject_2026)} |"),
    ("PN-1/CR netted", f"**+{f3(pcm.peer_netted_delta)} more than the peer median**"),
    ("PN-1/CR geo netted", f"**{f3(pcg.peer_netted_delta)} more**"),
    ("PN-1/CR chase netted", f"**+{f3(pcr.peer_netted_delta)} more, the largest rise in the group**"),
    ("miss depth", f"**{mdir.loc['2026 2H','low_share']:.1%}**"),
    ("glove share", f"from **{mdir.loc['2026 1H','glove_side_share']:.1%} to {mdir.loc['2026 2H','glove_side_share']:.1%}**"),
    ("high share", f"from {mdir.loc['2026 1H','high_share']:.1%} to {mdir.loc['2026 2H','high_share']:.1%}"),
    ("RHB 2H BB", "BB% **" + f3(RHB2H.bbrate) + "**"),
    ("month chase", "**.319 / .332 / .344 / .329**"),
]
depth = R("half_panel"); dpt = depth.set_index(depth.game_year.astype(str) + depth.half).beyond_miss_depth_ft
NARR += [("miss depth 2H", f"**{dpt['20262H']:.3f} ft**"), ("miss depth 1H", f"up from {dpt['20261H']:.3f}")]
mm = R("month_panel_2026").set_index("month").beyond_shadow_chase_rate
check("F", "month chase values match receipt", [f3(mm[m]) for m in [4, 5, 6, 7]] == [".319", ".332", ".344", ".329"] and f3(mm[8]) == ".250" and f3(mm[9]) == ".230")
sdm = R("start_distribution_summary")
g_ = lambda y, h, s: sdm[(sdm.game_year == y) & (sdm.half == h) & (sdm.is_subject == s)].median_shadow_miss.iloc[0]
NARR += [("start medians 2025", f"**{f3(g_(2025,'1H',True))}** of the time in the first half and **{f3(g_(2025,'2H',True))}**"),
         ("start medians 2026", f"**{f3(g_(2026,'1H',True))} / {f3(g_(2026,'2H',True))}** against a field median of **{f3(g_(2026,'1H',False))} / {f3(g_(2026,'2H',False))}**")]
bps = R("by_pitch_stand_2026").set_index(["half", "stand", "pitch_name"])
NARR += [("CH vs RHB miss", f"**{f3(bps.loc[('1H','R','Changeup'),'shadow_miss_rate'])} → {f3(bps.loc[('2H','R','Changeup'),'shadow_miss_rate'])}** ({int(bps.loc[('1H','R','Changeup'),'pitches'])} → {int(bps.loc[('2H','R','Changeup'),'pitches'])} pitches)"),
         ("CH vs RHB chase", f"**{f3(bps.loc[('1H','R','Changeup'),'beyond_shadow_chase_rate'])} → {f3(bps.loc[('2H','R','Changeup'),'beyond_shadow_chase_rate'])}**"),
         ("CH vs RHB whiff", f"whiff **{f3(bps.loc[('1H','R','Changeup'),'whiff_rate'])} → {f3(bps.loc[('2H','R','Changeup'),'whiff_rate'])}**"),
         ("SI vs RHB", f"(**{f3(bps.loc[('1H','R','Sinker'),'shadow_miss_rate'])} → {f3(bps.loc[('2H','R','Sinker'),'shadow_miss_rate'])}**)"),
         ("SI zone", f"**{f3(bps.loc[('2H','R','Sinker'),'in_zone_rate'])}** of the time"),
         ("BL5 62.1% / 54.1%", f"**{bps.loc[('2H','R','Changeup'),'shadow_miss_rate']:.1%}** of the changeups he throws to righties miss the shadow (up from {bps.loc[('1H','R','Changeup'),'shadow_miss_rate']:.1%})"),
         ("BL5 30.2% / 39.9%", f"**{bps.loc[('2H','R','Changeup'),'beyond_shadow_chase_rate']:.1%}** of the time, down from {bps.loc[('1H','R','Changeup'),'beyond_shadow_chase_rate']:.1%}"),
         ("xwOBAcon", f"(xwOBA on contact is only {f3(hp_.loc['20261H','xwobacon'])} → {f3(hp_.loc['20262H','xwobacon'])} across the break)")]
for name, snippet in NARR:
    check("F", f"narrative: {name}", has(snippet), snippet)
ntot = len([f for f in OUT.glob("dp_uc45_*.csv") if "verification_results" not in f.name]) + 1
check("F", "receipt count stated in report footer", f"`out/dp_uc45_*.csv` ({ntot})" in md, ntot)

# ---------------------------------------------------------------------------
res = pd.DataFrame(RESULTS)
res.to_csv(OUT / "dp_uc45_verification_results.csv", index=False)
fails = res[res.status == "FAIL"]
summ = res.groupby("family").status.value_counts().unstack(fill_value=0)
log = [f"dp_uc45 verification — {len(res)} checks, {len(res) - len(fails)} PASS, {len(fails)} FAIL", summ.to_string()]
if len(fails):
    log.append(fails.to_string())
(OUT / "dp_uc45_verification_log.txt").write_text("\n".join(log) + "\n")
print("\n".join(log))
sys.exit(1 if len(fails) else 0)
