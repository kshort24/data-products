"""
dp_uc34_crawford_ytd.py — build script for uc-pos-011-crawford-ytd-001.
Produces every CSV/JSON receipt and every figure quoted in the report.
Run from this directory.
"""
from __future__ import annotations
import json, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import dp_uc34_kernel as k

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY, RED, GREY, GOLD = '#002D72', '#E81828', '#B8BFCB', '#C4A24A'
plt.rcParams.update({'figure.dpi': 150, 'font.size': 9,
                     'axes.edgecolor': '#55606E', 'axes.labelcolor': '#1a1a1a',
                     'axes.titlesize': 10.5, 'axes.titleweight': 'bold',
                     'axes.titlecolor': NAVY, 'savefig.bbox': 'tight'})
R3 = lambda d: d.round(3)
H = {}


def main():
    pos, pps = k.load_frames()
    w = k.woba_weights()
    jc = pos[pos.batter == k.SUBJECT_MLBAM].copy()
    assert jc.player_name.nunique() == 1 and jc.player_name.iat[0] == k.SUBJECT
    jc['window'] = np.where(jc.game_date < k.BREAK, 'pre_0615', 'post_0615')
    jc['hill_window'] = np.where(jc.game_date < k.HILL_DEBUT, 'pre_hill', 'post_hill')
    jc['count_state'] = np.select([jc.strikes == 2, jc.balls > jc.strikes],
                                  ['two_strike', 'ahead'], default='even_or_behind')
    H['as_of'] = str(jc.game_date.max().date())
    H['games'] = int(jc.game_pk.nunique())
    H['pitch_rows'] = int(len(jc))

    # ── L1 season ────────────────────────────────────────────────────────
    season = k.nresults_unrounded(['game_year'], jc, w)
    H['season'] = {c: (float(season[c].iat[0]) if season[c].dtype.kind == 'f'
                       else int(season[c].iat[0])) for c in
                   ['plate_apps', 'at_bats', 'hits', 'walks', 'strikeouts', 'hrs',
                    'ba', 'obp', 'slg', 'ops', 'iso', 'woba', 'krate', 'bbrate', 'babip']}

    # ── L2 monthly master ────────────────────────────────────────────────
    lv = ['game_year', 'month']
    z = k.nresults_unrounded(lv, jc, w)
    for f in (k.swing_rate, k.chase_rate_g, k.whiff_rate_fix, k.ooz_whiff_rate,
              k.fpsr_fix, k.srfp, k.hard_hit_rate_fix, k.barrel_rate_g,
              k.battedball_profile, k.xcontact):
        part = f(['month'], jc)
        dupes = [c for c in part.columns if c in z.columns and c != 'month']
        z = z.merge(part.drop(columns=dupes), on='month', how='left')
    z['below_pa_floor'] = z.plate_apps < k.PA_FLOOR
    z['month_is_partial'] = z.month == jc.game_date.max().month
    assert len(z) == jc.month.nunique(), 'fan-out in monthly master'
    assert z.plate_apps.sum() == season.plate_apps.iat[0], 'PA leak'
    z.to_csv(f'{OUT}/dp_uc34_monthly_master.csv', index=False)
    panel = R3(z[['month', 'plate_apps', 'ba', 'obp', 'slg', 'iso', 'woba', 'babip',
                  'krate', 'bbrate', 'swing_rate', 'chase_rate', 'whiff_rate',
                  'gb_rate', 'mean_la', 'hard_hit_rate', 'xwobacon_bip',
                  'in_zone_rate', 'fpsr', 'below_pa_floor', 'month_is_partial']])
    panel.to_csv(f'{OUT}/dp_uc34_monthly_panel.csv', index=False)
    H['monthly_woba'] = {int(r.month): round(float(r.woba), 3) for r in z.itertuples()}
    H['monthly_pa'] = {int(r.month): int(r.plate_apps) for r in z.itertuples()}
    H['months_below_floor'] = [int(m) for m in z[z.below_pa_floor].month]

    # ── L2b window split (DPO narrative breakpoint) ──────────────────────
    lvw = ['window']
    zw = k.nresults_unrounded(lvw, jc.assign(game_year=2026), w)
    for f in (k.swing_rate, k.chase_rate_g, k.whiff_rate_fix, k.ooz_whiff_rate,
              k.fpsr_fix, k.srfp, k.hard_hit_rate_fix, k.barrel_rate_g,
              k.battedball_profile, k.xcontact):
        part = f(lvw, jc)
        dupes = [c for c in part.columns if c in zw.columns and c != 'window']
        zw = zw.merge(part.drop(columns=dupes), on='window', how='left')
    zw.to_csv(f'{OUT}/dp_uc34_window_split.csv', index=False)
    pre = zw[zw.window == 'pre_0615'].iloc[0]; post = zw[zw.window == 'post_0615'].iloc[0]
    H['window'] = {'break': k.BREAK,
                   'pre': {c: (round(float(pre[c]), 4) if isinstance(pre[c], (float, np.floating)) else int(pre[c]))
                           for c in ['plate_apps', 'ba', 'obp', 'slg', 'iso', 'woba', 'babip',
                                     'krate', 'bbrate', 'gb_rate', 'mean_la', 'hard_hit_rate',
                                     'xwobacon_bip', 'chase_rate', 'whiff_rate', 'swing_rate', 'hrs']},
                   'post': {c: (round(float(post[c]), 4) if isinstance(post[c], (float, np.floating)) else int(post[c]))
                            for c in ['plate_apps', 'ba', 'obp', 'slg', 'iso', 'woba', 'babip',
                                      'krate', 'bbrate', 'gb_rate', 'mean_la', 'hard_hit_rate',
                                      'xwobacon_bip', 'chase_rate', 'whiff_rate', 'swing_rate', 'hrs']}}

    # ── breakpoint sensitivity scan (RC-5) ───────────────────────────────
    scan = []
    for d in ['2026-05-01', '2026-05-15', '2026-06-01', '2026-06-08', k.BREAK,
              '2026-06-22', '2026-07-01', '2026-07-15', '2026-08-01']:
        a, b = jc[jc.game_date < d], jc[jc.game_date >= d]
        ra = k.nresults_unrounded(['game_year'], a, w)
        rb = k.nresults_unrounded(['game_year'], b, w)
        scan.append({'breakpoint': d, 'pre_pa': int(ra.plate_apps.iat[0]),
                     'pre_woba': float(ra.woba.iat[0]), 'post_pa': int(rb.plate_apps.iat[0]),
                     'post_woba': float(rb.woba.iat[0]),
                     'delta_woba': float(rb.woba.iat[0] - ra.woba.iat[0])})
    scan = pd.DataFrame(scan)
    scan.to_csv(f'{OUT}/dp_uc34_breakpoint_scan.csv', index=False)
    H['breakpoint_scan'] = scan.round(4).to_dict('records')

    # ── L3 rolling / cumulative ──────────────────────────────────────────
    rl = k.running_line_pa(jc, w, group='game_year')
    rl.to_csv(f'{OUT}/dp_uc34_rolling_line.csv', index=False)

    # ── CX context: Phillies CF, Statcast era ────────────────────────────
    cntxt, pool_cf = k.cf_context_pool(pos, pps)
    cntxt['season_key'] = (cntxt.player_name.str.split(',').str[0] + ' '
                           + cntxt.game_year.astype(str))
    cf_seasons = k.nresults_unrounded(['player_name', 'game_year'], cntxt, w)
    cf_seasons = cf_seasons.merge(pool_cf[['player_name', 'game_year', 'uq_cf_games']],
                                  on=['player_name', 'game_year'])
    cf_seasons.sort_values('game_year').to_csv(f'{OUT}/dp_uc34_cf_context_pool.csv', index=False)
    H['cf_pool_seasons'] = int(len(cf_seasons))
    H['cf_pool'] = R3(cf_seasons[['player_name', 'game_year', 'uq_cf_games',
                                  'plate_apps', 'ba', 'obp', 'woba', 'bbrate']]
                      ).sort_values('game_year').to_dict('records')
    cf_rl = k.running_line_pa(cntxt, w, group='season_key')
    cf_rl.to_csv(f'{OUT}/dp_uc34_cf_context_rolling.csv', index=False)
    jc_pa_ctx = int(cf_rl[cf_rl.season_key == 'Crawford 2026'].cum_pa.max())
    H['crawford_ctx_pa'] = jc_pa_ctx
    snap = (cf_rl[cf_rl.cum_pa == jc_pa_ctx]
            .sort_values('cum_woba', ascending=False).reset_index(drop=True))
    snap['woba_rank'] = snap.index + 1
    snap.to_csv(f'{OUT}/dp_uc34_cf_matched_pa_snapshot.csv', index=False)
    H['matched_pa_snapshot'] = R3(snap[['season_key', 'cum_pa', 'cum_ba',
                                        'cum_obp', 'cum_woba', 'woba_rank']]).to_dict('records')
    H['crawford_woba_rank'] = int(snap[snap.season_key == 'Crawford 2026'].woba_rank.iat[0])
    H['cf_pool_n'] = int(len(snap))

    # ── population benchmark: Phillies hitter-seasons >= 50 PA ───────────
    bp = k.nresults_unrounded(['player_name', 'game_year'], pos, w)
    bp = bp[bp.plate_apps >= k.PA_FLOOR]
    d1 = k.swing_rate(['player_name', 'game_year'], pos)
    d2 = k.whiff_rate_fix(['player_name', 'game_year'], pos)[['player_name', 'game_year', 'whiff_rate']]
    d3 = k.chase_rate_g(['player_name', 'game_year'], pos)[['player_name', 'game_year', 'chase_rate']]
    d4 = k.battedball_profile(['player_name', 'game_year'], pos)[
        ['player_name', 'game_year', 'bips', 'tracked_bips', 'gb_rate', 'fb_rate',
         'ld_rate', 'mean_la', 'mean_ev']]
    pool = (bp.merge(d1.drop(columns=['pitches']), on=['player_name', 'game_year'])
              .merge(d2, on=['player_name', 'game_year'])
              .merge(d3, on=['player_name', 'game_year'])
              .merge(d4, on=['player_name', 'game_year']))
    pool.to_csv(f'{OUT}/dp_uc34_population_pool.csv', index=False)
    me = pool[pool.player_name == k.SUBJECT].iloc[0]
    prof = []
    for col, lbl in [('swing_rate', 'Swing Rate'), ('chase_rate', 'Chase Rate'),
                     ('whiff_rate', 'Whiff Rate'), ('gb_rate', 'Ground-Ball Rate'),
                     ('mean_la', 'Mean Launch Angle'), ('ba', 'BA'), ('obp', 'OBP'),
                     ('woba', 'wOBA'), ('iso', 'ISO'), ('krate', 'K%'), ('bbrate', 'BB%'),
                     ('babip', 'BABIP')]:
        s = pool[col].dropna()
        prof.append({'metric': lbl, 'column': col, 'crawford': float(me[col]),
                     'pool_median': float(s.median()), 'pool_n': int(len(s)),
                     'percentile': k.pool_percentile(pool, col, me[col])})
    prof = pd.DataFrame(prof)
    prof.to_csv(f'{OUT}/dp_uc34_profile_percentiles.csv', index=False)
    H['pool_n'] = int(len(pool)); H['pool_players'] = int(pool.player_name.nunique())
    H['profile'] = prof.round(3).to_dict('records')
    arche = pool.nsmallest(10, 'mean_la')[['player_name', 'game_year', 'plate_apps',
                                           'mean_la', 'gb_rate', 'ba', 'iso', 'woba']]
    arche.to_csv(f'{OUT}/dp_uc34_archetype_cohort.csv', index=False)
    H['archetype'] = R3(arche).to_dict('records')

    # ── platoon ──────────────────────────────────────────────────────────
    pa = k.pa_rows(jc).copy()
    pa['halfmonth'] = (pa.game_date.dt.strftime('%Y-%m')
                       + np.where(pa.game_date.dt.day <= 15, 'a', 'b'))
    hm = pa.groupby(['halfmonth', 'p_throws']).size().unstack(fill_value=0)
    for c in ('L', 'R'):
        if c not in hm.columns: hm[c] = 0
    hm['pa'] = hm.L + hm.R; hm['lhp_share'] = hm.L / hm.pa
    hm = hm.reset_index()
    hm.to_csv(f'{OUT}/dp_uc34_platoon_exposure.csv', index=False)
    H['lhp_share_halfmonth'] = R3(hm[['halfmonth', 'L', 'R', 'pa', 'lhp_share']]).to_dict('records')

    plat = k.nresults_unrounded(['hill_window', 'p_throws'], jc.assign(game_year=2026), w)
    plat.to_csv(f'{OUT}/dp_uc34_platoon_splits.csv', index=False)
    H['platoon_splits'] = R3(plat[['hill_window', 'p_throws', 'plate_apps', 'ba',
                                   'obp', 'slg', 'woba', 'krate', 'bbrate']]).to_dict('records')
    cfx = k.platoon_counterfactual(jc, w, 'hill_window', 'pre_hill', 'post_hill')
    cfx.to_csv(f'{OUT}/dp_uc34_platoon_counterfactual.csv', index=False)
    H['platoon_counterfactual'] = cfx.round(4).to_dict('records')
    H['hill_debut'] = k.HILL_DEBUT
    H['lhp_share_pre_hill'] = round(float((plat[(plat.hill_window == 'pre_hill') & (plat.p_throws == 'L')].plate_apps.iat[0])
                                          / plat[plat.hill_window == 'pre_hill'].plate_apps.sum()), 4)
    H['lhp_share_post_hill'] = round(float((plat[(plat.hill_window == 'post_hill') & (plat.p_throws == 'L')].plate_apps.iat[0])
                                           / plat[plat.hill_window == 'post_hill'].plate_apps.sum()), 4)
    aug = k.pa_rows(jc[jc.month == 8])
    H['aug_lhp_pa'] = int((aug.p_throws == 'L').sum()); H['aug_pa'] = int(len(aug))

    # ── pitch type / group ───────────────────────────────────────────────
    pg = k.nresults_unrounded(['window', 'pitch_group'], jc.assign(game_year=2026), w)
    for f in (k.swing_rate, k.chase_rate_g, k.whiff_rate_fix):
        part = f(['window', 'pitch_group'], jc)
        dupes = [c for c in part.columns if c in pg.columns and c not in ('window', 'pitch_group')]
        pg = pg.merge(part.drop(columns=dupes), on=['window', 'pitch_group'], how='left')
    pg.to_csv(f'{OUT}/dp_uc34_pitch_group_window.csv', index=False)
    H['pitch_group_window'] = R3(pg[['window', 'pitch_group', 'pitches', 'plate_apps',
                                     'ba', 'slg', 'woba', 'krate', 'whiff_rate',
                                     'chase_rate']]).to_dict('records')

    pt = k.nresults_unrounded(['game_year', 'pitch_type'], jc, w)
    ptd = k.whiff_rate_fix(['pitch_type'], jc)[['pitch_type', 'swings', 'whiff_rate']]
    ptc = k.chase_rate_g(['pitch_type'], jc)[['pitch_type', 'chase_rate', 'pitches']]
    pt = pt.drop(columns=['pitches']).merge(ptd, on='pitch_type').merge(ptc, on='pitch_type')
    pt = pt[pt.pitches >= 40].sort_values('pitches', ascending=False)
    pt.to_csv(f'{OUT}/dp_uc34_pitch_type_season.csv', index=False)
    H['pitch_type'] = R3(pt[['pitch_type', 'pitches', 'plate_apps', 'ba', 'slg',
                             'woba', 'krate', 'whiff_rate', 'chase_rate']]).to_dict('records')

    # ── count state ──────────────────────────────────────────────────────
    cs = k.nresults_unrounded(['window', 'count_state'], jc.assign(game_year=2026), w)
    cs.to_csv(f'{OUT}/dp_uc34_count_state.csv', index=False)
    H['count_state'] = R3(cs[['window', 'count_state', 'plate_apps', 'ba', 'obp',
                              'slg', 'woba', 'krate']]).to_dict('records')

    # ── ground-ball quality (the speed question) ─────────────────────────
    bip = jc[jc.type == 'X']
    gb = bip[bip.bb_type == 'ground_ball']
    gbq = gb.groupby('window').apply(lambda d: pd.Series({
        'gb': len(d), 'gb_hits': int(d.events.isin(k.HIT_EV).sum()),
        'gb_ba': float(d.events.isin(k.HIT_EV).mean()),
        'gb_mean_ev': float(d.launch_speed.mean()),
        'gb_xba': float(d.estimated_ba_using_speedangle.mean()),
        'gb_hits_under_90ft': int(((d.events.isin(k.HIT_EV)) & (d.hit_distance_sc <= 90)).sum()),
    }), include_groups=False).reset_index()
    gbq.to_csv(f'{OUT}/dp_uc34_groundball_quality.csv', index=False)
    H['groundball'] = R3(gbq).to_dict('records')

    with open(f'{OUT}/dp_uc34_headlines.json', 'w') as fh:
        json.dump(H, fh, indent=2, default=str)

    figures(jc, z, zw, rl, cf_rl, cf_seasons, pool, me, hm, pg, scan)
    print('receipts + figures written')
    return H


# ══════════════════════════════════════════════════════════════════════════
def figures(jc, z, zw, rl, cf_rl, cf_seasons, pool, me, hm, pg, scan):
    # FIG 1 — the DPO's ask: CF context ghost lines, three results KPIs
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.1))
    specs = [('cum_ba', 'Batting Average', (.180, .375)),
             ('cum_obp', 'On-Base Percentage', (.220, .430)),
             ('cum_woba', 'wOBA', (.200, .430))]
    for ax, (col, title, ylim) in zip(axes, specs):
        for sk, g in cf_rl.groupby('season_key'):
            g = g[g.cum_pa >= k.PA_FLOOR]
            if sk == 'Crawford 2026':
                continue
            ax.plot(g.cum_pa, g[col], color=GREY, lw=1.1, zorder=1)
            ax.annotate(sk.split()[0][:3] + " '" + sk.split()[1][2:],
                        xy=(g.cum_pa.iat[-1], g[col].iat[-1]), fontsize=5.4,
                        color='#7A828F', xytext=(3, 0), textcoords='offset points',
                        va='center')
        c = cf_rl[cf_rl.season_key == 'Crawford 2026']
        c = c[c.cum_pa >= k.PA_FLOOR]
        ax.plot(c.cum_pa, c[col], color=RED, lw=2.4, zorder=3, label='Crawford 2026')
        ax.scatter([c.cum_pa.iat[-1]], [c[col].iat[-1]], color=RED, s=26, zorder=4)
        ax.set_title(title); ax.set_xlabel('cumulative plate appearances')
        ax.set_ylim(*ylim); ax.grid(alpha=.22, lw=.6)
        ax.axvline(c.cum_pa.iat[-1], color=NAVY, lw=.7, ls=':', alpha=.6)
    axes[0].set_ylabel('season-to-date')
    axes[0].legend(loc='lower right', fontsize=7, frameon=False)
    fig.suptitle('Justin Crawford 2026 vs Phillies primary centre fielders, Statcast era',
                 color=NAVY, fontweight='bold', y=1.02, fontsize=11.5)
    fig.text(0.5, -0.045, 'Grey = the 8 comparator player-seasons (>80 games in CF). '
             'Left tail below 50 PA suppressed. Dotted line = Crawford as-of PA.',
             ha='center', fontsize=7, color='#55606E')
    fig.savefig(f'{OUT}/dp_uc34_fig1_cf_context.png'); plt.close(fig)

    # FIG 2 — monthly results with floor shading
    fig, ax = plt.subplots(figsize=(9.2, 3.9))
    ax2 = ax.twinx()
    ax2.bar(z.month, z.plate_apps, color='#E7EBF2', width=.62, zorder=0)
    ax2.set_ylabel('plate appearances', color='#8C93A0', fontsize=8)
    ax2.set_ylim(0, z.plate_apps.max() * 3.0); ax2.tick_params(labelsize=7, colors='#8C93A0')
    ax2.axhline(k.PA_FLOOR, color=GOLD, lw=1.0, ls='--')
    ax2.annotate('50-PA floor', xy=(z.month.min() - .05, k.PA_FLOOR), fontsize=6.4,
                 color=GOLD, va='bottom')
    for col, lbl, c, mk in [('ba', 'BA', NAVY, 'o'), ('obp', 'OBP', GOLD, 's'),
                            ('woba', 'wOBA', RED, 'D')]:
        ax.plot(z.month, z[col], marker=mk, color=c, lw=2.0, ms=5, label=lbl, zorder=3)
    for m in z[z.below_pa_floor].month:
        ax.axvspan(m - .42, m + .42, color='#FBF3E0', zorder=-1)
    ax.set_xticks(z.month)
    ax.set_xticklabels(['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'][:len(z)])
    ax.set_ylabel('rate'); ax.set_ylim(.15, .50); ax.grid(alpha=.22, lw=.6)
    ax.legend(loc='upper left', fontsize=8, frameon=False, ncol=3)
    ax.set_title('Monthly results — the path is not a steady climb\n'
                 'shaded months are below the 50-PA reliability floor', loc='left')
    ax.set_zorder(ax2.get_zorder() + 1); ax.patch.set_visible(False)
    fig.savefig(f'{OUT}/dp_uc34_fig2_monthly_results.png'); plt.close(fig)

    # FIG 3 — mechanism: what moved and what didn't
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 3.9))
    items = [('babip', 'BABIP'), ('xwobacon_bip', 'xwOBAcon'), ('iso', 'ISO'),
             ('krate', 'K%'), ('whiff_rate', 'Whiff%'), ('chase_rate', 'Chase%'),
             ('gb_rate', 'GB%'), ('hard_hit_rate', 'Hard-Hit%')]
    pre = zw[zw.window == 'pre_0615'].iloc[0]; post = zw[zw.window == 'post_0615'].iloc[0]
    ypos = np.arange(len(items))[::-1]
    ax = axes[0]
    for y, (col, lbl) in zip(ypos, items):
        a, b = float(pre[col]), float(post[col])
        ax.annotate('', xy=(b, y), xytext=(a, y),
                    arrowprops=dict(arrowstyle='-|>', lw=1.7,
                                    color=RED if b > a else NAVY, alpha=.85))
        ax.scatter([a], [y], color='#9AA3B0', s=26, zorder=3)
        ax.scatter([b], [y], color=RED if b > a else NAVY, s=34, zorder=3)
        ax.annotate(f'{a:.3f} → {b:.3f}', xy=(max(a, b), y), xytext=(7, 0),
                    textcoords='offset points', fontsize=6.8, va='center', color='#40484F')
    ax.set_yticks(ypos); ax.set_yticklabels([l for _, l in items], fontsize=8.5)
    ax.set_xlim(0, .78); ax.grid(axis='x', alpha=.22, lw=.6)
    ax.set_title('Before vs after 15 Jun — what actually moved', loc='left')
    ax.set_xlabel('rate')

    ax = axes[1]
    b2 = z[['month', 'gb_rate', 'ld_rate', 'fb_rate', 'pu_rate']].set_index('month')
    b2.plot(kind='bar', stacked=True, ax=ax, width=.72,
            color=['#7C8798', NAVY, '#5C7FBF', GOLD], legend=False)
    ax.set_xticklabels(['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'][:len(z)], rotation=0)
    ax2 = ax.twinx()
    ax2.plot(range(len(z)), z.mean_la, color=RED, marker='D', ms=5, lw=2.1)
    ax2.set_ylabel('mean launch angle (°)', color=RED, fontsize=8)
    ax2.tick_params(colors=RED, labelsize=7); ax2.set_ylim(-6, 22)
    ax2.axhline(float(pool.mean_la.median()), color=RED, ls=(0, (5, 4)), lw=.9, alpha=.45)
    ax2.annotate(f'pool median LA {pool.mean_la.median():.1f}°',
                 xy=(len(z) - .55, pool.mean_la.median()), fontsize=6.2, color=RED,
                 va='bottom', ha='right', alpha=.85,
                 xytext=(0, 2), textcoords='offset points')
    ax.set_ylabel('batted-ball share'); ax.set_ylim(0, 1.16); ax.set_xlabel('')
    ax2.set_ylim(-6, 27.5)
    ax.legend(['GB', 'LD', 'FB', 'PU'], fontsize=7, frameon=False, ncol=4,
              loc='upper center', bbox_to_anchor=(.5, 1.005))
    ax.set_title('Batted-ball mix and launch angle — unchanged', loc='left')
    fig.savefig(f'{OUT}/dp_uc34_fig3_mechanism.png'); plt.close(fig)

    # FIG 4 — profile vs population
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.0))
    ax = axes[0]
    ax.scatter(pool.mean_la, pool.woba, s=17, color=GREY, alpha=.75, zorder=1)
    lowla = pool.nsmallest(8, 'mean_la')
    ax.scatter(lowla.mean_la, lowla.woba, s=30, facecolors='none',
               edgecolors=NAVY, lw=1.0, zorder=2)
    lowla = lowla.sort_values('woba', ascending=False).reset_index(drop=True)
    for i, r in enumerate(lowla.itertuples()):
        if r.player_name == k.SUBJECT: continue
        dx, dy = [(8, 7), (8, -13), (-10, 10), (-8, -14), (10, 5), (9, -12), (-12, 8), (10, 10)][i % 8]
        ax.annotate(f"{r.player_name.split(',')[0]} '{str(r.game_year)[2:]}",
                    xy=(r.mean_la, r.woba), fontsize=6.0, color='#55606E',
                    xytext=(dx, dy), textcoords='offset points',
                    arrowprops=dict(arrowstyle='-', lw=.45, color='#B8BFCB',
                                    shrinkA=0, shrinkB=2))
    ax.scatter([me.mean_la], [me.woba], s=95, color=RED, zorder=4, marker='*')
    ax.annotate('Crawford 2026', xy=(me.mean_la, me.woba), xytext=(11, -19),
                textcoords='offset points', fontsize=7.6, color=RED, fontweight='bold')
    ax.axhline(pool.woba.median(), color='#9AA3B0', ls=':', lw=.9)
    ax.set_xlim(-3, 28)
    ax.set_xlabel('mean launch angle on tracked BIP (°)'); ax.set_ylabel('wOBA')
    ax.grid(alpha=.2, lw=.6)
    ax.set_title(f'The archetype — {len(pool)} Phillies hitter-seasons since 2015', loc='left')

    ax = axes[1]
    prof_rows = [('swing_rate', 'Swing%'), ('chase_rate', 'Chase%'), ('whiff_rate', 'Whiff%'),
                 ('gb_rate', 'GB%'), ('mean_la', 'Mean LA'), ('ba', 'BA'),
                 ('obp', 'OBP'), ('woba', 'wOBA'), ('iso', 'ISO')]
    pct = [k.pool_percentile(pool, c, me[c]) for c, _ in prof_rows]
    y = np.arange(len(prof_rows))[::-1]
    cols = [RED if p >= 75 else (NAVY if p <= 25 else '#8C93A0') for p in pct]
    ax.barh(y, pct, color=cols, height=.62)
    ax.axvline(50, color='#55606E', lw=.9, ls='--')
    for yy, p in zip(y, pct):
        ax.annotate(f'{p:.0f}', xy=(p, yy), xytext=(4, 0), textcoords='offset points',
                    fontsize=7.2, va='center', color='#40484F')
    ax.set_yticks(y); ax.set_yticklabels([l for _, l in prof_rows], fontsize=8.5)
    ax.set_xlim(0, 108); ax.set_xlabel('percentile within the Phillies pool')
    ax.grid(axis='x', alpha=.2, lw=.6)
    ax.set_title('Profile percentiles — the scouting report verifies', loc='left')
    fig.savefig(f'{OUT}/dp_uc34_fig4_profile.png'); plt.close(fig)

    # FIG 5 — platoon exposure
    fig, ax = plt.subplots(figsize=(9.2, 3.5))
    xs = np.arange(len(hm))
    ax.bar(xs, hm.lhp_share, color=[RED if s < .05 else NAVY for s in hm.lhp_share],
           width=.62)
    ax.axhline(float(hm.L.sum() / hm.pa.sum()), color=GOLD, ls='--', lw=1.1)
    ax.annotate(f'season {hm.L.sum()/hm.pa.sum():.1%}', xy=(0, hm.L.sum()/hm.pa.sum()),
                fontsize=6.8, color=GOLD, va='bottom', xytext=(2, 2), textcoords='offset points')
    hill_ix = [i for i, v in enumerate(hm.halfmonth) if v == '2026-06a']
    if hill_ix:
        ax.axvline(hill_ix[0] + .5, color='#55606E', lw=1.1, ls=':')
        ax.annotate('Derek Hill\nacquired 13 Jun', xy=(hill_ix[0] + .6, .34), fontsize=6.8,
                    color='#40484F')
    for i, r in enumerate(hm.itertuples()):
        ax.annotate(f'{int(r.L)}/{int(r.pa)}', xy=(i, r.lhp_share), xytext=(0, 3),
                    textcoords='offset points', ha='center', fontsize=6.2, color='#55606E')
    ax.set_xticks(xs); ax.set_xticklabels(hm.halfmonth, rotation=45, ha='right', fontsize=7)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel('share of PA vs LHP'); ax.set_ylim(0, .45); ax.grid(axis='y', alpha=.22, lw=.6)
    ax.set_title('Platoon exposure by half-month — the shielding starts in August, not with Hill',
                 loc='left')
    fig.savefig(f'{OUT}/dp_uc34_fig5_platoon.png'); plt.close(fig)

    # FIG 6 — pitch group
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 3.8))
    order = ['fastball', 'breaking', 'offspeed']
    p = pg.pivot_table(index='pitch_group', columns='window', values='woba').reindex(order)
    n = pg.pivot_table(index='pitch_group', columns='window', values='plate_apps').reindex(order)
    x = np.arange(len(order))
    ax = axes[0]
    ax.bar(x - .19, p['pre_0615'], .36, color='#9AA3B0', label='before 15 Jun')
    ax.bar(x + .19, p['post_0615'], .36, color=RED, label='from 15 Jun')
    for i in x:
        ax.annotate(f"{int(n['pre_0615'].iloc[i])} PA", xy=(i - .19, p['pre_0615'].iloc[i]),
                    ha='center', xytext=(0, 2), textcoords='offset points', fontsize=6.2, color='#55606E')
        ax.annotate(f"{int(n['post_0615'].iloc[i])} PA", xy=(i + .19, p['post_0615'].iloc[i]),
                    ha='center', xytext=(0, 2), textcoords='offset points', fontsize=6.2, color=RED)
    ax.set_xticks(x); ax.set_xticklabels([o.title() for o in order])
    ax.set_ylabel('wOBA'); ax.set_ylim(0, .42); ax.grid(axis='y', alpha=.22, lw=.6)
    ax.legend(fontsize=7.5, frameon=False)
    ax.set_title('wOBA by pitch group', loc='left')
    ax = axes[1]
    c = pg.pivot_table(index='pitch_group', columns='window', values='chase_rate').reindex(order)
    ax.bar(x - .19, c['pre_0615'], .36, color='#9AA3B0', label='before 15 Jun')
    ax.bar(x + .19, c['post_0615'], .36, color=NAVY, label='from 15 Jun')
    ax.set_xticks(x); ax.set_xticklabels([o.title() for o in order])
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel('chase rate'); ax.set_ylim(0, .62); ax.grid(axis='y', alpha=.22, lw=.6)
    ax.legend(fontsize=7.5, frameon=False)
    ax.set_title('Chase rate by pitch group — offspeed is the clean change', loc='left')
    fig.savefig(f'{OUT}/dp_uc34_fig6_pitch_group.png'); plt.close(fig)


if __name__ == '__main__':
    main()
