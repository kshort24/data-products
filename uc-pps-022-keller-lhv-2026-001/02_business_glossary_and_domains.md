# 02 — Business Glossary & Domain Terms
## UC #27 · `uc-pps-022` · Layer 1

Agent: `business-glossary-agent`

**Verdict: 0 new CDEs required. 1 new candidate term surfaced and routed, not defined.**

Every business term this product publishes already has an approved definition in the pps
glossary, established across UC#8 → UC#11 → UC#15 → UC#26. This UC introduces no new business
meaning. That is deliberate: a first-look report on an unfamiliar pitcher is exactly the
situation in which an agent is most tempted to invent a metric, and Governance Principle 1
exists to stop it.

---

## 1. Approved terms used (inherited, unchanged)

| Term | Business definition | Primary CDEs | Approved in |
|---|---|---|---|
| **Plate Appearance (PA)** | A completed batter-pitcher confrontation. Any pitch carrying a terminal `events` value other than `pickoff_1b` | `events` | UC#8 |
| **wOBA allowed** | Weighted on-base average charged to the pitcher, using season wOBA weights | `events`, `wBB…wHR` | UC#8 |
| **xwOBA on contact (xwOBAcon)** | Mean expected wOBA over balls in play only. The contact-quality read | `estimated_woba_using_speedangle`, `type` | UC#8; **grain corrected UC#26** |
| **Whiff Rate** | Swings that miss ÷ total swings | `description` | UC#8 |
| **Swinging-Strike Rate (SwStr%)** | Whiffs ÷ total pitches | `description` | UC#8 |
| **Chase Rate** | Swings at out-of-zone pitches ÷ out-of-zone pitches | `zone`, `description` | UC#8 |
| **In-Zone Rate** | Pitches in the rulebook zone ÷ total pitches | `zone` | UC#8 |
| **Putaway Rate** | Strikeouts ÷ pitches thrown in two-strike counts | `strikes`, `events` | UC#8 |
| **First-Pitch Strike Rate (FPSR)** | Non-ball outcomes on pitch 1 ÷ plate appearances | `pitch_number`, `type` | UC#8 |
| **Hard-Hit Rate** | Batted balls at ≥95 mph exit velocity ÷ balls in play | `launch_speed`, `type` | UC#8 |
| **Edge Rate** | Pitches within one baseball-width of the zone boundary ÷ located pitches | `plate_x/z`, `sz_top/bot` | UC#8 |
| **Out-of-Zone Called-Strike Rate** | Called strikes on out-of-zone pitches ÷ out-of-zone pitches | `zone`, `description` | UC#8 |
| **Air / Ground-Ball Rate** | Share of balls in play by `bb_type` | `bb_type`, `type` | UC#8 |
| **Chase-Up Rate** | Swing rate on pitches above the rulebook zone top | `plate_z`, `sz_top` | UC#8 |
| **Times Through the Order (TTO)** | Which pass through the lineup this PA falls in | `n_thruorder_pitcher` | UC#7 |
| **Attack Zone** | Heart / zone-edge / shadow / chase partition of the plate | `plate_x/z`, `sz_top/bot` | UC#11 |

---

## 2. Candidate term — routed, **not** defined

### SR-M1 · "Mayza Success Rate" / Quick At-Bat Rate

**Status: CANDIDATE — NOT APPROVED — PROVISIONAL. Do not treat as glossary.**
*(Per DQ-16, every mention of SR-M1 anywhere in this package carries the provisional banner,
including the numbers quoted below.)*

**Business intent as supplied by the DPO**, transcribed from Tim Mayza's *On Pattison*
interview: a two-pitch reliever's aim is a **quick at-bat**, defined as *getting to two
strikes or a ground ball within three pitches*.

The glossary agent will not approve this term, for a documented reason rather than a
procedural one:

> The supplied sentence admits **three materially different measurements**, and the supplied
> implementation computes a fourth reading that matches none of them exactly. Against
> Keller's 146 PA the candidates return **.411**, **.452**, and **.637** — a 22.6-point
> spread. A term whose value depends this heavily on an unstated reading cannot carry a
> single approved definition.

Per Governance Principle 1 the agent does **not** pick a reading. The disambiguation, the
reconciliation table, and a recommendation are packaged in `04_ §SR-M1` and returned to the
human DPO for ratification.

**Duplicate / conflict scan against the existing glossary:**

| Existing term | Overlap with SR-M1 | Conflict? |
|---|---|---|
| Putaway Rate (UC#8) | Both reason about two-strike counts | **No.** Putaway is conditioned *on* being at two strikes; SR-M1 measures *arriving* there |
| First-Pitch Strike Rate (UC#8) | Both are early-count efficiency measures | **No.** FPSR is pitch 1 only |
| QR-1…QR-3 quick-recovery family (UC#22 / `uc-pps-019`, provisional) | Naming collision risk on "Q…" prefixes | **Watch.** QR-* is provisional-pending-ratification per the Sánchez UC. Recommend SR-M1 keep the `SR-` prefix to avoid a namespace clash, and that both families be ratified in the same sitting |
| Air / Ground-Ball Rate (UC#8) | SR-M1's ground-ball leg reuses `bb_type == 'ground_ball'` | **No conflict; note a dependency.** If the `bb_type` mapping ever changes, SR-M1 and Air/GB Rate move together |

**Naming standards check:** `success_rate` as a column name is non-compliant with the pps
convention — it is unqualified and would collide with any other success construct in the
semantic layer. Recommend the ratified column be named **`qab_rate`** (quick at-bat rate)
with `sr_m1` as the KPI id.

---

## 3. Terms deliberately *not* created

| Tempting term | Why it was not created |
|---|---|
| "Stuff+ equivalent" / composite arsenal score | Requires a modelled population baseline that does not exist in this repo. Would be an invented CDE |
| "MLB-equivalent wOBA" | Would require a translation factor the repo does not have. Publishing one would be inference dressed as measurement |
| "Command grade" | `edge_rate` and `location_profile` already carry the underlying evidence. A letter grade adds opinion, not information |
| "Sinker effectiveness index" | The finding is real, but it is expressible entirely in already-approved terms (hard-hit rate, xwOBAcon, in-zone rate). No new term needed |

---

## 4. Gaps returned to the DPO

| # | Gap | Owner |
|---|---|---|
| GL-1 | SR-M1 has no approved definition; three candidate readings quantified in `04_ §SR-M1` | Human DPO |
| GL-2 | No approved AAA→MLB translation term exists in the pps glossary. Every future minor-league UC will hit this | Human DPO — candidate for its own UC |
| GL-3 | "Success rate" column naming is non-compliant; recommend `qab_rate` | Human DPO, at ratification |
