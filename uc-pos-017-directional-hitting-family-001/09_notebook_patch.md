# 09 · Notebook Patch
**`Baseball Functions.ipynb` · applied 2026-09-17 by `apply_notebook_patch.py`**

## What changes

| Cell | Type | Change |
|---|---|---|
| "## Pull AIR Rate" | markdown | **v1.1.0 AMENDMENT appended.** Original text left untouched (the amend-don't-replace convention from uc-pos-016). Adds the three-change table, the breaking-change notice, the technical lineage the original cell never got, and the certification verdict. |
| `def pull_air_rate` | code | **Body replaced.** Derives `loc_*` from `hc_*` (PA-L1), denominator narrowed to classifiable BIP, dead `total_pulls` removed, `below_floor` added, NULL-safe rate. |
| *(new, after `pull_air_rate`)* | markdown | **"# Directional Hitting"** — glossary (11 terms), technical lineage (9 CDEs), DQ rule summary, open items, usage. |
| *(new)* | code | `HC_SCALE`/`HC_ORIGIN_*`/`DIR_SLOPE`/`BIP_FLOOR`/`DIRECTIONS`/`DIRECTION_COLORS`/`PROFILE_COLS`, `classifiable_bip`, `derive_loc`, `hit_direction`, `assert_spray_convention`, `build_bip`, `direction_rate`, `bb_type_profile`. |

## How to apply

```bash
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python apply_notebook_patch.py
```

Requires `_notebook_patch_payload.json` beside it. Both are committed to the repo root.

**Safety properties:**
- **Backs up first** to `Baseball Functions.ipynb.bak-<timestamp>` before writing.
- **Idempotent** — detects the amendment marker and exits without changing anything
  if it has already run.
- **Locates cells by content, not index.** Cell 55/56 are the current positions;
  the script finds `## Pull AIR Rate` and the following `def pull_air_rate`, so it
  still works if cells have moved.
- Writes `indent=1, ensure_ascii=False`, matching the notebook's existing format,
  so the diff is the patch and nothing else.

## After applying

The notebook gains `direction_rate` and `bb_type_profile` as inline definitions,
matching every other function in the guidebook. `numpy` and `pandas` must already
be imported (cell 0 does this).

**Reconciliation obligation:** the notebook is the authoring surface; the certified
module copy is `dp_uc46_kernel.py`. The two must not drift. Gate 7 of the Function
Certification Checklist is where that is checked — and it is the exact obligation
nobody held for cell 56, which is why it was broken for weeks while three kernels
transcribed it.

## Rollback

```bash
cp "Baseball Functions.ipynb.bak-<timestamp>" "Baseball Functions.ipynb"
```
