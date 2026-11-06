# BID: Taijuan Walker, Phillies career recap (2023–26) with pre-Phillies context, PDF + interactive dashboard

**Status:** FILED 2026-11-05 20:19 ET · **AWARDED by RFP rule (treat as winner)** · delivery and actuals in `07` §5.
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments) · **Human DPO:** Kellen Short
**ID reservation:** UC **#62** · contract `uc-pps-038` · build `dp_uc62` · folder `uc-pps-038-walker-phillies-career-recap-001`
**Collision check (20:17 ET):** the UC61 ledger patch reserves "next: UC #62 / dp_uc62 · pps `uc-pps-038`". No `dp_uc62*` file in the MLB
root or `out/`, and no `uc-pps-038` folder in the control plane. Repo ledger tail still reads UC52; UC52–UC61 patches are pending paste.

## The ask
1. "Tell me the story of Tai Walker": a Phillies career recap for a pitcher the club paid $18M in 2026 while he pitched in the Angels' system.
2. The client's own frame and chart: every Walker MLB season 2015–26 against Phillies pitcher-seasons since 2015, wOBA as a function of K%,
   his career overall highlighted.
3. Standing instructions: build in the MLB data plane; receipts `00`–`07` here; scouting-report skill for voice; bid treated as won.
4. Deliverables: **PDF report** (required), **interactive dashboard** (explore), any further form the organization chooses.

### Client questions → chapters
| Q | Question | Primary evidence |
|---|---|---|
| Q1 | What did the Phillies get for four years? | tenure line by season from the house log; outs and BF reconciled to public IP; ranks in the KP-1 Phillies pitcher-season pool |
| Q2 | What did they buy in December 2022? | 2015–22 career frame (CF-2d, id-locked); the client's K%→wOBA chart, rebuilt; **KR-1** residual; same-basis luck gap (WB-1 vs XW-1) |
| Q3 | What broke? | arsenal by season: mix, velocity, whiff by pitch; K%, chase, zone, hard-hit, barrel; **PR-1** pre-registered ledger |
| Q4 | What did it cost? | **CE-1** contract economics: AAV carry-in over outs and batters faced from the log |
| Q5 | How did it end? | 2026 start log (GS-1) + the release / Angels timeline as labelled carry-ins (never computed on) |

### Claims graded (HP rows; bars set here, before any grade is computed)
| HP | Claim | Source | Bar |
|---|---|---|---|
| HP-01 | The client CSV reproduces | client code, cell above | pitches and PA per season match the client frame rebuilt with NF-1 + `pps` (K49 `kellen_frame` rule, subject passed in), exact |
| HP-02 | "Paid nearly $18 million this season" | client; CI-1 | carry-in: $18M = final year of 4/$72M → CONFIRMED / PARTLY / NOT |
| HP-03 | "To pitch in the Angels minor league system" | client; CI-2..CI-4 | carry-in timeline; graded on completeness |
| HP-04 | 2026 worst, 2024 3rd-worst of 199 Phillies pitcher-seasons by wOBA | turn-1 reply | restated on the governed pool (regular season, KP-1 ≥ 100 PA); CONFIRMED if both ranks hold, PARTLY if one |
| HP-05 | Career split .303 (2015–22) vs .350 (2023–26) | turn-1 reply | governed `nresults` on the pooled frame, ±.003 |
| HP-06 | 2015 `ev_mu` 88.9 is a tracking artifact | turn-1 reply | share of 2015 BIP with null/imputed EV vs 2016+; CONFIRMED if 2015 ≥ 2× the 2016–22 rate |
| HP-07 | Code defects CR-1..CR-4 (games > 3 vs "at least 3"; no career row; `inds` / `leadoff_walk_rate` merged then dropped; `subtitle` kwarg) | turn-1 reply | each reproduced or withdrawn on the pinned stack (plotly 6.0.1) |

## Pre-registration (filed 20:19 ET, before any signature below marked *unseen* is computed)
**Disclosure.** At T0 the organization read the client CSV: season K%, whiff%, wOBA, hard-hit, barrel and the turn-1 OLS residuals.
Signatures built on those numbers are marked *seen*. Nothing marked *unseen* has been computed by anyone in this session.

**PR-1 ledger.** Scored with the inherited PA-1 rule (`K48.signature_verdict` / `strength_from_signatures`). Regular season, MLB games,
id-locked (MLBAM 592836). **Before** = 2021–22 pooled (the two Mets seasons that set his market). **After** = 2023–26 pooled (the Phillies tenure).

| Family | # | Signature | Dir | Bar | Status |
|---|---|---|---|---|---|
| H-S "the stuff declined" | S1 | K% | − | 3.0 pts | seen |
| | S2 | whiff% (K44) | − | 3.0 pts | seen |
| | S3 | four-seam (FF) mean velocity | − | 1.0 mph | unseen |
| | S4 | splitter (FS) whiff% | − | 5.0 pts | unseen |
| | S5 | xwOBA (XW-1) | + | .025 | unseen |
| H-L "it was mostly luck" | L1 | luck gap = WB-1 wOBA − XW-1 xwOBA | + | .015 | unseen |
| | L2 | luck gap, 2024 alone vs before | + | .020 | unseen |
| H-R "the price was set on a residual" | R1 | KR-1 residual, 2021–22 pooled, vs 0 | − | .025 | seen |
| | R2 | luck gap, 2021–22 pooled, vs 0 | − | .010 | unseen |
| | R3 | KR-1 residual, 2021–22 vs 2015–19 pooled | − | .010 | seen |

**Call rule (registered):** H-S SUPPORTED/STRONG and H-L UNSUPPORTED → "the arm, not the luck"; H-L SUPPORTED/STRONG and H-S not →
"a sound arm, unlucky"; both → "both"; neither → "no single story". H-R SUPPORTED/STRONG appends "and the price was set on a residual".
A bar changed after publication is a breaking change (`version-controller`).

**KR-1 (new, provisional).** wOBA allowed minus the wOBA a pitcher-season "should" allow at its K%, from an unweighted OLS (the client's
`trendline='ols'`) of house wOBA on K% over the Phillies pitcher-season pool 2015–26 (regular season, KP-1 ≥ 100 PA), **subject excluded**.
Spec in `03` §2; R² and n printed wherever the line is drawn (V4).

**CE-1 (new, provisional).** Contract cost per out recorded and per batter faced, by season = AAV carry-in ÷ log counts. Labelled
"AAV basis"; no cash-flow, deferral or luxury-tax claims.

## Why this shop wins
1. **Inherit, don't re-derive.** `dp_uc53_kernel` (sha `03d7e380…`) and through it K52/K51/K50/K49/K48/K44: `nresults`, whiff/chase/putaway,
   hard-hit, barrel, CF-2d career frame, house pitcher-seasons + RP-1 role, GS-1 game score, XW-1 xwOBA, WB-1 same-basis wOBA, PA-1 ledger,
   OU-2 outs, NF-1 client-frame reproduction. Visual standard `phillies_dp.recap_viz` V1–V7 (sha `e6c9436a…`).
2. **Premise checked before bidding.** The client's "nearly $18 million … Angels minor league system" is reconciled against four public sources
   (CI-1..CI-4) before a word is written, including a conflict between them on the Angels innings.
3. **Pre-registered.** The ending of the story is a scored ledger, not a narrator's preference.
4. **One narrative module** feeds report and dashboard, so the PDF and the page cannot disagree.

## Scope
**In:** kernel, build, receipts, EDA to file, HP grades, PR-1, KR-1, CE-1, 8–10 figures (V1–V7 audited), PDF (≤ 10 pp), dashboard
(repo copy + Artifact), harness, `00`–`07`, README, contract, ledger patch.
**Out:** ERA/FIP recomputation (ER is not in the log; ERA is a carry-in), minor-league Statcast (not in the house data), contract
advice beyond the 2026 facts, the client's notebook (not edited).

## Price
| Phase | Departments | Tokens | Minutes |
|---|---|---|---|
| T0 recon (2 planes, 6 kernels, skill), env, carry-ins, BID, `01` | strategy & intake | 95k | 12 |
| T1 kernel, build, HP reproduction, EDA, receipts | engineering | 60k | 10 |
| T2 figures + V1–V7 audit + render QA | design | 55k | 10 |
| T3 narrative module + dashboard + Artifact | consumer success | 55k | 10 |
| T4 report + PDF | analytics-enabler | 25k | 5 |
| T5 harness + DQ + certification | quality | 30k | 6 |
| T6 `02`–`07`, README, contract, ledger patch | governance + platform | 40k | 8 |
| **Total** | | **≈360k** | **≈61 min** |

**Calibration.** UC61 (hitter, kit only) came in −55% on a 410k bid; UC53 (pitcher, PDF + dashboard + Artifact) ran ≈ 518k counter-basis
with a 275k T0. This bid uses UC61's counter basis (context consumed) and adds Tier B (PDF + dashboard + Artifact ≈ 80k), a two-club career
frame and three new objects. T0 is priced at what it actually cost here.

**Competitive position.** A shop without this kernel re-derives wOBA weights, the PA rule, xwOBA basis, outs and the Phillies pool
(≈ 150–200k more), and would ship the client's 2025 row with its 18 NLDS pitches inside a "regular season" rate (SRC-1, found in T0 profiling).
