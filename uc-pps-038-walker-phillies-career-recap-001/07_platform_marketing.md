# 07 · Platform & Marketing
**version-controller · privacy-watchdog · data-observability · cost-watchdog · token-economist**
`uc-pps-038-walker-phillies-career-recap-001` · UC #62 · `dp_uc62` v1.0.0

## 1 · Version (`version-controller`)
- **`dp_uc62` v1.0.0**, first release. Additive: no inherited file edited; the `dp_uc53` chain and `recap_viz` are pinned and unchanged.
- Artifact "Taijuan Walker, Phillie": v1 (20:33 ET), v2 (20:36 ET, correction: BID filing stamp 20:24 → 20:19 ET, see §6). Content otherwise identical.
- **Breaking if changed:** PR-1 bars, KR-1 population, CE-1 basis.

## 2 · Privacy (`privacy-watchdog`)
Public-figure performance data plus public contract reporting. No injury or medical inference (harness F). Internal: CLEAR. External: after DPO review of the cost chapter.

## 3 · Observability: tripwires (`data-observability`)
| Tripwire | Action |
|---|---|
| A pinned file changes (10 pins) | `assert_lineage()` fails closed; re-run harness |
| House log passes the 2026-10-01 anchor | K53 `load_house` refuses; re-pin for 2027 |
| Walker appears in a 2027 MLB log (any club) | v1.1.0: new season row, refit nothing else |
| `walker.parquet` or an opponent file changes | DQ-01/05 + harness A must still pass |
| The KP-1 pool changes (new 2026 data) | KR-1 refit = correction; re-render F1/F2 |

## 4 · Cost (`cost-watchdog`)
Full rebuild ≈ 30 s on the laptop VM (house log load ≈ 5 s, NF-1 client frame ≈ 6 s, harness raw read ≈ 6 s, kaleido ≈ 3 s). Storage: 38 receipts ≈ 1.6 MB. **Session waste found:** one `device_list_dir` on MLB `out/` (≈ 700 entries) cost ≈ 25k tokens of context for a 9-file need. Rule: stage by explicit path or `ls out/dp_ucNN_*`, never list `out/`.

## 5 · Bid vs actual (`token-economist`)
Counter = session context consumed, estimated from the turn log (this session exposes no live counter). Clock from the device's file stamps: RFP 20:14 ET → last receipt 20:39 ET (device clock; ≈ 25 min).
| Mark | When (ET) | Evidence | Cumulative tokens (est.) |
|---|---|---|---|
| C1 | 20:18 | recon of both planes, 6 kernels, skill, carry-ins, env install | ≈ 75k |
| C2 | 20:19 | BID + intake filed | ≈ 82k |
| C3 | 20:24 | kernel, T1 build, HP + DQ (15/0/0) | ≈ 112k |
| C4 | 20:28 | narrative, F1–F9, 2 render-QA rounds (incl. the 25k listing) | ≈ 165k |
| C5 | 20:30 | report + PDF (8 pp), one layout pass | ≈ 177k |
| C6 | 20:32 | harness 47/47 (2 harness fixes) | ≈ 187k |
| C7 | 20:37 | dashboard, headless look, Artifact v1 + v2 | ≈ 205k |
| C8 | 20:39 | `00`–`07`, README, contract, ledger patch, copies, reply | **≈ 240k** |

| Phase | Bid | Actual (est.) | Δ |
|---|---|---|---|
| T0 recon + BID + `01` | 95k / 12 min | 82k / 5 min | −14% / −58% |
| T1 kernel + build + HP | 60k / 10 | 30k / 5 | −50% / −50% |
| T2 figures + audit + QA | 55k / 10 | 53k / 4 | −4% / −60% |
| T3 dashboard + Artifact | 55k / 10 | 18k / 5 | −67% / −50% |
| T4 report + PDF | 25k / 5 | 12k / 2 | −52% / −60% |
| T5 harness + DQ | 30k / 6 | 10k / 2 | −67% / −67% |
| T6 `02`–`07`, README, contract, ledger | 40k / 8 | 35k / 2 (overlapped T3) | −13% / −75% |
| **Total** | **≈ 360k / 61 min** | **≈ 240k / ≈ 25 min** | **−33% tokens · −59% time** |

**Calibration:**
- Third straight recap well under bid (UC60 −50%, UC61 −55%, UC62 −33%). The `dp_uc53` chain absorbed a new subject, a two-club career and a new pool with one parameterized call (CF-2d).
- **Where the bid was right:** T0 and T2. Reading two planes costs what it costs, and render QA spends its budget on images.
- **Where it was wrong:** T3 (the shell pattern makes the dashboard cheap) and T5 (the harness is mostly assertions on receipts).
- **Rule for the next pitcher career recap with PDF + dashboard:** T0 80k · T1 35k · T2 45k · T3 25k · T4 15k · T5 15k · T6 35k ≈ **250k / 40 min**.

**Competitive position, restated with actuals:** the defects a kernel-less shop would ship are now concrete: the client frame's 483 missing pitches (O-26), 18 NLDS pitches in a regular-season row (SRC-1), a 2015 EV "spike" that is a population change (EV-1), and the 4/22 "start" that was bulk relief.

## 6 · Corrections in this run
- The BID and five files first stamped the filing time as 20:24 ET. File stamps show 20:19:18, before the kernel (20:20:40) and the first PR-1 run. Corrected everywhere before delivery; the order of registration and scoring is unchanged.
- A takeaway first carried "the 15-win season" with no carry-in source; removed (harness F now regex-checks it).

## 7 · Marketing line
> **A $72 million question, answered on bars set before the answer.** The agentified organization reconciled Taijuan Walker's Phillies innings to the out (402.2), then scored a pre-registered ledger: the stuff declined, the Mets-era luck went away, and the contract was priced on a gap his strikeouts never explained. Every number in the PDF and the dashboard traces to a receipt and passed a harness that recomputes from raw data without the kernel.
