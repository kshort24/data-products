"""
dp_uc47_archetype_gap.py — UC #47 / uc-pps-032 build
"Archetype Gap Analysis — pilot: the Elite RHP Four-Seamer"

Two questions, kept apart on purpose (01_strategy_intake.md §2):
  Part A · internal cohort ranking — the six Phillies-affiliated arms
  Part B · external gap            — who, not on the 2026 Phillies, would move
                                     the staff's elite-four-seam share most
Plus Part H · the human parent — the client's own notebook claims, reproduced
with his method and re-run governed.

Every number in the report and the dashboard is read from out/dp_uc47_*.
Run:  MLB_DATA_ROOT=<.../Python Scripts/MLB> python dp_uc47_archetype_gap.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import dp_uc47_kernel as K

OUT = Path(os.environ.get("DP_UC47_OUT", Path(__file__).resolve().parent / "out"))
OUT.mkdir(parents=True, exist_ok=True)
SPEC = K.ELITE_RHP_FF
PFX = "dp_uc47_"


def save(df: pd.DataFrame, name: str, **kw):
    df.to_csv(OUT / f"{PFX}{name}.csv", index=False, **kw)
    return df


# ---------------------------------------------------------------------------
# 0 · Anchor guard + universe (FR-1)
# ---------------------------------------------------------------------------
U, rec, keying = K.house_pitch_universe()
max_phi = str(pd.to_datetime(U[U.src == 'phils'].game_date).max().date())
assert max_phi == K.ANCHOR_DATE, f"anchor drift: log ends {max_phi}, build pinned to {K.ANCHOR_DATE}"
assert rec['union_dup_pitch_keys'] == 0
save(pd.DataFrame([rec]).T.reset_index().rename(columns={'index': 'step', 0: 'rows'}), 'universe_receipt')
save(keying, 'nphl_file_keying')

names = K.resolve_pitcher_names(U)
save(names, 'name_resolution')
NAME = names.set_index('pitcher').name_display
name_meta = dict(t2_agreement=names.attrs['t2_agreement'], t2_overlap_n=names.attrs['t2_overlap_n'])

# ---------------------------------------------------------------------------
# 1 · Pitcher-season frame (AF-2), stabilization (SG-7), trend (SG-6)
# ---------------------------------------------------------------------------
g = K.archetype_frame(U, SPEC)
pop0 = g.n >= SPEC.pop_floor
F = U[(U.p_throws == 'R') & (U.pitch_type == 'FF') & U.game_year.between(*SPEC.era)]
stab = pd.DataFrame([K.split_half_k(F, m) for m in ['velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']])
stab['reliability_at_subject_floor'] = SPEC.subject_floor / (SPEC.subject_floor + stab.k)
stab['reliability_at_pop_floor'] = SPEC.pop_floor / (SPEC.pop_floor + stab.k)
stab['shrink'] = stab.reliability_at_subject_floor < 0.90       # SG-7 decision rule
save(stab, 'stabilization')

for m in ['velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']:
    row = stab.set_index('metric').loc[m]
    if row.shrink:
        ncol = K.METRIC_DEFS[m]['stab_n']
        mu = g.loc[pop0, m].mean()
        g[m + '_stab'] = K.stabilize(g[m], g[ncol], row.k, mu)
    else:
        g[m + '_stab'] = g[m]
g, trend = K.season_trend_adjust(g, [m + '_stab' for m in ['velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']],
                                 pop0, ref_year=K.CURRENT_SEASON, alpha=SPEC.trend_alpha)
trend['metric'] = trend.metric.str.replace('_stab', '', regex=False)
save(trend, 'trend_adjust')
for m in ['velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']:
    g[m + '_final'] = g[m + '_stab_adj']

# ---------------------------------------------------------------------------
# 2 · Grades (SG-1 via AF-3)
# ---------------------------------------------------------------------------
G = K.archetype_grades(g, SPEC, value_suffix='_final', pop_mask=pop0)
G['name'] = G.pitcher.map(NAME)
phi26 = set(U[(U.src == 'phils') & (U.phillies_role == 'pitching') & (U.game_year == K.CURRENT_SEASON)].pitcher.unique())
G['on_phi_2026'] = G.pitcher.isin(phi26)
G['is_cohort'] = G.pitcher.isin(K.COHORT)
G['phi_season'] = G.frame.eq('PHI')
keep_cols = ['game_year', 'pitcher', 'name', 'is_cohort', 'on_phi_2026', 'phi_season', 'frame', 'coverage',
             'role', 'med_pitches_per_outing', 'games', 'n', 'swings', 'pa_end', 'usage', 'thin', 'pop_member',
             'velo', 'ivb_in', 'spin', 'ext', 'hb_in', 'whiff_rate', 'rv100', 'xwoba',
             'velo_final', 'ivb_in_final', 'spin_final', 'whiff_rate_final', 'rv100_final',
             'g_velo', 'g_ivb_in', 'g_spin', 'g_whiff_rate', 'g_rv100',
             'z_velo', 'z_ivb_in', 'z_spin', 'z_whiff_rate', 'z_rv100',
             'shape_grade', 'results_grade', 'shape_score', 'results_score',
             'ff_elite_shape_flag', 'ff_elite_results_flag', 'ff_elite_archetype_flag',
             'ff_elite_composite', 'efc_score', 'archetype_tier']
graded = G[G.n >= SPEC.subject_floor]
save(graded[keep_cols].sort_values('efc_score', ascending=False).round(4), 'population_graded')

# population moments + normality (the 20-80 scale assumes it — test it, uc-pps-030 rule 2)
mom = []
P = G[pop0]
for m, _ in SPEC.shape + SPEC.results:
    v = P[m + '_final'].dropna()
    sw = stats.shapiro(v)
    # rank-derived twin agreement (SG-3)
    twin = [K.scouting_grade(x, v.values, higher_is_better=True) for x in v.values]
    div = np.array([t['divergence'] for t in twin])
    mom.append(dict(metric=m, n=len(v), mean=v.mean(), sd=v.std(ddof=1), p5=v.quantile(.05), p95=v.quantile(.95),
                    skew=stats.skew(v), shapiro_p=sw.pvalue, normal_at_05=sw.pvalue >= .05,
                    twin_identical_share=float(np.mean(div == 0)), twin_max_abs_div=float(np.nanmax(np.abs(div))),
                    skew_flags=int(np.sum(np.abs(div) >= K.K44.DIVERGENCE_FLAG))))
mom = save(pd.DataFrame(mom), 'population_moments')

# ---------------------------------------------------------------------------
# 3 · PART A — the cohort
# ---------------------------------------------------------------------------
C = G[G.is_cohort & (G.n >= SPEC.subject_floor)].copy()
C['arm'] = C.pitcher.map(K.COHORT)
C['cohort_rank_in_population'] = C.efc_score.apply(lambda s: int((G.loc[pop0, 'efc_score'] > s).sum()) + 1)
save(C[['arm'] + keep_cols + ['cohort_rank_in_population']].sort_values(['arm', 'game_year']).round(4), 'cohort_seasons')

lb = []
for pid, arm in K.COHORT.items():
    s = C[C.pitcher == pid]
    if s.empty:
        lb.append(dict(arm=arm, pitcher=pid, graded_seasons=0)); continue
    best = s.sort_values('efc_score', ascending=False).iloc[0]
    cur = s[s.game_year == s.game_year.max()].iloc[0]
    lb.append(dict(arm=arm, pitcher=pid, graded_seasons=len(s),
                   elite_seasons=int(s.ff_elite_archetype_flag.sum()),
                   best_year=int(best.game_year), best_efc=best.efc_score, best_composite=best.ff_elite_composite,
                   best_shape=best.shape_grade, best_results=best.results_grade, best_tier=best.archetype_tier,
                   best_rank_in_population=int(best.cohort_rank_in_population),
                   latest_year=int(cur.game_year), latest_efc=cur.efc_score, latest_composite=cur.ff_elite_composite,
                   latest_shape=cur.shape_grade, latest_results=cur.results_grade, latest_tier=cur.archetype_tier,
                   latest_thin=bool(cur.thin), latest_n=int(cur.n), latest_is_phi=bool(cur.phi_season)))
lb = pd.DataFrame(lb).sort_values('best_efc', ascending=False)
lb['cohort_rank_best'] = range(1, len(lb) + 1)
lb['cohort_rank_latest'] = lb.latest_efc.rank(ascending=False, method='min').astype(int)
save(lb.round(4), 'cohort_leaderboard')

# weight sensitivity (AF-4) on each arm's best season and on each arm's 2026 season
best_idx = C.sort_values('efc_score', ascending=False).groupby('pitcher').head(1).index
ws_best = K.weight_sensitivity(G, G.index.isin(best_idx))
ws_best['arm'] = ws_best.pitcher.map(K.COHORT)
save(ws_best[['arm', 'game_year', 'shape_score', 'results_score'] + [c for c in ws_best if c.startswith('rank_w')]].round(3),
     'weight_sensitivity_cohort_best')
ws26 = K.weight_sensitivity(G, G.is_cohort & (G.game_year == 2026) & (G.n >= SPEC.subject_floor))
ws26['arm'] = ws26.pitcher.map(K.COHORT)
save(ws26[['arm', 'game_year', 'n', 'thin', 'shape_score', 'results_score'] + [c for c in ws26 if c.startswith('rank_w')]].round(3),
     'weight_sensitivity_cohort_2026')

# ---------------------------------------------------------------------------
# 4 · PART B — the external gap
# ---------------------------------------------------------------------------
staff = G[G.pitcher.isin(phi26) & (G.game_year == 2026)].copy()
# staff FF volume must be PHILLIES four-seams only (a mid-season add's prior-club rows excluded)
phi_ff = U[(U.src == 'phils') & (U.phillies_role == 'pitching') & (U.game_year == 2026) &
           (U.p_throws == 'R') & (U.pitch_type == 'FF')].groupby('pitcher').size()
staff['n_phi'] = staff.pitcher.map(phi_ff).fillna(0).astype(int)
staff = staff[staff.n_phi > 0].copy()
staff_for_share = staff.assign(n=staff.n_phi)
save(staff[['pitcher', 'name', 'role', 'n', 'n_phi', 'thin', 'velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100',
            'shape_grade', 'results_grade', 'ff_elite_composite', 'efc_score', 'archetype_tier',
            'ff_elite_shape_flag', 'ff_elite_results_flag', 'ff_elite_archetype_flag']]
     .sort_values('efc_score', ascending=False).round(4), 'staff_2026')

efs = pd.DataFrame([K.elite_share(staff_for_share, f) for f in
                    ['ff_elite_archetype_flag', 'ff_elite_shape_flag', 'ff_elite_results_flag']])
# carry-in scenario: Bowlan unavailable (client notebook, 9/17 oblique) — NOT a data fact
wo_b = staff_for_share[staff_for_share.pitcher != 680742]
efs_b = K.elite_share(wo_b, 'ff_elite_archetype_flag'); efs_b['flag'] = 'ff_elite_archetype_flag|carry_in_bowlan_out'
efs = pd.concat([efs, pd.DataFrame([efs_b])], ignore_index=True)
save(efs.round(4), 'efs_2026')

# candidate pool: not on the 2026 Phillies, 2025-2026 seasons.
# CB-1 candidate evidence floor: to be RANKED a candidate needs a season that clears the
# population floor (>= 100 FF) — the same evidence bar as the arms he is graded against.
# Latest qualifying season is used. Arms with only a 50-99 FF season go to the WATCH LIST.
pool = G[~G.on_phi_2026 & G.game_year.isin([2025, 2026]) & (G.n >= SPEC.subject_floor) & G.efc_score.notna()]
qual = pool[pool.n >= SPEC.pop_floor].sort_values('game_year', ascending=False).groupby('pitcher').head(1)
watch = pool[~pool.pitcher.isin(qual.pitcher)].sort_values('game_year', ascending=False).groupby('pitcher').head(1)
cand = qual.sort_values('efc_score', ascending=False).copy()
cand['cand_rank'] = range(1, len(cand) + 1)
cand['board'] = 'RANKED'
watch = watch.sort_values('efc_score', ascending=False).copy()
watch['cand_rank'] = np.nan
watch['board'] = 'WATCH (THIN)'
# the ungoverned rank (no stabilization, no trend) — to show what the governance changed
Graw = K.archetype_grades(g.assign(**{m + '_raw': g[m] for m in ['velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']}),
                          SPEC, value_suffix='_raw', pop_mask=pop0)
raw_score = Graw.set_index(['game_year', 'pitcher']).efc_score
for fr_ in (cand, watch):
    fr_['efc_score_ungoverned'] = [raw_score.get((y, p), np.nan) for y, p in zip(fr_.game_year, fr_.pitcher)]
cand['ungoverned_rank'] = cand.efc_score_ungoverned.rank(ascending=False, method='min')
watch['ungoverned_rank'] = np.nan
both = pd.concat([cand, watch], ignore_index=True)
save(both[['board', 'cand_rank', 'ungoverned_rank', 'game_year', 'pitcher', 'name', 'is_cohort', 'frame', 'coverage', 'role',
           'games', 'n', 'swings', 'thin', 'velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100',
           'whiff_rate_final', 'rv100_final', 'shape_grade', 'results_grade', 'ff_elite_composite',
           'efc_score', 'efc_score_ungoverned', 'archetype_tier']].round(4), 'candidates')

needle = K.needle_swap(pd.concat([cand.head(25), watch]), staff_for_share, SPEC)
needle['name'] = needle.pitcher.map(NAME)
needle['displaced_name'] = needle.displaced_pitcher.map(NAME)
needle = needle.merge(both[['pitcher', 'board', 'cand_rank', 'archetype_tier', 'coverage', 'games', 'n']], on='pitcher')
rk = needle.board.eq('RANKED')
needle.loc[rk, 'needle_rank'] = needle.loc[rk, 'delta_staff_score'].rank(ascending=False, method='min')
save(needle.sort_values('needle_rank').round(4), 'needle')

# gap size: best external current vs best internal current (and with the carry-in)
int_best = staff[staff.efc_score.notna()].sort_values('efc_score', ascending=False)
int_best_nb = int_best[int_best.pitcher != 680742]
ext_best = cand.iloc[0]
ext_best_complete = cand[cand.coverage == 'COMPLETE'].iloc[0]
watch_best = watch.iloc[0]
gap = pd.DataFrame([
    dict(view='best external vs best internal (2026)', external=ext_best['name'], ext_efc=ext_best.efc_score,
         internal=int_best.iloc[0]['name'], int_efc=int_best.iloc[0].efc_score),
    dict(view='best external vs best internal, Bowlan out (carry-in)', external=ext_best['name'], ext_efc=ext_best.efc_score,
         internal=int_best_nb.iloc[0]['name'], int_efc=int_best_nb.iloc[0].efc_score),
    dict(view='best COMPLETE-coverage external vs best internal', external=ext_best_complete['name'],
         ext_efc=ext_best_complete.efc_score, internal=int_best.iloc[0]['name'], int_efc=int_best.iloc[0].efc_score),
    dict(view='best WATCH-LIST (thin) external vs best internal', external=watch_best['name'],
         ext_efc=watch_best.efc_score, internal=int_best.iloc[0]['name'], int_efc=int_best.iloc[0].efc_score),
])
gap['gap_points'] = gap.ext_efc - gap.int_efc
save(gap.round(3), 'gap_size')

# aspirational ceiling — the whole bounded era
ceil_ = G[pop0].sort_values('efc_score', ascending=False).head(15)
save(ceil_[['game_year', 'pitcher', 'name', 'is_cohort', 'coverage', 'role', 'n', 'velo', 'ivb_in', 'spin',
            'whiff_rate', 'rv100', 'shape_grade', 'results_grade', 'ff_elite_composite', 'efc_score', 'archetype_tier']].round(4),
     'aspirational_ceiling')

tiers = G[pop0].archetype_tier.value_counts().rename_axis('tier').reset_index(name='pitcher_seasons')
tiers['share'] = tiers.pitcher_seasons / tiers.pitcher_seasons.sum()
save(tiers.round(4), 'tier_distribution')

# ---------------------------------------------------------------------------
# 5 · Sensitivity matrix — does the answer survive the method?
# ---------------------------------------------------------------------------
def variant(label, gg, pm):
    GG = K.archetype_grades(gg, SPEC, value_suffix='_v', pop_mask=pm)
    cc = GG[GG.pitcher.isin(K.COHORT) & (GG.n >= SPEC.subject_floor)]
    best = cc.sort_values('efc_score', ascending=False).groupby('pitcher').head(1).sort_values('efc_score', ascending=False)
    ca = GG[~GG.pitcher.isin(phi26) & GG.game_year.isin([2025, 2026]) & (GG.n >= SPEC.pop_floor) & GG.efc_score.notna()]
    ca = ca.sort_values('game_year', ascending=False).groupby('pitcher').head(1).sort_values('efc_score', ascending=False)
    s26 = GG[GG.pitcher.isin(phi26) & (GG.game_year == 2026)]
    return dict(variant=label, pop_n=int(pm.sum()),
                cohort_order=' > '.join(best.pitcher.map(K.COHORT)),
                cohort_1=K.COHORT[best.pitcher.iloc[0]],
                candidate_1=NAME.get(ca.pitcher.iloc[0]), candidate_1_year=int(ca.game_year.iloc[0]),
                candidate_top5=' | '.join(ca.pitcher.head(5).map(NAME)),
                staff_elite_arms=int(s26.ff_elite_archetype_flag.sum()),
                bowlan_2026_tier=s26.loc[s26.pitcher == 680742, 'archetype_tier'].iloc[0])

sens = []
gv = g.copy()
for m in ['velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']:
    gv[m + '_v'] = gv[m + '_final']
sens.append(variant('governed (stabilized + trend-adjusted, union frame)', gv, pop0))
gv2 = g.copy()
for m in ['velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']:
    gv2[m + '_v'] = g[m] + (g[m + '_stab_adj'] - g[m + '_stab'])        # trend only
sens.append(variant('no stabilization (trend only)', gv2, pop0))
gv3 = g.copy()
for m in ['velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']:
    gv3[m + '_v'] = g[m + '_stab']                                        # stabilization only
sens.append(variant('no trend adjustment (stabilized only)', gv3, pop0))
gv4 = g.copy()
for m in ['velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']:
    gv4[m + '_v'] = g[m]
sens.append(variant('ungoverned (raw values)', gv4, pop0))
gv5 = g.copy()
for m in ['velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']:
    gv5[m + '_v'] = g[m + '_final']
pm5 = pop0 & g.frame.isin(['PHI', 'VS_PHI'])
sens.append(variant('SG-2 classic population (Phillies logs only)', gv5, pm5))
pm6 = pop0 & g.coverage.eq('COMPLETE')
sens.append(variant('COMPLETE-coverage population only', gv5, pm6))
save(pd.DataFrame(sens), 'sensitivity_matrix')

# ---------------------------------------------------------------------------
# 6 · PART H — the human parent (client notebook claims)
# ---------------------------------------------------------------------------
PPS = U[(U.src == 'phils') & (U.phillies_role == 'pitching')]
hp = []

# HP-1 Wheeler velocity (September 2026.ipynb cell 101, chart 1)
zw = PPS[(PPS.pitcher == 554430) & (PPS.pitch_type == 'FF')]
wv = zw.groupby('game_year').release_speed.agg(
    n='size', mean='mean', p05=lambda s: s.quantile(.05), p25=lambda s: s.quantile(.25), median='median',
    p75=lambda s: s.quantile(.75), p95=lambda s: s.quantile(.95), max='max',
    share_99_plus=lambda s: (s >= 99).mean()).reset_index()
save(wv.round(4), 'hp_wheeler_velo_by_year')
lr = stats.linregress(wv.game_year, wv['median'])
i24, i26 = wv.set_index('game_year').loc[2024], wv.set_index('game_year').loc[2026]
ov = max(0, min(i24.p75, i26.p75) - max(i24.p25, i26.p25)) / (max(i24.p75, i26.p75) - min(i24.p25, i26.p25))
hp.append(dict(id='HP-1a', claim='Wheeler FF velocity "clearly trending down"', source='September 2026.ipynb c101 chart 1',
               client_value='visual', governed_value=f"median {wv['median'].iloc[0]:.1f} ({int(wv.game_year.iloc[0])}) -> {i26['median']:.1f} (2026); slope {lr.slope:+.2f} mph/season, p={lr.pvalue:.3f}",
               verdict='SUPPORTED' if (lr.slope < 0 and lr.pvalue < .05) else ('DIRECTIONAL' if lr.slope < 0 else 'NOT SUPPORTED')))
hp.append(dict(id='HP-1b', claim='"the middle 50% of his FFs in 2026 roughly matches 2024"', source='same subtitle',
               client_value=f"band drawn at {i26.p25:.1f}-{i26.p75:.1f}",
               governed_value=f"2024 IQR {i24.p25:.1f}-{i24.p75:.1f} vs 2026 IQR {i26.p25:.1f}-{i26.p75:.1f}; overlap {ov:.0%}",
               verdict='SUPPORTED' if ov >= .6 else 'PARTLY'))
pre = wv[wv.game_year < 2024]
hp.append(dict(id='HP-1c', claim='"Not approaching that 99 mph mark like prior years"', source='same subtitle',
               client_value='99 mph reference line',
               governed_value=f"99+ share: {', '.join(f'{int(r.game_year)} {r.share_99_plus:.1%}' for r in wv.itertuples())}; 2026 max {i26['max']:.1f}",
               verdict='SUPPORTED' if (i26.share_99_plus < pre.share_99_plus.max()) else 'NOT SUPPORTED'))

# HP-2..4 Painter (charts 2-4) — the client's own half split: month < 7
ap = PPS[(PPS.pitcher == 691725) & (PPS.pitch_type == 'FF')].copy()
ap['month'] = pd.to_datetime(ap.game_date).dt.month
ap['half'] = np.where(ap.month < 7, 'First Half', 'Second Half')
spin_all = ap.release_spin_rate
removed = int((spin_all < 1500).sum())
aps = ap[ap.release_spin_rate >= 1500]
h1, h2 = aps[aps.half == 'First Half'], aps[aps.half == 'Second Half']
t_spin = stats.ttest_ind(h1.release_spin_rate, h2.release_spin_rate, equal_var=False)
ap['ivb_in'] = ap.pfx_z * 12
r1, r2 = ap[ap.half == 'First Half'].ivb_in, ap[ap.half == 'Second Half'].ivb_in
t_ivb = stats.ttest_ind(r1, r2, equal_var=False)
halves = ap.groupby('half').agg(n=('pitch_type', 'size'), first=('game_date', 'min'), last=('game_date', 'max'),
                                velo=('release_speed', 'mean'), spin=('release_spin_rate', 'mean'),
                                ivb_in=('ivb_in', 'mean')).reset_index()
halves['spin_ex_outlier'] = [h1.release_spin_rate.mean(), h2.release_spin_rate.mean()]
for col, a, b in [('spin', h1.release_spin_rate, h2.release_spin_rate), ('ivb', r1, r2)]:
    for q in (5, 25, 50, 75, 95):
        halves[f'{col}_p{q:02d}'] = [a.quantile(q / 100), b.quantile(q / 100)]
halves['spin_outliers_removed'] = [int((ap[ap.half == h].release_spin_rate < 1500).sum()) for h in halves.half]
save(halves.round(3), 'hp_painter_halves')
pg = G[(G.pitcher == 691725) & (G.game_year == 2026)].iloc[0]
hp.append(dict(id='HP-2', claim='Painter "has elite velo"', source='c101 chart 2 subtitle',
               client_value='visual vs Wheeler 2026 band', governed_value=f"velo {pg.velo:.1f} mph -> grade {pg.g_velo:.0f} ({K.grade_label(pg.g_velo)})",
               verdict='SUPPORTED' if pg.g_velo >= 60 else ('PARTLY' if pg.g_velo >= 55 else 'NOT SUPPORTED')))
hp.append(dict(id='HP-3', claim='Painter FF spin: "Clear difference after his demotion"', source='c101 chart 3',
               client_value=f"{h1.release_spin_rate.mean():.0f} vs {h2.release_spin_rate.mean():.0f} rpm (his >=1500 filter removes {removed} pitch)",
               governed_value=f"delta {h2.release_spin_rate.mean() - h1.release_spin_rate.mean():+.0f} rpm = {(h2.release_spin_rate.mean() - h1.release_spin_rate.mean()) / mom.set_index('metric').loc['spin', 'sd']:.2f} population SD, Welch t={t_spin.statistic:.2f}, p={t_spin.pvalue:.2g}",
               verdict='SUPPORTED' if t_spin.pvalue < .05 else 'NOT SUPPORTED'))
hp.append(dict(id='HP-4', claim='Painter FF ride: "Noticeably more after going down to AAA"', source='c101 chart 4',
               client_value=f"{r1.mean():.1f} vs {r2.mean():.1f} in", governed_value=f"delta {r2.mean() - r1.mean():+.2f} in = {(r2.mean() - r1.mean()) / mom.set_index('metric').loc['ivb_in', 'sd']:.2f} population SD (~{10 * (r2.mean() - r1.mean()) / mom.set_index('metric').loc['ivb_in', 'sd']:.1f} grade pts), Welch t={t_ivb.statistic:.2f}, p={t_ivb.pvalue:.2g}",
               verdict=('SUPPORTED (small)' if abs(r2.mean() - r1.mean()) / mom.set_index('metric').loc['ivb_in', 'sd'] < .5 else 'SUPPORTED')
               if (t_ivb.pvalue < .05 and r2.mean() > r1.mean()) else 'NOT SUPPORTED'))

# HP-5 Duran index card, 9/17: "70 FF"
dg = G[(G.pitcher == 661395) & (G.game_year == 2026)].iloc[0]
hp.append(dict(id='HP-5', claim='Duran index card (9/17): "70 FF"', source='September 2026.ipynb c85',
               client_value='70', governed_value=f"shape {dg.shape_grade:.0f} / results {dg.results_grade:.0f} / composite {dg.ff_elite_composite:.0f}; velo {dg.g_velo:.0f}, ride {dg.g_ivb_in:.0f}, spin {dg.g_spin:.0f}, whiff {dg.g_whiff_rate:.0f}, RV {dg.g_rv100:.0f}",
               verdict='SUPPORTED' if dg.ff_elite_composite >= 70 else ('PARTLY' if max(dg.shape_grade, dg.results_grade) >= 70 else 'NOT SUPPORTED')))

# HP-6 Bowlan (Brand Guidelines and Graph Samples.md, 2025 context chart)
KF = K.kellen_frame_raw()
b_raw = KF[KF.pitcher == 680742]
q25_raw = b_raw.pfx_z.quantile(.25)
share_below_raw = float((KF.pfx_z < q25_raw).mean())
UG = U[(U.pitch_type == 'FF')]
b_gov = UG[UG.pitcher == 680742]
q25_gov = b_gov.pfx_z.quantile(.25)
share_below_gov = float((UG.pfx_z < q25_gov).mean())
bg25 = G[(G.pitcher == 680742) & (G.game_year == 2025)].iloc[0]
bg26 = G[(G.pitcher == 680742) & (G.game_year == 2026)].iloc[0]
hp.append(dict(id='HP-6a', claim='Bowlan "gets exceptional vert on his Four-Seam Fastball"', source='Brand Guidelines & Graph Samples, Bowlan violin/histogram',
               client_value=f"his frame: Bowlan's 25th-pctile ride sits above {share_below_raw:.1%} of all FF ({len(KF):,} pitches, all hands, MiLB + dups incl.)",
               governed_value=f"governed frame: {share_below_gov:.1%} of {len(UG):,}; ride grade {bg25.g_ivb_in:.0f} (2025) / {bg26.g_ivb_in:.0f} (2026)",
               verdict='SUPPORTED' if min(bg25.g_ivb_in, bg26.g_ivb_in) >= 60 else 'PARTLY'))
hp.append(dict(id='HP-6b', claim='Bowlan spin: "Does he also spin it exceptionally? Not really."', source='same, commented-out cell',
               client_value='not exceptional', governed_value=f"spin grade {bg25.g_spin:.0f} (2025) / {bg26.g_spin:.0f} (2026)",
               verdict='SUPPORTED' if max(bg25.g_spin, bg26.g_spin) < 60 else 'NOT SUPPORTED'))
hp.append(dict(id='HP-6c', claim='Bowlan: "his FF whiff rate is ridiculous?" / "in 2025 his FF got a ton of whiff"', source='same',
               client_value='question', governed_value=f"2025 whiff {bg25.whiff_rate:.3f} on {int(bg25.swings)} swings -> grade {bg25.g_whiff_rate:.0f}; 2026 {bg26.whiff_rate:.3f} -> {bg26.g_whiff_rate:.0f}",
               verdict='SUPPORTED' if bg25.g_whiff_rate >= 70 else ('PARTLY' if bg25.g_whiff_rate >= 60 else 'NOT SUPPORTED')))
hpdf = save(pd.DataFrame(hp), 'hp_reconciliation')

# frame-contamination receipt for the client's frame
kf_rec = dict(rows_kellen_frame_ff=len(KF), rows_governed_ff=len(UG),
              kellen_frame_dup_pitch_keys=int(KF.duplicated(K.PITCH_KEY).sum()),
              kellen_frame_milb_rows=int((~KF.home_team.isin(K.MLB_CLUBS)).sum()),
              kellen_frame_lhp_rows=int((KF.p_throws == 'L').sum()))
save(pd.DataFrame([kf_rec]).T.reset_index().rename(columns={'index': 'measure', 0: 'value'}), 'hp_client_frame_audit')

# ---------------------------------------------------------------------------
# 7 · DQ scorecard (executed rules)
# ---------------------------------------------------------------------------
dq = []
def rule(rid, dim, desc, ok, obs, sev='FAIL'):
    dq.append(dict(rule=rid, dimension=dim, description=desc, result='PASS' if ok else sev, observed=obs))

rule('DQ-01', 'uniqueness', 'No duplicate PITCH_KEY in the governed union', rec['union_dup_pitch_keys'] == 0, rec['union_dup_pitch_keys'])
rule('DQ-02', 'validity', 'No MiLB rows survive the level gate', int((~U.home_team.isin(K.MLB_CLUBS)).sum()) == 0, int((~U.home_team.isin(K.MLB_CLUBS)).sum()))
rule('DQ-03', 'validity', 'Regular season only', set(U.game_type.unique()) == {'R'}, sorted(U.game_type.unique()))
rule('DQ-04', 'consistency', 'Entity locks: each cohort id has rows and resolves to one display name',
     all(G.pitcher.eq(p).any() for p in K.COHORT), {K.COHORT[p]: int(G.pitcher.eq(p).sum()) for p in K.COHORT})
rule('DQ-05', 'accuracy', 'NR-1 tier-2 name parse agrees with keyed names (accent-folded) >= 97%',
     name_meta['t2_agreement'] >= .97, f"{name_meta['t2_agreement']:.3f} on {name_meta['t2_overlap_n']}")
unres = G[pop0 & G.name.str.startswith('MLBAM')]
rule('DQ-06', 'completeness', 'Unresolved pitcher names in the population (WARN if any)', len(unres) == 0, len(unres), sev='WARN')
ff = F
rule('DQ-07', 'completeness', 'FF release_speed / pfx_z / spin non-null >= 99% (grain: tracked pitch)',
     float(ff[['release_speed', 'pfx_z', 'release_spin_rate']].notna().all(axis=1).mean()) >= .99,
     round(float(ff[['release_speed', 'pfx_z', 'release_spin_rate']].notna().all(axis=1).mean()), 4))
rule('DQ-08', 'completeness', 'delta_run_exp non-null on FF pitches (grain: pitch)', float(ff.delta_run_exp.notna().mean()) >= .99,
     round(float(ff.delta_run_exp.notna().mean()), 4))
rule('DQ-09', 'validity', 'xwOBA populated only on PA-ending rows (grain-aware, D-1)',
     int(ff[ff.events.isna() & ff.estimated_woba_using_speedangle.notna()].shape[0]) == 0,
     int(ff[ff.events.isna() & ff.estimated_woba_using_speedangle.notna()].shape[0]))
rule('DQ-10', 'validity', 'RHP arm side is negative pfx_x (asserted, not assumed)', float(ff.pfx_x.median()) < 0, round(float(ff.pfx_x.median()), 3))
rule('DQ-11', 'consistency', 'Population >= 25 pitcher-seasons (SG-2 floor rule never triggers)', int(pop0.sum()) >= 25, int(pop0.sum()))
nonnormal = mom[~mom.normal_at_05].metric.tolist()
rule('DQ-12', 'distribution', 'Population normality (Shapiro) — WARN per failing metric; twin grade published', len(nonnormal) == 0,
     ','.join(nonnormal) or 'none', sev='WARN')
rule('DQ-13', 'distribution', 'SG-3 skew flag (|z-grade minus rank-grade| >= 10) fires on no population member',
     int(mom.skew_flags.sum()) == 0, int(mom.skew_flags.sum()), sev='WARN')
rule('DQ-14', 'comparability', 'Population is a bounded sampling frame, not MLB-wide (permanent WARN, DPO decision 11)', False,
     f"{int((G[pop0].coverage == 'PARTIAL').sum())} of {int(pop0.sum())} population pitcher-seasons are PARTIAL coverage", sev='WARN')
rule('DQ-15', 'comparability', 'Velocity/spin drift adjusted (SG-6) — every cross-season grade is in 2026 terms',
     bool(trend[trend.metric.isin(['velo', 'spin'])].adjusted.all()), trend[['metric', 'adjusted']].to_dict('records'))
rule('DQ-16', 'accuracy', 'Staff FF volume uses Phillies-log pitches only (mid-season adds not inflated)',
     bool((staff.n_phi <= staff.n).all()), int((staff.n - staff.n_phi).sum()))
rule('DQ-17', 'timeliness', f'Phillies log current through anchor {K.ANCHOR_DATE}', max_phi == K.ANCHOR_DATE, max_phi)
mcf = G[(G.pitcher == 686934) & (G.game_year == 2026)]
rule('DQ-18', 'completeness', 'Cohort subject floor: McFarlane graded THIN (>=50, <100 FF)',
     bool(len(mcf) and mcf.n.iloc[0] >= SPEC.subject_floor and mcf.thin.iloc[0]), int(mcf.n.iloc[0]) if len(mcf) else 0, sev='WARN')
rule('DQ-19', 'validity', 'Parent kernel sha256 matches the pinned uc-pps-030 hash', K.parent_kernel_hash() == K.PARENT_KERNEL_SHA256, K.parent_kernel_hash()[:12])
dqdf = save(pd.DataFrame(dq), 'dq_scorecard')

fresh = pd.DataFrame([
    dict(source='phils_2026.parquet', max_game_date=max_phi, note='Phillies log; anchor'),
    dict(source='nphl (128 files)', max_game_date=str(pd.to_datetime(U[U.src == 'nphl'].game_date).max().date()), note='most player files end 2025'),
    dict(source='identity lookup', max_game_date='2026-09-22', note='MLBAM 694819 = Jacob Misiorowski (Baseball Savant player page via web search) — identity only, no data'),
    dict(source='carry-in', max_game_date='2026-09-17', note='Bowlan left 9/17 vs NYM with a suspected oblique (client notebook c85) — not in data'),
])
save(fresh, 'freshness_manifest')

# ---------------------------------------------------------------------------
# 8 · Headlines + dashboard payload (the only numbers prose may use)
# ---------------------------------------------------------------------------
def r(x, d=3):
    return None if (x is None or (isinstance(x, float) and np.isnan(x))) else round(float(x), d)

bow26 = G[(G.pitcher == 680742) & (G.game_year == 2026)].iloc[0]
pop_rank_bow = int((G.loc[pop0, 'efc_score'] > bow26.efc_score).sum()) + 1
H = dict(
    universe=rec, pop_n=int(pop0.sum()), era=list(SPEC.era), graded_n=int((G.n >= SPEC.subject_floor).sum()),
    name_t2_agreement=r(name_meta['t2_agreement'], 4), name_t2_overlap=name_meta['t2_overlap_n'],
    unresolved_in_pop=int(len(unres)),
    tiers={t: int(n) for t, n in zip(tiers.tier, tiers.pitcher_seasons)},
    elite_share_of_population=r(float((G[pop0].archetype_tier == 'ELITE').mean()), 4),
    stab={row.metric: dict(k=r(row.k, 1), r_full=r(row.r_full), shrink=bool(row.shrink), rel50=r(row.reliability_at_subject_floor)) for row in stab.itertuples()},
    trend={row.metric: dict(slope=r(row.slope_per_season, 4), p=r(row.p_value, 5), adjusted=bool(row.adjusted), shift=r(row.shift_2018_to_ref, 3)) for row in trend.itertuples()},
    cohort=lb.round(4).to_dict('records'),
    bowlan26=dict(efc=r(bow26.efc_score), shape=r(bow26.shape_grade, 0), results=r(bow26.results_grade, 0),
                  composite=r(bow26.ff_elite_composite, 0), pop_rank=pop_rank_bow, velo=r(bow26.velo, 2), ivb=r(bow26.ivb_in, 2),
                  spin=r(bow26.spin, 0), whiff=r(bow26.whiff_rate), rv100=r(bow26.rv100, 2), n=int(bow26.n),
                  g_velo=r(bow26.g_velo, 0), g_ivb=r(bow26.g_ivb_in, 0), g_spin=r(bow26.g_spin, 0), g_whiff=r(bow26.g_whiff_rate, 0), g_rv=r(bow26.g_rv100, 0)),
    efs={row.flag: dict(share=r(row.share, 4), elite_ff=int(row.elite_ff), total_ff=int(row.total_ff)) for row in efs.itertuples()},
    staff=staff.sort_values('efc_score', ascending=False)[['name', 'role', 'n_phi', 'shape_grade', 'results_grade', 'ff_elite_composite', 'efc_score', 'archetype_tier']].round(3).to_dict('records'),
    watch=watch.head(10)[['name', 'game_year', 'coverage', 'role', 'games', 'n', 'swings', 'shape_grade', 'results_grade',
                          'ff_elite_composite', 'efc_score', 'efc_score_ungoverned', 'archetype_tier', 'velo', 'ivb_in', 'spin', 'whiff_rate']].round(3).to_dict('records'),
    candidates=cand.head(15)[['cand_rank', 'ungoverned_rank', 'name', 'game_year', 'coverage', 'role', 'games', 'n', 'swings',
                              'shape_grade', 'results_grade', 'ff_elite_composite', 'efc_score', 'efc_score_ungoverned', 'archetype_tier',
                              'velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100']].round(3).to_dict('records'),
    needle=needle.sort_values(['board', 'needle_rank']).round(4).to_dict('records'),
    gap=gap.round(3).to_dict('records'),
    ceiling=ceil_.head(10)[['name', 'game_year', 'coverage', 'efc_score', 'ff_elite_composite', 'archetype_tier']].round(3).to_dict('records'),
    sensitivity=pd.DataFrame(sens).to_dict('records'),
    hp=hpdf.to_dict('records'), client_frame=kf_rec,
    moments=mom.round(4).to_dict('records'),
    dq=dict(passed=int((dqdf.result == 'PASS').sum()), warn=int((dqdf.result == 'WARN').sum()), fail=int((dqdf.result == 'FAIL').sum())),
    ws_best=ws_best[['arm', 'game_year'] + [c for c in ws_best if c.startswith('rank_w')]].to_dict('records'),
    ws26=ws26[['arm'] + [c for c in ws26 if c.startswith('rank_w')]].to_dict('records'),
    wheeler_velo=wv.round(3).to_dict('records'), painter_halves=halves.round(3).to_dict('records'),
)
(OUT / f"{PFX}headlines.json").write_text(json.dumps(H, indent=1, default=str))

# dashboard payload: every graded pitcher-season (compact)
pay = graded[['game_year', 'pitcher', 'name', 'is_cohort', 'on_phi_2026', 'coverage', 'role', 'n', 'games', 'thin', 'pop_member',
              'velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100', 'g_velo', 'g_ivb_in', 'g_spin', 'g_whiff_rate', 'g_rv100',
              'shape_score', 'results_score', 'shape_grade', 'results_grade', 'ff_elite_composite', 'efc_score', 'archetype_tier']].copy()
pay['arm'] = pay.pitcher.map(K.COHORT).fillna('')
(OUT / f"{PFX}payload.json").write_text(pay.round(3).to_json(orient='records'))
print(json.dumps(dict(pop=int(pop0.sum()), dq=H['dq'], cohort_1=lb.iloc[0].arm, cand_1=cand.iloc[0]['name']), default=str))
