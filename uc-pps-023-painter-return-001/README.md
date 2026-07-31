# uc-pps-painter-return-001

**Andrew Painter — return read vs the Baltimore Orioles, 2026-07-31.**
UC **#29** · contract `uc-pps-023` · build artifact `dp_uc28` · value stream `pps`

Status: ✅ **Build complete — ready for human DPO sign-off.** Internal only.

---

## What this is

Painter starts tonight in Baltimore after five Triple-A rehab-shaped starts following a mid-June option. This package asks whether he adjusted, and turns the answer into four different sets of actions — for Painter, for Realmuto, for the pitching department, and for the manager.

**The short version:** his stuff didn't change and it was never the problem. His four-seam is dead average in velocity, ride, extension and elevation, and it misses roughly half as many bats as the pool median. The most likely reason — a hypothesis, not a finding — is that his arm slot varies 13.8° across his arsenal against a league median of 4.25°. What Triple-A actually changed is his attack plan: four-seam usage from 33% to 49%.

---

## Deliverables

### Reader-facing (in the **MLB repo**, `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB`)

| File | What |
|---|---|
| `dp_uc28_painter_vs_orioles_report.pdf` | **The report.** 11 pages, Phillies-branded, 12 tables, 5 figures. |
| `dp_uc28_painter_vs_orioles_report.md` | Markdown source of the above |
| `dp_uc28_painter_vs_orioles_dashboard.html` | **Interactive dashboard.** Self-contained, 7 tabs, opens in any browser, no server. |

### Build & verification (MLB repo)

| File | What |
|---|---|
| `dp_uc28_painter_vs_orioles.py` | The build. **The only place numbers are computed.** |
| `dp_uc28_build_pdf.py` | Markdown → weasyprint renderer |
| `dp_uc28_build_dashboard.py` | Reads the CSV receipts, inlines them as JSON |
| `dp_uc28_verification.py` | Independent verification — **76/76 checks passed** |
| `out/dp_uc28_*.csv` | 23 CSV receipts — every table in the report and dashboard |
| `out/dp_uc28_fig*.png` | 5 figures, each traceable to a receipt |
| `out/dp_uc28_console_receipt.txt` | Full build stdout |
| `out/dp_uc28_verification_log.txt` | Every verification check, named |

### Governance trail (this folder)

| File | Department |
|---|---|
| `00_dpo_orchestration_record.md` | **Start here.** Sequencing, gates, capability map, publish decision |
| `01_strategy_intake.md` | Strategy & Intake — entity lock, fitness, gap report, steward rulings |
| `02_engineering_design.md` | Engineering (Design) — model, KPI specs, EDA, union validation, lineage |
| `03_governance.md` | Governance — semantic layer, metadata, tagging, privacy |
| `04_engineering_build.md` | Engineering (Build) — implementation, receipts, findings |
| `05_quality_certification.md` | Quality — DQ rules, scorecard, certification, verification |
| `06_consumer_success.md` | Consumer Success — data dictionary, 4 persona cards, queries, dashboard spec |
| `07_platform_marketing.md` | Platform & Marketing — observability, versioning, backtest, narrative |
| `USE_CASE_uc-pps-painter-return-001.md` | The contract — yml header + business questions answered |

---

## What makes this run different

**It's the first `uc-pps` report that declined part of its own brief.** The standard pattern builds a lineup-by-lineup attack plan against the opponent. There is **zero Orioles data in this repo** and Painter has never faced them. Fabricating a lineup was rejected at the intake gate; the use case was formally descoped to a self-scout and the gap was published in the report's own warning box rather than buried in governance. The freed analysis budget went into delivery mechanics — which is where the actual finding turned out to be.

**It introduces benchmarking to the pattern.** A .106 whiff rate is a number. A .106 whiff rate at the 26th percentile on 55th-percentile velocity is a diagnosis. Every future scouting report in this repo should carry a comparison population.

**The two consumer surfaces cannot disagree.** The dashboard reads the same CSV receipts the PDF is written from and performs no recomputation in the browser.

---

## Reading order

- **In a hurry / going to the advance meeting** → the PDF, "Bottom line" section (5 numbered findings).
- **Calling the game tonight** → `06_consumer_success.md` §6.2, your persona card.
- **Checking whether to trust it** → `05_quality_certification.md`, then `out/dp_uc28_verification_log.txt`.
- **Reviewing the pipeline** → `00_dpo_orchestration_record.md`, then 01→07 in order.
- **Exploring the data yourself** → the dashboard, or `06_consumer_success.md` §6.3 query templates.

---

## Open items for the human DPO

Five, none blocking — listed at `00_dpo_orchestration_record.md`. The one that matters most: **the tipping hypothesis is the report's central causal claim and it is correlational.** The report says so twice, in its own voice. It is being instrumented tonight rather than assumed.

## Ledger

The installed `pitcher-scouting-report` skill's `references/uc-ledger.md` is stale and needs a one-line append:

> `| 29 | uc-pps-023 | Painter return read vs BAL (2026-07-31) | Delivered | dp_uc28_painter_vs_orioles* + uc-pps-023-*.md; first self-scout variant |`
>
> Next available: **UC #30 / `dp_uc29` / `uc-pps-024` / `uc-pos-008`**

## Closure

This UC closes on the **post-game backtest** — 8 checks at `07_platform_marketing.md` §7.4. Item 6 (the tipping hypothesis) is the one worth caring about, and a single start cannot settle it.
