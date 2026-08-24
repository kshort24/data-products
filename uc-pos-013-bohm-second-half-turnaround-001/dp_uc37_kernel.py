"""
dp_uc37_kernel.py — data loader + governed KPI kernel for uc-pos-013
====================================================================
Use case  : uc-pos-013-bohm-second-half-turnaround-001 (Phillies Offense, Alec Bohm)
Data plane: C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB

Every function here is either (a) transcribed from `Baseball Functions.ipynb`
— the governed authority — or (b) inherited from `dp_uc33_kernel.py` /
`dp_uc34_kernel.py` (the `_fix` lineage), or (c) NEW to this UC and marked
as such.

Defect handling follows the uc-pos-010 / uc-pos-011 precedent: a governed
function carrying a defect is NOT silently patched. A `_fix` variant is added
beside it, the original is retained upstream, and both are reported in 05.

INHERITED DEFECT REGISTER (all still open repo-wide)
----------------------------------------------------------------------------
D1  whiff_rate      inner-merges swings->whiffs; a level group with swings but
                    ZERO whiffs vanishes from the output entirely.
D2  hard_hit_rate   same inner-merge shape; zero-hard-hit group vanishes.
D3  fpsr            zero-first-pitch-ball group (perfect 1.000 FPSR) vanishes.
D4  nresults        rounds rates to 3dp on return; ratios inherit the rounding.
D5/O-7  pull_air_rate  reads `loc_x`/`loc_y`, which do NOT exist in the parquet
                    schema (`hc_x`/`hc_y` do). Re-checked against the current
                    `Baseball Functions.ipynb` (cell 24) at intake for THIS
                    build: still unexecutable as written. This UC ships
                    `pull_air_rate_fix`, which derives the loc coordinates
                    from `hc_x`/`hc_y` per the house `cbp-spray_AI.md`
                    convention and then applies the governed classification
                    VERBATIM. The classification is scale-invariant (the
                    ±4.7-slope boundaries pass through the origin), so only
                    centering + y-flip matter; both are asserted empirically
                    at load (see `derive_loc`).
D6/O-8  hard_hit_rate  denominator is ALL BIP incl. untracked, so an untracked
                    BIP is silently scored "not hard hit". 2026 Bohm has ONE
                    untracked BIP — divergence quantified in 05.

D1-D3 share one root cause: dropped zero-numerator groups -> NaN after
left-merge -> a blanket `.fillna(0)` would turn that into a measured zero.
No blanket fillna is used in this build.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

# Data plane root. Defaults to the MLB repo on the DPO's machine; override with
# the DP_UC37_DATA environment variable (the build sandbox sets it to a staged copy).
DATA = os.environ.get(
    'DP_UC37_DATA',
    r'C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB')
SUBJECT = 'Bohm, Alec'
SUBJECT_MLBAM = 664761              # confirmed by filter, not assumed
AS_OF = '2026-08-22'                # max game_date in the pos frame at build
# The DPO's submitted operator IS the governed breakpoint:
#   post = vs[vs.game_date > '2026-07-15']   (first game back: 2026-07-16)
#   pre  = vs[vs.game_date < '2026-07-16']   (last game before break: 2026-07-12)
# The two are exact complements — no Phillies game falls on 7/13–7/15.
BREAK = '2026-07-15'                # post-break = game_date > BREAK
PA_FLOOR = 50                       # standing batter rate-stat floor
BIP_FLOOR = 50                      # metric-specific floor for LA / EV / bb-type stats

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

# cbp-spray_AI.md §Data Quality rule 1: loc_* are centered feet-from-plate;
# from raw Statcast hc_*, origin is (125.42, 198.27) and y must be flipped.
HC_ORIGIN_X, HC_ORIGIN_Y = 125.42, 198.27
HC_SCALE = 2.495671   # ft per hc unit — classification is invariant to this


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


def risp_rows(df):
    """RISP-state pitch rows, per the DPO's submitted operator:
    `(df.on_2b.isna() == False) | (df.on_3b.isna() == False)`.

    Semantics note (kpi-calculator ruling, 02_engineering_design §RISP):
    because `nresults`/`pa_rows` keeps only terminal-event rows, a PA counts
    as a RISP PA iff runners were in scoring position ON THE TERMINAL PITCH.
    A PA in which a runner reached 2B mid-PA and was erased before the final
    pitch is not a RISP PA under this definition; this matches the DPO's
    notebook method exactly and is the definition verified in dp_uc37_verification.
    """
    return df[df.on_2b.notna() | df.on_3b.notna()]


def in_zone(df):
    """In-zone pitch rows per the DPO operator `df.zone < 10` (zone 1–9).
    NULL zone rows (5 in Bohm 2026) are excluded from BOTH zone populations."""
    return df[df.zone < 10]


# ══════════════════════════════════════════════════════════════════════════
# GOVERNED (rebuilt) — results
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
# GOVERNED — run creation (transcribed VERBATIM from Baseball Functions.ipynb
# cell 14; no defect found — grain-safe: PA grain first, then level)
# ══════════════════════════════════════════════════════════════════════════
def runs_created(level, df):
    """Governed `runs_created`: for each PA, (max post_bat_score − min bat_score),
    summed to `level`. This is 'runs that scored during the subject's plate
    appearances' — it credits RBI *and* runs that scored by other means
    (wild pitch, steal of home, error) while he was at the plate.

    ⚠ Glossary note: this is the DPO-notebook `runs_created`, NOT SC-1 wRC
    (uc-pos-004) and NOT the Bill James RC formula. The three must never be
    conflated; see 03_governance."""
    level = _lv(level)
    rdf = df.groupby(level + ['game_pk', 'at_bat_number'], as_index=False
                     ).agg(min_bs=('bat_score', 'min'),
                           max_pbs=('post_bat_score', 'max'))
    rdf['runs_created'] = rdf.max_pbs - rdf.min_bs
    return rdf.groupby(level, as_index=False
                       ).agg(runs_created=('runs_created', 'sum'))


def rc_rate(level, df):
    """RC-R1 — NEW-PROVISIONAL. `runs_created` divided by plate appearances at
    the same level. Required because the pre/post windows differ 377 vs 135 PA
    and the raw governed total is volume-confounded across them."""
    level = _lv(level)
    rc = runs_created(level, df)
    pa = pa_rows(df).groupby(level, as_index=False).agg(plate_apps=_sz())
    out = pa.merge(rc, on=level, how='left')
    out['runs_created'] = out.runs_created.fillna(0).astype(int)
    out['rc_per_pa'] = np.where(out.plate_apps > 0,
                                out.runs_created / out.plate_apps, np.nan)
    return out


# ══════════════════════════════════════════════════════════════════════════
# GOVERNED — indicators (transcribed VERBATIM from cell 17, minus the round)
# ══════════════════════════════════════════════════════════════════════════
def inds_unrounded(level, df):
    """Governed `inds` means, without the notebook's `.round(1)` (D4-adjacent).
    ⚠ O-3 trap (uc-pps-024): when run on ALL pitch rows — as the DPO snippet
    does — `ev_mu`/`la_mu` average every non-null `launch_speed`, which
    INCLUDES tracked foul balls, not just balls in play. The house tracked-BIP
    standard lives in `battedball_profile`. Both are shipped; the report's
    headline uses tracked BIP and the reconciliation is quantified in 05."""
    level = _lv(level)
    return df.groupby(level, as_index=False).agg(
        counter=_sz(), unique_players=('batter', 'nunique'),
        pitch_speed_mu=('release_speed', 'mean'),
        ev_mu=('launch_speed', 'mean'), ev_std=('launch_speed', 'std'),
        la_mu=('launch_angle', 'mean'), dist_mu=('hit_distance_sc', 'mean'))


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
    see RC-4; it must not be read as hitter behaviour."""
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


def zone_swing_whiff(level, df):
    """In-zone discipline panel, per the DPO operators:
    `swing_rate(level, df[df.zone < 10])` and `whiff_rate(level, df[df.zone < 10])`.
    Returns z_pitches / z_swings / swing_rate_in_zone / whiff_rate_in_zone."""
    level = _lv(level)
    z = in_zone(df)
    s = swing_rate(level, z).rename(columns={
        'pitches': 'z_pitches', 'swings': 'z_swings',
        'swing_rate': 'swing_rate_in_zone'})
    w = whiff_rate_fix(level, z).rename(columns={
        'swings': 'z_swings_w', 'whiffs': 'z_whiffs',
        'whiff_rate': 'whiff_rate_in_zone'})
    out = s.merge(w, on=level, how='left')
    return out.drop(columns=['z_swings_w'])


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
    CONSUMED here, not redefined. This is a PITCHER metric on a hitter panel —
    see RC-4."""
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
    """D2-corrected merge. ⚠ D6/O-8 retained deliberately: the governed
    denominator is ALL BIP including untracked; divergence reported in 05."""
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
    """CR-1 (uc-pos-011, provisional). Batted-ball type shares plus launch-angle
    / exit-velocity central tendency on TRACKED balls in play.

    Sensor-boundary NULL standard (uc-pos-009): an untracked BIP is not a
    zero-launch-angle BIP. Shares are computed over ALL BIP (bb_type is
    classifier-derived and complete); launch statistics are computed over
    tracked BIP only and are NULL below `bip_floor`."""
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
    """CR-2 (uc-pos-011, provisional). Mean expected outcome on contact.
    ⚠ Averaged over BIP → xwOBAcon, NOT xwOBA (O-4 naming convention)."""
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
# O-7 REMEDIATION — pull-air rate that executes against the governed schema
# ══════════════════════════════════════════════════════════════════════════
def derive_loc(df):
    """PA-L1 — NEW-PROVISIONAL. Derives `loc_x`/`loc_y` (centered
    feet-from-plate) from raw Statcast `hc_x`/`hc_y`, per cbp-spray_AI.md
    §Data Quality rule 1: origin (125.42, 198.27), y flipped, uniform scale.

    Coordinate-convention assertion (uc-pps-025 rule — assert, don't assume):
    +loc_x must be the RF side (spray angle = atan2(loc_x, loc_y); 0° = CF,
    negative = LF). Verified empirically in the build: RHB pulled ground
    balls (Bohm's) must have median loc_x < 0. The build refuses to publish
    pull-side output if that assertion fails."""
    out = df.copy()
    out['loc_x'] = HC_SCALE * (out.hc_x.astype('float64') - HC_ORIGIN_X)
    out['loc_y'] = HC_SCALE * (HC_ORIGIN_Y - out.hc_y.astype('float64'))
    return out


def hit_direction(bip):
    """The governed stand-aware classification, VERBATIM from
    `Baseball Functions.ipynb` cell 24 (±4.7-slope boundaries). Requires
    loc_x/loc_y (call `derive_loc` first). Scale-invariant."""
    return np.where(
        bip.stand == 'R',
        np.select(
            [bip.loc_y <= -4.7 * bip.loc_x,
             (bip.loc_y > -4.7 * bip.loc_x) & (bip.loc_y > 4.7 * bip.loc_x),
             bip.loc_y <= 4.7 * bip.loc_x],
            ['Pull', 'Straightaway', 'Oppo'], default='not grouped'),
        np.select(
            [bip.loc_y <= 4.7 * bip.loc_x,
             (bip.loc_y > -4.7 * bip.loc_x) & (bip.loc_y > 4.7 * bip.loc_x),
             bip.loc_y <= -4.7 * bip.loc_x],
            ['Pull', 'Straightaway', 'Oppo'], default='not grouped'))


def pull_air_rate_fix(level, df):
    """PA-F1 — the O-7 remediation. Formula VERBATIM from the governed
    `pull_air_rate` (cell 24) after the loc derivation:

        pull_air_rate = (pulled BIP with bb_type != 'ground_ball') / ALL BIP

    Notes preserved from the governed function: 'air' = fly ball + line drive
    + popup (anything not a ground ball); the denominator is TOTAL BIP, not
    total pulls (the governed function computes `total_pulls` and never uses
    it — that dead variable is part of open item O-7's history).
    An hc-untracked BIP cannot be classified; `hc_tracked` is shipped beside
    the rate (D6-shaped exposure; 0 rows for Bohm 2026)."""
    level = _lv(level)
    bip = derive_loc(df[df.type == 'X'])
    bip = bip.assign(hit_direction=hit_direction(bip))
    tot = bip.groupby(level, as_index=False).agg(total_bips=_sz())
    trk = bip[bip.hc_x.notna() & bip.hc_y.notna()].groupby(
        level, as_index=False).agg(hc_tracked=_sz())
    pa_air = bip[(bip.hit_direction == 'Pull') & (bip.bb_type != 'ground_ball')
                 ].groupby(level, as_index=False).agg(pull_airs=_sz())
    pulls = bip[bip.hit_direction == 'Pull'].groupby(
        level, as_index=False).agg(total_pulls=_sz())
    out = (tot.merge(trk, on=level, how='left')
              .merge(pulls, on=level, how='left')
              .merge(pa_air, on=level, how='left'))
    for c in ('hc_tracked', 'total_pulls', 'pull_airs'):
        out[c] = out[c].fillna(0).astype(int)
    out['pull_air_rate'] = np.where(out.total_bips > 0,
                                    out.pull_airs / out.total_bips, np.nan)
    out['pull_rate'] = np.where(out.total_bips > 0,
                                out.total_pulls / out.total_bips, np.nan)
    return out


# ══════════════════════════════════════════════════════════════════════════
# INHERITED — trajectory, platoon, benchmarks
# ══════════════════════════════════════════════════════════════════════════
def running_line_pa(df, woba_w, group='game_year'):
    """AP-6 (uc-pos-010) as extended by uc-pos-011 — cumulative wOBA, BA, OBP
    indexed by cumulative PA within `group`. THIS UC extends it additively to
    **cum_slg** (total bases / AB), because SLG is the requester's first
    top-line KPI; the extension is non-breaking, mirroring the uc-pos-011
    BA/OBP precedent. Ordered by game_date -> game_pk -> at_bat_number.
    Regular + postseason."""
    pa = pa_rows(df).sort_values([group, 'game_date', 'game_pk',
                                  'at_bat_number']).copy()
    w = woba_w.set_index('Season')
    n = len(pa)
    num = np.zeros(n); den = np.zeros(n)
    h = np.zeros(n); ab = np.zeros(n); ob = np.zeros(n); obd = np.zeros(n)
    tb = np.zeros(n)
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
        tb[i] = {'single': 1.0, 'double': 2.0, 'triple': 3.0,
                 'home_run': 4.0}.get(e, 0.0)
        ob[i] = 1.0 if (e in HIT_EV or e in BB_EV or e == 'hit_by_pitch') else 0.0
        obd[i] = ab[i] + (1.0 if (e in BB_EV or e == 'hit_by_pitch'
                                  or e == 'sac_fly') else 0.0)
    pa['_n'], pa['_d'], pa['_h'], pa['_ab'], pa['_ob'], pa['_obd'], pa['_tb'] = \
        num, den, h, ab, ob, obd, tb
    g = pa.groupby(group)
    pa['cum_pa'] = g.cumcount() + 1
    pa['cum_woba'] = g._n.cumsum() / g._d.cumsum().replace(0, np.nan)
    pa['cum_ba'] = g._h.cumsum() / g._ab.cumsum().replace(0, np.nan)
    pa['cum_obp'] = g._ob.cumsum() / g._obd.cumsum().replace(0, np.nan)
    pa['cum_slg'] = g._tb.cumsum() / g._ab.cumsum().replace(0, np.nan)
    cols = [group, 'game_year', 'game_date', 'cum_pa',
            'cum_ba', 'cum_obp', 'cum_slg', 'cum_woba']
    cols = list(dict.fromkeys(cols))
    return pa[cols].reset_index(drop=True)


def platoon_counterfactual(df, woba_w, window_col, cf_from, cf_to,
                           metrics=('ba', 'obp', 'slg', 'woba')):
    """PL-1 (uc-pos-011, provisional). Direct standardisation of a hitter's
    line to a reference platoon mix. `mix_effect` > 0 means the observed line
    is FLATTERED by the platoon mix relative to the reference window."""
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
    Self-inclusive, matching the uc-pos-010 / uc-pps-025 precedent."""
    s = pool[col].dropna()
    if len(s) == 0:
        return np.nan
    return float((s < value).mean() * 100)
