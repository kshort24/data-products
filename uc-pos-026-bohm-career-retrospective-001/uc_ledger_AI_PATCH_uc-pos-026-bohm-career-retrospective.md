# Ledger patch: UC #67 / uc-pos-026 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. Paste the UC52–UC66 patches first; they are still pending.

| 67 | `uc-pos-026` | **Alec Bohm, Phillie: 2026 finish + Phillies career retrospective** (2026-11-22) | Delivered · READY-CONDITIONAL (C1–C7) · harness 51/51 · DQ 11/0/0 · V1–V7 8/8 | `dp_uc67_*` + `uc-pos-026-Alec Bohm Career Retrospective 20261122.md`; primary consumables `dp_uc67_bohm_career_retrospective_report.pdf` and `dp_uc67_bohm_career_retrospective_dashboard.html`. Trail in `Agents for Data Products/data-products/uc-pos-026-bohm-career-retrospective-001/`. First out-of-sample score of a parent UC; first deciding-run object; found TP-1 |

Pattern inheritance additions (UC67):
- pos recap spine K61 → **K67** (`spray_frame_for` generalizes K61's side-bound spray frame; `field_outline()` wraps the UC61 geometry)
- New, provisional: **GW-1** deciding run · **XC-1** xBA conversion · **G-LD** batted-ball relevance gate · **RS-1** RISP repeatability
- **TP-1** frame rule: `truncated_pa` non-terminal (house fix to K57 `NON_PA` pending, breaking)

Next available: **UC #68 / dp_uc68** (pps `uc-pps-043` · pos `uc-pos-027` · cat `uc-cat-003`) — as of 2026-11-22.

## Findings worth carrying
1. TP-1: K57 `NON_PA` omits `truncated_pa` (65 rows 2024–26). Run an `events` census against `NON_PA` at T0 of every UC until the house fix lands.
2. Never restate a DQ bar to make it pass. A gap that moves BA, OBP and SLG together is an AB problem.
3. uc-pos-013's career table carries postseason PA (2022–25); its pre-break window carries 3 TP-1 phantom PA.
4. plotly.js collapses a single category axis whose labels are all numeric strings; set `categoryarray` + range (RQ-3).
5. Score parent UCs out of sample with a pre-registered ledger when a recap continues them (H-F pattern).
