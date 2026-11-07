# Alex McFarlane
Time to recap Alex McFarlane's 2026 season. Frankly, it has to go hand-in-hand with the guy who was drafted in the round following McFarlane back in 2022. A fellow right-handed college reliever from Florida, Orion Kerkering. Taken in the 5th round out of Central Florida, Kerk was rushed to the majors back in 2023 to pitch in leverage situations for several iterations of this ballclub.

Now it was Alex McFarlane's time to ascend to the big league bullpen. During the fateful weekend in Atlanta which cost Rob Thomson his job, Alex McFarlane sat in the Phillies bullpen. Ready to be used. He was not needed.

McFarlane dominated AA for most of 2026, I do not have statcast data for that. I do have data from his brief stint in AAA along with all 333 of his major league pitches across 21 outings including two postseason games.

McFarlane emerged as a key plank in the Bridge to Duran, the highwire act conducted by Don Mattingly when protecting a lead down the stretch for this ballclub. McFarlane's presence in the "Circle of Trust" belied his inexperience. His eye-popping stuff plays against big league hitters. Improved command in 2026 brought improved results with solid underlying metrics.


First we take a look at his overall year. He pitched to a .280 wOBA (good!) and .633 OPS (solid!). Decent chunk of hard hits and barrles, but very strong whiff in total and good chase. Pointing to quality stuff. 26% K and 8.2% BB are good. The ratio just exceeding 3:1 is quite good.

Then we look at his pitch plot which is... hard to contextualize. Lots of FF that ride between 12 and 18 inches and run about a foot. His sinker runs up to 18 inches. Bullet slider angles nicely off his FF which likely explains the deception to lefties. Speeds them up with heaters up and out over the plate. Follows that with a hammer slider that looks the same out of the hand before falling off the table. Sweeper sweeps at least a foot but is fairly flat., but can tunnel off his sinker when on.

Now we look at pitch maps to gauge approach against left-handed batters and right-handed batters. Callouts at the stand level include: Against LHB, quality K Rate (33%) and Elite Walks Rate (2%). While against RHB: Diverse pitch mix | Just .179 BAA but lots of hard contact in the underlyings (41% HH, 9% Barrel).

So then we look at his pitches against each batter handedness. Plus SL to LHB: 38% Whiff/50% Chase. FF gets 32% Whiff on Swings to RHB. (33% whiff vs LHB).

Which is indicating that he has an outlier fastball. So we build a graph to contextualize against other right-handed four-seam fastballs either thrown by Phillies pitchers or to Phillies batters since 2015. McFarlane has elite spin and elite velocity. His fastball is an outlier.

```python
pn = 'McFarlane, Alex'
df = pps#[pps.player_name == pn]
gy = 2026
df['am_color'] = np.where(df.player_name == pn
                          ,"Alex McFarlane"
                          ,"Context"
                         )
level = ['player_name'
         ,'game_year'
         ,'p_throws'
         ,'am_color'
        ]
kpis = ['pitches'
        ,'plate_apps'
        ,'games'
        ,'ba','obp','slg'
        ,'ops'
        ,'woba'
        ,'krate'
        ,'bbrate'
        ,'hr_rate'
        #,'runs_created'
        ,'whiff_rate'
        ,'chase_rate'
        ,'hard_hit_rate'
        ,'barrel_rate'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique'))
                    ,on = level, how = 'left', suffixes = ('_res','_gms')
                   ).merge(hard_hit_rate(level,df)
                           ,on = level, how = 'left', suffixes = ('','_hh')
                          ).merge(barrel_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_br')
                                 ).merge(whiff_rate(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_wr')
                                        ).merge(chase_rate(level,df)
                                                ,on = level, how = 'left', suffixes = ('','_cr')
                                               ).merge(fpsr(level,df)
                                                       ,on = level, how = 'left', suffixes = ('','_fpsr')
                                                      )
z[z.player_name == pn][level+kpis].round(3)

# Pitch Plot
fig = px.scatter(df[df.player_name == pn]
                 ,x='pfx_x'
                 ,y='pfx_z'
                 ,color='pitch_name'
                 ,title = "Alex McFarlane Pitch Plot"
                 ,template = 'plotly_dark'
                 ,labels=data_dictionary
                 ,subtitle = "Velocity is stronger than shape in his Stuff model"
                )
fig.add_hline(y=0
              ,line_dash='dot'
             )
fig.add_vline(x=0
              ,line_dash='dot'
             )
fig.show()
# Nasty stuff

# Stand Level - don't skip a step!
# Pull commentary for Pitch Map visual
level = ['player_name'
         ,'game_year'
         ,'p_throws'
         ,'am_color'
         ,'stand'
         #,'pitch_type','pitch_name'
        ]
kpis = ['pitches'
        ,'plate_apps'
        ,'games'
        ,'ba','obp','slg'
        ,'ops'
        ,'woba'
        ,'krate'
        ,'bbrate'
        ,'hr_rate'
        #,'runs_created'
        ,'whiff_rate'
        ,'chase_rate'
        ,'hard_hit_rate'
        ,'barrel_rate'
        # ,'usage'
        # ,'plate_x'
        # ,'plate_z'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique'))
                    ,on = level, how = 'left', suffixes = ('_res','_gms')
                   ).merge(hard_hit_rate(level,df)
                           ,on = level, how = 'left', suffixes = ('','_hh')
                          ).merge(barrel_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_br')
                                 ).merge(whiff_rate(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_wr')
                                        ).merge(chase_rate(level,df)
                                                ,on = level, how = 'left', suffixes = ('','_cr')
                                               ).merge(fpsr(level,df)
                                                       ,on = level, how = 'left', suffixes = ('','_fpsr')
                                                      )
z[z.player_name == pn][level+kpis].round(3)

# Pitch Map - Use the animation from Claude Design
pms = pd.DataFrame()
lpm = lhb_pitch_mix(df[df.player_name == pn])
lpm['stand'] = 'L'
rpm = rhb_pitch_mix(df[df.player_name == pn])
rpm['stand'] = 'R'
pms = pd.concat([lpm,rpm])
fig = px.scatter(pms
                 ,x='plate_x'
                 ,y='plate_z'
                 ,color='pitch_name'
                 ,size='usage'
                 #,title = "{} {} Pitch Map.".format(pn.split(', ')[1],pn.split(', ')[0])
                 ,template = 'plotly_dark'
                 ,labels=data_dictionary
                 ,facet_col = 'stand'
                 ,text='pitch_type'
                 ,subtitle = "vs LHB: 63.4% FF + 27.5% SL | Elite K Rate (33%) and Limits Walks (2% BB Rate.)"
                 #,subtitle = "vs RHB: 45.6% SI + 25% FF + 15.6% SL + 13.9% ST | Just .179 BAA but lots of hard contact in the underlyings"
                )
fig.add_shape(type='rect'
              ,x0=-0.83
              ,x1=0.83
              ,y0=df[df.player_name == pn].sz_bot.mean()
              ,y1=df[df.player_name == pn].sz_top.mean()
              ,row='all',col='all'
              ,fillcolor='gray'
              ,opacity=0.15
             )
fig.show()

# Pitch and Stand Level
level = ['player_name'
         ,'game_year'
         ,'p_throws'
         ,'am_color'
         ,'stand'
         ,'pitch_type'
         ,'pitch_name'
        ]
kpis = ['pitches'
        ,'plate_apps'
        ,'games'
        ,'ba','obp','slg'
        ,'ops'
        ,'woba'
        ,'krate'
        ,'bbrate'
        ,'hr_rate'
        #,'runs_created'
        ,'whiff_rate'
        ,'chase_rate'
        ,'hard_hit_rate'
        ,'barrel_rate'
        ,'usage'
        ,'plate_x'
        ,'plate_z'
        ,'putaway_rate'
        ,'in_zone_rate'
       ]
z = nresults(level,df
            ).merge(df.groupby(level,as_index=False).agg(games = ('game_pk','nunique'))
                    ,on = level, how = 'left', suffixes = ('_res','_gms')
                   ).merge(hard_hit_rate(level,df)
                           ,on = level, how = 'left', suffixes = ('','_hh')
                          ).merge(barrel_rate(level,df)
                                  ,on = level, how = 'left', suffixes = ('','_br')
                                 ).merge(whiff_rate(level,df)
                                         ,on = level, how = 'left', suffixes = ('','_wr')
                                        ).merge(chase_rate(level,df)
                                                ,on = level, how = 'left', suffixes = ('','_cr')
                                               ).merge(fpsr(level,df)
                                                       ,on = level, how = 'left', suffixes = ('','_fpsr')
                                                      ).merge(pms
                                                              ,on = ['stand','pitch_type'
                                                                    ,'pitch_name'], how = 'left', suffixes = ('','_pm')
                                                             ).merge(putaway_rate(level,df)
                                                                     ,on = level, how= 'left', suffixes = ('','_par')
                                                                    )
z[z.player_name == pn][level+kpis].round(3)

z[(z.stand == 'L')&(z.pitch_type == 'SL')&(z.player_name == pn)][level+['whiff_rate'
                                                                        ,'chase_rate'
                                                                        ,'putaway_rate'
                                                                        ,'usage'
                                                                        ,'release_speed'
                                                                        ,'release_spin_rate'
                                                                        ,'pfx_x'
                                                                        ,'pfx_z'
                                                                       ]].round(3)

z[(z.stand == 'L')&(z.pitch_type == 'FF')&(z.player_name == pn)][level+['whiff_rate'
                                                                        ,'chase_rate'
                                                                        ,'putaway_rate'
                                                                        ,'usage'
                                                                        ,'release_speed'
                                                                        ,'release_spin_rate'
                                                                        ,'pfx_x'
                                                                        ,'pfx_z'
                                                                       ]].round(3)

z[(z.stand == 'R')&(z.pitch_type.isin(['FF','SI','SL','ST']))&(z.player_name == pn)][level+['whiff_rate'
                                                                        ,'chase_rate'
                                                                        ,'putaway_rate'
                                                                        ,'usage'
                                                                        ,'release_speed'
                                                                        ,'release_spin_rate'
                                                                        ,'pfx_x'
                                                                        ,'pfx_z'
                                                                       ]].sort_values(by='usage',ascending=False).round(3)

zfig = z[z.player_name == pn][level+kpis].round(3)
fig = px.scatter(zfig
                 ,x='plate_x'
                 ,y='plate_z'
                 ,color='pitch_name'
                 ,size='usage'
                 ,title = "Pitch Map with Commentary"
                 #,title = "{} {} Pitch Map.".format(pn.split(', ')[1],pn.split(', ')[0])
                 ,template = 'plotly_dark'
                 ,labels=data_dictionary
                 ,facet_col = 'stand'
                 ,subtitle = "Plus SL to LHB: 38% Whiff/50% Chase. FF gets 32% Whiff on Swings to RHB. (33% whiff vs LHB)"
                 ,text='pitch_type'
                )
fig.add_shape(type='rect'
              ,x0=-0.83
              ,x1=0.83
              ,y0=df[df.player_name == pn].sz_bot.mean()
              ,y1=df[df.player_name == pn].sz_top.mean()
              ,row='all',col='all'
              ,fillcolor='gray'
              ,opacity=0.15
             )
fig.show()

# His fastball is probably what makes him elite
# Let's start with velo and spin
ff = pd.concat([pps[(pps.p_throws == 'R') & (pps.pitch_type == 'FF')]
                ,pos[(pos.p_throws == 'R') & (pos.pitch_type == 'FF')]
               ]
              )
df = ff
df['am_color'] = np.where(df.player_name == pn
                          ,"Alex McFarlane"
                          ,"Context"
                         )
level = ['player_name'
        ]
fig = px.scatter(df
                 ,x='release_spin_rate'
                 ,y='release_speed'
                 ,title = "Pitch Velocity as a function of Spin Rate"
                 ,subtitle = "Righty Four-Seam Fastballs thrown in any Phillies game since 2015."
                 ,color='am_color'
                 ,template='plotly_dark'
                 ,marginal_y = 'histogram'
                 ,marginal_x = 'histogram'
                 ,labels=data_dictionary | {'am_color' : 'Highlight Alex McFarlane'
                                            ,'release_speed' : 'Pitch Velocity (mph)'
                                            ,'release_spin_rate' : 'Spin Rate (rpm)'
                                           }
                )
fig.show()

# Alex McFarlane throws an outlier Four-Seam Fastball
```