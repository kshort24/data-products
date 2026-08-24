# 05 · Quality & Certification
**data-quality-engineer · certification-agent**

## DQ scorecard

| Dimension | Check | Result | Class |
|---|---|---|---|
| Uniqueness | PITCH_KEY (`game_pk`,`at_bat_number`,`pitch_number`) duplicates, 2026 & career | 0 / 0 | ✅ PASS |
| Validity | entity lock: 1 `player_name`, 1 MLBAM, 1 `stand` | ✅ | ✅ PASS |
| Validity | `game_type` universe 2026 | `{'R'}` only | ✅ PASS |
| Completeness | `description` NULL | 0 | ✅ PASS |
| Completeness | `p_throws`, `bat_score`, `post_bat_score`, `on_2b/3b` (nullable-by-design) NULL-where-unexpected | 0 | ✅ PASS |
| Completeness | `zone` NULL | **5 rows** — excluded from BOTH zone populations (chase and z-swing denominators stay symmetric) | ⚠ WARN (disclosed) |
| Completeness | `pitch_type` NULL 5 + `EP` 6 → `pitch_group='other'` | 11/1,865 pitches outside group panels (0.6%) | ⚠ WARN (disclosed) |
| Completeness | tracked BIP | 399/400 (1 untracked; **0** `hc_x/hc_y` NULL) | ⚠ WARN — D6/O-8 exposure < 0.2 pt |
| Accuracy | `bat_score` monotone within PA (first == min, all PAs) | ✅ | ✅ PASS |
| Accuracy | window complementarity; 13–15 Jul empty; PA/pitch conservation at all five grains | ✅ | ✅ PASS |
| Validity | `events` universe vs governed sets | **3 `truncated_pa` rows** (all pre-break) — O-5 fork, counted PA+AB with no outcome; worst-case 2-pt effect on pre-break BA | ⚠ WARN (inherited open item) |
| Validity | `description` universe vs SWINGS/WHIFFS | 5 `automatic_ball/strike` rows — non-swings, denominators only | ⚠ WARN (disclosed) |
| Consistency | coordinate convention: median pulled-GB `loc_x` = −45.4 ft (LF for RHB); classification identical at scale C=1.0 and C=2.495671 | ✅ | ✅ PASS |
| Timeliness | freshness 2026-08-22 (T-1 at build); all 12 season files load | ✅ | ✅ PASS |

**Totals: 9 PASS / 5 WARN / 0 FAIL.** No blocking issue; every WARN is disclosed on the consuming
surface it affects.

## Independent verification

`dp_uc37_verification.py` — separate code path (reverse-order load, subject-first filter, inline
masks, algebraic re-expression of the pull classification, first/last-path runs-created, repaired
DPO-notebook merge chain as the original-method leg): **227 PASS / 0 FAIL** across 16 sections.
Notable legs: §11 proves the pull-air classification scale-invariant and cross-checks a spray-angle
formulation (0 disagreements); §12 recomputes PL-1 by hand-weighted sums; §14 recomputes the post-window
wOBA at all ten breakpoints; §15 reproduces the DPO's own method and matches the kernel at 3–4dp on
every compared value (D4 rounding acknowledged).

## Defect register

| ID | Status here |
|---|---|
| D1 `whiff_rate` inner-merge | `_fix` used; original untouched. Repo-wide fix = **O-2**, open |
| D2 `hard_hit_rate` inner-merge | `_fix` used | 
| D3 `fpsr` zero-ball drop | `_fix` used |
| D4 `nresults` 3dp rounding | avoided (counts path); **O-3** open |
| D5/**O-7** `pull_air_rate` unexecutable (`loc_*` not in schema) | **REMEDIATED this build** via PA-L1 + PA-F1 (derivation + verbatim boundary logic). Original untouched; remediation **provisional pending DPO ratification** of the hc→loc derivation |
| D6/**O-8** `hard_hit_rate` untracked-BIP denominator | retained deliberately (governed convention); exposure quantified: 1 untracked BIP season-wide, divergence < 0.2 pt |
| O-5 `truncated_pa` PA fork (uc-pos-008) | 3 rows, quantified, disclosed; not forked silently |
| O-3 `inds` foul contamination | quantified: all-rows EV runs **~6 mph below** tracked-BIP EV (84.2 vs 90.1 pre; 85.2 vs 91.7 post); reconciliation receipt shipped |

## Certification readiness — **READY**

| Artifact | Present | Consistent |
|---|---|---|
| Use-case doc + validator disposition (GO) | ✅ `01`, UC doc | ✅ |
| Design specs + new-KPI registrations (RC-R1, PA-L1, PA-F1, ZS-1 provisional) | ✅ `02` | ✅ |
| Glossary disambiguation + tagging + privacy (LOW) | ✅ `03` | ✅ |
| Lineage + build inventory | ✅ `04` | ✅ |
| DQ scorecard + independent verification | ✅ this doc | ✅ 227/227 |
| Consumables (PDF, dashboard) trace to receipts | ✅ | ✅ (dashboard reads CSVs; report figures receipt-backed; screenshot QA on all 7 tabs, 0 console errors) |
| Version manifest + comms | ✅ `07` | ✅ |

Certification agent returns **ready**; publish decision rests with the DPO (`00`).
