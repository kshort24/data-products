# 06 — Consumer Success
## uc-pps-019 · analytics-enabler + consumer-onboarding

## How to read this product, by persona

**Pitching department (primary consumer).** Your tempo metric has a first governed baseline: QR-1 = 50.3% (2026 H1) vs 52.2% (2025), staff median 42.6%. Track it from `out/dp_uc21_sanchez_qr_yoy.csv`; the quality companion (`_qr_quality_yoy.csv`) is the one to watch — quick-PA wOBA .342 with 10/12 HR is the actionable cell. Re-run cadence suggestion: monthly, or per 5 starts.

**Manager.** §2 monthly table + fig 2 for leash context; TTO receipt shows no through-the-order alarm. The KC start is quarantined as an outlier in the log — one start, 23% of season runs.

**Catcher.** §5 battery split is directional (Marchán 71 PA, Stubbs 30 PA) — use it as a conversation starter on sequencing, not a scorecard. The two-putaway mix (SL 31.0%, CH 29.2%) is the concrete sequencing fact.

**Sánchez.** §3 arsenal table: the slider gains are real and quantified; the sinker-to-RHB early-count cell is the second-half homework.

## Query patterns
All receipts are flat CSVs in `<MLB repo>/out/` prefixed `dp_uc21_`. Rebuild: run `dp_uc21_sanchez_first_half.py` (env `MLB_DATA_ROOT` optional). Verify: `dp_uc21_verification.py`.

## FAQ
- **Why doesn't RA9 match his ERA on Baseball-Reference?** RA9 counts all runs while on the mound from score deltas; no earned/unearned split, bequeathed-runner distortion possible. Trend-valid, not bookkeeping-valid.
- **Is the 50.2 IP record confirmed here?** No — SL-1 computes 51.2 IP by event-out method (window 4/30–6/3), which is *consistent with* the official 50.2; record adjudication is MLB's.
- **Why is QR-1 "provisional"?** First governed use. Ratify the 02 spec to promote it; changing the formula afterward is a breaking change (03 §D).
