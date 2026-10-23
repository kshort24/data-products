"""dp_uc56_sosa_recap.py - BUILD for UC #56 / uc-pos-021 (Edmundo Sosa 2026 recap, "We Really Do Love Sosa").
Writes out/dp_uc56_*.csv receipts, out/dp_uc56_headlines.json and out/dp_uc56_dq_scorecard.csv; EDA to eda/dp_uc56/.
Every narrative number in the report and dashboard is read from headlines.json; nothing downstream computes."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc56_kernel as K  # noqa: E402
from phillies_dp import eda  # noqa: E402  (data-plane package; writes under root=EDA_ROOT)

T0 = time.time()
OUT, P = K.OUT, K.P
OUT.mkdir(exist_ok=True)
H: dict = {}
DQ: list = []


def save(df: pd.DataFrame, name: str) -> pd.DataFrame:
    df.to_csv(OUT / f"{P}{name}.csv", index=False)
    return df


def dq(rule, status, detail):
    DQ.append(dict(rule=rule, status=status, detail=detail))


def num(x):
    if x is pd.NA or x is pd.NaT:                 # J-2: nullable NA must serialise as null, not the string "<NA>"
        return None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        return None if np.isnan(x) else float(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def jdef(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    y = num(x)
    return y if y is not x else str(x)


def panel(level, d: pd.DataFrame, woba_w, bat=True) -> pd.DataFrame:
    """The house KPI panel + the client's batted-ball and out-of-zone asks, at any grain (inherited functions only)."""
    level = list(level)
    z = K.nresults_unrounded(level, d, woba_w)
    dp = d[d.pitch_type.notna()]
    parts = [(K.xwoba_pa(level, d), ["xwoba"]),
             (K.chase_rate_g(level, dp), ["chases", "ooz", "chase_rate"]),
             (K.whiff_rate_fix(level, d), ["swings", "whiffs", "whiff_rate"]),
             (K.swing_rate(level, d), ["swing_rate"]),
             (K.ooz_whiff_rate(level, dp), ["ooz_whiff_rate"]),
             (K.zone_swing_whiff(level, dp), ["swing_rate_in_zone", "whiff_rate_in_zone"]),
             (K.hard_hit_rate_fix(level, d), ["hard_hits", "hard_hit_rate"]),
             (K.barrel_rate_g(level, d), ["barrels", "barrel_rate"]),
             (K.battedball_profile(level, d), ["bips", "ld_rate", "fb_rate", "gb_rate", "pu_rate", "mean_la"]),
             (K.ev_profile(level, d), ["n_ev", "ev_mu", "ev50", "ev90", "ev_max"]),
             (K.pull_air(level, d), ["pull_airs", "pull_air_rate"]),
             (K.oz1(level, d), ["oz_pa", "oz_ab", "oz_hits", "oz_xhits", "oz_ba", "oz_xba", "oz_gap", "oz_call"])]
    if bat and "bat_speed" in d.columns:
        parts.append((K.bat_tracking(level, d), ["tracked_swings", "bat_speed_mu", "swing_length_mu"]))
    for r, cols in parts:
        if len(r):
            z = z.merge(r[level + [c for c in cols if c in r.columns and c not in z.columns]], on=level, how="left")
    z["ops"] = z.obp + z.slg
    z["contact_rate"] = 1 - z.whiff_rate
    z["ooz_contact_rate"] = 1 - z.ooz_whiff_rate
    z["zone_contact_rate"] = 1 - z.whiff_rate_in_zone
    return z


# ================================================================ A. lineage, load
lineage = K.assert_lineage()
H["lineage"] = {k: v[:16] for k, v in lineage.items()}
dq("LIN-1 lineage pins", "PASS", f"{len(lineage)} files sha256-pinned (K55 + K46 + barrel_rate.py + 14 through K55)")
ph = K.load_house()
woba_w = K.woba_weights()
pos_all, pps_all = ph[ph.phillies_role == "batting"], ph[ph.phillies_role == "pitching"]
pos_r, pps_r = pos_all[pos_all.game_type == "R"], pps_all[pps_all.game_type == "R"]
H["anchor"], H["data_max_date"] = K.ANCHOR_GAME_DATE, str(ph.game_date.max())[:10]
dq("ANC-1 pinned anchor", "PASS", f"house log max game_date {H['data_max_date']} <= {K.ANCHOR_GAME_DATE}")

# ================================================================ B. subject frames + sources
s_all = pos_all[pos_all.batter == K.SUBJECT_ID]
s = K.subject_rows(pos_all)
assert set(s.game_year.unique()) == set(K.PHI_SEASONS), "subject seasons drifted"
assert s.player_name.nunique() == 1 and (pos_all[pos_all.player_name == K.SUBJECT_NAME].batter == K.SUBJECT_ID).all()
assert (s.stand == "R").all(), "Sosa bats R in every Phillies row"
dq("ENT-1 id lock", "PASS", f"batter=={K.SUBJECT_ID} & batting role & R: {len(s)} pitches 2022-26; name maps to one id; stand R")
gt = K.pa_rows(s_all).groupby(["game_year", "game_type"]).size().rename("pa").reset_index()
save(gt, "game_type_ledger")
H["src4"] = {"spring_2026_pa": int(gt[(gt.game_year == 2026) & (gt.game_type == "S")].pa.sum()),
             "post_2026_pa": int(gt[(gt.game_year == 2026) & gt.game_type.isin(K.POSTSEASON_TYPES)].pa.sum()),
             "nonR_all_pa": int(gt[gt.game_type != "R"].pa.sum())}
dq("SRC-4 client frame game types", "WARN", f"client frame carries {H['src4']['nonR_all_pa']} non-regular PHI PA 2022-26 incl. "
   f"{H['src4']['spring_2026_pa']} spring + {H['src4']['post_2026_pa']} Wild Card PA in 2026; excluded from every governed rate")
stl = K.stl_rows()
stl_c = save(panel(["game_year"], stl[stl.game_year >= 2021], woba_w, bat=False), "stl_context")
H["stl"] = {int(r.game_year): dict(pa=int(r.plate_apps), ba=num(r.ba), obp=num(r.obp), slg=num(r.slg), woba=num(r.woba),
                                   xwoba=num(r.xwoba), chase=num(r.chase_rate), ooz_contact=num(r.ooz_contact_rate))
            for r in stl_c.itertuples()}
dq("SRC-5 two-team client frame", "WARN", f"client frame includes {K.STL_FILE} (STL {int(stl.game_year.min())}-{int(stl.game_year.max())}, "
   f"{len(stl)} R pitches, no bat tracking); shown as labelled context only, never pooled")
ps = K.subject_rows(pos_all, K.POSTSEASON_TYPES)
psl = save(K.nresults_unrounded(["game_year"], ps, woba_w), "postseason_ledger")
H["post"] = {int(r.game_year): dict(pa=int(r.plate_apps), ba=num(r.ba), ops=num(r.obp + r.slg)) for r in psl.itertuples()}
H["post_total_pa"] = int(psl.plate_apps.sum())
s26 = s[s.game_year == K.SEASON]
H["games_with_pa_2026"] = int(s26.game_pk.nunique())
H["first_game_2026"], H["last_game_2026"] = str(s26.game_date.min())[:10], str(s26.game_date.max())[:10]
H["pa_by_hand_2026"] = K.pa_rows(s26).groupby("p_throws").size().to_dict()
print(eda.to_file(s[["game_year", "pitch_type", "release_speed", "zone", "description", "events", "type", "bb_type",
                     "launch_speed", "launch_angle", "estimated_ba_using_speedangle", "estimated_woba_using_speedangle",
                     "bat_speed", "hc_x", "hc_y", "p_throws"]], "subject_regular_season", K.UC, root=K.EDA_ROOT))

# ================================================================ C. season card (Q1, Q3, Q4) + house percentiles
card = save(panel(["game_year"], s, woba_w), "season_panel")
pool = K.hitter_seasons(pos_r, woba_w)
lv = ["batter", "game_year"]
for r, cols in ((K.ev_profile(lv, pos_r), ["ev_mu", "ev50", "ev90", "ev_max"]),
                (K.pull_air(lv, pos_r), ["pull_air_rate"]),
                (K.oz1(lv, pos_r), ["oz_ba", "oz_xba", "oz_gap"])):
    pool = pool.merge(r[lv + cols], on=lv, how="left")
stand = pos_r.groupby(lv, as_index=False).agg(stand=("stand", lambda x: x.mode().iat[0]))
pool = save(pool.merge(stand, on=lv, how="left"), "hitter_pool")
print(eda.to_file(pool, "hitter_pool", K.UC, root=K.EDA_ROOT))
CARD = [("plate_apps", "PA", None), ("ba", "AVG", True), ("obp", "OBP", True), ("slg", "SLG", True), ("ops", "OPS", True),
        ("woba", "wOBA", True), ("xwoba", "xwOBA", True), ("bbrate", "BB%", True), ("krate", "K%", False),
        ("swing_rate", "Swing", None), ("contact_rate", "Contact", True), ("chase_rate", "Chase", False),
        ("whiff_rate", "Whiff", False), ("ooz_contact_rate", "OOZ contact", True), ("oz_ba", "OOZ BA", True),
        ("hard_hit_rate", "Hard-hit", True), ("barrel_rate", "Barrel/BIP", True), ("ev_mu", "Mean EV", True),
        ("ev50", "EV50 (median)", True), ("ev90", "EV90", True), ("ev_max", "Max EV", True),
        ("pull_air_rate", "Pull AIR%", True), ("bat_speed_mu", "Bat speed", True)]
pool["ops"] = pool.obp + pool.slg
rows = []
for r in card.itertuples():
    for m, lab, good in CARD:
        v = getattr(r, m, np.nan)
        if good is None or pd.isna(v) or m not in pool.columns:
            rows.append(dict(game_year=r.game_year, metric=m, label=lab, value=v, better_than=np.nan, n=np.nan))
            continue
        popm = pool[pool[m].notna()]
        hb = K.house_percentile(popm, m, v, higher_is_better=good)
        rows.append(dict(game_year=r.game_year, metric=m, label=lab, value=v, better_than=hb["percentile"], n=hb["n"]))
cardl = save(pd.DataFrame(rows), "season_card")
H["pool_n"], H["pool_years"] = int(len(pool)), f"{int(pool.game_year.min())}-{int(pool.game_year.max())}"
H["season"] = {int(r.game_year): {m: num(getattr(r, m, np.nan)) for m, _, _ in CARD} for r in card.itertuples()}
for r in card.itertuples():
    H["season"][int(r.game_year)].update(oz_xba=num(r.oz_xba), oz_gap=num(r.oz_gap), oz_call=r.oz_call, oz_pa=int(r.oz_pa),
                                         n_ev=int(r.n_ev), zone_contact_rate=num(r.zone_contact_rate),
                                         swing_rate_in_zone=num(r.swing_rate_in_zone), ld_rate=num(r.ld_rate),
                                         gb_rate=num(r.gb_rate), fb_rate=num(r.fb_rate), babip=num(r.babip), iso=num(r.iso),
                                         tracked_swings=num(getattr(r, "tracked_swings", np.nan)))
H["card_better"] = {int(y): {r.metric: num(r.better_than) for r in g.itertuples()} for y, g in cardl.groupby("game_year")}
c4 = card[card.game_year.isin((2023, 2024, 2025, 2026))].set_index("game_year")
H["own_rank_2026"] = {}
for m, _, good in CARD:
    if good is None or m == "bat_speed_mu":
        continue
    H["own_rank_2026"][m] = int(c4[m].rank(ascending=not good, method="min")[2026])   # 1 = best of 2023-26
base = s[s.game_year.isin(K.BASELINE)]
b_tot = panel(["_k"], base.assign(_k=1), woba_w).iloc[0]
H["baseline"] = {m: num(b_tot[m]) for m in ("plate_apps", "ba", "obp", "slg", "ops", "woba", "xwoba", "bbrate", "krate",
                                             "chase_rate", "ooz_contact_rate", "hard_hit_rate", "barrel_rate", "ev90", "oz_ba", "oz_xba")}

# ================================================================ D. cumulative wOBA and OPS (CM-1; Q1)
sR = s.assign(series=s.game_year.astype(str))
specs = {"woba": K.woba_house_spec(woba_w), "obp": K.OBP_SPEC, "slg": K.SLG_SPEC}
cum = {}
for m, sp in specs.items():
    rec = card[["game_year", m]].assign(series=card.game_year.astype(str)).rename(columns={m: "value"})[["series", "value"]]
    cum[m] = K.cumulative_frame(sR, sp, by=("series",), pa_exclude=K.NON_PA, regular_season=True, reconcile=rec, tol=1e-9)
cum["ops"] = K.cumulative_ops(cum["obp"], cum["slg"])
for m in ("woba", "ops"):
    save(cum[m].assign(metric=m)[["series", "game_date", "cum_pa", "value", "metric"]], f"cum_{m}")
dq("CM-1 endpoint reconcile", "PASS", "wOBA/OBP/SLG final points == K40 nresults for every season (tol 1e-9); OPS = OBP + SLG on the same rows")
chk = []
for m in ("woba", "ops"):
    c = cum[m]
    for pa in (50, 100, 150, 200, 250):
        at = c[(c.cum_pa == pa) & c.series.isin(["2023", "2024", "2025", "2026"])].set_index("series").value
        if len(at) == 4:
            chk.append(dict(metric=m, cum_pa=pa, v2026=at["2026"], rank_2026=int(at.rank(ascending=False)["2026"]),
                            best=at.idxmax(), worst=at.idxmin()))
chk = save(pd.DataFrame(chk), "cum_checkpoints")
H["cum_ck"] = {f"{r.metric}_{r.cum_pa}": dict(v=num(r.v2026), rank=int(r.rank_2026), best=r.best, worst=r.worst) for r in chk.itertuples()}
H["cum_2026_last_of_4_share"] = float((chk.rank_2026 == 4).mean())

# ================================================================ E. 2026 form: rolling, monthly, ER-1, TR-1 at the break (Q2)
rf = []
for yr, g in s[s.game_year >= 2023].groupby("game_year"):
    r = K.rolling_form(g, woba_w, 100).merge(K.rolling_xwoba(g, 100), on=["pa_idx", "game_date"], how="left")
    rf.append(r.assign(game_year=yr))
rf = save(pd.concat(rf, ignore_index=True), "rolling_100pa")
mon = save(panel(["month"], s26, woba_w), "monthly_2026")
H["month26"] = {int(r.month): dict(pa=int(r.plate_apps), ba=num(r.ba), ops=num(r.ops), woba=num(r.woba), xwoba=num(r.xwoba),
                                   chase=num(r.chase_rate), hh=num(r.hard_hit_rate), krate=num(r.krate)) for r in mon.itertuples()}
r26 = rf[rf.game_year == 2026]
H["roll26"] = dict(first=num(r26.roll_woba.iloc[0]), last=num(r26.roll_woba.iloc[-1]), min=num(r26.roll_woba.min()),
                   min_date=str(r26.loc[r26.roll_woba.idxmin(), "game_date"])[:10], max=num(r26.roll_woba.max()),
                   max_date=str(r26.loc[r26.roll_woba.idxmax(), "game_date"])[:10],
                   x_first=num(r26.roll_xwoba.iloc[0]), x_last=num(r26.roll_xwoba.iloc[-1]))
ER = {}
s_er = s[s.game_year >= 2023]
for basis in ("woba", "xwoba"):
    atoms = K.pa_atoms(s_er, woba_w, basis)
    career = atoms.num.sum() / atoms.den.sum()
    segs, tests = K.er1_segments(atoms, career)
    crit = K.er1_null_crit(atoms)
    power = K.er1_power(atoms, crit)
    save(segs.assign(basis=basis), f"er1_segments_{basis}")
    save(tests.assign(basis=basis), f"er1_tests_{basis}")
    save(power.assign(basis=basis), f"er1_power_{basis}")
    seg26 = segs[segs.game_year == 2026]
    ER[basis] = dict(career=num(career), n_seg_2026=int(len(seg26)),
                     segs_2026=[{k: jdef(v) for k, v in r._asdict().items() if k != "Index"} for r in seg26.itertuples()],
                     splits_by_year={int(y): int((segs.game_year == y).sum()) for y in (2023, 2024, 2025, 2026)},
                     power_2026={f"{d:.2f}": num(p) for d, p in power[power.game_year == 2026][["delta", "power"]].itertuples(index=False)}
                     if "game_year" in power.columns else {f"{d:.2f}": num(p) for d, p in power[["delta", "power"]].itertuples(index=False)})
H["er1"] = ER
asb = K.asb_first_game(pos_r, 2026)
H["asb_first_game_2026"] = str(asb)[:10]
pre, post = s26[s26.game_date < asb], s26[s26.game_date >= asb]
tpre, tpost = K.tr1_metrics(pre, woba_w), K.tr1_metrics(post, woba_w)
trl, trc = K.tr1_ledger(tpre, tpost)
save(trl, "tr1_asb_ledger")
H["tr1"] = dict(call=trc["call"], results=trc["results"], process=trc["process"], pre_pa=tpre["plate_apps"], post_pa=tpost["plate_apps"],
                rows={r.sig: dict(metric=r.metric, pre=num(r.pre), post=num(r.post), delta=num(r.delta), p=num(r.p_value), verdict=r.verdict)
                      for r in trl.itertuples()})
# platoon (bench-role question): by pitcher hand, 2026 and 2023-25
pl = K.nresults_unrounded(["game_year", "p_throws"], s[s.game_year >= 2023], woba_w).merge(
    K.xwoba_pa(["game_year", "p_throws"], s[s.game_year >= 2023])[["game_year", "p_throws", "xwoba"]], on=["game_year", "p_throws"])
save(pl, "platoon_by_season")
plb = K.nresults_unrounded(["p_throws"], s[s.game_year.isin(K.BASELINE)], woba_w).merge(
    K.xwoba_pa(["p_throws"], s[s.game_year.isin(K.BASELINE)])[["p_throws", "xwoba"]], on="p_throws")
H["platoon"] = {f"{r.p_throws}|{int(r.game_year)}": dict(pa=int(r.plate_apps), woba=num(r.woba), xwoba=num(r.xwoba), ops=num(r.obp + r.slg))
                for r in pl.itertuples()}
H["platoon"].update({f"{r.p_throws}|base": dict(pa=int(r.plate_apps), woba=num(r.woba), xwoba=num(r.xwoba), ops=num(r.obp + r.slg))
                     for r in plb.itertuples()})
rhb_pl = K.nresults_unrounded(["p_throws"], pos_r[(pos_r.stand == "R") & pos_r.game_year.isin(K.CLIENT_POOL_YEARS)], woba_w)
H["rhb_platoon_woba"] = {r.p_throws: num(r.woba) for r in rhb_pl.itertuples()}
# CI-2 media frame, reproduced as a receipt (NOT a test: chosen after the fact by the outlet)
games = sorted(s26.game_pk.unique(), key=lambda g: s26[s26.game_pk == g].game_date.iloc[0])
# the outlet counts team games; we count his last games with a PA - disclosed
last = s26[s26.game_pk.isin(games[-50:])]
lz = K.nresults_unrounded(["_k"], last.assign(_k=1), woba_w).iloc[0]
H["ci2_last50"] = dict(pa=int(lz.plate_apps), ba=num(lz.ba), obp=num(lz.obp), slg=num(lz.slg), ops=num(lz.obp + lz.slg),
                       first_date=str(last.game_date.min())[:10], games=50)

# ================================================================ F. batted ball indicators + decline flags (Q3)
dft, wa = K.wa1(card)
save(dft, "wa1_decline_flags")
H["df"] = {r.flag: dict(metric=r.metric, label=r.label, baseline=num(r.baseline), v2026=num(r.v2026), delta=num(r.delta),
                        bar=r.bar, flagged=bool(r.flagged), years=r.baseline_years) for r in dft.itertuples()}
H["wa1"] = {k: num(v) for k, v in wa.items()}
comps = pd.DataFrame(K.WA_COMPS, columns=["player", "team", "years", "total_m", "source"]).assign(aav_m=lambda d: d.total_m / d.years)
save(comps, "wa1_comps")
H["wa1"]["comps"] = [dict(player=r.player, team=r.team, years=int(r.years), total=float(r.total_m), aav=float(r.aav_m)) for r in comps.itertuples()]
H["wa1"]["salary"] = {str(k): v for k, v in K.WA_SALARY.items()}
bt_peer = K.bat_tracking(lv, pos_r[pos_r.game_year >= 2024])
bt_peer = bt_peer.merge(stand, on=lv, how="left")
bt26 = bt_peer[(bt_peer.game_year == 2026) & (bt_peer.tracked_swings >= 100)]
if len(bt26):
    hb = K.house_percentile(bt26, "bat_speed_mu", H["season"][2026]["bat_speed_mu"])
    H["bat_speed_pct_2026"] = dict(pct=hb["percentile"], rank=hb["rank"], n=hb["n"], median=num(bt26.bat_speed_mu.median()))
save(bt_peer, "bat_tracking_peers")

# ================================================================ G. approach: OZ-1, CC-1, client scatter (Q4, Q6)
rhb = pool[(pool.stand == "R") & pool.game_year.isin(K.CLIENT_POOL_YEARS)].copy()
save(rhb, "rhb_pool_2022_26")
H["rhb_n"] = int(len(rhb))
H["rhb_ooz_contact_median"] = num(rhb.ooz_contact_rate.median())
H["rhb_chase_median"] = num(rhb.chase_rate.median())
H["rhb_swing_median"] = num(rhb.swing_rate.median())
H["rhb_woba_median"] = num(rhb.woba.median())
r_s = float(np.corrcoef(rhb.swing_rate, rhb.woba)[0, 1])
wts = rhb.plate_apps.to_numpy(float)
def _wcorr(x, y, w):
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    return float(np.average((x - mx) * (y - my), weights=w) / np.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w)))
H["hp09_corr"] = dict(r=r_s, r_pa_weighted=_wcorr(rhb.swing_rate.to_numpy(), rhb.woba.to_numpy(), wts), n=int(len(rhb)))
sosa_rhb = rhb[rhb.batter == K.SUBJECT_ID].sort_values("game_year")
H["rhb_rank"] = {}
for r in sosa_rhb.itertuples():
    pop_y = rhb   # whole 2022-26 pool, as the client's scatter shows it
    H["rhb_rank"][int(r.game_year)] = dict(
        swing=K.house_percentile(pop_y, "swing_rate", r.swing_rate), woba=K.house_percentile(pop_y, "woba", r.woba),
        chase=K.house_percentile(pop_y, "chase_rate", r.chase_rate, higher_is_better=False),
        ooz_contact=K.house_percentile(pop_y, "ooz_contact_rate", r.ooz_contact_rate),
        contact=K.house_percentile(pop_y, "contact_rate", r.contact_rate))
oz_s = H["season"]
H["oz_sustainable"] = {y: bool((oz_s[y]["oz_call"] in ("EARNED", "RAN COLD")) and (oz_s[y]["ooz_contact_rate"] >= H["rhb_ooz_contact_median"]))
                       for y in (2023, 2024, 2025, 2026)}
ref = K.take_reference(pos_r[pos_r.delta_run_exp.notna()])
cc = K.chase_cost(["game_year"], s, ref)
cc_pool = K.chase_cost(lv, pos_r[pos_r.batter.isin(rhb.batter.unique()) & pos_r.game_year.isin(K.CLIENT_POOL_YEARS)], ref)
cc_pool = cc_pool.merge(rhb[lv], on=lv, how="inner")
save(cc, "cc1_chase_cost")
save(cc_pool, "cc1_rhb_pool")
H["cc1"] = {int(r.game_year): dict(chases=int(r.chases), runs=num(r.chase_cost_runs), per100=num(r.cost_per_100_chases),
                                   per100_ooz=num(r.cost_per_100_ooz)) for r in cc.itertuples()}
H["cc1_rhb_median_per100"] = num(cc_pool.cost_per_100_chases.median())
H["cc1_rhb_median_per100_ooz"] = num(cc_pool.cost_per_100_ooz.median())

# ================================================================ H. pitch groups and velocity (Q5)
sp = s[s.pitch_type.notna()].copy()
sp["pgroup"] = np.select([sp.pitch_type.isin(K.FB_TYPES) & (sp.release_speed > K.VELO_HI), sp.pitch_type.isin(K.FB_TYPES),
                          sp.pitch_group.eq("breaking"), sp.pitch_group.eq("offspeed")],
                         ["fastball 95+", "fastball <95", "breaking", "offspeed"], "other")
pgl = ["game_year", "pgroup"]
pg = K.nresults_unrounded(pgl, sp, woba_w)
for r, cols in ((K.xwoba_pa(pgl, sp), ["xwoba"]), (K.whiff_rate_fix(pgl, sp), ["swings", "whiffs", "whiff_rate"]),
                (K.chase_rate_g(pgl, sp), ["ooz", "chases", "chase_rate"]), (K.hard_hit_rate_fix(pgl, sp), ["bips", "hard_hits", "hard_hit_rate"])):
    pg = pg.merge(r[pgl + cols], on=pgl, how="left")
pg = save(pg, "pitch_group_by_season")
pg = pg[pg.pgroup != "other"]
H["pg"] = {f"{r.pgroup}|{int(r.game_year)}": dict(pitches=int(r.pitches), pa=num(r.plate_apps), woba=num(r.woba), xwoba=num(r.xwoba),
                                                  whiff=num(r.whiff_rate), swings=num(r.swings), chase=num(r.chase_rate),
                                                  hh=num(r.hard_hit_rate), bips=num(r.bips)) for r in pg.itertuples()}
# 2023-25 pooled baseline by group, for HP-06 / HP-07
spb = sp[sp.game_year.isin(K.BASELINE)].assign(_k=1)
pgb = K.nresults_unrounded(["pgroup"], spb, woba_w).merge(K.xwoba_pa(["pgroup"], spb)[["pgroup", "xwoba"]], on="pgroup").merge(
    K.whiff_rate_fix(["pgroup"], spb)[["pgroup", "swings", "whiffs", "whiff_rate"]], on="pgroup")
save(pgb, "pitch_group_baseline_2023_25")
H["pg_base"] = {r.pgroup: dict(pa=int(r.plate_apps), woba=num(r.woba), xwoba=num(r.xwoba), whiff=num(r.whiff_rate), swings=int(r.swings),
                               whiffs=int(r.whiffs)) for r in pgb.itertuples() if r.pgroup != "other"}
for grp in ("fastball 95+", "breaking"):
    b, c = H["pg_base"][grp], H["pg"][f"{grp}|2026"]
    _, p = K.two_prop_z(b["whiffs"], b["swings"], int(round(c["whiff"] * c["swings"])), int(c["swings"]))
    H["pg_base"][grp]["whiff_p_vs_2026"] = num(p)
# velocity seen by season (who threw him what)
velo = sp[sp.pitch_type.isin(K.FB_TYPES)].groupby("game_year", as_index=False).agg(fb_seen=("release_speed", "size"),
                                                                                      fb_velo_mu=("release_speed", "mean"),
                                                                                      share_95=("release_speed", lambda x: (x > K.VELO_HI).mean()))
save(velo, "fastball_velocity_seen")
H["velo_seen"] = {int(r.game_year): dict(n=int(r.fb_seen), mu=num(r.fb_velo_mu), share95=num(r.share_95)) for r in velo.itertuples()}

# ================================================================ I. tenure and versatility (Q7)
car = K.nresults_unrounded(["_k"], s.assign(_k=1), woba_w).iloc[0]
H["phi_career"] = dict(pa=int(car.plate_apps), ba=num(car.ba), obp=num(car.obp), slg=num(car.slg), ops=num(car.obp + car.slg),
                       woba=num(car.woba), hr=int((K.pa_rows(s).events == "home_run").sum()),
                       xbh=int(K.pa_rows(s).events.isin(["double", "triple", "home_run"]).sum()), games=int(s.game_pk.nunique()))
tl = K.nresults_unrounded(["batter"], pos_r[pos_r.game_year.isin(K.PHI_SEASONS)], woba_w)
tl = tl.merge(pos_r.groupby("batter", as_index=False).agg(player_name=("player_name", "last"),
                                                        stand=("stand", lambda x: x.mode().iat[0])), on="batter")
tl = tl[(tl.plate_apps >= 800)].copy()
tl["ops"] = tl.obp + tl.slg
tl = save(tl.sort_values("woba", ascending=False), "phi_2022_26_tenure_board")
H["tenure_board"] = dict(n=int(len(tl)), woba_rank=int((tl.woba > car.woba).sum() + 1),
                         rhb_n=int((tl.stand == "R").sum()), rhb_woba_rank=int(((tl.stand == "R") & (tl.woba > car.woba)).sum() + 1))
posg = []
for col, lab in K.POSITIONS.items():
    g = pps_r[pps_r[col] == K.SUBJECT_ID].groupby("game_year").game_pk.nunique().rename("games").reset_index().assign(position=lab)
    posg.append(g)
posg = save(pd.concat(posg, ignore_index=True), "games_by_position")
H["pos_games"] = {f"{r.position}|{int(r.game_year)}": int(r.games) for r in posg.itertuples()}
H["pos_count_2026"] = int(posg[(posg.game_year == 2026) & (posg.games > 0)].position.nunique())
H["pos_count_career"] = int(posg[posg.games > 0].position.nunique())
dq("POS-1 fielding games from the house log", "WARN", "games where fielder_k == id on the Phillies fielding side; counts appearances "
   "at a position (incl. late-inning moves), so a game can count at two positions; B-Ref carry-in (CI-4) shown beside it")

# ================================================================ J. DQ rules + headlines
ss = s[s.type == "X"]
dq("SEN-1 EV coverage on BIP", "PASS" if ss.launch_speed.notna().mean() > 0.99 else "WARN",
   f"{ss.launch_speed.notna().mean():.2%} of 2022-26 BIP carry launch_speed; untracked BIP leave EV-1 denominators")
xba_cov = pd.to_numeric(K.oz_pa(s).query("type == 'X'").estimated_ba_using_speedangle, errors="coerce").notna().mean()
dq("SEN-2 OZ-xBA coverage", "PASS" if xba_cov > 0.97 else "WARN", f"{xba_cov:.2%} of out-of-zone BIP carry estimated_ba (fallback: actual outcome)")
H["oz_xba_cov"] = float(xba_cov)
bt_cov = s[s.game_year >= 2024].query("description in @K.SWINGS").bat_speed.notna().mean()
dq("SEN-3 bat speed coverage 2024-26", "PASS" if bt_cov > 0.85 else "WARN", f"{bt_cov:.1%} of swings tracked (BT-1 floor 50 swings)")
dq("GL-1 EV50 definition", "WARN", "EV50 = median EV (client's definition); Statcast's public EV50 = mean of hardest 50% - disclosed, not substituted")
dq("SRC-6 2022 PHI sample", "WARN", f"2022 PHI = {H['season'][2022]['plate_apps']} PA; shown, never a baseline (baseline 2023-25 = {H['baseline']['plate_apps']} PA)")
dq("PAR-1 PA reconcile CI-1", "PASS" if H["season"][2026]["plate_apps"] == 250 else "FAIL",
   f"2026 PA {H['season'][2026]['plate_apps']} vs B-Ref 250; slash {K.f3(H['season'][2026]['ba'])}/{K.f3(H['season'][2026]['obp'])}/{K.f3(H['season'][2026]['slg'])} vs .247/.283/.429")
dq("TR-1 date fixed", "PASS", f"first post-break game {H['asb_first_game_2026']} from schedule gap (BID: never hand-keyed)")
dq("OZ-1 bars unchanged", "PASS" if (K.OZ_HOT, K.OZ_COLD) == (0.030, -0.030) else "FAIL", "+/-.030 as pre-registered")
dq("WA-1 bars unchanged", "PASS" if [b[3] for b in K.DF_BARS] == [1.0, 1.0, 0.040, 0.020, 0.020, 0.030] else "FAIL", "six DF bars as pre-registered")
dq("RATE-1 rates in [0,1]", "PASS" if all(0 <= H["season"][y][m] <= 1 for y in K.PHI_SEASONS for m in ("chase_rate", "contact_rate", "hard_hit_rate", "barrel_rate", "pull_air_rate") if H["season"][y][m] is not None) else "FAIL", "season-level rate KPIs bounded")
H["dq"] = {"pass": sum(d["status"] == "PASS" for d in DQ), "warn": sum(d["status"] == "WARN" for d in DQ), "fail": sum(d["status"] == "FAIL" for d in DQ)}
save(pd.DataFrame(DQ), "dq_scorecard")
H["build_seconds"] = round(time.time() - T0, 1)
(OUT / f"{P}headlines.json").write_text(json.dumps(H, indent=1, default=jdef), encoding="utf-8")
print("DQ", H["dq"], "seconds", H["build_seconds"])
