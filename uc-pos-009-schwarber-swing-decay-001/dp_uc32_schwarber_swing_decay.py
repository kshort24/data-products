"""
dp_uc32 — Kyle Schwarber Swing Decay (uc-pos-009-schwarber-swing-decay-001)
===========================================================================

Build script for UC #33. Produces every number that appears in the reader
report, the PDF and the interactive dashboard. Nothing is published that this
script did not compute.

Governance
----------
* Entity lock is an MLBAM id (`batter == 656941`), never a name filter.
* Locked KPI kernel inherited VERBATIM from `Baseball Functions.ipynb`
  (get_stats / nresults / whiff_rate / chase_rate / barrel_rate /
  hard_hit_rate / ev90 / inds). New KPIs are the SW-1..SW-9 family, each
  specified in 04_architecture_and_kpi_specs.md before appearing here.
* **Bat-tracking NULL policy (DPO decision, 2026-08-08): NO IMPUTATION.**
  Bat-tracking KPIs are computed only on rows where the sensor recorded a
  value. Seasons outside the sensor window render as "not measured", never as
  a number. Coverage is published beside every bat-tracking figure (SW-7).
  The cost of the alternative is quantified in receipt `x1_imputation_harm`.
* Every table written to out/ as a CSV receipt. Figures trace to receipts.

Usage
-----
    python dp_uc32_schwarber_swing_decay.py

Data root resolution order: $DP_MLB_ROOT -> relative -> Windows abs -> mount.
"""

from __future__ import annotations

import os
import sys
import glob
import json
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 80)

# ---------------------------------------------------------------------------
# 0. Environment
# ---------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

_CANDIDATES = [
    os.environ.get("DP_MLB_ROOT"),
    os.path.join(HERE, "..", "..", "..", "Python Scripts", "MLB"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB",
    "/sessions/admiring-inspiring-galileo/mnt/MLB",
]


def _resolve_root() -> str:
    for c in _CANDIDATES:
        if c and os.path.isdir(os.path.join(c, "data", "phillies")):
            return os.path.abspath(c)
    raise RuntimeError(
        "Could not locate the MLB data root. Set $DP_MLB_ROOT to the folder "
        "containing data/phillies/*.parquet."
    )


ROOT = _resolve_root()
print(f"[dp_uc32] data root: {ROOT}")

SCHWARBER = 656941          # MLBAM id — the entity lock
PITCH_KEY = ["game_pk", "at_bat_number", "pitch_number"]

# Phillies brand
PHI_RED, PHI_NAVY, PHI_LIGHT = "#E81828", "#002D72", "#7A99C2"

RECEIPTS: dict[str, str] = {}


def receipt(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Write a CSV receipt. Every published number must pass through here."""
    path = os.path.join(OUT, f"dp_uc32_{name}.csv")
    df.to_csv(path, index=False)
    RECEIPTS[name] = path
    print(f"  receipt  {name:<34} {len(df):>5} rows")
    return df


# ---------------------------------------------------------------------------
# 1. Locked KPI kernel — inherited verbatim, do not re-derive
# ---------------------------------------------------------------------------

SWINGS = [
    "foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
    "swinging_pitchout", "swinging_strike", "swinging_strike_blocked",
]
WHIFFS = [
    "foul_tip", "missed_bunt", "swinging_pitchout",
    "swinging_strike", "swinging_strike_blocked",
]
HITS = ["single", "double", "triple", "home_run"]


def whiff_rate(level, df):
    u = df[df.description.isin(SWINGS)].groupby(level, as_index=False).agg(swings=("des", "size"))
    v = df[df.description.isin(WHIFFS)].groupby(level, as_index=False).agg(whiffs=("des", "size"))
    w = u.merge(v, on=level, how="left")
    w["whiffs"] = w.whiffs.fillna(0).astype(int)
    w["whiff_rate"] = w.whiffs / w.swings
    return w


def chase_rate(level, df):
    chase = df[(df.zone > 9) & (df.description.isin(SWINGS))]
    i = chase.groupby(level, as_index=False).agg(chases=("des", "size"))
    j = df[df.zone > 9].groupby(level, as_index=False).agg(ooz=("des", "size"))
    cr = (i.merge(j, on=level, how="right")
            .merge(df.groupby(level, as_index=False).agg(pitches=("des", "size")),
                   on=level, how="right"))
    cr["chases"] = cr.chases.fillna(0)
    cr["chase_rate"] = cr.chases / cr.ooz
    cr["in_zone_rate"] = (cr.pitches - cr.ooz) / cr.pitches
    return cr.round(3)


def barrel_rate(level, df):
    if isinstance(level, str):
        level = [level]
    bip_pop = df[df.type == "X"]
    bips = bip_pop.groupby(level, as_index=False).agg(bips=("des", "size"))
    barrels = (bip_pop[bip_pop.launch_speed_angle == 6]
               .groupby(level, as_index=False).agg(barrels=("des", "size")))
    out = bips.merge(barrels, on=level, how="left")
    out["barrels"] = out.barrels.fillna(0).astype(int)
    out["barrel_rate"] = np.where(out.bips > 0, (out.barrels / out.bips).round(3), 0)
    return out


def hard_hit_rate(level, df):
    bip = df[df.type == "X"]
    hh = (bip[bip.launch_speed >= 95].groupby(level, as_index=False).agg(hard_hits=("des", "size"))
          .merge(bip.groupby(level, as_index=False).agg(bips=("des", "size")),
                 on=level, how="right"))
    hh["hard_hits"] = hh.hard_hits.fillna(0)
    hh["hard_hit_rate"] = hh.hard_hits / hh.bips
    return hh


def ev90(level, df):
    bip = df[df.type == "X"]
    return bip.groupby(level, as_index=False).agg(ev90=("launch_speed", lambda x: x.quantile(0.90)))


def inds(level, df):
    return df.groupby(level, as_index=False).agg(
        counter=("des", "size"),
        pitch_speed_mu=("release_speed", "mean"),
        ev_mu=("launch_speed", "mean"),
        ev_std=("launch_speed", "std"),
        la_mu=("launch_angle", "mean"),
        dist_mu=("hit_distance_sc", "mean"),
    ).round(2)


def _results_core(level, df):
    """Slim re-implementation of the counting kernel used by nresults().

    Uses the identical event classification as the locked `get_stats`. Kept
    local so the build has no notebook dependency; verified row-for-row against
    the locked function in dp_uc32_verification.py (check V-02).
    """
    if isinstance(level, str):
        level = [level]
    ev = df.events.replace(np.nan, "NA")
    g = df.groupby(level, as_index=False)
    out = g.agg(pitches=("des", "size"))

    def _cnt(mask, col):
        s = df[mask].groupby(level, as_index=False).agg(**{col: ("des", "size")})
        return s

    out = out.merge(_cnt(~ev.isin(["NA", "pickoff_1b"]), "plate_apps"), on=level, how="left")
    out = out.merge(_cnt(~ev.isin(["NA", "pickoff_1b", "walk", "intent_walk", "hit_by_pitch",
                                   "sac_fly", "sac_bunt"]), "at_bats"), on=level, how="left")
    out = out.merge(_cnt(df.type == "X", "bip"), on=level, how="left")
    out = out.merge(_cnt(df.events.isin(HITS), "hits"), on=level, how="left")
    out = out.merge(_cnt(df.events == "double", "doubles"), on=level, how="left")
    out = out.merge(_cnt(df.events == "triple", "triples"), on=level, how="left")
    out = out.merge(_cnt(df.events == "home_run", "hrs"), on=level, how="left")
    out = out.merge(_cnt(df.events.isin(["walk", "intent_walk"]), "walks"), on=level, how="left")
    out = out.merge(_cnt(df.events.isin(["strikeout", "strikeout_double_play"]), "strikeouts"),
                    on=level, how="left")
    out = out.merge(_cnt(df.events == "hit_by_pitch", "hbp"), on=level, how="left")
    out = out.merge(_cnt(df.events.isin(["sac_fly", "sac_fly_double_play"]), "sf"), on=level, how="left")
    for c in ["plate_apps", "at_bats", "bip", "hits", "doubles", "triples", "hrs",
              "walks", "strikeouts", "hbp", "sf"]:
        out[c] = out[c].fillna(0).astype(int)
    out["singles"] = out.hits - out.doubles - out.triples - out.hrs
    out["ba"] = (out.hits / out.at_bats).round(3)
    out["obp"] = ((out.hits + out.walks + out.hbp) /
                  (out.at_bats + out.walks + out.hbp + out.sf)).round(3)
    out["slg"] = ((out.singles + 2 * out.doubles + 3 * out.triples + 4 * out.hrs)
                  / out.at_bats).round(3)
    out["ops"] = (out.obp + out.slg).round(3)
    out["iso"] = (out.slg - out.ba).round(3)
    out["krate"] = (out.strikeouts / out.plate_apps).round(3)
    out["bbrate"] = (out.walks / out.plate_apps).round(3)
    out["hr_rate"] = (out.hrs / out.plate_apps).round(3)
    # xwOBA on contact (Statcast native), honest denominator published alongside
    bipd = df[df.type == "X"]
    xw = bipd.groupby(level, as_index=False).agg(
        xwobacon=("estimated_woba_using_speedangle", "mean"),
        xwobacon_n=("estimated_woba_using_speedangle", "count"),
        xslgcon=("estimated_slg_using_speedangle", "mean"),
    )
    out = out.merge(xw, on=level, how="left")
    out["xwobacon"] = out.xwobacon.round(3)
    out["xslgcon"] = out.xslgcon.round(3)
    return out


# ---------------------------------------------------------------------------
# 2. New KPI family — SW-1 .. SW-9 (specs in 04_)
# ---------------------------------------------------------------------------

SS_LO, SS_HI = 8, 32           # Statcast sweet-spot launch-angle band
HARD_EV = 95                   # Statcast hard-hit threshold
FAST_SWING = 75                # Statcast fast-swing threshold (mph)
AA_LO, AA_HI = 5, 20           # attack-angle fit window
SQ_UP = 0.80                   # squared-up threshold


def plate_speed_mph(df: pd.DataFrame) -> pd.Series:
    """SW-4 support: pitch speed at the front edge of home plate (y = 17/12 ft).

    Exact kinematics from the Statcast 9P trajectory fit — not an approximation.
    Statcast's published squared-up formula is calibrated on *plate* speed, so
    using release_speed here would bias max-EV high by ~8-9 mph and depress the
    squared-up rate. Validated in check V-11 (expect ~8-10 mph below release).
    """
    y0, y_target = 50.0, 17.0 / 12.0
    vy0, ay = df.vy0.astype(float), df.ay.astype(float)
    disc = vy0 ** 2 - 2 * ay * (y0 - y_target)
    disc = disc.clip(lower=0)
    t = (-vy0 - np.sqrt(disc)) / ay
    vx = df.vx0.astype(float) + df.ax.astype(float) * t
    vy = vy0 + ay * t
    vz = df.vz0.astype(float) + df.az.astype(float) * t
    return np.sqrt(vx ** 2 + vy ** 2 + vz ** 2) * 0.681818


# Statcast parquet uses pandas nullable extension dtypes (Int64/Float64) for
# several trajectory and bat-tracking columns. pd.NA short-circuits boolean
# comparison, so coerce to numpy float once, up front, before any masking.
_NUMERIC = [
    "launch_speed", "launch_angle", "launch_speed_angle", "hit_distance_sc",
    "bat_speed", "swing_length", "attack_angle", "attack_direction",
    "swing_path_tilt", "intercept_ball_minus_batter_pos_x_inches",
    "intercept_ball_minus_batter_pos_y_inches", "release_speed", "effective_speed",
    "vx0", "vy0", "vz0", "ax", "ay", "az", "zone", "balls", "strikes",
    "estimated_woba_using_speedangle", "estimated_ba_using_speedangle",
    "estimated_slg_using_speedangle", "hc_x", "hc_y", "plate_x", "plate_z",
]


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    for c in _NUMERIC:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce").astype("float64")
    return d


def add_swing_features(df: pd.DataFrame) -> pd.DataFrame:
    d = coerce_numeric(df)
    d["is_swing"] = d.description.isin(SWINGS)
    d["is_whiff"] = d.description.isin(WHIFFS)
    d["is_bip"] = d.type == "X"

    # SW-1 sweet spot / SW-2 ideal contact
    d["ss_flag"] = np.where(d.is_bip & d.launch_angle.between(SS_LO, SS_HI), 1,
                            np.where(d.is_bip, 0, np.nan))
    d["ideal_flag"] = np.where(
        d.is_bip & d.launch_angle.between(SS_LO, SS_HI) & (d.launch_speed >= HARD_EV), 1,
        np.where(d.is_bip, 0, np.nan))

    # SW-3 fast swing (measured swings only — NO imputation)
    meas = d.is_swing & d.bat_speed.notna()
    d["bt_measured"] = meas
    d["fast_swing"] = np.where(meas, (d.bat_speed >= FAST_SWING).astype(float), np.nan)

    # SW-4 squared-up rate (measured swings that ended in a ball in play)
    d["plate_speed"] = np.nan
    traj = d[["vx0", "vy0", "vz0", "ax", "ay", "az"]].notna().all(axis=1)
    d.loc[traj, "plate_speed"] = plate_speed_mph(d.loc[traj])
    sq_pop = d.is_bip & d.bat_speed.notna() & d.plate_speed.notna() & d.launch_speed.notna()
    max_ev = 1.23 * d.bat_speed + 0.2306 * d.plate_speed
    d["squared_up_pct"] = np.where(sq_pop & (max_ev > 0), d.launch_speed / max_ev, np.nan)
    d["squared_up"] = np.where(d.squared_up_pct.notna(),
                               (d.squared_up_pct >= SQ_UP).astype(float), np.nan)
    # Blast = squared-up contact produced by a fast swing
    d["blast"] = np.where(d.squared_up.notna() & d.fast_swing.notna(),
                          ((d.squared_up == 1) & (d.fast_swing == 1)).astype(float), np.nan)

    # SW-5 attack-angle fit (2025+ only)
    aa = d.is_swing & d.attack_angle.notna()
    d["aa_measured"] = aa
    d["aa_fit"] = np.where(aa, d.attack_angle.between(AA_LO, AA_HI).astype(float), np.nan)

    # SW-6 contact depth (inches out front of the batter's centre of mass)
    d["contact_depth"] = np.where(d.is_bip, d.intercept_ball_minus_batter_pos_y_inches, np.nan)
    return d


def bat_tracking_block(level, d: pd.DataFrame) -> pd.DataFrame:
    """SW-3/4/5/6/7 rolled to `level`. Coverage (SW-7) ships with every row."""
    if isinstance(level, str):
        level = [level]
    sw = d[d.is_swing]
    g = sw.groupby(level, as_index=False)
    out = g.agg(
        swings=("des", "size"),
        bt_swings=("bat_speed", "count"),
        bat_speed_mu=("bat_speed", "mean"),
        bat_speed_p90=("bat_speed", lambda x: x.quantile(0.90)),
        bat_speed_sd=("bat_speed", "std"),
        swing_length_mu=("swing_length", "mean"),
        fast_swing_rate=("fast_swing", "mean"),
        aa_swings=("attack_angle", "count"),
        attack_angle_mu=("attack_angle", "mean"),
        attack_dir_mu=("attack_direction", "mean"),
        swing_path_tilt_mu=("swing_path_tilt", "mean"),
        aa_fit_rate=("aa_fit", "mean"),
    )
    out["bt_coverage"] = (out.bt_swings / out.swings).round(3)      # SW-7
    out["aa_coverage"] = (out.aa_swings / out.swings).round(3)      # SW-7
    bip = d[d.is_bip]
    gb = bip.groupby(level, as_index=False).agg(
        sq_n=("squared_up", "count"),
        squared_up_rate=("squared_up", "mean"),
        squared_up_pct_mu=("squared_up_pct", "mean"),
        blast_rate=("blast", "mean"),
        contact_depth_mu=("contact_depth", "mean"),
        contact_depth_n=("contact_depth", "count"),
    )
    out = out.merge(gb, on=level, how="left")
    # Coverage gate: suppress any rate whose denominator is zero-coverage
    for col, cov in [("bat_speed_mu", "bt_swings"), ("bat_speed_p90", "bt_swings"),
                     ("bat_speed_sd", "bt_swings"), ("swing_length_mu", "bt_swings"),
                     ("fast_swing_rate", "bt_swings"), ("attack_angle_mu", "aa_swings"),
                     ("attack_dir_mu", "aa_swings"), ("swing_path_tilt_mu", "aa_swings"),
                     ("aa_fit_rate", "aa_swings")]:
        out[col] = out[col].where(out[cov] > 0)
    return out.round(3)


def contact_block(level, d: pd.DataFrame) -> pd.DataFrame:
    """SW-1 / SW-2 plus the locked contact-quality kernel."""
    if isinstance(level, str):
        level = [level]
    bip = d[d.is_bip]
    out = bip.groupby(level, as_index=False).agg(
        bips=("des", "size"),
        ev_mu=("launch_speed", "mean"),
        ev90=("launch_speed", lambda x: x.quantile(0.90)),
        ev_max=("launch_speed", "max"),
        la_mu=("launch_angle", "mean"),
        la_sd=("launch_angle", "std"),
        dist_mu=("hit_distance_sc", "mean"),
        sweet_spot_rate=("ss_flag", "mean"),          # SW-1
        ideal_contact_rate=("ideal_flag", "mean"),    # SW-2
    )
    out = out.merge(barrel_rate(level, d)[level + ["barrels", "barrel_rate"]], on=level, how="left")
    out = out.merge(hard_hit_rate(level, d)[level + ["hard_hit_rate"]], on=level, how="left")
    return out.round(3)


# ---------------------------------------------------------------------------
# 3. Load & lock
# ---------------------------------------------------------------------------

print("\n[1] load + entity lock")

phils_files = sorted(glob.glob(os.path.join(ROOT, "data", "phillies", "phils_*.parquet")))
phils = pd.concat([pd.read_parquet(f) for f in phils_files], ignore_index=True)
pos = phils[phils.phillies_role == "batting"].copy()

nphl_sch = pd.read_parquet(os.path.join(ROOT, "data", "opponents", "schwarber.parquet"))

raw_pre = len(nphl_sch[nphl_sch.batter == SCHWARBER]) + len(pos[pos.batter == SCHWARBER])
car = pd.concat([nphl_sch[nphl_sch.batter == SCHWARBER], pos[pos.batter == SCHWARBER]],
                ignore_index=True, sort=False)
dupes_dropped = len(car) - len(car.drop_duplicates(subset=PITCH_KEY))
car = car.drop_duplicates(subset=PITCH_KEY)
nonreg = (car.game_type != "R").sum()
car = car[car.game_type == "R"].copy()
car["game_date"] = pd.to_datetime(car.game_date)
car = car.sort_values(["game_date", "game_pk", "at_bat_number", "pitch_number"]).reset_index(drop=True)
car = add_swing_features(car)

# name-filter contamination probe (the canonical failure mode)
name_only = pd.concat([
    nphl_sch[nphl_sch.player_name.astype(str).str.contains("Schwarber", na=False)],
    pos[pos.player_name.astype(str).str.contains("Schwarber", na=False)],
], ignore_index=True).drop_duplicates(subset=PITCH_KEY)
contam_ids = sorted(set(name_only.batter.dropna().unique()) - {SCHWARBER})

print(f"  entity lock batter=={SCHWARBER}: {len(car):,} regular-season pitches "
      f"({car.game_year.min()}-{car.game_year.max()})")
print(f"  dedup dropped {dupes_dropped} | non-regular-season dropped {nonreg} | "
      f"name-filter contamination ids: {contam_ids or 'none'}")

d26 = car[car.game_year == 2026].copy()
d25 = car[car.game_year == 2025].copy()

# ---------------------------------------------------------------------------
# 4. A — Career / season spine
# ---------------------------------------------------------------------------

print("\n[2] A — career season spine")

a1 = (_results_core(["game_year"], car)
      .merge(contact_block(["game_year"], car), on="game_year", how="left")
      .merge(bat_tracking_block(["game_year"], car), on="game_year", how="left")
      .merge(whiff_rate(["game_year"], car)[["game_year", "swings", "whiff_rate"]]
             .rename(columns={"swings": "swings_wr"}), on="game_year", how="left")
      .merge(chase_rate(["game_year"], car)[["game_year", "chase_rate", "in_zone_rate"]],
             on="game_year", how="left"))
iz = whiff_rate(["game_year"], car[car.zone < 10])[["game_year", "whiff_rate"]] \
    .rename(columns={"whiff_rate": "whiff_rate_iz"})
a1 = a1.merge(iz, on="game_year", how="left")
a1["team_context"] = np.where(a1.game_year <= 2021, "pre-PHI (nphl)", "PHI (pos)")
receipt("a1_career_season_spine", a1)

# A2 — bat-tracking coverage register (SW-7). This is the governance receipt.
print("\n[3] A2 — bat-tracking coverage register (SW-7)")
cov_rows = []
for y, g in car.groupby("game_year"):
    sw = g[g.is_swing]
    bip = g[g.is_bip]
    cov_rows.append({
        "game_year": int(y),
        "swings": len(sw),
        "bips": len(bip),
        "bat_speed_n": int(sw.bat_speed.notna().sum()),
        "bat_speed_coverage": round(sw.bat_speed.notna().mean(), 3) if len(sw) else np.nan,
        "swing_length_n": int(sw.swing_length.notna().sum()),
        "attack_angle_n": int(sw.attack_angle.notna().sum()),
        "attack_angle_coverage": round(sw.attack_angle.notna().mean(), 3) if len(sw) else np.nan,
        "swing_path_tilt_n": int(sw.swing_path_tilt.notna().sum()),
        "contact_depth_n": int(bip.intercept_ball_minus_batter_pos_y_inches.notna().sum()),
        "launch_angle_coverage": round(bip.launch_angle.notna().mean(), 3) if len(bip) else np.nan,
        "sensor_status": ("bat tracking + swing path" if sw.attack_angle.notna().mean() > 0.5
                          else "bat tracking only" if sw.bat_speed.notna().mean() > 0.5
                          else "not measured"),
    })
a2 = receipt("a2_bat_tracking_coverage", pd.DataFrame(cov_rows))

# X1 — imputation harm probe. Quantifies the cost of the rejected policy.
print("\n[4] X1 — imputation harm probe")
sw_all = car[car.is_swing].copy()
career_mu = sw_all.bat_speed.mean()                      # the value that would have been imputed
imp = sw_all.copy()
imp["bat_speed_imputed"] = imp.bat_speed.fillna(career_mu)
x1 = imp.groupby("game_year", as_index=False).agg(
    swings=("des", "size"),
    measured_n=("bat_speed", "count"),
    measured_mu=("bat_speed", "mean"),
    measured_sd=("bat_speed", "std"),
    imputed_mu=("bat_speed_imputed", "mean"),
    imputed_sd=("bat_speed_imputed", "std"),
)
x1["coverage"] = (x1.measured_n / x1.swings).round(3)
x1["fabricated_rows"] = x1.swings - x1.measured_n
x1["mu_error"] = (x1.imputed_mu - x1.measured_mu).round(3)
x1["sd_shrinkage"] = (x1.imputed_sd - x1.measured_sd).round(3)
x1["policy_shipped"] = np.where(x1.measured_n > 0, "measured — publish", "not measured — suppress")
x1["career_mean_used_for_imputation"] = round(career_mu, 3)
x1 = x1.round(3)
receipt("x1_imputation_harm", x1)

# Headline harm numbers for the report
harm = {
    "career_mean_bat_speed": round(career_mu, 2),
    "seasons_with_zero_coverage": int((x1.measured_n == 0).sum()),
    "swings_that_would_be_fabricated": int(x1.loc[x1.measured_n == 0, "swings"].sum()),
    "share_of_career_swings_fabricated": round(
        x1.loc[x1.measured_n == 0, "swings"].sum() / x1.swings.sum(), 3),
    "measured_sd_2026": float(x1.loc[x1.game_year == 2026, "measured_sd"].iloc[0]),
}

# ---------------------------------------------------------------------------
# 5. B — Within-2026 decay (the primary question)
# ---------------------------------------------------------------------------

print("\n[5] B — within-2026 decay")

# B1 monthly
for tag, dd in [("b1_monthly_2026", d26), ("b2_monthly_2025", d25)]:
    x = dd.copy()
    x["month"] = x.game_date.dt.month
    m = (_results_core(["month"], x)
         .merge(contact_block(["month"], x), on="month", how="left")
         .merge(bat_tracking_block(["month"], x), on="month", how="left")
         .merge(chase_rate(["month"], x)[["month", "chase_rate", "in_zone_rate"]],
                on="month", how="left")
         .merge(whiff_rate(["month"], x)[["month", "whiff_rate"]], on="month", how="left"))
    m["month_name"] = pd.to_datetime(m.month, format="%m").dt.strftime("%b")
    receipt(tag, m)

b1 = pd.read_csv(RECEIPTS["b1_monthly_2026"])

# B3 rolling windows over balls in play (order = chronological)
print("\n[6] B3 — rolling BIP windows")
bip26 = d26[d26.is_bip].reset_index(drop=True).copy()
bip26["bip_idx"] = np.arange(1, len(bip26) + 1)
W = 60
roll = pd.DataFrame({
    "bip_idx": bip26.bip_idx,
    "game_date": bip26.game_date.dt.strftime("%Y-%m-%d"),
    "window_n": bip26.bip_idx.rolling(W).count(),
    "barrel_rate": (bip26.launch_speed_angle == 6).rolling(W).mean(),
    "ideal_contact_rate": bip26.ideal_flag.rolling(W).mean(),
    "sweet_spot_rate": bip26.ss_flag.rolling(W).mean(),
    "hard_hit_rate": (bip26.launch_speed >= HARD_EV).rolling(W).mean(),
    "ev_mu": bip26.launch_speed.rolling(W).mean(),
    "ev90": bip26.launch_speed.rolling(W).quantile(0.90),
    "la_mu": bip26.launch_angle.rolling(W).mean(),
    "squared_up_rate": bip26.squared_up.rolling(W).mean(),
    "xwobacon": bip26.estimated_woba_using_speedangle.rolling(W).mean(),
}).dropna(subset=["window_n"]).round(4)
receipt("b3_rolling_bip_2026", roll)

# B4 rolling swing windows (bat tracking) — measured swings only
sw26 = d26[d26.is_swing & d26.bat_speed.notna()].reset_index(drop=True).copy()
sw26["swing_idx"] = np.arange(1, len(sw26) + 1)
WS = 150
rolls = pd.DataFrame({
    "swing_idx": sw26.swing_idx,
    "game_date": sw26.game_date.dt.strftime("%Y-%m-%d"),
    "bat_speed_mu": sw26.bat_speed.rolling(WS).mean(),
    "bat_speed_p90": sw26.bat_speed.rolling(WS).quantile(0.90),
    "fast_swing_rate": sw26.fast_swing.rolling(WS).mean(),
    "swing_length_mu": sw26.swing_length.rolling(WS).mean(),
    "attack_angle_mu": sw26.attack_angle.rolling(WS).mean(),
    "swing_path_tilt_mu": sw26.swing_path_tilt.rolling(WS).mean(),
    "aa_fit_rate": sw26.aa_fit.rolling(WS).mean(),
}).dropna(subset=["bat_speed_mu"]).round(4)
receipt("b4_rolling_swings_2026", rolls)

# B5 phase split — data-driven, not calendar-driven.
# Split at the chronological midpoint of 2026 balls in play so both phases
# carry equal BIP weight; the report states the date and the n on both sides.
mid = len(bip26) // 2
split_date = bip26.loc[mid, "game_date"]
d26 = d26.copy()
d26["phase"] = np.where(d26.game_date < split_date, "A: through " + split_date.strftime("%b %d"),
                        "B: since " + split_date.strftime("%b %d"))
b5 = (_results_core(["phase"], d26)
      .merge(contact_block(["phase"], d26), on="phase", how="left")
      .merge(bat_tracking_block(["phase"], d26), on="phase", how="left")
      .merge(chase_rate(["phase"], d26)[["phase", "chase_rate", "in_zone_rate"]],
             on="phase", how="left")
      .merge(whiff_rate(["phase"], d26)[["phase", "whiff_rate"]], on="phase", how="left"))
izp = whiff_rate(["phase"], d26[d26.zone < 10])[["phase", "whiff_rate"]] \
    .rename(columns={"whiff_rate": "whiff_rate_iz"})
b5 = b5.merge(izp, on="phase", how="left").sort_values("phase")
receipt("b5_phase_split_2026", b5)

# B6 delta table — the report's core exhibit
metrics = ["ev_mu", "ev90", "la_mu", "sweet_spot_rate", "ideal_contact_rate", "barrel_rate",
           "hard_hit_rate", "xwobacon", "squared_up_rate", "blast_rate", "bat_speed_mu",
           "bat_speed_p90", "fast_swing_rate", "swing_length_mu", "attack_angle_mu",
           "swing_path_tilt_mu", "aa_fit_rate", "contact_depth_mu", "chase_rate",
           "whiff_rate", "whiff_rate_iz", "slg", "iso", "ops"]
pa_, pb_ = b5.iloc[0], b5.iloc[1]
b6 = pd.DataFrame({
    "metric": metrics,
    "phase_a": [pa_.get(m, np.nan) for m in metrics],
    "phase_b": [pb_.get(m, np.nan) for m in metrics],
})
b6["delta"] = (b6.phase_b - b6.phase_a).round(4)
b6["pct_change"] = np.where(b6.phase_a.abs() > 1e-9,
                            (100 * b6.delta / b6.phase_a).round(1), np.nan)
b6["phase_a_label"] = pa_["phase"]
b6["phase_b_label"] = pb_["phase"]
b6["phase_a_bips"], b6["phase_b_bips"] = pa_["bips"], pb_["bips"]
b6["phase_a_pa"], b6["phase_b_pa"] = pa_["plate_apps"], pb_["plate_apps"]
receipt("b6_phase_delta", b6.round(4))

# ---------------------------------------------------------------------------
# 6. C — Diagnosis: where did the damage go?
# ---------------------------------------------------------------------------

print("\n[7] C — diagnosis")

GROUP_MAP = {"FF": "Fastballs", "SI": "Fastballs", "FC": "Fastballs",
             "CH": "Offspeed", "FS": "Offspeed", "FO": "Offspeed", "SC": "Offspeed",
             "KC": "Breaking", "CU": "Breaking", "CS": "Breaking", "SL": "Breaking",
             "ST": "Breaking", "SV": "Breaking", "KN": "Breaking"}
for frame in (car, d26, d25):
    frame["pitch_group"] = frame.pitch_type.map(GROUP_MAP).fillna("Other")

# C1 launch-angle distribution buckets — is he getting under the ball?
def la_buckets(dd, label):
    bip = dd[dd.is_bip & dd.launch_angle.notna()].copy()
    bins = [-90, -10, 8, 20, 32, 50, 90]
    names = ["Topped (<-10)", "Low drive (-10 to 8)", "Ideal low (8-20)",
             "Ideal high (20-32)", "Under (32-50)", "Pop up (>50)"]
    bip["la_bucket"] = pd.cut(bip.launch_angle, bins=bins, labels=names,
                              right=False).astype(str)
    t = bip.groupby("la_bucket", as_index=False, observed=True).agg(
        bips=("des", "size"), ev_mu=("launch_speed", "mean"),
        xwobacon=("estimated_woba_using_speedangle", "mean"),
        hard_hit=("launch_speed", lambda x: (x >= HARD_EV).mean()))
    t["share"] = (t.bips / t.bips.sum()).round(4)
    t["window"] = label
    return t.round(3)

c1 = pd.concat([la_buckets(d26[d26.phase == pa_["phase"]], pa_["phase"]),
                la_buckets(d26[d26.phase == pb_["phase"]], pb_["phase"]),
                la_buckets(d25, "2025 full season")], ignore_index=True)
receipt("c1_la_distribution", c1)

# C2 pitch group x phase
c2 = (_results_core(["phase", "pitch_group"], d26)
      .merge(contact_block(["phase", "pitch_group"], d26), on=["phase", "pitch_group"], how="left")
      .merge(whiff_rate(["phase", "pitch_group"], d26)[["phase", "pitch_group", "whiff_rate"]],
             on=["phase", "pitch_group"], how="left"))
receipt("c2_pitch_group_phase", c2)

# C3 handedness x phase
c3 = (_results_core(["phase", "p_throws"], d26)
      .merge(contact_block(["phase", "p_throws"], d26), on=["phase", "p_throws"], how="left")
      .merge(bat_tracking_block(["phase", "p_throws"], d26), on=["phase", "p_throws"], how="left"))
receipt("c3_handedness_phase", c3)

# C4 velocity band — is he late on velocity?
d26["velo_band"] = pd.cut(d26.release_speed, bins=[0, 88, 93, 96, 110],
                          labels=["<88 (soft)", "88-93", "93-96", "96+ (premium)"]).astype(str)
d26 = d26[d26.velo_band != "nan"].copy()
c4 = (_results_core(["phase", "velo_band"], d26)
      .merge(contact_block(["phase", "velo_band"], d26), on=["phase", "velo_band"], how="left")
      .merge(bat_tracking_block(["phase", "velo_band"], d26), on=["phase", "velo_band"], how="left")
      .merge(whiff_rate(["phase", "velo_band"], d26)[["phase", "velo_band", "whiff_rate"]],
             on=["phase", "velo_band"], how="left"))
receipt("c4_velocity_band_phase", c4)

# C5 batted ball type mix
def bbt(dd, label):
    bip = dd[dd.is_bip & dd.bb_type.notna()]
    t = bip.groupby("bb_type", as_index=False).agg(
        bips=("des", "size"), ev_mu=("launch_speed", "mean"),
        xwobacon=("estimated_woba_using_speedangle", "mean"))
    t["share"] = (t.bips / t.bips.sum()).round(4)
    t["window"] = label
    return t.round(3)

c5 = pd.concat([bbt(d26[d26.phase == pa_["phase"]], pa_["phase"]),
                bbt(d26[d26.phase == pb_["phase"]], pb_["phase"]),
                bbt(d25, "2025 full season")], ignore_index=True)
receipt("c5_batted_ball_mix", c5)

# C6 pull/air — where is he hitting it
for frame in (d26,):
    frame["loc_x"] = 2.5 * (frame.hc_x - 125.42)
    frame["loc_y"] = 2.5 * (198.27 - frame.hc_y)
bipd = d26[d26.is_bip & d26.loc_x.notna() & d26.loc_y.notna()].copy()
# Schwarber is LHB: pull = right field => loc_y <= 4.7 * loc_x
bipd["hit_direction"] = np.select(
    [bipd.loc_y <= 4.7 * bipd.loc_x,
     bipd.loc_y <= -4.7 * bipd.loc_x],
    ["Pull", "Oppo"], default="Straightaway")
c6 = bipd.groupby(["phase", "hit_direction"], as_index=False).agg(
    bips=("des", "size"), ev_mu=("launch_speed", "mean"), la_mu=("launch_angle", "mean"),
    xwobacon=("estimated_woba_using_speedangle", "mean"),
    barrels=("launch_speed_angle", lambda x: (x == 6).sum()))
c6["share"] = c6.bips / c6.groupby("phase").bips.transform("sum")
c6["barrel_rate"] = c6.barrels / c6.bips
receipt("c6_spray_direction_phase", c6.round(3))

# C7 count leverage — two-strike vs ahead
d26["count_state"] = np.where(d26.strikes == 2, "Two strikes",
                              np.where(d26.balls > d26.strikes, "Ahead", "Even/Behind"))
c7 = (_results_core(["phase", "count_state"], d26)
      .merge(contact_block(["phase", "count_state"], d26), on=["phase", "count_state"], how="left")
      .merge(bat_tracking_block(["phase", "count_state"], d26),
             on=["phase", "count_state"], how="left"))
receipt("c7_count_state_phase", c7)

# ---------------------------------------------------------------------------
# 7. D — Swing path (2025 vs 2026, the only window that exists)
# ---------------------------------------------------------------------------

print("\n[8] D — swing path 2025 v 2026")

sp = car[car.game_year.isin([2025, 2026])].copy()
d1 = bat_tracking_block(["game_year"], sp)
receipt("d1_swing_path_year", d1)

# D2 swing path by pitch group
d2 = bat_tracking_block(["game_year", "pitch_group"], sp)
receipt("d2_swing_path_group", d2)

# D3 attack angle vs outcome — does his own path predict his own damage?
sp_bip = sp[sp.is_bip & sp.attack_angle.notna()].copy()
sp_bip["aa_bucket"] = pd.cut(sp_bip.attack_angle, bins=[-30, 0, 5, 10, 15, 20, 25, 60],
                             labels=["<0", "0-5", "5-10", "10-15", "15-20",
                                     "20-25", "25+"]).astype(str)
d3 = sp_bip.groupby(["game_year", "aa_bucket"], as_index=False).agg(
    bips=("des", "size"), ev_mu=("launch_speed", "mean"), la_mu=("launch_angle", "mean"),
    barrels=("launch_speed_angle", lambda x: (x == 6).sum()),
    xwobacon=("estimated_woba_using_speedangle", "mean"))
d3["barrel_rate"] = (d3.barrels / d3.bips).round(3)
receipt("d3_attack_angle_outcome", d3.round(3))

# D4 contact depth distribution
d4 = sp[sp.is_bip & sp.contact_depth.notna()].groupby("game_year", as_index=False).agg(
    n=("contact_depth", "size"), depth_mu=("contact_depth", "mean"),
    depth_p25=("contact_depth", lambda x: x.quantile(0.25)),
    depth_p75=("contact_depth", lambda x: x.quantile(0.75)),
    depth_sd=("contact_depth", "std"))
d4b = d26[d26.is_bip & d26.contact_depth.notna()].groupby("phase", as_index=False).agg(
    n=("contact_depth", "size"), depth_mu=("contact_depth", "mean"),
    depth_p25=("contact_depth", lambda x: x.quantile(0.25)),
    depth_p75=("contact_depth", lambda x: x.quantile(0.75)),
    depth_sd=("contact_depth", "std")).rename(columns={"phase": "game_year"})
receipt("d4_contact_depth", pd.concat([d4, d4b], ignore_index=True).round(2))

# ---------------------------------------------------------------------------
# 8. E — Peer context (Phillies LHB, Statcast era) — secondary framing
# ---------------------------------------------------------------------------

print("\n[9] E — Phillies LHB peer pool")

lhb = pos[(pos.stand == "L") & (pos.game_type == "R")].drop_duplicates(subset=PITCH_KEY).copy()
lhb["game_date"] = pd.to_datetime(lhb.game_date)
lhb = add_swing_features(lhb)
e1 = (_results_core(["player_name", "game_year"], lhb)
      .merge(contact_block(["player_name", "game_year"], lhb),
             on=["player_name", "game_year"], how="left")
      .merge(bat_tracking_block(["player_name", "game_year"], lhb),
             on=["player_name", "game_year"], how="left"))
e1 = e1[e1.plate_apps >= 100].copy()          # house threshold for publishing batter rates
e1["is_schwarber"] = e1.player_name == "Schwarber, Kyle"
receipt("e1_phillies_lhb_pool", e1.round(3))

# E2 — 2026 bat-tracking percentile position within the measured pool
pool26 = e1[(e1.game_year == 2026) & (e1.bt_swings > 0)]
e2rows = []
for col in ["bat_speed_mu", "fast_swing_rate", "swing_length_mu", "attack_angle_mu",
            "swing_path_tilt_mu", "squared_up_rate", "ideal_contact_rate",
            "sweet_spot_rate", "barrel_rate", "ev90"]:
    if col not in pool26 or pool26[col].notna().sum() < 3:
        continue
    v = pool26.loc[pool26.is_schwarber, col]
    if v.empty or pd.isna(v.iloc[0]):
        continue
    sv = float(v.iloc[0])
    e2rows.append({"metric": col, "schwarber": round(sv, 3),
                   "pool_n": int(pool26[col].notna().sum()),
                   "pool_median": round(pool26[col].median(), 3),
                   "pool_max": round(pool26[col].max(), 3),
                   "pctile": round(100 * (pool26[col] < sv).mean(), 1)})
receipt("e2_lhb_percentiles_2026", pd.DataFrame(e2rows))

# ---------------------------------------------------------------------------
# 9. DQ scorecard & freshness manifest
# ---------------------------------------------------------------------------

print("\n[10] DQ scorecard")

dq = []


def check(rule, dimension, cond, detail):
    dq.append({"rule": rule, "dimension": dimension,
               "result": "PASS" if bool(cond) else "FAIL", "detail": detail})


check("DQ-01", "uniqueness", car.duplicated(subset=PITCH_KEY).sum() == 0,
      f"{car.duplicated(subset=PITCH_KEY).sum()} duplicate pitch keys after dedup")
check("DQ-02", "validity", set(car.batter.unique()) == {SCHWARBER},
      f"batter ids present: {sorted(car.batter.unique())}")
check("DQ-03", "validity", not contam_ids,
      f"name-filter would have pulled extra ids: {contam_ids or 'none'}")
check("DQ-04", "validity", set(car.game_type.unique()) == {"R"},
      f"game_type values: {sorted(car.game_type.unique())}")
check("DQ-05", "consistency", set(car.stand.dropna().unique()) == {"L"},
      f"stand values: {sorted(car.stand.dropna().unique())}")
check("DQ-06", "completeness",
      car[car.is_bip].launch_angle.notna().mean() > 0.97,
      f"launch_angle coverage on BIP: {car[car.is_bip].launch_angle.notna().mean():.3f}")
check("DQ-07", "completeness",
      d26[d26.is_swing].bat_speed.notna().mean() > 0.95,
      f"2026 bat_speed coverage on swings: {d26[d26.is_swing].bat_speed.notna().mean():.3f}")
_pre24 = car[(car.game_year < 2024) & car.is_swing]
check("DQ-08", "accuracy", _pre24.bat_speed.notna().sum() == 0,
      f"pre-2024 bat_speed values present: {int(_pre24.bat_speed.notna().sum())} (expected 0)")
_pre25 = car[(car.game_year < 2025) & car.is_swing]
check("DQ-09", "accuracy", _pre25.attack_angle.notna().sum() == 0,
      f"pre-2025 attack_angle values present: {int(_pre25.attack_angle.notna().sum())} (expected 0)")
check("DQ-10", "accuracy",
      a1.loc[a1.game_year < 2024, "bat_speed_mu"].isna().all(),
      "no bat_speed_mu published for any pre-sensor season (no-imputation policy)")
check("DQ-11", "accuracy",
      a1.loc[a1.game_year < 2025, "attack_angle_mu"].isna().all(),
      "no attack_angle_mu published for any pre-sensor season")
_ps = car.plate_speed.dropna()
check("DQ-12", "validity", (_ps.between(60, 105)).mean() > 0.99,
      f"derived plate speed in [60,105] mph: {(_ps.between(60,105)).mean():.4f}")
_gap = (car.release_speed - car.plate_speed).dropna()
check("DQ-13", "accuracy", 5 < _gap.mean() < 12,
      f"release minus plate speed mean = {_gap.mean():.2f} mph (physics sanity: 5-12)")
_sq = car.squared_up_pct.dropna()
check("DQ-14", "validity", (_sq.between(0, 1.15)).mean() > 0.99,
      f"squared_up_pct in [0,1.15]: {(_sq.between(0,1.15)).mean():.4f}")
check("DQ-15", "consistency",
      abs(int(a1.bips.sum()) - int(car.is_bip.sum())) == 0,
      f"season-spine BIP total {int(a1.bips.sum())} == source BIP {int(car.is_bip.sum())}")
check("DQ-16", "consistency",
      int(b5.bips.sum()) == int(d26.is_bip.sum()),
      f"phase-split BIP {int(b5.bips.sum())} == 2026 BIP {int(d26.is_bip.sum())}")
check("DQ-17", "timeliness",
      (pd.Timestamp.today().normalize() - car.game_date.max()).days <= 3,
      f"max game_date {car.game_date.max():%Y-%m-%d}, "
      f"{(pd.Timestamp.today().normalize() - car.game_date.max()).days} days stale")
check("DQ-18", "completeness", len(d26[d26.is_bip]) >= 150,
      f"2026 BIP available: {len(d26[d26.is_bip])} (min 150 to publish phase splits)")
check("DQ-19", "validity",
      car[car.is_bip].launch_speed.dropna().between(5, 125).mean() > 0.999,
      "launch_speed within physical bounds")
check("DQ-20", "consistency",
      set(a2.loc[a2.sensor_status != "not measured", "game_year"]) == {2024, 2025, 2026},
      f"measured seasons: {sorted(a2.loc[a2.sensor_status!='not measured','game_year'])}")
check("DQ-21", "uniqueness", e1.duplicated(subset=["player_name", "game_year"]).sum() == 0,
      "peer pool has one row per player-season (no join fan-out)")
check("DQ-22", "completeness", len(RECEIPTS) >= 20,
      f"{len(RECEIPTS)} receipts written")
check("DQ-23", "accuracy", x1.loc[x1.measured_n == 0, "measured_mu"].isna().all(),
      "zero-coverage seasons carry a null measured mean, not a filled one")
check("DQ-24", "validity", roll.window_n.min() == W,
      f"rolling window size held at {W} BIP throughout")

dqdf = pd.DataFrame(dq)
receipt("dq_scorecard", dqdf)
print(dqdf.to_string(index=False))
n_fail = (dqdf.result == "FAIL").sum()
print(f"\n  DQ: {(dqdf.result=='PASS').sum()}/{len(dqdf)} PASS, {n_fail} FAIL")

fresh = pd.DataFrame([
    {"source": "data/phillies/phils_*.parquet", "rows_loaded": len(phils),
     "max_game_date": str(pos.game_date.max()), "role": "primary (2022-2026 PHI)"},
    {"source": "data/opponents/schwarber.parquet", "rows_loaded": len(nphl_sch),
     "max_game_date": str(nphl_sch.game_date.max()), "role": "career backfill (2015-2021)"},
    {"source": "entity lock", "rows_loaded": len(car),
     "max_game_date": f"{car.game_date.max():%Y-%m-%d}", "role": f"batter=={SCHWARBER}, game_type=R"},
    {"source": "build timestamp", "rows_loaded": np.nan,
     "max_game_date": str(pd.Timestamp.now()), "role": "run time"},
])
receipt("freshness_manifest", fresh)

# ---------------------------------------------------------------------------
# 10. Figures (Phillies brand; every number traces to a receipt above)
# ---------------------------------------------------------------------------

print("\n[11] figures")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

plt.rcParams.update({
    "font.family": "DejaVu Sans", "axes.edgecolor": "#cfd4da",
    "axes.labelcolor": PHI_NAVY, "text.color": "#1f2933",
    "xtick.color": "#6b7280", "ytick.color": "#6b7280",
    "axes.titlecolor": PHI_NAVY, "figure.facecolor": "white",
    "axes.grid": True, "grid.color": "#eef1f4", "grid.linewidth": 0.8,
    "axes.axisbelow": True,
})


def _finish(fig, path):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  figure   {path}")


# Fig 1 — rolling damage curve
fig, ax = plt.subplots(figsize=(10, 4.6))
ax.plot(roll.bip_idx, roll.barrel_rate * 100, color=PHI_RED, lw=2.4, label=f"Barrel rate ({W}-BIP roll)")
ax.plot(roll.bip_idx, roll.ideal_contact_rate * 100, color=PHI_NAVY, lw=2.0, ls="--",
        label=f"Ideal-contact rate SW-2 ({W}-BIP roll)")
ax.plot(roll.bip_idx, roll.sweet_spot_rate * 100, color=PHI_LIGHT, lw=1.8, ls=":",
        label=f"Sweet-spot rate SW-1 ({W}-BIP roll)")
ax.set_xlabel("Ball in play, chronological (2026)")
ax.set_ylabel("Rate (%)")
ax.set_title("Fig 1 — Sweet spot held. Damage did not.\n"
             "Rolling 60-BIP windows, 2026 regular season",
             loc="left", fontsize=12.5, fontweight="bold", pad=12)
ax.legend(frameon=False, fontsize=9, loc="upper right")
_finish(fig, "dp_uc32_fig1_rolling_damage.png")

# Fig 2 — bat speed flat vs damage falling (the dissociation)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.plot(rolls.swing_idx, rolls.bat_speed_mu, color=PHI_NAVY, lw=2.4)
ax1.fill_between(rolls.swing_idx, rolls.bat_speed_mu - 0.5, rolls.bat_speed_mu + 0.5,
                 color=PHI_NAVY, alpha=0.10)
ax1.set_title("Bat speed (150-swing roll)", loc="left", fontsize=11, fontweight="bold")
ax1.set_xlabel("Measured swing, chronological (2026)")
ax1.set_ylabel("mph")
ax2.plot(roll.bip_idx, roll.ev90, color=PHI_RED, lw=2.4)
ax2.set_title("EV90 (60-BIP roll)", loc="left", fontsize=11, fontweight="bold")
ax2.set_xlabel("Ball in play, chronological (2026)")
ax2.set_ylabel("mph")
fig.suptitle("Fig 2 — The engine is intact; the transfer is not.",
             x=0.005, ha="left", fontsize=13, fontweight="bold", color=PHI_NAVY)
_finish(fig, "dp_uc32_fig2_speed_vs_output.png")

# Fig 3 — launch angle redistribution
piv = c1.pivot_table(index="la_bucket", columns="window", values="share", observed=False)
order = ["Topped (<-10)", "Low drive (-10 to 8)", "Ideal low (8-20)",
         "Ideal high (20-32)", "Under (32-50)", "Pop up (>50)"]
piv = piv.reindex(order)
cols = [pa_["phase"], pb_["phase"]]
fig, ax = plt.subplots(figsize=(10, 4.4))
x = np.arange(len(piv))
w = 0.38
ax.bar(x - w / 2, piv[cols[0]].values * 100, w, color=PHI_NAVY, label=cols[0])
ax.bar(x + w / 2, piv[cols[1]].values * 100, w, color=PHI_RED, label=cols[1])
ax.set_xticks(x)
ax.set_xticklabels(order, rotation=18, ha="right", fontsize=9)
ax.set_ylabel("Share of balls in play (%)")
ax.set_title("Fig 3 — Contact moved up, out of the damage band.",
             loc="left", fontsize=13, fontweight="bold")
ax.legend(frameon=False, fontsize=9)
_finish(fig, "dp_uc32_fig3_la_distribution.png")

# Fig 4 — imputation harm
fig, ax = plt.subplots(figsize=(10, 4.4))
meas = x1[x1.measured_n > 0]
ax.plot(x1.game_year, x1.imputed_mu, color="#b0b7c3", lw=2.2, ls="--", marker="o", ms=5,
        label="If NULLs were mean-imputed (rejected policy)")
ax.plot(meas.game_year, meas.measured_mu, color=PHI_RED, lw=3.0, marker="o", ms=7,
        label="Measured only (shipped policy)")
ax.axvspan(2014.5, 2023.5, color="#fdeef0", zorder=0)
ax.text(2019, ax.get_ylim()[0] + 0.4, "no sensor — nothing to average",
        fontsize=9, color="#9aa3af", ha="center")
ax.set_xlabel("Season")
ax.set_ylabel("Bat speed (mph)")
ax.set_title("Fig 4 — Imputation would have drawn a nine-season trend that was never measured.",
             loc="left", fontsize=12.5, fontweight="bold")
ax.legend(frameon=False, fontsize=9, loc="lower right")
_finish(fig, "dp_uc32_fig4_imputation_harm.png")

# Fig 5 — swing path 2025 v 2026
fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
for ax, col, lab in zip(axes,
                        ["attack_angle", "swing_path_tilt", "swing_length"],
                        ["Attack angle (deg)", "Swing path tilt (deg)", "Swing length (ft)"]):
    for yr, c in [(2025, PHI_LIGHT), (2026, PHI_RED)]:
        v = sp[(sp.game_year == yr) & sp.is_swing][col].dropna()
        if len(v):
            ax.hist(v, bins=45, density=True, histtype="step", lw=2.2, color=c, label=str(yr))
    ax.set_xlabel(lab)
    ax.set_yticks([])
    ax.legend(frameon=False, fontsize=8)
fig.suptitle("Fig 5 — Swing shape is unchanged year over year.",
             x=0.005, ha="left", fontsize=13, fontweight="bold", color=PHI_NAVY)
_finish(fig, "dp_uc32_fig5_swing_path.png")

# ---------------------------------------------------------------------------
# 11. Headline JSON for the report / dashboard builders
# ---------------------------------------------------------------------------

s26 = a1[a1.game_year == 2026].iloc[0]
s25 = a1[a1.game_year == 2025].iloc[0]
head = {
    "as_of": f"{car.game_date.max():%Y-%m-%d}",
    "split_date": split_date.strftime("%Y-%m-%d"),
    "phase_a": pa_["phase"], "phase_b": pb_["phase"],
    "career_pitches": int(len(car)),
    "y2026": {k: (None if pd.isna(s26[k]) else float(s26[k])) for k in
              ["plate_apps", "bips", "ev_mu", "ev90", "la_mu", "sweet_spot_rate",
               "ideal_contact_rate", "barrel_rate", "hard_hit_rate", "bat_speed_mu",
               "fast_swing_rate", "attack_angle_mu", "swing_path_tilt_mu",
               "squared_up_rate", "xwobacon", "slg", "iso", "ops", "chase_rate",
               "whiff_rate", "whiff_rate_iz", "hrs", "krate", "bbrate"]},
    "y2025": {k: (None if pd.isna(s25[k]) else float(s25[k])) for k in
              ["plate_apps", "bips", "ev_mu", "ev90", "la_mu", "sweet_spot_rate",
               "ideal_contact_rate", "barrel_rate", "hard_hit_rate", "bat_speed_mu",
               "fast_swing_rate", "attack_angle_mu", "swing_path_tilt_mu",
               "squared_up_rate", "xwobacon", "slg", "iso", "ops", "chase_rate",
               "whiff_rate", "whiff_rate_iz", "hrs", "krate", "bbrate"]},
    "imputation_harm": harm,
    "dq": {"pass": int((dqdf.result == "PASS").sum()), "total": int(len(dqdf)),
           "fail": int(n_fail)},
    "receipts": sorted(RECEIPTS),
}
with open(os.path.join(OUT, "dp_uc32_headline.json"), "w") as f:
    json.dump(head, f, indent=2, default=str)
print(f"\n  headline  out/dp_uc32_headline.json")

print(f"\n[dp_uc32] complete — {len(RECEIPTS)} receipts, 5 figures, "
      f"DQ {(dqdf.result=='PASS').sum()}/{len(dqdf)}")
if n_fail:
    print("  *** DQ FAILURES PRESENT — do not publish until resolved ***")
    sys.exit(1)
