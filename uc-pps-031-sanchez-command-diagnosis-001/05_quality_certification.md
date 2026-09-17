# 05 · Quality & Certification — `uc-pps-031`

Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (`out/dp_uc45_dq_scorecard.csv`) — 16 PASS · 1 WARN · 0 FAIL

| Rule | Check | Evidence | Status |
|---|---|---|---|
| DQ-1 | entity lock 650911 → one name | Sánchez, Cristopher | PASS |
| DQ-2 | no duplicate pitch keys | 0 dropped | PASS |
| DQ-3 | regular season only | R | PASS |
| DQ-4 | anchor 2026-09-15 | 2026-09-15 | PASS |
| DQ-5 | location completeness ≥ 99.9% | 0.99991 | PASS |
| DQ-6 | `zone` completeness ≥ 99.9% | 0.99991 | PASS |
| DQ-7 | every 2026 appearance is a start | 31/31 | PASS |
| DQ-8 | `plate_x` sign rule | −2.01 / +1.98 | PASS |
| DQ-9 | SZ regions partition located pitches | exact | PASS |
| DQ-10 | edge twin = governed `edge_rate` | ≤ 0.0005 | PASS |
| DQ-11 | 2026 rails constant per batter (O-18) | 1.000 | PASS |
| DQ-12 | geometry vs `zone` disagreement < 6% | 0.0401 | PASS |
| DQ-13 | PN-1 cohort ≥ 10 | 11 (min across bases) | PASS |
| DQ-14 | ZC-1 coverage ≥ 60% (2025) | 0.780 | PASS |
| DQ-15 | 2021-22 swingman flag | 873 pitches | PASS |
| DQ-16 | no rate on a zero denominator | season grain | PASS |
| DQ-17 | `arm_angle` completeness ≥ 90% | 0.777, not used | **WARN** |

## 2 · Known-defect register, exposure in this build (`out/dp_uc45_defect_exposure.csv`)

| Defect | Exposure | Effect on published numbers |
|---|---|---|
| D-1/D-2 `whiff_rate` inner join drops zero-whiff groups | 2 of 135 appearances at game grain | none (no game-grain whiff published) |
| D-7/O-13 null `zone` counted in-zone | 1 pitch (2025) | 2025 in-zone about +0.0003 |
| O-8 untracked BIP counted not-hard-hit | 8 BIP | notebook table hard-hit only |
| O-14 `bbrate` excludes IBB | 0 IBB | none |
| `fpsr` drops groups with no first-pitch ball | 1 appearance at game grain | none |
| `chase_rate` NaN for zero-chase groups | 0 | none |
| D-9 `nresults(['batter'])` | not called | n/a |
| **O-18 (NEW)** 2026 zone rails redefined | league-wide | **controlled** with ZC-1 + PN-1; every 2025→2026 zone statement carries its decomposition |

**O-18 registration.** Statcast `sz_top`/`sz_bot` in the 2026 cache are a constant per batter (ABS height-based
zone). For the same 32 hitters, the top of the zone is a median 0.234 ft lower than in 2025, and lower for 84% of
them. Every geometry and `zone`-attribute KPI shifts at the 2025/2026 boundary; league in-zone .503 → .465.
Tripwire T-3 watches for a mid-season rail change.

## 3 · Verification (`dp_uc45_verification.py`) — **436 / 436 PASS**

| Family | What it proves | Independence | Checks |
|---|---|---|---|
| A | Source & entity integrity, exclusions, IBB = 0, arsenal | pyarrow direct, no kernel | 16 |
| B | Season / half / month / league panels recomputed | numpy re-implementation | 214 |
| C | Geometry via a **different algorithm** (clamp projection); corner and crosswalk counts; SZ-5 shares | independent | 11 |
| D | O-18 audit, ZC-1 re-score, league drift, decomposition identity, PN-1 medians and ranks | independent | 18 |
| E | z / p for every half premise and key splits; verdict logic | closed-form z | 14 |
| F | **Narrative ↔ receipt**: 60 numbers quoted in the report | text match against receipt-formatted values | 60 |
| G | **Parent reproduction**: the client's cell run with `Baseball Functions.ipynb`'s own code | executes notebook cells | 81 |
| H | Byte-identical inheritance, notebook gap (E-2), dashboard hygiene, figures, PDF, DQ | file-level | 22 |

**Family F caught a real error on its first run.** The report said pitches thrown ahead went ".312 → .313". The
receipt value is 0.3115, which formats as **.311**. Both occurrences were corrected. Every receipt-level family
had passed. This is the third UC in which the narrative family caught a prose error the data checks could not
(after `uc-pos-016` V-1 and `uc-pps-030` §3).

**Family H caught a false-positive design flaw in itself.** Its first "Section A byte-identical" check failed
because `barrel_rate` was inserted mid-section. The check was rewritten to prove both halves are identical and in
order, rather than loosened.

## 4 · Method-variance dispositions

- Kernel wOBA (FanGraphs weights / PA) vs Statcast `woba_value` scale: ≈ .01 apart, as dispositioned in `uc-pps-019` §05. The kernel number is governed. The bid-time exploration quoted the Statcast scale (.275 → .309); the report uses the kernel (.263 → .298).
- Geometric in-zone vs Statcast `zone`: 4.0% of pitches disagree. The kernel number is governed; the geometric twin is used only inside ZC-1.

## 5 · Certification (certification-agent) — **READY-CONDITIONAL**

| Artefact | Present | Consistent |
|---|---|---|
| Use-case contract `uc-pps-031-Cristopher Sanchez Command 20260916.md` | ✓ | ✓ |
| BID + reconciliation | ✓ | ✓ (`07` §3) |
| Glossary + KPI specs + crosswalk (`03`) | ✓ | ✓ |
| Lineage (`03` §3) | ✓ | ✓ |
| Data model + joins (`02`) | ✓ | ✓ |
| DQ scorecard | ✓ | 0 FAIL |
| Verification | ✓ | 436/436 |
| Report PDF + dashboard | ✓ | family F + H |
| Ledger patch | ✓ | UC #45 free in all three namespaces |

Conditions C1–C6 as in `00` §8.
