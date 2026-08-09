# 02 — Business Glossary, Tagging & Privacy

**Layer 1 — Intake & Discovery** · Department: Governance
**Agents:** `business-glossary-agent` · `data-tagger` · `privacy-watchdog`
**Use case:** `uc-pos-009-schwarber-swing-decay-001` · **Build:** `dp_uc32`

> **Governance principle 1 — no CDE inference.** No term below was invented. Every entry is either (a) inherited verbatim from the locked kernel, (b) a published Statcast definition with the source named, or (c) a **report-local** term composed from existing physical CDEs and returned to the DPO as a promotion candidate.

---

## 1. Inherited terms — locked, used byte-identical

| Term | Definition | Physical CDEs | Source |
|---|---|---|---|
| Ball in Play (BIP) | Pitch with `type == 'X'` | `type` | locked kernel |
| Swing | `description ∈ {foul, foul_bunt, foul_tip, hit_into_play, missed_bunt, swinging_pitchout, swinging_strike, swinging_strike_blocked}` | `description` | locked `whiff_rate` |
| Whiff Rate | whiffs ÷ swings | `description` | locked |
| Chase Rate | swings at `zone > 9` ÷ pitches at `zone > 9` | `zone`, `description` | locked |
| In-Zone Whiff Rate | Whiff Rate restricted to `zone < 10` | `zone`, `description` | locked |
| Barrel Rate | `launch_speed_angle == 6` ÷ BIP | `launch_speed_angle`, `type` | locked |
| Hard-Hit Rate | `launch_speed >= 95` ÷ BIP | `launch_speed`, `type` | locked |
| EV90 | 90th percentile of `launch_speed` over BIP | `launch_speed`, `type` | locked |
| xwOBA on Contact | mean `estimated_woba_using_speedangle` over BIP | `estimated_woba_using_speedangle` | Statcast native |
| ISO | SLG − BA | derived | standard |

---

## 2. Report-local terms — SW-1 … SW-9

**Status: PROVISIONAL.** Nine terms is a large batch. All are roster-general (nothing is Schwarber-specific) and all are returned to the DPO for ratification (**OI-2**).

### SW-1 · Sweet-Spot Rate
**Plain language.** The share of balls in play struck at a launch angle in the 8–32° band.
**Formula.** `count(8 ≤ launch_angle ≤ 32) / count(type == 'X')`
**Source.** Statcast published definition.
**⚠️ Known limitation — this is the report's central metrological finding.** The band is wide enough that a low line drive and a home-run-angle fly ball are scored identically. For a hitter whose value concentrates in the top third of the band, SW-1 can **rise while production falls**. Observed here: +6.4% while SLG fell 27.2%. **SW-1 must not be used alone as a contact-quality indicator for power hitters.** Use SW-2 or Damage-Band Rate.

### SW-2 · Ideal-Contact Rate
**Plain language.** The share of balls in play that are *both* in the sweet-spot band *and* hit hard.
**Formula.** `count(8 ≤ launch_angle ≤ 32 AND launch_speed ≥ 95) / count(type == 'X')`
**Rationale.** Repairs SW-1's blind spot on the velocity axis. Caught the 2026 decline (−10.2%) where SW-1 did not.
**Promotion candidate: strong.** Roster-general, cheap, uses only locked CDEs.

### SW-3 · Fast-Swing Rate
**Plain language.** The share of *measured* swings taken at 75 mph or more.
**Formula.** `count(bat_speed ≥ 75) / count(bat_speed IS NOT NULL AND is_swing)`
**Window.** 2024+ only. **Denominator is measured swings, not all swings.**
**Source.** 75 mph is the Statcast "fast swing" convention.

### SW-4 · Squared-Up Rate *(provisional — see caveat)*
**Plain language.** The share of contact that converts the available bat-and-pitch energy into exit velocity at 80% efficiency or better.
**Formula.** `squared_up_pct = launch_speed / (1.23 × bat_speed + 0.2306 × plate_speed)`; squared up when `≥ 0.80`.
**`plate_speed` derivation.** Speed at the front edge of home plate (`y = 17/12` ft), solved exactly from the Statcast 9-parameter trajectory fit (`vx0, vy0, vz0, ax, ay, az`) — **not** approximated from `release_speed`. Statcast's constants are calibrated on plate speed; substituting release speed would inflate max-EV by ~7 mph and depress the rate.
**Validation.** Mean release-minus-plate gap 7.18 mph (DQ-13, expected 5–12). All values in [0, 1.15] (DQ-14).
**⚠️ Caveat.** The 1.23 / 0.2306 constants are published approximations. Treated as **directional**. Logged as **OI-3**.

### SW-5 · Attack-Angle Fit Rate
**Plain language.** Share of measured swings with an attack angle in the 5–20° window.
**Formula.** `count(5 ≤ attack_angle ≤ 20) / count(attack_angle IS NOT NULL AND is_swing)`
**Window.** 2025+ only.

### SW-6 · Contact Depth
**Plain language.** How far in front of the batter, in inches, the ball is met.
**Physical CDE.** `intercept_ball_minus_batter_pos_y_inches`, aggregated as a mean over BIP.
**Window.** 2025+ only.
**⚠️ Interpretation warning.** Higher is not automatically better. Established here that a within-season *decline* in contact depth may represent **return to the player's own baseline** rather than degradation. Always compare to the player's prior-season mean, never to the prior phase alone.

### SW-7 · Bat-Tracking Coverage Rate
**Plain language.** The share of the denominator population for which the sensor actually recorded a value.
**Formula.** `count(field IS NOT NULL) / count(denominator population)`
**Purpose.** This is a **governance KPI, not an analytical one.** It exists to make the no-imputation policy visible and enforceable. It must be published beside every bat-tracking aggregate.
**Promotion candidate: strong** — generalises to any sensor-era field in any data product.

### SW-8 · Damage-Band Rate
**Plain language.** The share of balls in play struck at 20–32° — the launch-angle band where a power hitter's extra-base value concentrates.
**Formula.** `count(20 ≤ launch_angle < 32) / count(type == 'X')`
**Rationale.** Emerged from the analysis, not from the intake. It is the metric that explains the decline that SW-1 hides. Band-specific xwOBAcon: 1.243, versus .736 for the 8–20° band.
**Promotion candidate: strong**, with the caveat that the band should be validated per-archetype before it becomes a roster-wide standard.

### SW-9 · Blast Rate
**Plain language.** Contact that is both squared up (SW-4) and produced by a fast swing (SW-3).
**Formula.** `count(squared_up AND fast_swing) / count(both measured)`
**Status.** Reported for completeness; inherits SW-4's provisional status.

---

## 3. Evidence-window terms — new governed concept

The single most reusable output of this UC.

| Term | Definition |
|---|---|
| **Full-Career Window** | 2015 → present. Fields available for the whole Statcast era |
| **Bat-Tracking Window** | 2024 → present. `bat_speed`, `swing_length` |
| **Swing-Path Window** | 2025 → present. `attack_angle`, `attack_direction`, `swing_path_tilt`, `intercept_*` |
| **Sensor Boundary** | The date a measurement instrument began operating. Data before it is **out of scope**, not missing |
| **Coverage Gate** | A publication rule: an aggregate over a sensor-era field may only be published together with its SW-7 coverage, and may not be published at all where coverage is zero |

**Proposed repository standard (OI-1):**

> Missing-because-the-instrument-did-not-exist is **out-of-scope data**, not missing data. Imputation is defensible only where a value existed and was not captured. Sensor-era fields must be computed on measured rows only, must publish coverage alongside every aggregate, and must render pre-sensor periods as *not measured* rather than as a number.

---

## 4. Terms explicitly NOT defined

| Requested / implied | Why not |
|---|---|
| "Pop" | Consumer shorthand, not a metric. Decomposed into SLG, ISO, barrel rate, EV90, HR rate; the report says where they agree |
| "Lost his swing" | Not a governed concept and the data contradicts the framing |
| "Aging curve" | Requires a population model this build does not have. Report speaks only to observed bat speed |
| "Ideal launch angle" (as a single number) | No single value is defensible. Expressed as bands (SW-1, SW-8) |

---

## 5. `data-tagger` — classification proposal

| Element | Sensitivity | Domain | Subject area | Product |
|---|---|---|---|---|
| `batter` (656941) | Public | Player Ops | Identity | `uc-pos-009` |
| `player_name` | Public | Player Ops | Identity | `uc-pos-009` |
| Statcast measurement CDEs | Internal | Baseball Systems | Ball flight / bat tracking | `uc-pos-009` |
| SW-1…SW-9 aggregates | **Internal — Restricted** | Player Ops | Performance evaluation | `uc-pos-009` |
| Persona action cards (§8 of report) | **Internal — Restricted** | Player Ops | Coaching intervention | `uc-pos-009` |
| Opposing-scout mirror view (§8.7) | **Internal — Restricted** | Advance Scouting | Competitive intelligence | `uc-pos-009` |
| DQ / verification receipts | Internal | Data Governance | Quality | `uc-pos-009` |

**Not published without approval:** the tagging proposal is submitted for DPO review, not applied.

---

## 6. `privacy-watchdog` — risk assessment

**Classification: Internal — Restricted. Not for external publication.**

| Risk | Present | Assessment |
|---|---|---|
| Direct PII | No | MLBAM id and name are public identifiers of a public figure acting in a public professional capacity |
| Quasi-identifiers | No | No demographic, medical, contractual or location data |
| Health / injury information | **No — and deliberately so** | The build reads **no** injury, workload, or medical data. §8.6 explicitly declines to infer fatigue |
| Re-identification | N/A | Single named subject by design |
| Combination risk | **Yes** | Performance-decline judgments about a **current employee**, combined with a front-office valuation section (§8.5) and coaching-intervention recommendations (§8.1) |
| Competitive-intelligence risk | **Yes** | §8.7 states plainly what opposing clubs can exploit. External disclosure would be self-harming |

### Findings

**PW-1 — Employment-adjacent judgment.** §8.5 speaks to contract and valuation implications for a current player. Restricted distribution; front-office section should not circulate to the clubhouse.

**PW-2 — The mirror view is a live vulnerability disclosure.** §8.7 enumerates three exploitable weaknesses. **Blocks external publication.** Internal circulation is the point of the section.

**PW-3 — No fatigue inference, and the report says so.** The build had bat-speed-by-month available and used it to *rule out* a fatigue narrative rather than construct one. Health inference from performance data is a standing risk in this class of product; here it was actively avoided and documented.

**PW-4 — No remediation required.** No masking, no aggregation floor, no suppression. The controls are distribution controls, not data controls.

**Verdict: cleared for internal circulation. Blocked for external publication.**
