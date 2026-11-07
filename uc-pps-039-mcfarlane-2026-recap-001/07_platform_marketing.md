# 07 · Platform & Marketing
Agents: `data-observability` · `cost-watchdog` · `version-controller` · `token-economist`

## 1 · Tripwires (`data-observability`)
| Tripwire | Rule | Action |
|---|---|---|
| Anchor | house log max game_date > 2026-10-01 | build refuses; v1.1.0 |
| O-26 | McFarlane name rows ≠ id rows | build refuses |
| EN-3 | a FO-1 name not drawn from pitching rows | DQ-16 FAIL |
| Lineage | any of 11 pins drift | build refuses |
| 2027 appearance | any 686934 row in a 2027 file | new UC, not a correction |

## 2 · Cost audit (`cost-watchdog`)
Heaviest step: loading 12 seasons × all roles for FO-1 (~600k rows, 57 columns) twice (build + harness). Acceptable for a one-off; a cached FO-1
pool parquet would cut the harness by ~60% if FO-1 is ratified and reused. Dashboard is 1.1 MB, 0.9 MB of it the 20k-point F5 sample (could be
thinned to 5k for the web view without changing the PDF).

## 3 · Versioning
v1.0.0 published to the repo; Artifact "Alex McFarlane 2026" v1. Breaking-change list in `03` §6.

## 4 · Marketing line (for the LinkedIn post, if used)
The client wrote the story; the team of agents checked every sentence of it against the data before it went on a slide. Eleven claims confirmed,
seven tightened, one corrected, and the one that couldn't be tested says so.

## 5 · Bid vs actual (`token-economist`)
Counter = session context consumed, estimated from the turn log (this session exposes no live counter). Clock: RFP 00:41 ET → last receipt ≈01:17 ET (≈36 min).
| Mark | When (ET) | Evidence | Cumulative tokens (est.) |
|---|---|---|---|
| C1 | 00:49 | recon of both planes, skill, 4 kernels, env install, 5 carry-ins (web) | ≈ 95k |
| C2 | 00:53 | BID + acceptance filed | ≈ 105k |
| C3 | 00:59 | kernel, T1 build, HP, DQ (2 fixes: EN-3, AB-1 status) | ≈ 150k |
| C4 | 01:03 | narrative, 8 figures, 2 render-QA rounds | ≈ 195k |
| C5 | 01:06 | report + PDF (10 pp) | ≈ 210k |
| C6 | 01:09 | dashboard (headless look), slide kit, harness 45/45 (2 harness fixes), Artifact v1 | ≈ 235k |
| C7 | 01:17 | `00`–`07`, README, contract, ledger patch, copies, reply | **≈ 265k** |

| Phase | Bid tokens | Bid min | Actual (est.) | Actual min |
|---|---|---|---|---|
| T0 | 110k | 10 | ≈ 105k | 12 |
| T1 | 60k | 8 | ≈ 45k | 6 |
| T2 | 45k | 6 | ≈ 45k | 4 |
| T3 | 35k | 5 | ≈ 15k | 3 |
| T4 | 45k | 6 | ≈ 20k | 3 |
| T5 | 25k | 4 | ≈ 5k | (in T4) |
| T6 | 40k | 6 | ≈ 30k | 8 |
| S-1 | 25k | 4 | (in T1/T2) | (in T1/T2) |
| **Total** | **≈385k** | **≈49** | **≈265k (−31%)** | **≈36 (−27%)** |

## 6 · Calibration
Under on every build phase; T0 on bid (web carry-in checks are real work). The narrative module paid for itself: report, dashboard and slides were
each ~10–20k because they only format receipts. Next recap with a client narrative: bid ≈ 1.1× UC62 actual (≈ 270k / 35 min), plus 20k per stretch.
