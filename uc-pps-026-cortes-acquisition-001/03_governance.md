# 03 — Governance

**Department:** Governance · **Use Case:** `uc-pps-026-cortes-acquisition-001`
**Agents:** `business-glossary-agent` · `metadata-mapper` · `technical-lineage-builder` ·
`data-dictionary` · `data-tagger` · `privacy-watchdog` · **Date:** 2026-08-20

---

## 1. business-glossary-agent — term dispositions

| Term | Status | Disposition |
|---|---|---|
| wOBA, xwOBA, Barrel %, Hard-Hit %, K%, BB%, Whiff, Chase, Putaway, FPSR, CSW | **locked-inherited** | Baseball Functions / dp_uc8→dp_uc11→dp_uc29 chain; cited, not redefined |
| `xwobacon` | **inherited-hardened** | BIP-only mean (uc-pps-021 O1); pitch-level `get_stats.xwoba` quarantined, never published |
| `zone_rate_strict` | **inherited-hardened** | TRACKED-population zone rate (uc-pps-024 O2); locked `in_zone_rate` never published |
| **Start Share / Bulk Share / Innings per Game / PAs per Game / Relief Share / Season Role Label (UD-1..6)** | **NEW — provisional** | DPO-supplied definitions (use-case notebook), specced in 02 §2.2 before use. Promotion candidates; "Bulk Appearance" (`entry_inning > 1 ∧ innings_delta > 2`) is the load-bearing new term. Duplicate check: dp_uc16's `opener_proxy` is adjacent, not conflicting (team-game frame vs pitcher-appearance frame) — cross-referenced, no collision. |
| Era Delta (ED-1) | report-local | mechanical reuse of dp_uc29 `role_conversion_delta` at new tiers; not a new term |
| "Bulk option behind an opener" | **not asserted** | true opener-pairing requires the *other* starter's log (team frame); this UC labels his own appearance shapes only — steward note in 01 §3 |

## 2. metadata-mapper — physical → business mapping

All exact: `pitcher`→MLBAM entity id · `inning`→appearance entry/exit derivations ·
`at_bat_number`→PA identity within game · `description`/`events`→pitch/PA outcomes ·
`stand`→batter handedness · `pfx_x/pfx_z`→movement (feet; ×12 to inches; **LHP sign convention
asserted empirically in DQ** — arm side for a LHP is the third-base-negative plate side, mirror of
the RHP exemplars) · `release_speed/release_spin_rate/release_extension/arm_angle`→stuff ·
`sz_top/sz_bot/plate_x/plate_z/zone`→location · woBA weights joined from
`wOBA and FIP Constants.csv` on `game_year == Season`. Unmapped-for-purpose: `bat_speed`
(swing-side, 2024+ only, informational); `pitcher_days_since_prev_game` (superseded by derived
rest days, 01 §2). Ambiguous: none surfaced.

## 3. technical-lineage-builder — hop map (column-level, per receipt)

`cortes.parquet` →(entity lock, R-filter, dedup)→ `d` →(min/max/nunique inning, size, nunique AB
per game_pk)→ **appearance grain** →(UD formulas, 02 §2.2)→ `dp_uc36_usage_by_season.csv` →
figures V1/report §Deployment. Parallel hops: `d` →(TRACKED filter)→ mix/location receipts;
`d` →(type=='X')→ contact receipts; `d` →(phase map)→ phase KPI receipts →(ED-1 delta)→ driver
receipts. Postseason context: `cortes.parquet` →(game_type ∈ D/L/W, **separate frame**)→
`dp_uc36_postseason_context.csv` (never joins a rate hop). Full source-to-figure trace enumerated
in `04_engineering_build.md` §receipts; every figure footnotes its CSV.

## 4. data-dictionary

Shipped as column headers + this trail (compact form, consistent with uc-pps-024/025): every
receipt column is either (a) a locked-glossary term, (b) a UD-family term specced in 02, or
(c) a mechanical descriptor (`pitches`, `games`, `entry_inning`…) defined at first use in the
receipt. No orphan columns; certification checks this (05).

## 5. data-tagger — classification proposal

`domain: Phillies Pitching (pps)` · `subject_area: player-evaluation/acquisition-onboarding` ·
`sensitivity: INTERNAL` (contains acquisition-evaluation judgments) · `data_product:
uc-pps-026-cortes-acquisition-001` · `pii: none beyond public MLBAM ids`. Pending DPO approval —
proposal only.

## 6. privacy-watchdog — risk read

Public-performance data of a public professional; no quasi-identifier combinations beyond what
MLB publishes. **Health nuance:** surgery/injury references are restricted to publicly reported
facts (mid-Oct 2025 surgery, 2025 in-season gap visible in the log) — no speculation about
procedure or prognosis appears in any artifact (01 G2). Risk: LOW. Internal publish scope upheld.
