# 00 · DPO Orchestration Record: `uc-pos-018-lineup-vs-sale-wc-g1-001`

**UC #50 · contract `uc-pos-018` · build `dp_uc50` · v1.0.0 · delivered 2026-09-29 ET (pre-game)**
Value stream: Position player / offense (`pos`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL** · independently verified **372 / 372** · DQ **15 PASS / 2 WARN / 0 FAIL** · 13 figures, render-QA'd

---

## 1 · The ask and how we framed it

Four notebook cells and a prompt. The cells are a Sale sketch and three index cards (Turner, Schwarber, Harper) at different grains and time slices: 2026 vs LHP, career vs Sale, and Sale against every lefty a hitter has faced. The prompt asks for the same rigor on the other six hitters, in batting order, plus one consolidated lineup scorecard with Sale on it.

The organization read it as **four jobs**:

1. **Ship before first pitch.** The game started at 2:00 p.m. ET, about 70 minutes after intake. The consumables (notecard, nine cards, PDF) went out first. Receipts, harness and paperwork followed. The ordering is logged as D-1 in the BID.
2. **Grade the three existing cards before writing six new ones.** Schwarber reproduced exactly. Turner's three KPIs held but had moved with the data. Turner's narrative did not hold as worded. Harper's ranking held, but the number is .190, not .100 (HP-01…HP-12).
3. **Give every hitter the visual his story needs.** Five chart types across nine cards: direction by pitch location (Turner), spray vs Sale (Schwarber), rank among lefties (Harper), vs-LHP by season (Bohm, Realmuto), and pitch group vs Sale's usage (Hill, De La Cruz, Stott, Sosa). There is no template chart.
4. **Tie every plan to what Sale actually throws that hitter.** Sale's 2026 arsenal by batter side is the hinge of the product: slider-sinker to lefties, four-seam-slider(-changeup) to righties. Every card's *Plan* line cites it.

## 2 · Delivery plan (departments actually engaged)

| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 6 gaps (1 blocking: the lineup ids, resolved from the log). Graded 12 client claims |
| | `source-system-profiler` | Id scan of all opponent files. Sale's pitches sit in `sale.parquet`, `atlp26` and 17 batter-keyed files. The lineup sits in 4–13 sources each. Sale 2025 is partial |
| | `domain-steward-proxy` | Carry-ins: game time/network, Sale named starter, batting order (client). Flagged the MV-1 wOBA/ROE difference |
| | `business-glossary-agent` | Glossed LR-1 ("Sale rank"), HL-1 thirds, XW-1 vs xwOBAcon, THIN |
| Engineering Design | `data-architect` | BF-1: one pass, one pitch-grain frame for nine batters + one pitcher, precedence-deduped |
| | `eda-agent` | Found the lefties' 2026 collapse vs Sale (1 hit in 24 PA), the flat TTO, Bohm's every-season LHP line, Realmuto's zero fastball barrels, Sosa's chase |
| | `join-validator` | Only merges are 1:1 on level keys (IC-1); the harness rebuilds without the kernel |
| | `metadata-mapper` | `batter` cannot be a `get_stats` level (D-50-1); `player_name` is the batter in batter-keyed pulls → id lock only |
| | `dashboard-specifier` | Card layout (header, 5 tiles, lede/Sale/Plan, one chart); notecard layout (`02` §5) |
| Governance | `kpi-calculator` | XW-1, HL-1, LR-1, TT-1, IC-1, NF-2 specified before code (`03` §2) |
| | `technical-lineage-builder` | Column-level lineage (`03` §3) |
| | `privacy-watchdog` / `data-tagger` | Public performance data; no health, no availability inference. **Internal** |
| | `version-controller` | v1.0.0; anchor pinned to Game 162 (2026-09-27) |
| Engineering Build | `data-engineer` | Build on the laptop VM (pyarrow/scipy/plotly in `/tmp`); PDF in cloud on receipts |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` | 17 rules, 0 FAIL, 2 designed WARNs |
| | `certification-agent` | Harness A–G, 372 checks, independent code path |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` / `product-narrator` | Nine ledes, the notecard, reading paths |
| Platform & Marketing | `cost-watchdog` / `token-economist` | Bid vs actual, calibration, tripwires |

**Not engaged:** `machine-learning-engineer` (no model), `semantic-modeler` (no cross-UC metric layer), `data-observability` (point-in-time game card; tripwires in `07`).

## 3 · Governance gate checks

| Gate | Result |
|---|---|
| G1 · Entities locked to MLBAM ids | **PASS**: nine batters resolved from the Phillies log (DQ-03), Sale 519242 (DQ-04). Names used only in NF-2 |
| G2 · Rule-1 search before anything new | **PASS**: xwOBA per PA (0 hits; only `xwobacon` exists → XW-1 new), location thirds (PM-2 zone cells exist, in-zone only → HL-1 new), LHP rank (client code only → LR-1), TTO (0 hits → TT-1). Directional family found (UC46) → imported |
| G3 · Locked KPIs inherited, not re-derived | **PASS**: `dp_uc44` `a2c119096db2`, `dp_uc46` `a45ac9a76395`, `dp_uc48` `0f63857a1032`, `barrel_rate.py` `6282f090394a`; asserted at build (DQ-15) |
| G4 · No re-derivation of existing work | **PASS**: the client's three cards are reproduced and graded, not redone. `uc-pos-001` is the layout parent |
| G5 · Small samples print denominators | **PASS**: PA on every line; THIN under 10 PA; FL-1 asterisk under 25 BIP (DQ-14); harness G |
| G6 · Superlatives name their population | **PASS**: "toughest" = LR-1 rank with n printed; "lowest in 12 seasons" asserted in code |
| G7 · Carry-ins labelled, never computed on | **PASS**: 4 in the freshness manifest. "Cleared the bases" is kept out of the product (harness G) |
| G8 · Every published number reconciles to a receipt | **PASS**: family F, 101 checks, every 3-decimal figure and percent in every lede |
| G9 · Client claims graded, not overwritten | **PASS**: 12 HP rows keep his words beside the governed value |
| G10 · Anchor pinned | **PASS**: the build refuses any regular-season anchor other than 2026-09-27 |

## 4 · Capability fulfilment

| Asked for | Delivered as | Where |
|---|---|---|
| Continue the rigor for six hitters, in order | Six new cards, same grains (2026 vs LHP, career vs Sale, LHP rank) plus pitch groups, location thirds, last 30 days | `out/dp_uc50_card_4…9_*.png`, report §3 |
| "Determine the narrative and visuals for each" | Nine tags and ledes; five chart types chosen per story | `dp_uc50_narratives.py`, `02` §5 |
| A card for each Phillies batter | Nine, including the client's three, governed | report §3 |
| Consolidated scorecard incl. Sale | One-page notecard (Sale strip + nine rows + the rule) and a lineup table | `out/dp_uc50_fig4_lineup_notecard.png`, report §2 |
| Sale 2026 from `atlp26` | The client's three Sale plots governed + arsenal by side + TTO + vs PHI | `out/dp_uc50_fig2/3_*`, report §1 |
| Data-plane functions and standards | Import-by-hash of the locked kernels; `(level, df)` signatures; new objects specified first | `dp_uc50_kernel.py`, `03` |
| Scouting-report skill inspiration | Bottom line first, data-window box, PA everywhere, single attack rule, candid caveats | report |
| Receipts 00–07 + bid with tokens and time | This folder | here |

## 5 · The finding, in the DPO's words

Sale is the same pitcher he was in 2024, with 1.3 more mph on the four-seam. The lefties at the top of this order can't be the plan: Schwarber and Harper are a combined 1-for-23 against him this year, and he is the toughest of the 20 lefties Harper has seen 20+ times. The offense has to come from the right side, where the career line against him is .278 wOBA. Bohm is the best bet on the card (.365 in 25 PA, and he's hit lefties every season he's played). Sale does not fade the third time through, so there is no reason to wait. The rule on every card is the same: make the slider a ball, and make the four-seam a strike.

## 6 · Where the organization argued with itself

**Turner's narrative.** `product-narrator` wanted to keep the client's line, *too many pulls on pitches away from him*. The `certification-agent` ran HL-1: on away-third pitches he pulls 31% and goes oppo 37%, and the away balls are weak (.241 wOBA) whichever way they go. **Resolution:** HP-05 reads *DOES NOT HOLD as worded*. The card keeps the client's instinct (*hit it where it's thrown* is sound) and points to what holds: the spin (breaking .218, changeup .212) and the away changeup Sale throws righties.

**"Jump on Sale early."** The client's notebook (cell 139) says getting to Sale early is huge. `eda-agent`: his wOBA by time through the order is .262 / .254 / .258. **Resolution:** the product says getting to him early is no easier than later. It also prints what does change the third time (the HR rate doubles, 1.2% → 2.4%). It doesn't claim early runs matter less. It only says Sale isn't easier early.

**Sosa is hot.** `consumer-onboarding-agent` wanted to lead with the last 30 days (.464 wOBA). `eda-agent`: on 37 PA with a .323 xwOBA. **Resolution:** both numbers print, and the lede leads with the Sale book (23 PA, .218) and the chase that explains it.

**Hill's double.** The client's notebook says it "cleared the bases" off Sale on 9/11. The log shows a 104.3-mph double on a four-seam in the 2nd inning. **Resolution:** the card says what the log shows. Runs are not computed in this build, so "cleared the bases" stays a carry-in in the client's words and out of the product (harness G).

**Which wOBA.** The harness first recomputed wOBA from Savant's `woba_value` and missed by up to .029 (Sosa). The cause is that Savant credits reached-on-error at single value; the house (FanGraphs weights over house PA) does not. **Resolution:** house wOBA stays published because it is the client's number and the repo's standard. The gap is measured per scope in `out/dp_uc50_method_variance.csv` (MV-1).

**De La Cruz's card.** 41 PA against lefties in 2026 and 9 against Sale. `certification-agent` refused a 2026-only narrative. **Resolution:** the story is built on the pooled 2024–26 split (66 PA vs breaking balls), and THIN is printed on the Sale line.

## 7 · Escalations to the human DPO

1. **E-1 · D-50-1, `get_stats` cannot take `batter` as a level.** `measure_calcs` renames a `batter` column to `pitches`, so `nresults(['batter'], df)` raises `KeyError`. Worked around with a display key. Fix upstream (non-breaking: rename only when `batter` is not in `level`).
2. **E-2 · O-26, second exposure.** A `nphl` name filter drops 10 of Sale's 2026 pitches (469 all-years) that `get_nphillies_data()` deduped into earlier batter-keyed files. Same fix as `uc-pps-034` E-3.
3. **E-3 · Ratify LR-1 and XW-1?** LR-1 is the client's Harper cut as a function (`lhp_rank`). XW-1 is the house's first PA-denominated xwOBA (the house had only `xwobacon`). Both are used on every card.
4. **E-4 · MV-1 policy.** House wOBA ≠ Savant `woba_value` whenever a hitter reaches on error. Recommend documenting it in the glossary as a deliberate choice.
5. **E-5 · Refresh `sale.parquet`.** It ends 2025-05-23. Harmless here (the profile is 2026-only), but any Sale career split is short.
6. **E-6 · Ledger.** Rows #25–#50 are pending pastes into `uc_ledger_AI.md`.
7. **E-7 · D-1, deadline bids.** Accept "reserve, build, bid mechanically, reconcile" as the protocol when intake-to-deadline is under 90 minutes?

## 8 · Publish recommendation

**READY-CONDITIONAL. Internal: manager, hitting coach, advance meeting, broadcast/content.**

- **C1** Head-to-head samples are small (27 PA max). THIN lines are directional only.
- **C2** Pitch groups are a proxy for Sale's pitches, not a similarity model.
- **C3** Carry-ins (batting order, game time, Harper's quote, "cleared the bases") are the client's or published reporting, never computed on.
- **C4** New objects (XW-1, HL-1, LR-1, TT-1, IC-1, NF-2) are provisional.
- **C5** Sale 2025 is partial in the repo; nothing published depends on it.
