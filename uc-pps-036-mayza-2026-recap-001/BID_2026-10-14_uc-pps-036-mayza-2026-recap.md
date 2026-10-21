# BID — Tim Mayza 2026 season recap: "Come and Get It"

**Status:** AWARDED 2026-10-14 00:35 ET (Tier A; DPO retitled the product "The Sheriff of the Phillies Bullpen"). Actuals will be reconciled in `07_platform_marketing.md` §3.
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-10-14 (00:21 ET; T0 wall clock 00:13→00:21 = 8 min)
**ID reservation:** UC **#52** · contract `uc-pps-036` · build artifact `dp_uc52` · folder `uc-pps-036-mayza-2026-recap-001`
**Collision check (bid time):** `dp_uc52*`: none at the MLB root, in `out/` or in the control plane. `uc-pps-036*`: no claim; it appears only as "next available" in `uc_ledger_AI.md` and in the UC51 patch/`07`.
**Working title:** "Come and Get It", from the client's note that he throws the sinker down the middle more than half the time. The DPO can rename it.

---

## Audit Phase 2 counters (session token counter, tokens left)
| Mark | When | Counter | Δ | Cumulative |
|---|---|---|---|---|
| C0 | Session start (request delivered) | 15,000,000 | — | 0 |
| C1 | After the `uc-house-format` skill and the ledger tail | 14,838,293 | 161.7k | 161.7k |
| C2 | End of T0 (ID claimed, carry-ins, id scan) | 14,808,457 | 29.8k | 191.5k |
| C3 | BID filed | 14,795,398 | 13.1k | **204.6k** gross · **~75.6k** net of the first-turn load |

**Read this before comparing against the 236k T0 baseline.** About **129k of C0→C1 was the first-turn load**: system prompt, skill listings and the ~15k-token client attachment. That load came before any repo read. T0 net of it is **~62.5k at C2**. Whether earlier UCs' counters included the same load isn't recorded, so `07` will report both the gross and the net figure.
- **House-format read:** `SKILL.md` (4.5 KB), the `BID.md` skeleton and the 20-line ledger tail come to **~3k tokens of content**, **~9k on the counter step**. The baseline line was 70k.
- **Prior-UC files opened: 0.** No UC48–51 folder, kernel, build or receipt was opened. Rule-1 used `grep -l` (file names only) across `dp_uc*_kernel.py`, `phillies_dp/*.py` and the control-plane `03` files. The cost comparison used `audit/cost_summary.csv` and `audit/hotspots.csv`, which are audit outputs, not UC files.
- **Client code:** the protocol's `<path/to/file>` placeholder was left unfilled. The code was read **once** from the attached notebook export. `tm_success_rate` was read once from its source, `July 2026.ipynb` cell 137, by cell extraction, not by opening the notebook.

## The ask (as submitted)
The client submitted a notebook export (Mayza's season recap) with code and claims. Its questions:
- (a) What did he do well? The client's thesis is that he threw strikes, got quick outs and avoided traffic, an "old-school" approach.
- (b) How were his platoon splits?
- (c) Was his stuff exceptional, especially his release point?
- (d) Was the success sustainable? Look at contact (HH%, barrel%, EV, xBA, xwOBA, xSLG), whiff, chase, K% and BB%.
- (e) How does 2026 compare with Mayza historically (results and indicators) and with Phillies LHP relievers historically (results only)? Which Phillies LHP is most similar by stuff, delivery and release?
- (f) Revisit the "Tim Mayza Success Rate".

Constraints: the shared work is inspiration and need not all ship; don't let the consumable balloon; keep it comparable with the other season recaps (UC48 Bowlan, UC49 Luzardo, UC51 Wheeler). Deliverables: a PDF report and a fully governed package, with an interactive dashboard if it makes sense.

**Client claims to be graded (HP rows, reproduced by the client's own method in T1 before any governed restatement):**
| HP | Claim |
|---|---|
| HP-01 | Third-lowest wOBA and OPS against of his career |
| HP-02 | Three-true-outcome rates in line with prior seasons |
| HP-03 | Highest hard-hit rate since his rookie year; more air, more distance |
| HP-04 | Barrel rate only the sixth-lowest of his career, yet the third-lowest wOBA ("expect a higher wOBA given the barrels") |
| HP-05 | Release point "bang average" among Phillies LHP |
| HP-06 | FF doesn't ride, SL doesn't sweep, SI vanilla, splitter unique |
| HP-07 | Bullet slider rare among Phillies LHP (Sanchez, Vasquez; maybe Banks and Morgan) |
| HP-08 | SL usage right at ~30% |
| HP-09 | Elite extension among Phillies LHP |
| HP-10 | Slightly better vs LHB; vs RHB more Ks and BBs, 7.8% barrel rate, 49% hard-hit |
| HP-11 | SI pretty much down the middle more than half the time, to both sides |
| HP-12 | SL whiff abnormally low vs LHB, good vs RHB; "SL is the weapon vs RHB, SI vs LHB" |
| HP-13 | Career quick-AB success ≈ 40% over ~1,500 PA (July 2026) |
| HP-14 | "Jose Alvarado lite" |

## Why this shop wins this RFP
1. **We inherit instead of re-deriving.** The recap spine comes from the UC51 kernel by sha256-pinned import: season card OC-1, career frame CF-2b, house percentiles, `runs_created` ("runs on watch"), pitch maps, release and extension. Rule-1 hits on file names confirm all of it exists. The only new code is the three KPIs below.
2. **We checked the premise before bidding.** Mayza was claimed off waivers from PIT on 2025-08-31 while on the 60-day IL (MLBTR). An MLBTR headline says the Phillies re-signed him to an MLB deal; the date and terms aren't verified. His 2027 status ("should he be back") is **unverified** and stays a labelled carry-in. We make no medical inference about the 2025 IL stint.
3. **We pre-register the client's own metric.** "Tim Mayza Success Rate" gets a provisional `03` §2 spec before any code. **The code doesn't match the stated definition:** `strikes` is the *pre-pitch* count. So `max_strikes == 2` over `pitch_number < 4` means two strikes within **two** pitches: a 1-1 → 1-2 third pitch is missed, and a three-pitch strikeout counts. We reproduce the client's version as HP-13, then ship the corrected definition beside it. Neither overwrites the other.
4. **We found two source traps before the build.**
   - The client frames carry **no `game_type` filter**. Phillies 2026 data has 66 spring and 6 postseason Mayza pitches next to 1,093 regular-season pitches.
   - The root `pp26.csv` is **stale**: 134 Mayza pitches, dated Apr 16. If the platoon cells read it, HP-10 to HP-12 move.

   The house rule (regular season only, postseason in its own ledger) fixes the first trap, and the HP reproduction tests the second.
5. **We build where the data lives.** The device home (`/sessions`) is 100% full, so the render stack was installed to `/tmp/pyrender` with `pip --target`, the UC49 pattern. Nothing gets staged. The build, figures and PDF run on the laptop VM against the parquet layer.

## Data position (verified at bid time, not assumed)
| Check | Result |
|---|---|
| Phillies logs | `data/phillies/phils_2015…2026.parquet`; 2026 has 52,863 rows, max `game_date` 2026-10-01 |
| Entity lock | MLBAM **641835**, LHP. 2026 regular season: **1,093 pitches, 60 games**, 2026-03-28 → 2026-09-25. 643 pitches vs RHB, 450 vs LHB |
| Postseason (own ledger) | 1 game, 6 pitches (F, 2026-10-01) |
| Career file | `data/opponents/mayza.parquet`, id 641835 only. Regular season 2017–19 and 2021–25 (no 2020 rows). 2025 has 162 pitches (partial season). Postseason rows 2022–24 are kept out of rates |
| Opponent-file exposure by id | 22 files. `mayza.parquet` has 5,221 rows; the rest are batter files with incidental matchups |
| House LHP population | 86 Phillies LHP pitcher-seasons (regular season, any n, 2015–26). The reliever subset and min-PA floor are set in `03` |
| Carry-ins | CI-1: waiver claim 2025-08-31 (MLBTR). CI-2: re-signed to an MLB deal (MLBTR headline; date unverified). CI-3: 2027 status unverified. CI-4: Pattison interview, "two strikes or a grounder within 3 pitches" (as the client's notebook paraphrases it; primary source not fetched). CI-5: "#37, The Sheriff" (client) |
| Environment | Device `/sessions` 100% full (29 MB free). Render stack pinned per `requirements-render.txt` into `/tmp/pyrender`. plotly 6.0.1, pandas 2.2.3 and weasyprint 70.0 import OK |

## Rule-1 search (file-name hits only; full table goes to `03` §0)
| Need | Hits | Disposition |
|---|---|---|
| Season card, career frame, `runs_created`, house percentiles | UC48/49/51 kernels | **Inherit** (UC51 kernel, pinned) |
| Release point, extension, arm angle | UC44/47–51 kernels | **Inherit**; arm angle only if UC50/51 expose it as a function |
| Pitch map by batter side | UC44/49–51 kernels | **Inherit** |
| xwOBA / expected stats | UC44/47–51 kernels | **Inherit**. This answers HP-04 with xwOBA − wOBA, so no new barrel-residual KPI is needed |
| Spin axis / bullet slider | UC50 kernel; `uc-pps-023` `03` | Check for a generalizable function → CF-style generalization, else new |
| Similarity / comps | UC44 kernel; `uc-pps-030`/`031` `03` | Check; likely **new** for LHP delivery comps |
| Quick-AB success rate | **0 hits** | **New, provisional** |

## Product types explored
| # | Form | The part of the story it owns | Bid |
|---|---|---|---|
| P1 | PDF recap report (≤10 pp, ≤9 sections) | Verdict, evidence, HP grades | **Build (hero)** |
| P2 | Interactive dashboard (≤8 chapters) + Artifact | Platoon, pitch-map and comps exploration | **Build**. It keeps the deliverable shape of UC48/49/51, so phase shares stay comparable |
| P3 | Persona card (UC24 style, one page) | A one-glance coaching card | **Not bid in Tier A** (priced in B) |
| P4 | 2027 projection / ML | Re-sign decision support | **Not bid**: no projection model in the house, and CI-3 is unverified |
| P5 | Video clips | Bullet slider and sinker visuals | **Not bid**: out of the comparison profile |

## Scope tiers (pick one)
The comparison-profile cap applies to every tier: report ≤10 pages / ≤9 sections · dashboard ≤8 chapters · ≤10 figures · ≤3 new KPIs.

**Tier A — Comparison profile (recommended).** Same shape as UC48/49/51, so the cost comparison is like-for-like.
- **Report, 9 sections:**
  1. Verdict
  2. Results card (wOBA, OPS, K%, BB%, HR%, runs on watch per game)
  3. Contact and sustainability (HH%, barrel%, EV/LA/distance, xwOBA − wOBA, whiff, chase)
  4. Platoon
  5. Stuff and delivery (arsenal, velocity, movement, release, extension, bullet slider)
  6. Weapons (SL vs RHB, SI vs LHB)
  7. Context (Mayza career; Phillies LHP relievers, results)
  8. Quick-AB success rate
  9. Comps and method appendix (HP grades)
- **Dashboard:** sections 1–8 as chapters.
- **10 figures:**
  - F1: wOBA/xwOBA by year
  - F2: HH% and barrel% by year
  - F3: barrel% vs wOBA, house LHP
  - F4: platoon pitch map
  - F5: arsenal movement and velocity
  - F6: release point and extension vs house LHP
  - F7: SL spin axis vs house LHP
  - F8: weapon matrix
  - F9: quick-AB rate vs house pitcher-seasons
  - F10: nearest Phillies LHP comps
- **3 new KPIs:**
  - K1: Quick-AB Success Rate, provisional, corrected definition plus the client's method as HP
  - K2: Bullet-slider flag (spin-axis band), provisional or a generalization of UC50
  - K3: LHP delivery-similarity distance (release x/z, extension, SI/SL velocity and movement), provisional

**Tier B — Tier A plus extras (≈ +85k, +6 min).** Persona card (P3) · arm-angle panel · an "Alvarado-lite" head-to-head comp (HP-14) · a postseason ledger page. Over the cap on pages (+1) and figures (+2), so it **breaks comparability**.

**Tier C — Lean (≈ −150k, −11 min).** PDF only, no dashboard. 6 figures (drops F3, F7, F8, F10). K1 only, with K2 and K3 deferred. Cheapest, but not comparable to UC48/49/51 on dashboard share.

**Deferred: priced, not built (any tier):** arm angle if not inheritable (~15k) · Alvarado-lite comp (~20k) · persona card (~35k) · postseason ledger page (~8k) · MLB-wide LHP context (not bid: the house population rule) · mound or rubber position (not in Statcast; not bid) · 2027 projection (not bid).

## Deliverables bid (Tier A)
| # | Deliverable | Notes |
|---|---|---|
| 1 | `dp_uc52_mayza_2026_recap_report.pdf` (+ `.md`) | ≤10 pp, 9 sections |
| 2 | `dp_uc52_mayza_2026_dashboard.html` (+ `_artifact.html`) + Artifact | ≤8 chapters; plotly via `phillies_dp.render.plotly_script_tag()` |
| 3 | `dp_uc52_kernel.py`, `_mayza_recap.py`, `_build_figs.py`, `_build_dashboard.py`, `_build_pdf.py`, `_hp.py`, `_verification.py` | MLB root |
| 4 | `out/dp_uc52_*`: CSVs, fig JSON+PNG, `headlines.json`, `dq_scorecard.csv`, `verification_log.csv`, `hp_grades.csv` | Every narrative number comes from `headlines.json` |
| 5 | Receipts `00`–`07`, README, this BID, contract, ledger patch | Control-plane folder + MLB root |

**Explicitly not bid:** ERA as computed (we use runs on watch) · medical inference (2025 IL) · MLB-wide ranks · postseason in any rate · mound-position claims.

## Price (Tier A)
**Basis:** recap actuals. UC48 Bowlan, the closest profile (reliever): 530k (430k in / 100k out, 42 min). UC49: 545k. UC51: 681k (580k in / 101k out, 46 min). Non-intake work in those runs was 292k–394k.
- **Up** for: 14 HP rows reproduced by the client's method, 3 new provisional KPIs (each with a `03` §2 spec and harness family), 10 figures at the cap, and the K1 definition fix.
- **Down** for: a small reliever sample (1,093 pitches), the house-format skill replacing prior-folder reads in T1/T6, and no staging (the build runs on the device).

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, recon, house format, carry-ins, env, id scan (**sunk at C2: 191.5k on the counter, gross**; +13.1k to file the BID; C3 = 204.6k) | ~197k | ~8k | 8 |
| T1 Kernel + build + receipts + HP reproduction (reconciling reported numbers) | 80k | 22k | 7 |
| T2 Figures (10) + brand + palette + render QA (dataviz skill load in) | 60k | 18k | 6 |
| T3 Dashboard (8 chapters) + headless QA + Artifact | 45k | 15k | 4 |
| T4 Report + PDF | 22k | 10k | 2 |
| T5 Verification harness (families A–G + K1–K3) | 35k | 14k | 3 |
| T6 Governance 00–07, README, contract, ledger, commits | 45k | 22k | 4 |
| D Defect discovery | 13k | 3k | 2 |
| Contingency 10% (on unsunk work) | 30k | 10k | 3 |
| **BID** | **~527k** | **~122k** | **~39 min** |

**Total ≈ 649k**, against 530k / 545k / 681k for the comparison set.
- **Time cross-check:** 0.10 min per 1k tokens × 0.7 (device build) × 649k ≈ 45 min; the T0 actual (8 min) runs under that rule, so the bid carries 39 min.
- **Token credits** at list ($10/M in, $50/M out) ≈ **$11.40**, band **$9.70–13.10** (±15%). Cowork bills subscription usage; read this as API-equivalent value.
- **De-scope options priced:** Tier C saves ~150k (≈ $3, 11 min). Tier B adds ~85k (≈ $1.60, 6 min).

### House calibration rules (carried; update from `07` §4)
- T0 is priced from the live counter at bid time (sunk work). This run separates the first-turn load (~129k) from repo work (~62.5k).
- Output: 0.8× scope-scaled for recaps built with a report builder.
- T1 input: ~80k when a reported number must be reconciled. That applies here: 14 HP rows.
- EDA: ~2k per subject, written to file through `phillies_dp.eda.to_file`.
- Fixed lines: render QA ~12k · skill loads ~15k · defect discovery ~13k.

## Pre-registered `05` catches (found at intake; `05` will tag each "intake could have caught: Y/N")
| # | Catch | Intake could have caught |
|---|---|---|
| SRC-1 | Client frames have no `game_type` filter (spring and postseason mixed into rates) | Y (caught) |
| SRC-2 | Root `pp26.csv` is stale (134 vs 1,093 Mayza pitches) | Y (caught; impact tested in T1) |
| DEF-1 | `tm_success_rate` reads the pre-pitch `strikes`, so the code measures "two strikes within two pitches" | Y (caught) |
| DEF-2 | The quick-AB figure's `add_hline` takes the first group's mean (`.unique()[0]`, the client's "# WHAT?") and draws it on both facets | Y (caught) |
| POP-1 | The barrel→wOBA context mixes `nphl` + `pps` + `pos` LHPs (Phillies opponents' LHPs included) and hard-codes `plate_apps > 73`, while the subtitle prints a computed `fltr` | Y (caught; restated in the house population) |

## Assumptions, exclusions, carry-ins
- Regular season for every rate; the postseason (6 pitches) gets its own ledger line with denominators.
- Entity lock by MLBAM id 641835, never by name.
- Population claims are tested in the client's own population (HP), then restated in the house population (Phillies LHP pitcher-seasons, with rank and n). The reliever definition and min-PA floor are fixed in `03` before figures.
- Carry-ins CI-1 to CI-5 are labelled at every use and never computed on.
- `07` adds the audit fields "house-format read (tokens)" and "prior-UC files opened (count)", and `05` tags every catch "intake could have caught: Y/N".

**Awaiting the DPO's scope pick: A (recommended) / B / C, plus any deferred items to un-defer.**
