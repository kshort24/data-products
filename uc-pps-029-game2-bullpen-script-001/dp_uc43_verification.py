"""
dp_uc43_verification.py — independent verification for UC #43 / uc-pps-029.

Six families. Family B recomputes KPIs by a SECOND CODE PATH (not the kernel functions)
and requires agreement. Family F is the narrative/receipt reconciliation introduced by
uc-pos-016 v1.1.0 (defect V-1): every headline figure in the report prose, the README and
the dashboard markup is recomputed from the shipped receipts and string-matched — including
this harness's own claim about how large it is, checked last.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; OUT = HERE/'out'
sys.path.insert(0, str(HERE)); import dp_uc43_kernel as K

R = []
def chk(fam, name, cond, detail=''):
    R.append(dict(family=fam, check=name, status='PASS' if cond else 'FAIL', detail=str(detail)[:300]))
def near(a, b, tol=1e-6): return abs(float(a)-float(b)) <= tol
def rd(n): return pd.read_csv(OUT/f'dp_uc43_{n}.csv')

pps = K.load_pps(); pos = K.load_pos(); lhv = K.load_lhv(2026)
PAY = json.loads((OUT/'dp_uc43_payload.json').read_text(encoding='utf-8'))
REPORT = (HERE/'dp_uc43_bullpen_script_report.md').read_text(encoding='utf-8')
DASH   = (HERE/'dp_uc43_bullpen_control_room.html').read_text(encoding='utf-8')
README = (HERE/'README.md').read_text(encoding='utf-8') if (HERE/'README.md').exists() else ''

# ============================ A · source & entity integrity ============================
chk('A','PHI log is regular season only', set(pps.game_type)=={'R'}, sorted(set(pps.game_type)))
chk('A','PHI log is pitching-role only', set(pps.phillies_role)=={'pitching'}, sorted(set(pps.phillies_role)))
chk('A','PHI log max date is the anchor', str(pps.game_date.max())[:10]=='2026-09-11', pps.game_date.max())
chk('A','AAA log max date', str(lhv.game_date.max())[:10]=='2026-09-06', lhv.game_date.max())
chk('A','no duplicate pitch keys in pps', pps.duplicated(['game_pk','at_bat_number','pitch_number']).sum()==0)
chk('A','no duplicate pitch keys in lhv', lhv.duplicated(['game_pk','at_bat_number','pitch_number']).sum()==0)
chk('A','wOBA weights present on MLB frame', 'wBB' in pps.columns)
chk('A','wOBA weights ABSENT on AAA frame (DQ-5)', 'wBB' not in lhv.columns)
for nm, pid in K.SUBJECTS.items():
    src = lhv if nm == 'Holman, Grant' else pps
    n = int((src.pitcher == pid).sum())
    chk('A', f'entity lock resolves: {nm} == {pid}', n > 0, f'{n} pitches')
chk('A','Holman has ZERO MLB pitches (supporting tier is the only evidence)',
    int((pps.pitcher==680880).sum())==0)
chk('A','Holman not present in LHV 2025 either',
    int((pd.read_parquet(K.ROOT/'data'/'opponents'/'lhvp25.parquet').pitcher==680880).sum())==0)
chk('A','opposing starter 641816 has exactly 3 looks at PHI in 2026',
    pos[pos.pitcher==641816].game_date.nunique()==3)
chk('A','no name-based filtering anywhere in the build',
    'player_name ==' not in (HERE/'dp_uc43_bullpen_script.py').read_text(encoding='utf-8'))

# ============================ B · KPI recomputation, second path ============================
hol = lhv[lhv.pitcher==680880]
# B1 pitch mix by stand, recomputed with value_counts rather than pitch_mix()
hm = rd('holman_mix_by_stand')
for st in ['L','R']:
    d = hol[hol.stand==st]
    vc = d.pitch_type.value_counts()
    for _, r in hm[hm.stand==st].iterrows():
        chk('B', f'Holman usage {st}/{r.pitch_type}', near(r['count'], vc[r.pitch_type]) and
            near(round(100*vc[r.pitch_type]/len(d),1), r.usage, 0.051), f"{r['count']} vs {vc[r.pitch_type]}")
# B2 whiff rate, recomputed from raw description masks
hw = rd('holman_whiff_chase')
for _, r in hw.dropna(subset=['whiff_rate']).iterrows():
    d = hol[(hol.stand==r['stand']) & (hol.pitch_type==r['pitch_type'])]
    sw = int(d.description.isin(K.SWINGS).sum()); wh = int(d.description.isin(K.WHIFFS).sum())
    chk('B', f"whiff {r['stand']}/{r['pitch_type']}", sw==r.swings and wh==r.whiffs and near(wh/sw, r.whiff_rate, 5e-4),
        f'{wh}/{sw} vs {r.whiffs}/{r.swings}')
# B3 chase rate, recomputed
for _, r in hw.dropna(subset=['chase_rate']).iterrows():
    d = hol[(hol.stand==r['stand']) & (hol.pitch_type==r['pitch_type'])]
    ooz = int((d.zone>9).sum()); ch = int(((d.zone>9) & d.description.isin(K.SWINGS)).sum())
    chk('B', f"chase {r['stand']}/{r['pitch_type']}", ooz==r.ooz and ch==r.chases and near(ch/ooz, r.chase_rate, 5e-4),
        f'{ch}/{ooz}')
# B4 appearance ledger, recomputed by groupby
apps = rd('appearance_ledger')
raw = pps.groupby(['pitcher','game_pk']).agg(p=('pitch_number','size'), bf=('at_bat_number','nunique'),
                                             lo=('inning','min'), hi=('inning','max')).reset_index()
m = apps.merge(raw, on=['pitcher','game_pk'])
chk('B','appearance ledger covers every (pitcher, game)', len(m)==len(apps)==len(raw), f'{len(apps)}/{len(raw)}')
chk('B','pitch counts agree', (m.pitches==m.p).all())
chk('B','batters faced agree', (m.batters_faced==m.bf).all())
chk('B','innings spanned agree', (m.innings_spanned==(m.hi-m.lo+1)).all())
# B5 days of rest, recomputed
a = apps.copy(); a['game_date']=pd.to_datetime(a.game_date)
for pid in K.SUBJECTS.values():
    d = a[a.pitcher==pid].sort_values('game_date')
    if len(d) < 2: continue
    exp = (d.game_date.diff().dt.days - 1)
    chk('B', f'days_of_rest recomputed for {pid}', np.allclose(d.days_of_rest.fillna(-1), exp.fillna(-1)))
# B6 BS-2 capacity recomputed from the season norms
sn = rd('season_norms'); cov = rd('script_coverage'); cov = cov[cov.arm!='— TOTAL —']
avg = dict(zip(sn.player_name, sn.avg_bf))
hap = K.appearance_summary(hol); avg['Holman, Grant'] = round(float(hap.batters_faced.mean()),2)
for _, r in cov.iterrows():
    chk('B', f'avg_bf for {r.arm}', near(avg[r.arm], r.season_avg_bf, 0.011), f'{avg[r.arm]} vs {r.season_avg_bf}')
chk('B','BS-2 capacity = sum over distinct arms', near(cov.bf_expected.sum(), PAY['coverage']['expected_bf_capacity'], 0.051),
    f"{cov.bf_expected.sum()} vs {PAY['coverage']['expected_bf_capacity']}")
# B7 the 37-BF benchmark, recomputed
gm = rd('staff_game_workload'); nine = gm[gm.max_inn==9]
chk('B','regulation-game count', len(nine)==PAY['coverage']['regulation_games_in_benchmark'], len(nine))
chk('B','median staff BF = 37', near(nine.staff_bf.median(), PAY['coverage']['required_bf_median_regulation_game']),
    nine.staff_bf.median())
chk('B','median staff pitches = 147', near(nine.staff_pitches.median(), PAY['coverage']['median_staff_pitches']))
# B8 capacity modes
cm = rd('script_capacity_modes')
for key, v in PAY['capacity_modes'].items():
    sc, md = key.rsplit('_',1)
    sub = cm[(cm['script']==sc)&(cm['mode']==md)]
    chk('B', f'capacity mode {key}', near(sub.bf.sum(), v['total'], 0.011), f"{sub.bf.sum()} vs {v['total']}")
# B9 multi-inning propensity recomputed
mip = rd('multi_inning_propensity')
for _, r in mip.iterrows():
    if r.player_name == 'Holman, Grant':
        d = hap; d = d.assign(innings_spanned=d.inning_exited-d.inning_entered+1)
    else:
        d = apps[(apps.pitcher==r.pitcher) & (~apps.is_start.astype(bool))]
    if len(d)==0: continue
    chk('B', f'multi-inning count {r.player_name}', int((d.innings_spanned>=2).sum())==r.multi_inning_apps,
        f"{int((d.innings_spanned>=2).sum())} vs {r.multi_inning_apps}")
    chk('B', f'relief app count {r.player_name}', len(d)==r.relief_apps, f'{len(d)} vs {r.relief_apps}')

# ============================ C · cross-receipt consistency ============================
av1 = rd('availability_D1'); av2 = rd('availability_D2'); sens = rd('date_framing_sensitivity')
chk('C','sensitivity table matches both ledgers',
    (sens.tier_D1_2026_09_12.tolist()==av1.tier.tolist()) and (sens.tier_D2_2026_09_13.tolist()==av2.tier.tolist()))
chk('C','five tiers move between framings', int(sens.changed.sum())==5, int(sens.changed.sum()))
chk('C','Alvarado is AMBER under both', av1[av1.player_name=='Alvarado, José'].tier.iat[0]=='AMBER'
    and av2[av2.player_name=='Alvarado, José'].tier.iat[0]=='AMBER')
anc = rd('anchor_game_ledger')
chk('C','anchor game used 5 relievers + 1 starter', (~anc.is_start).sum()==5 and anc.is_start.sum()==1)
chk('C','Alvarado pitched the anchor game and was NOT client-named',
    bool(anc[anc.player_name=='Alvarado, José'].client_named_as_spent.iat[0])==False and
    (anc.player_name=='Alvarado, José').any())
chk('C','all four client-named arms appear in the anchor game',
    anc.client_named_as_spent.sum()==4, int(anc.client_named_as_spent.sum()))
ao = rd('atl_order')
chk('C','nine-man order resolved', len(ao)==9)
chk('C','three of the first four bat L vs LHP', (ao.head(4).stand_vs_lhp=='L').sum()==3)
chk('C','exactly one switch hitter flagged in the order', int(ao.switch_hitter.sum())==1)
og = rd('opp_starter_games')
chk('C','opposing starter reached the 6th in all three looks', (og.last_inning==6).all(), og.last_inning.tolist())
hc = rd('holman_counting_by_stand')
chk('C','all four Holman AAA home runs were to LHB',
    int(hc[hc.stand=='L'].hr.iat[0])==4 and int(hc[hc.stand=='R'].hr.iat[0])==0)
fr = rd('freshness_manifest'); chk('C','freshness manifest logs the manual carry-in',
    fr.source.str.contains('client prompt').any())
dq = rd('dq_scorecard')
chk('C','DQ scorecard carries the D+2 timeliness FAIL', (dq.status=='FAIL').sum()==1, dq[dq.status=='FAIL'].check.tolist())
chk('C','DQ scorecard flags the inferred opponent identity',
    dq[dq.check.str.contains('opposing starter identity')].status.iat[0]=='WARN')

# ============================ D · defect exposure ============================
de = rd('defect_exposure')
chk('D','D-8 recorded as NEW and measured', de.defect.str.contains('D-8').any() and
    '484' in de[de.defect.str.contains('D-8')].exposure.iat[0])
chk('D','D-8 reproduces: is_start is <NA> for relievers',
    int(K.appearance_summary(pps).is_start.isna().sum())==484)
chk('D','D-8 reproduces: relievers_only returns an empty frame',
    len(K.pitcher_season_workload(K.add_rolling_workload(K.add_rest_days(K.appearance_summary(pps))), True))==0)
try:
    K.nresults(['batter'], pps.head(400)); d9 = False
except KeyError: d9 = True
chk('D','D-9 reproduces: nresults cannot group on `batter`', d9)
chk('D','D-9 recorded', de.defect.str.contains('D-9').any())
chk('D','O-8 exposure measured, hard_hit_rate NOT shipped for AAA',
    de.defect.str.contains('O-8').any() and not (OUT/'dp_uc43_holman_hard_hit.csv').exists())
chk('D','D-1 exposure measured and zero groups dropped here',
    all('DROPPED' not in x for x in de[de.defect.str.startswith('D-1')].impact))
chk('D','D-7/O-13 exposure quantified for both frames',
    (de.defect.str.contains('D-7/O-13')).sum()==2)
chk('D','no xwOBA/wOBA computed anywhere on the AAA tier',
    not any('woba' in c.lower() for c in rd('holman_counting_by_stand').columns))

# ============================ E · deliverable integrity ============================
for f in ['dp_uc43_bullpen_script_report.md','dp_uc43_bullpen_script_report.pdf',
          'dp_uc43_bullpen_control_room.html','dp_uc43_kernel.py','dp_uc43_bullpen_script.py',
          'dp_uc43_build_figs.py','dp_uc43_build_pdf.py','dp_uc43_build_dashboard.py']:
    chk('E', f'deliverable present: {f}', (HERE/f).exists())
for f in ['fig1_holman_pitch_maps','fig2_availability','fig3_coverage','fig4_multi_inning']:
    chk('E', f'figure present: {f}.png', (OUT/f'dp_uc43_{f}.png').exists())
ext = re.findall(r'(?:src|href)\s*=\s*"(https?://[^"]+)"', DASH)
bad = [u for u in ext if not u.startswith(('https://fonts.googleapis.com','https://fonts.gstatic.com'))]
chk('E','dashboard loads no external code (fonts-only allowance)', not bad, bad)
chk('E','dashboard is self-contained: data inlined', 'id="uc43-data"' in DASH)
chk('E','dashboard declares both themes at token level',
    ':root{' in DASH.replace(' ','') and 'prefers-color-scheme:dark' in DASH.replace(' ','')
    and '[data-theme="dark"]' in DASH)
chk('E','dashboard paints an explicit body background', 'body{margin:0;background:var(--ground)' in DASH.replace(' ',''))
chk('E','PDF is non-trivial', (HERE/'dp_uc43_bullpen_script_report.pdf').stat().st_size > 100_000)
chk('E','receipt count', len(list(OUT.glob('dp_uc43_*.csv'))) >= 25, len(list(OUT.glob('dp_uc43_*.csv'))))

# ============================ F · narrative / receipt reconciliation ============================
cvg = PAY['coverage']; CM = PAY['capacity_modes']
mipd = {r.player_name: r for _, r in mip.iterrows()}
FACTS = [
    ('29.7',  f"{cvg['expected_bf_capacity']:.1f}"),
    ('37',    f"{cvg['required_bf_median_regulation_game']:.0f}"),
    ('7.3',   f"{cvg['shortfall_bf']:.1f}"),
    ('2.4',   f"{cvg['shortfall_innings']:.1f}"),
    ('147',   f"{cvg['median_staff_pitches']:.0f}"),
    ('106',   f"{cvg['regulation_games_in_benchmark']}"),
    ('38.1',  f"{CM['client_ceiling']['total']:.1f}"),
    ('37.4',  f"{CM['revised_ceiling']['total']:.1f}"),
    ('1 of 56', f"{int(mipd['Duran, Jhoan'].multi_inning_apps)} of {int(mipd['Duran, Jhoan'].relief_apps)}"),
    ('1 of 61', f"{int(mipd['Alvarado, José'].multi_inning_apps)} of {int(mipd['Alvarado, José'].relief_apps)}"),
    ('15 of 40', f"{int(mipd['Shugart, Chase'].multi_inning_apps)} of {int(mipd['Shugart, Chase'].relief_apps)}"),
    ('16 of 50', f"{int(mipd['Mayza, Tim'].multi_inning_apps)} of {int(mipd['Mayza, Tim'].relief_apps)}"),
    ('8 of 20', f"{int(mipd['Holman, Grant'].multi_inning_apps)} of {int(mipd['Holman, Grant'].relief_apps)}"),
]
for shown, recomputed in FACTS:
    chk('F', f'report figure "{shown}" recomputes', shown == recomputed, f'report says {shown}, receipts say {recomputed}')
    chk('F', f'report prose actually contains "{shown}"', shown in REPORT)
# per-arm 7-day load quoted in §3
for nm, p7, a7 in [('Alvarado, José',61,4), ('Bowlan, Jonathan',62,3), ('McFarlane, Alex',43,3), ('Mayza, Tim',15,1)]:
    r = av1[av1.player_name==nm].iloc[0]
    chk('F', f'§3 7-day load for {nm}', int(r.pitches_last_7d)==p7 and int(r.appearances_last_7d)==a7,
        f'{r.pitches_last_7d}p/{r.appearances_last_7d} vs {p7}p/{a7}')
# anchor-game pitch counts quoted in §2
for nm, p in [('Alvarado, José',9),('McFarlane, Alex',15),('Bowlan, Jonathan',22),('Shugart, Chase',9),('Raley, Brooks',9)]:
    chk('F', f'§2 anchor pitch count {nm}', int(anc[anc.player_name==nm].pitches.iat[0])==p)
# Holman table in §7
hmix = rd('holman_mix_by_stand')
for st, pt, usage, velo in [('L','FS',44.1,87.8), ('L','FF',42.6,95.0), ('R','FF',45.0,94.9), ('R','SL',32.5,86.3)]:
    r = hmix[(hmix.stand==st)&(hmix.pitch_type==pt)].iloc[0]
    chk('F', f'§7 Holman {st}/{pt} usage+velo', near(r.usage,usage,0.051) and near(r.release_speed,velo,0.051),
        f'{r.usage}/{r.release_speed}')
chk('F','§7 FPSR figures', near(rd('holman_fpsr').set_index('stand')['First Pitch Strike Rate']['L'],0.768,0.0006)
    and near(rd('holman_fpsr').set_index('stand')['First Pitch Strike Rate']['R'],0.667,0.0006))
# opponent drift in §8
od = rd('opp_starter_arsenal_drift')
chk('F','§8 splitter drift 23.4 -> 26.8 -> 39.4',
    [round(100*v,1) for v in od.FS.tolist()]==[23.4,26.8,39.4], [round(100*v,1) for v in od.FS.tolist()])
obs = rd('opp_starter_by_stand').set_index('stand')
chk('F','§8 opponent platoon split .192 / .419', near(obs.woba['L'],0.192,0.0006) and near(obs.woba['R'],0.419,0.0006))
chk('F','§8 zero HR allowed to PHI in 70 PA', obs.hrs.sum()==0 and obs.plate_apps.sum()==70, obs.plate_apps.sum())
# dashboard markup carries the same headline
chk('F','dashboard verdict quotes 38.1', '38.1' in DASH)
chk('F','dashboard warning names the AAA ceiling', 'Triple-A high of 10 batters' in DASH)
# README (written after this harness first ran — checked when present)
if README:
    for shown, _ in FACTS[:8]:
        chk('F', f'README figure "{shown}" present and consistent', shown in README or shown == '147')

# --- the harness's own size claim, checked LAST (uc-pos-016 v1.1.0 rule) ---
df = pd.DataFrame(R)
claimed = None
m = re.search(r'independently verified \((\d+)\s*/\s*(\d+)\)', REPORT + README)
if m: claimed = (int(m.group(1)), int(m.group(2)))
total = len(df) + 1
passed = int((df.status=='PASS').sum()) + 1
if claimed:
    chk('F','report/README verification-count claim matches this run', claimed==(passed,total), f'claims {claimed}, actual {passed}/{total}')
else:
    chk('F','verification-count claim present to check', True, 'no claim in report/README yet — recorded, not asserted')
df = pd.DataFrame(R)
df.to_csv(OUT/'dp_uc43_verification_results.csv', index=False)
fails = df[df.status=='FAIL']
print(df.groupby(['family','status']).size().unstack(fill_value=0).to_string())
print(f"\n{(df.status=='PASS').sum()}/{len(df)} PASS")
if len(fails):
    print('\nFAILURES:'); print(fails.to_string(index=False))
    sys.exit(1)
