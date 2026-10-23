"""
dp_uc56_kernel.py - governed kernel for UC #56 / uc-pos-021
"We Really Do Love Sosa - Edmundo Sosa's 2026 season recap (and possibly his Phillies tenure)"

Lives in the CONTROL PLANE folder per the RFP ("all the output and governance stuff in the subfolder"):
  Agents for Data Products/data-products/uc-pos-021-sosa-2026-recap-001/
The DATA PLANE (MLB repo: data/, phillies_dp, dp_uc55_kernel.py, barrel_rate.py, Baseball Functions.ipynb) is READ ONLY.

INHERITANCE POLICY (03_governance.md §0, Rule-1):
  * Section A - INHERITED BY IMPORT, sha256-pinned, never copied:
      dp_uc55_kernel (uc-pos-020, K55 -> K54 -> K40/K34/K53 chain + K40a; 14 pins re-assert through it):
        nresults_unrounded, pa_rows, chase/whiff/swing/HH/barrel fixes, CR-1, XW-1, RF-2/RF-2x, KP-1, PA-1,
        two_prop_z, CM-1 cumulative frames, TR-1 tr1_metrics/tr1_ledger, CC-1 take_reference/chase_cost,
        ooz_whiff_rate, zone_swing_whiff, hitter_seasons, BT-1 bat_tracking, ER-1 (pa_atoms, er1_*), brand.
      dp_uc46_kernel (uc-pos-017 directional family, CONDITIONALLY CERTIFIED): build_bip, pull_air_rate (v1.1.0,
        O-7 closed), assert_spray_convention.
      barrel_rate.py (client function, pinned through the K54 chain; pinned again here for the HP family).
  * Section B - NON-BREAKING GENERALIZATION:
      client_frame(name)  = K54.client_frame generalized from a module constant to a parameter.
      ev_profile          = UC27 `ev90` precedent + the client's ev_mu/ev50/ev_max definitions (GL-1: EV50 = MEDIAN EV,
                            the client's definition; Statcast's public EV50 is the mean of the hardest 50% - disclosed).
      asb_first_game      = the UC55 schedule-gap rule (>= 3 days in July) as a function.
  * Section C - NEW to this UC, PROVISIONAL (pre-registered in the BID 2026-10-23 14:04 ET):
      OZ-1  out-of-zone damage: OZ-BA vs OZ-xBA on PAs ending out of the zone, + OZ contact; call per season.
      WA-1  walkaway number: carry-in comp band + six decline flags (DF) -> AAV ceiling and term.
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

__version__ = "1.0.0"
HERE = Path(__file__).resolve().parent                                   # control-plane package folder
DP = HERE.parent                                                         # data-products/
_MLB_CANDIDATES = [os.environ.get("MLB_DATA_ROOT"),
                   str(HERE.parents[2] / "MLB"),                         # laptop VM mounts (~/mnt/MLB)
                   str(HERE.parents[2] / "Python Scripts" / "MLB"),      # Windows: Documents/Python Scripts/MLB
                   r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]
MLB = next(Path(p) for p in _MLB_CANDIDATES if p and (Path(p) / "dp_uc55_kernel.py").exists())
os.environ.setdefault("MLB_DATA_ROOT", str(MLB))
UC46_DIR = DP / "uc-pos-017-directional-hitting-family-001"
for _d in (MLB, UC46_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))
import dp_uc55_kernel as K55  # noqa: E402
import dp_uc46_kernel as K46  # noqa: E402

K54, K40a = K55.K54, K55.K40a
K40, K44, K51 = K54.K40, K54.K44, K54.K51
OUT = HERE / "out"
EDA_ROOT = HERE                                    # phillies_dp.eda.to_file(root=EDA_ROOT) -> eda/dp_uc56/
P = "dp_uc56_"
UC = "dp_uc56"
PIN = {
    MLB / "dp_uc55_kernel.py": "9bdcce59794e21aa0ddc6ce87ed273b8158fd7ab981fbd0eacbe1b1b79b2e5a8",
    UC46_DIR / "dp_uc46_kernel.py": "a45ac9a76395b2f82d235dddae77237090a1c8a03fb3ec1d6a9b8fd3c27f61b2",
    MLB / "barrel_rate.py": "6282f090394aaef89101085ede5fae4b77c4663da95ed4274fadbc0e455a185c",
}


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def assert_lineage() -> dict:
    out = {}
    for f, h in PIN.items():
        got = sha(f)
        assert got == h, f"{Path(f).name} drifted ({got[:12]} != {h[:12]})"
        out[Path(f).name] = got
    out.update(K55.assert_lineage())          # 14 more pins through K55 (K54 + K40a + 12 through K54)
    return out


# ---- Section A: inherited names -------------------------------------------------------------------------
PITCH_KEY, SWINGS, WHIFFS, NON_PA, NON_AB = K54.PITCH_KEY, K54.SWINGS, K54.WHIFFS, K54.NON_PA, K54.NON_AB
HIT_EV, BB_EV, K_EV, PITCH_GROUP = K54.HIT_EV, K54.BB_EV, K54.K_EV, K54.PITCH_GROUP
_nresults_inherited, pa_rows, woba_weights = K54.nresults_unrounded, K54.pa_rows, K54.woba_weights
chase_rate_g, whiff_rate_fix, swing_rate = K54.chase_rate_g, K54.whiff_rate_fix, K54.swing_rate
ooz_whiff_rate, zone_swing_whiff = K54.ooz_whiff_rate, K54.zone_swing_whiff
hard_hit_rate_fix, barrel_rate_g, battedball_profile = K54.hard_hit_rate_fix, K54.barrel_rate_g, K54.battedball_profile
xwoba_pa, rolling_form, rolling_xwoba = K54.xwoba_pa, K54.rolling_form, K54.rolling_xwoba
house_percentile, signature_verdict, strength_from_signatures = K54.house_percentile, K54.signature_verdict, K54.strength_from_signatures
two_prop_z, cumulative_frame, cumulative_ops, woba_house_spec = K54.two_prop_z, K54.cumulative_frame, K54.cumulative_ops, K54.woba_house_spec
OBP_SPEC, SLG_SPEC = K54.OBP_SPEC, K54.SLG_SPEC
hitter_seasons, tr1_metrics, tr1_ledger, TR_SIGNATURES, TR_RULE = K54.hitter_seasons, K54.tr1_metrics, K54.tr1_ledger, K54.TR_SIGNATURES, K54.TR_RULE
take_reference, chase_cost, ooz_rows = K54.take_reference, K54.chase_cost, K54.ooz_rows
bat_tracking = K40.bat_tracking
pa_atoms, er1_segments, er1_null_crit, er1_power, split_gain = K55.pa_atoms, K55.er1_segments, K55.er1_null_crit, K55.er1_power, K55.split_gain
ER_MIN_SEG, ER_PERMS, ER_ALPHA, ER_SEED, ER_BAND = K55.ER_MIN_SEG, K55.ER_PERMS, K55.ER_ALPHA, K55.ER_SEED, K55.ER_BAND
build_bip, pull_air_rate, assert_spray_convention = K46.build_bip, K46.pull_air_rate, K46.assert_spray_convention
f3, pct = K54.f3, K54.pct
PHILLIES_RED, PHILLIES_NAVY, PHILLIES_BLUE, PHILLIES_CREAM = K54.PHILLIES_RED, K54.PHILLIES_NAVY, K54.PHILLIES_BLUE, K54.PHILLIES_CREAM
NEUTRAL_GRAY, LIGHT_GRAY = K54.NEUTRAL_GRAY, K54.LIGHT_GRAY

# ---- Subject (entity lock by MLBAM id; the name is used only to reproduce the client frame) ------------
SUBJECT_ID = 624641                     # Edmundo Sosa, bats R (resolved from data at bid time)
SUBJECT_NAME = "Sosa, Edmundo"          # client's pn
SUBJECT_DISPLAY = "Edmundo Sosa"
STL_FILE = "edmundo.parquet"            # SRC-5: data/opponents/, STL 2018-22, no bat tracking
SEASON = 2026
PHI_SEASONS = (2022, 2023, 2024, 2025, 2026)
BASELINE = (2023, 2024, 2025)           # SRC-6: 2022 PHI is 59 PA - shown, never a baseline
ANCHOR_GAME_DATE = "2026-10-01"
POSTSEASON_TYPES = ("F", "D", "L", "W")
CLIENT_POOL_YEARS = (2022, 2023, 2024, 2025, 2026)   # the client's `z.game_year > gy-5`
FB_TYPES = ("FF", "SI", "FC")
VELO_HI = 94.9                          # the house/client velocity split (UC55 HP-09: release_speed > 94.9)
POSITIONS = {"fielder_3": "1B", "fielder_4": "2B", "fielder_5": "3B", "fielder_6": "SS",
             "fielder_7": "LF", "fielder_8": "CF", "fielder_9": "RF"}
load_house = K55.load_house            # LP-1 with K55 COLS; asserts the pinned anchor


def subject_rows(pos: pd.DataFrame, game_types=("R",)) -> pd.DataFrame:
    s = pos[(pos.batter == SUBJECT_ID) & (pos.phillies_role == "batting") & pos.game_type.isin(game_types)]
    assert s.duplicated(PITCH_KEY).sum() == 0, "EN-2 fan-out on the subject"
    return s


def stl_rows(game_types=("R",)) -> pd.DataFrame:
    """SRC-5 context only: St. Louis seasons from the opponents file. Never pooled with Phillies rows in a rate."""
    a = pd.read_parquet(MLB / "data" / "opponents" / STL_FILE)
    a = a[(a.batter == SUBJECT_ID) & a.game_type.isin(game_types)].drop_duplicates(PITCH_KEY)
    return K54._prep(a)


# ---- Section B: generalizations -------------------------------------------------------------------------
def client_frame(pos_all: pd.DataFrame, name: str = SUBJECT_NAME) -> pd.DataFrame:
    """The client's `pd.concat([nphl[nphl.player_name == pn], pos[pos.player_name == pn]])`, reproduced:
    every opponent parquet (de-duped on PITCH_KEY within nphl only), then pos with NO game_type filter."""
    frames = []
    for f in sorted((MLB / "data" / "opponents").glob("*.parquet")):
        if not (pd.read_parquet(f, columns=["player_name"]).player_name == name).any():
            continue
        d = pd.read_parquet(f)
        frames.append(d[d.player_name == name].assign(_src=f.name))
    nphl = pd.concat(frames, ignore_index=True).drop_duplicates(PITCH_KEY, keep="first") if frames else pd.DataFrame()
    p = pos_all[pos_all.player_name == name].assign(_src="pos")
    return K54._prep(pd.concat([nphl, p], ignore_index=True, sort=False))


def ev_profile(level, df: pd.DataFrame) -> pd.DataFrame:
    """EV-1. Exit-velocity distribution on TRACKED balls in play (sensor-boundary standard: untracked BIP leave the
    denominator). ev_mu = mean (client `ev_mu`), ev50 = MEDIAN (client comment, GL-1), ev90 = 0.90 quantile
    (UC27 precedent), ev_max = max. n_ev carried beside every value."""
    level = [level] if isinstance(level, str) else list(level)
    b = df[(df.type == "X")].copy()
    b["launch_speed"] = pd.to_numeric(b.launch_speed, errors="coerce")
    b = b[b.launch_speed.notna()]
    g = b.groupby(level, as_index=False).agg(n_ev=("launch_speed", "size"), ev_mu=("launch_speed", "mean"),
                                            ev50=("launch_speed", "median"),
                                            ev90=("launch_speed", lambda x: x.quantile(0.90)),
                                            ev_max=("launch_speed", "max"))
    return g


def pull_air(level, df: pd.DataFrame) -> pd.DataFrame:
    """K46 pull_air_rate on the classifiable-BIP frame (asserts the spray convention before returning)."""
    level = [level] if isinstance(level, str) else list(level)
    if df[(df.type == "X") & df.hc_x.notna()].empty:
        return pd.DataFrame(columns=level + ["total_bips", "pull_airs", "pull_air_rate"])
    bip = build_bip(level, df)
    return pull_air_rate(level, bip)


def asb_first_game(season_rows: pd.DataFrame, year: int) -> pd.Timestamp:
    """The first game after the All-Star break: the largest July gap (>= 3 days) in the house schedule."""
    dates = pd.Series(sorted(pd.to_datetime(season_rows[(season_rows.game_year == year)].game_date).dt.normalize().unique()))
    jul = dates[(dates.dt.month == 7)]
    gaps = jul.diff().dt.days.fillna(0)            # D-1: an unfilled leading NaN made argmax return July 1
    assert gaps.max() >= 3, f"no All-Star gap found in July {year}"
    return pd.Timestamp(jul.iloc[int(gaps.to_numpy().argmax())])


def nresults_unrounded(level, df: pd.DataFrame, woba_w: pd.DataFrame) -> pd.DataFrame:
    """WB-2 (found by this UC's harness): the inherited K40/K54 `nresults_unrounded` weights EVERY event with 2026 constants
    when `game_year` is not in `level`, so a pooled multi-season wOBA mixes seasons on one year's weights. This wrapper keeps
    every inherited column and replaces only `woba` (pooled) with sum(per-season numerator) / sum(per-season denominator).
    Identical to the inherited function whenever `game_year` is in the level. Non-breaking for single-season grains."""
    level = [level] if isinstance(level, str) else list(level)
    z = _nresults_inherited(level, df, woba_w)
    if "game_year" in level or df.empty:
        return z
    zy = _nresults_inherited(level + ["game_year"], df, woba_w)
    den = zy.at_bats + zy.unint_walks + zy.sf + zy.hbp
    zy = zy.assign(_num=zy.woba.fillna(0) * den, _den=den)
    agg = zy.groupby(level, as_index=False)[["_num", "_den"]].sum()
    agg["woba_pooled"] = np.where(agg._den > 0, agg._num / agg._den, np.nan)
    z = z.drop(columns=["woba"]).merge(agg[level + ["woba_pooled"]], on=level, how="left").rename(columns={"woba_pooled": "woba"})
    return z


# ---- Section C: OZ-1 out-of-zone damage (bars pre-registered in the BID) -------------------------------
OZ_HOT, OZ_COLD = 0.030, -0.030


def oz_pa(df: pd.DataFrame) -> pd.DataFrame:
    """PAs whose final pitch was out of the zone (zone 11-14) with a pitch_type (AB-1)."""
    pa = pa_rows(df)
    return pa[(pa.zone > 9) & pa.pitch_type.notna()]


def oz1(level, df: pd.DataFrame) -> pd.DataFrame:
    level = [level] if isinstance(level, str) else list(level)
    o = oz_pa(df).copy()
    o["_ab"] = (~o.events.isin(NON_AB)).astype(float)
    o["_hit"] = o.events.isin(HIT_EV).astype(float)
    est = pd.to_numeric(o.estimated_ba_using_speedangle, errors="coerce")
    o["_xba"] = np.where(o.type.eq("X"), np.where(est.notna(), est, o._hit), 0.0) * o._ab
    o["_bip"] = o.type.eq("X").astype(float)
    g = o.groupby(level, as_index=False).agg(oz_pa=("events", "size"), oz_ab=("_ab", "sum"), oz_hits=("_hit", "sum"),
                                             oz_xhits=("_xba", "sum"), oz_bip=("_bip", "sum"))
    g["oz_ba"] = np.where(g.oz_ab > 0, g.oz_hits / g.oz_ab, np.nan)
    g["oz_xba"] = np.where(g.oz_ab > 0, g.oz_xhits / g.oz_ab, np.nan)
    g["oz_gap"] = g.oz_ba - g.oz_xba
    g["oz_call"] = np.select([g.oz_gap >= OZ_HOT, g.oz_gap <= OZ_COLD], ["RAN HOT", "RAN COLD"], "EARNED")
    return g


# ---- Section C: WA-1 walkaway number (inputs: carry-ins CI-3/CI-5; data: decline flags) ------------------
WA_FLOOR_M = 4.4                         # CI-3: 2026 salary ($M)
WA_COMPS = [  # CI-5, 2025-26 offseason utility deals (player, team, years, total $M, source)
    ("Amed Rosario", "NYY", 1, 2.5, "Bleacher Report FA tracker 2025-26"),
    ("Miguel Rojas", "LAD", 1, 5.5, "Bleacher Report FA tracker 2025-26"),
    ("Isiah Kiner-Falefa", "BOS", 1, 6.0, "AP via DC News Now / KRON4"),
    ("Willi Castro", "COL", 2, 12.8, "ESPN report headline (2-year, $12.8M)"),
]
WA_SALARY = {2022: 0.7156, 2023: 0.95, 2024: 1.7, 2025: 3.0, 2026: 4.4}   # CI-3 ($M)
DF_BARS = [  # (flag, metric, direction good, bar, label) - 2026 vs 2023-25 PHI mean (bat speed: 2024-25)
    ("DF-1", "bat_speed_mu", +1, 1.0, "Bat speed (mph)"),
    ("DF-2", "ev90", +1, 1.0, "EV90 (mph)"),
    ("DF-3", "hard_hit_rate", +1, 0.040, "Hard-hit rate"),
    ("DF-4", "barrel_rate", +1, 0.020, "Barrel / BIP"),
    ("DF-5", "xwoba", +1, 0.020, "xwOBA"),
    ("DF-6", "ooz_contact_rate", +1, 0.030, "Out-of-zone contact"),
]
WA_RULE = ("walkaway AAV = top CI-5 comp AAV rounded down to $0.5M; term <= 2 years if DF <= 2, "
           "1 year (+ club option) if DF >= 3; anything above = everyday money -> let him go")


def wa1(card: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    c = card.set_index("game_year")
    rows = []
    for fid, m, d, bar, lab in DF_BARS:
        base_years = [y for y in BASELINE if y in c.index and pd.notna(c.loc[y, m])]
        base = float(np.mean([c.loc[y, m] for y in base_years])) if base_years else np.nan
        v = float(c.loc[SEASON, m]) if SEASON in c.index else np.nan
        delta = (v - base) * d
        rows.append(dict(flag=fid, metric=m, label=lab, baseline_years="-".join(map(str, (base_years[0], base_years[-1]))) if base_years else "",
                         baseline=base, v2026=v, delta=v - base, bar=bar, flagged=bool(delta <= -bar)))
    t = pd.DataFrame(rows)
    aav = [tot / yrs for _, _, yrs, tot, _ in WA_COMPS]
    ceiling = np.floor(max(aav) * 2) / 2
    n = int(t.flagged.sum())
    term = "1 year (+ club option)" if n >= 3 else "up to 2 years"
    years = 1 if n >= 3 else 2
    return t, dict(floor=WA_FLOOR_M, ceiling=float(ceiling), comp_max_aav=float(max(aav)), comp_min_aav=float(min(aav)),
                   df_count=n, term=term, years=years, walkaway_total=float(ceiling * years), rule=WA_RULE)
