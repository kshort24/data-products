# uc-pps-025-raley-acquisition-001

**Brooks Raley — trade-deadline acquisition read, 2026-08-04.**
UC **#31** · contract `uc-pps-025` · build artifact `dp_uc30` · value stream `pps`

Status: ✅ **Build complete — ready for human DPO sign-off.** Internal — Restricted.

---

## What this is

The second of the deadline-acquisition onboarding reads. Raley is a 38-year-old left-handed reliever with Tommy John surgery in the middle of his record, acquired from the Mets. The organization has never worked with him — there are zero Phillies rows — so this is an intake dossier, not an opponent attack plan.

The consumer's hunch was that Raley "provides a funky look from the left-hand side." This package tests that against every left-hander the Phillies have employed in the Statcast era and then turns the answer into three sets of actions — for the pitching department, the battery, and the manager.

**The short version.** The results are excellent (.185/.257/.273, .239 wOBA post-surgery) and they are outrunning the contact: hard-hit rate is up to 33.1%, xwOBAcon is .307, and two home runs in 269 batters faced is not a repeatable skill. Expect regression toward ~.290–.310.

The funky-look hunch is **correct, and the surgery made it funkier**. His release slot dropped and widened post-TJ, giving him the 5th-lowest slot among 30 Phillies left-handers since 2015. Against a left-handed hitter the ball leaves his hand about **one inch** from the centre of that hitter's own box — the population average is 11.5 inches. Left-handers don't miss more often against him, but they miss by 53% more distance and their contact quality collapses (.239 xwOBAcon vs .349 for right-handers).

He is **not a specialist** — 70 of 75 outings faced at least one right-hander — and right-handed contact is the exposure. The single highest-value fix needs nothing from his arm: with two strikes against right-handers he throws his 11.5%-whiff sweeper twice as often as his 48.0%-whiff cutter.

---

## Deliverables

### Reader-facing

| File | What |
|---|---|
| `dp_uc30_raley_acquisition_read_report.pdf` | **The report.** 11 pages, Phillies-branded, 9 tables, 5 figures |
| `dp_uc30_raley_acquisition_read_report.md` | Markdown source |
| `uc-pps-025-Brooks Raley PHI 20260804.md` | Use-case contract — problem statement, six questions answered, actions |

### Build & verification

| File | What |
|---|---|
| `dp_uc30_raley_acquisition_read.py` | The build. **The only place numbers are computed** |
| `dp_uc30_build_pdf.py` | Markdown → weasyprint renderer |
| `dp_uc30_verification.py` | Independent recompute — **661/661 checks passed** |
| `out/` | 21 CSV receipts + 5 figures + DQ scorecard + freshness manifest + verification results |

### Governance trail

`00_dpo_orchestration_record.md` (spine) · `01_strategy_intake.md` · `02_engineering_design.md` · `03_governance.md` · `04_engineering_build.md` · `05_quality_certification.md` · `06_consumer_success.md` · `07_platform_marketing.md`

---

## What's new in this UC

**A benchmarked population study.** UC#30 (Kilian) asked "what did the role change do to him." This one asks "is this unusual, and compared to what." Answering it required scoring the subject against a defined population — all 28 Phillies left-handers with ≥300 pitches since 2015 — rather than against his own history. Raley is deliberately **excluded from the centroid** he is measured against. That pattern generalizes to any "is this pitcher's X unusual?" question.

**A proxy that ships with its calibration.** Statcast's native `arm_angle` exists in this repo's Phillies files only from 2025; the requested benchmark spans 2015–2026. Rather than truncate the population or silently substitute, the build derives **Release Slot Angle** from release coordinates, calibrates it against native `arm_angle` on the 10-pitcher overlap (**r = 0.831**, residuals published to ±14°), gates publication on `|r| ≥ 0.80` as a DQ rule, and labels RSA a proxy everywhere it appears. **New house rule: a derived metric standing in for a missing field must ship with its calibration.**

**A published negative result.** One of the four new KPIs — the Release Distinctiveness Index — does *not* support the report's headline. Raley scores 1.26 against a population mean of 1.20, i.e. unremarkable, because RDI is a distance and discards direction. It is reported as a negative finding in the report body rather than quietly dropped.

**A defect caught by the harness.** First verification run came back 657/659. Both failures were real: the inherited `xwobacon()` reports its balls-in-play count using `size` semantics, counting batted balls with no tracked xwOBA estimate, so the published *n* runs 2–5 high (178 vs 176 post-TJ). The rates are correct. The locked function was **not edited** — it is shared with `dp_uc28`/`dp_uc29` and patching it mid-build would silently fork a definition. Instead the gap is asserted in the harness, disclosed in the report caveats, and logged as **open item O4** for a coordinated version bump. See `05_quality_certification.md` §5.3.

---

## New KPIs

| KPI | One line | Status |
|---|---|---|
| **Release Slot Angle (RSA)** | `deg(atan2(rel_z, |rel_x|))` — arm-slot proxy computable across the full 2015–2026 span | Report-local; strong promotion candidate **with its calibration rule attached** |
| **Sightline Offset (SLO)** | Lateral feet between release point and the centre of the hitter's box | Report-local; strong candidate. Depends on an asserted coordinate convention |
| **Release Tipping Delta (RTD)** | Max gap between per-pitch-type mean release points, in inches | Report-local; promote only with its within-pitch-noise comparator |
| **Release Distinctiveness Index (RDI)** | SD-distance from the population centroid | Report-local; **weak candidate** — direction-blind, produced a negative result |

---

## Reading rules

1. **Never quote a blended Raley number.** Pre-TJ and post-TJ are separate tiers by design and are never combined.
2. **Post-TJ is 269 batters faced.** Every rate carries its n. The vs-LHH split is 100 BF.
3. **RSA is a proxy.** It orders pitchers low-slot to high-slot reliably; it does not reproduce a specific arm angle.
4. **SLO is geometry, not outcome.** The tracking claim rests on miss-distance and contact-quality splits with small samples.
5. **RDI does not support the distinctiveness headline.** Do not cite it in support.
6. **xwOBAcon BIP counts run 2–5 high** (open item O4). The rates are correct.

---

## Verification

```bash
python dp_uc30_raley_acquisition_read.py    # rebuild all receipts and figures
python dp_uc30_verification.py              # 661 independent checks
python dp_uc30_build_pdf.py                 # markdown → branded PDF
```

Set `MLB_DATA_ROOT` to override the data path. The harness deliberately **does not** import the build's locked KPI functions — it recomputes everything from primitive pandas operations so a logic error in a shared function surfaces as a mismatch rather than being faithfully reproduced.

---

## Closure step

Re-read at **100 batters faced in a Phillies uniform**. The backtest scores three things: whether the two-strike cutter recommendation was adopted, whether it moved the right-handed contact quality off .349, and whether the explicit regression forecast (~.290–.310 wOBA against a .239 baseline) held. **That forecast is on the record.**
