# 01 · Strategy & Intake — `uc-pps-032`

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy`

## 1 · Ledger and ID reservation

| Namespace | Ground truth checked | Claimed |
|---|---|---|
| UC ordinal | `uc-pos-017` README "Next: UC #47"; `uc_ledger_AI.md` says #25 (stale — known drift) | **#47** |
| Build artifact | `ls dp_uc4*` at MLB root → max `dp_uc44` at root; control plane max `dp_uc46`; `out/` no `dp_uc47*` | **`dp_uc47`** |
| Stream id | control plane `uc-pps-031` latest; no `uc-pps-032*` anywhere | **`uc-pps-032`** |

## 2 · Use-case validation (gap report)

| # | Gap | Blocking? | Resolution |
|---|---|---|---|
| V-1 | Value stream for evaluating non-Phillies players | Blocking | **DPO decision 9: `pps` with scope note** (00 header) |
| V-2 | Population for the external comparison | Blocking | **Decision 10: bounded set, "this era"** → 2018–2026 |
| V-3 | Is `nphl` league-wide? | Blocking | **Decision 11: non-Phillies, not MLB-wide** → profiled (§3) |
| V-4 | Operational definition of "benefit most" | Blocking | **Decision 12: aspirational, open to suggestions** → EFS + needle swap (AF-5/6) |
| V-5 | The ask cites a profile UC ("UC-PPS-XXX-A") whose flags this reuses | Blocking | Rule-1 search: **it doesn't exist**. Flags defined here first (G4 in `00`) |
| V-6 | "Stuff" collides with SG-4 "Stuff grade" | Non-blocking | Rename → `ff_elite_shape_flag`; escalated E-2 |
| V-7 | "Currently on the Phillies" undefined | Non-blocking | = threw ≥1 pitch for PHI in the 2026 regular season. Domínguez (41 pitches *against* PHI in 2026) is therefore external |

## 3 · Source profiling — what `nphl` actually is

`get_nphillies_data()` = every parquet in `data/opponents/` concatenated, de-duplicated **only within itself**.

| Measure | Value |
|---|---|
| Files | 128 |
| Rows | 905,751 |
| Minor-league files (home/away not MLB clubs) | **15** — `abel`, `clearwater_*25`, `clw*26`, `curet`, `lhv*25/26`, `mccambley`, `mcgarry`, `painter` (2022 CLR), `sweet_aaa`, `turnbulllhv` |
| Rows removed by the level gate | 164,755 |
| Rows that duplicate the Phillies logs | 30,229 |
| Internal duplicates (after the level gate) | 17,464 |
| Pitcher-keyed files | 85 (single pitcher or a team pitching pull) |
| **Batter-keyed team files** | `giants-of-rangers-of-24`, `marlins-of-24-25`, `nats-of-23`, `tigers-of-20-22`, `white-sox-of-25-26` (plus every hitter file and the `bdodgers` batting pull) — **`player_name` is the batter** |
| Governed union (regular season) | **1,219,975** pitches, 0 duplicate keys |

Consequence: a pitcher-season in the frame is one of four sampling situations (`row_frame`): a Phillies
season (complete), a dedicated player file (complete), a team pitching pull (complete), or incidental rows —
starts against the Phillies or at-bats against a hitter Kellen pulled (partial). 139 of the 405 population
pitcher-seasons are PARTIAL. That is a known, permanent property of the frame (DQ-14 WARN).

**Fitness for purpose**

| CDE | Completeness on RHP FF, 2018–26 | Fit? |
|---|---|---|
| `release_speed`, `pfx_z`, `release_spin_rate` | 99.76% jointly non-null | ✅ |
| `description` (swing/whiff) | 100% | ✅ |
| `delta_run_exp` | 100% on every file, every year | ✅ |
| `estimated_woba_using_speedangle` | PA-ending rows only (by design) | ✅ context only |
| `arm_angle` | NULL before 2025, 29% null in 2026 | ❌ not used (uc-pps-030 DQ-6 precedent) |

## 4 · The cohort, entity-locked

| Arm | MLBAM | How resolved | FF seasons in frame (≥50) | Affiliation note |
|---|---|---|---|---|
| Zack Wheeler | 554430 | prior UC (uc-pps-020) | 2018–2026 (9) | 2018–19 via `wheeler.parquet` (NYM) |
| Andrew Painter | 691725 | prior UC (uc-pps-030) | 2026 | AAA never graded (LV-1) |
| Alex McFarlane | 686934 | prior UC (uc-pps-029) | 2026 — **94 FF, THIN** | |
| Jhoan Duran | 661395 | prior UC (uc-pps-018) | 2022–2026 (5) | 2022–25 via `duran.parquet` (MIN) |
| Jonathan Bowlan | 680742 | prior UC (uc-pps-029) | 2025–2026 | 2025 via `bowlan.parquet` (KC) |
| Seranthony Domínguez | **622554** | **resolved this UC**: modal pitcher-keyed name, 4,008 PHI rows | 2018–2024 (5) | 2025–26 not graded (41 pitches vs PHI in 2026) |

## 5 · Premises stress-tested

| # | Premise (from the ask) | Verdict |
|---|---|---|
| P-1 | "At six, this is a cohort" | **Accepted with a caveat** — six arms but 23 graded pitcher-seasons; Wheeler alone is 9 of them. Ranking is by each arm's best and latest season, never pooled |
| P-2 | The profile UC defined `ff_elite_*_flag` | **False** — no such UC in either repo (G4) |
| P-3 | `nphl` might be Phillies-opponents-only | **False, in a more awkward way** — it's a hand-curated convenience sample incl. MiLB and hitter-keyed pulls (§3) |
| P-4 | "Which player not on the Phillies would most improve 2026's elite-FF share" implies a gap | **Inverted** — the Phillies own the #2 four-seam in the frame; the gap is depth (one arm), not quality |
| P-5 | The cohort is "elite-FF-caliber" | **Partly** — by the governed bar, only Bowlan 2026 is elite on both axes; Wheeler/Duran/Domínguez are results-elite, McFarlane shape-elite (thin), Painter neither |
| P-6 | Notebook subtitles (Wheeler, Painter ×3) | Reproduced and graded — report §6 |

## 6 · Carry-ins and external lookups (logged, never computed on)

| Item | Source | Use |
|---|---|---|
| Bowlan left 9/17 with a suspected oblique | client notebook, `September 2026.ipynb` cell 85 | scenario "Bowlan out" only, labelled carry-in |
| MLBAM 694819 = Jacob Misiorowski | Baseball Savant player page (web search) | display name only |
| Chadwick register (`pybaseball.playerid_reverse_lookup`) | **blocked at the proxy** | not used |
