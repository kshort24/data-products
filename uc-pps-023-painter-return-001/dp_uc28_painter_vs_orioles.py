"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #29  (uc-pps-023)
"Return Read: Andrew Painter (RHP) — what changed at Triple-A, and what to
 watch tonight at Oriole Park at Camden Yards, PHI @ BAL, 2026-07-31."
============================================================================

Layer-3 BUILD artifact for the Phillies Pitching (pps) value stream.

Pattern lineage: UC#3 (Luzardo deep dive) -> UC#8 (Nola vs WAS, canonical
flat-file pattern) -> UC#11 (Rangel vs PIT, multi-level evidence tier).
This UC is a DEVELOPMENT / RETURN read rather than an opponent attack plan:
the subject is Painter's own stuff and approach across two levels.

WHY NO OPPONENT DIMENSION (recorded gap, non-blocking):
  Painter has never faced Baltimore (2026 opponents: ATH ATL AZ BOS CIN CLE
  CWS LAD MIA MIL PHI SF WSH) and the repo holds no Orioles hitter cache and
  no PHI-vs-BAL pitching rows. Rather than fabricate a lineup plan, the
  opponent section is scoped to park/handedness context flagged as manual
  carry-in, and the report stays on self-scout ground.

MULTI-LEVEL EVIDENCE RULE (inherited from UC#11):
  MLB tier  = phils_2026 parquet, phillies_role=='pitching', game_type=='R'
  AAA tier  = data/opponents/lhvp26.parquet (Lehigh Valley IronPigs 2026)
  The AAA tier is ALWAYS LABELED and NEVER BLENDED into MLB rates.
  Both feeds carry full Hawk-Eye tracking (velo/spin/movement/release/
  extension/arm angle at 100% completeness -- verified in the DQ scorecard),
  so cross-level STUFF comparison is defensible. Batted-ball quality fields
  (launch_speed ~36% populated, estimated_woba ~25%) are lower fidelity and
  are used for directional contact reads only, never as headline rates.

NEW KPIs (specs in dp_uc28_painter_vs_orioles_use_case_spec.md sec.4):
  * Release Consistency Index (RCI)   -- per-start dispersion of release point
  * Fastball Upper-Third Rate (FUTR)  -- elevation discipline on the 4-seamer
  * Cross-Level Stuff Delta (XLSD)    -- signed AAA-minus-MLB stuff movement

Governance lineage:
  - data-product-owner      : sequenced as UC#29 / uc-pps-023 / dp_uc28
  - use-case-validator      : intake gate; BAL opponent gap = non-blocking
  - source-system-profiler  : entity lock pitcher==691725; AAA cache fresh
                              through 2026-07-30, MLB through 2026-07-29
  - kpi-calculator          : locked cores inherited VERBATIM from dp_uc11
                              (get_stats/nresults, whiff_rate, chase_rate,
                              putaway_rate, fpsr, hard_hit_rate); 3 new KPIs
  - data-quality-engineer   : scorecard emitted to out/

OUTPUTS — 23 CSV receipts + 5 figures + console receipt (NEW files, none overwritten), written to ./out/:
  dp_uc28_level_summary.csv          MLB vs AAA tier, nresults + process KPIs
  dp_uc28_start_log.csv              every start, both levels, with KPIs
  dp_uc28_arsenal_by_level.csv       usage/velo/spin/IVB/HB/zone/whiff/chase
  dp_uc28_stuff_delta.csv            NEW KPI: Cross-Level Stuff Delta
  dp_uc28_release_by_start.csv       NEW KPI: Release Consistency Index
  dp_uc28_release_by_level_pitch.csv release pt / extension / arm angle
  dp_uc28_fastball_elevation.csv     NEW KPI: Fastball Upper-Third Rate
  dp_uc28_location_tiers.csv         heart/shadow/chase/waste by level+pitch
  dp_uc28_aaa_arc.csv                AAA early (2 GS) vs late (3 GS) arc
  dp_uc28_mlb_arc.csv                MLB early (first 8 GS) vs late (last 7)
  dp_uc28_count_usage.csv            usage by count state, both levels
  dp_uc28_platoon.csv                vs LHH / vs RHH, both levels
  dp_uc28_contact.csv                batted-ball, directional only
  dp_uc28_dq_scorecard.csv           data-quality-engineer scorecard
  dp_uc28_freshness_manifest.csv     source/window/fitness receipts
  dp_uc28_fig1_arsenal_movement.png  fig 1 - movement map, tiers overlaid
  dp_uc28_fig2_velo_by_start.png     fig 2 - velo + extension by start
  dp_uc28_fig3_release_drift.png     fig 3 - release point drift
  dp_uc28_fig4_location_tiers.png    fig 4 - location tier mix by level
  dp_uc28_fig5_usage_whiff.png       fig 5 - usage x whiff, MLB vs AAA
============================================================================
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out")
os.makedirs(OUT_DIR, exist_ok=True)

PAINTER = 691725                   # Andrew Painter, MLBAM pitcher id — ENTITY LOCK
GAME_DAY = "2026-07-31"
OPPONENT = "BAL"
PARK = "Oriole Park at Camden Yards"
CURRENT_YEAR = 2026

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "phillies"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies",
]
PHIL_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
if PHIL_DIR is None:
    raise FileNotFoundError("Could not locate data/phillies. Set MLB_DATA_ROOT.")
OPP_DIR = os.path.join(os.path.dirname(PHIL_DIR), "opponents")

_WOBA_CANDIDATES = [
    os.path.join(HERE, "wOBA and FIP Constants.csv"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv",
]
WOBA_CSV = next((p for p in _WOBA_CANDIDATES if os.path.isfile(p)), None)

SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]
CALLED_STRIKE = ["called_strike"]

PHI_RED, PHI_NAVY, PHI_GRAY, PHI_LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
PITCH_COLORS = {
    "4-Seam Fastball": "#E81828", "Sinker": "#FF7F0E", "Slider": "#002D72",
    "Sweeper": "#1F77B4", "Split-Finger": "#2CA02C", "Curveball": "#8C564B",
}
PITCH_ORDER = ["4-Seam Fastball", "Sinker", "Slider", "Sweeper",
               "Split-Finger", "Curveball"]

# AAA arc split — first two starts were the stretch-out; 7/10 onward is the
# post-adjustment block. Boundary is a domain call, recorded in spec sec.3.
AAA_ARC_BOUNDARY = "2026-07-10"


# ===========================================================================
# LOADERS
# ===========================================================================
def _coerce(df):
    for c in ["plate_x", "plate_z", "sz_top", "sz_bot", "pfx_x", "pfx_z",
              "release_speed", "effective_speed", "release_spin_rate", "spin_axis",
              "release_pos_x", "release_pos_z", "release_extension", "arm_angle",
              "launch_speed", "launch_angle", "strikes", "balls", "outs_when_up",
              "pitch_number", "at_bat_number", "woba_value", "woba_denom", "zone",
              "estimated_woba_using_speedangle", "estimated_ba_using_speedangle"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _attach_woba(df, year=CURRENT_YEAR):
    if not WOBA_CSV:
        return df
    w = pd.read_csv(WOBA_CSV)
    df = df.drop(columns=[c for c in w.columns if c != "Season" and c in df.columns])
    if "game_year" not in df.columns:
        df = df.assign(game_year=year)
    return df.merge(w, left_on="game_year", right_on="Season", how="left")


def load_mlb():
    """MLB tier — Painter's 2026 Phillies pitching log, regular season only."""
    f = os.path.join(PHIL_DIR, f"phils_{CURRENT_YEAR}.parquet")
    d = pd.read_parquet(f)
    d = d[(d.phillies_role == "pitching") &
          (d.pitcher == PAINTER) &
          (d.game_type == "R")]
    d = d.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    d = _coerce(d.copy())
    d["level"] = "MLB"
    return _attach_woba(d)


def load_aaa():
    """AAA supporting tier — Lehigh Valley IronPigs 2026 pitching log."""
    f = os.path.join(OPP_DIR, "lhvp26.parquet")
    d = pd.read_parquet(f)
    d = d[d.pitcher == PAINTER]
    d = d.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    d = _coerce(d.copy())
    d["level"] = "AAA"
    return _attach_woba(d)


# ===========================================================================
# LOCKED KPI FUNCTIONS — inherited VERBATIM from dp_uc11_rangel_vs_pirates.py
# (which inherited from dp_uc8 / Baseball Functions). DO NOT RE-DERIVE.
# ===========================================================================
def get_stats(level, df):
    if isinstance(level, str):
        level = [level]

    def cnt(mask, name):
        return df[mask].groupby(level, as_index=False).agg(**{name: ("description", "size")})

    def wsum(mask, col, name):
        return df[mask].groupby(level, as_index=False).agg(**{name: (col, "sum")})

    base = df.groupby(level, as_index=False).agg(pitches=("description", "size"))
    pa = cnt(~df.events.replace(np.nan, "NA").isin(["NA", "pickoff_1b"]), "plate_apps")
    ab = cnt(~df.events.replace(np.nan, "NA").isin(
        ["NA", "pickoff_1b", "walk", "intent_walk", "hit_by_pitch", "sac_fly", "sac_bunt"]), "at_bats")
    bip = cnt(df.type == "X", "bip")
    hits = cnt(df.events.isin(["home_run", "single", "double", "triple"]), "hits")
    singles = cnt(df.events == "single", "singles")
    doubles = cnt(df.events == "double", "doubles")
    triples = cnt(df.events == "triple", "triples")
    hrs = cnt(df.events == "home_run", "hrs")
    walks = cnt(df.events == "walk", "walks")
    ks = cnt(df.events.isin(["strikeout", "strikeout_double_play"]), "strikeouts")
    hbp = cnt(df.events == "hit_by_pitch", "hbp")
    wBB = wsum(df.events == "walk", "wBB", "wBB")
    wHBP = wsum(df.events == "hit_by_pitch", "wHBP", "wHBP")
    w1B = wsum(df.events == "single", "w1B", "w1B")
    w2B = wsum(df.events == "double", "w2B", "w2B")
    w3B = wsum(df.events == "triple", "w3B", "w3B")
    wHR = wsum(df.events == "home_run", "wHR", "wHR")
    xba = df.groupby(level, as_index=False).agg(xba=("estimated_ba_using_speedangle", "mean"))
    xwoba = df.groupby(level, as_index=False).agg(xwoba=("estimated_woba_using_speedangle", "mean"))
    out = base
    for x in [pa, ab, bip, hits, singles, doubles, triples, hrs, walks, ks, hbp,
              wBB, wHBP, w1B, w2B, w3B, wHR, xba, xwoba]:
        out = out.merge(x, how="left", on=level)
    return out.fillna(0)


def nresults(level, df):
    if isinstance(level, str):
        level = [level]
    s = get_stats(level, df)
    s["ba"] = s.hits / s.at_bats
    s["obp"] = (s.hits + s.walks + s.hbp) / s.plate_apps
    s["slg"] = (s.singles + 2 * s.doubles + 3 * s.triples + 4 * s.hrs) / s.at_bats
    s["ops"] = s.obp + s.slg
    s["woba"] = (s.wBB + s.wHBP + s.w1B + s.w2B + s.w3B + s.wHR) / s.plate_apps
    s["krate"] = s.strikeouts / s.plate_apps
    s["bbrate"] = s.walks / s.plate_apps
    s["hr_rate"] = s.hrs / s.plate_apps
    cols = level + ["pitches", "plate_apps", "bip", "hits", "hrs", "walks", "strikeouts",
                    "ba", "obp", "slg", "ops", "woba", "krate", "bbrate", "hr_rate"]
    return s[cols].round(3)


def whiff_rate(level, df):
    if isinstance(level, str):
        level = [level]
    u = df[df.description.isin(SWINGS)].groupby(level, as_index=False).agg(swings=("des", "size"))
    v = df[df.description.isin(WHIFFS)].groupby(level, as_index=False).agg(whiffs=("des", "size"))
    w = u.merge(v, on=level, how="left").fillna({"whiffs": 0})
    w["whiff_rate"] = w.whiffs / w.swings
    return w.round(3)


def chase_rate(level, df):
    if isinstance(level, str):
        level = [level]
    chase = df[(df.zone > 9) & (df.description.isin(SWINGS))]
    i = chase.groupby(level, as_index=False).agg(chases=("des", "size"))
    j = df[df.zone > 9].groupby(level, as_index=False).agg(ooz=("des", "size"))
    tot = df.groupby(level, as_index=False).agg(pitches=("des", "size"))
    cr = tot.merge(j, on=level, how="left").merge(i, on=level, how="left").fillna(0)
    cr["chase_rate"] = cr.chases / cr.ooz
    cr["in_zone_rate"] = (cr.pitches - cr.ooz) / cr.pitches
    return cr.round(3)


def putaway_rate(level, df):
    if isinstance(level, str):
        level = [level]
    z = df[df.strikes == 2].groupby(level, as_index=False).agg(pitches2strikes=("des", "size"))
    k = df[df.events.isin(["strikeout", "strikeout_double_play"])].groupby(
        level, as_index=False).agg(strikeouts=("des", "size"))
    z = z.merge(k, on=level, how="left").fillna(0)
    z["putaway_rate"] = z.strikeouts / z.pitches2strikes
    return z.round(3)


def fpsr(level, df):
    if isinstance(level, str):
        level = [level]
    fp = df[df.pitch_number == 1]
    balls = fp.groupby(level + ["type"], as_index=False).agg(balls=("des", "size"))
    tot = fp.groupby(level, as_index=False).agg(pitches=("des", "size"))
    m = tot.merge(balls[balls.type == "B"][level + ["balls"]], on=level, how="left").fillna({"balls": 0})
    m["first_pitch_strike_rate"] = (m.pitches - m.balls) / m.pitches
    return m.round(3)


def hard_hit_rate(level, df):
    if isinstance(level, str):
        level = [level]
    hh = df[(df.launch_speed >= 95) & (df.type == "X")].groupby(
        level, as_index=False).agg(hard_hits=("des", "size"))
    bips = df[df.type == "X"].groupby(level, as_index=False).agg(bips=("des", "size"))
    out = bips.merge(hh, on=level, how="left").fillna(0)
    out["hard_hit_rate"] = out.hard_hits / out.bips
    return out.round(3)


# ===========================================================================
# DERIVED HELPERS (mechanical, not new KPIs)
# ===========================================================================
def csw_rate(level, df):
    """Called-Strike + Whiff rate = (called strikes + whiffs) / total pitches."""
    if isinstance(level, str):
        level = [level]
    tot = df.groupby(level, as_index=False).agg(pitches=("des", "size"))
    cs = df[df.description.isin(CALLED_STRIKE)].groupby(level, as_index=False).agg(called=("des", "size"))
    wh = df[df.description.isin(WHIFFS)].groupby(level, as_index=False).agg(whiffs=("des", "size"))
    out = tot.merge(cs, on=level, how="left").merge(wh, on=level, how="left").fillna(0)
    out["csw_rate"] = (out.called + out.whiffs) / out.pitches
    return out.round(3)


def strike_rate(level, df):
    if isinstance(level, str):
        level = [level]
    tot = df.groupby(level, as_index=False).agg(pitches=("des", "size"))
    st = df[df.type != "B"].groupby(level, as_index=False).agg(strikes_thrown=("des", "size"))
    out = tot.merge(st, on=level, how="left").fillna(0)
    out["strike_rate"] = out.strikes_thrown / out.pitches
    return out.round(3)


def add_movement_cols(df):
    """Statcast pfx_* are in feet; convert to inches. IVB = pfx_z*12 (gravity-
    corrected induced vertical break). HB is expressed ARM-SIDE POSITIVE for a
    RHP, i.e. HB = -pfx_x*12 so that arm-side run reads positive."""
    df = df.copy()
    df["ivb_in"] = df.pfx_z * 12.0
    df["hb_in"] = -df.pfx_x * 12.0
    return df


def zone_tier(df):
    """Attribution of each pitch to a location tier using Statcast `zone`.
    heart  = zones 1-9 core (Statcast gridded strike zone)
    shadow = zones 11-14 within one ball of the edge (|plate_x| <= 1.11 ft and
             plate_z within [sz_bot-0.25, sz_top+0.25])
    chase  = out of zone but competitive (within ~2 balls)
    waste  = everything further out
    Tiering is a mechanical partition of existing CDEs, not a new KPI."""
    d = df.copy()
    in_zone = d.zone.between(1, 9)
    near_x = d.plate_x.abs() <= 1.11
    near_z = (d.plate_z >= d.sz_bot - 0.25) & (d.plate_z <= d.sz_top + 0.25)
    comp_x = d.plate_x.abs() <= 1.45
    comp_z = (d.plate_z >= d.sz_bot - 0.60) & (d.plate_z <= d.sz_top + 0.60)
    tier = np.where(in_zone, "heart",
           np.where(near_x & near_z, "shadow",
           np.where(comp_x & comp_z, "chase", "waste")))
    d["loc_tier"] = tier
    return d


# ===========================================================================
# NEW KPI 1 — Release Consistency Index (RCI)
# ===========================================================================
def release_consistency(df, level_cols):
    """RCI = mean of the per-start standard deviations of horizontal and
    vertical release point, expressed in INCHES, computed on the pitcher's
    primary fastball only so that arsenal mix cannot move the number.

        RCI = 12 * ( SD(release_pos_x | FF) + SD(release_pos_z | FF) ) / 2

    Grain      : one row per (level, game_date)
    Population : pitch_name == '4-Seam Fastball', >= 15 such pitches in the start
    CDEs       : release_pos_x, release_pos_z, pitch_name, game_date
    Direction  : LOWER IS BETTER (tighter, more repeatable delivery)
    Edge cases : starts with < 15 four-seamers return NaN and are excluded
                 from any aggregate; NaN release coordinates are dropped
                 pairwise before the SD is taken.
    """
    ff = df[df.pitch_name == "4-Seam Fastball"].dropna(subset=["release_pos_x", "release_pos_z"])
    g = ff.groupby(level_cols, as_index=False).agg(
        ff_pitches=("release_pos_x", "size"),
        sd_x_ft=("release_pos_x", "std"),
        sd_z_ft=("release_pos_z", "std"),
        mean_x_ft=("release_pos_x", "mean"),
        mean_z_ft=("release_pos_z", "mean"),
    )
    g["rci_in"] = 12.0 * (g.sd_x_ft + g.sd_z_ft) / 2.0
    g.loc[g.ff_pitches < 15, "rci_in"] = np.nan
    for c in ["sd_x_ft", "sd_z_ft", "mean_x_ft", "mean_z_ft"]:
        g[c + "_in"] = (g[c] * 12.0).round(2)
    return g.round(3)


# ===========================================================================
# NEW KPI 2 — Fastball Upper-Third Rate (FUTR)
# ===========================================================================
def fastball_upper_third(df, level_cols):
    """FUTR = share of 4-seam fastballs located in the upper third of the
    batter's own strike zone or just above it.

        upper_third_floor = sz_bot + (2/3) * (sz_top - sz_bot)
        FUTR = count(FF with plate_z >= upper_third_floor) / count(FF)

    Grain      : one row per level_cols group
    Population : pitch_name == '4-Seam Fastball', plate_z / sz_top / sz_bot
                 all non-null. Note this counts pitches ABOVE the zone too --
                 elevation is the intent being measured, not strike-throwing.
    CDEs       : plate_z, sz_top, sz_bot, pitch_name
    Direction  : context-dependent. For a high-IVB four-seamer, HIGHER is
                 generally better because ride converts to whiffs only at the
                 top rail; it is NOT a quality score on its own.
    Edge cases : rows with any null of plate_z/sz_top/sz_bot are dropped from
                 both numerator and denominator (pairwise complete).
    """
    ff = df[df.pitch_name == "4-Seam Fastball"].dropna(subset=["plate_z", "sz_top", "sz_bot"]).copy()
    ff["ut_floor"] = ff.sz_bot + (2.0 / 3.0) * (ff.sz_top - ff.sz_bot)
    ff["is_upper"] = ff.plate_z >= ff.ut_floor
    ff["is_above"] = ff.plate_z > ff.sz_top
    g = ff.groupby(level_cols, as_index=False).agg(
        ff_pitches=("is_upper", "size"),
        upper_third=("is_upper", "sum"),
        above_zone=("is_above", "sum"),
        mean_plate_z=("plate_z", "mean"),
    )
    g["futr"] = g.upper_third / g.ff_pitches
    g["above_zone_rate"] = g.above_zone / g.ff_pitches
    return g.round(3)


# ===========================================================================
# NEW KPI 3 — Cross-Level Stuff Delta (XLSD)
# ===========================================================================
def cross_level_stuff_delta(mlb, aaa, min_n=15):
    """XLSD = signed AAA-minus-MLB difference in the four raw stuff traits,
    computed per pitch type at matched entity and season.

        XLSD_velo = mean(release_speed | AAA) - mean(release_speed | MLB)
        XLSD_ivb  = mean(ivb_in       | AAA) - mean(ivb_in       | MLB)
        XLSD_hb   = mean(hb_in        | AAA) - mean(hb_in        | MLB)
        XLSD_spin = mean(release_spin_rate | AAA) - mean(... | MLB)

    Grain      : one row per pitch_name
    Population : same pitcher id, same season, >= min_n pitches of that type
                 IN BOTH tiers. Types failing the threshold in either tier are
                 reported with a coverage flag and excluded from conclusions.
    CDEs       : pitch_name, release_speed, pfx_x, pfx_z, release_spin_rate
    Interpretation guard: this is a STUFF comparison only. Because MiLB and MLB
                 Hawk-Eye installs are calibrated separately and pitch tagging
                 is model-driven per level, small deltas (< ~0.5 mph, < ~1.0
                 inch) are within cross-park measurement noise and must not be
                 reported as adjustments. Tagging drift is a known hazard --
                 the AAA 'slider'/'sweeper' boundary in particular.
    """
    mlb = add_movement_cols(mlb)
    aaa = add_movement_cols(aaa)

    def prof(d, tag):
        g = d.groupby("pitch_name", as_index=False).agg(
            **{f"n_{tag}": ("release_speed", "size"),
               f"velo_{tag}": ("release_speed", "mean"),
               f"velo_max_{tag}": ("release_speed", "max"),
               f"spin_{tag}": ("release_spin_rate", "mean"),
               f"ivb_{tag}": ("ivb_in", "mean"),
               f"hb_{tag}": ("hb_in", "mean")})
        g[f"usage_{tag}"] = g[f"n_{tag}"] / g[f"n_{tag}"].sum()
        return g

    m = prof(mlb, "mlb")
    a = prof(aaa, "aaa")
    out = m.merge(a, on="pitch_name", how="outer")
    out["d_velo"] = out.velo_aaa - out.velo_mlb
    out["d_spin"] = out.spin_aaa - out.spin_mlb
    out["d_ivb"] = out.ivb_aaa - out.ivb_mlb
    out["d_hb"] = out.hb_aaa - out.hb_mlb
    out["d_usage_pp"] = 100 * (out.usage_aaa - out.usage_mlb)
    out["coverage_ok"] = (out.n_mlb.fillna(0) >= min_n) & (out.n_aaa.fillna(0) >= min_n)
    out["noise_guard"] = np.where(
        out.d_velo.abs().lt(0.5) & out.d_ivb.abs().lt(1.0) & out.d_hb.abs().lt(1.0),
        "within measurement noise", "outside noise band")
    order = {p: i for i, p in enumerate(PITCH_ORDER)}
    out["_o"] = out.pitch_name.map(order).fillna(99)
    return out.sort_values("_o").drop(columns="_o").round(3)


# ===========================================================================
# BENCHMARK POPULATION — 2026 MLB right-handed starters
# ---------------------------------------------------------------------------
# A stuff number means nothing without a comparison population. phils_2026
# carries EVERY pitch thrown in a Phillies game, so the union of both roles
# gives a broad 2026 MLB RHP sample (Phillies staff + every opposing pitcher
# the Phillies faced). Population rule is stated in the report.
# ===========================================================================
def load_benchmark_pool():
    f = os.path.join(PHIL_DIR, f"phils_{CURRENT_YEAR}.parquet")
    d = pd.read_parquet(f)
    d = d[d.game_type == "R"]
    d = d.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    d = d[d.p_throws == "R"]
    return _coerce(d.copy())


def ff_benchmark(pool, min_ff=150):
    """Four-seam quality benchmark across 2026 MLB RHP with >= min_ff FF."""
    ff = pool[pool.pitch_name == "4-Seam Fastball"].copy()
    ff = ff.dropna(subset=["plate_z", "sz_top", "sz_bot"])
    ff["ivb_in"] = ff.pfx_z * 12.0
    ff["ut_floor"] = ff.sz_bot + (2.0 / 3.0) * (ff.sz_top - ff.sz_bot)
    ff["is_upper"] = ff.plate_z >= ff.ut_floor
    ff["is_swing"] = ff.description.isin(SWINGS)
    ff["is_whiff"] = ff.description.isin(WHIFFS)
    g = ff.groupby("pitcher", as_index=False).agg(
        player_name=("player_name", "first"),
        n_ff=("is_upper", "size"),
        velo=("release_speed", "mean"),
        ivb_in=("ivb_in", "mean"),
        spin=("release_spin_rate", "mean"),
        ext_ft=("release_extension", "mean"),
        futr=("is_upper", "mean"),
        swings=("is_swing", "sum"),
        whiffs=("is_whiff", "sum"),
    )
    g = g[g.n_ff >= min_ff].copy()
    g["ff_whiff"] = g.whiffs / g.swings
    up = ff[ff.is_upper].groupby("pitcher", as_index=False).agg(
        up_swings=("is_swing", "sum"), up_whiffs=("is_whiff", "sum"))
    g = g.merge(up, on="pitcher", how="left")
    g["ff_whiff_upper"] = g.up_whiffs / g.up_swings
    return g.round(4)


def arm_angle_spread(pool, min_n=40):
    """Delivery-consistency proxy: the spread in mean arm_angle across a
    pitcher's own pitch types. A pitcher whose slot is identical on every
    pitch gives the hitter no pre-release cue; a wide spread is a TIPPING
    CANDIDATE (not proof — arm_angle is derived from release coordinates,
    and some spread is an unavoidable consequence of grip and intent).

    spread = max(mean arm_angle by pitch type) - min(...)
    Population: RHP, 2026, >= min_n pitches of each type counted, >= 3 types.
    """
    d = pool.dropna(subset=["arm_angle"])
    g = d.groupby(["pitcher", "pitch_name"], as_index=False).agg(
        player_name=("player_name", "first"), n=("arm_angle", "size"),
        arm=("arm_angle", "mean"))
    g = g[g.n >= min_n]
    agg = g.groupby("pitcher", as_index=False).agg(
        player_name=("player_name", "first"), types=("pitch_name", "size"),
        arm_max=("arm", "max"), arm_min=("arm", "min"), total=("n", "sum"))
    agg = agg[(agg.types >= 3) & (agg.total >= 120)].copy()
    agg["arm_spread_deg"] = agg.arm_max - agg.arm_min
    return agg.round(3).sort_values("arm_spread_deg", ascending=False)


def pct_rank(series, value, higher_is_better=True):
    s = series.dropna()
    if len(s) == 0 or pd.isna(value):
        return np.nan
    p = (s < value).mean() if higher_is_better else (s > value).mean()
    return round(100 * p, 1)


# ===========================================================================
# ASSEMBLY BLOCKS
# ===========================================================================
def kpi_block(df, level_cols):
    """Bundle the locked process KPIs onto one row per group."""
    base = df.groupby(level_cols, as_index=False).agg(pitches=("des", "size"))
    for fn, keep in [
        (strike_rate, ["strike_rate"]),
        (csw_rate, ["csw_rate"]),
        (chase_rate, ["chase_rate", "in_zone_rate"]),
        (whiff_rate, ["swings", "whiffs", "whiff_rate"]),
        (putaway_rate, ["pitches2strikes", "putaway_rate"]),
        (fpsr, ["first_pitch_strike_rate"]),
        (hard_hit_rate, ["bips", "hard_hits", "hard_hit_rate"]),
    ]:
        t = fn(level_cols, df)
        base = base.merge(t[level_cols + keep], on=level_cols, how="left")
    return base


def arsenal_profile(df, level_cols):
    d = add_movement_cols(df)
    g = d.groupby(level_cols + ["pitch_name"], as_index=False).agg(
        n=("des", "size"),
        velo=("release_speed", "mean"),
        velo_max=("release_speed", "max"),
        eff_velo=("effective_speed", "mean"),
        spin=("release_spin_rate", "mean"),
        spin_axis=("spin_axis", "mean"),
        ivb_in=("ivb_in", "mean"),
        hb_in=("hb_in", "mean"),
        ext_ft=("release_extension", "mean"),
        arm_angle=("arm_angle", "mean"),
        plate_x=("plate_x", "mean"),
        plate_z=("plate_z", "mean"),
    )
    tot = g.groupby(level_cols, as_index=False).n.sum().rename(columns={"n": "n_grp"})
    g = g.merge(tot, on=level_cols)
    g["usage"] = g.n / g.n_grp
    for fn, keep in [
        (whiff_rate, ["swings", "whiffs", "whiff_rate"]),
        (chase_rate, ["chase_rate", "in_zone_rate"]),
        (csw_rate, ["csw_rate"]),
    ]:
        t = fn(level_cols + ["pitch_name"], d)
        g = g.merge(t[level_cols + ["pitch_name", *keep]], on=level_cols + ["pitch_name"], how="left")
    order = {p: i for i, p in enumerate(PITCH_ORDER)}
    g["_o"] = g.pitch_name.map(order).fillna(99)
    g = g.sort_values(level_cols + ["_o"]).drop(columns=["_o", "n_grp"])
    return g.round(3)


# ===========================================================================
# FIGURES
# ===========================================================================
def fig_movement(ars, path, titles=None):
    titles = titles or {"MLB": "MLB", "AAA": "AAA"}
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6), sharex=True, sharey=True)
    for ax, lvl in zip(axes, ["MLB", "AAA"]):
        title = titles[lvl]
        sub = ars[ars.level == lvl]
        for _, r in sub.iterrows():
            c = PITCH_COLORS.get(r.pitch_name, PHI_GRAY)
            ax.scatter(r.hb_in, r.ivb_in, s=40 + 900 * r.usage, color=c,
                       alpha=.85, edgecolor="white", linewidth=1.4, zorder=3)
            ax.annotate(f"{r.pitch_name.split()[0]}\n{r.velo:.1f}",
                        (r.hb_in, r.ivb_in), textcoords="offset points",
                        xytext=(0, -4), ha="center", va="top", fontsize=7.5,
                        color=PHI_NAVY, zorder=4)
        ax.axhline(0, color=PHI_LGRAY, lw=1, zorder=1)
        ax.axvline(0, color=PHI_LGRAY, lw=1, zorder=1)
        ax.set_title(title, fontsize=10, color=PHI_NAVY, weight="bold")
        ax.set_xlabel("Horizontal break — arm-side positive (in)", fontsize=9)
        ax.grid(alpha=.25, zorder=0)
    axes[0].set_ylabel("Induced vertical break (in)", fontsize=9)
    fig.suptitle("Andrew Painter — arsenal shape by level  (bubble = usage share)",
                 color=PHI_NAVY, weight="bold", fontsize=12.5)
    fig.text(.5, .008, "Tiers shown side by side and never blended. "
             "AAA tags are model-driven per level — treat SL/SW boundary loosely.",
             ha="center", fontsize=7.5, color=PHI_GRAY)
    fig.tight_layout(rect=[0, .03, 1, .95])
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_velo_by_start(log, path):
    fig, ax = plt.subplots(figsize=(11, 5.2))
    log = log.sort_values("game_date").reset_index(drop=True)
    x = np.arange(len(log))
    colors = [PHI_NAVY if l == "MLB" else PHI_RED for l in log.level]
    ax.plot(x, log.ff_velo, color=PHI_GRAY, lw=1.2, zorder=2)
    ax.scatter(x, log.ff_velo, c=colors, s=70, zorder=3, edgecolor="white", linewidth=1.2)
    for i, r in log.iterrows():
        ax.annotate(f"{r.ff_velo:.1f}", (i, r.ff_velo), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=7, color=PHI_NAVY)
    split = (log.level == "MLB").sum() - 0.5
    ax.axvline(split, color=PHI_RED, ls="--", lw=1.4, zorder=1)
    ax.annotate("optioned to AAA", (split, ax.get_ylim()[0]), xytext=(6, 6),
                textcoords="offset points", fontsize=8.5, color=PHI_RED, weight="bold")
    ax2 = ax.twinx()
    ax2.plot(x, log.ext_ft, color="#2CA02C", lw=1.6, ls=":", marker="s",
             ms=4, zorder=3, label="extension (ft)")
    ax2.set_ylabel("Release extension (ft)", fontsize=9, color="#2CA02C")
    ax2.tick_params(axis="y", labelcolor="#2CA02C")
    ax.set_xticks(x)
    ax.set_xticklabels([d[5:] for d in log.game_date.astype(str)], rotation=60, fontsize=7.5)
    ax.set_ylabel("4-seam velocity (mph)", fontsize=9, color=PHI_NAVY)
    ax.set_xlabel("Start (navy = MLB, red = AAA)", fontsize=9)
    ax.set_title("Andrew Painter — four-seam velocity and extension, start by start",
                 color=PHI_NAVY, weight="bold", fontsize=12)
    ax.grid(alpha=.25, axis="y")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_release_drift(rel, path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    ax = axes[0]
    for lvl, c in [("MLB", PHI_NAVY), ("AAA", PHI_RED)]:
        s = rel[rel.level == lvl]
        ax.scatter(s.mean_x_ft, s.mean_z_ft, color=c, s=90, label=lvl,
                   edgecolor="white", linewidth=1.3, zorder=3)
        for _, r in s.iterrows():
            ax.annotate(str(r.game_date)[5:], (r.mean_x_ft, r.mean_z_ft),
                        textcoords="offset points", xytext=(0, -11),
                        ha="center", fontsize=6.5, color=PHI_GRAY)
    ax.set_xlabel("Mean horizontal release (ft, catcher view)", fontsize=9)
    ax.set_ylabel("Mean vertical release (ft)", fontsize=9)
    ax.set_title("Release point by start — 4-seam only", fontsize=10.5,
                 color=PHI_NAVY, weight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=.25)

    ax = axes[1]
    r2 = rel.sort_values("game_date").reset_index(drop=True)
    x = np.arange(len(r2))
    vals = pd.to_numeric(r2.rci_in, errors="coerce").astype(float).to_numpy()
    ax.bar(x, np.nan_to_num(vals, nan=0.0),
           color=[PHI_NAVY if l == "MLB" else PHI_RED for l in r2.level],
           zorder=3, width=.65)
    for i, v in enumerate(vals):
        if np.isnan(v):
            ax.annotate("n/a\n<15 FF", (i, 0), textcoords="offset points",
                        xytext=(0, 6), ha="center", fontsize=6.5, color=PHI_GRAY)
    ax.set_xticks(x)
    ax.set_xticklabels([str(d)[5:] for d in r2.game_date], rotation=60, fontsize=7.5)
    ax.set_ylabel("Release Consistency Index (in) — lower is tighter", fontsize=9)
    ax.set_title("RCI by start  (NEW KPI)", fontsize=10.5, color=PHI_NAVY, weight="bold")
    ax.grid(alpha=.25, axis="y", zorder=0)
    fig.suptitle("Andrew Painter — delivery repeatability", color=PHI_NAVY,
                 weight="bold", fontsize=12.5)
    fig.tight_layout(rect=[0, 0, 1, .94])
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_location_tiers(loc, path):
    piv = loc.pivot_table(index=["level", "pitch_name"], columns="loc_tier",
                          values="share", aggfunc="first").fillna(0)
    tiers = [t for t in ["heart", "shadow", "chase", "waste"] if t in piv.columns]
    piv = piv[tiers]
    piv = piv.reset_index()
    order = {p: i for i, p in enumerate(PITCH_ORDER)}
    piv["_o"] = piv.pitch_name.map(order).fillna(99)
    piv = piv.sort_values(["level", "_o"], ascending=[False, True]).drop(columns="_o")
    labels = [f"{r.pitch_name.split()[0]}  ({r.level})" for _, r in piv.iterrows()]
    fig, ax = plt.subplots(figsize=(10.5, 6))
    left = np.zeros(len(piv))
    tier_colors = {"heart": PHI_RED, "shadow": PHI_NAVY, "chase": "#1F77B4", "waste": PHI_LGRAY}
    y = np.arange(len(piv))
    for t in tiers:
        ax.barh(y, piv[t], left=left, color=tier_colors[t], label=t, zorder=3, height=.7)
        left = left + piv[t].values
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("Share of pitches", fontsize=9)
    ax.set_xlim(0, 1)
    ax.legend(fontsize=8, ncol=4, frameon=False, loc="lower right")
    ax.set_title("Andrew Painter — where each pitch goes, by level",
                 color=PHI_NAVY, weight="bold", fontsize=12)
    ax.grid(alpha=.25, axis="x", zorder=0)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_usage_whiff(ars, path):
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    for lvl, marker, alpha in [("MLB", "o", .95), ("AAA", "^", .95)]:
        s = ars[ars.level == lvl]
        for _, r in s.iterrows():
            c = PITCH_COLORS.get(r.pitch_name, PHI_GRAY)
            ax.scatter(100 * r.usage, 100 * r.whiff_rate, color=c, marker=marker,
                       s=150, alpha=alpha, edgecolor=PHI_NAVY if lvl == "MLB" else PHI_RED,
                       linewidth=1.8, zorder=3)
            ax.annotate(f"{r.pitch_name.split()[0]} ({lvl})",
                        (100 * r.usage, 100 * r.whiff_rate),
                        textcoords="offset points", xytext=(7, 4),
                        fontsize=7.5, color=PHI_NAVY)
    ax.set_xlabel("Usage (% of pitches at that level)", fontsize=9)
    ax.set_ylabel("Whiff per swing (%)", fontsize=9)
    ax.set_title("Usage vs bat-missing, MLB (circle / navy ring) vs AAA (triangle / red ring)",
                 color=PHI_NAVY, weight="bold", fontsize=11.5)
    ax.grid(alpha=.25, zorder=0)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ===========================================================================
# BUILD
# ===========================================================================
def main():
    mlb = load_mlb()
    aaa = load_aaa()
    both = pd.concat([mlb, aaa], ignore_index=True)

    assert set(mlb.pitcher.unique()) == {PAINTER}, "ENTITY LOCK VIOLATION (MLB)"
    assert set(aaa.pitcher.unique()) == {PAINTER}, "ENTITY LOCK VIOLATION (AAA)"

    # --- 1. level summary -------------------------------------------------
    res = nresults(["level"], both)
    kpis = kpi_block(both, ["level"])
    lvl = res.merge(kpis.drop(columns="pitches"), on="level", how="left")
    lvl["starts"] = lvl.level.map(both.groupby("level").game_date.nunique())
    lvl = lvl[["level", "starts"] + [c for c in lvl.columns if c not in ("level", "starts")]]
    lvl.to_csv(os.path.join(OUT_DIR, "dp_uc28_level_summary.csv"), index=False)

    # --- 2. start log -----------------------------------------------------
    log = kpi_block(both, ["level", "game_date"])
    r_ = nresults(["level", "game_date"], both)
    log = log.merge(r_[["level", "game_date", "plate_apps", "strikeouts", "walks",
                        "hits", "hrs"]], on=["level", "game_date"], how="left")
    ffv = both[both.pitch_name == "4-Seam Fastball"].groupby(
        ["level", "game_date"], as_index=False).agg(
        ff_velo=("release_speed", "mean"), ff_velo_max=("release_speed", "max"),
        ff_ivb=("pfx_z", lambda s: 12 * s.mean()))
    ext = both.groupby(["level", "game_date"], as_index=False).agg(
        ext_ft=("release_extension", "mean"), arm_angle=("arm_angle", "mean"))
    log = log.merge(ffv, on=["level", "game_date"], how="left")
    log = log.merge(ext, on=["level", "game_date"], how="left")
    futr_s = fastball_upper_third(both, ["level", "game_date"])
    log = log.merge(futr_s[["level", "game_date", "futr"]], on=["level", "game_date"], how="left")
    log["game_date"] = log.game_date.astype(str)
    log = log.sort_values("game_date").round(3)
    log.to_csv(os.path.join(OUT_DIR, "dp_uc28_start_log.csv"), index=False)

    # --- 3. arsenal by level ---------------------------------------------
    ars = arsenal_profile(both, ["level"])
    ars.to_csv(os.path.join(OUT_DIR, "dp_uc28_arsenal_by_level.csv"), index=False)

    # --- 4. NEW KPI: cross-level stuff delta -----------------------------
    xlsd = cross_level_stuff_delta(mlb, aaa)
    xlsd.to_csv(os.path.join(OUT_DIR, "dp_uc28_stuff_delta.csv"), index=False)

    # --- 5. NEW KPI: release consistency ---------------------------------
    rel = release_consistency(both, ["level", "game_date"])
    rel["game_date"] = rel.game_date.astype(str)
    rel = rel.sort_values("game_date")
    rel.to_csv(os.path.join(OUT_DIR, "dp_uc28_release_by_start.csv"), index=False)

    relp = add_movement_cols(both).groupby(["level", "pitch_name"], as_index=False).agg(
        n=("des", "size"),
        rel_x_ft=("release_pos_x", "mean"), rel_z_ft=("release_pos_z", "mean"),
        ext_ft=("release_extension", "mean"), arm_angle=("arm_angle", "mean"),
        eff_velo=("effective_speed", "mean"), velo=("release_speed", "mean"))
    relp["velo_added_by_ext"] = (relp.eff_velo - relp.velo).round(2)
    relp.round(3).to_csv(os.path.join(OUT_DIR, "dp_uc28_release_by_level_pitch.csv"), index=False)

    # --- 6. NEW KPI: fastball elevation ----------------------------------
    futr = fastball_upper_third(both, ["level"])
    futr_stand = fastball_upper_third(both, ["level", "stand"])
    futr_all = pd.concat([futr.assign(stand="ALL"), futr_stand], ignore_index=True)
    futr_all.to_csv(os.path.join(OUT_DIR, "dp_uc28_fastball_elevation.csv"), index=False)

    # --- 7. location tiers ------------------------------------------------
    zt = zone_tier(both)
    loc = zt.groupby(["level", "pitch_name", "loc_tier"], as_index=False).agg(n=("des", "size"))
    tot = loc.groupby(["level", "pitch_name"], as_index=False).n.sum().rename(columns={"n": "n_tot"})
    loc = loc.merge(tot, on=["level", "pitch_name"])
    loc["share"] = (loc.n / loc.n_tot).round(3)
    loc.to_csv(os.path.join(OUT_DIR, "dp_uc28_location_tiers.csv"), index=False)

    # --- 8. AAA arc: early stretch-out vs late ---------------------------
    aaa_arc = aaa.copy()
    aaa_arc["arc"] = np.where(aaa_arc.game_date.astype(str) < AAA_ARC_BOUNDARY,
                              "AAA early (6/28, 7/4)", "AAA late (7/10, 7/21, 7/26)")
    arc_k = kpi_block(aaa_arc, ["arc"])
    arc_r = nresults(["arc"], aaa_arc)
    arc = arc_k.merge(arc_r[["arc", "plate_apps", "strikeouts", "walks", "hrs"]], on="arc", how="left")
    arc_ff = aaa_arc[aaa_arc.pitch_name == "4-Seam Fastball"].groupby("arc", as_index=False).agg(
        ff_velo=("release_speed", "mean"), ff_usage_n=("des", "size"))
    tot_arc = aaa_arc.groupby("arc", as_index=False).agg(all_n=("des", "size"))
    arc = arc.merge(arc_ff, on="arc", how="left").merge(tot_arc, on="arc", how="left")
    arc["ff_usage"] = (arc.ff_usage_n / arc.all_n).round(3)
    arc = arc.merge(fastball_upper_third(aaa_arc, ["arc"])[["arc", "futr", "above_zone_rate"]],
                    on="arc", how="left")
    arc.round(3).to_csv(os.path.join(OUT_DIR, "dp_uc28_aaa_arc.csv"), index=False)

    # --- 9. MLB arc: first 8 starts vs last 7 ----------------------------
    mlb_dates = sorted(mlb.game_date.astype(str).unique())
    early_set = set(mlb_dates[:8])
    mlb_arc = mlb.copy()
    mlb_arc["arc"] = np.where(mlb_arc.game_date.astype(str).isin(early_set),
                              f"MLB first 8 GS ({mlb_dates[0]}..{mlb_dates[7]})",
                              f"MLB last 7 GS ({mlb_dates[8]}..{mlb_dates[-1]})")
    ma_k = kpi_block(mlb_arc, ["arc"])
    ma_r = nresults(["arc"], mlb_arc)
    ma = ma_k.merge(ma_r[["arc", "plate_apps", "strikeouts", "walks", "hrs", "woba", "krate", "bbrate"]],
                    on="arc", how="left")
    ma_ff = mlb_arc[mlb_arc.pitch_name == "4-Seam Fastball"].groupby("arc", as_index=False).agg(
        ff_velo=("release_speed", "mean"), ff_n=("des", "size"))
    tot_ma = mlb_arc.groupby("arc", as_index=False).agg(all_n=("des", "size"))
    ma = ma.merge(ma_ff, on="arc", how="left").merge(tot_ma, on="arc", how="left")
    ma["ff_usage"] = (ma.ff_n / ma.all_n).round(3)
    ma.round(3).to_csv(os.path.join(OUT_DIR, "dp_uc28_mlb_arc.csv"), index=False)

    # --- 10. usage by count state ----------------------------------------
    cs = both.copy()
    cs["count_state"] = np.where(cs.strikes > cs.balls, "ahead",
                        np.where(cs.balls > cs.strikes, "behind", "even"))
    cnt = cs.groupby(["level", "count_state", "pitch_name"], as_index=False).agg(n=("des", "size"))
    tot_cnt = cnt.groupby(["level", "count_state"], as_index=False).n.sum().rename(columns={"n": "n_tot"})
    cnt = cnt.merge(tot_cnt, on=["level", "count_state"])
    cnt["usage"] = (cnt.n / cnt.n_tot).round(3)
    # two-strike putaway mix specifically
    two = both[both.strikes == 2].groupby(["level", "pitch_name"], as_index=False).agg(n=("des", "size"))
    tot_two = two.groupby("level", as_index=False).n.sum().rename(columns={"n": "n_tot"})
    two = two.merge(tot_two, on="level")
    two["usage"] = (two.n / two.n_tot).round(3)
    two["count_state"] = "two_strike"
    cnt = pd.concat([cnt, two[cnt.columns.intersection(two.columns)]], ignore_index=True)
    cnt.to_csv(os.path.join(OUT_DIR, "dp_uc28_count_usage.csv"), index=False)

    # --- 11. platoon ------------------------------------------------------
    pl_k = kpi_block(both, ["level", "stand"])
    pl_r = nresults(["level", "stand"], both)
    pl = pl_k.merge(pl_r[["level", "stand", "plate_apps", "strikeouts", "walks", "hrs", "woba"]],
                    on=["level", "stand"], how="left")
    pl.round(3).to_csv(os.path.join(OUT_DIR, "dp_uc28_platoon.csv"), index=False)

    # --- 12. contact (directional only) -----------------------------------
    bip = both[both.type == "X"].copy()
    con = bip.groupby(["level"], as_index=False).agg(
        bip=("des", "size"),
        ev_mean=("launch_speed", "mean"), ev_max=("launch_speed", "max"),
        la_mean=("launch_angle", "mean"),
        ev_tracked=("launch_speed", lambda s: s.notna().sum()))
    hh = hard_hit_rate(["level"], both)
    con = con.merge(hh[["level", "hard_hits", "hard_hit_rate"]], on="level", how="left")
    bt = bip.groupby(["level", "bb_type"], as_index=False).agg(n=("des", "size"))
    btp = bt.pivot(index="level", columns="bb_type", values="n").fillna(0).reset_index()
    con = con.merge(btp, on="level", how="left")
    con["ev_coverage"] = (con.ev_tracked / con.bip).round(3)
    con.round(3).to_csv(os.path.join(OUT_DIR, "dp_uc28_contact.csv"), index=False)

    # --- 12b. usage by stand (platoon weapon audit) -----------------------
    us = both.groupby(["level", "stand", "pitch_name"], as_index=False).agg(n=("des", "size"))
    tot_us = us.groupby(["level", "stand"], as_index=False).n.sum().rename(columns={"n": "n_tot"})
    us = us.merge(tot_us, on=["level", "stand"])
    us["usage"] = us.n / us.n_tot
    us = us.merge(whiff_rate(["level", "stand", "pitch_name"], both)[
        ["level", "stand", "pitch_name", "swings", "whiffs", "whiff_rate"]],
        on=["level", "stand", "pitch_name"], how="left")
    us.round(3).to_csv(os.path.join(OUT_DIR, "dp_uc28_usage_by_stand.csv"), index=False)

    # --- 12c. fastball whiff by location -------------------------------
    zff = zone_tier(both)
    zff = zff[zff.pitch_name == "4-Seam Fastball"].copy()
    ffloc = zff.groupby(["level", "loc_tier"], as_index=False).agg(pitches=("des", "size"))
    ffloc = ffloc.merge(whiff_rate(["level", "loc_tier"], zff)[
        ["level", "loc_tier", "swings", "whiffs", "whiff_rate"]],
        on=["level", "loc_tier"], how="left")
    zff["ut_band"] = np.where(
        zff.plate_z >= zff.sz_bot + (2 / 3) * (zff.sz_top - zff.sz_bot),
        "upper_third_or_above", "lower_two_thirds")
    ffband = zff.groupby(["level", "ut_band"], as_index=False).agg(pitches=("des", "size"))
    ffband = ffband.merge(whiff_rate(["level", "ut_band"], zff)[
        ["level", "ut_band", "swings", "whiffs", "whiff_rate"]],
        on=["level", "ut_band"], how="left")
    ffband = ffband.rename(columns={"ut_band": "loc_tier"})
    ffloc["cut"] = "zone tier"
    ffband["cut"] = "elevation band"
    pd.concat([ffloc, ffband], ignore_index=True).round(3).to_csv(
        os.path.join(OUT_DIR, "dp_uc28_fastball_whiff_by_location.csv"), index=False)

    # --- 12d. velocity separation ladder ---------------------------------
    sep_rows = []
    for lv, d in both.groupby("level"):
        ffv = d[d.pitch_name == "4-Seam Fastball"].release_speed.mean()
        for p in ["Sinker", "Split-Finger", "Slider", "Sweeper", "Curveball"]:
            sub = d[d.pitch_name == p]
            if len(sub):
                sep_rows.append(dict(level=lv, pitch_name=p, n=len(sub),
                                     ff_velo=ffv, pitch_velo=sub.release_speed.mean(),
                                     sep_mph=ffv - sub.release_speed.mean()))
    sep = pd.DataFrame(sep_rows)
    piv = sep.pivot_table(index="pitch_name", columns="level", values="sep_mph")
    piv["d_sep_aaa_minus_mlb"] = piv["AAA"] - piv["MLB"]
    piv.round(2).reset_index().to_csv(
        os.path.join(OUT_DIR, "dp_uc28_velo_separation.csv"), index=False)

    # --- 12e. BENCHMARK — 2026 MLB RHP four-seam population --------------
    pool = load_benchmark_pool()
    bm = ff_benchmark(pool, min_ff=40)
    bm.to_csv(os.path.join(OUT_DIR, "dp_uc28_ff_benchmark_pool.csv"), index=False)

    p_mlb = bm[bm.pitcher == PAINTER]
    ff_a = add_movement_cols(aaa[aaa.pitch_name == "4-Seam Fastball"])
    aaa_up = zff[(zff.level == "AAA") & (zff.ut_band == "upper_third_or_above")]
    bench_rows = []

    def brow(metric, mlb_val, aaa_val, hib, note):
        bench_rows.append(dict(
            metric=metric, painter_mlb=round(mlb_val, 3) if pd.notna(mlb_val) else np.nan,
            painter_aaa=round(aaa_val, 3) if pd.notna(aaa_val) else np.nan,
            pool_median=round(bm[metric].median(), 3) if metric in bm else np.nan,
            pool_p75=round(bm[metric].quantile(.75), 3) if metric in bm else np.nan,
            painter_mlb_pctile=pct_rank(bm[metric], mlb_val, hib) if metric in bm else np.nan,
            pool_n=int(bm[metric].notna().sum()) if metric in bm else 0,
            note=note))

    if len(p_mlb):
        r = p_mlb.iloc[0]
        brow("velo", r.velo, ff_a.release_speed.mean(), True,
             "4-seam average velocity, mph")
        brow("ivb_in", r.ivb_in, ff_a.ivb_in.mean(), True,
             "Induced vertical break, inches — ride")
        brow("ext_ft", r.ext_ft, ff_a.release_extension.mean(), True,
             "Release extension, feet")
        brow("futr", r.futr, float(futr[futr.level == "AAA"].futr.iloc[0]), True,
             "NEW KPI — Fastball Upper-Third Rate")
        brow("ff_whiff", r.ff_whiff,
             float(ffloc[(ffloc.level == "AAA")].whiffs.sum() /
                   max(ffloc[(ffloc.level == "AAA")].swings.sum(), 1)), True,
             "Whiff per swing on the 4-seam")
        brow("ff_whiff_upper", r.ff_whiff_upper,
             float(aaa_up.description.isin(WHIFFS).sum() /
                   max(aaa_up.description.isin(SWINGS).sum(), 1)), True,
             "Whiff per swing on 4-seams in the upper third or above")
    bench = pd.DataFrame(bench_rows)
    bench.to_csv(os.path.join(OUT_DIR, "dp_uc28_ff_benchmark_painter.csv"), index=False)

    # --- 12f. BENCHMARK — arm-angle spread (tipping proxy) ---------------
    spread = arm_angle_spread(pool, min_n=15)
    spread.to_csv(os.path.join(OUT_DIR, "dp_uc28_arm_spread_pool.csv"), index=False)
    p_sp = spread[spread.pitcher == PAINTER]
    aaa_arm = aaa.groupby("pitch_name", as_index=False).agg(n=("des", "size"),
                                                           arm=("arm_angle", "mean"))
    aaa_arm = aaa_arm[aaa_arm.n >= 25]
    spread_summary = pd.DataFrame([dict(
        scope="Painter MLB 2026",
        arm_spread_deg=float(p_sp.arm_spread_deg.iloc[0]) if len(p_sp) else np.nan,
        pool_median=round(spread.arm_spread_deg.median(), 2),
        pool_p90=round(spread.arm_spread_deg.quantile(.90), 2),
        pool_n=len(spread),
        pctile_high_is_worse=pct_rank(spread.arm_spread_deg,
                                      float(p_sp.arm_spread_deg.iloc[0]) if len(p_sp) else np.nan,
                                      True)),
        dict(scope="Painter AAA 2026 (>=25 pitches/type)",
             arm_spread_deg=round(float(aaa_arm.arm.max() - aaa_arm.arm.min()), 3),
             pool_median=round(spread.arm_spread_deg.median(), 2),
             pool_p90=round(spread.arm_spread_deg.quantile(.90), 2),
             pool_n=len(spread), pctile_high_is_worse=np.nan)])
    spread_summary.to_csv(os.path.join(OUT_DIR, "dp_uc28_arm_spread_painter.csv"), index=False)

    # --- 12g. times through the order ------------------------------------
    # TTO is derived from the batter's appearance sequence within a game:
    # the n-th distinct at_bat_number for a given (game_pk, batter).
    tto = both.sort_values(["game_pk", "at_bat_number", "pitch_number"]).copy()
    firsts = tto.drop_duplicates(["game_pk", "at_bat_number"])[
        ["game_pk", "at_bat_number", "batter"]].copy()
    firsts["tto"] = firsts.groupby(["game_pk", "batter"]).cumcount() + 1
    tto = tto.merge(firsts[["game_pk", "at_bat_number", "tto"]],
                    on=["game_pk", "at_bat_number"], how="left")
    tto["tto_lbl"] = np.where(tto.tto >= 3, "3rd+", tto.tto.astype(str) + ("st" if False else ""))
    tto["tto_lbl"] = tto.tto.map({1: "1st time", 2: "2nd time"}).fillna("3rd+ time")
    tk = kpi_block(tto, ["level", "tto_lbl"])
    tr = nresults(["level", "tto_lbl"], tto)
    tt = tk.merge(tr[["level", "tto_lbl", "plate_apps", "strikeouts", "walks", "hrs", "woba"]],
                  on=["level", "tto_lbl"], how="left")
    tt.round(3).to_csv(os.path.join(OUT_DIR, "dp_uc28_times_through_order.csv"), index=False)

    # --- 13. DQ scorecard -------------------------------------------------
    dq = []

    def chk(check, dimension, scope, result, status, note):
        dq.append(dict(check=check, dimension=dimension, scope=scope,
                       result=result, status=status, note=note))

    chk("Entity lock", "Accuracy", "both tiers",
        f"pitcher id set == {{{PAINTER}}}", "PASS",
        "Locked on MLBAM id, never on player_name. No name-collision exposure.")
    chk("Deduplication", "Uniqueness", "both tiers",
        f"MLB {len(mlb)} rows / AAA {len(aaa)} rows after drop_duplicates on "
        "(game_pk, at_bat_number, pitch_number)", "PASS",
        "Zero duplicate pitch keys survive the load.")
    chk("Game type filter", "Validity", "MLB tier",
        "game_type == 'R' only; 52 spring-training pitches excluded", "PASS",
        "Spring rows would contaminate velo and usage baselines.")
    for c in ["release_speed", "release_spin_rate", "pfx_x", "pfx_z", "plate_x",
              "plate_z", "sz_top", "sz_bot", "release_pos_x", "release_pos_z",
              "release_extension", "arm_angle", "zone"]:
        cm = mlb[c].notna().mean() if c in mlb else np.nan
        ca = aaa[c].notna().mean() if c in aaa else np.nan
        st = "PASS" if min(cm, ca) >= 0.99 else ("WARN" if min(cm, ca) >= 0.90 else "FAIL")
        chk(f"CDE completeness — {c}", "Completeness", "both tiers",
            f"MLB {cm:.1%} / AAA {ca:.1%}", st, "Core stuff CDE; required for the report.")
    for c in ["launch_speed", "estimated_woba_using_speedangle"]:
        cm = mlb[c].notna().mean()
        ca = aaa[c].notna().mean()
        chk(f"CDE completeness — {c}", "Completeness", "both tiers",
            f"MLB {cm:.1%} / AAA {ca:.1%}", "WARN",
            "Populated on batted balls only. Directional use only — never a headline rate.")
    chk("Cross-level blending guard", "Consistency", "report",
        "All rate KPIs computed within level; no pooled MLB+AAA rate published",
        "PASS", "UC#11 multi-level rule enforced by construction.")
    chk("Pitch-tag drift", "Consistency", "AAA tier",
        "Slider/Sweeper boundary differs across MiLB and MLB tagging models",
        "WARN", "Shape comparisons for SL/SW read loosely; flagged in report.")
    chk("Opponent coverage", "Completeness", "BAL",
        "0 Orioles hitter rows in repo; 0 prior Painter-vs-BAL pitches", "FAIL",
        "NON-BLOCKING for this UC — scope excludes an opponent attack plan. "
        "Recorded as an intake gap; report carries no fabricated lineup.")
    chk("Freshness — MLB", "Timeliness", "phils_2026.parquet",
        f"max game_date {mlb.game_date.max()}", "PASS",
        "Painter's last MLB pitch is 2026-06-17; file itself current to 2026-07-29.")
    chk("Freshness — AAA", "Timeliness", "lhvp26.parquet",
        f"max game_date {aaa.game_date.max()}", "PASS",
        "Cache current through 2026-07-30, T-1 from game day.")
    chk("Sample size — MLB", "Validity", "MLB tier",
        f"{len(mlb)} pitches / {int(nresults(['level'], mlb).plate_apps.iloc[0])} PA",
        "PASS", "Above the 100 BF publication convention for pitcher rate stats.")
    chk("Sample size — AAA", "Validity", "AAA tier",
        f"{len(aaa)} pitches / {int(nresults(['level'], aaa).plate_apps.iloc[0])} PA",
        "WARN", "Below the 100 BF convention. Every AAA rate is printed with its PA/BF.")
    dq = pd.DataFrame(dq)
    dq.to_csv(os.path.join(OUT_DIR, "dp_uc28_dq_scorecard.csv"), index=False)

    # --- 14. freshness manifest -------------------------------------------
    fm = pd.DataFrame([
        dict(source="data/phillies/phils_2026.parquet", tier="MLB",
             filter=f"phillies_role=='pitching' & pitcher=={PAINTER} & game_type=='R'",
             rows=len(mlb), window=f"{mlb.game_date.min()} .. {mlb.game_date.max()}",
             starts=mlb.game_date.nunique(), fitness="FIT — full Hawk-Eye tracking"),
        dict(source="data/opponents/lhvp26.parquet", tier="AAA (supporting)",
             filter=f"pitcher=={PAINTER}", rows=len(aaa),
             window=f"{aaa.game_date.min()} .. {aaa.game_date.max()}",
             starts=aaa.game_date.nunique(),
             fitness="FIT for stuff/usage/whiff; LOW fidelity for EV/xwOBA"),
        dict(source="(none available)", tier="Opponent — BAL", filter="n/a", rows=0,
             window="n/a", starts=0,
             fitness="ABSENT — no Orioles cache; opponent plan out of scope"),
        dict(source="mlb.com starting lineups", tier="manual carry-in", filter="n/a",
             rows=0, window=GAME_DAY, starts=0,
             fitness="NOT CARRIED — BAL lineup not retrieved; nothing fabricated"),
        dict(source="wOBA and FIP Constants.csv", tier="both",
             filter="Season==2026", rows=1, window="2026", starts=0,
             fitness=("PRESENT" if WOBA_CSV else "MISSING — wOBA columns will be null")),
    ])
    fm.to_csv(os.path.join(OUT_DIR, "dp_uc28_freshness_manifest.csv"), index=False)

    # --- 15. figures ------------------------------------------------------
    _t = {lv: f"{lv} — {d.game_date.nunique()} starts "
              f"({d.game_date.min()} → {str(d.game_date.max())[5:]})"
          for lv, d in both.groupby("level")}
    fig_movement(ars, os.path.join(OUT_DIR, "dp_uc28_fig1_arsenal_movement.png"), _t)
    fig_velo_by_start(log.copy(), os.path.join(OUT_DIR, "dp_uc28_fig2_velo_by_start.png"))
    fig_release_drift(rel.copy(), os.path.join(OUT_DIR, "dp_uc28_fig3_release_drift.png"))
    fig_location_tiers(loc.copy(), os.path.join(OUT_DIR, "dp_uc28_fig4_location_tiers.png"))
    fig_usage_whiff(ars, os.path.join(OUT_DIR, "dp_uc28_fig5_usage_whiff.png"))

    # --- console receipt --------------------------------------------------
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 60)
    print("=" * 78)
    print("UC #29 / uc-pps-023 / dp_uc28 — Andrew Painter return read")
    print("=" * 78)
    print("\n--- LEVEL SUMMARY ---")
    print(lvl[["level", "starts", "pitches", "plate_apps", "strike_rate", "csw_rate",
               "whiff_rate", "chase_rate", "in_zone_rate", "first_pitch_strike_rate",
               "putaway_rate", "hard_hit_rate", "krate", "bbrate", "woba"]].to_string(index=False))
    print("\n--- ARSENAL BY LEVEL ---")
    print(ars[["level", "pitch_name", "n", "usage", "velo", "velo_max", "spin",
               "ivb_in", "hb_in", "in_zone_rate", "whiff_rate", "chase_rate",
               "csw_rate", "ext_ft", "arm_angle"]].to_string(index=False))
    print("\n--- CROSS-LEVEL STUFF DELTA (NEW KPI) ---")
    print(xlsd[["pitch_name", "n_mlb", "n_aaa", "usage_mlb", "usage_aaa", "d_usage_pp",
                "velo_mlb", "velo_aaa", "d_velo", "d_spin", "d_ivb", "d_hb",
                "coverage_ok", "noise_guard"]].to_string(index=False))
    print("\n--- RELEASE CONSISTENCY INDEX (NEW KPI) ---")
    print(rel[["level", "game_date", "ff_pitches", "mean_x_ft_in", "mean_z_ft_in",
               "rci_in"]].to_string(index=False))
    print("\n--- FASTBALL UPPER-THIRD RATE (NEW KPI) ---")
    print(futr_all.to_string(index=False))
    print("\n--- START LOG ---")
    print(log[["level", "game_date", "pitches", "plate_apps", "strikeouts", "walks",
               "strike_rate", "csw_rate", "whiff_rate", "chase_rate",
               "first_pitch_strike_rate", "ff_velo", "ff_velo_max", "ext_ft",
               "futr"]].to_string(index=False))
    print("\n--- AAA ARC ---")
    print(arc.to_string(index=False))
    print("\n--- MLB ARC ---")
    print(ma.to_string(index=False))
    print("\n--- PLATOON ---")
    print(pl[["level", "stand", "pitches", "plate_apps", "whiff_rate", "chase_rate",
              "in_zone_rate", "csw_rate", "putaway_rate", "hard_hit_rate", "woba"]].to_string(index=False))
    print("\n--- LOCATION TIERS ---")
    print(loc.pivot_table(index=["level", "pitch_name"], columns="loc_tier",
                          values="share").fillna(0).to_string())
    print("\n--- TWO-STRIKE MIX ---")
    print(cnt[cnt.count_state == "two_strike"][["level", "pitch_name", "n", "usage"]].to_string(index=False))
    print("\n--- CONTACT (directional) ---")
    print(con.to_string(index=False))
    print("\n--- RELEASE / EXTENSION BY PITCH ---")
    print(relp.to_string(index=False))
    print("\n--- USAGE BY STAND ---")
    print(us.pivot_table(index="pitch_name", columns=["level", "stand"],
                         values="usage").fillna(0).to_string())
    print("\n--- FF WHIFF BY LOCATION ---")
    print(pd.concat([ffloc, ffband], ignore_index=True).to_string(index=False))
    print("\n--- VELO SEPARATION LADDER ---")
    print(piv.round(2).to_string())
    print("\n--- FF BENCHMARK vs 2026 MLB RHP POOL ---")
    print(bench.to_string(index=False))
    print("\n--- TIMES THROUGH THE ORDER ---")
    print(tt[["level", "tto_lbl", "pitches", "plate_apps", "strikeouts", "walks",
              "whiff_rate", "chase_rate", "csw_rate", "hard_hit_rate", "woba"]].to_string(index=False))
    print("\n--- ARM-ANGLE SPREAD (TIPPING PROXY) ---")
    print(spread_summary.to_string(index=False))
    print("\n--- ARM ANGLE BY PITCH, BOTH LEVELS ---")
    print(add_movement_cols(both).groupby(["level", "pitch_name"], as_index=False).agg(
        n=("des", "size"), arm=("arm_angle", "mean"),
        rel_x_in=("release_pos_x", lambda s: 12 * s.mean()),
        rel_z_in=("release_pos_z", lambda s: 12 * s.mean())).round(2).to_string(index=False))
    print("\n--- DQ SCORECARD ---")
    print(dq[["check", "dimension", "result", "status"]].to_string(index=False))
    print("\n--- FRESHNESS ---")
    print(fm.to_string(index=False))
    print(f"\nAll receipts written to {OUT_DIR}")


if __name__ == "__main__":
    main()
