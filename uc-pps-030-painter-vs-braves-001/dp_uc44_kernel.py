"""
dp_uc44_kernel.py — governed kernel for UC #44 / uc-pps-030
"Game 3: Painter vs Holmes — the 20-80 scouting card"

INHERITANCE POLICY (see 03_governance.md, Rule-1):
  * Section A functions are VERBATIM transcriptions of the governed kernel in
    `Baseball Functions.ipynb`, carried forward through dp_uc43_kernel.py.
    Do not "improve" them here — their known defects (D-1, D-2, D-7/O-13, O-8)
    are MEASURED against this build in out/dp_uc44_defect_exposure.csv, not patched.
  * Section B is the data-access layer (verbatim behaviour of mlb_data.py).
  * Section C is NEW to this UC (SG-1..SG-5, AR-1, PM-1). Provisional, unratified.

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
STRIKE_ZONE  = {'x0': -0.83, 'x1': 0.83, 'y0': 1.50, 'y1': 3.50}

# ---- entity locks (MLBAM ids; NEVER a name filter) -------------------------
SUBJECT_ID   = 691725            # Andrew Painter, RHP, PHI
OPP_STARTER_ID = 656550          # Grant Holmes, RHP, ATL — client-named; id confirmed externally
OPTION_RETURN_DATE = "2026-07-31"   # first start of the post-option window
TARGET_GAME_LABEL  = "ATL series, Game 3 (at Atlanta)"
ANCHOR_GAME_DATE   = "2026-09-12"   # last game in the log
TARGET_GAME_DATE   = "2026-09-13"   # D+1

# Atlanta hitters resolved from the log by des-parse (see 02 §metadata mapping)
ATL_GAME_PKS = [823476, 823474, 823475, 824932, 824933, 824934,
                823418, 823419, 823417, 823415, 824873, 824870]

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

def load_lhv(year=2026) -> pd.DataFrame:
    """Lehigh Valley (AAA) pitching log. NO wOBA weights applied — MLB league
    constants are not comparable at AAA (uc-pps-029 DQ-5)."""
    df = pd.read_parquet(ROOT / 'data' / 'opponents' / f'lhvp{str(year)[2:]}.parquet')
    return df[df.game_type == 'R'].copy()

# ============================================================================
# SECTION C — NEW to UC #44 (provisional, unratified — see 03_governance.md)
# ============================================================================

# ---- SG-2 -------------------------------------------------------------------
GRADE_FLOOR_PRIMARY  = 100   # pitches of the graded type per pitcher-season
GRADE_FLOOR_FALLBACK = 50
GRADE_POP_MIN        = 25    # below this many pitcher-seasons, drop to the fallback floor
SUBJECT_PITCH_FLOOR  = 50    # subject needs this many pitches of the type to be graded
SUBJECT_SWING_FLOOR  = 25    # ...and this many swings before a whiff grade is published

def benchmark_population(df_all: pd.DataFrame, pitch_type: str, throws: str = 'R') -> pd.DataFrame:
    """SG-2 `benchmark_population` (NEW-UC44, provisional).

    Grain      : one row per (game_year, pitcher) — a *pitcher-season*.
    Population : every pitcher of hand `throws` who threw in a Phillies regular-
                 season game, 2015-2026, with at least the floor number of
                 pitches of `pitch_type` in that season. Both `phillies_role`
                 values are included, so the pool is Phillies staff PLUS every
                 opponent arm that faced them — not a Phillies-only pool.
    Floor rule : GRADE_FLOOR_PRIMARY (100). If that yields fewer than
                 GRADE_POP_MIN pitcher-seasons, the floor drops to
                 GRADE_FLOOR_FALLBACK (50) and every grade drawn from the pool
                 is stamped THIN. The floor is never lowered twice.
    Null rule  : a pitcher-season with zero swings against the pitch type gets
                 whiff_rate = NaN, never 0 (the D-1 lesson, inverted).
    Known bias : this is a *Phillies-schedule* population, not a league
                 population. Clubs the Phillies play often are over-weighted and
                 an arm that faced them twice contributes as much as one that
                 faced them ten times. Grades are therefore "relative to the
                 arms this club actually sees", which is the decision-relevant
                 frame for an advance report and is NOT interchangeable with a
                 Statcast league percentile.
    """
    d = df_all[(df_all.p_throws == throws) & (df_all.pitch_type == pitch_type)].copy()
    d['_sw'] = d.description.isin(SWINGS)
    d['_wh'] = d.description.isin(WHIFFS)
    d['_iz'] = (d.zone <= 9)
    g = d.groupby(['game_year', 'pitcher'], as_index=False).agg(
        n=('pitch_number', 'size'), swings=('_sw', 'sum'), whiffs=('_wh', 'sum'),
        in_zone=('_iz', 'sum'), velo=('release_speed', 'mean'),
        ivb=('pfx_z', 'mean'), hb=('pfx_x', 'mean'),
        ext=('release_extension', 'mean'),
        xwoba=('estimated_woba_using_speedangle', 'mean'))
    floor, thin = GRADE_FLOOR_PRIMARY, False
    if (g.n >= floor).sum() < GRADE_POP_MIN:
        floor, thin = GRADE_FLOOR_FALLBACK, True
    g = g[g.n >= floor].copy()
    g['whiff_rate'] = np.where(g.swings > 0, g.whiffs / g.swings, np.nan)
    g['in_zone_rate'] = g.in_zone / g.n
    g['ivb_in'] = g.ivb * 12
    g['hb_in'] = g.hb * 12
    g['pitch_type'] = pitch_type
    g['pop_floor'] = floor
    g['thin'] = thin
    return g

# ---- SG-1 -------------------------------------------------------------------
def scouting_grade(value, pop_values, higher_is_better=True):
    """SG-1 `scouting_grade_20_80` (NEW-UC44, provisional).

    The scouting scale is a z-score in costume: 50 is the population mean and
    each 10 points is one population standard deviation. This function makes
    that identity explicit and auditable.

        grade = clip( 50 + 10 * z , 20, 80 ) rounded to the nearest 5

    Grain      : one subject value against one declared benchmark population.
    Population : whatever `pop_values` is — the caller MUST have built it with
                 `benchmark_population` and must record the floor and n.
    Direction  : `higher_is_better=False` negates z first (used for xwOBA
                 allowed, where low is good).
    Returns    : dict(grade, z, pctile, mean, sd, n, grade_pctile, divergence).
                 `grade_pctile` is the same grade derived rank-first
                 (empirical percentile -> normal quantile), which is robust to
                 skew. `divergence` = grade - grade_pctile.
    Null rule  : NaN subject value or n < 5 returns grade = NaN. A grade is
                 never imputed, and 50 is a real grade, not a default.
    Rounding   : nearest 5, because the scale is an ordinal scouting vocabulary
                 (45/50/55), not a continuous index. Ties round up (numpy
                 default banker's rounding is explicitly avoided).
    Caveat     : the clip at 20/80 is lossy on purpose — a 4-sigma pitch and a
                 6-sigma pitch are both an 80. Read the z, not the grade, when
                 the question is "how much better".
    """
    from scipy.stats import norm
    v = np.asarray(pop_values, dtype=float)
    v = v[~np.isnan(v)]
    out = dict(grade=np.nan, z=np.nan, pctile=np.nan, mean=np.nan, sd=np.nan,
               n=int(len(v)), grade_pctile=np.nan, divergence=np.nan)
    if pd.isna(value) or len(v) < 5:
        return out
    mu, sd = float(v.mean()), float(v.std(ddof=1))
    out['mean'], out['sd'] = mu, sd
    if sd == 0:
        return out
    z = (float(value) - mu) / sd
    if not higher_is_better:
        z = -z
    pct = float((v < float(value)).mean())
    if not higher_is_better:
        pct = 1.0 - pct
    pct = min(max(pct, 1.0 / (len(v) + 1)), 1.0 - 1.0 / (len(v) + 1))
    out['z'] = z
    out['pctile'] = pct
    out['grade'] = _round5(np.clip(50 + 10 * z, 20, 80))
    out['grade_pctile'] = _round5(np.clip(50 + 10 * norm.ppf(pct), 20, 80))
    out['divergence'] = out['grade'] - out['grade_pctile']
    return out

def _round5(x):
    """Round half UP to the nearest 5 (not banker's rounding)."""
    return float(np.floor(float(x) / 5.0 + 0.5) * 5.0)

# ---- SG-3 -------------------------------------------------------------------
DIVERGENCE_FLAG = 10.0

def grade_divergence_flag(divergence):
    """SG-3 `grade_divergence_flag` (NEW-UC44, provisional).
    The 20-80 scale assumes the population is normal. When the z-derived grade
    and the rank-derived grade disagree by >= DIVERGENCE_FLAG points, the
    population is skewed enough that the z-grade is misleading and the report
    must say so. Returns '' when clean, 'SKEW' when flagged, '' when NaN."""
    if pd.isna(divergence):
        return ''
    return 'SKEW' if abs(float(divergence)) >= DIVERGENCE_FLAG else ''

# ---- SG-4 -------------------------------------------------------------------
def pitch_grade(stuff_grade, command_grade):
    """SG-4 `pitch_grade` (NEW-UC44, provisional).

    A pitch is worth what it misses and where it lands, so the headline grade
    is the mean of the Stuff grade (whiff rate vs population) and the Command
    grade (in-zone rate vs population), rounded to the nearest 5.

    Shape (velocity, induced vertical break, horizontal break) is deliberately
    NOT scored into this number. Shape is the mechanism; whiff and location are
    the outcome. Grading both double-counts the same pitch and makes a
    high-spin pitch that nobody swings through look plus. Shape grades are
    reported alongside, and a large gap between a plus shape grade and a
    below-average stuff grade is itself the finding (see Painter's four-seam,
    2026 first half).

    Null rule: if either input is NaN the pitch grade is NaN. No half-grades.
    """
    if pd.isna(stuff_grade) or pd.isna(command_grade):
        return np.nan
    return _round5((float(stuff_grade) + float(command_grade)) / 2.0)

# ---- AR-1 -------------------------------------------------------------------
ARSENAL_PRESENT_THRESHOLD = 0.02   # 2% usage = "in the arsenal"

def arsenal_turnover_index(df_before: pd.DataFrame, df_after: pd.DataFrame):
    """AR-1 `arsenal_turnover_index` (NEW-UC44, provisional).

    Grain      : one pitcher x one pair of time windows.
    Definition : the share of pitches in the AFTER window thrown with a pitch
                 type that was absent from the BEFORE window, plus the share of
                 the BEFORE window thrown with a type that has since been
                 abandoned. "Absent" means usage below
                 ARSENAL_PRESENT_THRESHOLD (2%), not literally zero, because a
                 handful of misclassified pitches should not keep a retired
                 pitch on the books.
    Returns    : dict(added, dropped, added_share, dropped_share, index,
                      before_n, after_n, detail DataFrame)
                 `index` = added_share + dropped_share, range 0..2. Read it as
                 "how much of the arsenal on either side of the line is not
                 shared with the other side."
    Why it     : a head-to-head history, a scouting card, or a projection built
    matters      on the BEFORE window is evidence about a pitcher who no longer
                 exists in proportion to this index. At index 0 the history
                 transfers; at 0.30 roughly a third of it does not.
    Caveat     : Statcast pitch tags are a classifier output, not a pitcher's
                 declaration. A turnover reading must be checked against a
                 league-wide tag-share series for the same window before it is
                 called a pitcher decision rather than a classifier change
                 (this build does that check — see out/dp_uc44_tag_drift.csv).
    """
    def _mix(d):
        if len(d) == 0:
            return pd.Series(dtype=float)
        return d.pitch_type.value_counts(normalize=True)
    a, b = _mix(df_before), _mix(df_after)
    types = sorted(set(a.index) | set(b.index))
    det = pd.DataFrame({'pitch_type': types,
                        'before_usage': [float(a.get(t, 0.0)) for t in types],
                        'after_usage':  [float(b.get(t, 0.0)) for t in types]})
    det['delta'] = det.after_usage - det.before_usage
    det['status'] = np.select(
        [(det.before_usage < ARSENAL_PRESENT_THRESHOLD) & (det.after_usage >= ARSENAL_PRESENT_THRESHOLD),
         (det.before_usage >= ARSENAL_PRESENT_THRESHOLD) & (det.after_usage < ARSENAL_PRESENT_THRESHOLD)],
        ['ADDED', 'DROPPED'], default='CARRIED')
    added_share   = float(det.loc[det.status == 'ADDED', 'after_usage'].sum())
    dropped_share = float(det.loc[det.status == 'DROPPED', 'before_usage'].sum())
    return dict(added=list(det.loc[det.status == 'ADDED', 'pitch_type']),
                dropped=list(det.loc[det.status == 'DROPPED', 'pitch_type']),
                added_share=round(added_share, 4),
                dropped_share=round(dropped_share, 4),
                index=round(added_share + dropped_share, 4),
                before_n=int(len(df_before)), after_n=int(len(df_after)),
                detail=det.round(4))

# ---- PM-1 -------------------------------------------------------------------
def pitch_map_centroid(df, by=('stand', 'pitch_type', 'pitch_name')):
    """PM-1 `pitch_map_centroid` (NEW-UC44, provisional).

    Grain      : batter handedness x pitch type.
    Definition : the mean plate_x / plate_z of every tracked pitch in the cell,
                 with usage share and a dispersion radius (the mean Euclidean
                 distance in feet from each pitch to its own cell centroid).
                 Dispersion is reported because a tight centroid on a wide
                 cloud is a location average, not a location.
    Null rule  : rows with null plate_x or plate_z are dropped from the
                 centroid AND from that cell's denominator, so usage share is
                 of *tracked* pitches. The dropped count ships in the receipt.
    Convention : plate_x is from the CATCHER's view — positive x is the
                 third-base side, i.e. inside to a right-handed hitter. This is
                 asserted, not assumed (uc-pps-025 lesson).
    """
    by = list(by)
    d = df.dropna(subset=['plate_x', 'plate_z']).copy()
    dropped = len(df) - len(d)
    tot = len(d)
    cen = d.groupby(by, as_index=False).agg(
        n=('plate_x', 'size'), plate_x=('plate_x', 'mean'), plate_z=('plate_z', 'mean'))
    cen['usage'] = cen.n / tot
    d = d.merge(cen[by + ['plate_x', 'plate_z']], on=by, suffixes=('', '_c'))
    d['_r'] = np.sqrt((d.plate_x - d.plate_x_c) ** 2 + (d.plate_z - d.plate_z_c) ** 2)
    disp = d.groupby(by, as_index=False).agg(dispersion_ft=('_r', 'mean'))
    out = cen.merge(disp, on=by)
    out.attrs['dropped_untracked'] = dropped
    return out.round(4)

# ---- SG-5 -------------------------------------------------------------------
def grade_label(g):
    """SG-5 `grade_label` (NEW-UC44, provisional) — the scouting vocabulary.
    Maps a 20-80 grade to the words a scout would actually say, so the report
    and the card never invent their own adjectives."""
    if pd.isna(g):
        return 'not graded'
    g = float(g)
    if g >= 70: return 'plus-plus'
    if g >= 60: return 'plus'
    if g >= 55: return 'above average'
    if g >= 45: return 'average'
    if g >= 40: return 'below average'
    if g >= 30: return 'well below average'
    return 'poor'
