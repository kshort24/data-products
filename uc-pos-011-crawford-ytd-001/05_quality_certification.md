# 05 · Quality & Certification
**data-quality-engineer · certification-agent**

## Verification — `dp_uc34_verification.py`

**127 PASS / 0 FAIL.** Independent path: parquet files read in **reverse year order**, the subject
filtered **before** the batting-role tag, every mask declared inline from raw columns, wOBA constants
re-read from the CSV. **No import of `dp_uc34_kernel`.**

| § | Coverage | Result |
|---|---|---|
| 1 | population, as-of date, single player, single stand | 5/5 |
| 2 | season line — 6 counts + 8 rates | 14/14 |
| 3 | monthly panel — PA and wOBA per month, sum identity, floor set | 15/15 |
| 4 | the mid-June window claim — 16 rate checks + 6 directional assertions | 22/22 |
| 5 | discipline — SWINGS/WHIFFS independently declared, 3 rates × 2 windows | 8/8 |
| 6 | batted ball — GB rate, mean LA, hard-hit × 2 windows, D6 divergence, null-sensor liveness | 11/11 |
| 7 | platoon — Hill debut derived, LHP shares, August, 3 counterfactual bounds | 9/9 |
| 8 | CF context — 110 CF games, pool size, matched-PA completeness, rank | 5/5 |
| 9 | population benchmark — 12 percentiles recomputed + 5 profile assertions | 20/20 |
| 10 | pitch mix — floors, PA and pitch sum identities, offspeed direction | 6/6 |
| 11 | breakpoint sensitivity — 9 wOBA recomputations + 2 sign assertions | 11/11 |

**Assertions the verification makes about the *conclusions*, not just the arithmetic** — these are
the ones that would catch a narrative drifting from its data:

- BA, OBP and wOBA all rose across the break — **and BB rate and ISO both FELL**, and HR after the break is exactly **0**
- chase rate moved less than 1 point — the "he stopped chasing" reading is blocked at the test layer
- mean launch angle moved less than 1° — the "he changed his swing" reading is blocked
- GB rate remains above 50% after the break
- the platoon mix effect is under 0.005 on all three metrics
- a mid-May breakpoint **reverses the sign**, and 15 June **is not the strongest available split**

## CDE-level DQ

| CDE | Dimension | Result |
|---|---|---|
| `player_name` / `batter` | validity | ✅ single value, MLBAM 702222 |
| `stand` | consistency | ✅ single value `L`, all 1,323 rows |
| `game_month` | consistency | ✅ equals `game_date` month, all rows |
| `plate_appearance_key` | uniqueness | ✅ one terminal row per `game_pk` + `at_bat_number` |
| `description` | validity | ✅ **zero unmapped values** against governed SWINGS/WHIFFS |
| `pitch_type` | completeness | ✅ 11 types, all map to `PITCH_GROUP`; `other` bucket empty |
| `zone` | completeness | ✅ non-null on every chase-denominator row |
| `bb_type` | completeness | ✅ **0% NULL** on BIP |
| `launch_speed` / `launch_angle` | completeness | ⚠ **0.74% NULL on 2026 BIP** — real sensor gaps; drives **O-8** |
| `estimated_woba_using_speedangle` | completeness | ⚠ 1.8% NULL on BIP; NULL not imputed |
| `fielder_8` | validity | ✅ Crawford = 110 CF games in 2026, independently reproduced |

## Reliability floors

| Bucket | Volume | Floor | Status |
|---|---|---|---|
| March 2026 | 13 PA | 50 PA | ❌ **below floor — flagged, retained, not interpreted** |
| April 2026 | 86 PA | 50 PA | ✅ |
| May 2026 | 83 PA | 50 PA | ✅ |
| June 2026 | 79 PA | 50 PA | ✅ |
| July 2026 | 59 PA | 50 PA | ✅ |
| **August 2026** | **42 PA** | 50 PA | ❌ **below floor AND partial — and it is the requester's strongest month** |
| Offspeed, post-break | 17 PA | 50 PA | ❌ below floor — the cleanest approach signal is also the thinnest |
| LHP, post-Hill | 23 PA | 50 PA | ❌ below floor |
| Launch angle / bb-type, per group | varies | 50 tracked BIP | NULL where unmet (March) |
| Pitch-type rows | ≥40 pitches | 40 | ✅ 8 of 11 types qualify |

> **The floor bites hardest exactly where the story is strongest.** August, the post-break offspeed
> cell and the post-Hill LHP split are the three most quotable cells in this product and all three are
> below floor. They are shipped — suppressing them would be its own distortion — but they carry the
> flag on every surface, and no ranking may include them.

## Six defects in the governed KPI kernel

Reported, **not patched in place**. `_fix` variants used for this build; originals untouched.
D1–D5 inherited from `uc-pos-010`; **D5's diagnosis is corrected and D6 is new.**

| ID | Function | Defect | Impact here |
|---|---|---|---|
| **D1** | `whiff_rate` | inner-merges swings→whiffs; a group with swings but **zero whiffs vanishes** | none this run — latent |
| **D2** | `hard_hit_rate` | same shape; a group with BIP but zero hard hits vanishes | none this run — latent |
| **D3** | `fpsr` | groups by `level+['type']` then returns only `type=='B'`; a group with a perfect 1.000 FPSR vanishes | none this run |
| **D4** | `nresults` | rounds to 3dp on return; any ratio of two rates inherits it | **avoided** — every rate rebuilt from counts. Material for ISO and BABIP, which are differences and ratios of rates |
| **D5** | `pull_air_rate` | **the function cannot execute against the governed data plane.** It reads `bip.loc_x` / `bip.loc_y`; the parquet schema has **`hc_x` / `hc_y`** and no `loc_*` columns at all. Confirmed against `ParquetFile(...).schema.names` | not used — **diagnosis corrected this build, opened as O-7** |
| **D6** | `hard_hit_rate` | **NEW.** The denominator is **all** balls in play, including those the sensor did not track — so an untracked BIP is silently scored *"not hard hit"* rather than excluded. Directly contradicts the uc-pos-009 sensor-boundary standard, which the same repo enforces for launch angle | **0.6 pt on the post-break window** — `43/120 = .3583` published vs `43/118 = .3644` on tracked BIP. Small here because tracking is 99.3% complete; **it scales linearly with any tracking gap** |

> **D6 is the interesting one.** D1–D3 are merge bugs. D6 is a *definitional* inconsistency: the repo
> treats an untracked ball in play as unknown for launch angle and as a negative observation for
> hard-hit rate, in the same function library, on the same rows. Both conventions are defensible in
> isolation; holding both at once is not. **The published number here follows the governed
> definition** — fidelity to the data plane outranks the build's own preference — and the divergence
> is asserted in verification §6 so it cannot drift unnoticed.

## Caveats that must travel with the numbers

1. **The improvement is BABIP-led.** BABIP +79 pts against xwOBAcon +49 pts, on ground balls whose mean exit velocity **fell** 4.4 mph. The gap is the part most likely to regress.
2. **The breakpoint was outcome-selected.** A mid-May boundary reverses the sign. Everything downstream of 15 June is descriptive, not inferential.
3. **August is 42 PA, below floor, partial, and nearly a pure RHP sample** (1 of 42 vs LHP). It is the strongest month and the least trustworthy.
4. **Regression to the mean is the null hypothesis.** April and May were poor; some improvement was expected with no change in skill.
5. **Opponent quality is uncontrolled.** No adjustment for who he faced beyond handedness.
6. **No causal claim is supported anywhere in this product** — including the platoon finding, which establishes only that the mix did *not* change over the window the hypothesis named.
7. **The archetype cohort is a Phillies-only pool**, and 6 of its 9 members are partial seasons. It bounds expectations; it does not forecast.

## Certification

**READY TO PUBLISH — internal.** All artifacts present, every headline independently reproduced on a
separate code path, every open item disclosed, every below-floor cell flagged on every surface.
