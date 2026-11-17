# 03 · Governance
Agents: `business-glossary-agent` · `metadata-mapper` · `data-dictionary` · `data-tagger` · `privacy-watchdog` · `dq-rule-definer`

## 0 · Inheritance policy (Rule-1, unchanged)
Inherited by sha256-pinned import only (K63 → K62 → K53 → K52 → K51 → K50 → K49 → K48 → K44 + `recap_viz`, `barrel_rate`, `cumulative_metric`): 12 files asserted per build.
The client function `pitch_sequence` is transcribed **verbatim** (Section B) and applied to PT-H tokens; it is never edited.

## 1 · Glossary entries (PROVISIONAL → DPO ratification, escalation #2)
| Term | Definition | Owner of meaning |
|---|---|---|
| **Pitch sequence (SQ-0)** | The ordered pitch types of one PA, joined by `-`, from the client's `pitch_sequence()` | client |
| **Sequence window (SQ-1)** | A run of k consecutive pitches inside one PA (k = 2–4), keyed by its last pitch | org (Q-C scope by DPO) |
| **Setup lift (SQ-2)** | Run value (pitcher view) of the window's last pitch minus Nola's mean for the same pitch type, count and batter side; ×100 = runs saved per 100 follow-ups | org (Q-A by DPO) |
| **Terminal ending (SQ-3)** | The last k pitches of a completed PA, scored on the PA outcome | org (Q-A by DPO) |
| **Poor contact (PC-1)** | Ball in play with Statcast `launch_speed_angle` 1, 2 or 3 (Weak, Topped, Under); denominator = tracked BIP | **DPO (Q-B)** |
| **Out PA (OUT-1)** | Completed PA whose terminal event records ≥ 1 out (K49 OU-1) | org (inherits OU-1) |
| **FADED / HELD / GREW / THIN (SQ-5)** | Era verdicts on era-internal setup lift (bars in the BID) | org, pre-registered |
| **Batterymate book (SQ-6)** | Pair-usage distribution in a catcher's starts; DISTINCT if within-season permutation p < .05 | org |
| **Predictability (PI-1)** | Next-pitch entropy given side (and previous pitch), bits | org (stretch) |
| **PT-H** | CU → KC (Nola); IN/PO/null → XX (breaks windows) | org |

## 2 · Specs filed before code
All in `BID_2026-11-16_…md` (22:47 ET). Post-compute additions, each classified by `version-controller`:
| Addition | When | Class | Why |
|---|---|---|---|
| SQ-5d decomposition (raw = base + lift) | after first era compute | non-breaking (descriptive; no bar moved) | separates "pitches got worse" from "order stopped working" |
| SQ-6 G7 robustness scope (2023–25) | after first SQ-6 compute | non-breaking (extra scope; filed test unchanged) | 2026 Stubbs starts cluster after the 7/05 pivot |
| `truncated_pa` added to non-PA terminals | before any SQ-3 receipt shipped | non-breaking (kernel v1.0.0 pre-release) | inning ended with the batter still up (1 in 2026) |
| REC-1 rows (walks + IBB; reconstructed outs) | after first REC-1 | non-breaking (disclosure) | house `nresults` excludes IBB; OU-1 misses no-event outs |

## 3 · Metadata map (`metadata-mapper`)
| Physical column | Term | Match |
|---|---|---|
| `pitch_type` → `pt` | SQ-0/SQ-1 token (PT-H) | exact (after PT-H) |
| `delta_run_exp` (negated) | run value, pitcher view (`rv100` K48 glossary, uc-pps-032) | exact |
| `launch_speed_angle` | PC-1 | exact (DPO-defined) |
| `fielder_2` (first pitch of game) | starting catcher | exact |
| `balls`, `strikes`, `stand` | count / side in LIFT_KEY | exact |
| `woba_value`, `woba_denom`, `estimated_woba_using_speedangle` | XW-1 | exact (inherited) |

## 4 · Tags (`data-tagger`)
Domain: Phillies Pitching · Subject: Aaron Nola · Sensitivity: **Public** (MLB performance data) · Product: `uc-pps-040` · Lifecycle: provisional KPIs.

## 5 · Privacy (`privacy-watchdog`)
Public-figure performance data from Statcast; no PII, no quasi-identifier risk, no health data. Catcher names are public roster facts. **Clear for external publish** (DPO decision).

## 6 · DQ rules (`dq-rule-definer`) → executed in `05`
Anchor · entity lock (O-26) · Hoffman guard · dedup · CDE completeness (`delta_run_exp`, LSA on BIP, `fielder_2`) · REC-1 (K, BB+IBB, outs, starts, games) · PT-H log ·
ASB SD-2 · catcher-name authority ×3 · SQ-0 ≡ SQ-1 token order · baseline joins ×3 · lift centering · XX drop counts · seasons row count.
