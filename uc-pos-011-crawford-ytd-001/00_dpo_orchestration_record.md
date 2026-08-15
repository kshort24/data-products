# 00 · DPO Orchestration Record
**UC #35 · `uc-pos-011-crawford-ytd-001` · `dp_uc34` · delivered 2026-08-15**
<br>Value stream: Phillies Offense (`pos`) · DPO: Kellen Short · Data window: 2015 → **2026-08-13**

---
## Delivery plan — layer status

| Layer | Status | Evidence |
|---|---|---|
| 1 — Intake & Discovery | ✅ complete | `01_strategy_intake.md` — validator pass 1 GO with 4 non-blocking conditions |
| 2 — Design | ✅ complete | `02_engineering_design.md`, `03_governance.md` |
| 3 — Build | ✅ complete | `04_engineering_build.md`; `dp_uc34_kernel.py`, `dp_uc34_crawford_ytd.py` |
| 4 — Certify & Publish | ✅ complete | `05_quality_certification.md` — **127/127 PASS** |

## Capability fulfilment

| Capability | Satisfied by | Status |
|---|---|---|
| RC-1 premises tested before they are explained | Report §1 — a verdict column on all four submitted assertions, ahead of any mechanism | ✅ |
| RC-2 results and approach at one grain | monthly master `z`, 44 columns × 6 months | ✅ |
| RC-3 denominator beside every rate | `plate_apps`, `pitches`, `ooz`, `bips`, `tracked_bips`, `first_pitches` all shipped | ✅ |
| RC-4 hitter approach ≠ pitcher intent | `fpsr` / `in_zone_rate` labelled as opponent metrics in kernel docstrings, report and dashboard | ✅ |
| RC-5 outcome-selected windows priced both ways | 9-point breakpoint sensitivity scan shipped as a first-class receipt, not an appendix | ✅ |
| CX-1 context against Phillies CF, Statcast era | `cf_context_pool()` transcribed from the DPO snippet; 8 comparator seasons | ✅ |
| CX-2 three cumulative results KPIs, ghosted context | `running_line_pa()` extended to BA and OBP; Fig 1 + interactive metric toggle | ✅ |
| RC-6 every number traceable to a governed KPI | `04_engineering_build.md` column-level lineage | ✅ |

## Governance gate checks

| Gate | Result |
|---|---|
| Validator go/no-go cleared before build | ✅ **GO.** Layer-1 repo search run first, per the standing rule — it prevented three KPIs being specced as new |
| Independent verification | ✅ **127 PASS / 0 FAIL**, no import of the build kernel |
| New KPIs registered as provisional | ✅ CR-1, CR-2, CX-1, PL-1 |
| Approved terms consumed, not forked | ✅ `fpsr` consumed (second `pos`-side use); SWINGS/WHIFFS/PA/PITCH_GROUP inherited |
| Sensor-boundary NULL standard | ✅ no blanket `.fillna(0)`; counts filled by name, rates left NULL below floor |
| `(level, df)` signature rule | ✅ all four new functions ship `(level, df)`; no inversion introduced |
| Alias reconciliation | ✅ `xwobacon_bip` named to the O-4 convention, not "xwOBA"; no notebook shorthand shipped |

## Layer-1 repo search — what it caught before design began

Per the standing rule from `uc-pos-010`, three commands were run before any KPI was called new.

| Finding | Consequence |
|---|---|
| `nresults`, `whiff_rate`, `chase_rate`, `hard_hit_rate`, `barrel_rate`, `fpsr`, `ev90` all exist and are governed | Consumed, not rebuilt. Only the D1–D4 `_fix` variants are re-expressed |
| `dp_uc33_kernel.py` already carries D1–D4 `_fix` variants and `running_line_pa` | **Inherited wholesale.** `running_line_pa` extended with BA/OBP rather than forked |
| No prior UC on Justin Crawford — `ls data-products/ \| grep -i crawford` returns nothing | Genuinely first-touch subject; no prior spec to reconcile |
| `PITCH_GROUP` map lives in `dp_uc18_marsh_breakout.py` L170 | Consumed verbatim |
| The standing batter floor is **50 PA** | Applied. It puts **both March and August below floor** — a material constraint on this UC's headline month |
| `pull_air_rate` exists but references `loc_x`/`loc_y` | **Not columns in the parquet schema.** Confirmed against `pq.ParquetFile(...).schema.names`. Not used; opened as **O-7** |

## Open items carried

| ID | Issue | Requires | Status |
|---|---|---|---|
| **O-2** | D1–D3: three governed functions silently drop zero-numerator groups. `_fix` variants used; originals untouched | DPO | **open — repo-wide, inherited from uc-pos-010** |
| **O-3** | `nresults` rounds to 3dp before ratios are taken | DPO | open — inherited |
| **O-4** | `xwobacon_bip` size semantics — a BIP-level mean is not comparable to `woba` | DPO | open — inherited from uc-pps-025; naming convention applied here |
| **O-5** | Three plate half-widths in repo (0.83 vs `dp_uc7` 0.708) | DPO | open — no zone artifact shipped here, not triggered |
| **O-7** | **NEW.** `pull_air_rate` cannot execute against the governed data plane — it reads `loc_x`/`loc_y`, which do not exist. `hc_x`/`hc_y` do | DPO | **open — new this build** |
| **O-8** | **NEW.** `hard_hit_rate` divides by ALL balls in play, so an untracked BIP is silently scored "not hard hit". 0.6 pt effect here; grows with any tracking gap | DPO | **open — new this build** |
| **O-9** | CR-1, CR-2, CX-1, PL-1 provisional pending ratification | DPO | open |

## Publish recommendation

**APPROVE for internal Phillies staff distribution.** Every headline independently verified on a
separate code path.

Three interpretive risks are stated in the report's opening block rather than buried:
(1) the improvement is BABIP-led on *softer* contact, (2) the 15 June breakpoint was chosen after
seeing the outcome and a mid-May breakpoint reverses its sign, (3) August — the strongest month — is
**42 PA, below the reliability floor**, and is very nearly a pure right-handed-pitching sample.

**Not approved for external or media distribution.** This product evaluates a rookie's readiness and
contains platoon-deployment findings about a named individual; see `03_governance.md` §Access asymmetry.
