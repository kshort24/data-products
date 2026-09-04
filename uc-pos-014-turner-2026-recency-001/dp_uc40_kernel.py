"""
dp_uc40_kernel.py — data loader + governed KPI kernel for uc-pos-014
====================================================================
Use case  : uc-pos-014-turner-2026-recency-001 (Phillies Offense, Trea Turner)
Parent    : uc-pos-006-turner-2026-offense-001 / dp_uc24 (2026-07-21, thru 07-20)
Data plane: C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB

Every function here is either (a) transcribed from `Baseball Functions.ipynb`
- the governed authority - or (b) inherited VERBATIM from `dp_uc37_kernel.py`
(itself the `dp_uc33`/`dp_uc34` `_fix` lineage), or (c) NEW to this UC and
marked NEW-UC40.

Defect handling follows the uc-pos-010 / uc-pos-011 / uc-pos-013 precedent: a
governed function carrying a defect is NOT silently patched. A `_fix` variant
is added beside it, the original is retained upstream, and both are reported
in 05.

INHERITED DEFECT REGISTER (all still open repo-wide)
----------------------------------------------------------------------------
D1  whiff_rate      inner-merges swings->whiffs; a level group with swings but
                    ZERO whiffs vanishes from the output entirely.
D2  hard_hit_rate   same inner-merge shape; zero-hard-hit group vanishes.
D3  fpsr            zero-first-pitch-ball group (perfect 1.000 FPSR) vanishes.
D4  nresults        rounds rates to 3dp on return; ratios inherit the rounding.
D5/O-7  pull_air_rate  reads `loc_x`/`loc_y`, absent from the parquet schema
                    (`hc_x`/`hc_y` exist). Remediated by `pull_air_rate_fix`
                    (uc-pos-013 PA-L1/PA-F1) - still pending DPO ratification.
D6/O-8  hard_hit_rate  denominator is ALL BIP incl. untracked, so an untracked
                    BIP is silently scored "not hard hit". Divergence is
                    quantified in 05 rather than patched.

UC40-SPECIFIC DATA-PLANE NOTES
----------------------------------------------------------------------------
* Two physical sources with ASYMMETRIC SCHEMAS.
  - pre-PHI (2015-2022, WSN then LAD): data/opponents/turner.parquet, 93 cols
  - PHI     (2023-2026)              : data/phillies/phils_{yr}.parquet, 123 cols
  The 30 PHI-only columns include `bat_speed`, `swing_length`, `attack_angle`.
  Bat tracking is therefore structurally 2024+ AND PHI-frame-only. Under the
  uc-pos-009 sensor-boundary standard this is NULL, never zero, never imputed.
* Turner was traded WSN -> LAD midseason 2021/2022; the era label is DERIVED
  per row from the batting side of the half-inning, never carried in.
* `estimated_woba_using_speedangle` is a per-PA xwOBA in this schema
  (uc-pps-028 settled fact): populated on PA-terminating rows only. Averaged
  over BIP it is xwOBAcon and is named as such (O-4).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

# Data plane root. Defaults to the MLB repo on the DPO's machine; override with
# the DP_UC37_DATA environment variable (the build sandbox sets it to a staged copy).
DATA = os.environ.get(
    'DP_UC40_DATA',
    r'C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB')
SUBJECT = 'Turner, Trea'
SUBJECT_MLBAM = 607208              # confirmed by filter, not assumed
AS_OF = '2026-09-02'                # max game_date in the pos frame at build
# WINDOW DEFINITIONS - NEW-UC40. The requester supplied no breakpoint ("recently"),
# so the DPO chose them and must therefore price the choice (uc-pos-011 RC-5):
#   W1 early   : game_date <  2026-07-01   (Mar 26 - Jun 30)
#   W2 july    : 2026-07-01 <= d < 2026-08-01
#   W3 recent  : game_date >= 2026-08-01   (Aug 1 - Sep 2)
# PARENT_ASOF is the cut of the parent product uc-pos-006 / dp_uc24; every
# parent-reproduction check is run on `game_date <= PARENT_ASOF`.
W_EARLY_END = '2026-07-01'
W_JULY_END = '2026-08-01'
PARENT_ASOF = '2026-07-20'
ASB_2026 = '2026-07-16'             # manual carry-in, inherited from uc-pos-006
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


# ══════════════════════════════════════════════════════════════════════════
# NEW-UC40 — two-source subject loader
# ══════════════════════════════════════════════════════════════════════════
def load_subject(mlbam=SUBJECT_MLBAM, phi_years=range(2023, 2027)):
    """Full career pitch log for one batter across the two physical sources.

    Returns a single frame with:
      * `src`        - 'opponents_parquet' | 'phillies_parquet' (provenance)
      * `bat_team`   - batting side of the half-inning (DERIVED, not carried in)
      * `era`        - WSN / LAD / PHI, derived from bat_team
      * `month`, `pitch_group`, `window` (2026 only), `game_date` as datetime

    Regular season + postseason are both returned; `game_type` is preserved so
    every downstream rate can filter to 'R'. Spring ('S') and exhibition ('E')
    are dropped at load, matching `load_frames`.

    Schema asymmetry is NOT reconciled by filling: the 30 PHI-only columns are
    left NaN on pre-PHI rows (uc-pos-009 sensor-boundary standard)."""
    frames = []
    opp = f'{DATA}/data/opponents/turner.parquet'
    if os.path.exists(opp):
        o = pd.read_parquet(opp)
        o = o[o.batter == mlbam].copy()
        o['src'] = 'opponents_parquet'
        frames.append(o)
    for y in phi_years:
        p = f'{DATA}/data/phillies/phils_{y}.parquet'
        if not os.path.exists(p):
            continue
        d = pd.read_parquet(p)
        batting = (((d.home_team == 'PHI') & (d.inning_topbot == 'Bot'))
                   | ((d.away_team == 'PHI') & (d.inning_topbot == 'Top')))
        d = d[batting & (d.batter == mlbam)].copy()
        d['src'] = 'phillies_parquet'
        frames.append(d)
    m = pd.concat(frames, ignore_index=True)
    m = m[~m.game_type.isin(['S', 'E'])].copy()
    m = m.drop_duplicates(subset=['game_pk', 'at_bat_number', 'pitch_number'])
    m['bat_team'] = np.where(m.inning_topbot == 'Top', m.away_team, m.home_team)
    m['era'] = m.bat_team.replace({'WSH': 'WSN'})
    m['game_date'] = pd.to_datetime(m.game_date)
    m['month'] = m.game_date.dt.month
    m['pitch_group'] = m.pitch_type.map(PITCH_GROUP).fillna('other')
    m['season'] = m.game_year
    return m.sort_values(['game_date', 'game_pk', 'at_bat_number', 'pitch_number']
                         ).reset_index(drop=True)


def add_windows(df, early_end=W_EARLY_END, july_end=W_JULY_END):
    """NEW-UC40. Labels 2026 rows W1_early / W2_july / W3_recent."""
    d = df.copy()
    gd = pd.to_datetime(d.game_date)
    d['window'] = np.select(
        [gd < early_end, gd < july_end],
        ['W1_early (Mar 26-Jun 30)', 'W2_july (Jul 1-31)'],
        default='W3_recent (Aug 1-Sep 2)')
    return d


# ══════════════════════════════════════════════════════════════════════════
# NEW-UC40 — measurables: bat tracking (Statcast 2024+, PHI frames only)
# ══════════════════════════════════════════════════════════════════════════
BAT_TRACK_FLOOR = 50        # tracked swings below which central tendency is NULL


def bat_tracking(level, df, floor=BAT_TRACK_FLOOR):
    """BT-1 - NEW-UC40-PROVISIONAL. Swing measurables on TRACKED swings only.

    Sensor-boundary standard (uc-pos-009): `bat_speed` exists only from 2024 and
    only in the Phillies frames. A row without it is NULL, never zero, and the
    absence is reported as coverage rather than silently averaged away.

    `fast_swing_rate` uses the Statcast 75 mph convention, inherited from
    `dp_uc24_turner_2026_review.bat_tracking` (the parent product) VERBATIM."""
    level = _lv(level)
    if 'bat_speed' not in df.columns:
        return pd.DataFrame()
    swings = df[df.description.isin(SWINGS)]
    tot = swings.groupby(level, as_index=False).agg(swings=_sz())
    tr = swings[swings.bat_speed.notna()]
    if tr.empty:
        out = tot.copy()
        for c in ('tracked_swings', 'bat_speed_mu', 'swing_length_mu',
                  'attack_angle_mu', 'fast_swing_rate'):
            out[c] = np.nan
        return out
    agg = tr.groupby(level, as_index=False).agg(
        tracked_swings=_sz(),
        bat_speed_mu=('bat_speed', 'mean'),
        bat_speed_p90=('bat_speed', lambda s: s.quantile(0.90)),
        swing_length_mu=('swing_length', 'mean'),
        attack_angle_mu=('attack_angle', 'mean'))
    fast = tr[tr.bat_speed >= 75].groupby(level, as_index=False).agg(fast_swings=_sz())
    out = tot.merge(agg, on=level, how='left').merge(fast, on=level, how='left')
    out['tracked_swings'] = out.tracked_swings.fillna(0).astype(int)
    out['fast_swings'] = out.fast_swings.fillna(0).astype(int)
    out['tracking_coverage'] = np.where(out.swings > 0,
                                        out.tracked_swings / out.swings, np.nan)
    out['fast_swing_rate'] = np.where(out.tracked_swings > 0,
                                      out.fast_swings / out.tracked_swings, np.nan)
    below = out.tracked_swings < floor
    out.loc[below, ['bat_speed_mu', 'bat_speed_p90', 'swing_length_mu',
                    'attack_angle_mu', 'fast_swing_rate']] = np.nan
    return out


# ══════════════════════════════════════════════════════════════════════════
# NEW-UC40 — RF-2 rolling form, re-specified off the governed PA atom
# ══════════════════════════════════════════════════════════════════════════
def rolling_form(df, woba_w, window_pa=100):
    """RF-2 (uc-pos-006, provisional -> RATIFIED-CANDIDATE here on 2nd reuse).

    Trailing `window_pa` rolling wOBA / OBP / SLG, PA-indexed, single season.

    Re-specified against the current governed denominators rather than the
    parent's: the parent divided both OBP and wOBA by raw PA. Here OBP uses
    AB+BB+HBP+SF and wOBA uses AB+uBB+SF+HBP, matching `nresults_unrounded`.
    The change is DECLARED, not silent - `05_quality_certification.md` carries
    the parent-vs-current reconciliation."""
    pa = pa_rows(df).sort_values(['game_date', 'game_pk', 'at_bat_number']).copy()
    w = woba_w.set_index('Season')
    ev = pa.events.to_numpy()
    yr = pa.game_year.to_numpy()
    n = len(pa)
    wn = np.zeros(n); wd = np.zeros(n)
    h = np.zeros(n); ab = np.zeros(n); tb = np.zeros(n)
    ob = np.zeros(n); obd = np.zeros(n)
    for i in range(n):
        e = ev[i]; y = int(yr[i])
        if y in w.index:
            c = w.loc[y]
            wn[i] = {'walk': c.wBB, 'hit_by_pitch': c.wHBP, 'single': c['w1B'],
                     'double': c['w2B'], 'triple': c['w3B'],
                     'home_run': c.wHR}.get(e, 0.0)
            wd[i] = 0.0 if e in ('intent_walk', 'sac_bunt') else 1.0
        ab[i] = 0.0 if e in NON_AB else 1.0
        h[i] = 1.0 if e in HIT_EV else 0.0
        tb[i] = {'single': 1.0, 'double': 2.0, 'triple': 3.0,
                 'home_run': 4.0}.get(e, 0.0)
        ob[i] = 1.0 if (e in HIT_EV or e in BB_EV or e == 'hit_by_pitch') else 0.0
        obd[i] = ab[i] + (1.0 if (e in BB_EV or e == 'hit_by_pitch'
                                  or e == 'sac_fly') else 0.0)
    r = pd.DataFrame({'pa_idx': np.arange(1, n + 1),
                      'game_date': pa.game_date.to_numpy()})
    S = lambda a: pd.Series(a).rolling(window_pa, min_periods=window_pa).sum()
    wn_c, wd_c = S(wn), S(wd)
    h_c, ab_c, tb_c, ob_c, obd_c = S(h), S(ab), S(tb), S(ob), S(obd)
    r['roll_woba'] = wn_c / wd_c.replace(0, np.nan)
    r['roll_ba'] = h_c / ab_c.replace(0, np.nan)
    r['roll_obp'] = ob_c / obd_c.replace(0, np.nan)
    r['roll_slg'] = tb_c / ab_c.replace(0, np.nan)
    r['roll_ops'] = r.roll_obp + r.roll_slg
    r['window_pa'] = window_pa
    return r.dropna(subset=['roll_woba']).reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════════
# NEW-UC40 — breakpoint sensitivity scan (RC-5 standing requirement)
# ══════════════════════════════════════════════════════════════════════════
def breakpoint_scan(df, woba_w, dates, metrics=('ba', 'obp', 'slg', 'ops', 'woba'),
                    min_pa=1):
    """RC-5 (uc-pos-011, standing). For each candidate cut date, recompute the
    pre/post split and report the delta on each metric.

    Contract: this is a FILTER over a precomputed atom, never a recomputation
    of the atom itself (uc-pps-028 environment rule)."""
    rows = []
    for d in dates:
        lab = df.assign(_w=np.where(pd.to_datetime(df.game_date) < d, 'pre', 'post'))
        r = nresults_unrounded(['_w'], lab, woba_w).set_index('_w')
        if 'pre' not in r.index or 'post' not in r.index:
            continue
        rec = {'breakpoint': d,
               'pre_pa': int(r.loc['pre', 'plate_apps']),
               'post_pa': int(r.loc['post', 'plate_apps'])}
        for m in metrics:
            rec[f'pre_{m}'] = r.loc['pre', m]
            rec[f'post_{m}'] = r.loc['post', m]
            rec[f'd_{m}'] = r.loc['post', m] - r.loc['pre', m]
        rec['below_floor'] = (rec['pre_pa'] < PA_FLOOR) or (rec['post_pa'] < PA_FLOOR)
        rows.append(rec)
    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════
# NEW-UC40 — PARENT REPRODUCTION (uc-pps-028 standing check)
# ══════════════════════════════════════════════════════════════════════════
def legacy_get_stats(level, df):
    """The PARENT product's `get_stats`, transcribed VERBATIM from
    `dp_uc24_turner_2026_review.py` (UC #25, 2026-07-21) for the sole purpose
    of reproducing its published figures.

    ⚠ DEPRECATED - DO NOT USE FOR NEW OUTPUT. Two definitional differences vs
    the current governed `nresults_unrounded`:
      (a) OBP denominator is raw PA, not AB+BB+HBP+SF;
      (b) wOBA denominator is raw PA, not AB+uBB+SF+HBP, and IBB is included.
    Both make OBP/wOBA read LOW relative to the current definition. The
    divergence is quantified, not hidden - see 05."""
    if isinstance(level, str):
        level = [level]
    g = lambda sub, name: sub.groupby(level, as_index=False).agg(**{name: ('description', 'size')})
    pitches = g(df, 'pitches')
    pa = g(df[~df.events.replace(np.nan, 'NA').isin(['NA', 'pickoff_1b'])], 'plate_apps')
    ab = g(df[~df.events.replace(np.nan, 'NA').isin(
        ['NA', 'pickoff_1b', 'walk', 'intent_walk', 'hit_by_pitch',
         'sac_fly', 'sac_bunt'])], 'at_bats')
    hits = g(df[df.events.isin(['home_run', 'single', 'double', 'triple'])], 'hits')
    s1 = g(df[df.events == 'single'], 'singles')
    s2 = g(df[df.events == 'double'], 'doubles')
    s3 = g(df[df.events == 'triple'], 'triples')
    hr = g(df[df.events == 'home_run'], 'hrs')
    bb = g(df[df.events == 'walk'], 'walks')
    ks = g(df[df.events.isin(['strikeout', 'strikeout_double_play'])], 'strikeouts')
    hbp = g(df[df.events == 'hit_by_pitch'], 'hbp')
    out = pitches
    for piece in (pa, ab, hits, s1, s2, s3, hr, bb, ks, hbp):
        out = out.merge(piece, on=level, how='left')
    for wcol, evn in [('wBB', 'walk'), ('wHBP', 'hit_by_pitch'), ('w1B', 'single'),
                      ('w2B', 'double'), ('w3B', 'triple'), ('wHR', 'home_run')]:
        piece = df[df.events == evn].groupby(level, as_index=False).agg(**{wcol: (wcol, 'sum')})
        out = out.merge(piece, on=level, how='left')
    xw = df.groupby(level, as_index=False).agg(
        xwoba=('estimated_woba_using_speedangle', 'mean'),
        xba=('estimated_ba_using_speedangle', 'mean'))
    out = out.merge(xw, on=level, how='left').fillna(0)
    out['ba'] = out.hits / out.at_bats
    out['obp'] = (out.hits + out.walks + out.hbp) / out.plate_apps
    out['slg'] = (out.singles + 2 * out.doubles + 3 * out.triples + 4 * out.hrs) / out.at_bats
    out['ops'] = out.obp + out.slg
    out['woba'] = (out.wBB + out.wHBP + out.w1B + out.w2B + out.w3B + out.wHR) / out.plate_apps
    out['xbh'] = out.doubles + out.triples + out.hrs
    out['iso'] = out.slg - out.ba
    out['krate'] = out.strikeouts / out.plate_apps
    out['bbrate'] = out.walks / out.plate_apps
    return out


def attach_woba_weight_cols(df, woba_w):
    """The parent merged the seasonal wOBA weight columns onto every pitch row
    (wBB..wHR) and summed them. `legacy_get_stats` needs those columns present;
    this reproduces the parent's merge exactly."""
    w = woba_w
    d = df.drop(columns=[c for c in w.columns if c != 'Season' and c in df.columns])
    return d.merge(w, left_on='game_year', right_on='Season',
                   suffixes=('_bad', ''), how='left')


# ══════════════════════════════════════════════════════════════════════════
# NEW-UC40 — D-7 / O-13 REMEDIATION: in_zone_rate counts NULL zone as in-zone
# ══════════════════════════════════════════════════════════════════════════
def in_zone_rate_fix(level, df):
    """D-7 / O-13 (found by this UC's verification harness, 2026-09-03).

    The governed `chase_rate_g` derives `in_zone_rate` by SUBTRACTION —
    `(pitches - ooz) / pitches` — so every row with a NULL `zone` is silently
    counted as an in-zone pitch. The kernel's own `in_zone()` helper excludes
    NULL zone from BOTH populations (uc-pos-013 precedent), so the two
    disagree by exactly the NULL-zone share (4 rows / 0.18% of Turner's 2026).

    This is the same family as D1-D3: a denominator that quietly absorbs rows
    it cannot classify. Per house policy the governed original is NOT patched;
    this `_fix` variant is shipped beside it and both values are reported.

        in_zone_rate_fix = (zone <= 9) / (zone <= 9 or zone > 9)

    `zone_null_rate` ships beside the rate so the exposure is always visible."""
    level = _lv(level)
    d = df[df.zone.notna()]
    iz = d[d.zone < 10].groupby(level, as_index=False).agg(z_in=_sz())
    tot = d.groupby(level, as_index=False).agg(z_classified=_sz())
    allp = df.groupby(level, as_index=False).agg(pitches_all=_sz())
    out = (allp.merge(tot, on=level, how='left').merge(iz, on=level, how='left'))
    for c in ('z_classified', 'z_in'):
        out[c] = out[c].fillna(0).astype(int)
    out['in_zone_rate_fix'] = np.where(out.z_classified > 0,
                                       out.z_in / out.z_classified, np.nan)
    out['zone_null_rate'] = np.where(out.pitches_all > 0,
                                     (out.pitches_all - out.z_classified) / out.pitches_all,
                                     np.nan)
    return out
