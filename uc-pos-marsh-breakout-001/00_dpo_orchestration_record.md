# 00 — DPO Orchestration Record · uc-pos-marsh-breakout-001 (UC #18)

**Use case:** Brandon Marsh is a first-time All-Star (2026). Explain the breakout: first-half results vs career, the indicators driving the change, and a data-backed narrative of tangible actions by Marsh / hitting department / manager.
**Requested by:** Kellen (DPO), 2026-07-12. **Delivered:** 2026-07-13.
**Value stream:** Phillies position player (pos). **Entity lock:** batter == 669016.

## Delivery plan (as executed)

| Layer | Work | Outcome |
|---|---|---|
| 1 Intake | Use-case validation, source fitness, entity/era resolution | GO — no blocking gaps (see 01) |
| 2 Design | KPI set: locked cores inherited verbatim + 4 derived approach indicators | Specs in 02; provisional definitions logged in 03 |
| 3 Build | `marsh_breakout_analysis.py` run live vs mounted parquet layer | 16 CSV consumables in `MLB/out/marsh_breakout_*` |
| 4 Certify/Publish | DQ receipts + independent recomputation of headline numbers | PASS (see 05); report published in-package |

## Governance gate checks

1. **No CDE inference** — all result metrics computed with locked Baseball Functions mechanics; new derived indicators (pulled-air rate, PA funnel, discipline panel, early-count wOBA) are flagged as NEW and specified in 02 with provisional definitions held for DPO ratification (03). None redefines an existing governed term.
2. **No build without specs** — build script embeds the locked kernel verbatim; new-files-only rule respected (no repo file edited; ledger updated via patch file).
3. **No publish without certification** — 05 records PASS on dedup, null, weight-join, and recomputation checks.
4. **Versioning** — first release of this product; no breaking-change surface.
5. **Privacy** — public MLB Statcast data, no PII beyond public player identity. Not blocking.

## Capability fulfillment

| Use-case requirement | Where met |
|---|---|
| First-half recap vs prior seasons | Report §1; `marsh_breakout_results_by_season.csv`, `_pace_per600.csv` |
| Indicators driving the change | Report §2–§5; discipline / battedball / spray / platoon / pitchgroup / countstate / funnel CSVs |
| Approach-change assessment | Report §3 (swing profile), §5 (2025-halves dating of the shift) |
| Persona action narrative | Report §6 (Marsh / hitting dept / manager), each claim tied to an indicator |
| Sustainability caveats | Report §7 + locked-proxy footnote |

## Publish recommendation

**READY — publish internal.** One conditional: the persona narrative in §6 is *inference consistent with the data*, labeled as such; it must not be quoted as observed fact. Ledger patch `uc_ledger_AI_PATCH_uc-pos-marsh-breakout-001.md` filed in MLB repo root; header advances to UC #19.

## Escalations to human DPO

- PD-1..PD-4 provisional definitions (03) await ratification — none blocking.
- July cold stretch (40 PA) is below the 50-PA convention; retained with flag because recency matters to the breakout question.
