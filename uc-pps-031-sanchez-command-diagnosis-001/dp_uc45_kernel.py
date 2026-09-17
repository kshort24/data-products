"""
dp_uc45_kernel.py — governed kernel for UC #45 / uc-pps-031
"Cristopher Sánchez — is he near the zone? A 2026 command diagnosis"

INHERITANCE POLICY (see 03_governance.md, Rule-1):
  * Section A  — VERBATIM transcription of the governed kernel in
    `Baseball Functions.ipynb`, carried forward byte-for-byte from
    dp_uc44_kernel.py Section A. Known defects (D-1/D-2, D-7/O-13, O-8, O-14)
    are MEASURED in out/dp_uc45_defect_exposure.csv, never patched here.
  * Section A2 — VERBATIM `_dist_to_zone_edge` + `edge_rate` (UC8 origin,
    glossary-approved, Register v2 P16 disposition A) as carried in
    dp_uc38_nola_stubbs_battery.py. NOTE: not yet present in the notebook.
  * Section B  — data access (verbatim behaviour of mlb_data.py, via dp_uc44).
  * (No Section C.) SG-1..SG-5 (dp_uc44) were considered and NOT inherited:
    within one zone-rail regime the pitcher-season population in the Phillies
    log is 13 arms at 500 pitches — too thin to grade. See 03 §1.
  * Section D  — NEW to this UC (SZ-0..SZ-5, CL-1, PN-1, ZC-1). Provisional.

Geometry constants are the Register v2 §4.1 ruling, not new choices:
  PLATE_HALF = 0.83 ft (Statcast plate half-width convention)
  BALL_FT    = 2.94 / 12 ft (one baseball diameter, ratified 2026-07-24)

Data plane: C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB
Control plane: C:\\Users\\Kellen\\OneDrive\\Documents\\Agents for Data Products
"""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Data-root resolution (portable: env var -> sandbox mount -> relative -> Windows)
# ----------------------------------------------------------------------------
_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT"),
    "/mnt/user-data/uploads/MLB",
    "./",
    "../../../Python Scripts/MLB",
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB",
]

def data_root() -> Path:
    for c in _CANDIDATES:
        if not c:
            continue
        p = Path(c)
        if (p / "data" / "phillies" / "phils_2026.parquet").exists():
            return p
    raise FileNotFoundError("MLB data plane not reachable; set MLB_DATA_ROOT")

ROOT = data_root()
WOBA_CSV = ROOT / "wOBA and FIP Constants.csv"

# ---- house constants -------------------------------------------------------
PHILLIES_RED  = "#E81828"
PHILLIES_BLUE = "#284898"
PHILLIES_NAVY = "#002D72"
PITCH_COLORS = {   # verbatim from skills/phillies-pitchmix-analysis/assets/pitch_colors.py
    '4-Seam Fastball': '#D22D49', 'Sinker': '#FE9D00', 'Cutter': '#933F2C',
    'Slider': '#EEE716', 'Sweeper': '#DDB33A', 'Slurve': '#93AFD4',
    'Curveball': '#00D1ED', 'Knuckle Curve': '#6236CD', 'Slow Curve': '#274BA7',
    'Changeup': '#1DBE3A', 'Split-Finger': '#3BACAC', 'Forkball': '#3BACAC',
    'Screwball': '#60DB33', 'Knuckleball': '#3C44CF', 'Eephus': '#888888',
    'Pitch Out': '#888888', 'Other': '#999999',
}
STAND_COLORS = {'LHB': '#284898', 'RHB': '#D22D49', 'L': '#284898', 'R': '#D22D49'}

# ---- geometry (Register v2 §4.1 — ratified, not new) -----------------------
PLATE_HALF = 0.83
BALL_FT = 2.94 / 12

# ---- entity lock (MLBAM id; NEVER a name filter) ----------------------------
SUBJECT_ID = 650911              # Cristopher Sánchez, LHP, PHI (uc-pps-019 lock)
SUBJECT_NAME = "Sánchez, Cristopher"
ANCHOR_GAME_DATE = "2026-09-15"  # last game in the cache; Sánchez started it
ASG_BREAK_2026 = "2026-07-13"    # first-half cut (named cause: All-Star break)
SEASONS = (2021, 2022, 2023, 2024, 2025, 2026)
SEASON_MERGE = {2021: "2021-22", 2022: "2021-22"}   # client permission

# ============================================================================
# SECTION A — VERBATIM from `Baseball Functions.ipynb` (locked, do not edit)
# ============================================================================
def get_stats(level, df):
    pitches = df.groupby(level, as_index=False).agg({'description': 'size'}).rename(columns={'size': 'pitches'})
    plate_apps = df[~df.events.replace(np.nan, 'NA').isin(['NA', 'pickoff_1b'])].groupby(level, as_index=False).agg({'description': 'size'})
    plate_apps = plate_apps.rename(columns={'description': 'plate_apps'})
    at_bats = df[~df.events.replace(np.nan, 'NA').isin(['NA', 'pickoff_1b', 'walk', 'intent_walk', 'hit_by_pitch', 'sac_fly', 'sac_bunt'])].groupby(level, as_index=False).agg({'description': 'size'})
    at_bats = at_bats.rename(columns={'description': 'at_bats'})
    bip = df[df.type == 'X'].groupby(level, as_index=False).agg({'description': 'size'}).rename(columns={'description': 'bip'})
    hits = df[df.events.isin(['home_run', 'single', 'double', 'triple'])].groupby(level, as_index=False).agg({'description': 'size'})
    hits = hits.rename(columns={'description': 'hits'})
    singles = df[df.events == 'single'].groupby(level, as_index=True).agg({'description': 'size'}).rename(columns={'description': 'singles'})
    doubles = df[df.events == 'double'].groupby(level, as_index=True).agg({'description': 'size'}).rename(columns={'description': 'doubles'})
    triples = df[df.events == 'triple'].groupby(level, as_index=True).agg({'description': 'size'}).rename(columns={'description': 'triples'})
    hrs = df[df.events == 'home_run'].groupby(level, as_index=True).agg({'description': 'size'}).rename(columns={'description': 'hrs'})
    walks = df[df.events == 'walk'].groupby(level, as_index=True).agg({'description': 'size'}).rename(columns={'description': 'walks'})
    ks = df[df.events.isin(['strikeout', 'strikeout_double_play'])].groupby(level, as_index=True).agg({'description': 'size'}).rename(columns={'description': 'strikeouts'})
    hbp = df[df.events == 'hit_by_pitch'].groupby(level, as_index=True).agg({'description': 'size'}).rename(columns={'description': 'hbp'})
    wBB = df[df.events == 'walk'].groupby(level, as_index=False).agg({'wBB': 'sum'})
    wHBP = df[df.events == 'hit_by_pitch'].groupby(level, as_index=False).agg({'wHBP': 'sum'})
    w1B = df[df.events == 'single'].groupby(level, as_index=False).agg({'w1B': 'sum'})
    w2B = df[df.events == 'double'].groupby(level, as_index=False).agg({'w2B': 'sum'})
    w3B = df[df.events == 'triple'].groupby(level, as_index=False).agg({'w3B': 'sum'})
    wHR = df[df.events == 'home_run'].groupby(level, as_index=False).agg({'wHR': 'sum'})
    xba = df.groupby(level, as_index=False).agg({'estimated_ba_using_speedangle': 'mean'})
    xwoba = df.groupby(level, as_index=False).agg({'estimated_woba_using_speedangle': 'mean'})
    a = pitches.merge(plate_apps, how='left', left_on=level, right_on=level)
    b = a.merge(at_bats, how='left', left_on=level, right_on=level)
    c = b.merge(hits, how='left', left_on=level, right_on=level)
    d = c.merge(singles, how='left', left_on=level, right_on=level)
    e = d.merge(doubles, how='left', left_on=level, right_on=level)
    f = e.merge(triples, how='left', left_on=level, right_on=level)
    g = f.merge(hrs, how='left', left_on=level, right_on=level)
    h = g.merge(walks, how='left', left_on=level, right_on=level)
    i = h.merge(hbp, how='left', left_on=level, right_on=level)
    j = i.merge(wBB, how='left', left_on=level, right_on=level)
    k = j.merge(wHBP, how='left', left_on=level, right_on=level)
    l = k.merge(w1B, how='left', left_on=level, right_on=level)
    m = l.merge(w2B, how='left', left_on=level, right_on=level)
    n = m.merge(w3B, how='left', left_on=level, right_on=level)
    o = n.merge(ks, how='left', left_on=level, right_on=level)
    p = o.merge(bip, how='left', left_on=level, right_on=level)
    q = p.merge(xba, how='left', left_on=level, right_on=level)
    r = q.merge(xwoba, how='left', left_on=level, right_on=level)
    stats = r.merge(wHR, how='left', left_on=level, right_on=level)
    stats = stats.replace(np.nan, 0)
    return stats

def measure_calcs(stats):
    stats.rename(columns={'batter': 'pitches'}, inplace=True)
    stats['ba'] = stats.hits / stats.at_bats
    stats['obp'] = (stats.hits + stats.walks + stats.hbp) / (stats.plate_apps)
    stats['slg'] = (stats.singles + 2 * stats.doubles + 3 * stats.triples + 4 * stats.hrs) / (stats.at_bats)
    stats['ops'] = stats.obp + stats.slg
    stats['woba'] = (stats.wBB + stats.wHBP + stats.w1B + stats.w2B + stats.w3B + stats.wHR) / (stats.plate_apps)
    return stats

def mcgs(level, df):
    return measure_calcs(get_stats(level, df)).rename(columns={'description': 'pitches'})

def nresults(level, df):
    if isinstance(level, str):
        level = [level]
    cols = level + ['pitches', 'plate_apps', 'bip', 'hits', 'hrs', 'walks',
                    'strikeouts', 'ba', 'obp', 'slg', 'ops', 'woba']
    x = mcgs(level, df).loc[:, cols].round(3)
    x['krate'] = x.strikeouts / x.plate_apps
    x['bbrate'] = x.walks / x.plate_apps
    x['hr_rate'] = x.hrs / x.plate_apps
    return x.round(3)

SWINGS = ['foul', 'foul_bunt', 'foul_tip', 'hit_into_play', 'missed_bunt',
          'swinging_pitchout', 'swinging_strike', 'swinging_strike_blocked']
WHIFFS = ['foul_tip', 'missed_bunt', 'swinging_pitchout', 'swinging_strike',
          'swinging_strike_blocked']

def whiff_rate(level, df):
    u = df[df.description.isin(SWINGS)].groupby(level, as_index=False).agg(swings=('des', 'size'))
    v = df[df.description.isin(WHIFFS)].groupby(level, as_index=False).agg(whiffs=('des', 'size'))
    w = u.merge(v, on=level)                 # << D-1/D-2: inner join drops zero-whiff groups
    w['whiff_rate'] = w.whiffs / w.swings
    return w

def chase_rate(level, df):
    chase = df[(df.zone > 9) & (df.description.isin(SWINGS))]
    i = chase.groupby(level, as_index=False).agg(chases=('des', 'size'))
    j = df[df.zone > 9].groupby(level, as_index=False).agg(ooz=('des', 'size'))
    cr = i.merge(j, on=level).merge(
        df.groupby(level, as_index=False).agg(pitches=('des', 'size')),
        on=level, how='right')
    cr['chase_rate'] = cr.chases / cr.ooz
    cr['in_zone_rate'] = (cr.pitches - cr.ooz) / cr.pitches   # << D-7/O-13: NULL zone counts in-zone
    return cr.round(3)

def pitch_mix(df):
    pm = df.groupby(['pitch_type', 'pitch_name'], as_index=False).agg(
        {'des': 'size', 'release_speed': 'mean', 'release_spin_rate': 'mean',
         'zone': 'mean', 'pfx_x': 'mean', 'plate_x': 'mean', 'pfx_z': 'mean',
         'plate_z': 'mean'}).rename(columns={'des': 'count'}).sort_values(by='count', ascending=False)
    pm['usage'] = round((pm['count'] / len(df)) * 100, 1)
    return pm.round(1)

def lhb_pitch_mix(df): return pitch_mix(df[df.stand == 'L'])
def rhb_pitch_mix(df): return pitch_mix(df[df.stand == 'R'])

def fpsr(level, df):
    x = df[df.pitch_number == 1].groupby(level + ['type'], as_index=False).agg(balls=('des', 'size')).merge(
        df[df.pitch_number == 1].groupby(level, as_index=False).agg(pitches=('des', 'size')),
        on=level, how='right')
    x['First Pitch Strike Rate'] = (x.pitches - x.balls) / x.pitches
    return x[x.type == 'B']

def putaway_rate(level, df):
    z = df[df.strikes == 2].groupby(level, as_index=False).agg(pitches2strikes=('des', 'size')).merge(
        df[df.events.isin(['strikeout', 'strikeout_double_play'])].groupby(level, as_index=False).agg(strikeouts=('des', 'size')),
        on=level, how='left', suffixes=('', '_ks'))
    z['putaway_rate'] = z.strikeouts / z.pitches2strikes
    return z.round(3)

def bb_type_by_level(level, df):
    bb = df[df.type == 'X'].groupby(level + ['bb_type'], as_index=False).agg(bips=('des', 'size'))
    grp = bb.groupby(level, as_index=False).agg(total_level=('bips', 'sum')).merge(bb, on=level, how='right')
    grp['share'] = grp.bips / grp.total_level
    return grp.round(3)

def hard_hit_rate(level, df):
    hh = df[(df.launch_speed >= 95) & (df.type == 'X')].groupby(level, as_index=False).agg(hard_hits=('des', 'size')).merge(
        df[df.type == 'X'].groupby(level, as_index=False).agg(bips=('des', 'size')), on=level)
    hh['hard_hit_rate'] = hh.hard_hits / hh.bips        # << O-8: untracked BIP counted as not-hard-hit
    hh['Hard Hit Rate'] = round((hh.hard_hit_rate * 100), 1)
    return hh

# ---- barrel_rate: VERBATIM from Baseball Functions.ipynb cell 58 (first
#      transcription into a dp kernel; dp_uc44 Section A did not carry it) ----
def barrel_rate(level, df, suffix=''):
    import numpy as np
    if isinstance(level, str):
        level = [level]

    bip_pop = df[df.type == 'X']                      # canonical BIP population (house standard)

    bips = (bip_pop
            .groupby(level, as_index=False)
            .agg(bips=('des', 'size')))               # denominator, mirrors hard_hit_rate

    barrels = (bip_pop[bip_pop.launch_speed_angle == 6]   # null lsa excluded automatically
               .groupby(level, as_index=False)
               .agg(barrels=('des', 'size')))         # numerator

    out = bips.merge(barrels, on=level, how='left')
    out['barrels'] = out.barrels.fillna(0).astype(int)    # groups with no barrels -> 0, not NaN
    out['barrel_rate'] = np.where(out.bips > 0,
                                  (out.barrels / out.bips).round(3),
                                  0)                   # 0-BIP guard: no division by zero

    if suffix:
        out = out.rename(columns={'bips': f'bips{suffix}'})

    return out

def two_prop_z(x1, n1, x2, n2):
    """Pooled two-proportion z — the repo's standing significance test (from dp_uc42/43)."""
    if min(n1, n2) == 0:
        return np.nan, np.nan
    p1, p2 = x1 / n1, x2 / n2
    p = (x1 + x2) / (n1 + n2)
    se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return np.nan, np.nan
    z = (p1 - p2) / se
    from scipy.stats import norm
    return float(z), float(2 * (1 - norm.cdf(abs(z))))


# ============================================================================
# SECTION A2 — VERBATIM governed Edge Rate (UC8 origin; Register v2 P16 = A)
# ============================================================================
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

# ============================================================================
# SECTION B — data access (verbatim behaviour of mlb_data.py)
# ============================================================================
def apply_woba_weights(df: pd.DataFrame) -> pd.DataFrame:
    weights = pd.read_csv(WOBA_CSV)
    overlap = [c for c in weights.columns if c != 'Season' and c in df.columns]
    if overlap:
        df = df.drop(columns=overlap)
    return df.merge(weights, left_on='game_year', right_on='Season', suffixes=('_bad', ''), how='left')

def load_phils(years=(2026,), role=None, regular_only=True) -> pd.DataFrame:
    frames = [pd.read_parquet(ROOT / 'data' / 'phillies' / f'phils_{y}.parquet') for y in years]
    df = pd.concat(frames, ignore_index=True)
    if regular_only:
        df = df[df.game_type == 'R']
    if role:
        df = df[df.phillies_role == role]
    return apply_woba_weights(df.copy())

def load_pps(years=(2026,)):  return load_phils(years, role='pitching')
def load_pos(years=(2026,)):  return load_phils(years, role='batting')
# ============================================================================
# SECTION D — NEW to UC #45 (provisional, unratified — see 03_governance.md §2)
# ============================================================================
#
# THE SHADOW ZONE, AND WHY IT IS NOT A FOURTH GEOMETRY
# ----------------------------------------------------
# The repo already carries three "edge/shadow" partitions:
#   (1) Edge Rate (UC8, pitcher-side, GOVERNED): Euclidean distance to the
#       zone perimeter <= BALL_FT, inside OR outside. A band that STRADDLES the line.
#   (2) OZ family (uc-pos-005, batter-side, provisional): rectangular band of
#       +-1 ball; shadow_in / shadow_out / heart / waste.
#   (3) Attack Zone (UC#11 / uc-pps-022): shadow = 0..0.33 ft OUTSIDE the zone
#       — a conflicting constant (UC#11 origin; still in use 07-25, after the
#       07-24 ball-width ruling).
# The client's "shadow of the zone" is a TARGET: the rulebook zone grown by one
# baseball. SZ adopts geometry (1) exactly — same distance function, same
# constant — so that, by construction:
#       Shadow Zone  = heart + edge_in + edge_out        (SZ-1)
#       Edge Rate    =        edge_in + edge_out        (governed, unchanged)
#       Shadow Miss  = beyond                            (SZ-2 = 1 - SZ-1)
# and "Shadow Miss" corresponds to OZ "waste" except at the four corners, where
# Euclidean (rounded) and rectangular (square) bands disagree. The corner
# disagreement is counted in out/dp_uc45_geometry_crosswalk.csv.

SZ_REGIONS = ['heart', 'edge_in', 'edge_out', 'beyond']

def signed_zone_distance(df: pd.DataFrame) -> np.ndarray:
    """SZ-0 support. Signed distance (ft) from pitch centre to the rulebook
    zone perimeter: NEGATIVE inside, POSITIVE outside. Magnitude is exactly the
    governed `_dist_to_zone_edge` (Section A2) — only the sign is added.
    Rows with a null location CDE return NaN (never 0)."""
    px = df.plate_x.astype(float).values
    pz = df.plate_z.astype(float).values
    bot = df.sz_bot.astype(float).values
    top = df.sz_top.astype(float).values
    ok = ~(np.isnan(px) | np.isnan(pz) | np.isnan(bot) | np.isnan(top))
    out = np.full(len(df), np.nan)
    if ok.any():
        dist = _dist_to_zone_edge(px[ok], pz[ok], bot[ok], top[ok])
        inside = (np.abs(px[ok]) <= PLATE_HALF) & (pz[ok] >= bot[ok]) & (pz[ok] <= top[ok])
        out[ok] = np.where(inside, -dist, dist)
    return out


def shadow_region(df: pd.DataFrame) -> pd.Series:
    """SZ-0 `shadow_region` (NEW-UC45, provisional).
    heart    : inside the zone and more than one ball from every edge
    edge_in  : inside the zone, within one ball of an edge
    edge_out : outside the zone, within one ball of the perimeter (Euclidean)
    beyond   : more than one ball outside the perimeter — "missed the shadow"
    untracked: any location CDE null (excluded from every SZ denominator).
    Boundary rule: a pitch exactly on the perimeter (s == 0) is edge_in; a
    pitch exactly BALL_FT outside is edge_out (<=), matching edge_rate's <=."""
    s = signed_zone_distance(df)
    lab = np.select(
        [np.isnan(s), s < -BALL_FT, s <= 0, s <= BALL_FT],
        ['untracked', 'heart', 'edge_in', 'edge_out'], default='beyond')
    return pd.Series(lab, index=df.index, name='shadow_region')


def shadow_profile(level, df: pd.DataFrame) -> pd.DataFrame:
    """SZ-1..SZ-4 `shadow_profile(level, df)` (NEW-UC45, provisional).

    Population : located pitches (all four location CDEs non-null).
    SZ-1 shadow_zone_rate        = (heart + edge_in + edge_out) / located
    SZ-2 shadow_miss_rate        = beyond / located            (= 1 - SZ-1)
         beyond_miss_depth_ft    = median signed distance of beyond pitches
    SZ-3 beyond_shadow_chase_rate= swings on beyond / beyond   (the client's proof)
    SZ-4 edge_out_chase_rate     = swings on edge_out / edge_out
         geo_zone_rate           = (heart + edge_in) / located (geometry twin
                                   of the kernel in_zone_rate; reconciled, not
                                   substituted — the kernel number is governed)
         edge_rate_twin          = (edge_in + edge_out) / located — must equal
                                   governed edge_rate() exactly (asserted).
    Swing      : kernel SWINGS list (Baseball Functions cell 21), verbatim.
    Null rule  : a rate whose denominator is 0 is NaN, never 0 (uc-pos-009
                 sensor-boundary standard). Count columns are filled with 0.
    """
    if isinstance(level, str):
        level = [level]
    d = df.copy()
    d['_reg'] = shadow_region(d)
    d['_s'] = signed_zone_distance(d)
    d = d[d._reg != 'untracked']
    d['_sw'] = d.description.isin(SWINGS)
    cnt = pd.crosstab([d[c] for c in level], d._reg).reindex(columns=SZ_REGIONS, fill_value=0)
    sw = pd.crosstab([d[c] for c in level], d._reg, values=d._sw, aggfunc='sum') \
           .reindex(columns=SZ_REGIONS).fillna(0)
    out = cnt.copy()
    out.columns = [f'n_{c}' for c in SZ_REGIONS]
    out['located_pitches'] = cnt.sum(axis=1)
    out['swings_beyond'] = sw['beyond']
    out['swings_edge_out'] = sw['edge_out']
    loc = out.located_pitches.replace(0, np.nan)
    out['shadow_zone_rate'] = (out.n_heart + out.n_edge_in + out.n_edge_out) / loc
    out['shadow_miss_rate'] = out.n_beyond / loc
    out['geo_zone_rate'] = (out.n_heart + out.n_edge_in) / loc
    out['edge_rate_twin'] = (out.n_edge_in + out.n_edge_out) / loc
    out['beyond_shadow_chase_rate'] = out.swings_beyond / out.n_beyond.replace(0, np.nan)
    out['edge_out_chase_rate'] = out.swings_edge_out / out.n_edge_out.replace(0, np.nan)
    depth = d[d._reg == 'beyond'].groupby(level)._s.median().rename('beyond_miss_depth_ft')
    out = out.join(depth).reset_index()
    return out.round(4)


def shadow_miss_direction(level, df: pd.DataFrame) -> pd.DataFrame:
    """SZ-5 `shadow_miss_direction` (NEW-UC45, provisional).
    For BEYOND pitches only: the dominant axis of the miss — whichever of the
    horizontal or vertical exceedance past the zone perimeter is larger.
      high / low           : vertical exceedance dominates
      arm_side / glove_side: horizontal exceedance dominates, MIRRORED by the
                             pitcher's hand (O-15 sign rule, asserted from data:
                             negative plate_x = third-base side; a LHP's arm
                             side is POSITIVE plate_x, a RHP's is NEGATIVE).
    Returns counts and shares of beyond pitches by direction."""
    if isinstance(level, str):
        level = [level]
    d = df.copy()
    d = d[shadow_region(d) == 'beyond'].copy()
    px = d.plate_x.astype(float); pz = d.plate_z.astype(float)
    dx = np.maximum(px.abs() - PLATE_HALF, 0)
    dz = np.maximum.reduce([(d.sz_bot.astype(float) - pz).values,
                            (pz - d.sz_top.astype(float)).values, np.zeros(len(d))])
    arm_pos = np.where(d.p_throws == 'L', px > 0, px < 0)
    d['direction'] = np.where(dz >= dx.values,
                              np.where(pz > d.sz_top.astype(float), 'high', 'low'),
                              np.where(arm_pos, 'arm_side', 'glove_side'))
    t = pd.crosstab([d[c] for c in level], d.direction)
    for c in ['arm_side', 'glove_side', 'high', 'low']:
        if c not in t.columns:
            t[c] = 0
    t = t[['arm_side', 'glove_side', 'high', 'low']]
    sh = t.div(t.sum(axis=1), axis=0).add_suffix('_share')
    return t.add_prefix('n_').join(sh).reset_index().round(4)


def count_leverage(level, df: pd.DataFrame) -> pd.DataFrame:
    """CL-1 `count_leverage(level, df)` — PD-7 (uc-pps-017) PROMOTED to a
    function per Register v2 P8 ('inline -> promote'). Formula unchanged:
      pitch_share_ahead   = pitches thrown with balls < strikes / pitches
      two_strike_pa_share = distinct PA that saw a 2-strike pitch / PA
    Extension (NEW-UC45, provisional, flagged in 03):
      pitch_share_even / pitch_share_behind  (balls == / > strikes)
      three_ball_pa_share = distinct PA that saw a 3-ball pitch / PA
    Count state is the PRE-pitch count (Statcast balls/strikes).
    PA key = (game_pk, at_bat_number); PA denominator = distinct keys."""
    if isinstance(level, str):
        level = [level]
    d = df.copy()
    d['_ahead'] = d.balls < d.strikes
    d['_even'] = d.balls == d.strikes
    d['_behind'] = d.balls > d.strikes
    g = d.groupby(level)
    out = pd.DataFrame({
        'pitches': g.size(),
        'pitch_share_ahead': g._ahead.mean(),
        'pitch_share_even': g._even.mean(),
        'pitch_share_behind': g._behind.mean(),
        'pa_keys': g.apply(lambda x: x[['game_pk', 'at_bat_number']].drop_duplicates().shape[0]),
    })
    def _pa_with(mask, name):
        k = d[mask].groupby(level).apply(lambda x: x[['game_pk', 'at_bat_number']].drop_duplicates().shape[0])
        return k.rename(name)
    out = out.join(_pa_with(d.strikes == 2, 'pa_two_strike')).join(_pa_with(d.balls == 3, 'pa_three_ball'))
    out[['pa_two_strike', 'pa_three_ball']] = out[['pa_two_strike', 'pa_three_ball']].fillna(0)
    out['two_strike_pa_share'] = out.pa_two_strike / out.pa_keys
    out['three_ball_pa_share'] = out.pa_three_ball / out.pa_keys
    return out.reset_index().round(4)


def peer_delta_pitcher(df_all: pd.DataFrame, subject: int, metric_fn, metric_col: str,
                       y0: int, y1: int, min_pitches: int = 500):
    """PN-1 `peer_delta_pitcher` (NEW-UC45 — pitcher-side adaptation of PB-1,
    uc-pos-014 v1.1.0). Exists because O-18 (this UC): Statcast's strike-zone
    rails changed definition between 2025 and 2026, so every zone-geometry
    metric moved league-wide. A raw YoY delta cannot separate the pitcher
    from the rulebook; a peer-netted delta can.
    Cohort   : pitchers in the Phillies log (BOTH phillies_role values) with
               >= min_pitches regular-season pitches in BOTH y0 and y1.
    metric_fn: a (level, df) kernel/SZ function; metric_col its output column.
    Returns  : (tidy cohort frame, headline dict) — same keys as PB-1."""
    d = df_all[df_all.game_year.isin([y0, y1])]
    n = d.groupby(['pitcher', 'game_year']).size().unstack()
    keep = n[(n.get(y0, 0) >= min_pitches) & (n.get(y1, 0) >= min_pitches)].index
    m = metric_fn(['pitcher', 'game_year'], d[d.pitcher.isin(keep)])
    p = m.pivot(index='pitcher', columns='game_year', values=metric_col)
    p.columns = [f'val_{c}' for c in p.columns]
    p = p.dropna().copy()
    p['delta'] = p[f'val_{y1}'] - p[f'val_{y0}']
    p = p.reset_index()
    med = float(p.delta.median())
    head = {'metric': metric_col, 'y0': y0, 'y1': y1, 'cohort_n': int(len(p)),
            'min_pitches': min_pitches, 'peer_median_delta': med,
            'subject_in_cohort': bool(subject in set(p.pitcher))}
    if head['subject_in_cohort']:
        s = p[p.pitcher == subject].iloc[0]
        head.update({f'subject_{y0}': float(s[f'val_{y0}']), f'subject_{y1}': float(s[f'val_{y1}']),
                     'subject_delta': float(s.delta),
                     'peer_netted_delta': float(s.delta - med),
                     'subject_rank_most_negative': int((p.delta < s.delta).sum()) + 1})
    return p, head


def abs_rails(df_2026: pd.DataFrame) -> pd.DataFrame:
    """ZC-1 support. The 2026 per-batter zone rails. O-18 established that
    2026 sz_top/sz_bot are ONE constant per batter (ABS height-based zone);
    the modal value is taken so the rare two-valued batter resolves
    deterministically. Returns batter -> (rail_top, rail_bot)."""
    d = df_2026.dropna(subset=['sz_top', 'sz_bot'])
    return d.groupby('batter').agg(
        rail_top=('sz_top', lambda s: s.astype(float).mode().iloc[0]),
        rail_bot=('sz_bot', lambda s: s.astype(float).mode().iloc[0])).reset_index()


def common_rail_rescore(df: pd.DataFrame, rails: pd.DataFrame) -> pd.DataFrame:
    """ZC-1 `common_rail_rescore` (NEW-UC45, provisional).
    Re-scores pitches from ANY season against the batter's 2026 ABS rails, so a
    2025 pitch and a 2026 pitch to the same hitter are judged against the same
    zone. Only batters with a 2026 rail survive (coverage is reported by the
    caller). plate_x / plate_z are untouched; only the vertical rails change.
    The Statcast `zone` attribute is NOT re-derived (it cannot be) — ZC-1 is for
    geometry-based SZ metrics only."""
    m = df.merge(rails, on='batter', how='inner')
    m['sz_top_native'] = m.sz_top
    m['sz_bot_native'] = m.sz_bot
    m['sz_top'] = m.rail_top
    m['sz_bot'] = m.rail_bot
    return m


def season_label(df: pd.DataFrame) -> pd.Series:
    """2021 and 2022 merge into '2021-22' (client permission; swingman sample)."""
    return df.game_year.astype(int).map(lambda y: SEASON_MERGE.get(y, str(y)))


def half_label(df: pd.DataFrame) -> pd.Series:
    """Calendar half, cut at 07-13 (the 2026 All-Star break). Applied to every
    season identically so prior-year halves are a seasonality control, not a
    claim about those seasons' own break dates."""
    gd = pd.to_datetime(df.game_date)
    return pd.Series(np.where(gd.dt.month * 100 + gd.dt.day <= 713, '1H', '2H'),
                     index=df.index, name='half')
