# Game 3: Painter vs Holmes — the 20-80 scouting card

**UC #44 · `uc-pps-030` · `dp_uc44` · v1.0.0 · delivered 2026-09-13 · READY-CONDITIONAL · independently verified (247/247)**
Phillies Pitching (`pps`) value stream · Human DPO: Kellen Short

## Start here

| If you want | Open |
|---|---|
| the card | `out/dp_uc44_fig1_notecard.png` |
| the argument | `dp_uc44_painter_vs_braves_report.pdf` |
| to interrogate it by side and window | `dp_uc44_painter_scouting_card.html` |
| the one sentence for the battery | report §6, "The single attack rule" |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the six conditions on certification | `05_quality_certification.md` §5 |
| the KPI specs, before reusing them | `03_governance.md` §2 |

## The finding, in one paragraph

Kellen's index card is right three times out of three — 21.8% four-seam whiff, 16.97" of ride, 39.5% splitter
whiff to left-handed hitters, breaking-ball in-zone rate that grades **55** — but the three numbers are not
about the same pitcher. **Painter has thrown zero splitters in eight starts since the option**; the pitch that
replaced it is a changeup 3.1 mph harder, 3.1" flatter and 3.0" more run, which allows **.160 xwOBA** and is now
the best pitch he throws. The lefty whiff gap between the two (.395 → .301) does not clear significance
(z = 1.20, p = 0.23). That one substitution carries the whole advance: the platoon has flipped (**29.7% K vs
RHH, 18.1% vs LHH**), 47 plate appearances of April head-to-head history against Atlanta are unusable
(**arsenal turnover 0.33**), and the actual leak is the **sweeper to left-handed hitters** — 64.5% in the zone,
20.0% whiff, .523 xwOBA on 9 tracked PA — against a lineup that runs **six left-handed bats out of nine**.
Separately, the four-seam went up: elevation rate .307 → **.349** against a population mean of .200 (a **70**),
doubling its whiff rate from a 35 to a 50 and costing a **command grade of 25** and ninety pitches for
twenty-three batters. Arsenal grade **50**, up from **45** on the arm that got optioned.

## Three things that need your decision

1. **Does the card get re-dated or re-issued?** "Plus FS — 39.5% whiff to LHB" is true and stale. It is the best
   number this shop has on that pitch if it ever comes back.
2. **Seven new governed objects, all provisional.** SG-1…SG-5 (the 20-80 family), AR-1 (arsenal turnover), PM-1
   (pitch-map centroid). Ratify on second use, or hold for review?
3. **`arm_angle` is 54% null** and the `uc-pps-023` arm-spread finding cannot be refreshed. Cache problem worth
   fixing upstream, or a field this repo cannot build on?

## What the 20-80 scale actually is

A z-score in costume: `grade = clip(50 + 10 × z, 20, 80)`, rounded to the nearest 5. Adopting it committed this
shop to three things it would otherwise have skipped — **a declared population**, **a minimum-sample gate**, and
**a test of the normality the scale assumes**.

The population is every right-handed pitcher who threw in a Phillies regular-season game 2015–2026, counted
once per season, with ≥100 pitches of that type. It is a **Phillies-schedule population, not a league
population**; a 60 here is not a Savant 60, and that sentence travels with every grade.

The normality test **failed on three of twelve populations** (sweeper whiff p = .015; changeup and sinker
in-zone p = .006 / < .001). Every grade therefore ships with a rank-derived twin, and **eleven of twelve came
back identical**; the twelfth differs by 5 points against a flag threshold of 10. Nothing was suppressed and
nothing was hidden.

Shape — velocity, ride, run — is graded and reported but **deliberately not scored into** the pitch grade. A
pitch is worth what it misses and where it lands. That exclusion is what makes it possible to write the
sentence this report needed: Painter's four-seam grades 60 on velocity and 70 on run, and 40 as a pitch.

## Package contents

```
00_dpo_orchestration_record.md      the spine: ask, gates, finding, internal arguments, escalations
01_strategy_intake.md               prior art, 6 gaps, 5 premises stress-tested, F1-F4 fitness, opponent resolution
02_engineering_design.md            data model, fan-out design-out, 8 EDA findings, metadata map, DQ rules, dashboard spec
03_governance.md                    Rule-1 search, 7 new objects specified, lineage, defect exposure, privacy, versioning
04_engineering_build.md             build manifest, environment disclosure, assertions, reuse queries, receipts
05_quality_certification.md         DQ scorecard (19), defect register, verification (247), certification + 6 conditions
06_consumer_success.md              personas, reading order, dashboard walkthrough, re-run recipe, reuse patterns
07_platform_marketing.md            6 tripwires, cost audit, bid vs actual, 5 calibration findings, post-game backtest
BID_2026-09-13_...md                the competitive bid — filed, awarded, reconciled in 07
dp_uc44_kernel.py                   governed kernel: A verbatim / B access / C new
dp_uc44_painter_vs_braves.py        the build
dp_uc44_build_figs.py               5 figures (one of them asserts its own title)
dp_uc44_build_pdf.py                markdown -> weasyprint
dp_uc44_build_dashboard.py + tpl/   self-contained interactive card
dp_uc44_verification.py             7 families, 247 checks
dp_uc44_painter_vs_braves_report.md/.pdf
dp_uc44_painter_scouting_card.html
out/                                31 receipts (24 CSV, 5 PNG, payload, verification log)
uc_ledger_AI_PATCH_...md            PENDING PASTE into uc_ledger_AI.md
```

## Reproducing this

```bash
export MLB_DATA_ROOT="/path/to/Python Scripts/MLB"
python dp_uc44_painter_vs_braves.py     # 24 receipts + payload
python dp_uc44_build_figs.py            # 5 figures
python dp_uc44_build_pdf.py             # 10-page branded PDF
python dp_uc44_build_dashboard.py       # interactive card
python dp_uc44_verification.py          # 247/247 expected
```

The build refuses to run if the anchor game is not 2026-09-12 — by design. A refreshed cache is a **new game**,
not a correction to this one.

## Governed objects: inherited vs. introduced

**Inherited verbatim** — `get_stats`, `measure_calcs`, `mcgs`, `nresults`, `whiff_rate`, `chase_rate`,
`pitch_mix`, `lhb_pitch_mix`, `rhb_pitch_mix`, `fpsr`, `putaway_rate`, `bb_type_by_level`, `hard_hit_rate`,
`SWINGS`, `WHIFFS` (`Baseball Functions.ipynb`, via `dp_uc43_kernel`); `two_prop_z` (`dp_uc42`);
`_apply_woba_weights` (`mlb_data.py`); `PITCH_COLORS` / `STRIKE_ZONE` (house skill).

**Introduced here, all provisional and unratified** — **SG-1** `scouting_grade_20_80`, **SG-2**
`benchmark_population`, **SG-3** `grade_divergence_flag`, **SG-4** `pitch_grade`, **SG-5** `grade_label`,
**AR-1** `arsenal_turnover_index` (with a mandatory league tag-drift control), **PM-1** `pitch_map_centroid`.

SG-1 and SG-2 are pitcher-agnostic and pitch-agnostic — they will grade any arm against any declared population
with no code change. Ratification requires an independent second use; the cheapest one is the post-game
backtest in `07` §6.

## What this build found wrong with its own draft

Verification family E reconciles **every number the report asserts** against a fresh reload of the parquet.
Four assertions failed on the first run; three were real errors in the prose, not in the data:

1. A Shapiro-Wilk p-value quoted from the wrong population floor (.833 → **.015, and it fails**).
2. "Five of nine" Atlanta bats left-handed — it is **six**.
3. "Divergences of 0.0 across the board" — **eleven of twelve**.

Every receipt was correct in all three cases. Receipt-to-receipt checking would have caught none of them.
