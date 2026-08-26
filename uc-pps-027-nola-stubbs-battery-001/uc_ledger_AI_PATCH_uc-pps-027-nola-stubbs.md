# uc_ledger_AI PATCH — paste into the MLB repo ledger

Append row:

| 38 | uc-pps-027 | The Nola–Stubbs Battery: game-planning under a changed catcher (pre-game 2026-08-26, PHI @ SEA) | **DELIVERED 2026-08-26 · CERTIFY-READY · 117/117 verification PASS** | `Agents for Data Products/data-products/uc-pps-027-nola-stubbs-battery-001/` — `dp_uc38_*` (build, verification, report harness, 00–07 spine, bid, telemetry). 5th extension of the Nola advance file; **first delivered consumer of `uc-cat-001`** (ships its KPI-1 and KPI-3 as BAT-4/BAT-9). New KPI family BAT-1…BAT-9 + CS-1, all NEW-PROVISIONAL pending ratification (O-11). New governance controls: **G3 confound panel** for non-randomised splits, **G4/AT-1 pitch-call attribution not observable**. First **Tier-A fixture unit-test harness** in the repo (certifies KPI logic without the data plane). **Headline finding: the approach change is PITCHER-LEVEL, not battery-specific — 10 of 12 metrics move the same way in the non-Stubbs starts (TR-1 adjustment-travel test).** New method family **TR-1 / TR-2 / OC-1 / LH-1 / CH-1** + guardrails **G6 / G7**, all NEW-PROVISIONAL. `uc-pps-021` tripwire closed: 3 of 4 indicators moved (LHH BB% .119→.068, CH vs LHH .179→.274, LHH wOBA .385→.313); LHH first-pitch strike rate did NOT move (.578→.581). **O-12 CLOSED** (accent-insensitive id→name cross-check — repo-wide pattern). Delivered across two runs; **36% over bid**, cause logged as calibration finding **C-1 premise risk**. New open items O-11/O-13/O-14 |

Update "Next available": **UC #39 / dp_uc39** (pps next **uc-pps-028** · pos next **uc-pos-014**).

---

**Ledger drift reminder:** this is roughly the sixth staged `uc_ledger_AI_PATCH_*` awaiting a
paste (pps-015, pps-016, pps-017, pos-006, pos-012, marsh, and now pps-027). The scouting
skill's own ledger copy also still reads "Next available: UC #12" and is ~26 UCs stale.
