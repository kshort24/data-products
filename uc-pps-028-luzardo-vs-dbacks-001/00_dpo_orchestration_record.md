# 00 · DPO Orchestration Record — uc-pps-028 (UC #39 / dp_uc39)

**Human DPO:** Kellen Short · **Run:** interactive, 2026-09-01, data plane mounted
**Orchestrator:** `data-product-owner` · **Outcome:** ✅ **DELIVERED — CERTIFY-READY · 195/195 verification PASS · 0 DQ FAIL**

---

## 1 · ID claim

| Counter | Highest on disk at intake | Claimed |
|---|---|---|
| Ledger UC | 38 (`uc-pps-027`, Nola–Stubbs, 2026-08-26) | **39** |
| pps contract | `uc-pps-027` | **`uc-pps-028`** |
| Build artifact | `dp_uc38` | **`dp_uc39`** |
| Package folder | — | `uc-pps-028-luzardo-vs-dbacks-001` |

Verified against the repo (`ls dp_uc*`, `ls uc-pps-0*`), not the drifting installed-skill ledger,
which still reads "next available UC #12". Ledger patch staged as
`uc_ledger_AI_PATCH_uc-pps-028-luzardo.md` — **escalation E-3**.

## 2 · Layer sequencing and gate status

| Layer | Agents | Gate | Status |
|---|---|---|---|
| **1 — Intake & Discovery** | use-case-validator · source-system-profiler · domain-steward-proxy · business-glossary-agent | before design | ✅ **PASS** — `01_strategy_intake.md`; 3 blocking gaps resolved, 3 non-blocking carried |
| **2 — Design** | data-architect · kpi-calculator · semantic-modeler · dq-rule-definer · data-dictionary · data-tagger · privacy-watchdog | before build | ✅ **PASS** — `02_engineering_design.md`, `03_governance.md` |
| **3 — Build** | technical-lineage-builder · data-engineer · data-quality-engineer · eda-agent | needs approved L2 | ✅ **PASS** — executed against the live plane; 30 receipts; 0 DQ FAIL — `04_engineering_build.md` |
| **4 — Certify & Publish** | certification-agent · analytics-enabler · consumer-onboarding · dashboard-specifier · cost-watchdog · version-controller | needs approved L3 | ✅ **CERTIFY-READY** — `05`, `06`, `07` |

Descoped with reasons recorded (`02` §5): `join-validator` (no cross-domain join),
`machine-learning-engineer` (no prediction task), `data-observability` (no post-publication pipeline).

## 3 · The orchestration decision that shaped this product

The ask contained **two client claims and an invitation to lead the narrative**:
*"maybe the Phillies' most consistent pitcher"* and *"since the end of April he has been very good."*

`uc-pps-027` closed with calibration finding **C-1**: *a harness built around a causal claim the
client already believes will fill cleanly and be wrong.* The DPO applied it directly. Two structural
rulings followed, and everything else in the package descends from them:

1. **Separate the claims.** "Very good" is a claim about **level**; "most consistent" is a claim about
   **variance**. Bundled, they produce one answer, and one of the two halves would have been wrong.
   Split, they produce two — and they disagree.
2. **Make the design able to fail.** Six independent axes, no composite index, ranked against the
   whole rotation, with the client's chosen boundary scanned across eight alternatives plus a
   full-season control. **Verification check 7 asserts that Luzardo's CN-1 rank is *not* 1 at every
   boundary** — the harness is written so that the report's central caveat is itself testable.

**Outcome: the level claim survived everything; the consistency claim did not.**
Luzardo is #1 in xwOBA at all eight boundaries *and* on the uncut season. His #1 in start-to-start
variation exists only in a three-boundary band around May 1, and on the floor axes the title belongs
to Cristopher Sánchez. Where he *does* lead unambiguously on consistency is workload — 21 straight
turns, none missed, in a 90–110 pitch band. That is a better answer than the one the premise expected,
and it is the answer the DPO was asked to lead with.

## 4 · Decisions taken under DPO delegation

| # | Decision | Rationale | Reversible? |
|---|---|---|---|
| **DV-1** | "Consistency" = **six axes, no composite** | A composite needs weights; weights are a knob that turns until the premise is confirmed (**G9**) | Yes — axes are independent |
| **DV-2** | Cohort floor **≥8 GS in window**; start floor **≥15 PA** | Keeps the cohort to actual rotation members; stops a 2-inning ejection reading as volatility | Yes — two constants |
| **DV-3** | Breakpoint **2026-05-01**, stated not fitted, **scanned across 8** + full-season control | An era boundary is a researcher degree of freedom (**G6**, inherited from `uc-pps-027`) | Yes — one list |
| **DV-4** | ARI as a **lens**, not a co-equal study | DPO's explicit choice; there is no ARI hitter cache and a live pull adds an unpinned source to a governed build | Yes — fast-follow available |
| **DV-5** | Career H2H **tiered by recency** (`AR-1`), planning uses current-era only | 2019 Arizona is not tonight's Arizona (defect **D-3**) | Yes |
| **DV-6** | Known defects **O-5 / O-8 carried, not patched** | Patching a locked kernel function inside a use-case build is how kernels drift; both escalate instead | Yes — DPO ratifies the fix |
| **DV-7** | Battery split emitted as a receipt but **not narrated as a driver** | `uc-pps-027` TR-1 established this staff's approach changes are pitcher-level | Yes |
| **DV-8** | Two dashboard builds from one payload (offline vendored / published with webfonts) | The clubhouse copy must open with no network; the shared copy should read well | Yes |

## 5 · Rule-1 grep — "does this KPI already exist?"

Run before declaring anything new (full table in `01` §5). Locked and inherited **verbatim**:
`get_stats`, `nresults`, `whiff_rate`, `chase_rate`, `putaway_rate`, `fpsr`, `hard_hit_rate`,
`csw_rate`, `outs_and_runs`, `fip`, TTO / battery / count-leverage splits. **Method inherited:**
`TR-2` breakpoint scan. **Genuinely new:** `CN-1…CN-6` (no prior art — the nearest, `RF-2` rolling
form from `uc-pos-006`, is a *level* smoother, not a *range*) and `AR-1`.

## 6 · Defects found this run — all repo-wide patterns

| # | Defect | Reach |
|---|---|---|
| **D-1** | CDE completeness tested at pitch grain for elements defined at PA or BIP grain → two spurious FAILs | **Any DQ loop in this repo that checks null rates without declaring grain** |
| **D-2** | Replay-review prose prefixed to `des` contaminates modal batter-name parsing (returned the review clause as James McCann's name) | **Every `des`-parse H2H panel since UC11.** Sibling of `O-12` accent-folding |
| **D-3** | Team-keyed career H2H panel silently mixes eras (Nick Ahmed and Evan Longoria beside Ketel Marte) | **Every "vs \<club\>" use case in the ledger** |
| — | Zero delta labelled `DEGRADED` by a strict `<` comparison | This build; fixed |

All fixed in-build; **`O-5` and `O-8` deliberately left open** and disclosed in every artifact.

## 7 · Escalations to the human DPO

| # | Item | Why it needs a human |
|---|---|---|
| **E-1** | **Ratify or retire `CN-1…CN-6` and `AR-1`** | New KPIs enter the locked set only by DPO decision. CN-5 in particular measures a *joint* pitcher-and-manager behaviour, which the DPO may want scoped differently |
| **E-2** | **Adopt `G8` and `G9` as standing guardrails** | They generalise well past baseball; if adopted they change how every future superlative ask is scoped |
| **E-3** | **Paste the ledger patch** | Ledger drift is now ~7 patches deep |
| **E-4** | **Decide on `O-5` and `O-8`** | Both are locked-kernel fixes. `O-8` also has a ratified-but-unpasted sibling (`O-7` pull-air remediation) |
| **E-5** | **Promote the corrected categorical palette** | The repo's `PITCH_COLORS` fails two of the six accessibility checks; this build ships a passing set. A brand-guidelines change, not a build change |
| **E-6** | **Confirm tonight's Arizona lineup** | The single largest uncertainty in the product; the hitter panel is explicitly UNVERIFIED |
| **E-7** | **Promote a grain-aware completeness helper into the governed kernel** | D-1 is repo-wide and cost three re-runs here alone |

## 8 · Tripwires armed for the next run

| # | Tripwire | Re-check |
|---|---|---|
| **RB-1** | **K% ≥ 30% while hard-hit ≥ 36%.** The report's central conditional: the harder contact is only affordable while he misses bats. If K% falls toward 27% with hard-hit still high, the profile breaks | after 2 starts |
| **RB-2** | **Sinker usage to RHB.** 12.1% and falling; .404 xwOBA. Does it go to zero? | after tonight |
| **RB-3** | **Changeup retirement.** 20.3% → 14.3%; deliberate or drift? | after 3 starts |
| **RB-4** | **Pitch count.** 109 / 110 / 104 in his last three, season highs, on a career-high innings pace | every start |
| **RB-5** | **4-seam velocity** 97.1 → 96.3 across the break | after tonight |
| **RB-6** | **CN-1 rank on the full season** (currently 3rd). If it converges toward 1 as the sample grows, the boundary-dependence caveat weakens honestly | end of season |
