# Calibration — uc-pps-027 (UC #38) · bid vs actual

**Bid:** 129k in / 92k out / 150 min → ≈ **$5.89** API-equivalent
**Actual:** 86k in / 64.3k out / 105 min → ≈ **$4.08** API-equivalent
**Variance:** **−33% input · −30% output · −30% time**

## But read the variance honestly

The run came in under bid on every axis **and did not deliver the full scope.** T3 execution
and the T4 numeric fill did not happen. Estimated remaining cost to complete once the data
plane is mounted: **~8k in / ~10k out / ~20 min ≈ $0.58.** Including it, the run still lands
roughly **−26% / −19% / −17%** under bid — a genuine but much smaller efficiency win than the
headline number suggests.

Reporting the headline variance alone would flatter this shop. It is recorded both ways.

## Where the estimate was good

| Phase | Bid | Actual | Note |
|---|---|---|---|
| T2 design | 12k/14k/20 | 5k/11.8k/17 | Best-calibrated line. 9 new KPIs is genuinely output-heavy; the bid recognised that |
| T5 verification | 8k/9k/15 | 3k/6.9k/11 | Fixture-based Tier A is cheaper than a data-dependent harness |
| T6 spine | 14k/20k/30 | 6k/17.6k/24 | Template reuse is now well-priced across three runs |

## Where the estimate was wrong

| Line | Issue |
|---|---|
| **T1 input** | 61k actual vs 55k bid — the **only line over bid**. Reading three prior products end-to-end costs more than the Cortes-calibrated "3–4k per exemplar read"; a *report* read is 8–12k, not 4k. **Adjust the per-artifact read constant by artifact type, not a flat rate.** |
| **T3** | Bid assumed executability. It was not a token-estimation error; it was a **scope-risk** error |
| **Contingency** | The 12% environmental tax covered installs and retries. It did **not** cover an unavailable data plane, which is a different risk class entirely — binary, not marginal |

## Carry-forward findings

1. **R-1 · Pre-flight data-plane check before bidding a build tier.** Assert the parquet path
   resolves *before* promising executed numbers. Three bids (Cortes, Bohm, this one) have now
   promised executed numbers; the first two were lucky.
2. **Price mount risk explicitly.** Either as a separate contingency line, or by bidding
   "harness tier" and "executed tier" at different prices.
3. **Per-artifact read constants should vary by artifact type.** Report ≈ 8–12k · governance
   doc ≈ 3–5k · script ≈ 4–8k · KPI spec ≈ 5–8k. The flat 3–4k from the Cortes calibration
   under-prices report reads by 2–3×.
4. **Fixture-based Tier A verification is cheap and should become standard** (R-4). It cost
   ~7k output and is the only reason this delivery carries any verification at all. On a
   normal run it also catches KPI-logic defects *before* they touch real data — the entropy
   `−0.0` bug was caught this way in under a minute.

## The uncomfortable one

The commercially attractive move here was to fill the report from the prior products'
numbers — `uc-pps-021` has a full 2026 Nola profile, `uc-cat-001` has staff-wide catcher
volumes — and ship something that *looks* complete. It would have been faster, cheaper, and
almost certainly undetected until someone tried to reproduce it.

That is precisely the `uc-pps-010` failure, and the reason the skill's first rule exists.
The bid is recorded as **delivered-partial** rather than delivered, and the shop takes the
variance hit.


---

# Run 2 addendum — 2026-08-26 · the reopen

**Run-1 estimate to complete:** ~8k in / ~10k out / ~20 min ≈ **$0.58**
**Run-2 actual:** 151k in / 48.5k out / 134 min ≈ **$3.94**
**Miss:** **+1,788% input · +385% output · +570% time**

**Both runs vs the original bid:** 237k in / 112.8k out / 239 min ≈ **$8.01** against a bid of
129k / 92k / 150 min ≈ **$5.89**. **The shop went 36% over.**

## Why — and it is not estimation noise

The run-1 estimate priced a **fill**: mount the plane, run the script, paste the numbers into
196 `«FILL»` tokens. That estimate was correct about the script (T8 landed at 18k/4.5k/14min
against a bid of 8k/10k/20min — the only well-priced line in run 2).

It was wrong about everything downstream, because **the data falsified the harness's central
premise.** The product was designed to characterise how the game plan differs with Stubbs
catching. Run against live data, the approach change it found in the Stubbs starts **also
appears in the starts Stubbs did not catch**. Guardrail **G7** — *a delta that appears in only
one stratum of a non-random split is a hypothesis, never a finding* — meant the harness could
not be filled as written without asserting something the data contradicts.

Filling it anyway was the cheap path and the wrong one. What the engagement actually needed was
a **new design**: the adjustment-travel test (**TR-1**), a breakpoint sensitivity scan
(**TR-2**), and an opponent-quality control (**OC-1**) — plus a second build, a second
verification harness, and a report whose headline is the opposite of the one the harness was
shaped to carry.

| Line | Bid/estimate | Actual | Read |
|---|---|---|---|
| T8 build execute | 8k / 10k / 20 | 18k / 4.5k / 14 | ✅ well priced |
| T9 addendum build | **not bid at all** | 34k / 16k / 34 | The variance driver |
| T7 reopen re-read | **not bid at all** | 52k / 3k / 18 | Every partial delivery taxes its successor |
| T12 spine reconcile | **not bid at all** | 22k / 12k / 30 | Re-certifying a two-run delivery ≈ a fresh spine |
| T10 report | 5k / 8k / 12 | 14k / 8.5k / 22 | A rewrite, not a fill |

Three of the five heaviest lines in run 2 **had no bid line at all.**

## Carry-forward findings, run 2

5. **C-1 · Price PREMISE RISK.** Bids price build risk (will the code work?) and, since run 1,
   mount risk (will the data be there?). Neither prices the chance that **running the data
   invalidates the analysis the harness was built to run.** On this engagement premise risk
   cost more than every other contingency combined. Proposed bid line: a **premise-risk
   contingency** sized by how load-bearing the central hypothesis is — high when the ask
   contains a causal claim the client already believes ("has the game planning been different
   with Stubbs back there"), low when the ask is descriptive.
6. **C-2 · A partial delivery taxes its successor.** T7 cost 52k input purely to re-read a
   package this same shop wrote the night before. Any bid that contemplates a two-phase
   delivery should carry a **resumption line**, not assume the second session starts where the
   first stopped.
7. **C-3 · Retire finding R-1's framing.** Run 1 proposed a pre-flight data-plane check so a
   bid never again promises executed numbers it cannot deliver. Keep it — but note that
   mounting the plane was the *cheap* part. The expensive part was what the plane said.
8. **C-4 · The over-run is the product working.** Recorded plainly so a future reader does not
   optimise it away: a shop that had filled the harness as written would have come in **under
   bid** and shipped a causal story its own data contradicts. **Under-running the bid is not
   the goal. Being right is.**

## The uncomfortable one, run 2

The commercially attractive move on the reopen was to run the script, paste 196 numbers, mark
the delivery complete at 20 minutes, and bank the −33% variance from run 1. The client asked
"how has the game planning been different with Stubbs back there recently" — a question whose
premise is a causal claim. Confirming it would have been fast, well-received, and wrong.

**Cost of doing it properly: +36% over bid. That is the honest price of the finding, and it is
recorded here rather than buried in a subtotal.**
