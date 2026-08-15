# 07 · Platform & Marketing
**cost-watchdog · data-observability · analytics-enabler**

## Cost
Trivial. 58 MB parquet, single-player slice, full build < 30 s single-threaded. No warehouse spend,
no scheduled compute. The context pool (270,954 rows → 217 seasons) is the heaviest step and runs once.

## Observability — re-run triggers
| Signal | Threshold | Action |
|---|---|---|
| August completes | after 8/31 | re-run; August ceases to be partial |
| Chase rate | returns above 30% over a 50-PA window | approach change did not hold — re-read |
| FPSR | returns above 55% | pitchers resumed attacking; the confound recedes and the hitter signal gets cleaner |
| New `description` value | any | **halt** — the governed SWINGS mapping is no longer exhaustive |
| Ratification of AP-2/3/6/9/10 | on DPO sign-off | promote to notebook; re-baseline verification |

**Staleness rule:** any figure quoted after **2026-08-13** must state the as-of date.

## Publication note — the video
Title *"Bryson Stott drawing 14 walks between strikeouts"* is **verified exactly**: 14 walks, zero
strikeouts, 11 games, Jul 29 → Aug 9, 46 PA. Longest such run of his career by 5.

Two corrections for the supporting narrative:
1. The stated **3:2 OBP:K is understated.** Stott's career figure is **1.85:1**, 83rd percentile
   against 217 Phillies hitter-seasons since 2015. He has cleared 3:2 every season since 2022.
2. *"Foul ball rate trending above average"* was **not shipped.** The proposed definition keyed on
   `launch_speed` being populated on non-BIP rows — which is open item **O3**, a data quirk the repo
   documents as a trap to filter out, not a definition. A `description`-based foul rate over swings
   is the correct build and is a candidate for the next iteration.

**The most publishable finding is the one not in the title.** First-pitch strike rate against Stott
fell from 67% to 41%. The story is not only that he stopped chasing — it is that the league stopped
challenging him, which is the clearest form of respect a lineup can be paid.

## Reuse
- **AP-6 rolling wOBA by cumulative PA** — general to any hitter; the ghost-line + cumulative-PA
  index is the strongest available "did he change" visual and should be the pos-side default.
- **AP-9 / AP-10** — general; ship together, since a rate ratio and a run length answer different questions.
- **The hitter/pitcher panel split (RC-4)** — should be a standing requirement for every approach study.
- **Pricing both window framings** — extends the `uc-pos-008` precedent from premises to *sample selection*.
