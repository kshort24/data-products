# uc-pps-027 · The Nola–Stubbs Battery

**UC #38 · build `dp_uc38` · PHI @ SEA, 2026-08-26 · delivered across two runs**

> ## ✅ STATUS: DELIVERED — CERTIFY-READY
>
> **117/117 independent verification checks PASS · 0 DQ FAIL · 43 package-audit checks PASS ·
> 43 receipts on disk · 0 `«FILL»` tokens remain.**
>
> Run 1 (2026-08-25, scheduled) shipped the harness **unfilled** — the MLB parquet plane was not
> mounted, and per the `pitcher-scouting-report` skill's first non-negotiable, no number was
> invented. Run 2 (2026-08-26) mounted the plane, executed both builds, and **changed the
> answer.**
>
> ```bash
> conda activate snakes
> cd <this folder>
> python dp_uc38_nola_stubbs_battery.py    # primary build   → 23 receipts
> python dp_uc38b_battery_addendum.py      # addendum build  → 20 receipts
> python dp_uc38b_build_figures.py         # 4 figures
> python dp_uc38_verification.py --full    # 48 PASS
> python dp_uc38b_verification.py          # 69 PASS
> python dp_uc38_package_audit.py          # 43 PASS (no data plane needed)
> ```
> Data root resolves from `$MLB_DATA_ROOT`, then `./data/phillies`, then the DPO's default path.
> wOBA constants resolve from `$MLB_WOBA_CSV`, then `./`, then the default path.

---

## The finding

The ask was: *how has the game planning been different with Stubbs back there, and is anything
they're doing driving the better results?*

**The game plan did change — and it is Nola's change, not Stubbs's.**

Since **2026-07-05** the battery throws a materially different game: changeup share
**12.7% → 22.8%**, two-strike fastball rate **47.8% → 35.4%**, changeup-when-behind
**12.5% → 28.2%**. The question the product exists to answer is whether that is the *pairing*.
So the build asks it as a design rather than a correlation: **does each change also appear in
the starts Stubbs did not catch?**

**Ten of twelve approach metrics move the same direction in both strata.** On the two-strike
fastball retreat, the non-Stubbs move is *larger*. An adjustment that survives a change of
catcher is a property of the pitcher. With PitchCom on Nola's belt that is consistent with him
driving it — and the data cannot say more than that, because **pitch-call attribution does not
exist in Statcast** (guardrail G4 / glossary AT-1).

What Stubbs adds is **degree, not direction**: the most extreme version of the same plan, plus
2026's best outcome line (**.310 wOBA in 8 starts** vs .363 Realmuto / .391 Marchán) against a
slate the rest of the staff found **harder**, not softer. The career panel is the counterweight:
across four seasons the battery is a coin flip (.307 vs .300), and in 2024 the two split Nola's
starts 16–16 and finished .315 / .304.

**Bonus, and the reason to read §5.2:** `uc-pps-021`'s July prescription was adopted and **three
of its four tripwires moved** — changeup vs LHH .179 → .274, LHH walk rate .119 → .068, LHH wOBA
.385 → .313. The fourth did not: first-pitch strike rate to lefties is **.578 → .581**. He is not
getting ahead of lefties, he is *escaping* them with the changeup. That is the fragility to
watch tonight.

---

## Read in this order

| # | File | What it is |
|---|---|---|
| 1 | `dp_uc38_battery_dashboard.html` | **The read, as a page** — self-contained, theme-aware, opens offline. Also published: https://claude.ai/code/artifact/f05d7823-ac11-414b-a213-f6251503a41f |
| 2 | `dp_uc38_nola_stubbs_battery_report.md` | The full governed report — bottom-line-first, PA printed on every small-sample line |
| 3 | `BID_2026-08-25_uc-pps-027-nola-stubbs.md` | The competitive bid, and §8 — why the shop went **36% over** and why that was correct |
| 4 | `05_quality_certification.md` | Certification verdict + the *Late finding* section |
| 5 | `telemetry/calibration_report.md` | Bid vs actual, both runs, with the honest counterfactual |

## Everything else

| File | What it is |
|---|---|
| `uc-pps-027-nola-stubbs-battery-001.md` | Use-case contract, acceptance criteria, delivery record |
| `00_`–`07_` | Governance spine — orchestration → intake → design → governance → build → certification → consumer → platform. Run-1 verdicts retained as history; run 2 authoritative |
| `dp_uc38_nola_stubbs_battery.py` | Primary build — locked outcome layer + BAT-1…BAT-9 |
| `dp_uc38b_battery_addendum.py` | Addendum build — TR-1 travel test, TR-2 breakpoint scan, OC-1 opponent control, LH-1, CH-1 |
| `dp_uc38b_build_figures.py` | Four figures, drawn **only** from receipts |
| `dp_uc38_verification.py` | Tier A fixtures + Tier B recompute (48) |
| `dp_uc38b_verification.py` | Three independent paths (69) — incl. **the DPO's own merge skeleton**, honoured as bid |
| `dp_uc38_package_audit.py` | Package-level governance audit; runs without the data plane (43) |
| `out/` | 43 receipts + 8 figures + verification results |
| `telemetry/` | Run economics ledger (both runs) + calibration report |
| `uc_ledger_AI_PATCH_*.md` | One-row ledger patch for Kellen to paste |
| `_receipts_bundle_2026-08-26.tar.gz` | Archive of `out/` as delivered (transfer artifact — safe to delete) |

## KPIs

**Outcome layer — 10 inherited verbatim** from the locked UC8 → UC25 line (`get_stats`/`nresults`,
whiff, chase, putaway, FPSR, hard-hit, edge rate, OOZ called-strike rate, air/GB, xwOBAcon).
Zero re-derivation. Do not edit.

**Battery layer (run 1):** CS-1 count state · BAT-1 pitch-mix share · BAT-2 first-pitch group mix ·
BAT-3 putaway-pitch mix · **BAT-4 two-strike fastball rate** *(inherited from `uc-cat-001` KPI-1 —
first build)* · BAT-5 repeat-pitch rate · BAT-6 arsenal entropy · BAT-7 ahead-vs-behind divergence ·
BAT-8 zone rate by count state · **BAT-9 in-zone whiff rate** *(inherited from `uc-cat-001` KPI-3 —
first build)*.

**Method layer (run 2, NEW-PROVISIONAL):** **TR-1** adjustment-travel test · **TR-2** breakpoint
sensitivity scan · **OC-1** opponent-quality control · **LH-1** handedness panel · **CH-1**
pitch-performance panel. Specs in `03_governance.md`; **TR-1 and OC-1 generalise well beyond
this UC.**

**New guardrails:** **G6** an era boundary is a researcher degree of freedom — scan it.
**G7** a delta that appears in only one stratum of a non-random split is a hypothesis, never a
finding.

## Lineage

Pattern **UC3 → UC6 → UC8 → UC11 → UC15 → UC25 → UC35 → UC38**.
Cross-stream: **`uc-cat-001`** (catcher philosophy — this UC is its **first delivered consumer**,
shipping 2 of its 10 KPIs) and **`uc-pps-021`** (the 2026 lefty diagnosis, re-asked and scored).

## What needs Kellen

| # | Action | Effort |
|---|---|---|
| **E-2** | Ratify or retire **BAT-5 / BAT-6 / BAT-7** and the new **TR-1 / TR-2 / OC-1 / LH-1 / CH-1** family | judgement call |
| **E-4** | Confirm tonight's battery | pre-game |
| **E-5** | `uc-cat-001` fast-follow — 7 KPIs and the staff-wide report still owed | scoping |
| **E-6** | Arm the **RHH walk tripwire** — 1.9% → 7.4% since 7/05. Re-check in two starts | monitoring |
| **E-7** | Paste the ledger patch | ~1 min |
| **E-8** | Post-game backtest of tonight — projected approach vs actual. Offered, not scheduled | your call |

*Closed this session: **E-1** (data plane mounted) · **O-12** (accent-insensitive id→name
cross-check — a repo-wide pattern, not just this build).*
