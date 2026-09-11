# BID ADDENDUM — `uc-pos-016` revision (`dp_uc42a` v1.1.0)

**Date:** 2026-09-10 · **Status:** *unsolicited — no RFP was issued for this revision* · **Priced retrospectively**

## Why this file exists

The v1.1.0 revision arrived as a direct improvement request against a delivered product, not as a competitive
RFP. It was built and delivered without a bid. This file prices it retrospectively, because an unbid revision
that never gets costed is how a delivery practice loses its calibration — and because the next revision in
this pairing should have a number agreed *before* it starts.

## What was asked

1. More interactivity than v1.0.0's single-toggle dashboard.
2. Different methods of telling the story, staying strictly inside what is factually in the data.
3. A true balls-in-play spray chart — a human-in-the-loop specification correction the DPO declared himself.
4. Animation, framed around a single grain identified in the rug on the x-axis margin.
5. Iterate on the delivered package, especially the governance deliverables.

## What it cost

| Phase | Input | Output |
|---|---|---|
| R0 Intake + parent reproduction | ~55k | ~4k |
| R1 Environment (bridge down, egress locked, folder access) | ~15k | ~2k |
| R2 Data layer (7 verbatim transcriptions, 6 new objects, PM-1, DC-1) | ~60k | ~22k |
| R3 Dashboard (3 templates, 5 scenes, 4 render-correction passes) | ~85k | ~30k |
| R4 Plotly notebook script (shipped untested) | ~15k | ~8k |
| R5 Verification (155 checks, 6 families) | ~25k | ~12k |
| R6 Governance amendment (00–07, README, report, ledger reissue) | ~45k | ~30k |
| **Total** | **~300k** | **~108k** |

**~2h05m wall clock · indicative ~$9.90 at the v1.0.0 bid's rates · ~1.7× the v1.0.0 delivery.**

## What the next bid in this pairing should look like

| Line item | Why it needs to be named separately |
|---|---|
| **Parent reproduction** | A fixed cost incurred before any new work begins. It is not intake and it is not analysis. |
| **Cold intake + environment verification** | v1.0.0's recommendation, still right. |
| **Broken device bridge + egress-locked sandbox** | **Move from contingency to base case.** Two consecutive sessions, identical failure. Price the working case as upside. |
| **Data-plane folder access** | Request it as the first action of intake. v1.0.0 shipped a narrower product for not having it. |
| **Governance amendment** | On a revision this runs ~28% of output tokens, because the amendment must argue against the parent as well as extend it. On a new UC it is a smaller share. |
| **Untestable dependencies** | If a deliverable needs a library the sandbox cannot install, either descope it or ship it explicitly untested and say so. `dp_uc42a_context_animation.py` is the latter. |

## Reconciliation

Recorded in `07_platform_marketing.md` §Bid vs. actual, with four calibration findings.
