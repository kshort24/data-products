# 05 — Quality & Certification

**Department:** Quality · **Agents:** `data-quality-engineer` · `certification-agent`
**Use Case:** `uc-pps-026-cortes-acquisition-001` · **Build:** `dp_uc36` · **Date:** 2026-08-20

---

## 1. data-quality-engineer — scorecard summary

Full scorecard: `out/dp_uc36_dq_scorecard.csv` — **29 checks: 28 PASS, 1 WARN, 0 FAIL.**

| Class | Result |
|---|---|
| Completeness (tracking fields, 2021+ tracked pitches) | all ≥ 0.95 PASS |
| Completeness (contact fields, BIP-only scoring) | all ≥ 0.95 PASS |
| Sensor boundary (`arm_angle` absent 2018-19) | PASS — disclosed, never imputed (uc-pos-009 standard); arm-angle trends start at 2021 |
| Validity/Uniqueness (entity, handedness, dedup, game_type, populations) | PASS |
| Accuracy hardenings (O1 xwOBAcon BIP-only · O2 strict zone · O3 EV type=='X') | PASS — locked functions inherited verbatim, hardened variants published |
| Consistency (2026 true gap == 0 rows · 2025 stint boundary disclosed) | PASS |
| LHP orientation (SI/CH pfx_x>0, ST pfx_x<0) | PASS — empirical sign assertion for the mirrored conventions |
| **WARN** | 2025 below full-season floor (8 G / 157 PA) — every 2025 surface prints its PA; standing disclosure, not a defect |

## 2. Independent verification — `dp_uc36_verification.py`

**184/184 PASS** (results receipt: `out/dp_uc36_verification_results.csv`). Design:

- **No import of the build module.** Plain boolean masks, a fresh wOBA implementation over the
  FanGraphs weights, separate season/split recomputes.
- **The UD family is recomputed with the human DPO's ORIGINAL notebook method** (min/max-at-bat
  double merge from the use-case document) against the build's min/max-inning shortcut —
  all 56 season-level UD cells agree exactly. The DPO's analysis reproduces to the digit.
- Every headline claim in the report is a named check: platoon lines (with PA), ED-1 deltas,
  FF velo/IVB by season and by month, mechanics drift, TTO, rest buckets, outing terciles,
  battery numbers, postseason context (including the Freeman grand-slam receipt: W game,
  inning 10, 0-0, FF at 92.2), and the entity/dedup/gap locks.
- **Two check-side corrections during the pass, zero build defects:** (a) a rounding-boundary
  artifact (92.665 at 2dp); (b) the harness's first "behind in the count" mask included 3-2
  counts, which the receipt's count-state definition classifies as two-strike — the harness now
  tests the stated definition. Both dispositions documented here per the uc-pps-019 precedent.
- Cross-method sanity: Statcast `woba_value/woba_denom` career wOBA agrees with the FanGraphs-
  weights implementation within .02 (known scale variance, informational).

## 3. certification-agent — readiness

| Artifact class | Present | Consistent |
|---|---|---|
| Intake gap report + premise register (01) | ✅ | ✅ P1 correction (Keller DFA) propagated to report + manifest |
| KPI specs before build (02, gate order) | ✅ | ✅ UD receipts match specs |
| Glossary/lineage/dictionary/tagging/privacy (03) | ✅ | ✅ no orphan receipt columns |
| Build + receipts (04, 28 CSV + 5 PNG + log) | ✅ | ✅ every figure footnotes its CSV |
| DQ scorecard | ✅ | ✅ 0 FAIL |
| Independent verification | ✅ | ✅ 184/184 |
| Consumables (report .md/.pdf · dashboard .html) | ✅ | ✅ surfaces round once, from receipts |
| Telemetry (bid-vs-actual ledger) | ✅ | ✅ `telemetry/` |
| Ledger patch + contract doc | ✅ | ✅ |

**Certification readiness: READY** — recommendation to publish (internal scope) rests with the
DPO in 00. No blocking items. Open items carried: O1/O2/O3 repo-wide decisions (inherited,
unchanged), plus one new fast-follow candidate (F1, see 00).
