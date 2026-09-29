"""
dp_uc50_kernel.py -- governed kernel for UC #50 / uc-pos-018
"NL Wild Card Series, Game 1: the Phillies lineup vs Chris Sale"
PHI @ ATL · Truist Park · 2026-09-29

INHERITANCE POLICY (Rule-1; see 03_governance.md):
  * Section A -- INHERITED BY IMPORT, sha256-pinned, never copied:
      dp_uc44_kernel  (uc-pps-030)  get_stats / nresults / whiff_rate / chase_rate /
                                    pitch_mix / lhb_pitch_mix / rhb_pitch_mix /
                                    bb_type_by_level / hard_hit_rate / two_prop_z /
                                    apply_woba_weights / brand constants
      dp_uc46_kernel  (uc-pos-017)  build_bip / direction_rate / bb_type_profile /
                                    pull_air_rate  (certified directional family;
                                    lives in the CONTROL PLANE package folder)
      barrel_rate.py  (MLB root)    barrel_rate (house module, notebook-identical)
      dp_uc48_kernel  (uc-pps-033)  xwobacon, runs_created
  * Section B -- data access. BF-1 (batter frame) generalises the id-scan +
    precedence-dedup pattern of dp_uc49 CF-2 from one pitcher to a lineup of
    batters plus one opposing pitcher, in ONE pass over the opponent files.
  * Section C -- NEW to this UC (provisional, specified in 03 §2 before code):
      XW-1  xwoba_pa         PA-denominated xwOBA (BIP expected + non-BIP actual)
      HL-1  horizontal_band  Inner / Middle / Away relative to the batter
      LR-1  lhp_rank         client's Harper cut generalised: rank of one LHP among
                             every LHP a hitter has faced (>= min PA)
      TT-1  tto_split        results by time through the order (n_thruorder_pitcher)
      IC-1  index_card       the per-hitter card: a COMPOSITION of locked KPIs

Entity locks: MLBAM ids only. Names are used ONLY to reproduce the client's own
frames in the HP (human-parent) reconciliation family.

Data plane:    C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB
Control plane: C:\\Users\\Kellen\\OneDrive\\Documents\\Agents for Data Products
"""
from __future__ import annotations

import glob
import hashlib
import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import dp_uc44_kernel as K44  # noqa: E402
import dp_uc48_kernel as K48  # noqa: E402
import barrel_rate as BR      # noqa: E402

__version__ = "1.0.0"
ROOT = K44.ROOT
PITCH_KEY = ["game_pk", "at_bat_number", "pitch_number"]

# ----------------------------------------------------------------------------
# Control-plane import of the certified directional family (dp_uc46, uc-pos-017)
# ----------------------------------------------------------------------------
_CP_REL = Path("Agents for Data Products") / "data-products" / "uc-pos-017-directional-hitting-family-001" / "dp_uc46_kernel.py"
_CP_CANDIDATES = [
    os.environ.get("DP_CONTROL_PLANE"),
    str(ROOT.resolve().parent / _CP_REL),          # laptop VM: ~/mnt/MLB -> ~/mnt/Agents for Data Products
    str(ROOT.resolve().parent.parent / _CP_REL),   # Windows: Documents/Python Scripts/MLB -> Documents/Agents...
    str(Path(r"C:\Users\Kellen\OneDrive\Documents") / _CP_REL),
]


def _load_k46():
    for c in _CP_CANDIDATES:
        if not c:
            continue
        p = Path(c)
        if p.is_dir():
            p = p / "data-products" / "uc-pos-017-directional-hitting-family-001" / "dp_uc46_kernel.py"
        if p.exists():
            spec = importlib.util.spec_from_file_location("dp_uc46_kernel", p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod, p
    raise FileNotFoundError("dp_uc46_kernel (uc-pos-017) not reachable; set DP_CONTROL_PLANE")


K46, K46_PATH = _load_k46()


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


PINS = {  # parent hashes recorded at build time (04 §2). A mismatch halts the build.
    "dp_uc44_kernel.py": None,
    "dp_uc48_kernel.py": None,
    "dp_uc46_kernel.py": None,
    "barrel_rate.py": None,
}


def lineage() -> dict:
    return {
        "dp_uc44_kernel.py": sha(K44.__file__),
        "dp_uc48_kernel.py": sha(K48.__file__),
        "dp_uc46_kernel.py": sha(K46_PATH),
        "barrel_rate.py": sha(BR.__file__),
    }


def assert_lineage(pins: dict | None = None) -> dict:
    now = lineage()
    for k, v in (pins or PINS).items():
        if v is not None and now[k] != v:
            raise AssertionError(f"parent kernel drift: {k} {now[k][:12]} != pinned {v[:12]}")
    return now


# Section A re-exports (so consumers import ONE module) ------------------------
get_stats, nresults = K44.get_stats, K44.nresults
whiff_rate, chase_rate = K44.whiff_rate, K44.chase_rate
pitch_mix, lhb_pitch_mix, rhb_pitch_mix = K44.pitch_mix, K44.lhb_pitch_mix, K44.rhb_pitch_mix
bb_type_by_level, hard_hit_rate, two_prop_z = K44.bb_type_by_level, K44.hard_hit_rate, K44.two_prop_z
apply_woba_weights = K44.apply_woba_weights
barrel_rate = BR.barrel_rate
xwobacon, runs_created = K48.xwobacon, K48.runs_created
build_bip, direction_rate = K46.build_bip, K46.direction_rate
bb_type_profile, pull_air_rate = K46.bb_type_profile, K46.pull_air_rate
SWINGS, WHIFFS = K44.SWINGS, K44.WHIFFS

PHILLIES_RED, PHILLIES_NAVY, PHILLIES_BLUE = K44.PHILLIES_RED, K44.PHILLIES_NAVY, K44.PHILLIES_BLUE
PITCH_COLORS = K44.PITCH_COLORS
DIRECTION_COLORS = K46.DIRECTION_COLORS
STRIKE_ZONE = K44.STRIKE_ZONE

# ----------------------------------------------------------------------------
# Constants: the game, the lineup, the opposing starter
# ----------------------------------------------------------------------------
GAME_LABEL = "NL Wild Card Series, Game 1"
GAME_DATE = "2026-09-29"
PARK = "Truist Park"
ANCHOR_GAME_DATE = "2026-09-27"      # last regular-season game (Game 162) in phils_2026.parquet
SEASON = 2026
SALE_ID = 519242                     # Chris Sale, LHP, ATL
SALE_NAME = "Sale, Chris"            # HP family only

# Batting order is a client carry-in (prompt, 2026-09-29). Ids resolved from the
# Phillies log by batter id x player_name mode (01 §3), never hand-keyed.
LINEUP = [
    # slot, display,           client name,          id,     bats
    (1, "Trea Turner",     "Turner, Trea",       607208, "R"),
    (2, "Kyle Schwarber",  "Schwarber, Kyle",    656941, "L"),
    (3, "Bryce Harper",    "Harper, Bryce",      547180, "L"),
    (4, "Alec Bohm",       "Bohm, Alec",         664761, "R"),
    (5, "Derek Hill",      "Hill, Derek",        656537, "R"),
    (6, "Bryan De La Cruz", "De La Cruz, Bryan", 650559, "R"),
    (7, "Bryson Stott",    "Stott, Bryson",      681082, "L"),
    (8, "Edmundo Sosa",    "Sosa, Edmundo",      624641, "R"),
    (9, "J.T. Realmuto",   "Realmuto, J.T.",     592663, "R"),
]
LINEUP_IDS = [r[3] for r in LINEUP]
CLIENT_CARDS = {607208, 656941, 547180}           # Turner, Schwarber, Harper: client-authored cards
NEW_CARDS = [i for i in LINEUP_IDS if i not in CLIENT_CARDS]

# Dedicated per-player files in data/opponents (precedence 1 for that id)
SUBJECT_FILES = {
    607208: "turner.parquet", 656941: "schwarber.parquet", 547180: "harper.parquet",
    592663: "realmuto.parquet", 656537: "derek_hill.parquet", 650559: "bdlc.parquet",
    624641: "edmundo.parquet", SALE_ID: "sale.parquet",
}
MLB_ONLY_EXCLUDE = {"lhvo26.parquet", "lhvp26.parquet", "lhvp25.parquet", "lhvb25.parquet",
                    "clwo26.parquet", "clwp26.parquet", "clearwater_batting25.parquet",
                    "clearwater_pitching25.parquet", "chst25.parquet", "sweet_aaa.parquet",
                    "turnbulllhv.parquet"}   # minor-league tiers never blend into MLB rates
REGULAR = ("R",)
POSTSEASON = ("F", "D", "L", "W")
H2H_MIN_PA_RANK = 20                 # the client's Harper cut: z.plate_apps > 19
THIN_PA = 10                         # house: < 10 PA = directional only
BIP_FLOOR = K46.BIP_FLOOR            # FL-1: 25 classifiable BIP per directional cell
HL_EDGE = 0.83 / 3                   # HL-1: thirds of the house plate half-width (ft)

LOAD_COLS = [
    "game_pk", "at_bat_number", "pitch_number", "game_date", "game_year", "game_type",
    "home_team", "away_team", "inning", "inning_topbot", "outs_when_up", "balls", "strikes",
    "batter", "pitcher", "player_name", "stand", "p_throws", "pitch_type", "pitch_name",
    "description", "events", "des", "type", "zone", "plate_x", "plate_z", "sz_top", "sz_bot",
    "release_speed", "release_spin_rate", "pfx_x", "pfx_z", "release_pos_x", "release_pos_z",
    "release_extension", "spin_axis", "arm_angle",
    "launch_speed", "launch_angle", "launch_speed_angle", "hit_distance_sc", "hc_x", "hc_y",
    "bb_type", "estimated_woba_using_speedangle", "estimated_ba_using_speedangle",
    "woba_value", "woba_denom", "delta_run_exp", "n_thruorder_pitcher",
    "on_1b", "on_2b", "on_3b", "bat_score", "post_bat_score", "bat_speed", "swing_length",
    "phillies_role",
]


# ============================================================================
# SECTION B -- data access
# ============================================================================
def _read(f: Path, cols=LOAD_COLS) -> pd.DataFrame:
    import pyarrow.parquet as pq
    have = set(pq.read_schema(f).names)
    return pd.read_parquet(f, columns=[c for c in cols if c in have])


def load_house(years=range(2015, 2027), batter_ids=LINEUP_IDS, pitcher_id=SALE_ID,
               include_all_phillies_batting=True) -> pd.DataFrame:
    """BF-1 · one pass, one frame.

    Sources and precedence (lower wins on PITCH_KEY collision):
      0  data/phillies/phils_YYYY.parquet   (Phillies log, batting rows + any pitch by `pitcher_id`)
      1  the dedicated file for that row's subject (SUBJECT_FILES)
      2  atlp26 / atlo26 (Braves 2026 logs)
      3  every other MLB opponent file
    Minor-league tiers (MLB_ONLY_EXCLUDE) are never read.
    Opponent rows are kept only where batter is a lineup id OR pitcher is `pitcher_id`
    (identity by id: the O-26 lesson -- `player_name` is the pitcher in pitcher-keyed
    pulls and the batter in batter-keyed pulls).
    """
    frames = []
    for y in years:
        d = _read(ROOT / "data" / "phillies" / f"phils_{y}.parquet")
        keep = (d.batter.isin(batter_ids) | (d.pitcher == pitcher_id))
        if include_all_phillies_batting and "phillies_role" in d:
            keep |= d.phillies_role.eq("batting")
        d = d[keep].copy()
        d["src"], d["prec"] = f"phils_{y}", 0
        frames.append(d)
    subj_files = {v: k for k, v in SUBJECT_FILES.items()}
    for f in sorted((ROOT / "data" / "opponents").glob("*.parquet")):
        if f.name in MLB_ONLY_EXCLUDE:
            continue
        d = _read(f)
        d = d[d.batter.isin(batter_ids) | (d.pitcher == pitcher_id)].copy()
        if not len(d):
            continue
        d["src"] = f.name
        if f.name in subj_files:
            sid = subj_files[f.name]
            d["prec"] = np.where((d.batter == sid) | (d.pitcher == sid), 1, 3)
        elif f.name.startswith("atl"):
            d["prec"] = 2
        else:
            d["prec"] = 3
        frames.append(d)
    H = pd.concat(frames, ignore_index=True)
    H["game_date"] = pd.to_datetime(H.game_date).dt.strftime("%Y-%m-%d")
    for c in ("game_year", "game_pk", "at_bat_number", "pitch_number", "batter", "pitcher"):
        H[c] = pd.to_numeric(H[c], errors="coerce")
    n_raw = len(H)
    H = H.sort_values(["prec", "src"]).drop_duplicates(PITCH_KEY, keep="first")
    n_dedup = len(H)
    H = apply_woba_weights(H).reset_index(drop=True)
    H.attrs["n_raw"], H.attrs["n_dedup"] = n_raw, n_dedup
    return H


def batter_frame(H: pd.DataFrame, batter_id: int, game_types=REGULAR) -> pd.DataFrame:
    d = H[(H.batter == batter_id)]
    if game_types:
        d = d[d.game_type.isin(game_types)]
    return d.copy()


def sale_frame(H: pd.DataFrame, years=None, game_types=REGULAR) -> pd.DataFrame:
    d = H[H.pitcher == SALE_ID]
    if years is not None:
        d = d[d.game_year.isin(list(years))]
    if game_types:
        d = d[d.game_type.isin(game_types)]
    return d.copy()


# ============================================================================
# SECTION C -- NEW (provisional)
# ============================================================================
PA_EVENTS_EXCLUDE = ["NA", "pickoff_1b"]   # get_stats' PA rule, verbatim


def xwoba_pa(level, df):
    """XW-1 · PA-denominated expected wOBA.

    Numerator: for batted-ball PA ends, `estimated_woba_using_speedangle`
    (Statcast's contact expectation); for every other PA end (K, BB, HBP, ...),
    the actual `woba_value`. Denominator: `woba_denom` summed over PA ends.
    A BIP with no expectation (untracked) falls back to its actual woba_value
    and is counted in `xw_fallback` (sensor-boundary disclosure, uc-pos-009).
    """
    if isinstance(level, str):
        level = [level]
    pa = df[df.woba_denom.fillna(0) > 0].copy()
    exp = pd.to_numeric(pa.estimated_woba_using_speedangle, errors="coerce")
    is_bip = pa.type.eq("X")
    pa["xw_num"] = np.where(is_bip & exp.notna(), exp, pd.to_numeric(pa.woba_value, errors="coerce").fillna(0))
    pa["xw_fb"] = (is_bip & exp.isna()).astype(int)
    out = pa.groupby(level, as_index=False).agg(xw_num=("xw_num", "sum"), xw_den=("woba_denom", "sum"),
                                                xw_fallback=("xw_fb", "sum"))
    out["xwoba"] = np.where(out.xw_den > 0, out.xw_num / out.xw_den, np.nan)
    return out


def horizontal_band(df: pd.DataFrame) -> pd.Series:
    """HL-1 · Inner / Middle / Away, relative to the batter.

    x_rel = plate_x for RHB, -plate_x for LHB (plate_x + = first-base side, catcher's
    view; E-7). Away = x_rel > +HL_EDGE, Inner = x_rel < -HL_EDGE, else Middle.
    Out-of-zone pitches keep their side. NULL plate_x -> NULL band.
    """
    x_rel = np.where(df.stand.eq("L"), -df.plate_x, df.plate_x)
    band = np.select([x_rel > HL_EDGE, x_rel < -HL_EDGE], ["Away", "Inner"], default="Middle")
    return pd.Series(np.where(pd.isna(df.plate_x), None, band), index=df.index, name="h_band")


def lhp_rank(df: pd.DataFrame, target_pitcher: int = SALE_ID, min_pa: int = H2H_MIN_PA_RANK,
             metric: str = "ops") -> dict:
    """LR-1 · the client's Harper cut, generalised.

    Among every LHP the hitter has faced with >= min_pa PA (client: `plate_apps > 19`),
    where does `target_pitcher` rank by `metric` (1 = lowest = best for the pitcher)?
    Returns the rank, the population size and the target's line; NaN rank if the
    target is below the PA floor (then the card says so rather than ranking him).
    """
    lhp = df[df.p_throws == "L"]
    z = nresults(["pitcher"], lhp)
    pop = z[z.plate_apps >= min_pa].sort_values(metric).reset_index(drop=True)
    row = z[z.pitcher == target_pitcher]
    out = {"n_pitchers": int(len(pop)), "target_pa": int(row.plate_apps.iloc[0]) if len(row) else 0,
           "target_metric": float(row[metric].iloc[0]) if len(row) else np.nan,
           "pop_median": float(pop[metric].median()) if len(pop) else np.nan}
    if len(row) and out["target_pa"] >= min_pa:
        out["rank"] = int(pop.index[pop.pitcher == target_pitcher][0]) + 1
    else:
        out["rank"] = np.nan
    return out


def tto_split(level, df):
    """TT-1 · results by time through the order (Statcast `n_thruorder_pitcher`),
    capped at '3+'. A pure dimension on nresults; no new arithmetic."""
    d = df.copy()
    d["tto"] = np.where(d.n_thruorder_pitcher >= 3, "3+", d.n_thruorder_pitcher.astype("Int64").astype(str))
    level = [level] if isinstance(level, str) else list(level)
    return nresults(level + ["tto"], d).merge(xwoba_pa(level + ["tto"], d)[level + ["tto", "xwoba"]],
                                               on=level + ["tto"], how="left")


CARD_KPIS = ["pitches", "plate_apps", "hits", "hrs", "walks", "strikeouts", "ba", "obp", "slg", "ops", "woba",
             "xwoba", "krate", "bbrate", "whiff_rate", "chase_rate", "bip", "barrel_rate", "hard_hit_rate"]


def index_card(level, df) -> pd.DataFrame:
    """IC-1 · the per-hitter card line. A COMPOSITION of locked KPIs (no new arithmetic):
    nresults ⋈ xwoba_pa ⋈ whiff_rate ⋈ chase_rate ⋈ barrel_rate ⋈ hard_hit_rate.
    Merges are LEFT on the level keys (1:1 by construction; asserted by the harness)."""
    level = [level] if isinstance(level, str) else list(level)
    z = nresults(level, df)
    z = z.merge(xwoba_pa(level, df)[level + ["xwoba", "xw_fallback"]], on=level, how="left")
    z = z.merge(whiff_rate(level, df)[level + ["swings", "whiffs", "whiff_rate"]], on=level, how="left")
    z = z.merge(chase_rate(level, df)[level + ["chases", "ooz", "chase_rate"]], on=level, how="left")
    z = z.merge(barrel_rate(level, df)[level + ["barrels", "barrel_rate"]], on=level, how="left")
    hh = hard_hit_rate(level, df)
    z = z.merge(hh[level + ["hard_hits", "hard_hit_rate"]], on=level, how="left")
    for c in ("whiffs", "chases", "barrels", "hard_hits"):
        z[c] = z[c].fillna(0)
    return z


def thin(pa) -> str:
    return "THIN" if pa < THIN_PA else ""


def fmt3(x) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    s = f"{x:.3f}"
    return s[1:] if s.startswith("0.") else s


def pct(x, d=1) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{100 * x:.{d}f}%"


# ----------------------------------------------------------------------------
# NF-2 · the client's frames, reproduced exactly (HP family only)
# ----------------------------------------------------------------------------
def nphl_name_frames(names, cols=LOAD_COLS) -> tuple[dict, dict]:
    """NF-2 (generalises dp_uc49 NF-1 to many names in one pass).

    `get_nphillies_data()` concatenates EVERY opponent parquet (minor-league tiers
    included) in sorted file order and drops duplicate PITCH_KEY rows keep='first'.
    A pitch that also sits in an alphabetically earlier, batter-keyed file survives
    there with player_name = the batter, and is lost to a pitcher-name filter (O-26).
    Returns ({name: frame}, {name: n_rows_lost_to_dedup})."""
    files = sorted((ROOT / "data" / "opponents").glob("*.parquet"))
    keys = []
    for i, f in enumerate(files):
        k = pd.read_parquet(f, columns=PITCH_KEY + ["player_name"])
        k["_file_i"], k["_row"] = i, np.arange(len(k))
        keys.append(k)
    allk = pd.concat(keys, ignore_index=True)
    allk["_first"] = ~allk.duplicated(subset=PITCH_KEY, keep="first")
    frames, lost = {}, {}
    for name in names:
        hit = allk[allk.player_name == name]
        lost[name] = int((~hit._first).sum())
        parts = []
        for i in sorted(hit._file_i.unique()):
            d = _read(files[i], cols)
            parts.append(d.iloc[hit[(hit._file_i == i) & hit._first]._row.values])
        frames[name] = apply_woba_weights(pd.concat(parts, ignore_index=True)) if parts else pd.DataFrame(columns=cols)
    return frames, lost


def client_pos(years=range(2015, 2027)) -> pd.DataFrame:
    """The client's `pos`: get_phillies_data() batting rows, ALL game types (no filter)."""
    frames = []
    for y in years:
        d = _read(ROOT / "data" / "phillies" / f"phils_{y}.parquet")
        frames.append(d[d.phillies_role == "batting"])
    return apply_woba_weights(pd.concat(frames, ignore_index=True))
