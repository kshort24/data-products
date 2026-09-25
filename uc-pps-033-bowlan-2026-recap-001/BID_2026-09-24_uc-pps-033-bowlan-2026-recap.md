# BID — Jonathan Bowlan 2026 Recap: "The Tick and a Half"

**Status:** **AWARDED 2026-09-24** (RFP exercise: bid filed, then treated as the winner per Kellen's instruction; actuals are reconciled in `07_platform_marketing.md` §3)
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-09-24 (23:58 ET)
**ID reservation:** UC **#48** · contract `uc-pps-033` · build artifact `dp_uc48` · folder `uc-pps-033-bowlan-2026-recap-001`
**Collision check (bid time):** `dp_uc48*`: none at the MLB root, none in `out/`, none in the control plane. `uc-pps-033*`: none. The ledger file still says "next #25" (known drift). Ground truth is the `uc-pps-032` patch, which says **next #48**.

---

## The ask (as submitted)

Three notebook cells in `September 2026.ipynb` (cells 115–117). Kellen wrote the first and third himself and Gemini Flash wrote the middle one:

1. **Kellen: the recap table.** The opening comment is *"functionalize that so I can use a similar analysis on Jonathan Bowlan."* The cell builds a career-by-season KPI table from 19 KPIs (slash line, wOBA, K/BB/HR rate, runs created, games, RC per PA and per game, four-seam velo/spin/vert, breaking-ball whiff, in-zone four-seam whiff). A `kpis_comments` list attaches **14 claims** to it, and one of them has a hole in it: *"Boost to an elite 32% K Rate (**xxth Percentile**)"*.
2. **Gemini: a 2×2 box-plot grid** of four-seam velocity, spin, and horizontal and vertical break by season.
3. **Kellen's reply: "A simpler view."** Four scatters: velo × spin by season; four-seam movement by season; Bowlan's four-seam against every other Phillies right-hander's (2017 excluded as "outlier data", with his middle-50% vertical-break band shaded); and his whole arsenal against Phillies RHP. The last one carries the note *"If the above were a DT, it could come from this view."* That is a drill-through he asked for without calling it a requirement.

Instructions that came with it: (a) interactive dashboard preferred; (b) **weave a narrative of Bowlan's season into the interactivity**; (c) **lean into the actions people in the Phillies pitching value stream could have taken to drive these results**; (d) a fully governed package with receipts `00`–`07`; (e) scouting-report inspiration; (f) data-plane coding standards.

## Why this shop wins this RFP

1. **We already graded this four-seam, one UC ago.** `uc-pps-032` graded Bowlan's 2026 four-seam **#2 of 405** RHP pitcher-seasons in the house frame and his 2025 (Royals) four-seam **RESULTS-ONLY**. A competitor would re-grade it. We **inherit the receipt** and ask the question that receipt raises: *what changed between a results-only 2025 and an elite 2026?* The client's own velocity chart already holds the answer, which is the tick and a half.
2. **We know what the client's `pitch_mix` does to "vert".** `pitch_mix` rounds `pfx_z` to 0.1 ft *before* the ×12, so vertical break can only move in **1.2-inch steps**. "Vert remained elite at 18 inches" prints 18.0 for both 2025 and 2026 because of that quantization. The unrounded values are different. A shop that copies the cell copies the artifact. We bid it as a reconciliation finding with a one-line fix.
3. **We fill the client's `xxth` instead of guessing it.** A percentile needs a population, and the house has one: *Phillies pitcher-seasons 2015–2026 with at least 100 PA* (Kellen's own "Phillies pitcher-seasons" idiom from the Luzardo cell). It is declared, floored and labelled "not MLB-wide" (the uc-pps-032 C1 precedent).
4. **"Actions people could have taken" is priced as evidence, not a story.** Each persona gets a **hypothesis → data signature → strength → what would confirm it** row, and the signature is computed from the log. Where the data cannot see the action (a bullpen session, a cue from the pitching coach), the row says so. No competitor that writes persona narratives can prove which parts are data and which parts are story. We can, because the verification harness checks every narrative number against a receipt.
5. **The carry-in is already stale, and we checked.** The client's notebook (and `uc-pps-032`) recorded a *suspected oblique* on 9/17. Reporting since then describes a **right groin strain with no IL placement** (Philadelphia Inquirer, 2026-09-18). We re-verify carry-ins before we reuse them.

## Data position (verified at bid time, not assumed)

| Check | Result |
|---|---|
| Phillies logs | `phils_2015…2026.parquet`, 554,828 rows, current through **2026-09-23** (3 days fresher than uc-pps-032's anchor) |
| Bowlan, entity lock | MLBAM **680742**. 2026: **967** regular-season pitches in **59** games (last game 9/17). Also 47 spring-training rows, which are excluded |
| Bowlan, pre-Phillies | `data/opponents/bowlan.parquet`: 2023 (56 pitches, 2 G), 2024 (68, 1 G), 2025 (727, 34 G). All regular season, all id 680742 |
| Cross-source duplicates | **19** pitches (KC @ PHI, 2025-09-13) are in both `bowlan.parquet` and the Phillies log (batting role). The client's frame avoids double-counting only because `pps` is pitching-role. The governed frame dedups by key |
| `nphl` exposure | "Bowlan" appears in **only** `bowlan.parquet` among the 128 opponent files (byte search on the device), so a name filter over `nphl` equals this one file |
| Inherited receipts | `out/dp_uc47_population_graded.csv` (Bowlan 2025 and 2026 grades), `dp_uc47_cohort_seasons.csv` |
| Client number drift | Notebook says ".269 wOBA" and "60 games". The current log says .272 and 59. We price a **cache-state probe** to find which data state produces the notebook's numbers |

## Deliverables bid

| # | Deliverable | Notes |
|---|---|---|
| 1 | **Interactive season dashboard** (hero) | Self-contained HTML, offline, and narrative-first. Six chapters. A **persona lens** re-reads every chapter through Front Office / Pitching Coach / Pitching Analyst / Catcher / Manager / Pitcher. The **drill-through** the client sketched runs from the arsenal-vs-staff plot to the single-pitch comparison. The client's `plotly_dark` is the default and brand light is a toggle |
| 2 | Governed kernel `dp_uc48_kernel.py` | Imports `dp_uc44_kernel` (sha256-pinned). Transcribes `runs_created` (approved, uc-pos-012) and `xwobacon` (uc-pps-021 O1) verbatim. **`season_recap(pitcher_id)`**: the client's cell, functionalized as he asked |
| 3 | Reader report `.md` + `.pdf` | Recap voice: bottom line first, data-window box, candid caveats |
| 4 | Persona Action Ledger | Hypothesis, signature, strength, confirmation for each persona. Hypotheses, never attributions |
| 5 | Human-parent reconciliation | The 14 `kpis_comments` claims plus 4 chart subtitles plus the Gemini cell, each reproduced by his method, then governed, with a verdict |
| 6 | Receipts | `00`–`07`, README, this BID, and about 25 CSV receipts |
| 7 | Verification harness | Families A–F, including F = every number the report prose and dashboard narrative assert |
| 8 | Ledger patch + repo-side contract | `uc_ledger_AI_PATCH_…` and `uc-pps-033-Jonathan Bowlan 2026 Recap 20260924.md` |

**Explicitly not bid:** re-grading the four-seam (inherited from uc-pps-032); any claim about what a coach *actually* did or said (no such record exists in either repo); injury modelling (carry-in only); 2027 projection; MLB-wide percentiles (no league-wide pull exists; see uc-pps-032 E-4).

## Price

**Basis:** `uc-pps-032` actuals (~525k tokens in, ~110k out, ~51 min).
**Down** for 16 staged files instead of 140. Per calibration finding C-1, T0 is priced by file count, which removes about 70% of the analogue's T0. No new population engine is needed, and the grades are inherited.
**Up** for a narrative dashboard with a persona lens and drill-through (bigger than the analogue's explorer), and for an 18-claim human-parent reconciliation plus the Gemini cell.
Output is priced at **0.5× the analogue** (C-2: five of five bids over-bid output). Contingency is **0%** (C-5: warm sandbox, bridge proven this session). **A defect-discovery line is priced for the first time** (C-4).

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, recon (two repos), 16-file staging, source profile (**sunk at bid time: ~100k**) | 110k | 8k | 10 |
| T1 Kernel + build + receipts + cache-state probe | 45k | 18k | 8 |
| T2 Figures (6) + brand-center compliance | 30k | 10k | 5 |
| T3 Narrative dashboard (6 chapters, persona lens, drill-through, theme toggle) | 35k | 25k | 10 |
| T4 Reader report + PDF | 25k | 14k | 6 |
| T5 Verification harness A–F | 20k | 10k | 4 |
| T6 Governance 00–07, README, contract, ledger patch, commit | 30k | 35k | 12 |
| D Defect discovery (new, C-4) | 10k | 3k | 2 |
| Contingency 0% | 0 | 0 | 0 |
| **BID** | **~305k** | **~123k** | **~57 min wall clock** |

**Token credits** at list rates ($10/M in, $50/M out): 305k × $10/M + 123k × $50/M ≈ **$9.20**, band **$7.50–11.00**.
Cowork bills subscription usage, so read this as API-equivalent credit value. It is **about half** the uc-pps-032 bid ($18.20) for a single-subject recap, and 15% under that UC's actual ($10.75).

**De-scope options priced:**
- Drop the dashboard (report only) → −25k out, −10 min, about −$1.60. *Not recommended.* The persona lens is the part of the ask that prose cannot carry.
- Report-only tier (no 00–07, no harness) → about **$4.50**.
- Recap table only (the client's cell, functionalized and reconciled) → about **$2.75**.

## Assumptions, exclusions, carry-ins

- **Regular season only.** Spring training (47 Bowlan rows in 2026) is excluded at load. The client's notebook excludes it too (`~game_type.isin(['S','E'])`).
- **Entity lock by MLBAM id, never by name.** The name filter the client used is reproduced once, in the reconciliation, to show that it matches.
- **"Elite" means the uc-pps-032 archetype bar** (≥60 on both axes) for the four-seam, and the house percentile KP-1 for rates. No other superlative is used without a named population.
- **Persona actions are hypotheses.** Neither repository records coaching instructions, bullpen sessions or pitch-design work. The ledger reports the signature an action would leave and whether that signature is present.
- **Carry-ins:** the Strahm-for-Bowlan offseason trade (MLB.com); the 9/17 exit, reported as a right groin strain with no IL stint (Philadelphia Inquirer, 2026-09-18). Neither is ever computed on.

---

> **STATUS UPDATE 2026-09-24: AWARDED.** Proceeding per Kellen's instruction to treat the bid as won.
> Actuals vs. bid are in `07_platform_marketing.md` §3. The delivery spine is `00_dpo_orchestration_record.md`.
