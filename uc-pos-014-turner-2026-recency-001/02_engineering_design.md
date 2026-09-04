# 02 · Engineering Design — `uc-pos-014-turner-2026-recency-001`

**Department:** Engineering Design · **Agents:** `source-system-profiler`, `data-architect`,
`eda-agent`, `join-validator`, `kpi-calculator` (specs in `03`), `metadata-mapper`
**Gate:** Layer 2 must close before build. **Status: CLOSED — model approved, joins validated.**

---

## 2.1 · Source profile — fitness for purpose

Two physical sources with **asymmetric schemas**. This is the single most important design fact in the build.

| | `data/opponents/turner.parquet` | `data/phillies/phils_{2023..2026}.parquet` |
|---|---|---|
| Rows (subject) | 15,279 | 9,759 |
| Columns | **93** | **123** |
| Coverage | 2015-08-21 → 2022-10-15 | 2023 → **2026-09-02** |
| Teams | WSN (2015–21), LAD (2021–22) | PHI |
| `game_type` | R 14,498 · D 417 · L 175 · W 152 · F 37 | R 9,401 · D 218 · L 107 · F 33 (S/E dropped) |
| Entity | single `batter` id, single `player_name` | filtered to `batter == 607208` |
| Refreshed | 2026-04-24 (static, historical) | **2026-09-03 14:45** |

**The 30 PHI-only columns** include `bat_speed`, `swing_length`, `attack_angle`, `attack_direction`,
`arm_angle`, `hyper_speed`, `estimated_slg_using_speedangle`, `age_bat`, win-expectancy fields, and
`api_break_*`. Consequences, all designed for rather than discovered late:

- **Bat tracking is structurally 2024+ and PHI-only.** Coverage on *swings* is 91.2% / 95.1% / 96.1% in
  2024/25/26 — stable enough for cross-year comparison, and the pre-2024 rows are NULL by sensor
  boundary (`uc-pos-009`), never zero.
- **`attack_angle` is empty in 2024** even though the column exists. A second, later sensor boundary
  inside the same column family. Asserted as DQ rule R-14 rather than assumed.
- **No career-spanning swing-measurable comparison is possible.** The report says so; it does not
  quietly chart a flat line for 2015–2023.

### Column-level fitness against the requested CDEs

| CDE family | Physical columns | Null rate (2026) | Fit |
|---|---|---|---|
| Results (slash, wOBA) | `events`, `type`, `game_year` + `wOBA and FIP Constants.csv` | 0% at **PA grain** | **FIT** |
| Contact quality | `launch_speed`, `launch_angle`, `launch_speed_angle`, `bb_type` | 0% on 2026 BIP; `bb_type` complete | **FIT** |
| Expected outcomes | `estimated_woba_using_speedangle` | populated on PA-terminating rows only | **FIT, with a grain caveat (O-4)** |
| Approach | `description`, `zone`, `balls`, `strikes`, `pitch_number` | `zone` 0.18% NULL → **defect D-7** | **FIT after the `_fix`** |
| Spray | `hc_x`, `hc_y` | 0% on 2026 BIP | **FIT via the O-7 remediation** |
| Measurables | `bat_speed`, `swing_length`, `attack_angle` | see above | **PARTIAL — 2024+ / 2025+ only** |
| Platoon | `p_throws` | 0% | **FIT** |
| Pitch identity | `pitch_type` | 4 rows unmapped in 2026 → `other`, never dropped | **FIT** |

**Grain-relative completeness (D-1, `uc-pps-028`) is enforced.** `events` is tested at PA grain and
`launch_speed` at tracked-BIP grain. Testing either at pitch grain produces a spurious FAIL, which is
exactly the defect that UC caught.

---

## 2.2 · Data model

**Grain:** one row per pitch, keyed `(game_pk, at_bat_number, pitch_number)`. 0 duplicates across the
union of both sources — verified, not assumed (R-2).

```
                 ┌──────────────────────────────┐
 turner.parquet  │  subject_pitch_log            │   wOBA and FIP Constants.csv
 (2015-2022) ───▶│  grain: pitch                 │◀── grain: season (1 row / Season)
 phils_{yr}      │  PK (game_pk, ab_no, pitch_no)│    join: game_year = Season
 (2023-2026) ───▶│  + src, bat_team, era, window │    cardinality: many-to-one
                 └──────────────┬────────────────┘
                                │  derive
        ┌───────────────────────┼────────────────────────┬─────────────────┐
        ▼                       ▼                        ▼                 ▼
   pa_atom (terminal      bip_atom (type=='X')     swing_atom            zone_atom
   event rows)            + tracked_bip subset     (description ∈ SWINGS) (zone notna)
        │                       │                        │                 │
        └──── results / wOBA ───┴── contact quality ─────┴── approach ─────┘
```

**Derived, never carried in:**

| Field | Derivation | Why not a carry-in |
|---|---|---|
| `bat_team` | `away_team` when `inning_topbot=='Top'`, else `home_team` | Turner was traded **mid-2021**; a roster carry-in would mislabel 1,044 LAD rows as WSN |
| `era` | `bat_team` with `WSH→WSN` | same |
| `window` | date bands on `game_date` | declared at intake (`01` §1.2), before results were seen |
| `pitch_group` | `PITCH_GROUP` map, unmapped → `other` | inherited verbatim from `dp_uc18`; `other` is retained, never dropped |
| `loc_x`/`loc_y` | `HC_SCALE * (hc_x − 125.42)`, `HC_SCALE * (198.27 − hc_y)` | O-7 remediation; convention **asserted** at build (R-7), not assumed |

**Filters, applied in a fixed order:** entity lock → drop `game_type ∈ {S,E}` → de-duplicate on the
pitch key → (for every rate) `game_type == 'R'`.

---

## 2.3 · `join-validator` — the two joins that could go wrong

| Join | Risk | Result |
|---|---|---|
| `turner.parquet` ∪ `phils_*` | **Row duplication** if a game appears in both (it cannot — disjoint date ranges — but a schema change could break that) | 0 duplicate pitch keys across the union. Date ranges verified disjoint: max opponent date 2022-10-15 < min PHI date 2023 |
| pitch log × wOBA constants | **Fan-out** if the constants file ever carried >1 row per Season | many-to-one confirmed; 0 seasons missing weights (R-8); row count unchanged pre/post join |
| window labels | **Overlap or gap** — the classic partition bug | `W1 + W2 + W3 == 602 PA == season PA` (R-22), asserted every run |
| platoon split | same | `L + R == 602 PA` (R-23) |

No union fan-out (the `uc-pos-007` trap) is possible here because the two sources are disjoint in time
and the subject is a single entity.

---

## 2.4 · `eda-agent` — what the exploration changed about the design

1. **Two baselines, not one.** His 2020–21 peak and his 2023–25 Phillies norm are different profiles
   (damage-driven vs contact/BABIP-driven). A single "career average" comparator would have hidden the
   most important structural fact about 2026, so the design carries **both** reference pools.
2. **The bat-speed trap.** August bat speed (69.2) is 1.6 mph below July and reads as a decline. Against
   the 2023–25 norm (69.7) it is inside noise. The EDA pass caught this, which is why **ST-1 was added
   to the design** — every headline window shift is priced against *two* baselines, one of which is
   well-powered. Without it, the report would have shipped a false mechanism.
3. **The popup signal.** 15.2% popup rate in the recent window was not in the requested CDE list and was
   surfaced by the batted-ball profile. It is the only measure that clears the noise bar, so the model
   promotes `pu_rate` from a supporting field to a headline KPI.
4. **September is 9 PA.** Confirmed at design time, which is why calendar months are a *supporting* cut
   and the three declared windows are the *primary* one.

---

## 2.5 · `metadata-mapper` — physical → business term

| Physical | Business term | Mapping | Owner |
|---|---|---|---|
| `events`, `type` | Plate Appearance / At Bat / Hit / Ball In Play | **exact** | Business Glossary (approved) |
| `estimated_woba_using_speedangle` | xwOBA (per PA) **or** xwOBAcon (averaged over BIP) | **ambiguous — resolved by grain**, see `03` O-4 | DPO ruling inherited from `uc-pps-025`/`uc-pps-028` |
| `launch_speed ≥ 95` | Hard-Hit | exact, denominator disputed (**O-8**) | open |
| `launch_speed_angle == 6` | Barrel | exact | approved |
| `zone < 10` | In Zone | exact; **`zone` NULL handling disputed (D-7)** | opened by this UC |
| `bat_speed` | Swing Speed | exact, 2024+ | approved |
| `attack_angle` | Attack Angle | exact, **2025+** | approved |
| `hc_x`,`hc_y` → `loc_x`,`loc_y` | Hit Direction / Pull | **derived (PA-L1)** — provisional | pending DPO ratification |

Unmapped: 4 pitch rows with an unrecognised `pitch_type` in 2026 → bucketed `other`, surfaced in every
pitch-group table rather than silently dropped.

---

*Gate decision: **APPROVED for build.** Model, joins, and derivations signed off by `data-architect`
2026-09-03. Two design changes were forced by EDA (ST-1 dual baselines; `pu_rate` promoted to headline).*
