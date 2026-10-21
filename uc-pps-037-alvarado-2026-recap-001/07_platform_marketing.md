# 07 · Platform & Marketing: `uc-pps-037`

Agents: `cost-watchdog` · `token-economist` · `data-observability` (tripwires only)

## 1 · Tripwires (armed; re-run the build when one trips)
| # | Tripwire | What happens |
|---|---|---|
| T-1 | His 2027 status is verified (signing, or signs elsewhere) | v1.1.0: carry-in line updated; nothing recomputed |
| T-2 | E-2 lands (CM-D1 fixed upstream) | re-run HP-10 on the client frame; retire CM-1a; F9 unchanged |
| T-3 | E-3 lands (AB-1 thrown-pitch filter in K44 zone/usage) | re-run D5. The thrown-pitch zone drop is larger (41.4% vs 47.2%), so the verdict cannot move toward blip |
| T-4 | `phils_2026.parquet` is refreshed past 2026-10-01 | the build refuses; re-pin the anchor → v1.1.0 |
| T-5 | **2027 season begins** | ranks superseded, not corrected. If he pitches in MLB, DB-1 can be graded out of sample (2027 vs the same bars) |

## 2 · Cost audit (`cost-watchdog`)
| Hotspot | Cost | Recommendation |
|---|---|---|
| **House-format read (tokens)** | **~7k of content**: card + ledger tail + BID/00/03/05/07/README/contract/recap skeletons at T0, 01/02/04/06 at T6 | Holds the UC52 gain (70k → ~12k → ~7k). Keep reading only the skeleton being written |
| **Prior-UC files opened (count)** | **13, 0 whole prior folders.** UC52 control-plane folder: README, 00, BID, 07, ledger patch, kernel (full), build script (full), build_pdf, build_report, build_dashboard. MLB root excerpts: K49 `appearance_log`/`game_score`, K48 PA-1, `cumulative_metric.py` (header, METRICS, figure). One `03` grep each in uc-pps-028 and uc-pps-018 | The UC52 kernel and build (~29k) were inheritance reads. The three builders (~9k) would be avoidable if the skill shipped `recap_build_shell.md` (the `profile()` composition plus builder skeletons) |
| First-turn load (system prompt + attachment + tool schemas) | ~130k on the counter before any repo read | Outside the org's control; T0 is reported gross and net |
| Environment loss (ENV-3) | ~4k (two failed installs) | `TMPDIR` line added to E-5 |
| Skill loads (dataviz; artifact quickstart) | ~14k | Fixed line |
| Defect loops (CM-D1, AB-1, RK-2, render QA ×2, prose fact-check) | ~25k | All changed published numbers or wording; worth every token |

## 3 · Bid vs actual (`token-economist`)
Denominator: the **session token counter** (one turn; the counter did not restart because the award came inside the RFP). The in/out split is estimated from what was written. Minutes run from the first tool call (10:48 ET) to the last receipt (~11:29 ET).

| Mark | When | Counter | Δ |
|---|---|---|---|
| C0 | session start | 15,000,000 | — |
| C3 | BID filed (end T0) | 14,725,228 | 274.8k |
| C4 | T1 done (kernel, build, HP) | 14,669,535 | 55.7k |
| C5 | T2 done (10 figures, palette, render QA) | 14,624,843 | 44.7k |
| C6 | T3+T4 done (narrative, dashboard, QA, report, PDF, Artifact v1) | 14,558,316 | 66.5k |
| C7 | T5+D done (DQ, harness 163/163, AB-1/RK-2 fixes, Artifact v2) | 14,523,662 | 34.7k |
| C8 | 00–06, README, contract, ledger patch written | 14,489,002 | 34.7k |
| C-final | this file + reply (estimated) | ≈14,482,000 | ≈7k |

| Phase | Bid in+out | Bid min | Actual (counter) | Actual min |
|---|---|---|---|---|
| T0 Intake, recon, house format, carry-ins, env, profile, Rule-1, BID | 264k | 9 | 274.8k | 9 |
| T1 Kernel + build + HP reproduction + EDA | 85k | 7 | 55.7k | 8 |
| T2 Figures + palette + render QA | 55k | 5 | 44.7k | 5 |
| T3 Dashboard + headless QA + Artifact | 45k | 5 | ≈51k (of 66.5k, est. split) | 4 |
| T4 Report + PDF | 14k | 2 | ≈15k (est. split) | 2 |
| T5 Verification harness + DQ | 35k | 3 | ≈24k (of 34.7k, est. split) | 4 |
| D Defect discovery | 13k | 2 | ≈11k (est. split) | 2 |
| T6 Governance 00–07, README, contract, ledger | 55k | 5 | ≈42k | 7 |
| Contingency | 31k | 3 | — | — |
| **Total** | **~597k (501k in / 96k out)** | **~41** | **≈518k (≈445k in / ≈73k out)** | **≈41** |

**Credits at list ($10/M in, $50/M out):** bid ≈ **$9.80**; actual ≈ **$8.10 (−17%)**. Tokens −13% vs bid; minutes on bid. The RFP outcome: the winning bid was delivered under price and on time, with every published number independently verified.

### Comparison with the other season recaps (same deliverable shape)
| UC | Subject | Total (counter) | Minutes | T0 / intake share | Shape |
|---|---|---|---|---|---|
| UC48 `uc-pps-033` | Bowlan (RP) | 530k | 42 | 26% | PDF + dashboard |
| UC49 `uc-pps-034` | Luzardo (SP) | 545k | 45 | 46% | PDF + dashboard |
| UC51 `uc-pps-035` | Wheeler (SP) | 681k | 46 | 45% | PDF + dashboard |
| UC52 `uc-pps-036` | Mayza (RP) | 469k | 35 | 44% gross · 23% net | 9 pp · 8 ch · 10 fig · 3+ KPIs |
| **UC53 `uc-pps-037`** | **Alvarado (RP, tenure lens)** | **≈518k** | **≈41** | **53% gross · 37% net of first-turn load** | **10 pp / 9 sections · 7 ch · 10 fig · 2 new objects** |

UC53 covered six seasons where UC52 covered one. It ran one pre-registered argument card, and it found three new house defects (CM-D1, AB-1, RK-2). It came in second-cheapest. The T0 share rose because the UC52 kernel and build were read in full to inherit from them (cost audit above).

## 4 · Calibration findings (fifth instrumented recap bid)
- **C-1 · T0 from the counter:** held (bid 264k sunk vs 274.8k actual, which includes the BID itself).
- **C-2 · Build tranches still over-bid:** T1–T6 + D bid 302k (+31k contingency) vs ≈243k actual (−20%, −28% with contingency). Next recap: T1 −15k, T3 −0, T5 −10k, T6 −10k, contingency 5%.
- **C-3 · T4 with a narrative module:** held (bid 14k, actual ≈15k). Keep ~14k.
- **C-4 (new) · Single-turn award:** with no stop between bid and build there is no second first-turn load. That saved ≈130k against a two-turn run like UC52, whose counter restarted. Price single-turn RFPs without a second T0.
- **C-5 (new) · Inheritance reads belong in T0:** reading the parent kernel and build in full costs ~29k. Price it at T0 (+25k) whenever the parent is a different subject, or add `recap_build_shell.md` to the house skill.
- **C-6 (new) · Harness catches cost ~1k each:** five catches came out of T5 (RK-2, D-1 exposure, two harness-side corrections, AB-1 via DQ) for ≈11k of defect work. Keep D at ~13k.

## 5 · What this product makes possible next (the marketing half)
- **Offseason decision packs.** DB-1 is subject-agnostic: every arbitration-eligible or free-agent reliever gets the same eight bars, registered before the numbers, in one constants change.
- **Bullpen volatility board.** OD-1 over `house_pitcher_seasons` ranks every Phillies reliever on clean-outing and blow-up rates in one call.
- **House back-checks.** E-2 (CM-D1), E-3 (AB-1) and E-4 (RK-2) each define a one-pass audit across UC48–52.

## 6 · Ledger
Patch file: `uc_ledger_AI_PATCH_uc-pps-037-alvarado-2026-recap.md` (**PENDING PASTE**; UC52's patch is also pending). Next available after this UC: **#54 / `dp_uc54`** (pps next `uc-pps-038` · pos next `uc-pos-019`).

## 7 · Commit
None made (E-8). The control-plane folder is not a git repository. Files written in the MLB repo: `eda/dp_uc53/` (2), plus the contract and ledger-patch copies at the root. The MLB repo's stale `.git/*.lock` files (UC52 `07` §7) still block a plain `git commit`.
