# 07 — DQ Scorecard, Certification, Consumption & Operations
## `uc-pos-007` / `dp_uc27` · Layers 3–4 · Agents: `data-quality-engineer`, `certification-agent`, `privacy-watchdog`, `query-builder`, `data-observability`, `version-controller`, `cost-watchdog`

---

## 1. DQ scorecard

**16 checks · 14 PASS · 2 WARN · 0 FAIL · all 9 blocking checks PASS.**
Receipt: `out/dp_uc27_dq_scorecard.csv`.

| ID | Dimension | Blocking | Result | Detail |
|---|---|---|---|---|
| DQ-01 | Uniqueness | Yes | **PASS** | 0 duplicate pitch keys after dedup |
| DQ-02 | Validity | Yes | **PASS** | 11 distinct batter ids, all in the roster lock |
| DQ-03 | Validity | Yes | **PASS** | `game_type` values present: `['R']` |
| DQ-04 | Validity | Yes | **PASS** | `p_throws` values present: `['R']` |
| DQ-05 | Consistency | Yes | **PASS** | 0 non-MLB `home_team` codes remain |
| DQ-06 | Accuracy | Yes | **PASS** | 0 Irma-relocated rows retained |
| DQ-07 | Accuracy | Yes | **PASS** | Miami cohort contains only `MIA` |
| DQ-08 | Completeness | Yes | **PASS** | 0 null wOBA cells in the published split |
| DQ-09 | Completeness | No | **PASS** | 80.2% of pitch rows have null `estimated_woba` — within the expected Statcast range (populated on contact and strikeouts only) |
| DQ-10 | Completeness | No | **PASS** | 99.4% of balls in play carry `launch_speed` |
| DQ-11 | Validity | No | **WARN** | Below the PA gate: **Sosa (25 PA), Crawford (10 PA)**. Published under banner, excluded from all pooled statements |
| DQ-12 | Timeliness | No | **PASS** | Max `game_date` 2026-07-22 vs build 2026-07-27 (T-5) |
| DQ-13 | Timeliness | No | **WARN** | `alcantara.parquet` max `game_date` **2025-04-12**. 2026 form observable only via `phils_2026` |
| DQ-14 | Consistency | Yes | **PASS** | BIP denominators identical across `hard_hit_rate`, `barrel_rate`, `get_stats` |
| DQ-15 | Uniqueness | Yes | **PASS** | 11 ids / 11 names, no collision |
| DQ-16 | Completeness | No | **PASS** | 11 of 11 rostered hitters have faced Alcantara in the log |

### 1.1 Independent verification

`dp_uc27_verification.py` — a separate process sharing no code with the build — re-reads the parquet
layer, re-applies the four governance filters from first principles, and recomputes every headline
number using long-form event counting instead of the merge-chain kernel.

| Group | Checks | Result |
|---|---|---|
| Pooled cohort panels (Miami / Other) | 24 | 24 PASS |
| Visitors-only Miami cohort | 7 | 7 PASS |
| Per-hitter venue split (21 hitter × cohort cells) | 126 | 126 PASS |
| Alcantara head-to-head (11 hitters) | 33 | 33 PASS |
| Alcantara by venue | 10 | 10 PASS |
| VD-1 delta arithmetic (10 hitters × 5 KPIs) | 50 | 50 PASS |
| Governance invariants | 6 | 6 PASS |
| **Total** | **256** | **256 PASS · 0 FAIL** |

Tolerances: `0.0011` on 3-dp rates (round-trip), `0.011` on EV90 (2-dp round-trip), `2.5e-4` on VD-1
deltas (4-dp round-trip on two stored values), exact on integer counts.
Receipt: `out/dp_uc27_verification_results.csv`.

---

## 2. Certification readiness

`certification-agent` verdict: **READY.**

| Required artifact | Present | Internally consistent |
|---|---|---|
| Use-case validation / gap report | `01_ §1` | Yes — 1 blocking gap raised and resolved before Layer 2 |
| Source fitness profile | `01_ §3` | Yes — quantified per hitter, per CDE |
| Glossary approvals | `02_` | Yes — 3 new CDEs approved, 2 KPI terms explicitly PROVISIONAL |
| Data dictionary | `03_` | Yes — 31 source columns, 24 receipts, 0 unmapped |
| Data model sign-off | `04_ §1` | Yes — single grain, one dimension join |
| KPI specifications | `04_ §2–3` | Yes — 18 locked inherited verbatim, 2 new fully specced |
| DQ rules + results | `05_ §1`, `07_ §1` | Yes — 16 rules, 16 results, 1:1 |
| Join validation | `05_ §2` | Yes — defect found, quantified, remediated, asserted |
| Lineage | `06_` | Yes — every published KPI traced to source columns |
| Acceptance criteria | `04_ §5` | Yes — 8 of 8 met |
| Independent recompute | `dp_uc27_verification.py` | Yes — 256/256 |
| Deliverables | report `.md`/`.pdf`, persona card `.pdf` | Yes |

**Consistency cross-checks performed by the certifier:**

* Every number in the reader report was located in a CSV receipt. No orphan figures.
* The persona card reads from CSVs at build time — it cannot diverge from the report.
* The `.md` and `.pdf` of the report are generated from the same source file.
* Every PROVISIONAL KPI carries its banner in both consumer artifacts.
* The exclusion audit row counts sum to the difference between union and governed frame.

**Privacy assessment** (`privacy-watchdog`): **PASS.** No PII. Inputs are publicly published
Statcast tracking data; player names and MLBAM ids are public professional identifiers. No
quasi-identifier combination, no re-identification surface. No flag raised against external
publication, though distribution is internal by DPO choice.

**Version** (`version-controller`): **v1.0.0.** New product. No predecessor, no breaking change, no
deprecation notice required. VD-1 and VD-2 are marked non-inheritable, so a future ratification
decision cannot break a downstream consumer.

---

## 3. Publish decision

**PUBLISH — internal, v1.0.0**, with the three standing caveats in `00_ §6`.

---

## 4. Consumption guide (`query-builder` / `analytics-enabler`)

### 4.1 Which frame answers which question

| Question | Use | Do not use |
|---|---|---|
| "How has this group hit at loanDepot, all history?" | `pooled_venue.csv` | — |
| **"What should we expect on July 28?"** | **`pooled_venue_visitors.csv`** | `pooled_venue.csv` — it includes 863 home-club PA |
| "Which individual has a real Miami effect?" | `venue_delta.csv`, filter `qualified == True`, read `venue_signal_class` | The raw `d_woba` column alone |
| "How do we attack Alcantara?" | `alcantara_mix.csv` (career) + `alcantara_recent_mix.csv` (2025–26 usage shift) | `alcantara_by_year.csv` alone — 2026 is one start |
| "Who has hit him?" | `alcantara_h2h.csv`, `alcantara_hitter_venue.csv` | Any row below 15 PA without printing the PA |

### 4.2 Worked query patterns

```python
import pandas as pd
OUT = "out"

# The decision-relevant venue read
vis = pd.read_csv(f"{OUT}/dp_uc27_pooled_venue_visitors.csv")
vis[["venue", "plate_apps", "woba", "xwoba", "hard_hit_rate", "barrel_rate"]]

# Only the hitters whose Miami split is worth acting on
vd = pd.read_csv(f"{OUT}/dp_uc27_venue_delta.csv")
vd.loc[vd.qualified & vd.venue_signal_class.str.startswith("Miami boost"),
       ["player", "pa_miami", "d_woba", "process_composite"]]

# Alcantara's punishable pitches against this roster, min 20 PA
mix = pd.read_csv(f"{OUT}/dp_uc27_alcantara_mix.csv")
mix.loc[mix.plate_apps >= 20].sort_values("xwoba", ascending=False)[
    ["pitch_name", "usage", "plate_apps", "woba", "xwoba", "hard_hit_rate", "chase_rate"]]
```

### 4.3 Interpretation rules for consumers

1. **Always read the PA.** Every rate in this product ships with its denominator. A 74-PA split is a
   tiebreaker, not a plan.
2. **Read wOBA and xwOBA together.** A large wOBA gap with a small xwOBA gap is sequencing luck.
   This product's headline is exactly that pattern.
3. **Never pool cohort A and cohort B.** Cohort B is a subset of A. Adding them double-counts.
4. **VD-1 and VD-2 are provisional.** Cite them with the banner; do not inherit them into a new UC.

### 4.4 FAQ

**Why is Rincones Jr. missing from the venue tables?** He has zero career plate appearances at
loanDepot park. VD-1 uses a set intersection, so no row is produced. His absence is a fact, not a gap.

**Why is Realmuto's Miami line so bad in one table and so good in another?** Because they are
different populations. `venue_split.csv` includes his 783 PA as a Marlin (2015–18);
`venue_split_visitors.csv` shows only his 124 PA as a visiting Phillie. See `02_ CDE-3`.

**Can I use this to say loanDepot is a pitcher's park?** No. This product benchmarks the roster
against itself. It has no league-wide baseline and cannot make a general park-factor claim.

---

## 5. Observability (`data-observability`)

This is a **point-in-time product tied to a dated event**, not a standing pipeline. Monitoring is
therefore refresh-trigger based rather than continuous.

| Watch | Trigger | Action |
|---|---|---|
| Alcantara cache staleness | `alcantara.parquet` max date < today − 30 d | Re-pull before any re-run; DQ-13 will WARN until fixed |
| Phillies cache staleness | `phils_2026.parquet` max date < today − 7 d | DQ-12 flips to WARN; refresh before re-publishing |
| Roster drift | Any of the 11 MLBAM ids no longer on the active roster, or a new hitter added | Entity lock is hard-coded — a roster change requires a code edit and a new version |
| Schema drift | Any of the 31 consumed columns disappears from a future parquet | Build raises at read time; no silent degradation |
| Venue-integrity drift | A new documented relocation involving `MIA` as nominal home club | Add the `game_pk` to `IRMA_GAME_PKS` (rename the constant) and re-run; DQ-06 covers it |
| Sample-gate drift | A hitter crosses the 40-PA Miami gate | `qualified` flips; DQ-11 WARN count changes |

**Re-run runbook:** refresh caches → `python dp_uc27_phillies_at_loandepot.py` →
`python dp_uc27_verification.py` (must exit 0) → rebuild PDF and card → bump the version in this
document. Never overwrite a prior UC's `out/` files.

---

## 6. Cost audit (`cost-watchdog`)

**PASS — one low-priority finding.**

| Metric | Value |
|---|---|
| Sources read | 30 parquet files + 1 CSV |
| Rows read (pre-filter) | ~1.9 M across all sources; 150,421 retained at the roster filter |
| Rows in the governed frame | 97,235 |
| Runtime | ~12 s single-threaded |
| Peak memory | < 2 GB |
| Outputs | 24 CSVs (~350 KB), 5 PNGs (~1.1 MB), 2 PDFs (~480 KB) |

**Finding C-1 (low).** `load_union()` reads every `data/opponents/*.parquet` with all ~115 columns
before filtering on `batter`. Passing a column projection to `read_parquet` would cut I/O by roughly
70%. Not worth changing for a 12-second job, but it is the obvious first optimisation if this pattern
is generalised to a league-wide study where the opponents directory is an order of magnitude larger.

**No other findings.** No recompute waste (single pass), no storage hotspot, no over-provisioning.

---

## 7. Open items returned to the human DPO

| # | Item | Type | Recommendation |
|---|---|---|---|
| O-1 | Ratify or reject **VD-1 Venue Delta** | Glossary decision | Ratify, with the DPO setting the minimum-PA gate explicitly rather than inheriting the build's 40/100 convention |
| O-2 | Ratify or reject **VD-2 Venue Signal Class** | Glossary decision | Hold. The scaling divisors need a fitted dispersion study across more than one roster before the classification is defensible |
| O-3 | Promote **`VENUE_TENURE_CONTEXT`** to the enterprise glossary | Glossary decision | Promote. Every roster with ex-members of an opposing club has this exposure; the trap is not specific to Miami |
| O-4 | Refresh `alcantara.parquet` | Data operation | Do it before first pitch if the arsenal section is going to be used in a meeting |
| O-5 | Commission a league-wide park-factor baseline | New use case | Would convert "this roster has not been suppressed" into "this park does not suppress," which is the question people actually think they are asking |
| O-6 | Update the stale `pitcher-scouting-report` UC ledger | Repo maintenance | Row text supplied in `00_ §1`; ledger is ~16 use cases behind |
