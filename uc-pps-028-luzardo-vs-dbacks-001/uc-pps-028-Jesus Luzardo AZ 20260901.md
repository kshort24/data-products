# Use Case Contract — uc-pps-028

```yaml
uc_id: uc-pps-028
ledger_uc: 39
build_artifact: dp_uc39
package: data-products/uc-pps-028-luzardo-vs-dbacks-001
value_stream: Phillies Pitching (pps)
variant: pre-scout + season consistency audit (premise adjudication)
subject:
  name: Jesús Luzardo
  mlbam_id: 666200
  throws: L
opponent:
  team: AZ (Arizona Diamondbacks)
  game_date: 2026-09-01
  lineup_confirmed: false          # UNVERIFIED — carried as a labelled gap
requested_by: Kellen Short (human DPO)
requested_on: 2026-09-01
extends: uc-pps-017                # All-Star-break first-half assessment (UC #19)
inherits_methods:
  - TR-2 breakpoint sensitivity scan   # uc-pps-027
  - multi-tier evidence separation     # uc-pps-011
  - des-parse batter id resolution     # uc-pps-011 (+ D-2 fix, this UC)
status: DELIVERED — CERTIFY-READY
delivered_on: 2026-09-01
verification: 195/195 PASS
dq: 28 rules, 0 FAIL, 2 WARN (O-5, O-8 carried)
```

## The ask, verbatim

> "I want to do a pre-scout on Jesús Luzardo before his start against the Diamondbacks tonight.
> Extend the analysis that was done on him at the All-Star break. He has been maybe the Phillies'
> most consistent pitcher in 2026? Since the end of April he has been very good. I have not done
> much inspection on my own, so I am leaning on the data-product-owner to guide the narrative here."

## Scope

**In:** 2026 season to date (27 starts through 2026-08-26) with 2025 as comparison; adversarial test
of the DPO's consistency and quality claims against the Phillies rotation with a scanned window
boundary; closure of every second-half watch item `uc-pps-017` left open; arsenal, TTO, handedness,
battery and workload splits; Arizona as a matchup lens.

**Out:** a fresh Arizona hitter pull; league-wide benchmarking; any predictive model; official
ERA / W–L (not computable from a pitch log).

## Acceptance criteria

| # | Criterion | Met |
|---|---|---|
| A-1 | The premise is adjudicated, not assumed | ✅ split verdict |
| A-2 | Every `uc-pps-017` watch item closed with a number | ✅ 16 tripwires |
| A-3 | The build reproduces its parent's published figures | ✅ 17/17 |
| A-4 | Opponent sample honesty; no confirmed lineup implied | ✅ |
| A-5 | Every published number traced to a receipt computed this session | ✅ 195/195 |
| A-6 | New KPIs specified before use | ✅ CN-1…CN-6, AR-1 |
| A-7 | An actionable recommendation exists for tonight | ✅ |

## Verdict

**Level claim — SUPPORTED, boundary-robust.** Best xwOBA on the staff (.257) at all eight tested
window boundaries and on the full uncut season.

**Consistency claim — NOT SUPPORTED as stated.** On floor axes (CN-2, CN-3, CN-6, RA9) the title is
Cristopher Sánchez's. Luzardo's CN-1 rank of 1 exists only in a narrow band around 2026-05-01; on the
full season he is 3rd. **He does lead unambiguously on CN-5 (workload predictability) at every
boundary** — 21 straight turns, none missed, a 90–110 pitch band.

## New governed objects (provisional — E-1)

`CN-1` start-to-start variation · `CN-2` floor rate · `CN-3` blow-up rate · `CN-4` rolling-3-start
range · `CN-5` workload predictability · `CN-6` length dependability · `AR-1` opponent recency tier
· guardrails **`G8`** (a superlative needs a named metric and an enumerated cohort) and **`G9`**
(never publish a composite index for a contested claim).

## Defects

**Fixed this run:** `D-1` grain-relative completeness · `D-2` replay-review prose in `des` parsing ·
`D-3` era-mixing in team-keyed H2H. All three are repo-wide patterns.
**Carried open:** `O-5` `truncated_pa` counted as PA · `O-8` untracked BIP counted as not-hard-hit.
