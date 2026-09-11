# Trea Turner — Whole-Field Directional Tendency

`uc-pos-016-turner-whole-field-directional-001` · UC #42 · **v1.1.0** (`dp_uc42a`) · supersedes **v1.0.0**
(`dp_uc42`) · **READY-CONDITIONAL** · both delivered 2026-09-10

## Start here

| If you want… | Open |
|---|---|
| **To poke at it** | `dp_uc42a_turner_whole_field_dashboard.html` — double-click, opens in any browser, no network needed. Five scenes, season-framed, spray chart and pitch map cross-linked on hover. |
| The verdict and the caveats, written out | `dp_uc42a_turner_whole_field_report.md` |
| The animated version in your own notebook | `dp_uc42a_context_animation.py` — **run it once before trusting it**, see condition 5 in `05` |
| What the org decided for you, and what still needs your sign-off | `00_dpo_orchestration_record.md` §9.7 |
| What broke in v1.0.0's paperwork | report §7, or `03` §7 — defect **V-1** |
| The raw rows | `out/dp_uc42a_turner_bip_extract.csv` (1,832 balls in play) · `out/dp_uc42a_turner_pitch_extract.csv` (9,485 pitches) |
| What this cost | `BID_ADDENDUM_2026-09-10_uc-pos-016_v1.1.0.md` + `07` §Bid vs. actual |

## The finding, in one paragraph

Your stated theory — that Turner is pulling outside-zone pitches too often in 2026 — **is not supported**: his
2026 outside-zone pull rate (39.4%, n = 71) is statistically indistinguishable from his pooled 2023–2025 rate
(**43.3%, n = 240**), z = −0.58, and points the opposite way from the premise. The real shift is **inside the
zone**: pull 40.1% vs 47.5% (z = −2.52), oppo 35.1% vs 29.5% (z = +2.04). v1.1.0 adds the two things that
change what to do with that. **It was him, not the pitchers** — inside the zone, where his direction moved 7.4
points, the 2026 pitch-location distribution is statistically indistinguishable from 2023–25 (p = 0.51); *out*
of the zone, where the attack changed sharply, his direction did not move at all. **And it explains about a
fifth of the down year** — in-zone total bases per ball in play fell .622 → .515, of which the directional
mix change accounts for 20%; 86% is every direction producing less than it used to.

> *v1.0.0's README stated the pooled figure as 36.7% (n = 228). That was wrong — it disagreed with v1.0.0's
> own shipped receipts, which said 43.3% / 240. Corrected here as defect **V-1**; the verdict is unchanged.*

## What changed in v1.1.0

1. **Your spray-chart correction, implemented both ways.** The chart v1.0.0 built was a pitch map. Both now
   ship, **cross-linked on a shared pitch key** — hover a batted ball and the pitch that produced it lights up
   on the other chart. That link is what made the attack-stability control (`PM-1`) possible.
2. **Season frames**, per your call on v1.0.0's open decision §7-3. The static facet grid is superseded, not
   deleted.
3. **Your context cell, governed and animated** — and corrected: plotting runs created (a count) against
   barrel rate (a rate) lets playing time masquerade as a barrel-rate effect. `RC-1` normalizes it; the raw
   axis is one toggle away. The cell's own title does not survive that correction — see `00` §9.7-4.
4. **Six new provisional objects**, all Rule-1 searched: `RC-1`, `PM-1`, `PM-2`, `DC-1`, `slg_bip`, `pitch_uid`.
5. **Verification grew from 33 checks to 155**, including 20 that reproduce v1.0.0 exactly before anything new
   was added, and 32 new ones that check the prose agrees with the receipts.

## Three things that need your confirmation

1. **The six new objects are unratified.** `PM-1` most sharply: it is the first χ² anywhere in this repo, and
   only its null arm has fired where it matters. A control that has never been shown to *detect* an in-zone
   change should not yet be fully trusted to have ruled one out — and the in-zone conclusion rests on it.
2. **`dp_uc42a_context_animation.py` is shipped untested.** `plotly` could not be installed in the build
   sandbox. Its data half was exercised; the figure builders were not.
3. **Paste the reissued ledger patch, not the original.** The v1.0.0 patch carries V-1. It was never pasted,
   so nothing has propagated.

Still open from v1.0.0: `tt_whole_field_uc.md` and your sketch **still have not reached a session**, so
`sort_rank` remains unreconciled against your own draft.

## Package contents

```
README.md                                    — this file
00_dpo_orchestration_record.md               — v1.0.0 spine + §9 v1.1.0 amendment
01_strategy_intake.md                        — gaps, premise stress-tests (P4–P6 new), source fitness
02_engineering_design.md                     — data model, EDA, design decisions, joins
03_governance.md                             — Rule-1 searches, object register, lineage, defects, versioning
04_engineering_build.md                      — build manifest, environment disclosures, assertions
05_quality_certification.md                  — DQ scorecard, defect register, 155-check verification, cert
06_consumer_success.md                       — how to read it, dashboard spec, reuse patterns
07_platform_marketing.md                     — monitors, cost audit, bid vs. actual, calibration findings
BID_2026-09-10_...md                         — the v1.0.0 competitive bid
BID_ADDENDUM_2026-09-10_..._v1.1.0.md        — the v1.1.0 revision, priced retrospectively (it was unbid)
uc_ledger_AI_PATCH_..._v1.1.0_REISSUED.md    — PASTE THIS ONE
uc_ledger_AI_PATCH_...md                     — v1.0.0 patch, superseded (carries V-1), kept for the record

dp_uc42a_kernel.py                — addendum kernel; IMPORTS dp_uc42_kernel rather than copying it,
                                    adds 7 verbatim Baseball Functions transcriptions + 6 new objects
dp_uc42a_build.py                 — the build; reproduces v1.0.0's tables first, then extends
dp_uc42a_build_dashboard.py       — tpl/ + receipts -> self-contained HTML
dp_uc42a_context_animation.py     — Plotly, for JupyterLab (UNTESTED — see 05 condition 5)
dp_uc42a_verification.py          — 155 checks, six families
tpl/style.css · tpl/body.html · tpl/app.js  — dashboard sources, assembled at build time
pq_reader.py                      — build-time-only pure-Python Parquet reader (unchanged from v1.0.0)

dp_uc42a_turner_whole_field_report.md        — the v1.1.0 narrative
dp_uc42a_turner_whole_field_dashboard.html   — the interactive dashboard

dp_uc42_*                         — v1.0.0, UNTOUCHED and still runnable
out/dp_uc42a_*                    — 15 receipts + the dashboard payload (see 04 §Receipt manifest)
out/dp_uc42_*                     — v1.0.0's receipts, untouched
```

## Reproducing this

```bash
# from this folder, with phils_{2023..2026}.parquet reachable the normal way
export DP_UC42_DATA="C:/Users/Kellen/OneDrive/Documents/Python Scripts/MLB"

python dp_uc42a_build.py             # writes every receipt into out/
python dp_uc42a_build_dashboard.py   # rebuilds the dashboard from tpl/ + out/
python dp_uc42a_verification.py      # 155 checks; non-zero exit if any fails
python dp_uc42a_context_animation.py # writes the three Plotly HTML figures (needs plotly)

# to include the 20 parent-reproduction checks, point the harness at v1.0.0's receipts:
DP_UC42_V1_OUT=./out python dp_uc42a_verification.py
```

`dp_uc42a_kernel.py` uses `pandas.read_parquet` when pyarrow is present (your `snakes` env) and falls back to
`pq_reader.py` only when it is not. `dp_uc42a_verification.py` **skips loudly** rather than passing silently
if v1.0.0's receipts are not found.

## Governed objects: inherited vs. introduced

| Object | Status |
|---|---|
| `derive_loc`, `hit_direction`, `in_zone`, `pooled_two_prop_z`, `directional_rate_table` | Inherited verbatim from `dp_uc42_kernel.py` / `dp_uc40_kernel.py` / `Baseball Functions.ipynb` |
| `get_stats`, `measure_calcs`, `mcgs`, `nresults`, `runs_created`, `hard_hit_rate`, `barrel_rate` | **Transcribed verbatim**, defects included, then measured against this build (`out/dp_uc42a_defect_exposure.csv`) |
| `RC-1`, `PM-1`, `PM-2`, `DC-1`, `slg_bip`, `pitch_uid`, `DIRECTION_COLORS` | **New in v1.1.0**, provisional, unratified |
| `sort_rank`, `WF-1`, `WF-2`, `P_THROWS_COLORS`, `MARKER_SIZE` | New in v1.0.0, **still provisional** |

Full detail, including the Rule-1 evidence and why each is provisional rather than locked, is in
`03_governance.md` §4–5.
