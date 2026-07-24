# Data Product Owner — Delivery Plan & Approval Gate
### UC-PPS-021 · Aaron Nola advance scout vs LA Dodgers @ CBP · orchestrated run 2026-07-22 (pre-game) · folder assembled 2026-07-24

This is the spine of the certified package: it records the decomposition, the four-layer agent workflow status, what each seat produced, the open items requiring human decisions, and the certification recommendation. All artifacts referenced live in this folder or in the repo root (`dp_uc25_*`) with receipts under `out/`.

> **Lineage note — this is the 3rd Nola advance product.** It extends `uc-pps-008` (vs WAS, 2026-06-24) and `uc-pps-014` (vs KC, 2026-07-05), which were delivered **before** the `data-products/<uc-id>/` folder convention existed (that convention began with the Marsh run, ~2026-07-13). Those two products therefore have **no 00–07 folder of their own**; this package re-certifies the KPI lineage they established and carries it forward. See README §"Re-certification of the prior Nola products."

---

## Decomposition (value-stream framework)

| Layer | Resolution |
|---|---|
| **Value Stream** | Phillies Pitching (`pps`) |
| **Use Case** | Bring the Nola advance file current (through his last start) and answer, for tonight's Dodgers start: where does the season line sit, what has shifted in his approach, *why* are the previously-identified leaks happening, and how do the seven named hitters match up. |
| **Personas** | Pitcher (Nola), Catcher (Realmuto/Marchan — Stubbs injured), Manager, Pitching Coach, Pitching Analyst |
| **Business questions** | 5 (see `uc-pps-021-*.md` §Business Questions) — season line, approach shift, lefty-leak mechanism, ABS re-test, the 7-hitter matchup |
| **KPIs** | wOBA/OPS/K%/BB%/HR-PA (locked `nresults`), whiff/chase/in-zone/putaway/FPSR/hard-hit (locked), **edge / OOZ-called-strike / AIR-GB (inherited from UC8, glossary-approved)**, chase-up (UC8 helper), xwOBAcon (report-local, DQ-hardened), ip_computed, monthly usage/velo |
| **Grain** | pitch-level; entity key `pitcher == 605400`; cascades via game_year, batter `stand`, month, pitch_name, and per-hitter (H2H) |
| **Data domains** | At-Bat Outcomes, Batted Ball Profile, Pitch Profile, Pitch Outcomes, Strike Zone, wOBA Weights |
| **Source frame** | `data/phillies/phils_2015..2026.parquet`, `phillies_role=='pitching' & pitcher==605400 & game_type=='R'`, deduped |

---

## Agent workflow status

| Layer | Status |
|---|---|
| Layer 1 — Intake & Discovery | **complete** |
| Layer 2 — Design | **complete** |
| Layer 3 — Build | **complete** |
| Layer 4 — Certify & Publish | **complete — verified 31/31; cleared for internal advance use; ledger append pending** |

### Agent assignments

| Agent (seat) | Artifact | Status | Note |
|---|---|---|---|
| Use Case Validator | `01_intake_validator_and_source_profile.md` | complete | No blocking gaps; 5 non-blocking items logged |
| Source System Profiler | `01_…` | complete | CDE fitness confirmed; entity lock 605400; freshness 7/16 (build) |
| Business Glossary Agent | `02_business_glossary_and_domains.md` | complete | Locked terms + UC8 trio; no inferred meaning |
| Domain Steward Proxy | `02_…` | complete | 6 domains; Nolan Hoffman contamination guard noted |
| Data Architect | `04_architecture_and_kpi_specs.md` | complete | Single-source cascade model |
| KPI Calculator | `04_…` | complete | Locked functions inherited verbatim; xwOBAcon DQ-hardened |
| Metadata Mapper | `02_…` / `03_data_dictionary.md` | complete | Physical→glossary; all exact |
| Data Dictionary | `03_data_dictionary.md` | complete | 14 CSV receipts documented |
| DQ Rule Definer | `05_dq_rules_and_join_validation.md` | complete | 8 CDE rules specified |
| Join Validator | `05_…` | complete | **No fan-out** (wOBA merge 29,015→29,015); H2H ids 7/7 unique |
| Technical Lineage Builder | `06_technical_lineage.md` | complete | Column-level, source→KPI |
| Data Engineer | `dp_uc25_nola_vs_dodgers.py` + `out/*.csv` | complete | Executed on parquet; 14 CSV + 6 PNG |
| Data Quality Engineer | `07_dq_scorecard.md` | complete | **6/6 governance checks PASS**; completeness explained |
| Certification Agent | `07_…` + `dp_uc25_verification.py` | complete | **Independent recompute 31/31 PASS — CERTIFY READY** |
| Privacy Watchdog | this doc | complete | **No PII** — public MLB game data; no re-identification risk |
| ML Engineer | n/a | skipped | No prediction/forecast in scope |
| Analytics Enabler / Consumer Onboarding | `..._report.pdf` + `..._persona_card.pdf` + `..._interactive.html` | complete | Reader report, per-persona actions, interactive dashboard |
| **Closure — post-game backtest** | `08_post_game_backtest.md` | **complete** | The 7/22 game synced post-build; plan-vs-actual closes the loop |

---

## Open items (require human DPO decision)

| # | Issue | Source | Severity | Recommended resolution |
|---|---|---|---|---|
| O1 | `xwobacon` (xwOBA on contact) has recurred (UC15 check → UC25 hardened); the locked `get_stats.xwoba` pitch-level column is contaminated by non-BIP rows | KPI Calculator / DQ Engineer | **Medium** | Promote `xwobacon` to the glossary and **deprecate the pitch-level `get_stats.xwoba`** for xwOBAcon reporting repo-wide |
| O2 | Matchup scope = 7 named hitters (manual carry-in), not a confirmed 1–9 lineup | Use Case Validator | Non-blocking | Confirm the actual card pre-game; documented everywhere |
| O3 | Prior Nola products `uc-pps-008` / `uc-pps-014` predate the folder convention — no 00–07 of their own | DPO | Low | This package re-certifies their inherited lineage (README) |
| O4 | **Post-build data event:** the 7/22 start synced into the cache after build (parquet re-wrote 2026-07-24). The pre-game numbers (7/16 cache) will not reproduce against the refreshed cache | Source Profiler | Non-blocking (freshness boundary) | Documented; the `08_post_game_backtest.md` uses the refreshed cache and closes the certification loop |

None are **blocking**. O1 is a governance-completeness follow-up. O4 is the normal pre-game→post-game freshness boundary, handled by the backtest.

---

## Certification recommendation

**`pass — cleared for internal advance use`.** Independent verification (`dp_uc25_verification.py`) recomputed every headline KPI via a separate code path: **31/31 PASS**. Entity lock, dedup, game_type, season coverage, freshness, and H2H coverage all PASS; join logic validated; glossary/lineage/dictionary complete and sourced (not inferred). The one medium open item (O1 xwOBAcon promotion) is a governance-completeness gap, not a correctness gap. **Ledger append pending** (`uc_ledger_AI_PATCH_uc-pps-021-nola-dodgers.md`).

```json
{
  "delivery_plan": {
    "use_case_id": "uc-pps-021",
    "build_id": "dp_uc25",
    "value_stream": "pps",
    "layer_status": {"layer_1_intake":"complete","layer_2_design":"complete","layer_3_build":"complete","layer_4_certify":"complete"},
    "verification": {"tool":"dp_uc25_verification.py","result":"31/31 PASS","status":"CERTIFY READY"}
  },
  "open_items": [
    {"issue":"xwobacon promotion + deprecate pitch-level get_stats.xwoba","source_agent":"kpi_calculator","requires_human":true,"status":"open"},
    {"issue":"matchup scope = 7 named hitters (manual carry-in)","source_agent":"use_case_validator","requires_human":false,"status":"documented"},
    {"issue":"prior Nola products predate folder convention","source_agent":"dpo","requires_human":false,"status":"re-certified here"},
    {"issue":"7/22 game synced post-build (freshness boundary)","source_agent":"source_system_profiler","requires_human":false,"status":"closed by 08_post_game_backtest"}
  ],
  "certification_recommendation": "pass — cleared for internal advance use; ledger append pending",
  "publish_approved_by": "pending (human DPO — Kellen Short)"
}
```

*Human-in-loop protocol: per the DPO contract, the human DPO resolves O1 and appends the ledger row. The product is delivered, verified, and usable; the closure backtest confirms the pre-game plan's predictive value.*
