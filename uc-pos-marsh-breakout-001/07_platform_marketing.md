# 07 — Platform & Marketing · uc-pos-marsh-breakout-001

## version-controller

`v1.0.0` — first release, 2026-07-13 (window through 2026-07-11; receipts `out/marsh_breakout_*.csv`, retained per new-files-only rule).
`v1.1.0` — **current**, 2026-07-13: refreshed to the complete first half (through 2026-07-12, +1 game), receipts re-emitted under repo-aligned prefix `out/dp_uc18_marsh_breakout_*.csv`, runtime deliverables added at MLB repo root (`dp_uc18_marsh_breakout.py`, `_report.md`, `_report.pdf` — Phillies-branded weasyprint per uc-pps house pipeline). Non-breaking: same schema; headline shifted .304→.301 BA, wOBA .358→.354. Planned `v1.2.0` (non-breaking) after season end: full-2026 window, monthly table extends. A change to PD-2 (pull threshold) after ratification would be **breaking** for `_spray_by_season.csv` consumers — requires DPO acknowledgment per guardrail #4.

## data-observability runbook

- **Freshness:** product is point-in-time (All-Star break). If quoted after 2026-07-11, staleness must be stated. Refresh = re-run script.
- **Schema drift:** upstream parquet layer is `mlb_data.py`-owned; if Statcast renames `estimated_woba_using_speedangle` or hit-coordinate fields, the script fails loudly (no silent nulls) — acceptable for a batch product.
- **Volume anomaly:** expected row count grows only via 2026-2H games (~40/game-week); any drop below 9,864 on re-run indicates cache regression.

## dashboard-specifier (deferred)

Not commissioned for v1. If requested: 4-panel spec — (1) season OPS/wOBA bars with 2026-1H highlight, (2) swing/chase/funnel line trio, (3) spray pull-air trend, (4) platoon exposure × production scatter. Filters: season, p_throws, count_state.

## Ledger & cross-plane

Runtime patch filed: `MLB/uc_ledger_AI_PATCH_uc-pos-marsh-breakout-001.md` (claims UC #18, advances header to UC #19). Control-plane home: this folder. Crosswalk rule (2026-07-02) satisfied.
