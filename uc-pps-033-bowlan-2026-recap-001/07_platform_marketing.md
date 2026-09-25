# 07 · Platform & Marketing: `uc-pps-033`

Agents: `cost-watchdog` · `token-economist` · `data-observability` (tripwires only)

## 1 · Tripwires (armed; re-run the build when one trips)

| # | Tripwire | Why it matters |
|---|---|---|
| T-1 | **Bowlan pitches again** (postseason or 2027) | The groin-strain carry-in resolves into data. Any postseason appearance is a v1.1.0 appendix; the regular-season numbers do not change |
| T-2 | **Sinker whiff clears .12 over ≥ 50 swings** | WA-1 comes off the watch list |
| T-3 | **Sweeper reaches ~500 pitches** | WA-2's RV/100 starts to mean something (uc-pps-032 SG-7: RV needs about 1,084 to be half signal) |
| T-4 | **O-25 is fixed upstream** (E-2) | The notebook-exact HP-13 row changes; re-run SR-1 with `governed=False` to confirm the two modes agree on ride |
| T-5 | **The 2027 season begins** | KP-1 gains a season of population. Percentiles are superseded, not corrected |

## 2 · Cost audit (`cost-watchdog`)

| Hotspot | Cost | Recommendation |
|---|---|---|
| Reading prior-UC receipts to match the house format (uc-pps-032 00–07, BID, README) | ~45k tokens of input, the largest single item after staging | Put the `00`–`07` skeleton, BID skeleton and harness family list into a **skill card** (or reuse `tpl/`). The pitcher-scouting-report skill's ledger is stale at UC #12 |
| Staging 16 files (60 MB) because the laptop VM is full | ~3 min, ~12k tokens | Free space on the VM (`/sessions` at 100%) or install `pyarrow` there. The whole build would then run where the data lives, with no staging and no commit |
| `plotly.min.js` inlined per dashboard (4.8 MB × 2 copies) | disk | Carry-forward (uc-pps-026 F1, uc-pps-032): one shared `_assets/plotly.min.js` |
| PNG export via kaleido/Chromium | ~40 s of ~70 s build | Fine for a recap; skip PNGs for dashboard-only runs |

## 3 · Bid vs actual (`token-economist`)

Denominator: **incremental session tokens** (new context + generated), estimated from the session counter, which is the same unit the bid was priced in. Minutes are wall clock from the first tool call (03:50 UTC) to the final commit (~04:32 UTC).

| Phase | Bid in | Bid out | Bid min | Actual in (est.) | Actual out (est.) | Actual min |
|---|---|---|---|---|---|---|
| T0 Intake, recon, staging, profile | 110k | 8k | 10 | ~130k | ~6k | 12 |
| T1 Kernel + build + receipts + probe | 45k | 18k | 8 | ~90k | ~22k | 7 |
| T2 Figures + brand compliance | 30k | 10k | 5 | ~55k | ~12k | 5 |
| T3 Narrative dashboard | 35k | 25k | 10 | ~45k | ~18k | 4 |
| T4 Report + PDF | 25k | 14k | 6 | ~25k | ~8k | 2 |
| T5 Verification harness | 20k | 10k | 4 | ~35k | ~10k | 3 |
| T6 Governance 00–07, README, contract, ledger, commit | 30k | 35k | 12 | ~40k | ~22k | 9 |
| D Defect discovery | 10k | 3k | 2 | ~10k | ~2k | (in T1) |
| **Total** | **~305k** | **~123k** | **~57** | **~430k** | **~100k** | **~42** |

**Credits at list ($10/M in, $50/M out):** bid ≈ **$9.20**, actual ≈ **$9.30** (+1%).
**Input +41%, output −19%, time −26%.** Full scope delivered; nothing was de-scoped. This is the first instrumented bid to land within 5% on cost, but only because an input overrun offset an output underrun.

## 4 · Calibration findings (sixth instrumented bid)

- **C-1 · Pricing T0 by file count worked for staging but missed two costs.** Reading the house format (about 45k) and loading three skills (scouting-report, dataviz, artifact-design, about 25k) were not priced. **Add a "house-format + skills" line: about 60k in when no template card exists, about 15k when one does.**
- **C-2 · Output came in under for the sixth time** (−19% at 0.5× the analogue). The gap is closing. **Next bid: 0.45×.**
- **C-3 · T1 input doubled** (45k bid → about 90k). The build ran three times, because B-1 and the HP-06 probe needed re-runs, and each run's output was read back. **Price 2 build iterations by default.**
- **C-4 · The defect line paid for itself.** It was priced at 13k and found three real defects: **O-25** (vert quantization), **B-1** (`GroupBy.first()` reading entry runners from later pitches), and **HP-18** (leaked loop state). Keep it.
- **C-5 · The 0.10 min / 1k-token rule with the 0.8 warm-sandbox multiplier held almost exactly:** 530k tokens → 53 min × 0.8 = 42 min predicted, and 42 actual.

## 5 · What this product makes possible next (the marketing half)

- **The recap series, cheaply.** The client's cell 114 lists the queue: Luzardo, Arraez, Nola, Painter, Wheeler. `career_frame` + `season_recap` + the chapter-driven dashboard builder make each one about 60% of this bid. The Luzardo recap is also SR-1's ratifying second use.
- **A persona ledger for every recap.** PA-1 is subject-agnostic. The thresholds are declared once, and each recap adds its own hypotheses. Over a season of recaps, the value stream accumulates a record of which kinds of actions leave signatures, which is the start of an evidence base for player development.
- **Arm vs role (VE-1) as a standing check** whenever a pitcher's usage changes (a starter to the pen, or a new leverage role).

## 6 · Ledger

Patch file: `uc_ledger_AI_PATCH_uc-pps-033-bowlan-2026-recap.md` (**PENDING PASTE**; the ledger still reads "next #25"). Next available after this UC: **#49 / `dp_uc49`** (pps next `uc-pps-034` · pos next `uc-pos-018`).
