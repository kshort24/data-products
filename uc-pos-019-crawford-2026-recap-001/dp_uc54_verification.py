"""dp_uc54_verification.py - INDEPENDENT harness for UC #54 / uc-pos-019 (definition-first).
Imports NO build kernel for computation: re-reads parquet, re-implements every KPI from the 03 §2 specs, then checks
headlines.json, the report, the dashboard and the receipts. Families: A lineage · B frame · C context · D story ·
E new objects (TR-1, CC-1, XO-2) · F every published string · G carry-in discipline. Writes out/dp_uc54_verification_log.csv."""
from __future__ import annotations
import glob, hashlib, json, math, os, re
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
MLB = Path(os.environ.get("MLB_DATA_ROOT", r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"))
DP = HERE.parent
H = json.loads((OUT / "dp_uc54_headlines.json").read_text(encoding="utf-8"))
MD = (HERE / "dp_uc54_crawford_2026_recap_report.md").read_text(encoding="utf-8")
HT = (HERE / "dp_uc54_crawford_2026_dashboard.html").read_text(encoding="utf-8")
LOG = []
ID, WRONG = 702222, 641487


def chk(fam, name, exp, got, tol=None):
    if tol is None:
        ok = exp == got
    else:
        ok = (exp is not None and got is not None and abs(float(exp) - float(got)) <= tol)
    LOG.append(dict(family=fam, check=name, expected=exp, got=got, status="PASS" if ok else "FAIL"))


def has(fam, name, s, where=("md", "html")):
    for w in where:
        LOG.append(dict(family=fam, check=f"{name} [{w}]", expected=s, got="present" if s in (MD if w == "md" else HT) else "MISSING",
                        status="PASS" if s in (MD if w == "md" else HT) else "FAIL"))


f3 = lambda x: (lambda s: s[1:] if s.startswith("0.") else ("-" + s[2:] if s.startswith("-0.") else s))(f"{x:.3f}")   # noqa: E731
pc = lambda x, d=1: f"{100 * x:.{d}f}%"   # noqa: E731
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"   # noqa: E731

# ---------------- A lineage -------------------------------------------------------------------------------------
for f, rel in [("dp_uc40_kernel.py", DP / "uc-pos-014-turner-2026-recency-001" / "dp_uc40_kernel.py"),
               ("dp_uc34_kernel.py", DP / "uc-pos-011-crawford-ytd-001" / "dp_uc34_kernel.py"),
               ("dp_uc53_kernel.py", DP / "uc-pps-037-alvarado-2026-recap-001" / "dp_uc53_kernel.py"),
               ("cumulative_metric.py", MLB / "cumulative_metric.py"), ("dp_uc22_harper_own_the_zone.py", MLB / "dp_uc22_harper_own_the_zone.py")]:
    chk("A", f"sha256 {f}", H["lineage"][f], hashlib.sha256(rel.read_bytes()).hexdigest()[:16])
kern = (HERE / "dp_uc54_kernel.py").read_text(encoding="utf-8")
chk("A", "TR-1 bars unchanged since BID", True, all(s in kern for s in ['"woba", +1, 0.030', '"ba", +1, 0.030', '"obp", +1, 0.030', '"slg", +1, 0.040',
                                                                          '"xwoba", +1, 0.025', '"krate", -1, 0.030', '"bbrate", +1, 0.015',
                                                                          '"chase_rate", -1, 0.030', '"hard_hit_rate", +1, 0.040', '"whiff_rate", -1, 0.030']))
bid = next(HERE.glob("BID_*.md")).read_text(encoding="utf-8")
chk("A", "TR-1 table present in BID", True, "| P6 | process | whiff rate | − | .030 |" in bid and "| R4 | results | SLG | + | .040 |" in bid)

# ---------------- B frame ---------------------------------------------------------------------------------------
COLS = ["game_pk", "at_bat_number", "pitch_number", "game_date", "game_year", "game_type", "batter", "pitcher", "player_name", "phillies_role",
        "events", "description", "zone", "type", "bb_type", "launch_speed", "launch_angle", "hit_distance_sc", "hc_x", "hc_y", "p_throws", "stand",
        "pitch_type", "on_2b", "on_3b", "estimated_woba_using_speedangle", "estimated_ba_using_speedangle", "woba_value", "woba_denom", "plate_x",
        "plate_z", "sz_top", "sz_bot", "balls", "strikes", "delta_run_exp", "fielder_8", "hit_location", "attack_angle", "bat_speed"]
fr = []
for y in range(2015, 2027):
    f = MLB / "data" / "phillies" / f"phils_{y}.parquet"
    names = pd.read_parquet(f, columns=None).columns if False else __import__("pyarrow.parquet", fromlist=["x"]).read_schema(f).names
    fr.append(pd.read_parquet(f, columns=[c for c in COLS if c in names]))
ALL = pd.concat(fr, ignore_index=True)
ALL["game_date"] = pd.to_datetime(ALL.game_date)
chk("B", "anchor (max game_date)", H["anchor"], str(ALL.game_date.max())[:10])
BAT = ALL[(ALL.phillies_role == "batting") & (ALL.game_type == "R")]
PIT = ALL[(ALL.phillies_role == "pitching") & (ALL.game_type == "R")]
S = BAT[BAT.batter == ID].copy()
chk("B", "subject pitches", H["pitches_seen"], len(S))
chk("B", "subject games with a PA-pitch", H["games_with_pa"], S.game_pk.nunique())
chk("B", "subject duplicate keys", 0, int(S.duplicated(["game_pk", "at_bat_number", "pitch_number"]).sum()))
chk("B", "spring pitches excluded", 125, int(((ALL.batter == ID) & (ALL.game_type == "S") & (ALL.phillies_role == "batting")).sum()))
POST = ALL[(ALL.batter == ID) & ALL.game_type.isin(["F", "D", "L", "W"]) & (ALL.phillies_role == "batting")]
chk("B", "postseason pitches", H["post"]["pitches"], len(POST)); chk("B", "postseason games", H["post"]["games"], POST.game_pk.nunique())
jp = BAT[BAT.batter == WRONG]   # harness correction HC-1: J.P. Crawford batted for PHI in 2017-18; the invariant is "never in the subject frame"
chk("B", "J.P. Crawford's PHI rows are 2017-18 under his own name", ([2017, 2018], ["Crawford, J.P."]), (sorted(jp.game_year.unique().tolist()), sorted(jp.player_name.unique().tolist())))
chk("B", "wrong-Crawford id never in the subject frame", 0, int((S.batter == WRONG).sum()))
chk("B", "a 'Crawford' substring filter would leak (ENT-2 exposure)", True, BAT.player_name.str.contains("Crawford").sum() > len(S))
wc = pd.read_parquet(MLB / "data" / "opponents" / "crawford.parquet", columns=["batter"])
chk("B", "crawford.parquet is J.P. Crawford (ENT-2)", [WRONG], sorted(wc.batter.unique().tolist()))
chk("B", "first / last game", (H["first_game"], H["last_game"]), (str(S.game_date.min())[:10], str(S.game_date.max())[:10]))

# ---------------- definitions (03 §2) ---------------------------------------------------------------------------
NONPA = {"pickoff_1b", "pickoff_2b", "pickoff_3b", "caught_stealing_2b", "caught_stealing_3b", "caught_stealing_home", "stolen_base_2b", "stolen_base_3b",
         "stolen_base_home", "pickoff_caught_stealing_2b", "pickoff_caught_stealing_3b", "pickoff_caught_stealing_home", "wild_pitch", "passed_ball",
         "other_advance", "runner_double_play", "defensive_indiff", "balk", "game_advisory", "ejection"}
NOTAB = {"walk", "intent_walk", "hit_by_pitch", "sac_fly", "sac_bunt", "sac_fly_double_play", "sac_bunt_double_play", "catcher_interf"}
HITS = {"single", "double", "triple", "home_run"}
SW = {"foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"}
WH = {"foul_tip", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"}
W = pd.read_csv(MLB / "wOBA and FIP Constants.csv").set_index("Season")


def line(d):
    pa = d[d.events.notna() & ~d.events.isin(NONPA)]
    e = pa.events
    ab = int((~e.isin(NOTAB)).sum()); h = int(e.isin(HITS).sum()); bb = int(e.isin({"walk", "intent_walk"}).sum()); ubb = int((e == "walk").sum())
    hbp = int((e == "hit_by_pitch").sum()); sf = int((e == "sac_fly").sum()); so = int(e.isin({"strikeout", "strikeout_double_play"}).sum())
    s1, s2, s3, hr = (int((e == x).sum()) for x in ("single", "double", "triple", "home_run"))
    tb = s1 + 2 * s2 + 3 * s3 + 4 * hr
    num = sum(W.loc[int(y)].wBB * (g.events == "walk").sum() + W.loc[int(y)].wHBP * (g.events == "hit_by_pitch").sum() + W.loc[int(y)]["w1B"] * (g.events == "single").sum()
              + W.loc[int(y)]["w2B"] * (g.events == "double").sum() + W.loc[int(y)]["w3B"] * (g.events == "triple").sum() + W.loc[int(y)].wHR * (g.events == "home_run").sum()
              for y, g in pa.groupby("game_year"))
    den = ab + ubb + sf + hbp
    return dict(pa=len(pa), ab=ab, h=h, bb=bb, so=so, hr=hr, ba=h / ab if ab else np.nan, obp=(h + bb + hbp) / (ab + bb + hbp + sf) if ab else np.nan,
                slg=tb / ab if ab else np.nan, woba=num / den if den else np.nan, babip=(h - hr) / (ab - so - hr + sf) if (ab - so - hr + sf) else np.nan, iso=(tb - h) / ab if ab else np.nan)


def xw(d):
    pa = d[d.woba_denom.fillna(0) > 0]
    est = pd.to_numeric(pa.estimated_woba_using_speedangle, errors="coerce")
    n = np.where((pa.type == "X") & est.notna(), est, pa.woba_value.fillna(0))
    return n.sum() / pa.woba_denom.sum()


def rates(d):
    dd = d[d.pitch_type.notna()]
    sw = d.description.isin(SW); ooz = dd.zone > 9
    bip = d[d.type == "X"]
    return dict(swing=sw.mean(), chase=dd[ooz].description.isin(SW).mean(), chases=int(dd[ooz].description.isin(SW).sum()), ooz=int(ooz.sum()),
                whiff=d[sw].description.isin(WH).mean(), ooz_whiff=dd[ooz & dd.description.isin(SW)].description.isin(WH).mean(),
                hh=(bip.launch_speed.fillna(0) >= 95).mean(), gb=(bip.bb_type == "ground_ball").mean(),
                la=bip[bip.launch_speed.notna() & bip.launch_angle.notna()].launch_angle.mean(), bips=len(bip))


# ---------------- D story -----------------------------------------------------------------------------------------
L = line(S); RT = rates(S)
for k, hk in (("pa", "plate_apps"), ("ab", "at_bats"), ("h", "hits"), ("hr", "hrs"), ("so", "strikeouts")):
    chk("D", f"season {k}", int(H[hk]), L[k])
for k in ("ba", "obp", "slg", "woba", "babip", "iso"):
    chk("D", f"season {k}", H[k], L[k], 1e-9)
chk("D", "season xwOBA (XW-1)", H["xwoba"], xw(S), 1e-9)
for k, hk in (("swing", "swing_rate"), ("chase", "chase_rate"), ("whiff", "whiff_rate"), ("hh", "hard_hit_rate"), ("gb", "gb_rate"), ("la", "mean_la")):
    chk("D", f"season {hk}", H[hk], RT[k], 1e-9)
chk("D", "out-of-zone contact", H["ooz_contact_rate"], 1 - RT["ooz_whiff"], 1e-9)
RS = line(S[S.on_2b.notna() | S.on_3b.notna()])
chk("D", "RISP BA", H["risp_ba"], RS["ba"], 1e-9); chk("D", "RISP PA", int(H["risp_pa"]), RS["pa"])
oz = S[S.zone > 9]; chk("D", "out-of-zone BA", H["ooz_ba"], line(oz)["ba"], 1e-9)
aa = S[S.description.isin(SW) & S.attack_angle.notna()].attack_angle.mean()
chk("D", "attack angle", H["attack_angle_mu"], aa, 1e-9)
# house pool
pool = []
_pac = BAT[BAT.events.notna() & ~BAT.events.isin(NONPA)].groupby(["batter", "game_year"]).size()
_keep = set(_pac[_pac >= 45].index)
for (b, y), g in BAT.groupby(["batter", "game_year"]):
    if (b, y) not in _keep:
        continue
    l = line(g)
    if l["pa"] >= 50:
        r = rates(g)
        a2 = g[g.description.isin(SW) & g.attack_angle.notna()].attack_angle.mean() if "attack_angle" in g and g.attack_angle.notna().sum() >= 50 else np.nan
        tb = g[g.type == "X"]; trk = tb[tb.launch_speed.notna() & tb.launch_angle.notna()]
        pool.append(dict(batter=b, year=y, pa=l["pa"], chase=r["chase"], whiff=r["whiff"], gb=r["gb"], la=trk.launch_angle.mean() if len(trk) >= 50 else np.nan, aa=a2))
pool = pd.DataFrame(pool)
chk("C", "house pool n (>=50 PA)", H["pool_n"], len(pool))
me = pool[(pool.batter == ID) & (pool.year == 2026)].iloc[0]
chk("C", "chase better-than pct", H["profile"]["chase_rate"]["better"], int(math.floor(100 * (pool.chase > me.chase).mean())))
chk("C", "whiff better-than pct", H["profile"]["whiff_rate"]["better"], int(math.floor(100 * (pool.whiff > me.whiff).mean())))
chk("C", "GB better-than pct", H["profile"]["gb_rate"]["better"], int(math.floor(100 * (pool.gb > me.gb).mean())))
la = pool[pool.la.notna()]
chk("C", "launch-angle pool n", H["profile"]["mean_la"]["n"], len(la))
chk("C", "launch-angle rank from the bottom", H["la_rank_low"], int((la.la < me.la).sum() + 1))
chk("C", "lowest launch angle among 100+ PA", 1, int((la[la.pa >= 100].la < me.la).sum() + 1))
aap = pool[pool.aa.notna()]
chk("C", "attack-angle rank from the bottom", 1, int((aap.aa < me.aa).sum() + 1)); chk("C", "attack-angle pool n", H["profile"]["attack_angle_mu"]["n"], len(aap))
# CX-1 (CF pool) re-derived
cfg = PIT.groupby(["game_year", "fielder_8"]).game_pk.nunique().rename("g").reset_index()
cfg = cfg[(cfg.g > 80) & cfg.fielder_8.isin(BAT.batter.unique())]
chk("C", "CX-1 seasons", H["cx"]["n"], len(cfg))
cfp = PIT[(PIT.fielder_8 == ID)].groupby("game_pk").size()
crow = S[S.game_pk.isin(cfp[cfp > 10].index)]
chk("C", "Crawford CF-games PA (CX-1 line)", 464, line(crow)["pa"])
mv = []
for r in cfg.itertuples():
    gp = PIT[(PIT.fielder_8 == r.fielder_8) & (PIT.game_year == r.game_year)].groupby("game_pk").size()
    g = BAT[(BAT.batter == r.fielder_8) & BAT.game_pk.isin(gp[gp > 10].index)]
    pa = g[g.events.notna() & ~g.events.isin(NONPA)].sort_values(["game_date", "game_pk", "at_bat_number"]).head(int(H["plate_apps"]))
    mv.append(dict(f=r.fielder_8, y=r.game_year, woba=line(g[g.set_index(["game_pk", "at_bat_number"]).index.isin(pa.set_index(["game_pk", "at_bat_number"]).index)])["woba"]))
mv = pd.DataFrame(mv); mv["rk"] = mv.woba.rank(ascending=False, method="min")
chk("C", "matched-volume wOBA rank", H["cx"]["rank"]["woba"], int(mv[(mv.f == ID) & (mv.y == 2026)].rk.iloc[0]))
# platoon, monthly receipt spot check
chk("D", "PA vs RHP", H["split"]["R"]["pa"], line(S[S.p_throws == "R"])["pa"])
chk("D", "chase vs LHP", H["split"]["L"]["chase"], rates(S[S.p_throws == "L"])["chase"], 1e-9)

# ---------------- E new objects -------------------------------------------------------------------------------------
pre, post = S[S.game_date < "2026-06-01"], S[S.game_date >= "2026-06-01"]
lp, lq, rp, rq = line(pre), line(post), rates(pre), rates(post)


def zp(x1, n1, x2, n2):
    p = (x1 + x2) / (n1 + n2); se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)); z = (x1 / n1 - x2 / n2) / se
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def verdict(b, a, d, bar, p=None):
    dl = (a - b) * d
    if abs(a - b) < bar / 4: return "ABSENT"
    if dl >= bar and (p is None or p < 0.05): return "PRESENT"
    if dl > 0: return "WEAK"
    if -dl >= bar: return "CONTRA"
    return "ABSENT"


def cnt(d, k):
    dd = d[d.pitch_type.notna()]; bip = d[d.type == "X"]; sw = d[d.description.isin(SW)]; l = line(d)
    return {"krate": (l["so"], l["pa"]), "bbrate": (l["bb"], l["pa"]), "chase_rate": (int(dd[dd.zone > 9].description.isin(SW).sum()), int((dd.zone > 9).sum())),
            "hard_hit_rate": (int((bip.launch_speed.fillna(0) >= 95).sum()), len(bip)), "whiff_rate": (int(sw.description.isin(WH).sum()), len(sw))}[k]


val = lambda d, l, r, k: {"woba": l["woba"], "ba": l["ba"], "obp": l["obp"], "slg": l["slg"], "xwoba": xw(d), "krate": l["so"] / l["pa"], "bbrate": l["bb"] / l["pa"],   # noqa: E731
                          "chase_rate": r["chase"], "hard_hit_rate": r["hh"], "whiff_rate": r["whiff"]}[k]
SIGS = [("R1", "woba", 1, .03, 0), ("R2", "ba", 1, .03, 0), ("R3", "obp", 1, .03, 0), ("R4", "slg", 1, .04, 0), ("P1", "xwoba", 1, .025, 0), ("P2", "krate", -1, .03, 1),
        ("P3", "bbrate", 1, .015, 1), ("P4", "chase_rate", -1, .03, 1), ("P5", "hard_hit_rate", 1, .04, 1), ("P6", "whiff_rate", -1, .03, 1)]
res, pro = [], []
for sid, k, d, bar, t in SIGS:
    b, a = val(pre, lp, rp, k), val(post, lq, rq, k)
    p = zp(*cnt(pre, k), *cnt(post, k)) if t else None
    v = verdict(b, a, d, bar, p)
    chk("E", f"TR-1 {sid} pre", H["tr1"]["rows"][sid]["pre"], b, 1e-9); chk("E", f"TR-1 {sid} post", H["tr1"]["rows"][sid]["post"], a, 1e-9)
    chk("E", f"TR-1 {sid} verdict", H["tr1"]["rows"][sid]["verdict"], v)
    (res if sid[0] == "R" else pro).append(v)


def roll(v):
    n, p, c = len(v), v.count("PRESENT"), v.count("CONTRA")
    return "STRONG" if p == n else "MIXED" if (c and p) else "SUPPORTED" if (2 * p >= n and not c) else "UNSUPPORTED"


Rr, Pp = roll(res), roll(pro)
call = "EARNED TURN" if Rr in ("STRONG", "SUPPORTED") and Pp in ("STRONG", "SUPPORTED") else "RESULTS TURN" if Rr in ("STRONG", "SUPPORTED") else "PROCESS TURN" if Pp in ("STRONG", "SUPPORTED") else "NO TURN"
chk("E", "TR-1 call", H["tr1"]["call"], call)
for d in ("2026-06-01", "2026-06-15", "2026-05-15"):
    chk("E", f"RC-5 d_wOBA at {d}", H["scan"][d]["d_woba"], line(S[S.game_date >= d])["woba"] - line(S[S.game_date < d])["woba"], 1e-9)
# rolling 100-PA wOBA
pa = S[S.events.notna() & ~S.events.isin(NONPA)].sort_values(["game_date", "game_pk", "at_bat_number"])
w26 = W.loc[2026]
num = pa.events.map({"walk": w26.wBB, "hit_by_pitch": w26.wHBP, "single": w26["w1B"], "double": w26["w2B"], "triple": w26["w3B"], "home_run": w26.wHR}).fillna(0)
den = (~pa.events.isin({"intent_walk", "sac_bunt"})).astype(float)
rw = (num.rolling(100).sum() / den.rolling(100).sum()).dropna()
chk("E", "rolling-100 min", H["roll_min"]["woba"], rw.min(), 1e-9); chk("E", "rolling-100 max", H["roll_max"]["woba"], rw.max(), 1e-9)
chk("E", "rolling-100 min date", H["roll_min"]["date"], str(pa.loc[rw.idxmin(), "game_date"])[:10])
# CC-1
REF = BAT[BAT.game_year.isin([2023, 2024, 2025, 2026]) & (BAT.zone > 9) & BAT.pitch_type.notna() & BAT.delta_run_exp.notna()]
ref = REF[~REF.description.isin(SW)].groupby(["balls", "strikes"]).delta_run_exp.mean()
so = S[(S.zone > 9) & S.pitch_type.notna() & S.delta_run_exp.notna()]
ch = so[so.description.isin(SW)]
cost = (ref.reindex(pd.MultiIndex.from_arrays([ch.balls, ch.strikes])).to_numpy() - ch.delta_run_exp.to_numpy())
chk("E", "CC-1 total runs", H["cc1"]["runs"], float(np.nansum(cost)), 1e-6); chk("E", "CC-1 chases", H["cc1"]["chases"], len(ch))
rr = ch.p_throws.eq("R").to_numpy()
chk("E", "CC-1 runs vs RHP", sum(v["runs"] for k, v in H["cc1"]["by"].items() if k.startswith("R_")), float(np.nansum(cost[rr])), 1e-6)
chk("E", "CC-1 2-strike runs", H["cc1"]["by_strikes"]["2"]["runs"], float(np.nansum(cost[ch.strikes.to_numpy() == 2])), 1e-6)
r3 = S.groupby(["game_pk", "at_bat_number"]).balls.max().ge(3).mean()
chk("E", "three-ball reach rate", H["reach3"]["value"], r3, 1e-9)
# XO-2 (v3)
def air(d):
    b = d[(d.type == "X") & d.bb_type.isin(["fly_ball", "line_drive", "popup"]) & d.hc_x.notna() & d.launch_speed.notna() & d.launch_angle.notna() & d.hit_distance_sc.notna()].copy()
    lx, ly = 2.495671 * (b.hc_x.astype(float) - 125.42), 2.495671 * (198.27 - b.hc_y.astype(float))
    b["ang"] = np.degrees(np.arctan2(lx, ly))
    b = b[(b.ang.abs() <= 15) & (b.hit_distance_sc >= 150)]
    b["out"] = b.events.isin(["double_play", "field_out", "sac_fly", "sac_fly_double_play", "triple_play"])
    return b
opp = air(PIT[(PIT.fielder_8 == ID) & (PIT.game_year == 2026)])
pl = air(pd.concat([PIT[PIT.fielder_8 != ID], BAT]).drop_duplicates(["game_pk", "at_bat_number", "pitch_number"]))
E, A_, Dd, G, O = (pl[c].to_numpy(float) for c in ("launch_speed", "launch_angle", "hit_distance_sc", "ang", "out"))
xo, outs = [], []
for r in opp.itertuples():
    m = (np.abs(E - r.launch_speed) <= 3) & (np.abs(A_ - r.launch_angle) <= 2) & (np.abs(Dd - r.hit_distance_sc) <= 10) & (np.abs(G - r.ang) <= 10)
    if m.sum() >= 10:
        xo.append(O[m].mean()); outs.append(float(r.out))
chk("E", "XO-2 opportunities", H["xo2"]["opps"], len(opp)); chk("E", "XO-2 scored", H["xo2"]["scored"], len(xo))
chk("E", "XO-2 outs", H["xo2"]["outs"], int(sum(outs))); chk("E", "XO-2 OAE", H["xo2"]["oae"], sum(outs) - sum(xo), 1e-6)
chk("E", "XO-2 pool size", H["xo2"]["pool_n"], len(pl))
# RHP breaking balls, AAA vs MLB, heart share and pull share
A = pd.read_parquet(MLB / "data" / "opponents" / "lhvb25.parquet"); A = A[(A.batter == ID) & (A.game_type == "R")].drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
BRK = {"SL", "ST", "CU", "KC", "SV", "CS"}
for lvl, d in (("AAA 2025", A), ("MLB 2026", S)):
    rb = d[(d.p_throws == "R") & d.pitch_type.isin(BRK)]
    bip = rb[rb.type == "X"]
    chk("E", f"{lvl} RHP-BB hard-hit", H["rhp_bb"][lvl]["hh"], (bip.launch_speed.fillna(0) >= 95).mean(), 1e-9)
    hits = rb[rb.events.isin(HITS) & rb.plate_x.notna() & rb.sz_top.notna()]
    ax = hits.plate_x.abs(); iz = (ax <= .83) & (hits.plate_z >= hits.sz_bot) & (hits.plate_z <= hits.sz_top)
    edge = ((.83 - ax) <= .25) | ((hits.plate_z - hits.sz_bot) <= .25) | ((hits.sz_top - hits.plate_z) <= .25)
    chk("E", f"{lvl} RHP-BB hits in heart", H["rhp_bb_hits_heart"][lvl]["heart"], int((iz & ~edge).sum()))
    chk("E", f"{lvl} RHP-BB hits", H["rhp_bb_hits_heart"][lvl]["hits"], len(hits))
    lx, ly = 2.495671 * (bip.hc_x.astype(float) - 125.42), 2.495671 * (198.27 - bip.hc_y.astype(float))
    pull = (ly <= 4.7 * lx); straight = (ly > -4.7 * lx) & (ly > 4.7 * lx); oppo = (ly <= -4.7 * lx)
    cls = pull | straight | oppo
    chk("E", f"{lvl} RHP-BB pull share (LHB)", H["direction"][f"{lvl}|rhpbb|Pull"]["share"], pull[cls].mean(), 1e-9)

# ---------------- F published strings -------------------------------------------------------------------------------
has("F", "slash line", f"{f3(L['ba'])}/{f3(L['obp'])}/{f3(L['slg'])}")
has("F", "wOBA + xwOBA", f"{f3(L['woba'])} wOBA (xwOBA {f3(xw(S))})")
has("F", "RISP", f"{f3(RS['ba'])} ({RS['h']} for {RS['ab']})")
has("F", "CF ranks", f"ranks {ordn(H['cx']['rank']['ba'])} in BA and {ordn(H['cx']['rank']['woba'])} in wOBA at {L['pa']} PA")
has("F", "TR-1 call", "NO TURN")
has("F", "BA turn", f"{f3(lp['ba'])} → {f3(lq['ba'])}")
has("F", "walk-rate fall", f"{pc(lp['bb'] / lp['pa'])} → {pc(lq['bb'] / lq['pa'])}")
has("F", "chase rate", f"chase {pc(RT['chase'])}")
has("F", "GB rate", f"{pc(RT['gb'])} grounders")
has("F", "launch angle rank", f"{RT['la']:.1f}° average launch angle ({ordn(int((la.la < me.la).sum() + 1))}-lowest of {len(la)}")
has("F", "CC-1 total", f"{float(np.nansum(cost)):.1f} runs over {len(ch)} chases")
has("F", "XO-2 line", f"{int(sum(outs))} outs against {sum(xo):.1f} expected: <b>{sum(outs) - sum(xo):+.1f}</b>", where=("html",))
has("F", "XO-2 line (md)", f"{int(sum(outs))} outs against {sum(xo):.1f} expected: **{sum(outs) - sum(xo):+.1f}**", where=("md",))
has("F", "client XO-1", f"{H['hp_xo1_client']['outs']} outs against {H['hp_xo1_client']['xouts']:.1f} expected")
has("F", "heart hits AAA", f"{H['rhp_bb_hits_heart']['AAA 2025']['heart']} of his {H['rhp_bb_hits_heart']['AAA 2025']['hits']} hits off righty spin")
has("F", "three-ball reach", f"{pc(r3)} of plate appearances")
has("F", "rolling trough", f3(rw.min()))
specs = json.loads((OUT / "dp_uc54_figure_specs.json").read_text(encoding="utf-8"))
chk("F", "figures shipped", 10, len(specs))
chk("F", "figure PNGs on disk", 10, len(list(OUT.glob("dp_uc54_f*_*.png"))))
bc = pd.read_csv(OUT / "dp_uc54_brand_checks.csv")
chk("F", "brand + claim checks all true", True, bool(bc[["claim_asserted", "font_arial", "has_title", "has_subtitle", "palette_ok"]].all().all()))
chk("F", "dashboard loads plotly by CDN src, not inline (HC-2)", True, 'src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@3.0.1' in HT and len(HT) < 1_500_000)
chk("F", "dashboard payload has no NaN", True, "NaN" not in HT)
pdf = (HERE / "dp_uc54_crawford_2026_recap_report.pdf").read_bytes()
chk("F", "PDF page cap (<= 10)", True, len(re.findall(rb"/Type\s*/Page[^s]", pdf)) <= 10)
dqs = pd.read_csv(OUT / "dp_uc54_dq_scorecard.csv")
chk("F", "DQ scorecard has no FAIL", 0, int((dqs.status == "FAIL").sum()))

# ---------------- G carry-in discipline ----------------------------------------------------------------------------
for sent_key, ci in (("−8 OAA", "CI-2"), ("149 G", "CI-2"), ("97th-percentile sprint speed", "CI-3"), ("debut 2026-03-26", "CI-1")):
    i = MD.find(sent_key); chk("G", f"'{sent_key}' labelled {ci} in report", True, i >= 0 and ci in MD[i:i + 400])
flat = json.dumps(H)
chk("G", "no OAA/DRS/WAR value enters headlines", True, not re.search(r'"(oaa|drs|war|sprint)[^"]*":', flat, re.I))
chk("G", "no carry-in games count (149) in headlines", True, '"games": 149' not in flat and '"g": 149' not in flat)
chk("G", "kernel/build never read carry-in values", True, all(x not in (HERE / f).read_text(encoding="utf-8") for f in ("dp_uc54_kernel.py", "dp_uc54_crawford_recap.py") for x in ("= -8", "= 149", "OAA =")))

log = pd.DataFrame(LOG)
log.to_csv(OUT / "dp_uc54_verification_log.csv", index=False)
fails = log[log.status != "PASS"]
print(f"verification: {int((log.status == 'PASS').sum())}/{len(log)} PASS"); print(fails.to_string() if len(fails) else "")
