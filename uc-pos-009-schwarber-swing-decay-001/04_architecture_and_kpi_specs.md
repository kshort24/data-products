# 04 — Architecture & KPI Specifications

**Layer 2 — Design** · Department: Engineering (Design)
**Agents:** `data-architect` · `kpi-calculator` · `eda-agent`
**Use case:** `uc-pos-009-schwarber-swing-decay-001` · **Build:** `dp_uc32`

> **Governance principle 2 — no pipeline build without approved specs.** Every KPI below was specified (plain language → formula → grain → population → CDEs → edge cases) before it appeared in any output.

---

## 1. `data-architect` — the model

### 1.1 The grain problem, and the decision that resolved it

The DPO supplied a working KPI block at grain `player_name × game_year × stand`. **That grain cannot answer the question asked.** "He has lost pop *as the season has progressed*" is an intra-season claim; `game_year` collapses the season to a point.

Three candidate chronological grains were considered:

| Option | Design | Verdict |
|---|---|---|
| **Calendar month** | `game_year × month` | **Adopted as secondary.** Intuitive, but months have unequal BIP (10 to 61 in 2026) so month-to-month comparison is confounded by sample size |
| **Rolling window over balls in play** | ordered BIP index, window = 60 | **Adopted as primary visual.** Constant denominator, no calendar artefacts, reveals the shape of the change rather than bucketing it |
| **Two-phase split at the BIP midpoint** | order BIP, split at index ⌊n/2⌋ | **Adopted as primary statistical exhibit.** Equal weight on both sides by construction (120 vs 122), and every metric gets one clean comparison |

**All three ship.** They answer the same question at three resolutions and the report states where they agree.

**Design rule established:** *when a consumer asks about change over a season, the split must be data-driven (equal evidence weight), not calendar-driven (equal time).* A calendar split at the All-Star break would have put 156 BIP on one side and 86 on the other, and the resulting delta would have been partly an artefact of denominator size.

### 1.2 Logical model

Three layers, one physical grain.

```
L0  PITCH SPINE (physical)     one row per pitch
    key: game_pk × at_bat_number × pitch_number
    filter: batter == 656941, game_type == 'R'
    24,891 rows
      |
      +-- derived flags: is_swing, is_bip, ss_flag, ideal_flag,
      |                  fast_swing, squared_up, aa_fit, contact_depth,
      |                  bt_measured, plate_speed
      |
L1  ANALYTICAL CUTS (logical)  no new grain, only groupings
      season | month | phase | rolling window | pitch_group | velo_band
      | la_bucket | count_state | hit_direction | aa_bucket
      |
L2  PUBLISHED RECEIPTS         24 CSVs, one grain each, declared in 03
```

**Everything aggregates from L0.** There is no intermediate materialised table, therefore no opportunity for two receipts to disagree about the underlying population — a class of defect that has bitten this repo before. DQ-15 and DQ-16 assert the totals reconcile.

### 1.3 Join strategy — and why there is almost none

**Deliberate design choice: this product joins two things only.**

| Join | Keys | Cardinality | Fan-out risk |
|---|---|---|---|
| `schwarber.parquet` ⊎ `pos` (concat, not join) | — | 11,449 + 13,442 | **Zero overlap** — sources are year-disjoint (2015–21 vs 2022–26). Verified: 0 duplicates dropped |
| KPI blocks merged onto the season/phase spine | grouping keys | 1:1 by construction | Left-merge onto a spine built by the same `groupby` |

No player-to-player join, no lineup reconstruction, no external cache, no manual carry-in. **The fan-out and grain-drift failure modes that dominated `uc-pos-007` and `uc-pos-008` are structurally absent here.** Join validation (05 §3) is correspondingly short — and that is a design outcome, not an oversight.

### 1.4 Evidence-window architecture

The most important structural feature. Three windows coexist in one table:

| Window | Span | Fields | Rows in scope |
|---|---|---|---|
| Full career | 2015–2026 | results, EV, LA, barrel, sweet spot, discipline | 24,891 pitches |
| Bat tracking | 2024–2026 | `bat_speed`, `swing_length` | 3,349 measured swings |
| Swing path | 2025–2026 | `attack_angle`, `attack_direction`, `swing_path_tilt`, `intercept_*` | 2,141 measured swings |

**Architectural enforcement:** `bat_tracking_block()` carries the coverage denominators (`bt_swings`, `aa_swings`) into every output row and applies a suppression pass that nulls nine columns wherever the denominator is zero. A window violation cannot reach a receipt without tripping DQ-10/DQ-11.

---

## 2. `eda-agent` — findings that shaped the design

Run before the KPI specs were frozen.

| # | Finding | Design consequence |
|---|---|---|
| E-1 | `bat_speed` coverage is **0.0%** in 2023 for this batter, not "limited" as the intake note stated | Report corrects the DPO. Verification check V-20 pins it |
| E-2 | Swing-path fields exist from 2025 — the intake was speculative and **the data is there** | Swing path promoted from "if possible" to a full report section (§4) |
| E-3 | Season-level 2026 looks **normal**, not alarming: SLG .518, ISO .276, 46-HR pace | Report opens by pricing the baseline honestly (§1) before diagnosing. Prevented an overstated narrative |
| E-4 | Monthly barrel rate falls 26.3 → 12.1 → 8.9 (May→Jul) while monthly bat speed is flat (74.1 → 74.1 → 74.4) | **Identified the dissociation that became the central finding.** Drove the two-panel Fig 2 design |
| E-5 | Sweet-spot % **rose** across the decline | Drove the SW-2 spec and the SW-8 Damage-Band Rate. Became the report's metrological finding |
| E-6 | Mean contact depth in Phase A (33.79 in) exceeds the **2025 season mean** (31.98 in) | Forced the honest caveat: Phase A was the anomaly. Prevented a false "he lost extension" conclusion |
| E-7 | Only 5 Phillies LHB have measured bat tracking in 2026 | Peer framing demoted to secondary; percentiles labelled as descriptive, not statistical |
| E-8 | Statcast parquet uses nullable extension dtypes; masking raises `TypeError` | `coerce_numeric()` added as hop 3 |

---

## 3. `kpi-calculator` — specifications

Each spec: **plain language → formula → grain → population → CDEs → edge cases**. Locked KPIs are inherited verbatim and not re-specified.

### SW-1 · Sweet-Spot Rate
- **Plain language.** Share of balls in play struck at 8–32°.
- **Formula.** `Σ[8 ≤ launch_angle ≤ 32] / Σ[type == 'X']`
- **Grain.** Any grouping over the pitch spine.
- **Population.** Balls in play. Null launch angle excluded from numerator, **retained in denominator** (0.4% of BIP).
- **CDEs.** `launch_angle`, `type`
- **Edge cases.** 0 BIP → null, not 0. Boundary inclusive on both ends.
- **⚠️ Known blind spot.** Insensitive to *where within* the band contact lands. Must not be used alone for power hitters. See SW-8.

### SW-2 · Ideal-Contact Rate
- **Plain language.** Share of balls in play both in the sweet-spot band and hit at 95+ mph.
- **Formula.** `Σ[8 ≤ launch_angle ≤ 32 AND launch_speed ≥ 95] / Σ[type == 'X']`
- **Population.** Balls in play. A row missing *either* input fails the numerator test.
- **CDEs.** `launch_angle`, `launch_speed`, `type`
- **Edge cases.** Null EV → not ideal (conservative). 0 BIP → null.

### SW-3 · Fast-Swing Rate
- **Plain language.** Share of measured swings at ≥ 75 mph.
- **Formula.** `Σ[bat_speed ≥ 75] / Σ[bat_speed IS NOT NULL AND is_swing]`
- **Population.** **Measured swings only.** This is the load-bearing clause.
- **CDEs.** `bat_speed`, `description`
- **Edge cases.** Zero measured swings → **null, never 0**. Pre-2024 → null by suppression.

### SW-4 · Squared-Up Rate *(provisional)*
- **Plain language.** Share of contact converting ≥ 80% of available bat-and-pitch energy into exit velocity.
- **Formula.**
  `t* = (−vy0 − √(vy0² − 2·ay·(50 − 17/12))) / ay`
  `plate_speed = ‖(vx0+ax·t*, vy0+ay·t*, vz0+az·t*)‖ × 0.681818`
  `max_ev = 1.23 × bat_speed + 0.2306 × plate_speed`
  `squared_up_pct = launch_speed / max_ev` ; squared up when `≥ 0.80`
- **Population.** Balls in play with non-null `bat_speed`, trajectory parameters and `launch_speed`.
- **CDEs.** `launch_speed`, `bat_speed`, `vx0..az`, `type`
- **Edge cases.** Negative discriminant → clipped to 0 (0.13% of pitches, no effect on BIP). `max_ev ≤ 0` → null.
- **Validation gates.** DQ-12 (plate speed in [60,105]), DQ-13 (release-minus-plate 5–12 mph; observed 7.18), DQ-14 (`squared_up_pct` in [0,1.15]).
- **⚠️ Provisional.** Constants are published approximations → **OI-3**.

### SW-5 · Attack-Angle Fit Rate
- **Formula.** `Σ[5 ≤ attack_angle ≤ 20] / Σ[attack_angle IS NOT NULL AND is_swing]`
- **Population.** Measured swings, 2025+.
- **Edge cases.** Zero measured → null.

### SW-6 · Contact Depth
- **Formula.** `mean(intercept_ball_minus_batter_pos_y_inches)` over BIP where measured.
- **Population.** Balls in play, 2025+.
- **⚠️ Edge case that mattered.** **Direction of change is not self-interpreting.** A decline may be a return to the player's own baseline. **Interpretation rule: always compare to the player's prior-season mean, never to the prior phase alone.** This rule exists because applying it changed a conclusion in this build (E-6).

### SW-7 · Bat-Tracking Coverage Rate
- **Formula.** `count(field NOT NULL) / count(denominator population)`
- **Grain.** Must match the grain of the aggregate it accompanies.
- **Purpose.** Governance control, not analysis. **Publication rule: no bat-tracking aggregate may be published without its coverage figure at the same grain.**
- **Edge cases.** Zero coverage → the aggregate is suppressed to null, and coverage renders as `0.000`, not null.

### SW-8 · Damage-Band Rate
- **Plain language.** Share of balls in play at 20–32° — where a power hitter's extra-base value concentrates.
- **Formula.** `Σ[20 ≤ launch_angle < 32] / Σ[type == 'X']`
- **Population.** Balls in play.
- **Provenance.** Emerged from the analysis (E-5), not the intake. Specified before it appeared in any output.
- **Edge cases.** Band boundaries are archetype-dependent. **Validated for this hitter only** (band xwOBAcon 1.243 vs .736 for 8–20°). Must be re-validated before roster-wide use.

### SW-9 · Blast Rate
- **Formula.** `Σ[squared_up AND fast_swing] / Σ[both measured]`
- **Status.** Inherits SW-4's provisional status.

---

## 4. What this architecture does *not* do

Stated explicitly so no consumer over-reads the product.

1. **No park adjustment.** All contact-quality figures are raw. A Citizens Bank Park factor would change the level of the EV/barrel numbers, not the within-season direction — but the level is uncorrected.
2. **No opponent-quality adjustment.** The breaking-ball finding (§3 of the report) may partly reflect *who* he faced rather than a durable change. This is the single largest unmodelled confounder.
3. **No aging model.** The product reports observed bat speed. It does not project it.
4. **No causal claim.** The report identifies a *mechanism* (launch-angle redistribution) and a *correlate* (chase rate). It does not claim the chase rate causes the angle shift, and says so.
5. **No significance testing.** Sample sizes are printed on every row instead. At 120 BIP per phase, formal intervals would be wide enough to be uninformative, and printing n is more honest than printing a p-value.
6. **Rolling windows are descriptive, not a changepoint model.** No changepoint was fitted; the split is a midpoint, chosen for balance rather than estimated.
