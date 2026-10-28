# 00 | DPO Orchestration Record: `uc-pos-023-schwarber-2026-hr-animation-001`

**UC #58 | contract `uc-pos-023` | build `dp\_uc58` | BID filed 2026-10-27 19:49 ET**
Value stream: Phillies Offense (`pos`) | Human DPO: Kellen Short
Status: **RELEASED v1.0.1 2026-10-27 ≈23:20 ET ([Release Sign-Off v1.0.1](RELEASE_SIGNOFF_2026-10-27_uc-pos-023_v1.0.1.md)) | READY-CONDITIONAL (C1–C7, `05`) | harness 31/31 | DQ 10/3/0.** v1.0.0 delivered ≈20:13 ET. Single chat, no hard stop (RFP: "consider the bid a winner … proceed"). **First Claude Design handoff UC**; third Schwarber product of 2026 (after UC21, UC33). Code and outputs live at the MLB root; this folder holds the trail plus copies of the deliverables (`data/`, `keyframes/`).

\---

## 1 | Framing the Ask

The client submitted `Schwarber\_2026\_Home\_Runs.md`. It storyboards an animated segment for the larger Schwarber 2026 recap video: Claude Design animates, and the client splices Savant clips. It includes his reference Python and a highlight shortlist. At intake (this chat) the DPO set three things: the technical overview assesses our existing Python; the prompt carries real governed numbers; the run covers intake, bid and the tech brief, then the RFP extended it to the full 00–07 build.

The organization read this as five jobs:

1. **Govern the pictures, not just the numbers.** Every on-screen string is templated from a receipt; the prompt's DATA block is the design data, byte-for-byte (V24).
2. **Choose highlights by rule.** HL-1 was fixed before looking, so the "max EV" and "max WPA" stops are reproducible, and the client's picks are graded against them.
3. **Grade the notebook.** 15 HP rows on the client's own words.
4. **Assess the Python honestly.** It is fit as a data engine after six fixes. It is not fit as a renderer.
5. **Hand off to a model.** The prompt gives Claude Design rules, tokens, a transition grammar, a segment/clip map, a self-check and keyframes, so it never has to ask back.

## 2 | Delivery Plan

|Phase|Departments|Output|
|-|-|-|
|T0|use-case-validator, source-system-profiler, domain-steward-proxy, business-glossary-agent, token-economist|`01`, BID|
|T1|data-architect, kpi-calculator, eda-agent, join-validator, data-engineer, technical-lineage-builder|`02`, `04`; kernel + build; HP grades; clip list; design data|
|T2|dashboard-specifier (motion), dataviz validation|8 keyframes, brand tokens|
|T3|analytics-enabler, data-architect (brief)|Claude Design prompt; feasibility brief|
|T4|data-quality-engineer, certification-agent|`05`; harness 28/28|
|T5|business-glossary-agent, metadata-mapper, data-dictionary, data-tagger, consumer-onboarding-agent, query-builder, version-controller, privacy-watchdog, data-observability, cost-watchdog|`03`, `06`, `07`, README, contract, ledger patch|

Not engaged: machine-learning-engineer (no prediction), semantic-modeler (no new semantic layer beyond HB-1).

## 3 | Governance gate checks

|Gate|Status|
|-|-|
|Use case validated (0 blocking gaps)|PASS (`01` §2, 10 non-blocking)|
|Entity lock by MLBAM id|PASS (656941, both sources, 0 duplicate keys)|
|Inherited lineage pins|PASS (18 unique files)|
|No CDE inference|PASS (all definitions consumed or pre-registered in the BID; HB-1 named apart from barrel rate)|
|Data anchor pinned|PASS (2026-10-01, sha `be5d313d…` unchanged)|
|Harness|PASS 28/28|
|Certification|READY-CONDITIONAL (C1–C7)|
|Privacy|Clear (public-figure data)|
|Publish|**APPROVED by the DPO (2026-10-27 22:53 ET): [Release Sign-Off v1.0.1](RELEASE_SIGNOFF_2026-10-27_uc-pos-023_v1.0.1.md)**|

## 4 | Arguments the organization had (and how they were settled)

* **Python animatic or data-only handoff?** The dashboard-specifier wanted a plotly animatic to "prove" the timing. The data-architect argued the client's own plotly path is the thing the brief rates unfit as a renderer, so shipping one would muddy the verdict. **Settled:** static keyframes in Tier A; animatic as Tier B.
* **Impute the two missing spray coordinates?** A nearest-neighbour bearing from similar-EV/LA balls was floated. **Rejected:** that's inference. SP-2 uses only what the play's own `des` text says, and marks the dot hollow.
* **LHP clips: fastballs or breaking balls?** The client's text and code disagree (G1). **Settled:** fastball clips (text) plus the breaking-ball beat (code). Both are in the cut; the DPO can flip.
* **Fix `cumulative\_metric` in place?** It is pinned and used by other products. **Settled:** wrap it here (DH-1, PA-X1); propose v1.1 to the DPO (`07` §1).

## 5 | Escalations

1. ~~**Publish:** approve the video for external use once Claude Design returns.~~ **Closed 22:53 ET:** BID + materials approved, video accepted ([Release Sign-Off v1.0.1](RELEASE_SIGNOFF_2026-10-27_uc-pos-023_v1.0.1.md)).
2. **G1:** confirm lefty fastball clips, not breaking balls.
3. **Clip 7** duplicates clip 4 (same homer). Reuse it, or swap in 5/9 vs COL (110.8 mph).
4. **`cumulative\_metric` v1.1** (DH-1 `order=`, PA-X1 default): approve as a breaking-by-value change.
5. **Ratify** HB-1, WP-1, HL-1, SP-1/2/3, PM-1, GR-1, DH-1.
6. **Ledger:** paste UC52–UC58 patches, oldest first.
7. **Housekeeping:** delete `MLB/out/\_to\_delete/dp\_uc58\_hp\_grades\_partial.csv` (deletes aren't permitted from this session).

## 6 | Delivery Summary

* **What the build found:** 45 HR (tied for the MLB lead, CI-1), 4th of 12 seasons. They were the softest, shortest and most-pulled homers of his five Phillies seasons, with 13 of 15 off lefties on fastballs. The client's notes hold up: 13 of 15 SUPPORTED (one with condition), HP-08 PARTLY (1st inning, not 9th), HP-06 NOT SUPPORTED on the count leg.
* **What the build fixed:** CP-1 (pitches → PA), DH-1 (doubleheader order), WP-1 (road HRs), SP-2 (two missing coordinates, one the longest homer), PM-size, SRC-D guard.
* **Bid vs actual:** ≈310k tokens / ≈34 min vs ≈400k / 45 min (−22% / −24%), `07` §5.

## 7 | Release v1.0.1 (post-award, DPO edits applied)

* **Trigger:** DPO approval, 2026-10-27 22:53 ET: BID + supporting materials APPROVED with edits; BID awarded for the full build; Claude Design video accepted.
* **DPO edits read back in:**
  * `00`–`07` (heading names, `|` separators, publish gate);
  * K1 markup: Title Case title, subtitle cut after "2021".
* **What the organization did with them:**
  * generalized the K1 markup into **ST-1** (Title Case titles, context-only subtitles) across all 8 keyframes and the prompt;
  * added **COPY-1**, one copy deck feeding both, so keyframe and prompt copy cannot drift;
  * extended the harness to **31/31**.
* **Data unchanged** (`design\_data.json` sha `e8de66ca…`; house log sha `be5d313d…`, anchor 2026-10-01).
* **Sign-off:** [Release Sign-Off v1.0.1](RELEASE_SIGNOFF_2026-10-27_uc-pos-023_v1.0.1.md). Open after release: G1/clip 7 (defaults used in the approved cut), house promotion of the provisional rules, `cumulative\_metric` v1.1, ledger paste, `\_to\_delete/` housekeeping.
