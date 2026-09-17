# BID — Cristopher Sánchez: is he *near* the zone, or not?

**Status:** **AWARDED 2026-09-16** (RFP exercise — bid filed and treated as the winner per Kellen's instruction; reconciled against actuals in `07_platform_marketing.md` §3).
**Bidder:** the data product organization (`data-product-owner`, on behalf of all seven departments)
**Human DPO:** Kellen Short · **Bid filed:** 2026-09-16 18:35 ET (22:35 UTC), eleven minutes after intake opened
**ID reservation:** UC **#45** · contract `uc-pps-031` · build artifact `dp_uc45` · folder `uc-pps-031-sanchez-command-diagnosis-001`
Collision check at bid time: `ls dp_uc45*` → none (MLB root, `out/`, control plane); `uc-pps-031*` → none.

---

## The ask (as submitted)

A command diagnosis on Cristopher Sánchez (LHP, MLBAM 650911), delivered as a fully governed package with a PDF
and — if it earns its place — an interactive dashboard. The ask carries **four client premises**, **one new KPI
to be specified**, **one existing KPI to be found and honoured**, and **one proof the client wants to see**:

| # | Client input | How this shop reads it |
|---|---|---|
| P1 | "His walk rate is up in 2026" | A premise to **test**, at season *and* in-season grain |
| P2 | "He is in the zone less" | A premise to test — and, at bid time, **the one most likely to be a measurement artefact** (below) |
| P3 | "He is getting less chase" | A premise to test |
| P4 | "He is getting ahead in the count less" | A premise to test against the existing count-leverage definition (PD-7), not a new one |
| K1 | A "shadow rate": zone expanded by one baseball width; how often he **misses the shadow completely** | A **new governed object**, specified before it is computed, and made semantically consistent with the three "shadow/edge" geometries already in the repo |
| K2 | "I think I have previously defined an edge rate function" | **Found:** `edge_rate(level, df)`, UC8 origin, glossary-approved, Register v2 P16 disposition **A**, ratified `BALL_FT = 2.94/12`. Inherited verbatim |
| E1 | "Prove this out by showing changes in chase_rate when outside the shadow" | The load-bearing chart of the engagement |
| N1 | The notebook cell (monthly 2026 + 2023–25 seasons, kernel functions) | Reproduced **exactly** as the parent-reproduction receipt before anything new is built on it |

## Why this shop wins this RFP

1. **We have already written the book on this pitcher.** `uc-pps-019` (UC #22, 2026-07-14) is this shop's first-half
   All-Star retrospective on Sánchez; its entity lock, its kernel and its QR family are inherited, not rediscovered.
2. **We already know where the three "shadows" are buried.** The repo carries three incompatible shadow/edge
   geometries — `edge_rate` (UC8, Euclidean ±1 ball), the OZ family (`uc-pos-005`, rectangular ±1 ball, batter-side)
   and the Attack Zone partition (`uc-pps-022`, a 0.33 ft "shadow"). A competitor bidding this cold will invent a
   fourth. We have priced a reconciliation instead.
3. **We found the confound before we priced the answer.** Bid-time profiling shows the 2026 cache carries a
   **different strike-zone definition** than 2025: `sz_top` is now a single constant per batter (395 of 413 batters
   have exactly one value; within-batter SD 0.000 vs 0.072 ft in 2025), and for the 32 batters with 100+ pitches in
   both seasons the median top of the zone fell **0.23 ft (≈2.8 in)**. That is the height-based ABS zone
   (top = 53.5% of batter height, bottom = 27%). League in-zone rate in the Phillies log fell **.503 → .464** with it.
   **Any 2025→2026 zone-rate comparison that does not net this out is measuring MLB's rulebook, not Sánchez.**
   This shop has priced a peer-netted control and a common-rail re-score as line items.
4. **Falsify-before-describe is standing policy.** At bid time two of the four premises already look season-false
   (walk rate .054 → .055; chase *up*, .316 → .362). The value of this engagement is in *where* they are true.

## Data position — verified at bid time

| Check | Result |
|---|---|
| Source | `data/phillies/phils_2021…2026.parquet`, regular season, 281,623 pitches after dedup; current through **2026-09-15** (Sánchez started that day) |
| Subject | 650911 → exactly one `player_name` ("Sánchez, Cristopher") in every season; 0 duplicate pitch keys |
| Subject volume | 2021-22: 873 · 2023: 1,460 · 2024: 2,797 · 2025: 2,896 · **2026: 2,960 pitches / 805 PA / 31 starts** |
| Location completeness | 1 null `plate_x`/`sz_top`/`zone` row (2025) across 10,986 subject pitches |
| Zone definition | **Changed between 2025 and 2026** (above) — priced as T1b |
| IBB exposure (O-14) | Sánchez has **0** intentional walks 2021–2026 — kernel `bbrate` equals public BB% for him |
| device_bash | **Up**, but the user-machine VM has **no free disk** for `pyarrow`/`plotly`/`weasyprint` → the data plane is staged into the cloud workspace and committed back (environmental contingency 8%) |

## Deliverables bid

| # | Deliverable | Notes |
|---|---|---|
| 1 | Branded PDF report | ~9 pp, verdict first, markdown → weasyprint, Phillies CSS |
| 2 | Interactive command dashboard | Self-contained HTML: season / half / month grain, stand filter, pitch filter, live shadow map, premise scorecard |
| 3 | Governed kernel `dp_uc45_kernel.py` | Section A verbatim (Baseball Functions via dp_uc44), A2 `edge_rate` verbatim (UC8 via dp_uc38), B data access, C inherited SG-1/3/5, D **new** |
| 4 | New governed objects | **SZ-0…SZ-4** (the Shadow Zone family), **CL-1** `count_leverage` (PD-7 promoted to a function per Register P8), **PN-1** pitcher-side peer-netted delta (PB-1 adaptation), **ZC-1** common-rail re-score |
| 5 | The client's notebook cell, reproduced | Receipt `dp_uc45_notebook_reproduction.csv`, kernel-verbatim, with defect exposure measured |
| 6 | Full receipts | `00`–`07` + README + this BID; ~25 CSV receipts, 5 figures, JSON payload |
| 7 | Independent verification | Families A–F incl. narrative-to-receipt reconciliation (family E is mandatory per `uc-pps-030` §3) |
| 8 | Ledger patch + repo-side UC contract | `uc_ledger_AI_PATCH_uc-pps-031-sanchez-command.md`, `uc-pps-031-Cristopher Sanchez Command 20260916.md` |

**Not bid:** pitch-design / stuff modelling; release-point mechanics (`arm_angle` is 54% null on the 2026 cache — standing DQ-6); catcher/battery attribution (requires the catcher × game receipt and is a separate question); umpire/ABS challenge outcomes (not in the cache); ratification of any new object.

## Price

**Basis:** `uc-pps-030` (bid 276k/136k, actual ≈450k gross in ~55 min) as the nearest structural analogue: one pitcher, same client, same depth. Adjusted **down** for a six-season (not twelve-season) frame and no opponent; adjusted **up** for a new KPI family that must reconcile with three existing geometries, a rulebook-change control that no prior UC has needed, and a notebook reproduction. Tokens are priced as **session-budget drawdown** (the denominator this shop can actually meter); the reconnaissance already spent at bid time is **carried into the price, not hidden**.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, Rule-1 search across both planes, prior-Sánchez retrieval, staging (**already spent**) | 190k | 6k | 11 |
| T1a Premise tests P1–P4, season + half + month | 20k | 4k | 4 |
| T1b ABS zone-definition control (PN-1 + ZC-1) | 20k | 4k | 5 |
| T2 Kernel transcription + SZ/CL/PN/ZC specification + build + defect exposure | 50k | 30k | 12 |
| T3 Five figures | 30k | 18k | 7 |
| T4 PDF + dashboard | 30k | 22k | 8 |
| T5 Verification harness, families A–F | 25k | 16k | 6 |
| T6 Governance spine 00–07 + README + ledger patch + repo contract | 30k | 34k | 9 |
| Subtotal | 395k | 134k | 62 |
| Environmental contingency 8% on unspent phases (staging round-trip, OneDrive mount lag) | +16k | +10k | +5 |
| **BID** | **~411k** | **~144k** | **~67 min wall clock** |

**Token credits** at list rates ($10/M in, $50/M out): 411k × $10/M + 144k × $50/M ≈ **$11.31**, band **$9–14**. Minutes derived at the calibrated ≈0.12 min per 1k tokens (`uc-pps-030` §3), not estimated independently — the last two bids over-estimated wall clock by ~3×.

**De-scope options priced:**
- Drop the dashboard → −22k out, −8 min, ≈ −$1.30. *Not recommended* — the finding lives at half × stand × pitch grain.
- Drop the ABS control → −40k in, −8k out ≈ −$0.80. **Refused.** Without it the report's second premise is a rulebook artefact presented as a pitcher finding.
- Report-only tier (no 00–07, no verification) ≈ **$5.40**.

## Assumptions, exclusions, carry-ins

- **Manual carry-ins:** "Sánchez is struggling with his command in 2026" and "his performance is demonstrably worse" are the client's framing and are **tested**, not assumed. The ABS zone definition (53.5% / 27% of height, 17 in wide) is an **external fact** used only to *explain* a change the data already shows; it enters no computation.
- **Window cut:** 2026 first half = through **2026-07-13** (the All-Star break; Sánchez's last first-half start 07-11, first second-half start 07-20). The cut has a named cause.
- **2021 and 2022 combined** as "2021-22" per the client's permission (873 pitches — a swingman sample, flagged).
- **Regular season only**; 50 spring and 315 postseason Sánchez pitches excluded.
- **Geometry:** `PLATE_HALF = 0.83 ft` and `BALL_FT = 2.94/12` (Register v2 §4.1 ruling). Per-pitch `sz_top`/`sz_bot`. No new constant is introduced.

---

> **STATUS UPDATE 2026-09-16: AWARDED.** Proceeded to delivery per Kellen's instruction to treat the bid as won.
> Delivery spine: `00_dpo_orchestration_record.md`. Actuals vs bid: `07_platform_marketing.md` §3.
