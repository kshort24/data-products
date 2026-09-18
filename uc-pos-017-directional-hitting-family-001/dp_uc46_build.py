"""dp_uc46_build -- exercise the family against Phillies pos 2024-2026 (R) and
emit CSV receipts. Library validation run, not an analysis UC."""
import sys, glob, json
import numpy as np, pandas as pd
sys.path.insert(0,'/home/claude/build/pkg')
import dp_uc46_kernel as k
OUT='/home/claude/build/out/'

fs = sorted(glob.glob('/mnt/user-data/uploads/MLB/data/phillies/phils_*.parquet'))
df = pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True)
pos = df[((df.home_team=='PHI')&(df.inning_topbot=='Bot'))|
         ((df.away_team=='PHI')&(df.inning_topbot=='Top'))].copy()
pos = pos[pos.game_type=='R']
raw_bip = pos[pos.type=='X']
bip = k.build_bip(['game_year'], pos)

# ---- 01 source profile -----------------------------------------------------
rows=[]
for y,g in raw_bip.groupby('game_year'):
    c = g[g.hc_x.notna()&g.hc_y.notna()]
    rows.append(dict(game_year=int(y), bip_all=len(g), bip_classifiable=len(c),
        bip_untracked=len(g)-len(c), untracked_pct=round((len(g)-len(c))/len(g)*100,3),
        bb_type_null=int(g.bb_type.isna().sum()),
        la_null=int(g.launch_angle.isna().sum()), la_null_pct=round(g.launch_angle.isna().mean()*100,3),
        ev_null=int(g.launch_speed.isna().sum()), ev_null_pct=round(g.launch_speed.isna().mean()*100,3),
        dist_null=int(g.hit_distance_sc.isna().sum()), dist_null_pct=round(g.hit_distance_sc.isna().mean()*100,3),
        dist_zero=int((g.hit_distance_sc==0).sum())))
sp = pd.DataFrame(rows); sp.to_csv(OUT+'01_source_profile.csv', index=False)

# ---- 02 direction rate, season grain --------------------------------------
dr_season = k.direction_rate(['game_year'], bip)
dr_season.round(6).to_csv(OUT+'02_direction_rate_season.csv', index=False)

# ---- 03 direction rate, season x stand ------------------------------------
k.direction_rate(['game_year','stand'], bip).round(6).to_csv(OUT+'03_direction_rate_season_stand.csv', index=False)

# ---- 04 direction rate, player x season (2026, floor applied) -------------
dr_p = k.direction_rate(['player_name','game_year'], bip)
dr_p26 = dr_p[dr_p.game_year==2026].sort_values('n_bip', ascending=False)
dr_p26.round(6).to_csv(OUT+'04_direction_rate_player_2026.csv', index=False)

# ---- 05 bb_type profile, season grain -------------------------------------
prof = k.bb_type_profile(['game_year'], bip)
prof.round(3).to_csv(OUT+'05_bb_type_profile_season.csv', index=False)

# ---- 06 bb_type profile at DIRECTION grain -> oppo_ld_rate ----------------
pd_dir = k.bb_type_profile(['game_year','hit_direction'], bip)
pd_dir.round(3).to_csv(OUT+'06_bb_type_profile_direction.csv', index=False)
oppo_ld = pd_dir[(pd_dir.hit_direction=='Oppo')&(pd_dir.bb_type=='line_drive')][
    ['game_year','bips','total_level','share','below_floor','n_la','mu_la','std_la',
     'n_ev','mu_ev','n_dist','mu_dist']].rename(columns={'share':'oppo_ld_rate'})
oppo_ld.round(6).to_csv(OUT+'07_oppo_ld_rate_season.csv', index=False)

# ---- 08 BREAKING CHANGE quantification: patched vs v0 denominator ---------
new = k.pull_air_rate(['game_year'], bip).set_index('game_year')
rows=[]
for y,g in raw_bip.groupby('game_year'):
    c = g[g.hc_x.notna()&g.hc_y.notna()].copy()
    c = k.derive_loc([], c); c['hit_direction']=k.hit_direction([], c)
    pull_air = len(c[(c.hit_direction=='Pull')&(c.bb_type!='ground_ball')])
    v0 = pull_air/len(g); v1 = pull_air/len(c)
    rows.append(dict(game_year=int(y), pull_airs=pull_air,
                     v0_denominator_all_bip=len(g), v0_pull_air_rate=round(v0,6),
                     v1_denominator_classifiable=len(c), v1_pull_air_rate=round(v1,6),
                     delta_pp=round((v1-v0)*100,4)))
bc = pd.DataFrame(rows); bc.to_csv(OUT+'08_breaking_change_pull_air_rate.csv', index=False)

# ---- 09 player scorecard source: 2026 qualified, direction x bb_type ------
qual = dr_p26[~dr_p26.below_floor].player_name.tolist()
b26 = bip[(bip.game_year==2026)&(bip.player_name.isin(qual))]
card = k.bb_type_profile(['player_name','hit_direction'], b26)
card.round(3).to_csv(OUT+'09_scorecard_source_2026.csv', index=False)

# ---- headline JSON at 6dp (display-rounding lesson, uc-pos-013) -----------
h = {}
for y in [2024,2025,2026]:
    r = dr_season[dr_season.game_year==y].iloc[0]
    h[str(y)] = dict(n_bip=int(r.n_bip), pull_rate=round(float(r.pull_rate),6),
                     straight_rate=round(float(r.straight_rate),6),
                     oppo_rate=round(float(r.oppo_rate),6))
    o = oppo_ld[oppo_ld.game_year==y].iloc[0]
    h[str(y)]['oppo_ld_rate']=round(float(o.oppo_ld_rate),6)
    h[str(y)]['oppo_bip']=int(o.total_level)
    b = bc[bc.game_year==y].iloc[0]
    h[str(y)]['pull_air_rate_v1']=round(float(b.v1_pull_air_rate),6)
    h[str(y)]['pull_air_rate_v0']=round(float(b.v0_pull_air_rate),6)
h['qualified_hitters_2026']=len(qual)
h['verification']='49/49'
json.dump(h, open(OUT+'headlines.json','w'), indent=2)

print('--- 02 direction_rate season ---'); print(dr_season.round(4).to_string(index=False))
print('\n--- 07 oppo_ld_rate ---'); print(oppo_ld.round(4).to_string(index=False))
print('\n--- 08 breaking change ---'); print(bc.to_string(index=False))
print('\n--- 03 by stand ---'); print(k.direction_rate(['game_year','stand'],bip).round(4).to_string(index=False))
print(f'\nqualified 2026 hitters (>={k.BIP_FLOOR} classifiable BIP): {len(qual)}')
print('\n--- top 8 by oppo_rate, 2026 qualified ---')
print(dr_p26[~dr_p26.below_floor].nlargest(8,'oppo_rate')[
    ['player_name','n_bip','pull_rate','straight_rate','oppo_rate']].round(3).to_string(index=False))
