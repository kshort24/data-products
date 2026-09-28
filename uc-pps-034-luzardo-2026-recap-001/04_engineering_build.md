# 04 · Engineering Build: `uc-pps-034`

Agent: `data-engineer`

## 1 · Build manifest (MLB repo root)

| File | Role | Runs on |
|---|---|---|
| `dp_uc49_kernel.py` | governed kernel (imports `dp_uc48_kernel` → `dp_uc44_kernel`, sha256-pinned) | laptop VM |
| `dp_uc49_luzardo_recap.py` | the build: data plane → `out/dp_uc49_*` receipts + `headlines.json` | laptop VM (13–16 s) |
| `dp_uc49_build_figs.py` | 9 figures, PNG + JSON; asserts each subtitle; brand + palette checks | cloud (Chromium/kaleido) |
| `dp_uc49_build_dashboard.py` | narrative dashboard (repo copy + Artifact body variant) + HP receipt | cloud |
| `dp_uc49_build_pdf.py` | markdown → weasyprint (inherited from `dp_uc48_build_pdf.py`) | cloud (pango) |
| `dp_uc49_verification.py` | independent harness, 226 checks | laptop VM |

## 2 · Environment disclosure

- **Laptop VM:** Python 3.10, pandas 2.3.3, numpy 2.2.6, matplotlib 3.10. `/sessions` is 100% full (42 MB free), so `pyarrow 25.0.1`, `scipy` and `plotly 7.1.0` were installed with `pip --target /tmp/pyl` and `TMPDIR=/tmp/pt` (the default `TMPDIR` lives on the full volume). Run with `PYTHONPATH=/tmp/pyl`. **These installs vanish on VM restart**; re-run the two pip lines in `README.md`.
- **Cloud render:** Python 3.11, pandas 3.0.2, plotly + kaleido (Chromium 1194), weasyprint. Reads only the staged receipts.
- **Bridge findings (platform):** (a) committing the same staged path twice can deliver the first version; stage each revision under a new path. (b) Two tool calls issued in parallel (an edit and a commit) raced once; commits are now sequential. (c) A stale `__pycache__` served an old kernel once; runs use `PYTHONDONTWRITEBYTECODE=1`.
- One environment probe was written to the repo during setup and cannot be deleted without permission; it was renamed into the receipt set as `out/dp_uc49_env_write_probe.txt` (5 bytes).

## 3 · Build-time assertions (the build fails rather than publish)

| Assertion | Where |
|---|---|
| `dp_uc48_kernel` and `dp_uc44_kernel` sha256 match the pins | build §0 (`assert_lineage`) |
| regular-season anchor == 2026-09-26 | build §0 |
| DQ scorecard has 0 FAIL | build §14 |
| each figure's subtitle claim (ranks, counts, Game Score, changeup counts, walk expectation) | `build_figs` before each `ship` |
| brand checks (Arial, title, subtitle, axis titles, palette) on every figure | `build_figs.ship` |
| every figure the report references exists | `build_pdf.embed` |

## 4 · Receipts (`out/`)

63 files: 41 CSV (including `verification_log.csv`), 11 JSON (9 figures + `headlines.json` + `figure_specs.json`), 9 PNG, 2 TXT (palette validation, environment probe).
Key ones: `recap_governed.csv`, `recap_notebook.csv`, `source_receipt.csv`, `opponent_id_scan.csv`, `context_population.csv`, `context_starter_workloads.csv`, `command_ols.csv`, `house_percentiles.csv`, `starts_2026.csv`, `career_game_scores.csv`, `laborday_pitches.csv`, `postseason_ledger.csv`, `october_card.csv`, `hp_reconciliation.csv`, `bs1_bowlan_v3_resolution.csv`, `dq_scorecard.csv`, `verification_log.csv`, `headlines.json`.

## 5 · Reuse

- **Next recap is two calls:** `K.career_frame(pitcher_id, subject_file)` then `K.season_recap(frame)`. The queue in cell 118: Arraez, Nola, Painter, Wheeler.
- **OC-1 is subject-agnostic.** Any pitcher's October card is `october_card(outing_signatures(frame_2026))`.
- **The PA stepper and the chapter template** in `dp_uc49_build_dashboard.py` take any single game (`laborday_*` receipts are keyed by `game_pk`).
