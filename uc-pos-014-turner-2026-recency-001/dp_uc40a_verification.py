"""
dp_uc40a_verification.py — INDEPENDENT harness for the uc-pos-014 v1.1.0 addendum
=================================================================================
Same contract as `dp_uc40_verification.py`: re-read the parquet, re-derive every
published bat-path number with hand-rolled masks, import nothing from the
addendum kernel for anything it verifies, and check that the report's SENTENCES
are entitled to the numbers.

Run:  DP_UC40_DATA=<MLB repo> python dp_uc40a_verification.py
"""
from __future__ import annotations

import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
DATA = os.environ.get('DP_UC40_DATA',
                      r'C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB')
T = 607208
TOL = 5e-4
_res = []


def chk(name, got, want, tol=TOL):
    if isinstance(want, (str, bool)) or isinstance(got, (str, bool)):
        ok = got == want
    elif want is None or (isinstance(want, float) and np.isnan(want)):
        ok = got is None or (isinstance(got, float) and np.isnan(got))
    else:
        ok = abs(float(got) - float(want)) <= tol
    _res.append((name, got, want, ok))


SW = {'foul', 'foul_bunt', 'foul_tip', 'hit_into_play', 'missed_bunt',
      'swinging_pitchout', 'swinging_strike', 'swinging_strike_blocked'}
BUNT = {'foul_bunt', 'missed_bunt'}
PG = {'FF': 'fastball', 'SI': 'fastball', 'FC': 'fastball', 'SL': 'breaking',
      'ST': 'breaking', 'CU': 'breaking', 'KC': 'breaking', 'SV': 'breaking',
      'CS': 'breaking', 'CH': 'offspeed', 'FS': 'offspeed', 'FO': 'offspeed',
      'SC': 'offspeed', 'KN': 'offspeed'}
SIDE, DEPTH = ('intercept_ball_minus_batter_pos_x_inches',
               'intercept_ball_minus_batter_pos_y_inches')


def read():
    """Independent load: different column-availability handling, different
    batting-side derivation order."""
    import pyarrow.parquet as pq
    fr = []
    for y in range(2023, 2027):
        p = f'{DATA}/data/phillies/phils_{y}.parquet'
        d = pd.read_parquet(p)
        for c in ('attack_angle', 'attack_direction', 'swing_path_tilt', SIDE, DEPTH,
                  'bat_speed', 'swing_length', 'hyper_speed'):
            if c not in d.columns:
                d[c] = np.nan
        home = (d.home_team == 'PHI') & (d.inning_topbot == 'Bot')
        away = (d.away_team == 'PHI') & (d.inning_topbot == 'Top')
        fr.append(d[home | away])
    a = pd.concat(fr, ignore_index=True)
    a = a[a.game_type == 'R'].copy()
    a['pg'] = a.pitch_type.map(PG).fillna('other')
    a['game_date'] = pd.to_datetime(a.game_date)
    return a


A = read()
SUB = A[A.batter == T].copy()


def path_pop(d):
    """BP-0 re-implemented: swings, minus bunts, minus degenerate (<25 mph)."""
    s = d[d.description.isin(SW) & ~d.description.isin(BUNT)]
    return s[s.attack_angle.notna() & ~(s.bat_speed.notna() & (s.bat_speed < 25))]


# ─────────────────────────────────── 1 · SENSOR BOUNDARIES / COVERAGE ─────
for y in (2023, 2024):
    chk(f'sensor: no attack_angle in {y}',
        int(SUB[SUB.game_year == y].attack_angle.notna().sum()), 0)
chk('sensor: no bat_speed in 2023', int(SUB[SUB.game_year == 2023].bat_speed.notna().sum()), 0)
chk('sensor: bat_speed present in 2024', bool(SUB[SUB.game_year == 2024].bat_speed.notna().sum() > 0), True)
cov = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_coverage.csv'))
cov = cov[cov.population == 'Trea Turner'].set_index('season')
for y in (2025, 2026):
    d = SUB[SUB.game_year == y]
    sw = d[d.description.isin(SW)]
    chk(f'coverage {y}: swings', int(len(sw)), int(cov.loc[y, 'swings']))
    chk(f'coverage {y}: tracked', int(d.attack_angle.notna().sum()), int(cov.loc[y, 'path_tracked']))
    chk(f'coverage {y}: rate', d.attack_angle.notna().sum() / len(sw), cov.loc[y, 'path_coverage'])
    chk(f'coverage {y}: bunts excluded',
        int(sw.description.isin(BUNT).sum()), int(cov.loc[y, 'bunts_excluded']))

# ─────────────────────────────────── 2 · CONVENTION ASSERTIONS ────────────
conv = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_convention_assertions.csv'))
chk('conventions: all pass', int((conv.status != 'PASS').sum()), 0)
chk('conventions: check count', int(len(conv)), 12)
P = A[(A.game_year >= 2025)]
sw = path_pop(P).copy()
sw['inside'] = np.where(sw.stand == 'R', -sw.plate_x, sw.plate_x)
for st in ('R', 'L'):
    s = sw[sw.stand == st]
    chk(f'C1-{st} side axis corr recomputed', s[SIDE].corr(s.inside),
        float(conv[conv.check == f'C1-{st}'].value.iloc[0]))
chk('C2 depth axis corr recomputed', sw[DEPTH].corr(sw.release_speed),
    float(conv[conv.check == 'C2'].value.iloc[0]))
b = sw[(sw.type == 'X') & sw.hc_x.notna() & (sw.launch_speed >= 95)
       & sw.bb_type.isin(['line_drive', 'fly_ball'])].copy()
spray = np.degrees(np.arctan2(b.hc_x - 125.42, 198.27 - b.hc_y))
b['pull_spray'] = np.where(b.stand == 'R', -spray, spray)
chk('C4 attack_direction sign corr recomputed', b.attack_direction.corr(b.pull_spray),
    float(conv[conv.check == 'C4'].value.iloc[0]))
chk('O-15: attack_direction is pull-NEGATIVE (corr < 0)',
    bool(b.attack_direction.corr(b.pull_spray) < 0), True)
for st in ('R', 'L'):
    s = b[b.stand == st]
    chk(f'C5 stand-normalised: sign is negative for {st}',
        bool(s.attack_direction.corr(s.pull_spray) < 0), True)
h = P[P.description.isin(SW)]
h = h[h.hyper_speed.notna() & h.launch_speed.notna()]
chk('O-17: hyper_speed == max(launch_speed, 88)',
    float(np.isclose(h.hyper_speed, np.maximum(h.launch_speed, 88)).mean()), 1.0)
chk('O-18: every tilt-gate disagreement is a bunt or a sub-25mph swing',
    bool(all((r.description in BUNT) or (pd.notna(r.bat_speed) and r.bat_speed < 25)
             for _, r in P[P.description.isin(SW)].pipe(
                 lambda d: d[d.swing_path_tilt.notna() != d.attack_angle.notna()]).iterrows())), True)

# ─────────────────────────────────── 3 · SUBJECT PANELS ───────────────────
ss = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_subject_by_season.csv')).set_index('game_year')
MET = ['attack_angle', 'attack_direction', 'swing_path_tilt', 'bat_speed', 'swing_length']
for y in (2025, 2026):
    t = path_pop(SUB[SUB.game_year == y])
    chk(f'BP-1 {y} tracked_swings', int(len(t)), int(ss.loc[y, 'tracked_swings']))
    for m in MET:
        chk(f'BP-1 {y} {m}', t[m].mean(), ss.loc[y, m])
    chk(f'BP-1 {y} intercept_side_in', t[SIDE].mean(), ss.loc[y, 'intercept_side_in'])
    chk(f'BP-1 {y} intercept_depth_in', t[DEPTH].mean(), ss.loc[y, 'intercept_depth_in'])
    chk(f'BP-1 {y} pull_direction is the negated column',
        -t.attack_direction.mean(), ss.loc[y, 'pull_direction'])
    chk(f'BP-1 {y} ideal_aa_rate (5-20 deg)',
        float(t.attack_angle.between(5, 20).mean()), ss.loc[y, 'ideal_aa_rate'])

sg = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_subject_by_pitch_group.csv'))
sg = sg.set_index(['game_year', 'pitch_group'])
for y in (2025, 2026):
    for g in ('fastball', 'breaking', 'offspeed'):
        t = path_pop(SUB[(SUB.game_year == y) & (SUB.pg == g)])
        chk(f'BP-2 {y}/{g} tracked', int(len(t)), int(sg.loc[(y, g), 'tracked_swings']))
        for m in ('attack_angle', 'swing_path_tilt', 'bat_speed'):
            chk(f'BP-2 {y}/{g} {m}', t[m].mean(), sg.loc[(y, g), m])
        chk(f'BP-2 {y}/{g} intercept_side_in', t[SIDE].mean(), sg.loc[(y, g), 'intercept_side_in'])

# ─────────────────────────────────── 4 · POPUP RATES ──────────────────────
pr = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_popup_rate_by_pitch_group.csv'))
pr = pr.set_index(['game_year', 'pitch_group'])
for y in range(2023, 2027):
    for g in ('fastball', 'breaking', 'offspeed'):
        bip = SUB[(SUB.game_year == y) & (SUB.pg == g) & (SUB.type == 'X')]
        chk(f'PU-2 {y}/{g} bip', int(len(bip)), int(pr.loc[(y, g), 'bip']))
        chk(f'PU-2 {y}/{g} popups', int((bip.bb_type == 'popup').sum()),
            int(pr.loc[(y, g), 'popups']))
        chk(f'PU-2 {y}/{g} pu_rate', float((bip.bb_type == 'popup').mean()),
            pr.loc[(y, g), 'pu_rate'])
rec = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_v1_reconciliation.csv'))
chk('PU-2 reconciles with the v1.0.0 popup rate', float(rec.delta.max()) < 1e-9, True)
chk('report claim: breaking popups roughly tripled 2025 -> 2026',
    bool(pr.loc[(2026, 'breaking'), 'pu_rate'] / pr.loc[(2025, 'breaking'), 'pu_rate'] > 2.8), True)
chk('report claim: fastball popup rate is flat',
    bool(abs(pr.loc[(2026, 'fastball'), 'pu_rate'] - pr.loc[(2025, 'fastball'), 'pu_rate']) < .01), True)

# ─────────────────────────────────── 5 · PEER CONTROL (PB-1) ──────────────
head = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_peer_delta.csv')).set_index('metric')
tp = path_pop(A[A.game_year.isin([2025, 2026])])
for metric, col in [('swing_path_tilt', 'swing_path_tilt'), ('attack_angle', 'attack_angle'),
                    ('bat_speed', 'bat_speed'), ('intercept_side_in', SIDE),
                    ('intercept_depth_in', DEPTH)]:
    g = tp.groupby(['batter', 'game_year'])[col].agg(['size', 'mean']).reset_index()
    p = g.pivot(index='batter', columns='game_year')
    p.columns = [f'{a_}_{b_}' for a_, b_ in p.columns]
    p = p[(p.size_2025 >= 200) & (p.size_2026 >= 200)]
    d = p.mean_2026 - p.mean_2025
    chk(f'PB-1 {metric} cohort size', int(len(p)), int(head.loc[metric, 'cohort_n']))
    chk(f'PB-1 {metric} subject delta', float(d.loc[T]), head.loc[metric, 'subject_delta'])
    chk(f'PB-1 {metric} peer median delta', float(d.median()), head.loc[metric, 'peer_median_delta'])
    chk(f'PB-1 {metric} peer-netted delta', float(d.loc[T] - d.median()),
        head.loc[metric, 'peer_netted_delta'])
chk('report claim: tilt drop is the largest in the cohort',
    int(head.loc['swing_path_tilt', 'subject_rank_most_negative']), 1)
chk('report claim: contact-side increase is the largest in the cohort',
    int(head.loc['intercept_side_in', 'subject_rank_most_negative']),
    int(head.loc['intercept_side_in', 'cohort_n']))
chk('report claim: bat speed went UP, not down',
    bool(head.loc['bat_speed', 'subject_delta'] > 0), True)
chk('report claim: attack angle change is small once peer-netted',
    bool(abs(head.loc['attack_angle', 'peer_netted_delta']) < 0.5), True)
chk('O-16: the peer median tilt delta is itself materially negative',
    bool(head.loc['swing_path_tilt', 'peer_median_delta'] < -0.5), True)

# ─────────────────────────────────── 6 · POPULATION PLACEMENT ─────────────
pct = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_population_percentiles.csv')).set_index('metric')
pool = path_pop(A[A.game_year == 2026]).groupby('batter').agg(
    n=('attack_angle', 'size'), tilt=('swing_path_tilt', 'mean'),
    side=(SIDE, 'mean'), aa=('attack_angle', 'mean'), bs=('bat_speed', 'mean'))
pool = pool[pool.n >= 200]
chk('pool size (200+ tracked swings, 2026)', int(len(pool)), int(pct.pool_n.iloc[0]))
chk('pool: Turner tilt', float(pool.loc[T, 'tilt']), pct.loc['swing_path_tilt', 'turner_2026'])
chk('report claim: Turner has the flattest plane in the pool',
    float(pool.tilt.min()), float(pool.loc[T, 'tilt']))
chk('report claim: tilt percentile is 0', float(pct.loc['swing_path_tilt', 'pctile']), 0.0)
chk('pool: contact-side percentile', float((pool.side < pool.loc[T, 'side']).mean() * 100),
    pct.loc['intercept_side_in', 'pctile'])

# ─────────────────────────────────── 7 · BREAKING POPUP POOL ──────────────
bh = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_breaking_popup_headline.csv')).set_index('season')
bb = A[(A.pg == 'breaking') & (A.type == 'X')]
for y in (2025, 2026):
    g = bb[bb.game_year == y].groupby('batter').agg(
        bip=('bb_type', 'size'), pu=('bb_type', lambda s: (s == 'popup').sum()))
    g = g[g.bip >= 40]
    g['rate'] = g.pu / g.bip
    chk(f'breaking pool {y}: qualifiers', int(len(g)), int(bh.loc[y, 'qualifiers']))
    chk(f'breaking pool {y}: median', float(g.rate.median()), bh.loc[y, 'pool_median'])
    chk(f'breaking pool {y}: subject rate', float(g.loc[T, 'rate']), bh.loc[y, 'subject_rate'])
    chk(f'breaking pool {y}: subject rank',
        int((g.rate > g.loc[T, 'rate']).sum()) + 1, int(bh.loc[y, 'subject_rank']))
chk('report claim: 2026 subject is rank 1 of the breaking-ball popup pool',
    int(bh.loc[2026, 'subject_rank']), 1)
chk('report claim: 2025 subject sat at the peer median',
    bool(abs(bh.loc[2025, 'subject_minus_median']) < .005), True)
chk('report claim: the peer median itself roughly doubled',
    bool(bh.loc[2026, 'pool_median'] / bh.loc[2025, 'pool_median'] > 1.7), True)

# ─────────────────────────────────── 8 · POPUP SIGNATURE ──────────────────
ps = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_popup_signature_season.csv'))
ps = ps.set_index(['game_year', 'is_popup'])
t26 = path_pop(SUB[SUB.game_year == 2026])
t26 = t26[t26.type == 'X']
for flag in (False, True):
    s = t26[(t26.bb_type == 'popup') == flag]
    chk(f'PU-1 2026 popup={flag} n', int(len(s)), int(ps.loc[(2026, flag), 'n']))
    chk(f'PU-1 2026 popup={flag} attack_angle', s.attack_angle.mean(),
        ps.loc[(2026, flag), 'attack_angle'])
    chk(f'PU-1 2026 popup={flag} tilt', s.swing_path_tilt.mean(),
        ps.loc[(2026, flag), 'swing_path_tilt'])
    chk(f'PU-1 2026 popup={flag} side', s[SIDE].mean(), ps.loc[(2026, flag), 'intercept_side_in'])
    chk(f'PU-1 2026 popup={flag} depth', s[DEPTH].mean(), ps.loc[(2026, flag), 'intercept_depth_in'])
    chk(f'PU-1 2026 popup={flag} bat_speed', s.bat_speed.mean(), ps.loc[(2026, flag), 'bat_speed'])
chk('report claim: popups come with a STEEPER attack angle',
    bool(ps.loc[(2026, True), 'attack_angle'] > ps.loc[(2026, False), 'attack_angle'] + 2), True)
chk('report claim: popups are met CLOSER to the body',
    bool(ps.loc[(2026, True), 'intercept_side_in'] < ps.loc[(2026, False), 'intercept_side_in']), True)
chk('report claim: popups are met FURTHER out front',
    bool(ps.loc[(2026, True), 'intercept_depth_in'] > ps.loc[(2026, False), 'intercept_depth_in']), True)
chk('report claim: popups are NOT a bat-speed story',
    bool(abs(ps.loc[(2026, True), 'bat_speed'] - ps.loc[(2026, False), 'bat_speed']) < 1.0), True)

# ─────────────────────────────────── 9 · REPORT TEXT SCAN ─────────────────
rpt = open(os.path.join(HERE, 'dp_uc40a_bat_path_report.md'), encoding='utf-8').read()
for tok, why in [('O-15', 'inverted attack_direction convention'),
                 ('O-16', 'team-wide tilt drift'), ('O-17', 'hyper_speed identity'),
                 ('O-18', 'bunt / degenerate swing exclusion'),
                 ('25.5', 'flattest plane'), ('12.1%', 'breaking popup rate'),
                 ('peer-netted', 'the O-16 control'),
                 ('no causation is identified', 'causation limit'),
                 ('2025 only', 'sensor boundary')]:
    chk(f'report discloses {why}', tok in rpt, True)
chk('report does not claim a bat-speed collapse on popups',
    bool(re.search(r'63\.6', rpt) is None or 'killed the story' in rpt), True)
chk('report carries the ungoverned-population correction note', 'killed the story' in rpt, True)

res = pd.DataFrame(_res, columns=['check', 'got', 'want', 'pass'])
res.to_csv(os.path.join(OUT, 'dp_uc40a_verification_results.csv'), index=False)
p_, t_ = int(res['pass'].sum()), len(res)
print(f'\nADDENDUM VERIFICATION: {p_}/{t_} PASS')
if p_ != t_:
    print(res[~res['pass']].to_string(index=False))
    sys.exit(1)
print('all checks pass')
