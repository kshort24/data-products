# uc-pps-024-kilian-acquisition-001

**Caleb Kilian — trade-deadline acquisition read, 2026-08-04.**
UC **#30** · contract `uc-pps-024` · build artifact `dp_uc29` · value stream `pps`

Status: ✅ **Build complete — ready for human DPO sign-off.** Internal only.

---

## What this is

The first of five deadline-acquisition onboarding reads, starting with the player who has the least MLB history. Kilian came up as a Cubs starting prospect, never stuck, threw no big-league innings in 2025, and spent 2026 in the Giants bullpen. This package asks what the conversion actually bought, and turns the answer into three different sets of actions — for the pitching department, for the battery, and for Don Mattingly.

**The short version:** the bullpen move worked and it is not subtle — all ten tracked process KPIs improved at once, strikeout rate 15.2% → 27.5%, and the four-seamer gained 2.9 mph. But xwOBAcon moved only .370 → .346, so what he bought was contact *avoidance*, not contact *management*. He is a reverse-platoon arm: he whiffs right-handed hitters at 37.5% and has given up all five of his home runs to them, against zero in 110 plate appearances versus lefties. Three of those five were sliders that backed up to the arm side instead of finishing away — 15 such pitches carry three home runs, while the 32 that finished glove-side carry none.

---

## Deliverables

### Reader-facing

| File | What |
|---|---|
| `dp_uc29_kilian_acquisition_read_report.pdf` | **The report.** 9 pages, Phillies-branded, 11 tables, 4 figures |
| `dp_uc29_kilian_acquisition_read_report.md` | Markdown source |
| `uc-pps-024-Caleb Kilian PHI 20260804.md` | Use-case contract — problem statement, questions answered, actions |

### Build & verification

| File | What |
|---|---|
| `dp_uc29_kilian_acquisition_read.py` | The build. **The only place numbers are computed** |
| `dp_uc29_build_pdf.py` | Markdown → weasyprint renderer |
| `dp_uc29_verification.py` | Independent recompute — **205/205 checks passed** |
| `out/` | 19 CSV receipts + 4 figures |

### Governance trail

`00_dpo_orchestration_record.md` (spine) · `01_strategy_intake.md` · `02_engineering_design.md` · `03_governance.md` · `04_engineering_build.md` · `05_quality_certification.md` · `06_consumer_success.md` · `07_platform_marketing.md`

---

## What's new in this UC

**First acquisition-onboarding variant.** Every prior pitcher-side UC anchored on Phillies data. This one runs entirely off an opponent-folder cache for a player who has never thrown a pitch for the organization — no Phillies rows, no opponent dimension, no assigned role.

**Three new KPIs**, each specified before use:

| KPI | What it measures | Why it exists |
|---|---|---|
| **Slider Finish Rate** | Share of sliders finishing glove-side vs backing up arm-side | Separates execution from pitch design — raw slider whiff rate can't |
| **Fastball Elevation Rate** | Share of four-seamers in the upper third of the *batter's* zone | A +15.7" IVB fastball realises its value above the barrel plane |
| **Role Conversion Delta** | Signed current-vs-prior delta per locked KPI, carrying both denominators | The most reusable of the three — any future converted acquisition inherits it |

**A tracked-pitch population rule** that applies repo-wide: 8 `automatic_ball` pitch-timer rows carry no pitch type, zone, or location. They count as balls for plate-appearance outcomes and are excluded from every usage and location denominator. Published usage uses **728 tracked pitches, not 736**.

---

## Certification

**PASS — cleared for internal advance use.** Independent verification recomputed every headline number through a separate code path (plain boolean masks, no import of the build module): **205/205**. The DQ scorecard ran 32 checks: **0 FAIL, 2 WARN**, both disclosed in the report's own caveats.

**The verification pass earned its keep.** Its first run returned 199/205, and three of the six failures were real defects in the draft:

1. **Exit-velocity means contaminated by foul balls** — `launch_speed` is populated on 114 foul rows in this feed, so the slider vertical-half table read 6-7 mph low. Corrected to 86.8 / 99.1 mph. → **O3**
2. **Zone rate inflated** by untracked rows flowing into the locked `in_zone_rate` calculation — 48.6% published, 48.1% correct. → **O2**
3. **Usage denominators inconsistent** — shares computed on one population, counts printed from another.

All three would have shipped without the independent recompute.

An earlier near-miss, caught in build rather than verification: `groupby().first()` returns the first *non-null* value per column independently, which reported 36 of 45 outings with inherited runners. The true figure is **13 of 45** — enough to have mis-described his role to the manager.

---

## Open items for the human DPO

| # | Item | Severity |
|---|---|---|
| **O1** | Promote `xwobacon` to the glossary, deprecate pitch-level `get_stats.xwoba` repo-wide *(carried from `uc-pps-021`; hardening applied here)* | Medium |
| **O2** | **New** — locked `chase_rate().in_zone_rate` counts null-zone rows as in-zone. Locked function left unmodified; strict variant published | Medium |
| **O3** | **New** — `launch_speed` is populated on foul balls. Recommend a shared `ev()` helper so the next UC can't hit this | Medium |
| **O4** | Reverse platoon split is directional at 83 PA vs RHH but drives the deployment recommendation | Low |

**Ledger append pending.** Next available: **UC #31 / dp_uc30** (`uc-pps-025` / `uc-pos-008`).

---

## Closure step

Re-read at **150 PA in Phillies uniform**: re-test the reverse platoon split (O4) and measure Slider Finish Rate against the 70% glove-side target.

## Reuse

The four remaining deadline acquisitions can take this structure directly — era-tier split with a never-blend rule, opponent descoped, persona sections for department / battery / manager, and Role Conversion Delta for anyone whose role changed. Build the cohort dashboard once rather than per player.
