# 02 — Engineering Design

**Department:** Engineering (Design) · **Use Case:** `uc-pps-026-cortes-acquisition-001`
**Agents:** `data-architect` · `kpi-calculator` · `eda-agent` · **Date:** 2026-08-20
**Gate order honored:** this file and 03 were written before any build code ran.

---

## 1. data-architect — model blueprint

**Grain:** pitch (source) → appearance (game) → season → phase. Entity key `pitcher == 641482`
enforced at load; dedup on `(game_pk, at_bat_number, pitch_number)`; `game_type == 'R'` for all
rates. Postseason (D/L/W) rows loaded once into a separate context frame, never joined to rates.

**Phase tiers (never blended, PA floors declared):**

| Phase | Seasons | Rationale |
|---|---|---|
| `2019 (NYY relief/bulk)` | 2019 | his only high-volume relief season |
| `2021 transition` | 2021 | bullpen → rotation conversion year |
| `2022 peak` | 2022 | All-Star season, career-best results |
| `2023-24 decline` | 2023–24 | the "fallen off" window under test (P5) |
| `2025 final (MIL→SD)` | 2025 | injury-interrupted last look, 599 pitches — **directional, below full-season floor; never quoted without its PA** |
| *excluded from phases* | 2018 (108 p), 2020 (165 p) | below floor; retained in season grain only |

**Appearance grain (the deployment spine).** One row per `(game_pk)`: entry inning
(`inning.min()`), exit inning (`inning.max()`), innings-delta (DPO definition), innings-appeared
(`inning.nunique()`, cross-check), pitches, unique PAs, entry score state, rest days (appearance-
date diff — `pitcher_days_since_prev_game` is 64% complete in 2018 and is not used).

## 2. kpi-calculator — locked inheritance + new KPI family

**Locked, inherited VERBATIM from `dp_uc29`/`dp_uc30` (no re-derivation):** `get_stats`/`nresults`,
`whiff_rate`, `chase_rate`, `putaway_rate`, `fpsr`, `hard_hit_rate`, `csw_rate`, `xwobacon`
(BIP-only, uc-pps-021 O1 hardening), `zone_rate_strict` (O2 hardening), `tracked()` population
rule, movement/thirds/count-state helpers. SWINGS/WHIFFS lists = the 8/5-value canonical lists
carried by the dp_uc29 exemplar.

**Rule-1 search performed before declaring anything new** (repo-search-before-declaring-kpi-new):
- `grep bulk|opener|start_share` across `data-products/`, `contract/`, MLB `dp_uc*.py` →
  `dp_uc16_bullpen_games_inventory.py` governs an **opener proxy** (`starter_bf <= 9`, game-level,
  team-wide pps frame) and an appearance grain, but **no start_share / bulk_share / bulk
  definition exists anywhere in the repo**. The DPO's notebook logic is therefore NEW, specced
  below, with dp_uc16 cited as adjacent prior art (different frame, different question).
- No prior UC on this subject (`ls data-products/ | grep -i cortes` → only this folder).

### NEW KPI family — UD (Usage & Deployment), DPO-supplied logic inherited from the use case

| ID | Name | Formula (grain: season unless noted) | Notes / edge cases |
|---|---|---|---|
| UD-1 | Start Share | `starts / games`, start ⇔ appearance `entry_inning == 1` | matches DPO notebook (`inning_start == 1`) |
| UD-2 | Bulk Share | `bulks / games`, bulk ⇔ `entry_inning > 1 AND innings_delta > 2` | **DPO definition verbatim**; `innings_delta = exit_inning − entry_inning` |
| UD-3 | Innings per Game | `Σ innings_delta / games` | DPO definition. **Disclosed limitation:** delta counts innings *spanned minus one* (a single-inning outing scores 0). `innings_appeared` (nunique) ships alongside as the cross-check; classification thresholds always use delta so the DPO's notebook reproduces exactly. |
| UD-4 | PAs per Game | `Σ unique PAs / games` | DPO notebook (`uq_pas`) |
| UD-5 | Relief Share | `(games − starts) / games` | complement, incl. bulks |
| UD-6 | Season Role Label | start-heavy ≥ .70 UD-1 · relief-heavy ≥ .70 UD-5 with UD-2 < .15 · bulk/hybrid otherwise | report-local label, derived only from UD-1/2/5; receipted per season |

Population: R rows, appearance grain. Null handling: none required (inning always populated);
seasons with < 3 appearances flagged `small_season`. **Edge case priced:** an extra-inning or
suspended-game entry cannot produce `entry_inning == 1` falsely; verified by min-entry audit.

### Driver analysis design (Business Question 4) — no new governed KPI required

- **ED-1 Era Delta** (pattern reuse: `role_conversion_delta` from dp_uc29, relabeled generically):
  signed peak-vs-decline process deltas (`2022 peak` vs `2023-24 decline`), both denominators
  printed, favourable-direction column so no delta is mis-signed.
- **ED-2 Outing-quality split:** career R appearances with ≥ 10 BF, split into good/bad terciles
  by per-outing wOBA-against, then process KPIs (FF velo, IVB, zone_strict, fpsr, chase, whiff)
  compared across terciles. Directional by construction; every cell prints its N.
- Season-level indicator table (velo/spin/IVB/whiff/chase/zone/fpsr/hh/xwobacon vs results) for
  the correlation read — with 8 seasons, r-values are **not** printed as inference, only ranked
  co-movement with the caveat stated.

## 3. eda-agent — pre-build observations feeding the design

2019 shows his relief/bulk mixed usage (33 G); 2021 is the live conversion year; FF-FC-ST is the
modern three-pitch core with CH reserved mostly for RHB (matches the DPO's subtitle in the use
case's own figure); 2025's two MIL games are starts in March/April, the six SD games are August
relief — the appearance grain must not average across that boundary, so 2025 splits into
`2025-MIL` / `2025-SD` stints in the outing log (season grain keeps 2025 whole, disclosed).

## 4. dashboard-specifier — consumable spec (implemented in `dp_uc36_build_dashboard.py`)

Self-contained HTML, **plotly.js inlined (vendored, not CDN — uc-pos-011 standing rule)**.
Views: (V1) deployment timeline — stacked start/bulk/relief appearance shares by season with
UD-3/UD-4 hover; (V2) arsenal evolution — usage by pitch × season, faceted L/R (the DPO's own
plotly pattern from the use case, adopted); (V3) stuff tracker — velo/spin/IVB/HB by season for a
**pitch-type dropdown** (DPO's interactive pattern, adopted as spec'd in the use case); (V4)
platoon board — phase × stand KPI cards. Every view footnotes its CSV receipt. Surfaces round
once, from full-precision receipts (dp_uc35 D4-family rule).
