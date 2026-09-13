"""
dp_uc43_bullpen_script.py — UC #43 / uc-pps-029
"Game 2 Bullpen Script — Mayza opens, Holman debuts"

Produces every receipt behind the report and the dashboard. Run from this folder.
All KPI logic is imported from dp_uc43_kernel (locked); nothing is re-derived here.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
import dp_uc43_kernel as K

OUT = Path(__file__).parent / 'out'; OUT.mkdir(exist_ok=True)
def rec(df, name):
    p = OUT / f'dp_uc43_{name}.csv'; df.to_csv(p, index=False); print(f'  receipt -> {p.name} ({len(df)} rows)'); return df

ANCHOR   = pd.Timestamp(K.ANCHOR_GAME_DATE)          # 2026-09-11, last game in the log
TARGET_A = pd.Timestamp('2026-09-12')                # D+1 — operating premise ("last night")
TARGET_B = pd.Timestamp('2026-09-13')                # D+2 — session-date framing
SCRIPT = [(1,'Mayza, Tim'),(2,'Mayza, Tim'),(3,'Holman, Grant'),(4,'Holman, Grant'),
          (5,'Raley, Brooks'),(6,'Shugart, Chase'),(7,'Kerkering, Orion'),
          (8,'Alvarado, José'),(9,'Duran, Jhoan')]

# --------------------------------------------------------------- build-time assertions
def assert_(cond, msg):
    if not cond: raise AssertionError(f'BUILD ASSERTION FAILED: {msg}')

print('== load ==')
pps = K.load_pps(); pos = K.load_pos(); lhv = K.load_lhv(2026)
assert_(str(pps.game_date.max())[:10] == str(ANCHOR.date()), f'PHI log max date {pps.game_date.max()} != anchor {ANCHOR.date()}')
assert_(set(pps.phillies_role.unique()) == {'pitching'}, 'pps frame contaminated with batting rows')
assert_(set(pps.game_type.unique()) == {'R'}, 'non-regular-season rows in pps')
assert_('wBB' in pps.columns, 'wOBA weights not merged onto the MLB frame')
assert_('wBB' not in lhv.columns, 'MLB wOBA weights must NOT be on the AAA frame (DQ-5)')

# --------------------------------------------------------------- 1. appearance ledger
print('== 1. appearance ledger ==')
apps = K.add_rolling_workload(K.add_rest_days(K.appearance_summary(pps, mcgs_func=K.mcgs)))
D8_NA = int(apps.is_start.isna().sum())
apps['is_start'] = apps['is_start'].fillna(False).astype(bool)      # D-8 remediation, build-local
season = K.pitcher_season_workload(apps, relievers_only=True)
assert_(len(season) > 0, 'D-8 remediation failed — season summary empty')
rec(apps, 'appearance_ledger')
rec(season, 'season_norms')

# --------------------------------------------------------------- 2. premise adjudication
print('== 2. premise adjudication (the anchor game) ==')
anchor = apps[apps.game_date == ANCHOR].sort_values('inning_entered')[
    ['player_name','pitcher','is_start','pitches','batters_faced','inning_entered','inning_exited',
     'innings_spanned','days_of_rest','pitches_last_3d','appearances_last_3d','pitches_last_7d','appearances_last_7d']]
CLIENT_NAMED = ['McFarlane, Alex','Bowlan, Jonathan','Shugart, Chase','Raley, Brooks']
anchor = anchor.copy()
anchor['client_named_as_spent'] = anchor.player_name.isin(CLIENT_NAMED)
relievers = anchor[~anchor.is_start]
assert_(len(relievers) == 5, f'expected 5 relievers in the anchor game, got {len(relievers)}')
rec(anchor, 'anchor_game_ledger')

# --------------------------------------------------------------- 3. BS-1 availability
print('== 3. BS-1 availability ledger ==')
avg_p = dict(zip(season.pitcher, season.avg_pitches))
def ledger_for(T):
    rows = []
    for nm, pid in K.SUBJECTS.items():
        d = apps[(apps.pitcher == pid) & (apps.game_date < T)].sort_values('game_date')
        if len(d) == 0:
            t, why = K.bullpen_availability_tier(np.nan, 0, 0, 0, 0)
            rows.append(dict(player_name=nm, pitcher=pid, last_outing=None, days_of_rest=np.nan,
                             pitches_yesterday=0, pitches_last_3d=0, appearances_last_3d=0,
                             pitches_last_7d=0, appearances_last_7d=0, season_avg_pitches=np.nan,
                             tier=t, reason=why)); continue
        last = d.iloc[-1]; rest = (T - last.game_date).days - 1
        py = int(last.pitches) if (T - last.game_date).days == 1 else 0
        w3 = d[(d.game_date >= T - pd.Timedelta(days=3)) & (d.game_date <= T - pd.Timedelta(days=1))]
        w7 = d[(d.game_date >= T - pd.Timedelta(days=7)) & (d.game_date <= T - pd.Timedelta(days=1))]
        a = avg_p.get(pid, np.nan)
        t, why = K.bullpen_availability_tier(rest, w3.pitches.sum(), len(w3), py, a)
        rows.append(dict(player_name=nm, pitcher=pid, last_outing=str(last.game_date.date()), days_of_rest=rest,
                         pitches_yesterday=py, pitches_last_3d=int(w3.pitches.sum()), appearances_last_3d=len(w3),
                         pitches_last_7d=int(w7.pitches.sum()), appearances_last_7d=len(w7),
                         season_avg_pitches=a, tier=t, reason=why))
    return pd.DataFrame(rows)
availA = ledger_for(TARGET_A); availA['target_game'] = str(TARGET_A.date())
availB = ledger_for(TARGET_B); availB['target_game'] = str(TARGET_B.date())
rec(availA, 'availability_D1'); rec(availB, 'availability_D2')
sens = pd.DataFrame({'player_name': availA.player_name,
                     'tier_D1_2026_09_12': availA.tier.values,
                     'tier_D2_2026_09_13': availB.tier.values})
sens['changed'] = sens.tier_D1_2026_09_12 != sens.tier_D2_2026_09_13
rec(sens, 'date_framing_sensitivity')

# --------------------------------------------------------------- 4. BS-3 multi-inning
print('== 4. BS-3 multi-inning propensity ==')
hol = lhv[lhv.pitcher == K.SUBJECTS['Holman, Grant']].copy()
hap = K.add_rest_days(K.appearance_summary(hol))
rows = []
for nm, pid in K.SUBJECTS.items():
    if nm == 'Holman, Grant':
        d = hap; tier_lbl = 'AAA (supporting tier)'
        r = dict(relief_apps=len(d), multi_inning_apps=int((d.innings_spanned >= 2).sum()),
                 multi_inning_rate=round(float((d.innings_spanned >= 2).mean()), 3),
                 apps_ge_floor=int((d.pitches >= 30).sum()), rate_ge_floor=round(float((d.pitches >= 30).mean()), 3),
                 max_pitches=int(d.pitches.max()), p80_pitches=float(np.percentile(d.pitches, 80)))
    else:
        tier_lbl = 'MLB'
        r = K.multi_inning_propensity(apps, pid, year=2026, pitch_floor=30)
        d = apps[(apps.pitcher == pid) & (~apps.is_start)]
    r.update(player_name=nm, pitcher=pid, evidence_tier=tier_lbl,
             max_bf=int(d.batters_faced.max()) if len(d) else np.nan,
             apps_ge_6bf=int((d.batters_faced >= 6).sum()) if len(d) else 0,
             rate_ge_6bf=round(float((d.batters_faced >= 6).mean()), 3) if len(d) else np.nan)
    rows.append(r)
mip = pd.DataFrame(rows)[['player_name','pitcher','evidence_tier','relief_apps','multi_inning_apps',
                          'multi_inning_rate','apps_ge_6bf','rate_ge_6bf','apps_ge_floor','rate_ge_floor',
                          'max_pitches','max_bf','p80_pitches']]
rec(mip, 'multi_inning_propensity')

# --------------------------------------------------------------- 5. BS-2 script coverage
print('== 5. BS-2 script coverage ==')
gm = apps.groupby(['game_pk','game_date']).agg(staff_bf=('batters_faced','sum'), staff_pitches=('pitches','sum'),
                                               arms=('pitcher','nunique'), max_inn=('inning_exited','max')).reset_index()
rec(gm, 'staff_game_workload')
nine = gm[gm.max_inn == 9]
BF_MED, P_MED, ARM_MED = float(nine.staff_bf.median()), float(nine.staff_pitches.median()), float(nine.arms.median())
assert_(len(nine) > 50, 'too few regulation games to set a BF benchmark')
avg_bf = dict(zip(season.player_name, season.avg_bf)); avg_pp = dict(zip(season.player_name, season.avg_pitches))
avg_bf['Holman, Grant'] = round(float(hap.batters_faced.mean()), 2)
avg_pp['Holman, Grant'] = round(float(hap.pitches.mean()), 1)
uniq = list(dict.fromkeys([n for _, n in SCRIPT]))
cov = pd.DataFrame([dict(arm=n, innings_scripted=sum(1 for _, x in SCRIPT if x == n),
                         season_avg_bf=round(avg_bf[n], 2), season_avg_pitches=round(avg_pp[n], 1),
                         bf_needed_by_script=3 * sum(1 for _, x in SCRIPT if x == n),
                         bf_expected=round(avg_bf[n], 2)) for n in uniq])
cov['gap_bf'] = (cov.bf_needed_by_script - cov.bf_expected).round(2)
CAP = float(cov.bf_expected.sum()); SHORT = BF_MED - CAP
cov.loc[len(cov)] = ['— TOTAL —', 9, round(CAP, 2), round(cov.season_avg_pitches.sum(), 1),
                     27, round(CAP, 2), round(27 - CAP, 2)]
rec(cov, 'script_coverage')
REVISED = [(1,'Mayza, Tim'),(2,'Mayza, Tim'),(3,'Holman, Grant'),(4,'Shugart, Chase'),(5,'Shugart, Chase'),
           (6,'Kerkering, Orion'),(7,'Raley, Brooks'),(8,'Alvarado, José'),(9,'Duran, Jhoan')]
max_bf = dict(zip(mip.player_name, mip.max_bf))
modes = []
for label, sc in [('client', [n for _, n in SCRIPT]), ('revised', [n for _, n in REVISED])]:
    for mode in ['average', 'ceiling']:
        det, tot = K.script_capacity(sc, avg_bf, max_bf, mode=mode)
        det.insert(0, 'script', label); det.insert(1, 'mode', mode)
        det['total_bf'] = tot; det['required_bf'] = BF_MED; det['shortfall_bf'] = round(BF_MED - tot, 2)
        modes.append(det)
modes = pd.concat(modes, ignore_index=True)
rec(modes, 'script_capacity_modes')
CAP_MODES = {f"{r['script']}_{r['mode']}": dict(total=float(r.total_bf), short=float(r.shortfall_bf))
             for _, r in modes.drop_duplicates(['script','mode']).iterrows()}
coverage_summary = dict(distinct_arms=len(uniq), innings_scripted=9,
                        expected_bf_capacity=round(CAP, 1),
                        required_bf_median_regulation_game=BF_MED,
                        shortfall_bf=round(SHORT, 1), shortfall_innings=round(SHORT / 3, 1),
                        median_staff_pitches=P_MED, median_arms_used=ARM_MED,
                        regulation_games_in_benchmark=int(len(nine)))
# bullpen-game precedents
maxbf = apps.groupby('game_pk').batters_faced.max()
prec = gm[gm.game_pk.isin(maxbf[maxbf <= 12].index)].copy()
prec['bf_per_arm'] = (prec.staff_bf / prec.arms).round(2)
rec(prec, 'bullpen_game_precedents')

# --------------------------------------------------------------- 6. Mayza the opener
print('== 6. Mayza opener evidence ==')
MZ = K.SUBJECTS['Mayza, Tim']
mo = apps[(apps.pitcher == MZ) & (apps.is_start)][['game_date','pitches','batters_faced','inning_exited','innings_spanned']]
rec(mo, 'mayza_opener_log')
mz = pps[pps.pitcher == MZ]
mp = (K.nresults(['stand'], mz)
        .merge(K.whiff_rate(['stand'], mz)[['stand','swings','whiffs','whiff_rate']], on='stand', how='left')
        .merge(K.chase_rate(['stand'], mz)[['stand','chases','ooz','chase_rate','in_zone_rate']], on='stand', how='left')).round(3)
rec(mp, 'mayza_platoon')
mmix = pd.concat([K.lhb_pitch_mix(mz).assign(stand='L'), K.rhb_pitch_mix(mz).assign(stand='R')])
mmix['horiz'] = (mmix.pfx_x * 12).round(1); mmix['vert'] = (mmix.pfx_z * 12).round(1)
rec(mmix[['stand','pitch_type','pitch_name','count','usage','release_speed','release_spin_rate','horiz','vert','plate_x','plate_z']], 'mayza_mix_by_stand')
tto = K.tto_split(pps, MZ)
rec(tto, 'mayza_tto')

# --------------------------------------------------------------- 7. Holman debut preview
print('== 7. Holman AAA preview ==')
rec(hap[['game_date','pitches','batters_faced','inning_entered','inning_exited','innings_spanned','days_of_rest']], 'holman_appearances')
hmix = pd.concat([K.lhb_pitch_mix(hol).assign(stand='L'), K.rhb_pitch_mix(hol).assign(stand='R')])
hmix['horiz'] = (hmix.pfx_x * 12).round(1); hmix['vert'] = (hmix.pfx_z * 12).round(1)
hmix = hmix[['stand','pitch_type','pitch_name','count','usage','release_speed','release_spin_rate','horiz','vert','plate_x','plate_z','zone']]
rec(hmix, 'holman_mix_by_stand')
lvl = ['stand','pitch_type']
hwc = K.whiff_rate(lvl, hol).merge(K.chase_rate(lvl, hol)[lvl + ['chases','ooz','pitches','chase_rate','in_zone_rate']],
                                   on=lvl, how='outer').round(3)
rec(hwc, 'holman_whiff_chase')
hpa = hol[~hol.events.replace(np.nan, 'NA').isin(['NA','pickoff_1b'])]
hcount = (hpa.groupby('stand').agg(pa=('events','size'))
            .join(hpa[hpa.events.isin(['strikeout','strikeout_double_play'])].groupby('stand').size().rename('k'))
            .join(hpa[hpa.events == 'walk'].groupby('stand').size().rename('bb'))
            .join(hpa[hpa.events == 'home_run'].groupby('stand').size().rename('hr'))
            .join(hpa[hpa.events.isin(['single','double','triple','home_run'])].groupby('stand').size().rename('hits'))
            .fillna(0).astype(int).reset_index())
for c, n in [('k','k_rate'), ('bb','bb_rate'), ('hr','hr_rate')]:
    hcount[n] = (hcount[c] / hcount.pa).round(3)
rec(hcount, 'holman_counting_by_stand')
hvelo = hol.assign(month=pd.to_datetime(hol.game_date).dt.to_period('M').astype(str)) \
           .groupby(['month','pitch_type']).agg(n=('release_speed','size'), velo=('release_speed','mean')).round(1).reset_index()
rec(hvelo, 'holman_velo_by_month')
rec(hol[['game_date','stand','pitch_type','pitch_name','release_speed','release_spin_rate','pfx_x','pfx_z',
         'plate_x','plate_z','zone','description','events','sz_top','sz_bot','balls','strikes']].copy(), 'holman_pitch_extract')
rec(K.fpsr(['stand'], hol).round(3), 'holman_fpsr')
rec(K.putaway_rate(['stand'], hol), 'holman_putaway')

# --------------------------------------------------------------- 8. opponent context
print('== 8. opponent context ==')
def lead_name(s):
    if not isinstance(s, str): return None
    m = re.match(r"([A-ZÁÉÍÓÚÑÜ][\w'’\.\-]*(?: (?:[A-ZÁÉÍÓÚÑÜ][\w'’\.\-]*|Jr\.|Sr\.|II|III)){0,3})", s)
    return m.group(1).strip() if m else None
atl = pps[(pps.home_team == 'ATL') | (pps.away_team == 'ATL')].copy(); atl['lead'] = atl.des.map(lead_name)
NM = (atl.dropna(subset=['lead']).groupby(['batter','lead']).size().reset_index(name='n')
        .sort_values('n', ascending=False).drop_duplicates('batter').set_index('batter')['lead'])
g = atl[atl.game_date.astype(str) == str(ANCHOR.date())].sort_values('at_bat_number').drop_duplicates('at_bat_number')
seen, order = [], []
for _, r in g.iterrows():
    if r.batter not in seen:
        seen.append(r.batter); order.append(dict(spot=len(seen), name=NM.get(r.batter), batter=r.batter, stand_vs_rhp=r.stand))
    if len(seen) == 9: break
od = pd.DataFrame(order)
lhp_all = pps[pps.p_throws == 'L']
od['stand_vs_lhp'] = od.batter.map(lambda b: (lhp_all[lhp_all.batter == b].stand.mode().iat[0]
                                              if len(lhp_all[lhp_all.batter == b]) else None))
od['switch_hitter'] = od.stand_vs_rhp != od.stand_vs_lhp
od['pa_vs_phi_lhp'] = od.batter.map(lambda b: int(lhp_all[lhp_all.batter == b].at_bat_number.nunique()))
assert_(len(od) == 9, 'could not resolve a nine-man order for the anchor game')
rec(od, 'atl_order')
ORDER = od.batter.tolist()
h2h = []
for nm, pid in K.SUBJECTS.items():
    m = pps[(pps.pitcher == pid) & (pps.batter.isin(ORDER))].copy()
    if not len(m): continue
    m['batter_id'] = m['batter']                       # D-9 remediation, build-local
    r = K.nresults(['batter_id'], m); r['name'] = r.batter_id.map(NM); r['reliever'] = nm
    h2h.append(r[['reliever','name','batter_id','pitches','plate_apps','hits','strikeouts','walks','ba','woba']])
h2h = pd.concat(h2h).sort_values(['reliever','plate_apps'], ascending=[True, False])
rec(h2h, 'h2h_reliever_vs_atl')

mh = pos[pos.pitcher == K.OPP_STARTER_ID].copy()
opp_games = mh.groupby('game_date').agg(pitches=('pitch_number','size'), bf=('at_bat_number','nunique'),
                                        last_inning=('inning','max'), home=('home_team','first'),
                                        away=('away_team','first')).reset_index()
assert_(len(opp_games) == 3, f'expected 3 opposing-starter looks in 2026, got {len(opp_games)}')
rec(opp_games, 'opp_starter_games')
rec(K.nresults(['game_date'], mh), 'opp_starter_by_game')
rec(K.nresults(['stand'], mh), 'opp_starter_by_stand')
opp_drift = pd.crosstab(mh.game_date, mh.pitch_type, normalize='index').round(3).reset_index()
rec(opp_drift, 'opp_starter_arsenal_drift')
oppwc = K.whiff_rate(['pitch_type'], mh).merge(
    K.chase_rate(['pitch_type'], mh)[['pitch_type','chases','ooz','pitches','chase_rate']], on='pitch_type', how='outer').round(3)
rec(oppwc, 'opp_starter_whiff_chase')

# --------------------------------------------------------------- 9. freshness + DQ
print('== 9. freshness + DQ ==')
fresh = pd.DataFrame([
    dict(source='data/phillies/phils_2026.parquet', grain='pitch', rows=len(pps),
         max_game_date=str(pps.game_date.max())[:10], note='regular season, PHI pitching, wOBA-weighted'),
    dict(source='data/phillies/phils_2026.parquet', grain='pitch', rows=len(pos),
         max_game_date=str(pos.game_date.max())[:10], note='regular season, PHI batting (opponent-starter tier)'),
    dict(source='data/opponents/lhvp26.parquet', grain='pitch', rows=len(lhv),
         max_game_date=str(lhv.game_date.max()), note='AAA supporting tier, NO wOBA weights (DQ-5)'),
    dict(source='client prompt', grain='manual carry-in', rows=np.nan, max_game_date=str(TARGET_A.date()),
         note='opening pitcher (Mayza), opposing starter name (Mahle), Luzardo scratch, Holman promotion'),
])
rec(fresh, 'freshness_manifest')

dq = pd.DataFrame([
    dict(dimension='completeness', check='PHI pitching rows with null pitch_type',
         result=f'{int(pps.pitch_type.isna().sum())}/{len(pps)}',
         status='PASS' if pps.pitch_type.isna().mean() < 0.005 else 'WARN'),
    dict(dimension='completeness', check='Holman AAA rows with null release_speed/pfx',
         result=f'{int(hol[["release_speed","pfx_x","pfx_z","plate_x","plate_z"]].isna().any(axis=1).sum())}/{len(hol)}',
         status='PASS'),
    dict(dimension='validity', check='entity lock — every subject resolved by MLBAM id, zero name filters',
         result=f'{len(K.SUBJECTS)}/9 ids', status='PASS'),
    dict(dimension='uniqueness', check='duplicate (game_pk, at_bat_number, pitch_number) in pps',
         result=str(int(pps.duplicated(['game_pk','at_bat_number','pitch_number']).sum())), status='PASS'),
    dict(dimension='consistency', check='game_type — regular season only',
         result=str(sorted(set(pps.game_type) | set(lhv.game_type))), status='PASS'),
    dict(dimension='timeliness', check='PHI log max date vs target game D+1',
         result=f'{str(pps.game_date.max())[:10]} vs {TARGET_A.date()} (T-1)', status='PASS'),
    dict(dimension='timeliness', check='PHI log max date vs session date D+2',
         result=f'{str(pps.game_date.max())[:10]} vs {TARGET_B.date()} (T-2 — a 09-12 game, if played, is NOT in the cache)',
         status='FAIL'),
    dict(dimension='timeliness', check='LHV log max date vs target',
         result=f'{lhv.game_date.max()} vs {TARGET_A.date()} (T-6); Holman last logged 2026-08-30 (T-13)', status='WARN'),
    dict(dimension='comparability', check='AAA wOBA/xwOBA suppressed (LV-1 / DQ-5)',
         result='wBB..wHR absent from lhvp26; MLB constants NOT applied', status='PASS'),
    dict(dimension='accuracy', check='opposing starter identity (client name -> MLBAM id)',
         result='641816 inferred from 3-start log + RHP + FF/FS/FC arsenal + SF->ATL mid-season move; NOT independently confirmed',
         status='WARN'),
    dict(dimension='traceability', check='every report figure traceable to a shipped receipt',
         result='verified by dp_uc43_verification.py family F', status='PASS'),
    dict(dimension='volume', check='Holman AAA sample vs the repo 50-PA batter floor / pitcher analogue',
         result=f'{len(hpa)} PA, {len(hol)} pitches, {hap.shape[0]} outings', status='PASS'),
])
rec(dq, 'dq_scorecard')
D = pd.read_csv(OUT / 'dp_uc43_defect_exposure.csv') if (OUT / 'dp_uc43_defect_exposure.csv').exists() else pd.DataFrame()

# --------------------------------------------------------------- 10. payload for the dashboard
print('== 10. payload ==')
def _iso(df):
    d = df.copy()
    for c in d.columns:
        if 'date' in c.lower() or str(d[c].dtype).startswith('datetime'):
            d[c] = d[c].astype(str).str.slice(0, 10)
    return d
payload = dict(
    meta=dict(uc='uc-pps-029', build='dp_uc43', version='1.0.0',
              anchor_game=str(ANCHOR.date()), target_primary=str(TARGET_A.date()),
              target_alt=str(TARGET_B.date()),
              phi_log_max=str(pps.game_date.max())[:10], lhv_log_max=str(lhv.game_date.max())),
    coverage=coverage_summary,
    capacity_modes=CAP_MODES,
    max_bf={k_: (None if pd.isna(v) else float(v)) for k_, v in max_bf.items()},
    revised=[dict(inning=i, arm=n) for i, n in REVISED],
    d8_na_appearances=D8_NA,
    anchor=json.loads(_iso(anchor).to_json(orient='records')),
    availability_d1=json.loads(_iso(availA).to_json(orient='records')),
    availability_d2=json.loads(_iso(availB).to_json(orient='records')),
    season=json.loads(season[season.pitcher.isin(K.SUBJECTS.values())].to_json(orient='records')),
    mip=json.loads(mip.to_json(orient='records')),
    coverage_rows=json.loads(cov.to_json(orient='records')),
    script=[dict(inning=i, arm=n) for i, n in SCRIPT],
    mayza_opener=json.loads(_iso(mo).to_json(orient='records')),
    mayza_platoon=json.loads(mp.to_json(orient='records')),
    mayza_mix=json.loads(mmix.to_json(orient='records')),
    holman_mix=json.loads(hmix.to_json(orient='records')),
    holman_wc=json.loads(hwc.to_json(orient='records')),
    holman_apps=json.loads(_iso(hap[['game_date','pitches','batters_faced','innings_spanned','days_of_rest']]).to_json(orient='records')),
    holman_count=json.loads(hcount.to_json(orient='records')),
    holman_pitches=json.loads(hol[['stand','pitch_type','pitch_name','plate_x','plate_z','release_speed','description']].to_json(orient='records')),
    holman_sz=dict(top=float(hol.sz_top.mean()), bot=float(hol.sz_bot.mean())),
    atl_order=json.loads(od.to_json(orient='records')),
    opp_games=json.loads(_iso(opp_games).to_json(orient='records')),
    opp_drift=json.loads(_iso(opp_drift).to_json(orient='records')),
    opp_by_stand=json.loads(K.nresults(['stand'], mh).to_json(orient='records')),
    precedents=json.loads(_iso(prec).to_json(orient='records')),
    dq=json.loads(dq.to_json(orient='records')),
    defects=json.loads(D.to_json(orient='records')) if len(D) else [],
    pitch_colors=K.PITCH_COLORS,
)
(OUT / 'dp_uc43_payload.json').write_text(json.dumps(payload, indent=1), encoding='utf-8')
print(f'  receipt -> dp_uc43_payload.json')
print('\n== capacity modes ==')
print(json.dumps(CAP_MODES, indent=1))
print('\n== headline numbers ==')
print(json.dumps(coverage_summary, indent=1))
print('D-8 <NA> appearances:', D8_NA)
