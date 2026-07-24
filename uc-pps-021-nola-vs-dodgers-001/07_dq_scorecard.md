# Layer 3 — Data Quality Scorecard
### UC-PPS-021 · rules from `05` executed against the built data (Nola career log, build cache through 2026-07-16)

Full receipt: `out/dp_uc25_dq_scorecard.csv`. Independent recompute: `dp_uc25_verification.py`.

## Governance scorecard

| Rule | CDE / check | Dimension | Result | Status |
|---|---|---|---|---|
| DQ1 | `pitcher == 605400` only | Uniqueness / entity lock | Hoffman 676510 excluded | ✅ PASS |
| DQ2 | `game_pk+ab+pitch` unique | Uniqueness | 0 duplicate keys | ✅ PASS |
| DQ3 | `game_type == 'R'` | Validity | regular season only | ✅ PASS |
| DQ4 | season coverage 2015..2026 | Completeness | 12 seasons present | ✅ PASS |
| DQ5 | freshness | Timeliness | max game_date == 2026-07-16 (build) | ✅ PASS |
| DQ6 | H2H resolution | Completeness | 7/7 named hitters resolved | ✅ PASS |
| DQ7 | locating CDEs completeness | Completeness | `pitch_name/release_speed/plate_x/plate_z/zone/description/stand` = 1.000 | ✅ PASS |
| DQ8 | `estimated_woba` on BIP | Fitness | >0.99 every season | ✅ PASS |

**Aggregate: 8/8 governance rules PASS. Zero blocking failures.**

## Structural / by-design notes (not failures)
- `events` / `woba_value` / `woba_denom` completeness **~0.26**: expected — only PA-ending pitches carry these. Rules scoped accordingly.
- `bb_type` **0.172**, `launch_speed`/`launch_angle` **0.295**: expected — balls-in-play only; drive AIR/GB and hard-hit, which are scoped to BIP.
- The pitch-level `get_stats.xwoba` column is **quarantined** (contaminated by non-BIP rows); `xwobacon` (BIP mean) used instead. Tracked as O1.

## Independent verification (Certification Agent input)
`dp_uc25_verification.py` reloads the parquet via a **separate code path** (game_type filter first, per-row wOBA weights) and asserts every headline number against both the receipts and the report:

**RESULT: 31/31 PASS — CERTIFY READY.** Covers season slash (.358/.509/5.1% HR), xwOBAcon (.384, and >99% BIP fitness), the L/R lefty-leak split (identical xwOBAcon, walk-driven gap), the contact-quality engine (career-low GB, career-high air), the ABS re-test, the recency split (last-3 .313; 7/05 0BB/0HR/7K; 7/16 3 HR), and the 7-hitter H2H (Betts 23 PA/.465/2 HR independently reproduced; Freeman 86; Muncy 11 K).

## Sample-size quality (the product's own DQ surface)
Carried into every output per house discipline:
- **H2H:** Freeman 86 PA = real sample; Muncy 25 / Betts 23 / Edman 19 = directional; Ohtani 9 / Tucker 8 / Pages 8 = thin (flagged, plans profile-driven).
- **Recency:** last-3 starts = 75 PA (directional); most recent (7/16) called out separately (3 HR).

**DQ Engineer verdict:** data quality is sufficient to publish for internal advance use. No remediation required. One tracked governance follow-up (O1 xwOBAcon promotion).
