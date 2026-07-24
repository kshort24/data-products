# Layer 4 — Certification Closure · Post-Game Backtest
### UC-PPS-021 · projected plan (pre-game, 7/16 cache) vs actual result (2026-07-22)

This is the closure step named in `dp_uc25_nola_vs_dodgers_use_case_spec.md` §8. The 2026-07-22 start synced into the cache on 2026-07-24 (post-build), so the plan the advance report projected can now be scored against what happened. **The pre-game product is unchanged** — this artifact is additive. Receipts: `out/dp_uc25_backtest_*.csv` (build script `dp_uc25_backtest.py`).

## The line

| | IP* | PA | H | HR | uBB | IBB | K | wOBA | xwOBAcon | 1P-strike |
|---|---|---|---|---|---|---|---|---|---|---|
| **7/22 vs LAD** | 5.1 | 23 | 7 | 2 | **0** | 1 | 4 | .420 | .478 | 65% |

A rough line (5.1 IP, .420 wOBA) — but read *how* it happened, because it is exactly the split the report drew.

## Plan vs actual

| Pre-game call (indicator) | 7/22 actual | Verdict |
|---|---|---|
| **Don't walk the lefties** (10.7% BB leak; 58.8% 1P-strike) | **0 unintentional walks**; 1P-strike up to **65%**; the only pass was an *intentional* walk to Ohtani | **HELD ✓** |
| **Keep the fastball down — never a pitch they can lift** (air 59.7% / HR 5.1%) | **2 HR** — Muncy on a 0-0 **changeup** (85, middle), Rushing on a 3-2 **4-seam** (94, up); game xwOBAcon **.478** | **BROKE ✗ — the flagged risk** |
| **Knuckle curve is the weapon** (42.5% whiff vs LHB) | KC **34% usage / 36% whiff** — the finish pitch, as designed | **HELD ✓** |
| **Betts is the danger — pitch him backward** | Betts **0-for-3** (flyout, groundout, K looking) | **HELD ✓** |
| **Ohtani danger on contact — don't let him beat you** | Ohtani **0-for-2 + intentional walk** | **HELD ✓** |
| **Freeman: loud contact even when the line is quiet** (.397 xwOBAcon) | Freeman **2-for-4, two doubles** | **CONFIRMED (predicted) ✓** |
| **The air-ball engine is the real run-prevention risk** (.384 xwOBAcon) | Both HR + Freeman's doubles in the air; game xwOBAcon .478 | **CONFIRMED ✓** |

## The seven, head-to-head (7/22)

| Hitter | PA | Line | vs the pre-game read |
|---|---|---|---|
| Mookie Betts | 3 | flyout, groundout, K looking | **plan held** — the danger bat, handled |
| Shohei Ohtani | 2 (+IBB) | lineout, groundout | **plan held** — handled, then walked by design |
| Freddie Freeman | 4 | **2 doubles** | **predicted** — the loud-contact book |
| Max Muncy | 3 | K, flyout, **HR** | mixed — owned twice, then a middle changeup left the yard |
| Kyle Tucker | 2 | two flyouts | plan held — profile read (no book) worked |
| Andy Pages | 3 | K, lineout, GIDP | plan held |
| Tommy Edman | 2 | flyout, single | contained |
| *Dalton Rushing (unnamed)* | 2 | **HR**, double | the bottom-of-order lefty catcher did the most damage — outside the 7-hitter scope (O2) |

## Certification closure verdict

**The report's diagnosis was validated.** Nola executed the *process* half of the plan — zero unintentional walks (the self-inflicted leak the report centered on), first-pitch strikes up to 65%, and the two danger bats (Betts, Ohtani) neutralized. He was beaten by the **contact-quality / air-ball engine the report named as the real risk**: two home runs in the air (including the 3-2 fastball the report explicitly warned against) and Freeman's predicted loud contact. Net predictive value: **high** — the plan correctly identified both what he could control (walks — fixed) and what would beat him (air-ball damage — realized).

**Actionable follow-through (feeds the next Nola UC):**
1. The walk fix is real and repeatable — 0 uBB on 65% first-pitch strikes. Bank it.
2. The two-strike / ahead-in-count **fastball location** is the open wound — the Rushing HR was a 3-2 four-seam up; the Muncy HR a 0-0 changeup middle. The "keep it down / never a liftable fastball" rule needs enforcement, not just intent.
3. **Scope lesson (O2):** the unnamed #8/9 lefties (Rushing, Teoscar) did real damage. A future advance should cover the full card, not a 7-hitter subset.

*Closure status: use case CLOSED. Recommend the walk-location follow-up as the seed for the next Nola pps UC.*
