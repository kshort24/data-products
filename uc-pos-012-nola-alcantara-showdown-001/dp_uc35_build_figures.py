"""
dp_uc35_build_figures.py — figures for uc-pos-012 (all numbers trace to out/ receipts)
Phillies brand on plotly_dark (DPO-specified template): red #E81828,
light-navy #6BACE4 (navy #002D72 is unreadable on dark), white, gold #FFC72C.
"""
import json
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
RED, BLUE, GOLD, GREY = '#E81828', '#6BACE4', '#FFC72C', '#8a8f98'

r = lambda n: pd.read_csv(os.path.join(OUT, f'dp_uc35_{n}.csv'))
H = json.load(open(os.path.join(OUT, 'dp_uc35_headlines.json')))

box = r('boxplot_population')
nola_c = H['nola_mia']
whe_c = H['wheeler_mia']
harper = r('harper_mia_seasons')
FLOOR = H['floor_pa']

LBL = {'rc_per_pa': 'RC per PA', 'game_year': 'Season', 'woba': 'wOBA',
       'plate_apps': 'Plate Appearances', 'stand': 'Batter Stand'}

# ── fig1: the box plot, re-imagined per the DPO prose ─────────────────────
fig = px.box(
    box.round(3), x='game_year', y='rc_per_pa',
    title='If Aaron Nola against the Marlins were a Phillies hitter',
    subtitle=(f'RC per PA, Phillies player-seasons with more than {FLOOR} PA '
              '(= Nola’s min season PA vs MIA) · 2015–2026 · '
              'Nola & Wheeler vs MIA as career constants · Harper vs MIA highlighted'),
    template='plotly_dark', points='all',
    color_discrete_sequence=[GREY],
    hover_data=['player_name', 'plate_apps', 'ba', 'obp', 'slg', 'woba',
                'runs_created'],
    labels=LBL)
fig.update_traces(marker=dict(size=3, opacity=0.45), line=dict(width=1.2))
fig.add_hline(y=round(nola_c['rc_per_pa'], 4), line_color=RED, line_width=3,
              annotation_text=(f"Noles (career vs MIA): {nola_c['rc_per_pa']:.3f} "
                               f"RC/PA over {int(nola_c['plate_apps'])} PA"),
              annotation_font_color=RED, annotation_position='top left')
fig.add_hline(y=round(whe_c['rc_per_pa'], 4), line_color=BLUE, line_width=3,
              line_dash='dash',
              annotation_text=(f"Wheeler (career vs MIA): {whe_c['rc_per_pa']:.3f} "
                               f"RC/PA over {int(whe_c['plate_apps'])} PA"),
              annotation_font_color=BLUE, annotation_position='bottom left')
hm = harper.round(3)
fig.add_trace(go.Scatter(
    x=hm.game_year, y=hm.rc_per_pa, mode='markers',
    name='Harper vs MIA (real, by season)',
    marker=dict(symbol='star', size=13, color=GOLD,
                line=dict(color='white', width=1)),
    customdata=hm[['plate_apps', 'woba', 'below_floor']],
    hovertemplate=('Harper vs MIA %{x}<br>RC/PA %{y:.3f}<br>'
                   'PA %{customdata[0]} · wOBA %{customdata[1]:.3f}<br>'
                   'below floor: %{customdata[2]}<extra></extra>')))
fig.update_xaxes(range=[2014, 2027], dtick=1)
fig.update_yaxes(range=[0, 0.31])
fig.update_layout(width=1200, height=650, legend=dict(orientation='h', y=-0.12),
                  showlegend=True)
fig.write_image(os.path.join(OUT, 'dp_uc35_fig1_boxplot.png'), scale=2)
fig.write_html(os.path.join(OUT, 'dp_uc35_fig1_boxplot.html'),
               include_plotlyjs='cdn')
print('fig1 done')

# ── fig2: season scatter faceted by batter stand, Nola highlighted ────────
ps = r('phi_hitter_season_stand')
ps = ps[ps.in_population].copy().round(3)
ps['entity'] = 'Phillies Hitters'
nms = r('nola_mia_season_stand').round(3)
fs = r('floor_derivation_stand').set_index('stand')['floor'].to_dict()
nms['in_population'] = True
fig2 = px.scatter(
    ps, x='game_year', y='rc_per_pa', facet_col='stand',
    title='Run creation by season and batter stand — the Noles composite batter vs real Phillies hitters',
    subtitle=(f'Per-stand floors = Nola’s min season PA vs MIA by stand '
              f"(L>{fs.get('L')}, R>{fs.get('R')}) · marker size = PA"),
    template='plotly_dark', color_discrete_sequence=[GREY],
    size='plate_apps', size_max=14, opacity=0.5,
    hover_data=['player_name', 'plate_apps', 'ba', 'obp', 'slg', 'woba', 'krate',
                'whiff_rate', 'chase_rate', 'hard_hit_rate', 'barrel_rate'],
    labels=LBL | {'player_name': 'Player Name (ambiguous column!)'})
for i, st in enumerate(['L', 'R']):
    d = nms[nms.stand == st]
    d = d[d.plate_apps > fs.get(st, 0)]
    fig2.add_trace(go.Scatter(
        x=d.game_year, y=d.rc_per_pa, mode='markers',
        name='Noles (MIA batters vs Nola)' if i == 0 else None,
        showlegend=(i == 0), legendgroup='noles',
        marker=dict(symbol='diamond', size=12, color=RED,
                    line=dict(color='white', width=1)),
        customdata=d[['plate_apps', 'woba', 'krate', 'whiff_rate']],
        hovertemplate=('Noles ' + st + 'HB %{x}<br>RC/PA %{y:.3f}<br>'
                       'PA %{customdata[0]} · wOBA %{customdata[1]:.3f}<br>'
                       'K %{customdata[2]:.3f} · whiff %{customdata[3]:.3f}'
                       '<extra></extra>')),
        row=1, col=i + 1)
fig2.update_xaxes(range=[2014, 2027], dtick=2)
fig2.update_yaxes(range=[0, 0.31])
fig2.update_layout(width=1200, height=600, legend=dict(orientation='h', y=-0.15))
fig2.write_image(os.path.join(OUT, 'dp_uc35_fig2_scatter_stand.png'), scale=2)
fig2.write_html(os.path.join(OUT, 'dp_uc35_fig2_scatter_stand.html'),
                include_plotlyjs='cdn')
print('fig2 done')

# ── fig3: exposure — who has thrown the most pitches at the PHI offense ───
exp = r('pitcher_exposure_rank_top25').head(10).copy()
exp['label'] = exp.apply(
    lambda x: (x.pitcher_name if isinstance(x.pitcher_name, str)
               else f'MLBAM {int(x.pitcher)}'), axis=1)
exp['flag'] = exp.name_source.fillna('').str.contains('carry-in').map(
    {True: ' *', False: ''})
exp['label'] = exp.label + exp.flag
colors = [RED if p == 645261 else (BLUE if '*' in l else GREY)
          for p, l in zip(exp.pitcher, exp.label)]
fig3 = go.Figure(go.Bar(
    x=exp.pitches[::-1], y=exp.label[::-1], orientation='h',
    marker_color=colors[::-1],
    customdata=exp[['plate_apps', 'first_year', 'last_year']][::-1],
    hovertemplate=('%{y}: %{x} pitches<br>%{customdata[0]} PA · '
                   '%{customdata[1]}–%{customdata[2]}<extra></extra>'),
    text=exp.pitches[::-1], textposition='outside'))
fig3.update_layout(
    template='plotly_dark', width=1100, height=560,
    title=dict(text='Pitches thrown to the Phillies offense, Statcast era (2015–2026)'
               '<br><sup>Alcantara in red — #2 in the frame, behind only Scherzer · '
               '* name via DPO carry-in, id-verified counts · unlabeled = MLBAM id (no local name authority)</sup>'),
    xaxis_title='Pitches to PHI batters (pos frame)')
fig3.write_image(os.path.join(OUT, 'dp_uc35_fig3_exposure.png'), scale=2)
fig3.write_html(os.path.join(OUT, 'dp_uc35_fig3_exposure.html'),
                include_plotlyjs='cdn')
print('fig3 done')

# ── fig4: the Harper book — most-faced + the Alcantara line ───────────────
hx = r('harper_pitcher_rank_top25').head(8).copy()
hx['label'] = hx.apply(
    lambda x: (x.pitcher_name if isinstance(x.pitcher_name, str)
               else f'MLBAM {int(x.pitcher)}'), axis=1)
hcolors = [RED if p == 645261 else GREY for p in hx.pitcher]
hva = H['harper_vs_alcantara']
fig4 = go.Figure(go.Bar(
    x=hx.plate_apps[::-1], y=hx.label[::-1], orientation='h',
    marker_color=hcolors[::-1], text=hx.plate_apps[::-1], textposition='outside',
    customdata=hx[['pitches']][::-1],
    hovertemplate='%{y}: %{x} PA · %{customdata[0]} pitches<extra></extra>'))
fig4.update_layout(
    template='plotly_dark', width=1100, height=520,
    title=dict(text='Harper as a Phillie: most-faced pitchers by PA (2019–2026)'
               '<br><sup>vs Alcantara (red): '
               f"{hva['ba']:.3f}/{hva['obp']:.3f}/{hva['slg']:.3f}, "
               f"wOBA {hva['woba']:.3f}, HH {hva['hard_hit_rate']:.0%}, "
               f"Barrel {hva['barrel_rate']:.0%} over {int(hva['plate_apps'])} PA</sup>"),
    xaxis_title='Plate appearances')
fig4.write_image(os.path.join(OUT, 'dp_uc35_fig4_harper_book.png'), scale=2)
fig4.write_html(os.path.join(OUT, 'dp_uc35_fig4_harper_book.html'),
                include_plotlyjs='cdn')
print('fig4 done')

# ── fig5: KPI family, four entities side by side ──────────────────────────
ents = [('Noles (vs MIA, career)', H['nola_mia'], RED),
        ('Wheeler vs MIA (career)', whe_c, BLUE),
        ('PHI offense vs Alcantara', H['phi_vs_alcantara'], GREY),
        ('Harper vs MIA (career)', H['harper_mia'], GOLD)]
kpis = [('woba', 'wOBA'), ('rc_per_pa', 'RC/PA'), ('krate', 'K rate'),
        ('whiff_rate', 'Whiff'), ('chase_rate', 'Chase'),
        ('hard_hit_rate', 'Hard Hit'), ('barrel_rate', 'Barrel')]
fig5 = go.Figure()
for name, d, c in ents:
    fig5.add_trace(go.Bar(
        name=f"{name} · {int(d['plate_apps'])} PA",
        x=[k[1] for k in kpis], y=[round(d[k[0]], 3) for k in kpis],
        marker_color=c, text=[f"{d[k[0]]:.3f}" for k in kpis],
        textposition='outside', textfont_size=9))
fig5.update_layout(
    template='plotly_dark', barmode='group', width=1200, height=560,
    title=dict(text='The KPI family, career grains — the composite batters each ace creates vs the real thing'
               '<br><sup>slash lines in the report tables · all rates unrounded until publication (D4 hygiene)</sup>'),
    legend=dict(orientation='h', y=-0.1), yaxis_title='Rate')
fig5.write_image(os.path.join(OUT, 'dp_uc35_fig5_kpi_family.png'), scale=2)
fig5.write_html(os.path.join(OUT, 'dp_uc35_fig5_kpi_family.html'),
                include_plotlyjs='cdn')
print('fig5 done')
