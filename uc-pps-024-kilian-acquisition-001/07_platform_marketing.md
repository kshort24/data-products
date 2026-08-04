# 07 — Platform & Marketing

**Department:** Platform (persistent) ∥ Marketing · **Agents:** `data-observability`, `version-controller`, `cost-watchdog`

---

## 7.1 `data-observability` — monitoring rules & runbook

This data product is **single-run, not a live pipeline** — there is no scheduled refresh, so classic freshness/volume alerting does not apply as written. What *does* need monitoring is the set of conditions under which this report becomes wrong.

### Staleness triggers — conditions that invalidate the report

| # | Trigger | Detection | Runbook |
|---|---|---|---|
| T1 | **Kilian throws for the Phillies** | `phils_2026.parquet` contains `pitcher == 668873` | Re-run the build with a third era tier (`2026 PHI`). Do **not** pool it into the SF tier |
| T2 | **150 PA in Phillies uniform reached** | PA count on the PHI tier | **Closure step.** Re-test the reverse platoon split (O4) and Slider Finish Rate vs the 70% target |
| T3 | **A role is assigned** | Manual / DPO input | Re-open the descoped opponent dimension (01 §V1) as a new UC |
| T4 | **Cache refresh past 2026-08-01** | `max(game_date)` in `kilian.parquet` | Re-run; any SF appearance after 8/01 is currently missing |
| T5 | **Sacramento 2025 MiLB cache acquired** | File appears in `data/opponents/` | Re-run with a bridging tier — this closes the single largest interpretive limitation |

### Schema-drift monitors

| Monitor | Threshold | Rationale |
|---|---|---|
| Tracking-field completeness | < 0.95 on tracked pop | Hawk-Eye degradation would silently weaken every location KPI |
| `automatic_ball` share | > 3% of rows | The tracked/full population gap widens; O2 impact grows |
| `launch_speed` on non-BIP rows | any change in behaviour | The O3 trap depends on current feed behaviour |
| Statcast field renames | `pitch_name`, `plate_x`, `zone`, `arm_angle` | Build asserts on these; a rename fails loudly, which is correct |

### Alert routing
Blocking assertion failure (entity lock, dedup, game type, 2025 gap) → build **stops**, no output, escalate to DPO. WARN-level → recorded in the scorecard, report proceeds with disclosure.

---

## 7.2 `version-controller` — versioning & change classification

**Version:** `dp_uc29` **v1.0.0** — initial release. **No consumers, no breaking-change surface.**

| Change class | Applies |
|---|---|
| Breaking | none |
| Non-breaking additive | 3 new KPIs, 19 receipts, 4 figures — all new files |
| Deprecation | none issued by this UC |

**Inheritance manifest — what this UC consumed and what it emits:**

| Inherited from | What | Integrity |
|---|---|---|
| `dp_uc28` (UC #29, Painter) | 8 locked KPI functions | **byte-identical**, unmodified even where defective (O2) |
| `uc-pps-021` (UC #26, Nola) | `xwobacon` BIP-only hardening | applied; contaminated column quarantined |
| `dp_uc11` (UC #11, Rangel) | Multi-tier evidence rule | adapted to role-era tiers, never-blend preserved |
| `dp_uc28` (UC #29, Painter) | Self-scout variant (opponent descoped) | extended to acquisition-onboarding |

**Emitted for downstream inheritance:**

| Artifact | Why the next UC should take it |
|---|---|
| **Role Conversion Delta** | The most portable of the three new KPIs. Any converted acquisition — starter→reliever, or the reverse — inherits it directly |
| **Tracked-pitch population rule** | Applies to every UC in the repo, not just this one. `automatic_ball` rows exist in all modern seasons |
| **`launch_speed` foul-contamination warning (O3)** | A trap any future UC will hit. Recommend a shared `ev()` helper |
| **Acquisition-onboarding template** | Four remaining deadline acquisitions can reuse this structure verbatim: era-tier split, no opponent, persona sections for department/battery/manager |

**Ledger patch required:**

```
| 30 | uc-pps-024 | Kilian acquisition read (deadline onboarding) | Delivered |
     `data-products/uc-pps-024-kilian-acquisition-001/` — dp_uc29 + 19 receipts +
     4 figures + 00-07 governance; 205/205 verification; NEW KPIs SFR/FER/RCD;
     first acquisition-onboarding variant; opened O2 (locked in_zone_rate) and
     O3 (launch_speed foul contamination) |

Next available: UC #31 / dp_uc30  (uc-pps-025 / uc-pos-008)
```

---

## 7.3 `cost-watchdog` — cost efficiency

| Dimension | Finding |
|---|---|
| Input volume | 291 KB parquet, 1,271 rows post-filter — trivial |
| Compute | Single-pass pandas, no ML, no cross-source joins. Full build + verification runs in seconds |
| Storage | 19 CSVs (~25 KB total) + 4 PNGs (~310 KB) + 371 KB PDF |
| Recompute waste | **None** — build is idempotent, writes only `dp_uc29_*` files, overwrites nothing |
| Over-provisioning | None |

**Optimization recommendations (ranked, none urgent):**

1. **Extract the locked KPI functions into a shared module.** They have now been copied verbatim across five UCs. A shared `baseball_kpis.py` would let the O2 fix land once instead of five times — and would have prevented the O3 trap entirely via a shared `ev()` helper. **Highest-value item in this file.**
2. **Build the acquisition dashboard once for the cohort**, not per player (see 06 §6.6). Four more acquisitions are queued.
3. **Cache the wOBA-constants merge** — negligible here, but it is re-read per build across every UC.

**Watchdog verdict:** ✅ no cost concerns. Recommendation 1 is a maintainability argument wearing a cost hat, and it is the one worth acting on.

---

## 7.4 Marketing / publication

**Publish scope:** 🔒 **Internal only.** Enforced by `03_governance.md` §3.3-3.4 — not a privacy block, a competitive and employment-sensitivity block. The report states exactly how to attack this pitcher and recommends limiting his usage.

**Distribution:** pitching department, catchers, Kilian, manager, front-office analytics.

**Artifacts:**

| Artifact | Audience |
|---|---|
| `dp_uc29_kilian_acquisition_read_report.pdf` (9pp, branded) | All four personas — the primary deliverable |
| `dp_uc29_kilian_acquisition_read_report.md` | Source, for amendment |
| `out/*.csv` (19 receipts) | Analysts |
| `00`–`07` governance trail | DPO, governance review |
| `dp_uc29_verification.py` | Anyone who wants to re-prove a number |

**Headline for internal circulation:**

> *The bullpen move worked — 15% strikeouts became 27% and he added three miles an hour. But he's a reverse-platoon arm who's given up all five of his homers to right-handed hitters, and three of them were sliders that backed up over the plate. Four batters, lefty-heavy stretches, and one very teachable fix.*
