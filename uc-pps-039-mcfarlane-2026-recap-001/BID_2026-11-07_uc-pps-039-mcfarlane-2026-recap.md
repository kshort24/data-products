# BID: Alex McFarlane 2026 season recap — report (PDF), dashboard (HTML), slide content for Claude Design, stretch posed

**Status:** FILED 2026-11-07 00:52 ET · **AWARDED by RFP rule (treat as winner) — acceptance below** · **DELIVERED ≈01:17 ET, READY-CONDITIONAL (C1–C5), harness 45/45.** Actuals ≈265k / ≈36 min vs ≈385k / ≈49 min bid (`07` §5).
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments) · **Human DPO:** Kellen Short
**ID reservation:** UC **#63** · contract `uc-pps-039` · build `dp_uc63` · folder `uc-pps-039-mcfarlane-2026-recap-001`
**Collision check (00:50 ET):** the UC62 ledger patch reserves "next: UC #63 / dp_uc63 · pps `uc-pps-039`". No `dp_uc63*` file in the MLB
root or `out/`; no `uc-pps-039` folder in the control plane before this one. Repo ledger tail still reads UC52; UC52–UC62 patches pending paste.

## The ask
1. Recap Alex McFarlane's 2026 (RHP, MLBAM **686934**), told "hand-in-hand" with Orion Kerkering, drafted one round later in 2022.
2. **The client's narrative is the commentary.** Prefer his exact language; examine every claim in it; ensure the data are accurate.
3. Deliverables: **PDF report**, **HTML** (interactive dashboard), **slide content** built to be supplemented with animated visuals
   (the client finishes in Claude Design), **bid + acceptance + governance** artifacts (`00`–`07`), and a **stretch addition posed by the org**.
4. Standing instructions: build in the MLB data plane; receipts `00`–`07` here; scouting-report skill for voice; data-plane coding standards.

### Client questions → chapters / slides
| Q | Question (client's words) | Primary evidence |
|---|---|---|
| Q1 | "Time to recap Alex McFarlane's 2026 season" — the arrival | carry-ins CI-1..CI-5 (draft, April recall, Atlanta weekend, July recall, AA line); stint ledger from the log |
| Q2 | "First we take a look at his overall year" | client frame (333 pitches, 21 outings incl. 2 postseason): `nresults`, whiff, chase, hard-hit, barrel; context percentiles |
| Q3 | "Then we look at his pitch plot" | arsenal shapes in inches (pfx × 12), velo, spin; BS-1r bullet test |
| Q4 | "Pitch maps … against LHB and RHB" | stand-level results + mix (K44 `lhb/rhb_pitch_mix`), the two client subtitles |
| Q5 | "His pitches against each batter handedness" | stand × pitch whiff / chase / putaway |
| Q6 | "He has an outlier fastball" | the client chart (RHP FF in any Phillies game since 2015, velo vs spin) + **FO-1** rank |
| Q7 | "Key plank in the Bridge to Duran" | **BD-1** bridge outings from the log (Duran 661395 later in the same game) |

### Claims graded (HP rows; bars set here, before the grade is computed)
**Disclosure.** At T0 the organization reproduced the client frame's overall line and both stand lines, the stand × pitch whiff/chase
table, and the arsenal shape quantiles (needed to confirm the frame and the entity lock). Rows built on those numbers are marked *seen*.
FO-1, BD-1, the context percentiles, the AAA tier and the stretch have **not** been computed by anyone in this session.

| HP | Claim (client's words) | Bar | Status |
|---|---|---|---|
| HP-01 | "all 333 of his major league pitches across 21 outings including two postseason games" | REC exact (pitches, outings, postseason games) | seen |
| HP-02 | ".280 wOBA (good!) and .633 OPS (solid!)" | REC ±.0015 | seen |
| HP-03 | "26% K and 8.2% BB … ratio just exceeding 3:1" | REC at the client's printed precision; K:BB from counts in (3.0, 3.5] | seen |
| HP-04 | "Decent chunk of hard hits and barrels, but very strong whiff in total and good chase" | CX-1 pool (Phillies pitcher-seasons, regular season 2015–26, ≥ 150 pitches; KP-1 percentile). "very strong whiff" = whiff ≥ 75th pct; "good chase" = chase ≥ 60th pct; "decent chunk" of hard hits = HH% at or above the pool median (worse than half). 3 legs SUPPORTED · 2 PARTLY · else NOT | unseen |
| HP-05 | Pitch plot: FF "ride between 12 and 18 inches and run about a foot"; SI "runs up to 18 inches"; ST "sweeps at least a foot but is fairly flat"; "bullet slider" | FF: 10th–90th pct IVB inside [12, 18] in; run: median |HB| ≥ 11 in = SUPPORTED, 8–11 = PARTLY. SI: 90th pct |HB| ≥ 17 in. ST: median |HB| ≥ 12 in and median |IVB| ≤ 4 in. SL: **BS-1r** (BS-1 with hand passed in: mean |HB| ≤ 4.0 in and mean |IVB| ≤ 4.0 in, ≥ 50 SL) | seen |
| HP-06 | vs LHB "63.4% FF + 27.5% SL \| quality K Rate (33%) and Elite Walks Rate (2%)" | REC at printed precision | seen |
| HP-07 | vs RHB "45.6% SI + 25% FF + 15.6% SL + 13.9% ST \| Just .179 BAA … (41% HH, 9% Barrel)" | REC at printed precision (rounded, not truncated) | seen |
| HP-08 | "Plus SL to LHB: 38% Whiff/50% Chase. FF gets 32% Whiff on Swings to RHB. (33% whiff vs LHB)" | REC at printed precision | seen |
| HP-09 | "McFarlane has elite spin and elite velocity. His fastball is an outlier." | **FO-1**: RHP FF pitcher-seasons in Phillies games (house `pps` + `pos`, game_type not S/E, 2015–26, ≥ 100 FF). Elite = ≥ 90th pct on mean velo AND mean spin. Outlier = no more than 1% of pool seasons sit at or above him on both | unseen |
| HP-10 | "McFarlane emerged as a key plank in the Bridge to Duran" | **BD-1**: regular-season outings where he entered with the Phillies ahead and Duran (661395) pitched later the same game. SUPPORTED ≥ 5 such outings and ≥ 25% of his outings; PARTLY 3–4 or 15–25%; else NOT | unseen |
| HP-11 | Carry-ins: Kerkering "5th round out of Central Florida"; McFarlane "sat in the Phillies bullpen" the Atlanta weekend that "cost Rob Thomson his job" and "was not needed"; Kerk "rushed to the majors back in 2023"; McFarlane "dominated AA" | CONFIRMED / PARTLY / CORRECTED against public sources (MLB.com, MLBTR, school sites) + the log (no April appearance) | carry-in |
| HP-12 | "Improved command in 2026" | no pre-2026 Statcast for him in either plane → NOT OBSERVABLE from data; carry-in only | n/a |

### New governed objects (provisional; specs in `03` §2 before code)
- **BS-1r** — K52 BS-1 bullet-slider rule with the pitcher hand passed in (K52 hard-binds LHP). Non-breaking generalization.
- **FO-1** — fastball outlier rank (above). Population and floor copied from UC #47 (≥ 100 FF per pitcher-season); raw, not drift-adjusted.
- **BD-1** — bridge-to-Duran outing flag (above).
- **ST-1** — stint ledger: MLB outings from the house log + AAA outings from `lhvp26` (supporting tier, never blended), dated.

## Stretch addition (posed by the org — S-1, priced separately, built only if T1–T5 land inside the bid)
**S-1 "Draft-class twins": McFarlane's first 21 MLB outings vs Kerkering's first 21 MLB outings** (postseason included, the way each
pitcher actually arrived). Same KPI set, arsenal shape, entry state. The client's narrative opens with Kerkering; this makes the pairing
a chart instead of an aside. Data: house log, Kerkering id-locked at T1. Cost: 25k / 4 min.
(Offered, not built: S-2 an AAA→MLB velocity/usage bridge; S-3 a 2027 role projection — out of scope, no forecasting agent engaged.)

## Why this shop wins
1. **Inherit, don't re-derive.** K62 → K53 → K52 → … → K44 by sha-pinned import: `nresults`, `whiff_rate`, `chase_rate`, `putaway_rate`,
   `hard_hit_rate`, `pitch_mix` / `lhb_pitch_mix` / `rhb_pitch_mix`, `fpsr`, BR-1 `barrel_rate`, XW-1, WB-1, KP-1 `house_percentile`,
   `house_pitcher_seasons`, BS-1, `recap_viz` V1–V7. The client's notebook functions are the K44 Section A transcriptions — same numbers.
2. **The client frame is reproduced, then governed.** Client `pps` = Phillies pitching role, all game types; for McFarlane that is 313 R + 20 F
   = 333 pitches (no S/E rows). Name filter and id lock agree (333 = 333) — no O-26 contamination.
3. **The narrative gets fact-checked before it gets formatted.** One carry-in is already flagged for correction at bid time
   (Kerkering's school), and two subtitle numbers are truncated rather than rounded (HP-06/07) — the report keeps his words and fixes the digits.

## Scope
**In:** kernel, build + receipts, HP grades, figures F1–F7, report `.md` + `.pdf`, dashboard `.html` (+ Artifact), slide content
(`slides/`, one file per slide + data CSV/JSON + animation cues + Claude Design brief), harness, `00`–`07`, README, contract, ledger patch, S-1.
**Out:** the animations themselves (Claude Design, client-led); a Stuff+ model (the client's "Stuff model" subtitle is quoted as his read,
not graded — no stuff model in the data plane); AA Statcast (none exists).

## Price
| Phase | Departments | Tokens | Minutes |
|---|---|---|---|
| T0 recon (both planes), carry-ins (web), source profile, BID | strategy & intake | 110k | 10 |
| T1 kernel, build, receipts, HP + DQ | engineering | 60k | 8 |
| T2 figures F1–F7, render QA | design | 45k | 6 |
| T3 report md + PDF in the client's words | analytics-enabler | 35k | 5 |
| T4 dashboard + slide content + Claude Design brief | consumer success | 45k | 6 |
| T5 harness, certification | quality | 25k | 4 |
| T6 `00`–`07`, README, contract, ledger patch | governance + platform | 40k | 6 |
| **Base total** | | **≈360k** | **≈45 min** |
| S-1 stretch | engineering + design | 25k | 4 |
| **With stretch** | | **≈385k** | **≈49 min** |

**Calibration:** UC62 (pitcher recap, PDF + dashboard, new subject) actual ≈240k / 25 min against a heavier bid. This RFP adds a slide-content
deliverable, a Claude Design kit, web carry-in verification and a stretch, so it prices at ≈1.5× UC62's actual. Small sample (333 pitches)
keeps T1 cheap.

**Competitive position:** a shop without this kernel re-derives seven KPI functions and the wOBA weights (≈150k more), would not know the
house BS-1 bullet line (and would print "bullet slider" unchecked), and would ship the client's "Central Florida" as written.

---

## Award & acceptance
| Field | Value |
|---|---|
| RFP | "Alex McFarlane 2026 Season Recap" (client prompt, `intake/client_prompt_2026-11-07.md`) |
| Award | **WON** — per the RFP's own rule ("consider the bid a winner for the RFP and proceed with the work") |
| Accepted by | `data-product-owner` on behalf of the org, 2026-11-07 00:53 ET; human DPO ratification pending (Kellen Short) |
| Accepted scope | Base (≈360k / ≈45 min) **+ S-1 stretch** (≈25k / ≈4 min) — the RFP invites "any other additions … driven by the data product organization" |
| Acceptance criteria | (1) every number in the report, dashboard and slides traces to an `out/dp_uc63_*` receipt computed this session; (2) the client frame reconciles exactly (HP-01); (3) every client sentence used as commentary is either kept verbatim or carries a visible correction; (4) harness all PASS; (5) V1–V7 PASS on every figure; (6) certification verdict recorded in `05`; (7) bid vs actual recorded in `07` |
| Change control | A bar in this BID changed after a grade is computed is a breaking change (`version-controller`) |
