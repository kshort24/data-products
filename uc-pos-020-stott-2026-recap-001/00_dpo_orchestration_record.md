# 00 · DPO Orchestration Record: `uc-pos-020-stott-2026-recap-001`

**UC #55 · contract `uc-pos-020` · build `dp_uc55` · v1.0.0 · delivered 2026-10-22 ET**
Value stream: Phillies Offense (`pos`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL (C1–C5)** · independently verified **185 / 185** · DQ **15 PASS / 5 WARN / 0 FAIL** · brand and claim checks 10 / 10 figures
Run: single turn. The RFP said to treat the bid as the winner, so the BID was filed and awarded at 19:27 ET and the build continued without a stop. **This is the second pos-side season recap.** It reuses the K54 recap shape (C-7) and is the first recap whose code lives in the data plane under an RFP that said "work inside the MLB repository".

---

## 1 · The ask and how we framed it
The client submitted a notebook export (`d8b91d3b-attachment.txt`, "Bryson Stott") that opens with a thesis: "Is there another level to unlock for him? I don't believe it." It contains:
- four questions: other way / all fields; line drives or fly balls; lefties, righties and pitch types; chasing less and walking
- three hand-set "Good" eras: early 2023, 2025 second half, summer 2026
- code for a season KPI panel, a Good/Bad A/B test, platoon and pitch-group splits, a velocity split, and an attack-direction exploration
- two notes for the organization: (1) "a better way to determine timeframes for Good or Bad"; (2) defense, meaning consolidate 2B and 3B, compare 2B with prior years, decide whether 3B could be full time, and check the "limited thump" that would follow

The session opened with the client's data-dictionary card for six bat-path and delivery CDEs. That card's open questions (sign convention, axis, availability) are in scope wherever they inform the answer.

The organization read this as **six jobs**:
1. **Answer the questions in the client's order**, one chapter each, with defense as its own chapter.
2. **Inherit, don't re-derive.**
   - The recap spine is K54 (uc-pos-019).
   - The bat-path semantics come from K40a (uc-pos-014 v1.1.0). It already proves that `attack_direction` is pull-negative and stand-normalised (O-15), which settles the sign question left open on the data-dictionary card.
   - Stott's own prior read is uc-pos-010 (dp_uc33).
3. **Build the timeframe tool the client asked for, and pre-register it.** ER-1 is permutation-tested change-point eras, and its parameters were written into the BID before any era split was computed.
4. **Make the A/B test fair.** GS-1 uses ten process signatures with bars. It scores process only, because the eras were chosen on results, and it runs on both the client's eras and the ER-1 eras.
5. **Rebuild the client's charts, not just restyle them.**
   - The cumulative wOBA/OPS request becomes the house cumulative-chart skill's ghost lines.
   - The attack-angle × attack-direction scatter becomes a population density with the governed middle-65% band and the sign flipped so pull reads right.
   - The Good/Bad tables become a signature dumbbell.
6. **Grade the client's claims on the client's own frame first** (HP-01…HP-14), then on the governed one.

## 2 · Delivery plan (departments actually engaged)
| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 7 gaps, 0 blocking (`01` §2) |
| | `source-system-profiler` | ID scan; SRC-4 (client frame carries 182 non-regular PA, including 37 spring and 3 exhibition PA in 2026); sensor boundaries; defensive opportunity counts by position |
| | `domain-steward-proxy` | 6 carry-ins (2026 line, OAA/DRS at 2B and 3B, the 2025 stance change, the Arraez move and Dombrowski's stance, career 2B, Bohm's contract year); SHIFT-1 (2023 shift rules bound the IO-1 pool) |
| | `business-glossary-agent` | 3 new terms (ER-1, GS-1, IO-1); BP-0/BP-1, O-15, DR-1, CR-1, PA-1 consumed |
| Engineering Design | `data-architect` · `eda-agent` · `metadata-mapper` · `dashboard-specifier` | pitch-grain frames; EDA to file (3 reports, MLB `eda/dp_uc55/`); 7-chapter spec keyed to the client's questions |
| Governance | `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` / `data-tagger` · `version-controller` | ER-1/GS-1/IO-1 specs (`03` §2); lineage to `headlines.json`; privacy LOW–MODERATE; v1.0.0 |
| Engineering Build | `data-engineer` | code and outputs in the MLB data plane (RFP); render stack `/tmp/pyrender`, `TMPDIR=/tmp/uc55/tmp` (ENV-3); 82 receipts in `out/` |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` · `certification-agent` | 20 DQ rules; harness families A–L, 185 checks |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` / `product-narrator` | reading paths, FAQ, ER-1 notebook cell, catalog entry (`06`) |
| Marketing | `brand-guardian` | brand + claim assertion on every figure; palette validated (PG-1 light and dark) |
| Platform | `cost-watchdog` / `token-economist` | bid vs actual, calibration, tripwires (`07`) |

**Not engaged:**
- `machine-learning-engineer`: no projection was bid.
- `join-validator`: single-grain frames; the EN-2 fan-out assertion stands in.
- `slide-builder`: no deck was asked for.

## 3 · Governance gate checks
| Gate | Result |
|---|---|
| G1 · Entity locked to MLBAM id | PASS: 681082 + batting role (`fielder_4`/`fielder_5` on defense). One name, one id (harness B) |
| G2 · Rule-1 search before declaring anything new | PASS (`03` §0). Hits: K54, K40a (bat path), K44 + IX-1 (client functions), UC5 (infield proxy precedent), XO-2 (neighbour machinery), dp_uc33. Era detection, era signatures and infield expected outs had 0 hits |
| G3 · Locked KPIs inherited, not re-derived | PASS: K54 `1a31b30a…` (12 more pins through it), K40a `807986c0…` |
| G4 · No re-derivation of existing work | PASS: slash, wOBA, xwOBA, chase/whiff, HH/barrel, CR-1, DR-1, RF-2, CM-1, BP-1, KP-1, PA-1 all imported |
| G5 · New KPIs specified before code | PASS: ER-1 and GS-1 parameters in the BID (19:27 ET), asserted unchanged (harness A, 19 checks). IO-1's pool (A-1) and neighbourhood (A-2) were amended after coverage gates failed; both are disclosed (`03` §2) |
| G6 · Every published number from a receipt | PASS: the narrative module formats from `headlines.json`; harness F, 18 checks |
| G7 · Carry-ins labelled, never computed on | PASS: harness G, 5 checks |
| G8 · Privacy before any external surface | PASS (internal): LOW–MODERATE (`03` §6) |
| G9 · Certification | READY-CONDITIONAL, conditions below |

## 4 · Arguments the organization had (and how they were settled)
- **"ER-1 found no eras. Is that a failed product?"** No. The client asked for a better way to set timeframes, and the honest answer is that at one season of PA no wOBA change point separates from variance. The power receipt shows what the tool *could* have found: a .080 step 50% of the time, a .120 step 79%. Settled: publish the null result, the power, and the hindsight-corrected p for each of the client's eras. Ship the notebook cell anyway so the client can rerun it on any player.
- **"Is 2B really a down year when OAA says +8?"** IO-1 reads −9 (sign stable across v1–v4) and agrees with DRS (−9). Settled: publish the proxy beside both carry-ins, never blended, and say it disagrees with OAA.
- **"Can we say he should move to 3B?"** No. 82 chances, the sign flips with neighbourhood width, and the front office has said it isn't the plan (CI-3). Settled: grade HP-12 **OPEN**, show the comparison with Bohm (proxy), and answer the thump question with data (HP-13).
- **"F7's title said every pitch group improved."** Render QA caught it: offspeed from RHP and breaking balls from LHP did not improve. Settled: the title now says Good eras were fastball eras, and the claim assertion tests the pitch-group pattern, not just the two hands (Q-2).
- **"Which wOBA?"** House wOBA (K40 weights) for every line and rank, and ER-1's primary basis. ER-1x uses XW-1's atom. The two are never mixed in one comparison.

## 5 · Escalations to the human DPO
1. **ENV-4 (platform, new):** the device commit tool served a cached copy when the same staged path was committed twice, so the first two re-runs executed stale code. It was caught by grepping for the edit before every run. Workaround: versioned staged filenames. Worth a platform ticket.
2. **CL-1 (client code):** the attack-direction block computes `std` as a mean and groups on the value itself. Graded in HP-10, not fixed in the notebook (the client's file).
3. **Ledger patches pending:** UC52–UC54 patches are still unpasted. This patch claims #55 and names #56 next.
4. **O-16 (inherited):** swing-path tilt fell team-wide 2025 → 2026 (median −1.2°). It is not compared year over year here; the calibration question stays open.

## 6 · Certification conditions (READY-CONDITIONAL)
- **C1:** IO-1 is a proxy. Any external use carries the "proxy" label and the OAA/DRS carry-ins beside it. The 3B result is never quoted without its sign-instability note.
- **C2:** ER-1 "no split" is quoted as "no change large enough to separate from variance", with the power figure. It is never quoted as "nothing changed".
- **C3:** GS-1 results families (wOBA, BA, BABIP) are reported, never scored, because the eras were chosen on results.
- **C4:** The 2025 stance change is a carry-in date. Bat-path changes around it are descriptive, not causal, and the depth climb started in June 2025, before the break.
- **C5:** The A-1/A-2 IO-1 amendments stand as disclosed. If a v1.1 restores the BID pool definition, the 2B numbers are re-run, not patched.
