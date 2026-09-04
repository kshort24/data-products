# 05 · Quality & Certification — `uc-pos-014-turner-2026-recency-001`

**Department:** Quality · **Agents:** `data-quality-engineer`, `use-case-validator` (re-entry),
`certification-agent`, `version-controller`
**Gate:** no publish without a certification-ready status.

## Headline

| | |
|---|---|
| Independent verification | **711 / 711 PASS** (`dp_uc40_verification.py`, `out/dp_uc40_verification_results.csv`) |
| DQ scorecard | **22 PASS · 3 WARN · 0 FAIL** (`out/dp_uc40_dq_scorecard.csv`) |
| Parent reproduction | **84 / 84** figures of `uc-pos-006` reproduced exactly; **0** definitional drift |
| Defects found by this UC | **1 new** (D-7 / O-13), disclosed and remediated by a `_fix`, governed original untouched |
| Package audit | **116 / 116 PASS** (`dp_uc40_package_audit.py`) |
| Certification | **READY** |

---

## 5.1 · Verification design

The harness re-reads the parquet with a **different batting-side derivation**, a **different filter
order**, and **hand-rolled boolean masks**. It imports nothing from `dp_uc40_kernel.py` for any value it
verifies. Coverage:

| Block | Checks |
|---|---|
| Frame integrity, entity lock, sensor boundaries, xwOBA grain | 16 |
| Career season panel (12 seasons × 14 metrics) | 168 |
| Career contact + approach panels (6 seasons × 17) | 102 |
| 2026 windows (3 × 25 incl. bat tracking and D-7 fix) | 76 |
| Monthly (7 × 5) | 35 |
| Platoon by season and by window + exposure shares | 73 |
| Pitch groups by window, pitch types | 90 |
| Breakpoint scan (10 cuts × 4) + 4 narrative claims | 44 |
| Parent reproduction, incl. an independent recomputation of the parent's July line | 8 |
| RF-1 / RF-2 | 11 |
| AD-1 / ST-1 | 9 |
| Pool and percentiles | 10 |
| **G8 superlative audit** — every "lowest/worst" claim re-derived against its enumerated cohort | 12 |
| **Report text scan** — required disclosures and figures present in the prose | 16 |
| **Total** | **711** |

The G8 audit and the text scan are the two blocks that make this harness more than a numeric diff: they
check that the *sentences* are entitled to the numbers.

### What verification caught (and the build had to change)

| # | Failure | Diagnosis | Resolution |
|---|---|---|---|
| 1 | `season 2026 in_zone_rate` and `W3 in_zone_rate` disagreed by 0.0009 / 0.0046 | **Not a build error — a defect in the governed `chase_rate_g`.** It derives `in_zone_rate` by subtraction, so NULL-`zone` rows are counted as in-zone | Shipped `in_zone_rate_fix` beside the governed original; re-cut every zone figure in the report and dashboard onto the corrected value; logged as **D-7 / O-13** |
| 2 | Report claimed the recent popup rate would be the **3rd-highest** of the 220-season pool | Off-by-count: the 97.7th percentile leaves 5 seasons at or above, not 3 | Report corrected to **5th-highest**; a permanent check now pins the rank |
| 3 | Report used the bare phrase "career worst" | **G8 violation** — a superlative without an enumerated cohort. This is the exact error the parent product `uc-pos-006` was caught making in July | Rewritten to "the lowest of his eleven qualified seasons"; a standing text check now blocks the bare phrase |

---

## 5.2 · DQ scorecard

| Status | Rules |
|---|---|
| **PASS (22)** | entity lock · pitch-key uniqueness · game_type purity · 12-season coverage · freshness (2026-09-02) · xwOBA grain · coordinate convention · wOBA weights joined · completeness at PA grain · completeness at tracked-BIP grain · zone completeness · hc completeness · three sensor boundaries · bat-tracking coverage stability · window PA floor · era derivation · schema asymmetry · parent reproduction · window partition · platoon partition · pool floor |
| **WARN (3)** | **R-16 O-8 exposure** — the governed hard-hit denominator includes untracked BIP. **Zero impact on this build**: 2026 has 0 untracked balls in play, so published and tracked-only rates are identical. Reported because the defect is still open repo-wide. · **R-18 PA floor: month** — March (23 PA) and September (9 PA) are below the 50-PA floor; flagged ⚠ on every surface, ranked nowhere · **R-25 D-7/O-13 exposure** — published minus corrected `in_zone_rate` = 0.0009 at 2026 season grain |
| **FAIL (0)** | — |

Grain-relative completeness (D-1) is enforced: `events` tested at PA grain, `launch_speed` at tracked-BIP
grain. Testing either at pitch grain would produce a spurious FAIL — the defect `uc-pps-028` found.

---

## 5.3 · Defect register as it stands after this UC

| ID | Function | State | Impact here |
|---|---|---|---|
| D1 | `whiff_rate` | open (zero-whiff group vanishes) | `_fix` used |
| D2 | `hard_hit_rate` merge | open | `_fix` used |
| D3 | `fpsr` | open | `_fix` used |
| D4 | `nresults` rounding | open | `nresults_unrounded` used |
| D5 / **O-7** | `pull_air_rate` reads `loc_*` | **remediated** by `uc-pos-013` PA-L1/PA-F1, **ratification still pending** | PA-F1 used; scale-invariance and convention asserted at build |
| D6 / **O-8** | hard-hit denominator includes untracked BIP | open | **0 impact** (0 untracked BIP in 2026); tracked-only variant shipped beside |
| **D-7 / O-13** | **`chase_rate_g.in_zone_rate` counts NULL `zone` as in-zone** | **NEW — opened by this UC** | `in_zone_rate_fix` shipped; exposure 0.0009 (season) / 0.0046 (recent window) |
| O-4 | xwOBA vs xwOBAcon naming | standing rule | enforced |
| O-5 | `truncated_pa` counted as PA | open | not encountered in this subject |
| O-11 | value-stream vs data-domain separation | open | not touched |
| O-12 | accent-folding in identity resolution | open | not applicable (single ASCII entity) |
| F1 | shared vendored charting asset | open | third copy of `_chartjs_4.4.1.umd.js` created |

**Policy held:** no governed function was patched inside a use-case build. Every correction is a `_fix`
sibling, and the originals are untouched upstream in `Baseball Functions.ipynb`.

---

## 5.4 · `version-controller`

| Change | Class | Consumer impact |
|---|---|---|
| New UC package `uc-pos-014` | **additive** | none |
| `uc-pos-006` figures **superseded** by a longer window | **non-breaking, supersession** | consumers of `dp_uc24` outputs should switch to `dp_uc40`; the parent's numbers remain correct **as of 2026-07-20** and reproduce exactly. `uc-pos-006` is not withdrawn — it is a valid earlier vintage |
| RF-2 denominator re-specified | **non-breaking for this subject** (agrees to 4 dp), **potentially breaking for a subject with sacrifice bunts** | declared in `03`; the parent's values are reproducible via `legacy_get_stats` |
| `in_zone_rate` corrected | **breaking for anyone quoting `chase_rate_g.in_zone_rate`** across every prior UC that published it | D-7 raised to the DPO; scope of prior exposure not assessed here |
| AD-1, ST-1, BT-1 | **new, provisional** | may not be reused without ratification |

---

## 5.5 · `certification-agent` — readiness

| Requirement | State |
|---|---|
| Lineage documented column-level for every KPI | ✅ `03` §3.3 |
| DQ scorecard executed, 0 FAIL | ✅ 23/2/0 |
| Glossary terms approved or explicitly provisional | ✅ `03` §3.1–3.2, 0 new business terms |
| Data model signed off | ✅ `02` |
| Acceptance criteria met | ✅ Q1–Q8 answered; Q6 answered within its declared structural limit |
| Independent verification | ✅ 711/711 |
| Parent reproduction (extension UC) | ✅ 84/84 |
| Privacy assessment complete | ✅ LOW–MODERATE, `03` §3.4 |
| Known defects disclosed on the consumable surface | ✅ report §10, dashboard "Declared limits" |
| Floors flagged everywhere they appear | ✅ ⚠ on every below-floor cell |

**Certification status: READY.** Publish decision belongs to the human Data Product Owner.
