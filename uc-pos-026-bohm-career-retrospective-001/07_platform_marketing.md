# 07 · Platform & Marketing
**version-controller · privacy-watchdog · data-observability · cost-watchdog · token-economist**
`uc-pos-026-bohm-career-retrospective-001` · UC #67 · `dp_uc67` v1.0.0

## 1 · Version (`version-controller`)
- **`dp_uc67` v1.0.0**, first release. Additive: no inherited file edited; the K61 chain, K48, K62 and the parent K37 are pinned and unchanged.
- **Breaking if changed:** PR-1 bars, GW-1 definition, G-LD population/bar, RS-1 threshold. The house-wide TP-1 fix (E-2) is breaking for every 2024–26 governed line and needs its own notice.

## 2 · Privacy (`privacy-watchdog`)
Public-figure performance data plus public reporting (salary, free agency). No injury or medical inference (harness F). Internal: CLEAR. External: after DPO review of C5.

## 3 · Observability: tripwires (`data-observability`)
| Tripwire | Action |
|---|---|
| A pinned file changes (4 frozen + 23) | `assert_lineage()` fails closed; re-run harness |
| House log passes the 2026-10-01 anchor | `load_house` refuses; re-pin for 2027 |
| K57 `NON_PA` gains `truncated_pa` (E-2 lands) | TP-1 becomes a no-op; harness A must still pass; v1.0.1 |
| Bohm appears in a 2027 MLB log with any club | out of scope for this UC (Phillies career closed); a new UC |
| uc-pos-013 errata (E-3) published | re-run REC-2 / HP-09; no number here changes |
| GW-1 ratified with a different population | refit ranks = correction, not breaking |

## 4 · Cost (`cost-watchdog`)
Full rebuild ≈ 75 s on the laptop VM (house log load ≈ 3 s; PA table for every Phillies batter 2015–26 ≈ 20 s; kaleido ≈ 10 s for 8 figures; harness raw read ≈ 15 s). Storage: 43 receipts ≈ 3 MB. **Session waste found:** two 4-panel figure re-renders for one plotly.js axis bug (F1) cost ≈ 6k tokens of image context; rule: for single-axis season charts set `categoryarray` up front (RQ-3).

## 5 · Bid vs actual (`token-economist`)
Counter = session context consumed, estimated from the turn log (this session exposes no live counter). Clock from the device's file stamps: RFP 13:24 ET → last receipt 13:53 ET.
| Mark | When (ET) | Evidence | Cumulative tokens (est.) |
|---|---|---|---|
| C1 | 13:29 | two-plane recon (CLAUDE.md ×2, house-format and spray skills, K61 chain probe, UC62 trail, uc-pos-013), env, carry-ins | ≈ 80k |
| C2 | 13:30 | BID + intake filed (`BID_…` 13:30:34) | ≈ 88k |
| C3 | 13:32–13:38 | kernel (pins frozen 13:32:24), T1 build, REC-1 first FAIL, HP grades | ≈ 125k |
| C4 | 13:38–13:42 | F1–F8, two render-QA rounds (11 image reads) | ≈ 165k |
| C5 | 13:42–13:45 | narrative, report, PDF (7 pp), dashboard, headless QA | ≈ 195k |
| C6 | 13:45–13:49 | harness 45/51 → **TP-1 found** → fix, full rebuild, 51/51 | ≈ 220k |
| C7 | 13:49–13:53 | `00`–`07`, README, contract, ledger patch, copies, reply | **≈ 250k** |

| Phase | Bid | Actual (est.) | Δ |
|---|---|---|---|
| T0 recon + BID + `01` | 85k / 12 min | 88k / 6 min | +4% / −50% |
| T1 kernel + build + HP | 55k / 10 | 37k / 6 | −33% / −40% |
| T2 figures + audit + QA | 50k / 10 | 40k / 4 | −20% / −60% |
| T3 dashboard | 30k / 7 | 15k / 2 | −50% / −71% |
| T4 report + PDF | 20k / 5 | 15k / 1 | −25% / −80% |
| T5 harness + DQ + certification | 20k / 5 | 12k / 2 | −40% / −60% |
| D defect discovery (TP-1, REC-1, leaderboard PA) | 10k / 3 | 13k / 2 | +30% / −33% |
| T6 `02`–`07`, README, contract, ledger | 40k / 8 | 30k / 4 | −25% / −50% |
| **Total** | **≈ 310k / 60 min** | **≈ 250k / ≈ 29 min** | **≈ −19% tokens · −52% time** |

**Calibration:**
- Fourth straight recap under bid on tokens (UC60 −50%, UC61 −55%, UC62 −33%, UC67 ≈ −19%). The margin is narrowing because two-plane recon is a fixed cost (T0 came in at bid) and defect discovery (D) ran over: the harness found a house-wide defect and our own misdiagnosis, and both had to be fixed and re-run end to end.
- **Where the bid was right:** T0 and D. Read the planes, then expect the harness to find something.
- **Where it was wrong:** T3/T4. With a carried shell and one narrative module, the dashboard and report are assembly, not authorship.
- **Rule for the next hitter career recap with PDF + dashboard:** T0 85k · T1 40k · T2 40k · T3 15k · T4 15k · T5 15k · D 15k · T6 30k ≈ **255k / 40 min**.

**Competitive position, restated with actuals:** what a kernel-less shop would have shipped is now concrete. Its 2026 line would be .247/.313/.381 against a public .249/.315/.383, unless it happened to exclude `truncated_pa`. It would carry uc-pos-013's postseason-contaminated career table forward. Its "game-winning RBI" would have no population to rank against. And it would have no way to say no to its own client's spray-chart angle.

## 6 · Corrections in this run
- **REC-1 misdiagnosis.** T1 attributed the .002 gap to a one-hit official-scorer change and restated the rule (+1 hit) to pass. The harness found the true cause (TP-1). The restatement is withdrawn; REC-1 runs on its original exact rule and passes.
- **HP-03 regrade.** NOT CONFIRMED before TP-1, PARTLY after. Both shown (C7).
- **BID competitive claim** about the client's pitch-grain cell: withdrawn (HP-01 63 = 63).
- **BID filing stamp** first typed 13:36; corrected to the device stamp (13:30:34) before any computation.

## 7 · Marketing line
> **The client asked for a spray chart if the line drives were the story. The organization filed the rule first, and the rule said no.** Alec Bohm's Phillies career, closed out on governed numbers: an out-of-sample check of our own August verdict (the contact held, the results did not), 63 deciding runs ranked against every Phillies win since 2015, a RISP record that is the best of his era and honestly not a skill, and a house-wide counting defect found by a harness that refuses to share the build's code.
