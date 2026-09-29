# 07 · Platform & Marketing: `uc-pos-018`

Agents: `cost-watchdog` · `token-economist` · `data-observability` (tripwires only)

## 1 · Tripwires (armed; re-run the build when one trips)

| # | Tripwire | What happens |
|---|---|---|
| T-1 | **Game 1 is played** (any PA vs Sale on 9/29) | v1.1.0: a postseason row joins each H2H line (never blended into regular season). The nine plans are graded: did Sale throw each side the predicted mix, and did the four-seam PAs produce more than the slider PAs? |
| T-2 | **The posted lineup differs from the carry-in** | Re-slot the notecard and cards. No number changes; the lineup aggregate re-derives |
| T-3 | **Sale starts again in this postseason** | Same build with a new anchor. TT-1 and the arsenal gain his October pitches |
| T-4 | **`get_nphillies_data()` dedup is fixed** (O-26, E-2) | HP-10 re-runs; the client-method Sale frame should equal the governed one |
| T-5 | **`get_stats` accepts `batter` as a level** (D-50-1, E-1) | The `hitter` display key can retire |

## 2 · Cost audit (`cost-watchdog`)

| Hotspot | Cost | Recommendation |
|---|---|---|
| Exploratory EDA printed wide tables for nine hitters into context | ~75k tokens | **Largest avoidable item.** Write EDA to a file on the device and read a 30-line summary. Would have saved ~55k |
| Reading the house format (uc-pps-034 README/00/BID/07, uc-pos-017 README/06, ledger, skill refs) | ~60k | Still the second-largest item (C-1 carried). A receipt-skeleton skill card would cut it to ~15k |
| Reading `.claude/iron_rules.md` and `preventable_errors.md` | ~8k | Those two files describe an academic-citation toolkit, not this repo's data plane. Skip them for data-product UCs (or move them out of the MLB `.claude/` folder) |
| Notebook read (cells 131–161 with outputs) | ~15k | Worth it: found cells 137 and 152 (HP-11, HP-12) and the client's "jump on Sale early" |
| Render QA (7 PNGs viewed) | ~12k | Paid for itself: 3 defects, including a wrong-direction axis label |
| PDF render in the cloud (pango absent on the VM) | 1 staging round-trip of 14 files (2.7 MB) | Fine. Installing weasyprint in the Windows conda env would remove it |

## 3 · Bid vs actual (`token-economist`)

Denominator: **session tokens from the live counter**, read at checkpoints (ID reservation, end of EDA, end of build, figures, PDF, harness, governance). The in/out split is estimated from the size of what was written (code ~1,700 lines, ~11 governance files, reasoning). Minutes are wall clock from the first tool call (16:47 UTC) to the final commit.

| Phase | Bid in+out | Bid min | Actual in+out (counter) | Actual min |
|---|---|---|---|---|
| T0 Intake, recon, format, notebook, id scan | 260k | 7 | ~260k | 3 |
| T1 Kernel + EDA + build + receipts (incl. T3 narratives) | 75k + 32k | 13 | ~120k | 8 |
| T2 Figures + render QA | 60k | 7 | ~37k | 4 |
| T4 Report + PDF | 28k | 4 | ~15k | 3 |
| T5 Harness | 32k | 4 | ~27k | 3 |
| T6 Governance 00–07, README, contract, ledger, commits | 83k | 12 | ~68k | 13 |
| D Defect discovery (inside T1/T5) | 13k | 2 | (inside) | (inside) |
| **Total** | **~583k (465k in / 118k out)** | **~49** | **~527k (≈ 432k in / ≈ 95k out, est.)** | **~36** |

**Credits at list ($10/M in, $50/M out):** bid ≈ **$10.55**, actual ≈ **$9.07** (−14%).
**Tokens −10%, output −19%, time −27%.** Full bid scope delivered, pre-game consumables first. The optional Artifact dashboard (+$0.50 de-scope line) was not built. It's offered to the DPO as a follow-on.

**D-1 grading.** The bid was written after the build. It was priced mechanically from `uc-pps-034` actuals and rules. The result came in **under** the bid on every phase except T1, which is the opposite of what a bid written to flatter the actuals would show. T1 over-ran by the size of the EDA printout (§2).

## 4 · Calibration findings (eighth instrumented bid)

- **C-1 · T0 from the counter held** (bid 255k + 5k; actual ~260k). Keep it.
- **C-2 · Output under-ran again** (−19%) even with nine narratives. Short per-subject prose is not "narrative" in the `uc-pps-034` sense. **Next bid: 0.8× for multi-subject cards, 1.0× only for long-form narrative.**
- **C-3 · Device-first held for the build** but not for EDA. **Price EDA separately: ~8k per subject if printed to context, ~2k if written to file.**
- **C-4 · The defect line paid:** D-50-1, MV-1, a second O-26 exposure, the house-PA definition gap.
- **C-5 · Time rule over-predicted:** 527k → 52.7 × 0.8 = 42 min predicted, ~36 actual. **For device builds with a deadline, use 0.7.**
- **C-6 · Render QA paid again** (3 defects). Keep ~12k.
- **C-7 (new) · Deadline protocol.** When intake-to-deadline is under 90 minutes: reserve the ID, read T0 off the counter, build and ship the consumable, then file a mechanically priced bid (D-1). It still reconciled within ±15%.

## 5 · What this product makes possible next (the marketing half)

- **The post-game grade (T-1).** Nine plans, each falsifiable: *the four-seam PA will out-produce the slider PA*, *Harper walks more than he chases*, *Sosa doesn't chase a changeup*. One run of the build after the game grades all nine.
- **Game 2 in one call.** The kernel is opponent-agnostic (`04` §7). A card for the Game 2 starter is the same build with a new id and a new narratives module.
- **The reverse card.** The same BF-1 frame, pointed at the Braves hitters against the Phillies' starter, is the `pps` twin of this product.
- **An interactive card deck (Artifact).** The notecard and nine cards as a phone-friendly page for the dugout iPad, if the DPO wants one.

## 6 · Ledger

Patch file: `uc_ledger_AI_PATCH_uc-pos-018-lineup-vs-sale.md` (**PENDING PASTE**). Next available after this UC: **#51 / `dp_uc51`** (pps next `uc-pps-035` · pos next `uc-pos-019`).
