# 07 — Platform & Marketing · uc-pps-017 (UC #19)

## data-observability

- **Freshness rule:** product is valid while `phils_2026.parquet` max game_date ≥ Luzardo's most recent start. Current: cache 2026-07-12, last start 2026-07-09 → healthy.
- **Drift watches for refresh runs:** (a) `n_thruorder_pitcher` or `fielder_2` null-rate rising above 0 (both 1.000 now); (b) a fifth pitch_name appearing (arsenal change → fig 1 layout + PD specs unaffected but report narrative stale); (c) events completeness drifting from ~0.25 (schema change signal).
- **Runbook:** on failure, stop and report — never backfill numbers outside the build script (UC-PPS-010 lesson).

## cost-watchdog

- Two parquet reads + one full-staff read per run; seconds of compute, ~16 small receipt files. No hotspots. Recommendation: none — do not optimize.

## version-controller / comms

- v1.0.0 published internal 2026-07-13. Suggested consumer note: "First-half Luzardo All-Star assessment available; RA9/FIP are reconstructions, official ERA not included; refresh scheduled post-break."
- Ledger: patch file at MLB root advances header to UC #20 (next pps: uc-pps-018); skill-side ledger update pending paste (known drift, flagged in 00).
