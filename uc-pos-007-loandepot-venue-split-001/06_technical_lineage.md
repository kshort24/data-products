# 06 — Technical Lineage
## `uc-pos-007` / `dp_uc27` · Layer 3 · Agent: `technical-lineage-builder`

Column-level source → target for every number this product publishes. Implemented by
`dp_uc27_phillies_at_loandepot.py`; independently recomputed by `dp_uc27_verification.py`.

---

## 1. Pipeline stages

```
STAGE 0 — SOURCE
  data/phillies/phils_{2015..2026}.parquet      121 cols, ~34k rows/season
    └─ where phillies_role == 'batting'
    └─ where batter ∈ ROSTER (11 MLBAM ids)
  data/opponents/*.parquet                       ~114-121 cols, 30 files carry roster rows
    └─ where batter ∈ ROSTER
  wOBA and FIP Constants.csv                     Season, wBB, wHBP, w1B, w2B, w3B, wHR
                                                                              │
STAGE 1 — UNION                                                               ▼
  pd.concat(frames)                                              150,421 rows (roster only)
    └─ provenance snapshot → out/dp_uc27_source_provenance.csv
                                                                              │
STAGE 2 — DEDUP                                                               ▼
  drop_duplicates(['game_pk','at_bat_number','pitch_number'], keep='first')
    └─ removes 5.9-18.4% of Miami rows per hitter (see 05_ §2.2)
                                                                              │
STAGE 3 — DIMENSION JOIN                                                      ▼
  drop pre-existing weight cols, then merge constants on game_year == Season
    └─ many-to-one, row count invariant
                                                                              │
STAGE 4 — GOVERNANCE FILTERS (ordered, attributed)                            ▼
  4a  game_type == 'R'                                    −6,439
  4b  home_team ∈ MLB_TEAMS        (COMPETITION_LEVEL)    −7,172
  4c  game_pk ∉ IRMA_GAME_PKS      (DS-2 venue integrity)    −44
  4d  p_throws == 'R'                                    −39,531
    └─ audit → out/dp_uc27_exclusion_audit.csv            = 97,235 rows retained
                                                                              │
STAGE 5 — DERIVED DIMENSIONS                                                  ▼
  player          = batter → ROSTER
  venue           = 'loanDepot park' if home_team=='MIA' else 'All other MLB parks'
  park_era        = 'pre-reconfig' if game_year<=2019 else 'post-reconfig'
  bat_team        = home_team if inning_topbot=='Bot' else away_team
  miami_home_club = venue=='loanDepot park' AND bat_team=='MIA'
                                                                              │
STAGE 6 — AGGREGATION (panel() at each grain)                                 ▼
  get_stats  ⋈  hard_hit_rate  ⋈  barrel_rate  ⋈  ev90  ⋈  discipline
    all merged on the grain key, all reading the same filtered frame
                                                                              │
STAGE 7 — NEW KPIs                                                            ▼
  venue_delta()  → VD-1 signed deltas, VD-2 signal class, qualification gate
                                                                              │
STAGE 8 — RECEIPTS + FIGURES                                                  ▼
  24 CSVs, 5 PNGs → out/
                                                                              │
STAGE 9 — VERIFICATION (separate process, no shared code)                     ▼
  dp_uc27_verification.py re-reads STAGE 0, re-applies STAGE 4 from first
  principles, recomputes every headline via long-form event counting
    └─ 256 checks → out/dp_uc27_verification_results.csv
```

---

## 2. Column-level lineage for published KPIs

| Published KPI | Source columns | Transformation | Target receipts |
|---|---|---|---|
| `plate_apps` | `events`, `description` | count rows where `events ∉ {null, pickoff_1b}` | all panel CSVs |
| `at_bats` | `events` | PA minus BB/IBB/HBP/SF/SH | intermediate |
| `ba` | `events` | (1B+2B+3B+HR) ÷ at_bats | all panel CSVs |
| `obp` | `events` | (H + BB + HBP) ÷ PA | all panel CSVs |
| `slg` | `events` | (1B + 2·2B + 3·3B + 4·HR) ÷ at_bats | all panel CSVs |
| `ops` | derived | obp + slg | all panel CSVs |
| `woba` | `events`, `wBB..wHR`, `game_year`→`Season` | Σ event weights ÷ PA | all panel CSVs |
| `xwoba` | `estimated_woba_using_speedangle` | mean over populated rows | all panel CSVs |
| `hard_hit_rate` | `launch_speed`, `type`, `des` | count(`launch_speed ≥ 95` ∧ `type=='X'`) ÷ count(`type=='X'`) | all panel CSVs |
| `barrel_rate` | `launch_speed_angle`, `type`, `des` | count(`lsa == 6` ∧ `type=='X'`) ÷ count(`type=='X'`) | all panel CSVs |
| `ev90` | `launch_speed`, `type` | 0.90 quantile over `type=='X'` | all panel CSVs |
| `krate` / `bbrate` / `hr_rate` | `events` | event count ÷ PA | all panel CSVs |
| `chase_rate` | `zone`, `description` | swings on `zone>9` ÷ pitches with `zone>9` | discipline, panel CSVs |
| `whiff_rate` | `description` | whiffs ÷ swings | discipline, panel CSVs |
| `z_swing_rate` / `zone_rate_seen` | `zone`, `description` | in-zone swing share; in-zone pitch share | `discipline_venue.csv` |
| `pitches_per_pa` | `description`, `events` | row count ÷ PA | all panel CSVs |
| `bb_type` share | `bb_type`, `type`, `des` | per-type count ÷ BIP at grain | `bbtype_venue.csv` |
| **VD-1** | `venue_split` panel | Miami cell − Other cell, per KPI, per hitter | `venue_delta.csv` |
| **VD-2** | VD-1 outputs | `nanmean` of three scaled process deltas, then sign-agreement classification | `venue_delta.csv` |
| Arsenal usage / velo / movement | `pitch_name`, `release_speed`, `release_spin_rate`, `pfx_x`, `pfx_z`, `des` | group by `pitch_name`, mean + share | `alcantara_mix.csv`, `alcantara_recent_mix.csv` |

---

## 3. Cohort lineage — which frame feeds which claim

| Report claim | Cohort | Receipt |
|---|---|---|
| "`.720` OPS in Miami vs `.804` elsewhere" | A — all rows | `pooled_venue.csv` |
| "`.783` OPS / `.391` xwOBA as visitors" | B — `¬miami_home_club` | `pooled_venue_visitors.csv` |
| "863 of 1,901 Miami PA are home-club" | A vs B row difference | `miami_home_club.csv` |
| "Realmuto `.371` wOBA as a visiting Phillie" | B, hitter grain | `venue_split_visitors.csv`, `miami_home_club.csv` |
| "Park-era effect vanishes for visitors" | A and B, era grain | `park_era.csv`, `park_era_visitors.csv` |
| "`.423` xwOBA vs Alcantara in Miami" | C — `pitcher == 645261` | `alcantara_venue.csv` |
| "Slider `.496` xwOBA, 55.2% hard-hit" | C, pitch grain | `alcantara_mix.csv` |
| "Four-seam 24.6% → 16.2%" | C career vs C 2025–26 | `alcantara_mix.csv`, `alcantara_recent_mix.csv` |
| Per-hitter VD-1 / VD-2 table | A, hitter grain | `venue_delta.csv` |
| Persona-card figures | A, B, C | read directly from the CSVs at card-build time |

**No claim in the reader report or persona card is hard-coded.** The persona card reads every
number from `out/*.csv` at build time, so it cannot drift from the build.

---

## 4. Reproducibility

| Property | Status |
|---|---|
| Deterministic | Yes. File discovery uses `sorted(glob(...))`; `keep='first'` on dedup is therefore stable |
| Portable | Yes. Data root resolves in order: `argv[1]` → `$MLB_DIR` → script directory → the absolute Windows path. Runs on both the sandbox mount and Kellen's machine |
| Idempotent | Yes. Re-running overwrites only `out/dp_uc27_*` files; no prior UC output is touched |
| Runtime | ~12 s single-threaded, 30 parquet reads |
| Verification independence | The harness shares **no imports** with the build. It re-reads the parquet layer, re-applies the filters, and recomputes slash lines by long-form event counting rather than the merge-chain kernel |

**Command sequence to reproduce end to end:**

```bash
python dp_uc27_phillies_at_loandepot.py <MLB_DIR> <MLB_DIR>/out   # build + receipts + figures
python dp_uc27_verification.py           <MLB_DIR> <MLB_DIR>/out   # 256 checks, exit 0 on success
python dp_uc27_build_pdf.py              <PACKAGE_DIR>             # 9-page reader PDF
python dp_uc27_build_persona_card.py     <PACKAGE_DIR>             # 1-page hitting card
```
