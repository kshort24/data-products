# 07 · Platform & Marketing: `uc-pps-036`

Agents: `cost-watchdog` · `token-economist` · `data-observability` (tripwires only)

## 1 · Tripwires (armed; re-run the build when one trips)
| # | Tripwire | What happens |
|---|---|---|
| T-1 | Another 2026 postseason appearance lands in `phils_2026.parquet` | v1.1.0: postseason ledger line only; rates unchanged |
| T-2 | 2027 status verified (CI-3) | v1.1.0: carry-in line updated |
| T-3 | E-2 (WB-1 upstream) or E-3 (NF-1 adds `launch_speed_angle`) lands | re-run HP-04 on the client frame; back-check UC48/49/51 |
| T-4 | **2027 season begins** | ranks superseded, not corrected |

## 2 · Cost audit (`cost-watchdog`)
| Hotspot | Cost | Recommendation |
|---|---|---|
| **House-format read (tokens)** | **~12k of content**: skill card 4.5 KB + ledger tail + BID skeleton (~3k) at T0, then 00–07/README/contract/dashboard/report skeletons (34.7 KB, ~9k) at T6. Counter step for the T0 skill load: ~9k | **Down from 70k (UC51) to ~12k.** The skill works; keep reading only the skeleton being written |
| **Prior-UC files opened (count)** | **7, all partial, 0 control-plane folders.** (1) `dp_uc51_kernel.py` header + CF-2b + IX-1 (inheritance by import) · (2) `dp_uc49_kernel.py` COLS/signatures via import (column projection) · (3) `dp_uc48_kernel.py` `house_percentile`, `runs_created` source · (4) `dp_uc44_kernel.py` `get_stats`/`measure_calcs`, `pitch_mix`…`hard_hit_rate` (wOBA basis, WB-1) · (5) `dp_uc50_kernel.py` `xwoba_pa` (WB-1) · (6) `dp_uc51_build_figs.py` lines 1–105 (house figure conventions) · (7) `uc_ledger_AI_PATCH_uc-pps-035…md` tail (patch format) | (1)–(5) are inheritance reads and unavoidable at ~1k each. (6) and (7) would be avoidable if the skill shipped `figs_shell.md` and `ledger_patch.md` skeletons |
| First-turn load (system prompt + attachment) | ~129k on the counter before any repo read | Outside the org's control; report T0 gross and net |
| EDA | ~2k (to file, 20-line summary) | Keep |
| Skill loads (dataviz, artifact design) | ~9k | Fixed line |
| Defect loops (WB-1, RQ-1…3) | ~25k | WB-1 and RQ-2 were worth every token; RQ-1/RQ-3 → guards now in code |

## 3 · Bid vs actual (`token-economist`)
Denominator: the **session token counter**, read at checkpoints. **The counter restarted at 15,000,000 when the award message arrived**, so the actual is the sum of two runs: bid turn (C0→C3) + build turn (C4→C-final). The in/out split is estimated from what was written. Minutes run from the first tool call to the last commit.

| Mark | Counter | Δ |
|---|---|---|
| C0 session start | 15,000,000 | — |
| C1 after skill + ledger tail | 14,838,293 | 161.7k (≈129k first-turn load) |
| C2 end of T0 | 14,808,457 | 29.8k |
| C3 BID filed | 14,795,398 | 13.1k (turn total 205.7k incl. reply) |
| C4 award (counter restarted) | 15,000,000 | — |
| C-final last commit | 14,737,248 (01:02 ET) | 262.8k (build turn) |

| Phase | Bid in+out | Bid min | Actual (counter) | Actual min |
|---|---|---|---|---|
| T0 Intake, recon, house format, carry-ins, id scan, BID | 205k | 8 | 205.7k | 8 |
| T1 Kernel + build + HP reproduction | 102k | 7 | 79.7k | 7 |
| T2 Figures + palette + render QA | 78k | 6 | 49.5k | 4 |
| T3 Dashboard + headless QA + Artifact | 60k | 4 | 38.5k | 5 |
| T4 Report + PDF | 32k | 2 | 8.4k | 2 |
| T5 Verification harness (incl. WB-1 restatement) | 49k | 3 | 28.9k | 3 |
| D Defect discovery (RQ-2/RQ-3 + PDF re-QA) | 16k | 2 | 9.7k | 1 |
| T6 Governance 00–07, README, contract, ledger, commits | 67k | 4 | 48.1k | 5 |
| Contingency | 40k | 3 | — | — |
| **Total** | **~649k (527k in / 122k out)** | **~39** | **~469k (205.7k + 262.8k)** | **35** |

**Credits at list ($10/M in, $50/M out):** bid ≈ **$11.40**; actual ≈ **$9.00 (−21%); tokens −28% vs bid, minutes −10%** (est. split ~360k in / ~108k out).

### Comparison with the other season recaps (same deliverable shape)
| UC | Subject | Total (counter) | Minutes | T0 / intake share | Report / dashboard / figures / new KPIs |
|---|---|---|---|---|---|
| UC48 `uc-pps-033` | Bowlan (RP) | 530k | 42 | 26% | PDF + dashboard |
| UC49 `uc-pps-034` | Luzardo (SP) | 545k | 45 | 46% | PDF + dashboard |
| UC51 `uc-pps-035` | Wheeler (SP) | 681k | 46 | 45% | PDF + dashboard |
| **UC52 `uc-pps-036`** | **Mayza (RP)** | **~469k (205.7k + 262.8k)** | **35** | **44% gross · 23% net of first-turn load** | 9 pp / 9 sections · 8 chapters · 10 figures · 3 KPIs (+RP-1 classifier, WB-1 companion) |

The comparison is like-for-like in shape. It is not like-for-like in input: this client supplied far more code (14 graded claims vs. 5–8 in earlier recaps), which pushed T1 and T5 up and should have made UC52 the most expensive recap. It came in cheapest, and the house-format skill is the main reason (70k → ~12k).

## 4 · Calibration findings (fourth instrumented recap bid)
- **C-1 · T0 from the counter:** held (bid 205k sunk = actual).
- **C-2 · Build tranches were over-bid by ~35%** (T1–T6 bid 404k vs actual 262.8k, −35%). With the house-format skill live, drop the per-tranche format-read allowance: T1 −20k, T6 −20k on the next recap.
- **C-3 (new) · Report with a narrative module:** T4 cost 8k when report and dashboard share one sentence source. Price T4 at ~12k when a narrative module exists.
- **C-4 (new) · Counter restarts per turn.** Record each turn's start and end reading; the actual is the sum of turns.
- **C-5 (new) · Comparison profile cap held:** 9/9 sections, 8/8 chapters, 10/10 figures, 3/3 KPIs. Nothing was cut to fit.

## 5 · What this product makes possible next (the marketing half)
- **Bullpen lefty set.** QA-1, BS-1 and DS-1 are subject-agnostic: a Strahm, Alvarado or Banks recap is a constants change plus narrative.
- **QA-1 as a bullpen approach board.** One call over `dp_uc52_quick_ab_house.csv` ranks every Phillies reliever on "ahead early".
- **WB-1 back-check (E-2):** a one-pass audit of UC48/49/51 for house-vs-Statcast basis comparisons.

## 6 · Ledger
Patch file: `uc_ledger_AI_PATCH_uc-pps-036-mayza-2026-recap.md` (**PENDING PASTE**). Next available after this UC: **#53 / `dp_uc53`** (pps next `uc-pps-037` · pos next `uc-pos-019`).

## 7 · Commit
MLB repo: `8c5849a` on `main`, 58 files, written with temp-index plumbing (`GIT_INDEX_FILE` → `write-tree` → `commit-tree`; ref written directly because `.git/refs/heads/main.lock`, `.git/index.lock` and `.git/HEAD.lock` are stale from an earlier session). The control-plane folder is not a git repository, so no commit there. **Note for the DPO:** those stale lock files will make your own `git commit` fail with "File exists" until they are removed. Six `tmp_obj_*` files under `.git/objects/` could not be unlinked (no delete permission); they are harmless.
