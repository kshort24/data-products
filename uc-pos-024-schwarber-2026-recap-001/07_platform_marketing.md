# 07 · Platform & Marketing
**version-controller · privacy-watchdog · data-observability · cost-watchdog · token-economist**
`uc-pos-024-schwarber-2026-recap-001` · UC #60 · `dp_uc60` v1.0.0

## 1 · Version (version-controller)
- **`dp_uc60` v1.0.0**, first release.
- **House assets SD-1/2/3 v1:** additive. Nothing existing imports them yet, and the house selftest stays 11/11.
- **Breaking-by-value proposal (needs DPO acknowledgement):** future kernels read the ASB from SD-2 instead of their own constant. Values are unchanged for 2026, because no games fall in the window.
- **Not done here:** the 13 pitcher redesign items (Tier B; each would be a v1.1 of its pps UC).

## 2 · Privacy (privacy-watchdog)
Public-figure performance data and public reporting only. The back and illness notes quote public team statements; no medical inference is made. Clear for external publish once the DPO approves.

## 3 · Observability: tripwires
| Tripwire | Action |
|---|---|
| House log passes the 2026-10-01 anchor | build refuses; re-pin |
| SD-1/2/3 sha changes | lineage fails closed; re-run harness |
| SD-1 DRAFT entries ratified or changed | re-tag status; pitcher redesign may start |
| New injury reporting with an onset date | add an SD-2 entry; re-run BK-1 on the new window (rule unchanged) |

## 4 · Cost (cost-watchdog)
Full rebuild ≈ 90 s on device. The most expensive step is the per-batter-season pool panel (≈ 12 s). Figures re-read receipts, except F2/F4/F5, which reload the career frame (≈ 6 s each). Next version: cache that frame to `out/`.

## 5 · Bid vs actual (token-economist)
Counter = session tokens-left (context consumed). Clock 20:06 ET (RFP) → ≈ 20:34 ET (delivery).
| Mark | When | Counter | Cumulative |
|---|---|---|---|
| C0 | RFP | 15,000,000 | 0 |
| C1 | recon + 9 web reads + profile | 14,954,980 | 45k |
| C2 | BID, `01`, intake copies | 14,942,724 | 57k |
| C3 | SD-1/2/3 + kernel + T1 build | 14,909,162 | 91k |
| C4 | F1–F8 + Tier 3 audit + render QA (3 rounds) | 14,836,582 | 163k |
| C5 | HP + narrative + report + PDF QA | 14,821,276 | 179k |
| C6 | dashboard + headless QA + season card | 14,800,931 | 199k |
| C7 | harness 28/28 | 14,790,814 | 209k |
| C8 | `02`–`07`, README, contract, ledger patch, copies (est.) | ≈14,760,000 | **≈240k** |

| Phase | Bid | Actual | Δ |
|---|---|---|---|
| T0 + BID | 90k / 9 min | 57k / 8 min | −37% |
| T1 | 101k / 10 | 34k / 4 | −66% |
| T2 | 92k / 10 | 72k / 9 | −22% |
| T3 | 46k / 6 | 16k / 3 | −65% |
| T4 | 49k / 6 | 20k / 3 | −59% |
| T5 | 34k / 4 | 10k / 2 | −71% |
| T6 | 43k / 6 | ≈31k / 6 | −28% |
| **Total** | **≈478k / 54 min** | **≈240k / ≈28 min** | **−50% tokens · −48% time** |

**Calibration:**
- This is the furthest under bid in the UC48–UC60 record, and outside the −28%…+9% band.
- **Two reasons:**
  - UC58 had already built the career loader, DH-1 and HR quality for the same subject two days earlier.
  - The recap shell (K57 panel, PDF and dashboard shells) imports whole.
- **Where the bid was right:** T2 (figures) ran close to bid, because three render-QA rounds were needed (CAT-1, shared box names, title-vs-data audits).
- **Rule for the next same-subject recap:** bid T1 at ≈ 40k and T3–T5 at ≈ 50% of the shell estimate.

## 6 · Marketing line
> **Schwarber's 2026 recap, closed out by a team of agents.** The agents graded the questions the city was asking, "Was it his back? Did he lose his pop? Should we be concerned?", on bars set before any number was computed. Answers: not visible in the log, partly, and not on the evidence, with one real flag in chase. Along the way the agentified organization built the house's first shared recap standard: comparison sets, era definitions and chart helpers that audit every figure against seven visual rules. The pitcher-recap redesign can now start from governed parts instead of notebook constants.
