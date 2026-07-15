# 03 — Glossary Alignment & KPI Specs · uc-pos-004 (dp_uc20)

**Agent roles:** business-glossary-agent + kpi-calculator · **Verdict: PASS** — 8/10 user KPIs map to locked terms; 2 NEW KPIs specified below (provisional SC-1, SC-2)

## User KPI list → glossary mapping
| User term | Locked term / status | Mechanics (inherited verbatim, dp_uc18 kernel) |
|---|---|---|
| home runs | HR (locked) | `events=='home_run'` count |
| batting average | BA (locked) | hits/AB, AB excludes walk, intent_walk, HBP, sac_fly, sac_bunt |
| obp | OBP (locked) | (H+BB+HBP)/PA |
| slg | SLG (locked) | TB/AB |
| ops | OPS (locked) | OBP+SLG |
| woba | wOBA (locked) | FanGraphs season weights joined game_year==Season; IBB excluded from BB |
| hard hit rate | Hard-Hit% (locked) | `launch_speed>=95` on `type=='X'` |
| barrel rate | Barrel% (locked) | `launch_speed_angle==6` — Statcast-native encoding, per DPO's note |
| **run creation** | **NEW → SC-1 wRC** | spec below |
| **pitches_per_plate_app** | **NEW → SC-2 P/PA** | spec below |

Standard scouting set also carried (all locked): K%, BB%, xwOBA proxy, chase, whiff, discipline panel, pulled-air, sweet-spot, GB/FB/LD/air, EV percentiles. Measurables tier (bat_speed, swing_length, attack_angle) are Statcast-native fields consumed as-is — no business meaning inferred.

---

## SC-1 — wRC ("run creation") — PROVISIONAL
- **Plain language:** How many runs the batter's overall offensive contribution was worth, scaled from how far his wOBA sits above/below league average, plus the league-average run value of his playing time.
- **Formula:** `wRAA = (wOBA − lgwOBA) / wOBAScale × PA`; `wRC = wRAA + lg(R/PA) × PA`; pace form `wRC/600 = wRC / PA × 600`.
- **Grain:** season (or any get_stats level); **Population:** all PA, R games, entity-locked.
- **Inputs:** locked wOBA (kernel); `lgwOBA` = `wOBA` column, `wOBAScale`, `R/PA` from `wOBA and FIP Constants.csv`, keyed Season==game_year.
- **Edge cases:** 2026 constants are FanGraphs in-season values → wRC provisional ±2% until season close (stated in report §3 and §7). Short seasons (2016, 2020): report per-600 form alongside raw. No park or league adjustment (that is wRC+, out of scope — no park-factor plane locally); the report says "wRC", never "wRC+".
- **Receipt:** `out/dp_uc20_schwarber_first_half_wrc_by_season.csv`.

## SC-2 — P/PA (pitches per plate appearance) — PROVISIONAL
- **Plain language:** How many pitches the batter makes the pitcher throw per completed plate appearance — a workload/patience indicator.
- **Formula:** `pitches / plate_apps` from the locked get_stats aggregates (pitches = all rows; PA = events not in {NA, pickoff_1b}).
- **Grain:** season; **Population:** all pitches, R games, entity-locked.
- **Edge cases:** truncated PA (inning-ending caught stealing etc.) count their pitches but no PA event on the batter's line only if events is null for the final pitch — consistent with kernel PA definition; acceptable at season grain. Interpretation guardrail: P/PA is an *approach descriptor*, not a value metric — report pairs it with swing-rate panel to avoid "more pitches = better" misread.
- **Receipt:** `out/dp_uc20_schwarber_first_half_ppa_by_season.csv`.

## Duplicate/conflict scan
No existing glossary term covers either concept (Marsh UC introduced no run-value KPI; pps UCs' FPSR/CSW are pitcher-side). No naming conflicts. **Recommend promotion to locked after DPO sign-off** — both formulas are FanGraphs-standard, no local invention.
