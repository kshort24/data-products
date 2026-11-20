# 07 · Platform & Marketing
Agents: `data-observability` · `cost-watchdog` · `version-controller` · `token-economist`

## 1 · Tripwires (`data-observability`)
| Tripwire | Rule | Action |
|---|---|---|
| Anchor | house log max game_date > 2026-10-01 | build refuses; v1.1.0 |
| O-26 | Shugart name rows ≠ id rows | build refuses |
| Lineage | `dp_uc64_kernel` or any chain pin drifts | build refuses |
| CW-1 | cumulative endpoint ≠ house wOBA / XW-1 | build refuses (assert in `cumulative_frame`) |
| Harness | any V-check FAIL | `dp_uc66_verification.py` exits 1 |
| 2027 appearance | any 663767 row in a 2027 file | new UC, not a correction |

## 2 · Cost audit (`cost-watchdog`)
Heaviest step: loading 12 seasons of the pitching log twice (build + harness CS-A recount). Acceptable for a one-off; if CS-A is ratified, a cached
`phi_rhp_relief_seasons` parquet would cut both by ~70%. Dashboard 0.64 MB (figure specs + 871-pitch explorer table; plotly.js from CDN, not inlined).
Render cost: 11 kaleido processes (RN-1) ≈ 35 s.

## 3 · Versioning
v1.0.0 published to the repo. Change list in `03` §6 (non-breaking text correction + DQ-17 before publish).

## 4 · Marketing line (for the LinkedIn post, if used)
The analyst asked the team of agents to pick the comparison set and fix the charts. It picked righty relievers and said why, wrote six visual rules
before drawing anything, and graded twelve sentences of the analyst's own notes — eight held, three held in part, and one ("he backed off the sweeper
to righties") turned out to be a change against lefties.

## 5 · Bid vs actual (`token-economist`)
Counter = session context consumed, estimated from the turn log (no live counter is exposed). Clock: RFP 13:59 ET → last receipt ≈14:42 ET (≈43 min).
| Mark | When (ET) | Evidence | Cumulative tokens (est.) |
|---|---|---|---|
| C1 | 14:08 | recon of both planes, 3 prior recaps' figures viewed, skills, kernel chain, env workaround (RN-3), carry-ins (web) | ≈ 110k |
| C2 | 14:13 | BID + acceptance filed | ≈ 125k |
| C3 | 14:19 | kernel, T1 build, HP grades (first compute after bars) | ≈ 165k |
| C4 | 14:24 | 11 figures, 2 eyeball-QA rounds (≈20 image reads), V1–V7 11/11 | ≈ 245k |
| C5 | 14:27 | report + PDF (11 pp), dashboard, harness 34/34 (2 harness fixes, 1 report correction) | ≈ 285k |
| C6 | 14:42 | `00`–`07`, README, contract, ledger patch, copies, reply | **≈ 325k** |

| Phase | Bid tokens | Bid min | Actual (est.) | Actual min |
|---|---|---|---|---|
| T0 | 120k | 14 | ≈ 125k | 14 |
| T1 | 70k | 10 | ≈ 40k | 6 |
| T2 | 75k | 14 | ≈ 80k | 5 |
| T3 | 35k | 6 | ≈ 20k | 2 |
| T4 | 30k | 5 | ≈ 10k | 1 |
| T5 | 25k | 5 | ≈ 15k | 2 |
| T6 | 35k | 6 | ≈ 25k | 11 |
| S-1 | 20k | 4 | ≈ 10k | (in T1/T2) |
| **Total** | **≈410k** | **≈64 min** | **≈325k** | **≈43 min** |

**Read:** under bid on both axes. T2 ran at bid on tokens because eyeball QA is image-heavy (the right place to spend, given the RFP's visual
complaint) but fast on the clock. T6 overran its minutes: receipts were generated from CSVs on the device (05 tables) rather than hand-typed, and the
stale-commit issue (RN-4) cost two extra verify cycles. **Calibration for the next pitcher recap:** ≈1.2× UC63's actual (≈320k / ≈45 min) with this
figure family reused; the VZ rules and CS-A make the next one cheaper if ratified.
