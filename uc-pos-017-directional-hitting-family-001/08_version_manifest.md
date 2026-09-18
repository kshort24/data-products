# 08 · Version Manifest & Consumer Notice
**`dp_uc46` v1.0.0 · 2026-09-17 · classification: MAJOR (breaking)**

## 1. Change classification

| Change | Class | Rationale |
|---|---|---|
| `hit_direction` extracted as a standalone function | **non-breaking** | Behaviour byte-identical to cell 56; family C confirms |
| `derive_loc` ratified and published | **non-breaking** | New object |
| `direction_rate` published | **non-breaking** | New object; supersedes a provisional that was never published outside `dp_uc42` |
| `bb_type_profile` published | **non-breaking** | New object; share arm reproduces cell 50 exactly (family D) |
| `pull_air_rate` now **executes** | **breaking-by-repair** | It previously raised `AttributeError`. Nothing consumed it successfully, so nothing is broken *in practice* — but the contract changes from "raises" to "returns". |
| `pull_air_rate` denominator narrowed to classifiable BIP | **BREAKING** | Published values change. See §2. |
| `pull_air_rate` returns `below_floor` | **non-breaking** | Additive column |
| `pull_air_rate` drops the dead `total_pulls` frame | **non-breaking** | Never returned |

**Overall: MAJOR.** One breaking change drives it.

## 2. The breaking change, quantified

`pull_air_rate` v0 divided by **all** balls in play. v1 divides by **classifiable**
balls in play — those with recorded hit coordinates. An untracked BIP can no longer
be silently scored "not a pull air."

| Season | `pull_airs` | v0 denominator | v0 rate | v1 denominator | v1 rate | Δ (pp) |
|---|---|---|---|---|---|---|
| 2024 | 819 | 4,217 | 0.194214 | 4,217 | 0.194214 | **0.0000** |
| 2025 | 828 | 4,238 | 0.195375 | 4,232 | 0.195652 | **+0.0277** |
| 2026 | 712 | 3,905 | 0.182330 | 3,902 | 0.182471 | **+0.0140** |

Receipt: `out/08_breaking_change_pull_air_rate.csv`.

**The magnitude is small and that is not the point.** Three things are true at once:

1. 2024 has **zero** untracked BIP, so the change is exactly nil that season. A
   consumer who checks only 2024 will conclude nothing changed.
2. The delta scales linearly with the tracking gap. At the 0.073% gap in this
   window it is hundredths of a point. It is not bounded there — a venue or a
   season with degraded tracking moves it by as much as the gap moves.
3. The direction is always the same: v0 **understates** the rate, always, by
   exactly the untracked share. A consistent one-directional bias is worse than
   noise, because it survives averaging.

A change that is currently small is still a definitional change, and is versioned
as one.

## 3. Consumer notice (draft — for DPO issue)

> **`pull_air_rate` has changed denominators, effective dp_uc46 v1.0.0.**
>
> The function previously could not execute against the current parquet schema; if
> you were calling it, you were getting an `AttributeError`, not a number. It now
> runs.
>
> It also now divides by *classifiable* balls in play — those with recorded hit
> coordinates — rather than by all balls in play. A batted ball whose location was
> never tracked cannot be shown to have been pulled in the air, so it leaves the
> denominator instead of counting against the hitter.
>
> Published Phillies values move by at most 0.03 percentage points in 2024–2026.
> If you have a saved `pull_air_rate` figure from before 2026-09-17, re-run it.
> If you are comparing to a public source, note that public pull-air figures
> generally use the all-BIP denominator.
>
> Two directional siblings are new and were not previously available in the
> guidebook: `direction_rate` (carrying `pull_rate`, `straight_rate` and
> `oppo_rate`) and `bb_type_profile`.

## 4. Deprecations

| Object | Status | Migration |
|---|---|---|
| `pull_air_rate_fix` (`dp_uc37`, `dp_uc40`) | DEPRECATED | Call `pull_air_rate` |
| `pulled_air(df, level)` (`dp_uc24`, `dp_uc31`, `marsh`) | DEPRECATED — inverted signature | Call `pull_air_rate(level, df)` |
| `directional_rate_table` (`dp_uc42`) | DEPRECATED | Call `direction_rate(level, df)` |
| `hit_direction` transcriptions (`dp_uc37`, `dp_uc40`, `dp_uc42`) | SUPERSEDED | Import from the kernel |

**No deprecated object is deleted or edited in this release.** They live inside
delivered, certified packages whose verification receipts run against them.
Migration happens at each package's next revision.

## 5. Forward compatibility

`v1.1.0` (planned, non-breaking): bat-path columns added to `bb_type_profile` as
additional profile suffixes, gated on O-14 (`attack_direction` sign) being resolved.
Additive only — no existing column changes.
