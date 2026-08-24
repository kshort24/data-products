# Nestor Cortes
He has signed for the Philadelphia Phillies on a major-league contract. To make room on the 40-man roster, Caleb Kilian was transferred to the 60-Day IL.

Nestor himself is returning from injury, undergoing some type of surgery on his arm last fall. His production has fallen off the last couple years since his All-Star campaign in 2022. He will most likely be remembered for being the pitcher who allowed the grand slam to Freddie Freeman in the 2024 World Series. He spent last year with San Diego.

Now, he will join a Phillies pitching staff that has looked worn down the last few weeks. He could offer them a sixth starter should the team opt for that rotation strategy as they have in the past. Don Mattingly has leveraged a six-man rotation in his managerial career too, I believe. It also seems plausible that Nestor will serve as a bulk option out of the bullpen, perhaps building up to provide more innings as needed. Given that he is a lefty and has been successful in the past, could the Phillies give him opportunities in high-leverage situations? Except perhaps facing Freddie Freeman with the bases loaded.

```python
vs = nc = pd.concat([nphl[nphl.player_name == 'Cortes, Nestor']
                ,pps[pps.player_name == 'Cortes, Nestor']
               ])
```

Questions for a Nestor Cortes scouting report:
- How has he been deployed in his career? Exclusively as a starter or as a reliver too? Bulk option behind an opener? This code snippet below helps inform my answer.
```python
# Start by analyzing his per-game performance
level = ['player_name' # Define per-game level, include game_year for later aggregation
         ,'game_year'
         ,'game_date'
         ,'game_pk'
        ]
# Merge to additional inning and at-bat level to get start and end of his appearances
z = df.groupby(level,as_index=False # Starting at the game level
          ).agg(min_ab = ('at_bat_number','min') # First At-Bat
                ,max_ab= ('at_bat_number','max') # Last At-Bat
                ,total_pitches = ('des','size') # The number of pitches he threw in this game
                ,uq_pas = ('at_bat_number','nunique') # The number of unique at-bats he had
               ).merge(df.groupby(level + ['inning','at_bat_number'],as_index=False # Merge to a group that includes the inning and at_bat_number so we can pull out the min and max we just ID'd
                                 ).agg(sizer = ('des','size') # This is a meaningless agg I just needed the group at the right level
                                      )
                       ,left_on = level + ['min_ab'] # I am finding the first plate appearance of a game
                       ,right_on = level + ['at_bat_number'] # Joining to where that plate appearance was at the inning/AB level so I can get the inning
                       ,how = 'left'
                       ,suffixes = ('','_ab')
                      ).merge(df.groupby(level + ['inning','at_bat_number'],as_index=False # Now for the max AB, join to an object grouped at the game-level on top of the inning/AB level
                                        ).agg(sizer = ('des','size') # Meaningless agg bc I wanted to group at the correct grain
                                             )
                              ,left_on = level + ['max_ab'] # Last plate appearance of a given game
                              ,right_on = level + ['at_bat_number'] # Find that plate appearance in my agg'd merger which will include the inning
                              ,how = 'left'
                              ,suffixes = ('_start','_end') # The innings that I previously pulled will be ambiguous but since I started with min and now do max, assign correct suffixes
                             )
# Intermediate KPIs, the number of innings in a start, the starting inning, the total number of pitches, and the total number of plate appearances
kpis = ['innings'
        ,'inning_start'
        ,'total_pitches'
        ,'uq_pas'
       ]
z['innings'] = z.inning_end-z.inning_start # Calculate the number of innings as the difference between the inning start and end
# Store in a dataframe that has been "aggregated" since it is like a staging table or intermediate grain
zagg = z[level+kpis]
level_agg = ['player_name','game_year'] # Define new level of granularity that will be used for final reporting
# For the final aggregation (fig level, gold layer, consumption-ready!) Group at the Season level and assess his usage profile across these KPIs
zfig = zagg.groupby(level_agg,as_index=False
            ).agg(total_games = ('game_pk','nunique') # Calculate the number of games he appeared in during the season
                  ,total_innings = ('innings','sum') # The unique number of innings he pitched in
                  ,total_pas = ('uq_pas','sum') # the number of unique at-bats he encountered
                 ).merge(zagg[zagg.inning_start == 1].groupby(level_agg,as_index=False # Filter to where the first inning he appeared in was the 1st inning to identify those as starts
                                                             ).agg(starts = ('game_pk','nunique')
                                                                  )
                         ,on = level_agg, how = 'left', suffixes = ('','_start')
                        ).merge(zagg[(zagg.inning_start > 1)&(zagg.innings > 2)].groupby(level_agg,as_index= False # Filter to where he appeared later in a game for more than 2 innings for "bulks"
                                                                                        ).agg(bulks = ('game_pk','nunique')
                                                                                             )
                                ,on = level_agg, how = 'left', suffixes = ('','_bulk')
                               ).fillna(0)
zfig['start_share'] = zfig.starts/zfig.total_games # Calculate share of appearances that were starts
zfig['bulk_share'] = zfig.bulks/zfig.total_games # Calculate share of appearances that were "bulks"
zfig['innings_per_gm'] = zfig.total_innings/zfig.total_games # Calculate ratio of innings to games
zfig['plate_apps_per_gm'] = zfig.total_pas/zfig.total_games # Calculate ratio of plate appearances to games
zfig.round(3)
```
So he started as a reliever but appears to have gotten some bulk appearances in 2019. 2020 was primarily out of the bullpen in his handful of appearnaces (1 start) and 2021 he likely transitioned from a role in the bullpen to starting. Since 2022, he has almost exclusively started.

- What are his platoon splits throughout his career? How has his approach to both LHB and RHB changed over his career?
```python
# How has his approach to both LHB and RHB changed over his career?
level = ['player_name'
          ,'game_year'
          ,'stand'
         ]
pm = df.groupby(level,as_index=False
          ).agg(total_pitches = ('des','size')
               ).merge(df.groupby(level + ['pitch_type'
                                            ,'pitch_name'
                                           ],as_index=False
                                 ).agg(pitches = ('des','size')
                                       ,velo = ('release_speed','mean')
                                       ,spin = ('release_spin_rate','mean')
                                       ,horiz = ('pfx_x','mean')
                                       ,vert = ('pfx_z','mean')
                                       ,plate_x = ('plate_x','mean')
                                       ,plate_z = ('plate_z','mean')
                                      )
                       ,on = level, how = 'right', suffixes = ('_total','')
                      ).round(2)
pm['usage'] = pm.pitches/pm.total_pitches
pm.round(3)
try:
    data_dictionary
except NameError:
    data_dictionary = {}
fig = px.scatter(pm[pm.usage > 0.01].sort_values(by=['stand','game_year']).round(3)
                 ,x='plate_x'
                 ,y='plate_z'
                 ,color='pitch_name'
                 ,size='usage'
                 ,text='pitch_type'
                 ,title = "Nestor Cortes Pitch Mix over Time"
                 ,facet_row = 'stand'
                 ,facet_col = 'game_year'
                 ,template = 'plotly_dark'
                 ,labels = data_dictionary | {'pitches' : 'Pitches'
                                              ,'total_pitches' : 'Total Pitches'
                                              ,'velo' : 'Avg. Velocity (mph)'
                                              ,'spin' : 'Avg. Spin (rpm)'
                                              ,'horiz' : 'Avg. Horizontal Break (ft)'
                                              ,'vert' : 'Avg. Vertical Break (ft)'
                                              ,'plate_x' : 'Plate Horiz'
                                              ,'plate_z' : 'Plate Vert'
                                              ,'game_year' : 'Season'
                                              ,'pitch_name' : 'Pitch Name'
                                              ,'stand' : 'Stand'
                                              ,'pitch_type' : 'Pitch Type'
                                              ,'usage' : 'Pitch Usage'
                                             }
                 ,hover_data = [c for c in pm.columns]
                 ,subtitle = "He lives on the outside part of the plate to either side. To LHB: FF, FC, and ST away. Adds a CH when working to RHB."
                )
fig.add_shape(type='rect',x0=-0.83,x1=0.83,y0=df.sz_bot.mean(),y1=df.sz_top.mean()
              ,row='all',col='all'
             )
fig.show()
```
This answers some stuff about his basic approach and how it evolves over time. In order to assess platoon splits and performance, I will need to leverage functions from Baseball Functions. Those similarly could have been used to do the above but who cares.
```python
# Inherit level from above
kpis = ['plate_apps' # nresults
        ,'ba','obp','slg' # nresults
        ,'ops','woba' #nresults
        ,'krate','bbrate' #nresults
        ,'chase_rate' # chase_rate
        ,'whiff_rate' # whiff_rate
        ,'putaway_rate' # putaway_rate
        ,'hard_hit_rate' # hard_hit_rate
        ,'barrel_rate' # barrel_rate
       ]
z = nresults(level,df
            ).merge(chase_rate(level,df)
                    ,on = level, how = 'left', suffixes = ('','_cr')
                   ).merge(whiff_rate(level,df)
                           ,on = level, how = 'left', suffixes = ('','_wr')
                          ).merge(putaway_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_par')
                                 ).merge(hard_hit_rate(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_hh')
                                        ).merge(barrel_rate(level,df)
                                               ,on = level, how = 'left', suffixes = ('','_br')
                                               ).fillna(0)
z[level+kpis].round(3).sort_values(by=level)
```
- What does his stuff typically look like? Was it trending in a certain direction before the injury and what should the Phillies be monitoring? He is slowing down but not particularly fast or anything like that.
```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Define your four figures here
pt = 'FF'
# for pt in df.pitch_type.unique().tolist():
fig1 = px.box(df[df.pitch_type == pt]
              ,x='game_year'
               ,y='release_speed'
               #,color='pitch_type'
               ,title = "Pitch Velocity by Year: {}".format(pt)
               ,template = 'plotly_dark'
               ,labels = {'game_year' : 'Season'
                          ,'release_speed' : 'Pitch Velocity (mph)'
                          ,'release_spin_rate' : 'Pitch Spin (rpm)'
                          ,'pfx_x' : 'Pitch Horizontal Break (ft)'
                          ,'pfx_z' : 'Pitch Vertical Break (ft)'
                         }
             )
fig2 = px.box(df[df.pitch_type == pt]
              ,x='game_year'
               ,y='release_spin_rate'
               #,color='pitch_type'
               ,title = "Pitch Spin by Year: {}".format(pt)
               ,template = 'plotly_dark'
               ,labels = {'game_year' : 'Season'
                          ,'release_speed' : 'Pitch Velocity (mph)'
                          ,'release_spin_rate' : 'Pitch Spin (rpm)'
                          ,'pfx_x' : 'Pitch Horizontal Break (ft)'
                          ,'pfx_z' : 'Pitch Vertical Break (ft)'
                         }
             )
fig3 = px.box(df[df.pitch_type == pt]
              ,x='game_year'
               ,y='pfx_x'
               #,color='pitch_type'
               ,title = "Pitch Horizontal Break by Year: {}".format(pt)
               ,template = 'plotly_dark'
               ,labels = {'game_year' : 'Season'
                          ,'release_speed' : 'Pitch Velocity (mph)'
                          ,'release_spin_rate' : 'Pitch Spin (rpm)'
                          ,'pfx_x' : 'Pitch Horizontal Break (ft)'
                          ,'pfx_z' : 'Pitch Vertical Break (ft)'
                         }
             )
fig4 = px.box(df[df.pitch_type == pt]
              ,x='game_year'
               ,y='pfx_z'
               #,color='pitch_type'
               ,title = "Pitch Vert by Year: {}".format(pt)
               ,template = 'plotly_dark'
               ,labels = {'game_year' : 'Season'
                          ,'release_speed' : 'Pitch Velocity (mph)'
                          ,'release_spin_rate' : 'Pitch Spin (rpm)'
                          ,'pfx_x' : 'Pitch Horizontal Break (ft)'
                          ,'pfx_z' : 'Pitch Vertical Break (ft)'
                         }
             )

combined_fig = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=[
        "Pitch Velocity by Year: {}".format(pt),
        "Pitch Spin by Year: {}".format(pt),
        "Pitch Horizontal Break by Year: {}".format(pt),
        "Pitch Vert by Year: {}".format(pt)
    ]
)

# Add traces from each Plotly Express figure
for trace in fig1.data:
    combined_fig.add_trace(trace, row=1, col=1)

for trace in fig2.data:
    combined_fig.add_trace(trace, row=1, col=2)

for trace in fig3.data:
    combined_fig.add_trace(trace, row=2, col=1)

for trace in fig4.data:
    combined_fig.add_trace(trace, row=2, col=2)

combined_fig.update_layout(
    height=900,
    width=1200,
    title_text="Tracking Nestor Cortes's Stuff",
    showlegend=True
)
combined_fig.update_layout(template = 'plotly_dark')
combined_fig.show()

# Or this interactive one
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Use all pitch types found in the dataframe
# Or replace this with your own specific list, e.g. ['FF', 'SL', 'CH', 'CU']
pitch_types = sorted(df['pitch_type'].dropna().unique().tolist())

labels = {
    'game_year': 'Season',
    'release_speed': 'Pitch Velocity (mph)',
    'release_spin_rate': 'Pitch Spin (rpm)',
    'pfx_x': 'Pitch Horizontal Break (ft)',
    'pfx_z': 'Pitch Vertical Break (ft)'
}

metrics = [
    {
        "col": "release_speed",
        "title": "Pitch Velocity by Year",
        "row": 1,
        "col_pos": 1
    },
    {
        "col": "release_spin_rate",
        "title": "Pitch Spin by Year",
        "row": 1,
        "col_pos": 2
    },
    {
        "col": "pfx_x",
        "title": "Pitch Horizontal Break by Year",
        "row": 2,
        "col_pos": 1
    },
    {
        "col": "pfx_z",
        "title": "Pitch Vertical Break by Year",
        "row": 2,
        "col_pos": 2
    }
]

combined_fig = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=[m["title"] for m in metrics],
    horizontal_spacing=0.08,
    vertical_spacing=0.12
)

trace_map = {}
trace_count = 0

for pt in pitch_types:
    trace_map[pt] = []

    for m in metrics:
        temp_fig = px.box(
            df[df['pitch_type'] == pt],
            x='game_year',
            y=m["col"],
            template='plotly_dark',
            labels=labels
        )

        for trace in temp_fig.data:
            trace.visible = pt == pitch_types[0]
            trace.showlegend = False

            combined_fig.add_trace(
                trace,
                row=m["row"],
                col=m["col_pos"]
            )

            trace_map[pt].append(trace_count)
            trace_count += 1

# Dropdown buttons
buttons = []

for pt in pitch_types:
    visible = [False] * trace_count

    for idx in trace_map[pt]:
        visible[idx] = True

    buttons.append(
        dict(
            label=pt,
            method="update",
            args=[
                {"visible": visible},
                {
                    "title": f"Tracking Nestor Cortes's Stuff: {pt}"
                }
            ]
        )
    )
combined_fig.update_layout(
    height=900,
    width=1200,
    template='plotly_dark',
    title=f"Tracking Nestor Cortes's Stuff: {pitch_types[0]}",
    showlegend=False,
    updatemenus=[
        dict(
            buttons=buttons,
            direction="down",
            x=1.02,
            y=1.00,
            xanchor="left",
            yanchor="top",
            showactive=True
        )
    ]
)

combined_fig.update_xaxes(title_text="Season", row=1, col=1)
combined_fig.update_xaxes(title_text="Season", row=1, col=2)
combined_fig.update_xaxes(title_text="Season", row=2, col=1)
combined_fig.update_xaxes(title_text="Season", row=2, col=2)

combined_fig.update_yaxes(title_text="Pitch Velocity (mph)", row=1, col=1)
combined_fig.update_yaxes(title_text="Pitch Spin (rpm)", row=1, col=2)
combined_fig.update_yaxes(title_text="Pitch Horizontal Break (ft)", row=2, col=1)
combined_fig.update_yaxes(title_text="Pitch Vertical Break (ft)", row=2, col=2)

combined_fig.show()
```
- How impactful was his stuff on his performance? What other indicators have correlated with his successful periods and which have correlated with his struggles?

Tailor these questions to actions that could be taken by various personas within the Phillies pitching value stream:
- Manager (Deployment questions, should the Phillies use him as a starter or a bulk reliever? Does it make sense to push him into high-leverage bullpen roles? Does he benefit from rest?)
- Battery (Pitch selection, efficacy against platoon splits)
- Pitching Deparment (Stuff tracking, indicators on performance, cues to chase best outcomes)

