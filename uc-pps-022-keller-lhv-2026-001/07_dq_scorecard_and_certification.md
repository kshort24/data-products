# 07 — DQ Scorecard, Certification & Publish Operations
## UC #27 · `uc-pps-022` · Layers 3-4

Agents: `data-quality-engineer`, `certification-agent`, `privacy-watchdog`,
`version-controller`, `data-observability`, `cost-watchdog`

---

## 1. `data-quality-engineer` scorecard

Executed against the rules specified in `05_`. **This table is transcribed verbatim from
`out/dp_uc26_dq_scorecard.csv`** — the executed scorecard is the source of truth, not this
document.

| Rule | Check | Detail | Observed | Result | Severity |
|---|---|---|---|---|---|
| DQ-02 | `entity_lock_pitcher_id` | `pitcher == 662144` | 1 distinct id, `['Keller, Brian']` | **PASS** | Blocking |
| DQ-03 | `entity_lock_no_brad_keller` | Brad Keller 641745 must be absent | absent; a name filter would have added **28 rows** | **PASS** | Blocking |
| DQ-01 | `dedup_pitch_key` | unique on `(game_pk, at_bat_number, pitch_number)` | 0 dupes | **PASS** | Blocking |
| DQ-04 | `game_type_regular_season` | `game_type == 'R'` | `['R']` | **PASS** | Blocking |
| DQ-05 | `cde_location_completeness` | `plate_x/plate_z/sz_top/sz_bot/zone` non-null | 100.0% | **PASS** | Blocking |
| DQ-06 | `cde_velocity_completeness` | `release_speed` non-null | 100.0% | **PASS** | Blocking |
| DQ-07 | `cde_contact_quality_on_bip` | EV + xwOBA populated on `type=='X'` | EV 100.0%, xwOBA 100.0% of 96 BIP | **PASS** | Blocking |
| DQ-14 | `comparison_population_defined` | LHV 2026 staff ex-Keller as benchmark | 41 pitchers, 14,427 pitches, 3,702 BF | **PASS** | Blocking |
| DQ-08 | `cde_spin_completeness` | `release_spin_rate` non-null | 99.4% | **PASS** | Warning |
| DQ-13 | `sample_size_bf` | BF vs the 100-BF publication convention | 146 BF over 8 starts | **PASS** | Warning |
| DQ-09 | `bat_tracking_absent` | not captured at AAA | `bat_speed` 0.0% | **WARN — documented** | Warning |
| DQ-13b | `sample_size_subsplits` | per-pitch and per-count splits below convention | slider 18 PA, sinker 19 PA, 2-strike cells 1-49 pitches | **WARN — mitigated by printing n** | Warning |
| — | `level_translation_unmodelled` | AAA→MLB factor not applied | 0 career MLB pitches | **WARN — documented** | Warning |
| DQ-16 | `sr_m1_ratification_status` | SR-M1 provisional containment | gap quantified in `sr_m1_variants.csv`; `STATUS` column on all 5 SR-M1 receipts | **WARN — flagged** | Warning |

**Score: 14 executed checks — 10 PASS · 4 WARN · 0 FAIL. All 8 blocking checks PASS.**

**Rule-to-check mapping.** `05_` specifies 16 rules; 14 appear as rows in the executed
scorecard. The other three (DQ-10 innings reconciliation, DQ-11 rate-denominator sanity,
DQ-12 splits-sum-to-whole) are executed as **runtime assertions in the verification harness**
rather than scorecard rows — blocks E10-E13 in `§2`, 13 checks, all passing. DQ-15
(timeliness) is recorded in the freshness manifest. Nothing specified went unexecuted.

All four warnings are *disclosure* warnings, not defects: the data is what it is, and the
mitigation in every case is that the limitation is printed where a reader will see it.

---

## 2. Independent verification (`dp_uc26_verification.py`)

Recomputes every published number by a second code path — direct boolean masks and scalar
arithmetic instead of the locked groupby/merge kernel — then reconciles against the CSV
receipts. Ledger: `out/dp_uc26_verification_ledger.csv`.

```
checks run : 107
passed     : 107
failed     : 0   (blocking: 0)
VERDICT    : PASS — every published number reconciles
```

| Block | Checks | What it proves |
|---|---|---|
| A — Entity lock | 5 | The slice is one pitcher, deduplicated, regular season, and free of Brad Keller |
| B — Volumes | 6 | Pitch, PA, BIP, and game counts match the receipts |
| C — Results | 12 | Slash line and rates recomputed from raw event counts; **wOBA recomputed directly from the FanGraphs 2026 constants** rather than from joined columns; xwOBAcon asserted to be BIP-only *and* asserted to differ from the pitch-level mean (proving the UC#26 grain fix is live) |
| D — Process KPIs | 11 | Whiff, chase, in-zone, FPSR, putaway, hard-hit, GB rates for both Keller and the baseline |
| E — Additivity | 13 | Every split sums to its total; per-start IP reconciles to season IP; HR receipt row count equals HR event count; both innings notations (36.2 baseball & 36.7 decimal) are asserted to describe the same 110 outs |
| F — The mechanism | 13 | Both halves of the early/late split recomputed independently, **plus two direction assertions** that fail if four-seam usage did not fall and sinker usage did not rise. The report's central claim is a test, not a sentence |
| G — Handedness | 7 | Includes an explicit assertion that all five home runs were hit by left-handed batters |
| H — Gameplan grid | 20 | Every two-strike and first-pitch cell in the persona card, plus the "58% of two-strike calls to LHB are four-seams" claim |
| I — Velocity decay | 7 | Per-inning means, plus a monotonicity assertion |
| J — PROVISIONAL SR-M1 | 5 | The DPO's supplied function reproduced by **two** further independent paths; denominator confirmed to be PA; the intent gap asserted to exist; the provisional banner asserted to be present in the data |
| K — Artefact parity | 5 | All four figures exist; no DQ check failed |

> **On J1-J2.** The Mayza success rate is computed three separate ways in this package — the
> DPO's original function, the harness's vectorised cumulative-sum reconstruction, and a
> per-PA Python loop. All three return **.411**. The number is not in question; only the
> *definition* is.

---

## 3. `privacy-watchdog` assessment

| Element | Finding |
|---|---|
| Direct PII | **None.** Player names and MLBAM ids are public professional identifiers |
| Quasi-identifiers | **None.** No age-location-role combinations that could re-identify a non-public individual. `age_pit` is public roster data |
| Sensitive categories | **None.** No health, injury, contract, biometric, or personal-contact data |
| Re-identification risk | **None.** Every subject in this product is a publicly rostered professional athlete whose performance is broadcast |
| Competitive sensitivity | **Present.** The gameplan recommendations and the identified exposures are proprietary analysis |

**Verdict: no privacy flags. Classified INTERNAL on competitive-sensitivity grounds only.
No barrier to internal publication. External publication would require a separate review of
the recommendation content — not of the underlying data.**

---

## 4. `version-controller`

| Field | Value |
|---|---|
| Version | **v1.0.0** |
| Change class | **New product** — no predecessor, no consumers, no breaking changes possible |
| Schema stability | The 25 receipt schemas are the v1 contract |
| Deprecation notices | None required |
| Forward-compatibility risk | **One, contained.** If the DPO ratifies SR-M1 as variant B or C, the `success_rate` values in this package become stale. Contained because SR-M1 is marked non-inheritable and carries a `STATUS` column — no downstream product can silently depend on it |
| Consumer communication | Not required at v1.0.0 |

**Planned v1.1.0 trigger:** SR-M1 ratification. At that point the column is renamed to
`qab_rate`, the guard rail from `04_ §5.5` is added, and this package's SR-M1 receipts are
regenerated under the ratified definition. That would be a **breaking change to the SR-M1
receipts only** and would require DPO acknowledgement per Governance Principle 4.

---

## 5. Escalations to the human DPO

| # | Item | Ask |
|---|---|---|
| **E1** | **SR-M1 ratification.** Six decisions R1-R6 in `04_ §5.7`. The headline: the as-written function returns `.411`, the literal reading of the interview sentence returns `.637`, and the recommendation is to ratify the as-written version under a renamed, honest label | Answer R1-R6 |
| **E2** | **UC ledger is ~15 use cases stale.** The installed skill's `references/uc-ledger.md` reads "Next available: UC #12". The row for this UC is drafted in `00_ §1` | Paste the row; consider rebuilding the ledger from `ls dp_uc*` |
| **E3** | **No AAA→MLB translation capability exists in the repo.** Every future minor-league UC will hit this wall. The repo has ~42 LHV pitchers, several with MLB innings in the same season (Wheeler, Painter, Hoffman, Trivino, Rangel), which is the raw material for a translation study | Decide whether to open a UC for it |

---

## 6. `data-observability` runbook

| Watch | Trigger | Action | Owner |
|---|---|---|---|
| **Freshness** | Keller makes another start | Re-run `dp_uc26_keller_lhv_2026.py`; the start-block split must be re-specified (currently a fixed 4/4) | Analyst |
| **Entity drift** | `lhvp26.parquet` refresh | DQ-02/DQ-03 re-assert automatically at build time and raise on breach | Automatic |
| **Schema drift** | Any source column in `03_` disappears or changes type | Build fails at `_coerce` or at KPI application | Automatic |
| **Promotion event** | Keller throws an MLB pitch | **This product's framing becomes obsolete.** Open a successor UC with an MLB primary tier and this package as the AAA supporting tier | DPO |
| **Approach reversion** | Four-seam usage returns above ~45% in a subsequent start | The report's central recommendation is being contradicted in practice — re-run and re-read before repeating the advice | Pitching staff / analyst |
| **KPI drift** | SR-M1 ratified under a different variant | Regenerate SR-M1 receipts, bump to v1.1.0, notify | DPO |
| **Baseline drift** | LHV staff composition changes materially (call-ups, rehab arms) | Benchmark shifts. Re-run; the baseline is recomputed from the same file so it self-updates | Automatic |

**Refresh cost:** single parquet read, ~15k rows, sub-10-second runtime, no network calls.
`cost-watchdog` returns **no findings** — there is nothing here worth optimising.

---

## 7. `certification-agent` verdict

| Required artefact | Present | Location |
|---|---|---|
| Use-case validation / gap report | Yes | `01_ §A` |
| Source fitness profile | Yes | `01_ §B` |
| Domain steward notes | Yes | `01_ §C` |
| Business glossary approval | Yes | `02_` |
| Data dictionary + metadata mapping | Yes | `03_` |
| Data model sign-off | Yes | `04_ §1-2` |
| KPI calculation specs | Yes | `04_ §4-5` |
| DQ rule specifications | Yes | `05_` |
| Join validation | Yes | `05_ §3` |
| Technical lineage | Yes | `06_` |
| Build script | Yes | `dp_uc26_keller_lhv_2026.py` |
| DQ scorecard (executed) | Yes | `§1` + `out/dp_uc26_dq_scorecard.csv` |
| Independent verification | Yes | `§2` + `dp_uc26_verification.py` + ledger |
| Freshness manifest | Yes | `out/dp_uc26_freshness_manifest.csv` |
| Privacy assessment | Yes | `§3` |
| Versioning record | Yes | `§4` |
| Observability runbook | Yes | `§6` |
| Consumer-facing deliverables | Yes | report `.md`/`.pdf`, Realmuto card `.pdf` |
| Acceptance criteria met | Yes | all four use-case questions answered — `00_ §5` |

**Internal consistency check:** the numbers in the reader report, the persona card, the CSV
receipts, and the verification ledger were cross-checked and agree. No orphan claims — every
assertion in the report traces to a receipt through `06_`.

### **CERTIFICATION STATUS: READY**

Conditional on the two standing caveats travelling with the product (`00_ §6`): level
translation is unmodelled, and SR-M1 is provisional. Both are printed on the report's first
page.

**Publish decision belongs to the `data-product-owner`.** Recorded in `00_ §6`: **PUBLISH —
internal.**
