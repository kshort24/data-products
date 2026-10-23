# Ledger patch: UC #55 / uc-pos-020 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. Paste the UC52, UC53 and UC54 patches first; they are still pending.

| 55 | `uc-pos-020` | **Bryson Stott 2026 season recap: "Another Level?"** (2026-10-22) | Delivered · READY-CONDITIONAL (C1–C5) · verified 185/185 · DQ 15/5/0 | `dp_uc55_*` + `uc-pos-020-Bryson Stott 2026 Recap 20261022.md`; primary consumables `dp_uc55_stott_2026_recap_report.pdf` and `dp_uc55_stott_2026_dashboard.html` (Artifact "Stott 2026 Recap"). Code and `out/` live in the MLB root (data plane, per RFP); trail and delivered copies in `Agents for Data Products/data-products/uc-pos-020-stott-2026-recap-001/`. Second pos recap; first governed era detector (ER-1) and infield expected-outs proxy (IO-1) |

Pattern inheritance additions (UC55):
- Season recap SR-1 … UC54 → **UC55 (second pos)**
- pos spine K54 → **K55** (K54 + K40a)
- Bat path K40a (uc-pos-014) → **UC55 (second use; conventions re-proven)**
- TR-1 → **GS-1 (labelled eras)**
- XO-2 → **IO-1 (infield, A-1 pool both halves)**
- New, provisional: **ER-1** form eras, **GS-1**, **IO-1**

Next available: **UC #56 / dp_uc56** (pps next `uc-pps-038` · pos next `uc-pos-021`) — as of 2026-10-22.

## Findings worth carrying
1. **SRC-4:** any `pos[pos.player_name == pn]` notebook frame includes spring, exhibition and postseason PA. Filter `game_type == "R"`.
2. **O-15 confirmed again:** `attack_direction` is pull-negative and stand-normalised. Flip it for display.
3. **C-11:** when the subject *is* the team's regular at a position, a "teammates at that position" pool is too thin. Use both halves of every house game (A-1).
4. **Q-3:** nullable `launch_speed_angle` / `launch_speed` must stay in BIP denominators (O-8). An inline `.mean()` on a nullable comparison silently drops them.
5. **ENV-4:** the device commit tool can re-serve a cached file for a repeated staged path. Use versioned staged names and grep before running.

## Repo-side artefacts to file
- `uc-pos-020-Bryson Stott 2026 Recap 20261022.md` → MLB repo root (**filed**)
- `uc_ledger_AI_PATCH_uc-pos-020-stott-2026-recap.md` → MLB repo root (**filed**)
- `eda/dp_uc55/` → MLB repo (**filed** by `phillies_dp.eda`)
- Code, `out/`, report, dashboard → MLB root (**filed**); copies of the report and dashboard → control-plane folder
