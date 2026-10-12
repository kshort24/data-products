# BID — Zack Wheeler 2026 Recap: "Still Zack Wheeler"

**Status:** **AWARDED 2026-10-12** (RFP exercise: bid filed, then treated as the winner per Kellen's instruction; actuals are reconciled in `07_platform_marketing.md` §3)
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-10-12 (13:05 ET)
**ID reservation:** UC **#51** · contract `uc-pps-035` · build artifact `dp_uc51` · folder `uc-pps-035-wheeler-2026-recap-001`
**Collision check (bid time):** `dp_uc51*`: none at the MLB root, none in `out/`, none in the control plane. `uc-pps-035*`: referenced only as "next" in the `uc-pps-034` and `uc-pos-018` ledger patches. Ground truth for numbering is the `uc-pos-018` patch (**next #51**, pps next `uc-pps-035`). `uc_ledger_AI.md` still reads "next #25" (E-6, carried).

---

## The ask (as submitted)

`October 2026.ipynb` cells 16 and 21–23, written by Kellen, handed over with the instruction *"Recap his 2026 season … consider previous work done this season … but this recap should stand alone."*

1. **The thesis (cell 16):** *"45 — One more year left on his deal, he started to show some signs of slowing down in the second half but for now he is still Zack Wheeler."*
2. **The KPI list (cell 21):** tied-up rate (the cell's "jam rate", renamed by the client after checking Baseball Savant's swing-timing definition: tied-up / centered / flail, centered = barrel within ±4 in), pitch map, pitch plot, top-level results (wOBA, OPS, K%, BB%), contact quality (HH%, barrel, LD%), edge rate (*"per Statcast Wheels was edging us 42.4% of the time"*), xwOBA *".263, very good!"*
3. **The code (cell 21):** a career KPI table over `pps[player_name == 'Wheeler, Zack']`, a 2026 pitch map by batter side, a movement plot, a platoon table (+ whiff, chase, `inds`) and a wOBA-by-season scatter colored by batter side.
4. **Three inline claims:** (a) *highest walk rate of his Phillies tenure (7.6%), the theme of his August struggles, "he lost his previously elite command"*; (b) *"most of the other results appear to just be noise"* (fewer barrels, no surge in LD or hard hit); (c) *"pretty strong platoon splits: elite against righties, lefties did more damage."* Two leads to chase: **edge rate and zone expansion.**
5. **Cell 23 (jam-rate development):** the threshold (`intercept_ball_minus_batter_pos_x_inches < 32.5`), a population scatter (player-seasons 2025–26, ≥50 swings), and *"57 balls in play on Zack Wheeler's sinker jamming righties in 2026."* The governed version of that function landed in `Baseball Functions.ipynb` on 10/9 (`jam_rate`, JR-1).

Instructions that came with it: governed, documented package with receipts `00`–`07` in a subfolder of `data-products`; scouting-report skill and prior MLB outputs for inspiration; data-plane coding standards; a **PDF report**; an **interactive dashboard if it makes sense**; other forms welcome; this bid.

## Why this shop wins this RFP

1. **We already hold the first half, certified.** `uc-pps-020` (UC #24, "The All-Star Who Wasn't") published 15 starts, 92.0 IP, a .246 wOBA, a 30.4 K% and a career-low 42.6% in-zone rate through 7/12. We reproduce those four numbers before we write a word of the second half, then add what nobody has yet: the second half, the stretch, the Wild Card relief outing and 2027. A competitor starts cold.
2. **We know the premise moved, and we checked before bidding.** The season is over. The log shows Wheeler started **Game 162 on 9/27** and then pitched **four innings in relief in Wild Card Game 3 on 10/1** (68 pitches, Braves 6–2, elimination). Reporting (Inquirer, 9/19/2026) attributes a six-start post-break slide (8.51 ERA) to a **mechanical flaw: dropping the glove and over-rotating**. That is a claim the log can test without a single medical inference (release point, arm angle, miss direction by start). We carry it in, label it, and test what the data can see.
3. **We found the source trap before the build.** An id scan for Wheeler (MLBAM 554430) finds his pitches in **24** opponent files. One is `lhvp26.parquet`: **148 Lehigh Valley rehab pitches** (3/28, 4/3, 4/8) tagged `game_type == 'R'` with `player_name == 'Wheeler, Zack'`. The client's cell-22 frame (`zw = nphl ∪ pps`, used for the jam-rate work) therefore carries AAA swings into "2026". Our own certified loader **CF-2 has the same exposure** (it admits every opponent file by id), so we price the fix (CF-2b, MLB-only) and a back-check of `uc-pps-034`.
4. **Rule-1 finds most of the KPI list already built.** Tied-up rate → `jam_rate` (JR-1, `Baseball Functions`, 10/9). Edge rate → `edge_rate` (UC8, `dp_uc8_nola_vs_nationals.py`). xwOBA → `xwoba_pa` (XW-1, `dp_uc50_kernel`). Hard-hit, barrel, LD → house functions. Recap table → SR-1 (ratified on its second use). October card → OC-1 (subject-agnostic). We **inherit by import or by source-pinned extraction** and spend the budget on what is new.
5. **The device runs the build where the data lives** (proven in UC49/UC50). Data build and harness on the laptop; only the render (Chromium, pango) in the cloud, on receipts.

## Data position (verified at bid time, not assumed)

| Check | Result |
|---|---|
| Phillies logs | `phils_2015…2026.parquet`; 2026 regular season through **2026-09-27** (Game 162); Wild Card rows 9/29–10/1 present |
| Wheeler, entity lock | MLBAM **554430**, RHP. 2026: **2,649** regular-season pitches in **28** games, first **2026-04-25**, last **2026-09-27**; **68 Wild Card pitches** (10/1, relief, innings 3–6) |
| Phillies tenure | 2020–2026 in `phils_*` (pitching role); 2022–2024 postseason rows present |
| Pre-Phillies | `wheeler.parquet` (pitcher-keyed): 2017–2019 Mets only (2013–14 not cached); 2017–19 also in `phils_*` batting role |
| `nphl` exposure by id | 24 files; **`lhvp26` (AAA rehab, 148 pitches)** and `atlo26` (179) are the 2026 exposures |
| Carry-ins | 2025 season ended 8/15/2025 (blood clot; venous thoracic outlet syndrome; rib-resection surgery 9/23/2025) · 3-yr/$126M extension (March 2024), one year left (2027) · 2026 line 14–5, 3.00 ERA, 28 GS, 162.0 IP, 193 K, 47 BB · post-break 8.51 ERA over six starts, reported mechanical cause · WC G3 4 IP / 2 R in relief |

## Product types explored

| # | Form | The part of the story only it can tell | Bid |
|---|---|---|---|
| P1 | **Feature report** (PDF) | The long read: still Wheeler, the stretch, the caveats | **Build** |
| P2 | **Narrative dashboard** (offline HTML + Artifact) | The season as chapters you can walk, with a start-by-start drill | **Build (hero)** |
| P3 | **The stretch forensics** | The six-start slide: command, edge, release point, glove-drop test | **Build** (chapter + figure) |
| P4 | **Swing-timing board** | Tied-up / centered / flail, with the population named; the sinker in on righties | **Build** |
| P5 | **"Still Wheeler" card for 2027** (pre-registered) | What "still Zack Wheeler" means in his own 2026 numbers, written before a 2027 pitch; grades the WC outing post hoc | **Build** (OC-1 second use) |
| P6 | **Notecard** | One picture, one line | Build 1 |
| P7 | **Postseason ledger** | WC G3 relief beside his 2022–24 Octobers | Build as a chapter |
| P8 | **Contract-value board** | "One more year left on his deal" priced against production | **Not bid.** No salary or WAR source in either repo; carry-in only |

## Deliverables bid

| # | Deliverable | Notes |
|---|---|---|
| 1 | Feature report `dp_uc51_wheeler_2026_recap_report.md` + `.pdf` | Bottom line first, data-window box, candid caveats; house voice |
| 2 | Narrative dashboard `dp_uc51_wheeler_2026_dashboard.html` | Self-contained, offline, light/dark, phone width; Artifact copy |
| 3 | Governed kernel `dp_uc51_kernel.py` | Imports `dp_uc49_kernel` and `dp_uc50_kernel` (sha256-pinned); extracts UC8 `edge_rate` and `Baseball Functions` `jam_rate` by source pin; CF-2b |
| 4 | Build `dp_uc51_wheeler_recap.py` + receipts `out/dp_uc51_*` | Every table a CSV; `headlines.json`; DQ scorecard |
| 5 | Figures (≈10) + notecard | Each asserts its subtitle before shipping; brand + palette checks |
| 6 | Verification harness `dp_uc51_verification.py` | Independent recompute of every published number |
| 7 | Client reconciliation (HP family) | Every claim and chart choice in cells 16/21–23 graded beside the governed value |
| 8 | Receipts `00`–`07`, README, this BID, contract, ledger patch | This folder + MLB root |

**Explicitly not bid:** ERA and IP as computed numbers (carry-ins only; the log gives "runs on watch" and OU-1 outs); any medical inference about the 2025 surgery or 2026 velocity; MLB-wide percentiles (house frame only); a 2027 projection (the card registers bars; it predicts nothing); P8.

## Price

**Basis:** `uc-pps-034` actuals (~425k in / ~120k out / 45 min, narrative multi-form) and `uc-pos-018` calibration C-1…C-7.
**Up** for a new KPI family on bat-tracking columns (swing timing), a mechanics test (release/arm angle), two extraction-inherited functions, a source fix with a back-check, and ten figures.
**Down** for inheriting SR-1, CF-2, OC-1, XW-1, JR-1, ER-1 and the chapter template; one in-season parent receipt (uc-pps-020) to reproduce; four carry-in fetches instead of seven; no pitch-by-pitch stepper.
C-1: T0 from the live counter. C-2: output at 1.0× (long-form narrative). C-3: T1 at ~55k in (device build, EDA to file). C-4: defect line kept. C-5: time rule 0.8 (no deadline). C-6: render-QA line kept. Contingency **0%** (bridge, device and imports proven at bid time).

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, two-repo recon, house format, notebook, Rule-1, carry-ins, id scan (**sunk at bid time: ~300k**) | 300k | 7k | 6 |
| T1 Kernel (CF-2b, extractions) + build + receipts + EDA to file, two iterations | 55k | 26k | 10 |
| T2 Figures (≈10) + notecard + brand/palette + render QA | 45k | 14k | 7 |
| T3 Narrative dashboard (7 chapters, start drill, card) + render QA + Artifact | 50k | 24k | 8 |
| T4 Feature report + PDF | 15k | 11k | 4 |
| T5 Verification harness | 25k | 11k | 4 |
| T6 Governance 00–07, README, contract, ledger patch, commits | 60k | 32k | 12 |
| D Defect discovery (C-4) | 10k | 3k | 2 |
| Contingency 0% | 0 | 0 | 0 |
| **BID** | **~560k** | **~128k** | **~53 min wall clock** |

Time cross-check (C-5, 0.10 min per 1k tokens × 0.8): 688k → 55 min. Consistent with the phase build-up.

**Token credits** at list rates ($10/M in, $50/M out): 560k × $10/M + 128k × $50/M ≈ **$12.00**, band **$10.00–14.00**.
Read this as API-equivalent credit value (Cowork bills subscription usage). It is **+17%** on the `uc-pps-034` actual ($10.25) for a new KPI family, a mechanics test and a loader fix, against fewer carry-ins and no game stepper.

**De-scope options priced:**
- Drop the dashboard (report + figures only) → −24k out, −8 min, about −$1.70. *Not recommended:* the start drill and the swing-timing board are interactive by nature.
- Report-only tier (no 00–07, no harness) → about **$5.75**.
- The client's cells only (KPI table, pitch map, pitch plot, platoon table, governed and reconciled) → about **$3.25**.

## Assumptions, exclusions, carry-ins

- **Regular season for every rate.** The Wild Card outing and 2022–24 Octobers live in the postseason ledger, printed with denominators. The client's `pps` frame keeps postseason rows (it excludes only `S`/`E`); the reconciliation shows the difference.
- **Entity lock by MLBAM id (554430)**, MLB games only. The name filter is reproduced once, in the reconciliation.
- **Tied-up rate is a public-data proxy** for Savant's swing-timing bucket (house JR-1). Savant's own value is not in the data; where the client quotes a Savant number (edge 42.4%, xwOBA .263) we reconcile to it and say which definition differs.
- **The mechanical claim** is a carry-in from reporting. The log can show release point, arm angle and where misses went; it cannot show a glove.
- **Carry-ins** are labelled at every use and never computed on.

---

> **STATUS UPDATE 2026-10-12: AWARDED.** Proceeding per Kellen's instruction to treat the bid as won.
> Actuals vs. bid are in `07_platform_marketing.md` §3. The delivery spine is `00_dpo_orchestration_record.md`.
