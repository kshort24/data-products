# 00 · DPO Orchestration Record: `uc-pps-033-bowlan-2026-recap-001`

**UC #48 · contract `uc-pps-033` · build `dp_uc48` · v1.0.0 · delivered 2026-09-25 (bid 2026-09-24 ET)**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL** · independently verified **153 / 153** · DQ **16 PASS / 3 WARN / 0 FAIL** · brand 58 pass / 0 fail

---

## 1 · The ask and how we framed it

Three notebook cells (`September 2026.ipynb` 115–117) held a season-recap table built from 19 KPIs with 14 inline claims (Kellen), a 2×2 box grid (Gemini Flash), and four scatters in reply (Kellen). The cell also said *"functionalize that so I can use a similar analysis on Jonathan Bowlan"* and *"If the above were a DT, it could come from this view."* The instructions asked for an interactive dashboard with the season's narrative in the interactivity, and for the actions people in the pitching value stream could have taken.

The organization read it as **four jobs**, run in this order:

1. **Reproduce the parent before improving it.** Re-run the client's cell exactly (name filter, rounded `pitch_mix`, `fillna(0)`), then the governed version (id lock, unrounded, NaN-safe), and require agreement on every KPI the two methods share (DQ-06). Only then grade the 22 claims.
2. **Inherit the grade and explain it.** `uc-pps-032` had already graded this four-seam #2 of 405 (2026) and RESULTS-ONLY #20 (2025). Re-grading it would re-derive existing work. The recap's question is *what moved between those two receipts*, and the answer is the velocity grade 50 → 60.
3. **Make "actions people could have taken" falsifiable.** Each persona gets a hypothesis with declared signatures, thresholds and a decision rule (PA-1). The log can show a signature; it cannot show the action. Every row says what would confirm it.
4. **Tell the story in chapters, one per chair.** Six chapters follow the season (buy → velocity → carry → platoon → counts → role). A persona lens re-reads each chapter for the person holding that job.

## 2 · Delivery plan (departments actually engaged)

| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 6 gaps (2 blocking, both resolved from the repo). Stress-tested 22 client claims plus 6 Gemini notes |
| | `source-system-profiler` | Profiled the two Bowlan sources, found the 19 cross-source duplicates and the 47 spring rows. A byte search showed "Bowlan" appears only in `bowlan.parquet` among the 128 `nphl` files |
| | `domain-steward-proxy` | Re-verified the carry-ins. The 9/17 exit is a **right groin strain, no IL** (Inquirer 2026-09-18), superseding the notebook and uc-pps-032's "suspected oblique". The Strahm trade is sourced to MLB.com |
| | `business-glossary-agent` | Flagged the **Runs Created** name collision (house meaning ≠ Bill James RC), which is kept with a glossary note. Named the persona set for this stream |
| Engineering Design | `data-architect` | One pitch-grain career frame (CF-1) with a precedence dedup. Every other table is a groupby of it, and there are no cross-grain joins |
| | `eda-agent` | Found the whole-arsenal velocity gain, the role-vs-arm question (→ VE-1), the sinker regression, the FPS paradox, and the 2017 ride level shift |
| | `join-validator` | Checked the only merges (recap KPI merges on the level key, 1:1). Family B rebuilds the frame without the kernel |
| | `metadata-mapper` | 24 physical → CDE mappings; `player_name` stays AMBIGUOUS (uc-pps-032 NR-1), so the build locks by id |
| | `dashboard-specifier` | Six chapters, persona lens, drill-through, appearance timeline, theme toggle (`02` §5) |
| Governance | `kpi-calculator` | SR-1, KP-1, AR-2, US-1, VE-1, CS-1, PA-1 specified before code (`03` §2) |
| | `technical-lineage-builder` | Column-level lineage for every published number (`03` §3) |
| | `privacy-watchdog` / `data-tagger` | Public performance data only → CLEAR. Tagged **Internal**; external publication is allowed after DPO review (no other club's players are ranked) |
| | `version-controller` | v1.0.0; anchor-pinned |
| Engineering Build | `data-engineer` | `dp_uc48_kernel.py` + build + 29 CSV / 13 JSON / 11 PNG receipts |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` | 19 rules, 0 FAIL, 3 designed WARNs |
| | `certification-agent` | Harness A–F, 153 checks |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` / `product-narrator` | Persona reading paths, dashboard walkthrough, the narrative |
| Platform & Marketing | `cost-watchdog` / `token-economist` | Bid vs actual, calibration, tripwires |

**Not engaged:** `machine-learning-engineer` (no model), `semantic-modeler` (no new cross-UC metric layer; KP-1 is provisional), `data-observability` (point-in-time recap; tripwires in `07`).

## 3 · Governance gate checks

| Gate | Result |
|---|---|
| G1 · Entity locked to MLBAM id | **PASS**: 680742; the name filter is used only to reproduce the client frame (HP family), and matches (DQ-06) |
| G2 · Rule-1 search before declaring anything new | **PASS**: `rc_per_gm`, `ff_vert`, `whiff_rate_iz_ff`, `whiff_rate_breaking`: 0 hits. `runs_created`/`rc_per_pa` found (uc-pos-012) and **inherited**. `xwobacon` found (uc-pps-021 O1) and **inherited**. RV/100 found (uc-pps-032) and **second use** |
| G3 · Locked KPIs inherited, not re-derived | **PASS**: `dp_uc44_kernel` imported, sha256 `a2c119096db2…` asserted at build and in the harness |
| G4 · No re-derivation of existing work | **PASS**: four-seam grades read from `out/dp_uc47_population_graded.csv`. FF pitch counts reconcile to this frame (DQ-08) |
| G5 · Small samples print denominators | **PASS**: 2023/2024 PA shown everywhere; every whiff shows its swings; every rate change shows its p |
| G6 · Superlatives name their population | **PASS**: "92nd percentile" is always the *house frame, 198 Phillies pitcher-seasons ≥100 PA*; "#2 of 405" always cites uc-pps-032 |
| G7 · Carry-ins labelled, sourced, never computed on | **PASS**: the trade and the 9/17 exit appear only as carry-ins (harness E) |
| G8 · Hypotheses never presented as attributions | **PASS**: PA-1 decision rule is published. Every ledger row has "what would confirm it". The dashboard says "hypotheses, not a record" on the ledger and in the footer |
| G9 · Every published number reconciles to a receipt | **PASS**: family F: 65 report numbers, 10 ledger strengths and 5 dashboard narrative numbers (80 checks) |
| G10 · Client claims graded, not overwritten | **PASS**: 22 HP rows keep the client's words verbatim next to the governed value |
| G11 · Anchor pinned | **PASS**: build refuses any `phils_2026` anchor other than 2026-09-23 |

## 4 · Capability fulfilment

| Asked for | Delivered as | Where |
|---|---|---|
| "Functionalize that" | `season_recap(df, governed=…)` + `career_frame(pitcher_id)`; the next recap is one call | `dp_uc48_kernel.py` SR-1 / CF-1 |
| The 19-KPI recap table | Governed + notebook-exact versions, reconciled | `out/dp_uc48_recap_*.csv`, report §1 |
| "xxth Percentile" | **92nd** (rank 15 of 198, house frame) | KP-1, `out/dp_uc48_house_percentiles.csv` |
| Velo box + IQR band | F2 (n printed) | dashboard ch. 2 |
| Gemini 2×2 | F3, governed (inches, n, imports, no leaked `gy`) + 6 audit notes | ch. 2 detail, `out/dp_uc48_gemini_cell_audit.csv` |
| "A simpler view" (velo × spin, movement) | F4, F5 | ch. 2, ch. 3 |
| Staff carry plot (2017 excluded, IQR band) | F6 + DQ-11 proving the 2017 exclusion | ch. 3 |
| "If the above were a DT" | **Drill-through**: pitch-type centroid map → click → that pitch vs every Phillies RHP | ch. 3 |
| Interactive dashboard with the narrative woven in | `dp_uc48_bowlan_2026_dashboard.html`: six chapters, persona lens, timeline, theme toggle, offline | repo root + control plane |
| Persona actions that could drive the results | PA-1 ledger: 10 hypotheses, 27 signatures, decision rule, confirmations | ch. callouts + ledger section, report §7 |
| 00–07 receipts, bid with token/time estimate | This folder; `BID_…md`; actuals in `07` §3 | here |

## 5 · The finding, in the DPO's words

The notebook's own velocity chart already held the answer: **the tick and a half is the whole archetype flip.** Kansas City had a four-seam with ride graded 60 and whiff graded 80. A velocity grade of 50 left its shape axis at 55, and a .302 wOBA hid it. In Philadelphia it came out 1.51 mph harder from the first pitch of every outing. The velocity grade moved to 60, the shape axis crossed the bar, and the pitch went from #20 to #2 of 405.

Three other things changed with it, and each maps to a chair. The **pitching analyst's** arsenal was rebuilt by platoon. The **catcher's** calls put the four-seam in two-strike and behind counts (both p < .01). The **manager** gave him one late inning, 59 times. The strikeout and walk gains that followed are real in direction and 92nd-percentile in size, but on one season of relief PA they are **not statistically settled**. The report says so.

## 6 · Where the organization argued with itself

**Re-grade or inherit?** `eda-agent` wanted to re-run the uc-pps-032 archetype engine on the refreshed log (anchor 9/23 vs 9/20). `data-product-owner` refused. Bowlan threw 0 pitches between 9/20 and 9/23 (last appearance 9/17), so his grade cannot have changed. Re-grading 405 pitcher-seasons for a recap re-derives existing work. **Resolution:** inherit, and prove the inheritance is safe (DQ-08: the FF counts reconcile exactly).

**"Elite" K rate.** `product-narrator` wanted "elite 32% K rate" as the headline, in the client's words. `certification-agent` pointed out that p = 0.18 on the 2025 → 2026 change. **Resolution:** the *level* is stated as a percentile (92nd, house frame) and the *change* as "not settled". Both are true, and neither is allowed to stand for the other.

**Should the persona ledger exist at all?** `privacy-watchdog` and `domain-steward-proxy` both worried that "the pitching coach added velocity" would read as a claim about a real person's work. **Resolution:** the ledger is written in the conditional (hypotheses), each hypothesis names its data signature and the evidence that would confirm it, and the decision rule is public. **CA-2** ("cut walks by getting ahead") is kept because it is **contradicted**. A ledger that can only confirm is not evidence.

**Runs Created.** `business-glossary-agent` flagged that the house term collides with Bill James' Runs Created (an offensive stat). Renaming an approved term is a breaking change for every notebook that uses it. **Resolution:** keep it, gloss it on first use, and decompose it (inherited runners) in the report. Escalated E-3.

**The 2017 exclusion.** The client dropped 2017 as "outlier data". `data-quality-engineer` wanted to know whether dropping a whole season was justified. DQ-11: 2017 staff four-seam ride sits 5.1 standard deviations above every other season, so it is a level shift. **Resolution:** the exclusion is kept and documented; no cause is asserted.

**Dark or light.** All four client cells use `plotly_dark`; the brand center mandates `plotly_white`. E-5 from uc-pps-032 is still open. **Resolution (same as uc-pps-032):** print follows the brand center (58/58 pass). The dashboard follows the viewer's theme and offers a one-click *Notebook dark* toggle.

## 7 · Escalations to the human DPO

1. **E-1 · Ratify `season_recap` (SR-1) as the house recap function.** It is the client's own cell with three fixes (O-25 rounding, `gy` leak, `fillna(0)`). The Luzardo recap in cell 114 is the cheapest second use.
2. **E-2 · Fix O-25 upstream?** `pitch_mix` rounds `pfx_*` to 0.1 ft. Changing `Baseball Functions.ipynb` is breaking for every chart built on it. Alternative: add `ivb_in`/`hb_in` columns to `pitch_mix` and leave `pfx_*` alone (non-breaking).
3. **E-3 · Runs Created naming.** Keep it (with the gloss), or add an alias `runs_on_watch`?
4. **E-4 · Persona set.** This UC used Front Office, Pitching Coach, Pitching Analyst, Catcher, Manager and Pitcher. Should Strength & Conditioning / Medical be a governed persona? PC-1 and MG-2 both point at it.
5. **E-5 · Brand standard** (carried from uc-pps-032, still open).
6. **E-6 · Ledger patch.** Rows #25–#48 are still pending pastes into `uc_ledger_AI.md`.

## 8 · Publish recommendation

**READY-CONDITIONAL. Internal, pitching department and front office.**

- **C1** Percentiles are house-frame (Phillies pitcher-seasons), not MLB-wide. Any external use carries that sentence.
- **C2** Persona ledger rows are hypotheses with data signatures. They never attribute an action to a named staff member.
- **C3** The trade and the 9/17 injury are carry-ins.
- **C4** 2025 → 2026 rate changes other than the usage shifts are directional (p > .05).
- **C5** New objects (CF-1, SR-1, KP-1, AR-2, US-1, VE-1, CS-1, PA-1) are provisional.
- **C6** Anchored to 2026-09-23. A postseason appearance or a refresh is v1.1.0.

External publication: permissible after DPO review (public data, one Phillies player, no other club's players ranked). Recommended audience: pitching coach, bullpen coach, catchers, manager, front office, the player.
