# BID: Phillies lineup vs Chris Sale, NL Wild Card Series Game 1

**Status:** **AWARDED 2026-09-29** (RFP exercise: bid filed, then treated as the winner per Kellen's instruction; actuals are reconciled in `07_platform_marketing.md` §3)
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-09-29 ET
**ID reservation:** UC **#50** · contract `uc-pos-018` · build artifact `dp_uc50` · folder `uc-pos-018-lineup-vs-sale-wc-g1-001`
**Collision check (bid time):** `dp_uc50*` had no files at the MLB root, in `out/` or in the control plane. `uc-pos-018*` appears only as "next" in the `uc-pps-034` ledger patch and in the `uc-pos-017` README. Numbering follows that patch (**next #50**). `uc_ledger_AI.md` still reads "next #25" (known drift, E-6 carried).

> **Procedural deviation D-1 (disclosed, not hidden).** First pitch was 2:00 p.m. ET, about 70 minutes after intake. The organization reserved the ID, priced the phases in its head, built, and shipped the pre-game consumables *before* writing this document. To keep the price honest, every line below is computed **mechanically** from `uc-pps-034`'s published actuals and its calibration rules C-1…C-6. T0 is the only line read off a live counter (C-1 method), and it was read at the moment of ID reservation, before any build work. `07` §3 grades the bid against the actuals. It does not get to grade itself kindly because it was written late.

---

## The ask (as submitted)

A prompt plus four notebook cells (`September 2026.ipynb`, cells 148–151), all Kellen's:

1. **Chris Sale preview (cell 148).** "Cursory, a starting point": the 2026 pitch-movement plot with a four-number subtitle (FF mph, SL whiff, SI run, CH whiff), pitch maps by batter side sized by usage, and release points.
2. **Three index cards (cells 149–151)** in lineup order:
   - **Turner**: vs LHP 2026 "pretty bad"; the narrative is *hit the ball where it is thrown, too many pulls on pitches away from him*. KPIs: AIR% on pulls (44%), LD rate straightaway (30%), BA oppo (.196), and a BIP facet by direction.
   - **Schwarber**: career vs Sale .327 wOBA / .779 OPS / 27 PA / .520 SLG; 1 in 5 BIP a barrel; less than half hit hard; a spray chart of his "5 career hits vs Sale".
   - **Harper**: "the best left-handed pitcher in baseball" (his quote); vs Sale **.100 OPS**, "BY FAR the worst" of LHP with 20+ PA.
3. **The instruction:** continue that rigor for **Bohm, Hill, De La Cruz, Stott, Sosa, Realmuto**, with a card each and a narrative and visual chosen for each. Add a **consolidated lineup scorecard** that includes Sale (2026 data in `atlp26`). Use the data plane's functions and standards, the scouting-report skill for inspiration, receipts `00`–`07` in the control plane, and this bid (tokens + time).

## Why this shop wins this RFP

1. **We have the parent pattern and the certified parts.** `uc-pos-001` (Phillies vs Wacha) is the house's lineup-vs-starter card. `uc-pos-017` certified the directional family (`build_bip`, `direction_rate`, `pull_air_rate`) that Turner's card leans on. `dp_uc44_kernel` carries the locked KPI kernel. We import all three by sha256. A competitor transcribes them, and transcription is how the repo got four drifting copies of `hit_direction`.
2. **We know where Sale's pitches actually live.** An id scan at bid time: Sale's pitches sit in **`sale.parquet` (2015 → 2025-05-23), `atlp26` (2026, 2,575)** and in 17 other opponent files, batter-keyed. Every lineup hitter's pitches sit in 4–13 source files (Phillies season logs included). A `player_name` filter misses them (O-26). We price one pass, one frame, id-locked, precedence-deduped (BF-1).
3. **We will grade the client's cards, not overwrite them.** Three of nine cards already exist. They get reproduced by his method, then by the governed one, and every difference is explained (HP family). The Harper ".100" is the first thing we check.
4. **The deadline is real and priced.** The first consumable (notecard + PDF) ships before first pitch. The receipts follow.
5. **The device runs the build where the data lives** (C-3). `pyarrow`, `scipy` and `plotly` go into `/tmp` on the laptop VM (the `/sessions` volume is full, 40 MB free). Only the PDF render (pango) runs in the cloud, on receipts.

## Data position (verified at bid time)

| Check | Result |
|---|---|
| Phillies log | `phils_2026.parquet` regular season through **2026-09-27** (Game 162); 162 games |
| Braves 2026 pitching | `atlp26.parquet` through 2026-09-27; Sale **2,575** pitches, 27 starts, last 2026-09-23 |
| Sale career | `sale.parquet` 2015-04-12 → 2025-05-23 (22,211 pitches). **2025 after 5/23 is present only vs the Phillies** → Sale's profile is 2026-only |
| Lineup ids (from the Phillies log, batter × modal name) | Turner 607208 · Schwarber 656941 · Harper 547180 · Bohm 664761 · Hill 656537 · De La Cruz 650559 · Stott 681082 · Sosa 624641 · Realmuto 592663 |
| H2H vs Sale | Every lineup PA vs Sale is 2023+; no postseason or spring PA exist |
| Minor-league tiers | `lhvo26` etc. hold De La Cruz and Bohm rows; excluded from MLB rates |

## Deliverables bid

| # | Deliverable | Notes |
|---|---|---|
| 1 | **One-page lineup notecard** (`out/dp_uc50_fig4_lineup_notecard.png`) | Sale strip + nine rows + the single attack rule. **Ships before first pitch** |
| 2 | **Nine index cards** (`out/dp_uc50_card_{1..9}_*.png`) | Three reproduced/governed from the client, six new. Each hitter gets the visual his story needs, not a template chart |
| 3 | Reader report `.md` + `.pdf` | Bottom line first, Sale section, lineup card, nine cards, notebook graded, caveats |
| 4 | Sale 2026 section | The client's three plots governed (movement, location by side, release) + TTO + arsenal by side |
| 5 | Governed kernel `dp_uc50_kernel.py` | Imports `dp_uc44` / `dp_uc46` / `dp_uc48` / `barrel_rate.py` (sha-pinned). New: XW-1, HL-1, LR-1, TT-1, IC-1, NF-2 |
| 6 | Build + receipts | `dp_uc50_lineup_vs_sale.py`, ~25 CSV receipts, DQ scorecard, freshness manifest, headlines JSON |
| 7 | Human-parent reconciliation | 12 HP rows |
| 8 | Verification harness | Independent code path (no kernel import); prose ↔ receipt family |
| 9 | Receipts `00`–`07`, README, this BID, contract, ledger patch | Control plane + MLB root |

**Explicitly not bid:** a Sale-shape similarity model (pitch groups are the proxy, labelled as one); park/weather/umpire; bullpen after Sale; any claim about the run value of Hill's 9/11 double beyond what the log shows; MLB-wide percentiles.

## Price

**Basis:** `uc-pps-034` actuals (~425k in, ~120k out, ~45 min, ≈$10.25) and its calibration C-1…C-6.
**Up:** nine subjects plus a pitcher instead of one; three client cards to reproduce; a 15-file id scan; a pre-game delivery with its own render-QA pass.
**Down:** analytic, not narrative-heavy per subject (the cards are short); every KPI function already exists except six small provisionals; the device environment repair is two pip lines (proven).
Per **C-1**, T0 is read off the counter at reservation. Per **C-2**, output is priced at 1.0× (nine narratives are prose). Per **C-3**, T1 input is ~50k because the build runs on the device. Per **C-4**, a defect line is kept. Per **C-6**, a render-QA line is added. Contingency **0%**.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, two-repo recon, house format + skills, notebook read, id scan (**sunk at reservation: ~255k**) | 255k | 5k | 7 |
| T1 Kernel (BF-1 + provisionals) + build + receipts, two iterations, on device | 50k | 25k | 9 |
| T2 Figures (4 + 9 cards) + render QA (C-6) | 45k | 15k | 7 |
| T3 Narratives for nine cards + notecard | 20k | 12k | 4 |
| T4 Report + PDF (cloud render) | 20k | 8k | 4 |
| T5 Verification harness (independent path) | 20k | 12k | 4 |
| T6 Governance 00–07, README, contract, ledger patch, commits | 45k | 38k | 12 |
| D Defect discovery (C-4) | 10k | 3k | 2 |
| Contingency 0% | 0 | 0 | 0 |
| **BID** | **~465k** | **~118k** | **~49 min wall clock** |

Time cross-check (C-5 rule, 0.10 min per 1k tokens × 0.8): 583k → 47 min. Consistent with the phase build-up.

**Token credits** at list rates ($10/M in, $50/M out): 465k × $10/M + 118k × $50/M ≈ **$10.55**, band **$9.00–12.50**.
Cowork bills subscription usage, so read this as API-equivalent credit value. It is **+3%** on the `uc-pps-034` actual ($10.25) for nine subjects plus a pitcher, because six of the nine cards run on functions this organization already certified.

**De-scope options priced:**
- Notecard + nine cards only (no report/PDF, no 00–07) → about **$5.40**.
- The six new cards only, no Sale section and no HP reconciliation → about **$4.10**. *Not recommended:* the Sale section is what makes the plans on the cards specific.
- Add an interactive dashboard (Artifact) → +10k in / +8k out / +5 min, about **+$0.50**.

## Assumptions, exclusions, carry-ins

- **Regular season for every rate.** The client's frames (`po26`, `pos`) keep spring and exhibition rows; the reconciliation shows where that matters.
- **Entity lock by MLBAM id.** Names reproduce the client's frames only (NF-2).
- **House wOBA** (FanGraphs weights over house PA) is the published wOBA, matching the client's numbers. Savant's `woba_value` credits reached-on-error; that difference is measured, not adopted (MV-1).
- **Carry-ins, labelled and never computed on:** batting order (prompt), game time/network (MLB.com, NBC listing), Harper's quote (client notebook).

---

> **STATUS UPDATE 2026-09-29: AWARDED.** Proceeding per Kellen's instruction to treat the bid as won.
> Actuals vs. bid are in `07_platform_marketing.md` §3. The delivery spine is `00_dpo_orchestration_record.md`.
