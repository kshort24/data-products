"""Figures for UC #44. Every number traces to a receipt in out/."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
sys.path.insert(0, str(Path(__file__).parent)); import dp_uc44_kernel as K

OUT = Path(__file__).parent/'out'
RED, NAVY, BLUE = K.PHILLIES_RED, K.PHILLIES_NAVY, K.PHILLIES_BLUE
CARD = '#FBF7EE'; RULE = '#D8CFBC'; INK = '#1B1B1B'
plt.rcParams.update({'font.size':9,'axes.edgecolor':'#444','axes.labelcolor':'#222','figure.dpi':170,
                     'font.family':'DejaVu Sans'})

pay   = json.loads((OUT/'dp_uc44_payload.json').read_text())
loc   = pd.read_csv(OUT/'dp_uc44_pitch_locations_post.csv')
cen   = pd.read_csv(OUT/'dp_uc44_pitch_map_centroids.csv')
gr    = pd.read_csv(OUT/'dp_uc44_grades.csv')
grpre = pd.read_csv(OUT/'dp_uc44_grades_pre_option.csv')
plat  = pd.read_csv(OUT/'dp_uc44_platoon_splits.csv')
sl    = pd.read_csv(OUT/'dp_uc44_start_log.csv')
mbs   = pd.read_csv(OUT/'dp_uc44_mix_by_stand.csv')
ffl   = pd.read_csv(OUT/'dp_uc44_ff_location_profile.csv')
turn  = pd.read_csv(OUT/'dp_uc44_arsenal_turnover_detail.csv')
sc    = pd.read_csv(OUT/'dp_uc44_splitter_vs_changeup.csv')
SZT, SZB = 3.40, 1.58   # placeholder, overwritten below

# strike zone from the subject's own log (mean sz_top / sz_bot of the graded window)
import dp_uc44_kernel as _K
_ap = _K.load_phils((2026,), role='pitching')
_ap = _ap[(_ap.pitcher==_K.SUBJECT_ID) & (_ap.game_date>=_K.OPTION_RETURN_DATE)]
SZT, SZB = float(_ap.sz_top.mean()), float(_ap.sz_bot.mean())

def grade_color(g):
    if pd.isna(g): return '#B9B9B9'
    g = float(g)
    if g >= 60: return '#1a7f37'
    if g >= 55: return '#5FA052'
    if g >= 45: return '#8A8A8A'
    if g >= 40: return '#D08C2E'
    return RED

# ============================================================================
# FIG 1 — THE NOTECARD
# ============================================================================
fig = plt.figure(figsize=(11.6, 6.9))
fig.patch.set_facecolor(CARD)
gs = fig.add_gridspec(1, 2, width_ratios=[1.02, 1.0], left=0.045, right=0.968, top=0.845, bottom=0.075, wspace=0.13)

# ---- header
fig.text(0.045, 0.955, 'ANDREW PAINTER', fontsize=23, fontweight='bold', color=NAVY, va='top')
fig.text(0.045, 0.905, 'RHP · Phillies · at Atlanta, Game 3 · 2026-09-13   |   vs RHP Grant Holmes',
         fontsize=10.2, color='#4A4A4A', va='top')
ag = pay['arsenal_grade']
fig.text(0.968, 0.955, f"ARSENAL  {ag['value']:.0f}", fontsize=20, fontweight='bold',
         color=grade_color(ag['value']), ha='right', va='top')
fig.text(0.968, 0.908, f"20-80 scale · post-option window · {pay['meta']['grade_window'].split('(')[1][:-1]}",
         fontsize=8.2, color='#6A6A6A', ha='right', va='top')
fig.lines.append(plt.Line2D([0.045,0.968],[0.878,0.878], transform=fig.transFigure, color=RED, lw=2.2))

# ---- LEFT: pitch maps by stand
gsL = gs[0].subgridspec(2, 1, height_ratios=[1, 0.30], hspace=0.30)
gsM = gsL[0].subgridspec(1, 2, wspace=0.06)
axcall = fig.add_subplot(gsL[1]); axcall.axis('off')
for i, (st, lbl) in enumerate(zip(['L','R'], ['vs LHH', 'vs RHH'])):
    ax = fig.add_subplot(gsM[i]); ax.set_facecolor(CARD)
    d = loc[loc.stand==st]
    ax.add_patch(Rectangle((-0.83, SZB), 1.66, SZT-SZB, facecolor='#FF5733', alpha=0.13,
                           edgecolor='black', lw=1.0, zorder=1))
    for pn, g_ in d.groupby('pitch_name'):
        ax.scatter(g_.plate_x, g_.plate_z, s=9, alpha=0.28, zorder=2,
                   color=K.PITCH_COLORS.get(pn,'#999'), linewidths=0)
    c = cen[cen.stand==st].sort_values('usage', ascending=False).reset_index(drop=True)
    placed = []
    for _, r in c.iterrows():
        if r.usage < 0.02: continue
        px, pz = r.plate_x, r.plate_z
        for qx, qz in placed:                      # nudge apart colliding centroids
            if abs(px-qx) < 0.20 and abs(pz-qz) < 0.20:
                px += 0.26 if px >= qx else -0.26
        placed.append((px, pz))
        ax.scatter([px],[pz], s=120+2100*r.usage, zorder=5,
                   color=K.PITCH_COLORS.get(r.pitch_name,'#999'), edgecolors='#111', linewidths=1.3, alpha=0.93)
        ax.text(px, pz, r.pitch_type, ha='center', va='center',
                fontsize=7.4, fontweight='bold', color='white', zorder=6)
    ax.set_xlim(-2.05, 2.05); ax.set_ylim(0.6, 4.9)
    ax.set_xticks([]); ax.set_yticks([])
    for s_ in ax.spines.values(): s_.set_color(RULE)
    p_ = plat[(plat.window=='Post-Option') & (plat.stand==st)].iloc[0]
    ax.set_title(f'{lbl}   ·   {int(p_.pa)} PA', fontsize=10.5, color=NAVY, fontweight='bold', pad=6)
    xc = 0.25 + i*0.50
    axcall.text(xc, 0.90, f'{p_.xwoba:.3f}', transform=axcall.transAxes, ha='center', va='top',
                fontsize=21, fontweight='bold', color=NAVY)
    axcall.text(xc, 0.42, 'xwOBA ALLOWED', transform=axcall.transAxes, ha='center', va='top',
                fontsize=7.6, color='#8A8A8A', fontweight='bold')
    axcall.text(xc, 0.24, f'{p_.whiff_rate:.1%} whiff  ·  {p_.krate:.0%} K  ·  {p_.bbrate:.0%} BB',
                transform=axcall.transAxes, ha='center', va='top', fontsize=8.4, color='#4A4A4A')
axcall.plot([0.02,0.98],[0.99,0.99], color=RULE, lw=0.8, transform=axcall.transAxes)
axcall.text(0.5, -0.10, "Catcher's view — third base at left, so negative plate_x is inside to a RHH.\n"
                        "Bubble = mean location, sized by usage. Haze = every tracked pitch.",
            transform=axcall.transAxes, ha='center', va='top', fontsize=7.2, color='#8A8A8A', style='italic')

# ---- RIGHT: the pitch rail
axR = fig.add_subplot(gs[1]); axR.axis('off'); axR.set_facecolor(CARD)
axR.set_xlim(0,1); axR.set_ylim(0,1)
rail = gr.sort_values('n', ascending=False).reset_index(drop=True)
DESC = {
 'FF': ("High-Ride FF", "{velo:.0f} mph · {ivb:.1f}\" ride · {ab:.0%} above the zone"),
 'ST': ("Sweeper, now the co-primary", "{velo:.0f} mph · {hb:.1f}\" sweep · usage {u:.0%} (was 11%)"),
 'CH': ("NEW Changeup — replaced the splitter", "{velo:.0f} mph · {hb:.1f}\" run · xwOBA {xw:.3f}"),
 'SL': ("Slider, the righty put-away", "{velo:.0f} mph · {hb:.1f}\" · {izr:.0%} in zone"),
 'SI': ("Sinker, a strike, not a weapon", "{velo:.0f} mph · lands {izr:.0%} in zone · xwOBA {xw:.3f}"),
 'CU': ("Curveball, a show-me", "{velo:.0f} mph · below the grading floor (n={n})"),
}
ab = float(ffl[ffl.window=='Post-Option'].above_zone_rate.iloc[0])
axR.text(0.0, 0.985, 'THE ARSENAL', fontsize=10.5, fontweight='bold', color=NAVY, va='top')
axR.text(1.0, 0.985, 'STUFF   CMD   PITCH', fontsize=8.3, fontweight='bold', color='#7A7A7A',
         va='top', ha='right', family='monospace')
y = 0.905; ROW = 0.152
for _, r in rail.iterrows():
    ttl, sub = DESC.get(r.pitch_type, (r.pitch_name, '{velo:.0f} mph'))
    sub = sub.format(velo=r.velo, ivb=r.ivb_in, hb=abs(r.hb_in), u=r.usage, xw=r.xwoba,
                     izr=r.in_zone_rate, ab=ab, n=int(r.n))
    axR.add_patch(Rectangle((0.0, y-ROW+0.028), 0.012, ROW-0.042,
                            color=K.PITCH_COLORS.get(r.pitch_name,'#999'), transform=axR.transAxes))
    axR.text(0.028, y, ttl, fontsize=10.6, fontweight='bold', color=INK, va='top')
    axR.text(0.028, y-0.041, sub, fontsize=8.1, color='#5A5A5A', va='top')
    axR.text(0.028, y-0.079, f'{int(r.n)} thrown · {r.usage:.0%} usage · {r.whiff_rate:.1%} whiff on {int(r.swings)} swings',
             fontsize=7.3, color='#8A8A8A', va='top')
    for j, (col, val) in enumerate([('stuff', r.stuff_grade), ('cmd', r.command_grade), ('pitch', r.pitch_grade)]):
        x = 0.795 + j*0.076
        txt = '—' if pd.isna(val) else f'{val:.0f}'
        w = 0.062 if col=='pitch' else 0.052
        if col == 'pitch' and not pd.isna(val):
            axR.add_patch(FancyBboxPatch((x-0.030, y-0.062), 0.070, 0.058,
                          boxstyle='round,pad=0.004,rounding_size=0.012',
                          facecolor=grade_color(val), edgecolor='none', transform=axR.transAxes))
            axR.text(x+0.005, y-0.033, txt, fontsize=13.5, fontweight='bold', color='white',
                     ha='center', va='center')
        else:
            axR.text(x, y-0.033, txt, fontsize=11.5, fontweight='bold',
                     color=grade_color(val), ha='center', va='center')
    axR.plot([0.0,1.0],[y-ROW+0.022]*2, color=RULE, lw=0.8, transform=axR.transAxes)
    y -= ROW
axR.text(0.0, y+0.006, '50 = major-league average · 10 points = 1 SD · population = RHP pitcher-seasons\n'
                       'in the Phillies game log, 2015-2026, ≥100 of that pitch (sweeper ≥50, thin)',
         fontsize=7.2, color='#7A7A7A', va='top', style='italic')
fig.savefig(OUT/'dp_uc44_fig1_notecard.png', bbox_inches='tight', facecolor=CARD)
plt.close(fig); print('fig1 notecard')

# ============================================================================
# FIG 2 — the arsenal he retired vs the one he brought back
# ============================================================================
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.3), gridspec_kw={'width_ratios':[1.25,1]})
t = turn.sort_values('after_usage', ascending=True)
yy = np.arange(len(t))
a1.barh(yy-0.19, t.before_usage, height=0.36, color='#B9C0CC', edgecolor='#8A93A3', label='Pre-option (14 GS, through 06-17)')
a1.barh(yy+0.19, t.after_usage,  height=0.36, color=NAVY,      edgecolor='#001A44', label='Post-option (8 GS, 07-31 →)')
for i, r in enumerate(t.itertuples()):
    if r.status != 'CARRIED':
        a1.text(max(r.before_usage, r.after_usage)+0.012, i, r.status, va='center',
                fontsize=8.2, fontweight='bold', color=RED if r.status=='DROPPED' else '#1a7f37')
a1.set_yticks(yy); a1.set_yticklabels(t.pitch_type, fontsize=9.5)
a1.set_xlabel('share of pitches in the window'); a1.set_xlim(0, 0.44)
a1.legend(fontsize=8, frameon=False, loc='lower right')
a1.grid(axis='x', color='#EEE', zorder=0); a1.set_axisbelow(True)
a1.set_title(f"AR-1 arsenal turnover index = {pay['turnover']['index']:.2f}",
             fontsize=10.5, color=NAVY, fontweight='bold', loc='left')

lab = ['whiff rate\n(all hitters)','whiff rate\nvs LHH','xwOBA\nallowed','in-zone\nrate']
fs_, ch_ = sc.iloc[0], sc.iloc[1]
v1 = [fs_.whiff_rate, fs_.whiff_vs_lhb, fs_.xwoba, fs_.in_zone_rate]
v2 = [ch_.whiff_rate, ch_.whiff_vs_lhb, ch_.xwoba, ch_.in_zone_rate]
x = np.arange(4)
a2.bar(x-0.19, v1, width=0.36, color='#3BACAC', edgecolor='#2A8080', label='FS — splitter (pre)')
a2.bar(x+0.19, v2, width=0.36, color='#1DBE3A', edgecolor='#128A28', label='CH — changeup (post)')
for xi, (p_, q_) in enumerate(zip(v1, v2)):
    a2.text(xi-0.19, p_+0.011, f'{p_:.3f}', ha='center', fontsize=7.8, color='#333')
    a2.text(xi+0.19, q_+0.011, f'{q_:.3f}', ha='center', fontsize=7.8, color='#333')
a2.set_xticks(x); a2.set_xticklabels(lab, fontsize=8.2); a2.set_ylim(0, 0.56)
a2.legend(fontsize=8, frameon=False, loc='upper right')
a2.grid(axis='y', color='#EEE', zorder=0); a2.set_axisbelow(True)
zl, pl = pay['fs_vs_ch']['z_lhb'], pay['fs_vs_ch']['p_lhb']
a2.set_title(f'The pitch that replaced the pitch   (LHH whiff gap: z={zl:.2f}, p={pl:.2f} — not significant)',
             fontsize=9.4, color=NAVY, fontweight='bold', loc='left')
fig.suptitle('The splitter is gone. What came back is not the same pitch — and is not worse.',
             fontsize=12.4, color=NAVY, fontweight='bold', y=1.015, x=0.02, ha='left')
fig.tight_layout(); fig.savefig(OUT/'dp_uc44_fig2_arsenal_turnover.png', bbox_inches='tight')
plt.close(fig); print('fig2 turnover')

# ============================================================================
# FIG 3 — grade rail, pre vs post
# ============================================================================
m = grpre[['pitch_type','pitch_grade','usage']].rename(columns={'pitch_grade':'pre','usage':'u_pre'}).merge(
    gr[['pitch_type','pitch_grade','usage']].rename(columns={'pitch_grade':'post','usage':'u_post'}),
    on='pitch_type', how='outer')
m['order'] = m[['u_pre','u_post']].max(axis=1)
m = m.sort_values('order')
fig, ax = plt.subplots(figsize=(8.6, 4.4))
yy = np.arange(len(m))
for i, r in enumerate(m.itertuples()):
    if not (pd.isna(r.pre) or pd.isna(r.post)):
        ax.annotate('', xy=(r.post, i), xytext=(r.pre, i),
                    arrowprops=dict(arrowstyle='-|>', color='#9AA3B2', lw=1.6, shrinkA=6, shrinkB=6))
    if not pd.isna(r.pre):
        ax.scatter(r.pre, i, s=155, color='#B9C0CC', edgecolors='#8A93A3', zorder=4)
        ax.text(r.pre, i, f'{r.pre:.0f}', ha='center', va='center', fontsize=7.6, color='#333', zorder=5)
    if not pd.isna(r.post):
        ax.scatter(r.post, i, s=175, color=grade_color(r.post), edgecolors='#222', zorder=4)
        ax.text(r.post, i, f'{r.post:.0f}', ha='center', va='center', fontsize=7.8, color='white',
                fontweight='bold', zorder=5)
    else:
        ax.text(r.pre+3, i, 'retired', fontsize=8, color=RED, va='center', style='italic')
ax.axvline(50, color='#888', lw=1.0, ls='--'); ax.text(50.3, len(m)-0.35, '50 = MLB average', fontsize=7.6, color='#777')
ax.set_yticks(yy); ax.set_yticklabels(m.pitch_type, fontsize=10)
ax.set_xlim(28, 68); ax.set_xlabel('SG-4 pitch grade (20-80)')
ax.grid(axis='x', color='#F0F0F0'); ax.set_axisbelow(True)
ax.set_title('Pitch-by-pitch, before the option and after\n'
             f"arsenal grade {np.average(grpre.dropna(subset=['pitch_grade']).pitch_grade, weights=grpre.dropna(subset=['pitch_grade']).usage):.0f}"
             f" → {pay['arsenal_grade']['value']:.0f}",
             fontsize=11.5, color=NAVY, fontweight='bold', loc='left')
fig.tight_layout(); fig.savefig(OUT/'dp_uc44_fig3_grade_shift.png', bbox_inches='tight')
plt.close(fig); print('fig3 grade shift')

# ============================================================================
# FIG 4 — the four-seam trade: elevation bought whiffs and cost strikes
# ============================================================================
allp = K.load_phils(tuple(range(2015,2027)), regular_only=True)
d = allp[(allp.p_throws=='R') & (allp.pitch_type=='FF')].copy()
d['_sw'] = d.description.isin(K.SWINGS); d['_wh'] = d.description.isin(K.WHIFFS); d['_iz'] = d.zone<=9
p = d.groupby(['game_year','pitcher'], as_index=False).agg(
    n=('pitch_number','size'), sw=('_sw','sum'), wh=('_wh','sum'), iz=('_iz','sum'))
p = p[p.n>=100]; p['whiff']=p.wh/p.sw; p['izr']=p.iz/p.n
fig, ax = plt.subplots(figsize=(7.8, 5.4))
ax.scatter(p.izr, p.whiff, s=16, color='#C9CEd8', edgecolors='none', zorder=2, label=f'RHP pitcher-seasons, ≥100 FF (n={len(p)})')
pre = gr_pre_ff = grpre[grpre.pitch_type=='FF'].iloc[0]; post = gr[gr.pitch_type=='FF'].iloc[0]
ax.annotate('', xy=(post.in_zone_rate, post.whiff_rate), xytext=(pre.in_zone_rate, pre.whiff_rate),
            arrowprops=dict(arrowstyle='-|>', color=RED, lw=2.2, shrinkA=9, shrinkB=9), zorder=5)
ax.scatter([pre.in_zone_rate],[pre.whiff_rate], s=190, color='white', edgecolors=RED, linewidths=2.2, zorder=6)
ax.scatter([post.in_zone_rate],[post.whiff_rate], s=210, color=RED, edgecolors='#7A0A14', linewidths=1.6, zorder=6)
ax.text(pre.in_zone_rate+0.007, pre.whiff_rate-0.012, 'pre-option\n.474 zone / .106 whiff', fontsize=8.4, color='#8A2A34')
ax.text(post.in_zone_rate-0.075, post.whiff_rate+0.012, 'post-option\n.422 zone / .218 whiff', fontsize=8.4, color=RED, fontweight='bold')
ax.axvline(p.izr.mean(), color='#AAA', lw=0.9, ls=':'); ax.axhline(p.whiff.mean(), color='#AAA', lw=0.9, ls=':')
ax.text(p.izr.mean()+0.004, 0.045, 'population mean zone rate', fontsize=7.2, color='#888', rotation=90)
ax.text(0.30, p.whiff.mean()+0.005, 'population mean whiff rate', fontsize=7.2, color='#888')
ax.set_xlabel('four-seam in-zone rate'); ax.set_ylabel('four-seam whiff rate (whiffs / swings)')
ax.set_xlim(0.30, 0.70); ax.set_ylim(0.03, 0.46)
ax.legend(fontsize=8, frameon=False, loc='upper right')
ax.grid(color='#F3F3F3'); ax.set_axisbelow(True)
ax.set_title('Painter moved the four-seam up. It bought a full grade of swing-and-miss\n'
             'and cost a grade and a half of zone.', fontsize=11.5, color=NAVY, fontweight='bold', loc='left')
fig.tight_layout(); fig.savefig(OUT/'dp_uc44_fig4_ff_trade.png', bbox_inches='tight')
plt.close(fig); print('fig4 ff trade')

# ============================================================================
# FIG 5 — eight starts back: process held, results did not
# ============================================================================
post_sl = sl[sl.window=='Post-Option'].reset_index(drop=True)
fig, ax = plt.subplots(figsize=(9.6, 4.4))
x = np.arange(len(post_sl))
ax.bar(x, post_sl.xwoba, color=[RED if v>=0.40 else '#B9C0CC' for v in post_sl.xwoba],
       edgecolor='#8A93A3', width=0.56, zorder=3, label='xwOBA allowed (per PA)')
ax2 = ax.twinx()
ax2.plot(x, post_sl.csw, color=NAVY, marker='o', lw=2.0, ms=6, zorder=5, label='CSW% (called + whiffs / pitches)')
ax2.set_ylim(0.18, 0.40); ax2.set_ylabel('CSW%', color=NAVY)
for xi, r in zip(x, post_sl.itertuples()):
    ax.text(xi, r.xwoba+0.008, f'{r.xwoba:.3f}', ha='center', fontsize=7.4, color='#444')
    ax2.text(xi, r.csw+0.012, f'{r.csw:.0%}', ha='center', fontsize=7.2, color=NAVY)
ax.set_xticks(x); ax.set_xticklabels([f'{r.game_date[5:]}\n{r.opponent} ({r.home_away})\n{int(r.bf)} BF'
                                      for r in post_sl.itertuples()], fontsize=7.8)
ax.set_ylim(0, 0.56); ax.set_ylabel('xwOBA allowed')
ax.grid(axis='y', color='#F2F2F2'); ax.set_axisbelow(True)
h1,l1 = ax.get_legend_handles_labels(); h2,l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, fontsize=8, frameon=False, loc='upper left')
_u400 = int((post_sl.xwoba < 0.400).sum())
_multi = post_sl[post_sl.hr >= 2]
assert set(_multi.game_date) == set(post_sl[post_sl.xwoba >= 0.400].game_date), 'title claim no longer holds'
ax.set_title(f'Eight starts back. {_u400} of 8 under .400 xwOBA — and the two that were not '
             f'are the only two with multiple home runs.',
             fontsize=11.3, color=NAVY, fontweight='bold', loc='left')
fig.tight_layout(); fig.savefig(OUT/'dp_uc44_fig5_start_log.png', bbox_inches='tight')
plt.close(fig); print('fig5 start log')
print('\nFIGURES COMPLETE')
