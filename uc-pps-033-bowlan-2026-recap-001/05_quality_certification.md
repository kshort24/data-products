# 05 · Quality & Certification: `uc-pps-033`

Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (executed; `out/dp_uc48_dq_scorecard.csv`)

| Rule | Dimension | Rule (grain) | Result | Observed |
|---|---|---|---|---|
| DQ-01 | uniqueness | no duplicate PITCH_KEY in CF-1 (pitch) | PASS | 0 |
| DQ-02 | consistency | entity lock: every row pitcher == 680742 (pitch) | PASS | [680742] |
| DQ-03 | validity | regular season only (pitch) | PASS | R |
| DQ-04 | timeliness | Phillies log current through the pinned anchor (file) | PASS | 2026-09-23 |
| DQ-05 | validity | p_throws == R (pitch) | PASS | R |
| DQ-06 | consistency | client frame == governed frame on 16 non-shape KPIs (pitcher-season) | PASS | 4 seasons × 16 KPIs |
| DQ-07 | comparability | KP-1 population is Phillies-only (**permanent**) | **WARN** | 198 pitcher-seasons |
| DQ-08 | consistency | inherited uc-pps-032 FF n == this frame's FF n (2025, 2026) | PASS | 243/243, 467/467 |
| DQ-09 | completeness | FF velo/spin/pfx jointly non-null ≥ 99% (pitch) | PASS | 1.0 |
| DQ-10 | completeness | bat_score/post_bat_score non-null (pitch) | PASS | 0 null |
| DQ-11 | comparability | 2017 staff FF ride is a level shift (season) | PASS | 17.3 in vs 14.8–15.9, z = 5.1 |
| DQ-12 | validity | xwOBA only as xwOBAcon (pitch) | PASS | quarantined |
| DQ-13 | validity | RHP arm-side FF pfx_x negative (pitch) | PASS | −0.66 ft |
| DQ-14 | consistency | cross-source duplicates removed by precedence (pitch) | PASS | 19 |
| DQ-15 | validity | D-1 exposure: no whiff subset drops a season (pitcher-season) | PASS | 4/4 |
| DQ-16 | completeness | NULL zone share (pitch) | **WARN** | 0.0006 (1 pitch) |
| DQ-17 | consistency | 2023/2024 flagged context-only (pitcher-season) | **WARN** | 14 / 17 PA |
| DQ-18 | validity | spring rows excluded (pitch) | PASS | 47 |
| DQ-19 | validity | parent kernel sha256 pinned (file) | PASS | a2c119096db2 |

**16 PASS · 3 WARN · 0 FAIL.** All three WARNs are designed in and disclosed in the report's warning box and caveats.

## 2 · Brand compliance (host MCP `brand-center-mcp`, in-process)

11 figures × 5 checks, plus `hover_fields_complete` on the 3 pitch-level scatters: **58 pass / 0 fail**. The other 8 figures record hover as n/a (aggregate charts). In the **first run, 2 checks failed**: the two box-plot figures had been declared `chart_type="pitch"`, so the validator demanded pitch-level hover fields a box cannot carry. They were reclassified as `box` (aggregate). That is a classification fix, not a waiver. Titles passed the subject–metric–year check on the first try, because the uc-pps-032 lesson was applied.

Palette (`out/dp_uc48_palette_validation.txt`): the brand pair red/navy passes CVD separation (ΔE 22.4), the normal-vision floor, and contrast in both themes. It fails the validator's lightness band. That is brand-mandated and disclosed; direct labels and n= annotations carry identity. The house `PITCH_COLORS` (Savant-derived, verbatim) **fail CVD** (FF/SI ΔE 2.0 protan), so every pitch-colored mark in the dashboard also carries a text label or a legend entry, and the drill-through buttons name each pitch.

## 3 · Verification harness: **153 / 153 PASS**

| Family | What it checks | Result |
|---|---|---|
| A · kernel fixtures | runs_created on a toy; PA-1 verdicts (PRESENT/WEAK/CONTRA/ABSENT, both directions) and roll-ups; KP-1 both directions; CS-1 precedence; **B-1 regression**; **O-25 quantization**; RV/100 sign | 13 / 13 |
| B · frame invariants | CF-1 rebuilt without the kernel: rows and rows per season, 19 duplicates, 47 spring rows, anchor, name ↔ id, no duplicate keys | 8 / 8 |
| C · independent recompute | 2025 and 2026 PA, K, BB, BA, wOBA (weights merged by hand), games, RC, FF velo/spin/ride, in-zone FF whiff, FPS; velo Δ; KP-1 n = 198, pct 92, rank 15; staff K rank 2 behind Duran; staff ride #7 of 132; 2017 z; VE-1; multi-inning; 41 entries in the 7th/8th; 15 dirty entries → 13 runs; FF share at 2K | 35 / 35 |
| D · surface consistency | dashboard payload == receipts (recap, ledger, HP, headlines); fig7 bar == receipt; every report PNG/JSON exists; repo dashboard offline; Artifact variant skeleton-free and Google-Fonts-only; < 16 MB; drill densities complete | 11 / 11 |
| E · governance | DQ 0 FAIL; brand 0 fail; parent hash; entity lock is an id; package manifest; carry-in labelling | 6 / 6 |
| F · narrative-to-receipt | **65** numbers the report asserts + **10** ledger strengths + **5** dashboard narrative numbers; each re-derived from a receipt and required to appear, formatted, in the text | 80 / 80 |

## 4 · What the build and the harness caught

The harness's first full run was **143 / 153**. Nine failures were harness bugs: a fixture expected (2 balls, 1 strike) to be "ahead"; four checks compared unrounded rates to `nresults`' published 3-dp values; a DataFrame `.equals` tripped on dtypes; plotly 7 serializes figure arrays as typed base64, so the bar check read the string `'dtype'`; and two "offline" regexes matched URLs inside the inlined plotly.js source. The tenth was the package manifest, which failed correctly because these documents did not exist yet. **No product number was wrong in the harness run.** The product errors were caught earlier, and they were real:

1. **B-1 · `GroupBy.first()` is not "the first row".** The first usage build said 73% of Bowlan's 2026 appearances began with men on base, an implausible number for an eighth-inning setup man. `first()` returns the first *non-null* value per column, so `on_1b` came from any later pitch of the outing. Fixed with a sorted `head(1)`, and pinned by a family-A regression. 2026 clean entries moved from 27% to 75%, and the runs-by-entry-state split changed from 43/16 appearances to 15/44.
2. **A subtitle that overstated.** Figure 11 first said "Steady from April through August." wOBA was steady; the K rate was not (18% in May, 40% in June). Rewritten to say which one held.
3. **Two denominators for one population.** Figure 6 counted 60,053 other Phillies RHP four-seams; the drill-through density counted 60,016 (37 rows lack `pfx`). Both now use the non-null population.
4. **HP-06 framing.** The first draft called the notebook's .269 "an earlier cache". The cache probe showed .269 appears only on a log cut at 2026-07-04 (29 G), which is not a plausible state for a season-end recap. The verdict became "HELD (±.003)" with that evidence.

## 5 · Certification

**READY-CONDITIONAL.** Lineage complete (`03` §3). Glossary drafted, with one naming escalation (E-3). DQ 0 FAIL. Harness 153/153. Acceptance criteria met (capability table `00` §4). Conditions C1–C6 in `00` §8.
