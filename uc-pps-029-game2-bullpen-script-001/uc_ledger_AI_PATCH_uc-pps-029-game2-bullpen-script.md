# UC Ledger patch — UC #43 / `uc-pps-029` / `dp_uc43`

**Paste the row below into `uc_ledger_AI.md` and update "Next available" to UC #44 / dp_uc44
(pps next: `uc-pps-030` · pos next: `uc-pos-017`).**

The ledger in the MLB repo is known to lag delivered UCs (see the standing `uc-ledger drift` note); verify
against `ls dp_uc*` and the control plane's `data-products/` tree before claiming any number. This row was
reserved and used consistently across every file in the package.

---

| 43 | uc-pps-029 | **Game 2 bullpen script — Mayza opens, Holman debuts (target 2026-09-12)** | Delivered — Verified 179/179 — Certification READY-CONDITIONAL | `data-products/uc-pps-029-game2-bullpen-script-001/` (00–07 + README + BID + report .md/.pdf + `dp_uc43_bullpen_control_room.html`) (**dp_uc43**), receipts `out/dp_uc43_*` (28 CSV + 4 PNG + payload + verification). **First bullpen-script UC** — prices a *prospective* plan rather than describing a pen; first UC to inherit `Bullpen_Functions.ipynb` verbatim. NEW provisional objects **BS-1** `bullpen_availability_tier`, **BS-2** `script_capacity`/`script_coverage_risk`, **BS-3** `multi_inning_propensity`, **OP-1** `opener_tto_delta` (could not discriminate — Mayza's entire 2026 population is TTO 1, which is itself the finding). **TWO NEW repo-wide defects: D-8** (`appearance_summary.is_start` is `pd.NA` for every reliever on a single-team frame → `pitcher_season_workload(relievers_only=True)` returns an EMPTY frame, silently) and **D-9** (`measure_calcs` renames `batter`→`pitches`, so `nresults(['batter'],df)` raises KeyError). Second competitive bid of the series priced under on time (−68%) and credits (−1%), over on output (+5%). Holman=680880 (AAA-only, zero MLB pitches); Mayza=641835; opposing starter **inferred** as MLBAM 641816 (O-10, no opponent pitcher name in the frame). **Finding:** the script is ceiling-dependent, not short — 29.7 expected BF at average outings vs a 37-BF regulation median (n=106 games), 38.1 at season highs, and its largest ceiling (10 BF) is Triple-A evidence in a debut. Client premises: "four arms down" → **five**, and the unnamed one (Alvarado) is the most-worked; "Duran goes multiple" → **1 of 56**; "Mayza gives you two" → **supported** (3 of 4 opener starts reached the 2nd). |

---

## What this UC adds to the pattern-inheritance map

- **Bullpen branch:** UC12 (reliever dashboard) → UC15/16 (bullpen-game inventory, multi-stint flag) →
  **UC43** (first prospective script pricing; first verbatim inheritance of the bullpen kernel).
- **Plan-shaped asks:** new branch. When the client supplies a finished plan rather than a question, the work
  is to price and falsify it. Cheaper to run and sharper in output than an open-ended ask — see `07` C-5.
- **Two-mode KPIs:** BS-2 ships `average` and `ceiling` capacity together because neither alone is honest.
  Extends the `uc-pos-016` DC-1 discipline (size a finding before amplifying it) from post-hoc revision to
  design time.
- **Cross-level evidence:** inherits `uc-pos-015` LV-1. AAA quoted for mix/shape/counting only; **no wOBA,
  no xwOBA, no hard-hit rate** at the AAA tier (the frame carries no wOBA weights and importing MLB constants
  would be a comparability violation).
- **Verification family F** (narrative/receipt reconciliation, from `uc-pos-016` v1.1.0) run again: 54 checks,
  zero findings. That is the outcome it is bought for.

## Open items carried forward

| ID | Item |
|---|---|
| **D-8** | Upstream one-line fix needed in `Bullpen_Functions.ipynb`. Tripwire BP-2. |
| **D-9** | Upstream conditional-rename fix needed in `Baseball Functions.ipynb`. Tripwire BP-3. |
| **BS-1/2/3, OP-1** | Provisional. Ratify only after an independent second use. |
| **O-10** | Opponent-pitcher name gap remains. Blocked this session by egress (StatsAPI 403). |
| **Backtest** | Post-game: scripted vs. actual innings, arms, and BS-1 tiers vs. who was actually used. The cheapest possible validation of BS-1 and the natural next UC. |
| **Bid denominator** | `07` C-2..C-5: fix the bid denominator to gross session consumption and re-baseline the series. |
