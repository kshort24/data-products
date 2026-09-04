# BID — Trea Turner 2026: recency read + season diagnosis

**Status:** **AWARDED 2026-09-03** (RFP exercise — bid filed and won; work proceeded immediately).
**Bidder:** the data product organization (`data-product-owner`, on behalf of all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-09-03
**ID reservation:** UC **#40** · contract `uc-pos-014` · build artifact `dp_uc40` · folder `uc-pos-014-turner-2026-recency-001`

---

## The ask (as submitted, 2026-09-03)

> "Let's take a look at Trea Turner. What is going on with him recently and maybe this year in general?
> Start by analyzing his high-level performance, defining where he has struggled this year. Then let's dig
> in to what 'good' has looked like in the past for him, both with the Phillies and in his prior career.
> Are there underlying indicators that are affecting his performance? Are there potential actions that could
> be taken by personas within the Phillies hitting department to drive better outcomes? Has his approach
> changed? Are there certain pitches or pitch groups that he is struggling against? Perhaps a trend against
> lefties or righties? Leaving a fair amount of latitude for data-product-owner to guide this direction."

Decomposed into eight answerable questions (Q1–Q8, see `01_strategy_intake.md`). Latitude is explicitly
delegated to the DPO; the DPO exercises it in three places, each declared at intake rather than after the
fact: (a) the **recency window definition**, (b) the **"good" benchmark definition**, and (c) the decision to
run this as an **extension of `uc-pos-006`** rather than a fresh study.

## The material fact that shapes this bid

This organization **already delivered a Trea Turner 2026 offense review** — UC #25 / `uc-pos-006` / `dp_uc24`,
2026-07-21, data through 2026-07-20, 33/33 verified. That product closed with an explicit open finding:

> *"July .980 OPS / 62 PA recovery real-but-young."*

Six weeks of new data now exist (2026-07-21 → 2026-09-02, 43 team games). **The single highest-value thing
this bid can buy is the resolution of that open call** — not a re-litigation of the season. A competing
organization bidding this RFP cold would spend its first hour rediscovering the down-year diagnosis this
shop published in July, and would have no parent figure to hold itself to.

Accordingly this bid prices a **parent-extension** UC, and commits to the standing
**parent-reproduction check** (`uc-pps-028`): before any new claim is made, the parent's published figures
are recomputed on the parent's own window and definitions, and any divergence is reported as a defect —
whether the divergence is in the data plane or in this organization's own evolving kernel.

## Deliverables bid (full-governance tier)

| # | Deliverable | Notes |
|---|---|---|
| 1 | **Branded PDF report** (~12 pp) | House voice per the scouting-report skill; §1 verdict table first (uc-pos-011 rule) |
| 2 | **Interactive HTML dashboard** | Self-contained, chart.js **vendored not CDN** (uc-pos-011 rule); month/window/split explorers |
| 3 | **Full receipts** | `00_`–`07_` + README + UC doc + this BID + telemetry; ~18–22 CSV receipts; 6 figures |
| 4 | **Independent verification harness** | `dp_uc40_verification.py`, second code path, every published number |
| 5 | **Governed kernel** | `dp_uc40_kernel.py` — inherits `dp_uc37` (`_fix` lineage, PL-1, PA-F1) verbatim where possible |
| 6 | **Ledger patch** | `uc_ledger_AI_PATCH_uc-pos-014-turner.md` |
| 7 | **Persona action card** | Hitting-department personas → observable → testable hypothesis (Q4), causation explicitly not claimed |

## Data position — verified at bid time (not assumed)

| Check | Result |
|---|---|
| PHI era source | `data/phillies/phils_{2023..2026}.parquet` — `phils_2026.parquet` refreshed **2026-09-03 14:45** |
| Pre-PHI source | `data/opponents/turner.parquet` — 15,279 rows, 93 cols, 2015-08-21 → 2022-10-15, single batter id |
| Entity lock | `batter == 607208`, single name `Turner, Trea` in both sources |
| 2026 volume | **2,276 R-season pitch rows · 602 PA · 135 games · 2026-03-26 → 2026-09-02** |
| New since parent | **43 games / ~169 PA** not in `uc-pos-006` |
| Season coverage | 2015–2022 (WSN→LAD, 14,498 R rows) + 2023–2026 (PHI, 9,401 R rows) = **12 seasons** |
| Schema asymmetry | PHI frames carry **30 columns** the pre-PHI frame does not — incl. `bat_speed`, `swing_length`, `attack_angle`. **Bat-tracking analysis is structurally PHI-2024+ only**; this is a sensor boundary, not a gap to impute (uc-pos-009 standard) |
| `bat_speed` coverage | 48.5–49.0% of pitch rows in 2024/2025/2026 — i.e. swings; stable across years, so cross-year comparison is legitimate |
| Duplicates | 0 on `(game_pk, at_bat_number, pitch_number)` |
| `game_type` | R / D / L / F / W present; **regular season only** in every rate; postseason cited as context with type disclosed |
| True gaps | No batting-order column (lineup-slot claims out of scope); no roster/medical/coaching log (causation not identifiable) |

## Price

**Basis:** instrumented actuals from `uc-pps-026` (bid 150k/105k/2.5h ≈ $6.75 → actual 110k/44.3k/93min
≈ $3.32) and `uc-pos-013` (nearest analogue: pos-side hitter window retrospective, 227 checks, dashboard +
PDF). **Method:** chars/4, ±20% systematic on input, ±5% on output; prices working tokens (artifacts, tool
I/O, reads), not harness overhead — comparable to telemetry history by construction.

Calibration adjustments applied to the `uc-pos-013` baseline:

- **−** kernel is ~85% inheritable from `dp_uc37` (the `_fix` lineage, PL-1, PA-F1 are already paid for)
- **+** 12 seasons of career context vs Bohm's 7, and a second physical source file with a different schema
- **+** the parent-reproduction check (a whole extra reconciliation surface, ~15 checks)
- **+** bat-tracking measurables panel (not in the Bohm build)
- **−** no RISP / runs-created family requested here

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T1 Recon + intake + source profile + bid *(largely spent at bid time)* | 70k | 8k | 25 |
| T2 Design: KPI specs, glossary deltas, model, lineage, DQ rules | 12k | 14k | 15 |
| T3 Build: `dp_uc40_kernel.py` + `dp_uc40_turner_recency.py` + receipts + 6 figures | 26k | 22k | 30 |
| T4 Report + PDF | 10k | 16k | 20 |
| T5 Interactive dashboard (vendored) | 10k | 14k | 15 |
| T6 Independent verification + parent-reproduction check | 12k | 12k | 20 |
| T7 Governance spine 00–07 + README + telemetry + ledger patch + close | 18k | 24k | 30 |
| Subtotal | 158k | 110k | 155 |
| Environmental contingency ~10% (pyarrow redirect, PDF cross-plane build, mount latency) | +16k | +11k | +16 |
| **BID** | **~174k** | **~121k** | **~2 h 51 m wall clock** |

**Token credits:** at Fable 5 API list rates ($10/M in, $50/M out):
174k × $10/M + 121k × $50/M ≈ **$7.79**, band **$7–10**. Cowork bills subscription usage; read as
API-equivalent credit value.

**De-scope options priced:** drop the dashboard → −14k out, −15 min, ≈ −$0.80. Drop the career (pre-PHI)
panel and answer 2026-only → −10k in / −8k out, −20 min, ≈ −$0.50 — **not recommended**, the RFP asks
explicitly for "prior career".

## Why this shop wins this RFP

1. **The parent is ours.** `uc-pos-006` is 6 weeks old, 33/33 verified, and its open call is exactly what the
   client is now asking about. We are not bidding to answer a question; we are bidding to *close a loop we
   already opened* — and we will hold ourselves to the parent's published numbers in public.
2. **Pattern inheritance is a price list.** The hitter kernel, the `_fix` defect lineage (D1–D6), the
   sensor-boundary NULL standard, PL-1 platoon counterfactual, the breakpoint-sensitivity requirement, the
   50-PA floor, and the vendor-don't-CDN dashboard rule are all already paid for by prior UCs. A competitor
   starts cold on every one of them and will either re-derive them or ship without them.
3. **We disclose our own defects.** Six known kernel defects (D1–D6) ship declared, with `_fix` variants
   beside the governed originals. That is a differentiator, not a liability.
4. **Falsify-before-describe is standing policy** (`uc-pps-027` C-1, `uc-pps-028` G8/G9). The client's phrasing
   contains at least two soft premises ("struggled", "approach has changed"). We price adjudicating them,
   including the outcome where the premise is wrong.

## Assumptions, exclusions, carry-ins

- **Regular-season rates only.** Postseason rows exist in both sources and are excluded from every rate; any
  postseason reference is labelled with `game_type`.
- **The 50-PA floor** is standing for batter rate stats. September 2026 (9 PA at bid time) is below floor and
  will carry ⚠ everywhere it appears; nothing is ranked on it.
- **Recency window is a DPO choice made after seeing the outcome** → a breakpoint-sensitivity scan is
  mandatory, not optional (`uc-pos-011` RC-5).
- **Causation is not identifiable.** No coaching, medical, roster, or batting-order data exists in this plane.
  Q4 (persona actions) is answered as *observable → persona remit → testable hypothesis*, never as attribution.
- **Manual carry-ins:** 2026 All-Star break = 2026-07-16 (inherited from `uc-pos-006`); Turner's 2021 midseason
  WSN→LAD trade (derived from the log, not carried in).
- **No external data is fetched.** Local parquet only.

## Award mechanics

On award this file is retained as the pricing receipt; `telemetry/run_economics_ledger.csv` and
`telemetry/calibration_report.md` record bid-vs-actual per phase and close the calibration loop.

---

> **STATUS UPDATE 2026-09-03: AWARDED.** Proceeded to delivery per the DPO's instruction to treat the bid as
> won. Actuals vs bid in `telemetry/`. Delivery spine: `00_dpo_orchestration_record.md`.
