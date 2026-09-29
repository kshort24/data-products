# 05 · Quality & Certification: `uc-pos-018`

Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard: 15 PASS / 2 WARN / 0 FAIL (`out/dp_uc50_dq_scorecard.csv`)

| Rule | Check | Result | Detail |
|---|---|---|---|
| DQ-01 | Anchor = Game 162 | PASS | 2026-09-27 |
| DQ-02 | No duplicate PITCH_KEY after precedence dedup | PASS | 378,334 → 360,327 |
| DQ-03 | Entity lock: lineup id → modal Phillies-log name | PASS | 9 / 9 |
| DQ-04 | 519242 is Sale in pitcher-keyed files | PASS | |
| DQ-05 | Sale throws L on every row | PASS | |
| DQ-06 | Rates regular season only | PASS | |
| DQ-07 | Postseason / spring PA vs Sale disclosed | PASS | 0 / 0 |
| DQ-08 | Sale 2026 BIP launch_speed ≥ 99% complete | PASS | 100% |
| DQ-09 | Lineup 2026 BIP hc_x ≥ 99% complete | PASS | 99.90% |
| DQ-10 | plate_x present for HL-1 | PASS | 99.70% |
| DQ-11 | XW-1 fallbacks disclosed | PASS | 0 |
| DQ-12 | Sale 2025 coverage | **WARN (designed)** | partial; nothing published depends on it |
| DQ-13 | De La Cruz pre-2026 coverage | **WARN (designed)** | `bdlc.parquet` ends 2025-04-16 |
| DQ-14 | FL-1 cells flagged, not silently suppressed | PASS | 7 cells below 25 BIP, asterisked, never quoted |
| DQ-15 | Parent kernels hash-pinned | PASS | 4 / 4 |
| DQ-16 | Minor-league tiers excluded | PASS | |
| DQ-17 | Lineup aggregate PA = Σ hitter PA vs Sale | PASS | 163 |

## 2 · Brand & render QA (C-6)

13 PNGs reviewed headlessly before shipping. Palette: Phillies Red `#E81828`, Navy `#002D72`, Blue `#284898` (LHB), Cream `#F3E5AB`, Gray `#8C8C8C`; pitch colours from `dp_uc44` PITCH_COLORS (slider darkened to `#C9B800` for contrast on white). Font: Liberation Sans. Every card footers its UC, build and receipt path. Three defects caught and fixed (see `02` §5).

## 3 · Verification harness: 372 / 372 (`dp_uc50_verification.py`)

**Independent code path.** The harness imports no kernel. It reads the parquet itself, dedups with its own precedence, maps events to FanGraphs weights itself, re-derives hit coordinates and the 4.7-slope classifier from scratch, and compares to the receipts.

| Family | Checks | What it can catch |
|---|---|---|
| A · source & identity | 12 | Wrong rows in the frame, id drift, dedup leaks, anchor drift |
| B · head-to-head vs Sale | 66 | Any error in the nine H2H lines and the lineup aggregate |
| C · 2026 vs LHP cards + LR-1 | 75 | Card tiles; Harper's rank, population and second-worst |
| D · Sale 2026 | 30 | Usage, velocity, whiff by pitch; TTO; usage by side |
| E · directional / HL-1 | 81 | Thirds, pull and oppo rates recomputed with an independent classifier |
| F · prose ↔ receipts | 101 | Every 3-decimal figure and every percent in every lede traced to a receipt; slash lines and PA in the Sale lines |
| G · governance conduct | 7 | Carry-ins labelled, no computed "cleared the bases", THIN printed, HP rows kept, 0 DQ FAIL |

## 4 · What the harness caught (first run 348 / 374)

| First-run failure | Cause | Disposition |
|---|---|---|
| PA off by 1–3 for seven hitters; Sale PA 646 vs 650 | Harness used `woba_denom > 0` as PA. House PA = event present, not `pickoff_1b` (includes IBB, sac bunts, and a few PA-ending rows whose `woba_denom` is null in the source, e.g. one Turner single and two Stott outs vs LHP in 2026) | Harness re-implements the **house** PA definition from its spec. Null `woba_denom` on real PAs noted as a source quirk |
| wOBA off by up to .029 | Savant `woba_value` credits reached-on-error | **MV-1**: harness recomputes house wOBA from FanGraphs weights (passes to .0015); Savant gap receipted |
| Hard-hit off by ≤ 0.5 pp | My comparison on a nullable Float dropped the untracked BIP | Harness now reproduces house O-8 behaviour; the tracked-only rate is receipted |
| Harper LR-1 second-worst .538 vs .478 | The harness hard-coded the client-frame value | Now compares to the governed receipt (.478, Kershaw) |
| Turner oppo rate | Harness oppo classifier did not exclude pulls | Fixed (select-order semantics, as in `dp_uc46`) |
| Stott slash line "missing" from card | The card deliberately prints "4 PA, all 2025 (THIN)" instead of a slash | Check narrowed to PA for THIN lines |

None of the first-run failures was a defect in a published number. Two were definitional (house PA, house wOBA), now written into `03` §2 so the next harness starts from them.

## 5 · Certification readiness (`certification-agent`)

| Artifact | Present | Consistent |
|---|---|---|
| Use case + gaps (`01`) | ✅ | ✅ |
| Source profile + coverage | ✅ | ✅ |
| Glossary deltas | ✅ | ✅ |
| KPI specs before code (`03` §2) | ✅ | ✅ |
| Lineage (`03` §3) | ✅ | ✅ |
| DQ scorecard | ✅ 0 FAIL | ✅ |
| Independent verification | ✅ 372/372 | ✅ |
| HP reconciliation | ✅ 12 rows | ✅ |
| Privacy review | ✅ Internal | ✅ |
| Version manifest | ✅ v1.0.0 | ✅ |

**Verdict: READY-CONDITIONAL** (conditions C1–C5 in `00` §8).
