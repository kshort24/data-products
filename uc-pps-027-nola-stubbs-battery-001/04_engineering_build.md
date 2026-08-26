# 04 · Layer 3 — Build

Agents: `data-engineer` · `data-quality-engineer`

---

## Status: ✅ EXECUTED (run 2, 2026-08-26) — 43 receipts written, 0 DQ FAIL

### Run 2 — the plane was mounted

The DPO granted access to `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB` on request.
Both builds ran against the live parquet plane.

| Artifact | Result |
|---|---|
| `dp_uc38_nola_stubbs_battery.py` | ✅ executed · 29,499 pitches · 311 starts · 2015–2026 · **23 receipts** · 0 DQ FAIL / 0 WARN |
| `dp_uc38b_battery_addendum.py` *(new in run 2)* | ✅ executed · **20 receipts** · 0 DQ FAIL |
| `dp_uc38b_build_figures.py` *(new in run 2)* | ✅ 4 figures |
| `dp_uc38_verification.py --full` | ✅ **48 PASS / 0 FAIL** (Tier A fixtures + Tier B recompute) |
| `dp_uc38b_verification.py` *(new in run 2)* | ✅ **69 PASS / 0 FAIL** — incl. the DPO's own skeleton as an independent path |
| Reader report | ✅ filled from receipts; 0 `«FILL»` tokens remain |

**Defect found and fixed in run 2 — O-12.** `resolve_catcher_names` compared the `pos`-frame
spelling (`Marchán, Rafael`, U+00E1) to the `uc-cat-001` dict spelling (`Marchan, Rafael`) with a
raw `.lower()`, producing a spurious **DQ FAIL** on a name that is the same name. Fixed with
NFKD accent folding before comparison; cross-check is now **7/7 AGREE**. Precedent: Sánchez
650911 (`uc-pps-019`). Repo-wide: any id→name cross-check in this codebase has the same bug.

**Why a second script rather than an edit (DV-9).** The travel test (TR-1) answers a question
the run-1 harness could not have anticipated — *does the approach change appear without
Stubbs?* Putting it in `dp_uc38b_*` leaves the certified primary build byte-stable and
independently re-runnable.

---

### Run 1 — what happened (retained for the record)

The build script was written to specification and passes compilation and unit tests. It
**could not be executed** because the MLB parquet data plane is not reachable from this
session's sandbox.

| Path | Reachable? |
|---|---|
| `Agents for Data Products/` (this repo) | ✅ mounted |
| `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies\phils_*.parquet` | ❌ **not mounted** |
| `data/opponents/*.parquet` | ❌ not mounted |
| `wOBA and FIP Constants.csv` | ❌ not mounted |

The session is non-interactive (scheduled task), so folder access could not be requested.

### What the build does when it cannot find data

```
FATAL: data/phillies not found on any candidate path.
Candidates tried: ...
NO OUTPUT IS WRITTEN -- per the pitcher-scouting-report skill, an unfilled
harness beats a fabricated one.
sys.exit(2)
```

It **refuses to emit partial receipts**. This is deliberate: the `uc-pps-010` failure was a
report with empty slots and no disclosure. A hard exit plus an explicitly-tokenised report is
the corrected behaviour.

### What WAS built and verified

| Artifact | Status |
|---|---|
| `dp_uc38_nola_stubbs_battery.py` | ✅ complete · compiles clean · 850 lines |
| Locked KPI functions (10) | ✅ inherited **verbatim** from `dp_uc25_nola_vs_dodgers.py` — byte-comparable |
| New battery KPIs (BAT-1…BAT-9, CS-1) | ✅ implemented · **18/18 unit tests PASS** |
| `dp_uc38_verification.py` | ✅ Tier A executed and passing; Tier B written, unrun |
| Figure code (4 figures) | ✅ written, unrun |
| DQ scorecard emitter | ✅ written; 15 rules wired |
| Freshness manifest emitter | ✅ written |
| Confound panel (G3) | ✅ written |
| Attribution guard (G4) | ✅ written to disk by the build |

### Unit test evidence (Tier A at run 1; full harness at run 2)

```
run 1 (2026-08-25, fixtures only) : 18 PASS · 0 FAIL · 0 UNRUN · 0 SKIP
run 2 (2026-08-26, --full)        : 48 PASS · 0 FAIL · 0 UNRUN · 0 SKIP
run 2 addendum path               : 69 PASS · 0 FAIL
                                    ---------------------------------
                                   117 PASS · 0 FAIL total
```

Covering: BAT-5 pair/repeat counting and single-pitch-PA exclusion; BAT-6 zero-entropy on a
single-type group and [0,1] bounding; BAT-7 identity/disjoint/symmetry/empty-side-NaN;
CS-1 domain closure; BAT-4 group membership; BAT-2 shares summing to 1; BAT-8 bounding;
BAT-9 filter symmetry; BAT-3 terminal-row population.
Receipt: `out/dp_uc38_verification_results.csv`.

### To unblock (E-1)

```bash
conda activate snakes
cd <this folder>
python dp_uc38_nola_stubbs_battery.py     # ~1 min, writes ./out
python dp_uc38_verification.py --full     # Tier A + Tier B independent recompute
```
Or set `MLB_DATA_ROOT` to the folder containing `phils_*.parquet`, or connect the MLB repo
as a Cowork folder and re-run the scheduled task.

### Engineering notes for whoever runs it

1. **Do not edit the locked KPI functions.** They are verbatim from `dp_uc25`. Editing them
   silently breaks comparability across the whole Nola advance file.
2. `RECENT_N_STARTS = 5` is the only knob that changes the headline. The sensitivity table
   is emitted regardless.
3. If DQ-7 (catcher name cross-check) FAILs, **stop** — it means an id→name authority
   disagreement, which is exactly the class of error the Nola/Nolan-Hoffman rule exists for.
4. `battery_panel` left-merges throughout so zero-event groups survive (the D1/D2 inner-merge
   defect on the repo-wide register). If you see a catcher slot vanish, that is a bug, not a
   filter.
5. Expected runtime < 60s. If it runs long, the `arsenal_entropy` / `count_state_divergence`
   loops are the hot spot (see cost note).
