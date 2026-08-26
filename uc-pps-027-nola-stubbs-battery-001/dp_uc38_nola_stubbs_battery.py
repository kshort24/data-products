"""
dp_uc38_nola_stubbs_battery.py
==============================================================================
UC #38 · contract `uc-pps-027` · The Nola-Stubbs Battery
Aaron Nola (RHP, MLBAM 605400) x catcher (`fielder_2`) game-planning read.
Game context: PHI @ SEA, 2026-08-26, Stubbs catching (DPO carry-in).

WHAT THIS SCRIPT IS
-------------------
A governed, single-file build. Every rate KPI in the OUTCOME layer is inherited
VERBATIM from the locked UC8 -> UC11 -> UC15 -> UC25 line (`dp_uc25_nola_vs_dodgers.py`)
-- do not re-derive them, do not "improve" them. Every KPI in the BATTERY layer
(`BAT-*`) is NEW in this UC and carries a kpi-calculator spec in
`02_engineering_design.md` plus a glossary entry in `03_governance.md`.

HOW TO RUN
----------
    conda activate snakes
    cd <this folder>
    python dp_uc38_nola_stubbs_battery.py

Data root resolution order (portable by design):
    1. $MLB_DATA_ROOT                      (env override)
    2. ./data/phillies                     (staged copy next to this script)
    3. C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB\\data\\phillies

Writes ~15 CSV receipts + 5 PNG figures + DQ scorecard + freshness manifest
+ headlines JSON into ./out/. NEW FILES ONLY -- never overwrites a prior UC.

GOVERNANCE NON-NEGOTIABLES ENCODED HERE
---------------------------------------
G1  Entity lock is `pitcher == 605400`. NEVER a name filter. (The canonical
    failure is Nola / "Nolan Hoffman" 676510 contamination.)
G2  Regular season only (`game_type == 'R'`); dedup on game_pk+at_bat_number+
    pitch_number.
G3  Catcher assignment is NOT RANDOM. Every catcher split ships with the
    confound panel (`dp_uc38_confound_panel.csv`). No causal claim may be
    published without it.
G4  PITCH-CALL ATTRIBUTION IS NOT IN THE DATA. Statcast carries no PitchCom
    sender field. This script measures WHAT WAS THROWN, never WHO CHOSE IT.
    Any narrative that says "Nola called" or "Stubbs called" is unsupported.
G5  Small-sample discipline: PA/pitch counts ride on every output row so the
    report can print them. Floors are applied as FLAGS, not silent filters.
==============================================================================
"""
from __future__ import annotations

import glob
import json
import os
import sys
import unicodedata
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ===========================================================================
# CONFIG
# ===========================================================================
NOLA = 605400                  # Aaron Nola  (NOT Nolan Hoffman 676510)
GAME_DAY = "2026-08-26"        # PHI @ SEA (corrected from 08-25 at UC reopen)
CURRENT_YEAR = 2026

# "his last several starts" -- bidder decision in the DPO's absence.
# Headline window = 5. Sensitivity variants computed so the headline cannot be
# a window artifact (see dp_uc38_window_sensitivity.csv).
RECENT_N_STARTS = 5
SENSITIVITY_WINDOWS = (3, 5, 8)

# Sample floors -- APPLIED AS FLAGS, NOT FILTERS (G5).
GAME_FLOOR = 3                 # >=3 distinct game_pk per catcher slot (uc-cat-001 A-4)
PITCH_FLOOR = 100              # publish-with-confidence floor for rate KPIs
PA_FLOOR = 50                  # publish-with-confidence floor for outcome KPIs

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "phillies"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies",
]
PHIL_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
_WOBA_CANDIDATES = [
    os.environ.get("MLB_WOBA_CSV", ""),                     # env override (run-2 portability fix)
    os.path.join(HERE, "wOBA and FIP Constants.csv"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv",
]
WOBA_CSV = next((p for p in _WOBA_CANDIDATES if os.path.isfile(p)), None)

# --- constants inherited VERBATIM from dp_uc8 / dp_uc15 / dp_uc25 ----------
PLATE_HALF = 0.83              # zone x in [-0.83, 0.83] (ft)
BALL_FT = 2.94 / 12.0          # one baseball width (~0.245 ft) -- edge shadow band
SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]
TAKES = ["called_strike", "ball", "blocked_ball", "ball_blocked"]

# PITCH_GROUP -- canonical dict, dp_uc18_marsh_breakout.py (via uc-cat-001 lineage)
PITCH_GROUP = {
    "FF": "fastball", "SI": "fastball", "FC": "fastball",
    "SL": "breaking", "ST": "breaking", "CU": "breaking", "KC": "breaking",
    "SV": "breaking", "CS": "breaking",
    "CH": "offspeed", "FS": "offspeed", "FO": "offspeed", "SC": "offspeed",
    "KN": "offspeed",
}

# Catcher id->name AUTHORITY for 2020-2026, from uc-cat-001 01b
# (pybaseball.playerid_reverse_lookup). Used as a CROSS-CHECK against the
# DPO's own pos-frame merge, which is the primary resolver because it also
# covers Nola's 2015-2019 catchers (outside uc-cat-001's profile window).
CATCHER_DICT_2020_26 = {
    592663: "Realmuto, J.T.",
    596117: "Stubbs, Garrett",
    665561: "Marchan, Rafael",
    595284: "Knapp, Andrew",
    605244: "Garcia, Aramis",
    664848: "Sands, Donny",
}
STUBBS = 596117
REALMUTO = 592663

EVENT_OUTS = {"field_out": 1, "strikeout": 1, "force_out": 1, "sac_fly": 1,
              "sac_bunt": 1, "fielders_choice_out": 1, "caught_stealing_2b": 0,
              "grounded_into_double_play": 2, "double_play": 2,
              "strikeout_double_play": 2, "sac_fly_double_play": 2,
              "triple_play": 3, "other_out": 1}

PHI_RED, PHI_NAVY, PHI_GRAY, PHI_LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"

DQ: list[dict] = []


def dq(check, result, detail="", severity="INFO"):
    DQ.append(dict(check=check, result=result, detail=detail, severity=severity))
    print(f"  [{severity:<4}] {check}: {result}  {detail}")


# ===========================================================================
# LOAD
# ===========================================================================
def _coerce(df):
    for c in ["plate_x", "plate_z", "sz_top", "sz_bot", "pfx_x", "pfx_z",
              "release_speed", "release_spin_rate", "launch_speed", "launch_angle",
              "strikes", "balls", "pitch_number", "woba_value", "woba_denom",
              "zone", "fielder_2", "batter", "pitcher"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_all_phillies():
    """Full Phillies frame (both roles) -- needed for catcher name resolution."""
    if PHIL_DIR is None:
        raise FileNotFoundError(
            "Could not locate data/phillies. Set MLB_DATA_ROOT or stage a copy.")
    frames = []
    for f in sorted(glob.glob(os.path.join(PHIL_DIR, "phils_*.parquet"))):
        frames.append(pd.read_parquet(f))
    df = pd.concat(frames, ignore_index=True)
    df = df[df.game_type == "R"].copy()
    df = df.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    df = _coerce(df)
    df["game_date"] = pd.to_datetime(df.game_date)
    return df


def split_roles(df):
    """pos = PHI batting, pps = PHI pitching. Mirrors mlb_data._split_phils."""
    if "phillies_role" in df.columns:
        pos = df[df.phillies_role == "batting"].copy()
        pps = df[df.phillies_role == "pitching"].copy()
    else:
        batting = (((df.home_team == "PHI") & (df.inning_topbot == "Bot"))
                   | ((df.away_team == "PHI") & (df.inning_topbot == "Top")))
        pos, pps = df[batting].copy(), df[~batting].copy()
    return pos, pps


def attach_woba_weights(df):
    if WOBA_CSV is None:
        dq("woba_weights_join", "MISSING",
           "wOBA and FIP Constants.csv not found -- woba column will be NaN",
           "FAIL")
        return df
    w = pd.read_csv(WOBA_CSV)
    df = df.drop(columns=[c for c in w.columns if c != "Season" and c in df.columns])
    return df.merge(w, left_on="game_year", right_on="Season", how="left")


# ===========================================================================
# LOCKED KPI FUNCTIONS -- inherited VERBATIM from dp_uc25_nola_vs_dodgers.py
# (which inherited from dp_uc15 <- dp_uc11 <- dp_uc8 <- Baseball Functions).
# DO NOT EDIT. Any change breaks comparability with the whole Nola advance file.
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
                    "ba", "obp", "slg", "ops", "woba", "xwoba", "krate", "bbrate", "hr_rate"]
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
    hh = df[(df.launch_speed >= 95) & (df.type == "X")].groupby(level, as_index=False).agg(hard_hits=("des", "size"))
    bips = df[df.type == "X"].groupby(level, as_index=False).agg(bips=("des", "size"))
    out = bips.merge(hh, on=level, how="left").fillna(0)
    out["hard_hit_rate"] = out.hard_hits / out.bips
    return out.round(3)


# --- NEW-IN-UC8 KPI functions, glossary approved, inherited VERBATIM -------
def _dist_to_zone_edge(px, pz, sz_bot, sz_top):
    hw = PLATE_HALF
    dx_out = np.maximum.reduce([-hw - px, px - hw, np.zeros_like(px)])
    dz_out = np.maximum.reduce([sz_bot - pz, pz - sz_top, np.zeros_like(pz)])
    outside = (dx_out > 0) | (dz_out > 0)
    dist_out = np.sqrt(dx_out ** 2 + dz_out ** 2)
    dist_in = np.minimum.reduce([hw - np.abs(px), pz - sz_bot, sz_top - pz])
    return np.where(outside, dist_out, dist_in)


def edge_rate(level, df):
    if isinstance(level, str):
        level = [level]
    d = df.dropna(subset=["plate_x", "plate_z", "sz_top", "sz_bot"]).copy()
    dist = _dist_to_zone_edge(d.plate_x.values, d.plate_z.values, d.sz_bot.values, d.sz_top.values)
    d["is_edge"] = dist <= BALL_FT
    tot = d.groupby(level, as_index=False).agg(located_pitches=("is_edge", "size"))
    eg = d.groupby(level, as_index=False).agg(edge_pitches=("is_edge", "sum"))
    out = tot.merge(eg, on=level, how="left").fillna(0)
    out["edge_rate"] = out.edge_pitches / out.located_pitches
    return out.round(3)


def ooz_called_strike_rate(level, df):
    if isinstance(level, str):
        level = [level]
    ooz = df[df.zone > 9]
    tot = ooz.groupby(level, as_index=False).agg(ooz_pitches=("des", "size"))
    cs = ooz[ooz.description == "called_strike"].groupby(level, as_index=False).agg(ooz_called_strikes=("des", "size"))
    takes = ooz[ooz.description.isin(TAKES)].groupby(level, as_index=False).agg(ooz_takes=("des", "size"))
    out = tot.merge(cs, on=level, how="left").merge(takes, on=level, how="left").fillna(0)
    out["ooz_called_strike_rate"] = out.ooz_called_strikes / out.ooz_pitches
    out["ooz_csr_per_take"] = np.where(out.ooz_takes > 0, out.ooz_called_strikes / out.ooz_takes, np.nan)
    return out.round(3)


def air_gb_rate(level, df):
    if isinstance(level, str):
        level = [level]
    bip = df[df.type == "X"].copy()
    tot = bip.groupby(level, as_index=False).agg(bip=("des", "size"))

    def share(mask, name):
        return bip[mask].groupby(level, as_index=False).agg(**{name: ("des", "size")})

    gb = share(bip.bb_type == "ground_ball", "gb")
    fb = share(bip.bb_type == "fly_ball", "fb")
    ld = share(bip.bb_type == "line_drive", "ld")
    pu = share(bip.bb_type == "popup", "pu")
    out = tot
    for x in [gb, fb, ld, pu]:
        out = out.merge(x, on=level, how="left")
    out = out.fillna(0)
    out["gb_rate"] = out.gb / out.bip
    out["fb_rate"] = out.fb / out.bip
    out["ld_rate"] = out.ld / out.bip
    out["pu_rate"] = out.pu / out.bip
    out["air_rate"] = (out.fb + out.ld + out.pu) / out.bip
    return out.round(3)


def xwobacon(level, df):
    """xwOBA on contact. The get_stats 'xwoba' column is a pitch-level mean
    contaminated by non-BIP rows and must NOT be cited (uc-pps-021 DQ fix)."""
    if isinstance(level, str):
        level = [level]
    b = df[df.type == "X"]
    if not len(b):
        return pd.DataFrame(columns=level + ["xwobacon"])
    return b.groupby(level, as_index=False).agg(
        xwobacon=("estimated_woba_using_speedangle", "mean")).round(3)


def ip_from_events(df):
    outs = df.events.map(EVENT_OUTS).fillna(0).sum()
    whole, rem = divmod(int(outs), 3)
    return float(f"{whole}.{rem}")


# ===========================================================================
# NEW IN THIS UC -- the BATTERY / GAME-PLAN layer (`BAT-*`)
# Specs: 02_engineering_design.md  ·  Glossary: 03_governance.md
# Every one of these measures WHAT WAS THROWN. None measures WHO CALLED IT (G4).
# ===========================================================================
def count_state(df):
    """CS-1. Ahead / even / behind from the PITCHER's perspective.
    ahead: strikes > balls · behind: balls > strikes · even: equal."""
    b, s = df.balls.values, df.strikes.values
    return np.where(s > b, "ahead", np.where(b > s, "behind", "even"))


def mix_share(level, df, col="pitch_type", min_pitches=0):
    """BAT-1. Usage share of `col` within each `level` group.
    Returns long form: level + [col, n, group_n, share]. Zero-count pitch types
    are ABSENT (not zero rows) -- callers that need the full support must
    reindex. `group_n` rides along so the report can print the denominator."""
    if isinstance(level, str):
        level = [level]
    d = df.dropna(subset=[col])
    n = d.groupby(level + [col], as_index=False).agg(n=("des", "size"))
    tot = d.groupby(level, as_index=False).agg(group_n=("des", "size"))
    out = n.merge(tot, on=level, how="left")
    out["share"] = out.n / out.group_n
    return out[out.group_n >= min_pitches].round(4)


def mix_vector(df, col="pitch_type", support=None):
    """Helper: normalised usage vector over a fixed `support` (list of labels).
    Missing labels get 0.0. Returns np.ndarray aligned to `support`."""
    v = df[col].value_counts()
    if support is None:
        support = sorted(v.index.tolist())
    arr = np.array([float(v.get(k, 0)) for k in support])
    tot = arr.sum()
    return arr / tot if tot > 0 else arr


def repeat_pitch_rate(level, df):
    """BAT-5 (NEW-PROVISIONAL). Within a plate appearance, the share of
    consecutive pitch pairs (n-1, n) that are the SAME pitch_type.

    Reads as CONVICTION vs MIXING: a battery that doubles up is willing to
    show the same shape twice; a battery that never repeats is either
    sequencing deliberately or is afraid of the hitter's timing.

    Denominator = pitch pairs, i.e. (pitches in PA - 1) summed over PAs with
    >=2 pitches. Single-pitch PAs contribute NOTHING to either side.
    Nulls: rows with null pitch_type break the chain -- the pair spanning a
    null is dropped from both numerator and denominator (conservative)."""
    if isinstance(level, str):
        level = [level]
    d = df.dropna(subset=["pitch_type"]).sort_values(
        ["game_pk", "at_bat_number", "pitch_number"]).copy()
    d["prev_type"] = d.groupby(["game_pk", "at_bat_number"]).pitch_type.shift(1)
    d["prev_num"] = d.groupby(["game_pk", "at_bat_number"]).pitch_number.shift(1)
    # only count pairs that are genuinely CONSECUTIVE (guards the null-break)
    pairs = d[(d.prev_type.notna()) & (d.pitch_number - d.prev_num == 1)].copy()
    pairs["is_repeat"] = (pairs.pitch_type == pairs.prev_type).astype(int)
    out = pairs.groupby(level, as_index=False).agg(
        pitch_pairs=("is_repeat", "size"), repeats=("is_repeat", "sum"))
    out["repeat_pitch_rate"] = np.where(
        out.pitch_pairs > 0, out.repeats / out.pitch_pairs, np.nan)
    return out.round(4)


def arsenal_entropy(level, df, col="pitch_type", global_support=None):
    """BAT-6 (NEW-PROVISIONAL). Shannon entropy of the pitch-type usage
    distribution -- a single-number PREDICTABILITY score.

        H      = -sum(p_i * ln p_i)                    (nats)
        H_norm = H / ln(K_global)                      in [0, 1]

    K_global = the count of distinct pitch types in Nola's arsenal across the
    WHOLE frame, so that groups are comparable to each other (normalising by
    each group's own active-type count would make a 2-pitch group with a 50/50
    split score 1.0, which is nonsense for this question).

    Reads: 0 = one pitch only (perfectly predictable). 1 = every pitch in the
    arsenal thrown equally often (maximally unpredictable). Note this is a
    FIRST-ORDER measure -- it is blind to sequence. BAT-5 and BAT-7 cover the
    conditional structure entropy cannot see."""
    if isinstance(level, str):
        level = [level]
    d = df.dropna(subset=[col])
    if global_support is None:
        global_support = sorted(d[col].dropna().unique().tolist())
    k_global = max(len(global_support), 2)
    rows = []
    for key, g in d.groupby(level):
        key = key if isinstance(key, tuple) else (key,)
        p = mix_vector(g, col, support=global_support)
        p = p[p > 0]
        h = float(-(p * np.log(p)).sum()) if len(p) else np.nan
        if h == h and abs(h) < 1e-12:
            h = 0.0                     # kill the -0.0 that a single-type group produces
        rows.append(dict(zip(level, key)) | {
            "pitches_typed": int(len(g)),
            "active_types": int((mix_vector(g, col, support=global_support) > 0).sum()),
            "entropy_nats": h,
            "entropy_norm": h / np.log(k_global) if h == h else np.nan,
        })
    return pd.DataFrame(rows).round(4)


def _js_divergence(p, q):
    """Jensen-Shannon divergence, base 2 -> bounded [0, 1]. 0*log0 := 0."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    if p.sum() <= 0 or q.sum() <= 0:
        return np.nan
    p, q = p / p.sum(), q / q.sum()
    m = 0.5 * (p + q)

    def _kl(a, b):
        mask = a > 0
        return float((a[mask] * np.log2(a[mask] / b[mask])).sum())

    return 0.5 * _kl(p, m) + 0.5 * _kl(q, m)


def count_state_divergence(level, df, col="pitch_type"):
    """BAT-7 (NEW-PROVISIONAL). Jensen-Shannon divergence between the
    AHEAD-count pitch mix and the BEHIND-count pitch mix, within each group.

    Reads as PLAN ADAPTIVITY: 0 = the battery throws the same distribution
    regardless of the count (one plan, executed). Toward 1 = the ahead and
    behind arsenals are effectively different pitchers.

    This is NOT a quality metric. High adaptivity is not automatically good --
    a pitcher who abandons his best pitch when behind is 'adaptive' and worse
    for it. Read it beside BAT-4 (what he actually goes to when behind).
    Reported only where BOTH sub-populations clear `min_side` pitches."""
    if isinstance(level, str):
        level = [level]
    d = df.dropna(subset=[col]).copy()
    d["count_state"] = count_state(d)
    support = sorted(d[col].dropna().unique().tolist())
    rows = []
    for key, g in d.groupby(level):
        key = key if isinstance(key, tuple) else (key,)
        a, b = g[g.count_state == "ahead"], g[g.count_state == "behind"]
        rows.append(dict(zip(level, key)) | {
            "ahead_pitches": int(len(a)),
            "behind_pitches": int(len(b)),
            "js_divergence": _js_divergence(mix_vector(a, col, support),
                                            mix_vector(b, col, support)),
        })
    return pd.DataFrame(rows).round(4)


def first_pitch_mix(level, df):
    """BAT-2 (NEW-PROVISIONAL). Pitch-GROUP share on `pitch_number == 1`.
    How does this battery START a hitter -- get-me-over fastball, or a
    breaking ball for a first-pitch strike? Denominator = first pitches."""
    if isinstance(level, str):
        level = [level]
    fp = df[df.pitch_number == 1].copy()
    fp["pitch_group"] = fp.pitch_type.map(PITCH_GROUP).fillna("other")
    return mix_share(level, fp, "pitch_group")


def putaway_pitch_mix(level, df):
    """BAT-3 (NEW-PROVISIONAL). On the pitch that TERMINATES a two-strike
    plate appearance, the pitch-GROUP share. What finishes hitters?
    Population: strikes == 2 AND events is non-null (PA-terminal row).
    Note this includes terminal CONTACT, not just strikeouts -- the question
    is 'what was the finish pitch', not 'what got the K'. The strikeout-only
    cut is `putaway_rate` (locked), reported beside it."""
    if isinstance(level, str):
        level = [level]
    d = df[(df.strikes == 2) & (df.events.notna()) & (df.events != "NA")].copy()
    d["pitch_group"] = d.pitch_type.map(PITCH_GROUP).fillna("other")
    return mix_share(level, d, "pitch_group")


def two_strike_fastball_rate(level, df):
    """BAT-4. Inherited from uc-cat-001 KPI-1 (governed, never shipped).
    Share of all two-strike pitches that are FASTBALL group.
    High = 'trust the stuff' (strength exploitation).
    Low  = 'make him chase' (weakness exploitation)."""
    if isinstance(level, str):
        level = [level]
    d = df[df.strikes == 2].dropna(subset=["pitch_type"]).copy()
    d["is_fb"] = (d.pitch_type.map(PITCH_GROUP) == "fastball").astype(int)
    out = d.groupby(level, as_index=False).agg(
        two_strike_pitches=("is_fb", "size"), two_strike_fastballs=("is_fb", "sum"))
    out["two_strike_fb_rate"] = np.where(
        out.two_strike_pitches > 0, out.two_strike_fastballs / out.two_strike_pitches, np.nan)
    return out.round(4)


def zone_rate_by_count_state(level, df):
    """BAT-8 (NEW-PROVISIONAL). In-zone rate (`zone <= 9`) split by count
    state. The 'does he attack or nibble when behind' indicator -- the direct
    process read on the uc-pps-021 lefty free-pass diagnosis.
    Nulls: rows with null `zone` fall out of BOTH sides (matches the governed
    `chase_rate` convention; open repo-wide item O-2)."""
    if isinstance(level, str):
        level = [level]
    d = df.dropna(subset=["zone"]).copy()
    d["count_state"] = count_state(d)
    d["in_zone"] = (d.zone <= 9).astype(int)
    out = d.groupby(level + ["count_state"], as_index=False).agg(
        located=("in_zone", "size"), in_zone=("in_zone", "sum"))
    out["zone_rate"] = out.in_zone / out.located
    return out.round(4)


def in_zone_whiff_rate(level, df):
    """BAT-9. Inherited from uc-cat-001 KPI-3 (governed, never shipped).
    Whiffs / swings, BOTH restricted to `zone <= 9`. Identical filter on each
    side -- the intake-doc label mismatch that uc-cat-001 caught is fixed here."""
    if isinstance(level, str):
        level = [level]
    d = df[df.zone <= 9]
    sw = d[d.description.isin(SWINGS)].groupby(level, as_index=False).agg(iz_swings=("des", "size"))
    wh = d[d.description.isin(WHIFFS)].groupby(level, as_index=False).agg(iz_whiffs=("des", "size"))
    out = sw.merge(wh, on=level, how="left").fillna({"iz_whiffs": 0})
    out["in_zone_whiff_rate"] = np.where(out.iz_swings > 0, out.iz_whiffs / out.iz_swings, np.nan)
    return out.round(4)


# ===========================================================================
# ASSEMBLY
# ===========================================================================
def battery_panel(level, df):
    """The full KPI family at one grain: exposure + locked outcome layer +
    battery layer. This is the workhorse -- every published table is a slice
    of one of these. Left-merges throughout so zero-event groups SURVIVE
    (the D1/D2 inner-merge defect from the repo-wide register)."""
    if isinstance(level, str):
        level = [level]
    exposure = df.groupby(level, as_index=False).agg(
        total_pitches=("des", "size"), uq_games=("game_pk", "nunique"))
    z = (exposure
         .merge(nresults(level, df), on=level, how="left", suffixes=("", "_res"))
         .merge(chase_rate(level, df)[level + ["ooz", "chases", "chase_rate", "in_zone_rate"]],
                on=level, how="left")
         .merge(whiff_rate(level, df)[level + ["swings", "whiffs", "whiff_rate"]],
                on=level, how="left")
         .merge(putaway_rate(level, df)[level + ["pitches2strikes", "putaway_rate"]],
                on=level, how="left")
         .merge(fpsr(level, df)[level + ["first_pitch_strike_rate"]], on=level, how="left")
         .merge(hard_hit_rate(level, df)[level + ["bips", "hard_hit_rate"]], on=level, how="left")
         .merge(xwobacon(level, df), on=level, how="left")
         .merge(edge_rate(level, df)[level + ["edge_rate"]], on=level, how="left")
         .merge(ooz_called_strike_rate(level, df)[level + ["ooz_called_strike_rate"]],
                on=level, how="left")
         .merge(air_gb_rate(level, df)[level + ["gb_rate", "air_rate"]], on=level, how="left")
         # --- battery layer ---
         .merge(two_strike_fastball_rate(level, df)[level + ["two_strike_pitches", "two_strike_fb_rate"]],
                on=level, how="left")
         .merge(in_zone_whiff_rate(level, df)[level + ["in_zone_whiff_rate"]], on=level, how="left")
         .merge(repeat_pitch_rate(level, df)[level + ["pitch_pairs", "repeat_pitch_rate"]],
                on=level, how="left")
         .merge(arsenal_entropy(level, df)[level + ["active_types", "entropy_norm"]],
                on=level, how="left")
         .merge(count_state_divergence(level, df)[level + ["ahead_pitches", "behind_pitches", "js_divergence"]],
                on=level, how="left")
         )
    # G5 -- floors ride as FLAGS, never as filters
    z["below_game_floor"] = z.uq_games < GAME_FLOOR
    z["below_pitch_floor"] = z.total_pitches < PITCH_FLOOR
    z["below_pa_floor"] = z.plate_apps < PA_FLOOR
    return z


def build_start_log(nola):
    """One row per Nola start, with the catcher who caught the majority of his
    pitches that game. `catcher_split` flags games where more than one catcher
    caught him -- those games are ambiguous for a catcher-attributed split and
    must be reported, not swallowed."""
    per_game_catcher = (nola.groupby(["game_pk", "fielder_2"], as_index=False)
                        .agg(n=("des", "size"))
                        .sort_values(["game_pk", "n"], ascending=[True, False]))
    modal = per_game_catcher.drop_duplicates("game_pk").rename(
        columns={"fielder_2": "catcher_id", "n": "catcher_pitches"})
    n_catchers = per_game_catcher.groupby("game_pk", as_index=False).agg(
        n_catchers=("fielder_2", "nunique"))
    modal = modal.merge(n_catchers, on="game_pk", how="left")
    modal["catcher_split"] = modal.n_catchers > 1

    rows = []
    for gp, g in nola.groupby("game_pk"):
        opp = g.away_team.iat[0] if g.home_team.iat[0] == "PHI" else g.home_team.iat[0]
        venue = "home" if g.home_team.iat[0] == "PHI" else "road"
        res = nresults(["game_pk"], g)
        rows.append(dict(
            game_pk=gp,
            game_date=g.game_date.min(),
            game_year=int(g.game_year.iat[0]),
            opponent=opp, venue=venue,
            pitches=len(g),
            ip_computed=ip_from_events(g),
            plate_apps=int(res.plate_apps.iat[0]) if len(res) else 0,
            hits=int(res.hits.iat[0]) if len(res) else 0,
            hrs=int(res.hrs.iat[0]) if len(res) else 0,
            walks=int(res.walks.iat[0]) if len(res) else 0,
            strikeouts=int(res.strikeouts.iat[0]) if len(res) else 0,
            woba=float(res.woba.iat[0]) if len(res) else np.nan,
        ))
    log = pd.DataFrame(rows).merge(modal[["game_pk", "catcher_id", "catcher_pitches",
                                          "n_catchers", "catcher_split"]],
                                   on="game_pk", how="left")
    log = log.sort_values("game_date").reset_index(drop=True)
    log["rest_days"] = log.game_date.diff().dt.days
    log["start_index_desc"] = np.arange(len(log))[::-1]      # 0 == most recent
    return log


def resolve_catcher_names(pos, nola):
    """Primary resolver = the DPO's own merge: catcher ids appear as BATTER ids
    in the Phillies batting frame, so the modal `player_name` per batter id is
    the name authority. Covers 2015-2019 catchers that uc-cat-001's 2020-26
    profile does not.
    Cross-check = CATCHER_DICT_2020_26 (pybaseball, uc-cat-001 01b). Any
    disagreement is a DQ FAIL, not a silent overwrite."""
    ids = sorted(nola.fielder_2.dropna().unique().astype(int).tolist())
    modal = (pos.dropna(subset=["batter", "player_name"])
             .groupby(["batter", "player_name"], as_index=False)
             .agg(pitches=("des", "size"))
             .sort_values(["batter", "pitches"], ascending=[True, False])
             .drop_duplicates("batter"))
    modal["batter"] = modal.batter.astype(int)
    name_map = dict(zip(modal.batter, modal.player_name))

    def _fold(x):
        """O-12 fix. Fold to ASCII + casefold before comparing names.
        The pos-frame carries MLBAM's accented spelling ('Marchan, Rafael' ->
        'Marchan, Rafael' with U+00E1); the uc-cat-001 pybaseball dict carries
        the unaccented spelling. A raw .lower() comparison called that a
        DISAGREE and raised a spurious DQ FAIL. Diacritics are a rendering
        difference, not an identity difference -- the MLBAM id is the identity.
        Precedent: Sanchez 650911 (uc-pps-019)."""
        return "".join(c for c in unicodedata.normalize("NFKD", x)
                       if not unicodedata.combining(c)).casefold().strip()

    out = []
    for cid in ids:
        primary = name_map.get(cid)
        authority = CATCHER_DICT_2020_26.get(cid)
        agree = (primary is None or authority is None or
                 _fold(primary.split(",")[0]) == _fold(authority.split(",")[0]))
        out.append(dict(catcher_id=cid,
                        name_from_pos_merge=primary,
                        name_from_uc_cat_001=authority,
                        resolved_name=primary or authority or f"UNRESOLVED_{cid}",
                        cross_check=("AGREE" if agree else "DISAGREE"),
                        source=("pos_merge" if primary else
                                ("uc-cat-001_dict" if authority else "UNRESOLVED"))))
    res = pd.DataFrame(out)
    bad = res[res.cross_check == "DISAGREE"]
    dq("catcher_name_cross_check",
       "PASS" if bad.empty else "FAIL",
       f"{len(res)} ids; {len(bad)} disagreements; "
       f"{int((res.source == 'UNRESOLVED').sum())} unresolved",
       "INFO" if bad.empty else "FAIL")
    return res


def confound_panel(start_log, cat_names):
    """G3. Catcher assignment is not random. This is the table that must ship
    beside every catcher split: what ELSE differs between the Stubbs starts and
    the non-Stubbs starts. If the Stubbs games are disproportionately at home,
    on extra rest, against weaker opponents, or clustered late in the season,
    the outcome delta is not cleanly a battery effect and the report must say so."""
    d = start_log.merge(cat_names[["catcher_id", "resolved_name"]], on="catcher_id", how="left")
    panel = d.groupby(["game_year", "resolved_name"], as_index=False).agg(
        starts=("game_pk", "nunique"),
        home_starts=("venue", lambda s: int((s == "home").sum())),
        mean_rest_days=("rest_days", "mean"),
        mean_pitches=("pitches", "mean"),
        mean_ip=("ip_computed", "mean"),
        first_date=("game_date", "min"),
        last_date=("game_date", "max"),
        opponents=("opponent", lambda s: ",".join(sorted(set(s)))),
        split_games=("catcher_split", "sum"),
    )
    panel["home_share"] = panel.home_starts / panel.starts
    return panel.round(3)


# ===========================================================================
# FIGURES
# ===========================================================================
def make_figures(mix_c, panel_season, start_log, cat_names, seq_window):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:                                    # pragma: no cover
        dq("figures", "SKIPPED", f"matplotlib unavailable: {e}", "WARN")
        return []
    made = []

    # fig 1 -- pitch mix by catcher (career), Stubbs highlighted
    try:
        piv = mix_c.pivot_table(index="pitch_type", columns="resolved_name",
                                values="share", aggfunc="first").fillna(0)
        ax = piv.plot(kind="bar", figsize=(11, 5.5), width=0.82,
                      color=[PHI_RED if "Stubbs" in c else PHI_NAVY if "Realmuto" in c
                             else PHI_GRAY for c in piv.columns])
        ax.set_title("Nola's arsenal, by catcher (career, regular season)",
                     color=PHI_NAVY, fontweight="bold")
        ax.set_ylabel("usage share"); ax.set_xlabel("")
        ax.legend(frameon=False, fontsize=8)
        plt.tight_layout(); p = os.path.join(OUT, "dp_uc38_fig1_mix_by_catcher.png")
        plt.savefig(p, dpi=150); plt.close(); made.append(p)
    except Exception as e:
        dq("fig1", "SKIPPED", str(e), "WARN")

    # fig 2 -- outcome by catcher over time
    try:
        fig, ax = plt.subplots(figsize=(11, 5))
        for nm, g in panel_season.groupby("resolved_name"):
            if g.total_pitches.sum() < PITCH_FLOOR:
                continue
            c = PHI_RED if "Stubbs" in str(nm) else PHI_NAVY if "Realmuto" in str(nm) else PHI_LGRAY
            ax.plot(g.game_year, g.woba, marker="o", label=str(nm), color=c,
                    linewidth=2.4 if c != PHI_LGRAY else 1.2)
        ax.set_title("wOBA allowed by battery, by season", color=PHI_NAVY, fontweight="bold")
        ax.set_ylabel("wOBA allowed"); ax.legend(frameon=False, fontsize=8)
        plt.tight_layout(); p = os.path.join(OUT, "dp_uc38_fig2_woba_by_battery.png")
        plt.savefig(p, dpi=150); plt.close(); made.append(p)
    except Exception as e:
        dq("fig2", "SKIPPED", str(e), "WARN")

    # fig 3 -- start log, coloured by catcher
    try:
        d = start_log.merge(cat_names[["catcher_id", "resolved_name"]], on="catcher_id", how="left")
        d = d[d.game_year == CURRENT_YEAR]
        colors = [PHI_RED if "Stubbs" in str(n) else PHI_NAVY for n in d.resolved_name]
        fig, ax = plt.subplots(figsize=(11, 4.6))
        ax.bar(range(len(d)), d.woba, color=colors)
        ax.set_xticks(range(len(d)))
        ax.set_xticklabels([f"{x:%m/%d}\n{o}" for x, o in zip(d.game_date, d.opponent)],
                           fontsize=7)
        ax.set_title(f"{CURRENT_YEAR} starts — wOBA allowed (red = Stubbs catching)",
                     color=PHI_NAVY, fontweight="bold")
        ax.set_ylabel("wOBA allowed")
        plt.tight_layout(); p = os.path.join(OUT, "dp_uc38_fig3_start_log.png")
        plt.savefig(p, dpi=150); plt.close(); made.append(p)
    except Exception as e:
        dq("fig3", "SKIPPED", str(e), "WARN")

    # fig 4 -- sequencing panel: repeat rate / entropy / JS divergence
    try:
        met = ["repeat_pitch_rate", "entropy_norm", "js_divergence"]
        lbl = ["repeat-pitch rate\n(BAT-5)", "arsenal entropy\n(BAT-6)",
               "ahead-vs-behind divergence\n(BAT-7)"]
        fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.4))
        for a, m, L in zip(axes, met, lbl):
            g = seq_window.dropna(subset=[m])
            a.bar(range(len(g)), g[m],
                  color=[PHI_RED if "Stubbs" in str(x) else PHI_NAVY for x in g.window_label])
            a.set_xticks(range(len(g)))
            a.set_xticklabels(g.window_label, rotation=30, ha="right", fontsize=7)
            a.set_title(L, color=PHI_NAVY, fontsize=9, fontweight="bold")
        plt.tight_layout(); p = os.path.join(OUT, "dp_uc38_fig4_sequencing.png")
        plt.savefig(p, dpi=150); plt.close(); made.append(p)
    except Exception as e:
        dq("fig4", "SKIPPED", str(e), "WARN")

    return made


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print("=" * 78)
    print("dp_uc38 · uc-pps-027 · The Nola-Stubbs Battery")
    print("=" * 78)

    if PHIL_DIR is None:
        print("\nFATAL: data/phillies not found on any candidate path.")
        print("Candidates tried:")
        for c in _DATA_CANDIDATES:
            print(f"  - {c or '(unset)'}")
        print("\nSet MLB_DATA_ROOT to the folder containing phils_*.parquet, or run")
        print("this script from the MLB repo. NO OUTPUT IS WRITTEN -- per the")
        print("pitcher-scouting-report skill, an unfilled harness beats a fabricated one.")
        sys.exit(2)

    print(f"\n[1/8] loading  ({PHIL_DIR})")
    allphi = load_all_phillies()
    pos, pps = split_roles(allphi)
    nola = pps[pps.pitcher == NOLA].copy()
    nola = attach_woba_weights(nola)
    dq("entity_lock", "PASS",
       f"pitcher==605400 only; {nola.pitcher.nunique()} distinct pitcher id(s); "
       f"{nola.player_name.nunique()} distinct player_name(s)",
       "INFO" if nola.pitcher.nunique() == 1 else "FAIL")
    dq("row_count", f"{len(nola):,} pitches",
       f"{nola.game_pk.nunique()} games, {nola.game_year.min()}-{nola.game_year.max()}")
    dq("fielder_2_null_rate", f"{nola.fielder_2.isna().mean():.4%}",
       "catcher CDE completeness",
       "INFO" if nola.fielder_2.isna().mean() < 0.001 else "WARN")
    as_of = nola.game_date.max()
    dq("freshness", str(as_of.date()), f"T-{(pd.Timestamp(GAME_DAY) - as_of).days} vs game day")

    print("\n[2/8] resolving catcher identities")
    cat_names = resolve_catcher_names(pos, nola)
    nola["catcher_id"] = nola.fielder_2.astype("Int64")
    nola = nola.merge(cat_names[["catcher_id", "resolved_name"]],
                      on="catcher_id", how="left")
    cat_names.to_csv(os.path.join(OUT, "dp_uc38_catcher_identity.csv"), index=False)

    print("\n[3/8] start log + windows")
    start_log = build_start_log(nola)
    start_log.to_csv(os.path.join(OUT, "dp_uc38_start_log.csv"), index=False)
    dq("catcher_split_games", f"{int(start_log.catcher_split.sum())} of {len(start_log)}",
       "starts where >1 catcher caught Nola (ambiguous for catcher attribution)",
       "INFO")

    recent_pks = set(start_log[start_log.start_index_desc < RECENT_N_STARTS].game_pk)
    nola["window"] = np.where(nola.game_pk.isin(recent_pks),
                              f"last_{RECENT_N_STARTS}",
                              np.where(nola.game_year == CURRENT_YEAR,
                                       f"{CURRENT_YEAR}_prior", "pre_2026"))

    print("\n[4/8] panels")
    panel_career = battery_panel(["catcher_id", "resolved_name"], nola)
    panel_season = battery_panel(["catcher_id", "resolved_name", "game_year"], nola)
    panel_window = battery_panel(["window", "catcher_id", "resolved_name"], nola)
    panel_overall = battery_panel(["player_name"], nola)          # Nola's own baseline
    for nm, d in [("battery_career", panel_career), ("battery_season", panel_season),
                  ("battery_window", panel_window), ("nola_baseline", panel_overall)]:
        d.sort_values(d.columns[0]).to_csv(os.path.join(OUT, f"dp_uc38_{nm}.csv"), index=False)

    print("\n[5/8] game-plan composition")
    mix_c = mix_share(["catcher_id", "resolved_name"], nola, "pitch_type")
    mix_cw = mix_share(["window", "catcher_id", "resolved_name"], nola, "pitch_type")
    fp_mix = first_pitch_mix(["window", "catcher_id", "resolved_name"], nola)
    pa_mix = putaway_pitch_mix(["window", "catcher_id", "resolved_name"], nola)
    zone_cs = zone_rate_by_count_state(["window", "catcher_id", "resolved_name"], nola)
    cs_mix = mix_share(["catcher_id", "resolved_name"], nola.assign(cs=count_state(nola)), "pitch_type")
    for nm, d in [("mix_by_catcher", mix_c), ("mix_by_catcher_window", mix_cw),
                  ("first_pitch_mix", fp_mix), ("putaway_pitch_mix", pa_mix),
                  ("zone_by_count_state", zone_cs), ("count_state_mix", cs_mix)]:
        d.to_csv(os.path.join(OUT, f"dp_uc38_{nm}.csv"), index=False)

    print("\n[6/8] sequencing + window sensitivity")
    seq_window = panel_window.assign(
        window_label=lambda d: d.window + " · " + d.resolved_name.fillna("?"))
    seq_window.to_csv(os.path.join(OUT, "dp_uc38_sequencing_window.csv"), index=False)

    sens = []
    for n in SENSITIVITY_WINDOWS:
        pks = set(start_log[start_log.start_index_desc < n].game_pk)
        sub = nola[nola.game_pk.isin(pks)]
        p = battery_panel(["resolved_name"], sub)
        p.insert(0, "window_n_starts", n)
        sens.append(p)
    sens = pd.concat(sens, ignore_index=True)
    sens.to_csv(os.path.join(OUT, "dp_uc38_window_sensitivity.csv"), index=False)
    dq("window_sensitivity", "COMPUTED",
       f"headline window = last {RECENT_N_STARTS} starts; variants {SENSITIVITY_WINDOWS}")

    print("\n[7/8] confound panel (G3)")
    conf = confound_panel(start_log, cat_names)
    conf.to_csv(os.path.join(OUT, "dp_uc38_confound_panel.csv"), index=False)

    # attribution guard -- written to disk so the report cannot forget it
    pd.DataFrame([dict(
        constraint="pitch_call_attribution",
        status="NOT OBSERVABLE",
        detail=("Statcast carries no PitchCom sender / pitch-call attribution field. "
                "This build measures WHAT WAS THROWN at the pitcher x catcher grain. "
                "It CANNOT distinguish a pitch Nola called from a pitch Stubbs called. "
                "Any narrative attributing a mix change to a specific person is "
                "unsupported by this data product."),
        governed_by="UC38 G4 / 03_governance.md AT-1")]).to_csv(
        os.path.join(OUT, "dp_uc38_attribution_guard.csv"), index=False)

    print("\n[8/8] figures, DQ, manifest")
    figs = make_figures(mix_c, panel_season, start_log, cat_names, seq_window)

    pd.DataFrame([dict(
        source=os.path.join(PHIL_DIR, "phils_*.parquet"),
        entity_lock="pitcher == 605400",
        filters="game_type=='R'; dedup game_pk+at_bat_number+pitch_number",
        rows=len(nola), games=int(nola.game_pk.nunique()),
        seasons=f"{int(nola.game_year.min())}-{int(nola.game_year.max())}",
        max_game_date=str(as_of.date()), game_day=GAME_DAY,
        woba_constants=WOBA_CSV or "MISSING",
        manual_carry_in=("Tonight's start PHI@SEA 2026-08-26 and the Stubbs pairing are "
                         "DPO prose, not a posted lineup — confirm pre-game"),
    )]).to_csv(os.path.join(OUT, "dp_uc38_freshness_manifest.csv"), index=False)
    pd.DataFrame(DQ).to_csv(os.path.join(OUT, "dp_uc38_dq_scorecard.csv"), index=False)

    stubbs_car = panel_career[panel_career.catcher_id == STUBBS]
    headlines = dict(
        as_of=str(as_of.date()), game_day=GAME_DAY,
        recent_n_starts=RECENT_N_STARTS,
        catchers_found=int(len(cat_names)),
        stubbs_career_pitches=int(stubbs_car.total_pitches.iat[0]) if len(stubbs_car) else 0,
        stubbs_career_games=int(stubbs_car.uq_games.iat[0]) if len(stubbs_car) else 0,
        stubbs_career_woba=float(stubbs_car.woba.iat[0]) if len(stubbs_car) else None,
        figures=[os.path.basename(f) for f in figs],
        attribution_constraint="pitch-call attribution NOT OBSERVABLE (G4)",
    )
    with open(os.path.join(OUT, "dp_uc38_headlines.json"), "w") as fh:
        json.dump(headlines, fh, indent=2, default=str)

    fails = [d for d in DQ if d["severity"] == "FAIL"]
    print("\n" + "=" * 78)
    print(f"DONE · {len(os.listdir(OUT))} files in ./out · "
          f"{len(fails)} DQ FAIL / {len([d for d in DQ if d['severity']=='WARN'])} WARN")
    print("=" * 78)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
