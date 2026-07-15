# 04 — Data Model & Technical Lineage (data-architect + technical-lineage-builder) · uc-pps-018

## Model
**Grain:** pitch (one row per pitch), entity-locked and deduped on `(game_pk, at_bat_number, pitch_number)`.
**Dimension added at load:** `era` ∈ {MIN 2022, MIN 2023, MIN 2024, MIN 2025, PHI 2025, PHI 2026 1H} — derived from source file + `game_year`; the Twins/Phillies 2025 split rides on the source seam (verified in 02), not on a team column.
**Join strategy:** single fact frame; only join is the wOBA constants lookup on `game_year == Season` (many-to-one, validated non-null → no fan-out possible). No cross-domain joins → join-validator scope trivially satisfied.

## Lineage (column-level, source → receipt)
```
duran.parquet ─┐  filter: pitcher==661395, game_type=='R'
phils_2025 ────┼─ concat(common cols) → dedup(game_pk,ab#,pitch#) → +era → +wOBA weights
phils_2026 ────┘                │
                                ├→ nresults/get_stats(era)+process KPIs → dp_uc19_duran_era_trend.csv → report §results, fig era_trend
                                ├→ groupby(era,pitch_name)+whiff_rate  → dp_uc19_duran_arsenal_by_era.csv → report §arsenal, fig arsenal_evolution
                                ├→ [era==PHI 2026 1H] groupby(stand,pitch_name) → dp_uc19_duran_2026_arsenal_by_stand.csv → report §platoon, fig arsenal_map
                                ├→ [2026] nresults(month)              → dp_uc19_duran_2026_monthly.csv → report §month-by-month
                                ├→ putaway_rate(era_group,pitch_name)  → dp_uc19_duran_putaway_by_pitch.csv → report §new looks
                                ├→ [2026, CH] by stand + FF velo ref   → dp_uc19_duran_changeup_detail.csv → report §new looks
                                ├→ structural checks                   → dp_uc19_dq_scorecard.csv → 05
                                └→ source windows + manual carry-ins   → dp_uc19_freshness_manifest.csv → report caveats
```
Field-level mappings are unchanged from the dp_uc11 lineage (Statcast native fields → locked KPI functions); no transformation logic was added beyond the era label and the descriptive aggregates listed above. The build script (`dp_uc19_duran_first_half.py`) implements exactly this diagram — data-engineer scope.

**Traceability rule enforced:** every number and figure in the report resolves to one of the eight receipts above.
