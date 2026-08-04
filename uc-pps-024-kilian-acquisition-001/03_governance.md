# 03 — Governance

**Department:** Governance · **Agents:** `business-glossary-agent`, `metadata-mapper`, `data-dictionary`, `data-tagger`, `privacy-watchdog`
**Layer 2 (parallel) verdict:** ✅ complete — no business meaning inferred; 3 promotion candidates returned to the DPO

---

## 3.1 `business-glossary-agent` — terms

**Provenance discipline:** every term below is either **locked** (inherited verbatim from the UC8 → UC11 → UC28 line and the Baseball Functions library), **inherited-approved** (already glossary-approved in a prior UC), or **report-local** (defined here from existing CDEs and flagged for promotion). **Nothing is inferred.**

| Term | Definition | Column | Provenance |
|---|---|---|---|
| Whiff rate | whiffs / swings | `whiff_rate` | **locked** |
| Chase rate | swings at out-of-zone / out-of-zone pitches | `chase_rate` | **locked** |
| Putaway rate | strikeouts / two-strike pitches | `putaway_rate` | **locked** |
| First-pitch strike rate | non-balls / first pitches of PA | `first_pitch_strike_rate` | **locked** |
| Hard-hit rate | BIP ≥ 95 mph / BIP | `hard_hit_rate` | **locked** |
| CSW rate | (called strikes + whiffs) / pitches | `csw_rate` | **locked** |
| K% / BB% / wOBA / HR rate | `nresults` family, FanGraphs-weighted wOBA | `krate`, `bbrate`, `woba`, `hr_rate` | **locked** |
| **xwOBAcon** | mean `estimated_woba_using_speedangle` over BIP (`type=='X'`) | `xwobacon` | **inherited-approved (hardened)** — from `uc-pps-021`; supersedes contaminated pitch-level `get_stats.xwoba` → **O1 still open** |
| **Tracked pitch** | a row representing an actually-thrown, tracked pitch (`pitch_name` non-null); excludes `automatic_ball` pitch-timer violations | *(population, not a column)* | **report-local → promotion candidate** |
| **Zone rate (strict)** | in-zone pitches / **tracked** pitches | `zone_rate_strict` | **report-local → promotion candidate** → **O2** |
| **Slider Finish Rate** | share of sliders finishing glove-side vs backing up arm-side | `slider_finish.h_side` | **report-local → promotion candidate** |
| **Fastball Elevation Rate** | share of four-seamers in the upper third of the batter-specific zone | `fastball_elevation.elevation_rate` | **report-local → promotion candidate** |
| **Role Conversion Delta** | signed current-era-minus-prior-era difference per locked KPI, carrying both denominators | `role_conversion_delta.delta` | **report-local → promotion candidate** |
| **Era tier** | role-defined evidence partition (2026 relief vs 2022-24 starting); never blended | `era_tier` | **report-local** — adapts UC11's level tier |

**Glossary Agent verdict:** ✅ **no new business meaning inferred.** Five report-local terms returned to the DPO as promotion candidates. All five are *compositions of existing approved CDEs* — none asserts a new business concept, which is the line the agent is forbidden to cross. Where a definitional question arose (what counts as a "pitch"), the agent did **not** decide it on semantic grounds: it was resolved by the source profiler from observed data (`automatic_ball` description) and recorded as a population rule.

**Domain gaps returned, not resolved:** the domain-steward-proxy context in 01.3 (conversion signatures, backed-up sliders, three-batter minimum) is general baseball knowledge, not sourced from a Phillies document. It informs interpretation but **defines no term here**, and is flagged for human ratification before any of it hardens into glossary language.

---

## 3.2 `metadata-mapper` — physical → business mapping

| Physical column | Business term | Mapping |
|---|---|---|
| `pitcher` | Pitcher (MLBAM id) | exact |
| `pitch_name` | Pitch Type | exact |
| `release_speed` | Velocity | exact |
| `pfx_z` × 12 | Induced Vertical Break (in) | exact (unit conversion) |
| `−pfx_x` × 12 | Horizontal Break, arm-side positive (in) | exact (unit conversion + sign convention) |
| `plate_x` | Horizontal location | exact — **orientation asserted, not assumed** (see 03.1 note below) |
| `plate_z`, `sz_top`, `sz_bot` | Vertical location, zone band | exact |
| `zone` | Statcast gridded zone | exact |
| `description` | Pitch Outcome | exact |
| `events` | At-Bat Outcome | exact (PA-terminal) |
| `stand` | Batter Handedness | exact |
| `type` | Ball / Strike / In-play | exact |
| `launch_speed` | Exit Velocity | **fuzzy** — populated on fouls as well as BIP; requires `type=='X'` filter → **O3** |
| `estimated_woba_using_speedangle` | xwOBA on contact | **fuzzy** — pitch-level mean contaminated → use BIP-only → **O1** |
| `pitcher_days_since_prev_game` | Rest days | exact |
| `fld_score` − `bat_score` | Entry score state | derived, exact |
| `on_1b/2b/3b` | Inherited runners | exact (non-null = occupied) |
| `bat_speed`, `swing_length`, `attack_angle` | Swing-side metrics | **unmapped — excluded**, 46% populated, no published KPI |

**Orientation assertion.** `plate_x` sign convention is the one mapping in this UC that could silently invert an entire recommendation — "throw it glove-side" becomes "throw it arm-side" if the sign is read backwards. The mapper refused to accept it from documentation alone. It is **asserted from the data on every build**: for this RHP, the sinker (arm-side run) must show mean `pfx_x` < 0 and mean `plate_x` < 0, and the slider (glove-side) the reverse. Both assertions PASS in the DQ scorecard.

**Ambiguous / unmapped returned to DPO:** 2 fuzzy (both already tracked as O1/O3), 3 unmapped-by-exclusion (swing-side fields). **No element was mapped on inference.**

---

## 3.3 `data-tagger` — classification proposal

| Element | Sensitivity | Domain | Subject area |
|---|---|---|---|
| All pitch-level tracking columns | **Public** — MLB Statcast is publicly distributed | Baseball Operations | Pitch Profile |
| Player identifiers (`pitcher`, `batter`, MLBAM ids) | **Public** — public roster identifiers | Baseball Operations | Player Master |
| Derived KPI outputs (`out/*.csv`) | **Internal** | Phillies Pitching | Pitching Performance |
| **Report narrative, persona sections, deployment recommendation** | **Internal — Confidential** | Phillies Pitching | Advance / Player Development |
| Governance trail (00-07) | **Internal** | Phillies Pitching | Data Governance |

**The tag that matters:** the *inputs* are public Statcast; the *outputs* are not. This package contains an explicit evaluation of a newly acquired player's weaknesses and a recommendation about how the manager should limit his usage. **Publish scope: internal only.** Tagging proposal returned for DPO approval; no tags published autonomously.

---

## 3.4 `privacy-watchdog` — privacy risk assessment

| Risk class | Finding |
|---|---|
| Direct PII | **None.** Public professional athletes identified by public MLBAM ids. No contact details, no personal identifiers, no health data |
| Quasi-identifiers | **None** — no combination of fields identifies a non-public individual |
| Re-identification risk | **None.** Every input row is already publicly published by MLB Advanced Media |
| Sensitive combinations | **One, non-privacy:** the report links a named individual to a performance-weakness assessment and a usage limitation. This is **employment-sensitive, not privacy-sensitive** |
| External publish | 🚫 **BLOCKED.** Not a privacy block — a competitive and employment-sensitivity block. The report tells a reader exactly how to attack this pitcher (arm-side sliders, fastballs down) and states he should be pulled after four batters |

**Watchdog verdict:** ✅ **no privacy remediation required.** Internal-only classification affirmed. Governance principle 5 is satisfied: the privacy assessment completed before any publish decision, and the external-publish path is closed.

---

## 3.5 Governance principle compliance

| Principle | Status |
|---|---|
| **1. No CDE inference** | ✅ 5 report-local terms are compositions of approved CDEs; the one definitional question (what is a "pitch") was resolved from observed data, not semantics |
| **2. No build without approved specs** | ✅ all 3 new KPIs fully specified in `02_engineering_design.md` §2.2 before appearing in any output |
| **3. No publish without certification** | ✅ see `05_quality_certification.md` — READY, 205/205 |
| **4. No breaking changes without notice** | ✅ n/a, new product; locked functions inherited byte-identical |
| **5. Privacy flags block external publish** | ✅ assessment complete; internal-only enforced |
