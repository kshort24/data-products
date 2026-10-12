# 07 · Platform & Marketing: `uc-pps-035`

Agents: `cost-watchdog` · `token-economist` · `data-observability` (tripwires only)

## 1 · Tripwires (armed; re-run the build when one trips)

| # | Tripwire | What happens |
|---|---|---|
| T-1 | **His first 2027 pitch** (spring excluded) | v1.1.0: each start graded against the Still-Wheeler card (ON-SCRIPT / OFF-SCRIPT / INCOMPLETE). Bars do not move |
| T-2 | **CF-2 fixed upstream** (`dp_uc49_kernel` v1.0.1, E-2) | Re-pin K49; CF-2b's MI-1/NM-1 wrappers retire; numbers unchanged by design |
| T-3 | **OU-1 retired for innings** (E-3) | Re-pin; GS-1b becomes GS-1; uc-pps-034's Game Score ranks re-checked |
| T-4 | **`jam_rate` edited in `Baseball Functions.ipynb`** | IX-1 pin fails and the build refuses to run. Intended: re-review JR-1, re-pin, re-run |
| T-5 | **Contract news** (extension, option, retirement) | Carry-in update in the freshness manifest; not a correction |
| T-6 | **Savant swing-timing labels appear in the export** | Replace the JR-1/ST-1 proxy with the source field; breaking for ST-1 |

## 2 · Cost audit (`cost-watchdog`)

| Hotspot | Cost | Recommendation |
|---|---|---|
| Reading the house format (UC49 00/01/02/03/04/05/06/07/BID/README, UC49 kernel and build, UC50 07) | ~70k tokens of input | Still the largest single item (C-1 carried a fourth time). A `tpl/` receipt skeleton or a recap skill card would cut it to ~20k |
| EDA printed to context (headlines dumps while hunting the slide window) | ~25k | Write EDA to a file and print a 20-line summary (UC50 C-3, not followed here) |
| Two skill loads (dataviz, artifact design) | ~15k | Fixed cost for any UC with a dashboard; price it (C-8) |
| `plotly.min.js` inlined (4.8 MB) in three dashboard copies (MLB root, this folder, Artifact) | disk | Shared `_assets/plotly.min.js` for repo copies (carried from UC49) |
| Client-population scan (all 128 opponent files for the intercept column) | ~2 s, 0.9M rows in memory | Fine on the VM; would not scale to all of Statcast |
| Cloud render environment (plotly, kaleido, weasyprint install) | ~1 min | A pinned requirements file for the render step |

## 3 · Bid vs actual (`token-economist`)

Denominator: **session tokens from the live counter**, read at checkpoints (bid filed, build green, figures shipped, dashboard QA, PDF, harness 204/204, governance). The in/out split is estimated from what was written (~1,900 lines of code, 12 governance files, the report, reasoning). Minutes are wall clock from the first tool call (12:57 ET) to the final write.

| Phase | Bid in+out | Bid min | Actual in+out (counter) | Actual min |
|---|---|---|---|---|
| T0 Intake, two-repo recon, house format, notebook, Rule-1, carry-ins, id scan | 307k | 6 | ~303k | 8 |
| T1 Kernel (CF-2b, IX-1, OU-2) + build + EDA, iterations | 81k | 10 | ~111k | 9 |
| T2 Figures (13) + palette validation + render QA | 59k | 7 | ~87k | 7 |
| T3 Narrative dashboard + headless QA + Artifact | 74k | 8 | ~61k | 6 |
| T4 Feature report (builder) + PDF | 26k | 4 | ~24k | 3 |
| T5 Verification harness (incl. one fix cycle and recommits) | 36k | 4 | ~45k | 5 |
| T6 Governance 00–07, README, contract, ledger, delivery copies | 92k | 12 | ~50k | 8 |
| D Defect discovery (inside T1/T5) | 13k | 2 | (inside) | (inside) |
| **Total** | **~688k (560k in / 128k out)** | **~53** | **~681k (≈ 580k in / ≈ 101k out, est.)** | **~46** |

**Credits at list ($10/M in, $50/M out):** bid ≈ **$12.00**, actual ≈ **$10.85** (−10%).
**Tokens −1%, output −21%, time −13%.** Full bid scope delivered (report, dashboard + Artifact, notecard, card, ledger, harness, receipts), plus one unbid item: the delivered copies of every deliverable and receipt in this folder, as the client asked.

## 4 · Calibration findings (ninth instrumented bid)

- **C-1 · T0 from the counter held again** (bid 300k sunk, actual ~303k). Keep it.
- **C-2 · Output came in under at 1.0×** (−21%). A recap built with a report *builder* (numbers formatted in code) writes less prose than a hand-written one. **Next recap: 0.8× scope-scaled output.**
- **C-3 · T1 input ran over (+37%)** because EDA went to context and the first build had two real defects (OU-1, the slide window). UC50's rule (EDA to file) was not followed. **Price T1 at ~80k in when the subject has a reported number to reconcile.**
- **C-4 · The defect line paid five times:** MI-1, NM-1, OU1-1, SJ-1, HP-13 (plus SR-2, a method rather than a defect).
- **C-5 · Time rule over-predicted again:** 681k → 68 × 0.8 = 54 min predicted, ~46 actual (0.68). **Use 0.7 for device builds** (UC50 found the same).
- **C-6 · Render QA paid** (notecard date axis, duplicated plot titles, phone overflow, nav overlap). Keep ~12k.
- **C-7 (new) · The harness caught a build defect** (SJ-1, 125 vs 124) that the DQ scorecard could not see, because the harness re-implemented the KPI from its definition rather than re-running the build's filter. Keep harnesses definition-first.
- **C-8 (new) · Price skill loads** (~15k) as a fixed line on any UC that ships a dashboard or new chart palette.

## 5 · What this product makes possible next (the marketing half)

- **A card for every 2027 starter.** The season card (OC-1, ratification pending) plus CF-2b gives Nola, Sánchez, Luzardo and Painter a registered 2027 bar in one call each, before spring training.
- **"Verify the stretch" as a service.** SR-2 checks any reported "N starts with an ERA of x" against the log and either names the window or refuses. Useful for broadcast and for front-office memos.
- **The Nola recap** (in flight in `October 2026.ipynb`). Same build, three constants; the chase-dependency thread maps onto ch. 3 and the card.
- **The contract-value board (E-8).** With a salary and WAR source, "one more year left on his deal" becomes gradeable.

## 6 · Ledger

Patch file: `uc_ledger_AI_PATCH_uc-pps-035-wheeler-2026-recap.md` (**PENDING PASTE**). Next available after this UC: **#52 / `dp_uc52`** (pps next `uc-pps-036` · pos next `uc-pos-019`).
