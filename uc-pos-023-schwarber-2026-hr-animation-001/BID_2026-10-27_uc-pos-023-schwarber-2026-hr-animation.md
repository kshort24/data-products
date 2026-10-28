# BID: Kyle Schwarber 2026 home runs, animated: "Forty-Five and a Question Mark"

**Status:** FILED 2026-10-27 19:49 ET · **AWARDED by RFP rule (treat as winner); build proceeds in this chat.** Actuals reconcile in `07_platform_marketing.md` §5.
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-10-27 (T0 wall clock 19:39 → 19:49 ET)
**ID reservation:** UC **#58** · contract `uc-pos-023` · build artifact `dp_uc58` · control-plane folder `uc-pos-023-schwarber-2026-hr-animation-001`
**Collision check (bid time):** no `dp_uc58*` in the MLB root, `out/`, `eda/` or the control plane. `uc-pos-023` / `dp_uc58` appear only as "next available" in the UC57 ledger patch. The repo ledger's own "Next available" line (UC52) is stale; UC52–UC57 patches are pending paste.

**Prior Schwarber work (inherited, not redone):**
| UC | Contract | Delivered | What it settled | What this bid takes from it |
|---|---|---|---|---|
| UC21 | `uc-pos-004` (`dp_uc20`) | 2026-07-14 | First-half ASG / Derby runner-up retrospective | Entity lock 656941, SC-1/SC-2 context; first-half framing |
| UC33 | `uc-pos-009` (`dp_uc32`) | 2026-08-08 | Swing decay; sensor-boundary NULL standard; sweet-spot-% failure | NULL standard (never `fillna(0)` a rate) |

**What is different about this RFP.** It is not a recap report. The client is producing a **video**: Claude Design animates a governed narrative, and the client splices Baseball Savant HR clips in between. The organization's product is therefore the **data and direction a motion designer needs**, governed the way a report would be: every number on screen traceable to a receipt, every highlight chosen by a rule fixed before looking, every client claim graded on his own frame. This is the **first Claude Design handoff UC** in the repo and the first whose consumer is another model.

## Audit counters (session token counter, tokens left)
| Mark | When | Counter | Δ | Cumulative |
|---|---|---|---|---|
| C0 | Turn start (this RFP) | 15,000,000 | — | 0 |
| C1 | Two-repo recon: both CLAUDE.md, ledger tail + UC57 patch, UC57 README/00/01/BID, K57 surface, Rule-1 greps (WPA, wall, ball size, cumulative), cbp-spray + CBP trace plan, clip pipeline (`resolve_play_ids.py`, `download_clips.py`) | 14,929,354 | 70.6k | 70.6k |
| C2 | Render stack to `/tmp/pyrender` (ENV-3), lineage 17/17, profile 2015–26 + opponent file, 2026 HR log, 9 web searches/reads (carry-ins) | 14,884,030 | 45.3k | 115.9k |
| C3 | BID, `00`, `01` written | ≈14,862,000 | ≈22k | **≈138k** |

## The ask (as submitted)
`Schwarber_2026_Home_Runs.md`: "What happened to this man? Should we be concerned?" The back and the lost pop are parked for the larger **Kyle Schwarber 2026 Season Recap** UC. This UC is ONLY the animated segment. Storyboard, in the client's order:
1. Cumulative HR by cumulative PA, one line per season, chronological; pre-Phillies in its own color; all years move together.
2. Fill in previous Phillies years in a different gray.
3. Follow 2026 deliberately, stopping to highlight HRs (max EV, max distance, max WPA, the Cardinals walk-off, a three-homer game), each stop cutting cleanly to a Savant clip.
4. Hold the finished lines; the end labels transition into a table of single-season HR totals showing where 2026 falls.
5. Spray chart: sketched Citizens Bank Park wall, 45 dots colored by pitcher hand; commentary on the perceived loss of thump (EV, distance, barrel rate).
6. Two pitch maps (LHP, RHP), colored by his `pitch_group`; LHP section cuts to clips "off lefty fastballs"; return and examine RHP. Return-from-clip transitions zoom out from the example to the whole view.
7. Consolidated view of the three screens to wrap.
Plus the client's reference Python (pandas + plotly express) for every view and a highlight shortlist in comments.

RFP instructions: (a) work in the MLB repo (data plane); (b) governed, documented, receipts `00`–`07` in a `data-products/` subfolder of the control plane; scouting-report skill and sibling MLB outputs for inspiration; data-plane coding standards; (c) token + time estimate framed as a competitive bid; (d) treat as won and proceed. From the intake Q&A (this chat): the technical overview assesses **our existing Python** (the client's reference code) as the engine behind the animation, and the Claude Design prompt carries **real governed numbers**.

### Client questions → scenes
| Q | Client ask | Scene | Data receipt |
|---|---|---|---|
| Q1 | Cumulative HR by PA, all seasons, eras colored | S1–S2 | `out/dp_uc58_cum_hr_by_pa.csv` |
| Q2 | 2026 with highlight stops + clip cuts | S3 | `out/dp_uc58_highlights.csv`, `out/dp_uc58_clip_list.csv` |
| Q3 | Hold → table of season totals, where 2026 ranks | S4 | `out/dp_uc58_season_table.csv` |
| Q4 | Spray chart on CBP outline, by hand; thump context | S5 | `out/dp_uc58_spray_2026.csv`, `out/dp_uc58_hr_quality_by_season.csv` |
| Q5 | Pitch maps LHP / RHP by pitch group; LHP clips; RHP read | S6–S7 | `out/dp_uc58_pitchmap_2026.csv`, `out/dp_uc58_hand_group_by_season.csv` |
| Q6 | Consolidated three-screen wrap | S8 | all of the above |

### Client claims to be graded (HP rows, client frame first)
| HP | Claim (client's words) | Source |
|---|---|---|
| HP-01 | "The 113 mph Max EV was the lowest of his Phillies tenure" | code comment |
| HP-02 | "the 106.3 average EV was also the lowest" | code comment |
| HP-03 | "His average home run was shorter than ever (Phillies era)" | code comment |
| HP-04 | "his longest was shorter than all but one season" | code comment |
| HP-05 | "91% of his home runs were barrels which is also the second-lowest of his Phillies tenure" | code comment |
| HP-06 | "his ability to crush breaking balls even from lefties seems to be compromised" (two HR on lefty breaking balls) | code comment |
| HP-07 | "He was not absolutely crushing RHP Fastballs … It is on FF from RHP" | code comment |
| HP-08 | Max EV: "Home run in the 9th inning of one of the doubleheader games against the Giants on 4/30" | code comment |
| HP-09 | Max distance: "Coors Field blast in the 5th inning from April 3rd" | code comment |
| HP-10 | Max WPA: "it is the Cardinals walk off on 8/23" (6/28 in New York considered) | code comment |
| HP-11 | "Three dongs against the Mets on 6/20" | code comment |
| HP-12 | LHP breaking-ball HRs: "Braves on 4/26 and Nats on 9/15 + ATL in playoffs" (Dylan Lee) | code comment |
| HP-13 | RHP four-seam top EV: "At Pittsburgh in May, Home against Colorado a week earlier and the Mets one from before" | code comment |
| HP-14 | "the one against the Braves on Labor Day to deliver a victory" | code comment |
| HP-15 | "place 45 dots for his home runs" | storyboard |

## Why this shop wins this RFP
### 1. We inherit instead of re-deriving.
- **Spine K57** (`dp_uc57_kernel.py`, MLB root, sha pinned at build) → K56 → K55 → K54 chain: **17 lineage pins re-asserted at bid time, 17/17 PASS.** Brings LP-1 loader, `PITCH_KEY`, `NON_PA`, `client_pitch_group` (CPG-1, the client's own map, verbatim), `barrel_rate_g`, DR-1/PA-L1 `derive_loc` (hc → feet, cbp-spray convention), `CBP_DIMS` (cbp-spray park SoT 329/374/401/369/330).
- **`cumulative_metric.py`** (house cumulative-by-PA engine behind Harper BB%, Marsh XBH, Alvarado wOBA) computes the S1–S3 curves with its `reconcile=` endpoint assertion. No new cumulative code.
- **WPA sign rule** mirrors `dp_uc51` (pitching WPA = +dHWE when PHI home, −dHWE away). Batting is the mirror: **WP-1** below.
- **Clip pipeline**: the clip list ships in the input schema of the client's own `resolve_play_ids.py` → `download_clips.py`, so the clip pull is two commands.

### 2. We checked the premise before bidding (carry-ins sourced, never computed on).
- **CI-1** MLB.com final 2026 leaders: Schwarber **45 HR, tied with Pete Crow-Armstrong for the MLB lead**; "followed up his career-high 56 homers from last year with 45". **Log reconciles: 45 regular-season HR, 702 PA.**
- **CI-2** Yahoo/SB Nation report card (2026-10-21): 156 G, .232/.354/.503, 130 wRC+, 2.9 fWAR; 22 HR in the first 56 games; first half .254/.367/.560, second half .199/.336/.416; a "mysterious back injury" the team downplayed (no onset date given); K% 31.4%; the 8/23 walk-off ended a three-year Phillies walk-off-HR drought.
- **CI-3** Game facts: 6/20 vs NYM 15-3, HRs off Freddy Peralta (456 ft), Cionel Pérez (457 ft, same inning) and Tobias Myers (6abc/AP); 8/23 vs STL 6-4, two-out two-run walk-off off Riley O'Brien, 459 ft, his MLB-leading 39th (TSN/AP); WC Game 2 at ATL (Wed 9/30): eighth-inning HR off Dylan Lee (MLB.com). **All three reconcile to the log** (pitcher ids, innings, distances).
- **CI-4** Wikipedia: 16 / 30 / 26 / 38 / 32 (25 WSH + 7 BOS) / 46 / 47; 385 career HR through 2026-09-15. **Log reconciles: 340 through 2025 + 45 = 385.**

### 3. We pre-register the argument (set 19:49 ET, before any grade is computed).
- **CP-1 x-axis = plate appearances.** The governed curve is `cumulative_metric.cumulative_frame(df, 'hr')`: one row per PA (`events` not null, minus `truncated_pa`), regular season, de-duplicated on `PITCH_KEY`, sorted date → game → at-bat. Endpoints asserted equal to the season HR count.
- **SE-1 seasons and eras.** 12 seasons, 2015–2026. Pre-Phillies = 2015–21 (CHC; 2021 WSH+BOS drawn as one season line, labelled); Phillies tenure = 2022–25; 2026 red. 2016 (2 games, 0 HR, knee) is drawn and labelled, never dropped.
- **WP-1 batter WPA** = `delta_home_win_exp` when he bats in the bottom half (PHI home), `−delta_home_win_exp` when in the top. Max WPA is ranked on WP-1, not on raw dHWE.
- **HL-1 highlight rules** (regular season 2026 unless stated): max EV (tie → longer); max distance; max WP-1; walk-off = home, bottom 9th+, HR ends the game (`post_bat_score > fld_score`); multi-HR game = max HR per `game_pk`; RHP four-seam top 3 by EV; LHP fastball clips = top 2 by EV among `Fastballs` from LHP; LHP breaking list = all. **Postseason HRs never enter a regular-season curve or table**; the WC homer is a labelled postscript beat.
- **SP-1 spray placement.** Bearing from DR-1 `loc_x/loc_y`; radius = `hit_distance_sc`, so every dot sits at its Statcast distance against the 329–401 ft outline. Validated by the median of `hypot(loc)/hit_distance_sc` (reported, not used).
- **SP-2 missing coordinates.** A HR without `hc_x/hc_y` gets the bearing of the field sector named in its `des` text (LF −36°, LCF −18°, CF 0°, RCF +18°, RF +36°), a hollow marker, and an "approximate" note. No `des` sector → an off-chart chip. Never silently dropped, never imputed from other balls.
- **SP-3 one outline, all parks.** Every HR is drawn on the CBP outline. The caption says so. Nothing on screen may say a road HR "would have been out" at CBP.
- **PM-1 pitch map.** Catcher's view, `plate_x`/`plate_z`; zone rectangle half-width 0.83 ft (house Statcast convention); top/bottom = his 2026 regular-season mean `sz_top`/`sz_bot` (client rule, drawing only, never a classifier). Ball drawn at true scale, diameter **2.9 in = 0.242 ft** (MLB regulation 9–9¼ in circumference). Color = client `pitch_group` (CPG-1).
- **HB-1 HR barrel share** (new, provisional) = barrels / HR, the client's `Barrels/HR`. It is NOT the house `barrel_rate` (barrels / BIP), which ships beside it under its own name.
- **Grade bars (HP-01…HP-07).** "Lowest / shorter than ever / second-lowest" are graded on the exact rank among the five Phillies seasons 2022–26, at the client's displayed precision (EV 0.1 mph, distance 1 ft, share 1%). SUPPORTED = rank matches; PARTLY = matches on one of two legs or within display rounding; NOT SUPPORTED otherwise. HP-06/07 graded on HR counts and EV by hand × group vs 2022–25, every cell printing n; cells under 5 HR print "too few to call".
- **Video defaults** (G10): 1920×1080, 30 fps, dark field in house colors; animation target ≈ 90 s excluding clips.

### 4. We found the traps before the build.
- **CP-1 (new): the client's `cumulative_pa` counts pitches.** `zfig.groupby('game_year').cumcount() + 1` runs over pitch rows: 2026 ends at **3,026 "PA"** instead of **702**. Every line is stretched ≈4.3× and seasons are stretched by their own P/PA, so the lines do not compare like for like.
- **CP-2 (new): HR credit lands on the first pitch of the PA.** The merge on (year, date, game, at-bat) tags every pitch of the HR at-bat; the step rises before the HR pitch. Fixed by CP-1's PA grain.
- **SRC-D (new, conditional): possible 2026 double count.** `ks_pos` ("Phillies Tenure") and `ks26` are concatenated with no de-duplication; if `ks_pos` holds 2026, every 2026 pitch appears twice and the 2026 line doubles. The CSVs are not in the repo, so this is flagged, not graded. The governed build de-duplicates on `PITCH_KEY`.
- **WP-1 (new): raw `delta_home_win_exp` sorts road HRs to the bottom.** The 6/28 HR at Citi Field (WP-1 ≈ +.37, 2nd of the season) has raw dHWE ≈ −.37. The client caught it by eye; the code would not.
- **SP-2 (new): two 2026 HRs have no hit coordinates**, and one is the **max-distance highlight** (4/3 Coors, 460 ft). The other is 9/5 vs ATL (435 ft). "45 dots" needs SP-2.
- **G1 (new): the LHP clip ask conflicts with itself.** The storyboard says "clips … off lefty fastballs"; the code says "look at the two homers he hit on lefty breaking balls". The log has **13** lefty-fastball HRs and **2** lefty breaking-ball HRs. Default: clips are lefty fastballs (storyboard), the two breaking balls are the "compromised" beat; DPO can flip.
- **CPG-1 (inherited):** the client map sends KN to Breaking, the house map to offspeed. 0 of 45 2026 HRs affected.
- **SPR-1 (new): the house log carries a spring HR** (3/22 at NYY) and the WC HR; regular season = 45.
- **ENV-3 (sixth occurrence):** device `/sessions` at 100%. Render stack runs from `/tmp/pyrender`; `TMPDIR=/tmp/piptmp`.

### 5. We build where the RFP says.
Code `dp_uc58_*.py`, `out/dp_uc58_*`, `eda/dp_uc58/` at the **MLB root**; the trail (this BID, `00`–`07`, README) plus copies of the prompt, brief, data package and keyframes in this folder. Inherited kernels are imported by pinned hash, never edited.

## Data position (verified at bid time)
| Check | Result |
|---|---|
| House log | `phils_2026.parquet` sha `be5d313d…` (unchanged since UC57); max `game_date` **2026-10-01** (anchor unchanged) |
| Pre-Phillies | `data/opponents/schwarber.parquet` (11,449 rows; CHC 2015–20, WSH/BOS 2021; max 2021-10-22); 0 duplicate keys |
| Entity lock | MLBAM **656941**, bats L, `phillies_role == 'batting'`; one name; 0 duplicate pitch keys 2022–26 |
| Regular-season HR (log) | 2015 16 · 2016 0 · 2017 30 · 2018 26 · 2019 38 · 2020 11 · 2021 32 · 2022 46 · 2023 47 · 2024 38 · 2025 56 · **2026 45** (CI-1, CI-4 reconcile) |
| 2026 regular season | 3,026 pitches · 702 PA · 45 HR; non-regular rows: S 31 · F 57 pitches; HRs S 1 · F 1 |
| 2026 HR field nulls | `launch_speed` 0 · `hit_distance_sc` 0 · `plate_x/z` 0 · `delta_home_win_exp` 0 · **`hc_x/hc_y` 2** |

## Product types explored
| # | Form | Owns | Bid |
|---|---|---|---|
| P1 | **Claude Design prompt package**: storyboard S1–S8, per-scene direction, transition grammar, brand tokens, embedded governed data (JSON) | the animation itself | **Build (hero)** |
| P2 | **Governed data package**: per-scene CSV/JSON + `headlines.json` + clip list in `resolve_play_ids.py` schema | every number on screen | **Build** |
| P3 | **Technical feasibility brief**: the client's reference Python assessed as the engine (defects, fixes, the governed replacement) | "can this code drive the animation" | **Build** |
| P4 | **Reference keyframes**: one PNG per scene end-state (S1–S7) + the S8 composite, house brand dark | what Claude Design must match; render QA | **Build** |
| P5 | Plotly HTML animatic of S1–S3 (frames + slider) | timing review before Claude Design | **Tier B** |
| P6 | Rendering the MP4 ourselves | | **Not bid**: that is Claude Design's job; the brief says how to capture frames if export is missing |

## Scope tiers
### Tier A (recommended, AWARDED): P1 + P2 + P3 + P4, receipts 00–07.
New KPIs (1): **HB-1**. New rules (provisional): CP-1, WP-1, HL-1, SP-1/SP-2/SP-3, PM-1. Figures: 8 keyframes.
### Tier B: Tier A + P5 animatic (≈ +55k, +7 min).
### Tier C: Lean, P1 + P2 only, no keyframes, brief folded into `04` (≈ −90k, −10 min).

## Deliverables (Tier A)
| # | Deliverable | Where |
|---|---|---|
| 1 | `dp_uc58_claude_design_prompt.md` | MLB root (+ copy here) |
| 2 | `dp_uc58_technical_feasibility_brief.md` | MLB root (+ copy here) |
| 3 | `out/dp_uc58_*` data package (CSV + `dp_uc58_design_data.json` + `headlines.json` + clip list + HP grades + DQ + verification log) · `eda/dp_uc58/` | MLB root (+ copy of the design data and clip list here) |
| 4 | `out/dp_uc58_k*.png` keyframes S1–S8 | MLB root (+ copy here) |
| 5 | `dp_uc58_kernel.py`, `dp_uc58_build.py`, `dp_uc58_build_keyframes.py`, `dp_uc58_build_prompt.py`, `dp_uc58_verification.py` | MLB root |
| 6 | Receipts `00`–`07`, README, this BID | this folder |
| 7 | Contract `uc-pos-023-Kyle Schwarber 2026 HR Animation 20261027.md`, ledger patch `uc_ledger_AI_PATCH_uc-pos-023-schwarber-2026-hr-animation.md` | MLB root (+ copy) |

**Explicitly not bid:** the back-injury and "lost pop" causal questions (parent recap UC) · rendering the MP4 · downloading clips · resolving `play_id`s from the cloud (StatsAPI is outside the egress allowlist; the client's resolver runs locally) · any claim that a road HR would have cleared the CBP wall · postseason or spring rows in any regular-season number.

## Price (Tier A)
**Basis:** UC57 (≈513k across two chats, 35 min build) and the recap set (466k–681k). **Down:** no report, no PDF, no dashboard; one new KPI; the cumulative engine and spray geometry are inherited whole. **Up:** a new consumer (another model) needs a prompt precise enough to animate without asking back; fifteen HP rows; eight keyframes; a feasibility brief on code we didn't write.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, recon, env, profile, carry-ins (**sunk ≈116k, 8 min**) + this BID, `00`, `01` | ~120k | ~22k | 10 |
| T1 Kernel + build (curves, table, spray, pitch maps, highlights, HP grades) + EDA to file | 55k | 18k | 8 |
| T2 Keyframes (8) + brand + render QA | 40k | 14k | 7 |
| T3 Claude Design prompt + feasibility brief | 25k | 18k | 6 |
| T4 Verification harness | 18k | 7k | 4 |
| T5 Governance 00–07, README, contract, ledger patch | 22k | 16k | 6 |
| D Defect discovery | 8k | 3k | 2 |
| Contingency 5% (unsunk) | 9k | 4k | 2 |
| **BID** | **~297k** | **~102k** | **~45 min** |

**Total ≈ 400k tokens, ≈ 45 minutes.** House list convention as in the UC57 BID ($10/M in, $50/M out): ≈ **$8.07**, band $6.85–9.30 (±15%). Cowork bills subscription usage; read this as API-equivalent value.

### Competitive position
A rival agentic org without this repo would have to rediscover that the client's x-axis counts pitches (CP-1), that raw dHWE hides road HRs (WP-1), that the longest HR has no spray coordinates (SP-2), and the hc → feet convention the house proved in UC38. It would hand Claude Design the client's notebook numbers, so the video would ship lines stretched 4.3×. We estimate that bid at **~0.55–0.75M tokens, 55–70 min**, with no receipts and no graded claims.

Our differentiators: highlights chosen by rules fixed before looking; every on-screen number keyed to a receipt row; the client's notebook graded, never overwritten; a clip list that drops into his own downloader; bid-vs-actual history (UC48–UC57 within −28% to +9%).

## Assumptions, exclusions, carry-ins
- Regular season for every curve, table, rate and map. Spring excluded and counted (SPR-1); the WC HR is a labelled postscript.
- Entity locked by MLBAM 656941 + batting role (house log) and by id in the opponent file; the name is used only to reproduce the client frame.
- Carry-ins CI-1…CI-4 are labelled at every use and never computed on.
- The client's CSV paths (`c:\Users\kshort4\Downloads\…`) are not reachable; the client frame is reproduced from the house log with the client's code verbatim.
