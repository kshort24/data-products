# 05 · Quality & Certification
Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (`out/dp_uc67_dq_scorecard.csv`): **11 PASS / 0 WARN / 0 FAIL**
| Rule | Check | Result |
|---|---|---|
| LIN-1 | Lineage pins hold (K61 chain + K48 + K62 + parent K37) | PASS (26 resolved) |
| ANC-1 | House anchor ≤ 2026-10-01 | PASS (last regular game 2026-09-27) |
| ENT-1 | Every row batter == 664761; 0 duplicate pitch keys | PASS (13,126 rows) |
| REG-1 | Regular season only; non-regular cells receipted | PASS |
| SEA-1 | Seasons = 2020–26 | PASS |
| REC-1 | 2026 log line = CI-1 exactly (BA/OBP/SLG ±.0005, HR, 2B) | PASS after TP-1: .2487/.3148/.3827, 141 H / 567 AB (see §4) |
| AB-1 | Games = CI-1 155 | PASS: 153 with a PA + 2 defensive-only |
| REC-2 | uc-pos-013 windows reproduce on today's log | PASS: 374 + 3 TP-1 rows = 377; 135 = 135; post-break wOBA .374 = .374 |
| SPR-1 | LD spray frame = CR-1 LD count; coordinates present | PASS (723 / 723) |
| GT-1 | No tied finals | PASS (1,842 games) |
| GW-1 | One deciding PA per win | PASS (927 / 927) |

## 2 · Independent harness (`dp_uc67_verification.py` → `out/dp_uc67_verification.csv`): **51 / 51 PASS**
| Family | What it does | Checks |
|---|---|---|
| A | Recomputes PA, hits, HR, 2B by season, 2026 AB/H and LD share from **raw parquet with pandas only** (PA rule written from the spec, not from K57) | 7 |
| B | Window PA and BA for the three 2026 windows; after-the-audit hard-hit from raw BIP | 7 |
| C | Rebuilds game finals and GW-1 from raw: one per win, Bohm 63 by season, rank #2 behind Schwarber, 3,575 PA, BA w/ RISP .314 and #1 of regulars | 5 |
| D | Re-scores PR-1 with an independently written PA-1 rule; checks signatures and directions against the filed BID text; BID precedes the kernel; refits G-LD (corr²); RS-1 = 4/7 | 5 |
| E | 9 published values present in both report and dashboard; every report figure exists; PDF newer than its source; plotly by CDN; V1–V7 clean; same bottom-line call in both | 20 |
| F | No medical language; no GAP markers; RBI only next to a carry-in; CI-1..CI-6 labelled; 9 HP rows; DQ no FAIL; lineage | 7 |

## 3 · Visual standard (`out/dp_uc67_visual_audit.csv`)
All 8 figures pass `recap_viz.audit` V1–V7 (N-A where a standard does not apply; F3 passes V4 with R², n and above/below on every panel). Eyeball QA found and fixed: **F1** collapsed every season onto one category (plotly.js single-axis bug with all-numeric category labels; fixed with an explicit `categoryarray` + range, noted RQ-3); **F2** legend colliding with panel titles (legend off, colour key in the subtitle); **F4** title claimed the line drives landed "the same way" when straightaway share rose 27% → 37% (title corrected); **F1/F6** clipped subtitles; dashboard inspector slash line overlapping its neighbour (grid widened).
**Palette:** house red `#E81828` / navy `#002D72` with grey context (UC62's validator result stands: navy fails the lightness band; compensated by symbol and label encoding).

## 4 · Catches (with "could intake have caught it?")
| Catch | Found by | Intake could have? |
|---|---|---|
| **TP-1: `truncated_pa` counted as PA/AB** | Harness family A (raw PA ≠ governed PA in 4 seasons) | Yes: an `events` value census against `NON_PA` at T0. Now standard |
| **Our REC-1 misdiagnosis.** T1 restated REC-1 as "+1 hit, scoring change" and passed it; the harness proved it wrong | Harness A + certification refusing a restated rule | Yes: a reconciliation gap that hits BA, OBP and SLG together is an AB problem, not a hit problem. Rule: never restate a DQ bar to pass; find the cause |
| HP-03 flips with TP-1 (NOT CONFIRMED → PARTLY) | Re-grade after the fix | n/a; disclosed as C7 |
| Leaderboard PA counted PA keys (3,586) not governed PA (3,575) | Harness C | Yes: one PA definition per UC |
| uc-pos-013 career table carries postseason PA (HP-09) | T0 probe, graded | Yes, and it was |
| BID's pitch-grain claim about the client cell | HP-01 | Yes: reproduce before claiming |
| Harness family D regex: f-string with a backslash | Python syntax error on first run | Harness defect, fixed |

## 5 · Certification (`certification-agent`): **READY-CONDITIONAL**
Present and consistent: lineage (`03` §3), DQ scorecard, glossary entries (`01` §5), KPI specs filed before code (BID 13:30; pins frozen 13:32), data model (`02`), acceptance criteria (BID scope), harness 51/51, visual audit 8/8. Conditions C1–C7 in `00` §8. Certification was **withheld** on the first T1 pass because REC-1 passed only on a restated rule.
