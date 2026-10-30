# Kyle Schwarber
What happened to this man? Should we be concerned? Perhaps...

It was his back?

Did he lose his pop?

These narratives will inform the larger Kyle Schwarber 2026 Season Recap use case. For this moment, I want to focus on something related but a little more specific. I want to build a narrative that will be animated by Claude Design. The mp4 of that animation will be concatenated with videos that I pull of his home runs from Baseball Savant. Together, this will form the video to accompany Kyle Schwarber's 2026 season recap.

So we are ONLY focusing on that, high level design:
- Cumulative home runs by season, so we start by defining the axes and drawing a step graph (?) line chart that moves across his cumulative plate appearances and accumulates his home runs. One line for each season, in chronological order. Provide a different color for his pre-Phillies tenure. All the years can move together.
- Then fill in the previous Phillies years, in a different shade of gray than the pre-Phillies teams.
- Then we will more deliberately follow the 2026 trend line, stopping a few times to highlight important home runs.

Home runs to highlight:
- Max EV
- Max distance
- Max WPA
- Specific games? At least the walk-off against St. Louis, did he have a three-homer game?

I can handle the editing myself in terms of integrating these clips, but I would like to see a nice transition where it cuts something off and transitions to the video clip.

Ok, so I need to provide the homers of interest for 2026, but when we get to the end of the line I want to hold the visual of the cumulative home runs.
<br> This should transition into a table of his single-season home run totals and we see where 2026 falls.

From there, we transition to the next visual which will be a spray chart of his home runs.
- Keep the layout simple, sketch an outline of the Citizens Bank Park outfield wall then place 45 dots for his home runs, color by pitcher handedness
- Commentary on this will contextualize the perceived loss of thump
- Contextualize his exit velocities, home run distance, and barrel rate.

Lastly, we will separate out two pitch map views, one for left-handed pitchers and one for righties. The color here will be the pitch_group column I typically determine in my code based on pitch_type.
- As we dig in to LHP, let's transition to a couple clips of him hitting dongs off lefty fastballs
- Then we return to the pitch map view and examine anything about RHP

Transitions back from a video clip to the visual will need to be clean, likely zooming out from the specific example we were looking at to take in the whole view.

Given that this is over, let's return with a consolidated view of the three screens before wrapping.

PYTHON CODE FOR REFERENCE:
```python
df = ks26 = pd.read_csv("c:\\Users\\kshort4\\Downloads\\ks26.csv")
ks26['src'] = '2026'
ks_pos = pd.read_csv("c:\\Users\\kshort4\\Downloads\\ks_pos.csv")
ks_pos['src'] = 'Phillies Tenure'
ks_nphl = pd.read_csv("c:\\Users\\kshort4\\Downloads\\ks_nphl.csv")
ks_nphl['src'] = 'Non-Phillies'
df = pd.concat([ks26[ks26.game_type == 'R'],ks_pos[ks_pos.game_type == 'R'],ks_nphl[ks_nphl.game_type == 'R']])
df['game_dt'] = pd.to_datetime(df.game_date)
df['month'] = df.game_dt.dt.month
df['pitch_group'] = np.select([df.pitch_type.isin(['FF','SI','FC'])
                               ,df.pitch_type.isin(['CH','FS','FO','SC'])
                               ,df.pitch_type.isin(['CU','KC','SL','ST','SV','CS','KN'])
                              ]
                              ,["Fastballs"
                                ,"Offspeed"
                                ,"Breaking"
                               ]
                              ,"Other"
                             )
df.groupby('month',as_index=False
          ).agg(pitches = ('des','size')
               )

data_dictionary = {'cumulative_pa' : 'Plate Appearance'
                         ,'cumulative_hrs' : 'Home Runs'
                         ,'src' : 'Tenure'
                        }

hrs = df[df.events == 'home_run'].sort_values(by=['game_year'
                    ,'game_date'
                    ,'game_pk'
                    ,'at_bat_number'
                   ]
               )
hrs.groupby('game_year',as_index=False
           ).agg(home_runs = ('des','size')
                ).sort_values(by='home_runs',ascending=False)

# Cumulative home runs, contextualized against his previous Phillies seasons and his entire career
# At the end the annotations at the end of each line should pleasantly transition into a table that ranks his cumulative_hrs for that game_year
hrs['cumulative_hrs'] = hrs.groupby('game_year').cumcount() + 1

z = df.merge(
    hrs[['game_year',
         'game_date',
         'game_pk',
         'at_bat_number',
         'cumulative_hrs']],
    on=['game_year', 'game_date', 'game_pk', 'at_bat_number'],
    how='left'
)

zfig = z.sort_values(
    by=['game_year',
        'game_date',
        'game_pk',
        'at_bat_number']
)

# Carry HR total forward until the next HR
zfig['cumulative_hrs'] = (
    zfig.groupby('game_year')['cumulative_hrs']
        .ffill()
        .fillna(0)
        .astype(int)
)

# Cumulative plate appearances
zfig['cumulative_pa'] = zfig.groupby('game_year').cumcount() + 1

zfig['Season'] = zfig['game_year'].astype(str)

fig = px.line(zfig
              ,x='cumulative_pa'
              ,y='cumulative_hrs'
              ,color='Season'
              ,facet_col = 'src'
              ,title='Kyle Schwarber Cumulative Home Runs'
              ,template='plotly_dark'
              ,labels = data_dictionary | {'cumulative_pa' : 'Plate Appearance'
                         ,'cumulative_hrs' : 'Home Runs'
                         ,'src' : 'Tenure'
                        }
             )

fig.show()
hrs.groupby('game_year',as_index=False
           ).agg(home_runs = ('des','size')
                ).sort_values(by='home_runs',ascending=False)

# Then draw a spray chart of the highlighted year and provide some context about the boom (max EV, mu EV, max Dist, mu Dist, Barrel Rate)
# I really need my loc_x and loc_y columns in order to do this

# fig = px.scatter(hrs[hrs.game_year > 2021].sort_values(by='game_year'
#                                                        #,ascending=False
#                                                       )
#                  ,x='loc_x'
#                  ,y='loc_y'
#                  ,title = "Spray Chart of Kyle Schwarber's Home Runs"
#                  ,template = 'plotly_dark' # Use a much simpler design, include a basic "V" shape for the foul line with an infield arc and a sketch of the Citizens Bank Park Outfield Wall
#                  ,color = 'p_throws'
#                  ,labels = data_dictionary
#                  ,facet_col = 'season'
#                 )
# fig.show()

# Going to at least get the calculations ready
df = hrs[hrs.game_year > 2021]
level = ['player_name'
         ,'game_year'
        ]
z = df.groupby(level,as_index=False
          ).agg(total_hrs = ('des','size')
                ,max_ev = ('launch_speed','max')
                ,mu_ev = ('launch_speed','mean')
                ,max_dist = ('hit_distance_sc','max')
                ,mu_dist = ('hit_distance_sc','mean')
               ).merge(df[df.launch_speed_angle == 6].groupby(level,as_index=False).agg(barrels = ('des','size'))
                       ,on = level, how = 'left', suffixes = ('','_br')
                      )
z['Barrels/HR'] = z.barrels/z.total_hrs
z
# The 113 mph Max EV was the lowest of his Phillies tenure and the 106.3 average EV was also the lowest.
# His average home run was shorter than ever (Phillies era) and his longest was shorter than all but one season. 
# 91% of his home runs were barrels which is also the second-lowest of his Phillies tenure.

# Next would be a view of "home run pitches" in the strike zone (catcher's perspective), split this out against pitcher handedness and color by pitch_group
fig = px.scatter(hrs[hrs.game_year == 2026].sort_values(by='p_throws')
                 ,x='plate_x'
                 ,y='plate_z'
                 ,color='pitch_group'
                 ,title = "Pitch Map of Kyle Schwarber's 2026 Home Runs"
                 ,facet_col = 'p_throws'
                 ,template = 'plotly_dark'
                 ,size = 'release_speed' # This should just be one size I think 0.25? or whatever I have in my repository for the width of a baseball
                 ,labels = data_dictionary
                 #,color = 'p_throws'
                )
fig.add_shape(type = 'rect'
              ,x0=-0.83, x1 = 0.83
              ,y0=ks26.sz_bot.mean()
              ,y1=ks26.sz_top.mean()
              ,row='all',col='all'
             )
fig.show()

df = hrs[hrs.game_year > 2021]
level = ['player_name'
         ,'game_year'
         ,'p_throws'
         ,'pitch_group'
        ]
z = df.groupby(level,as_index=False
          ).agg(total_hrs = ('des','size')
                ,max_ev = ('launch_speed','max')
                ,mu_ev = ('launch_speed','mean')
                ,max_dist = ('hit_distance_sc','max')
                ,mu_dist = ('hit_distance_sc','mean')
               ).merge(df[df.launch_speed_angle == 6].groupby(level,as_index=False).agg(barrels = ('des','size'))
                       ,on = level, how = 'left', suffixes = ('','_br')
                      )
z['Barrels/HR'] = z.barrels/z.total_hrs
# Look at LHP first
z[z.p_throws == 'L'].sort_values(by=['pitch_group','game_year']) # First hings first, ignore Offspeed!
# Then we also want to consider share of total homers?
# Well his ability to crush breaking balls even from lefties seems to be compromised. So we will look at the two homers he hit on lefty breaking balls and likely move on!

# Against RHP?
z[z.p_throws == 'R'].sort_values(by=['pitch_group','game_year']) # First hings first, ignore Offspeed!


# He was not absolutely crushing RHP Fastballs, but that could be a pitch type thing? It is on FF from RHP
# I want to watch him absolutely hammer a few four-seam fastballs before we wrap.
df = hrs[(hrs.pitch_group == 'Fastballs') & (hrs.p_throws == 'R')]
level = ['player_name'
         ,'game_year'
         ,'p_throws'
         ,'pitch_type'
        ]
z = df.groupby(level,as_index=False
          ).agg(total_hrs = ('des','size')
                ,max_ev = ('launch_speed','max')
                ,mu_ev = ('launch_speed','mean')
                ,max_dist = ('hit_distance_sc','max')
                ,mu_dist = ('hit_distance_sc','mean')
               ).merge(df[df.launch_speed_angle == 6].groupby(level,as_index=False).agg(barrels = ('des','size'))
                       ,on = level, how = 'left', suffixes = ('','_br')
                      )
z['Barrels/HR'] = z.barrels/z.total_hrs
z.groupby('game_year',as_index=False).agg(uq_pt = ('pitch_type','nunique'))
z[z.game_year > 2021].sort_values(by=['pitch_type','game_year'])

# Identify his big booms in 2026, some of these should be notes on the timeline, some of them will be DTs from the pitch map. I don't think the spray chart leads to homers? Maybe it should.
# Max EV
# Max Dist
# High WPA
# St. Louis homer if not already one of those
# Three homer game?
# Two homers off lefty breaking balls + Dylan Lee in the playoffs
# Three highest EV off RHP FF

# His playoff homer off Dylan Lee is fairly relevant for this video too, so need to figure out how to incorporate that?
cols = ['p_throws','pitch_type','launch_speed','launch_angle','hit_distance_sc','launch_speed_angle'
       ]
ks26[(ks26.events == 'home_run') & (ks26.game_type != 'R')][cols]

cols = ['game_date'
        ,'game_pk'
        ,'inning'
        ,'away_team'
        ,'home_team'
        ,'at_bat_number'
        ,'p_throws'
        ,'pitch_type'
        ,'launch_speed'
        ,'launch_angle'
        ,'hit_distance_sc'
        ,'launch_speed_angle'
        ,'delta_home_win_exp'
       ]
df = ks26[(ks26.events == 'home_run') & (ks26.game_type == 'R')][cols]
# df.sort_values(by='launch_speed',ascending=False) # Home run in the 9th inning of one of the doubleheader games against the Giants on 4/30
# df.sort_values(by='hit_distance_sc',ascending=False) # Coors Field blast in the 5th inning from April 3rd
# df.sort_values(by='delta_home_win_exp',ascending=False) # Even looking at the one from 6/28 in New York, it is the Cardinals walk off on 8/23, good!
# df.groupby(['away_team','home_team','game_date','game_pk'],as_index=False).agg(hrs = ('at_bat_number','size')).sort_values(by='hrs',ascending=False) # Three dongs against the Mets on 6/20
# df[(df.pitch_type.isin(['SL','ST','SV','CU','KC'])) & (df.p_throws == 'L')][cols] # Braves on 4/26 and Nats on 9/15 + ATL in playoffs
# df[(df.pitch_type == 'FF') & (df.p_throws == 'R')][cols].sort_values(by='launch_speed',ascending=False) # At Pittsburgh in May, Home against Colorado a week earlier and the Mets one from before
# Also since I can see it, the one against the Braves on Labor Day to deliver a victory would be cool too.
```