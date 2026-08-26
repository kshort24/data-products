# 01 · Layer 1 — Intake, Validation & Source Profile

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`

---

## A · Use-case validator — gap report

**Verdict: PROCEED.** One blocking issue, discovered at execution rather than intake.

| # | Gap | Class | Resolution |
|---|---|---|---|
| V-1 | "His last several starts" undefined | Non-blocking | DV-1: last 5 starts, with 3/8 sensitivity variants. Disclosed on the published surface |
| V-2 | "Actions they have made… driving positive outcomes" implies causal attribution | **Design-blocking, resolved** | Reframed as *observable approach change co-moving with outcome change*. Causal language prohibited (G3); person-level attribution impossible (G4/AT-1) |
| V-3 | PitchCom pitch-calling is central to the ask and **absent from the data** | **Non-blocking, permanent limit** | Stated up front in the report, written to `dp_uc38_attribution_guard.csv`, and repeated in §9. Not a research gap — a data-plane fact |
| V-4 | Catcher assignment is not randomised | Non-blocking, **design-shaping** | Confound panel made a mandatory ship-along (G3). No causal claim survives review without it |
| V-5 | Tonight's battery and lineup are DPO prose, not a posted card | Non-blocking | Logged as manual carry-in in the freshness manifest; confirm pre-game |
| V-6 | Nola's 2015–19 catchers are outside `uc-cat-001`'s 2020–26 identity profile | Non-blocking | Dual-path resolution (DV-2) with a cross-check that FAILs loudly on disagreement |
| V-7 | Expected small samples at `Nola × Stubbs × window` | Non-blocking | G5 floors as flags; PA/pitch counts ride on every row and print on every report line |
| V-8 | The supplied KPI list is "not exhaustive… reference where appropriate" | Non-blocking | Honoured in full as the outcome layer; the DPO's exact merge is additionally reused as the Tier-B **independent verification path** |
| ~~**V-9**~~ | ~~MLB parquet data plane not mounted in the execution session~~ | ~~**BLOCKING**~~ | ✅ **RESOLVED 2026-08-26** — DPO granted folder access on request; build executed against `phils_2015..2026.parquet` (29,499 Nola pitches, 311 starts). Source profile re-derived live, superseding the `uc-cat-001` carry-in |

## B · Source-system profiler — fitness for purpose

**Overall: FIT.** Every CDE the use case needs exists and is fit; the only defect is
*reachability*, not quality.

| CDE | Column | Fitness | Evidence |
|---|---|---|---|
| Catcher identity | `fielder_2` | **FIT** — 0.000% null | `uc-cat-001` 01b, 143,389 pitches 2020–26 |
| Pitcher entity | `pitcher` | **FIT** | lock 605400; guards Nolan Hoffman 676510 |
| Pitch type | `pitch_type` | **FIT** — 0.030% null | `uc-cat-001` 01b |
| Count state | `balls`, `strikes` | **FIT** | complete |
| Sequence position | `pitch_number`, `at_bat_number`, `game_pk` | **FIT** | the BAT-5 chain key |
| Zone | `zone` | **FIT** — 0.031% null, range 1–14 | zone 10 legitimately absent from the Statcast schema |
| Location | `plate_x/z`, `sz_top/bot` | **FIT** — 0.031% null | same 44-row tracking-dropout cluster |
| Outcome | `events` | **FIT** — 74.3% null **by design** | populated only on PA-terminal rows; must aggregate at PA grain |
| Contact quality | `estimated_woba_using_speedangle` | **FIT on BIP** — >99% populated | pitch-level mean is contaminated; use `xwobacon` (`uc-pps-021` fix) |
| Batted-ball type | `bb_type`, `launch_speed` | **FIT** | air/GB and hard-hit |
| wOBA weights | `wOBA and FIP Constants.csv` | **FIT** | per-year join; `uc-cat-001` caught a 2013-for-2023 transcription error in an earlier spec — per-year join is the standing correction |

**Catcher population (carry-in, `uc-cat-001` 01b, profiled 2026-08-09, staff-wide 2020–26):**

| `fielder_2` | Name | Pitches | Share |
|---|---|---|---|
| 592663 | J.T. Realmuto | 103,807 | 72.40% |
| **596117** | **Garrett Stubbs** | **18,015** | **12.56%** |
| 665561 | Rafael Marchán | 12,832 | 8.95% |
| 595284 | Andrew Knapp | 8,434 | 5.88% |
| 605244 | Aramis Garcia | 279 | 0.19% |
| 664848 | Donny Sands | 22 | 0.02% |

*Nola's personal distribution is computed by the build, not assumed from this table. His
2015–19 batterymates are outside this window entirely and are resolved by DV-2.*

**Fitness caveat that shapes the report:** Stubbs is the **backup**. At ~12.6% staff-wide,
the `Nola × Stubbs × last-5` cell is expected to be small. The product is designed so that a
small answer is a *reportable* answer — floors flag rather than filter, and the sensitivity
table exists so a thin window cannot masquerade as a finding.

## C · Domain steward proxy — rules, quirks, prior findings

| # | Domain knowledge | Consequence for this build |
|---|---|---|
| D-1 | **PitchCom lets the pitcher call his own game.** The DPO states Nola wears the transmitter | Makes "catcher effect" conceptually ambiguous *even if the data were richer*. The unit of analysis is deliberately **the battery**, never a person |
| D-2 | Backup catchers are assigned, often as a "personal catcher" arrangement or around rest days | G3 confound panel |
| D-3 | Nola's 2026 shape (`uc-pps-021`, through 7/16): career-worst .358 wOBA / .509 SLG / 5.1% HR-per-PA, **velocity intact**, K% steady at 23.8% | The improvement being investigated is against a **declining** baseline — "pitching well lately" must be measured against his own 2026 mean, not his career |
| D-4 | The whole lefty gap is the free pass: **10.7% BB vs LHB / 2.8% vs RHB** on **58.8% / 73.5%** first-pitch strikes, with *identical* contact quality by side | The single most decision-useful cell in this product (report §5.1) |
| D-5 | The changeup woke up: 26.9% whiff vs LHB (up from ~16% at UC8), July usage to 21%; the knuckle curve remains the identity at ~34% to both sides | The concrete mix prediction §3.1 tests |
| D-6 | The ABS/zone hypothesis was tested twice and rejected — edge rate .370 vs .374 career norm | Do not spend a section on the umpire |
| D-7 | Against Miami specifically, the lefty polarity **reverses** (`uc-pos-012`) — the league-wide leak is not universal | Opponent-conditional effects are real; another reason the confound panel matters |
| D-8 | A pitch log can carry **two catchers in one game** | `catcher_split` flag; those games are ambiguous and are reported, not assigned |

## D · Business glossary agent — term status

| Term | Status | Authority |
|---|---|---|
| wOBA, xwOBAcon, K%, BB%, HR/PA, whiff, chase, putaway, first-pitch strike, hard-hit, edge rate, OOZ called-strike rate, air/GB rate | **APPROVED — locked** | UC8 → UC11 → UC15 → UC25 line; `Baseball Functions.ipynb` |
| Two-strike fastball usage, in-zone whiff | **APPROVED** | `uc-cat-001` KPI-1 / KPI-3 — definitions inherited verbatim, first implementation is this UC |
| Catcher, battery, count state | **DRAFTED this UC** | `03_governance.md` |
| Repeat-pitch rate, arsenal entropy, ahead-vs-behind divergence, zone rate by count state, first-pitch mix, putaway-pitch mix | **NEW-PROVISIONAL** | `03_governance.md`; require DPO ratification (E-2) before entering the locked set |

**No CDE meaning was inferred by any agent** (CLAUDE.md governance principle #1). Where a
definition did not exist, the term is marked NEW-PROVISIONAL and returned to the DPO rather
than quietly adopted.
