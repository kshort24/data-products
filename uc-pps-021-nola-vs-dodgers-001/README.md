# uc-pps-021 · Aaron Nola advance scout vs the LA Dodgers
### Governed data-product package · build `dp_uc25` · UC #26 · value stream `pps`

The 00–08 markdowns in this folder are the **departmental receipts** — the per-layer proof that this product was built on the agentified-organization governance principles (entity lock, no CDE inference, locked-KPI inheritance, DQ + join validation, independent verification, certification). They document the four-layer workflow (Intake → Design → Build → Certify) for the reader report and its consumables.

## Folder contents

| File | Layer | Seat |
|---|---|---|
| `00_DPO_delivery_plan.md` | Orchestration | Data Product Owner — spine, agent status, open items, certification recommendation |
| `01_intake_validator_and_source_profile.md` | 1 — Intake | Use Case Validator + Source System Profiler |
| `02_business_glossary_and_domains.md` | 1 — Intake | Business Glossary + Domain Steward + Metadata Mapper |
| `03_data_dictionary.md` | 2 — Design | Data Dictionary (14 CSV receipts) |
| `04_architecture_and_kpi_specs.md` | 2 — Design | Data Architect + KPI Calculator |
| `05_dq_rules_and_join_validation.md` | 2/3 | DQ Rule Definer + Join Validator |
| `06_technical_lineage.md` | 3 — Build | Technical Lineage Builder |
| `07_dq_scorecard.md` | 3 — Build | Data Quality Engineer (+ independent verification 31/31) |
| `08_post_game_backtest.md` | 4 — Certify | Certification closure — projected plan vs the actual 7/22 result |

## Deliverables (in the repo root / `out/`)

- **Reader report:** `dp_uc25_nola_vs_dodgers_report.md` / `.pdf` (branded, 9pp)
- **Consumables:** `dp_uc25_nola_vs_dodgers_persona_card.pdf`, `dp_uc25_nola_vs_dodgers_interactive.html`
- **Governance:** `dp_uc25_nola_vs_dodgers_use_case_spec.md` (§1–§8), `uc-pps-021-Aaron Nola LAD 20260722.md` (contract), `uc_ledger_AI_PATCH_uc-pps-021-nola-dodgers.md`
- **Build + verification:** `dp_uc25_nola_vs_dodgers.py`, `dp_uc25_verification.py` (31/31 PASS), `dp_uc25_backtest.py`
- **Receipts:** `out/dp_uc25_*.csv` (14) + `out/dp_uc25_*.png` (6) + `out/dp_uc25_backtest_*.csv` (4)

## Certification status

**PASS — cleared for internal advance use.** Independent recompute 31/31; 8/8 DQ governance rules PASS; join logic validated; glossary/lineage/dictionary complete and sourced. **Ledger append pending** (patch staged). One medium open item: **O1** — promote `xwobacon` to the glossary and deprecate the contaminated pitch-level `get_stats.xwoba` column.

## Re-certification of the prior Nola products (the "extension" note)

This is the **third** Nola advance product, and it inherits directly from two earlier ones:

| Prior product | UC | Delivered | Folder? |
|---|---|---|---|
| Nola vs Nationals | `uc-pps-008` (dp_uc8) | 2026-06-24 | **none** — origin of the edge / OOZ-CS / AIR-GB KPIs |
| Nola vs Royals | `uc-pps-014` (dp_uc15) | 2026-07-05 | **none** — origin of the slider profile + self-contained locked kernel |

Both predate the `data-products/<uc-id>/` folder convention (which began ~2026-07-13 with the Marsh run), so **neither has its own 00–08 package.** This folder therefore serves double duty: it certifies `uc-pps-021` *and* re-certifies the KPI lineage those two products established —

- the **locked KPI kernel** (`get_stats/nresults`, whiff, chase, putaway, fpsr, hard_hit) is inherited verbatim from the UC8→UC11→UC15 line (see `04`/`06`);
- the **UC8 trio** (edge rate, OOZ called-strike rate, AIR/GB rate) is re-used with its original glossary approval — no re-derivation (see `02`);
- the prior products are **extended, not superseded** — they remain valid opponent-specific reports; only their stale *season* figures are superseded by this UC's live line.

No separate back-fill of 00–08 folders is proposed for `uc-pps-008` / `uc-pps-014`; their governance is carried forward and re-affirmed here. If a full retrospective package is wanted for either, it can be generated on the same template.

## Freshness boundary (important)

The pre-game product was built on the cache **through 2026-07-16** (Nola's prior start). The **2026-07-22 start synced in on 2026-07-24**, after build. The 00–07 artifacts describe the pre-game product as built; `08_post_game_backtest.md` uses the refreshed cache to close the loop. Re-running `dp_uc25_nola_vs_dodgers.py` now will fold the 7/22 game into the season line — expected, and the reason the freshness window is stamped on every artifact.
