# Token-Economist Calibration Report · uc-pps-026 (dp_uc36) · 2026-08-20

**Third instrumented run** (after uc-pos-004 pilot and uc-pps-019). **First run bid BEFORE award** —
the bid was filed 2026-08-19 as a competitive-bid receipt, held overnight on the DPO's "bid only"
decision, and awarded 2026-08-20. Every T2-T7 bid therefore preceded its execution by design;
T1 was largely spent at bid time and priced as such in the bid itself.

## Headline economics — bid vs actual

| Axis | Bid | Actual (est.) | Error |
|---|---|---|---|
| Input tokens | 150,000 | ~110,000 | **−27% over-bid** |
| Output tokens | 105,000 | ~44,300 | **−58% over-bid** |
| Wall-clock | ~150 min | ~93 min (bid session ~27 + award session ~66) | **−38% over-bid** |
| Token credits (Fable 5 list $10/$50 per M) | ≈$6.75 (band $6–9) | **≈$3.32** | ~half the bid |
| Accuracy | — | 184/184 verification · DQ 28 PASS/1 WARN/0 FAIL · build exit 0 first pass · 4 retries (1 semantic-adjacent: figure axis) | — |

*Method: chars/4 on artifacts for output; tool-result chars/4 + context reconstruction for input
(±20% systematic on input, ±5% on output — unchanged from the pilot). Prices working tokens, not
harness/system overhead, consistent with all prior ledgers.*

## Why the over-bid, honestly

1. **The bid scaled from the wrong axis.** It priced "acquisition depth" off Kilian's 205-check
   and Raley's 661-check packages, assuming verification scope drives output volume. It doesn't —
   **receipt-comparison harness design** (recompute vs published CSVs, loop-generated checks)
   buys arbitrary check counts at near-constant authoring cost. 184 checks cost ~4.3k output
   tokens, not the bid's 10k.
2. **Template inheritance keeps compounding.** The uc-pos-004 calibration predicted a spine
   template would cut trail cost 30-40%; actual T7 output came in 57% under bid because the
   Kilian 00-07 + telemetry schema needed no re-derivation at all. The pattern-inheritance map
   remains, economically, a price list — and its prices keep falling.
3. **Career-scale data does not scale cost.** 10,316 pitches vs Kilian's 1,271 changed compute
   time by seconds and token cost by ~0. The bid carried an unnecessary "career-scale" premium.
4. **Input over-bid is the recon double-count.** The bid priced T1 at 63k *including* already-
   spent recon, then the contingency added headroom on top of a warm sandbox. Actual environment
   tax: 3 installs, ~3 minutes.

## Corrections for the next bid

- Price verification by *harness design* (receipt-comparison ≈ 3-5k out flat), never by check
  count.
- Drop the data-volume premium entirely for pitch-level frames under ~50k rows.
- Carry contingency at 5% on a warm sandbox, 15% only on cold.
- Keep pricing the consumables (report/dashboard) at Kilian rates — those came in close to bid
  (T4/T5 output within ~2-3x, the tightest phases after T2).

## Fidelity-to-plan verdict for the DPO

Scope: **delivered as bid** (PDF + dashboard + full 00-07 + UD family + verification), plus the
premise corrections the data forced (P4 MIL→SD) and the DPO's P1 correction (Keller DFA). Cost:
**under bid on all three axes** — the bid was honest at bid time but conservative; the shop
banked the efficiency rather than consuming it. No scope was cut to hit the number.
