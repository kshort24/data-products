"""
dp_uc43_kernel.py — governed kernel for UC #43 / uc-pps-029
"Game 2 Bullpen Script — Mayza opens, Holman debuts"

INHERITANCE POLICY (see 03_governance.md, Rule-1):
  * Section A functions are VERBATIM transcriptions of the governed kernel in
    `Baseball Functions.ipynb`. Do not "improve" them here — their known defects
    are measured against this build in out/dp_uc43_defect_exposure.csv, not patched.
  * Section B functions are VERBATIM transcriptions of `Bullpen_Functions.ipynb`
    (appearance_summary / add_rest_days / add_rolling_workload /
     pitcher_season_workload / build_bullpen_workload).
  * Section C is NEW to this UC (BS-1..BS-5, OP-1). Provisional, unratified.

Data plane: C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB
"""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Data-root resolution (portable: env var -> sandbox mount -> Windows path)
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
SUBJECTS = {
    "Mayza, Tim":       641835,
    "Holman, Grant":    680880,
    "Raley, Brooks":    548384,
    "Shugart, Chase":   663767,
    "Kerkering, Orion": 689147,
    "Alvarado, José":   621237,
    "Duran, Jhoan":     661395,
    "McFarlane, Alex":  686934,
    "Bowlan, Jonathan": 680742,
}
OPP_STARTER_ID = 641816          # client-named "Mahle" — see 01 G-3 / 05 DQ-7
TARGET_GAME_LABEL = "ATL series, Game 2"
ANCHOR_GAME_DATE  = "2026-09-11"  # last game in the log = the client's "last night"

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

# ============================================================================
# SECTION B — VERBATIM from `Bullpen_Functions.ipynb` (locked, do not edit)
# ============================================================================
def appearance_summary(df, mcgs_func=None):
    df = df.copy()
    keys = ['pitcher', 'player_name', 'game_year', 'game_date', 'game_pk', 'home_team', 'away_team']
    agg = (df.groupby(keys, as_index=False, dropna=False)
             .agg(pitches=('pitch_number', 'count'),
                  batters_faced=('at_bat_number', 'nunique'),
                  inning_entered=('inning', 'min'),
                  inning_exited=('inning', 'max')))
    agg['innings_spanned'] = agg['inning_exited'] - agg['inning_entered'] + 1
    first_pitch = df[(df['inning'] == 1) & (df['pitch_number'] == 1)].copy()
    first_pitch = (first_pitch.sort_values(['game_pk', 'inning_topbot', 'at_bat_number'])
                   .groupby(['game_pk', 'inning_topbot'], as_index=False)
                   .first()[['game_pk', 'inning_topbot', 'pitcher']]
                   .rename(columns={'pitcher': 'starter_pitcher'}))
    agg = agg.merge(
        first_pitch[first_pitch['inning_topbot'] == 'Top'].rename(columns={'starter_pitcher': 'home_starter'}).drop(columns='inning_topbot'),
        on='game_pk', how='left').merge(
        first_pitch[first_pitch['inning_topbot'] == 'Bot'].rename(columns={'starter_pitcher': 'away_starter'}).drop(columns='inning_topbot'),
        on='game_pk', how='left')
    agg['is_start'] = ((agg['pitcher'] == agg['home_starter']) | (agg['pitcher'] == agg['away_starter']))
    agg = agg.drop(columns=['home_starter', 'away_starter'])
    if mcgs_func is not None:
        mcgs_out = mcgs_func(['pitcher', 'game_pk'], df)[['pitcher', 'game_pk', 'plate_apps', 'bip', 'hits',
                                                          'hrs', 'walks', 'strikeouts', 'ba', 'obp', 'slg', 'ops', 'woba']]
        agg = agg.merge(mcgs_out, on=['pitcher', 'game_pk'], how='left')
    agg = agg.sort_values(['pitcher', 'game_date', 'game_pk']).reset_index(drop=True)
    return agg

def add_rest_days(apps, within='season'):
    df = apps.copy()
    df['game_date'] = pd.to_datetime(df['game_date'])
    grp = ['pitcher', 'game_year'] if within == 'season' else ['pitcher']
    df = df.sort_values(grp + ['game_date', 'game_pk']).reset_index(drop=True)
    df['prev_appearance_date'] = df.groupby(grp)['game_date'].shift(1)
    df['days_between'] = (df['game_date'] - df['prev_appearance_date']).dt.days
    df['days_of_rest'] = df['days_between'] - 1
    return df

def add_rolling_workload(apps, windows=(3, 7, 14)):
    df = apps.copy()
    df['game_date'] = pd.to_datetime(df['game_date'])
    df = df.sort_values(['pitcher', 'game_year', 'game_date', 'game_pk']).reset_index(drop=True)
    for n in windows:
        pitches_col, apps_col = f'pitches_last_{n}d', f'appearances_last_{n}d'
        df[pitches_col] = 0
        df[apps_col] = 0
        for (pid, yr), g in df.groupby(['pitcher', 'game_year'], sort=False):
            g = g.sort_values(['game_date', 'game_pk'])
            dates, pcs = g['game_date'].values, g['pitches'].values
            p_roll = np.zeros(len(g)); a_roll = np.zeros(len(g), dtype=int)
            for i in range(len(g)):
                lo = dates[i] - np.timedelta64(n, 'D')
                hi = dates[i] - np.timedelta64(1, 'D')
                mask = (dates >= lo) & (dates <= hi)
                p_roll[i] = pcs[mask].sum(); a_roll[i] = mask.sum()
            df.loc[g.index, pitches_col] = p_roll
            df.loc[g.index, apps_col] = a_roll
    return df

def pitcher_season_workload(apps, relievers_only=True):
    df = apps.copy()
    if relievers_only and 'is_start' in df.columns:
        df = df[~df['is_start']].copy()
    has_rolling = 'appearances_last_3d' in df.columns
    df['_is_3in4'] = (df['appearances_last_3d'] >= 2) if has_rolling else False
    df['_is_b2b'] = df['days_of_rest'] == 0
    df['_is_multi_inning'] = df['innings_spanned'] >= 2
    out = (df.groupby(['pitcher', 'player_name', 'game_year'], as_index=False)
             .agg(appearances=('game_pk', 'nunique'), total_pitches=('pitches', 'sum'),
                  total_bf=('batters_faced', 'sum'), avg_pitches=('pitches', 'mean'),
                  avg_bf=('batters_faced', 'mean'), avg_days_of_rest=('days_of_rest', 'mean'),
                  median_days_of_rest=('days_of_rest', 'median'), b2b_appearances=('_is_b2b', 'sum'),
                  three_in_four=('_is_3in4', 'sum'), multi_inning_apps=('_is_multi_inning', 'sum')))
    out['pct_b2b'] = (out['b2b_appearances'] / out['appearances']).round(3)
    for c in ['avg_pitches', 'avg_bf', 'avg_days_of_rest', 'median_days_of_rest']:
        out[c] = out[c].round(2)
    return out.sort_values(['game_year', 'appearances'], ascending=[True, False]).reset_index(drop=True)

def build_bullpen_workload(df, mcgs_func=None, windows=(3, 7, 14), relievers_only=True):
    apps = appearance_summary(df, mcgs_func=mcgs_func)
    apps = add_rest_days(apps, within='season')
    apps = add_rolling_workload(apps, windows=windows)
    season = pitcher_season_workload(apps, relievers_only=relievers_only)
    return apps, season

# ============================================================================
# SECTION C — NEW to UC #43 (provisional, unratified — see 03_governance.md)
# ============================================================================
def apply_woba_weights(df: pd.DataFrame) -> pd.DataFrame:
    """Verbatim behaviour of mlb_data._apply_woba_weights. MLB league constants —
    DO NOT apply to minor-league frames (comparability, see 05 DQ-5)."""
    weights = pd.read_csv(WOBA_CSV)
    overlap = [c for c in weights.columns if c != 'Season' and c in df.columns]
    if overlap:
        df = df.drop(columns=overlap)
    return df.merge(weights, left_on='game_year', right_on='Season', suffixes=('_bad', ''), how='left')

def load_pps(years=(2026,)) -> pd.DataFrame:
    """Phillies pitching-staff pitch log, regular season, wOBA-weighted."""
    frames = [pd.read_parquet(ROOT / 'data' / 'phillies' / f'phils_{y}.parquet') for y in years]
    df = pd.concat(frames, ignore_index=True)
    df = df[(df.game_type == 'R') & (df.phillies_role == 'pitching')].copy()
    return apply_woba_weights(df)

def load_pos(years=(2026,)) -> pd.DataFrame:
    frames = [pd.read_parquet(ROOT / 'data' / 'phillies' / f'phils_{y}.parquet') for y in years]
    df = pd.concat(frames, ignore_index=True)
    df = df[(df.game_type == 'R') & (df.phillies_role == 'batting')].copy()
    return apply_woba_weights(df)

def load_lhv(year=2026) -> pd.DataFrame:
    """Lehigh Valley (AAA) pitching log. NO wOBA weights applied — see 05 DQ-5."""
    df = pd.read_parquet(ROOT / 'data' / 'opponents' / f'lhvp{str(year)[2:]}.parquet')
    return df[df.game_type == 'R'].copy()

# ---- BS-1 -------------------------------------------------------------------
AVAILABILITY_TIERS = ['GREEN', 'AMBER', 'RED']

def bullpen_availability_tier(days_of_rest, pitches_last_3d, appearances_last_3d,
                              pitches_yesterday, season_avg_pitches):
    """BS-1 `bullpen_availability_tier` (NEW-UC43, provisional).

    Grain      : one pitcher × one target game.
    Population : Phillies relievers with >=1 logged 2026 appearance.
    Definition : RED   if the arm threw yesterday AND yesterday's pitch count
                        was at or above his season average outing, OR he has
                        made 3 appearances in the last 3 days.
                 AMBER if he threw yesterday below his season average, OR he
                        has 2 appearances in the last 3 days, OR his 3-day
                        pitch load is >= 1.5x his season average outing.
                 GREEN otherwise.
    Null rule  : a pitcher with no prior 2026 appearance (season debut) is GREEN
                 with a `debut` flag — rest is undefined, not zero.
    Rationale  : the client's premise ("four arms down") treats *an appearance*
                 as the unit of unavailability. The log shows pitch count and
                 appearance density diverge sharply; this tier separates them.
    """
    if pd.isna(days_of_rest):
        return 'GREEN', 'debut/no prior 2026 outing'
    d = float(days_of_rest); p3 = float(pitches_last_3d); a3 = float(appearances_last_3d)
    py = float(pitches_yesterday); avg = float(season_avg_pitches)
    if (d == 0 and py >= avg) or a3 >= 3:
        return 'RED', f'{int(py)}p on 0 days rest (season avg {avg:.0f}p)' if d == 0 else f'{int(a3)} apps in 3d'
    if (d == 0 and py < avg):
        return 'AMBER', f'{int(py)}p on 0 days rest, below his {avg:.0f}p average'
    if a3 >= 2:
        return 'AMBER', f'{int(a3)} apps in last 3d'
    if avg > 0 and p3 >= 1.5 * avg:
        return 'AMBER', f'{int(p3)}p in last 3d vs {avg:.0f}p avg outing'
    return 'GREEN', f'{int(d)} days rest, {int(p3)}p in last 3d'

# ---- BS-2 -------------------------------------------------------------------
def script_coverage(script_rows):
    """BS-2 `script_coverage_risk` (NEW-UC43, provisional).
    Input : ordered list of dicts {inning, pitcher, tier, expected_innings}
    Output: dict with innings_scripted, expected_innings_delivered, shortfall,
            and the first inning at which cumulative expected coverage falls
            below the scripted inning number.
    """
    scripted = len(script_rows)
    cum, breach = 0.0, None
    for i, r in enumerate(script_rows, start=1):
        cum += float(r['expected_innings'])
        if breach is None and cum < i:
            breach = i
    return {'innings_scripted': scripted,
            'expected_innings_delivered': round(cum, 2),
            'shortfall': round(scripted - cum, 2),
            'first_breach_inning': breach}

def script_capacity(script, mean_bf, max_bf, mode='average'):
    """BS-2b `script_capacity` (NEW-UC43, provisional).

    Each arm delivers ONE outing however many innings the script gives him, so
    capacity is summed over DISTINCT arms, not over slots.
      mode='average' : every arm delivers his 2026 mean BF. The conservative read.
      mode='ceiling' : an arm asked for >=2 innings delivers his observed max BF
                       for the season; a one-inning arm still delivers his mean.
                       The "everybody goes to his high-water mark" read.
    The ceiling number is only as good as the evidence behind each ceiling — an
    AAA maximum is not an MLB maximum, and the caller must say so.
    """
    slots = {}
    for arm in script:
        if arm:
            slots[arm] = slots.get(arm, 0) + 1
    rows = []
    for arm, k_ in slots.items():
        if mode == 'ceiling' and k_ >= 2 and arm in max_bf and not pd.isna(max_bf[arm]):
            bf, basis = float(max_bf[arm]), f'season max BF ({k_} innings asked)'
        else:
            bf, basis = float(mean_bf[arm]), 'mean outing'
        rows.append(dict(arm=arm, innings=k_, bf=round(bf, 2), basis=basis))
    return pd.DataFrame(rows), round(float(sum(r['bf'] for r in rows)), 2)

# ---- BS-3 -------------------------------------------------------------------
def multi_inning_propensity(apps, pitcher_id, year=None, pitch_floor=30):
    """BS-3 `multi_inning_propensity` (NEW-UC43, provisional).
    Share of a pitcher's RELIEF outings spanning >=2 innings, and the share
    reaching `pitch_floor` pitches. Grain: pitcher x season (or career if
    year is None). Zero-denominator returns NaN, never 0 (D-1 lesson)."""
    d = apps[(apps.pitcher == pitcher_id) & (~apps.is_start)]
    if year is not None:
        d = d[d.game_year == year]
    n = len(d)
    if n == 0:
        return {'relief_apps': 0, 'multi_inning_apps': 0, 'multi_inning_rate': np.nan,
                'apps_ge_floor': 0, 'rate_ge_floor': np.nan, 'max_pitches': np.nan,
                'p80_pitches': np.nan}
    return {'relief_apps': n,
            'multi_inning_apps': int((d.innings_spanned >= 2).sum()),
            'multi_inning_rate': round(float((d.innings_spanned >= 2).mean()), 3),
            'apps_ge_floor': int((d.pitches >= pitch_floor).sum()),
            'rate_ge_floor': round(float((d.pitches >= pitch_floor).mean()), 3),
            'max_pitches': int(d.pitches.max()),
            'p80_pitches': float(np.percentile(d.pitches, 80))}

# ---- OP-1 -------------------------------------------------------------------
def tto_split(df, pitcher_id):
    """OP-1 `opener_tto_delta` (NEW-UC43, provisional).
    Results-against split by `n_thruorder_pitcher` for one pitcher.
    Answers: does this arm hold up a second time through? Grain: pitcher x TTO.
    """
    d = df[df.pitcher == pitcher_id].copy()
    d['tto'] = d['n_thruorder_pitcher']
    base = nresults(['tto'], d)
    wr = whiff_rate(['tto'], d)
    return base.merge(wr[['tto', 'swings', 'whiffs', 'whiff_rate']], on='tto', how='left')

# ---- BS-5 -------------------------------------------------------------------
def two_prop_z(x1, n1, x2, n2):
    """Pooled two-proportion z — the repo's standing significance test."""
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
