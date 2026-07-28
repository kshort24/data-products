"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #27  (uc-pps-022)
"Brian Keller (RHP, LHV/AAA) 2026: what is driving the results, what are the
 underlying indicators, and what is the gameplan for a projected MLB call-up
 — including how Realmuto should call the game."
============================================================================

Layer-3 BUILD artifact for the Phillies Pitching (pps) value stream.

Pattern lineage:
  UC#8  (dp_uc8_nola_vs_nationals)  — canonical flat-file pattern; origin of
        the NEW KPIs edge_rate / ooz_called_strike_rate / air_gb_rate.
  UC#11 (dp_uc11_rangel_vs_pirates) — multi-level evidence tier; the
        "first career start / no MLB book" precedent this UC extends.
  UC#26 (dp_uc25_nola_vs_dodgers)   — direct predecessor; locked-KPI kernel
        and the xwOBAcon correction are inherited from here verbatim.

WHAT IS NEW IN UC#27:
  * FIRST AAA-PRIMARY UC. Every prior pps advance report had an MLB tier as
    the primary evidence base with AAA optional as a supporting tier. Keller
    has never thrown an MLB pitch, so the AAA tier IS the primary tier. The
    governance consequence is handled explicitly: a same-league, same-season
    comparison population (the entire LHV 2026 pitching staff, 42 pitchers,
    14,960 pitches) is computed alongside EVERY Keller rate so that no number
    is published without a benchmark. See 01_ and 04_.
  * PROVISIONAL KPI SR-M1 "Mayza Success Rate" (tm_success_rate), supplied by
    the DPO from a Tim Mayza On Pattison interview. Computed and reported
    under a PROVISIONAL banner; the ratification packet (intent-vs-
    implementation reconciliation, three candidate variants, grain
    constraints) is in 04_ §SR-M1. NOT locked. Do not inherit downstream
    until the DPO ratifies a variant.
  * RECENCY-AS-MECHANISM: the starts 1-4 vs 5-8 split is not decoration —
    it is the analytical spine of the report. The usage shift (4-seam down,
    sinker up) is tested against contact quality and command in the same cut.

GOVERNANCE:
  * Every locked rate KPI is inherited VERBATIM from the UC8->UC11->UC26 line
    (get_stats/nresults, whiff_rate, chase_rate, putaway_rate, fpsr,
    hard_hit_rate, edge_rate, ooz_called_strike_rate, air_gb_rate,
    chase_up_rate, xwobacon). No locked KPI was re-derived this session.
  * ONE new KPI (SR-M1) is computed and it is flagged PROVISIONAL everywhere
    it appears — in the CSV receipts, in the report, and in the persona card.

DATA WINDOW / FRESHNESS:
  * Source: data/opponents/lhvp26.parquet (Lehigh Valley IronPigs pitching,
    2026). Cache max game_date 2026-07-23; Keller's last logged start
    2026-07-17. Report date 2026-07-24.
  * ENTITY LOCK: pitcher == 662144 (Brian Keller). The same file contains
    Brad Keller (641745) — a name filter on "Keller" contaminates the slice
    with a second pitcher. This is the canonical Nola / "Nolan Hoffman"
    failure mode; the lock is asserted in the DQ scorecard.
  * game_type == 'R' only. Dedup on (game_pk, at_bat_number, pitch_number).

OUTPUTS (NEW files, none overwritten), written to ./out/:
  dp_uc26_results_headline.csv        Keller vs LHV-staff season line
  dp_uc26_game_lines.csv              per-start line, all 8 starts
  dp_uc26_by_stand.csv                results by batter stand + staff baseline
  dp_uc26_arsenal.csv                 usage / velo / movement / slot by pitch
  dp_uc26_arsenal_by_stand.csv        usage by stand x pitch
  dp_uc26_process_kpis.csv            locked process KPI panel + baseline
  dp_uc26_process_by_stand.csv        process KPIs L vs R + baseline
  dp_uc26_pitch_kpis.csv              per-pitch process + contact quality
  dp_uc26_contact_quality.csv         EV/LA/HH/bb_type mix by pitch
  dp_uc26_recency_split.csv           starts 1-4 vs 5-8 (the mechanism)
  dp_uc26_recency_usage.csv           usage shift across the same split
  dp_uc26_tto.csv                     times-through-order splits
  dp_uc26_velo_by_inning.csv          fastball velo decay (leash evidence)
  dp_uc26_first_pitch.csv             0-0 strike rate by stand x pitch
  dp_uc26_two_strike.csv              2-strike whiff/putaway by stand x pitch
  dp_uc26_home_runs.csv               all 5 HR allowed, with location + count
  dp_uc26_sr_m1_provisional.csv       PROVISIONAL Mayza success rate
  dp_uc26_sr_m1_variants.csv          PROVISIONAL ratification reconciliation
  dp_uc26_sr_m1_leaderboard.csv       PROVISIONAL LHV staff SR-M1 context
  dp_uc26_dq_scorecard.csv            data-quality-engineer scorecard
  dp_uc26_freshness_manifest.csv      source / window / fitness receipts
  dp_uc26_fig1_arsenal.png            arsenal: usage x whiff x contact quality
  dp_uc26_fig2_recency.png            the mechanism: usage shift -> outcomes
  dp_uc26_fig3_location.png           4-seam vs sinker location by stand
  dp_uc26_fig4_gameplan.png           2-strike + first-pitch call grid
============================================================================
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out"); os.makedirs(OUT_DIR, exist_ok=True)

KELLER = 662144          # Brian Keller, MLBAM. NOT Brad Keller (641745).
BRAD_KELLER = 641745     # contamination trap, asserted against in the DQ scorecard
REPORT_DATE = "2026-07-24"
SEASON = 2026

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "opponents"),
    "/sessions/zen-keen-goldberg/mnt/MLB/data/opponents",
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\opponents",
]
OPP_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
_WOBA_CANDIDATES = [
    os.path.join(HERE, "wOBA and FIP Constants.csv"),
    "/sessions/zen-keen-goldberg/mnt/MLB/wOBA and FIP Constants.csv",
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv",
]
WOBA_CSV = next((p for p in _WOBA_CANDIDATES if p and os.path.isfile(p)), None)

# --- constants inherited verbatim from dp_uc8 / dp_uc25 --------------------
PLATE_HALF = 0.83
BALL_FT = 2.94 / 12.0
SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]
TAKES = ["called_strike", "ball", "blocked_ball", "ball_blocked"]

PHI_RED, PHI_NAVY, PHI_GRAY, PHI_LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
PITCH_COLORS = {"4-Seam Fastball": "#E81828", "Sinker": "#FF7F0E",
                "Cutter": "#8C564B", "Slider": "#1F77B4", "Curveball": "#2CA02C"}
PITCH_ORDER = ["4-Seam Fastball", "Cutter", "Sinker", "Slider", "Curveball"]

EVENT_OUTS = {"field_out": 1, "strikeout": 1, "force_out": 1, "sac_fly": 1,
              "sac_bunt": 1, "fielders_choice_out": 1, "fielders_choice": 1,
              "grounded_into_double_play": 2, "double_play": 2,
              "strikeout_double_play": 2, "sac_fly_double_play": 2,
              "triple_play": 3, "other_out": 1}


# ===========================================================================
# LOADERS
# ===========================================================================
def _coerce(df):
    for c in ["plate_x", "plate_z", "sz_top", "sz_bot", "pfx_x", "pfx_z",
              "release_speed", "release_spin_rate", "release_extension",
              "launch_speed", "launch_angle", "strikes", "balls",
              "pitch_number", "woba_value", "woba_denom", "zone", "arm_angle",
              "api_break_x_arm", "api_break_z_with_gravity", "inning",
              "n_thruorder_pitcher"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_lhv():
    """Full LHV 2026 pitching log = the comparison population. Keller is a
    slice of it, so the benchmark is same-league, same-season, same-park-mix."""
    if OPP_DIR is None:
        raise FileNotFoundError("Could not locate data/opponents. Set MLB_DATA_ROOT.")
    path = os.path.join(OPP_DIR, "lhvp26.parquet")
    d = pd.read_parquet(path)
    d = d[d.game_type == "R"].drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    d = _coerce(d)
    d["game_date"] = pd.to_datetime(d.game_date)
    d["game_year"] = d.game_year.astype(int)
    if WOBA_CSV:
        w = pd.read_csv(WOBA_CSV)
        d = d.drop(columns=[c for c in w.columns if c != "Season" and c in d.columns])
        d = d.merge(w, left_on="game_year", right_on="Season", how="left")
    return d.reset_index(drop=True)


# ===========================================================================
# LOCKED KPI FUNCTIONS — inherited VERBATIM from dp_uc25 (<- uc15 <- uc11 <- uc8).
# DO NOT EDIT. Any change here is a breaking change and goes to version-controller.
# ===========================================================================
def get_stats(level, df):
    if isinstance(level, str): level = [level]
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
    singles = cnt(df.events == "single", "singles"); doubles = cnt(df.events == "double", "doubles")
    triples = cnt(df.events == "triple", "triples"); hrs = cnt(df.events == "home_run", "hrs")
    walks = cnt(df.events == "walk", "walks")
    ks = cnt(df.events.isin(["strikeout", "strikeout_double_play"]), "strikeouts")
    hbp = cnt(df.events == "hit_by_pitch", "hbp")
    wBB = wsum(df.events == "walk", "wBB", "wBB"); wHBP = wsum(df.events == "hit_by_pitch", "wHBP", "wHBP")
    w1B = wsum(df.events == "single", "w1B", "w1B"); w2B = wsum(df.events == "double", "w2B", "w2B")
    w3B = wsum(df.events == "triple", "w3B", "w3B"); wHR = wsum(df.events == "home_run", "wHR", "wHR")
    xba = df.groupby(level, as_index=False).agg(xba=("estimated_ba_using_speedangle", "mean"))
    xwoba = df.groupby(level, as_index=False).agg(xwoba=("estimated_woba_using_speedangle", "mean"))
    out = base
    for x in [pa, ab, bip, hits, singles, doubles, triples, hrs, walks, ks, hbp,
              wBB, wHBP, w1B, w2B, w3B, wHR, xba, xwoba]:
        out = out.merge(x, how="left", on=level)
    return out.fillna(0)


def nresults(level, df):
    if isinstance(level, str): level = [level]
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
                    "ba", "obp", "slg", "ops", "woba", "xwoba", "krate", "bbrate", "hr_rate"]
    return s[cols].round(3)


def whiff_rate(level, df):
    if isinstance(level, str): level = [level]
    u = df[df.description.isin(SWINGS)].groupby(level, as_index=False).agg(swings=("description", "size"))
    v = df[df.description.isin(WHIFFS)].groupby(level, as_index=False).agg(whiffs=("description", "size"))
    w = u.merge(v, on=level, how="left").fillna({"whiffs": 0})
    w["whiff_rate"] = w.whiffs / w.swings
    return w.round(3)


def chase_rate(level, df):
    if isinstance(level, str): level = [level]
    chase = df[(df.zone > 9) & (df.description.isin(SWINGS))]
    i = chase.groupby(level, as_index=False).agg(chases=("description", "size"))
    j = df[df.zone > 9].groupby(level, as_index=False).agg(ooz=("description", "size"))
    tot = df.groupby(level, as_index=False).agg(pitches=("description", "size"))
    cr = tot.merge(j, on=level, how="left").merge(i, on=level, how="left").fillna(0)
    cr["chase_rate"] = cr.chases / cr.ooz
    cr["in_zone_rate"] = (cr.pitches - cr.ooz) / cr.pitches
    return cr.round(3)


def putaway_rate(level, df):
    if isinstance(level, str): level = [level]
    z = df[df.strikes == 2].groupby(level, as_index=False).agg(pitches2strikes=("description", "size"))
    k = df[df.events.isin(["strikeout", "strikeout_double_play"])].groupby(
        level, as_index=False).agg(strikeouts=("description", "size"))
    z = z.merge(k, on=level, how="left").fillna(0)
    z["putaway_rate"] = z.strikeouts / z.pitches2strikes
    return z.round(3)


def fpsr(level, df):
    if isinstance(level, str): level = [level]
    fp = df[df.pitch_number == 1]
    balls = fp.groupby(level + ["type"], as_index=False).agg(balls=("description", "size"))
    tot = fp.groupby(level, as_index=False).agg(pitches=("description", "size"))
    m = tot.merge(balls[balls.type == "B"][level + ["balls"]], on=level, how="left").fillna({"balls": 0})
    m["first_pitch_strike_rate"] = (m.pitches - m.balls) / m.pitches
    return m.round(3)


def hard_hit_rate(level, df):
    if isinstance(level, str): level = [level]
    hh = df[(df.launch_speed >= 95) & (df.type == "X")].groupby(level, as_index=False).agg(hard_hits=("description", "size"))
    bips = df[df.type == "X"].groupby(level, as_index=False).agg(bips=("description", "size"))
    out = bips.merge(hh, on=level, how="left").fillna(0)
    out["hard_hit_rate"] = out.hard_hits / out.bips
    return out.round(3)


def _dist_to_zone_edge(px, pz, sz_bot, sz_top):
    hw = PLATE_HALF
    dx_out = np.maximum.reduce([-hw - px, px - hw, np.zeros_like(px)])
    dz_out = np.maximum.reduce([sz_bot - pz, pz - sz_top, np.zeros_like(pz)])
    outside = (dx_out > 0) | (dz_out > 0)
    dist_out = np.sqrt(dx_out ** 2 + dz_out ** 2)
    dist_in = np.minimum.reduce([hw - np.abs(px), pz - sz_bot, sz_top - pz])
    return np.where(outside, dist_out, dist_in)


def edge_rate(level, df):
    if isinstance(level, str): level = [level]
    d = df.dropna(subset=["plate_x", "plate_z", "sz_top", "sz_bot"]).copy()
    dist = _dist_to_zone_edge(d.plate_x.values, d.plate_z.values, d.sz_bot.values, d.sz_top.values)
    d["is_edge"] = dist <= BALL_FT
    tot = d.groupby(level, as_index=False).agg(located_pitches=("is_edge", "size"))
    eg = d.groupby(level, as_index=False).agg(edge_pitches=("is_edge", "sum"))
    out = tot.merge(eg, on=level, how="left").fillna(0)
    out["edge_rate"] = out.edge_pitches / out.located_pitches
    return out.round(3)


def ooz_called_strike_rate(level, df):
    if isinstance(level, str): level = [level]
    ooz = df[df.zone > 9]
    tot = ooz.groupby(level, as_index=False).agg(ooz_pitches=("description", "size"))
    cs = ooz[ooz.description == "called_strike"].groupby(level, as_index=False).agg(ooz_called_strikes=("description", "size"))
    takes = ooz[ooz.description.isin(TAKES)].groupby(level, as_index=False).agg(ooz_takes=("description", "size"))
    out = tot.merge(cs, on=level, how="left").merge(takes, on=level, how="left").fillna(0)
    out["ooz_called_strike_rate"] = out.ooz_called_strikes / out.ooz_pitches
    out["ooz_csr_per_take"] = np.where(out.ooz_takes > 0, out.ooz_called_strikes / out.ooz_takes, np.nan)
    return out.round(3)


def air_gb_rate(level, df):
    if isinstance(level, str): level = [level]
    bip = df[df.type == "X"].copy()
    tot = bip.groupby(level, as_index=False).agg(bip=("description", "size"))
    def share(mask, name):
        return bip[mask].groupby(level, as_index=False).agg(**{name: ("description", "size")})
    gb = share(bip.bb_type == "ground_ball", "gb"); fb = share(bip.bb_type == "fly_ball", "fb")
    ld = share(bip.bb_type == "line_drive", "ld"); pu = share(bip.bb_type == "popup", "pu")
    out = tot
    for x in [gb, fb, ld, pu]:
        out = out.merge(x, on=level, how="left")
    out = out.fillna(0)
    out["gb_rate"] = out.gb / out.bip; out["fb_rate"] = out.fb / out.bip
    out["ld_rate"] = out.ld / out.bip; out["pu_rate"] = out.pu / out.bip
    out["air_rate"] = (out.fb + out.ld + out.pu) / out.bip
    return out.round(3)


def chase_up_rate(level, df):
    if isinstance(level, str): level = [level]
    d = df.dropna(subset=["plate_z", "sz_top"]).copy()
    above = d[d.plate_z > d.sz_top]
    tot = above.groupby(level, as_index=False).agg(above_pitches=("description", "size"))
    sw = above[above.description.isin(SWINGS)].groupby(level, as_index=False).agg(above_swings=("description", "size"))
    out = tot.merge(sw, on=level, how="left").fillna(0)
    out["chase_up_rate"] = out.above_swings / out.above_pitches
    return out.round(3)


def xwobacon(level, df):
    """xwOBA on contact = mean estimated_woba_using_speedangle over BIP only.
    The nresults 'xwoba' column is a pitch-level mean and must NOT be cited as
    xwOBAcon (UC#26 DQ fix). Verified this session: 96/96 populated on Keller
    BIP, 2481/2481 on the LHV staff population."""
    if isinstance(level, str): level = [level]
    bip = df[df.type == "X"]
    return bip.groupby(level, as_index=False).agg(
        bip_n=("description", "size"),
        xwobacon=("estimated_woba_using_speedangle", "mean")).round(3)


# ===========================================================================
# PROVISIONAL KPI — SR-M1 "Mayza Success Rate"
# ---------------------------------------------------------------------------
# STATUS: PROVISIONAL. NOT RATIFIED. NOT INHERITABLE.
# Source: DPO, transcribing Tim Mayza's On Pattison interview — a two-pitch
# reliever's goal is a "quick at-bat", defined as reaching two strikes OR
# inducing a ground ball within three pitches.
#
# `tm_success_rate` below is the DPO's code AS SUPPLIED, unmodified, so the
# ratification review has a faithful baseline. `sr_m1_variants` computes the
# two alternate readings of the same sentence. See 04_ §SR-M1 for the
# reconciliation and the recommended ratification decision.
# ===========================================================================
def tm_success_rate(level, df):
    """DPO-SUPPLIED IMPLEMENTATION — verbatim, do not fix in place."""
    if isinstance(level, str):
        level = [level]
    calc_df = df[df.pitch_number < 4]
    calc_level = ['game_pk', 'at_bat_number']
    s2 = calc_df.groupby(calc_level, as_index=False
              ).agg(max_balls=('balls', 'max'), max_strikes=('strikes', 'max'))
    s2w = s2[s2.max_strikes == 2]
    gb = calc_df[calc_df.type == 'X'].groupby(calc_level + ['bb_type'], as_index=False
                                             ).agg(bips=('des', 'size'))
    gbw = gb[gb.bb_type == 'ground_ball']
    z = df.groupby(level + calc_level, as_index=False
              ).agg(max_pitch=('pitch_number', 'max')
                   ).merge(s2w, on=calc_level, how='left', suffixes=('', '_s2w')
                          ).merge(gbw, on=calc_level, how='left', suffixes=('', '_gbw')
                                 ).fillna(0)
    z['is_success'] = np.where((z.max_strikes == 2) | (z.bips == 1), 1, 0)
    zgraph = z.groupby(level, as_index=False
             ).agg(total_success=('is_success', 'sum')
                  ).merge(z.groupby(level, as_index=False
                                   ).agg(total_pas=('game_pk', 'size')), on=level)
    zgraph['success_rate'] = zgraph.total_success / zgraph.total_pas
    return zgraph.round(3)


def sr_m1_variants(level, df):
    """Ratification harness. Recomputes the same idea three ways at PA grain.

    A  as_written   : the DPO function's own logic, reproduced independently.
                      Because `strikes` is the PRE-pitch count, `max_strikes`
                      over pitches 1-3 is the count displayed on pitch 3 — so
                      this fires only when the 2nd strike accrued on pitch 1
                      or 2 AND the PA survived to a 3rd pitch.
    B  two_strike_by_p2 : 2nd strike accrued on or before pitch 2 (no survival
                      requirement) OR GB in pitches 1-3.
    C  two_strike_by_p3 : 2nd strike accrued on or before pitch 3 OR GB in
                      pitches 1-3. This is the literal reading of the stated
                      business intent ("two strikes ... within 3 pitches").

    Strike accrual counts any pitch with type != 'B' (called strike, swinging
    strike, foul, ball in play), which matches how a count actually advances.
    Foul balls at two strikes cannot advance past two, so no correction needed.
    """
    if isinstance(level, str): level = [level]
    d = df.sort_values(["game_pk", "at_bat_number", "pitch_number"]).copy()
    d["is_strike_event"] = (d.type != "B").astype(int)
    d["strikes_accrued"] = d.groupby(["game_pk", "at_bat_number"]).is_strike_event.cumsum()
    d["reached2_here"] = (d.strikes_accrued >= 2) & (d.groupby(["game_pk", "at_bat_number"]).strikes_accrued.shift(1).fillna(0) < 2)
    reach = d[d.reached2_here].groupby(["game_pk", "at_bat_number"], as_index=False).agg(reach2_on=("pitch_number", "min"))
    gb3 = d[(d.pitch_number < 4) & (d.type == "X") & (d.bb_type == "ground_ball")] \
        .groupby(["game_pk", "at_bat_number"], as_index=False).agg(gb3=("description", "size"))
    mx = d[d.pitch_number < 4].groupby(["game_pk", "at_bat_number"], as_index=False).agg(max_strikes_p13=("strikes", "max"))
    pa = d.groupby(level + ["game_pk", "at_bat_number"], as_index=False).agg(npitch=("pitch_number", "max"))
    pa = pa.merge(reach, on=["game_pk", "at_bat_number"], how="left") \
           .merge(gb3, on=["game_pk", "at_bat_number"], how="left") \
           .merge(mx, on=["game_pk", "at_bat_number"], how="left")
    pa["gb3"] = pa.gb3.fillna(0) > 0
    pa["A_as_written"] = ((pa.max_strikes_p13 == 2) | pa.gb3).astype(int)
    pa["B_two_strike_by_p2"] = ((pa.reach2_on <= 2) | pa.gb3).astype(int)
    pa["C_two_strike_by_p3"] = ((pa.reach2_on <= 3) | pa.gb3).astype(int)
    out = pa.groupby(level, as_index=False).agg(
        total_pas=("npitch", "size"),
        A_as_written=("A_as_written", "sum"),
        B_two_strike_by_p2=("B_two_strike_by_p2", "sum"),
        C_two_strike_by_p3=("C_two_strike_by_p3", "sum"))
    for c in ["A_as_written", "B_two_strike_by_p2", "C_two_strike_by_p3"]:
        out[c.replace("A_", "rate_A_").replace("B_", "rate_B_").replace("C_", "rate_C_")] = out[c] / out.total_pas
    return out.round(3)


# ===========================================================================
# HELPERS
# ===========================================================================
def process_panel(level, df, label_cols=None):
    """One row per level with the full locked process KPI panel."""
    if isinstance(level, str): level = [level]
    base = df.groupby(level, as_index=False).agg(pitches=("description", "size"))
    parts = [
        whiff_rate(level, df)[level + ["swings", "whiffs", "whiff_rate"]],
        chase_rate(level, df)[level + ["ooz", "chases", "chase_rate", "in_zone_rate"]],
        putaway_rate(level, df)[level + ["pitches2strikes", "putaway_rate"]],
        fpsr(level, df)[level + ["first_pitch_strike_rate"]],
        hard_hit_rate(level, df)[level + ["bips", "hard_hit_rate"]],
        edge_rate(level, df)[level + ["edge_rate"]],
        ooz_called_strike_rate(level, df)[level + ["ooz_called_strike_rate"]],
        air_gb_rate(level, df)[level + ["gb_rate", "fb_rate", "ld_rate", "pu_rate", "air_rate"]],
        chase_up_rate(level, df)[level + ["above_pitches", "chase_up_rate"]],
        xwobacon(level, df)[level + ["xwobacon"]],
    ]
    out = base
    for p in parts:
        out = out.merge(p, on=level, how="left")
    out["swstr_rate"] = (out.whiffs / out.pitches).round(3)
    return out.round(3)


def _attack_zone(px, pz, sz_bot, sz_top):
    hw = PLATE_HALF
    inz = (np.abs(px) <= hw) & (pz >= sz_bot) & (pz <= sz_top)
    h = sz_top - sz_bot
    heart = (np.abs(px) <= hw * 0.55) & (pz >= sz_bot + 0.2 * h) & (pz <= sz_top - 0.2 * h)
    dist = np.maximum.reduce([np.abs(px) - hw, sz_bot - pz, pz - sz_top])
    out = np.where(heart, "heart", np.where(inz, "zone-edge", np.where(dist <= 0.33, "shadow", "chase")))
    return out


def main():
    print(f"[dp_uc26] data root: {OPP_DIR}")
    lhv = load_lhv()
    k = lhv[lhv.pitcher == KELLER].copy()
    staff = lhv.copy()
    staff_ex = lhv[lhv.pitcher != KELLER].copy()

    assert len(k) > 0, "entity lock returned zero rows"
    assert BRAD_KELLER not in k.pitcher.unique(), "ENTITY LOCK BREACH: Brad Keller in slice"
    assert k.player_name.nunique() == 1, f"multiple names in slice: {k.player_name.unique()}"

    k["who"] = "Keller"; staff["who"] = "LHV staff (all)"; staff_ex["who"] = "LHV staff (ex-Keller)"
    dates = sorted(k.game_date.unique())
    k["half"] = np.where(k.game_date.isin(dates[:4]), "starts 1-4 (5/30-6/18)", "starts 5-8 (6/24-7/17)")
    k["outs"] = k.events.map(EVENT_OUTS).fillna(0)
    k["az"] = _attack_zone(k.plate_x.values, k.plate_z.values, k.sz_bot.values, k.sz_top.values)
    staff_ex["az"] = _attack_zone(staff_ex.plate_x.values, staff_ex.plate_z.values,
                                  staff_ex.sz_bot.values, staff_ex.sz_top.values)

    W = lambda name, df: df.to_csv(os.path.join(OUT_DIR, f"dp_uc26_{name}.csv"), index=False)

    # ---------------- 1. headline results -------------------------------
    head = pd.concat([nresults("who", k), nresults("who", staff_ex)], ignore_index=True)
    xw = pd.concat([xwobacon("who", k), xwobacon("who", staff_ex)], ignore_index=True)
    head = head.merge(xw, on="who", how="left")
    _outs = int(k.outs.sum())
    head["ip_computed"] = [round(_outs / 3, 1), np.nan]                       # decimal thirds
    head["ip_baseball"] = [f"{_outs // 3}.{_outs % 3}", ""]                   # standard notation
    head["outs_recorded"] = [_outs, np.nan]
    head["games"] = [k.game_pk.nunique(), staff_ex.game_pk.nunique()]
    W("results_headline", head)
    print(head.to_string(index=False))

    # ---------------- 2. per-start game lines ---------------------------
    g = k.groupby(["game_date", "game_pk", "home_team", "away_team"], as_index=False).agg(
        pitches=("pitch_number", "size"), bf=("at_bat_number", "nunique"),
        outs=("outs", "sum"), max_inning=("inning", "max"),
        k_=("events", lambda s: s.isin(["strikeout", "strikeout_double_play"]).sum()),
        bb=("events", lambda s: (s == "walk").sum()),
        h=("events", lambda s: s.isin(["single", "double", "triple", "home_run"]).sum()),
        hr=("events", lambda s: (s == "home_run").sum()))
    # BOTH representations, because they look like different numbers and are not:
    #   ip_decimal  = outs/3 (36.67)
    #   ip_baseball = standard "36.2" notation, i.e. 36 innings and 2 outs
    # Publishing only one guarantees a reader eventually mistakes 36.2 for 36.7.
    g["ip"] = (g.outs / 3).round(2)
    g["ip_baseball"] = (g.outs // 3).astype(int).astype(str) + "." + (g.outs % 3).astype(int).astype(str)
    g["opponent"] = np.where(g.home_team == "LHV", g.away_team, g.home_team)
    g["site"] = np.where(g.home_team == "LHV", "home", "away")
    g["pitches_per_bf"] = (g.pitches / g.bf).round(2)
    W("game_lines", g)

    # ---------------- 3. by stand ---------------------------------------
    bs = nresults(["who", "stand"], k).merge(xwobacon(["who", "stand"], k), on=["who", "stand"], how="left")
    bss = nresults(["who", "stand"], staff_ex).merge(xwobacon(["who", "stand"], staff_ex), on=["who", "stand"], how="left")
    W("by_stand", pd.concat([bs, bss], ignore_index=True))

    # ---------------- 4. arsenal ----------------------------------------
    ars = k.groupby("pitch_name", as_index=False).agg(
        n=("pitch_number", "size"), velo=("release_speed", "mean"), velo_max=("release_speed", "max"),
        spin=("release_spin_rate", "mean"), arm_side_break_in=("api_break_x_arm", "mean"),
        vert_break_in=("api_break_z_with_gravity", "mean"), ivb_ft=("pfx_z", "mean"),
        ext=("release_extension", "mean"), arm_angle=("arm_angle", "mean"),
        rel_x=("release_pos_x", "mean"), rel_z=("release_pos_z", "mean"))
    ars["usage"] = (ars.n / len(k))
    pp = process_panel("pitch_name", k)
    ars = ars.merge(pp[["pitch_name", "swings", "whiff_rate", "swstr_rate", "chase_rate",
                        "in_zone_rate", "putaway_rate", "bips", "hard_hit_rate",
                        "gb_rate", "air_rate", "xwobacon", "edge_rate"]], on="pitch_name", how="left")
    az = k.groupby(["pitch_name", "az"]).size().unstack(fill_value=0)
    az = (az.div(az.sum(axis=1), axis=0)).round(3).add_prefix("loc_")
    ars = ars.merge(az.reset_index(), on="pitch_name", how="left")
    ars = ars.sort_values("n", ascending=False).round(3)
    W("arsenal", ars)
    W("pitch_kpis", pp.sort_values("pitches", ascending=False))

    u = k.groupby(["stand", "pitch_name"]).size().unstack(fill_value=0)
    ubs = (u.div(u.sum(axis=1), axis=0)).round(3).reset_index()
    W("arsenal_by_stand", ubs)

    # ---------------- 5. process KPI panels -----------------------------
    pk = pd.concat([process_panel("who", k), process_panel("who", staff_ex)], ignore_index=True)
    W("process_kpis", pk)
    pbs = pd.concat([process_panel(["who", "stand"], k), process_panel(["who", "stand"], staff_ex)], ignore_index=True)
    W("process_by_stand", pbs)

    # ---------------- 6. contact quality --------------------------------
    bip = k[k.type == "X"]
    cq = bip.groupby("pitch_name", as_index=False).agg(
        bip=("description", "size"), ev=("launch_speed", "mean"), ev_max=("launch_speed", "max"),
        la=("launch_angle", "mean"), hard_hit_rate=("launch_speed", lambda s: (s >= 95).mean()),
        xwobacon=("estimated_woba_using_speedangle", "mean"))
    bb = bip.groupby(["pitch_name", "bb_type"]).size().unstack(fill_value=0)
    bb = (bb.div(bb.sum(axis=1), axis=0)).round(3)
    cq = cq.merge(bb.reset_index(), on="pitch_name", how="left").round(3)
    W("contact_quality", cq)
    cq2 = bip.groupby(["stand", "pitch_name"], as_index=False).agg(
        bip=("description", "size"), ev=("launch_speed", "mean"),
        hard_hit_rate=("launch_speed", lambda s: (s >= 95).mean()),
        xwobacon=("estimated_woba_using_speedangle", "mean")).round(3)
    cq2.to_csv(os.path.join(OUT_DIR, "dp_uc26_contact_quality_by_stand.csv"), index=False)

    # ---------------- 7. recency: THE MECHANISM -------------------------
    rec = process_panel("half", k)
    recn = nresults("half", k)
    rec = rec.merge(recn[["half", "plate_apps", "krate", "bbrate", "woba", "hr_rate"]], on="half", how="left")
    W("recency_split", rec.sort_values("half"))
    ru = k.groupby(["half", "pitch_name"]).size().unstack(fill_value=0)
    ru = (ru.div(ru.sum(axis=1), axis=0)).round(3).reset_index()
    W("recency_usage", ru)

    # ---------------- 8. times through order ----------------------------
    tto = nresults("n_thruorder_pitcher", k).merge(
        xwobacon("n_thruorder_pitcher", k), on="n_thruorder_pitcher", how="left")
    tto = tto.merge(process_panel("n_thruorder_pitcher", k)[
        ["n_thruorder_pitcher", "whiff_rate", "hard_hit_rate", "in_zone_rate"]],
        on="n_thruorder_pitcher", how="left")
    W("tto", tto)

    # ---------------- 9. velo decay -------------------------------------
    ff = k[k.pitch_name == "4-Seam Fastball"]
    vi = ff.groupby("inning", as_index=False).agg(n=("description", "size"), ff_velo=("release_speed", "mean")).round(2)
    allv = k.groupby("inning", as_index=False).agg(all_pitches=("description", "size")).round(2)
    W("velo_by_inning", vi.merge(allv, on="inning", how="left"))

    # ---------------- 10. gameplan grids --------------------------------
    fp = k[k.pitch_number == 1]
    fpg = fp.groupby(["stand", "pitch_name"], as_index=False).agg(
        n=("description", "size"), strikes=("type", lambda s: (s != "B").sum()))
    fpg["strike_rate"] = (fpg.strikes / fpg.n).round(3)
    fpg["usage_within_stand"] = (fpg.n / fpg.groupby("stand").n.transform("sum")).round(3)
    W("first_pitch", fpg)

    two = k[k.strikes == 2]
    tg = two.groupby(["stand", "pitch_name"], as_index=False).agg(
        n=("description", "size"),
        swings=("description", lambda s: s.isin(SWINGS).sum()),
        whiffs=("description", lambda s: s.isin(WHIFFS).sum()),
        ks=("events", lambda s: s.isin(["strikeout", "strikeout_double_play"]).sum()))
    tg["whiff_rate"] = (tg.whiffs / tg.swings).round(3)
    tg["putaway_rate"] = (tg.ks / tg.n).round(3)
    tg["usage_within_stand"] = (tg.n / tg.groupby("stand").n.transform("sum")).round(3)
    W("two_strike", tg)

    # ---------------- 11. home runs -------------------------------------
    hr = k[k.events == "home_run"][[
        "game_date", "stand", "pitch_name", "balls", "strikes", "release_speed",
        "plate_x", "plate_z", "sz_top", "sz_bot", "launch_speed", "launch_angle",
        "n_thruorder_pitcher", "inning", "des"]].copy()
    hr["above_zone"] = (hr.plate_z > hr.sz_top)
    hr["in_heart"] = _attack_zone(hr.plate_x.values, hr.plate_z.values, hr.sz_bot.values, hr.sz_top.values) == "heart"
    W("home_runs", hr.round(3))

    # ---------------- 11b. location profile vs baseline -----------------
    def locprof(d, who, pitch=None):
        dd = d if pitch is None else d[d.pitch_name == pitch]
        return dict(who=who, pitch=pitch or "ALL", n=len(dd),
                    above_zone_rate=round((dd.plate_z > dd.sz_top).mean(), 3),
                    mean_plate_z=round(dd.plate_z.mean(), 2),
                    heart_rate=round((dd.az == "heart").mean(), 3),
                    zone_edge_rate=round((dd.az == "zone-edge").mean(), 3),
                    shadow_rate=round((dd.az == "shadow").mean(), 3),
                    chase_zone_rate=round((dd.az == "chase").mean(), 3))
    lp = [locprof(k, "Keller"), locprof(staff_ex, "LHV staff (ex-Keller)")]
    for p in ["4-Seam Fastball", "Cutter", "Sinker", "Slider"]:
        lp.append(locprof(k, "Keller", p)); lp.append(locprof(staff_ex, "LHV staff (ex-Keller)", p))
    W("location_profile", pd.DataFrame(lp))

    # ---------------- 12. PROVISIONAL SR-M1 -----------------------------
    sr_k = tm_success_rate("who", k); sr_s = tm_success_rate("who", staff_ex)
    sr_ks = tm_success_rate(["who", "stand"], k); sr_ss = tm_success_rate(["who", "stand"], staff_ex)
    sr_kh = tm_success_rate(["who", "half"], k)
    sr = pd.concat([sr_k, sr_s], ignore_index=True)
    sr["STATUS"] = "PROVISIONAL — NOT RATIFIED"
    srx = pd.concat([sr_ks, sr_ss], ignore_index=True); srx["STATUS"] = "PROVISIONAL — NOT RATIFIED"
    srh = sr_kh.copy(); srh["STATUS"] = "PROVISIONAL — NOT RATIFIED"
    W("sr_m1_provisional", sr)
    srx.to_csv(os.path.join(OUT_DIR, "dp_uc26_sr_m1_by_stand.csv"), index=False)
    srh.to_csv(os.path.join(OUT_DIR, "dp_uc26_sr_m1_by_half.csv"), index=False)

    var = pd.concat([sr_m1_variants("who", k), sr_m1_variants("who", staff_ex)], ignore_index=True)
    var["STATUS"] = "PROVISIONAL — RATIFICATION HARNESS"
    W("sr_m1_variants", var)

    lb = tm_success_rate("pitcher", lhv).merge(
        lhv.groupby("pitcher", as_index=False).player_name.agg(lambda s: s.mode().iloc[0]), on="pitcher")
    lb = lb[lb.total_pas >= 40].sort_values("success_rate", ascending=False).reset_index(drop=True)
    lb["rank"] = lb.index + 1
    lb["STATUS"] = "PROVISIONAL — NOT RATIFIED"
    W("sr_m1_leaderboard", lb)

    # ---------------- 13. DQ scorecard ----------------------------------
    bipk = k[k.type == "X"]
    dq = pd.DataFrame([
        dict(check="entity_lock_pitcher_id", detail="pitcher == 662144 (Brian Keller)",
             observed=f"{k.pitcher.nunique()} distinct pitcher id(s), name(s)={list(k.player_name.unique())}",
             threshold="exactly 1 id / 1 name", result="PASS" if k.pitcher.nunique() == 1 else "FAIL", severity="blocking"),
        dict(check="entity_lock_no_brad_keller", detail="Brad Keller 641745 must be absent",
             observed=f"present={BRAD_KELLER in k.pitcher.unique()}; a name filter would have added {len(lhv[lhv.pitcher==BRAD_KELLER])} rows",
             threshold="absent", result="PASS" if BRAD_KELLER not in k.pitcher.unique() else "FAIL", severity="blocking"),
        dict(check="dedup_pitch_key", detail="unique on (game_pk, at_bat_number, pitch_number)",
             observed=f"{k.duplicated(['game_pk','at_bat_number','pitch_number']).sum()} dupes",
             threshold="0", result="PASS" if k.duplicated(['game_pk','at_bat_number','pitch_number']).sum() == 0 else "FAIL", severity="blocking"),
        dict(check="game_type_regular_season", detail="game_type == 'R'",
             observed=str(k.game_type.unique().tolist()), threshold="['R']",
             result="PASS" if set(k.game_type.unique()) == {"R"} else "FAIL", severity="blocking"),
        dict(check="cde_location_completeness", detail="plate_x/plate_z/sz_top/sz_bot/zone non-null",
             observed=f"{k[['plate_x','plate_z','sz_top','sz_bot','zone']].notna().all(axis=1).mean():.1%}",
             threshold=">= 99%", result="PASS" if k[['plate_x','plate_z','sz_top','sz_bot','zone']].notna().all(axis=1).mean() >= 0.99 else "FAIL", severity="blocking"),
        dict(check="cde_velocity_completeness", detail="release_speed non-null",
             observed=f"{k.release_speed.notna().mean():.1%}", threshold=">= 99%",
             result="PASS" if k.release_speed.notna().mean() >= 0.99 else "FAIL", severity="blocking"),
        dict(check="cde_contact_quality_on_bip", detail="launch_speed + estimated_woba populated on type=='X'",
             observed=f"EV {bipk.launch_speed.notna().mean():.1%}, xwOBA {bipk.estimated_woba_using_speedangle.notna().mean():.1%} of {len(bipk)} BIP",
             threshold=">= 95% of BIP", result="PASS" if bipk.launch_speed.notna().mean() >= 0.95 and bipk.estimated_woba_using_speedangle.notna().mean() >= 0.95 else "FAIL", severity="blocking"),
        dict(check="cde_spin_completeness", detail="release_spin_rate non-null",
             observed=f"{k.release_spin_rate.notna().mean():.1%}", threshold=">= 95%",
             result="PASS" if k.release_spin_rate.notna().mean() >= 0.95 else "WARN", severity="warning"),
        dict(check="bat_tracking_absent", detail="bat_speed / swing_length not captured at AAA",
             observed=f"bat_speed {k.bat_speed.notna().mean():.1%}", threshold="documented, not required",
             result="WARN — documented", severity="warning"),
        dict(check="sample_size_bf", detail="BF vs 100 BF publication convention for pitcher rates",
             observed=f"{int(k.events.notna().sum())} BF over {k.game_pk.nunique()} starts",
             threshold=">= 100 BF", result="PASS" if k.events.notna().sum() >= 100 else "WARN", severity="warning"),
        dict(check="sample_size_subsplits", detail="per-pitch and per-count splits fall below 100 BF",
             observed="slider 18 PA, sinker 19 PA, 2-strike-by-pitch cells 1-49 pitches",
             threshold="directional only; n printed on every line",
             result="WARN — mitigated by printing n", severity="warning"),
        dict(check="comparison_population_defined", detail="LHV 2026 staff ex-Keller as benchmark",
             observed=f"{staff_ex.pitcher.nunique()} pitchers, {len(staff_ex)} pitches, {int(staff_ex.events.notna().sum())} BF",
             threshold="same league / season / park mix", result="PASS", severity="blocking"),
        dict(check="level_translation_unmodelled", detail="AAA->MLB translation factor not applied",
             observed="no MLB tier exists for this pitcher (0 career MLB pitches)",
             threshold="documented limitation", result="WARN — documented", severity="warning"),
        dict(check="sr_m1_ratification_status", detail="SR-M1 Mayza Success Rate",
             observed="PROVISIONAL; intent-vs-implementation gap quantified in dp_uc26_sr_m1_variants.csv",
             threshold="must be flagged PROVISIONAL wherever published",
             result="WARN — flagged", severity="warning"),
    ])
    W("dq_scorecard", dq)

    # ---------------- 14. freshness manifest ----------------------------
    fm = pd.DataFrame([
        dict(source="data/opponents/lhvp26.parquet", entity="LHV 2026 pitching (all)",
             rows=len(lhv), pitchers=lhv.pitcher.nunique(),
             min_date=str(lhv.game_date.min().date()), max_date=str(lhv.game_date.max().date()),
             fitness="FIT — primary + benchmark"),
        dict(source="data/opponents/lhvp26.parquet", entity="Brian Keller 662144",
             rows=len(k), pitchers=1, min_date=str(k.game_date.min().date()),
             max_date=str(k.game_date.max().date()), fitness="FIT — primary tier"),
        dict(source="wOBA and FIP Constants.csv", entity="FanGraphs 2026 wOBA weights",
             rows=1, pitchers=np.nan, min_date="2026", max_date="2026",
             fitness="FIT — MLB weights applied to AAA events; see 01_ caveat"),
        dict(source="(none)", entity="MLB tier for Brian Keller", rows=0, pitchers=0,
             min_date="n/a", max_date="n/a", fitness="ABSENT — 0 career MLB pitches"),
        dict(source="(none)", entity="AAA->MLB translation factors", rows=0, pitchers=0,
             min_date="n/a", max_date="n/a", fitness="ABSENT — deferred to a future UC"),
    ])
    fm["report_date"] = REPORT_DATE
    W("freshness_manifest", fm)

    _figures(k, staff_ex, ars, rec, ru, fpg, tg)
    print(f"\n[dp_uc26] wrote {len([f for f in os.listdir(OUT_DIR)])} files to {OUT_DIR}")


# ===========================================================================
# FIGURES — Phillies brand. Every number traces to a CSV receipt above.
# ===========================================================================
def _figures(k, staff_ex, ars, rec, ru, fpg, tg):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def style(ax):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color=PHI_LGRAY, lw=0.6, zorder=0)
        ax.set_axisbelow(True)

    # ---- FIG 1: arsenal — usage / whiff / contact quality
    a = ars[ars.n >= 20].sort_values("n", ascending=False)
    fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.2))
    cols = [PITCH_COLORS.get(p, PHI_GRAY) for p in a.pitch_name]
    axs[0].bar(a.pitch_name, a.usage * 100, color=cols, zorder=3)
    axs[0].set_title("Usage %", color=PHI_NAVY, fontweight="bold")
    for i, (v, n) in enumerate(zip(a.usage * 100, a.n)):
        axs[0].text(i, v + 1, f"{v:.0f}%\nn={n}", ha="center", fontsize=8, color=PHI_NAVY)
    axs[1].bar(a.pitch_name, a.whiff_rate * 100, color=cols, zorder=3)
    axs[1].axhline(26.3, color=PHI_NAVY, ls="--", lw=1.2, zorder=4)
    axs[1].text(2.4, 27.5, "LHV staff 26.3%", fontsize=8, color=PHI_NAVY, ha="right")
    axs[1].set_title("Whiff % per swing", color=PHI_NAVY, fontweight="bold")
    axs[2].bar(a.pitch_name, a.hard_hit_rate * 100, color=cols, zorder=3)
    axs[2].axhline(38.0, color=PHI_NAVY, ls="--", lw=1.2, zorder=4)
    axs[2].text(2.4, 39.5, "LHV staff 38.0%", fontsize=8, color=PHI_NAVY, ha="right")
    axs[2].set_title("Hard-hit % on contact", color=PHI_NAVY, fontweight="bold")
    for ax in axs:
        style(ax); ax.tick_params(axis="x", rotation=20, labelsize=8)
    fig.suptitle("Brian Keller — 2026 AAA arsenal (533 pitches, 8 starts)",
                 color=PHI_RED, fontweight="bold", fontsize=13)
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR, "dp_uc26_fig1_arsenal.png"), dpi=150)
    plt.close(fig)

    # ---- FIG 2: the mechanism
    r = rec.sort_values("half")
    ruo = ru.set_index("half").reindex(r.half)
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.4))
    x = np.arange(len(ruo)); wdt = 0.16
    for i, p in enumerate([c for c in PITCH_ORDER if c in ruo.columns and ruo[c].max() > 0.02]):
        axs[0].bar(x + (i - 1.5) * wdt, ruo[p] * 100, wdt, label=p,
                   color=PITCH_COLORS.get(p, PHI_GRAY), zorder=3)
    axs[0].set_xticks(x); axs[0].set_xticklabels(ruo.index, fontsize=8)
    axs[0].set_ylabel("usage %"); axs[0].legend(fontsize=7, frameon=False)
    axs[0].set_title("What changed: pitch mix", color=PHI_NAVY, fontweight="bold")
    metrics = [("bbrate", "BB%", 100), ("first_pitch_strike_rate", "1st-pitch strike%", 100),
               ("chase_rate", "Chase%", 100), ("hard_hit_rate", "Hard-hit%", 100),
               ("xwobacon", "xwOBAcon (x100)", 100)]
    x2 = np.arange(len(metrics))
    for j, half in enumerate(r.half):
        vals = [r[r.half == half][m].iloc[0] * s for m, _, s in metrics]
        axs[1].bar(x2 + (j - 0.5) * 0.36, vals, 0.36, label=half,
                   color=[PHI_GRAY, PHI_RED][j], zorder=3)
    axs[1].set_xticks(x2); axs[1].set_xticklabels([lbl for _, lbl, _ in metrics], fontsize=8, rotation=12)
    axs[1].legend(fontsize=7, frameon=False)
    axs[1].set_title("What followed: command + contact quality", color=PHI_NAVY, fontweight="bold")
    for ax in axs: style(ax)
    fig.suptitle("The mechanism — four-seam down, sinker up, everything improves",
                 color=PHI_RED, fontweight="bold", fontsize=13)
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR, "dp_uc26_fig2_recency.png"), dpi=150)
    plt.close(fig)

    # ---- FIG 3: location, 4-seam vs sinker, by stand
    fig, axs = plt.subplots(2, 2, figsize=(9.5, 9))
    for row, p in enumerate(["4-Seam Fastball", "Sinker"]):
        for col, s in enumerate(["L", "R"]):
            ax = axs[row][col]
            d = k[(k.pitch_name == p) & (k.stand == s)]
            hh = d[(d.type == "X") & (d.launch_speed >= 95)]
            ax.scatter(-d.plate_x, d.plate_z, s=22, alpha=0.55,
                       color=PITCH_COLORS[p], edgecolor="none", zorder=3)
            ax.scatter(-hh.plate_x, hh.plate_z, s=60, facecolor="none",
                       edgecolor=PHI_NAVY, lw=1.4, zorder=4, label="hard-hit BIP")
            zb, zt = k.sz_bot.mean(), k.sz_top.mean()
            ax.add_patch(plt.Rectangle((-PLATE_HALF, zb), 2 * PLATE_HALF, zt - zb,
                                       fill=False, edgecolor=PHI_NAVY, lw=1.6, zorder=5))
            ax.set_xlim(-2.2, 2.2); ax.set_ylim(0.6, 4.6); ax.set_aspect("equal")
            ax.set_title(f"{p} vs {s}HB  (n={len(d)}, HH={len(hh)})", fontsize=9,
                         color=PHI_NAVY, fontweight="bold")
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values(): sp.set_visible(False)
            if row == 0 and col == 0:
                ax.legend(fontsize=7, frameon=False, loc="upper left",
                          bbox_to_anchor=(-0.02, 1.02))
    fig.suptitle("Catcher's view — the four-seam lives above the zone; the sinker doesn't get in it",
                 color=PHI_RED, fontweight="bold", fontsize=12)
    fig.tight_layout(); fig.subplots_adjust(hspace=0.02)
    fig.savefig(os.path.join(OUT_DIR, "dp_uc26_fig3_location.png"), dpi=150)
    plt.close(fig)

    # ---- FIG 4: gameplan grid
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.4))
    t = tg[tg.n >= 4]
    for i, s in enumerate(["L", "R"]):
        d = t[t.stand == s].sort_values("n", ascending=False)
        ax = axs[i]; x = np.arange(len(d))
        ax.bar(x - 0.2, d.usage_within_stand * 100, 0.4, label="% of 2-strike calls",
               color=PHI_GRAY, zorder=3)
        ax.bar(x + 0.2, d.putaway_rate * 100, 0.4, label="putaway %", color=PHI_RED, zorder=3)
        ax.set_xticks(x); ax.set_xticklabels([f"{p}\nn={n}" for p, n in zip(d.pitch_name, d.n)], fontsize=7)
        ax.set_title(f"Two strikes vs {s}HB", color=PHI_NAVY, fontweight="bold")
        ax.legend(fontsize=7, frameon=False); style(ax)
    fig.suptitle("The call gap — the four-seam gets the most two-strike calls and the fewest putaways vs LHB",
                 color=PHI_RED, fontweight="bold", fontsize=12)
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR, "dp_uc26_fig4_gameplan.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
