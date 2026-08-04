# 04 — Engineering (Build)

**Layer 3 — Build** · UC #31 · `uc-pps-025` · build `dp_uc30`
**Agents:** `technical-lineage-builder` → `data-engineer`

---

## 4.1 `technical-lineage-builder` — column-level lineage

```
data/opponents/raley.parquet
  │  pitcher == 548384                      ── ENTITY LOCK (asserted)
  │  game_type == 'R'
  │  drop_duplicates(game_pk, at_bat_number, pitch_number)
  ▼
raley  (4,184 rows, pitch grain)
  │
  ├─ game_date ──▶ era      = Pre-TJ | Post-TJ   (rehab gap asserted empty)
  ├─ inning_topbot + home/away_team ──▶ pitching_team  ── asserts 0 PHI rows
  ├─ game_year ──▶ ⨝ wOBA and FIP Constants.csv (Season)  ── 1:1, no fan-out
  │
  ├─ pitch_name.notna() ──▶ tracked          (18 rows quarantined)
  │     ├─ release_pos_x, release_pos_z ──▶ RSA  = deg(atan2(z, |x|))
  │     ├─ release_pos_x, stand         ──▶ SLO  = |x − boxcenter(stand)|
  │     ├─ release_pos_x/z × pitch_name ──▶ RTD  = max pairwise · 12
  │     ├─ pfx_x, pfx_z (×12)           ──▶ arsenal movement
  │     └─ plate_x, plate_z, zone       ──▶ location, zone_rate_strict
  │
  ├─ description ──▶ SWINGS / WHIFFS / CALLED_STRIKE
  │     └──▶ whiff_rate · csw_rate · chase_rate · putaway_rate
  ├─ events     ──▶ get_stats → nresults (BA/OBP/SLG/wOBA/K%/BB%/HR%)
  ├─ type=='X' + launch_speed          ──▶ hard_hit_rate
  ├─ type=='X' + est_woba_speedangle   ──▶ xwobacon           [BIP ONLY]
  ├─ bat_speed / swing_length / miss_distance ──▶ tracking proxies  [2023+]
  └─ game_pk × inning × fld/bat_score × on_1b/2b/3b ──▶ outing_log → deployment

data/phillies/phils_2015..2026.parquet
  │  phillies_role=='pitching' & p_throws=='L' & game_type=='R'
  │  drop_duplicates(...)  ·  pitch_name.notna()
  ▼
lhp  (65,221 rows) ──▶ groupby(pitcher) ──▶ ≥300 pitches ──▶ 28 pitchers
  │     ├─ mean release_pos_x/z ──▶ RSA, SLO
  │     └─ centroid + SD (RALEY EXCLUDED) ──▶ RDI
  │
  └─ arm_angle (2025-26 only) ──▶ ⨝ RSA ──▶ calibration (r, slope, residuals)
```

**Every published number traces to exactly one receipt CSV.** Figures render only from quantities that also appear in a receipt.

---

## 4.2 `data-engineer` — implementation notes

**Artifact:** `dp_uc30_raley_acquisition_read.py` — the single place any number is computed.

### Governance-relevant implementation decisions

| Decision | Rationale |
|---|---|
| Locked KPI functions copied **byte-identical** from `dp_uc29` | Governance principle 2. Re-deriving them would silently fork the definitions |
| `rest_bucket` cast to `str` **at the caller**, not fixed in `get_stats` | `pd.cut` returns a Categorical; the locked `get_stats` ends in `.fillna(0)`, which raises on a Categorical key. The locked function is inherited verbatim and **must not be edited** — so the caller adapts. Commented inline |
| Coordinate convention **asserted at runtime**, build fails loudly if violated | Every sightline claim depends on it. An assumption this load-bearing does not get to be an assumption |
| Benchmark centroid computed **before** Raley's rows are appended | Prevents the subject from influencing the yardstick. Asserted in DQ |
| Untracked rows quarantined from usage/location, **retained** for PA outcomes | An automatic ball is a real ball for outcome purposes and not a pitch for mix purposes. Inherited from UC#30 O2 |
| RSA calibration is a **DQ gate**, not a footnote | If `|r| < 0.80` the build records a FAIL and RSA must not be published as an arm-slot proxy |
| Portable data-root resolution (env var → relative → sandbox mount → Windows path) | Runs unmodified on the sandbox and on Kellen's machine |
| `emit()` wrapper for every receipt | Guarantees a registered, named CSV per published table. New filenames only — no prior UC output is overwritten |
| `dp_uc30_headline.json` written at the end | Machine-readable handoff for the PDF renderer and the verification harness |

### Outputs

**21 CSV receipts** — `era_summary` · `season_log` · `arsenal_by_era` · `arsenal_post_tj` · `platoon` · `pitch_by_hand` · `count_usage` · `two_strike` · `lhp_release_benchmark` · `rsa_calibration` · `sightline` · `release_by_pitch` · `tracking_proxies` · `monthly_arc` · `outing_log` · `deployment` · `batter_sequence` · `rest_workload` · `damage_log` · `dq_scorecard` · `freshness_manifest`

**5 figures** (Phillies brand: red `#E81828`, navy `#002D72`) —
`fig1_release_benchmark` · `fig2_arsenal_movement` · `fig3_platoon_process` · `fig4_location_by_hand` · `fig5_deployment`

### Build log summary

```
entity lock          1 pitcher id, 1 name, p_throws = L
era partition        pre 3,162 + post 1,022 = 4,184  (rehab gap: 0 rows)
coordinate check     LHP +2.072 / RHP −2.079 · HBP LHH +1.915 / RHH −2.198
benchmark            28 Phillies LHP, 65,221 pitches, centroid excludes Raley
RSA calibration      r = 0.831 (n = 10)  →  PASS (gate ≥ 0.80)
untracked rows       18 quarantined
DQ scorecard         38 / 38 PASS
```

### Reproducibility

```bash
python dp_uc30_raley_acquisition_read.py    # rebuild receipts + figures
python dp_uc30_verification.py              # independent recompute (661 checks)
python dp_uc30_build_pdf.py                 # markdown → branded PDF
```

Data root override: `MLB_DATA_ROOT=/path/to/MLB/data/phillies`.
