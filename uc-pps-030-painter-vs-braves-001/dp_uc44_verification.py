"""
dp_uc44_verification.py — independent verification for UC #44 / uc-pps-030.

Recomputes from the parquet rather than trusting the build's receipts, then
reconciles every number the report and the card publish.

Families
  A  entity lock, scope, freshness
  B  SG-1 grade transform — mathematical correctness of the 20-80 identity
  C  SG-2 population construction and floor rules
  D  receipt internal consistency
  E  narrative reconciliation — every number asserted in the report markdown
  F  known-defect exposure claims
  G  deliverable integrity (figures, PDF, dashboard, receipts present)
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats as sps
import dp_uc44_kernel as K

HERE = Path(__file__).parent; OUT = HERE/'out'
PASS, FAIL, LOG = 0, 0, []
def ck(fam, name, cond, detail=''):
    global PASS, FAIL
    ok = bool(cond)
    PASS, FAIL = PASS+ok, FAIL+(not ok)
    LOG.append(f"[{fam}] {'PASS' if ok else 'FAIL'}  {name}" + (f'  — {detail}' if detail else ''))
    return ok
def close(a, b, tol=5e-4): return (a is not None and b is not None and abs(float(a)-float(b)) <= tol)

pay  = json.loads((OUT/'dp_uc44_payload.json').read_text())
rep  = (HERE/'dp_uc44_painter_vs_braves_report.md').read_text(encoding='utf-8')
gr   = pd.read_csv(OUT/'dp_uc44_grades.csv')
plat = pd.read_csv(OUT/'dp_uc44_platoon_splits.csv')
sl   = pd.read_csv(OUT/'dp_uc44_start_log.csv')
mbs  = pd.read_csv(OUT/'dp_uc44_mix_by_stand.csv')
ffl  = pd.read_csv(OUT/'dp_uc44_ff_location_profile.csv')
rec  = pd.read_csv(OUT/'dp_uc44_notecard_reconciliation.csv')
turn = pd.read_csv(OUT/'dp_uc44_arsenal_turnover_detail.csv')
sc   = pd.read_csv(OUT/'dp_uc44_splitter_vs_changeup.csv')
biz  = pd.read_csv(OUT/'dp_uc44_breaking_izr_pooled.csv')
lin  = pd.read_csv(OUT/'dp_uc44_atl_lineup_vs_phi.csv')
h2h  = pd.read_csv(OUT/'dp_uc44_h2h_atl.csv')
dex  = pd.read_csv(OUT/'dp_uc44_defect_exposure.csv')

# ---- independent reload --------------------------------------------------
allp = K.load_phils(tuple(range(2015,2027)), regular_only=True)
ap   = allp[(allp.game_year==2026)&(allp.phillies_role=='pitching')&(allp.pitcher==K.SUBJECT_ID)].copy()
ap['window'] = np.where(ap.game_date>=K.OPTION_RETURN_DATE,'Post-Option','Pre-Option')
PRE, POST = ap[ap.window=='Pre-Option'], ap[ap.window=='Post-Option']
def wr(d):
    s=int(d.description.isin(K.SWINGS).sum()); w=int(d.description.isin(K.WHIFFS).sum())
    return w, s, (w/s if s else np.nan)

# ========================= A · lock / scope / freshness ====================
ck('A','entity lock resolves to one player', ap.player_name.nunique()==1, str(ap.player_name.unique()))
ck('A','entity lock is Painter', ap.player_name.iloc[0]=='Painter, Andrew')
ck('A','no name filter anywhere in the build source',
   'player_name ==' not in (HERE/'dp_uc44_painter_vs_braves.py').read_text())
ck('A','regular season only', (ap.game_type=='R').all())
ck('A','no duplicate pitch rows', ap.duplicated(subset=['game_pk','at_bat_number','pitch_number']).sum()==0)
ck('A','anchor date matches the pin', allp[allp.game_year==2026].game_date.max()==K.ANCHOR_GAME_DATE)
ck('A','target game is D+1 of the anchor',
   pd.Timestamp(K.TARGET_GAME_DATE)-pd.Timestamp(K.ANCHOR_GAME_DATE)==pd.Timedelta(days=1))
ck('A','windows partition the season', len(PRE)+len(POST)==len(ap))
ck('A','post-option window is 8 starts', POST.game_date.nunique()==8, str(POST.game_date.nunique()))
ck('A','pre-option window is 14 starts', PRE.game_date.nunique()==14)
ck('A','post-option pitch count 720', len(POST)==720, str(len(POST)))
ck('A','post-option PA 185', int(POST.events.notna().sum())==185)
ck('A','opponent starter id is Holmes lock', K.OPP_STARTER_ID==656550)
ck('A','ATL game_pk list has 12 games', len(set(K.ATL_GAME_PKS))==12)

# ========================= B · SG-1 transform correctness ==================
rng = np.random.default_rng(44)
popn = rng.normal(10, 2, 4000)
ck('B','grade at the population mean is 50', K.scouting_grade(10.0, popn)['grade']==50.0)
g1 = K.scouting_grade(float(popn.mean()+popn.std(ddof=1)), popn)
ck('B','+1 SD is a 60', g1['grade']==60.0, f"z={g1['z']:.3f}")
g2 = K.scouting_grade(float(popn.mean()-2*popn.std(ddof=1)), popn)
ck('B','-2 SD is a 30', g2['grade']==30.0)
ck('B','grade clips at 80', K.scouting_grade(float(popn.mean()+9*popn.std(ddof=1)), popn)['grade']==80.0)
ck('B','grade clips at 20', K.scouting_grade(float(popn.mean()-9*popn.std(ddof=1)), popn)['grade']==20.0)
gi = K.scouting_grade(float(popn.mean()+popn.std(ddof=1)), popn, higher_is_better=False)
ck('B','direction flip inverts the grade', gi['grade']==40.0)
ck('B','NaN subject returns NaN grade', pd.isna(K.scouting_grade(np.nan, popn)['grade']))
ck('B','population under 5 returns NaN', pd.isna(K.scouting_grade(1.0, [1,2,3])['grade']))
ck('B','zero-variance population returns NaN', pd.isna(K.scouting_grade(1.0, [2.0]*30)['grade']))
ck('B','rounding is half-up not banker\'s', K._round5(52.5)==55.0 and K._round5(47.5)==50.0)
ck('B','z-grade and rank-grade agree on a normal population',
   abs(K.scouting_grade(13.0, popn)['divergence'])<=5)
ck('B','divergence flag fires at 10 and not at 9',
   K.grade_divergence_flag(10)=='SKEW' and K.grade_divergence_flag(-11)=='SKEW'
   and K.grade_divergence_flag(9)=='' and K.grade_divergence_flag(np.nan)=='')
sk = rng.lognormal(0, 1, 6000)
gs = K.scouting_grade(0.20, sk)      # left tail of a right-skewed population
ck('B','skewed population trips the divergence flag',
   K.grade_divergence_flag(gs['divergence'])=='SKEW', f"div={gs['divergence']}")
ck('B','pitch_grade is the mean of stuff and command', K.pitch_grade(50,60)==55.0)
ck('B','pitch_grade is NaN when either input is NaN', pd.isna(K.pitch_grade(np.nan,60)))
ck('B','grade_label vocabulary is monotone',
   [K.grade_label(g) for g in [75,65,57,50,42,35,25]] ==
   ['plus-plus','plus','above average','average','below average','well below average','poor'])

# ========================= C · SG-2 population rules ======================
for r in gr.itertuples():
    pop = K.benchmark_population(allp, r.pitch_type, 'R')
    ck('C', f'{r.pitch_type} population size reproduces', len(pop)==r.pop_n, f'{len(pop)} vs {r.pop_n}')
    ck('C', f'{r.pitch_type} floor rule honoured',
       int(pop.pop_floor.iloc[0])==r.pop_floor and
       (r.pop_floor==K.GRADE_FLOOR_PRIMARY or len(pop)>=1))
    ck('C', f'{r.pitch_type} THIN flag set iff floor was lowered',
       bool(pop.thin.iloc[0])==(int(pop.pop_floor.iloc[0])==K.GRADE_FLOOR_FALLBACK)==bool(r.pop_thin))
    ck('C', f'{r.pitch_type} every population member clears the floor', (pop.n>=r.pop_floor).all())
    ck('C', f'{r.pitch_type} population is RHP only',
       allp[(allp.pitch_type==r.pitch_type)&(allp.pitcher.isin(pop.pitcher))].p_throws.eq('R').all()
       if len(pop) else True)
ck('C','sweeper is the only THIN population', list(gr[gr.pop_thin].pitch_type)==['ST'],
   str(list(gr[gr.pop_thin].pitch_type)))
ck('C','pitcher-season grain: population has no duplicate (year, pitcher)',
   not K.benchmark_population(allp,'FF','R').duplicated(subset=['game_year','pitcher']).any())
ck('C','population spans more than one club',
   allp[allp.p_throws=='R'].phillies_role.nunique()==2)
# normality claims made in the report
NORM_WHIFF = {'FF':.0616,'SL':.2102,'ST':.0153,'CU':.2767,'CH':.1077,'SI':.2870}
NORM_IZR   = {'FF':.0777,'SL':.3099,'ST':.2099,'CU':.0591,'CH':.0064,'SI':.0009}
for pt in NORM_WHIFF:
    pop = K.benchmark_population(allp, pt, 'R')
    pw = sps.shapiro(pop.whiff_rate.dropna())[1]; pz = sps.shapiro(pop.in_zone_rate.dropna())[1]
    ck('C', f'{pt} whiff-rate Shapiro p reproduces', close(pw, NORM_WHIFF[pt], 1e-3), f'{pw:.4f}')
    ck('C', f'{pt} in-zone Shapiro p reproduces', close(pz, NORM_IZR[pt], 1e-3), f'{pz:.4f}')
ck('C','report names exactly the three populations that fail normality',
   [pt for pt in NORM_WHIFF if NORM_WHIFF[pt] <= .05]==['ST'] and
   sorted(pt for pt in NORM_IZR if NORM_IZR[pt] <= .05)==['CH','SI'] and
   'fails for the sweeper' in rep and 'fails for the changeup' in rep)
_divs = []
for r in gr.itertuples():
    _pop = K.benchmark_population(allp, r.pitch_type, 'R')
    _divs.append(K.scouting_grade(wr(POST[POST.pitch_type==r.pitch_type])[2], _pop.whiff_rate)['divergence'])
    _divs.append(K.scouting_grade((POST[POST.pitch_type==r.pitch_type].zone<=9).mean(), _pop.in_zone_rate)['divergence'])
ck('C','11 of 12 grades identical z-derived and rank-derived',
   sum(1 for d in _divs if close(d, 0.0))==11, str([round(d,1) for d in _divs]))
ck('C','the one divergence is slider command at 5 points',
   close(K.scouting_grade((POST[POST.pitch_type=='SL'].zone<=9).mean(),
         K.benchmark_population(allp,'SL','R').in_zone_rate)['divergence'], -5.0)
   and 'slider command' in rep)
ck('C','no grade trips the 10-point SKEW flag',
   all(K.grade_divergence_flag(d)=='' for d in _divs)
   and (gr.stuff_flag.fillna('')=='').all() and (gr.command_flag.fillna('')=='').all())

# ========================= D · receipt consistency ========================
for r in gr.itertuples():
    d = POST[POST.pitch_type==r.pitch_type]
    w_, s_, x_ = wr(d)
    ck('D', f'{r.pitch_type} n reproduces', len(d)==r.n)
    ck('D', f'{r.pitch_type} whiff reproduces', close(x_, r.whiff_rate))
    ck('D', f'{r.pitch_type} in-zone reproduces', close((d.zone<=9).mean(), r.in_zone_rate))
    ck('D', f'{r.pitch_type} velo reproduces', close(d.release_speed.mean(), r.velo, 5e-3))
    ck('D', f'{r.pitch_type} usage reproduces', close(len(d)/len(POST), r.usage))
    pop = K.benchmark_population(allp, r.pitch_type, 'R')
    gg = K.scouting_grade(x_, pop.whiff_rate)
    gated = (len(d) >= K.SUBJECT_PITCH_FLOOR) and (s_ >= K.SUBJECT_SWING_FLOOR)
    ck('D', f'{r.pitch_type} stuff grade reproduces',
       (pd.isna(r.stuff_grade) and not gated) or (gated and gg['grade']==r.stuff_grade))
    ck('D', f'{r.pitch_type} pitch grade = mean(stuff, command)',
       (pd.isna(r.pitch_grade) and (pd.isna(r.stuff_grade) or pd.isna(r.command_grade)))
       or close(K.pitch_grade(r.stuff_grade, r.command_grade), r.pitch_grade))
ck('D','grade gates: nothing under the pitch floor is graded',
   gr[gr.n < K.SUBJECT_PITCH_FLOOR].pitch_grade.isna().all())
ck('D','curveball is ungraded', pd.isna(gr[gr.pitch_type=='CU'].pitch_grade.iloc[0]))
ck('D','usage sums to 1 across the arsenal', close(gr.usage.sum(), 1.0, 1e-3))
ck('D','arsenal grade is the usage-weighted pitch grade',
   close(np.average(gr.dropna(subset=['pitch_grade']).pitch_grade,
                    weights=gr.dropna(subset=['pitch_grade']).usage),
         pay['arsenal_grade']['raw'], 1e-3))
for r in plat.itertuples():
    d = ap[ap.stand==r.stand] if r.window=='Full 2026' else ap[(ap.window==r.window)&(ap.stand==r.stand)]
    w_, s_, x_ = wr(d)
    ck('D', f'platoon {r.window}/{r.stand} pitches', len(d)==r.pitches)
    ck('D', f'platoon {r.window}/{r.stand} PA', int(d.events.notna().sum())==r.pa)
    ck('D', f'platoon {r.window}/{r.stand} whiff', close(x_, r.whiff_rate))
    ck('D', f'platoon {r.window}/{r.stand} xwOBA', close(d.estimated_woba_using_speedangle.mean(), r.xwoba))
ck('D','start log covers every start', len(sl)==ap.game_date.nunique())
ck('D','start log BF sums to season PA', int(sl.bf.sum())==int(ap.events.notna().sum()))
ck('D','start log pitches sum to season pitches', int(sl.pitches.sum())==len(ap))
ck('D','mix_by_stand n sums to window pitches per stand',
   all(close(mbs[(mbs.window==w)&(mbs.stand==s)].n.sum(),
             len(ap[(ap.window==w)&(ap.stand==s)]) if w!='Full 2026' else len(ap[ap.stand==s]), 0.5)
       for w in ['Pre-Option','Post-Option','Full 2026'] for s in ['L','R']))
ck('D','turnover detail usages each sum to 1',
   close(turn.before_usage.sum(),1.0,1e-3) and close(turn.after_usage.sum(),1.0,1e-3))
ck('D','AR-1 index = added_share + dropped_share',
   close(pay['turnover']['index'], pay['turnover']['added_share']+pay['turnover']['dropped_share']))
ck('D','AR-1 added is exactly [CH]', pay['turnover']['added']==['CH'])
ck('D','AR-1 dropped is exactly [FS]', pay['turnover']['dropped']==['FS'])
ck('D','lineup PA descend', (lin.sort_values('pa',ascending=False).pa.values==lin.pa.values).all())
ck('D','H2H PA total is 47', int(h2h.pa.sum())==47)
ck('D','H2H comes only from the two April starts',
   sorted(ap[ap.game_pk.isin(K.ATL_GAME_PKS)].game_date.unique())==['2026-04-19','2026-04-24'])

# ========================= E · narrative reconciliation ===================
def in_report(s): return s in rep
post_ff = POST[POST.pitch_type=='FF']; pre_ff = PRE[PRE.pitch_type=='FF']
_, _, ffw = wr(post_ff)
ck('E','report FF whiff .218', in_report('.218') and close(ffw, .218, 1e-3))
ck('E','report FF ride 17.0"', in_report('+17.0"') and close(post_ff.pfx_z.mean()*12, 17.0, .05))
ck('E','report FF elevation .349', in_report('.349') and close((post_ff.plate_z>post_ff.sz_top).mean(), .349, 1e-3))
ck('E','report FF pre elevation .307', close((pre_ff.plate_z>pre_ff.sz_top).mean(), .307, 1e-3))
ck('E','report FF in-zone .422', in_report('.422') and close((post_ff.zone<=9).mean(), .422, 1e-3))
ck('E','report FF pre whiff .106', close(wr(pre_ff)[2], .106, 1e-3))
fsl = ap[(ap.pitch_type=='FS')&(ap.stand=='L')]; w_,s_,x_ = wr(fsl)
ck('E','report splitter-vs-LHB .395 on 76 swings', in_report('.395') and close(x_,.395,1e-3) and s_==76)
ck('E','report zero splitters post-option', (POST.pitch_type=='FS').sum()==0 and in_report('zero splitters'))
ck('E','report last splitter date is 2026-06-17',
   ap[ap.pitch_type=='FS'].game_date.max()=='2026-06-17' and in_report('06-17'))
chl = POST[(POST.pitch_type=='CH')&(POST.stand=='L')]; w_,s_,x_ = wr(chl)
ck('E','report changeup-vs-LHB .301 on 73 swings', in_report('.301') and close(x_,.301,1e-3) and s_==73)
ck('E','report CH xwOBA .160', in_report('.160') and close(POST[POST.pitch_type=='CH'].estimated_woba_using_speedangle.mean(), .160, 1e-3))
ck('E','report CH-vs-LHB xwOBA .178', in_report('.178') and close(chl.estimated_woba_using_speedangle.mean(), .178, 1e-3))
chr_ = POST[(POST.pitch_type=='CH')&(POST.stand=='R')]; w_,s_,x_ = wr(chr_)
ck('E','report CH-vs-RHB .452 whiff / .130 xwOBA',
   in_report('.452') and close(x_,.452,1e-3) and close(chr_.estimated_woba_using_speedangle.mean(),.130,1e-3))
stl = POST[(POST.pitch_type=='ST')&(POST.stand=='L')]; w_,s_,x_ = wr(stl)
ck('E','report sweeper-vs-LHH .645 zone / .200 whiff / .523 xwOBA on 9 PA',
   in_report('64.5%') and close((stl.zone<=9).mean(),.645,1e-3) and close(x_,.200,1e-3)
   and close(stl.estimated_woba_using_speedangle.mean(),.523,1e-3)
   and int(stl.estimated_woba_using_speedangle.notna().sum())==9)
ck('E','report platoon whiff .322 / .238',
   close(wr(POST[POST.stand=='R'])[2],.322,1e-3) and close(wr(POST[POST.stand=='L'])[2],.238,1e-3))
kr = lambda d: d.events.isin(['strikeout','strikeout_double_play']).sum()/d.events.notna().sum()
ck('E','report K rate 29.7% RHH / 18.1% LHH',
   close(kr(POST[POST.stand=='R']),.297,1e-3) and close(kr(POST[POST.stand=='L']),.181,1e-3))
z,p_ = K.two_prop_z(*wr(POST[POST.stand=='L'])[:2][::-1][::-1], *wr(POST[POST.stand=='R'])[:2])
zz = K.two_prop_z(wr(POST[POST.stand=='L'])[0], wr(POST[POST.stand=='L'])[1],
                  wr(POST[POST.stand=='R'])[0], wr(POST[POST.stand=='R'])[1])
ck('E','report platoon z=-1.78 p=0.075', close(zz[0],-1.78,5e-3) and close(zz[1],.075,1e-3))
zf = K.two_prop_z(30,76,22,73)
ck('E','report FS-vs-CH lefty z=1.20 p=0.23', close(zf[0],1.20,5e-3) and close(zf[1],.232,1e-3))
hou = ap[ap.game_date=='2026-09-08']
ck('E','report HOU 27 BF / 6 K / 2 BB / 2 HR',
   int(hou.events.notna().sum())==27 and int(hou.events.isin(['strikeout','strikeout_double_play']).sum())==6
   and int((hou.events=='walk').sum())==2 and int((hou.events=='home_run').sum())==2)
ck('E','report HOU .438 xwOBA / .550 xwOBAcon',
   in_report('.438') and close(hou.estimated_woba_using_speedangle.mean(),.438,1e-3)
   and close(hou[hou.type=='X'].estimated_woba_using_speedangle.mean(),.550,1e-3))
ck('E','report HOU hard-hit 8 of 19 tracked',
   int(((hou.launch_speed>=95)&(hou.type=='X')).sum())==8 and int(((hou.type=='X')&hou.launch_speed.notna()).sum())==19)
ck('E','report "two starts over .400 are the only two with 2+ HR"',
   set(sl[(sl.window=='Post-Option')&(sl.xwoba>=.400)].game_date)
   == set(sl[(sl.window=='Post-Option')&(sl.hr>=2)].game_date))
ck('E','report 4 of 5 post-option HR came in those two starts',
   int(sl[(sl.window=='Post-Option')&(sl.hr>=2)].hr.sum())==4 and int(sl[sl.window=='Post-Option'].hr.sum())==5)
ck('E','report breaking IZR .477 and grade 55',
   close(biz[biz.window=='Full 2026'].in_zone_rate.iloc[0],.477,1e-3)
   and biz[biz.window=='Full 2026'].grade.iloc[0]==55.0 and in_report('grade 55'))
ck('E','report efficiency 90.0 pitches / 23.1 BF per start',
   close(len(POST)/8, 90.0, .05) and close(POST.events.notna().sum()/8, 23.1, .05))
ck('E','report FPSR .612 -> .638',
   close((PRE[PRE.pitch_number==1].type!='B').mean(),.612,1e-3)
   and close((POST[POST.pitch_number==1].type!='B').mean(),.638,1e-3))
ck('E','report 6 of Atlanta\'s 9 most-used bats are LHH',
   int((lin[lin.pa>=18].head(9).stand=='L').sum())==6 and 'six hit left-handed' in rep,
   str(int((lin[lin.pa>=18].head(9).stand=='L').sum())))
ck('E','report Acuna .447 / Harris .436 / Riley .374',
   close(lin[lin.name=='Ronald Acuña Jr.'].xwoba.iloc[0],.447,1e-3)
   and close(lin[lin.name=='Michael Harris II'].xwoba.iloc[0],.436,1e-3)
   and close(lin[lin.name=='Austin Riley'].xwoba.iloc[0],.374,1e-3))
ck('E','report Holmes 260 pitches / 69 PA / .372 xwOBA',
   pay['holmes']['pitches']==260 and pay['holmes']['pa']==69 and close(pay['holmes']['xwoba'],.372,1e-3))
ck('E','report Holmes SL+FF = 87% vs RHH',
   close(sum(m['usage_vs_rhb'] for m in pay['holmes']['mix'] if m['pitch_type'] in ('SL','FF')), .871, 2e-3))
ck('E','report league FS share did not fall (4.1% Jun -> 5.4% Sep)',
   close(pay['tag_drift']['fs_share_jun'],.0414,1e-3) and close(pay['tag_drift']['fs_share_sep'],.0539,1e-3)
   and pay['tag_drift']['verdict']=='pitcher decision')
ck('E','every reconciliation row reconciles', all('RECONCILES' in v or 'Confirmed' in v or 'GRADED' in v
                                                   for v in rec.verdict))
grpre_ = pd.read_csv(OUT/'dp_uc44_grades_pre_option.csv').dropna(subset=['pitch_grade'])
ck('E','report arsenal grade 50 post / 45 pre',
   pay['arsenal_grade']['value']==50.0
   and K._round5(np.average(grpre_.pitch_grade, weights=grpre_.usage))==45.0
   and in_report('**Arsenal grade: 50**, covering 98%') and in_report('up from **45**'))
ck('E','report turnover index 0.37', close(pay['turnover']['index'],.366,5e-3) and in_report('0.37'))
ck('E','report H2H turnover 0.33', close(pay['h2h']['turnover_vs_today']['index'],.3278,1e-3) and in_report('0.33'))
ck('E','report max H2H PA for one hitter is 7', pay['h2h']['max_pa_single_hitter']==7 and in_report('7 PA'))

# ========================= F · defect exposure ============================
ck('F','D-7/O-13 claim: zero null zone in the graded window',
   (int(POST.zone.isna().sum())==0) and (dex[dex.defect=='D-7/O-13'].exposed.iloc[0]=='NO'))
ck('F','O-8 claim: every post-option BIP is tracked',
   int(((POST.type=='X')&POST.launch_speed.isna()).sum())==0
   and dex[dex.defect=='O-8'].exposed.iloc[0]=='NO')
ck('F','O-5 claim: exactly one truncated_pa',
   int((POST.events=='truncated_pa').sum())==1 and dex[dex.defect=='O-5'].exposed.iloc[0]=='YES')
kwr = K.whiff_rate(['pitch_type'], POST)
ck('F','D-1 claim: kernel whiff_rate drops no post-option pitch type',
   set(kwr.pitch_type)==set(POST.pitch_type.unique())
   and dex[dex.defect=='D-1/D-2'].exposed.iloc[0]=='NO')
ck('F','D-1 still reproduces as a live defect on a zero-whiff group',
   'CU' not in set(K.whiff_rate(['pitch_type'], POST[POST.stand=='R']).pitch_type))
ck('F','xwOBA field is PA-level, not contact-level',
   close(POST[POST.events=='strikeout'].estimated_woba_using_speedangle.mean(), 0.0)
   and POST[POST.events=='walk'].estimated_woba_using_speedangle.mean() > 0.6)
ck('F','arm_angle descope is warranted (>50% null)', POST.arm_angle.isna().mean() > 0.5)
ck('F','AAA rows carry no wOBA weight columns', 'wBB' not in K.load_lhv(2026).columns)

# ========================= G · deliverables ==============================
must = ['dp_uc44_fig1_notecard.png','dp_uc44_fig2_arsenal_turnover.png','dp_uc44_fig3_grade_shift.png',
        'dp_uc44_fig4_ff_trade.png','dp_uc44_fig5_start_log.png','dp_uc44_payload.json',
        'dp_uc44_grades.csv','dp_uc44_platoon_splits.csv','dp_uc44_start_log.csv',
        'dp_uc44_dq_scorecard.csv','dp_uc44_defect_exposure.csv','dp_uc44_freshness_manifest.csv',
        'dp_uc44_notecard_reconciliation.csv','dp_uc44_arsenal_turnover.csv','dp_uc44_tag_drift.csv',
        'dp_uc44_mix_by_stand.csv','dp_uc44_benchmark_population_moments.csv','dp_uc44_holmes_profile.csv',
        'dp_uc44_breaking_izr_pooled.csv','dp_uc44_ff_location_profile.csv','dp_uc44_efficiency.csv',
        'dp_uc44_pitch_map_centroids.csv','dp_uc44_atl_lineup_vs_phi.csv','dp_uc44_h2h_atl.csv',
        'dp_uc44_grades_pre_option.csv','dp_uc44_pitch_locations_post.csv','dp_uc44_splitter_vs_changeup.csv',
        'dp_uc44_arsenal_turnover_detail.csv','dp_uc44_pitch_map_centroids_pre.csv']
for f in must:
    ck('G', f'receipt present: {f}', (OUT/f).exists())
for f in ['dp_uc44_painter_vs_braves_report.md','dp_uc44_painter_vs_braves_report.pdf',
          'dp_uc44_painter_scouting_card.html','dp_uc44_kernel.py','dp_uc44_painter_vs_braves.py',
          'dp_uc44_build_figs.py','dp_uc44_build_pdf.py','dp_uc44_build_dashboard.py']:
    ck('G', f'deliverable present: {f}', (HERE/f).exists())
ck('G','PDF is non-trivial', (HERE/'dp_uc44_painter_vs_braves_report.pdf').stat().st_size > 200_000)
dash = (HERE/'dp_uc44_painter_scouting_card.html').read_text()
ck('G','dashboard is self-contained (no external fetch)',
   not re.search(r'src=["\']https?://', dash) and not re.search(r'<link[^>]+https?://', dash))
ck('G','every figure the report references exists',
   all((HERE/m).exists() for m in re.findall(r'!\[[^\]]*\]\((out/[^)]+)\)', rep)))
ck('G','report declares the entity lock', 'pitcher == 691725' in rep)
ck('G','report declares the population', 'Phillies-schedule population' in rep)
ck('G','report prints denominators on the small cells', 'on 9 tracked plate appearances' in rep)

# ========================= report =========================================
(OUT/'dp_uc44_verification_log.txt').write_text('\n'.join(LOG)+f'\n\n{PASS} PASS · {FAIL} FAIL\n')
print('\n'.join(l for l in LOG if 'FAIL' in l) or '(no failures)')
print(f'\n{PASS} PASS · {FAIL} FAIL  ->  out/dp_uc44_verification_log.txt')
sys.exit(1 if FAIL else 0)
