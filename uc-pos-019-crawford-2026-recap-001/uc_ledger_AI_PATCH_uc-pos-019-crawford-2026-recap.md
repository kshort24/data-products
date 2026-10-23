# Ledger patch: UC #54 / uc-pos-019 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. (The UC52 and UC53 patches are also still pending; paste those first.)

| 54 | `uc-pos-019` | **Justin Crawford 2026 season recap: "Exactly as Advertised"** (2026-10-20) | Delivered · READY-CONDITIONAL (C1–C5) · verified 157/157 · DQ 12/4/0 | `dp_uc54_*` + `uc-pos-019-Justin Crawford 2026 Recap 20261020.md`; primary consumables `dp_uc54_crawford_2026_recap_report.pdf` and `dp_uc54_crawford_2026_dashboard.html` (Artifact "Crawford 2026 Recap"). Code, `out/` and trail live in `Agents for Data Products/data-products/uc-pos-019-crawford-2026-recap-001/`. **First pos-side season recap**; first pre-registered hitter turn test (TR-1) |

Pattern inheritance additions (UC54): Season recap SR-1 UC48 → … → UC53 → **UC54 (first pos)** · pos spine K33 → K34 → K37 → K40 → **K54** · CX-1 (uc-pos-011) → **UC54 (second use; ratify)** · OZ attack regions (uc-pos-005) → **UC54 by IX-1** · CM-1 → **CM-1b multi-panel ghost lines** · RF-2 → **RF-2x rolling xwOBA** · New, provisional: **TR-1** turn ledger, **CC-1** chase cost, **XO-2** sector expected outs

Next available: **UC #55 / dp_uc55** (pps next `uc-pps-038` · pos next `uc-pos-020`) — as of 2026-10-20.

## Findings worth carrying
1. **SF-1:** K40 `nresults_unrounded` drops `sac_fly_double_play` from OBP and wOBA denominators (in NON_AB, not in SF).
2. **TP-1:** K40 `pa_rows` counts `truncated_pa` as a PA and an AB.
3. **CM-D2:** `cumulative_metric.METRICS["hard_hit_rate"]` raises on nullable-float `launch_speed`; pass an NA-safe spec dict.
4. **ENT-2:** `data/opponents/crawford.parquet` is J.P. Crawford (641487), who also batted for PHI in 2017–18. Lock by id, never by name or substring.
5. **SRC-2:** `white-sox-of-25-26.parquet` duplicates 3 Phillies 2026 MLB pitches; any `nphl ∪ pos` frame double-counts them.
6. **Q-8:** KP-1 percentile 0 is a floor, not "last". Print the rank.

## Repo-side artefacts to file
- `uc-pos-019-Justin Crawford 2026 Recap 20261020.md` → MLB repo root (**filed**)
- `uc_ledger_AI_PATCH_uc-pos-019-crawford-2026-recap.md` → MLB repo root (**filed**)
- `eda/dp_uc54/` → MLB repo (**filed** by `phillies_dp.eda`)
- Code, reports, dashboard, `out/` → control-plane folder (per RFP; not copied to the MLB root)
