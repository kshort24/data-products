"""
dp_uc37_bohm_turnaround.py — build script for uc-pos-013-bohm-second-half-turnaround-001.
Produces every CSV/JSON receipt and every figure quoted in the report.
Run from this directory. Data root: DP_UC37_DATA env var, else the MLB repo path.
"""
from __future__ import annotations
import json, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import dp_uc37_kernel as k

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY, RED, GREY, GOLD = '#002D72', '#E81828', '#B8BFCB', '#C4A24A'
plt.rcParams.update({'figure.dpi': 150, 'font.size': 9,
                     'axes.edgecolor': '#55606E', 'axes.labelcolor': '#1a1a1a',
                     'axes.titlesize': 10.5, 'axes.titleweight': 'bold',
                     'axes.titlecolor': NAVY, 'savefig.bbox': 'tight'})
R3 = lambda d: d.round(3)
H = {}

KPI_FUNS = (k.swing_rate, k.chase_rate_g, k.whiff_rate_fix, k.ooz_whiff_rate,
            k.zone_swing_whiff, k.fpsr_fix, k.srfp, k.hard_hit_rate_fix,
            k.barrel_rate_g, k.battedball_profile, k.xcontact,
            k.pull_air_rate_fix, k.rc_rate)


def kpi_master(base, lv, jc, w, assign_year=None):
    """One master frame: nresults + the full KPI battery merged at `lv`."""
    src = jc if assign_year is None else jc.assign(game_year=assign_year)
    z = k.nresults_unrounded(lv, src, w)
    for f in KPI_FUNS:
        part = f(lv, jc)
        dupes = [c for c in part.columns if c in z.columns and c not in lv]
        z = z.merge(part.drop(columns=dupes), on=lv, how='left')
    # ba_risp — the DPO operator: nresults on the RISP-state frame, ba only
    risp = k.nresults_unrounded(lv, k.risp_rows(src), w)[
        lv + ['plate_apps', 'at_bats', 'hits', 'ba', 'slg', 'woba']].rename(
        columns={'plate_apps': 'risp_pa', 'at_bats': 'risp_ab',
                 'hits': 'risp_hits', 'ba': 'ba_risp', 'slg': 'slg_risp',
                 'woba': 'woba_risp'})
    z = z.merge(risp, on=lv, how='left')
    # governed inds means (O-3-exposed variant, shipped for reconciliation)
    iz = k.inds_unrounded(lv, jc)[lv + ['ev_mu', 'la_mu']].rename(
        columns={'ev_mu': 'ev_mu_inds_allrows', 'la_mu': 'la_mu_inds_allrows'})
    z = z.merge(iz, on=lv, how='left')
    return z


def main():
    pos, pps = k.load_frames()
    w = k.woba_weights()
    ab = pos[pos.batter == k.SUBJECT_MLBAM].copy()
    assert ab.player_name.nunique() == 1 and ab.player_name.iat[0] == k.SUBJECT
    assert (ab.stand == 'R').all()
    b26 = ab[ab.game_year == 2026].copy()
    b26['window'] = np.where(b26.game_date > k.BREAK, 'post_break', 'pre_break')

    # coordinate-convention assertion (uc-pps-025 rule): RHB pulled GROUND
    # BALLS must sit on the negative-loc_x (LF) side under the derivation.
    _bip = k.derive_loc(b26[b26.type == 'X'])
    _bip = _bip.assign(hit_direction=k.hit_direction(_bip))
    med_pull_gb_x = float(_bip[(_bip.hit_direction == 'Pull')
                               & (_bip.bb_type == 'ground_ball')].loc_x.median())
    assert med_pull_gb_x < 0, 'coordinate convention violated: +x must be RF side'
    H['coord_assert_median_pull_gb_loc_x_ft'] = round(med_pull_gb_x, 1)
    H['unclassified_bip'] = int((_bip.hit_direction == 'not grouped').sum())

    H['as_of'] = str(b26.game_date.max().date())
    H['games'] = int(b26.game_pk.nunique())
    H['pitch_rows'] = int(len(b26))
    H['break_operator'] = "post = game_date > '2026-07-15' (DPO-submitted)"
    H['last_pre_game'] = str(b26[b26.window == 'pre_break'].game_date.max().date())
    H['first_post_game'] = str(b26[b26.window == 'post_break'].game_date.min().date())

    # ── L1 season + career by year ───────────────────────────────────────
    season = kpi_master(ab, ['game_year'], b26, w)
    season26 = season.iloc[0]
    career = kpi_master(ab, ['game_year'], ab, w)
    career['below_pa_floor'] = career.plate_apps < k.PA_FLOOR
    career.to_csv(f'{OUT}/dp_uc37_career_by_year.csv', index=False)
    H['career'] = R3(career[['game_year', 'plate_apps', 'ba', 'obp', 'slg', 'woba',
                             'krate', 'whiff_rate', 'whiff_rate_in_zone',
                             'chase_rate', 'swing_rate_in_zone', 'hard_hit_rate',
                             'barrel_rate', 'pull_air_rate', 'mean_la', 'mean_ev',
                             'ba_risp', 'rc_per_pa']]).to_dict('records')
    H['season'] = {c: (float(season26[c]) if isinstance(season26[c], (float, np.floating))
                       else int(season26[c])) for c in
                   ['plate_apps', 'at_bats', 'hits', 'walks', 'strikeouts', 'hrs',
                    'ba', 'obp', 'slg', 'ops', 'iso', 'woba', 'krate', 'bbrate',
                    'babip', 'ba_risp', 'risp_pa', 'runs_created', 'rc_per_pa',
                    'pull_air_rate', 'hard_hit_rate', 'barrel_rate',
                    'whiff_rate', 'chase_rate', 'swing_rate_in_zone',
                    'whiff_rate_in_zone']}

    # ── L2 window split — THE headline contrast ──────────────────────────
    zw = kpi_master(ab, ['window'], b26, w, assign_year=2026)
    zw['below_pa_floor'] = zw.plate_apps < k.PA_FLOOR
    assert zw.plate_apps.sum() == season26.plate_apps, 'PA leak across windows'
    zw.to_csv(f'{OUT}/dp_uc37_window_split.csv', index=False)
    WCOLS = ['plate_apps', 'ba', 'obp', 'slg', 'ops', 'iso', 'woba', 'babip',
             'krate', 'bbrate', 'hrs', 'doubles', 'ba_risp', 'risp_pa', 'risp_ab',
             'slg_risp', 'woba_risp', 'runs_created', 'rc_per_pa',
             'hard_hit_rate', 'barrel_rate', 'pull_air_rate', 'pull_rate',
             'mean_la', 'mean_ev', 'ev_mu_inds_allrows', 'la_mu_inds_allrows',
             'gb_rate', 'fb_rate', 'ld_rate', 'pu_rate', 'xwobacon_bip', 'xba_bip',
             'swing_rate', 'chase_rate', 'whiff_rate', 'swing_rate_in_zone',
             'whiff_rate_in_zone', 'ooz_whiff_rate', 'srfp',
             'fpsr', 'in_zone_rate', 'bips', 'tracked_bips']
    pre = zw[zw.window == 'pre_break'].iloc[0]
    post = zw[zw.window == 'post_break'].iloc[0]
    def _row(r):
        # 6dp: enough precision that every display surface (report 3dp,
        # dashboard 1dp-of-percent) rounds identically from the stored value
        return {c: (round(float(r[c]), 6) if isinstance(r[c], (float, np.floating))
                    else int(r[c])) for c in WCOLS}
    H['window'] = {'break': k.BREAK, 'pre': _row(pre), 'post': _row(post)}

    # ── breakpoint sensitivity scan (RC-5 standing requirement) ──────────
    scan = []
    for d in ['2026-05-01', '2026-05-15', '2026-06-01', '2026-06-15',
              '2026-07-01', '2026-07-08', '2026-07-16', '2026-07-17',
              '2026-08-01', '2026-08-08']:
        a, b = b26[b26.game_date < d], b26[b26.game_date >= d]
        ra = k.nresults_unrounded(['game_year'], a, w)
        rb = k.nresults_unrounded(['game_year'], b, w)
        scan.append({'breakpoint': d,
                     'pre_pa': int(ra.plate_apps.iat[0]), 'post_pa': int(rb.plate_apps.iat[0]),
                     'pre_slg': float(ra.slg.iat[0]), 'post_slg': float(rb.slg.iat[0]),
                     'pre_woba': float(ra.woba.iat[0]), 'post_woba': float(rb.woba.iat[0]),
                     'delta_slg': float(rb.slg.iat[0] - ra.slg.iat[0]),
                     'delta_woba': float(rb.woba.iat[0] - ra.woba.iat[0])})
    scan = pd.DataFrame(scan)
    scan.to_csv(f'{OUT}/dp_uc37_breakpoint_scan.csv', index=False)
    H['breakpoint_scan'] = scan.round(4).to_dict('records')

    # ── L2b monthly master ───────────────────────────────────────────────
    z = kpi_master(ab, ['month'], b26, w, assign_year=2026)
    z['below_pa_floor'] = z.plate_apps < k.PA_FLOOR
    z['month_is_partial'] = z.month == b26.game_date.max().month
    assert len(z) == b26.month.nunique(), 'fan-out in monthly master'
    assert z.plate_apps.sum() == season26.plate_apps, 'PA leak in monthly master'
    z.to_csv(f'{OUT}/dp_uc37_monthly_master.csv', index=False)
    panel = R3(z[['month', 'plate_apps', 'ba', 'slg', 'woba', 'babip', 'ba_risp',
                  'risp_pa', 'rc_per_pa', 'krate', 'whiff_rate', 'chase_rate',
                  'swing_rate_in_zone', 'whiff_rate_in_zone', 'hard_hit_rate',
                  'barrel_rate', 'pull_air_rate', 'mean_la', 'mean_ev',
                  'below_pa_floor', 'month_is_partial']])
    panel.to_csv(f'{OUT}/dp_uc37_monthly_panel.csv', index=False)
    H['monthly_woba'] = {int(r.month): round(float(r.woba), 3) for r in z.itertuples()}
    H['monthly_slg'] = {int(r.month): round(float(r.slg), 3) for r in z.itertuples()}
    H['monthly_pa'] = {int(r.month): int(r.plate_apps) for r in z.itertuples()}
    H['months_below_floor'] = [int(m) for m in z[z.below_pa_floor].month]

    # ── L3 career trajectory ghost lines ─────────────────────────────────
    rl = k.running_line_pa(ab, w, group='game_year')
    rl.to_csv(f'{OUT}/dp_uc37_running_line.csv', index=False)
    pa26 = k.pa_rows(b26)
    H['break_cum_pa'] = int(len(pa26[pa26.game_date <= k.BREAK]))

    # ── platoon ──────────────────────────────────────────────────────────
    plat = kpi_master(ab, ['window', 'p_throws'], b26, w, assign_year=2026)
    plat['below_pa_floor'] = plat.plate_apps < k.PA_FLOOR
    plat.to_csv(f'{OUT}/dp_uc37_platoon_splits.csv', index=False)
    H['platoon_splits'] = R3(plat[['window', 'p_throws', 'plate_apps', 'ba', 'obp',
                                   'slg', 'woba', 'krate', 'whiff_rate',
                                   'hard_hit_rate', 'below_pa_floor']]).to_dict('records')
    cfx = k.platoon_counterfactual(b26, w, 'window', 'pre_break', 'post_break')
    cfx.to_csv(f'{OUT}/dp_uc37_platoon_counterfactual.csv', index=False)
    H['platoon_counterfactual'] = cfx.round(4).to_dict('records')
    H['lhp_share_pre'] = round(float((k.pa_rows(b26[b26.window == 'pre_break'])
                                      .p_throws == 'L').mean()), 4)
    H['lhp_share_post'] = round(float((k.pa_rows(b26[b26.window == 'post_break'])
                                       .p_throws == 'L').mean()), 4)

    # ── pitch group / type ───────────────────────────────────────────────
    pg = k.nresults_unrounded(['window', 'pitch_group'],
                              b26.assign(game_year=2026), w)
    for f in (k.swing_rate, k.chase_rate_g, k.whiff_rate_fix, k.zone_swing_whiff,
              k.hard_hit_rate_fix):
        part = f(['window', 'pitch_group'], b26)
        dupes = [c for c in part.columns
                 if c in pg.columns and c not in ('window', 'pitch_group')]
        pg = pg.merge(part.drop(columns=dupes), on=['window', 'pitch_group'], how='left')
    pg['below_pa_floor'] = pg.plate_apps < k.PA_FLOOR
    pg.to_csv(f'{OUT}/dp_uc37_pitch_group_window.csv', index=False)
    H['pitch_group_window'] = R3(pg[['window', 'pitch_group', 'pitches', 'plate_apps',
                                     'ba', 'slg', 'woba', 'krate', 'whiff_rate',
                                     'chase_rate', 'whiff_rate_in_zone',
                                     'hard_hit_rate', 'below_pa_floor']]).to_dict('records')

    pt = k.nresults_unrounded(['game_year', 'pitch_type'], b26, w)
    ptd = k.whiff_rate_fix(['pitch_type'], b26)[['pitch_type', 'swings', 'whiff_rate']]
    ptc = k.chase_rate_g(['pitch_type'], b26)[['pitch_type', 'chase_rate', 'pitches']]
    pt = pt.drop(columns=['pitches']).merge(ptd, on='pitch_type').merge(ptc, on='pitch_type')
    pt = pt[pt.pitches >= 40].sort_values('pitches', ascending=False)
    pt.to_csv(f'{OUT}/dp_uc37_pitch_type_season.csv', index=False)
    H['pitch_type'] = R3(pt[['pitch_type', 'pitches', 'plate_apps', 'ba', 'slg',
                             'woba', 'krate', 'whiff_rate', 'chase_rate']]).to_dict('records')

    # ── pull-air detail (the DPO's past digging, now governed) ───────────
    bip = k.derive_loc(b26[b26.type == 'X'])
    bip = bip.assign(hit_direction=k.hit_direction(bip),
                     is_air=bip.bb_type != 'ground_ball')
    dirs = (bip.groupby(['window', 'hit_direction', 'is_air'], as_index=False)
            .agg(bips=('des', 'size'),
                 hits=('events', lambda s: int(s.isin(k.HIT_EV).sum())),
                 hrs=('events', lambda s: int((s == 'home_run').sum())),
                 mean_ev=('launch_speed', 'mean'),
                 xwobacon=('estimated_woba_using_speedangle', 'mean')))
    tot_w = bip.groupby('window', as_index=False).agg(window_bips=('des', 'size'))
    dirs = dirs.merge(tot_w, on='window')
    dirs['share_of_bip'] = dirs.bips / dirs.window_bips
    dirs.to_csv(f'{OUT}/dp_uc37_direction_air_matrix.csv', index=False)
    H['direction_air'] = R3(dirs).to_dict('records')
    pa_evq = (bip[(bip.hit_direction == 'Pull') & bip.is_air]
              .groupby('window', as_index=False)
              .agg(pull_airs=('des', 'size'),
                   pa_hits=('events', lambda s: int(s.isin(k.HIT_EV).sum())),
                   pa_hrs=('events', lambda s: int((s == 'home_run').sum())),
                   pa_mean_ev=('launch_speed', 'mean'),
                   pa_mean_dist=('hit_distance_sc', 'mean')))
    pa_evq.to_csv(f'{OUT}/dp_uc37_pull_air_quality.csv', index=False)
    H['pull_air_quality'] = R3(pa_evq).to_dict('records')

    # ── population benchmark: Phillies hitter-seasons >= 50 PA, 2015- ────
    bp = k.nresults_unrounded(['player_name', 'game_year'], pos, w)
    bp = bp[bp.plate_apps >= k.PA_FLOOR]
    d1 = k.swing_rate(['player_name', 'game_year'], pos)
    d2 = k.whiff_rate_fix(['player_name', 'game_year'], pos)[
        ['player_name', 'game_year', 'whiff_rate']]
    d3 = k.chase_rate_g(['player_name', 'game_year'], pos)[
        ['player_name', 'game_year', 'chase_rate']]
    d4 = k.battedball_profile(['player_name', 'game_year'], pos)[
        ['player_name', 'game_year', 'bips', 'tracked_bips', 'gb_rate',
         'fb_rate', 'ld_rate', 'mean_la', 'mean_ev']]
    d5 = k.hard_hit_rate_fix(['player_name', 'game_year'], pos)[
        ['player_name', 'game_year', 'hard_hit_rate']]
    d6 = k.barrel_rate_g(['player_name', 'game_year'], pos)[
        ['player_name', 'game_year', 'barrel_rate']]
    d7 = k.pull_air_rate_fix(['player_name', 'game_year'], pos)[
        ['player_name', 'game_year', 'pull_air_rate']]
    d8 = k.zone_swing_whiff(['player_name', 'game_year'], pos)[
        ['player_name', 'game_year', 'swing_rate_in_zone', 'whiff_rate_in_zone']]
    pool = bp
    for dd in (d1.drop(columns=['pitches']), d2, d3, d4, d5, d6, d7, d8):
        pool = pool.merge(dd, on=['player_name', 'game_year'], how='left')
    pool.to_csv(f'{OUT}/dp_uc37_population_pool.csv', index=False)
    H['pool_n'] = int(len(pool)); H['pool_players'] = int(pool.player_name.nunique())

    me26 = pool[(pool.player_name == k.SUBJECT) & (pool.game_year == 2026)].iloc[0]
    prof = []
    for col, lbl in [('slg', 'SLG'), ('woba', 'wOBA'), ('iso', 'ISO'),
                     ('hard_hit_rate', 'Hard-Hit%'), ('barrel_rate', 'Barrel%'),
                     ('pull_air_rate', 'Pull-Air%'), ('mean_ev', 'Mean EV'),
                     ('mean_la', 'Mean LA'), ('whiff_rate', 'Whiff%'),
                     ('whiff_rate_in_zone', 'Z-Whiff%'), ('chase_rate', 'Chase%'),
                     ('swing_rate_in_zone', 'Z-Swing%'), ('krate', 'K%')]:
        s = pool[col].dropna()
        prof.append({'metric': lbl, 'column': col,
                     'bohm_2026': float(me26[col]),
                     'bohm_pre': float(pre[col]) if col in WCOLS else np.nan,
                     'bohm_post': float(post[col]) if col in WCOLS else np.nan,
                     'pool_median': float(s.median()), 'pool_n': int(len(s)),
                     'pct_2026': k.pool_percentile(pool, col, me26[col]),
                     'pct_post_window': (k.pool_percentile(pool, col, float(post[col]))
                                         if col in WCOLS else np.nan)})
    prof = pd.DataFrame(prof)
    prof.to_csv(f'{OUT}/dp_uc37_profile_percentiles.csv', index=False)
    H['profile'] = prof.round(3).to_dict('records')

    # ── inds reconciliation receipt (O-3 exposure quantified) ────────────
    rec = []
    for nm, d in [('pre_break', b26[b26.window == 'pre_break']),
                  ('post_break', b26[b26.window == 'post_break'])]:
        allrows = k.inds_unrounded(['window'], d).iloc[0]
        bipd = d[d.type == 'X']
        tr = bipd[bipd.launch_speed.notna() & bipd.launch_angle.notna()]
        fouls_tracked = int(d[(d.type != 'X') & d.launch_speed.notna()].shape[0])
        rec.append({'window': nm,
                    'ev_mu_inds_allrows': float(allrows.ev_mu),
                    'la_mu_inds_allrows': float(allrows.la_mu),
                    'mean_ev_tracked_bip': float(tr.launch_speed.mean()),
                    'mean_la_tracked_bip': float(tr.launch_angle.mean()),
                    'non_bip_rows_with_launch_speed': fouls_tracked,
                    'tracked_bip': int(len(tr)), 'all_bip': int(len(bipd))})
    rec = pd.DataFrame(rec)
    rec.to_csv(f'{OUT}/dp_uc37_inds_reconciliation.csv', index=False)
    H['inds_reconciliation'] = rec.round(3).to_dict('records')

    with open(f'{OUT}/dp_uc37_headlines.json', 'w') as fh:
        json.dump(H, fh, indent=2, default=str)

    figures(b26, z, zw, rl, plat, pg, scan, pool, me26, prof, career, cfx)
    print('receipts + figures written')
    return H


# ══════════════════════════════════════════════════════════════════════════
def figures(b26, z, zw, rl, plat, pg, scan, pool, me26, prof, career, cfx):
    pre = zw[zw.window == 'pre_break'].iloc[0]
    post = zw[zw.window == 'post_break'].iloc[0]
    MONTH_LBL = {3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep'}

    # FIG 1 — career ghost lines, cum SLG + cum wOBA, break marker on 2026
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.2))
    for ax, (col, title) in zip(axes, [('cum_slg', 'Slugging Percentage'),
                                       ('cum_woba', 'wOBA')]):
        for yr, g in rl.groupby('game_year'):
            g = g[g.cum_pa >= k.PA_FLOOR]
            if yr == 2026 or len(g) == 0:
                continue
            ax.plot(g.cum_pa, g[col], color=GREY, lw=1.1, zorder=1)
            ax.annotate(f"'{str(yr)[2:]}", xy=(g.cum_pa.iat[-1], g[col].iat[-1]),
                        fontsize=6, color='#7A828F', xytext=(3, 0),
                        textcoords='offset points', va='center')
        c = rl[rl.game_year == 2026]; c = c[c.cum_pa >= k.PA_FLOOR]
        ax.plot(c.cum_pa, c[col], color=RED, lw=2.4, zorder=3, label='2026')
        bp = c[c.cum_pa <= 377]
        ax.scatter([377], [c[c.cum_pa == 377][col].iat[0]], color=NAVY, s=30,
                   zorder=5, marker='D')
        ax.annotate('All-Star break\n(PA 377)', xy=(377, c[c.cum_pa == 377][col].iat[0]),
                    xytext=(-72, 14), textcoords='offset points', fontsize=6.6,
                    color=NAVY)
        ax.scatter([c.cum_pa.iat[-1]], [c[col].iat[-1]], color=RED, s=26, zorder=4)
        ax.set_title(title); ax.set_xlabel('cumulative plate appearances')
        ax.grid(alpha=.22, lw=.6)
    axes[0].set_ylabel('season-to-date'); axes[0].legend(loc='lower right',
                                                         fontsize=7, frameon=False)
    fig.suptitle('Alec Bohm 2026 vs his own six prior seasons — cumulative results by PA',
                 color=NAVY, fontweight='bold', y=1.02, fontsize=11.5)
    fig.text(0.5, -0.05, 'Grey = 2020–2025 self-referential ghost lines. Left tail '
             'below 50 PA suppressed. Navy diamond = the DPO break operator '
             '(post = games after 15 Jul).', ha='center', fontsize=7, color='#55606E')
    fig.savefig(f'{OUT}/dp_uc37_fig1_career_ghost.png'); plt.close(fig)

    # FIG 2 — monthly results + PA floor
    fig, ax = plt.subplots(figsize=(9.2, 3.9))
    ax2 = ax.twinx()
    ax2.bar(z.month, z.plate_apps, color='#E7EBF2', width=.62, zorder=0)
    ax2.set_ylabel('plate appearances', color='#8C93A0', fontsize=8)
    ax2.set_ylim(0, z.plate_apps.max() * 3.0)
    ax2.tick_params(labelsize=7, colors='#8C93A0')
    ax2.axhline(k.PA_FLOOR, color=GOLD, lw=1.0, ls='--')
    ax2.annotate('50-PA floor', xy=(z.month.min() - .05, k.PA_FLOOR), fontsize=6.4,
                 color=GOLD, va='bottom')
    for col, lbl, c, mk in [('ba', 'BA', NAVY, 'o'), ('slg', 'SLG', RED, 'D'),
                            ('woba', 'wOBA', GOLD, 's')]:
        ax.plot(z.month, z[col], marker=mk, color=c, lw=2.0, ms=5, label=lbl, zorder=3)
    for m in z[z.below_pa_floor].month:
        ax.axvspan(m - .42, m + .42, color='#FBF3E0', zorder=-1)
    ax.axvline(7.5, color=NAVY, lw=1.1, ls=':')
    ax.annotate('All-Star break', xy=(7.52, .62), fontsize=6.8, color=NAVY)
    ax.set_xticks(z.month); ax.set_xticklabels([MONTH_LBL[m] for m in z.month])
    ax.set_ylabel('rate'); ax.set_ylim(.10, .68); ax.grid(alpha=.22, lw=.6)
    ax.legend(loc='upper left', fontsize=8, frameon=False, ncol=3)
    ax.set_title('Monthly results — where the surge actually lives\n'
                 'shaded months are below the 50-PA reliability floor', loc='left')
    ax.set_zorder(ax2.get_zorder() + 1); ax.patch.set_visible(False)
    fig.savefig(f'{OUT}/dp_uc37_fig2_monthly.png'); plt.close(fig)

    # FIG 3 — pre/post mechanism arrows: results left, process right
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.3))
    left = [('slg', 'SLG'), ('woba', 'wOBA'), ('ba', 'BA'), ('ba_risp', 'BA w/ RISP'),
            ('iso', 'ISO'), ('babip', 'BABIP'), ('xwobacon_bip', 'xwOBAcon'),
            ('rc_per_pa', 'RC / PA')]
    right = [('hard_hit_rate', 'Hard-Hit%'), ('barrel_rate', 'Barrel%'),
             ('pull_air_rate', 'Pull-Air%'), ('gb_rate', 'GB%'),
             ('whiff_rate', 'Whiff%'), ('whiff_rate_in_zone', 'Z-Whiff%'),
             ('chase_rate', 'Chase%'), ('swing_rate_in_zone', 'Z-Swing%'),
             ('krate', 'K%')]
    for ax, items, ttl in [(axes[0], left, 'Results — before vs after the break'),
                           (axes[1], right, 'Process — contact quality & decisions')]:
        ypos = np.arange(len(items))[::-1]
        for y, (col, lbl) in zip(ypos, items):
            a, b = float(pre[col]), float(post[col])
            ax.annotate('', xy=(b, y), xytext=(a, y),
                        arrowprops=dict(arrowstyle='-|>', lw=1.7,
                                        color=RED if b > a else NAVY, alpha=.85))
            ax.scatter([a], [y], color='#9AA3B0', s=26, zorder=3)
            ax.scatter([b], [y], color=RED if b > a else NAVY, s=34, zorder=3)
            ax.annotate(f'{a:.3f} → {b:.3f}', xy=(max(a, b), y), xytext=(7, 0),
                        textcoords='offset points', fontsize=6.8, va='center',
                        color='#40484F')
        ax.set_yticks(ypos); ax.set_yticklabels([l for _, l in items], fontsize=8.5)
        ax.set_xlim(0, .72); ax.grid(axis='x', alpha=.22, lw=.6)
        ax.set_title(ttl, loc='left'); ax.set_xlabel('rate')
    fig.text(0.5, -0.04, 'Grey dot = pre-break (377 PA) · colored dot = post-break '
             '(135 PA). Red = increase, navy = decrease.',
             ha='center', fontsize=7, color='#55606E')
    fig.savefig(f'{OUT}/dp_uc37_fig3_mechanism.png'); plt.close(fig)

    # FIG 4 — contact quality: monthly EV/hard-hit/barrel/pull-air + career pull-air
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 3.9))
    ax = axes[0]
    for col, lbl, c, mk in [('hard_hit_rate', 'Hard-Hit%', NAVY, 'o'),
                            ('pull_air_rate', 'Pull-Air%', RED, 'D'),
                            ('barrel_rate', 'Barrel%', GOLD, 's')]:
        ax.plot(z.month, z[col], marker=mk, color=c, lw=2.0, ms=5, label=lbl)
    ax.axvline(7.5, color=NAVY, lw=1.1, ls=':')
    ax.set_xticks(z.month); ax.set_xticklabels([MONTH_LBL[m] for m in z.month])
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylim(0, .62); ax.grid(alpha=.22, lw=.6)
    ax.legend(fontsize=7.5, frameon=False, ncol=3)
    ax2 = ax.twinx()
    ax2.plot(z.month, z.mean_ev, color='#7C8798', lw=1.4, ls='--', marker='.')
    ax2.set_ylabel('mean EV, tracked BIP (mph)', color='#7C8798', fontsize=7.5)
    ax2.tick_params(colors='#7C8798', labelsize=7)
    ax.set_title('Contact quality by month — dotted line = All-Star break', loc='left')
    ax = axes[1]
    cr = career.copy()
    ax.bar(cr.game_year - .19, cr.pull_air_rate, .36, color=RED, label='Pull-Air%')
    ax.bar(cr.game_year + .19, cr.barrel_rate, .36, color=NAVY, label='Barrel%')
    for r in cr.itertuples():
        ax.annotate(f'{r.pull_air_rate:.1%}', xy=(r.game_year - .19, r.pull_air_rate),
                    ha='center', xytext=(0, 2), textcoords='offset points',
                    fontsize=6.0, color=RED)
    ax.set_xticks(cr.game_year); ax.set_xticklabels(cr.game_year, fontsize=8)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylim(0, .30); ax.grid(axis='y', alpha=.22, lw=.6)
    ax.legend(fontsize=7.5, frameon=False)
    ax.set_title('Career pull-air & barrel — the 2026 profile in context', loc='left')
    fig.savefig(f'{OUT}/dp_uc37_fig4_contact.png'); plt.close(fig)

    # FIG 5 — platoon
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 3.7))
    order = [('pre_break', 'L'), ('pre_break', 'R'),
             ('post_break', 'L'), ('post_break', 'R')]
    lbls = ['pre vs LHP', 'pre vs RHP', 'post vs LHP', 'post vs RHP']
    for ax, col, ttl in [(axes[0], 'slg', 'SLG by window × handedness'),
                         (axes[1], 'woba', 'wOBA by window × handedness')]:
        vals, ns, colors = [], [], []
        for wname, t in order:
            r = plat[(plat.window == wname) & (plat.p_throws == t)].iloc[0]
            vals.append(float(r[col])); ns.append(int(r.plate_apps))
            colors.append(RED if wname == 'post_break' else '#9AA3B0')
        x = np.arange(4)
        ax.bar(x, vals, .58, color=colors)
        for i, (v, n) in enumerate(zip(vals, ns)):
            flag = ' ⚠' if n < k.PA_FLOOR else ''
            ax.annotate(f'{v:.3f}\n{n} PA{flag}', xy=(i, v), ha='center',
                        xytext=(0, 3), textcoords='offset points', fontsize=6.6,
                        color='#40484F')
        ax.set_xticks(x); ax.set_xticklabels(lbls, fontsize=7.6)
        ax.set_ylim(0, max(vals) * 1.3); ax.grid(axis='y', alpha=.22, lw=.6)
        ax.set_title(ttl, loc='left')
    fig.text(0.5, -0.04, '⚠ = below the 50-PA floor; no ranking may lean on that '
             'cell. Mix effect from direct standardisation (PL-1): '
             + ', '.join(f"{r.metric} {r.mix_effect:+.4f}" for r in cfx.itertuples()),
             ha='center', fontsize=7, color='#55606E')
    fig.savefig(f'{OUT}/dp_uc37_fig5_platoon.png'); plt.close(fig)

    # FIG 6 — pitch group
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 3.8))
    order = ['fastball', 'breaking', 'offspeed']
    p = pg.pivot_table(index='pitch_group', columns='window', values='slg').reindex(order)
    n = pg.pivot_table(index='pitch_group', columns='window', values='plate_apps').reindex(order)
    x = np.arange(len(order))
    ax = axes[0]
    ax.bar(x - .19, p['pre_break'], .36, color='#9AA3B0', label='pre-break')
    ax.bar(x + .19, p['post_break'], .36, color=RED, label='post-break')
    for i in x:
        na, nb = int(n['pre_break'].iloc[i]), int(n['post_break'].iloc[i])
        ax.annotate(f'{na} PA', xy=(i - .19, p['pre_break'].iloc[i]), ha='center',
                    xytext=(0, 2), textcoords='offset points', fontsize=6.2, color='#55606E')
        ax.annotate(f'{nb} PA' + (' ⚠' if nb < k.PA_FLOOR else ''),
                    xy=(i + .19, p['post_break'].iloc[i]), ha='center',
                    xytext=(0, 2), textcoords='offset points', fontsize=6.2, color=RED)
    ax.set_xticks(x); ax.set_xticklabels([o.title() for o in order])
    ax.set_ylabel('SLG'); ax.grid(axis='y', alpha=.22, lw=.6)
    ax.legend(fontsize=7.5, frameon=False)
    ax.set_title('SLG by pitch group — where the damage comes from', loc='left')
    ax = axes[1]
    c = pg.pivot_table(index='pitch_group', columns='window', values='whiff_rate').reindex(order)
    ax.bar(x - .19, c['pre_break'], .36, color='#9AA3B0', label='pre-break')
    ax.bar(x + .19, c['post_break'], .36, color=NAVY, label='post-break')
    ax.set_xticks(x); ax.set_xticklabels([o.title() for o in order])
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel('whiff rate'); ax.grid(axis='y', alpha=.22, lw=.6)
    ax.legend(fontsize=7.5, frameon=False)
    ax.set_title('Whiff rate by pitch group', loc='left')
    fig.savefig(f'{OUT}/dp_uc37_fig6_pitch_group.png'); plt.close(fig)


if __name__ == '__main__':
    main()
