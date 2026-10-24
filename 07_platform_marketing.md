# 07 · Platform & Marketing
**data-observability · version-controller · cost-watchdog · privacy-watchdog · token-economist**
`uc-pos-022-turner-2026-recap-001` · UC #57 · `dp_uc57` v1.0.0

## 1 · Tripwires (v1.1.0 triggers)
| # | Tripwire | Action |
|---|---|---|
| T-1 | Position decision announced (2B / OF / SS) | Narrative update to ch. 6; CI-2 refresh; no data change |
| T-2 | First 2027 PA in any house file | v1.1.0 re-run; the anchor guard refuses a silent rerun. First-look metrics: fastball IZ swing by hand, tilt peer-netted by month, breaking-ball popup rate |
| T-3 | Single-Swing Pilot Gate 2 closes + PL-1 fixed | Tier B: add the reconstructed swing (2026 Truist Park HR beside one breaking-ball popup) as a dashboard chapter |
| T-4 | Statcast re-calibrates bat-path fields (O-16 resolved either way) | Re-run PB-1/PB-2; if the team-wide tilt drift is a sensor change, C1 tightens |
| T-5 | Request to share outside the front office | privacy-watchdog re-review (internal-only today) |

## 2 · Version
v1.0.0, new product. No breaking change to any inherited kernel; K56/K55/K40a imported unchanged and pinned.

## 3 · Cost audit (cost-watchdog)
Pipeline 31 s end to end (build 10 s, figures ~12 s with kaleido, PDF ~5 s, harness ~4 s). Storage: 63 receipts 3.1 MB; PDF 1.8 MB; dashboard 0.19 MB (plotly from CDN). No waste worth fixing.

## 4 · Privacy (privacy-watchdog)
Named public figure, performance data and publicly reported contract terms only. No quasi-identifiers beyond what MLB publishes. Internal; external publish needs a re-review (T-5).

## 5 · Bid vs actual (token-economist)
**Instrument:** the session token counter (tokens left). This build ran in a **new chat**, as the BID allowed; T0 (100.5k, 9 min) is sunk from the bidding chat.

| Mark | When (ET) | Counter | Δ |
|---|---|---|---|
| C0 | session start | 15,000,000 | — |
| C1 | first tool call (session context load: system prompt + tool roster) | 14,874,128 | 125.9k |
| C2 | re-recon done (BID/00/01, K55, K56, K40a, UC55/56 shells, client cell) | 14,764,792 | 109.3k |
| C3 | T1 done (kernel, build, HP) | 14,698,444 | 66.3k |
| C4 | T2 done (9 figures, two render-QA passes) | 14,647,775 | 50.7k |
| C5 | T3+T4 done (narrative, report, PDF QA, dashboard, Playwright QA, Artifact v1) | 14,623,757 | 24.0k |
| C6 | T5 done (34-check harness, full deterministic rebuild) | 14,615,669 | 8.1k |
| C7 | T6 (02-07, README, contract, ledger patch) + reply | ≈14,588,000 (est.) | ≈28k |

| Phase | Bid tokens | Bid min | Actual tokens | Actual min |
|---|---|---|---|---|
| T0 (sunk, bidding chat) | ~107k | 9 | 100.5k | 9 |
| New-chat surcharge (session load + re-recon) | **35k** | 3 | **235.2k** | 4 |
| T1 Kernel + build + HP + EDA | 85k | 8 | 66.3k | 6 |
| T2 Figures + QA | 73k | 7 | 50.7k | 4 |
| T3 + T4 Dashboard, report, PDF, Artifact | 67k | 9 | 24.0k | 4 |
| T5 Harness | 34k | 4 | 8.1k | 2 |
| T6 Governance | 41k | 6 | ≈28k | ≈6 |
| D + contingency | 29k | 4 | (inside T1-T2: NA-1, CAT-1, F3 label overlap) | — |
| **Total** | **~471k** (436k + 35k new-chat) | **~50** | **≈513k** | **≈35** |

- **Tokens ≈ +9% over** the bid as adjusted for a new chat (+18% over the 436k headline). **Minutes ≈ 30% under.**
- **Credits at list** ($10/M in, $50/M out; in/out split estimated from what was written, ≈60k out this chat): this chat ≈ $6.5 + T0 ≈ $2.0 = **≈ $8.5** against a bid of $8.84 (−4%). Output came in light; input (context re-reads) came in heavy.
- **The miss is entirely the new-chat surcharge:** 235k actual vs 35k bid. The post-recon build (T1-T6, ≈177k) came in **≈ 40% under** its 296k line, because K40a, K56 and the UC55/56 shells were inherited whole.

## 6 · Calibration findings
- **C-15 (new) · A new chat is not a 35k surcharge.** It costs a fixed session load (≈126k here: system prompt plus the tool roster, which this account's connectors make large) plus a re-recon (≈109k: BID, receipts, three kernels, two prior shells). Price "continue in a new chat" at **+230k**, or continue in the bidding chat when its context is not already heavy.
- **C-16 (new) · With a whole-recap shell to inherit (K56 + UC55/56 builders), the post-recon build is ≈175k.** Down from ≈225k (UC56) and ≈322k (UC55).
- **C-13 held:** the work is front-loaded. Reading is now the cost centre, not building.

## 7 · Comparison with the season recaps
| UC | Subject | Total | Minutes | Shape |
|---|---|---|---|---|
| UC54 `uc-pos-019` | Crawford | ≈576k | ≈46 | 10 pp · 7 ch · 10 fig · 3 new |
| UC55 `uc-pos-020` | Stott | ≈485k | ≈44 | 10 pp · 7 ch · 10 fig · 3 new |
| UC56 `uc-pos-021` | Sosa | ≈466k | ≈34 | 8 pp · 8 ch · 9 fig · 2 new |
| **UC57 `uc-pos-022`** | **Turner** | **≈513k (two chats)** | **≈44 (9 + 35)** | **7 pp · 6 ch · 9 fig · 1 new KPI + 2 rules** |
