# 00 · DPO Orchestration Record — `uc-pps-031-sanchez-command-diagnosis-001`

**UC #45 · contract `uc-pps-031` · build `dp_uc45` · v1.0.0 · 2026-09-16**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL** · independently verified **436 / 436** (8 families) · DQ **16 PASS / 1 WARN / 0 FAIL**

---

## 1 · The ask and framing

Kellen asked for a command diagnosis on Cristopher Sánchez. The ask came with four premises (walks up, zone down,
chase down, ahead-in-count down), one existing KPI to locate and honour (edge rate), one new KPI to specify
("shadow rate": the zone grown by one baseball, and how often he misses it completely), one proof to show
(chase when the pitch is outside the shadow), and a notebook cell that started the analysis.

The organization read this as **a measurement question before it was a pitcher question**. The phrase "near the
zone" has three existing definitions in this repo, and the zone itself changed definition between the two seasons
being compared. The work ran in this order:

1. **Find what already exists** (Rule-1): the governed `edge_rate`, PD-7 count leverage, PB-1 peer netting, and the
   three shadow/edge geometries.
2. **Reproduce the client's cell exactly** before building anything on top of it (parent-reproduction check).
3. **Test the premises at two grains** (season and in-season), because at bid time two of them already looked false
   for the season.
4. **Control for the rulebook** before attributing any 2025→2026 zone movement to the pitcher.
5. **Then answer "is he near the zone?"** and show the proof.

## 2 · Delivery plan (departments actually engaged)

| Layer | Agent / capability | What it actually did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 4 premises + 2 KPI asks + 1 proof ask stress-tested; 5 gaps, 0 blocking after resolution (`01` §3) |
| | `source-system-profiler` | Six-season fitness; **found O-18** (2026 zone rails are a per-batter constant, top ~0.23 ft lower) |
| | `domain-steward-proxy` | Sourced the ABS zone definition externally (MLB.com) to *explain* O-18; enters no computation |
| Engineering Design | `data-architect` | One frame (all pitchers in PHI games 2021–26) + a subject slice; the league control comes for free |
| | `eda-agent` | 9 findings; three changed the build (`02` §3) |
| | `join-validator` | Two joins (common-rail merge, starter merge); both checked for fan-out |
| | `metadata-mapper` | 21 physical columns mapped; `player_name` role-dependence flagged (it is the *batter* on batting-role rows) |
| | `dashboard-specifier` | Window × compare × side × pitch spec, with the O-18 caveat in the header |
| Governance | `business-glossary-agent` | Shadow Zone family named to avoid colliding with OZ "shadow_in/out" and Attack Zone "shadow" |
| | `kpi-calculator` | SZ-0…SZ-5, CL-1, PN-1, ZC-1 specified in plain language before code (`03` §2) |
| | `technical-lineage-builder` | Column-level lineage for every published number (`03` §3) |
| | `privacy-watchdog` | Public performance data only; CLEAR |
| | `data-tagger` | Internal, restricted; external publication blocked |
| | `version-controller` | v1.0.0; O-18 is recorded as a **breaking environmental change** for every zone KPI in the repo |
| Engineering Build | `data-engineer` | `dp_uc45_kernel.py` + build + 29 receipts + 6 figures + PDF + dashboard |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` | 17 DQ rules; 1 WARN (arm_angle, not used) |
| | `certification-agent` | 8-family verification harness, 436 checks; family F caught **one real prose error** |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` | Persona actions, re-run recipe, the "target the shadow, not the heart" rule |
| Platform & Marketing | `cost-watchdog` / `token-economist` | Bid vs actual, calibration, tripwires |

**Not engaged:** `machine-learning-engineer` (no forecasting), `data-observability` (point-in-time diagnosis).

## 3 · Governance gate checks

| Gate | Result |
|---|---|
| G1 · Entity locked to an MLBAM id | **PASS**: `pitcher == 650911`, one `player_name`, all rows pitching-role |
| G2 · Rule-1 search before declaring any KPI new | **PASS**: 9 names searched; `edge_rate`, PD-7, PB-1 reused; 3 shadow geometries reconciled (`03` §1) |
| G3 · Locked kernel inherited verbatim | **PASS**: Section A matches dp_uc44 byte for byte (plus the notebook's `barrel_rate`, also byte-identical); A2 `edge_rate` matches dp_uc38 byte for byte |
| G4 · Client's method reproduced before extension | **PASS**: family G runs the notebook's own cells; 81/81 |
| G5 · Known-defect exposure measured | **PASS**: 8 defects read (`05` §2) |
| G6 · Environmental confounds controlled before attribution | **PASS**: O-18 found at bid time, controlled with ZC-1 + PN-1 |
| G7 · Small samples print their denominators | **PASS**: every split test carries n; the 2H is labelled 11 starts / 280 PA |
| G8 · Every published number reconciles to a receipt | **PASS**: family F, 60 narrative assertions |
| G9 · A figure title that makes a claim asserts it | **PASS**: Fig 3's build fails unless the 2H drop is significant |
| G10 · New geometry does not fork the ratified constant | **PASS**: SZ uses `BALL_FT = 2.94/12` and the governed distance function; the edge twin equals `edge_rate` |

## 4 · Capability fulfilment

| Client capability requested | Delivered as | Where |
|---|---|---|
| High-level performance across years (2021–22 combined) | Season panel 2021-22 → 2026 + 2026 halves + months | `season_panel`, `half_panel`, `month_panel_2026`; report §1 |
| Walk rate up / zone less / less chase / ahead less, "if the data backs it" | Premise tests at two grains with z/p, league deltas, and verdicts | `premise_tests`; report §1 |
| "A couple KPIs for edge rate or zone shadow rate" | Governed Edge Rate (reused) + Shadow Zone family SZ-0…SZ-5 (new) | `03` §2; report §2 |
| "Check prior work and enforce semantic consistency" | Rule-1 search; three-geometry crosswalk; SZ built on the ratified constant and distance function | `geometry_crosswalk`; `03` §1 |
| "Is he near the zone?" | Answer: near the edge as often; missing the shadow more; hitters stopped chasing the misses | report §4 |
| "Prove it with chase_rate outside the shadow" | SZ-3 by half, month, side, pitch and count, with league controls | Fig 3, `split_tests` |
| The notebook cell | Reproduced verbatim with the notebook's own code | `notebook_reproduction`; family G |
| PDF | 8 pp, branded | `dp_uc45_sanchez_command_report.pdf` |
| Interactive dashboard | Self-contained; live shadow map; compare windows; premise and start tables | `dp_uc45_command_dashboard.html` |
| Organization-driven additions | O-18 finding + ZC-1/PN-1 controls; miss-direction; count-state chase; start distribution | report §3–§6 |
| Token + time estimate framed as a bid | BID filed, awarded; reconciled | `BID_…md`, `07` §3 |

## 5 · The finding, in the DPO's words

Kellen's four premises are **true since the All-Star break and mostly false for the season.** Walk rate for the
season is flat (.054 → .055). Chase went up (.316 → .362). Share of pitches thrown ahead is flat (.311 → .313).
In-zone rate did fall (.519 → .465), but that is where the organization had to stop and look at the ruler: **the
2026 zone is a fixed, height-based zone per hitter, and its top sits a median 0.23 ft lower than the 2025 zone for
the same hitters.** Every pitcher's zone numbers moved. On common rails, half of Sánchez's zone drop is his own
and a third is the ruler.

Since the break, all four premises hold: walks .048 → .068, in-zone .472 → .452, chase .386 → .320, ahead
.333 → .278. The chase and count moves are significant; the walk and zone moves are directional.

The answer to "is he near the zone?" is **both of Kellen's scenarios, in sequence.** His Edge Rate hasn't moved
(.365 → .358): he's around the line as often as ever. But he misses the one-baseball shadow more often
(.344 → .407, and +.038 of that survives the rail and league controls). In the first half, hitters bailed him out
by chasing those misses 33.3% of the time, well above the league's 27.4%. Since the break that fell to 26.0%, while
the league stayed flat. When he was ahead in the count, chase on those misses fell from 40.1% to 30.7%, which is
league average. His misses moved from low (chaseable) to glove-side and up (easy to take). The leak is the
changeup to right-handed hitters: 62.1% of them miss the shadow, and righties chase only 30.2% of those misses.

## 6 · Where the organization argued with itself

**Which peer control to trust.** `eda-agent` ran PN-1 (peer-netted YoY, the PB-1 pattern) on native rails. It said
Sánchez's shadow-miss rise (+.063) was just the staff's (+.060): nothing to see. `source-system-profiler` objected.
The lower zone top hurts high-zone pitchers more than low-zone pitchers, so native-rail peer netting
**over-corrects for a sinker/changeup lefty**. **Resolution:** build ZC-1 (re-score 2025 against each hitter's 2026
rails). It showed the ruler moves Sánchez's 2025 number by only +.011. PN-1 was then re-run on common rails and
agreed with ZC-1 (+.027 net). Both versions ship. The report explains why the native one is misleading here, and
the analyst action says to use ZC-1 first from now on.

**Whether to call P2 supported.** `business-glossary-agent` wanted P2 marked "rulebook artefact", based on the
league-pooled netting (−.016 of −.054). `kpi-calculator` pointed out that league-pooled netting has the same
profile-mix flaw. **Resolution:** decompose on common rails: 50% his own, 34% rail change, 16% league drift.
P2 ships as "supported, half his own".

**Whether "shadow" can be the term.** Three repo objects already use the word. `business-glossary-agent` proposed
"Expanded Zone". The DPO's own word was "shadow", and consumers will search for it. **Resolution:** keep the client's
word, but make it a compound term (**Shadow Zone / Shadow Miss**) with an explicit crosswalk to OZ `shadow_in/out`
and Attack Zone `shadow`, and build it on the governed Edge Rate geometry so the numbers can't disagree.

**Whether to grade on the 20-80 scale (SG-1, second use).** It would have counted toward ratifying SG-1.
`kpi-calculator` refused: within one zone definition, the pitcher-season population in the log is 13 arms at 500
pitches, and pooling across 2025/2026 mixes rails. **Resolution:** not used. The start-level distribution
(282 starts in 2026, 315 in 2025) gives the "where does he sit" context without a grade.

**The March start.** One start of 87 pitches sits alone in the 2026 month panel. `consumer-onboarding-agent`
wanted it dropped from the trend. **Resolution:** kept in every receipt and the dashboard, folded out of the
report's month figure with a label.

## 7 · Escalations to the human DPO

1. **E-1 · O-18 affects every zone KPI in the repo.** Any 2025→2026 comparison of `in_zone_rate`, `chase_rate`,
   `edge_rate`, OZ-1…4, Attack Zone, or `ooz_called_strike_rate` is confounded. **Decision needed:** adopt ZC-1
   (common-rail re-score) as the standing control for cross-2026 zone comparisons, and restate any delivered UC
   that compared across the boundary? First candidate: `uc-pps-030`'s SG-2 in-zone benchmark, which pools 2015–2026 pitcher-seasons across the rail change.
2. **E-2 · `edge_rate` is governed (Register P16 = A) but is not in `Baseball Functions.ipynb`.** The register asked
   for confirmation that UC8's approval reached the notebook; it hasn't. **Decision needed:** paste
   `_dist_to_zone_edge` + `edge_rate` from `dp_uc45_kernel.py` Section A2.
3. **E-3 · The Attack Zone "shadow" (0.33 ft, UC#11 / `uc-pps-022`) conflicts with the ratified `BALL_FT`.** It moves
   5.5% of Sánchez's pitches. **Decision needed:** restate it on `BALL_FT` or rename it.
4. **E-4 · Nine new provisional objects.** SZ-0…SZ-5, CL-1 (a promotion of PD-7, not a new definition), PN-1, ZC-1.
   **Decision needed:** ratify SZ-1/SZ-2/SZ-3 on second use?
5. **E-5 · The changeup to RHB is the actionable item.** It goes to the pitching staff, not the analytics backlog.
   Tripwire T-1 (`07` §4) re-reads it after two more starts.

## 8 · Publish recommendation

**READY-CONDITIONAL — internal, need-to-know.**

- **C1** Valid for data through 2026-09-15. The build refuses a different anchor.
- **C2** Any 2025→2026 zone statement must carry its ZC-1 decomposition. A raw delta alone is not publishable.
- **C3** 2026 second-half walk and zone moves are directional (p = .23, .29).
- **C4** League controls are "all pitchers in Phillies games", not MLB.
- **C5** SZ, CL-1, PN-1 and ZC-1 are provisional.
- **C6** Release point and arm angle are out of scope (DQ-17 WARN).

External publication: **blocked**. Distribution: pitching coach, pitching analyst, catcher, manager.
