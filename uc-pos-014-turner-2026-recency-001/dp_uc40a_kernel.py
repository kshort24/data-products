"""
dp_uc40a_kernel.py — BAT-PATH extension kernel for uc-pos-014 v1.1.0
=====================================================================
Addendum build `dp_uc40a`. Extends `dp_uc40_kernel.py`; does not replace it.
Everything in `dp_uc40_kernel` is imported and re-exported unchanged.

WHY THIS FILE EXISTS
--------------------
The v1.0.0 product found that Turner's Aug-Sep popup rate (15.2% of BIP vs a
5.0% Phillies norm, z = 4.12) was the only signal clearing the noise bar, but
it could only describe the OUTCOME. Statcast's bat-path columns describe the
SWING that produced it. None of them had a governed definition in this data
plane before this build (Rule-1 grep: one exploratory histogram in
`November 2025.ipynb`, no spec, no lineage).

GOVERNANCE POSTURE (matches `Baseball Functions.ipynb` discipline)
-----------------------------------------------------------------
1. Every column gets a SEMANTIC definition with a cited source, and a
   TECHNICAL definition (units, grain, population, null policy).
2. Every sign convention is ASSERTED against the data, never assumed
   (the uc-pps-025 rule). The assertions live in `assert_conventions()` and
   the build REFUSES TO PUBLISH if any of them fails.
3. Sensor boundaries are NULL, never zero, never imputed (uc-pos-009).
4. A defect in a source column is reported, not silently corrected.

THE SIX COLUMNS
---------------
| column                                     | ships from | semantic                              |
|--------------------------------------------|-----------|----------------------------------------|
| `bat_speed`                                | 2024      | sweet-spot speed at contact (mph)      |
| `swing_length`                             | 2024      | length of the barrel's path (ft)       |
| `attack_angle`                             | 2025      | VERTICAL direction of the sweet spot at contact (deg) |
| `attack_direction`                         | 2025      | HORIZONTAL direction of the sweet spot at contact (deg) |
| `swing_path_tilt`                          | 2025      | vertical tilt of the swing PLANE on the way to contact (deg) |
| `intercept_ball_minus_batter_pos_x_inches` | 2025      | contact point, LATERAL distance from the batter's centre of mass (in) |
| `intercept_ball_minus_batter_pos_y_inches` | 2025      | contact point, DEPTH in front of the batter's centre of mass (in) |
| `hyper_speed`                              | 2025      | **NOT a bat-path column** — see O-17    |

Definitions are sourced from the MLB Statcast glossary (attack-angle,
attack-direction, swing-path-tilt, intercept-point). Sign conventions and axis
assignments are NOT taken from the glossary — they are proven here, because
this build found that one of them does not hold in this data plane (O-15).

OPEN ITEMS RAISED BY THIS BUILD
-------------------------------
O-15  `attack_direction` is **PULL-NEGATIVE / OPPO-POSITIVE** in this data
      plane. The published MLB glossary states the opposite ("Pull = positive").
      Four independent anchors agree with the data and against the glossary —
      see `assert_conventions()`. Any consumer reading the glossary convention
      onto this column will invert every pull/oppo conclusion it draws.
O-16  `swing_path_tilt` fell **team-wide** by ~1.1-1.2 deg from 2025 to 2026
      across every Phillies hitter with >=200 tracked swings in both years.
      Real league trend or a calibration change is UNKNOWN. Therefore no
      year-over-year tilt comparison may be published without netting it
      against a peer baseline (`peer_delta()` exists for exactly this).
O-18  Bat-path columns are **degenerate on bunts and checked swings**. The
      governed `SWINGS` list contains `foul_bunt` and `missed_bunt`, which are
      not swing paths; those rows carry absurd values (bat speed 8-14 mph,
      attack angle -53 deg) and are the only rows where `swing_path_tilt`
      goes NULL while `attack_angle` is present. `intercept_*` has its own,
      slightly wider gate (25 of 21,700 swings, 0.12%). Bat-path population is
      therefore defined as swings EXCLUDING bunts; rows with
      `bat_speed < 25` mph are flagged degenerate, excluded from central
      tendencies, and counted on every panel.
O-17  `hyper_speed` is a **deterministic transform of `launch_speed`**:
      `hyper_speed == max(launch_speed, 88)` on 100.0% of 6,720 tracked 2026
      Phillies swings. It carries no information beyond exit velocity and must
      never be reported as an independent measure of contact quality.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from dp_uc40_kernel import (  # noqa: F401  — re-exported unchanged
    DATA, SUBJECT, SUBJECT_MLBAM, AS_OF, PA_FLOOR, BIP_FLOOR,
    SWINGS, WHIFFS, NON_PA, NON_AB, HIT_EV, K_EV, BB_EV, PITCH_GROUP,
    _sz, _lv, load_frames, load_subject, woba_weights, pa_rows, in_zone,
    nresults_unrounded, battedball_profile, pool_percentile,
)

# ══════════════════════════════════════════════════════════════════════════
# GOVERNED CONSTANTS — bat path
# ══════════════════════════════════════════════════════════════════════════
# Physical column names, aliased to business-readable names ONCE, here.
# Downstream code never touches the raw names (metadata-mapper requirement).
BP_COLS = {
    'attack_angle': 'attack_angle',
    'attack_direction': 'attack_direction',
    'swing_path_tilt': 'swing_path_tilt',
    'intercept_ball_minus_batter_pos_x_inches': 'intercept_side_in',
    'intercept_ball_minus_batter_pos_y_inches': 'intercept_depth_in',
    'bat_speed': 'bat_speed',
    'swing_length': 'swing_length',
}
BP_MEASURES = list(BP_COLS.values())

BAT_PATH_FIRST_SEASON = 2025      # attack_*/tilt/intercept sensor boundary
BAT_SPEED_FIRST_SEASON = 2024     # bat_speed / swing_length sensor boundary
SWING_FLOOR = 25                  # tracked swings below which means are NULL
BUNT_DESC = ['foul_bunt', 'missed_bunt']   # in SWINGS, but not swing paths (O-18)
DEGENERATE_BAT_SPEED = 25.0       # mph — below this the path columns are noise (O-18)

# MLB glossary reference values, carried in as CONTEXT ONLY (never computed here)
LG_ATTACK_ANGLE_MEAN = 10.0       # deg — "MLB average attack angle is about 10"
IDEAL_AA_LO, IDEAL_AA_HI = 5.0, 20.0   # deg — glossary "ideal attack angle range"
LG_TILT_MEAN = 32.0               # deg — "Major League average swing path tilt ~32"
ADJ_EV_FLOOR = 88.0               # mph — the hyper_speed floor proven in O-17


# ══════════════════════════════════════════════════════════════════════════
# POPULATION — the swing atom
# ══════════════════════════════════════════════════════════════════════════
def swing_rows(df):
    """The governed swing population: `description in SWINGS`.
    Bat-path columns are populated on swings only; every bat-path denominator
    in this kernel is a swing count, never a pitch count."""
    return df[df.description.isin(SWINGS)]


def bat_path_population(df):
    """BP-0 — the governed bat-path population (O-18).

    Swings, EXCLUDING bunts (`foul_bunt`, `missed_bunt`): a bunt is in the
    governed SWINGS list but is not a swing path, and bunt rows are the only
    ones in the 2025-26 Phillies frame where `swing_path_tilt` goes NULL while
    `attack_angle` is present.

    Rows with `bat_speed < 25` mph are NOT dropped here — they are marked
    `degenerate_path` so every downstream panel can exclude them from central
    tendencies while still counting them. Nothing is silently discarded."""
    s = swing_rows(df).copy()
    s = s[~s.description.isin(BUNT_DESC)]
    if 'bat_speed' in s.columns:
        s['degenerate_path'] = s.bat_speed.notna() & (s.bat_speed < DEGENERATE_BAT_SPEED)
    else:
        s['degenerate_path'] = False
    return s


def tracked_swings(df):
    """Bat-path population rows on which the bat was tracked and the path is
    not degenerate. `attack_angle` is the sentinel gate (asserted C6a-C6d)."""
    s = bat_path_population(df)
    if 'attack_angle' not in s.columns:
        return s.iloc[0:0]
    return s[s.attack_angle.notna() & ~s.degenerate_path]


def with_bat_path(df):
    """Renames the physical columns to their business names, once."""
    have = {k: v for k, v in BP_COLS.items() if k in df.columns}
    return df.rename(columns=have)


# ══════════════════════════════════════════════════════════════════════════
# CONVENTION ASSERTIONS — the build refuses to publish if any of these fail
# ══════════════════════════════════════════════════════════════════════════
def assert_conventions(pos_all, verbose=True):
    """Proves, against the data, every semantic claim this kernel makes.

    Population: ALL Phillies batters, regular season, most recent full season
    with bat path — never the subject alone, so the conventions cannot be
    fitted to the subject's own quirks.

    Returns a DataFrame of checks; raises AssertionError on any hard failure.
    """
    d = pos_all[(pos_all.game_type == 'R') & (pos_all.game_year >= BAT_PATH_FIRST_SEASON)].copy()
    d = with_bat_path(d)
    sw = bat_path_population(d)
    sw = sw[sw.attack_angle.notna() & ~sw.degenerate_path].copy()
    sw['px_inside'] = np.where(sw.stand == 'R', -sw.plate_x, sw.plate_x)   # + = INSIDE
    rows = []

    def add(cid, claim, stat, value, rule, ok, hard=True):
        rows.append(dict(check=cid, claim=claim, statistic=stat,
                         value=round(float(value), 4), rule=rule,
                         status='PASS' if ok else 'FAIL', hard=hard))

    # C1 — intercept_side_in is the LATERAL axis (distance from the body)
    for st in ('R', 'L'):
        s = sw[sw.stand == st]
        r = s.intercept_side_in.corr(s.px_inside)
        add(f'C1-{st}', 'intercept_side_in = lateral distance from the batter; '
                        'an INSIDE pitch is met CLOSER to the body',
            f'corr(intercept_side_in, inside-ness) | stand={st}', r, 'r < -0.60', r < -0.60)

    # C2 — intercept_depth_in is the DEPTH axis (exogenous timing anchor)
    r = sw.intercept_depth_in.corr(sw.release_speed)
    add('C2', 'intercept_depth_in = depth in front of the batter; a SLOWER pitch '
              'is met FURTHER out front',
        'corr(intercept_depth_in, release_speed)', r, 'r < -0.35', r < -0.35)

    # C3 — neither intercept axis is a HEIGHT axis
    rz = abs(sw.intercept_side_in.corr(sw.plate_z))
    add('C3', 'no vertical intercept component ships; neither axis tracks pitch height '
              'the way a height axis would',
        '|corr(intercept_side_in, plate_z)|', rz, '|r| < 0.30', rz < 0.30)

    # C4 — attack_direction SIGN (O-15). Anchor: hard-hit air balls, where the
    #      ball leaves close to the barrel's direction of travel.
    b = sw[(sw.type == 'X') & sw.hc_x.notna() & sw.hc_y.notna()
           & (sw.launch_speed >= 95) & sw.bb_type.isin(['line_drive', 'fly_ball'])].copy()
    spray = np.degrees(np.arctan2(b.hc_x - 125.42, 198.27 - b.hc_y))
    b['pull_spray'] = np.where(b.stand == 'R', -spray, spray)      # + = PULL side
    r = b.attack_direction.corr(b.pull_spray)
    add('C4', 'attack_direction is PULL-NEGATIVE / OPPO-POSITIVE in this data plane '
              '(O-15 — the INVERSE of the published MLB glossary convention)',
        'corr(attack_direction, pull-side spray) on hard-hit air balls', r,
        'r < -0.50', r < -0.50)

    # C5 — attack_direction is STAND-NORMALISED, not a fixed field frame
    signs = []
    for st in ('R', 'L'):
        s = b[b.stand == st]
        signs.append(s.attack_direction.corr(s.pull_spray))
    same = (signs[0] < 0) and (signs[1] < 0)
    add('C5', 'attack_direction is stand-normalised: the sign means the same thing '
              'for LHH and RHH (so it is an inverted convention, not a field frame)',
        'sign of corr for R and for L', min(signs), 'both < 0', same)

    # C6 — tracking gates. attack_angle/attack_direction share ONE gate exactly;
    #      swing_path_tilt and intercept_* have slightly wider gates (O-18).
    s = d[d.description.isin(SWINGS)]
    gate = s.attack_angle.notna()
    ex = int((s.attack_direction.notna() != gate).sum())
    add('C6a', 'attack_angle and attack_direction share ONE tracking gate exactly',
        'rows where notna() disagrees', ex, '== 0', ex == 0)
    for c, cid in [('swing_path_tilt', 'C6b'), ('intercept_side_in', 'C6c')]:
        r = float((s[c].notna() != gate).mean())
        add(cid, f'{c} gate agrees with attack_angle to within 0.2% (O-18: the '
                 f'disagreements are bunts and checked swings)',
            f'share of swings where {c} notna() disagrees', r, '< 0.002', r < 0.002)
    # C6d — every gate disagreement is a bunt or a degenerate-speed swing
    bad = s[(s.swing_path_tilt.notna() != gate)]
    isbunt = bool(len(bad) == 0 or ((bad.description.isin(BUNT_DESC))
                                    | (bad.bat_speed < DEGENERATE_BAT_SPEED)).all())
    add('C6d', 'O-18: every swing_path_tilt gate disagreement is a bunt or a '
               'checked swing under 25 mph, never a normal swing',
        'all disagreements explained', 1.0 if isbunt else 0.0, '== 1', isbunt)

    # C7 — O-17: hyper_speed is a deterministic transform of launch_speed
    if 'hyper_speed' in d.columns:
        h = s[s.hyper_speed.notna() & s.launch_speed.notna()]
        frac = float(np.isclose(h.hyper_speed, np.maximum(h.launch_speed, ADJ_EV_FLOOR)).mean())
        add('C7', 'O-17: hyper_speed == max(launch_speed, 88); it is NOT independent '
                  'information and must never be reported as a separate measure',
            'share of rows satisfying the identity', frac, '> 0.999', frac > 0.999)

    # C8 — attack_angle relates to launch_angle in the physically expected direction
    hh = sw[(sw.type == 'X') & (sw.launch_speed >= 95)]
    r = hh.attack_angle.corr(hh.launch_angle)
    add('C8', 'attack_angle (bat) predicts launch_angle (ball) on well-struck contact',
        'corr(attack_angle, launch_angle) on hard-hit BIP', r, 'r > 0.25', r > 0.25)

    out = pd.DataFrame(rows)
    if verbose:
        print(out.to_string(index=False))
    bad = out[(out.status == 'FAIL') & out.hard]
    if len(bad):
        raise AssertionError('bat-path convention assertions FAILED:\n' + bad.to_string(index=False))
    return out


# ══════════════════════════════════════════════════════════════════════════
# BP-1 — swing path profile (NEW-PROVISIONAL)
# ══════════════════════════════════════════════════════════════════════════
def swing_path_profile(level, df, floor=SWING_FLOOR):
    """BP-1. The governed bat-path panel at any grain.

    Grain     : one row per `level`, over the TRACKED SWING population.
    Denominator: tracked swings. `tracking_coverage` = tracked / all swings and
                 ships beside every value so a coverage gap can never be read
                 as a behaviour change.
    Null policy: below `floor` tracked swings every central tendency is NULL
                 (sensor-boundary standard, uc-pos-009). Counts are never NULL.
    Sign note  : `attack_direction` is PULL-NEGATIVE here (O-15). The derived
                 `pull_direction` flips it so a consumer reading the MLB glossary
                 convention gets the right answer; BOTH ship.
    """
    level = _lv(level)
    d = with_bat_path(df)
    allsw = bat_path_population(d)
    tr = (allsw[allsw.attack_angle.notna() & ~allsw.degenerate_path]
          if 'attack_angle' in allsw.columns else allsw.iloc[0:0])
    base = allsw.groupby(level, as_index=False).agg(swings=_sz())
    if tr.empty:
        for c in ['tracked_swings'] + BP_MEASURES:
            base[c] = np.nan
        base['tracked_swings'] = 0
        return base
    agg = tr.groupby(level, as_index=False).agg(
        tracked_swings=_sz(),
        attack_angle=('attack_angle', 'mean'),
        attack_angle_med=('attack_angle', 'median'),
        attack_direction=('attack_direction', 'mean'),
        swing_path_tilt=('swing_path_tilt', 'mean'),
        swing_path_tilt_med=('swing_path_tilt', 'median'),
        intercept_side_in=('intercept_side_in', 'mean'),
        intercept_depth_in=('intercept_depth_in', 'mean'),
        bat_speed=('bat_speed', 'mean'),
        swing_length=('swing_length', 'mean'))
    ideal = tr[tr.attack_angle.between(IDEAL_AA_LO, IDEAL_AA_HI)].groupby(
        level, as_index=False).agg(ideal_aa_swings=_sz())
    out = base.merge(agg, on=level, how='left').merge(ideal, on=level, how='left')
    out['tracked_swings'] = out.tracked_swings.fillna(0).astype(int)
    out['ideal_aa_swings'] = out.ideal_aa_swings.fillna(0).astype(int)
    out['tracking_coverage'] = np.where(out.swings > 0, out.tracked_swings / out.swings, np.nan)
    out['ideal_aa_rate'] = np.where(out.tracked_swings > 0,
                                    out.ideal_aa_swings / out.tracked_swings, np.nan)
    out['pull_direction'] = -out.attack_direction        # O-15 corrected view
    below = out.tracked_swings < floor
    out.loc[below, [c for c in out.columns if c in BP_MEASURES
                    or c in ('attack_angle_med', 'swing_path_tilt_med',
                             'ideal_aa_rate', 'pull_direction')]] = np.nan
    out['below_swing_floor'] = below
    return out


# ══════════════════════════════════════════════════════════════════════════
# PU-1 — popup signature (NEW-PROVISIONAL)
# ══════════════════════════════════════════════════════════════════════════
def popup_signature(level, df, floor=10):
    """PU-1. Bat path on popups vs every other tracked ball in play, at `level`.

    Grain      : one row per (`level`, is_popup).
    Population : tracked-swing BIP only. `bb_type` is classifier-derived and
                 complete, so the popup flag itself has no sensor gap; the bat
                 path does, which is why the population is the tracked subset
                 and `n` ships on every row.
    Floor      : 10 BIP — deliberately lower than the 50-PA rate floor because
                 this is a CONTRAST of means, not a rate estimate. Every cell
                 below `floor` is flagged, and the report must carry the flag.
    """
    level = _lv(level)
    d = with_bat_path(df)
    b = bat_path_population(d)
    b = b[(b.type == 'X') & b.attack_angle.notna() & ~b.degenerate_path].copy()
    b['is_popup'] = b.bb_type == 'popup'
    out = b.groupby(level + ['is_popup'], as_index=False).agg(
        n=_sz(),
        attack_angle=('attack_angle', 'mean'),
        attack_direction=('attack_direction', 'mean'),
        swing_path_tilt=('swing_path_tilt', 'mean'),
        intercept_side_in=('intercept_side_in', 'mean'),
        intercept_depth_in=('intercept_depth_in', 'mean'),
        bat_speed=('bat_speed', 'mean'),
        swing_length=('swing_length', 'mean'),
        launch_angle=('launch_angle', 'mean'),
        launch_speed=('launch_speed', 'mean'),
        plate_z=('plate_z', 'mean'))
    out['pull_direction'] = -out.attack_direction
    out['below_floor'] = out.n < floor
    return out


def popup_rate(level, df):
    """PU-2. Popup share of balls in play at any grain, on the COMPLETE
    `bb_type` classifier (no sensor gate) so it reconciles with the v1.0.0
    `battedball_profile.pu_rate` exactly."""
    level = _lv(level)
    b = df[df.type == 'X']
    tot = b.groupby(level, as_index=False).agg(bip=_sz())
    pu = b[b.bb_type == 'popup'].groupby(level, as_index=False).agg(popups=_sz())
    out = tot.merge(pu, on=level, how='left')
    out['popups'] = out.popups.fillna(0).astype(int)
    out['pu_rate'] = np.where(out.bip > 0, out.popups / out.bip, np.nan)
    return out


# ══════════════════════════════════════════════════════════════════════════
# PB-1 — peer-baseline delta (NEW-PROVISIONAL) — the O-16 control
# ══════════════════════════════════════════════════════════════════════════
def peer_delta(pos_all, subject, metric, y0, y1, min_swings=200, agg='mean'):
    """PB-1. Year-over-year change for the subject, NET of the change seen by a
    peer cohort measured on the same instrument in the same seasons.

    Exists because O-16: `swing_path_tilt` moved team-wide between 2025 and
    2026. A raw YoY delta on an instrumented column cannot distinguish a real
    swing change from a calibration change; a peer-netted delta can.

    Cohort: Phillies batters with >= `min_swings` tracked swings in BOTH years.
    Returns (tidy DataFrame of every peer, dict of the subject's headline).
    """
    d = with_bat_path(pos_all[(pos_all.game_type == 'R')
                              & pos_all.game_year.isin([y0, y1])])
    sw = bat_path_population(d)
    sw = sw[sw.attack_angle.notna() & ~sw.degenerate_path]
    g = sw.groupby(['batter', 'game_year']).agg(
        n=(metric, 'size'), val=(metric, agg)).reset_index()
    p = g.pivot(index='batter', columns='game_year')
    p.columns = [f'{a}_{b}' for a, b in p.columns]
    p = p[(p[f'n_{y0}'] >= min_swings) & (p[f'n_{y1}'] >= min_swings)].copy()
    p['delta'] = p[f'val_{y1}'] - p[f'val_{y0}']
    p = p.reset_index()
    med = float(p.delta.median())
    if subject not in set(p.batter):
        return p, {'metric': metric, 'subject_in_cohort': False}
    s = p[p.batter == subject].iloc[0]
    head = {'metric': metric, 'subject_in_cohort': True, 'cohort_n': int(len(p)),
            f'subject_{y0}': float(s[f'val_{y0}']), f'subject_{y1}': float(s[f'val_{y1}']),
            'subject_delta': float(s.delta), 'peer_median_delta': med,
            'peer_netted_delta': float(s.delta - med),
            'subject_rank_most_negative': int((p.delta < s.delta).sum()) + 1}
    return p, head


# ══════════════════════════════════════════════════════════════════════════
# BP-2 — bat path x pitch group (the DPO's requested grain)
# ══════════════════════════════════════════════════════════════════════════
def path_by_pitch_group(df, extra_level=None, floor=SWING_FLOOR):
    """BP-2. `swing_path_profile` at the `pitch_group` grain, with the popup
    rate joined on. `pitch_group` is the DPO's own mapping, inherited verbatim
    from `PITCH_GROUP` (dp_uc18 lineage); unmapped pitch types fall to 'other'
    and are retained, never dropped."""
    level = (['pitch_group'] if extra_level is None
             else _lv(extra_level) + ['pitch_group'])
    d = df.copy()
    if 'pitch_group' not in d.columns:
        d['pitch_group'] = d.pitch_type.map(PITCH_GROUP).fillna('other')
    prof = swing_path_profile(level, d, floor=floor)
    pu = popup_rate(level, d)
    return prof.merge(pu, on=level, how='left')
