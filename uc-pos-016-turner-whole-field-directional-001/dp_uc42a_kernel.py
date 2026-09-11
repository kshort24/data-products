"""
dp_uc42a_kernel.py — v1.1.0 addendum kernel for uc-pos-016 (dp_uc42a).
============================================================================
Use case  : uc-pos-016-turner-whole-field-directional-001
Parent    : dp_uc42 v1.0.0 (2026-09-10) — this file EXTENDS it, does not
            replace it. Everything the parent already governs is imported
            from `dp_uc42_kernel`, never re-derived here.

WHAT IS NEW IN v1.1.0 AND WHY
----------------------------------------------------------------------------
The v1.0.0 finding is unchanged and is not re-litigated. Three things drove
this addendum, all client-initiated:

  1. HUMAN-IN-THE-LOOP CORRECTION (self-declared by the DPO). The chart
     requested in v1 as a "spray chart" was specified as, and built as, a
     PITCH MAP (`plate_x`/`plate_z`). A true balls-in-play spray chart
     (`hc_x`/`hc_y` -> `loc_x`/`loc_y` on the field) was the intent. Both
     now ship, cross-linked on a shared pitch key, because the link between
     them is where the v1.0.0 in-zone finding physically lives.
  2. NARRATIVE / INTERACTIVITY. v1 shipped a static facet grid; open
     decision #1 in the v1 report ("static vs animated") was explicitly left
     to the human DPO and has now been answered: SEASON-FRAME ANIMATION.
  3. CONTEXT GRAIN. The DPO supplied a Plotly cell placing Turner-2026 in a
     population of Phillies player-seasons (barrel rate x runs created, rug
     on the x-axis margin). That rug tick is the single grain the animated
     narrative descends from.

NEW-UC42a OBJECTS (provisional, pending ratification — see 03_governance.md)
----------------------------------------------------------------------------
load_phils()            pyarrow-optional parquet loader (pq_reader fallback).
build_pitch_frame()     Turner pitch-level frame carrying `pitch_uid`, the
                        join key that links the pitch map to the spray chart.
context_player_seasons()Phillies batter player-season context pool.
STRIKE_ZONE             Governed plate-side zone rectangle constants.
PA_FLOOR                50 PA — the repo's batter floor (NOT 20; confirmed by
                        repo search, see uc-pos-014 lineage).

GOVERNED FUNCTIONS TRANSCRIBED VERBATIM FROM `Baseball Functions.ipynb`
----------------------------------------------------------------------------
get_stats (cell 13), measure_calcs (cell 15), mcgs (cell 17),
nresults (cell 19), runs_created (cell 31), hard_hit_rate (cell 52),
barrel_rate (cell 58). Transcribed as-is, defects included, then each known
defect is DISCLOSED rather than silently patched:

  D-1/D-2/D-3  inner-merge drop of zero-numerator groups (hard_hit_rate's
               merge has no how='left'; a player-season with zero hard hits
               disappears instead of scoring 0.0). Measured, not assumed —
               see out/dp_uc42a_defect_exposure.csv.
  D-4          nresults() rounds to 3 dp BEFORE deriving krate/bbrate.
               Not used by this build (we consume ops/woba/plate_apps only).
  O-8          hard_hit_rate counts untracked BIP (NULL launch_speed) in the
               denominator as "not hard hit". Measured and disclosed.
  O-14         nresults().bbrate is unintentional-BB/PA. Not consumed here.
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd

# --- inherited verbatim from the parent build; nothing re-derived ----------
from dp_uc42_kernel import (                      # noqa: F401
    SUBJECT, SUBJECT_MLBAM, AS_OF,
    HC_ORIGIN_X, HC_ORIGIN_Y, HC_SCALE,
    P_THROWS_COLORS, MARKER_SIZE,
    derive_loc, hit_direction, in_zone, sort_rank,
    directional_rate_table, pooled_two_prop_z,
)

DATA = os.environ.get(
    'DP_UC42_DATA',
    r'C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB')

# NEW-UC42a — the repo batter floor, confirmed by search, not assumed
PA_FLOOR = 50

# NEW-UC42a — plate-side strike-zone rectangle used to draw the pitch map.
# Half-plate is 8.5 in = 0.7083 ft; the Statcast `zone` field remains the
# GOVERNED in/out authority (zone < 10), this is drawing geometry only.
STRIKE_ZONE = dict(x_half=0.7083, z_top=3.5, z_bot=1.5)

DIRECTION_COLORS = {          # NEW-UC42a, brand-consistent, locked like P_THROWS_COLORS
    'Pull':         '#E81828',   # Phillies Red
    'Straightaway': '#6F7378',   # Neutral grey
    'Oppo':         '#002D72',   # Phillies Navy
}

SEASONS = [2023, 2024, 2025, 2026]
CURRENT = 2026
BASELINE = [2023, 2024, 2025]


# ---------------------------------------------------------------------------
# Loading — pyarrow when present (Kellen's `snakes` env), pq_reader otherwise
# ---------------------------------------------------------------------------
LOAD_COLUMNS = [
    'game_year', 'game_date', 'game_pk', 'at_bat_number', 'pitch_number',
    'batter', 'player_name', 'p_throws', 'stand', 'pitch_type', 'pitch_name',
    'zone', 'plate_x', 'plate_z', 'sz_top', 'sz_bot', 'hc_x', 'hc_y',
    'type', 'events', 'description', 'des', 'bb_type',
    'launch_speed', 'launch_angle', 'launch_speed_angle', 'hit_distance_sc',
    'home_team', 'away_team', 'inning', 'inning_topbot', 'game_type',
    'bat_score', 'post_bat_score', 'balls', 'strikes',
]

_WEIGHT_COLS = ['wBB', 'wHBP', 'w1B', 'w2B', 'w3B', 'wHR']


def _read_one(path, columns):
    try:
        return pd.read_parquet(path, columns=columns)
    except Exception:
        import pq_reader
        data, n = pq_reader.read_parquet_columns(path, columns)
        return pd.DataFrame({c: data[c] for c in columns})


def apply_woba_weights(df, woba_csv=None):
    """VERBATIM behavior of mlb_data._apply_woba_weights: per-season weight
    merge on game_year -> Season. The per-season join is the point: dp_uc40
    once defaulted a pooled multi-season wOBA to 2026 constants and had to be
    corrected (see uc-pos-015 memory). Asserts one weight row per season so a
    duplicated constants row can never fan the frame out."""
    woba_csv = woba_csv or f'{DATA}/wOBA and FIP Constants.csv'
    weights = pd.read_csv(woba_csv)
    weights = weights[['Season'] + _WEIGHT_COLS]
    assert weights.Season.is_unique or not weights.duplicated().any(), \
        'wOBA constants: duplicate Season rows would fan out the merge'
    weights = weights.drop_duplicates(subset='Season')
    overlap = [c for c in _WEIGHT_COLS if c in df.columns]
    if overlap:
        df = df.drop(columns=overlap)
    n_before = len(df)
    out = df.merge(weights, left_on='game_year', right_on='Season',
                   suffixes=('_bad', ''), how='left')
    assert len(out) == n_before, 'wOBA weight merge changed row count (fan-out)'
    return out


def load_pos(years=SEASONS, data_dir=None):
    """Phillies BATTING rows (the `pos` frame), regular season, for `years`.
    Mirrors mlb_data._tag_phillies_role + _split_phils exactly."""
    data_dir = data_dir or DATA
    frames = []
    for y in years:
        p = f'{data_dir}/data/phillies/phils_{y}.parquet'
        if os.path.exists(p):
            frames.append(_read_one(p, LOAD_COLUMNS))
    df = pd.concat(frames, ignore_index=True)
    batting = (((df.home_team == 'PHI') & (df.inning_topbot == 'Bot'))
               | ((df.away_team == 'PHI') & (df.inning_topbot == 'Top')))
    pos = df[batting].copy()
    pos = pos[~pos.game_type.isin(['S', 'E'])].copy()
    pos['game_date'] = pd.to_datetime(pos.game_date)
    return apply_woba_weights(pos)


def turner_rows(pos):
    """Entity lock by MLBAM id, never by name (repo rule)."""
    return pos[pos.batter == SUBJECT_MLBAM].copy()


# ---------------------------------------------------------------------------
# GOVERNED TRANSCRIPTIONS — Baseball Functions.ipynb, verbatim
# ---------------------------------------------------------------------------
def get_stats(level, df):
    """VERBATIM — Baseball Functions.ipynb cell 13."""
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
    stats = p.merge(wHR, how='left', left_on=level, right_on=level)
    stats = stats.replace(np.nan, 0)
    return stats


def measure_calcs(stats):
    """VERBATIM — Baseball Functions.ipynb cell 15."""
    stats.rename(columns={'batter': 'pitches'}, inplace=True)
    stats['ba'] = stats.hits / stats.at_bats
    stats['obp'] = (stats.hits + stats.walks + stats.hbp) / (stats.plate_apps)
    stats['slg'] = (stats.singles + 2 * stats.doubles + 3 * stats.triples + 4 * stats.hrs) / (stats.at_bats)
    stats['ops'] = stats.obp + stats.slg
    stats['woba'] = (stats.wBB + stats.wHBP + stats.w1B + stats.w2B + stats.w3B + stats.wHR) / (stats.plate_apps)
    return stats


def mcgs(level, df):
    """VERBATIM — Baseball Functions.ipynb cell 17."""
    return measure_calcs(get_stats(level, df)).rename(columns={'description': 'pitches'})


def nresults(level, df):
    """VERBATIM — Baseball Functions.ipynb cell 19. D-4 (round-before-ratio)
    affects krate/bbrate only; this build consumes ops/woba/plate_apps."""
    if isinstance(level, str):
        level = [level]
    cols = level + ['pitches', 'plate_apps', 'bip', 'hits', 'hrs', 'walks',
                    'strikeouts', 'ba', 'obp', 'slg', 'ops', 'woba']
    x = mcgs(level, df).loc[:, cols].round(3)
    x['krate'] = x.strikeouts / x.plate_apps
    x['bbrate'] = x.walks / x.plate_apps        # O-14: unintentional BB / PA
    x['hr_rate'] = x.hrs / x.plate_apps
    return x.round(3)


def runs_created(level, df):
    """VERBATIM — Baseball Functions.ipynb cell 31."""
    if isinstance(level, str):
        level = [level]
    rdf = df.groupby(level + ['game_pk', 'at_bat_number'], as_index=False).agg(
        min_bs=('bat_score', 'min'), max_pbs=('post_bat_score', 'max'))
    rdf['runs_created'] = rdf.max_pbs - rdf.min_bs
    return rdf.groupby(level, as_index=False).agg(runs_created=('runs_created', 'sum'))


def hard_hit_rate(level, df):
    """VERBATIM — Baseball Functions.ipynb cell 52. Carries D-1 (inner merge
    drops zero-hard-hit groups) and O-8 (untracked BIP counted as not-hard).
    Both measured in dp_uc42a_build.py rather than assumed away."""
    hh = df[(df.launch_speed >= 95) & (df.type == 'X')].groupby(level, as_index=False).agg(
        hard_hits=('des', 'size')).merge(
        df[df.type == 'X'].groupby(level, as_index=False).agg(bips=('des', 'size')), on=level)
    hh['hard_hit_rate'] = hh.hard_hits / hh.bips
    hh['Hard Hit Rate'] = round((hh.hard_hit_rate * 100), 1)
    return hh


def barrel_rate(level, df, suffix=''):
    """VERBATIM — Baseball Functions.ipynb cell 58 (the repaired version:
    left merge + fillna(0) + zero-BIP guard already applied upstream)."""
    if isinstance(level, str):
        level = [level]
    bip_pop = df[df.type == 'X']
    bips = bip_pop.groupby(level, as_index=False).agg(bips=('des', 'size'))
    barrels = bip_pop[bip_pop.launch_speed_angle == 6].groupby(level, as_index=False).agg(barrels=('des', 'size'))
    out = bips.merge(barrels, on=level, how='left')
    out['barrels'] = out.barrels.fillna(0).astype(int)
    out['barrel_rate'] = np.where(out.bips > 0, (out.barrels / out.bips).round(3), 0)
    if suffix:
        out = out.rename(columns={'bips': f'bips{suffix}'})
    return out


# ---------------------------------------------------------------------------
# NEW-UC42a — pitch frame, BIP frame, context pool
# ---------------------------------------------------------------------------
def pitch_uid(df):
    """NEW-UC42a — the join key that links a pitch-map dot to a spray-chart
    dot. Statcast's natural pitch grain: game x at-bat x pitch number."""
    return (df.game_pk.astype('int64').astype(str) + '-'
            + df.at_bat_number.astype('int64').astype(str) + '-'
            + df.pitch_number.astype('int64').astype(str))


def build_pitch_frame(pos_subject):
    """NEW-UC42a — every regular-season pitch Turner saw, carrying plate-side
    location. This is the population the PITCH MAP draws; it is a strict
    superset of the BIP frame, linked by `pitch_uid`."""
    p = pos_subject[pos_subject.game_type == 'R'].copy()
    p['pitch_uid'] = pitch_uid(p)
    p['is_bip'] = p.type == 'X'
    p['in_zone'] = np.where(p.zone.notna(), p.zone < 10, np.nan)
    return p


def build_bip_frame(pos_rs):
    """Reproduces dp_uc42's BIP frame EXACTLY (same filters, same order of
    operations), then adds `pitch_uid` and the plate-side columns the linked
    view needs. The parent-reproduction check in dp_uc42a_verification.py
    asserts the counts match v1.0.0 row for row."""
    bip = pos_rs[pos_rs.type == 'X'].copy()
    bip = bip[bip.hc_x.notna() & bip.hc_y.notna()]
    bip = derive_loc(bip)
    bip['hit_direction'] = hit_direction(bip)
    bip = bip[bip.zone.notna()]
    bip['ooz'] = bip.zone >= 10
    bip['sort_rank'] = [sort_rank(d, s) for d, s in zip(bip.hit_direction, bip.stand)]
    bip['pitch_uid'] = pitch_uid(bip)
    med_pull_x = bip.loc[bip.hit_direction == 'Pull', 'loc_x'].median()
    assert med_pull_x < 0, (
        f'coordinate convention assertion failed: median loc_x for Pull = {med_pull_x}')
    return bip


def context_player_seasons(pos, pa_floor=PA_FLOOR):
    """NEW-UC42a — the population behind the rug. One row per Phillies batter
    player-season, regular season only, at or above the repo's 50-PA batter
    floor. Assembled with the governed functions above in the same merge order
    the DPO's own notebook cell used."""
    df = pos[pos.game_type == 'R'].copy()
    level = ['player_name', 'game_year']
    z = (df.groupby(level, as_index=False).agg(games=('game_pk', 'nunique'))
         .merge(nresults(level, df), on=level, how='left', suffixes=('', '_res'))
         .merge(runs_created(level, df), on=level, how='left', suffixes=('', '_rc'))
         .merge(hard_hit_rate(level, df), on=level, how='left', suffixes=('', '_hh'))
         .merge(barrel_rate(level, df), on=level, how='left', suffixes=('', '_br')))
    z = z[z.plate_apps >= pa_floor].copy()
    z['is_subject'] = (z.player_name == SUBJECT) & (z.game_year == CURRENT)
    z['df_color'] = np.where(z.is_subject, "Trea Turner '26", 'Context')
    return z


# ---------------------------------------------------------------------------
# NEW-UC42a provisional objects — RC-1, PM-1, PM-2
# ---------------------------------------------------------------------------
def runs_created_per_600(z):
    """RC-1 (NEW-UC42a, provisional) — PA-normalized run creation.

    WHY THIS EXISTS. The DPO's context cell plots `runs_created` (a COUNTING
    stat) against `barrel_rate` (a RATE). Playing time is then the loudest
    signal on the y-axis and the reader attributes it to the x-axis: a
    full-time .060-barrel hitter always sits above a part-time .150-barrel
    hitter, and the chart looks like barrel rate buys runs when what it is
    mostly showing is plate appearances. RC-1 puts both axes on the same
    footing. It does NOT replace `runs_created`; both ship, and the dashboard
    lets the reader switch, because the raw counting stat is the correct
    answer to 'who drove in the most runs' and the wrong answer to 'who
    creates runs best for his contact profile'.

    600 PA is a convention (roughly a qualified season), not a league
    constant; it rescales and never reranks within a fixed PA."""
    out = z.copy()
    out['runs_created_per_600'] = np.where(
        out.plate_apps > 0, out.runs_created / out.plate_apps * 600, np.nan)
    return out


def pitch_location_profile(pitches, level='game_year'):
    """PM-1 (NEW-UC42a, provisional) — per-season profile of WHERE the subject
    was pitched. This is the control on the batted-ball finding: if the
    opponent's attack plan moved between seasons, a change in batted-ball
    direction is at least partly the pitcher's doing, not the hitter's. Uses
    the governed `zone` field only; plate_x/plate_z summaries are descriptive.

    Rows with NULL `zone` are excluded from the share vector (the D-7/O-13
    standard) and counted separately so the exclusion is visible."""
    rows = []
    for val, g in pitches.groupby(level):
        z = g[g.zone.notna()]
        n = len(z)
        rec = {level: val, 'n_pitches': len(g), 'n_zone_known': n,
               'n_zone_null': int(g.zone.isna().sum()),
               'in_zone_rate': float((z.zone < 10).mean()) if n else np.nan,
               'median_plate_x': float(g.plate_x.median()),
               'median_plate_z': float(g.plate_z.median())}
        for zc in [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14]:
            rec[f'z{zc}_share'] = float((z.zone == zc).mean()) if n else np.nan
        rows.append(rec)
    return pd.DataFrame(rows)


def zone_cell_direction_mix(bip, level='game_year'):
    """PM-2 (NEW-UC42a, provisional, diagnostic-only) — in-zone batted-ball
    direction mix per Statcast zone cell. The bridge object between the pitch
    map and the spray chart: for each place the pitch was, where did the ball
    go. Not a KPI; cell counts are small by construction."""
    iz = bip[~bip.ooz].copy()
    iz['zone_int'] = iz.zone.astype(int)
    return (iz.groupby([level, 'zone_int', 'hit_direction'])
              .size().rename('n').reset_index())


# NEW-UC42a — DC-1 directional value decomposition
TOTAL_BASES = {'single': 1, 'double': 2, 'triple': 3, 'home_run': 4}


def bip_value_table(bip, level=('game_year', 'hit_direction')):
    """Per-direction production ON CONTACT. `slg_bip` is total bases per ball
    in play — NOT slugging percentage (the denominator is BIP, not at-bats),
    named distinctly so it can never be read as the league stat."""
    b = bip.copy()
    b['tb'] = b.events.map(TOTAL_BASES).fillna(0)
    b['hit'] = b.events.isin(TOTAL_BASES).astype(int)
    g = (b.groupby(list(level))
           .agg(n=('tb', 'size'), hits=('hit', 'sum'), tb=('tb', 'sum'))
           .reset_index())
    g['ba_bip'] = g.hits / g.n
    g['slg_bip'] = g.tb / g.n
    return g


def directional_value_decomposition(bip, current=CURRENT, baseline=BASELINE):
    """DC-1 (NEW-UC42a, provisional, DIAGNOSTIC-ONLY).

    Splits the change in total-bases-per-BIP into the part attributable to the
    DIRECTIONAL MIX moving (fewer pulls, more oppo) and the part attributable
    to each direction simply producing less than it used to. Standard
    two-way (Oaxaca-style) accounting identity:

        actual_gap = mix_effect + rate_effect + interaction

    THIS IS ARITHMETIC, NOT CAUSATION. It answers "how much of the observed
    drop is bookkeeping-consistent with the mix change" and nothing else. It
    cannot say the mix change caused anything, and the interaction term is
    reported rather than folded into either side so the identity stays visible.
    One season vs a three-season pool; no uncertainty band is attached because
    a decomposition of point estimates does not have one."""
    v_cur = bip_value_table(bip[bip.game_year == current], level=('hit_direction',))
    v_base = bip_value_table(bip[bip.game_year.isin(baseline)], level=('hit_direction',))
    m = v_base[['hit_direction', 'n', 'slg_bip']].merge(
        v_cur[['hit_direction', 'n', 'slg_bip']], on='hit_direction',
        suffixes=('_base', '_cur'))
    mix_b = m.n_base / m.n_base.sum()
    mix_c = m.n_cur / m.n_cur.sum()
    base_base = float((mix_b * m.slg_bip_base).sum())
    mix_only = float((mix_c * m.slg_bip_base).sum())
    rate_only = float((mix_b * m.slg_bip_cur).sum())
    actual_cur = float(m.tb_cur.sum() / m.n_cur.sum()) if 'tb_cur' in m else \
        float((mix_c * m.slg_bip_cur).sum())
    gap = actual_cur - base_base
    mix_effect = mix_only - base_base
    rate_effect = rate_only - base_base
    return pd.DataFrame([dict(
        baseline_slg_bip=base_base, current_slg_bip=actual_cur, gap=gap,
        mix_effect=mix_effect, rate_effect=rate_effect,
        interaction=gap - mix_effect - rate_effect,
        mix_share_of_gap=mix_effect / gap if gap else np.nan,
        rate_share_of_gap=rate_effect / gap if gap else np.nan,
        n_current=int(m.n_cur.sum()), n_baseline=int(m.n_base.sum()))])
