# BID — Nestor Cortes Acquisition Read

**Status:** BID SUBMITTED — WORK NOT AWARDED. No build, design, or governance work has begun.
**Bidder:** Company of Agents (data-product-owner, on behalf of all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-08-19
**ID reservation (pending award):** UC **#37** · contract `uc-pps-026` · build artifact `dp_uc36` · folder `uc-pps-026-cortes-acquisition-001`
*Reservation note: the ledger's "Next available" remains UC #37 / dp_uc36 until a delivery row is appended. If another UC is delivered first, this bid re-prices only its recon delta — the scope and method stand.*

---

## The ask (from the submitted use case, 2026-08-19)

Acquisition-onboarding scouting read on **Nestor Cortes (LHP, MLBAM 641482)**, signed today to a
1-yr prorated major-league deal (Kilian → 60-day IL for the roster spot), returning from
mid-October 2025 arm surgery with zero competitive pitches since. Four question families:

1. **Deployment history** — starter vs reliever vs bulk-behind-opener, by season (DPO supplied working notebook logic: start = `inning_start == 1`; bulk = `inning_start > 1 & innings > 2`; start_share / bulk_share / innings_per_gm / plate_apps_per_gm)
2. **Platoon splits & approach evolution** — pitch mix, location, and results vs LHB/RHB by season
3. **Stuff trajectory** — velo/spin/break by pitch type by year; pre-surgery trend; what the Phillies should monitor on return
4. **Performance drivers** — which indicators correlate with his good and bad periods

Tailored to three personas: **Manager** (6th starter? bulk? high-leverage lefty?), **Battery**
(pitch selection, platoon efficacy), **Pitching Department** (stuff tracking, cues to chase).

## Deliverables bid (full-governance tier)

1. Branded PDF report (~10 pp) with persona sections — house voice per the pitcher-scouting-report skill
2. Interactive HTML dashboard (plotly, vendored not CDN per the uc-pos-011 rule; DPO's pitch-type dropdown pattern adopted)
3. Full receipts: `00_`–`07_` + README + contract doc, ~25–30 CSV receipts, independent verification harness, ledger patch, token-economist telemetry
4. Governed deployment-KPI family (start_share / bulk_share / innings_per_gm) — **after** the mandatory Rule-1 grep (uc-pps-015 bullpen-games inventory likely already governs "bulk"; inherit, don't reinvent)

## Data position — verified at bid time (not assumed)

| Check | Result |
|---|---|
| Source | `data/opponents/cortes.parquet` — exists, fetched ~2026-08-15 |
| Entity lock | single id **641482**, single name 'Cortes, Nestor' |
| Volume | 10,316 pitches · 120 cols · 2018-03-31 → 2025-09-03 |
| Seasons | 2018: 108 · 2019: 1,305 · 2020: 165 · 2021: 1,524 · 2022: 2,673 · 2023: 1,070 · 2024: 2,872 · 2025: 599 |
| game_type | R 10,087 · D 152 · L 55 · W 21 (2024 World Series in-frame; postseason context-only, never blended into rates) |
| Arsenal | FF 4,707 · FC 2,543 · ST 1,471 · CH 822 · SL 527 · SI 172 · CU 60 |
| DPO probe reconciliation | `cortes_np.csv` (repo root) = 10,316 rows — identical frame; notebook numbers will trace |
| **True gap** | **2026 — zero rows.** He has not pitched since surgery. Governed as the Kilian-2025-gap pattern (disclose, never impute). |

## Price

**Basis:** instrumented actuals from `uc-pos-004` and `uc-pps-019` token-economist ledgers
(last instrumented run landed within ~4% of bid), scaled for acquisition-variant depth
(dp_uc29 Kilian: 205 checks), dashboard (dp_uc28/dp_uc35 precedent), and career-scale data
(8 seasons vs Kilian's 2 eras). **Method:** chars/4, ±20% systematic on input, ±5% on output —
prices working tokens (artifacts, tool I/O, reads), not harness overhead; comparable to
telemetry history by construction.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T1 Recon + intake + source profile *(largely already spent at bid time)* | 63k | 7k | 20 |
| T2 Design: KPI specs, glossary, lineage, DQ rules | 10k | 12k | 15 |
| T3 Build: `dp_uc36` script + receipts + figures | 20k | 18k | 25 |
| T4 Report + PDF | 8k | 12k | 15 |
| T5 Interactive dashboard | 8k | 12k | 15 |
| T6 Independent verification | 8k | 10k | 15 |
| T7 Governance spine 00–07 + contract + telemetry + close | 16k | 22k | 30 |
| Subtotal | 133k | 93k | 135 |
| Environmental contingency ~15% (installs, retries, mount latency) | +17k | +12k | +15 |
| **BID** | **~150k** | **~105k** | **~2.5 h wall clock** |

**Token credits:** at Fable 5 API list rates ($10/M in, $50/M out):
150k × $10/M + 105k × $50/M ≈ **$6.75**, band **$6–9**. Cowork bills subscription usage;
read as API-equivalent credit value.

**De-scope option priced:** drop the dashboard → −20k out, −15 min, ≈ −$1.00.

## Why this shop wins

Pattern inheritance is a price list. Pitcher-side kernel ~70–85% verbatim from `dp_uc29`/`dp_uc30`;
the acquisition template is two weeks old and this is its third deployment; D1–D4 kernel fixes,
sensor-boundary NULL standard, and the never-blend era-tier rule are already paid for. A competing
organization starts cold on all of it. Recon is complete and sunk into this bid.

## Assumptions, exclusions, carry-ins

- Regular-season rates only; postseason (incl. 2024 WS) cited as context with game_type disclosed.
- No 2026 rehab/minors data exists locally; a rehab assignment triggers the closure-step re-read, not this product.
- Surgery type unspecified in reporting — logged as an intake gap, not guessed.
- Manual carry-ins (with sources, per freshness-manifest convention): signing 2026-08-19, 1-yr prorated ML deal, Kilian→60-day IL, surgery mid-Oct 2025, expected multi-inning relief role.
  Sources: NBC Sports player news 2026-08-19; Philadelphia Inquirer 2026-08-19; MLB.com; pricing via ayautomate.com / openrouter.ai (Fable 5 list rates).

## Award mechanics

On award, this file is superseded by the standard package and its telemetry ledger records
bid-vs-actual per phase (calibration report closes the loop). The bid stands as submitted;
if data freshness or roster facts change materially before award, the DPO re-verifies the
data-position table before starting.

---

> **STATUS UPDATE 2026-08-20: AWARDED AND DELIVERED.** This document is retained as the pricing receipt. Actuals vs bid live in `telemetry/run_economics_ledger.csv` + `telemetry/calibration_report.md` (under bid on all axes; scope delivered in full). Delivery spine: `00_dpo_orchestration_record.md`.
