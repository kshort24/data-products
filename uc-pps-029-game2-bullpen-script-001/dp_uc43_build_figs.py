"""Figures for UC #43. Every number traces to a receipt in out/."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, str(Path(__file__).parent)); import dp_uc43_kernel as K
OUT = Path(__file__).parent/'out'
RED, NAVY = K.PHILLIES_RED, K.PHILLIES_NAVY
TIER = {'GREEN':'#1DBE3A','AMBER':'#FE9D00','RED':'#D22D49'}
plt.rcParams.update({'font.size':9,'axes.edgecolor':'#444','axes.labelcolor':'#222','figure.dpi':150})

# ---- FIG 1: Holman pitch maps by batter handedness (the client's own chart) ----
h = pd.read_csv(OUT/'dp_uc43_holman_pitch_extract.csv')
mix = pd.read_csv(OUT/'dp_uc43_holman_mix_by_stand.csv')
sz_top, sz_bot = h.sz_top.mean(), h.sz_bot.mean()
fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.6), sharex=True, sharey=True)
for ax, st, lbl in zip(axes, ['L','R'], ['vs LHH','vs RHH']):
    d = h[h.stand==st]
    ax.add_patch(Rectangle((-0.83, sz_bot), 1.66, sz_top-sz_bot, fill=True, facecolor='#FF5733',
                           alpha=0.15, edgecolor='black', lw=1, zorder=1))
    for pn, grp in d.groupby('pitch_name'):
        ax.scatter(grp.plate_x, grp.plate_z, s=26, alpha=0.72, zorder=3,
                   color=K.PITCH_COLORS.get(pn, '#999999'), edgecolors='white', linewidths=0.4, label=pn)
    m = mix[mix.stand==st]
    for _, r in m.iterrows():
        ax.scatter([r.plate_x],[r.plate_z], s=330, zorder=5, marker='o',
                   color=K.PITCH_COLORS.get(r.pitch_name,'#999'), edgecolors='#111', linewidths=1.4)
        ax.text(r.plate_x, r.plate_z, r.pitch_type, ha='center', va='center', fontsize=7.5,
                fontweight='bold', color='white', zorder=6)
    ax.set_title(f'{lbl}  (n={len(d)})', fontsize=10, color=NAVY, fontweight='bold')
    ax.set_xlim(-2.2, 2.2); ax.set_ylim(0.2, 5.0); ax.set_xlabel('plate_x (ft, catcher view)')
    ax.axhline(0, color='#bbb', lw=0.6)
axes[0].set_ylabel('plate_z (ft)')
axes[1].legend(loc='upper right', fontsize=7.5, frameon=True, framealpha=0.95)
fig.suptitle('Grant Holman — 2026 Lehigh Valley pitch locations, by batter handedness',
             fontsize=12, color=NAVY, fontweight='bold', y=0.99)
fig.text(0.5, 0.005, 'Large labelled markers = mean location of each pitch type. Strike zone = league ±0.83 ft × mean sz_bot/sz_top for this pitcher.',
         ha='center', fontsize=7, color='#666')
fig.tight_layout(rect=[0,0.02,1,0.95]); fig.savefig(OUT/'dp_uc43_fig1_holman_pitch_maps.png', bbox_inches='tight'); plt.close(fig)

# ---- FIG 2: availability ledger, both date framings ----
a1 = pd.read_csv(OUT/'dp_uc43_availability_D1.csv'); a2 = pd.read_csv(OUT/'dp_uc43_availability_D2.csv')
order = ['Mayza, Tim','Holman, Grant','Raley, Brooks','Shugart, Chase','Kerkering, Orion',
         'Alvarado, José','Duran, Jhoan','McFarlane, Alex','Bowlan, Jonathan']
fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2), sharey=True)
for ax, a, ttl in zip(axes, [a1, a2], ['Target D+1 · 2026-09-12  (operating premise)','Target D+2 · 2026-09-13  (session-date framing)']):
    a = a.set_index('player_name').loc[order].reset_index()
    y = np.arange(len(a))[::-1]
    ax.barh(y, a.pitches_last_7d, color=[TIER[t] for t in a.tier], edgecolor='#333', height=0.62)
    for yy, (_, r) in zip(y, a.iterrows()):
        ax.text(r.pitches_last_7d+1.2, yy, f"{int(r.pitches_last_7d)}p / {int(r.appearances_last_7d)}app",
                va='center', fontsize=7.6, color='#333')
    ax.set_yticks(y); ax.set_yticklabels(a.player_name, fontsize=8.5)
    ax.set_xlim(0, 78); ax.set_xlabel('pitches thrown in the 7 days before the target game')
    ax.set_title(ttl, fontsize=9.5, color=NAVY, fontweight='bold')
    ax.grid(axis='x', color='#eee', zorder=0)
h_ = [plt.Rectangle((0,0),1,1,color=TIER[k]) for k in ['GREEN','AMBER','RED']]
fig.legend(h_, ['GREEN  available','AMBER  use with care','RED  do not use'], fontsize=8, ncol=3, loc='lower center', frameon=False, bbox_to_anchor=(0.5, -0.01))
fig.suptitle('BS-1 · Bullpen availability, and how much it depends on which night "last night" was',
             fontsize=11.5, color=NAVY, fontweight='bold')
fig.tight_layout(rect=[0,0.06,1,0.93]); fig.savefig(OUT/'dp_uc43_fig2_availability.png', bbox_inches='tight'); plt.close(fig)

# ---- FIG 3: BS-2 coverage, both capacity modes ----
cov = pd.read_csv(OUT/'dp_uc43_script_coverage.csv'); cov = cov[cov.arm!='— TOTAL —']
pay = json.loads((OUT/'dp_uc43_payload.json').read_text())
cs = pay['coverage']; CM = pay['capacity_modes']
fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.8, 4.2), gridspec_kw={'width_ratios':[1.45,1]})
y = np.arange(len(cov))[::-1]
axL.barh(y, cov.bf_needed_by_script, color='#dfe3ea', edgecolor='#9aa3b2', height=0.62, label='batters the script needs')
axL.barh(y, cov.bf_expected, color=NAVY, height=0.34, label='batters his average outing delivers')
for yy,(_,r) in zip(y, cov.iterrows()):
    axL.text(r.bf_needed_by_script+0.25, yy, f"{r.gap_bf:+.1f}", va='center', fontsize=8,
             color=RED if r.gap_bf>0 else '#1a7f37', fontweight='bold')
axL.set_yticks(y); axL.set_yticklabels([f"{a}  ({int(n)} inn)" for a,n in zip(cov.arm, cov.innings_scripted)], fontsize=8.5)
axL.set_xlabel('batters faced'); axL.set_xlim(0, 7.0)
axL.legend(fontsize=7.5, loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False)
axL.set_title('Per arm: what the script asks vs. what he averages', fontsize=9.5, color=NAVY, fontweight='bold')
axL.grid(axis='x', color='#eee', zorder=0)

labels = ['yours\navg outing','yours\nall at max','revised\nall at max']
vals   = [CM['client_average']['total'], CM['client_ceiling']['total'], CM['revised_ceiling']['total']]
cols   = [RED, '#7d8ba6', NAVY]
need   = cs['required_bf_median_regulation_game']
bars = axR.bar(labels, vals, color=cols, edgecolor='#333', width=0.6)
for b_, v in zip(bars, vals):
    axR.text(b_.get_x()+b_.get_width()/2, v-2.6, f'{v:.1f}', ha='center', fontweight='bold', fontsize=9.5, color='white')
axR.axhline(need, color=RED, lw=1.6, ls='--')
axR.text(-0.42, need+1.1, f'{need:.0f} BF needed for a regulation nine', color=RED, fontsize=7.8, ha='left', fontweight='bold')
axR.set_ylim(0, 43); axR.set_ylabel('batters faced'); axR.tick_params(axis='x', labelsize=8.0)
axR.set_title(f"Capacity vs. a regulation nine\n(median of {cs['regulation_games_in_benchmark']} games, 2026)",
              fontsize=9.5, color=NAVY, fontweight='bold')
axR.grid(axis='y', color='#eee', zorder=0)
fig.suptitle('BS-2 · The script is not short so much as ceiling-dependent', fontsize=11.5, color=NAVY, fontweight='bold')
fig.tight_layout(rect=[0,0.03,1,0.92]); fig.savefig(OUT/'dp_uc43_fig3_coverage.png', bbox_inches='tight'); plt.close(fig)

# ---- FIG 4: BS-3 multi-inning propensity ----
mip = pd.read_csv(OUT/'dp_uc43_multi_inning_propensity.csv').dropna(subset=['multi_inning_rate'])
mip = mip.sort_values('multi_inning_rate')
fig, ax = plt.subplots(figsize=(7.6, 3.9))
cols = ['#3BACAC' if t.startswith('AAA') else NAVY for t in mip.evidence_tier]
bars = ax.barh(mip.player_name, mip.multi_inning_rate, color=cols, edgecolor='#333', height=0.6)
for b,(_,r) in zip(bars, mip.iterrows()):
    ax.text(r.multi_inning_rate+0.008, b.get_y()+b.get_height()/2,
            f"{int(r.multi_inning_apps)}/{int(r.relief_apps)}", va='center', fontsize=7.8, color='#333')
NOTE = {'Duran, Jhoan': "← the client's pick to go multiple",
        'Shugart, Chase': "← the pen's actual length arm",
        'Holman, Grant': "← debutant, AAA evidence only"}
for i, (_, r) in enumerate(mip.iterrows()):
    if r.player_name in NOTE:
        ax.text(0.475, i, NOTE[r.player_name], va='center', fontsize=7.8, color=RED, fontweight='bold')
ax.set_xlim(0, 0.80); ax.set_xlabel('share of relief outings spanning ≥ 2 innings (2026)')
ax.set_title('BS-3 · Who actually stretches', fontsize=11, color=NAVY, fontweight='bold', loc='left')
fig.text(0.02, 0.005, 'Teal = AAA supporting tier (Holman). Navy = 2026 MLB relief log. Labels: multi-inning outings / total relief outings.', fontsize=7.0, color='#666')
ax.grid(axis='x', color='#eee', zorder=0)
fig.tight_layout(rect=[0,0.05,1,1]); fig.savefig(OUT/'dp_uc43_fig4_multi_inning.png', bbox_inches='tight'); plt.close(fig)
print('figures written:', sorted(p.name for p in OUT.glob('dp_uc43_fig*.png')))
