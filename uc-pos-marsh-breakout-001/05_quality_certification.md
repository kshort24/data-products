# 05 — Quality & Certification · uc-pos-marsh-breakout-001

## data-quality-engineer — scorecard (from `marsh_breakout_dq_receipts.csv`)

| Check | Result | Class |
|---|---|---|
| Duplicate pitch keys after concat | 0 / 9,864 | PASS |
| Null zone | 0.04% | PASS |
| Null launch_speed on BIP | 0.20% | PASS |
| Null hit coords on BIP | 0.07% | PASS |
| Null xwOBA-proxy on BIP | 0.47% | PASS |
| wOBA weight join nulls | 0 | PASS |
| Season sample floors (50 PA) | min season = 260 PA | PASS |
| July 2026 split | 40 PA | WARNING — flagged in report §7 / PD-4 |

## Independent verification (certification-agent)

Headline numbers recomputed from raw event counts, independent of the build kernel: PA 359 ✓ · AB 336, H 102 → BA .304 ✓ · HR 15 ✓ · BB 17 (+1 IBB, excluded per locked mechanics) ✓ · direct-weight wOBA .358 ✓ · Marsh appeared in 90 of the team's 96 regular-season games ✓ · 2022 era split LAA 1,268 / PHI 539 pitch rows ✓.

Claim-trace audit: every quantitative claim in report §1–§7 traces to a named CSV; §6 persona narrative contains no quantitative claim not present in §1–§5 and is labeled as inference.

**Certification status: READY** (conditional on PD-1..PD-4 ratification; none blocking).

## data-observability / version-controller / cost-watchdog (post-publish notes)

- **Refresh trigger:** re-run script after 2026 season end for the full-season update; monthly table will silently extend — no schema change (non-breaking).
- **Drift watch:** if `wOBA and FIP Constants.csv` 2026 row is revised by FanGraphs, results shift at the 3rd decimal; re-run and re-stamp.
- **Cost:** single-entity parquet scans, <10s runtime, no recompute waste. No findings.
