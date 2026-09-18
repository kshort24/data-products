# uc-pos-017 · Directional Hitting Function Family
**UC #46 · `dp_uc46` v1.0.0 · delivered 2026-09-17 · CONDITIONALLY CERTIFIED**
**Verification 130/130 PASS (A–E 49/49 · F 74/74 · Gate 7 7/7) · DQ 17 PASS / 1 WARN / 0 FAIL**

A **library** build. The deliverable is a certified function family for
`Baseball Functions.ipynb` — the guidebook to the MLB repository — not an analysis.

## What shipped

| File | What |
|---|---|
| `dp_uc46_kernel.py` | The seven certified functions. **This is the deliverable.** |
| `dp_uc46_verification.py` | Families A–E · 49 checks · hand-computed fixtures, real-data invariants, parent reproduction |
| `dp_uc46_family_f.py` | Family F · 74 checks · every prose figure recomputed from receipts |
| `dp_uc46_notebook_reconcile.py` | **Gate 7** · 7 checks · executes the patched notebook's own cells and diffs them against the module |
| `dp_uc46_build.py` | Validation run → 10 CSV receipts |
| `dp_uc46_dq.py` | 18 DQ rules, executed |
| `dp_uc46_scorecard.py` | Notecard generator |
| `dp_uc46_report.md` | Findings from the validation run |
| `00`–`08` | Governance spine |
| **`07_FUNCTION_CERTIFICATION_CHECKLIST.md`** | **The reusable ten-gate admission standard.** Domain-independent. |
| `09_notebook_patch.md` | Exact cell replacements for the guidebook |
| `out/` | 10 receipts + `headlines.json` + notecards HTML |
| `telemetry/` | Bid vs actual, calibration |

## The functions

```python
import dp_uc46_kernel as k

bip = k.build_bip(['player_name'], pos)          # gate → derive → classify → assert

k.direction_rate(['player_name', 'game_year'], bip)
#   n_bip · pull_n · straight_n · oppo_n
#   pull_rate · straight_rate · oppo_rate        ← sum to 1 (DR-3)
#   below_floor                                   ← 25 classifiable BIP (FL-1)

k.bb_type_profile(['player_name'], bip)
#   bips · total_level · share
#   n/min/max/mu/std/p5/p95  ×  {la, ev, dist}    ← each sensor its own n

k.bb_type_profile(['player_name', 'hit_direction'], bip)   # oppo_ld_rate lives here
#   .query("hit_direction=='Oppo' and bb_type=='line_drive'").share

k.pull_air_rate(['player_name'], bip)            # PATCHED — runs for the first time
```

Every public function is `(level, df)`. No exceptions, including the ones that
ignore `level`.

## Rulings carried

`O-7` PA-L1 ratified, cell 56 patched · `DEN-1` classifiable-BIP denominators ·
`LD-1` oppo LD / oppo BIP · `FL-1` 25-BIP floor · `DR-3` three rates publish together ·
`N-5` `(level, df)` is a repo-wide lint rule, not a per-function ruling

## Breaking change

`pull_air_rate` denominator narrowed to classifiable BIP. Published Phillies values
move ≤ 0.03pp in 2024–2026 (0.0000pp in 2024 — the season has no untracked BIP).
Consumer notice drafted in `08_version_manifest.md` §3.

## Open

`C-1` FL-1 suppression below player×season · `C-2` DQ-07 `hit_distance_sc == 0` ·
`C-3` `impl_hash` UNAVAILABLE (F1) · `O-20` `mu_la` vs `inds`' `la_mu` ·
`O-21` `(level, df)` lint rule specified, not built · `O-22` three deprecated
`pulled_air(df, level)` copies awaiting migration · `N-2` bat-path columns → v1.1.0

**Next: UC #47 / dp_uc47 · pos next uc-pos-018 · pps next uc-pps-032**
