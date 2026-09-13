# UC LEDGER PATCH — `uc-pps-030` (UC #44)

**PENDING PASTE** into `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\uc_ledger_AI.md`.
The repo-side ledger lags delivered UCs (known drift — verify with `ls dp_uc*` before claiming a number).

---

## Row to append

| UC | ID | Subject | Status | Key artifacts |
|---|---|---|---|---|
| 44 | `uc-pps-030` | Painter vs Braves, Game 3 (2026-09-13) — the 20-80 scouting card | Delivered · READY-CONDITIONAL · verified 247/247 | `dp_uc44_*` + `uc-pps-030-Andrew Painter ATL 20260913.md`; trail at `Agents for Data Products/data-products/uc-pps-030-painter-vs-braves-001/` |

**Next available: UC #45.**

## Pattern inheritance map — additions

- Pitcher-side deep dive: UC3 → UC8 → UC11 → **UC29 (`uc-pps-023`, Painter return)** → **UC44 (this)**
- Self-scout variant (opponent descoped or bounded): UC29 → **UC44**
- **Scouting-grade family (NEW):** UC44 is the origin of SG-1…SG-5. Pitcher- and pitch-agnostic; reusable by any uc-pps or uc-pos build
- **Arsenal-composition change (NEW):** UC44 is the origin of AR-1 and of the mandatory league tag-drift control

## New governed objects (all PROVISIONAL — ratification requires an independent second use)

| Object | What it does |
|---|---|
| **SG-1** `scouting_grade_20_80` | `clip(50 + 10z, 20, 80)` rounded to 5, half-up. Returns z, percentile, and a rank-derived twin grade |
| **SG-2** `benchmark_population` | RHP/LHP pitcher-seasons in the Phillies game log 2015–2026, ≥100 of the graded pitch. Floor drops to 50 and stamps THIN below 25 pitcher-seasons |
| **SG-3** `grade_divergence_flag` | Fires at a 10-point disagreement between the z-grade and the rank-grade — the normality assumption's watchdog |
| **SG-4** `pitch_grade` | mean(stuff, command). Shape deliberately excluded |
| **SG-5** `grade_label` | Controlled scouting vocabulary |
| **AR-1** `arsenal_turnover_index` | Share of an arsenal not shared across two windows. **Requires the league tag-drift control before being called a pitcher decision** |
| **PM-1** `pitch_map_centroid` | Usage-weighted location centroid + dispersion, by stand × pitch |

## Findings worth carrying to the next UC

1. **`arm_angle` is 54% null on the 2026 cache.** The `uc-pps-023` arm-spread finding is not refreshable. Any UC planning release-point work must check this field first.
2. **`estimated_woba_using_speedangle` is PA-grain xwOBA, not xwOBAcon** — populated on every PA-ending row (K = 0.000, BB = 0.698). Confirmed by assertion (DQ-8). This settles the `uc-pps-021` ambiguity: pitch-level `.mean()` over all rows *is* a valid xwOBA; `.mean()` restricted to `type=='X'` is xwOBAcon. Report both, label both, print both n's.
3. **Sweeper (`ST`) pitcher-seasons at a 100-pitch floor: only 14** in twelve years of Phillies games. Any sweeper benchmark needs the lowered floor and a THIN stamp until the tag matures.
4. **Painter's splitter is gone**, replaced by a changeup since 2026-07-31. Any prior Painter analysis quoting `FS` is stale. Tripwire T-2 in `07`.
5. **Three benchmark populations fail Shapiro-Wilk** (ST whiff .015; CH in-zone .006; SI in-zone < .001). Grades still agreed with their rank-derived twins, but future SG-1 users must run the test rather than assume it.

## Repo-side artefacts to file

- `uc-pps-030-Andrew Painter ATL 20260913.md` → MLB repo root (the registry contract)
- `dp_uc44_*.py` / `.md` / `.pdf` / `.html` → MLB repo root, alongside `dp_uc28_*`
- `out/dp_uc44_*` → MLB repo `out/`

## Calibration note for the ledger's own maintenance

This shop has now over-estimated wall clock by ~3× on two consecutive competitive bids while estimating tokens
to within 10%. Future bids should price in tokens and derive minutes at ≈0.10 min per 1k tokens. See
`07_platform_marketing.md` §3.
