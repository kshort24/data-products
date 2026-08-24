# 00 — DPO Orchestration Record

**Agent:** `data-product-owner` (orchestrator) · **Use Case:** `uc-pps-026-cortes-acquisition-001` · **Value stream:** `pps`
**Ledger IDs:** UC **#37** · contract `uc-pps-026` · build artifact `dp_uc36`
**Human DPO:** Kellen Short · **Bid:** 2026-08-19 · **Awarded:** 2026-08-20 · **Delivered:** 2026-08-20
**Recommendation:** ✅ **Ready to publish (internal)** — 184/184 verification, 0 blocking items.

This is the spine: delivery plan, governance gates, capability fulfillment, publish
recommendation, and — new to this UC — the **bid-vs-actual economics gate** the human DPO
requested at award. Department detail lives in 01–07.

---

## The ask, in one line

> *"We signed Nestor Cortes off arm surgery. How has he been deployed in his career, what are his
> platoon splits and how has his approach evolved, what did his stuff look like and what was
> trending before the injury, and what actually drives his good and bad stretches — turned into
> actions for the manager, the battery, and the pitching department?"*

**First UC delivered through a competitive-bid flow:** bid filed 2026-08-19 (tokens/$/time),
held on the DPO's "bid only" decision, awarded 2026-08-20 with two DPO notes: (1) **premise
correction — Brian Keller was DFA'd for the 40-man spot**, not a Kilian 60-day-IL move (logged
P1, no analytic impact); (2) **telemetry must mirror the bid** for post-delivery fidelity
comparison (delivered in `telemetry/`).

## Delivery plan & layer status

| Layer | Departments | Status |
|---|---|---|
| 0 — Bid | DPO | ✅ BID doc retained in-folder as the pricing receipt |
| 1 — Intake & Discovery | Strategy & Intake | ✅ GO — 0 blocking, 6 non-blocking; 6-premise register (1 DPO-corrected, 1 data-corrected) |
| 2 — Design | Engineering (Design) ∥ Governance | ✅ UD-1..6 specced before use (gate order held); Rule-1 grep performed |
| 3 — Build | Engineering (Build) | ✅ exit 0 first pass — 28 CSV + 5 figures + console log |
| 4 — Certify | Quality | ✅ **READY** — 184/184 independent checks · DQ 28 PASS / 1 WARN / 0 FAIL |
| 5 — Launch | Consumer Success ∥ Marketing | ✅ 7pp branded PDF + 4.9MB self-contained dashboard + persona guides |
| 6 — Operations | Platform (persistent) | ✅ RB-1 re-baseline tripwire ARMED (2026 rows fail loudly by design) |

**Front door:** `visual-intake-agent` skipped — written use case from the human DPO.

**Pattern inheritance.** UC#3 → UC#8 → UC#11 → UC#29 (Painter, return-from-injury) →
UC#30 (Kilian, acquisition template) → UC#31 (Raley) → **UC#37 (this): third pitcher
acquisition read, first acquisition × return-from-surgery hybrid, first competitive-bid flow.**

## What is genuinely new in this UC

1. **The UD deployment family (UD-1..6)** — the DPO's own notebook logic, promoted to governed
   specs. The verification harness runs the DPO's *original double-merge method* as the
   independent code path; all 56 season-cells agree exactly. Glossary promotion candidates.
2. **The bid flow itself** — a priced, held, then awarded engagement with bid-vs-actual
   telemetry. Reusable for any future UC where the human DPO wants cost visibility before work.
3. **The pre-return baseline shape** — subject has both a career record AND a hard data
   boundary (surgery). The product's freshness model is a tripwire (07 RB-1), not a schedule.

## Governance gates checked at handoff

| Gate | Where enforced | Result |
|---|---|---|
| 1. No CDE inference | 03 glossary | ✅ locked-inherited or DPO-supplied; UD family specced from the DPO's definitions, returned as promotion candidates |
| 2. No build without approved specs | 02 → 04 | ✅ 01–03 written before build ran |
| 3. No publish without certification | 05 | ✅ READY; 184/184 |
| 4. No breaking changes without notice | 07 | ✅ new product, v1.0.0 manifest |
| 5. Privacy flags block external publish | 03 | ✅ INTERNAL — acquisition-evaluation judgments; health facts restricted to public reporting |

## Escalations / open items for the human DPO

| # | Item | Severity | Ask |
|---|---|---|---|
| O1-O3 | xwOBAcon promotion · strict zone · EV foul trap (inherited, unchanged) | Medium | standing repo-wide decisions; this UC applied all three hardenings |
| **UD** | UD-1..6 provisional | Medium | ratify for the glossary — "Bulk Appearance" is the load-bearing term; next converted/bulk pitcher inherits |
| **F1** | Shared vendored `_assets/plotly.min.js` for dashboard products | Low | cost-watchdog recommendation (07 §3) — ~4.7 MB per future dashboard |
| O4 | 2019-vintage leverage evidence | Low | any high-leverage deployment decision should wait for post-return data (report says so in-line) |

## Capability fulfillment map

| Consumer question | Answered in | Backed by |
|---|---|---|
| Deployment history — starter/reliever/bulk? | Report §Deployment · dashboard V1 | `usage_by_season`, `appearance_log` (DPO-method verified) |
| Platoon splits & approach evolution? | Report §What he throws · dashboard V2 | `platoon_by_phase/season`, `mix_by_hand_season`, `pitch_by_hand_2023_25` |
| Stuff, pre-injury trend, what to monitor? | Report §The stuff · dashboard V3 | `stuff_by_pitch_season`, `monthly_arc_2024_25`, `mechanics_by_season` |
| What drives good/bad stretches? | Report §Drivers · fig5 | `era_delta_peak_decline`, `outing_terciles`, `season_indicators` |
| Manager actions (6-man? bulk? leverage? rest?) | Report §Manager | `times_through_order`, `rest_performance`, `relief_entry_states_2019_21` |
| Battery actions | Report §Battery | `putaway_pitch_by_hand`, `count_usage_*`, `location_side_by_hand` |
| Pitching-department cues | Report §Pitching department | velo/IVB/slot receipts + tercile tells |
| (The Freeman clause) | Report §Manager item 5 | `postseason_context` (context only) |

**8 of 8 question families answered with receipts.** Nothing answered from judgment alone.

## Economics gate (new, DPO-requested)

Bid ~150k in / ~105k out / ~2.5h / ≈$6.75 → actual ~110k / ~44.3k / ~93 min / **≈$3.32**.
**Under bid on all axes with full scope delivered** — detail and corrections in
`telemetry/calibration_report.md`. The bid discipline held: no scope trimmed to hit a number.

## Publish recommendation

✅ **PASS — cleared for internal use.** Ledger append: UC #37 / `uc-pps-026` / `dp_uc36`.
**Next available: UC #38 / dp_uc37** (pps next `uc-pps-027` · pos next `uc-pos-013`).

```json
{"uc":37,"id":"uc-pps-026","build":"dp_uc36","status":"delivered_pending_dpo_signoff",
 "bid":{"filed":"2026-08-19","awarded":"2026-08-20","tokens_in":150000,"tokens_out":105000,
        "minutes":150,"usd":6.75},
 "actual":{"tokens_in_est":110000,"tokens_out_est":44300,"minutes":93,"usd":3.32,
           "verification":"184/184","dq":"28 PASS/1 WARN/0 FAIL"},
 "open_items":["O1","O2","O3(inherited)","UD ratification","F1 shared plotly asset"],
 "closure_step":"RB-1 armed: first 2026 rows -> re-run build+verification, grade 3 falsifiable calls, publish v1.1 return read; RB-2 at 100 PHI BF"}
```
