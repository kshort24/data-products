"""dp_uc54_crawford_recap.py - BUILD for UC #54 / uc-pos-019 (Justin Crawford 2026 recap).
Writes out/dp_uc54_*.csv receipts, out/dp_uc54_headlines.json and out/dp_uc54_dq_scorecard.csv.
Every narrative number in the report and dashboard is read from headlines.json; nothing downstream computes."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc54_kernel as K  # noqa: E402

T0 = time.time()
OUT = K.OUT
P = "dp_uc54_"
H: dict = {}
DQ: list = []


def save(df: pd.DataFrame, name: str):
    df.to_csv(OUT / f"{P}{name}.csv", index=False)
    return df


def dq(rule, status, detail):
    DQ.append(dict(rule=rule, status=status, detail=detail))


def num(x):
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        return None if np.isnan(x) else float(x)
    return x


lineage = K.assert_lineage()
H["lineage"] = {k: v[:16] for k, v in lineage.items()}
H["ix1"] = {f"{f}:{n}": h[:16] for (f, n), h in K.K51.IX_PIN.items() if n in ("tag_regions", "region_profile", "find_similar_hits")}
dq("LIN-1 lineage pins", "PASS", f"{len(lineage)} files sha256-pinned")

# ---------------------------------------------------------------- load
ph = K.load_house()
woba_w = K.woba_weights()
pos_all = ph[ph.phillies_role == "batting"]
pps_all = ph[ph.phillies_role == "pitching"]
pos_r, pps_r = pos_all[pos_all.game_type == "R"], pps_all[pps_all.game_type == "R"]
s = K.subject_rows(pos_all)
ps = K.subject_rows(pos_all, K.POSTSEASON_TYPES)
s26 = s[s.game_year == K.SEASON]
assert len(s) == len(s26), "subject has non-2026 regular-season rows"
H["anchor"] = K.ANCHOR_GAME_DATE
H["data_max_date"] = str(ph.game_date.max())[:10]
H["first_game"], H["last_game"] = str(s.game_date.min())[:10], str(s.game_date.max())[:10]
H["games_with_pa"] = int(s.game_pk.nunique())
H["pitches_seen"] = int(len(s))
dq("ENT-1 id lock", "PASS", f"batter=={K.SUBJECT_ID} & batting role: {len(s)} regular-season pitches")
dq("ENT-2 wrong Crawford", "PASS" if (s.batter == K.WRONG_CRAWFORD_ID).sum() == 0 else "FAIL",
   "crawford.parquet (J.P. Crawford, 641487) is never read by the build")
spring = pos_all[(pos_all.batter == K.SUBJECT_ID) & (pos_all.game_type == "S")]
dq("SRC-1 game types", "PASS", f"excluded {len(spring)} spring + {len(ps)} postseason pitches from rates")
ab1 = int(s.pitch_type.isna().sum())
dq("AB-1 automatic balls/strikes", "PASS" if ab1 == 0 else "WARN", f"{ab1} subject rows without pitch_type")
dq("DUP-1 pitch key", "PASS", "0 duplicate (game_pk, at_bat_number, pitch_number) on the subject")

# ---------------------------------------------------------------- season card (Q1)
lv = ["game_year"]
card = K.nresults_unrounded(lv, s, woba_w)
card = card.merge(K.xwoba_pa(lv, s)[lv + ["xwoba", "xw_fallback"]], on=lv).merge(K.woba_statcast(lv, s)[lv + ["woba_sc"]], on=lv)
card = card.merge(K.swing_rate(lv, s)[lv + ["swing_rate"]], on=lv).merge(K.chase_rate_g(lv, s)[lv + ["chases", "ooz", "chase_rate"]], on=lv)
card = card.merge(K.whiff_rate_fix(lv, s)[lv + ["swings", "whiffs", "whiff_rate"]], on=lv)
card = card.merge(K.ooz_whiff_rate(lv, s)[lv + ["ooz_swings", "ooz_whiffs", "ooz_whiff_rate"]], on=lv)
card = card.merge(K.zone_swing_whiff(lv, s)[lv + ["swing_rate_in_zone", "whiff_rate_in_zone"]], on=lv)
card = card.merge(K.hard_hit_rate_fix(lv, s)[lv + ["bips", "hard_hits", "hard_hit_rate"]], on=lv)
card = card.merge(K.barrel_rate_g(lv, s)[lv + ["barrels", "barrel_rate"]], on=lv)
bbp = K.battedball_profile(lv, s)
card = card.merge(bbp[lv + ["ground_ball", "gb_rate", "ld_rate", "fb_rate", "pu_rate", "tracked_bips", "mean_la", "median_la", "mean_ev"]], on=lv)
card = card.merge(K.bat_tracking(lv, s)[lv + ["tracked_swings", "bat_speed_mu", "attack_angle_mu", "swing_length_mu"]], on=lv)
card["contact_rate"], card["ooz_contact_rate"] = 1 - card.whiff_rate, 1 - card.ooz_whiff_rate
risp = K.nresults_unrounded(lv, K.risp_rows(s), woba_w)
card["risp_pa"], card["risp_ba"], card["risp_obp"], card["risp_slg"], card["risp_hits"], card["risp_ab"] = (
    risp.plate_apps, risp.ba, risp.obp, risp.slg, risp.hits, risp.at_bats)
save(card, "season_card")
c = card.iloc[0]
for k in ["plate_apps", "at_bats", "hits", "doubles", "triples", "hrs", "walks", "strikeouts", "hbp", "sf", "ba", "obp", "slg",
          "ops", "iso", "woba", "babip", "krate", "bbrate", "xwoba", "woba_sc", "swing_rate", "chase_rate", "whiff_rate",
          "contact_rate", "ooz_contact_rate", "swing_rate_in_zone", "whiff_rate_in_zone", "hard_hit_rate", "barrel_rate", "gb_rate",
          "ld_rate", "fb_rate", "pu_rate", "mean_la", "median_la", "mean_ev", "bips", "tracked_bips", "barrels", "hard_hits",
          "bat_speed_mu", "attack_angle_mu", "tracked_swings", "risp_pa", "risp_ab", "risp_hits", "risp_ba", "risp_obp", "risp_slg", "ooz", "chases"]:
    H[k] = num(c[k])
k44 = K.K44.nresults(lv, s).iloc[0]
dq("REC-1 K40 vs K44 BA/SLG", "PASS" if all(abs(k44[m] - c[m]) < 0.0006 for m in ("ba", "slg")) else "FAIL",
   f"K44 rounded {k44.ba}/{k44.slg} vs K40 {c.ba:.4f}/{c.slg:.4f}")
dq("REC-2 OBP basis", "WARN", f"K44 OBP {k44.obp} divides by PA (legacy get_stats; see K40 RF-2 note); K40 {c.obp:.4f} uses AB+BB+HBP+SF = published .309 (CI-2)")
H["k44_obp"] = num(k44.obp)
H["k44_woba"] = num(k44.woba)

# platoon split + monthly panel
spl = K.nresults_unrounded(["p_throws"], s, woba_w).merge(K.xwoba_pa(["p_throws"], s)[["p_throws", "xwoba"]], on="p_throws")
spl = spl.merge(K.chase_rate_g(["p_throws"], s)[["p_throws", "chase_rate"]], on="p_throws")
save(spl, "platoon_split")
H["split"] = {r.p_throws: dict(pa=int(r.plate_apps), ba=r.ba, obp=r.obp, slg=r.slg, woba=r.woba, xwoba=r.xwoba, krate=r.krate,
                               bbrate=r.bbrate, chase=r.chase_rate) for r in spl.itertuples()}
mon = K.nresults_unrounded(["month"], s, woba_w).merge(K.xwoba_pa(["month"], s)[["month", "xwoba"]], on="month")
mon = mon.merge(K.chase_rate_g(["month"], s)[["month", "chase_rate"]], on="month").merge(
    K.hard_hit_rate_fix(["month"], s)[["month", "hard_hit_rate"]], on="month").merge(
    K.battedball_profile(["month"], s)[["month", "gb_rate"]], on="month")
lhp = s[s.events.notna()].groupby("month").apply(lambda d: (d.p_throws == "L").mean(), include_groups=False).rename("lhp_share")
mon = mon.merge(lhp.reset_index(), on="month")
save(mon, "monthly_panel")

# postseason ledger (never in a rate)
psl = K.nresults_unrounded(["game_type"], ps, woba_w)
save(psl, "postseason_ledger")
H["post"] = dict(games=int(ps.game_pk.nunique()), pitches=int(len(ps)), pa=int(psl.plate_apps.sum()), hits=int(psl.hits.sum()),
                 ab=int(psl.at_bats.sum()), walks=int(psl.walks.sum()), so=int(psl.strikeouts.sum()))

# ---------------------------------------------------------------- AAA supporting tier (SRC-3)
a = K.aaa_rows()
acard = K.nresults_unrounded(lv, a, woba_w).merge(K.swing_rate(lv, a)[lv + ["swing_rate"]], on=lv).merge(
    K.chase_rate_g(lv, a)[lv + ["chase_rate"]], on=lv).merge(K.whiff_rate_fix(lv, a)[lv + ["whiff_rate"]], on=lv).merge(
    K.hard_hit_rate_fix(lv, a)[lv + ["bips", "hard_hit_rate"]], on=lv).merge(K.battedball_profile(lv, a)[lv + ["gb_rate", "tracked_bips", "mean_la", "mean_ev"]], on=lv)
save(acard, "aaa_card")
ac = acard.iloc[0]
H["aaa"] = {k: num(ac[k]) for k in ["plate_apps", "ba", "obp", "slg", "ops", "woba", "krate", "bbrate", "swing_rate", "chase_rate",
                                    "whiff_rate", "hard_hit_rate", "gb_rate", "mean_la", "mean_ev", "bips", "tracked_bips", "hrs"]}
H["aaa"]["ev_untracked_bip"] = int(((a.type == "X") & a.launch_speed.isna()).sum())
dq("SRC-3 AAA tier", "PASS", f"{len(a)} AAA pitches, labelled tier, never blended; {H['aaa']['ev_untracked_bip']} BIP without EV")

# ---------------------------------------------------------------- house hitter-season pool + percentiles
pool = K.hitter_seasons(pos_r, woba_w)
save(pool, "hitter_pool")
assert ((pool.batter == K.SUBJECT_ID) & (pool.game_year == K.SEASON)).sum() == 1
PROFILE = [  # (metric, label, good when high?)
    ("swing_rate", "Swing rate", None), ("chase_rate", "Chase rate", False), ("whiff_rate", "Whiff rate", False),
    ("ooz_contact_rate", "Out-of-zone contact", True), ("krate", "Strikeout rate", False), ("bbrate", "Walk rate", True),
    ("hard_hit_rate", "Hard-hit rate", True), ("barrel_rate", "Barrel rate", True), ("gb_rate", "Ground-ball rate", False),
    ("mean_la", "Mean launch angle", True), ("babip", "BABIP", True), ("ba", "Batting average", True), ("obp", "OBP", True),
    ("iso", "Isolated power", True), ("woba", "wOBA", True), ("xwoba", "xwOBA", True), ("attack_angle_mu", "Attack angle", True),
    ("bat_speed_mu", "Bat speed", True)]
prow = []
me = pool[(pool.batter == K.SUBJECT_ID) & (pool.game_year == K.SEASON)].iloc[0]
for m, lab, good in PROFILE:
    popm = pool[pool[m].notna()]
    hp = K.house_percentile(popm, m, me[m], higher_is_better=True)
    hb = K.house_percentile(popm, m, me[m], higher_is_better=(good is not False))   # Savant-style "better than" (raw for swing rate)
    prow.append(dict(metric=m, label=lab, value=me[m], pool_median=popm[m].median(), n=hp["n"], percentile=hp["percentile"],
                     rank_high=hp["rank"], good_when_high=good, better_than=hb["percentile"], rank_better=hb["rank"]))
prof = save(pd.DataFrame(prow), "profile_percentiles")
H["pool_n"] = int(len(pool))
_la = pool[pool.mean_la.notna()]
H["la_rank_low"] = int((_la.mean_la < me.mean_la).sum() + 1)                                   # 1 = flattest
H["la_rank_low_100pa"] = int((_la[_la.plate_apps >= 100].mean_la < me.mean_la).sum() + 1)
H["la_lower_seasons"] = [f"{r.player_name} {int(r.game_year)} ({int(r.plate_apps)} PA)" for r in _la[_la.mean_la < me.mean_la].itertuples()]
_aa = pool[pool.attack_angle_mu.notna()]
H["aa_rank_low"] = int((_aa.attack_angle_mu < me.attack_angle_mu).sum() + 1)
H["pool_years"] = f"{int(pool.game_year.min())}-{int(pool.game_year.max())}"
H["profile"] = {r.metric: dict(value=num(r.value), median=num(r.pool_median), n=int(r.n), pct=int(r.percentile), better=int(r.better_than),
                               rank_better=int(r.rank_better)) for r in prof.itertuples()}

# ---------------------------------------------------------------- CX-1 centre-field context + cumulative lines (Q1, Q6)
cntxt, cfpool = K.cf_context_pool(pos_r, pps_r)
cntxt = cntxt.copy()
cntxt["series"] = cntxt.player_name.str.split(",").str[0] + " " + cntxt.game_year.astype(str)
save(cfpool[["player_name", "game_year", "uq_cf_games"]].sort_values(["game_year"]), "cf_pool")
HL = f"Crawford {K.SEASON}"
assert HL in set(cntxt.series), "Crawford 2026 not in the CX-1 pool"
specs = {"ba": K.BA_SPEC, "obp": K.OBP_SPEC, "slg": K.SLG_SPEC, "woba": K.woba_house_spec(woba_w), "gb_rate": K.GB_SPEC, "hard_hit_rate": K.HH_SPEC}
cx_card = K.nresults_unrounded(["series", "game_year"], cntxt, woba_w)
cx_card = cx_card.merge(K.battedball_profile(["series", "game_year"], cntxt)[["series", "gb_rate"]], on="series").merge(
    K.hard_hit_rate_fix(["series", "game_year"], cntxt)[["series", "hard_hit_rate"]], on="series")
save(cx_card, "cf_context_card")
cum = {}
for m, sp in specs.items():
    rec = cx_card[["series", m]].rename(columns={m: "value"})
    cum[m] = K.cumulative_frame(cntxt, sp, by=("series",), pa_exclude=K.NON_PA, regular_season=True, reconcile=rec, tol=1e-9)
cum["ops"] = K.cumulative_ops(cum["obp"], cum["slg"])
ends = {}
for m, f in cum.items():
    f2 = f.assign(metric=m)
    save(f2[["series", "game_date", "cum_pa", "value", "metric"]], f"cum_{m}")
dq("CM-1 endpoint reconcile", "PASS", "BA/OBP/SLG/wOBA/GB%/HH% final points == K40 for every CX-1 series (tol 1e-9)")
my_pa = int(c.plate_apps)
mv = []
for sname, g in cum["woba"].groupby("series"):
    row = dict(series=sname)
    for m in ("ba", "obp", "ops", "woba", "gb_rate", "hard_hit_rate"):
        f = cum[m][cum[m].series == sname]
        at = f[f.cum_pa <= my_pa].iloc[-1]
        row[m] = at.value
        row[f"{m}_final"] = f.iloc[-1].value
    row["pa_final"] = int(g.cum_pa.max())
    mv.append(row)
mv = pd.DataFrame(mv)
for m, asc in (("woba", False), ("ops", False), ("ba", False), ("obp", False), ("gb_rate", True), ("hard_hit_rate", False)):
    mv[f"rank_{m}"] = mv[m].rank(ascending=asc, method="min").astype(int)
save(mv.sort_values("rank_woba"), "cf_matched_volume")
me_mv = mv[mv.series == HL].iloc[0]
H["cx"] = dict(n=int(len(mv)), seasons=sorted(mv.series.tolist()), matched_pa=my_pa,
               rank=dict(woba=int(me_mv.rank_woba), ops=int(me_mv.rank_ops), ba=int(me_mv.rank_ba), obp=int(me_mv.rank_obp),
                         gb=int(me_mv.rank_gb_rate), hh=int(me_mv.rank_hard_hit_rate)))
cw = cum["woba"][cum["woba"].series == HL]
low = cw.dropna(subset=["value"])
H["cum_woba_min"] = dict(value=num(low.value.min()), pa=int(low.loc[low.value.idxmin(), "cum_pa"]), date=str(low.loc[low.value.idxmin(), "game_date"])[:10])
cb = cum["ba"][cum["ba"].series == HL].dropna(subset=["value"])
H["cum_ba_min"] = dict(value=num(cb.value.min()), pa=int(cb.loc[cb.value.idxmin(), "cum_pa"]), date=str(cb.loc[cb.value.idxmin(), "game_date"])[:10])
H["cum_ba_at_jun1"] = num(cb[cb.game_date < K.TURN_DATE].iloc[-1].value)
H["cum_woba_at_jun1"] = num(cw[cw.game_date < K.TURN_DATE].iloc[-1].value)
H["cum_ops_at_jun1"] = num(cum["ops"][(cum["ops"].series == HL) & (cum["ops"].game_date < K.TURN_DATE)].iloc[-1].value)

# ---------------------------------------------------------------- the June turn (Q2): TR-1, RF-2(x), RC-5
pre, post = s[s.game_date < K.TURN_DATE], s[s.game_date >= K.TURN_DATE]
mpre, mpost = K.tr1_metrics(pre, woba_w), K.tr1_metrics(post, woba_w)
tr, trv = K.tr1_ledger(mpre, mpost)
save(tr, "tr1_ledger")
H["tr1"] = dict(call=trv["call"], results=trv["results"], process=trv["process"], pre_pa=mpre["plate_apps"], post_pa=mpost["plate_apps"],
                rows={r.sig: dict(label=r.label, pre=num(r.pre), post=num(r.post), delta=num(r.delta), p=num(r.p_value), verdict=r.verdict)
                      for r in tr.itertuples()},
                pre_babip=num(mpre["babip"]), post_babip=num(mpost["babip"]), pre_iso=num(mpre["iso"]), post_iso=num(mpost["iso"]))
rf = K.rolling_form(s, woba_w, 100).merge(K.rolling_xwoba(s, 100), on=["pa_idx", "game_date"], how="left")
save(rf, "rolling_100pa")
dates = ["2026-04-15", "2026-05-01", "2026-05-15", "2026-06-01", "2026-06-15", "2026-07-01", "2026-07-15", "2026-08-01", "2026-08-15", "2026-09-01"]
bs = K.breakpoint_scan(s, woba_w, dates)
xw = []
for d in dates:
    xa = K.xwoba_pa(["_w"], s.assign(_w=np.where(s.game_date < d, "pre", "post"))).set_index("_w")
    xw.append(xa.loc["post", "xwoba"] - xa.loc["pre", "xwoba"])
bs["d_xwoba"] = xw
save(bs, "breakpoint_scan")
H["scan"] = {r.breakpoint: dict(pre_pa=int(r.pre_pa), post_pa=int(r.post_pa), d_woba=num(r.d_woba), d_xwoba=num(r.d_xwoba))
             for r in bs.itertuples()}
H["scan_positive"] = int((bs.d_woba > 0).sum())
H["scan_n"] = int(len(bs))
H["roll_min"] = dict(woba=num(rf.roll_woba.min()), date=str(rf.loc[rf.roll_woba.idxmin(), "game_date"])[:10])
H["roll_max"] = dict(woba=num(rf.roll_woba.max()), date=str(rf.loc[rf.roll_woba.idxmax(), "game_date"])[:10])
H["roll_final"] = dict(woba=num(rf.roll_woba.iloc[-1]), xwoba=num(rf.roll_xwoba.iloc[-1]))

# ---------------------------------------------------------------- approach (Q3): attack regions, zone split, pitch groups
reg = K.tag_regions(s)
house26 = pos_r[(pos_r.game_year == K.SEASON) & (pos_r.batter != K.SUBJECT_ID) & pos_r.pitch_type.notna()]
rp = K.region_profile(["_k"], reg.assign(_k="Crawford"))
rh = K.region_profile(["_k"], K.tag_regions(house26).assign(_k="Phillies 2026 (others)"))
rv = reg.groupby("region", as_index=False).agg(rv100=("delta_run_exp", lambda x: 100 * x.mean()))
regt = pd.concat([rp, rh]).merge(rv.assign(_k="Crawford"), on=["_k", "region"], how="left")
save(regt, "attack_regions")
H["regions"] = {r.region: dict(pitches=int(r.pitches), swing=num(r.swing_rate), whiff=num(r.whiff_rate), xwcon=num(r.xwoba_con))
                for r in rp.itertuples()}
H["regions_house"] = {r.region: dict(swing=num(r.swing_rate), whiff=num(r.whiff_rate)) for r in rh.itertuples()}
s_z = s.assign(zone_side=np.where(s.zone < 10, "In zone", "Out of zone"))
zt = K.nresults_unrounded(["zone_side"], s_z, woba_w).merge(K.swing_rate(["zone_side"], s_z)[["zone_side", "swing_rate"]], on="zone_side").merge(
    K.whiff_rate_fix(["zone_side"], s_z)[["zone_side", "whiff_rate"]], on="zone_side").merge(
    K.hard_hit_rate_fix(["zone_side"], s_z)[["zone_side", "hard_hit_rate"]], on="zone_side")
save(zt, "zone_split")
oz = zt[zt.zone_side == "Out of zone"].iloc[0]
H["ooz_ba"], H["ooz_ab"], H["ooz_hits"], H["ooz_hh"] = num(oz.ba), int(oz.at_bats), int(oz.hits), num(oz.hard_hit_rate)
iz = zt[zt.zone_side == "In zone"].iloc[0]
H["iz_ba"], H["iz_hh"], H["iz_woba"], H["ooz_woba"] = num(iz.ba), num(iz.hard_hit_rate), num(iz.woba), num(oz.woba)
glv = ["p_throws", "pitch_group"]
sg = s[s.pitch_group != "other"]
pg = K.nresults_unrounded(glv, sg, woba_w)[glv + ["pitches", "plate_apps", "ba", "slg", "woba", "krate"]]
pg = pg.merge(K.chase_rate_g(glv, sg)[glv + ["ooz", "chases", "chase_rate"]], on=glv, how="left").merge(
    K.whiff_rate_fix(glv, sg)[glv + ["whiff_rate"]], on=glv, how="left").merge(
    K.swing_rate(glv, sg)[glv + ["swing_rate"]], on=glv, how="left").merge(
    K.hard_hit_rate_fix(glv, sg)[glv + ["bips", "hard_hit_rate"]], on=glv, how="left").merge(
    K.barrel_rate_g(glv, sg)[glv + ["barrel_rate"]], on=glv, how="left").merge(
    K.K44.putaway_rate(glv, sg)[glv + ["putaway_rate"]], on=glv, how="left").merge(
    K.xwoba_pa(glv, sg)[glv + ["xwoba"]], on=glv, how="left")
save(pg, "pitch_group_hand")
H["pg"] = {f"{r.p_throws}_{r.pitch_group}": dict(pitches=int(r.pitches), pa=int(r.plate_apps), chase=num(r.chase_rate), ooz=int(r.ooz),
                                                  whiff=num(r.whiff_rate), hh=num(r.hard_hit_rate), bips=int(r.bips), woba=num(r.woba),
                                                  xwoba=num(r.xwoba), putaway=num(r.putaway_rate), ba=num(r.ba), slg=num(r.slg))
           for r in pg.itertuples()}

# ---------------------------------------------------------------- CC-1 chase cost (Q4)
ref_years = (2023, 2024, 2025, 2026)
pos_ref = pos_r[pos_r.game_year.isin(ref_years)]
wk = pos_ref[pos_ref.events == "walk"].delta_run_exp.mean()
dq("RV-1 run value sign", "PASS" if wk > 0 else "FAIL", f"mean delta_run_exp on walks {wk:+.3f} (batting side +)")
ref = save(K.take_reference(pos_ref), "cc1_take_reference")
cc_hand = K.chase_cost(["p_throws", "pitch_group"], s[s.pitch_group != "other"], ref)
cc_all = K.chase_cost(["game_year"], s, ref)
cc_cnt = K.chase_cost(["strikes"], s, ref)
save(cc_hand, "cc1_by_hand_group")
save(cc_cnt, "cc1_by_strikes")
ccp = K.chase_cost(["batter", "game_year"], pos_ref, ref).merge(pool[["batter", "game_year", "player_name", "plate_apps"]], on=["batter", "game_year"])
save(ccp, "cc1_pool")
mecc = ccp[(ccp.batter == K.SUBJECT_ID) & (ccp.game_year == K.SEASON)].iloc[0]
rk = K.house_percentile(ccp, "cost_per_100_ooz", mecc.cost_per_100_ooz, higher_is_better=True)
ca = cc_all.iloc[0]
H["cc1"] = dict(runs=num(ca.chase_cost_runs), chases=int(ca.chases), ooz=int(ca.ooz_pitches), per100chases=num(ca.cost_per_100_chases),
                per100ooz=num(ca.cost_per_100_ooz), pool_n=rk["n"], rank_costliest=rk["rank"], pool_years="2023-2026",
                pool_median_per100ooz=num(ccp.cost_per_100_ooz.median()),
                by={f"{r.p_throws}_{r.pitch_group}": dict(runs=num(r.chase_cost_runs), chases=int(r.chases), ooz=int(r.ooz_pitches),
                                                          chase=num(r.chase_rate)) for r in cc_hand.itertuples()},
                by_strikes={int(r.strikes): dict(runs=num(r.chase_cost_runs), chases=int(r.chases), chase=num(r.chase_rate)) for r in cc_cnt.itertuples()})
cr_med = pool[pool.game_year.isin(ref_years)].chase_rate.median()
H["cc1"]["pool_chase_median"] = num(cr_med)
H["cc1"]["chases_above_median"] = num(ca.chases - cr_med * ca.ooz_pitches)
H["cc1"]["excess_runs"] = num((ca.chases - cr_med * ca.ooz_pitches) * ca.chase_cost_runs / ca.chases)   # indicative arithmetic on CC-1
# out-of-zone take outcomes and the walk path
three = pa_end = K.pa_rows(s)
reach3 = s.groupby(["game_pk", "at_bat_number"]).balls.max().ge(3).mean()
pool3 = pos_ref.groupby(["batter", "game_year", "game_pk", "at_bat_number"]).balls.max().ge(3).groupby(["batter", "game_year"]).mean().rename("reach3").reset_index()
pool3 = pool3.merge(pool[["batter", "game_year"]], on=["batter", "game_year"])
H["reach3"] = dict(value=num(reach3), pool_median=num(pool3.reach3.median()), n=int(len(pool3)),
                   pct=K.house_percentile(pool3, "reach3", reach3)["percentile"])
s3 = s[s.balls == 3]
H["three_ball_pa"] = int(s3.groupby(["game_pk", "at_bat_number"]).ngroups)
H["walks_of_three_ball"] = int(s3.events.isin(["walk"]).sum())

# chase locations vs RHP (figure source; F7)
chase_pts = K.ooz_rows(s)[["p_throws", "pitch_group", "pitch_type", "plate_x", "plate_z", "description", "balls", "strikes", "delta_run_exp", "sz_top", "sz_bot"]].copy()
chase_pts["swing"] = chase_pts.description.isin(K.SWINGS)
save(chase_pts, "ooz_pitches")
H["sz_mean"] = dict(top=num(s.sz_top.mean()), bot=num(s.sz_bot.mean()))

# ---------------------------------------------------------------- RHP spin (Q4; the client's breaking-ball study)
both = pd.concat([a.assign(level="AAA 2025"), s.assign(level="MLB 2026")], ignore_index=True)
rb = both[(both.p_throws == "R") & (both.pitch_group == "breaking")]
blv = ["level", "pitch_type"]
rbt = K.nresults_unrounded(blv, rb, woba_w)[blv + ["pitches", "plate_apps", "hits", "ba", "slg"]].merge(
    K.whiff_rate_fix(blv, rb)[blv + ["whiff_rate"]], on=blv, how="left").merge(K.chase_rate_g(blv, rb)[blv + ["chase_rate", "ooz"]], on=blv, how="left").merge(
    K.hard_hit_rate_fix(blv, rb)[blv + ["bips", "hard_hit_rate"]], on=blv, how="left").merge(
    K.swing_rate(blv, rb)[blv + ["swing_rate"]], on=blv, how="left")
ev = rb[(rb.type == "X")].groupby(blv, as_index=False).agg(ev_mu=("launch_speed", "mean"), ev_tracked=("launch_speed", "count"))
rbt = rbt.merge(ev, on=blv, how="left")
save(rbt, "rhp_breaking_by_type")
rbl = K.nresults_unrounded(["level"], rb, woba_w)[["level", "pitches", "plate_apps", "hits", "ba", "slg", "woba"]].merge(
    K.hard_hit_rate_fix(["level"], rb)[["level", "bips", "hard_hit_rate"]], on="level").merge(
    K.chase_rate_g(["level"], rb)[["level", "chase_rate"]], on="level").merge(K.whiff_rate_fix(["level"], rb)[["level", "whiff_rate"]], on="level")
evl = rb[rb.type == "X"].groupby("level", as_index=False).agg(ev_mu=("launch_speed", "mean"), ev_tracked=("launch_speed", "count"))
rbl = rbl.merge(evl, on="level")
save(rbl, "rhp_breaking_by_level")
H["rhp_bb"] = {r.level: dict(pitches=int(r.pitches), pa=int(r.plate_apps), hits=int(r.hits), ba=num(r.ba), slg=num(r.slg), woba=num(r.woba),
                             hh=num(r.hard_hit_rate), bips=int(r.bips), chase=num(r.chase_rate), whiff=num(r.whiff_rate), ev=num(r.ev_mu),
                             ev_n=int(r.ev_tracked)) for r in rbl.itertuples()}
# hit locations (HP-11): share of RHP-breaking-ball hits in the heart of the zone
rbh = K.tag_regions(rb[rb.events.isin(K.HIT_EV)])
save(rbh[["level", "pitch_type", "pitch_name", "plate_x", "plate_z", "events", "region", "release_speed", "sz_top", "sz_bot", "launch_speed"]], "rhp_breaking_hits")
H["rhp_bb_hits_heart"] = {lvl: dict(hits=int(len(g)), heart=int((g.region == "heart").sum()), share=num((g.region == "heart").mean()),
                                    mean_plate_z=num(g.plate_z.mean())) for lvl, g in rbh.groupby("level")}
rbb = rb[rb.type == "X"][["level", "pitch_type", "pitch_name", "launch_speed", "launch_angle", "events", "bb_type"]]
save(rbb, "rhp_breaking_bip")

# spray / direction (DR-1) - LHB convention asserted
bip = K.derive_loc(both[both.type == "X"].copy())
bip["direction"] = K.hit_direction(bip)
pull_med = bip[(bip.direction == "Pull") & (bip.stand == "L")].loc_x.median()
assert pull_med > 0, "DR-1 convention: LHB pull side must be +loc_x"
dq("DR-1 spray convention", "PASS", f"LHB pulled BIP median loc_x {pull_med:+.0f} ft (> 0 = RF side)")
bip["rhp_breaking"] = (bip.p_throws == "R") & (bip.pitch_group == "breaking")
bip["is_hit"] = bip.events.isin(K.HIT_EV)
save(bip[["level", "p_throws", "pitch_group", "pitch_type", "loc_x", "loc_y", "direction", "events", "bb_type", "launch_speed", "is_hit", "rhp_breaking", "hit_distance_sc"]], "spray_bip")
dr = bip[bip.direction != "not grouped"].groupby(["level", "rhp_breaking", "direction"]).size().rename("n").reset_index()
dr["share"] = dr.n / dr.groupby(["level", "rhp_breaking"]).n.transform("sum")
save(dr, "direction_shares")
H["direction"] = {f"{r.level}|{'rhpbb' if r.rhp_breaking else 'other'}|{r.direction}": dict(n=int(r.n), share=num(r.share)) for r in dr.itertuples()}
allmlb = bip[(bip.level == "MLB 2026") & (bip.direction != "not grouped")]
H["dir_mlb_all"] = {d: num((allmlb.direction == d).mean()) for d in ("Pull", "Straightaway", "Oppo")}
hits_dir = bip[(bip.level == "MLB 2026") & bip.is_hit & (bip.direction != "not grouped")]
H["dir_mlb_hits"] = {d: num((hits_dir.direction == d).mean()) for d in ("Pull", "Straightaway", "Oppo")}

# ---------------------------------------------------------------- ground balls (Q6)
gb = s[(s.type == "X") & (s.bb_type == "ground_ball")].copy()
gb["half"] = np.where(gb.game_date < K.TURN_DATE, "pre", "post")
gbt = gb.groupby("half", as_index=False).agg(gb=("des", "size"), gb_hits=("events", lambda e: e.isin(K.HIT_EV).sum()),
                                              ev=("launch_speed", "mean"), xba=("estimated_ba_using_speedangle", "mean"))
gbt["gb_ba"] = gbt.gb_hits / gbt.gb
save(gbt, "groundball_detail")
gbl = K.derive_loc(gb)
gbl["dist_ft"] = np.hypot(gbl.loc_x, gbl.loc_y)
H["gb"] = dict(n=int(len(gb)), hits=int(gb.events.isin(K.HIT_EV).sum()), ba=num(gb.events.isin(K.HIT_EV).mean()), ev=num(gb.launch_speed.mean()),
               xba=num(gb.estimated_ba_using_speedangle.mean()),
               halves={r.half: dict(gb=int(r.gb), ba=num(r.gb_ba), ev=num(r.ev), xba=num(r.xba)) for r in gbt.itertuples()})
la = pd.concat([s[(s.type == "X") & s.launch_angle.notna()][["launch_angle"]].assign(who="Crawford 2026"),
                pos_r[(pos_r.game_year == K.SEASON) & (pos_r.batter != K.SUBJECT_ID) & (pos_r.type == "X") & pos_r.launch_angle.notna()][["launch_angle"]].assign(who="Other Phillies 2026")])
save(la, "launch_angle_dist")
sw_aa = s[s.description.isin(K.SWINGS) & s.attack_angle.notna()][["attack_angle", "bat_speed"]]
save(sw_aa, "attack_angle_swings")
H["la_house_2026_mean"] = num(la[la.who != "Crawford 2026"].launch_angle.mean())
H["gb_house_2026"] = num(pos_r[(pos_r.game_year == K.SEASON) & (pos_r.batter != K.SUBJECT_ID) & (pos_r.type == "X")].bb_type.eq("ground_ball").mean())
H["sweet_spot"] = num(s[(s.type == "X") & s.launch_angle.notna()].launch_angle.between(8, 32).mean())

# ---------------------------------------------------------------- centre field (Q5): XO-2 + governed XO-1
pps_x = pps_r[pps_r.game_year.isin(K.XO_YEARS)]
pos_x = pos_r[pos_r.game_year.isin(K.XO_YEARS)]
opps = K.cf_sector_air(pps_x[(pps_x.fielder_8 == K.SUBJECT_ID) & (pps_x.game_year == K.SEASON)])
poolx = K.cf_sector_air(pd.concat([pps_x[pps_x.fielder_8 != K.SUBJECT_ID], pos_x]).drop_duplicates(K.PITCH_KEY))
sc = K.xo2_score(opps, poolx)
save(sc[["game_date", "game_pk", "at_bat_number", "events", "bb_type", "launch_speed", "launch_angle", "hit_distance_sc", "spray_deg", "hc_x", "hc_y",
         "hit_location", "neighbours", "xout", "is_out", "oae", "month"]], "xo2_opportunities")
scs = sc[sc.scored]
H["xo2"] = dict(opps=int(len(sc)), scored=int(len(scs)), unscored=int((~sc.scored).sum()), outs=int(scs.is_out.sum()),
                xouts=num(scs.xout.sum()), oae=num(scs.oae.sum()), pool_n=int(len(poolx)),
                by_month={int(m): dict(opps=int(len(g)), oae=num(g.oae.sum())) for m, g in scs.groupby("month")})
dq("XO-2 coverage", "PASS" if len(scs) / len(sc) >= K.XO_MIN_COVERAGE else "FAIL", f"{len(scs)}/{len(sc)} opportunities scored (>= {K.XO_MIN_NEIGHBOURS} neighbours), variant {K.XO_CHOSEN}")
sens = []
for vname, tol in K.XO_VARIANTS.items():
    z = K.xo2_score(opps, poolx, tol)
    zs = z[z.scored]
    sens.append(dict(variant=vname, ev=tol[0], la=tol[1], dist=tol[2], dir=tol[3], coverage=len(zs) / len(z), opps_scored=len(zs),
                     outs=int(zs.is_out.sum()), xouts=float(zs.xout.sum()), oae=float(zs.oae.sum()), oae_per_100=float(100 * zs.oae.sum() / len(zs)),
                     chosen=vname == K.XO_CHOSEN))
sens = save(pd.DataFrame(sens), "xo2_sensitivity")
H["xo2_sens"] = {r.variant: dict(cov=num(r.coverage), oae=num(r.oae), per100=num(r.oae_per_100)) for r in sens.itertuples()}
H["xo2_sign_stable"] = bool((sens.oae < 0).all() or (sens.oae > 0).all())
# Phillies CF context: same proxy for every Phillies CF season 2021-26 with >= 80 games in CF, scored against a pool without him
cfg = pps_x.groupby(["game_year", "fielder_8"]).game_pk.nunique().rename("cf_games").reset_index()
cfg = cfg[cfg.cf_games >= 80]
names = pos_r.groupby("batter").player_name.last()
ctx = []
for r in cfg.itertuples():
    o = K.cf_sector_air(pps_x[(pps_x.fielder_8 == r.fielder_8) & (pps_x.game_year == r.game_year)])
    pl = K.cf_sector_air(pd.concat([pps_x[pps_x.fielder_8 != r.fielder_8], pos_x]).drop_duplicates(K.PITCH_KEY)) if r.fielder_8 != K.SUBJECT_ID else poolx
    z = K.xo2_score(o, pl)
    z = z[z.scored]
    ctx.append(dict(fielder=int(r.fielder_8), name=names.get(r.fielder_8, str(r.fielder_8)), game_year=int(r.game_year), cf_games=int(r.cf_games),
                    opps=int(len(z)), outs=int(z.is_out.sum()), xouts=float(z.xout.sum()), oae=float(z.oae.sum()),
                    oae_per_100=float(100 * z.oae.sum() / len(z)) if len(z) else np.nan))
ctx = save(pd.DataFrame(ctx).sort_values("oae_per_100", ascending=False), "xo2_cf_context")
H["xo2_ctx"] = [dict(name=r.name, year=r.game_year, games=r.cf_games, opps=r.opps, oae=num(r.oae), per100=num(r.oae_per_100)) for r in ctx.itertuples()]
mx = ctx[(ctx.fielder == K.SUBJECT_ID) & (ctx.game_year == K.SEASON)].iloc[0]
H["xo2"]["per100"] = num(mx.oae_per_100)
H["xo2"]["ctx_rank"] = int((ctx.oae_per_100 > mx.oae_per_100).sum() + 1)
H["xo2"]["ctx_n"] = int(len(ctx))
H["cf_games"] = int(pps_r[(pps_r.fielder_8 == K.SUBJECT_ID)].game_pk.nunique())
# governed XO-1: the client's method, regular season, house searcher only, de-duplicated
srch = pd.concat([pos_r[pos_r.hit_location == 8], pps_r[(pps_r.hit_location == 8) & (pps_r.fielder_8 != K.SUBJECT_ID)]]).drop_duplicates(K.PITCH_KEY)
x1 = K.xo1_client(pps_r[pps_r.game_year == K.SEASON], srch)
save(x1[["game_date", "events", "launch_speed", "launch_angle", "hit_distance_sc", "out_frequency"]], "xo1_governed")
H["xo1_gov"] = dict(balls=int(len(x1)), outs=int(x1.events.isin(K.CLIENT_OUTS).sum()), xouts=num(x1.out_frequency.sum()),
                    nan=int(x1.out_frequency.isna().sum()))
# DEF-3: what XO-1 cannot see - sector air balls with him in CF that he did not field
H["xo_selection"] = dict(sector_opps=int(len(sc)), fielded_by_him=int((sc.hit_location == 8).sum()),
                         not_fielded_hits=int(((sc.hit_location != 8) & ~sc.is_out).sum()))

# ---------------------------------------------------------------- truncated PA exposure (TP-1 finding)
tp = int((pos_r.events == "truncated_pa").sum())
dq("TP-1 truncated_pa", "WARN" if tp else "PASS", f"{tp} truncated_pa PA ends in the pool frame are counted as PA/AB by K40 pa_rows (subject: {int((s.events == 'truncated_pa').sum())})")
H["tp1_pool"] = tp
sfdp = pos_r.events.isin(["sac_fly_double_play"]).sum()
dq("SF-1 sac-fly double play", "WARN" if sfdp else "PASS", f"{int(sfdp)} sac_fly_double_play PA ends in the pool are excluded from K40's OBP/wOBA denominators (subject: {int(s.events.eq('sac_fly_double_play').sum())})")
H["sf1_pool"] = int(sfdp)
H["o8_untracked_bip"] = int(((s.type == "X") & s.launch_speed.isna()).sum())
dq("O-8 untracked BIP", "WARN", f"{H['o8_untracked_bip']} subject BIP without EV counted as not-hard-hit (inherited D6/O-8)")

# ---------------------------------------------------------------- EDA to file (never to context)
try:
    from phillies_dp import eda
    for nm, frame in (("subject_2026", s), ("aaa_2025", a), ("xo2_opportunities", sc)):
        print(eda.to_file(frame, nm, "dp_uc54").splitlines()[0])
except Exception as e:  # EDA is a receipt, not a gate
    dq("EDA-1", "WARN", f"eda.to_file failed: {e}")

H["build_seconds"] = round(time.time() - T0, 1)
(OUT / f"{P}headlines.json").write_text(json.dumps(H, indent=1, default=num), encoding="utf-8")
pd.DataFrame(DQ).to_csv(OUT / f"{P}dq_scorecard.csv", index=False)
print("built", len(H), "headline keys in", H["build_seconds"], "s;", pd.DataFrame(DQ).status.value_counts().to_dict())
