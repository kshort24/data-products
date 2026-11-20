# BID: Chase Shugart 2026 season recap — report (PDF), dashboard (HTML), PNG figure set, redesigned pitcher-recap visuals

**Status:** FILED 2026-11-20 14:12 ET · **AWARDED by RFP rule (treat as winner) — acceptance below.** **DELIVERED ≈14:42 ET, READY-CONDITIONAL (C1–C4), harness 34/34.** Actuals ≈325k / ≈43 min vs ≈410k / ≈64 min bid (`07` §5).
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments) · **Human DPO:** Kellen Short
**ID reservation:** UC **#66** · contract `uc-pps-042` · build `dp_uc66` · folder `uc-pps-042-shugart-2026-recap-001`
**Collision check (14:08 ET):** UC65 ledger patch reserves "next: UC #66 / dp_uc66 · pps `uc-pps-042`". No `dp_uc66*` in the MLB root or `out/`;
no `uc-pps-042` folder in the control plane before this one. UC52–UC65 ledger patches still pending paste.

## The ask
1. Recap Chase Shugart's 2026 (RHP, MLBAM **663767**; acquired from PIT 2026-01-13). High level first, then dimensioned splits, then the
   underlying indicators that could be driving the outcomes.
2. **The client's scratch work is the starting hypothesis set.** Every claim in it is graded on a bar filed here, before compute.
3. **Visual redesign.** The client is "not thrilled" with the last pitcher recaps' visuals. Required: pitch plot, pitch map, a better
   cumulative pitch-usage view than by-month, cumulative wOBA/OPS if appropriate. PNGs of every graph.
4. **Comparison sets are delegated to the org** (righty relievers? middle relievers? all RHP? his own history?). The org decides and defends it.
5. Deliverables: PDF report, interactive HTML, PNGs, receipts `00`–`07` here, bid + acceptance. Build in the MLB data plane, house standards.

## T0 findings that shape the price (recon only; no KPI computed)
- **Entity lock:** `pitcher == 663767`; name filter `'Shugart, Chase'` returns the same 944 rows (O-26 clean).
- **The client frame carries spring training.** House `pps` keeps all game types; Shugart's 944 = **871 regular season + 73 spring (S)**,
  no postseason. The governed frame is regular season (871). The client frame is reconciled and disclosed, never graded on (FR-1).
- **No usable own history in the plane.** Outside 2026 he appears only as fragments: 77 MLB pitches in 2025 (vs PHI in `phils_2025`, plus
  slices of opponent files), 115 AAA pitches in `lhvp26` (2026). Own-history comparison is NOT OBSERVABLE at the house standard; AAA is a
  supporting tier (usage, velo, counts) and never blended.
- **Device render stack:** the device session disk is full (`/sessions` 100%); `pip install -r requirements-render.txt` fails. Pinned stack
  installed to `/tmp/pylib` and put on `PYTHONPATH` (RN-3, disclosed in `04`).

## Comparison sets — the org's decision (the client delegated it)
| Set | Definition | Used for | Why |
|---|---|---|---|
| **CS-A** `phi_rhp_relief_seasons` (new, DRAFT; mirrors registered `phi_lhp_relief_seasons`) | Phillies pitcher-seasons, regular season 2015–26, `p_throws == 'R'`, CX-1 (≥ 150 pitches), RP-1 reliever (starts ≤ 20% of games) | every season-level percentile; F1 | Same handedness and role. A RHP reliever's platoon, K and contact profile is not comparable to a starter's (times through the order, pitch count) |
| **CS-B** `phi_bullpen_2026` | 2026 Phillies relievers, either hand, RP-1, ≥ 150 pitches; named | role / leverage (HP-12), labelled ranks | "Where does he sit in *this* bullpen" is the middle-relief question |
| **CS-C** `phi_rhp_pitch_stand_seasons` | CS-A pitchers' pitch type × batter hand × season cells, ≥ 50 pitches of that type to that hand | pitch-level platoon context (HP-04, HP-06) | The client's sinker-vs-LHB claim is "atypical" — atypical needs a population of RHP sinkers vs LHB |
| CS-D own history | — | **not used** (NOT OBSERVABLE: 77 fragmentary MLB pitches 2025) | Disclosed, no comparison drawn. Public 2024–25 lines are not carried in |
| Rejected | all Phillies RHP (starters + relievers); league RHP relievers | — | All-RHP mixes roles. `nphl` is a curated opponent set, not a sampling frame — a league percentile from it would be biased |

"Middle reliever" is a role, not a population cut: it is answered inside CS-B by entry state (HP-12), not by filtering the context pool.

## Client claims graded (HP rows; bars filed 14:12 ET before any KPI is computed)
All grades on the regular-season frame (871 pitches). SUPPORTED / PARTLY / NOT. Percentiles = KP-1 `house_percentile` (share of pool strictly worse).
| HP | Claim (client's words) | Bar |
|---|---|---|
| HP-01 | "Mostly even leaning slightly reverse platoon splits" | gap = wOBA vs RHB − wOBA vs LHB. SUPPORTED if gap in (0, .040] (righties slightly better = reverse for a RHP) and xwOBA gap has the same sign; PARTLY if \|gap\| ≤ .040 with one sign disagreeing; NOT otherwise. Context: CS-A median gap (sides ≥ 60 PA) |
| HP-02 | "a solid year overall" | wOBA and xwOBA percentiles in CS-A: both ≥ 50 SUPPORTED, one PARTLY, neither NOT |
| HP-03 | LHB: "struck out more, walked less, and whiffed more", "did more damage when they connected"; RHB: "hit him more frequently and drew more walks but did not slug as much" | 6 legs: K% L>R, BB% L<R, whiff% L>R, SLG L>R, BA R>L, OBP R>L. 6/6 SUPPORTED, 4–5 PARTLY, else NOT |
| HP-04 | "cutter is a problem against right-handed batters"; drives success vs LHB | FC wOBA vs RHB > his overall wOBA vs RHB **and** FC RV/100 vs RHB < 0; FC wOBA vs LHB < overall vs LHB **and** RV/100 vs LHB > 0. Both sides SUPPORTED, one PARTLY |
| HP-05 | the cutter lets him "own the inside part of the plate to left-handed batters" | share of FC to LHB at `plate_x ≥ +0.277 ft` (inner third and in, catcher's view): ≥ 50% SUPPORTED, 35–50% PARTLY |
| HP-06 | "Fascinating how effective his SI was against lefties. That is atypical." | SI × LHB wOBA percentile in CS-C (lower is better): ≥ 75 SUPPORTED, 50–75 PARTLY |
| HP-07 | "a majority of his strikeouts came on his sinker" | SI share of strikeout pitches ≥ 50% SUPPORTED; plurality PARTLY |
| HP-08 | "June was bad and he likely lost some command" | June wOBA highest of months with ≥ 15 PA **and** (June BB% highest or June zone% lowest). Both legs SUPPORTED, one PARTLY |
| HP-09 | "His Cutter Usage actually took off at the end of the season"; "He backed off his Sweeper" to RHB; "abandoning his sweeper at the end of the year did coincide with a strong finish" | 3 legs on the final calendar month he pitched vs everything before it: FC share ≥ 1.5×; ST share vs RHB ≤ 0.5×; final-month wOBA < season wOBA. 3/3 SUPPORTED, 2 PARTLY |
| HP-10 | ".430 SLG allowed … Fairly average, maybe a touch high" | REC: which frame prints .430 (±.0015). Grade: SLG percentile in CS-A 30–55 SUPPORTED, 15–30 or 55–70 PARTLY |
| HP-11 | "His 10% barrel rate is high" | REC ±0.5 pt; barrel% percentile ≤ 25 SUPPORTED, 25–40 PARTLY |
| HP-12 | "a middle reliever with the occasional flex into higher-leverage situations" | LC-1 (K63 FN-1 late-close: entered 7th+ with Phillies margin −1..+3) share of RS outings in [15%, 45%] **and** below CS-B's top-quartile LC share. Both SUPPORTED, one PARTLY |
| HP-13 | "he should focus on being sinker/sweeper to righties" | a recommendation — **not graded**. Evidence table: RV/100, wOBA, whiff by pitch vs RHB with n, and what the sweeper did when thrown |

## New governed objects (provisional; specs in `03` §2 before code)
- **FR-1** client-frame reconciliation (all game types vs regular season), disclosed on page 1.
- **CS-A / CS-B / CS-C** comparison sets above (CS-A proposed for `data/_schema/comparison_sets.json`, DRAFT).
- **CU-1** cumulative pitch usage: running share of each pitch type by pitch of season, faceted by batter hand, regular season;
  plotted against appearance number with stint boundaries marked (V1 cumulative exception).
- **CW-1** cumulative wOBA and xwOBA against by PA (house `cumulative_metric.py`, endpoints reconciled to K44 `nresults` / XW-1),
  faceted by batter hand, CS-A median as reference.
- **IN-1** inner-third share (HP-05). **LC-1** late-close share (K63 FN-1 definition reused, not changed).
- **VZ-1…VZ-6** recap visual rules added on top of V1–V7 (the redesign; `03` §3): finding-as-title; independent scales per metric
  (no mixed-scale rates on one axis); "better" direction normalized and labelled; no in-plot labels that can collide; contrast-checked pitch
  palette; pitch maps as location densities by pitch × hand, not mean-location bubbles.

## Stretch (posed by the org — S-1, priced separately, built only if T1–T5 land inside the bid)
**S-1 Command by stint.** He was optioned and recalled several times (public transactions, carry-in). The client's thesis is "keeping his
command consistent". S-1 cuts the season by MLB stint (from the log's appearance gaps, cross-checked to the transaction carry-ins) and shows
zone%, BB%, first-pitch strike% and wOBA per stint. Cost 20k / 4 min.
(Offered, not built: S-2 a 2027 role projection — needs the machine-learning-engineer; S-3 a stuff model — none in the plane.)

## Why this shop wins
1. **Inherit, don't re-derive.** K64 → K63 → … → K44 by sha-pinned import: `nresults`, `whiff_rate`, `chase_rate`, `putaway_rate`, `fpsr`,
   `hard_hit_rate`, `pitch_mix`, BR-1, XW-1, KP-1, CX-1, RP-1, `rv100`, `recap_viz` V1–V7, `cumulative_metric`. The client's notebook functions
   are the K44 Section A transcriptions — same numbers.
2. **We caught the frame problem before the bid.** 73 spring-training pitches sit inside the client's `pps`; a shop that ran his cells as
   written would publish a blended season line.
3. **We answer the visual complaint with rules, not taste.** The last recaps put BB% and barrel% on the same 0–60 axis as K%, bubbled
   mean pitch locations (a 0.3-ft average says nothing about where a pitch lives), and let labels collide. VZ-1…VZ-6 are machine-checked
   where possible and eyeball-QA'd where not.

## Scope
**In:** kernel, build + receipts, HP grades, figures F1–F9 (+ S-1), PNGs, report `.md` + `.pdf`, dashboard `.html`, harness, `00`–`07`,
README, contract, ledger patch. **Out:** postseason (none for him); stuff model; 2027 projection.

## Price
| Phase | Departments | Tokens | Minutes |
|---|---|---|---|
| T0 recon (both planes, 3 prior recaps' visuals), carry-ins (web), frame + history profile, comparison-set decision, BID | strategy & intake | 120k | 14 |
| T1 kernel, build, receipts, HP + DQ | engineering | 70k | 10 |
| T2 figures F1–F9 redesigned (VZ rules), V1–V7 audit, two eyeball-QA rounds | design | 75k | 14 |
| T3 report md + PDF | analytics-enabler | 35k | 6 |
| T4 dashboard | consumer success | 30k | 5 |
| T5 harness, certification | quality | 25k | 5 |
| T6 `00`–`07`, README, contract, ledger patch | governance + platform | 35k | 6 |
| **Base total** | | **≈390k** | **≈60 min** |
| S-1 stretch | engineering + design | 20k | 4 |
| **With stretch** | | **≈410k** | **≈64 min** |

**Calibration:** UC63 (RHP reliever recap, PDF + dashboard + slides) actual ≈265k / 36 min; UC64 actual ≈300k / 60 min. This RFP drops
slides but adds a full visual redesign (new figure family, extra QA round), two cumulative views, a comparison-set decision and a device
render-env workaround: ≈1.45× UC63's actual.

**Competitive position:** a shop without this kernel re-derives the KPI functions and wOBA weights (≈150k more), would run the client's
`pps` with spring training inside it, and would pick "all RHP" as context because it is the biggest pool.

---

## Award & acceptance
| Field | Value |
|---|---|
| RFP | "Chase Shugart 2026 Season Recap" (`intake/client_prompt_2026-11-20.md`) |
| Award | **WON** — per the RFP's own rule ("consider the bid a winner for the RFP and proceed with the work") |
| Accepted by | `data-product-owner` on behalf of the org, 2026-11-20 14:13 ET; human DPO ratification pending (Kellen Short) |
| Accepted scope | Base (≈390k / ≈60 min) **+ S-1** (≈20k / ≈4 min) |
| Acceptance criteria | (1) every number in report and dashboard traces to an `out/dp_uc66_*` receipt computed this session; (2) FR-1 reconciles exactly; (3) every HP bar unchanged after first compute; (4) harness all PASS; (5) V1–V7 + VZ rules recorded per figure; (6) certification verdict in `05`; (7) bid vs actual in `07` |
| Change control | A bar changed after a grade is computed is a breaking change (`version-controller`) |
