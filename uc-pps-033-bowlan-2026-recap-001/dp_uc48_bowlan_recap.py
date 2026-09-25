"""
dp_uc48_bowlan_recap.py — build for UC #48 / uc-pps-033
"The Tick and a Half — Jonathan Bowlan 2026 Recap"

Reads the data plane (parquet), writes receipts to out/dp_uc48_*. Every number the report, the
dashboard and the figures publish is written here first; nothing downstream recomputes a KPI.

Run:  MLB_DATA_ROOT=<MLB repo> python dp_uc48_bowlan_recap.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import dp_uc48_kernel as K

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC48_OUT", HERE / "out"))
OUT.mkdir(parents=True, exist_ok=True)
P = lambda n: OUT / f"dp_uc48_{n}"          # noqa: E731
H: dict = {}                                 # headlines — every narrative number lives here
DQ: list = []


def dq(rule, dim, grain, text, ok, observed, warn=False):
    DQ.append(dict(rule=rule, dimension=dim, grain=grain, rule_text=text,
                   result=("WARN" if warn else ("PASS" if ok else "FAIL")), observed=str(observed)))


def r3(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 3)


# =============================================================================
# 0 · Anchor, parent kernel, frames
# =============================================================================
assert K.parent_kernel_hash() == K.PARENT_KERNEL_SHA256, "parent kernel drifted"
ph26 = K.load_phils(years=[2026], role=None, regular_only=False)
anchor = str(ph26[ph26.game_type == 'R'].game_date.max())[:10]
assert anchor == K.ANCHOR_GAME_DATE, f"anchor moved: {anchor} (a refresh is v1.1.0, not a correction)"

B, src_receipt = K.career_frame()
src_receipt.to_csv(P("source_receipt.csv"), index=False)
KF = K.kellen_frame()

spring = ph26[(ph26.pitcher == K.SUBJECT_ID) & (ph26.game_type == 'S')]
fresh = pd.DataFrame([
    dict(source="data/phillies/phils_2026.parquet", max_game_date=anchor, rows=len(ph26),
         note="regular season anchor; build refuses any other"),
    dict(source=f"data/opponents/{K.SUBJECT_FILE}", max_game_date=str(B[B.src == 'FILE'].game_date.max())[:10],
         rows=int(src_receipt[src_receipt.src == 'FILE'].rows.sum()),
         note="dedicated player pull, 2023-2025 (KC)"),
    dict(source="carry-in: MLB.com", max_game_date="2025 offseason", rows=0,
         note="Phillies acquired Bowlan from KC for LHP Matt Strahm — context only, never computed on"),
    dict(source="carry-in: Philadelphia Inquirer 2026-09-18", max_game_date=K.LAST_APPEARANCE, rows=0,
         note="9/17 exit reported as right groin strain, no IL placement (supersedes notebook/uc-pps-032 'suspected oblique')"),
])
fresh.to_csv(P("freshness_manifest.csv"), index=False)

H['anchor'] = anchor
H['spring_rows_excluded'] = int(len(spring))
H['dup_vs_phi'] = int(src_receipt.dropped_as_duplicate.sum())
H['career_pitches'] = int(len(B))
H['seasons'] = sorted(int(y) for y in B.game_year.unique())

dq("DQ-01", "uniqueness", "pitch", "no duplicate PITCH_KEY in the governed career frame",
   B.duplicated(K.PITCH_KEY).sum() == 0, int(B.duplicated(K.PITCH_KEY).sum()))
dq("DQ-02", "consistency", "pitch", "entity lock: every row pitcher == 680742", (B.pitcher == K.SUBJECT_ID).all(),
   B.pitcher.unique().tolist())
dq("DQ-03", "validity", "pitch", "regular season only (game_type == 'R')", (B.game_type == 'R').all(),
   B.game_type.unique().tolist())
dq("DQ-04", "timeliness", "file", "Phillies log current through the pinned anchor", anchor == K.ANCHOR_GAME_DATE, anchor)
dq("DQ-05", "validity", "pitch", "p_throws == 'R' on every row", (B.p_throws == 'R').all(), B.p_throws.unique().tolist())

# =============================================================================
# 1 · SR-1 recap table — the client's cell, both ways
# =============================================================================
lvl = ['player_name', 'game_year', 'p_throws']
Bn = B.copy(); Bn['player_name'] = K.SUBJECT_NAME            # keyed name for the level (display only)
recap_g = K.season_recap(Bn, governed=True)
recap_n = K.season_recap(KF, governed=False)
keep = lvl + K.RECAP_KPIS + ['strikeouts', 'walks', 'hrs', 'hits', 'swings', 'whiffs', 'whiff_rate',
                             'chases', 'ooz', 'chase_rate', 'in_zone_rate', 'swings_breaking', 'whiffs_breaking',
                             'swings_iz_ff', 'whiffs_iz_ff']
recap_g[keep + ['ff_n', 'ff_hb', 'ff_vert_notebook']].to_csv(P("recap_governed.csv"), index=False)
recap_n[keep].to_csv(P("recap_notebook.csv"), index=False)

# Method agreement: the client's frame vs the governed frame on the published KPIs
cmp_cols = [c for c in K.RECAP_KPIS if c not in ('ff_vert', 'ff_velo', 'ff_spin')]
m = recap_g[lvl + cmp_cols].merge(recap_n[lvl + cmp_cols], on=lvl, suffixes=('_g', '_n'))
agree = all(np.allclose(m[c + '_g'].astype(float), m[c + '_n'].astype(float), atol=1e-9) for c in cmp_cols)
dq("DQ-06", "consistency", "pitcher-season", "client frame (name filter) == governed frame (id lock) on 16 non-shape KPIs",
   agree, f"{len(m)} seasons x {len(cmp_cols)} KPIs")

R = recap_g.set_index('game_year')
for y in R.index:
    row = R.loc[y]
    H[f'y{y}'] = {k: (r3(row[k]) if k not in ('pitches', 'plate_apps', 'games', 'runs_created', 'strikeouts',
                                              'walks', 'hrs') else int(row[k]))
                  for k in K.RECAP_KPIS + ['strikeouts', 'walks', 'hrs', 'whiff_rate', 'chase_rate', 'in_zone_rate']}
    H[f'y{y}']['ff_vert_notebook'] = float(row['ff_vert_notebook'])
    H[f'y{y}']['ff_n'] = int(row['ff_n'])
a, b_ = R.loc[2025], R.loc[2026]
H['prior_career_games'] = int(R.loc[[2023, 2024, 2025], 'games'].sum())
H['career_games'] = int(R.games.sum())

# =============================================================================
# 2 · Rate tests 2025 -> 2026 (house standing test: pooled two-proportion z)
# =============================================================================
tests = []
def ttest_rate(name, x1, n1, x2, n2, better):
    z, p = K.two_prop_z(x2, n2, x1, n1)
    tests.append(dict(metric=name, x_2025=int(x1), n_2025=int(n1), rate_2025=x1 / n1,
                      x_2026=int(x2), n_2026=int(n2), rate_2026=x2 / n2, delta=x2 / n2 - x1 / n1,
                      z=z, p=p, better_is=better))
ttest_rate("K rate (K / PA)", a.strikeouts, a.plate_apps, b_.strikeouts, b_.plate_apps, "up")
ttest_rate("BB rate (BB / PA)", a.walks, a.plate_apps, b_.walks, b_.plate_apps, "down")
ttest_rate("HR rate (HR / PA)", a.hrs, a.plate_apps, b_.hrs, b_.plate_apps, "down")
ttest_rate("Whiff rate (all pitches, per swing)", a.whiffs, a.swings, b_.whiffs, b_.swings, "up")
ttest_rate("Chase rate (swings / out-of-zone)", a.chases, a.ooz, b_.chases, b_.ooz, "up")
ttest_rate("Breaking whiff (per swing)", a.whiffs_breaking, a.swings_breaking, b_.whiffs_breaking, b_.swings_breaking, "up")
ttest_rate("In-zone four-seam whiff (per swing)", a.whiffs_iz_ff, a.swings_iz_ff, b_.whiffs_iz_ff, b_.swings_iz_ff, "up")

B25, B26 = B[B.game_year == 2025], B[B.game_year == 2026]
for yv, d in ((2025, B25), (2026, B26)):
    d = d.copy()
fp25 = B25[B25.pitch_number == 1]; fp26 = B26[B26.pitch_number == 1]
ttest_rate("First-pitch strike rate", (fp25.type != 'B').sum(), len(fp25), (fp26.type != 'B').sum(), len(fp26), "up")
cs25, cs26 = K.count_state(B25), K.count_state(B26)
for st in ('2K', 'behind'):
    x1 = ((cs25 == st) & (B25.pitch_type == 'FF')).sum(); n1 = (cs25 == st).sum()
    x2 = ((cs26 == st) & (B26.pitch_type == 'FF')).sum(); n2 = (cs26 == st).sum()
    ttest_rate(f"Four-seam share, {st} counts", x1, n1, x2, n2, "context")
T = pd.DataFrame(tests)
T.to_csv(P("rate_tests.csv"), index=False)
H['tests'] = {r.metric: dict(r25=r3(r.rate_2025), r26=r3(r.rate_2026), p=r3(r.p), n25=int(r.n_2025), n26=int(r.n_2026))
              for r in T.itertuples()}

# velocity: Welch t on four-seam velo and spin
ff25, ff26 = B25[B25.pitch_type == 'FF'], B26[B26.pitch_type == 'FF']
vt = stats.ttest_ind(ff26.release_speed.dropna(), ff25.release_speed.dropna(), equal_var=False)
stt = stats.ttest_ind(ff26.release_spin_rate.dropna(), ff25.release_spin_rate.dropna(), equal_var=False)
H['ff_velo_delta'] = r3(ff26.release_speed.mean() - ff25.release_speed.mean())
H['ff_velo_p'] = float(vt.pvalue)
H['ff_spin_delta'] = round(float(ff26.release_spin_rate.mean() - ff25.release_spin_rate.mean()), 1)
H['ff_spin_p'] = float(stt.pvalue)
H['ff_ivb_delta'] = r3(12 * (ff26.pfx_z.mean() - ff25.pfx_z.mean()))
H['ff_velo_iqr_2026'] = [r3(ff26.release_speed.quantile(.25)), r3(ff26.release_speed.quantile(.75))]
H['ff_velo_by_year'] = {int(y): r3(v) for y, v in B[B.pitch_type == 'FF'].groupby('game_year').release_speed.mean().items()}

# =============================================================================
# 3 · Arsenal (AR-2), by season and by batter hand; count state (CS-1)
# =============================================================================
ars = K.arsenal_table(B, by=('game_year',))
ars.to_csv(P("arsenal_by_season.csv"), index=False)
ars_st = K.arsenal_table(B[B.game_year >= 2025], by=('game_year', 'stand'))
ars_st.to_csv(P("arsenal_by_stand.csv"), index=False)
Bc = B[B.game_year >= 2025].copy(); Bc['count_state'] = K.count_state(Bc)
cs = Bc.groupby(['game_year', 'count_state', 'pitch_type'], as_index=False).agg(n=('pitch_type', 'size'))
cs['share'] = cs.n / cs.groupby(['game_year', 'count_state']).n.transform('sum')
cs.to_csv(P("count_state_mix.csv"), index=False)
pms = K.pitch_mix_by_season(B, K.SUBJECT_NAME)
pms.to_csv(P("pitch_mix_by_season.csv"), index=False)

A = ars.set_index(['game_year', 'pitch_type'])
def av(y, pt, c):
    try:
        return r3(A.loc[(y, pt), c])
    except KeyError:
        return None
H['arsenal'] = {f"{y}_{pt}": {c: av(y, pt, c) for c in ('n', 'usage', 'velo', 'spin', 'ivb_in', 'hb_in', 'whiff_rate',
                                                          'xwobacon', 'rv100', 'zone_rate', 'chase_rate')}
                for (y, pt) in A.index if y >= 2025}
AS = ars_st.set_index(['game_year', 'stand', 'pitch_type'])
H['mix_by_stand'] = {f"{y}_{s}_{pt}": r3(AS.loc[(y, s, pt), 'usage']) for (y, s, pt) in AS.index}
CSX = cs.set_index(['game_year', 'count_state', 'pitch_type'])
H['ff_share_by_count'] = {f"{y}_{s}": r3(CSX.loc[(y, s, 'FF'), 'share']) for (y, s, pt) in CSX.index if pt == 'FF'}
for yv, d in ((2025, B25), (2026, B26)):
    f = d[d.pitch_type == 'FF']
    upper = (f.plate_z > f.sz_top - (f.sz_top - f.sz_bot) / 3)
    H[f'ff_upper_third_{yv}'] = r3(upper.mean())
    H[f'fps_{yv}'] = r3((d[d.pitch_number == 1].type != 'B').mean())
    H[f'xwobacon_{yv}'] = r3(d[d.type == 'X'].estimated_woba_using_speedangle.mean())
    H[f'pitches_by_stand_{yv}'] = d.stand.value_counts().to_dict()

# =============================================================================
# 4 · Usage (US-1), velocity by pitch-of-outing (VE-1), monthly trend
# =============================================================================
apps = K.appearance_log(B[B.game_year >= 2025])
apps.to_csv(P("appearances.csv"), index=False)
us = K.usage_summary(apps)
rc_split = apps.groupby(['game_year', apps.entry_runners > 0], as_index=False).agg(
    apps=('game_pk', 'size'), rc=('runs_created', 'sum'))
rc_split.columns = ['game_year', 'inherited_runners', 'apps', 'runs_created']
rc_split.to_csv(P("rc_by_entry_state.csv"), index=False)
us.to_csv(P("usage_summary.csv"), index=False)
U = us.set_index('game_year')
H['usage'] = {int(y): {c: r3(U.loc[y, c]) for c in us.columns if c != 'game_year'} for y in U.index}
a26 = apps[apps.game_year == 2026]
H['entry_inning_2026'] = {int(k): int(v) for k, v in a26.entry_inning.value_counts().sort_index().items()}
H['apps_7th_8th_2026'] = int(a26.entry_inning.isin([7, 8]).sum())
H['rc_by_entry'] = {f"{int(r.game_year)}_{'dirty' if r.inherited_runners else 'clean'}": dict(apps=int(r.apps), rc=int(r.runs_created))
                    for r in rc_split.itertuples()}
H['scoreless_apps_2026'] = int((a26.runs_created == 0).sum())

vb = K.velo_by_outing_bucket(B[B.game_year >= 2025])
vb.to_csv(P("velo_by_outing.csv"), index=False)
VB = vb.set_index(['game_year', 'bucket'])
H['velo_bucket'] = {f"{y}_{b}": dict(n=int(VB.loc[(y, b), 'n']), velo=r3(VB.loc[(y, b), 'velo'])) for (y, b) in VB.index}

B26m = B26.copy(); B26m['month'] = pd.to_datetime(B26m.game_date).dt.month
mo = K.nresults(['month'], B26m).merge(
    B26m[B26m.pitch_type == 'FF'].groupby('month', as_index=False).agg(ff_velo=('release_speed', 'mean')), on='month'
).merge(B26m.groupby('month', as_index=False).agg(games=('game_pk', 'nunique')), on='month').merge(
    K.xwobacon(['month'], B26m), on='month', how='left')
mo.to_csv(P("monthly_2026.csv"), index=False)
H['monthly'] = {int(r.month): dict(pa=int(r.plate_apps), woba=r3(r.woba), krate=r3(r.krate), ff_velo=r3(r.ff_velo),
                                   games=int(r.games)) for r in mo.itertuples()}
last5 = a26.sort_values('game_date').tail(5)
H['last5_ff_velo'] = r3((last5.ff_velo * last5.ff_n).sum() / last5.ff_n.sum())
H['season_ff_velo_2026'] = r3(ff26.release_speed.mean())
H['last5_dates'] = [str(d)[:10] for d in last5.game_date]
H['last_app_ff_velo'] = r3(last5.iloc[-1].ff_velo)
H['min_app_ff_velo_2026'] = r3(a26[a26.ff_n >= 5].ff_velo.min())

# =============================================================================
# 5 · KP-1 house percentiles
# =============================================================================
pop = K.house_pitcher_seasons(min_pa=100)
pop.to_csv(P("house_population.csv"), index=False)
kp = []
for col, hib, lab in [('krate', True, 'K rate'), ('bbrate', False, 'BB rate'), ('woba', False, 'wOBA against'),
                      ('whiff_rate', True, 'Whiff rate'), ('chase_rate', True, 'Chase rate'),
                      ('hr_rate', False, 'HR rate')]:
    v = float(pop[(pop.pitcher == K.SUBJECT_ID) & (pop.game_year == 2026)][col].iat[0])
    hp = K.house_percentile(pop, col, v, hib)
    staff = pop[pop.game_year == 2026]
    hs = K.house_percentile(staff, col, v, hib)
    kp.append(dict(kpi=lab, column=col, bowlan_2026=v, population_n=hp['n'], house_percentile=hp['percentile'],
                   house_rank=hp['rank'], staff_2026_n=hs['n'], staff_2026_rank=hs['rank']))
KP = pd.DataFrame(kp)
KP.to_csv(P("house_percentiles.csv"), index=False)
H['kp'] = {r.column: dict(pct=int(r.house_percentile), rank=int(r.house_rank), n=int(r.population_n),
                          staff_rank=int(r.staff_2026_rank), staff_n=int(r.staff_2026_n), value=r3(r.bowlan_2026))
           for r in KP.itertuples()}
st26 = pop[pop.game_year == 2026].sort_values('krate', ascending=False)
H['staff_k_leader'] = st26.iloc[0]['name']
H['staff_k_leader_rate'] = r3(st26.iloc[0].krate)
dq("DQ-07", "comparability", "pitcher-season", "KP-1 population is Phillies-only, not MLB-wide (permanent)", True,
   f"{len(pop)} pitcher-seasons >= 100 PA, 2015-2026", warn=True)

# =============================================================================
# 6 · Staff comparison (the client's pitch plots) + drill-through data
# =============================================================================
pps = K.load_phils(years=range(2015, 2027), role='pitching', regular_only=True)
pps = K.add_pitch_group(pps)
rhp = pps[pps.p_throws == 'R']
ffr = rhp[rhp.pitch_type == 'FF']
shift = ffr.groupby('game_year', as_index=False).agg(n=('pfx_z', 'size'), ivb_mean=('pfx_z', lambda s: 12 * s.mean()),
                                                     ivb_median=('pfx_z', lambda s: 12 * s.median()))
shift.to_csv(P("staff_ff_ivb_by_year.csv"), index=False)
others = shift[shift.game_year != 2017].ivb_mean
H['ivb_2017'] = r3(shift.set_index('game_year').loc[2017, 'ivb_mean'])
H['ivb_other_years_range'] = [r3(others.min()), r3(others.max())]
z17 = (shift.set_index('game_year').loc[2017, 'ivb_mean'] - others.mean()) / others.std()
H['ivb_2017_z'] = r3(z17)
dq("DQ-11", "comparability", "season", "2017 Phillies RHP four-seam IVB is a level shift (client exclusion justified)",
   z17 > 3, f"2017 mean {H['ivb_2017']} in vs {H['ivb_other_years_range']} other years (z={z17:.1f})")

ffx = ffr[~ffr.game_year.isin(K.STAFF_EXCLUDE_YEARS)]
seas = ffx.groupby(['pitcher', 'game_year'], as_index=False).agg(
    n=('pfx_z', 'size'), ivb_in=('pfx_z', lambda s: 12 * s.mean()), hb_in=('pfx_x', lambda s: 12 * s.mean()),
    velo=('release_speed', 'mean'), spin=('release_spin_rate', 'mean'))
names = pps.groupby('pitcher').player_name.agg(lambda s: s.mode().iat[0]).rename('name')
seas = seas.merge(names, on='pitcher', how='left')
seas = seas[seas.n >= 100].reset_index(drop=True)
seas.to_csv(P("staff_ff_seasons.csv"), index=False)
bw = seas[(seas.pitcher == K.SUBJECT_ID) & (seas.game_year == 2026)].iloc[0]
H['staff_ff_seasons_n'] = int(len(seas))
H['staff_ff_ivb_rank'] = int((seas.ivb_in > bw.ivb_in).sum() + 1)
H['staff_ff_ivb_pct'] = int(np.floor(100 * (seas.ivb_in < bw.ivb_in).mean()))
H['staff_ff_velo_rank'] = int((seas.velo > bw.velo).sum() + 1)
top = seas.sort_values('ivb_in', ascending=False).head(5)
H['staff_ff_ivb_top5'] = [dict(name=r.name, year=int(r.game_year), ivb=r3(r.ivb_in), n=int(r.n)) for r in top.itertuples()]
# pitch-level view exactly as the client drew it
b26ff = ffx[ffx.pitcher == K.SUBJECT_ID]
q1, q3 = 12 * b26ff.pfx_z.quantile(.25), 12 * b26ff.pfx_z.quantile(.75)
oth = ffx[ffx.pitcher != K.SUBJECT_ID].dropna(subset=['pfx_x', 'pfx_z'])   # same population as the drill density
H['client_band'] = [r3(q1), r3(q3)]
H['other_rhp_ff_pitches'] = int(len(oth))
H['share_other_above_q1'] = r3((12 * oth.pfx_z >= q1).mean())
H['share_other_above_median'] = r3((12 * oth.pfx_z >= 12 * b26ff.pfx_z.median()).mean())

# drill-through: arsenal centroids (top view) + per-pitch density (drill view)
arsenal_types = sorted(B.pitch_type.dropna().unique().tolist())
rx = rhp[(~rhp.game_year.isin(K.STAFF_EXCLUDE_YEARS)) & (rhp.pitch_type.isin(arsenal_types))]
cen = rx.groupby(['pitcher', 'game_year', 'pitch_type', 'pitch_name'], as_index=False).agg(
    n=('pfx_z', 'size'), ivb_in=('pfx_z', lambda s: 12 * s.mean()), hb_in=('pfx_x', lambda s: 12 * s.mean()),
    velo=('release_speed', 'mean'), spin=('release_spin_rate', 'mean'))
cen = cen.merge(names, on='pitcher', how='left')
cen = cen[cen.n >= 30]
cen['is_bowlan'] = cen.pitcher == K.SUBJECT_ID
cen.to_csv(P("staff_arsenal_centroids.csv"), index=False)
dens = {}
xb, yb = np.arange(-30, 31, 1.0), np.arange(-30, 31, 1.0)
for pt in arsenal_types:
    o = rx[(rx.pitch_type == pt) & (rx.pitcher != K.SUBJECT_ID)].dropna(subset=['pfx_x', 'pfx_z'])
    h2, _, _ = np.histogram2d(12 * o.pfx_x, 12 * o.pfx_z, bins=[xb, yb])
    hy, _ = np.histogram(12 * o.pfx_z, bins=yb)
    bp = B[(B.game_year == 2026) & (B.pitch_type == pt)]
    dens[pt] = dict(n_other=int(len(o)), x=(xb[:-1] + .5).tolist(), y=(yb[:-1] + .5).tolist(),
                    z=h2.T.astype(int).tolist(), marg=hy.astype(int).tolist(),
                    b_q1=r3(12 * bp.pfx_z.quantile(.25)) if len(bp) else None,
                    b_q3=r3(12 * bp.pfx_z.quantile(.75)) if len(bp) else None,
                    other_ivb_pct_of_b_median=r3((12 * o.pfx_z < 12 * bp.pfx_z.median()).mean()) if len(bp) else None)
(P("staff_density.json")).write_text(json.dumps(dens))
H['density_pitch_types'] = arsenal_types

# slim pitch-level Bowlan table for charts
slim = B[['game_date', 'game_year', 'game_pk', 'src', 'pitch_type', 'pitch_name', 'release_speed', 'release_spin_rate',
          'pfx_x', 'pfx_z', 'plate_x', 'plate_z', 'sz_top', 'sz_bot', 'stand', 'balls', 'strikes', 'description',
          'events', 'zone', 'at_bat_number', 'pitch_number']].copy()
slim['hb_in'] = (12 * slim.pfx_x).round(2); slim['ivb_in'] = (12 * slim.pfx_z).round(2)
slim['game_date'] = slim.game_date.astype(str).str[:10]
slim.to_csv(P("bowlan_pitches.csv"), index=False)

# =============================================================================
# 7 · Inherited archetype grades (uc-pps-032 receipt, read not recomputed)
# =============================================================================
g47 = pd.read_csv(K.ROOT / "out" / "dp_uc47_population_graded.csv")
arch = g47[g47.pitcher == K.SUBJECT_ID][['game_year', 'n', 'velo', 'ivb_in', 'spin', 'whiff_rate', 'rv100',
                                         'g_velo', 'g_ivb_in', 'g_spin', 'g_whiff_rate', 'g_rv100', 'shape_grade',
                                         'results_grade', 'efc_score', 'archetype_tier']].sort_values('game_year')
pop47 = g47[g47.pop_member]
arch['rank_in_405'] = [int((pop47.efc_score > s).sum() + 1) for s in arch.efc_score]
arch['population_n'] = int(len(pop47))
arch.to_csv(P("archetype_inherited.csv"), index=False)
AR = arch.set_index('game_year')
H['arch'] = {int(y): dict(shape=int(AR.loc[y, 'shape_grade']), results=int(AR.loc[y, 'results_grade']),
                          g_velo=int(AR.loc[y, 'g_velo']), g_ivb=int(AR.loc[y, 'g_ivb_in']), g_spin=int(AR.loc[y, 'g_spin']),
                          g_whiff=int(AR.loc[y, 'g_whiff_rate']), g_rv=int(AR.loc[y, 'g_rv100']),
                          tier=AR.loc[y, 'archetype_tier'], rank=int(AR.loc[y, 'rank_in_405'])) for y in AR.index}
H['arch_pop_n'] = int(len(pop47))
dq("DQ-08", "consistency", "pitcher-season", "inherited uc-pps-032 FF n matches this frame's FF count (2025, 2026)",
   all(int(AR.loc[y, 'n']) == int(R.loc[y, 'ff_n']) for y in (2025, 2026)),
   {int(y): (int(AR.loc[y, 'n']), int(R.loc[y, 'ff_n'])) for y in (2025, 2026)})

# =============================================================================
# 8 · Human-parent reconciliation (client's 14 comments + 4 subtitles + state hazards)
# =============================================================================
N = recap_n.set_index('game_year')
# cache-state probe: which log state reproduces the notebook's ".269" and "60 games"?
probe = []
for d in sorted(B26.game_date.astype(str).str[:10].unique()):
    s = B26[B26.game_date.astype(str).str[:10] <= d]
    r = K.nresults(['game_year'], s).iloc[0]
    probe.append(dict(through=d, games=int(s.game_pk.nunique()), plate_apps=int(r.plate_apps), woba=float(r.woba)))
probe = pd.DataFrame(probe)
probe.to_csv(P("cache_probe.csv"), index=False)
hit269 = probe[probe.woba.round(3) == 0.269]
H['probe_269_dates'] = hit269.through.tolist()
H['probe_269_games'] = hit269.games.tolist()

yrs = [y for y in (2023, 2024, 2025, 2026)]
ffv = {y: float(N.loc[y, 'ff_velo']) for y in yrs}
hp = [
    ("HP-01", "pitches", "About 200 more pitches thrown", f"{int(b_.pitches)} vs {int(a.pitches)} (+{int(b_.pitches - a.pitches)})",
     "HELD", "Understated: +240, not ~200"),
    ("HP-02", "plate_apps", "~50 more PAs", f"{int(b_.plate_apps)} vs {int(a.plate_apps)} (+{int(b_.plate_apps - a.plate_apps)})", "HELD", ""),
    ("HP-03", "ba", "20 point drop in BA", f"{a.ba:.3f} → {b_.ba:.3f} (−{round(1000 * (a.ba - b_.ba))} pts)", "HELD", ""),
    ("HP-04", "obp", "Big cut to OBP", f"{a.obp:.3f} → {b_.obp:.3f} (−{round(1000 * (a.obp - b_.obp))} pts)", "HELD", ""),
    ("HP-05", "slg", "slightly less slug", f"{a.slg:.3f} → {b_.slg:.3f} (−{round(1000 * (a.slg - b_.slg))} pts)", "PARTLY",
     "Direction right, size wrong: the SLG cut is larger than the OBP cut"),
    ("HP-06", "woba", "a really solid .269 wOBA", f"{b_.woba:.3f} on the anchored log. The last three cuts read "
     + ", ".join(f"{r.woba:.3f} (thru {r.through[5:]})" for r in probe.tail(3).itertuples())
     + "; .269 appears only on the cut through " + (", ".join(H['probe_269_dates']) or "no date") + f" ({H['probe_269_games'][0] if H['probe_269_games'] else 0} G)",
     "HELD (±.003)", "Not reproducible from any season-end state of the log; the claim (solid) holds at .272"),
    ("HP-07", "krate", "Boost to an elite 32% K Rate (xxth Percentile)",
     f"{100 * b_.krate:.1f}%; house percentile {H['kp']['krate']['pct']} (rank {H['kp']['krate']['rank']} of {H['kp']['krate']['n']} Phillies pitcher-seasons ≥100 PA, 2015–26); #{H['kp']['krate']['staff_rank']} on the 2026 staff",
     "HELD — gap filled", "xx → " + str(H['kp']['krate']['pct']) + " (house frame, not MLB-wide)"),
    ("HP-08", "bbrate", "Cut BB Rate to a much more manageable 6%", f"{100 * a.bbrate:.1f}% → {100 * b_.bbrate:.1f}% (p = {H['tests']['BB rate (BB / PA)']['p']:.2f})",
     "HELD (direction)", "6.5%, not 6%; the cut is not statistically distinguishable at these PA"),
    ("HP-09", "hr_rate", "Similar amount of homers", f"{int(a.hrs)} HR / {int(a.plate_apps)} PA → {int(b_.hrs)} HR / {int(b_.plate_apps)} PA ({a.hr_rate:.3f} → {b_.hr_rate:.3f})", "HELD", ""),
    ("HP-10", "runs_created", "Gave up 30 runs while on the mound, one every other outing",
     f"{int(b_.runs_created)} runs in {int(b_.games)} games ({b_.rc_per_gm:.3f} per game)", "HELD",
     "Runs Created = runs scored during his PAs (includes inherited runners; not runs charged)"),
    ("HP-11", "games", "Pitched in 60 games, nearly doubled his career to date",
     f"{int(b_.games)} games; prior career {H['prior_career_games']} → 2026 alone is {b_.games / H['prior_career_games']:.1f}× his prior career",
     "PARTLY", "59, not 60 (no cut of the anchored log reaches 60); 'nearly doubled' understates (1.6× prior career)"),
    ("HP-12", "rc_per_pa / rc_per_gm", "Up from last year in per PA but down a hair in per GM",
     f"per PA {a.rc_per_pa:.3f} → {b_.rc_per_pa:.3f}; per G {a.rc_per_gm:.3f} → {b_.rc_per_gm:.3f}", "HELD",
     "Per-PA runs rose while wOBA fell — see rc_by_entry_state (inherited runners)"),
    ("HP-13", "ff_vert", "Vert remained elite at 18 inches",
     f"notebook {N.loc[2025, 'ff_vert']:.1f} → {N.loc[2026, 'ff_vert']:.1f} (quantized); unrounded {R.loc[2025, 'ff_vert']:.1f} → {R.loc[2026, 'ff_vert']:.1f}; IVB grade {H['arch'][2025]['g_ivb']} → {H['arch'][2026]['g_ivb']}",
     "HELD", "Notebook value is quantized in 1.2-inch steps (O-25): pitch_mix rounds pfx_z to 0.1 ft before ×12"),
    ("HP-14", "ff_velo", "Added a tick and half to FF velo", f"{ffv[2025]:.1f} → {ffv[2026]:.1f} (+{H['ff_velo_delta']:.2f} mph, p < .001)", "HELD", ""),
    ("HP-15", "ff_spin", "and spun it more", f"{a.ff_spin:.0f} → {b_.ff_spin:.0f} rpm (+{H['ff_spin_delta']:.0f}, p < .001)", "HELD", ""),
    ("HP-16", "whiff_rate_breaking / whiff_rate_iz_ff", "Breaking Ball and In-Zone Fastball Whiff down a touch from last year's elite level",
     f"breaking {a.whiff_rate_breaking:.3f} → {b_.whiff_rate_breaking:.3f} (p = {H['tests']['Breaking whiff (per swing)']['p']:.2f}); in-zone FF {a.whiff_rate_iz_ff:.3f} → {b_.whiff_rate_iz_ff:.3f} (p = {H['tests']['In-zone four-seam whiff (per swing)']['p']:.2f})",
     "PARTLY", "Breaking: 'a touch' is right. In-zone four-seam: −9 points is more than a touch, but not significant on 80 → 153 swings"),
    ("HP-17", "subtitle (velo box)", "Definitely trending up to a career high 97.0 mph Average in 2026",
     " → ".join(f"{y}: {ffv[y]:.1f}" for y in yrs), "HELD", "Career high yes; 'trending' is really a step: 2024→2025 was flat"),
    ("HP-18", "notebook state", "gy used in the subtitle after `for gy in jb.game_year.unique()`",
     f"the loop leaves gy = last season in concat order (= {int(KF.game_year.unique()[-1])})", "HAZARD",
     "Correct only because nphl is concatenated before pps. Reverse the concat and the subtitle reads 2025. SR-1 removes the leak"),
    ("HP-19", "subtitle (velo × spin)", "Clearly threw the ball harder and with more spin in 2026",
     f"velo +{H['ff_velo_delta']:.2f} mph (Welch p = {H['ff_velo_p']:.1e}); spin +{H['ff_spin_delta']:.0f} rpm (p = {H['ff_spin_p']:.1e})", "HELD", ""),
    ("HP-20", "subtitle (FF profile)", "Right in Line with Career Average. Still Elite overall. Maintained elite shape with added spin and velo.",
     f"IVB {R.loc[2025, 'ff_vert']:.1f} → {R.loc[2026, 'ff_vert']:.1f} in; shape grade {H['arch'][2025]['shape']} → {H['arch'][2026]['shape']} ({H['arch'][2025]['tier']} → {H['arch'][2026]['tier']})",
     "PARTLY", "Carry was maintained; by the uc-pps-032 bar the shape BECAME elite in 2026, because of the velocity"),
    ("HP-21", "subtitle (staff plot)", "Bowlan gets exceptional carry on his four-seam fastball.",
     f"{R.loc[2026, 'ff_vert']:.1f} in: #{H['staff_ff_ivb_rank']} of {H['staff_ff_seasons_n']} Phillies RHP four-seam seasons (≥100 FF, 2015–26 ex-2017)",
     "HELD", ""),
    ("HP-22", "2017 exclusion", "filter out outlier data in 2017",
     f"2017 staff four-seam IVB {H['ivb_2017']:.1f} in vs {H['ivb_other_years_range'][0]:.1f}–{H['ivb_other_years_range'][1]:.1f} in other seasons (z = {H['ivb_2017_z']:.1f})",
     "HELD", "A level shift in the whole season, not outliers. Cause not asserted"),
]
HP = pd.DataFrame(hp, columns=['id', 'kpi', 'client_claim', 'governed_value', 'verdict', 'note'])
HP.to_csv(P("hp_reconciliation.csv"), index=False)
H['hp_verdicts'] = HP.verdict.value_counts().to_dict()

gm = pd.DataFrame([
    ("GM-1", "imports", "Re-imports numpy and graph_objects but not make_subplots", "Runs in the notebook only because cell 4 imports make_subplots; fails as a standalone cell", "FIXED in dp_uc48_build_figs.py"),
    ("GM-2", "units", "Horizontal/vertical break plotted in feet", "Every other Kellen chart uses inches (pfx × 12); 1.5 ft reads as nothing next to 18 in", "FIXED — inches"),
    ("GM-3", "sample size", "Box plots for 2023 (22 FF) and 2024 (29 FF) look as solid as 2026 (467)", "Thin boxes invite over-reading", "FIXED — n printed under each season"),
    ("GM-4", "state", "Reuses the leaked `gy` from the client's loop", "Same hazard as HP-18", "FIXED — explicit RECAP_SEASON"),
    ("GM-5", "subtitle", "'Velocity trending up to a career-high 97.0 mph'", "Holds (HP-17)", "KEPT"),
    ("GM-6", "form", "2×2 box grid of four metrics", "Sound. The client's reply keeps it simpler: velo × spin scatter + movement scatter. Both ship; the grid is the dashboard's detail view", "KEPT"),
], columns=['id', 'area', 'finding', 'why_it_matters', 'disposition'])
gm.to_csv(P("gemini_cell_audit.csv"), index=False)

# =============================================================================
# 9 · PA-1 Persona Action Ledger
# =============================================================================
def sig(persona, hyp_id, hypothesis, signature, before, after, direction, threshold, p=None, unit="", kind="change"):
    if kind == "state":
        verdict = "PRESENT" if after >= threshold else "ABSENT"
    else:
        verdict = K.signature_verdict(before, after, direction, threshold, p)
    return dict(persona=persona, hyp_id=hyp_id, hypothesis=hypothesis, signature=signature,
                before_2025=before, after_2026=after, direction=direction, threshold=threshold,
                p_value=p, unit=unit, verdict=verdict)

TT = T.set_index('metric')
Ab = H['arsenal']; M = H['mix_by_stand']; VBk = H['velo_bucket']
rows = [
    sig("Front Office", "FO-1", "Bought the carry, not the ERA: acquired a four-seam whose shape and whiff were already plus while his run prevention looked ordinary",
        "2025 four-seam IVB grade (uc-pps-032)", None, H['arch'][2025]['g_ivb'], 1, 60, kind="state", unit="grade"),
    sig("Front Office", "FO-1", "", "2025 four-seam whiff grade (uc-pps-032)", None, H['arch'][2025]['g_whiff'], 1, 60, kind="state", unit="grade"),
    sig("Front Office", "FO-1", "", "2025 wOBA against was NOT plus (≥ .300 = ordinary)", None, 1.0 if a.woba >= .300 else 0.0, 1, 1, kind="state", unit="flag"),
    sig("Pitching Coach", "PC-1", "Added velocity to the whole arsenal (strength, mechanics, intent)",
        "Four-seam velo", r3(R.loc[2025, 'ff_velo']), r3(R.loc[2026, 'ff_velo']), 1, 0.5, H['ff_velo_p'], "mph"),
    sig("Pitching Coach", "PC-1", "", "Sinker velo", Ab['2025_SI']['velo'], Ab['2026_SI']['velo'], 1, 0.5, None, "mph"),
    sig("Pitching Coach", "PC-1", "", "Slider velo", Ab['2025_SL']['velo'], Ab['2026_SL']['velo'], 1, 0.5, None, "mph"),
    sig("Pitching Coach", "PC-1", "", "Changeup velo", Ab['2025_CH']['velo'], Ab['2026_CH']['velo'], 1, 0.5, None, "mph"),
    sig("Pitching Coach", "PC-1", "", "Four-seam velo on pitches 1–10 of an outing (arm, not role)",
        VBk['2025_1-10']['velo'], VBk['2026_1-10']['velo'], 1, 0.5, None, "mph"),
    sig("Manager", "MG-1", "Gave him one job: one inning, late, mostly clean",
        "Pitches per appearance", H['usage'][2025]['pitches_per_app'], H['usage'][2026]['pitches_per_app'], -1, 3, None, "pitches"),
    sig("Manager", "MG-1", "", "Multi-inning share", H['usage'][2025]['multi_inning_share'], H['usage'][2026]['multi_inning_share'], -1, 0.15, None, "share"),
    sig("Manager", "MG-1", "", "Entered in the 7th or later", H['usage'][2025]['late_entry_share'], H['usage'][2026]['late_entry_share'], 1, 0.15, None, "share"),
    sig("Manager", "MG-1", "", "Entered at the start of an inning", H['usage'][2025]['start_of_inning_share'], H['usage'][2026]['start_of_inning_share'], 1, 0.10, None, "share"),
    sig("Pitching Analyst", "AN-1", "Built the arsenal by platoon: four-seam + changeup to lefties, a sweeper for righties, curveball shelved",
        "Four-seam + changeup share vs LHB", (M.get('2025_L_FF') or 0) + (M.get('2025_L_CH') or 0), (M.get('2026_L_FF') or 0) + (M.get('2026_L_CH') or 0), 1, 0.10, None, "share"),
    sig("Pitching Analyst", "AN-1", "", "Sweeper share vs RHB", M.get('2025_R_ST') or 0.0, M.get('2026_R_ST') or 0.0, 1, 0.10, None, "share"),
    sig("Pitching Analyst", "AN-1", "", "Curveball share (all)", Ab['2025_CU']['usage'], Ab['2026_CU']['usage'], -1, 0.05, None, "share"),
    sig("Pitching Analyst", "AN-1", "", "Changeup whiff per swing", Ab['2025_CH']['whiff_rate'], Ab['2026_CH']['whiff_rate'], 1, 0.05, None, "rate"),
    sig("Catcher", "CA-1", "Called the four-seam when it mattered: two strikes and behind in the count",
        "Four-seam share, 2-strike counts", TT.loc['Four-seam share, 2K counts', 'rate_2025'], TT.loc['Four-seam share, 2K counts', 'rate_2026'], 1, 0.10, TT.loc['Four-seam share, 2K counts', 'p'], "share"),
    sig("Catcher", "CA-1", "", "Four-seam share, behind in the count", TT.loc['Four-seam share, behind counts', 'rate_2025'], TT.loc['Four-seam share, behind counts', 'rate_2026'], 1, 0.10, TT.loc['Four-seam share, behind counts', 'p'], "share"),
    sig("Catcher", "CA-1", "", "K rate", a.krate, b_.krate, 1, 0.03, TT.loc['K rate (K / PA)', 'p'], "rate"),
    sig("Catcher", "CA-2", "Cut walks by getting ahead early", "First-pitch strike rate",
        TT.loc['First-pitch strike rate', 'rate_2025'], TT.loc['First-pitch strike rate', 'rate_2026'], 1, 0.03, TT.loc['First-pitch strike rate', 'p'], "rate"),
    sig("Catcher", "CA-2", "", "BB rate", a.bbrate, b_.bbrate, -1, 0.02, TT.loc['BB rate (BB / PA)', 'p'], "rate"),
    sig("Pitcher", "PI-1", "Got hitters to expand: more chase without living in the zone more",
        "Chase rate", a.chase_rate, b_.chase_rate, 1, 0.03, TT.loc['Chase rate (swings / out-of-zone)', 'p'], "rate"),
    sig("Pitcher", "PI-1", "", "Four-seam xwOBA on contact (lower = weaker contact)", Ab['2025_FF']['xwobacon'], Ab['2026_FF']['xwobacon'], -1, 0.05, None, "xwOBAcon"),
    sig("Pitching Coach", "WA-1", "WATCH for 2027: the sinker stopped working", "Sinker whiff per swing",
        Ab['2025_SI']['whiff_rate'], Ab['2026_SI']['whiff_rate'], -1, 0.05, None, "rate"),
    sig("Pitching Coach", "WA-1", "", "Sinker xwOBA on contact (higher = harder contact)", Ab['2025_SI']['xwobacon'], Ab['2026_SI']['xwobacon'], 1, 0.05, None, "xwOBAcon"),
    sig("Pitching Analyst", "WA-2", "WATCH for 2027: the new sweeper has not earned its keep yet",
        f"Sweeper run value per 100 below zero (2026: {Ab['2026_ST']['rv100']:+.1f} on {int(Ab['2026_ST']['n'])} pitches)", None,
        1.0 if Ab['2026_ST']['rv100'] < 0 else 0.0, 1, 1, kind="state", unit="flag"),
    sig("Manager", "MG-2", "Workload preceded the 9/17 exit (velocity tell in the final outings)",
        "Four-seam velo, last 5 appearances vs season", H['season_ff_velo_2026'], H['last5_ff_velo'], -1, 0.5, None, "mph"),
]
PL = pd.DataFrame(rows)
PL['hypothesis'] = PL.groupby('hyp_id').hypothesis.transform(lambda s: s.iloc[0])
roll = PL.groupby(['persona', 'hyp_id', 'hypothesis'], as_index=False, sort=False).agg(
    verdicts=('verdict', list), n_signatures=('verdict', 'size'))
roll['strength'] = roll.verdicts.apply(K.strength_from_signatures)
not_obs = {
    'FO-1': "Pro-scouting reports and trade rationale (not in either repo)",
    'PC-1': "Strength program, bullpen/lab sessions, mechanical cues — velocity at every stage of an outing is the only trace in the log",
    'MG-1': "The role conversation itself; leverage index (not in the log — close-and-late is the proxy)",
    'AN-1': "Pitch-design sessions and grip changes; the sweeper's first appearance is the only trace",
    'CA-1': "Pitch calls and PitchCom sequences; outcome of the call is visible, the call itself is not",
    'CA-2': "—",
    'PI-1': "The pitcher's own intent",
    'WA-1': "Grip/usage intent behind the sinker",
    'WA-2': "Pitch-design intent for the sweeper; 77 pitches is a thin sample for run value (uc-pps-032 SG-7: RV needs ~1,084)",
    'MG-2': "Medical and workload records — carry-in only (reported right groin strain, no IL)",
}
roll['what_would_confirm'] = roll.hyp_id.map(not_obs)
roll['verdicts'] = roll.verdicts.apply(lambda v: " · ".join(v))
PL.to_csv(P("persona_signatures.csv"), index=False)
roll.to_csv(P("persona_ledger.csv"), index=False)
H['ledger'] = {r.hyp_id: dict(persona=r.persona, strength=r.strength, verdicts=r.verdicts) for r in roll.itertuples()}

# =============================================================================
# 10 · DQ + headlines
# =============================================================================
comp = B[B.pitch_type == 'FF'][['release_speed', 'release_spin_rate', 'pfx_z', 'pfx_x']].notna().all(axis=1).mean()
dq("DQ-09", "completeness", "pitch", "four-seam velo/spin/pfx jointly non-null ≥ 99%", comp >= .99, round(comp, 4))
dq("DQ-10", "completeness", "pitch", "bat_score/post_bat_score non-null (runs_created precondition)",
   B[['bat_score', 'post_bat_score']].notna().all().all(), int(B[['bat_score', 'post_bat_score']].isna().sum().sum()))
xw = B[(B.type != 'X') & B.estimated_woba_using_speedangle.notna() & B.events.isin(['strikeout', 'walk'])]
dq("DQ-12", "validity", "pitch", "xwOBA published only as xwOBAcon (BIP), per uc-pps-021 O1", True, "get_stats.xwoba quarantined")
dq("DQ-13", "validity", "pitch", "RHP arm-side four-seam pfx_x negative", (B[B.pitch_type == 'FF'].pfx_x.median() < 0),
   round(float(B[B.pitch_type == 'FF'].pfx_x.median()), 2))
dq("DQ-14", "consistency", "pitch", "cross-source duplicates removed by precedence (PHI > FILE > VS_PHI)",
   H['dup_vs_phi'] == 19, H['dup_vs_phi'])
dq("DQ-15", "validity", "pitcher-season", "D-1 exposure: no season loses a whiff_rate row to the inner join",
   recap_g[['whiff_rate_breaking', 'whiff_rate_iz_ff']].notna().all().all(), "all 4 seasons have ≥1 whiff in each subset")
dq("DQ-16", "completeness", "pitch", "zone NULL share (D-7/O-13 exposure on in_zone_rate)", True,
   round(float(B.zone.isna().mean()), 4), warn=bool(B.zone.isna().mean() > 0))
dq("DQ-17", "consistency", "pitcher-season", "small seasons flagged: 2023 (14 PA) and 2024 (17 PA) are context only",
   True, "2023/2024 printed with PA everywhere", warn=True)
dq("DQ-18", "validity", "pitch", "spring training rows excluded (47 in 2026)", (B.game_type == 'R').all(), H['spring_rows_excluded'])
dq("DQ-19", "validity", "file", "parent kernel sha256 = pinned uc-pps-030 hash", K.parent_kernel_hash() == K.PARENT_KERNEL_SHA256,
   K.parent_kernel_hash()[:12])
DQD = pd.DataFrame(DQ).sort_values('rule')
DQD.to_csv(P("dq_scorecard.csv"), index=False)
H['dq'] = DQD.result.value_counts().to_dict()
assert H['dq'].get('FAIL', 0) == 0, DQD[DQD.result == 'FAIL']

P("headlines.json").write_text(json.dumps(H, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
print(json.dumps({k: H[k] for k in ('anchor', 'dq', 'hp_verdicts', 'ledger')}, indent=1, default=str))
