# 05 · Quality & Certification — `uc-pos-016-turner-whole-field-directional-001`

**Agents:** `data-quality-engineer`, `certification-agent`, `version-controller`

## Scope disclosure (read this first)

This is a **diagnostic-tier build**: one subject, one narrow directional question, delivered against a
33-check independent spot-verification harness. It is **not** the ~200-700-check exhaustive independent
recompute harness a full certification-tier hitter-season review gets (`uc-pos-014` ran 711+180 checks).
That is a deliberate scope match to the ask (a single premise test, not a season review), priced explicitly
in the BID, and disclosed here rather than implied away by reusing the word "certified" without a qualifier.

## DQ scorecard

| Dimension | Result |
|---|---|
| Completeness | 0 nulls in `hc_x`/`hc_y`/`zone` for the 1,832-row BIP population (checked, not assumed — see `04`) |
| Accuracy | Coordinate-convention assertion PASSED; `hit_direction`/`derive_loc`/`in_zone` are governed and unmodified |
| Validity | `game_type` restricted to `'R'`; `batter` restricted to the confirmed MLBAM id; no schema drift detected across `phils_2023..2026.parquet` |
| Consistency | `hit_direction` classification applied identically across all four seasons and both `p_throws` values |
| Uniqueness | n/a — no multi-source concat/dedup for this single-entity, single-frame-family pull |
| Timeliness | `phils_2026.parquet` current through 2026-09-09 (one day behind build date) |
| **Comparability** | ⚠ **Watch item.** Outside-zone BIP volume differs materially by year (71-99 BIP), and the *share* of BIP that are outside-zone has trended down (20.2%→15.8%). Rates are comparable in construction but not in statistical power across years — disclosed in the report, not smoothed over. |

**22 PASS / 1 WARN (comparability) / 0 FAIL.**

## Defect register

**0 new defects found in the governed kernel.** `hit_direction`, `derive_loc`, and `in_zone` were exercised
against a population (0 untracked BIP, 0 null zone) that does not trigger any of the six previously-known
kernel defects (D1-D6/O-5/O-7/O-8) — none of those functions are even called by this build's rate
computation, and the ones that are (`hit_direction`, `derive_loc`, `in_zone`) have no open defect against
them in the register.

## Independent spot-verification

`dp_uc42_verification.py` recomputes every published count, rate, z-score, and the coordinate-convention
assertion from the raw BIP extract using plain-Python loops — a different code path from the build's pandas
`groupby` — so a shared bug would have to be duplicated by hand, not inherited by construction.

**Result: 33/33 PASS.** (12 published BIP/pull/oppo counts x 3 fields = ~check-equivalents, 4 z-scores, 4
outside-zone-share values, 1 coordinate assertion; see `out/dp_uc42_verification_results.csv` for the full
list.)

## Certification decision

**READY-CONDITIONAL.**

Conditions attached, rather than an unqualified READY:
1. The outside-zone-specific test (the literal claim in the premise) is **underpowered** (n=71 in 2026) —
   a true effect at the hypothesized size could exist without clearing significance here. This is stated
   in the report itself (§6), not just in this file.
2. **`sort_rank` and WF-1/WF-2 are new, provisional, single-use objects** (E-1) — not yet ratified, not yet
   reused a second time. Standard repo practice (per `repo-search-before-declaring-kpi-new.md` and the
   `uc-pos-014` precedent) is to promote to APPROVED only after a second independent reuse.
3. This build has not been reconciled against Kellen's own `tt_whole_field_uc.md` / sketch, because neither
   reached this session (`01` G-1). If either surfaces later with additional detail (e.g., a specific
   `sort_rank` definition already in use elsewhere), this certification should be revisited.

None of these block internal delivery; all three are exactly the kind of condition a READY-CONDITIONAL
status exists to carry forward explicitly rather than silently resolve.

## Versioning

**v1.0.0, new use case** — no prior version to compare against. `version-controller` classification: n/a
(first delivery).
