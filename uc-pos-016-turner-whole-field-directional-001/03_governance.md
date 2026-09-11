# 03 · Governance — `uc-pos-016-turner-whole-field-directional-001`

**Version: v1.1.0** — the v1.0.0 text below is unchanged; the v1.1.0 delta is the amendment section appended at the end of this file.

**Agents:** `business-glossary-agent`, `kpi-calculator`, `technical-lineage-builder`, `data-tagger`,
`privacy-watchdog`, `domain-steward-proxy`

## Rule-1 grep (mandatory before any KPI/function is declared new — `repo-search-before-declaring-kpi-new.md`)

```
grep -rn "def hit_direction"        -> Baseball Functions.ipynb cell 56 (as `pull_air_rate`'s inline logic);
                                        extracted verbatim as a standalone fn in dp_uc40_kernel.py (PA-F1 lineage)
grep -rn "def derive_loc"           -> dp_uc40_kernel.py line 455 (PA-L1)
grep -rn "def in_zone"              -> dp_uc40_kernel.py line 167
grep -rli "sort_rank"               -> 0 matches anywhere in either repo
ls data-products/ | grep -i turner  -> uc-pos-006-turner-2026-offense-001, uc-pos-014-turner-2026-recency-001
```

**Findings applied:**
- `hit_direction`, `derive_loc`, `in_zone` are all governed and reused verbatim — **0 KPIs re-derived that
  already existed.**
- `sort_rank` is genuinely absent from the repo. The requester's own instruction ("as currently defined is
  valid only for a right-handed batter's field orientation") describes a function this organization has
  never shipped. Per Rule 3 (a notebook alias is not a name) and the spirit of Rule 1, this is declared
  **NEW-UC42**, not "the existing `sort_rank`, fixed" — because there is no existing governed `sort_rank` to
  fix. See `01_strategy_intake.md` G-2.
- Two prior Turner UCs exist (`uc-pos-006`, `uc-pos-014`) — both reviewed (see `00` and this UC's report
  §3) for the MLBAM id, the coordinate convention, and the schema notes (asymmetric pre-PHI/PHI columns),
  all of which carried forward cleanly.

## New governed objects (provisional — E-1, pending ratification before a third reuse)

| Object | Definition | Status |
|---|---|---|
| **`sort_rank(direction, stand)`** | Facet-column order: R → Pull=0, Straightaway=1, Oppo=2; L → Oppo=0, Straightaway=1, Pull=2. Keeps physical field left-right reading consistent across batter sides. | NEW-UC42, provisional |
| **`WF-1 oppo_rate_ooz`** | `(BIP with hit_direction=='Oppo') / (all BIP)`, restricted to BIP whose pitch was out of the strike zone (`zone >= 10`), grouped by `game_year`. | NEW-UC42, provisional — diagnostic use only, not locked (see `00` §6) |
| **`WF-2 pull_rate_ooz`** | Same construction, `hit_direction=='Pull'`. | NEW-UC42, provisional |
| **`P_THROWS_COLORS`** | `{'R': '#002D72', 'L': '#E81828'}` — locked dict, Phillies Navy/Red. | NEW-UC42; candidate for promotion to a shared brand-center constant — it is currently redefined ad hoc per script across the repo, which is exactly the instability the requester flagged |

**Why diagnostic, not locked (kpi-calculator recommendation, ratified by the DPO):** WF-1/WF-2 are built on
71-99 BIP per year — well below the volume this repo's rate-stat conventions treat as comfortable (the
standing 50-PA batter floor is itself a *plate-appearance* floor for full-season rates; a per-year,
zone-filtered BIP count in the double digits is a materially smaller population). Locking a KPI whose first
measurement is a null result, on a population this size, risks a false sense of settled-ness. Recommendation:
revisit locking after either a full 2026 season close-out (more BIP) or a second-subject reuse (tests
whether the WF-1/WF-2 construction generalizes).

## Technical lineage (column-level, abbreviated — full trace in `out/dp_uc42_turner_bip_extract.csv`)

```
hc_x, hc_y (Statcast raw)
  -> derive_loc()          -> loc_x, loc_y
  -> hit_direction(loc_x, loc_y, stand)  -> hit_direction {Pull, Straightaway, Oppo, not grouped}
zone (Statcast raw)
  -> in_zone() / ooz flag  -> zone_bucket {in_zone, outside}
hit_direction x zone_bucket x game_year
  -> directional_rate_table()  -> WF-1, WF-2 (pull_rate, oppo_rate, straight_rate) per (game_year, zone)
WF-1/WF-2 (2026) vs WF-1/WF-2 (2023-2025 pooled)
  -> pooled_two_prop_z()   -> z-scores published in §6 of the report
```

## Privacy assessment

**LOW.** Single public MLB player's own publicly-reported on-field performance data (Statcast, MLB's own
public data feed). No PII beyond a public figure's professional statistics; no combination of fields creates
a re-identification risk that does not already exist in the public record (his name and MLBAM id are already
public). No external publication surface is proposed for this diagnostic build — internal Baseball
Operations use only, consistent with `uc-pos-014`'s precedent.

## Data tagging

`sensitivity: public-professional-stats` · `domain: player-performance` · `subject-area: hitting/plate-discipline`
· `data-product: uc-pos-016-turner-whole-field-directional-001` · `value-stream: pos`

---

# v1.1.0 AMENDMENT — Governance (`dp_uc42a`, 2026-09-10)

**Agents:** `business-glossary-agent`, `kpi-calculator`, `technical-lineage-builder`, `data-tagger`,
`privacy-watchdog`, `version-controller`

## 4 · Rule-1 grep (mandatory before any KPI/function is declared new)

```
grep -ril "runs_created_per_600|per_600|per600"        -> 0 matches
grep -ril "pitch_location_profile|location_profile"    -> 0 matches
grep -ril "zone_cell_direction_mix"                    -> 0 matches
grep -ril "directional_value_decomposition|decomposition|oaxaca" -> 0 matches
grep -ril "slg_bip"                                    -> 0 matches
grep -ril "pitch_uid"                                  -> 0 matches
grep -ril "chi2|chisquare|chi_square|total_variation"  -> 0 matches
grep -ril "runs_created"                               -> Baseball Functions.ipynb cell 31  (REUSED VERBATIM)
grep -ril "def sort_rank"                              -> dp_uc42_kernel.py only (this UC's own v1.0.0)
```

**Search scope, stated so it can be judged:** 51 files — `Baseball Functions.ipynb` (the governed authority),
`Bullpen_Functions.ipynb`, `mlb_data.py`, `barrel_rate.py`, `qab_rate.py`, `three_true_outcomes.py`,
`leadoff_walk_rate.py`, `harper_cumulative_bb_rate.py`, `first60_season_analysis.py`,
`pitching_first60_analysis.py`, six `dp_uc*` build scripts including both prior Turner UCs
(`dp_uc24_turner_2026_review.py`, `dp_uc22_harper_own_the_zone.py`), `phillies-data-analyst.skill`,
`use-case-validator-v2.skill`, `cbp-spray_AI.md`, `CBP Outfield Trace Plan_AI.md`, `Graph Builder Skill.md`,
`product-narrator.md`, `HOUSEKEEPING.md`, the MLB `README.md`, `three_true_outcomes_business_glossary.md`,
`uc_ledger_AI.md`, and the complete v1.0.0 package. **Not a whole-repo grep** — `device_bash` was unavailable
this session (`04` §Environment), so files were staged individually rather than searched in place. The scope
covers every location a governed KPI has ever been defined in this repo's history, but it is a *sample*, and
if any of the six turns out to exist elsewhere, that version supersedes these.

**Findings applied:**
- `runs_created`, `nresults`, `mcgs`, `get_stats`, `measure_calcs`, `hard_hit_rate`, `barrel_rate` all exist
  and are **transcribed verbatim, defects included** — 0 KPIs re-derived that already existed.
- **No χ² or distributional test exists anywhere in this repo.** `PM-1` is the first. That is itself a reason
  to treat it as provisional rather than as an established house method — it has no precedent to be checked
  against, and `00` §9.7-3 asks for a reuse on a subject where the in-zone attack *did* change.
- Six objects declared **NEW-UC42a** below.

## 5 · New governed objects (provisional — E-1, pending ratification)

| Object | Definition | Why provisional, specifically |
|---|---|---|
| **`RC-1 runs_created_per_600`** | `runs_created / plate_apps × 600`, at `player_name × game_year`. | Rescaling is trivially correct; the *convention* is not. 600 PA is roughly a qualified season, not a league constant, and the object's real content is the editorial claim that run creation should be normalized before being read against a rate. That claim needs a second consumer before it is house policy. |
| **`PM-1 pitch_location_profile`** + the three-way stability test | Per-season pitch-location profile (in-zone rate, 13-cell zone share vector, median `plate_x`/`plate_z`), plus χ² and total-variation distance of 2026 against pooled 2023–25: whole plate, in-zone conditional, out-of-zone conditional. | First χ² in the repo, and **only its null arm has ever fired**. A control that has only ever returned "no change" where it matters has not been shown to detect change. Needs a subject whose in-zone attack demonstrably moved. |
| **`PM-2 zone_cell_direction_mix`** | In-zone BIP direction counts per Statcast zone cell × season. | Cell counts are single-to-low-double digits by construction. Diagnostic bridge object between the two charts; **never a KPI**, and it ships with its n printed beside every rate so no one is tempted. |
| **`DC-1 directional_value_decomposition`** | Two-way (Oaxaca-style) split of Δ`slg_bip` into mix effect, rate effect and interaction, one season vs a pooled baseline. | Arithmetic identity, not inference: no uncertainty band exists for a decomposition of point estimates, and none is fabricated. The interaction term is reported rather than folded into either side so the identity visibly closes. Ratify only after it is used where the mix effect is *large*, to check it does not overclaim. |
| **`slg_bip`** | Total bases per **ball in play**. | Named distinctly from slugging percentage on purpose — the denominator is BIP, not at-bats, and a reader who mistakes one for the other is off by a factor of roughly two. Glossary candidate precisely because the collision risk is high. |
| **`pitch_uid`** | `game_pk`–`at_bat_number`–`pitch_number`. | Trivially correct and asserted unique across 9,485 rows, but it is a **key**, and keys that leak into shipped extracts become de-facto contracts. Declared so that if Statcast ever changes at-bat numbering the dependency is documented rather than discovered. |

**Carried forward, still provisional:** `sort_rank` (unreconciled, G-1), `WF-1 oppo_rate_ooz` /
`WF-2 pull_rate_ooz` (still single-use), `P_THROWS_COLORS` / `MARKER_SIZE`. **`DIRECTION_COLORS`** is added as
a locked brand map on the same footing as `P_THROWS_COLORS`, and for the same reason: colors assigned per call
by categorical order are the instability defect the DPO flagged in the original intake.

## 6 · Technical lineage (delta)

```
plate_x, plate_z (Statcast raw, catcher's-view feet — NO transform applied)
  └─► pitch map geometry (drawing only; `zone` remains the governed in/out authority)
zone (Statcast raw)
  ├─► in_zone()  -> zone < 10                        [inherited, verbatim]
  ├─► ZONE_ROW / ZONE_COL labels (1-9 -> Up/Middle/Down x Inside/Middle/Outside)
  │      ^ labelling only; empirically confirmed against median plate_x per cell (`02` EDA)
  └─► 13-cell share vector -> PM-1 chi2 / total-variation distance
game_pk, at_bat_number, pitch_number
  └─► pitch_uid   -> the join between the spray chart and the pitch map
events
  └─► TOTAL_BASES {single:1, double:2, triple:3, home_run:4}  -> slg_bip -> DC-1
bat_score, post_bat_score
  └─► runs_created()  [verbatim, cell 31] -> RC-1 runs_created_per_600
launch_speed / launch_speed_angle
  └─► hard_hit_rate() / barrel_rate()  [verbatim, cells 52/58] -> context pool axes
wBB..wHR (per season, from wOBA and FIP Constants.csv)
  └─► get_stats -> measure_calcs -> mcgs -> nresults  [verbatim, cells 13/15/17/19] -> woba, ops
```

## 7 · Defect register additions

| ID | Defect | Where | Status |
|---|---|---|---|
| **V-1** | **Narrative/receipt divergence in v1.0.0.** `README.md`, `00` §5 and the ledger patch state the pooled 2023–25 outside-zone pull rate as 36.7% (n = 228); v1.0.0's own `dp_uc42_significance_2026_vs_pooled.csv` says 43.3% (n = 240), and v1.0.0's report and `01` agree with the CSV. A superseded draft figure survived into three summary files. | v1.0.0 paperwork, not its analysis | **Corrected** in this package + reissued ledger patch. No verdict changes (z = −0.58 either way). **Severity material** — the ledger patch would have propagated it; the live ledger never received it, so it did not. |
| **V-1 remediation** | Verification family **F — narrative/receipt reconciliation**. Every headline figure in the report's prose and the dashboard's markup is recomputed from the shipped receipts and string-matched against the narrative, including the report's own claim about the harness size. **46 checks.** | `dp_uc42a_verification.py` | **Enforced in this build.** Recommend promoting repo-wide (`00` §9.7-5) — this repo has verified receipts for many UCs; nothing until now checked that the prose agreed with them. |
| **D-1 / O-8 exposure** | Both measured against this build rather than assumed inapplicable: 3 player-seasons lost to D-1's inner merge (kept here via a pool-level `how='left'`, the governed function unpatched); 36 untracked BIP league-wide and 1 for the subject under O-8. | `out/dp_uc42a_defect_exposure.csv` | Disclosed, not patched. |
| **O-12 avoided** | The repo-wide accent-fold name defect touches `player_name`, which the context pool uses as a display grain. The subject is locked by MLBAM id throughout, so O-12 cannot reach any published subject figure. | `01` F3 | Noted, contained. |

## 8 · Versioning (`version-controller`)

**v1.1.0 — MINOR, non-breaking.** Every v1.0.0 artifact remains present and valid. New artifacts are
additive; the `dp_uc42a_*` namespace does not collide with `dp_uc42_*`. No v1.0.0 column, file or figure was
removed or redefined. The single changed value in the package is the V-1 prose correction, which brings prose
into line with receipts that never changed. **No consumer communication required beyond the reissued ledger
patch** — v1.0.0 had no downstream consumers, having been delivered the same day.

Deprecation: the static facet grid (`out/dp_uc42_fig1_facet_grid.png`) is **superseded, not removed** — it
remains in the package as the record of what v1.0.0 shipped.

## 9 · Privacy and tagging (delta)

**Unchanged — LOW.** `plate_x`, `plate_z`, `launch_speed`, `launch_angle` and the score fields are the same
public Statcast feed at the same grain the package already carried. The context pool adds 20 other Phillies
batters' public season lines; all are public figures' publicly reported professional performance. No
combination here creates a re-identification risk that does not already exist in the public record. No
external publication surface is proposed.

Tags unchanged, plus: `data-product: uc-pos-016 … · version: 1.1.0 · supersedes: dp_uc42 v1.0.0`.
