"""
dp_uc33_kernel.py — data loader + governed KPI kernel for uc-pos-010
====================================================================
Use case  : uc-pos-010-stott-approach-change-001 (Phillies Offense, Bryson Stott)
Data plane: C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB

Every function here is either (a) transcribed VERBATIM from
`Baseball Functions.ipynb` — the governed authority — or (b) a NEW function
introduced by this UC and marked as such.

Where a governed function carries a defect that would corrupt this use case,
the defect is NOT silently patched. A `_fix` variant is added beside it, the
original is retained, and both are reported in 05_quality. See DEFECTS below.

DEFECTS FOUND IN THE GOVERNED KERNEL (reported, not unilaterally fixed)
----------------------------------------------------------------------
D1  whiff_rate   inner-merges swings->whiffs. A level group with swings but
                 ZERO whiffs VANISHES from the output entirely.
D2  hard_hit_rate same inner-merge shape: a group with BIP but zero hard hits
                 VANISHES.
D3  fpsr         groups by level+['type'], then returns only rows where
                 type=='B'. A group with ZERO first-pitch balls (i.e. a perfect
                 1.000 first-pitch-strike rate) VANISHES.
D4  nresults     rounds rates to 3dp on return. Any ratio built by dividing two
                 nresults rates (e.g. bbrate/krate) inherits that rounding.
D5  pull_air_rate computes `total_pulls` and never uses it; the published rate
                 is pull_airs / total_bips (pulled air per BIP), not per pull.
                 Left-merge on air_pulls means a group with pulls but zero
                 pulled AIR yields NaN rather than 0.

D1-D3 share one root cause and one consequence: they drop zero-numerator groups,
which downstream left-merges then render as NaN, which a blanket .fillna(0)
then converts into a measured zero. The DPO's working notebook contained exactly
that `.fillna(0)` — it was compensating for these three defects.
"""
from __future__ import annotations

import glob
import os

import numpy as np
import pandas as pd

DATA = '/mnt/user-data/uploads/MLB'
SUBJECT = 'Stott, Bryson'
SUBJECT_MLBAM = 681082          # pinned, per qab_rate.py


# ══════════════════════════════════════════════════════════════════════════
# Loader — mirrors mlb_data._tag_phillies_role / _split_phils exactly
# ══════════════════════════════════════════════════════════════════════════
def load_pos(years=range(2015, 2027)) -> pd.DataFrame:
    frames = []
    for y in years:
        p = f'{DATA}/data/phillies/phils_{y}.parquet'
        if os.path.exists(p):
            frames.append(pd.read_parquet(p))
    df = pd.concat(frames, ignore_index=True)
    batting = (((df.home_team == 'PHI') & (df.inning_topbot == 'Bot'))
               | ((df.away_team == 'PHI') & (df.inning_topbot == 'Top')))
    pos = df[batting].copy()
    # August 2026.ipynb line 1: regular + postseason, exclude Spring / Exhibition
    pos = pos[~pos.game_type.isin(['S', 'E'])].copy()
    pos['game_date'] = pd.to_datetime(pos.game_date)
    pos['month'] = pos.game_date.dt.month          # ← B-3 resolution, see 03_governance
    return pos


# ══════════════════════════════════════════════════════════════════════════
# GOVERNED — verbatim from Baseball Functions.ipynb
# ══════════════════════════════════════════════════════════════════════════
SWINGS = ['foul', 'foul_bunt', 'foul_tip', 'hit_into_play', 'missed_bunt',
          'swinging_pitchout', 'swinging_strike', 'swinging_strike_blocked']
WHIFFS = ['foul_tip', 'missed_bunt', 'swinging_pitchout', 'swinging_strike',
          'swinging_strike_blocked']

# PA definition — dp_uc24 L219 / dp_uc22 L80
NON_PA = ['NA', 'pickoff_1b', 'pickoff_2b', 'pickoff_3b',
          'caught_stealing_2b', 'caught_stealing_3b', 'caught_stealing_home',
          'stolen_base_2b', 'stolen_base_3b', 'stolen_base_home',
          'pickoff_caught_stealing_2b', 'pickoff_caught_stealing_3b',
          'pickoff_caught_stealing_home', 'wild_pitch', 'passed_ball',
          'other_advance', 'runner_double_play', 'defensive_indiff',
          'balk', 'game_advisory', 'ejection', 'stolen_base_home']
K_EV = {'strikeout', 'strikeout_double_play'}
BB_EV = {'walk', 'intent_walk'}
HIT_EV = {'single', 'double', 'triple', 'home_run'}
NON_AB = {'walk', 'intent_walk', 'hit_by_pitch', 'sac_fly', 'sac_bunt',
          'sac_fly_double_play', 'sac_bunt_double_play', 'catcher_interf'}


def pa_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Terminal plate-appearance rows."""
    return df[~df.events.replace(np.nan, 'NA').isin(NON_PA)]


def _sz(x):
    return ('des', 'size')


def whiff_rate_fix(level, df):
    """D1-corrected: outer semantics so zero-whiff groups survive."""
    u = df[df.description.isin(SWINGS)].groupby(level, as_index=False).agg(swings=_sz(0))
    v = df[df.description.isin(WHIFFS)].groupby(level, as_index=False).agg(whiffs=_sz(0))
    w = u.merge(v, on=level, how='left')
    w['whiffs'] = w.whiffs.fillna(0).astype(int)     # a count, genuinely zero
    w['whiff_rate'] = np.where(w.swings > 0, w.whiffs / w.swings, np.nan)
    return w


def chase_rate_g(level, df):
    """Verbatim governed logic (no defect found)."""
    chase = df[(df.zone > 9) & (df.description.isin(SWINGS))]
    i = chase.groupby(level, as_index=False).agg(chases=_sz(0))
    j = df[df.zone > 9].groupby(level, as_index=False).agg(ooz=_sz(0))
    cr = (i.merge(j, on=level, how='right')
           .merge(df.groupby(level, as_index=False).agg(pitches=_sz(0)),
                  on=level, how='right'))
    cr['chases'] = cr.chases.fillna(0)
    cr['chase_rate'] = np.where(cr.ooz > 0, cr.chases / cr.ooz, np.nan)
    cr['in_zone_rate'] = (cr.pitches - cr.ooz) / cr.pitches
    return cr


def swing_rate(level, df):
    """AP-2 — NEW. Inherits the governed SWINGS list; declares no classifier.

    Reconciles with whiff_rate by construction: `swings` here is the same
    population whiff_rate divides by.
    """
    s = df[df.description.isin(SWINGS)].groupby(level, as_index=False).agg(swings=_sz(0))
    p = df.groupby(level, as_index=False).agg(pitches=_sz(0))
    out = p.merge(s, on=level, how='left')
    out['swings'] = out.swings.fillna(0).astype(int)
    out['swing_rate'] = np.where(out.pitches > 0, out.swings / out.pitches, np.nan)
    return out


def fpsr_fix(level, df):
    """D3-corrected first-pitch strike rate. Same formula as the governed
    version — (pitches - balls) / pitches over pitch_number == 1 — but built so
    a group with zero first-pitch balls survives at 1.000 instead of vanishing.
    """
    fp = df[df.pitch_number == 1]
    p = fp.groupby(level, as_index=False).agg(first_pitches=_sz(0))
    b = (fp[fp.type == 'B'].groupby(level, as_index=False).agg(first_pitch_balls=_sz(0)))
    out = p.merge(b, on=level, how='left')
    out['first_pitch_balls'] = out.first_pitch_balls.fillna(0).astype(int)
    out['fpsr'] = (out.first_pitches - out.first_pitch_balls) / out.first_pitches
    return out


def hard_hit_rate_fix(level, df):
    """D2-corrected."""
    bip = df[df.type == 'X']
    d = bip.groupby(level, as_index=False).agg(bips=_sz(0))
    n = bip[bip.launch_speed >= 95].groupby(level, as_index=False).agg(hard_hits=_sz(0))
    out = d.merge(n, on=level, how='left')
    out['hard_hits'] = out.hard_hits.fillna(0).astype(int)
    out['hard_hit_rate'] = np.where(out.bips > 0, out.hard_hits / out.bips, np.nan)
    return out


def barrel_rate_g(level, df):
    """Verbatim governed logic — already handles the zero-numerator case."""
    bip = df[df.type == 'X']
    d = bip.groupby(level, as_index=False).agg(bips=_sz(0))
    n = bip[bip.launch_speed_angle == 6].groupby(level, as_index=False).agg(barrels=_sz(0))
    out = d.merge(n, on=level, how='left')
    out['barrels'] = out.barrels.fillna(0).astype(int)
    out['barrel_rate'] = np.where(out.bips > 0, out.barrels / out.bips, np.nan)
    return out


def ev90(level, df, floor=40):
    """Governed formula. Adds the UC's 40-BIP floor as an explicit NULL, rather
    than publishing a 90th percentile over a handful of batted balls."""
    bip = df[(df.type == 'X') & df.launch_speed.notna()]
    out = bip.groupby(level, as_index=False).agg(
        ev90=('launch_speed', lambda x: x.quantile(0.90)), ev_bips=('launch_speed', 'size'))
    out.loc[out.ev_bips < floor, 'ev90'] = np.nan
    return out


def nresults_unrounded(level, df, woba_w: pd.DataFrame):
    """Rebuild of the governed nresults WITHOUT the 3dp rounding (D4).

    Slash line and wOBA computed from counts. wOBA uses the seasonal constants
    from `wOBA and FIP Constants.csv`, matching dp_uc24's running_line weight map
    (which keys 'walk' but NOT 'intent_walk' — the wOBA convention).
    """
    pa = pa_rows(df).copy()
    g = lambda d, n: d.groupby(level, as_index=False).agg(**{n: _sz(0)})

    out = g(pa, 'plate_apps')
    out = out.merge(df.groupby(level, as_index=False).agg(pitches=_sz(0)), on=level, how='left')
    for name, mask in [
        ('at_bats',    ~pa.events.isin(NON_AB)),
        ('hits',        pa.events.isin(HIT_EV)),
        ('walks',       pa.events.isin(BB_EV)),
        ('unint_walks', pa.events == 'walk'),
        ('hbp',         pa.events == 'hit_by_pitch'),
        ('strikeouts',  pa.events.isin(K_EV)),
        ('sf',          pa.events == 'sac_fly'),
        ('singles',     pa.events == 'single'),
        ('doubles',     pa.events == 'double'),
        ('triples',     pa.events == 'triple'),
        ('hrs',         pa.events == 'home_run'),
        ('bip',         pa.type == 'X'),
    ]:
        out = out.merge(g(pa[mask], name), on=level, how='left')
        out[name] = out[name].fillna(0).astype(int)

    tb = out.singles + 2 * out.doubles + 3 * out.triples + 4 * out.hrs
    out['ba']  = np.where(out.at_bats > 0, out.hits / out.at_bats, np.nan)
    out['obp'] = np.where((out.at_bats + out.walks + out.hbp + out.sf) > 0,
                          (out.hits + out.walks + out.hbp)
                          / (out.at_bats + out.walks + out.hbp + out.sf), np.nan)
    out['slg'] = np.where(out.at_bats > 0, tb / out.at_bats, np.nan)
    out['ops'] = out.obp + out.slg
    out['krate']  = out.strikeouts / out.plate_apps
    out['bbrate'] = out.walks / out.plate_apps

    # wOBA — seasonal weights, IBB excluded per convention
    yr_col = 'game_year' if 'game_year' in level else None
    w = woba_w.set_index('Season')
    def _woba(r):
        y = int(r.game_year) if yr_col else 2026
        if y not in w.index:
            return np.nan
        c = w.loc[y]
        num = (c.wBB * r.unint_walks + c.wHBP * r.hbp + c['w1B'] * r.singles
               + c['w2B'] * r.doubles + c['w3B'] * r.triples + c.wHR * r.hrs)
        den = r.at_bats + r.unint_walks + r.sf + r.hbp
        return num / den if den > 0 else np.nan
    out['woba'] = out.apply(_woba, axis=1) if yr_col else np.nan
    return out


# ══════════════════════════════════════════════════════════════════════════
# NEW — AP-9 / AP-10, per AMENDMENT-3
# ══════════════════════════════════════════════════════════════════════════
def discipline_ratio(level, df, unintentional_only=True):
    """AP-9. BB/K from counts. K==0 -> NaN + k_free flag + raw counts."""
    pa = pa_rows(df)
    bb = {'walk'} if unintentional_only else BB_EV
    out = pa.groupby(level, as_index=False).agg(plate_apps=_sz(0))
    for n, s in (('walks', bb), ('strikeouts', K_EV)):
        sub = pa[pa.events.isin(s)].groupby(level, as_index=False).agg(**{n: _sz(0)})
        out = out.merge(sub, on=level, how='left')
        out[n] = out[n].fillna(0).astype(int)
    out['bbrate'] = out.walks / out.plate_apps
    out['krate'] = out.strikeouts / out.plate_apps
    out['k_free'] = out.strikeouts == 0
    out['bb_per_k'] = np.where(out.k_free, np.nan,
                               out.walks / out.strikeouts.replace(0, np.nan))
    out['bb_minus_k'] = out.bbrate - out.krate
    return out


def walks_between_ks(level, df, unintentional_only=True):
    """AP-10. Longest run of walks between consecutive strikeouts."""
    pa = pa_rows(df).sort_values(['game_date', 'game_pk', 'at_bat_number'])
    bb = {'walk'} if unintentional_only else BB_EV
    rows = []
    for keys, grp in pa.groupby(list(level), sort=False):
        is_bb = grp.events.isin(bb).to_numpy()
        is_k = grp.events.isin(K_EV).to_numpy()
        dates = grp.game_date.to_numpy()
        pks = grp.game_pk.to_numpy()
        best = cur = 0
        bs = be = cs = None
        bg = set(); cg = set()
        for i in range(len(grp)):
            if is_k[i]:
                cur, cs, cg = 0, None, set()
            elif is_bb[i]:
                if cur == 0:
                    cs = dates[i]
                cur += 1; cg.add(pks[i])
                if cur > best:
                    best, bs, be, bg = cur, cs, dates[i], set(cg)
        rows.append(dict(zip(list(level), keys if isinstance(keys, tuple) else (keys,)))
                    | {'max_bb_run': best, 'current_bb_run': cur,
                       'run_start_date': bs, 'run_end_date': be,
                       'run_games': len(bg)})
    return pd.DataFrame(rows)


def running_line_pa(df, woba_w):
    """AP-6 — RF-1 (`running_line`) re-indexed from game_date to CUMULATIVE PA.

    One row per (game_year, cumulative_pa). wOBA-to-date using that season's
    weights. Regular season + postseason, per the pos filter.
    """
    pa = pa_rows(df).sort_values(['game_year', 'game_date', 'game_pk', 'at_bat_number']).copy()
    w = woba_w.set_index('Season')
    num = np.zeros(len(pa)); den = np.zeros(len(pa))
    ev = pa.events.to_numpy(); yr = pa.game_year.to_numpy()
    for i in range(len(pa)):
        y = int(yr[i])
        if y not in w.index:
            continue
        c = w.loc[y]; e = ev[i]
        num[i] = {'walk': c.wBB, 'hit_by_pitch': c.wHBP, 'single': c['w1B'],
                  'double': c['w2B'], 'triple': c['w3B'], 'home_run': c.wHR}.get(e, 0.0)
        den[i] = 0.0 if e in ('intent_walk', 'sac_bunt') else 1.0
    pa['_n'], pa['_d'] = num, den
    pa['cum_pa'] = pa.groupby('game_year').cumcount() + 1
    pa['cum_woba'] = (pa.groupby('game_year')._n.cumsum()
                      / pa.groupby('game_year')._d.cumsum().replace(0, np.nan))
    return pa[['game_year', 'game_date', 'cum_pa', 'cum_woba']].reset_index(drop=True)
