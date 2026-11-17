# 01 · Strategy & Intake
Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`

## 1 · Use case (from `intake/client_prompt_2026-11-16.md`)
Business question: *How did Aaron Nola's 2026 go as a whole, and how does he sequence pitches — by batter side, by catcher, and over his career — in ways that prevent runs?*
Personas: Pitching Coach, Pitching Analyst, Catchers, Front Office. Grain: pitch (house log) → window / PA / start / pitcher-season.

## 2 · Validator verdict: **GO** (0 blocking · 3 non-blocking, all closed at intake)
| # | Gap | Class | Resolution |
|---|---|---|---|
| G-1 | Credit rule for a sequence undefined (any-n-gram vs ending vs setup) | non-blocking (design) | DPO ruling **Q-A**: setup lift (headline) + terminal endings |
| G-2 | "Weak contact" has no house glossary term | **would block (Principle 1)** | returned to DPO → ruling **Q-B**: Savant LSA 1–3 → **PC-1** |
| G-3 | Sequence length / window scope unspecified ("can of worms") | non-blocking | DPO ruling **Q-C**: career-wide, every length k ∈ {2,3,4} |

## 3 · Source profile (`source-system-profiler`; full EDA in `MLB/eda/dp_uc64/nola_regular_2015_2026.md`)
| Item | Value |
|---|---|
| Nola rows, pitching role, all types | 31,077 (R 30,079 · D 299 · L 245 · F 227 · W 148 · S 79) |
| PA groups (game_pk × at_bat) | 8,003 (the T0 / BID count). **7,773** end on a Nola batter event (SQ-3 / PI frame); the rest end in pickoff / CS / truncated (14) or were finished by a reliever after he left mid-PA |
| 2026 | 33 starts, 2,955 pitches, 745 PA (458 LHB / 288 RHB at T0 probe) |
| `delta_run_exp` null | 22 of 30,079 |
| BIP with null `launch_speed_angle` | 43 of 5,164 (excluded from PC-1 denominators) |
| `fielder_2` null | 0 |
| Curveball tags | CU 2015–16, KC 2017+ (one pitch) → PT-H |
| 2026 SL tag | 19 pitches, 83.1 mph, −0.8 in IVB / 3.6 in HB — kept as tagged, too few to read |
| IN / PO / null tokens | 25 / 21 / 14 windows (k = 2/3/4) dropped |
| Sequence-length profile (T0) | PA length 1–4 pitches = 64% of PAs; 2026 = 502 distinct full strings over 746 PA → full strings too sparse to rank |

**Fitness:** fit for purpose at career scope for k = 2–3; k = 4 descriptive (20 rankable of 976 distinct).

## 4 · Domain steward notes (`domain-steward-proxy`)
- **Prior Nola products** (re-read, not re-graded): `uc-pps-008` (dp_uc8, edge/OOZ/AIR-GB origin), `uc-pps-014` (dp_uc15), `uc-pps-021` (dp_uc25, LHB tripwires), `uc-pos-012` (dp_uc35 Alcántara), `uc-pps-027` (dp_uc38 battery: TR-1, G4, G7; BAT-4/5), `uc-cat-002` (dp_uc59, Nola's best half with Stubbs).
- **PitchCom / G4:** no Statcast field attributes the call. Batterymate = catcher behind the plate.
- **Cutter arrives 2021** (1.5% 2021 → 7–9% 2022–26): era E1 has no cutter; cutter sequences are structurally THIN in E1.
- **2025** injury-shortened (17 starts, 407 PA); 2020 short (287 PA).
- **EN-3:** in batting-role rows `player_name` is the hitter (Nola's own at-bats carry his name with other pitchers' ids) — the harness hit this at V03 and was corrected to pitching rows.

## 5 · Carry-ins (public; display + REC-1 only)
| CI | Fact | Source |
|---|---|---|
| CI-1 | 2026: 33 GS, 175.1 IP, 7-12, 4.67 ERA, 177 K, 59 BB, 1.35 WHIP | CBS Sports player page; ESPN player page |
| CI-2 | 5.86 ERA through 13 starts (after the 6/07 CWS start) | MLB.com, "What does Nola need to do to turn around rough season?" |
| CI-3 | 2.93 ERA, 61:20 K:BB over 11 starts since Aug 1 | CBS Sports news note |
| CI-4 | Wild Card Game 3 starter at ATL on short rest; 1.2 IP, loss | CBS Sports |

## 6 · Glossary (`business-glossary-agent`) — new terms, PROVISIONAL pending DPO ratification
SQ-0 pitch sequence (client function) · PT-H pitch-type harmonization · SQ-1 sequence window · SQ-2 setup lift · SQ-3 terminal ending ·
**PC-1 poor contact (DPO-defined)** · OUT-1 out PA · SQ-4 stability (shrink + PA-cluster bootstrap) · SQ-5 era drift / FADED · SQ-5d decomposition ·
SQ-6 batterymate book · PI-1 predictability. Full definitions: BID table + `03` §2. No collision with existing terms (BAT-5 repeat-pitch rate is a
usage rate on pairs; SQ-2 is a value measure on pairs — related, distinct).
