"""dp_uc52_mayza_recap.py — UC #52 / uc-pps-036 build. Writes every receipt to out/dp_uc52_* and every
narrative number to out/dp_uc52_headlines.json. Figures, report and dashboard read only these receipts."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc52_kernel as K
from phillies_dp import eda

OUT = K.ROOT / "out"; OUT.mkdir(exist_ok=True)
P = lambda n: OUT / f"dp_uc52_{n}"
H = {}                                     # headlines
LIN = K.assert_lineage()

# ---------------- frames ----------------
ph = K.load_house()
cf, cf_receipt = K.career_frame_ext(ph)
cf_receipt.to_csv(P("career_receipt.csv"), index=False)
s26 = cf[cf.game_year == K.SEASON].copy()
assert s26.game_type.eq("R").all() and s26.pitcher.eq(K.SUBJECT_ID).all()
print(eda.to_file(s26, "mayza_2026_regular", "dp_uc52"))
H["frame"] = dict(pitches=int(len(s26)), games=int(s26.game_pk.nunique()), first=s26.game_date.min(),
                  last=s26.game_date.max(), anchor=K.ANCHOR_GAME_DATE, career_seasons=sorted(map(int, cf.game_year.unique())),
                  career_pitches=int(len(cf)))
assert H["frame"]["first"] == K.FIRST_APPEARANCE and H["frame"]["last"] == K.LAST_REGULAR_APPEARANCE

# postseason: own ledger
ps = K.load_phils_cols(years=[K.SEASON], role="pitching", regular_only=False, cols=K.HOUSE_COLS)
ps = ps[(ps.pitcher == K.SUBJECT_ID) & ps.game_type.isin(K.POSTSEASON_TYPES)]
psl = K.nresults(["game_type", "game_date"], ps); psl.to_csv(P("postseason_ledger.csv"), index=False)
H["postseason"] = psl.to_dict("records")

# ---------------- career table (results + indicators) ----------------
def profile(level, d):
    t = K.nresults(level, d)
    t = t.merge(d.groupby(level, as_index=False).agg(games=("game_pk", "nunique")), on=level, how="left")
    t = t.merge(K.runs_created(level, d), on=level, how="left")
    t["rc_per_gm"] = t.runs_created / t.games
    t = t.merge(K.hard_hit_rate(level, d)[level + ["hard_hit_rate"]], on=level, how="left")
    br = K.barrel_rate(level, d); t = t.merge(br[level + ["barrel_rate"]], on=level, how="left")
    xw = K.xwoba_pa(level, d); t = t.merge(xw[level + [c for c in xw.columns if c.startswith("xwoba")]], on=level, how="left")
    t = t.merge(K.woba_statcast(level, d)[level + ["woba_sc"]], on=level, how="left")
    bip = d[d.type == "X"]
    t = t.merge(bip.groupby(level, as_index=False).agg(ev_mu=("launch_speed", "mean"), la_mu=("launch_angle", "mean"),
                dist_mu=("hit_distance_sc", "mean"), xba_bip=("estimated_ba_using_speedangle", "mean"),
                xslg_bip=("estimated_slg_using_speedangle", "mean"),
                gb_rate=("bb_type", lambda s: (s == "ground_ball").mean())), on=level, how="left")
    t = t.merge(K.whiff_rate(level, d)[level + ["whiff_rate"]], on=level, how="left")
    t = t.merge(K.chase_rate(level, d)[level + ["chase_rate", "in_zone_rate"]], on=level, how="left")
    t = t.merge(K.quick_ab_rate(level, d), on=level, how="left")
    t["k_minus_bb"] = t.krate - t.bbrate
    return t

car = profile(["game_year"], cf)
xcol = [c for c in car.columns if c.startswith("xwoba")][0]
car = car.rename(columns={xcol: "xwoba"}); car["xwoba_gap"] = car.xwoba - car.woba_sc   # same basis only (WB-1)
car.to_csv(P("career.csv"), index=False)
c26 = car[car.game_year == K.SEASON].iloc[0]
def rank(col, asc=True, d=car):
    v = d.set_index("game_year")[col].rank(ascending=asc, method="min")
    return int(v[K.SEASON])
H["season"] = {k: (float(c26[k]) if pd.notna(c26[k]) else None) for k in
               ["pitches", "plate_apps", "games", "ba", "obp", "slg", "ops", "woba", "woba_sc", "xwoba", "xwoba_gap", "krate", "bbrate",
                "hr_rate", "k_minus_bb", "runs_created", "rc_per_gm", "hard_hit_rate", "barrel_rate", "ev_mu", "la_mu",
                "dist_mu", "gb_rate", "whiff_rate", "chase_rate", "in_zone_rate", "quick_ab_rate", "qa_2k_rate", "qa_gb_rate", "qa_pas"]}
H["career_rank"] = dict(n_seasons=int(len(car)), woba_low=rank("woba"), woba_sc_low=rank("woba_sc"), ops_low=rank("ops"), xwoba_low=rank("xwoba"),
                        hh_high=rank("hard_hit_rate", False), barrel_low=rank("barrel_rate"), dist_high=rank("dist_mu", False),
                        la_high=rank("la_mu", False), rc_per_gm_low=rank("rc_per_gm"), quick_ab_high=rank("quick_ab_rate", False),
                        krate_high=rank("krate", False), bbrate_low=rank("bbrate"))
prior = car[car.game_year < K.SEASON]
H["career_prior"] = dict(woba=float((prior.woba * prior.plate_apps).sum() / prior.plate_apps.sum()),
                         krate_min=float(prior.krate.min()), krate_max=float(prior.krate.max()),
                         bbrate_min=float(prior.bbrate.min()), bbrate_max=float(prior.bbrate.max()),
                         hr_min=float(prior.hr_rate.min()), hr_max=float(prior.hr_rate.max()),
                         hh_since_rookie_max=float(prior[prior.game_year > prior.game_year.min()].hard_hit_rate.max()),
                         rookie_year=int(prior.game_year.min()), small_seasons=[int(y) for y in car[car.pitches < 400].game_year])
car_all = profile([], cf.assign(_k=1)) if False else None

# ---------------- platoon 2026 ----------------
pl = profile(["stand"], s26)
pl = pl.rename(columns={[c for c in pl.columns if c.startswith("xwoba")][0]: "xwoba"})
pl.to_csv(P("platoon_2026.csv"), index=False)
H["platoon"] = {r.stand: {k: float(getattr(r, k)) for k in ["plate_apps", "woba", "woba_sc", "xwoba", "ops", "slg", "krate", "bbrate",
                "hr_rate", "hard_hit_rate", "barrel_rate", "whiff_rate", "quick_ab_rate"]} for r in pl.itertuples()}

# ---------------- arsenal & weapons 2026 ----------------
lv = ["stand", "pitch_type", "pitch_name"]
ars = s26.groupby(lv, as_index=False).agg(pitches=("pitch_type", "size"), velo=("release_speed", "mean"),
        hb_in=("pfx_x", lambda s: 12 * s.mean()), ivb_in=("pfx_z", lambda s: 12 * s.mean()),
        spin=("release_spin_rate", "mean"), plate_x=("plate_x", "mean"), plate_z=("plate_z", "mean"))
ars["usage"] = ars.pitches / ars.groupby("stand").pitches.transform("sum")
for fn, cols in [(K.whiff_rate, ["whiff_rate"]), (K.chase_rate, ["chase_rate", "in_zone_rate"]), (K.putaway_rate, ["putaway_rate"])]:
    ars = ars.merge(fn(lv, s26)[lv + cols], on=lv, how="left")
res = K.nresults(lv, s26)[lv + ["plate_apps", "ba", "slg", "woba"]]
ars = ars.merge(res, on=lv, how="left")
ars.to_csv(P("weapons_2026.csv"), index=False)
mix = s26.groupby(["pitch_type", "pitch_name"], as_index=False).agg(pitches=("pitch_type", "size"), velo=("release_speed", "mean"),
        velo_sd=("release_speed", "std"), hb_in=("pfx_x", lambda s: 12 * s.mean()), ivb_in=("pfx_z", lambda s: 12 * s.mean()),
        spin=("release_spin_rate", "mean"), spin_axis=("spin_axis", "mean"), ext=("release_extension", "mean"))
mix["usage"] = mix.pitches / mix.pitches.sum(); mix = mix.sort_values("pitches", ascending=False)
mix.to_csv(P("arsenal_2026.csv"), index=False)
H["arsenal"] = {r.pitch_type: dict(name=r.pitch_name, usage=float(r.usage), velo=float(r.velo), hb_in=float(r.hb_in),
                ivb_in=float(r.ivb_in), spin_axis=float(r.spin_axis), pitches=int(r.pitches)) for r in mix.itertuples()}
H["weapons"] = {f"{r.pitch_type}_vs_{r.stand}": dict(pitches=int(r.pitches), usage=float(r.usage),
                whiff=None if pd.isna(r.whiff_rate) else float(r.whiff_rate),
                chase=None if pd.isna(r.chase_rate) else float(r.chase_rate),
                zone=None if pd.isna(r.in_zone_rate) else float(r.in_zone_rate),
                putaway=None if pd.isna(r.putaway_rate) else float(r.putaway_rate),
                pa=None if pd.isna(r.plate_apps) else int(r.plate_apps), slg=None if pd.isna(r.slg) else float(r.slg),
                woba=None if pd.isna(r.woba) else float(r.woba),
                plate_x=float(r.plate_x), plate_z=float(r.plate_z)) for r in ars.itertuples()}
si = s26[s26.pitch_type == "SI"]
H["si_zone"] = {st: dict(in_zone=float(g.zone.between(1, 9).mean()), middle_third=float((g.plate_x.abs() <= 0.83 / 3).mean()),
                heart_zone5=float((g.zone == 5).mean())) for st, g in si.groupby("stand")}

# ---------------- house context ----------------
hs = K.house_pitcher_seasons(ph)
hs.to_csv(P("house_pitcher_seasons.csv"), index=False)
lrp = hs[(hs.p_throws == "L") & (hs.role == "RP") & (hs.plate_apps >= K.KP_MIN_PA)].copy()
me = lrp[(lrp.pitcher == K.SUBJECT_ID) & (lrp.game_year == K.SEASON)]
assert len(me) == 1, "subject season missing from the LHP RP population"
lrp["k_minus_bb"] = lrp.krate - lrp.bbrate
lrp.to_csv(P("house_lhp_rp.csv"), index=False)
mrow = me.iloc[0]
H["house_lhp_rp"] = dict(n=int(len(lrp)), years=[int(lrp.game_year.min()), int(lrp.game_year.max())],
    woba=K.house_percentile(lrp, "woba", float(mrow.woba), higher_is_better=False),
    ops=K.house_percentile(lrp, "ops", float(mrow.ops), higher_is_better=False),
    rc_per_gm=K.house_percentile(lrp, "rc_per_gm", float(mrow.rc_per_gm), higher_is_better=False),
    k_minus_bb=K.house_percentile(lrp, "k_minus_bb", float(mrow.krate - mrow.bbrate)),
    bbrate=K.house_percentile(lrp, "bbrate", float(mrow.bbrate), higher_is_better=False),
    games=K.house_percentile(lrp, "games", float(mrow.games)),
    median_woba=float(lrp.woba.median()), best_woba=lrp.nsmallest(3, "woba")[["player_name", "game_year", "woba", "plate_apps"]].to_dict("records"))

# barrel -> wOBA context: house LHP pitcher-seasons (any role), >= 100 PA
lhp_lvl = ["pitcher", "game_year", "p_throws"]
lhp = ph[ph.p_throws == "L"]
bw = K.nresults(lhp_lvl, lhp)[lhp_lvl + ["plate_apps", "woba"]]
bw = bw.merge(K.barrel_rate(lhp_lvl, lhp)[lhp_lvl + ["barrel_rate"]], on=lhp_lvl, how="left")
xw = K.xwoba_pa(lhp_lvl, lhp); bw = bw.merge(xw[lhp_lvl + [c for c in xw.columns if c.startswith("xwoba")][:1]].rename(
    columns=lambda c: "xwoba" if c.startswith("xwoba") else c), on=lhp_lvl, how="left")
bw = bw.merge(hs[["pitcher", "game_year", "player_name", "role"]], on=["pitcher", "game_year"], how="left")
bw = bw[bw.plate_apps >= K.KP_MIN_PA].copy()
b1, b0 = np.polyfit(bw.barrel_rate, bw.woba, 1)
bw["woba_fit"] = b0 + b1 * bw.barrel_rate; bw["woba_resid"] = bw.woba - bw.woba_fit
bw.to_csv(P("house_lhp_barrel_woba.csv"), index=False)
mb = bw[(bw.pitcher == K.SUBJECT_ID) & (bw.game_year == K.SEASON)].iloc[0]
H["barrel_context"] = dict(n=int(len(bw)), slope=float(b1), intercept=float(b0), barrel_rate=float(mb.barrel_rate),
    woba=float(mb.woba), woba_fit=float(mb.woba_fit), resid=float(mb.woba_resid),
    resid_rank_low=int((bw.woba_resid < mb.woba_resid).sum() + 1), r=float(np.corrcoef(bw.barrel_rate, bw.woba)[0, 1]))

# ---------------- stuff & delivery ----------------
dt = K.delivery_table(pd.concat([ph[ph.pitcher != K.SUBJECT_ID], cf], ignore_index=True))
ds = K.delivery_distance(dt)
dt.to_csv(P("delivery_house_lhp.csv"), index=False); ds.to_csv(P("delivery_distance.csv"), index=False)
dpop = dt[dt.pitcher != K.SUBJECT_ID]
mdt = dt[(dt.pitcher == K.SUBJECT_ID) & (dt.game_year == K.SEASON)].iloc[0]
def pct_in(col, v):  # share of house LHP seasons strictly below v
    return dict(n=int(dpop[col].notna().sum()), pct_below=int(np.floor(100 * (dpop[col] < v).mean())))
H["delivery"] = dict(rel_x=float(mdt.rel_x), rel_z=float(mdt.rel_z), ext=float(mdt.ext), primary_fb=mdt.primary_fb,
    fb_velo=float(mdt.fb_velo), fb_hb_in=float(mdt.fb_hb_in), fb_ivb_in=float(mdt.fb_ivb_in),
    rel_x_pct=pct_in("rel_x", mdt.rel_x), rel_z_pct=pct_in("rel_z", mdt.rel_z), ext_pct=pct_in("ext", mdt.ext),
    arm_angle_2026=float(s26.arm_angle.mean()) if s26.arm_angle.notna().any() else None,
    arm_angle_cov=float(s26.arm_angle.notna().mean()),
    comps=ds.head(5)[["player_name", "game_year", "primary_fb", "distance"]].to_dict("records"),
    n_pop=int(len(dpop)), n_pitchers=int(dpop.pitcher.nunique()))
alv = ds[ds.player_name.str.contains("Alvarado", na=False)]
H["delivery"]["alvarado"] = None if alv.empty else dict(rank=int(alv.index[0] + 1), distance=float(alv.distance.iloc[0]),
                                                        season=int(alv.game_year.iloc[0]))
# arm angle (2025+ only): house LHP 2026 seasons
aa = ph[(ph.p_throws == "L") & (ph.game_year == K.SEASON)].groupby("pitcher").agg(n=("arm_angle", "count"), aa=("arm_angle", "mean"))
aa = aa[aa.n >= 100]
H["delivery"]["arm_angle_rank_high_2026"] = dict(n=int(len(aa)), rank=int((aa.aa > aa.loc[K.SUBJECT_ID, "aa"]).sum() + 1)) if K.SUBJECT_ID in aa.index else None
bs = K.bullet_slider(ph[ph.pitcher != K.SUBJECT_ID], extra=cf)
bs.to_csv(P("bullet_slider.csv"), index=False)
msl = bs[(bs.pitcher == K.SUBJECT_ID) & (bs.game_year == K.SEASON)].iloc[0]
others = bs[bs.pitcher != K.SUBJECT_ID]
H["bullet_slider"] = dict(hb_in=float(msl.hb_in), ivb_in=float(msl.ivb_in), spin_axis=float(msl.spin_axis), velo=float(msl.velo),
    bullet=bool(msl.bullet), n_pop=int(len(others)), n_bullet_others=int(others.bullet.sum()),
    bullet_others=others[others.bullet][["player_name", "game_year", "hb_in", "ivb_in", "sliders"]].to_dict("records"),
    hb_rank_smallest=int((others.hb_in.abs() < abs(msl.hb_in)).sum() + 1))
# extension of FS uniqueness
fs = ph[(ph.p_throws == "L") & (ph.pitch_type == "FS")].groupby(["pitcher", "game_year"]).size()
H["splitter_house_lhp_seasons_ge50"] = int((fs >= 50).sum())


# pitch shapes vs house LHP pitcher-seasons (min 50 of that pitch), for HP-06
shp = pd.concat([ph[ph.pitcher != K.SUBJECT_ID], cf], ignore_index=True)
shp = shp[(shp.p_throws == "L") & shp.pitch_type.isin(["FF", "SI", "SL"])].groupby(["pitcher", "game_year", "pitch_type"], as_index=False).agg(
    n=("pitch_type", "size"), hb_in=("pfx_x", lambda s: 12 * s.mean()), ivb_in=("pfx_z", lambda s: 12 * s.mean()), velo=("release_speed", "mean"))
shp = shp[shp.n >= 50]; shp.to_csv(P("shapes_house_lhp.csv"), index=False)
H["shapes"] = {}
for pt, g in shp.groupby("pitch_type"):
    m = g[(g.pitcher == K.SUBJECT_ID) & (g.game_year == K.SEASON)].iloc[0]; o = g[g.pitcher != K.SUBJECT_ID]
    H["shapes"][pt] = dict(n=int(len(o)), hb_in=float(m.hb_in), ivb_in=float(m.ivb_in), velo=float(m.velo),
        absHB_pct_below=int(100 * (o.hb_in.abs() < abs(m.hb_in)).mean()), ivb_pct_below=int(100 * (o.ivb_in < m.ivb_in).mean()),
        velo_pct_below=int(100 * (o.velo < m.velo).mean()), median_hb=float(o.hb_in.median()), median_ivb=float(o.ivb_in.median()))

# ---------------- QA-1 across house pitcher-seasons ----------------
qa = K.quick_ab_rate(["pitcher", "game_year", "p_throws"], ph).merge(hs[["pitcher", "game_year", "player_name", "role", "plate_apps"]],
                                                                    on=["pitcher", "game_year"], how="left")
qa = qa[qa.qa_pas >= K.KP_MIN_PA]
qa.to_csv(P("quick_ab_house.csv"), index=False)
mq = qa[(qa.pitcher == K.SUBJECT_ID) & (qa.game_year == K.SEASON)].iloc[0]
H["quick_ab"] = dict(rate=float(mq.quick_ab_rate), pas=int(mq.qa_pas), two_k=float(mq.qa_2k_rate), gb=float(mq.qa_gb_rate),
    house=K.house_percentile(qa, "quick_ab_rate", float(mq.quick_ab_rate)), house_median=float(qa.quick_ab_rate.median()),
    career=float(K.quick_ab_rate([], cf.assign(_=1)).quick_ab_rate.iloc[0]) if False else
           float(K.quick_ab_rate(["pitcher"], cf).quick_ab_rate.iloc[0]),
    career_pas=int(K.quick_ab_rate(["pitcher"], cf).qa_pas.iloc[0]))
# does it matter? wOBA by QA-1 outcome for the subject's 2026 PAs
H["lineage"] = LIN
json.dump(H, open(P("headlines.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("headlines written:", len(H), "blocks")
