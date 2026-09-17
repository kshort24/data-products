"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #45  (uc-pps-031)
"Cristopher Sánchez — is he near the zone? A 2026 command diagnosis"
============================================================================
Layer-3 BUILD artifact, Phillies Pitching (pps) value stream.

Pattern lineage : UC3 -> UC8 (edge_rate) -> UC11 -> uc-pps-017 (PD-7)
                  -> uc-pps-019 (Sánchez ASG, entity lock) -> uc-pos-014 (PB-1)
                  -> uc-pps-030 (kernel layout) -> THIS.
Kernel          : dp_uc45_kernel.py (A verbatim, A2 governed edge_rate verbatim,
                  B access, D new: SZ-0..SZ-5, CL-1, PN-1, ZC-1).

DATA WINDOW
  phils_2021..2026.parquet, game_type == 'R', dedup game_pk+at_bat_number+
  pitch_number. Subject = pitcher 650911 (entity lock, asserted). 2021 and 2022
  merged as '2021-22'. Anchor = 2026-09-15 (last game in the cache).
  2026 first half = game_date <= 2026-07-13 (All-Star break).

CONTROLS (why this build is not a raw YoY table)
  O-18: 2026 strike-zone rails are a per-batter constant (ABS height-based
  zone). Every zone-geometry metric moved league-wide. Every 2025->2026 zone
  claim therefore ships with PN-1 (peer-netted) and ZC-1 (common-rail) twins,
  and every 2026 1H->2H claim ships with the league 1H->2H delta.

OUTPUTS -> $DP_OUT (default ./out): dp_uc45_*.csv, dp_uc45_payload.json
Run: python dp_uc45_sanchez_command.py   (exit 0 == every build assertion held)
============================================================================
"""
from __future__ import annotations
import json, os, sys, datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dp_uc45_kernel as K   # noqa: E402

OUT = Path(os.environ.get("DP_OUT", HERE / "out"))
OUT.mkdir(parents=True, exist_ok=True)
PN1_FLOOR = 200   # 12 arms clear 200 pitches in both 2025 and 2026; 6 clear 500
DEDUP = ["game_pk", "at_bat_number", "pitch_number"]
RECEIPTS: list[str] = []


def W(name: str, df: pd.DataFrame):
    p = OUT / f"dp_uc45_{name}.csv"
    df.to_csv(p, index=False)
    RECEIPTS.append(p.name)
    return df


def zp(x1, n1, x2, n2):
    z, p = K.two_prop_z(float(x1), float(n1), float(x2), float(n2))
    return round(z, 3) if z == z else np.nan, round(p, 4) if p == p else np.nan


# ---------------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------------
def load_all() -> pd.DataFrame:
    df = K.load_phils(years=K.SEASONS, role=None, regular_only=True)
    n0 = len(df)
    df = df.drop_duplicates(DEDUP).reset_index(drop=True)
    df.attrs["dedup_dropped"] = n0 - len(df)
    for c in ["plate_x", "plate_z", "sz_top", "sz_bot", "zone", "balls", "strikes",
              "pitch_number", "launch_speed", "launch_speed_angle",
              "estimated_woba_using_speedangle", "woba_value", "woba_denom"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
    df["season"] = K.season_label(df)
    df["half"] = K.half_label(df)
    df["month"] = pd.to_datetime(df.game_date).dt.month        # notebook convention
    df["region"] = K.shadow_region(df)
    df["sdist"] = K.signed_zone_distance(df)
    df["is_swing"] = df.description.isin(K.SWINGS)
    return df


# ---------------------------------------------------------------------------
# PANEL — kernel + SZ + CL-1 at any grain
# ---------------------------------------------------------------------------
def panel(level, d: pd.DataFrame) -> pd.DataFrame:
    level = list(level)
    nr = K.nresults(level, d)
    xw = d.groupby(level, as_index=False).agg(xwoba=("estimated_woba_using_speedangle", "mean"))
    xwc = d[d.type == "X"].groupby(level, as_index=False).agg(xwobacon=("estimated_woba_using_speedangle", "mean"))
    cr = K.chase_rate(level, d)[level + ["chases", "ooz", "chase_rate", "in_zone_rate"]]
    wr = K.whiff_rate(level, d)[level + ["swings", "whiffs", "whiff_rate"]]
    fp = K.fpsr(level, d)[level + ["First Pitch Strike Rate"]].rename(
        columns={"First Pitch Strike Rate": "fpsr"})
    er = K.edge_rate(level, d)[level + ["edge_pitches", "edge_rate"]]
    sz = K.shadow_profile(level, d)
    cl = K.count_leverage(level, d)[level + ["pitch_share_ahead", "pitch_share_even",
                                             "pitch_share_behind", "two_strike_pa_share",
                                             "three_ball_pa_share"]]
    hbp = d[d.events == "hit_by_pitch"].groupby(level, as_index=False).size().rename(columns={"size": "hbp"})
    out = nr
    for x in [xw, xwc, cr, wr, fp, er, sz, cl, hbp]:
        out = out.merge(x, on=level, how="left")
    out["hbp"] = out.hbp.fillna(0).astype(int)
    out["bb_hbp_rate"] = (out.walks + out.hbp) / out.plate_apps
    out["zone_swing_rate"] = (out.swings - out.chases) / (out.pitches - out.ooz)
    return out


def main():
    t0 = dt.datetime.now(dt.timezone.utc)
    df = load_all()
    assert df.duplicated(DEDUP).sum() == 0
    assert df.game_date.max() == K.ANCHOR_GAME_DATE, f"anchor drift: {df.game_date.max()}"

    cs = df[df.pitcher == K.SUBJECT_ID].copy()
    names = cs.player_name.unique().tolist()
    assert names == [K.SUBJECT_NAME], names                       # G1 entity lock
    assert set(cs.p_throws) == {"L"}
    # O-15 sign rule, asserted from data (never assumed)
    hbp = df[df.events == "hit_by_pitch"].groupby("stand").plate_x.mean()
    assert hbp["R"] < 0 < hbp["L"], "plate_x sign convention changed"
    assert cs[cs.pitch_name == "Sinker"].pfx_x.mean() > 0, "LHP arm-side sign"

    # all 2026 appearances are starts (first PHI pitcher of the game)
    pps = df[df.phillies_role == "pitching"]
    first = pps.sort_values(["game_pk", "inning", "at_bat_number", "pitch_number"]) \
               .groupby("game_pk").pitcher.first()
    g26 = cs[cs.game_year == 2026].game_pk.unique()
    starts26 = int((first.reindex(g26) == K.SUBJECT_ID).sum())
    assert starts26 == len(g26) == 31, (starts26, len(g26))

    # ---------------- 1. freshness manifest --------------------------------
    fm = []
    for y in K.SEASONS:
        d = df[df.game_year == y]; s = cs[cs.game_year == y]
        fm.append(dict(season=y, league_pitches=len(d), league_min_date=d.game_date.min(),
                       league_max_date=d.game_date.max(), subject_pitches=len(s),
                       subject_games=s.game_pk.nunique(),
                       subject_untracked=int((s.region == "untracked").sum()),
                       subject_null_zone=int(s.zone.isna().sum())))
    fm = pd.DataFrame(fm)
    fm["dedup_dropped_all_seasons"] = df.attrs["dedup_dropped"]
    fm["anchor_game_date"] = K.ANCHOR_GAME_DATE
    fm["asg_cut_2026"] = K.ASG_BREAK_2026
    fm["built_utc"] = t0.isoformat(timespec="seconds")
    W("freshness_manifest", fm)

    # ---------------- 2. parent reproduction (the DPO's notebook cell) -----
    # Verbatim shape of the client's cell: 2026 by month + 2023-2025 by season
    def nb_block(level, d):
        z = K.nresults(level, d).merge(K.chase_rate(level, d), on=level, how="left", suffixes=("", "_cr")) \
             .merge(K.whiff_rate(level, d), on=level, how="left", suffixes=("", "_wr")) \
             .merge(K.barrel_rate(level, d), on=level, how="left", suffixes=("", "_br")) \
             .merge(K.hard_hit_rate(level, d), on=level, how="left", suffixes=("", "_hh")) \
             .merge(K.fpsr(level, d), on=level, how="left", suffixes=("", "_fpsr"))
        z["pitches_per_pa"] = z.pitches / z.plate_apps
        return z
    kpis = ["pitches", "plate_apps", "bbrate", "in_zone_rate", "chase_rate", "barrel_rate",
            "hard_hit_rate", "First Pitch Strike Rate"]
    z = nb_block(["player_name", "month", "game_year"], cs[cs.game_year == 2026])
    ctx = cs[(cs.game_year > 2022) & (cs.game_year < 2026)]
    zc = nb_block(["player_name", "game_year"], ctx)
    zc["month"] = "All"
    zfig = pd.concat([zc, z])[["player_name", "game_year", "month"] + kpis + ["pitches_per_pa"]].round(3)
    W("notebook_reproduction", zfig)

    # ---------------- 3. panels -------------------------------------------
    season = W("season_panel", panel(["season"], cs))
    half = W("half_panel", panel(["game_year", "half"], cs[cs.game_year >= 2023]))
    c26 = cs[cs.game_year == 2026]
    month = W("month_panel_2026", panel(["month"], c26))
    start = panel(["game_date"], c26)
    start["opponent"] = c26.groupby("game_date").apply(
        lambda x: x.away_team.iloc[0] if x.home_team.iloc[0] == "PHI" else x.home_team.iloc[0]).values
    start["half"] = np.where(start.game_date <= K.ASG_BREAK_2026, "1H", "2H")
    W("start_log_2026", start)

    # ---------------- 4. league controls ----------------------------------
    lg = panel(["game_year", "half"], df)
    lg.insert(0, "population", "all pitchers in PHI games")
    lgl = panel(["game_year", "half"], df[df.p_throws == "L"])
    lgl.insert(0, "population", "LHP in PHI games")
    lgs = panel(["game_year"], df); lgs.insert(0, "population", "all pitchers in PHI games"); lgs["half"] = "season"
    lgls = panel(["game_year"], df[df.p_throws == "L"]); lgls.insert(0, "population", "LHP in PHI games"); lgls["half"] = "season"
    league = W("league_control", pd.concat([lgs, lg, lgls, lgl], ignore_index=True))

    # ---------------- 5. O-18 zone-rail audit -----------------------------
    aud = []
    for y in K.SEASONS:
        d = df[df.game_year == y].dropna(subset=["sz_top"])
        g = d.groupby("batter").agg(n=("sz_top", "size"), nu=("sz_top", "nunique"), sd=("sz_top", "std"))
        g = g[g.n >= 100]
        aud.append(dict(season=y, batters_100=len(g), share_single_valued=round((g.nu == 1).mean(), 4),
                        share_constant_1cm=round((g.sd.fillna(0) < 0.01).mean(), 4),
                        median_within_batter_sd_ft=round(float(g.sd.median()), 4),
                        league_mean_sz_top=round(float(d.sz_top.mean()), 4),
                        league_mean_sz_bot=round(float(d.sz_bot.mean()), 4)))
    aud = pd.DataFrame(aud)
    x = df[df.game_year.isin([2025, 2026])].dropna(subset=["sz_top"])
    gb = x.groupby(["batter", "game_year"]).agg(n=("sz_top", "size"), top=("sz_top", "median"),
                                                 bot=("sz_bot", "median")).unstack()
    gb = gb[(gb[("n", 2025)] >= 100) & (gb[("n", 2026)] >= 100)]
    dtop = gb[("top", 2026)] - gb[("top", 2025)]
    dbot = gb[("bot", 2026)] - gb[("bot", 2025)]
    aud["same_batter_n_2025_2026"] = len(gb)
    aud["same_batter_median_dtop_ft"] = round(float(dtop.median()), 4)
    aud["same_batter_median_dbot_ft"] = round(float(dbot.median()), 4)
    aud["same_batter_share_top_lower"] = round(float((dtop < 0).mean()), 4)
    W("zone_rail_audit", aud)
    assert aud.set_index("season").loc[2026, "share_constant_1cm"] > 0.95
    assert aud.set_index("season").loc[2025, "share_constant_1cm"] < 0.1

    # ---------------- 6. PN-1 peer-netted deltas --------------------------
    def m_kernel_zone(level, d):  return K.chase_rate(level, d)
    def m_bb(level, d):           return K.nresults(level, d)
    metrics = [(K.chase_rate, "in_zone_rate"), (K.chase_rate, "chase_rate"),
               (K.shadow_profile, "shadow_zone_rate"), (K.shadow_profile, "shadow_miss_rate"),
               (K.shadow_profile, "beyond_shadow_chase_rate"), (K.shadow_profile, "edge_out_chase_rate"),
               (K.edge_rate, "edge_rate"), (K.shadow_profile, "geo_zone_rate"),
               (K.nresults, "bbrate"), (K.count_leverage, "pitch_share_ahead"),
               (K.fpsr, "First Pitch Strike Rate")]
    heads, cohorts = [], []
    rails = K.abs_rails(df[df.game_year == 2026])
    pit_names = df[df.phillies_role == "pitching"].drop_duplicates("pitcher").set_index("pitcher").player_name
    geo_metrics = {"shadow_zone_rate", "shadow_miss_rate", "beyond_shadow_chase_rate",
                   "edge_out_chase_rate", "geo_zone_rate"}
    railed = K.common_rail_rescore(df[df.game_year.isin([2025, 2026]) & df.sz_top.notna()], rails)
    for basis, frame, pairs in [("native_rails", df, [(2024, 2025), (2025, 2026)]),
                                ("2026_abs_rails", railed, [(2025, 2026)])]:
        for y0, y1 in pairs:
            for fn, col in metrics:
                if basis != "native_rails" and col not in geo_metrics:
                    continue
                p, h = K.peer_delta_pitcher(frame, K.SUBJECT_ID, fn, col, y0, y1, min_pitches=PN1_FLOOR)
                h["basis"] = basis
                heads.append(h)
                p = p.rename(columns={f"val_{y0}": "val_y0", f"val_{y1}": "val_y1"})
                p["metric"], p["y0"], p["y1"], p["basis"] = col, y0, y1, basis
                p["pitcher_label"] = p.pitcher.map(pit_names).fillna("opponent arm (name not in log, O-10)")
                cohorts.append(p)
    pn = pd.DataFrame(heads)
    for c in ["subject_2024", "subject_2025", "subject_2026"]:
        if c not in pn.columns:
            pn[c] = np.nan
    W("peer_delta", pn.round(4))
    W("peer_cohort", pd.concat(cohorts, ignore_index=True).round(4))

    # ---------------- 7. ZC-1 common-rail re-score -------------------------
    zc_rows = []
    for y in [2024, 2025, 2026]:
        s = cs[(cs.game_year == y) & cs.sz_top.notna()]
        r = K.common_rail_rescore(s, rails)
        nat = K.shadow_profile(["game_year"], r.assign(sz_top=r.sz_top_native, sz_bot=r.sz_bot_native))
        com = K.shadow_profile(["game_year"], r)
        for lab, t in [("native_rails", nat), ("2026_abs_rails", com)]:
            row = t.iloc[0].to_dict(); row.update(rails_basis=lab, subject_located=len(s),
                                                  covered=len(r), coverage=round(len(r) / len(s), 4))
            zc_rows.append(row)
    # league twin (all pitchers, covered batters) for netting the common-rail view
    for y in [2025, 2026]:
        s = df[(df.game_year == y) & df.sz_top.notna()]
        r = K.common_rail_rescore(s, rails)
        com = K.shadow_profile(["game_year"], r).iloc[0].to_dict()
        com.update(rails_basis="2026_abs_rails", subject_located=np.nan, covered=len(r),
                   coverage=round(len(r) / len(s), 4), population="league")
        zc_rows.append(com)
    zc = pd.DataFrame(zc_rows)
    zc["population"] = zc.get("population", pd.Series(dtype=object)).fillna("Sánchez")
    W("common_rail", zc.round(4))
    # decomposition of the native 2025->2026 delta (covered batters)
    SUB = zc[zc.population == "Sánchez"].set_index(["game_year", "rails_basis"])
    LEA = zc[zc.population == "league"].set_index("game_year")
    dec = []
    for m in ["shadow_miss_rate", "geo_zone_rate", "beyond_shadow_chase_rate", "edge_rate_twin"]:
        n25, r25 = SUB.loc[(2025, "native_rails"), m], SUB.loc[(2025, "2026_abs_rails"), m]
        v26 = SUB.loc[(2026, "2026_abs_rails"), m]
        lcr = LEA.loc[2026, m] - LEA.loc[2025, m]
        dec.append(dict(metric=m, subject_2025_native=n25, subject_2025_on_2026_rails=r25, subject_2026=v26,
                        native_delta=v26 - n25, rail_effect=r25 - n25, common_rail_delta=v26 - r25,
                        league_common_rail_delta=lcr, subject_specific=(v26 - r25) - lcr,
                        subject_specific_share=((v26 - r25) - lcr) / (v26 - n25) if abs(v26 - n25) > 1e-9 else np.nan))
    dec = pd.DataFrame(dec)
    assert (dec.rail_effect + dec.common_rail_delta - dec.native_delta).abs().max() < 1e-9
    W("rail_decomposition", dec.round(4))

    # ---------------- 8. splits -------------------------------------------
    st = panel(["season", "stand"], cs); W("by_stand", st)
    sth = panel(["game_year", "half", "stand"], cs[cs.game_year >= 2025]); W("by_stand_half", sth)
    main_p = cs[cs.pitch_name.isin(["Sinker", "Changeup", "Slider"])]
    W("by_pitch", panel(["season", "pitch_name"], main_p))
    W("by_pitch_half", panel(["game_year", "half", "pitch_name"], main_p[main_p.game_year >= 2025]))
    W("by_pitch_stand_2026", panel(["half", "stand", "pitch_name"], main_p[main_p.game_year == 2026]))
    md = K.shadow_miss_direction(["season"], cs)
    mdh = K.shadow_miss_direction(["game_year", "half"], cs[cs.game_year >= 2025])
    mdh["season"] = mdh.game_year.astype(str) + " " + mdh.half
    W("miss_direction", pd.concat([md, mdh[md.columns]], ignore_index=True))
    # count-state grain: where did the chase go?
    cb = cs[cs.game_year >= 2025].copy()
    cb["count_state"] = np.select([(cb.balls == 0) & (cb.strikes == 0), cb.balls < cb.strikes,
                                   cb.balls == cb.strikes], ["0-0", "ahead", "even"], "behind")
    W("count_state", panel(["game_year", "half", "count_state"], cb))
    lcb = df[df.game_year == 2026].copy()
    lcb["count_state"] = np.select([(lcb.balls == 0) & (lcb.strikes == 0), lcb.balls < lcb.strikes,
                                    lcb.balls == lcb.strikes], ["0-0", "ahead", "even"], "behind")
    W("count_state_league_2026", K.shadow_profile(["half", "count_state"], lcb))

    # ---------------- 9. start distribution (every starter in the log) ------
    first_all = df.sort_values(["game_pk", "inning_topbot", "inning", "at_bat_number", "pitch_number"])
    sp = first_all.groupby(["game_pk", "inning_topbot"]).pitcher.first().reset_index()
    sdl = []
    for y in [2025, 2026]:
        dy = df[df.game_year == y].merge(sp, on=["game_pk", "inning_topbot", "pitcher"])
        t = K.shadow_profile(["game_year", "game_pk", "pitcher", "half"], dy)
        sdl.append(t[t.located_pitches >= 50])
    sd = pd.concat(sdl, ignore_index=True)
    sd["is_subject"] = sd.pitcher == K.SUBJECT_ID
    W("start_distribution", sd)
    assert int(sd[(sd.game_year == 2026)].is_subject.sum()) == 31
    sdm = sd.groupby(["game_year", "half", "is_subject"]).agg(
        starts=("game_pk", "size"), median_shadow_miss=("shadow_miss_rate", "median"),
        median_beyond_chase=("beyond_shadow_chase_rate", "median"),
        pooled_shadow_miss=("n_beyond", "sum"), located=("located_pitches", "sum")).reset_index()
    sdm["pooled_shadow_miss"] = sdm.pooled_shadow_miss / sdm.located
    W("start_distribution_summary", sdm.round(4))

    # ---------------- 10. geometry crosswalk ------------------------------
    loc = cs[cs.region != "untracked"].copy()
    rect_band = (loc.plate_x.abs() <= K.PLATE_HALF + K.BALL_FT) & \
                (loc.plate_z >= loc.sz_bot - K.BALL_FT) & (loc.plate_z <= loc.sz_top + K.BALL_FT)
    sz_in = loc.region != "beyond"
    geo_in = loc.sdist <= 0
    kz_in = loc.zone <= 9
    er_tw = K.shadow_profile(["season"], cs)[["season", "edge_rate_twin"]] \
        .merge(K.edge_rate(["season"], cs)[["season", "edge_rate"]], on="season")
    xw = pd.DataFrame([
        dict(check="SZ shadow vs OZ rectangular band (corners)", pitches=len(loc),
             disagree=int((sz_in != rect_band).sum()), disagree_share=round(float((sz_in != rect_band).mean()), 4)),
        dict(check="geometric zone vs Statcast zone attribute", pitches=len(loc),
             disagree=int((geo_in != kz_in).sum()), disagree_share=round(float((geo_in != kz_in).mean()), 4)),
        dict(check="edge_rate_twin == governed edge_rate (max abs diff, by season)", pitches=len(loc),
             disagree=int(((er_tw.edge_rate_twin - er_tw.edge_rate).abs() > 0.0006).sum()),
             disagree_share=round(float((er_tw.edge_rate_twin - er_tw.edge_rate).abs().max()), 5)),
        dict(check="Attack Zone (uc-pps-022) 0.33 ft shadow vs SZ 0.245 ft edge_out", pitches=len(loc),
             disagree=int(((loc.sdist > 0) & (loc.sdist <= 0.33) & (loc.sdist > K.BALL_FT)).sum()),
             disagree_share=round(float(((loc.sdist > K.BALL_FT) & (loc.sdist <= 0.33)).mean()), 4)),
    ])
    W("geometry_crosswalk", xw)
    assert (er_tw.edge_rate_twin - er_tw.edge_rate).abs().max() < 0.0006   # twin == governed

    # ---------------- 11. premise tests -----------------------------------
    S = season.set_index("season"); H = half.set_index(["game_year", "half"])
    L = league.set_index(["population", "game_year", "half"])
    PN = pn[(pn.y1 == 2026) & (pn.basis == "native_rails")].set_index("metric")
    ZC = zc[zc.population == "Sánchez"].set_index(["game_year", "rails_basis"])
    ZL = zc[zc.population == "league"].set_index("game_year")

    def season_test(pid, claim, col, num, den, better):
        a, b = S.loc["2025"], S.loc["2026"]
        z_, p_ = zp(b[num], b[den], a[num], a[den])
        return dict(premise=pid, claim=claim, metric=col, window="2025 -> 2026 season",
                    v_before=round(a[col], 4), v_after=round(b[col], 4), n_before=int(a[den]),
                    n_after=int(b[den]), delta=round(b[col] - a[col], 4), z=z_, p=p_)

    def half_test(pid, claim, col, num, den):
        a, b = H.loc[(2026, "1H")], H.loc[(2026, "2H")]
        z_, p_ = zp(b[num], b[den], a[num], a[den])
        la = L.loc[("all pitchers in PHI games", 2026, "1H"), col]
        lb = L.loc[("all pitchers in PHI games", 2026, "2H"), col]
        return dict(premise=pid, claim=claim, metric=col, window="2026 1H -> 2H",
                    v_before=round(a[col], 4), v_after=round(b[col], 4), n_before=int(a[den]),
                    n_after=int(b[den]), delta=round(b[col] - a[col], 4), z=z_, p=p_,
                    league_delta=round(lb - la, 4), netted_delta=round((b[col] - a[col]) - (lb - la), 4))

    S["ahead_n"] = S.pitch_share_ahead * S.pitches
    H["ahead_n"] = H.pitch_share_ahead * H.pitches
    S["iz_n"] = S.pitches - S.ooz; H["iz_n"] = H.pitches - H.ooz
    S["sz_n"] = S.shadow_zone_rate * S.located_pitches; H["sz_n"] = H.shadow_zone_rate * H.located_pitches
    S["woba_num"] = S.woba * S.plate_apps

    rows = [
        season_test("P1", "walk rate is up", "bbrate", "walks", "plate_apps", "lower"),
        half_test("P1", "walk rate is up", "bbrate", "walks", "plate_apps"),
        season_test("P2", "in the zone less", "in_zone_rate", "iz_n", "pitches", "higher"),
        half_test("P2", "in the zone less", "in_zone_rate", "iz_n", "pitches"),
        season_test("P3", "getting less chase", "chase_rate", "chases", "ooz", "higher"),
        half_test("P3", "getting less chase", "chase_rate", "chases", "ooz"),
        season_test("P4", "ahead in the count less", "pitch_share_ahead", "ahead_n", "pitches", "higher"),
        half_test("P4", "ahead in the count less", "pitch_share_ahead", "ahead_n", "pitches"),
        season_test("K2", "edge rate (governed) — around the edge as much?", "edge_rate", "edge_pitches", "located_pitches", "n/a"),
        half_test("K2", "edge rate (governed) — around the edge as much?", "edge_rate", "edge_pitches", "located_pitches"),
        season_test("K1", "missing the shadow completely more", "shadow_miss_rate", "n_beyond", "located_pitches", "lower"),
        half_test("K1", "missing the shadow completely more", "shadow_miss_rate", "n_beyond", "located_pitches"),
        season_test("E1", "less chase when outside the shadow", "beyond_shadow_chase_rate", "swings_beyond", "n_beyond", "higher"),
        half_test("E1", "less chase when outside the shadow", "beyond_shadow_chase_rate", "swings_beyond", "n_beyond"),
    ]
    pt = pd.DataFrame(rows)
    # attach season-level controls
    lg25 = L.loc[("all pitchers in PHI games", 2025, "season")]
    lg26 = L.loc[("all pitchers in PHI games", 2026, "season")]
    for i, r in pt.iterrows():
        if r.window.startswith("2025"):
            pt.loc[i, "league_delta"] = round(lg26[r.metric] - lg25[r.metric], 4)
            pt.loc[i, "netted_delta"] = round(r.delta - (lg26[r.metric] - lg25[r.metric]), 4)
            if r.metric in PN.index:
                pt.loc[i, "pn1_peer_median_delta"] = round(PN.loc[r.metric, "peer_median_delta"], 4)
                pt.loc[i, "pn1_netted_delta"] = round(PN.loc[r.metric, "peer_netted_delta"], 4)
                pt.loc[i, "pn1_cohort_n"] = int(PN.loc[r.metric, "cohort_n"])
                pt.loc[i, "pn1_rank_most_negative"] = int(PN.loc[r.metric, "subject_rank_most_negative"])
    DEC = dec.set_index("metric")
    PNR = pn[(pn.y1 == 2026) & (pn.basis == "2026_abs_rails")].set_index("metric")
    geo_map = {"shadow_miss_rate": "shadow_miss_rate", "beyond_shadow_chase_rate": "beyond_shadow_chase_rate",
               "in_zone_rate": "geo_zone_rate", "edge_rate": "edge_rate_twin"}
    for m, gm in geo_map.items():
        i = pt[(pt.metric == m) & pt.window.str.startswith("2025")].index[0]
        pt.loc[i, "zc1_metric"] = gm
        pt.loc[i, "zc1_native_delta"] = round(DEC.loc[gm, "native_delta"], 4)
        pt.loc[i, "zc1_rail_effect"] = round(DEC.loc[gm, "rail_effect"], 4)
        pt.loc[i, "zc1_league_cr_delta"] = round(DEC.loc[gm, "league_common_rail_delta"], 4)
        pt.loc[i, "zc1_subject_specific"] = round(DEC.loc[gm, "subject_specific"], 4)
        if gm in PNR.index:
            pt.loc[i, "pn1cr_peer_median_delta"] = round(PNR.loc[gm, "peer_median_delta"], 4)
            pt.loc[i, "pn1cr_netted_delta"] = round(PNR.loc[gm, "peer_netted_delta"], 4)
            pt.loc[i, "pn1cr_rank_most_negative"] = int(PNR.loc[gm, "subject_rank_most_negative"])
            pt.loc[i, "pn1cr_cohort_n"] = int(PNR.loc[gm, "cohort_n"])

    def verdict(r):
        sig = r.p < 0.05 if r.p == r.p else False
        up = r.delta > 0
        net = r.netted_delta
        if r.premise == "P1":
            if r.window.startswith("2025"):
                return "NOT SUPPORTED at season grain (flat)" if abs(r.delta) < 0.01 else ("SUPPORTED" if up else "CONTRADICTED")
            return ("SUPPORTED — directional" if up and not sig else "SUPPORTED" if up else "CONTRADICTED")
        if r.premise == "P2":
            if r.window.startswith("2025"):
                ss = r.zc1_subject_specific
                return (f"SUPPORTED — about {abs(ss / r.zc1_native_delta):.0%} his own; "
                        f"{abs(r.zc1_rail_effect / r.zc1_native_delta):.0%} ABS rail change (O-18)") if not up else "CONTRADICTED"
            return "DIRECTIONAL, inside noise" if not sig else ("SUPPORTED" if not up else "CONTRADICTED")
        if r.premise in ("P3", "E1"):
            if r.window.startswith("2025"):
                return "CONTRADICTED — chase went UP (1H-driven)" if up else ("SUPPORTED" if sig else "DIRECTIONAL")
            return ("SUPPORTED" if (not up and sig) else "SUPPORTED — directional" if not up else "CONTRADICTED")
        if r.premise == "P4":
            if r.window.startswith("2025"):
                return "NOT SUPPORTED at season grain (flat)" if abs(r.delta) < 0.01 else ("SUPPORTED" if not up else "CONTRADICTED")
            return "SUPPORTED" if (not up and sig) else ("SUPPORTED — directional" if not up else "CONTRADICTED")
        if r.premise == "K2":
            return "FLAT — around the edge as often" if abs(r.delta) < 0.015 else ("UP" if up else "DOWN")
        if r.premise == "K1":
            if r.window.startswith("2025"):
                ss = r.zc1_subject_specific
                return (f"SUPPORTED — {ss:+.3f} survives rail + league netting "
                        f"({abs(ss / r.zc1_native_delta):.0%} his own)") if (up and ss > 0.01) else ("SUPPORTED raw only" if up else "CONTRADICTED")
            return "SUPPORTED — directional" if up and not sig else ("SUPPORTED" if up else "CONTRADICTED")
        return ""
    pt["verdict"] = pt.apply(verdict, axis=1)
    W("premise_tests", pt)

    # ---------------- 11b. split tests (2026 1H -> 2H, beyond-shadow chase) --
    stt = []
    def _bt(label, d1, d2, dl1, dl2):
        a = K.shadow_profile(["half"], d1).iloc[0]; b = K.shadow_profile(["half"], d2).iloc[0]
        la = K.shadow_profile(["half"], dl1).iloc[0]; lb = K.shadow_profile(["half"], dl2).iloc[0]
        z_, p_ = zp(b.swings_beyond, b.n_beyond, a.swings_beyond, a.n_beyond)
        stt.append(dict(split=label, n_beyond_1h=int(a.n_beyond), chase_1h=round(a.beyond_shadow_chase_rate, 4),
                        n_beyond_2h=int(b.n_beyond), chase_2h=round(b.beyond_shadow_chase_rate, 4),
                        delta=round(b.beyond_shadow_chase_rate - a.beyond_shadow_chase_rate, 4), z=z_, p=p_,
                        league_1h=round(la.beyond_shadow_chase_rate, 4), league_2h=round(lb.beyond_shadow_chase_rate, 4),
                        miss_1h=round(a.shadow_miss_rate, 4), miss_2h=round(b.shadow_miss_rate, 4)))
    L26 = df[df.game_year == 2026]
    for lab, fs, fl in [
        ("all pitches", lambda x: x, lambda x: x),
        ("vs RHB", lambda x: x[x.stand == "R"], lambda x: x[x.stand == "R"]),
        ("vs LHB", lambda x: x[x.stand == "L"], lambda x: x[x.stand == "L"]),
        ("Changeup", lambda x: x[x.pitch_name == "Changeup"], lambda x: x[x.pitch_name == "Changeup"]),
        ("Sinker", lambda x: x[x.pitch_name == "Sinker"], lambda x: x[x.pitch_name == "Sinker"]),
        ("Slider", lambda x: x[x.pitch_name == "Slider"], lambda x: x[x.pitch_name == "Slider"]),
        ("pitcher ahead (balls < strikes)", lambda x: x[x.balls < x.strikes], lambda x: x[x.balls < x.strikes]),
        ("two strikes", lambda x: x[x.strikes == 2], lambda x: x[x.strikes == 2]),
    ]:
        s1, s2 = fs(c26[c26.half == "1H"]), fs(c26[c26.half == "2H"])
        l1, l2 = fl(L26[L26.half == "1H"]), fl(L26[L26.half == "2H"])
        _bt(lab, s1, s2, l1, l2)
    W("split_tests", pd.DataFrame(stt))

    # ---------------- 12. defect exposure ---------------------------------
    wr_all = K.whiff_rate(["game_date"], cs)
    fp_all = K.fpsr(["game_date"], cs)
    de = pd.DataFrame([
        dict(defect="D-1/D-2 whiff_rate inner join drops zero-whiff groups", grain="subject start",
             exposed=int(cs.game_date.nunique() - wr_all.game_date.nunique()), note="groups lost"),
        dict(defect="D-7/O-13 chase_rate counts NULL zone as in-zone", grain="subject pitch",
             exposed=int(cs.zone.isna().sum()), note="2025 only; 1 pitch"),
        dict(defect="O-8 hard_hit_rate counts untracked BIP as not-hard-hit", grain="subject BIP",
             exposed=int(((cs.type == "X") & cs.launch_speed.isna()).sum()), note="untracked BIP"),
        dict(defect="O-14 bbrate excludes intent_walk from numerator", grain="subject PA",
             exposed=int((cs.events == "intent_walk").sum()), note="IBB count 2021-26"),
        dict(defect="fpsr returns only groups with >=1 first-pitch ball", grain="subject start",
             exposed=int(cs.game_date.nunique() - fp_all.game_date.nunique()), note="groups lost"),
        dict(defect="chase_rate inner i/j merge -> NaN for zero-chase groups", grain="subject month",
             exposed=int(K.chase_rate(["month", "game_year"], cs).chase_rate.isna().sum()), note="groups NaN"),
        dict(defect="O-18 NEW: 2026 zone rails redefined (ABS) — YoY zone metrics confounded", grain="league",
             exposed=1, note="controlled with PN-1 + ZC-1; see zone_rail_audit"),
        dict(defect="D-9 nresults(['batter']) KeyError", grain="n/a", exposed=0, note="not called at batter grain"),
    ])
    W("defect_exposure", de)

    # ---------------- 13. DQ scorecard ------------------------------------
    dq = [
        ("DQ-1", "entity lock: 650911 -> one player_name", len(names) == 1, str(names)),
        ("DQ-2", "no duplicate pitch keys after dedup", True, f"dropped {df.attrs['dedup_dropped']}"),
        ("DQ-3", "regular season only", set(df.game_type) == {"R"}, str(sorted(set(df.game_type)))),
        ("DQ-4", "anchor = 2026-09-15", df.game_date.max() == K.ANCHOR_GAME_DATE, df.game_date.max()),
        ("DQ-5", "subject location completeness >= 99.9%", (cs.region != "untracked").mean() >= 0.999,
         f"{(cs.region != 'untracked').mean():.5f}"),
        ("DQ-6", "subject zone attribute completeness >= 99.9%", cs.zone.notna().mean() >= 0.999,
         f"{cs.zone.notna().mean():.5f}"),
        ("DQ-7", "every 2026 appearance is a start", starts26 == 31, f"{starts26}/31"),
        ("DQ-8", "plate_x sign: RHB HBP < 0 < LHB HBP", hbp["R"] < 0 < hbp["L"], f"{hbp['R']:.2f}/{hbp['L']:.2f}"),
        ("DQ-9", "SZ regions partition located pitches exactly",
         int((season.n_heart + season.n_edge_in + season.n_edge_out + season.n_beyond - season.located_pitches).abs().sum()) == 0, "sum check"),
        ("DQ-10", "edge_rate_twin == governed edge_rate", bool((er_tw.edge_rate_twin - er_tw.edge_rate).abs().max() < 0.0006), "<=0.0005"),
        ("DQ-11", "2026 rails constant per batter, SD < 0.01 ft (O-18)", aud.set_index("season").loc[2026, "share_constant_1cm"] > 0.95,
         f"{aud.set_index('season').loc[2026, 'share_constant_1cm']:.3f}"),
        ("DQ-12", "geometric vs Statcast zone disagreement < 6%", xw.iloc[1].disagree_share < 0.06, f"{xw.iloc[1].disagree_share:.4f}"),
        ("DQ-13", "PN-1 cohort >= 10 arms (2025->2026)", int(pn[pn.y1 == 2026].cohort_n.min()) >= 10,
         str(int(pn[pn.y1 == 2026].cohort_n.min())) + " (min across bases)"),
        ("DQ-14", "ZC-1 subject coverage >= 60% (2025)", float(zc[(zc.population == 'Sánchez') & (zc.game_year == 2025)].coverage.iloc[0]) >= 0.6,
         f"{float(zc[(zc.population == 'Sánchez') & (zc.game_year == 2025)].coverage.iloc[0]):.3f}"),
        ("DQ-15", "2021-22 sample flagged (swingman, <1000 pitches)", int(S.loc['2021-22', 'pitches']) < 1000, str(int(S.loc['2021-22', 'pitches']))),
        ("DQ-16", "no rate published on a zero denominator", bool(season.beyond_shadow_chase_rate.notna().all()), "season grain"),
        ("DQ-17", "arm_angle completeness (2026, subject)", c26.arm_angle.notna().mean() >= 0.9, f"{c26.arm_angle.notna().mean():.3f} — not used"),
    ]
    dq = pd.DataFrame(dq, columns=["rule", "description", "pass", "evidence"])
    dq["status"] = np.where(dq["pass"], "PASS", np.where(dq.rule == "DQ-17", "WARN", "FAIL"))
    W("dq_scorecard", dq)
    hard_fail = dq[(dq.status == "FAIL")]
    assert hard_fail.empty, hard_fail

    # ---------------- 14. dashboard payload -------------------------------
    pl = cs[(cs.game_year >= 2025) & (cs.region != "untracked")][
        ["game_year", "half", "month", "game_date", "stand", "pitch_name", "plate_x", "plate_z",
         "sz_top", "sz_bot", "region", "is_swing", "description", "balls", "strikes", "zone",
         "events", "pitch_number"]].copy()
    pl["pa_end"] = (pl.events.notna() & (pl.events != "pickoff_1b")).astype(int)
    pl["walk"] = (pl.events == "walk").astype(int)
    pl["in_zone_attr"] = (pl.zone <= 9).astype(int)
    pl = pl.drop(columns=["events", "zone"])
    pl["plate_x"] = pl.plate_x.round(3); pl["plate_z"] = pl.plate_z.round(3)
    pl["sz_top"] = pl.sz_top.round(3); pl["sz_bot"] = pl.sz_bot.round(3)
    pl["is_swing"] = pl.is_swing.astype(int)
    pl["whiff"] = pl.description.isin(K.WHIFFS).astype(int)
    pl = pl.drop(columns=["description"])
    W("pitch_locations", pl)
    payload = dict(
        meta=dict(uc="UC #45", contract="uc-pps-031", build="dp_uc45", subject=K.SUBJECT_NAME,
                  mlbam=K.SUBJECT_ID, anchor=K.ANCHOR_GAME_DATE, asg_cut=K.ASG_BREAK_2026,
                  ball_ft=K.BALL_FT, plate_half=K.PLATE_HALF, built_utc=t0.isoformat(timespec="seconds")),
        pitches=dict(cols=list(pl.columns), rows=pl.values.tolist()),
        season=season.round(4).to_dict(orient="records"),
        half=half.round(4).to_dict(orient="records"),
        month=month.round(4).to_dict(orient="records"),
        starts=start.round(4).to_dict(orient="records"),
        league=league[["population", "game_year", "half", "in_zone_rate", "chase_rate", "edge_rate",
                       "shadow_zone_rate", "shadow_miss_rate", "beyond_shadow_chase_rate",
                       "pitch_share_ahead", "bbrate"]].round(4).to_dict(orient="records"),
        premises=pt.round(4).replace({np.nan: None}).to_dict(orient="records"),
        start_dist=sd[["game_year", "half", "is_subject", "shadow_miss_rate", "beyond_shadow_chase_rate"]].round(4).to_dict(orient="records"),
    )
    (OUT / "dp_uc45_payload.json").write_text(json.dumps(payload, default=lambda o: None if o != o else str(o)))
    RECEIPTS.append("dp_uc45_payload.json")
    print(f"BUILD OK — {len(RECEIPTS)} receipts in {OUT}  ({(dt.datetime.now(dt.timezone.utc)-t0).seconds}s)")
    print(pt[["premise", "window", "metric", "v_before", "v_after", "delta", "p", "netted_delta", "verdict"]].to_string())


if __name__ == "__main__":
    main()
