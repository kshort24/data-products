# BID: Aaron Nola 2026 season recap + career pitch-sequencing engine — report (PDF), dashboard (HTML), governed package

**Status:** FILED 2026-11-16 22:47 ET · **AWARDED by RFP rule (treat as winner) — acceptance below** · **DELIVERED ≈23:35 ET, READY-CONDITIONAL (C1–C4), harness 43/43.** Actuals ≈300k / ≈62 min vs ≈545k / ≈68 min bid (`07` §5).
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments) · **Human DPO:** Kellen Short
**ID reservation:** UC **#64** · contract `uc-pps-040` · build `dp_uc64` · folder `uc-pps-040-nola-2026-recap-sequencing-001`
**Collision check (22:44 ET):** UC63 ledger patch reserves "next: UC #64 / dp_uc64 · pps `uc-pps-040`". No `dp_uc64*` in the MLB root or `out/`;
no `uc-pps-040` folder in the control plane before this one. Repo ledger tail still pending the UC52–UC63 pastes.

## The ask
1. Recap Aaron Nola's 2026 (RHP, MLBAM **605400**) as a **holistic season arc**, leveraging the five prior Nola-touching products
   (`uc-pps-008` dp_uc8 Nationals · `uc-pps-014` dp_uc15 Royals · `uc-pps-021` dp_uc25 Dodgers · `uc-pos-012` dp_uc35 Alcántara ·
   `uc-pps-027` dp_uc38 Nola–Stubbs battery · and the Nola rows of `uc-cat-002` dp_uc59). "Don't necessarily tie out any narratives":
   no HP claim-grading ledger this time; prior products are *re-read at season's end*, not re-litigated.
2. **New capability: pitch sequencing.** How he sequences vs LHB and RHB; which sequences get outs, strikeouts and poor contact —
   "the sequences that maximize run prevention"; differences by batterymate; drift over his career ("used to rely on a sequence in his younger years").
3. Deliverables: **PDF report**, **interactive dashboard**, **bid + acceptance + `00`–`07`**, other additions at the org's discretion.

### DPO rulings taken at intake (binding; `intake/client_prompt_2026-11-16.md`)
Q-A credit rule = **setup lift + terminal endings** · Q-B weak contact = **Savant LSA 1–3** (PC-1) · Q-C windows = **career-wide, every length**, 2026 as highlight.

## Frame & entity lock
House log `data/phillies/phils_2015..2026.parquet`, `phillies_role == 'pitching'`, `pitcher == 605400` (name frame == id frame asserted, O-26;
the Nolan Hoffman 676510 contamination is the canonical failure). Regular season (`R`) for every KPI; 2026 Wild Card Game 3 (38 pitches) reported as a
separate line. Anchor = house max game_date 2026-10-01 (pinned). T0 profile: 30,079 regular-season pitches, 8,003 PA over 2015–26; 2026 = 2,955 pitches / 746 PA.

## New governed objects (PROVISIONAL; specs here, before code; kernel `dp_uc64_kernel.py` Section C)
| ID | Object | Spec (plain language → formula) |
|---|---|---|
| **SQ-0** | `pitch_sequence` (client function) | Transcribed **verbatim** from the client prompt as Section B; applied *after* PT-H. Output column `seq` = pitch types of the PA joined by `-`. |
| **PT-H** | pitch-type harmonization | `CU → KC` (Nola's curveball is tagged CU 2015–16, KC 2017+: one pitch, two labels). `IN`, `PO`, null → token `XX`; any window containing `XX` is dropped from SQ-1/2/3 (counted in DQ). All other tags as recorded (incl. 2026's `SL`, kept and flagged). |
| **SQ-1** | sequence window | Every contiguous run of k pitches inside one PA, k ∈ {2,3,4}, ordered by `pitch_number`. Grain: (game_pk, at_bat_number, end pitch). Carries stand, era, catcher (`fielder_2` of the end pitch), count *before* the end pitch. |
| **SQ-2** | setup lift (headline) | For a window ending on pitch *j* of type *t* in count *c* to stand *s*: `lift_j = (−delta_run_exp_j) − b(t, c, s, E)` where *b* = Nola's mean pitcher-POV run value of pitch type *t* in count *c* to stand *s* within the same era *E* (career pool when E = all). Sequence lift = 100 × mean(lift_j) = **runs saved per 100 follow-up pitches beyond what that pitch earns in that count anyway**. Companion lifts on the same baseline rule: **CSW lift** (called strike or whiff, house CSW) and **whiff/swing**. Isolates the setup from pitch quality and count. |
| **SQ-3** | terminal ending | The last k pitches of a PA (PA length ≥ k), k ∈ {2,3,4}, scored on the PA: **out rate** (OUT-1), **K rate**, **PC-1 share** of tracked BIP, **XW-1 xwOBA** per PA, **ending RV** = −100 × Σ delta_run_exp over the k pitches per PA. Full PA sequences (SQ-0 `seq`) reported for PAs of length ≤ 3. |
| **PC-1** | poor contact (DPO-defined, Q-B) | BIP (`type == 'X'`) with `launch_speed_angle ∈ {1,2,3}` (Savant Weak / Topped / Under). Denominator = BIP with non-null LSA; untracked BIP counted separately. |
| **OUT-1** | out PA | PA whose terminal event records ≥ 1 out under K49 OU-1 `outs_recorded` (K, field outs, DPs, FC-with-out, sac). |
| **SQ-4** | stability | Rank only windows with n ≥ **50** (career) / ≥ **30** (stand × era, catcher cells). Ranked value = shrunk lift `lift × n/(n+100)`. 90% interval = PA-cluster bootstrap (1,000 reps, seed 64). |
| **SQ-5** | era drift / "fade" | Eras (pre-registered): **E1 Young 2015–19** (age 22–26, pre-cutter) · **E2 2020–23** (cutter from 2021) · **E3 Recent 2025–26** (the client's "last couple years"). **2024 sits in neither comparison window** on purpose (G6: scan it). A sequence **FADED** if lift(E1) − lift(E3) ≥ **1.5 runs/100**, both cells n ≥ 30, and the bootstrap 90% CI of the difference excludes 0; **HELD** if |diff| < 1.5 or CI includes 0; **GREW** symmetric. Baselines are era-internal, so a fade is a *sequencing* fade, not a stuff decline. G6 sensitivity: E1′ = 2017–19, E3′ = 2024–26. |
| **SQ-6** | batterymate book | Pair-usage distribution (k=2, per stand) by catcher (`fielder_2`, ≥ 8 Nola starts in the scope). Distance = Jensen–Shannon divergence vs a permutation null (catcher labels shuffled across starts **within season**, 500 reps). p < 0.05 = **DISTINCT BOOK**, else **SAME BOOK**. Lift by catcher for the top pairs is descriptive. Catcher names resolved from Phillies batting-role rows by batter id (EN-3 discipline). Guardrail G4 carried: Statcast cannot attribute a pitch call. |
| **PI-1** (stretch S-1) | predictability | Per pitcher-season: `H(next | prev, stand)` and information gain `IG = H(next | stand) − H(next | prev, stand)`, in bits, over within-PA pairs (PT-H applied to Nola; raw tags for others). Context = `phi_sp_seasons` (SD-1, ≥ 2,000 pitches). |

### Inherited, not re-derived (K63 → K62 → K53 → … → K44, sha-pinned import)
`nresults`, `whiff_rate`, `chase_rate`, `putaway_rate`, `fpsr`, `hard_hit_rate`, `pitch_mix`, CSW (K53), `rv100` / `xwobacon` / `count_state` /
`arsenal_table` / `house_percentile` (K48), `game_score` GS-1 / `outs_recorded` OU-1 / `context_frame` CX-1 (K49), XW-1 (K50), BR-1 (K51),
`starts_by_game` (K52), `recap_viz` SD-3 (V1–V7 audit, `asb_2026` era registry SD-2, `phi_sp_seasons` SD-1).

## Season arc (Part I) — what gets built
- 2026 line vs his career and vs `phi_sp_seasons` (KP-1 percentiles); reconciliation REC-1 of log K / BB / outs to the public line (CI-1).
- Start-by-start GS-1 and XW-1 with the SD-2 `asb_2026` halves and calendar months (descriptive; no breakpoint claims).
- Arsenal 2026 vs 2025 vs 2018 (peak): usage, velo, shape, whiff, RV/100.
- **Prior-products re-read** (PR-R): the four `uc-pps-021` LHB tripwires and the `uc-pps-027` approach metrics at season's end, first vs second half.
- Catcher split 2026 (inherits the `uc-pps-027` / `uc-cat-002` frame).

### Carry-ins (public; display + reconciliation only)
CI-1 2026 line: 33 GS, 175.1 IP, 7-12, 4.67 ERA, 177 K, 59 BB, 1.35 WHIP (CBS Sports / ESPN) · CI-2 5.86 ERA through 13 starts (MLB.com, June) ·
CI-3 2.93 ERA over 11 starts from August 1 (CBS Sports) · CI-4 Wild Card Game 3 start at ATL, 1.2 IP, loss (CBS Sports).

## Stretch (posed by the org)
**S-1 Predictability (PI-1):** is Nola harder or easier to guess pitch-to-pitch than he used to be, and than other Phillies starters? 20k / 3 min.
Offered, not built: S-2 count-conditioned Markov simulator ("what should he throw next") — would need the `machine-learning-engineer` and a validation design.

## Why this shop wins
1. **The house already holds the Nola file.** Five prior Nola products and the battery study (TR-1 / G4 / G7) mean the batterymate question starts from
   a known answer ("Nola's change, not Stubbs's") instead of a blank page — and the org knows *not* to claim pitch-call attribution.
2. **Sequencing done as a counterfactual, not a leaderboard.** Raw "FF-KC gets outs" tables reward good pitches and pitcher-friendly counts. SQ-2 credits only
   what the setup adds over the same pitch in the same count. A shop without that baseline ranks the knuckle curve, not the sequence.
3. **The CU→KC relabel and the cutter's 2021 arrival are handled before the era comparison**, so "faded" cannot be a tagging artifact or an arsenal change.
4. **Inherit, don't re-derive:** ~14 locked KPI functions by pinned import; the wOBA weights and XW-1 come for free.

## Scope
**In:** kernel, build + receipts, figures (V1–V7), report `.md` + `.pdf`, dashboard `.html` (+ Artifact), harness, `00`–`07`, README, contract, ledger patch, S-1.
**Out:** pitch-call attribution (not in Statcast, G4); tunneling / release-point sequencing physics; postseason sequencing (38 pitches); a predictive next-pitch model (S-2).

## Price
| Phase | Departments | Tokens | Minutes |
|---|---|---|---|
| T0 recon (both planes), 5 prior Nola products, sequence profile, intake Q&A, carry-ins, BID | strategy & intake | 140k | 14 |
| T1 kernel (SQ family), build, receipts, bootstrap + permutation | engineering | 120k | 16 |
| T2 figures (V1–V7), render QA | design | 60k | 8 |
| T3 report md + PDF | analytics-enabler | 55k | 7 |
| T4 dashboard + Artifact | consumer success | 50k | 7 |
| T5 independent harness, DQ, certification | quality | 45k | 6 |
| T6 `00`–`07`, README, contract, ledger patch | governance + platform | 55k | 7 |
| **Base total** | | **≈525k** | **≈65 min** |
| S-1 stretch | engineering + design | 20k | 3 |
| **With stretch** | | **≈545k** | **≈68 min** |

**Calibration:** UC63 (reliever recap, new subject) actual ≈265k / 36 min; UC59 (catcher corps, three subjects + new function family) actual ≈542k / 87 min.
This RFP is a starter recap (≈9× McFarlane's pitch count) plus a new KPI family with resampling, so it prices between them, nearer UC59.
**Competitive position:** a shop without the kernel re-derives ~14 KPI functions (≈150k), would rank pitches instead of sequences, and would re-open the
battery question the house already answered.

---

## Award & acceptance
| Field | Value |
|---|---|
| RFP | "Aaron Nola 2026 season analysis + pitch sequencing" (`intake/client_prompt_2026-11-16.md`) |
| Award | **WON** — per the RFP's own rule ("consider the bid a winner for the RFP and proceed with the work") |
| Accepted by | `data-product-owner` on behalf of the org, 2026-11-16 22:48 ET; human DPO ratification pending (Kellen Short) |
| Accepted scope | Base (≈525k / ≈65 min) **+ S-1** (≈20k / ≈3 min) |
| Acceptance criteria | (1) every number in report and dashboard traces to an `out/dp_uc64_*` receipt computed this session; (2) entity lock + REC-1 reconcile; (3) SQ bars above unchanged after first compute (change = breaking, `version-controller`); (4) harness all PASS; (5) V1–V7 on every figure; (6) certification verdict in `05`; (7) bid vs actual in `07` |
