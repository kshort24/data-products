# ADDENDUM v1.1.0 — Bat Path · `uc-pos-014` / `dp_uc40a`

**Requested and delivered 2026-09-03 · data as of 2026-09-02 · Human DPO: Kellen Short**
**Verification 180/180 PASS · conventions 12/12 · DQ 10 PASS / 3 WARN / 0 FAIL · CERTIFICATION READY**

---

## 1 · The ask

> "Additional data points available in the most recent years of Statcast data that might offer more
> insight into this proclivity to popups… columns around bat path, things like attack angle and intercept
> point… I have not used these columns much so am not super familiar with them. I would expect the
> data-product-owner to rely on agents like the domain-steward-proxy and source-system-profiler to drive
> an understanding of exactly what these columns are and how to interpret them. Any new functions written
> to leverage these columns should follow the governance discipline of the Baseball Functions script…
> including technical and semantic definitions, documented lineage… double-click into his bat tracking
> against breaking balls… use the pitch_group column."

Scoped as an **additive v1.1.0 addendum**, not a new UC: same subject, same data plane, same value
stream, and it inherits the v1.0.0 kernel unchanged. The `uc-pps-019` `dp_uc21a` addendum is the
precedent.

## 2 · How the ask was honoured

| The DPO asked for | Delivered |
|---|---|
| Understand what the columns actually are | `03a` §1 — six semantic definitions, each with a cited MLB Statcast glossary source. **Nothing inferred.** |
| How to interpret them | `03a` §2 — **12 conventions proven against the data**, not assumed. Two of them are findings: the intercept axes are side and depth with no height component, and **the `attack_direction` sign is inverted versus the published glossary (O-15)** |
| Governance discipline of `Baseball Functions` | `03a` §4 technical definitions (type, units, grain, population, null policy) · §5 KPI specs · §6 column-level lineage · every new function carries its own docstring spec, floors, and null policy |
| Documented lineage | `03a` §6, source column → hop → KPI, for all six new KPIs |
| Double-click on breaking balls | Report §4 — popup rate by pitch group across four seasons, the peer pool, and the breaking-ball-only mechanics table |
| Use `pitch_group` | BP-2 is built on it. Map inherited **verbatim** from the data plane's `PITCH_GROUP` (`dp_uc18` lineage); `other` retained, never dropped |

## 3 · What it found

**Two things changed in the swing and both clear the noise bar.** The swing plane flattened
**27.9° → 25.5°** (peer-netted −1.20°, the largest drop in an 8-hitter cohort; 25.5° is the **flattest of
all 11 Phillies** with 200+ tracked swings, against an MLB average of ~32°) and the contact point moved
**1.35″ further from his body** (peer-netted +1.17″, the largest increase in the cohort; **+1.70″ on
breaking balls**). Attack angle, attack direction, contact depth, swing length and bat speed are all
inside noise once peer-netted.

**The popup problem is a breaking-ball problem.** Popup rate on breaking balls **3.9% → 12.1%** while
fastball (4.7% → 4.2%) and offspeed (4.2% → 4.7%) sat still. He went from **rank 6 of 12 — exactly the
Phillies median — to rank 1 of 10, +4.6 points clear** of a peer median that itself doubled.

**And it is still not bat speed.** v1.0.0 ruled bat speed out from the outcome side; the path data rules
it out from the input side (+0.49 mph peer-netted). Two independent methods, same answer.

## 4 · Gates

| Guardrail | Result |
|---|---|
| No CDE meaning inferred by a downstream agent | ✅ every definition sourced to a cited glossary page |
| Conventions asserted, never assumed | ✅ 12/12, and the build **refuses to publish** on failure |
| Sensor boundaries NULL, never imputed | ✅ path 2025+, `bat_speed` 2024+, `attack_angle` empty in 2024 |
| Rule-1 grep before declaring anything new | ✅ one exploratory notebook cell found; no governed prior art |
| Reconcile with the parent version | ✅ popup rate agrees to < 1e-9 |
| Peer control on instrumented year-over-year claims | ✅ PB-1 on all 7 metrics (O-16) |
| Falsify before describe | ✅ **BP-0 killed the bat-speed-collapse story**; the report says so |
| No causation claimed | ✅ report §6 is hypotheses mapped to remit |

## 5 · Package delta

```
ADDENDUM_v1.1.0_bat_path.md              this file
03a_bat_path_semantics_and_lineage.md    semantics · conventions · dictionary · specs · lineage
05a_bat_path_certification.md            verification design · DQ · defects · versioning · escalations
dp_uc40a_kernel.py                       BP-0/1/2, PU-1/2, PB-1, assert_conventions
dp_uc40a_bat_path.py                     the build
dp_uc40a_verification.py                 180 independent checks
dp_uc40a_bat_path_report.md / .pdf       the consumable
out/dp_uc40a_*.csv                       16 receipts + headlines + console log
out/dp_uc40a_fig1..4.png                 4 figures
dp_uc40_turner_recency_dashboard*.html   + a "Bat path" tab
```

**Escalations E-8 … E-12 added to `00` §7.** O-15 is the one that matters outside this product.
