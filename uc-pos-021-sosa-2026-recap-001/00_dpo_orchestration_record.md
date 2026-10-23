# 00 · DPO Orchestration Record: `uc-pos-021-sosa-2026-recap-001`

**UC #56 · contract `uc-pos-021` · build `dp_uc56` v1.0.0 · delivered 2026-10-23 ET**
Value stream: Phillies Offense (`pos`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL (C1–C5)** · independently verified **161 / 161** · DQ **12 PASS / 5 WARN / 0 FAIL** · brand and claim checks 9 / 9 figures
Run: single turn. The RFP said to treat the bid as the winner, so the BID was filed and awarded at 14:04 ET and the build continued without a stop. **Third pos-side season recap**, and the first written as a possible **end-of-tenure** recap (the UC53 Alvarado framing applied to a hitter). **All code, receipts and deliverables live in this control-plane folder**; the MLB data plane was read, never written.

---

## 1 · The ask and how we framed it
The client submitted a notebook export (`acd30523-attachment.txt`, "Edmundo Sosa") headed "We really do Love Sosa". It asks:
- whether 2026 top-line results sit below his prior Phillies years, shown as cumulative wOBA/OPS lines with 2026 highlighted;
- whether there was an uptick through the year;
- whether he is "over-the-hump" or still a useful utility infielder, read through batted-ball indicators (Barrel, HH, muEV, EV50, EV90, maxEV, Pull AIR%);
- whether his high-chase, high-contact approach (chase, contact, out-of-zone contact, out-of-zone BA) is sustainable;
- whether he has fallen off against velocity or breaking balls;
- a walkaway contract number, explicitly delegated to web research.

Its code builds a season KPI panel on `pd.concat([nphl, pos])` and a Phillies-RHB swing-rate × wOBA scatter ("Edmundo swung the bat and had high wOBAs among Phillies RHB").

The organization read this as **six jobs**:
1. **Answer in the client's order**, one chapter each, ending on the walkaway.
2. **Inherit, don't re-derive.** Spine K55 (uc-pos-020) → K54 → K40 chain; CC-1 chase cost and `ooz_whiff_rate` (K54); ER-1 (K55); TR-1 (K54); `pull_air_rate` v1.1.0 (K46, uc-pos-017). The notebook's own `pull_air_rate` cannot run (O-7), which is why it is commented out.
3. **Pre-register the uptick test.** The media frame ("final 50 games, .806 OPS") was picked after the fact; TR-1 at the All-Star break was fixed in the BID.
4. **Separate results from skill.** Every "down year" claim is shown on results and on process (xwOBA, contact quality, bat speed).
5. **Make the walkaway a rule, not a vibe.** WA-1: band from carry-ins, term from six pre-registered decline flags computed on the data.
6. **Grade the client's claims on the client's own frame first** (HP-01…HP-11), then on the governed one.

## 2 · Delivery plan (departments actually engaged)
| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 6 gaps, 0 blocking (`01` §2) |
| | `source-system-profiler` | ID lock; SRC-4 (spring + WC rows in the client frame), SRC-5 (two-team frame), SRC-6 (2022 = 59 PA); sensor coverage |
| | `domain-steward-proxy` | 7 carry-ins (line, salary history, bWAR, comps, age, injury, Phillies career) via 8 web reads; CBA expiry noted |
| | `business-glossary-agent` | 2 new terms (OZ-1, WA-1); GL-1 (EV50 ambiguity) disclosed, client definition kept |
| Engineering Design | `data-architect` · `eda-agent` · `metadata-mapper` · `dashboard-specifier` | pitch-grain frames; EDA to file (`eda/dp_uc56/`, 2 reports); 8-chapter spec |
| Governance | `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` / `data-tagger` · `version-controller` | OZ-1 / WA-1 specs; lineage to `headlines.json`; privacy LOW (public-figure performance + public salaries); v1.0.0 |
| Engineering Build | `data-engineer` | kernel + build + HP + figures + report + dashboard in this folder; render stack `/tmp/pyrender` (ENV-3) |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` · `certification-agent` | 17 DQ rules; harness families A–N, 161 checks |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` / `product-narrator` | reading paths, FAQ, query templates (`06`) |
| Marketing | `brand-guardian` | brand + claim assertion on every figure; Artifact "Love Sosa" |
| Platform | `cost-watchdog` / `token-economist` | bid vs actual, calibration (`07`) |

**Not engaged:** `machine-learning-engineer` (no projection bid) · `join-validator` (single-grain frames; EN-2 fan-out assertion stands in) · `slide-builder` (no deck asked).

## 3 · Governance gate checks
| Gate | Result |
|---|---|
| G1 · Entity locked to MLBAM id | PASS: 624641 + batting role; one name; bats R in every row (harness B) |
| G2 · Rule-1 search before declaring anything new | PASS (`03` §0). OZ-1 and WA-1 had 0 hits; EV50 had no house definition (GL-1) |
| G3 · Locked KPIs inherited, not re-derived | PASS: K55 `9bdcce59…`, K46 `a45ac9a7…`, `barrel_rate.py` `6282f090…`, 16 files pinned in all |
| G4 · No re-derivation of existing work | PASS, with one governed amendment: WB-2 wrapper (`03` §4) |
| G5 · New KPIs specified before code | PASS: OZ-1 bars and WA-1 rule in the BID (14:04 ET); asserted unchanged (harness A) |
| G6 · Every published number from a receipt | PASS: narrative module formats from `headlines.json`; harness M |
| G7 · Carry-ins labelled, never computed on | PASS: CI-1…CI-7 labelled in the report (harness M); WA-1 band is disclosed carry-in arithmetic |
| G8 · Privacy before any external surface | PASS (internal): LOW (`03` §6) |
| G9 · Certification | READY-CONDITIONAL, conditions below |

## 4 · Arguments the organization had (and how they were settled)
- **"Is it fair to call 2026 a down year when xwOBA was his best?"** Both are true. Settled: the report leads with "a down year in results, not in the bat" and shows both on every chart that could be read either way (F2, F3, F4).
- **"The uptick is real - he hit .806 OPS over his last 50 games."** The results moved; the process didn't. TR-1 (fixed date) returns RESULTS TURN with xwOBA, K%, hard-hit and whiff all moving the wrong way. Settled: report the media frame as a reconciled receipt (.787 OPS over his last 50 games with a PA), never as a test.
- **"Was he worse against breaking balls?"** No; he was never good against them, and 2026 was his best expected year. Graded CONTRADICTED (HP-07). Render QA forced the F6 title off "the hole was offspeed" because offspeed xwOBA actually rose; the swing-and-miss is the finding (Q-2).
- **"Should the walkaway reward a 0-flag bat with more than comp money?"** No. The walkaway prices the role (bench, platoon vs LHP), and the comps are bench deals. Flags set the term, not the AAV.
- **"Which wOBA for pooled baselines?"** The harness found the inherited function weights pooled seasons with 2026 constants (WB-2). Settled: K56 wraps it so pooled wOBA is per-season-weighted; single-season numbers are unchanged; deltas logged.

## 5 · Escalations to the human DPO
1. **WB-2 (inherited, new):** `nresults_unrounded` (K40 → K54) uses 2026 wOBA constants whenever `game_year` is not in the level. Every multi-season pooled wOBA published by UC34–UC55 that used a level without `game_year` is affected by up to ~.003 here. Recommend a v1.1 of the K54 spine and a sweep of prior packages. Not patched upstream (outside this UC's write scope).
2. **CL-2 (client code):** `inds` `ev_mu` averages `launch_speed` over every tracked pitch, fouls included (2026: 81.7 vs 87.5 mph on BIP).
3. **Ledger patches pending:** UC52–UC55 patches are still unpasted. This patch claims #56 and names #57 next.
4. **Contract decision is the DPO's.** WA-1 is a framework, not advice; the CBA expiry (CI-2) is unpriced.

## 6 · Certification conditions (READY-CONDITIONAL)
- **C1:** WA-1 is quoted with its basis ("top 2025-26 utility comp AAV; term from six decline flags") and the words "not a valuation model".
- **C2:** TR-1 is quoted as a direction call on 162 vs 88 PA, never as a size estimate.
- **C3:** Pitch-group results (28–83 PA per cell) are never quoted without PA.
- **C4:** EV50 is always labelled "median EV (client definition)".
- **C5:** Pooled wOBA figures in this package use the WB-2 wrapper. If the K54 spine ships a v1.1 fix, re-run; numbers should not change.
