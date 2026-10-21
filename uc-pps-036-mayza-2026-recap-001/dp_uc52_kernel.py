"""
dp_uc52_kernel.py — governed kernel for UC #52 / uc-pps-036
"The Sheriff of the Phillies Bullpen — Tim Mayza's 2026 Recap"

INHERITANCE POLICY (control-plane 03_governance.md §0, Rule-1):
  * Section A  — INHERITED BY IMPORT, sha256-pinned, never copied:
      dp_uc51_kernel (uc-pps-035) and, through it, K49 / K50 / K48 / K44 / barrel_rate.py:
        nresults, whiff_rate, chase_rate, putaway_rate, hard_hit_rate, pitch_mix (K44) · runs_created,
        house_percentile (KP-1), season_recap (SR-1) (K48) · load_phils_cols (LP-1), context floors (K49) ·
        xwoba_pa (XW-1, K50) · barrel_rate (BR-1) · career_frame_mlb (CF-2b, K51) · extract (IX-1, K51)
  * Section A2 — INHERITED BY SOURCE-PINNED EXTRACTION (IX-1, second use):
        inds            ← Baseball Functions.ipynb   (client's indicator function; HP family only)
        tm_success_rate ← July 2026.ipynb, cell 137   (client's "Tim Mayza Success Rate"; HP-13 only)
  * Section B  — NON-BREAKING GENERALIZATION:
        CF-2c career_frame_ext — CF-2b plus EXTRA_COLS (release point, spin axis, arm angle, xSLG, distance)
              joined by (pitcher, PITCH_KEY) from the subject's own file and the house log (EN-2).
  * Section C  — NEW to this UC, PROVISIONAL (specs in 03 §2, written before code):
        QA-1 quick_ab_rate        — "two strikes or a ground ball within the first three pitches"
        BS-1 bullet_slider        — pitcher-season slider with |HB| <= 4.0 in and |IVB| <= 4.0 in
        DS-1 delivery_distance    — z-scored Euclidean distance on release x/z, extension, primary FB velo/HB/IVB
        RP-1 role_from_starts     — reliever = starts <= 20% of games (start = first Phillies pitcher of the game)

Data plane    : C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB
Control plane : C:\\Users\\Kellen\\OneDrive\\Documents\\Agents for Data Products
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

__version__ = "1.0.0"
_HERE = Path(__file__).resolve().parent
for _p in [os.environ.get("MLB_DATA_ROOT"), str(_HERE), r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]:
    if _p and (Path(_p) / "dp_uc51_kernel.py").exists() and _p not in sys.path:
        sys.path.insert(0, _p)
import dp_uc51_kernel as K51  # noqa: E402

K49, K50, K48, K44 = K51.K49, K51.K50, K51.K48, K51.K44
ROOT = K51.ROOT
PIN = {"dp_uc51_kernel.py": "4845bae228615bf2322532287015712f3b5235252f20c2f82929d53d70b0f555"}


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def assert_lineage() -> dict:
    out = {}
    for f, h in PIN.items():
        got = sha(ROOT / f)
        assert got == h, f"{f} drifted ({got[:12]} != {h[:12]})"
        out[f] = got
    out.update(K51.assert_lineage())
    return out


# ---- Section A: inherited names ------------------------------------------------------------
PITCH_KEY = K51.PITCH_KEY
nresults, whiff_rate, chase_rate = K44.nresults, K44.whiff_rate, K44.chase_rate
putaway_rate, hard_hit_rate, pitch_mix = K44.putaway_rate, K44.hard_hit_rate, K44.pitch_mix
runs_created, house_percentile, season_recap = K48.runs_created, K48.house_percentile, K48.season_recap
load_phils_cols, xwoba_pa, barrel_rate = K49.load_phils_cols, K50.xwoba_pa, K51.barrel_rate
PHILLIES_RED, PHILLIES_NAVY, PHILLIES_BLUE, PHILLIES_CREAM = K51.PHILLIES_RED, K51.PHILLIES_NAVY, K51.PHILLIES_BLUE, K51.PHILLIES_CREAM
NEUTRAL_GRAY, LIGHT_GRAY = K51.NEUTRAL_GRAY, K51.LIGHT_GRAY
KP_MIN_PA = K49.KP_MIN_PA                  # 100 PA: house pitcher-season floor (KP-1)
CONTEXT_MIN_PITCHES = K49.CONTEXT_MIN_PITCHES   # 150 pitches (CX-1)
POSTSEASON_TYPES = K49.POSTSEASON_TYPES

# ---- Section A2: IX-1 extractions (client functions, HP family only) ------------------------
_IND = K51.extract("Baseball Functions.ipynb", ["inds"])
_TMS = K51.extract("July 2026.ipynb", ["tm_success_rate"])
inds, tm_success_rate = _IND["inds"], _TMS["tm_success_rate"]

# ---- Subject (entity lock by MLBAM id; names only to reproduce the client's frames) ----------
SUBJECT_ID = 641835                        # Tim Mayza, LHP (resolved from data at bid time)
SUBJECT_NAME = "Mayza, Tim"
SUBJECT_DISPLAY = "Tim Mayza"
SUBJECT_FILE = "mayza.parquet"             # pitcher-keyed pull: TOR/NYY/PIT 2017-2025
SEASON = 2026
FIRST_APPEARANCE = "2026-03-28"
LAST_REGULAR_APPEARANCE = "2026-09-25"
ANCHOR_GAME_DATE = "2026-10-01"            # max game_date in phils_2026.parquet at build time (pinned)
NICKNAME = "The Sheriff"                   # carry-in CI-5 (client), display only
EXTRA_COLS = ["release_pos_x", "release_pos_z", "spin_axis", "arm_angle",
              "estimated_slg_using_speedangle", "hit_distance_sc", "launch_speed_angle",
              "woba_value", "woba_denom"]
HOUSE_COLS = K49.COLS + EXTRA_COLS
FB_TYPES = ("FF", "SI")
SL_TYPES = ("SL",)                          # Mayza's breaking ball is tagged SL; ST/SV are separate shapes


def load_house(years=range(2015, 2027)) -> pd.DataFrame:
    """LP-1 with EXTRA_COLS: Phillies pitching role, regular season, wOBA weights applied (K44)."""
    ph = load_phils_cols(years=years, role="pitching", regular_only=True, cols=HOUSE_COLS)
    assert ph.game_date.max() <= ANCHOR_GAME_DATE, "anchor drift: house log runs past the pinned anchor"
    return ph


def career_frame_ext(ph: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """CF-2c. CF-2b (regular season, MLB games, own name) + EXTRA_COLS by (pitcher, PITCH_KEY) (EN-2).
    Source order for extras: house log first (Phillies games), then the subject's own file."""
    df, receipt, milb = K51.career_frame_mlb(SUBJECT_ID, SUBJECT_FILE, SUBJECT_NAME, SUBJECT_DISPLAY, ph=ph)
    assert len(milb) == 0, f"CF-2b dropped {len(milb)} non-MLB rows; record in 04 before proceeding"
    key = ["pitcher"] + PITCH_KEY
    own = pd.read_parquet(ROOT / "data" / "opponents" / SUBJECT_FILE)
    own = own[own.pitcher == SUBJECT_ID][key + [c for c in EXTRA_COLS if c in own.columns]]
    hse = ph[ph.pitcher == SUBJECT_ID][key + EXTRA_COLS]
    ext = pd.concat([hse, own], ignore_index=True).drop_duplicates(subset=key, keep="first")
    df = df.drop(columns=[c for c in EXTRA_COLS if c in df.columns]).merge(ext, on=key, how="left")
    assert df.duplicated(subset=key).sum() == 0, "EN-2 fan-out"
    return df, receipt


def woba_statcast(level, df: pd.DataFrame) -> pd.DataFrame:
    """WB-1 (basis companion of XW-1, not a new KPI): actual wOBA on XW-1's own rows and denominator
    (sum woba_value / sum woba_denom over PA ends with woba_denom > 0). Exists so xwOBA is only ever compared
    with an actual on the same basis. House wOBA (K44 nresults: FanGraphs weights over every PA, errors as outs)
    stays the basis for ranks."""
    if isinstance(level, str):
        level = [level]
    pa = df[df.woba_denom.fillna(0) > 0]
    out = pa.groupby(level, as_index=False).agg(ws_num=("woba_value", "sum"), ws_den=("woba_denom", "sum"))
    out["woba_sc"] = out.ws_num / out.ws_den
    return out


# ---- Section C: new, provisional ----------------------------------------------------------
STRIKEOUT_EVENTS = ("strikeout", "strikeout_double_play")


def quick_ab_rate(level, df: pd.DataFrame, max_pitch: int = 3) -> pd.DataFrame:
    """QA-1. Share of completed PAs in which, within the first `max_pitch` pitches, the pitcher either
    (a) reaches a two-strike count (post-pitch count; a strikeout on pitch <= max_pitch counts) or
    (b) gets a ground ball in play. Denominator: PAs whose last pitch carries a PA-ending event.
    Columns: qa_pas, qa_2k, qa_gb, qa_success, quick_ab_rate, qa_2k_rate, qa_gb_rate."""
    if isinstance(level, str):
        level = [level]
    pa_key = ["game_pk", "at_bat_number"]
    d = df.sort_values(pa_key + ["pitch_number"]).copy()
    nxt = d.groupby(pa_key).strikes.shift(-1)
    last = nxt.isna()
    k_end = d.events.isin(STRIKEOUT_EVENTS)
    adds = ((d.type == "S") & (d.strikes < 2)).astype(int)
    d["s_post"] = np.where(~last, nxt, np.where(k_end, 3, d.strikes + adds))
    early = d.pitch_number <= max_pitch
    d["is_2k"] = (early & (d.s_post >= 2)).astype(int)
    d["is_gb"] = (early & (d.type == "X") & (d.bb_type == "ground_ball")).astype(int)
    d["ends"] = (last & d.events.notna()).astype(int)
    pa = d.groupby(level + pa_key, as_index=False).agg(two_k=("is_2k", "max"), gb=("is_gb", "max"), ends=("ends", "max"))
    pa = pa[pa.ends == 1]
    pa["success"] = ((pa.two_k == 1) | (pa.gb == 1)).astype(int)
    out = pa.groupby(level, as_index=False).agg(qa_pas=("success", "size"), qa_2k=("two_k", "sum"),
                                                qa_gb=("gb", "sum"), qa_success=("success", "sum"))
    out["quick_ab_rate"] = out.qa_success / out.qa_pas
    out["qa_2k_rate"] = out.qa_2k / out.qa_pas
    out["qa_gb_rate"] = out.qa_gb / out.qa_pas
    return out


BS_MAX_HB_IN = 4.0
BS_MAX_IVB_IN = 4.0
BS_MIN_PITCHES = 50


def bullet_slider(ph: pd.DataFrame, extra: pd.DataFrame | None = None, types=SL_TYPES) -> pd.DataFrame:
    """BS-1. Pitcher-season slider shape (inches, catcher view: pfx * 12) and the bullet flag:
    mean |HB| <= 4.0 in AND mean |IVB| <= 4.0 in, min 50 sliders. Also carries mean spin axis and velo.
    Population: LHP pitcher-seasons in `ph` (+ `extra` rows, e.g. the subject's career)."""
    d = pd.concat([ph, extra], ignore_index=True) if extra is not None else ph
    d = d[(d.p_throws == "L") & d.pitch_type.isin(types)]
    g = d.groupby(["pitcher", "game_year"], as_index=False).agg(
        player_name=("player_name", "last"), sliders=("pitch_type", "size"),
        hb_in=("pfx_x", lambda s: 12 * s.mean()), ivb_in=("pfx_z", lambda s: 12 * s.mean()),
        spin_axis=("spin_axis", "mean"), velo=("release_speed", "mean"))
    g = g[g.sliders >= BS_MIN_PITCHES].copy()
    g["bullet"] = (g.hb_in.abs() <= BS_MAX_HB_IN) & (g.ivb_in.abs() <= BS_MAX_IVB_IN)
    return g.round(2)


def primary_fastball(df: pd.DataFrame) -> str:
    fb = df[df.pitch_type.isin(FB_TYPES)].pitch_type.value_counts()
    return fb.index[0] if len(fb) else None


DS_FEATURES = ["rel_x", "rel_z", "ext", "fb_velo", "fb_hb_in", "fb_ivb_in"]


def delivery_table(d: pd.DataFrame, min_pitches: int = CONTEXT_MIN_PITCHES) -> pd.DataFrame:
    """DS-1 inputs, one row per LHP pitcher-season (min 150 pitches): release x/z, extension (all pitches),
    primary fastball (FF or SI, whichever he threw more) velo, HB and IVB in inches."""
    d = d[d.p_throws == "L"]
    rows = []
    for (pid, yr), g in d.groupby(["pitcher", "game_year"]):
        if len(g) < min_pitches:
            continue
        pfb = primary_fastball(g)
        if pfb is None:
            continue
        f = g[g.pitch_type == pfb]
        rows.append(dict(pitcher=pid, game_year=yr, player_name=g.player_name.iloc[-1], pitches=len(g),
                         rel_x=g.release_pos_x.mean(), rel_z=g.release_pos_z.mean(), ext=g.release_extension.mean(),
                         primary_fb=pfb, fb_velo=f.release_speed.mean(), fb_hb_in=12 * f.pfx_x.mean(),
                         fb_ivb_in=12 * f.pfx_z.mean()))
    return pd.DataFrame(rows).dropna(subset=DS_FEATURES)


def delivery_distance(tab: pd.DataFrame, target_pitcher: int = SUBJECT_ID, target_year: int = SEASON) -> pd.DataFrame:
    """DS-1. z-score each feature over the population, Euclidean distance to the target season.
    Returns every other pitcher's single nearest season, sorted ascending."""
    z = tab.copy()
    for c in DS_FEATURES:
        z[c + "_z"] = (z[c] - z[c].mean()) / z[c].std(ddof=0)
    t = z[(z.pitcher == target_pitcher) & (z.game_year == target_year)]
    assert len(t) == 1, "DS-1: target season missing from the population"
    zc = [c + "_z" for c in DS_FEATURES]
    z["distance"] = np.sqrt(((z[zc] - t[zc].values[0]) ** 2).sum(axis=1))
    o = z[z.pitcher != target_pitcher].sort_values("distance").drop_duplicates("pitcher")
    return o.reset_index(drop=True)


def starts_by_game(ph: pd.DataFrame) -> pd.DataFrame:
    """RP-1 helper. The starter of each Phillies game = pitcher of the first pitch (inning, at_bat, pitch)."""
    first = ph.sort_values(["game_pk", "inning", "at_bat_number", "pitch_number"]).drop_duplicates("game_pk")
    return first[["game_pk", "pitcher"]].assign(is_start=1)


def house_pitcher_seasons(ph: pd.DataFrame) -> pd.DataFrame:
    """Phillies pitcher-seasons (regular season) with results, runs on watch, games, starts and RP-1 role."""
    lvl = ["pitcher", "game_year", "p_throws"]
    res = nresults(lvl, ph)
    g = ph.groupby(lvl, as_index=False).agg(games=("game_pk", "nunique"), player_name=("player_name", "last"))
    st = starts_by_game(ph)
    s = ph[["pitcher", "game_year", "game_pk"]].drop_duplicates().merge(st, on=["game_pk", "pitcher"], how="left")
    s = s.groupby(["pitcher", "game_year"], as_index=False).agg(starts=("is_start", "sum"))
    rc = runs_created(lvl, ph)
    out = res.merge(g, on=lvl).merge(s, on=["pitcher", "game_year"], how="left").merge(rc, on=lvl, how="left")
    out["starts"] = out.starts.fillna(0).astype(int)
    out["role"] = np.where(out.starts <= 0.2 * out.games, "RP", "SP")
    out["rc_per_gm"] = out.runs_created / out.games
    return out
