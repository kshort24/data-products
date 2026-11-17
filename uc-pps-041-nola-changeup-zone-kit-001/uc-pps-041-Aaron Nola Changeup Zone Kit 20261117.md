# Use Case uc-pps-041 — Aaron Nola 2026: the changeup, in the zone (Claude Design kit)

```yml
name: Aaron Nola Changeup Zone Kit 20261117
id: uc-pps-041-Aaron Nola Changeup Zone Kit 20261117
description: >
  Analytical closer for the client's video of Nola's 28 changeups taken for strikes in zones 7-9 in 2026: a baseball-true, zone-scaled
  home-plate map of all 489 MLB changeups with the 28 highlighted, a count board, and five KPI cards, shipped as a Claude Design kit.
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — READY-CONDITIONAL (C1-C3)
owner: Kellen Short
parent_use_case: uc-pps-040 (UC #64); client notebook code (intake/client_prompt_2026-11-17.md)
uc_number: 65
build: dp_uc65 v1.0.0
kernel: dp_uc65_kernel.py (imports dp_uc64_kernel 32a83b84..., 13 pins)
entity_lock: pitcher == 605400
window: 2026 MLB (R + postseason) for the map; regular season 2015-2026 for cards; anchor 2026-10-01
kpis_inherited: putaway_rate, whiff_rate, chase_rate (in_zone_rate), nresults, csw, rv100, K48 GROUP_MAP; UC64 SQ-2 + prior re-read
kpis_new: CZ-1, PNZ-1, BB-1, EC-1, TS-1, ZN-1, CSB-1, FP-1 (provisional); deviation DV-1
deliverables: [slides/ kit (content, registry 33 strings, brief, manifest, data 12, ref 6 PNG + 6 JSON)]
verification: harness 20/20 · DQ 5/0/0 · V1-V7 6/6 · clip reconciliation 28 = 28
trail: Agents for Data Products/data-products/uc-pps-041-nola-changeup-zone-kit-001/
```
