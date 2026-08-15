# 00 · DPO Orchestration Record
**UC #34 · `uc-pos-010-stott-approach-change-001` · `dp_uc33` · delivered 2026-08-15**
<br>Value stream: Phillies Offense (`pos`) · DPO: Kellen Short · Data window: 2015 → **2026-08-13**

---
## Delivery plan — layer status

| Layer | Status | Evidence |
|---|---|---|
| 1 — Intake & Discovery | ✅ complete | `01_strategy_intake.md`; validator pass 1 gap report + Amendments 1–3 |
| 2 — Design | ✅ complete | `02_engineering_design.md`, `03_governance.md` |
| 3 — Build | ✅ complete | `04_engineering_build.md`; `dp_uc33_kernel.py` |
| 4 — Certify & Publish | ✅ complete | `05_quality_certification.md` — **86/86 PASS** |

## Capability fulfillment

| Capability | Satisfied by | Status |
|---|---|---|
| RC-1 results + approach at one grain | monthly master `z`, 46 cols | ✅ |
| RC-2 partial month distinguishable | `month_is_partial`; flagged on every surface | ✅ |
| RC-3 denominator beside every rate | `plate_apps`,`pitches`,`ooz`,`bips`,`first_pitches`,`ooz_swings` all shipped | ✅ |
| RC-4 hitter approach ≠ pitcher intent | two separate panels, PDF §2 + dashboard tabs | ✅ |
| RC-5 compare against a declared anchor | April anchor + rolling-PA view | ✅ |
| RC-6 every number traceable to a governed KPI | `06_technical_lineage.md` | ✅ |

## Governance gate checks

| Gate | Result |
|---|---|
| Validator go/no-go cleared before build | ⚠ **Built under a Layer-1 NO-GO with explicit DPO instruction.** 6 of 14 blocking items resolved by data-plane access (below); the rest are disclosed, not silently closed |
| Independent verification | ✅ 86 PASS / 0 FAIL, no import of the build kernel |
| New KPIs registered as provisional | ✅ AP-2, AP-3, AP-6, AP-9, AP-10 |
| Approved terms consumed, not forked | ✅ `fpsr` consumed; SWINGS/WHIFFS/PA definition inherited |
| Sensor-boundary NULL standard | ✅ no blanket `.fillna(0)`; counts filled by name, rates left NULL |

## Blocking items — resolved by data-plane access

| ID | Resolution |
|---|---|
| **B-1** three SWINGS lists | **RESOLVED.** `Baseball Functions.ipynb` is the authority and uses the **8-value list including `swinging_pitchout`** in both `whiff_rate` and `chase_rate`. `dp_uc7` L437's 7-value constant is stale. |
| **B-2** `fpsr` duplication | **RESOLVED.** Consumed, not rebuilt. Notebook formula `(pitches − balls)/pitches` over `pitch_number == 1` confirmed. |
| **B-3** `month` derivation | **RESOLVED.** Declared as `game_date.dt.month` (calendar). **March exists and is real** — 13 PA, 2 games. No March/April merge is applied; March is retained as its own bucket and flagged below floor. |
| **B-5** PA floor | **RESOLVED.** 50 PA adopted, per the standing standard. |
| **B-11** QAB at pitch grain | **AVOIDED.** QAB not used; see B-12. |
| **B-14** streak vs. ratio | **RESOLVED.** Both shipped — AP-10 for the title's claim, AP-9 for context. |

## Open items carried

| ID | Issue | Requires | Status |
|---|---|---|---|
| **O-1** | `quality_at_bat_rate` is **not present in `Baseball Functions.ipynb`**. The only implementation is `qab_rate.py`, which carries a NOT-AUTHORIZED banner, and its OI-1 (810 vs 1500) is open. QAB was therefore **excluded** from this build. | DPO | open |
| **O-2** | Three governed functions silently drop zero-numerator groups (`whiff_rate`, `hard_hit_rate`, `fpsr`). `_fix` variants used here; originals untouched. | DPO | **open — repo-wide** |
| **O-3** | `nresults` rounds to 3dp before ratios are taken. Demonstrated: August BB/K reads 3.2676 from rounded rates vs **3.25** from counts. | DPO | open |
| **O-4** | `pull_air_rate` computes `total_pulls` and never uses it; published rate is pulled-air per **BIP**. Not used in this build. | DPO | open |
| **O-5** | Three plate half-widths in repo (0.83 Statcast vs `dp_uc7` 0.708). No zone artifact shipped here, so not triggered. | DPO | open |
| **O-6** | AP-2/3/6/9/10 provisional pending ratification. | DPO | open |

## Publish recommendation

**APPROVE for internal Phillies staff distribution.** Every headline independently verified.
The single interpretive risk — that the improvement reads as Stott's doing alone when pitcher
first-pitch strike rate fell 26 points over the same window — is stated in the report's opening
paragraph, not buried. **Not approved for external/media distribution** (restricted use, per
`03_governance.md`).
