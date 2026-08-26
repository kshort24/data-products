# 06 · Consumer Success — How to Use This Data Product

Agents: `analytics-enabler` · `consumer-onboarding-agent` · `query-builder`

---

## A · Persona guides

### Pitching Coach
**Your question:** *Is the recent run real, and can we keep doing whatever is causing it?*

Read in this order:
1. **Report §6 (sensitivity)** — first, not last. If the effect only exists at one window
   size, stop reading; there is nothing to keep doing.
2. **Report §7 (confound panel)** — if the Stubbs starts were all at home on extra rest
   against weak lineups, you are looking at scheduling, not game-planning.
3. **Report §5.1 (the lefty channel)** — the actionable cell. First-pitch strike rate to
   LHB is the lever `uc-pps-021` identified and this product re-tests.
4. **Report §3 (the mix)** — what actually changed in the arsenal.

**What you may not conclude:** that Stubbs is calling a better game. The data cannot see who
called anything (AT-1).

### Catching Coordinator
**Your question:** *What is different about how this battery works?*

Go to **§4 (sequencing)** and read all three KPIs together — never one alone. Then **§3.2 /
§3.3** for how hitters get started and finished. **§8** places the pairing on the
`uc-cat-001` strength-vs-weakness axis.

**Caveat you must carry:** `ooz_called_strike_rate` in §5 is the only line partly reflecting
*receiving* skill. Everything else is battery-level and cannot be assigned to the catcher.

### Pitcher / Catcher (the battery itself)
**Your question:** *What are we doing well and what should we repeat tonight?*

**§1 bottom line** and **§3** are yours. Everything is descriptive — this product does not
tell you what to throw; it tells you what you have been throwing when things went well, and
whether the pattern is thick enough to trust. The PA counts on every line are the honesty
check: if it says 30 PA, treat it as a hint, not a plan.

### Advance Group / Analyst
**Your question:** *Is this product sound enough to build on?*

Start with **`05_quality_certification.md`**, then **`02_engineering_design.md` §B** for the
KPI specs. The receipts in `out/` are the only citable numbers. `dp_uc38_verification.py`
is the second path — if you change the build, re-run Tier B.

## B · Common query patterns

```python
import pandas as pd
OUT = "out/"

# 1) The headline comparison
w = pd.read_csv(OUT + "dp_uc38_battery_window.csv")
w[w.window == "last_5"][["resolved_name", "plate_apps", "woba", "xwobacon",
                         "first_pitch_strike_rate", "below_pa_floor"]]

# 2) Did the plan change, or just the results?
seq = pd.read_csv(OUT + "dp_uc38_sequencing_window.csv")
seq[["window_label", "repeat_pitch_rate", "entropy_norm", "js_divergence"]]

# 3) Mix delta vs Nola's own baseline  (the benchmark that matters)
mix  = pd.read_csv(OUT + "dp_uc38_mix_by_catcher_window.csv")
base = pd.read_csv(OUT + "dp_uc38_nola_baseline.csv")
stubbs = mix[(mix.window == "last_5") & (mix.catcher_id == 596117)]

# 4) Is it a window artifact?
pd.read_csv(OUT + "dp_uc38_window_sensitivity.csv")[
    ["window_n_starts", "resolved_name", "plate_apps", "woba", "whiff_rate"]]

# 5) The confound check  — run this BEFORE quoting any gap
pd.read_csv(OUT + "dp_uc38_confound_panel.csv")

# 6) Per-start detail
log = pd.read_csv(OUT + "dp_uc38_start_log.csv")
log[log.game_year == 2026][["game_date", "opponent", "venue", "rest_days",
                            "catcher_id", "catcher_split", "ip_computed",
                            "strikeouts", "walks", "hrs", "woba"]]
```

## C · Interpretation guide — the four traps

| Trap | Why it is tempting | The discipline |
|---|---|---|
| **"Stubbs calls a better game"** | It is the natural sentence and the one people want | AT-1. Attribution is not in the data. Say "with Stubbs catching", never "Stubbs called" |
| **Reading a wOBA gap as a real effect** | wOBA is the familiar number | Check **xwOBAcon**. A wOBA gap without an xwOBAcon gap is sequence luck (`uc-pps-021` house rule) |
| **Quoting a rate without its denominator** | Rates look authoritative | Every table carries PA / pitches / `below_*_floor`. Print them |
| **Treating high entropy or high adaptivity as good** | They sound sophisticated | Neither has a good direction. Nola's identity is a curve thrown a third of the time; drifting off it would raise entropy and hurt |

## D · FAQ

**Q. Why can't we tell who called the pitch?**
Statcast records what was thrown, where, and what happened. There is no PitchCom telemetry,
no shake-off log, no call attribution. This is a property of the data plane, not a gap this
product chose to leave. (AT-1)

**Q. Why compare to Nola's own mean instead of the league?**
The question is whether *his* plan changed. A league benchmark would import arsenal
differences the question does not care about.

**Q. The Stubbs sample looks small. Is the product useless?**
No — but the answer may be "not enough evidence", and that is a legitimate deliverable. The
floors flag rather than filter so you can see exactly how thin it is.

**Q. Can this settle Realmuto vs Stubbs?**
No. One pitcher, non-random assignment, small samples. `uc-cat-001` was designed for that
question at staff scale and is the right vehicle. This UC built its plumbing.

**Q. Why is there no dashboard?**
Priced as a bid option and not taken, to keep the delivery tight. Easy fast-follow.
