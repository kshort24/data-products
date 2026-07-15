# 01 — Intake Gap Report (use-case-validator) · uc-pps-018

**Use case as received (DPO, 2026-07-13):** Recap Duran's first half as Phillies closer; 24 saves known externally; "has he done anything differently to get started this year?"; compare vs 2025 Phillies stint and prior Twins career; PDF required; accurate, disciplined, documented, defensible.

| # | Gap | Class | Resolution |
|---|---|---|---|
| G1 | "Saves" not derivable from pitch-level Statcast without a game-state reconstruction KPI | **Blocking until DPO decision** | DPO chose manual carry-in (2026-07-13). Resolved — logged in freshness manifest; no save-situation splits anywhere in product. |
| G2 | Deliverable depth unspecified ("creative delivery ok") | Non-blocking | DPO chose full governance package. |
| G3 | "First half" boundary — All-Star break vs calendar | Non-blocking | Defined as all 2026 R games through cache freshness 2026-07-12 (last appearance 07-11). Break starts today; no games missed. |
| G4 | "Prior career with the Twins" window | Non-blocking | Full available Twins cache 2022–2025-07-28 (`duran.parquet`); debut year = 2022, so career coverage is complete. |
| G5 | No official IP/ERA/W-L in pitch data | Non-blocking | Product speaks in PA-denominated rates from the locked kernel; stated in report caveats. No reconstruction attempted (unlike uc-pps-017's provisional PD-KPIs — narrower scope was chosen here deliberately). |

**Feasibility:** PASS. All business questions answerable from locked KPIs on entity-locked pitch logs. **Go.**
