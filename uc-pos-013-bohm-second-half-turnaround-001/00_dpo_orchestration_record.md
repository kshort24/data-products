# 00 · DPO Orchestration Record
**UC #38 · `uc-pos-013-bohm-second-half-turnaround-001` · `dp_uc37` · delivered 2026-08-24**
<br>Value stream: Phillies Offense (`pos`) · DPO: Kellen Short · Data window: 2015 → **2026-08-22**

---
## Delivery plan — layer status

| Layer | Status | Evidence |
|---|---|---|
| 1 — Intake & Discovery | ✅ complete | `01_strategy_intake.md` — validator GO, 0 blocking, 6 conditions; Layer-1 repo search run first |
| 2 — Design | ✅ complete | `02_engineering_design.md`, `03_governance.md` |
| 3 — Build | ✅ complete | `04_engineering_build.md`; `dp_uc37_kernel.py`, `dp_uc37_bohm_turnaround.py` |
| 4 — Certify & Publish | ✅ complete | `05_quality_certification.md` — DQ 9 PASS / 5 WARN / 0 FAIL · verification **227/227 PASS** — certification **ready** |

## Capability fulfilment (what the requester asked for, where it landed)

| Capability | Satisfied by | Status |
|---|---|---|
| Calibrate first: were the outcomes positive? | Report §1 verdict table + §2, ahead of any mechanism (RC-1 grammar) | ✅ |
| Top-line SLG · BA w/RISP · run creation | `window_split` receipt; RISP via the DPO's own operator; governed `runs_created` + RC-R1 rate | ✅ |
| Contact quality incl. pull-air, hard-hit, air, barrel | §3 + `direction_air_matrix` + `pull_air_quality`; **O-7 remediated so pull-air executes at all** | ✅ |
| "Rarely whiffs" + approach change | §3 + career trajectory + pool percentiles (z-whiff 2nd pctile); approach verdict MOSTLY FALSE | ✅ |
| Platoon + pitch_groups | §4; PL-1 direct standardisation; PITCH_GROUP map verbatim | ✅ |
| Persona-actionability within the value stream | Report §5 — correlate→persona hypothesis table, causation explicitly not identified | ✅ |
| DPO's notebook method honored | Transcribed as the §15 verification leg (2 paren repairs logged); its data dictionary names carried onto every surface | ✅ |
| Outcome-selected window priced both ways | 10-point breakpoint scan, first-class receipt; sign survives every boundary | ✅ |
| PDF + interactive dashboard | house weasyprint PDF (7 pp) + self-contained vendored-Chart.js dashboard (7 tabs, screenshot-QA'd) | ✅ |

## Governance gate checks

| Gate | Result |
|---|---|
| No CDE inference | ✅ definitions consumed from the notebook/glossary lineage; gaps (C-1..C-6) resolved by ruling, logged in `01` |
| No build without approved specs | ✅ `02` specs precede `04`; lineage in `04` covers every published KPI |
| No publish without certification | ✅ `05` returns ready before this record's recommendation |
| Breaking changes | ✅ none (v1.0.0, first release); additive `cum_slg` flagged to the AP-6 bundle |
| Privacy before external exposure | ✅ `03` — LOW; internal-only distribution |
| New KPIs provisional, originals untouched | ✅ RC-R1, PA-L1, PA-F1, ZS-1 registered provisional; D1–D6 originals untouched; O-7 remediation is a NEW name, not a patch |
| Sensor-boundary NULL standard | ✅ no blanket fillna; NULLs survive into the dashboard payload as `null` |
| `(level, df)` signature rule | ✅ every new function ships `(level, df)` |
| Alias reconciliation | ✅ `par`/`pulled_air` → `pull_air_rate`; `dd`=`vs` placeholder resolved in `02` |

## Open items

| ID | Issue | Status |
|---|---|---|
| O-2 | D1–D3 zero-numerator drops, repo-wide | open, inherited |
| O-3 | D4 rounding + `inds` foul contamination (quantified here: ~6 mph) | open, inherited |
| O-4 | xwOBAcon naming | open; convention applied |
| O-5 | `truncated_pa` PA fork | open; 3 rows quantified here |
| **O-7** | `pull_air_rate` unexecutable | **remediation shipped (PA-L1 + PA-F1) — awaiting DPO ratification of the hc→loc derivation**; on ratification, promote to the glossary and close |
| O-8 | hard-hit untracked denominator | open; exposure < 0.2 pt here |
| **O-11 (NEW)** | Value-stream vs data-domain separation formalized in `02` — needs a Register ruling to become standard | **open — new this build** |
| F1 | shared `_assets/` for vendored chart lib (3rd copy) | open, forwarded (uc-pps-026) |

## Publish recommendation

**APPROVE for internal Phillies staff distribution.** Every headline recomputed on an independent
path; the finding survives all ten candidate breakpoints; both headline windows clear the 50-PA floor
— a first for this UC family's headline contrast.

Three interpretive risks stated on page 1 rather than buried: (1) the post-break vs LHP and RISP
cells that carry the loudest numbers are below floor; (2) the recovery began ~1 May — the break is a
narrative marker, not a structural breakpoint; (3) part of the BA/BABIP jump is correction of a
pre-break under-performance, so expect settling even if the process holds.

**Not approved for external/media distribution** (staff-role hypothesis table in §5; `03` tagging).

September refresh armed (`07`): below-floor cells may clear as the post-window grows → v1.1.0.
