"""dp_uc53_alvarado_recap.py - UC #53 / uc-pps-037 build. Writes every receipt to out/dp_uc53_* and every narrative
number to out/dp_uc53_headlines.json. Figures, report and dashboard read only these receipts."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc53_kernel as K
from phillies_dp import eda

OUT = K.OUT
P = lambda n: OUT / f"dp_uc53_{n}"
H = {}
LIN = K.assert_lineage()
ALL = lambda f, d, **kw: f(["_k"], d.assign(_k=1), **kw).drop(columns="_k").iloc[0]


def fnum(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)


# ---------------- frames ----------------
ph = K.load_house()
assert ph[(ph.pitcher == K.SUBJECT_ID) & (ph.game_year < 2021)].empty, "ENT-1: pre-tenure house rows leaked into the pitching frame"
cf, cf_receipt, milb = K.career_frame_for(ph)
cf_receipt.to_csv(P("career_receipt.csv"), index=False); milb.to_csv(P("career_milb_dropped.csv"), index=False)
te = cf[cf.game_year.isin(K.TENURE)].copy()
hz = ph[ph.pitcher == K.SUBJECT_ID]
chk = te.groupby("game_year").size().to_dict(), hz.groupby("game_year").size().to_dict()
assert chk[0] == chk[1], f"tenure frame != house log by year: {chk}"
s26 = te[te.game_year == K.SEASON].copy()
assert s26.game_type.eq("R").all() and s26.pitcher.eq(K.SUBJECT_ID).all()
print(eda.to_file(s26, "alvarado_2026_regular", "dp_uc53"))
print(eda.to_file(te, "alvarado_tenure_regular", "dp_uc53"))
H["frame"] = dict(pitches=int(len(s26)), games=int(s26.game_pk.nunique()), first=s26.game_date.min(), last=s26.game_date.max(),
                  anchor=K.ANCHOR_GAME_DATE, career_seasons=sorted(map(int, cf.game_year.unique())), career_pitches=int(len(cf)),
                  tenure_pitches=int(len(te)), tenure_games=int(te.game_pk.nunique()), milb_dropped=int(milb.rows.sum()) if len(milb) else 0,
                  by_year={int(k): int(v) for k, v in chk[0].items()})
assert H["frame"]["first"] == K.FIRST_APPEARANCE and H["frame"]["last"] == K.LAST_REGULAR_APPEARANCE

# postseason: own ledger
pa = K.load_phils_cols(years=K.TENURE, role="pitching", regular_only=False, cols=K.HOUSE_COLS)
ps = pa[(pa.pitcher == K.SUBJECT_ID) & pa.game_type.isin(K.POSTSEASON_TYPES)]
psl = K.nresults(["game_year"], ps).merge(ps.groupby("game_year", as_index=False).agg(games=("game_pk", "nunique")), on="game_year")
psl.to_csv(P("postseason_ledger.csv"), index=False)
H["postseason"] = psl[["game_year", "games", "pitches", "plate_apps", "strikeouts", "woba"]].to_dict("records")
raw18 = K.load_phils_cols(years=[2018], role=None, regular_only=False, cols=["pitcher", "player_name", "game_pk", "game_year", "game_type", "game_date"])
H["ent1_rows"] = int(((raw18.pitcher == K.SUBJECT_ID) & (raw18.player_name != K.SUBJECT_NAME)).sum())
H["spring_2026_pitches"] = int(((pa.pitcher == K.SUBJECT_ID) & (pa.game_type == "S") & (pa.game_year == 2026)).sum())


# ---------------- year table (results + indicators) ----------------
def profile(level, d):
    t = K.nresults(level, d)
    t = t.merge(d.groupby(level, as_index=False).agg(games=("game_pk", "nunique")), on=level, how="left")
    t = t.merge(K.runs_created(level, d), on=level, how="left"); t["rc_per_gm"] = t.runs_created / t.games
    t = t.merge(K.hard_hit_rate(level, d)[level + ["hard_hit_rate"]], on=level, how="left")
    t = t.merge(K.barrel_rate(level, d)[level + ["barrel_rate"]], on=level, how="left")
    xw = K.xwoba_pa(level, d); xc = [c for c in xw.columns if c.startswith("xwoba")][0]
    t = t.merge(xw[level + [xc]].rename(columns={xc: "xwoba"}), on=level, how="left")
    t = t.merge(K.woba_statcast(level, d)[level + ["woba_sc"]], on=level, how="left")
    t = t.merge(K.whiff_rate(level, d)[level + ["whiff_rate"]], on=level, how="left")
    t = t.merge(K.chase_rate(level, d)[level + ["chase_rate", "in_zone_rate"]], on=level, how="left")
    t = t.merge(K.csw(level, d)[level + ["csw_rate"]], on=level, how="left")
    hbp = d[d.events == "hit_by_pitch"].groupby(level, as_index=False).agg(hbp=("events", "size"))
    t = t.merge(hbp, on=level, how="left"); t["hbp"] = t.hbp.fillna(0); t["hbp_rate"] = t.hbp / t.plate_apps
    t["k_minus_bb"] = (t.strikeouts - t.walks) / t.plate_apps          # RK-2: from counts, not from K44's rounded rates
    t["luck_gap"] = t.woba_sc - t.xwoba
    return t


yr = profile(["game_year"], cf)
yr["team"] = np.where(yr.game_year >= 2021, "PHI", "TB")
yr.to_csv(P("career_by_year.csv"), index=False)
ten = yr[yr.team == "PHI"].copy()
c26 = ten[ten.game_year == K.SEASON].iloc[0]
def trank(col, asc=True):
    return int(ten.set_index("game_year")[col].rank(ascending=asc, method="min")[K.SEASON])
H["season"] = {k: fnum(c26[k]) for k in ["pitches", "plate_apps", "games", "ba", "obp", "slg", "ops", "woba", "woba_sc", "xwoba",
               "luck_gap", "krate", "bbrate", "hr_rate", "k_minus_bb", "runs_created", "rc_per_gm", "hard_hit_rate", "barrel_rate",
               "whiff_rate", "chase_rate", "in_zone_rate", "csw_rate", "hbp", "hbp_rate", "strikeouts", "walks", "hrs"]}
H["tenure_rank_2026"] = dict(n=int(len(ten)), woba_worst=trank("woba", False), rc_per_gm_worst=trank("rc_per_gm", False),
    xwoba_worst=trank("xwoba", False), krate_low=trank("krate"), bbrate_high=trank("bbrate", False), zone_low=trank("in_zone_rate"),
    whiff_low=trank("whiff_rate"), chase_low=trank("chase_rate"), hh_low=trank("hard_hit_rate"), csw_low=trank("csw_rate"),
    k_minus_bb_low=trank("k_minus_bb"), hbp_high=trank("hbp", False))
H["by_year"] = {int(r.game_year): {k: fnum(getattr(r, k)) for k in ["plate_apps", "games", "woba", "woba_sc", "xwoba", "ops", "ba", "krate",
                "bbrate", "k_minus_bb", "rc_per_gm", "hard_hit_rate", "barrel_rate", "whiff_rate", "chase_rate", "in_zone_rate", "csw_rate"]}
                | {"team": r.team} for r in yr.itertuples()}

# tenure totals
tt = K.nresults(["pitcher"], te).iloc[0]
H["tenure"] = dict(pitches=int(tt.pitches), plate_apps=int(tt.plate_apps), woba=float(tt.woba), ops=float(tt.ops), ba=float(tt.ba),
                   strikeouts=int(tt.strikeouts), walks=int(tt.walks), krate=float(tt.krate), bbrate=float(tt.bbrate),
                   games=int(te.game_pk.nunique()), runs_created=float(K.runs_created(["pitcher"], te).runs_created.iloc[0]))
pre = ten[ten.game_year < K.SEASON]
H["tenure_pre2026"] = {k: float((pre[k] * pre.plate_apps).sum() / pre.plate_apps.sum()) for k in
                       ["woba", "krate", "bbrate", "k_minus_bb", "whiff_rate", "chase_rate", "in_zone_rate", "hard_hit_rate"]}
pk = ten[ten.game_year.isin([2022, 2023])]
H["peak_2022_23"] = dict(krate=float(pk.strikeouts.sum() / pk.plate_apps.sum()), bbrate=float(pk.walks.sum() / pk.plate_apps.sum()),
    woba_best_rank={int(y): int(ten.set_index("game_year").woba.rank(method="min")[y]) for y in (2022, 2023)})

# ---------------- house leaderboard (Phillies PA faced, 2015-26, regular season) ----------------
hs = K.house_pitcher_seasons(ph)
hs.to_csv(P("house_pitcher_seasons.csv"), index=False)
role = K.tenure_role(hs, range(2015, 2027))
lb = hs.groupby("pitcher", as_index=False).agg(plate_apps=("plate_apps", "sum")).merge(role, on="pitcher")
lb = lb.sort_values("plate_apps", ascending=False).reset_index(drop=True); lb["rank"] = lb.index + 1
lb.to_csv(P("house_pa_leaderboard.csv"), index=False)
me = lb[lb.pitcher == K.SUBJECT_ID].iloc[0]
above_rp = lb[(lb["rank"] < me["rank"]) & (lb.role_span == "RP")]
H["leaderboard"] = dict(rank=int(me["rank"]), n=int(len(lb)), pa=int(me.plate_apps), games=int(me.games),
    rp_rank=int((lb[lb.role_span == "RP"].plate_apps > me.plate_apps).sum() + 1), n_rp=int((lb.role_span == "RP").sum()),
    rp_above=above_rp[["player_name", "plate_apps", "games", "starts"]].to_dict("records"),
    games_rank=int((lb.games > me.games).sum() + 1),
    top=lb.head(15)[["rank", "player_name", "plate_apps", "games", "starts", "role_span"]].to_dict("records"))

# ---------------- pitch types by year (FC, SI) ----------------
lv = ["game_year", "pitch_type"]
pt = cf[cf.pitch_type.isin(["FC", "SI", "SL", "FF"])]
py = pt.groupby(lv, as_index=False).agg(pitches=("pitch_type", "size"), velo=("release_speed", "mean"), velo_med=("release_speed", "median"),
        velo_p90=("release_speed", lambda s: s.quantile(.9)), spin=("release_spin_rate", "mean"),
        hb_in=("pfx_x", lambda s: 12 * s.mean()), ivb_in=("pfx_z", lambda s: 12 * s.mean()))
py["usage"] = py.pitches / py.game_year.map(cf.groupby("game_year").size())
for fn, cols in [(K.whiff_rate, ["whiff_rate"]), (K.chase_rate, ["chase_rate", "in_zone_rate"]), (K.putaway_rate, ["putaway_rate", "pitches2strikes"]),
                 (K.csw, ["csw_rate"])]:
    py = py.merge(fn(lv, pt)[lv + cols], on=lv, how="left")
py = py.merge(K.nresults(lv, pt)[lv + ["plate_apps", "ba", "slg", "woba", "krate"]], on=lv, how="left")
xw = K.xwoba_pa(lv, pt); xc = [c for c in xw.columns if c.startswith("xwoba")][0]
py = py.merge(xw[lv + [xc]].rename(columns={xc: "xwoba"}), on=lv, how="left")
py.to_csv(P("pitch_types_by_year.csv"), index=False)
cf[cf.pitch_type.isin(["FC", "SI"])][["game_year", "game_date", "pitch_type", "release_speed", "release_spin_rate", "pfx_x", "pfx_z"]].to_csv(
    P("fc_si_pitches.csv"), index=False)                                                   # pitch-level receipt for F5/F6
def pyv(ptp, y, c):
    r = py[(py.pitch_type == ptp) & (py.game_year == y)]
    return fnum(r[c].iloc[0]) if len(r) else None
H["pitch_by_year"] = {ptp: {int(y): {c: pyv(ptp, y, c) for c in ["pitches", "usage", "velo", "velo_med", "velo_p90", "spin", "hb_in", "ivb_in",
                       "whiff_rate", "chase_rate", "in_zone_rate", "putaway_rate", "csw_rate", "woba", "xwoba", "slg", "krate", "plate_apps"]}
                       for y in sorted(py[py.pitch_type == ptp].game_year.unique())} for ptp in ["FC", "SI"]}
for ptp in ["FC", "SI"]:
    v = py[(py.pitch_type == ptp)].set_index("game_year").velo
    H[f"{ptp.lower()}_velo"] = dict(y2026=float(v[2026]), peak=float(v.max()), peak_year=int(v.idxmax()),
                                   tenure_rank_low=int(v[v.index >= 2021].rank(method="min")[2026]),
                                   drop_vs_peak=float(v[2026] - v.max()))
fct = te[te.pitch_type == "FC"]
cr_ = ALL(K.chase_rate, fct); rr_ = ALL(K.nresults, fct)
H["fc_tenure"] = dict(pitches=int(len(fct)), in_zone=float(cr_.in_zone_rate), chase=float(cr_.chase_rate), ooz=int(cr_.ooz),
                      krate=float(rr_.krate), whiff=float(ALL(K.whiff_rate, fct).whiff_rate), putaway=float(ALL(K.putaway_rate, fct).putaway_rate))
mix26 = K.pitch_mix(s26); mix26.to_csv(P("arsenal_2026.csv"), index=False)
H["arsenal_2026"] = {r.pitch_type: dict(name=r.pitch_name, usage=float(r.usage), velo=float(r.release_speed), n=int(r.count)) for r in mix26.itertuples()}

# 2026 monthly (form and arm across the season)
s26m = s26.assign(month=pd.to_datetime(s26.game_date).dt.month.clip(lower=4))   # 3/28-3/31 folded into April
mo = profile(["month"], s26m)
for ptp in ["SI", "FC"]:
    mo = mo.merge(s26m[s26m.pitch_type == ptp].groupby("month", as_index=False).agg(**{f"{ptp.lower()}_velo": ("release_speed", "mean")}), on="month", how="left")
mo.to_csv(P("monthly_2026.csv"), index=False)
H["monthly_2026"] = {int(r.month): dict(pa=int(r.plate_apps), woba=float(r.woba), xwoba=fnum(r.xwoba), krate=float(r.krate), bbrate=float(r.bbrate),
                     si_velo=fnum(r.si_velo), fc_velo=fnum(r.fc_velo), games=int(r.games)) for r in mo.itertuples()}

# ---------------- cutter in house context ----------------
lv2 = ["pitcher", "pitch_type"]
zc = K.nresults(lv2, ph).merge(K.putaway_rate(lv2, ph), on=lv2, how="left", suffixes=("", "_par"))
zc = zc[zc.pitches2strikes >= 20].merge(hs.groupby("pitcher", as_index=False).player_name.last(), on="pitcher", how="left")
zc["putaway_rate"] = zc.strikeouts / zc.pitches2strikes                 # RK-1: rank on the unrounded rate (K44 rounds to 3 dp)
zc.to_csv(P("house_putaway_pitcher_pitch.csv"), index=False)
mz = zc[(zc.pitcher == K.SUBJECT_ID) & (zc.pitch_type == "FC")].iloc[0]
H["fc_putaway_house"] = dict(n=int(len(zc)), value=float(mz.putaway_rate), rank=int((zc.putaway_rate > mz.putaway_rate).sum() + 1),
    pitches2strikes=int(mz.pitches2strikes), pct=K.house_percentile(zc, "putaway_rate", float(mz.putaway_rate)),
    above_max_p2s=int(zc[zc.putaway_rate > mz.putaway_rate].pitches2strikes.max()),
    n_ge300=int((zc.pitches2strikes >= 300).sum()),
    rank_ge300=int((zc[zc.pitches2strikes >= 300].putaway_rate > mz.putaway_rate).sum() + 1),
    top5=zc.nlargest(5, "putaway_rate")[["player_name", "pitch_type", "putaway_rate", "pitches2strikes"]].to_dict("records"))
lv3 = ["pitcher", "pitch_type", "game_year"]
wc = K.nresults(lv3, ph)[lv3 + ["pitches"]].merge(K.whiff_rate(lv3, ph), on=lv3, how="left")
wc = wc[(wc.pitches >= 50) & wc.whiff_rate.notna()].merge(              # D-1: zero-whiff groups carry no rate; excluded, disclosed in 03 §4
    hs[["pitcher", "game_year", "player_name"]], on=["pitcher", "game_year"], how="left")
wc.to_csv(P("house_whiff_pitcher_pitch_season.csv"), index=False)
mine = wc[(wc.pitcher == K.SUBJECT_ID) & (wc.pitch_type == "FC")].sort_values("game_year")
H["fc_whiff_house"] = dict(n=int(len(wc)), by_year={int(r.game_year): dict(whiff=float(r.whiff_rate),
    pct=K.house_percentile(wc, "whiff_rate", float(r.whiff_rate)), rank=int((wc.whiff_rate > r.whiff_rate).sum() + 1)) for r in mine.itertuples()})

# ---------------- OD-1 outing bands + cumulative ----------------
gs = K.game_score(te)
gb = K.outing_bands(gs); gb.to_csv(P("appearance_log.csv"), index=False)
br = K.band_rates(gb); br["damage_top5"] = [K.damage_concentration(gb[gb.game_year == y]) for y in br.game_year]
br.to_csv(P("outing_bands_by_year.csv"), index=False)
H["outing_bands"] = {int(r["game_year"]): dict(apps=int(r["apps"]), clean=int(r["clean"]), dented=int(r["dented"]), blowup=int(r["blow-up"]),
                     clean_rate=float(r["clean_rate"]), blowup_rate=float(r["blow-up_rate"]), runs=float(r["runs"]), damage_top5=float(r["damage_top5"]))
                     for _, r in br.iterrows()}
g26 = gb[gb.game_year == K.SEASON]
H["outings_2026"] = dict(apps=int(len(g26)), clean=int((g26.band == "clean").sum()), blowups=int((g26.band == "blow-up").sum()),
    runs=float(g26.r.sum()), worst5_runs=float(g26.nlargest(5, "r").r.sum()),
    runs_outside_worst5=float(g26.r.sum() - g26.nlargest(5, "r").r.sum()),
    multi_inning=int((g26.inn_last > g26.inn_first).sum()), outs=int(g26.outs.sum()))
wsy = K.woba_statcast(["game_year"], te).rename(columns={"woba_sc": "value"})
cumf = K.cumulative_frame(te, K.WOBA_SC_SPEC, reconcile=wsy, tol=1e-9)          # CM-1a, endpoints == WB-1 (asserted)
cumf.to_csv(P("cumulative_woba.csv"), index=False)
cum_raw = K.cumulative_frame(te, "woba")                                          # module default (CM-D1 exposure)
fin = lambda c: {int(y): float(v) for y, v in c.groupby("game_year").value.last().items()}
H["cumulative"] = dict(final=fin(cumf), final_module_default=fin(cum_raw), min_den=int(cumf.attrs["min_den"]),
                       cm_d1_rows=int((te.events.notna() & (te.woba_denom.fillna(0) == 0) & (te.woba_value.fillna(0) > 0)).sum()))

# ---------------- DB-1 ledger ----------------
def db_metrics(d, gbs):
    r = ALL(K.nresults, d); w = ALL(K.chase_rate, d)
    xw = ALL(K.xwoba_pa, d); xcol = [c for c in xw.index if str(c).startswith("xwoba")][0]
    fc = d[d.pitch_type == "FC"]; si = d[d.pitch_type == "SI"]
    yrs = sorted(gbs.game_year.unique())
    return dict(si_velo=float(si.release_speed.mean()), fc_velo=float(fc.release_speed.mean()),
                fc_whiff=float(ALL(K.whiff_rate, fc).whiff_rate), chase_rate=float(w.chase_rate), in_zone_rate=float(w.in_zone_rate),
                k_minus_bb=float((r.strikeouts - r.walks) / r.plate_apps), luck_gap=float(ALL(K.woba_statcast, d).woba_sc - xw[xcol]),
                damage_top5=float(np.mean([K.damage_concentration(gbs[gbs.game_year == y]) for y in yrs])))
base_d = te[te.game_year.isin(K.DB_BASELINE_YEARS)]
base = db_metrics(base_d, gb[gb.game_year.isin(K.DB_BASELINE_YEARS)])
now = db_metrics(s26, g26)
led, roll = K.db1_ledger(base, now)
sens = db_metrics(te[te.game_year.isin(K.DB_SENSITIVITY_YEARS)], gb[gb.game_year.isin(K.DB_SENSITIVITY_YEARS)])
led_s, roll_s = K.db1_ledger(sens, now)
led.to_csv(P("db1_ledger.csv"), index=False); led_s.to_csv(P("db1_ledger_sensitivity_2021_25.csv"), index=False)
H["db1"] = dict(baseline_years=list(K.DB_BASELINE_YEARS), rows=led.to_dict("records"), rollup=roll,
                sensitivity=dict(years=list(K.DB_SENSITIVITY_YEARS), rollup=roll_s, verdicts=led_s.set_index("sig").verdict.to_dict()))

# ---------------- house reliever context for 2026 ----------------
rp = hs[(hs.role == "RP") & (hs.plate_apps >= K.KP_MIN_PA)].copy(); rp["k_minus_bb"] = (rp.strikeouts - rp.walks) / rp.plate_apps
rp.to_csv(P("house_rp_seasons.csv"), index=False)
m26 = rp[(rp.pitcher == K.SUBJECT_ID) & (rp.game_year == K.SEASON)].iloc[0]
H["house_rp"] = dict(n=int(len(rp)), years=[int(rp.game_year.min()), int(rp.game_year.max())],
    woba=K.house_percentile(rp, "woba", float(m26.woba), higher_is_better=False),
    rc_per_gm=K.house_percentile(rp, "rc_per_gm", float(m26.rc_per_gm), higher_is_better=False),
    k_minus_bb=K.house_percentile(rp, "k_minus_bb", float((m26.strikeouts - m26.walks) / m26.plate_apps)),
    tenure={int(r.game_year): K.house_percentile(rp, "woba", float(r.woba), higher_is_better=False)
            for r in rp[rp.pitcher == K.SUBJECT_ID].itertuples()},
    n_2026=int((rp.game_year == K.SEASON).sum()),
    rank_2026_pen=int((rp[rp.game_year == K.SEASON].woba < m26.woba).sum() + 1))


t26 = s26[s26.pitch_type.notna()]
H["ab1"] = dict(rows_2026=int(s26.pitch_type.isna().sum()), thrown_2026=int(len(t26)), rows_tenure=int(te.pitch_type.isna().sum()),
                zone_thrown_2026=float((t26.zone <= 9).mean()), auto_balls=int((s26.description == "automatic_ball").sum()),
                auto_strikes=int((s26.description == "automatic_strike").sum()))
# ---------------- DQ scorecard (rules specified in 05 §1; executed here) ----------------
DQ = []
def rule(i, dim, txt, ok, obs, warn=False):
    DQ.append(dict(rule=i, dimension=dim, rule_text=txt, result="PASS" if ok else ("WARN" if warn else "FAIL"), observed=obs))
key = ["pitcher"] + K.PITCH_KEY
rule("DQ-01", "uniqueness", "no duplicate pitch key in the tenure frame (pitch)", te.duplicated(subset=key).sum() == 0, int(te.duplicated(subset=key).sum()))
rule("DQ-02", "consistency", "entity lock: every tenure row pitcher == 621237 (pitch)", te.pitcher.eq(K.SUBJECT_ID).all(), int(te.pitcher.nunique()))
rule("DQ-03", "validity", "regular season only in the rate frames (pitch)", cf.game_type.eq("R").all(), str(sorted(cf.game_type.unique())))
rule("DQ-04", "timeliness", "phils_2026 file (all game types) current through the pinned anchor; regular season ends before it (file)",
     pa.game_date.max() == K.ANCHOR_GAME_DATE and ph.game_date.max() <= K.ANCHOR_GAME_DATE, f"file {pa.game_date.max()}, regular {ph.game_date.max()}")
rule("DQ-05", "consistency", "ENT-1: no pitching-role rows for 621237 before 2021; raw 2018 rows exist under another name", H["ent1_rows"] > 0 and
     ph[(ph.pitcher == K.SUBJECT_ID) & (ph.game_year < 2021)].empty, f"raw {H['ent1_rows']}, in frame 0")
thrown = te[te.pitch_type.notna()]
rule("DQ-06", "completeness", "release_speed non-null on every thrown pitch (tenure)", thrown.release_speed.notna().all(), int(thrown.release_speed.isna().sum()))
nul = te[te.pitch_type.isna()]
rule("DQ-07", "validity", "AB-1: every row without a pitch_type is an automatic ball/strike (no pitch thrown)",
     nul.description.isin(["automatic_ball", "automatic_strike"]).all(), f"{len(nul)} rows, all {sorted(nul.game_year.unique().tolist())}")
zn = int(te.zone.isna().sum())
rule("DQ-08", "validity", "zone null on tenure rows (K44 D-7 counts them in-zone; all are AB-1 rows)", zn == 0, f"{zn} rows; 2026 zone on thrown pitches {H['ab1']['zone_thrown_2026']:.3f}", warn=True)
rule("DQ-09", "consistency", "tenure frame == house log pitch counts by year", chk[0] == chk[1], str(chk[0]))
rule("DQ-10", "consistency", "CM-1a cumulative endpoints == WB-1 by year (asserted in build)", True, "tol 1e-9")
okb = all(v["clean"] + v["dented"] + v["blowup"] == v["apps"] for v in H["outing_bands"].values()) and \
      all(H["outing_bands"][int(y)]["apps"] == int(te[te.game_year == y].game_pk.nunique()) for y in K.TENURE)
rule("DQ-11", "consistency", "OD-1 bands partition appearances; appearances == games by year", okb, "6/6 seasons")
rule("DQ-12", "consistency", "carry-in CI-7 (NBC: 68 G, 70 K) reconciles to the log", H["frame"]["games"] == 68 and int(H["season"]["strikeouts"]) == 70, f"{H['frame']['games']} G, {int(H['season']['strikeouts'])} K")
rule("DQ-13", "accuracy", "CM-D1 exposure: PA ends with woba_value > 0 and woba_denom 0/NaN (tenure)", H["cumulative"]["cm_d1_rows"] == 0,
     H["cumulative"]["cm_d1_rows"], warn=True)
dqd = pd.DataFrame(DQ); dqd.to_csv(P("dq_scorecard.csv"), index=False)
H["dq"] = dqd.result.value_counts().to_dict()
assert "FAIL" not in H["dq"], dqd[dqd.result == "FAIL"]
H["lineage"] = LIN
json.dump(H, open(P("headlines.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("headlines written:", len(H), "blocks")
