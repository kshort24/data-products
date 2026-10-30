# BID: Kyle Schwarber 2026 season recap, "Forty-Five and a Question Mark" (full product)

**Status:** FILED 2026-10-29 20:14 ET · **AWARDED by RFP rule (treat as winner)** · **DELIVERED ≈20:34 ET, READY-CONDITIONAL (C1–C6), harness 28/28.** Actuals: ≈240k / ≈28 min vs ≈478k / 54 min (`07` §5).
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments) · **Human DPO:** Kellen Short
**ID reservation:** UC **#60** · contract `uc-pos-024` · build `dp_uc60` · folder `uc-pos-024-schwarber-2026-recap-001`
**Collision check:** `dp_uc59` is taken by the catcher-corps recap (`uc-cat-002`, delivered 10-29). Its ledger patch reserves "next: UC #60 / dp_uc60 · pos `uc-pos-024`". No `dp_uc60*` exists in either plane. The repo ledger still reads UC52; UC52–UC59 patches are pending paste.

## The ask
1. **The parent recap UC58 deferred.** UC58's intake parked these questions for this product: "What happened to this man? Should we be concerned? Perhaps... It was his back? Did he lose his pop?"
2. **Deliverables.** A full governed package; a **PDF report** (required); an **interactive dashboard** ("if it makes sense"); other outputs at the org's discretion.
3. **Tier 3 of the Pitcher Recap Visual Redesign brief, "considered".**
   - **Our reading:** the brief's seven visual standards (V1–V7) are the acceptance criteria for every figure in this recap. Its **shared dependencies** (comparison sets, era definitions, helpers) are built once, here, as house assets the pitcher redesign will reuse.
   - **Not in this UC:** the 13 pitcher redesign items, which modify uc-pps-033…037. Bid separately as Tier B. The brief's own governance says each redesign traces to the UC it modifies, and this UC modifies none of them.
4. **Standing instructions.** Work in the MLB repo; receipts `00`–`07` here; scouting-report-skill inspiration; a competitive token/time bid, treated as won.

### Client questions → report chapters
| Q | Ask | Ch. | Primary figure (all pass V1–V7) |
|---|---|---|---|
| Q1 | "What happened to this man?" | §2 | F1 season dots (wOBA, sized by PA) over the Phillies hitter-season box per year · F2 cumulative wOBA by PA, 2022–26 (V1 exception) |
| Q2 | Where and when did it turn? | §3 | F3 2026 by month, wOBA and xwOBA dots sized by PA, with era aggregates (H1 / H2) and the back date marked |
| Q3 | "It was his back?" | §4 | F4 bat-speed distribution by month (IQR-shaded boxes) against his 2025 band; absence ledger |
| Q4 | "Did he lose his pop?" | §5 | F5 exit-velocity boxes by season, 95 mph line, hard-hit % labels · F6 damage-band (20–32°) share against the pool |
| Q5 | "Should we be concerned?" | §6 | F7 K% vs chase, Phillies hitter seasons, trendline with R² and n, his seasons highlighted · F8 xwOBA by hand × pitch group, 2025 → 2026 dumbbells (V5 replacement for bars) |
| — | Recap close | §7–8 | Three things for 2027; client notes graded; caveats |

### Client claims graded (HP rows)
| HP | Claim | Source |
|---|---|---|
| HP-01 | "Should we be concerned?" (decline is real, not noise) | UC58 intake |
| HP-02 | "It was his back?" | UC58 intake |
| HP-03 | "Did he lose his pop?" | UC58 intake |
| HP-04 | 1st half .254/.367/.560 → 2nd half .199/.336/.416 | CI-2 report card |
| HP-05 | K% 31.4%, his highest since 2017; 220 strikeouts | CI-2 |
| HP-06 | Chase 26.1%, up from 21.5%, highest since 2020 | CI-2 (Savant definition; graded on the house definition with the gap disclosed) |
| HP-07 | September: .172 AVG, .710 OPS | CI-2/CI-7 |
| HP-08 | 32 HR through the break, 13 after | CI-7 |

## Why this shop wins
### 1. Inherit, don't re-derive
- **K57** (pos recap spine; slash/wOBA/xwOBA, cell panel, `hitter_seasons`, `house_percentile`, `two_prop_z`, `bat_tracking`, `breakpoint_scan`).
- **K58** (UC58: career loader 2015–26, DH-1 game order, WP-1, HR quality HB-1, SP-1 spray, PA-X1).
- **`cumulative_metric`**.
- **UC33's** sensor-boundary NULL standard (bat tracking 2024+, swing path 2025+) and damage band SW-8.
- **K47** tiered pitcher-name resolver.
- **20 pins re-asserted at bid time: PASS.** UC58's HR-quality grades (HP-01–05 there) are cited, not recomputed.

### 2. We checked the premise before bidding (carry-ins sourced, never computed on)
- **CI-1** 45 HR, tied for the MLB lead (MLB.com).
- **CI-2** .232/.354/.503, 130 wRC+, 2.9 fWAR; halves .254/.367/.560 → .199/.336/.416; K% 31.4%; chase 26.1%; "mysterious back injury" with no onset date (Yahoo/SB Nation).
- **CI-5** Back: late scratch Tue 6/23 at WSH, "lower back tightness … while he was trying to swing". Missed that game only; pinch-hit 6/24 (10-pitch walk); started again 6/25. No IL (MLB.com; NBC Sports Philadelphia).
- **CI-6** Illness absences: 5/18–5/20 stomach issue (ended a 225-game streak); 7/28–7/29 gastrointestinal issue in Miami (MLB.com; 6abc/AP).
- **CI-7** Through the break 32 HR; after it 13; September .172 / .710 OPS; age 33; five-year, $150M deal signed last winter (Roundtable).
- **Log reconciles at bid time:**
  - 156 G of 162; the 6 missed dates match CI-5/CI-6 exactly (5/18, 5/19, 5/20, 6/23, 7/28, 7/29).
  - 702 PA.
  - First half 415 PA, second half 287.

### 3. Pre-registered (20:14 ET, before any grade is computed)
- **ER-1 eras (shared registry):**
  - **2026 All-Star break window = 7/13–7/15** (no MLB games; ASG 7/14 at CBP). H1 = through 7/12, H2 = from 7/16.
  - Three different ASB constants ship in the repo (`"2026-07-13"`, `"2026-07-14"`, `"2026-07-16"`). They are equivalent only because no games fall in the window. The registry asserts that.
  - **BK date = 2026-06-23** (CI-5).
- **CS-1 comparison set:** Phillies hitter seasons, regular season, ≥ 200 PA, 2015–26 (house log; **n = 122**), via K57 `hitter_seasons`. The per-year context box uses that year's members.
- **BK-1 back test (HP-02), set in advance:**
  - **Pre** = 3/26–6/22; **post** = 6/25–9/27.
  - Process metrics: bat speed (mean, p90), swing length, EV p90 on BIP, hard-hit %, barrel %, chase, whiff, xwOBAcon.
  - **"CONSISTENT WITH A PHYSICAL CHANGE"** if bat speed mean or p90 falls ≥ 1.0 mph, **or** EV p90 falls ≥ 1.5 mph, post vs pre, **and** the date breakpoint scan's best split for xwOBA lands within 15 team games of 6/23.
  - **"NOT VISIBLE IN THE LOG"** if no physical leg moves.
  - **"PARTLY"** otherwise.
  - The grade never says "caused".
- **POP-1 (HP-03):** "lost pop" = 2026 vs his 2022–25 Phillies range on EV p90 (BIP), barrel % (BIP), ISO and HR/PA. **SUPPORTED** if ≥ 3 of 4 sit at or below his tenure low; **PARTLY** if 1–2; **NOT SUPPORTED** if 0. UC58's HR-quality grades are cited alongside.
- **CN-1 concern (HP-01):** process vs results. **SUPPORTED** if 2026 xwOBA sits below his 2022–25 low **and** below the CS-1 median of ≥ 600-PA seasons, or if K% and chase both pass the change test (`two_prop_z`, |z| ≥ 1.96 vs 2022–25 pooled). **PARTLY** if one leg; **NOT SUPPORTED** if none.
- **Repro rows (HP-04…08)** are reproduced on the house log. A mismatch > 1 point (.001) is reported as a definition gap, not a failure.

### 4. Traps found before the build
- **ER-0:** three ASB constants (above).
- **PA-702 vs 701:** UC58's PA-X1 counts 701 (one `truncated_pa`); the K57 `nresults` path counts 702. This recap uses the K57 spine and states 702, matching FanGraphs (CI-2 needs reconfirming at build).
- **OPS .853 vs .857:** CI-2 prints .853, CI-7 .857; .232/.354/.503 sums to .857. The log settles it.
- **Sensor boundary (OI-1, UC33):** no bat speed before 2024; no swing path before 2025. F4 starts in 2024 and says "not measured" before that.
- **V1 discrete-dots rule vs monthly data:** monthly points are dots sized by PA, never joined. A dotted LOWESS-free linear trend only (sketched, R² printed).
- **Absences:** two stomach/GI absences (5 games) bracket the back scratch. BK-1 excludes only the 6/23–6/24 window and reports the illness dates beside it, so illness isn't silently attributed to the back.

## Product types
| # | Form | Bid |
|---|---|---|
| P1 | PDF recap (≤ 9 pp, 8 sections, 8 figures) | **Build (hero)** |
| P2 | Interactive dashboard (7 chapters, hover on every chart) | **Build** (it makes sense: monthly and box views reward hover) |
| P3 | Shared Tier 3 dependencies: `phillies_dp/recap_viz.py` (trendline + R², IQR box, discrete-dot series) + `data/_schema/comparison_sets.json` + `data/_schema/eras.json` | **Build** (house asset, self-tested) |
| P4 | Season card (one-page PNG) | **Build** (2027 planning handout) |
| P5 | Pitcher redesign items 1–13 on uc-pps-033…037 | **Tier B** |

## Tiers
- **Tier A (AWARDED):** P1–P4, receipts `00`–`07`. New KPIs: none (BK-1, POP-1, CN-1 are grade rules). New house assets: SD-1 comparison sets, SD-2 eras, SD-3 helpers.
- **Tier B:** + pitcher redesign items 1, 2, 3 and 4 (Alvarado, Wheeler; the brief's first wave) as a v1.1 of each pps UC. ≈ +260k, +30 min.
- **Tier C:** PDF only, no dashboard or card. ≈ −120k, −12 min.

## Price (Tier A)
**Basis:** pos recaps UC54–UC57 actual 466k–576k (UC57 ≈513k); UC58 ≈310k.
- **Down:** UC58 already built the HR layer and the career loader; spine inherited.
- **Up:** the shared Tier 3 assets; a 7-standard visual audit on 8 figures; the absence/back reconciliation.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 recon, profile, 9 carry-in reads, BID, `00`, `01` (**≈62k sunk**) | 70k | 20k | 9 |
| T1 kernel + shared assets (SD-1/2/3 + self-test) + build + HP grades | 75k | 26k | 10 |
| T2 figures (8) + V1–V7 audit + render QA + season card | 70k | 22k | 10 |
| T3 narrative + report + PDF | 30k | 16k | 6 |
| T4 dashboard (7 chapters) + QA | 35k | 14k | 6 |
| T5 harness | 25k | 9k | 4 |
| T6 governance `02`–`07`, README, contract, ledger patch | 25k | 18k | 6 |
| Contingency 5% | 17k | 6k | 3 |
| **BID** | **~347k** | **~131k** | **~54 min** |

**Total ≈ 478k tokens, ≈ 54 minutes.** House list convention ($10/M in, $50/M out): ≈ **$10.0**, band $8.5–11.5.

**Competitive position.** A rival org would rebuild the hitter pool, the PA and DH conventions, the sensor boundary and a back-injury timeline from scratch. It would likely plot monthly lines, the exact pattern Tier 3 bans. Our estimate for that bid: **0.8–1.1M tokens, 75–95 min**, with no reusable Tier 3 assets. Our record: UC48–UC58 within −28% to +9% of bid.

## Assumptions, exclusions
- Regular season in every rate. The WC (5 PA, 1 HR off Dylan Lee) is a separate ledger line. Spring excluded.
- **Not bid:**
  - medical claims;
  - any statement that the back *caused* anything;
  - projections of 2027 performance (we give three things to watch, not a forecast);
  - MLB-wide ranks (house population rule);
  - the pitcher redesign items (Tier B).
