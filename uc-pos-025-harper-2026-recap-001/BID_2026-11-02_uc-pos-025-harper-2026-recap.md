# BID: Bryce Harper 2026 season recap, "Bryce Harper | 3 |" notecard (governed pieces for Claude Design)

**Status:** FILED 2026-11-02 18:05 ET · **AWARDED by RFP rule (treat as winner)** · **DELIVERED ≈18:22 ET, READY-CONDITIONAL (C1–C6), harness 25/25.** Actuals: ≈183k / ≈28 min vs ≈410k / 57 min (`07` §5).
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments) · **Human DPO:** Kellen Short
**ID reservation:** UC **#61** · contract `uc-pos-025` · build `dp_uc61` · folder `uc-pos-025-harper-2026-recap-001`
**Collision check:** the UC60 ledger patch reserves "next: UC #61 / dp_uc61 · pos `uc-pos-025`". No `dp_uc61*` file and no `uc-pos-025` folder exists in either plane. The repo ledger still reads UC52; UC52–UC60 patches are pending paste.

## The ask
1. **A 2026 season recap of Bryce Harper, as one notecard** under the headline "Bryce Harper | 3 | {one line}", in three regions:
   - **TL-a** 3–5 executive-summary bullets, each one or two sentences, every number traceable.
   - **TL-b** cumulative wOBA by PA, 2026 against his 2015–25 seasons; OPS, OBP, SLG, BA and HR shipped in the same data so the card can switch metric.
   - **TR** pitch map split by pitcher hand: pitch groups, locations, KPI callouts, platoon commentary. The story: what he hunts and damages.
   - **B** spray chart of his hits on a basic field sketch, with batted-ball KPIs (hard-hit, barrel, line drive, direction).
2. **Pieces, not a finished poster.** Every region ships as (a) a reference PNG that passes the house visual standard, (b) the data behind it as CSV + JSON, (c) copy. A Claude Design brief ties them together for the later build and animation.
3. **"Build off the previous UC."** UC #23 (`uc-pos-005`, dp_uc22, "Own the Zone", first half 2026) is the only governed Harper UC. Its OZ-1..OZ-4 edge KPIs are carried forward to the full season. Ad-hoc Harper notebook scripts (`harper_vs_lhp_deep_dive.py`, `harper_2026_visuals.py`) are cited as context, not inherited (ungoverned).
4. **Standing instructions:** MLB repo, receipts `00`–`07` here, scouting-report-skill inspiration, competitive bid treated as won.

### Client questions → notecard regions
| Q | Ask | Region | Primary piece |
|---|---|---|---|
| Q1 | What kind of year was it? | headline + TL-a | `headlines.json`; season line vs his 11 prior Statcast seasons and the Phillies hitter-season pool |
| Q2 | How did it build? | TL-b | F1 cumulative wOBA by PA: 2026 red over the Washington (2015–18) and Phillies (2019–25) envelopes; OPS/OBP/SLG/BA/HR in the same long table |
| Q3 | What does he hunt and punish, and the platoon split? | TR | F2 pitch map, catcher's view, LHP and RHP panels, balls by pitch group, damage marked; callouts from the hand × group panel |
| Q4 | Where does the ball go? | B | F3 spray of hits on the basic field sketch; batted-ball KPI strip with his tenure range |

### Claims graded (HP rows; bars below, set before any grade is computed)
| HP | Claim | Source |
|---|---|---|
| HP-01 | .269/.380/.485, 29 HR, 155 H, 32 2B, 148 SO, 577 AB, 162 G | CI-1 MLB.com |
| HP-02 | "His approach and discipline held up" | CI-2 RotoWire season note |
| HP-03 | "His hard contact faded" | CI-2 |
| HP-04 | .997 OPS vs RHP, .657 vs LHP | CI-2 |
| HP-05 | 29th HR on 9/27 vs Tampa Bay; one HR in his prior 27 games | CI-2 |
| HP-06 | "He is owning the edge" (first half) holds for the full season | UC #23 headline, carried forward |

## Why this shop wins
### 1. Inherit, don't re-derive
- **K60 → K58 → K57 chain** (20+ pins): `season_panel`, `nresults_unrounded` (WB-2), `xwoba_pa`, `cell_panel`, CR-1 batted-ball profile, PA-L1 `derive_loc`, DR-1 `hit_direction`, K46 `pull_air`, DH-1 `game_seq`, the house `wall_outline`, `two_prop_z`, `ch1`.
- **SD-1/2/3** (UC60): `recap_viz` V1–V7 audit, `asb_2026` era, `phi_hitter_seasons_200` pool.
- **UC #23** `tag_regions` + `oz_kpis` (OZ family) imported, pinned.
- **Generalizations (Section B, non-breaking):** `load_career` parameterized on the subject (K58 hard-binds Schwarber); `pa_ledger` + `cum_slash` widen `cumulative_metric` from one metric to the whole slash line, endpoints reconciled to `nresults_unrounded`.

### 2. Premise checked before bidding (carry-ins quoted, never computed on)
- **CI-1** (MLB.com player page): 2026 162 G, 577 AB, 93 R, 155 H, 32 2B, 29 HR, 87 RBI, 148 SO, 7 SB, .269/.380/.485, .865 OPS.
- **CI-2** (RotoWire player page, 2026 notes): ".269/.380/.485, 29 HR, 87 RBI, 93 R, 7 SB across 693 PA"; "approach and discipline held up but hard contact faded"; ".997 OPS vs RHP, .657 vs LHP"; Aug 4 move to the outfield (first OF work since 2022) to make room for Luis Arraez; Aug 10 DH with knee soreness; 9/27 HR No. 29 vs TB "just once in his prior 27 games". RotoWire's injury list mixes 2025 items (wrist inflammation, June) and is **not** used.
- **Log reconciles at bid time:** 693 PA, 577 AB, 155 H, 32 2B, 3 3B, 29 HR, 148 SO, .269/.380/.485 exactly. 161 games with a PA + 1 defensive-only game (5/9 vs COL, fielding play at 1B in the log) = 162 G. 0 `truncated_pa`.
- **Disclosure:** the T0 source profile printed the season panel (chase, BB%, hard-hit, barrel, EV p90 by season) before these bars were written. The bars are leg-and-range rules fixed here, before any grade, H1/H2 split, hand panel or OZ run.

### 3. Pre-registered (18:05 ET)
- **Eras:** Washington 2015–18 (`data/opponents/harper.parquet`, id-locked) · Phillies 2019–25 · 2026. 2020 (58 G) stays in every band and is labelled. H1 ≤ 7/12, H2 ≥ 7/16 (SD-2 `asb_2026`).
- **AP-1 approach held (HP-02):** legs = 2026 chase rate ≤ his 2019–25 max; BB% ≥ his 2019–25 min; K% ≤ his 2019–25 max. 3 legs SUPPORTED · 2 PARTLY · else NOT SUPPORTED.
- **HC-1 hard contact faded (HP-03):** legs = hard-hit rate, barrel rate, EV p90 at or below his 2019–25 minimum. ≥ 2 SUPPORTED · 1 PARTLY · 0 NOT SUPPORTED. H2 vs H1 hard-hit `ch1` z reported beside, not graded.
- **OZ-H edge held (HP-06):** full-season OZ-1 ≥ 2025 OZ-1 → HELD; H2 vs H1 OZ-1 `ch1` CHANGED downward → FADED IN H2.
- **REC rules (HP-01/04/05):** slash ±.0015, counts exact; OPS by hand ±.002.
- **SM-1 floors:** hand × group cells < 30 PA or < 15 BIP print "small sample"; never a headline.
- **NC-1 notecard copy rule (new):** every number on the card resolves to a key in `headlines.json` (harness-checked). No causal or medical claims (regex-checked).

### 4. Visual standard
Every figure passes `recap_viz.audit` V1–V7 with eyeball QA. F1 is the V1 exception (cumulative lines). F2 draws balls **to scale** on the catcher's view with the house zone (half-width 0.83 ft). F3 draws every park on one basic sketch with the caption "Every park, drawn on one outline".

## Scope
**In:** kernel, T1 build + receipts, F1–F3 + composed reference notecard, HP grades, exec bullets, Claude Design brief + data kit, harness, `00`–`07`, README, contract, ledger patch.
**Out (Tier B, offered):** PDF report and multi-chapter dashboard (the notecard is the consumable); the animation itself (Claude Design, client-led); RBI/R/SB derivation (carry-ins only).

## Price
| Phase | Departments | Tokens | Minutes |
|---|---|---|---|
| T0 recon, carry-ins, BID, `01` | strategy & intake | 110k | 12 |
| T1 kernel, build, receipts | engineering | 70k | 10 |
| T2 F1–F3, reference card, V1–V7 audit | design | 90k | 12 |
| T3 HP grades, bullets, headline | analytics-enabler | 30k | 5 |
| T4 Claude Design brief + data kit | consumer success | 30k | 5 |
| T5 harness, certification | quality | 30k | 5 |
| T6 `02`–`07`, README, contract, ledger patch | governance + platform | 50k | 8 |
| **Total** | | **≈410k** | **≈57 min** |

**Calibration:** UC60 ran −50% on a same-subject recap with the shell imported whole. This bid prices a new subject (career loader generalization), a new cumulative contract (CM-2), two new chart forms for the house recap shell (pitch map, spray) and a new deliverable type (design kit), so it sits at ≈ 85% of UC60's bid rather than at UC60's actual.

**Competitive position:** a shop without this kernel would re-derive the slash line, wOBA weights, spray convention and zone geometry (≈ 150–200k more), and would not catch the 4/30 doubleheader order defect (DH-1) that UC58 already found.
