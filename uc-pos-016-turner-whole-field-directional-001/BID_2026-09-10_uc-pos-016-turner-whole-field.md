# BID — Trea Turner: Whole-Field Directional Tendency

**Status:** **AWARDED 2026-09-10** (RFP exercise — bid filed and won per Kellen's explicit instruction to
treat the bid as a winner and proceed; work below reflects the actual delivery, reconciled against this bid
in `07_platform_marketing.md`).
**Bidder:** the data product organization (`data-product-owner`, on behalf of all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-09-10
**ID reservation:** UC **#42** · contract `uc-pos-016` · build artifact `dp_uc42` · folder `uc-pos-016-turner-whole-field-directional-001`

---

## The ask (as submitted, 2026-09-10)

A working theory, not a confirmed finding: Turner is pulling outside-zone pitches too often in 2026 rather
than going the other way, a drift from 2023-2025 Phillies-era behavior. Explicit instruction to **lead the
narrative against the data**, not confirm the premise. Attached (referenced, not received by this session —
see `01_strategy_intake.md` G-1): a working markdown draft and a hand-sketch of the intended visual layout.
Five known corrections to carry in without re-deriving; three open decisions delegated to this layer to
resolve rather than default on silently.

## Why this shop wins this RFP

1. **The entity and the coordinate system are already paid for.** Turner's MLBAM id (607208), the
   `hc_x`/`hc_y` → `loc_x`/`loc_y` transform, and the governed `hit_direction` classification were all
   established and verified across two prior Turner builds (`uc-pos-006`, `uc-pos-014`). A competitor
   bidding this cold re-derives all three; this shop reuses them verbatim and inherits their defect history
   for free (the O-7 loc_x/loc_y-schema-absence fix, in particular, would otherwise bite a from-scratch
   build immediately).
2. **We disclose a gap instead of guessing past it.** `sort_rank` was requested as "fix the existing
   function's handedness bug" — no such function exists in the repo. A shop optimizing for the appearance of
   completeness fabricates one and calls it inherited. This shop searched (Rule 1), found nothing, said so,
   and built a new one correctly rather than guessing at unseen prior logic.
3. **Falsify-before-describe is standing policy**, and it earns its keep here: the premise, tested literally,
   does not hold. A shop that defaults to confirming what the client hypothesized would have shipped the
   wrong finding.

## Data position — verified at bid time, not assumed

| Check | Result |
|---|---|
| Source | `data/phillies/phils_{2023..2026}.parquet`; `phils_2026.parquet` current through 2026-09-09 |
| Entity lock | `batter == 607208` — reconfirmed a third time (after `uc-pos-006`, `uc-pos-014`) |
| Volume | 1,832 regular-season BIP, 2023-2026 (490/408/484/450) |
| Untracked BIP | 0 — no D6/O-8 exposure for this subject/window |
| Stand mix | 100% `R` — verified, not assumed |
| Schema | No asymmetry issue for this UC (Phillies-era only; the pre-PHI `turner.parquet` schema mismatch that affects full-career hitter UCs does not apply here) |

## Deliverables bid

| # | Deliverable | Notes |
|---|---|---|
| 1 | Branded PDF report | ~4 pp, verdict table first, reportlab (environment substitution for weasyprint — see `04`) |
| 2 | Interactive HTML dashboard | Self-contained, Chart.js vendored inline (reused from `uc-pos-014`'s vendored copy, not re-fetched) |
| 3 | Full receipts | `00`-`07` + README + this BID; 5 CSV receipts + 2 figures |
| 4 | Independent verification | `dp_uc42_verification.py`, 33 spot-checks, second code path (diagnostic tier — see `05`, not the full ~700-check harness) |
| 5 | Governed kernel | `dp_uc42_kernel.py` — `derive_loc`/`hit_direction`/`in_zone` inherited verbatim; `sort_rank` new |
| 6 | Ledger patch | `uc_ledger_AI_PATCH_uc-pos-016-turner-whole-field.md` |

**Explicitly not bid / out of scope:** a persona action card (no causal/coaching angle requested), a
consumer-onboarding pass beyond the primary requester persona, a swing-mechanics follow-on (flagged in `06`
as a natural next UC, not this one).

## Price

**Basis:** `uc-pos-014`'s instrumented actuals (174k in / 121k out / 171 min bid → 121k / 74k / 65 min
actual) as the nearest analogue for a Turner-subject, kernel-inheriting hitter UC, discounted further for
this UC's single-question (not full-season) scope, and **loaded with an explicit environmental-contingency
phase** — the one line item this repo's bid history has not previously had to price (see `07`'s calibration
finding).

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake + repo reconnaissance (cold pairing, no prior session context) | 40k | 4k | 15 |
| T1 Environmental contingency (device-bridge failure, egress-blocked package managers, pure-Python Parquet reader) | 45k | 18k | 25 |
| T2 Kernel + build + verification (85% inherited from `dp_uc40_kernel.py`) | 15k | 12k | 15 |
| T3 Figures + PDF + dashboard (vendored Chart.js reused, not re-fetched) | 12k | 10k | 15 |
| T4 Governance spine 00-07 + README + BID + ledger patch | 14k | 16k | 15 |
| Subtotal | 126k | 60k | 85 |
| Environmental contingency ~15% (device bridge could reconnect mid-build; PDF cross-plane build) | +19k | +9k | +10 |
| **BID** | **~145k** | **~69k** | **~1 h 35 m wall clock** |

**Token credits:** at Fable 5 API list rates ($10/M in, $50/M out): 145k × $10/M + 69k × $50/M ≈ **$4.90**,
band **$4-7**. Cowork bills subscription usage; read as API-equivalent credit value.

**De-scope options priced:** drop the dashboard → −10k out, −15 min, ≈ −$0.50. Drop the second figure
(pull/oppo trend bars, keep only the facet grid) → −4k out, −8 min, ≈ −$0.20 — not recommended, it is the
figure that makes the in-zone finding legible without reading the z-scores.

## Assumptions, exclusions, carry-ins

- **Regular-season rates only** — postseason BIP exist for 2023-2024 (218+33 rows) and are excluded from
  every rate; 2026 has no postseason yet, so including postseason for prior years only would be an
  apples-to-oranges baseline.
- **No RISP / count-state / platoon-deep-dive** requested here — scoped strictly to whole-field direction.
- **Manual carry-in:** none needed — no season-boundary or All-Star-break definitions are used by this UC.
- **No external data fetched.** Local parquet only, read via a build-time pure-Python fallback reader (see
  `04`) because the standard `pyarrow` path was unavailable in this session's environment.

## Award mechanics

On award this file is retained as the pricing receipt; bid-vs-actual reconciliation lives in
`07_platform_marketing.md` (no separate `telemetry/` directory for this diagnostic-tier build — the
reconciliation table in `07` serves that purpose at this scope).

---

> **STATUS UPDATE 2026-09-10: AWARDED.** Proceeded to delivery per Kellen's instruction to treat the bid as
> won. Actuals vs. bid in `07_platform_marketing.md`. Delivery spine: `00_dpo_orchestration_record.md`.
