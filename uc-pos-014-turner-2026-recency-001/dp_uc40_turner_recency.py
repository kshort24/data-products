"""
dp_uc40_turner_recency.py — Layer-3 BUILD for uc-pos-014-turner-2026-recency-001
================================================================================
UC #40 · Phillies Offense (pos) value stream · subject Trea Turner (607208)
Parent : uc-pos-006-turner-2026-offense-001 / dp_uc24 (2026-07-21, thru 07-20)

Implements exactly what 02_engineering_design.md models and 03_governance.md
specifies. No metric is defined here; every KPI comes from dp_uc40_kernel.py,
which is either transcribed from the governed Baseball Functions notebook or
inherited from the dp_uc33/34/37 `_fix` lineage.

Run:
    DP_UC40_DATA=<MLB repo path> python dp_uc40_turner_recency.py [outdir]
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dp_uc40_kernel as K                                    # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
P = lambda n: os.path.join(OUT, f'dp_uc40_{n}')
R = lambda df, n: (df.to_csv(P(n + '.csv'), index=False), print(f'  wrote {n}.csv  {df.shape}'))

pd.set_option('display.width', 200)
pd.set_option('display.max_columns', 60)

H: dict = {}          # headlines.json — every number the report may quote


def sec(t):
    print('\n' + '=' * 78 + f'\n{t}\n' + '=' * 78)


# ═════════════════════════════════════════════════════════════ LOAD ═══════
sec('LOAD')
w = K.woba_weights()
m_all = K.load_subject()                       # career, R + postseason
m = m_all[m_all.game_type == 'R'].copy()       # every rate uses R only
m = K.add_windows(m)
m26 = m[m.game_year == 2026].copy()
mphi = m[m.game_year >= 2023].copy()

print(f'career R rows      : {len(m):,}   seasons {m.game_year.min()}-{m.game_year.max()}')
print(f'2026 R rows        : {len(m26):,}  games {m26.game_pk.nunique()}  '
      f'{m26.game_date.min().date()} .. {m26.game_date.max().date()}')
print(f'postseason excluded: {len(m_all) - len(m):,} rows '
      f'({sorted(m_all[m_all.game_type != "R"].game_type.unique())})')

H['as_of'] = str(m26.game_date.max().date())
H['games_2026'] = int(m26.game_pk.nunique())
H['pitches_2026'] = int(len(m26))

# Coordinate-convention assertion (uc-pps-025 rule: assert, don't assume).
_gb = K.derive_loc(m26[(m26.type == 'X') & (m26.bb_type == 'ground_ball')])
_gb = _gb.assign(hd=K.hit_direction(_gb))
_med = _gb[_gb.hd == 'Pull'].loc_x.median()
assert _med < 0, f'coordinate convention failed: RHB pulled GB median loc_x={_med}'
print(f'coord assertion OK : RHB pulled-GB median loc_x = {_med:.2f} (< 0 = LF side)')

# xwOBA grain assertion (uc-pps-028 settled fact).
_pa_rows = K.pa_rows(m26)
_n_pitch_xw = int(m26.estimated_woba_using_speedangle.notna().sum())
_n_pa_xw = int(_pa_rows.estimated_woba_using_speedangle.notna().sum())
print(f'xwOBA grain        : {_n_pitch_xw} non-null pitch rows vs {_n_pa_xw} on PA rows '
      f'-> {"PER-PA CONFIRMED" if _n_pitch_xw == _n_pa_xw else "MIXED GRAIN"}')
H['xwoba_grain_pitch_rows'] = _n_pitch_xw
H['xwoba_grain_pa_rows'] = _n_pa_xw


# ═════════════════════════════════════════ Q4 — CAREER PANEL ("good") ═════
sec('Q4 · CAREER BY SEASON — what "good" looked like')
car = K.nresults_unrounded(['game_year'], m, w)
era = m.groupby('game_year').era.agg(lambda s: s.mode().iat[0]).rename('era')
src = m.groupby('game_year').src.agg(lambda s: s.mode().iat[0]).rename('src')
car = car.merge(era, on='game_year').merge(src, on='game_year')
car['hr_600'] = car.hrs / car.plate_apps * 600
car['xbh'] = car.doubles + car.triples + car.hrs
xw = m.groupby('game_year', as_index=False).agg(
    xwoba=('estimated_woba_using_speedangle', 'mean'))
car = car.merge(xw, on='game_year')
car['below_floor'] = car.plate_apps < K.PA_FLOOR
cols = ['game_year', 'era', 'src', 'plate_apps', 'at_bats', 'hits', 'doubles', 'triples',
        'hrs', 'xbh', 'walks', 'strikeouts', 'ba', 'obp', 'slg', 'ops', 'iso', 'woba',
        'xwoba', 'babip', 'krate', 'bbrate', 'hr_600', 'below_floor']
car_out = car[cols].round(4)
R(car_out, 'career_by_season')
print(car_out.to_string(index=False))

cc = K.battedball_profile(['game_year'], m)
cc = cc.merge(K.hard_hit_rate_fix(['game_year'], m)[['game_year', 'hard_hits', 'hard_hit_rate']],
              on='game_year', how='left')
cc = cc.merge(K.barrel_rate_g(['game_year'], m)[['game_year', 'barrels', 'barrel_rate']],
              on='game_year', how='left')
cc = cc.merge(K.xcontact(['game_year'], m)[['game_year', 'xba_bip', 'xwobacon_bip']],
              on='game_year', how='left')
# O-8 exposure: tracked-only denominator beside the governed one
_bip = m[m.type == 'X']
_tr = _bip[_bip.launch_speed.notna()]
o8 = (_tr[_tr.launch_speed >= 95].groupby('game_year').size().rename('hard_tracked')
      .to_frame().join(_tr.groupby('game_year').size().rename('tracked_bip')).reset_index())
o8['hard_hit_rate_tracked_only'] = o8.hard_tracked / o8.tracked_bip
cc = cc.merge(o8, on='game_year', how='left')
R(cc.round(4), 'career_contact')
print(cc[['game_year', 'bips', 'tracked_bips', 'mean_ev', 'mean_la', 'hard_hit_rate',
          'hard_hit_rate_tracked_only', 'barrel_rate', 'gb_rate', 'fb_rate', 'ld_rate',
          'pu_rate', 'xwobacon_bip']].round(3).to_string(index=False))

ca = K.swing_rate(['game_year'], m)
for f, keep in [(K.whiff_rate_fix, ['game_year', 'swings', 'whiffs', 'whiff_rate']),
                (K.chase_rate_g, ['game_year', 'ooz', 'chase_rate', 'in_zone_rate']),
                (K.zone_swing_whiff, ['game_year', 'z_pitches', 'swing_rate_in_zone',
                                      'whiff_rate_in_zone']),
                (K.ooz_whiff_rate, ['game_year', 'ooz_whiff_rate']),
                (K.in_zone_rate_fix, ['game_year', 'in_zone_rate_fix', 'zone_null_rate']),
                (K.srfp, ['game_year', 'srfp']),
                (K.fpsr_fix, ['game_year', 'fpsr'])]:
    ca = ca.merge(f(['game_year'], m)[keep], on='game_year', how='left',
                  suffixes=('', '_d'))
ca = ca.loc[:, ~ca.columns.duplicated()]
R(ca.round(4), 'career_approach')
print(ca[['game_year', 'pitches', 'swing_rate', 'whiff_rate', 'chase_rate',
          'swing_rate_in_zone', 'whiff_rate_in_zone', 'in_zone_rate', 'in_zone_rate_fix',
          'zone_null_rate', 'srfp']].round(4).to_string(index=False))

cp = K.pull_air_rate_fix(['game_year'], m)
R(cp.round(4), 'career_pull_air')
print(cp.round(3).to_string(index=False))

cb = K.bat_tracking(['game_year'], m)
R(cb.round(4), 'career_bat_tracking')
print(cb.round(3).to_string(index=False))

H['career'] = car_out.set_index('game_year')[
    ['era', 'plate_apps', 'ba', 'obp', 'slg', 'ops', 'iso', 'woba', 'krate', 'bbrate', 'hrs']
].round(4).to_dict('index')


# ═══════════════════════════════════ Q1/Q2 — 2026 WINDOWS + MONTHLY ═══════
sec('Q1 · 2026 BY WINDOW — what is going on recently')
WL = ['W1_early (Mar 26-Jun 30)', 'W2_july (Jul 1-31)', 'W3_recent (Aug 1-Sep 2)']


def panel(level, df, label_order=None):
    """Assembles the standard hitter panel at any level, from kernel parts only."""
    r = K.nresults_unrounded(level, df, w)
    r = r.merge(K.battedball_profile(level, df, bip_floor=25), on=level, how='left',
                suffixes=('', '_bb'))
    r = r.merge(K.hard_hit_rate_fix(level, df)[level + ['hard_hits', 'hard_hit_rate']],
                on=level, how='left')
    r = r.merge(K.barrel_rate_g(level, df)[level + ['barrels', 'barrel_rate']],
                on=level, how='left')
    r = r.merge(K.xcontact(level, df, bip_floor=25)[level + ['xba_bip', 'xwobacon_bip']],
                on=level, how='left')
    r = r.merge(K.swing_rate(level, df)[level + ['swings', 'swing_rate']], on=level, how='left')
    r = r.merge(K.whiff_rate_fix(level, df)[level + ['whiffs', 'whiff_rate']], on=level, how='left')
    r = r.merge(K.chase_rate_g(level, df)[level + ['ooz', 'chase_rate', 'in_zone_rate']],
                on=level, how='left')
    r = r.merge(K.zone_swing_whiff(level, df)[level + ['z_pitches', 'swing_rate_in_zone',
                                                       'whiff_rate_in_zone']],
                on=level, how='left')
    r = r.merge(K.ooz_whiff_rate(level, df)[level + ['ooz_whiff_rate']], on=level, how='left')
    r = r.merge(K.in_zone_rate_fix(level, df)[level + ['in_zone_rate_fix', 'zone_null_rate']],
                on=level, how='left')
    r = r.merge(K.srfp(level, df)[level + ['srfp']], on=level, how='left')
    r = r.merge(K.fpsr_fix(level, df)[level + ['fpsr']], on=level, how='left')
    r = r.merge(K.pull_air_rate_fix(level, df)[level + ['total_pulls', 'pull_airs',
                                                        'pull_air_rate', 'pull_rate']],
                on=level, how='left')
    bt = K.bat_tracking(level, df, floor=25)
    if not bt.empty:
        r = r.merge(bt[level + ['tracked_swings', 'bat_speed_mu', 'swing_length_mu',
                                'attack_angle_mu', 'fast_swing_rate']], on=level, how='left')
    r['below_floor'] = r.plate_apps < K.PA_FLOOR
    if label_order:
        r[level[0]] = pd.Categorical(r[level[0]], label_order, ordered=True)
        r = r.sort_values(level[0])
    return r.loc[:, ~r.columns.duplicated()]


win = panel(['window'], m26, WL)
R(win.round(4), 'window_split')
SHOW = ['window', 'plate_apps', 'ba', 'obp', 'slg', 'ops', 'iso', 'woba', 'babip', 'krate',
        'bbrate', 'hrs', 'mean_ev', 'mean_la', 'hard_hit_rate', 'barrel_rate', 'pu_rate',
        'xwobacon_bip', 'swing_rate', 'chase_rate', 'whiff_rate', 'swing_rate_in_zone',
        'whiff_rate_in_zone', 'in_zone_rate', 'srfp', 'pull_air_rate', 'bat_speed_mu',
        'fast_swing_rate']
print(win[SHOW].round(3).to_string(index=False))
H['window'] = win.set_index('window')[[c for c in SHOW if c != 'window']].round(4).to_dict('index')

sec('Q1 · 2026 BY MONTH')
mon = panel(['month'], m26)
R(mon.round(4), 'monthly_master')
print(mon[['month', 'plate_apps', 'ba', 'obp', 'slg', 'ops', 'woba', 'krate', 'bbrate',
           'mean_ev', 'hard_hit_rate', 'barrel_rate', 'pu_rate', 'bat_speed_mu',
           'fast_swing_rate', 'below_floor']].round(3).to_string(index=False))
H['monthly'] = mon.set_index('month')[
    ['plate_apps', 'ba', 'obp', 'slg', 'ops', 'woba', 'krate', 'bbrate', 'mean_ev',
     'hard_hit_rate', 'barrel_rate', 'pu_rate', 'bat_speed_mu', 'fast_swing_rate',
     'below_floor']].round(4).to_dict('index')

# PHI-era window comparison: is W3 bad relative to his own Phillies norm?
sec('Q2 · PHI-ERA REFERENCE (2023-2025 combined) vs 2026 windows')
phi_ref = panel(['era'], mphi[mphi.game_year <= 2025])
R(phi_ref.round(4), 'phi_reference_2023_2025')
print(phi_ref[SHOW[1:]].round(3).to_string(index=False))
H['phi_2023_2025'] = phi_ref[[c for c in SHOW if c != 'window']].round(4).to_dict('records')[0]


# ═════════════════════════════════════ RC-5 BREAKPOINT SENSITIVITY ════════
sec('RC-5 · BREAKPOINT SENSITIVITY SCAN (the window was DPO-chosen)')
cands = ['2026-06-01', '2026-06-15', '2026-07-01', '2026-07-08', '2026-07-16',
         '2026-07-21', '2026-08-01', '2026-08-08', '2026-08-15', '2026-08-22']
scan = K.breakpoint_scan(m26, w, cands)
R(scan.round(4), 'breakpoint_scan')
print(scan[['breakpoint', 'pre_pa', 'post_pa', 'pre_ops', 'post_ops', 'd_ops',
            'pre_woba', 'post_woba', 'd_woba', 'below_floor']].round(3).to_string(index=False))
H['breakpoint_scan'] = scan[['breakpoint', 'pre_pa', 'post_pa', 'd_ops', 'd_woba',
                             'below_floor']].round(4).to_dict('records')


# ═══════════════════════════════════════════ RF-1 / RF-2 TRAJECTORY ═══════
sec('RF-1 · season-to-date trajectory (PHI era)  ·  RF-2 · rolling form')
run = K.running_line_pa(mphi, w, group='game_year')
R(run.round(4), 'running_line')
print(run.groupby('game_year').tail(1)[['game_year', 'cum_pa', 'cum_ba', 'cum_obp',
                                        'cum_slg', 'cum_woba']].round(3).to_string(index=False))
roll = K.rolling_form(m26, w, window_pa=100)
R(roll.round(4), 'rolling_form')
if len(roll):
    print(f'RF-2 n={len(roll)}  min_woba={roll.roll_woba.min():.3f} @PA{int(roll.loc[roll.roll_woba.idxmin(),"pa_idx"])}'
          f'  max_woba={roll.roll_woba.max():.3f} @PA{int(roll.loc[roll.roll_woba.idxmax(),"pa_idx"])}'
          f'  last={roll.roll_woba.iloc[-1]:.3f}')
    H['rf2'] = {'n': int(len(roll)), 'min_woba': float(roll.roll_woba.min()),
                'max_woba': float(roll.roll_woba.max()),
                'last_woba': float(roll.roll_woba.iloc[-1]),
                'last_ops': float(roll.roll_ops.iloc[-1]),
                'max_ops': float(roll.roll_ops.max()),
                'min_ops': float(roll.roll_ops.min())}


# ═══════════════════════════════════════ Q8 — PITCH GROUPS / TYPES ════════
sec('Q8 · PITCH GROUP x WINDOW (2026)')
pgw = panel(['window', 'pitch_group'], m26)
pgw['usage'] = pgw.pitches / pgw.groupby('window', observed=True).pitches.transform('sum')
keep = ['window', 'pitch_group', 'pitches', 'usage', 'plate_apps', 'ba', 'slg', 'woba',
        'krate', 'whiff_rate', 'chase_rate', 'swing_rate_in_zone', 'hard_hit_rate',
        'xwobacon_bip', 'below_floor']
R(pgw.round(4), 'pitch_group_window')
print(pgw[keep].round(3).to_string(index=False))
H['pitch_group_window'] = pgw[keep].round(4).astype(
    {'window': str}).to_dict('records')

sec('Q8 · PITCH GROUP x SEASON (PHI era)')
pgs = panel(['game_year', 'pitch_group'], mphi)
pgs['usage'] = pgs.pitches / pgs.groupby('game_year').pitches.transform('sum')
R(pgs.round(4), 'pitch_group_season')
print(pgs[['game_year', 'pitch_group', 'pitches', 'usage', 'plate_apps', 'ba', 'slg',
           'woba', 'whiff_rate', 'chase_rate', 'below_floor']].round(3).to_string(index=False))
H['pitch_group_season'] = pgs[['game_year', 'pitch_group', 'usage', 'plate_apps', 'ba',
                               'slg', 'woba', 'whiff_rate', 'below_floor']].round(4).to_dict('records')

sec('Q8 · PITCH TYPE x 2026 (season, >=25 pitches)')
pts = panel(['pitch_type'], m26)
pts = pts[pts.pitches >= 25].sort_values('pitches', ascending=False)
pts['usage'] = pts.pitches / len(m26)
R(pts.round(4), 'pitch_type_2026')
print(pts[['pitch_type', 'pitches', 'usage', 'plate_apps', 'ba', 'slg', 'woba',
           'whiff_rate', 'chase_rate', 'hard_hit_rate', 'below_floor']].round(3).to_string(index=False))
H['pitch_type_2026'] = pts[['pitch_type', 'pitches', 'usage', 'plate_apps', 'ba', 'slg',
                            'woba', 'whiff_rate', 'below_floor']].round(4).to_dict('records')


# ══════════════════════════════════════════════ Q8 — PLATOON ══════════════
sec('Q8 · PLATOON x SEASON (career)')
pls = panel(['game_year', 'p_throws'], m)
R(pls.round(4), 'platoon_season')
print(pls[['game_year', 'p_throws', 'plate_apps', 'ba', 'obp', 'slg', 'ops', 'woba',
           'krate', 'whiff_rate', 'chase_rate', 'hard_hit_rate', 'below_floor']].round(3).to_string(index=False))
H['platoon_season'] = pls[['game_year', 'p_throws', 'plate_apps', 'ba', 'obp', 'slg',
                           'ops', 'woba', 'krate', 'whiff_rate', 'below_floor']].round(4).to_dict('records')

sec('Q8 · PLATOON x WINDOW (2026)')
plw = panel(['window', 'p_throws'], m26)
R(plw.round(4), 'platoon_window')
print(plw[['window', 'p_throws', 'plate_apps', 'ba', 'obp', 'slg', 'ops', 'woba',
           'krate', 'whiff_rate', 'chase_rate', 'hard_hit_rate', 'mean_ev',
           'below_floor']].round(3).to_string(index=False))
H['platoon_window'] = plw[['window', 'p_throws', 'plate_apps', 'ba', 'obp', 'slg', 'ops',
                           'woba', 'krate', 'below_floor']].round(4).astype(
    {'window': str}).to_dict('records')

sec('PL-1 · PLATOON EXPOSURE + COUNTERFACTUAL')
exp = (K.pa_rows(m26).groupby(['window', 'p_throws'], observed=True).size()
       .rename('pa').reset_index())
exp['share'] = exp.pa / exp.groupby('window', observed=True).pa.transform('sum')
exp_all = (K.pa_rows(m).groupby(['game_year', 'p_throws']).size().rename('pa').reset_index())
exp_all['share'] = exp_all.pa / exp_all.groupby('game_year').pa.transform('sum')
R(exp.round(4), 'platoon_exposure_window')
R(exp_all.round(4), 'platoon_exposure_season')
print(exp.round(3).to_string(index=False))
print(exp_all[exp_all.game_year >= 2023].round(3).to_string(index=False))

cf_rows = []
for frm, to in [(WL[0], WL[2]), (WL[1], WL[2]), (WL[0], WL[1])]:
    c = K.platoon_counterfactual(m26, w, 'window', frm, to)
    c['from_label'], c['to_label'] = frm, to
    cf_rows.append(c)
cf = pd.concat(cf_rows, ignore_index=True)
R(cf.round(4), 'platoon_counterfactual')
print(cf[['from_label', 'to_label', 'metric', 'actual', 'reweighted_to_reference',
          'mix_effect']].round(4).to_string(index=False))
H['platoon_counterfactual'] = cf[['from_label', 'to_label', 'metric', 'actual',
                                  'reweighted_to_reference', 'mix_effect']].round(4).to_dict('records')


# ═════════════════════════════════════════════ COUNT LEVERAGE ═════════════
sec('COUNT STATE x WINDOW (2026)')
m26 = m26.assign(count_state=np.select(
    [m26.strikes == 2, m26.balls > m26.strikes],
    ['two_strike', 'ahead'], default='even_or_behind'))
cs = panel(['window', 'count_state'], m26)
R(cs.round(4), 'count_state_window')
print(cs[['window', 'count_state', 'pitches', 'plate_apps', 'ba', 'slg', 'woba',
          'krate', 'swing_rate', 'whiff_rate', 'below_floor']].round(3).to_string(index=False))


# ═══════════════════════════ Q2 — POPULATION BENCHMARK (G8 cohort) ════════
sec('Q2 · POPULATION POOL — Phillies hitter-seasons 2015-2026, >=50 PA')
pos_all, _ = K.load_frames()
pos_all = pos_all[pos_all.game_type == 'R'].copy()
pool = K.nresults_unrounded(['game_year', 'batter'], pos_all, w)
pool = pool[pool.plate_apps >= K.PA_FLOOR].copy()
for f, cols in [(K.whiff_rate_fix, ['whiff_rate']), (K.chase_rate_g, ['chase_rate']),
                (K.swing_rate, ['swing_rate']),
                (K.zone_swing_whiff, ['swing_rate_in_zone', 'whiff_rate_in_zone']),
                (K.hard_hit_rate_fix, ['hard_hit_rate']),
                (K.barrel_rate_g, ['barrel_rate']),
                (K.pull_air_rate_fix, ['pull_air_rate'])]:
    pool = pool.merge(f(['game_year', 'batter'], pos_all)[['game_year', 'batter'] + cols],
                      on=['game_year', 'batter'], how='left')
bbp = K.battedball_profile(['game_year', 'batter'], pos_all, bip_floor=25)
pool = pool.merge(bbp[['game_year', 'batter', 'mean_ev', 'mean_la', 'pu_rate', 'gb_rate']],
                  on=['game_year', 'batter'], how='left')
name = pos_all.groupby('batter').des.size().rename('_n')     # placeholder to keep grain
R(pool.round(4), 'population_pool')
print(f'pool: {len(pool)} hitter-seasons, {pool.batter.nunique()} players, '
      f'{pool.game_year.min()}-{pool.game_year.max()}')
H['pool_n'] = int(len(pool))
H['pool_players'] = int(pool.batter.nunique())

PCT_METRICS = ['ops', 'woba', 'slg', 'obp', 'ba', 'iso', 'krate', 'bbrate', 'whiff_rate',
               'chase_rate', 'swing_rate_in_zone', 'hard_hit_rate', 'barrel_rate',
               'mean_ev', 'pu_rate', 'pull_air_rate']
season26 = car[car.game_year == 2026].iloc[0]
win3 = win[win.window == WL[2]].iloc[0]
w3_pool_row = {}
rows = []
for mt in PCT_METRICS:
    v_season = season26.get(mt, np.nan)
    if pd.isna(v_season) and mt in cc.columns:
        v_season = cc[cc.game_year == 2026].iloc[0][mt]
    if pd.isna(v_season) and mt in ca.columns:
        v_season = ca[ca.game_year == 2026].iloc[0][mt]
    if pd.isna(v_season) and mt in cp.columns:
        v_season = cp[cp.game_year == 2026].iloc[0][mt]
    v_w3 = win3.get(mt, np.nan)
    rows.append({'metric': mt,
                 'turner_2026_season': v_season,
                 'pctile_season': K.pool_percentile(pool, mt, v_season) if pd.notna(v_season) else np.nan,
                 'turner_2026_W3_recent': v_w3,
                 'pctile_W3_as_a_season': K.pool_percentile(pool, mt, v_w3) if pd.notna(v_w3) else np.nan,
                 'pool_median': pool[mt].median() if mt in pool else np.nan})
pct = pd.DataFrame(rows)
R(pct.round(4), 'profile_percentiles')
print(pct.round(3).to_string(index=False))
H['percentiles'] = pct.round(4).to_dict('records')


# ══════════════════════ PARENT REPRODUCTION (uc-pps-028 standing check) ═══
sec('PARENT REPRODUCTION — uc-pos-006 / dp_uc24 published figures')
PARENT = {  # transcribed from out/dp_uc24_turner_2026_review_results_by_season.csv
    2015: dict(plate_apps=44, ba=.225, obp=.295, slg=.325, ops=.620, woba=.278, krate=.182 if False else .273),
    2016: dict(plate_apps=324, ba=.342, obp=.370, slg=.567, ops=.937, woba=.395, krate=.182),
    2017: dict(plate_apps=448, ba=.283, obp=.337, slg=.450, ops=.787, woba=.337, krate=.179),
    2018: dict(plate_apps=738, ba=.271, obp=.340, slg=.415, ops=.755, woba=.330, krate=.179),
    2019: dict(plate_apps=568, ba=.297, obp=.350, slg=.496, ops=.847, woba=.355, krate=.199),
    2020: dict(plate_apps=259, ba=.335, obp=.394, slg=.588, ops=.982, woba=.413, krate=.139),
    2021: dict(plate_apps=645, ba=.327, obp=.372, slg=.535, ops=.907, woba=.386, krate=.171),
    2022: dict(plate_apps=707, ba=.297, obp=.341, slg=.465, ops=.806, woba=.349, krate=.185),
    2023: dict(plate_apps=692, ba=.265, obp=.316, slg=.456, ops=.773, woba=.332, krate=.217),
    2024: dict(plate_apps=541, ba=.294, obp=.336, slg=.467, ops=.804, woba=.348, krate=.181),
    2025: dict(plate_apps=641, ba=.302, obp=.353, slg=.454, ops=.807, woba=.350, krate=.167),
    2026: dict(plate_apps=433, ba=.246, obp=.296, slg=.396, ops=.691, woba=.303, krate=.224),
}
m_par = m[m.game_date <= K.PARENT_ASOF].copy()
m_par = K.attach_woba_weight_cols(m_par, w)
legacy = K.legacy_get_stats(['game_year'], m_par).set_index('game_year')
cur = K.nresults_unrounded(['game_year'], m_par, w).set_index('game_year')
rows = []
for yr, pub in PARENT.items():
    for mt, pv in pub.items():
        lv = legacy.loc[yr, mt] if yr in legacy.index and mt in legacy.columns else np.nan
        cvv = cur.loc[yr, mt] if yr in cur.index and mt in cur.columns else np.nan
        rows.append({'season': yr, 'metric': mt, 'parent_published': pv,
                     'legacy_recomputed': lv, 'current_definition': cvv,
                     'repro_delta': (round(lv, 3) - pv) if pd.notna(lv) else np.nan,
                     'definition_delta': (cvv - lv) if pd.notna(lv) and pd.notna(cvv) else np.nan})
rep = pd.DataFrame(rows)
rep['repro_pass'] = rep.repro_delta.abs() < 5e-4
R(rep.round(5), 'parent_reproduction')
n_pass = int(rep.repro_pass.sum())
print(f'parent-reproduction: {n_pass}/{len(rep)} figures reproduce EXACTLY on the '
      f"parent's own definitions and window (<= {K.PARENT_ASOF})")
print(rep[~rep.repro_pass][['season', 'metric', 'parent_published', 'legacy_recomputed',
                            'repro_delta']].to_string(index=False))
print('\nDefinitional drift, parent get_stats -> current nresults_unrounded (2026 only):')
print(rep[(rep.season == 2026)][['metric', 'legacy_recomputed', 'current_definition',
                                 'definition_delta']].round(4).to_string(index=False))
H['parent_repro'] = {'checks': int(len(rep)), 'pass': n_pass,
                     'window': K.PARENT_ASOF,
                     'fails': rep[~rep.repro_pass][['season', 'metric', 'parent_published',
                                                    'legacy_recomputed']].round(4).to_dict('records')}

# the parent's open call, resolved
par_july = K.legacy_get_stats(['month'], K.attach_woba_weight_cols(
    m26[m26.game_date <= K.PARENT_ASOF].assign(month=lambda d: d.game_date.dt.month), w))
H['parent_july_asof_0720'] = par_july[par_july.month == 7][
    ['month', 'plate_apps', 'ba', 'obp', 'slg', 'ops', 'woba']].round(4).to_dict('records')
print('\nParent\'s July claim as it stood on 2026-07-20:')
print(par_july[par_july.month == 7][['month', 'plate_apps', 'ba', 'obp', 'slg', 'ops',
                                     'woba']].round(3).to_string(index=False))


# ══════════════════════════ AD-1 APPROACH DIFFERENTIAL (NEW-PROVISIONAL) ══
sec('AD-1 · APPROACH DIFFERENTIAL — in-zone swing minus chase')
# Rule-1 grep executed at design time: the only prior governed relative is
# uc-pos-005 OZ-3 "edge decision differential", which is the SHADOW-BAND form
# (shadow_in swing - shadow_out swing). AD-1 is the whole-zone form. OZ-3 is
# INHERITED, not redefined, and OZ-3's edge-case warning is inherited verbatim:
# AD-1 can fall while judgment improves if the hitter cuts swings on BOTH
# sides, so it may never be headlined alone - always beside its two components.
ad_season = ca[['game_year', 'swing_rate_in_zone', 'chase_rate']].copy()
ad_season['approach_differential'] = ad_season.swing_rate_in_zone - ad_season.chase_rate
ad_season = ad_season.merge(car_out[['game_year', 'plate_apps', 'below_floor']], on='game_year')
ad_season['rank_low_to_high'] = ad_season[~ad_season.below_floor].approach_differential.rank()
R(ad_season.round(4), 'approach_differential_season')
print(ad_season.round(4).to_string(index=False))
ad_win = win[['window', 'swing_rate_in_zone', 'chase_rate', 'plate_apps']].copy()
ad_win['approach_differential'] = ad_win.swing_rate_in_zone - ad_win.chase_rate
R(ad_win.round(4), 'approach_differential_window')
print(ad_win.round(4).to_string(index=False))
H['ad1_season'] = ad_season.round(4).to_dict('records')
H['ad1_window'] = ad_win.round(4).astype({'window': str}).to_dict('records')


# ═══════════════════ ST-1 SHIFT TESTS — is the window move bigger than noise ══
sec('ST-1 · WINDOW-SHIFT UNCERTAINTY (NEW-PROVISIONAL)')
# Standing honesty requirement: a five-week window can move a mean by chance.
# Two-sample Welch z on continuous measures; two-proportion z on rates. These
# are DESCRIPTIVE uncertainty bands on a non-random, self-selected window --
# they are NOT hypothesis tests of a causal claim, and the report says so.
def _welch(a, b, name):
    a, b = a.dropna(), b.dropna()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return {'measure': name, 'kind': 'mean', 'n_july': len(a), 'n_recent': len(b),
            'july': a.mean(), 'recent': b.mean(), 'delta': b.mean() - a.mean(),
            'se': se, 'z': (b.mean() - a.mean()) / se if se else np.nan}


def _prop(ka, na, kb, nb, name):
    pa_, pb_ = ka / na, kb / nb
    pp = (ka + kb) / (na + nb)
    se = np.sqrt(pp * (1 - pp) * (1 / na + 1 / nb))
    return {'measure': name, 'kind': 'rate', 'n_july': na, 'n_recent': nb,
            'july': pa_, 'recent': pb_, 'delta': pb_ - pa_, 'se': se,
            'z': (pb_ - pa_) / se if se else np.nan}


jl, rc = WL[1], WL[2]
sw_j = m26[(m26.window == jl) & m26.description.isin(K.SWINGS) & m26.bat_speed.notna()]
sw_r = m26[(m26.window == rc) & m26.description.isin(K.SWINGS) & m26.bat_speed.notna()]
bp_j = m26[(m26.window == jl) & (m26.type == 'X')]
bp_r = m26[(m26.window == rc) & (m26.type == 'X')]
tests = [
    _welch(sw_j.bat_speed, sw_r.bat_speed, 'bat speed (mph, tracked swings)'),
    _welch(bp_j.launch_speed, bp_r.launch_speed, 'exit velocity (mph, tracked BIP)'),
    _welch(bp_j.launch_angle, bp_r.launch_angle, 'launch angle (deg, tracked BIP)'),
    _prop((bp_j.bb_type == 'popup').sum(), len(bp_j),
          (bp_r.bb_type == 'popup').sum(), len(bp_r), 'popup rate (of BIP)'),
    _prop((bp_j.launch_speed >= 95).sum(), len(bp_j),
          (bp_r.launch_speed >= 95).sum(), len(bp_r), 'hard-hit rate (of BIP)'),
    _prop((sw_j.bat_speed >= 75).sum(), len(sw_j),
          (sw_r.bat_speed >= 75).sum(), len(sw_r), 'fast-swing rate (of tracked swings)'),
]
# Second, better-powered comparison: the recent window against his own
# 2023-25 Phillies norm (1,871 PA) rather than against a 102-PA July.
ref = mphi[mphi.game_year <= 2025]
sw_p = ref[ref.description.isin(K.SWINGS) & ref.bat_speed.notna()]
bp_p = ref[ref.type == 'X']
tests2 = [
    _welch(sw_p.bat_speed, sw_r.bat_speed, 'bat speed (mph, tracked swings)'),
    _welch(bp_p.launch_speed, bp_r.launch_speed, 'exit velocity (mph, tracked BIP)'),
    _welch(bp_p.launch_angle, bp_r.launch_angle, 'launch angle (deg, tracked BIP)'),
    _prop((bp_p.bb_type == 'popup').sum(), len(bp_p),
          (bp_r.bb_type == 'popup').sum(), len(bp_r), 'popup rate (of BIP)'),
    _prop((bp_p.launch_speed >= 95).sum(), len(bp_p),
          (bp_r.launch_speed >= 95).sum(), len(bp_r), 'hard-hit rate (of BIP)'),
    _prop((sw_p.bat_speed >= 75).sum(), len(sw_p),
          (sw_r.bat_speed >= 75).sum(), len(sw_r), 'fast-swing rate (of tracked swings)'),
]
for r_ in tests:
    r_['baseline'] = 'W2_july (102 PA)'
for r_ in tests2:
    r_['baseline'] = 'PHI 2023-25 norm (1,871 PA)'
    r_['n_july'], r_['july'] = r_['n_july'], r_['july']
tests = tests + tests2
st = pd.DataFrame(tests).rename(columns={'n_july': 'n_baseline', 'july': 'baseline_value'})
st['abs_z'] = st.z.abs()
st['band'] = np.where(st.abs_z >= 2.5, 'clearly beyond noise',
                      np.where(st.abs_z >= 1.5, 'suggestive', 'within noise'))
st = st[['baseline', 'measure', 'kind', 'n_baseline', 'n_recent', 'baseline_value',
         'recent', 'delta', 'se', 'z', 'abs_z', 'band']]
R(st.round(4), 'shift_tests_july_vs_recent')
print(st.round(3).to_string(index=False))
H['shift_tests'] = st.round(4).to_dict('records')


# ══════════════════════════════════════════════════════ DQ RECEIPTS ═══════
sec('DQ RECEIPTS')
bip_all = m[m.type == 'X']
bip26 = m26[m26.type == 'X']
dq = pd.DataFrame([
    ('R-1 entity lock', 'batter ids in frame', m.batter.nunique(), 1, 'PASS' if m.batter.nunique() == 1 else 'FAIL'),
    ('R-2 pitch-key uniqueness', 'duplicate (game_pk,ab,pitch)',
     int(m_all.duplicated(subset=['game_pk', 'at_bat_number', 'pitch_number']).sum()), 0,
     'PASS' if m_all.duplicated(subset=['game_pk', 'at_bat_number', 'pitch_number']).sum() == 0 else 'FAIL'),
    ('R-3 game_type purity', 'non-R rows in rate frame',
     int((m.game_type != 'R').sum()), 0, 'PASS' if (m.game_type != 'R').sum() == 0 else 'FAIL'),
    ('R-4 season coverage', 'seasons present', int(m.game_year.nunique()), 12,
     'PASS' if m.game_year.nunique() == 12 else 'FAIL'),
    ('R-5 freshness', 'max game_date', str(m26.game_date.max().date()), '>=2026-09-01',
     'PASS' if str(m26.game_date.max().date()) >= '2026-09-01' else 'WARN'),
    ('R-6 xwOBA grain (uc-pps-028)', 'non-null pitch rows == non-null PA rows',
     f'{_n_pitch_xw}=={_n_pa_xw}', 'equal', 'PASS' if _n_pitch_xw == _n_pa_xw else 'FAIL'),
    ('R-7 coordinate convention', 'RHB pulled-GB median loc_x', round(float(_med), 2), '< 0',
     'PASS' if _med < 0 else 'FAIL'),
    ('R-8 wOBA weights joined', 'seasons missing weights',
     int(sum(y not in w.Season.values for y in m.game_year.unique())), 0,
     'PASS' if all(y in w.Season.values for y in m.game_year.unique()) else 'FAIL'),
    ('R-9 completeness: events @ PA grain', 'null events on PA rows',
     int(K.pa_rows(m26).events.isna().sum()), 0,
     'PASS' if K.pa_rows(m26).events.isna().sum() == 0 else 'FAIL'),
    ('R-10 completeness: launch_speed @ tracked-BIP grain', 'null LS rate on 2026 BIP',
     round(float(bip26.launch_speed.isna().mean()), 4), '<0.02',
     'PASS' if bip26.launch_speed.isna().mean() < 0.02 else 'WARN'),
    ('R-11 completeness: zone', 'null zone rate 2026',
     round(float(m26.zone.isna().mean()), 4), '<0.02',
     'PASS' if m26.zone.isna().mean() < 0.02 else 'WARN'),
    ('R-12 completeness: hc_x/hc_y @ BIP grain', 'untraced BIP 2026',
     int((bip26.hc_x.isna() | bip26.hc_y.isna()).sum()), 0,
     'PASS' if (bip26.hc_x.isna() | bip26.hc_y.isna()).sum() == 0 else 'WARN'),
    ('R-13 sensor boundary: bat_speed', '2023 tracked swings (expect 0)',
     int(cb[cb.game_year == 2023].tracked_swings.iloc[0]), 0,
     'PASS' if cb[cb.game_year == 2023].tracked_swings.iloc[0] == 0 else 'FAIL'),
    ('R-14 sensor boundary: attack_angle', '2024 non-null (expect 0 - later sensor)',
     int(m[m.game_year == 2024].attack_angle.notna().sum()), 0,
     'PASS' if m[m.game_year == 2024].attack_angle.notna().sum() == 0 else 'WARN'),
    ('R-15 bat-tracking coverage stability', 'min coverage 2024-26',
     round(float(cb[cb.game_year >= 2024].tracking_coverage.min()), 3), '>0.85',
     'PASS' if cb[cb.game_year >= 2024].tracking_coverage.min() > 0.85 else 'WARN'),
    ('R-16 O-8 exposure', '2026 untracked BIP counted as not-hard-hit',
     int(len(bip26) - int(bip26.launch_speed.notna().sum())), 'report only', 'WARN'),
    ('R-17 PA floor: window', 'windows below 50 PA', int(win.below_floor.sum()), 0,
     'PASS' if win.below_floor.sum() == 0 else 'WARN'),
    ('R-18 PA floor: month', 'months below 50 PA', int(mon.below_floor.sum()), 'flagged',
     'WARN'),
    ('R-19 era derivation', '2021 shows both WSN and LAD',
     int(m[m.game_year == 2021].era.nunique()), 2,
     'PASS' if m[m.game_year == 2021].era.nunique() == 2 else 'FAIL'),
    ('R-20 schema asymmetry declared', 'PHI-only cols absent pre-2023',
     int(m[m.game_year < 2023].bat_speed.notna().sum()), 0,
     'PASS' if m[m.game_year < 2023].bat_speed.notna().sum() == 0 else 'FAIL'),
    ('R-21 parent reproduction', 'parent figures reproduced', f'{n_pass}/{len(rep)}',
     f'{len(rep)}/{len(rep)}', 'PASS' if n_pass == len(rep) else 'FAIL'),
    ('R-22 window partition', 'window PA sums to season PA',
     int(win.plate_apps.sum()), int(car.loc[car.game_year == 2026, 'plate_apps'].iloc[0]),
     'PASS' if win.plate_apps.sum() == car.loc[car.game_year == 2026, 'plate_apps'].iloc[0] else 'FAIL'),
    ('R-23 platoon partition', 'L+R PA sums to season PA',
     int(pls[pls.game_year == 2026].plate_apps.sum()),
     int(car.loc[car.game_year == 2026, 'plate_apps'].iloc[0]),
     'PASS' if pls[pls.game_year == 2026].plate_apps.sum() == car.loc[car.game_year == 2026, 'plate_apps'].iloc[0] else 'FAIL'),
    ('R-25 D-7/O-13 exposure', 'in_zone_rate vs in_zone_rate_fix, 2026',
     round(float(ca.loc[ca.game_year == 2026, 'in_zone_rate'].iloc[0]
                 - ca.loc[ca.game_year == 2026, 'in_zone_rate_fix'].iloc[0]), 4),
     'report only', 'WARN'),
    ('R-24 pool floor', 'pool rows below 50 PA', int((pool.plate_apps < 50).sum()), 0,
     'PASS' if (pool.plate_apps < 50).sum() == 0 else 'FAIL'),
], columns=['rule', 'measure', 'observed', 'expected', 'status'])
R(dq, 'dq_scorecard')
print(dq.to_string(index=False))
H['dq'] = {'pass': int((dq.status == 'PASS').sum()), 'warn': int((dq.status == 'WARN').sum()),
           'fail': int((dq.status == 'FAIL').sum())}
print(f"\nDQ: {H['dq']['pass']} PASS / {H['dq']['warn']} WARN / {H['dq']['fail']} FAIL")


# ══════════════════════════════════════════════════════════ FIGURES ═══════
sec('FIGURES')
import matplotlib                                              # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt                                # noqa: E402
from matplotlib.ticker import PercentFormatter                 # noqa: E402

# Palette: uc-pps-028 validated replacement (the repo PITCH_COLORS fail 2 of the
# dataviz six checks). Phillies navy/red retained for subject emphasis.
NAVY, RED, TEAL, AMBER, VIOLET = '#002D72', '#E81828', '#00919E', '#C97A00', '#8250C4'
GREY, LGREY = '#6B7280', '#D9DEE5'
plt.rcParams.update({'font.size': 9, 'axes.titlesize': 11, 'axes.titleweight': 'bold',
                     'axes.titlecolor': NAVY, 'axes.edgecolor': '#9AA3AF',
                     'figure.facecolor': 'white', 'axes.facecolor': 'white'})
FIG = lambda n: os.path.join(OUT, f'dp_uc40_fig{n}.png')


def _clean(ax, ylab=None):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', color=LGREY, lw=.8, alpha=.9)
    ax.set_axisbelow(True)
    if ylab:
        ax.set_ylabel(ylab)


# fig1 — career: what "good" looked like
c = car_out[car_out.plate_apps >= K.PA_FLOOR].copy()
fig, ax = plt.subplots(figsize=(10, 4.8))
xs = np.arange(len(c))
colors = [RED if y == 2026 else (LGREY if e != 'PHI' else '#AEB6C2')
          for y, e in zip(c.game_year, c.era)]
ax.bar(xs, c.ops, color=colors, width=.66)
for x, v, e in zip(xs, c.ops, c.era):
    ax.text(x, v + .012, f'{v:.3f}', ha='center', fontsize=8, color=NAVY)
    ax.text(x, .02, e, ha='center', fontsize=7.5, color='white', weight='bold')
ax2 = ax.twinx()
ax2.plot(xs, c.woba, color=NAVY, marker='o', lw=2, ms=4.5, label='wOBA')
ax2.plot(xs, c.xwoba, color=TEAL, marker='s', ls='--', lw=1.6, ms=4, label='xwOBA (per-PA)')
ax2.set_ylabel('wOBA / xwOBA'); ax2.spines[['top']].set_visible(False)
ax.set_xticks(xs); ax.set_xticklabels(c.game_year.astype(str))
ax.set_title('Trea Turner — 12 seasons of results. 2026 is the low-water mark of a qualified career')
_clean(ax, 'OPS')
h, l = ax2.get_legend_handles_labels()
ax2.legend(h, l, frameon=False, loc='upper right', ncol=2, fontsize=8.5)
fig.tight_layout(); fig.savefig(FIG(1), dpi=165); plt.close(fig)
print('  fig1 career')

# fig2 — RF-1 trajectory (PHI era) + RF-2 rolling form with the parent cut marked
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7.2),
                             gridspec_kw={'height_ratios': [1.05, 1]})
shade = {2023: '#C3C9D4', 2024: '#9AA3AF', 2025: '#4A5568'}
for yr, col in shade.items():
    s = run[run.game_year == yr]
    a1.plot(s.cum_pa, s.cum_woba, color=col, lw=1.7,
            label=f'{yr} (final {s.cum_woba.iloc[-1]:.3f})')
s26 = run[run.game_year == 2026]
a1.plot(s26.cum_pa, s26.cum_woba, color=RED, lw=3,
        label=f'2026 ({s26.cum_woba.iloc[-1]:.3f} to date)', zorder=5)
a1.scatter(s26.cum_pa.iloc[-1], s26.cum_woba.iloc[-1], color=RED, s=42, zorder=6)
par_pa = int(K.pa_rows(m26[m26.game_date <= K.PARENT_ASOF]).shape[0])
a1.axvline(par_pa, color=VIOLET, ls=':', lw=1.5)
a1.annotate('parent product published\n(2026-07-20, PA %d)' % par_pa, (par_pa - 6, .445),
            color=VIOLET, fontsize=8, ha='right', va='top')
a1.set_ylim(.20, .46); a1.set_xlabel('Cumulative plate appearances within season')
a1.set_title('RF-1 · season-to-date wOBA, Phillies era — 2026 never reaches the 2023–25 band')
_clean(a1, 'Season-to-date wOBA')
a1.legend(frameon=False, ncol=4, fontsize=8.5, loc='lower right')

a2.plot(roll.pa_idx, roll.roll_woba, color=RED, lw=2.4, label='trailing 100-PA wOBA')
a2.axhline(float(car_out.loc[car_out.game_year.between(2023, 2025), 'woba'].mean()),
           color=NAVY, ls='--', lw=1.2, label='2023–25 PHI norm')
imax = int(roll.roll_woba.idxmax())
a2.scatter(roll.pa_idx[imax], roll.roll_woba[imax], color=VIOLET, s=45, zorder=5)
a2.annotate(f'peak {roll.roll_woba[imax]:.3f} ({roll.game_date[imax].date()})',
            (roll.pa_idx[imax], roll.roll_woba[imax]), textcoords='offset points',
            xytext=(-10, -4), fontsize=8, color=VIOLET, ha='right', va='top')
a2.scatter(roll.pa_idx.iloc[-1], roll.roll_woba.iloc[-1], color=RED, s=45, zorder=5)
a2.annotate(f'now {roll.roll_woba.iloc[-1]:.3f}', (roll.pa_idx.iloc[-1], roll.roll_woba.iloc[-1]),
            textcoords='offset points', xytext=(-8, -16), fontsize=8, color=RED, ha='right')
a2.axvline(par_pa, color=VIOLET, ls=':', lw=1.5)
a2.set_xlabel('Plate appearance index, 2026')
a2.set_title('RF-2 · rolling form — the surge peaked the week the parent product shipped')
_clean(a2, 'Trailing 100-PA wOBA')
a2.legend(frameon=False, fontsize=8.5, loc='upper left')
fig.tight_layout(); fig.savefig(FIG(2), dpi=165); plt.close(fig)
print('  fig2 trajectory + rolling form')

# fig3 — mechanism: what moved between the windows
met = [('mean_ev', 'Exit velocity (mph)', 1),
       ('hard_hit_rate', 'Hard-hit %', 100), ('barrel_rate', 'Barrel %', 100),
       ('pu_rate', 'Popup % of BIP', 100), ('bat_speed_mu', 'Bat speed (mph)', 1),
       ('fast_swing_rate', 'Fast-swing % (>=75 mph)', 100), ('iso', 'ISO (points)', 1000),
       ('chase_rate', 'Chase %', 100), ('swing_rate_in_zone', 'In-zone swing %', 100),
       ('krate', 'Strikeout %', 100)]
fig, axes = plt.subplots(2, 5, figsize=(13.5, 5.6))
wv = win.set_index('window')
for ax, (col, lab, sc) in zip(axes.ravel(), met):
    vals = [wv.loc[k, col] * sc for k in WL]
    ax.plot([0, 1, 2], vals, color=GREY, lw=1.6, zorder=1)
    ax.scatter([0, 1, 2], vals, color=[NAVY, AMBER, RED], s=70, zorder=3)
    for i, v in enumerate(vals):
        ax.annotate(f'{v:.1f}' if sc != 1 or col == 'mean_ev' or col == 'bat_speed_mu'
                    else f'{v:.3f}', (i, v), textcoords='offset points',
                    xytext=(0, 9 if i != 1 else -16), ha='center', fontsize=8,
                    color=[NAVY, AMBER, RED][i])
    ax.set_title(lab, fontsize=9.5)
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(['Mar–Jun', 'Jul', 'Aug–Sep'], fontsize=8)
    ax.margins(y=.30, x=.22); _clean(ax)
fig.suptitle('The mechanism — decisions improved, contact quality collapsed  '
             '(Mar–Jun · July · Aug–Sep 2026)', color=NAVY, weight='bold', y=1.0)
fig.tight_layout(); fig.savefig(FIG(3), dpi=165); plt.close(fig)
print('  fig3 mechanism')

# fig4 — monthly OPS + bat speed
mo = mon.copy()
fig, ax = plt.subplots(figsize=(10, 4.6))
lab = {3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep'}
cols = [AMBER if mm == 7 else (RED if mm >= 8 else '#AEB6C2') for mm in mo.month]
bars = ax.bar([lab[x] for x in mo.month], mo.ops, color=cols, width=.62)
for b, v, pa, fl in zip(bars, mo.ops, mo.plate_apps, mo.below_floor):
    ax.text(b.get_x() + b.get_width() / 2, v + .014,
            f'{v:.3f}\n{int(pa)} PA' + (' ⚠' if fl else ''), ha='center', fontsize=8, color=NAVY)
ax.axhline(float(phi_ref.ops.iloc[0]), color=NAVY, ls='--', lw=1.3)
ax.text(6.35, float(phi_ref.ops.iloc[0]) + .012, f'2023–25 PHI norm {phi_ref.ops.iloc[0]:.3f}',
        color=NAVY, fontsize=8, ha='right')
ax2 = ax.twinx()
ax2.plot([lab[x] for x in mo.month], mo.bat_speed_mu, color=VIOLET, marker='D', lw=1.8, ms=5,
         label='avg bat speed (mph)')
ax2.set_ylabel('Bat speed (mph)'); ax2.spines[['top']].set_visible(False)
ax2.legend(frameon=False, loc='upper left', fontsize=8.5)
ax.set_ylim(0, max(mo.ops) * 1.30)
ax.set_title('2026 by month — one good month, and a bat that slowed down after it')
_clean(ax, 'OPS')
fig.tight_layout(); fig.savefig(FIG(4), dpi=165); plt.close(fig)
print('  fig4 monthly')

# fig5 — platoon
fig, (b1, b2) = plt.subplots(1, 2, figsize=(12.4, 4.6), gridspec_kw={'width_ratios': [1.45, 1]})
ps = pls[(pls.game_year >= 2016) & (~pls.below_floor)]
for hand, col, mk in [('L', VIOLET, 'o'), ('R', TEAL, 's')]:
    s = ps[ps.p_throws == hand]
    b1.plot(s.game_year.astype(str), s.ops, color=col, marker=mk, lw=2, ms=5,
            label=f'vs {hand}HP')
b1.axvspan(9.5, 10.5, color=RED, alpha=.07)
b1.set_title('Platoon by season — the left-handed edge is gone')
_clean(b1, 'OPS'); b1.legend(frameon=False, ncol=2, fontsize=9)
pw = plw.set_index(['window', 'p_throws'])
x = np.arange(3); wd = .36
for i, (hand, col) in enumerate([('L', VIOLET), ('R', TEAL)]):
    vals = [pw.loc[(k, hand), 'ops'] for k in WL]
    fl = [pw.loc[(k, hand), 'below_floor'] for k in WL]
    bb = b2.bar(x + (i - .5) * wd, vals, wd, color=col, label=f'vs {hand}HP')
    for r, v, f_ in zip(bb, vals, fl):
        b2.text(r.get_x() + r.get_width() / 2, v + .015,
                f'{v:.3f}' + ('⚠' if f_ else ''), ha='center', fontsize=7.5, color=NAVY)
b2.set_xticks(x); b2.set_xticklabels(['Mar–Jun', 'Jul', 'Aug–Sep'])
b2.set_title('…and 2026 splits by window (⚠ = under 50 PA)')
_clean(b2, 'OPS'); b2.legend(frameon=False, ncol=2, fontsize=9)
fig.tight_layout(); fig.savefig(FIG(5), dpi=165); plt.close(fig)
print('  fig5 platoon')

# fig6 — pitch groups
fig, (c1, c2) = plt.subplots(1, 2, figsize=(12.4, 4.6))
gg = pgw[pgw.pitch_group.isin(['fastball', 'breaking', 'offspeed'])]
x = np.arange(3); wd = .26
for i, (win_lab, col) in enumerate(zip(WL, [NAVY, AMBER, RED])):
    s = gg[gg.window == win_lab].set_index('pitch_group').reindex(
        ['fastball', 'breaking', 'offspeed'])
    bb = c1.bar(x + (i - 1) * wd, s.woba.values, wd, color=col,
                label=win_lab.split(' ')[0])
    for r, v, f_ in zip(bb, s.woba.values, s.below_floor.values):
        if pd.notna(v):
            c1.text(r.get_x() + r.get_width() / 2, v + .008,
                    f'{v:.3f}' + ('⚠' if f_ else ''), ha='center', fontsize=7, color=NAVY,
                    rotation=90, va='bottom')
c1.set_xticks(x); c1.set_xticklabels(['Fastball', 'Breaking', 'Offspeed'])
c1.set_ylim(0, .62)
c1.set_title('wOBA by pitch group and window (⚠ = under 50 PA)')
_clean(c1, 'wOBA'); c1.legend(frameon=False, ncol=3, fontsize=8.5)
pt = pts.sort_values('woba')
GCOL = {'fastball': TEAL, 'breaking': RED, 'offspeed': AMBER, 'other': GREY}
cc2 = [GCOL.get(K.PITCH_GROUP.get(t_, 'other'), GREY) for t_ in pt.pitch_type]
c2.barh(pt.pitch_type, pt.woba, color=cc2)
from matplotlib.patches import Patch                            # noqa: E402
c2.legend(handles=[Patch(color=GCOL[g], label=g) for g in ('fastball', 'breaking', 'offspeed')],
          frameon=False, ncol=3, fontsize=8.5, loc='lower right')
for i, (v, wr, n, fl) in enumerate(zip(pt.woba, pt.whiff_rate, pt.pitches, pt.below_floor)):
    c2.text(v + .006, i, f'{v:.3f}  ·  whiff {wr*100:.0f}%  ·  {int(n)} p'
            + ('  ⚠' if fl else ''), va='center', fontsize=8, color=NAVY)
c2.set_xlim(0, .72)
c2.set_title('2026 by pitch type — the sweeper is the hole')
_clean(c2); c2.set_xlabel('wOBA')
fig.tight_layout(); fig.savefig(FIG(6), dpi=165); plt.close(fig)
print('  fig6 pitch groups')


# ═══════════════════════════════════════════════════════ HEADLINES ════════
H['generated'] = pd.Timestamp.now().isoformat(timespec='seconds')
H['subject'] = {'name': K.SUBJECT, 'mlbam': K.SUBJECT_MLBAM}
H['windows'] = WL
H['parent'] = {'uc': 'uc-pos-006-turner-2026-offense-001', 'build': 'dp_uc24',
               'as_of': K.PARENT_ASOF, 'delivered': '2026-07-21'}
def _keys(o):
    if isinstance(o, dict):
        return {str(k): _keys(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_keys(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if pd.isna(o) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if o is pd.NA:
        return None
    return o


with open(P('headlines.json'), 'w', encoding='utf-8') as f:
    json.dump(_keys(H), f, indent=1, default=str)
print(f'\n  wrote headlines.json  ({len(H)} top-level keys)')
sec('BUILD COMPLETE')
