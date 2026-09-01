# 03 · Governance — uc-pps-028 (UC #39 / dp_uc39)

**Layer 2 agents:** `dq-rule-definer` · `data-dictionary` · `data-tagger` · `privacy-watchdog`
**Status: ✅ PASS.** 28 DQ rules executed, **0 FAIL**, 2 WARN (both known, carried open defects).

---

## 1 · dq-rule-definer — rule specifications

| Rule | Dimension | Spec | Result |
|---|---|---|---|
| ENTITY-LOCK-1 | Validity | exactly one distinct `pitcher` id, equal to 666200 | **PASS** |
| ENTITY-LOCK-2 | Consistency | exactly one resolved `player_name` in the locked frame | **PASS** — `Luzardo, Jesús` |
| DEDUP | Uniqueness | 0 duplicates on `game_pk + at_bat_number + pitch_number` | **PASS** |
| GAME-TYPE | Validity | `game_type` values ⊆ {R} across all frames | **PASS** |
| **XWOBA-GRAIN** | **Accuracy** | count of non-null `estimated_woba_using_speedangle` at pitch grain **must equal** the count at PA-terminating grain — otherwise the pitch-level mean is not a per-PA xwOBA | **PASS** — 664 = 664 |
| XWOBA-COVERAGE | Completeness | <3% of PA lack an xwOBA value; the uncovered event mix is enumerated | **PASS** — 9/673 (4 `sac_bunt`, 3 `truncated_pa`, 2 untracked) |
| O-5 | Validity | `truncated_pa` present → known open defect | **WARN** — 3 rows |
| O-8 | Accuracy | untracked BIP counted as not-hard-hit by locked `hard_hit_rate` | **WARN** — 2/408 BIP; shadow rate emitted |
| CDE-COMPLETENESS × 15 | Completeness | each element ≥90% non-null **at the grain it is defined on** | **PASS** ×15 |
| START-LOG | Validity | every appearance in the subject frame is a game he started | **PASS** — 27/27 |
| CONTINUITY | Accuracy | this build reproduces the 17 figures `uc-pps-017` published for H1 | **PASS** — 17/17 within tolerance |
| H2H-RECENCY | Validity | current-era tier contains only batters with `last_faced ≥ 2025-01-01` | **PASS** |
| H2H-NAMES | Validity | every batter name resolves to a plausible 4–34 char string from `des` | **PASS** |
| FIGURES | Completeness | 5 figures rendered | **PASS** |

**Why CONTINUITY is the load-bearing rule.** This product claims to *extend* `uc-pps-017`. If it
cannot reproduce that product's published first-half numbers from the same plane, it is not an
extension — it is a second, contradictory measurement wearing the first one's name. All 17 match:
PA 465, wOBA .295, xwOBA .269, hard-hit .305, whiff .325, CSW .331, FPS .600, zone .468, chase .333,
putaway .241, K% .292, BB% .075, HR 9, IP 108.2, RA9 3.64, starts 19; FIP 2.84→2.82 (−0.02, inside
the 0.02 tolerance for a value that depends on the reconstructed-IP denominator).

## 2 · data-dictionary — published elements

| Element | Grain | Type | Definition | Source lineage |
|---|---|---|---|---|
| `game_pk` | start | int | MLB game identifier | Statcast, verbatim |
| `outs` | start | int | outs recorded, via `OUTS_MAP` over PA-terminating `events` | derived (PD-1, locked) |
| `ip` | start | str | `outs//3 . outs%3` — **reconstructed, not official** | derived (PD-1, locked) |
| `runs` | start | int | Σ `max(post_bat_score − bat_score, 0)` over PAs — **RA9 basis, not earned runs** | derived (PD-2, locked) |
| `woba` | any | float | locked `nresults` wOBA using FanGraphs season constants | Baseball Functions (locked) |
| `xwoba` | any | float | mean `estimated_woba_using_speedangle`; **per-PA**, see XWOBA-GRAIN | Statcast + DQ assertion |
| `cn1_xwoba_sd` | pitcher × window | float | population SD of start xwOBA | **NEW — CN-1, provisional** |
| `cn2_floor_rate` | pitcher × window | float | share of starts, `outs≥15 & runs≤3` | **NEW — CN-2, provisional** |
| `cn3_blowup_rate` | pitcher × window | float | share of starts, `runs≥5 or outs<12` | **NEW — CN-3, provisional** |
| `cn4_roll3_range` | pitcher × window | float | mean rolling-3-start xwOBA range | **NEW — CN-4, provisional** |
| `cn5_pitch_sd` | pitcher × window | float | SD of pitch count per start | **NEW — CN-5, provisional** |
| `cn6_outs_sd` | pitcher × window | float | SD of outs per start | **NEW — CN-6, provisional** |
| `tier` | batter | str | `current-era (faced 2025-26)` \| `historical only (pre-2025)` | **NEW — AR-1, provisional** |
| `hard_hit_rate` | any | float | locked: hard hits ÷ **all** BIP (carries O-8) | Baseball Functions (locked) |
| `hard_hit_rate_tracked` | any | float | hard hits ÷ **tracked** BIP (O-8 shadow) | derived, diagnostic only |

## 3 · data-tagger — classification

| Axis | Value |
|---|---|
| Sensitivity | **Public** — MLB Statcast is publicly published; no PII, no salary, no medical, no internal evaluation |
| Domain | Baseball Operations → Pitching |
| Subject area | Advance scouting / player performance |
| Data product membership | `uc-pps-028` · Phillies Pitching value stream |
| Retention | Session artifact; receipts retained in-package indefinitely |
| Distribution | Internal + a private hosted artifact page (owner-controlled sharing) |

## 4 · privacy-watchdog

**No privacy risk identified.** Every element is public Statcast telemetry about professional
athletes performing in public. No quasi-identifier combination creates re-identification risk —
the subjects are already identified by name and MLBAM id in the public source. **One note for the
pattern library:** batter names are parsed from public play-by-play text, never joined against any
roster, contract, or medical source, so the panel cannot accidentally acquire a non-public attribute.

## 5 · Guardrails in force

| ID | Guardrail | Origin |
|---|---|---|
| **G5** | No silent filtering — every floor is emitted as a flag with its count | `uc-pps-027` |
| **G6** | An era boundary is a researcher degree of freedom: scan it, or report the claim as boundary-dependent | `uc-pps-027` |
| **G7** | A delta in only one stratum of a non-random split is a hypothesis, never a finding | `uc-pps-027` |
| **G8** *(new)* | **A superlative is not a finding until the metric behind it is named and its cohort is enumerated.** "Most consistent" must resolve to *most consistent by X, among Y, over window Z* before it may appear in a deliverable. | **this UC** |
| **G9** *(new)* | **Never publish a composite index for a contested claim.** Where a client's word maps to several measurable axes, publish the axes and let them disagree in public. | **this UC** |
| Rule-1 | Grep the repo before declaring a KPI new | repo-search memory |
| Skill #1 | Never publish a number the build script did not compute this session | `pitcher-scouting-report` |
