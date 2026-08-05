# UC-POS-008 — Luis Arraez, deadline acquisition read

```yaml
use_case_id: uc-pos-008-arraez-acquisition-001
ledger_uc: 32
build_artifact: dp_uc31
value_stream: pos
subject:
  name: Luis Arraez
  mlbam_id: 650333
  bats: L
  acquired: 2026 trade deadline (from SF)
  phillies_pa_at_build: 0
consumer: Human DPO (Kellen Short), on behalf of the Phillies batting department
personas: [hitting coach, manager, analytics group, front office]
requested: 2026-08-04
delivered: 2026-08-04
status: build complete — ready for human DPO sign-off
classification: Internal — Restricted
version: 1.0.0

evidence_window:
  primary: {span: "2026-03-26..2026-08-02", pitches: 1727, pa: 464, role: "carries all forward-looking claims"}
  shadow:  {span: "2019-05-18..2025-09-28", pitches: 13501, pa: 3533, role: "stability backdrop only"}
sources:
  - {file: data/opponents/arraez.parquet, rows: 15228, entity: "batter==650333", filters: "game_type=='R', dedup(pitch key)"}
  - {file: data/phillies/phils_2026.parquet, rows: 16269, entity: "phillies_role=='batting'", role: "comparison set + lineup structure"}
  - {file: wOBA and FIP Constants.csv, role: "season wOBA weights, joined on game_year"}
  - {file: league_sc_data.csv, role: "structural reference ONLY — max year 2023, not a 2026 benchmark"}
manual_carry_ins:
  - deadline acquisition and roster context
  - Mattingly's cleanup-spot decision
  - Harper's move back to the outfield
  - "leadoff-hitter premise — CONTESTED, see open item OI-1"

new_kpis_provisional: [AR-1 TSSR, AR-2 TSDL, AR-3 DPGH, AR-4 SPCR, AR-5 LSOP, AR-6 SPRC, AR-7 TSV]
locked_kpis_modified: 0
quality: {build_dq: "24/24", verification: "368/368", failures: 0}
```

---

## Problem statement

The Phillies acquired Luis Arraez at the 2026 deadline. He is the headline addition, he has reshuffled the infield, and he has pushed Bryce Harper back to the outfield for the rest of the season. **The organisation has never employed him and has zero plate appearances of him in its own uniform.**

The consumer holds a strong prior — a contact-first, low-slug, extremely low-whiff hitter who puts together wild at-bats — and wants it tested rather than confirmed. Beyond the profile, one decision is live: **where in the batting order should he hit?** Mattingly has him at cleanup on the theory that it is the spot with the most opportunities with men on base. The consumer wants to know whether the top of the order would be better, and specifically whether to swap him with Schwarber.

## Questions

| # | Question | KPI | Answered in |
|---|---|---|---|
| Q1 | What are his top-line results? | locked slash, wOBA/xwOBA, SC-1, SC-2 | report §1 |
| Q2 | What underlying indicators are the results standing on? | locked contact-quality + discipline + bat tracking | report §2 |
| Q3 | How well does he collect hits with two strikes? | **AR-1, AR-2** | report §3 |
| Q4 | Which pitch groups and which handedness can he slug? | **AR-3** | report §4 |
| Q5 | How does he perform with runners in scoring position? | **AR-4** | report §5 |
| Q6 | Where should he bat, and what is it worth? | **AR-5, AR-6, AR-7** | report §6 |
| Q7 | What should the batting department actually do? | — (synthesis) | report §7 |

## Answers, in one line each

**Q1.** .324/.347/.441 in 464 PA, .337 wOBA, .117 ISO — a career-high ISO built from 23 doubles and 7 triples, with a 4.5% strikeout rate.

**Q2.** The results are **33 points of wOBA ahead of the contact** for the first time in his career, on an 0.7% barrel rate, 86.0 mph exit velocity and a 0.0% fast-swing rate. Expect .300–.310. **The "wild at-bats" prior is not supported** — 3.72 pitches per PA, below average.

**Q3.** **The standout finding.** He survives two strikes 90.1% of the time; the best Phillie is 67.0% and Schwarber is 43.0%. He is the only regular on the roster who is not a net negative in two-strike plate appearances. He does it by expanding to a 56.3% chase rate with a 4.7% whiff rate. But surviving is not damaging: his two-strike line is .264/.296/.333.

**Q4.** All the supported damage is **fastballs from right-handers** — .481 SLG on a .331 xwOBAcon over 187 balls in play. The apparent power against left-handed breaking balls (.500 SLG) sits on a 78.1 mph average exit velocity and a .253 xwOBAcon and is not real. **Against LHP overall he is outrunning his contact by 71 points of wOBA.**

**Q5.** Best on the roster — **34.3% of scoring-position runners driven in**, with **one strikeout in 89 such plate appearances**. But his own seven-year range is .222–.560; plan on ~.30.

**Q6.** **The whole decision is worth 3.95 runs per 162.** Cleanup is his best individual slot and the consumer's reasoning about it is confirmed (slot 4 leads the order at 47.8% men-on). Against the **observed** lineup (Turner leading off) the proposed swap **costs 2.58 runs**; against the **stated** lineup (Schwarber leading off) it gains **0.65** — inside the noise. The model's own preference is **Arraez second, Schwarber fourth** (+1.79 over the stated arrangement), and the reason is downstream: slots 2–3 hand their runners to better converters than slots 4–5 do.

**Q7.** Leave the approach alone; the only live coaching conversation is the left-handed matchup. Monitor out-of-zone contact rate as the early-warning signal. Use the two-strike skill as a late-inning contact tool. Set expectations at league-average offence with an extreme distribution — Schwarber outproduces him in every lineup slot by ~20 runs per 162.

## Actions

**Hitting coach**
1. Do not chase launch angle. The adjustment already happened (attack angle 3.9° → 7.6°) and it worked.
2. Monitor out-of-zone contact rate (89.2%). It is the leading indicator for everything else.
3. Prepare the left-handed-pitching matchup conversation — .441 SLG on a .256 xwOBA, 2.1% walk rate.

**Manager**
4. Keep him at cleanup, or move him to second. Both are defensible and about one run apart. Do **not** swap him with the leadoff hitter under the observed lineup.
5. Use him as the roster's highest-probability ball-in-play option in late-inning contact spots.

**Analytics group**
6. Hold the organisation to the .300–.310 wOBA projection and the three closure tests.
7. Do not propagate AR-1…AR-7 into other products before ratification.

**Front office**
8. Message him as a fit and a contact skill, not as an offensive upgrade.

## Open items

| # | Item | Severity |
|---|---|---|
| OI-1 | **Leadoff premise contested** — request says Schwarber, log says Turner (399 PA vs 95). Both framings priced; recommendation changes sign | **Blocking for circulation to manager/coaching staff** |
| OI-2 | AR-1…AR-7 provisional; ratification needed | Non-blocking |
| OI-3 | O4 `xwobacon` size semantics — carried from `uc-pps-025` | Non-blocking |
| OI-4 | **O5 (new)** `truncated_pa` definitional fork; 2026 unaffected | Non-blocking |
| OI-5 | AR-6 holds opportunity weights fixed | Non-blocking |
| OI-6 | No Citizens Bank Park adjustment | Non-blocking |

## Closure

Re-read at **150 PA in a Phillies uniform**, testing three falsifiable projections:

1. wOBA regresses from .337 toward **.300–.310**.
2. Production vs LHP declines toward the **.256 xwOBA**.
3. **Two-strike survival holds above .85.** If this fails, supersede the UC rather than amend it — the acquisition thesis rests on it.

## Ledger

| Field | Value |
|---|---|
| UC number | **32** |
| Contract | `uc-pos-008` |
| Build artifact | `dp_uc31` |
| Prior in `pos` | UC #28 / `uc-pos-007` / `dp_uc27` (loanDepot venue split) |
| Prior overall | UC #31 / `uc-pps-025` / `dp_uc30` (Raley acquisition read) |
| **Next available** | **UC #33 / `dp_uc32`** (`pos` next: `uc-pos-009` · `pps` next: `uc-pps-026`) |

> **Ledger maintenance.** `uc_ledger_AI.md` in the MLB repo is stale (last updated at UC #25). This row and the intervening UCs #26–#32 need to be appended. Flagged to the human DPO.
