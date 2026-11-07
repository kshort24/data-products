# Ledger patch: UC #63 / uc-pps-039 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. Paste the UC52–UC62 patches first; they are still pending.

| 63 | `uc-pps-039` | **Alex McFarlane 2026 season recap: "Nasty Stuff, Outlier Heater"** (2026-11-07) | Delivered · READY-CONDITIONAL (C1–C5) · harness 45/45 · DQ 10/6/0 · V1–V7 8/8 | `dp_uc63_*` + `uc-pps-039-Alex McFarlane 2026 Recap 20261107.md`; consumables `dp_uc63_mcfarlane_2026_recap_report.pdf`, `dp_uc63_mcfarlane_2026_dashboard.html` (Artifact "Alex McFarlane 2026"), `out/dp_uc63_design_kit/` (13-slide Claude Design kit). Trail in `Agents for Data Products/data-products/uc-pps-039-mcfarlane-2026-recap-001/`. First recap with the client's narrative as commentary (CL-1) |

Pattern inheritance additions (UC63):
- pitcher recap spine K62 → **K63** (imports K62 whole; no edits upstream)
- **BS-1r**: K52 bullet-slider rule with the hand passed in
- New, provisional: **FO-1** fastball velo × spin rank · **BD-1** bridge-to-Duran outing · **ST-1** stint ledger · **FN-1** first-N outings · **CL-1** client-language copy rule
- Slide-content kit (13 slides) on the UC61 kit pattern

Next available: **UC #64 / dp_uc64** (pps next `uc-pps-040` · pos next `uc-pos-026` · cat next `uc-cat-003`) — as of 2026-11-07.

## Findings worth carrying
1. **EN-3:** in batting-role (`pos`) rows `player_name` is the hitter. Any pitcher population built from pps ∪ pos must name pitchers from pitching rows.
2. **RK-3:** K44 `chase_rate` rounds to .001; percentiles can move by one at ties.
3. Client drafts truncate digits (2.6 → "2"); grade at printed precision with rounding, not truncation.
4. AB-1 recurs: one automatic ball in a 333-pitch frame moves usage shares off 100%.
