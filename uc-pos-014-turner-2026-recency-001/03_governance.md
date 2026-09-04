# 03 · Governance — glossary, KPI specs, lineage · `uc-pos-014-turner-2026-recency-001`

**Department:** Governance · **Agents:** `business-glossary-agent`, `kpi-calculator`,
`technical-lineage-builder`, `data-dictionary`, `data-tagger`, `privacy-watchdog`, `dq-rule-definer`
**Gate:** no CDE may be defined by a downstream agent; no new KPI may be declared new without the Rule-1 grep.

---

## 3.0 · Rule-1 grep — executed before anything was called new

Mandatory step (`repo-search-before-declaring-kpi-new`). Searched both repos for prior art on every
candidate KPI before writing a spec.

| Candidate | Grep result | Disposition |
|---|---|---|
| Approach / decision differential | **HIT** — `uc-pos-005` **OZ-3 Edge Decision Differential** (shadow-band form: `swing_rate(shadow_in) − swing_rate(shadow_out)`) | **INHERIT, don't redefine.** AD-1 is the whole-zone form and is specified below as a *sibling*, carrying OZ-3's edge-case caveat verbatim |
| Rolling-form wOBA | **HIT** — `uc-pos-006` RF-2 (provisional) | **Second reuse → ratification candidate.** Re-specified onto current denominators; the change is declared, not silent |
| Season-to-date trajectory | **HIT** — `uc-pos-006` RF-1, extended by `uc-pos-010` AP-6 / `uc-pos-011` / `uc-pos-013` (`running_line_pa`) | inherit `running_line_pa` verbatim |
| Platoon counterfactual | **HIT** — `uc-pos-011` PL-1 | inherit verbatim |
| Breakpoint sensitivity | **HIT** — `uc-pos-011` RC-5 (standing requirement) | inherit; mandatory here |
| Pull-air rate | **HIT** — governed `pull_air_rate` (defective, O-7) + `uc-pos-013` PA-F1 remediation | inherit PA-F1 |
| Bat tracking panel | **HIT** — `dp_uc24` (the parent) `bat_tracking` | inherit the 75-mph fast-swing convention verbatim; formalise as BT-1 |
| Window-shift uncertainty band | **MISS** — no prior z/CI receipt in either repo | **NEW: ST-1** |
| Population percentile pool | **HIT** — `uc-pos-010` / `uc-pos-011` / `uc-pos-013` `pool_percentile` | inherit verbatim |

---

## 3.1 · Glossary — terms consumed (not redefined)

| Term | Status | Definition source |
|---|---|---|
| Plate Appearance, At Bat, Hit, Walk, Strikeout, BIP | APPROVED | Business Glossary via `Baseball Functions.ipynb` |
| BA / OBP / SLG / OPS / ISO / BABIP / wOBA | APPROVED | `nresults` (D4-corrected as `nresults_unrounded`) + seasonal wOBA constants |
| Barrel, Hard-Hit, Sweet Spot | APPROVED (Hard-Hit denominator **disputed — O-8**) | Statcast conventions, governed kernel |
| Chase, In-Zone Swing, Whiff, First-Pitch Swing (`srfp`), First-Pitch Strike (`fpsr`) | APPROVED | governed kernel; **`fpsr` and `in_zone_rate` are PITCHER metrics on a hitter panel and are labelled as such** |
| xwOBA (per PA) / xwOBAcon (mean over BIP) | APPROVED with the **O-4 naming rule** | `uc-pps-025`; grain confirmed by `uc-pps-028` and re-asserted here (R-6) |
| Pull / Straightaway / Oppo, Pull-Air | PROVISIONAL (PA-L1 / PA-F1) | `uc-pos-013`, pending DPO ratification |
| Swing Speed, Swing Length, Attack Angle | APPROVED, sensor-bounded | Statcast bat tracking |

**No new business term was minted by this UC.** Two new *metrics* over approved terms are specified below.

---

## 3.2 · KPI specs

### AD-1 — Approach Differential — **NEW-PROVISIONAL**
- **Plain language:** one number for whether he is separating balls from strikes across the whole plate —
  how often he swings at strikes, minus how often he swings at balls.
- **Formula:** `swing_rate(zone ≤ 9) − swing_rate(zone > 9)`, i.e. `swing_rate_in_zone − chase_rate`.
  Rows with NULL `zone` are excluded from **both** populations.
- **Relationship to OZ-3 (`uc-pos-005`):** OZ-3 is the same idea restricted to the shadow band. AD-1 is
  the whole-zone sibling. **OZ-3 is not superseded**; the two answer different questions (edge judgment
  vs overall aggression pattern).
- **Inherited caveat, verbatim from OZ-3:** *can fall while judgment improves if the hitter cuts swings on
  both sides — must never be headlined alone.* AD-1 is published beside both components everywhere.
- **Floor:** the standing 50-PA floor at the level of aggregation; ranked only over qualified seasons.
- **Ratification:** required before a third use.

### ST-1 — Window-Shift Uncertainty Band — **NEW-PROVISIONAL**
- **Plain language:** before saying a five-week window "moved" a measure, say how much of that move a
  coin could produce.
- **Formula:** two-sample Welch z for continuous measures; two-proportion pooled z for rates. Reported
  against **two baselines** — the adjacent window, and the well-powered 2023–25 Phillies norm.
- **Bands:** `|z| ≥ 2.5` clearly beyond noise · `1.5 ≤ |z| < 2.5` suggestive · `< 1.5` within noise.
- **Hard constraint on interpretation:** the window is **non-random and outcome-selected**, so these are
  *descriptive uncertainty bands*, **not** hypothesis tests and **not** evidence of causation. The report
  and the dashboard both state this at the point of use. Publishing them without that sentence is a
  governance violation.
- **Why it exists:** the EDA pass produced a plausible, wrong mechanism ("his bat slowed down"). ST-1 is
  the receipt that killed it.

### RF-2 — Rolling-Form wOBA — **PROVISIONAL → RATIFICATION CANDIDATE (2nd reuse)**
- Trailing 100-PA wOBA, PA-indexed, single season.
- **Change from `uc-pos-006`, declared:** the parent divided by raw PA; this build uses the governed wOBA
  denominator `AB + uBB + SF + HBP`. For this subject the two agree to four decimals (see `05`), but the
  change is recorded because the next subject may have sacrifice bunts.

### BT-1 — Swing Measurables — **NEW-PROVISIONAL (formalising the parent's ad-hoc panel)**
- Mean/90th-percentile bat speed, swing length, attack angle, and fast-swing rate (`bat_speed ≥ 75`) over
  **tracked swings only**.
- **Sensor-boundary rule:** an untracked swing is NULL, never zero. Coverage ships beside the value.
- **Floor:** 25 tracked swings at window grain, 50 at season grain; below that the central tendencies are
  NULL rather than noisy.

### Inherited verbatim (no re-specification)
`nresults_unrounded` (D4) · `whiff_rate_fix` (D1) · `hard_hit_rate_fix` (D2, D6 retained) ·
`fpsr_fix` (D3) · `chase_rate_g` · `zone_swing_whiff` (ZS-1) · `ooz_whiff_rate` · `barrel_rate_g` ·
`battedball_profile` (CR-1) · `xcontact` (CR-2) · `derive_loc` (PA-L1) · `pull_air_rate_fix` (PA-F1) ·
`running_line_pa` (AP-6) · `platoon_counterfactual` (PL-1) · `pool_percentile` · RC-5 breakpoint scan.

### D-7 / O-13 — `in_zone_rate_fix` — **NEW REMEDIATION**
See `05` §Defects. Specified here because it changes a published number: the governed `chase_rate_g`
computes `in_zone_rate` as `(pitches − ooz) / pitches`, which counts NULL-`zone` rows as in-zone.
`in_zone_rate_fix` = `count(zone ≤ 9) / count(zone notna)`, with `zone_null_rate` shipped beside it.

---

## 3.3 · Technical lineage (column-level, source → KPI)

| KPI | Source columns | Hops |
|---|---|---|
| BA / OBP / SLG / OPS / ISO / BABIP | `events`, `type`, `game_year` | pitch → filter `game_type=='R'` → `pa_rows` (events ∉ NON_PA) → count masks → ratios (no intermediate rounding, D4) |
| wOBA | `events` + `wOBA and FIP Constants.{wBB,wHBP,w1B,w2B,w3B,wHR}` | pitch → `pa_rows` → per-event weight lookup on `game_year` → Σnum / (AB+uBB+SF+HBP) |
| xwOBA | `estimated_woba_using_speedangle` | pitch → mean over non-null (== PA-terminating rows, asserted R-6) |
| xwOBAcon | same column | pitch → `type=='X'` → mean; **named differently because the grain differs (O-4)** |
| Hard-Hit | `launch_speed`, `type` | pitch → BIP → `≥95` / all BIP *(O-8: tracked-only variant shipped beside it)* |
| Barrel | `launch_speed_angle`, `type` | pitch → BIP → `==6` / all BIP |
| Popup / GB / FB / LD share | `bb_type`, `type` | pitch → BIP → share; `bb_type` is classifier-derived and complete, so shares use ALL BIP (CR-1) |
| Mean EV / LA | `launch_speed`, `launch_angle` | pitch → BIP → **tracked** BIP → mean (CR-1 two-population design) |
| Swing / Whiff / Chase / In-zone swing | `description`, `zone` | pitch → SWINGS ∩ WHIFFS masks; zone partition excludes NULL from both sides |
| `in_zone_rate_fix` | `zone` | pitch → non-null zone → `≤9` share |
| `srfp` / `fpsr` | `pitch_number`, `description`, `type` | pitch → `pitch_number==1` → swing share / (1 − ball share) |
| Pull-Air | `hc_x`, `hc_y`, `bb_type`, `stand` | pitch → BIP → `derive_loc` (centre, y-flip, uniform scale) → governed ±4.7-slope classification → `Pull ∧ bb_type≠ground_ball` / all BIP |
| Bat speed / fast-swing | `bat_speed`, `description` | pitch → SWINGS → non-null `bat_speed` → mean / `≥75` share |
| AD-1 | `zone`, `description` | two swing rates over the zone partition → difference |
| RF-1 / RF-2 | `events` + constants | `pa_rows` ordered by date/game/AB → cumulative or 100-PA trailing sums → ratios |
| ST-1 | any of the above | two windows → Welch or pooled two-proportion z |

**Manual carry-ins (not derivable from the log), with source:** 2026 All-Star break = 2026-07-16
(inherited from `uc-pos-006`); the parent product's delivery date 2026-07-21 and as-of date 2026-07-20
(from the parent package itself). Nothing else is carried in. No external data was fetched.

---

## 3.4 · `data-tagger` and `privacy-watchdog`

| Element | Sensitivity | Domain | Product |
|---|---|---|---|
| All CDEs in this build | **Internal — Baseball Operations** | Phillies Offense (`pos`) | `uc-pos-014` |
| Persona hypotheses (§8 of the report) | **Internal — restricted**; player-facing surfaces in `06` exclude them | Phillies Offense | `uc-pos-014` |

**Privacy assessment: LOW–MODERATE**, one notch above the usual `pos` baseline, for the same reason
`uc-pos-011` was raised: the subject is a named, identifiable individual and the product discusses
performance decline and possible coaching intervention — information the subject may not have seen. All
inputs are publicly broadcast Statcast measurements; no health, contract, medical, or personnel data is
present or inferred. **The product contains no PII beyond a public player identity.** No external
publication surface is proposed. The player-facing brief in `06` is scoped to mechanics and excludes the
decline framing, the persona table, and the population percentile placement.

*Gate decision: **APPROVED.** Two new provisional KPIs (AD-1, ST-1), one promoted to ratification
candidate (RF-2), one new remediation (D-7 `in_zone_rate_fix`), zero new business terms.*
