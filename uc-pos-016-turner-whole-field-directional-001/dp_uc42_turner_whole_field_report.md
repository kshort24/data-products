# Trea Turner — Whole-Field Directional Tendency

**`uc-pos-016-turner-whole-field-directional-001` · UC #42 · `dp_uc42` · Phillies Offense (`pos`) value stream**
**Requested and delivered 2026-09-10 · data as of 2026-09-09 · Human DPO: Kellen Short**
**Status: READY-CONDITIONAL (diagnostic-only tier — see §7) · spot-verification 33/33 PASS**

---

## 1 · Verdict, before any explanation

| Question | Answer |
|---|---|
| Is Turner pulling outside-zone pitches too often in 2026, drifting from 2023–2025? | **No.** On outside-zone balls in play specifically, his 2026 pull rate (39%, n=71) is flat-to-slightly-*lower* than the pooled 2023–2025 rate (43%, n=240); the gap is not distinguishable from noise (z = −0.58). |
| Is there a real directional drift anywhere in the data? | **Yes — but it runs the opposite way, and it lives in-zone, not out-of-zone.** On in-zone balls in play, 2026 pull rate is 40% vs a 2023–2025 pooled 48% (z = −2.52), and oppo rate is 35% vs 30% (z = +2.04). Turner is going the other way *more*, not less — and it is happening on pitches he *should* be able to pull. |
| Should this ship as a locked KPI or a diagnostic? | **Diagnostic-only, provisional.** See §7 and the open item for the human DPO. |

**The premise, tested against the data rather than assumed, does not survive contact with the data as stated.** The 2026 directional shift is real by the repo's own uncertainty-band convention (|z| ≥ 2.5 for the in-zone pull-rate move), but it is a *smaller sample, in-zone* story, not the *outside-zone* story the working theory named. Reporting the premise as confirmed would have been the wrong finding.

---

## 2 · What was asked, and how it was scoped

Kellen's working theory (submitted as `tt_whole_field_uc.md` plus a hand sketch of the intended facet-grid layout) was that Turner is pulling too many outside-zone pitches in 2026 rather than serving them the other way, and that this is a drift from his 2023–2025 Phillies-era behavior. He asked the data-product-owner to lead the narrative against the data, not confirm the premise, and flagged three open decisions for this layer to resolve rather than default silently: (1) static facet grid vs. an animated-frame layout, (2) formal locked KPI vs. diagnostic visual, (3) ledger ID assignment. He also supplied four corrections to carry in without re-deriving them (source-of-truth data, `hit_direction` reuse, a locked `p_throws` color map, a fixed marker size) and one gap to close rather than silently generalize (`sort_rank`'s handedness scope).

**Data-plane intake note (blocking for full fidelity, non-blocking for delivery):** the two files Kellen said he was attaching — his working markdown and a photo of the hand-drawn sketch — did not arrive in this session (checked the connected folders, the upload area, and the Agents-repo `data-products/` and `Claude outputs/` directories; neither file exists in either repo). The prompt text itself was detailed enough to build from directly, and is treated here as the intake document of record. The one place this genuinely bites is `sort_rank`: it is invoked in the prompt as something that *already exists* with a known RHB-only bug, but it does not appear anywhere in the repo (`Baseball Functions.ipynb`, the kernel lineage, or the spray-chart skill) — only `hit_direction` does. Rather than guess at undocumented prior logic, this build ships a **new, handedness-correct `sort_rank`** (§4) built the right way from the start, and flags the gap for Kellen to reconcile against his own file when he re-attaches it.

## 3 · Data position — verified at build time, not assumed

| Check | Result |
|---|---|
| Source | `data/phillies/phils_{2023..2026}.parquet` — repo's governed cache, read via `get_phillies_data()`'s on-disk contract (Kellen's data-plane rule: no Baseball Savant CSV exports) |
| Freshness | `phils_2026.parquet` covers through **2026-09-09** (yesterday relative to this build) |
| Entity lock | `batter == 607208` (`SUBJECT_MLBAM`, confirmed twice before in this repo — `uc-pos-006`, `uc-pos-014`) |
| Grain | Pitch-level, filtered to **balls in play** (`type == 'X'`), by Turner, regular season only (`game_type == 'R'`) for cross-year comparability |
| Coordinate source | `hc_x`/`hc_y` (raw Statcast) → `loc_x`/`loc_y` via the governed `derive_loc()` transform (origin `(125.42, 198.27)`, y-flipped, `HC_SCALE = 2.495671`) — **not** hardcoded per file, inherited verbatim from `dp_uc40_kernel.py` (itself sourced from `cbp-spray_AI.md` §Data Quality rule 1) |
| `hit_direction` | Governed, stand-aware, ±4.7-slope classification — **verbatim** from `Baseball Functions.ipynb` cell 56 (`pull_air_rate`) via the `dp_uc40_kernel.py` extraction. Not redefined here. |
| Zone convention | Governed `in_zone()` operator: `zone < 10` (zones 1–9); **NULL-zone rows excluded from both populations** (same convention used to fix the repo-wide D-7/O-13 defect) |
| Handedness | Turner is **100% `stand == 'R'`** in this dataset (2023–2026, 9,485 regular-season pitch rows) — the L-branch of `hit_direction` and the new `sort_rank` is implemented and documented, but not exercised by this subject |
| Untracked BIP | 0 rows with null `hc_x`/`hc_y` in Turner's BIP population (2023–2026) — the D6/O-8 untracked-BIP caveat does not apply here |
| Volume | 1,832 regular-season BIP, 2023–2026 (2023: 490, 2024: 408, 2025: 484, 2026: 450) |
| Duplicates | n/a — single-player pull, no cross-source concat/dedup needed |

## 4 · Known corrections carried in, and how each was implemented

| # | Correction requested | How it was implemented |
|---|---|---|
| 1 | Source from the repo's `pos` dataframe / `get_phillies_data()`, not local Savant CSV exports | Read `data/phillies/phils_{2023..2026}.parquet` directly (the same on-disk contract `get_phillies_data()` serves from); `hit_direction` computed with the governed function, not re-derived |
| 2 | Lock the `p_throws` color map — it currently remaps per call/facet | `P_THROWS_COLORS = {'R': '#002D72', 'L': '#E81828'}` (Phillies Navy / Red), passed as an explicit dict everywhere `p_throws` is colored — never left to implicit categorical-order assignment |
| 3 | `sort_rank` is RHB-only as currently defined — document, don't silently generalize | No prior `sort_rank` was found in the repo (see §2 gap note); this build ships a **new**, handedness-aware version: `R` → Pull=0, Straightaway=1, Oppo=2; `L` → Oppo=0, Straightaway=1, Pull=2. This keeps the physical field reading (negative `loc_x` = left side of the chart) consistent regardless of batter side, rather than reproducing a one-side-only ordering. **NEW-UC42, provisional pending Kellen's reconciliation against his own draft.** |
| 4 | Drop `release_speed` as marker size; use a fixed size approximating a baseball | `MARKER_SIZE` is a constant (no data-encoded size channel) on every point in Fig. 1 |
| 5 | Entity lock via MLBAM ID, not name filter | `batter == 607208` throughout; never `player_name == 'Turner, Trea'` |

## 5 · The finding

Restricting to **balls in play that came off a pitch outside the strike zone** — the exact population the working theory is about — Turner's 2026 pull rate (39.4%, 28-for-71) is not distinguishable from his pooled 2023–2025 rate (43.3%, 104-for-240; pooled two-proportion z = −0.58) and his oppo rate is essentially flat (35.2% vs 34.6%, z = +0.10). There is no outside-zone pull drift in the data, in either direction, at this sample size.

The real movement is on **balls in play off pitches in the zone**: pull rate 40.1% in 2026 vs. 47.5% pooled 2023–2025 (z = −2.52) and oppo rate 35.1% vs. 29.5% (z = +2.04) — both clear this repo's moderate uncertainty band (|z| ≥ 2.5 / ≥ 1.5, the `ST-1` convention used on `uc-pos-014`). 2026 is the **lowest pull-rate, highest oppo-rate season of the four** on in-zone contact, and the shift is not monotonic year-over-year (2024 was actually Turner's most pull-heavy in-zone season of the window) — 2026 is the outlier year, not the end of a steady trend.

Two honest caveats travel with this finding. First, the outside-zone test is **underpowered**: 71 BIP in 2026 and 240 pooled is a small population for a two-proportion test, and a true effect of the size hypothesized could exist without clearing significance here — absence of evidence is not evidence of absence at this n. Second, the share of Turner's BIP that come from outside-zone pitches at all has been trending down across the window (20.2% → 17.2% → 14.7% → 15.8%), which is itself worth a sentence: he is making contact with fewer outside pitches to test the premise on, not more.

**Bottom line:** the working theory, read literally (pull-drift specifically on outside-zone contact), is not supported. The organization's own falsify-before-describe standard (`uc-pps-027` C-1 / `uc-pps-028` G8-G9) says this gets reported as a negative finding, not softened into a directional hint. The more defensible, data-led story is a smaller-sample in-zone shift toward the *opposite* of the hypothesis — more oppo, less pull — worth tracking with more PA rather than treating as settled.

## 6 · Open decisions resolved at this layer

1. **Static facet grid vs. animated frame (Kellen's call to confirm).** This build recommends and ships the **static facet grid** — `hit_direction` (columns, RHB field-order via the new `sort_rank`) × `game_year` (rows), colored by `p_throws` — matching the layout described in Kellen's sketch and consistent with the existing `run-spray-chart-60` skill's faceting pattern (`facet_col=stand` / `facet_row=gy_color`) already in production. An animated-frame-on-season version (matching the platform's Goldsberry-style animation framework) is a straightforward follow-on if Kellen prefers it after seeing the static version — **flagged for his confirmation, not defaulted past him.**
2. **Formal locked KPI vs. diagnostic-only visual.** Ships as **diagnostic-only, with two provisional KPI candidates** (`WF-1 oppo_rate_ooz`, `WF-2 pull_rate_ooz`, §7) rather than a locked, ratified KPI. The outside-zone sample sizes here (71–99 BIP/year) are below the repo's usual rate-stat comfort zone, and the finding itself is a null result on the premise's exact claim — locking a KPI around a metric that just returned "not significant" is premature. Revisit locking after either a full-season close-out or a multi-player reuse.
3. **Ledger ID assignment.** `uc-pos-016` / UC **#42** / `dp_uc42` — verified against the ledger index and the `data-products/` directory listing (`uc-pos-015-delacruz-era-comparison-001` was the last pos-stream folder; UC #41/`dp_uc41` was Delacruz). No collision found in either namespace at build time.

## 7 · What shipped, and the honesty gate on scope

This is a **diagnostic-tier build**, not a full certification-tier season review like `uc-pos-014`: one subject, one narrow directional question, a spot-verification harness rather than an exhaustive independent-recompute harness, and no dashboard-specifier/consumer-onboarding pass beyond the single dashboard tab this question needs. That scope reduction is priced explicitly in the BID, not hidden.

New provisional objects (E-1, pending ratification before reuse):
- **`sort_rank(direction, stand)`** — NEW-UC42, handedness-aware facet ordering (§4-3)
- **`WF-1 oppo_rate_ooz`** = oppo-hit BIP / all BIP, restricted to outside-zone pitches, by `game_year`
- **`WF-2 pull_rate_ooz`** = pull-hit BIP / all BIP, restricted to outside-zone pitches, by `game_year`
- **`P_THROWS_COLORS`** — locked brand color dict, candidate for promotion to a shared brand-center constant (currently redefined per script across the repo)

**Certification: READY-CONDITIONAL.** Spot-verification (33/33) reproduced every published count, rate, z-score, and the coordinate-convention assertion from the raw BIP extract independently, using plain-Python loops rather than the build's pandas groupby path; it is not the ~200+-check harness a full hitter-season UC gets, and that gap is disclosed rather than implied away.
