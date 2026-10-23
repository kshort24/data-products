# EDA · dp_uc56 · subject_regular_season

_Written 2026-10-23 18:16 by phillies_dp.eda.to_file — 4,223 rows × 16 columns._

## Shape
```text
4223 rows x 16 columns
```

## Dtypes
```text
game_year                            Int64
pitch_type                          object
release_speed                      Float64
zone                               Float64
description                         object
events                              object
type                                object
bb_type                             object
launch_speed                       Float64
launch_angle                       Float64
estimated_ba_using_speedangle      Float64
estimated_woba_using_speedangle    Float64
bat_speed                          Float64
hc_x                               Float64
hc_y                               Float64
p_throws                            object
```

## Null counts
```text
                                 nulls   pct
game_year                            0   0.0
pitch_type                           1   0.0
release_speed                        0   0.0
zone                                 1   0.0
description                          0   0.0
events                            3078  72.9
type                                 0   0.0
bb_type                           3412  80.8
launch_speed                      2590  61.3
launch_angle                      2588  61.3
estimated_ba_using_speedangle     3419  81.0
estimated_woba_using_speedangle   3198  75.7
bat_speed                         2597  61.5
hc_x                              3412  80.8
hc_y                              3412  80.8
p_throws                             0   0.0
```

## describe()
```text
                                  count unique          top  freq         mean        std      min      25%     50%        75%       max
game_year                        4223.0   <NA>         <NA>  <NA>  2024.284632   1.206515   2022.0   2023.0  2024.0     2025.0    2026.0
pitch_type                         4222     16           FF  1279          NaN        NaN      NaN      NaN     NaN        NaN       NaN
release_speed                    4223.0   <NA>         <NA>  <NA>    88.985982   6.137815     47.5     84.7    89.9       93.9     101.9
zone                             4222.0   <NA>         <NA>  <NA>     9.244908   4.261161      1.0      5.0    11.0       13.0      14.0
description                        4223     13         ball  1086          NaN        NaN      NaN      NaN     NaN        NaN       NaN
events                             1145     18    field_out   434          NaN        NaN      NaN      NaN     NaN        NaN       NaN
type                               4223      3            S  2212          NaN        NaN      NaN      NaN     NaN        NaN       NaN
bb_type                             811      4  ground_ball   364          NaN        NaN      NaN      NaN     NaN        NaN       NaN
launch_speed                     1633.0   <NA>         <NA>  <NA>    81.034844  16.085354     15.7     70.7    80.2       93.9     113.7
launch_angle                     1635.0   <NA>         <NA>  <NA>    15.926606  33.189962    -84.0     -7.0    18.0       40.0      87.0
estimated_ba_using_speedangle     804.0   <NA>         <NA>  <NA>     0.331019   0.288323    0.001  0.08375  0.2575    0.51025       1.0
estimated_woba_using_speedangle  1025.0   <NA>         <NA>  <NA>     0.324589   0.374015      0.0    0.018   0.194      0.548       2.0
bat_speed                        1626.0   <NA>         <NA>  <NA>    71.004515   7.449086  3.38395     68.4    72.1  75.198675  87.02764
hc_x                              811.0   <NA>         <NA>  <NA>   119.574673  38.804478    17.56     98.7   113.8    142.185    229.65
hc_y                              811.0   <NA>         <NA>  <NA>   125.660703  41.255851    21.64   94.755   130.0    160.985    217.83
p_throws                           4223      2            R  2248          NaN        NaN      NaN      NaN     NaN        NaN       NaN
```

## head(20)
```text
        game_year pitch_type  release_speed  zone      description     events type      bb_type  launch_speed  launch_angle  estimated_ba_using_speedangle  estimated_woba_using_speedangle  bat_speed    hc_x   hc_y p_throws
306628       2022         FF           93.7   3.0    hit_into_play  field_out    X  ground_ball          82.0         -41.0                          0.091                            0.086       <NA>  106.39  167.3        R
306629       2022         FF           95.2   5.0             foul       None    S         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306630       2022         FF           94.2   9.0    called_strike       None    S         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306665       2022         CH           88.5  13.0  swinging_strike  strikeout    S         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306666       2022         SI           93.6   7.0             foul       None    S         None          79.6         -33.0                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306667       2022         CH           87.9   4.0             foul       None    S         None          72.6         -40.0                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306668       2022         FF           95.4  14.0     blocked_ball       None    B         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306669       2022         SI           94.6  14.0             ball       None    B         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306768       2022         FF           93.9  11.0  swinging_strike  strikeout    S         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306769       2022         SL           84.8  13.0             ball       None    B         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306770       2022         CU           85.0  14.0  swinging_strike       None    S         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306771       2022         CU           81.5  14.0    called_strike       None    S         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306856       2022         FF           93.2   2.0    hit_into_play  field_out    X     fly_ball          82.7          40.0                          0.026                            0.033       <NA>  120.78  88.68        L
306858       2022         SL           84.5  13.0             foul       None    S         None          91.4          24.0                           <NA>                             <NA>       <NA>    <NA>   <NA>        L
306864       2022         FF           93.4   5.0             foul       None    S         None          86.7          25.0                           <NA>                             <NA>       <NA>    <NA>   <NA>        L
306869       2022         SL           83.5   8.0  swinging_strike       None    S         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        L
306914       2022         FF           97.4   3.0         foul_tip  strikeout    S         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306919       2022         SI           95.3   8.0    called_strike       None    S         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306924       2022         FC           86.5  14.0  swinging_strike       None    S         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
306926       2022         FF           95.7  14.0             ball       None    B         None          <NA>          <NA>                           <NA>                             <NA>       <NA>    <NA>   <NA>        R
```
