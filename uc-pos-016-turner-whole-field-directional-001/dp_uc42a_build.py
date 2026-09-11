"""
dp_uc42a_build.py — v1.1.0 addendum build for uc-pos-016 (dp_uc42a).
============================================================================
Extends dp_uc42's build. Reproduces every v1.0.0 published figure first
(parent-reproduction check), then adds only what the addendum needs:

  * a PITCH-LEVEL frame (plate_x/plate_z) -> the pitch map the DPO actually
    wanted in v1 and specified as a spray chart (his declared correction);
  * a true BALLS-IN-PLAY spray frame on field coordinates, sharing a
    `pitch_uid` with the pitch frame so the two views cross-highlight;
  * the zone-cell decomposition of the v1.0.0 in-zone finding: WHICH parts of
    the strike zone the pull->oppo shift came from. New question, same data,
    no new claim beyond what the counts support;
  * the Phillies player-season context pool behind the DPO's rug plot.

Usage:
    DP_UC42_DATA="C:/Users/Kellen/OneDrive/Documents/Python Scripts/MLB" \
        python dp_uc42a_build.py
"""
import json
import os

import numpy as np
import pandas as pd

from dp_uc42a_kernel import (
    load_pos, turner_rows, build_pitch_frame, build_bip_frame,
    context_player_seasons, directional_rate_table, pooled_two_prop_z,
    hard_hit_rate, runs_created_per_600, pitch_location_profile,
    zone_cell_direction_mix, bip_value_table, directional_value_decomposition,
    SEASONS, CURRENT, BASELINE, SUBJECT, SUBJECT_MLBAM,
    AS_OF, PA_FLOOR, DIRECTION_COLORS, P_THROWS_COLORS, STRIKE_ZONE,
)

OUT = 'out'
os.makedirs(OUT, exist_ok=True)
DIRS = ['Pull', 'Straightaway', 'Oppo']

# Statcast zone geography — used for LABELS only. `zone` itself stays the
# governed in/out authority (zone < 10); nothing below re-derives it.
ZONE_ROW = {1: 'Up', 2: 'Up', 3: 'Up', 4: 'Middle', 5: 'Middle',
            6: 'Middle', 7: 'Down', 8: 'Down', 9: 'Down'}
ZONE_COL_RHB = {1: 'Inside', 2: 'Middle', 3: 'Outside',
                4: 'Inside', 5: 'Middle', 6: 'Outside',
                7: 'Inside', 8: 'Middle', 9: 'Outside'}


def rate_block(cur, base, label, dimension):
    """2026 vs pooled 2023-25 pull/oppo/straightaway, with the ST-1 band."""
    rows = []
    for metric in DIRS:
        x1, n1 = int((cur.hit_direction == metric).sum()), len(cur)
        x2, n2 = int((base.hit_direction == metric).sum()), len(base)
        if n1 == 0 or n2 == 0:
            rows.append(dict(dimension=dimension, slice=label, metric=metric.lower(),
                             rate_2026=np.nan, n_2026=n1, rate_2023_25=np.nan,
                             n_2023_25=n2, diff=np.nan, z=np.nan))
            continue
        z, diff = pooled_two_prop_z(x1, n1, x2, n2)
        rows.append(dict(dimension=dimension, slice=label, metric=metric.lower(),
                         rate_2026=x1 / n1, n_2026=n1,
                         rate_2023_25=x2 / n2, n_2023_25=n2, diff=diff, z=z))
    return rows


def main():
    pos = load_pos(SEASONS)
    tt = turner_rows(pos)
    pitches = build_pitch_frame(tt)
    pos_rs = tt[tt.game_type == 'R'].copy()
    bip = build_bip_frame(pos_rs)

    # -- 1. PARENT REPRODUCTION: v1.0.0's three published tables ------------
    tabs = [directional_rate_table(bip[bip.ooz], 'outside'),
            directional_rate_table(bip[~bip.ooz], 'in_zone'),
            directional_rate_table(bip, 'all')]
    full = pd.concat(tabs, ignore_index=True).sort_values(['zone', 'game_year'])
    full.to_csv(f'{OUT}/dp_uc42a_kpi_directional_by_zone_year.csv', index=False)

    sig_rows = []
    for zone_label, mask in [('outside', bip.ooz), ('in_zone', ~bip.ooz)]:
        base = bip[mask & bip.game_year.isin(BASELINE)]
        cur = bip[mask & (bip.game_year == CURRENT)]
        sig_rows += rate_block(cur, base, zone_label, 'zone_class')
    # Column names are held identical to v1.0.0's file (zone / metric / ... / z)
    # so the parent-reproduction check is a straight column-for-column compare
    # rather than a mapping the harness could get wrong in the build's favour.
    sig = (pd.DataFrame(sig_rows).drop(columns=['dimension'])
             .rename(columns={'slice': 'zone'}))
    sig = sig[['zone', 'metric', 'rate_2026', 'n_2026', 'rate_2023_25',
               'n_2023_25', 'diff', 'z']]
    sig.to_csv(f'{OUT}/dp_uc42a_significance_2026_vs_pooled.csv', index=False)

    ooz_share = bip.groupby('game_year').ooz.mean().reset_index()
    ooz_share.columns = ['game_year', 'ooz_share_of_bip']
    ooz_share.to_csv(f'{OUT}/dp_uc42a_ooz_share_by_year.csv', index=False)

    # -- 2. NEW: where in the zone the in-zone shift lives ------------------
    iz = bip[~bip.ooz].copy()
    iz['zone_int'] = iz.zone.astype(int)
    iz['zone_row'] = iz.zone_int.map(ZONE_ROW)
    iz['zone_col'] = iz.zone_int.map(ZONE_COL_RHB)

    cell_rows = []
    for dim, col in [('zone_row', 'zone_row'), ('zone_col', 'zone_col'),
                     ('zone_cell', 'zone_int')]:
        for val, grp in iz.groupby(col):
            cell_rows += rate_block(grp[grp.game_year == CURRENT],
                                    grp[grp.game_year.isin(BASELINE)],
                                    str(val), dim)
    cells = pd.DataFrame(cell_rows)
    cells.to_csv(f'{OUT}/dp_uc42a_in_zone_decomposition.csv', index=False)

    # PM-2 — per-zone-cell direction mix by season (pitch map <-> spray bridge)
    mix = zone_cell_direction_mix(bip)
    mix.to_csv(f'{OUT}/dp_uc42a_zone_cell_direction_mix.csv', index=False)

    # -- 2b. PM-1: did the OPPONENT move, or did the hitter? ---------------
    prof = pitch_location_profile(pitches[pitches.game_type == 'R'])
    prof.to_csv(f'{OUT}/dp_uc42a_pitch_location_profile.csv', index=False)

    # PM-1 is run THREE ways on purpose. The whole-plate test answers "did
    # anything about the attack plan move"; the two conditional tests answer
    # the question the finding actually needs — did the IN-ZONE attack move,
    # given that the in-zone batted-ball direction did. A pooled test can be
    # significant off an out-of-zone-only change and be read as if it licensed
    # an in-zone explanation. Splitting it removes that reading.
    zk = pitches[(pitches.game_type == 'R') & pitches.zone.notna()]

    def _chi(cells, label, conditional):
        sub = zk[zk.zone.isin(cells)] if conditional else zk
        cur = sub[sub.game_year == CURRENT]
        bas = sub[sub.game_year.isin(BASELINE)]
        obs = np.array([int((cur.zone == c).sum()) for c in cells], dtype=float)
        base_share = np.array([float((bas.zone == c).mean()) for c in cells])
        exp = base_share * obs.sum()
        chi2 = float(((obs - exp) ** 2 / np.where(exp > 0, exp, np.nan)).sum())
        dof = len(cells) - 1
        try:
            from scipy.stats import chi2 as _d
            pval = float(_d.sf(chi2, dof))
        except Exception:
            pval = float('nan')
        tvd = float(0.5 * np.abs(obs / obs.sum() - base_share).sum())
        return dict(test=label, cells=','.join(str(c) for c in cells),
                    n_2026=int(obs.sum()), n_2023_25=int(len(bas)),
                    chi2=chi2, dof=dof, p_value=pval,
                    total_variation_distance=tvd,
                    max_cell_shift_pp=float(np.abs(obs / obs.sum() - base_share).max() * 100))

    ALLZ = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14]
    stability = pd.DataFrame([
        _chi(ALLZ, 'PM-1a whole-plate attack-location stability', False),
        _chi([1, 2, 3, 4, 5, 6, 7, 8, 9], 'PM-1b IN-ZONE attack stability (conditional on in-zone)', True),
        _chi([11, 12, 13, 14], 'PM-1c OUT-OF-ZONE attack stability (conditional on out-of-zone)', True),
    ])
    stability['p_text'] = ['%.1e' % v if v < 1e-3 else '%.3f' % v for v in stability.p_value]
    stability['in_zone_rate_2026'] = float((zk[zk.game_year == CURRENT].zone < 10).mean())
    stability['in_zone_rate_2023_25'] = float((zk[zk.game_year.isin(BASELINE)].zone < 10).mean())
    stability.to_csv(f'{OUT}/dp_uc42a_attack_stability.csv', index=False)

    # -- 2c. DC-1: how much of the damage loss the mix change accounts for --
    val = bip_value_table(bip)
    val.to_csv(f'{OUT}/dp_uc42a_bip_value_by_direction.csv', index=False)
    val_iz = bip_value_table(bip[~bip.ooz])
    val_iz.insert(0, 'zone', 'in_zone')
    val_iz.to_csv(f'{OUT}/dp_uc42a_bip_value_in_zone.csv', index=False)

    dec_all = directional_value_decomposition(bip)
    dec_all.insert(0, 'population', 'all BIP')
    dec_iz = directional_value_decomposition(bip[~bip.ooz])
    dec_iz.insert(0, 'population', 'in-zone BIP')
    dec = pd.concat([dec_all, dec_iz], ignore_index=True)
    dec.to_csv(f'{OUT}/dp_uc42a_value_decomposition.csv', index=False)

    # -- 3. NEW: context pool behind the rug --------------------------------
    ctx = runs_created_per_600(context_player_seasons(pos))
    keep = ['player_name', 'game_year', 'games', 'pitches', 'plate_apps',
            'woba', 'ops', 'hard_hit_rate', 'barrel_rate', 'runs_created',
            'runs_created_per_600', 'bips', 'barrels', 'hard_hits',
            'df_color', 'is_subject']
    ctx_out = ctx[keep].copy()
    ctx_out.to_csv(f'{OUT}/dp_uc42a_context_player_seasons.csv', index=False)

    # -- 4. Defect exposure, measured not assumed ---------------------------
    lvl = ['player_name', 'game_year']
    rs = pos[pos.game_type == 'R']
    all_bip_groups = rs[rs.type == 'X'].groupby(lvl).size().rename('bips').reset_index()
    hh_groups = hard_hit_rate(lvl, rs)[lvl]
    dropped = all_bip_groups.merge(hh_groups, on=lvl, how='left', indicator=True)
    d1_dropped = dropped[dropped._merge == 'left_only']
    untracked = rs[(rs.type == 'X') & rs.launch_speed.isna()]
    defects = pd.DataFrame([
        dict(defect='D-1 hard_hit_rate inner merge drops zero-hard-hit groups',
             exposure_metric='player-seasons with >=1 BIP but 0 hard hits, dropped',
             value=int(len(d1_dropped)),
             affects_this_build=bool(len(d1_dropped) > 0)),
        dict(defect='O-8 hard_hit_rate counts untracked BIP as not-hard-hit',
             exposure_metric='BIP rows with NULL launch_speed in the 2023-26 pos pool',
             value=int(len(untracked)),
             affects_this_build=bool(len(untracked) > 0)),
        dict(defect='O-8 (subject)', exposure_metric='Turner BIP rows with NULL launch_speed',
             value=int(((pos_rs.type == 'X') & pos_rs.launch_speed.isna()).sum()),
             affects_this_build=bool(((pos_rs.type == 'X') & pos_rs.launch_speed.isna()).sum() > 0)),
        dict(defect='D-7/O-13 in_zone counts NULL zone as in-zone',
             exposure_metric='Turner BIP rows with NULL zone (excluded from BOTH populations here)',
             value=int((pos_rs[pos_rs.type == 'X'].zone.isna()).sum()),
             affects_this_build=False),
    ])
    defects.to_csv(f'{OUT}/dp_uc42a_defect_exposure.csv', index=False)

    # -- 5. Season-frame payload for the dashboard --------------------------
    b = bip.copy()
    b['month'] = b.game_date.dt.month
    bip_recs = [
        dict(u=r.pitch_uid, y=int(r.game_year), x=round(float(r.loc_x), 1),
             yy=round(float(r.loc_y), 1), d=r.hit_direction,
             oz=bool(r.ooz), z=int(r.zone), t=r.p_throws,
             px=None if pd.isna(r.plate_x) else round(float(r.plate_x), 3),
             pz=None if pd.isna(r.plate_z) else round(float(r.plate_z), 3),
             ev=None if pd.isna(r.launch_speed) else round(float(r.launch_speed), 1),
             la=None if pd.isna(r.launch_angle) else round(float(r.launch_angle), 1),
             e=(r.events if isinstance(r.events, str) else ''),
             bb=(r.bb_type if isinstance(r.bb_type, str) else ''),
             pt=(r.pitch_type if isinstance(r.pitch_type, str) else ''),
             dt=r.game_date.strftime('%Y-%m-%d'), m=int(r.month))
        for r in b.itertuples()
    ]

    # Non-BIP pitches are drawn as a faint backdrop only, so they ship as four
    # parallel arrays instead of 7.6k objects (~3x smaller payload, same data).
    p = pitches.copy()
    nb = p[(~p.is_bip) & p.plate_x.notna() & p.plate_z.notna()]
    nonbip_cols = dict(
        y=[int(v) for v in nb.game_year],
        px=[round(float(v), 2) for v in nb.plate_x],
        pz=[round(float(v), 2) for v in nb.plate_z],
        oz=[(-1 if pd.isna(v) else int(v >= 10)) for v in nb.zone],
        t=[(1 if v == 'L' else 0) for v in nb.p_throws],
    )

    ctx_recs = [
        dict(p=r.player_name, y=int(r.game_year), br=float(r.barrel_rate),
             rc=float(r.runs_created), rc6=round(float(r.runs_created_per_600), 2),
             g=int(r.games), pa=int(r.plate_apps),
             woba=float(r.woba), ops=float(r.ops),
             hh=(None if pd.isna(r.hard_hit_rate) else round(float(r.hard_hit_rate), 4)),
             s=bool(r.is_subject))
        for r in ctx_out.itertuples()
    ]

    payload = dict(
        meta=dict(uc='uc-pos-016-turner-whole-field-directional-001',
                  dp='dp_uc42a', version='1.1.0', parent='dp_uc42 v1.0.0',
                  subject=SUBJECT, mlbam=SUBJECT_MLBAM, as_of=AS_OF,
                  seasons=SEASONS, pa_floor=PA_FLOOR,
                  dir_colors=DIRECTION_COLORS, throws_colors=P_THROWS_COLORS,
                  zone=STRIKE_ZONE),
        bip=bip_recs, other=nonbip_cols, ctx=ctx_recs,
        rates=json.loads(full.to_json(orient='records')),
        sig=json.loads(sig.to_json(orient='records')),
        cells=json.loads(cells.to_json(orient='records')),
        mix=json.loads(mix.to_json(orient='records')),
        prof=json.loads(prof.to_json(orient='records')),
        stability=json.loads(stability.to_json(orient='records')),
        value=json.loads(val.to_json(orient='records')),
        value_iz=json.loads(val_iz.to_json(orient='records')),
        decomp=json.loads(dec.to_json(orient='records')),
        ooz=json.loads(ooz_share.to_json(orient='records')),
        defects=json.loads(defects.to_json(orient='records')),
    )
    with open(f'{OUT}/dp_uc42a_payload.json', 'w') as f:
        json.dump(payload, f, separators=(',', ':'))

    bip.to_csv(f'{OUT}/dp_uc42a_turner_bip_extract.csv', index=False)
    p[['pitch_uid', 'game_year', 'game_date', 'plate_x', 'plate_z', 'zone',
       'pitch_type', 'p_throws', 'type', 'is_bip', 'events', 'description']
      ].to_csv(f'{OUT}/dp_uc42a_turner_pitch_extract.csv', index=False)

    print(f'BIP rows: {len(bip)}  | all pitches: {len(p)}  | non-BIP w/ loc: {len(nb)}')
    print(f'context player-seasons (>= {PA_FLOOR} PA): {len(ctx_out)}')
    print(full.to_string(index=False))
    print(sig.to_string(index=False))
    print(cells[cells.dimension != 'zone_cell'].to_string(index=False))
    print(defects.to_string(index=False))
    print(prof[['game_year', 'n_pitches', 'in_zone_rate', 'median_plate_x',
                'median_plate_z']].to_string(index=False))
    print(stability.to_string(index=False))
    print(dec.to_string(index=False))
    print(val_iz.to_string(index=False))
    tt_ctx = ctx_out[ctx_out.player_name == SUBJECT]
    print(tt_ctx[['game_year', 'plate_apps', 'barrel_rate', 'hard_hit_rate',
                  'woba', 'ops', 'runs_created', 'runs_created_per_600']].to_string(index=False))
    return bip, p, ctx_out, full, sig, cells


if __name__ == '__main__':
    main()
