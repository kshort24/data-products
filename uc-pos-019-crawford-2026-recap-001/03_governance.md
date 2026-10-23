# 03 · Governance
**business-glossary-agent · kpi-calculator · technical-lineage-builder · privacy-watchdog · data-tagger · version-controller**

## 0 · Rule-1 search
| Need | Search (names + synonyms) | Hit | Disposition |
|---|---|---|---|
| Slash line, wOBA (house weights), RISP, swing/chase/whiff/OOZ, CR-1, CR-2, PA-L1, DR-1, RF-2, RC-5, BT-1, percentiles | pos kernels K18…K40 | **K40** (`dp_uc40_kernel.py`) | inherit, pinned `895c0edc…` |
| Centre-field comparison population | "centre field", "fielder_8", "cf_context" | **K34 CX-1** | inherit, pinned `263e57d1…` |
| xwOBA, WB-1, KP-1, PA-1, IX-1, two-prop z, brand | pps chain | **K53 → K52 → K51/K50/K48/K44** | inherit, pinned `03d7e380…` |
| Cumulative by PA | "cumulative", "running" | **`cumulative_metric.py` CM-1** + K53 CM-1a | inherit; spec dicts for BA/OBP/SLG/wOBA-house/GB%/HH% (supported API) |
| Heart/shadow/waste regions | "shadow", "heart", "attack region" | **UC22 `tag_regions` / `region_profile`** | IX-1 extraction (UC22 parses argv at import); constants asserted from source |
| Similar-hit expected outs | "similar", "expected out", "find_similar" | **`Baseball Functions.ipynb` `find_similar_hits`** | XO-1, IX-1 extraction (client-authored) |
| Outfield run-saving | "run saving", "OAA" | UC4 (delta_run_exp proxies, no catch probability) | read, not inherited: different question (run value per play) |
| Run value per pitch | "delta_run_exp", "rv100" | K47 convention (batting side +) | convention inherited; DQ RV-1 asserts sign |
| Turn / breakpoint verdict | "turn", "breakpoint", "signature" | RC-5 scan (K40); DB-1 (K53, decline-or-blip, pitcher) | **0 hits for a hitter turn test → TR-1 NEW** on PA-1 |
| Chase cost | "chase cost", "chase run value", "swing take" | none | **CC-1 NEW** |
| Sector expected outs | "sector", "opportunit" | none | **XO-2 NEW** (generalizes XO-1's neighbourhood) |

## 1 · Inherited by import (sha256-pinned; `dp_uc54_kernel.assert_lineage()` checks 12 files)
K40 (`nresults_unrounded`, `pa_rows`, `risp_rows`, `whiff_rate_fix`, `chase_rate_g`, `swing_rate`, `zone_swing_whiff`, `ooz_whiff_rate`, `hard_hit_rate_fix`, `barrel_rate_g`, `battedball_profile`, `xcontact`, `derive_loc`, `hit_direction`, `bat_tracking`, `rolling_form`, `breakpoint_scan`) · K34 (`cf_context_pool`, `HILL_DEBUT`) · K53 chain (`load_phils_cols`, `xwoba_pa`, `woba_statcast`, `house_percentile`, `signature_verdict`, `strength_from_signatures`, `extract`, `two_prop_z`, brand) · CM-1.
**Generalized (non-breaking):** CM-1 spec dicts · CM-1b multi-panel ghost lines (figure side) · RF-2x rolling xwOBA on RF-2's index.

## 2 · KPI specs for new objects (written before code)
### TR-1 · June-turn ledger (bars registered in the BID, 2026-10-20 23:18 ET)
- **Windows:** pre = 2026-03-26 → 05-31; post = 06-01 → 09-27 (regular season).
- **Signatures:** R1 wOBA +.030 · R2 BA +.030 · R3 OBP +.030 · R4 SLG +.040 · P1 xwOBA +.025 · P2 K% −.030 · P3 BB% +.015 · P4 chase −.030 · P5 hard-hit +.040 · P6 whiff −.030.
- **Verdicts:** PA-1 `signature_verdict`, with two-proportion p for proportions (P2–P6).
- **Roll-up:** `strength_from_signatures` per family. Results and process both SUPPORTED/STRONG → EARNED TURN; results only → RESULTS TURN; process only → PROCESS TURN; neither → NO TURN.
- **Disclosure:** UC34 published one June-1 split through 2026-08-13 (+.019 wOBA), which the bidder had read.
### CC-1 · Chase cost
- **Out-of-zone pitch:** zone 11–14, `pitch_type` not null (AB-1), `delta_run_exp` not null.
- **Reference:** E[take] = mean `delta_run_exp` of out-of-zone takes by (balls, strikes) over house batting 2023–26.
- **Cost per chase:** E[take | count] − rv(swing). Reported as total runs, per 100 chases and per 100 out-of-zone pitches, by hand × pitch group and by strikes.
- **Pool rank:** house hitter-seasons 2023–26, n=65.
- **Companion (no new arithmetic):** three-ball reach rate, and "chases above the house-median rate × mean cost per chase" labelled as arithmetic (C5).
### XO-2 · Sector expected outs (proxy)
- **Opportunity:** regular-season air BIP (fly ball, line drive, popup) with him at `fielder_8`, tracked EV/LA/distance/hc, spray angle within ±15° of dead centre (PA-L1 coordinates), distance ≥150 ft.
- **Out:** the client's out list, verbatim.
- **xOut:** out share among comparison balls (same filters, every Phillies game 2015–26, not fielded by him, de-duplicated) inside the neighbourhood. Unscored if <10 neighbours. OAE = Σ(out − xOut).
- **Neighbourhood selection rule:** take the first variant, in order of closeness to the client's EV 2 / LA 1 / dist 5, that scores ≥90% of opportunities: v1 client + dir 7.5° (45%) → v2 client, no dir (76%) → **v3 EV 3 / LA 2 / dist 10 / dir 10° (92%, chosen)** → v4 (97%). All four are reported (`out/dp_uc54_xo2_sensitivity.csv`).
- **Context:** every Phillies CF season since 2015 with ≥80 CF games, each scored against a pool without him.

## 3 · Technical lineage
`phils_{2015..2026}.parquet` + `lhvb25.parquet` → `dp_uc54_kernel` (inherited functions) → `dp_uc54_crawford_recap.py` → `out/dp_uc54_*.csv` + `headlines.json` → `dp_uc54_hp.py` (adds `hp`) → `dp_uc54_build_figs.py` (PNG/JSON; asserts claims) → `dp_uc54_narrative.py` → `dp_uc54_build_report.py` → `.md` → `dp_uc54_build_pdf.py` → `.pdf`; `dp_uc54_build_dashboard.py` → `.html` + `_artifact.html` → Artifact. The harness (`dp_uc54_verification.py`) reads parquet directly and checks headlines, receipts, report and dashboard.

## 4 · Defects found by building (reported, not patched upstream)
| ID | Where | What | Exposure |
|---|---|---|---|
| **SF-1** | K40 `nresults_unrounded` | `sac_fly_double_play` is in NON_AB but not SF, so it drops out of OBP/wOBA denominators | 2 pool PA; subject 0 |
| **TP-1** | K40 `pa_rows` | `truncated_pa` counted as a PA and an AB | 34 pool PA; subject 0 |
| **CM-D2** | `cumulative_metric.py` | `METRICS["hard_hit_rate"]` raises on nullable-float EV (`pd.NA >= 95`) | blocks HH% lines for any frame with untracked BIP |
| **REC-2** | K44 `nresults` | OBP divides by PA (legacy get_stats) → .305 vs .309 | known (K40 RF-2 note); disclosed |
| **ENT-2** | data layer | `crawford.parquet` = J.P. Crawford; he also has PHI 2017–18 rows | any name or file lock |
| **SRC-2** | data layer | `white-sox-of-25-26.parquet` duplicates 3 of his 2026 MLB pitches | the client's `nphl ∪ pos` frame |
| O-8 | inherited | untracked BIP counted as not-hard-hit | 4 subject BIP |

## 5 · Tagging (data-tagger)
Domain `pos` · subject areas Batting / Plate Discipline / Batted Ball / Outfield Defense (proxy) · sensitivity **Internal** · product `uc-pos-019`.

## 6 · Privacy (privacy-watchdog): LOW–MODERATE (inherits the uc-pos-011 ruling)
- A public player and publicly tracked performance; no PII beyond the name.
- Rated above baseline because the product evaluates a 22-year-old's development path and documents deployment (platoon) context.
- **Player-facing surface:** chapters 3–5 only (his approach and contact). The defense proxy, platoon context and cohort comparisons stay staff-only unless the DPO and player development decide otherwise.
- **Restricted uses:** contract, arbitration or option valuation; media distribution; any causal claim about platooning.

## 7 · Versioning (version-controller)
- **v1.0.0.** New objects TR-1, CC-1 and XO-2 have no consumers, so they are cheap to change now.
- **Non-breaking:** CM-1 spec dicts, CM-1b, RF-2x.
- **v1.1.0 triggers:** a 2027 appearance, a K40 SF-1/TP-1 fix that moves a rank, or a sourced final OAA that changes C1.
