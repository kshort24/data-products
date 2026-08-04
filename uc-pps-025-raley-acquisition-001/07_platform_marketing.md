# 07 — Platform & Operations

**Layer 4 / Layer 6** · UC #31 · `uc-pps-025` · build `dp_uc30`
**Agents:** `data-observability` → `version-controller` → `cost-watchdog`

---

## 7.1 `data-observability` — monitoring rules & runbook

This is a point-in-time dossier, not a scheduled pipeline. Monitoring is therefore about **staleness and invalidation**, not job health.

| Rule | Trigger | Severity | Action |
|---|---|---|---|
| **OBS-1 — cache staleness** | `raley.parquet` max `game_date` more than 7 days behind today | Warning | Refresh cache; the report's freshness banner is wrong |
| **OBS-2 — Phillies rows appear** | any row where the pitching team is PHI | **Info — expected and desirable** | This is the closure trigger. See 7.2 |
| **OBS-3 — entity-lock breach** | distinct `pitcher` ids ≠ 1, or distinct `player_name` ≠ 1 after lock | **Critical** | Halt. Cache contamination — the Nola/"Nolan Hoffman" failure mode |
| **OBS-4 — coordinate-convention flip** | Phillies LHP mean `release_pos_x` ≤ 0, or RHP mean ≥ 0 | **Critical** | Halt. Every sightline number is invalid. Rebuild after re-establishing the convention |
| **OBS-5 — RSA calibration decay** | `|r|` vs native `arm_angle` drops below 0.80 on rebuild | **Critical** | RSA may no longer be published as an arm-slot proxy. Fall back to native `arm_angle` and truncate the benchmark window |
| **OBS-6 — benchmark population shrink** | Phillies LHP with ≥300 pitches falls below 20 | Warning | Distinctiveness claims lose their comparator; widen the window or lower the threshold and re-state |
| **OBS-7 — schema drift** | any CDE in the lineage disappears or changes dtype | **Critical** | Halt build |
| **OBS-8 — critical CDE completeness** | `release_pos_x/z`, `stand`, `description` fall below 0.95 | **Critical** | Halt build |
| **OBS-9 — velocity cliff** | rolling 5-outing mean velocity drops > 2 mph below the post-TJ mean (85.0) | Warning | Health signal. Escalate to the pitching department; the dossier's expectations no longer hold |
| **OBS-10 — sweeper IVB movement** | rolling sweeper IVB moves > 1.5 in from 4.8 | Info | The report's primary development recommendation is either working or worsening. Re-read |

**Runbook.** Critical → halt and notify the human DPO; do not publish downstream. Warning → publish with a corrected freshness banner and a note. Info → log; feed OBS-9/10 to the pitching department as a development-tracking signal.

**Observability does not remediate.** It detects, alerts and documents.

---

## 7.2 `version-controller`

**Version:** `uc-pps-025 v1.0` · build `dp_uc30` · 2026-08-04
**Change class:** **New product.** No prior version, no consumers, no breaking-change surface.

### Inheritance ledger

| Inherited from | What | Class |
|---|---|---|
| `dp_uc29` (UC#30, Kilian) | 9 locked KPI functions, byte-identical | Non-breaking |
| `dp_uc29` | Acquisition-onboarding package shape (no opponent, no in-org baseline) | Non-breaking |
| uc-pps-021 O1 | `xwobacon` supersedes pitch-level `xwoba` | Non-breaking |
| uc-pps-024 O2 | `zone_rate_strict` supersedes `chase_rate.in_zone_rate`; untracked-row quarantine | Non-breaking |

### Introduced

| Item | Class | Consumer impact |
|---|---|---|
| RSA, RDI, SLO, RTD | New report-local KPIs | None — no prior definition to break |
| Population-benchmark pattern | New method | Reusable; no breaking surface |
| Proxy-with-published-calibration rule | New governance rule | **Applies forward.** Any future derived metric standing in for a missing field must ship its calibration |

### Deprecation notices

None.

### Forward-looking, for the next revision

| Item | Note |
|---|---|
| **O4 — `xwobacon_bip` `size` semantics** | Fix in the next KPI-function revision, alongside uc-pps-021 O1. **Will be a breaking change** to the count column (not the rate) — every UC from `dp_uc28` forward publishes it, so it needs a coordinated version bump and a consumer notice, which is precisely why it was not patched here |
| **RDI** | Either promote with its direction-blindness attached, or replace with a signed two-axis form before it is reused |

---

## 7.3 `cost-watchdog`

| Dimension | Finding |
|---|---|
| Compute | Local pandas over 4,184 subject rows + 65,221 benchmark rows. Full build ≈ seconds. Negligible |
| Heaviest step | Loading 12 `phils_*.parquet` files for the benchmark — mitigated by **column projection** (14–15 columns of 94–121) and conditional `arm_angle` read |
| Storage | 21 CSVs + 5 PNGs + PDF ≈ 1.3 MB |
| Recompute waste | None — single-pass build; verification is a deliberate second path and is the point, not waste |
| Over-provisioning | None |

**Recommendations (unranked, all low priority):**

1. If the benchmark population is reused across future UCs, cache the 28-pitcher aggregate to `data/_derived/phillies_lhp_release_benchmark.parquet` rather than re-scanning 12 season files. Payback after ~3 uses.
2. The `pyarrow.ParquetFile` schema probe per file is cheap but repeated; a one-time schema manifest would remove it.

**No changes implemented.** Findings only.

---

## 7.4 Ledger update required

The `pitcher-scouting-report` skill's installed ledger (`references/uc-ledger.md`) is stale — it reads "Next available: UC #12". It cannot be edited from inside a session. **Please apply this row and bump the pointer:**

```
| 31 | uc-pps-025 | Raley acquisition read (2026-08-04) | Delivered | data-products/uc-pps-025-raley-acquisition-001/ — dp_uc30; 2nd acquisition-onboarding variant; adds population-benchmark pattern + proxy-with-calibration rule (RSA/RDI/SLO/RTD); 661/661 verification |
```

**Next available: UC #32 / dp_uc31** (`uc-pps-026` / `uc-pos-008`).

---

## 7.5 Closure step

**Trigger:** Raley reaches **100 batters faced in a Phillies uniform** (OBS-2 fires on first PHI row; count from there).

**The backtest asks three things:**

1. **Was the sequencing recommendation adopted?** Did two-strike cutter usage vs RHH rise from 20.3%? Did sweeper usage in those counts fall from 44.7%?
2. **Did it move the outcome?** Compare RHH xwOBAcon against the .349 baseline and RHH hard-hit against 36.0%.
3. **Did the expectation hold?** Post-TJ wOBA was .239 against a .307 xwOBAcon. This dossier forecast regression toward roughly .290–.310. **That forecast is on the record and should be scored.**

Secondary: did sweeper IVB move back toward 2.5 in (OBS-10), and did RTD fall below the 2.3-in within-pitch noise floor?
