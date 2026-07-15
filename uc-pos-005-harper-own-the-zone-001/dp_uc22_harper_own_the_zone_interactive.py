"""
uc-pos-005 / dp_uc22 — interactive consumable builder.
Assembles the branded single-file HTML from the out/ receipts (no raw
recompute here — consumables read certified receipts only).
Output: dp_uc22_harper_own_the_zone_interactive.html (repo root).
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

MLB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT = MLB / "out"
STEM = "dp_uc22_harper_own_the_zone"
RED, NAVY, CREAM, GRAY, LGRAY = '#E81828', '#002D72', '#F3E5AB', '#8C8C8C', '#D9D9D9'
DARK_BG, PANEL = '#0E1117', '#161B24'

def styled(fig, title, sub=None, h=460):
    fig.update_layout(
        template='plotly_dark', paper_bgcolor=PANEL, plot_bgcolor=PANEL,
        font=dict(family='Arial, sans-serif', size=13, color='#E6E6E6'),
        title=dict(text=title + (f"<br><sup style='color:#9AA4B2'>{sub}</sup>" if sub else ''),
                   font=dict(size=17, color=CREAM)),
        height=h, margin=dict(t=90, l=60, r=30, b=50), legend=dict(orientation='h', y=-0.15))
    return fig

def zone_shapes(sz_bot, sz_top, per_col=True):
    shp = []
    for band, op in [(0.25, 0.18), (0.0, 0.55)]:
        shp.append(dict(type='rect', x0=-0.83-band, x1=0.83+band,
                        y0=sz_bot-band, y1=sz_top+band,
                        line=dict(color=CREAM if band == 0 else GRAY, width=1.4 if band == 0 else 1, dash='solid' if band == 0 else 'dot'),
                        opacity=op, row='all', col='all') if per_col else None)
    return [s for s in shp if s]

# ---------------------------------------------------------------- load ----
res  = pd.read_csv(OUT/f'{STEM}_results_by_season.csv')
disc = pd.read_csv(OUT/f'{STEM}_discipline_by_season.csv')
bb   = pd.read_csv(OUT/f'{STEM}_battedball_by_season.csv')
bpg  = pd.read_csv(OUT/f'{STEM}_battedball_by_pitchgroup.csv')
oz   = pd.read_csv(OUT/f'{STEM}_oz_kpis_by_season.csv')
plat = pd.read_csv(OUT/f'{STEM}_platoon_results.csv')
platb= pd.read_csv(OUT/f'{STEM}_platoon_battedball.csv')
mo   = pd.read_csv(OUT/f'{STEM}_2026_monthly.csv')
band = pd.read_csv(OUT/f'{STEM}_2026_shadow_band_pitchlog.csv')
rp   = pd.read_csv(OUT/f'{STEM}_region_profile_by_season.csv')
lab  = lambda s: s.astype(str).str.replace('2026', '2026·1H')

figs = []

# --- Fig 1: the shadow band, pitch by pitch --------------------------------
b = band.copy()
b['what'] = b.outcome.map({'take': 'Take', 'xbh': 'Extra-base hit', 'single': 'Single',
                           'swing_other': 'Other swing'})
f = px.scatter(b, x='plate_x', y='plate_z', facet_col='p_throws',
               color='what',
               color_discrete_map={'Take': GRAY, 'Extra-base hit': RED,
                                   'Single': CREAM, 'Other swing': '#3D7EBF'},
               category_orders={'what': ['Take','Other swing','Single','Extra-base hit'],
                                'p_throws': ['L','R']},
               hover_data=['game_date','pitch_name','description','events','balls','strikes',
                           'launch_speed','release_speed'],
               labels={'plate_x': 'Plate x (ft)', 'plate_z': 'Plate z (ft)', 'what': '',
                       'p_throws': 'Pitcher throws'})
szb, szt = band.sz_bot.mean(), band.sz_top.mean()
for bandw, col, dash, op in [(0.25, GRAY, 'dot', 0.9), (0.0, CREAM, 'solid', 0.9)]:
    f.add_shape(type='rect', x0=-0.83-bandw, x1=0.83+bandw, y0=szb-bandw, y1=szt+bandw,
                line=dict(color=col, width=1.5, dash=dash), opacity=op, row='all', col='all')
f.add_annotation(x=0, y=(szb+szt)/2, text='ZONE', showarrow=False,
                 font=dict(color=CREAM, size=11), opacity=0.5, row='all', col='all')
f.update_traces(marker=dict(size=8, opacity=0.85))
f.update_traces(selector=dict(name='Extra-base hit'), marker=dict(size=13, symbol='star'))
f.update_traces(selector=dict(name='Take'), marker=dict(size=6, opacity=0.45))
f.update_yaxes(scaleanchor='x', scaleratio=1)
figs.append(styled(f, 'Every 2026 pitch on the edge — 564 decisions in the shadow band',
                   'Dotted line = one ball width (0.25 ft) around the rulebook zone. Takes fade back; damage stars forward.', h=560))

# --- Fig 2: OZ family trends ------------------------------------------------
f = go.Figure()
x = lab(oz.season)
f.add_trace(go.Scatter(x=x, y=oz.oz1_shadow_out_take, name='OZ-1 shadow-out take rate',
                       mode='lines+markers', line=dict(color=CREAM, width=3)))
f.add_trace(go.Scatter(x=x, y=oz.oz2_shadow_in_attack, name='OZ-2 shadow-in attack rate',
                       mode='lines+markers', line=dict(color=RED, width=3)))
f.add_trace(go.Scatter(x=x, y=oz.oz3_edge_decision_diff, name='OZ-3 edge decision differential',
                       mode='lines+markers', line=dict(color=GRAY, width=2, dash='dot')))
figs.append(styled(f, 'Owning the edge, 2019–2026', 'Take the borderline ball (OZ-1 up), and swing at borderline strikes only when they are worth it (OZ-2 down, quality up — see damage panel).'))

# --- Fig 3: damage — barrels overall and on the edge ------------------------
f = make_subplots(rows=1, cols=2, subplot_titles=('All batted balls', 'Shadow-in swings only'))
f.add_trace(go.Bar(x=lab(bb.season), y=bb.barrel_rate, name='Barrel%', marker_color=RED), 1, 1)
f.add_trace(go.Scatter(x=lab(bb.season), y=bb.xwoba_con, name='xwOBAcon', mode='lines+markers',
                       line=dict(color=CREAM, width=2.5)), 1, 1)
f.add_trace(go.Bar(x=lab(oz.season), y=oz.oz4_shadow_in_barrel, name='OZ-4 barrel% (edge)',
                   marker_color=NAVY, marker_line=dict(color=RED, width=1.5)), 1, 2)
f.add_trace(go.Scatter(x=lab(oz.season), y=oz.oz4_shadow_in_xwobacon, name='OZ-4 xwOBAcon (edge)',
                       mode='lines+markers', line=dict(color=CREAM, width=2.5, dash='dot')), 1, 2)
figs.append(styled(f, 'Punishing what creeps in', 'Overall barrel rate is off the 2021 peak — but edge-pitch damage is the best since 2021.'))

# --- Fig 4: barrels by pitch group ------------------------------------------
f = px.line(bpg, x='season', y='barrel_rate', color='pitch_group', markers=True,
            color_discrete_map={'fastball': RED, 'breaking': '#3D7EBF', 'offspeed': CREAM},
            labels={'barrel_rate': 'Barrel%', 'season': '', 'pitch_group': ''})
figs.append(styled(f, 'Barrel% by pitch group — the profile inverted',
                   '2026: best breaking-ball barrel rate since 2021; career-tenure low vs fastballs.'))

# --- Fig 5: platoon ----------------------------------------------------------
f = make_subplots(rows=1, cols=2, subplot_titles=('wOBA by season', 'Barrel% by season'))
for hand, col in [('L', '#3D7EBF'), ('R', RED)]:
    pl = plat[plat.p_throws == hand]
    pb = platb[platb.p_throws == hand]
    f.add_trace(go.Scatter(x=lab(pl.season), y=pl.woba, name=f'vs {hand}HP',
                           mode='lines+markers', line=dict(color=col, width=3)), 1, 1)
    f.add_trace(go.Scatter(x=lab(pb.season), y=pb.barrel_rate, name=f'vs {hand}HP barrel',
                           mode='lines+markers', showlegend=False,
                           line=dict(color=col, width=2, dash='dot')), 1, 2)
figs.append(styled(f, 'Platoon splits — the 2026 watch item',
                   'Elite vs RHP (.418 wOBA, 17 HR). vs LHP: .292 wOBA, 88.0 avg EV — the softest of the tenure.'))

# --- Fig 6: 2026 monthly ------------------------------------------------------
f = go.Figure()
f.add_trace(go.Bar(x=mo.month, y=mo.hrs, name='HR', marker_color=RED, opacity=0.75, yaxis='y2'))
f.add_trace(go.Scatter(x=mo.month, y=mo.woba, name='wOBA', mode='lines+markers',
                       line=dict(color=CREAM, width=3)))
f.add_trace(go.Scatter(x=mo.month, y=mo.xwoba, name='xwOBA (BIP proxy)', mode='lines+markers',
                       line=dict(color=GRAY, width=2, dash='dot')))
f.update_layout(yaxis2=dict(overlaying='y', side='right', title='HR', showgrid=False))
figs.append(styled(f, '2026 month by month', 'April–June: .376–.420 wOBA. Early July cooldown into the break (48 PA).'))

# ------------------------------------------------------------- assemble ----
r26 = res[res.season == 2026].iloc[0]
o26 = oz[oz.season == 2026].iloc[0]
d26 = disc[disc.season == 2026].iloc[0]
cards = [
    ('.260/.360/.497', 'AVG / OBP / SLG', f"{int(r26.plate_apps)} PA · 20 HR"),
    (f"{r26.woba:.3f}", 'wOBA', f"xwOBA {r26.xwoba:.3f}"),
    (f"{r26.bbrate*100:.1f}%", 'walk rate', 'best since 2020'),
    (f"{o26.oz1_shadow_out_take*100:.1f}%", 'OZ-1 edge take rate', 'best since 2021'),
    (f"{o26.oz4_shadow_in_xwobacon:.3f}", 'OZ-4 edge xwOBAcon', 'up from .361 / .406'),
    (f"{d26.chase_rate*100:.1f}%", 'chase rate', 'vs 35.6% in 2025'),
]
card_html = ''.join(
    f"<div class='card'><div class='big'>{v}</div><div class='k'>{k}</div><div class='s'>{s}</div></div>"
    for v, k, s in cards)
body = ''.join(f"<div class='panel'>{f.to_html(full_html=False, include_plotlyjs=False, config={'displaylogo': False})}</div>"
               for f in figs)

html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<title>Bryce Harper — Own the Zone · 2026 First Half</title>
<script src='https://cdn.plot.ly/plotly-2.32.0.min.js'></script>
<style>
 body {{ background:{DARK_BG}; color:#E6E6E6; font-family: Arial, Helvetica, sans-serif; margin:0; }}
 .hero {{ background: linear-gradient(135deg, {NAVY} 0%, #001638 100%); border-bottom: 4px solid {RED};
          padding: 36px 48px 28px; }}
 .hero h1 {{ margin:0; font-size: 30px; color:#fff; }}
 .hero h1 span {{ color:{RED}; }}
 .hero p {{ color:#B9C4D4; max-width: 900px; line-height:1.5; }}
 .meta {{ color:#7E8AA0; font-size: 12px; }}
 .cards {{ display:flex; flex-wrap:wrap; gap:14px; padding: 22px 48px 6px; }}
 .card {{ background:{PANEL}; border:1px solid #26304050; border-left: 3px solid {RED};
          border-radius: 10px; padding: 14px 20px; min-width: 150px; }}
 .card .big {{ font-size: 24px; font-weight: bold; color:{CREAM}; }}
 .card .k {{ font-size: 12px; color:#9AA4B2; text-transform: uppercase; letter-spacing: .06em; margin-top:4px; }}
 .card .s {{ font-size: 12px; color:#7E8AA0; margin-top:2px; }}
 .panel {{ margin: 18px 48px; border-radius: 12px; overflow:hidden; }}
 .foot {{ padding: 20px 48px 40px; color:#7E8AA0; font-size: 12px; line-height: 1.6; }}
</style></head>
<body>
<div class='hero'>
  <h1>Bryce Harper — <span>Own the moment. Own the zone.</span></h1>
  <p>First-half 2026, governed read. Takes first: is he laying off the pitches a ball's width off the plate?
     Then the punishment: what happens when the same pitch creeps a ball's width inside the line.
     Full Phillies tenure (2019–2026) as the benchmark — no opt-outs there either.</p>
  <p class='meta'>uc-pos-005-harper-own-the-zone-001 · dp_uc22 · window through 2026-07-12 (All-Star break) ·
     96 G / 408 PA · verification 18/18 PASS · OZ-1..4 provisional pending glossary ratification ·
     9th All-Star selection = manual carry-in</p>
</div>
<div class='cards'>{card_html}</div>
{body}
<div class='foot'>
  Receipts: <code>out/dp_uc22_*</code> (20 files) · Governance trail: <code>Agents for Data Products/data-products/uc-pos-005-harper-own-the-zone-001/</code> (00–07)
  · Locked kernel inherited verbatim from dp_uc18/dp_uc20 · Shadow band = ±0.25 ft (one ball width, DPO-provided) around the rulebook zone, per-pitch sz_top/sz_bot
  · Data: Baseball Savant Statcast via local parquet cache, R games only, dedup (game_pk, at_bat_number, pitch_number).
</div>
</body></html>"""

out_file = MLB / f"{STEM}_interactive.html"
out_file.write_text(html, encoding='utf-8')
print(f"wrote {out_file} ({len(html):,} bytes, {len(figs)} figures)")
