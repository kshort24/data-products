# 03a · Bat-Path Semantics, Technical Definitions & Lineage
### `uc-pos-014` v1.1.0 · `dp_uc40a` · addendum to `03_governance.md`

**Departments:** Governance · **Agents:** `domain-steward-proxy`, `source-system-profiler`,
`business-glossary-agent`, `data-dictionary`, `metadata-mapper`, `kpi-calculator`,
`technical-lineage-builder`, `dq-rule-definer`
**Gate:** no bat-path number may be produced until every column below has a semantic definition, a
technical definition, an asserted convention, and a documented lineage. **Status: CLOSED.**

---

## 0 · Why this document exists

The DPO's follow-up asked for insight from columns he had not used before, and asked explicitly that any
new work follow the governance discipline of `Baseball Functions.ipynb` — technical and semantic
definitions, documented lineage.

**Rule-1 grep result:** the six bat-path columns appear in the data plane in exactly one place —
a single exploratory `px.histogram(swing_path_tilt)` cell in `November 2025.ipynb`. There is **no
governed function, no definition, no lineage, and no glossary entry** for any of them anywhere in either
repository. `dp_uc20` and `dp_uc24` reference `attack_angle` only inside a `bat_tracking` panel that
returns `NaN` for it (the column is empty in 2024).

So these are **new CDEs**, and the `business-glossary-agent` cannot infer their meaning — the
`domain-steward-proxy` must source it. Sources used are cited per term. **Nothing in this document is
inferred from the subject's own data**; where the data and the published source disagree, that
disagreement is itself the finding and is recorded as an open item.

---

## 1 · `domain-steward-proxy` — semantic definitions (sourced, not inferred)

All four definitions come from the MLB Statcast glossary. Statcast bat tracking began with bat speed and
swing length in **2024**; swing path, attack angle, attack direction and intercept point were added for
**2025**.

### 1.1 Attack Angle — `attack_angle`
> *"Attack angle measures the vertical direction that the sweet spot of the bat is traveling at the
> moment it hits the baseball."* Measured **at contact** (or, on a swing-and-miss, at the point where bat
> and ball cross paths). Positive = the barrel is moving **upward**. **MLB average ≈ 10°**; seasonal
> player averages run roughly 0°–20°. The glossary defines an **"ideal attack angle" band of 5°–20°** —
> "the range at which swings produce the most value for the batter."
> *Distinct from launch angle, which describes how the **ball** leaves the bat.*
> — [MLB Statcast glossary: Attack Angle](https://www.mlb.com/glossary/statcast/attack-angle), [Ideal Attack Angle](https://www.mlb.com/glossary/statcast/ideal-attack-angle)

### 1.2 Attack Direction — `attack_direction`
> *"Attack direction measures the horizontal direction that the sweet spot of the bat is moving at the
> point of contact with the baseball"*, against a line from home plate to straightaway centre field.
> 0° = straight to centre. **The glossary states pull = positive, oppo = negative**, with an MLB average
> of about 2° pull and a seasonal range of roughly 15° pull to 10° oppo. The glossary also warns that
> attack direction **reflects swing timing** — early and late swings move it substantially.
> — [MLB Statcast glossary: Attack Direction](https://www.mlb.com/glossary/statcast/attack-direction)
>
> ⚠ **The sign convention above does NOT hold in this data plane. See O-15 in §3.**

### 1.3 Swing Path (Tilt) — `swing_path_tilt`
> *"Swing path is a metric that tells you the shape of a hitter's swing on the way toward contact. The
> tilt of the swing is defined as the vertical angle formed by the bat path compared to the ground."*
> 0° = perfectly flat, 90° = a golf swing. **MLB average ≈ 32°**; seasonal player averages run roughly
> 20° (flattest) to 50° (steepest).
> *Key distinction from attack angle:* **"swing path measures the overall plane the bat follows over the
> course of the swing, while attack angle measures the direction that the barrel of the bat is moving at
> the point of contact."** Swing path is about the **shape on the way to** contact; attack angle is about
> **what is happening at** contact.
> — [MLB Statcast glossary: Swing Path (Tilt)](https://www.mlb.com/glossary/statcast/swing-path-tilt)

### 1.4 Intercept Point — `intercept_ball_minus_batter_pos_{x,y}_inches`
> *"Where the hitter makes contact with the ball — or where the bat and ball pass nearest to each other,
> in the case of a swing-and-miss."* Statcast reports it two ways: relative to the **front edge of home
> plate**, and relative to the **batter's centre of mass** (the midpoint between his hips). Units are
> **inches**; "out in front" is positive, "deep"/"behind" is negative.
> — [MLB Statcast glossary: Intercept Point](https://www.mlb.com/glossary/statcast/intercept-point)
>
> The two columns in this data plane are the **batter-relative** pair. The glossary does not say which
> physical axis each column carries, and the column names do not disambiguate it. **§2 proves it.**

### 1.5 Bat Speed / Swing Length — `bat_speed`, `swing_length`
Inherited from BT-1 (`03_governance.md` §3.2). Sweet-spot speed at contact (mph) and the length of the
barrel's path to contact (ft). Available from **2024**. The 75-mph "fast swing" threshold is inherited
verbatim from the parent product `dp_uc24`.

### 1.6 `hyper_speed` — **NOT a bat-path column**
No glossary entry was needed: §2 check **C7** proves it is exactly `max(launch_speed, 88)` on 100.0% of
6,720 tracked 2026 Phillies swings — Statcast's *Adjusted Exit Velocity*. It is a deterministic transform
of a column already governed by this product and carries **no independent information**. **O-17: it must
never be reported as a separate measure of contact quality.** It is not used anywhere in this addendum.

---

## 2 · `source-system-profiler` — the conventions, proven

**House rule (`uc-pps-025`): assert the convention, never assume it.** The build calls
`assert_conventions()` before producing a single number and **refuses to publish** if any hard check
fails. The population is **all Phillies batters, regular season, 2025–2026** — never the subject alone,
so a convention cannot be fitted to his quirks. All 12 checks pass; receipts in
`out/dp_uc40a_bp_convention_assertions.csv`.

| Check | Claim | Statistic | Value | Rule |
|---|---|---|---|---|
| C1-R / C1-L | `intercept_..._x` is the **lateral** axis — an inside pitch is met **closer to the body** | corr with inside-ness of the pitch | **−0.953 / −0.887** | r < −0.60 |
| C2 | `intercept_..._y` is the **depth** axis — a slower pitch is met **further out front** | corr with `release_speed` | **−0.557** | r < −0.35 |
| C3 | **No height component ships.** Neither axis behaves like a vertical axis | \|corr(side, `plate_z`)\| | 0.090 | \|r\| < 0.30 |
| C4 | `attack_direction` is **pull-negative** here | corr with pull-side spray, hard-hit air balls | **−0.790** | r < −0.50 |
| C5 | …and it is **stand-normalised**, not a fixed field frame | sign of that corr for LHH and RHH | both negative | both < 0 |
| C6a | `attack_angle` and `attack_direction` share **one** tracking gate exactly | disagreeing rows | 0 | == 0 |
| C6b / C6c | `swing_path_tilt` and `intercept_*` gates agree to within 0.2% | share disagreeing | 0.0001 / 0.0012 | < 0.002 |
| C6d | Every gate disagreement is a **bunt or a sub-25 mph checked swing** | all explained | yes | == 1 |
| C7 | `hyper_speed` == `max(launch_speed, 88)` | share satisfying the identity | **1.0000** | > 0.999 |
| C8 | `attack_angle` (bat) predicts `launch_angle` (ball) on well-struck contact | corr on hard-hit BIP | **+0.428** | r > 0.25 |

**The depth axis, shown rather than asserted** — mean `intercept_depth_in` by pitch velocity, all
Phillies 2025–26 tracked swings. Monotone across every bucket, which is what makes C2 an anchor rather
than a correlation:

| Pitch velocity | < 80 | 80–86 | 86–92 | 92–96 | 96+ |
|---|---|---|---|---|---|
| **Contact depth (in front, inches)** | **41.1** | 36.5 | 31.2 | 23.2 | **20.4** |
| Attack angle (°) | 17.2 | 14.0 | 10.7 | 5.1 | 2.1 |
| Attack direction (°) | −16.3 | −10.5 | −3.1 | +8.8 | +12.9 |

---

## 3 · Open items raised by this addendum

> **ID-collision note (resolved 2026-09-04).** These four items were first drafted as **O-14 … O-17**.
> A concurrent session claimed **O-14** for an unrelated defect (`nresults().bbrate` is
> unintentional-BB/PA — `intent_walk` sits in the denominator, not the numerator). To avoid two open
> items sharing an ID, this addendum's items were renumbered **+1 to O-15 … O-18** before publication.
> **The open-item register has no allocator**, which is how the collision happened —
> raised to the DPO as **E-13**.

| ID | Severity | Item |
|---|---|---|
| **O-15** | **HIGH — semantic, breaking for any consumer** | **`attack_direction` is PULL-NEGATIVE / OPPO-POSITIVE in this data plane, the inverse of the published MLB glossary convention.** Four independent anchors agree with the data and against the glossary: pull-side spray on hard-hit air balls (r = −0.79); contact depth (r = −0.89 — deep contact goes oppo, out-front contact pulls); the velocity table above (96+ mph fastballs, met deep and fought off, sit at **+12.9**; sub-80 mph breaking balls, met out front and pulled, at **−16.3**); and identical sign behaviour for LHH and RHH. **Any consumer applying the glossary convention inverts every pull/oppo conclusion.** Mitigation shipped: a derived `pull_direction = −attack_direction` accompanies the raw column in every receipt and every panel. **Escalated to the DPO — a Savant methodology check is warranted before this is treated as settled.** |
| **O-16** | **MEDIUM — comparability** | **`swing_path_tilt` fell team-wide between 2025 and 2026.** Every one of the 8 Phillies with 200+ tracked swings in both years moved down or flat; the cohort median delta is **−1.15°**. Whether this is a real league trend or a Statcast calibration change is **unknown from inside this data plane**. **Standing rule from this build: no year-over-year tilt (or any instrumented bat-path) comparison may be published without a peer-netted control.** `peer_delta()` (PB-1) exists for exactly this and is used on every year-over-year claim in the addendum. |
| **O-17** | LOW — redundancy | `hyper_speed` is `max(launch_speed, 88)`. Not independent information; excluded from this product and flagged for the glossary. |
| **O-18** | MEDIUM — population | **Bat-path columns are degenerate on bunts and checked swings.** `foul_bunt` and `missed_bunt` are in the governed `SWINGS` list but are not swing paths; those rows carry absurd values (bat speed 8–14 mph, attack angle −53°) and are the only rows where `swing_path_tilt` goes NULL while `attack_angle` is present. `intercept_*` has a slightly wider gate (25 of 21,700 swings, 0.12%). **BP-0 defines the bat-path population as swings excluding bunts, with sub-25 mph swings flagged degenerate, excluded from central tendencies, and counted.** This is a definitional exclusion, not a filter tuned to a result — and it **changed a headline**: on an ungoverned population the breaking-ball popup swing showed a 7 mph bat-speed collapse; under BP-0 the gap is −0.5 mph and the story disappears. |

---

## 4 · `data-dictionary` — technical definitions

| Business term | Physical column | Type | Units | Grain | Population | Null policy |
|---|---|---|---|---|---|---|
| Attack Angle | `attack_angle` | double | degrees, + = upward | pitch | tracked swings, 2025+ | NULL pre-2025 (sensor boundary) and on untracked swings. **Never imputed.** |
| Attack Direction | `attack_direction` | double | degrees, **pull-negative here (O-15)** | pitch | tracked swings, 2025+ | as above |
| Pull Direction *(derived)* | `pull_direction` | double | degrees, **pull-positive** | pitch | derived `= −attack_direction` | inherits |
| Swing Path Tilt | `swing_path_tilt` | double | degrees, 0 = flat | pitch | tracked swings, 2025+ | as above; also NULL on bunts (O-18) |
| Contact Point — Side | `intercept_ball_minus_batter_pos_x_inches` → `intercept_side_in` | double | inches from the batter's centre of mass | pitch | tracked swings, 2025+ | as above |
| Contact Point — Depth | `intercept_ball_minus_batter_pos_y_inches` → `intercept_depth_in` | double | inches out in front of the centre of mass | pitch | tracked swings, 2025+ | as above |
| Swing Speed | `bat_speed` | double | mph | pitch | swings, 2024+ | NULL pre-2024 |
| Swing Length | `swing_length` | double | feet | pitch | swings, 2024+ | NULL pre-2024 |
| Adjusted Exit Velocity | `hyper_speed` | double | mph | pitch | tracked BIP + tracked fouls | **deprecated for this product (O-17)** |

**Renaming happens once**, in `dp_uc40a_kernel.BP_COLS`. No downstream function touches a raw Statcast
column name — the `metadata-mapper` requirement.

---

## 5 · `kpi-calculator` — KPI specs (all NEW-PROVISIONAL)

### BP-0 · Bat-Path Population
- **Plain language:** which swings are eligible to have a bat path measured.
- **Formula:** `description ∈ SWINGS` **and** `description ∉ {foul_bunt, missed_bunt}`; rows with
  `bat_speed < 25` mph are flagged `degenerate_path` and excluded from central tendencies but counted.
- **Why:** O-18. A bunt is a swing in the governed `SWINGS` list but not a swing path.

### BP-1 · Swing Path Profile — `swing_path_profile(level, df)`
- **Plain language:** the standard bat-path panel at any grain.
- **Returns:** swings, tracked swings, `tracking_coverage`, means and medians for attack angle and tilt,
  means for attack direction / `pull_direction` / contact side / contact depth / bat speed / swing length,
  and `ideal_aa_rate` = share of tracked swings with `attack_angle ∈ [5°, 20°]` (the glossary band).
- **Denominator:** tracked swings. **Coverage ships beside every value** so a tracking gap can never be
  read as a behaviour change.
- **Floor:** 25 tracked swings; below it every central tendency is NULL (sensor-boundary standard,
  `uc-pos-009`). Counts are never NULL. `below_swing_floor` ships on every row.

### BP-2 · Path by Pitch Group — `path_by_pitch_group(df, extra_level)`
- BP-1 at the `pitch_group` grain with PU-2 joined on. **`pitch_group` is the DPO's own mapping,
  inherited verbatim** from `PITCH_GROUP` (`dp_uc18` lineage, identical in `dp_uc20`/`dp_uc22`/`dp_uc24`):
  `FF SI FC → fastball`, `SL ST CU KC SV CS → breaking`, `CH FS FO SC KN → offspeed`, unmapped → `other`.
  `other` is retained on every panel, never dropped.

### PU-1 · Popup Signature — `popup_signature(level, df)`
- **Plain language:** how the swing on a popup differs from the swing on everything else he puts in play.
- **Population:** tracked, non-degenerate balls in play. **Floor 10 BIP** — deliberately below the 50-PA
  rate floor because this is a *contrast of means*, not a rate estimate; `n` ships on every row and every
  cell below the floor is flagged.

### PU-2 · Popup Rate — `popup_rate(level, df)`
- Popups ÷ **all** balls in play. Uses the complete `bb_type` classifier with **no tracking gate**, so it
  reconciles **exactly** with the v1.0.0 `battedball_profile.pu_rate`. The build asserts the max absolute
  difference is below 1×10⁻⁹ and fails if not.
- **PU-1 and PU-2 have different denominators on purpose** (PU-1 needs a bat path, PU-2 does not). Both
  ship; the report states the difference.

### PB-1 · Peer-Netted Delta — `peer_delta(pos, subject, metric, y0, y1)`
- **Plain language:** the subject's year-over-year change, minus the change seen by hitters measured on
  the same instrument in the same two seasons.
- **Cohort:** Phillies batters with ≥ 200 tracked swings in **both** years (8 hitters for 2025→2026).
- **Returns:** raw delta, peer median delta, **peer-netted delta**, and the subject's rank in the cohort.
- **Why it is mandatory here:** O-16. Without it a calibration change reads as a swing change.

### ST-1 (inherited from v1.0.0)
Welch z on continuous measures, applied to every bat-path shift against two baselines. Bands unchanged
(1.5 suggestive / 2.5 clearly beyond noise). **Same standing caveat: descriptive uncertainty bands on
non-random windows, never hypothesis tests of a causal claim.**

---

## 6 · `technical-lineage-builder` — column-level lineage

| KPI | Source columns | Hops |
|---|---|---|
| BP-0 population | `description`, `bat_speed` | pitch → `game_type=='R'` → `description ∈ SWINGS` → drop `foul_bunt`/`missed_bunt` → flag `bat_speed < 25` |
| BP-1 tracking coverage | `attack_angle`, `description` | BP-0 → `attack_angle.notna()` ÷ all BP-0 swings |
| BP-1 attack angle / tilt / direction | `attack_angle`, `swing_path_tilt`, `attack_direction` | BP-0 → tracked, non-degenerate → mean/median at `level` → NULL below the 25-swing floor |
| BP-1 `pull_direction` | `attack_direction` | as above → **negate** (O-15 correction) |
| BP-1 contact side / depth | `intercept_..._x/y_inches` | as above; renamed once in `BP_COLS` |
| BP-1 `ideal_aa_rate` | `attack_angle` | as above → share in [5°, 20°] (glossary band, carried in as a constant) |
| BP-2 | + `pitch_type` | as above, grouped by `pitch_type → PITCH_GROUP` (verbatim) |
| PU-1 | + `bb_type`, `type`, `launch_angle`, `launch_speed`, `plate_z` | BP-0 tracked non-degenerate → `type=='X'` → split on `bb_type=='popup'` → means |
| PU-2 | `bb_type`, `type` | pitch → `type=='X'` → `bb_type=='popup'` ÷ all BIP (**no tracking gate**) |
| PB-1 | any BP-1 measure + `batter`, `game_year` | BP-0 tracked → per-batter-season mean → cohort filter (≥200 both years) → subject delta − cohort median delta |
| Convention assertions | + `plate_x`, `plate_z`, `stand`, `release_speed`, `hc_x`, `hc_y`, `launch_speed`, `hyper_speed` | see §2 |

**Manual carry-ins (not derivable from the log), with source:** MLB league averages (attack angle ≈ 10°,
swing path tilt ≈ 32°), the ideal-attack-angle band (5°–20°), and the 88-mph adjusted-EV floor — all from
the MLB Statcast glossary pages cited in §1. They are used **only as narrative reference points**; no
computed value in this addendum depends on them except `ideal_aa_rate`, whose band is the carry-in.

---

## 7 · `privacy-watchdog` and `data-tagger` — delta from `03`

No change to the classification: **Internal — Baseball Operations**, sensitivity **LOW–MODERATE**.
Bat-path columns are publicly broadcast Statcast measurements of a named player and add no new category
of sensitivity. One note for the player-facing surface: **§6 of the addendum report (the mechanical
hypotheses) is the part most likely to be read as a coaching directive**, and per `06` the player-facing
brief carries the mechanics without the decline framing or the roster percentile placement.

---

*Gate decision: **APPROVED.** 4 new provisional KPIs (BP-0, BP-1/BP-2, PU-1/PU-2, PB-1), 0 new business
terms minted without a cited source, 4 new open items (O-15 … O-18), 12/12 conventions asserted.
Signed off 2026-09-03.*

**Sources:** [Attack Angle](https://www.mlb.com/glossary/statcast/attack-angle) ·
[Ideal Attack Angle](https://www.mlb.com/glossary/statcast/ideal-attack-angle) ·
[Attack Direction](https://www.mlb.com/glossary/statcast/attack-direction) ·
[Swing Path (Tilt)](https://www.mlb.com/glossary/statcast/swing-path-tilt) ·
[Intercept Point](https://www.mlb.com/glossary/statcast/intercept-point) ·
[Baseball Savant swing-path / attack-angle leaderboard](https://baseballsavant.mlb.com/leaderboard/bat-tracking/swing-path-attack-angle)
