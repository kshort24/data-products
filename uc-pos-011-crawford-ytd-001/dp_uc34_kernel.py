"""
dp_uc34_kernel.py — data loader + governed KPI kernel for uc-pos-011
====================================================================
Use case  : uc-pos-011-crawford-ytd-001 (Phillies Offense, Justin Crawford)
Data plane: C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB

Every function here is either (a) transcribed from `Baseball Functions.ipynb`
— the governed authority — or (b) a NEW function introduced by this UC and
marked as such.

Defect handling follows the uc-pos-010 precedent: a governed function carrying
a defect is NOT silently patched. A `_fix` variant is added beside it, the
original is retained upstream, and both are reported in 05_quality.

INHERITED DEFECT REGISTER (opened uc-pos-010, still open repo-wide — O-2/O-3)
----------------------------------------------------------------------------
D1  whiff_rate      inner-merges swings->whiffs; a level group with swings but
                    ZERO whiffs vanishes from the output entirely.
D2  hard_hit_rate   same inner-merge shape: a group with BIP but zero hard hits
                    vanishes.
D3  fpsr            groups by level+['type'] then returns only type=='B'; a
                    group with ZERO first-pitch balls (a perfect 1.000 FPSR)
                    vanishes.
D4  nresults        rounds rates to 3dp on return. Any ratio built from two
                    nresults rates inherits that rounding.
D5  pull_air_rate   references `loc_x`/`loc_y`, which do NOT exist in the
                    parquet schema (`hc_x`/`hc_y` do). NEW THIS BUILD — the
                    function cannot execute against the governed data plane.
                    Not used here; reported as O-7.

D1-D3 share one root cause and one consequence: they drop zero-numerator groups,
which a downstream left-merge renders NaN, which a blanket `.fillna(0)` then
converts into a *measured zero*. No blanket fillna is used in this build.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

# Data plane root. Defaults to the MLB repo on the DPO's machine; override with
# the DP_UC34_DATA environment variable (the build sandbox sets it to a staged copy).
DATA = os.environ.get(
    'DP_UC34_DATA',
    r'C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB')
SUBJECT = 'Crawford, Justin'
SUBJECT_MLBAM = 702222              # confirmed by filter, not assumed
AS_OF = '2026-08-13'                # max game_date in the pos frame
BREAK = '2026-06-15'                # DPO narrative breakpoint ("roughly mid-June")
HILL_DEBUT = '2026-06-13'           # Derek Hill first PHI game, derived not assumed
PA_FLOOR = 50                       # standing batter rate-stat floor
BIP_FLOOR = 50                      # metric-specific floor for LA / bb-type shares

# ══════════════════════════════════════════════════════════════════════════
# GOVERNED CONSTANTS — Baseball Functions.ipynb is the authority (uc-pos-010 B-1)
# ══════════════════════════════════════════════════════════════════════════
SWINGS = ['foul', 'foul_bunt', 'foul_tip', 'hit_into_play', 'missed_bunt',
          'swinging_pitchout', 'swinging_strike', 'swinging_strike_blocked']
WHIFFS = ['foul_tip', 'missed_bunt', 'swinging_pitchout', 'swinging_strike',
          'swinging_strike_blocked']

NON_PA = ['NA', 'pickoff_1b', 'pickoff_2b', 'pickoff_3b',
          'caught_stealing_2b', 'caught_stealing_3b', 'caught_stealing_home',
          'stolen_base_2b', 'stolen_base_3b', 'stolen_base_home',
          'pickoff_caught_stealing_2b', 'pickoff_caught_stealing_3b',
          'pickoff_caught_stealing_home', 'wild_pitch', 'passed_ball',
          'other_advance', 'runner_double_play', 'defensive_indiff',
          'balk', 'game_advisory', 'ejection']
K_EV = {'strikeout', 'strikeout_double_play'}
BB_EV = {'walk', 'intent_walk'}
HIT_EV = {'single', 'double', 'triple', 'home_run'}
NON_AB = {'walk', 'intent_walk', 'hit_by_pitch', 'sac_fly', 'sac_bunt',
          'sac_fly_double_play', 'sac_bunt_double_play', 'catcher_interf'}

# canonical map — dp_uc18_marsh_breakout.py L170
PITCH_GROUP = {
    'FF': 'fastball', 'SI': 'fastball', 'FC': 'fastball',
    'SL': 'breaking', 'ST': 'breaking', 'CU': 'breaking', 'KC': 'breaking',
    'SV': 'breaking', 'CS': 'breaking',
    'CH': 'offspeed', 'FS': 'offspeed', 'FO': 'offspeed', 'SC': 'offspeed',
    'KN': 'offspeed',
}


def _sz(*_):
    return ('des', 'size')


def _lv(level):
    return [level] if isinstance(level, str) else list(level)


# ══════════════════════════════════════════════════════════════════════════
# Loader — mirrors mlb_data._tag_phillies_role / _split_phils
# ══════════════════════════════════════════════════════════════════════════
def load_frames(years=range(2015, 2027)):
    """Returns (pos, pps). pos = PHI batting; pps = PHI pitching.
    Regular season + postseason; Spring ('S') and Exhibition ('E') excluded."""
    frames = []
    for y in years:
        p = f'{DATA}/data/phillies/phils_{y}.parquet'
        if os.path.exists(p):
            frames.append(pd.read_parquet(p))
    df = pd.concat(frames, ignore_index=True)
    batting = (((df.home_team == 'PHI') & (df.inning_topbot == 'Bot'))
               | ((df.away_team == 'PHI') & (df.inning_topbot == 'Top')))
    pos = df[batting].copy()
    pps = df[~batting].copy()
    for d in (pos, pps):
        pass
    pos = pos[~pos.game_type.isin(['S', 'E'])].copy()
    pps = pps[~pps.game_type.isin(['S', 'E'])].copy()
    for d in (pos, pps):
        d['game_date'] = pd.to_datetime(d.game_date)
        d['month'] = d.game_date.dt.month           # calendar, no Mar/Apr merge
        d['pitch_group'] = d.pitch_type.map(PITCH_GROUP).fillna('other')
    return pos, pps


def woba_weights():
    return pd.read_csv(f'{DATA}/wOBA and FIP Constants.csv')


def pa_rows(df):
    """Terminal plate-appearance rows."""
    return df[~df.events.replace(np.nan, 'NA').isin(NON_PA)]


# ══════════════════════════════════════════════════════════════════════════
# GOVERNED (rebuilt) — results
# ══════════════════════════════════════════════════════════════════════════
def nresults_unrounded(level, df, woba_w):
    """D4-corrected `nresults`. Slash line and wOBA from COUNTS, no 3dp round.
    wOBA uses seasonal constants from `wOBA and FIP Constants.csv`; IBB is
    excluded from the numerator and the denominator (the wOBA convention,
    matching dp_uc24's running_line weight map)."""
    level = _lv(level)
    pa = pa_rows(df).copy()
    g = lambda d, n: d.groupby(level, as_index=False).agg(**{n: _sz()})

    out = g(pa, 'plate_apps')
    out = out.merge(df.groupby(level, as_index=False).agg(pitches=_sz()),
                    on=level, how='left')
    for name, mask in [
        ('at_bats',     ~pa.events.isin(NON_AB)),
        ('hits',         pa.events.isin(HIT_EV)),
        ('walks',        pa.events.isin(BB_EV)),
        ('unint_walks',  pa.events == 'walk'),
        ('hbp',          pa.events == 'hit_by_pitch'),
        ('strikeouts',   pa.events.isin(K_EV)),
        ('sf',           pa.events == 'sac_fly'),
        ('singles',      pa.events == 'single'),
        ('doubles',      pa.events == 'double'),
        ('triples',      pa.events == 'triple'),
        ('hrs',          pa.events == 'home_run'),
        ('bip',          pa.type == 'X'),
    ]:
        out = out.merge(g(pa[mask], name), on=level, how='left')
        out[name] = out[name].fillna(0).astype(int)     # counts — genuinely zero

    tb = out.singles + 2 * out.doubles + 3 * out.triples + 4 * out.hrs
    obp_den = out.at_bats + out.walks + out.hbp + out.sf
    out['ba'] = np.where(out.at_bats > 0, out.hits / out.at_bats, np.nan)
    out['obp'] = np.where(obp_den > 0,
                          (out.hits + out.walks + out.hbp) / obp_den, np.nan)
    out['slg'] = np.where(out.at_bats > 0, tb / out.at_bats, np.nan)
    out['ops'] = out.obp + out.slg
    out['iso'] = out.slg - out.ba
    out['krate'] = out.strikeouts / out.plate_apps
    out['bbrate'] = out.walks / out.plate_apps
    # BABIP — NEW (CR-4). AB - K - HR + SF is the standard denominator.
    bab_den = out.at_bats - out.strikeouts - out.hrs + out.sf
    out['babip'] = np.where(bab_den > 0, (out.hits - out.hrs) / bab_den, np.nan)

    w = woba_w.set_index('Season')
    has_year = 'game_year' in level

    def _woba(r):
        y = int(r.game_year) if has_year else 2026
        if y not in w.index:
            return np.nan
        c = w.loc[y]
        num = (c.wBB * r.unint_walks + c.wHBP * r.hbp + c['w1B'] * r.singles
               + c['w2B'] * r.doubles + c['w3B'] * r.triples + c.wHR * r.hrs)
        den = r.at_bats + r.unint_walks + r.sf + r.hbp
        return num / den if den > 0 else np.nan

    out['woba'] = out.apply(_woba, axis=1)
    return out


# ══════════════════════════════════════════════════════════════════════════
# GOVERNED — approach
# ══════════════════════════════════════════════════════════════════════════
def whiff_rate_fix(level, df):
    """D1-corrected: left-merge so zero-whiff groups survive."""
    level = _lv(level)
    u = df[df.description.isin(SWINGS)].groupby(level, as_index=False).agg(swings=_sz())
    v = df[df.description.isin(WHIFFS)].groupby(level, as_index=False).agg(whiffs=_sz())
    w = u.merge(v, on=level, how='left')
    w['whiffs'] = w.whiffs.fillna(0).astype(int)
    w['whiff_rate'] = np.where(w.swings > 0, w.whiffs / w.swings, np.nan)
    return w


def chase_rate_g(level, df):
    """Governed logic (no defect found). `in_zone_rate` is a PITCHER metric —
    see RC-4, it must not be read as hitter behaviour."""
    level = _lv(level)
    chase = df[(df.zone > 9) & (df.description.isin(SWINGS))]
    i = chase.groupby(level, as_index=False).agg(chases=_sz())
    j = df[df.zone > 9].groupby(level, as_index=False).agg(ooz=_sz())
    cr = (i.merge(j, on=level, how='right')
           .merge(df.groupby(level, as_index=False).agg(pitches=_sz()),
                  on=level, how='right'))
    cr['chases'] = cr.chases.fillna(0)
    cr['chase_rate'] = np.where(cr.ooz > 0, cr.chases / cr.ooz, np.nan)
    cr['in_zone_rate'] = (cr.pitches - cr.ooz) / cr.pitches
    return cr


def swing_rate(level, df):
    """AP-2 (uc-pos-010, provisional). Inherits the governed SWINGS list."""
    level = _lv(level)
    s = df[df.description.isin(SWINGS)].groupby(level, as_index=False).agg(swings=_sz())
    p = df.groupby(level, as_index=False).agg(pitches=_sz())
    out = p.merge(s, on=level, how='left')
    out['swings'] = out.swings.fillna(0).astype(int)
    out['swing_rate'] = np.where(out.pitches > 0, out.swings / out.pitches, np.nan)
    return out


def ooz_whiff_rate(level, df):
    """uc-cat-001 same-filter-both-sides correction:
    (ooz & swing & whiff) / (ooz & swing)."""
    level = _lv(level)
    ooz = df[df.zone > 9]
    return whiff_rate_fix(level, ooz).rename(
        columns={'swings': 'ooz_swings', 'whiffs': 'ooz_whiffs',
                 'whiff_rate': 'ooz_whiff_rate'})


def fpsr_fix(level, df):
    """D3-corrected. `fpsr` is APPROVED (cde.fpsr, Rangel contract) and is
    CONSUMED here, not redefined. Formula unchanged:
    (first_pitches - first_pitch_balls) / first_pitches over pitch_number == 1.
    This is a PITCHER metric on a hitter panel — see RC-4."""
    level = _lv(level)
    fp = df[df.pitch_number == 1]
    p = fp.groupby(level, as_index=False).agg(first_pitches=_sz())
    b = fp[fp.type == 'B'].groupby(level, as_index=False).agg(first_pitch_balls=_sz())
    out = p.merge(b, on=level, how='left')
    out['first_pitch_balls'] = out.first_pitch_balls.fillna(0).astype(int)
    out['fpsr'] = (out.first_pitches - out.first_pitch_balls) / out.first_pitches
    return out


def srfp(level, df):
    """AP-3 (uc-pos-010, provisional) — swing rate on the first pitch."""
    level = _lv(level)
    out = swing_rate(level, df[df.pitch_number == 1])
    return out.rename(columns={'pitches': 'first_pitches',
                               'swings': 'first_pitch_swings',
                               'swing_rate': 'srfp'})


# ══════════════════════════════════════════════════════════════════════════
# GOVERNED — contact
# ══════════════════════════════════════════════════════════════════════════
def hard_hit_rate_fix(level, df):
    """D2-corrected."""
    level = _lv(level)
    bip = df[df.type == 'X']
    d = bip.groupby(level, as_index=False).agg(bips=_sz())
    n = bip[bip.launch_speed >= 95].groupby(level, as_index=False).agg(hard_hits=_sz())
    out = d.merge(n, on=level, how='left')
    out['hard_hits'] = out.hard_hits.fillna(0).astype(int)
    out['hard_hit_rate'] = np.where(out.bips > 0, out.hard_hits / out.bips, np.nan)
    return out


def barrel_rate_g(level, df):
    """Governed logic — already handles the zero-numerator case."""
    level = _lv(level)
    bip = df[df.type == 'X']
    d = bip.groupby(level, as_index=False).agg(bips=_sz())
    n = bip[bip.launch_speed_angle == 6].groupby(level, as_index=False).agg(barrels=_sz())
    out = d.merge(n, on=level, how='left')
    out['barrels'] = out.barrels.fillna(0).astype(int)
    out['barrel_rate'] = np.where(out.bips > 0, out.barrels / out.bips, np.nan)
    return out


def battedball_profile(level, df, bip_floor=BIP_FLOOR):
    """CR-1 — NEW-PROVISIONAL. Batted-ball type shares plus launch-angle
    central tendency on TRACKED balls in play.

    Sensor-boundary NULL standard (uc-pos-009): an untracked BIP is not a
    zero-launch-angle BIP. Shares are computed over ALL BIP (bb_type is
    classifier-derived and complete); launch-angle statistics are computed
    over tracked BIP only and are NULL below `bip_floor`.
    """
    level = _lv(level)
    bip = df[df.type == 'X']
    tot = bip.groupby(level, as_index=False).agg(bips=_sz())
    bt = bip.groupby(level + ['bb_type'], as_index=False).agg(n=_sz())
    piv = bt.pivot_table(index=level, columns='bb_type', values='n',
                         fill_value=0).reset_index()
    out = tot.merge(piv, on=level, how='left')
    for src, short in [('ground_ball', 'gb'), ('fly_ball', 'fb'),
                       ('line_drive', 'ld'), ('popup', 'pu')]:
        if src not in out.columns:
            out[src] = 0
        out[src] = out[src].fillna(0).astype(int)
        out[f'{short}_rate'] = out[src] / out.bips
    tr = bip[bip.launch_speed.notna() & bip.launch_angle.notna()]
    la = tr.groupby(level, as_index=False).agg(
        tracked_bips=_sz(), mean_la=('launch_angle', 'mean'),
        median_la=('launch_angle', 'median'), mean_ev=('launch_speed', 'mean'))
    out = out.merge(la, on=level, how='left')
    out['tracked_bips'] = out.tracked_bips.fillna(0).astype(int)
    out.loc[out.tracked_bips < bip_floor,
            ['mean_la', 'median_la', 'mean_ev']] = np.nan
    return out


def xcontact(level, df, bip_floor=BIP_FLOOR):
    """CR-2 — NEW-PROVISIONAL. Mean expected outcome on contact.

    ⚠ `estimated_woba_using_speedangle` is a BIP-level Statcast estimate. It is
    averaged over BIP here and is therefore xwOBAcon, NOT xwOBA — the two have
    different denominators and must never be compared to `woba` directly.
    Named `xwobacon_bip` per open item O-4 (uc-pps-025).
    """
    level = _lv(level)
    bip = df[df.type == 'X']
    out = bip.groupby(level, as_index=False).agg(
        bips=_sz(),
        xba_bip=('estimated_ba_using_speedangle', 'mean'),
        xwobacon_bip=('estimated_woba_using_speedangle', 'mean'),
        xba_tracked=('estimated_ba_using_speedangle', 'count'))
    out.loc[out.xba_tracked < bip_floor, ['xba_bip', 'xwobacon_bip']] = np.nan
    return out


# ══════════════════════════════════════════════════════════════════════════
# NEW — this UC
# ══════════════════════════════════════════════════════════════════════════
def running_line_pa(df, woba_w, group='game_year'):
    """AP-6 (uc-pos-010) EXTENDED — cumulative wOBA **plus BA and OBP** indexed
    by cumulative PA within `group`. The BA/OBP extension is what makes the
    three-panel context ghost-line chart possible (CR-3).

    Ordered by game_date -> game_pk -> at_bat_number. Regular + postseason.
    """
    pa = pa_rows(df).sort_values([group, 'game_date', 'game_pk',
                                  'at_bat_number']).copy()
    w = woba_w.set_index('Season')
    n = len(pa)
    num = np.zeros(n); den = np.zeros(n)
    h = np.zeros(n); ab = np.zeros(n); ob = np.zeros(n); obd = np.zeros(n)
    ev = pa.events.to_numpy(); yr = pa.game_year.to_numpy()
    for i in range(n):
        y = int(yr[i]); e = ev[i]
        if y in w.index:
            c = w.loc[y]
            num[i] = {'walk': c.wBB, 'hit_by_pitch': c.wHBP, 'single': c['w1B'],
                      'double': c['w2B'], 'triple': c['w3B'],
                      'home_run': c.wHR}.get(e, 0.0)
            den[i] = 0.0 if e in ('intent_walk', 'sac_bunt') else 1.0
        ab[i] = 0.0 if e in NON_AB else 1.0
        h[i] = 1.0 if e in HIT_EV else 0.0
        ob[i] = 1.0 if (e in HIT_EV or e in BB_EV or e == 'hit_by_pitch') else 0.0
        obd[i] = ab[i] + (1.0 if (e in BB_EV or e == 'hit_by_pitch'
                                  or e == 'sac_fly') else 0.0)
    pa['_n'], pa['_d'], pa['_h'], pa['_ab'], pa['_ob'], pa['_obd'] = \
        num, den, h, ab, ob, obd
    g = pa.groupby(group)
    pa['cum_pa'] = g.cumcount() + 1
    pa['cum_woba'] = g._n.cumsum() / g._d.cumsum().replace(0, np.nan)
    pa['cum_ba'] = g._h.cumsum() / g._ab.cumsum().replace(0, np.nan)
    pa['cum_obp'] = g._ob.cumsum() / g._obd.cumsum().replace(0, np.nan)
    cols = [group, 'game_year', 'game_date', 'cum_pa',
            'cum_ba', 'cum_obp', 'cum_woba']
    cols = list(dict.fromkeys(cols))
    return pa[cols].reset_index(drop=True)


def cf_context_pool(pos, pps, min_cf_games=80, min_cf_pitches=10):
    """CX-1 — NEW-PROVISIONAL. Transcribed from the DPO's submitted notebook
    snippet without alteration of its thresholds.

    Defines the comparison population as **Phillies primary centre fielders in
    the Statcast era** and restricts each comparator's PA to games in which he
    actually played centre.

    Step 1  fielder_8 on the PHI-pitching frame identifies who played CF, by
            game, for the Phillies. Joined to the batting frame on
            fielder_8 == batter to recover the name.
    Step 2  keep player-seasons with > `min_cf_games` unique CF games
            (DPO ruling: half a season, 81 games).
    Step 3  keep games in which he took > `min_cf_pitches` defensive pitches in
            CF, then inner-join his batting rows for those games.

    Returns (cntxt_rows, pool_seasons).
    """
    cf8 = (pps.groupby(['game_year', 'fielder_8'], as_index=False)
              .agg(uq_cf_games=('game_pk', 'nunique'))
              .merge(pos.groupby(['player_name', 'batter'], as_index=False)
                        .agg(pitches=_sz()),
                     left_on=['fielder_8'], right_on=['batter'],
                     how='inner', suffixes=('_cf8', '_pos')))
    pool = cf8[cf8.uq_cf_games > min_cf_games].copy()
    pps_cf8 = (pps.groupby(['game_pk', 'game_year', 'fielder_8'], as_index=False)
                  .agg(cf8_pitches=_sz())
                  .merge(pool, on=['game_year', 'fielder_8']))
    cntxt = (pps_cf8[pps_cf8.cf8_pitches > min_cf_pitches]
             .merge(pos[pos.player_name.isin(pool.player_name.unique().tolist())],
                    on=['game_year', 'game_pk', 'batter', 'player_name'],
                    how='inner', suffixes=('_pps', '_pos')))
    return cntxt, pool


def platoon_counterfactual(df, woba_w, window_col, cf_from, cf_to,
                           metrics=('ba', 'obp', 'woba')):
    """PL-1 — NEW-PROVISIONAL. Direct standardisation of a hitter's line to a
    reference platoon mix.

    Answers: how much of the `cf_to` window's line is explained by *facing a
    different mix of LHP/RHP* rather than hitting better?

    Holds the `cf_to` window's within-split rates fixed and re-weights them by
    the `cf_from` window's PA share by `p_throws`. The gap between the actual
    and the re-weighted value is the platoon-mix contribution.

    Returns a tidy frame; `mix_effect` > 0 means the observed line is FLATTERED
    by the platoon mix relative to the reference window.
    """
    r = nresults_unrounded([window_col, 'p_throws'], df.assign(game_year=2026), woba_w)
    a = r[r[window_col] == cf_to].set_index('p_throws')
    b = r[r[window_col] == cf_from].set_index('p_throws')
    idx = sorted(set(a.index) | set(b.index))
    a = a.reindex(idx); b = b.reindex(idx)
    w_actual = (a.plate_apps / a.plate_apps.sum()).fillna(0)
    w_ref = (b.plate_apps / b.plate_apps.sum()).fillna(0)
    rows = []
    for m in metrics:
        vals = a[m]
        actual = float((vals.fillna(0) * w_actual).sum())
        reweighted = float((vals.fillna(0) * w_ref).sum())
        rows.append({'metric': m, 'window': cf_to, 'reference_mix': cf_from,
                     'actual': actual, 'reweighted_to_reference': reweighted,
                     'mix_effect': actual - reweighted})
    out = pd.DataFrame(rows)
    out.attrs['weights_actual'] = w_actual.to_dict()
    out.attrs['weights_reference'] = w_ref.to_dict()
    return out


def pool_percentile(pool, col, value):
    """Share of the benchmark pool strictly below `value`, in percent.
    The subject's own season is retained in the pool (self-inclusive), matching
    the uc-pos-010 / uc-pps-025 population-benchmark precedent."""
    s = pool[col].dropna()
    if len(s) == 0:
        return np.nan
    return float((s < value).mean() * 100)
