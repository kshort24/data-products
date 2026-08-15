# 06 · Consumer Success
**consumer-onboarding-agent · analytics-enabler · dashboard-specifier · query-builder**

## Persona guides

### Hitting Coach — *what to reinforce, and what not to*
Your number is **whiff rate: 20.5% → 15.9%**, and the strikeout rate that follows it (20.9% → 15.2%).
That is real, it is within his control, and it is the reason he is still in the lineup. Reinforce it.

**Do not reinforce the aggression.** Chase rate is flat at 37.5% — he did not become more selective,
he became *more* aggressive and got rewarded for it. First-pitch swing rate rose 33.6% → 43.0%, and
his production when **ahead** in the count collapsed from a .545 wOBA to .340. A hitter doing more
damage in neutral counts than in hitter's counts is a hitter who is not hunting.

The one target that has not moved at all is **launch angle: 2.28° → 2.22°**. Second percentile among
217 Phillies hitter-seasons since 2015. Ground-ball rate came down 5.6 points, which is something —
but the angle underneath it is identical, which means the batted-ball distribution shifted without
the swing changing. Treat the GB-rate improvement as noise until the angle moves with it.

### Manager — *what to bet on*
The improvement is real and it is smaller than it looks. Roughly two-thirds of the wOBA gain traces to
a 79-point BABIP jump on **softer** contact — his ground balls are 4.4 mph slower and getting 54 more
points of batting average. That is legs and placement. It is a genuine skill and it is volatile.

On the platoon: **the data does not support the shielding as currently practised.** His line against
left-handers has been *better* since Derek Hill arrived (.333/.391/.333 vs .143/.250/.143), on 23
plate appearances — too few to act on, which is precisely the argument for giving him the plate
appearances that would settle it. One left-hander in 42 August plate appearances does not generate
that evidence, and it makes August's .356 wOBA unreadable as a measure of progress.

Position him against the eight Phillies centre-field seasons in the context tab, not against his own
April. At matched volume he is **7th of 8 in wOBA and 4th of 8 in OBP** — the gap between those two
numbers is the season.

### Performance Analyst — *what is signal*
March (13 PA) and **August (42 PA)** are both below the 50-PA floor. Do not rank either. The August
exclusion matters most — it is the month the narrative rests on.

The two-panel discipline read is the useful frame: `chase_rate` and `whiff_rate` are his; `fpsr` and
`in_zone_rate` are what pitchers did **to** him. The cleanest single-cell finding is offspeed —
chase 50.0% → 35.3%, wOBA .168 → .303 — and it is **17 plate appearances**. Re-test it in September
before anyone builds a plan on it.

The next study is the sinker. He posts a .350 wOBA against sinkers on a 13.6% whiff rate, which
should not happen to a hitter with a 2° average launch angle. Understanding why he beats sinkers is
probably the most transferable thing in this dataset.

### Player Development — *the honest read*
He has proven the contact tool: a **12th-percentile whiff rate as a rookie** is a genuine major-league
skill and it is not going away. He has not proven the batted-ball profile can carry a regular. The
nine lowest launch angles in the Phillies pool since 2015 cluster between a .254 and a .374 wOBA, and
the only two above .350 came on 100–156 plate appearances with materially more power. **Ben Revere
2015 — .298/.077/.311 over 388 PA — is the honest full-season ceiling case for this profile.**

The gap between "he is figuring it out" and "he is a good major-league hitter" is entirely launch
angle, and it is the same gap the reports flagged three years ago. This season has not closed it.

### Player — *the one-liner*
You are striking out far less and putting more balls in play, and your speed is turning those into
hits. The next step is the same one it has always been: get the ball off the ground.

## Common queries

```python
import pandas as pd, dp_uc34_kernel as k
z   = pd.read_csv('dp_uc34_monthly_master.csv')
pool = pd.read_csv('dp_uc34_population_pool.csv')

z[~z.below_pa_floor][['month','woba','babip','krate','gb_rate','mean_la']]  # interpretable months
z[z.month_is_partial]                                                      # what not to compare
pd.read_csv('dp_uc34_breakpoint_scan.csv')                                 # before quoting any split

# any Phillies hitter-season, same benchmark
pool.nsmallest(15, 'mean_la')[['player_name','game_year','plate_apps','mean_la','gb_rate','woba']]

# re-run the whole context layer for a different position
pos, pps = k.load_frames()
cntxt, seasons = k.cf_context_pool(pos, pps, min_cf_games=80)

# test any platoon-shielding claim, on any window
k.platoon_counterfactual(df, k.woba_weights(), 'my_window', 'before', 'after')
```

## Interpretation rules

| Metric | Read it as | Do **not** |
|---|---|---|
| `fpsr`, `in_zone_rate` | what pitchers did **to** him | read as hitter behaviour (RC-4) |
| `chase_rate` | swing decision on out-of-zone pitches | compare across differing OOZ counts without the denominator |
| `xwobacon_bip` | expected value **per ball in play** | compare to `woba` — different denominators (O-4) |
| `mean_la` | central tendency on **tracked** BIP | read where tracked BIP < 50 — it is NULL by design |
| `gb_rate` | share of **all** BIP | assume it moves with launch angle — here it did not |
| `hard_hit_rate` | governed definition, **all-BIP denominator** | forget that untracked BIP count as not-hard-hit (O-8) |
| BABIP | outcome on balls in play | read as a skill without the exit-velocity column beside it |
| `mix_effect` (PL-1) | how much a line is flattered by its platoon mix | read as a causal estimate of anything else |
| any March or August 2026 row | nothing | interpret or rank — both are below the 50-PA floor |
| the 15 June split | a descriptive contrast | treat as inferential — it was outcome-selected |

## Dashboard

`dp_uc34_crawford_ytd_dashboard.html` — **fully self-contained; the charting library is inlined, so it
renders with no network and can be emailed as a single attachment.** Eight KPI tiles with before/after
deltas · seven tabs (overview, centre-field context, profile vs population, what changed, platoon,
pitch types, governance) · the CF ghost-line chart with a live BA/OBP/wOBA toggle · breakpoint
sensitivity · archetype scatter · a governance tab carrying the interpretation rules, the floor table
and all six kernel defects. Below-floor rows are amber-shaded everywhere they appear, and both the
mechanism warning and the reliability warning render above the fold on every tab.
