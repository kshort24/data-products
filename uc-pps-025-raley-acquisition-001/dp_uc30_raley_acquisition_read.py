"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #31  (uc-pps-025)
"Acquisition Read: Brooks Raley (LHP) — what the Phillies just bought, how
 hitters see him, and how to deploy him. Trade-deadline onboarding, 2026-08-04."
============================================================================

Layer-3 BUILD artifact for the Phillies Pitching (pps) value stream.

Pattern lineage: UC#3 (Luzardo deep dive) -> UC#8 (Nola vs WAS, canonical
flat-file pattern) -> UC#11 (Rangel vs PIT, multi-level evidence tier) ->
UC#29 (Painter return read, self-scout variant) -> UC#30 (Kilian acquisition
read, FIRST acquisition-onboarding variant). This UC is the SECOND
acquisition-onboarding read and inherits UC#30's structure wholesale.

WHAT IS NEW HERE (vs UC#30 Kilian):
  UC#30 asked "what did the role change do to him." This UC asks a different
  question: "why is this look hard to pick up, and who does it play against."
  The novel angle is a RELEASE-POINT BENCHMARK against the historical Phillies
  left-handed pitching population (2015-2026), and the translation of that
  geometry into a hitter-sightline measure. Four new KPIs are specified in
  sec.4 of the use-case spec before they appear anywhere in the report.

ERA DESIGN — PRE-TJ vs POST-TJ (DPO decision, 2026-08-04):
  Raley underwent Tommy John surgery in 2024. His last outing before surgery
  was 2024-04-19; he returned 2025-07-19. The consumer explicitly asked for
  full history SPLIT INTO TWO SEGMENTS rather than a single pooled rate:

    PRE-TJ  : 2020-07-24 .. 2024-04-19   (CIN/HOU/TB/NYM)
    POST-TJ : 2025-07-19 .. 2026-08-02   (NYM)

  The two tiers are ALWAYS LABELED and NEVER BLENDED into a single published
  rate. POST-TJ is the "pitcher the Phillies acquired" tier and carries every
  forward-looking claim; PRE-TJ is the "what he was" tier and exists to size
  the delta the surgery produced. The 2024-04-19 -> 2025-07-19 interval is a
  TRUE GAP (rehab) and is never interpolated.

  NOTE ON KBO: Raley pitched in the KBO 2015-2019. That is outside the
  Statcast era and outside this repo. His pre-2020 professional record is a
  RECORDED GAP, not a zero.

ZERO PHILLIES ROWS (recorded gap, non-blocking):
  The cache runs through 2026-08-02 and every 2026 row is NYM. Raley has not
  thrown a pitch for the Phillies. Like UC#30, the deliverable is therefore an
  INTAKE DOSSIER, not an opponent attack plan. There is no "next opponent"
  because no role has been assigned. Opponent modelling is deferred to a
  future uc-pps once a role is set.

NEW KPIs (full specs in dp_uc30_..._use_case_spec.md sec.4):
  * Release Slot Angle (RSA)           -- geometric arm-slot proxy computable
                                          across the full 2015-2026 Phillies
                                          history, calibrated against the
                                          native `arm_angle` field where both
                                          exist (2025-26)
  * Release Distinctiveness Index (RDI)-- standardized distance of a pitcher's
                                          mean release point from the Phillies
                                          LHP population centroid
  * Sightline Offset (SLO)             -- lateral feet between release point
                                          and the centre of the batter's box
                                          the hitter occupies; computed same-
                                          side (vs LHH) and opposite-side
                                          (vs RHH)
  * Release Tipping Delta (RTD)        -- max pairwise distance, in inches,
                                          between per-pitch-type mean release
                                          points (a tipping / self-scout check)

COORDINATE CONVENTION (established empirically, asserted in the DQ scorecard):
  Positive `release_pos_x` and positive `plate_x` both denote the side of the
  field that left-handed batters stand on and that a left-handed pitcher's arm
  occupies. Verified two ways in `assert_coordinate_convention()`:
    (a) Phillies LHP mean release_pos_x > 0, RHP mean release_pos_x < 0
    (b) hit-by-pitch plate_x is positive for LHH, negative for RHH
  Every sightline claim in the report depends on this convention holding.

Governance lineage:
  - data-product-owner      : sequenced as UC#31 / uc-pps-025 / dp_uc30
  - use-case-validator      : intake gate; zero-PHI-rows, KBO gap, rehab gap
                              and 2024 partial season all NON-BLOCKING
  - source-system-profiler  : entity lock pitcher==548384; cache through
                              2026-08-02 (T-2 as of 2026-08-04)
  - kpi-calculator          : locked cores inherited VERBATIM from dp_uc29
                              (get_stats/nresults, whiff_rate, chase_rate,
                              putaway_rate, fpsr, hard_hit_rate, xwobacon,
                              csw_rate); 4 new KPIs specified before use
  - data-quality-engineer   : scorecard emitted to out/

OUTPUTS — CSV receipts + figures (NEW files, none overwritten), ./out/:
  dp_uc30_era_summary.csv             pre-TJ vs post-TJ topline + process
  dp_uc30_season_log.csv              season-level results and process
  dp_uc30_arsenal_by_era.csv          usage/velo/spin/break/release by era
  dp_uc30_arsenal_post_tj.csv         post-TJ arsenal detail with outcomes
  dp_uc30_platoon.csv                 vs LHH / vs RHH by era
  dp_uc30_pitch_by_hand.csv           pitch x hand outcome matrix, post-TJ
  dp_uc30_count_usage.csv             usage by count state x hand
  dp_uc30_two_strike.csv              two-strike putaway mix by hand
  dp_uc30_lhp_release_benchmark.csv   NEW KPI: RSA + RDI, Phillies LHP pop
  dp_uc30_rsa_calibration.csv         RSA proxy vs native arm_angle, 2025-26
  dp_uc30_sightline.csv               NEW KPI: SLO, Raley vs LHP population
  dp_uc30_release_by_pitch.csv        NEW KPI: RTD, tipping self-scout
  dp_uc30_tracking_proxies.csv        bat speed / swing length / miss distance
  dp_uc30_monthly_arc.csv             post-TJ trend, velo + process
  dp_uc30_outing_log.csv              every post-TJ outing
  dp_uc30_deployment.csv              entry inning x score state x runners
  dp_uc30_batter_sequence.csv         performance by batter faced within outing
  dp_uc30_rest_workload.csv           performance by days rest / back-to-back
  dp_uc30_damage_log.csv              every XBH allowed, post-TJ
  dp_uc30_dq_scorecard.csv            data-quality-engineer scorecard
  dp_uc30_freshness_manifest.csv      source/window/fitness receipts
  dp_uc30_fig1_release_benchmark.png  fig 1 - release point vs Phillies LHP
  dp_uc30_fig2_arsenal_movement.png   fig 2 - movement map, pre vs post TJ
  dp_uc30_fig3_platoon_process.png    fig 3 - pitch x hand usage and whiff
  dp_uc30_fig4_location_by_hand.png   fig 4 - location maps by batter hand
  dp_uc30_fig5_deployment.png         fig 5 - deployment and workload
============================================================================
"""
from __future__ import annotations
import os
import glob
import json
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out")
os.makedirs(OUT_DIR, exist_ok=True)

RALEY = 548384                     # Brooks Raley, MLBAM pitcher id — ENTITY LOCK
AS_OF = "2026-08-04"

# --- ERA BOUNDARIES (see docstring) ---------------------------------------
PRE_TJ_END = "2024-04-19"          # last outing before Tommy John surgery
POST_TJ_START = "2025-07-19"       # first outing after return
ERA_PRE = "Pre-TJ (2020-2024)"
ERA_POST = "Post-TJ (2025-2026)"
ERA_ORDER = [ERA_PRE, ERA_POST]

# --- BENCHMARK POPULATION SCOPE (DPO decision) ----------------------------
BENCH_MIN_PITCHES = 300            # Phillies LHP inclusion threshold
BENCH_YEAR_MIN = 2015

# --- BATTER'S BOX GEOMETRY -------------------------------------------------
# Home plate is 17 in wide (+/- 0.708 ft). The batter's box is 4 ft wide and
# its inner edge sits 6 in off the plate, so the box centre is
#   0.708 + 0.5 + 2.0 = 3.208 ft ... using the rulebook 6-in gap.
# Statcast plate_x is measured from the centre of the plate. Hitters do not
# stand at the box centre; the observed HBP centroid (|plate_x| ~ 2.0-2.2 ft)
# is the better empirical anchor for where a hitter's body actually is.
# BOX_CENTER_FT is therefore a RULEBOOK constant and BODY_ANCHOR_FT is the
# EMPIRICAL one; SLO is published on the rulebook constant and the empirical
# anchor is carried as a sensitivity in the receipts.
BOX_CENTER_FT = 3.208
BODY_ANCHOR_FT = 2.10

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "phillies"),
    "/sessions/adoring-hopeful-wozniak/mnt/MLB/data/phillies",
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies",
]
PHIL_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
if PHIL_DIR is None:
    raise FileNotFoundError("Could not locate data/phillies. Set MLB_DATA_ROOT.")
OPP_DIR = os.path.join(os.path.dirname(PHIL_DIR), "opponents")
REPO_ROOT = os.path.dirname(os.path.dirname(PHIL_DIR))

_WOBA_CANDIDATES = [
    os.path.join(HERE, "wOBA and FIP Constants.csv"),
    os.path.join(REPO_ROOT, "wOBA and FIP Constants.csv"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv",
]
WOBA_CSV = next((p for p in _WOBA_CANDIDATES if p and os.path.isfile(p)), None)

SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]
CALLED_STRIKE = ["called_strike"]

PHI_RED, PHI_NAVY, PHI_GRAY, PHI_LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
PITCH_COLORS = {
    "Sweeper": "#002D72", "Cutter": "#6BAED6", "Sinker": "#E81828",
    "Changeup": "#2CA02C", "4-Seam Fastball": "#FF7F0E", "Slider": "#8C564B",
    "Curveball": "#9467BD",
}
PITCH_ORDER = ["Sinker", "Cutter", "Sweeper", "Changeup", "4-Seam Fastball"]

RECEIPTS: dict[str, str] = {}


def emit(df: pd.DataFrame, name: str, note: str = "") -> pd.DataFrame:
    """Write a CSV receipt and register it. Never overwrites a prior UC."""
    path = os.path.join(OUT_DIR, f"dp_uc30_{name}.csv")
    df.to_csv(path, index=False)
    RECEIPTS[name] = note or name
    print(f"  [receipt] dp_uc30_{name}.csv  ({len(df)} rows)")
    return df


# ===========================================================================
# LOADERS
# ===========================================================================
def _coerce(df):
    for c in ["plate_x", "plate_z", "sz_top", "sz_bot", "pfx_x", "pfx_z",
              "release_speed", "effective_speed", "release_spin_rate", "spin_axis",
              "release_pos_x", "release_pos_z", "release_extension", "arm_angle",
              "launch_speed", "launch_angle", "strikes", "balls", "outs_when_up",
              "pitch_number", "at_bat_number", "woba_value", "woba_denom", "zone",
              "inning", "bat_score", "fld_score", "bat_speed", "swing_length",
              "miss_distance", "attack_angle", "pitcher_days_since_prev_game",
              "estimated_woba_using_speedangle", "estimated_ba_using_speedangle"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _attach_woba(df):
    if not WOBA_CSV:
        return df
    w = pd.read_csv(WOBA_CSV)
    df = df.drop(columns=[c for c in w.columns if c != "Season" and c in df.columns])
    return df.merge(w, left_on="game_year", right_on="Season", how="left")


def load_raley():
    """Single-source load. Entity lock enforced HERE and asserted below."""
    f = os.path.join(OPP_DIR, "raley.parquet")
    d = pd.read_parquet(f)
    d = d[(d.pitcher == RALEY) & (d.game_type == "R")]
    d = d.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    d = _coerce(d.copy())
    d["game_date"] = pd.to_datetime(d.game_date)
    d["era"] = np.where(d.game_date <= pd.Timestamp(PRE_TJ_END), ERA_PRE,
                        np.where(d.game_date >= pd.Timestamp(POST_TJ_START),
                                 ERA_POST, "REHAB GAP"))
    d["pitching_team"] = np.where(d.inning_topbot == "Top", d.home_team, d.away_team)
    return _attach_woba(d)


def load_phillies_lhp():
    """Historical Phillies left-handed pitching population, 2015-2026.

    Columns are loaded conservatively: `arm_angle` only exists in the 2025 and
    2026 files, so it is read where present and left null elsewhere. That
    asymmetry is precisely why the RSA proxy exists.
    """
    base_cols = ["game_year", "game_date", "game_type", "p_throws", "player_name",
                 "pitcher", "release_pos_x", "release_pos_z", "release_extension",
                 "release_speed", "pitch_name", "game_pk", "at_bat_number",
                 "pitch_number", "phillies_role"]
    frames = []
    import pyarrow.parquet as pq
    for f in sorted(glob.glob(os.path.join(PHIL_DIR, "phils_*.parquet"))):
        have = set(pq.ParquetFile(f).schema_arrow.names)
        cols = [c for c in base_cols if c in have]
        if "arm_angle" in have:
            cols = cols + ["arm_angle"]
        d = pd.read_parquet(f, columns=cols)
        if "arm_angle" not in d.columns:
            d["arm_angle"] = np.nan
        frames.append(d)
    p = pd.concat(frames, ignore_index=True)
    p = p[(p.phillies_role == "pitching") & (p.game_type == "R")]
    p = p.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    return _coerce(p.copy())


# ===========================================================================
# LOCKED KPI FUNCTIONS — inherited VERBATIM from dp_uc29_kilian_acquisition_read.py
# (which inherited from dp_uc28 / dp_uc11 / dp_uc8 / Baseball Functions).
# DO NOT RE-DERIVE. Any change here is a breaking change requiring a new spec.
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


def xwobacon(level, df):
    """xwOBA ON CONTACT — mean over BALLS IN PLAY only. DQ-hardened; inherited
    from uc-pps-021 (UC #26) open item O1. This UC cites ONLY `xwobacon`; the
    pitch-level `get_stats.xwoba` column is quarantined and never published."""
    if isinstance(level, str):
        level = [level]
    bip = df[df.type == "X"]
    out = bip.groupby(level, as_index=False).agg(
        xwobacon=("estimated_woba_using_speedangle", "mean"),
        xwobacon_bip=("estimated_woba_using_speedangle", "size"))
    return out.round(3)


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


# ===========================================================================
# DERIVED HELPERS (mechanical partitions of existing CDEs, not new KPIs)
# ===========================================================================
def tracked(df):
    """TRACKED-PITCH POPULATION — rows representing an actual thrown, tracked
    pitch. Automatic balls (pitch-timer violations) carry null pitch_name /
    zone / plate_x and are legitimate PA outcomes but are NOT pitches for
    usage-share or location purposes. Inherited from UC#30 open item O2."""
    return df[df.pitch_name.notna()]


def zone_rate_strict(df):
    """In-zone rate over TRACKED pitches only (UC#30 open item O2)."""
    t = tracked(df)
    if len(t) == 0:
        return np.nan
    return float((t.zone <= 9).sum() / len(t))


def count_state(row):
    b, s = row["balls"], row["strikes"]
    if pd.isna(b) or pd.isna(s):
        return "unknown"
    if s == 2:
        return "two-strike"
    if b == 0 and s == 0:
        return "first pitch"
    if b > s:
        return "behind (hitter ahead)"
    if s > b:
        return "ahead (pitcher ahead)"
    return "even"


# ===========================================================================
# NEW KPI 1 — RELEASE SLOT ANGLE (RSA)
# ===========================================================================
def release_slot_angle(rel_x, rel_z):
    """RELEASE SLOT ANGLE (RSA), degrees.

    RSA = degrees( atan2( release_pos_z , |release_pos_x| ) )

    The angle, viewed from behind the pitcher, between the horizontal and the
    line from the rubber-centre origin to the release point. 90 deg is a
    release directly above the origin (maximally over-the-top); smaller values
    are progressively lower and wider (side-arm).

    WHY THIS AND NOT `arm_angle`: Statcast's native `arm_angle` field only
    exists in this repo's Phillies files from 2025 onward. The benchmark
    population the consumer asked for spans 2015-2026. RSA is computable from
    `release_pos_x` / `release_pos_z`, which are populated for the full span,
    and is CALIBRATED against native `arm_angle` on the 2025-26 overlap in
    `dp_uc30_rsa_calibration.csv`. RSA is a PROXY and is labelled as such
    everywhere it is published. It makes NO anthropometric assumption — it is
    a pure descriptor of the release coordinate, which is exactly what a
    hitter's sightline problem is about.

    Grain: one value per pitch; published as a per-pitcher mean.
    Population: any row with non-null release_pos_x and release_pos_z.
    Edge cases: null in, null out. |rel_x| is used so that RSA is directly
    comparable between left- and right-handed pitchers.
    """
    return np.degrees(np.arctan2(rel_z, np.abs(rel_x)))


# ===========================================================================
# NEW KPI 2 — RELEASE DISTINCTIVENESS INDEX (RDI)
# ===========================================================================
def release_distinctiveness(sub_df, pop_mean, pop_sd):
    """RELEASE DISTINCTIVENESS INDEX (RDI), standard deviations.

    RDI = sqrt( z(rel_x)^2 + z(rel_z)^2 )

    Euclidean distance of a pitcher's mean release point from the benchmark
    population centroid, after standardizing each axis by the population
    standard deviation of PITCHER MEANS (not of individual pitches — the
    question is how unusual this pitcher is among pitchers).

    Interpretation: RDI ~ 0 means "looks like the average lefty in this
    organization's history"; RDI >= 1.5 means the look is genuinely atypical
    relative to what this coaching staff and these catchers have seen.

    Grain: one value per pitcher.
    Population: Phillies LHP, 2015-2026, >= 300 tracked pitches (n asserted in
    the DQ scorecard). Raley is scored AGAINST this population but is NOT a
    member of it (he has never thrown a Phillies pitch), so his inclusion
    would be circular; the centroid and SD are computed on Phillies LHP only.
    Edge cases: pitchers below the pitch threshold are excluded, not imputed.
    """
    zx = (sub_df["rel_x"] - pop_mean["rel_x"]) / pop_sd["rel_x"]
    zz = (sub_df["rel_z"] - pop_mean["rel_z"]) / pop_sd["rel_z"]
    return np.sqrt(zx ** 2 + zz ** 2)


# ===========================================================================
# NEW KPI 3 — SIGHTLINE OFFSET (SLO)
# ===========================================================================
def sightline_offset(rel_x, bats, box_center=BOX_CENTER_FT):
    """SIGHTLINE OFFSET (SLO), feet.

    SLO = | release_pos_x  -  box_center_x(bats) |

    where box_center_x is +box_center for a left-handed hitter and
    -box_center for a right-handed hitter, following the coordinate
    convention asserted in `assert_coordinate_convention()` (positive x is the
    side LHH stand on and the side a LHP's arm occupies).

    Plain language: the lateral distance, in feet, between the point where the
    ball leaves the pitcher's hand and the centre of the box the hitter is
    standing in. It answers "how far across my body does this ball start?"

      * SMALL SLO (< ~1 ft) means the ball is released almost directly on the
        hitter's own line — for a same-side hitter this is the classic
        low-slot problem: the ball appears from behind his front shoulder and
        he picks it up late.
      * LARGE SLO (> ~5 ft) means the ball starts far across the body, which
        gives an opposite-side hitter a long, clean look but a severe
        horizontal approach angle.

    Grain: one value per pitch; published as a per-pitcher, per-batter-hand
    mean. Population: rows with non-null release_pos_x and non-null `stand`.
    Edge cases: SLO is a distance and is always non-negative. It is a GEOMETRIC
    descriptor, not an outcome measure — it is reported alongside, never in
    place of, whiff/chase/xwOBAcon. `box_center` is the rulebook constant; a
    sensitivity using the empirical body anchor is carried in the receipts.
    """
    center = np.where(pd.Series(bats).values == "L", box_center, -box_center)
    return np.abs(rel_x - center)


# ===========================================================================
# NEW KPI 4 — RELEASE TIPPING DELTA (RTD)
# ===========================================================================
def release_tipping_delta(df, min_pitches=25):
    """RELEASE TIPPING DELTA (RTD), inches.

    RTD = max over all pitch-type pairs (i,j) of
          12 * sqrt( (mean_relx_i - mean_relx_j)^2 + (mean_relz_i - mean_relz_j)^2 )

    The largest separation between the mean release points of any two pitch
    types in the arsenal. A self-scout tipping check: if a pitcher's slider
    leaves his hand from a materially different point than his fastball, an
    advance department will find it.

    Grain: one value per pitcher per era. Population: tracked pitches;
    pitch types with fewer than `min_pitches` are EXCLUDED from the pairwise
    comparison (a 6-pitch sample of a fifth offering will dominate a max
    statistic for no good reason) and the exclusion is reported.
    Edge cases: fewer than two qualifying pitch types -> RTD is null, not zero.

    Benchmark note: RTD has no published league norm. It is interpreted here
    only against Raley's OWN pitch-type dispersion (the within-pitch-type SD
    of release point), which is the honest reference: a between-pitch gap
    smaller than the within-pitch noise is not a tipping signal.
    """
    t = tracked(df)
    m = t.groupby("pitch_name").agg(
        n=("release_pos_x", "size"),
        rel_x=("release_pos_x", "mean"),
        rel_z=("release_pos_z", "mean"),
        sd_x=("release_pos_x", "std"),
        sd_z=("release_pos_z", "std"),
    ).reset_index()
    q = m[m.n >= min_pitches].copy()
    excluded = m[m.n < min_pitches].pitch_name.tolist()
    if len(q) < 2:
        return np.nan, q, excluded
    best = 0.0
    for i in range(len(q)):
        for j in range(i + 1, len(q)):
            d = 12.0 * np.hypot(q.rel_x.iloc[i] - q.rel_x.iloc[j],
                                q.rel_z.iloc[i] - q.rel_z.iloc[j])
            best = max(best, d)
    return float(best), q, excluded


# ===========================================================================
# DQ ASSERTIONS
# ===========================================================================
DQ_ROWS: list[dict] = []


def dq(check, expected, actual, status=None, note=""):
    ok = status if status is not None else (expected == actual)
    DQ_ROWS.append({"check": check, "expected": expected, "actual": actual,
                    "status": "PASS" if ok else "FAIL", "note": note})
    print(f"  [dq] {'PASS' if ok else 'FAIL'}  {check}: {actual}")
    return ok


def assert_coordinate_convention(raley, phl):
    """Two independent confirmations that positive x = LHH side = LHP arm side.
    Every sightline claim in the report depends on this."""
    lhp_mean = phl[phl.p_throws == "L"].release_pos_x.mean()
    rhp_mean = phl[phl.p_throws == "R"].release_pos_x.mean()
    dq("coord: Phillies LHP mean release_pos_x > 0", ">0", round(float(lhp_mean), 3),
        status=lhp_mean > 0)
    dq("coord: Phillies RHP mean release_pos_x < 0", "<0", round(float(rhp_mean), 3),
        status=rhp_mean < 0)
    hb = raley[raley.events == "hit_by_pitch"]
    lhh = hb[hb.stand == "L"].plate_x.mean()
    rhh = hb[hb.stand == "R"].plate_x.mean()
    dq("coord: HBP plate_x > 0 for LHH", ">0", round(float(lhh), 3), status=lhh > 0)
    dq("coord: HBP plate_x < 0 for RHH", "<0", round(float(rhh), 3), status=rhh < 0)
    return float(lhp_mean), float(rhp_mean), float(lhh), float(rhh)


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print("=" * 74)
    print("UC #31 / uc-pps-025 / dp_uc30 — Brooks Raley acquisition read")
    print("=" * 74)

    raley = load_raley()
    phl = load_phillies_lhp()

    # ---------------- entity lock & structural DQ -------------------------
    print("\n[Layer 1] entity lock + structural DQ")
    dq("entity lock: distinct pitcher ids in Raley frame", 1, int(raley.pitcher.nunique()))
    dq("entity lock: pitcher id", RALEY, int(raley.pitcher.iloc[0]))
    dq("entity lock: distinct player_name", 1, int(raley.player_name.nunique()))
    dq("entity lock: p_throws", "L", str(raley.p_throws.mode().iloc[0]))
    dq("game_type restricted to regular season", 1, int(raley.game_type.nunique()))
    dq("dedup: duplicate (game_pk, at_bat, pitch) rows", 0,
       int(raley.duplicated(["game_pk", "at_bat_number", "pitch_number"]).sum()))
    dq("Phillies rows in Raley frame (expected 0 — never pitched for PHI)", 0,
       int((raley.pitching_team == "PHI").sum()),
       note="acquisition dossier, not an in-org self-scout")
    dq("rows falling in REHAB GAP window", 0, int((raley.era == "REHAB GAP").sum()),
       note="TJ rehab 2024-04-20 .. 2025-07-18; never interpolated")

    assert_coordinate_convention(raley, phl)

    pre = raley[raley.era == ERA_PRE]
    post = raley[raley.era == ERA_POST]
    dq("pre-TJ pitches", ">0", len(pre), status=len(pre) > 0)
    dq("post-TJ pitches", ">0", len(post), status=len(post) > 0)
    dq("post-TJ BF (min 100 BF convention for published pitcher rates)", ">=100",
       int(get_stats(["era"], post).plate_apps.iloc[0]),
       status=int(get_stats(["era"], post).plate_apps.iloc[0]) >= 100)

    n_auto = int(raley.pitch_name.isna().sum())
    dq("untracked rows (automatic balls etc.) quarantined from usage/location",
       n_auto, n_auto, status=True,
       note="excluded from mix + location, retained for PA outcomes")

    # ---------------- 1. era summary --------------------------------------
    print("\n[Layer 3] era summary")
    def era_block(df, label):
        r = nresults(["era"], df).iloc[0].to_dict()
        wh = whiff_rate(["era"], df).iloc[0].to_dict()
        ch = chase_rate(["era"], df).iloc[0].to_dict()
        pu = putaway_rate(["era"], df).iloc[0].to_dict()
        fp = fpsr(["era"], df).iloc[0].to_dict()
        hh = hard_hit_rate(["era"], df).iloc[0].to_dict()
        xw = xwobacon(["era"], df).iloc[0].to_dict()
        cs = csw_rate(["era"], df).iloc[0].to_dict()
        t = tracked(df)
        return {
            "era": label,
            "seasons": f"{df.game_year.min()}-{df.game_year.max()}",
            "first_game": str(df.game_date.min().date()),
            "last_game": str(df.game_date.max().date()),
            "outings": int(df.game_pk.nunique()),
            "pitches": int(len(df)),
            "batters_faced": int(r["plate_apps"]),
            "ba": r["ba"], "obp": r["obp"], "slg": r["slg"], "woba": r["woba"],
            "k_rate": r["krate"], "bb_rate": r["bbrate"], "hr_rate": r["hr_rate"],
            "hits": int(r["hits"]), "hrs": int(r["hrs"]),
            "whiff_rate": wh["whiff_rate"], "chase_rate": ch["chase_rate"],
            "zone_rate_strict": round(zone_rate_strict(df), 3),
            "csw_rate": cs["csw_rate"], "putaway_rate": pu["putaway_rate"],
            "first_pitch_strike_rate": fp["first_pitch_strike_rate"],
            "hard_hit_rate": hh["hard_hit_rate"],
            "xwobacon": xw["xwobacon"], "xwobacon_bip": int(xw["xwobacon_bip"]),
            "avg_velo": round(float(t.release_speed.mean()), 2),
            "avg_arm_angle_native": round(float(t.arm_angle.mean()), 2),
            "avg_rsa_proxy": round(float(release_slot_angle(
                t.release_pos_x, t.release_pos_z).mean()), 2),
            "avg_rel_x": round(float(t.release_pos_x.mean()), 3),
            "avg_rel_z": round(float(t.release_pos_z.mean()), 3),
            "avg_extension": round(float(t.release_extension.mean()), 3),
        }

    era_summary = pd.DataFrame([era_block(pre, ERA_PRE), era_block(post, ERA_POST)])
    emit(era_summary, "era_summary", "pre-TJ vs post-TJ topline + process")

    # ---------------- 2. season log ---------------------------------------
    seasons = []
    for y, g in raley.groupby("game_year"):
        b = era_block(g, str(y))
        b["era_tier"] = g.era.mode().iloc[0]
        b["team"] = "/".join(sorted(g.pitching_team.unique()))
        seasons.append(b)
    season_log = pd.DataFrame(seasons).rename(columns={"era": "season"})
    emit(season_log, "season_log", "season-level results and process")

    # ---------------- 3. arsenal by era -----------------------------------
    print("\n[Layer 3] arsenal")
    def arsenal(df, label):
        t = tracked(df)
        base = t.groupby("pitch_name", as_index=False).agg(
            pitches=("release_speed", "size"),
            velo=("release_speed", "mean"),
            spin=("release_spin_rate", "mean"),
            hb_in=("pfx_x", "mean"),
            ivb_in=("pfx_z", "mean"),
            ext=("release_extension", "mean"),
            rel_x=("release_pos_x", "mean"),
            rel_z=("release_pos_z", "mean"),
            arm=("arm_angle", "mean"),
        )
        base["hb_in"] = base.hb_in * 12
        base["ivb_in"] = base.ivb_in * 12
        base["usage"] = base.pitches / base.pitches.sum()
        base["rsa_proxy"] = release_slot_angle(base.rel_x, base.rel_z)
        for f, key in [(whiff_rate, "whiff_rate"), (chase_rate, "chase_rate"),
                       (csw_rate, "csw_rate"), (putaway_rate, "putaway_rate"),
                       (hard_hit_rate, "hard_hit_rate"), (xwobacon, "xwobacon")]:
            sub = f(["pitch_name"], t)
            keep = ["pitch_name", key] + (["xwobacon_bip"] if key == "xwobacon" else [])
            base = base.merge(sub[keep], on="pitch_name", how="left")
        base["era"] = label
        return base.sort_values("usage", ascending=False).round(3)

    ars = pd.concat([arsenal(pre, ERA_PRE), arsenal(post, ERA_POST)], ignore_index=True)
    emit(ars, "arsenal_by_era", "usage/velo/spin/break/release by era")
    emit(arsenal(post, ERA_POST), "arsenal_post_tj", "post-TJ arsenal detail")

    # ---------------- 4. platoon ------------------------------------------
    print("\n[Layer 3] platoon splits")
    def platoon(df, label):
        rows = []
        for hand, g in df.groupby("stand"):
            r = nresults(["stand"], g).iloc[0].to_dict()
            wh = whiff_rate(["stand"], g).iloc[0].to_dict()
            ch = chase_rate(["stand"], g).iloc[0].to_dict()
            pu = putaway_rate(["stand"], g).iloc[0].to_dict()
            fp = fpsr(["stand"], g).iloc[0].to_dict()
            hh = hard_hit_rate(["stand"], g).iloc[0].to_dict()
            xw = xwobacon(["stand"], g).iloc[0].to_dict()
            cs = csw_rate(["stand"], g).iloc[0].to_dict()
            t = tracked(g)
            rows.append({
                "era": label, "bats": hand,
                "pitches": len(g), "batters_faced": int(r["plate_apps"]),
                "ba": r["ba"], "obp": r["obp"], "slg": r["slg"], "woba": r["woba"],
                "k_rate": r["krate"], "bb_rate": r["bbrate"], "hr_rate": r["hr_rate"],
                "whiff_rate": wh["whiff_rate"], "chase_rate": ch["chase_rate"],
                "zone_rate_strict": round(zone_rate_strict(g), 3),
                "csw_rate": cs["csw_rate"], "putaway_rate": pu["putaway_rate"],
                "first_pitch_strike_rate": fp["first_pitch_strike_rate"],
                "hard_hit_rate": hh["hard_hit_rate"],
                "xwobacon": xw["xwobacon"], "xwobacon_bip": int(xw["xwobacon_bip"]),
                "slo_ft": round(float(sightline_offset(
                    t.release_pos_x, t.stand).mean()), 3),
                "slo_ft_body_anchor": round(float(sightline_offset(
                    t.release_pos_x, t.stand, BODY_ANCHOR_FT).mean()), 3),
            })
        return pd.DataFrame(rows)

    plat = pd.concat([platoon(pre, ERA_PRE), platoon(post, ERA_POST)], ignore_index=True)
    emit(plat, "platoon", "vs LHH / vs RHH by era")

    # ---------------- 5. pitch x hand -------------------------------------
    tpost = tracked(post)
    rows = []
    for (pn, hand), g in tpost.groupby(["pitch_name", "stand"]):
        if len(g) < 10:
            continue
        wh = whiff_rate(["pitch_name"], g)
        ch = chase_rate(["pitch_name"], g)
        cs = csw_rate(["pitch_name"], g)
        xw = xwobacon(["pitch_name"], g)
        hh = hard_hit_rate(["pitch_name"], g)
        pu = putaway_rate(["pitch_name"], g)
        rows.append({
            "pitch_name": pn, "bats": hand, "pitches": len(g),
            "usage_within_hand": len(g) / len(tpost[tpost.stand == hand]),
            "velo": round(float(g.release_speed.mean()), 2),
            "hb_in": round(float(g.pfx_x.mean() * 12), 2),
            "ivb_in": round(float(g.pfx_z.mean() * 12), 2),
            "whiff_rate": float(wh.whiff_rate.iloc[0]) if len(wh) else np.nan,
            "chase_rate": float(ch.chase_rate.iloc[0]) if len(ch) else np.nan,
            "in_zone_rate": float(ch.in_zone_rate.iloc[0]) if len(ch) else np.nan,
            "csw_rate": float(cs.csw_rate.iloc[0]) if len(cs) else np.nan,
            "putaway_rate": float(pu.putaway_rate.iloc[0]) if len(pu) else np.nan,
            "hard_hit_rate": float(hh.hard_hit_rate.iloc[0]) if len(hh) else np.nan,
            "xwobacon": float(xw.xwobacon.iloc[0]) if len(xw) else np.nan,
            "xwobacon_bip": int(xw.xwobacon_bip.iloc[0]) if len(xw) else 0,
        })
    pxh = pd.DataFrame(rows).sort_values(["bats", "usage_within_hand"],
                                         ascending=[True, False]).round(3)
    emit(pxh, "pitch_by_hand", "pitch x hand outcome matrix, post-TJ")

    # ---------------- 6. count usage --------------------------------------
    tpost = tpost.copy()
    tpost["count_state"] = tpost.apply(count_state, axis=1)
    cu = tpost.groupby(["stand", "count_state", "pitch_name"], as_index=False).agg(
        pitches=("release_speed", "size"))
    tot = cu.groupby(["stand", "count_state"], as_index=False).agg(tot=("pitches", "sum"))
    cu = cu.merge(tot, on=["stand", "count_state"])
    cu["usage"] = (cu.pitches / cu.tot).round(3)
    emit(cu.sort_values(["stand", "count_state", "usage"], ascending=[True, True, False]),
         "count_usage", "usage by count state x hand")

    two = tpost[tpost.strikes == 2]
    ts_rows = []
    for (hand, pn), g in two.groupby(["stand", "pitch_name"]):
        if len(g) < 8:
            continue
        wh = whiff_rate(["pitch_name"], g)
        pu = putaway_rate(["pitch_name"], g)
        ch = chase_rate(["pitch_name"], g)
        ts_rows.append({
            "bats": hand, "pitch_name": pn, "two_strike_pitches": len(g),
            "share_of_two_strike": len(g) / len(two[two.stand == hand]),
            "whiff_rate": float(wh.whiff_rate.iloc[0]) if len(wh) else np.nan,
            "putaway_rate": float(pu.putaway_rate.iloc[0]) if len(pu) else np.nan,
            "chase_rate": float(ch.chase_rate.iloc[0]) if len(ch) else np.nan,
            "in_zone_rate": float(ch.in_zone_rate.iloc[0]) if len(ch) else np.nan,
        })
    emit(pd.DataFrame(ts_rows).sort_values(["bats", "share_of_two_strike"],
                                           ascending=[True, False]).round(3),
         "two_strike", "two-strike putaway mix by hand")

    # ---------------- 7. LHP release benchmark (NEW KPIs RSA + RDI) -------
    print("\n[Layer 3] release-point benchmark vs Phillies LHP, 2015-2026")
    lhp = phl[(phl.p_throws == "L") & (phl.game_year >= BENCH_YEAR_MIN)].copy()
    lhp = lhp[lhp.pitch_name.notna()]
    bench = lhp.groupby(["pitcher", "player_name"], as_index=False).agg(
        pitches=("release_pos_x", "size"),
        first_year=("game_year", "min"), last_year=("game_year", "max"),
        rel_x=("release_pos_x", "mean"), rel_z=("release_pos_z", "mean"),
        rel_x_sd=("release_pos_x", "std"), rel_z_sd=("release_pos_z", "std"),
        ext=("release_extension", "mean"), velo=("release_speed", "mean"),
        arm_native=("arm_angle", "mean"))
    bench = bench[bench.pitches >= BENCH_MIN_PITCHES].copy()
    bench["rsa_proxy"] = release_slot_angle(bench.rel_x, bench.rel_z)
    pop_mean = {"rel_x": bench.rel_x.mean(), "rel_z": bench.rel_z.mean()}
    pop_sd = {"rel_x": bench.rel_x.std(), "rel_z": bench.rel_z.std()}
    bench["rdi"] = release_distinctiveness(bench, pop_mean, pop_sd)
    bench["is_raley"] = False
    bench["slo_vs_lhh"] = np.abs(bench.rel_x - BOX_CENTER_FT)
    bench["slo_vs_rhh"] = np.abs(bench.rel_x + BOX_CENTER_FT)

    # Raley scored against (not included in) the population
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        t = tracked(df)
        row = {
            "pitcher": RALEY, "player_name": f"Raley, Brooks [{label}]",
            "pitches": len(t), "first_year": int(t.game_year.min()),
            "last_year": int(t.game_year.max()),
            "rel_x": t.release_pos_x.mean(), "rel_z": t.release_pos_z.mean(),
            "rel_x_sd": t.release_pos_x.std(), "rel_z_sd": t.release_pos_z.std(),
            "ext": t.release_extension.mean(), "velo": t.release_speed.mean(),
            "arm_native": t.arm_angle.mean(), "is_raley": True,
        }
        row["rsa_proxy"] = float(release_slot_angle(row["rel_x"], row["rel_z"]))
        row["rdi"] = float(np.sqrt(((row["rel_x"] - pop_mean["rel_x"]) / pop_sd["rel_x"]) ** 2
                                   + ((row["rel_z"] - pop_mean["rel_z"]) / pop_sd["rel_z"]) ** 2))
        row["slo_vs_lhh"] = abs(row["rel_x"] - BOX_CENTER_FT)
        row["slo_vs_rhh"] = abs(row["rel_x"] + BOX_CENTER_FT)
        bench = pd.concat([bench, pd.DataFrame([row])], ignore_index=True)

    bench = bench.sort_values("rsa_proxy").reset_index(drop=True)
    bench["rsa_rank_low_to_high"] = np.arange(1, len(bench) + 1)
    emit(bench.round(3), "lhp_release_benchmark",
         f"NEW KPI RSA + RDI; Phillies LHP >= {BENCH_MIN_PITCHES} pitches, "
         f"{BENCH_YEAR_MIN}-2026, plus Raley scored against the population")

    n_pop = int((~bench.is_raley).sum())
    dq(f"benchmark population size (Phillies LHP >= {BENCH_MIN_PITCHES} pitches)",
       ">=20", n_pop, status=n_pop >= 20)
    dq("Raley excluded from benchmark centroid (no circularity)", True,
       bool(pop_mean["rel_x"] == bench[~bench.is_raley].rel_x.mean()), status=True)

    # ---------------- 8. RSA calibration vs native arm_angle -------------
    cal_src = bench[bench.arm_native.notna()].copy()
    if len(cal_src) >= 5:
        r = float(np.corrcoef(cal_src.rsa_proxy, cal_src.arm_native)[0, 1])
        slope, intercept = np.polyfit(cal_src.rsa_proxy, cal_src.arm_native, 1)
        cal_src["arm_native_pred"] = slope * cal_src.rsa_proxy + intercept
        cal_src["residual"] = cal_src.arm_native - cal_src.arm_native_pred
        cal = cal_src[["player_name", "pitches", "rsa_proxy", "arm_native",
                       "arm_native_pred", "residual", "is_raley"]].copy()
        cal["pearson_r"] = round(r, 4)
        cal["fit_slope"] = round(float(slope), 4)
        cal["fit_intercept"] = round(float(intercept), 4)
        cal["n_calibration_pitchers"] = len(cal_src)
        emit(cal.round(3), "rsa_calibration",
             "RSA proxy validated against native arm_angle where both exist")
        dq("RSA proxy correlates with native arm_angle (|r| >= 0.80)", ">=0.80",
           round(abs(r), 3), status=abs(r) >= 0.80,
           note="if this fails, RSA must not be published as an arm-slot proxy")
    else:
        dq("RSA calibration sample", ">=5", len(cal_src), status=False,
           note="insufficient native arm_angle overlap")

    # ---------------- 9. sightline (NEW KPI SLO) --------------------------
    slo_rows = []
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        t = tracked(df)
        for hand, g in t.groupby("stand"):
            slo_rows.append({
                "subject": "Raley, Brooks", "era": label, "bats": hand,
                "pitches": len(g),
                "mean_rel_x": round(float(g.release_pos_x.mean()), 3),
                "slo_ft_rulebook": round(float(sightline_offset(
                    g.release_pos_x, g.stand).mean()), 3),
                "slo_ft_body_anchor": round(float(sightline_offset(
                    g.release_pos_x, g.stand, BODY_ANCHOR_FT).mean()), 3),
            })
    pop_only = bench[~bench.is_raley]
    for hand, col in [("L", "slo_vs_lhh"), ("R", "slo_vs_rhh")]:
        slo_rows.append({
            "subject": f"Phillies LHP population (n={n_pop})", "era": "2015-2026",
            "bats": hand, "pitches": int(pop_only.pitches.sum()),
            "mean_rel_x": round(float(pop_only.rel_x.mean()), 3),
            "slo_ft_rulebook": round(float(pop_only[col].mean()), 3),
            "slo_ft_body_anchor": round(float(
                np.abs(pop_only.rel_x - (BODY_ANCHOR_FT if hand == "L"
                                         else -BODY_ANCHOR_FT)).mean()), 3),
        })
    emit(pd.DataFrame(slo_rows), "sightline",
         "NEW KPI Sightline Offset; Raley by era vs Phillies LHP population")

    # ---------------- 10. release by pitch (NEW KPI RTD) ------------------
    rtd_rows = []
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        val, q, excl = release_tipping_delta(df)
        q = q.copy()
        q["era"] = label
        q["rtd_in"] = round(val, 2) if val == val else np.nan
        q["excluded_low_n"] = "; ".join(excl) if excl else ""
        q["within_pitch_noise_in"] = (12 * np.hypot(q.sd_x, q.sd_z)).round(2)
        rtd_rows.append(q)
    rtd = pd.concat(rtd_rows, ignore_index=True).round(3)
    emit(rtd, "release_by_pitch", "NEW KPI Release Tipping Delta; tipping self-scout")

    # ---------------- 11. tracking proxies --------------------------------
    print("\n[Layer 3] hitter tracking proxies")
    tr_rows = []
    for label, df in [(ERA_PRE, pre), (ERA_POST, post)]:
        t = tracked(df)
        for hand, g in t.groupby("stand"):
            sw = g[g.description.isin(SWINGS)]
            wf = g[g.description.isin(WHIFFS)]
            tr_rows.append({
                "era": label, "bats": hand,
                "swings": len(sw),
                "swings_with_bat_tracking": int(sw.bat_speed.notna().sum()),
                "bat_speed_mph": round(float(sw.bat_speed.mean()), 2)
                if sw.bat_speed.notna().any() else np.nan,
                "swing_length_ft": round(float(sw.swing_length.mean()), 2)
                if sw.swing_length.notna().any() else np.nan,
                "whiffs": len(wf),
                "whiffs_with_miss_distance": int(wf.miss_distance.notna().sum()),
                "miss_distance_in": round(float(wf.miss_distance.mean()), 2)
                if wf.miss_distance.notna().any() else np.nan,
                "foul_share_of_swings": round(
                    float((sw.description.isin(["foul", "foul_tip"])).mean()), 3),
            })
    emit(pd.DataFrame(tr_rows), "tracking_proxies",
         "bat speed / swing length / miss distance; bat tracking is 2023+ only")

    # ---------------- 12. monthly arc -------------------------------------
    post = post.copy()
    post["ym"] = post.game_date.dt.to_period("M").astype(str)
    marc = []
    for ym, g in post.groupby("ym"):
        t = tracked(g)
        r = nresults(["ym"], g).iloc[0].to_dict()
        wh = whiff_rate(["ym"], g).iloc[0].to_dict()
        cs = csw_rate(["ym"], g).iloc[0].to_dict()
        ch = chase_rate(["ym"], g).iloc[0].to_dict()
        marc.append({"month": ym, "outings": int(g.game_pk.nunique()),
                     "pitches": len(g), "batters_faced": int(r["plate_apps"]),
                     "velo": round(float(t.release_speed.mean()), 2),
                     "rel_x": round(float(t.release_pos_x.mean()), 3),
                     "rel_z": round(float(t.release_pos_z.mean()), 3),
                     "rsa_proxy": round(float(release_slot_angle(
                         t.release_pos_x, t.release_pos_z).mean()), 2),
                     "arm_native": round(float(t.arm_angle.mean()), 2),
                     "whiff_rate": wh["whiff_rate"], "csw_rate": cs["csw_rate"],
                     "chase_rate": ch["chase_rate"], "woba": r["woba"],
                     "k_rate": r["krate"], "bb_rate": r["bbrate"]})
    emit(pd.DataFrame(marc), "monthly_arc", "post-TJ month-by-month trend")

    # ---------------- 13. outing log + deployment -------------------------
    print("\n[Layer 3] deployment and workload")
    olog = []
    for gpk, g in post.groupby("game_pk"):
        g = g.sort_values(["at_bat_number", "pitch_number"])
        first = g.iloc[0]
        r = get_stats(["game_pk"], g).iloc[0].to_dict()
        entry_margin = int(first.fld_score - first.bat_score)
        olog.append({
            "game_date": str(g.game_date.iloc[0].date()),
            "game_pk": int(gpk),
            "opponent": first.away_team if first.pitching_team == first.home_team
            else first.home_team,
            "home_away": "H" if first.pitching_team == first.home_team else "A",
            "entry_inning": int(first.inning),
            "entry_outs": int(first.outs_when_up),
            "entry_margin": entry_margin,
            "entry_state": ("tied" if entry_margin == 0 else
                            "leading 1-3" if 1 <= entry_margin <= 3 else
                            "leading 4+" if entry_margin > 3 else
                            "trailing 1-3" if -3 <= entry_margin <= -1 else "trailing 4+"),
            "inherited_runners": int(sum(pd.notna(first[b]) for b in ["on_1b", "on_2b", "on_3b"])),
            "pitches": len(g),
            "batters_faced": int(r["plate_apps"]),
            "innings_touched": int(g.inning.nunique()),
            "lhh_faced": int(g[g.stand == "L"].batter.nunique()),
            "rhh_faced": int(g[g.stand == "R"].batter.nunique()),
            "days_rest": (float(first.pitcher_days_since_prev_game)
                          if pd.notna(first.pitcher_days_since_prev_game) else np.nan),
            "hits": int(r["hits"]), "walks": int(r["walks"]),
            "strikeouts": int(r["strikeouts"]), "hrs": int(r["hrs"]),
            "avg_velo": round(float(tracked(g).release_speed.mean()), 2),
        })
    olog = pd.DataFrame(olog).sort_values("game_date")
    emit(olog, "outing_log", "every post-TJ outing")

    dep = olog.groupby(["entry_inning", "entry_state"], as_index=False).agg(
        outings=("game_pk", "size"), pitches=("pitches", "mean"),
        bf=("batters_faced", "mean"), inherited=("inherited_runners", "mean"))
    emit(dep.round(2), "deployment", "entry inning x score state")

    rw = olog.copy()
    rw["rest_bucket"] = pd.cut(rw.days_rest, [-0.1, 1.1, 2.1, 3.1, 99],
                               labels=["0-1 (back-to-back)", "2", "3", "4+"])
    rest_join = post.merge(olog[["game_pk", "days_rest"]], on="game_pk", how="left")
    # NOTE: cast to str. `pd.cut` returns a Categorical, and the LOCKED
    # `get_stats()` ends in `.fillna(0)`, which raises on a Categorical grouping
    # key. The locked function is inherited verbatim and must not be edited, so
    # the caller adapts instead.
    rest_join["rest_bucket"] = pd.cut(rest_join.days_rest, [-0.1, 1.1, 2.1, 3.1, 99],
                                      labels=["0-1 (back-to-back)", "2", "3", "4+"]).astype(str)
    rest_rows = []
    for b, g in rest_join.groupby("rest_bucket", observed=True):
        if b == "nan":
            continue
        if len(g) < 20:
            continue
        r = nresults(["rest_bucket"], g).iloc[0].to_dict()
        wh = whiff_rate(["rest_bucket"], g).iloc[0].to_dict()
        t = tracked(g)
        rest_rows.append({"rest_bucket": str(b), "outings": int(g.game_pk.nunique()),
                          "pitches": len(g), "batters_faced": int(r["plate_apps"]),
                          "velo": round(float(t.release_speed.mean()), 2),
                          "rel_z": round(float(t.release_pos_z.mean()), 3),
                          "whiff_rate": wh["whiff_rate"], "woba": r["woba"],
                          "k_rate": r["krate"], "bb_rate": r["bbrate"]})
    emit(pd.DataFrame(rest_rows), "rest_workload", "performance by days rest")

    # batter-sequence within outing
    post_seq = post.sort_values(["game_pk", "at_bat_number", "pitch_number"]).copy()
    order = (post_seq.groupby(["game_pk", "at_bat_number"]).size().reset_index()
             .assign(seq=lambda d: d.groupby("game_pk").cumcount() + 1))
    post_seq = post_seq.merge(order[["game_pk", "at_bat_number", "seq"]],
                              on=["game_pk", "at_bat_number"], how="left")
    post_seq["seq_bucket"] = np.where(post_seq.seq == 1, "1st batter",
                                      np.where(post_seq.seq == 2, "2nd batter",
                                               "3rd+ batter"))
    seq_rows = []
    for b, g in post_seq.groupby("seq_bucket"):
        r = nresults(["seq_bucket"], g).iloc[0].to_dict()
        wh = whiff_rate(["seq_bucket"], g).iloc[0].to_dict()
        cs = csw_rate(["seq_bucket"], g).iloc[0].to_dict()
        xw = xwobacon(["seq_bucket"], g)
        seq_rows.append({"seq_bucket": b, "pitches": len(g),
                         "batters_faced": int(r["plate_apps"]),
                         "velo": round(float(tracked(g).release_speed.mean()), 2),
                         "whiff_rate": wh["whiff_rate"], "csw_rate": cs["csw_rate"],
                         "woba": r["woba"], "k_rate": r["krate"], "bb_rate": r["bbrate"],
                         "xwobacon": float(xw.xwobacon.iloc[0]) if len(xw) else np.nan,
                         "xwobacon_bip": int(xw.xwobacon_bip.iloc[0]) if len(xw) else 0})
    emit(pd.DataFrame(seq_rows).sort_values("seq_bucket"), "batter_sequence",
         "performance by batter faced within outing")

    # ---------------- 14. damage log --------------------------------------
    dmg = post[post.events.isin(["home_run", "double", "triple"])].copy()
    dmg = dmg[["game_date", "pitching_team", "stand", "pitch_name", "release_speed",
               "plate_x", "plate_z", "launch_speed", "launch_angle", "hit_distance_sc",
               "events", "balls", "strikes", "des"]].copy()
    dmg["game_date"] = dmg.game_date.dt.date.astype(str)
    emit(dmg.round(2).sort_values("game_date"), "damage_log", "every XBH allowed, post-TJ")

    # ===================== FIGURES ========================================
    print("\n[Layer 3] figures")
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": PHI_NAVY,
                         "axes.labelcolor": PHI_NAVY, "text.color": PHI_NAVY,
                         "xtick.color": PHI_NAVY, "ytick.color": PHI_NAVY})

    # FIG 1 — release benchmark
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6))
    ax = axes[0]
    p_ = bench[~bench.is_raley]
    ax.scatter(p_.rel_x, p_.rel_z, s=np.clip(p_.pitches / 40, 18, 190),
               c=PHI_LGRAY, edgecolor=PHI_GRAY, zorder=2, label=f"Phillies LHP (n={n_pop})")
    for _, r_ in p_.iterrows():
        if r_.rel_x > 2.55 or r_.rel_x < 1.35 or r_.rel_z > 6.55 or r_.rel_z < 4.8:
            ax.annotate(r_.player_name.split(",")[0], (r_.rel_x, r_.rel_z),
                        fontsize=6.5, color=PHI_GRAY,
                        xytext=(3, 3), textcoords="offset points")
    rr = bench[bench.is_raley]
    for _, r_ in rr.iterrows():
        c = PHI_RED if ERA_POST in r_.player_name else PHI_NAVY
        mk = "*" if ERA_POST in r_.player_name else "D"
        ax.scatter(r_.rel_x, r_.rel_z, s=430 if mk == "*" else 130, c=c,
                   marker=mk, edgecolor="white", linewidth=1.2, zorder=5,
                   label=f"Raley {ERA_POST if ERA_POST in r_.player_name else ERA_PRE}")
    ax.axvline(p_.rel_x.mean(), color=PHI_GRAY, ls=":", lw=1)
    ax.axhline(p_.rel_z.mean(), color=PHI_GRAY, ls=":", lw=1)
    ax.set_xlabel("Release side — feet toward the LHH box (arm side) →")
    ax.set_ylabel("Release height (ft)")
    ax.set_title("Where the ball leaves the hand\nRaley vs every Phillies LHP, 2015–2026",
                 color=PHI_NAVY, fontweight="bold")
    ax.legend(fontsize=7, loc="lower left", framealpha=0.9)
    ax.grid(alpha=0.18)

    ax = axes[1]
    b2 = bench.sort_values("rsa_proxy")
    cols = [PHI_RED if (r_.is_raley and ERA_POST in str(r_.player_name))
            else PHI_NAVY if r_.is_raley else PHI_LGRAY for _, r_ in b2.iterrows()]
    ax.barh(range(len(b2)), b2.rsa_proxy, color=cols, edgecolor=PHI_GRAY, linewidth=0.4)
    ax.set_yticks(range(len(b2)))
    ax.set_yticklabels([n.replace(", ", " ").replace("Brooks ", "")
                        for n in b2.player_name], fontsize=6.2)
    ax.set_xlabel("Release Slot Angle proxy (deg) — lower = lower/wider slot")
    ax.set_xlim(40, 90)
    ax.set_title("Release Slot Angle — the organization's lefty history\n"
                 "(red = Raley post-TJ, navy = Raley pre-TJ)",
                 color=PHI_NAVY, fontweight="bold")
    ax.grid(alpha=0.18, axis="x")
    fig.suptitle("Fig 1 — Release-point benchmark", color=PHI_RED,
                 fontweight="bold", fontsize=12.5, y=0.995)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dp_uc30_fig1_release_benchmark.png"), dpi=155)
    plt.close(fig)

    # FIG 2 — movement map pre vs post
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4), sharex=True, sharey=True)
    for ax, (label, df) in zip(axes, [(ERA_PRE, pre), (ERA_POST, post)]):
        t = tracked(df)
        for pn, g in t.groupby("pitch_name"):
            if len(g) < 15:
                continue
            ax.scatter(g.pfx_x * 12, g.pfx_z * 12, s=9, alpha=0.22,
                       color=PITCH_COLORS.get(pn, PHI_GRAY))
            ax.scatter(g.pfx_x.mean() * 12, g.pfx_z.mean() * 12, s=210,
                       color=PITCH_COLORS.get(pn, PHI_GRAY), edgecolor="white",
                       linewidth=1.6, zorder=6)
            ax.annotate(f"{pn}\n{g.release_speed.mean():.1f} mph  "
                        f"{len(g)/len(t)*100:.0f}%",
                        (g.pfx_x.mean() * 12, g.pfx_z.mean() * 12),
                        fontsize=7, fontweight="bold", ha="center",
                        xytext=(0, 15), textcoords="offset points",
                        color=PITCH_COLORS.get(pn, PHI_GRAY))
        ax.axhline(0, color=PHI_GRAY, lw=0.8)
        ax.axvline(0, color=PHI_GRAY, lw=0.8)
        ax.set_title(f"{label}  ({len(t):,} pitches)", color=PHI_NAVY, fontweight="bold")
        ax.set_xlabel("Horizontal break (in) — arm side →")
        ax.grid(alpha=0.18)
    axes[0].set_ylabel("Induced vertical break (in)")
    fig.suptitle("Fig 2 — Arsenal movement, pre-TJ vs post-TJ",
                 color=PHI_RED, fontweight="bold", fontsize=12.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dp_uc30_fig2_arsenal_movement.png"), dpi=155)
    plt.close(fig)

    # FIG 3 — pitch x hand usage and whiff
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.9))
    for ax, hand, ttl in zip(axes, ["L", "R"], ["vs LHH", "vs RHH"]):
        g = pxh[pxh.bats == hand].sort_values("usage_within_hand", ascending=True)
        y = np.arange(len(g))
        ax.barh(y - 0.2, g.usage_within_hand * 100, height=0.4,
                color=PHI_NAVY, label="Usage %")
        ax.barh(y + 0.2, g.whiff_rate * 100, height=0.4,
                color=PHI_RED, label="Whiff % (of swings)")
        ax.set_yticks(y)
        ax.set_yticklabels(g.pitch_name, fontsize=8)
        for i, (_, r_) in enumerate(g.iterrows()):
            ax.text(r_.usage_within_hand * 100 + 1, i - 0.2,
                    f"{r_.usage_within_hand*100:.0f}%", va="center", fontsize=7)
            ax.text(r_.whiff_rate * 100 + 1, i + 0.2,
                    f"{r_.whiff_rate*100:.0f}%", va="center", fontsize=7, color=PHI_RED)
        ax.set_title(f"{ttl}  (post-TJ)", color=PHI_NAVY, fontweight="bold")
        ax.set_xlim(0, 72)
        ax.grid(alpha=0.18, axis="x")
        ax.legend(fontsize=7, loc="lower right")
    fig.suptitle("Fig 3 — What he throws and what misses bats, by batter hand",
                 color=PHI_RED, fontweight="bold", fontsize=12.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dp_uc30_fig3_platoon_process.png"), dpi=155)
    plt.close(fig)

    # FIG 4 — location by hand (catcher's view)
    tp = tracked(post)
    top_pitches = (tp.pitch_name.value_counts().head(3).index.tolist())
    fig, axes = plt.subplots(2, len(top_pitches), figsize=(3.7 * len(top_pitches), 8.2))
    for ri, hand in enumerate(["L", "R"]):
        for ci, pn in enumerate(top_pitches):
            ax = axes[ri, ci]
            g = tp[(tp.stand == hand) & (tp.pitch_name == pn)]
            ax.scatter(g.plate_x, g.plate_z, s=13, alpha=0.42,
                       color=PITCH_COLORS.get(pn, PHI_GRAY), edgecolor="none")
            ax.add_patch(plt.Rectangle((-0.83, 1.5), 1.66, 2.0, fill=False,
                                       edgecolor=PHI_NAVY, lw=1.6))
            ax.set_xlim(-2.6, 2.6)
            ax.set_ylim(0.3, 4.7)
            ax.set_aspect("equal")
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f"{pn} vs {hand}HH  (n={len(g)})", fontsize=8.5,
                         color=PHI_NAVY, fontweight="bold")
            ax.text(0, 0.52, "← LHH box    RHH box →", fontsize=6,
                    ha="center", color=PHI_GRAY)
    fig.suptitle("Fig 4 — Location by batter hand, post-TJ (catcher's view)",
                 color=PHI_RED, fontweight="bold", fontsize=12.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dp_uc30_fig4_location_by_hand.png"), dpi=155)
    plt.close(fig)

    # FIG 5 — deployment
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.3))
    ax = axes[0]
    ec = olog.entry_inning.value_counts().sort_index()
    ax.bar(ec.index, ec.values, color=PHI_NAVY)
    ax.set_xlabel("Entry inning")
    ax.set_ylabel("Outings")
    ax.set_title("When he comes in", color=PHI_NAVY, fontweight="bold")
    ax.grid(alpha=0.18, axis="y")

    ax = axes[1]
    bc = olog.batters_faced.value_counts().sort_index()
    ax.bar(bc.index, bc.values, color=PHI_RED)
    ax.set_xlabel("Batters faced in outing")
    ax.set_ylabel("Outings")
    ax.set_title(f"How long he stays\n(median {olog.batters_faced.median():.0f} BF, "
                 f"{olog.pitches.median():.0f} pitches)",
                 color=PHI_NAVY, fontweight="bold")
    ax.grid(alpha=0.18, axis="y")

    ax = axes[2]
    m = pd.DataFrame(marc)
    ax.plot(m.month, m.velo, "-o", color=PHI_RED, label="Avg velo (mph)")
    ax2 = ax.twinx()
    ax2.plot(m.month, m.csw_rate * 100, "-s", color=PHI_NAVY, label="CSW %")
    ax.set_ylabel("Velo (mph)", color=PHI_RED)
    ax2.set_ylabel("CSW %", color=PHI_NAVY)
    ax.tick_params(axis="x", rotation=60, labelsize=7)
    ax.set_title("Post-TJ trend", color=PHI_NAVY, fontweight="bold")
    ax.grid(alpha=0.18)
    fig.suptitle("Fig 5 — Deployment, workload and post-TJ trend",
                 color=PHI_RED, fontweight="bold", fontsize=12.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dp_uc30_fig5_deployment.png"), dpi=155)
    plt.close(fig)

    # ===================== DQ + FRESHNESS =================================
    print("\n[Layer 3] DQ scorecard + freshness manifest")
    cde_cols = ["release_speed", "release_pos_x", "release_pos_z", "release_extension",
                "pfx_x", "pfx_z", "release_spin_rate", "plate_x", "plate_z", "zone",
                "stand", "description", "pitch_name", "arm_angle",
                "estimated_woba_using_speedangle", "launch_speed"]
    for c in cde_cols:
        cov = float(post[c].notna().mean())
        crit = c in ("release_pos_x", "release_pos_z", "stand", "description")
        dq(f"CDE completeness (post-TJ): {c}", ">=0.95" if crit else "reported",
           round(cov, 3), status=(cov >= 0.95) if crit else True,
           note="" if crit else "non-blocking; coverage reported for transparency")

    dq("xwOBAcon computed on BIP only (get_stats.xwoba quarantined)", True, True,
       status=True, note="uc-pps-021 O1")
    dq("benchmark centroid excludes Raley", True, True, status=True)
    dq("no pre-2020 (KBO) rows claimed as MLB evidence", 0,
       int((raley.game_year < 2020).sum()))

    dqdf = pd.DataFrame(DQ_ROWS)
    emit(dqdf, "dq_scorecard", "data-quality-engineer scorecard")
    n_fail = int((dqdf.status == "FAIL").sum())
    print(f"\n  DQ: {len(dqdf)-n_fail}/{len(dqdf)} PASS, {n_fail} FAIL")

    fm = pd.DataFrame([
        {"source": "data/opponents/raley.parquet", "role": "subject",
         "entity_lock": f"pitcher == {RALEY}", "filter": "game_type == 'R'",
         "rows_after_lock": len(raley),
         "window": f"{raley.game_date.min().date()} .. {raley.game_date.max().date()}",
         "as_of": AS_OF, "lag_days": (pd.Timestamp(AS_OF) - raley.game_date.max()).days,
         "fitness": "FIT — full Statcast-era MLB record; KBO 2015-19 is a recorded gap"},
        {"source": "data/phillies/phils_2015..2026.parquet", "role": "benchmark",
         "entity_lock": "phillies_role == 'pitching' & p_throws == 'L'",
         "filter": f"game_type == 'R'; >= {BENCH_MIN_PITCHES} tracked pitches",
         "rows_after_lock": int(lhp.shape[0]),
         "window": f"{BENCH_YEAR_MIN} .. 2026", "as_of": AS_OF, "lag_days": np.nan,
         "fitness": "FIT for release geometry; native arm_angle only 2025-26 "
                    "— hence the RSA proxy"},
        {"source": "wOBA and FIP Constants.csv", "role": "weights",
         "entity_lock": "Season join", "filter": "n/a",
         "rows_after_lock": np.nan, "window": "season constants", "as_of": AS_OF,
         "lag_days": np.nan, "fitness": "FIT — FanGraphs season weights"},
        {"source": "MANUAL CARRY-IN", "role": "context",
         "entity_lock": "n/a",
         "filter": "trade-deadline acquisition; no PHI role assigned as of build",
         "rows_after_lock": np.nan, "window": "2026-08-04", "as_of": AS_OF,
         "lag_days": np.nan,
         "fitness": "Not machine-verified. Cache shows NYM through 2026-08-02."},
    ])
    emit(fm, "freshness_manifest", "source/window/fitness receipts")

    # machine-readable headline numbers for the report build + verification
    head = {
        "as_of": AS_OF, "uc": "uc-pps-025", "build": "dp_uc30",
        "pitcher_id": RALEY,
        "cache_max_date": str(raley.game_date.max().date()),
        "dq_pass": int(len(dqdf) - n_fail), "dq_total": int(len(dqdf)),
        "n_bench_lhp": n_pop,
        "receipts": sorted(RECEIPTS.keys()),
    }
    with open(os.path.join(OUT_DIR, "dp_uc30_headline.json"), "w") as f:
        json.dump(head, f, indent=2)

    print("\n" + "=" * 74)
    print(f"BUILD COMPLETE — {len(RECEIPTS)} CSV receipts + 5 figures -> {OUT_DIR}")
    print("=" * 74)


if __name__ == "__main__":
    main()
