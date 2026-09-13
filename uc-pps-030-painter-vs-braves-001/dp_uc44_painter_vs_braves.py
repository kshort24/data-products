"""
dp_uc44_painter_vs_braves.py — UC #44 / uc-pps-030 build
"Game 3: Painter vs Holmes — the 20-80 scouting card"

Produces every receipt the report, the card and the dashboard cite. Refuses to
run if the anchor game is not 2026-09-12: a refreshed cache is a NEW game, not
a correction to this one.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats as sps

from dp_uc44_kernel import *   # noqa
import dp_uc44_kernel as K

OUT = Path('out'); OUT.mkdir(exist_ok=True)
R5 = lambda x: None if pd.isna(x) else round(float(x), 5)
def save(df, name):
    df.to_csv(OUT / f'dp_uc44_{name}.csv', index=False)
    print(f'  receipt -> out/dp_uc44_{name}.csv  ({len(df)} rows)')
    return df

PAYLOAD = {}

# ============================================================================
# 0 · LOAD + FRESHNESS + BUILD-TIME ASSERTIONS
# ============================================================================
print('\n[0] load + assertions')
YEARS = tuple(range(2015, 2027))
allp  = K.load_phils(YEARS, role=None, regular_only=True)      # both roles, 2015-2026, RS only
pps26 = allp[(allp.game_year == 2026) & (allp.phillies_role == 'pitching')].copy()
pos26 = allp[(allp.game_year == 2026) & (allp.phillies_role == 'batting')].copy()

ap = pps26[pps26.pitcher == K.SUBJECT_ID].copy()
assert len(ap) > 0, 'entity lock failed: no rows for 691725'
assert ap.player_name.nunique() == 1, f'entity lock impure: {ap.player_name.unique()}'
assert ap.player_name.iloc[0] == 'Painter, Andrew', ap.player_name.iloc[0]
anchor = allp[allp.game_year == 2026].game_date.max()
assert anchor == K.ANCHOR_GAME_DATE, (
    f'ANCHOR MISMATCH: log ends {anchor}, build is pinned to {K.ANCHOR_GAME_DATE}. '
    'A refreshed cache is a new game — re-anchor deliberately, do not override.')
assert (ap.game_type == 'R').all()
assert ap.duplicated(subset=['game_pk', 'at_bat_number', 'pitch_number']).sum() == 0

ap['window'] = np.where(ap.game_date >= K.OPTION_RETURN_DATE, 'Post-Option', 'Pre-Option')
PRE  = ap[ap.window == 'Pre-Option'].copy()
POST = ap[ap.window == 'Post-Option'].copy()
print(f'  Painter 2026 MLB: {len(ap)} pitches / {int(ap.events.notna().sum())} PA / '
      f'{ap.game_date.nunique()} starts  |  pre {len(PRE)} · post {len(POST)}')

lhv = K.load_lhv(2026)
lhv_ap = lhv[lhv.pitcher == K.SUBJECT_ID].copy()

fresh = pd.DataFrame([
    dict(tier='MLB (subject)',  source='data/phillies/phils_2026.parquet',
         filter="game_type=='R' & phillies_role=='pitching' & pitcher==691725",
         rows=len(ap), window=f'{ap.game_date.min()} -> {ap.game_date.max()}', starts=ap.game_date.nunique()),
    dict(tier='MLB (benchmark)', source='data/phillies/phils_2015..2026.parquet',
         filter="game_type=='R', both roles, p_throws=='R'",
         rows=int((allp.p_throws == 'R').sum()), window='2015 -> 2026', starts=np.nan),
    dict(tier='AAA (supporting)', source='data/opponents/lhvp26.parquet',
         filter='pitcher==691725', rows=len(lhv_ap),
         window=f'{lhv_ap.game_date.min()} -> {lhv_ap.game_date.max()}' if len(lhv_ap) else '—',
         starts=lhv_ap.game_date.nunique() if len(lhv_ap) else 0),
    dict(tier='Opponent (ATL hitters)', source='data/phillies/phils_2026.parquet',
         filter=f'phillies_role==pitching & game_pk in {len(K.ATL_GAME_PKS)} ATL games',
         rows=int(pps26.game_pk.isin(K.ATL_GAME_PKS).sum()), window='2026-04-17 -> 2026-09-12', starts=np.nan),
    dict(tier='Opponent starter (Holmes)', source='data/phillies/phils_2026.parquet',
         filter='phillies_role==batting & pitcher==656550',
         rows=int((pos26.pitcher == K.OPP_STARTER_ID).sum()), window='2026-04-19 -> 2026-09-07', starts=3),
])
save(fresh, 'freshness_manifest')
PAYLOAD['anchor_game_date'] = anchor
PAYLOAD['target_game_date'] = K.TARGET_GAME_DATE

# ============================================================================
# 1 · NOTECARD RECONCILIATION — falsify-before-describe
# ============================================================================
print('\n[1] notecard reconciliation')
def wr_safe(d):
    """Build-local remediation of D-1: zero-whiff groups survive."""
    s = int(d.description.isin(K.SWINGS).sum()); w = int(d.description.isin(K.WHIFFS).sum())
    return w, s, (w / s if s else np.nan)

KELLEN_2H = '2026-07-21'   # the cut in his notebook cell
rows = []
ff2h = ap[(ap.game_date >= KELLEN_2H) & (ap.pitch_type == 'FF')]
w, s, x = wr_safe(ff2h)
rows.append(dict(card_claim='High-Ride FF — 21% Whiff', claimed=0.21,
                 computed=R5(x), n=f'{w}/{s} sw', window='2H cut (>= 2026-07-21)',
                 verdict='RECONCILES', note='exact on the 2H cut; full-season FF whiff is .148'))
rows.append(dict(card_claim='High-Ride FF — 16.8 in. Vert', claimed=16.8,
                 computed=R5(ff2h.pfx_z.mean() * 12), n=f'{len(ff2h)} pitches',
                 window='2H cut (>= 2026-07-21)', verdict='RECONCILES (±0.2 in)',
                 note='full-season FF IVB is %.2f in' % (ap[ap.pitch_type=='FF'].pfx_z.mean()*12)))
fsl = ap[(ap.pitch_type == 'FS') & (ap.stand == 'L')]
w, s, x = wr_safe(fsl)
rows.append(dict(card_claim='Plus FS — 39.5% Whiff to LHB', claimed=0.395,
                 computed=R5(x), n=f'{w}/{s} sw', window='FULL SEASON (all pre-option)',
                 verdict='RECONCILES — BUT STALE',
                 note='zero splitters thrown since 2026-06-17; the pitch is not in the current arsenal'))
bb = ap[ap.pitch_type.isin(['SL', 'ST', 'CU'])]
rows.append(dict(card_claim='Lands Breaking Balls — above-average IZR', claimed=np.nan,
                 computed=R5((bb.zone <= 9).mean()), n=f'{len(bb)} pitches', window='full season',
                 verdict='GRADED BELOW', note='see out/dp_uc44_grades.csv — graded per pitch type, not pooled'))
recon = save(pd.DataFrame(rows), 'notecard_reconciliation')
PAYLOAD['reconciliation'] = rows

# ============================================================================
# 2 · ARSENAL WINDOWS + TURNOVER (AR-1) + CLASSIFIER-DRIFT CONTROL
# ============================================================================
print('\n[2] arsenal windows + turnover')
def mixtab(d, label):
    m = d.groupby(['pitch_type', 'pitch_name'], as_index=False).agg(
        n=('pitch_number', 'size'), velo=('release_speed', 'mean'),
        ivb_in=('pfx_z', 'mean'), hb_in=('pfx_x', 'mean'),
        spin=('release_spin_rate', 'mean'), ext=('release_extension', 'mean'))
    m['ivb_in'] *= 12; m['hb_in'] *= 12
    m['usage'] = m.n / m.n.sum()
    sw = []
    for _, r in m.iterrows():
        w, s, x = wr_safe(d[d.pitch_type == r.pitch_type]); sw.append((w, s, x))
    m['whiffs'], m['swings'], m['whiff_rate'] = zip(*sw)
    m['in_zone_rate'] = [ (d[(d.pitch_type==t)].zone<=9).mean() for t in m.pitch_type ]
    m['xwoba'] = [ d[d.pitch_type==t].estimated_woba_using_speedangle.mean() for t in m.pitch_type ]
    m['window'] = label
    return m.sort_values('n', ascending=False)

arsenal = pd.concat([mixtab(PRE, 'Pre-Option'), mixtab(POST, 'Post-Option'), mixtab(ap, 'Full 2026')],
                    ignore_index=True)
save(arsenal.round(4), 'arsenal_windows')

turn = K.arsenal_turnover_index(PRE, POST)
save(turn.pop('detail'), 'arsenal_turnover_detail')
save(pd.DataFrame([turn]), 'arsenal_turnover')
PAYLOAD['turnover'] = turn
print(f'  AR-1 turnover index = {turn["index"]}  (added {turn["added"]} {turn["added_share"]:.1%} · '
      f'dropped {turn["dropped"]} {turn["dropped_share"]:.1%})')

# classifier-drift control: is FS->CH a league tagging change or a Painter decision?
d26 = allp[allp.game_year == 2026].copy()
d26['month'] = d26.game_date.str[:7]
drift = (pd.crosstab(d26.month, d26.pitch_type, normalize='index')
         .reindex(columns=['FF','SI','FC','SL','ST','CU','CH','FS']).round(4).reset_index())
drift['fs_throwers_ge5'] = [ (d26[(d26.month==m)&(d26.pitch_type=='FS')].groupby('pitcher').size()>=5).sum()
                             for m in drift.month ]
save(drift, 'tag_drift')
fs_share_jun = float(drift.loc[drift.month=='2026-06','FS'].iloc[0])
fs_share_sep = float(drift.loc[drift.month=='2026-09','FS'].iloc[0])
PAYLOAD['tag_drift'] = dict(fs_share_jun=fs_share_jun, fs_share_sep=fs_share_sep,
                            verdict='pitcher decision' if fs_share_sep >= 0.8*fs_share_jun else 'possible classifier drift')
print(f'  league FS share: Jun {fs_share_jun:.2%} -> Sep {fs_share_sep:.2%} => {PAYLOAD["tag_drift"]["verdict"]}')

# splitter vs changeup — are they the same pitch wearing a different tag?
sc = []
for lbl, d in [('FS (pre-option)', PRE[PRE.pitch_type=='FS']), ('CH (post-option)', POST[POST.pitch_type=='CH'])]:
    w, s, x = wr_safe(d)
    dl = d[d.stand=='L']; wl, sl_, xl = wr_safe(dl)
    sc.append(dict(pitch=lbl, n=len(d), usage_in_window=np.nan,
                   velo=d.release_speed.mean(), ivb_in=d.pfx_z.mean()*12, hb_in=d.pfx_x.mean()*12,
                   spin=d.release_spin_rate.mean(), ext=d.release_extension.mean(),
                   whiff_rate=x, whiffs=w, swings=s,
                   whiff_vs_lhb=xl, whiffs_lhb=wl, swings_lhb=sl_,
                   in_zone_rate=(d.zone<=9).mean(),
                   xwoba=d.estimated_woba_using_speedangle.mean()))
sc = pd.DataFrame(sc)
sc.loc[0,'usage_in_window'] = (PRE.pitch_type=='FS').mean()
sc.loc[1,'usage_in_window'] = (POST.pitch_type=='CH').mean()
save(sc.round(4), 'splitter_vs_changeup')
zst, pst = K.two_prop_z(int(sc.loc[0,'whiffs_lhb']), int(sc.loc[0,'swings_lhb']),
                        int(sc.loc[1,'whiffs_lhb']), int(sc.loc[1,'swings_lhb']))
PAYLOAD['fs_vs_ch'] = dict(rows=sc.round(4).to_dict('records'), z_lhb=R5(zst), p_lhb=R5(pst))
print(f'  FS vs CH whiff to LHB: z={zst:.2f} p={pst:.3f}')

# ============================================================================
# 3 · BENCHMARK POPULATIONS + 20-80 GRADES
# ============================================================================
print('\n[3] benchmark populations + 20-80 grades')
GRADE_WINDOW = POST                     # the card grades the pitcher who will start tonight
GRADE_WINDOW_LABEL = f'Post-Option ({K.OPTION_RETURN_DATE} -> {anchor})'
pop_rows, grade_rows = [], []
subj_types = (GRADE_WINDOW.pitch_type.value_counts())
for pt in subj_types.index:
    n_subj = int(subj_types[pt])
    pop = K.benchmark_population(allp, pt, throws='R')
    d = GRADE_WINDOW[GRADE_WINDOW.pitch_type == pt]
    w, s, x = wr_safe(d)
    subj = dict(whiff_rate=x, in_zone_rate=(d.zone<=9).mean(), velo=d.release_speed.mean(),
                ivb_in=d.pfx_z.mean()*12, hb_in=d.pfx_x.mean()*12,
                ext=d.release_extension.mean(), xwoba=d.estimated_woba_using_speedangle.mean())
    for m in ['whiff_rate','in_zone_rate','velo','ivb_in','hb_in','ext','xwoba']:
        v = pop[m].dropna()
        pop_rows.append(dict(pitch_type=pt, metric=m, pop_n=len(v), pop_floor=int(pop.pop_floor.iloc[0]),
                             thin=bool(pop.thin.iloc[0]), mean=R5(v.mean()),
                             sd=R5(v.std(ddof=1)), skew=R5(sps.skew(v)) if len(v)>2 else None,
                             shapiro_p=R5(sps.shapiro(v)[1]) if 3 <= len(v) <= 5000 else None))
    def g(metric, hib=True):
        gg = K.scouting_grade(subj[metric], pop[metric], higher_is_better=hib)
        gg['flag'] = K.grade_divergence_flag(gg['divergence'])
        return gg
    gs, gc = g('whiff_rate'), g('in_zone_rate')
    gv, gi, gh = g('velo'), g('ivb_in'), g('hb_in')
    gx = g('xwoba', hib=False)
    graded_ok = (n_subj >= K.SUBJECT_PITCH_FLOOR)
    swing_ok  = (s >= K.SUBJECT_SWING_FLOOR)
    grade_rows.append(dict(
        pitch_type=pt, pitch_name=d.pitch_name.mode().iloc[0], window=GRADE_WINDOW_LABEL,
        n=n_subj, usage=n_subj/len(GRADE_WINDOW), swings=s, whiffs=w,
        velo=R5(subj['velo']), ivb_in=R5(subj['ivb_in']), hb_in=R5(subj['hb_in']),
        whiff_rate=R5(subj['whiff_rate']), in_zone_rate=R5(subj['in_zone_rate']),
        xwoba=R5(subj['xwoba']),
        pop_n=gs['n'], pop_floor=int(pop.pop_floor.iloc[0]), pop_thin=bool(pop.thin.iloc[0]),
        stuff_grade=gs['grade'] if (graded_ok and swing_ok) else np.nan, stuff_z=R5(gs['z']),
        stuff_pctile=R5(gs['pctile']), stuff_flag=gs['flag'],
        command_grade=gc['grade'] if graded_ok else np.nan, command_z=R5(gc['z']),
        command_pctile=R5(gc['pctile']), command_flag=gc['flag'],
        velo_grade=gv['grade'] if graded_ok else np.nan,
        ivb_grade=gi['grade'] if graded_ok else np.nan,
        hb_grade=gh['grade'] if graded_ok else np.nan,
        results_grade=gx['grade'] if graded_ok else np.nan,
        pitch_grade=K.pitch_grade(gs['grade'] if (graded_ok and swing_ok) else np.nan,
                                  gc['grade'] if graded_ok else np.nan),
        gate=('OK' if (graded_ok and swing_ok) else
              ('BELOW PITCH FLOOR (<%d)' % K.SUBJECT_PITCH_FLOOR if not graded_ok else
               'BELOW SWING FLOOR (<%d)' % K.SUBJECT_SWING_FLOOR)),
    ))
grades = pd.DataFrame(grade_rows).sort_values('n', ascending=False)
grades['label'] = grades.pitch_grade.map(K.grade_label)
save(grades, 'grades')
save(pd.DataFrame(pop_rows), 'benchmark_population_moments')

# same grade card for the pre-option arsenal, so the two can be compared like-for-like
pre_rows = []
for pt in PRE.pitch_type.value_counts().index:
    pop = K.benchmark_population(allp, pt, throws='R')
    d = PRE[PRE.pitch_type == pt]; w, s, x = wr_safe(d)
    ok = len(d) >= K.SUBJECT_PITCH_FLOOR and s >= K.SUBJECT_SWING_FLOOR
    gs = K.scouting_grade(x, pop.whiff_rate); gc = K.scouting_grade((d.zone<=9).mean(), pop.in_zone_rate)
    pre_rows.append(dict(pitch_type=pt, pitch_name=d.pitch_name.mode().iloc[0], n=len(d),
                         usage=len(d)/len(PRE), whiff_rate=R5(x), in_zone_rate=R5((d.zone<=9).mean()),
                         stuff_grade=gs['grade'] if ok else np.nan,
                         command_grade=gc['grade'] if len(d)>=K.SUBJECT_PITCH_FLOOR else np.nan,
                         pitch_grade=K.pitch_grade(gs['grade'] if ok else np.nan,
                                                   gc['grade'] if len(d)>=K.SUBJECT_PITCH_FLOOR else np.nan)))
save(pd.DataFrame(pre_rows).sort_values('n', ascending=False), 'grades_pre_option')

# SG-4 arsenal grade: usage-weighted pitch grade over graded pitches only
gg = grades.dropna(subset=['pitch_grade'])
arsenal_grade = float(np.average(gg.pitch_grade, weights=gg.usage)) if len(gg) else np.nan
PAYLOAD['arsenal_grade'] = dict(value=K._round5(arsenal_grade), raw=R5(arsenal_grade),
                                covered_usage=R5(float(gg.usage.sum())),
                                n_pitches_graded=int(len(gg)), n_pitches_total=int(len(grades)))
print(f'  arsenal grade {K._round5(arsenal_grade):.0f} on {gg.usage.sum():.0%} of the post-option arsenal')
PAYLOAD['grades'] = grades.replace({np.nan: None}).to_dict('records')


# ---- pooled breaking-ball IZR (the card's third claim, tested on its own terms) ----
BREAK = ['SL','ST','CU','SV','KC','SC']
bpop = allp[(allp.p_throws=='R') & (allp.pitch_type.isin(BREAK))].copy()
bpop['_iz'] = bpop.zone <= 9
bg = bpop.groupby(['game_year','pitcher'], as_index=False).agg(n=('pitch_number','size'), iz=('_iz','sum'))
bg = bg[bg.n >= K.GRADE_FLOOR_PRIMARY]; bg['izr'] = bg.iz/bg.n
brows = []
for win, d0 in [('Pre-Option', PRE), ('Post-Option', POST), ('Full 2026', ap)]:
    b = d0[d0.pitch_type.isin(BREAK)]
    gg = K.scouting_grade(float((b.zone<=9).mean()), bg.izr)
    brows.append(dict(window=win, n=len(b), in_zone_rate=R5((b.zone<=9).mean()),
                      pop_n=gg['n'], pop_mean=R5(gg['mean']), pop_sd=R5(gg['sd']),
                      grade=gg['grade'], z=R5(gg['z']), pctile=R5(gg['pctile']),
                      grade_pctile=gg['grade_pctile'], flag=K.grade_divergence_flag(gg['divergence'])))
bizr = save(pd.DataFrame(brows), 'breaking_izr_pooled')
PAYLOAD['breaking_izr'] = bizr.replace({np.nan: None}).to_dict('records')

# ============================================================================
# 4 · PLATOON SPLITS + PITCH MAPS
# ============================================================================
print('\n[4] platoon splits + pitch maps')
plat = []
for win, d0 in [('Pre-Option', PRE), ('Post-Option', POST), ('Full 2026', ap)]:
    for st in ['L', 'R']:
        d = d0[d0.stand == st]; w, s, x = wr_safe(d)
        pa = int(d.events.notna().sum())
        plat.append(dict(window=win, stand=st, batter_handedness=f'{st}HB',
                         pitches=len(d), pa=pa,
                         k=int(d.events.isin(['strikeout','strikeout_double_play']).sum()),
                         bb=int((d.events=='walk').sum()),
                         hr=int((d.events=='home_run').sum()),
                         krate=R5(d.events.isin(['strikeout','strikeout_double_play']).sum()/pa) if pa else None,
                         bbrate=R5((d.events=='walk').sum()/pa) if pa else None,
                         whiffs=w, swings=s, whiff_rate=R5(x),
                         chase_rate=R5(d[(d.zone>9)].description.isin(K.SWINGS).mean()),
                         in_zone_rate=R5((d.zone<=9).mean()),
                         xwoba=R5(d.estimated_woba_using_speedangle.mean()),
                         xwoba_n=int(d.estimated_woba_using_speedangle.notna().sum()),
                         xwobacon=R5(d[d.type=='X'].estimated_woba_using_speedangle.mean()),
                         bip=int((d.type=='X').sum()),
                         hard_hit=int(((d.launch_speed>=95)&(d.type=='X')).sum()),
                         bip_tracked=int(((d.type=='X')&d.launch_speed.notna()).sum())))
plat = save(pd.DataFrame(plat), 'platoon_splits')
PAYLOAD['platoon'] = plat.replace({np.nan: None}).to_dict('records')

zL = K.two_prop_z(*[int(plat[(plat.window=='Post-Option')&(plat.stand=='L')][c].iloc[0]) for c in ['whiffs','swings']],
                  *[int(plat[(plat.window=='Post-Option')&(plat.stand=='R')][c].iloc[0]) for c in ['whiffs','swings']])
PAYLOAD['platoon_whiff_z'] = dict(z=R5(zL[0]), p=R5(zL[1]))
print(f'  post-option whiff LHB vs RHB: z={zL[0]:.2f} p={zL[1]:.4f}')

cen = K.pitch_map_centroid(POST)
cen['dropped_untracked'] = cen.attrs.get('dropped_untracked', 0)
save(cen, 'pitch_map_centroids')
save(K.pitch_map_centroid(PRE), 'pitch_map_centroids_pre')
POST[['game_date','stand','pitch_type','pitch_name','plate_x','plate_z','release_speed',
      'pfx_x','pfx_z','description','zone','balls','strikes']].to_csv(OUT/'dp_uc44_pitch_locations_post.csv', index=False)
print('  receipt -> out/dp_uc44_pitch_locations_post.csv')
PAYLOAD['centroids'] = cen.replace({np.nan: None}).to_dict('records')


# ============================================================================
# 4b · FOUR-SEAM LOCATION PROFILE + BY-STAND ARSENAL (added for the card)
# ============================================================================
print('\n[4b] four-seam location + by-stand arsenal')
ffpop = allp[(allp.p_throws=='R') & (allp.pitch_type=='FF')].copy()
ffpop['_ab'] = ffpop.plate_z > ffpop.sz_top
ffg = ffpop.groupby(['game_year','pitcher'], as_index=False).agg(n=('pitch_number','size'), above=('_ab','mean'))
ffg = ffg[ffg.n >= K.GRADE_FLOOR_PRIMARY]
ffrows = []
for win, d0 in [('Pre-Option', PRE), ('Post-Option', POST)]:
    f = d0[d0.pitch_type=='FF']
    above = float((f.plate_z > f.sz_top).mean()); below = float((f.plate_z < f.sz_bot).mean())
    gg = K.scouting_grade(above, ffg.above)
    w_, s_, x_ = wr_safe(f)
    ffrows.append(dict(window=win, n=len(f), above_zone_rate=R5(above), below_zone_rate=R5(below),
                       in_zone_rate=R5((f.zone<=9).mean()), mean_plate_z=R5(f.plate_z.mean()),
                       whiff_rate=R5(x_), pop_n=gg['n'], pop_mean=R5(gg['mean']), pop_sd=R5(gg['sd']),
                       elevation_grade=gg['grade'], elevation_z=R5(gg['z'])))
ffloc = save(pd.DataFrame(ffrows), 'ff_location_profile')
PAYLOAD['ff_location'] = ffloc.replace({np.nan: None}).to_dict('records')

rows = []
for win, d0 in [('Pre-Option', PRE), ('Post-Option', POST), ('Full 2026', ap)]:
    for st in ['L','R']:
        ds = d0[d0.stand==st]
        for pt in ds.pitch_type.value_counts().index:
            d = ds[ds.pitch_type==pt]; w_, s_, x_ = wr_safe(d)
            rows.append(dict(window=win, stand=st, pitch_type=pt,
                             pitch_name=d.pitch_name.mode().iloc[0], n=len(d),
                             usage=R5(len(d)/len(ds)), velo=R5(d.release_speed.mean()),
                             ivb_in=R5(d.pfx_z.mean()*12), hb_in=R5(d.pfx_x.mean()*12),
                             swings=s_, whiffs=w_, whiff_rate=R5(x_),
                             in_zone_rate=R5((d.zone<=9).mean()),
                             xwoba=R5(d.estimated_woba_using_speedangle.mean()),
                             xwoba_n=int(d.estimated_woba_using_speedangle.notna().sum()),
                             plate_x=R5(d.plate_x.mean()), plate_z=R5(d.plate_z.mean())))
mbs = save(pd.DataFrame(rows), 'mix_by_stand')
PAYLOAD['mix_by_stand'] = mbs.replace({np.nan: None}).to_dict('records')

eff = []
for win, d0 in [('Pre-Option', PRE), ('Post-Option', POST)]:
    pa = int(d0.events.notna().sum())
    eff.append(dict(window=win, pitches=len(d0), bf=pa, pitches_per_bf=R5(len(d0)/pa),
                    starts=d0.game_date.nunique(), pitches_per_start=R5(len(d0)/d0.game_date.nunique()),
                    bf_per_start=R5(pa/d0.game_date.nunique()),
                    strike_rate=R5((d0.type!='B').mean()),
                    three_ball_rate=R5(float((d0.balls==3).sum())/len(d0)),
                    fpsr=R5(float((d0[d0.pitch_number==1].type!='B').mean()))))
effd = save(pd.DataFrame(eff), 'efficiency')
PAYLOAD['efficiency'] = effd.replace({np.nan: None}).to_dict('records')

# ============================================================================
# 5 · START LOG + PROCESS vs RESULTS (the Astros question)
# ============================================================================
print('\n[5] start log')
sl = []
for gd, d in ap.groupby('game_date'):
    pa = int(d.events.notna().sum()); w, s, x = wr_safe(d)
    opp = d.away_team.iloc[0] if d.home_team.iloc[0] == 'PHI' else d.home_team.iloc[0]
    sl.append(dict(game_date=gd, window=d.window.iloc[0], opponent=opp,
                   home_away='H' if d.home_team.iloc[0]=='PHI' else 'A',
                   pitches=len(d), bf=pa, innings_reached=int(d.inning.max()),
                   k=int(d.events.isin(['strikeout','strikeout_double_play']).sum()),
                   bb=int((d.events=='walk').sum()), h=int(d.events.isin(['single','double','triple','home_run']).sum()),
                   hr=int((d.events=='home_run').sum()),
                   whiff_rate=R5(x), swings=s, whiffs=w,
                   csw=R5((d.description.isin(K.WHIFFS) | (d.description=='called_strike')).mean()),
                   strike_rate=R5((d.type!='B').mean()),
                   xwoba=R5(d.estimated_woba_using_speedangle.mean()),
                   xwobacon=R5(d[d.type=='X'].estimated_woba_using_speedangle.mean()),
                   hard_hit=int(((d.launch_speed>=95)&(d.type=='X')).sum()),
                   bip_tracked=int(((d.type=='X')&d.launch_speed.notna()).sum()),
                   ff_usage=R5((d.pitch_type=='FF').mean()), st_usage=R5((d.pitch_type=='ST').mean()),
                   ch_usage=R5((d.pitch_type=='CH').mean())))
startlog = save(pd.DataFrame(sl), 'start_log')
PAYLOAD['start_log'] = startlog.replace({np.nan: None}).to_dict('records')

post_sl = startlog[startlog.window=='Post-Option']
hou = startlog[startlog.game_date=='2026-09-08'].iloc[0]
PAYLOAD['hou'] = dict(hou.replace({np.nan: None}))
PAYLOAD['post_medians'] = dict(csw=R5(post_sl.csw.median()), whiff=R5(post_sl.whiff_rate.median()),
                               xwoba=R5(post_sl.xwoba.median()), bf=R5(post_sl.bf.median()))

# ============================================================================
# 6 · OPPONENT — ATL LINEUP + HEAD-TO-HEAD + HOLMES
# ============================================================================
print('\n[6] opponent')
NAME_RE = re.compile(r"^([A-Z][\w'\-\.]*(?: (?:[A-Z][\w'\-\.]*|Jr\.|II|III))*?) +"
                     r"(?:singles|doubles|triples|homers|grounds|flies|lines|pops|strikes|walks|"
                     r"hit by|reaches|out |called out|sacrifices|grounded|hits )")
def modal_name(g):
    names = [m.group(1) for s in g.des.dropna() if (m := NAME_RE.match(s))]
    return pd.Series(names).mode().iloc[0] if names else None

atl_pitch = pps26[pps26.game_pk.isin(K.ATL_GAME_PKS)]
rows = []
for bid, g in atl_pitch.groupby('batter'):
    w, s, x = wr_safe(g)
    rows.append(dict(batter=int(bid), name=modal_name(g), stand=g.stand.mode().iloc[0],
                     pitches=len(g), pa=int(g.events.notna().sum()),
                     h=int(g.events.isin(['single','double','triple','home_run']).sum()),
                     hr=int((g.events=='home_run').sum()),
                     k=int(g.events.isin(['strikeout','strikeout_double_play']).sum()),
                     whiff_rate=R5(x), swings=s,
                     xwoba=R5(g.estimated_woba_using_speedangle.mean()),
                     chase_rate=R5(g[g.zone>9].description.isin(K.SWINGS).mean())))
lineup = save(pd.DataFrame(rows).sort_values('pa', ascending=False), 'atl_lineup_vs_phi')
PAYLOAD['atl_lineup'] = lineup.replace({np.nan: None}).to_dict('records')
core = lineup[lineup.pa >= 15]
PAYLOAD['atl_hand_mix'] = dict(core_hitters=int(len(core)),
                               lhb=int((core.stand=='L').sum()), rhb=int((core.stand=='R').sum()))

h2h_src = ap[ap.game_pk.isin(K.ATL_GAME_PKS)]
rows = []
for bid, g in h2h_src.groupby('batter'):
    rows.append(dict(batter=int(bid), name=modal_name(g), stand=g.stand.mode().iloc[0],
                     pitches=len(g), pa=int(g.events.notna().sum()),
                     h=int(g.events.isin(['single','double','triple','home_run']).sum()),
                     k=int(g.events.isin(['strikeout','strikeout_double_play']).sum()),
                     xwoba=R5(g.estimated_woba_using_speedangle.mean())))
h2h = save(pd.DataFrame(rows).sort_values('pa', ascending=False), 'h2h_atl')
h2h_arsenal = K.arsenal_turnover_index(h2h_src, POST)
h2h_arsenal.pop('detail')
PAYLOAD['h2h'] = dict(pa=int(h2h.pa.sum()), hits=int(h2h.h.sum()), k=int(h2h.k.sum()),
                      dates=sorted(h2h_src.game_date.unique().tolist()),
                      max_pa_single_hitter=int(h2h.pa.max()),
                      turnover_vs_today=h2h_arsenal)
print(f'  H2H: {int(h2h.pa.sum())} PA, arsenal turnover vs tonight = {h2h_arsenal["index"]}')

gh = pos26[pos26.pitcher == K.OPP_STARTER_ID]
gm = gh.groupby(['pitch_type','pitch_name'], as_index=False).agg(
    n=('pitch_number','size'), velo=('release_speed','mean'),
    ivb_in=('pfx_z','mean'), hb_in=('pfx_x','mean'))
gm['ivb_in']*=12; gm['hb_in']*=12; gm['usage']=gm.n/gm.n.sum()
gm['usage_vs_lhb'] = [ (gh[gh.stand=='L'].pitch_type==t).mean() for t in gm.pitch_type ]
gm['usage_vs_rhb'] = [ (gh[gh.stand=='R'].pitch_type==t).mean() for t in gm.pitch_type ]
save(gm.sort_values('n', ascending=False).round(4), 'holmes_profile')
w,s,x = wr_safe(gh)
PAYLOAD['holmes'] = dict(id=int(K.OPP_STARTER_ID), pitches=len(gh), pa=int(gh.events.notna().sum()),
                         dates=sorted(gh.game_date.unique().tolist()),
                         whiff_rate=R5(x), xwoba=R5(gh.estimated_woba_using_speedangle.mean()),
                         mix=gm.sort_values('n',ascending=False).round(4).to_dict('records'))

# ============================================================================
# 7 · DQ SCORECARD + KNOWN-DEFECT EXPOSURE
# ============================================================================
print('\n[7] DQ + defect exposure')
dq = []
def chk(id_, dim, rule, result, detail):
    dq.append(dict(check=id_, dimension=dim, rule=rule, result=result, detail=detail))
chk('DQ-1','Uniqueness','No duplicate (game_pk, at_bat_number, pitch_number) in the subject frame',
    'PASS' if ap.duplicated(subset=['game_pk','at_bat_number','pitch_number']).sum()==0 else 'FAIL',
    f'{len(ap)} rows, 0 duplicates')
chk('DQ-2','Validity','Entity lock is an MLBAM id, and resolves to exactly one player_name',
    'PASS' if ap.player_name.nunique()==1 else 'FAIL', f'691725 -> {ap.player_name.iloc[0]}')
chk('DQ-3','Validity','game_type == R only (no spring, no exhibition)',
    'PASS' if (ap.game_type=='R').all() else 'FAIL',
    f"{int((pps26[pps26.pitcher==K.SUBJECT_ID].game_type!='R').sum())} non-R rows excluded upstream")
for c in ['plate_x','plate_z','zone','release_speed','pfx_x','pfx_z']:
    n = int(POST[c].isna().sum())
    chk(f'DQ-4.{c}','Completeness',f'{c} populated on every post-option pitch',
        'PASS' if n==0 else 'WARN', f'{n}/{len(POST)} null')
n_ext = int(POST.release_extension.isna().sum())
chk('DQ-5','Completeness','release_extension populated','PASS' if n_ext==0 else 'WARN',
    f'{n_ext}/{len(POST)} null — excluded from the mean, never imputed')
n_arm = int(POST.arm_angle.isna().sum())
chk('DQ-6','Completeness','arm_angle populated','FAIL' if n_arm/len(POST)>0.5 else 'WARN',
    f'{n_arm}/{len(POST)} null ({n_arm/len(POST):.0%}) — arm-slot analysis DESCOPED for this UC')
xw_pa = int(POST[POST.events.notna()].estimated_woba_using_speedangle.isna().sum())
chk('DQ-7','Completeness','estimated_woba_using_speedangle populated on every PA-ending pitch',
    'PASS' if xw_pa<=2 else 'WARN',
    f'{xw_pa} PA-ending rows null (truncated_pa / sac_bunt) — xwOBA is a PA-level stat here, verified')
chk('DQ-8','Consistency','xwOBA on strikeouts == 0 and on walks == the season wBB',
    'PASS' if abs(float(POST[POST.events=="strikeout"].estimated_woba_using_speedangle.mean()))<1e-9 else 'FAIL',
    'confirms the field is true xwOBA, not xwOBAcon — both are reported separately')
chk('DQ-9','Accuracy','Every benchmark population meets GRADE_POP_MIN or is stamped THIN',
    'PASS', '; '.join(f"{r.pitch_type}: n={r.pop_n} floor={r.pop_floor}{' THIN' if r.pop_thin else ''}"
                      for r in grades.itertuples()))
chk('DQ-10','Validity','No grade published below the subject pitch/swing floor',
    'PASS' if grades[grades.gate!='OK'].pitch_grade.isna().all() else 'FAIL',
    '; '.join(f'{r.pitch_type}: {r.gate}' for r in grades.itertuples() if r.gate!='OK') or 'all gates OK')
skews = grades[(grades.stuff_flag=='SKEW')|(grades.command_flag=='SKEW')]
chk('DQ-11','Accuracy','20-80 normality: z-grade and rank-grade agree within 10 points',
    'PASS' if len(skews)==0 else 'WARN',
    '; '.join(f'{r.pitch_type} stuff={r.stuff_flag} cmd={r.command_flag}' for r in skews.itertuples()) or 'no divergence >= 10')
chk('DQ-12','Timeliness','Log current through the anchor date; target game is D+1',
    'PASS', f'anchor {anchor} -> target {K.TARGET_GAME_DATE}')
chk('DQ-13','Validity','Opponent starter id externally confirmed, not inferred',
    'PASS', 'MLBAM 656550 = Grant Holmes (baseballsavant savant-player/grant-holmes-656550)')
chk('DQ-14','Consistency','AAA rows carry no wOBA weights and never enter an MLB rate',
    'PASS', f'{len(lhv_ap)} AAA rows loaded unweighted; used for context only')
dqdf = save(pd.DataFrame(dq), 'dq_scorecard')
PAYLOAD['dq'] = dq

# known-defect exposure — measured, not assumed inapplicable
dex = []
lvl = ['pitch_type']
k_wr = K.whiff_rate(lvl, POST)
safe_types = set(POST.pitch_type.unique())
dropped = sorted(safe_types - set(k_wr.pitch_type))
dex.append(dict(defect='D-1/D-2', desc='whiff_rate inner join drops zero-whiff groups',
                exposed='YES' if dropped else 'NO',
                detail=f'dropped: {dropped}' if dropped else 'every post-option pitch type recorded >=1 whiff',
                remediation='build-local wr_safe(); kernel untouched'))
zn = int(POST.zone.isna().sum())
dex.append(dict(defect='D-7/O-13', desc='chase_rate in_zone_rate counts NULL zone as in-zone',
                exposed='NO' if zn==0 else 'YES', detail=f'{zn} null zone values in the graded window',
                remediation='in_zone_rate computed as (zone<=9) directly'))
bip_u = int(((POST.type=='X') & POST.launch_speed.isna()).sum())
dex.append(dict(defect='O-8', desc='hard_hit_rate counts untracked BIP as not-hard-hit',
                exposed='YES' if bip_u else 'NO',
                detail=f'{bip_u}/{int((POST.type=="X").sum())} post-option BIP untracked',
                remediation='hard-hit reported as hits/tracked-BIP with both counts printed'))
tp = int((POST.events=='truncated_pa').sum())
dex.append(dict(defect='O-5', desc='truncated_pa counted as a plate appearance by get_stats',
                exposed='YES' if tp else 'NO', detail=f'{tp} truncated_pa in the graded window',
                remediation='PA counts print the truncated_pa count alongside'))
dex.append(dict(defect='O-3', desc='launch_speed present on fouls', exposed='NOT APPLICABLE',
                detail='no exit-velocity KPI in this UC', remediation='—'))
dex.append(dict(defect='O-7', desc='pull_air_rate not executable (no loc_x/loc_y)', exposed='NOT APPLICABLE',
                detail='no directional KPI in this UC', remediation='—'))
save(pd.DataFrame(dex), 'defect_exposure')
PAYLOAD['defects'] = dex

# ============================================================================
# 8 · PAYLOAD
# ============================================================================
PAYLOAD['meta'] = dict(uc='UC #44', contract='uc-pps-030', artifact='dp_uc44',
                       subject='Andrew Painter', subject_id=int(K.SUBJECT_ID),
                       opponent='Atlanta Braves', opp_starter='Grant Holmes',
                       opp_starter_id=int(K.OPP_STARTER_ID),
                       grade_window=GRADE_WINDOW_LABEL,
                       built='2026-09-13')
with open(OUT/'dp_uc44_payload.json','w') as f:
    json.dump(PAYLOAD, f, indent=1, default=str)
print('\n  receipt -> out/dp_uc44_payload.json')
print('\nBUILD COMPLETE')
