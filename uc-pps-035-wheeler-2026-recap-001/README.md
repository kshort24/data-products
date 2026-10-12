# Still Zack Wheeler — 2026 Recap

**UC #51 · `uc-pps-035` · `dp_uc51` · v1.0.0 · delivered 2026-10-12 · READY-CONDITIONAL · independently verified (204/204)**
Phillies Pitching (`pps`) · Human DPO: Kellen Short

## Start here

| If you want | Open |
|---|---|
| the story on paper | `dp_uc51_wheeler_2026_recap_report.pdf` (this folder; also at the MLB root) |
| the story, walked | `dp_uc51_wheeler_2026_dashboard.html` (offline) or the published Artifact "Still Zack Wheeler" |
| the one picture | `out/dp_uc51_fig13_notecard.png` |
| the six-start slide | dashboard ch. 4 (start drill), report §4, `out/dp_uc51_stretch_windows.csv` |
| what 2027 has to look like | dashboard ch. 8, report §8, `out/dp_uc51_still_wheeler_card.csv` |
| which of your notebook claims held | report §9, `out/dp_uc51_hp_reconciliation.csv` |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the bid, and how it went | `BID_…md` → `07` §3 |

## The finding, in one paragraph

He is still Zack Wheeler. His .263 xwOBA (your Savant number exactly) is #6 of 41 Phillies seasons with a starter's workload since 2015, and six of the top ten are his. The walk rate (7.3%, a Phillies-tenure high) is one six-start slide: from 7/27 to 8/24 he walked 13.4% of hitters against 5.9% the rest of the year (p = .004), and that window is the only one that reproduces the reported 8.51 ERA. During it his clear misses drifted to the arm side (25.5% vs 17.8%) while his four-seam release point did not move; the reported cause, a dropped glove, is not something the log can see. He finished with six starts of 6.2% walks and 1.67 runs per 27 outs. The bigger change was the zone: the fewest pitches in it of his Phillies years (42.1%) and the most chases (36.2%), with the splitter now his second pitch. Contact quality was noise, as the notebook said, and lefties did the damage. The slowing is across years (97.2 mph in 2021, 95.2 now). A 2027 card, written before any 2027 pitch, says what still being this pitcher has to look like.

## Package contents

```
00_dpo_orchestration_record.md   the spine: framing, 12 gates, capability table, arguments, 8 escalations, C1–C6
01_strategy_intake.md            ID reservation, 8 gaps, source profile (24-file id scan, MI-1, NM-1), carry-ins
02_engineering_design.md         one frame + the defensive log, 9 EDA findings, metadata map, dashboard spec
03_governance.md                 Rule-1 search, glossary, KPI specs (CF-2b, IX-1, OU-2, GS-1b, ST-1, NC-1, MX-1, SR-2), lineage, defects, privacy
04_engineering_build.md          manifest, environment, build-time assertions, receipts, reuse
05_quality_certification.md      DQ 26/4/0, brand 13/13, palette, harness 204/204, what the build caught
06_consumer_success.md           product forms and readers, reading paths, walkthrough, card guide, FAQ, catalog entry
07_platform_marketing.md         tripwires, cost audit, bid vs actual, calibration C-1…C-8, what's next
BID_2026-10-12_…md               the competitive bid: filed, awarded, reconciled in 07
dp_uc51_wheeler_2026_recap_report.md / .pdf      the feature report (delivered copy)
dp_uc51_wheeler_2026_dashboard.html              the narrative dashboard, offline (delivered copy)
code/                            dp_uc51_*.py — kernel, build, figures, dashboard, report, PDF, client grading, harness
out/                             dp_uc51_* — 70 receipts: CSV, JSON, 13 PNG figures, DQ scorecard, verification log
uc-pps-035-Zack Wheeler 2026 Recap 20261012.md   repo-side contract (copy; the original is at the MLB root)
uc_ledger_AI_PATCH_uc-pps-035-wheeler-2026-recap.md   PENDING PASTE
```

**Data plane (MLB repo root):** the same `dp_uc51_*.py`, report, dashboard (+ `_artifact.html`) and `out/dp_uc51_*`. The code in `code/` is a copy; run it from the MLB root, where the data lives.

## Governed objects: inherited vs introduced

**Inherited by import (sha256-pinned):** `dp_uc49_kernel` (CF-2, US-1b, GS-1, VB-1, OC-1, CX-1, KP-1b, BN-1) → `dp_uc48_kernel` (SR-1, `runs_created`, `xwobacon`, AR-2, KP-1) → `dp_uc44_kernel` (`nresults`, whiff, chase, hard-hit, LD, PM-1, `two_prop_z`); `dp_uc50_kernel` (XW-1 xwOBA) → `barrel_rate.py`.
**Inherited by source-pinned extraction (IX-1):** ER-1 `edge_rate` (UC8), JR-1 `jam_rate` (house library, 10/9), RCI `release_consistency` (UC28).
**Inherited by receipt:** `uc-pps-020` first-half figures (reproduced 6/6).
**Second use (ratify):** OC-1, as the 2027 Still-Wheeler card.
**Generalized (non-breaking):** CF-2b (MLB-only, subject name, enrichment).
**Introduced (provisional):** OU-2 outs · GS-1b · ST-1 swing timing · NC-1 clear miss · MX-1 release by start · SR-2 window by reconciliation · IX-1 extraction · PL-2 six-pitch palette.

## Reproducing this

```bash
# laptop VM (the /sessions volume is full): install to /tmp once per VM session
TMPDIR=/tmp/pt python3 -m pip install --no-cache-dir --target /tmp/pyl pyarrow scipy
cd "<MLB repo>"
PYTHONPATH=/tmp/pyl PYTHONDONTWRITEBYTECODE=1 MLB_DATA_ROOT="$PWD" python3 dp_uc51_wheeler_recap.py     # 26 PASS / 4 WARN / 0 FAIL
# render (needs plotly + kaleido for PNG and pango for weasyprint)
python3 dp_uc51_build_figs.py && python3 dp_uc51_build_dashboard.py && python3 dp_uc51_build_report.py && python3 dp_uc51_build_pdf.py
PYTHONPATH=/tmp/pyl MLB_DATA_ROOT="$PWD" python3 dp_uc51_verification.py                                   # 204/204 expected
```

The build refuses to run unless the regular-season log ends 2026-09-27 and every pinned module and extracted segment matches its hash. A 2027 pitch is v1.1.0, not a correction.

## Defects found by building

- **MI-1** CF-2 admits any opponent file holding the pitcher's id; `lhvp26.parquet` tags 148 Lehigh Valley rehab pitches as regular season. They would have entered his 2026 rates.
- **NM-1** CF-2 stamps UC49's subject name ("Luzardo, Jesús") on every frame it builds.
- **OU1-1** OU-1's event map misses base-running outs: 480 vs the published 486 outs. OU-2 reads the outs sequence and matches.
- **SJ-1** (build-caught by the harness) the sinker tied-up count included a foul bunt; fixed to JR-1's swing list.
- **HP-13** the notebook's jam-rate population pools `player_name` across `pos` and `pps`, so 33 of 186 points are hitters, not pitchers.
