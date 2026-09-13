# Game 2 Bullpen Script — Mayza opens, Holman debuts

**UC #43 · `uc-pps-029` · `dp_uc43` · v1.0.0 · delivered 2026-09-13 · READY-CONDITIONAL · independently verified (179/179)**
Phillies Pitching Staff (`pps`) value stream · Human DPO: Kellen Short

## Start here

| If you want | Open |
|---|---|
| the argument | `dp_uc43_bullpen_script_report.pdf` |
| to rebuild the script yourself | `dp_uc43_bullpen_control_room.html` |
| the ledger a coach would use | `out/dp_uc43_availability_D1.csv` |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the five conditions on certification | `05_quality_certification.md` §5 |
| what this build found wrong with the governed kernel | `03_governance.md` §4 |

## The finding, in one paragraph

Nine innings from seven arms, priced at each arm's own 2026 average outing, delivers **29.7 batters faced**
against a **37**-batter regulation median (n=**106** regulation games) — **7.3** batters, about **2.4 innings**, short. Priced at every arm's season high it
delivers **38.1** and just covers; the recommended reallocation prices at **37.4** on the same basis. The script is therefore not simply short; it is **ceiling-dependent**, and
the largest ceiling in it is **10 batters faced, set at Triple-A, by a pitcher making his major-league debut**.
Two of the client's stated premises did not survive: five relievers pitched in the anchor game, not four (the
unnamed one, Alvarado, is the most-worked arm in the pen and is scripted for the eighth), and Duran — the pick
to go multiple — has gone two innings in **1 of 56** relief outings this season. Mayza opening, by contrast,
is well supported: four opener starts this year, **three reached the second inning**, and a two-inning open
never reaches a hitter twice.

## Three things that need your confirmation

1. **Which game is this for?** D+1 (2026-09-12) or D+2 (2026-09-13)? Five of nine availability tiers move
   between them. If D+2, refresh the parquet cache first — the shipped D+2 ledger may be a game stale.
2. **Is MLBAM 641816 Mahle?** Inferred from four constraints; StatsAPI is unreachable from this session.
3. **Why hasn't Kerkering pitched since 09-04?** 59 appearances, then seven days. The log has no answer and
   this build asserts none — but the recommended revision leans on him.

## Two defects found in the governed kernel

- **D-8 (high, repo-wide):** `appearance_summary` returns `is_start = pd.NA` for every non-starter on a
  single-team frame (484 of 632 here), so `pitcher_season_workload(relievers_only=True)` returns an **empty
  DataFrame, silently**. Any prior bullpen analysis that got "no relievers" got a bug, not a result.
- **D-9 (medium, repo-wide):** `measure_calcs` renames a column named `batter` to `pitches`, so
  `nresults(['batter'], df)` raises `KeyError`.

Both reproduce as live assertions in the verification harness. Both remediated build-locally; the locked
notebooks are untouched. Fixes in `03_governance.md` §4.

## Package contents

```
00_dpo_orchestration_record.md      the spine: ask, gates, finding, escalations, publish call
01_strategy_intake.md               7 gaps, 7 premises stress-tested, source fitness, opponent resolution
02_engineering_design.md            data model, joins, 8 EDA findings, metadata map, DQ rules, dashboard spec
03_governance.md                    Rule-1 search, 4 new objects, lineage, 2 new defects, privacy, versioning
04_engineering_build.md             build manifest, environment, assertions, reuse queries, receipts
05_quality_certification.md         DQ scorecard (12), defect register, verification (179), certification
06_consumer_success.md              personas, reading order, dashboard walkthrough, re-run recipe
07_platform_marketing.md            7 tripwires, cost audit, bid vs actual, 4 calibration findings
BID_2026-09-13_...md                the competitive bid — filed, awarded, reconciled in 07
dp_uc43_kernel.py                   governed kernel: A verbatim / B verbatim / C new
dp_uc43_bullpen_script.py           the build
dp_uc43_build_figs.py               4 figures
dp_uc43_build_pdf.py                markdown -> weasyprint
dp_uc43_build_dashboard.py + tpl/   self-contained dashboard
dp_uc43_verification.py             6 families, 179 checks
dp_uc43_bullpen_script_report.md/.pdf
dp_uc43_bullpen_control_room.html
out/                                43 receipts (CSV, PNG, JSON)
uc_ledger_AI_PATCH_...md            PENDING PASTE into uc_ledger_AI.md
```

## Reproducing this

```bash
# with data/phillies/phils_2026.parquet and data/opponents/lhvp26.parquet reachable:
export MLB_DATA_ROOT="/path/to/MLB"
python dp_uc43_bullpen_script.py     # receipts + payload
python dp_uc43_build_figs.py         # 4 figures
python dp_uc43_build_pdf.py          # PDF
python dp_uc43_build_dashboard.py    # dashboard
python dp_uc43_verification.py       # 179/179 expected
```

The build refuses to run if the anchor game is not 2026-09-11 — by design. A refreshed cache is a **new
game**, not a correction to this one.

## Governed objects: inherited vs. introduced

**Inherited verbatim** — `get_stats`, `measure_calcs`, `mcgs`, `nresults`, `whiff_rate`, `chase_rate`,
`pitch_mix`, `lhb_pitch_mix`, `rhb_pitch_mix`, `fpsr`, `putaway_rate`, `bb_type_by_level`, `hard_hit_rate`
(`Baseball Functions.ipynb`); `appearance_summary`, `add_rest_days`, `add_rolling_workload`,
`pitcher_season_workload`, `build_bullpen_workload` (`Bullpen_Functions.ipynb`); `PITCH_COLORS` /
`STRIKE_ZONE` (house skill); `_apply_woba_weights` (`mlb_data.py`); `two_prop_z` (`dp_uc42`).

**Introduced here, all provisional and unratified** — **BS-1** `bullpen_availability_tier`, **BS-2**
`script_capacity` / `script_coverage_risk`, **BS-3** `multi_inning_propensity`, **OP-1** `opener_tto_delta`
(specified, executed, **could not discriminate** — and that null is itself the finding: a two-inning open
never reaches a hitter twice).

Ratification requires an independent second use. The cheapest one is the post-game backtest offered in `07`.
