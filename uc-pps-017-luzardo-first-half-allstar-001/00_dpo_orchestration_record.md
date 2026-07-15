# 00 — DPO Orchestration Record · uc-pps-017-luzardo-first-half-allstar-001 (UC #19)

**Use case:** Jesús Luzardo is a first-time All-Star (2026). Assess the first half: high-level outcomes first, then the indicators that plausibly drove them, then a persona-action narrative (manager / pitching department / Luzardo / catcher) with retrospective credit **and** a second-half watch list per persona.
**Requested by:** Kellen (DPO), 2026-07-13. **Delivered:** 2026-07-13.
**Value stream:** Phillies Pitching (pps). **Entity lock:** pitcher == 666200.
**Pattern:** pps mirror of `uc-pos-marsh-breakout-001` (UC #18, Marsh first-All-Star retrospective); KPI kernel inherited from dp_uc11 (current pps exemplar).

## Delivery plan (as executed)

| Layer | Work | Outcome |
|---|---|---|
| 1 Intake | Use-case validation, source fitness, entity/freshness lock | GO — no blocking gaps (see 01) |
| 2 Design | Locked cores inherited verbatim + 7 derived KPIs (PD-1..PD-7) | Specs in 02; provisional definitions logged in 03 |
| 3 Build | `dp_uc17_luzardo_first_half.py` run live vs mounted parquet layer | 13 CSV + 3 PNG receipts in `MLB/out/dp_uc17_*` |
| 4 Certify/Publish | DQ scorecard + independent recomputation of headline numbers | PASS (see 05); report published in-package (.md + .pdf) |

## Governance gate checks

1. **No CDE inference** — all result metrics computed with locked Baseball Functions mechanics inherited verbatim via dp_uc11. New derived KPIs (PD-1..PD-7) are flagged NEW, specified in 02, and held provisional for DPO ratification (03). None redefines an existing governed term. IP and RA9 are explicitly labeled reconstructions; **official ERA/W-L are not published** because the pitch log cannot compute them.
2. **No build without specs** — build script embeds the locked kernel verbatim; new-files-only respected (no repo file edited; receipts are new `dp_uc17_*` files; ledger updated via patch file at MLB repo root).
3. **No publish without certification** — 05 records PASS on entity lock, dedup, game_type, weights join, and independent recomputation (K=136, PA=465, wOBA=.295, sweeper usage=.371, starts=19 — exact match).
4. **Versioning** — first release (v1.0.0); no breaking-change surface.
5. **Privacy** — public MLB Statcast data; no PII beyond public player identity. Not blocking.

## Capability fulfillment

| Use-case requirement | Where met |
|---|---|
| High-level outcomes first | Report §1–§2; `season_line`, `season_xwoba`, `start_log`, `staff_benchmark`, `monthly` receipts |
| Indicators driving performance | Report §3–§5; `arsenal_yoy`, `process_kpis_yoy`, `by_stand_yoy`, `tto_yoy`, `count_leverage_yoy` receipts |
| Persona narrative (mgr / dept / Luzardo / catcher) | Report §6, each claim tied to an indicator, labeled inference |
| Forward-looking watch lists | Report §6 (per persona) + §7 sustainability |
| Scouting-report style, adapted | House template adapted from advance-report to retrospective (same voice, warning box, receipts discipline) |

## Publish recommendation

**READY — publish internal.** Conditional (inherited from UC #18): the §6 persona narrative is *inference consistent with the data* and must not be quoted as observed fact. Ledger patch `uc_ledger_AI_PATCH_uc-pps-017-luzardo-first-half.md` filed at MLB repo root; header advances to UC #20 (next pps: uc-pps-018).

## Escalations to human DPO

- PD-1..PD-7 provisional definitions (03) await ratification — none blocking.
- July split (49 PA) and Marchán battery split (70 PA) are below the 100-BF convention; retained with flags because recency and battery attribution are core to the use case.
- Skill-side UC ledger (`references/uc-ledger.md`) still shows "next = #12"; repo reality is ahead of it — patch files pending paste (known drift).
