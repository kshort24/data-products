"""
dp_uc53_kernel.py - governed kernel for UC #53 / uc-pps-037
"The Full Ride - Jose Alvarado's 2026, and five-plus years in red pinstripes"

INHERITANCE POLICY (control-plane 03_governance.md §0, Rule-1):
  * Section A - INHERITED BY IMPORT, sha256-pinned, never copied:
      dp_uc52_kernel (uc-pps-036) and, through it, dp_uc51_kernel -> K49 / K50 / K48 / K44 / barrel_rate:
        nresults, whiff_rate, chase_rate, putaway_rate, hard_hit_rate, pitch_mix (K44) - runs_created, house_percentile,
        signature_verdict + strength_from_signatures (PA-1, K48) - load_phils_cols (LP-1), game_score (GS-1) (K49) -
        xwoba_pa (XW-1, K50) - barrel_rate (BR-1) - career_frame_mlb (CF-2b, K51) - woba_statcast (WB-1),
        house_pitcher_seasons + RP-1 role (K52)
      cumulative_metric.py (house module CM-1): cumulative_frame, fig_cumulative_metric
  * Section B - NON-BREAKING GENERALIZATION:
      CF-2d career_frame_for - CF-2c (K52) with the subject passed in, not read from K52's module constants.
      RP-1t tenure_role - RP-1 at the pitcher x span grain (starts <= 20% of games over the span).
  * Section C - NEW to this UC, PROVISIONAL (specs in 03 §2, written before code):
      OD-1 outing_bands - each regular-season appearance banded by runs on watch: clean (0) / dented (1) / blow-up (>= 2)
      DB-1 decline-or-blip ledger - 8 pre-registered signatures scored with PA-1 against a pooled 2022-24 baseline.
           REGISTERED 2026-10-18 ~11:00 ET, before any 2026 rate was computed by this UC (only pitch and game counts
           had been read). Disclosure: the MLB.com carry-in CI-6 (mid-season Statcast figures) was read at T0.
  * CSW% is a LOCKED house term (uc-pps-018 03: (called strikes + whiffs) / pitches); computed inline, not new.

Data plane    : C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB   (parquet, parent kernels)
Control plane : C:\\Users\\Kellen\\OneDrive\\Documents\\Agents for Data Products (this file, out/, receipts)
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

__version__ = "1.0.0"
HERE = Path(__file__).resolve().parent
UC52_DIR = HERE.parent / "uc-pps-036-mayza-2026-recap-001"
_MLB_CANDIDATES = [os.environ.get("MLB_DATA_ROOT"), str(HERE.parent.parent.parent / "Python Scripts" / "MLB"),
                   r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]
for _p in _MLB_CANDIDATES:
    if _p and (Path(_p) / "dp_uc51_kernel.py").exists():
        os.environ.setdefault("MLB_DATA_ROOT", _p)
        if _p not in sys.path:
            sys.path.insert(0, _p)
        break
if str(UC52_DIR) not in sys.path:
    sys.path.insert(0, str(UC52_DIR))
import dp_uc52_kernel as K52  # noqa: E402
import cumulative_metric as CM  # noqa: E402

K51, K49, K50, K48, K44 = K52.K51, K52.K49, K52.K50, K52.K48, K52.K44
ROOT = K52.ROOT                                   # MLB data plane
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
PIN = {UC52_DIR / "dp_uc52_kernel.py": "3667f8028acd9974412d2d1a64cda3c6c335e7495f9d803a4b8cb29afebaa284",
       ROOT / "cumulative_metric.py": "a28887406d98880993baa67aca5b3246db23e99615f3ffab28b1fb4ddf526365"}


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def assert_lineage() -> dict:
    out = {}
    for f, h in PIN.items():
        got = sha(f)
        assert got == h, f"{Path(f).name} drifted ({got[:12]} != {h[:12]})"
        out[Path(f).name] = got
    out.update(K52.assert_lineage())
    return out


# ---- Section A: inherited names --------------------------------------------------------------
PITCH_KEY = K52.PITCH_KEY
nresults, whiff_rate, chase_rate, putaway_rate = K44.nresults, K44.whiff_rate, K44.chase_rate, K44.putaway_rate
hard_hit_rate, pitch_mix, WHIFFS, SWINGS = K44.hard_hit_rate, K44.pitch_mix, K44.WHIFFS, K44.SWINGS
runs_created, house_percentile = K48.runs_created, K48.house_percentile
signature_verdict, strength_from_signatures = K48.signature_verdict, K48.strength_from_signatures
load_phils_cols, game_score, xwoba_pa, barrel_rate = K49.load_phils_cols, K49.game_score, K50.xwoba_pa, K51.barrel_rate
woba_statcast, house_pitcher_seasons = K52.woba_statcast, K52.house_pitcher_seasons
cumulative_frame, fig_cumulative_metric = CM.cumulative_frame, CM.fig_cumulative_metric
PHILLIES_RED, PHILLIES_NAVY, PHILLIES_BLUE, PHILLIES_CREAM = K52.PHILLIES_RED, K52.PHILLIES_NAVY, K52.PHILLIES_BLUE, K52.PHILLIES_CREAM
NEUTRAL_GRAY, LIGHT_GRAY = K52.NEUTRAL_GRAY, K52.LIGHT_GRAY
KP_MIN_PA, CONTEXT_MIN_PITCHES, POSTSEASON_TYPES = K52.KP_MIN_PA, K52.CONTEXT_MIN_PITCHES, K52.POSTSEASON_TYPES
EXTRA_COLS, HOUSE_COLS = K52.EXTRA_COLS, K52.HOUSE_COLS

# ---- Subject (entity lock by MLBAM id + pitching role; names only to reproduce the client frame) --
SUBJECT_ID = 621237                    # Jose Alvarado, LHP (resolved from data at bid time; uc-pps-016)
SUBJECT_NAME = "Alvarado, José"        # client's pn
SUBJECT_DISPLAY = "José Alvarado"
SUBJECT_FILE = "alvarado.parquet"      # pitcher-keyed pull: TB 2017-2020
SEASON = 2026
TENURE = list(range(2021, 2027))       # Phillies regular seasons
FIRST_APPEARANCE = "2026-03-28"
LAST_REGULAR_APPEARANCE = "2026-09-26"
ANCHOR_GAME_DATE = "2026-10-01"        # max game_date in phils_2026.parquet at build time (pinned)
NICKNAME = "Mr. Punchie"               # carry-in CI-8 (client), display only
CSW_CALLED = "called_strike"


def load_house(years=range(2015, 2027), regular_only=True) -> pd.DataFrame:
    """LP-1 with K52 HOUSE_COLS. Pitching role (excludes ENT-1 rows where 621237 appears as an opposing pitcher)."""
    ph = load_phils_cols(years=years, role="pitching", regular_only=regular_only, cols=HOUSE_COLS)
    assert ph.game_date.max() <= ANCHOR_GAME_DATE, "anchor drift: house log runs past the pinned anchor"
    return ph


def career_frame_for(ph: pd.DataFrame, pid=SUBJECT_ID, file=SUBJECT_FILE, name=SUBJECT_NAME, display=SUBJECT_DISPLAY):
    """CF-2d. CF-2c (K52.career_frame_ext) with the subject as arguments. CF-2b (regular season, MLB games, own name)
    + EXTRA_COLS by (pitcher, PITCH_KEY), house log first, then the subject's own file. Returns (frame, receipt, milb)."""
    df, receipt, milb = K51.career_frame_mlb(pid, file, name, display, ph=ph)
    key = ["pitcher"] + PITCH_KEY
    own = pd.read_parquet(ROOT / "data" / "opponents" / file)
    own = own[own.pitcher == pid][key + [c for c in EXTRA_COLS if c in own.columns]]
    hse = ph[ph.pitcher == pid][key + EXTRA_COLS]
    ext = pd.concat([hse, own], ignore_index=True).drop_duplicates(subset=key, keep="first")
    df = df.drop(columns=[c for c in EXTRA_COLS if c in df.columns]).merge(ext, on=key, how="left")
    assert df.duplicated(subset=key).sum() == 0, "EN-2 fan-out"
    return df, receipt, milb


def tenure_role(hs: pd.DataFrame, years) -> pd.DataFrame:
    """RP-1t. RP-1 at the pitcher x span grain: games and starts summed over `years`; RP when starts <= 20% of games."""
    t = hs[hs.game_year.isin(years)].groupby("pitcher", as_index=False).agg(
        player_name=("player_name", "last"), games=("games", "sum"), starts=("starts", "sum"),
        seasons=("game_year", "nunique"), first=("game_year", "min"), last=("game_year", "max"))
    t["role_span"] = np.where(t.starts <= 0.2 * t.games, "RP", "SP")
    return t


def csw(level, df: pd.DataFrame) -> pd.DataFrame:
    """CSW% (locked house term): (called strikes + whiffs) / pitches."""
    if isinstance(level, str):
        level = [level]
    d = df.assign(_cs=(df.description == CSW_CALLED).astype(int), _wh=df.description.isin(WHIFFS).astype(int))
    o = d.groupby(level, as_index=False).agg(pitches_csw=("_cs", "size"), cs=("_cs", "sum"), whiffs_csw=("_wh", "sum"))
    o["csw_rate"] = (o.cs + o.whiffs_csw) / o.pitches_csw
    o["called_strike_rate"] = o.cs / o.pitches_csw
    return o


# CM-1a: corrected wOBA spec for cumulative_frame (CM-D1: the module's "woba" numerator sums woba_value on PA ends
# whose woba_denom is 0 / NaN - intentional walks carry 0.4, sac bunts 0.9 - so the running line runs high).
# Passed as a metric dict (supported API), so the pinned module is not edited. Endpoints reconcile to WB-1.
WOBA_SC_SPEC = dict(num=lambda p: p["woba_value"].fillna(0).where(p["woba_denom"].fillna(0) > 0, 0),
                    den=lambda p: p["woba_denom"].fillna(0), fmt=".3f", label="wOBA", min_den=25)


# ---- Section C: OD-1 -------------------------------------------------------------------------
OD_BANDS = ("clean", "dented", "blow-up")


def outing_bands(gs: pd.DataFrame) -> pd.DataFrame:
    """OD-1. One row per regular-season appearance (GS-1 output). Band by runs on watch `r`:
    clean = 0, dented = 1, blow-up >= 2. NaN r (no PA ended) -> clean (0 runs on watch)."""
    g = gs.copy()
    g["r"] = g.r.fillna(0)
    g["band"] = np.select([g.r == 0, g.r == 1], ["clean", "dented"], default="blow-up")
    return g


def band_rates(gb: pd.DataFrame, by="game_year") -> pd.DataFrame:
    t = gb.groupby([by, "band"]).size().unstack(fill_value=0).reindex(columns=list(OD_BANDS), fill_value=0)
    t["apps"] = t.sum(axis=1)
    for b in OD_BANDS:
        t[b + "_rate"] = t[b] / t.apps
    t["runs"] = gb.groupby(by).r.sum()
    return t.reset_index()


def damage_concentration(gb: pd.DataFrame, k: int = 5) -> float:
    """Share of a season's runs on watch that came in its k worst appearances (by r, then lowest game score)."""
    tot = gb.r.sum()
    if tot == 0:
        return 0.0
    worst = gb.sort_values(["r", "game_score"], ascending=[False, True]).head(k)
    return float(worst.r.sum() / tot)


# ---- Section C: DB-1 (PRE-REGISTERED; changing any row after publication is BREAKING) ----------
DB_BASELINE_YEARS = (2022, 2023, 2024)  # three full Phillies seasons with the cutter; 2021 precedes it as a
                                        # primary pitch, 2025 is a 28-game partial season around CI-3
DB_SENSITIVITY_YEARS = (2021, 2022, 2023, 2024, 2025)
# id, hypothesis, metric key, direction the hypothesis predicts (+1 up / -1 down), threshold (PA-1), plain label
DB_SIGNATURES = [
    ("D1", "decline", "si_velo",      -1, 1.0,   "Sinker velocity (mph)"),
    ("D2", "decline", "fc_velo",      -1, 1.0,   "Cutter velocity (mph)"),
    ("D3", "decline", "fc_whiff",     -1, 0.06,  "Cutter whiff rate"),
    ("D4", "decline", "chase_rate",   -1, 0.04,  "Chase rate (all pitches)"),
    ("D5", "decline", "in_zone_rate", -1, 0.03,  "Zone rate (all pitches)"),
    ("D6", "decline", "k_minus_bb",   -1, 0.05,  "K% minus BB%"),
    ("B1", "blip",    "luck_gap",     +1, 0.025, "wOBA minus xwOBA, same basis (bad luck)"),
    ("B2", "blip",    "damage_top5",  +1, 0.10,  "Share of runs on watch in his 5 worst outings"),
]
DB_RULE = ("decline SUPPORTED/STRONG and blip not -> DECLINE (move on) | blip SUPPORTED/STRONG and decline not -> "
           "BLIP (one more year) | both -> DECLINE WITH NOISE | neither -> UNRESOLVED")


def db1_ledger(base: dict, now: dict) -> tuple[pd.DataFrame, dict]:
    rows = []
    for sid, hyp, key, direction, thr, label in DB_SIGNATURES:
        b, n = base.get(key), now.get(key)
        v = signature_verdict(b, n, direction, thr)
        rows.append(dict(sig=sid, hypothesis=hyp, metric=key, label=label, direction=direction, threshold=thr,
                         baseline=b, season=n, delta=None if b is None or n is None else n - b, verdict=v))
    t = pd.DataFrame(rows)
    dec = strength_from_signatures(t[t.hypothesis == "decline"].verdict.tolist())
    bl = strength_from_signatures(t[t.hypothesis == "blip"].verdict.tolist())
    D, B = dec in ("STRONG", "SUPPORTED"), bl in ("STRONG", "SUPPORTED")
    call = "DECLINE WITH NOISE" if D and B else "DECLINE" if D else "BLIP" if B else "UNRESOLVED"
    return t, dict(decline=dec, blip=bl, call=call, rule=DB_RULE)
