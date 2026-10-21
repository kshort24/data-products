"""dp_uc52_verification.py — independent harness for UC #52 / uc-pps-036.
Imports NO build kernel for computation (pandas/numpy/pyarrow only). Re-reads parquet and re-implements each KPI from
the 03 §2 specs. Families: A lineage · B frame · C context · D story (KPIs) · E figures/claims · F published strings · G carry-ins.
Also writes the DQ scorecard. Outputs out/dp_uc52_verification_log.csv and out/dp_uc52_dq_scorecard.csv."""
from __future__ import annotations
import glob, hashlib, json, re
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent; OUT = ROOT / "out"
H = json.loads((OUT / "dp_uc52_headlines.json").read_text())
LOG, DQ = [], []
def chk(fam, name, ok, got="", exp=""):
    LOG.append(dict(family=fam, check=name, passed=bool(ok), got=str(got)[:160], expected=str(exp)[:160]))
SID, YR = 641835, 2026
KEY = ["game_pk", "at_bat_number", "pitch_number"]
STRIKEOUTS = {"strikeout", "strikeout_double_play"}

# ---------------- A lineage ----------------
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()           # noqa: E731
chk("A", "dp_uc51_kernel sha256 pinned", sha(ROOT / "dp_uc51_kernel.py") == "4845bae228615bf2322532287015712f3b5235252f20c2f82929d53d70b0f555")
chk("A", "headlines lineage matches disk", all(sha(ROOT / f) == h for f, h in H["lineage"].items()), list(H["lineage"])[:3])
for f in ["dp_uc52_kernel.py", "dp_uc52_mayza_recap.py", "dp_uc52_hp.py", "dp_uc52_build_figs.py", "dp_uc52_build_dashboard.py",
          "dp_uc52_build_report.py", "dp_uc52_build_pdf.py", "dp_uc52_narrative.py", "dp_uc52_mayza_2026_recap_report.pdf",
          "dp_uc52_mayza_2026_dashboard.html", "dp_uc52_mayza_2026_dashboard_artifact.html"]:
    chk("A", f"exists {f}", (ROOT / f).exists())
src = (ROOT / "dp_uc52_verification.py").read_text()
chk("A", "harness imports no build kernel", not re.search(r"^\s*(import|from)\s+dp_uc\d+", src, re.M))

# ---------------- B frame (independent read) ----------------
cols = ["pitcher", "player_name", "game_pk", "game_date", "game_year", "game_type", "home_team", "away_team", "inning", "inning_topbot",
        "at_bat_number", "pitch_number", "pitch_type", "release_speed", "release_pos_x", "release_pos_z", "release_extension", "pfx_x", "pfx_z",
        "plate_x", "plate_z", "zone", "spin_axis", "description", "events", "type", "bb_type", "balls", "strikes", "stand", "p_throws",
        "launch_speed", "launch_angle", "launch_speed_angle", "estimated_woba_using_speedangle", "woba_value", "woba_denom", "bat_score", "post_bat_score"]
def rd(f):
    import pyarrow.parquet as pq
    have = pq.read_schema(f).names
    return pd.read_parquet(f, columns=[c for c in cols if c in have])
ph = pd.concat([rd(f) for f in sorted(glob.glob(str(ROOT / "data/phillies/phils_20*.parquet")))], ignore_index=True)
# Phillies pitching rows: Phillies are the fielding team
ph = ph[((ph.home_team == "PHI") & (ph.inning_topbot == "Top")) | ((ph.away_team == "PHI") & (ph.inning_topbot == "Bot"))]
rs = ph[ph.game_type == "R"]
own = rd(ROOT / "data/opponents/mayza.parquet"); own = own[(own.pitcher == SID) & (own.game_type == "R")]
s26 = rs[(rs.pitcher == SID) & (rs.game_year == YR)]
chk("B", "2026 RS pitches", len(s26) == H["frame"]["pitches"] == 1093, len(s26), 1093)
chk("B", "2026 games", s26.game_pk.nunique() == H["frame"]["games"], s26.game_pk.nunique(), H["frame"]["games"])
chk("B", "first/last date", (s26.game_date.min(), s26.game_date.max()) == (H["frame"]["first"], H["frame"]["last"]), (s26.game_date.min(), s26.game_date.max()))
chk("B", "subject throws L only", set(s26.p_throws) == {"L"})
chk("B", "no duplicate pitch keys 2026", not s26.duplicated(subset=KEY).any())
car = pd.concat([rs[rs.pitcher == SID], own], ignore_index=True).drop_duplicates(subset=KEY)
chk("B", "career pitches (dedup by key)", len(car) == H["frame"]["career_pitches"], len(car), H["frame"]["career_pitches"])
chk("B", "career seasons", sorted(car.game_year.unique().tolist()) == H["frame"]["career_seasons"], sorted(car.game_year.unique().tolist()))
ps = ph[(ph.pitcher == SID) & ph.game_type.isin(["F", "D", "L", "W"]) & (ph.game_year == YR)]
chk("B", "postseason kept out of rates (own ledger)", len(ps) == H["postseason"][0]["pitches"], len(ps))
chk("B", "anchor", ph.game_date.max() <= H["frame"]["anchor"], ph.game_date.max())

# ---------------- re-implemented KPIs (from 03 §2 specs) ----------------
def pa_end(d): return d[d.woba_denom.fillna(0) > 0]
def woba(d): p = pa_end(d); return p.woba_value.sum() / p.woba_denom.sum()
def xwoba(d):
    p = pa_end(d); e = p.estimated_woba_using_speedangle
    num = np.where((p.type == "X") & e.notna(), e, p.woba_value.fillna(0)); return num.sum() / p.woba_denom.sum()
def pas(d): return int(d.events.notna().sum())
def krate(d): return d.events.isin(STRIKEOUTS).sum() / pas(d)
def bbrate(d): return d.events.isin(["walk"]).sum() / pas(d)
def hh(d): b = d[d.type == "X"]; return (b.launch_speed >= 95).sum() / len(b)
def barrel(d): b = d[(d.type == "X") & d.launch_speed_angle.notna()]; return (b.launch_speed_angle == 6).sum() / len(b)
def qa1(d):
    d = d.sort_values(["game_pk", "at_bat_number", "pitch_number"]); out = []
    for _, g in d.groupby(["game_pk", "at_bat_number"]):
        if pd.isna(g.events.iloc[-1]): continue
        s = g.strikes.tolist(); post = s[1:] + [3 if g.events.iloc[-1] in STRIKEOUTS else s[-1] + int(g.type.iloc[-1] == "S" and s[-1] < 2)]
        early = (g.pitch_number <= 3).tolist()
        two = any(e and p >= 2 for e, p in zip(early, post))
        gb = any(e and t == "X" and b == "ground_ball" for e, t, b in zip(early, g.type, g.bb_type))
        out.append(two or gb)
    return float(np.mean(out)), len(out)
TOL = 0.0015
S = H["season"]
W = pd.read_csv(ROOT / "wOBA and FIP Constants.csv").drop_duplicates("Season").set_index("Season")
def woba_house(d):   # K44 definition re-implemented: FanGraphs weights, denominator = every PA event except pickoff_1b
    e = d[d.events.notna() & (d.events != "pickoff_1b")]; w = W.loc[int(e.game_year.iloc[0])]
    num = sum(w[c] * e.events.eq(ev).sum() for c, ev in [("wBB", "walk"), ("wHBP", "hit_by_pitch"), ("w1B", "single"), ("w2B", "double"), ("w3B", "triple"), ("wHR", "home_run")])
    return num / len(e)
chk("D", "2026 house wOBA re-implemented (FanGraphs weights)", abs(woba_house(s26) - S["woba"]) <= 0.0015, round(woba_house(s26), 4), round(S["woba"], 4))
for nm, fn in [("woba_sc", woba), ("xwoba", xwoba), ("krate", krate), ("bbrate", bbrate), ("hard_hit_rate", hh), ("barrel_rate", barrel)]:
    v = fn(s26); chk("D", f"2026 {nm} re-implemented", abs(v - S[nm]) <= TOL, round(v, 4), round(S[nm], 4))
q, n = qa1(s26); chk("D", "QA-1 2026 re-implemented", abs(q - H["quick_ab"]["rate"]) < 1e-9 and n == H["quick_ab"]["pas"], (round(q, 4), n))
qc, nc = qa1(car); chk("D", "QA-1 career re-implemented", abs(qc - H["quick_ab"]["career"]) < 1e-9 and nc == H["quick_ab"]["career_pas"], (round(qc, 4), nc))
for st in ["L", "R"]:
    d = s26[s26.stand == st]
    chk("D", f"platoon {st} wOBA (house)", abs(woba_house(d) - H["platoon"][st]["woba"]) <= TOL, round(woba_house(d), 4), H["platoon"][st]["woba"])
    chk("D", f"platoon {st} wOBA (Statcast)", abs(woba(d) - H["platoon"][st]["woba_sc"]) <= TOL, round(woba(d), 4), H["platoon"][st]["woba_sc"])
    chk("D", f"platoon {st} barrel", abs(barrel(d) - H["platoon"][st]["barrel_rate"]) <= TOL, round(barrel(d), 4))
    chk("D", f"platoon {st} xwOBA", abs(xwoba(d) - H["platoon"][st]["xwoba"]) <= TOL, round(xwoba(d), 4))
# career ranks (wOBA, HH, barrel) by season
cs = pd.DataFrame([dict(y=y, woba=woba_house(g), hh=hh(g), barrel=barrel(g), qa=qa1(g)[0]) for y, g in car.groupby("game_year")]).set_index("y")
chk("D", "career wOBA rank (low)", int(cs.woba.rank(method="min")[YR]) == H["career_rank"]["woba_low"], int(cs.woba.rank(method="min")[YR]))
chk("D", "career HH rank (high)", int(cs.hh.rank(ascending=False, method="min")[YR]) == H["career_rank"]["hh_high"])
chk("D", "career barrel rank (low)", int(cs.barrel.rank(method="min")[YR]) == H["career_rank"]["barrel_low"])
chk("D", "career QA-1 lowest in 2026", int(cs.qa.rank(ascending=False, method="min")[YR]) == H["career_rank"]["quick_ab_high"] == len(cs))
# BS-1
sl = pd.concat([rs[(rs.p_throws == "L") & (rs.pitch_type == "SL") & (rs.pitcher != SID)], car[car.pitch_type == "SL"]])
g = sl.groupby(["pitcher", "game_year"]).agg(n=("pfx_x", "size"), hb=("pfx_x", "mean"), ivb=("pfx_z", "mean"))
g = g[g.n >= 50]; g["bullet"] = (12 * g.hb.abs() <= 4) & (12 * g.ivb.abs() <= 4)
chk("D", "BS-1 Mayza 2026 bullet", bool(g.loc[(SID, YR), "bullet"]))
oth = g.drop(index=[i for i in g.index if i[0] == SID])
chk("D", "BS-1 other bullet seasons", int(oth.bullet.sum()) == H["bullet_slider"]["n_bullet_others"] and len(oth) == H["bullet_slider"]["n_pop"], (int(oth.bullet.sum()), len(oth)))
# DS-1
rows = []
for (pid, y), gg in pd.concat([rs[(rs.p_throws == "L") & (rs.pitcher != SID)], car]).groupby(["pitcher", "game_year"]):
    if len(gg) < 150: continue
    fb = gg[gg.pitch_type.isin(["FF", "SI"])].pitch_type.value_counts()
    if fb.empty: continue
    f = gg[gg.pitch_type == fb.index[0]]
    rows.append(dict(pitcher=pid, y=y, name=gg.player_name.iloc[-1], a=gg.release_pos_x.mean(), b=gg.release_pos_z.mean(), c=gg.release_extension.mean(),
                     d=f.release_speed.mean(), e=12 * f.pfx_x.mean(), f=12 * f.pfx_z.mean()))
t = pd.DataFrame(rows).dropna(); fz = ["a", "b", "c", "d", "e", "f"]
z = (t[fz] - t[fz].mean()) / t[fz].std(ddof=0); me = z[(t.pitcher == SID) & (t.y == YR)].values[0]
t["dist"] = np.sqrt(((z - me) ** 2).sum(axis=1)); near = t[t.pitcher != SID].sort_values("dist").drop_duplicates("pitcher")
chk("D", "DS-1 nearest comp", (near.name.iloc[0], int(near.y.iloc[0])) == (H["delivery"]["comps"][0]["player_name"], H["delivery"]["comps"][0]["game_year"]), (near.name.iloc[0], near.y.iloc[0]))
chk("D", "DS-1 Alvarado rank", int(np.where(near.name.str.startswith("Alvarado"))[0][0] + 1) == H["delivery"]["alvarado"]["rank"])

# ---------------- C context: house LHP relievers (RP-1) ----------------
first = rs.sort_values(["game_pk", "inning", "at_bat_number", "pitch_number"]).drop_duplicates("game_pk")[["game_pk", "pitcher"]]
st = set(map(tuple, first.values))
recs = []
for (pid, y), gg in rs[rs.p_throws == "L"].groupby(["pitcher", "game_year"]):
    games = gg.game_pk.unique(); starts = sum((gp, pid) in st for gp in games)
    if starts > 0.2 * len(games) or pas(gg) < 100: continue
    recs.append(dict(pitcher=pid, y=y, woba=woba_house(gg), bb=bbrate(gg)))
lr = pd.DataFrame(recs)
chk("C", "LHP RP population n", len(lr) == H["house_lhp_rp"]["n"], len(lr), H["house_lhp_rp"]["n"])
r = int((lr.woba < lr[(lr.pitcher == SID) & (lr.y == YR)].woba.iloc[0]).sum() + 1)
chk("C", "Mayza wOBA rank among LHP RP (house basis)", r == H["house_lhp_rp"]["woba"]["rank"], r, H["house_lhp_rp"]["woba"]["rank"])
rb = int((lr.bb < lr[(lr.pitcher == SID) & (lr.y == YR)].bb.iloc[0]).sum() + 1)
chk("C", "Mayza BB% rank among LHP RP", rb == H["house_lhp_rp"]["bbrate"]["rank"], rb, H["house_lhp_rp"]["bbrate"]["rank"])

# ---------------- E figure claims ----------------
specs = pd.read_csv(OUT / "dp_uc52_figure_specs.csv"); br = pd.read_csv(OUT / "dp_uc52_brand_checks.csv")
chk("E", "10 figures, all brand checks pass", len(specs) == 10 and br.drop(columns=["figure", "off_palette"]).all().all())
chk("E", "figure count within cap", len(specs) <= 10)
hpg = pd.read_csv(OUT / "dp_uc52_hp_grades.csv"); chk("E", "14 HP rows graded", len(hpg) == 14 and hpg.grade.notna().all())

# ---------------- F published strings ----------------
md = (ROOT / "dp_uc52_mayza_2026_recap_report.md").read_text(encoding="utf-8")
dash = (ROOT / "dp_uc52_mayza_2026_dashboard.html").read_text(encoding="utf-8").split('<script id="payload"')[0]
chk("F", "report section cap ≤ 9", sum(1 for l in md.splitlines() if l.startswith("## ")) <= 9)
chk("F", "dashboard chapters ≤ 8", dash.count('class="chno">Chapter') <= 8, dash.count('class="chno">Chapter'))
chk("F", "no 'nan'/'None' published", not re.search(r"\bnan\b|\bNone\b", md + dash), re.findall(r".{20}\bnan\b.{10}", md)[:2])
chk("F", "no bad ordinals", not re.search(r"\b\d*(1[123]st|1[123]nd|1[123]rd|[^1]?1th|[^1]?2th|[^1]?3th)\b", md + dash))
want = {"woba": f"{S['woba']:.3f}".lstrip("0"), "xwoba": f"{S['xwoba']:.3f}".lstrip("0"), "bb": f"{100 * S['bbrate']:.1f}%",
        "qa": f"{100 * H['quick_ab']['rate']:.1f}%", "hh": f"{100 * S['hard_hit_rate']:.1f}%", "ext": f"{H['delivery']['ext']:.2f} ft"}
for k, v in want.items():
    chk("F", f"string '{v}' in report and dashboard", v in md and v in dash, v)
chk("F", "re-implemented house wOBA string matches published", f"{woba_house(s26):.3f}".lstrip("0") == want["woba"], f"{woba_house(s26):.3f}")
chk("F", "Statcast-basis wOBA string published beside xwOBA", f"{woba(s26):.3f}".lstrip("0") in md and f"{woba(s26):.3f}".lstrip("0") in dash)
chk("F", "'third-best of nine' consistent", "third-best of his nine" in dash and H["career_rank"]["woba_low"] == 3)
import markdown
from html.parser import HTMLParser
class _T(HTMLParser):
    def __init__(self): super().__init__(); self.t = []
    def handle_data(self, d): self.t.append(d)
_p = _T(); _p.feed(markdown.markdown(md, extensions=["tables"])); _txt = " ".join(_p.t)
_heads = [l[3:].strip() for l in md.splitlines() if l.startswith("## ")] + ["Candid caveats"]
chk("F", "no HP cell split by a pipe (RQ-3)", all("|" not in str(x) for x in hpg.governed.tolist() + hpg.claim.tolist()))
chk("F", "every report section survives HTML rendering (RQ-2)", all(h in _txt for h in _heads), [h for h in _heads if h not in _txt])
pdfp = ROOT / "dp_uc52_mayza_2026_recap_report.pdf"
chk("F", "pdf ≤ 10 pages", pdfp.read_bytes().count(b"/Type /Page\n") <= 10 or pdfp.read_bytes().count(b"/Type /Page") - pdfp.read_bytes().count(b"/Type /Pages") <= 10)

# ---------------- G carry-ins ----------------
hs = json.dumps(H)
chk("G", "no carry-in value computed on (headlines)", "2025-08-31" not in hs and "MLBTR" not in hs)
for ci in ["2025-08-31", "not verified"]:
    chk("G", f"carry-in '{ci}' labelled in report", ci in md and "Carry-ins, never computed on" in md)
chk("G", "no ERA published", not re.search(r"\bERA\b(?! )", md.replace("It is not ERA", "").replace("not ERA", "")))

# ---------------- DQ scorecard (2026 subject frame + career) ----------------
def dq(rule, dim, ok, n_bad=0):
    DQ.append(dict(rule=rule, dimension=dim, passed=bool(ok), failing_rows=int(n_bad)))
dq("DQ-01 pitch key unique (career)", "uniqueness", not car.duplicated(subset=KEY).any(), car.duplicated(subset=KEY).sum())
dq("DQ-02 game_type == R (rates)", "validity", set(car.game_type) == {"R"})
dq("DQ-03 release_speed in [60,105]", "validity", s26.release_speed.dropna().between(60, 105).all(), (~s26.release_speed.dropna().between(60, 105)).sum())
dq("DQ-04 |pfx| ≤ 3 ft", "validity", (s26[["pfx_x", "pfx_z"]].abs().dropna() <= 3).all().all())
dq("DQ-05 spin_axis in [0,360]", "validity", s26.spin_axis.dropna().between(0, 360).all())
dq("DQ-06 release_extension in [4,8] ft", "validity", s26.release_extension.dropna().between(4, 8).all(), (~s26.release_extension.dropna().between(4, 8)).sum())
dq("DQ-07 pitch_type null ≤ 1%", "completeness", s26.pitch_type.isna().mean() <= 0.01, s26.pitch_type.isna().sum())
dq("DQ-08 BIP launch_speed tracked ≥ 95%", "completeness", s26[s26.type == "X"].launch_speed.notna().mean() >= 0.95, s26[s26.type == "X"].launch_speed.isna().sum())
dq("DQ-09 career launch_speed_angle coverage on BIP ≥ 90%", "completeness", car[car.type == "X"].launch_speed_angle.notna().mean() >= 0.9,
   car[car.type == "X"].launch_speed_angle.isna().sum())
dq("DQ-10 arm_angle coverage 2026 (informational ≥ 70%)", "completeness", s26.arm_angle.notna().mean() >= 0.7 if "arm_angle" in s26 else True)
dq("DQ-11 woba_denom present on PA-ending rows", "consistency", (s26[s26.events.notna()].woba_denom.notna().mean()) >= 0.99)
dq("DQ-12 game_date ≤ anchor", "timeliness", s26.game_date.max() <= H["frame"]["anchor"])
pd.DataFrame(DQ).to_csv(OUT / "dp_uc52_dq_scorecard.csv", index=False)
L = pd.DataFrame(LOG); L.to_csv(OUT / "dp_uc52_verification_log.csv", index=False)
print(f"verification {L.passed.sum()}/{len(L)} pass; DQ {sum(d['passed'] for d in DQ)}/{len(DQ)} pass")
print(L[~L.passed].to_string(index=False)[:1500]); print(pd.DataFrame(DQ)[lambda x: ~x.passed].to_string(index=False))
