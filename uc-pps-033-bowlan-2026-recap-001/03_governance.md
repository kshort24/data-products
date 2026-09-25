# 03 · Governance: `uc-pps-033`

Agents: `business-glossary-agent` · `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 0 · Rule-1 search (before anything was declared new)

```
grep -rn "rc_per_gm|ff_vert|ff_velo|ff_spin|whiff_rate_iz_ff|whiff_rate_breaking"  MLB/*.py MLB/*.md data-products/  → 0 hits
grep -rn "runs_created"          → Baseball Functions.ipynb cell 30/31 (approved term); uc-pos-012 03 §1 (rc_per_pa derived) — INHERITED
grep -rn "def xwobacon"          → dp_uc25 / dp_uc26 / dp_uc29 / dp_uc30 (uc-pps-021 O1) — INHERITED (verbatim)
grep -rn "rv100|Run Value per 100" → uc-pps-032 glossary (provisional) — SECOND USE
grep -rn "pitch_group"           → September 2026.ipynb cell 5 (group_map) — INHERITED (verbatim)
grep -rn "house_percentile|season_recap|career_frame|persona_ledger|velo_by_outing" → 0 hits
ls data-products | grep -i bowlan → none (Bowlan appears in uc-pps-012, uc-pps-029, uc-pps-032 as a cohort/bullpen member)
```

## 1 · Business glossary

| Term | Definition | Status | Note |
|---|---|---|---|
| **Runs Created (house)** | Runs that scored during the plate appearances a pitcher threw: Σ over PA of max(`post_bat_score`) − min(`bat_score`) | EXISTING (approved) | **Not** Bill James' Runs Created. Includes inherited runners who score; excludes his own runners who score after he leaves. Escalated E-3 |
| **RC per PA / RC per game** | Runs Created ÷ PA; ÷ appearances | `rc_per_pa` EXISTING; `rc_per_gm` NEW · provisional | |
| **Games (pitcher)** | Distinct `game_pk` in which he threw ≥1 pitch | NEW · provisional | = appearances |
| **Four-seam ride (IVB)** | mean(`pfx_z`) × 12 over four-seams, **unrounded** | EXISTING (`ivb_in`) | client alias "vert"; notebook `ff_vert` is the rounded variant (O-25) |
| **Breaking-ball whiff** | whiffs ÷ swings on pitch_group Breaking (KC CU CS SL ST SV KN) | NEW · provisional | client's `whiff_rate_breaking` |
| **In-zone four-seam whiff** | whiffs ÷ swings on four-seams with `zone < 10` | NEW · provisional | client's `whiff_rate_iz_ff` |
| **House percentile (KP-1)** | Share of the house population strictly worse than the value | NEW · provisional | population always named |
| **Count state (CS-1)** | 2K if strikes = 2; else behind / ahead / even | NEW · provisional | 2K takes precedence |
| **Appearance entry state (US-1)** | inning, outs, runners on and lead at the **first pitch** of an appearance | NEW · provisional | |
| **Persona signature (PA-1)** | A measurable change an action by a persona would leave in the log | NEW · provisional | a signature is evidence *consistent with* an action, never proof |
| **Run Value per 100** | −100 × mean(`delta_run_exp`) | uc-pps-032 · **second use** | ratification recommended |
| **xwOBA on contact** | mean xwOBA over balls in play | EXISTING (uc-pps-021 O1) | |

**Personas (value stream `pps`)**, as used here: Front Office · Pitching Coach · Pitching Analyst · Catcher · Manager · Pitcher. Strength & Conditioning / Medical is proposed (E-4).

## 2 · KPI specifications (`kpi-calculator`)

**Inherited, unchanged:** `get_stats`, `nresults`, `whiff_rate`, `chase_rate`, `pitch_mix`, `fpsr`, `two_prop_z`, `apply_woba_weights`, `load_phils` (by import, `dp_uc44_kernel` sha256 `a2c119096db2…`); `runs_created`, `GROUP_MAP`, `xwobacon` (verbatim transcription).

| ID | Object | Plain language | Formula / rule | Grain | Edge cases |
|---|---|---|---|---|---|
| **CF-1** | `career_frame` | Every regular-season pitch he threw, once | phils (pitching → PHI, batting → VS_PHI) ∪ subject file (FILE); `pitcher == id`; `game_type == 'R'`; dedup on PITCH_KEY with precedence PHI > FILE > VS_PHI | pitch | returns a source receipt with kept/dropped by season |
| **SR-1** | `season_recap` | The client's table, as a function | the cell-115 merge chain; `governed=False` reproduces the notebook exactly; `governed=True` reads ff_* from unrounded FF means, keeps NaN, and carries denominators | pitcher-season | the `gy` loop leak removed (`pitch_mix_by_season` sorts and never exports its loop variable) |
| **KP-1** | `house_pitcher_seasons` / `house_percentile` | Where does this rate sit among Phillies pitcher-seasons? | population: `phils_*` pitching role, R, grouped pitcher × season, PA ≥ 100. pct = ⌊100 × share strictly worse⌋; rank = 1 + count strictly better | pitcher-season | ties share the better rank; direction declared per KPI |
| **AR-2** | `arsenal_table` | Per pitch type, what it looked like and what it did | n, usage, velo, spin, IVB, HB, whiff/swing, chase/OOZ, zone rate, xwOBAcon (BIP), RV/100 | season × pitch (× stand) | whiff NaN when 0 swings |
| **CS-1** | `count_state` | Which count was it? | 2K ⇐ strikes = 2; behind ⇐ balls > strikes; ahead ⇐ strikes > balls; else even | pitch | 2K precedence |
| **US-1** | `appearance_log` / `usage_summary` | How was he used? | entry state from the first pitch (sorted by `at_bat_number, pitch_number`, `head(1)`); pitches, innings spanned, RC per appearance; shares by season | appearance → season | rest NULL on a file's first outing |
| **VE-1** | `velo_by_outing_bucket` | Is the velocity arm or role? | four-seam mean velo by pitch-of-outing bucket 1–10 / 11–20 / 21+ | season × bucket | buckets fixed before looking |
| **PA-1** | `signature_verdict` / `strength_from_signatures` | Does the log carry the signature of this action? | signature PRESENT iff Δ × direction ≥ threshold (and p < .05 where tested); WEAK if the right direction but under the bar; CONTRA if the opposite direction ≥ threshold; ABSENT if \|Δ\| < threshold/4. Hypothesis STRONG iff all PRESENT; SUPPORTED iff ≥ half PRESENT and no CONTRA; MIXED if CONTRA and PRESENT; else UNSUPPORTED | hypothesis | thresholds declared in the build before the verdicts were read; state-type signatures compare a level to a bar |

**PA-1 thresholds (declared):** velocity 0.5 mph · pitches/app 3 · shares 0.10 (role/entry 0.15, curveball 0.05) · rates 0.03 (K, chase, FPS), 0.02 (BB), 0.05 (whiff, xwOBAcon) · grade bar 60.

## 3 · Technical lineage (published numbers)

| Published number | Lineage |
|---|---|
| Recap KPIs (G, PA, slash, wOBA, K/BB/HR, RC) | CF-1 → `nresults` / `runs_created` / nunique(`game_pk`) by `player_name, game_year, p_throws` |
| FF velo / spin / ride | CF-1 · `pitch_type=='FF'` → mean(`release_speed`), mean(`release_spin_rate`), mean(`pfx_z`)×12 (unrounded) |
| Breaking / in-zone FF whiff | CF-1 · pitch_group Breaking / (FF & `zone<10`) → `whiff_rate` |
| K-rate percentile 92 | `phils_*` pitching R → `nresults` by pitcher × season → PA ≥ 100 (198) → KP-1 |
| Staff ride rank #7 of 132 | `phils_*` pitching R · RHP · FF · ≠2017 → mean(`pfx_z`)×12 by pitcher × season, n ≥ 100 → rank |
| Four-seam grades (#20 → #2 of 405) | `out/dp_uc47_population_graded.csv` (read-only) → rank on `efc_score` within `pop_member` |
| Mix by stand / count | CF-1 ≥ 2025 → AR-2 by stand / CS-1 share of FF |
| Usage and RC by entry | CF-1 ≥ 2025 → US-1 |
| VE-1 | CF-1 ≥ 2025 → cumcount within `game_pk` → bucket → FF mean velo |
| Persona verdicts | the above receipts → PA-1 rules |
| HP verdicts | `kellen_frame()` (client's method) vs CF-1 (governed) + cache probe |

## 4 · Defect exposure

| Defect | Exposed? | Why |
|---|---|---|
| D-1/D-2 `whiff_rate` inner join drops zero-whiff groups | **No** (DQ-15) | every season has ≥1 whiff in each subset. `fillna(0)` is used only in the notebook-exact mode |
| D-7/O-13 NULL zone counted in-zone | **Marginal** (DQ-16 WARN) | 1 NULL-zone pitch of 1,818; `in_zone_rate` is not published as a finding |
| O-12 accent folding | No | id lock |
| O-23 `nphl` has no level gate or cross-source dedup | **No** | only `bowlan.parquet` touches this subject; CF-1 dedups against the Phillies log (19 rows) |
| O-24 batter-keyed pulls | No | id lock |
| **NEW O-25** `pitch_mix` rounds `pfx_x/pfx_z` to 0.1 ft → IVB/HB quantized in 1.2-inch steps | **Yes → handled** | SR-1 governed mode reads unrounded means; HP-13 shows both. Upstream fix escalated (E-2) |
| **NEW B-1** `GroupBy.first()` returns the first *non-null* value per column | **Yes → fixed in build** | used to read entry runners, it pulled `on_1b` from later pitches; 2026 "clean entry" read 27% → corrected to 75% (`05` §4) |
| **NEW HP-18** notebook loop variable `gy` leaks into subtitles | **Yes → handled** | SR-1 has no leaked state; `RECAP_SEASON` is explicit |

## 5 · Privacy, tagging, versioning

- **Privacy (`privacy-watchdog`):** public MLB performance data for one player; injury information is a *published news report*, carried in as context and never modelled. No staff member is named in any hypothesis. **CLEAR.**
- **Tags (`data-tagger`):** Internal · domain `pps` · subject *pitching / season recap* · product `dp_uc48`. External publication permissible after DPO review.
- **Versioning (`version-controller`):** v1.0.0. **Breaking:** KP-1 population or floor, PA-1 thresholds or decision rule, CF-1 precedence. **Non-breaking:** a refreshed anchor (v1.1.0), a postseason appendix.

## 6 · Ratification path

| Object | Cheapest independent second use |
|---|---|
| SR-1 `season_recap`, CF-1 | The Luzardo recap (cell 114) or the Nola/Painter/Wheeler recaps the client listed next |
| KP-1 | Any recap that asks "what percentile" |
| PA-1 | Any recap with a value-stream narrative, since the thresholds should hold unchanged |
| VE-1 | Any reliever-to-role change (e.g., a starter moved to the bullpen) |
| RV/100 (uc-pps-032) | **This UC** is its second use → ratification recommended |
