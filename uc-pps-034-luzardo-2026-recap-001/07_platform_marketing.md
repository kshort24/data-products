# 07 · Platform & Marketing: `uc-pps-034`

Agents: `cost-watchdog` · `token-economist` · `data-observability` (tripwires only)

## 1 · Tripwires (armed; re-run the build when one trips)

| # | Tripwire | What happens |
|---|---|---|
| T-1 | **He pitches in Game 162** (activated as a reliever, carry-in) | v1.1.0: new anchor, one OC-1 graded outing, the regular-season rates move by one relief outing |
| T-2 | **Any postseason pitch** | OC-1 grades each outing (ON-SCRIPT / OFF-SCRIPT / INCOMPLETE); the postseason ledger gains rows. Bars do not move |
| T-3 | **`get_nphillies_data()` dedup changes** (E-3) | HP-08 / DQ-22 re-run; the client frame should then equal CF-2 on regular-season rows |
| T-4 | **`dp_uc48_kernel` v1.0.1** lands (E-2) | Re-pin the parent hash; US-1b retires in favour of the upstream fix |
| T-5 | **2027 season begins** | CX-1 and KP-1 gain a season; ranks are superseded, not corrected |

## 2 · Cost audit (`cost-watchdog`)

| Hotspot | Cost | Recommendation |
|---|---|---|
| Reading the house format (uc-pps-033 00/07/BID/README, kernel, build) | ~55k tokens of input | Still the largest single item. A `tpl/` receipt skeleton or a skill card for the 00–07 + BID pattern would cut it to ~15k (C-1 carried) |
| Carry-in research (7 facts, 7 fetches) | ~15k | Worth it: one fact (the IL) superseded the prompt's premise and reshaped two chapters |
| Device environment repair (pyarrow/scipy/plotly into `/tmp`) | ~3 min, ~6k | **Closed uc-pps-033's staging hotspot**: 0 data files staged (vs 16 files / 60 MB). The installs are session-scoped; put the two pip lines in a bootstrap script |
| Commit caching on the bridge (same staged path delivered stale) | 3 wasted calls | Stage every revision under a new path (now standard) |
| `plotly.min.js` inlined (4.8 MB) in two dashboard copies | disk | Carry-forward: a shared `_assets/plotly.min.js` for repo copies |
| PNG export via kaleido | ~8 s | Fine |

## 3 · Bid vs actual (`token-economist`)

Denominator: **incremental session tokens** from the session counter (the unit the bid was priced in). The in/out split is estimated from the size of what was written. Minutes are wall clock from the first tool call (00:24 UTC) to the final commit.

| Phase | Bid in | Bid out | Bid min | Actual in (est.) | Actual out (est.) | Actual min |
|---|---|---|---|---|---|---|
| T0 Intake, recon, carry-ins, env repair, profile | 245k | 6k | 8 | ~245k | ~8k | 7 |
| T1 Kernel (CF-2) + build + receipts, iterations | 90k | 22k | 9 | ~48k | ~24k | 13 |
| T2 Figures + brand + palette validation | 55k | 12k | 6 | ~26k | ~13k | 5 |
| T3 Narrative dashboard (+ headless QA, Artifact publish) | 50k | 22k | 8 | ~36k | ~22k | 5 |
| T4 Feature report + PDF | 30k | 10k | 4 | ~8k | ~9k | 3 |
| T5 Verification harness | 35k | 10k | 4 | ~17k | ~11k | 3 |
| T6 Governance 00–07, README, contract, ledger, commits | 45k | 20k | 10 | ~35k | ~30k | 9 |
| D Defect discovery (in T0/T1) | 10k | 3k | 2 | ~10k | ~3k | (in T1) |
| **Total** | **~560k** | **~105k** | **~51** | **~425k** | **~120k** | **~45** |

**Credits at list ($10/M in, $50/M out):** bid ≈ **$10.85**, actual ≈ **$10.25** (−5.5%).
**Input −24%, output +14%, time −12%.** Full scope delivered, plus one unbid item (the Artifact publish of the dashboard). Just outside ±5% on cost, and again an input under-run offset an output over-run. Session counter at close: ~545k incremental tokens (00:24–01:09 UTC).

## 4 · Calibration findings (seventh instrumented bid)

- **C-1 · T0 was priced from the counter at bid time and landed exactly.** Pricing sunk work from the live counter is the right method; keep it.
- **C-2 · Output came in *over* for the first time** (+14%), after six under-runs. Narrative products write more prose (the report, eight chapters of dashboard copy, 00–07 with arguments). **Next bid: 1.0× scope-scaled actual for narrative UCs, 0.9× for analytic ones.**
- **C-3 · T1 input came in at half the bid.** Running on the device means build output is read as a short JSON summary rather than re-staged frames. **Price T1 at ~50k in when the build runs on the device.**
- **C-4 · The defect line paid again.** Priced at 13k; found O-26, BS-1 (and with it the resolution of uc-pps-033 V-3), ENV-1, E-7 and HP-10. Keep it.
- **C-5 · Time rule held:** ~545k tokens → 54.5 min × 0.8 = 44 min predicted, ~45 actual.
- **C-6 (new) · Price a render-QA line for dashboards** (~5k in, 2 min). Headless screenshots at desktop light/dark and phone width caught four defects (NaN payload, plot height overlap, dark-mode ink, a stray U+FFFD in the vendored library) that the harness could not see.

## 5 · What this product makes possible next (the marketing half)

- **The October card as a series.** OC-1 is subject-agnostic. A card for every Phillies starter and high-leverage reliever before the Wild Card round costs one function call each, and the postseason grades all of them in one v1.1.0 run.
- **Game stories on demand.** The Labor Day stepper takes any `game_pk`. A "start of the week" product for broadcast is the same receipts with a different key.
- **The recap queue.** Cell 118 lists Arraez, Nola, Painter and Wheeler next. With SR-1 + CF-2 ratified, each is the two calls in `04` §5 plus the chapter template.
- **The acquisitions board (E-8).** The one form not built. It needs a transaction source; with one, "one of Dombrowski's best" becomes gradeable.

## 6 · Ledger

Patch file: `uc_ledger_AI_PATCH_uc-pps-034-luzardo-2026-recap.md` (**PENDING PASTE**). Next available after this UC: **#50 / `dp_uc50`** (pps next `uc-pps-035` · pos next `uc-pos-018`).
