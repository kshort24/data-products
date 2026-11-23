# BID: Alec Bohm, 2026 recap → Phillies career retrospective (2020–26), PDF + interactive dashboard

**Status:** FILED 2026-11-22 13:30 ET · **AWARDED by RFP rule (treat as winner)** · delivery and actuals in `07` §5.
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments) · **Human DPO:** Kellen Short
**ID reservation:** UC **#67** · contract `uc-pos-026` · build `dp_uc67` · folder `uc-pos-026-bohm-career-retrospective-001`
**Collision check (13:29 ET):** the UC66 ledger patch (uc-pps-042, 2026-11-20) reserves "next: UC #67 / dp_uc67 · pos `uc-pos-026`". No `dp_uc67*`
in the MLB root or `out/`; no `uc-pos-026` folder in the control plane. Repo ledger tail is stale; UC52–UC66 patches are pending paste.

## The ask
1. **Continue uc-pos-013** (UC #38, `dp_uc37`, delivered 2026-08-24 on data through 2026-08-22): did the second-half turnaround hold to the end of 2026?
2. **Contextualize 2026 against his Phillies career**, then a **career retrospective** written on the client's assumption that he will not return.
3. **The client's thread** (notebook comments): line drives, platoon (RHP), RHP breaking balls, luck. If the line-drive deficiency is a good
   angle, ship the LD spray chart **in the house field-outline style** (wall + foul lines + infield diamond: `dp_uc61` F3 / K58 `wall_outline`).
4. **Highlight run creation and RISP skill**, including the client's game-winning-runs cell (videos are out of scope; the cell is in scope).
5. Standing instructions: build in the MLB data plane; receipts `00`–`07` here; scouting-report skill for voice; bid treated as won.

### Client questions → chapters
| Q | Question | Primary evidence |
|---|---|---|
| Q1 | Did the turnaround hold? | three 2026 windows (pre-break / UC37 post-break to 8/22 / **8/23–end, unseen**), **PR-1 H-F** |
| Q2 | Where does 2026 sit in his career and among Phillies hitters? | season panel 2020–26 (regular season, id-locked), KP-1 ranks on house hitter-seasons 2015–26 |
| Q3 | Was the problem line drives? | **PR-1 H-LD** + pool relevance gate (LD share → wOBA); LD spray chart with field outline |
| Q4 | Was the problem righties, and righty spin? | **PR-1 H-R**: platoon × pitch group, results vs process (xwOBA), xBA>.500 conversion |
| Q5 | Run creation and RISP | runs on watch (K48 `runs_created`), RISP splits, **GW-1** deciding runs, **RS-1** repeatability rule |
| Q6 | The Phillies career, closed out | seven seasons, ranks, profile drift (whiff ↓, pull-air ↓), carry-ins for the departure |

## Claims graded (HP rows; bars set here, before any grade is computed)
| HP | Claim (source) | Bar |
|---|---|---|
| HP-01 | Game-winning cell reproduces (client) | client operators on a reconstructed `gms`; 2026 row count = GW-1 2026 count ± mechanism differences, each explained |
| HP-02 | "Bohm did not hit enough line drives in 2026" (client) | = H-LD verdict SUPPORTED/STRONG |
| HP-03 | "Solid against lefties but struggled against righties too much in 2026" (client) | vs LHP 2026 wOBA ≥ his 2020–25 vs-LHP pooled − .015 **and** vs RHP 2026 is his lowest or 2nd-lowest season (≥ 100 PA) |
| HP-04 | vs RHP: "hard-hit consistent, barrel mostly fine, LD sank a bit" (client) | hard-hit and barrel inside his 2020–25 vs-RHP season range; LD below his 2020–25 vs-RHP pooled rate |
| HP-05 | vs RHP: "more ground balls, but not a ton more" (client) | 2026 GB% vs RHP minus 2020–25 pooled in (0, +4.0 pts] |
| HP-06 | "He stopped being able to hit righty breaking balls" (client) | 2026 wOBA vs RHP breaking is his lowest season (≥ 50 PA in the cell) |
| HP-07 | vs RHP breaking 2026: "hard-hit highest since 2020, barrel just under 6%, LD in line" (client) | three legs: HH rank 1 of 2021–26; barrel 5.0–6.0%; LD within ±3 pts of 2020–25 pooled |
| HP-08 | "Not an overtly unlucky year: 76% of BIP with xBA > .500 became hits" vs RHP breaking (client) | reproduce 76% ± 1 pt; then rank 2026 among his seasons on the same rule |
| HP-09 | uc-pos-013 §6 career table (parent UC, our own) | each PA count equals the governed regular-season count; a miss is graded as a parent defect, not overwritten |

## Pre-registration (filed 13:30 ET)
**Disclosure.** At T0 the organization saw: house hitter-season wOBA and PA by season (2020 .381 … 2026 .307, 632 PA) from a probe of the
KP-1 pool, the MLB.com / NBC Sports season line (.249/.315/.383, 15 HR, 155 G), and the uc-pos-013 receipts through 2026-08-22. Nothing after
2026-08-22, no platoon, pitch-group, line-drive, RISP or game-winning number has been computed in this session. Signatures built on those are *unseen*.
The client's own notebook comments (HP-02..HP-08) were written after the client saw their numbers; their grades are labelled *client-seen*.

**PR-1 ledger.** Scored with the inherited PA-1 rule (`K48.signature_verdict` / `strength_from_signatures`). Regular season, id-locked (MLBAM 664761).

| Family | # | Signature | Before → After | Dir | Bar | Status |
|---|---|---|---|---|---|---|
| **H-F "the turnaround faded"** | F1 | wOBA | UC37 post-break (7/16–8/22) → **8/23–end** | − | .048 (half the UC37 jump) | unseen |
| | F2 | hard-hit rate | same | − | 3.0 pts | unseen |
| | F3 | in-zone whiff | same | + | 2.6 pts | unseen |
| | F4 | xwOBAcon | same | − | .045 | unseen |
| | F5 | wOBA vs breaking balls | same | − | .076 | unseen |
| **H-LD "the line drives went missing"** | L1 | LD share of BIP | 2020–25 pooled → 2026 | − | 2.0 pts | client-seen |
| | L2 | LD share vs RHP | same | − | 2.0 pts | client-seen |
| | L3 | LD share vs RHP breaking | same | − | 3.0 pts | unseen |
| **H-R "righties, not lefties"** | R1 | wOBA vs RHP | 2020–25 pooled → 2026 | − | .025 | client-seen |
| | R2 | wOBA vs RHP breaking | same | − | .040 | client-seen |
| | R3 | xwOBA vs RHP | same | − | .025 | unseen |

**Gate G-LD (pool relevance, unseen):** across Phillies hitter-seasons 2015–26 with ≥ 200 PA, OLS of wOBA on LD share has slope > 0 and R² ≥ .05.
**Call rules (registered):** H-F STRONG/SUPPORTED → "it faded"; UNSUPPORTED with ≤ 1 CONTRA → "it held"; MIXED → "it held in the contact, not the results"
(or the reverse, named by which signatures moved). **The LD angle is "good" iff H-LD is SUPPORTED/STRONG and G-LD passes**; then the spray chart leads
§3 of the report. Otherwise the spray chart ships as context in the dashboard and the report says the angle did not hold. H-R: R1/R2 PRESENT with R3
ABSENT/WEAK → "results, not process" (luck); R3 PRESENT → "the contact got worse".
**RS-1 (RISP repeatability, unseen):** "a RISP hitter" iff his wOBA with RISP exceeds his wOBA without RISP in ≥ 5 of 7 seasons (2020 counted,
labelled). Fewer → the RISP line is reported as results, not as a skill.
A bar changed after publication is a breaking change (`version-controller`).

**GW-1 (new, provisional): deciding run.** In a Phillies win, the plate appearance during which the Phillies' score first passed the opponent's
final total (the run that was never answered). Credited to the batter at the plate whatever the mechanism; mechanism printed (hit, HR, sac fly,
walk/HBP, out, error, wild pitch/passed ball). Not RBI: RBI is not in the log and is a carry-in only. Spec in `03` §2.

## Why this shop wins
1. **Inherit, don't re-derive.** `dp_uc61_kernel` (23 pins: K60 → K58 → K57 → K54/K40 chain, `recap_viz`): `nresults_unrounded` (WB-2),
   XW-1, `cell_panel`, CR-1 batted-ball profile, DR-1 direction, PA-L1 coordinates, K46 pull-air, KP-1 percentile + house hitter-seasons,
   K48 `runs_created` (runs on watch) and PA-1, K58 `wall_outline` + `CBP_DIMS` and the `dp_uc61` F3 field drawing the client asked for.
2. **We grade our own parent.** uc-pos-013 is a house product; HP-09 checks its career table, and PR-1 H-F scores its headline out of sample.
3. **Pre-registered.** Whether the LD angle earns the spray chart is decided by a filed rule, not by the narrator.
4. **One narrative module** feeds report and dashboard, so the PDF and the page cannot disagree.

## Scope
**In:** kernel, build, receipts, EDA to file, HP grades, PR-1, GW-1, RS-1, LD spray chart (field outline), 8–10 figures (V1–V7 audited), PDF
(≤ 10 pp), dashboard (repo copy), harness, `00`–`07`, README, contract, ledger patch.
**Out:** the videos (game-winning and helmet-spike compilations: client says not analysis), defense (no fielding data in the plane), contract
or market-value advice (carry-ins only), WAR/OPS+ (carry-ins, never computed), the client's notebook (not edited).

## Price
| Phase | Departments | Tokens | Minutes |
|---|---|---|---|
| T0 recon (2 planes, K61 chain, parent UC37, skill), env, carry-ins, BID, `01` | strategy & intake | 85k | 12 |
| T1 kernel, build, HP reproduction, GW-1, EDA, receipts | engineering | 55k | 10 |
| T2 figures + field-outline spray + V1–V7 audit + render QA | design | 50k | 10 |
| T3 narrative module + dashboard | consumer success | 30k | 7 |
| T4 report + PDF | analytics-enabler | 20k | 5 |
| T5 harness + DQ + certification | quality | 20k | 5 |
| T6 `02`–`07`, README, contract, ledger patch | governance + platform | 40k | 8 |
| D defect discovery (always priced) | all | 10k | 3 |
| **Total** | | **≈310k** | **≈60 min** |

**Calibration.** UC62 (pitcher career recap, PDF + dashboard + Artifact) bid 360k / 61 min and came in at ≈240k / 25 min; its own rule for the next
career recap was 250k / 40 min. This bid adds a parent-UC continuation (three-window H-F), a new KPI (GW-1) needing a reconstructed game table,
and a field-outline spray chart, and drops the Artifact (not requested). T0 is priced at what two-plane recon has actually cost.

**Competitive position.** A shop without this kernel re-derives wOBA weights by season, the PA and RISP rules, xwOBA basis, the hitter pool and
the field geometry (≈ 150k more), and would inherit uc-pos-013's career table as written (HP-09 suspects postseason PA in it: probe shows 631
regular-season PA in 2022 vs 695 printed). It would also score the client's game-winning cell at pitch grain, crediting runs that scored on a
wild pitch in the middle of a plate appearance the same as a base hit.
