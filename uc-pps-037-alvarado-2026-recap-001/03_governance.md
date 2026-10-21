# 03 · Governance: `uc-pps-037`

Agents: `business-glossary-agent` · `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 0 · Rule-1 search (before anything was declared new)
| Candidate | Search terms | Result |
|---|---|---|
| Season profile, runs on watch, house percentile, xwOBA, same-basis wOBA, RP-1 | `nresults`, `runs_created`, `house_percentile`, `xwoba_pa`, `woba_statcast`, `house_pitcher_seasons` | **Found** (UC52 kernel → UC51 → K49/K50/K48/K44) → imported, pinned |
| Career frame | `career_frame`, `CF-2` | **Found but subject-hard-coded** (CF-2c reads K52 constants) → **CF-2d** non-breaking generalization |
| Cumulative wOBA by PA | `cumulative_frame` | **Found** (house `cumulative_metric.py`) → imported, pinned. Default woba spec defective (CM-D1) → corrected spec passed as a metric dict (CM-1a) |
| Per-appearance line | `appearance_log`, `game_score`, `outing` | **Found** K49 GS-1 / US-1b → imported |
| Pre-registered verdict rule | `signature_verdict`, `strength_from_signatures` | **Found** K48 PA-1 → imported |
| CSW% | `csw` | **Found**: locked glossary term (uc-pps-018 `03`), no kernel function → computed inline to the locked definition |
| Blow-up / clean outing | `blow.?up`, `clean outing`, `volatil` | **Found** uc-pps-028 CN-3 (starts: runs ≥5 or outs <12; provisional) → thresholds don't transfer to relief → **OD-1 new, provisional** |
| Decline vs blip | `decline`, `blip`, `bounce` | **0 hits** as a KPI → **DB-1 new, provisional** |
| "Full-time reliever" over a span | `role`, `RP-1` | **Found** RP-1 at pitcher-season grain → **RP-1t** grain generalization |
| Multi-stint appearance | `multi.?stint` | Found (uc-pps-016, unratified) → not needed; one line in the outing log only |

## 1 · Business glossary
| Term | Definition | Status |
|---|---|---|
| **Tenure** | José Alvarado's Phillies regular seasons, 2021–26 | New (this UC) |
| **Runs on watch** | Runs scored during the PAs he threw (K48 `runs_created`). Not ERA, not earned runs | Approved (inherited) |
| **wOBA (house)** vs **wOBA (Statcast basis, WB-1)** | House: K44 FanGraphs weights over every PA, used for ranks. WB-1: Σ`woba_value`/Σ`woba_denom` on XW-1's own rows, the only actual set beside xwOBA | Approved (inherited; WB-1 second use) |
| **CSW%** | (called strikes + whiffs) / pitches | Approved (locked, uc-pps-018) |
| **OD-1 outing band** | Each regular-season appearance: clean = 0 runs on watch, dented = 1, blow-up ≥ 2. Not a quality score; ignores inherited runners and leverage | New, provisional |
| **DB-1 decline-or-blip ledger** | 8 signatures (6 decline, 2 blip) with registered bars, scored by PA-1 against pooled 2022–24; roll-ups by PA-1; call by the rule in §2. A grade of 2026, **not** a 2027 forecast | New, provisional |
| **AB-1 automatic pitch** | A log row with `description` automatic_ball/automatic_strike and no `pitch_type`: no pitch was thrown | New (defect term) |
| **RP-1t** | RP-1 over a span: starts ≤ 20% of games summed over the span | Generalization |

## 2 · KPI specifications (`kpi-calculator`), written before code; the harness implements from these
**OD-1 `outing_bands`** · grain: appearance (`game_pk`) · population: regular-season appearances 2021–26 · formula: r = Σ over his PAs of (max `post_bat_score` − min `bat_score`); band clean if r = 0, dented if r = 1, else blow-up · edge: an appearance with no completed PA has r = 0 · companion `damage_top5` = Σ r of the five highest-r appearances ÷ season Σ r · test: DQ-11.

**DB-1 ledger** (REGISTERED 2026-10-18 ~11:00 ET in `dp_uc53_kernel.py`, before any 2026 rate was computed by this UC):
| Sig | Hypothesis | Metric (2026 vs pooled 2022–24) | Predicted direction | Bar (PA-1 threshold) |
|---|---|---|---|---|
| D1 | decline | sinker mean velocity | down | 1.0 mph |
| D2 | decline | cutter mean velocity | down | 1.0 mph |
| D3 | decline | cutter whiff per swing | down | 6 pts |
| D4 | decline | chase rate, all pitches (K44) | down | 4 pts |
| D5 | decline | zone rate, all pitches (K44) | down | 3 pts |
| D6 | decline | (K − BB) / PA | down | 5 pts |
| B1 | blip | wOBA − xwOBA, same basis (WB-1 − XW-1) | up | .025 |
| B2 | blip | damage_top5 (season mean over baseline years) | up | 10 pts |

PA-1 verdict per signature: PRESENT (moved the predicted way ≥ bar) · WEAK (predicted way, < bar) · ABSENT (|Δ| < bar/4) · CONTRA (opposite way ≥ bar). Roll-up per hypothesis (PA-1): STRONG / SUPPORTED / MIXED / UNSUPPORTED. **Call:** decline ∈ {STRONG, SUPPORTED} and blip not → DECLINE; blip ∈ {STRONG, SUPPORTED} and decline not → BLIP; both → DECLINE WITH NOISE; neither → UNRESOLVED. Baseline rationale: 2022–24 are the three full Phillies seasons with the cutter as a primary pitch. 2021 precedes that, and 2025 is a 28-game partial season around CI-3. Sensitivity: the same bars against pooled 2021–25.

**CM-1a `WOBA_SC_SPEC`** · CM-1 cumulative frame with numerator `woba_value` only where `woba_denom > 0`, denominator Σ`woba_denom`, floor 25 · endpoints asserted equal to WB-1 by season (tol 1e-9).

**CF-2d `career_frame_for`** · CF-2c with (pid, file, name, display) as arguments; same precedence, extras and fan-out assert.

**RP-1t `tenure_role`** · games and starts (starter = pitcher of the game's first pitch) summed over 2015–26; RP when starts ≤ 0.2 × games.

## 3 · Technical lineage (published numbers)
| Published number | Receipt | Built from |
|---|---|---|
| Leaderboard (§2, F1) | `house_pa_leaderboard.csv` | house log 2015–26 → K44 `nresults` by pitcher → RP-1t |
| Year table, F2, F7 | `career_by_year.csv` | CF-2d → profile (K44, K48, K50, WB-1, CSW) |
| Cutter / sinker by year (F5, F6) | `pitch_types_by_year.csv`, `fc_si_pitches.csv` | CF-2d by pitch type |
| Putaway / whiff context (F3, F4) | `house_putaway_pitcher_pitch.csv`, `house_whiff_pitcher_pitch_season.csv` | house log → K44 |
| Monthly 2026 | `monthly_2026.csv` | 2026 frame by month |
| OD-1 (F8) | `appearance_log.csv`, `outing_bands_by_year.csv` | GS-1 → OD-1 |
| Cumulative (F9) | `cumulative_woba.csv` | CM-1 with CM-1a spec |
| DB-1 (F10, §8) | `db1_ledger.csv`, `db1_ledger_sensitivity_2021_25.csv` | metrics above → PA-1 |
| HP grades (§9) | `hp_grades.csv` | client frame → K44 / CM-1 default |
| Every narrative number | `headlines.json` → `dp_uc53_narrative.py` | all of the above |

## 4 · Defect exposure
| Defect | Exposed here? | Evidence |
|---|---|---|
| K44 D-1/D-2 (`whiff_rate` inner join drops zero-whiff groups) | Yes (1 group) | whiff population 897 pitcher-pitch-seasons; the dropped group would rank last; no rank changes |
| K44 D-7 / O-13 (null zone counted in-zone) | Yes (16 rows, all AB-1) | DQ-08 WARN; 2026 zone 42.2% house vs 41.4% thrown |
| K44 O-8 (untracked BIP not hard-hit) | Latent | hard-hit uses all BIP; disclosed |
| WB-1 basis trap (UC52) | Guarded | xwOBA only beside WB-1 |
| **CM-D1** (new) | **Yes** | 9 tenure PA ends with `woba_value` > 0 and `woba_denom` 0/NaN (IBB 0.4, sac bunt 0.9); default line ends 2026 at .360 vs .351 |
| **AB-1** (new) | **Yes** | 16 rows in 2026 (15 automatic balls, 1 automatic strike); in pitch counts and usage denominators |
| **RK-2** (new) | **Yes, fixed** | K−BB from rounded K%/BB% printed 15.6%; from counts 15.7% (harness F caught it) |
| **ENT-1** (new) | **Yes, guarded** | 9 rows in 2018 with `pitcher == 621237` under a batter's name; DQ-05 |

## 5 · Privacy, tagging, versioning
- **Privacy:** CLEAR. Public MLB performance data; carry-ins are published reporting. The 2025 suspension and 2023 IL appear only as reported facts with sources; no medical or behavioral inference.
- **Tags:** Internal · domain Phillies Pitching · subject area reliever evaluation / roster decision support · product `uc-pps-037` · no PII.
- **Versioning:** v1.0.0, anchor 2026-10-01.
  - **v1.1.0** = a tripwire in `07` §1.
  - Changing a DB-1 bar, the baseline years or the call rule after publication is **breaking**.
  - Adopting E-2 (CM-D1 upstream) is a **correction** to the module; it does not change this UC's numbers.

## 6 · Ratification path
| Object | Recommendation |
|---|---|
| WB-1 (UC52 → UC53) | Ratify (second clean use) |
| RP-1 (UC52 → UC53) | Ratify (second clean use) |
| CF-2d | Upstream as the parameterized CF-2c in the next kernel |
| OD-1 | Provisional; second use needed (any reliever recap) |
| DB-1 | Provisional; second use needed. Reuse the bars as registered, or register new ones before reading data |
| CM-1a | Retire once E-2 lands upstream |
