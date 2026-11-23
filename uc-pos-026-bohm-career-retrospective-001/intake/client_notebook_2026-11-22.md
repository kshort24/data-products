# Alec Bohm
Career retrospective.

Touch on his performance in 2026. This should be a continuation of uc-pos-013. Contextualize that against his career with the Phillies then dig in to a career retrospective acting under the assumption that he will not be returning to the Phillies next season.

I have done some cursory work, but the agents should expand upon. If the line drive deficiency is a good angle, then include the spray chart that I started below but align it the spray chart visual I like with a simple outline of an outfield wall and diamond for the infield.

Highlight his run creation and skill with runners in scoring position. I identified a long (and boring) video of him driving in game-winning runs. I also manually put together the helmet spike compilation. Neither of these are relevant to the analysis, but I am including them in the code that I am sharing just for organization within my notebooks.

```python
# Damn I did promise some people that I would do Alec Bohm helmet spikes
# concat_mp4s_in_folder('Alec Bohm Helmet Spike Compilation')

# But I would like to do Alec Bohm game-winning runs for the Phillies

bohm = pos[pos.player_name == 'Bohm, Alec']
df = bohm[bohm.post_bat_score > bohm.bat_score].merge(gms[gms.wl == 'W'], on = ['game_pk','game_date','game_year','away_team','home_team'])
gw = df[(df.bat_score <= df.runs_against)&(df.post_bat_score > df.runs_against)]
cols = ['game_date'
        ,'game_year'
        ,'inning'
        ,'events'
        ,'bat_score','post_bat_score'
        ,'runs_against'
        ,'runs_for'
       ]
gw[gw.game_year == 2026][cols].sort_values(by='game_date')

#concat_mp4s_in_folder('Alec Bohm driving in the deciding run in games the Phillies won',18)

df = bohm
level = ['player_name'
         ,'game_year'
         ,'stand'
        ]
kpis = ['pitches'
        ,'plate_apps'
        ,'games'
        ,'ba','obp','slg'
        ,'ops'
        ,'woba'
        ,'ba_risp'
        ,'runs_created'
        ,'hard_hit_rate'
        ,'barrel_rate'
        ,'line_drive_rate'
        ,'pull_air_rate'
        #,'pull_rate'
        ,'whiff_rate'
        ,'krate'
        ,'bbrate'
        #,'la_mu'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique'))
                    ,on = level, how = 'left', suffixes = ('','_gms')
                   ).merge(runs_created(level,df)
                           ,on = level, how = 'left', suffixes = ('','_rc')
                          ).merge(hard_hit_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_hh')
                                 ).merge(barrel_rate(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_br')
                                        ).merge(bb_type_by_level(level,df[df.bb_type == 'line_drive'])
                                                ,on = level, how = 'left', suffixes = ('','_ld')
                                               ).merge(nresults(level,df[(df.on_2b.isna() == False) | (df.on_3b.isna() == False)])
                                                       ,on = level, how = 'left', suffixes = ('','_risp')
                                                      ).merge(pull_air_rate(level,df)
                                                              ,on = level, how = 'left', suffixes = ('','_par')
                                                             ).merge(whiff_rate(level,df)
                                                                     ,on = level, how = 'left', suffixes = ('','_wr')
                                                                    ).merge(whiff_rate(level,df[df.zone < 10])
                                                                            ,on = level, how = 'left', suffixes = ('','_iz')
                                                                           ).merge(inds(level,df)
                                                                                   ,on = level, how = 'left', suffixes = ('','_inds')
                                                                                  ).fillna(0)
z['line_drive_rate'] = z.bips_ld/z.bip
z[level+kpis].round(3)

zfig = bb_type_by_level(level,df)
fig = px.bar(zfig
             ,x='game_year'
             ,y='share'
             ,facet_col = 'bb_type',facet_col_wrap = 2
             ,title = "Alec Bohm Batted Balls by Type"
             ,template = 'plotly_dark'
             ,text = 'share'
             ,color='bb_type'
             ,labels = data_dictionary | {'bb_type' : 'Batted Ball Type'
                                          ,'share' : 'Share of Batted Balls'
                                         }
            )
fig.show()

# I think Bohm did not hit enough line drives in 2026
ld = bohm[bohm.bb_type == 'line_drive']
fig = px.scatter(ld.sort_values(by='game_year')
                 ,x='loc_x'
                 ,y='loc_y'
                 ,facet_col='game_year',facet_col_wrap=4
                 ,color='events'
                 ,title = "Spray Chart of Alec Bohm Line Drives"
                 ,template = 'plotly_dark'
                 ,labels = data_dictionary
                )
fig.show()

# Check on platoon splits
level = ['player_name'
         ,'game_year'
         ,'p_throws'
        ]
kpis = ['pitches'
        ,'plate_apps'
        ,'games'
        ,'ba','obp','slg'
        ,'ops'
        ,'woba'
        ,'ba_risp'
        ,'runs_created'
        ,'hard_hit_rate'
        ,'barrel_rate'
        ,'line_drive_rate'
        ,'pull_air_rate'
        #,'pull_rate'
        ,'whiff_rate'
        ,'krate'
        ,'bbrate'
        #,'la_mu'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique'))
                    ,on = level, how = 'left', suffixes = ('','_gms')
                   ).merge(runs_created(level,df)
                           ,on = level, how = 'left', suffixes = ('','_rc')
                          ).merge(hard_hit_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_hh')
                                 ).merge(barrel_rate(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_br')
                                        ).merge(bb_type_by_level(level,df[df.bb_type == 'line_drive'])
                                                ,on = level, how = 'left', suffixes = ('','_ld')
                                               ).merge(nresults(level,df[(df.on_2b.isna() == False) | (df.on_3b.isna() == False)])
                                                       ,on = level, how = 'left', suffixes = ('','_risp')
                                                      ).merge(pull_air_rate(level,df)
                                                              ,on = level, how = 'left', suffixes = ('','_par')
                                                             ).merge(whiff_rate(level,df)
                                                                     ,on = level, how = 'left', suffixes = ('','_wr')
                                                                    ).merge(whiff_rate(level,df[df.zone < 10])
                                                                            ,on = level, how = 'left', suffixes = ('','_iz')
                                                                           ).merge(inds(level,df)
                                                                                   ,on = level, how = 'left', suffixes = ('','_inds')
                                                                                  ).fillna(0)
z['line_drive_rate'] = z.bips_ld/z.bip
z[level+kpis].round(3)

fig = px.bar(z
                 ,x='game_year'
                 ,y='woba'
                 #,size='plate_apps'
                 ,text='woba'
                 ,color='p_throws'
                 ,title = "Alec Bohm wOBA split by pitcher handedness"
             ,subtitle = "Bohm continued to be solid against lefties but struggled against righties too much in 2026."
                 ,template = 'plotly_dark'
             ,barmode='group'
                 #,facet_col='p_throws'
                 ,labels=data_dictionary
                )
fig.show()

z[z.p_throws == 'R'][level+kpis].round(3)
# Hard Hit Rate was consistent, barrel rate mostly fine, but his line drive rate did sink a bit.

bbtr = bb_type_by_level(level,df[df.p_throws == 'R'])
bbtr[bbtr.bb_type == 'ground_ball'] # He did hit more groundballs but not a ton more. In his best years against righties he was in the air more

# First look, I don't care about popups.
cntxt = pd.concat([pos[(pos.stand == 'R') & (pos.p_throws == 'R')]
                   ,pps[(pps.stand == 'R') & (pps.p_throws == 'R')]
                   ,nphl[(nphl.stand == 'R') & (nphl.p_throws == 'R')]
                  ]
                 )
level = ['player_name'
         ,'game_year'
         ,'ab_color'
        ]
cntxt['ab_color'] = np.where(cntxt.player_name == 'Bohm, Alec'
                             ,'Alec Bohm'
                             ,'Context'
                            )
zc = nresults(level,cntxt).merge(bb_type_by_level(level,cntxt)
                                 ,on = level, how = 'left', suffixes = ('','_bbt')
                                )
fig = px.scatter(zc[(zc.bb_type != 'popup') & (zc.plate_apps > 49)]
                 ,facet_col = 'bb_type',facet_col_wrap = 3
                 ,title = "wOBA as a function of Batted Ball Share."
                 ,subtitle = "RHB against RHP Player-Seasons in my dataset. Min 50 PAs. Highlight Alec Bohm"
                 ,color = 'ab_color'
                 ,template = 'plotly_dark'
                 ,x='share'
                 ,y='woba'
                 ,labels = data_dictionary | {'share' : 'Share of BIPs'
                                              ,'ab_color' : 'Is Alec Bohm?'
                                             }
                 ,hover_data = level
                 ,trendline='ols'
                )
fig.show()

# Idk exactly what I was going for here
# So dig in to his performance against RHP by looking at the pitch group level
df = bohm[bohm.p_throws == 'R']
level = ['player_name'
         ,'game_year'
         ,'pitch_group'
        ]
kpis = ['pitches'
        ,'plate_apps'
        ,'games'
        ,'ba','obp','slg'
        ,'ops'
        ,'woba'
        ,'ba_risp'
        ,'runs_created'
        ,'hard_hit_rate'
        ,'barrel_rate'
        ,'line_drive_rate'
        ,'pull_air_rate'
        #,'pull_rate'
        ,'whiff_rate'
        ,'krate'
        ,'bbrate'
        #,'la_mu'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique'))
                    ,on = level, how = 'left', suffixes = ('','_gms')
                   ).merge(runs_created(level,df)
                           ,on = level, how = 'left', suffixes = ('','_rc')
                          ).merge(hard_hit_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_hh')
                                 ).merge(barrel_rate(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_br')
                                        ).merge(bb_type_by_level(level,df[df.bb_type == 'line_drive'])
                                                ,on = level, how = 'left', suffixes = ('','_ld')
                                               ).merge(nresults(level,df[(df.on_2b.isna() == False) | (df.on_3b.isna() == False)])
                                                       ,on = level, how = 'left', suffixes = ('','_risp')
                                                      ).merge(pull_air_rate(level,df)
                                                              ,on = level, how = 'left', suffixes = ('','_par')
                                                             ).merge(whiff_rate(level,df)
                                                                     ,on = level, how = 'left', suffixes = ('','_wr')
                                                                    ).merge(whiff_rate(level,df[df.zone < 10])
                                                                            ,on = level, how = 'left', suffixes = ('','_iz')
                                                                           ).merge(inds(level,df)
                                                                                   ,on = level, how = 'left', suffixes = ('','_inds')
                                                                                  ).fillna(0)
z['line_drive_rate'] = z.bips_ld/z.bip
z[level+kpis].round(3)

zfig = z[z.pitch_group != 'Other'][level+kpis].round(3)
fig = px.bar(zfig.sort_values(by=['game_year','pitches'])
             ,x='game_year'
             ,y='woba'
             ,color='pitch_group'
             ,facet_col='pitch_group',facet_col_wrap=4
             ,text='woba'
             ,template='plotly_dark'
             ,title = "Alec Bohm wOBA against RHP by Pitch Group"
             ,labels=data_dictionary | {'pitch_group' : 'Pitch Group'}
             ,subtitle = "He stopped being able to hit righty breaking balls."
            )
fig.show()

# However, his underlyings appear to be pretty strong against this pitch group in 2026.
# His hard hit rate was the highest it has been since 2020
# His barrel rate was just under 6% which is where it has been in the past
# His line drive rate was in line with prior years
# Pull air rate seems to be all over the place
zfig[zfig.pitch_group == 'Breaking']

# Define a new set of KPIs and examine at the pitch group level before trying to see if the pitch_type tells us anything
# Underlyings still look pretty solid.
df = bohm[(bohm.p_throws == 'R') & (bohm.pitch_group == 'Breaking')]
level = ['player_name'
         ,'game_year'
         ,'pitch_group'
         #,'pitch_type'
        ]
kpis = ['pitches'
        ,'ba','obp','slg'
        ,'ops'
        ,'woba'
        ,'hard_hit_rate'
        ,'barrel_rate'
        ,'line_drive_rate'
        ,'pull_air_rate'
        ,'whiff_rate'
        ,'chase_rate'
        ,'whiff_rate_iz'
        ,'ev_mu'
        ,'la_mu'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique'))
                    ,on = level, how = 'left', suffixes = ('','_gms')
                   ).merge(runs_created(level,df)
                           ,on = level, how = 'left', suffixes = ('','_rc')
                          ).merge(hard_hit_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_hh')
                                 ).merge(barrel_rate(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_br')
                                        ).merge(bb_type_by_level(level,df[df.bb_type == 'line_drive'])
                                                ,on = level, how = 'left', suffixes = ('','_ld')
                                               ).merge(nresults(level,df[(df.on_2b.isna() == False) | (df.on_3b.isna() == False)])
                                                       ,on = level, how = 'left', suffixes = ('','_risp')
                                                      ).merge(pull_air_rate(level,df)
                                                              ,on = level, how = 'left', suffixes = ('','_par')
                                                             ).merge(whiff_rate(level,df)
                                                                     ,on = level, how = 'left', suffixes = ('','_wr')
                                                                    ).merge(whiff_rate(level,df[df.zone < 10])
                                                                            ,on = level, how = 'left', suffixes = ('','_iz')
                                                                           ).merge(inds(level,df)
                                                                                   ,on = level, how = 'left', suffixes = ('','_inds')
                                                                                  ).merge(chase_rate(level,df)
                                                                                          ,on = level, how = 'left', suffixes = ('','cr')
                                                                                         ).fillna(0)
z['line_drive_rate'] = z.bips_ld/z.bip
z[level+kpis].round(3)

df = bohm[(bohm.p_throws == 'R') & (bohm.pitch_group == 'Breaking')]
level = ['player_name'
         ,'game_year'
         ,'pitch_group'
         ,'pitch_type'
        ]
kpis = ['pitches'
        ,'ba','obp','slg'
        ,'ops'
        ,'woba'
        ,'hard_hit_rate'
        ,'barrel_rate'
        ,'line_drive_rate'
        ,'pull_air_rate'
        ,'whiff_rate'
        ,'chase_rate'
        ,'whiff_rate_iz'
        ,'ev_mu'
        ,'la_mu'
        ,'putaway_rate'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique'))
                    ,on = level, how = 'left', suffixes = ('','_gms')
                   ).merge(runs_created(level,df)
                           ,on = level, how = 'left', suffixes = ('','_rc')
                          ).merge(hard_hit_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_hh')
                                 ).merge(barrel_rate(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_br')
                                        ).merge(bb_type_by_level(level,df[df.bb_type == 'line_drive'])
                                                ,on = level, how = 'left', suffixes = ('','_ld')
                                               ).merge(nresults(level,df[(df.on_2b.isna() == False) | (df.on_3b.isna() == False)])
                                                       ,on = level, how = 'left', suffixes = ('','_risp')
                                                      ).merge(pull_air_rate(level,df)
                                                              ,on = level, how = 'left', suffixes = ('','_par')
                                                             ).merge(whiff_rate(level,df)
                                                                     ,on = level, how = 'left', suffixes = ('','_wr')
                                                                    ).merge(whiff_rate(level,df[df.zone < 10])
                                                                            ,on = level, how = 'left', suffixes = ('','_iz')
                                                                           ).merge(inds(level,df)
                                                                                   ,on = level, how = 'left', suffixes = ('','_inds')
                                                                                  ).merge(chase_rate(level,df)
                                                                                          ,on = level, how = 'left', suffixes = ('','cr')
                                                                                         ).merge(putaway_rate(level,df)
                                                                                                 ,on = level, how = 'left', suffixes = ('','par')
                                                                                                ).fillna(0)
z['line_drive_rate'] = z.bips_ld/z.bip
z[z.pitches > 9][level+kpis].round(3)

# Checked LD Rate, Barrel Rate, Hard Hit Rate. Maybe some difficulty against the curve?
# wOBA not super consequential either. How about swing decisions? Chase/Whiff/In Zone Whiff/Putaway
zfig = z[(z.pitch_type.isin(['SL','ST','KC','CU']))][level+kpis].round(3)
fig = px.scatter(zfig
                 ,x='game_year'
                 ,y='woba'
                 ,size='pitches'
                 ,color='pitch_type'
                 ,facet_col='pitch_type',facet_col_wrap=2
                 ,title = "Alec Bohm wOBA against RHP Breaking Balls"
                 ,template = 'plotly_dark'
                 ,labels = data_dictionary
                )
fig.show()

# How about swing decisions? Chase/Whiff/In Zone Whiff/Putaway
# Nothing is jumping out to me as abnormal from prior years.
zfig = z[(z.pitch_type.isin(['SL','ST','KC','CU']))][level+kpis].round(3)
fig = px.scatter(zfig
                 ,x='game_year'
                 ,y='putaway_rate'
                 ,size='pitches'
                 ,color='pitch_type'
                 ,facet_col='pitch_type',facet_col_wrap=2
                 ,title = "Alec Bohm Putaway Rate against RHP Breaking Balls"
                 ,template = 'plotly_dark'
                 ,labels = data_dictionary
                )
fig.show()

# Was he really just unlucky in 2026?

level = ['player_name'
         ,'game_year'
         ,'pitch_group'
         #,'pitch_type'
        ]
df.groupby(level,as_index=False).agg(mu_xba = ('estimated_ba_using_speedangle','mean')
                                     ,mu_xwoba = ('estimated_woba_using_speedangle','mean')
                                     ,mu_xslg = ('estimated_slg_using_speedangle','mean')
                                    )
df['hit_id'] = np.where(df.events.isin(hits)
                        ,"Base Hit"
                        ,"Not a hit"
                       )
fig = px.scatter(df[(df.estimated_ba_using_speedangle > .5)&(df.type == 'X')] # BIPs
                 ,x='launch_angle'
                 ,y='estimated_ba_using_speedangle'
                 ,color='hit_id'
                 ,facet_col = 'game_year',facet_col_wrap = 4
                 ,template = 'plotly_dark'
                 ,title = "xBA using EV and LA as a function of Launch Angle"
                 ,subtitle = "Alec Bohm against RHP Breaking Balls. Color by if the BIP was a hit or not."
                 ,labels = data_dictionary
                )
fig.show()

z = df[(df.estimated_ba_using_speedangle > .5)&(df.type == 'X')].groupby(level,as_index=False
                                                                    ).agg(likely_hits = ('des','size')
                                                                         ).merge(df[(df.estimated_ba_using_speedangle > .5)&(df.type == 'X') & (df.hit_id == 'Base Hit')].groupby(level,as_index=False
                                                                                                                                                     ).agg(hits = ('des','size')
                                                                                                                                                           )
                                                                                 ,on = level, how = 'left', suffixes = ('','_hits')
                                                                                ).fillna(0)
z['hit_rate'] = z.hits/z.likely_hits
z.round(3) # Not an overtly unlucky year (76% of his batted balls with xBA above .500 turnd into hits)

fig = px.scatter(df[df.type == 'X'].sort_values(by='game_year')
                 ,x='loc_x'
                 ,y='loc_y'
                 ,facet_col='game_year',facet_col_wrap=4
                 ,color='events'
                 ,title = "Spray Chart of Alec Bohm Balls in Play against RHP Breaking Balls"
                 ,template = 'plotly_dark'
                 ,labels = data_dictionary
                )
fig.show()
```