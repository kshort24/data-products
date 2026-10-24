# Ledger patch: UC #57 / uc-pos-022 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. Paste the UC52-UC56 patches first; they are still pending.

| 57 | `uc-pos-022` | **Trea Turner 2026 season recap: "Sounding the Alarm"** (2026-10-23) | Delivered · READY-CONDITIONAL (C1-C6) · verified 34/34 · DQ 10/3/0 | `dp_uc57_*` + `uc-pos-022-Trea Turner 2026 Recap 20261023.md`; primary consumables `dp_uc57_turner_2026_recap_report.pdf` and `dp_uc57_turner_2026_dashboard.html` (Artifact "Sounding the Alarm"). Code and outputs at the MLB root; trail in `Agents for Data Products/data-products/uc-pos-022-turner-2026-recap-001/`. Fourth pos recap; fourth Turner product of 2026 (closes UC25, UC40/40a, UC42); first recap built in a new chat from a filed BID |

Pattern inheritance additions (UC57):
- Season recap SR-1 … UC56 → **UC57 (fourth pos)**
- pos spine K56 → **K57** (K56 + cell_panel + CT-1/PR-1/VS-1/PP-1)
- K40a bat path → **UC57 full-season close-out** (UC40a 2026-09-02 cut reproduced exactly)
- New, provisional: **PR-1** pitch-recognition gap; rules **CT-1**, **PP-1**; adopted **VS-1**

Next available: **UC #58 / dp_uc58** (pps next `uc-pps-038` · pos next `uc-pos-023`) — as of 2026-10-23.

## Findings worth carrying
1. **SRC-PA:** `events.notna()` over-counts PA by baserunning outs (`caught_stealing_2b`); use K40 `pa_rows`.
2. **NA-1:** nullable dtypes in the house log break `np.where` on comparisons; `.fillna(False)` first.
3. **CPG-1:** the notebook's pitch-group map puts KN in Breaking; the house map has it in offspeed.
4. **C-15:** a new chat costs ≈230k before the first line of code (session load + re-recon). Price it.
