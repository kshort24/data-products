"""
dp_uc40_verification.py — INDEPENDENT verification harness for uc-pos-014
=========================================================================
Contract (UC11 / uc-pos-013 precedent): this file must not import the build's
KPI kernel for anything it verifies. It re-reads the parquet, re-derives every
published number with hand-rolled boolean masks, and compares against (a) the
CSV receipts the build wrote and (b) the figures quoted in the report.

A check may fail for three reasons and all three are useful:
  * the build is wrong          -> fix the build
  * the verification is wrong   -> fix the verification, record the disposition
  * the two differ by method    -> record a method-variance disposition in 05

Run:  DP_UC40_DATA=<MLB repo> python dp_uc40_verification.py
"""
from __future__ import annotations

import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
DATA = os.environ.get('DP_UC40_DATA',
                      r'C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB')
TREA = 607208
TOL = 5e-4

_res = []


def chk(name, got, want, tol=TOL):
    if isinstance(want, str) or isinstance(got, str) or isinstance(want, bool):
        ok = got == want
    elif want is None or (isinstance(want, float) and np.isnan(want)):
        ok = got is None or (isinstance(got, float) and np.isnan(got))
    else:
        ok = abs(float(got) - float(want)) <= tol
    _res.append((name, got, want, ok))
    return ok


# ─────────────────────────────────────────── independent data acquisition ──
def read_raw():
    """Deliberately NOT the kernel loader: different filter order, different
    batting-side derivation (uses `inning_topbot` against the away side)."""
    fr = []
    o = pd.read_parquet(f'{DATA}/data/opponents/turner.parquet')
    fr.append(o[o.batter == TREA])
    for y in (2023, 2024, 2025, 2026):
        d = pd.read_parquet(f'{DATA}/data/phillies/phils_{y}.parquet')
        away_bat = (d.away_team == 'PHI') & (d.inning_topbot == 'Top')
        home_bat = (d.home_team == 'PHI') & (d.inning_topbot == 'Bot')
        fr.append(d[(away_bat | home_bat) & (d.batter == TREA)])
    a = pd.concat(fr, ignore_index=True)
    a = a[~a.game_type.isin(['S', 'E'])]
    a = a.drop_duplicates(subset=['game_pk', 'at_bat_number', 'pitch_number'])
    a['game_date'] = pd.to_datetime(a.game_date)
    return a


RAW = read_raw()
R = RAW[RAW.game_type == 'R'].copy()
R26 = R[R.game_year == 2026].copy()
WTS = pd.read_csv(f'{DATA}/wOBA and FIP Constants.csv').set_index('Season')

NON_PA = {'NA', 'pickoff_1b', 'pickoff_2b', 'pickoff_3b', 'caught_stealing_2b',
          'caught_stealing_3b', 'caught_stealing_home', 'stolen_base_2b',
          'stolen_base_3b', 'stolen_base_home', 'pickoff_caught_stealing_2b',
          'pickoff_caught_stealing_3b', 'pickoff_caught_stealing_home',
          'wild_pitch', 'passed_ball', 'other_advance', 'runner_double_play',
          'defensive_indiff', 'balk', 'game_advisory', 'ejection'}
NON_AB = {'walk', 'intent_walk', 'hit_by_pitch', 'sac_fly', 'sac_bunt',
          'sac_fly_double_play', 'sac_bunt_double_play', 'catcher_interf'}
HITS = {'single', 'double', 'triple', 'home_run'}
SWINGS = {'foul', 'foul_bunt', 'foul_tip', 'hit_into_play', 'missed_bunt',
          'swinging_pitchout', 'swinging_strike', 'swinging_strike_blocked'}
WHIFFS = {'foul_tip', 'missed_bunt', 'swinging_pitchout', 'swinging_strike',
          'swinging_strike_blocked'}


def line(df, year=None):
    """Hand-rolled slash line + wOBA. No kernel, no groupby-merge chain."""
    e = df.events.fillna('NA')
    pa = df[~e.isin(NON_PA)]
    ev = pa.events
    ab = int((~ev.isin(NON_AB)).sum())
    h = int(ev.isin(HITS).sum())
    s1 = int((ev == 'single').sum()); s2 = int((ev == 'double').sum())
    s3 = int((ev == 'triple').sum()); hr = int((ev == 'home_run').sum())
    ubb = int((ev == 'walk').sum()); ibb = int((ev == 'intent_walk').sum())
    hbp = int((ev == 'hit_by_pitch').sum()); sf = int((ev == 'sac_fly').sum())
    k = int(ev.isin({'strikeout', 'strikeout_double_play'}).sum())
    tb = s1 + 2 * s2 + 3 * s3 + 4 * hr
    y = int(year if year is not None else pa.game_year.mode().iat[0])
    c = WTS.loc[y]
    wn = (c.wBB * ubb + c.wHBP * hbp + c['w1B'] * s1 + c['w2B'] * s2
          + c['w3B'] * s3 + c.wHR * hr)
    wd = ab + ubb + sf + hbp
    obpd = ab + ubb + ibb + hbp + sf
    babd = ab - k - hr + sf
    return dict(pa=len(pa), ab=ab, h=h, hr=hr, bb=ubb + ibb, k=k,
                ba=h / ab, obp=(h + ubb + ibb + hbp) / obpd, slg=tb / ab,
                ops=(h + ubb + ibb + hbp) / obpd + tb / ab,
                iso=tb / ab - h / ab, woba=wn / wd,
                krate=k / len(pa), bbrate=(ubb + ibb) / len(pa),
                babip=(h - hr) / babd)


def approach(df):
    sw = df.description.isin(SWINGS)
    wh = df.description.isin(WHIFFS)
    iz = df.zone < 10
    ooz = df.zone > 9
    fp = df.pitch_number == 1
    return dict(pitches=len(df), swing_rate=sw.mean(),
                whiff_rate=wh[sw].sum() / sw.sum(),
                chase_rate=sw[ooz].sum() / ooz.sum(),
                z_swing=sw[iz].sum() / iz.sum(),
                z_whiff=(sw & wh)[iz].sum() / (sw & iz).sum(),
                ooz_whiff=(sw & wh)[ooz].sum() / (sw & ooz).sum(),
                in_zone_rate=iz.sum() / (iz.sum() + ooz.sum()) if (iz.sum() + ooz.sum()) else np.nan,
                srfp=sw[fp].sum() / fp.sum(),
                fpsr=(fp.sum() - (df[fp].type == 'B').sum()) / fp.sum())


def contact(df):
    b = df[df.type == 'X']
    tr = b[b.launch_speed.notna() & b.launch_angle.notna()]
    return dict(bip=len(b), tracked=len(tr), ev=tr.launch_speed.mean(),
                la=tr.launch_angle.mean(),
                hard=(b.launch_speed >= 95).sum() / len(b),
                barrel=(b.launch_speed_angle == 6).sum() / len(b),
                gb=(b.bb_type == 'ground_ball').sum() / len(b),
                fb=(b.bb_type == 'fly_ball').sum() / len(b),
                ld=(b.bb_type == 'line_drive').sum() / len(b),
                pu=(b.bb_type == 'popup').sum() / len(b),
                xwobacon=b.estimated_woba_using_speedangle.mean())


# ═════════════════════════════ 1 · FRAME-LEVEL / DQ ═══════════════════════
chk('frame: single batter id', int(RAW.batter.nunique()), 1)
chk('frame: no duplicate pitch keys',
    int(RAW.duplicated(subset=['game_pk', 'at_bat_number', 'pitch_number']).sum()), 0)
chk('frame: 12 seasons present', int(R.game_year.nunique()), 12)
chk('frame: 2026 R pitch rows', int(len(R26)), 2276)
chk('frame: 2026 games', int(R26.game_pk.nunique()), 135)
chk('frame: max game_date', str(R26.game_date.max().date()), '2026-09-02')
chk('frame: min 2026 game_date', str(R26.game_date.min().date()), '2026-03-26')
chk('frame: no spring/exhibition rows', int(RAW.game_type.isin(['S', 'E']).sum()), 0)
chk('frame: postseason rows excluded from R', int((R.game_type != 'R').sum()), 0)
chk('frame: 2021 shows two batting teams',
    int(R[R.game_year == 2021].apply(
        lambda r: r.away_team if r.inning_topbot == 'Top' else r.home_team,
        axis=1).nunique()), 2)
chk('sensor boundary: no bat_speed before 2023',
    int(R[R.game_year < 2023].get('bat_speed', pd.Series(dtype=float)).notna().sum()), 0)
chk('sensor boundary: no bat_speed in 2023',
    int(R[R.game_year == 2023].bat_speed.notna().sum()), 0)
chk('sensor boundary: no attack_angle in 2024',
    int(R[R.game_year == 2024].attack_angle.notna().sum()), 0)
chk('xwOBA is per-PA (non-null pitch rows == non-null PA rows)',
    int(R26.estimated_woba_using_speedangle.notna().sum()),
    int(R26[~R26.events.fillna('NA').isin(NON_PA)]
        .estimated_woba_using_speedangle.notna().sum()))
chk('2026 untracked BIP (O-8 exposure)',
    int((R26[R26.type == 'X'].launch_speed.isna()).sum()), 0)
chk('2026 untraced BIP hc_x/hc_y',
    int((R26[R26.type == 'X'].hc_x.isna() | R26[R26.type == 'X'].hc_y.isna()).sum()), 0)

# ═════════════════════════════ 2 · SEASON PANEL ═══════════════════════════
car = pd.read_csv(os.path.join(OUT, 'dp_uc40_career_by_season.csv')).set_index('game_year')
for y in range(2015, 2027):
    L = line(R[R.game_year == y], y)
    for k_, col in [('pa', 'plate_apps'), ('ab', 'at_bats'), ('h', 'hits'),
                    ('hr', 'hrs'), ('k', 'strikeouts'), ('ba', 'ba'),
                    ('obp', 'obp'), ('slg', 'slg'), ('ops', 'ops'),
                    ('woba', 'woba'), ('iso', 'iso'), ('babip', 'babip'),
                    ('krate', 'krate'), ('bbrate', 'bbrate')]:
        chk(f'season {y} {col}', L[k_], car.loc[y, col])

# contact + approach panels, PHI era only (keeps the check list proportionate)
cc = pd.read_csv(os.path.join(OUT, 'dp_uc40_career_contact.csv')).set_index('game_year')
ca = pd.read_csv(os.path.join(OUT, 'dp_uc40_career_approach.csv')).set_index('game_year')
for y in (2020, 2021, 2023, 2024, 2025, 2026):
    C = contact(R[R.game_year == y]); A = approach(R[R.game_year == y])
    chk(f'season {y} bip', C['bip'], cc.loc[y, 'bips'])
    chk(f'season {y} mean_ev', C['ev'], cc.loc[y, 'mean_ev'])
    chk(f'season {y} mean_la', C['la'], cc.loc[y, 'mean_la'])
    chk(f'season {y} hard_hit_rate', C['hard'], cc.loc[y, 'hard_hit_rate'])
    chk(f'season {y} barrel_rate', C['barrel'], cc.loc[y, 'barrel_rate'])
    chk(f'season {y} pu_rate', C['pu'], cc.loc[y, 'pu_rate'])
    chk(f'season {y} xwobacon', C['xwobacon'], cc.loc[y, 'xwobacon_bip'])
    chk(f'season {y} swing_rate', A['swing_rate'], ca.loc[y, 'swing_rate'])
    chk(f'season {y} whiff_rate', A['whiff_rate'], ca.loc[y, 'whiff_rate'])
    chk(f'season {y} chase_rate', A['chase_rate'], ca.loc[y, 'chase_rate'])
    chk(f'season {y} z_swing', A['z_swing'], ca.loc[y, 'swing_rate_in_zone'])
    chk(f'season {y} z_whiff', A['z_whiff'], ca.loc[y, 'whiff_rate_in_zone'])
    chk(f'season {y} in_zone_rate_fix (D-7 corrected)', A['in_zone_rate'],
        ca.loc[y, 'in_zone_rate_fix'])
    chk(f'season {y} D-7 exposure == zone_null_rate',
        float(R[R.game_year == y].zone.isna().mean()), ca.loc[y, 'zone_null_rate'])
    chk(f'season {y} srfp', A['srfp'], ca.loc[y, 'srfp'])
    chk(f'season {y} fpsr', A['fpsr'], ca.loc[y, 'fpsr'])

# ═════════════════════════════ 3 · WINDOWS ═══════════════════════════════
W1 = R26[R26.game_date < '2026-07-01']
W2 = R26[(R26.game_date >= '2026-07-01') & (R26.game_date < '2026-08-01')]
W3 = R26[R26.game_date >= '2026-08-01']
win = pd.read_csv(os.path.join(OUT, 'dp_uc40_window_split.csv'))
win['k'] = win.window.str[:2]
win = win.set_index('k')
chk('windows partition 2026 exactly', int(len(W1) + len(W2) + len(W3)), int(len(R26)))
for key, sub in [('W1', W1), ('W2', W2), ('W3', W3)]:
    L = line(sub, 2026); C = contact(sub); A = approach(sub)
    for k_, col in [('pa', 'plate_apps'), ('ba', 'ba'), ('obp', 'obp'), ('slg', 'slg'),
                    ('ops', 'ops'), ('woba', 'woba'), ('iso', 'iso'), ('babip', 'babip'),
                    ('krate', 'krate'), ('bbrate', 'bbrate'), ('hr', 'hrs')]:
        chk(f'{key} {col}', L[k_], win.loc[key, col])
    for k_, col in [('bip', 'bips'), ('ev', 'mean_ev'), ('la', 'mean_la'),
                    ('hard', 'hard_hit_rate'), ('barrel', 'barrel_rate'),
                    ('pu', 'pu_rate'), ('gb', 'gb_rate'), ('fb', 'fb_rate'),
                    ('ld', 'ld_rate'), ('xwobacon', 'xwobacon_bip')]:
        chk(f'{key} {col}', C[k_], win.loc[key, col])
    for k_, col in [('swing_rate', 'swing_rate'), ('whiff_rate', 'whiff_rate'),
                    ('chase_rate', 'chase_rate'), ('z_swing', 'swing_rate_in_zone'),
                    ('z_whiff', 'whiff_rate_in_zone'), ('ooz_whiff', 'ooz_whiff_rate'),
                    ('srfp', 'srfp'), ('fpsr', 'fpsr')]:
        chk(f'{key} {col}', A[k_], win.loc[key, col])
    chk(f'{key} in_zone_rate_fix (D-7 corrected)', A['in_zone_rate'],
        win.loc[key, 'in_zone_rate_fix'])
    chk(f'{key} zone_null_rate', float(sub.zone.isna().mean()), win.loc[key, 'zone_null_rate'])
    bt = sub[sub.description.isin(SWINGS) & sub.bat_speed.notna()]
    chk(f'{key} bat_speed_mu', bt.bat_speed.mean(), win.loc[key, 'bat_speed_mu'])
    chk(f'{key} fast_swing_rate', (bt.bat_speed >= 75).mean(), win.loc[key, 'fast_swing_rate'])
    chk(f'{key} tracked_swings', int(len(bt)), win.loc[key, 'tracked_swings'])

# ═════════════════════════════ 4 · MONTHLY ═══════════════════════════════
mon = pd.read_csv(os.path.join(OUT, 'dp_uc40_monthly_master.csv')).set_index('month')
for mm in range(3, 10):
    sub = R26[R26.game_date.dt.month == mm]
    L = line(sub, 2026)
    chk(f'month {mm} plate_apps', L['pa'], mon.loc[mm, 'plate_apps'])
    chk(f'month {mm} ops', L['ops'], mon.loc[mm, 'ops'])
    chk(f'month {mm} woba', L['woba'], mon.loc[mm, 'woba'])
    chk(f'month {mm} krate', L['krate'], mon.loc[mm, 'krate'])
    chk(f'month {mm} below_floor', bool(L['pa'] < 50), bool(mon.loc[mm, 'below_floor']))

# ═════════════════════════════ 5 · PLATOON ═══════════════════════════════
pls = pd.read_csv(os.path.join(OUT, 'dp_uc40_platoon_season.csv'))
pls = pls.set_index(['game_year', 'p_throws'])
for y in (2020, 2021, 2022, 2023, 2024, 2025, 2026):
    for hand in ('L', 'R'):
        L = line(R[(R.game_year == y) & (R.p_throws == hand)], y)
        chk(f'platoon {y} {hand} pa', L['pa'], pls.loc[(y, hand), 'plate_apps'])
        chk(f'platoon {y} {hand} ops', L['ops'], pls.loc[(y, hand), 'ops'])
        chk(f'platoon {y} {hand} woba', L['woba'], pls.loc[(y, hand), 'woba'])
        chk(f'platoon {y} {hand} krate', L['krate'], pls.loc[(y, hand), 'krate'])
plw = pd.read_csv(os.path.join(OUT, 'dp_uc40_platoon_window.csv'))
plw['k'] = plw.window.str[:2]
plw = plw.set_index(['k', 'p_throws'])
for key, sub in [('W1', W1), ('W2', W2), ('W3', W3)]:
    for hand in ('L', 'R'):
        s = sub[sub.p_throws == hand]
        L = line(s, 2026)
        chk(f'platoon {key} {hand} pa', L['pa'], plw.loc[(key, hand), 'plate_apps'])
        chk(f'platoon {key} {hand} ops', L['ops'], plw.loc[(key, hand), 'ops'])
        chk(f'platoon {key} {hand} woba', L['woba'], plw.loc[(key, hand), 'woba'])
        chk(f'platoon {key} {hand} below_floor', bool(L['pa'] < 50),
            bool(plw.loc[(key, hand), 'below_floor']))
chk('W3 vs RHP mean EV (report §7)',
    W3[(W3.p_throws == 'R') & (W3.type == 'X')].launch_speed.mean(), 83.86, tol=.006)
# platoon exposure shares
for key, sub, want in [('W1', W1, None), ('W2', W2, None), ('W3', W3, None)]:
    pa = sub[~sub.events.fillna('NA').isin(NON_PA)]
    sh = (pa.p_throws == 'L').mean()
    exp = pd.read_csv(os.path.join(OUT, 'dp_uc40_platoon_exposure_window.csv'))
    exp['k'] = exp.window.str[:2]
    chk(f'exposure {key} LHP share',
        sh, float(exp[(exp.k == key) & (exp.p_throws == 'L')].share.iloc[0]))

# ═════════════════════════════ 6 · PITCH GROUPS / TYPES ══════════════════
PG = {'FF': 'fastball', 'SI': 'fastball', 'FC': 'fastball', 'SL': 'breaking',
      'ST': 'breaking', 'CU': 'breaking', 'KC': 'breaking', 'SV': 'breaking',
      'CS': 'breaking', 'CH': 'offspeed', 'FS': 'offspeed', 'FO': 'offspeed',
      'SC': 'offspeed', 'KN': 'offspeed'}
pgw = pd.read_csv(os.path.join(OUT, 'dp_uc40_pitch_group_window.csv'))
pgw['k'] = pgw.window.str[:2]
pgw = pgw.set_index(['k', 'pitch_group'])
for key, sub in [('W1', W1), ('W2', W2), ('W3', W3)]:
    g = sub.assign(pg=sub.pitch_type.map(PG).fillna('other'))
    for grp in ('fastball', 'breaking', 'offspeed'):
        s = g[g.pg == grp]
        if not len(s):
            continue
        L = line(s, 2026); A = approach(s)
        chk(f'pg {key} {grp} pitches', len(s), pgw.loc[(key, grp), 'pitches'])
        chk(f'pg {key} {grp} usage', len(s) / len(sub), pgw.loc[(key, grp), 'usage'])
        chk(f'pg {key} {grp} pa', L['pa'], pgw.loc[(key, grp), 'plate_apps'])
        chk(f'pg {key} {grp} ba', L['ba'], pgw.loc[(key, grp), 'ba'])
        chk(f'pg {key} {grp} slg', L['slg'], pgw.loc[(key, grp), 'slg'])
        chk(f'pg {key} {grp} woba', L['woba'], pgw.loc[(key, grp), 'woba'])
        chk(f'pg {key} {grp} whiff', A['whiff_rate'], pgw.loc[(key, grp), 'whiff_rate'])
pts = pd.read_csv(os.path.join(OUT, 'dp_uc40_pitch_type_2026.csv')).set_index('pitch_type')
for pt in pts.index:
    s = R26[R26.pitch_type == pt]
    L = line(s, 2026); A = approach(s)
    chk(f'pt {pt} pitches', len(s), pts.loc[pt, 'pitches'])
    chk(f'pt {pt} woba', L['woba'], pts.loc[pt, 'woba'])
    chk(f'pt {pt} whiff', A['whiff_rate'], pts.loc[pt, 'whiff_rate'])
chk('report §7: ST+SL share of all 2026 pitches',
    int((R26.pitch_type.isin(['ST', 'SL'])).sum()) / len(R26), 0.278, tol=.0006)
chk('report §7: ST+SL pitch count', int((R26.pitch_type.isin(['ST', 'SL'])).sum()), 632)

# ═════════════════════════════ 7 · BREAKPOINT SCAN ═══════════════════════
scan = pd.read_csv(os.path.join(OUT, 'dp_uc40_breakpoint_scan.csv')).set_index('breakpoint')
for bp in scan.index:
    pre = R26[R26.game_date < bp]; post = R26[R26.game_date >= bp]
    Lp, Lq = line(pre, 2026), line(post, 2026)
    chk(f'scan {bp} pre_pa', Lp['pa'], scan.loc[bp, 'pre_pa'])
    chk(f'scan {bp} post_pa', Lq['pa'], scan.loc[bp, 'post_pa'])
    chk(f'scan {bp} d_ops', Lq['ops'] - Lp['ops'], scan.loc[bp, 'd_ops'])
    chk(f'scan {bp} d_woba', Lq['woba'] - Lp['woba'], scan.loc[bp, 'd_woba'])
chk('report §3 claim: sign flips at 2026-07-21 (first negative cut)',
    str(scan[scan.d_ops < 0].index.min()), '2026-07-21')
chk('report §3 claim: all cuts before 07-21 positive',
    bool((scan[scan.index < '2026-07-21'].d_ops > 0).all()), True)
chk('report §3 claim: all cuts from 07-21 negative',
    bool((scan[scan.index >= '2026-07-21'].d_ops < 0).all()), True)
chk('report §3 claim: monotone worsening from 07-21',
    bool(scan[scan.index >= '2026-07-21'].d_ops.is_monotonic_decreasing), True)

# ═════════════════════════════ 8 · PARENT REPRODUCTION ═══════════════════
rep = pd.read_csv(os.path.join(OUT, 'dp_uc40_parent_reproduction.csv'))
chk('parent repro: all checks pass', int((~rep.repro_pass).sum()), 0)
chk('parent repro: check count', int(len(rep)), 84)
chk('parent repro: zero definitional drift on 2026',
    float(rep[rep.season == 2026].definition_delta.abs().max()), 0.0, tol=5e-5)
# independent recomputation of the parent's headline July figure
par = R26[R26.game_date <= '2026-07-20']
jul = par[par.game_date.dt.month == 7]
e = jul.events.fillna('NA'); pa_j = jul[~e.isin(NON_PA)]
ab_j = int((~pa_j.events.isin(NON_AB)).sum())
h_j = int(pa_j.events.isin(HITS).sum())
tb_j = int(pa_j.events.map({'single': 1, 'double': 2, 'triple': 3, 'home_run': 4}).fillna(0).sum())
bb_j = int(pa_j.events.isin({'walk', 'intent_walk'}).sum())
hbp_j = int((pa_j.events == 'hit_by_pitch').sum())
chk("parent's July PA (as of 07-20)", len(pa_j), 62)
chk("parent's July BA", h_j / ab_j, .304, tol=.0006)
chk("parent's July SLG", tb_j / ab_j, .625, tol=.0006)
chk("parent's July OBP (parent definition: /PA)",
    (h_j + bb_j + hbp_j) / len(pa_j), .355, tol=.0006)
chk("parent's July OPS (parent definition)",
    (h_j + bb_j + hbp_j) / len(pa_j) + tb_j / ab_j, .980, tol=.0011)

# ═════════════════════════════ 9 · RF-1 / RF-2 ═══════════════════════════
roll = pd.read_csv(os.path.join(OUT, 'dp_uc40_rolling_form.csv'))
roll['game_date'] = pd.to_datetime(roll.game_date)
chk('RF-2 peak wOBA', float(roll.roll_woba.max()), .4212, tol=.0006)
chk('RF-2 peak date', str(roll.loc[roll.roll_woba.idxmax(), 'game_date'].date()), '2026-07-21')
chk('RF-2 last wOBA', float(roll.roll_woba.iloc[-1]), .2385, tol=.0011)
chk('RF-2 peak-to-now drop (report §3: 183 pts)',
    round((roll.roll_woba.max() - roll.roll_woba.iloc[-1]) * 1000), 183, tol=1)
run = pd.read_csv(os.path.join(OUT, 'dp_uc40_running_line.csv'))
for y in (2023, 2024, 2025, 2026):
    s = run[run.game_year == y]
    L = line(R[R.game_year == y], y)
    chk(f'RF-1 {y} final cum_woba == season woba', float(s.cum_woba.iloc[-1]), L['woba'])
    chk(f'RF-1 {y} final cum_pa == season PA', int(s.cum_pa.iloc[-1]), L['pa'])
chk('RF-1 2026 never reaches 2023-25 band after PA 100',
    bool(run[(run.game_year == 2026) & (run.cum_pa >= 100)].cum_woba.max() < 0.3320), True)

# ═════════════════════════════ 10 · AD-1 / ST-1 ══════════════════════════
ad = pd.read_csv(os.path.join(OUT, 'dp_uc40_approach_differential_season.csv')).set_index('game_year')
for y in (2021, 2023, 2024, 2025, 2026):
    A = approach(R[R.game_year == y])
    chk(f'AD-1 {y}', A['z_swing'] - A['chase_rate'], ad.loc[y, 'approach_differential'])
q = ad[~ad.below_floor]
chk('AD-1 2026 rank among 11 qualified (2 = 2nd lowest)',
    int(q.approach_differential.rank().loc[2026]), 2)
st = pd.read_csv(os.path.join(OUT, 'dp_uc40_shift_tests_july_vs_recent.csv'))
norm = st[st.baseline.str.startswith('PHI')].set_index('measure')
pop_z = float(norm.loc['popup rate (of BIP)', 'z'])
chk('ST-1 popup z vs PHI norm', pop_z, 4.119, tol=.006)
chk('ST-1 popup is the only measure clearing |z|>=2.5 vs the PHI norm',
    int((norm.z.abs() >= 2.5).sum()), 1)
chk('ST-1 bat speed vs PHI norm is within noise',
    bool(abs(float(norm.loc['bat speed (mph, tracked swings)', 'z'])) < 1.5), True)

# ═════════════════════════════ 11 · POOL / PERCENTILES ═══════════════════
pool = pd.read_csv(os.path.join(OUT, 'dp_uc40_population_pool.csv'))
chk('pool: hitter-seasons', int(len(pool)), 220)
chk('pool: distinct players', int(pool.batter.nunique()), 100)
chk('pool: none below the 50-PA floor', int((pool.plate_apps < 50).sum()), 0)
pct = pd.read_csv(os.path.join(OUT, 'dp_uc40_profile_percentiles.csv')).set_index('metric')
for mt in ('ops', 'woba', 'slg', 'iso'):
    v = float(pct.loc[mt, 'turner_2026_season'])
    chk(f'pctile {mt} season recomputed',
        float((pool[mt].dropna() < v).mean() * 100), float(pct.loc[mt, 'pctile_season']))
chk('report §4: W3 popup rate percentile',
    float(pct.loc['pu_rate', 'pctile_W3_as_a_season']), 97.727, tol=.006)
chk('report §4: W3 popup would be 5th-highest of the 220 pool seasons',
    int((pool.pu_rate.dropna() >= float(pct.loc['pu_rate', 'turner_2026_W3_recent'])).sum()), 5)
chk('D-7/O-13 exposure: 2026 published minus corrected in_zone_rate',
    round(float(ca.loc[2026, 'in_zone_rate'] - ca.loc[2026, 'in_zone_rate_fix']), 4), 0.0009)

# ═════════════════════════════ 12 · REPORT SUPERLATIVES (G8) ═════════════
qual = car[car.plate_apps >= 50]
chk('G8 cohort: 11 qualified seasons', int(len(qual)), 11)
for mt in ('ba', 'obp', 'slg', 'ops', 'iso', 'woba', 'babip'):
    chk(f'G8: 2026 is the lowest qualified season in {mt}',
        int((qual[mt] < qual.loc[2026, mt]).sum()) + 1, 1)
plq = pls.reset_index()
plq = plq[~plq.below_floor]
chk('G8: 2026 vs RHP is the lowest qualified RHP season',
    int((plq[(plq.p_throws == 'R')].ops < plq[(plq.p_throws == 'R') & (plq.game_year == 2026)].ops.iloc[0]).sum()) + 1, 1)
chk('G8: 2026 vs LHP is the lowest qualified LHP season (by <0.0003)',
    int((plq[(plq.p_throws == 'L')].ops < plq[(plq.p_throws == 'L') & (plq.game_year == 2026)].ops.iloc[0]).sum()) + 1, 1)
chk('report §1: 2023 and 2026 K% within 0.001',
    bool(abs(car.loc[2023, 'krate'] - car.loc[2026, 'krate']) < 0.001), True)
chk('report §2: August is the best K% month above the 50-PA floor',
    int(mon[(mon.plate_apps >= 50)].krate.idxmin()), 8)
chk('report §6: breaking usage rises across the three windows',
    bool(pgw.loc[('W1', 'breaking'), 'usage'] < pgw.loc[('W2', 'breaking'), 'usage']
         < pgw.loc[('W3', 'breaking'), 'usage']), True)
chk('report §6: W3 fastball slg', float(pgw.loc[('W3', 'fastball'), 'slg']), .231, tol=.0006)
cf = pd.read_csv(os.path.join(OUT, 'dp_uc40_platoon_counterfactual.csv'))
chk('PL-1: |mix effect| on wOBA into W3 < 0.003',
    bool(cf[(cf.metric == 'woba') & (cf.to_label.str.startswith('W3'))].mix_effect.abs().max() < .003), True)

# ═════════════════════════════ 13 · REPORT TEXT SCAN ═════════════════════
rpt = open(os.path.join(HERE, 'dp_uc40_turner_recency_report.md'), encoding='utf-8').read()
for tok, why in [('.207/.279/.276', 'W3 slash'), ('.239/.292/.376', 'season slash'),
                 ('.630', 'vs LHP OPS'), ('.686', 'vs RHP OPS'),
                 ('15.2%', 'W3 popup rate'), ('4.12', 'popup z'),
                 ('97.7th percentile', 'popup percentile'), ('84', 'parent repro count'),
                 ('2026-07-21', 'peak/flip date'), ('.421', 'RF-2 peak'),
                 ('.238', 'RF-2 now'), ('.345', 'AD-1 2026'),
                 ('D-7 / O-13', 'new defect disclosure'),
                 ('fifth-highest', 'popup pool rank'), ('44.8%', 'D-7-corrected zone rate')]:
    chk(f'report mentions {why} ({tok})', tok in rpt, True)
chk('report carries no un-cohorted "career worst"',
    bool(re.search(r'career worst(?! )', rpt) is None), True)
chk('report discloses the 50-PA floor', '50-PA floor' in rpt, True)
chk('report discloses causation limit', 'causation is not identified' in rpt.lower()
    or 'Direction of causation is not identified' in rpt, True)

# ═════════════════════════════ REPORT ════════════════════════════════════
res = pd.DataFrame(_res, columns=['check', 'got', 'want', 'pass'])
res.to_csv(os.path.join(OUT, 'dp_uc40_verification_results.csv'), index=False)
npass, ntot = int(res['pass'].sum()), len(res)
print(f'\nVERIFICATION: {npass}/{ntot} PASS')
if npass != ntot:
    print('\nFAILURES:')
    print(res[~res['pass']].to_string(index=False))
    sys.exit(1)
print('all checks pass')
