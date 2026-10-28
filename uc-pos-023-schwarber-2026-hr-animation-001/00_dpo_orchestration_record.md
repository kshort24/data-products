# 00 · DPO Orchestration Record: `uc-pos-023-schwarber-2026-hr-animation-001`

**UC #58 · contract `uc-pos-023` · build `dp_uc58` · BID filed 2026-10-27 19:49 ET**
Value stream: Phillies Offense (`pos`) · Human DPO: Kellen Short
Status: **DELIVERED 2026-10-27 ≈20:13 ET · READY-CONDITIONAL (C1–C7, `05`) · harness 28/28 · DQ 10/3/0.** Single chat, no hard stop (RFP: "consider the bid a winner … proceed"). **First Claude Design handoff UC**; third Schwarber product of 2026 (after UC21, UC33). Code and outputs live at the MLB root; this folder holds the trail plus copies of the deliverables (`data/`, `keyframes/`).

---

## 1 · The ask and how we framed it
The client submitted `Schwarber_2026_Home_Runs.md`. It storyboards an animated segment for the larger Schwarber 2026 recap video: Claude Design animates, and the client splices Savant clips. It includes his reference Python and a highlight shortlist. At intake (this chat) the DPO set three things: the technical overview assesses **our existing Python**; the prompt carries **real governed numbers**; the run covers intake, bid and the tech brief, then the RFP extended it to the full 00–07 build.

The organization read this as **five jobs**:
1. **Govern the pictures, not just the numbers.** Every on-screen string is templated from a receipt; the prompt's DATA block is the design data, byte-for-byte (V24).
2. **Choose highlights by rule.** HL-1 was fixed before looking, so the "max EV" and "max WPA" stops are reproducible, and the client's picks are graded against them.
3. **Grade the notebook.** 15 HP rows on the client's own words.
4. **Assess the Python honestly.** It is fit as a data engine after six fixes. It is not fit as a renderer.
5. **Hand off to a model.** The prompt gives Claude Design rules, tokens, a transition grammar, a segment/clip map, a self-check and keyframes, so it never has to ask back.

## 2 · Delivery plan (departments engaged)
| Phase | Departments | Output |
|---|---|---|
| T0 | use-case-validator, source-system-profiler, domain-steward-proxy, business-glossary-agent, token-economist | `01`, BID |
| T1 | data-architect, kpi-calculator, eda-agent, join-validator, data-engineer, technical-lineage-builder | `02`, `04`; kernel + build; HP grades; clip list; design data |
| T2 | dashboard-specifier (motion), dataviz validation | 8 keyframes, brand tokens |
| T3 | analytics-enabler, data-architect (brief) | Claude Design prompt; feasibility brief |
| T4 | data-quality-engineer, certification-agent | `05`; harness 28/28 |
| T5 | business-glossary-agent, metadata-mapper, data-dictionary, data-tagger, consumer-onboarding-agent, query-builder, version-controller, privacy-watchdog, data-observability, cost-watchdog | `03`, `06`, `07`, README, contract, ledger patch |

Not engaged: machine-learning-engineer (no prediction), semantic-modeler (no new semantic layer beyond HB-1).

## 3 · Governance gate checks
| Gate | Status |
|---|---|
| Use case validated (0 blocking gaps) | PASS (`01` §2, 10 non-blocking) |
| Entity lock by MLBAM id | PASS (656941, both sources, 0 duplicate keys) |
| Inherited lineage pins | PASS (18 unique files) |
| No CDE inference | PASS (all definitions consumed or pre-registered in the BID; HB-1 named apart from barrel rate) |
| Data anchor pinned | PASS (2026-10-01, sha `be5d313d…` unchanged) |
| Harness | PASS 28/28 |
| Certification | READY-CONDITIONAL (C1–C7) |
| Privacy | Clear (public-figure data) |
| Publish | **DPO decision** (the video is external) |

## 4 · Arguments the organization had (and how they were settled)
- **Python animatic or data-only handoff?** The dashboard-specifier wanted a plotly animatic to "prove" the timing. The data-architect argued the client's own plotly path is the thing the brief rates unfit as a renderer, so shipping one would muddy the verdict. **Settled:** static keyframes in Tier A; animatic as Tier B.
- **Impute the two missing spray coordinates?** A nearest-neighbour bearing from similar-EV/LA balls was floated. **Rejected:** that's inference. SP-2 uses only what the play's own `des` text says, and marks the dot hollow.
- **LHP clips: fastballs or breaking balls?** The client's text and code disagree (G1). **Settled:** fastball clips (text) plus the breaking-ball beat (code). Both are in the cut; the DPO can flip.
- **Fix `cumulative_metric` in place?** It is pinned and used by other products. **Settled:** wrap it here (DH-1, PA-X1); propose v1.1 to the DPO (`07` §1).

## 5 · Escalations to the human DPO
1. **Publish:** approve the video for external use once Claude Design returns.
2. **G1:** confirm lefty fastball clips, not breaking balls.
3. **Clip 7** duplicates clip 4 (same homer). Reuse it, or swap in 5/9 vs COL (110.8 mph).
4. **`cumulative_metric` v1.1** (DH-1 `order=`, PA-X1 default): approve as a breaking-by-value change.
5. **Ratify** HB-1, WP-1, HL-1, SP-1/2/3, PM-1, GR-1, DH-1.
6. **Ledger:** paste UC52–UC58 patches, oldest first.
7. **Housekeeping:** delete `MLB/out/_to_delete/dp_uc58_hp_grades_partial.csv` (deletes aren't permitted from this session).

## 6 · Delivery summary
- **What the build found:** 45 HR (tied for the MLB lead, CI-1), 4th of 12 seasons. They were the softest, shortest and most-pulled homers of his five Phillies seasons, with 13 of 15 off lefties on fastballs. The client's notes hold up: 13 of 15 SUPPORTED (one with condition), HP-08 PARTLY (1st inning, not 9th), HP-06 NOT SUPPORTED on the count leg.
- **What the build fixed:** CP-1 (pitches → PA), DH-1 (doubleheader order), WP-1 (road HRs), SP-2 (two missing coordinates, one the longest homer), PM-size, SRC-D guard.
- **Bid vs actual:** ≈310k tokens / ≈34 min vs ≈400k / 45 min (−22% / −24%), `07` §5.
