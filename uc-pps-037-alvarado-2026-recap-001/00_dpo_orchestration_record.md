# 00 · DPO Orchestration Record: `uc-pps-037-alvarado-2026-recap-001`

**UC #53 · contract `uc-pps-037` · build `dp_uc53` · v1.0.0 · delivered 2026-10-18 ET**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL (C1–C6)** · independently verified **163 / 163** · DQ **11 PASS / 2 WARN / 0 FAIL** · brand 10 / 10 figures pass
Run: single turn. The RFP said to treat the bid as the winner, so the BID was filed and awarded at 10:57 ET and the build continued without a stop. House-format skill loaded first.

---

## 1 · The ask and how we framed it
The client submitted a notebook export (`c9ed969a-attachment.txt`), "Jose Alvarado". It opens with a closing note: "the last year of the José Alvarado Experience… remarkably inconsistent, sometimes reliable." It then runs code across his Phillies tenure:
- a `nresults` PA leaderboard
- tenure and by-year results
- cutter KPIs: putaway, whiff, chase, zone
- two pitcher × pitch scatters
- a 2×2 of cutter metrics by year
- a CSW table
- the house cumulative wOBA chart

The RFP asked for:
- a recap in the house pattern
- a tenure lens, since this is likely the end
- where 2026 declined
- an argument for moving on, or for "it was a blip"
- 00–07 receipts in a control-plane subfolder
- outputs in a control-plane folder
- a token and time estimate framed as a competitive bid

The organization read it as **four jobs**:
1. **Find the spine before writing.**
   - The tenure is real: #14 of 199 Phillies pitchers in PA faced, and #3 among relievers.
   - 2026 was his worst season as a Phillie on results.
   - The stuff and strike-throwing declined while the contact stayed soft. So part of 2026 was luck, but the part that wasn't luck got worse in the second half.
2. **Hold the comparison profile.** Five forms were scoped and two built: the PDF (10 pp / 9 sections) and the dashboard (7 chapters). It carries 10 figures and 2 new objects, the same shape as UC48/49/51/52. The decision memo is folded into report §8.
3. **Make the ending falsifiable.** DB-1 is eight decline-or-blip signatures with bars, written into the kernel before any 2026 rate was computed and scored by the inherited PA-1 rule. The call follows the roll-up.
4. **Reproduce the parent before improving it.** Ten HP rows were rebuilt on the client's own frame (`pps`, all game types, by name) with the client's functions, then restated on the governed frame.

## 2 · Delivery plan (departments actually engaged)
| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 7 gaps (0 blocking) → `01` §2 |
| | `source-system-profiler` | id scan: 27 opponent files hold 621237. Found ENT-1 (2018 rows under a batter's name) and SRC-1 (client frame mixes spring and postseason) |
| | `domain-steward-proxy` | 8 carry-ins: option, free agency, 2025 suspension, 2022 demotion, 2023 IL, 2026 role, ERA line, client lore |
| | `business-glossary-agent` | 4 new terms (OD-1 bands, DB-1 ledger, AB-1 automatic-pitch rows, tenure); CSW confirmed as locked |
| Engineering Design | `data-architect` · `eda-agent` · `metadata-mapper` · `dashboard-specifier` | CF-2d frame; EDA to file (2 reports); 7-chapter spec |
| Governance | `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` / `data-tagger` · `version-controller` | specs for OD-1 and DB-1 before code; lineage to `headlines.json`; privacy CLEAR; v1.0.0 |
| Engineering Build | `data-engineer` | everything ran on the laptop VM (render stack in `/tmp/pyrender`, `TMPDIR=/tmp`); 45 receipts in `out/` |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` · `certification-agent` | 13 DQ rules; harness families A–G, 163 checks |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` / `product-narrator` | reading paths, FAQ, catalog entry (`06`) |
| Platform & Marketing | `cost-watchdog` / `token-economist` | bid vs actual, calibration, tripwires (`07`) |

**Not engaged:** `machine-learning-engineer` (no projection bid; DB-1 is the governed substitute) · `join-validator` (single-grain frame; the EN-2 fan-out assert stands in) · `cost-watchdog` beyond `07`.

## 3 · Governance gate checks
| Gate | Result |
|---|---|
| G1 · Entity locked to MLBAM id | PASS: 621237 with `phillies_role == 'pitching'` (ENT-1 shows why the role matters) |
| G2 · Rule-1 search before declaring anything new | PASS: table in `03` §0; CSW and CN-3 found, DB-1 had 0 hits |
| G3 · Locked KPIs inherited, not re-derived | PASS: `dp_uc52_kernel.py` sha256 `3667f802…` (→ UC51 → K49/K50/K48/K44/barrel_rate) + `cumulative_metric.py` `a2888740…` |
| G4 · No re-derivation of existing work | PASS: season profile, runs on watch, WB-1, XW-1, RP-1, GS-1, PA-1 and the cumulative chart are all imported |
| G5 · Small samples print denominators | PASS: PA on every split; monthly cells 42–55 PA flagged |
| G6 · Superlatives name their population | PASS: "of 199 Phillies pitchers", "of 104 Phillies relief seasons", "of 897 pitcher-pitch-seasons", "of his 6 Phillies seasons" |
| G7 · Carry-ins labelled, sourced, never computed on | PASS: harness G (9/9); DQ-12 reconciles CI-7's 68 G / 70 K to the log |
| G8 · Pre-registration is not prediction | PASS: DB-1 judges 2026 against registered bars; it does not forecast 2027. Disclosure: carry-in CI-6 (mid-season Statcast figures) was read at T0, before registration |
| G9 · Every published number reconciles to a receipt | PASS: harness F 59/59; one narrative module feeds report and dashboard |
| G10 · Client claims graded, not overwritten | PASS: 10 HP rows (9 confirmed, 1 partly) |
| G11 · Anchor pinned | PASS: 2026-10-01 (build refuses a later log) |
| G12 · No medical inference | PASS: 2023 IL and 2025 suspension are carry-ins only |

## 4 · Capability fulfilment
| Asked for | Delivered as | Where |
|---|---|---|
| Season recap in the house pattern | 10-page PDF, 7-chapter dashboard + Artifact "The Full Ride" | folder root |
| Entire Phillies tenure | leaderboard, year table, outing bands and cumulative lines 2021–26 | report §2, §7; ch. 1, 6 |
| How 2026 declined | results vs his own seasons; cutter whiff and velocity; zone; monthly fade | §3–§6; ch. 2–5 |
| Move on, or a blip | DB-1 pre-registered ledger + both cases + call | §8; ch. 7 |
| Receipts 00–07, bid with tokens and time | this folder; `BID_…`; `07` §3 | here |
| Outputs in the control plane | all code, `out/` (45 receipts), report, dashboard | this folder (EDA at MLB `eda/dp_uc53/`, the house location) |

## 5 · The finding, in the DPO's words
José Alvarado gave the Phillies five-plus years and 1,273 batters, #14 among 199 Phillies pitchers since 2015 and #3 among relievers. 2022 and 2023 ranked #9 and #10 of 104 Phillies relief seasons. 2026 was his worst season here: a .342 wOBA against, 10 blow-ups in 68 outings, and the fewest clean outings. Some of it was luck. Hitters out-hit their contact by .040, and his hard-hit rate was a tenure low. But the arm told a different story. The cutter averaged 91.5 mph, 1.6 under 2022–24, and its whiff rate fell from 48.9% to 39.1%. His zone rate hit a tenure low, and from August his velocity faded while his expected numbers caught up with his results. On the pre-registered ledger, decline is SUPPORTED and blip is MIXED, so the call is DECLINE: move on. A return makes sense only on a short, cheap deal in a lower-leverage role.

## 6 · Where the organization argued with itself
**Is 2026 a blip?** `product-narrator` wanted to lead with the luck gap (+.040, five times his norm) and the 31.7% hard-hit rate, the case MLB.com made in July (CI-6). `kpi-calculator` pointed to the monthly receipts: from August his xwOBA (.344, .347) matched his results while the sinker fell to 97.1. **Resolution:** both cases ship in full in §8. The call is the registered roll-up, not either agent's preference.

**Was it "a few disasters"?** The client called the season "remarkably inconsistent". The B2 signature tested whether the damage clustered in a few blow-ups, which would support "blip". It came out CONTRA: his five worst outings held 39% of his runs, the smallest share of any Phillies season. **Resolution:** the dashboard says the damage was spread out, and the inconsistency is shown as frequency (10 blow-ups, 68% clean) rather than concentration.

**Which cumulative line is right?** The house module's default wOBA ended 2026 at .360. The same-basis wOBA (WB-1) said .351. **Resolution:** CM-D1. The module counts `woba_value` on intentional walks and sac bunts, whose `woba_denom` is 0. F9 passes a corrected spec (CM-1a) with endpoints asserted equal to WB-1, and the module is escalated (E-2), not edited.

## 7 · Escalations to the human DPO
1. **E-1 · Ratify** WB-1 (second use; UC52 first), RP-1 (second use) and CF-2c→**CF-2d** (subject passed in; recommend upstreaming CF-2d into the next kernel as the parameterized form).
2. **E-2 · Upstream CM-D1** in `cumulative_metric.py`: `METRICS["woba"]` numerator should be `woba_value` where `woba_denom > 0`. API-compatible, but values change, so `version-controller` classifies it a **correction**: re-render any published cumulative wOBA chart (the client's Alvarado chart ran high in 4 of 6 seasons).
3. **E-3 · AB-1** (new). The 2026 log carries automatic balls and strikes (16 for Alvarado) with no pitch. K44 counts them as pitches, and as in-zone (D-7). Recommend a `thrown` filter for zone and usage, then a back-check of 2026 zone rates in UC48–52.
4. **E-4 · RK-2.** K−BB computed from K44's rounded K% and BB% drifts by up to 0.1 pts (15.6% vs 15.7% here). UC52 used `krate − bbrate` for K−BB percentiles; recommend computing it from counts upstream.
5. **E-5 · ENV-3.** On the laptop VM, `pip` fails with ENOSPC unless `TMPDIR` is moved off the full `/sessions` volume. Add `TMPDIR=/tmp/...` to the MLB `CLAUDE.md` setup line.
6. **E-6 · Ledger.** `uc_ledger_AI_PATCH_uc-pps-037-alvarado-2026-recap.md` is a **pending paste** (copies here and at the MLB root).
7. **E-7 · Decision ownership.** DB-1 grades 2026; whether and at what price to re-sign is the front office's call. The report gives evidence and a registered verdict, not contract terms.
8. **E-8 · Commit.** Not made. Commits were not requested this run, and the MLB repo still carries stale `.git/*.lock` files (UC52 `07` §7). Files written to the MLB repo: `eda/dp_uc53/` (2) plus the contract and ledger-patch copies.

## 8 · Publish recommendation
**READY-CONDITIONAL. Internal audience (front office, pitching department, bullpen staff).**
- **C1** Ranks and percentiles are Phillies-frame (2015–26), not MLB-wide.
- **C2** Carry-ins are reported facts, never computed on; contract status per NBC (2026-10-02).
- **C3** OD-1 and DB-1 are provisional (first use). Changing a DB-1 bar after publication is breaking.
- **C4** Relief samples are small (274 PA; monthly cells 42–55 PA). Read direction, not decimals.
- **C5** Two wOBA bases, labelled. xwOBA is compared only with Statcast-basis wOBA.
- **C6** AB-1: the house zone rate includes 16 automatic-pitch rows in 2026. The thrown-pitch zone rate (41.4%) is printed beside it.

External publication: after DPO review of C2 and the §8 wording (it discusses a named player's contract decision).
