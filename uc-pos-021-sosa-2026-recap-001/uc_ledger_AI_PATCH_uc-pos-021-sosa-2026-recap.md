# Ledger patch: UC #56 / uc-pos-021 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. Paste the UC52–UC55 patches first; they are still pending.

| 56 | `uc-pos-021` | **Edmundo Sosa 2026 season recap: "We Really Do Love Sosa"** (2026-10-23) | Delivered · READY-CONDITIONAL (C1–C5) · verified 161/161 · DQ 12/5/0 | `dp_uc56_*` + `uc-pos-021-Edmundo Sosa 2026 Recap 20261023.md`; primary consumables `dp_uc56_sosa_2026_recap_report.pdf` and `dp_uc56_sosa_2026_dashboard.html` (Artifact "Love Sosa"). **Everything** (code, out/, eda/, trail) in `Agents for Data Products/data-products/uc-pos-021-sosa-2026-recap-001/` per RFP; MLB data plane read-only. Third pos recap; first end-of-tenure hitter recap; first walkaway rule (WA-1) |

Pattern inheritance additions (UC56):
- Season recap SR-1 … UC55 → **UC56 (third pos; end-of-tenure framing from UC53)**
- pos spine K55 → **K56** (K55 + K46 + WB-2 wrapper)
- TR-1 → **UC56 (All-Star-break date from the schedule)**
- ER-1 → **UC56 (second use, parameters unchanged)**
- New, provisional: **OZ-1** out-of-zone damage, **WA-1** walkaway number

Next available: **UC #57 / dp_uc57** (pps next `uc-pps-038` · pos next `uc-pos-022`) — as of 2026-10-23.

## Findings worth carrying
1. **WB-2:** inherited `nresults_unrounded` weights pooled multi-season wOBA with 2026 constants when `game_year` is not in the level. Use the K56 wrapper or add `game_year` and aggregate.
2. **SRC-5:** a `pd.concat([nphl, pos])` client frame can span two teams; the opponents file has no bat tracking.
3. **GL-1:** "EV50" means median in this notebook, not Statcast's hardest-half mean.
4. **D-1:** `argmax` on a diff with a leading NaN returns 0; fill before argmax.
5. **Q-3 (plotly):** two `$` in one title/subtitle render as MathJax; use `&#36;`.
