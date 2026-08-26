# 00 · DPO Orchestration Record — uc-pps-027 (UC #38 / dp_uc38)

**Human DPO:** Kellen Short
**Run 1:** scheduled task, 2026-08-25, non-interactive — Layers 1, 2 and 4 delivered; **Layer 3 blocked** (data plane unmounted).
**Run 2 (REOPEN):** interactive, 2026-08-26 — data plane mounted by the DPO; **Layer 3 executed, Layer 4 certified.**
**Orchestrator:** `data-product-owner` · **Outcome:** ✅ **DELIVERED — CERTIFY-READY. 117/117 verification PASS.**

---

## 1 · ID claim

| Counter | Highest on disk at intake | Claimed |
|---|---|---|
| Ledger UC | 37 (`uc-pos-013`, Bohm, 2026-08-23) | **38** |
| pps contract | `uc-pps-026` (Cortes, 2026-08-20) | **`uc-pps-027`** |
| Build artifact | `dp_uc37` (Bohm) | **`dp_uc38`** |

Verified against the repo, not the drifting `uc_ledger_AI.md`. Ledger patch staged as
`uc_ledger_AI_PATCH_uc-pps-027-nola-stubbs.md`.

## 2 · Layer sequencing and gate status

| Layer | Agents | Gate | Status |
|---|---|---|---|
| **1 — Intake & Discovery** | use-case-validator · source-system-profiler · domain-steward-proxy · business-glossary-agent | Must complete before design | ✅ **PASS** — see `01_strategy_intake.md` |
| **2 — Design** | data-architect · kpi-calculator · metadata-mapper · dq-rule-definer · data-dictionary · data-tagger | Must complete before build | ✅ **PASS** — see `02_engineering_design.md`, `03_governance.md` |
| **3 — Build** | technical-lineage-builder · data-engineer · data-quality-engineer | Requires approved L2 | ✅ **PASS (run 2)** — pipeline executed against the live plane; 23 primary + 20 addendum receipts; 0 DQ FAIL. See `04_engineering_build.md` |
| **4 — Certify & Publish** | certification-agent · analytics-enabler · privacy-watchdog · cost-watchdog · version-controller | Requires approved L3 | ✅ **CERTIFY-READY (run 2)** — all blocking artifacts present. See `05_quality_certification.md` |

**The gate held, and then it opened.** Run 1 is the governance system working as designed:
Layer 3 could not complete, so Layer 4 returned **not-ready** and the report shipped with every
numeric slot explicitly unfilled rather than estimated. The failure mode this prevents is
`uc-pps-010` — a report that shipped with 19 empty harness slots and no disclosure, retired and
its ID burned. Run 2 mounted the plane and closed the gate legitimately: **every number in the
filled report was computed on 2026-08-26 by `dp_uc38_*.py` / `dp_uc38b_*.py`.** Nothing was
carried over from an estimate, because no estimate was ever written down.

## 3 · Decisions taken in the DPO's absence

The scheduled task instructs autonomous execution. Six decisions were made and are logged
here for ratification:

| # | Decision | Rationale | Reversible? |
|---|---|---|---|
| **DV-1** | "Last several starts" = **last 5**, with 3/5/8 sensitivity | No definition supplied; sensitivity prevents window-shopping | Yes — one constant (`RECENT_N_STARTS`) |
| **DV-2** | Catcher name resolution: DPO's `pos`-merge is **primary**, `uc-cat-001` dict is **cross-check** | The DPO's own logic covers Nola's 2015–19 catchers, which `uc-cat-001`'s 2020–26 profile does not | Yes |
| **DV-3** | Game floor **≥3 game_pk** inherited from `uc-cat-001` A-4; pitch floor 100, PA floor 50 — all as **flags** | Consistency with the adjacent product; G5 forbids silent filtering | Yes |
| **DV-4** | Seattle lineup advance **de-scoped** | The ask is a battery product, not an opponent product; priced as a bid option | Yes — offered fast-follow |
| **DV-5** | Nine new `BAT-*` KPIs created rather than reusing `uc-cat-001`'s ten verbatim | Three of the ten map directly (shipped as BAT-4/BAT-9/`fpsr`); the sequencing family (BAT-5/6/7) has no repo precedent — Rule-1 grep found none | Ratify BAT-5/6/7 or retire them |
| **DV-6** | **No numbers published.** Harness ships unfilled | Skill non-negotiable #1 | **SUPERSEDED in run 2** — plane mounted, harness filled from receipts |
| **DV-7** *(run 2)* | Game date corrected **2026-08-25 → 2026-08-26**; the run-1 date was carry-in prose | Nola's last start is 8/19; the frame confirms no 8/25 Nola appearance | Yes |
| **DV-8** *(run 2)* | Breakpoint **2026-07-05**, stated not fitted, and scanned across 8 boundaries (TR-2) | An era boundary is a researcher degree of freedom (**G6**) | Yes — one constant |
| **DV-9** *(run 2)* | Second build `dp_uc38b_battery_addendum.py` created rather than editing the certified primary | The travel test (TR-1) is a design the run-1 harness could not have anticipated; the primary build stays byte-stable and re-verifiable | Yes |

## 4 · Rule-1 grep — "does this KPI already exist?"

Before declaring any KPI new, the repo was searched for prior art:

| Candidate | Prior art found | Disposition |
|---|---|---|
| Arsenal / pitch mix share | `dp_uc25` usage tables, `dp_uc18` PITCH_GROUP dict | **Inherit** the dict; the share computation is trivial and unnamed — shipped as BAT-1 |
| Two-strike fastball usage | `uc-cat-001` KPI-1, specced never built | **Inherit definition verbatim**, ship as BAT-4 |
| In-zone whiff | `uc-cat-001` KPI-3 (incl. its label-mismatch fix) | **Inherit definition verbatim**, ship as BAT-9 |
| First-pitch strike | `fpsr`, locked since UC8; also `uc-cat-001` KPI-4 | **Locked KPI — use as-is**, do not re-implement |
| Edge / OOZ-CS / air-GB | UC8, glossary approved | **Inherit verbatim** |
| Repeat-pitch rate | **none** | NEW-PROVISIONAL BAT-5 |
| Arsenal entropy | **none** | NEW-PROVISIONAL BAT-6 |
| Ahead-vs-behind divergence | **none** | NEW-PROVISIONAL BAT-7 |
| Zone rate by count state | adjacent (`chase_rate.in_zone_rate`, unsplit) | NEW-PROVISIONAL BAT-8, built on the governed in-zone boundary |

## 5 · Escalations to the human DPO

| # | Item | Why it needs a human |
|---|---|---|
| ~~**E-1**~~ | ~~Mount the MLB data plane~~ | ✅ **CLOSED 2026-08-26** — folder granted, both builds and both verification harnesses executed |
| **E-2** | Ratify or retire BAT-5 / BAT-6 / BAT-7 | New KPIs enter the locked set only by DPO decision |
| **E-3** | Confirm tonight's battery and lineup | Carry-in prose, not a posted card |
| **E-4** | Approve DV-1 window definition | Affects the headline |
| **E-5** | Decide whether to fund the `uc-cat-001` completion fast-follow | This UC paid for the plumbing; the remaining seven KPIs are cheap now |
| **E-6** | Paste the ledger patch | Ledger drift is now ~6 patches deep |
