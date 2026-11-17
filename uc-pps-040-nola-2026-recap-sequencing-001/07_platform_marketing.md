# 07 · Platform & Marketing
Agents: `data-observability` · `cost-watchdog` · `version-controller` · `token-economist`

## 1 · Tripwires (`data-observability`)
| Tripwire | Rule | Action |
|---|---|---|
| Anchor | house log max game_date > 2026-10-01 | build refuses; v1.1.0 (2027 refresh) |
| O-26 / Hoffman | 605400 name rows ≠ id rows; 'Nola, Aaron' maps to > 1 pitcher id | build refuses |
| Lineage | any of 12 pins drift | build refuses |
| Baseline join | any window without a baseline | DQ FAIL (BLOCK) |
| Lift centering | mean k=2 lift beyond ±0.5 runs/100 | WARN (baseline drift) |
| 2027 watch | KC-KC vs RHB lift, 2027 alone n ≥ 30 | re-run SQ-5 with E3 = 2026–27 |

## 2 · Cost audit (`cost-watchdog`)
Build ≈ 28 s; harness ≈ 60 s (plain-Python PA loops, deliberately a different path). The bootstrap is cheap (PA-level sums); the 500-rep SQ-6
permutation ≈ 2 s per scope. Dashboard is 1.1 MB, ≈ 0.6 MB of it the embedded receipts for the explorer (could ship as a sidecar JSON).
Heaviest repeat cost is re-reading 12 parquet years in three scripts; a cached `nola_regular` parquet would save ≈ 15 s per run if the engine is reused.

## 3 · Versioning (`version-controller`)
v1.0.0 published to the repo; Artifact "Aaron Nola 2026" v1. Breaking-change candidates (none shipped): any change to SQ-5 bars, SHRINK_M, RANK_MIN_N,
PC-1 LSA set, or PT-H map. Non-breaking additions this release: SQ-5d, G7 scope, `truncated_pa`, REC-1 rows (`03` §2).

## 4 · Marketing line (if used)
The client asked a question nobody in the shop had answered: which of Aaron Nola's pitch sequences actually prevent runs? The team of agents built
the engine to answer it as a counterfactual, scoring each pitch against itself in the same count. It put error bars on every sequence and told the client how many would look good by chance. The answer: he finishes with the curve, his young-era book still works as a book, and the 2026 damage was the fastballs, not the order.

## 5 · Bid vs actual (`token-economist`)
Counter = session context consumed, estimated from the turn log (no live counter in this session). Clock: RFP 22:33 ET → last receipt ≈23:35 ET (≈62 min).
| Mark | When (ET) | Evidence | Cumulative tokens (est.) |
|---|---|---|---|
| C1 | 22:41 | recon of both planes, 2 skills, 6 prior Nola products, env install (RN-0), sequence-length probe | ≈ 75k |
| C2 | 22:48 | DPO ruling round (Q-A/B/C), carry-ins (web), BID + acceptance | ≈ 95k |
| C3 | 23:00 | kernel + build (3 fix cycles: Hoffman guard, nullable dtype, REC-1 dispositions), first read of results | ≈ 140k |
| C4 | 23:08 | figures (RN-1/RN-2 renderer workarounds), two eyeball-QA rounds (10 PNG reads) | ≈ 205k |
| C5 | 23:16 | report + PDF (12 pp, one page-sheet read), fact-check corrections, dashboard + headless test | ≈ 250k |
| C6 | 23:35 | harness 43/43, `00`–`07`, README, contract, ledger patch, package copy, Artifact | ≈ 300k |

| | Bid | Actual (est.) | Variance |
|---|---|---|---|
| Tokens | ≈ 545k | ≈ 300k | −45% |
| Minutes | ≈ 68 | ≈ 62 | −9% |

**Why under on tokens:** the inherited kernel did what the bid said it would (no KPI re-derivation), and the SQ family vectorized cleanly (build 28 s).
**Where it overran inside phases:** render-environment failures (RN-0..RN-2) and image QA (10 figure reads + PDF sheets) cost ≈ 60k that the bid did
not price; future bids on the device VM should carry a ≈ 10% render-QA line. **Calibration for the next sequencing UC:** ≈ 0.6× this bid when the
engine is reused as-is.
