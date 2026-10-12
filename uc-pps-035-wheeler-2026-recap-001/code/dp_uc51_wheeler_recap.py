"""
dp_uc51_wheeler_recap.py — build for UC #51 / uc-pps-035
"Still Zack Wheeler — the 2026 Recap"

Reads the data plane (parquet), writes receipts to out/dp_uc51_*. Every number the report, the dashboard and the
figures publish is written here first; nothing downstream recomputes a KPI.

Run (laptop VM, space-constrained):
  PYTHONPATH=/tmp/pyl PYTHONDONTWRITEBYTECODE=1 MLB_DATA_ROOT=<MLB repo> python3 dp_uc51_wheeler_recap.py
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import dp_uc51_kernel as K

T0 = time.time()
HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC51_OUT", HERE / "out"))
OUT.mkdir(parents=True, exist_ok=True)
P = lambda n: OUT / f"dp_uc51_{n}"          # noqa: E731
H: dict = {}                                 # headlines — every narrative number lives here
DQ: list = []


def dq(rule, dim, grain, text, ok, observed, warn=False):
    DQ.append(dict(rule=rule, dimension=dim, grain=grain, rule_text=text,
                   result=("WARN" if warn else ("PASS" if ok else "FAIL")), observed=str(observed)))


def r3(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 3)


def rate(x, n):
    return float(x) / float(n) if n else np.nan


def ztest(name, x1, n1, x2, n2):
    z, p = K.two_prop_z(x1, n1, x2, n2)
    return dict(test=name, x1=int(x1), n1=int(n1), r1=rate(x1, n1), x2=int(x2), n2=int(n2), r2=rate(x2, n2),
                z=float(z), p=float(p))


# =============================================================================
# 0 · Lineage, anchor, frames
# =============================================================================
lineage = K.assert_lineage()
lin = pd.concat([pd.DataFrame([dict(file=f, object="module", sha256=h, mechanism="import (pinned)") for f, h in lineage.items()]),
                 K.ix_receipt().rename(columns={'segment_sha256': 'sha256'}).assign(mechanism="IX-1 extraction (pinned)")
                 [['file', 'object', 'sha256', 'mechanism']]], ignore_index=True)
lin.to_csv(P("lineage_pins.csv"), index=False)

PH = K.load_phils_cols(years=range(2015, 2027), role=None, regular_only=False, cols=K.K49.COLS + K.ENRICH_COLS)
anchor = str(PH[(PH.game_year == 2026) & (PH.game_type == 'R')].game_date.max())[:10]
assert anchor == K.ANCHOR_GAME_DATE, f"anchor moved: {anchor} (a refresh is v1.1.0, not a correction)"
PPS = PH[(PH.phillies_role == 'pitching') & (PH.game_type == 'R')]          # governed house pitching frame

scan = K.opponent_id_scan(K.SUBJECT_ID, K.SUBJECT_NAME)
scan.to_csv(P("opponent_id_scan.csv"), index=False)
L, src, milb = K.career_frame_mlb(scan=scan, ph=PH, ph_enrich=PH)
src.to_csv(P("source_receipt.csv"), index=False)
milb.to_csv(P("milb_rows_excluded.csv"), index=False)
LP, src_post, _ = K.career_frame_mlb(scan=scan, game_types=K.POSTSEASON_TYPES, ph=PH, ph_enrich=PH)
src_post.to_csv(P("source_receipt_postseason.csv"), index=False)

# The CF-2 the org certified in UC49, run unchanged for this subject: what MI-1 and NM-1 would have published
L_cf2, _ = K.K49.career_frame(K.SUBJECT_ID, K.SUBJECT_FILE, K.SUBJECT_DISPLAY, scan=scan, ph=PH)
cf2_2026 = L_cf2[L_cf2.game_year == 2026]
H['cf2_exposure'] = dict(rows_2026=int(len(cf2_2026)), milb_rows=int(milb.rows.sum()) if len(milb) else 0,
                         milb_games=int(len(milb)), name_stamped=str(L_cf2.player_name.iat[0]))

LE = L[L.game_year.isin(K.PHILLIES_ERA)].copy()            # his Phillies tenure
DEF = PH[(PH.phillies_role == 'pitching') & ~PH.game_type.isin(['S', 'E']) & PH.game_pk.isin(set(L.game_pk) | set(LP.game_pk))]
OU2 = K.outs_by_pa(DEF)                                     # OU-2: outs per PA from the full defensive log
OU2[OU2.pitcher == K.SUBJECT_ID].to_csv(P("outs_by_pa.csv"), index=False)
L26 = L[L.game_year == 2026].copy()
L25 = L[L.game_year == 2025].copy()
spring = PH[(PH.pitcher == K.SUBJECT_ID) & (PH.game_type == 'S')]
H.update(anchor=anchor, spring_rows_excluded=int(len(spring)), career_pitches=int(len(L)),
         seasons=sorted(int(y) for y in L.game_year.unique()), dup_removed=int(src.dropped_as_duplicate.sum()),
         opp_files_with_subject=int(len(scan)), opp_files_name_matched=int(scan.player_name_is_subject.sum()),
         first_appearance=str(L26.game_date.min())[:10], last_appearance=str(L26.game_date.max())[:10],
         games_2026=int(L26.game_pk.nunique()), pitches_2026=int(len(L26)),
         postseason_pitches=int(len(LP)), postseason_games=int(LP.game_pk.nunique()))

fresh = pd.DataFrame([
    dict(source="data/phillies/phils_2015..2026.parquet", max_game_date=anchor, rows=len(PH),
         note="regular-season anchor (Game 162, 2026-09-27); Wild Card rows through 2026-10-01; build refuses any other anchor"),
    dict(source=f"data/opponents/{K.SUBJECT_FILE}", max_game_date=str(L[L.src == 'FILE'].game_date.max())[:10],
         rows=int(src[src.src == 'FILE'].rows.sum()), note="pitcher-keyed pull, NYM 2017-2019 (2013-14 not cached; 2015-16 missed, TJ)"),
    dict(source="data/opponents/* (id scan)", max_game_date="", rows=int(scan.rows.sum()),
         note=f"{len(scan)} files hold pitcher==554430; lhvp26.parquet = AAA rehab (excluded, MI-1)"),
    dict(source="carry-in: MLB.com 2025-08 / Inquirer 2026-09-19", max_game_date="2025-09-23", rows=0,
         note="2025 season ended after 8/15/2025 (blood clot; venous thoracic outlet syndrome; first-rib resection 9/23/2025) — context only, never modeled"),
    dict(source="carry-in: Inquirer 2026-09-19", max_game_date="2026-09-19", rows=0,
         note="3-yr/$126M extension signed March 2024, one year left (2027); 8.51 ERA over six starts after the break, reported cause a mechanical flaw (dropping the glove, over-rotating), since fixed; FF ~96.5 (Jul 2025) vs ~95.5 (Sep 2026)"),
    dict(source="carry-in: StatMuse (season totals)", max_game_date="2026-09-27", rows=0,
         note="2026 regular season: 14-5, 3.00 ERA, 28 GS, 162.0 IP, 193 K, 47 BB, 1.05 WHIP"),
    dict(source="carry-in: week-ahead-2026-09-28 / -10-05 / -10-12 (repo)", max_game_date="2026-10-01", rows=0,
         note="Game 162 6 IP / 1 ER, WC clinched 9/27; WC G3 10/1 at ATL: Nola 1.2 IP (Harris 3-run HR), Wheeler relief, Albies 2-run HR in the 4th, ATL 6-2"),
    dict(source="carry-in: FOX 29 2026-10-01", max_game_date="2026-10-01", rows=0,
         note="WC G3: Wheeler four innings of relief, two runs; Phillies eliminated"),
    dict(source="client: October 2026.ipynb cell 21", max_game_date="2026-10-12", rows=0,
         note="Baseball Savant values quoted by the client: Edge% 42.4, xwOBA .263 (reconciled, never substituted)"),
])
fresh.to_csv(P("freshness_manifest.csv"), index=False)

dq("DQ-01", "uniqueness", "pitch", "no duplicate PITCH_KEY in the governed career frame (CF-2b)",
   L.duplicated(K.PITCH_KEY).sum() == 0, int(L.duplicated(K.PITCH_KEY).sum()))
dq("DQ-02", "consistency", "pitch", "entity lock: every row pitcher == 554430", (L.pitcher == K.SUBJECT_ID).all(),
   L.pitcher.unique().tolist())
dq("DQ-03", "validity", "pitch", "regular season only in the rate frame", (L.game_type == 'R').all(), L.game_type.unique().tolist())
dq("DQ-04", "timeliness", "file", "Phillies log current through the pinned anchor (Game 162)", anchor == K.ANCHOR_GAME_DATE, anchor)
dq("DQ-05", "validity", "pitch", "p_throws == 'R' on every row", (L.p_throws == 'R').all(), L.p_throws.unique().tolist())
dq("DQ-06", "validity", "game", "MI-1: no minor-league game in the governed frame (both clubs MLB)",
   L.home_team.isin(K.mlb_teams(PH)).all() and L.away_team.isin(K.mlb_teams(PH)).all(),
   f"{int(milb.rows.sum()) if len(milb) else 0} AAA rows excluded ({len(milb)} games)")
dq("DQ-07", "consistency", "season", "2026 appearances == 28 (carry-in: 28 GS)", L26.game_pk.nunique() == 28, int(L26.game_pk.nunique()))
dq("DQ-08", "timeliness", "season", "2026 window = 4/25 .. 9/27 (debut after rehab; Game 162)",
   (str(L26.game_date.min())[:10], str(L26.game_date.max())[:10]) == (K.FIRST_APPEARANCE, K.LAST_REGULAR_APPEARANCE),
   f"{str(L26.game_date.min())[:10]} .. {str(L26.game_date.max())[:10]}")
dq("DQ-09", "consistency", "pitch", "Phillies-era rows all come from the house log (src == PHI)", (LE.src == 'PHI').all(),
   LE.src.value_counts().to_dict())
cov = LE[LE.events.notna()].groupby('game_year').woba_denom.apply(lambda s: s.notna().mean())
dq("DQ-10", "completeness", "pitch", "EN-1: woba_denom present on >= 99% of PA-ending rows, every Phillies-era season",
   (cov >= .99).all(), cov.round(3).to_dict())

# =============================================================================
# 1 · The recap table — SR-1 (third use) + the client's cell-21 KPI set
# =============================================================================
lvl = ['player_name', 'game_year']
CLIENT_KPIS = ['pitches', 'plate_apps', 'games', 'jam_rate', 'ba', 'obp', 'slg', 'woba', 'ops', 'krate', 'bbrate',
               'hard_hit_rate', 'barrel_rate', 'line_drive_rate']


def client_table(df, level):
    """The client's cell-21 merge chain, verbatim in structure (left merges on `level`)."""
    z = (K.nresults(level, df)
         .merge(K.hard_hit_rate(level, df), on=level, how='left', suffixes=('', '_hh'))
         .merge(K.barrel_rate(level, df), on=level, how='left', suffixes=('', '_br'))
         .merge(K.bb_type_by_level(level, df[df.bb_type == 'line_drive']), on=level, how='left', suffixes=('', '_ld'))
         .merge(K.jam_rate(level, df), on=level, how='left', suffixes=('', '_jam'))
         .merge(df.groupby(level, as_index=False).agg(games=('game_pk', 'nunique')), on=level, how='left', suffixes=('', '_gms')))
    z['line_drive_rate'] = z.bips_ld / z.bip
    return z


def governed_table(df, level):
    z = client_table(df, level)
    z = (z.merge(K.whiff_rate(level, df)[level + ['swings', 'whiffs', 'whiff_rate']], on=level, how='left')
          .merge(K.chase_rate(level, df)[level + ['chases', 'ooz', 'chase_rate']], on=level, how='left')
          .merge(K.xwoba_pa(level, df)[level + ['xwoba', 'xw_den', 'xw_fallback']], on=level, how='left')
          .merge(K.xwobacon(level, df), on=level, how='left')
          .merge(K.edge_rate(level, df)[level + ['located_pitches', 'edge_pitches', 'edge_rate']], on=level, how='left')
          .merge(K.runs_created(level, df), on=level, how='left'))
    t = df.assign(_tr=df.zone.notna(), _iz=df.zone.between(1, 9)).groupby(level, as_index=False).agg(
        tracked=('_tr', 'sum'), in_zone_n=('_iz', 'sum'))
    z = z.merge(t, on=level, how='left')
    z['in_zone_rate'] = z.in_zone_n / z.tracked
    ff = df[df.pitch_type == 'FF'].groupby(level, as_index=False).agg(ff_n=('release_speed', 'size'), ff_velo=('release_speed', 'mean'))
    z = z.merge(ff, on=level, how='left')
    z['k_minus_bb'] = z.krate - z.bbrate
    return z


REC = governed_table(L, lvl)
REC['era'] = np.where(REC.game_year >= 2020, 'PHI', 'NYM')
keep = lvl + ['era'] + CLIENT_KPIS + ['strikeouts', 'walks', 'hrs', 'hits', 'bip', 'bips', 'hard_hits', 'barrels', 'bips_ld',
                                       'tracked_swings', 'jams', 'swings', 'whiffs', 'whiff_rate', 'chases', 'ooz', 'chase_rate',
                                       'tracked', 'in_zone_n', 'in_zone_rate', 'located_pitches', 'edge_pitches', 'edge_rate',
                                       'xwoba', 'xw_den', 'xwobacon', 'runs_created', 'ff_velo', 'k_minus_bb']
REC[keep].to_csv(P("recap_governed.csv"), index=False)
RE = REC[REC.era == 'PHI'].set_index('game_year')
y26 = RE.loc[2026]
H['line26'] = {c: (int(y26[c]) if c in ('pitches', 'plate_apps', 'games', 'strikeouts', 'walks', 'hrs', 'hits', 'jams',
                                         'tracked_swings', 'barrels', 'bips', 'hard_hits', 'bips_ld') else r3(y26[c]))
               for c in ['pitches', 'plate_apps', 'games', 'strikeouts', 'walks', 'hrs', 'hits', 'ba', 'obp', 'slg', 'ops', 'woba',
                         'xwoba', 'xwobacon', 'krate', 'bbrate', 'k_minus_bb', 'whiff_rate', 'chase_rate', 'in_zone_rate',
                         'edge_rate', 'hard_hit_rate', 'barrel_rate', 'line_drive_rate', 'jam_rate', 'jams', 'tracked_swings',
                         'barrels', 'bips', 'hard_hits', 'bips_ld', 'ff_velo']}
H['era_rank'] = {}
for c, hib in [('bbrate', False), ('krate', True), ('woba', False), ('xwoba', False), ('barrel_rate', False),
               ('hard_hit_rate', False), ('line_drive_rate', False), ('chase_rate', True), ('in_zone_rate', True),
               ('edge_rate', True), ('whiff_rate', True), ('ff_velo', True), ('k_minus_bb', True)]:
    s = RE[c]
    # rank 1 = best of the seven Phillies seasons; "worst" = rank 7
    H['era_rank'][c] = dict(rank_best=int((s > s.loc[2026]).sum() + 1) if hib else int((s < s.loc[2026]).sum() + 1),
                            n=int(len(s)), era_min=r3(s.min()), era_max=r3(s.max()),
                            prior_best=r3(s.drop(2026).max() if hib else s.drop(2026).min()),
                            prior_worst=r3(s.drop(2026).min() if hib else s.drop(2026).max()))
H['era_seasons'] = {int(y): dict(pa=int(r_.plate_apps), woba=r3(r_.woba), xwoba=r3(r_.xwoba), krate=r3(r_.krate),
                                 bbrate=r3(r_.bbrate), hh=r3(r_.hard_hit_rate), barrel=r3(r_.barrel_rate),
                                 ld=r3(r_.line_drive_rate), edge=r3(r_.edge_rate), in_zone=r3(r_.in_zone_rate),
                                 chase=r3(r_.chase_rate), whiff=r3(r_.whiff_rate), velo=r3(r_.ff_velo),
                                 jam=r3(r_.jam_rate), games=int(r_.games))
                    for y, r_ in RE.iterrows()}

# The client's own frame for the table: pps[pps.player_name == 'Wheeler, Zack'] (postseason kept, S/E dropped)
pps_client = PH[(PH.phillies_role == 'pitching') & ~PH.game_type.isin(['S', 'E'])]
KF = pps_client[pps_client.player_name == K.SUBJECT_NAME].copy()
RECN = client_table(KF, lvl)
RECN[lvl + CLIENT_KPIS].to_csv(P("recap_notebook.csv"), index=False)
kpost = KF.groupby('game_year').game_type.apply(lambda s: int((s != 'R').sum())).rename('client_postseason_pitches').reset_index()
hpf = (REC[REC.era == 'PHI'][['game_year', 'pitches', 'plate_apps', 'woba', 'bbrate', 'jam_rate']]
       .merge(RECN[['game_year', 'pitches', 'plate_apps', 'woba', 'bbrate', 'jam_rate']], on='game_year', suffixes=('_gov', '_nb'))
       .merge(kpost, on='game_year', how='left'))
hpf.to_csv(P("hp_season_frames.csv"), index=False)
dq("DQ-11", "consistency", "pitch", "client frame (pps name filter) minus its postseason rows == CF-2b, every Phillies season",
   ((hpf.pitches_nb - hpf.client_postseason_pitches) == hpf.pitches_gov).all(),
   f"{int(hpf.pitches_nb.sum())} - {int(hpf.client_postseason_pitches.sum())} = {int(hpf.pitches_gov.sum())}")
H['client26'] = {c: r3(RECN.set_index('game_year').loc[2026, c]) for c in ['pitches', 'plate_apps', 'woba', 'bbrate', 'krate', 'jam_rate']}

# =============================================================================
# 2 · Tests: what moved 2025 -> 2026 and against his Phillies baseline (2021-2025, full seasons)
# =============================================================================
base = LE[LE.game_year.between(2021, 2025)]
bres = K.nresults(['player_name'], base).iloc[0]
b_hh = K.hard_hit_rate(['player_name'], base).iloc[0]; b_br = K.barrel_rate(['player_name'], base).iloc[0]
b_ld = int((base[base.type == 'X'].bb_type == 'line_drive').sum())
b_ch = K.chase_rate(['player_name'], base).iloc[0]
b_iz = base.zone.between(1, 9).sum(); b_tr = base.zone.notna().sum()
b_ed = K.edge_rate(['player_name'], base).iloc[0]
y25 = RE.loc[2025]
tests = []
for nm, x26, n26, x25, n25, xb, nb in [
    ('BB per PA', y26.walks, y26.plate_apps, y25.walks, y25.plate_apps, bres.walks, bres.plate_apps),
    ('K per PA', y26.strikeouts, y26.plate_apps, y25.strikeouts, y25.plate_apps, bres.strikeouts, bres.plate_apps),
    ('Hard-hit per BIP', y26.hard_hits, y26.bips, y25.hard_hits, y25.bips, b_hh.hard_hits, b_hh.bips),
    ('Barrel per BIP', y26.barrels, y26.bips, y25.barrels, y25.bips, b_br.barrels, b_br.bips),
    ('Line drive per BIP', y26.bips_ld, y26.bip, y25.bips_ld, y25.bip, b_ld, int(bres.bip)),
    ('Chase (swings / out-of-zone)', y26.chases, y26.ooz, y25.chases, y25.ooz, b_ch.chases, b_ch.ooz),
    ('In-zone (tracked)', y26.in_zone_n, y26.tracked, y25.in_zone_n, y25.tracked, b_iz, b_tr),
    ('Edge (ER-1)', y26.edge_pitches, y26.located_pitches, y25.edge_pitches, y25.located_pitches, b_ed.edge_pitches, b_ed.located_pitches),
]:
    t1 = ztest(nm + ' · 2026 vs 2025', x26, n26, x25, n25); t1['comparison'] = '2026 vs 2025'
    t2 = ztest(nm + ' · 2026 vs 2021-25', x26, n26, xb, nb); t2['comparison'] = '2026 vs 2021-2025 pooled'
    tests += [t1, t2]
TT = pd.DataFrame(tests)
TT.to_csv(P("rate_tests.csv"), index=False)
H['tests'] = {r_.test: dict(r1=r3(r_.r1), r2=r3(r_.r2), p=r3(r_.p), z=r3(r_.z)) for r_ in TT.itertuples()}
H['base'] = dict(bbrate=r3(rate(bres.walks, bres.plate_apps)), krate=r3(rate(bres.strikeouts, bres.plate_apps)),
                 pa=int(bres.plate_apps), edge=r3(rate(b_ed.edge_pitches, b_ed.located_pitches)),
                 in_zone=r3(rate(b_iz, b_tr)), chase=r3(rate(b_ch.chases, b_ch.ooz)))

# =============================================================================
# 3 · House context: KP-1 percentiles, CX-1b starter workloads
# =============================================================================
pop = K.house_pitcher_seasons_from(PPS)
pop = pop.merge(K.xwoba_pa(['pitcher', 'game_year'], PPS)[['pitcher', 'game_year', 'xwoba']], on=['pitcher', 'game_year'], how='left')
pop['k_minus_bb'] = pop.krate - pop.bbrate
pop.to_csv(P("house_population.csv"), index=False)
kp = []
for col, hib, lab in [('krate', True, 'K rate'), ('bbrate', False, 'BB rate'), ('k_minus_bb', True, 'K-BB'),
                      ('woba', False, 'wOBA'), ('xwoba', False, 'xwOBA'), ('whiff_rate', True, 'Whiff rate'),
                      ('chase_rate', True, 'Chase rate')]:
    v = pop[(pop.pitcher == K.SUBJECT_ID) & (pop.game_year == 2026)][col].iat[0]
    hp_ = K.house_percentile(pop.dropna(subset=[col]), col, v, hib)
    staff = pop[pop.game_year == 2026]
    srank = int(((staff[col] > v) if hib else (staff[col] < v)).sum() + 1)
    kp.append(dict(kpi=lab, column=col, value=v, **hp_, staff_rank_2026=srank, staff_n_2026=len(staff)))
KP = pd.DataFrame(kp)
KP.to_csv(P("house_percentiles.csv"), index=False)
H['kp'] = {r_.column: dict(value=r3(r_.value), pct=int(r_.percentile), rank=int(r_.rank), n=int(r_.n),
                           staff_rank=int(r_.staff_rank_2026), staff_n=int(r_.staff_n_2026)) for r_ in KP.itertuples()}

CX = K.context_frame(PPS)
CX = CX.merge(K.xwoba_pa(['pitcher', 'game_year'], PPS)[['pitcher', 'game_year', 'xwoba']], on=['pitcher', 'game_year'], how='left')
CX = CX.merge(K.edge_rate(['pitcher', 'game_year'], PPS)[['pitcher', 'game_year', 'edge_rate']], on=['pitcher', 'game_year'], how='left')
SW = CX[CX.pitches >= K.STARTER_WORKLOAD].copy()
SW['k_minus_bb'] = SW.krate - SW.bbrate
for c, asc in [('xwoba', True), ('woba', True), ('k_minus_bb', False), ('bbrate', True), ('edge_rate', False), ('whiff_rate', False)]:
    SW[f'rank_{c}'] = SW[c].rank(ascending=asc, method='min').astype(int)
SW.to_csv(P("context_starter_workloads.csv"), index=False)
s26 = SW[(SW.pitcher == K.SUBJECT_ID) & (SW.game_year == 2026)].iloc[0]
H['ctx_sw'] = dict(n=int(len(SW)), **{f'rank_{c}': int(s26[f'rank_{c}']) for c in ('xwoba', 'woba', 'k_minus_bb', 'bbrate', 'edge_rate', 'whiff_rate')},
                   staff26=SW[SW.game_year == 2026].sort_values('xwoba')[['name', 'pitches', 'xwoba', 'woba', 'bbrate']].round(3).to_dict('records'),
                   wheeler_seasons_top10_xwoba=int(((SW.pitcher == K.SUBJECT_ID) & (SW.rank_xwoba <= 10)).sum()))

# =============================================================================
# 4 · Edge and zone expansion (ER-1 inherited; client's Savant 42.4% reconciled)
# =============================================================================
L26['month'] = pd.to_datetime(L26.game_date).dt.month
apps = K.appearance_log(L26)
gs26 = K.game_score_b(L26, OU2)
sig26 = K.outing_signatures(L26)
starts = (gs26.merge(apps[['game_pk', 'ff_velo', 'ff_max', 'rest_days']], on='game_pk', how='left')
              .merge(sig26[['game_pk', 'whiff_per_100', 'chase_rate', 'bb_rate', 'first_n_ff_velo', 'first_n_ff', 'ooz', 'chases']],
                     on='game_pk'))
starts['opp'] = np.where(starts.home_team == 'PHI', starts.away_team, starts.home_team)
starts['venue'] = np.where(starts.home_team == 'PHI', 'home', 'away')
starts['start_no'] = np.arange(1, len(starts) + 1)
starts['period'] = K.stretch_label(starts)
SWN = K.stretch_windows(starts)
SWN.to_csv(P("stretch_windows.csv"), index=False)
dq("DQ-30", "consistency", "window", "SR-2: exactly one six-start post-break window reconciles to the reported 8.51, and it is the stretch",
   int(SWN.reconciles_to_carry_in.sum()) == 1 and SWN[SWN.reconciles_to_carry_in]['first'].iat[0] == K.STRETCH_FIRST,
   SWN[SWN.reconciles_to_carry_in][['first', 'last', 'r', 'outs']].to_dict('records'))
H['stretch_windows'] = [dict(first=a, last=b, r27=r3(c)) for a, b, c in zip(SWN['first'], SWN['last'], SWN.r27)]
starts = (starts.merge(K.edge_rate(['game_pk'], L26)[['game_pk', 'located_pitches', 'edge_pitches', 'edge_rate']], on='game_pk', how='left')
                .merge(K.xwoba_pa(['game_pk'], L26)[['game_pk', 'xwoba']], on='game_pk', how='left')
                .merge(L26.assign(_tr=L26.zone.notna(), _iz=L26.zone.between(1, 9)).groupby('game_pk', as_index=False)
                       .agg(tracked=('_tr', 'sum'), in_zone_n=('_iz', 'sum')), on='game_pk', how='left'))
starts['in_zone_rate'] = starts.in_zone_n / starts.tracked
NC = K.clear_miss(L26)
nc_g = NC.groupby('game_pk', as_index=False).agg(located=('clear_miss', 'size'), clear_miss=('clear_miss', 'sum'),
                                                 miss_arm=('miss_side', lambda s: (s == 'arm').sum()),
                                                 miss_glove=('miss_side', lambda s: (s == 'glove').sum()),
                                                 miss_high=('miss_side', lambda s: (s == 'high').sum()),
                                                 miss_low=('miss_side', lambda s: (s == 'low').sum()))
nc_g['clear_miss_rate'] = nc_g.clear_miss / nc_g.located
MX = K.mechanics_by_start(L26)
starts = starts.merge(nc_g, on='game_pk', how='left').merge(MX.drop(columns=['game_date', 'velo']), on='game_pk', how='left')
starts['kbb'] = (starts.k - starts.bb) / starts.pa
starts['r27'] = 27 * starts.r / starts.outs
starts.to_csv(P("starts_2026.csv"), index=False)
dq("DQ-12", "validity", "game", "OU-1: no inning credits more than 3 outs (2026)",
   (L26.assign(_o=K.outs_recorded(L26)).groupby(['game_pk', 'inning'])._o.sum() <= 3).all(), "per game-inning")
dq("DQ-13", "consistency", "game", "every 2026 regular-season appearance is a start (entered in the 1st)", starts.started.all(),
   int(starts.started.sum()))
L26 = L26.merge(starts[['game_pk', 'period']], on='game_pk', how='left')
H['stretch_dates'] = [str(d)[:10] for d in starts[starts.period == 'stretch'].game_date]


def period_table(df, st, key):
    z = governed_table(df.assign(player_name=K.SUBJECT_NAME), ['player_name', key]).drop(columns='player_name')
    s = st.groupby(key, as_index=False).agg(starts=('game_pk', 'size'), r=('r', 'sum'), outs=('outs', 'sum'),
                                            gs=('game_score', 'mean'), ff_first15=('first_n_ff_velo', 'mean'),
                                            clear_miss=('clear_miss', 'sum'), located=('located', 'sum'),
                                            miss_arm=('miss_arm', 'sum'), miss_glove=('miss_glove', 'sum'),
                                            miss_high=('miss_high', 'sum'), miss_low=('miss_low', 'sum'))
    z = z.merge(s, on=key, how='left')
    z['r27'] = 27 * z.r / z.outs
    z['clear_miss_rate'] = z.clear_miss / z.located
    for side in ('arm', 'glove', 'high', 'low'):
        z[f'miss_{side}_share'] = z[f'miss_{side}'] / z.clear_miss
    return z


PER = period_table(L26, starts, 'period')
order = {'first_half': 0, 'opener': 1, 'stretch': 2, 'finish': 3}
PER = PER.sort_values('period', key=lambda s: s.map(order))
PER.to_csv(P("periods_2026.csv"), index=False)
H['periods'] = {r_.period: dict(starts=int(r_.starts), pa=int(r_.plate_apps), krate=r3(r_.krate), bbrate=r3(r_.bbrate),
                                woba=r3(r_.woba), xwoba=r3(r_.xwoba), edge=r3(r_.edge_rate), in_zone=r3(r_.in_zone_rate),
                                chase=r3(r_.chase_rate), whiff=r3(r_.whiff_rate), hh=r3(r_.hard_hit_rate),
                                barrel=r3(r_.barrel_rate), r=int(r_.r), outs=int(r_.outs), r27=r3(r_.r27),
                                walks=int(r_.walks), strikeouts=int(r_.strikeouts), velo=r3(r_.ff_velo),
                                first15=r3(r_.ff_first15), clear_miss=r3(r_.clear_miss_rate),
                                miss_arm=r3(r_.miss_arm_share), miss_glove=r3(r_.miss_glove_share),
                                miss_high=r3(r_.miss_high_share), miss_low=r3(r_.miss_low_share), tied=r3(r_.jam_rate))
                for r_ in PER.itertuples()}
MO = period_table(L26, starts.assign(month=pd.to_datetime(starts.game_date).dt.month), 'month')
MO.to_csv(P("monthly_2026.csv"), index=False)
H['months'] = {int(r_.month): dict(starts=int(r_.starts), pa=int(r_.plate_apps), bbrate=r3(r_.bbrate), krate=r3(r_.krate),
                                   woba=r3(r_.woba), xwoba=r3(r_.xwoba), edge=r3(r_.edge_rate), in_zone=r3(r_.in_zone_rate),
                                   chase=r3(r_.chase_rate), r27=r3(r_.r27), velo=r3(r_.ff_velo), walks=int(r_.walks))
               for r_ in MO.itertuples()}
L26['half'] = np.where(L26.game_date < K.ALL_STAR_BREAK, 'first', 'second')
HV = period_table(L26, starts.assign(half=np.where(starts.game_date < K.ALL_STAR_BREAK, 'first', 'second')), 'half')
HV.to_csv(P("halves_2026.csv"), index=False)
H['halves'] = {r_.half: dict(starts=int(r_.starts), pa=int(r_.plate_apps), bbrate=r3(r_.bbrate), krate=r3(r_.krate),
                             woba=r3(r_.woba), xwoba=r3(r_.xwoba), edge=r3(r_.edge_rate), in_zone=r3(r_.in_zone_rate),
                             chase=r3(r_.chase_rate), r27=r3(r_.r27), velo=r3(r_.ff_velo), r=int(r_.r), outs=int(r_.outs))
               for r_ in HV.itertuples()}

rest = PER[PER.period != 'stretch'][['walks', 'plate_apps', 'edge_pitches', 'located_pitches', 'in_zone_n', 'tracked',
                                     'chases', 'ooz', 'clear_miss', 'located', 'strikeouts', 'miss_arm']].sum()
stv = PER[PER.period == 'stretch'].iloc[0]
pt = [ztest('BB per PA · stretch vs rest of 2026', stv.walks, stv.plate_apps, rest.walks, rest.plate_apps),
      ztest('K per PA · stretch vs rest of 2026', stv.strikeouts, stv.plate_apps, rest.strikeouts, rest.plate_apps),
      ztest('Edge · stretch vs rest of 2026', stv.edge_pitches, stv.located_pitches, rest.edge_pitches, rest.located_pitches),
      ztest('In-zone · stretch vs rest of 2026', stv.in_zone_n, stv.tracked, rest.in_zone_n, rest.tracked),
      ztest('Chase · stretch vs rest of 2026', stv.chases, stv.ooz, rest.chases, rest.ooz),
      ztest('Clear miss · stretch vs rest of 2026', stv.clear_miss, stv.located, rest.clear_miss, rest.located),
      ztest('Arm-side share of clear misses · stretch vs rest of 2026', stv.miss_arm, stv.clear_miss, rest.miss_arm, rest.clear_miss)]
mx = starts.dropna(subset=['rel_x'])
for c, lab in [('rel_x', 'FF release x (ft)'), ('rel_z', 'FF release height (ft)'), ('arm_angle', 'FF arm angle (deg)'),
               ('ext', 'FF extension (ft)'), ('rci_in', 'Release consistency RCI (in)'), ('ff_velo', 'FF velocity (mph)')]:
    a = mx[mx.period == 'stretch'][c].dropna(); b = mx[mx.period != 'stretch'][c].dropna()
    t, p = stats.ttest_ind(a, b, equal_var=False) if len(a) > 1 and len(b) > 1 else (np.nan, np.nan)
    pt.append(dict(test=f'{lab} · stretch vs rest of 2026 (start means, Welch)', r1=a.mean(), n1=len(a), r2=b.mean(), n2=len(b),
                   z=float(t), p=float(p), x1=np.nan, x2=np.nan))
PT = pd.DataFrame(pt)
PT.to_csv(P("stretch_tests.csv"), index=False)
H['stretch_tests'] = {r_.test.split(' · ')[0]: dict(stretch=r3(r_.r1), rest=r3(r_.r2), p=r3(r_.p), n1=int(r_.n1), n2=int(r_.n2))
                      for r_ in PT.itertuples()}
H['arm_angle_cov_2026'] = r3(L26[L26.pitch_type == 'FF'].arm_angle.notna().mean())
H['savant_reconcile'] = dict(edge_client=0.424, edge_er1=H['line26']['edge_rate'], xwoba_client=0.263, xwoba_xw1=H['line26']['xwoba'])

# =============================================================================
# 5 · Swing timing: JR-1 tied-up rate, ST-1 buckets, the sinker in on righties
# =============================================================================
STY = K.swing_timing(['game_year'], LE[LE.game_year >= 2025])
STY.to_csv(P("swing_timing_by_season.csv"), index=False)
STP = K.swing_timing(['pitch_type', 'stand'], L26)
STP = STP.merge(K.jam_rate(['pitch_type', 'stand'], L26)[['pitch_type', 'stand', 'below_floor']], on=['pitch_type', 'stand'], how='left')
STP.to_csv(P("swing_timing_by_pitch_stand_2026.csv"), index=False)
H['st'] = {int(r_.game_year): dict(tied=r3(r_.tied_up_rate), centered=r3(r_.centered_rate), flail=r3(r_.flail_rate),
                                   n=int(r_.tracked_swings)) for r_ in STY.itertuples()}
H['st_pitch'] = [dict(pt=r_.pitch_type, stand=r_.stand, tied=r3(r_.tied_up_rate), n=int(r_.tracked_swings),
                      below_floor=bool(r_.below_floor)) for r_ in STP.itertuples()]

pp = PPS[PPS.game_year >= 2025]
JP = K.swing_timing(['pitcher', 'game_year'], pp)
JP = JP[JP.tracked_swings >= K.JAM_SWING_FLOOR].copy()
JP = JP.merge(pp.groupby('pitcher').player_name.agg(lambda s: s.mode().iat[0]).rename('name'), on='pitcher')
JP['rank_tied'] = JP.tied_up_rate.rank(ascending=False, method='min').astype(int)
JP.to_csv(P("tied_up_population.csv"), index=False)
j26 = JP[(JP.pitcher == K.SUBJECT_ID) & (JP.game_year == 2026)].iloc[0]
big = JP[JP.tracked_swings >= 500]
H['tied_pop'] = dict(n=int(len(JP)), rank=int(j26.rank_tied), value=r3(j26.tied_up_rate), mean=r3(JP.tied_up_rate.mean()),
                     n_big=int(len(big)), rank_big=int((big.tied_up_rate > j26.tied_up_rate).sum() + 1),
                     leader=JP.sort_values('tied_up_rate', ascending=False).iloc[0][['name', 'game_year', 'tied_up_rate', 'tracked_swings']].astype(str).to_dict())

COL = 'intercept_ball_minus_batter_pos_x_inches'
JR_SWINGS = ['foul', 'foul_tip', 'hit_into_play', 'swinging_pitchout', 'swinging_strike', 'swinging_strike_blocked']  # JR-1's list (no bunts)
si = L26[(L26.pitch_type == 'SI') & (L26.stand == 'R') & L26.description.isin(JR_SWINGS) & (L26[COL] < K.JAM_MAX_IN)]
si_bip = si[si.type == 'X']
hits = ['single', 'double', 'triple', 'home_run']
H['si_jam'] = dict(swings=int(len(si)), bip=int(len(si_bip)), not_in_play=int((si.type == 'S').sum()),
                   hits=int(si_bip.events.isin(hits).sum()), xwobacon=r3(si_bip.estimated_woba_using_speedangle.mean()),
                   ev=r3(si_bip.launch_speed.mean()), gb_share=r3((si_bip.bb_type == 'ground_ball').mean()))
nf, nphl_lost = K.K49.nphl_name_frame(K.SUBJECT_NAME)
enr = []
for f in sorted(set(scan[scan.player_name_is_subject].file)):
    fp = K.K49.OPP_DIR / f
    if COL in K.K49._cols_in(fp, [COL]):
        e = pd.read_parquet(fp, columns=['pitcher'] + K.PITCH_KEY + [COL]); enr.append(e[e.pitcher == K.SUBJECT_ID])
nf = nf.merge(pd.concat(enr).drop_duplicates(['pitcher'] + K.PITCH_KEY), on=['pitcher'] + K.PITCH_KEY, how='left') if enr else nf.assign(**{COL: np.nan})
ZW = pd.concat([nf, PH[(PH.phillies_role == 'pitching') & ~PH.game_type.isin(['S', 'E']) & (PH.player_name == K.SUBJECT_NAME)]],
               ignore_index=True, sort=False)
zsi = ZW[(ZW.pitch_type == 'SI') & (ZW.game_year == 2026) & (ZW.stand == 'R') & (ZW[COL] < K.JAM_MAX_IN)]
H['si_jam_client'] = dict(bip=int((zsi.type == 'X').sum()), not_in_play=int((zsi.type == 'S').sum()),
                          bunts=int((zsi.description == 'foul_bunt').sum()),
                          lhv_rows=int((zsi.home_team.eq('LHV') | zsi.away_team.eq('LHV')).sum()),
                          postseason_rows=int((zsi.game_type != 'R').sum()))
H['zw'] = dict(rows=int(len(ZW)), rows_2026=int((ZW.game_year == 2026).sum()),
               lhv_2026=int(((ZW.game_year == 2026) & (ZW.home_team.eq('LHV') | ZW.away_team.eq('LHV'))).sum()),
               nphl_lost_to_dedup=int(nphl_lost))
zwj = K.jam_rate(['game_year'], ZW[ZW.game_year == 2026]).iloc[0]
H['zw_jam26'] = dict(jam_rate=r3(zwj.jam_rate), tracked=int(zwj.tracked_swings))
sw_all = ZW[(ZW.game_year == 2026) & ZW.description.isin(K.SWINGS)]
H['zw_jam26_draft'] = r3(rate((ZW[(ZW.game_year == 2026)][COL] < 32.5).sum(), len(sw_all)))

opp_rows = []
for f in sorted(K.K49.OPP_DIR.glob('*.parquet')):
    cols = K.K49._cols_in(f, ['player_name', 'game_year', 'description', 'des'] + K.PITCH_KEY + [COL])
    if COL not in cols:
        continue
    d = pd.read_parquet(f, columns=cols); opp_rows.append(d[d.game_year >= 2025].assign(_f=f.name))
OPP = pd.concat(opp_rows, ignore_index=True).drop_duplicates(subset=K.PITCH_KEY, keep='first')
pos_ = PH[(PH.phillies_role == 'batting') & ~PH.game_type.isin(['S', 'E']) & (PH.game_year >= 2025)]
pps_ = PH[(PH.phillies_role == 'pitching') & ~PH.game_type.isin(['S', 'E']) & (PH.game_year >= 2025)]
CPOP = pd.concat([OPP.assign(_role='nphl'), pos_.assign(_role='pos'), pps_.assign(_role='pps')], ignore_index=True, sort=False)
cz = K.jam_rate(['player_name', 'game_year'], CPOP)
roles = CPOP.groupby(['player_name', 'game_year'])._role.agg(lambda s: ','.join(sorted(set(s)))).rename('roles').reset_index()
cz = cz.merge(roles, on=['player_name', 'game_year'], how='left')
cz = cz[cz.tracked_swings > 49]
cz.to_csv(P("tied_up_population_client.csv"), index=False)
cw = cz[(cz.player_name == K.SUBJECT_NAME) & (cz.game_year == 2026)].iloc[0]
H['tied_pop_client'] = dict(n=int(len(cz)), batter_seasons=int(cz.roles.str.contains('pos').sum()),
                            rank=int((cz.jam_rate > cw.jam_rate).sum() + 1), value=r3(cw.jam_rate))
del OPP, CPOP

# =============================================================================
# 6 · Platoon splits (client cell 21, governed)
# =============================================================================
PL = governed_table(LE, ['player_name', 'game_year', 'stand'])
PL.to_csv(P("platoon_by_season.csv"), index=False)
H['platoon'] = {f"{int(r_.game_year)}{r_.stand}": dict(pa=int(r_.plate_apps), woba=r3(r_.woba), xwoba=r3(r_.xwoba),
                                                        krate=r3(r_.krate), bbrate=r3(r_.bbrate), hh=r3(r_.hard_hit_rate),
                                                        barrel=r3(r_.barrel_rate), whiff=r3(r_.whiff_rate), chase=r3(r_.chase_rate),
                                                        edge=r3(r_.edge_rate), tied=r3(r_.jam_rate))
                for r_ in PL.itertuples()}
pl26 = PL[PL.game_year == 2026].set_index('stand')
H['platoon_gap'] = {int(y): r3(g.woba[g.stand == 'L'].iat[0] - g.woba[g.stand == 'R'].iat[0]) for y, g in PL.groupby('game_year')}
H['platoon_xgap'] = {int(y): r3(g.xwoba[g.stand == 'L'].iat[0] - g.xwoba[g.stand == 'R'].iat[0]) for y, g in PL.groupby('game_year')}
pl_tests = [ztest('BB per PA · LHB vs RHB 2026', pl26.loc['L', 'walks'], pl26.loc['L', 'plate_apps'], pl26.loc['R', 'walks'], pl26.loc['R', 'plate_apps']),
            ztest('K per PA · LHB vs RHB 2026', pl26.loc['L', 'strikeouts'], pl26.loc['L', 'plate_apps'], pl26.loc['R', 'strikeouts'], pl26.loc['R', 'plate_apps']),
            ztest('Hard-hit · LHB vs RHB 2026', pl26.loc['L', 'hard_hits'], pl26.loc['L', 'bips'], pl26.loc['R', 'hard_hits'], pl26.loc['R', 'bips']),
            ztest('Barrel · LHB vs RHB 2026', pl26.loc['L', 'barrels'], pl26.loc['L', 'bips'], pl26.loc['R', 'barrels'], pl26.loc['R', 'bips'])]
pd.DataFrame(pl_tests).to_csv(P("platoon_tests.csv"), index=False)
H['platoon_tests'] = {t['test'].split(' · ')[0]: dict(L=r3(t['r1']), R=r3(t['r2']), p=r3(t['p'])) for t in pl_tests}
PLN = client_table(KF, ['player_name', 'game_year', 'stand'])
PLN.to_csv(P("platoon_notebook.csv"), index=False)

# =============================================================================
# 7 · Arsenal (AR-2), pitch map (PM-1), pitch plot points
# =============================================================================
ars = K.arsenal_table(LE[LE.game_year >= 2024], by=('game_year',))
ars.to_csv(P("arsenal_by_season.csv"), index=False)
ars_st = K.arsenal_table(L26, by=('stand',))
ars_st = ars_st.merge(K.xwoba_pa(['stand', 'pitch_type'], L26)[['stand', 'pitch_type', 'xwoba']], on=['stand', 'pitch_type'], how='left')
ars_st.to_csv(P("arsenal_by_stand_2026.csv"), index=False)
pm = K.pitch_map_centroid(L26)
pm.to_csv(P("pitch_map_2026.csv"), index=False)


def av(df_, y, pt_, c):
    s = df_[(df_.game_year == y) & (df_.pitch_type == pt_)]
    return r3(s[c].iat[0]) if len(s) else None


H['ars'] = {str(y): {p_: dict(usage=av(ars, y, p_, 'usage'), velo=av(ars, y, p_, 'velo'), whiff=av(ars, y, p_, 'whiff_rate'),
                              rv100=av(ars, y, p_, 'rv100'), n=av(ars, y, p_, 'n'), ivb=av(ars, y, p_, 'ivb_in'), hb=av(ars, y, p_, 'hb_in'),
                              xwobacon=av(ars, y, p_, 'xwobacon'))
                     for p_ in ars[ars.game_year == y].pitch_type} for y in (2024, 2025, 2026)}
H['ars_stand'] = {st: {r_.pitch_type: dict(usage=r3(r_.usage), whiff=r3(r_.whiff_rate), n=int(r_.n), xwoba=r3(r_.xwoba))
                       for r_ in ars_st[ars_st.stand == st].itertuples()} for st in ('L', 'R')}
slim = L26[['game_pk', 'game_date', 'inning', 'at_bat_number', 'pitch_number', 'stand', 'pitch_type', 'pitch_name',
            'release_speed', 'pfx_x', 'pfx_z', 'plate_x', 'plate_z', 'zone', 'description', 'events', 'type', 'balls', 'strikes',
            COL, 'period']].copy()
slim['game_date'] = slim.game_date.astype(str).str[:10]
slim['ivb_in'] = slim.pfx_z * 12; slim['hb_in'] = slim.pfx_x * 12
slim.round(3).to_csv(P("wheeler_pitches_2026.csv"), index=False)
H['sz'] = dict(top=r3(L26.sz_top.mean()), bot=r3(L26.sz_bot.mean()))
dq("DQ-14", "validity", "pitch", "RHP arm-side FF pfx_x negative (catcher view, + = first-base side)",
   L26[L26.pitch_type == 'FF'].pfx_x.mean() < 0, r3(L26[L26.pitch_type == 'FF'].pfx_x.mean()))

# =============================================================================
# 8 · Velocity: by month 2024-2026; the carry-in figures
# =============================================================================
vel = (LE[(LE.pitch_type == 'FF') & LE.game_year.isin([2024, 2025, 2026])]
       .assign(month=lambda d: pd.to_datetime(d.game_date).dt.month)
       .groupby(['game_year', 'month'], as_index=False).agg(n=('release_speed', 'size'), velo=('release_speed', 'mean')))
vel.to_csv(P("ff_velo_by_month.csv"), index=False)
vm = vel.set_index(['game_year', 'month']).velo
H['velo'] = dict(jul25=r3(vm.get((2025, 7))), sep26=r3(vm.get((2026, 9))), apr26=r3(vm.get((2026, 4))),
                 season26=r3(H['line26']['ff_velo']), season25=r3(RE.loc[2025, 'ff_velo']), season21=r3(RE.loc[2021, 'ff_velo']),
                 by_year={int(y): r3(v) for y, v in RE.ff_velo.items()})

# =============================================================================
# 9 · Parent reproduction — uc-pps-020 first-half publishes
# =============================================================================
fh = L26[L26.half == 'first']
fh_r = K.nresults(['half'], fh).iloc[0]
fh_out = int(K.outs_recorded(fh).sum())
fh_ch = K.chase_rate(['half'], fh).iloc[0]
repro = pd.DataFrame([
    dict(parent='uc-pps-020', figure='first-half starts', published=15, recomputed=int(fh.game_pk.nunique())),
    dict(parent='uc-pps-020', figure='first-half IP (event outs)', published=92.0, recomputed=float(f"{fh_out // 3}.{fh_out % 3}")),
    dict(parent='uc-pps-020', figure='first-half wOBA', published=0.246, recomputed=round(float(fh_r.woba), 3)),
    dict(parent='uc-pps-020', figure='first-half K%', published=0.304, recomputed=round(float(fh_r.krate), 3)),
    dict(parent='uc-pps-020', figure='first-half BB%', published=0.062, recomputed=round(float(fh_r.bbrate), 3)),
    dict(parent='uc-pps-020', figure='first-half chase rate', published=0.362, recomputed=round(float(fh_ch.chase_rate), 3)),
])
repro['match'] = (repro.published - repro.recomputed).abs() <= 0.0015
repro.to_csv(P("parent_reproduction.csv"), index=False)
H['repro'] = f"{int(repro.match.sum())}/{len(repro)}"
dq("DQ-15", "consistency", "season", "parent reproduction: uc-pps-020 first-half figures recomputed from CF-2b",
   repro.match.all(), H['repro'])
H['fh_in_zone_all_pitches'] = r3(rate(fh.zone.between(1, 9).sum(), len(fh)))

# =============================================================================
# 10 · Carry-in reconciliation (season totals, Game 162)
# =============================================================================
outs26 = int(starts.outs.sum())                                   # OU-2
outs26_ou1 = int(K.outs_recorded(L26).sum())
ibb = int((L26.events == 'intent_walk').sum())
g162 = starts[starts.game_date.astype(str).str[:10] == K.LAST_REGULAR_APPEARANCE].iloc[0]
H['carry'] = dict(outs=outs26, outs_ou1=outs26_ou1, ip=f"{outs26 // 3}.{outs26 % 3}", k=int(y26.strikeouts), bb=int(y26.walks), ibb=ibb,
                  starts=int(len(starts)), r_on_watch=int(starts.r.sum()),
                  g162=dict(date=str(g162.game_date)[:10], ip=g162.ip_display, r=int(g162.r), k=int(g162.k), bb=int(g162.bb),
                            pitches=int(g162.pitches), opp=g162.opp))
dq("DQ-16", "consistency", "season", "2026 strikeouts == carry-in 193", int(y26.strikeouts) == 193, int(y26.strikeouts))
dq("DQ-17", "consistency", "season", "2026 walks (+ IBB) == carry-in 47", int(y26.walks) + ibb == 47, f"{int(y26.walks)} + {ibb} IBB")
dq("DQ-18", "consistency", "season", "OU-2 outs == carry-in 162.0 IP (486 outs); OU-1 shown beside it", outs26 == 486,
   f"OU-2 {outs26} · OU-1 {outs26_ou1}")
dq("DQ-19", "consistency", "game", "Game 162 reconciles to carry-in (6 IP, 1 run)", (g162.ip_display == '6.0') and int(g162.r) <= 1,
   f"{g162.ip_display} IP, {int(g162.r)} R on watch")

# =============================================================================
# 11 · Postseason ledger — the Wild Card relief outing beside his Phillies Octobers
# =============================================================================
pl = K.game_score_b(LP, OU2)
pl['round'] = pl.game_type.map({'F': 'Wild Card', 'D': 'Division Series', 'L': 'LCS', 'W': 'World Series'})
pl['role'] = np.where(pl.started, 'start', 'relief')
pl['opp'] = np.where(pl.home_team == 'PHI', pl.away_team, pl.home_team)
pl = pl.merge(K.first_n_velo(LP)[['game_pk', 'first_n_ff_velo']], on='game_pk', how='left')
pl = pl.merge(K.xwoba_pa(['game_pk'], LP)[['game_pk', 'xwoba']], on='game_pk', how='left')
pl.to_csv(P("postseason_ledger.csv"), index=False)
H['post'] = [dict(date=str(r_.game_date)[:10], round=r_.round, opp=r_.opp, role=r_.role, ip=r_.ip_display, outs=int(r_.outs),
                  pa=int(r_.pa), h=int(r_.h), r=int(r_.r), bb=int(r_.bb), k=int(r_.k), hr=int(r_.hr), pitches=int(r_.pitches),
                  gs=int(r_.game_score)) for r_ in pl.itertuples()]
pt_ = K.nresults(['game_type'], LP.assign(game_type='ALL')).iloc[0]
H['post_tot'] = dict(games=int(len(pl)), starts=int(pl.started.sum()), pa=int(pt_.plate_apps), woba=r3(pt_.woba),
                     krate=r3(pt_.krate), bbrate=r3(pt_.bbrate), outs=int(pl.outs.sum()), r=int(pl.r.sum()))
WC = LP[LP.game_pk == K.WC_GAME_PK].sort_values(['at_bat_number', 'pitch_number']).copy()
names = K.K49.batter_names(PH[PH.game_year == 2026])
WC['batter_name'] = WC.batter.map(names).fillna(WC.batter.astype(str))
wpa = WC[WC.events.notna()][['inning', 'at_bat_number', 'batter_name', 'stand', 'events', 'des', 'launch_speed',
                             'estimated_woba_using_speedangle', 'bat_score', 'post_bat_score']].copy()
wpa['runs'] = wpa.post_bat_score - wpa.bat_score
wpa.to_csv(P("wc_g3_plate_appearances.csv"), index=False)
wcg = pl[pl.game_pk == K.WC_GAME_PK].iloc[0]
wc_hr = wpa[wpa.events == 'home_run']
H['wc'] = dict(date='2026-10-01', ip=wcg.ip_display, r=int(wcg.r), h=int(wcg.h), bb=int(wcg.bb), k=int(wcg.k), hr=int(wcg.hr),
               pitches=int(wcg.pitches), pa=int(wcg.pa), inn_first=int(wcg.inn_first), inn_last=int(wcg.inn_last),
               hr_batters=wc_hr.batter_name.tolist(), hr_innings=wc_hr.inning.astype(int).tolist(),
               hr_runs=wc_hr.runs.astype(int).tolist(), first15=r3(wcg.first_n_ff_velo), xwoba=r3(wcg.xwoba),
               days_since_g162=int((pd.Timestamp('2026-10-01') - pd.Timestamp(K.LAST_REGULAR_APPEARANCE)).days))
dq("DQ-20", "consistency", "game", "WC G3 relief reconciles to carry-in (4 IP, 2 R, Albies 2-run HR in the 4th)",
   wcg.ip_display == '4.0' and int(wcg.r) == 2 and any('Albies' in str(b) for b in H['wc']['hr_batters']),
   f"{wcg.ip_display} IP, {int(wcg.r)} R, HR {H['wc']['hr_batters']} inn {H['wc']['hr_innings']}")

# =============================================================================
# 12 · The "Still Wheeler" card for 2027 — OC-1, second use, pre-registered
# =============================================================================
card = K.october_card(sig26)
card['registered_on'] = '2026-10-12'
card['anchor'] = anchor
card['applies_to'] = '2027 regular-season starts (and any 2027 postseason outing)'
LPR = LE[LE.game_year.between(2021, 2025)]
card_prime = K.october_card(K.outing_signatures(LPR))
card = card.merge(card_prime[['signature', 'bar', 'season_median']].rename(columns={'bar': 'bar_2021_25', 'season_median': 'median_2021_25'}),
                  on='signature')
card.to_csv(P("still_wheeler_card.csv"), index=False)
graded = pd.DataFrame([dict(game_pk=r_.game_pk, game_date=str(r_.game_date)[:10], **K.grade_outing(r_, card))
                       for _, r_ in sig26.iterrows()])
graded = graded.merge(starts[['game_pk', 'r', 'outs', 'game_score', 'period']], on='game_pk')
graded.to_csv(P("still_wheeler_backtest_2026.csv"), index=False)
bt = graded.groupby('period').verdict.apply(lambda s: f"{int((s == 'ON-SCRIPT').sum())}/{len(s)}").to_dict()
on = graded[graded.verdict == 'ON-SCRIPT']; off = graded[graded.verdict == 'OFF-SCRIPT']
prime_g = pd.DataFrame([K.grade_outing(r_, card) for _, r_ in K.outing_signatures(LPR).iterrows()])
wc_sig = K.outing_signatures(WC)
wc_grade = K.grade_outing(wc_sig.iloc[0], card)
H['card'] = dict(bars={r_.signature: r3(r_.bar) for r_ in card.itertuples()},
                 bars_prime={r_.signature: r3(r_.bar_2021_25) for r_ in card.itertuples()},
                 medians={r_.signature: r3(r_.season_median) for r_ in card.itertuples()},
                 medians_prime={r_.signature: r3(r_.median_2021_25) for r_ in card.itertuples()},
                 labels={r_.signature: r_.label for r_ in card.itertuples()},
                 backtest_by_period=bt, on=int(len(on)), off=int(len(off)),
                 on_r27=r3(27 * on.r.sum() / on.outs.sum()) if len(on) else None,
                 off_r27=r3(27 * off.r.sum() / off.outs.sum()) if len(off) else None,
                 prime_on_share=r3((prime_g.verdict == 'ON-SCRIPT').mean()), prime_starts=int(len(prime_g)),
                 wc_posthoc=wc_grade, wc_values={c: r3(wc_sig.iloc[0][c]) for c in ('first_n_ff_velo', 'chase_rate', 'whiff_per_100', 'bb_rate')})

# =============================================================================
# 13 · DQ tail, write
# =============================================================================
trk = H['line26']['tracked_swings'] / max(int(y26.swings), 1)
dq("DQ-21", "completeness", "pitch", "2026 swings carrying a tracked intercept (JR-1 denominator / house swings) >= 90%",
   trk >= .90, r3(trk))
dq("DQ-22", "completeness", "pitch", "NULL zone share (governed in_zone uses tracked denominator)", float(L.zone.isna().mean()) < .01,
   r3(float(L.zone.isna().mean())))
dq("DQ-23", "completeness", "pitch", "FF arm_angle coverage 2026 (MX-1 arm angle published only with its n)",
   True, H['arm_angle_cov_2026'], warn=H['arm_angle_cov_2026'] < .95)
dq("DQ-24", "comparability", "pitcher-season", "KP-1 / CX-1b / tied-up populations are Phillies-only (permanent)", True,
   f"{len(pop)} / {len(SW)} / {len(JP)} pitcher-seasons", warn=True)
dq("DQ-25", "validity", "pitch", "spring and exhibition rows excluded", True, int(len(spring)))
dq("DQ-26", "consistency", "file", "parent modules sha256-pinned; IX-1 segments sha256-pinned", True,
   f"{len(lineage)} modules, {len(K.IX_PIN)} segments")
dq("DQ-27", "validity", "pitch", "postseason pitches never enter a rate (ledger only)",
   (L.game_type == 'R').all() and LP.game_type.isin(K.POSTSEASON_TYPES).all(), f"{len(LP)} postseason pitches, {LP.game_pk.nunique()} games")
dq("DQ-28", "consistency", "pitch", "MI-1 exposure in the client's cell-22 frame (zw): AAA rehab rows in '2026'",
   True, H['zw']['lhv_2026'], warn=H['zw']['lhv_2026'] > 0)
dq("DQ-29", "consistency", "pitch", "O-26 exposure: Wheeler pitches the nphl name filter loses to keep-first dedup",
   True, int(nphl_lost), warn=nphl_lost > 0)
DQD = pd.DataFrame(DQ)
DQD.to_csv(P("dq_scorecard.csv"), index=False)
H['dq'] = DQD.result.value_counts().to_dict()
H['build_seconds'] = round(time.time() - T0, 1)
P("headlines.json").write_text(json.dumps(H, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
print(DQD[['rule', 'result', 'observed']].to_string())
print(json.dumps({k: H[k] for k in ('anchor', 'dq', 'build_seconds')}, default=str))
assert (DQD.result != 'FAIL').all(), DQD[DQD.result == 'FAIL'].to_string()
