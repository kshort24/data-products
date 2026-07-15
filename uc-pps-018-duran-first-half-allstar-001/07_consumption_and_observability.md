# 07 — Consumption & Observability · uc-pps-018

## How to use this product (analytics-enabler)
- **Start with the PDF** (`dp_uc19_duran_first_half_report.pdf`) — bottom line first; every number's denominator is printed where samples are small.
- **To re-query:** load receipts from `out/dp_uc19_*.csv` — era grain for trends, era×pitch for arsenal, stand×pitch for platoon plans, month for 2026 texture. All rates ride the locked dp_uc11 KPI definitions; do not recompute them with different formulas.
- **Do not** quote save-situation splits from this product — none exist (saves are a carry-in fact, by design).

## Persona quick-reads (consumer-onboarding)
- **Manager:** report §watch-list item 1 (role/load) and §month-by-month.
- **Pitching department:** §arsenal redesign + §new looks; the actionable lever is splitter-vs-LHB (.369 xwOBA) → changeup share.
- **Battery:** §platoon plans + the attack-rule table; FPSR is your early-warning gauge.
- **Front office / content (Kellen's video work):** §bottom line + fig `dp_uc19_arsenal_evolution.png` is the shareable "what changed" visual.

## Observability & refresh (data-observability)
- **Freshness:** product is frozen at cache 2026-07-12. Re-run `dp_uc19_duran_first_half.py` after any `phils_2026` cache refresh — receipts regenerate in place (dp_uc19 namespace only).
- **Drift triggers for a second-half refresh or new UC:** FPSR < 52% over any 15-appearance window; BB% > 8%; splitter-vs-LHB xwOBA still > .350 at 40+ BIP; any new pitch classification appearing in the log.
- **Schema watch:** if Statcast renames estimated_* fields or pitch_name labels (e.g., Split-Finger reclassification), the build fails loudly at the coerce/groupby step — fix the loader, not the KPIs.

## Closure step (offered, standard for the pps pattern)
End-of-season backtest: re-run the era comparison with the full 2026 season and check whether the first-half process gains (whiff, putaway, out-of-zone approach) held; reconcile the carry-in save total against the final official number.
