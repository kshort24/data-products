# Ledger patch: UC #61 / uc-pos-025 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. Paste the UC52–UC60 patches first; they are still pending.

| 61 | `uc-pos-025` | **Bryce Harper 2026 season recap: "Bryce Harper \| 3 \| The Eye Carried a Softer Bat"** (2026-11-02) | Delivered · READY-CONDITIONAL (C1–C6) · verified 25/25 · DQ 14/0/0 · V1–V7 3/3 | `dp_uc61_*` + `uc-pos-025-Bryce Harper 2026 Recap 20261102.md`; primary consumable `out/dp_uc61_design_kit/` (Claude Design kit + brief), reference `out/dp_uc61_notecard_reference.png`. Trail in `Agents for Data Products/data-products/uc-pos-025-harper-2026-recap-001/`. Closes the Harper 2026 set (UC #23) |

Pattern inheritance additions (UC61):
- pos recap spine K60 → **K61** (subject-parameterized `load_career`)
- `cumulative_metric` (one metric) → **CM-2** whole slash line + career envelope
- UC #23 OZ family → full-season carry-forward (OZ-H)
- First **design-kit** consumable: NC-1 copy registry + sha manifest + Claude Design brief (pattern from UC58's brief)
- New, provisional: AP-1, HC-1, OZ-H, DMG-1, DH-2

Next available: **UC #62 / dp_uc62** (pps next `uc-pps-038` · pos next `uc-pos-026` · cat next `uc-cat-003`) — as of 2026-11-02.

## Findings worth carrying
1. The June ad-hoc "lefties are luck" read (95 PA) did not hold: full-season xwOBA vs LHP .314.
2. K58 `load_career` is subject-bound; use K61's parameterized loader.
3. Nullable `launch_speed >= 95` → NA; `fillna(False)` every pitch-level flag.
4. Spray points are fielded points: 14 hits sit past a foul line; never filter fair territory on hc.
