# 07 — Consumption & Observability (analytics-enabler + consumer-onboarding + data-observability) · uc-pps-020

## How to consume this product
- **Two-minute read:** report "Bottom line" (5 numbered claims) + fig 1. The whole case is: rates All-Star-grade, volume wasn't.
- **Per-persona entry points:** manager → §2 start log + §4 TTO; pitching dept → §3 arsenal/velocity + the sinker flag; Wheeler → §3 location strategy + §5; front office → §1 staff benchmark + §5 advocacy note.
- **Query the receipts, not the report:** all 15 CSVs in `out/dp_uc23_*` are grain-labeled. To re-slice (e.g., different velo grain, added split), re-run `dp_uc23_wheeler_first_half.py` — do not hand-edit receipts.

## Interpretation guardrails for consumers
- xwOBA columns are the contact-only proxy; never quote them as full-PA xwOBA (see report header).
- RA9 ≠ ERA; IP is event-out reconstructed. Quote as "runs allowed per 9 while on the mound."
- Sub-100-PA cells (July, April, TTO-3) are directional; the report prints PA on every such line — keep them attached when excerpting.
- The report never explains *why* Wheeler debuted late; do not attach a cause when circulating.

## Observability / refresh triggers
| Trigger | Action |
|---|---|
| phils_2026 cache refresh post-ASG | No action — first half is closed; receipts frozen |
| Season end (or award-ballot window) | Renewal: full-year refresh as Cy Young advocacy brief (offered in 00) — re-parameterize `FH_CUTOFF[2026]` to season end |
| Sinker deployment review (staff-level flag, §5) | Cross-UC follow-up candidate: early-count sinker usage staff-wide (joins uc-pps-019 finding) |
| Schema drift in caches (e.g., pitch taxonomy relabel) | Arsenal receipts keyed on `pitch_name` strings — relabel would surface as new rows, not silent corruption; check `dp_uc23_wheeler_arsenal_yoy.csv` row set on any re-run |

## Version status
v1.0.0 — first delivery, no prior consumers, no deprecations. Any change to the locked kernel is out of scope for this product (kernel is owned upstream, dp_uc21 lineage).
