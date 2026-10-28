# Ledger patch: UC #58 / uc-pos-023 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. Paste the UC52-UC57 patches first; they are still pending.

| 58 | `uc-pos-023` | **Kyle Schwarber 2026 home runs, animated: "Forty-Five and a Question Mark"** (2026-10-27) | Delivered · READY-CONDITIONAL (C1-C7) · verified 28/28 · DQ 10/3/0 | `dp_uc58_*` + `uc-pos-023-Kyle Schwarber 2026 HR Animation 20261027.md`; primary consumables `dp_uc58_claude_design_prompt.md` (+ 8 keyframes `out/dp_uc58_k*.png`), `dp_uc58_technical_feasibility_brief.md`, `out/dp_uc58_clip_list.csv`. Code and outputs at the MLB root; trail in `Agents for Data Products/data-products/uc-pos-023-schwarber-2026-hr-animation-001/`. **First Claude Design handoff UC** (consumer is a model); third Schwarber product of 2026 (after UC21, UC33) |

Pattern inheritance additions (UC58):
- Cumulative engine `cumulative_metric` → **UC58** (first governed use with `reconcile=`; DH-1 and PA-X1 wrappers)
- WPA sign `dp_uc51` (pitching) → **WP-1 (batting mirror)**
- Spray K40 DR-1/PA-L1 + K54 `CBP_DIMS` → **SP-1/SP-2/SP-3** (HR placement at Statcast distance)
- New, provisional: **HB-1** HR barrel share; rules **CP-1, HL-1, PM-1, GR-1**; handoff pattern **CD-1** (receipt-templated prompt + DATA block + keyframes + segment/clip map)

Next available: **UC #59 / dp_uc59** (pps next `uc-pps-038` · pos next `uc-pos-024`) — as of 2026-10-27.

## Findings worth carrying
1. **DH-1:** game_pk order is not game order on doubleheader days; `cumulative_metric` inherits it. `sv_id` is null 2017–26. Propose an `order=` argument in v1.1.
2. **PA-X1:** `cumulative_metric`'s default drops only `truncated_pa`; pass `NON_PA` (or make it the default).
3. **WP-1:** raw `delta_home_win_exp` ranks road HRs last; the batter mirror is required for any "biggest swing" claim.
4. **CP-1:** `cumcount()` on pitch rows is a pitch count. The client's notebook pattern stretches every season 4–6×.
