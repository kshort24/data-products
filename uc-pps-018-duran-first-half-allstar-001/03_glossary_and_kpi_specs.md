# 03 — Glossary Alignment & KPI Specs (business-glossary-agent + kpi-calculator) · uc-pps-018

## Glossary status
**No new business terms required.** Every metric in the report resolves to an already-approved term in the pps value stream glossary (approved lineage UC8 → UC11). The two facts without pitch-data definitions — *Save* and *All-Star selection* — are handled as **manual carry-ins**, not glossary terms, per governance rule 1 (no CDE inference) and the DPO's intake decision. If a future UC wants save-situation analytics, "Save Opportunity" must go through glossary approval first — returned to DPO as a known gap, not resolved here.

## KPI register — all locked, inherited verbatim from dp_uc11
| KPI | Function | Grain used here | Notes |
|---|---|---|---|
| wOBA against | `nresults` | era / month | season-specific FanGraphs weights |
| xwOBA / xBA against | `get_stats` | era | mean of Statcast estimated fields |
| K% / BB% / HR-per-PA | `nresults` | era / month | PA-denominated |
| Whiff rate | `whiff_rate` | era / era×pitch / stand×pitch / month | swings denominator printed |
| Chase & in-zone rate | `chase_rate` | era | zone > 9 = out of zone |
| Putaway rate | `putaway_rate` | era / era-group×pitch | 2-strike pitches denominator printed |
| First-pitch strike rate | `fpsr` | era | pitch_number == 1 |
| Hard-hit rate | `hard_hit_rate` | era | launch_speed ≥ 95, BIP denominator |

**New KPIs: none.** Arsenal usage/velocity/movement aggregates and the CH–FF velocity separation column reuse the descriptive-aggregate and separation patterns already specified and approved in dp_uc11 (§4 of its spec); no new computational logic was introduced.

## Deliberate scope narrowing vs uc-pps-017
uc-pps-017 (Luzardo) introduced seven provisional reconstruction KPIs (IP-from-log, RA9, FIP, CSW, TTO…). This UC **did not inherit them**: a closer retrospective is served by PA-rates + process metrics, and fewer provisional KPIs means a smaller certification surface. Recorded so the divergence reads as a choice, not an omission.
