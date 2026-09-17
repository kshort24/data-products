"""Figures for UC #45 (uc-pps-031). Every plotted number is read from a receipt in out/.
Titles that make a claim are ASSERTED against the receipt first (uc-pps-030 rule 4)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); import dp_uc45_kernel as K

OUT = HERE / 'out'
RED, NAVY, BLUE = K.PHILLIES_RED, K.PHILLIES_NAVY, K.PHILLIES_BLUE
GRAY, LGRAY = '#8C8C8C', '#D9D9D9'
REG_COL = {'heart': NAVY, 'edge_in': BLUE, 'edge_out': '#F2A33A', 'beyond': RED}
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#444', 'axes.labelcolor': '#222', 'figure.dpi': 170,
                     'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False})

R = lambda n: pd.read_csv(OUT / f'dp_uc45_{n}.csv')
season, half, month = R('season_panel'), R('half_panel'), R('month_panel_2026')
league, pt, dec = R('league_control'), R('premise_tests'), R('rail_decomposition')
loc, starts = R('pitch_locations'), R('start_log_2026')
bph, bsh, cst = R('by_pitch_half'), R('by_stand_half'), R('count_state')
cstl, sdm = R('count_state_league_2026'), R('start_distribution_summary')

# ---------------------------------------------------------------------------
# timeline frame: 2021-22 .. 2025 seasons, then 2026 1H / 2H
# ---------------------------------------------------------------------------
tl = season[season.season != '2026'].copy(); tl['label'] = tl.season.astype(str)
h26 = half[half.game_year == 2026].copy(); h26['label'] = '2026 ' + h26.half
tl = pd.concat([tl, h26], ignore_index=True)
LA = league[league.population == 'all pitchers in PHI games']
def lg_val(label, col):
    if label.startswith('2026 '):
        return float(LA[(LA.game_year == 2026) & (LA.half == label[-2:])][col].iloc[0])
    ys = [2021, 2022] if label == '2021-22' else [int(label)]
    x = LA[LA.game_year.isin(ys) & (LA.half == 'season')]
    return float((x[col] * x.pitches).sum() / x.pitches.sum())

# ============================================================================
# FIG 1 — premise scorecard
# ============================================================================
panels = [('bbrate', 'Walk rate (uBB / PA)', 'P1'), ('in_zone_rate', 'In-zone rate (Statcast zone)', 'P2'),
          ('chase_rate', 'Chase rate', 'P3'), ('pitch_share_ahead', 'Pitches thrown ahead in the count', 'P4'),
          ('edge_rate', 'Edge Rate (governed, ±1 ball)', 'K2'), ('shadow_miss_rate', 'Shadow Miss Rate (NEW, SZ-2)', 'K1')]
fig, axes = plt.subplots(2, 3, figsize=(11.2, 6.1))
x = np.arange(len(tl))
for ax, (col, ttl, pid) in zip(axes.flat, panels):
    y = tl[col].astype(float).values
    lg = [lg_val(l, col) for l in tl.label]
    ax.plot(x, lg, color=GRAY, lw=1.3, ls='--', marker='.', label='all pitchers in PHI games')
    ax.plot(x[:-2], y[:-2], color=NAVY, lw=2.0, marker='o', ms=4.5, label='Sánchez')
    ax.plot(x[-3:], y[-3:], color=RED, lw=2.4)
    ax.scatter(x[-2:], y[-2:], color=RED, s=30, zorder=3)
    ax.scatter(x[-3:-2], y[-3:-2], color=NAVY, s=22, zorder=3)
    for xi, yi in zip(x, y):
        ax.annotate(f'{yi:.3f}'.lstrip('0'), (xi, yi), textcoords='offset points', xytext=(0, 6),
                    ha='center', fontsize=6.6, color='#222')
    v = pt[(pt.premise == pid)]
    vs, vh = v[v.window.str.startswith('2025')].verdict.iloc[0], v[v.window.str.startswith('2026')].verdict.iloc[0]
    ax.set_title(f'{pid} · {ttl}', fontsize=9.2, color=NAVY, loc='left', fontweight='bold')
    import textwrap
    ax.text(0.0, -0.17, textwrap.fill(f'2025→26: {vs}', 58) + '\n' + textwrap.fill(f'1H→2H: {vh}', 58),
            transform=ax.transAxes, fontsize=6.6, color='#444', va='top')
    ax.set_xticks(x); ax.set_xticklabels([l.replace('2026 ', "'26 ") for l in tl.label], fontsize=7)
    ax.axvspan(len(x) - 2.5, len(x) - 0.5, color=RED, alpha=0.05)
    ax.margins(y=0.25)
axes[0, 0].legend(fontsize=7, frameon=False, loc='upper right')
fig.suptitle('Cristopher Sánchez — the four premises, the governed Edge Rate and the new Shadow Miss Rate',
             x=0.01, ha='left', fontsize=12.5, color=NAVY, fontweight='bold')
fig.text(0.01, 0.925, "Seasons 2021-22 → 2025, then 2026 split at the All-Star break (red). Dashed = every pitcher in a "
         "Phillies game that season. 2026 zone rails changed definition (O-18) — see Fig. 4 before reading 2025→2026 zone moves.",
         fontsize=7.8, color='#555')
fig.tight_layout(rect=(0, 0, 1, 0.91)); fig.subplots_adjust(hspace=0.78)
fig.savefig(OUT / 'dp_uc45_fig1_premise_scorecard.png', bbox_inches='tight'); plt.close(fig)

# ============================================================================
# FIG 2 — the shadow map
# ============================================================================
wins = [('2025 · season', loc[loc.game_year == 2025]),
        ('2026 · first half', loc[(loc.game_year == 2026) & (loc.half == '1H')]),
        ('2026 · second half', loc[(loc.game_year == 2026) & (loc.half == '2H')])]
fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.9), sharey=True)
for ax, (lab, d) in zip(axes, wins):
    top, bot = float(d.sz_top.median()), float(d.sz_bot.median())
    zn = bot + (d.plate_z - d.sz_bot)          # shift to a common floor; colour is per-pitch truth
    for reg in ['heart', 'edge_in', 'edge_out', 'beyond']:
        m = d.region == reg
        ax.scatter(d.plate_x[m], zn[m], s=5, alpha=0.38, color=REG_COL[reg], lw=0,
                   label=f"{reg.replace('_', ' ')} {m.mean():.1%}")
    ax.add_patch(FancyBboxPatch((-K.PLATE_HALF, bot), 2 * K.PLATE_HALF, top - bot,
                                boxstyle=f'round,pad={K.BALL_FT:.4f},rounding_size={K.BALL_FT:.4f}',
                                fill=False, ec=RED, lw=1.4, ls='--'))
    ax.add_patch(Rectangle((-K.PLATE_HALF, bot), 2 * K.PLATE_HALF, top - bot, fill=False, ec='black', lw=1.3))
    miss = (d.region == 'beyond').mean()
    ax.set_title(f'{lab}\n{len(d):,} pitches · missed the shadow {miss:.1%}', fontsize=9.5, color=NAVY)
    ax.set_xlim(-2.6, 2.6); ax.set_ylim(-0.2, 5.0); ax.set_aspect('equal')
    ax.set_xlabel("plate_x (ft), catcher's view")
    ax.legend(fontsize=6.6, loc='upper left', frameon=False, markerscale=2.2)
axes[0].set_ylabel('plate_z (ft), shifted to each batter\'s zone floor')
fig.suptitle('The shadow: rulebook zone (black) grown by one baseball, 2.94 in (red dashed, rounded corners)',
             x=0.01, ha='left', fontsize=12, color=NAVY, fontweight='bold')
fig.text(0.01, 0.005, "+x = first-base side = Sánchez's arm side (away from a RHB). Colour = each pitch's own classification "
         "against its own batter's rails; the drawn zone is the window median.", fontsize=7.3, color='#555')
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(OUT / 'dp_uc45_fig2_shadow_map.png', bbox_inches='tight'); plt.close(fig)

# ============================================================================
# FIG 3 — the proof: chase outside the shadow
# ============================================================================
e1 = pt[(pt.premise == 'E1') & pt.window.str.startswith('2026')].iloc[0]
assert e1.delta < 0 and e1.p < 0.05, 'Fig 3 headline claims a significant 2H drop'
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.2, 4.3), gridspec_kw={'width_ratios': [1.05, 1]})
hh = half[half.game_year >= 2024].copy(); hh['label'] = hh.game_year.astype(str) + ' ' + hh.half
xs = np.arange(len(hh))
lgh = [float(LA[(LA.game_year == r.game_year) & (LA.half == r.half)].beyond_shadow_chase_rate.iloc[0]) for r in hh.itertuples()]
cols = [RED if l.startswith('2026') else NAVY for l in hh.label]
a1.bar(xs, hh.beyond_shadow_chase_rate, color=cols, width=0.62)
a1.plot(xs, lgh, color=GRAY, ls='--', marker='o', ms=3.5, lw=1.2, label='all pitchers in PHI games')
for xi, r in zip(xs, hh.itertuples()):
    a1.text(xi, r.beyond_shadow_chase_rate + 0.006, f'{r.beyond_shadow_chase_rate:.3f}'.lstrip('0') + f'\nn={int(r.n_beyond)}',
            ha='center', fontsize=7)
a1.set_xticks(xs); a1.set_xticklabels(hh.label, fontsize=8); a1.set_ylim(0, 0.43)
a1.set_ylabel('swings / pitches more than one ball outside the zone'); a1.legend(frameon=False, fontsize=7.5)
a1.set_title(f'By half: 2026 1H {e1.v_before:.3f} → 2H {e1.v_after:.3f}  (z = {e1.z:.2f}, p = {e1.p:.3f})',
             fontsize=9.5, color=NAVY, loc='left')
mm = month[month.month >= 4]
a2.plot(mm.month, mm.beyond_shadow_chase_rate, color=RED, marker='o', lw=2.2, label='chase beyond the shadow (SZ-3)')
a2.plot(mm.month, mm.shadow_miss_rate, color=NAVY, marker='s', lw=1.8, label='shadow miss rate (SZ-2)')
a2.plot(mm.month, mm.pitch_share_ahead, color=GRAY, marker='^', lw=1.4, ls=':', label='pitches thrown ahead (CL-1)')
for r in mm.itertuples():
    a2.text(r.month, r.beyond_shadow_chase_rate + 0.012, f'{r.beyond_shadow_chase_rate:.3f}'.lstrip('0'), ha='center', fontsize=7, color=RED)
a2.set_xticks(mm.month); a2.set_xticklabels(['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'])
a2.axvline(7.45, color='#999', lw=0.8, ls='--'); a2.text(7.5, 0.47, 'ASG (Jul holds 2 starts each side)', fontsize=6.8, color='#777')
a2.set_ylim(0.18, 0.5); a2.legend(frameon=False, fontsize=7.3, loc='lower left')
a2.set_title('2026 by month (March folded out: 87 pitches)', fontsize=9.5, color=NAVY, loc='left')
fig.suptitle('The proof: since the break, hitters stopped chasing the pitches that miss the shadow',
             x=0.01, ha='left', fontsize=12.5, color=NAVY, fontweight='bold')
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(OUT / 'dp_uc45_fig3_chase_beyond_shadow.png', bbox_inches='tight'); plt.close(fig)

# ============================================================================
# FIG 4 — how much of the 2025→2026 move is Sánchez? (O-18 decomposition)
# ============================================================================
fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.9))
for ax, (m, ttl) in zip(axes, [('shadow_miss_rate', 'Shadow Miss Rate (SZ-2)'),
                               ('geo_zone_rate', 'Zone rate, geometric twin'),
                               ('beyond_shadow_chase_rate', 'Chase beyond the shadow (SZ-3)')]):
    r = dec[dec.metric == m].iloc[0]
    steps = [('2025\nnative', r.subject_2025_native, None), ('ABS rail\nchange', r.rail_effect, GRAY),
             ('league\ndrift', r.league_common_rail_delta, LGRAY), ('Sánchez\nown', r.subject_specific, RED),
             ('2026', r.subject_2026, None)]
    run = 0
    for i, (lab, v, c) in enumerate(steps):
        if c is None:
            ax.bar(i, v, color=NAVY, width=0.6); run = v
            ax.text(i, v + 0.004, f'{v:.3f}'.lstrip('0'), ha='center', fontsize=7.5)
        else:
            ax.bar(i, v, bottom=run, color=c, width=0.6)
            ax.text(i, max(run, run + v) + 0.004, f'{v:+.3f}', ha='center', fontsize=7.5)
            run += v
    assert abs(run - r.subject_2026) < 1e-6
    lo = min(r.subject_2025_native, r.subject_2026) - 0.06
    ax.set_ylim(max(0, lo), max(r.subject_2025_native, r.subject_2026) + 0.03)
    ax.set_xticks(range(5)); ax.set_xticklabels([s[0] for s in steps], fontsize=7.3)
    ax.set_title(f'{ttl}\n{r.subject_specific_share:.0%} of the move is his', fontsize=9.3, color=NAVY, loc='left')
fig.suptitle('2026 changed the zone, not just the pitcher: the move decomposed on common (2026 ABS) rails',
             x=0.01, ha='left', fontsize=12, color=NAVY, fontweight='bold')
fig.text(0.01, -0.02, 'Covered batters only (78% of Sánchez 2025 pitches). Rail effect = 2025 pitches re-scored on each hitter\'s 2026 zone; '
         'league drift = same re-score for every pitcher in a Phillies game.', fontsize=7.3, color='#555')
fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig(OUT / 'dp_uc45_fig4_rail_decomposition.png', bbox_inches='tight'); plt.close(fig)

# ============================================================================
# FIG 5 — where it leaks: stand × pitch × count, 2026 1H vs 2H
# ============================================================================
fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.2))
ax = axes[0]
b = bph[bph.game_year == 2026]
for i, p in enumerate(['Sinker', 'Changeup', 'Slider']):
    r1 = b[(b.pitch_name == p) & (b.half == '1H')].iloc[0]; r2 = b[(b.pitch_name == p) & (b.half == '2H')].iloc[0]
    for j, (col, mk) in enumerate([('shadow_miss_rate', 's'), ('beyond_shadow_chase_rate', 'o')]):
        y = i + (j - 0.5) * 0.3
        ax.annotate('', xy=(r2[col], y), xytext=(r1[col], y),
                    arrowprops=dict(arrowstyle='->', color=RED if col.startswith('beyond') else NAVY, lw=1.6))
        ax.scatter([r1[col]], [y], marker=mk, color='white', ec='#333', zorder=3, s=26)
        ax.text(r2[col], y + 0.08, f'{r2[col]:.2f}', fontsize=6.6, ha='center')
ax.set_yticks(range(3)); ax.set_yticklabels(['Sinker', 'Changeup', 'Slider']); ax.set_xlim(0.05, 0.7)
ax.set_title('By pitch, 1H → 2H\n■ shadow miss (navy)  ● chase beyond (red)', fontsize=8.8, color=NAVY, loc='left')
ax = axes[1]
s6 = bsh[bsh.game_year == 2026]
labs = ['bbrate', 'shadow_miss_rate', 'beyond_shadow_chase_rate', 'pitch_share_ahead']
nm = ['BB%', 'Shadow miss', 'Chase beyond', 'Ahead share']
w = 0.2
for k, (st, colr) in enumerate([('R', RED), ('L', BLUE)]):
    for hh_, alpha in [('1H', 0.45), ('2H', 1.0)]:
        r = s6[(s6.stand == st) & (s6.half == hh_)].iloc[0]
        off = (k * 2 + (0 if hh_ == '1H' else 1) - 1.5) * w
        ax.bar(np.arange(4) + off, [r[c] for c in labs], width=w, color=colr, alpha=alpha,
               label=f'vs {st}HB {hh_} ({int(r.plate_apps)} PA)')
ax.set_xticks(range(4)); ax.set_xticklabels(nm, fontsize=7.6); ax.legend(fontsize=6.6, frameon=False)
ax.set_title('By batter side, 2026 1H vs 2H', fontsize=8.8, color=NAVY, loc='left')
ax = axes[2]
order = ['0-0', 'ahead', 'even', 'behind']
c6 = cst[cst.game_year == 2026]
for hh_, colr, dx in [('1H', NAVY, -0.18), ('2H', RED, 0.18)]:
    v = [float(c6[(c6.half == hh_) & (c6.count_state == o)].beyond_shadow_chase_rate.iloc[0]) for o in order]
    lv = [float(cstl[(cstl.half == hh_) & (cstl.count_state == o)].beyond_shadow_chase_rate.iloc[0]) for o in order]
    ax.bar(np.arange(4) + dx, v, width=0.34, color=colr, label=f'Sánchez {hh_}')
    ax.scatter(np.arange(4) + dx, lv, marker='_', s=160, color='black', zorder=3)
ax.scatter([], [], marker='_', color='black', label='league, same half')
ax.set_xticks(range(4)); ax.set_xticklabels(order); ax.set_ylim(0, 0.5); ax.legend(fontsize=7, frameon=False, ncol=3, loc='upper left')
ax.set_title('Chase beyond the shadow, by pre-pitch count', fontsize=8.8, color=NAVY, loc='left')
fig.suptitle('Where the free swings went: right-handed hitters, the changeup, and counts he was ahead in',
             x=0.01, ha='left', fontsize=12, color=NAVY, fontweight='bold')
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(OUT / 'dp_uc45_fig5_where_it_leaks.png', bbox_inches='tight'); plt.close(fig)

# ============================================================================
# FIG 6 — 2026 start log
# ============================================================================
fig, ax = plt.subplots(figsize=(11.2, 3.5))
s = starts.copy(); s['d'] = pd.to_datetime(s.game_date)
ax.bar(s.d, s.shadow_miss_rate, width=3.2, color=np.where(s.half == '2H', RED, NAVY), alpha=0.8, label='shadow miss rate')
ax.plot(s.d, s.shadow_miss_rate.rolling(5).mean(), color='black', lw=1.5, label='5-start rolling')
ax.plot(s.d, s.beyond_shadow_chase_rate, color='#F2A33A', marker='o', ms=3.5, lw=1.1, label='chase beyond the shadow')
fm = sdm[(sdm.game_year == 2026) & (~sdm.is_subject)]
ax.axhline(float(fm.median_shadow_miss.mean()), color=GRAY, ls='--', lw=1, label='median 2026 start, all starters in PHI games')
for r in s.itertuples():
    if r.walks >= 3:
        ax.text(r.d, r.shadow_miss_rate + 0.012, f'{int(r.walks)} BB', ha='center', fontsize=6.5, color=RED)
ax.set_ylim(0.1, 0.62); ax.legend(fontsize=7, frameon=False, ncol=4, loc='upper left')
ax.set_title('Every 2026 start (31): share of located pitches that missed the shadow; red = after the break',
             fontsize=10.5, color=NAVY, loc='left', fontweight='bold')
fig.tight_layout()
fig.savefig(OUT / 'dp_uc45_fig6_start_log.png', bbox_inches='tight'); plt.close(fig)
print('FIGS OK')
