"""dp_uc53_verification.py - independent harness for UC #53 / uc-pps-037.
DEFINITION-FIRST: imports no dp_uc* kernel and no house module for computation. Re-reads the parquet with its own
projection, applies its own filters and de-duplication, and re-implements each KPI from 03 §2. Families:
A lineage · B frame · C context · D/E story · F every published string · G carry-in discipline.
Writes out/dp_uc53_verification_log.csv. Exit code 1 on any FAIL."""
from __future__ import annotations
import hashlib, json, os, re, sys
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
MLB = Path(os.environ.get("MLB_DATA_ROOT", r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"))
H = json.loads((OUT / "dp_uc53_headlines.json").read_text())
SPECS = {s["figure"]: s for s in json.loads((OUT / "dp_uc53_figure_specs.json").read_text())}
REPORT = (HERE / "dp_uc53_alvarado_2026_recap_report.md").read_text(encoding="utf-8")
DASH = (HERE / "dp_uc53_alvarado_2026_dashboard.html").read_text(encoding="utf-8")
import html as _h
DASH_T = _h.unescape(re.sub(r"<[^>]+>", " ", DASH.split('<script id="payload"')[0]))
LOG = []
def check(fam, name, ok, obs="", exp=""):
    LOG.append(dict(family=fam, check=name, result="PASS" if ok else "FAIL", observed=str(obs)[:200], expected=str(exp)[:200]))
near = lambda a, b, t=1e-6: a is not None and b is not None and abs(float(a) - float(b)) <= t   # noqa: E731
f3 = lambda x: f"{x:.3f}".lstrip("0") if 0 <= x < 1 else f"{x:.3f}"                        # noqa: E731
pc = lambda x, d=1: f"{100 * x:.{d}f}%"                                                        # noqa: E731
PID, SEASON, TEN = 621237, 2026, list(range(2021, 2027))

# ---- spec constants (03 §2), typed here independently of the kernel ----
SWINGS = {"foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"}
WHIFFS = {"foul_tip", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"}
KS = {"strikeout", "strikeout_double_play"}
DB_SPEC = {"D1": ("si_velo", -1, 1.0), "D2": ("fc_velo", -1, 1.0), "D3": ("fc_whiff", -1, .06), "D4": ("chase_rate", -1, .04),
           "D5": ("in_zone_rate", -1, .03), "D6": ("k_minus_bb", -1, .05), "B1": ("luck_gap", 1, .025), "B2": ("damage_top5", 1, .10)}
PINS = {HERE.parent / "uc-pps-036-mayza-2026-recap-001" / "dp_uc52_kernel.py": "3667f8028acd9974412d2d1a64cda3c6c335e7495f9d803a4b8cb29afebaa284",
        MLB / "cumulative_metric.py": "a28887406d98880993baa67aca5b3246db23e99615f3ffab28b1fb4ddf526365"}

# ---- own load ----
WANT = ["pitcher", "player_name", "game_type", "game_pk", "game_year", "game_date", "at_bat_number", "pitch_number", "inning", "events",
        "phillies_role", "description", "pitch_type", "release_speed", "zone", "woba_value", "woba_denom", "estimated_woba_using_speedangle",
        "type", "bat_score", "post_bat_score", "launch_speed", "strikes", "p_throws"]
fr = []
for y in range(2015, 2027):
    f = MLB / "data" / "phillies" / f"phils_{y}.parquet"
    cols = [c for c in WANT if c in pq.read_schema(f).names]
    fr.append(pd.read_parquet(f, columns=cols))
raw = pd.concat(fr, ignore_index=True)
raw["game_date"] = raw.game_date.astype(str).str[:10]
anchor = raw[raw.game_year == 2026].game_date.max()
pit = raw[(raw.phillies_role == "pitching")]
reg = pit[pit.game_type == "R"].drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
me = reg[reg.pitcher == PID]
s26 = me[me.game_year == SEASON]

# ---- KPI re-implementations ----
def pa_ends(d): return d[d.events.notna() & (d.events != "pickoff_1b")]
def rates(d):
    p = pa_ends(d); n = len(p)
    k = p.events.isin(KS).sum(); bb = (p.events == "walk").sum()
    sw = d.description.isin(SWINGS).sum(); wh = d.description.isin(WHIFFS).sum()
    ooz = (d.zone > 9).sum(); ch = ((d.zone > 9) & d.description.isin(SWINGS)).sum()
    wd = p[p.woba_denom.fillna(0) > 0]
    exp = pd.to_numeric(wd.estimated_woba_using_speedangle, errors="coerce")
    xn = np.where(wd.type.eq("X") & exp.notna(), exp, wd.woba_value.fillna(0))
    bip = d[d.type == "X"]
    rr = d.groupby(["game_pk", "at_bat_number"]).agg(a=("bat_score", "min"), b=("post_bat_score", "max"))
    return dict(pa=n, k=int(k), bb=int(bb), krate=k / n, bbrate=bb / n, k_minus_bb=(k - bb) / n, whiff=wh / sw if sw else np.nan,
                chase=ch / ooz if ooz else np.nan, zone=(len(d) - ooz) / len(d), csw=((d.description == "called_strike").sum() + wh) / len(d),
                woba_sc=wd.woba_value.sum() / wd.woba_denom.sum(), xwoba=xn.sum() / wd.woba_denom.sum(),
                hh=(bip.launch_speed >= 95).sum() / len(bip), hbp=int((p.events == "hit_by_pitch").sum()), runs=float((rr.b - rr.a).sum()),
                games=d.game_pk.nunique())
def runs_by_game(d):
    rr = d.groupby(["game_pk", "at_bat_number"]).agg(a=("bat_score", "min"), b=("post_bat_score", "max"), y=("game_year", "first"))
    rr["r"] = rr.b - rr.a
    return rr.groupby("game_pk").agg(r=("r", "sum"), y=("y", "first"))
def verdict(b, n, d, t):
    delta = (n - b) * d
    if abs(n - b) < t / 4: return "ABSENT"
    if delta >= t: return "PRESENT"
    if delta > 0: return "WEAK"
    if -delta >= t: return "CONTRA"
    return "ABSENT"
def rollup(v):
    n, p, c = len(v), v.count("PRESENT"), v.count("CONTRA")
    if n and p == n: return "STRONG"
    if c and p: return "MIXED"
    if p * 2 >= n and not c: return "SUPPORTED"
    return "UNSUPPORTED"

# ================= A · lineage =================
for f, h in PINS.items():
    check("A", f"sha256 {f.name}", hashlib.sha256(f.read_bytes()).hexdigest() == h, hashlib.sha256(f.read_bytes()).hexdigest()[:12], h[:12])
check("A", "anchor = max game_date in phils_2026", anchor == "2026-10-01" == H["frame"]["anchor"], anchor, "2026-10-01")
dq = pd.read_csv(OUT / "dp_uc53_dq_scorecard.csv")
check("A", "DQ scorecard has 0 FAIL", (dq.result == "FAIL").sum() == 0, dq.result.value_counts().to_dict())
kt = (HERE / "dp_uc53_kernel.py").read_text(encoding="utf-8")
check("A", "DB-1 registration note present in kernel", "REGISTERED 2026-10-18" in kt)
for r in H["db1"]["rows"]:
    m, d, t = DB_SPEC[r["sig"]]
    check("A", f"DB-1 {r['sig']} bar == 03 spec", r["metric"] == m and r["direction"] == d and near(r["threshold"], t), (r["metric"], r["direction"], r["threshold"]), (m, d, t))

# ================= B · frame =================
byy = me.groupby("game_year").size().to_dict()
check("B", "tenure pitches by year", {int(k): int(v) for k, v in byy.items()} == {int(k): v for k, v in H["frame"]["by_year"].items()}, byy, H["frame"]["by_year"])
check("B", "no pre-2021 pitching rows for 621237", me.game_year.min() == 2021, me.game_year.min())
e1 = raw[(raw.game_year == 2018) & (raw.pitcher == PID) & (raw.player_name != "Alvarado, José")]
check("B", "ENT-1 rows (2018, other name)", len(e1) == H["ent1_rows"] == 9, len(e1), 9)
sp = pit[(pit.pitcher == PID) & (pit.game_type == "S") & (pit.game_year == 2026)]
check("B", "spring 2026 pitches excluded", len(sp) == H["spring_2026_pitches"], len(sp), H["spring_2026_pitches"])
check("B", "own dedup removes nothing", len(pit[pit.game_type == "R"]) == len(reg), len(pit[pit.game_type == "R"]) - len(reg), 0)
check("B", "2026 games / first / last", (s26.game_pk.nunique(), s26.game_date.min(), s26.game_date.max()) == (68, H["frame"]["first"], H["frame"]["last"]),
      (s26.game_pk.nunique(), s26.game_date.min(), s26.game_date.max()))
ab = s26[s26.pitch_type.isna()]
check("B", "AB-1 rows are automatic ball/strike", len(ab) == H["ab1"]["rows_2026"] and ab.description.isin(["automatic_ball", "automatic_strike"]).all(), len(ab))
R26 = rates(s26); S = H["season"]
for k, hk, tol in [("pa", "plate_apps", 0), ("k", "strikeouts", 0), ("bb", "walks", 0), ("hbp", "hbp", 0), ("runs", "runs_created", 0),
                   ("krate", "krate", .0006), ("bbrate", "bbrate", .0006), ("k_minus_bb", "k_minus_bb", .0012), ("whiff", "whiff_rate", 1e-9),
                   ("chase", "chase_rate", .0006), ("zone", "in_zone_rate", .0006), ("csw", "csw_rate", 1e-9), ("woba_sc", "woba_sc", 1e-9),
                   ("xwoba", "xwoba", 1e-9), ("hh", "hard_hit_rate", 1e-9)]:
    check("B", f"2026 {k}", near(R26[k], S[hk], tol), R26[k], S[hk])
check("B", "AB-1 zone on thrown pitches", near((s26[s26.pitch_type.notna()].zone <= 9).mean(), H["ab1"]["zone_thrown_2026"]))
for p_ in ("FC", "SI"):
    for y in TEN:
        v = me[(me.game_year == y) & (me.pitch_type == p_)].release_speed.mean()
        check("B", f"{p_} velo {y}", near(v, H["pitch_by_year"][p_][str(y)]["velo"], 1e-9), round(v, 3))

# ================= C · context =================
lb = pa_ends(reg).groupby("pitcher").size().sort_values(ascending=False)
rk = int((lb > lb[PID]).sum() + 1)
check("C", "PA leaderboard rank / n / PA", (rk, len(lb), int(lb[PID])) == (H["leaderboard"]["rank"], H["leaderboard"]["n"], H["leaderboard"]["pa"]), (rk, len(lb), int(lb[PID])))
first = reg.sort_values(["game_pk", "inning", "at_bat_number", "pitch_number"]).drop_duplicates("game_pk")
starts = first.groupby("pitcher").size(); games = reg.groupby("pitcher").game_pk.nunique()
rp = (starts.reindex(games.index, fill_value=0) <= 0.2 * games)
above = [p for p in lb.index[:rk - 1] if rp[p]]
check("C", "relievers above him (RP-1t)", len(above) == 2 and H["leaderboard"]["rp_rank"] == 3, len(above))
check("C", "games rank", int((games > games[PID]).sum() + 1) == H["leaderboard"]["games_rank"], int((games > games[PID]).sum() + 1))
tw = reg[reg.strikes == 2].groupby(["pitcher", "pitch_type"]).size().rename("n2")
kk = reg[reg.events.isin(KS)].groupby(["pitcher", "pitch_type"]).size().rename("k")
pu = pd.concat([tw, kk], axis=1).dropna(subset=["n2"]); pu = pu[pu.n2 >= 20]; pu["r"] = pu.k / pu.n2
v = pu.loc[(PID, "FC"), "r"]
check("C", "cutter putaway value / rank / n", near(v, H["fc_putaway_house"]["value"], 1e-9) and int((pu.r > v).sum() + 1) == H["fc_putaway_house"]["rank"]
      and len(pu) == H["fc_putaway_house"]["n"], (round(v, 4), int((pu.r > v).sum() + 1), len(pu)))
g300 = pu[pu.n2 >= 300]
check("C", "cutter putaway rank among 300+", int((g300.r > v).sum() + 1) == H["fc_putaway_house"]["rank_ge300"] and len(g300) == H["fc_putaway_house"]["n_ge300"], (int((g300.r > v).sum() + 1), len(g300)))
g3 = reg.groupby(["pitcher", "pitch_type", "game_year"])
ws = pd.DataFrame(dict(n=g3.size(), sw=g3.description.apply(lambda s: s.isin(SWINGS).sum()), wh=g3.description.apply(lambda s: s.isin(WHIFFS).sum())))
ws = ws[(ws.n >= 50) & (ws.wh > 0)]; ws["w"] = ws.wh / ws.sw
for y in ("2021", "2026"):
    val = ws.loc[(PID, "FC", int(y)), "w"]
    check("C", f"cutter whiff {y} value / rank", near(val, H["fc_whiff_house"]["by_year"][y]["whiff"], 1e-9) and int((ws.w > val).sum() + 1) == H["fc_whiff_house"]["by_year"][y]["rank"],
          (round(val, 4), int((ws.w > val).sum() + 1)))
check("C", "whiff population n", len(ws) == H["fc_whiff_house"]["n"], len(ws), H["fc_whiff_house"]["n"])
pa_ps = pa_ends(reg).groupby(["pitcher", "game_year"]).size()
gp = reg.groupby(["pitcher", "game_year"]).game_pk.nunique()
st = first.groupby(["pitcher", "game_year"]).size().reindex(gp.index, fill_value=0)
rp_pop = ((st <= 0.2 * gp) & (pa_ps.reindex(gp.index) >= 100)).sum()
check("C", "house RP population n", int(rp_pop) == H["house_rp"]["n"], int(rp_pop), H["house_rp"]["n"])

# ================= D/E · story =================
rg = runs_by_game(me)
for y in TEN:
    g = rg[rg.y == y]
    bands = (int((g.r == 0).sum()), int((g.r == 1).sum()), int((g.r >= 2).sum()))
    ob = H["outing_bands"][str(y)]
    check("D", f"OD-1 bands {y}", bands == (ob["clean"], ob["dented"], ob["blowup"]), bands)
    top = g.r.sort_values(ascending=False).head(5).sum() / g.r.sum()
    check("D", f"OD-1 damage top-5 {y}", near(top, ob["damage_top5"], 1e-9), round(top, 4))
mo = s26.assign(m=pd.to_datetime(s26.game_date).dt.month.clip(lower=4))
for m_, p_ in [(6, "SI"), (9, "SI"), (6, "FC"), (9, "FC")]:
    v = mo[(mo.m == m_) & (mo.pitch_type == p_)].release_speed.mean()
    check("D", f"{p_} velo month {m_}", near(v, H["monthly_2026"][str(m_)][f"{p_.lower()}_velo"], 1e-9), round(v, 3))
for m_ in (8, 9):
    v = rates(mo[mo.m == m_])
    check("D", f"xwOBA month {m_}", near(v["xwoba"], H["monthly_2026"][str(m_)]["xwoba"], 1e-9), round(v["xwoba"], 4))
    check("D", f"BB% month {m_}", near(v["bbrate"], H["monthly_2026"][str(m_)]["bbrate"], .0006), round(v["bbrate"], 4))
cum = {}
for y in TEN:
    p = me[(me.game_year == y) & me.events.notna() & (me.events != "truncated_pa")].sort_values(["game_date", "game_pk", "at_bat_number"])  # CM-1 PA rule
    num = p.woba_value.fillna(0).where(p.woba_denom.fillna(0) > 0, 0).cumsum(); den = p.woba_denom.fillna(0).cumsum()
    cum[y] = pd.Series(np.where(den >= 25, num / den.replace(0, np.nan), np.nan), index=range(1, len(p) + 1))
    check("E", f"CM-1a endpoint {y} == WB-1", near(cum[y].iloc[-1], rates(me[me.game_year == y])["woba_sc"], 1e-9), round(cum[y].iloc[-1], 4))
cv = pd.DataFrame(cum); a26 = cv[SEASON].dropna(); prior = cv.drop(columns=SEASON).loc[a26.index].max(axis=1)
share = float((a26 > prior).mean())
check("E", "share of 2026 PAs above every prior season", near(share, SPECS["f09_cumulative_woba"]["share_pa_above_all_prior"], 1e-9), round(share, 4))
pooled = sum(rates(me[me.game_year == y])["woba_sc"] * 0 for y in []) or None
pr = pa_ends(me[me.game_year < SEASON]); pr = pr[pr.woba_denom.fillna(0) > 0]
check("E", "2026 line never reaches the pooled 2021-25 level", a26.min() > pr.woba_value.sum() / pr.woba_denom.sum(), round(a26.min(), 4), round(pr.woba_value.sum() / pr.woba_denom.sum(), 4))
def dbm(d, years):
    r = rates(d); fc = d[d.pitch_type == "FC"]; rf = rates(fc); g = runs_by_game(d)
    dmg = np.mean([gg.r.sort_values(ascending=False).head(5).sum() / gg.r.sum() for _, gg in g.groupby("y")])
    return dict(si_velo=d[d.pitch_type == "SI"].release_speed.mean(), fc_velo=fc.release_speed.mean(), fc_whiff=rf["whiff"], chase_rate=r["chase"],
                in_zone_rate=r["zone"], k_minus_bb=r["k_minus_bb"], luck_gap=r["woba_sc"] - r["xwoba"], damage_top5=dmg)
base = dbm(me[me.game_year.isin([2022, 2023, 2024])], None); now = dbm(s26, None)
vv = {}
for sig, (m, d, t) in DB_SPEC.items():
    vv[sig] = verdict(base[m], now[m], d, t)
    row = next(r for r in H["db1"]["rows"] if r["sig"] == sig)
    tol = .0006 if m in ("chase_rate", "in_zone_rate") else 1e-9       # K44 chase_rate rounds to 3 dp (spec 03 §2)
    check("E", f"DB-1 {sig} values + verdict", near(base[m], row["baseline"], tol) and near(now[m], row["season"], tol) and vv[sig] == row["verdict"],
          (round(base[m], 4), round(now[m], 4), vv[sig]), (row["baseline"], row["season"], row["verdict"]))
dec = rollup([vv[s] for s in DB_SPEC if s.startswith("D")]); bl = rollup([vv[s] for s in DB_SPEC if s.startswith("B")])
call = "DECLINE WITH NOISE" if dec in ("STRONG", "SUPPORTED") and bl in ("STRONG", "SUPPORTED") else "DECLINE" if dec in ("STRONG", "SUPPORTED") else "BLIP" if bl in ("STRONG", "SUPPORTED") else "UNRESOLVED"
check("E", "DB-1 roll-up and call", (dec, bl, call) == (H["db1"]["rollup"]["decline"], H["db1"]["rollup"]["blip"], H["db1"]["rollup"]["call"]), (dec, bl, call))
sb = dbm(me[me.game_year.isin([2021, 2022, 2023, 2024, 2025])], None)
sv = {s: verdict(sb[m], now[m], d, t) for s, (m, d, t) in DB_SPEC.items()}
sd = rollup([sv[s] for s in sv if s.startswith("D")]); sbl = rollup([sv[s] for s in sv if s.startswith("B")])
check("E", "DB-1 sensitivity call (2021-25)", ("DECLINE" if sd in ("STRONG", "SUPPORTED") and sbl not in ("STRONG", "SUPPORTED") else "?") == H["db1"]["sensitivity"]["rollup"]["call"], (sd, sbl))

# ================= F · published strings (formatted from harness values) =================
L = H["leaderboard"]
PUB = {
    "2026 wOBA Statcast basis": f3(R26["woba_sc"]), "2026 xwOBA": f3(R26["xwoba"]), "luck gap": f3(R26["woba_sc"] - R26["xwoba"]),
    "cutter velo 2026": f"{me[(me.game_year == 2026) & (me.pitch_type == 'FC')].release_speed.mean():.1f}",
    "sinker velo 2026": f"{me[(me.game_year == 2026) & (me.pitch_type == 'SI')].release_speed.mean():.1f}",
    "cutter whiff 2026": pc(ws.loc[(PID, "FC", 2026), "w"]), "cutter whiff 2021": pc(ws.loc[(PID, "FC", 2021), "w"]),
    "whiff rank 2026": f"#{int((ws.w > ws.loc[(PID, 'FC', 2026), 'w']).sum() + 1)}", "PA faced": f"{int(lb[PID]):,}", "leaderboard rank": f"#{rk}",
    "zone 2026": pc(R26["zone"]), "zone thrown 2026": pc((s26[s26.pitch_type.notna()].zone <= 9).mean()), "chase 2026": pc(R26["chase"]),
    "hard-hit 2026": pc(R26["hh"]), "K-BB 2026": pc(R26["k_minus_bb"]), "blow-ups": f"{int((rg[rg.y == 2026].r >= 2).sum())} of 68 outings",
    "clean outings": f"{int((rg[rg.y == 2026].r == 0).sum())} of 68 outings", "June sinker": f"{mo[(mo.m == 6) & (mo.pitch_type == 'SI')].release_speed.mean():.1f}",
    "Sept sinker": f"{mo[(mo.m == 9) & (mo.pitch_type == 'SI')].release_speed.mean():.1f}", "share above prior": pc(share, 0),
    "putaway": pc(pu.loc[(PID, 'FC'), 'r']), "tenure K": f"{int(pa_ends(me).events.isin(KS).sum())}", "HBP": f"hit {R26['hbp']} batters",
    "call": "DECLINE", "decline roll-up": dec, "blip roll-up": bl,
}
for name, sstr in PUB.items():
    check("F", f"report has {name} '{sstr}'", sstr in REPORT, "", sstr)
    check("F", f"dashboard has {name} '{sstr}'", sstr in DASH_T, "", sstr)
for bad in ["bridge-to-Duran", "fucntion", "NaN", "nan%", "{", "}}"]:
    check("F", f"banned '{bad}' absent from report", bad not in REPORT.replace("{{", ""), REPORT.count(bad))
check("F", "HP table has 10 graded rows", len(re.findall(r"^\| HP-\d\d \|", REPORT, flags=re.M)) == 10)

# ================= G · carry-in discipline =================
for src in ["CBS News", "NBC Sports Philadelphia", "6abc", "(SI)", "MLB.com", "(client)"]:
    check("G", f"carry-in source labelled: {src}", src in REPORT and src in DASH_T)
era_lines = [l for l in REPORT.splitlines() if re.search(r"\bERA\b", l)]
check("G", "ERA appears only as a carry-in or a 'not ERA' note", all(("5.86 ERA" in l) or ("Not ERA" in l) or ("xERA" in l) for l in era_lines), len(era_lines))
inj = [l for l in REPORT.splitlines() if re.search(r"injur", l, re.I)]
check("G", "no causal injury language", all(re.search(r"not (show|inferred)|does not show|missed time with injury|injury not inferred", l, re.I) for l in inj), inj[:2])
check("G", "$9M only beside its carry-in source", all(("CBS" in l) or ("CI-1" in l) for l in REPORT.splitlines() if "$9M" in l))

lg = pd.DataFrame(LOG); lg.to_csv(OUT / "dp_uc53_verification_log.csv", index=False)
n_pass = (lg.result == "PASS").sum()
print(f"{n_pass}/{len(lg)} PASS"); print(lg.groupby("family").result.value_counts().unstack(fill_value=0).to_string())
if n_pass != len(lg):
    print(lg[lg.result == "FAIL"].to_string()); sys.exit(1)
