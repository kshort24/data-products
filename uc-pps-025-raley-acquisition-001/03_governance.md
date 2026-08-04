# 03 — Governance

**Layer 2 — Governance (parallel to Design)** · UC #31 · `uc-pps-025` · build `dp_uc30`
**Agents:** `business-glossary-agent` → `metadata-mapper` → `data-dictionary` → `data-tagger` → `privacy-watchdog`

---

## 3.1 `business-glossary-agent` — glossary deltas

**Governance principle 1: no agent may infer a CDE's business meaning.** Nothing in this build defines what an existing enterprise term means. Four new *report-local* terms were required; each is composed entirely from existing physical CDEs and is returned to the DPO as a promotion candidate, not published as an approved glossary entry.

### Terms inherited (no change)

`plate appearance` · `whiff rate` · `chase rate` · `called-strike + whiff rate` · `putaway rate` · `first-pitch strike rate` · `hard-hit rate` · `wOBA` · `xwOBA on contact` · `in-zone rate (strict)` · `induced vertical break` · `horizontal break` · `release extension`

### Terms introduced — report-local, promotion candidates

| Term | Composed from | Status | Promotion note |
|---|---|---|---|
| **Release Slot Angle (RSA)** | `release_pos_x`, `release_pos_z` | Report-local | Strong candidate. Generalizes to any pitcher, any hand. **Must be promoted together with its calibration requirement** (|r| ≥ 0.80 vs native `arm_angle`), otherwise it will drift into being cited as an arm angle |
| **Release Distinctiveness Index (RDI)** | `release_pos_x`, `release_pos_z` + a named population | Report-local | **Weak candidate.** Direction-blind by construction; produced a negative result here. If promoted, promote with the limitation attached, or replace with a directional (signed, two-axis) form |
| **Sightline Offset (SLO)** | `release_pos_x`, `stand` | Report-local | Strong candidate. Depends on a coordinate convention that must be asserted, not assumed — promote the DQ assertion alongside the term |
| **Release Tipping Delta (RTD)** | `release_pos_x`, `release_pos_z`, `pitch_name` | Report-local | Candidate. Has no league benchmark; promote only with the within-pitch-noise comparator, never alone |

### Conflict / duplicate scan

| Existing term | Proposed term | Verdict |
|---|---|---|
| `arm_angle` (Statcast native) | Release Slot Angle | **Not a duplicate — a documented proxy.** Different scale, different origin, correlated at r = 0.831. Naming deliberately avoids "arm angle" to prevent substitution |
| `release_pos_x` | Sightline Offset | Not a duplicate — SLO is a *distance to a batter reference point*, not a coordinate |
| CH–FF separation (uc-pps-011) | Release Tipping Delta | Not a duplicate — that measures *movement/velocity* separation between pitches; RTD measures *release-location* separation |

**Gaps returned to DPO:** none blocking. No business meaning was inferred at any layer.

---

## 3.2 `metadata-mapper` — physical → business mapping

| Physical column | Business term | Mapping | Note |
|---|---|---|---|
| `pitcher` | Pitcher identifier | Exact | MLBAM id — the entity lock |
| `release_pos_x` | Release point, horizontal | Exact | Sign convention **asserted**, not assumed (01.2) |
| `release_pos_z` | Release point, height | Exact | |
| `release_extension` | Release extension | Exact | |
| `arm_angle` | Arm angle | Exact | **Availability gap** 2015–2024 in Phillies files → RSA proxy |
| `pfx_x` / `pfx_z` | Horizontal / induced vertical break | Exact | ×12 to inches at publication |
| `zone` | Strike-zone location bucket | Exact | `> 9` = out of zone; **null ≠ in zone** — see O2 |
| `stand` | Batter handedness | Exact | |
| `description` | Pitch outcome | Exact | Drives swing/whiff/called-strike sets |
| `events` | Plate-appearance outcome | Exact | |
| `estimated_woba_using_speedangle` | xwOBA | **Ambiguous → resolved** | Pitch-level use quarantined (uc-pps-021 O1); BIP-only `xwobacon` published |
| `launch_speed` | Exit velocity | Exact | |
| `bat_speed`, `swing_length` | Bat-tracking measures | Exact | **Coverage gap pre-2023** |
| `miss_distance` | Swing miss distance | Exact | Populated on whiffs only |
| `pitcher_days_since_prev_game` | Days rest | Exact | |
| `age_pit` | Pitcher age | Exact | Source of the "age 38" claim — **not a manual carry-in** |
| `phillies_role` | Org role partition | Exact | Benchmark filter |

**Unmapped physical elements:** none used in the report.
**Ambiguous, escalated and resolved:** 1 (`estimated_woba_using_speedangle`).

---

## 3.3 `data-dictionary` — published outputs

All 21 CSV receipts carry self-describing column names traceable to the CDEs above. Column semantics that are not self-evident:

| Column | Meaning |
|---|---|
| `era` | `Pre-TJ (2020-2024)` or `Post-TJ (2025-2026)` — **never blend** |
| `zone_rate_strict` | In-zone share over **tracked** pitches only |
| `xwobacon` / `xwobacon_bip` | BIP-only mean xwOBA / its BIP count — **see O4: the count uses `size` semantics and slightly overstates the estimated-sample** |
| `rsa_proxy` | Release Slot Angle — **a proxy**, calibrated in `dp_uc30_rsa_calibration.csv` |
| `rdi` | Release Distinctiveness Index vs the 28-pitcher Phillies LHP centroid |
| `slo_ft_rulebook` / `slo_ft_body_anchor` | Sightline Offset under the rulebook box centre / the empirical HBP anchor |
| `rtd_in` / `within_pitch_noise_in` | Release Tipping Delta and its honest comparator |
| `is_raley` | Flags the two rows scored against, but excluded from, the benchmark centroid |
| `entry_state` | Score state at the moment he entered the game |

---

## 3.4 `data-tagger` — classification proposal

| Element | Sensitivity | Domain | Subject area | Product membership |
|---|---|---|---|---|
| All pitch-level source rows | Internal | Baseball Operations | Pitch Profile / Pitch Outcomes | `uc-pps-025` |
| Release-geometry receipts | Internal | Baseball Operations | Pitch Profile | `uc-pps-025` |
| Benchmark population receipt | **Internal — Restricted** | Baseball Operations | Pitch Profile | `uc-pps-025` · contains comparative evaluation of 28 named current and former employees |
| Reader report (PDF/MD) | **Internal — Restricted** | Baseball Operations | Scouting | `uc-pps-025` · contains acquisition-evaluation judgments and deployment recommendations about a current employee |
| Governance trail 00–07 | Internal | Data Governance | Metadata | `uc-pps-025` |

**Proposal only.** Final sensitivity determination is the human DPO's.

---

## 3.5 `privacy-watchdog` — risk assessment

| Check | Finding |
|---|---|
| Direct PII | **None.** Public MLBAM player identifiers and public names only. No contact details, no contract terms, no medical records |
| Medical inference | ⚠️ **Flagged.** The product is explicitly structured around a surgery. The date boundary is derived from *publicly observable appearance gaps in the pitch log* — not from any medical record — and the report makes no claim about the procedure, prognosis, or the player's physical condition beyond what the pitch data shows. **This distinction must be preserved in any downstream reuse.** |
| Quasi-identifiers | Player, team, date and pitch type are all publicly broadcast. No re-identification risk beyond public knowledge |
| Sensitive combinations | The benchmark receipt ranks 28 named pitchers on a physical delivery attribute. Innocuous individually; as a ranked list it is a comparative employee evaluation → **Internal — Restricted** |
| Employee-evaluation content | ⚠️ The report contains deployment recommendations and performance-expectation statements about a current employee, including an explicit regression forecast |
| External publication | ❌ **BLOCKED.** Governance principle 5. Internal use only |
| Aggregation risk | Low — all figures are player-level and derived from public tracking data |

**Verdict: cleared for internal distribution. External publication blocked.**
