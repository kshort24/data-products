# 01 · Strategy & Intake
**use-case-validator · source-system-profiler · domain-steward-proxy · business-glossary-agent**

## 1 · ID reservation
UC **#56** · `uc-pos-021` · `dp_uc56` · folder `uc-pos-021-sosa-2026-recap-001`. Collision scan clean (BID). Prior Sosa intake `uc-pos-003` (Layer-1 NO-GO) is not reopened; its "career scope" open item is answered for this product only (Phillies-only governed frame, STL as labelled context).

## 2 · Gap report (use-case-validator) — 6 gaps, 0 blocking
| # | Gap | Class | Resolution |
|---|---|---|---|
| G-1 | "Prior years with the Phillies" — 2022 is 59 PA | Non-blocking | Baseline 2023–25; 2022 shown, labelled (SRC-6) |
| G-2 | EV50 has two public meanings | Non-blocking | Client's comment ("median exit velo") governs; disclosed (GL-1) |
| G-3 | "Uptick" has no window | Non-blocking | TR-1 at the All-Star break, fixed in BID; ER-1 for change points |
| G-4 | "Sustainable" undefined | Non-blocking | OZ-1 call rule pre-registered |
| G-5 | Walkaway has no data in house | Non-blocking | Web carry-ins (CI-3, CI-5) + WA-1 rule |
| G-6 | Client frame mixes teams and game types | Non-blocking | Reproduced verbatim for HP rows; governed frame is PHI regular season |

## 3 · Source profile (source-system-profiler)
| Source | Rows for subject | Notes |
|---|---|---|
| `data/phillies/phils_2015..2026.parquet` | 4,223 regular-season pitches 2022–26 (+ 45 non-R PA) | anchor 2026-10-01; bat tracking from 2024 (96.6% of swings) |
| `data/opponents/edmundo.parquet` | 1,688 pitches STL 2018–22 (1,674 R) | no bat-tracking columns; ends 2022-07-23 (trade 07-30) |
| Sensor coverage | EV on 99.63% of BIP; `estimated_ba` on 98.28% of out-of-zone BIP | untracked BIP leave EV denominators |
| Postseason | 2022 10 · 2023 1 · 2024 5 · 2025 3 · 2026 7 PA | ledger only |

## 4 · Carry-ins (domain-steward-proxy) — quoted, never computed on
| CI | Fact | Source |
|---|---|---|
| CI-1 | 2026: .247/.283/.429, 9 HR, 250 PA, 84 G, 89 OPS+, 1.0 bWAR | Baseball-Reference |
| CI-2 | Final 50 G .275/.313/.493 (.806 OPS, 149 PA); RISP .923 OPS; top-16% OAA & sprint; $4.4M; CBA expires after 2026 | NBC Sports Philadelphia, 2026-10-02 |
| CI-3 | Salaries: 2022 $715.6k · 2023 $950k · 2024 $1.7M · 2025 $3.0M · 2026 $4.4M | Spotrac; Wikipedia; MLB.com 2026-01-08 |
| CI-4 | bWAR 2021 3.2 · 2022 1.4 · 2023 0.6 · 2024 2.2 · 2025 2.3 · 2026 1.0; 2026 LF 32 / 3B 21 / SS 18 / 2B 14 G | Baseball-Reference |
| CI-5 | Rosario 1/$2.5M (NYY) · Rojas 1/$5.5M (LAD) · Kiner-Falefa 1/$6.0M (BOS) · W. Castro 2/$12.8M (COL) | Bleacher Report FA tracker; AP; ESPN headline |
| CI-6 | Born 1996-03-06; acquired 2022-07-30 for JoJo Romero; left groin injury 2026-09-30 (WC G2) | Wikipedia; NBC Sports |
| CI-7 | Phillies career .260/.302/.444, 392 G; positive offensive WAR every Phillies season | PhillyVoice, 2026-10-09 |

**Conflict resolved:** NBC printed .242/.280/.410 and 8 HR on 10-02 (pre-finale); B-Ref and the log agree on .247/.283/.429. The log wins.

## 5 · Glossary (business-glossary-agent)
| Term | Definition | Status |
|---|---|---|
| **OZ-1 out-of-zone damage** | For PAs ending on a pitch in zone 11–14: OZ-BA = hits/AB; OZ-xBA = mean `estimated_ba_using_speedangle` over the same AB (K = 0; BIP lacking an estimate use the actual outcome); call RAN HOT (≥ +.030) / RAN COLD (≤ −.030) / EARNED | New, provisional |
| **WA-1 walkaway number** | AAV ceiling = top 2025–26 utility-comp AAV rounded down to $0.5M; term ≤2 yrs if ≤2 of six decline flags trip, 1 yr (+option) if ≥3 | New, provisional |
| **EV50** | Median exit velocity on tracked BIP (client definition). Not Statcast's "EV50" | Disclosed (GL-1) |
| EV90 / max EV / mean EV | 0.90 quantile / max / mean of tracked BIP exit velocity (UC27 precedent) | Inherited definition |
| Pull AIR% | Pulled non-ground-ball BIP / classifiable BIP (K46 v1.1.0) | Inherited |
| Chase cost (CC-1) | E[take run value \| count] − run value of the swing, per out-of-zone swing | Inherited (K54) |

## 6 · Data-dictionary carry-forward
Inherited CDE descriptions for `launch_speed`, `launch_speed_angle`, `estimated_ba_using_speedangle`, `zone`, `description`, `bat_speed`, `hc_x/hc_y`, `fielder_3…9` are unchanged from uc-pos-017/019/020. New physical outputs are described in `02` §3.
