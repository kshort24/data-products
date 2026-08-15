# 06 · Consumer Success
**consumer-onboarding-agent · analytics-enabler · dashboard-specifier · query-builder**

## Persona guides

### Hitting Coach — *what to reinforce*
Your number is **first-pitch swing rate: 24.0% in May → 7.1% in August.** That is the largest,
cleanest, most-within-his-control change in the dataset. Chase rate confirms it (33.8% → 21.5%),
and out-of-zone whiff rate says he is also making better contact when he does expand.
**Reinforce the first-pitch discipline specifically** — not "keep doing what you're doing."
Read the right-hand panel before you give the cue: pitchers threw him a first-pitch strike only
41% of the time in August, down from 67% in April. Part of what looks like patience is being
handed to him. The plan is still correct; just do not credit him with all of it.

### Manager — *what to bet on*
August OBP is **.527** on 56 PA. The on-base profile is real and is consistent with a career-long
strength (83rd percentile OBP:K among Phillies hitter-seasons since 2015), but 56 partial-month
plate appearances will not confirm a new level. **The durable read is the season line, not August.**
If you are moving him up the order, the case rests on five seasons of OBP:K, not on 11 games.

### Performance Analyst — *what is signal*
March (13 PA) is below floor — do not rank it. August is above floor but partial. The two-step
shape (May step, Jun–Jul plateau, Aug step) is more interesting than the "steady climb" framing:
two steps invite *what changed at each step*. The FPSR collapse is the confound to chase down next
— a pitch-mix and zone-profile study would separate "pitching around him" from "attacking him
differently."

### Player — *the one-liner*
You are taking the first pitch and not chasing, and it is working. Pitchers have noticed and are
giving you less to hit. Nothing here says change anything.

## Common queries
```python
z = pd.read_csv('out/dp_uc33_monthly_master.csv')

z[~z.below_pa_floor][['month','woba','chase_rate','srfp','fpsr']]      # interpretable months only
z[z.month_is_partial]                                                   # what not to compare
walks_between_ks(['player_name','game_year'], pos[pos.player_name=='Stott, Bryson'])
ctx = pd.read_csv('out/dp_uc33_context_pool.csv')                       # any Phillies hitter
ctx[ctx.plate_apps>=50].nlargest(10,'bb_per_k')[['player_name','game_year','bb_per_k']]
```

## Interpretation rules
| Metric | Read it as | Do **not** |
|---|---|---|
| `fpsr`, `in_zone_rate` | what pitchers did **to** him | read as hitter behaviour |
| `chase_rate` | swing decision on out-of-zone pitches | compare across differing OOZ counts without the denominator |
| `bb_per_k` | walks per punchout | use when `k_free` is True — it is NULL by design |
| `max_bb_run` | a streak | substitute for `bb_per_k`; they are different statistics |
| any March row | nothing | interpret — 13 PA |

## Dashboard
`dp_uc33_stott_approach_change_dashboard.html` — self-contained, Plotly CDN, dark theme.
Six KPI tiles with month-over-month deltas · rolling-wOBA ghost-line chart · four-tab approach
panel (hitter / pitcher / contact / discipline) · monthly results · context scatter with the 3:2
ray · streak view with game table. Both selection-bias and partial-month warnings render inline.
