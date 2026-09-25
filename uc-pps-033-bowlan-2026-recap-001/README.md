# The Tick and a Half — Jonathan Bowlan 2026 Recap

**UC #48 · `uc-pps-033` · `dp_uc48` · v1.0.0 · delivered 2026-09-25 · READY-CONDITIONAL · independently verified (153/153)**
Phillies Pitching (`pps`) · Human DPO: Kellen Short

## Start here

| If you want | Open |
|---|---|
| to explore the season | `dp_uc48_bowlan_2026_dashboard.html` (offline; pick a role under **Read as**) |
| the story on paper | `dp_uc48_bowlan_2026_recap_report.pdf` |
| the one picture | `out/dp_uc48_fig1_archetype_flip.png` |
| which of your notebook claims held | report §8, or the dashboard's *Your notebook, graded* |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the decisions that are yours | `00` §7 |
| the bid, and how it went | `BID_…md` → `07` §3 |

## The finding, in one paragraph

Kansas City had a four-seam with plus ride (grade 60) and elite whiff (80), hidden behind a .302 wOBA. A velocity grade of 50 held its shape axis to 55, so uc-pps-032 had it RESULTS-ONLY, #20 of 405. In Philadelphia it came out **1.51 mph harder (95.5 → 97.0) from the first pitch of every outing** (95.2 → 96.7 on pitches 1–10, so the gain is arm, not role). The ride held (17.7 → 18.0 in), the velocity grade moved to 60, and the pitch became **ELITE, #2 of 405**. The arsenal was rebuilt by platoon (four-seam + changeup 58% → 82% vs lefties; a new sweeper for righties). The four-seam became the answer at two strikes (35% → 52%) and when behind (33% → 52%), both p < .01. He got one late inning, 59 times. K rate rose to 31.5% (**92nd percentile** of 198 Phillies pitcher-seasons, second on the staff to Duran) and BB rate fell to 6.5%. On one season of relief PA those two changes are directional, not settled. Watch the sinker (whiff .176 → .055) and the unproven sweeper. The log shows no velocity warning before the 9/17 exit, which was reported as a right groin strain with no IL stint (a carry-in).

## Package contents

```
00_dpo_orchestration_record.md   the spine: framing, 11 gates, capability table, arguments, 6 escalations, C1–C6
01_strategy_intake.md            ID reservation, 6 gaps, source profile, entity lock, 22 claims, carry-ins
02_engineering_design.md         one frame / many groupbys, 8 EDA findings, metadata map, dashboard spec
03_governance.md                 Rule-1 search, glossary, 8 KPI specs (incl. PA-1 decision rule), lineage, defects
04_engineering_build.md          manifest, environment disclosure, build-time assertions, receipts, reuse
05_quality_certification.md      DQ 16/3/0, brand 58/0, harness 153/153, what the build caught
06_consumer_success.md           persona reading paths, dashboard walkthrough, FAQ, catalog entry
07_platform_marketing.md         5 tripwires, cost audit, bid vs actual, 5 calibration findings, what's next
BID_2026-09-24_…md               the competitive bid: filed, awarded, reconciled in 07
dp_uc48_kernel.py                A (import, sha-pinned) · A2 (verbatim) · C: CF-1 SR-1 KP-1 AR-2 CS-1 US-1 VE-1 PA-1
dp_uc48_bowlan_recap.py          the build
dp_uc48_build_figs.py            11 figures, each asserting its subtitle; brand-center compliance
dp_uc48_build_dashboard.py       the narrative dashboard (repo copy + Artifact body variant)
dp_uc48_build_pdf.py             markdown → weasyprint
dp_uc48_verification.py          6 families, 153 checks
dp_uc48_bowlan_2026_recap_report.md / .pdf
dp_uc48_bowlan_2026_dashboard.html
out/                             29 CSV, 13 JSON, 11 PNG, 1 TXT
uc-pps-033-Jonathan Bowlan 2026 Recap 20260924.md          repo-side contract
uc_ledger_AI_PATCH_uc-pps-033-bowlan-2026-recap.md         PENDING PASTE
```

## Governed objects: inherited vs introduced

**Inherited (by import, sha256-pinned):** `dp_uc44_kernel`: `nresults`, `whiff_rate`, `chase_rate`, `pitch_mix`, `fpsr`, `two_prop_z`, `load_phils`, `apply_woba_weights`.
**Inherited (verbatim):** `runs_created` (Baseball Functions cell 31; approved, uc-pos-012), `GROUP_MAP` (September 2026 cell 5), `xwobacon` (uc-pps-021 O1).
**Inherited (receipt, read-only):** uc-pps-032 four-seam grades. **Second use:** RV/100 (ratification recommended).
**Introduced (provisional):** CF-1 `career_frame` · SR-1 `season_recap` · KP-1 `house_percentile` · AR-2 `arsenal_table` · CS-1 `count_state` · US-1 `appearance_log` · VE-1 `velo_by_outing_bucket` · PA-1 persona signatures and decision rule.

## Reproducing this

```bash
export MLB_DATA_ROOT="/path/to/Python Scripts/MLB"     # dp_uc44_kernel.py + out/dp_uc47_population_graded.csv live there
python dp_uc48_bowlan_recap.py && python dp_uc48_build_figs.py && python dp_uc48_build_dashboard.py \
  && python dp_uc48_build_pdf.py && PKG_DIR="<this folder>" python dp_uc48_verification.py   # 153/153 expected
```

The build refuses to run unless the Phillies log ends 2026-09-23. A refreshed cache is v1.1.0, not a correction.

## Three repo-wide defects found by building

- **O-25** `pitch_mix` rounds `pfx_x`/`pfx_z` to 0.1 ft before anyone multiplies by 12, so every notebook "vert" and "horizontal break" read off it moves in 1.2-inch steps.
- **B-1** `GroupBy.first()` returns the first *non-null* value per column, not the first row. Any "entry state" or "first pitch" read with it can borrow values from later rows.
- **HP-18** A notebook loop (`for gy in …unique()`) leaves `gy` set to whatever season came last in concat order, and later cells use it as "this season".
