# 04 — Engineering (Build)

**Department:** Engineering · **Agents:** `technical-lineage-builder`, `data-engineer`
**Layer 3 verdict:** ✅ complete — 19 CSV receipts + 4 figures, all new files, nothing overwritten

---

## 4.1 `technical-lineage-builder` — column-level lineage

```
data/opponents/kilian.parquet  (1,271 rows post-filter)
  │
  ├─ FILTER  pitcher == 668873 ∧ game_type == 'R'        [ENTITY LOCK — asserted]
  ├─ DEDUP   (game_pk, at_bat_number, pitch_number)      [0 removed]
  ├─ COERCE  27 numeric columns via to_numeric(errors='coerce')
  ├─ DERIVE  era_tier = 2026 ? '2026 SF (relief)' : '2022-24 CHC (start)'
  └─ JOIN    wOBA and FIP Constants.csv  ON game_year = Season   [left, 1:1]
     │
     ├── P1 FULL (n=736 / 535) ────────────────────────────────────────┐
     │     get_stats → nresults ────────────► era_summary, season_log,  │
     │                                        platoon, batter_sequence, │
     │                                        monthly_arc              │
     │     events == 'home_run' ───────────► damage_log                │
     │     groupby game_pk + entry state ──► outing_log, deployment    │
     │                                                                 │
     ├── P2 TRACKED (pitch_name notna, n=728) ────────────────────────┤
     │     groupby pitch_name ─────────────► arsenal_by_era,           │
     │                                        arsenal_2026,            │
     │                                        pitch_by_hand            │
     │     count_state × stand ────────────► count_usage               │
     │     zone <= 9 / n ──────────────────► zone_rate_strict          │
     │     plate_x sign → h_side ──────────► slider_finish       [NEW] │
     │     plate_z vs sz band → v_third ───► fastball_elevation  [NEW] │
     │                                        slider_vertical_half     │
     │                                                                 │
     └── P3 BIP (type == 'X', n=118) ─────────────────────────────────┘
           launch_speed ─────────────────► avg_ev, hard_hit_rate
           estimated_woba_using_speedangle ─► xwobacon  [BIP-ONLY, O1 hardened]

  P1 ⊕ P2 per KPI ──────────────────────► role_conversion_delta  [NEW]
```

### Transformation notes worth carrying forward

| Transformation | Logic | Why it is recorded |
|---|---|---|
| `hb_in = −pfx_x × 12` | Sign flipped so arm-side run reads **positive** for a RHP | Raw `pfx_x` is glove-side-positive; publishing it unflipped would invert every movement statement |
| `ivb_in = pfx_z × 12` | Feet → inches, already gravity-corrected | — |
| `h_side` | `plate_x > 0.15` glove / `< −0.15` arm / else middle | ±0.15 ft dead zone prevents a pitch on the centreline being forced to a side |
| `v_third` | Per-pitch thirds of `sz_bot..sz_top` | **Batter-height normalised** — a league-average box would bias against tall/short hitters |
| `xwobacon` | mean over `type=='X'` only | O1 hardening; the locked `get_stats.xwoba` is computed but **never published** |
| `avg_ev` | mean `launch_speed` over `type=='X'` only | **O3** — `launch_speed` is populated on 114 foul rows; omitting the filter reads ~6 mph low |
| `count_state` | `strikes==2` → two strikes; `0-0`; `balls>strikes` → behind; else ahead/even | Two-strike takes precedence so the putaway population is unambiguous |
| Entry state | first row per `game_pk` by `(at_bat_number, pitch_number)` via `.head(1)` | **`groupby().first()` was rejected** — it returns the first *non-null* value per column independently, which fabricated an impossible entry state (35 entries at 0 outs with runners on). `.head(1)` returns the actual row |

That last row is a genuine near-miss: an early exploratory pass using `.first()` reported 36 of 45 entries with inherited runners. The true figure is **13 of 45**. Had it survived, the manager section would have described him as a mid-inning fireman, which he is not.

---

## 4.2 `data-engineer` — implementation

**Artifact:** `dp_uc29_kilian_acquisition_read.py` (~950 lines). Implements the 02 blueprint exactly; **no logic was designed here**.

**Portability:** data root resolves through `MLB_DATA_ROOT` env var → relative `./data/phillies` → sandbox mount path → absolute Windows path. Runs unmodified on both the sandbox and Kellen's machine.

**Locked-function discipline:** the eight inherited KPI functions were copied byte-identical from `dp_uc28_painter_vs_orioles.py`. **When a defect was found in `chase_rate()` (O2), the function was still not modified** — a separate `zone_rate_strict()` was added and the report publishes that. This is the same pattern `uc-pps-021` used for `xwobacon`, and it keeps the inherited line stable across UCs at the cost of carrying an open item.

**Output discipline:** all files written to `./out/` with the `dp_uc29_` prefix. No prior UC's outputs are touched.

### Receipts produced

| # | File | Contents |
|---|---|---|
| 1 | `dp_uc29_era_summary.csv` | Current vs prior era, outcomes + process |
| 2 | `dp_uc29_season_log.csv` | Per-season, 2025 gap visible as absence |
| 3 | `dp_uc29_arsenal_by_era.csv` | Usage/velo/spin/IVB/HB/ext/arm by era × pitch |
| 4 | `dp_uc29_arsenal_2026.csv` | 2026 arsenal with outcomes |
| 5 | `dp_uc29_role_conversion_delta.csv` | **NEW KPI** — 10 KPIs, both denominators |
| 6 | `dp_uc29_platoon.csv` | vs LHH / vs RHH |
| 7 | `dp_uc29_pitch_by_hand.csv` | Pitch × hand outcome matrix |
| 8 | `dp_uc29_count_usage.csv` | Usage by count state × hand (tracked pop) |
| 9 | `dp_uc29_slider_finish.csv` | **NEW KPI** — Slider Finish Rate |
| 10 | `dp_uc29_fastball_elevation.csv` | **NEW KPI** — Fastball Elevation Rate |
| 11 | `dp_uc29_slider_vertical_half.csv` | Slider by vertical half vs RHH |
| 12 | `dp_uc29_fps_by_hand.csv` | First-pitch strike rate by hand |
| 13 | `dp_uc29_damage_log.csv` | All 5 home runs with location + count |
| 14 | `dp_uc29_outing_log.csv` | All 45 outings: pitches, BF, entry, rest |
| 15 | `dp_uc29_deployment.csv` | Entry inning × score state × inherited |
| 16 | `dp_uc29_batter_sequence.csv` | Performance by batters-faced bucket |
| 17 | `dp_uc29_monthly_arc.csv` | Within-season trend |
| 18 | `dp_uc29_dq_scorecard.csv` | 32 DQ checks |
| 19 | `dp_uc29_freshness_manifest.csv` | Source/window/fitness receipts |
| F1 | `dp_uc29_fig1_arsenal_movement.png` | Movement map, prior vs current |
| F2 | `dp_uc29_fig2_role_conversion.png` | Conversion deltas |
| F3 | `dp_uc29_fig3_location_damage.png` | SFR + FER damage maps |
| F4 | `dp_uc29_fig4_deployment.png` | Deployment + leash |

**Figure discipline:** Phillies brand (red `#E81828`, navy `#002D72`). Every figure cites its source CSV in the footer, and **every panel prints its own denominator** — the FER panel was rebuilt mid-session after review found it labelling pitch counts beneath bars computed on balls in play.

### In-build assertions (blocking — the script will not produce output if these fail)

```python
assert d.pitcher.nunique() == 1 and d.pitcher.iloc[0] == KILIAN   # entity lock
assert d.game_type.unique().tolist() == ["R"]                      # regular season
assert not d.duplicated([...]).any()                               # dedup
assert 2025 not in d.game_year.unique()                            # true gap intact
```

---

## 4.3 Handoff to Quality

Delivered to `data-quality-engineer` and `certification-agent`:
- the build script and its 19 receipts + 4 figures
- an in-build DQ scorecard (32 checks)
- a freshness manifest recording all four source tiers including the two absent ones

**Not delivered, by design:** any narrative claim. The report was written *after* certification returned, from the receipts — not alongside the build.
