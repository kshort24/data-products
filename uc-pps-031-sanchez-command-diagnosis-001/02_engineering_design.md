# 02 · Engineering Design — `uc-pps-031`

Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier`

## 1 · Data model

```
phils_2021..2026.parquet  (both phillies_role values, game_type == 'R', dedup PITCH_KEY)
        │  + wOBA weights by season (Section B, verbatim)
        │  + derived: season (2021-22 merge), half (<= 07-13), month, region (SZ-0), sdist, is_swing
        ▼
  ALL  ─────────────► league controls (all pitchers / LHP) by season × half
   │   ─────────────► PN-1 cohort (pitchers ≥200 pitches in both years)
   │   ─────────────► starter distribution (first pitcher per game_pk × inning_topbot)
   │   ── ZC-1 ─────► common-rail frame (2026 rails by batter, inner join)
   ▼
  CS = ALL[pitcher == 650911]  ──► season / half / month / start / stand / pitch / count panels
```

One frame, one grain (pitch). Every rate is computed with a `(level, df)` function; there are no pre-aggregated
joins, so there is nothing to fan out.

## 2 · Joins (join-validator)

| Join | Keys | Cardinality | Check |
|---|---|---|---|
| wOBA weights | `game_year` → `Season` | m:1 | row count unchanged (asserted by construction: left join on a unique key) |
| ZC-1 rails | `batter` → rails | m:1 (rails unique by batter; mode resolves the 18 two-valued batters) | inner, so coverage is **reported** (2024 64%, 2025 78%, 2026 100%) |
| Starter merge | `game_pk, inning_topbot, pitcher` | m:1 | 2026 subject starts = 31 asserted |
| Panel merges | `level` | 1:1 | all left joins onto `nresults` |

## 3 · EDA findings (eda-agent)

1. **Season premises diverge from in-season ones.** Chase rose for the season but fell after the break. This drove the two-grain design.
2. **The league's zone numbers dropped in 2026** (in-zone .503 → .465). This led to the rail audit, which found O-18.
3. **2026 `sz_top` is constant per batter.** This became ZC-1.
4. **Native peer netting erases the finding; common-rail netting restores it.** Low-zone pitchers were affected less by the lower top. PN-1 now ships on both bases.
5. `player_name` is the batter on batting-role rows. The PN-1 cohort receipt labels opponents as "name not in log (O-10)".
6. The edge band is flat for Sánchez in every window, so "near the edge" and "near the shadow" diverge.
7. Misses moved: the low share fell and the glove-side and high shares rose after the break (SZ-5).
8. The 2025 second half was his best shadow-miss half on record (.321). 2026 is compared against a peak.
9. March 2026 is one start (87 pitches); it is labelled everywhere it appears.

## 4 · Metadata map (metadata-mapper)

| Physical | CDE / term | Notes |
|---|---|---|
| `plate_x`, `plate_z` | Pitch location | catcher's view; −x = 3B side (asserted via HBP sign) |
| `sz_top`, `sz_bot` | Zone rails | **2026 = per-batter constant (O-18)** |
| `zone` | Statcast zone attribute | `<= 9` in-zone (kernel); 1 null |
| `description` | Pitch result | SWINGS list, Baseball Functions cell 21 |
| `events` | PA outcome | `walk` only in `bbrate` (O-14, 0 IBB here) |
| `balls`, `strikes` | Pre-pitch count | CL-1 |
| `pitch_number` | Pitch of PA | FPSR |
| `pitch_name`, `stand`, `p_throws` | Dimensions | |
| `estimated_woba_using_speedangle` | xwOBA (PA grain) | per uc-pps-030 finding |
| `launch_speed`, `launch_speed_angle`, `type` | Contact | kernel only |
| `game_pk`, `at_bat_number`, `pitch_number` | PITCH_KEY | dedup |
| `batter` | Rail key | ZC-1 |
| `inning_topbot`, `inning` | Starter derivation | |
| `pitcher`, `player_name` | Entity | name valid only on pitching-role rows |
| `arm_angle` | — | **unmapped** (WARN, not used) |

## 5 · DQ rules requested (to dq-rule-definer)

Entity lock, dedup, R-only, anchor, location completeness, zone completeness, starts, sign rule, region partition,
edge-twin equality, rail constancy, geometric/attribute agreement, PN-1 cohort size, ZC-1 coverage, the 2021-22 flag,
no rate on a zero denominator, arm_angle. See `05` §1.

## 6 · Dashboard spec (dashboard-specifier)

- **Controls:** Window (2025 · 2026 1H · 2026 2H · 2026) · Compare (2025 · 2026 1H · 2025 2H) · Batter (both/L/R) · Pitch (all/SI/CH/SL).
- **Tiles:** pitches, PA, BB%, in-zone, chase, ahead, Edge Rate, Shadow Miss, Chase Beyond, whiff. Each shows its delta vs the compare window. Governed tiles have a navy top border; new ones red.
- **Shadow map:** tracked pitches coloured by SZ-0 region; zone plus rounded shadow outline; modes all / missed / chased.
- **Chase-beyond bars:** four halves with league ticks. **Trend:** 2026 monthly for a chosen metric vs the 2025 season line.
- **Tables:** premise verdicts, 2026 start log.
- **Failure mode stated in the header:** a raw 2025→2026 zone delta is not rail-controlled. The page tells the reader where the controlled number lives.
- **Hygiene:** no CDN, no fetch; the payload is embedded; works at 390 px.
