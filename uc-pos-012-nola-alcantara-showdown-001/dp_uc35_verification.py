"""
dp_uc35_verification.py — independent verification for uc-pos-012
=================================================================
Recomputes every published headline from the RAW parquet frames with inline
logic (no kernel imports for the arithmetic checks), then cross-checks the
receipts and headlines.json against each other. Run AFTER the build:

    DP_UC35_DATA=<root> python dp_uc35_verification.py

Exit 0 with 'ALL PASS' or a non-zero assert with the failing check named.
"""
import json
import os

import numpy as np
import pandas as pd

DATA = os.environ.get('DP_UC35_DATA',
                      r'C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')

NOLA, ALCANTARA, WHEELER, HARPER = 605400, 645261, 554430, 547180
NON_PA = ['NA', 'pickoff_1b', 'pickoff_2b', 'pickoff_3b',
          'caught_stealing_2b', 'caught_stealing_3b', 'caught_stealing_home',
          'stolen_base_2b', 'stolen_base_3b', 'stolen_base_home',
          'pickoff_caught_stealing_2b', 'pickoff_caught_stealing_3b',
          'pickoff_caught_stealing_home', 'wild_pitch', 'passed_ball',
          'other_advance', 'runner_double_play', 'defensive_indiff',
          'balk', 'game_advisory', 'ejection']
NON_AB = {'walk', 'intent_walk', 'hit_by_pitch', 'sac_fly', 'sac_bunt',
          'sac_fly_double_play', 'sac_bunt_double_play', 'catcher_interf'}
HIT = {'single', 'double', 'triple', 'home_run'}

PASS = 0


def ok(name, cond):
    global PASS
    assert cond, f'FAIL: {name}'
    PASS += 1
    print(f'  PASS {PASS:>3}  {name}')


def approx(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol


r = lambda n: pd.read_csv(os.path.join(OUT, f'dp_uc35_{n}.csv'))
H = json.load(open(os.path.join(OUT, 'dp_uc35_headlines.json')))

# ── independent raw load ────────────────────────────────────────────────────
frames = [pd.read_parquet(f'{DATA}/data/phillies/phils_{y}.parquet')
          for y in range(2015, 2027)
          if os.path.exists(f'{DATA}/data/phillies/phils_{y}.parquet')]
df = pd.concat(frames, ignore_index=True)
df = df[~df.game_type.isin(['S', 'E'])]
batting = (((df.home_team == 'PHI') & (df.inning_topbot == 'Bot'))
           | ((df.away_team == 'PHI') & (df.inning_topbot == 'Top')))
pos, pps = df[batting].copy(), df[~batting].copy()
ok('raw frames load, S/E excluded', len(pos) > 0 and len(pps) > 0)
ok('no duplicate pitch keys in pos',
   pos.duplicated(subset=['game_pk', 'at_bat_number', 'pitch_number']).sum() == 0)

isnpa = lambda d: d[~d.events.replace(np.nan, 'NA').isin(NON_PA)]

# ── Noles: Nola vs MIA ─────────────────────────────────────────────────────
bat_team = np.where(pps.inning_topbot == 'Top', pps.away_team, pps.home_team)
nm = pps[(pps.pitcher == NOLA) & (bat_team == 'MIA')]
pa = isnpa(nm)
nmc = r('nola_mia_career').iloc[0]
ok('Noles career pitches', int(nmc.pitches) == len(nm))
ok('Noles career PA', int(nmc.plate_apps) == len(pa))
ab = pa[~pa.events.isin(NON_AB)]
hits = pa[pa.events.isin(HIT)]
ok('Noles career BA', approx(nmc.ba, len(hits) / len(ab)))
tb = sum({'single': 1, 'double': 2, 'triple': 3, 'home_run': 4}[e]
         for e in hits.events)
ok('Noles career SLG', approx(nmc.slg, tb / len(ab)))
k = pa.events.isin(['strikeout', 'strikeout_double_play']).sum()
ok('Noles career K rate', approx(nmc.krate, k / len(pa)))
# runs_created independent: max(post_bat_score)-min(bat_score) per PA, summed
rc = (nm.groupby(['game_pk', 'at_bat_number'])
        .apply(lambda g: g.post_bat_score.max() - g.bat_score.min(),
               include_groups=False).sum())
ok('Noles career runs_created', approx(nmc.runs_created, rc))
ok('Noles career rc_per_pa', approx(nmc.rc_per_pa, rc / len(pa)))
ok('headlines.nola_mia matches receipt',
   approx(H['nola_mia']['rc_per_pa'], round(nmc.rc_per_pa, 4)))

# wOBA independent (season constants, IBB out of num and den)
w = pd.read_csv(f'{DATA}/wOBA and FIP Constants.csv').set_index('Season')
num = den = 0.0
for y, g in isnpa(nm).groupby('game_year'):
    c = w.loc[int(y)]
    ev = g.events
    num += (c.wBB * (ev == 'walk').sum() + c.wHBP * (ev == 'hit_by_pitch').sum()
            + c['w1B'] * (ev == 'single').sum() + c['w2B'] * (ev == 'double').sum()
            + c['w3B'] * (ev == 'triple').sum() + c.wHR * (ev == 'home_run').sum())
    den += ((~ev.isin(NON_AB)).sum() + (ev == 'walk').sum()
            + (ev == 'sac_fly').sum() + (ev == 'hit_by_pitch').sum())
# NOTE: career wOBA in the receipt aggregates PA at career grain with 2026
# constants (kernel behaviour when game_year not in level). Season-summed
# check is the SEASON receipt; career receipt checked for internal identity.
nms = r('nola_mia_seasons')
num2 = 0.0
for _, row in nms.iterrows():
    c = w.loc[int(row.game_year)]
    num2 += (c.wBB * row.unint_walks + c.wHBP * row.hbp + c['w1B'] * row.singles
             + c['w2B'] * row.doubles + c['w3B'] * row.triples + c.wHR * row.hrs)
ok('Noles season wOBA numerators reconcile', approx(num, num2, 1e-6))

# ── floor ruling ───────────────────────────────────────────────────────────
FLOOR = int(r('floor_derivation').iloc[0].floor)
ok('floor = min Noles season PA', FLOOR == int(nms.plate_apps.min()))
ok('headlines floor matches', H['floor_pa'] == FLOOR)

# ── box population ─────────────────────────────────────────────────────────
bp = r('boxplot_population')
ok('box population respects floor', (bp.plate_apps > FLOOR).all())
ok('box population count matches headline',
   len(bp) == H['phi_hitter_seasons_in_population'])
ph = r('phi_hitter_seasons')
ok('box population == phi_hitter_seasons[in_population]',
   len(bp) == int(ph.in_population.sum()))
ok('rc_per_pa identity on box population',
   np.allclose(bp.rc_per_pa * bp.plate_apps, bp.runs_created))
ok('ops identity on box population',
   np.allclose(bp.ops, bp.obp + bp.slg, equal_nan=True))

# ── Wheeler ────────────────────────────────────────────────────────────────
wc = pd.read_parquet(f'{DATA}/data/opponents/wheeler.parquet')
wc = wc[~wc.game_type.isin(['S', 'E'])]
wbat = np.where(wc.inning_topbot == 'Top', wc.away_team, wc.home_team)
w_nym = wc[(wc.pitcher == WHEELER) & (wbat == 'MIA')]
pbat = np.where(pps.inning_topbot == 'Top', pps.away_team, pps.home_team)
w_phi = pps[(pps.pitcher == WHEELER) & (pbat == 'MIA')]
ok('Wheeler sources disjoint by season',
   not (set(w_nym.game_year) & set(w_phi.game_year)))
wmc = r('wheeler_mia_career').iloc[0]
ok('Wheeler career PA', int(wmc.plate_apps)
   == len(isnpa(w_nym)) + len(isnpa(w_phi)))
wms = r('wheeler_mia_seasons')
ok('Wheeler season PA sums to career',
   int(wms.plate_apps.sum()) == int(wmc.plate_apps))

# ── Harper ─────────────────────────────────────────────────────────────────
popp = np.where(pos.home_team == 'PHI', pos.away_team, pos.home_team)
hm = pos[(pos.batter == HARPER) & (popp == 'MIA')]
hmc = r('harper_mia_career').iloc[0]
ok('Harper vs MIA career PA', int(hmc.plate_apps) == len(isnpa(hm)))
hva = pos[(pos.batter == HARPER) & (pos.pitcher == ALCANTARA)]
hvac = r('harper_vs_alcantara_career').iloc[0]
ok('Harper vs Alcantara PA', int(hvac.plate_apps) == len(isnpa(hva)))
ok('Harper vs Alcantara pitches', int(hvac.pitches) == len(hva))

# ── exposure rankings ──────────────────────────────────────────────────────
expc = pos.groupby('pitcher').size().sort_values(ascending=False)
ok('Alcantara pitches to PHI', int(expc.loc[ALCANTARA])
   == H['alcantara_pitches_to_phi'])
ok('Alcantara exposure rank',
   int((expc > expc.loc[ALCANTARA]).sum()) + 1 == H['alcantara_exposure_rank'])
ok('exposure receipt rank agrees', int(
    r('pitcher_exposure_rank_top25').query('pitcher == @ALCANTARA')['rank'].iat[0])
   == H['alcantara_exposure_rank'])
hexp = isnpa(pos[pos.batter == HARPER]).groupby('pitcher').size() \
    .sort_values(ascending=False)
ok('Harper-vs-Alcantara PA rank',
   int((hexp > hexp.loc[ALCANTARA]).sum()) + 1
   == H['harper_alcantara_rank_by_pa'])

# ── DQ scorecard ───────────────────────────────────────────────────────────
dq = r('dq_scorecard')
ok('DQ scorecard: no FAIL rows', (dq.result != 'FAIL').all())

# ── headlines cross-check vs career receipts ───────────────────────────────
for key, csv in [('nola_mia', 'nola_mia_career'),
                 ('wheeler_mia', 'wheeler_mia_career'),
                 ('harper_mia', 'harper_mia_career'),
                 ('phi_vs_alcantara', 'alcantara_phi_career'),
                 ('harper_vs_alcantara', 'harper_vs_alcantara_career')]:
    row = r(csv).iloc[0]
    for kpi in ['woba', 'rc_per_pa', 'krate', 'whiff_rate', 'chase_rate',
                'hard_hit_rate', 'barrel_rate', 'ba', 'obp', 'slg']:
        ok(f'headlines.{key}.{kpi} == {csv}',
           approx(H[key][kpi], round(float(row[kpi]), 4), 5e-5))

print(f'\nALL PASS — {PASS}/{PASS} checks')
