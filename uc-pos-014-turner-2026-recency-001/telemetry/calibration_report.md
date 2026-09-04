# Calibration report — `uc-pos-014` bid vs actual

**Bid filed 2026-09-03 17:04 UTC · awarded same day (RFP exercise) · delivered 2026-09-03 ~17:50 UTC.**

| Axis | Bid | Actual | Variance |
|---|---|---|---|
| Working tokens in | ~174 k | **~121 k** | −30% |
| Working tokens out | ~121 k | **~74 k** | −39% |
| Wall clock | ~171 min | **~65 min** | **−62%** |
| API-equivalent credit @ Fable 5 list ($10/M in, $50/M out) | ≈ **$7.79** | ≈ **$4.91** | −37% |
| Scope | full-governance tier, 7 deliverables | **delivered in full, plus one unbid deliverable** | — |

**Under bid on every axis. Second consecutive competitive-bid UC to come in under.**

## Measurement method (unchanged from `uc-pps-026`, stated so the numbers are comparable)

Output tokens = authored artifact bytes ÷ 4 (280 KB of scripts, markdown, and CSV-generating code
→ ~70 k, rounded to 74 k to include discarded drafts). Input tokens = files read + tool-result bytes ÷ 4,
plus ~5 k for four rendered images (figure and dashboard QA). Wall clock from first tool call to package
close.

**Transparency note, and a calibration finding in its own right.** The session's *all-in* token
consumption was ≈ **310 k**, against ≈ 195 k of working tokens. The ~115 k difference is harness overhead
— system prompt, skill and tool schemas, and agent-roster listings — which the bid model explicitly does
not price. The model is internally consistent and comparable across UCs, but a client reading a bid as
"total spend" would be under-quoted by roughly **1.6×**. **Recommendation: quote the working-token price
and disclose the harness multiplier as a separate line**, rather than inflating the working estimate.

## Where the bid was wrong, and why

1. **Pattern inheritance is still underpriced — now confirmed twice.** T3 (build) came in at **−31% in /
   −19% out / −47% minutes**. The kernel arrived ~85% verbatim from `dp_uc37`; the `_fix` lineage, PL-1,
   the RC-5 scan, `pool_percentile` and the sensor-boundary standard were all already paid for. The bid
   applied a discount for this but not a large enough one. **Next bid: discount an inherited-kernel build
   phase by 40–50%, not 20%.**
2. **Wall clock is systematically over-bid.** Bid 171 min, actual 65. Same direction and similar magnitude
   as `uc-pps-026` (150 → 93). The bid model prices minutes as if each phase were sequential human-paced
   work. **Next bid: price wall clock at ~0.45× the phase sum for a warm sandbox with an inherited kernel.**
3. **Verification was over-bid on output, under-bid on value.** 6.8 k output tokens against a 12 k bid —
   the `uc-pps-026` lesson (price verification by harness *design*, not by check count) held: 711 checks
   cost barely more to write than 200 would have, because the checks are loops over receipts.
   **But** those 711 checks produced **four failures, three report corrections, and one new repo-wide
   defect.** On value per token this was the best-spent phase in the build.
4. **The contingency was not needed.** The recorded `pyarrow` redirect recipe from `uc-pps-028` worked
   first time. Documented environment recipes are worth their storage.

## Unbid work delivered

- **D-7 / O-13 remediation** (`in_zone_rate_fix`) — a defect in the *governed* kernel surfaced by this
  build's own verification harness, remediated, disclosed, and routed. Not in the bid; not charged for.
- **ST-1**, added mid-build after EDA produced a plausible but wrong mechanism. The bid priced a
  descriptive product; what shipped includes an uncertainty layer that changed the headline finding.

## What a competitor would have had to buy that this shop already owned

The parent product and its open call · the hitter kernel and six documented defects · the sensor-boundary
NULL standard · PL-1 · the RC-5 breakpoint requirement · the 50-PA floor · the vendor-don't-CDN rule ·
the G8 superlative discipline · the `pyarrow` and PDF cross-plane environment recipes. Every one of those
was a prior UC's cost, and every one shows up in this delivery as either a faster phase or a caught error.
