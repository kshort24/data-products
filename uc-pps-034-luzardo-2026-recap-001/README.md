# The Chase — Jesús Luzardo 2026 Recap

**UC #49 · `uc-pps-034` · `dp_uc49` · v1.0.0 · delivered 2026-09-27 · READY-CONDITIONAL · independently verified (226/226)**
Phillies Pitching (`pps`) · Human DPO: Kellen Short

## Start here

| If you want | Open |
|---|---|
| the story, walked | `dp_uc49_luzardo_2026_dashboard.html` (MLB root, offline) or the published Artifact "Luzardo's 2026 Chase" |
| the story on paper | `dp_uc49_luzardo_2026_recap_report.pdf` |
| the one picture | `out/dp_uc49_fig1_the_chase.png` (or the notecard, `out/dp_uc49_fig9_notecard.png`) |
| Labor Day, pitch by pitch | dashboard chapter 6 (stepper), `out/dp_uc49_laborday_pitches.csv` |
| what "defining" means for October | dashboard chapter 8, report §8, `out/dp_uc49_october_card.csv` |
| which of your notebook claims held | report §9, `out/dp_uc49_hp_reconciliation.csv` |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the bid, and how it went | `BID_…md` → `07` §3 |

## The finding, in one paragraph

Luzardo stopped needing the strike zone. His in-zone rate fell from 50.5% to 46.5% (p = 0.002, lowest since 2021), his chase rate rose to a career-high 33.7%, and his walk rate held at 7.1% where a Phillies lefty at that zone rate would walk 9.2%. Among the 41 Phillies seasons with a starter's workload since 2015, his 31.9% whiff rate is **#1**, and no season beats it on both chase and whiff (#28 chase / #31 whiff across all 259 pitcher-seasons). The second half was a different pitcher (1.87 runs on watch per 27 outs, against 3.82 before the break). Labor Day was the best start of his career by Game Score (100; next best 86), his only 27-out game, with 28 of 61 out-of-zone pitches chased, 23 whiffs, and a faster four-seam in the ninth. Then the log goes quiet (IL 9/15, carry-in). The October card writes down, before any postseason pitch, what it would take for October to look like this season, and prints its own backtest so nobody mistakes it for a prediction.

## Package contents

```
00_dpo_orchestration_record.md   the spine: framing, 12 gates, capability table, arguments, 8 escalations, C1–C6
01_strategy_intake.md            ID reservation, 7 gaps, source profile (21-file id scan, O-26, BS-1), carry-ins
02_engineering_design.md         one frame / many groupbys, device-first build, 8 EDA findings, metadata map, dashboard spec
03_governance.md                 Rule-1 search, glossary, KPI specs (CF-2 … OC-1, PL-1), lineage, defects, privacy, versioning
04_engineering_build.md          manifest, environment disclosure, build-time assertions, receipts, reuse
05_quality_certification.md      DQ 21/2/0, brand 9/9, palette, harness 226/226, what the build caught
06_consumer_success.md           the product forms and their readers, reading paths, walkthrough, FAQ, catalog entry
07_platform_marketing.md         tripwires, cost audit, bid vs actual, calibration C-1…C-6, what's next
BID_2026-09-27_…md               the competitive bid: filed, awarded, reconciled in 07
uc-pps-034-Jesus Luzardo 2026 Recap 20260927.md            repo-side contract (copy; the original is at the MLB root)
uc_ledger_AI_PATCH_uc-pps-034-luzardo-2026-recap.md        PENDING PASTE
```

**Data plane (MLB repo root):** `dp_uc49_kernel.py` · `dp_uc49_luzardo_recap.py` · `dp_uc49_build_figs.py` · `dp_uc49_build_dashboard.py` · `dp_uc49_build_pdf.py` · `dp_uc49_verification.py` · `dp_uc49_luzardo_2026_recap_report.md/.pdf` · `dp_uc49_luzardo_2026_dashboard.html` (+ `_artifact.html`) · `out/dp_uc49_*` (63 files).

## Governed objects: inherited vs introduced

**Inherited by import (sha256-pinned):** `dp_uc48_kernel` (SR-1 `season_recap` **second use**, `runs_created`, `xwobacon`, AR-2, CS-1, KP-1, `rv100`) → `dp_uc44_kernel` (`nresults`, `whiff_rate`, `chase_rate`, `pitch_mix`, `fpsr`, `two_prop_z`, PM-1).
**Inherited by receipt:** `uc-pps-017` first-half figures (reproduced 4/4) and its sweeper-first finding.
**Generalized (non-breaking):** CF-2 (from CF-1), LP-1, KP-1b, US-1b (ENV-1 fix).
**Introduced (provisional):** CX-1/1b context and starter cut · GS-1 Game Score (log-derived) · OU-1 outs · VB-1 first-15 velocity · OC-1 October card · NF-1 `nphl` reproduction · BN-1 batter names · PL-1 pitch palette.

## Reproducing this

```bash
# laptop VM (the /sessions volume is full): install to /tmp once per VM session
TMPDIR=/tmp/pt python3 -m pip install --no-cache-dir --target /tmp/pyl pyarrow scipy plotly
cd "<MLB repo>"
PYTHONPATH=/tmp/pyl PYTHONDONTWRITEBYTECODE=1 MLB_DATA_ROOT="$PWD" python3 dp_uc49_luzardo_recap.py     # 21 PASS / 2 WARN / 0 FAIL
# render (needs Chromium for kaleido and pango for weasyprint)
python3 dp_uc49_build_figs.py && python3 dp_uc49_build_dashboard.py && python3 dp_uc49_build_pdf.py
PYTHONPATH=/tmp/pyl MLB_DATA_ROOT="$PWD" python3 dp_uc49_verification.py                                  # 226/226 expected
```

The build refuses to run unless the regular-season log ends 2026-09-26. Game 162 or a postseason pitch is v1.1.0, not a correction.

## Defects found by building

- **O-26** `get_nphillies_data()` de-duplicates across opponent files `keep='first'` in file-name order, so a pitch that also sits in an earlier batter-keyed pull survives with the *batter's* name. `nphl[nphl.player_name == 'Luzardo, Jesús']` silently loses 230 regular-season pitches.
- **BS-1** A byte search is not a source profiler (2 files found vs 21 by id). The back-check **closes uc-pps-033 V-3**: Bowlan's notebook ".269 / 60 G" is one Lehigh Valley outing (2026-04-26) entering through `lhvp26.parquet`.
- **ENV-1** `dp_uc48_kernel` US-1 groups by `game_pk` twice; pandas 2.3 raises.
- **E-7** `dp_uc44_kernel` PM-1's docstring has the `plate_x` sign backwards (+ is the first-base side).
- **HP-10** `px.scatter(trendline='ols', color=…)` fits one line per color group, including a line through the highlighted player's own points.
