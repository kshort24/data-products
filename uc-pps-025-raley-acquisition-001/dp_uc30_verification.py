"""
============================================================================
UC #31 (uc-pps-025) — INDEPENDENT RECOMPUTE HARNESS
============================================================================
Layer-4 certification artifact.

PURPOSE. Prove that every number published in
`dp_uc30_raley_acquisition_read_report.md` reconciles to the source data, by
recomputing it through a DIFFERENT code path than the build script used.

METHOD. The build script routes almost everything through the locked
`get_stats()` / `nresults()` family inherited from dp_uc29. This harness
deliberately does NOT import or reuse those functions. It recomputes each
quantity from primitive pandas operations — direct boolean masks, explicit
event counting, hand-rolled wOBA from the FanGraphs constants — and asserts
agreement with the CSV receipts to a stated tolerance.

A number that only agrees with itself has not been verified. The point of the
separate code path is that a logic error in the locked functions would show up
here as a mismatch rather than being silently reproduced.

SCOPE. Structural locks, era partition, every cell of era_summary,
season_log, arsenal_by_era, platoon, pitch_by_hand, two_strike, sightline,
lhp_release_benchmark, release_by_pitch, tracking_proxies, outing_log,
deployment, damage_log — plus the four NEW KPI formulas recomputed from
scratch, and every headline figure quoted in the report prose.

Run:  python dp_uc30_verification.py
Exit: 0 if all assertions pass, 1 otherwise.
============================================================================
"""
from __future__ import annotations
import os
import sys
import glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

RALEY = 548384
PRE_TJ_END = "2024-04-19"
POST_TJ_START = "2025-07-19"
ERA_PRE = "Pre-TJ (2020-2024)"
ERA_POST = "Post-TJ (2025-2026)"
BENCH_MIN_PITCHES = 300
BOX_CENTER_FT = 3.208

_DATA = [os.environ.get("MLB_DATA_ROOT", ""),
         "/sessions/adoring-hopeful-wozniak/mnt/MLB/data/phillies",
         r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies"]
PHIL_DIR = next((p for p in _DATA if p and os.path.isdir(p)), None)
OPP_DIR = os.path.join(os.path.dirname(PHIL_DIR), "opponents")
REPO_ROOT = os.path.dirname(os.path.dirname(PHIL_DIR))
WOBA_CSV = os.path.join(REPO_ROOT, "wOBA and FIP Constants.csv")

SWINGS = {"foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"}
WHIFFS = {"foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"}

RESULTS: list[dict] = []


def check(name, expected, actual, tol=0.0011, group=""):
    """Assert agreement. Numeric compare within tol; else exact."""
    try:
        if expected is None or actual is None:
            ok = expected is actual
        elif isinstance(expected, str) or isinstance(actual, str):
            ok = str(expected) == str(actual)
        elif (isinstance(expected, float) and np.isnan(expected)) or \
             (isinstance(actual, float) and np.isnan(actual)):
            ok = (isinstance(expected, float) and np.isnan(expected)) and \
                 (isinstance(actual, float) and np.isnan(actual))
        else:
            ok = abs(float(expected) - float(actual)) <= tol
    except Exception:
        ok = False
    RESULTS.append({"group": group, "check": name, "published": expected,
                    "recomputed": actual, "status": "PASS" if ok else "FAIL"})
    if not ok:
        print(f"    FAIL  {name}: published={expected} recomputed={actual}")
    return ok


# ---------------------------------------------------------------------------
# INDEPENDENT PRIMITIVES — deliberately not the locked functions
# ---------------------------------------------------------------------------
def v_pa(df):
    """Plate appearances = rows carrying a terminal event, excluding pickoffs.
    Independent path: notna() + explicit exclusion, not `.replace().isin()`."""
    e = df.events
    return int(((e.notna()) & (e != "pickoff_1b") & (e != "")).sum())


def v_ab(df):
    e = df.events
    non_ab = {"walk", "intent_walk", "hit_by_pitch", "sac_fly", "sac_bunt", "pickoff_1b"}
    return int(((e.notna()) & (~e.isin(non_ab))).sum())


def v_event_count(df, *names):
    return int(df.events.isin(names).sum())


def v_woba(df):
    """Hand-rolled wOBA from FanGraphs season constants, joined per row.
    Independent path: builds the numerator from event counts x that season's
    weight, rather than summing pre-joined weight columns."""
    w = pd.read_csv(WOBA_CSV).set_index("Season")
    num = 0.0
    for yr, g in df.groupby("game_year"):
        c = w.loc[yr]
        num += (v_event_count(g, "walk") * c.wBB
                + v_event_count(g, "hit_by_pitch") * c.wHBP
                + v_event_count(g, "single") * c.w1B
                + v_event_count(g, "double") * c.w2B
                + v_event_count(g, "triple") * c.w3B
                + v_event_count(g, "home_run") * c.wHR)
    pa = v_pa(df)
    return num / pa if pa else np.nan


def v_whiff(df):
    sw = int(df.description.isin(SWINGS).sum())
    wh = int(df.description.isin(WHIFFS).sum())
    return wh / sw if sw else np.nan


def v_chase(df):
    ooz = df[df.zone > 9]
    if not len(ooz):
        return np.nan
    return float(ooz.description.isin(SWINGS).sum() / len(ooz))


def v_zone_strict(df):
    t = df[df.pitch_name.notna()]
    return float((t.zone <= 9).sum() / len(t)) if len(t) else np.nan


def v_csw(df):
    n = len(df)
    called = int((df.description == "called_strike").sum())
    wh = int(df.description.isin(WHIFFS).sum())
    return (called + wh) / n if n else np.nan


def v_putaway(df):
    two = int((df.strikes == 2).sum())
    k = v_event_count(df, "strikeout", "strikeout_double_play")
    return k / two if two else np.nan


def v_fpsr(df):
    fp = df[df.pitch_number == 1]
    if not len(fp):
        return np.nan
    return float((fp.type != "B").sum() / len(fp))


def v_hardhit(df):
    bip = df[df.type == "X"]
    if not len(bip):
        return np.nan
    return float((bip.launch_speed >= 95).sum() / len(bip))


def v_xwobacon(df):
    bip = df[df.type == "X"]
    s = bip.estimated_woba_using_speedangle.dropna()
    return float(s.mean()) if len(s) else np.nan


def v_rsa(x, z):
    return float(np.degrees(np.arctan2(z, abs(x))))


def v_slo(rel_x_series, stand_series, center=BOX_CENTER_FT):
    c = np.where(stand_series.values == "L", center, -center)
    return float(np.mean(np.abs(rel_x_series.values - c)))


# ---------------------------------------------------------------------------
def load_raley():
    d = pd.read_parquet(os.path.join(OPP_DIR, "raley.parquet"))
    d = d[(d.pitcher == RALEY) & (d.game_type == "R")]
    d = d.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"]).copy()
    for c in ["release_pos_x", "release_pos_z", "release_extension", "release_speed",
              "release_spin_rate", "pfx_x", "pfx_z", "zone", "strikes", "balls",
              "pitch_number", "launch_speed", "arm_angle", "inning",
              "bat_speed", "swing_length", "miss_distance",
              "estimated_woba_using_speedangle"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["game_date"] = pd.to_datetime(d.game_date)
    d["era"] = np.where(d.game_date <= pd.Timestamp(PRE_TJ_END), ERA_PRE,
                        np.where(d.game_date >= pd.Timestamp(POST_TJ_START),
                                 ERA_POST, "REHAB GAP"))
    return d


def load_lhp():
    import pyarrow.parquet as pq
    frames = []
    for f in sorted(glob.glob(os.path.join(PHIL_DIR, "phils_*.parquet"))):
        have = set(pq.ParquetFile(f).schema_arrow.names)
        cols = [c for c in ["game_year", "game_type", "p_throws", "player_name", "pitcher",
                            "release_pos_x", "release_pos_z", "release_extension",
                            "release_speed", "pitch_name", "game_pk", "at_bat_number",
                            "pitch_number", "phillies_role"] if c in have]
        if "arm_angle" in have:
            cols += ["arm_angle"]
        d = pd.read_parquet(f, columns=cols)
        if "arm_angle" not in d.columns:
            d["arm_angle"] = np.nan
        frames.append(d)
    p = pd.concat(frames, ignore_index=True)
    p = p[(p.phillies_role == "pitching") & (p.game_type == "R")]
    return p.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])


def r(name):
    return pd.read_csv(os.path.join(OUT, f"dp_uc30_{name}.csv"))


# ---------------------------------------------------------------------------
def main():
    print("=" * 74)
    print("UC #31 / uc-pps-025 — INDEPENDENT RECOMPUTE HARNESS")
    print("=" * 74)

    d = load_raley()
    pre = d[d.era == ERA_PRE]
    post = d[d.era == ERA_POST]
    tpost = post[post.pitch_name.notna()]

    # ---------------- structural ------------------------------------------
    print("\n[1] structural locks and era partition")
    g = "structural"
    check("distinct pitcher ids", 1, int(d.pitcher.nunique()), group=g)
    check("pitcher id is Raley", RALEY, int(d.pitcher.unique()[0]), group=g)
    check("throws L", "L", str(d.p_throws.unique()[0]), group=g)
    check("game_type all R", 1, int(d.game_type.nunique()), group=g)
    check("duplicate pitch rows", 0,
          int(d.duplicated(["game_pk", "at_bat_number", "pitch_number"]).sum()), group=g)
    check("rows in rehab gap", 0, int((d.era == "REHAB GAP").sum()), group=g)
    check("zero Phillies rows", 0, int((np.where(d.inning_topbot == "Top", d.home_team,
                                                 d.away_team) == "PHI").sum()), group=g)
    check("pre+post = total rows", len(d), len(pre) + len(post), group=g)
    check("no pre-2020 rows", 0, int((d.game_year < 2020).sum()), group=g)
    check("last pre-TJ game date", PRE_TJ_END, str(pre.game_date.max().date()), group=g)
    check("first post-TJ game date", POST_TJ_START, str(post.game_date.min().date()), group=g)

    # ---------------- era summary -----------------------------------------
    print("\n[2] era_summary — every published cell")
    es = r("era_summary").set_index("era")
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        g = f"era_summary[{label}]"
        row = es.loc[label]
        t = df[df.pitch_name.notna()]
        pa, ab = v_pa(df), v_ab(df)
        hits = v_event_count(df, "home_run", "single", "double", "triple")
        singles = v_event_count(df, "single")
        dbl = v_event_count(df, "double")
        tri = v_event_count(df, "triple")
        hr = v_event_count(df, "home_run")
        bb = v_event_count(df, "walk")
        hbp = v_event_count(df, "hit_by_pitch")
        ks = v_event_count(df, "strikeout", "strikeout_double_play")
        check("outings", row.outings, int(df.game_pk.nunique()), group=g)
        check("pitches", row.pitches, len(df), group=g)
        check("batters_faced", row.batters_faced, pa, group=g)
        check("hits", row.hits, hits, group=g)
        check("hrs", row.hrs, hr, group=g)
        check("ba", row.ba, round(hits / ab, 3), group=g)
        check("obp", row.obp, round((hits + bb + hbp) / pa, 3), group=g)
        check("slg", row.slg,
              round((singles + 2 * dbl + 3 * tri + 4 * hr) / ab, 3), group=g)
        check("woba", row.woba, round(v_woba(df), 3), group=g)
        check("k_rate", row.k_rate, round(ks / pa, 3), group=g)
        check("bb_rate", row.bb_rate, round(bb / pa, 3), group=g)
        check("hr_rate", row.hr_rate, round(hr / pa, 3), group=g)
        check("whiff_rate", row.whiff_rate, round(v_whiff(df), 3), group=g)
        check("chase_rate", row.chase_rate, round(v_chase(df), 3), group=g)
        check("zone_rate_strict", row.zone_rate_strict, round(v_zone_strict(df), 3), group=g)
        check("csw_rate", row.csw_rate, round(v_csw(df), 3), group=g)
        check("putaway_rate", row.putaway_rate, round(v_putaway(df), 3), group=g)
        check("first_pitch_strike_rate", row.first_pitch_strike_rate,
              round(v_fpsr(df), 3), group=g)
        check("hard_hit_rate", row.hard_hit_rate, round(v_hardhit(df), 3), group=g)
        check("xwobacon", row.xwobacon, round(v_xwobacon(df), 3), group=g)
        # OPEN ITEM O4 (found by this harness, 2026-08-04):
        # the locked `xwobacon()` reports its BIP count with `.agg(..., "size")`,
        # which counts every ball in play including those carrying NO tracked
        # xwOBA estimate. The MEAN is computed over non-nulls and is correct;
        # only the published n is inflated. The locked function is inherited
        # verbatim and is NOT edited. Both counts are therefore asserted here
        # and the gap is carried as a documented open item.
        bip_all = int((df.type == "X").sum())
        bip_est = int(df[df.type == "X"].estimated_woba_using_speedangle.notna().sum())
        check("xwobacon_bip (published = all BIP, `size` semantics)",
              row.xwobacon_bip, bip_all, group=g)
        check("O4: BIP rows lacking an xwOBA estimate (published n minus true n)",
              int(row.xwobacon_bip) - bip_est, bip_all - bip_est, group=g)
        check("avg_velo", row.avg_velo, round(float(t.release_speed.mean()), 2),
              tol=0.011, group=g)
        check("avg_arm_angle_native", row.avg_arm_angle_native,
              round(float(t.arm_angle.mean()), 2), tol=0.011, group=g)
        check("avg_rel_x", row.avg_rel_x, round(float(t.release_pos_x.mean()), 3), group=g)
        check("avg_rel_z", row.avg_rel_z, round(float(t.release_pos_z.mean()), 3), group=g)
        check("avg_extension", row.avg_extension,
              round(float(t.release_extension.mean()), 3), group=g)
        check("avg_rsa_proxy (NEW KPI recomputed)", row.avg_rsa_proxy,
              round(float(np.degrees(np.arctan2(t.release_pos_z,
                                                t.release_pos_x.abs())).mean()), 2),
              tol=0.011, group=g)

    # ---------------- season log ------------------------------------------
    print("\n[3] season_log")
    sl = r("season_log").set_index("season")
    for y, sub in d.groupby("game_year"):
        g = f"season_log[{y}]"
        row = sl.loc[y]
        check("pitches", row.pitches, len(sub), group=g)
        check("batters_faced", row.batters_faced, v_pa(sub), group=g)
        check("outings", row.outings, int(sub.game_pk.nunique()), group=g)
        check("woba", row.woba, round(v_woba(sub), 3), group=g)
        check("whiff_rate", row.whiff_rate, round(v_whiff(sub), 3), group=g)
        check("hard_hit_rate", row.hard_hit_rate, round(v_hardhit(sub), 3), group=g)
    check("season_log rows == distinct seasons", len(sl), int(d.game_year.nunique()),
          group="season_log")

    # ---------------- arsenal ---------------------------------------------
    print("\n[4] arsenal_by_era")
    ars = r("arsenal_by_era")
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        t = df[df.pitch_name.notna()]
        sub = ars[ars.era == label]
        check(f"[{label}] usage sums to 1", 1.0, round(float(sub.usage.sum()), 3),
              tol=0.0016, group="arsenal")
        check(f"[{label}] pitch-type count", len(sub), int(t.pitch_name.nunique()),
              group="arsenal")
        for _, row in sub.iterrows():
            gg = f"arsenal[{label}/{row.pitch_name}]"
            p = t[t.pitch_name == row.pitch_name]
            check("pitches", row.pitches, len(p), group=gg)
            check("usage", row.usage, round(len(p) / len(t), 3), group=gg)
            check("velo", row.velo, round(float(p.release_speed.mean()), 3),
                  tol=0.0011, group=gg)
            check("spin", row.spin, round(float(p.release_spin_rate.mean()), 3),
                  tol=0.011, group=gg)
            check("ivb_in", row.ivb_in, round(float(p.pfx_z.mean() * 12), 3),
                  tol=0.0011, group=gg)
            check("hb_in", row.hb_in, round(float(p.pfx_x.mean() * 12), 3),
                  tol=0.0011, group=gg)
            check("whiff_rate", row.whiff_rate, round(v_whiff(p), 3), group=gg)
            check("chase_rate", row.chase_rate, round(v_chase(p), 3), group=gg)
            check("csw_rate", row.csw_rate, round(v_csw(p), 3), group=gg)
            check("hard_hit_rate", row.hard_hit_rate, round(v_hardhit(p), 3), group=gg)
            check("xwobacon", row.xwobacon, round(v_xwobacon(p), 3), group=gg)

    # ---------------- platoon ---------------------------------------------
    print("\n[5] platoon")
    pl = r("platoon")
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        for hand in ["L", "R"]:
            gg = f"platoon[{label}/{hand}]"
            sub = df[df.stand == hand]
            row = pl[(pl.era == label) & (pl.bats == hand)].iloc[0]
            check("pitches", row.pitches, len(sub), group=gg)
            check("batters_faced", row.batters_faced, v_pa(sub), group=gg)
            check("woba", row.woba, round(v_woba(sub), 3), group=gg)
            check("whiff_rate", row.whiff_rate, round(v_whiff(sub), 3), group=gg)
            check("chase_rate", row.chase_rate, round(v_chase(sub), 3), group=gg)
            check("csw_rate", row.csw_rate, round(v_csw(sub), 3), group=gg)
            check("putaway_rate", row.putaway_rate, round(v_putaway(sub), 3), group=gg)
            check("first_pitch_strike_rate", row.first_pitch_strike_rate,
                  round(v_fpsr(sub), 3), group=gg)
            check("hard_hit_rate", row.hard_hit_rate, round(v_hardhit(sub), 3), group=gg)
            check("xwobacon", row.xwobacon, round(v_xwobacon(sub), 3), group=gg)
            check("zone_rate_strict", row.zone_rate_strict,
                  round(v_zone_strict(sub), 3), group=gg)
            t = sub[sub.pitch_name.notna()]
            check("slo_ft (NEW KPI recomputed)", row.slo_ft,
                  round(v_slo(t.release_pos_x, t.stand), 3), group=gg)

    # ---------------- pitch x hand ----------------------------------------
    print("\n[6] pitch_by_hand")
    pxh = r("pitch_by_hand")
    for _, row in pxh.iterrows():
        gg = f"pxh[{row.pitch_name}/{row.bats}]"
        p = tpost[(tpost.pitch_name == row.pitch_name) & (tpost.stand == row.bats)]
        check("pitches", row.pitches, len(p), group=gg)
        check("usage_within_hand", row.usage_within_hand,
              round(len(p) / len(tpost[tpost.stand == row.bats]), 3), group=gg)
        check("whiff_rate", row.whiff_rate, round(v_whiff(p), 3), group=gg)
        check("chase_rate", row.chase_rate, round(v_chase(p), 3), group=gg)
        check("in_zone_rate", row.in_zone_rate,
              round(float((p.zone <= 9).sum() / len(p)), 3), group=gg)
        check("csw_rate", row.csw_rate, round(v_csw(p), 3), group=gg)
        check("hard_hit_rate", row.hard_hit_rate, round(v_hardhit(p), 3), group=gg)
        check("xwobacon", row.xwobacon, round(v_xwobacon(p), 3), group=gg)
        check("velo", row.velo, round(float(p.release_speed.mean()), 2),
              tol=0.011, group=gg)

    # ---------------- two strike ------------------------------------------
    print("\n[7] two_strike")
    ts = r("two_strike")
    two = tpost[tpost.strikes == 2]
    for _, row in ts.iterrows():
        gg = f"two_strike[{row.pitch_name}/{row.bats}]"
        p = two[(two.pitch_name == row.pitch_name) & (two.stand == row.bats)]
        check("two_strike_pitches", row.two_strike_pitches, len(p), group=gg)
        check("share_of_two_strike", row.share_of_two_strike,
              round(len(p) / len(two[two.stand == row.bats]), 3), group=gg)
        check("whiff_rate", row.whiff_rate, round(v_whiff(p), 3), group=gg)
        check("chase_rate", row.chase_rate, round(v_chase(p), 3), group=gg)
        check("in_zone_rate", row.in_zone_rate,
              round(float((p.zone <= 9).sum() / len(p)), 3), group=gg)

    # ---------------- NEW KPI: benchmark population -----------------------
    print("\n[8] lhp_release_benchmark — RSA / RDI / SLO recomputed from source")
    lhp = load_lhp()
    lhp = lhp[(lhp.p_throws == "L") & (lhp.game_year >= 2015) & lhp.pitch_name.notna()]
    agg = lhp.groupby(["pitcher", "player_name"]).agg(
        n=("release_pos_x", "size"), rel_x=("release_pos_x", "mean"),
        rel_z=("release_pos_z", "mean")).reset_index()
    agg = agg[agg.n >= BENCH_MIN_PITCHES]
    bm = r("lhp_release_benchmark")
    pop = bm[~bm.is_raley]
    g = "benchmark"
    check("population size", len(pop), len(agg), group=g)
    check("population is 28 (as reported)", 28, len(agg), group=g)
    mx, sx = agg.rel_x.mean(), agg.rel_x.std()
    mz, sz = agg.rel_z.mean(), agg.rel_z.std()
    for _, row in pop.iterrows():
        a = agg[agg.pitcher == row.pitcher]
        if not len(a):
            check(f"pitcher {row.player_name} present in recompute", True, False, group=g)
            continue
        a = a.iloc[0]
        gg = f"bench[{row.player_name}]"
        check("pitches", row.pitches, int(a.n), group=gg)
        check("rel_x", row.rel_x, round(float(a.rel_x), 3), group=gg)
        check("rel_z", row.rel_z, round(float(a.rel_z), 3), group=gg)
        check("rsa_proxy", row.rsa_proxy, round(v_rsa(a.rel_x, a.rel_z), 3),
              tol=0.0011, group=gg)
        check("rdi", row.rdi, round(float(np.hypot((a.rel_x - mx) / sx,
                                                   (a.rel_z - mz) / sz)), 3), group=gg)
        check("slo_vs_lhh", row.slo_vs_lhh, round(abs(a.rel_x - BOX_CENTER_FT), 3), group=gg)
        check("slo_vs_rhh", row.slo_vs_rhh, round(abs(a.rel_x + BOX_CENTER_FT), 3), group=gg)

    # Raley's own rows, and the ranking claim in the report
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        t = df[df.pitch_name.notna()]
        row = bm[bm.player_name.str.contains(label, regex=False)].iloc[0]
        gg = f"bench[Raley {label}]"
        check("rel_x", row.rel_x, round(float(t.release_pos_x.mean()), 3), group=gg)
        check("rel_z", row.rel_z, round(float(t.release_pos_z.mean()), 3), group=gg)
        check("rsa_proxy", row.rsa_proxy,
              round(v_rsa(t.release_pos_x.mean(), t.release_pos_z.mean()), 3),
              tol=0.0011, group=gg)
        check("rdi (centroid excludes Raley)", row.rdi,
              round(float(np.hypot((t.release_pos_x.mean() - mx) / sx,
                                   (t.release_pos_z.mean() - mz) / sz)), 3), group=gg)
    ranked = bm.sort_values("rsa_proxy").reset_index(drop=True)
    raley_post_rank = int(ranked.index[ranked.player_name.str.contains(
        ERA_POST, regex=False)][0]) + 1
    check("REPORT CLAIM: Raley post-TJ is 5th-lowest RSA of 30", 5, raley_post_rank,
          group="report_claims")
    check("REPORT CLAIM: benchmark table has 30 rows (28 pop + 2 Raley)", 30, len(bm),
          group="report_claims")

    # ---------------- NEW KPI: RTD ----------------------------------------
    print("\n[9] release_by_pitch — Release Tipping Delta recomputed")
    rbp = r("release_by_pitch")
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        t = df[df.pitch_name.notna()]
        m = t.groupby("pitch_name").agg(n=("release_pos_x", "size"),
                                        x=("release_pos_x", "mean"),
                                        z=("release_pos_z", "mean")).reset_index()
        q = m[m.n >= 25]
        best = 0.0
        for i in range(len(q)):
            for j in range(i + 1, len(q)):
                best = max(best, 12 * float(np.hypot(q.x.iloc[i] - q.x.iloc[j],
                                                     q.z.iloc[i] - q.z.iloc[j])))
        pub = float(rbp[rbp.era == label].rtd_in.iloc[0])
        check(f"RTD [{label}]", pub, round(best, 2), tol=0.011, group="RTD")

    post_rtd = float(rbp[rbp.era == ERA_POST].rtd_in.iloc[0])
    pre_rtd = float(rbp[rbp.era == ERA_PRE].rtd_in.iloc[0])
    check("REPORT CLAIM: post-TJ RTD is 5.3 in", 5.3, round(post_rtd, 1),
          tol=0.051, group="report_claims")
    check("REPORT CLAIM: pre-TJ RTD is 7.7 in", 7.7, round(pre_rtd, 1),
          tol=0.051, group="report_claims")
    check("REPORT CLAIM: RTD improved after surgery", True, post_rtd < pre_rtd,
          group="report_claims")

    sw = tpost[tpost.pitch_name == "Sweeper"]
    ct = tpost[tpost.pitch_name == "Cutter"]
    check("REPORT CLAIM: sweeper released ~3.2 in wider than cutter", 3.2,
          round(12 * float(sw.release_pos_x.mean() - ct.release_pos_x.mean()), 1),
          tol=0.051, group="report_claims")
    check("REPORT CLAIM: sweeper released ~4.0 in lower than cutter", 4.0,
          round(12 * float(ct.release_pos_z.mean() - sw.release_pos_z.mean()), 1),
          tol=0.051, group="report_claims")

    # ---------------- sightline -------------------------------------------
    print("\n[10] sightline")
    sg = r("sightline")
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        t = df[df.pitch_name.notna()]
        for hand in ["L", "R"]:
            sub = t[t.stand == hand]
            row = sg[(sg.era == label) & (sg.bats == hand) &
                     (sg.subject == "Raley, Brooks")].iloc[0]
            gg = f"sightline[{label}/{hand}]"
            check("pitches", row.pitches, len(sub), group=gg)
            check("mean_rel_x", row.mean_rel_x,
                  round(float(sub.release_pos_x.mean()), 3), group=gg)
            check("slo_ft_rulebook", row.slo_ft_rulebook,
                  round(v_slo(sub.release_pos_x, sub.stand), 3), group=gg)
    pop_slo_l = round(float(pop.slo_vs_lhh.mean()), 3)
    check("REPORT CLAIM: population SLO vs LHH = 0.96 ft", 0.96, round(pop_slo_l, 2),
          tol=0.0051, group="report_claims")
    raley_post_slo_l = float(bm[bm.player_name.str.contains(ERA_POST, regex=False)
                                ].slo_vs_lhh.iloc[0])
    check("REPORT CLAIM: Raley post-TJ SLO vs LHH = 0.08 ft", 0.08,
          round(raley_post_slo_l, 2), tol=0.0051, group="report_claims")
    check("REPORT CLAIM: Raley post-TJ SLO vs RHH = 6.34 ft", 6.34,
          round(float(bm[bm.player_name.str.contains(ERA_POST, regex=False)
                         ].slo_vs_rhh.iloc[0]), 2), tol=0.0051, group="report_claims")
    check("REPORT CLAIM: RDI post-TJ (1.26) ~ population mean (1.20), i.e. NOT unusual",
          True, abs(float(bm[bm.player_name.str.contains(ERA_POST, regex=False)].rdi.iloc[0])
                    - float(pop.rdi.mean())) < 0.25, group="report_claims")

    # ---------------- tracking proxies ------------------------------------
    print("\n[11] tracking_proxies")
    tp = r("tracking_proxies")
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        t = df[df.pitch_name.notna()]
        for hand in ["L", "R"]:
            sub = t[t.stand == hand]
            swg = sub[sub.description.isin(SWINGS)]
            wf = sub[sub.description.isin(WHIFFS)]
            row = tp[(tp.era == label) & (tp.bats == hand)].iloc[0]
            gg = f"tracking[{label}/{hand}]"
            check("swings", row.swings, len(swg), group=gg)
            check("whiffs", row.whiffs, len(wf), group=gg)
            check("whiffs_with_miss_distance", row.whiffs_with_miss_distance,
                  int(wf.miss_distance.notna().sum()), group=gg)
            check("miss_distance_in", row.miss_distance_in,
                  round(float(wf.miss_distance.mean()), 2), tol=0.011, group=gg)
            check("swing_length_ft", row.swing_length_ft,
                  round(float(swg.swing_length.mean()), 2), tol=0.011, group=gg)

    # ---------------- outings / deployment / damage ------------------------
    print("\n[12] outing_log, deployment, damage_log")
    ol = r("outing_log")
    g = "outings"
    check("outing count", len(ol), int(post.game_pk.nunique()), group=g)
    check("total pitches reconcile", int(ol.pitches.sum()), len(post), group=g)
    check("total BF reconcile", int(ol.batters_faced.sum()), v_pa(post), group=g)
    check("REPORT CLAIM: 34 outings entering the 7th", 34,
          int((ol.entry_inning == 7).sum()), group="report_claims")
    check("REPORT CLAIM: 17 entering the 6th", 17,
          int((ol.entry_inning == 6).sum()), group="report_claims")
    check("REPORT CLAIM: 15 entering the 8th", 15,
          int((ol.entry_inning == 8).sum()), group="report_claims")
    check("REPORT CLAIM: median 14 pitches", 14, float(ol.pitches.median()),
          group="report_claims")
    check("REPORT CLAIM: 26 of 75 with inherited runners", 26,
          int((ol.inherited_runners > 0).sum()), group="report_claims")
    check("REPORT CLAIM: 70 of 75 outings faced >= 1 RHH", 70,
          int((ol.rhh_faced > 0).sum()), group="report_claims")
    check("REPORT CLAIM: 5 outings faced only LHH", 5,
          int(((ol.rhh_faced == 0) & (ol.lhh_faced > 0)).sum()), group="report_claims")
    check("REPORT CLAIM: 12 multi-inning outings", 12,
          int((ol.innings_touched > 1).sum()), group="report_claims")
    check("REPORT CLAIM: 12 outings on 0-1 days rest", 12,
          int((ol.days_rest <= 1).sum()), group="report_claims")
    check("REPORT CLAIM: 18 outings entering 7th leading 1-3", 18,
          int(((ol.entry_inning == 7) & (ol.entry_state == "leading 1-3")).sum()),
          group="report_claims")
    check("REPORT CLAIM: 30 outings of exactly 3 BF", 30,
          int((ol.batters_faced == 3).sum()), group="report_claims")
    check("REPORT CLAIM: 22 outings of exactly 4 BF", 22,
          int((ol.batters_faced == 4).sum()), group="report_claims")

    dep = r("deployment")
    check("deployment outings reconcile", int(dep.outings.sum()), len(ol), group="outings")

    dl = r("damage_log")
    xbh = post[post.events.isin(["home_run", "double", "triple"])]
    check("damage_log rows", len(dl), len(xbh), group="damage")
    check("REPORT CLAIM: 16 XBH allowed post-TJ", 16, len(xbh), group="report_claims")
    check("REPORT CLAIM: 11 of 16 XBH on the sweeper", 11,
          int((xbh.pitch_name == "Sweeper").sum()), group="report_claims")
    check("REPORT CLAIM: 11 XBH allowed to RHH", 11,
          int((xbh.stand == "R").sum()), group="report_claims")
    check("REPORT CLAIM: 7 of those on the sweeper", 7,
          int(((xbh.stand == "R") & (xbh.pitch_name == "Sweeper")).sum()),
          group="report_claims")
    check("REPORT CLAIM: 2 HR allowed post-TJ", 2,
          v_event_count(post, "home_run"), group="report_claims")

    # ---------------- narrative claims ------------------------------------
    print("\n[13] remaining report prose claims")
    g = "report_claims"
    check("age 38 in 2026", 38, int(post[post.game_year == 2026].age_pit.max()), group=g)
    check("post-TJ arsenal is 4 pitches", 4, int(tpost.pitch_name.nunique()), group=g)
    check("curveball gone post-TJ", 0, int((tpost.pitch_name == "Curveball").sum()), group=g)
    check("4-seam gone post-TJ", 0,
          int((tpost.pitch_name == "4-Seam Fastball").sum()), group=g)
    check("pre-TJ arsenal was 6 pitches", 6,
          int(pre[pre.pitch_name.notna()].pitch_name.nunique()), group=g)
    check("more pitches to RHH than LHH post-TJ (661 vs 361)", 661,
          int((post.stand == "R").sum()), group=g)
    check("post-TJ pitches to LHH", 361, int((post.stand == "L").sum()), group=g)
    swp_pre = pre[pre.pitch_name == "Sweeper"]
    swp_post = tpost[tpost.pitch_name == "Sweeper"]
    check("sweeper whiff fell 37.2% -> 23.2%", 0.372, round(v_whiff(swp_pre), 3), group=g)
    check("sweeper whiff post-TJ", 0.232, round(v_whiff(swp_post), 3), group=g)
    check("sweeper IVB gained ~2.3 in", 2.3,
          round(float(swp_post.pfx_z.mean() * 12 - swp_pre.pfx_z.mean() * 12), 1),
          tol=0.051, group=g)
    check("July 2026 was the hardest post-TJ month (86.4 mph)", 86.4,
          round(float(tpost[(tpost.game_year == 2026) &
                            (tpost.game_date.dt.month == 7)].release_speed.mean()), 1),
          tol=0.051, group=g)
    check("release moved 3.7 in further arm-side after surgery", 3.7,
          round(12 * float(tpost.release_pos_x.mean()
                           - pre[pre.pitch_name.notna()].release_pos_x.mean()), 1),
          tol=0.051, group=g)

    mn = r("monthly_arc")
    for m_, v_ in [("2026-05", 0.267), ("2026-06", 0.211), ("2026-07", 0.170)]:
        check(f"whiff decline {m_}", v_,
              round(float(mn[mn.month == m_].whiff_rate.iloc[0]), 3), group=g)

    rw = r("rest_workload")
    b2b = rw[rw.rest_bucket.str.startswith("0-1")].iloc[0]
    check("back-to-back walk rate 2.6%", 0.026, round(float(b2b.bb_rate), 3), group=g)
    check("back-to-back velo 84.40", 84.40, round(float(b2b.velo), 2),
          tol=0.011, group=g)
    bs = r("batter_sequence").set_index("seq_bucket")
    check("1st batter whiff 27.7%", 0.277, round(float(bs.loc["1st batter"].whiff_rate), 3),
          group=g)
    check("3rd+ batter whiff 20.8%", 0.208,
          round(float(bs.loc["3rd+ batter"].whiff_rate), 3), group=g)

    cal = r("rsa_calibration")
    check("RSA calibration r = 0.831", 0.831, round(float(cal.pearson_r.iloc[0]), 3),
          group=g)
    check("RSA calibration n = 10 pitchers", 10,
          int(cal.n_calibration_pitchers.iloc[0]), group=g)

    dqs = r("dq_scorecard")
    check("build DQ scorecard is 38/38 PASS", 38, int((dqs.status == "PASS").sum()), group=g)
    check("build DQ scorecard has no FAILs", 0, int((dqs.status == "FAIL").sum()), group=g)

    # ---------------- report ----------------------------------------------
    res = pd.DataFrame(RESULTS)
    res.to_csv(os.path.join(OUT, "dp_uc30_verification_results.csv"), index=False)
    n = len(res)
    nf = int((res.status == "FAIL").sum())
    print("\n" + "=" * 74)
    print(f"VERIFICATION: {n - nf}/{n} PASS, {nf} FAIL")
    if nf:
        print("\nFailures:")
        print(res[res.status == "FAIL"].to_string(index=False))
    print("Results -> out/dp_uc30_verification_results.csv")
    print("=" * 74)
    return 1 if nf else 0


if __name__ == "__main__":
    sys.exit(main())
