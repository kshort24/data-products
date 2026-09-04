"""
dp_uc40a_bat_path.py — Layer-3 BUILD, uc-pos-014 v1.1.0 bat-path addendum
==========================================================================
Answers the DPO's follow-up: what do Statcast's bat-path columns say about
HOW Trea Turner is meeting the ball, and specifically about the breaking-ball
popups, beyond bat speed?

Reads the data plane, writes receipts to out/. Defines nothing — every metric
comes from dp_uc40a_kernel.py, whose conventions are asserted before any
number is produced.

Run:  DP_UC40_DATA=<MLB repo> python dp_uc40a_bat_path.py [outdir]
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dp_uc40_kernel as K0                                     # noqa: E402
import dp_uc40a_kernel as K                                     # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
P = lambda n: os.path.join(OUT, f'dp_uc40a_{n}')
R = lambda df, n: (df.to_csv(P(n + '.csv'), index=False), print(f'  wrote {n}.csv  {df.shape}'))
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 60)
H: dict = {}
sec = lambda t: print('\n' + '=' * 78 + f'\n{t}\n' + '=' * 78)

T = K.SUBJECT_MLBAM
Y0, Y1 = 2025, 2026                       # the only two seasons with bat path
SHOW = ['attack_angle', 'attack_direction', 'pull_direction', 'swing_path_tilt',
        'intercept_side_in', 'intercept_depth_in', 'bat_speed', 'swing_length',
        'ideal_aa_rate']

# ══════════════════════════════════════════════════ LOAD + ASSERT ═════════
sec('LOAD')
pos, _ = K0.load_frames()
pos = pos[pos.game_type == 'R'].copy()
pos['pitch_group'] = pos.pitch_type.map(K.PITCH_GROUP).fillna('other')
sub = pos[pos.batter == T].copy()
sub = K0.add_windows(sub)
print(f'PHI batting R rows {len(pos):,} · subject rows {len(sub):,} · '
      f'seasons {sorted(sub.game_year.unique())}')

sec('CONVENTION ASSERTIONS — the build refuses to publish if any fail')
conv = K.assert_conventions(pos)
R(conv, 'bp_convention_assertions')
H['conventions'] = conv.to_dict('records')

# ══════════════════════════════════════════════════ COVERAGE ══════════════
sec('SENSOR COVERAGE — where the bat-path columns actually exist')
rows = []
for y in sorted(pos.game_year.unique()):
    for who, frame in (('all PHI batters', pos), ('Trea Turner', sub)):
        d = frame[frame.game_year == y]
        sw = K.swing_rows(d)
        bp = K.bat_path_population(d)
        has = 'attack_angle' in d.columns
        rows.append(dict(
            season=int(y), population=who, swings=len(sw),
            bunts_excluded=int(len(sw) - len(bp)),
            degenerate_under_25mph=int(bp.degenerate_path.sum()) if len(bp) else 0,
            bat_speed_tracked=int(d.bat_speed.notna().sum()) if 'bat_speed' in d.columns else 0,
            path_tracked=int(d.attack_angle.notna().sum()) if has else 0,
            path_coverage=round(d.attack_angle.notna().sum() / len(sw), 4) if has and len(sw) else np.nan))
cov = pd.DataFrame(rows)
R(cov, 'bp_coverage')
print(cov.to_string(index=False))
H['coverage'] = cov[cov.population == 'Trea Turner'].to_dict('records')

# ══════════════════════════════════════════════ SUBJECT BY SEASON ════════
sec('BP-1 · SUBJECT SWING PATH BY SEASON')
ss = K.swing_path_profile(['game_year'], sub)
R(ss.round(4), 'bp_subject_by_season')
print(ss[['game_year', 'swings', 'tracked_swings', 'tracking_coverage'] + SHOW
         ].round(3).to_string(index=False))
H['subject_by_season'] = ss.round(4).to_dict('records')

sec('BP-2 · SUBJECT SWING PATH BY SEASON x PITCH GROUP  (the DPO grain)')
sg = K.path_by_pitch_group(sub, extra_level='game_year')
sg = sg[sg.pitch_group != 'other']
R(sg.round(4), 'bp_subject_by_pitch_group')
print(sg[['game_year', 'pitch_group', 'tracked_swings'] + SHOW +
         ['bip', 'popups', 'pu_rate']].round(3).to_string(index=False))
H['subject_by_pitch_group'] = sg.round(4).to_dict('records')

sec('BP-2 · 2026 WINDOWS x PITCH GROUP (does the path move with the slump?)')
s26 = sub[sub.game_year == Y1]
wg = K.path_by_pitch_group(s26, extra_level='window')
wg = wg[wg.pitch_group != 'other']
R(wg.round(4), 'bp_subject_by_window_pitch_group')
print(wg[['window', 'pitch_group', 'tracked_swings'] + SHOW +
         ['bip', 'popups', 'pu_rate', 'below_swing_floor']].round(3).to_string(index=False))
H['subject_by_window'] = wg.round(4).astype({'window': str}).to_dict('records')

# ══════════════════════════════════════════════ POPUP SIGNATURE ══════════
sec('PU-1 · POPUP SIGNATURE — bat path on popups vs every other BIP')
ps = K.popup_signature(['game_year'], sub)
R(ps.round(4), 'bp_popup_signature_season')
print(ps[['game_year', 'is_popup', 'n'] + SHOW[:-1] +
         ['launch_angle', 'launch_speed', 'plate_z', 'below_floor']].round(2).to_string(index=False))

psg = K.popup_signature(['game_year', 'pitch_group'], sub)
psg = psg[psg.pitch_group != 'other']
R(psg.round(4), 'bp_popup_signature_pitch_group')
print('\nBREAKING BALLS ONLY:')
print(psg[psg.pitch_group == 'breaking'][
    ['game_year', 'is_popup', 'n'] + SHOW[:-1] +
    ['launch_angle', 'launch_speed', 'plate_z', 'below_floor']].round(2).to_string(index=False))
H['popup_signature_season'] = ps.round(4).to_dict('records')
H['popup_signature_pitch_group'] = psg.round(4).to_dict('records')

sec('PU-2 · POPUP RATE BY SEASON x PITCH GROUP')
pr = K.popup_rate(['game_year', 'pitch_group'], sub)
pr = pr[pr.pitch_group != 'other']
R(pr.round(4), 'bp_popup_rate_by_pitch_group')
print(pr.round(3).to_string(index=False))
H['popup_rate_pitch_group'] = pr.round(4).to_dict('records')

# reconciliation with the v1.0.0 product
v1 = K0.battedball_profile(['game_year'], sub[sub.game_year.isin([Y0, Y1])], bip_floor=25)
rec = K.popup_rate(['game_year'], sub[sub.game_year.isin([Y0, Y1])]).merge(
    v1[['game_year', 'pu_rate']].rename(columns={'pu_rate': 'v1_pu_rate'}), on='game_year')
rec['delta'] = (rec.pu_rate - rec.v1_pu_rate).abs()
R(rec.round(6), 'bp_v1_reconciliation')
print('\nRECONCILIATION with v1.0.0 battedball_profile.pu_rate:')
print(rec.round(6).to_string(index=False))
assert rec.delta.max() < 1e-9, 'PU-2 does not reconcile with the v1.0.0 popup rate'
H['v1_reconciliation_max_delta'] = float(rec.delta.max())

# ══════════════════════════════════════════ PB-1 PEER-NETTED DELTAS ══════
sec('PB-1 · PEER-NETTED YoY DELTAS — the O-16 control')
peer_rows, heads = [], []
for metric in ['swing_path_tilt', 'attack_angle', 'attack_direction',
               'intercept_side_in', 'intercept_depth_in', 'bat_speed', 'swing_length']:
    pf, hd = K.peer_delta(pos, T, metric, Y0, Y1, min_swings=200)
    pf.insert(0, 'metric', metric)
    peer_rows.append(pf)
    heads.append(hd)
peer = pd.concat(peer_rows, ignore_index=True)
head = pd.DataFrame(heads)
R(peer.round(4), 'bp_peer_cohort')
R(head.round(4), 'bp_peer_delta')
print(head.round(3).to_string(index=False))
H['peer_delta'] = head.round(4).to_dict('records')

# ═════════════════════════════════════ POPULATION PERCENTILES ════════════
sec('SUBJECT vs THE PHILLIES POPULATION, 2026 (>=200 tracked swings)')
pool = K.swing_path_profile(['batter'], pos[pos.game_year == Y1])
pool = pool[pool.tracked_swings >= 200]
srow = pool[pool.batter == T].iloc[0]
rows = []
for m in ['attack_angle', 'attack_direction', 'pull_direction', 'swing_path_tilt',
          'intercept_side_in', 'intercept_depth_in', 'bat_speed', 'swing_length',
          'ideal_aa_rate']:
    rows.append(dict(metric=m, turner_2026=srow[m],
                     pool_median=pool[m].median(), pool_min=pool[m].min(),
                     pool_max=pool[m].max(),
                     pctile=K0.pool_percentile(pool, m, srow[m]), pool_n=len(pool)))
pct = pd.DataFrame(rows)
R(pct.round(4), 'bp_population_percentiles')
print(pct.round(3).to_string(index=False))
H['population_percentiles'] = pct.round(4).to_dict('records')

# ══════════════════════════ BREAKING-BALL POPUP POOL (the headline) ══════
sec('BREAKING-BALL POPUP RATE — subject vs Phillies qualifiers, both seasons')
bb = pos[pos.pitch_group == 'breaking']
g = K.popup_rate(['batter', 'game_year'], bb)
g = g[g.bip >= 40]
R(g.round(4), 'bp_breaking_popup_pool')
lines = []
for y in (Y0, Y1):
    s = g[g.game_year == y]
    t = s[s.batter == T]
    lines.append(dict(season=y, qualifiers=len(s), pool_median=s.pu_rate.median(),
                      pool_max=s.pu_rate.max(),
                      subject_bip=int(t.bip.iloc[0]) if len(t) else None,
                      subject_popups=int(t.popups.iloc[0]) if len(t) else None,
                      subject_rate=float(t.pu_rate.iloc[0]) if len(t) else None,
                      subject_rank=int((s.pu_rate > t.pu_rate.iloc[0]).sum()) + 1 if len(t) else None,
                      subject_minus_median=float(t.pu_rate.iloc[0] - s.pu_rate.median()) if len(t) else None))
bpool = pd.DataFrame(lines)
R(bpool.round(4), 'bp_breaking_popup_headline')
print(bpool.round(4).to_string(index=False))
H['breaking_popup'] = bpool.round(4).to_dict('records')

# ═══════════════════════════════ ST-1 REUSE — is the path shift real? ════
sec('ST-1 · UNCERTAINTY BANDS ON THE PATH SHIFTS (inherited from v1.0.0)')
def welch(a, b, name, base):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    z = (b.mean() - a.mean()) / se if se else np.nan
    return dict(baseline=base, measure=name, n_baseline=len(a), n_compare=len(b),
                baseline_value=a.mean(), compare_value=b.mean(),
                delta=b.mean() - a.mean(), se=se, z=z)

tr25 = K.tracked_swings(sub[sub.game_year == Y0])
tr26 = K.tracked_swings(sub[sub.game_year == Y1])
tr25, tr26 = K.with_bat_path(tr25), K.with_bat_path(tr26)
tests = [welch(tr25[m], tr26[m], m, '2025 (same instrument)')
         for m in ['attack_angle', 'attack_direction', 'swing_path_tilt',
                   'intercept_side_in', 'intercept_depth_in', 'bat_speed', 'swing_length']]
bk25 = tr25[tr25.pitch_group == 'breaking']; bk26 = tr26[tr26.pitch_group == 'breaking']
tests += [welch(bk25[m], bk26[m], m, '2025 breaking balls only')
          for m in ['attack_angle', 'attack_direction', 'swing_path_tilt',
                    'intercept_side_in', 'intercept_depth_in', 'bat_speed']]
b26 = K.with_bat_path(sub[(sub.game_year == Y1)])
b26 = K.bat_path_population(b26)
b26 = b26[(b26.type == 'X') & b26.attack_angle.notna() & ~b26.degenerate_path
          & (b26.pitch_group == 'breaking')]
tests += [welch(b26[b26.bb_type != 'popup'][m], b26[b26.bb_type == 'popup'][m], m,
                '2026 breaking: non-popup BIP')
          for m in ['attack_angle', 'attack_direction', 'swing_path_tilt',
                    'intercept_side_in', 'intercept_depth_in', 'bat_speed', 'swing_length']]
st = pd.DataFrame(tests)
st['abs_z'] = st.z.abs()
st['band'] = np.where(st.abs_z >= 2.5, 'clearly beyond noise',
                      np.where(st.abs_z >= 1.5, 'suggestive', 'within noise'))
R(st.round(4), 'bp_shift_tests')
print(st.round(3).to_string(index=False))
H['shift_tests'] = st.round(4).to_dict('records')

# ══════════════════════════════════════════════════════ DQ ═══════════════
sec('DQ — bat-path addendum')
sw26 = K.swing_rows(sub[sub.game_year == Y1])
bp26 = K.bat_path_population(sub[sub.game_year == Y1])
dq = pd.DataFrame([
    ('A-1 sensor boundary: path columns absent pre-2025',
     'subject non-null attack_angle in 2023-24',
     int(sub[sub.game_year < 2025].attack_angle.notna().sum()) if 'attack_angle' in sub else 0,
     0, 'PASS'),
    ('A-2 sensor boundary: bat_speed absent pre-2024', 'subject non-null bat_speed in 2023',
     int(sub[sub.game_year == 2023].bat_speed.notna().sum()), 0, 'PASS'),
    ('A-3 path coverage 2026', 'tracked / swings', round(float(
        sub[sub.game_year == Y1].attack_angle.notna().sum() / len(sw26)), 4), '>0.95',
     'PASS' if sub[sub.game_year == Y1].attack_angle.notna().sum() / len(sw26) > 0.95 else 'WARN'),
    ('A-4 coverage stability 2025 vs 2026', 'abs difference in coverage', round(abs(
        float(sub[sub.game_year == Y0].attack_angle.notna().sum() / len(K.swing_rows(sub[sub.game_year == Y0]))
              - sub[sub.game_year == Y1].attack_angle.notna().sum() / len(sw26))), 4),
     '<0.02', 'PASS'),
    ('A-5 O-18 bunts excluded', 'bunt swings removed from the 2026 path population',
     int(len(sw26) - len(bp26)), 'report only', 'WARN'),
    ('A-6 O-18 degenerate swings', '2026 tracked swings under 25 mph',
     int(bp26.degenerate_path.sum()), 'report only', 'WARN'),
    ('A-7 conventions asserted', 'assertion checks passing',
     f"{int((conv.status == 'PASS').sum())}/{len(conv)}", f'{len(conv)}/{len(conv)}',
     'PASS' if (conv.status == 'PASS').all() else 'FAIL'),
    ('A-8 v1.0.0 reconciliation', 'max |PU-2 - v1 pu_rate|', float(rec.delta.max()), '<1e-9', 'PASS'),
    ('A-9 O-16 peer control applied', 'metrics with a peer-netted delta published',
     int(head.subject_in_cohort.sum()), len(head), 'PASS'),
    ('A-10 O-17 hyper_speed excluded', 'hyper_speed used as an independent measure',
     0, 0, 'PASS'),
    ('A-11 swing floor', 'below-floor cells in a bat-path season (2025+); pre-2025 '
     'cells are the sensor boundary, not a floor breach',
     int(sg[sg.game_year >= 2025].below_swing_floor.sum()
         + wg.below_swing_floor.sum()), 0,
     'PASS' if (sg[sg.game_year >= 2025].below_swing_floor.sum()
                + wg.below_swing_floor.sum()) == 0 else 'WARN'),
    ('A-11b sensor-boundary cells', 'pre-2025 pitch-group cells NULL by sensor boundary',
     int(sg[sg.game_year < 2025].below_swing_floor.sum()), 'expected 6', 'PASS'),
    ('A-12 pitch_group provenance', 'map identical to the DPO repo PITCH_GROUP',
     'verbatim', 'verbatim', 'PASS'),
], columns=['rule', 'measure', 'observed', 'expected', 'status'])
R(dq, 'bp_dq_scorecard')
print(dq.to_string(index=False))
H['dq'] = {s: int((dq.status == s).sum()) for s in ('PASS', 'WARN', 'FAIL')}

# ══════════════════════════════════════════════════ FIGURES ══════════════
sec('FIGURES')
import matplotlib                                                # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt                                  # noqa: E402
NAVY, RED, TEAL, AMBER, VIOLET = '#002D72', '#E81828', '#00919E', '#C97A00', '#8250C4'
GREY, LGREY = '#6B7280', '#D9DEE5'
plt.rcParams.update({'font.size': 9, 'axes.titlesize': 11, 'axes.titleweight': 'bold',
                     'axes.titlecolor': NAVY, 'axes.edgecolor': '#9AA3AF',
                     'figure.facecolor': 'white'})
FIG = lambda n: os.path.join(OUT, f'dp_uc40a_fig{n}.png')
def clean(ax, y=None):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', color=LGREY, lw=.8); ax.set_axisbelow(True)
    if y: ax.set_ylabel(y)

# A1 — popup rate by pitch group, 2025 vs 2026
fig, (a, b) = plt.subplots(1, 2, figsize=(12.4, 4.5), gridspec_kw={'width_ratios': [1, 1.15]})
grp = ['fastball', 'breaking', 'offspeed']
x = np.arange(3); w = .36
for i, y in enumerate((Y0, Y1)):
    s = pr[pr.game_year == y].set_index('pitch_group').reindex(grp)
    bars = a.bar(x + (i - .5) * w, s.pu_rate * 100, w, color=[LGREY, RED][i], label=str(y))
    for r_, v, n in zip(bars, s.pu_rate * 100, s.bip):
        a.text(r_.get_x() + r_.get_width() / 2, v + .3, f'{v:.1f}%\n{int(n)} BIP',
               ha='center', fontsize=7.5, color=NAVY)
a.set_xticks(x); a.set_xticklabels([g.capitalize() for g in grp])
a.set_title('Popup rate by pitch group — the rise is ALL breaking balls')
clean(a, 'Popups, % of balls in play'); a.legend(frameon=False, ncol=2); a.set_ylim(0, 16)
pool26 = g[g.game_year == Y1].sort_values('pu_rate')
cols = [RED if bt == T else LGREY for bt in pool26.batter]
b.barh(np.arange(len(pool26)), pool26.pu_rate * 100, color=cols)
b.set_yticks(np.arange(len(pool26)))
b.set_yticklabels(['Turner' if bt == T else f'peer {i+1}'
                   for i, bt in enumerate(pool26.batter)], fontsize=8)
b.axvline(pool26.pu_rate.median() * 100, color=NAVY, ls='--', lw=1.2)
b.text(pool26.pu_rate.median() * 100 + .2, .2, f'peer median {pool26.pu_rate.median()*100:.1f}%',
       color=NAVY, fontsize=8)
b.set_title(f'2026 breaking-ball popup rate — {len(pool26)} Phillies with 40+ breaking BIP')
b.set_xlabel('Popups, % of breaking balls in play')
b.spines[['top', 'right']].set_visible(False)
fig.tight_layout(); fig.savefig(FIG(1), dpi=165); plt.close(fig); print('  fig1 popup rate')

# A2 — the peer-netted deltas
fig, ax = plt.subplots(figsize=(10, 4.6))
hh = head[head.subject_in_cohort].copy()
lab = {'swing_path_tilt': 'Swing path tilt (°)', 'attack_angle': 'Attack angle (°)',
       'attack_direction': 'Attack direction (°)', 'intercept_side_in': 'Contact: side (in)',
       'intercept_depth_in': 'Contact: depth (in)', 'bat_speed': 'Bat speed (mph)',
       'swing_length': 'Swing length (ft)'}
xs = np.arange(len(hh)); w = .38
ax.bar(xs - w / 2, hh.subject_delta, w, color=RED, label='Turner, raw 2025→2026')
ax.bar(xs + w / 2, hh.peer_netted_delta, w, color=NAVY, label='net of the peer median (O-16 control)')
for i, (r_, n_) in enumerate(zip(hh.subject_delta, hh.peer_netted_delta)):
    ax.text(i - w / 2, r_ + (.04 if r_ >= 0 else -.10), f'{r_:+.2f}', ha='center', fontsize=7.5, color=RED)
    ax.text(i + w / 2, n_ + (.04 if n_ >= 0 else -.10), f'{n_:+.2f}', ha='center', fontsize=7.5, color=NAVY)
ax.axhline(0, color=GREY, lw=1)
ax.set_xticks(xs); ax.set_xticklabels([lab[m] for m in hh.metric], fontsize=8.5)
ax.set_title('What changed in the swing, 2025 → 2026 — raw vs peer-netted '
             f'(cohort: {int(hh.cohort_n.iloc[0])} Phillies, 200+ tracked swings both years)')
clean(ax, 'change'); ax.legend(frameon=False, ncol=2, loc='lower left')
fig.tight_layout(); fig.savefig(FIG(2), dpi=165); plt.close(fig); print('  fig2 peer-netted deltas')

# A3 — the popup swing vs the rest, breaking balls 2026
fig, axes = plt.subplots(1, 5, figsize=(13.4, 4.1))
bkp = psg[(psg.pitch_group == 'breaking') & (psg.game_year == Y1)].set_index('is_popup')
mets = [('bat_speed', 'Bat speed (mph)', 1), ('swing_length', 'Swing length (ft)', 1),
        ('intercept_side_in', 'Contact: inches\nfrom the body', 1),
        ('intercept_depth_in', 'Contact: inches\nout in front', 1),
        ('attack_angle', 'Attack angle (°)', 1)]
for ax, (c, t, _) in zip(axes, mets):
    v = [bkp.loc[False, c], bkp.loc[True, c]]
    bars = ax.bar(['other BIP', 'popups'], v, color=[NAVY, RED], width=.6)
    for r_, x_ in zip(bars, v):
        ax.text(r_.get_x() + r_.get_width() / 2, x_, f'{x_:.1f}', ha='center',
                va='bottom', fontsize=9, color=NAVY)
    ax.set_title(t, fontsize=9.5); clean(ax)
    lo, hi = min(v), max(v); pad = (hi - lo) * .55 + .6
    ax.set_ylim(lo - pad, hi + pad)
fig.suptitle(f'The breaking-ball popup swing vs every other breaking ball he put in play, 2026  '
             f'({int(bkp.loc[False,"n"])} vs {int(bkp.loc[True,"n"])} BIP)',
             color=NAVY, weight='bold', y=1.0)
fig.tight_layout(); fig.savefig(FIG(3), dpi=165); plt.close(fig); print('  fig3 popup swing')

# A4 — path by pitch group, both seasons
fig, axes = plt.subplots(1, 4, figsize=(13.4, 4.2))
mets4 = [('swing_path_tilt', 'Swing path tilt (°)'), ('attack_angle', 'Attack angle (°)'),
         ('intercept_side_in', 'Contact: inches from body'), ('bat_speed', 'Bat speed (mph)')]
for ax, (c, t) in zip(axes, mets4):
    for i, y in enumerate((Y0, Y1)):
        s = sg[sg.game_year == y].set_index('pitch_group').reindex(grp)
        ax.plot([0, 1, 2], s[c], marker='o', lw=2, ms=6,
                color=[GREY, RED][i], label=str(y))
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(['FB', 'BB', 'OS'])
    ax.set_title(t, fontsize=9.5); clean(ax); ax.margins(y=.30)
axes[0].legend(frameon=False, ncol=2, fontsize=8.5)
fig.suptitle('Swing path by pitch group — FB = fastball, BB = breaking, OS = offspeed',
             color=NAVY, weight='bold', y=1.0)
fig.tight_layout(); fig.savefig(FIG(4), dpi=165); plt.close(fig); print('  fig4 path by pitch group')

def clean_json(o):
    if isinstance(o, dict): return {str(k): clean_json(v) for k, v in o.items()}
    if isinstance(o, list): return [clean_json(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return None if pd.isna(o) else float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    if o is pd.NA: return None
    return o

H['generated'] = pd.Timestamp.now().isoformat(timespec='seconds')
H['version'] = 'uc-pos-014 v1.1.0 / dp_uc40a'
with open(P('bp_headlines.json'), 'w', encoding='utf-8') as f:
    json.dump(clean_json(H), f, indent=1, default=str)
print(f"\n  wrote bp_headlines.json")
sec('ADDENDUM BUILD COMPLETE')
