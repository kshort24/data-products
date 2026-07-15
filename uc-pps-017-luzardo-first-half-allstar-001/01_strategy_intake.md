# 01 — Strategy & Intake · uc-pps-017 (UC #19)

## use-case-validator — gap report

| # | Check | Class | Finding | Resolution |
|---|---|---|---|---|
| 1 | Outcome question defined | — | "Assess Luzardo's first half behind the All-Star nod: results first, then drivers, then persona actions" | Clear. GO |
| 2 | Personas named | — | Manager, pitching department, Luzardo, catcher | Mapped to KPI views in 02 |
| 3 | Deliverable style | Non-blocking | "Scouting-report style, or a different product if better" | DPO chose full-org retrospective (Marsh UC #18 shape) — adapted advance-report template |
| 4 | Official ERA / W-L requested implicitly ("high-level stats") | **Blocking risk** | Pitch log cannot compute earned runs or decisions | Substituted RA9 (on-mound score deltas) + FIP, both labeled reconstructions; report states official ERA is not published. Accepted by DPO |
| 5 | All-Star selection verifiability | Non-blocking | Not derivable from pitch log | Logged as user-provided manual carry-in in freshness manifest |
| 6 | 2025 vs 2026 window asymmetry | Non-blocking | Full season vs first half | Rate-stat comparisons only; asymmetry flagged in report warning box |

**Gate decision: GO** (one blocking risk resolved by substitution, all else non-blocking).

## source-system-profiler — fitness for purpose

- **Entity lock:** `pitcher == 666200` (Jesús Luzardo). Verified single id across both season files; no name-based filtering (Nola/"Nolan Hoffman" rule).
- **2026:** `data/phillies/phils_2026.parquet` — 1,836 R-game pitches, 19 starts, 2026-03-29..2026-07-09. Cache fresh through 2026-07-12 (T-1). Fit.
- **2025:** `data/phillies/phils_2025.parquet` — 3,013 R-game pitches, 32 starts, full season. Fit as comparison base.
- **CDE completeness (pitch grain):** pitch_name / release_speed / plate_x / plate_z / zone / description / stand / fielder_2 / n_thruorder_pitcher / bat_score / post_bat_score all 1.000 non-null. `events`, `woba_value`, `woba_denom` ≈ 0.25 non-null — expected: populated only on PA-terminal pitches. Fit.
- **Known gaps:** no earned-run, no win/loss, no league-wide (non-Phillies) benchmark population in local caches → staff-internal benchmark used instead; caveated.

## domain-steward-proxy — context carried in

- Luzardo acquired by trade ahead of 2025 (first Phillies season = 2025 → clean YoY base).
- 2026 All-Star selection (first career) — user-provided.
- Catcher ids resolved from the data itself (batter-row name lookup), not hand-keyed: 592663 → Realmuto, J.T.; 665561 → Marchán, Rafael.
