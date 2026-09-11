# 01 · Strategy & Intake — `uc-pos-016-turner-whole-field-directional-001`

**Version: v1.1.0** — the v1.0.0 text below is unchanged; the v1.1.0 delta is the amendment section appended at the end of this file.

**Agents:** `use-case-validator`, `source-system-profiler`, `domain-steward-proxy`
**Visual-intake-agent:** skipped — the request arrived as text plus two referenced attachments that did not
reach this session (see G-1 below); no image was available to route through visual intake.

## The ask

> "My working theory is that Turner is pulling outside-zone pitches too often in 2026 rather than going the
> other way, and that this is a drift from 2023-2025 behavior. The DPO should lead the narrative analysis
> against the data rather than take this premise as given — if the data doesn't support it, say so."

Plus a named use case (`tt_whole_field_uc.md`, referenced as attached) and a hand-drawn sketch of the
intended visual layout (referenced as attached, described as a static facet grid: `facet_col=hit_direction`,
`facet_row=game_year`). Both attachments were flagged by the requester as raw inputs, not finished specs.

## Gap report

| # | Gap | Blocking? | Resolution |
|---|---|---|---|
| **G-1** | The two referenced attachments (`tt_whole_field_uc.md`, the sketch photo) do not exist anywhere reachable from this session — checked the connected `Agents for Data Products` folder (root, `data-products/`, `Claude outputs/`, `_contract_run_inputs/`), the `Python Scripts\MLB` folder (root, `.claude/`, `skills/`, `data/`), and the upload area. | **Non-blocking.** | The requester's prompt text is detailed enough to build a complete spec from directly (premise, corrections, grain, open decisions all stated explicitly). Treated as the intake document of record. Flagged for reconciliation once the actual files reach a future session. |
| **G-2** | The prompt references `sort_rank` as an existing, previously-defined function with a known bug ("valid only for a right-handed batter's field orientation"). No function by that name exists anywhere in the repo (`Baseball Functions.ipynb`, `dp_uc40_kernel.py` lineage, `cbp-spray_AI.md`, `run-spray-chart-60`) — only `hit_direction` does, which *is* found and reused verbatim. | **Non-blocking**, but material. | Per the mandatory Rule-1 grep step (`repo-search-before-declaring-kpi-new.md`), a `sort_rank` this build authors from scratch cannot honestly be called "the existing function, fixed" — it is **NEW-UC42**, built handedness-correct from the start rather than reproducing an unseen prior version. Documented in `03_governance.md`. |
| **G-3** | `hit_direction` requires a batted-ball classification, which by construction only covers plate appearances that end in a ball in play. "Pulling outside-zone pitches" as literally phrased could also be read as a swing-decision question (does he swing at more outside pitches at all) rather than a contact-outcome question (of the ones he puts in play, where do they go). | Non-blocking. | Scoped to the contact-outcome reading — hit_direction only exists post-contact, and the grain the requester specified ("sliced by hit_direction") presupposes a BIP population. Swing-decision framing (chase rate on outside pitches) is out of scope for this UC; noted as a natural follow-on. |

**0 blocking gaps.** Build proceeded.

## Premises stress-tested (falsify-before-describe, per `uc-pps-027`/`uc-pps-028` standing policy)

| Premise | Verdict |
|---|---|
| P1 — "Turner is pulling outside-zone pitches too often in 2026" | **Not supported.** 2026 outside-zone pull rate (39%, n=71) is statistically indistinguishable from pooled 2023-25 (43%, n=240; z=-0.58). |
| P2 — "...rather than going the other way" | **Not supported in the outside-zone population** (oppo rate flat: 35% vs 35%, z=+0.10). |
| P3 — "...and this is a drift from 2023-2025 behavior" | **Split verdict.** No drift found in the outside-zone population as claimed. A real drift **does** exist, but in-zone and in the *opposite* direction of the premise (more oppo, less pull). Reported per the P3-style split-verdict convention established on `uc-pos-014`/`uc-pos-012` (a bundled claim can be half-right). |

## Source-system fitness (F1-F4 gate)

| Check | Result |
|---|---|
| F1 source fitness | `data/phillies/phils_{2023..2026}.parquet` has every field needed (`hc_x`, `hc_y`, `zone`, `stand`, `p_throws`, `batter`, `type`, `events`); `phils_2026.parquet` current through 2026-09-09 |
| F2 empirical assumption-testing | Coordinate-convention assertion (median `loc_x` < 0 for Turner's Pull BIP, an RHB) run and PASSED before any figure was drawn |
| F3 grain supportability | Pitch-level → BIP is directly supported; no aggregation-then-disaggregation needed |
| F4 cache horizon | No refresh needed — the cached parquet already reflects yesterday's games |

## Declared DPO discretion

1. **Regular season only** for every rate (postseason BIP exist for 2023/2024 but not 2026 yet — an apples-
   to-oranges pooled baseline if included). Postseason volume: 218 D + 107 L + 33 F rows in the raw pull,
   entirely from 2023-2024; excluded from every published rate.
2. **Outside-zone vs in-zone split as the primary analytical cut**, rather than a single pooled pull/oppo
   rate — this is what the premise itself requires to be tested honestly (a pooled rate could hide an
   in-zone/out-of-zone divergence in either direction).
3. **Diagnostic-only, not a locked KPI** (see `02_engineering_design.md` and `00` §6) — a DPO call flagged
   for Kellen per his explicit request not to default silently on this point.

---

# v1.1.0 AMENDMENT — Strategy & Intake (`dp_uc42a`, 2026-09-10)

**Agents:** `use-case-validator`, `source-system-profiler`, `domain-steward-proxy`
**Visual-intake-agent:** engaged this round — the revision request arrived with a **pasted Plotly code cell**
as its primary visual input. Code, not an image, so it routed as a specification rather than a sketch; the
two attachments from the original intake are *still* missing (G-1 remains open).

## The revision ask, as received

> "I was fairly disappointed with the first iteration of this data product… Help me improve it based on the
> output of what was there and the additional context I am providing below. I am looking for something a
> little more interactive like the dashboards in the HTML. Explore ways to drive the narrative I am getting.
> Focus on delivering what is factually in the data, but try different methods for telling the story. **The
> spray chart that I requested was not a balls in play spray chart, it was a pitch map. This is a mistake on
> my part as the human-in-the-loop.** I expect that to be a part of the deliverable. As much as possible,
> iterate on top what was already complete and delivered in the prior iteration, particularly the governance
> deliverables. Help me animate this so that I can tell a story about a single-grain identified in the rug
> graph on the margins of the x-axis."

Plus a Plotly cell: `px.scatter` of Phillies player-seasons, `x=barrel_rate`, `y=runs_created`, `size=games`,
`color=df_color` (a Turner-2026 flag), `marginal_x='rug'`, hover on `woba`/`ops`/`plate_apps`/`hard_hit_rate`,
built from `nresults` / `runs_created` / `hard_hit_rate` / `barrel_rate` on `level=['player_name','game_year']`.

## Gap report (v1.1.0)

| # | Gap | Blocking? | Resolution |
|---|---|---|---|
| **G-1** | *(carried, unchanged)* `tt_whole_field_uc.md` and the sketch photo still have not reached a session. | Non-blocking. | Still open. `sort_rank` remains unreconciled against the DPO's own draft. |
| **G-4** | The spray-chart correction is **ambiguous as written**: "the spray chart I requested was not a BIP spray chart, it was a pitch map… I expect that to be a part of the deliverable" parses either as *(a)* "I mis-specified; I want the real spray chart" or *(b)* "what I got is a pitch map and I want to keep it." | **Non-blocking, resolved by asking.** | Put to the human DPO directly rather than guessed. He chose **both, cross-linked** — which is also the reading that cannot be wrong, and which turned out to enable `PM-1` (`02` §Design). Recorded because a guess here would have silently halved the deliverable. |
| **G-5** | The supplied cell's title asserts a claim — *"Trea is creating runs for a player of his Barrel Rate Profile."* Stress-testing it (below, P4) shows it does not hold for 2026 on a playing-time-normalized axis. | Non-blocking, **material**. | Title left off the shipped chart; chart titled for what it shows; the contradiction escalated (`00` §9.7-4) rather than either silently reproduced or silently dropped. This is the `uc-pos-008` "price both framings when a premise contradicts the log" rule applied to a chart title. |
| **G-6** | "Animate this" does not say *what varies across frames* — season, month, pitcher hand, and grain depth are all defensible. | **Non-blocking, resolved by asking.** | Put to the DPO with three options. He chose **season frames (2023→2026)** over a population→season→pitch grain descent. Recorded because v1.0.0's §7-3 escalation on exactly this axis had recommended *static*; the human overruled it, which is the escalation working, not failing. |

**0 blocking gaps.** Build proceeded.

## Premises stress-tested (v1.1.0 additions)

| Premise | Verdict |
|---|---|
| **P4 — "Trea is creating runs for a player of his Barrel Rate Profile"** (the supplied cell's own title) | **Not supported for 2026.** 53.5 runs created per 600 PA at a .064 barrel rate. Bohm 2026 creates 87.1 at a **lower** .060. Turner's own 2023/2024/2025 seasons produce 67.6 / 69.9 / 69.3 at 600 PA. The claim's apparent support in the original cell comes from plotting a counting stat against a rate — see `RC-1`, `03` §5. |
| **P5 — "the interesting story is the directional shift"** (implicit in the revision request) | **Half-supported.** The shift is real (v1.0.0, reproduced). `DC-1` shows it accounts for **20%** of the in-zone damage loss; 86% is per-direction production falling everywhere. The story is real and smaller than it looks. |
| **P6 — "pitchers are attacking him the same way"** (never asserted by the client; tested because the finding needs it) | **Supported in-zone, refuted out-of-zone.** `PM-1b` p = 0.51 in-zone; `PM-1c` p ≈ 1e−15 out-of-zone. This is the load-bearing new result. |

## Source-system fitness (delta)

| Check | Result |
|---|---|
| F1 | Additional fields required by the revision — `plate_x`, `plate_z`, `launch_speed`, `launch_angle`, `launch_speed_angle`, `bat_score`, `post_bat_score`, `des`, `description`, `events` — all present in `phils_{2023..2026}.parquet` at pitch grain. **0 missing.** |
| F1b | wOBA weights required by the governed `nresults` path: `wOBA and FIP Constants.csv`, merged **per season** on `game_year → Season` (the `mlb_data._apply_woba_weights` contract). Row-count assertion added so a duplicated constants row cannot fan the frame out — `dp_uc41` had to correct a pooled multi-season wOBA that had defaulted to 2026 constants. **PASSED.** |
| F2 | Coordinate convention re-asserted (median `loc_x` < 0 for Pull, > 0 for Oppo). Plate-side convention **derived empirically rather than assumed**: for this RHB, Pull median `plate_x` = −0.110 and Oppo = +0.231, so negative `plate_x` is inside. Zones 1/4/7 sit at ≈ −0.5 and 3/6/9 at ≈ +0.5, confirming the inside/outside labelling used in the zone decomposition. |
| F3 | Context pool grain (`player_name × game_year`) is directly supported. **Known hazard, disclosed:** `player_name` is a *name* key, and this repo has an open accent-fold defect (O-12) on name matching. It is used here only for the context pool's display grain — the subject is still locked by MLBAM id — so O-12 cannot affect any published subject figure. |
| F4 | No refresh needed; cache current through 2026-09-09. |

## Declared DPO discretion (v1.1.0)

1. **Context pool window = 2023–2026, not the full 2015–2026 cache.** A wider pool makes a denser rug, but
   pooling across eras imports the comparability problem `uc-pos-015` had to open a whole DQ dimension for.
   The UC's window is the Phillies era; the rug stays inside it. 65 player-seasons is ample rug density.
2. **50-PA floor on the context pool**, per the repo's confirmed batter floor (not 20 — that was checked, and
   `repo-search-before-declaring-kpi-new.md` records the correction).
3. **Governed KPI functions transcribed verbatim, defects included** (`get_stats`, `measure_calcs`, `mcgs`,
   `nresults`, `runs_created`, `hard_hit_rate`, `barrel_rate`), then each known defect **measured** against
   this build rather than assumed inapplicable — `out/dp_uc42a_defect_exposure.csv`. Two of the four bite,
   marginally, and are disclosed in the report §9.
4. **PM-1 split three ways** rather than reported as one whole-plate test. A pooled test here is significant
   (p = 2.6e-12) purely off the out-of-zone change and would have read as licence for an in-zone claim it
   does not support. Splitting it is the difference between the finding and its opposite.
