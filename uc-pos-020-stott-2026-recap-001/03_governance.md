# 03 · Governance
**kpi-calculator · technical-lineage-builder · privacy-watchdog · data-tagger · version-controller**

## 0 · Rule-1 search (before anything was declared new)
| Need | Hits | Disposition |
|---|---|---|
| Slash, wOBA, xwOBA, chase/whiff/swing, HH/barrel, CR-1, DR-1, RF-2/RF-2x, KP-1, PA-1, two-prop z, CM-1 cumulative + spec dicts, hitter pool, TR-1 atom | **K54** (`dp_uc54_kernel.py`, uc-pos-019) → K40 / K34 / K53 → K52 → K51/K50/K48/K44, `cumulative_metric.py` | **Inherit by import** (pin `1a31b30a…` + 12 through K54) |
| Bat path: BP-0 population, BP-1 profile, conventions C1–C8 (O-15 sign, C2 depth), `peer_delta`, sensor boundaries | **K40a** (`dp_uc40a_kernel.py`, uc-pos-014 v1.1.0) | **Inherit by import** (pin `807986c0…`) |
| Client functions `nresults`, `chase_rate`, `whiff_rate`, `hard_hit_rate`, `bb_type_by_level` | K44 (Baseball Functions verbatim) | Inherit (HP family only) |
| Client `inds`; `barrel_rate` | `Baseball Functions.ipynb` (IX-1 extraction) · `barrel_rate.py` (pinned in the K53 chain) | Inherit (HP family only) |
| Stott approach change, first-pitch-strike collapse | uc-pos-010 / dp_uc33 receipts | Cite; not recomputed |
| Era detection from data | RC-5 scans requester dates; TR-1 tests one date | **0 hits → ER-1 (new)** |
| Good-vs-Bad signature test on labelled eras | TR-1 (one date, pre/post) | **GS-1 = TR-1 generalized** (same PA-1 rule; new signature set) |
| Infield expected outs | UC5 (hit-location credit, left side, 2026 to June); XO-2 (CF neighbourhood) | **0 hits for infield neighbourhood → IO-1 (new)** on XO-2's machinery; UC5 kept as the method check |

## 1 · Inheritance manifest
`dp_uc55_kernel.py` imports `dp_uc54_kernel` and `dp_uc40a_kernel` by path and re-asserts 14 sha256 pins at every run (`assert_lineage`). Nothing is copied. The dashboard shell is carried from `dp_uc54_build_dashboard.py` by a recorded generator (`_dp_uc55_make_dashboard_builder.py`). Figure helpers (`base`, `ship`, brand walk) are carried from UC54.

## 2 · KPI specs (kpi-calculator) — written before code, BID 19:27 ET
### ER-1 form eras
- **Atom:** per PA, `num` = house-weight wOBA numerator, `den` = AB + uBB + SF + HBP (K40 verbatim). The ER-1x basis is XW-1's atom.
- **Split:** maximize the weighted SSE gain over split points with both sides ≥100 PA. Accept the split if the share of 500 within-segment order permutations (seed 55) with gain ≥ observed is < .10. Repeat on the best remaining segment until 3 segments or no acceptance.
- **Labels:** segment rate vs career rate (same basis): Good ≥ +.020, Bad ≤ −.020, else Par.
- **Receipts:** `er1_segments_*`, `er1_tests_*`, `er1_power_*` (post-hoc power, labelled), `client_split_*` (the client's split gain vs the same season's max-gain null).
- **Result:** wOBA, no season splits (first-split p .12–.46). xwOBA: 2022 only (3 segments).

### GS-1 good-era signatures
- S1 xwOBA +.025 · S2 BB% +.015 · S3 K% −.030 · S4 chase −.030 · S5 whiff −.030 · S6 hard-hit +.040 · S7 barrel/BIP +.020 · S8 LD% +.030 · S9 oppo share +.030 · S10 FB% +.030.
- Proportions take `two_prop_z`. Each signature is scored with PA-1 `signature_verdict`, and the roll-up uses `strength_from_signatures`.
- Call: STRONG/SUPPORTED → DIFFERENT HITTER; MIXED → PARTLY DIFFERENT; else SAME HITTER, RESULTS RAN AHEAD.
- Frames: client pooled; client within 2023 / 2025 / 2026; ER-1x; 2026 vs 2022-25. ER-1 (wOBA) has no Good segment → NO DATA.

### IO-1 infield sector expected outs (PROXY)
- **Sector rule (BID):** the contiguous 2° spray band, around the peak, where the position records ≥50% of the outs (hit_location) in the 2023-26 pool. Result: 2B +10° to +36°, 3B −50° to −26°.
- **Opportunity:** a regular-season grounder (no bunts) in the sector with the subject at the position (Phillies fielding side).
- **Expected out:** the out share of pool grounders within the neighbourhood, with ≥10 neighbours.
- **Outs:** field_out, force_out, grounded_into_double_play, double_play, fielders_choice_out, triple_play. Errors are not outs.
- **AMENDMENT A-1 (pool), forced by the coverage gate.** BID pool = other Phillies fielders at the position. Stott *was* the Phillies 2B for most of 2023-25, so the pool was thin, and v1–v3 left 2B coverage at 57–62%. A-1 widens the **pool only** to both halves of every Phillies game: `fielder_N` is the fielding team's player on either side. The opportunity set, sector rule and out set are unchanged.
- **AMENDMENT A-2 (neighbourhood).** After A-1, v3 reached 89.3% pooled 2023-26 coverage at 2B (gate 90%). A-2 adds v4 = (EV 6, LA 8, spray 10), continuing the BID's own widening step, and selects it by the same first-to-pass rule (94.9%). 3B passes at v3 (92.1%).
- **Disclosure:** the v3 2B values were seen in the smoke test before A-1/A-2 were written. The amendments were forced by the coverage gates, not the scores. Sign stability across v1–v4 is published (`io1_sensitivity.csv`): 2B 2025 and 2026 are stable; 3B 2026 is not.

## 3 · Lineage (technical-lineage-builder)
```
phils_2015..2026.parquet ─LP-1(K49 via K54, COLS+bat-path+fielders)─▶ ph (anchor-asserted)
  ├─ batting, R, batter==681082 ─▶ s ─┬─ K40 nresults/xwoba/chase/whiff/HH/barrel/CR-1 ─▶ season_panel, season_card, monthly_2026, platoon_*, hand_group_*, velocity_*
  │                                   ├─ CM-1 cumulative_frame (reconcile=K40, tol 1e-9) ─▶ cum_woba, cum_ops, cum_checkpoints
  │                                   ├─ RF-2 / RF-2x ─▶ rolling_100pa
  │                                   ├─ pa_atoms ─▶ ER-1 ─▶ er1_segments/tests/power, client_split ─▶ label_rows ─▶ GS-1 ─▶ gs1_ledger, era_metrics
  │                                   ├─ DR-1 derive_loc/hit_direction ─▶ spray_bip, direction_shares
  │                                   └─ K40a BP-0/BP-1 ─▶ bat_path_* , stott_tracked_swings, band_contact
  ├─ batting R 2025-26 (all) ─▶ K40a assert_conventions ─▶ bat_path_conventions ; peers ─▶ bat_path_peers
  ├─ both roles R 2025-26 ─▶ BP-0 tracked ─▶ ad_band (governed middle 65%), bat_path_population_density
  └─ both roles R grounders ─▶ IO-1 sector + neighbour scoring ─▶ io1_summary, io1_sensitivity, io1_opportunities, io1_phillies_context ; UC5 check ─▶ uc5_fielded_check
headlines.json ◀─ every receipt above ─▶ dp_uc55_narrative ─▶ report.md/.pdf, dashboard ; figures read receipts only
```

## 4 · Defects found by building
| ID | Where | Finding | Disposition |
|---|---|---|---|
| SRC-4 | client frame | `pos[pos.player_name == pn]` includes spring, exhibition and postseason PA (182; 53 in 2026) | Both frames reported (HP) |
| CL-1 | client notebook | attack-direction block: `std_ad` aggregates `mean`; level includes the value | Graded HP-10; notebook untouched |
| ERA-1 | client notebook | 2025 "second half" window starts July 1, before the July 18 restart | Reproduced verbatim; flagged |
| Q-1 | F9 | numeric-string x collapsed the season axis to one category (render QA) | Fixed (numeric axis) |
| Q-2 | F7 | title claimed "every pitch group" improved; offspeed vs RHP and breaking vs LHP did not | Title rewritten; claim assertion now tests the pattern |
| Q-3 | harness | nullable `launch_speed_angle` (2 BIP in 2026) skipped by `.mean()`; governed barrel denominators keep them (O-8 family) | Harness aligned to the governed convention |
| J-1 | build | JSON default returned the object unchanged → circular-reference error | Fixed (`jdef`) |
| ENV-3 | laptop VM | `/sessions` 100% full (third occurrence) | `/tmp/pyrender`, `TMPDIR=/tmp/uc55/tmp` |
| ENV-4 | platform | commit tool re-served a cached file for a repeated staged path; two runs used stale code | Versioned staged names; escalated (`00` §5) |
| ENV-5 | laptop VM | Python 3.10 rejects nested same-quote f-strings that 3.12 accepts | Rewritten |

## 5 · Inherited exposures (disclosed, not fixed here)
TP-1 (3 truncated PA counted as PA/AB) · O-8 (4 untracked BIP count as not hard-hit) · O-16 (tilt drift) · SF-1 (0 on subject).

## 6 · Privacy (privacy-watchdog / data-tagger)
**LOW–MODERATE.** Public-figure performance data. No health, contract terms or personal data is computed. Carry-ins quote published media only, including Dombrowski's public remarks. Classification: Internal. Player-facing use is limited to chapters 1, 4 and 5 (his own line and swing). The defense comparison with named teammates (Bohm, Sosa, Arraez) and the thump ledger stay internal.

## 7 · Versioning (version-controller)
v1.0.0, new product, nothing breaking. Kernel `__version__ = "1.0.0"`. IO-1 A-1/A-2 are pre-release amendments, recorded here. Any change to the BID pool definition in v1.1 is breaking for IO-1 (numbers re-run).
