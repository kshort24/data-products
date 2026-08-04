# 00 — DPO Orchestration Record

**Agent:** `data-product-owner` (orchestrator) · **Use Case:** `uc-pps-kilian-acquisition-001` · **Value stream:** `pps`
**Ledger IDs:** UC **#30** · contract `uc-pps-024` · build artifact `dp_uc29`
**Human DPO:** Kellen Short · **Date:** 2026-08-04
**Recommendation:** ✅ **Ready to publish** — pending human acknowledgment of 4 non-blocking open items.

This is the spine of the package: the sequenced delivery plan, the governance gates checked at each handoff, the capability-fulfillment map, and the publish recommendation. Department detail lives in files 01–07.

---

## The ask, in one line

> *"We just acquired Caleb Kilian at the deadline. He's the one with the least history — a Cubs starting prospect who converted to relief for a bad Giants team this year. What did we buy, what should the pitching department do with him, what should the battery call, and how should Mattingly use him?"*

**Four named personas, four different decisions, one pitcher who has never worked with this organization.** The deliverable is an onboarding dossier, not a stat sheet — and notably not an opponent attack plan, because there is no opponent yet.

---

## Delivery plan & layer status

| Layer | Departments | Status |
|---|---|---|
| 1 — Intake & Discovery | Strategy & Intake | ✅ complete (**GO**, 0 blocking, 5 non-blocking gaps) |
| 2 — Design | Engineering (Design) ∥ Governance | ✅ complete — 3 new KPIs specified before use |
| 3 — Build | Engineering (Build) | ✅ complete — 19 CSV receipts, 4 figures |
| 4 — Certify | Quality | ✅ **READY** — 205/205 independent checks, 0 FAIL, 2 WARN |
| 5 — Launch | Consumer Success ∥ Marketing | ✅ artifacts staged (branded PDF, 9pp + markdown source) |
| 6 — Operations | Platform (persistent) | ✅ closure step defined (re-read at 150 PA in Phillies uniform) |

**Front door:** `visual-intake-agent` skipped — the request arrived as written prose from the human DPO. Sequence started at `use-case-validator`.

**Pattern inheritance.** UC#3 (Luzardo deep dive) → UC#8 (Nola vs WAS, canonical flat-file) → UC#11 (Rangel, multi-level evidence) → UC#29 (Painter, first self-scout variant) → **UC#30 (this one, first acquisition-onboarding variant)**.

---

## What is genuinely new in this UC

This is the first UC in the `pps` line where **the subject has never pitched for the organization**. That changes three things structurally, and they are worth recording because the next four deadline acquisitions will inherit them:

1. **No Phillies rows, by construction.** Every prior pitcher-side UC could anchor on `phils_<year>.parquet`. This one runs entirely off an opponent-folder cache. The entity lock and dedup discipline carry over unchanged; the *source* does not.
2. **No opponent dimension, and no role to attach one to.** UC#29 descoped the opponent because Painter had never faced Baltimore. Here it is descoped for a stronger reason: there is no next opponent, because there is no assigned role. **Descope is a decision, not an omission** — recorded in 01 as non-blocking with an explicit follow-on trigger.
3. **A role-era split replaces the level tier.** UC#11 and UC#29 used MLB/AAA tiers. Here the equivalent evidential structure is 2026-relief vs 2022-24-starting, with the same never-blend rule. Generalized as the **Role Conversion Delta** KPI so the next converted acquisition can reuse it.

---

## Governance gates checked at handoff

| Gate (CLAUDE.md governance principle) | Where enforced | Result |
|---|---|---|
| **1. No CDE inference** | 02 glossary | ✅ All terms locked-inherited or explicitly flagged report-local. Two report-local terms (`slider_finish_rate`, `fastball_elevation_rate`) defined from existing CDEs, returned to DPO as promotion candidates — not invented meaning |
| **2. No pipeline build without approved specs** | 04 → 05 | ✅ Build implements the 04 KPI specs; all three new KPIs written to spec (plain language + formula + grain + population + CDEs + edge cases) **before** appearing in any output |
| **3. No publish without certification** | 07 | ✅ `certification-agent` returns READY; 205/205 independent verification |
| **4. No breaking changes without notice** | 07 | ✅ n/a — new data product, no consumers to break. Locked KPI functions inherited byte-identical from `dp_uc28` |
| **5. Privacy flags block external publish** | 03 | ✅ No PII beyond public MLBAM player identifiers. **Internal use only** — contains acquisition-evaluation judgments |

---

## Escalations to the human DPO

| # | Item | Raised by | Severity | Ask |
|---|---|---|---|---|
| **O1** | `xwobacon` glossary promotion (carried forward from `uc-pps-021`) | kpi-calculator | Medium | Promote `xwobacon` to the glossary and formally deprecate pitch-level `get_stats.xwoba` repo-wide. **This UC applied the hardening and cites only `xwobacon`** — the governance paperwork is still open |
| **O2** | **NEW** — locked `chase_rate().in_zone_rate` counts null-zone rows as in-zone | data-quality-engineer | Medium | The inherited function inflates zone rate whenever untracked `automatic_ball` rows are present (0.486 vs 0.481 here). Locked function left unmodified per the inheritance rule; this UC publishes a strict variant. Needs a repo-wide decision like O1 |
| **O3** | **NEW** — `launch_speed` is populated on foul balls, not only balls in play | data-quality-engineer | Medium | 114 of 736 rows in the 2026 tier. Any EV mean that omits `type=='X'` reads several mph low. Caught in this session's verification pass after an early draft got it wrong. Recommend a lint rule or a shared `ev()` helper |
| **O4** | Reverse platoon split is directional, not settled | use-case-validator | Low | 83 PA vs RHH carrying all five home runs. The deployment recommendation leans on it. Re-test at 150 PA in Phillies uniform before treating as permanent |

**None of these block publication.** O2 and O3 were both found *by* this UC's quality process and are strictly repo-improving.

---

## Capability fulfillment map

| Consumer question | Answered in | Backed by |
|---|---|---|
| What are his top-line results? | Report §"What the role change actually did" | `era_summary`, `season_log` |
| What do the underlying indicators say? | Report §Bottom line 1-2, §arsenal | `role_conversion_delta`, `arsenal_by_era` |
| What should we expect going forward? | Report §Bottom line 2, 5 · §pitching department | `monthly_arc`, `batter_sequence` |
| How does he approach LHH vs RHH? | Report §Approach vs LHH · §Approach vs RHH | `platoon`, `pitch_by_hand`, `count_usage` |
| What can the pitching department act on? | Report §"the development plan" | `slider_finish`, `fastball_elevation`, `damage_log` |
| What should the battery call? | Report §"the pitch-selection card" | `count_usage`, `slider_vertical_half`, `fps_by_hand` |
| How should Mattingly use him? | Report §"how to use him" | `deployment`, `outing_log`, `batter_sequence` |

**7 of 7 consumer questions answered with receipts.** No question was answered from judgment alone.

---

## Publish recommendation

✅ **PASS — cleared for internal advance use.**

Independent verification (`dp_uc29_verification.py`) recomputed every headline number via a separate code path — plain boolean masks, no import of the build module — and returned **205/205 PASS**. That pass caught **three real defects** in the draft (contaminated exit-velocity means, an inflated zone rate, and inconsistent usage denominators), all of which were fixed in the build rather than papered over in the prose.

Entity lock, dedup, game-type, era coverage, freshness and the 2025 true gap all PASS. Glossary, lineage and dictionary are complete and sourced, not inferred. Two DQ WARNs are sample-size and locked-function disclosures, both surfaced in the report's own caveats section.

**Ledger append pending:** UC #30 / `uc-pps-024` / `dp_uc29`. Next available: **UC #31 / dp_uc30** (`uc-pps-025` / `uc-pos-008`).

```json
{"uc":30,"id":"uc-pps-024","build":"dp_uc29","status":"build_complete_pending_dpo_signoff",
 "open_items":[
   {"id":"O1","issue":"xwobacon glossary promotion + deprecate get_stats.xwoba","source_agent":"kpi_calculator","requires_human":true,"status":"open","carried_from":"uc-pps-021"},
   {"id":"O2","issue":"locked chase_rate.in_zone_rate counts null zone as in-zone","source_agent":"data_quality_engineer","requires_human":true,"status":"open","new_this_uc":true},
   {"id":"O3","issue":"launch_speed populated on foul rows; EV means must filter type=='X'","source_agent":"data_quality_engineer","requires_human":true,"status":"open","new_this_uc":true},
   {"id":"O4","issue":"reverse platoon split directional at 83 PA vs RHH","source_agent":"use_case_validator","requires_human":false,"status":"open"}],
 "closure_step":"re-read at 150 PA in Phillies uniform; re-test platoon + Slider Finish Rate vs 70% target"}
```
