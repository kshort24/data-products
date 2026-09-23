# BID — Archetype Gap Analysis, pilot: the Elite RHP Four-Seamer

**Status:** **AWARDED 2026-09-22** (RFP exercise — bid filed and treated as the winner per Kellen's instruction; reconciled against actuals in `07_platform_marketing.md` §3).
**Bidder:** the data product organization (`data-product-owner`, on behalf of all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-09-22 (23:00 ET)
**ID reservation:** UC **#47** · contract `uc-pps-032` · build artifact `dp_uc47` · folder `uc-pps-032-elite-rhp-ff-archetype-gap-001`
**Collision check (bid time):** `dp_uc47*` — none at MLB root, none in `out/`, none in the control plane. `uc-pps-032*` — none. Ledger file says "next #25" and is stale (known drift, see `uc-ledger-drift`); ground truth is `uc-pos-017` README → **next #47**.

---

## The ask (as submitted)

A notebook cell titled **"Roster addition"** in `September 2026.ipynb` (cell 101), written in the client's own
hand, with four DPO decisions already answered inline:

| # | Decision | Client answer |
|---|---|---|
| 9 | New value stream `rca`? | **Keep as `pps` with a scope note** |
| 10 | Population for the external comparison | **Bounded set** ("this era") |
| 11 | `nphl` scope | **Non-Phillies, but not MLB-wide** |
| 12 | "Benefit most" — aspirational or plausible-acquisition? | **Aspirational, open to suggestions** |

Plus: a six-arm cohort (Wheeler, Painter, McFarlane, Duran, Bowlan, Seranthony Domínguez), a draft data spec
(grain pitcher × season; flags `ff_elite_stuff_flag` / `ff_elite_results_flag`), and four working Plotly cells —
Wheeler's four-seam velocity by year against a 99 mph line, Painter's velocity, spin and ride split at the
demotion. Each cell carries a subtitle that is a **claim**: *"Clearly trending down, but the middle 50% of his
FFs in 2026 roughly matches 2024"*, *"Clear difference after his demotion"*, *"Noticeably more after going down
to AAA."* Deliverables: 00–07 receipts, PDF, a dashboard if it earns its place, and the instruction to **tell
the story, not report the facts.**

## Why this shop wins this RFP

1. **The grading engine already exists, and this is its ratification.** `uc-pps-030` (Painter, 2026-09-13)
   built SG-1 `scouting_grade_20_80` and SG-2 `benchmark_population` and left them *provisional pending an
   independent second use*. An archetype is a grade on a population. This engagement **is** the second use —
   a competitor re-invents a 20-80 scale; we ratify one.
2. **We know what `nphl` actually is, because we have been burned by it.** It is every parquet in
   `data/opponents/` concatenated — 128 files, **905,751 rows**, of which **18,305** are internal duplicates,
   **30,229** duplicate rows already in the Phillies logs, and **15 files are minor-league** (Lehigh Valley,
   Clearwater, Jacksonville, Toledo…). The client's own "every four-seamer in my dataset" frame (the Bowlan and
   Kilian ride charts in `brand-center-mcp/Brand Guidelines and Graph Samples.md`) concatenates `pps + pos +
   nphl` with none of that removed. A shop that takes the frame at face value grades MLB arms against Double-A
   fastballs. We price the cleaning as the first deliverable, not a footnote.
3. **"Not MLB-wide" is a sampling-frame problem, and we have the method.** A pitcher-season in this frame can be
   a full season (a dedicated player file), a team pull, or two incidental starts against the Phillies. Two
   starts of whiff rate is not a fastball. We bid an **empirical-Bayes stabilization** step (split-half
   reliability → shrinkage constant) so that a thin sample cannot top a leaderboard by luck. No competitor bid
   that we have seen prices this.
4. **The human parent is the product.** The client's notebook subtitles are checkable. House standard since
   `uc-pos-015` is to reproduce the requester's own method first and attribute every divergence. Four notebook
   claims plus two prior hand-grades (Duran "70 FF" on the 9/17 index card; Bowlan "exceptional vert") are
   priced as a reconciliation family.
5. **Names are a known trap here.** `player_name` is the *batter* on batting-role rows (uc-pps-031 finding 5),
   and team pulls in `nphl` are batter-keyed. We bid a keyed-frame name resolver with a `des`-parse fallback,
   validated against the keyed names before it is trusted.

## Data position — verified at bid time, not assumed

| Check | Result |
|---|---|
| Phillies logs | `phils_2015…2026.parquet`, 554,289 rows; 2026 current through **2026-09-20** |
| `nphl` | 128 files / 905,751 rows; 15 MiLB files; 18,305 internal dups; 30,229 dups of the Phillies logs |
| Era (decision 10) | **2018–2026** — the first and last season any cohort arm threw an MLB four-seamer in the frame |
| Bounded population (preview) | **405** RHP four-seam pitcher-seasons ≥100 FF, 2018–2026, in the de-duplicated MLB-only union |
| Drift | Velocity **+0.16 mph/season (p<.001)** and spin **+8.3 rpm/season (p=.003)** across the era; ride, whiff, run value flat. A 2018 grade and a 2026 grade are not on the same ruler without an adjustment |
| Entity locks | Wheeler 554430 · Painter 691725 · McFarlane 686934 · Duran 661395 · Bowlan 680742 · Domínguez **622554** (resolved from the log) |
| Thin subject | **McFarlane: 94 four-seamers**, all 2026 — below the population floor, above the 50-pitch subject floor. Gradable, stamped THIN |
| Carry-in | Bowlan left the 9/17 game with a suspected oblique (client notebook). Not in the parquet. Logged, not modelled |

## Deliverables bid

| # | Deliverable | Notes |
|---|---|---|
| 1 | **Archetype map** (hero figure) | Every pitcher-season in the bounded set, shape grade × results grade, the elite quadrant shaded, the six arms traced across their seasons |
| 2 | Narrative PDF | ~12 pp, story-first, in the client's notebook voice; Phillies brand; verdicts before tables |
| 3 | Interactive archetype explorer | Self-contained HTML; population / cohort / candidate filters, weight slider, role toggle; reads the same receipts as the PDF |
| 4 | Governed kernel `dp_uc47_kernel.py` | Inherits `dp_uc44_kernel` by import with a hash check; new Section C is **archetype-agnostic** — a spec object, not an FF-shaped function |
| 5 | New governed objects | FR-1 universe, NR-1 name resolver, AF-1…AF-6 archetype family, SG-6 trend adjust, SG-7 stabilization — each with a kpi-calculator spec |
| 6 | Human-parent reconciliation | 6 client claims, reproduced with his method and re-run governed |
| 7 | Receipts | `00`–`07` + README + this BID; ~30 CSV receipts; brand-center compliance scorecard |
| 8 | Verification harness | Families A–F, including F = every number the report prose asserts |
| 9 | Ledger patch + repo-side contract | `uc_ledger_AI_PATCH_…` and `uc-pps-032-… 20260922.md` |

**Explicitly not bid:** availability, contracts, service time, injury status (decision 12 — aspirational);
true league-wide population (decision 11 — the frame is bounded and labelled as such everywhere); projections
of 2027 performance; any ratification of AF-1…AF-6 (needs a second use — the pilot is by definition the first).

## Price

**Basis:** `uc-pps-030` actuals (~450k tokens, ~55 min) — same grading engine, same client, same depth.
**Up** for a population ~1.9× the rows of any prior pps build (1.22M-row union vs 393k), a cohort of six
instead of one subject, an external candidate pool, a new KPI family, and a human-parent reconciliation.
**Down** for inheriting SG-1/SG-2, the PDF and dashboard templates, and the verification harness pattern.
Denominator is **incremental session tokens** (new context + generated), consistent with the last three bids.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, cross-repo recon, 128-file staging, `nphl` profiling (**sunk at bid time: ~330k**) | 300k | 30k | 12 |
| T1 Universe build, name resolution, drift + reliability study | 60k | 18k | 8 |
| T2 Kernel Section C + AF/SG specs + build + receipts | 90k | 45k | 16 |
| T3 Figures (6) + brand-center compliance pass | 45k | 22k | 9 |
| T4 PDF + interactive explorer | 45k | 35k | 11 |
| T5 Verification harness, families A–F | 35k | 20k | 7 |
| T6 Governance spine 00–07, README, contract, ledger patch | 35k | 55k | 12 |
| Subtotal | 610k | 225k | 75 |
| Contingency 5% (bridge up this session; egress partial — PyPI yes, Chadwick/StatsAPI no) | +30k | +11k | +5 |
| **BID** | **~640k** | **~236k** | **~80 min wall clock** |

**Token credits:** at list rates ($10/M in, $50/M out): 640k × $10/M + 236k × $50/M ≈ **$18.20**, band **$15–22**.
Cowork bills subscription usage; read as API-equivalent credit value.

**De-scope options priced:**
- Drop the explorer → −35k out, −11 min, ≈ −$1.75. *Not recommended*: the weight slider is how the client sees that "best" depends on what he values.
- Cohort ranking only (sub-question 1, no external gap) → ≈ **$9.50**. That is the profile UC the client said needs no new product.
- Report-only tier (no 00–07, no harness) → ≈ **$8.00**.
- Add availability/contract plumbing (decision 12, constrained) → **cannot be bid**: no roster or contract source exists in either repository.

## Assumptions, exclusions, carry-ins

- **Regular season only.** Postseason, spring, exhibition excluded at load (GT-1: level by source first, date second).
- **Minor-league rows never enter the population.** Level gate = both teams are MLB clubs.
- **"Currently on the Phillies" = threw a pitch for Philadelphia in the 2026 regular season.** Anyone else is a candidate. Seranthony Domínguez (41 pitches *against* the Phillies in 2026) is therefore a candidate as well as a cohort member, and the report says so.
- **No external data enters any computation.** One external-identity attempt (Chadwick register via `pybaseball`) failed at the proxy; names are resolved from the logs only and validated.
- **Bowlan's injury** is a client carry-in, not a data fact.

---

> **STATUS UPDATE 2026-09-22: AWARDED.** Proceeding per Kellen's instruction to treat the bid as won.
> Actuals vs. bid in `07_platform_marketing.md` §3. Delivery spine: `00_dpo_orchestration_record.md`.
