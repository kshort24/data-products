# BID — Game 2 Bullpen Script: Mayza opens, Holman debuts

**Status:** **AWARDED 2026-09-13** (RFP exercise — bid filed and won per Kellen's explicit instruction to
treat the bid as a winner and proceed; reconciled against actuals in `07_platform_marketing.md`).
**Bidder:** the data product organization (`data-product-owner`, on behalf of all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-09-13
**ID reservation:** UC **#43** · contract `uc-pps-029` · build artifact `dp_uc43` ·
folder `uc-pps-029-game2-bullpen-script-001`

---

## The ask (as submitted)

A game-script note, written in the client's own voice, that arrived already invalidated in one place: the
scheduled starter (Luzardo) was scratched and Mayza opens instead. The note carries (a) an availability claim
— "last night cost four arms at an inning apiece" — (b) a nine-inning, nine-slot bullpen script, (c) a bet on
which arm goes multiple, and (d) a notebook cell profiling Grant Holman's Lehigh Valley work by batter
handedness, ahead of what would be his major-league debut. Deliverables requested: a governed package with
00–07 receipts, a PDF report, and an interactive dashboard if it earns its place.

## Why this shop wins this RFP

1. **The bullpen kernel is already paid for.** `Bullpen_Functions.ipynb` (`appearance_summary`,
   `add_rest_days`, `add_rolling_workload`, `pitcher_season_workload`) is the governed path from pitch-level
   Statcast to an availability ledger, and this shop inherits it verbatim rather than re-deriving rest days
   from scratch. A competitor bidding this cold writes its own rest logic and gets a different answer.
2. **This shop tests the client's premises instead of dressing them.** Falsify-before-describe is standing
   policy here (`uc-pps-027`, `uc-pps-028`, `uc-pos-016`). The ask contains three checkable claims. A shop
   optimizing for agreeableness ships a prettier version of the note. The value in this engagement is
   entirely in the claims that don't survive.
3. **We disclose the gap in the ask rather than picking a convenient reading.** The note's "last night"
   cannot be reconciled with the session date without choosing one of two target games, and the choice moves
   five of nine availability calls. That gets priced and escalated, not silently defaulted.
4. **Cross-level discipline is already governed here.** `uc-pos-015` (LV-1) established how AAA evidence
   enters an MLB conclusion. Holman is AAA-only; this shop already knows which of his numbers may be quoted
   and which may not.

## Data position — verified at bid time, not assumed

| Check | Result |
|---|---|
| Source (MLB) | `data/phillies/phils_2026.parquet` — regular season, PHI pitching, current through **2026-09-11** |
| Source (AAA) | `data/opponents/lhvp26.parquet` — current through **2026-09-06**; **no wOBA weight columns** |
| Entity locks | 9 MLBAM ids resolved before any computation; 8 in the MLB log, 1 (Holman, 680880) AAA-only |
| Holman volume | 348 pitches, 104 PA, 20 appearances — above the repo's small-sample floor for a mix/shape read |
| Holman MLB volume | **zero** — the supporting tier is the only evidence, and must be labelled as such throughout |
| Opponent starter | **no name field exists for opponent pitchers** (standing defect O-10) — identity must be inferred from the log and disclosed as inferred |
| Known defect exposure | D-1, D-7/O-13, O-3, O-8, O-14 all in scope; measured against the build, not assumed inapplicable |

## Deliverables bid

| # | Deliverable | Notes |
|---|---|---|
| 1 | Branded PDF report | ~7 pp, verdict first, markdown → weasyprint, Phillies CSS |
| 2 | Interactive dashboard | Self-contained HTML; a script the client can rebuild inning by inning with the coverage math live. No external code. |
| 3 | Governed kernel | `dp_uc43_kernel.py` — Sections A/B verbatim from the two governed notebooks, Section C new |
| 4 | Full receipts | `00`–`07` + README + this BID; ~28 CSV receipts + 4 figures + a JSON payload |
| 5 | Independent verification | 6 families including **family F** narrative/receipt reconciliation |
| 6 | Ledger patch | `uc_ledger_AI_PATCH_uc-pps-029-game2-bullpen-script.md` |

**Explicitly not bid / out of scope:** a post-game backtest (offered as the closure step, not delivered here);
a full opponent advance on the Braves lineup; run-expectancy or leverage-index modelling; any recommendation
that depends on a roster move not visible in the log.

## Price

**Basis:** `uc-pps-026` (Cortes, the first competitive-bid UC, bid $6.75 → actual $3.32) and `uc-pos-016`
(bid $4.90, delivered under on all axes) as the nearest analogues, loaded upward for three things neither of
them carried: **nine subjects instead of one**, **two source frames at two competitive levels**, and an
**opponent entity that has to be inferred rather than looked up**.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake + cross-repo reconnaissance (control plane + data plane, cold pairing) | 45k | 5k | 18 |
| T1 Source profiling + 10 entity resolutions incl. the unnamed opponent starter | 40k | 8k | 20 |
| T2 Kernel transcription (two notebooks) + build + defect-exposure measurement | 35k | 22k | 28 |
| T3 Figures + PDF + interactive dashboard | 25k | 26k | 30 |
| T4 Verification harness, families A–F | 12k | 14k | 15 |
| T5 Governance spine 00–07 + README + BID + ledger patch | 18k | 22k | 20 |
| Subtotal | 175k | 97k | 131 |
| Environmental contingency ~15% (device bridge + egress are the BASE CASE in this pairing) | +26k | +15k | +20 |
| **BID** | **~201k** | **~112k** | **~2 h 31 m wall clock** |

**Token credits:** at list rates ($10/M in, $50/M out): 201k × $10/M + 112k × $50/M ≈ **$7.61**, band
**$6–9**. Cowork bills subscription usage; read as API-equivalent credit value.

**De-scope options priced:** drop the interactive dashboard → −24k out, −28 min, ≈ −$1.20 (not recommended —
the coverage arithmetic is the finding, and a static table makes it look like a rounding argument rather than
a decision). Drop the opponent-starter section → −10k in, −6k out, −15 min, ≈ −$0.40. Report-only tier
(no 00–07, no verification) → ≈ **$3.10**.

## Assumptions, exclusions, carry-ins

- **Manual carry-ins from the client, accepted as given and logged:** Luzardo scratched; Mayza opens; the
  opposing starter is named "Mahle"; Holman is being promoted. None of these is in the log; all are in the
  freshness manifest.
- **Target game.** Priced for the game immediately after the last logged game (D+1, 2026-09-12), with the
  session-date framing (D+2) priced as a sensitivity rather than an alternative deliverable.
- **Regular season only.** Spring/exhibition rows are excluded from every rate on both frames.
- **No external data fetched.** Local parquet only. MLB StatsAPI is not reachable from this session's egress,
  which is why the opponent identity is inferred rather than looked up.
- **AAA rates are never blended into MLB rates**, and no wOBA is computed at AAA.

## Award mechanics

On award this file is retained as the pricing receipt; bid-vs-actual reconciliation lives in
`07_platform_marketing.md`.

---

> **STATUS UPDATE 2026-09-13: AWARDED.** Proceeded to delivery per Kellen's instruction to treat the bid as
> won. Actuals vs. bid in `07_platform_marketing.md`. Delivery spine: `00_dpo_orchestration_record.md`.
