# 03 · Governance
**business-glossary-agent · metadata-mapper · data-dictionary · data-tagger · domain-steward-proxy**
`uc-pos-025-harper-2026-recap-001` · UC #61 · `dp_uc61` v1.0.0

## 0 · Inheritance (Rule-1 searches at T0)
| Searched for | Found | Decision |
|---|---|---|
| prior Harper UCs | UC #23 dp_uc22 (governed); four ad-hoc scripts (ungoverned) | import `tag_regions` / `oz_kpis` (pinned); cite the scripts; H1 OZ-1 reproduces .411 exactly (OZ-REP) |
| recap spine | K60 → K58 → K57 | inherit by import (`season_panel`, `ev_profile`, `ch1`, `game_seq`, `wall_outline`) |
| career loader | K58 `load_career` (Schwarber-bound) | parameterized copy in Section B; K58 unchanged |
| cumulative contract | `cumulative_metric.py` (one metric, Statcast `woba_value`) | CM-2 widens it to the slash line on house weights; module pinned, not edited |
| spray / direction | K40 PA-L1, DR-1; K56 pull-air; K54 CBP_DIMS | reused; convention asserted for a LHB |
| hitter pools, eras | SD-1 `phi_hitter_seasons_200`; SD-2 `asb_2026` | reused |
| doubleheader order | K58 DH-1; UC58 finding for 2026-04-30 | DH-2 override (sourced) |

**Pins:** `dp_uc60_kernel.py` `534e2399…`, `dp_uc22_harper_own_the_zone.py` `530d05cd…`, `cumulative_metric.py` `a2888740…` + the K60 chain = **23, all PASS**.

## 1 · Glossary (provisional, DPO to ratify)
- **AP-1** approach held: three legs (chase ≤ 2019–25 max, BB% ≥ min, K% ≤ max).
- **HC-1** hard contact faded: three legs (hard-hit, barrel, EV p90 at or below the 2019–25 minimum).
- **OZ-H** edge held: full-season OZ-1 ≥ prior season, and no CHANGED-downward H2.
- **DMG-1** damage; **CM-2** cumulative slash; **NC-1** notecard copy rule; **DH-2** sourced DH order.

## 2 · Data dictionary: published receipts (`out/dp_uc61_*`, 34 + kit)
`season_panel` (12 seasons × slash, xwOBA, discipline, contact, batted-ball, direction, OZ), `context_pool_200`, `position_ledger_2026`, `by_half_2026`, `by_month_2026`, `cum_slash_2015_26` (8,000+ PA rows), `career_envelope`, `hand_2026`, `hand_2019_25`, `hand_group_2026`, `hand_group_2019_25`, `by_year_hand`, `pitch_map_2026`, `zone_damage_2026`, `oz_by_season`, `oz_by_half_2026`, `spray_2026`, `field_outline.json`, `hr_log_2026`, `headlines.json` (6 dp), `hp_grades`, `notecard_copy.json`, `dq_scorecard`, `visual_audit`, `figure_specs.json`, `verification`, `f1`–`f3` JSON + PNG, `notecard_reference.png`, `design_kit/` (16 files + `manifest.json`).

**Tagging (data-tagger):** public-figure performance data, domain `pos`, internal until the DPO publishes. No PII. Pitcher names are not carried into the kit.

## 3 · Findings for the house (domain-steward-proxy)
1. **The June "lefties are luck" read did not hold.** The ad-hoc vs-LHP report (95 PA) leaned on a .383 xwOBA; the full season finished .314 xwOBA vs LHP. Ad-hoc small-sample reads should carry a re-test date.
2. **K58 `load_career` is subject-bound** (module constants). Section B's parameterized loader is the candidate to replace it in the next kernel that touches it.
3. **DH order:** 27 career DH days still order by game_pk (fallback). Only intra-day cumulative paths are affected. A team-level DH registry (SD-2 entry) would close it for every player.
4. **Nullable booleans:** `launch_speed >= 95` on nullable Float64 yields NA; `~` then fails. Every DMG / hard-hit flag in a pitch-level receipt should `fillna(False)`.
5. **Fielded point ≠ landing point:** 14 hits sit up to 7.1° past a foul line on the spray (doubles fielded in foul ground). Any "fair-territory" filter on hc must not drop them.
