# BID — José Alvarado 2026 season recap (Phillies tenure lens): "The Full Ride"

**Status:** FILED 2026-10-18 10:57 ET · **AWARDED 2026-10-18 10:57 ET (Tier A)**. Per the RFP, the exercise treats this bid as the winner, so the build proceeds in the same turn without a stop. Actuals are reconciled in `07_platform_marketing.md` §3.
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-10-18 (10:57 ET; T0 wall clock 10:48→10:57 = 9 min)
**ID reservation:** UC **#53** · contract `uc-pps-037` · build artifact `dp_uc53` · folder `uc-pps-037-alvarado-2026-recap-001`
**Collision check (bid time):** `dp_uc53*`: none at the MLB root, in `out/` or in the control plane. `uc-pps-037*`: no claim; it appears only as "next available" in `uc_ledger_AI_PATCH_uc-pps-036-mayza-2026-recap.md` and UC52 `07` §6. Prior Alvarado work: `uc-pps-016` (multi-stint workload flag, stopped at scaffolding; nothing to inherit but the MLBAM id).
**Working title:** "The Full Ride", from the client's line that in one season the Phillies "captured nearly the full ride" of the José Alvarado Experience. The DPO can rename it.

---

## Audit Phase 2 counters (session token counter, tokens left)
| Mark | When | Counter | Δ | Cumulative |
|---|---|---|---|---|
| C0 | Session start (request delivered) | 15,000,000 | — | 0 |
| C0' | First visible reading (after first-turn load + tool-schema load) | 14,869,738 | 130.3k | 130.3k (first-turn load) |
| C1 | After `uc-house-format` card, ledger tail, UC52 BID/README/00/07, UC52 kernel + build | 14,787,802 | 81.9k | 212.2k |
| C2 | End of T0 (render stack, data profile, Rule-1, carry-ins, skeletons) | 14,743,344 | 44.5k | 256.7k |
| C3 | BID filed | read in `07` | | |

- **First-turn load ~130k** (system prompt, skill listings, the client notebook). Repo work in T0 net of it: **~126k**, about double UC52's ~62.5k. Why: this run opened the UC52 kernel and build script **in full** (~13k + ~16k) to inherit from them, read 7 skeletons (00, 03, 05, 07, README, contract, BID + recap report), and lost two calls to a device pip failure (see "Data position").
- **House-format read (tokens):** card 4.5 KB + ledger tail + 8 skeletons (~21 KB) ≈ **~7k tokens of content**.
- **Prior-UC files opened:** UC52 control-plane folder: README, 00, BID, 07, ledger patch, kernel (full), build (full). Kernels at MLB root by **function excerpt only**: K49 `appearance_log`/`game_score` (lines 230–300), K48 `signature_verdict`/`strength_from_signatures` (344–380). One control-plane `03` excerpt (uc-pps-028 CN-3). `07` will count them.

## The ask (as submitted)
A notebook export (`c9ed969a-attachment.txt`) titled "Jose Alvarado": a closing note on "the last year of the José Alvarado Experience", plus code and claims across his whole Phillies tenure. Instructions from the RFP:
- (a) Work inside the MLB data plane; let the control-plane organization drive the build; follow the house receipts standard (00–07) and take inspiration from the scouting-report skill and prior recaps.
- (b) Follow the pattern of the other season recaps (UC48 Bowlan, UC49 Luzardo, UC51 Wheeler, UC52 Mayza).
- (c) Consider his **entire Phillies tenure**, since this is most likely the end.
- (d) Where appropriate, show how **2026 declined** relative to his prior performance.
- (e) If appropriate, argue **for moving on**, or argue it was **a blip** with another good year left.
- (f) Receipts in a control-plane `data-products/` subfolder in 00–07 format; outputs and artifacts in a control-plane folder.
- (g) Include a token and time estimate, framed as a competitive bid.

**Client claims to be graded (HP rows; reproduced by the client's own method before any governed restatement):**
| HP | Claim |
|---|---|
| HP-01 | Since 2015 he has been on the mound for the 14th-most plate appearances for the Phillies; Héctor Neris is the only full-time reliever with more |
| HP-02 | Phillies tenure: .300 wOBA, .668 OPS against, 399 strikeouts |
| HP-03 | His two best seasons were 2022 and 2023; 2023 was excellent; "he must have missed some time with injury" |
| HP-04 | 2022–23: ~35% K, <10% BB, BA against just above .200 |
| HP-05 | Cutter (tenure): in zone 28% of the time, 38% chase (~1,400 out-of-zone pitches), ~52% K rate, 48% whiff, 26% putaway |
| HP-06 | Cutter putaway is elite among Phillies pitcher × pitch combos (≥20 two-strike pitches) |
| HP-07 | Cutter velocity trending down |
| HP-08 | In 2026 the cutter's whiff rate "fell off a cliff"; 2026 whiff ≈ 39% (the client's hard-coded `hline` at 0.39) |
| HP-09 | The cutter went from among the most elite swing-and-miss pitches to "just very good" |
| HP-10 | 2026 was "remarkably inconsistent, sometimes reliable" (cumulative wOBA-against chart) |

## Why this shop wins this RFP
1. **We inherit instead of re-deriving.** The recap spine comes from the UC52 kernel by sha256-pinned import (`3667f802…`). Through it come UC51 and K49/K50/K48/K44/barrel_rate: nresults, whiff/chase/putaway, hard-hit, barrel, xwOBA (XW-1) with its same-basis wOBA companion (WB-1), runs on watch, house percentiles, the season card, the career frame (CF-2c), and the RP-1 reliever role. The client's own cumulative chart is a house module, `cumulative_metric.py` (sha `a2888740…`), whose docstring already names the Alvarado wOBA-against chart, so we import it rather than redraw it. Per-appearance outs, K, BB, H, HR and runs come from K49 `game_score` (GS-1). The decline-or-blip argument runs on K48's pre-registered decision rule (PA-1 `signature_verdict` / `strength_from_signatures`). **Every bar in the argument is written down before the 2026 numbers are read.**
2. **We checked the premise before bidding** (carry-ins, sourced, never computed on):
   - CI-1: club option exercised for 2026, $9M (CBS News, Nov 2025).
   - CI-2: listed as a free agent after 2026 (NBC Sports Philadelphia, 2026-10-02).
   - CI-3: 80-game PED suspension announced 2025-05-18; ineligible for the 2025 postseason (6abc).
   - CI-4: optioned to Triple-A Lehigh Valley in May 2022 with a 7.62 ERA in 13 IP (SI).
   - CI-5: reinstated from the 15-day IL 2023-06-09 (MLB.com release). **No medical inference.**
   - CI-6: mid-2026 role reduced; MLB.com (2026-07-04) cites a 3.82 xERA against a 6.10 ERA at the time.
   - CI-7: season line 5.86 ERA, 68 G, 58⅓ IP, 70 K (NBC, 2026-10-02). Display only; we report runs on watch.
   - CI-8: "Mr. Punchie"; Caleb Cotham credited with the cutter (both from the client).
   - The "is it the end?" premise is CI-2 plus the client's view. We argue both cases and say which one the evidence favors.
3. **We pre-register the argument.** DB-1, the "decline-or-blip" ledger, is 8 signatures with bars written in `03` §2 **before** the 2026 values are read. Each signature is scored with the inherited PA-1 rule against his 2022–24 Phillies baseline. Decline signatures are arm and stuff: velocity, cutter whiff, chase, zone rate, K−BB. Blip signatures are luck and sample: xwOBA vs same-basis wOBA, BABIP-type contact quality, and the share of damage in a few outings. The verdict follows the roll-up, flattering or not.
4. **We found three source traps before the build.**
   - **ENT-1:** 9 rows in `phils_2018.parquet` carry `pitcher == 621237` under the batter's name "Santana, Carlos" (Alvarado pitched for TB against the Phillies). An id lock without `role="pitching"` leaks them into the tenure. The house loader's pitching role excludes them, and DQ asserts it.
   - **SRC-1:** the client's `pps` frame has no `game_type` filter. 53 spring pitches (2026) and 335 postseason pitches (2022–24) sit in the client's tenure totals. HP-01 to HP-05 are reproduced on the client's frame, then restated regular-season only.
   - **DEF-1 (client chart):** the whiff scatter draws a hard-coded `hline` at 0.39 labelled "2026 Whiff". We recompute it and print the computed value.
5. **We build where the data lives.** Everything runs on the laptop VM against the parquet layer, with nothing staged. The device home (`/sessions`) is 100% full, and pip's temp dir also lives there. The first install failed with ENOSPC until `TMPDIR` was moved to `/tmp` (new environment finding **ENV-3**, recorded in `04`). Outputs and artifacts go to the control-plane folder (the convention since UC52 was moved off the MLB root after its commit). Kernels are imported from the MLB root by path.

## Data position (verified at bid time, not assumed)
| Check | Result |
|---|---|
| Phillies logs | `data/phillies/phils_2015…2026.parquet`. 2026 has 52,863 rows; max `game_date` 2026-10-01 (pinned anchor) |
| Entity lock | MLBAM **621237**, LHP. 2026 regular season: **1,145 pitches, 68 games**, 2026-03-28 → 2026-09-26. No 2026 postseason rows. 53 spring pitches excluded |
| Phillies tenure (regular season) | 2021: 1,045 / 64 G · 2022: 881 / 59 · 2023: 742 / 42 · 2024: 1,052 / 66 · 2025: 457 / 28 (CI-3) · 2026: 1,145 / 68 |
| Postseason (own ledger) | 2022: 200 pitches over 12 G (F, D, L, W) · 2023: 113 / 8 · 2024: 22 / 1 |
| Career file | `data/opponents/alvarado.parquet`, id 621237 only, TB 2017–20 (regular season 2,281; 2020 ALCS rows kept out of rates) |
| Opponent-file exposure by id | 27 files |
| Environment | plotly 6.0.1, pandas 2.2.3, weasyprint 70.0, kaleido 0.2.1 installed to `/tmp/pyrender` (TMPDIR=/tmp). Lineage UC52 → UC51 → K49/K50/K48/K44/barrel_rate asserts clean. `phillies_dp.selftest` 3/3 |

## Rule-1 search (file-name and function hits; full table goes to `03` §0)
| Need | Hits | Disposition |
|---|---|---|
| Season card, career frame, house percentiles, runs on watch, xwOBA + WB-1, RP-1 | UC52 kernel | **Inherit** (pinned) |
| Cumulative wOBA by PA | `cumulative_metric.py` (house module) | **Inherit** (pinned) |
| Per-appearance line (outs, K, BB, H, HR, runs) | K49 `game_score` (GS-1) / `appearance_log` (US-1b) | **Inherit** |
| Pre-registered verdict rule | K48 PA-1 `signature_verdict` / `strength_from_signatures` | **Inherit** |
| Velocity by outing | K48 VE-1, K49 VB-1 | Inherit if a figure needs it |
| Blow-up / clean outing | uc-pps-028 CN-3 (**starts only**: runs ≥5 or outs <12; provisional, `03` only) | **New, provisional OD-1** (relief outcome bands). CN-3's start thresholds don't transfer |
| Decline vs blip | **0 hits** | **New, provisional DB-1** (signature set on PA-1) |
| CSW% | to check in T1 | Inherit, or provisional CS-1 (client formula) |

## Product types explored
| # | Form | The part of the story it owns | Bid |
|---|---|---|---|
| P1 | PDF recap report (≤10 pp, ≤9 sections) | Tenure, decline evidence, the argument, HP grades | **Build (hero)** |
| P2 | Interactive dashboard (≤8 chapters) + Artifact | Year-over-year cutter and sinker exploration, outing log | **Build**: keeps the UC48/49/51/52 shape |
| P3 | Front-office decision memo (one page) | "Re-sign or let walk" | **Folded into report §8**, no separate form, so the consumable doesn't balloon |
| P4 | 2027 projection / ML | Probability of a bounce-back | **Not bid**: no projection model in the house; DB-1 is the governed substitute |
| P5 | Tenure highlight video | Signature moments (2022 World Series run) | **Not bid**: out of profile |

## Scope tiers (pick one)
Comparison-profile cap for every tier: report ≤10 pp / ≤9 sections · dashboard ≤8 chapters · ≤10 figures · ≤3 new KPIs.

**Tier A — Comparison profile (recommended, AWARDED).**
- **Report, 9 sections:**
  1. Bottom line
  2. Five years in red pinstripes (tenure leaderboard, year table)
  3. 2026 against his own standard (results, wOBA vs xwOBA on one basis)
  4. The cutter
  5. The sinker and velocity
  6. Command
  7. The ride: inconsistency (outing bands, cumulative wOBA)
  8. Move on or a blip? (DB-1)
  9. Your notebook, graded + caveats
- **Dashboard:** sections 1–8 as chapters.
- **10 figures:**
  - F1: Phillies PA leaderboard 2015–26
  - F2: career wOBA/xwOBA by year
  - F3: cutter putaway vs pitches (house pitcher × pitch)
  - F4: cutter whiff vs pitches (pitcher × pitch × season)
  - F5: cutter 2×2 metrics by year
  - F6: sinker and cutter velocity by year
  - F7: command by year (zone, chase, BB%)
  - F8: outing bands by season
  - F9: cumulative wOBA against by season
  - F10: DB-1 signature ledger
- **≤3 new KPIs:** OD-1 outing outcome bands · DB-1 decline-or-blip ledger · CS-1 CSW% (only if Rule-1 finds none).

**Tier B — Tier A plus extras (≈ +80k, +6 min).** Persona card · postseason tenure ledger page (2022 run) · a TB-vs-PHI pitch-design comparison. Breaks comparability (+1 page, +2 figures).

**Tier C — Lean (≈ −140k, −10 min).** PDF only; 6 figures (drops F3, F4, F7, F8); DB-1 only.

**Deferred: priced, not built:** postseason ledger page (~8k) · persona card (~35k) · MLB-wide context (not bid: house population rule) · 2027 projection (not bid).

## Deliverables bid (Tier A)
| # | Deliverable | Notes |
|---|---|---|
| 1 | `dp_uc53_alvarado_2026_recap_report.pdf` (+ `.md`) | ≤10 pp, 9 sections |
| 2 | `dp_uc53_alvarado_2026_dashboard.html` (+ `_artifact.html`) + Artifact | ≤8 chapters; plotly via `phillies_dp.render.plotly_script_tag()` |
| 3 | `dp_uc53_kernel.py`, `_alvarado_recap.py`, `_hp.py`, `_build_figs.py`, `_narrative.py`, `_build_dashboard.py`, `_build_report.py`, `_build_pdf.py`, `_verification.py` | Control-plane folder; MLB kernels imported by path |
| 4 | `out/dp_uc53_*`: CSVs, fig JSON+PNG, `headlines.json`, `dq_scorecard.csv`, `verification_log.csv`, `hp_grades.csv` | Every narrative number comes from `headlines.json` |
| 5 | Receipts `00`–`07`, README, this BID, contract, ledger patch | Control-plane folder (contract + ledger patch copies at MLB root) |

**Explicitly not bid:** ERA as computed (runs on watch instead; CI-7 shown as a labelled carry-in) · medical inference (2023 IL, CI-5) · any inference about the 2025 suspension's effect on performance · MLB-wide ranks · postseason in any rate.

## Price (Tier A)
**Basis:** UC52 Mayza actuals, the closest profile (LHP reliever, same shape): **~469k** (205.7k T0 + 262.8k build), 35 min, adjusted by the house calibration rules (C-2: build tranches over-bid 35%, so drop T1 −20k and T6 −20k; C-3: T4 ~12k with a narrative module).
- **Up** for: a six-season tenure frame plus TB career (vs. one season), a pre-registered argument card (DB-1), the T0 overrun above (sunk), and two client scatters that need house pitcher × pitch populations.
- **Down** for: 10 HP rows (UC52 had 14), a single turn (no re-read after the award), and inherited cumulative and appearance machinery.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, two-repo recon, house format, carry-ins, env, data profile, Rule-1 (**sunk: 256.7k on the counter at C2, gross**) + filing this BID | ~254k | ~10k | 9 |
| T1 Kernel + build + HP reproduction + EDA to file | 70k | 15k | 7 |
| T2 Figures (10) + brand + palette + render QA | 42k | 13k | 5 |
| T3 Dashboard (8 chapters) + headless QA + Artifact | 33k | 12k | 5 |
| T4 Report + PDF (narrative module) | 8k | 6k | 2 |
| T5 Verification harness (families A–G + OD-1/DB-1) | 25k | 10k | 3 |
| T6 Governance 00–07, README, contract, ledger patch | 35k | 20k | 5 |
| D Defect discovery | 10k | 3k | 2 |
| Contingency 10% (on unsunk work) | 24k | 7k | 3 |
| **BID** | **~501k** | **~96k** | **~41 min** |

**Total ≈ 597k**, against 469k (UC52) / 530k / 545k / 681k for the comparison set.
- **Time cross-check:** 0.10 min per 1k × 0.7 (device build) × 597k ≈ 42 min.
- **Token credits** at list ($10/M in, $50/M out) ≈ **$9.80**, band **$8.30–11.30** (±15%). Cowork bills subscription usage; read this as API-equivalent value.

### Competitive position (how this bid compares with a rival agentic org)
A rival shop without this repo's inheritance would have to re-derive wOBA weights, the reliever role, the house percentile, runs on watch and the cumulative chart, and discover the ENT-1 and SRC-1 traps the hard way. Our estimate of that rival bid is **~0.9–1.1M tokens and 60–75 min**: about +350k for re-derivation and +100k for defect loops (UC44–UC49 history). It would also lack the 00–07 receipts and an independent harness. Our differentiators:
1. Pinned inheritance, so numbers are comparable with UC48–52.
2. A pre-registered verdict instead of a narrative fitted after the fact.
3. Client claims graded, never overwritten.
4. An instrumented bid with a public bid-vs-actual history (UC48–UC52 within −28% to +5%).

### House calibration rules (carried; update from `07` §4)
- T0 is priced from the live counter at bid time (sunk work). Report gross and net of the first-turn load.
- Output: 0.8× scope-scaled for recaps built with a report builder.
- Build tranches: UC52's −35% over-bid is applied (T1 −20k, T6 −20k).
- T4: ~12k when a narrative module exists (bid 14k).
- Fixed lines: render QA ~12k · skill loads ~15k (dataviz; artifact-design) · defect discovery ~13k.

## Pre-registered `05` catches (found at intake; `05` will tag each "intake could have caught: Y/N")
| # | Catch | Intake could have caught |
|---|---|---|
| ENT-1 | 2018 rows with `pitcher == 621237` under a batter's `player_name` | Y (caught) |
| SRC-1 | Client `pps` mixes spring (53) and postseason (335) pitches into tenure totals | Y (caught) |
| DEF-1 | Whiff scatter `hline` hard-coded at 0.39 and labelled as the 2026 value | Y (caught) |
| DEF-2 | Client scatter titles say "fucntion" (typo) and the putaway scatter's floor comment says 17 while the filter is >19 | Y (caught; cosmetic) |
| ENV-3 | pip ENOSPC from `TMPDIR` on the full `/sessions` volume | Y (caught at T0) |

## Assumptions, exclusions, carry-ins
- Regular season for every rate; postseason (2022–24) gets its own ledger line with denominators.
- Entity lock by MLBAM id 621237 with the pitching role, never by name (names only to reproduce the client frame).
- Population claims are tested in the client's own population (HP), then restated in the house population (Phillies pitcher-seasons 2015–26; reliever = RP-1), with rank and n.
- "Tenure" = Phillies regular seasons 2021–26. TB 2017–20 appears only in velocity and stuff trends, labelled.
- Carry-ins CI-1 to CI-8 are labelled at every use and never computed on.
