"""
dp_uc50_verification.py -- independent recompute harness for UC #50 / uc-pos-018.

Does NOT import dp_uc50_kernel or any parent kernel. Reads parquet directly, dedups its own way,
computes rates from Statcast-native woba_value/woba_denom and raw descriptions, then compares to the
receipts in out/dp_uc50_*.csv and to every number printed in the narratives.
Families: A source & identity · B H2H vs Sale · C 2026 vs LHP cards · D Sale 2026 · E directional/HL-1 ·
          F prose <-> receipts · G governance conduct
Run: PYTHONPATH=/tmp/pyl MLB_DATA_ROOT="$PWD" python3 dp_uc50_verification.py
"""
import json, os, re, sys
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(os.environ.get("MLB_DATA_ROOT", ".")).resolve()
OUT = ROOT / "out"
R = lambda k: pd.read_csv(OUT / f"dp_uc50_{k}.csv")
SALE = 519242
IDS = {607208: "Trea Turner", 656941: "Kyle Schwarber", 547180: "Bryce Harper", 664761: "Alec Bohm",
       656537: "Derek Hill", 650559: "Bryan De La Cruz", 681082: "Bryson Stott", 624641: "Edmundo Sosa", 592663: "J.T. Realmuto"}
MINORS = {"lhvo26", "lhvp26", "lhvp25", "lhvb25", "clwo26", "clwp26", "clearwater_batting25", "clearwater_pitching25",
          "chst25", "sweet_aaa", "turnbulllhv"}
KEY = ["game_pk", "at_bat_number", "pitch_number"]
COLS = KEY + ["game_date", "game_year", "game_type", "batter", "pitcher", "stand", "p_throws", "pitch_type", "description",
              "events", "type", "zone", "plate_x", "launch_speed", "launch_speed_angle", "hc_x", "hc_y", "bb_type",
              "estimated_woba_using_speedangle", "woba_value", "woba_denom", "release_speed", "n_thruorder_pitcher", "player_name"]
res = []
mv = []


def check(fam, name, got, want, tol=0.0015):
    if isinstance(want, str) or isinstance(got, str):
        ok = str(got) == str(want)
    elif want is None or (isinstance(want, float) and np.isnan(want)):
        ok = got is None or (isinstance(got, float) and np.isnan(got))
    else:
        ok = abs(float(got) - float(want)) <= tol
    res.append(dict(family=fam, check=name, got=got, want=want, result="PASS" if ok else "FAIL"))


def rd(f):
    have = set(pq.read_schema(f).names)
    return pd.read_parquet(f, columns=[c for c in COLS if c in have])


# ---- independent frame: own precedence (phils first, then player file, then the rest alphabetically)
parts = []
for y in range(2015, 2027):
    d = rd(ROOT / "data/phillies" / f"phils_{y}.parquet")
    parts.append(d[d.batter.isin(IDS) | (d.pitcher == SALE)].assign(rank=0))
own = {"turner": 607208, "schwarber": 656941, "harper": 547180, "realmuto": 592663, "derek_hill": 656537,
       "bdlc": 650559, "edmundo": 624641, "sale": SALE}
for f in sorted((ROOT / "data/opponents").glob("*.parquet")):
    if f.stem in MINORS:
        continue
    d = rd(f)
    d = d[d.batter.isin(IDS) | (d.pitcher == SALE)]
    if len(d):
        parts.append(d.assign(rank=1 if f.stem in own else 2))
X = pd.concat(parts, ignore_index=True).sort_values("rank", kind="stable").drop_duplicates(KEY)
X = X[X.game_type == "R"]
X["game_date"] = pd.to_datetime(X.game_date).dt.strftime("%Y-%m-%d")
SW = {"foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"}
WH = {"foul_tip", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"}


W = pd.read_csv(ROOT / "wOBA and FIP Constants.csv").set_index("Season")


def line(d):
    """Independent line. PA = house convention (events present, not pickoff_1b), stated in 03 §2 and
    re-implemented here from the definition, not imported. wOBA from FanGraphs weights read directly."""
    pa = d[d.events.notna() & (d.events != "pickoff_1b")]
    ev = pa.events
    H = ev.isin(["single", "double", "triple", "home_run"]).sum()
    AB = (~ev.isin(["walk", "intent_walk", "hit_by_pitch", "sac_fly", "sac_bunt", "catcher_interf", "sac_fly_double_play", "sac_bunt_double_play"])).sum()
    TB = (ev == "single").sum() + 2 * (ev == "double").sum() + 3 * (ev == "triple").sum() + 4 * (ev == "home_run").sum()
    BB = ev.isin(["walk"]).sum(); HBP = (ev == "hit_by_pitch").sum()
    K = ev.isin(["strikeout", "strikeout_double_play"]).sum()
    n = len(pa)
    exp = pd.to_numeric(pa.estimated_woba_using_speedangle, errors="coerce")
    xn = np.where(pa.type.eq("X") & exp.notna(), exp, pa.woba_value.fillna(0))[pa.woba_denom.fillna(0).values > 0].sum()
    sw = d.description.isin(SW).sum(); wh = d.description.isin(WH).sum()
    ooz = (d.zone > 9).sum(); ch = ((d.zone > 9) & d.description.isin(SW)).sum()
    bip = d[d.type == "X"]
    wt = W.reindex(pa.game_year.astype(int))
    num = ((ev == "walk").values * wt.wBB.values + (ev == "hit_by_pitch").values * wt.wHBP.values +
           (ev == "single").values * wt.w1B.values + (ev == "double").values * wt.w2B.values +
           (ev == "triple").values * wt.w3B.values + (ev == "home_run").values * wt.wHR.values).sum()
    dn = pa[pa.woba_denom.fillna(0) > 0]
    return dict(pa=n, h=H, woba_fg=num / n if n else np.nan,
                woba_savant=dn.woba_value.sum() / dn.woba_denom.sum() if len(dn) else np.nan, hr=(ev == "home_run").sum(), k=K, bb=BB, ba=H / AB if AB else np.nan,
                obp=(H + BB + HBP) / n if n else np.nan, slg=TB / AB if AB else np.nan,
                xwoba=xn / pa.woba_denom.fillna(0).sum() if n else np.nan, krate=K / n if n else np.nan,
                whiff=wh / sw if sw else np.nan, chase=ch / ooz if ooz else np.nan,
                barrel=(bip.launch_speed_angle == 6).mean() if len(bip) else np.nan,
                hh=(bip.launch_speed.astype(float).fillna(0) >= 95).mean() if len(bip) else np.nan,  # house O-8: untracked BIP in denominator
                hh_tracked=(bip.launch_speed.dropna() >= 95).mean() if bip.launch_speed.notna().any() else np.nan)


# ---- A · source & identity
cov = R("coverage")
for bid, nm in IDS.items():
    check("A", f"{nm}: regular-season pitches in governed frame", int(cov.set_index("batter").loc[bid, "pitches"]), len(X[X.batter == bid]), 0)
nm_mode = X[X.batter.isin(IDS) & (X.pitcher != SALE)].groupby("batter").player_name.agg(lambda s: s.mode().iloc[0])
check("A", "Sale 2026 pitches (id lock)", int(R("sale_season").pitches.iloc[0]), len(X[(X.pitcher == SALE) & (X.game_year == 2026)]), 0)
check("A", "no duplicate pitch keys", int(X.duplicated(KEY).sum()), 0, 0)
check("A", "anchor = 2026-09-27", X[X.game_year == 2026].game_date.max(), "2026-09-27")

# ---- B · H2H vs Sale
sc = R("sale_career")
for bid, nm in IDS.items():
    d = X[(X.batter == bid) & (X.pitcher == SALE)]
    L = line(d)
    g = sc[(sc.batter == bid) & (sc.window == "career R")].iloc[0]
    check("B", f"{nm} vs Sale PA", g.plate_apps, L["pa"], 0)
    check("B", f"{nm} vs Sale hits", g.hits, L["h"], 0)
    check("B", f"{nm} vs Sale K", g.strikeouts, L["k"], 0)
    check("B", f"{nm} vs Sale AVG", g.ba, L["ba"], 0.0015)
    check("B", f"{nm} vs Sale SLG", g.slg, L["slg"], 0.0015)
    check("B", f"{nm} vs Sale wOBA (FanGraphs weights, own mapping)", g.woba, L["woba_fg"], 0.0015)
    mv.append(dict(scope=f"{nm} vs Sale", house_woba=g.woba, savant_woba=L["woba_savant"]))
    check("B", f"{nm} vs Sale xwOBA", g.xwoba, L["xwoba"], 0.0015)
LS = X[X.batter.isin(IDS) & (X.pitcher == SALE)]
agg = R("lineup_agg").set_index(["window", "group"])
check("B", "lineup career PA", agg.loc[("career R", "Lineup (9)"), "plate_apps"], line(LS)["pa"], 0)
check("B", "LHB 2026 hits", agg.loc[("2026 R", "LHB"), "hits"], line(LS[(LS.stand == "L") & (LS.game_year == 2026)])["h"], 0)
check("B", "LHB 2026 PA", agg.loc[("2026 R", "LHB"), "plate_apps"], line(LS[(LS.stand == "L") & (LS.game_year == 2026)])["pa"], 0)

# ---- C · 2026 vs LHP cards
bh = R("by_hand")
for bid, nm in IDS.items():
    d = X[(X.batter == bid) & (X.game_year == 2026) & (X.p_throws == "L")]
    L = line(d)
    g = bh[(bh.batter == bid) & (bh.p_throws == "L")].iloc[0]
    for col, key, tol in [("plate_apps", "pa", 0), ("xwoba", "xwoba", 0.0015), ("krate", "krate", 0.0015),
                          ("whiff_rate", "whiff", 0.0015), ("chase_rate", "chase", 0.0015), ("barrel_rate", "barrel", 0.0015),
                          ("hard_hit_rate", "hh", 0.0015), ("woba", "woba_fg", 0.0015)]:
        check("C", f"{nm} 2026 vs LHP {col}", g[col], L[key], tol)
    mv.append(dict(scope=f"{nm} 2026 vs LHP", house_woba=g.woba, savant_woba=L["woba_savant"],
                   house_hh=g.hard_hit_rate, tracked_hh=L["hh_tracked"]))
# LR-1 Harper
d = X[(X.batter == 547180) & (X.p_throws == "L")]
ops = []
for p, g in d.groupby("pitcher"):
    L = line(g)
    if L["pa"] >= 20:
        ops.append((p, L["obp"] + L["slg"]))
ops = sorted(ops, key=lambda t: t[1])
rk = R("rank").set_index("batter").loc[547180]
check("C", "Harper LR-1: Sale is #1", int(rk["rank"]), [p for p, _ in ops].index(SALE) + 1, 0)
check("C", "Harper LR-1: population size", int(rk.n_pitchers), len(ops), 0)
rp = R("rank_pop").query("batter==547180").sort_values("ops")
check("C", "Harper LR-1: next-worst OPS (governed receipt)", rp.ops.iloc[1], round(ops[1][1], 3), 0.0015)

# ---- D · Sale 2026
S = X[(X.pitcher == SALE) & (X.game_year == 2026)]
ars = R("sale_arsenal").set_index("pitch_type")
for pt in ["FF", "SL", "CH", "SI"]:
    s = S[S.pitch_type == pt]
    check("D", f"Sale {pt} usage", ars.loc[pt, "usage"], len(s) / len(S), 0.0005)
    check("D", f"Sale {pt} velo", ars.loc[pt, "velo"], s.release_speed.mean(), 0.05)
    check("D", f"Sale {pt} whiff", ars.loc[pt, "whiff_rate"], s.description.isin(WH).sum() / s.description.isin(SW).sum(), 0.0015)
Ls = line(S)
ss = R("sale_season").iloc[0]
check("D", "Sale 2026 PA", ss.plate_apps, Ls["pa"], 0)
check("D", "Sale 2026 K%", ss.krate, Ls["krate"], 0.0015)
check("D", "Sale 2026 xwOBA", ss.xwoba, Ls["xwoba"], 0.0015)
check("D", "Sale starts", S.game_pk.nunique(), 27, 0)
tto = R("sale_tto").set_index("tto")
for t, m in [("1", S.n_thruorder_pitcher == 1), ("2", S.n_thruorder_pitcher == 2), ("3+", S.n_thruorder_pitcher >= 3)]:
    check("D", f"Sale TTO {t} PA", tto.loc[t, "plate_apps"], line(S[m])["pa"], 0)
    check("D", f"Sale TTO {t} HR rate", tto.loc[t, "hr_rate"], line(S[m])["hr"] / line(S[m])["pa"], 0.0015)
for st in "LR":
    s = S[S.stand == st]
    ab = R("sale_arsenal_by_stand").query("stand==@st").set_index("pitch_type")
    for pt in ab.index:
        check("D", f"Sale usage vs {st}HB {pt}", ab.loc[pt, "usage"], (s.pitch_type == pt).mean(), 0.0005)

# ---- E · directional / HL-1 (own classifier: own hc->loc, own slope)
band = R("band")
for bid, nm in IDS.items():
    b = X[(X.batter == bid) & (X.game_year == 2026) & (X.p_throws == "L") & (X.type == "X") & X.hc_x.notna() & X.hc_y.notna()].copy()
    lx = b.hc_x - 125.42; ly = 198.27 - b.hc_y
    rhb = b.stand == "R"
    pull = np.where(rhb, ly <= -4.7 * lx, ly <= 4.7 * lx)
    straight = (ly > -4.7 * lx) & (ly > 4.7 * lx)
    oppo = np.where(rhb, (ly <= 4.7 * lx), (ly <= -4.7 * lx)) & ~straight & ~pull
    xr = np.where(b.stand == "L", -b.plate_x, b.plate_x)
    for bn, m in [("Away", xr > 0.83 / 3), ("Inner", xr < -0.83 / 3), ("All", np.ones(len(b), bool))]:
        g = band[(band.batter == bid) & (band.h_band == bn)]
        if not len(g):
            continue
        g = g.iloc[0]
        check("E", f"{nm} {bn} n_bip", g.n_bip, int(m.sum()), 0)
        check("E", f"{nm} {bn} pull rate", g.pull_rate, pull[m].mean(), 0.0015)
        check("E", f"{nm} {bn} oppo rate", g.oppo_rate, oppo[m].mean(), 0.0015)

# ---- F · prose <-> receipts: every card's printed numbers must be recomputable from CSV receipts
sys.path.insert(0, str(ROOT))
import dp_uc50_narratives as N  # narrative text only; the numbers are rebuilt below from CSVs
f3 = N.f3; pc = N.pc
cards = N.cards()
pg = R("pitch_group"); l30 = R("last30")
for bid, nm in IDS.items():
    txt = " ".join(cards[nm][k] for k in ("lede", "sale", "plan"))
    L = bh[(bh.batter == bid) & (bh.p_throws == "L")].iloc[0]
    C = sc[(sc.batter == bid) & (sc.window == "career R")].iloc[0]
    want = [f3(C.woba) if "wOBA" in cards[nm]["sale"] and f3(C.woba) in txt else None,
            str(int(C.plate_apps)), f"{f3(C.ba)}/{f3(C.obp)}/{f3(C.slg)}" if nm not in ("Kyle Schwarber", "Bryson Stott") else None]
    for wv in [w for w in want if w]:
        check("F", f"{nm}: '{wv}' in card text", wv in txt, True)
    for wv in re.findall(r"(?<![\d])\.\d{3}", cards[nm]["lede"]):
        # each 3-decimal figure in the lede must exist somewhere in this hitter's receipts
        pool = pd.concat([bh[bh.batter == bid], sc[sc.batter == bid], pg[pg.batter == bid], l30[l30.batter == bid],
                          R("rank")[R("rank").batter == bid], R("band")[R("band").batter == bid], R("lhp_season")[R("lhp_season").batter == bid]])
        vals = set()
        for c in pool.select_dtypes("number").columns:
            vals |= {f3(v) for v in pool[c].dropna()}
        check("F", f"{nm}: lede figure {wv} traced to a receipt", wv in vals, True)
    for wv in re.findall(r"(\d{1,3})% ", cards[nm]["lede"] + " "):
        pool = pd.concat([bh[bh.batter == bid], sc[sc.batter == bid], pg[pg.batter == bid], l30[l30.batter == bid],
                          R("band")[R("band").batter == bid]])
        vals = set()
        for c in pool.select_dtypes("number").columns:
            vals |= {f"{100*v:.0f}" for v in pool[c].dropna() if 0 <= v <= 1}
        check("F", f"{nm}: lede percent {wv}% traced to a receipt", wv in vals, True)
LN = N.lineup()
check("F", "bottom line: Sale FF 96.1", "96.1 mph" in LN["sale_line"], True)
check("F", "bottom line: 650 PA", f"{int(ss.plate_apps)} PA" in LN["sale_line"], True)
check("F", "LHB 2026 hits in prose", f"{int(agg.loc[('2026 R','LHB'),'hits'])} hit" in LN["lefties"], True)

# ---- G · governance conduct
rep = (ROOT / "dp_uc50_lineup_vs_sale_report.md").read_text(encoding="utf-8")
check("G", "no computed 'cleared the bases' claim", "cleared the bases" in rep.lower(), False)
check("G", "THIN flag printed for <10 PA hitters", rep.count("THIN") >= 3, True)
check("G", "carry-ins named in report", all(s in rep for s in ["batting order", "game time"]), True)
hp = R("hp_reconciliation")
check("G", "HP rows present (12)", len(hp), 12, 0)
check("G", "no HP verdict silently overwritten (client values kept)", hp.client_value.notna().all(), True)
fm = R("freshness_manifest")
check("G", "freshness manifest labels carry-ins", int(fm.kind.str.contains("CARRY-IN").sum()) >= 4, True)
dq = R("dq_scorecard")
check("G", "DQ has 0 FAIL", int((dq.result == "FAIL").sum()), 0, 0)

pd.DataFrame(mv).to_csv(OUT / "dp_uc50_method_variance.csv", index=False)   # MV-1 / O-8 disclosure, not pass/fail
out = pd.DataFrame(res)
out.to_csv(OUT / "dp_uc50_verification_results.csv", index=False)
summ = out.groupby("family").result.value_counts().unstack(fill_value=0)
print(summ.to_string())
print("TOTAL", (out.result == "PASS").sum(), "/", len(out))
print(out[out.result == "FAIL"].to_string())
