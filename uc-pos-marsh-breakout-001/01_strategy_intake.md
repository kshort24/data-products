# 01 — Strategy & Intake · uc-pos-marsh-breakout-001

## use-case-validator — gap report (condensed)

**Verdict: GO.** Prompt-form use case (visual-intake-agent skipped per convention for written use cases).

| # | Gap | Class | Resolution |
|---|---|---|---|
| 1 | "Rest of his career" spans an LAA era not in `pos` | Non-blocking | `data/opponents/marsh.parquet` covers 2021-07-18 → 2022-07-31; concatenated with dedup on pitch key |
| 2 | "First half" boundary undefined | Non-blocking | Defined as regular-season games through 2026-07-11 (last cached game before the break) — PD-1 |
| 3 | "Approach" is not a governed CDE | Non-blocking | Operationalized as the swing-decision indicator panel (02 §2); narrative labeled as inference |
| 4 | All-Star selection not verifiable in Statcast data | Non-blocking | Taken as given from requester; no roster claim made from data |
| 5 | 2026 wOBA weights availability | Cleared | `wOBA and FIP Constants.csv` has a 2026 row |

## source-system-profiler — fitness (condensed)

Entity 669016 present in all six seasons; 9,864 deduped regular-season pitches. Null rates: zone 0.04%, launch_speed on BIP 0.2%, hit coordinates on BIP 0.07%, estimated_woba on BIP 0.47% — all fit for purpose. wOBA weight join: 0 null rows. 2026 cache fresh through 2026-07-11 (complete first half). 2021 season is 260 PA (post-debut July call-up) — above the 50-PA floor, retained.

## domain-steward-proxy — context notes

- Marsh traded LAA→PHI ~2022-08-02; 2022 season line blends stints (flagged in report).
- Career-long platoon shielding vs LHP is a known managerial pattern — LHP PA share is therefore a *role* indicator, not just a performance split.
- CBP is favorable for LHB pull-side air; pulled-air rate is the domain-preferred lens for "same EV, more SLG" questions.
