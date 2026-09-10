# 01 · Strategy & Intake — `uc-pos-016-turner-whole-field-directional-001`

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
