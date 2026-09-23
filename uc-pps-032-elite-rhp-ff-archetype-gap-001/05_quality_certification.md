# 05 · Quality & Certification — `uc-pps-032`

Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (executed — `out/dp_uc47_dq_scorecard.csv`)

| Rule | Dimension | Rule (grain declared) | Result | Observed |
|---|---|---|---|---|
| DQ-01 | uniqueness | no duplicate `PITCH_KEY` in the union (pitch) | PASS | 0 |
| DQ-02 | validity | no MiLB rows survive the level gate (pitch) | PASS | 0 |
| DQ-03 | validity | regular season only (pitch) | PASS | R |
| DQ-04 | consistency | each cohort id present and display-locked (pitcher) | PASS | 6/6 |
| DQ-05 | accuracy | NR-1 tier-2 agreement ≥ 97% (pitcher) | PASS | 0.979 on 242 |
| DQ-06 | completeness | unresolved names in the population (pitcher-season) | **WARN** | 5 |
| DQ-07 | completeness | velo/pfx_z/spin jointly non-null ≥ 99% (tracked pitch) | PASS | 0.9976 |
| DQ-08 | completeness | `delta_run_exp` non-null (pitch) | PASS | 1.0 |
| DQ-09 | validity | xwOBA only on PA-ending rows (pitch — D-1 grain lesson) | PASS | 0 violations |
| DQ-10 | validity | RHP arm side negative `pfx_x` (asserted) | PASS | median −0.64 |
| DQ-11 | consistency | population ≥ 25 (SG-2 floor never triggers) | PASS | 405 |
| DQ-12 | distribution | normality per metric (Shapiro) | **WARN** | ride, RV/100 |
| DQ-13 | distribution | SG-3 skew flag fires on no member | PASS | 0 |
| DQ-14 | comparability | frame is bounded, not MLB-wide (**permanent**) | **WARN** | 139 of 405 PARTIAL |
| DQ-15 | comparability | velo/spin drift-adjusted to 2026 | PASS | velo, spin adjusted |
| DQ-16 | accuracy | staff FF volume from Phillies-log rows only | PASS | 416 non-PHI FF excluded |
| DQ-17 | timeliness | Phillies log current through the anchor | PASS | 2026-09-20 |
| DQ-18 | completeness | McFarlane graded THIN (50 ≤ n < 100) | PASS | 94 |
| DQ-19 | validity | parent kernel sha256 = pinned uc-pps-030 hash | PASS | a2c119096db2 |

**16 PASS · 3 WARN · 0 FAIL.** All three WARNs are designed-in and disclosed in the report's warning box and §7.

## 2 · Brand compliance (host MCP: `brand-center-mcp`)

`validate_brand_compliance` run on all 7 figures × 5 checks (color palette, plotly conventions, voice, title
factual, governance tags): **35 / 35 pass.** `hover_fields_complete` is recorded **n/a** — its required sets are
for pitch-level and batted-ball charts; every figure here is aggregate.

Two things the compliance pass surfaced, not hid:
- **First run: 11 fails.** All 7 "plotly conventions" fails were the validator's key precedence (BC-1, `03` §4);
  4 "title factual" fails were real — titles without a subject–metric–year qualifier. Titles were rewritten to
  brand form ("Zack Wheeler — Four-Seam Fastball Velocity by Year, 2020–2026").
- **The client's own title fails the brand check.** "Zack Wheeler Four-Seam Fastball Velocity by Year" (his
  notebook) lacks a qualifier; and his `plotly_dark` template fails `plotly_conventions_met`. The brand center
  and the notebook disagree — escalated (00 E-5), not silently resolved.

Palette: cohort colors validated with the `dataviz` validator — **light mode all 6 checks pass**; dark mode
passes with one contrast WARN (#2F5DA8 at 2.7:1), relieved by direct labels and table views
(`out/dp_uc47_palette_validation.txt`).

## 3 · Verification harness — **241 / 241 PASS**

| Family | What it checks | Result |
|---|---|---|
| A · kernel fixtures | SG-1 grades on a hand-built population (mean→50, +1 SD→60, clip, sign flip, NaN, n<5, half-up rounding); SG-6 on synthetic drift; SG-7 shrink at n = k; AF-3/5/6 on toy frames | 22 / 22 |
| B · universe invariants | keys, level gate, game type, row accounting closes, receipt = rebuild, keying of named files, independent dedup path, population count via plain groupby | 11 / 11 |
| C · independent recompute | 5 cohort seasons × 7 metrics straight from parquet with plain pandas (not the kernel) + the inherited `whiff_rate` cross-check; staff total 4,201; Bowlan 467; Misiorowski's single start | 41 / 41 |
| D · surface consistency | payload = receipts; slider at w = 0.5 reproduces `efc_score`; all five weight ranks reproduce; dashboard offline; figure JSON = receipt; CB-1 floors hold | 19 / 19 |
| E · governance | DQ 0 FAIL; brand 35/35; palette; every report figure exists; entity locks are ids; all 14 package files present | 28 / 28 |
| F · narrative-to-receipt | **120** numbers the report prose asserts, each re-derived from a receipt and required to appear, formatted, in the report | 120 / 120 |

## 4 · What the harness caught

First full run: **223 / 227** (before the package-manifest checks were added). Three of the four failures were
harness bugs (a random "flat" series that wasn't flat at seed 7; pandas reading the string `n/a` as NaN, which
failed two brand checks). **One was real:**

1. **Family F caught a prose error.** The report said rank-twin grades agree on "79–92%" of pitcher-seasons. The
   receipt minimum is 0.795, which formats as **80%**. The sentence had been "corrected" by hand from 80 to 79
   during drafting; the harness put it back. Every receipt was right; only the prose was wrong — the
   uc-pps-030 lesson, again.

Separately, the **brand-center compliance pass** in the figure build caught 11 fails (§2) before a single figure
shipped, and a second prose claim was caught during drafting by re-reading the receipt rather than the harness: the report
first said every NR-1 name miss was "an accent"; the five that remain after folding are suffixes and initials.
Fixed in the report and `03` §4.

## 5 · Certification

**READY-CONDITIONAL.** Lineage complete (`03` §3), glossary drafted with one rename escalated, DQ 0 FAIL, harness
241/241, acceptance criteria met (capability table `00` §4). Conditions C1–C6 in `00` §8.
