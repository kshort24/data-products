# 02 · Engineering Design
**data-architect · kpi-calculator · join-validator · eda-agent**

## Grain layers

| Layer | Grain | Rows | Purpose |
|---|---|---|---|
| L0 population | `player_name` × `game_year`, ≥50 PA | **217** hitter-seasons (98 players) | profile percentile benchmark |
| L0b context | `player_name` × `game_year`, >80 CF games | **9** player-seasons (8 comparators) | CX-1 centre-field comparison set |
| L1 monthly | `game_year` × `month` | 6 | primary curated frame `z`, 44 columns |
| L1b window | `window` (pre/post 15 Jun) | 2 | the premise contrast |
| L1c platoon | `hill_window` × `p_throws` | 4 | PL-1 counterfactual input |
| L2 rolling | `season_key` × `cumulative_pa` | 4,177 across 9 seasons | CX-2 ghost-line hero chart |
| L3 pitch | `window` × `pitch_group` / `pitch_type` | 6 / 8 | arsenal read |

## KPI register

| ID | KPI | Status | Source / definition |
|---|---|---|---|
| — | PA / slash / wOBA / K% / BB% | **INHERITED** (rebuilt unrounded per D4) | `nresults`; seasonal wOBA constants, IBB excluded |
| — | chase / whiff / swing / hard-hit / barrel / OOZ-whiff | **INHERITED** | notebook; D1–D2 `_fix` variants from `dp_uc33_kernel` |
| AP-1 | `fpsr` | **INHERITED-APPROVED** | `cde.fpsr` approved in the Rangel contract. **Second `pos`-side use** — value-stream annotation, not a new term |
| AP-2/3 | `swing_rate`, `srfp` | INHERITED-PROVISIONAL | from `uc-pos-010`, consumed unchanged |
| AP-6 | rolling line by cumulative PA | **INHERITED-EXTENDED** | `running_line_pa` **extended from wOBA to BA and OBP**. Extension, not a fork — same ordering, same weights |
| **CR-1** | `battedball_profile` | **NEW-PROVISIONAL** | GB/FB/LD/PU shares over all BIP; `mean_la`/`median_la`/`mean_ev` over **tracked** BIP only, NULL below 50 |
| **CR-2** | `xcontact` (`xba_bip`, `xwobacon_bip`) | **NEW-PROVISIONAL** | mean Statcast estimate per BIP. **Not comparable to `woba`** — different denominator, per O-4 |
| — | `babip` | **NEW field on `nresults_unrounded`** | `(H − HR) / (AB − K − HR + SF)` |
| **CX-1** | `cf_context_pool` | **NEW-PROVISIONAL** | transcribed verbatim from the DPO's notebook snippet; thresholds unchanged |
| **PL-1** | `platoon_counterfactual` | **NEW-PROVISIONAL** | direct standardisation — target-window within-split rates × reference-window PA weights |

## Join validation

| Check | Result |
|---|---|
| L1 monthly master stable at 6 rows across 10 merges | ✅ no fan-out |
| monthly PA sum == season PA | ✅ 362 == 362 |
| pitch-group PA sum == season PA | ✅ 362; pitch rows sum == 1,323 |
| `swings` in `swing_rate` == `swings` in `whiff_rate` denominator | ✅ same population by construction |
| CX-1 three-step join (pps `fielder_8` → pos `batter` → per-game restriction) | ✅ **fan-out risk is real here** — the `fielder_8` × `game_pk` grain must be de-duplicated before the batting join, or a player's PA multiply by his defensive innings. Verified: Crawford's context PA = **361** vs season 362, a 1-PA difference from one game in which he did not clear the >10-pitch CF threshold. Expected and disclosed, not silently absorbed |
| left-merge NULLs | rates NULL where the denominator is absent; **no blanket `fillna`** |

## EDA notes that shaped the design

- **wOBA path is .327 / .310 / .252 / .308 / .263 / .356.** Not a ramp — May is the trough, **July is a relapse**. This killed the "steady climb" framing at design time and moved the breakpoint scan from nice-to-have to required.
- **BABIP +79 pts against xwOBAcon +49 pts** across the break → the results/contact split (C-2) is where the answer lives.
- **Mean launch angle 2.28° → 2.22°.** The single most important null result in the build; the design must make it hard to miss, hence its own row on Fig 3 and its own KPI tile.
- **GB mean exit velocity FELL 84.9 → 80.4 mph while GB batting average ROSE .258 → .312.** Required a dedicated ground-ball-quality receipt — this is the speed hypothesis, and it is confirmable.
- **LHP share 15.3% → 15.0% across Hill's debut, but 2.4% in August.** The premise is falsified at the window grain and confirmed at the half-month grain. **The design must report both**, otherwise either grain alone misleads.
