# 05 · Quality & Certification
**dq-rule-definer · data-quality-engineer · certification-agent · brand-guardian**

## 1 · DQ scorecard — 15 PASS / 5 WARN / 0 FAIL (`out/dp_uc55_dq_scorecard.csv`)
| Rule | Status | Detail |
|---|---|---|
| LIN-1 lineage pins | PASS | 14 sha256 pins |
| BP-C K40a conventions | PASS | 12/12 re-proven (O-15 pull-negative, stand-normalised; C2 depth) |
| ENT-1 id lock | PASS | 11,834 pitches 2022-26; one name ↔ one id |
| SRC-4 client frame game types | WARN | 182 non-regular PA in the client frame; excluded from every governed rate |
| DUP-1 pitch key | PASS | 0 duplicates |
| CM-1 endpoint reconcile | PASS | tol 1e-9, every season |
| ER-1 determinism | PASS | seed 55, 500 permutations, params == BID |
| DR-1 spray convention | PASS | LHB pull median `loc_x` +76 ft |
| IO-0 field frame | PASS | 3B −35°, 2B +24° |
| IO-1 coverage 2B | PASS | v4 (A-2), 94.9% pooled 2023-26 |
| IO-1 coverage 3B | PASS | v3, 92.1% |
| IO-1 sign stability | WARN | 2B 2025/2026 stable; **3B 2026 not stable** (published as such) |
| TP-1 truncated PA | WARN | 3 on subject (inherited) |
| SF-1 | PASS | 0 on subject |
| O-8 untracked BIP | WARN | 4 on subject (inherited) |
| BT-0 sensor boundary | PASS | NULL before 2024/2025, never imputed |
| SHIFT-1 pool years | PASS | IO-1 pool 2023-26 |
| A-1/A-2 amendments | WARN | disclosed (`03` §2) |
| CI-0 carry-ins | PASS | text only |
| EDA-1 | PASS | 3 reports |

## 2 · Independent harness — **185 / 185 PASS** (`dp_uc55_verification.py`, `out/dp_uc55_verification_log.csv`)
It reads the raw parquet itself and never imports a kernel. Governed constants are re-typed from K40, with the citation.

| Family | Checks | What it proves |
|---|---|---|
| A pre-registration | 19 | ER-1 parameters and GS-1 bars in the kernel equal the BID text; IO-1 BID tolerances unchanged; A-1/A-2 marked |
| B entity & frame | 7 | anchor; id lock; no duplicates; SRC-4 counts; games |
| C season line | 71 | every season's PA, slash, wOBA (house weights from the CSV), xwOBA atom, BB/K, chase, whiff, HH, barrel, LD recomputed inline; CI-1 reconcile; own ranks; CM-1 endpoint |
| D ER-1 | 20 | career rate; every season's best split point and gain by a naive O(n²) scan; label rule; power monotone; client era rates and hindsight p |
| E GS-1 | 12 | pooled era counts inline (incl. its own spray classifier); two-prop p and PA-1 verdicts re-implemented; call; summer-2026 PRESENT pair |
| F published strings | 18 | 13 report strings re-derived; "oppo fell every season", "pull career high", "worst whiff", "August lowest chase", "best chase year" are true |
| G carry-ins | 5 | no carry-in numerals in code; none in `headlines.json` |
| H IO-1 | 7 | 2B 2026 opportunities, scored count and OAE re-scored by a naive neighbour scan; coverage; sign stability; 3B games |
| I bat path | 7 | contact depth and pull direction 2025/2026 inline; ASB marker; 2025 H1 depth; O-15 sign re-proven inline |
| J figures & brand | 12 | 10 figures, every brand/claim check, PNG+JSON, palette receipt |
| K forms | 4 | PDF ≤10 pages (`pdfinfo`); dashboard CDN-pinned, 10-figure payload; Artifact variant |
| L HP family | 3 | 14 rows; client 2026 PA = governed + non-regular; CL-1 confirmed |

## 3 · Brand and palette (brand-guardian)
- 10/10 figures: claim asserted, Arial, title, subtitle, every colour on the allow-list (`out/dp_uc55_brand_checks.csv`).
- Palette validator (`out/dp_uc55_palette_validation.txt`):
  - The PG-1 trio (direction / pitch group) passes all checks, light and dark.
  - The brand highlight trio (red / navy / gray) passes CVD and normal-vision separation. It flags lightness (navy) and chroma (gray) by design: it is a highlight-vs-context encoding, always direct-labelled, not a categorical palette.

## 4 · Catches, with "could intake have caught it?"
| # | Catch | Caught by | Intake could have? |
|---|---|---|---|
| Q-1 | F9 season axis collapsed to one tick | render QA (looked at every figure, C-8) | No — a rendering issue |
| Q-2 | F7 title overstated ("every pitch group") | render QA + reading the chart against its title | Partly — a claim assertion on the full pattern would have; now added |
| Q-3 | Harness barrel denominators differed by 2 BIP | harness C (3 FAIL → fixed in the harness to the governed O-8 convention) | Yes — O-8 is known; the harness now cites it |
| Q-4 | IO-1 coverage gate failed at 2B (BID pool) | build-time gate | Yes — "Stott *is* the Phillies 2B pool" was knowable at T0; priced into C-11 |
| Q-5 | ENV-4 stale commits | grep-before-run discipline | No — platform behaviour |

## 5 · Certification verdict (certification-agent)
**READY-CONDITIONAL.** All artifacts are present and internally consistent:
- BID, 00–07
- lineage
- DQ (0 FAIL)
- harness 185/185
- glossary entries for three provisional KPIs
- privacy assessment
- version manifest

Conditions C1–C5 are in `00` §6. Publish decision: human DPO.
