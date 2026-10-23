# 07 · Platform & Marketing
**data-observability · version-controller · cost-watchdog · token-economist · communications-agent**

## 1 · Tripwires (v1.1.0 triggers)
| # | Tripwire | Action |
|---|---|---|
| T-1 | Final 2026 OAA/DRS at 3B published (full sample) | Re-read HP-12 and C1 wording; IO-1 3B stays a proxy |
| T-2 | First 2027 Stott PA in `phils_2027.parquet` | v1.1.0: rerun ER-1 on 2027 to date; the anchor guard refuses a silent rerun |
| T-3 | Statcast or the house changes the `attack_direction` sign or adds bat path for 2024 | Re-run K40a conventions; re-check F6 and HP-10 |
| T-4 | O-16 (tilt drift) resolved as calibration | Allow year-over-year tilt in §5 |
| T-5 | Request to share beyond staff | Privacy re-review (`03` §6); teammate comparisons stay internal |
| T-6 | UC52–55 ledger patches pasted | Confirm #56 next |

## 2 · Cost audit (cost-watchdog)
- **Most expensive step:** the harness (~60 s). It reads 12 seasons of raw parquet itself, by design (independence).
- **ER-1:** 500 permutations × 5 seasons × 2 bases, plus 200-sim power, ≈ 5 s. A vectorized cumulative-sum split is O(n) per permutation.
- **IO-1:** neighbour scans over ~3k opportunities (subject + Phillies context) against ~15–25k pool grounders, ≈ 4 s.
- **Storage:** 82 receipts, ~4 MB. Dashboard 0.32 MB (plotly from CDN). PDF 2.1 MB.
- **Platform cost found:** ENV-4 cost ~3 extra runs (~6k tokens). Versioned staged names avoid it.

## 3 · Bid vs actual (`token-economist`)
Denominator: the session token counter, one turn after the turn-1 data-dictionary reply. The in/out split is estimated from what was written: ~180 KB of Python, ~60 KB of receipts and BID, report text, and dashboard. Minutes run from the first tool call of this turn (19:17 ET) to the last receipt (~20:00 ET).

| Mark | When | Counter | Δ |
|---|---|---|---|
| C0 | session start (turn 1) | 15,000,000 | — |
| C0' | start of this turn, after the schema load | 14,989,939 | 10.1k |
| C3 | BID filed and awarded (end T0) | 14,837,161 | 152.8k |
| C4 | T1 done (kernel, build, smoke, IO-1 A-1/A-2, HP) | 14,746,257 | 90.9k |
| C5 | T2 done (dataviz skill, palette, 10 figures, two render-QA passes) | 14,670,697 | 75.6k |
| C6 | T3+T4 done (narrative, report, PDF, dashboard generator + QA) | 14,611,036 | 59.7k |
| C7 | T5 done (harness 185/185, including 3 harness fixes) | 14,574,936 | 36.1k |
| C7' | Artifact quickstart + publish | 14,560,979 | 14.0k |
| C8 | 00–06 written | 14,538,991 | 22.0k |
| C-final | 07, README, contract, ledger, copies, reply (estimated) | ≈14,515,000 | ≈24k |

| Phase | Bid in+out | Bid min | Actual (counter) | Actual min |
|---|---|---|---|---|
| T0 Intake, recon, carry-ins, env, profile, Rule-1, BID (incl. turn-1 + load) | ~167k | 10 | 162.9k | 10 |
| T1 Kernel + build + HP + EDA | 97k | 11 | 90.9k | 9 |
| T2 Figures + palette + render QA | 73k | 8 | 75.6k | 6 |
| T3 Dashboard + QA + Artifact | 52k | 6 | ≈52k (incl. the 14k Artifact quickstart) | 5 |
| T4 Report + PDF | 20k | 3 | ≈22k | 3 |
| T5 Harness | 27k | 4 | 36.1k | 4 |
| T6 Governance 00–07, README, contract, ledger | 43k | 6 | ≈46k | 7 |
| D Defect discovery | 13k | 2 | (inside T1–T5: A-1/A-2, Q-1, Q-2, Q-3, J-1, ENV-4, ENV-5) | — |
| Contingency | 17k | 2 | — | — |
| **Total** | **~509k (400k in / 109k out)** | **~52** | **≈485k (≈400k in / ≈85k out)** | **≈44** |

**Credits at list ($10/M in, $50/M out):** bid ≈ **$9.45**; actual ≈ **$8.25 (−13%)**. Tokens came in about 5% under bid and minutes about 15% under (44 vs 52). The winning bid was delivered under price and ahead of time, with every published number independently verified.

### Comparison with the season recaps
| UC | Subject | Total (counter) | Minutes | Shape |
|---|---|---|---|---|
| UC51 `uc-pps-035` | Wheeler (SP) | 681k | 46 | PDF + dashboard |
| UC52 `uc-pps-036` | Mayza (RP) | 469k | 35 | 9 pp · 8 ch · 10 fig |
| UC53 `uc-pps-037` | Alvarado (RP) | ≈518k | ≈41 | 10 pp · 7 ch · 10 fig · 2 new |
| UC54 `uc-pos-019` | Crawford (CF, rookie) | ≈576k | ≈46 | 10 pp · 7 ch · 10 fig · 3 new |
| **UC55 `uc-pos-020`** | **Stott (2B/3B, five seasons)** | **≈485k** | **≈44** | **10 pp · 7 ch · 10 fig · 3 new · code in the data plane** |

## 4 · Calibration findings (seventh instrumented recap bid)
- **C-7 held:** the second pos recap cost 91k less than the first (≈485k vs ≈576k). T0 dropped ~126k because the spine (K54) and bat path (K40a) were found and imported in two lines.
- **C-10 (new) · Five seasons cost less than you'd think:** multi-season inputs added ~10k to T1. The new KPIs (ER-1 permutation, IO-1 two-sector neighbour scoring) drove T1, not the season count.
- **C-11 (new) · Price the "subject is the pool" problem at T0:** when the subject is the team's regular at a position, a "teammates at that position" comparator will be thin. IO-1's A-1 should have been the BID definition. Future infield or catcher proxies: pool = both halves of every house game.
- **C-12 (new) · Harness at five seasons:** T5 ran +34%. Inline re-derivation of 5 seasons × 12 metrics plus a naive O(n²) split scan is the cost. Price T5 at 35k for multi-season recaps.
- **C-8 confirmed:** render QA again caught a content error (Q-2), not only layout.

## 5 · What this product makes possible next (the marketing half)
- **ER-1 for the roster:** the notebook cell runs on any batter. A one-page "real eras vs remembered eras" board for every Phillies regular would replace hand-set hot/cold windows across the notebooks.
- **IO-1 infield board:** 2B/3B/SS for every Phillies infielder since 2023, with OAA/DRS carried in beside it. It answers the Stott-or-Bohm-at-third question with a full season once 2027 data lands.
- **Contact-depth tracker:** BP-1 contact depth by month for every hitter. The Stott read suggests the stance change showed up there first.
- **Pre-registered A/B tests (GS-1):** a reusable answer to "what's different when he's going good".

## 6 · Ledger
Patch: `uc_ledger_AI_PATCH_uc-pos-020-stott-2026-recap.md` (folder copy + MLB root). Next available after this UC: **UC #56 / dp_uc56** (pps next `uc-pps-038` · pos next `uc-pos-021`).
