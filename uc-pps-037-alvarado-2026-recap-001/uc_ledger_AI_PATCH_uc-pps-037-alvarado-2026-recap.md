# Ledger patch: UC #53 / uc-pps-037 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. (UC52's patch is also still pending; paste it first.)

| 53 | `uc-pps-037` | **José Alvarado 2026 season recap: "The Full Ride"** (2026-10-18) | Delivered · READY-CONDITIONAL (C1–C6) · verified 163/163 · DQ 11/2/0 | `dp_uc53_*` + `uc-pps-037-José Alvarado 2026 Recap 20261018.md`; primary consumables `dp_uc53_alvarado_2026_recap_report.pdf` and `dp_uc53_alvarado_2026_dashboard.html` (Artifact "The Full Ride"). Code, `out/` and trail live in `Agents for Data Products/data-products/uc-pps-037-alvarado-2026-recap-001/` (first recap built entirely in the control-plane folder). First pre-registered verdict ledger (DB-1); first tenure-lens recap |

Pattern inheritance additions (UC53): Season recap UC48 SR-1 → UC49 → UC51 → UC52 → **UC53** · Career frame CF-2c (UC52) → **CF-2d (subject as arguments)** · WB-1 (UC52) → **UC53 (second use; ratify)** · RP-1 (UC52) → **UC53 (second use; ratify)**, **RP-1t** span grain · Cumulative chart CM-1 → **CM-1a corrected spec** · New, provisional: **OD-1** outing bands, **DB-1** decline-or-blip ledger

Next available: **UC #54 / dp_uc54** (pps next `uc-pps-038` · pos next `uc-pos-019`) — as of 2026-10-18.

## Findings worth carrying
1. **CM-D1:** `cumulative_metric.METRICS["woba"]` counts `woba_value` where `woba_denom` is 0 (IBB 0.4, sac bunt 0.9). Pass a corrected spec or fix upstream.
2. **AB-1:** 2026 logs carry automatic balls/strikes with no pitch; K44 counts them as pitches and in-zone. Filter `pitch_type.notna()` for zone and usage.
3. **RK-2:** compute K−BB from counts, not from K44's rounded K% and BB%.
4. **ENT-1:** in Phillies logs, an opposing pitcher's id can appear under a Phillies batter's `player_name`. Always lock by id **and** `phillies_role`.
5. **ENV-3:** laptop VM pip needs `TMPDIR=/tmp/...` while `/sessions` is full; run installs in the foreground.

## Repo-side artefacts to file
- `uc-pps-037-José Alvarado 2026 Recap 20261018.md` → MLB repo root (**filed**)
- `uc_ledger_AI_PATCH_uc-pps-037-alvarado-2026-recap.md` → MLB repo root (**filed**)
- `eda/dp_uc53/` → MLB repo (**filed** by `phillies_dp.eda`)
- Code, reports, dashboard, `out/` → control-plane folder (per RFP; not copied to the MLB root)
