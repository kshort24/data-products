# 00 · DPO Orchestration Record: `uc-pos-019-crawford-2026-recap-001`

**UC #54 · contract `uc-pos-019` · build `dp_uc54` · v1.0.0 · delivered 2026-10-20 ET**
Value stream: Phillies Offense (`pos`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL (C1–C5)** · independently verified **157 / 157** · DQ **12 PASS / 4 WARN / 0 FAIL** · brand and claim checks 10 / 10 figures
Run: single turn. The RFP said to treat the bid as the winner, so the BID was filed and awarded at 23:18 ET and the build continued without a stop. The house-format skill was loaded first. **This is the first pos-side season recap**; it sets the pos recap shape that UC48–UC53 set for pitchers.

---

## 1 · The ask and how we framed it
The client submitted a notebook export (`a4523113-attachment.txt`, "Justin Crawford") with six questions and code:
- top-line results
- pitch-group chase/whiff by hand
- in/out-of-zone splits
- RHP pitch-mix and mean-location scatter
- RHP breaking-ball tables
- an EV box plot, a hit pitch map and a spray chart faceted AAA 2025 vs MLB 2026
- a similar-hit expected-outs read of his centre-field defense

The RFP asked for:
- **good visuals**: cumulative line graphs and cleaner versions of the client's own plots, "rather than fairly lame bar charts and simple line graphs"
- governed, documented output with 00–07 receipts
- scouting-report-skill inspiration
- data-plane coding standards
- outputs in a new control-plane folder
- a bid with token and time estimates

The organization read it as **five jobs**:
1. **Answer the six questions in the client's order**, one chapter each, with Q4 (improvement) split into the walk path and the righty-spin study.
2. **Inherit, don't re-derive.** The pos spine is K40 (uc-pos-014). This player's own YTD read, uc-pos-011 / K34, supplies the CX-1 centre-field pool and the "requester breakpoints are outcome-selected" lesson. The cumulative module (CM-1) draws the lines.
3. **Make "better from June 1" falsifiable.** TR-1, ten signatures with bars, was written into the BID before any split was computed.
4. **Rebuild the client's charts, not just restyle them.** The mean-location scatter becomes a chase map with the mean marked. The EV box becomes a box-plus-points by pitch type. The hit pitch map gains the UC22 heart region. The spray chart goes onto a drawn field at CBP dimensions with the house DR-1 boundaries.
5. **Grade the client's defense method on its own terms first** (HP-13), then show what it cannot see (DEF-3).

## 2 · Delivery plan (departments actually engaged)
| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 6 gaps, 0 blocking (`01` §2) |
| | `source-system-profiler` | id scan; found ENT-2 (wrong Crawford file), SRC-1 (client frame game types), SRC-2 (3 duplicate MLB rows in an opponent file), SRC-3 (AAA tier) |
| | `domain-steward-proxy` | 4 carry-ins (debut, final line + OAA/DRS + platoon role, early-season OAA + sprint speed, AAA 2025 line) |
| | `business-glossary-agent` | 3 new terms (TR-1, CC-1, XO-2); attack regions, CX-1, CR-1, PA-1 consumed |
| Engineering Design | `data-architect` · `eda-agent` · `metadata-mapper` · `dashboard-specifier` | pitch-grain frames; EDA to file (3 reports, MLB `eda/dp_uc54/`); 7-chapter spec keyed to the client's questions |
| Governance | `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` / `data-tagger` · `version-controller` | specs for TR-1/CC-1/XO-2 in `03` §2; lineage to `headlines.json`; privacy LOW–MODERATE (inherits uc-pos-011 ruling); v1.0.0 |
| Engineering Build | `data-engineer` | everything ran on the laptop VM (render stack `/tmp/pyrender`, `TMPDIR=/tmp/uc54/tmp`, ENV-3); 69 receipts in `out/` |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` · `certification-agent` | 16 DQ rules; harness families A–G, 157 checks |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` / `product-narrator` | reading paths, FAQ, catalog entry (`06`) |
| Marketing | `brand-guardian` | brand + claim assertion on every figure; PG-1 palette validated light and dark |
| Platform | `cost-watchdog` / `token-economist` | bid vs actual, calibration, tripwires (`07`) |

**Not engaged:**
- `machine-learning-engineer`: no projection was bid.
- `join-validator`: single-grain frames; the EN-2 fan-out asserts stand in.
- `slide-builder`: no deck was asked for.

## 3 · Governance gate checks
| Gate | Result |
|---|---|
| G1 · Entity locked to MLBAM id | PASS: 702222 + `phillies_role == 'batting'`. ENT-2: `crawford.parquet` is J.P. Crawford (641487), who also batted for PHI in 2017–18, so a name or substring filter leaks (harness B) |
| G2 · Rule-1 search before declaring anything new | PASS: `03` §0. K40, K34, UC22 OZ and the client's `find_similar_hits` found; turn test, chase cost and sector expected outs had 0 hits |
| G3 · Locked KPIs inherited, not re-derived | PASS: K40 `895c0edc…`, K34 `263e57d1…`, K53 `03d7e380…` (→ K52 → K51/K50/K48/K44), `cumulative_metric.py` `a2888740…`, UC22 `530d05cd…` (IX-1) |
| G4 · No re-derivation of existing work | PASS: slash line, wOBA, RISP, chase/whiff/swing, CR-1, XW-1, KP-1, PA-1, RF-2, RC-5, CX-1, DR-1, OZ regions all imported |
| G5 · New KPIs specified before code | PASS: TR-1 bars in the BID (23:18 ET) and asserted unchanged (harness A); CC-1 and XO-2 specs in `03` §2. XO-2's neighbourhood was chosen by a disclosed selection rule after a coverage failure (`05` catch Q-4) |
| G6 · Every published number from a receipt | PASS: narrative module formats from `headlines.json`; harness F 39/39 strings |
| G7 · Carry-ins labelled, never computed on | PASS: harness G 7/7 |
| G8 · Privacy before any external surface | PASS (internal): LOW–MODERATE; player-facing surface scoped per uc-pos-011 (`03` §6) |
| G9 · Certification | READY-CONDITIONAL, conditions below |

## 4 · Arguments the organization had (and how they were settled)
- **"Should XO-2 publish at all?"** The log has no catch probability. Settled: publish as a labelled proxy, with its rank, its sign across four neighbourhood variants (all negative), and the external −8 OAA beside it, never blended. The point of the chapter is DEF-3, why the notebook's method reads ±0, and that needs a counter-measure.
- **"Lowest launch angle in the house?"** Render QA caught a misread: KP-1 percentile 0 is a floor, not a rank. Haseley 2020 (91 PA) is flatter. Settled: print the rank (2nd-lowest of 189, lowest with 100+ PA) from `headlines.json`, and assert it in the harness.
- **"Is the June turn real?"** The client says yes and UC34 said "directionally, mechanism differs". TR-1 reads NO TURN; batting average is the one PRESENT signature. Settled: report the surge (rolling trough June 18 → peak August 9) as what actually happened, with the scan beside it.
- **"Which wOBA?"** House wOBA (K40, FanGraphs weights) for every rank and line. CM-1's Statcast-basis wOBA is not used, so CM-D1 does not arise. xwOBA is compared only with house wOBA on the same PA rows via XW-1.

## 5 · Escalations to the human DPO
1. **SF-1 (K40 defect, 2 pool PA):** `sac_fly_double_play` sits in NON_AB but not in SF, so K40 drops it from OBP and wOBA denominators. The FanGraphs convention counts it. Inherited and disclosed; DPO to rule on a K40 `_fix`.
2. **TP-1 (K40 exposure, 34 pool PA):** `truncated_pa` counts as a PA and an at-bat in `pa_rows`. The subject has 0.
3. **CM-D2 (house module):** `cumulative_metric.METRICS["hard_hit_rate"]` raises on nullable-float `launch_speed`. Worked around with an equivalent spec dict; the module is untouched (pinned).
4. **Ledger patches pending:** UC52 and UC53 patches are still unpasted. This patch claims #54 and names #55 next.

## 6 · Certification conditions (READY-CONDITIONAL)
- **C1:** XO-2 is a proxy. Any external use carries the "sign and rank, not decimal" label and the CI-2 OAA beside it.
- **C2:** AAA comparisons stay labelled as a supporting tier.
- **C3:** Player-facing use is limited to chapters 3–5 (his own approach and contact), per the uc-pos-011 privacy ruling.
- **C4:** SF-1 / TP-1 rulings may move pool wOBA in the 4th decimal; ranks would be re-run, not patched.
- **C5:** CC-1's "≈6 runs at the house-median chase rate" is arithmetic on CC-1, not a projection, and must be quoted that way.
