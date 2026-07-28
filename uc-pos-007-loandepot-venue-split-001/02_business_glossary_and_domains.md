# 02 — Business Glossary & Domain Rules
## `uc-pos-007` / `dp_uc27` · Layer 1 · Agents: `business-glossary-agent`, `domain-steward-proxy`

Governance principle 1 applies: **no agent in this pipeline defined a CDE's business meaning.**
Every term below is either (a) an already-approved term inherited from a prior UC, (b) a new term
drafted by `business-glossary-agent` and approved by the human DPO at intake, or (c) a candidate
term explicitly marked PROVISIONAL and routed to ratification.

---

## 1. Inherited approved CDEs — no change

These carry their existing enterprise definitions from `uc-pos-004` / `uc-pos-006` and are used
here without modification. Listed for completeness of the certification package.

| CDE | Definition (inherited) | Physical source |
|---|---|---|
| Plate Appearance | A completed batter-pitcher confrontation, excluding pickoff events | `events` not in {null, `pickoff_1b`} |
| At Bat | A plate appearance excluding walks, intentional walks, hit-by-pitch, sacrifice flies and sacrifice bunts | `events` exclusion list |
| Ball In Play | A pitch put into fair or foul territory by the bat and tracked | `type == 'X'` |
| Weighted On-Base Average (wOBA) | Linear-weights run value per plate appearance using season-specific FanGraphs constants | `wBB..wHR` summed ÷ `plate_apps` |
| Expected wOBA (xwOBA) | Statcast's exit-velocity/launch-angle estimate of wOBA on contact | mean of `estimated_woba_using_speedangle` |
| Hard-Hit Rate | Share of balls in play with exit velocity ≥ 95 mph | `launch_speed >= 95` ÷ BIP |
| Barrel Rate | Share of balls in play in Statcast's optimal EV/LA class | `launch_speed_angle == 6` ÷ BIP |
| EV90 | The 90th percentile of exit velocity over balls in play | `launch_speed.quantile(0.90)` |
| Chase Rate | Share of out-of-zone pitches swung at | swings where `zone > 9` ÷ `zone > 9` |
| Whiff Rate | Share of swings that miss | whiffs ÷ swings |
| Pitcher Handedness | The throwing hand of the pitcher in the confrontation | `p_throws` |

---

## 2. New CDEs required by this use case

Both drafted by `business-glossary-agent`, checked against the existing glossary for duplicates and
naming conflicts (none found), and **approved by the human DPO at intake**. Both are inheritable.

### CDE-1 · `VENUE_COHORT`

> **Business definition.** The classification of a plate appearance by the ballpark in which it
> occurred, for the purpose of venue-comparative analysis. For this product the domain is binary:
> `loanDepot park` (the Miami Marlins' home ballpark) and `All other MLB parks`.

| Attribute | Value |
|---|---|
| Domain | `loanDepot park` \| `All other MLB parks` |
| Physical derivation | `home_team == 'MIA'` → `loanDepot park`, else `All other MLB parks` |
| Grain | Pitch, rolled to plate appearance |
| **Known limitation** | Statcast carries no `venue_id`. `home_team` is a **club** identifier, not a **venue** identifier, so it misclassifies any game a club plays away from its own park while remaining the nominal home team. Correction applied for the single documented instance in this window (see DS-2, `01_ §4`) |
| Escalation | `metadata-mapper` classified this mapping as **ambiguous** and escalated it. Human DPO ruled: accept the proxy, publish the exclusion, and publish a parallel visiting-club cohort. Ruling recorded in `00_ §2` |
| Related | `VENUE_TENURE_CONTEXT` (below) |

### CDE-2 · `COMPETITION_LEVEL`

> **Business definition.** The level of professional competition at which a plate appearance
> occurred. Rates computed at different levels are not comparable and must not be pooled.

| Attribute | Value |
|---|---|
| Domain | `MLB` \| `MiLB` |
| Physical derivation | `home_team` present in the 31-code MLB club allow-list → `MLB`, else `MiLB` |
| Grain | Pitch |
| Rule | **MiLB rows are excluded from every published figure in this product.** They are not down-weighted, tiered, or footnoted — they are removed |
| Rationale | The local `nphl` frame concatenates Lehigh Valley and Clearwater affiliate pulls alongside MLB pulls. Minor-league Statcast tracking is lower fidelity, and the competition is not comparable. See `01_ §3.3` for the contamination that this rule removes |

### CDE-3 · `VENUE_TENURE_CONTEXT`

> **Business definition.** Whether the batter was employed by the home club of the venue at the
> time of the plate appearance. Distinguishes "performance at a ballpark as a visitor" from
> "performance at a ballpark as its home player," which conflate team quality, career stage and
> playing-time context with any true venue effect.

| Attribute | Value |
|---|---|
| Domain | `home club` \| `visiting club` |
| Physical derivation | batting team (`home_team` if `inning_topbot == 'Bot'` else `away_team`) equals the venue's club |
| Grain | Pitch |
| Why it exists | Without it, 45% of this product's Miami cohort is a career-stage artifact. See DS-1, `01_ §4` |
| Reusability | **High.** Every roster with ex-members of an opposing club has this exposure. Recommended for promotion to the enterprise glossary |

---

## 3. Candidate KPI terms — PROVISIONAL, not inheritable

Two new KPIs were required. Neither has an approved enterprise definition. Both are computed and
published **under a provisional banner**; no downstream use case may inherit them until ratified.
Full computational specs are in `04_ §3`.

| Term | Status | Why it is provisional |
|---|---|---|
| **VD-1 Venue Delta** | PROVISIONAL | The arithmetic is trivial and uncontroversial (a signed difference at a fixed grain). What is *not* settled is the **minimum-PA gate** at which a venue delta becomes publishable. This product used 40 PA (Miami) / 100 PA (elsewhere) — a house convention, not a derived threshold |
| **VD-2 Venue Signal Class** | PROVISIONAL | Two judgement calls with no approved basis: (a) the **scaling divisors** that put hard-hit %, barrel % and EV90 on a comparable footing (`0.06`, `0.035`, `2.5` — approximate population dispersions, eyeballed, not fitted); (b) the **classification boundaries** (`±.020` wOBA, `±0.30` composite). Different reasonable choices would reclassify borderline hitters |

**Ratification path.** Both terms belong to the same family as SR-M1 (`uc-pps-022`) and the QR-1..3
family (`uc-pps-019`): computed, useful, published under banner, awaiting a DPO decision. The
`business-glossary-agent` recommendation is to ratify VD-1 (with the PA gate set explicitly by the
DPO rather than by the build) and to hold VD-2 pending a fitted dispersion study across more than
one roster.

---

## 4. Domain rules registered against this product

Surfaced by `domain-steward-proxy` and recorded here so a future run inherits them rather than
rediscovering them. Full narrative in `01_ §4`.

| ID | Rule | Enforcement |
|---|---|---|
| DS-1 | A venue cohort that includes a hitter's own tenure with the venue's club is not a venue cohort. Publish both cuts | Design rule — two cohort frames built (`pooled_venue`, `pooled_venue_visitors`) |
| DS-2 | 2017-09-15/16/17 MIA-vs-MIL games were played at Miller Park (Hurricane Irma relocation). `game_pk` 492302, 492317, 492332 | Hard exclusion, tested by DQ-06 |
| DS-3 | loanDepot's playing surface changed across the window (CF sculpture removed after 2018; outfield walls moved in for 2020). A career-spanning Miami cohort is not one park | Park-era split computed and published; conclusion is that the apparent era effect is DS-1 in disguise |
| DS-4 | `pitches_per_pa` as total pitches ÷ PA slightly overstates the absolute level under a handedness filter; venue deltas are unaffected | Documented in the report caveats |
| DS-5 | Alcantara returned from Tommy John surgery in 2025; pre- and post-surgery arsenal should not be pooled without saying so | Career mix and 2025–26 mix reported separately |

---

## 5. Glossary deltas summary

| Action | Count | Terms |
|---|---|---|
| Inherited unchanged | 11 | Slash-line, contact-quality and discipline CDEs from `uc-pos-004` / `uc-pos-006` |
| New, approved, inheritable | 3 | `VENUE_COHORT`, `COMPETITION_LEVEL`, `VENUE_TENURE_CONTEXT` |
| New, PROVISIONAL, **not** inheritable | 2 | VD-1 Venue Delta, VD-2 Venue Signal Class |
| Duplicates or naming conflicts detected | 0 | — |
| Definitions inferred by a non-glossary agent | **0** | Governance principle 1 held |
