# 03 · Governance
Agents: `kpi-calculator` · `technical-lineage-builder` · `dq-rule-definer` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 0 · Rule-1 search before declaring anything new
| Candidate | Search | Hit | Decision |
|---|---|---|---|
| game-winning / go-ahead / deciding run | `grep -i "walkoff\|go.ahead\|deciding\|game.winning\|gwrbi"` across `dp_uc*_kernel.py`, control-plane `03_*` | K58 `walkoff` (HL-1: walk-off HR only) | **GW-1 new** (HL-1 is a subset: walk-off homers) |
| xBA > .500 conversion | grep `estimated_ba_using_speedangle > .5`, `likely_hits` | 0 governed (client cell only) | **XC-1 new** (client rule, governed) |
| batted-ball share → wOBA relevance | grep `trendline.*share\|ld_rate.*woba` | `recap_viz.trendline_r2` (method only) | **G-LD new** gate; fit by plain OLS, refit independently in the harness |
| RISP repeatability | grep `risp` | K37 `risp_rows` (definition) | **RS-1 new** rule on the inherited definition |
| truncated PA | grep `truncated_pa` across kernels | **0 hits** (absent from K57 `NON_PA`) | **TP-1 new** frame rule; defect escalated (E-2) |
| season panel, slash, wOBA, xwOBA | K60, K57 WB-2, XW-1 | found | inherited |
| batted-ball profile, pull-air, direction, coordinates | CR-1, K46, DR-1, PA-L1 | found | inherited |
| runs created | K48 `runs_created` | found | inherited ("runs on watch") |
| field outline | K58 `wall_outline`, UC61 field geometry | found | inherited; geometry wrapped as `field_outline()` (Section B) |
| batter-side spray frame | K61 `spray_frame` | found, side-bound (`BATS = "L"`) | Section B generalization `spray_frame_for(stand)` |
| hitter pool, percentile | K54 `hitter_seasons`, KP-1 | found | inherited |
| pre-registered ledger rule | K48 PA-1 | found | PR-1 is a new instance scored by PA-1 |

## 1 · Inheritance (`technical-lineage-builder`)
`dp_uc67_kernel.py` imports, never copies. Pins frozen at first build (`dp_uc67_pins.json`, 13:32:24 ET, after the BID) and asserted at every run, plus K61's own 23:
`dp_uc61_kernel.py 0466c66e…` · `dp_uc48_kernel.py 0f63857a…` · `dp_uc62_kernel.py 2adc6005…` (matches UC62's manifest) · `dp_uc37_kernel.py 396c4600…` (control plane, parent).
**Section B (non-breaking):** `spray_frame_for`, `field_outline`, TP-1 in `load_house`.

## 2 · New KPI specs (`kpi-calculator`; GW-1 and the PR-1/G-LD/RS-1 bars written into the BID at 13:30 ET, before code)
### GW-1 deciding run (provisional)
- **Plain language:** in a game the Phillies won, the plate appearance during which they scored the run the opponent never answered.
- **Formula:** for each win with opponent final `opp`, the PA with `bat_score(first pitch) ≤ opp < max post_bat_score(PA)`. Exactly one per win.
- **Grain:** PA → counted per batter × season. **Population for ranks:** Phillies regulars 2020–26 with ≥1,000 governed PA (n = 11).
- **CDEs:** `bat_score`, `post_bat_score` (batting role), opponent `post_bat_score` (pitching role) for the final; `events` for mechanism.
- **Edge cases:** a run scoring on a wild pitch / error mid-PA still credits the batter ("during PA" mechanism; 0 for Bohm); extra innings and walk-offs need no special case.
### XC-1 xBA conversion (provisional)
`hits / likely_hits` over BIP (`type == "X"`) with `estimated_ba_using_speedangle > .5`. Untracked BIP drop out (no xBA). Small cells print counts.
### G-LD gate (provisional)
OLS `woba ~ ld_rate` over K54 hitter-seasons 2015–26 with ≥200 PA (subject included, he is a Phillie): passes iff slope > 0 and R² ≥ .05. Result: slope +.093, **R² .007**, n = 122 → fails. GB and FB fits reported as context, not gated.
### RS-1 (provisional)
Count of seasons with `woba_risp − woba_nonrisp > 0`; "a RISP hitter" iff ≥5 of 7. Result **4 of 7** (negative 2021, 2022, 2025).
### TP-1 (frame rule)
`events == "truncated_pa"` → NA in the UC67 frame. The row stays (a pitch, possibly a swing). Effect on Bohm: −3 PA/AB in 2026 (all pre-break), −1 in 2024.
### PR-1 ledger
Eleven signatures in three families, bars and windows verbatim in the BID and `dp_uc67_kernel.PR1`. Changing a bar after publication is **breaking**.

## 3 · Lineage to the published numbers
```
phils_2015..2026.parquet ─ LP-1 (K49) ─ load_house (TP-1) ─┬─ subject (id, R, W-3) ─┬─ season_panel / CR-1 / K46 / WB-1 / K48 ─ season_panel.csv
                                                          │                        ├─ windows ─ windows_2026.csv ─┐
                                                          │                        ├─ platoon / pitch-group cells ┼─ PR-1 (PA-1) ─ pr1_ledger.csv
                                                          │                        └─ spray_frame_for ─ ld_spray.csv + field_outline.json (K58 wall)
                                                          ├─ K54 hitter_seasons ─ hitter_pool_kp1.csv ─ G-LD ─ g_ld_fit.json
                                                          └─ game_table ⋈ pa_table ─ GW-1 ─ gw1_bohm_log.csv · phillies_leaderboard_2020_26.csv
parent dp_uc37 receipts ─ REC-2, HP-09
headlines.json ◄──────────────────────────────────────────────────── all of the above
   └─ dp_uc67_narrative.py ─┬─ report .md → .pdf
                            └─ dashboard .html
```

## 4 · Defects and findings (carried to the DPO)
| ID | Finding | Status |
|---|---|---|
| **TP-1 (new)** | K57 `NON_PA` omits `truncated_pa`; 65 such rows in the 2024–26 log count as PA and AB. Bohm 2026 log read .247/.313/.381 against a public .249/.315/.383 until fixed | Fixed in this frame; house fix escalated as breaking (E-2) |
| **REC-1 misdiagnosis (ours)** | T1 called the gap "one hit, official-scorer change" and restated the rule to pass. Wrong; withdrawn | `05` §4 |
| **HP-09 parent defect** | uc-pos-013's career table carries postseason PA in 2022–25 (+64, +53, +15, +16) | Errata recommended (E-3) |
| **SRC-1 (recurrence)** | Client-style frames without a game_type filter mix postseason | Known |
| **Client CR-1** | `chase_rate` and `putaway_rate` merge suffixes `'cr'` / `'par'` lack the underscore the other merges use, so any overlapping column comes back as e.g. `pitchescr` | Client code (cosmetic) |
| **Client CR-2** | `df['hit_id'] = …` assigns on a filtered slice (`bohm[...]`), a SettingWithCopy pattern; `hits` is a notebook global not in the shared cells | Client code |
| BID claim (ours) | "client pitch-grain cell credits mid-PA runs": not for Bohm | Withdrawn (E-4) |

## 5 · Privacy and tags (`privacy-watchdog`, `data-tagger`)
Public-figure performance data and public reporting. No medical inference (harness F). Salary appears only as a labelled carry-in. Tags: domain `pos`, subject area `player evaluation / career retrospective`, sensitivity **Internal**. **CLEAR** for internal; external after DPO review of C5.

## 6 · Version (`version-controller`)
`dp_uc67` **v1.0.0**, first release; additive (no inherited file edited). Breaking-change triggers: any PR-1 bar, the GW-1 definition, the G-LD population or bar, the RS-1 threshold. The house TP-1 fix (E-2) would be **breaking** for every 2024–26 governed line and needs its own version notice.
