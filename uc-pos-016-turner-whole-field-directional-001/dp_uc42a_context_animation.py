"""
dp_uc42a_context_animation.py — the rug-grain animation, for JupyterLab.
============================================================================
This is the notebook-side companion to the dashboard: the DPO's own Plotly
context cell, kept in his idiom, made animated, and put on the governed
kernel instead of ad-hoc groupbys.

Run it in the `snakes` env (needs plotly + pyarrow):

    from dp_uc42a_context_animation import figures
    figs = figures()
    figs['context'].show()

or from a shell, which writes standalone HTML next to this file:

    DP_UC42_DATA="C:/Users/Kellen/OneDrive/Documents/Python Scripts/MLB" \
        python dp_uc42a_context_animation.py

THREE CHANGES FROM THE ORIGINAL CELL, EACH DELIBERATE
----------------------------------------------------------------------------
1. `animation_frame` on `game_year`, with the rug tick for the framed season
   highlighted. That is the "single grain on the margin" the animation is
   about: one tick = one player-season, and the frame walks it.
2. Y axis defaults to RC-1 (`runs_created_per_600`) rather than raw
   `runs_created`. The original cell puts a COUNTING stat on the y axis
   against a RATE on the x axis, which lets playing time masquerade as a
   barrel-rate effect. Pass `metric='runs_created'` to get the original axis
   back — both ship, neither is hidden.
3. Every KPI comes from the governed functions in `dp_uc42a_kernel`
   (`nresults`, `runs_created`, `hard_hit_rate`, `barrel_rate`), transcribed
   verbatim from `Baseball Functions.ipynb`, rather than being recomputed
   inline. Colors come from the locked `DIRECTION_COLORS` map so they cannot
   be reassigned per call — the instability defect flagged in v1.0.0.

The original cell's title claim — "Trea is creating runs for a player of his
Barrel Rate Profile" — is left OFF the chart on purpose. On the normalized
axis it does not hold for 2026: at a .064 barrel rate he creates 53.5 runs
per 600 PA, below Bohm (.060 / 87.1) and below each of his own 2023-25
seasons. The chart is titled for what it shows instead.
"""
from __future__ import annotations

import os

import pandas as pd

from dp_uc42a_kernel import (
    load_pos, context_player_seasons, runs_created_per_600,
    turner_rows, build_pitch_frame, build_bip_frame,
    DIRECTION_COLORS, SEASONS, CURRENT, SUBJECT, AS_OF, PA_FLOOR, STRIKE_ZONE,
)

SUBJ_LABEL = "Trea Turner '26"
CONTEXT_LABEL = 'Context'
GREY = DIRECTION_COLORS['Straightaway']
NAVY = DIRECTION_COLORS['Oppo']
RED = DIRECTION_COLORS['Pull']

DATA_DICTIONARY = {
    'barrel_rate': 'Barrel Rate',
    'runs_created': 'Runs Created',
    'runs_created_per_600': 'Runs Created / 600 PA  (RC-1, provisional)',
    'game_year': 'Season',
    'player_name': 'Phillies Batter',
    'plate_apps': 'Plate Appearances',
    'hard_hit_rate': 'Hard Hit Rate',
    'woba': 'wOBA', 'ops': 'OPS', 'games': 'Games',
    'df_color': 'Is Trea Turner in 2026?',
    'hit_direction': 'Hit Direction',
    'loc_x': 'Field X (ft)', 'loc_y': 'Field Y (ft)',
    'plate_x': 'Plate X (ft)', 'plate_z': 'Plate Z (ft)',
}


# ---------------------------------------------------------------------------
def context_frame(pos=None, metric='runs_created_per_600'):
    """The rug population: Phillies batter player-seasons at or above the
    50-PA repo floor, on governed KPIs."""
    if pos is None:
        pos = load_pos(SEASONS)
    z = runs_created_per_600(context_player_seasons(pos, PA_FLOOR))
    z['label'] = z.player_name.str.split(', ').str[::-1].str.join(' ')
    z['metric'] = z[metric]
    return z


def _go():
    import plotly.graph_objects as go
    return go


def fig_context(z, metric='runs_created_per_600'):
    """Season-framed scatter with a rug on the x margin.

    Built with graph_objects rather than px.scatter(marginal_x='rug',
    animation_frame=...) on purpose: px builds the marginal as a subplot and
    the combination of marginals with animation frames has been version-
    sensitive. Explicit frames always animate."""
    go = _go()
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.88, 0.12], vertical_spacing=0.03)

    def traces(year):
        sub = z[(z.player_name == SUBJECT) & (z.game_year == year)]
        other_tt = z[(z.player_name == SUBJECT) & (z.game_year != year)]
        rest = z[z.player_name != SUBJECT]
        hov = ('<b>%{customdata[0]} · %{customdata[1]}</b><br>'
               'Barrel rate %{x:.3f}<br>' + DATA_DICTIONARY[metric] + ' %{y:.1f}<br>'
               'PA %{customdata[2]} · G %{customdata[3]}<br>'
               'wOBA %{customdata[4]:.3f} · OPS %{customdata[5]:.3f}'
               '<extra></extra>')

        def cd(d):
            return d[['label', 'game_year', 'plate_apps', 'games', 'woba', 'ops']].values

        def scat(d, color, name, size_ref=True, opacity=.85, line=0):
            return go.Scatter(
                x=d.barrel_rate, y=d.metric, mode='markers', name=name,
                customdata=cd(d), hovertemplate=hov,
                marker=dict(color=color, opacity=opacity,
                            size=d.games, sizemode='area',
                            sizeref=z.games.max() / 26 ** 2, sizemin=4,
                            line=dict(width=line, color='#ffffff')))

        def rug(d, color, width, name):
            return go.Scatter(
                x=d.barrel_rate, y=[0] * len(d), mode='markers', name=name,
                marker=dict(symbol='line-ns-open', color=color,
                            size=14, line=dict(width=width, color=color)),
                hoverinfo='skip', showlegend=False)

        return ([scat(rest, GREY, 'Other Phillies player-seasons', opacity=.35),
                 scat(other_tt, NAVY, 'Turner, other seasons', opacity=.55),
                 scat(sub, RED, SUBJ_LABEL.replace("'26", "'" + str(year)[2:]),
                      opacity=.95, line=2)],
                [rug(rest, '#aab3bd', 1, 'rug'),
                 rug(other_tt, NAVY, 2, 'rug'),
                 rug(sub, RED, 3, 'rug')])

    top, bottom = traces(SEASONS[-1])
    for t in top:
        fig.add_trace(t, row=1, col=1)
    for t in bottom:
        fig.add_trace(t, row=2, col=1)

    frames = []
    for yr in SEASONS:
        tp, bt = traces(yr)
        frames.append(go.Frame(name=str(yr), data=tp + bt,
                               traces=list(range(len(tp) + len(bt)))))
    fig.frames = frames

    steps = [dict(method='animate', label=str(yr),
                  args=[[str(yr)], dict(mode='immediate',
                                        frame=dict(duration=600, redraw=True),
                                        transition=dict(duration=300))])
             for yr in SEASONS]
    fig.update_layout(
        template='plotly_white',
        title=dict(text=('Trea Turner’s season is one tick in the rug<br>'
                         '<sup>Phillies batter seasons ≥ %d PA, %d–%d · bubble area = games · '
                         'data as of %s · uc-pos-016 / dp_uc42a v1.1.0</sup>'
                         % (PA_FLOOR, SEASONS[0], SEASONS[-1], AS_OF))),
        legend=dict(orientation='h', y=1.02, yanchor='bottom'),
        margin=dict(t=110, r=40, b=70, l=70),
        updatemenus=[dict(type='buttons', showactive=False, x=0.02, y=1.14,
                          xanchor='left', yanchor='top',
                          buttons=[
                              dict(label='▶ Play', method='animate',
                                   args=[None, dict(frame=dict(duration=1100, redraw=True),
                                                    fromcurrent=True,
                                                    transition=dict(duration=350))]),
                              dict(label='❚❚ Pause', method='animate',
                                   args=[[None], dict(mode='immediate',
                                                      frame=dict(duration=0, redraw=False))])])],
        sliders=[dict(active=len(SEASONS) - 1, y=-0.02, x=0.12, len=0.82,
                      currentvalue=dict(prefix='Season  ', font=dict(size=15)),
                      steps=steps)])
    fig.update_yaxes(title_text=DATA_DICTIONARY[metric], row=1, col=1)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False,
                     title_text='rug', row=2, col=1)
    fig.update_xaxes(title_text=DATA_DICTIONARY['barrel_rate'], row=2, col=1)
    return fig


def fig_spray(bip):
    """Season-framed spray chart on governed field coordinates, with the
    ±4.7-slope hit_direction boundary drawn so the classification is
    auditable by eye rather than taken on trust."""
    go = _go()
    fig = go.Figure()

    def traces(year):
        out = []
        for d in ['Pull', 'Straightaway', 'Oppo']:
            s = bip[(bip.game_year == year) & (bip.hit_direction == d)]
            out.append(go.Scatter(
                x=s.loc_x, y=s.loc_y, mode='markers', name=d,
                customdata=s[['zone', 'pitch_type', 'events', 'game_date']].astype(str).values,
                hovertemplate=('<b>' + d + '</b><br>zone %{customdata[0]} · '
                               '%{customdata[1]}<br>%{customdata[2]}<br>'
                               '%{customdata[3]}<extra></extra>'),
                marker=dict(color=DIRECTION_COLORS[d], size=7, opacity=.78)))
        return out

    for t in traces(SEASONS[-1]):
        fig.add_trace(t)
    fig.frames = [go.Frame(name=str(y), data=traces(y), traces=[0, 1, 2])
                  for y in SEASONS]
    for sign in (-1, 1):
        fig.add_shape(type='line', x0=0, y0=0, x1=sign * 430 / 4.7, y1=430,
                      line=dict(color='#8a949e', width=1, dash='dash'))
    for sign in (-1, 1):
        fig.add_shape(type='line', x0=0, y0=0, x1=sign * 233, y1=233,
                      line=dict(color='#dfe4ea', width=1))
    fig.update_layout(
        template='plotly_white',
        title=('Whole-field spray, balls in play<br><sup>governed derive_loc + '
               'hit_direction · dashed = ±4.7-slope boundary</sup>'),
        xaxis=dict(title='Field X (ft)', range=[-330, 330],
                   scaleanchor='y', scaleratio=1),
        yaxis=dict(title='Field Y (ft)', range=[-20, 430]),
        margin=dict(t=100, b=60),
        updatemenus=[dict(type='buttons', showactive=False, x=0.02, y=1.12,
                          buttons=[dict(label='▶ Play', method='animate',
                                        args=[None, dict(frame=dict(duration=1100, redraw=True),
                                                         fromcurrent=True)])])],
        sliders=[dict(active=len(SEASONS) - 1, currentvalue=dict(prefix='Season  '),
                      steps=[dict(method='animate', label=str(y),
                                  args=[[str(y)], dict(mode='immediate',
                                                       frame=dict(duration=500, redraw=True))])
                             for y in SEASONS])])
    return fig


def fig_pitchmap(bip):
    """Season-framed pitch map — the chart v1.0.0 actually built when a spray
    chart was specified. Colored by the direction the ball was hit, which is
    the join between this view and the spray chart."""
    go = _go()
    z = STRIKE_ZONE
    fig = go.Figure()

    def traces(year):
        out = []
        for d in ['Pull', 'Straightaway', 'Oppo']:
            s = bip[(bip.game_year == year) & (bip.hit_direction == d)
                    & bip.plate_x.notna()]
            out.append(go.Scatter(
                x=s.plate_x, y=s.plate_z, mode='markers', name=d,
                customdata=s[['zone', 'pitch_type', 'events']].astype(str).values,
                hovertemplate=('<b>hit ' + d + '</b><br>zone %{customdata[0]} · '
                               '%{customdata[1]}<br>%{customdata[2]}<extra></extra>'),
                marker=dict(color=DIRECTION_COLORS[d], size=7, opacity=.8)))
        return out

    for t in traces(SEASONS[-1]):
        fig.add_trace(t)
    fig.frames = [go.Frame(name=str(y), data=traces(y), traces=[0, 1, 2])
                  for y in SEASONS]
    fig.add_shape(type='rect', x0=-z['x_half'], x1=z['x_half'],
                  y0=z['z_bot'], y1=z['z_top'],
                  line=dict(color='#43505c', width=1.5))
    for i in (1, 2):
        fig.add_shape(type='line', x0=-z['x_half'] + 2 * z['x_half'] * i / 3,
                      x1=-z['x_half'] + 2 * z['x_half'] * i / 3,
                      y0=z['z_bot'], y1=z['z_top'], line=dict(color='#dfe4ea', width=1))
        fig.add_shape(type='line', x0=-z['x_half'], x1=z['x_half'],
                      y0=z['z_bot'] + (z['z_top'] - z['z_bot']) * i / 3,
                      y1=z['z_bot'] + (z['z_top'] - z['z_bot']) * i / 3,
                      line=dict(color='#dfe4ea', width=1))
    fig.update_layout(
        template='plotly_white',
        title=("Pitch map — where the pitch was, colored by where the ball went<br>"
               "<sup>catcher's view · RHB stands on the negative plate_x side · "
               "box = Statcast zones 1–9, the governed in/out authority</sup>"),
        xaxis=dict(title='plate_x (ft)', range=[-2.3, 2.3],
                   scaleanchor='y', scaleratio=1),
        yaxis=dict(title='plate_z (ft)', range=[0.2, 4.6]),
        margin=dict(t=110, b=60),
        updatemenus=[dict(type='buttons', showactive=False, x=0.02, y=1.12,
                          buttons=[dict(label='▶ Play', method='animate',
                                        args=[None, dict(frame=dict(duration=1100, redraw=True),
                                                         fromcurrent=True)])])],
        sliders=[dict(active=len(SEASONS) - 1, currentvalue=dict(prefix='Season  '),
                      steps=[dict(method='animate', label=str(y),
                                  args=[[str(y)], dict(mode='immediate',
                                                       frame=dict(duration=500, redraw=True))])
                             for y in SEASONS])])
    return fig


def figures(metric='runs_created_per_600'):
    pos = load_pos(SEASONS)
    z = context_frame(pos, metric)
    tt = turner_rows(pos)
    bip = build_bip_frame(tt[tt.game_type == 'R'])
    return {'context': fig_context(z, metric),
            'spray': fig_spray(bip),
            'pitchmap': fig_pitchmap(bip)}


def main():
    figs = figures()
    for name, fig in figs.items():
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out',
                         f'dp_uc42a_plotly_{name}.html')
        # plotly.js is INLINED, not pulled from a CDN — the repo's
        # vendor-don't-CDN rule (uc-pos-011). Bigger file, works offline,
        # works in five years.
        fig.write_html(p, include_plotlyjs=True, auto_play=False)
        print('wrote', p)


if __name__ == '__main__':
    main()
