# Trea Turner — Whole-Field Directional Tendency

`uc-pos-016-turner-whole-field-directional-001` · UC #42 · build artifact `dp_uc42` · **v1.0.0** ·
**READY-CONDITIONAL** · delivered 2026-09-10

## Start here

| If you want... | Open |
|---|---|
| The verdict, fast | `dp_uc42_turner_whole_field_report.pdf` — page 1 |
| To poke at it interactively | `dp_uc42_turner_whole_field_dashboard.html` — double-click, opens in any browser, no network needed |
| The full narrative | `dp_uc42_turner_whole_field_report.md` |
| What the org decided on your behalf, and what still needs your sign-off | `00_dpo_orchestration_record.md` §7 |
| The raw row-level data | `out/dp_uc42_turner_bip_extract.csv` |
| What this cost and how that compares to the bid | `BID_2026-09-10_uc-pos-016-turner-whole-field.md` + `07_platform_marketing.md` |

## The finding, in one paragraph

Your stated theory — that Turner is pulling outside-zone pitches too often in 2026 — **is not supported**:
his 2026 outside-zone pull rate (39.4%, n=71) is statistically indistinguishable from his 2023-2025 pooled
rate (36.7%, n=228). What the data does show is a different, real shift: **inside the zone**, his pull rate
has declined and his oppo rate has risen from 2023 to 2026, clearing the moderate-to-strong band on a pooled
two-proportion test. Full detail, including the zone-specific grain that makes this distinction visible, is
in the report and in `00` §5.

## Two things that need your confirmation before this goes further

1. **`tt_whole_field_uc.md` and your sketch photo never reached this session**, despite being referenced as
   attached. This build worked from your prompt text alone. If either file has detail this build missed
   (especially a specific `sort_rank` definition), flag it and this should be revisited.
2. **`sort_rank` was requested as an existing function to fix — none was found anywhere in either repo.** A
   new, handedness-correct version was built from scratch instead (`dp_uc42_kernel.py::sort_rank`), labeled
   provisional. If a version already exists somewhere this search missed, that one should supersede it.

Also open: whether to promote the static facet-grid layout (shipped) vs. the animated-frame alternative
(not built) — see `00` §7 item 3 for the recommendation and reasoning.

## Package contents

```
README.md                                     — this file
00_dpo_orchestration_record.md                — DPO spine: plan, gates, findings, escalations
01_strategy_intake.md                         — gaps, premise stress-test, source fitness
02_engineering_design.md                      — data model, EDA, design decisions
03_governance.md                              — Rule-1 search, new-object register, lineage
04_engineering_build.md                       — build manifest, environment notes
05_quality_certification.md                   — DQ scorecard, verification, cert decision
06_consumer_success.md                        — how to read this, dashboard spec, reuse patterns
07_platform_marketing.md                      — monitors, cost audit, bid-vs-actual
BID_2026-09-10_uc-pos-016-turner-whole-field.md — the competitive bid (awarded, reconciled in 07)
uc_ledger_AI_PATCH_uc-pos-016-turner-whole-field.md — ledger patch, pending paste into the MLB repo ledger

dp_uc42_kernel.py                             — governed functions: derive_loc, hit_direction, in_zone
                                                 (verbatim, inherited) + sort_rank, P_THROWS_COLORS,
                                                 MARKER_SIZE (new, this UC)
dp_uc42_turner_whole_field.py                 — build script; run this to reproduce all receipts
dp_uc42_verification.py                       — independent spot-verification (33 checks, second code path)
dp_uc42_build_pdf.py                          — report.md -> branded PDF
dp_uc42_build_dashboard.py                    — receipts -> self-contained interactive HTML dashboard

dp_uc42_turner_whole_field_report.md          — the narrative report (source of the PDF)
dp_uc42_turner_whole_field_report.pdf         — branded PDF (reportlab; weasyprint unavailable, see 04)
dp_uc42_turner_whole_field_dashboard.html     — interactive dashboard, Chart.js vendored inline

out/
  dp_uc42_turner_bip_extract.csv              — 1,832 rows, every Turner regular-season BIP 2023-2026
  dp_uc42_kpi_directional_by_zone_year.csv    — pull/oppo/straightaway counts + rates
  dp_uc42_significance_2026_vs_pooled.csv     — pooled two-proportion z-tests
  dp_uc42_ooz_share_by_year.csv               — share of BIP that came from an outside-zone pitch
  dp_uc42_verification_results.csv            — 33/33 independent spot-check results
  dp_uc42_fig1_facet_grid.png                 — whole-field directional map (hit_direction x game_year x p_throws)
  dp_uc42_fig2_pull_oppo_trend.png            — pull/oppo rate by season, split on zone
```

## Reproducing this on the real data plane

This package was built in a cloud sandbox because the device bridge to your machine was unreachable this
session (see `04` for the full disclosure) — `dp_uc42_kernel.py` and `dp_uc42_turner_whole_field.py` are
written for your normal environment (`pandas.read_parquet`, standard pyarrow path), not the pure-Python
fallback reader used to build this delivery. To reproduce:

```
python dp_uc42_turner_whole_field.py   # writes everything in out/
python dp_uc42_verification.py         # re-runs the 33 independent spot-checks
python dp_uc42_build_pdf.py            # rebuilds the PDF from the .md report
python dp_uc42_build_dashboard.py      # rebuilds the dashboard HTML
```

All four expect to be run from this folder, with `phils_{2023..2026}.parquet` reachable the normal way
(`get_phillies_data()` / `mlb_data.py` conventions).

## Governed objects this UC inherited vs. introduced

| Object | Status |
|---|---|
| `derive_loc`, `hit_direction`, `in_zone` | Inherited verbatim from `dp_uc40_kernel.py` / `Baseball Functions.ipynb` |
| `sort_rank(direction, stand)` | **New**, provisional — not yet ratified (see confirmation item 2 above) |
| `P_THROWS_COLORS`, `MARKER_SIZE` | New, locked per your corrections (brand-consistent color map, fixed marker size) |
| WF-1 `oppo_rate_ooz`, WF-2 `pull_rate_ooz` | New, diagnostic-only — not a ledgered KPI (see `00` §7 item 4) |

Full detail on every item above, including reasoning, is in `03_governance.md`.
