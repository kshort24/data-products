# BID: Aaron Nola's changeup in the zone — pitch map + KPI cards, built as a Claude Design animation kit

**Status:** FILED 2026-11-17 16:58 ET · **AWARDED by RFP rule (treat as winner) — acceptance below** · **DELIVERED ≈17:10 ET, READY-CONDITIONAL (C1–C3), harness 20/20.** Actuals ≈150k / ≈17 min vs ≈210k / ≈35 min bid (`07` §5).
**Bidder:** the data product organization (`data-product-owner`) · **Human DPO:** Kellen Short
**ID reservation:** UC **#65** · contract `uc-pps-041` · build `dp_uc65` · folder `uc-pps-041-nola-changeup-zone-kit-001`
**Collision check (16:58 ET):** UC64 patch reserves "next: UC #65 / dp_uc65 · pps `uc-pps-041`"; no `dp_uc65*` in the MLB root, no `uc-pps-041` folder. Parent: `uc-pps-040` (UC #64).

## The ask
An analytical closer for the client's video of Nola's 2026 changeups taken for strikes in the bottom third (zones 7/8/9): (1) the home-plate pitch map of
all his changeups with the video's pitches highlighted; (2) a few cards on the changeup — the client's KPIs (early even-count usage vs LHB, two-strike
group usage, LHB line, putaway / whiff / chase / in-zone) and others the org judges relevant. Output = figures and content Claude Design will animate.

## Frame & entity lock
House log, pitching role, `pitcher == 605400` (O-26 asserted; Hoffman guard). **Highlight set (CZ-1) = the client's definition on the client frame =
28 pitches (27 R + 1 F) = the 28 clips on disk.** Pitch-map population = **MLB changeups, 2026 regular season + Wild Card (489)**; the 13 spring-training
changeups in the client's `pps` are excluded (registered deviation **DV-1**: a "2026 pitch map" should not mix exhibition pitches; none of the 28 is affected).
Card KPIs = regular season (house rule), with a client-frame reproduction receipt beside each (**REC-C**).

## New governed objects (PROVISIONAL; kernel `dp_uc65_kernel.py` Section C)
| ID | Object | Spec |
|---|---|---|
| **CZ-1** | bottom-third called-strike changeup | `pitch_type == 'CH' & description == 'called_strike' & zone ∈ {7,8,9}` (client's line 89, verbatim) |
| **PNZ-1** | zone-normalized height | `plate_z_n = 1.5 + 2.0 × (plate_z − sz_bot)/(sz_top − sz_bot)`: each pitch drawn on a standard 1.5–3.5 ft zone *relative to its own batter's zone*, so Statcast zones 7/8/9 (batter-specific) land in the drawn bottom row. Raw `plate_z` with the client's mean zone ships as the alternate reference (client form). |
| **BB-1** | baseball-true marker | a pitch is a circle of diameter **2.9 in (0.242 ft)** in plate coordinates (client: "consistent for the size of a baseball"). |
| **EC-1** | early even-count usage | share of pitches to a side in counts with `balls == strikes & strikes < 2` (0-0, 1-1) that are changeups (client's Table 2, `lhb_pitch_mix` usage) |
| **TS-1** | two-strike group usage | share of `strikes == 2` pitches by K48 `GROUP_MAP` group, per year × side (client's Figure 1/2) |
| **ZN-1** | changeup location shares | in-zone (zones 1–9), bottom third (7–9), below the zone (`plate_z < sz_bot`), of all changeups; context pool = Phillies SP seasons (≥ 2,000 pitches) with ≥ 100 changeups |
| **CSB-1** | bottom-third take rate | CZ-1 / changeups located in zones 7–9 |
| **FP-1** | first-pitch changeup to LHB | CH share of first pitches to LHB and its strike rate (`type != 'B'`); ties to UC64's lefty first-pitch tripwire |

Inherited, not re-derived (K64 → K63 → … → K44, pinned): `nresults`, `putaway_rate`, `whiff_rate`, `chase_rate` (`in_zone_rate`), `pitch_mix` / `lhb_pitch_mix`,
`fpsr`, CSW, `rv100`, `add_pitch_group` (K48 GROUP_MAP), PT-H, recap_viz V1–V7; UC64 receipts for the 7/05 pivot and SQ-2 setup lift (CH → KC vs LHB).

## Deliverables
`slides/` kit on the UC61/UC63 pattern: `slide_content.md` (scene by scene: on-screen copy, visual, data, animation cue, speaker note), `copy_registry.json`
(every on-screen string, NC-1), `data/` per-scene receipts (incl. the 28-pitch table in date order with coordinates for the landing animation), `ref/`
16:9 reference PNGs (dark, to sit after video) + plotly JSON, `dp_uc65_claude_design_brief.md`, `manifest.json` (sha256). Plus `00`–`07`, README, contract, ledger patch.

## Price
| Phase | Tokens | Minutes |
|---|---|---|
| T0 frame lock, clip reconciliation, bid | 40k | 6 |
| T1 kernel + build + receipts (client-frame repro + governed) | 45k | 8 |
| T2 figures (pitch map ×2, card charts), V1–V7 + eyeball QA | 50k | 8 |
| T4 slide content, registry, brief, manifest | 35k | 6 |
| T5–T6 harness, `00`–`07`, README, contract, ledger | 40k | 7 |
| **Total** | **≈210k** | **≈35 min** |

**Calibration:** UC63's slide kit portion ≈ 45k; UC64 actual ≈ 300k / 62 min for a full recap + engine. This is a narrow follow-on reusing K64 and UC64 receipts.
**Why this shop:** it already holds the clip-to-pitch reconciliation (28 = 28), the batter-specific-zone trap, and the 7/05 changeup pivot from UC64; a fresh shop would draw raw heights and show highlighted "bottom-third" pitches floating outside the drawn zone.

## Award & acceptance
| Field | Value |
|---|---|
| Award | **WON** per the RFP rule; accepted by `data-product-owner` 2026-11-17 16:59 ET; DPO ratification pending |
| Acceptance criteria | (1) highlight set reconciles to the 28 clips; (2) every on-screen number in `copy_registry.json` traces to an `out/dp_uc65_*` receipt computed this session; (3) V1–V7 on every reference figure; (4) harness all PASS; (5) bid vs actual in `07` |
