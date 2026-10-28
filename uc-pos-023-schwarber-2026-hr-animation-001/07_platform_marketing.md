# 07 | Platform \& Marketing

**version-controller | privacy-watchdog | data-observability | cost-watchdog | token-economist**
`uc-pos-023-schwarber-2026-hr-animation-001` | UC #58 | `dp\_uc58` v1.0.0

## 1 | Version (version-controller)

`dp\_uc58` **v1.0.1** (copy-only, **non-breaking**) supersedes v1.0.0. ST-1/COPY-1 changed titles and subtitles only; the data is byte-identical. See [Release Sign-Off v1.0.1](RELEASE_SIGNOFF_2026-10-27_uc-pos-023_v1.0.1.md). v1.0.0 was the first release. Nothing upstream changed: the inherited kernels are imported and pinned, never edited. The proposed `cumulative\_metric` v1.1 (DH-1 `order=`, PA-X1 default) would be a **behavioural change for every house cumulative chart**. Classify it as breaking-by-value (DH-day step positions; PA counts in seasons with runner-out rows) and get the DPO's acknowledgement before it ships.

## 2 | Privacy (privacy-watchdog)

Public-figure performance data and public game facts only. No PII, no quasi-identifiers. Clear for external publish (the video) once the DPO approves. Carry-ins quote public reporting (CI-1…CI-4) and are attributed.

## 3 | Observability (data-observability): tripwires

|Tripwire|Action|
|-|-|
|House log passes the 2026-10-01 anchor (WC Game 3 or later rows land)|Build refuses to run; re-pin and re-verify; the WC postscript may gain rows|
|`cumulative\_metric` sha changes|Lineage fails closed; re-run the harness; drop the DH-1/PA-X1 wrappers if v1.1 absorbs them|
|Statcast backfills `hc\_x/hc\_y` on the two SP-2 homers|DQ-05 flips to PASS; dots turn solid; v1.0.1 (non-breaking)|
|Claude Design returns segments|Check each against the prompt §6 self-check and the keyframes before splicing|
|Parent Schwarber recap UC opens|It inherits `hr\_quality\_by\_season`, `spray\_by\_season`, HP-01…05 by import, not re-derivation|

## 4 | Cost (cost-watchdog)

The full rebuild takes ≈ 25 s on device and is deterministic. The only expensive step is keyframe rendering (kaleido, ≈ 15 s for 8 frames). No recomputation across scripts: keyframes and prompt read receipts only.

## 5 | Bid vs Actual (token-economist)

Counter = session tokens-left (context consumed). Bid filed 19:49 ET; build ran in this chat with no hard stop.

|Mark|When|Counter|Cumulative|
|-|-|-|-|
|C0|Turn start|15,000,000|0|
|C3|BID, `00`(draft), `01` filed|14,870,096|130k|
|C4|T1 build + DH-1 fix + names|14,803,110|197k|
|C5|T2 dataviz validation + 8 keyframes + QA|14,760,601|239k|
|C6|T3 prompt + feasibility brief|14,738,535|261k|
|C7|T4 harness 28/28|14,726,715|273k|
|C8|T5 `02`–`06`, contract, ledger patch, copies|14,707,991|292k|
|C9|`07`, `00`, README, project doc (est. at write)|≈14,690,000|**≈310k**|

|Phase|Bid (in+out)|Actual|Δ|
|-|-|-|-|
|T0 + BID|142k|130k|−8%|
|T1 build (+ D defect discovery)|84k|67k|−20%|
|T2 keyframes|54k|42k|−22%|
|T3 prompt + brief|43k|22k|−49%|
|T4 harness|25k|12k|−52%|
|T5 governance|38k|≈37k|−3%|
|Contingency|13k|0||
|**Total**|**≈400k / 45 min**|**≈310k / ≈34 min** (19:39 → ≈20:13 ET)|**−22% tokens \| −24% time**|

**Calibration note:** T3 and T4 were over-bid. Templating the prompt from receipts made the narrative cheap, and the harness re-used the receipts' shapes. T1 absorbed two unplanned defects (DH-1, PA-X1) and still came in under. Within the UC48–UC57 band (−28% to +9%). Next handoff UC: bid T3 at ≈25k and T4 at ≈15k.

## 6 | Marketing Line (for the DPO's use)

> An agentified organization took a notebook of half-finished plotly sketches and turned it into a governed motion brief for Claude Design. Every number on screen traces to a receipt. The highlights were chosen by rules written before anyone looked. The client's own notes were graded, never overwritten. Along the way the team of agents found that the sketch's x-axis counted pitches, not plate appearances, and that the house cumulative engine has run doubleheaders in the wrong order. Both are fixed, both are documented, and the run cost about 310k tokens in 34 minutes.

## 7 | Post-award Telemetry (token-economist), v1.0.1

|Mark|When|Counter|Cumulative (this session)|
|-|-|-|-|
|R0|Session start (approval message, 22:53 ET)|15,000,000|0|
|R1|Re-read edited `00`–`07` + K1 markup; tripwire check (house log rewritten, sha unchanged)|14,966,543|33k|
|R2|ST-1/COPY-1 applied, keyframes + prompt rebuilt, harness 31/31|14,975,539 (counter refreshed after Q&A)|≈58k|
|R3|Sign-off, receipts, copies, project doc|≈14,955,000 (est.)|**≈78k**|

Not in the original BID: post-approval revisions are a separate line item. Calibration: **≈78k / ≈30 min for a copy-only re-release**, about 20% of the original build. Price future DPO-edit passes at ≈80k.
