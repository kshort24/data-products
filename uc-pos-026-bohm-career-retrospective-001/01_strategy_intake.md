# 01 · Strategy & Intake: `uc-pos-026`

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`

## 1 · Ledger and ID reservation
- Ground truth for numbering: `uc_ledger_AI_PATCH_uc-pps-042-shugart-2026-recap.md` (pending paste; wins over the stale repo ledger tail) → **UC #67, `uc-pos-026`, `dp_uc67`**.
- Collision check 2026-11-22 13:29 ET: no `dp_uc67*` in the MLB root or `out/`; no `uc-pos-026*` folder in the control plane.
- Prior art for this subject: **uc-pos-013** (UC #38, `dp_uc37`, delivered 2026-08-24, data to 2026-08-22). Inherited by import (`risp_rows`, `BREAK`) and graded (HP-09, PR-1 H-F), never copied.
- Shape inherited from the pos recaps UC56/UC58/UC60/UC61 (kernel chain, field outline, recap_viz) and UC62 (career recap: PDF + dashboard, trail layout, BID).

## 2 · Use-case validation (gap report)
| # | Gap | Class | Resolution |
|---|---|---|---|
| V-1 | "Continuation of uc-pos-013" names no question | Non-blocking | Q1: did the turnaround hold? Scored as PR-1 H-F on the unseen 8/24–9/27 window |
| V-2 | "If the line drive deficiency is a good angle": "good" undefined | Non-blocking | H-LD + pool gate G-LD, rule filed in the BID before either was computed |
| V-3 | "The spray chart visual I like" not named | Non-blocking | Resolved to the house field sketch (`dp_uc61` F3 / K58 `wall_outline` + 90-ft diamond + 95-ft arc), the only outfield-wall-plus-diamond chart in the repo |
| V-4 | "Game-winning runs" undefined; client cell needs a `gms` table not in the plane | Non-blocking | GW-1 spec (BID); `gms` reconstructed from the house log (`game_table`), HP-01 reproduces the client cell on it |
| V-5 | "Skill with RISP" presumes a skill | Non-blocking | RS-1 repeatability rule filed; results and skill reported separately |
| V-6 | "Will not be returning" is an assumption | Non-blocking | Treated as the client's frame; public status as carry-ins CI-2/CI-3 (no qualifying offer; free agent) |
| V-7 | Videos (game-winning, helmet spikes) in the cells | Non-blocking | Out of scope per the client ("not relevant to the analysis") |
| V-8 | Client comments are claims with no bars | Non-blocking | HP-01..HP-08 bars set in the BID; HP-09 added for the parent |

**Go.** No blocking gap.

## 3 · Source profiling (`source-system-profiler`)
| Source | Rows | Notes |
|---|---|---|
| `data/phillies/phils_2015…2026.parquet` via LP-1 (K49) | 556,863 house rows; anchor 2026-10-01 (last regular game 2026-09-27) | 1,842 regular-season games 2015–26 (2020 = 60) |
| Bohm, batting, id 664761, regular season | **13,126 pitches**, 2020–26 | 0 duplicate pitch keys (EN-2) |
| Bohm, excluded | 2022 D/F/L/W 53/25/64/75 · 2023 D/F/L 67/28/89 · 2024 D 39 · 2025 D 60 · 2026 E 6, F 41 (Wild Card), S 123 | receipted in `headlines.excluded_non_regular` |
| `truncated_pa` rows (TP-1) | Bohm 4 (2026: 3, all pre-break); Phillies 2024–26: 65 across both roles | found by harness family A; see `03` §4 |
| Parent receipts `dp_uc37_headlines.json`, `dp_uc37_career_by_year.csv` | read, not inherited | REC-2 and HP-09 |

EDA to file: MLB `eda/dp_uc67/bohm_reg_2020_26.md`.

## 4 · Domain context and carry-ins (`domain-steward-proxy`)
| CI | Fact | Source | Used for |
|---|---|---|---|
| CI-1 | 2026: 155 G, .249/.315/.383, 15 HR, 29 2B, 88 RBI; 2026 salary $10.2M | NBC Sports Philadelphia; MLB.com free-agency profile (2026-10-09) | REC-1 (exact), AB-1 (155 G = 153 with a PA + 2 defensive-only) |
| CI-2 | Phillies did not extend the $23.15M qualifying offer; free agent without draft-pick compensation | NBC Sports Philadelphia, Nov 2026 | departure frame |
| CI-3 | Dombrowski: "those 90 runs he drives in every year will be missed" | NBC Sports Philadelphia | §5 framing (quote < 15 words) |
| CI-4 | .159/.227/.206 with a .171 BABIP through 35 games | MLB.com profile | §2 April context |
| CI-5 | Moved to first base after the Arraez acquisition | NBC Sports Philadelphia | position context; log: 106 G at 3B, 50 at 1B |
| CI-6 | NLWCS loss to Atlanta; go-ahead HR in Game 2 | MLB.com | postseason, excluded from rates |

**Conflict resolved:** CI-1's 155 G vs 153 games with a PA in the log → 2 defensive-only appearances (fielder columns). Reconciled exactly (AB-1).

## 5 · Glossary (`business-glossary-agent`)
| Term | Status | Definition |
|---|---|---|
| **GW-1 deciding run** | NEW, provisional | In a Phillies win, the PA during which the Phillies' score first passed the opponent's final total; credited to the batter at the plate; mechanism printed. Not RBI |
| **XC-1 xBA conversion** | NEW, provisional (client's rule, governed) | Share of BIP with `estimated_ba_using_speedangle` > .500 that became hits |
| **G-LD gate** | NEW, provisional | OLS of wOBA on LD share across Phillies hitter-seasons 2015–26 (≥200 PA): passes iff slope > 0 and R² ≥ .05 |
| **RS-1 RISP repeatability** | NEW, provisional | RISP wOBA > non-RISP wOBA in ≥5 of 7 seasons |
| **W-3 windows** | Scoped | pre-break (≤ 7/15), UC37 post-break (7/16–8/22), after the audit (8/23–end; first game 8/24) |
| **TP-1** | NEW frame rule | `truncated_pa` rows are non-terminal (not PA, not AB); pitches kept |
| Runs on watch | Existing (K48 `runs_created`), scoped | runs that scored during his PA, whatever the mechanism. Not Bill James RC |
| RISP | Existing (K37 `risp_rows`) | runner on 2B or 3B on the terminal pitch |
| Luck gap | Existing pair (WB-1 − XW-1) | Statcast-basis wOBA minus xwOBA, same PA ends |
