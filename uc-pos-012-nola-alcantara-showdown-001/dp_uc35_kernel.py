"""
dp_uc35_kernel.py — data loader + governed KPI kernel for uc-pos-012
====================================================================
Use case  : uc-pos-012-nola-alcantara-showdown-001 (Phillies Offense)
Data plane: C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB

Every function here is either (a) transcribed from `Baseball Functions.ipynb`
— the governed authority — or (b) inherited verbatim from `dp_uc34_kernel.py`
(uc-pos-011), which itself transcribed the same authority, or (c) NEW in this
UC and marked as such.

Defect handling follows the uc-pos-010/011 precedent: a governed function
carrying a defect is NOT silently patched. A `_fix` variant sits beside it,
the original is retained upstream, and both are reported in 05_quality.

INHERITED DEFECT REGISTER (opened uc-pos-010/011, still open repo-wide)
----------------------------------------------------------------------
D1  whiff_rate      inner-merges swings->whiffs; a level group with swings but
                    ZERO whiffs vanishes from the output entirely.
D2  hard_hit_rate   same inner-merge shape: a group with BIP but zero hard
                    hits vanishes. ALSO O-8 (uc-pos-011): denominator counts
                    untracked BIP as "not hard hit". The _fix here corrects
                    the merge shape only; the O-8 denominator question is
                    reported, not silently changed (house barrel convention
                    keeps untracked BIP in the denominator too).
D3  fpsr            drops zero-first-pitch-ball groups (not used this UC).
D4  nresults        rounds rates to 3dp on return; ratios built downstream
                    inherit the rounding. `nresults_unrounded` corrects.
D5/O-7 pull_air_rate cannot execute (loc_x/loc_y absent). Not used here.

This UC adds no new defects to the register; `runs_created` transcribed
verbatim and found clean (see 05_quality for the zero-PA-group note RC-A).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

# Data plane root. Defaults to the MLB repo on the DPO's machine; override with
# the DP_UC35_DATA environment variable (the build sandbox sets it to a staged copy).
DATA = os.environ.get(
    'DP_UC35_DATA',
    r'C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB')

# ── Entity locks (MLBAM ids — never name filters; Nola/"Nolan Hoffman" rule) ──
NOLA = 605400          # Aaron Nola      (confirmed by filter in build)
ALCANTARA = 645261     # Sandy Alcantara (confirmed from alcantara.parquet)
WHEELER = 554430       # Zack Wheeler    (confirmed from wheeler.parquet)
HARPER = 547180        # Bryce Harper    (confirmed by filter in build)
SCHERZER = 453286      # Max Scherzer    (comparison population only)
DEGROM = 594798        # Jacob deGrom    (comparison population only)

AS_OF = '2026-08-17'   # max game_date in the staged frames (asserted in build)
GAME = '2026-08-19'    # Nola vs Alcantara, CBP, 6:05 PM ET

# ── DPO floor ruling (this UC) ──────────────────────────────────────────────
# Human DPO, intake 2026-08-18: "It is about Aaron Nola, use his minimum
# plate_apps in the dataset." The player-season floor for every comparison
# population is therefore the MINIMUM season-level PA that the synthetic
# "Nola vs MIA" batter posts across his career vs Miami — DERIVED in the
# build (dp_uc35_floor_derivation.csv), never hand-keyed. This consciously
# deviates from the house 50-PA batter floor; the deviation is governed in
# 03_governance and flagged on every published surface.
PA_FLOOR_HOUSE = 50    # standing house floor, retained for flagging only

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


def _sz(*_):
    return ('des', 'size')


def _lv(level):
    return [level] if isinstance(level, str) else list(level)


# ══════════════════════════════════════════════════════════════════════════
# Loader — mirrors mlb_data._tag_phillies_role / _split_phils (dp_uc34 verbatim)
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
    pos = pos[~pos.game_type.isin(['S', 'E'])].copy()
    pps = pps[~pps.game_type.isin(['S', 'E'])].copy()
    for d in (pos, pps):
        d['game_date'] = pd.to_datetime(d.game_date)
    return pos, pps


def load_opponent(name):
    """Single-player cache from data/opponents/<name>.parquet, S/E excluded.
    Used for Wheeler's 2017-2019 NYM seasons (pre-PHI coverage of vs-MIA)."""
    d = pd.read_parquet(f'{DATA}/data/opponents/{name}.parquet')
    d = d[~d.game_type.isin(['S', 'E'])].copy()
    d['game_date'] = pd.to_datetime(d.game_date)
    return d


def opponent_of_phi(df):
    """Opposing team for rows in a PHI frame."""
    return np.where(df.home_team == 'PHI', df.away_team, df.home_team)


def woba_weights():
    return pd.read_csv(f'{DATA}/wOBA and FIP Constants.csv')


def pa_rows(df):
    """Terminal plate-appearance rows."""
    return df[~df.events.replace(np.nan, 'NA').isin(NON_PA)]


# ══════════════════════════════════════════════════════════════════════════
# GOVERNED (rebuilt) — results  [dp_uc34_kernel verbatim]
# ══════════════════════════════════════════════════════════════════════════
def nresults_unrounded(level, df, woba_w):
    """D4-corrected `nresults`. Slash line and wOBA from COUNTS, no 3dp round.
    wOBA uses seasonal constants from `wOBA and FIP Constants.csv`; IBB is
    excluded from the numerator and the denominator (the wOBA convention)."""
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
# GOVERNED — approach  [dp_uc34_kernel verbatim]
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
    it must not be read as hitter behaviour (uc-pos-011 RC-4). O-2 (uc-pps-024
    null-zone handling) remains open repo-wide: rows with null `zone` fall out
    of both numerator and denominator here, matching the governed original."""
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


# ══════════════════════════════════════════════════════════════════════════
# GOVERNED — contact  [dp_uc34_kernel verbatim + Baseball Functions barrel_rate]
# ══════════════════════════════════════════════════════════════════════════
def hard_hit_rate_fix(level, df):
    """D2-corrected (merge shape). O-8 denominator convention retained:
    untracked BIP stay in the denominator, matching the governed original and
    the house barrel convention. Reported, not changed."""
    level = _lv(level)
    bip = df[df.type == 'X']
    d = bip.groupby(level, as_index=False).agg(bips=_sz())
    n = bip[bip.launch_speed >= 95].groupby(level, as_index=False).agg(hard_hits=_sz())
    out = d.merge(n, on=level, how='left')
    out['hard_hits'] = out.hard_hits.fillna(0).astype(int)
    out['hard_hit_rate'] = np.where(out.bips > 0, out.hard_hits / out.bips, np.nan)
    return out


def barrel_rate_g(level, df, suffix=''):
    """Transcribed from `Baseball Functions.ipynb` (approved barrel_rate).
    One deviation, disclosed: the governed original rounds barrel_rate to 3dp
    and returns 0 (not NaN) on zero BIP; here the round is dropped (D4 family
    hygiene — rounding happens at publication) and zero-BIP returns NaN so a
    no-contact group cannot masquerade as a measured 0% barrel rate."""
    level = _lv(level)
    bip_pop = df[df.type == 'X']
    bips = bip_pop.groupby(level, as_index=False).agg(bips=_sz())
    barrels = (bip_pop[bip_pop.launch_speed_angle == 6]
               .groupby(level, as_index=False).agg(barrels=_sz()))
    out = bips.merge(barrels, on=level, how='left')
    out['barrels'] = out.barrels.fillna(0).astype(int)
    out['barrel_rate'] = np.where(out.bips > 0, out.barrels / out.bips, np.nan)
    if suffix:
        out = out.rename(columns={'bips': f'bips{suffix}'})
    return out


# ══════════════════════════════════════════════════════════════════════════
# GOVERNED — run creation  [Baseball Functions.ipynb verbatim]
# ══════════════════════════════════════════════════════════════════════════
def runs_created(level, df):
    """Transcribed VERBATIM from `Baseball Functions.ipynb` (approved term
    `runs_created`, glossary + lineage in the notebook). PA-level runs =
    max(post_bat_score) - min(bat_score) within [level, game_pk,
    at_bat_number]; summed to the requested grain."""
    if isinstance(level, str):
        level = [level]
    rdf = df.groupby(level + ['game_pk', 'at_bat_number'], as_index=False
                     ).agg(min_bs=('bat_score', 'min'),
                           max_pbs=('post_bat_score', 'max'))
    rdf['runs_created'] = rdf.max_pbs - rdf.min_bs
    return rdf.groupby(level, as_index=False
                       ).agg(runs_created=('runs_created', 'sum'))


# ══════════════════════════════════════════════════════════════════════════
# NEW — this UC
# ══════════════════════════════════════════════════════════════════════════
def kpi_family(level, df, woba_w):
    """KF-1 — NEW-PROVISIONAL (composition only; every component is governed).
    The use case's full KPI family at one grain: slash line + wOBA + K rate
    (nresults_unrounded), whiff (D1-fix), chase (governed), hard hit (D2-fix),
    barrel (governed), runs_created (governed verbatim) and rc_per_pa =
    runs_created / plate_apps (the use case's own derived KPI, computed from
    unrounded components — D4 avoided by construction)."""
    level = _lv(level)
    z = (nresults_unrounded(level, df, woba_w)
         .merge(whiff_rate_fix(level, df), on=level, how='left',
                suffixes=('', '_wr'))
         .merge(chase_rate_g(level, df)[level + ['chases', 'ooz', 'chase_rate']],
                on=level, how='left')
         .merge(hard_hit_rate_fix(level, df), on=level, how='left')
         .merge(barrel_rate_g(level, df, suffix='_barrel'), on=level, how='left')
         .merge(runs_created(level, df), on=level, how='left'))
    z['runs_created'] = z.runs_created.fillna(0)
    z['rc_per_pa'] = np.where(z.plate_apps > 0,
                              z.runs_created / z.plate_apps, np.nan)
    return z


def synthetic_batter(df, label, opponent=None, pitcher=None):
    """SB-1 — NEW-PROVISIONAL. Builds the 'pitcher as a batter' population:
    all pitches thrown BY `pitcher` in a PHI-pitching (or opponent-cache)
    frame, optionally restricted to games against `opponent`. The rows are the
    OPPOSING team's offensive events, so aggregating them with the batter KPI
    family yields the composite batter that pitcher 'elicited'.
    Adds entity columns so the frame concatenates cleanly with pos-side data."""
    d = df[df.pitcher == pitcher].copy() if pitcher is not None else df.copy()
    if opponent is not None:
        # batting team on a pitching frame: Top of inning -> away team bats
        bat_team = np.where(d.inning_topbot == 'Top', d.away_team, d.home_team)
        d = d[bat_team == opponent].copy()
    d['entity'] = label
    return d
