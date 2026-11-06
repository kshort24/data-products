# Ledger patch: UC #62 / uc-pps-038 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. Paste the UC52–UC61 patches first; they are still pending.

| 62 | `uc-pps-038` | **Taijuan Walker, Phillies career recap: "Taijuan Walker, Phillie"** (2026-11-05) | Delivered · READY-CONDITIONAL (C1–C6) · harness 47/47 · DQ 15/0/0 · V1–V7 9/9 | `dp_uc62_*` + `uc-pps-038-Taijuan Walker Phillies Career Recap 20261105.md`; primary consumables `dp_uc62_walker_phillies_career_recap_report.pdf` and `dp_uc62_walker_phillies_career_dashboard.html` (Artifact "Taijuan Walker, Phillie"). Trail in `Agents for Data Products/data-products/uc-pps-038-walker-phillies-career-recap-001/`. First career recap of a departed pitcher; first contract-economics object |

Pattern inheritance additions (UC62):
- pitcher recap spine K53 → **K62** (CF-2d called with a new subject; no kernel edit needed)
- New, provisional: **KR-1** K-expected residual · **CE-1** contract economics (AAV basis) · **PR-1** stuff/luck/residual ledger
- KF-1: K49 `kellen_frame` generalized to any name (client-frame reproduction)

Next available: **UC #63 / dp_uc63** (pps next `uc-pps-039` · pos next `uc-pos-026` · cat next `uc-cat-003`) — as of 2026-11-05.

## Findings worth carrying
1. O-26 recurs: the client's name-filtered `nphl` dropped 483 Walker pitches. Count id rows vs name rows at T0 for any multi-club pitcher.
2. EV-1: `inds().ev_mu` changes population between 2015 and 2016+ (non-BIP EV rows 16% → 39–46%).
3. The Phillies pool runs a +.019 median luck gap (WB-1 − XW-1). Read any pitcher's luck gap against it, not against zero.
4. Opener games: a carry-in "start" can be bulk relief. Check the first pitch of the game.
