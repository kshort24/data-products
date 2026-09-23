# Eleven Percent, All of It Bowlan — Archetype Gap Analysis (pilot: the Elite RHP Four-Seamer)

**UC #47 · `uc-pps-032` · `dp_uc47` · v1.0.0 · delivered 2026-09-22 · READY-CONDITIONAL · independently verified (241/241)**
Phillies Pitching (`pps`, scope note: external evaluation) · Human DPO: Kellen Short

## Start here

| If you want | Open |
|---|---|
| the story | `dp_uc47_elite_ff_archetype_gap_report.pdf` |
| to play with it | `dp_uc47_archetype_explorer.html` (offline; *Notebook dark* toggle) |
| the one picture | `out/dp_uc47_fig1_archetype_map.png` |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the four decisions that are yours | `00` §7 |
| the KPI specs, before reusing them | `03_governance.md` §2 |
| the bid, and how it went | `BID_…md` → `07` §3 |

## The finding, in one paragraph

The notebook asked which archetype — and which player — would move the needle most if added. For the elite
right-handed four-seam, the answer starts by inverting the question: **the Phillies already own the #2
four-seam in the frame** (Jonathan Bowlan, 2026: 97.0 mph, 18.0" of ride, .370 whiff, shape 60 / results 75,
second of 405 pitcher-seasons since 2018), and he is the **only** plus-on-both-axes arm on the staff — so the
2026 elite-four-seam share is **11.1%, all of it his**, and zero if the 9/17 oblique (a carry-in) keeps him out.
**No external arm with a full season of evidence grades higher**: the best is Ohtani's 2025 (58.5, results-only);
the only ranked archetype is Ben Casparius (a Dodgers reliever); the only arm above Bowlan is Jacob Misiorowski,
whom the frame has seen for one start. The needle lives in the rotation — a starter's 669 four-seams move the
share almost 3× a reliever's 241, and the rotation's four-seams score 57, 46, 45 and 39. Inside the room, "best"
depends on what you value: **Duran** if only results count, **McFarlane** (94 pitches, THIN) if only shape counts,
**Bowlan** everywhere between. Your notebook's claims mostly held — Wheeler's velocity is trending down and 2026
matches 2024; Painter's spin (+144 rpm) and ride (+0.8") did jump after the demotion, though the pitch still
grades 40 on results; the Duran "70 FF" card is a 75 on results and a 50 on shape.

## Package contents

```
00_dpo_orchestration_record.md   the spine: framing, 12 gates, capability table, arguments, 6 escalations, C1–C6
01_strategy_intake.md            ID reservation, 7 gaps, what nphl actually is, cohort locks, 6 premises
02_engineering_design.md         one grain / five masks, 7 EDA findings, metadata map, dashboard spec
03_governance.md                 Rule-1 search, 14-term glossary (incl. the stuff→shape rename), 12 KPI specs, lineage, defects
04_engineering_build.md          manifest, environment disclosure, build-time assertions, receipts, reuse
05_quality_certification.md      DQ 16/3/0, brand-center 35/35, harness 241/241, what it caught
06_consumer_success.md           personas, explorer walkthrough, how to read a grade, FAQ, catalog entry
07_platform_marketing.md         5 tripwires, cost audit, bid vs actual, 5 calibration findings, what's next
BID_2026-09-22_…md               the competitive bid — filed, awarded, reconciled in 07
dp_uc47_kernel.py                Section C (FR-1, NR-1, AF-1…AF-6, SG-6, SG-7); imports dp_uc44_kernel (hash-pinned)
dp_uc47_archetype_gap.py         the build
dp_uc47_build_figs.py            7 figures, each asserting its own headline; brand-center MCP compliance
dp_uc47_build_pdf.py             markdown → weasyprint
dp_uc47_build_dashboard.py       Archetype Explorer
dp_uc47_verification.py          6 families, 241 checks
dp_uc47_elite_ff_archetype_gap_report.md / .pdf
dp_uc47_archetype_explorer.html
out/                             27 CSV, 7 PNG, 9 JSON, 2 TXT
uc-pps-032-Elite RHP FF Archetype Gap 20260922.md      repo-side contract
uc_ledger_AI_PATCH_uc-pps-032-elite-rhp-ff-archetype-gap.md   PENDING PASTE
```

## Governed objects: inherited vs introduced

**Inherited (by import, sha256-pinned):** `dp_uc44_kernel` Sections A/B — `get_stats`, `nresults`, `whiff_rate`,
`SWINGS`, `WHIFFS`, … — and **SG-1** `scouting_grade_20_80`, **SG-2** floors, **SG-3**, **SG-5**. This UC is SG-1/SG-2's
independent second use → ratification recommended.

**Introduced (all provisional):** **FR-1** `house_pitch_universe` · **NR-1** `resolve_pitcher_names` ·
**AF-1** `ArchetypeSpec` · **AF-2** `archetype_frame` · **AF-3** `archetype_grades` (+ `ff_elite_shape_flag`,
`ff_elite_results_flag`, `ff_elite_archetype_flag`, composite) · **AF-4** `weight_sensitivity` · **AF-5**
`elite_ff_share` · **AF-6** `needle_swap` · **SG-6** `season_trend_adjust` · **SG-7** `stabilization_k` / `stabilize` ·
**CB-1** candidate evidence floor. Promoted: **Competition Level** (third UC to need it).

## Reproducing this

```bash
export MLB_DATA_ROOT="/path/to/Python Scripts/MLB"     # dp_uc44_kernel.py lives there
python dp_uc47_archetype_gap.py && python dp_uc47_build_figs.py && python dp_uc47_build_pdf.py \
  && python dp_uc47_build_dashboard.py && python dp_uc47_verification.py      # 241/241 expected
```

The build refuses to run unless the Phillies log ends 2026-09-20. A refreshed cache is v1.1.0, not a correction.

## Three new repo-wide defects found by building

- **O-23** `get_nphillies_data()` concatenates 15 minor-league files and never de-duplicates against the
  Phillies logs — every "my dataset" comparison built on `pd.concat([pps, pos, nphl])` carries MiLB pitches and
  duplicates (for four-seams: 51,435 and 9,698).
- **O-24** Team pulls such as `giants-of-rangers-of-24` are batter-keyed: `player_name` is the hitter.
- **BC-1** `brand-center-mcp` `validate_brand_compliance` reads `plotly_template` → `template` → `layout`; a
  bare `template` string hides the layout's Arial font and fails the check.
