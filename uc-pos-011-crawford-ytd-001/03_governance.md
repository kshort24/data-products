# 03 · Governance
**business-glossary-agent · metadata-mapper · data-tagger · privacy-watchdog · version-controller**

## Glossary — terms consumed and introduced

| Term | Status | Definition | Note |
|---|---|---|---|
| First-Pitch Strike Rate (`fpsr`) | **APPROVED — consumed** | `(first_pitches − first_pitch_balls) / first_pitches` | Second `pos`-side use of a `pps`-side approved term. Value-stream annotation only; **no formula change** |
| Swing / Whiff classifier | **RATIFIED (uc-pos-010) — inherited** | the 8-value SWINGS list including `swinging_pitchout`; 5-value WHIFFS | Not re-litigated |
| Swing Rate, First-Pitch Swing Rate | PROVISIONAL — inherited | AP-2 / AP-3 from `uc-pos-010` | Consumed unchanged |
| **BABIP** | **NEW — provisional** | `(H − HR) / (AB − K − HR + SF)` | Introduced because the premise "hitting the ball better" cannot be adjudicated without separating results from contact |
| **Batted-Ball Profile (CR-1)** | **NEW — provisional** | GB/FB/LD/PU shares over **all** BIP; `mean_la` / `median_la` / `mean_ev` over **tracked** BIP, NULL below 50 tracked | **Two populations in one function, deliberately.** `bb_type` is classifier-derived and complete; launch angle is sensor-derived and is not. Collapsing them would violate the uc-pos-009 standard |
| **Expected Outcome on Contact (CR-2)** | **NEW — provisional** | mean `estimated_woba_using_speedangle` over BIP, published as **`xwobacon_bip`** | **Never to be compared to `woba`.** Different denominator. Name carries the O-4 convention so the trap is visible at the column |
| **Centre-Field Context Pool (CX-1)** | **NEW — provisional** | Phillies player-seasons with **>80 games** at `fielder_8`, restricted to games with **>10** defensive pitches in centre | Thresholds supplied by the DPO and **transcribed without alteration** |
| **Platoon Mix Effect (PL-1)** | **NEW — provisional** | direct standardisation: target-window within-split rates re-weighted by reference-window PA shares. Positive = the observed line is flattered by the mix | A causal-attribution guard, not a performance metric |
| Reliability Floor | **DECLARED** | 50 PA for PA-denominated rates; 50 tracked BIP for launch-angle statistics; 40 pitches for pitch-type rows | March and August 2026 both fall below the PA floor |
| Narrative Breakpoint | **DECLARED** | 2026-06-15, requester-supplied, **outcome-selected** | Never reported without the sensitivity scan beside it |
| Month | **DECLARED (inherited)** | `game_date.dt.month`, calendar | No March/April merge |

## Metadata mapping

All **14 CDEs mapped exact** against the live `pos` / `pps` schema. Zero unmapped, zero inferred —
each confirmed by reading the column, not by naming convention. Two negative confirmations are worth
recording because they changed the build:

- **`loc_x` / `loc_y` do not exist** in the parquet schema (`hc_x` / `hc_y` do). Confirmed against
  `pyarrow.parquet.ParquetFile(...).schema.names`. This makes the governed `pull_air_rate`
  non-executable — opened as **O-7**.
- **`launch_speed` is 0.74% NULL on 2026 BIP.** Real, and the reason **O-8** is not hypothetical.

## Tagging

Domain `pos` · subject area *Batting / Plate Discipline / Batted Ball* · sensitivity **Internal** ·
product `uc-pos-011`.

## Privacy — **LOW–MODERATE**

Public player name, publicly-tracked on-field performance. No PII beyond a public figure's name.
No health, injury, contract, option-status or personnel-evaluation data is joined, and none may be
without a fresh review.

**Rated above the usual `pos` baseline for two reasons:**

1. **Prospect-evaluation framing.** The product renders a judgement on whether a rookie's profile can
   support a major-league regular, and names the comparison cohort. That is closer to an internal
   evaluation than to a performance report.
2. **Access asymmetry.** Crawford is both a named persona in `06` and the subject of a product whose
   findings bear directly on his playing time — the August platoon shielding is documented here in a
   way it may not have been communicated to him.

**Recommendation:** staff receive the full artifact. The player-facing surface is the persona section
in `06`, scoped to his own approach and contact metrics, **excluding the deployment findings and the
archetype-ceiling cohort**. Any decision to share the fuller read with the player is a human one and
sits with the DPO and player development, not with this product.

## Restricted uses

Contract, arbitration or option valuation · public or media distribution · any causal claim
(see `05` §caveats) · **any ranking that includes a March or August 2026 row** · comparison of
`xwobacon_bip` against `woba`.

## Version control

| Change | Class |
|---|---|
| `fpsr` cross-value-stream reuse (2nd `pos`-side use) | **non-breaking** — no formula change |
| `running_line_pa` extended with `cum_ba` / `cum_obp` | **non-breaking — additive.** Existing `cum_woba` consumers see identical values; verified against `dp_uc33`'s output shape |
| `babip` added to `nresults_unrounded` | **non-breaking — additive column** |
| CR-1, CR-2, CX-1, PL-1 | new, no consumers, **cheap to change now** |
| D5/D6 disclosure (O-7, O-8) | **no code change shipped.** `pull_air_rate` and the governed `hard_hit_rate` are untouched; the defects are reported for DPO ruling |
