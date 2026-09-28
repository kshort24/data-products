# BID — Jesús Luzardo 2026 Recap: "The Chase"

**Status:** **AWARDED 2026-09-27** (RFP exercise: bid filed, then treated as the winner per Kellen's instruction; actuals are reconciled in `07_platform_marketing.md` §3)
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-09-27 (20:31 ET)
**ID reservation:** UC **#49** · contract `uc-pps-034` · build artifact `dp_uc49` · folder `uc-pps-034-luzardo-2026-recap-001`
**Collision check (bid time):** `dp_uc49*`: none at the MLB root, none in `out/`, none in the control plane. `uc-pps-034*`: referenced only as "next" in the `uc-pps-033` ledger patch. Ground truth for numbering is that patch (**next #49**); `uc_ledger_AI.md` still reads "next #25" (known drift, E-6 carried).

---

## The ask (as submitted)

Two notebook cells in `September 2026.ipynb`, both written by Kellen:

1. **Cell 118, the recap code.** A career-by-season KPI table (14 KPIs: slash line, wOBA, K/BB/HR rate, whiff, chase, in-zone, first-pitch strike), a 2026 drill, and three scatters over *Phillies pitcher-seasons, min 150 pitches*: **whiff × chase** (with the "plus chase / plus whiff" quadrant shaded), the same faceted by handedness, and **walk rate × in-zone rate** with an OLS trendline. It ends on a 2026 pitch-location map by batter side and an unfinished `edge_rate` function. Two inline claims: *"Luzardo does not need to be in the strike zone, he gets chase and whiff"* and *"He does this better than most pitchers in my dataset."*
2. **Cell 51, the narrative.** Labor Day complete-game shutout, 1–0 over Atlanta, "the best shift of his Major League career"; first All-Star selection, in the park he will call home for five more seasons; an extension that "could look to be one of the best acquisitions" of the Dombrowski era. The cell closes on the thesis: *"2023 is the season to rue. 2026 could be the season to celebrate, forever … For Jesús Luzardo, it could be."*

Instructions that came with it: (a) **the narrative drives the use case**; (b) **explore different types of data products** that could tell this story; (c) storytelling, not business, but grounded in data; (d) visuals well-labelled, curated and governed; (e) receipts `00`–`07` in the control plane; (f) scouting-report inspiration and data-plane coding standards; (g) this bid.

## Why this shop wins this RFP

1. **We already hold two Luzardo receipts, and we inherit them instead of re-deriving.** `uc-pps-017` (first half, All-Star assessment: sweeper-first redesign, 2nd-time-through cliff at .368) and `uc-pps-028` (consistency audit: best staff xwOBA since May, 90–110 pitch band, the cliff closed to .279). A competitor starts cold. We start with the first two acts of the story already certified and add the third: August, Labor Day, and the silence after it.
2. **We know the premise has moved, and we checked before bidding.** The cell says the regular season is "done" for him. The log agrees for a different reason: his last pitch was **2026-09-07**, the Labor Day shutout. Reporting since then: scratched from the 9/12 start with shoulder stiffness, **15-day IL on 9/15 (shoulder inflammation)**, a 30-pitch bullpen on 9/25, and activation for Game 162 **out of the bullpen** (Phillies Nation 2026-09-24; SI 2026-09-27). That turns "a defining postseason" from a flourish into the product's central, open question. We carry those facts in, label them, and never compute on them.
3. **"Defining" gets pre-registered, not narrated.** We will publish, *before* October, what a defining postseason would look like in this pitcher's own data: velocity back to his season band, the sweeper still winning the chase, the second time through holding. Each line gets a threshold drawn from his 2026 log. The postseason then grades the card (v1.1.0). No competitor that writes a season-in-review can be proven wrong. We can, and that is why the story is worth reading.
4. **We found the source trap before the build.** `uc-pps-033` profiled `nphl` with a byte search ("Bowlan appears only in bowlan.parquet"). An id-column scan for Luzardo finds his pitches in **21** opponent files, not the 2 a byte search finds, because batter-keyed pulls carry the batter's name in `player_name` and compressed parquet hides strings. The client's name filter happens to be safe (it only matches the pitcher-keyed file). A governed frame keyed by id is not safe unless it deduplicates across all 21. We price the fix (CF-2) and a back-check of `uc-pps-033`.
5. **The device can run the build where the data lives.** `uc-pps-033`'s top cost hotspot was staging 60 MB because the laptop VM had no `pyarrow`. At bid time we installed `pyarrow`, `scipy` and `plotly` into `/tmp` on the device (outside the full `/sessions` volume). The data build and the harness run on the laptop; only the render step (Chromium for PNG, pango for PDF) runs in the cloud, on receipts.

## Data position (verified at bid time, not assumed)

| Check | Result |
|---|---|
| Phillies logs | `phils_2015…2026.parquet`, 555,760 rows, current through **2026-09-26** (Game 161) |
| Luzardo, entity lock | MLBAM **666200**, LHP. 2026: **2,860** regular-season pitches in **29** games, last **2026-09-07** (109 pitches, 9 innings, PHI vs ATL). 165 spring rows excluded |
| 2025 (first Phillies season) | 3,013 regular-season pitches, 32 games; plus **112 NLDS pitches in 2 games** (postseason ledger) |
| Pre-Phillies | `data/opponents/luzardo.parquet`: 2019–2024 (OAK/MIA), 8,553 regular-season pitches; 195 Wild Card + 73 Division Series pitches (2020 OAK, 2023 MIA **at Citizens Bank Park**) |
| `nphl` exposure by id | 21 files hold Luzardo pitches (id scan); by name, only `luzardo.parquet`. Cross-source dedup is required |
| Carry-ins | Trade from MIA, Dec 2024 (MLB.com); 5-yr/$135M extension covering 2027–31, 3/10/2026 (MLB.com); first All-Star selection, named 7/7, ASG at Citizens Bank Park 7/14 (MLB.com); NL Pitcher of the Month, August (MLB.com); Labor Day box (2 H, 1 BB, 12 K, 1:51, Schwarber HR in the 8th; MLB.com); shoulder IL (above) |

## Product types explored (the "explore different types" half of the ask)

The organization will **scope eight product forms against the narrative** and build the five that the data can carry today. Each is judged on one question: *what part of the story can only this form tell?*

| # | Form | The part of the story it owns | Bid |
|---|---|---|---|
| P1 | **Narrative dashboard** (chapters, offline HTML) | The season as an arc you can walk: arrival → the bet → the chase → the summer → Labor Day → the silence → October | **Build (hero)** |
| P2 | **Game story**: Labor Day, pitch by pitch | 109 pitches as a sequence; the "two game plans" reporters described, tested by time through the order | **Build** (inside P1 + one figure) |
| P3 | **October card**: pre-registered | What "defining" would look like, with thresholds, graded after the fact | **Build** |
| P4 | **Feature report** (PDF) | The long read: the chase thesis, the context scatters, the caveats | **Build** |
| P5 | **Context board**: the client's three scatters, governed | "Better than most pitchers in my dataset", with the dataset named and the rank printed | **Build** (figures + dashboard) |
| P6 | **Shareable notecards** (single-image) | One number, one picture, for a thread or a broadcast graphic | Build 1 (the Labor Day card) |
| P7 | **Postseason ledger** (career October, pitch-level) | The 2023 Wild Card at the Bank, the 2025 NLDS | Build as a chapter (tiny samples, printed) |
| P8 | **Dombrowski acquisitions board** | "One of the best acquisitions" | **Not bid.** No transaction table exists in either repo; "acquired by" cannot be keyed. Offered as the next UC with a roster source |

## Deliverables bid

| # | Deliverable | Notes |
|---|---|---|
| 1 | **Narrative dashboard** `dp_uc49_luzardo_2026_dashboard.html` | Self-contained, offline. Seven chapters; Labor Day replay (pitch-by-pitch table + by-inning mix); context board with drill-through; October card. Brand light by default, *Notebook dark* toggle (E-5 carried) |
| 2 | Governed kernel `dp_uc49_kernel.py` | Imports `dp_uc48_kernel` (sha256-pinned), which imports `dp_uc44_kernel`. **CF-2** generalizes CF-1 (subject id + file as parameters, id scan over `nphl`); SR-1 **second use** (ratification) |
| 3 | Feature report `.md` + `.pdf` | Bottom line first, data-window box, candid caveats |
| 4 | October card | Pre-registered signatures + thresholds + the rule that grades them (`out/dp_uc49_october_card.csv`) |
| 5 | Human-parent reconciliation | The cell's KPI table reproduced by his method, then governed; each claim and chart subtitle graded |
| 6 | Figures (≈8) | Each asserts its subtitle before it is written; brand compliance checked in-process |
| 7 | Verification harness | Independent recompute families, including every number the report and dashboard narrative assert |
| 8 | Receipts `00`–`07`, README, this BID, contract, ledger patch | This folder + MLB root |

**Explicitly not bid:** ERA and innings as computed numbers (earned runs are not in Statcast; the published 2.87 ERA is a carry-in); any medical inference about the shoulder (the log can show velocity and workload, not a diagnosis); P8; MLB-wide percentiles (house frame only, as in `uc-pps-032` C1); a 2027 projection.

## Price

**Basis:** `uc-pps-033` actuals (~430k in, ~100k out, 42 min), adjusted by its calibration findings C-1 to C-5.
**Up** for eight career seasons across 22 source files instead of four across two; carry-in research (7 sources); device environment repair; a product-type exploration; a pitch-by-pitch game story; a pre-registered October card.
**Down** for inheriting two prior Luzardo receipts and SR-1 instead of building a recap engine; no persona ledger.
Per C-1, a **house-format + skills** line is priced (no template card exists yet). Per C-3, **two build iterations** are priced. Per C-4, the **defect-discovery** line is kept. Per C-2, output is priced at 0.9× scope-scaled actual. Contingency **0%** (bridge and device proven at bid time).

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, two-repo recon, house format + skill, carry-in research, device env repair, source profile (**sunk at bid time: ~245k**) | 245k | 6k | 8 |
| T1 Kernel (CF-2) + build + receipts, two iterations | 90k | 22k | 9 |
| T2 Figures (≈8) + brand compliance (cloud render) | 55k | 12k | 6 |
| T3 Narrative dashboard (7 chapters, game replay, context drill-through, October card) | 50k | 22k | 8 |
| T4 Feature report + PDF | 30k | 10k | 4 |
| T5 Verification harness | 35k | 10k | 4 |
| T6 Governance 00–07, README, contract, ledger patch, commits | 45k | 20k | 10 |
| D Defect discovery (C-4) | 10k | 3k | 2 |
| Contingency 0% | 0 | 0 | 0 |
| **BID** | **~560k** | **~105k** | **~51 min wall clock** |

Time cross-check (C-5 rule, 0.10 min per 1k tokens × 0.8 warm-sandbox multiplier): 665k → 53 min. Consistent with the phase build-up.

**Token credits** at list rates ($10/M in, $50/M out): 560k × $10/M + 105k × $50/M ≈ **$10.85**, band **$9.00–13.00**.
Cowork bills subscription usage, so read this as API-equivalent credit value. It is **+17%** on the `uc-pps-033` actual ($9.30) for twice the career, twice the sources and three product forms that did not exist in that UC.

**De-scope options priced:**
- Drop the dashboard (report + figures only) → −22k out, −8 min, about −$1.60. *Not recommended.* The game replay and the October card are interactive by nature.
- Report-only tier (no 00–07, no harness) → about **$5.25**.
- The client's cell only (recap + three scatters, governed and reconciled) → about **$3.00**.

## Assumptions, exclusions, carry-ins

- **Regular season for every rate.** Postseason pitches (2020 F, 2023 F, 2025 D) live only in the postseason ledger, printed with their denominators. The client's frame keeps them (it excludes only `S`/`E`); the reconciliation shows the difference.
- **Entity lock by MLBAM id (666200), never by name.** The accented name filter is reproduced once, in the reconciliation.
- **"Better than most pitchers in my dataset"** is tested in the client's own population (Phillies pitcher-seasons, 2015–2026, ≥150 pitches) and restated with the rank and population size. It is never extended to MLB.
- **The shoulder.** The log can show velocity by start and workload; it cannot show an injury. The product states what the log shows before 9/7 and nothing more.
- **Carry-ins** (see Data position) are labelled at every use and never computed on.

---

> **STATUS UPDATE 2026-09-27: AWARDED.** Proceeding per Kellen's instruction to treat the bid as won.
> Actuals vs. bid are in `07_platform_marketing.md` §3. The delivery spine is `00_dpo_orchestration_record.md`.
