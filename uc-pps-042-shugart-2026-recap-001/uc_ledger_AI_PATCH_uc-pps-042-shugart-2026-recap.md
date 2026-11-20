# Ledger patch: UC #66 / uc-pps-042 (PENDING PASTE into `uc_ledger_AI.md`; paste UC52–UC65 first)

| 66 | `uc-pps-042` | **Chase Shugart 2026 season recap: "A Solid Middle Reliever Who Rebuilt His Plan Against Lefties"** (2026-11-20) | Delivered · READY-CONDITIONAL (C1–C4) · harness 34/34 · DQ 12/5/0 · V1–V7 11/11 · HP 8/3/1 | `dp_uc66_*` + `uc-pps-042-Chase Shugart 2026 Recap 20261120.md`; consumables `dp_uc66_shugart_2026_recap_report.pdf`, `dp_uc66_shugart_2026_dashboard.html`, 11 PNGs. Trail in `Agents for Data Products/data-products/uc-pps-042-shugart-2026-recap-001/`. First recap with org-chosen comparison sets and the VZ visual rules |

Pattern additions: K64 → **K66** (imports K64 whole) · CS-A `phi_rhp_relief_seasons` (DRAFT) · CS-B · CS-C · IN-1 · LC-1 (= FN-1) · CU-1 · CW-1 · S-1 · **VZ-1…VZ-6**.
Next available: **UC #67 / dp_uc67** (pps `uc-pps-043` · pos `uc-pos-026` · cat `uc-cat-003`) — as of 2026-11-20.

## Findings worth carrying
1. **Grade the client's notebook on the governed frame, then reconcile his printed numbers to it** — here they matched only the regular-season frame, which settled FR-1.
2. **Split cumulative usage by batter hand.** The by-month, all-batters view hid that the sweeper retreat was against lefties.
3. **House zone rate counts automatic balls in-zone (D-7).** A 4-pitch IBB moved a month's zone rate by 1 pt; harnesses on nullable dtypes must use `.sum()/len()`, not `.mean()`.
4. **Device VM:** session disk can fill (install render stack to `/tmp/pylib`, RN-3); reuse of a staged path in `device_commit_files` can deliver a stale file (commit from a fresh staged name and verify md5, RN-4).
