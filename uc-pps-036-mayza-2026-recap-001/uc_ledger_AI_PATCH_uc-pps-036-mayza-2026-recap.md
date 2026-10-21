# Ledger patch: UC #52 / uc-pps-036 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line.

| 52 | `uc-pps-036` | **Tim Mayza 2026 season recap: "The Sheriff of the Phillies Bullpen"** (2026-10-14) | Delivered · READY-CONDITIONAL (C1–C5) · verified 74/74 · DQ 12/0/0 | `dp_uc52_*` + `uc-pps-036-Tim Mayza 2026 Recap 20261014.md`; primary consumables `dp_uc52_mayza_2026_recap_report.pdf` and `dp_uc52_mayza_2026_dashboard.html` (Artifact "The Sheriff of the Phillies Bullpen"); trail at `Agents for Data Products/data-products/uc-pps-036-mayza-2026-recap-001/`. First UC run with the `uc-house-format` skill (audit Phase 2); first shared narrative module; first reliever recap since UC48 |

Pattern inheritance additions (UC52): Season recap UC48 SR-1 → UC49 → UC51 → **UC52** · Career frame CF-2b (UC51) → **CF-2c (EN-2 extra columns)** · Inheritance by extraction IX-1 (UC51) → **UC52 (second use; ratify)** · New, provisional: **QA-1** quick-AB rate, **BS-1** bullet slider, **DS-1** delivery distance, **RP-1** reliever role · Basis companion **WB-1** (Statcast-basis wOBA beside XW-1)

Next available: **UC #53 / dp_uc53** (pps next `uc-pps-037` · pos next `uc-pos-019`) — as of 2026-10-14.

## Findings worth carrying
1. **WB-1:** house `nresults` wOBA (FanGraphs weights, errors as outs, every PA) and Statcast-basis wOBA differ by about .014 for this pitcher. Never set xwOBA beside `nresults` wOBA. Back-check UC48/49/51.
2. **HX-1:** `nphl_name_frame` (NF-1) drops `launch_speed_angle`; client-frame barrel rates are wrong for non-Phillies years.
3. **EN-2:** CF-2 projects no release point, spin axis, launch_speed_angle or woba_value. CF-2c joins them by pitch key.
4. **DEF-1:** `strikes` is the pre-pitch count. Any "two strikes within N pitches" rule must read the next pitch's count.
5. **RQ-2:** a `<` in published text opens a phantom HTML tag and silently drops the rest of a weasyprint PDF. `build_pdf` now asserts every section survives.
6. **RQ-1:** kaleido 0.2.1 + plotly 6 collapses string-category x on scatter traces; use numeric x.
7. **Root `pp26.csv` is stale** (through 2026-04-14). Never read it for 2026.

## Repo-side artefacts to file
- `uc-pps-036-Tim Mayza 2026 Recap 20261014.md` → MLB repo root (**filed**)
- `dp_uc52_*.py` / `.md` / `.pdf` / `.html` → MLB repo root (**filed**)
- `out/dp_uc52_*` → MLB repo `out/` (**filed**, 42 files)
