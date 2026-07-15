# 03 — Governance
## uc-pps-019 · business-glossary + data-tagger + privacy-watchdog

## A. Business glossary alignment
No governed term is redefined. Locked terms consumed as-is: PA, wOBA, xwOBA, whiff rate, chase rate, in-zone rate, putaway rate, first-pitch strike rate, hard-hit rate, CSW, TTO, RA9-from-deltas, FIP.

**New provisional terms** (pending human-DPO ratification; definitions in 02 §C):
| Term | ID | Status |
|---|---|---|
| Quick-Resolution Rate | QR-1 | Provisional — new in uc-pps-019 |
| Pitches per PA | QR-2 | Provisional (descriptive companion) |
| Quick-Resolution Quality | QR-3 | Provisional — new in uc-pps-019 |
| Scoreless-Streak Receipt | SL-1 | Provisional — receipt-class metric, not for reuse without caveats |

Duplicate check: no existing QR-family term in prior UC specs (checked dp_uc17/18/20 spec sections). "Pitches per PA" appeared informally in UC #21 (SC-2, P/PA from the batter side); QR-2 is the pitcher-side mirror — cross-referenced, not conflicting.

## B. Tagging proposal (data-tagger — for DPO review, not published)
- Sensitivity: **Public** (professional on-field performance; no PII beyond public identity).
- Domain: Phillies Pitching (pps) value stream. Subject area: pitcher performance retrospective.
- Product membership: `uc-pps-019-sanchez-first-half-allstar-001` · runtime crosswalk `dp_uc21`.

## C. Privacy-watchdog note
Player-level performance data of a public figure in a professional context; no quasi-identifier combination risk beyond what MLB publishes. Persona narratives reference staff roles (catcher, manager) generically or by public identity. **No flags. External-publish gate: clear.**

## D. Version-controller note
New product, v1.0.0. No consumer migrations. QR-family KPIs marked provisional — promotion to governed status is a non-breaking additive change; any later formula change to QR-1 after ratification would be **breaking** for trend continuity and requires a version bump + consumer notice.
