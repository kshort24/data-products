# BID — Game 3: Painter vs Holmes, and the 20-80 scouting card

**Status:** **AWARDED 2026-09-13** (RFP exercise — bid filed and won per Kellen's explicit instruction to treat the bid as a winner and proceed; reconciled against actuals in `07_platform_marketing.md`).
**Bidder:** the data product organization (`data-product-owner`, on behalf of all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-09-13
**ID reservation:** UC **#44** · contract `uc-pps-030` · build artifact `dp_uc44` · folder `uc-pps-030-painter-vs-braves-001`

---

## The ask (as submitted)

A Game 3 advance on Andrew Painter at Atlanta, opposite Grant Holmes, with the wild-card seeding stakes stated
by the client. The ask arrives with **three artefacts that a competitor would treat as three different jobs**:

1. **An index card the client sketched by hand last night.** Pitch maps by handedness down the left with a
   one-stat callout per side; a pitch-description rail down the right carrying three specific claims —
   *"High-Ride FF (21% Whiff and 16.8 in. Vert)"*, *"Plus FS (39.5% Whiff to LHB)"*, *"Lands Breaking Balls
   (Above Average IZR)"*. **These are checkable numbers, and checking them is the job.**
2. **A speculative KPI.** *"An interesting twist could be assessing his pitches on a 20-80 scouting scale which
   is normally distributed around 50 as Major League average."* That is a request for a new governed object
   with a distributional assumption baked into its definition — an assumption that has to be tested, not
   restated.
3. **A notebook cell**, already written, that cuts Painter's season at `2026-07-21` into "First Half" /
   "Second Half" and reads pitch mix, in-zone rate, whiff and chase off that cut, plus a Phillies
   pitcher-seasons-since-2015 context scatter for breaking-ball in-zone rate.

Deliverables requested: a fully governed package with 00–07 receipts, a PDF report, an interactive dashboard
if it earns its place, and — explicitly — *"any other additions driven by the data product organization."*

## Why this shop wins this RFP

1. **We have scouted this pitcher before, and we know what we got wrong.** `uc-pps-023` (2026-07-31) is this
   shop's return read on Painter. Its headline finding — *"the four-seam is the anomaly, not the secondaries"*
   — is the direct ancestor of the card's first line. A competitor bidding this cold re-derives that finding
   at full price. We inherit it and spend the budget on what has changed since.
2. **Falsify-before-describe is standing policy here, and this ask is unusually falsifiable.** The card
   carries three numbers. A shop optimizing for agreeableness reproduces them in a nicer font. The value in
   this engagement is concentrated in whichever of the three does not survive contact with the current log —
   and this shop has priced the search for it rather than the presentation of it.
3. **A 20-80 scale is a governance problem wearing a scouting costume.** The scale *is* a z-score: 50 is the
   mean, 10 points is a standard deviation. That makes three things mandatory before a single grade can ship —
   a declared population, a minimum-sample gate, and a test of the normality the scale assumes. This shop
   writes the kpi-calculator spec first (`03_governance.md` §2) and computes second. A shop that ships grades
   without a named population has shipped decoration.
4. **The cross-level and small-sample discipline is already paid for.** `uc-pps-023` (AAA supporting tier),
   `uc-pos-015` (LV-1, how minor-league evidence enters an MLB conclusion) and `uc-pps-029` (the sensor-
   boundary and untracked-BIP rules) are all in force. Painter's by-stand, by-pitch cells run 7–131 pitches;
   knowing in advance which of them may carry a grade is the difference between a card and a liability.
5. **Known-defect exposure is measured, not assumed inapplicable.** D-1/D-2, D-7/O-13, O-3, O-5, O-7, O-8 all
   have a documented reading against this build before any number is published.

## Data position — verified at bid time, not assumed

| Check | Result |
|---|---|
| Source (MLB) | `data/phillies/phils_2026.parquet` — regular season, current through **2026-09-12**; target game D+1 |
| Benchmark frame | `phils_2015…2026.parquet`, both `phillies_role` values — 393,126 RHP pitches available for population construction |
| Subject volume | 1,861 MLB pitches / 484 PA / 22 starts in 2026; **720 pitches / 185 PA in the 8 starts since the option** |
| Entity lock | `pitcher == 691725` resolves to exactly one `player_name`; never a name filter |
| Opponent starter | MLBAM **656550** = Grant Holmes — **confirmed externally**, not inferred from the log (this is an improvement on `uc-pps-029`, where standing defect O-10 forced an inference) |
| Opponent hitters | 17 Atlanta bats resolvable by `des`-parse across 12 Phillies–Atlanta games; 9 clear 13 PA |
| Head-to-head | **47 PA, both starts in April** — and, on first inspection, against a materially different arsenal. Priced as a *finding*, not as a plan input |
| Splitter presence post-option | **zero** — discovered at bid time. This is the engagement |
| `arm_angle` completeness | **46%** in the graded window. Arm-slot analysis (the `uc-pps-023` signature angle) is **not bid** |
| Population thinness | Sweeper clears 100 pitches for only 14 pitcher-seasons. A floor-lowering rule has to exist *before* grades ship |

## Deliverables bid

| # | Deliverable | Notes |
|---|---|---|
| 1 | **The notecard, rendered** | The client's own index-card layout as a branded figure — pitch maps by stand with a one-stat callout each, grade rail on the right. This is the hero artefact, not an appendix |
| 2 | Branded PDF report | ~10 pp, verdict first, markdown → weasyprint, Phillies CSS |
| 3 | Interactive scouting card | Self-contained HTML; window / handedness / pitch-type filters, live pitch maps, four receipt tables. No external code, no CDN |
| 4 | Governed kernel | `dp_uc44_kernel.py` — Section A verbatim from `Baseball Functions.ipynb` via `dp_uc43_kernel`, Section C new |
| 5 | **Seven new governed objects** | SG-1…SG-5 (the 20-80 family), AR-1 (arsenal turnover), PM-1 (pitch-map centroid), each with a full kpi-calculator spec |
| 6 | Full receipts | `00`–`07` + README + this BID; ~30 CSV receipts, 5 figures, a JSON payload |
| 7 | Independent verification | 7 families (A–G) including narrative/receipt reconciliation of every number the report asserts |
| 8 | Ledger patch + repo-side UC contract | `uc_ledger_AI_PATCH_…` and `uc-pps-030-Andrew Painter ATL 20260913.md` |

**Explicitly not bid / out of scope:** arm-slot / release-point analysis (`arm_angle` 54% null — descoped with cause); a full Braves advance on Holmes's season (the repo holds Holmes only against Philadelphia); any bullpen or leverage modelling; a post-game backtest (offered as the closure step, not delivered here); ratification of the new KPI family (requires an independent second use).

## Price

**Basis:** `uc-pps-029` (bid ~201k in / ~112k out / 2 h 31 m) as the nearest structural analogue — same client, same
week, same governance depth, same device-bridge pairing. Adjusted **down** for a single subject instead of
nine and a confirmed rather than inferred opponent id; adjusted **up** for a **twelve-season benchmark frame**
(the 2015–2026 pull is an order of magnitude more data than any prior uc-pps build has loaded), a **brand-new
KPI family with a distributional assumption that must be tested**, and a **bespoke hero figure** built to a
client sketch rather than to a house template.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, cross-repo reconnaissance, prior-Painter retrieval | 40k | 5k | 14 |
| T1 Source profiling, entity locks, notecard reconciliation (the falsification pass) | 45k | 7k | 16 |
| T2 Kernel transcription + SG/AR/PM specification + build + defect exposure | 55k | 26k | 26 |
| T3 The notecard figure + 4 supporting figures | 30k | 20k | 22 |
| T4 PDF + interactive card | 25k | 22k | 18 |
| T5 Verification harness, families A–G | 20k | 16k | 14 |
| T6 Governance spine 00–07 + README + BID + ledger patch + repo contract | 25k | 28k | 20 |
| Subtotal | 240k | 124k | 130 |
| Environmental contingency ~15% — **`device_bash` is down on this device** (Windows update 2026-09-08 broke the workspace mount), so the whole data plane has to be staged into the cloud container and committed back | +36k | +12k | +18 |
| **BID** | **~276k** | **~136k** | **~2 h 28 m wall clock** |

**Token credits:** at list rates ($10/M in, $50/M out): 276k × $10/M + 136k × $50/M ≈ **$9.56**, band **$8–12**.
Cowork bills subscription usage; read as API-equivalent credit value.

**De-scope options priced:**
- Drop the interactive card → −18k out, −18 min, ≈ −$0.95. *Not recommended* — the by-stand, by-pitch cells are where the finding lives, and a static card cannot show six pitches × three windows × three handedness states.
- Drop the 20-80 family, report raw rates only → −30k in, −22k out, −30 min, ≈ −$1.40. This is the ask, so this is really a different engagement.
- Report-only tier (no 00–07, no verification harness) → ≈ **$4.10**.
- Add the Holmes half as a full second advance → +35k in, +15k out, +25 min, ≈ −— **cannot be bid**: the repo holds 260 Holmes pitches, all against Philadelphia. Priced as unavailable rather than expensive.

## Assumptions, exclusions, carry-ins

- **Manual carry-ins from the client, accepted as given and logged, none of them in the parquet:** Painter starts Game 3; Holmes starts opposite him; the Phillies are three games up on Arizona and one back of the Cubs; Atlanta is out of reach.
- **Target game** is D+1 of the last logged game (2026-09-12 → 2026-09-13). The build refuses to run against a different anchor.
- **Regular season only.** 52 spring-training pitches excluded from every rate.
- **AAA is never blended.** Lehigh Valley rows load unweighted and enter no MLB rate.
- **No external data fetched into any computation.** One external lookup was made — confirming MLBAM 656550 is Grant Holmes — and it is logged as an identity check, not a data source.
- **The grading window is the post-option arsenal.** A full-season grade would average two different pitchers, and the bid says so up front rather than discovering it in delivery.

## Award mechanics

On award this file is retained as the pricing receipt; bid-vs-actual reconciliation lives in
`07_platform_marketing.md` §3.

---

> **STATUS UPDATE 2026-09-13: AWARDED.** Proceeded to delivery per Kellen's instruction to treat the bid as
> won. Actuals vs. bid in `07_platform_marketing.md`. Delivery spine: `00_dpo_orchestration_record.md`.
