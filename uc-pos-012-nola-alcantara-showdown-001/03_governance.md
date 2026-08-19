# 03 · Governance
**business-glossary-agent · metadata-mapper · data-tagger · privacy-watchdog · dq-rule-definer**

## Glossary — terms consumed vs introduced

| Term | Status | Authority | Note |
|---|---|---|---|
| Slash Line (BA/OBP/SLG), OPS, wOBA, K Rate | **approved — consumed** | `Baseball Functions.ipynb` via `nresults` lineage; unrounded variant per O-3 | wOBA: seasonal constants; IBB excluded num+den |
| Whiff Rate, Chase Rate | approved — consumed | notebook; D1 `_fix` used for whiff | `in_zone_rate` not published (pitcher metric on hitter panels — RC-4 precedent) |
| Hard Hit Rate | approved — consumed | notebook; D2 `_fix` | O-8 denominator convention disclosed on every surface it appears |
| Barrel / Barrel Rate | approved — consumed | notebook `barrel_rate` (glossary + lineage in-cell) | publication-round dropped, zero-BIP → NULL; both deviations disclosed in kernel docstring |
| Runs Created / `rc_per_pa` | approved — consumed / **derived KPI of this UC** | notebook `runs_created` verbatim (`max(post_bat_score) − min(bat_score)` per PA, summed) | `rc_per_pa` = RC ÷ PA at the same grain, unrounded components |
| **Noles (synthetic batter)** | **NEW — provisional (SB-1)** | this UC | "the composite batter a pitcher elicits from an opponent"; must always carry pitcher + opponent + PA |
| **KPI Family (KF-1)** | NEW — provisional | this UC | composition only; introduces no arithmetic of its own |
| **Ruling Floor (HD-1)** | NEW — provisional | human DPO, 2026-08-18 | subject-derived PA floor; see deviation register below |

No duplicate or conflicting term detected against the repo glossary artifacts; `xwobacon` family
not used in this UC (no expected-stats KPI requested).

## Deviation register

| # | House standard | This UC | Justification | Containment |
|---|---|---|---|---|
| DV-1 | 50-PA batter floor for published rate stats | 27 / 11 / 12 PA (Nola-derived) | Explicit human-DPO ruling HD-1 at intake | `below_house_floor` flag on every hitter-season row; report §7 bars sub-50 cells from rankings; dashboard badge |
| DV-2 | `barrel_rate` returns 0 on zero BIP, rounds 3dp | NULL on zero BIP, no round | D4-family hygiene; a no-contact group is not a measured 0% | kernel docstring + this row |
| DV-3 | Regular-season-only default filter | R + postseason (S/E excluded) | dp_uc34 kernel precedent inherited; MIA has no postseason overlap with PHI in-frame, so the Noles/Wheeler entities are unaffected | disclosed here |

## Metadata mapping (CDE → physical)

All exact matches except: `opponent` (derived — mapping logged in 02), `bat_team` (derived),
`entity` (constructed by SB-1), `pitcher_name` on ranking receipts (**unmapped for most ids — O-10**;
`name_source` column carries the authority per row: `local cache` | `manual carry-in` | blank=id-only).

## Classification & tagging proposal

| Dimension | Tag |
|---|---|
| Domain | Baseball Operations / Player Performance |
| Data product | `dp_uc35` · uc-pos-012 · Phillies Offense value stream |
| Sensitivity | **PUBLIC-source, LOW risk** — all inputs are public Statcast broadcast data; subjects are public-figure professionals evaluated on public performance |
| Consumer scope | Internal Phillies staff (pre-game). External/media redistribution requires O-10 name-carry-in strip + sub-floor cell strip (00 §Publish) |

## Privacy watchdog

No PII beyond public professional identities (MLBAM ids are public identifiers). No health,
contract, or off-field data touched. The composite-batter framing aggregates **teams**, lowering
individual exposure relative to prior player-subject UCs. One asymmetry note: the Harper-vs-Alcantara
H2H book is strategy-adjacent; it is standard advance-scouting content and stays inside the internal
scope tag. **Risk: LOW.** No masking required.

## DQ rules defined for this UC (executed in 05)

| CDE | Dimension | Rule |
|---|---|---|
| pitch key | Uniqueness | `(game_pk, at_bat_number, pitch_number)` unique per frame |
| `pitcher`/`batter` locks | Accuracy | mode-of-name or sole-id-in-cache must equal the locked entity |
| Wheeler concat | Consistency | cache seasons ∩ pps seasons = ∅ |
| `bat_score`,`post_bat_score` | Completeness | 0 nulls (runs_created precondition) |
| `launch_speed_angle` | Completeness | 2026 BIP null rate receipted (< 1% tolerance, INFO) |
| `zone` | Completeness | null rate receipted (O-2 disclosure, INFO) |
| `game_type` | Validity | ∈ {R, postseason codes}; S/E absent after load |
| KPI outputs | Accuracy | `0 ≤ rate ≤ 1`; `ops = obp + slg`; `rc_per_pa × PA = RC` (identity checks in verification) |
