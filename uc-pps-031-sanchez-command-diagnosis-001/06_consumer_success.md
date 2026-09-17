# 06 · Consumer Success — `uc-pps-031`

Agents: `consumer-onboarding-agent` · `analytics-enabler`

## 1 · Personas and what each should take away

| Persona | Read | The one thing to act on |
|---|---|---|
| **Pitching coach** | Report bottom line, §5–§6 | Get the changeup to righties back **within one baseball** of the zone. Don't aim for more strikes over the heart. Track SZ-2 on CH vs RHB (2H .621) |
| **Sánchez** | Fig 2 and Fig 5 (visuals only) | His misses moved from low to glove side and up, where hitters don't swing |
| **Catcher** | §5 count table | When ahead, righties no longer chase the miss (.401 → .307). Set the target inside the shadow |
| **Pitching analyst** | §3, `03` §2 | Put every 2025→2026 zone comparison through ZC-1 first. Native peer-netting misleads for low-zone arms |
| **Manager** | Bottom line 1–2, "Manager" action | A location problem with one pitch against one side; expected results moved less than actual |

## 2 · Reading order

1. Report → *Bottom line* (1 page).
2. Fig 1 (premise scorecard), then §3 before trusting any 2025→2026 zone number.
3. Fig 3 (the proof), then §6 (where it leaks).
4. The dashboard, to check any split yourself.

## 3 · Dashboard walkthrough

- Default view: **2026 2H vs 2026 1H**, both sides, all pitches. Every tile shows the delta.
- Pick **Batter: RHB** and **Pitch: Changeup**, then **Missed the shadow**. You'll see the arm-side cloud that drives the finding (Shadow Miss .621, Chase Beyond .302).
- Switch **Compare** to **2025 2H** to see how far he is from his best half. Remember that comparison crosses the rail change.
- **Chase beyond the shadow, by window** follows your filters. The black ticks are the league for all pitches and both sides.
- **Trend** is fixed to receipt values (monthly, 2026) and doesn't follow the filters.

## 4 · How to read the new KPIs

- **Edge Rate** (governed): how often he's within a ball of the line, on either side. *High = living on the corners.*
- **Shadow Miss Rate** (SZ-2): how often he misses the zone by more than a ball. *High = non-competitive misses.*
- **Chase beyond the shadow** (SZ-3): how often hitters still swing at those. *High = hitters bailing him out.*
- The three together tell the story: **Edge flat + Shadow Miss up + Chase Beyond down = wild misses that no longer
  get swung at.** Edge flat with Shadow Miss flat and Chase Beyond down would instead mean hitters have adjusted to
  a pitcher who hasn't changed.

## 5 · Reuse patterns

- **Any command question:** `shadow_profile` + `edge_rate` + `count_leverage` at the same grain. SZ-1…4 and Edge Rate share one distance function, so they can't disagree.
- **Any 2025→2026 zone question:** `abs_rails` → `common_rail_rescore` → metric, then net against the league run through the same re-score.
- **Any "is it him or the environment" question:** PN-1 on the **common-rail** basis.
- **A client's notebook cell:** reproduce it with the notebook's own code first (family G pattern) before extending it.

## 6 · FAQ

- *Why does the report say chase went up when you also say hitters stopped chasing?* Both are true, at different grains. The season is up because the first half was a spike (.386). Since the break it's down (.320).
- *Isn't the zone drop just ABS?* About a third of it is. On common rails, half is his own (`rail_decomposition`).
- *Why not use the 0.33 ft Attack Zone shadow?* It conflicts with the ratified one-ball constant (E-3).
- *Where's the 20-80 grade?* Not enough same-rail pitcher-seasons to grade against (`03` §1).
