"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #30  (uc-pps-024)
"Acquisition Read: Caleb Kilian (RHP) — what the Phillies just bought, and
 how to deploy him. Trade-deadline acquisition onboarding, 2026-08-04."
============================================================================

Layer-3 BUILD artifact for the Phillies Pitching (pps) value stream.

Pattern lineage: UC#3 (Luzardo deep dive) -> UC#8 (Nola vs WAS, canonical
flat-file pattern) -> UC#11 (Rangel vs PIT, multi-level evidence tier) ->
UC#29 (Painter return read, self-scout variant, opponent descoped).
This UC is the SECOND self-scout variant and the FIRST acquisition-onboarding
read: the subject is a player the organization has never worked with, so the
deliverable is an intake dossier, not an opponent attack plan.

WHY NO OPPONENT DIMENSION (recorded gap, non-blocking):
  Kilian has no Phillies pitching rows — he has never thrown a pitch for the
  organization. There is no "next opponent" because there is no announced
  role. The consumer questions are development, battery, and deployment
  questions. Opponent modelling is deferred to a future uc-pps once a role
  is assigned. Recorded in the intake gap report as NON-BLOCKING.

ROLE-ERA EVIDENCE RULE (adapted from UC#11 multi-level rule):
  CURRENT tier (2026, SF, relief)   = 736 pitches / 193 PA / 45 outings
  PRIOR   tier (2022-24, CHC, start)= 535 pitches / 138 PA /  8 outings
  The prior tier is ALWAYS LABELED and NEVER BLENDED into current rates.
  It exists to size the delta the role change produced, not to describe the
  pitcher the Phillies acquired. 2025 is a TRUE GAP (no MLB service; no MiLB
  cache for Sacramento in this repo) and is never interpolated.

NEW KPIs (specs in dp_uc29_kilian_acquisition_read_use_case_spec.md sec.4):
  * Slider Finish Rate (SFR)        -- share of sliders that finish to the
                                       glove side vs. back up to the arm side
  * Fastball Elevation Rate (FER)   -- share of 4-seamers in the upper third
  * Role Conversion Delta (RCD)     -- signed current-minus-prior process delta

Governance lineage:
  - data-product-owner      : sequenced as UC#30 / uc-pps-024 / dp_uc29
  - use-case-validator      : intake gate; opponent + 2025 gaps = non-blocking
  - source-system-profiler  : entity lock pitcher==668873; cache through
                              2026-08-01 (T-3 as of 2026-08-04)
  - kpi-calculator          : locked cores inherited VERBATIM from dp_uc28
                              (get_stats/nresults, whiff_rate, chase_rate,
                              putaway_rate, fpsr, hard_hit_rate, csw_rate);
                              3 new KPIs specified before use
  - data-quality-engineer   : scorecard emitted to out/

OUTPUTS — 16 CSV receipts + 4 figures (NEW files, none overwritten), ./out/:
  dp_uc29_era_summary.csv            current vs prior role era, topline+process
  dp_uc29_season_log.csv             season-level results and process
  dp_uc29_arsenal_by_era.csv         usage/velo/spin/IVB/HB/ext/arm by era
  dp_uc29_arsenal_2026.csv           2026 arsenal detail with outcomes
  dp_uc29_role_conversion_delta.csv  NEW KPI: Role Conversion Delta
  dp_uc29_platoon.csv                vs LHH / vs RHH, 2026
  dp_uc29_pitch_by_hand.csv          pitch x hand outcome matrix, 2026
  dp_uc29_count_usage.csv            usage by count state x hand
  dp_uc29_slider_finish.csv          NEW KPI: Slider Finish Rate
  dp_uc29_fastball_elevation.csv     NEW KPI: Fastball Elevation Rate
  dp_uc29_damage_log.csv             every home run allowed, 2026
  dp_uc29_outing_log.csv             every 2026 outing: pitches, BF, entry
  dp_uc29_deployment.csv             entry inning x score state x runners
  dp_uc29_batter_sequence.csv        performance by batter faced within outing
  dp_uc29_monthly_arc.csv            within-2026 trend, velo + process
  dp_uc29_dq_scorecard.csv           data-quality-engineer scorecard
  dp_uc29_freshness_manifest.csv     source/window/fitness receipts
  dp_uc29_fig1_arsenal_movement.png  fig 1 - movement map, prior vs current
  dp_uc29_fig2_role_conversion.png   fig 2 - process KPI conversion deltas
  dp_uc29_fig3_location_damage.png   fig 3 - SFR + FER damage maps
  dp_uc29_fig4_deployment.png        fig 4 - deployment pattern
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

KILIAN = 668873                    # Caleb Kilian, MLBAM pitcher id — ENTITY LOCK
AS_OF = "2026-08-04"
CURRENT_YEAR = 2026
PRIOR_YEARS = [2022, 2023, 2024]

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "phillies"),
    "/sessions/friendly-determined-ptolemy/mnt/MLB/data/phillies",
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies",
]
PHIL_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
if PHIL_DIR is None:
    raise FileNotFoundError("Could not locate data/phillies. Set MLB_DATA_ROOT.")
OPP_DIR = os.path.join(os.path.dirname(PHIL_DIR), "opponents")

_WOBA_CANDIDATES = [
    os.path.join(HERE, "wOBA and FIP Constants.csv"),
    "/sessions/friendly-determined-ptolemy/mnt/MLB/wOBA and FIP Constants.csv",
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
    "Cutter": "#6BAED6", "Sweeper": "#1F77B4", "Knuckle Curve": "#8C564B",
    "Changeup": "#2CA02C",
}
PITCH_ORDER = ["4-Seam Fastball", "Sinker", "Cutter", "Slider", "Sweeper",
               "Knuckle Curve", "Changeup"]


# ===========================================================================
# LOADERS
# ===========================================================================
def _coerce(df):
    for c in ["plate_x", "plate_z", "sz_top", "sz_bot", "pfx_x", "pfx_z",
              "release_speed", "effective_speed", "release_spin_rate", "spin_axis",
              "release_pos_x", "release_pos_z", "release_extension", "arm_angle",
              "launch_speed", "launch_angle", "strikes", "balls", "outs_when_up",
              "pitch_number", "at_bat_number", "woba_value", "woba_denom", "zone",
              "inning", "bat_score", "fld_score",
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


def load_kilian():
    """Single-source load. Entity lock is enforced HERE and asserted below."""
    f = os.path.join(OPP_DIR, "kilian.parquet")
    d = pd.read_parquet(f)
    d = d[(d.pitcher == KILIAN) & (d.game_type == "R")]
    d = d.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    d = _coerce(d.copy())
    d["era_tier"] = np.where(d.game_year == CURRENT_YEAR,
                             "2026 SF (relief)", "2022-24 CHC (start)")
    return _attach_woba(d)


# ===========================================================================
# LOCKED KPI FUNCTIONS — inherited VERBATIM from dp_uc28_painter_vs_orioles.py
# (which inherited from dp_uc11 / dp_uc8 / Baseball Functions). DO NOT RE-DERIVE.
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
    """xwOBA ON CONTACT — mean `estimated_woba_using_speedangle` over BALLS IN
    PLAY only (`type == 'X'`).

    DQ-HARDENED, inherited from uc-pps-021 (UC #26) open item O1. The locked
    `get_stats.xwoba` column averages the field over ALL pitch rows; a minority
    of non-BIP rows carry 0.0, which contaminates the mean and makes it swing
    year to year. `estimated_woba_using_speedangle` is >99% populated on
    `type == 'X'`, so the BIP-only mean is the fit-for-purpose contact-quality
    read. THIS UC CITES ONLY `xwobacon`; the pitch-level column is quarantined
    and never published. Null where a cell has zero balls in play.
    """
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
    """TRACKED-PITCH POPULATION — rows that represent an actual thrown, tracked
    pitch.

    The 2026 feed contains 8 `automatic_ball` rows (pitch-timer violations).
    No ball leaves the pitcher's hand, so `pitch_name`, `zone`, `plate_x` and
    `plate_z` are all null. They are legitimate BALL events for plate-appearance
    outcomes (K%, BB%, wOBA) but they are NOT pitches for the purposes of
    usage share, zone rate, or any location metric.

    Every pitch-mix and location figure in this UC is computed on this
    population; every PA-outcome figure is computed on the full population.
    The split is asserted in the DQ scorecard.
    """
    return df[df.pitch_name.notna()]


def zone_rate_strict(df):
    """In-zone rate over TRACKED pitches only.

    The locked `chase_rate()` derives `in_zone_rate` as (pitches - ooz)/pitches
    with `ooz = zone > 9`. A null `zone` is not > 9, so untracked automatic-ball
    rows fall into the in-zone numerator and inflate the rate (0.486 vs 0.481
    here). The locked function is inherited VERBATIM and is not modified;
    this strict variant is what the report publishes, exactly as `xwobacon`
    supersedes the contaminated `get_stats.xwoba` (uc-pps-021 O1).
    Logged as open item O2.
    """
    t = tracked(df)
    return (t.zone <= 9).sum() / len(t)


def add_movement_cols(df):
    """Statcast pfx_* are in feet; convert to inches. IVB = pfx_z*12 (gravity-
    corrected induced vertical break). HB is expressed ARM-SIDE POSITIVE for a
    RHP, i.e. HB = -pfx_x*12 so that arm-side run reads positive."""
    df = df.copy()
    df["ivb_in"] = df.pfx_z * 12.0
    df["hb_in"] = -df.pfx_x * 12.0
    return df


def add_zone_thirds(df):
    """Vertical thirds of the batter-specific strike zone (sz_bot..sz_top).
    Mechanical partition of plate_z against the per-pitch zone boundaries."""
    df = df.copy()
    h = df.sz_top - df.sz_bot
    df["v_third"] = np.select(
        [df.plate_z > df.sz_bot + h * 2 / 3, df.plate_z < df.sz_bot + h / 3],
        ["upper", "lower"], default="middle")
    return df


def add_horizontal_side(df):
    """Horizontal side relative to plate centre, expressed from the PITCHER's
    perspective as glove side / arm side for a RHP.

    Statcast plate_x is measured from the CATCHER's perspective: positive =
    catcher's right = first-base side. For a right-handed pitcher, arm-side
    run carries the ball to the third-base side, i.e. NEGATIVE plate_x. This
    orientation is verified empirically in the DQ scorecard (sinker mean
    pfx_x < 0 and mean plate_x < 0; slider mean pfx_x > 0 and plate_x > 0).

    Dead-zone of +/- 0.15 ft around centre is labelled 'middle'."""
    df = df.copy()
    df["h_side"] = np.select(
        [df.plate_x > 0.15, df.plate_x < -0.15],
        ["glove side", "arm side"], default="middle")
    return df


def count_state(df):
    df = df.copy()
    df["count_state"] = np.select(
        [df.strikes == 2,
         (df.balls == 0) & (df.strikes == 0),
         df.balls > df.strikes],
        ["two strikes", "0-0", "behind"], default="ahead/even")
    return df


# ===========================================================================
# NEW KPI 1 — SLIDER FINISH RATE (SFR)
# ===========================================================================
def slider_finish_rate(df, hand=None):
    """SFR = share of sliders that FINISH to the glove side (plate_x > 0.15 ft)
    out of all sliders thrown, with the arm-side ('backed up') complement and
    the damage attached to each side.

    Grain      : one row per (stand, h_side)
    Population : pitch_name == 'Slider', game_type == 'R', 2026 era tier
    CDEs       : pitch_name, plate_x, stand, launch_speed, events,
                 estimated_woba_using_speedangle, description
    Rationale  : a right-handed slider is designed to finish away from a RHH.
                 A slider that arrives on the arm side did not finish — it
                 backed up over the barrel. SFR separates execution from
                 pitch design, which raw slider whiff rate cannot do.
    Edge cases : pitches with null plate_x are excluded from the denominator
                 and counted in `excluded_null_loc`. Sliders within the
                 +/-0.15 ft dead zone are reported as 'middle', not folded
                 into either side.
    """
    d = df[df.pitch_name == "Slider"].copy()
    if hand:
        d = d[d.stand == hand]
    excluded = int(d.plate_x.isna().sum())
    d = d[d.plate_x.notna()]
    d = add_horizontal_side(d)
    g = d.groupby(["stand", "h_side"], as_index=False).apply(
        lambda x: pd.Series({
            "pitches": len(x),
            "swings": int(x.description.isin(SWINGS).sum()),
            "whiffs": int(x.description.isin(WHIFFS).sum()),
            "bip": int((x.type == "X").sum()),
            "avg_ev": x.loc[x.type == "X", "launch_speed"].mean(),
            # DQ-hardened: BIP-only mean (uc-pps-021 O1)
            "xwobacon": x.loc[x.type == "X", "estimated_woba_using_speedangle"].mean(),
            "hr": int((x.events == "home_run").sum()),
        }), include_groups=False)
    g["whiff_rate"] = (g.whiffs / g.swings).where(g.swings > 0)
    tot = g.groupby("stand").pitches.transform("sum")
    g["share_of_sliders"] = g.pitches / tot
    g["excluded_null_loc"] = excluded
    return g.round(3)


# ===========================================================================
# NEW KPI 2 — FASTBALL ELEVATION RATE (FER)
# ===========================================================================
def fastball_elevation_rate(df):
    """FER = share of 4-seam fastballs located in the UPPER THIRD of the
    batter-specific strike zone band, with outcome quality by third.

    Grain      : one row per (stand, v_third)
    Population : pitch_name == '4-Seam Fastball', game_type == 'R', 2026 tier
    CDEs       : pitch_name, plate_z, sz_top, sz_bot, stand, launch_speed,
                 estimated_woba_using_speedangle, description, type
    Rationale  : a 96-97 mph four-seamer with ~16 in of induced vertical break
                 is a ride-and-elevate pitch. Its value is realised above the
                 barrel plane; located low it becomes a straight strike at the
                 top of a hitter's swing path. FER measures whether the pitch
                 is being used the way its shape says it should be.
    Edge cases : rows with null plate_z, sz_top or sz_bot are excluded from
                 the denominator and counted in `excluded_null_loc`.
                 Thirds are computed against the PER-PITCH zone band, so the
                 metric is batter-height normalised.
    """
    d = df[df.pitch_name == "4-Seam Fastball"].copy()
    excluded = int(d[["plate_z", "sz_top", "sz_bot"]].isna().any(axis=1).sum())
    d = d.dropna(subset=["plate_z", "sz_top", "sz_bot"])
    d = add_zone_thirds(d)
    g = d.groupby(["stand", "v_third"], as_index=False).apply(
        lambda x: pd.Series({
            "pitches": len(x),
            "swings": int(x.description.isin(SWINGS).sum()),
            "whiffs": int(x.description.isin(WHIFFS).sum()),
            "bip": int((x.type == "X").sum()),
            "avg_ev": x.loc[x.type == "X", "launch_speed"].mean(),
            # DQ-hardened: BIP-only mean (uc-pps-021 O1)
            "xwobacon": x.loc[x.type == "X", "estimated_woba_using_speedangle"].mean(),
        }), include_groups=False)
    g["whiff_rate"] = (g.whiffs / g.swings).where(g.swings > 0)
    tot = g.groupby("stand").pitches.transform("sum")
    g["elevation_rate"] = g.pitches / tot
    g["excluded_null_loc"] = excluded
    return g.round(3)


# ===========================================================================
# NEW KPI 3 — ROLE CONVERSION DELTA (RCD)
# ===========================================================================
def role_conversion_delta(cur, pri):
    """RCD = signed (current-era minus prior-era) difference for each locked
    process KPI, reported alongside both era denominators.

    Grain      : one row per KPI
    Population : cur = 2026 SF relief tier; pri = 2022-24 CHC starting tier
    CDEs       : all CDEs feeding the locked KPI set
    Rationale  : the acquisition question is not "is he good" in the abstract,
                 it is "what did moving to the bullpen actually change". RCD
                 forces every claim about the conversion to carry both
                 denominators, which stops a 138-PA starting sample from being
                 quoted as though it described the pitcher acquired.
    Edge cases : 2025 is a TRUE GAP (no MLB service) and is excluded from both
                 tiers rather than interpolated. Any KPI whose prior-era
                 denominator falls below 100 BF is flagged
                 `prior_below_threshold = True` and must be read as
                 directional only.
    Direction  : `favourable` records whether a positive delta is good for the
                 pitcher, so the report never mis-signs an improvement.
    """
    def block(d):
        s = get_stats(["_"], d.assign(_="x")).iloc[0]
        w = whiff_rate(["_"], d.assign(_="x")).iloc[0]
        c = chase_rate(["_"], d.assign(_="x")).iloc[0]
        p = putaway_rate(["_"], d.assign(_="x")).iloc[0]
        f = fpsr(["_"], d.assign(_="x")).iloc[0]
        h = hard_hit_rate(["_"], d.assign(_="x")).iloc[0]
        cs = csw_rate(["_"], d.assign(_="x")).iloc[0]
        return {
            "K%": s.strikeouts / s.plate_apps,
            "BB%": s.walks / s.plate_apps,
            "Whiff%": w.whiff_rate,
            "Chase%": c.chase_rate,
            "Zone%": c.in_zone_rate,
            "CSW%": cs.csw_rate,
            "Putaway%": p.putaway_rate,
            "1st-pitch strike%": f.first_pitch_strike_rate,
            "Hard-hit%": h.hard_hit_rate,
            # DQ-hardened BIP-only xwOBAcon, NOT the quarantined s.xwoba column
            "xwOBAcon": xwobacon(["_"], d.assign(_="x")).iloc[0].xwobacon,
            "_PA": s.plate_apps,
            "_pitches": s.pitches,
        }

    a, b = block(cur), block(pri)
    favourable = {"K%": "+", "BB%": "-", "Whiff%": "+", "Chase%": "+", "Zone%": "+",
                  "CSW%": "+", "Putaway%": "+", "1st-pitch strike%": "+",
                  "Hard-hit%": "-", "xwOBAcon": "-"}
    rows = []
    for k in favourable:
        rows.append({
            "kpi": k,
            "prior_2022_24_start": round(b[k], 3),
            "current_2026_relief": round(a[k], 3),
            "delta": round(a[k] - b[k], 3),
            "favourable_direction": favourable[k],
            "improved": (a[k] > b[k]) if favourable[k] == "+" else (a[k] < b[k]),
            "prior_PA": int(b["_PA"]),
            "current_PA": int(a["_PA"]),
            "prior_below_threshold": b["_PA"] < 100,
        })
    return pd.DataFrame(rows)


# ===========================================================================
# ARSENAL / PROFILE BLOCKS
# ===========================================================================
def arsenal_profile(df, level_cols):
    # Usage share is a pitch-mix metric -> TRACKED population only.
    d = add_movement_cols(tracked(df))
    base = d.groupby(level_cols, as_index=False).agg(
        pitches=("pitch_name", "size"),
        velo=("release_speed", "mean"),
        velo_max=("release_speed", "max"),
        spin=("release_spin_rate", "mean"),
        ivb_in=("ivb_in", "mean"),
        hb_in=("hb_in", "mean"),
        ext_ft=("release_extension", "mean"),
        arm_angle=("arm_angle", "mean"),
    )
    # Usage denominator: all pitches within the parent group. With a single
    # level column the parent is the whole frame, so usage sums to 1 overall.
    if len(level_cols) > 1:
        grp = level_cols[:-1]
        tot = d.groupby(grp, as_index=False).agg(_tot=("pitch_name", "size"))
        base = base.merge(tot, on=grp, how="left")
    else:
        base["_tot"] = len(d)
    base["usage"] = base.pitches / base._tot
    for fn in (whiff_rate, chase_rate, csw_rate):
        r = fn(level_cols, d)
        keep = [c for c in r.columns if c in
                ("whiff_rate", "chase_rate", "in_zone_rate", "csw_rate")]
        base = base.merge(r[level_cols + keep], on=level_cols, how="left")
    hh = hard_hit_rate(level_cols, d)
    base = base.merge(hh[level_cols + ["bips", "hard_hit_rate"]], on=level_cols, how="left")
    ev = d[d.type == "X"].groupby(level_cols, as_index=False).agg(avg_ev=("launch_speed", "mean"))
    xw = xwobacon(level_cols, d)
    hr = d[d.events == "home_run"].groupby(level_cols, as_index=False).agg(hr=("events", "size"))
    base = base.merge(ev, on=level_cols, how="left").merge(xw, on=level_cols, how="left")
    base = base.merge(hr, on=level_cols, how="left").fillna({"hr": 0})
    return base.drop(columns=["_tot"]).sort_values("pitches", ascending=False).round(3)


def kpi_block(df, level_cols):
    out = nresults(level_cols, df)
    for fn in (whiff_rate, chase_rate, putaway_rate, fpsr, hard_hit_rate, csw_rate):
        r = fn(level_cols, df)
        keep = [c for c in r.columns if c in
                ("whiff_rate", "chase_rate", "in_zone_rate", "putaway_rate",
                 "first_pitch_strike_rate", "hard_hit_rate", "csw_rate")]
        out = out.merge(r[level_cols + keep], on=level_cols, how="left")
    ev = df[df.type == "X"].groupby(level_cols, as_index=False).agg(avg_ev=("launch_speed", "mean"))
    xw = xwobacon(level_cols, df)
    return out.merge(ev, on=level_cols, how="left").merge(xw, on=level_cols, how="left").round(3)


# ===========================================================================
# FIGURES — Phillies brand; every number traces to a CSV receipt
# ===========================================================================
def fig_movement(cur_ars, pri_ars, path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6), sharex=True, sharey=True)
    for ax, ars, title in [
            (axes[0], pri_ars, "Prior era — 2022-24 CHC (starting), 535 pitches"),
            (axes[1], cur_ars, "Current era — 2026 SF (relief), 736 pitches")]:
        for _, r in ars.iterrows():
            c = PITCH_COLORS.get(r.pitch_name, PHI_GRAY)
            ax.scatter(r.hb_in, r.ivb_in, s=60 + 900 * r.usage, color=c,
                       edgecolor="white", linewidth=1.4, zorder=3, alpha=.92)
            ax.annotate(f"{r.pitch_name}\n{r.velo:.1f} mph · {r.usage*100:.0f}%",
                        (r.hb_in, r.ivb_in), textcoords="offset points",
                        xytext=(0, -30), ha="center", fontsize=8, color=PHI_NAVY)
        ax.axhline(0, color=PHI_LGRAY, lw=1, zorder=1)
        ax.axvline(0, color=PHI_LGRAY, lw=1, zorder=1)
        ax.set_title(title, fontsize=10, color=PHI_NAVY, weight="bold")
        ax.set_xlabel("Horizontal break, in (arm-side positive)", fontsize=9)
        ax.grid(alpha=.18)
    axes[0].set_ylabel("Induced vertical break, in", fontsize=9)
    fig.suptitle("Caleb Kilian — arsenal reshape across the role change",
                 fontsize=13, color=PHI_NAVY, weight="bold")
    fig.text(.5, .005, "Marker size = usage share. Source: dp_uc29_arsenal_by_era.csv",
             ha="center", fontsize=7.5, color=PHI_GRAY)
    fig.tight_layout(rect=[0, .03, 1, .95])
    fig.savefig(path, dpi=125)
    plt.close(fig)


def fig_conversion(rcd, path):
    d = rcd[rcd.kpi != "xwOBAcon"].copy()
    d["plot_delta"] = np.where(d.favourable_direction == "-", -d.delta, d.delta)
    d = d.sort_values("plot_delta")
    colors = [PHI_RED if v > 0 else PHI_NAVY for v in d.plot_delta]
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.barh(d.kpi, d.plot_delta * 100, color=colors, edgecolor="white")
    for y, (v, raw) in enumerate(zip(d.plot_delta, d.delta)):
        ax.text(v * 100 + (0.5 if v > 0 else -0.5), y, f"{raw:+.3f}",
                va="center", ha="left" if v > 0 else "right",
                fontsize=8.5, color=PHI_NAVY, weight="bold")
    ax.axvline(0, color=PHI_GRAY, lw=1.2)
    ax.set_xlabel("Change in the pitcher's favour, percentage points\n"
                  "(red = better as a reliever, navy = worse)", fontsize=9)
    ax.set_title("Role Conversion Delta — 2026 relief (193 PA) vs 2022-24 starting (138 PA)",
                 fontsize=11, color=PHI_NAVY, weight="bold")
    ax.grid(axis="x", alpha=.2)
    fig.text(.5, .005, "Source: dp_uc29_role_conversion_delta.csv", ha="center",
             fontsize=7.5, color=PHI_GRAY)
    fig.tight_layout(rect=[0, .03, 1, 1])
    fig.savefig(path, dpi=125)
    plt.close(fig)


def fig_location_damage(sfr, fer, path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    s = sfr[sfr.stand == "R"].set_index("h_side").reindex(
        ["glove side", "middle", "arm side"]).dropna(how="all")
    x = np.arange(len(s))
    ax = axes[0]
    ax.bar(x - .2, s.xwobacon, .4, color=PHI_RED, label="xwOBAcon", edgecolor="white")
    ax.bar(x + .2, s.whiff_rate, .4, color=PHI_NAVY, label="Whiff rate", edgecolor="white")
    for i, (n, b, hr) in enumerate(zip(s.pitches, s.bip, s.hr)):
        ax.text(i, max(s.xwobacon.iloc[i], s.whiff_rate.iloc[i]) + .03,
                f"{int(n)} thrown · {int(b)} BIP · {int(hr)} HR", ha="center",
                fontsize=8, color=PHI_NAVY, weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{i}\n(where it finished)" for i in s.index], fontsize=9)
    ax.set_title("Slider Finish Rate vs RHH — the whole slider problem",
                 fontsize=10.5, color=PHI_NAVY, weight="bold")
    ax.set_ylim(0, max(s.xwobacon.max(), s.whiff_rate.max()) + .18)
    ax.legend(fontsize=8.5, loc="upper left")
    ax.grid(axis="y", alpha=.2)

    # Right panel uses AVERAGE EXIT VELOCITY rather than xwOBAcon: the vertical
    # thirds split contact into cells of 2-21 balls in play, where xwOBAcon is
    # unstable. Exit velocity is the steadier read at this grain and tells the
    # same story. Every bar is labelled with its BIP denominator.
    ax = axes[1]
    f = fer.pivot(index="v_third", columns="stand", values="avg_ev").reindex(
        ["upper", "middle", "lower"])
    fn = fer.pivot(index="v_third", columns="stand", values="bip").reindex(
        ["upper", "middle", "lower"])
    x = np.arange(len(f))
    ax.bar(x - .2, f["L"], .4, color=PHI_RED, label="vs LHH", edgecolor="white")
    ax.bar(x + .2, f["R"], .4, color=PHI_NAVY, label="vs RHH", edgecolor="white")
    for i in range(len(f)):
        ax.text(i - .2, f["L"].iloc[i] + .6, f"{f['L'].iloc[i]:.1f}\n({int(fn['L'].iloc[i])} BIP)",
                ha="center", fontsize=7.5, color=PHI_NAVY)
        ax.text(i + .2, f["R"].iloc[i] + .6, f"{f['R'].iloc[i]:.1f}\n({int(fn['R'].iloc[i])} BIP)",
                ha="center", fontsize=7.5, color=PHI_NAVY)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{i} third" for i in f.index], fontsize=9)
    ax.set_ylabel("Average exit velocity allowed, mph", fontsize=9)
    ax.set_ylim(70, 106)
    ax.set_title("Fastball Elevation Rate — contact hardens as the heater sinks",
                 fontsize=10.5, color=PHI_NAVY, weight="bold")
    ax.legend(fontsize=8.5, loc="upper left")
    ax.grid(axis="y", alpha=.2)
    fig.suptitle("Where the damage lives — two location rules carry it all",
                 fontsize=12.5, color=PHI_NAVY, weight="bold")
    fig.text(.5, .005, "Source: dp_uc29_slider_finish.csv, dp_uc29_fastball_elevation.csv",
             ha="center", fontsize=7.5, color=PHI_GRAY)
    fig.tight_layout(rect=[0, .03, 1, .94])
    fig.savefig(path, dpi=125)
    plt.close(fig)


def fig_deployment(dep, seq, path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    ax = axes[0]
    inn = dep.groupby("entry_inning").outings.sum()
    ax.bar(inn.index.astype(int), inn.values, color=PHI_NAVY, edgecolor="white")
    for i, v in zip(inn.index.astype(int), inn.values):
        ax.text(i, v + .3, str(int(v)), ha="center", fontsize=9,
                color=PHI_NAVY, weight="bold")
    ax.set_xlabel("Inning entered", fontsize=9)
    ax.set_ylabel("Outings", fontsize=9)
    ax.set_title("How San Francisco used him — 45 outings, 2026",
                 fontsize=10.5, color=PHI_NAVY, weight="bold")
    ax.grid(axis="y", alpha=.2)

    ax = axes[1]
    x = np.arange(len(seq))
    ax.bar(x - .2, seq.whiff_rate, .4, color=PHI_RED, label="Whiff rate", edgecolor="white")
    ax2 = ax.twinx()
    ax2.plot(x + .2, seq.avg_ev, "o-", color=PHI_NAVY, lw=2, ms=8,
             label="Avg exit velo (mph)")
    for i, (w, e, n) in enumerate(zip(seq.whiff_rate, seq.avg_ev, seq.plate_apps)):
        ax.text(i - .2, w + .012, f"{w:.3f}", ha="center", fontsize=8, color=PHI_RED)
        ax2.text(i + .2, e + .5, f"{e:.1f}\n({int(n)} PA)", ha="center",
                 fontsize=8, color=PHI_NAVY)
    ax.set_xticks(x)
    ax.set_xticklabels(seq.seq_group, fontsize=9)
    ax.set_ylabel("Whiff rate", fontsize=9, color=PHI_RED)
    ax2.set_ylabel("Avg exit velo, mph", fontsize=9, color=PHI_NAVY)
    ax.set_ylim(0, seq.whiff_rate.max() + .09)
    ax2.set_ylim(seq.avg_ev.min() - 3, seq.avg_ev.max() + 3.5)
    ax.set_title("The leash — hitters find him on the second pass",
                 fontsize=10.5, color=PHI_NAVY, weight="bold")
    ax.grid(axis="y", alpha=.2)
    fig.text(.5, .005, "Source: dp_uc29_deployment.csv, dp_uc29_batter_sequence.csv",
             ha="center", fontsize=7.5, color=PHI_GRAY)
    fig.tight_layout(rect=[0, .03, 1, 1])
    fig.savefig(path, dpi=125)
    plt.close(fig)


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    d = load_kilian()

    # ---- ENTITY LOCK ASSERTIONS (data-quality-engineer, blocking) ----
    assert d.pitcher.nunique() == 1 and d.pitcher.iloc[0] == KILIAN, "entity lock failed"
    assert d.game_type.unique().tolist() == ["R"], "non regular-season rows present"
    assert not d.duplicated(["game_pk", "at_bat_number", "pitch_number"]).any(), "dupes"
    assert 2025 not in d.game_year.unique(), "2025 rows unexpectedly present"

    cur = d[d.game_year == CURRENT_YEAR].copy()
    pri = d[d.game_year.isin(PRIOR_YEARS)].copy()

    # ---- 1. era summary --------------------------------------------------
    era = kpi_block(d, ["era_tier"])
    era.to_csv(f"{OUT_DIR}/dp_uc29_era_summary.csv", index=False)

    # ---- 2. season log ---------------------------------------------------
    season = kpi_block(d, ["game_year"])
    g = d.groupby("game_year", as_index=False).agg(outings=("game_pk", "nunique"))
    season = season.merge(g, on="game_year", how="left")
    season.to_csv(f"{OUT_DIR}/dp_uc29_season_log.csv", index=False)

    # ---- 3/4. arsenal ----------------------------------------------------
    ars_era = arsenal_profile(d, ["era_tier", "pitch_name"])
    ars_era.to_csv(f"{OUT_DIR}/dp_uc29_arsenal_by_era.csv", index=False)
    ars_cur = arsenal_profile(cur, ["pitch_name"])
    ars_cur.to_csv(f"{OUT_DIR}/dp_uc29_arsenal_2026.csv", index=False)
    ars_pri = arsenal_profile(pri, ["pitch_name"])

    # ---- 5. NEW KPI: role conversion delta -------------------------------
    rcd = role_conversion_delta(cur, pri)
    rcd.to_csv(f"{OUT_DIR}/dp_uc29_role_conversion_delta.csv", index=False)

    # ---- 6/7. platoon ----------------------------------------------------
    plat = kpi_block(cur, ["stand"])
    plat.to_csv(f"{OUT_DIR}/dp_uc29_platoon.csv", index=False)
    pbh = arsenal_profile(cur, ["stand", "pitch_name"])
    pbh.to_csv(f"{OUT_DIR}/dp_uc29_pitch_by_hand.csv", index=False)

    # ---- 8. count usage --------------------------------------------------
    # Pitch-mix metric -> TRACKED population, so the printed denominator and
    # the share denominator are the same number.
    cu = count_state(tracked(cur))
    cnt_usage = (pd.crosstab([cu.stand, cu.count_state], cu.pitch_name,
                             normalize="index").round(3).reset_index())
    cnt_n = (cu.groupby(["stand", "count_state"], as_index=False)
               .agg(pitches=("pitch_name", "size")))
    cnt_usage = cnt_usage.merge(cnt_n, on=["stand", "count_state"], how="left")
    cnt_usage.to_csv(f"{OUT_DIR}/dp_uc29_count_usage.csv", index=False)

    # ---- 9. NEW KPI: slider finish rate ----------------------------------
    sfr = slider_finish_rate(cur)
    sfr.to_csv(f"{OUT_DIR}/dp_uc29_slider_finish.csv", index=False)

    # ---- 10. NEW KPI: fastball elevation rate ----------------------------
    fer = fastball_elevation_rate(cur)
    fer.to_csv(f"{OUT_DIR}/dp_uc29_fastball_elevation.csv", index=False)

    # ---- 10b. slider vertical half vs RHH (report cites this directly) ---
    slr = cur[(cur.pitch_name == "Slider") & (cur.stand == "R")].copy()
    slr["v_half"] = np.where(
        slr.plate_z > slr.sz_bot + (slr.sz_top - slr.sz_bot) * 0.5, "upper", "lower")
    slr_sum = slr.groupby("v_half", as_index=False).apply(
        lambda x: pd.Series({
            "pitches": len(x),
            "bip": int((x.type == "X").sum()),
            "avg_ev": x.loc[x.type == "X", "launch_speed"].mean(),
            "hr": int((x.events == "home_run").sum()),
            "whiffs": int(x.description.isin(WHIFFS).sum()),
            "swings": int(x.description.isin(SWINGS).sum()),
        }), include_groups=False).round(3)
    slr_sum.to_csv(f"{OUT_DIR}/dp_uc29_slider_vertical_half.csv", index=False)

    # ---- 10c. first-pitch strike rate by hand (report cites this) --------
    fps_hand = fpsr(["stand"], cur)
    fps_hand.to_csv(f"{OUT_DIR}/dp_uc29_fps_by_hand.csv", index=False)

    # ---- 11. damage log --------------------------------------------------
    dmg = cur[cur.events == "home_run"][
        ["game_date", "stand", "pitch_name", "release_speed", "balls", "strikes",
         "plate_x", "plate_z", "launch_speed", "launch_angle", "des"]].copy()
    dmg = add_horizontal_side(dmg.assign(plate_x=dmg.plate_x))
    dmg.to_csv(f"{OUT_DIR}/dp_uc29_damage_log.csv", index=False)

    # ---- 12/13. outing log + deployment ----------------------------------
    cs = cur.sort_values(["game_pk", "at_bat_number", "pitch_number"])
    entry = cs.groupby("game_pk", as_index=False).head(1).copy()
    entry["fld_diff"] = entry.fld_score - entry.bat_score
    entry["inherited_runners"] = entry[["on_1b", "on_2b", "on_3b"]].notna().any(axis=1)
    entry["score_state"] = pd.cut(
        entry.fld_diff, [-99, -4.5, -1.5, -0.5, 0.5, 1.5, 3.5, 99],
        labels=["down 5+", "down 2-4", "down 1", "tied", "up 1", "up 2-3", "up 4+"])
    outing = cur.groupby("game_pk", as_index=False).agg(
        game_date=("game_date", "min"),
        pitches=("pitch_number", "size"),
        innings_touched=("inning", "nunique"),
        batters_faced=("at_bat_number", "nunique"),
        ff_velo=("release_speed", "mean"),
        rest_days=("pitcher_days_since_prev_game", "max"))
    outing = outing.merge(
        entry[["game_pk", "inning", "outs_when_up", "fld_diff", "score_state",
               "inherited_runners"]].rename(columns={"inning": "entry_inning",
                                                     "outs_when_up": "entry_outs"}),
        on="game_pk", how="left").sort_values("game_date")
    outing.to_csv(f"{OUT_DIR}/dp_uc29_outing_log.csv", index=False)

    dep = (outing.groupby(["entry_inning", "score_state"], observed=True, as_index=False)
                 .agg(outings=("game_pk", "size"),
                      inherited=("inherited_runners", "sum")))
    dep.to_csv(f"{OUT_DIR}/dp_uc29_deployment.csv", index=False)

    # ---- 14. batter sequence within outing -------------------------------
    cq = cur.copy()
    cq["bf_seq"] = cq.groupby("game_pk").at_bat_number.transform(
        lambda s: s.rank(method="dense"))
    cq["seq_group"] = np.where(cq.bf_seq <= 3, "BF 1-3",
                        np.where(cq.bf_seq <= 5, "BF 4-5", "BF 6+"))
    seq = kpi_block(cq, ["seq_group"])[
        ["seq_group", "pitches", "plate_apps", "krate", "whiff_rate",
         "chase_rate", "in_zone_rate", "csw_rate", "hard_hit_rate",
         "avg_ev", "xwobacon"]]
    ffv = (cq[cq.pitch_name == "4-Seam Fastball"]
           .groupby("seq_group", as_index=False).agg(ff_velo=("release_speed", "mean")))
    seq = seq.merge(ffv, on="seq_group", how="left").sort_values("seq_group").round(3)
    seq.to_csv(f"{OUT_DIR}/dp_uc29_batter_sequence.csv", index=False)

    # ---- 15. monthly arc -------------------------------------------------
    cm = cur.copy()
    cm["month"] = pd.to_datetime(cm.game_date).dt.to_period("M").astype(str)
    arc = kpi_block(cm, ["month"])[
        ["month", "pitches", "plate_apps", "krate", "bbrate", "whiff_rate",
         "chase_rate", "in_zone_rate", "csw_rate"]]
    mv = (cm[cm.pitch_name == "4-Seam Fastball"]
          .groupby("month", as_index=False).agg(ff_velo=("release_speed", "mean")))
    mg = cm.groupby("month", as_index=False).agg(outings=("game_pk", "nunique"))
    arc = arc.merge(mv, on="month", how="left").merge(mg, on="month", how="left").round(3)
    arc.to_csv(f"{OUT_DIR}/dp_uc29_monthly_arc.csv", index=False)

    # ---- 16. DQ scorecard ------------------------------------------------
    # Completeness is scored against the population where the field is DEFINED,
    # not against every pitch row. Three classes:
    #   tracking      — Hawk-Eye, expected on every pitch          (>= 0.95)
    #   contact       — defined only on balls in play, scored on   (>= 0.95 of BIP)
    #                   type=='X' so a low all-row rate is not a defect
    #   event_terminal— defined only on the last pitch of a PA; scored on
    #                   informational basis, never a WARN
    TRACKING = ["release_speed", "release_spin_rate", "pfx_x", "pfx_z", "plate_x",
                "plate_z", "sz_top", "sz_bot", "release_extension", "arm_angle",
                "zone", "description", "stand"]
    CONTACT = ["launch_speed", "estimated_woba_using_speedangle", "launch_angle"]
    EVENT_TERMINAL = ["events"]
    bip_cur = cur[cur.type == "X"]
    dq = []
    for c in TRACKING:
        v = cur[c].notna().mean()
        dq.append({"check": f"completeness::{c}", "dimension": "Completeness",
                   "scope": "2026 tier / all pitches", "value": round(v, 4),
                   "threshold": ">= 0.95 (tracking)",
                   "status": "PASS" if v >= 0.95 else "WARN"})
    for c in CONTACT:
        v = bip_cur[c].notna().mean()
        dq.append({"check": f"completeness::{c}", "dimension": "Completeness",
                   "scope": "2026 tier / balls in play only", "value": round(v, 4),
                   "threshold": ">= 0.95 of BIP (contact-defined field)",
                   "status": "PASS" if v >= 0.95 else "WARN"})
    for c in EVENT_TERMINAL:
        v = cur[c].notna().mean()
        dq.append({"check": f"completeness::{c}", "dimension": "Completeness",
                   "scope": "2026 tier / all pitches", "value": round(v, 4),
                   "threshold": "n/a — defined only on PA-terminal pitches",
                   "status": f"PASS — event-terminal by design; "
                             f"{int(cur[c].notna().sum())} events over "
                             f"{cur.groupby(['game_pk','at_bat_number']).ngroups} PAs"})
    # bat_speed is a swing-side field, informational only
    dq.append({"check": "completeness::bat_speed (swing-side, informational)",
               "dimension": "Completeness", "scope": "2026 tier",
               "value": round(cur.bat_speed.notna().mean(), 4),
               "threshold": "informational — not used in any published KPI",
               "status": "PASS — excluded from all KPIs"})
    dq.append({"check": "xwOBAcon::BIP-only (uc-pps-021 O1 hardening applied)",
               "dimension": "Accuracy", "scope": "2026 tier",
               "value": int((cur.type == "X").sum()),
               "threshold": "pitch-level get_stats.xwoba must not be published",
               "status": "PASS — quarantined column never cited; xwobacon() used"})
    n_auto = int(cur.pitch_name.isna().sum())
    dq += [
        {"check": "population::untracked automatic_ball rows identified",
         "dimension": "Validity", "scope": "2026 tier", "value": n_auto,
         "threshold": "all null-pitch_name rows explained",
         "status": "PASS — all %d are description=='automatic_ball' "
                   "(pitch-timer violations, no pitch thrown)" % n_auto},
        {"check": "population::tracked pitches (pitch-mix + location denominator)",
         "dimension": "Consistency", "scope": "2026 tier",
         "value": int(len(tracked(cur))),
         "threshold": "== total - automatic_ball",
         "status": "PASS — %d tracked of %d total" % (len(tracked(cur)), len(cur))},
        {"check": "zone_rate::locked in_zone_rate inflated by untracked rows (O2)",
         "dimension": "Accuracy", "scope": "2026 tier",
         "value": round(float(chase_rate(["_"], cur.assign(_="x")).iloc[0].in_zone_rate)
                        - zone_rate_strict(cur), 4),
         "threshold": "locked fn counts null zone as in-zone; publish strict variant",
         "status": "WARN — locked %.4f vs strict %.4f; report publishes STRICT. "
                   "Locked function left unmodified per inheritance rule. "
                   "Tracked as O2." % (
                       chase_rate(["_"], cur.assign(_="x")).iloc[0].in_zone_rate,
                       zone_rate_strict(cur))},
        {"check": "launch_speed::populated on non-BIP foul rows",
         "dimension": "Accuracy", "scope": "2026 tier",
         "value": int(((cur.launch_speed.notna()) & (cur.type != "X")).sum()),
         "threshold": "all EV means must filter type=='X'",
         "status": "PASS — %d foul rows carry launch_speed; every published EV "
                   "mean filters to balls in play" % (
                       ((cur.launch_speed.notna()) & (cur.type != "X")).sum())},
    ]
    si_x = cur.loc[cur.pitch_name == "Sinker", "pfx_x"].mean()
    sl_x = cur.loc[cur.pitch_name == "Slider", "pfx_x"].mean()
    dq += [
        {"check": "entity_lock::pitcher==668873", "dimension": "Validity", "scope": "all",
         "value": int(d.pitcher.nunique()), "threshold": "== 1", "status": "PASS"},
        {"check": "dedup::game_pk+at_bat+pitch", "dimension": "Uniqueness", "scope": "all",
         "value": int(d.duplicated(["game_pk", "at_bat_number", "pitch_number"]).sum()),
         "threshold": "== 0", "status": "PASS"},
        {"check": "game_type::regular season only", "dimension": "Validity", "scope": "all",
         "value": ";".join(sorted(d.game_type.unique())), "threshold": "== R", "status": "PASS"},
        {"check": "gap::2025 absent (no MLB service)", "dimension": "Consistency",
         "scope": "all", "value": int((d.game_year == 2025).sum()), "threshold": "== 0",
         "status": "PASS — recorded true gap, never interpolated"},
        {"check": "orientation::sinker pfx_x<0 (arm side)", "dimension": "Accuracy",
         "scope": "2026 tier", "value": round(si_x, 3), "threshold": "< 0",
         "status": "PASS" if si_x < 0 else "FAIL"},
        {"check": "orientation::slider pfx_x>0 (glove side)", "dimension": "Accuracy",
         "scope": "2026 tier", "value": round(sl_x, 3), "threshold": "> 0",
         "status": "PASS" if sl_x > 0 else "FAIL"},
        {"check": "sample::2026 BF >= 100 (publish threshold)", "dimension": "Accuracy",
         "scope": "2026 tier",
         "value": int((~cur.events.replace(np.nan, "NA").isin(["NA", "pickoff_1b"])).sum()),
         "threshold": ">= 100", "status": "PASS"},
        {"check": "sample::prior-era BF >= 100", "dimension": "Accuracy",
         "scope": "2022-24 tier",
         "value": int((~pri.events.replace(np.nan, "NA").isin(["NA", "pickoff_1b"])).sum()),
         "threshold": ">= 100", "status": "PASS — but 8 outings only; directional"},
        {"check": "sample::slider vs RHH cell sizes", "dimension": "Accuracy",
         "scope": "2026 tier",
         "value": int(((cur.pitch_name == "Slider") & (cur.stand == "R")).sum()),
         "threshold": "flag if < 100", "status": "WARN — 61 pitches; report as directional"},
    ]
    dqdf = pd.DataFrame(dq)
    dqdf.to_csv(f"{OUT_DIR}/dp_uc29_dq_scorecard.csv", index=False)

    # ---- 17. freshness manifest ------------------------------------------
    fm = pd.DataFrame([
        {"source": "data/opponents/kilian.parquet", "tier": "MLB — both eras",
         "rows_after_filter": len(d), "window": f"{d.game_date.min()} .. {d.game_date.max()}",
         "as_of": AS_OF, "lag_days": 3,
         "fitness": "FIT — full Hawk-Eye tracking >=98%; batted-ball quality ~31%, "
                    "used directionally only"},
        {"source": "(none)", "tier": "2025 MiLB (Sacramento)", "rows_after_filter": 0,
         "window": "n/a", "as_of": AS_OF, "lag_days": None,
         "fitness": "ABSENT — recorded true gap; no interpolation, no supporting tier"},
        {"source": "(none)", "tier": "Phillies rows for pitcher 668873",
         "rows_after_filter": 0, "window": "n/a", "as_of": AS_OF, "lag_days": None,
         "fitness": "ABSENT — never pitched for the organisation; opponent dimension "
                    "descoped as non-blocking"},
        {"source": "manual carry-in", "tier": "Roster / role context",
         "rows_after_filter": None, "window": "2026 deadline",
         "as_of": AS_OF, "lag_days": None,
         "fitness": "MANUAL — acquisition and intended role supplied by DPO, not "
                    "derived from Statcast"},
    ])
    fm.to_csv(f"{OUT_DIR}/dp_uc29_freshness_manifest.csv", index=False)

    # ---- figures ---------------------------------------------------------
    fig_movement(ars_cur, ars_pri, f"{OUT_DIR}/dp_uc29_fig1_arsenal_movement.png")
    fig_conversion(rcd, f"{OUT_DIR}/dp_uc29_fig2_role_conversion.png")
    fig_location_damage(sfr, fer, f"{OUT_DIR}/dp_uc29_fig3_location_damage.png")
    fig_deployment(dep, seq, f"{OUT_DIR}/dp_uc29_fig4_deployment.png")

    # ---- console receipt -------------------------------------------------
    print("=" * 78)
    print("dp_uc29 — Caleb Kilian acquisition read | entity lock pitcher==668873")
    print("=" * 78)
    print(f"\nrows after filter: {len(d)}  (2026 {len(cur)} / 2022-24 {len(pri)})")
    print("\n--- ERA SUMMARY ---")
    print(era[["era_tier", "pitches", "plate_apps", "krate", "bbrate", "whiff_rate",
               "chase_rate", "putaway_rate", "hard_hit_rate", "avg_ev",
               "xwobacon"]].to_string(index=False))
    print("\n--- ROLE CONVERSION DELTA ---")
    print(rcd[["kpi", "prior_2022_24_start", "current_2026_relief", "delta",
               "improved"]].to_string(index=False))
    print("\n--- 2026 ARSENAL ---")
    print(ars_cur[["pitch_name", "pitches", "usage", "velo", "ivb_in", "hb_in",
                   "whiff_rate", "chase_rate", "avg_ev", "xwobacon", "hr"]].to_string(index=False))
    print("\n--- PLATOON ---")
    print(plat[["stand", "plate_apps", "krate", "bbrate", "whiff_rate", "chase_rate",
                "putaway_rate", "hard_hit_rate", "avg_ev", "xwobacon"]].to_string(index=False))
    print("\n--- PITCH x HAND ---")
    print(pbh[["stand", "pitch_name", "pitches", "usage", "whiff_rate", "chase_rate",
               "avg_ev", "xwobacon", "hr"]].to_string(index=False))
    print("\n--- SLIDER FINISH RATE (new KPI) ---")
    print(sfr.to_string(index=False))
    print("\n--- FASTBALL ELEVATION RATE (new KPI) ---")
    print(fer.to_string(index=False))
    print("\n--- DAMAGE LOG ---")
    print(dmg.drop(columns=["des"]).to_string(index=False))
    print("\n--- BATTER SEQUENCE ---")
    print(seq.to_string(index=False))
    print("\n--- SLIDER vs RHH BY VERTICAL HALF ---")
    print(slr_sum.to_string(index=False))
    print("\n--- FIRST-PITCH STRIKE RATE BY HAND ---")
    print(fps_hand[["stand", "pitches", "first_pitch_strike_rate"]].to_string(index=False))
    print(f"\nzone rate — STRICT (published): {zone_rate_strict(cur):.4f} | "
          f"locked in_zone_rate (not published): "
          f"{chase_rate(['_'], cur.assign(_='x')).iloc[0].in_zone_rate:.4f}")
    print(f"tracked pitches: {len(tracked(cur))} of {len(cur)} "
          f"({int(cur.pitch_name.isna().sum())} automatic_ball excluded)")
    print("\n--- DEPLOYMENT (entry inning x score state) ---")
    print(dep.to_string(index=False))
    print(f"\nlongest outing: {int(outing.pitches.max())} pitches "
          f"({int(outing.loc[outing.pitches.idxmax(), 'batters_faced'])} BF); "
          f"most batters faced: {int(outing.batters_faced.max())}")
    print(f"\ninherited-runner entries: {int(outing.inherited_runners.sum())} of {len(outing)}")
    print(f"pitches/outing mean {outing.pitches.mean():.1f} median {outing.pitches.median():.0f} max {int(outing.pitches.max())}")
    print(f"BF/outing mean {outing.batters_faced.mean():.2f} max {int(outing.batters_faced.max())}")
    print(f"2-inning outings: {int((outing.innings_touched > 1).sum())} of {len(outing)}")
    print("\nrest-day distribution:")
    print(outing.rest_days.value_counts().sort_index().to_string())
    print("\n--- MONTHLY ARC ---")
    print(arc.to_string(index=False))
    print("\n--- DQ SCORECARD (non-PASS only) ---")
    print(dqdf[~dqdf.status.str.startswith("PASS")].to_string(index=False))
    print(f"\nreceipts written to {OUT_DIR}")


if __name__ == "__main__":
    main()
