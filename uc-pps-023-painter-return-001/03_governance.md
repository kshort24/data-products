# 03 — Governance

**Department:** `coa-dept-governance` · **Lead:** `governance-lead`
**Use Case:** `uc-pps-painter-return-001` · UC #29 · `dp_uc28`
**Layer 2 verdict:** ✅ complete — semantic layer defined, metadata mapped, tags proposed, privacy assessed (**internal-only**).

Agents run: `semantic-modeler` · `metadata-mapper` · `data-tagger` · `privacy-watchdog`.

---

## 3.1 `semantic-modeler` — KPI semantic layer

The purpose of this layer is to stop the three new KPIs from being quoted in contexts where they are meaningless.

### Aggregation constraints

| KPI | Valid dimensions | **Forbidden** | Additive? |
|---|---|---|---|
| **RCI** | `level`, `game_date` | ❌ never averaged across levels; ❌ never computed on <15 four-seams; ❌ never on a non-fastball | No — it is a dispersion statistic. Averaging RCI across starts is permitted for a within-level summary; averaging it across the MLB/AAA boundary is not. |
| **FUTR** | `level`, `game_date`, `stand`, `arc` | ❌ never pooled across levels | Yes, over four-seams within a level. |
| **XLSD** | `pitch_name` only | ❌ never aggregated to a single "stuff score"; ❌ never reported without the `noise_guard` flag; ❌ never for a pitch type failing `coverage_ok` | No. |
| `arm_spread_deg` | `pitcher` | ❌ **never quoted as evidence of tipping without the correlational caveat** | No. |
| All locked KPIs | `level` + any within-level dimension | ❌ never across `level` | Per inherited definitions. |

### The governing rule of this data product

> **No rate KPI may be computed with a denominator that spans more than one `level`.**

This is enforced structurally (02.1) rather than by convention. A future contributor cannot violate it by accident without deleting a `groupby`.

### Provisional status: `arm_spread_deg`

`semantic-modeler` **declines to ratify** `arm_spread_deg` as a standing glossary term in this cycle, while permitting its use in this report. Reasons:

1. `arm_angle` is itself **derived** by Statcast from release coordinates, so the metric is two levels removed from raw measurement.
2. Some slot spread is physically unavoidable — every pitcher's sweeper releases lower than his four-seam. The metric therefore has a **non-zero floor that varies by arsenal composition**, and a six-pitch pitcher is not comparable to a three-pitch pitcher without adjustment.
3. The benchmark pool (n=23) is too small and too Phillies-weighted to establish a population distribution.

**Ratification path:** compute across a full-season league-wide RHP population, stratified by arsenal size, and test whether spread predicts four-seam whiff residual after controlling for velocity and ride. Until then the metric is **UC-scoped and labelled correlational.** The report complies — it names the hypothesis as a hypothesis, twice.

---

## 3.2 `metadata-mapper` — physical → business term

| Physical column | Business term | Mapping | Note |
|---|---|---|---|
| `release_speed` | Pitch Velocity | **exact** | |
| `effective_speed` | Perceived Velocity | **exact** | extension-adjusted |
| `release_spin_rate` | Spin Rate | **exact** | |
| `spin_axis` | Spin Axis | **exact** | carried, not reported |
| `pfx_z` | Induced Vertical Break | **exact** (after ×12) | |
| `pfx_x` | Horizontal Break | **exact** (after ×−12) | **sign convention documented** |
| `release_pos_x/z` | Release Point | **exact** | |
| `release_extension` | Extension | **exact** | |
| `arm_angle` | Arm Angle | **fuzzy** | Statcast-derived, not directly measured. Flagged. |
| `plate_x`, `plate_z` | Pitch Location | **exact** | |
| `sz_top`, `sz_bot` | Strike Zone Boundary | **exact** | batter-specific |
| `zone` | Gridded Zone | **exact** | 1–9 in, 11–14 out |
| `description` | Pitch Outcome | **exact** | |
| `events` | Plate Appearance Outcome | **exact** | |
| `launch_speed` | Exit Velocity | **exact but sparse** | 36% populated |
| `estimated_woba_using_speedangle` | Expected wOBA | ⛔ **unmapped by ruling** | deprecated at pitch level (UC-PPS-021) |
| `loc_tier` | Location Tier | **derived** | defined in this UC |
| `tto` | Times Through the Order | **derived** | defined in this UC |

**Ambiguous / unmapped surfaced to DPO:** `arm_angle` (fuzzy — derived field carrying a headline claim). Recorded as open item #1 at 00.

---

## 3.3 `data-tagger` — classification proposal

| Element | Sensitivity | Domain | Subject area | Product membership |
|---|---|---|---|---|
| MLB tier (`phils_2026` filtered) | **Internal — Competitive** | Phillies Pitching | Pitch Profile, Pitch Outcomes | `uc-pps-painter-return-001` |
| AAA tier (`lhvp26` filtered) | **Internal — Competitive** | Phillies Pitching (player development) | Pitch Profile | `uc-pps-painter-return-001` |
| Benchmark pool | **Internal — Competitive** | League-wide | Pitch Profile | `uc-pps-painter-return-001` |
| Release / extension / arm angle receipts | **Internal — Restricted** | Phillies Pitching | Biomechanical proxy | `uc-pps-painter-return-001` |
| Reader report + dashboard | **Internal — Restricted** | Phillies Pitching | Advance / Development | `uc-pps-painter-return-001` |

**Escalation on the Restricted tier.** `data-tagger` proposes a **higher** classification than the usual `uc-pps` advance report. Rationale: this package contains a **named tipping hypothesis about a specific pitcher on our own roster**, plus per-pitch release-point signatures. In an opponent's hands it is an attack plan against Andrew Painter. That is a materially different exposure profile from a standard scouting report on an opposing starter.

*Requires DPO approval. Not self-published.*

---

## 3.4 `privacy-watchdog` — risk assessment

| Check | Finding | Severity |
|---|---|---|
| Direct PII | None. Player identity (MLBAM id, name) is public-domain professional performance data. | 🟢 none |
| Quasi-identifiers | None beyond the subject himself, who is the intentional subject. | 🟢 none |
| Re-identification of third parties | Batter ids appear in the `tto` derivation but **no batter-level output is published**. Opponent hitters are not named anywhere in any artifact. | 🟢 none |
| Health / medical inference | ⚠️ **Flagged.** Painter has a documented injury history, and this package publishes **extension decline, arm-angle decline, and release-point instability** across a date series. That combination invites clinical or physical-condition inference that this data cannot support. | 🟡 **medium** |
| Employment / competitive consequence | ⚠️ **Flagged.** The report bears directly on a roster decision about a specific identified individual. | 🟡 **medium** |
| External publish suitability | ⛔ **BLOCKED.** | 🔴 |

### Rulings

**R1 — External publish is blocked.** Governance principle 5. This package does not leave the organisation in any form.

**R2 — No health claim may be made from mechanical drift.** The build reports extension declining 6.451 → 6.293 ft and arm angle 47.1° → 40.6° across the AAA stint. These are **measurements**, and the report is required to present them as measurements with performance implications only. It complies — the report attributes the trend to "reaching rather than getting down the mound," a mechanical framing, and makes **no** claim about arm health, fatigue, or injury risk anywhere. Verified by `certification-agent` (05.3).

**R3 — Distribution list is need-to-know.** The four named personas (Painter, Realmuto, pitching department, manager) plus the human DPO. The tipping hypothesis in particular should not circulate beyond people who can act on it.

**R4 — The subject is a consumer of this product.** Painter is both the analysed entity and a named persona. `consumer-onboarding-agent` (06.2) is directed to write his persona card in developmental language — what to do next — rather than as a deficiency audit. Verified at 06.2.

---

## Governance sign-off

```json
{
  "semantic_layer": "defined; arm_spread_deg held PROVISIONAL",
  "metadata_mapping": "complete; 1 fuzzy mapping escalated (arm_angle)",
  "tagging": "proposed — Internal/Restricted, escalated above pattern default, awaiting DPO approval",
  "privacy": "assessed — 2 medium flags, external publish BLOCKED, 4 rulings issued",
  "blocking_issues": 0,
  "layer_2_governance": "COMPLETE"
}
```
