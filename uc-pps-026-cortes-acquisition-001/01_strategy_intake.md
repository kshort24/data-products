# 01 — Strategy & Intake

**Department:** Strategy & Intake · **Use Case:** `uc-pps-026-cortes-acquisition-001`
**Agents:** `use-case-validator` · `source-system-profiler` · `domain-steward-proxy`
**Ledger IDs:** UC **#37** · contract `uc-pps-026` · build `dp_uc36` · **Date:** 2026-08-20
**Front door:** `visual-intake-agent` skipped — written use case supplied by the human DPO (`Nestor Cortes Use Case.md`, filed in this folder's intake record).

---

## 1. use-case-validator — gap report

**Verdict: GO — 0 blocking, 6 non-blocking.** The use case arrived unusually complete: four
question families, three named personas, and working notebook logic for the deployment KPIs.

### Premise register (verified against data or corrected by DPO)

| # | Premise as submitted | Disposition |
|---|---|---|
| P1 | "To make room on the 40-man roster, Caleb Kilian was transferred to the 60-Day IL" | **CORRECTED BY DPO (2026-08-20): Brian Keller was DFA'd to make room.** Information only — no analytic impact; roster mechanics are out of data-plane scope. Logged as a manual carry-in correction. |
| P2 | "All-Star campaign in 2022" | **SUPPORTED** — 2022 is his career-peak season in-frame (see 04 build: .225 wOBA-against over 617 PA, career best among full seasons). All-Star selection itself = manual carry-in (not a Statcast field). |
| P3 | "Allowed the grand slam to Freddie Freeman in the 2024 World Series" | **VERIFIED IN-FRAME** — game_type `W`, 2024-10-25, inning 10, 0-0 count, FF at 92.2 mph: "Freddie Freeman hits a grand slam (1) to right field." Receipt: `out/dp_uc36_postseason_context.csv`. Context only — postseason rows never blend into rates. |
| P4 | "He spent last year with San Diego" | **PARTIALLY SUPPORTED** — 2025 in-frame is **MIL (2 games, Mar 29 + Apr 3) then SD (6 games, Aug 6 – Sep 3)**. He *finished* 2025 with San Diego. The 4-month in-season gap is itself evidence: 2025 was already injury-interrupted before the fall surgery. |
| P5 | "Production has fallen off the last couple years since 2022" | **TESTABLE** — this is Business Question 4's driver analysis; priced, not presumed. |
| P6 | "Don Mattingly has leveraged a six-man rotation in his managerial career" | **OUT OF DATA-PLANE AUTHORITY** — manager-history claim, no local source. Carried as unverified DPO context; the deliverable answers "does Cortes fit a 6th-starter/bulk role", not "what has Mattingly done historically". |

### Gaps (all non-blocking)

| # | Gap | Severity | Disposition |
|---|---|---|---|
| G1 | **2026 is a true gap** — zero competitive pitches since 2025-09-03 (surgery mid-Oct 2025). | non-blocking | Kilian-pattern governance: disclose, never impute. The product is a *pre-return baseline*, and says so on page 1. |
| G2 | Surgery type unspecified in reporting available at intake ("some type of surgery on his arm"). | non-blocking | Not guessed. Monitoring cues in the report are generic to arm-surgery return (velo/spin/extension baselines), not procedure-specific. |
| G3 | No Phillies rows, by construction (signed 2026-08-19). | non-blocking | Acquisition-variant standard (inherited from uc-pps-024). |
| G4 | No 2026 rehab/MiLB data locally. | non-blocking | Closure step: re-read at first 100 PHI batters faced (or after 3 rehab outings if a cache lands). |
| G5 | ERA/IP/saves not derivable — no built `gms_AI` for this pitcher. | non-blocking | Rate stats + appearance-grain KPIs carry the deployment story; disclosed in report caveats. |
| G6 | High-leverage relief evidence is dated — his last sustained relief work is 2019–21. | non-blocking | The manager section prices this: leverage answers are marked **directional, era-dated**. |

## 2. source-system-profiler — fitness report

**Source:** `data/opponents/cortes.parquet` · fetched ~2026-08-15 · **entity lock `pitcher == 641482`** (single id, single name in-frame).

| Property | Value |
|---|---|
| Rows / cols | 10,316 pitches / 120 columns · career 2018-03-31 → 2025-09-03 |
| game_type | R 10,087 · D 153 · L 55 · W 21 — **rates computed on R only**; postseason = context receipts |
| Team by season (derived: fielding team = home if Top else away) | 2018 BAL · 2019 NYY · 2020 SEA · 2021–24 NYY · 2025 MIL→SD |
| Season pitch volumes (R) | 2018: 108 · 2019: 1,305 · 2020: 165 · 2021: 1,524 · 2022: 2,465 · 2023: 1,070 · 2024: 2,851 · 2025: 599 |
| Arsenal in-frame | FF 4,707 · FC 2,543 · ST 1,471 · CH 822 · SL 527 · SI 172 · CU 60 |
| DPO probe reconciliation | `cortes_np.csv` (MLB repo root, DPO's own nphl+pps concat) = identical 10,316-row frame — notebook numbers will trace |

**Field availability boundaries (sensor-boundary NULL standard, uc-pos-009 — never impute):**

| Field | Boundary |
|---|---|
| `arm_angle` | **absent 2018–19** (0%), partial 2020 (75%), ≥92% 2021+ — arm-angle trend reads start at 2021 |
| `bat_speed` | swing-side field, 2024+ only — informational, excluded from KPIs |
| `launch_speed` | populated on fouls (O3 standing trap) — every EV mean filters `type == 'X'` |
| `pitcher_days_since_prev_game` | 64% in 2018 — **rest days derived from appearance-date diffs instead** |
| Null-`pitch_name` rows | 10 in R frame (8 `automatic_ball`, 2 `ball`) — TRACKED population excludes them from mix/location denominators |
| Hawk-Eye core (velo/spin/plate/sz/zone) | ≥96% every season — FIT |

**Fitness verdict: FIT for all four question families**, with the platoon and stuff families
strongest (career-scale denominators) and the leverage sub-question weakest (era-dated, G6).

## 3. domain-steward-proxy — carry-ins and steward notes

Manual carry-ins (logged in the freshness manifest, sources in 07):
signing 2026-08-19, 1-yr prorated ML deal · **Brian Keller DFA'd for the 40-man spot (DPO
correction supersedes the use-case text)** · surgery mid-Oct 2025, no competitive pitches since ·
reporting expectation: multi-inning relief for the 2026 stretch run · 2022 All-Star selection.

Steward notes: (a) LHP — platoon direction conventions flip vs the RHP exemplars: arm side =
first-base side, `hb_in = -pfx_x*12` still reads arm-side positive for a LHP only after a sign
check, asserted empirically in the DQ scorecard; (b) his 2019 usage includes opener-adjacent
"bulk" work — the DPO's bulk definition is the governing one (02 §2); (c) 2020 SEA is a 5-game
COVID-season sliver — kept in season grain, excluded from phase tiers (below the 100-BF floor).
