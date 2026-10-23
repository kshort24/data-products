# 07 · Platform & Marketing
**data-observability · version-controller · cost-watchdog · token-economist · communications-agent**

## 1 · Tripwires (v1.1.0 triggers)
| # | Tripwire | Action |
|---|---|---|
| T-1 | Statcast publishes a final 2026 OAA whose sign differs from XO-2's | re-check XO-2; C1 wording |
| T-2 | Any 2027 Crawford appearance enters `phils_2027.parquet` | v1.1.0 recap update; the anchor guard refuses a silent rerun |
| T-3 | K40 gains an SF-1 or TP-1 `_fix` | re-run pool ranks; publish the deltas |
| T-4 | UC52/53/54 ledger patches pasted | confirm #55 as next |
| T-5 | A request to share beyond staff (player, media) | privacy re-review (`03` §6) before any surface |

## 2 · Cost audit (cost-watchdog)
- **Most expensive step:** `dp_uc54_hp.py` (~70 s) scans all 130 opponent parquets twice: once for the client's name-filtered frame, once for the client's defense searcher. A one-time name index of `data/opponents/` would cut that to seconds for every future HP family.
- **XO-2 neighbour search:** O(opportunities × pool), ~0.5 s per CF season. The 9-season context run costs ~5 s. Fine at this scale.
- **Storage:** 69 receipts, ~3.6 MB; the dashboard is 0.5 MB (plotly from CDN).

## 3 · Bid vs actual (`token-economist`)
Denominator: the session token counter (one turn; the award came inside the RFP, so the counter never restarted). The in/out split is estimated from what was written: ~169 KB of Python and ~60 KB of receipts. Minutes run from the first tool call (23:07 ET) to the last receipt (~23:53 ET).

| Mark | When | Counter | Δ |
|---|---|---|---|
| C0 | session start | 15,000,000 | — |
| C0' | first visible reading (first-turn load) | 14,869,918 | 130.1k |
| C3 | BID filed (end T0) | 14,711,231 | 158.7k |
| C4 | T1 done (kernel, build, HP, EDA) | 14,626,048 | 85.2k |
| C5 | T2 done (dataviz skill, 10 figures, palette, two render-QA passes) | 14,550,558 | 75.5k |
| C6 | T3+T4 done (narrative, report, PDF, launch-angle fix, dashboard, QA, Artifact) | 14,480,677 | 69.9k |
| C7 | T5 done (harness 157/157) | 14,461,297 | 19.4k |
| C8 | 00–06 written | 14,438,041 | 23.3k |
| C9 | 07, README, contract, ledger patch written | 14,427,867 | 10.2k |
| C-final | this correction + reply (estimated) | ≈14,424,000 | ≈4k |

| Phase | Bid in+out | Bid min | Actual (counter) | Actual min |
|---|---|---|---|---|
| T0 Intake, recon, house format, carry-ins, env, profile, Rule-1, BID | ~290k | 13 | 288.8k | 11 |
| T1 Kernel + build + HP + EDA | 85k | 9 | 85.2k | 10 |
| T2 Figures + palette + render QA | 60k | 7 | 75.5k | 7 |
| T3 Dashboard + QA + Artifact | 45k | 5 | ≈50k (of 69.9k, est. split) | 5 |
| T4 Report + PDF | 14k | 2 | ≈20k (incl. the Q-8 fix loop) | 3 |
| T5 Harness | 30k | 4 | 19.4k | 3 |
| T6 Governance 00–07, README, contract, ledger | 45k | 6 | ≈37k | 5 |
| D Defect discovery | 13k | 2 | (inside T1–T4: SF-1, CM-D2, XO-2 coverage, Q-8) | — |
| Contingency | 16k | 2 | — | — |
| **Total** | **~598k (503k in / 95k out)** | **~50** | **≈576k (≈481k in / ≈95k out)** | **≈46** |

**Credits at list ($10/M in, $50/M out):** bid ≈ **$9.80**; actual ≈ **$9.55 (−3%)**. Tokens came in 4% under bid and minutes 8% under (46 vs 50). The winning bid was delivered under price and ahead of time, with every published number independently verified.

### Comparison with the other season recaps
| UC | Subject | Total (counter) | Minutes | Shape |
|---|---|---|---|---|
| UC48 `uc-pps-033` | Bowlan (RP) | 530k | 42 | PDF + dashboard |
| UC49 `uc-pps-034` | Luzardo (SP) | 545k | 45 | PDF + dashboard |
| UC51 `uc-pps-035` | Wheeler (SP) | 681k | 46 | PDF + dashboard |
| UC52 `uc-pps-036` | Mayza (RP) | 469k | 35 | 9 pp · 8 ch · 10 fig |
| UC53 `uc-pps-037` | Alvarado (RP, tenure) | ≈518k | ≈41 | 10 pp · 7 ch · 10 fig · 2 new |
| **UC54 `uc-pos-019`** | **Crawford (CF, rookie)** | **≈576k** | **≈46** | **10 pp · 7 ch · 10 fig · 3 new · first pos recap** |

## 4 · Calibration findings (sixth instrumented recap bid)
- **C-1 · T0 from the counter:** held (bid ~290k vs 288.8k).
- **C-2 · Build tranches:**
  - T1 landed exactly on bid.
  - T2 ran +26%. The second render-QA pass (5 figures) and the dataviz skill load (~10k) were under-priced. Price T2 at 70k for a recap with 3+ "rebuild the client's chart" figures.
  - T5 ran −35% (single-subject harness).
  - T6 ran −18%.
- **C-7 (new) · pos recap shape:** the first pos recap cost ≈576k. Its spine is now K54 (K40 + K34 + K53 + CM-1 + OZ + XO). The next pos recap should bid T0 −40k (no spine discovery) and T1 −10k.
- **C-8 (new) · Look at every figure:** the one render-QA pass caught a content error (Q-8, a floored percentile read as a rank), not only layout. Keep render QA priced at ~12k plus a 5k fix loop.
- **C-9 (new) · An opponent name index pays for itself:** the HP family's opponent scans are the slowest step in every recap with a client `nphl` frame (`02`/`07` §2).

## 5 · What this product makes possible next (the marketing half)
- **A pos recap line for the whole roster.** K54 is subject-agnostic except for constants. Bohm, Stott, Marsh and the rest get the same seven chapters in one constants change, and CX-1 generalizes to any position via `fielder_N`.
- **A chase-cost board.** CC-1 over every 2026 Phillies hitter ranks who gives away the most runs chasing, and against which pitch × hand.
- **Outfield proxy board.** XO-2 for every Phillies OF season since 2015 (the CF context is already computed), with Statcast OAA carried in beside it.
- **TR-1 as the house answer to "he's been better since…".** Pre-register the bars, then read the verdict. It is reusable for any in-season turn claim.

## 6 · Ledger
Patch: `uc_ledger_AI_PATCH_uc-pos-019-crawford-2026-recap.md` (folder copy + MLB root). Next available after this UC: **UC #55 / dp_uc55** (pps next `uc-pps-038` · pos next `uc-pos-020`).
