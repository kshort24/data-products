# 07 · Platform & Marketing
**version-controller · privacy-watchdog · data-observability · cost-watchdog · token-economist**
`uc-pos-025-harper-2026-recap-001` · UC #61 · `dp_uc61` v1.0.0

## 1 · Version (version-controller)
- **`dp_uc61` v1.0.0**, first release. Additive: no inherited file edited; K58, `cumulative_metric`, `recap_viz`, dp_uc22 are pinned and unchanged.
- **Non-breaking proposals (DPO acknowledgement):** CM-2 into `cumulative_metric` v1.1; the parameterized `load_career` to replace K58's subject-bound one; DH-2 as an SD-2 registry entry.

## 2 · Privacy (privacy-watchdog)
Public-figure performance data and public reporting only. No injury or medical claim (V18). Pitcher names are not in the kit. Clear for external publish once the DPO approves.

## 3 · Observability: tripwires
| Tripwire | Action |
|---|---|
| House log passes the 2026-10-01 anchor | build refuses; re-pin |
| Any pinned file changes | lineage fails closed; re-run harness |
| `harper.parquet` changes | ENT-1 / V05 re-run; Washington endpoints must still match |
| Kit file edited by hand | `manifest.json` sha mismatch → V21 fails |
| Claude Design output prints a number not in `copy_notecard.json` | NC-1 breach: send back |

## 4 · Cost (cost-watchdog)
Full rebuild ≈ 45 s on device. The most expensive step is the 2015–26 house-log load for the CS-1 pool (≈ 8 s). The harness reloads raw parquet per season (≈ 12 s); acceptable for a one-off. Next version: cache the pool to `out/`.

## 5 · Bid vs actual (token-economist)
Counter = session context consumed (estimated from the turn log; this session exposes no live counter). Clock 17:54 ET (RFP) → ≈ 18:22 ET (delivery).
| Mark | When | Cumulative (est.) |
|---|---|---|
| C1 | recon: control plane, data plane, prior UCs, carry-ins | ≈ 70k |
| C2 | BID, intake (18:05) | ≈ 78k |
| C3 | kernel + T1 build + DQ 14/14 | ≈ 100k |
| C4 | HP + narrative | ≈ 112k |
| C5 | F1–F3 + 2 render-QA rounds + card | ≈ 140k |
| C6 | kit + brief | ≈ 150k |
| C7 | harness 25/25 | ≈ 160k |
| C8 | `00`–`07`, README, contract, ledger patch, copies | **≈ 183k** |

| Phase | Bid | Actual (est.) | Δ |
|---|---|---|---|
| T0 + BID | 110k / 12 min | 78k / 11 min | −29% |
| T1 | 70k / 10 | 22k / 3 | −69% |
| T2 | 90k / 12 | 28k / 5 | −69% |
| T3 | 30k / 5 | 12k / 2 | −60% |
| T4 | 30k / 5 | 10k / 1 | −67% |
| T5 | 30k / 5 | 10k / 2 | −67% |
| T6 | 50k / 8 | 23k / 4 | −54% |
| **Total** | **≈410k / 57 min** | **≈183k / ≈28 min** | **−55% tokens · −51% time** |

**Calibration:**
- Second straight recap ≥ 50% under bid (UC60 −50%). The bid's "new subject" premium was too high: the K60 chain absorbed the subject change with one parameterized loader.
- **Where the bid was right:** T0. Reading two planes and checking the premise against public sources costs what it costs.
- **Rule for the next hitter recap with an opponent file:** bid T1–T2 at ≈ 50k combined and T3–T5 at ≈ 30k combined; keep T0 at ≈ 80k.

## 6 · Marketing line
> **Bryce Harper's 2026, closed out by a team of agents, in pieces built for a designer.** The agentified organization reconciled his line to MLB.com before writing a word (693 PA, .269/.380/.485, all 162 games), then graded the public story on bars set in advance: the approach held, the thump faded, and lefties, not luck, were the leak. It shipped a notecard kit, not a poster. Every number Claude Design will print is registered to its source and re-checked by an independent harness, so the card can be restyled and animated without one number drifting.
