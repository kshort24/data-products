# 01 · Strategy & Intake
**use-case-validator · source-system-profiler · domain-steward-proxy**

## Use case as submitted

> **Aaron Nola and Sandy Alcantara starting against one another** — *Aaron Nola against the Marlins.*
> value_stream = Phillies Offense · Level of Granularity = Phillies RHB with plate_apps similar to
> Nola against Miami RHB · kpis = Slash Line, wOBA, K Rates, Whiff, Chase, and Hard Hit Rate, Add
> Barrel Rate · data_viz = prose.
> What if the "batter" that Aaron Nola elicited in terms of offensive output by season [were] just a
> straight line across all years of this box plot — instead of the current format where he is called
> out as his own point for each of his own game_year level performances against MIA. Let's change
> that so it is just a constant. Same with Wheeler. Then highlight the individual Bryce Harper
> against Marlins in the Statcast era. [...] Sandy Alcantara has thrown more [pitches] to the
> Phillies offense in the Statcast era than [anyone]. Bryce Harper has faced him third most of any
> pitcher since 2015. The only other real competitor could be Max Scherzer or Jacob deGrom. [...]
> Take the description of this graph. Generate Business Intelligence. Show me a scatter plot at
> discrete season levels with the highlight on Aaron Nola against the Marlins. Facet Columns by
> Batter Stand. *(Python snippet supplied — concat of `nola` vs-MIA rows with `pos`, `nresults` +
> `whiff_rate` + `runs_created` merge, `rc_per_pa` derivation, `criteria = 15`, `px.box` spec.)*
> Deliverables: PDF report, fully governed package, explore an interactive dashboard.

## Validator disposition — **GO**, 0 blocking, 5 conditions

| # | Condition | Resolution |
|---|---|---|
| C-1 | Submitted `criteria = 15` conflicts with the house 50-PA floor | **Escalated to the human DPO at intake** (the AskUserQuestion gate). Ruling HD-1: floor = Nola's own minimum PA vs MIA, derived per grain (27 season / 11 L / 12 R). Deviation governed in `03_governance.md` |
| C-2 | "More pitches than anyone" / "third most" / "every year" are testable claims stated as facts | Treated as **premises to verify, not constraints to satisfy** — verdict table (P1–P5) leads the report. P2, P3-as-posed and P5 falsified or out-of-plane; both framings priced (uc-pos-008 rule) |
| C-3 | One prose sentence is garbled ("thrown more pitchers … than Sandy Alcantara") | Interpreted as *pitches … than anyone*; interpretation logged here, tested as P2 rather than assumed |
| C-4 | "Phillies RHB with plate_apps similar to Nola against Miami RHB" underdetermines the scatter population | Resolved as: stand-faceted player-season-stand grain, per-stand floor from HD-1; the Noles composite carries the opposing batter's stand. Career stand rows (262/434 PA) marked as the citable split |
| C-5 | `data_dictionary` referenced in the snippet is session-local to the DPO's notebooks, not governed | Labels re-declared explicitly in `dp_uc35_build_figures.py`; the snippet's joke label ("Player Name (ambiguous column!)") retained on the hover it belonged to |

## Source-system profiler — fitness for purpose

| CDE | Physical column | Fitness |
|---|---|---|
| `batter_id` / `pitcher_id` | `batter` / `pitcher` | ✅ MLBAM ids; entity locks 605400/645261/554430/547180 asserted against caches or mode-of-name |
| `player_name` | `player_name` | ⚠ **means "the Phillie of interest"** — batter on `pos`, pitcher on `pps` (receipted in `dp_uc35_player_name_semantics.csv`). No name authority for *opposing* pitchers → **O-10** |
| `opponent` | derived: `home_team`/`away_team` vs `inning_topbot` | ✅ batting team on a pitching frame = away if Top else home |
| `pa_result_event` / `description` / `type` | `events` / `description` / `type` | ✅ all values map to governed NON_PA / SWINGS / WHIFFS sets |
| `zone` (chase) | `zone` | ⚠ null rate receipted in DQ scorecard; O-2 null-zone convention inherited unchanged |
| `launch_speed` / `launch_speed_angle` | same | ✅ hard-hit ≥95; barrel `==6`; 2026 BIP `launch_speed_angle` null rate receipted (O-8 disclosure) |
| `bat_score` / `post_bat_score` (runs_created) | same | ✅ **100% complete** — DQ scorecard PASS |
| `stand` | `stand` | ✅ complete; the facet key |
| wOBA constants | `wOBA and FIP Constants.csv` | ✅ 2015–2026 rows present |

**Populations.**
`pos`/`pps` from `phils_2015–2026.parquet`, S/E excluded, R+postseason retained (kernel convention).
"Noles" = 2,672 pitches / 696 PA / 28 games (2015-08-23 → 2026-07-28). Wheeler-vs-MIA = `pps`
2020–2026 **+ `wheeler.parquet` 2017–2019 (NYM)** — coverage verified disjoint; `alcantara.parquet`
is **stale (max 2025-04-12)** and used for entity lock only, never for rates. Harper-vs-MIA = 401 PA
(2019–). PHI-vs-Alcantara = 2,278 pitches / 612 PA / 24 games (2018–).

## Domain steward — rulings applied

1. **SWINGS/WHIFFS/NON_PA lists** — notebook-ratified sets, inherited unchanged via the dp_uc34 kernel.
2. **`runs_created`** — approved notebook term with its own glossary + lineage block; transcribed verbatim. `rc_per_pa = runs_created / plate_apps` is the use case's derived KPI, computed from unrounded components.
3. **Constants over per-season points (HD-2)** — a *design* ruling, not a data ruling: the constant is the career aggregate at the entity grain; the per-season receipts still ship so nothing is hidden by the redesign.
4. **A composite batter is a valid analysis entity** (`SB-1`) but must never be phrased as a claim about any individual Marlin; report and dashboard hold that line.
5. **Game context** (Nola vs Alcantara, 2026-08-19, CBP) and the Scherzer/deGrom display names are **manual carry-ins** from the DPO's intake prose, logged in `dp_uc35_freshness_manifest.csv`.
6. **The 7/28 prior meeting** (game_pk 823838, MIA 1–0) was discovered in-frame during intake — both starters' lines receipted; it anchors the report's "rematch" framing without any external source.

## Window rule

No outcome-selected window in this UC — the frame is the full Statcast era on both sides, and the
only windows shown (per-season receipts) are complete calendar seasons. The 2026-vs-career contrast
for both starters is presented with both PA counts on every surface.
