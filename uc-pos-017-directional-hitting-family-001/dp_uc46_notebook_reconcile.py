"""Gate 7 reconciliation -- the PATCHED NOTEBOOK cells vs the certified module.

Executes the notebook's own new code cells against real data and asserts their
output is identical to dp_uc46_kernel's. This is the obligation nobody held for
cell 56, which is why it shipped broken while three kernels transcribed it.
"""
import json, sys, glob
import numpy as np, pandas as pd
sys.path.insert(0,'/home/claude/build/pkg'); import dp_uc46_kernel as k

nb = json.load(open('/mnt/user-data/uploads/MLB/Baseball Functions.ipynb', encoding='utf-8'))
cells = nb['cells']
src = lambda i: ''.join(cells[i]['source'])
i_par = next(i for i,c in enumerate(cells) if c['cell_type']=='code' and 'def pull_air_rate' in src(i))
i_fam = next(i for i,c in enumerate(cells) if c['cell_type']=='code' and 'def direction_rate' in src(i))

NS = {'np': np, 'pd': pd}
exec(src(i_fam), NS)          # the guidebook's directional family cell
exec(src(i_par), NS)          # the guidebook's patched pull_air_rate cell
print(f'executed notebook cells {i_fam} and {i_par} -- no exception')
defined = sorted(n for n,v in NS.items() if callable(v) and getattr(v,'__module__',None)=='builtins' or
                 (callable(v) and n not in ('np','pd') and not n.startswith('_')))
print('notebook now defines:', [n for n in defined if n in
      ('classifiable_bip','derive_loc','hit_direction','assert_spray_convention',
       'build_bip','direction_rate','bb_type_profile','pull_air_rate')])

fs = sorted(glob.glob('/mnt/user-data/uploads/MLB/data/phillies/phils_*.parquet'))
df = pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True)
pos = df[((df.home_team=='PHI')&(df.inning_topbot=='Bot'))|
         ((df.away_team=='PHI')&(df.inning_topbot=='Top'))]
pos = pos[pos.game_type=='R']

G = []
def eq(name, a, b):
    a = a.sort_index(axis=1).reset_index(drop=True); b = b.sort_index(axis=1).reset_index(drop=True)
    ok = a.shape == b.shape and list(a.columns)==list(b.columns)
    if ok:
        try: pd.testing.assert_frame_equal(a, b, check_dtype=False); 
        except AssertionError as e: ok=False; print('   ', str(e).split(chr(10))[0])
    G.append((name, ok)); print(f'  [{"PASS" if ok else "FAIL"}] {name}')

print('\n--- notebook vs module, identical output required ---')
nb_bip = NS['build_bip'](['game_year'], pos)
km_bip = k.build_bip(['game_year'], pos)
eq('build_bip frame', nb_bip[['loc_x','loc_y','hit_direction']], km_bip[['loc_x','loc_y','hit_direction']])
for lvl in (['game_year'], ['game_year','stand'], ['player_name','game_year']):
    eq(f'direction_rate{lvl}', NS['direction_rate'](lvl, nb_bip), k.direction_rate(lvl, km_bip))
eq('bb_type_profile[game_year]', NS['bb_type_profile'](['game_year'], nb_bip),
   k.bb_type_profile(['game_year'], km_bip))
eq('bb_type_profile[game_year,hit_direction]',
   NS['bb_type_profile'](['game_year','hit_direction'], nb_bip),
   k.bb_type_profile(['game_year','hit_direction'], km_bip))
eq('pull_air_rate[game_year]', NS['pull_air_rate'](['game_year'], nb_bip),
   k.pull_air_rate(['game_year'], km_bip))

# and the headline the report publishes, computed from the NOTEBOOK
r = NS['direction_rate'](['game_year'], nb_bip)
r26 = r[r.game_year==2026].iloc[0]
print(f"\nnotebook 2026: pull {r26.pull_rate*100:.1f}% straight {r26.straight_rate*100:.1f}% "
      f"oppo {r26.oppo_rate*100:.1f}%  (report says 45.7 / 24.5 / 29.8)")
p = NS['bb_type_profile'](['game_year','hit_direction'], nb_bip)
o = p[(p.game_year==2026)&(p.hit_direction=='Oppo')&(p.bb_type=='line_drive')].iloc[0]
print(f"notebook 2026 oppo_ld_rate: {o.share*100:.2f}%  (report says 25.17%)")

n=sum(1 for _,ok in G if ok)
print(f'\nGATE 7 RECONCILIATION: {n}/{len(G)} ' + ('PASS' if n==len(G) else '*** FAIL ***'))
sys.exit(0 if n==len(G) else 1)
