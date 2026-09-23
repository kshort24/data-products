# 00 · DPO Orchestration Record — `uc-pps-032-elite-rhp-ff-archetype-gap-001`

**UC #47 · contract `uc-pps-032` · build `dp_uc47` · v1.0.0 · 2026-09-22**
Value stream: Phillies Pitching (`pps`) **with scope note** (DPO decision 9) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL** · independently verified **241 / 241** · DQ **16 PASS / 3 WARN / 0 FAIL**

> **Scope note (decision 9).** `pps` has analysed pitchers the Phillies already have. This use case grades
> pitchers the Phillies *don't* have, against a defined need. The organization proposed a new value stream
> (`rca`, Roster Construction / Acquisition); the DPO kept it in `pps`. Consequence recorded here so the next
> reader doesn't re-litigate it: **`pps` now includes external-candidate evaluation when the need is a
> Phillies pitching need.** If a second acquisition-style product lands outside pitching, revisit `rca`.

---

## 1 · The ask and framing

A notebook cell titled "Roster addition" (`September 2026.ipynb`, cell 101) asked a general question — *given
team X's roster, which archetype and which player would move the needle most?* — with a pilot (elite RHP
four-seam), a six-arm cohort, a draft data spec, four answered DPO decisions, and four Plotly cells whose
subtitles are claims.

The organization read it as **three jobs**, and ran them in this order:

1. **Clean the frame before grading anyone.** The client's comparison set is `pps + pos + nphl`. `nphl` is 128
   files including 15 minor-league files and ~48k duplicate rows. Grading against an uncleaned frame grades MLB
   arms against Double-A fastballs.
2. **Keep the two sub-questions apart.** Part A (the cohort) and Part B (the external gap) share an engine and
   nothing else. Part A answers "who's best in the room"; Part B answers "what's out there, and what would it
   change". The report answers them in that order and never lets a Part A ranking stand in for a Part B one.
3. **Tell the story the data has, not the one the ask implies.** The ask presumed a gap to fill. The data says
   the Phillies already own the #2 four-seam in the frame — and that the gap is *depth*, not *quality*. The
   report is built around that inversion.

## 2 · Delivery plan (departments actually engaged)

| Layer | Agent / capability | What it actually did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 7 gaps, 6 client premises stress-tested; 2 blocking gaps resolved by DPO decisions already in the ask |
| | `source-system-profiler` | Profiled all 128 `nphl` files: level, keying, year span, duplicate load. Found the batter-keyed team pulls |
| | `domain-steward-proxy` | Resolved Seranthony Domínguez = 622554; confirmed 694819 = Misiorowski (identity-only lookup); logged Bowlan carry-in |
| Engineering Design | `data-architect` | One universe (FR-1), one pitcher-season grain, two masks (population / candidate) — no joins across grains |
| | `eda-agent` | Drift study (velo/spin drift, ride/whiff/RV flat); reliability study (RV/100 is 21% split-half) — both changed the build |
| | `join-validator` | Universe is a concat + precedence dedup, not a join; verified by an independent dedup path (family B) |
| | `metadata-mapper` | 29 physical columns → CDEs; `player_name` flagged AMBIGUOUS (batter vs pitcher) → NR-1 |
| | `dashboard-specifier` | Six-tab explorer; one live control (weight) whose formula is a verified KPI, not a browser recomputation |
| Governance | `business-glossary-agent` | 14 terms; **renamed `ff_elite_stuff_flag` → `ff_elite_shape_flag`** (collision with SG-4 "Stuff grade") |
| | `kpi-calculator` | FR-1, NR-1, AF-1…AF-6, SG-6, SG-7, CB-1 specified before code (`03` §2) |
| | `technical-lineage-builder` | Column-level trace for every published number (`03` §3) |
| | `privacy-watchdog` | Public performance data; player identities already public — CLEAR |
| | `data-tagger` | Internal — Restricted; external publication blocked (candidate list naming other clubs' players) |
| | `version-controller` | v1.0.0; population definition is breaking-change-governed |
| Engineering Build | `data-engineer` | `dp_uc47_kernel.py` (Section C new), build, 30+ receipts |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` | 19 DQ rules executed; 0 FAIL, 3 permanent WARN |
| | `certification-agent` | 6-family harness, 241 assertions; family F caught one real prose error before publication (`05` §4) |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` / `product-narrator` | Persona routing; narrative report; the client's own chart idiom reproduced and governed |
| Platform & Marketing | `cost-watchdog` / `token-economist` | Bid vs actual; brand-center MCP compliance pass; 5 tripwires |

**Not engaged:** `machine-learning-engineer` (no model — stabilization is closed-form empirical Bayes, not a
fitted learner), `data-observability` (point-in-time product; a refresh is a new version).

## 3 · Governance gate checks

| Gate | Result |
|---|---|
| G1 · Entities locked to MLBAM ids | **PASS** — six cohort ids; Domínguez resolved from the log (622554), not typed |
| G2 · Rule-1 search before any KPI declared new | **PASS** — `ff_elite*`, `archetype`, `benchmark_population`, `rv100`, `season_adjust`, `ivb` searched in both repos. SG-1/SG-2 found and **inherited**; 0 collisions for new objects; 1 near-miss (`delta_run_exp` used for defence in `dp_uc4` — different grain, different sign convention, documented) |
| G3 · Locked KPIs inherited, not re-derived | **PASS** — `dp_uc44_kernel` imported, sha256 pinned and re-verified |
| G4 · The profile UC the ask cites exists | **FAIL → resolved.** "UC-PPS-XXX-A" with `ff_elite_*_flag` was never built. The flags are **defined here for the first time**; the ask's "same glossary term, different population" becomes "first definition, bounded population" |
| G5 · Frame governed before use | **PASS** — 164,755 MiLB rows, 30,229 cross-source and 17,464 internal duplicates removed; row accounting closes (family B) |
| G6 · No published rate below its floor | **PASS** — 50-FF subject floor, 25-swing whiff floor, 100-FF population and board floor (CB-1) |
| G7 · Small samples print denominators | **PASS** — every board row prints games and four-seams; McFarlane stamped THIN in every surface |
| G8 · Superlatives named, cohorts enumerated (uc-pps-028 G8) | **PASS** — "best four-seam" is always *by composite at w = 0.5, among the 405, 2018–26*; F6 shows it under every weight |
| G9 · No composite for a contested claim without its axes (uc-pps-028 G9) | **PASS** — the composite ships with both axes and a weight sweep; the winner changes at the extremes and the report says so |
| G10 · The scale's normality assumption tested | **PASS** — 2 of 5 metrics non-normal; rank twin published; skew flag 0 |
| G11 · Every published number reconciles to a receipt | **PASS** — family F, 120 narrative assertions |
| G12 · Carry-ins labelled as carry-ins | **PASS** — Bowlan injury appears only in scenarios labelled "carry-in" |

## 4 · Capability fulfilment

| Asked for | Delivered as | Where |
|---|---|---|
| Six arms as a cohort / population | Part A: graded every cohort pitcher-season 2018–26, leaderboard + weight sweep | report §3, `out/dp_uc47_cohort_*` |
| Archetype gap, generalized | AF-1 `ArchetypeSpec`; the pilot is one instance | `dp_uc47_kernel.py` |
| `ff_elite_stuff_flag` / `ff_elite_results_flag` | `ff_elite_shape_flag` (renamed) / `ff_elite_results_flag` / `ff_elite_archetype_flag` | `03` §1 |
| "Benefit most" — aspirational, open to suggestions | Suggestion taken: the **needle swap** (AF-6) — role-volume × grade gap vs the staff's marginal four-seam, plus EFS | report §5 |
| Bounded population, "this era" | 2018–26 (first and last cohort four-seam season), drift-adjusted to 2026 | `03` §2 SG-6 |
| Confirm `nphl` scope | Profiled: convenience sample of MLB + MiLB, 128 files, player/team/hitter keyed | `01` §3, `out/dp_uc47_nphl_file_keying.csv` |
| The four notebook cells | Reproduced, re-run governed, verdicts + one notebook-state hazard | report §6 |
| PDF | 10 pp, narrative, brand-center-compliant figures | `dp_uc47_elite_ff_archetype_gap_report.pdf` |
| Dashboard if it makes sense | Archetype Explorer — six tabs, weight slider, notebook-dark toggle, offline | `dp_uc47_archetype_explorer.html` |
| Brand guidelines + host MCP servers | `brand-center-mcp` `get_brand_guidelines` (palette, template) + `validate_brand_compliance` on every figure (35/35 pass) | `out/dp_uc47_brand_compliance.csv` |
| Bid (tokens + time) | Filed, awarded, reconciled | `BID_…md`, `07` §3 |

## 5 · The finding, in the DPO's words

The notebook asked who would move the needle. Before answering, the organization had to find out where the
needle *was*. It's at **11.1%**: of the 4,201 four-seams Phillies right-handers threw in 2026, 467 came from an
arm that is plus on both axes — and all 467 are Jonathan Bowlan's. His 2026 four-seam is the **second-best of
405** in the bounded frame since 2018. So the premise inverts: the Phillies don't lack an elite four-seam; they
have exactly one, and the client's own notebook records him leaving a game on 9/17 holding his side.

Externally, **nobody on the ranked board out-grades him**. The best external four-seam with a real season of
evidence (Ohtani 2025, 58.5) sits 6.5 points under Bowlan and 1.9 under Duran. One ranked arm is the archetype
(Casparius). The only arm above Bowlan — Misiorowski — has one start in the frame.

The needle, properly defined, lives in the rotation: a starter's 669 four-seams move the share almost three
times what a reliever's 241 do, and the rotation's four-seams score 57, 46, 45 and 39. An elite *starter*
four-seam is the archetype worth hunting; the frame contains one, seen once.

## 6 · Where the organization argued with itself

**Stuff vs shape.** `kpi-calculator` implemented the client's `ff_elite_stuff_flag` verbatim.
`business-glossary-agent` blocked it: SG-4 already defines "Stuff grade" as the whiff grade, and this UC's
results axis *contains* whiff. One word would have meant the physical profile here and the outcome there.
**Resolution:** `ff_elite_shape_flag`, with the client's name kept as a retired alias. Escalated (E-2).

**Whether to stabilize at all.** `eda-agent` found run value per 100 has a split-half reliability of 0.21 —
half-signal at ~1,084 pitches. `data-architect` proposed dropping run value from the results axis. The DPO
agent refused: dropping a metric because it is noisy is a definitional change dressed as a technical one.
**Resolution:** keep it, shrink it (SG-7). It now contributes in proportion to its evidence — near-nothing for
a 100-pitch reliever, meaningfully for a 1,300-pitch starter. The shrinkage decision rule (shrink when
reliability at the 50-pitch subject floor < 0.90) is written down so it can be challenged.

**The one-start leader.** The first build put Misiorowski #1 on the external board on 69 pitches.
`consumer-onboarding-agent` wanted him cut. `analytics-enabler` pointed out that his *shape* is reliable at 69
pitches (k < 1) and cutting him hides the most interesting fastball in the frame. **Resolution:** CB-1 — the
board requires the same 100-FF evidence as the population; everyone 50–99 goes on a visible watch list. He
leads the watch list and the report tells his story in its own paragraph.

**Nola's name in the needle.** The swap mechanic names the staff's lowest-scoring four-seam in each role:
Nola (SP), Richards (RP). `product-narrator` flagged that a coach reads "replaces Nola" as a roster
recommendation. **Resolution:** kept — it is the true accounting — but every surface calls it "the ledger", and
the report says in plain words that his game is built on the other three-quarters of his pitches.

**Plotly white vs plotly dark.** The brand-center MCP mandates `plotly_white` + Arial; every one of the
client's cells in this ask uses `plotly_dark`. **Resolution:** print surfaces follow the brand center (35/35
compliance); the dashboard offers the client's dark template as a one-click toggle. Escalated (E-5) — the
brand center and the notebook disagree, and only the DPO can say which one is the standard.

## 7 · Escalations to the human DPO

1. **E-1 · Ratify SG-1 / SG-2.** This is their independent second use: new population (405 vs 232), normality
   re-tested, rank twins ≤ 5 apart, skew flag silent. **Recommend ratify.**
2. **E-2 · Approve the rename** `ff_elite_stuff_flag` → `ff_elite_shape_flag`, or overrule it and re-name SG-4.
3. **E-3 · Pull full seasons for the watch list's top arms** (Misiorowski, Mason Miller, Megill, Greene). One
   `get_player_data` call each moves them onto the board or off it.
4. **E-4 · Is "not MLB-wide" permanent?** If this engine becomes a trade board, it needs a league-wide pull —
   a data-sourcing project (T-shirt: 1 UC), not an analytics one.
5. **E-5 · Brand standard:** `plotly_white` (brand center) or `plotly_dark` (notebook practice)?
6. **E-6 · Seven provisional objects** (FR-1, NR-1, AF-1…AF-6, SG-6, SG-7, CB-1). Ratify on second use; the
   cheapest is a second archetype on the same engine (`03` §6).

## 8 · Publish recommendation

**READY-CONDITIONAL — internal, need-to-know.**

- **C1** Grades are relative to a **bounded, non-MLB-wide frame**. Any external use of a grade carries that sentence.
- **C2** Aspirational only. No row of the external board is a trade recommendation.
- **C3** Bowlan-out scenarios are client carry-ins, not data.
- **C4** McFarlane (94 FF) and every watch-list arm are THIN. Read ±1 grade.
- **C5** All new objects are provisional; no downstream build may treat AF-* as ratified.
- **C6** Anchored to a log ending 2026-09-20; the build refuses a different anchor. A refresh is v1.1.0.

External publication: **blocked** (other clubs' players named in a Phillies acquisition context).
Distribution: DPO, front office, pitching coach, pitching analyst.
