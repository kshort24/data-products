"""
dp_uc46_verification -- independent verification for the directional family.

Families
  A  hand-computed fixture (synthetic, every expected value derived by hand
     in the docstring below -- NOT by running the code and recording output)
  B  real-data invariants (Phillies pos 2024-2026, game_type R)
  C  parent reproduction: direction_rate vs dp_uc42 directional_rate_table
  D  share-arm reproduction: bb_type_profile vs governed bb_type_by_level (cell 50)
  E  sensor-boundary conduct (per-sensor n, no fillna leakage, NULL rates)
  F  narrative/receipt reconciliation (run by dp_uc46_family_f.py after the
     report is written)

Register Principle 4: a KPI is not verified by being reused. Family A is the
only family that can detect a wrong formula; B-E detect drift and misconduct.
"""
import sys, glob
import numpy as np
import pandas as pd
sys.path.insert(0, '/home/claude/build/pkg')
import dp_uc46_kernel as k

CHECKS = []
def chk(fam, name, cond, detail=''):
    CHECKS.append((fam, name, bool(cond), detail))

# ==========================================================================
# FIXTURE -- hand-derived expectations
# --------------------------------------------------------------------------
# Inverse of PA-L1:  hc_x = loc_x/2.495671 + 125.42 ; hc_y = 198.27 - loc_y/2.495671
#   loc_x -100 -> hc_x  85.35085 | loc_x +100 -> hc_x 165.48915 | loc_x 0 -> 125.42
#   loc_y  200 -> hc_y 118.13176 | loc_y  300 -> hc_y  78.06264
#
# RHB (Pull when loc_y <= -4.7*loc_x):
#   (-100,200): 200 <= 470   -> Pull          x3  (2 ground_ball, 1 fly_ball)
#   (+100,200): 200 <= 470   -> Oppo          x4  (3 line_drive,  1 fly_ball)
#   (   0,300): 300>0 & 300>0-> Straightaway  x1  (1 line_drive)
#   + 1 untracked BIP (hc NaN)   -> MUST be excluded (DEN-1)
#   + 1 non-BIP row (type='S')   -> MUST be excluded
#   => n_bip 8 | pull 3 oppo 4 straight 1
#      pull_rate 3/8=.375  oppo_rate 4/8=.500  straight_rate 1/8=.125  sum=1
#      pull_air_rate = non-GB pulls (1 fly_ball) / 8 = .125
#      oppo_ld_rate  = 3 line_drive / 4 oppo BIP = .750          (LD-1)
#   Oppo line_drive sensor values: la [20,30,NaN] ev [100,105,90] dist [250,260,200]
#      n_la 2  mu_la 25.0  std_la sqrt(50)=7.07107  min_la 20 max_la 30
#      n_ev 3  mu_ev 98.33333  min_ev 90 max_ev 105
#      n_dist 3  mu_dist 236.66667
#
# LHB (Pull when loc_y <= +4.7*loc_x):
#   (+100,200) -> Pull  x1 (line_drive) | (-100,200) -> Oppo x1 (ground_ball)
#   => n_bip 2 | pull_rate .5 oppo_rate .5 straight_rate 0
# ==========================================================================
HX_NEG, HX_POS, HX_MID = 85.35085, 165.48915, 125.42
HY_200, HY_300 = 118.13176, 78.06264

def row(pn, stand, hx, hy, bbt, la, ev, dist, typ='X'):
    return dict(player_name=pn, stand=stand, hc_x=hx, hc_y=hy, bb_type=bbt,
                launch_angle=la, launch_speed=ev, hit_distance_sc=dist,
                type=typ, des='d')

R = 'Test, Righty'; L = 'Test, Lefty'
fx = pd.DataFrame([
    row(R,'R',HX_NEG,HY_200,'ground_ball', -10, 92, 15),
    row(R,'R',HX_NEG,HY_200,'ground_ball',  -5, 88, 30),
    row(R,'R',HX_NEG,HY_200,'fly_ball',     32, 99, 340),
    row(R,'R',HX_POS,HY_200,'line_drive',   20,100, 250),
    row(R,'R',HX_POS,HY_200,'line_drive',   30,105, 260),
    row(R,'R',HX_POS,HY_200,'line_drive', np.nan,90, 200),
    row(R,'R',HX_POS,HY_200,'fly_ball',     35, 95, 330),
    row(R,'R',HX_MID,HY_300,'line_drive',   18, 98, 240),
    row(R,'R',np.nan,np.nan,'ground_ball',  -8, 85, 20),          # untracked
    row(R,'R',HX_NEG,HY_200,'ground_ball',  -9, 91, 25,typ='S'),  # not a BIP
    row(L,'L',HX_POS,HY_200,'line_drive',   22,101, 255),
    row(L,'L',HX_NEG,HY_200,'ground_ball',  -6, 89, 18),
])

LV = ['player_name']
bip = k.build_bip(LV, fx)

chk('A','fixture: classifiable BIP excludes untracked + non-BIP', len(bip)==10, f'n={len(bip)}')
chk('A','fixture: no "not grouped" leakage', (bip.hit_direction==k.UNGROUPED).sum()==0)

dr = k.direction_rate(LV, bip).set_index('player_name')
r = dr.loc[R]
chk('A','fixture RHB n_bip==8', r.n_bip==8, f'{r.n_bip}')
chk('A','fixture RHB pull_n==3', r.pull_n==3, f'{r.pull_n}')
chk('A','fixture RHB oppo_n==4', r.oppo_n==4, f'{r.oppo_n}')
chk('A','fixture RHB straight_n==1', r.straight_n==1, f'{r.straight_n}')
chk('A','fixture RHB pull_rate==0.375', abs(r.pull_rate-0.375)<1e-12, f'{r.pull_rate}')
chk('A','fixture RHB oppo_rate==0.500', abs(r.oppo_rate-0.500)<1e-12, f'{r.oppo_rate}')
chk('A','fixture RHB straight_rate==0.125', abs(r.straight_rate-0.125)<1e-12, f'{r.straight_rate}')
l = dr.loc[L]
chk('A','fixture LHB pull_rate==0.5 (stand-aware mirror)', abs(l.pull_rate-0.5)<1e-12, f'{l.pull_rate}')
chk('A','fixture LHB oppo_rate==0.5 (stand-aware mirror)', abs(l.oppo_rate-0.5)<1e-12, f'{l.oppo_rate}')
chk('A','fixture LHB straight_rate==0.0', abs(l.straight_rate-0.0)<1e-12, f'{l.straight_rate}')

par = k.pull_air_rate(LV, bip).set_index('player_name')
chk('A','fixture RHB pull_air_rate==0.125', abs(par.loc[R,'pull_air_rate']-0.125)<1e-12,
    f'{par.loc[R,"pull_air_rate"]}')
chk('A','fixture RHB pull_air denominator is classifiable BIP (8, not 9)',
    par.loc[R,'total_bips']==8, f'{par.loc[R,"total_bips"]}')

pr = k.bb_type_profile(LV+['hit_direction'], bip)
ld = pr[(pr.player_name==R)&(pr.hit_direction=='Oppo')&(pr.bb_type=='line_drive')].iloc[0]
chk('A','fixture oppo_ld_rate==0.750 (LD-1: oppo LD / oppo BIP)', abs(ld.share-0.75)<1e-12, f'{ld.share}')
chk('A','fixture oppo denominator total_level==4', ld.total_level==4, f'{ld.total_level}')
chk('A','fixture n_la==2 (one NULL launch_angle dropped)', ld.n_la==2, f'{ld.n_la}')
chk('A','fixture n_ev==3', ld.n_ev==3, f'{ld.n_ev}')
chk('A','fixture n_dist==3', ld.n_dist==3, f'{ld.n_dist}')
chk('A','fixture per-sensor n DIFFER (n_la != n_ev)', ld.n_la!=ld.n_ev, f'{ld.n_la} vs {ld.n_ev}')
chk('A','fixture mu_la==25.0 (NULL excluded, not zero-filled)', abs(ld.mu_la-25.0)<1e-9, f'{ld.mu_la}')
chk('A','fixture std_la==sqrt(50)', abs(ld.std_la-np.sqrt(50))<1e-9, f'{ld.std_la}')
chk('A','fixture min_la==20 / max_la==30', ld.min_la==20 and ld.max_la==30, f'{ld.min_la}/{ld.max_la}')
chk('A','fixture mu_ev==98.33333', abs(ld.mu_ev-295/3)<1e-9, f'{ld.mu_ev}')
chk('A','fixture mu_dist==236.66667', abs(ld.mu_dist-710/3)<1e-9, f'{ld.mu_dist}')
chk('A','fixture below_floor True at n=4 (FL-1=25)', bool(ld.below_floor))

# convention assertion must FAIL loudly on an inverted frame
inv = bip.copy(); inv['loc_x'] = -inv.loc_x
try:
    k.assert_spray_convention(LV, inv); raised = False
except AssertionError:
    raised = True
chk('A','O-15 convention assertion RAISES on inverted loc_x', raised)

# ==========================================================================
# REAL DATA
# ==========================================================================
fs = sorted(glob.glob('/mnt/user-data/uploads/MLB/data/phillies/phils_*.parquet'))
df = pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True)
pos = df[((df.home_team=='PHI')&(df.inning_topbot=='Bot'))|
         ((df.away_team=='PHI')&(df.inning_topbot=='Top'))].copy()
pos = pos[pos.game_type=='R']
RB = k.build_bip(['game_year'], pos)

chk('B','real: spray convention holds (RHB pull median loc_x < 0)',
    k.assert_spray_convention(['game_year'], RB)['R'] < 0)
chk('B','real: LHB pull median loc_x > 0',
    k.assert_spray_convention(['game_year'], RB)['L'] > 0)
chk('B','real: zero "not grouped"', (RB.hit_direction==k.UNGROUPED).sum()==0)
chk('B','real: PITCH_KEY unique (no fan-out)', not RB.duplicated(subset=k.PITCH_KEY).any(),
    f'dups={int(RB.duplicated(subset=k.PITCH_KEY).sum())}')

dry = k.direction_rate(['game_year'], RB)
chk('B','real: rates sum to 1.0 every cell (DR-3)',
    np.allclose(dry.pull_rate+dry.straight_rate+dry.oppo_rate, 1.0),
    str((dry.pull_rate+dry.straight_rate+dry.oppo_rate).round(12).tolist()))
chk('B','real: counts sum to n_bip every cell',
    ((dry.pull_n+dry.straight_n+dry.oppo_n)==dry.n_bip).all())
chk('B','real: no cell below FL-1 floor at season grain', (~dry.below_floor).all())

# ==========================================================================
# C -- parent reproduction against dp_uc42 directional_rate_table
# ==========================================================================
def parent_directional_rate_table(bip, level='game_year'):
    """VERBATIM logic of dp_uc42_kernel.directional_rate_table."""
    rows=[]
    for yr,grp in bip.groupby(level):
        n=len(grp)
        pull=(grp.hit_direction=='Pull').sum(); oppo=(grp.hit_direction=='Oppo').sum()
        st=(grp.hit_direction=='Straightaway').sum()
        rows.append(dict(**{level:yr}, n_bip=n, pull_n=pull, oppo_n=oppo, straight_n=st,
                         pull_rate=pull/n if n else np.nan, oppo_rate=oppo/n if n else np.nan,
                         straight_rate=st/n if n else np.nan))
    return pd.DataFrame(rows)

p = parent_directional_rate_table(RB).set_index('game_year')
c = dry.set_index('game_year')
for col in ['n_bip','pull_n','oppo_n','straight_n']:
    chk('C', f'parent reproduction: {col} identical', (p[col].values==c[col].values).all(),
        f'{p[col].tolist()} vs {c[col].tolist()}')
for col in ['pull_rate','oppo_rate','straight_rate']:
    chk('C', f'parent reproduction: {col} identical', np.allclose(p[col].values,c[col].values))

# ==========================================================================
# D -- share arm reproduces the governed bb_type_by_level (cell 50)
# ==========================================================================
def cell50_bb_type_by_level(level, df):
    """VERBATIM Baseball Functions.ipynb cell 50."""
    bb = df[df.type=='X'].groupby(level+['bb_type'], as_index=False).agg(bips=('des','size'))
    grp = bb.groupby(level, as_index=False).agg(total_level=('bips','sum')).merge(bb, on=level, how='right')
    grp['share'] = grp.bips/grp.total_level
    return grp.round(3)

gov = cell50_bb_type_by_level(['game_year'], RB).set_index(['game_year','bb_type']).sort_index()
new = k.bb_type_profile(['game_year'], RB).set_index(['game_year','bb_type']).sort_index()
chk('D','share arm: same cells as cell 50', list(gov.index)==list(new.index))
chk('D','share arm: bips identical to cell 50', (gov.bips.values==new.bips.values).all())
chk('D','share arm: total_level identical to cell 50', (gov.total_level.values==new.total_level.values).all())
chk('D','share arm: share identical to cell 50 (3dp)',
    np.allclose(gov.share.values, new.share.round(3).values))

# ==========================================================================
# E -- sensor-boundary conduct
# ==========================================================================
prof26 = k.bb_type_profile(['game_year'], RB)
p26 = prof26[prof26.game_year==2026]
chk('E','per-sensor n present for all three sensors',
    all(c_ in prof26.columns for c_ in ['n_la','n_ev','n_dist']))
chk('E','2026: at least one cell where n_la != bips (sensor gap visible, not hidden)',
    (p26.n_la != p26.bips).any(),
    f'{[(r.bb_type,int(r.bips),int(r.n_la)) for r in p26.itertuples()]}')
chk('E','no rate column was zero-filled: direction_rate rates are NaN-safe',
    dry[['pull_rate','straight_rate','oppo_rate']].notna().all().all())
empty = RB.iloc[0:0]
er = k.direction_rate(['game_year'], empty)
chk('E','empty frame returns empty, does not raise', len(er)==0)

# ==========================================================================
print(f'\n{"="*78}\ndp_uc46 VERIFICATION\n{"="*78}')
fam_order = ['A','B','C','D','E']
npass = sum(1 for c in CHECKS if c[2])
for fam in fam_order:
    rows=[c for c in CHECKS if c[0]==fam]
    print(f'\n--- family {fam}: {sum(1 for r in rows if r[2])}/{len(rows)} ---')
    for _,name,ok,detail in rows:
        print(f'  [{"PASS" if ok else "FAIL"}] {name}' + (f'   ({detail})' if not ok and detail else ''))
print(f'\n{"="*78}\nTOTAL {npass}/{len(CHECKS)} ' + ('PASS' if npass==len(CHECKS) else '*** FAIL ***'))
sys.exit(0 if npass==len(CHECKS) else 1)
