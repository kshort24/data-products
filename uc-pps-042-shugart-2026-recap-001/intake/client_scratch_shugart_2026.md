# Chase Shugart
2026 retrospective.

So what I found. Mostly even leaning slightly reverse platoon splits and a solid year overall. Lefties did more damage when they connected but struck out more, walked less, and whiffed more. Righties hit him more frequently and drew more walks but did not slug as much as left-handed batters.

This seems to be driven by his cutters and sinkers which are both pretty good pitches. Although his cutter is a problem against right-handed batters. It allows him to own the inside part of the plate to left-handed batters. This sets up his sinker as a weapon to lefties.

June was bad and he likely lost some command. I think there is an argument to make that he should focus on being sinker/sweeper to righties but abandoning his sweeper at the end of the year did coincide with a strong finish.

Keeping his command consistent should set him up for continued success as a middle reliever with the occasional flex into higher-leverage situations in the future for this bullpen.

```python
pn = 'Shugart, Chase'
df = pps[pps.player_name == pn]
level = ['player_name'
         ,'game_year'
         ,'p_throws'
         #,'stand'
        ]
kpis = ['pitches'
        ,'plate_apps'
        ,'games'
        ,'ba','obp','slg','ops'
        ,'woba'
        ,'krate'
        ,'bbrate'
        ,'whiff_rate'
        ,'chase_rate'
        #,'First Pitch Strike Rate'
        ,'hard_hit_rate'
        ,'barrel_rate'
        ,'in_zone_rate'
        ,'whiff_rate_iz'
        ,'contact_rate_ooz'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique')
                                                        )
                    ,on = level, how = 'left', suffixes = ('','_gms')
                   ).merge(whiff_rate(level,df)
                           ,on = level, how = 'left', suffixes = ('','_wr')
                          ).merge(chase_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_cr')
                                 ).merge(fpsr(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_fpsr')
                                        ).merge(putaway_rate(level,df)
                                                ,on = level, how = 'left', suffixes = ('','_par')
                                               ).merge(hard_hit_rate(level,df)
                                                       ,on = level, how = 'left', suffixes = ('','_hh')
                                                      ).merge(barrel_rate(level,df)
                                                              ,on = level, how = 'left', suffixes = ('','_br')
                                                             ).merge(whiff_rate(level,df[df.zone < 10])
                                                                     ,on = level, how = 'left', suffixes = ('','_iz')
                                                                    ).merge(whiff_rate(level,df[df.zone > 9])
                                                                            ,on = level, how = 'left', suffixes = ('','_ooz')
                                                                           )
z['contact_rate_ooz'] = 1-z.whiff_rate_ooz
z[level+kpis].round(3)

# Also need to throw a pitch plot in here for reference
# Pitch Plot
fig = px.scatter(df[df.player_name == pn]
                 ,x='pfx_x'
                 ,y='pfx_z'
                 ,color='pitch_name'
                 ,title = "{} {} Pitch Plot".format(pn.split(', ')[1]
                                                    ,pn.split(', ')[0]
                                                   )
                 ,template = 'plotly_dark'
                 ,labels=data_dictionary
                 ,subtitle = "Outlier cutter, most likely due to the horizontal movement (not really). Also looks to get good run on his sinker (meh). Wide spread of pitches in general."
                )
fig.add_hline(y=0
              ,line_dash='dot'
             )
fig.add_vline(x=0
              ,line_dash='dot'
             )
fig.show()

# Context pitch plot (RHPs in my dataset)
cntxt = pd.concat([pos[pos.p_throws == 'R']
                   ,pps[pps.p_throws == 'R']
                   ,nphl[nphl.p_throws == 'R']
                  ])
fig = px.scatter(cntxt[cntxt.pitch_type.isin(['SI','FC','ST'])]
                 ,x='pfx_x'
                 ,y='pfx_z'
                 ,color='pitch_name'
                 ,title = "RHP Pitch Plots of Sinkers, Cutters, and Sweepers"
                 ,template = 'plotly_dark'
                 ,labels=data_dictionary
                 #,subtitle = "Outlier cutter, most likely due to the horizontal movement. Also looks to get good run on his sinker. Wide spread of pitches in general."
                )
fig.add_hline(y=0
              ,line_dash='dot'
             )
fig.add_vline(x=0
              ,line_dash='dot'
             )
fig.show()

level = ['player_name'
         ,'game_year'
         ,'p_throws'
         ,'stand'
        ]
kpis = ['pitches'
        ,'plate_apps'
        #,'games'
        ,'ba','obp','slg','ops'
        ,'woba'
        ,'krate'
        ,'bbrate'
        ,'whiff_rate'
        ,'chase_rate'
        #,'First Pitch Strike Rate'
        ,'hard_hit_rate'
        ,'barrel_rate'
        ,'in_zone_rate'
        ,'whiff_rate_iz'
        ,'contact_rate_ooz'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique')
                                                        )
                    ,on = level, how = 'left', suffixes = ('','_gms')
                   ).merge(whiff_rate(level,df)
                           ,on = level, how = 'left', suffixes = ('','_wr')
                          ).merge(chase_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_cr')
                                 ).merge(fpsr(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_fpsr')
                                        ).merge(putaway_rate(level,df)
                                                ,on = level, how = 'left', suffixes = ('','_par')
                                               ).merge(hard_hit_rate(level,df)
                                                       ,on = level, how = 'left', suffixes = ('','_hh')
                                                      ).merge(barrel_rate(level,df)
                                                              ,on = level, how = 'left', suffixes = ('','_br')
                                                             ).merge(whiff_rate(level,df[df.zone < 10])
                                                                     ,on = level, how = 'left', suffixes = ('','_iz')
                                                                    ).merge(whiff_rate(level,df[df.zone > 9])
                                                                            ,on = level, how = 'left', suffixes = ('','_ooz')
                                                                           )
z['contact_rate_ooz'] = 1-z.whiff_rate_ooz
z[level+kpis].round(3)

# Interesting platoon splits. Better BAA and OBP against LHB (fewer walks and stronger K Rate)
# But lefties hit him hard, more slug and barrels.
# Righties slugged less but hit better overall. They also walked more. He threw more pitches in the zone to righties but got less swing and misson those pitches in the zone.

# Let's check out a pitch map now
lpm = lhb_pitch_mix(df)
lpm['stand'] = 'L'
rpm = rhb_pitch_mix(df)
rpm['stand'] = 'R'
pm = pd.concat([lpm
                ,rpm]
              )
fig = px.scatter(pm
                 ,x='plate_x'
                 ,y='plate_z'
                 ,size='usage'
                 ,facet_col = 'stand'
                 ,title = "{} {} Pitch Map".format(pn.split(', ')[1]
                                                    ,pn.split(', ')[0]
                                                   )
                 ,template = 'plotly_dark'
                 ,subtitle = "Fairly even splits. Righties hit him more frequently and walk more but not as much pop. Lefties swing-and-miss more but do more damage when they connect."
                 ,labels = data_dictionary
                 ,color='pitch_name'
                )
fig.add_shape(type='rect'
              ,x0=-0.83,x1=0.83
              ,y0=df.sz_bot.mean(),y1=df.sz_top.mean()
              ,row='all',col='all'
             )
fig.show()

# Looking at his cutter. It is a strong pitch to throw against lefties and drives a lot of his success there
# But against righties it is not a good pitch to throw.
level = ['player_name'
         ,'game_year'
         #,'p_throws'
         ,'stand'
         ,'pitch_type'
        ]
kpis = ['pitches'
        #,'plate_apps'
        #,'games'
        ,'ba','obp','slg','ops'
        ,'woba'
        ,'krate'
        ,'bbrate'
        ,'whiff_rate'
        ,'chase_rate'
        ,'putaway_rate'
        #,'First Pitch Strike Rate'
        ,'hard_hit_rate'
        ,'barrel_rate'
        ,'in_zone_rate'
        ,'whiff_rate_iz'
        ,'contact_rate_ooz'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique')
                                                        )
                    ,on = level, how = 'left', suffixes = ('','_gms')
                   ).merge(whiff_rate(level,df)
                           ,on = level, how = 'left', suffixes = ('','_wr')
                          ).merge(chase_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_cr')
                                 ).merge(fpsr(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_fpsr')
                                        ).merge(putaway_rate(level,df)
                                                ,on = level, how = 'left', suffixes = ('','_par')
                                               ).merge(hard_hit_rate(level,df)
                                                       ,on = level, how = 'left', suffixes = ('','_hh')
                                                      ).merge(barrel_rate(level,df)
                                                              ,on = level, how = 'left', suffixes = ('','_br')
                                                             ).merge(whiff_rate(level,df[df.zone < 10])
                                                                     ,on = level, how = 'left', suffixes = ('','_iz')
                                                                    ).merge(whiff_rate(level,df[df.zone > 9])
                                                                            ,on = level, how = 'left', suffixes = ('','_ooz')
                                                                           ).merge(putaway_rate(level,df)
                                                                                   ,on = level, how = 'left', suffixes = ('','_par')
                                                                                  ).fillna(0)
z['contact_rate_ooz'] = 1-z.whiff_rate_ooz
z[z.pitch_type == 'FC'][level+kpis].round(3)

# Double-click into lefties
# Fascinating how effective his SI was against lefties. That is atypical.
z[z.stand == 'L'][level+kpis].round(3).sort_values(by='pitches',ascending=False)
# Double-click into righties
# His sinker also played well against righties although it got barreled at a decent clip. He was a bit wild with it.
# But he should aim to be more SI/ST against righties
z[z.stand == 'R'][level+kpis].round(3).sort_values(by='pitches',ascending=False)
# Then I want to know what kinds of pitches got strikeouts for him
# This is fairly remarkable that a majority of his strikeouts came on his sinker.
lpmk = lhb_pitch_mix(df[df.events.isin(['strikeout','strikeout_double_play'])])
lpmk['stand'] = 'L'
rpmk = rhb_pitch_mix(df[df.events.isin(['strikeout','strikeout_double_play'])])
rpmk['stand'] = 'R'
pmk = pd.concat([lpmk,rpmk])
zk = pmk.merge(nresults(['stand'],df)
          ,on = ['stand']
          ,suffixes = ('','_res')
         )
zk['kshare'] = zk['count']/zk.strikeouts
zk[['pitch_type'
    ,'pitch_name'
    ,'stand'
    ,'count'
    ,'kshare'
   ]].round(3).sort_values(by=['stand','kshare'],ascending=False)
# I want to see how his pitch mix evolved throughout the season
# Specifically, did his cutter usage change? How about to righties?
# I can roughly do this by looking at it by month.
pms = pd.DataFrame()
rpms = pd.DataFrame()
for m in df.month.unique().tolist():
    pm = pitch_mix(df[df.month == m])
    pm['month'] = m
    rpm = rhb_pitch_mix(df[df.month == m])
    rpm['month'] = m
    pms = pd.concat([pms,pm])
    rpms = pd.concat([rpms,rpm])
    print(m)
fig = px.line(pms.sort_values(by='month')
              ,x='month'
              ,y='usage'
              ,color = 'pitch_name'
              ,title = "Chase Shugart Pitch Usage by Month"
              ,subtitle = "His Cutter Usage actually took off at the end of the season."
              ,markers='all'
              ,template = 'plotly_dark'
              ,labels = data_dictionary | {'usage' : 'Pitch Usage'
                                           ,'month' : 'Month'
                                          }
             )
fig.show()
fig = px.line(rpms.sort_values(by='month')
              ,x='month'
              ,y='usage'
              ,color = 'pitch_name'
              ,title = "Chase Shugart Pitch Usage to RHB by Month"
              ,subtitle = "He backed off his Sweeper."
              ,markers='all'
              ,template = 'plotly_dark'
              ,labels = data_dictionary | {'usage' : 'Pitch Usage'
                                           ,'month' : 'Month'
                                          }
             )
fig.show()
# Ok one last thing to wonder about: Results by month?
# June was a mess and he walked a lot of guys then
# So limit the walks and you will likely have success?
level = ['player_name'
         ,'game_year'
         #,'p_throws'
         #,'stand'
         #,'pitch_type'
         ,'month'
        ]
kpis = ['pitches'
        ,'plate_apps'
        ,'games'
        ,'ba','obp','slg','ops'
        ,'woba'
        ,'krate'
        ,'bbrate'
        ,'whiff_rate'
        ,'chase_rate'
        #,'putaway_rate'
        #,'First Pitch Strike Rate'
        ,'hard_hit_rate'
        ,'barrel_rate'
        ,'in_zone_rate'
        ,'whiff_rate_iz'
        ,'contact_rate_ooz'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique')
                                                        )
                    ,on = level, how = 'left', suffixes = ('','_gms')
                   ).merge(whiff_rate(level,df)
                           ,on = level, how = 'left', suffixes = ('','_wr')
                          ).merge(chase_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_cr')
                                 ).merge(fpsr(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_fpsr')
                                        ).merge(putaway_rate(level,df)
                                                ,on = level, how = 'left', suffixes = ('','_par')
                                               ).merge(hard_hit_rate(level,df)
                                                       ,on = level, how = 'left', suffixes = ('','_hh')
                                                      ).merge(barrel_rate(level,df)
                                                              ,on = level, how = 'left', suffixes = ('','_br')
                                                             ).merge(whiff_rate(level,df[df.zone < 10])
                                                                     ,on = level, how = 'left', suffixes = ('','_iz')
                                                                    ).merge(whiff_rate(level,df[df.zone > 9])
                                                                            ,on = level, how = 'left', suffixes = ('','_ooz')
                                                                           ).merge(putaway_rate(level,df)
                                                                                   ,on = level, how = 'left', suffixes = ('','_par')
                                                                                  ).fillna(0)
z['contact_rate_ooz'] = 1-z.whiff_rate_ooz
z[level+kpis].round(3)

# # I feel like that is some decent slug to allow
# cntxt = pd.concat([pps,pos])
# level = ['player_name','game_year']
# zcntxt = nresults(level,cntxt)
# fig = px.scatter(zcntxt[zcntxt.plate_apps > 49]
#                  ,x='pitches'
#                  ,y='slg'
#                  ,title = "Slugging Percentage as a function of Pitches Seen"
#                  ,template = 'plotly_dark'
#                  ,subtitle = "How does Chase Shugart's .430 SLG allowed in 2026 look against this context? Fairly average, maybe a touch high."
#                  ,labels = data_dictionary
#                  ,marginal_y = 'histogram'
#                 )
# fig.add_hline(y=.430
#               ,line_dash = 'dot'
#               ,annotation_text = ".430 SLG"
#              )
# fig.show()

# His 10% barrel rate is high
```