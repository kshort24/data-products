"""
dp_uc35_nola_alcantara.py — build script for uc-pos-012
=======================================================
UC #36 · uc-pos-012-nola-alcantara-showdown-001 · Phillies Offense value stream
Game context: Aaron Nola (PHI) vs Sandy Alcantara (MIA), CBP, 2026-08-19.

Concept (human DPO): treat "Aaron Nola against the Marlins" as a synthetic
Phillies HITTER — the composite batter Nola *elicits* from Miami — and place
him inside the Phillies player-season offensive distribution. Same for
Wheeler. Highlight the real Bryce Harper vs MIA. Flip side: Sandy Alcantara
is the pitcher who has thrown the most pitches to the Phillies offense in the
Statcast era; quantify that exposure and Harper's book against him.

DPO floor ruling (intake 2026-08-18): the comparison floor is NOLA'S MINIMUM
season plate_apps vs MIA, derived from the data at each published grain —
never the house 50-PA floor (deviation governed in 03_governance).

Every KPI comes from dp_uc35_kernel.py (governed / _fix variants). Every
figure's numbers trace to a CSV receipt in out/.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dp_uc35_kernel import (  # noqa: E402
    ALCANTARA, DATA, HARPER, NOLA, PA_FLOOR_HOUSE, WHEELER,
    kpi_family, load_frames, load_opponent, opponent_of_phi, pa_rows,
    runs_created, synthetic_batter, woba_weights)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)

# Manual carry-ins (logged in the freshness manifest, dp_uc25 lineup precedent):
# display names for pitcher ids the DPO named in the intake prose. These ids are
# NOT used in any filter or join — annotation only. Everything filtered joins on
# ids confirmed from local caches or the entity-lock asserts below.
MANUAL_NAME_CARRYIN = {453286: 'Scherzer, Max', 594798: 'deGrom, Jacob'}

KPI_COLS = ['plate_apps', 'pitches', 'ba', 'obp', 'slg', 'ops', 'woba',
            'krate', 'whiff_rate', 'chase_rate', 'hard_hit_rate',
            'barrel_rate', 'runs_created', 'rc_per_pa']


def save(df, name):
    p = os.path.join(OUT, f'dp_uc35_{name}.csv')
    df.to_csv(p, index=False)
    print(f'  receipt {name}: {df.shape}')
    return df


def main():
    w = woba_weights()
    pos, pps = load_frames()

    # ── entity locks + dedup + freshness asserts ────────────────────────────
    key = ['game_pk', 'at_bat_number', 'pitch_number']
    for nm, d in [('pos', pos), ('pps', pps)]:
        dup = d.duplicated(subset=key).sum()
        assert dup == 0, f'{nm} carries {dup} duplicate pitch rows'
    as_of = max(pos.game_date.max(), pps.game_date.max()).date().isoformat()

    nola_name = pps.loc[pps.pitcher == NOLA, 'player_name'].mode()
    assert list(nola_name) == ['Nola, Aaron'], f'entity lock fail: {list(nola_name)}'
    harper_name = pos.loc[pos.batter == HARPER, 'player_name'].mode()
    assert list(harper_name) == ['Harper, Bryce'], f'entity lock fail: {list(harper_name)}'
    wheeler_cache = load_opponent('wheeler')
    assert set(wheeler_cache.pitcher.unique()) == {WHEELER}
    alc_cache = load_opponent('alcantara')
    assert set(alc_cache.pitcher.unique()) == {ALCANTARA}
    assert list(alc_cache.player_name.mode()) == ['Alcantara, Sandy']

    # semantics probe (receipted): player_name is the PHILLIE of interest —
    # batter on pos rows, pitcher on pps rows. Never a pitcher name on pos.
    sem = pd.DataFrame([
        {'frame': 'pos', 'row_meaning': 'PHI batting',
         'player_name_is': 'batter',
         'check': pos.loc[pos.batter == HARPER, 'player_name'].mode().iat[0]},
        {'frame': 'pps', 'row_meaning': 'PHI pitching',
         'player_name_is': 'pitcher',
         'check': pps.loc[pps.pitcher == NOLA, 'player_name'].mode().iat[0]},
    ])
    save(sem, 'player_name_semantics')

    # ── the synthetic batter: "Noles" = what Nola elicits from Miami ────────
    nola_mia = synthetic_batter(pps, 'Noles', opponent='MIA', pitcher=NOLA)
    assert len(nola_mia), 'no Nola vs MIA rows'
    nm_season = kpi_family(['game_year'], nola_mia, w).assign(entity='Noles')
    nm_season_stand = kpi_family(['game_year', 'stand'], nola_mia, w).assign(entity='Noles')
    nm_career = kpi_family(['entity'], nola_mia, w)
    nm_career_stand = kpi_family(['entity', 'stand'], nola_mia, w)
    save(nm_season, 'nola_mia_seasons')
    save(nm_season_stand, 'nola_mia_season_stand')
    save(nm_career, 'nola_mia_career')
    save(nm_career_stand, 'nola_mia_career_stand')

    # ── DPO floor ruling: Nola's minimum plate_apps in the dataset ─────────
    FLOOR = int(nm_season.plate_apps.min())
    floor_stand = (nm_season_stand.groupby('stand', as_index=False)
                   .agg(floor=('plate_apps', 'min')))
    floor_stand['floor'] = floor_stand['floor'].astype(int)
    fd = pd.DataFrame([{
        'rule': "human DPO 2026-08-18: 'use his minimum plate_apps in the dataset'",
        'grain': 'game_year', 'floor': FLOOR,
        'house_floor_deviated_from': PA_FLOOR_HOUSE,
        'derived_from_rows': len(nm_season)}])
    save(fd, 'floor_derivation')
    save(floor_stand, 'floor_derivation_stand')
    print(f'  FLOOR (season grain) = {FLOOR} PA; by stand = '
          f'{dict(zip(floor_stand.stand, floor_stand.floor))}')

    # ── Wheeler vs MIA: career constant (2017-2019 NYM cache + 2020- pps) ──
    wh_pps = synthetic_batter(pps, 'Wheeler vs MIA', opponent='MIA', pitcher=WHEELER)
    wh_nym = synthetic_batter(wheeler_cache, 'Wheeler vs MIA', opponent='MIA',
                              pitcher=WHEELER)
    overlap = set(wh_pps.game_year.unique()) & set(wh_nym.game_year.unique())
    assert not overlap, f'Wheeler source overlap: {overlap}'
    shared = [c for c in wh_pps.columns if c in wh_nym.columns]
    wheeler_mia = pd.concat([wh_pps[shared], wh_nym[shared]], ignore_index=True)
    assert wheeler_mia.duplicated(subset=key).sum() == 0
    wm_season = kpi_family(['game_year'], wheeler_mia, w).assign(entity='Wheeler vs MIA')
    wm_career = kpi_family(['entity'], wheeler_mia, w)
    save(wm_season, 'wheeler_mia_seasons')
    save(wm_career, 'wheeler_mia_career')

    # ── Phillies hitter-seasons (the box population) ───────────────────────
    lvl = ['player_name', 'batter', 'game_year']
    phit = kpi_family(lvl, pos, w)
    phit['below_house_floor'] = phit.plate_apps < PA_FLOOR_HOUSE
    phit['in_population'] = phit.plate_apps > FLOOR
    save(phit, 'phi_hitter_seasons')

    lvl_s = ['player_name', 'batter', 'game_year', 'stand']
    phit_stand = kpi_family(lvl_s, pos, w)
    phit_stand = phit_stand.merge(floor_stand, on='stand', how='left')
    phit_stand['in_population'] = phit_stand.plate_apps > phit_stand['floor']
    save(phit_stand, 'phi_hitter_season_stand')

    # ── Harper vs MIA (the real hitter, highlighted) ───────────────────────
    harper_mia = pos[(pos.batter == HARPER) & (opponent_of_phi(pos) == 'MIA')].copy()
    harper_mia['entity'] = 'Harper vs MIA'
    hm_season = kpi_family(['game_year'], harper_mia, w).assign(entity='Harper vs MIA')
    hm_season['below_floor'] = hm_season.plate_apps <= FLOOR
    hm_career = kpi_family(['entity'], harper_mia, w)
    save(hm_season, 'harper_mia_seasons')
    save(hm_career, 'harper_mia_career')

    # ── box-plot master frame (fig1 traces to this receipt) ────────────────
    box = phit[phit.in_population].copy()
    box['entity'] = 'Phillies Hitters'
    keep = ['entity', 'player_name', 'game_year'] + KPI_COLS
    box_master = box[keep].copy()
    save(box_master, 'boxplot_population')

    # ── the flip side: Alcantara vs the Phillies offense ───────────────────
    alc_vs_phi = pos[pos.pitcher == ALCANTARA].copy()
    alc_vs_phi['entity'] = 'PHI vs Alcantara'
    av_season = kpi_family(['game_year'], alc_vs_phi, w).assign(entity='PHI vs Alcantara')
    av_career = kpi_family(['entity'], alc_vs_phi, w)
    av_stand = kpi_family(['entity', 'stand'], alc_vs_phi, w)
    save(av_season, 'alcantara_phi_seasons')
    save(av_career, 'alcantara_phi_career')
    save(av_stand, 'alcantara_phi_career_stand')

    # exposure ranking: every pitcher the PHI offense has seen since 2015
    exp = (pos.groupby('pitcher', as_index=False)
              .agg(pitches=('des', 'size'),
                   first_year=('game_year', 'min'),
                   last_year=('game_year', 'max')))
    pa_ct = (pa_rows(pos).groupby('pitcher', as_index=False)
             .agg(plate_apps=('des', 'size')))
    exp = exp.merge(pa_ct, on='pitcher', how='left')
    exp['plate_apps'] = exp.plate_apps.fillna(0).astype(int)
    exp = exp.sort_values('pitches', ascending=False).reset_index(drop=True)
    exp['rank'] = np.arange(1, len(exp) + 1)
    cache_names = {ALCANTARA: 'Alcantara, Sandy', WHEELER: 'Wheeler, Zack',
                   NOLA: 'Nola, Aaron'}
    exp['pitcher_name'] = exp.pitcher.map(cache_names)
    exp['name_source'] = np.where(exp.pitcher_name.notna(), 'local cache', '')
    mc = exp.pitcher.map(MANUAL_NAME_CARRYIN)
    exp.loc[exp.pitcher_name.isna() & mc.notna(), 'name_source'] = \
        'manual carry-in (DPO intake prose) — verify'
    exp['pitcher_name'] = exp.pitcher_name.fillna(mc)
    alc_rank = int(exp.loc[exp.pitcher == ALCANTARA, 'rank'].iat[0])
    save(exp.head(25), 'pitcher_exposure_rank_top25')

    # Harper's most-faced pitchers since 2015
    hp = pos[pos.batter == HARPER]
    hexp = (hp.groupby('pitcher', as_index=False)
              .agg(pitches=('des', 'size')))
    hpa = (pa_rows(hp).groupby('pitcher', as_index=False)
           .agg(plate_apps=('des', 'size')))
    hexp = (hexp.merge(hpa, on='pitcher', how='left')
                .sort_values('plate_apps', ascending=False)
                .reset_index(drop=True))
    hexp['plate_apps'] = hexp.plate_apps.fillna(0).astype(int)
    hexp['rank_by_pa'] = np.arange(1, len(hexp) + 1)
    hexp['pitcher_name'] = hexp.pitcher.map(cache_names)
    mc2 = hexp.pitcher.map(MANUAL_NAME_CARRYIN)
    hexp['name_source'] = np.where(hexp.pitcher_name.notna(), 'local cache', '')
    hexp.loc[hexp.pitcher_name.isna() & mc2.notna(), 'name_source'] = \
        'manual carry-in (DPO intake prose) — verify'
    hexp['pitcher_name'] = hexp.pitcher_name.fillna(mc2)
    harper_alc_rank = int(hexp.loc[hexp.pitcher == ALCANTARA, 'rank_by_pa'].iat[0])
    save(hexp.head(25), 'harper_pitcher_rank_top25')

    # Harper vs Alcantara head-to-head
    h_v_a = hp[hp.pitcher == ALCANTARA].copy()
    hva_career = kpi_family(['batter'], h_v_a, w).assign(entity='Harper vs Alcantara')
    hva_season = kpi_family(['game_year'], h_v_a, w).assign(entity='Harper vs Alcantara')
    save(hva_career, 'harper_vs_alcantara_career')
    save(hva_season, 'harper_vs_alcantara_seasons')

    # Harper vs the other two carry-in ids (Scherzer / deGrom), annotation ids
    hvx = []
    for pid, nm in MANUAL_NAME_CARRYIN.items():
        d = hp[hp.pitcher == pid]
        if len(d):
            r = kpi_family(['batter'], d, w)
            r['pitcher'] = pid
            r['pitcher_name'] = nm
            hvx.append(r)
    if hvx:
        save(pd.concat(hvx, ignore_index=True), 'harper_vs_carryin_pitchers')

    # ── DQ scorecard ───────────────────────────────────────────────────────
    bip26 = pos[(pos.game_year == 2026) & (pos.type == 'X')]
    dq = pd.DataFrame([
        {'check': 'dedup (game_pk, at_bat_number, pitch_number)',
         'frame': 'pos+pps', 'result': 'PASS', 'value': 0},
        {'check': 'entity lock Nola 605400 -> "Nola, Aaron" (mode of player_name)',
         'frame': 'pps', 'result': 'PASS', 'value': 605400},
        {'check': 'entity lock Harper 547180 -> "Harper, Bryce"',
         'frame': 'pos', 'result': 'PASS', 'value': 547180},
        {'check': 'entity lock Alcantara 645261 (alcantara.parquet, sole id)',
         'frame': 'cache', 'result': 'PASS', 'value': 645261},
        {'check': 'entity lock Wheeler 554430 (wheeler.parquet, sole id)',
         'frame': 'cache', 'result': 'PASS', 'value': 554430},
        {'check': 'Wheeler source overlap (cache years x pps years)',
         'frame': 'wheeler_mia', 'result': 'PASS', 'value': 0},
        {'check': 'game_type: S/E excluded, R+postseason retained',
         'frame': 'pos+pps', 'result': 'PASS',
         'value': ','.join(sorted(set(pos.game_type.unique())))},
        {'check': 'launch_speed_angle null rate on 2026 BIP (barrel CDE)',
         'frame': 'pos', 'result': 'INFO',
         'value': round(float(bip26.launch_speed_angle.isna().mean()), 4)},
        {'check': 'zone null rate all rows (chase CDE, O-2 open)',
         'frame': 'pos', 'result': 'INFO',
         'value': round(float(pos.zone.isna().mean()), 4)},
        {'check': 'bat_score/post_bat_score completeness (runs_created CDEs)',
         'frame': 'pos', 'result': 'PASS' if pos.bat_score.notna().all()
            and pos.post_bat_score.notna().all() else 'FAIL',
         'value': int(pos.bat_score.isna().sum() + pos.post_bat_score.isna().sum())},
    ])
    save(dq, 'dq_scorecard')

    # ── freshness manifest ─────────────────────────────────────────────────
    fr = pd.DataFrame([
        {'source': 'data/phillies/phils_2015-2026.parquet',
         'max_game_date': as_of, 'note': 'T-1 vs 2026-08-18 intake; Nola last start 2026-08-13 in-frame'},
        {'source': 'data/opponents/wheeler.parquet',
         'max_game_date': str(wheeler_cache.game_date.max().date()),
         'note': 'NYM years 2017-2019 only; used solely for Wheeler-vs-MIA pre-PHI coverage'},
        {'source': 'data/opponents/alcantara.parquet',
         'max_game_date': str(alc_cache.game_date.max().date()),
         'note': 'STALE (no 2026); used for entity lock only — all vs-PHI analysis from pos'},
        {'source': 'manual carry-in',
         'max_game_date': '2026-08-18',
         'note': 'game context (Nola vs Alcantara, CBP 2026-08-19) + display names for ids '
                 + str(MANUAL_NAME_CARRYIN) + ' from DPO intake prose; ids annotation-only'},
    ])
    save(fr, 'freshness_manifest')

    # ── headline numbers for report/dashboard (single source of truth) ─────
    n_c, w_c, h_c = nm_career.iloc[0], wm_career.iloc[0], hm_career.iloc[0]
    a_c = av_career.iloc[0]
    hva = hva_career.iloc[0] if len(hva_career) else None
    headlines = {
        'as_of': as_of, 'game': '2026-08-19', 'floor_pa': FLOOR,
        'floor_by_stand': {r.stand: int(r.floor) for r in floor_stand.itertuples()},
        'nola_mia': {k: round(float(n_c[k]), 4) for k in KPI_COLS},
        'wheeler_mia': {k: round(float(w_c[k]), 4) for k in KPI_COLS},
        'harper_mia': {k: round(float(h_c[k]), 4) for k in KPI_COLS},
        'phi_vs_alcantara': {k: round(float(a_c[k]), 4) for k in KPI_COLS},
        'harper_vs_alcantara': (
            {k: round(float(hva[k]), 4) for k in KPI_COLS} if hva is not None else None),
        'alcantara_exposure_rank': alc_rank,
        'alcantara_pitches_to_phi': int(exp.loc[exp.pitcher == ALCANTARA, 'pitches'].iat[0]),
        'harper_alcantara_rank_by_pa': harper_alc_rank,
        'phi_hitter_seasons_in_population': int(phit.in_population.sum()),
        'nola_mia_seasons': int(len(nm_season)),
    }
    with open(os.path.join(OUT, 'dp_uc35_headlines.json'), 'w') as f:
        json.dump(headlines, f, indent=2)
    print(json.dumps(headlines, indent=2)[:2200])


if __name__ == '__main__':
    main()
