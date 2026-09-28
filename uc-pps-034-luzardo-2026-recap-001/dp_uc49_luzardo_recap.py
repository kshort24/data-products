"""
dp_uc49_luzardo_recap.py — build for UC #49 / uc-pps-034
"The Chase — Jesús Luzardo 2026 Recap"

Reads the data plane (parquet), writes receipts to out/dp_uc49_*. Every number the report, the dashboard
and the figures publish is written here first; nothing downstream recomputes a KPI.

Run (laptop VM, space-constrained):  PYTHONPATH=/tmp/pyl MLB_DATA_ROOT=<MLB repo> python3 dp_uc49_luzardo_recap.py
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd

import dp_uc49_kernel as K

T0 = time.time()
HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC49_OUT", HERE / "out"))
OUT.mkdir(parents=True, exist_ok=True)
P = lambda n: OUT / f"dp_uc49_{n}"          # noqa: E731
H: dict = {}                                 # headlines — every narrative number lives here
DQ: list = []


def dq(rule, dim, grain, text, ok, observed, warn=False):
    DQ.append(dict(rule=rule, dimension=dim, grain=grain, rule_text=text,
                   result=("WARN" if warn else ("PASS" if ok else "FAIL")), observed=str(observed)))


def r3(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 3)


def rate(x, n):
    return float(x) / float(n) if n else np.nan


# =============================================================================
# 0 · Lineage, anchor, frames
# =============================================================================
K.assert_lineage()
PH = K.load_phils_cols(years=range(2015, 2027), role=None, regular_only=False)
anchor = str(PH[(PH.game_year == 2026) & (PH.game_type == 'R')].game_date.max())[:10]
assert anchor == K.ANCHOR_GAME_DATE, f"anchor moved: {anchor} (a refresh is v1.1.0, not a correction)"
PPS = PH[(PH.phillies_role == 'pitching') & (PH.game_type == 'R')]          # governed house pitching frame

scan = K.opponent_id_scan(K.SUBJECT_ID)
scan.to_csv(P("opponent_id_scan.csv"), index=False)
L, src = K.career_frame(scan=scan, ph=PH)                                         # regular season, all sources
src.to_csv(P("source_receipt.csv"), index=False)
LP, src_post = K.career_frame(scan=scan, game_types=K.POSTSEASON_TYPES, ph=PH)     # postseason ledger only
src_post.to_csv(P("source_receipt_postseason.csv"), index=False)
KF, nphl_lost = K.kellen_frame(ph=PH)

spring = PH[(PH.pitcher == K.SUBJECT_ID) & (PH.game_type == 'S')]
L26 = L[L.game_year == 2026].copy()
L25 = L[L.game_year == 2025].copy()
H.update(anchor=anchor, spring_rows_excluded=int(len(spring)), career_pitches=int(len(L)),
         seasons=sorted(int(y) for y in L.game_year.unique()),
         dup_removed=int(src.dropped_as_duplicate.sum()), opp_files_with_subject=int(len(scan)),
         opp_files_name_matched=int(scan.player_name_is_subject.sum()), nphl_lost_to_dedup=int(nphl_lost),
         last_appearance=str(L26.game_date.max())[:10], games_2026=int(L26.game_pk.nunique()),
         pitches_2026=int(len(L26)))
nphl_added = int(src[(src.src == 'NPHL_ID')].kept.sum())
H['nphl_id_rows_kept'] = nphl_added

fresh = pd.DataFrame([
    dict(source="data/phillies/phils_2015..2026.parquet", max_game_date=anchor, rows=len(PH),
         note="regular-season anchor (Game 161); build refuses any other"),
    dict(source=f"data/opponents/{K.SUBJECT_FILE}", max_game_date=str(L[L.src == 'FILE'].game_date.max())[:10],
         rows=int(src[src.src == 'FILE'].rows.sum()), note="pitcher-keyed pull, OAK/MIA 2019-2024 (regular season)"),
    dict(source="data/opponents/* (id scan)", max_game_date="", rows=int(scan.rows.sum()),
         note=f"{len(scan)} files hold pitcher==666200; {nphl_added} regular-season pitches survive dedup beyond PHI+FILE"),
    dict(source="carry-in: MLB.com 2024-12", max_game_date="2024-12", rows=0,
         note="acquired from MIA for Starlyn Caba and Emaarion Boyd (context only)"),
    dict(source="carry-in: MLB.com 2026-03-10", max_game_date="2026-03-10", rows=0,
         note="5-yr / $135M extension covering 2027-2031, 2032 club option (context only)"),
    dict(source="carry-in: MLB.com 2026-07-07", max_game_date="2026-07-14", rows=0,
         note="first career All-Star selection (named 7/7 as a replacement); ASG at Citizens Bank Park 7/14"),
    dict(source="carry-in: MLB.com 2026-09-07", max_game_date="2026-09-07", rows=0,
         note="Labor Day box: CG SHO, 2 H, 1 BB, 12 K, 1:51, Schwarber solo HR 8th off Didier Fuentes; NL Pitcher of the Month (Aug)"),
    dict(source="carry-in: Phillies Nation 2026-09-24", max_game_date="2026-09-24", rows=0,
         note="scratched 9/12 (shoulder stiffness); 15-day IL 9/15 (shoulder inflammation); 2.87 ERA in 29 starts, 1.84 post-ASB"),
    dict(source="carry-in: SI 2026-09-27", max_game_date="2026-09-27", rows=0,
         note="activated for Game 162, available out of the bullpen (Mattingly)"),
])
fresh.to_csv(P("freshness_manifest.csv"), index=False)

dq("DQ-01", "uniqueness", "pitch", "no duplicate PITCH_KEY in the governed career frame (CF-2)",
   L.duplicated(K.PITCH_KEY).sum() == 0, int(L.duplicated(K.PITCH_KEY).sum()))
dq("DQ-02", "consistency", "pitch", "entity lock: every row pitcher == 666200", (L.pitcher == K.SUBJECT_ID).all(),
   L.pitcher.unique().tolist())
dq("DQ-03", "validity", "pitch", "regular season only in the rate frame (game_type == 'R')", (L.game_type == 'R').all(),
   L.game_type.unique().tolist())
dq("DQ-04", "timeliness", "file", "Phillies log current through the pinned anchor", anchor == K.ANCHOR_GAME_DATE, anchor)
dq("DQ-05", "validity", "pitch", "p_throws == 'L' on every row", (L.p_throws == 'L').all(), L.p_throws.unique().tolist())
dq("DQ-06", "timeliness", "pitch", "no 2026 appearance after the Labor Day game (carry-in: IL 9/15)",
   str(L26.game_date.max())[:10] == K.LAST_APPEARANCE, str(L26.game_date.max())[:10])
dq("DQ-07", "consistency", "season", "2026 appearances == 29 (carry-in: '2.87 ERA in 29 starts')",
   L26.game_pk.nunique() == 29, int(L26.game_pk.nunique()))
dq("DQ-08", "completeness", "file", "opponent id scan finds every file the name filter finds",
   set(scan[scan.player_name_is_subject].file) >= {K.SUBJECT_FILE}, scan.file.tolist())

# =============================================================================
# 1 · SR-1 recap (second use) — the client's cell, both ways
# =============================================================================
lvl = ['player_name', 'game_year', 'p_throws']
CLIENT_KPIS = ['pitches', 'plate_apps', 'ba', 'obp', 'slg', 'ops', 'woba', 'krate', 'bbrate', 'hr_rate',
               'whiff_rate', 'chase_rate', 'in_zone_rate', 'First Pitch Strike Rate']


def recap(df, governed):
    z = K.season_recap(df, governed=governed)
    f = K.fpsr(lvl, df)[lvl + ['First Pitch Strike Rate']]
    z = z.merge(f, on=lvl, how='left')
    if governed:   # in_zone over TRACKED pitches (D-7/O-13 fix), carried beside the notebook value
        t = df.assign(_tr=df.zone.notna(), _iz=df.zone.between(1, 9)).groupby(lvl, as_index=False).agg(
            tracked=('_tr', 'sum'), in_zone_n=('_iz', 'sum'))
        z = z.merge(t, on=lvl, how='left')
        z['in_zone_rate_notebook'] = z.in_zone_rate
        z['in_zone_rate'] = z.in_zone_n / z.tracked
    return z


recap_g = recap(L, True)
recap_n = recap(KF, False)
extra = ['strikeouts', 'walks', 'hrs', 'hits', 'swings', 'whiffs', 'chases', 'ooz', 'runs_created', 'games',
         'ff_velo', 'ff_spin', 'ff_vert']
recap_g[lvl + CLIENT_KPIS + extra + ['ff_n', 'ff_hb', 'tracked', 'in_zone_rate_notebook']].to_csv(P("recap_governed.csv"), index=False)
recap_n[lvl + CLIENT_KPIS + extra].to_csv(P("recap_notebook.csv"), index=False)

# HP reconciliation by season: where the client's frame and the governed frame part ways, and why
kf_types = KF.groupby('game_year').game_type.apply(lambda s: int((s != 'R').sum())).rename('client_postseason_pitches')
m = recap_g[lvl + ['pitches', 'plate_apps', 'woba', 'krate', 'bbrate']].merge(
    recap_n[lvl + ['pitches', 'plate_apps', 'woba', 'krate', 'bbrate']], on=lvl, how='outer', suffixes=('_gov', '_client'))
m = m.merge(kf_types, left_on='game_year', right_index=True, how='left')
m['pitch_gap'] = m.pitches_client - m.pitches_gov
hp_season = m.sort_values('game_year')
hp_season.to_csv(P("hp_season_frames.csv"), index=False)
H['client_frame_pitch_gap_total'] = int(hp_season.pitch_gap.sum())
H['client_postseason_pitches_total'] = int(hp_season.client_postseason_pitches.sum())

# Frame-agreement rule: the ONLY differences allowed are (a) postseason rows the client keeps and
# (b) rows the nphl keep-first dedup took away (O-26). Rebuild the client frame's regular season, add
# back the O-26 rows by id, and require exact agreement with CF-2.
kf_reg = KF[KF.game_type == 'R']
agree = (len(kf_reg) + nphl_lost == len(L))
dq("DQ-09", "consistency", "pitch", "client frame (regular season) + O-26 losses == CF-2 governed frame",
   agree, f"{len(kf_reg)} + {nphl_lost} vs {len(L)}")

R = recap_g.set_index('game_year')
for y in R.index:
    row = R.loc[y]
    H[f'y{y}'] = {k: (int(row[k]) if k in ('pitches', 'plate_apps', 'games', 'strikeouts', 'walks', 'hrs', 'swings',
                                           'whiffs', 'chases', 'ooz', 'runs_created', 'tracked') else r3(row[k]))
                  for k in CLIENT_KPIS + extra + ['tracked'] if k in row.index}
a, b = R.loc[2025], R.loc[2026]

# =============================================================================
# 2 · Rate tests 2025 -> 2026 (house standing test: pooled two-proportion z)
# =============================================================================
tests = []


def ttest(name, x1, n1, x2, n2, better):
    z, p = K.two_prop_z(x2, n2, x1, n1)
    tests.append(dict(metric=name, x_2025=int(x1), n_2025=int(n1), rate_2025=rate(x1, n1), x_2026=int(x2),
                      n_2026=int(n2), rate_2026=rate(x2, n2), delta=rate(x2, n2) - rate(x1, n1), z=z, p=p, better_is=better))


ttest("K rate (K / PA)", a.strikeouts, a.plate_apps, b.strikeouts, b.plate_apps, "up")
ttest("BB rate (BB / PA)", a.walks, a.plate_apps, b.walks, b.plate_apps, "down")
ttest("HR rate (HR / PA)", a.hrs, a.plate_apps, b.hrs, b.plate_apps, "down")
ttest("Whiff rate (per swing)", a.whiffs, a.swings, b.whiffs, b.swings, "up")
ttest("Chase rate (swings / out-of-zone)", a.chases, a.ooz, b.chases, b.ooz, "up")
ttest("In-zone rate (tracked)", round(a.in_zone_rate * a.tracked), a.tracked, round(b.in_zone_rate * b.tracked), b.tracked, "context")
T = pd.DataFrame(tests)
T.to_csv(P("rate_tests.csv"), index=False)
H['tests'] = {t['metric']: dict(r25=r3(t['rate_2025']), r26=r3(t['rate_2026']), p=r3(t['p'])) for t in tests}

# =============================================================================
# 3 · CX-1 context board — "better than most pitchers in my dataset"
# =============================================================================
CX = K.context_frame(PPS)
CX['is_subject'] = CX.pitcher == K.SUBJECT_ID
mu_ch, mu_wh = CX.chase_rate.mean(), CX.whiff_rate.mean()
CX['plus_chase'] = CX.chase_rate >= mu_ch
CX['plus_whiff'] = CX.whiff_rate >= mu_wh
CX['plus_plus'] = CX.plus_chase & CX.plus_whiff
CX['rank_whiff'] = CX.whiff_rate.rank(ascending=False, method='min').astype(int)
CX['rank_chase'] = CX.chase_rate.rank(ascending=False, method='min').astype(int)
CX['dominated_by'] = [int(((CX.chase_rate > c) & (CX.whiff_rate > w)).sum()) for c, w in zip(CX.chase_rate, CX.whiff_rate)]
CX['rank_whiff_lhp'] = CX.groupby('p_throws').whiff_rate.rank(ascending=False, method='min').astype(int)
CX['rank_chase_lhp'] = CX.groupby('p_throws').chase_rate.rank(ascending=False, method='min').astype(int)
CX.to_csv(P("context_population.csv"), index=False)
ctx = {}
for y in (2025, 2026):
    r_ = CX[(CX.pitcher == K.SUBJECT_ID) & (CX.game_year == y)].iloc[0]
    ctx[str(y)] = dict(whiff=r3(r_.whiff_rate), chase=r3(r_.chase_rate), in_zone=r3(r_.in_zone_rate),
                       bbrate=r3(r_.bbrate), rank_whiff=int(r_.rank_whiff), rank_chase=int(r_.rank_chase),
                       dominated_by=int(r_.dominated_by), plus_plus=bool(r_.plus_plus),
                       rank_whiff_lhp=int(r_.rank_whiff_lhp), rank_chase_lhp=int(r_.rank_chase_lhp),
                       pitches=int(r_.pitches))
H['ctx'] = ctx
H['ctx_n'] = int(len(CX)); H['ctx_n_lhp'] = int((CX.p_throws == 'L').sum())
H['ctx_mean_chase'] = r3(mu_ch); H['ctx_mean_whiff'] = r3(mu_wh)
H['ctx_plus_plus_n'] = int(CX.plus_plus.sum())
H['ctx_undominated_n'] = int((CX.dominated_by == 0).sum())
undom = CX[CX.dominated_by == 0].sort_values('chase_rate')[['name', 'game_year', 'p_throws', 'pitches', 'chase_rate', 'whiff_rate']]
undom.to_csv(P("context_frontier.csv"), index=False)
# CX-1b: starter workloads only (>= 2,000 pitches in a season — declared in 03 §2)
SW = CX[CX.pitches >= 2000].copy()
SW['rank_whiff_sw'] = SW.whiff_rate.rank(ascending=False, method='min').astype(int)
SW['rank_chase_sw'] = SW.chase_rate.rank(ascending=False, method='min').astype(int)
SW['dominated_by_sw'] = [int(((SW.chase_rate > c) & (SW.whiff_rate > w)).sum()) for c, w in zip(SW.chase_rate, SW.whiff_rate)]
SW.to_csv(P("context_starter_workloads.csv"), index=False)
s26 = SW[(SW.pitcher == K.SUBJECT_ID) & (SW.game_year == 2026)].iloc[0]
H['ctx_sw'] = dict(n=int(len(SW)), rank_whiff=int(s26.rank_whiff_sw), rank_chase=int(s26.rank_chase_sw),
                   dominated_by=int(s26.dominated_by_sw),
                   next_whiff=SW.sort_values('whiff_rate', ascending=False).iloc[1][['name', 'game_year', 'whiff_rate']].astype(str).to_dict())

# The client's own version of the population (name-keyed, postseason kept) — for the HP row only
pps_client = PH[(PH.phillies_role == 'pitching') & ~PH.game_type.isin(['S', 'E'])]
zc = K.nresults(lvl, pps_client).merge(K.whiff_rate(lvl, pps_client), on=lvl, how='left').merge(
    K.chase_rate(lvl, pps_client), on=lvl, how='left', suffixes=('', '_cr'))
zfig = zc[zc.pitches > 149]
zl = zfig[(zfig.player_name == K.SUBJECT_NAME) & (zfig.game_year == 2026)].iloc[0]
H['client_ctx'] = dict(n=int(len(zfig)), mean_chase=r3(zfig.chase_rate.mean()), mean_whiff=r3(zfig.whiff_rate.mean()),
                       luz26_whiff=r3(zl.whiff_rate), luz26_chase=r3(zl.chase_rate),
                       luz26_rank_whiff=int((zfig.whiff_rate > zl.whiff_rate).sum() + 1),
                       luz26_rank_chase=int((zfig.chase_rate > zl.chase_rate).sum() + 1))

# Command: walk rate as a function of in-zone rate (client's OLS trendline, per handedness facet)
cmd = []
for th, g in CX.groupby('p_throws'):
    slope, icpt = np.polyfit(g.in_zone_rate, g.bbrate, 1)
    resid = g.bbrate - (icpt + slope * g.in_zone_rate)
    for y in (2025, 2026):
        s = g[(g.pitcher == K.SUBJECT_ID) & (g.game_year == y)]
        if len(s):
            e = icpt + slope * s.in_zone_rate.iat[0]
            cmd.append(dict(p_throws=th, game_year=y, in_zone_rate=s.in_zone_rate.iat[0], bbrate=s.bbrate.iat[0],
                            expected_bbrate=e, residual=s.bbrate.iat[0] - e,
                            residual_pctile=int(np.floor(100 * (resid > s.bbrate.iat[0] - e).mean())),
                            slope=slope, intercept=icpt, n=len(g)))
    cmd.append(dict(p_throws=th, game_year=None, slope=slope, intercept=icpt, n=len(g)))
CMD = pd.DataFrame(cmd)
CMD.to_csv(P("command_ols.csv"), index=False)
c26 = CMD[(CMD.game_year == 2026)].iloc[0]
H['cmd26'] = dict(in_zone=r3(c26.in_zone_rate), bb=r3(c26.bbrate), expected=r3(c26.expected_bbrate),
                  residual=r3(c26.residual), slope=r3(c26.slope), n=int(c26.n), residual_pctile=int(c26.residual_pctile))

# =============================================================================
# 4 · KP-1 house percentiles (Phillies pitcher-seasons >= 100 PA) + 2026 staff rank
# =============================================================================
pop = K.house_pitcher_seasons_from(PPS)
pop.to_csv(P("house_population.csv"), index=False)
kp = []
for col, hib, lab in [('krate', True, 'K rate'), ('bbrate', False, 'BB rate'), ('woba', False, 'wOBA'),
                      ('whiff_rate', True, 'Whiff rate'), ('chase_rate', True, 'Chase rate')]:
    v = pop[(pop.pitcher == K.SUBJECT_ID) & (pop.game_year == 2026)][col].iat[0]
    hp_ = K.house_percentile(pop, col, v, hib)
    staff = pop[pop.game_year == 2026]
    srank = int(((staff[col] > v) if hib else (staff[col] < v)).sum() + 1)
    kp.append(dict(kpi=lab, column=col, value=v, **hp_, staff_rank_2026=srank, staff_n_2026=len(staff)))
KP = pd.DataFrame(kp)
KP.to_csv(P("house_percentiles.csv"), index=False)
H['kp'] = {r_.column: dict(value=r3(r_.value), pct=int(r_.percentile), rank=int(r_.rank), n=int(r_.n),
                           staff_rank=int(r_.staff_rank_2026), staff_n=int(r_.staff_n_2026)) for r_ in KP.itertuples()}

# =============================================================================
# 5 · Arsenal (AR-2) by season and by batter side; pitch map (PM-1) 2026
# =============================================================================
ars = K.arsenal_table(L, by=('game_year',))
ars.to_csv(P("arsenal_by_season.csv"), index=False)
ars_st = K.arsenal_table(L26, by=('stand',))
ars_st.to_csv(P("arsenal_by_stand_2026.csv"), index=False)
pm = K.pitch_map_centroid(L26)
pm['untracked_dropped'] = pm.attrs.get('dropped_untracked', 0)
pm.to_csv(P("pitch_map_2026.csv"), index=False)
# the client's version: lhb/rhb_pitch_mix, rounded to 0.1 ft (O-25), usage in % of that side's pitches
pmc = []
for st in ('L', 'R'):
    x = K.pitch_mix(KF[(KF.game_year == 2026) & (KF.stand == st)]); x['stand'] = st; pmc.append(x)
pd.concat(pmc).to_csv(P("pitch_map_2026_notebook.csv"), index=False)


def av(df_, y, pt, c):
    s = df_[(df_.game_year == y) & (df_.pitch_type == pt)]
    return r3(s[c].iat[0]) if len(s) else None


H['ars'] = {str(y): {pt: dict(usage=av(ars, y, pt, 'usage'), velo=av(ars, y, pt, 'velo'), whiff=av(ars, y, pt, 'whiff_rate'),
                              chase=av(ars, y, pt, 'chase_rate'), rv100=av(ars, y, pt, 'rv100'), n=av(ars, y, pt, 'n'))
                     for pt in ars[ars.game_year == y].pitch_type} for y in (2024, 2025, 2026)}
H['ars_stand'] = {st: {r_.pitch_type: dict(usage=r3(r_.usage), whiff=r3(r_.whiff_rate), chase=r3(r_.chase_rate), n=int(r_.n))
                       for r_ in ars_st[ars_st.stand == st].itertuples()} for st in ('L', 'R')}

# =============================================================================
# 6 · 2026 season arc: per start (US-1 + GS-1 + VB-1), month, half, TTO
# =============================================================================
apps = K.appearance_log(L26)
gs26 = K.game_score(L26)
sig26 = K.outing_signatures(L26)
starts = (gs26.merge(apps[['game_pk', 'ff_velo', 'ff_max', 'rest_days']], on='game_pk', how='left')
              .merge(sig26[['game_pk', 'whiff_per_100', 'chase_rate', 'bb_rate', 'first_n_ff_velo', 'first_n_ff']], on='game_pk'))
starts['opp'] = np.where(starts.home_team == 'PHI', starts.away_team, starts.home_team)
starts['venue'] = np.where(starts.home_team == 'PHI', 'home', 'away')
starts['start_no'] = np.arange(1, len(starts) + 1)
starts['half'] = np.where(starts.game_date < K.ALL_STAR_BREAK, 'first', 'second')
starts['kbb'] = (starts.k - starts.bb) / starts.pa
starts['kbb_roll5'] = starts.kbb.rolling(5, min_periods=3).mean()
starts.to_csv(P("starts_2026.csv"), index=False)
dq("DQ-10", "validity", "game", "OU-1: no inning credits more than 3 outs (2026)",
   (L26.assign(_o=K.outs_recorded(L26)).groupby(['game_pk', 'inning'])._o.sum() <= 3).all(), "per game-inning")
dq("DQ-11", "consistency", "game", "every 2026 appearance is a start (entered in the 1st)", starts.started.all(),
   int(starts.started.sum()))

L26['month'] = pd.to_datetime(L26.game_date).dt.month
mo = K.nresults(['month'], L26).merge(K.whiff_rate(['month'], L26), on='month', how='left').merge(
    K.chase_rate(['month'], L26), on='month', how='left', suffixes=('', '_cr'))
mo = mo.merge(K.xwobacon(['month'], L26), on='month', how='left').merge(
    starts.assign(month=pd.to_datetime(starts.game_date).dt.month).groupby('month', as_index=False).agg(
        starts=('game_pk', 'size'), r=('r', 'sum'), outs=('outs', 'sum'), ff_velo=('ff_velo', 'mean')), on='month')
mo['runs_per_27_outs'] = 27 * mo.r / mo.outs
mo.to_csv(P("monthly_2026.csv"), index=False)
H['aug'] = {c: (int(mo.set_index('month').loc[8, c]) if c in ('starts', 'r', 'outs', 'plate_apps', 'strikeouts', 'walks')
                else r3(mo.set_index('month').loc[8, c]))
            for c in ('starts', 'plate_apps', 'strikeouts', 'walks', 'krate', 'bbrate', 'woba', 'whiff_rate', 'r', 'outs', 'runs_per_27_outs')}

L26['half'] = np.where(L26.game_date < K.ALL_STAR_BREAK, 'first', 'second')
hv = K.nresults(['half'], L26).merge(K.xwobacon(['half'], L26), on='half').merge(
    starts.groupby('half', as_index=False).agg(starts=('game_pk', 'size'), r=('r', 'sum'), outs=('outs', 'sum')), on='half')
hv['runs_per_27_outs'] = 27 * hv.r / hv.outs
hv.to_csv(P("halves_2026.csv"), index=False)
H['halves'] = {r_.half: dict(starts=int(r_.starts), pa=int(r_.plate_apps), krate=r3(r_.krate), bbrate=r3(r_.bbrate),
                             woba=r3(r_.woba), xwobacon=r3(r_.xwobacon), r=int(r_.r), outs=int(r_.outs),
                             r27=r3(r_.runs_per_27_outs)) for r_ in hv.itertuples()}

tto = K.nresults(['half', 'n_thruorder_pitcher'], L26)
tto.to_csv(P("tto_2026.csv"), index=False)
tto_all = K.nresults(['n_thruorder_pitcher'], L26)
H['tto'] = {int(r_.n_thruorder_pitcher): dict(pa=int(r_.plate_apps), woba=r3(r_.woba)) for r_ in tto_all.itertuples()}

# Parent reproduction (uc-pps-017 first-half publishes: 19 starts, 29.2 K%, TTO1 .198, TTO2 .368)
fh = L26[L26.half == 'first']
fh_r = K.nresults(['half'], fh).iloc[0]
fh_t = K.nresults(['n_thruorder_pitcher'], fh).set_index('n_thruorder_pitcher')
repro = pd.DataFrame([
    dict(parent='uc-pps-017', figure='first-half starts', published=19, recomputed=int(fh.game_pk.nunique())),
    dict(parent='uc-pps-017', figure='first-half K%', published=0.292, recomputed=round(float(fh_r.krate), 3)),
    dict(parent='uc-pps-017', figure='1st time through wOBA', published=0.198, recomputed=round(float(fh_t.loc[1, 'woba']), 3)),
    dict(parent='uc-pps-017', figure='2nd time through wOBA', published=0.368, recomputed=round(float(fh_t.loc[2, 'woba']), 3)),
])
repro['match'] = (repro.published - repro.recomputed).abs() <= 0.0015
repro.to_csv(P("parent_reproduction.csv"), index=False)
dq("DQ-12", "consistency", "season", "parent reproduction: uc-pps-017 first-half figures recomputed from CF-2",
   repro.match.all(), f"{int(repro.match.sum())}/{len(repro)}")

# =============================================================================
# 7 · Career game scores (GS-1) — "the best shift of his Major League career"
# =============================================================================
gsc = K.game_score(L)
gsc['team'] = np.where(gsc.game_year >= 2025, 'PHI', np.where(gsc.game_year <= 2021, 'OAK/MIA', 'MIA'))
gsc['opp_home'] = gsc.home_team + ' vs ' + gsc.away_team
gsc = gsc.sort_values('game_score', ascending=False).reset_index(drop=True)
gsc['gs_rank'] = gsc.game_score.rank(ascending=False, method='min').astype(int)
gsc.to_csv(P("career_game_scores.csv"), index=False)
ld = gsc[gsc.game_pk == K.LABOR_DAY_GAME_PK].iloc[0]
H['gs'] = dict(n_games=int(len(gsc)), n_starts=int(gsc.started.sum()), labor_day=int(ld.game_score),
               labor_day_rank=int(ld.gs_rank), max_outs_other=int(gsc[gsc.game_pk != K.LABOR_DAY_GAME_PK].outs.max()),
               nine_inning_games=int((gsc.inn_last >= 9).sum()),
               next_best=int(gsc[gsc.game_pk != K.LABOR_DAY_GAME_PK].game_score.max()),
               next_best_date=str(gsc[gsc.game_pk != K.LABOR_DAY_GAME_PK].iloc[0].game_date)[:10],
               next_best_line=gsc[gsc.game_pk != K.LABOR_DAY_GAME_PK].iloc[0][['ip_display', 'h', 'r', 'bb', 'k']].astype(str).to_dict(),
               career_12k_games=int((gsc.k >= 12).sum()), career_max_k=int(gsc.k.max()),
               scoreless_starts_7plus=int(((gsc.r == 0) & (gsc.outs >= 21)).sum()))
dq("DQ-13", "consistency", "game", "Labor Day OU-1 outs == 27 (a nine-inning complete game)", int(ld.outs) == 27, int(ld.outs))

# =============================================================================
# 8 · Labor Day, pitch by pitch (the game story)
# =============================================================================
G = L26[L26.game_pk == K.LABOR_DAY_GAME_PK].sort_values(['at_bat_number', 'pitch_number']).copy()
names = K.batter_names(PH[(PH.game_year == 2026)])
G['batter_name'] = G.batter.map(names).fillna(G.batter.astype(str))
G['pitch_of_game'] = np.arange(1, len(G) + 1)
G['is_whiff'] = G.description.isin(K.WHIFFS)
G['is_swing'] = G.description.isin(K.SWINGS)
G['is_csw'] = G.is_whiff | (G.description == 'called_strike')
G['count'] = G.balls.astype(int).astype(str) + '-' + G.strikes.astype(int).astype(str)
keep_g = ['pitch_of_game', 'inning', 'at_bat_number', 'pitch_number', 'batter', 'batter_name', 'stand', 'n_thruorder_pitcher',
          'count', 'pitch_type', 'pitch_name', 'release_speed', 'release_spin_rate', 'plate_x', 'plate_z', 'zone',
          'description', 'events', 'is_whiff', 'is_swing', 'is_csw', 'launch_speed', 'estimated_woba_using_speedangle',
          'delta_run_exp', 'outs_when_up', 'des']
G[keep_g].to_csv(P("laborday_pitches.csv"), index=False)
pa = G.groupby('at_bat_number', as_index=False).agg(
    inning=('inning', 'first'), batter_name=('batter_name', 'first'), stand=('stand', 'first'),
    tto=('n_thruorder_pitcher', 'first'), pitches=('pitch_type', 'size'), sequence=('pitch_type', lambda s: '-'.join(s)),
    whiffs=('is_whiff', 'sum'), result=('events', lambda s: s.dropna().iat[-1] if s.notna().any() else ''),
    des=('des', lambda s: s.dropna().iat[-1] if s.notna().any() else ''))
pa.to_csv(P("laborday_pa.csv"), index=False)
byinn = G.groupby('inning', as_index=False).agg(pitches=('pitch_type', 'size'), whiffs=('is_whiff', 'sum'),
                                                csw=('is_csw', 'sum'), ff_velo=('release_speed', lambda s: np.nan),
                                                k=('events', lambda s: s.isin(['strikeout']).sum()),
                                                batters=('at_bat_number', 'nunique'))
byinn['ff_velo'] = byinn.inning.map(G[G.pitch_type == 'FF'].groupby('inning').release_speed.mean())
byinn['csw_rate'] = byinn.csw / byinn.pitches
byinn.to_csv(P("laborday_by_inning.csv"), index=False)
mix = G.groupby(['n_thruorder_pitcher', 'stand', 'pitch_type'], as_index=False).agg(n=('pitch_type', 'size'))
mix['share'] = mix.n / mix.groupby(['n_thruorder_pitcher', 'stand']).n.transform('sum')
mix.to_csv(P("laborday_mix_by_tto.csv"), index=False)
mix_tto = G.groupby(['n_thruorder_pitcher', 'pitch_type'], as_index=False).agg(n=('pitch_type', 'size'))
mix_tto['share'] = mix_tto.n / mix_tto.groupby('n_thruorder_pitcher').n.transform('sum')
season_mix = L26[L26.game_pk != K.LABOR_DAY_GAME_PK].pitch_type.value_counts(normalize=True)
H['ld_mix_tto'] = {int(t): {r_.pitch_type: r3(r_.share) for r_ in mix_tto[mix_tto.n_thruorder_pitcher == t].itertuples()}
                   for t in sorted(mix_tto.n_thruorder_pitcher.unique())}
H['season_mix_ex_ld'] = {k: r3(v) for k, v in season_mix.items()}

box = dict(pitches=len(G), h=int(G.events.isin(['single', 'double', 'triple', 'home_run']).sum()),
           bb=int((G.events == 'walk').sum()), k=int(G.events.isin(['strikeout', 'strikeout_double_play']).sum()),
           whiffs=int(G.is_whiff.sum()), swinging_strikes=int(G.description.isin(['swinging_strike', 'swinging_strike_blocked']).sum()),
           csw=int(G.is_csw.sum()), batters=int(G.at_bat_number.nunique()), runs=int(ld.r),
           max_inning=int(G.inning.max()), ff_velo=r3(G[G.pitch_type == 'FF'].release_speed.mean()),
           ff_velo_9th=r3(G[(G.pitch_type == 'FF') & (G.inning == 9)].release_speed.mean()),
           ff_max=r3(G[G.pitch_type == 'FF'].release_speed.max()), first_pitch_strikes=int((G[G.pitch_number == 1].type != 'B').sum()),
           pa=int(G.at_bat_number.nunique()), ooz=int((G.zone > 9).sum()),
           chases=int(((G.zone > 9) & G.is_swing).sum()), swings=int(G.is_swing.sum()),
           max_pitches_in_inning=int(byinn.pitches.max()), min_pitches_in_inning=int(byinn.pitches.min()),
           gs=int(ld.game_score))
box['chase_rate'] = r3(box['chases'] / box['ooz'])
box['whiff_rate'] = r3(box['whiffs'] / box['swings'])
box['csw_rate'] = r3(box['csw'] / box['pitches'])
# The run: the Phillies' half of the 8th, from the batting-role log
bat = PH[(PH.game_pk == K.LABOR_DAY_GAME_PK) & (PH.phillies_role == 'batting')]
hr = bat[bat.events == 'home_run']
box['phi_runs'] = int(bat.post_bat_score.max())
box['atl_runs'] = int(G.post_bat_score.max())
box['hr_inning'] = int(hr.inning.iat[0]) if len(hr) else None
box['hr_des'] = hr.des.iat[0] if len(hr) else None
box['hr_pitcher'] = int(hr.pitcher.iat[0]) if len(hr) else None
box['hr_launch_speed'] = r3(hr.launch_speed.iat[0]) if len(hr) else None
H['ld'] = box
carry = [('pitches', None, 109), ('h', None, 2), ('bb', None, 1), ('k', None, 12),
         ('whiffs', 'house WHIFFS (swinging strikes + foul tips); MLB.com "23 swings and misses"', 23),
         ('phi_runs', None, 1), ('atl_runs', None, 0), ('hr_inning', None, 8)]
rec = pd.DataFrame([dict(item=i, carry_in=c, log=box[i], note=n or '', match=(box[i] == c)) for i, n, c in carry])
rec.to_csv(P("laborday_box_reconcile.csv"), index=False)
dq("DQ-14", "consistency", "game", "Labor Day log reconciles to the published box (MLB.com carry-in)",
   rec.match.all(), rec[['item', 'log', 'carry_in']].to_dict('records'), warn=not rec.match.all())

# =============================================================================
# 9 · Velocity by start and the silence after Labor Day
# =============================================================================
vb = starts[['start_no', 'game_date', 'opp', 'pitches', 'ff_velo', 'first_n_ff_velo', 'first_n_ff', 'ff_max']].copy()
band = vb.ff_velo.quantile([0.25, 0.5, 0.75]).tolist()
vb.to_csv(P("velo_by_start_2026.csv"), index=False)
last3 = vb.tail(3)
H['velo'] = dict(p25=r3(band[0]), med=r3(band[1]), p75=r3(band[2]), season=r3(L26[L26.pitch_type == 'FF'].release_speed.mean()),
                 last3=[r3(v) for v in last3.ff_velo], last3_dates=[str(d)[:10] for d in last3.game_date],
                 ld=r3(vb[vb.game_date.astype(str).str[:10] == K.LAST_APPEARANCE].ff_velo.iat[0]),
                 ld_first15=r3(vb[vb.game_date.astype(str).str[:10] == K.LAST_APPEARANCE].first_n_ff_velo.iat[0]),
                 first15_p25=r3(vb.first_n_ff_velo.quantile(0.25)), first15_med=r3(vb.first_n_ff_velo.median()),
                 max_pitches=int(vb.pitches.max()), ld_pitches=int(vb[vb.game_date.astype(str).str[:10] == K.LAST_APPEARANCE].pitches.iat[0]),
                 pitches_sd=r3(vb.pitches.std()), pitch_min=int(vb.pitches.min()))
H['velo']['ld_rank_pitches'] = int((vb.pitches > H['velo']['ld_pitches']).sum() + 1)
v25 = K.first_n_velo(L25)
H['velo']['first15_2025_med'] = r3(v25.first_n_ff_velo.median())

# =============================================================================
# 10 · Postseason ledger (career) — pitch level, tiny samples, printed
# =============================================================================
pl = K.game_score(LP)
pl['round'] = pl.game_type.map({'F': 'Wild Card', 'D': 'Division Series', 'L': 'LCS', 'W': 'World Series'})
pl['team'] = np.where(pl.game_year >= 2025, 'PHI', np.where(pl.game_year <= 2021, 'OAK', 'MIA'))
pl['role'] = np.where(pl.started, 'start', 'relief')
pl['venue'] = pl.home_team
pl = pl.merge(K.first_n_velo(LP)[['game_pk', 'first_n_ff_velo']], on='game_pk', how='left')
pl.to_csv(P("postseason_ledger.csv"), index=False)
H['post'] = [dict(date=str(r_.game_date)[:10], round=r_.round, team=r_.team, venue=r_.venue, role=r_.role,
                  outs=int(r_.outs), ip=r_.ip_display, pa=int(r_.pa), h=int(r_.h), r=int(r_.r), bb=int(r_.bb), k=int(r_.k),
                  hr=int(r_.hr), pitches=int(r_.pitches)) for r_ in pl.itertuples()]
post_tot = K.nresults(['game_type'], LP.assign(game_type='ALL'))
H['post_tot'] = dict(games=int(len(pl)), pa=int(post_tot.plate_apps.iat[0]), woba=r3(post_tot.woba.iat[0]),
                     krate=r3(post_tot.krate.iat[0]), outs=int(pl.outs.sum()), r=int(pl.r.sum()))

# =============================================================================
# 11 · OC-1 October card — pre-registered before any postseason pitch
# =============================================================================
card = K.october_card(sig26)
card['registered_on'] = '2026-09-27'
card['anchor'] = anchor
card.to_csv(P("october_card.csv"), index=False)
# Would the card have called his own 2026 starts on-script? (calibration of the rule, not a prediction)
graded = pd.DataFrame([dict(game_pk=r_.game_pk, game_date=str(r_.game_date)[:10], **K.grade_outing(r_, card))
                       for _, r_ in sig26.iterrows()])
graded = graded.merge(starts[['game_pk', 'r', 'outs', 'game_score']], on='game_pk')
graded.to_csv(P("october_card_backtest_2026.csv"), index=False)
on = graded[graded.verdict == 'ON-SCRIPT']; off = graded[graded.verdict == 'OFF-SCRIPT']
H['oc'] = dict(bars={r_.signature: r3(r_.bar) for r_ in card.itertuples()},
               backtest_on=int(len(on)), backtest_off=int(len(off)),
               on_r27=r3(27 * on.r.sum() / on.outs.sum()), off_r27=r3(27 * off.r.sum() / off.outs.sum()),
               on_gs=r3(on.game_score.mean()), off_gs=r3(off.game_score.mean()))
pgr = pd.DataFrame([dict(game_date=str(r_.game_date)[:10], **K.grade_outing(r_, card))
                    for _, r_ in K.outing_signatures(LP).iterrows()])
pgr.to_csv(P("october_card_postseason_history.csv"), index=False)
H['oc_history'] = pgr.to_dict('records')

# =============================================================================
# 12 · Slim frames for the dashboard (no recomputation downstream)
# =============================================================================
slim = L26[['game_pk', 'game_date', 'inning', 'at_bat_number', 'pitch_number', 'stand', 'pitch_type', 'pitch_name',
            'release_speed', 'plate_x', 'plate_z', 'zone', 'description', 'balls', 'strikes', 'n_thruorder_pitcher']].copy()
slim['game_date'] = slim.game_date.astype(str).str[:10]
slim.round(3).to_csv(P("luzardo_pitches_2026.csv"), index=False)
H['sz'] = dict(top=r3(L26.sz_top.mean()), bot=r3(L26.sz_bot.mean()))

# =============================================================================
# 13 · Back-check of uc-pps-033's byte-search claim (BS-1), by id
# =============================================================================
bscan = K.opponent_id_scan(680742, 'Bowlan, Jonathan')
bscan.to_csv(P("bs1_bowlan_backcheck.csv"), index=False)
H['bs1_bowlan_files'] = int(len(bscan))
H['bs1_bowlan_name_files'] = int(bscan.player_name_is_subject.sum()) if len(bscan) else 0
# uc-pps-033 V-3 ("notebook says .269 wOBA / 60 G; the log says .272 / 59") — test the SOURCE hypothesis:
# the client's name filter over nphl also admits pitcher-keyed AAA rows (lhvp26.parquet).
bnf, _ = K.nphl_name_frame('Bowlan, Jonathan')
bph = PH[(PH.phillies_role == 'pitching') & ~PH.game_type.isin(['S', 'E']) & (PH.player_name == 'Bowlan, Jonathan')
         & (PH.game_year == 2026)]
bkf = pd.concat([bph, bnf[bnf.game_year == 2026]], ignore_index=True, sort=False)
v3 = []
for lab, d in (('MLB log only (uc-pps-033 governed)', bph), ("client frame incl. nphl name rows", bkf)):
    r_ = K.nresults(['game_year'], d).iloc[0]
    v3.append(dict(frame=lab, games=int(d.game_pk.nunique()), pitches=int(r_.pitches), pa=int(r_.plate_apps),
                   woba=float(r_.woba), krate=float(r_.krate)))
aaa = bnf[(bnf.game_year == 2026)]
V3 = pd.DataFrame(v3)
V3['aaa_rows'] = [0, int(len(aaa))]
V3['aaa_game'] = ['', ';'.join(sorted(set(aaa.game_date.astype(str).str[:10] + ' ' + aaa.home_team + ' v ' + aaa.away_team)))]
V3.to_csv(P("bs1_bowlan_v3_resolution.csv"), index=False)
H['bs1_v3'] = V3.round(3).to_dict('records')

# =============================================================================
# 14 · DQ tail, write
# =============================================================================
dq("DQ-15", "completeness", "pitch", "FF velo/spin/pfx jointly non-null >= 99% (2026)",
   L26[L26.pitch_type == 'FF'][['release_speed', 'release_spin_rate', 'pfx_z']].notna().all(axis=1).mean() >= .99,
   r3(L26[L26.pitch_type == 'FF'][['release_speed', 'release_spin_rate', 'pfx_z']].notna().all(axis=1).mean()))
nz = float(L.zone.isna().mean())
dq("DQ-16", "completeness", "pitch", "NULL zone share (D-7/O-13 exposure; governed in_zone uses tracked denominator)",
   nz < 0.01, r3(nz), warn=nz > 0)
dq("DQ-17", "validity", "pitch", "LHP arm-side FF pfx_x positive (catcher view)", L26[L26.pitch_type == 'FF'].pfx_x.mean() > 0,
   r3(L26[L26.pitch_type == 'FF'].pfx_x.mean()))
dq("DQ-18", "comparability", "pitcher-season", "CX-1/KP-1 populations are Phillies-only (permanent)", True,
   f"{len(CX)} / {len(pop)} pitcher-seasons", warn=True)
dq("DQ-19", "validity", "pitch", "spring and exhibition rows excluded", True, int(len(spring)))
dq("DQ-20", "consistency", "file", "parent kernels sha256 pinned (K48, K44)", True,
   f"{K.PARENT_KERNEL_SHA256[:12]} / {K.GRANDPARENT_KERNEL_SHA256[:12]}")
dq("DQ-21", "validity", "pitch", "D-1 exposure: no whiff subset drops a season (inner join)",
   set(K.whiff_rate(lvl, L).game_year) == set(L.game_year), f"{L.game_year.nunique()} seasons")
dq("DQ-22", "consistency", "pitcher-season", "O-26: pitches the client's nphl name filter loses to keep-first dedup",
   True, int(nphl_lost), warn=nphl_lost > 0)
dq("DQ-23", "validity", "pitch", "postseason pitches never enter a rate (ledger only)", (L.game_type == 'R').all() and
   LP.game_type.isin(K.POSTSEASON_TYPES).all(), f"{len(LP)} postseason pitches, {LP.game_pk.nunique()} games")
DQD = pd.DataFrame(DQ)
DQD.to_csv(P("dq_scorecard.csv"), index=False)
H['dq'] = DQD.result.value_counts().to_dict()
assert (DQD.result != 'FAIL').all(), DQD[DQD.result == 'FAIL'].to_string()
H['build_seconds'] = round(time.time() - T0, 1)
P("headlines.json").write_text(json.dumps(H, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
print(json.dumps({k: H[k] for k in ('anchor', 'dq', 'build_seconds', 'nphl_lost_to_dedup', 'gs', 'ld')}, indent=1, default=str))
