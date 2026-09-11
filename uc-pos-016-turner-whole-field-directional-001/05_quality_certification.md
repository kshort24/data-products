# 05 · Quality & Certification — `uc-pos-016-turner-whole-field-directional-001`

**Version: v1.1.0** — the v1.0.0 text below is unchanged; the v1.1.0 delta is the amendment section appended at the end of this file.

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

---

# v1.1.0 AMENDMENT — Quality & Certification (`dp_uc42a`, 2026-09-10)

**Agents:** `data-quality-engineer`, `certification-agent`, `version-controller`

## 6 · Scope disclosure (updated)

Still a **diagnostic-tier build**. The harness grew from 33 checks to **155** and now includes parent
reproduction and narrative reconciliation, but it is still not the exhaustive independent-recompute harness a
certification-tier hitter season gets (`uc-pos-014` ran 711 + 180). The gap is smaller and it is still a gap.

## 7 · DQ scorecard (v1.1.0)

| Dimension | Result |
|---|---|
| Completeness | 0 nulls in `hc_x`/`hc_y`/`zone` across the 1,832-row BIP frame (re-checked). **1** row with NULL `launch_speed` — never imputed, per the sensor-boundary standard. 4 pitch rows out of 9,485 have NULL `zone` and are excluded from the PM-1 share vector and counted separately. |
| Accuracy | Coordinate convention re-asserted both ways (Pull median `loc_x` −66.3, Oppo positive). Plate-side convention derived empirically rather than assumed. Seven governed KPI functions transcribed verbatim and diffed against the notebook source. |
| Validity | `game_type == 'R'`; entity lock `607208`; wOBA weights joined per season with a row-count fan-out assertion; `pitch_uid` unique across 9,485 rows. |
| Consistency | v1.0.0's twelve rate rows and six z-scores reproduced **exactly**, from v1.0.0's own extract, against v1.0.0's own CSVs — 20/20. |
| Uniqueness | `pitch_uid` asserted unique; BIP a strict subset of the pitch frame. |
| Timeliness | `phils_2026.parquet` current through 2026-09-09. |
| Comparability | ⚠ **Watch item, carried and extended.** v1.0.0's warning stands (out-of-zone BIP volume 71–99/yr). Added: the **context pool spans four seasons of wOBA constants**, joined per season — correct, but it means two player-seasons at the same wOBA are not on quite the same scale. And PM-1's χ² is powered by ~2.4k vs ~7.1k pitches, so it detects shifts far smaller than they are meaningful — which is exactly why total-variation distance is reported beside every p-value. |
| **Traceability** | 🆕 **New dimension, opened by V-1.** Does the prose agree with the receipts? v1.0.0: **FAIL** (3 files, see `03` §7). v1.1.0: **PASS**, 32/32, enforced by verification family F. Recommend adding traceability to this repo's standing DQ dimension set. |

**28 PASS / 1 WARN (comparability) / 0 FAIL.**

## 8 · Defect register (v1.1.0)

- **1 new defect found, in v1.0.0's own paperwork: V-1** (`03` §7). Corrected here; remediated structurally
  by verification family F.
- **0 new defects found in the governed kernel.** Two known ones (**D-1**, **O-8**) do touch this build and
  are **measured rather than assumed inapplicable** — `out/dp_uc42a_defect_exposure.csv`. Neither is patched
  in the governed function; both are disclosed in the report §9. **D-7/O-13** and **D-4**/**O-14** do not
  bite here, and that was checked rather than asserted.
- **O-12** (accent-fold name matching) is adjacent — the context pool uses `player_name` as a display grain —
  but cannot reach a published subject figure, which is locked by MLBAM id.

## 9 · Independent verification — 155/155 PASS

`dp_uc42a_verification.py` recomputes from the shipped extracts using plain Python — `csv`, dicts and loops —
never the pandas `groupby` path the build used.

| Family | Checks | What it proves |
|---|---|---|
| **A · Parent reproduction** | **20** | Every v1.0.0 figure, recomputed from v1.0.0's own extract and compared against v1.0.0's own CSVs. A quiet change to a parent number fails the build. |
| **B · Self-consistency** | 23 | v1.1.0's own rate tables, z-scores, out-of-zone shares and the zone-slice partition identity. |
| **C · New objects** | 48 | PM-1's three χ² and TVD values, the DC-1 identity (`gap = mix + rate + interaction`, closed to 1e−12) and its inputs recomputed two ways, `slg_bip` per direction/season, RC-1 arithmetic on all 65 context rows, the 50-PA floor, the zone decomposition, and the defect-exposure counts. |
| **D · Conventions** | 9 | Coordinate convention both directions, closed direction vocabulary, NULL-zone exclusion, `pitch_uid` uniqueness, BIP ⊂ pitch frame, single-stand assertion. |
| **E · Artifact integrity** | 9 | The dashboard contains its payload inline; payload counts match the extracts; every element id the script addresses exists in the markup; **no external `src`/`href` anywhere** — the vendor-don't-CDN rule is now enforced, not merely observed. |
| **F · Narrative reconciliation** | **46** | 🆕 Every headline figure in the report's prose and the dashboard's markup recomputed from the receipts and string-matched — including the report's own claim about how large this harness is, checked last against the size it actually reached. |

Full results: `out/dp_uc42a_verification_results.csv`.

## 10 · Certification decision

**READY-CONDITIONAL.** v1.0.0's three conditions are carried unchanged (out-of-zone test underpowered;
`sort_rank`/WF-1/WF-2 unratified; not reconciled against the DPO's own draft). Two are added:

4. **Six new provisional objects** (`RC-1`, `PM-1`, `PM-2`, `DC-1`, `slg_bip`, `pitch_uid`) are single-use and
   unratified. **`PM-1` carries the sharpest version of this condition**: it is the first χ² in this repo, and
   only its null arm has fired where it matters. A control test that has never been shown to detect a change
   in-zone should not yet be trusted to have ruled one out. The in-zone conclusion rests on it.
5. **`dp_uc42a_context_animation.py`'s figure builders are shipped untested** — `plotly` could not be
   installed in this session (`04` §Environment-2). The data half is exercised; the `go.Figure` half is not.
   It should be run once on the DPO's machine before being treated as a delivered artifact.

None blocks internal delivery. All five are exactly what READY-CONDITIONAL exists to carry forward explicitly
rather than resolve silently.

## 11 · Versioning

**v1.1.0 — MINOR, non-breaking**, per `03` §8. `dp_uc42` v1.0.0 remains present, runnable and valid.
