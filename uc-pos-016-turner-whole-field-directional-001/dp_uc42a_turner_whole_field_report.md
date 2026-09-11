# Trea Turner — Whole-Field Directional Tendency · v1.1.0

**`uc-pos-016-turner-whole-field-directional-001` · UC #42 · build artifact `dp_uc42a` · Phillies Offense (`pos`) value stream**
**Parent: `dp_uc42` v1.0.0 (2026-09-10) · this revision 2026-09-10 · data as of 2026-09-09 · Human DPO: Kellen Short**
**Status: READY-CONDITIONAL (diagnostic tier) · verification 155/155 PASS, including 20 parent-reproduction checks and 46 narrative reconciliations**

---

## 0 · What changed since v1.0.0, and what did not

**The v1.0.0 finding is unchanged and was not re-litigated.** Every number v1.0.0 published was recomputed
from v1.0.0's own shipped extract and compared, row for row, against v1.0.0's own shipped CSVs before a line
of new work was added. All 20 of those checks pass. If this revision had quietly moved a parent number, the
harness would have failed rather than the report explaining it away afterwards.

Three things drove the revision, all client-initiated:

| # | Driver | What it produced |
|---|---|---|
| 1 | **Human-in-the-loop specification correction, self-declared by the DPO.** The chart requested in v1 as a "spray chart" was specified as, and built as, a **pitch map** (`plate_x`/`plate_z`). A true balls-in-play spray chart on field coordinates was the intent. | Both views now ship, **cross-linked on a shared `pitch_uid`**. Hovering a batted ball lights the pitch that produced it, and the reverse. The link is not decoration: it is where the v1.0.0 in-zone finding physically lives, and it made §3 below possible. |
| 2 | **Open decision #1 from v1.0.0 §7 answered.** "Static facet grid vs. animated frames" was flagged for the DPO's call rather than defaulted. He called it: **season frames**. | The static facet grid is superseded by a season-framed interactive dashboard (2023 → 2026) and a matching Plotly script for JupyterLab. |
| 3 | **A context grain supplied by the DPO** — a Plotly cell placing Turner-2026 in a population of Phillies player-seasons (barrel rate × runs created, rug on the x-axis margin). | The rug tick is the entry point of the narrative, and the cell's own construction turned out to need a correction of its own (§6, RC-1). |

**One defect in v1.0.0's own paperwork was found and is corrected here** — see §7, V-1. It is a
narrative-versus-receipt divergence, not an analytical error: v1's receipts and its report agreed; two of
its summary files did not agree with either.

---

## 1 · The verdict, before any explanation

| Question | Answer |
|---|---|
| Is Turner over-pulling **outside-zone** pitches in 2026, drifting from 2023–2025? | **No.** 2026 outside-zone pull rate is 39.4% (28 of 71) against a pooled 2023–2025 rate of 43.3% (104 of 240). Pooled two-proportion z = −0.58 — inside the noise band, and pointing the opposite way from the premise. Underpowered, not disproven. |
| Is there a real directional shift anywhere in the data? | **Yes, and it is in the zone.** In-zone pull rate 40.1% vs 47.5% pooled (z = −2.52); in-zone oppo rate 35.1% vs 29.5% (z = +2.04). |
| Did the pitchers move, or did the hitter? | **Inside the zone, the hitter.** The 2026 in-zone pitch-location distribution is statistically indistinguishable from pooled 2023–25 (χ² = 7.3, df 8, p = 0.51). Outside the zone the attack changed sharply (χ² = 72.8, df 3, p ≈ 1e−15) — and that is precisely the population where his batted-ball direction did **not** move. |
| Does the directional shift explain the down year? | **Mostly not — about a fifth of it.** In-zone total bases per ball in play fell .622 → .515. The directional mix change accounts for 20% of that gap; 86% is every direction producing less than it used to. |

**The premise, read literally, is not supported.** v1.0.0 said that and this revision does not soften it. What
v1.1.0 adds is that the finding which *is* supported turns out to explain much less of Turner's 2026 than its
size suggests — which is a more useful thing for the client to know than a louder version of the same headline.

---

## 2 · The narrative, in the order the evidence arrives

**One tick in the rug is a whole season.** The context population is 65 Phillies batter player-seasons from
2023–2026 at or above the repo's 50-PA batter floor. Turner's 2026 sits at a .064 barrel rate — mid-pack,
and *not* the lowest of his own four Phillies seasons (2025 was lower, at .058). On raw runs created his 2026
looks unremarkable. On PA-normalized run creation it does not: **53.5 runs created per 600 PA, the lowest of
his four Phillies seasons** (67.6 / 69.9 / 69.3 in 2023 / 2024 / 2025). The down year is real and it is not a
barrel-rate story.

**Inside that tick, the batted balls moved the other way.** Season by season, in-zone contact goes 47.3% pull
(2023) → 52.4% (2024) → 43.8% (2025) → 40.1% (2026), with oppo running the mirror image, 29.9% → 25.4% →
32.4% → 35.1%. 2026 is the low-pull, high-oppo extreme of the window. It is also not a monotonic trend: 2024
is his most pull-heavy in-zone season of the four, so 2026 is the outlier year, not the endpoint of a slide.

**The shift is whole-zone, not local.** Split the in-zone population by where the pitch was — three rows
(up/middle/down) and three columns (inside/middle/outside) of the Statcast zone — and pull rate is down in
**every one of the six slices**, by between 5.8 and 8.7 percentage points. No individual slice clears the
uncertainty band on its own; the aggregate clears it because the sub-effects all point the same way. A
location-specific cause would have concentrated. This one did not.

**And the pitchers were not the cause of it.** §3.

---

## 3 · The control: PM-1 attack-location stability

A batted-ball direction change means nothing on its own. If opponents changed where they threw, the ball
would go somewhere else without the hitter changing at all. So the attack plan is held up as a control:
Turner's 2026 pitch-location distribution against pooled 2023–25, as a χ² on the Statcast zone-share vector
plus a total-variation distance so the *size* of any shift is visible next to its significance.

It is run three ways on purpose. A pooled whole-plate test can be significant off an out-of-zone-only change
and then be read as if it licensed an in-zone explanation.

| Test | n 2026 | χ² | df | p | total-variation distance |
|---|---|---|---|---|---|
| **PM-1a** whole plate | 2,356 | 81.0 | 12 | 2.6e-12 | 5.7 pp |
| **PM-1b** in-zone, conditional on in-zone | 1,109 | 7.3 | 8 | **0.506** | 3.1 pp |
| **PM-1c** out-of-zone, conditional on out-of-zone | 1,247 | 72.8 | 3 | 1.1e-15 | 8.2 pp |

**The two halves disagree, and that is the finding.**

- **Inside the zone the attack held.** No detectable change in where he was pitched, and 3.1 pp of probability
  mass moved in total — yet his in-zone batted-ball direction moved 7.4 points of pull rate. The change is on
  the hitter's side of the ball.
- **Outside the zone the attack changed sharply**, and in a nameable way: **down-and-away (zone 14) is down
  3.7 pp and up-and-in (zone 11) is up 4.2 pp**; those two cells are essentially the whole shift. Yet his
  out-of-zone batted-ball direction did not move at all (|z| ≤ 0.58 on all three directions).

**So the premise looked at the population where the pitchers changed and he did not.** That is not a
rhetorical flourish; it is the cleanest available reading of the two tests side by side, and it is the reason
the null result in §1 should be read as *the premise is aimed at the wrong population*, not merely *the
sample was small* — although it is also small, and that caveat still stands.

**What PM-1 does not do.** It is a distributional test on pitch **location** only. It does not control for
pitch mix, sequencing, velocity, count, or who was on the mound. "The in-zone attack plan held" means
locations held, and nothing more than that.

---

## 4 · DC-1: how much of the down year the directional shift actually explains

Total bases per ball in play on in-zone contact — written `slg_bip`, named distinctly from slugging
percentage because the denominator is balls in play, not at-bats — fell from **.622** pooled 2023–25 to
**.515** in 2026. A two-way (Oaxaca-style) accounting split separates the part attributable to the
directional **mix** moving from the part attributable to each direction simply producing **less**:

| Component | Value | Share of the gap |
|---|---|---|
| Baseline (pooled 2023–25) | .622 | — |
| Mix effect — fewer pulls, more oppo, at 2023–25 production rates | **−.022** | **20%** |
| Rate effect — 2023–25 mix, at 2026 production rates | **−.092** | **86%** |
| Interaction | +.007 | −6% |
| 2026 actual | .515 | |

Per-direction, in-zone: pull `slg_bip` .766 → .632, straightaway .538 → .447, oppo .454 → .429. **Every
direction is down.** Going the other way more often costs him something, but four times as much of the damage
loss is that the contact itself is worth less wherever it goes.

**This is arithmetic, not causation.** It answers how much of the observed drop is bookkeeping-consistent
with the mix change and nothing else. It cannot say the mix change caused anything; it compares one season
against a three-season pool; and it is a decomposition of point estimates, so no uncertainty band is
attached to it. The interaction term is reported rather than folded into either side so the identity stays
visible and the reader can check that it closes.

---

## 5 · Data position — verified at build time, not assumed

| Check | Result |
|---|---|
| Source | `data/phillies/phils_{2023..2026}.parquet` — the repo's governed cache, read through the on-disk contract `get_phillies_data()` serves from |
| Freshness | `phils_2026.parquet` covers through **2026-09-09** |
| Entity lock | `batter == 607208`, confirmed by filter, never by name match (fourth confirmation across three Turner UCs) |
| Grain | Pitch-level; balls in play are `type == 'X'`; regular season only (`game_type == 'R'`) for cross-year rate comparability |
| Volume | **1,832** balls in play and **9,485** pitches, 2023–2026 — identical to v1.0.0, row for row |
| Coordinates | `hc_x`/`hc_y` → `loc_x`/`loc_y` via the governed `derive_loc()`; convention assertion passes (median `loc_x` for Pull is −66.3, and for Oppo is positive) |
| Zone authority | Statcast `zone`; `zone < 10` is in-zone; NULL zone excluded from **both** populations (the D-7/O-13 standard). 0 rows excluded for this subject |
| Handedness | `stand == 'R'` on 100% of rows — the L branch of `hit_direction` and `sort_rank` is implemented and documented but never exercised |
| Untracked BIP | 1 of 1,832 rows has NULL `launch_speed` (affects hard-hit rate only; never imputed — the sensor-boundary standard from `uc-pos-009`) |
| Context pool | 65 Phillies batter player-seasons at or above the 50-PA repo floor, on governed KPIs |
| Pitch grain | `pitch_uid` = `game_pk`–`at_bat_number`–`pitch_number`; unique across all 9,485 rows; the BIP frame is a strict subset |

---

## 6 · RC-1, and why the requested chart needed a correction of its own

The context cell supplied by the DPO plots **runs created** — a counting stat — against **barrel rate**, a
rate. Playing time then becomes the loudest signal on the y axis and the reader charges it to the x axis: a
full-time .060-barrel hitter always sits above a part-time .150-barrel hitter, and the chart reads as if
barrel rate buys runs.

The cell's own title — *"Trea is creating runs for a player of his Barrel Rate Profile"* — does not survive
the correction for 2026. At a .064 barrel rate he creates 53.5 runs per 600 PA. Bohm 2026, at a **lower**
.060 barrel rate, creates 87.1. Each of Turner's own 2023–25 seasons beats his 2026 on the normalized axis.
On the raw axis none of that is visible.

**RC-1 `runs_created_per_600` ships as a provisional KPI candidate, and the raw count ships beside it.** The
dashboard toggles between them. The counting stat is the right answer to *who drove in the most runs* and the
wrong answer to *who creates runs best for his contact profile*; neither is hidden. 600 PA is a convention,
roughly a qualified season — it rescales and never reranks within a fixed PA.

---

## 7 · V-1 — a defect in v1.0.0's paperwork, found by the parent-reproduction check

The parent-reproduction check compares v1.0.0's shipped CSVs against a recomputation from v1.0.0's own
extract. Those agree exactly. Reading across to v1.0.0's prose, two files do not:

| File | States | Shipped receipt says |
|---|---|---|
| `dp_uc42_turner_whole_field_report.md` §1, §5 | 43%, n = 240 | ✅ agrees |
| `01_strategy_intake.md` P1 | 43%, n = 240 | ✅ agrees |
| `README.md` "The finding, in one paragraph" | **36.7%, n = 228** | ❌ 43.3%, n = 240 |
| `00_dpo_orchestration_record.md` §5 | **36.7%, n = 228** | ❌ 43.3%, n = 240 |
| `uc_ledger_AI_PATCH_...md` | **36.7%, n = 228** | ❌ 43.3%, n = 240 |

The analysis, the figures, the significance test and the report were all right. Three summary files carried a
figure from an earlier draft that the final receipts superseded, and the ledger patch — the one artifact
meant to outlive the package — carried it too. Nothing about the verdict changes: 39.4% vs 43.3% is still
z = −0.58, still inside the noise band, still not support for the premise.

**Classification: V-1, narrative/receipt divergence. Severity: material, because the ledger patch would have
propagated it.** Corrected in this revision's README, `00`, and a reissued ledger patch.

**The generalizable fix, and it is now enforced rather than recommended:** the verification harness gained a
sixth family, **F — narrative/receipt reconciliation**. Every headline figure stated in this report's prose
and in the dashboard's markup is now recomputed from the shipped receipts and string-matched against the
narrative. A number that appears in prose but not in a receipt, or that disagrees with one, fails the build.
Recommend promoting this to a repo-wide practice — the receipts have been independently verified in this
repo for many UCs, but until now nothing checked that the prose agreed with them.

---

## 8 · What is provisional, and what is inherited

**New in v1.1.0 — provisional, unratified, do not reuse without DPO sign-off:**

| Object | Kind | Definition |
|---|---|---|
| `RC-1 runs_created_per_600` | KPI candidate | `runs_created / plate_apps × 600`. Guards the rate-vs-counting-stat confound (§6). |
| `PM-1 pitch_location_profile` + stability test | Control test | Per-season pitch-location profile plus the three-way χ² / total-variation stability test (§3). Split so an out-of-zone change can never be read as licensing an in-zone explanation. |
| `PM-2 zone_cell_direction_mix` | Diagnostic | In-zone batted-ball direction mix per Statcast zone cell. The bridge object between the pitch map and the spray chart. Cell counts are small by construction; not a KPI. |
| `DC-1 directional_value_decomposition` | Diagnostic | Two-way split of the change in `slg_bip` into mix effect, rate effect and interaction (§4). Point estimates only. |
| `slg_bip` | Metric | Total bases per ball in play. Named distinctly from slugging percentage because the denominator is BIP, not at-bats. |
| `pitch_uid` | Key | `game_pk`–`at_bat_number`–`pitch_number`. The join between the two linked views. |

**Carried forward from v1.0.0, still provisional:** `sort_rank(direction, stand)` — still pending the DPO's
reconciliation against his own draft (gap G-1); `WF-1 oppo_rate_ooz` / `WF-2 pull_rate_ooz` — still
diagnostic-only, still awaiting a second independent reuse; `P_THROWS_COLORS` / `MARKER_SIZE` — still
candidates for promotion to shared brand-center constants.

**Inherited verbatim, nothing re-derived:** `derive_loc` (`dp_uc40_kernel.py` PA-L1, from `cbp-spray_AI.md`
DQ rule 1) · `hit_direction` (`Baseball Functions.ipynb` cell 56) · `in_zone` (`zone < 10`, NULL excluded
from both populations) · `pooled_two_prop_z` (ST-1, `uc-pos-014`) · and, new to this revision but transcribed
as-is rather than reimplemented, `get_stats` / `measure_calcs` / `mcgs` / `nresults` / `runs_created` /
`hard_hit_rate` / `barrel_rate` from `Baseball Functions.ipynb` cells 13/15/17/19/31/52/58 — defects included
and disclosed (§9), not silently patched.

---

## 9 · Known kernel defects, measured against this build rather than assumed away

| Defect | Exposure in this build | Bites here? |
|---|---|---|
| **D-1** `hard_hit_rate`'s inner merge drops zero-hard-hit groups | 3 player-seasons in the 2023–26 context pool have ≥1 BIP and 0 hard hits | **Yes** — those rows keep a NULL hard-hit rate here rather than vanishing, because the context pool merges `how='left'`. Disclosed, not patched in the governed function. |
| **O-8** `hard_hit_rate` counts untracked BIP (NULL `launch_speed`) as not-hard-hit | 36 rows league-wide in the pool; **1** for Turner | **Yes, marginally.** Never imputed. |
| **D-7/O-13** `in_zone` counts NULL `zone` as in-zone | 0 Turner BIP rows have NULL `zone` | No — and NULL zone is excluded from **both** populations here regardless, per the standard. |
| **D-4** `nresults()` rounds to 3 dp before deriving `krate`/`bbrate` | Not consumed — this build takes `ops`/`woba`/`plate_apps` only | No |
| **O-14** `nresults().bbrate` is unintentional-BB/PA | Not consumed | No |

---

## 10 · Honest limits

- The out-of-zone test is **underpowered**: 71 balls in play in 2026 against 240 pooled. A true effect the
  size the premise supposed could exist here without clearing the band. Absence of evidence, not evidence of
  absence. §3 sharpens *why* the premise misses but does not repair the sample size.
- Turner is right-handed on 100% of these rows. The left-handed branch of `hit_direction` and `sort_rank` is
  implemented and documented but **untested by this build**.
- PM-1 tests pitch **location** only (§3).
- DC-1 is arithmetic on point estimates, one season against a three-season pool, and not a causal claim (§4).
- Season comparisons pool across parks and opponents. **No park or opponent-quality control is applied**;
  `uc-pos-007` (loanDepot) is this repo's precedent for how much that can matter.
- This remains a **diagnostic-tier** build. The harness is 155 checks — far more than v1.0.0's 33, and it now
  includes parent reproduction and narrative reconciliation — but it is still not the exhaustive
  independent-recompute harness a certification-tier hitter season gets (`uc-pos-014` ran 711 + 180). That
  gap is priced, not hidden.
- The two attachments referenced in the original intake (`tt_whole_field_uc.md`, a hand-sketch) **still have
  not reached a session**. The `sort_rank` reconciliation in v1.0.0's gap G-1 remains open.

---

## 11 · Certification

**READY-CONDITIONAL**, carrying v1.0.0's three conditions plus two of its own:

1. *(from v1.0.0)* The out-of-zone test is underpowered at n = 71 — stated, not hidden.
2. *(from v1.0.0)* `sort_rank`, WF-1 and WF-2 are unratified pending a second independent reuse.
3. *(from v1.0.0)* Not yet reconciled against the DPO's own draft and sketch, neither of which has reached a
   session.
4. **New.** `RC-1`, `PM-1`, `PM-2`, `DC-1` and `slg_bip` are single-use and unratified on the same standard.
   `PM-1` in particular is a control test that would benefit from being run on a subject where the attack
   plan *did* change in-zone, to confirm it detects what it claims to.
5. **New.** V-1 (§7) is corrected in this package, but the live MLB-repo `uc_ledger_AI.md` has never had the
   v1.0.0 patch pasted into it — so the erroneous figure has not propagated, and the reissued patch
   supersedes it. Paste the reissued patch, not the original.

**Publish recommendation: publish internally now.** Privacy remains LOW (public on-field performance data for
a public figure); no external surface is proposed.
