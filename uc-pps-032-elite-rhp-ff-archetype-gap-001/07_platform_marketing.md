# 07 · Platform & Marketing — `uc-pps-032`

Agents: `cost-watchdog` · `token-economist` · `data-observability` (tripwires only)

## 1 · Tripwires (armed — re-run the build when one trips)

| # | Tripwire | Why it matters |
|---|---|---|
| T-1 | **Bowlan's status** is confirmed (IL or active) | Turns the carry-in scenario into data. If out, EFS = 0 and the room's best is Duran (results-only) |
| T-2 | A full-season `nphl` file lands for any **watch-list** arm (Misiorowski first) | Moves him onto the board or off it; the external #1 may change |
| T-3 | **McFarlane reaches 100 four-seams** | THIN comes off; he joins the population and his results grade stabilizes |
| T-4 | **Painter's whiff rate on the four-seam clears .22** (grade ≈ 50) over ≥ 150 swings | The better-looking pitch starts landing; he moves out of "neither" |
| T-5 | The 2027 season begins | SG-6 re-fits drift with 2027 as the reference year — every grade in this package is superseded, not corrected |

## 2 · Cost audit (`cost-watchdog`)

| Hotspot | Cost | Recommendation |
|---|---|---|
| Staging 140 parquet files (111 MB `nphl` + 60 MB Phillies) into the sandbox | ~3 min, ~25k tokens of tool output | **Cache FR-1 as `data/_governed/house_pitch_universe.parquet`** (1.22M rows) on the laptop. It's identical across every UC that touches `nphl`, and would make the next archetype a 20-second build |
| FR-1 rebuild in the harness (family B) | 12 s | Keep — the harness must not trust the build's copy |
| `plotly.min.js` inlined per dashboard (4.8 MB) | disk | Carry-forward of F1 (uc-pps-026): one shared `_assets/plotly.min.js` for all dashboards |
| Split-half k estimation | < 1 s | none |

## 3 · Bid vs actual (`token-economist`)

Denominator: **incremental session tokens** (new context + generated), read from the session's token counter
— the same unit the bid was priced in. Minutes are wall clock from the first tool call (02:49 UTC) to the last
commit.

| Phase | Bid in | Bid out | Bid min | Actual in (est.) | Actual out (est.) | Actual min |
|---|---|---|---|---|---|---|
| T0 Intake, recon, staging, `nphl` profiling | 300k | 30k | 12 | ~300k | ~15k | 12 |
| T1 Universe, names, drift, reliability | 60k | 18k | 8 | ~45k | ~10k | 5 |
| T2 Kernel + build + receipts | 90k | 45k | 16 | ~60k | ~22k | 6 |
| T3 Figures + brand compliance | 45k | 22k | 9 | ~40k | ~9k | 4 |
| T4 PDF + explorer | 45k | 35k | 11 | ~45k | ~14k | 5 |
| T5 Verification | 35k | 20k | 7 | ~15k | ~9k | 3 |
| T6 Governance spine + commit | 35k | 55k | 12 | ~20k | ~31k | 16 |
| Contingency | 30k | 11k | 5 | 0 | 0 | 0 |
| **Total** | **~640k** | **~236k** | **~80** | **~525k** | **~110k** | **~51** |

**Credits at list ($10/M in, $50/M out):** bid ≈ **$18.20** → actual ≈ **$10.75** (−41%).
**Input −18%, output −53%, time −36%.** Full scope delivered; nothing de-scoped.

## 4 · Calibration findings (fifth instrumented bid)

- **C-1 · T0 is now the whole input budget.** Recon + staging + profiling was ~55% of input tokens — staging
  output (file lists, 128-file profile tables) is the expensive part, not analysis. The cached governed universe
  (§2) would cut the next archetype's T0 by more than half. **Price T0 by file count, not by question.**
- **C-2 · Output was over-bid for the fifth time running.** Five of five instrumented bids have come in under on
  output. Inheritance (a scaffold 00–07, a PDF builder, a harness pattern) saves writing more than reading.
  **Next bid: output at 0.5× the analogue, not 0.9×.**
- **C-3 · The 0.10 min / 1k-token rule held.** ~635k tokens → 64 min predicted vs ~51 actual; tighter than
  uc-pps-030 (3× high). Keep it, with a 0.8 multiplier on a warm sandbox.
- **C-4 · Price a defect line again.** Three new defects (O-23, O-24, BC-1) were found by building, not by
  reading. uc-pps-029 recommended pricing defect discovery; it was right, and it wasn't priced here either.
- **C-5 · The contingency was unused** (sixth time in a row). Drop to 0% on a warm sandbox; keep 5% when the
  device bridge is unproven.

## 5 · What this product makes possible next (the marketing half)

- **Archetype #2 in an afternoon.** The engine takes a spec: an elite LHP sweeper, a ground-ball sinker, a
  ride-first reliever four-seam. First generalization task: hand-aware horizontal break in AF-2 (LHP arm side is
  +`pfx_x`, so an LHP sweeper's glove-side break is negative).
- **Hitter archetypes.** AF-1 is pitch-shaped today; the same two-axis idea (shape = bat speed/attack angle,
  results = xwOBAcon/whiff) fits `pos` — and uc-pos-014 already governed the bat-path columns.
- **A trade board, if you want one.** Needs a league-wide pull (00 E-4) and a contract source. The grading,
  the stabilization and the needle already exist.

## 6 · Ledger

Patch file: `uc_ledger_AI_PATCH_uc-pps-032-elite-rhp-ff-archetype-gap.md` (**PENDING PASTE** — the ledger still
reads "next #25"). Next available after this UC: **#48 / `dp_uc48`** (pps next `uc-pps-033` · pos next `uc-pos-018`).
