# 00 · DPO Orchestration Record — `uc-pps-029-game2-bullpen-script-001`

**Version: v1.0.0**
**Orchestrator:** `data-product-owner`, on behalf of all seven departments
**Human DPO:** Kellen Short · **UC #43** · contract `uc-pps-029` · build artifact `dp_uc43`
**Delivery date:** 2026-09-13 · **Status:** READY-CONDITIONAL (see `05`)

## 1 · The ask and framing

Kellen handed over a game-script note written in his own voice, which had already invalidated itself in one
place: it was drafted around a Luzardo start, Luzardo was scratched, and Mayza opens instead. The note carries
an availability claim ("last night cost four arms at an inning apiece"), a nine-inning bullpen script, a bet
on which arm would go multiple, and a notebook cell profiling Grant Holman's Lehigh Valley work ahead of a
likely major-league debut. He asked for a governed package with 00–07 receipts, a PDF report, an interactive
dashboard if it earned its place, and a token/time estimate framed as a competitive RFP bid — to be treated as
won, and proceeded on.

The organization read this as a **plan-shaped ask**: the client supplied the hypotheses, so the work is to
price and falsify them rather than to describe the bullpen. That read shaped everything downstream.

## 2 · Delivery plan (departments actually engaged)

| Order | Department | Output | Status |
|---|---|---|---|
| 0 | Pricing | `BID_2026-09-13_uc-pps-029-game2-bullpen-script.md` — filed, awarded, reconciled in `07` | Done |
| 1 | Strategy & Intake | `01_strategy_intake.md` — gap report (7), premise stress-test (7), source fitness, opponent resolution, discretion log | Done |
| 2 | Engineering Design | `02_engineering_design.md` — 6-layer data model, join/fan-out check, 8 EDA findings, the design change they forced, metadata map, DQ rules, dashboard spec | Done |
| 3 | Governance | `03_governance.md` — Rule-1 search, 4 new objects, column lineage, 2 new defects, exposure table, privacy, tagging, versioning | Done |
| 4 | Engineering Build | `04_engineering_build.md` — build manifest, environment, 10 build-time assertions, reuse queries, 43 receipts | Done |
| 5 | Quality & Certification | `05_quality_certification.md` — 12-check DQ scorecard, defect register, 171-check verification, certification decision | Done |
| 6 | Consumer Success | `06_consumer_success.md` — personas, reading order, dashboard walkthrough, re-run recipe, action note | Done |
| 7 | Platform & Marketing | `07_platform_marketing.md` — 7 tripwires, cost audit, bid-vs-actual, 4 calibration findings | Done |

Layer-1's four agents (`use-case-validator`, `source-system-profiler`, `domain-steward-proxy`,
`business-glossary-agent`) did not produce separate hand-off files; at this scope their outputs are folded
into `01`, in line with `uc-pos-014` and `uc-pos-016`. `machine-learning-engineer`, `cost-watchdog`'s
infrastructure arm, and `consumer-onboarding-agent`'s full multi-persona pass were scoped out — no prediction
task, no pipeline to cost, one primary persona.

## 3 · Governance gate checks

| Gate | Result |
|---|---|
| **No CDE inference** | One definition was missing — "an arm is down." The build did **not** infer it silently; it registered `bullpen_availability_tier` as a new, provisional, unratified object with a full spec (`03` §2) and said so in the report's caveats. Every other term was inherited. |
| **No build without approved specs** | All seven gaps and all seven premises were logged and dispositioned in `01` before `02`/`04` began. The one ambiguity that could not be resolved from the data (the target date) was priced both ways rather than defaulted. |
| **No publish without certification** | `05` ran before this file. **READY-CONDITIONAL**, five conditions, one DQ **FAIL** deliberately shipped attached to the framing it belongs to. |
| **No breaking changes without notice** | v1.0.0, no prior version. Change semantics registered in `03` §8, including the note that a cache refresh is not a patch here — the anchor moves. |
| **Privacy flags block external publish** | **LOW** (`03` §6). Two findings sit adjacent to a medical inference (Holman's 44-day gap, Kerkering's seven-day absence); **neither is characterised** and no cause is asserted for either. |

All five cleared. No gate overridden.

## 4 · Capability fulfilment

| Kellen's requirement | Fulfilled by | Note |
|---|---|---|
| Work in the MLB repo as the data plane | `dp_uc43_kernel.py::load_pps/load_pos/load_lhv` read `data/phillies/` and `data/opponents/` | Data-plane folder access requested as the **first action** of intake |
| Use the Agents repo as the structure and engine | 00–07 spine + BID in `data-products/uc-pps-029-game2-bullpen-script-001/` | Layout inherited from `uc-pos-016` |
| Receipts in a subfolder of `data-products/`, 00–07 format | 8 governance files + README + BID + ledger patch | |
| Follow the scouting-report skill for inspiration | Entity lock by MLBAM id; multi-level evidence tier for a small sample; PA printed on every small-sample line; bottom-line-first with a data-window warning at the top; candid caveats at the end; markdown→weasyprint PDF | The skill's non-negotiables were treated as binding, not advisory |
| Follow data-plane coding standards | Sections A and B of the kernel are **verbatim transcriptions** of the two governed notebooks; `PITCH_COLORS` and the strike-zone overlay inherited from the house skill | Known defects measured against the build, not patched |
| Token/time estimate as a competitive RFP bid, treated as won | `BID_...md`, reconciled in `07` §3 | Under on time and credits, over on output — with the measurement caveat stated |
| PDF report | `dp_uc43_bullpen_script_report.pdf` | 7 pp, 4 figures embedded as data URIs |
| Explore an interactive dashboard | `dp_uc43_bullpen_control_room.html` | Self-contained; the script is rebuildable inning by inning with the arithmetic live |
| Other additions driven by the organization | The recommended revision (report §6); the second BS-2 capacity mode; the D+1/D+2 sensitivity; verification family F; two defect write-ups | None of these were asked for |

## 5 · The finding, in the DPO's words

**The script is sound in who it uses and fragile in what it assumes they can do.** Nine innings from seven
arms, priced at each arm's own 2026 average outing, delivers **29.7 batters faced** against a **37-batter**
regulation median — about **2.4 innings** short. Priced at every arm's season high it delivers **38.1** and
just covers. So the plan is not simply short; it is **ceiling-dependent**. And the single largest ceiling it
leans on is **ten batters faced, set at Triple-A by a pitcher who would be making his major-league debut**.

Two of the client's three stated premises did not survive:

- **"Four arms at an inning apiece."** It was five. Alvarado threw the 7th and is absent from the list — and
  by workload he is the most compromised arm in the pen (zero days rest, fourth appearance in seven days, 61
  pitches in that window). Meanwhile two arms he wrote off, Shugart and Raley, threw **nine pitches each**.
  He is protecting the wrong arms and has the tired one scripted for the eighth inning.
- **"Duran's the name I'd bet on to go multiple."** Duran has gone two innings in **1 of 56** relief outings
  this season. The pen's length is Shugart (15 of 40), Mayza (16 of 50) and, on AAA evidence, Holman (8 of 20).

One premise survived cleanly and is worth saying so: **Mayza can give you two.** Four opener starts this year,
three reached the second inning, mean 25.8 pitches. And a structural point that removes a worry nobody raised:
a two-inning open reaches batters 1–6, all still first-time-through — every one of his 987 pitches in 2026 is
`n_thruorder_pitcher == 1`. The constraint on Mayza is pitch count, not the order.

The recommendation is a **reallocation, not a replacement**: same seven arms, with the two-inning asks moved
off (Mayza, Holman) and onto (Mayza, Shugart). That prices at 37.4 against the client's 38.1 — the same
number inside the noise — but every stretch in it has been done in the major leagues by the arm being asked.

## 6 · Where the organization argued with itself

Three points of internal friction, all resolved by disclosure rather than by taking the convenient answer:

1. **The headline was too loud the first time.** The initial BS-2 result — "2.4 innings short" — was true at
   the average and rhetorically oversized, because the EDA had already shown that relievers in bullpen games
   run well above their season average (5.0 and 7.1 BF per arm in this season's two precedents). Keeping the
   single number would have made a plausible plan look incompetent. Adding the ceiling mode made the finding
   **smaller** and made it correct. This is the `uc-pos-016` DC-1 discipline — size a finding before
   amplifying it — applied at design time rather than in a revision.
2. **The recommended revision prices *worse* on the metric that produced the finding.** Under the average
   mode the revision is identical to the client's script (same seven arms, 29.7 BF), and an earlier draft of
   it used six arms and scored *worse*. The organization could have quietly chosen the metric that flattered
   its own recommendation. Instead the revision is argued on **evidence quality** — whose ceiling, set in
   which league — and the metric's own weakness is written into the KPI spec (`03` §2, BS-2 "known weakness").
3. **The target date.** Adopting D+2 (the session date) would have produced a much cleaner story: zero RED
   arms, a comfortable pen, no awkward conditional. The log does not support it, and the client's own four
   names reconcile exactly to the 09-11 game. D+1 was adopted, D+2 shipped as a priced sensitivity with a DQ
   **FAIL** attached, and the difference between them is reported as a finding rather than smoothed away.

## 7 · Escalations to the human DPO

These need Kellen's answer, not just his awareness:

1. **Which game is this for?** D+1 (2026-09-12) or D+2 (2026-09-13)? Five of nine availability tiers move.
   If it is D+2, **refresh the parquet cache before acting** — a 09-12 game, if it exists, is not in it, and
   the D+2 ledger as shipped is computed from a log that may be a game short.
2. **Is MLBAM 641816 Mahle?** The inference rests on four constraints (`01`) and is strong, but StatsAPI is
   unreachable from this session and nothing independent confirms it. If it is wrong, report §8 describes the
   wrong pitcher.
3. **Do you know why Kerkering hasn't pitched since 09-04?** 59 appearances, then seven days. The log has no
   explanation and this build asserts none. It matters: he is the freshest arm in the pen and the revision
   leans on him.
4. **D-8 needs an upstream fix, and it is not cosmetic.** `pitcher_season_workload(relievers_only=True)` has
   been returning an **empty DataFrame, silently**, for every caller passing a single-team frame. Any prior
   bullpen analysis that got "no relievers" got a bug. The one-line fix is in `03` §4; this build worked
   around it locally rather than editing the locked notebook.
5. **BS-1's thresholds are unratified judgment.** The inputs are governed; the GREEN/AMBER/RED cut-points are
   this build's. Recommend leaving all four new objects provisional until an independent second use — and the
   cheapest second use is the post-game backtest offered in `07`.
6. **Ledger patch is pending paste.** `uc_ledger_AI_PATCH_uc-pps-029-game2-bullpen-script.md`. Mechanical, but
   it is the artifact meant to outlive this package, and per the V-1 lesson an unpasted patch propagates
   nothing.

## 8 · Publish recommendation

**Publish internally now, as READY-CONDITIONAL.** The analysis is independently verified (179/179 across six
families, including a full narrative/receipt reconciliation), it answers the question the client actually
asked, and it answers it against him where the data says so. Do not promote BS-1/BS-2/BS-3/OP-1 to
APPROVED-KPI status yet. Do not re-quote the AAA tier out of context. Do not act on the availability ledger
until the target game is confirmed. External publication is not blocked by privacy but was not the ask.
