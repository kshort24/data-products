# 07 · Platform & Marketing — `uc-pps-029-game2-bullpen-script-001`

**UC #43 · `uc-pps-029` · `dp_uc43` · v1.0.0**
**Agents:** `data-observability`, `cost-watchdog`, `token-economist`, `version-controller`

## 1 · Monitors / tripwires

| ID | Watches | Fires when | Then |
|---|---|---|---|
| **BP-1** | the anchor game | `phils_2026.parquet` gains a game after 2026-09-11 | Every availability figure in this package is stale. Re-run; do not patch. A refreshed run is a new game. |
| **BP-2** | D-8 upstream | `appearance_summary(...).is_start.isna().sum() == 0` | The governed kernel has been fixed. Drop the build-local `.fillna(False)` and re-verify family D. |
| **BP-3** | D-9 upstream | `nresults(['batter'], df)` stops raising | Drop the `batter_id` alias. |
| **BP-4** | Holman | his first MLB pitch appears in `phils_2026.parquet` | The supporting tier stops being the only evidence. Re-run §7 of the report against MLB data and compare — the first real test of whether the AAA mix and shape travelled. |
| **BP-5** | the opponent inference | any source confirms or refutes MLBAM 641816 = Mahle | Either clear the DQ WARN or rewrite §8. |
| **BP-6** | BS-1 ratification | a second UC reuses `bullpen_availability_tier` | Compare its tier calls against that build's independent read before promoting to APPROVED. |
| **BP-7** | the 37-BF benchmark | season ends, or the club changes | Re-derive. It is club- and season-specific and it is the denominator of the whole finding. |

**Closure step offered, not delivered:** the post-game backtest — scripted innings vs. actual innings, scripted
arms vs. actual arms, BS-1 tiers vs. who Thomson actually used. That is the cheapest possible validation of
BS-1 and it is the natural next UC.

## 2 · Cost / efficiency audit (`cost-watchdog`)

| Line | Finding |
|---|---|
| **Biggest cost avoided** | Requesting data-plane folder access as the first action of intake. Without it the build has no data at all — the control plane contains no parquet. One tool call, whole engagement. |
| **Second biggest** | Verbatim kernel transcription. Sections A and B of `dp_uc43_kernel.py` are ~250 lines that would otherwise have been re-derived and, being re-derived, would have quietly disagreed with the notebook. Cost: one read of each notebook. |
| **Wasted** | ~6k tokens on three rounds of matplotlib label-collision fixes across figures 2–4, and ~4k on a `to_json` epoch-date serialisation round-trip. Both are avoidable: the figure lesson is to size the annotation gutter before plotting; the JSON lesson is to cast date columns to ISO strings once, at the payload boundary. |
| **Also wasted** | One build cycle on the D+1/D+2 ambiguity before deciding to ship both. Cheaper to have decided to ship both at intake — the ambiguity was visible in the first five minutes. |
| **Storage** | 43 receipts, ~2.9 MB. The largest is the 348-row Holman pitch extract (~60 KB) and the payload (~530 KB). Both earn their place: the extract is what makes the pitch map reproducible, the payload is what makes the dashboard self-contained. |
| **Efficiency win worth reusing** | Two capacity modes cost ~3k tokens and replaced a headline that was true but overstated. Best return in the build. |

## 3 · Bid vs. actual (`token-economist`)

Bid: `BID_2026-09-13_uc-pps-029-game2-bullpen-script.md` — **~201k in / ~112k out / ~2 h 31 m ≈ $7.61**.

| Axis | Bid | Actual | Variance |
|---|---|---|---|
| Wall clock | ~2 h 31 m | **~48 min** to certification | **−68%** |
| Session token consumption (gross, all turns) | — | **~430 k** measured at end of build | — |
| Tokens in (bid basis: unique input) | ~201 k | **~165 k** est. | −18% |
| Tokens out (bid basis) | ~112 k | **~118 k** est. | +5% |
| Credit equivalent | ~$7.61 | **≈ $7.55** | −1% |

**Measurement caveat, stated rather than buried.** The bid is denominated in *unique* input tokens, following
the `uc-pos-014`/`uc-pos-016` basis. This session's instrument reports *gross* consumption, which includes
re-sent conversation context on every turn and is therefore several times larger. The two are not the same
quantity and the reconciliation above converts between them by estimate, not by measurement. Until the repo
adopts one denominator, every bid-vs-actual in this series carries this ambiguity. **Recommendation: fix the
denominator to gross session consumption in the next bid**, since that is the number the instrument actually
produces, and re-baseline the historical bids against it.

### Where the variance came from

- **Under on time (−68%).** Three drivers: egress was open (no `pq_reader` fallback, no reportlab
  substitution, weasyprint installed in one call); the bullpen kernel already existed and was inherited whole;
  and the D-8 failure surfaced on the *first* run rather than after a plausible-looking wrong answer had been
  built on top of it. The build asserted `len(season) > 0` and stopped.
- **Slightly over on output (+5%).** Two things the bid did not price: the second capacity mode (a design
  change forced by EDA, ~3k) and the governance write-up of two newly-found defects (~5k). Finding defects is
  not free, and neither of the two prior competitive bids had to price it.
- **The contingency was mispriced in both directions.** 15% was loaded for the device bridge and egress. The
  bridge did fail (as bid); egress did **not** (unlike the last two sessions). Net: the contingency roughly
  paid for the figure-layout churn instead of what it was bought for.

## 4 · Calibration findings

| ID | Finding |
|---|---|
| **C-2** | **Bid the subject count, not the subject.** This UC had nine subjects plus an unnamed opponent; the two prior competitive bids had one each. The 175k-in subtotal was built by loading a single-subject analogue and scaling by judgment, and it came in 18% high — but the *output* side, which scales with the number of things that have to be written about, came in over. Next multi-subject bid: scale input sub-linearly and output roughly linearly with subject count. |
| **C-3** | **Price a defect-discovery line.** Two repo-wide defects were found and each cost roughly 2.5k output tokens to characterise, reproduce as a live assertion, and write up. Builds that transcribe a governed kernel verbatim should expect to find things; that is most of why the transcription rule exists. Add a line item. |
| **C-4** | **Environmental contingency should be split, not pooled.** Bridge failure and egress lockout are independent and have different costs. Pooling them at 15% meant the bid could not be right: it over-priced the session where only one fired. Price them separately at ~8% and ~10%. |
| **C-5** | **A plan-shaped ask is cheaper than a question-shaped ask, and more valuable.** The client handed over a finished script. Testing a stated plan is mechanically cheaper than open-ended analysis — the hypotheses are given — and the findings are sharper because they are falsifications rather than descriptions. Two of three stated premises failed. Future intake should notice when an ask is plan-shaped and bid it lower. |

## 5 · Publication

| Surface | Status |
|---|---|
| Repo package (`data-products/uc-pps-029-game2-bullpen-script-001/`) | **the certified copy** |
| PDF report | delivered to the client in-session and committed to the repo |
| Interactive dashboard | committed to the repo; also published as a hosted artifact for convenience. **The repo copy is the certified one**; the hosted page is a mirror of this build and will drift on any rebuild. |
| Ledger patch | `uc_ledger_AI_PATCH_uc-pps-029-game2-bullpen-script.md` — **pending paste** into `uc_ledger_AI.md` |
| External / public | not requested, not blocked (privacy LOW) |
