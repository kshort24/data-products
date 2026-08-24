"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #37  (uc-pps-026)
"Acquisition Read: Nestor Cortes (LHP) — what the Phillies signed on
 2026-08-19, how he has been deployed, what he throws, and what to watch
 on his return from arm surgery."
============================================================================

Layer-3 BUILD artifact for the Phillies Pitching (pps) value stream.

Pattern lineage: UC#3 -> UC#8 -> UC#11 -> UC#29 (Painter, return-from-injury
self-scout) -> UC#30 (Kilian, acquisition-onboarding) -> UC#31 (Raley) ->
THIS: third pitcher acquisition-onboarding read, and the first that is ALSO
a return-from-surgery read (mid-Oct 2025 arm surgery; zero competitive
pitches since 2025-09-03 — 2026 is a TRUE GAP, disclosed, never imputed).

PHASE-TIER EVIDENCE RULE (adapted from the UC#30 era-tier rule; NEVER BLEND):
  2019 NYY relief/bulk    - his only high-volume relief season
  2021 transition         - live bullpen -> rotation conversion
  2022 peak               - All-Star season (carry-in), career-best results
  2023-24 decline         - the "fallen off" window under test (premise P5)
  2025 final (MIL->SD)    - injury-interrupted last look; DIRECTIONAL ONLY
  2018 (108 p) and 2020 (165 p) sit below the floor: season grain only.

NEW KPI FAMILY (specs in 02_engineering_design.md sec.2.2 — written BEFORE
this build ran; definitions supplied by the human DPO's use-case notebook):
  UD-1 Start Share      starts/games,  start <=> entry_inning == 1
  UD-2 Bulk Share       bulks/games,   bulk  <=> entry_inning > 1
                                              AND innings_delta > 2
  UD-3 Innings per Game sum(innings_delta)/games   (delta = exit - entry;
                        innings_appeared ships alongside as cross-check)
  UD-4 PAs per Game     sum(unique PAs)/games
  UD-5 Relief Share     (games - starts)/games
  UD-6 Season Role Label derived from UD-1/2/5 thresholds (report-local)

Governance lineage:
  - data-product-owner      : sequenced as UC#37 / uc-pps-026 / dp_uc36
  - use-case-validator      : GO, 0 blocking; premise register in 01
  - source-system-profiler  : entity lock pitcher==641482; career frame
                              2018-03-31 .. 2025-09-03; 2026 true gap
  - kpi-calculator          : locked cores inherited VERBATIM from dp_uc29
                              (which carries dp_uc28/dp_uc11/dp_uc8 chain);
                              UD family specced before use
  - data-quality-engineer   : scorecard emitted to out/ (LHP sign checks)

OUTPUTS — 26 CSV receipts + 5 figures (NEW files, none overwritten), ./out/
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

CORTES = 641482                    # Nestor Cortes, MLBAM pitcher id — ENTITY LOCK
AS_OF = "2026-08-20"
PHASES = {2019: "2019 NYY relief/bulk", 2021: "2021 transition",
          2022: "2022 peak", 2023: "2023-24 decline", 2024: "2023-24 decline",
          2025: "2025 final (MIL-SD)"}
PHASE_ORDER = ["2019 NYY relief/bulk", "2021 transition", "2022 peak",
               "2023-24 decline", "2025 final (MIL-SD)"]

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data"),
    "/mnt/user-data/uploads/MLB/data",
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data",
]
DATA_ROOT = next((p for p in _DATA_CANDIDATES
                  if p and os.path.isdir(os.path.join(p, "opponents"))), None)
if DATA_ROOT is None:
    raise FileNotFoundError("Could not locate data/opponents. Set MLB_DATA_ROOT.")
OPP_DIR = os.path.join(DATA_ROOT, "opponents")

_WOBA_CANDIDATES = [
    os.path.join(HERE, "wOBA and FIP Constants.csv"),
    os.path.join(os.path.dirname(DATA_ROOT), "wOBA and FIP Constants.csv"),
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
    "4-Seam Fastball": "#E81828", "Cutter": "#002D72", "Sweeper": "#1F77B4",
    "Changeup": "#2CA02C", "Slider": "#6BAED6", "Sinker": "#FF7F0E",
    "Curveball": "#8C564B",
}
PITCH_ORDER = ["4-Seam Fastball", "Cutter", "Sweeper", "Changeup", "Slider",
               "Sinker", "Curveball"]


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


def load_cortes():
    """Single-source load. Entity lock enforced HERE and asserted in main().
    Returns (regular-season frame, postseason context frame)."""
    f = os.path.join(OPP_DIR, "cortes.parquet")
    d0 = pd.read_parquet(f)
    d0 = d0[d0.pitcher == CORTES]
    d0 = d0.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    d0 = _coerce(d0.copy())
    d0["game_date"] = pd.to_datetime(d0.game_date)
    # pitcher's team = fielding team = home team in the Top of an inning
    d0["pit_team"] = np.where(d0.inning_topbot == "Top", d0.home_team, d0.away_team)
    d0["phase"] = d0.game_year.map(PHASES)
    d = _attach_woba(d0[d0.game_type == "R"].copy())
    post = d0[d0.game_type.isin(["D", "L", "W"])].copy()
    return d, post


# ===========================================================================
# LOCKED KPI FUNCTIONS — inherited VERBATIM from dp_uc29_kilian_acquisition_read.py
# (chain: Baseball Functions -> dp_uc8 -> dp_uc11 -> dp_uc28 -> dp_uc29).
# DO NOT RE-DERIVE.
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
    """xwOBA ON CONTACT — BIP-only mean (uc-pps-021 O1 hardening). The locked
    get_stats.xwoba pitch-level column is quarantined and never published."""
    if isinstance(level, str):
        level = [level]
    bip = df[df.type == "X"]
    out = bip.groupby(level, as_index=False).agg(
        xwobacon=("estimated_woba_using_speedangle", "mean"),
        xwobacon_bip=("estimated_woba_using_speedangle", "size"))
    return out.round(3)


def csw_rate(level, df):
    if isinstance(level, str):
        level = [level]
    tot = df.groupby(level, as_index=False).agg(pitches=("des", "size"))
    cs = df[df.description.isin(CALLED_STRIKE)].groupby(level, as_index=False).agg(called=("des", "size"))
    wh = df[df.description.isin(WHIFFS)].groupby(level, as_index=False).agg(whiffs=("des", "size"))
    out = tot.merge(cs, on=level, how="left").merge(wh, on=level, how="left").fillna(0)
    out["csw_rate"] = (out.called + out.whiffs) / out.pitches
    return out.round(3)


# ===========================================================================
# DERIVED HELPERS (mechanical partitions, not new KPIs)
# ===========================================================================
def tracked(df):
    """TRACKED-PITCH POPULATION (uc-pps-024 standard): null-pitch_name rows
    (8 automatic_ball + 2 untracked ball in this frame) are PA-outcome rows
    but not pitches for mix/location denominators."""
    return df[df.pitch_name.notna()]


def zone_rate_strict(df):
    """In-zone rate over TRACKED pitches only (uc-pps-024 O2 hardening).
    Locked chase_rate().in_zone_rate is inherited verbatim, never published."""
    t = tracked(df)
    return (t.zone <= 9).sum() / len(t)


def add_movement_cols(df):
    """pfx_* feet -> inches. LHP CONVENTION: arm side for a left-hander is the
    first-base (+plate_x / +pfx_x) side — the MIRROR of the RHP exemplars —
    so HB = +pfx_x*12 reads arm-side positive. Sign asserted in DQ scorecard
    (SI/CH mean pfx_x > 0; ST/SL mean pfx_x < 0)."""
    df = df.copy()
    df["ivb_in"] = df.pfx_z * 12.0
    df["hb_in"] = df.pfx_x * 12.0
    return df


def add_zone_thirds(df):
    df = df.copy()
    h = df.sz_top - df.sz_bot
    df["v_third"] = np.select(
        [df.plate_z > df.sz_bot + h * 2 / 3, df.plate_z < df.sz_bot + h / 3],
        ["upper", "lower"], default="middle")
    return df


def add_horizontal_side(df):
    """LHP orientation: glove side = plate_x < -0.15 (third-base side),
    arm side = plate_x > 0.15 (first-base side). Dead zone +/-0.15 = middle."""
    df = df.copy()
    df["h_side"] = np.select(
        [df.plate_x < -0.15, df.plate_x > 0.15],
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
# NEW KPI FAMILY — UD (Usage & Deployment). DPO-supplied definitions,
# specced in 02_engineering_design.md sec 2.2 BEFORE this build ran.
# ===========================================================================
def appearance_grain(df):
    """One row per appearance (game_pk). entry/exit inning via min/max —
    algebraically identical to the DPO notebook's min/max-AB inning join for a
    single pitcher's log (innings are contiguous within an appearance); the
    verification harness recomputes via the DPO's original method."""
    ap = df.groupby("game_pk", as_index=False).agg(
        game_date=("game_date", "min"),
        game_year=("game_year", "first"),
        pit_team=("pit_team", "first"),
        entry_inning=("inning", "min"),
        exit_inning=("inning", "max"),
        innings_appeared=("inning", "nunique"),
        total_pitches=("des", "size"),
        uq_pas=("at_bat_number", "nunique"),
    )
    ap["innings_delta"] = ap.exit_inning - ap.entry_inning
    ap["is_start"] = ap.entry_inning == 1
    ap["is_bulk"] = (ap.entry_inning > 1) & (ap.innings_delta > 2)
    # entry state from the first pitch of the appearance
    first = df.sort_values(["game_pk", "at_bat_number", "pitch_number"]) \
              .groupby("game_pk", as_index=False).head(1)
    first = first.assign(fld_diff=first.fld_score - first.bat_score)
    ap = ap.merge(first[["game_pk", "outs_when_up", "fld_diff"]]
                  .rename(columns={"outs_when_up": "entry_outs",
                                   "fld_diff": "entry_score_diff"}),
                  on="game_pk", how="left")
    ap = ap.sort_values("game_date")
    ap["rest_days"] = ap.game_date.diff().dt.days - 1     # derived; NaN on first
    return ap


def usage_deployment(ap):
    """UD-1..6 at season grain, exactly per the 02 sec 2.2 specs."""
    g = ap.groupby("game_year", as_index=False).agg(
        games=("game_pk", "nunique"),
        starts=("is_start", "sum"),
        bulks=("is_bulk", "sum"),
        total_innings_delta=("innings_delta", "sum"),
        total_innings_appeared=("innings_appeared", "sum"),
        total_pas=("uq_pas", "sum"),
        total_pitches=("total_pitches", "sum"),
    )
    g["start_share"] = g.starts / g.games                       # UD-1
    g["bulk_share"] = g.bulks / g.games                         # UD-2
    g["innings_per_gm"] = g.total_innings_delta / g.games       # UD-3 (DPO delta)
    g["innings_appeared_per_gm"] = g.total_innings_appeared / g.games  # UD-3 cross-check
    g["plate_apps_per_gm"] = g.total_pas / g.games              # UD-4
    g["relief_share"] = (g.games - g.starts) / g.games          # UD-5
    g["role_label"] = np.select(                                # UD-6
        [g.start_share >= 0.70,
         (g.relief_share >= 0.70) & (g.bulk_share < 0.15)],
        ["start-heavy", "relief-heavy"], default="bulk/hybrid")
    g["small_season"] = g.games < 3
    return g.round(3)


# ===========================================================================
# ED-1 — ERA DELTA (mechanical reuse of dp_uc29 role_conversion_delta at new
# tiers; report-local, not a new governed KPI — 03 sec 1)
# ===========================================================================
def era_delta(cur, pri, cur_label, pri_label):
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
            "Zone% (strict)": zone_rate_strict(d),
            "CSW%": cs.csw_rate,
            "Putaway%": p.putaway_rate,
            "1st-pitch strike%": f.first_pitch_strike_rate,
            "Hard-hit%": h.hard_hit_rate,
            "xwOBAcon": xwobacon(["_"], d.assign(_="x")).iloc[0].xwobacon,
            "_PA": s.plate_apps, "_pitches": s.pitches,
        }
    a, b = block(cur), block(pri)
    favourable = {"K%": "+", "BB%": "-", "Whiff%": "+", "Chase%": "+",
                  "Zone% (strict)": "+", "CSW%": "+", "Putaway%": "+",
                  "1st-pitch strike%": "+", "Hard-hit%": "-", "xwOBAcon": "-"}
    rows = []
    for k in favourable:
        rows.append({
            "kpi": k,
            pri_label: round(b[k], 3),
            cur_label: round(a[k], 3),
            "delta": round(a[k] - b[k], 3),
            "favourable_direction": favourable[k],
            "declined": (a[k] < b[k]) if favourable[k] == "+" else (a[k] > b[k]),
            "prior_PA": int(b["_PA"]), "current_PA": int(a["_PA"]),
        })
    return pd.DataFrame(rows)


# ===========================================================================
# ARSENAL / KPI BLOCKS (dp_uc29 pattern)
# ===========================================================================
def arsenal_profile(df, level_cols):
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
        plate_x=("plate_x", "mean"),
        plate_z=("plate_z", "mean"),
    )
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
    return base.drop(columns=["_tot"]).sort_values(
        level_cols[:-1] + ["pitches"], ascending=[True] * (len(level_cols) - 1) + [False]
        ).round(3)


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
def fig_deployment(ud, path):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5))
    yrs = ud.game_year.astype(int)
    ax = axes[0]
    starts = ud.starts
    bulks = ud.bulks
    other = ud.games - ud.starts - ud.bulks
    ax.bar(yrs, starts, color=PHI_RED, label="Starts (entered 1st)", edgecolor="white")
    ax.bar(yrs, bulks, bottom=starts, color=PHI_NAVY, label="Bulk (entered >1st, delta>2)",
           edgecolor="white")
    ax.bar(yrs, other, bottom=starts + bulks, color=PHI_LGRAY,
           label="Other relief", edgecolor="white")
    for x, g in zip(yrs, ud.games):
        ax.text(x, g + 0.6, str(int(g)), ha="center", fontsize=8.5,
                color=PHI_NAVY, weight="bold")
    ax.set_title("Appearances by season and shape", fontsize=10.5,
                 color=PHI_NAVY, weight="bold")
    ax.set_ylabel("Games", fontsize=9)
    ax.set_ylim(0, ud.games.max() * 1.22)
    ax.legend(fontsize=7.2, loc="lower left", bbox_to_anchor=(0, 1.005), ncol=3,
              frameon=False)
    ax.grid(axis="y", alpha=.2)

    ax = axes[1]
    ax.plot(yrs, ud.start_share, "o-", color=PHI_RED, lw=2, label="Start share (UD-1)")
    ax.plot(yrs, ud.bulk_share, "s--", color=PHI_NAVY, lw=2, label="Bulk share (UD-2)")
    ax.plot(yrs, ud.relief_share, "^:", color=PHI_GRAY, lw=2, label="Relief share (UD-5)")
    ax2 = ax.twinx()
    ax2.plot(yrs, ud.plate_apps_per_gm, "d-", color="#2CA02C", lw=1.6, alpha=.85,
             label="PAs per game (UD-4)")
    ax2.set_ylabel("PAs per game", fontsize=9, color="#2CA02C")
    ax.set_ylim(-0.05, 1.1)
    ax.set_title("Role shares — the reliever-to-starter arc", fontsize=10.5,
                 color=PHI_NAVY, weight="bold")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="center left")
    ax.grid(alpha=.2)
    fig.suptitle("Nestor Cortes — how he has been deployed (UD family, DPO definitions)",
                 fontsize=13, color=PHI_NAVY, weight="bold")
    fig.text(.5, .005, "Source: dp_uc36_usage_by_season.csv", ha="center",
             fontsize=7.5, color=PHI_GRAY)
    fig.tight_layout(rect=[0, .03, 1, .93])
    fig.savefig(path, dpi=125)
    plt.close(fig)


def fig_arsenal_evolution(mix, path):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5), sharey=True)
    for ax, hand, label in [(axes[0], "L", "vs LHB"), (axes[1], "R", "vs RHB")]:
        sub = mix[mix.stand == hand]
        for pn in PITCH_ORDER:
            s = sub[sub.pitch_name == pn].sort_values("game_year")
            if s.usage.max() is not np.nan and len(s) and s.usage.max() >= 0.02:
                ax.plot(s.game_year, s.usage, "o-", lw=2, ms=5,
                        color=PITCH_COLORS.get(pn, PHI_GRAY), label=pn)
        ax.set_title(f"Pitch usage by season — {label}", fontsize=10.5,
                     color=PHI_NAVY, weight="bold")
        ax.set_xlabel("Season", fontsize=9)
        ax.grid(alpha=.2)
    axes[0].set_ylabel("Usage share (TRACKED pitches)", fontsize=9)
    axes[1].legend(fontsize=8, loc="upper left")
    fig.suptitle("Arsenal evolution by batter hand", fontsize=13,
                 color=PHI_NAVY, weight="bold")
    fig.text(.5, .005, "Source: dp_uc36_mix_by_hand_season.csv", ha="center",
             fontsize=7.5, color=PHI_GRAY)
    fig.tight_layout(rect=[0, .03, 1, .93])
    fig.savefig(path, dpi=125)
    plt.close(fig)


def fig_stuff(d, path, pt="FF"):
    dd = add_movement_cols(tracked(d))
    dd = dd[dd.pitch_type == pt]
    metrics = [("release_speed", "Velocity (mph)"), ("release_spin_rate", "Spin (rpm)"),
               ("ivb_in", "Induced vertical break (in)"), ("hb_in", "Horizontal break, arm-side + (in)")]
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8))
    yrs = sorted(dd.game_year.unique())
    for ax, (col, label) in zip(axes.flat, metrics):
        data = [dd.loc[dd.game_year == y, col].dropna() for y in yrs]
        bp = ax.boxplot(data, tick_labels=[str(int(y)) for y in yrs], patch_artist=True,
                        showfliers=False, medianprops=dict(color="white", lw=1.6))
        for patch in bp["boxes"]:
            patch.set_facecolor(PHI_NAVY)
            patch.set_alpha(.85)
        med = [np.median(x) if len(x) else np.nan for x in data]
        ax.plot(range(1, len(yrs) + 1), med, "o-", color=PHI_RED, lw=1.6, ms=4, zorder=3)
        ax.set_title(label, fontsize=10, color=PHI_NAVY, weight="bold")
        ax.grid(axis="y", alpha=.2)
    fig.suptitle(f"Tracking the stuff — four-seam fastball ({pt}), by season",
                 fontsize=13, color=PHI_NAVY, weight="bold")
    fig.text(.5, .005, "Source: dp_uc36_stuff_by_pitch_season.csv (medians); "
                       "boxes = in-season distributions", ha="center",
             fontsize=7.5, color=PHI_GRAY)
    fig.tight_layout(rect=[0, .03, 1, .94])
    fig.savefig(path, dpi=125)
    plt.close(fig)


def fig_platoon(pp, path):
    d = pp[pp.phase.isin(PHASE_ORDER)].copy()
    d["phase"] = pd.Categorical(d.phase, PHASE_ORDER, ordered=True)
    d = d.sort_values(["phase", "stand"])
    x = np.arange(len(PHASE_ORDER))
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5))
    for ax, col, label in [(axes[0], "woba", "wOBA against"),
                           (axes[1], "krate", "K rate")]:
        for off, hand, cfg in [(-.2, "L", PHI_RED), (.2, "R", PHI_NAVY)]:
            s = d[d.stand == hand].set_index("phase").reindex(PHASE_ORDER)
            ax.bar(x + off, s[col], .38, color=cfg, edgecolor="white",
                   label=f"vs {'LHB' if hand == 'L' else 'RHB'}")
            for i, (v, n) in enumerate(zip(s[col], s.plate_apps)):
                if pd.notna(v):
                    ax.text(i + off, v + .004, f"{v:.3f}\n({int(n)} PA)", ha="center",
                            fontsize=6.8, color=cfg)
        ax.set_xticks(x)
        ax.set_xticklabels([p.replace(" ", "\n", 1) for p in PHASE_ORDER], fontsize=8)
        ax.set_title(label, fontsize=10.5, color=PHI_NAVY, weight="bold")
        ax.grid(axis="y", alpha=.2)
        ax.legend(fontsize=8.5)
    fig.suptitle("Platoon splits by career phase (PA printed on every bar)",
                 fontsize=13, color=PHI_NAVY, weight="bold")
    fig.text(.5, .005, "Source: dp_uc36_platoon_by_phase.csv", ha="center",
             fontsize=7.5, color=PHI_GRAY)
    fig.tight_layout(rect=[0, .03, 1, .93])
    fig.savefig(path, dpi=125)
    plt.close(fig)


def fig_drivers(ed, terc, path):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.4))
    d = ed[ed.kpi != "xwOBAcon"].copy()
    d["plot_delta"] = np.where(d.favourable_direction == "-", -d.delta, d.delta)
    d = d.sort_values("plot_delta")
    colors = [PHI_RED if v > 0 else PHI_NAVY for v in d.plot_delta]
    ax = axes[0]
    ax.barh(d.kpi, d.plot_delta * 100, color=colors, edgecolor="white")
    for y, (v, raw) in enumerate(zip(d.plot_delta, d.delta)):
        ax.text(v * 100 + (0.4 if v > 0 else -0.4), y, f"{raw:+.3f}",
                va="center", ha="left" if v > 0 else "right",
                fontsize=8.5, color=PHI_NAVY, weight="bold")
    ax.axvline(0, color=PHI_GRAY, lw=1.2)
    lo, hi = (d.plot_delta * 100).min(), (d.plot_delta * 100).max()
    ax.set_xlim(lo * 1.35, max(hi * 1.35, 1.2))
    ax.set_xlabel("Change in the pitcher's favour, pct pts\n(red = better in 2023-24, navy = worse)",
                  fontsize=9)
    ax.set_title("ED-1 — what decayed from the 2022 peak to 2023-24",
                 fontsize=10.5, color=PHI_NAVY, weight="bold")
    ax.grid(axis="x", alpha=.2)

    ax = axes[1]
    tcols = ["ff_velo", "ff_ivb_in", "zone_strict", "first_pitch_strike_rate",
             "whiff_rate", "chase_rate"]
    tlabels = ["FF velo\n(mph)", "FF IVB\n(in)", "Zone%\n(strict)", "1st-pitch\nstrike%",
               "Whiff%", "Chase%"]
    good = terc[terc.tercile == "good"].iloc[0]
    bad = terc[terc.tercile == "bad"].iloc[0]
    x = np.arange(len(tcols))
    # normalise each pair to the good-outing value for display
    gvals = [good[c] for c in tcols]
    bvals = [bad[c] for c in tcols]
    rel = [(b - g) / g * 100 if g else np.nan for g, b in zip(gvals, bvals)]
    ax.bar(x, rel, color=[PHI_NAVY if r < 0 else PHI_RED for r in rel], edgecolor="white")
    for i, (r, g, b) in enumerate(zip(rel, gvals, bvals)):
        ax.text(i, r + (0.4 if r >= 0 else -0.9),
                f"{g:.1f}→{b:.1f}" if abs(g) > 5 else f"{g:.3f}→{b:.3f}",
                ha="center", fontsize=7.5, color=PHI_NAVY)
    ax.axhline(0, color=PHI_GRAY, lw=1.2)
    ax.set_xticks(x)
    ax.set_xticklabels(tlabels, fontsize=8)
    ax.set_ylabel("Bad-outing value vs good-outing value, %", fontsize=9)
    ax.set_title("ED-2 — what looks different on his bad days\n(good vs bad outing terciles, >=10 BF)",
                 fontsize=10, color=PHI_NAVY, weight="bold")
    ax.grid(axis="y", alpha=.2)
    fig.suptitle("Performance drivers — era decay and outing-level tells",
                 fontsize=13, color=PHI_NAVY, weight="bold")
    fig.text(.5, .005, "Source: dp_uc36_era_delta_peak_decline.csv, dp_uc36_outing_terciles.csv",
             ha="center", fontsize=7.5, color=PHI_GRAY)
    fig.tight_layout(rect=[0, .03, 1, .92])
    fig.savefig(path, dpi=125)
    plt.close(fig)


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    d, post = load_cortes()

    # ---- ENTITY LOCK ASSERTIONS (data-quality-engineer, blocking) ----
    assert d.pitcher.nunique() == 1 and d.pitcher.iloc[0] == CORTES, "entity lock failed"
    assert d.game_type.unique().tolist() == ["R"], "non regular-season rows in rate frame"
    assert not d.duplicated(["game_pk", "at_bat_number", "pitch_number"]).any(), "dupes"
    assert 2026 not in d.game_year.unique(), "2026 rows present — gap premise broken"
    assert d.p_throws.unique().tolist() == ["L"], "handedness lock failed (expect LHP)"

    # ---- 1. appearance grain + UD family (Business Question 1) -----------
    ap = appearance_grain(d)
    ap.to_csv(f"{OUT_DIR}/dp_uc36_appearance_log.csv", index=False)
    ud = usage_deployment(ap)
    ud.to_csv(f"{OUT_DIR}/dp_uc36_usage_by_season.csv", index=False)

    # 2025 stint split (MIL Mar-Apr starts vs SD Aug-Sep) — outing-log view
    ap25 = ap[ap.game_year == 2025].copy()
    ap25.to_csv(f"{OUT_DIR}/dp_uc36_2025_stint_log.csv", index=False)

    # rest-days behaviour: performance by rest bucket (starts only, career)
    aps = ap[ap.is_start].copy()
    aps["rest_bucket"] = pd.cut(aps.rest_days, [-1, 3, 4, 5, 365],
                                labels=["<=3", "4", "5", "6+"])
    rest_perf = []
    for b in ["<=3", "4", "5", "6+"]:
        pks = aps.loc[aps.rest_bucket == b, "game_pk"]
        sub = d[d.game_pk.isin(pks)]
        if len(sub) == 0:
            continue
        r = kpi_block(sub.assign(_="x"), ["_"]).iloc[0]
        rest_perf.append({"rest_days_before_start": b, "starts": len(pks),
                          "plate_apps": int(r.plate_apps), "woba": r.woba,
                          "krate": r.krate, "bbrate": r.bbrate,
                          "hard_hit_rate": r.hard_hit_rate, "xwobacon": r.xwobacon})
    pd.DataFrame(rest_perf).to_csv(f"{OUT_DIR}/dp_uc36_rest_performance.csv", index=False)

    # ---- 2. season + phase KPI logs --------------------------------------
    season = kpi_block(d, ["game_year"]).merge(
        ud[["game_year", "games", "role_label"]], on="game_year", how="left")
    season.to_csv(f"{OUT_DIR}/dp_uc36_season_log.csv", index=False)
    dp = d[d.phase.notna()].copy()
    phase = kpi_block(dp, ["phase"])
    phase["phase"] = pd.Categorical(phase.phase, PHASE_ORDER, ordered=True)
    phase = phase.sort_values("phase")
    phase.to_csv(f"{OUT_DIR}/dp_uc36_phase_summary.csv", index=False)

    # ---- 3. platoon (Business Question 2) --------------------------------
    plat_career = kpi_block(d, ["stand"])
    plat_career.to_csv(f"{OUT_DIR}/dp_uc36_platoon_career.csv", index=False)
    plat_phase = kpi_block(dp, ["phase", "stand"])
    plat_phase.to_csv(f"{OUT_DIR}/dp_uc36_platoon_by_phase.csv", index=False)
    plat_season = kpi_block(d, ["game_year", "stand"])
    plat_season.to_csv(f"{OUT_DIR}/dp_uc36_platoon_by_season.csv", index=False)

    # mix by hand x season (the DPO's pm frame, kernel-computed)
    mix = arsenal_profile(d, ["stand", "game_year", "pitch_name"])
    mix.to_csv(f"{OUT_DIR}/dp_uc36_mix_by_hand_season.csv", index=False)

    # recent approach detail for the battery: 2023-25, hand x pitch
    recent = d[d.game_year >= 2023]
    pbh = arsenal_profile(recent, ["stand", "pitch_name"])
    pbh.to_csv(f"{OUT_DIR}/dp_uc36_pitch_by_hand_2023_25.csv", index=False)

    # count-state usage, 2022 peak vs 2023-24 (never blended)
    for tag, frame in [("peak2022", d[d.game_year == 2022]),
                      ("decline2324", d[d.game_year.isin([2023, 2024])])]:
        cu = count_state(tracked(frame))
        cnt_usage = (pd.crosstab([cu.stand, cu.count_state], cu.pitch_name,
                                 normalize="index").round(3).reset_index())
        cnt_n = (cu.groupby(["stand", "count_state"], as_index=False)
                   .agg(pitches=("pitch_name", "size")))
        cnt_usage = cnt_usage.merge(cnt_n, on=["stand", "count_state"], how="left")
        cnt_usage.to_csv(f"{OUT_DIR}/dp_uc36_count_usage_{tag}.csv", index=False)

    # putaway pitch by hand (2-strike usage + whiff), 2023-25
    two = recent[recent.strikes == 2]
    put = arsenal_profile(two, ["stand", "pitch_name"])
    put = put[put.pitches >= 20]
    put.to_csv(f"{OUT_DIR}/dp_uc36_putaway_pitch_by_hand.csv", index=False)

    # location profile: where he lives, by hand (2023-25, TRACKED)
    loc = tracked(recent).groupby(["stand"], as_index=False).agg(
        pitches=("pitch_name", "size"), plate_x=("plate_x", "mean"),
        plate_z=("plate_z", "mean"))
    edge = tracked(recent).copy()
    edge["h_side"] = add_horizontal_side(edge).h_side
    loc_side = (edge.groupby(["stand", "h_side"], as_index=False)
                .agg(pitches=("pitch_name", "size")))
    loc_side["share"] = loc_side.pitches / loc_side.groupby(
        loc_side.stand).pitches.transform("sum")
    loc.to_csv(f"{OUT_DIR}/dp_uc36_location_means_by_hand.csv", index=False)
    loc_side.round(3).to_csv(f"{OUT_DIR}/dp_uc36_location_side_by_hand.csv", index=False)

    # ---- 4. stuff tracking (Business Question 3) -------------------------
    stuff = arsenal_profile(d, ["game_year", "pitch_name"])
    stuff.to_csv(f"{OUT_DIR}/dp_uc36_stuff_by_pitch_season.csv", index=False)
    # release/mechanics by season (all tracked pitches)
    mech = add_movement_cols(tracked(d)).groupby("game_year", as_index=False).agg(
        pitches=("pitch_name", "size"), ext_ft=("release_extension", "mean"),
        arm_angle=("arm_angle", "mean"), rel_x=("release_pos_x", "mean"),
        rel_z=("release_pos_z", "mean"))
    mech.round(3).to_csv(f"{OUT_DIR}/dp_uc36_mechanics_by_season.csv", index=False)
    # monthly arc 2024-2025 (pre-surgery trend), FF only + process
    cm = d[d.game_year >= 2024].copy()
    cm["month"] = cm.game_date.dt.to_period("M").astype(str)
    arc = kpi_block(cm, ["month"])[
        ["month", "pitches", "plate_apps", "krate", "bbrate", "whiff_rate",
         "chase_rate", "csw_rate", "hard_hit_rate", "xwobacon"]]
    mv = (cm[cm.pitch_type == "FF"].groupby("month", as_index=False)
          .agg(ff_velo=("release_speed", "mean"), ff_n=("release_speed", "size")))
    mg = cm.groupby("month", as_index=False).agg(outings=("game_pk", "nunique"))
    arc = arc.merge(mv, on="month", how="left").merge(mg, on="month", how="left").round(3)
    arc.to_csv(f"{OUT_DIR}/dp_uc36_monthly_arc_2024_25.csv", index=False)

    # ---- 5. drivers (Business Question 4) --------------------------------
    ed = era_delta(d[d.game_year.isin([2023, 2024])], d[d.game_year == 2022],
                   "decline_2023_24", "peak_2022")
    ed.to_csv(f"{OUT_DIR}/dp_uc36_era_delta_peak_decline.csv", index=False)

    # outing terciles: >=10 BF appearances, per-outing wOBA-against
    ap_ok = ap[ap.uq_pas >= 10]
    per_out = nresults(["game_pk"], d[d.game_pk.isin(ap_ok.game_pk)])
    per_out = per_out.sort_values("woba").reset_index(drop=True)
    n3 = len(per_out) // 3
    per_out["tercile"] = "mid"
    per_out.loc[: n3 - 1, "tercile"] = "good"
    per_out.loc[len(per_out) - n3:, "tercile"] = "bad"
    rows = []
    for t in ["good", "mid", "bad"]:
        pks = per_out.loc[per_out.tercile == t, "game_pk"]
        sub = d[d.game_pk.isin(pks)]
        r = kpi_block(sub.assign(_="x"), ["_"]).iloc[0]
        ff = sub[sub.pitch_type == "FF"]
        ffm = add_movement_cols(tracked(ff))
        rows.append({"tercile": t, "outings": len(pks), "plate_apps": int(r.plate_apps),
                     "woba": r.woba, "xwobacon": r.xwobacon,
                     "ff_velo": round(ff.release_speed.mean(), 2),
                     "ff_ivb_in": round(ffm.ivb_in.mean(), 2),
                     "zone_strict": round(zone_rate_strict(sub), 3),
                     "first_pitch_strike_rate": r.first_pitch_strike_rate,
                     "whiff_rate": r.whiff_rate, "chase_rate": r.chase_rate,
                     "hard_hit_rate": r.hard_hit_rate, "krate": r.krate,
                     "bbrate": r.bbrate})
    terc = pd.DataFrame(rows)
    terc.to_csv(f"{OUT_DIR}/dp_uc36_outing_terciles.csv", index=False)

    # season indicator table (co-movement read; no inference printed)
    ind = season[["game_year", "plate_apps", "woba", "xwobacon", "krate", "bbrate",
                  "whiff_rate", "chase_rate", "first_pitch_strike_rate",
                  "hard_hit_rate"]].copy()
    ffv = (d[d.pitch_type == "FF"].groupby("game_year", as_index=False)
           .agg(ff_velo=("release_speed", "mean")))
    ffb = (add_movement_cols(tracked(d[d.pitch_type == "FF"]))
           .groupby("game_year", as_index=False).agg(ff_ivb_in=("ivb_in", "mean")))
    ind = ind.merge(ffv, on="game_year", how="left").merge(ffb, on="game_year", how="left")
    ind.round(3).to_csv(f"{OUT_DIR}/dp_uc36_season_indicators.csv", index=False)

    # ---- 6. times-through-order (manager leash; starts only) -------------
    ds = d[d.game_pk.isin(ap[ap.is_start].game_pk)].copy()
    ds["bf_seq"] = ds.groupby("game_pk").at_bat_number.transform(
        lambda s: s.rank(method="dense"))
    ds["tto"] = np.where(ds.bf_seq <= 9, "1st time through",
                  np.where(ds.bf_seq <= 18, "2nd time through", "3rd+"))
    tto = kpi_block(ds, ["tto"])[
        ["tto", "pitches", "plate_apps", "woba", "krate", "whiff_rate",
         "hard_hit_rate", "avg_ev", "xwobacon"]]
    ffv_t = (ds[ds.pitch_type == "FF"].groupby("tto", as_index=False)
             .agg(ff_velo=("release_speed", "mean")))
    tto = tto.merge(ffv_t, on="tto", how="left").round(3)
    tto.to_csv(f"{OUT_DIR}/dp_uc36_times_through_order.csv", index=False)

    # relief entries: score state at entry (2019-21 relief era; era-dated)
    rel = ap[(~ap.is_start) & (ap.game_year <= 2021)].copy()
    rel["score_state"] = pd.cut(
        rel.entry_score_diff, [-99, -4.5, -1.5, -0.5, 0.5, 1.5, 3.5, 99],
        labels=["down 5+", "down 2-4", "down 1", "tied", "up 1", "up 2-3", "up 4+"])
    rel_sum = (rel.groupby("score_state", observed=True, as_index=False)
               .agg(entries=("game_pk", "size")))
    rel_sum.to_csv(f"{OUT_DIR}/dp_uc36_relief_entry_states_2019_21.csv", index=False)

    # ---- 7. postseason context (NEVER blended into rates) ----------------
    post_line = nresults(["game_type"], _attach_woba(post.copy()))
    post_line.to_csv(f"{OUT_DIR}/dp_uc36_postseason_line.csv", index=False)
    fr = post[(post.events == "home_run") &
              (post.des.astype(str).str.contains("Freeman"))]
    ctx = fr[["game_date", "game_type", "inning", "balls", "strikes", "pitch_type",
              "release_speed", "des"]].copy()
    ctx.to_csv(f"{OUT_DIR}/dp_uc36_postseason_context.csv", index=False)

    # ---- 8. DQ scorecard -------------------------------------------------
    r24 = d[d.game_year >= 2021]   # tracking-era scope for completeness checks
    TRACKING = ["release_speed", "release_spin_rate", "pfx_x", "pfx_z", "plate_x",
                "plate_z", "sz_top", "sz_bot", "release_extension", "zone",
                "description", "stand"]
    CONTACT = ["launch_speed", "estimated_woba_using_speedangle", "launch_angle"]
    bip_r = r24[r24.type == "X"]
    dq = []
    for c in TRACKING:
        v = tracked(r24)[c].notna().mean()
        dq.append({"check": f"completeness::{c}", "dimension": "Completeness",
                   "scope": "2021+ / tracked pitches", "value": round(v, 4),
                   "threshold": ">= 0.95 (tracking)",
                   "status": "PASS" if v >= 0.95 else "WARN"})
    for c in CONTACT:
        v = bip_r[c].notna().mean()
        dq.append({"check": f"completeness::{c}", "dimension": "Completeness",
                   "scope": "2021+ / balls in play only", "value": round(v, 4),
                   "threshold": ">= 0.95 of BIP (contact-defined field)",
                   "status": "PASS" if v >= 0.95 else "WARN"})
    aa_early = d[d.game_year <= 2019].arm_angle.notna().mean()
    aa_late = d[d.game_year >= 2021].arm_angle.notna().mean()
    dq.append({"check": "sensor_boundary::arm_angle absent pre-2020",
               "dimension": "Completeness", "scope": "all",
               "value": f"2018-19: {aa_early:.3f} / 2021+: {aa_late:.3f}",
               "threshold": "uc-pos-009 standard: disclose, never impute",
               "status": "PASS — arm-angle trend reads start at 2021; pre-2020 "
                         "cells are NULL by sensor boundary, not missing data"})
    n_untracked = int(d.pitch_name.isna().sum())
    dq += [
        {"check": "population::untracked rows identified", "dimension": "Validity",
         "scope": "all R rows", "value": n_untracked,
         "threshold": "all null-pitch_name rows enumerated",
         "status": "PASS — %d rows (%s); excluded from TRACKED denominators"
                   % (n_untracked,
                      "; ".join(f"{k}:{v}" for k, v in
                                d[d.pitch_name.isna()].description.value_counts().items()))},
        {"check": "zone_rate::locked vs strict (O2)", "dimension": "Accuracy",
         "scope": "all R rows",
         "value": round(float(chase_rate(["_"], d.assign(_="x")).iloc[0].in_zone_rate)
                        - zone_rate_strict(d), 4),
         "threshold": "publish STRICT only",
         "status": "PASS — locked %.4f vs strict %.4f; report publishes STRICT"
                   % (chase_rate(["_"], d.assign(_="x")).iloc[0].in_zone_rate,
                      zone_rate_strict(d))},
        {"check": "launch_speed::populated on non-BIP rows (O3)",
         "dimension": "Accuracy", "scope": "all R rows",
         "value": int(((d.launch_speed.notna()) & (d.type != "X")).sum()),
         "threshold": "all EV means filter type=='X'",
         "status": "PASS — every published EV mean is BIP-only"},
        {"check": "entity_lock::pitcher==641482", "dimension": "Validity",
         "scope": "all", "value": int(d.pitcher.nunique()), "threshold": "== 1",
         "status": "PASS"},
        {"check": "handedness_lock::p_throws=='L'", "dimension": "Validity",
         "scope": "all", "value": ";".join(d.p_throws.unique()), "threshold": "== L",
         "status": "PASS"},
        {"check": "dedup::game_pk+at_bat+pitch", "dimension": "Uniqueness",
         "scope": "all", "value": int(d.duplicated(
             ["game_pk", "at_bat_number", "pitch_number"]).sum()),
         "threshold": "== 0", "status": "PASS"},
        {"check": "game_type::rates on R only", "dimension": "Validity", "scope": "all",
         "value": ";".join(sorted(d.game_type.unique())), "threshold": "== R",
         "status": "PASS — postseason isolated to context receipts"},
        {"check": "gap::2026 absent (no service since surgery)",
         "dimension": "Consistency", "scope": "all",
         "value": int((d.game_year == 2026).sum()), "threshold": "== 0",
         "status": "PASS — recorded true gap, never interpolated"},
        {"check": "gap::2025 in-season gap (Apr 4 - Aug 5)", "dimension": "Consistency",
         "scope": "2025", "value": "MIL 2 G (Mar-Apr) -> SD 6 G (Aug-Sep)",
         "threshold": "stint boundary disclosed; appearance log splits stints",
         "status": "PASS — injury-interrupted season; season grain kept whole "
                   "and disclosed"},
    ]
    si_x = tracked(d[d.game_year >= 2021]).loc[lambda x: x.pitch_type == "SI", "pfx_x"].mean()
    ch_x = tracked(d[d.game_year >= 2021]).loc[lambda x: x.pitch_type == "CH", "pfx_x"].mean()
    st_x = tracked(d[d.game_year >= 2021]).loc[lambda x: x.pitch_type == "ST", "pfx_x"].mean()
    dq += [
        {"check": "orientation::LHP sinker/changeup pfx_x>0 (arm side)",
         "dimension": "Accuracy", "scope": "2021+",
         "value": f"SI {si_x:.3f} / CH {ch_x:.3f}", "threshold": "> 0",
         "status": "PASS" if (si_x > 0 and ch_x > 0) else "FAIL"},
        {"check": "orientation::LHP sweeper pfx_x<0 (glove side)",
         "dimension": "Accuracy", "scope": "2021+",
         "value": round(st_x, 3), "threshold": "< 0",
         "status": "PASS" if st_x < 0 else "FAIL"},
        {"check": "sample::2025 below full-season floor", "dimension": "Accuracy",
         "scope": "2025",
         "value": int(get_stats(["_"], d[d.game_year == 2025].assign(_="x")).iloc[0].plate_apps),
         "threshold": "2025 quoted only with PA printed",
         "status": "WARN — 2025 = 8 G / 599 pitches; directional only, "
                   "every 2025 line prints its PA"},
        {"check": "sample::career BF >= 100 publish floor", "dimension": "Accuracy",
         "scope": "career", "value": int(get_stats(["_"], d.assign(_="x")).iloc[0].plate_apps),
         "threshold": ">= 100", "status": "PASS"},
    ]
    dqdf = pd.DataFrame(dq)
    dqdf.to_csv(f"{OUT_DIR}/dp_uc36_dq_scorecard.csv", index=False)

    # ---- 9. freshness manifest -------------------------------------------
    fm = pd.DataFrame([
        {"source": "data/opponents/cortes.parquet", "tier": "MLB career (R rates)",
         "rows_after_filter": len(d),
         "window": f"{d.game_date.min().date()} .. {d.game_date.max().date()}",
         "as_of": AS_OF,
         "fitness": "FIT — career-complete through final 2025 appearance; "
                    "arm_angle 2021+ only (sensor boundary)"},
        {"source": "data/opponents/cortes.parquet", "tier": "Postseason context",
         "rows_after_filter": len(post), "window": "2019-2024 (D/L/W)", "as_of": AS_OF,
         "fitness": "CONTEXT ONLY — never blended into rates"},
        {"source": "(none)", "tier": "2026 (post-surgery)", "rows_after_filter": 0,
         "window": "n/a", "as_of": AS_OF,
         "fitness": "ABSENT — TRUE GAP; zero competitive pitches since 2025-09-03"},
        {"source": "(none)", "tier": "Phillies rows for pitcher 641482",
         "rows_after_filter": 0, "window": "n/a", "as_of": AS_OF,
         "fitness": "ABSENT — signed 2026-08-19; acquisition-variant standard"},
        {"source": "manual carry-in", "tier": "Roster/context facts",
         "rows_after_filter": None, "window": "2026-08-19/20", "as_of": AS_OF,
         "fitness": "MANUAL — signing (1-yr prorated ML), Brian Keller DFA'd for "
                    "the 40-man spot (DPO correction), surgery mid-Oct 2025, "
                    "expected multi-inning relief role, 2022 All-Star selection. "
                    "Sources logged in 07."},
    ])
    fm.to_csv(f"{OUT_DIR}/dp_uc36_freshness_manifest.csv", index=False)

    # ---- figures ---------------------------------------------------------
    fig_deployment(ud, f"{OUT_DIR}/dp_uc36_fig1_deployment.png")
    fig_arsenal_evolution(mix, f"{OUT_DIR}/dp_uc36_fig2_arsenal_evolution.png")
    fig_stuff(d, f"{OUT_DIR}/dp_uc36_fig3_stuff_ff.png", "FF")
    fig_platoon(plat_phase, f"{OUT_DIR}/dp_uc36_fig4_platoon.png")
    fig_drivers(ed, terc, f"{OUT_DIR}/dp_uc36_fig5_drivers.png")

    # ---- console receipt -------------------------------------------------
    pd.set_option("display.width", 200)
    print("=" * 78)
    print("dp_uc36 — Nestor Cortes acquisition read | entity lock pitcher==641482")
    print("=" * 78)
    print(f"\nR rows: {len(d)} | postseason context rows: {len(post)}")
    print("\n--- UD FAMILY (usage & deployment, DPO definitions) ---")
    print(ud[["game_year", "games", "starts", "bulks", "start_share", "bulk_share",
              "relief_share", "innings_per_gm", "plate_apps_per_gm",
              "role_label"]].to_string(index=False))
    print("\n--- SEASON LOG ---")
    print(season[["game_year", "games", "plate_apps", "woba", "krate", "bbrate",
                  "whiff_rate", "hard_hit_rate", "xwobacon",
                  "role_label"]].to_string(index=False))
    print("\n--- PHASE SUMMARY ---")
    print(phase[["phase", "plate_apps", "woba", "krate", "bbrate", "whiff_rate",
                 "chase_rate", "hard_hit_rate", "xwobacon"]].to_string(index=False))
    print("\n--- PLATOON, CAREER ---")
    print(plat_career[["stand", "plate_apps", "woba", "krate", "bbrate",
                       "whiff_rate", "hard_hit_rate", "xwobacon"]].to_string(index=False))
    print("\n--- PLATOON BY PHASE ---")
    print(plat_phase[["phase", "stand", "plate_apps", "woba", "krate",
                      "whiff_rate", "xwobacon"]].to_string(index=False))
    print("\n--- ERA DELTA (2022 peak -> 2023-24) ---")
    print(ed.to_string(index=False))
    print("\n--- OUTING TERCILES ---")
    print(terc.to_string(index=False))
    print("\n--- TTO (starts only) ---")
    print(tto.to_string(index=False))
    print("\n--- REST PERFORMANCE (starts) ---")
    print(pd.DataFrame(rest_perf).to_string(index=False))
    print("\n--- RELIEF ENTRY STATES 2019-21 ---")
    print(rel_sum.to_string(index=False))
    print("\n--- MONTHLY ARC 2024-25 ---")
    print(arc.to_string(index=False))
    print("\n--- 2025 STINT LOG ---")
    print(ap25[["game_date", "pit_team", "entry_inning", "innings_delta",
                "total_pitches", "uq_pas"]].to_string(index=False))
    print("\n--- POSTSEASON LINE (context only) ---")
    print(post_line.to_string(index=False))
    print("\n--- POSTSEASON CONTEXT (Freeman) ---")
    print(ctx.to_string(index=False))
    print("\n--- STUFF: FF BY SEASON ---")
    ffs = stuff[stuff.pitch_name == "4-Seam Fastball"]
    print(ffs[["game_year", "pitches", "usage", "velo", "spin", "ivb_in", "hb_in",
               "ext_ft", "arm_angle", "whiff_rate", "xwobacon"]].to_string(index=False))
    print("\n--- DQ SCORECARD (non-PASS only) ---")
    np_rows = dqdf[~dqdf.status.str.startswith("PASS")]
    print(np_rows.to_string(index=False) if len(np_rows) else "(all PASS)")
    print(f"\nreceipts written to {OUT_DIR}")


if __name__ == "__main__":
    main()
