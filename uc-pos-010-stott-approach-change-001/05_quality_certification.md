# 05 · Quality & Certification
**data-quality-engineer · certification-agent**

## Verification — `dp_uc33_verification.py`

**86 PASS / 0 FAIL.** Independent path: files read in reverse order, subject filtered *before*
role, all masks declared inline. No import of `dp_uc33_kernel`.

| § | Coverage | Result |
|---|---|---|
| 1 | population, month buckets, as-of date | 4/4 |
| 2 | monthly PA / BA / OBP / BB% / K% / OPS identity | 36/36 |
| 3 | swing / chase / whiff / OOZ-whiff / FPSR / 1st-pitch swing | 36/36 |
| 4 | AP-10 streak — 14 BB, 0 K, 11 games, 46 PA | 6/6 |
| 5 | OBP:K claim vs 217-season pool | 4/4 |

## CDE-level DQ

| CDE | Dimension | Result |
|---|---|---|
| `player_name` | validity | ✅ single value |
| `game_month` | consistency | ✅ equals `game_date` month, all rows |
| `plate_appearance_key` | uniqueness | ✅ one terminal row per key |
| `pitch_number` | validity | ✅ first-pitch count == PA count, every month |
| `description` | validity | ✅ **zero unmapped values** against governed SWINGS/WHIFFS |
| `launch_speed` | validity | ⚠ populated on fouls (**O3**) — every contact metric filters `type=='X'` |
| `zone` | completeness | ✅ non-null on all rows used as a chase denominator |

## Reliability floors

| Bucket | PA | Floor | Status |
|---|---|---|---|
| March | 13 | 50 | ❌ **below floor — flagged, not dropped, not interpreted** |
| April–July | 82–107 | 50 | ✅ |
| August | 56 | 50 | ✅ but **partial month** |
| EV90 | — | 40 BIP | NULL where unmet |

## ⚠ Three defects found in the governed kernel

Reported, **not patched in place**. `_fix` variants used for this build; originals untouched.

| ID | Function | Defect | Impact here |
|---|---|---|---|
| **D1** | `whiff_rate` | inner-merges swings→whiffs; a group with swings but **zero whiffs vanishes** | none this run (no zero-whiff month) — but latent |
| **D2** | `hard_hit_rate` | same shape; a group with BIP but zero hard hits vanishes | none this run |
| **D3** | `fpsr` | groups by `level+['type']` then returns only `type=='B'`; a group with **zero first-pitch balls (a perfect 1.000 FPSR) vanishes** | none this run (August had 33 balls of 56) |
| **D4** | `nresults` | rounds to 3dp on return; any ratio of two `nresults` rates inherits it | **material** — August BB/K reads **3.2676** from rounded rates vs **3.25** from counts |

> **D1–D3 share one root cause and one consequence.** They drop zero-numerator groups, which a
> downstream left-merge renders NaN, which a blanket `.fillna(0)` then converts into a *measured
> zero*. The DPO's working notebook contained exactly that `.fillna(0)` — **it was compensating
> for these three defects.** Fixing the merges removes the need for it.

## Caveats that must travel with the numbers
1. **Opponent quality and platoon mix uncontrolled.** No adjustment for who he faced.
2. **Regression to the mean is the null.** April was extreme; some improvement was expected without any change.
3. **August is 56 PA and partial.** Above floor, well below confirmatory.
4. **The streak window is outcome-selected.** Its BB%/K% are descriptive only.
5. **Pitcher behaviour moved further than hitter behaviour.** FPSR −26 pts vs chase −12 pts. Direction of causation is not identified.

## Certification
**READY TO PUBLISH — internal.** All artifacts present, all headlines independently reproduced,
every open item disclosed.
