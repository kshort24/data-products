# 02 — Business Glossary & Domain Tagging

**Agents:** `business-glossary-agent` → `metadata-mapper` → `data-tagger` → `privacy-watchdog`
**Layer 2 — Design (Governance track)** · UC #32 · `uc-pos-008` · `dp_uc31`

---

## 1. Governance principle 1 compliance

> *No agent may define or infer a CDE's business meaning.*

Every term used in this product falls into exactly one of three classes:

| Class | Count | Rule applied |
|---|---|---|
| **Locked-inherited** | 21 | Definition carried byte-identical from a prior ratified UC. Not restated, not reinterpreted |
| **Report-local (provisional)** | 7 | Newly composed **from existing physical CDEs**. No new business meaning invented — each is an arithmetic composition of already-defined elements. Returned to the DPO as promotion candidates |
| **Physical-only** | 18 | Statcast source fields with vendor-defined meaning. Mapped, never redefined |

**Zero terms were inferred.** Where a definition was needed and unavailable, the work stopped and the gap was returned (none occurred in this UC).

---

## 2. Locked-inherited terms

Carried from `dp_uc20` (SC-1, SC-2), `dp_uc24` (RF-1, RF-2) and the shared Baseball Functions kernel. **Not redefined here.**

| Term | Origin | Used for |
|---|---|---|
| Plate Appearance (locked basis) | Baseball Functions | Season line denominators |
| At Bat | Baseball Functions | BA / SLG denominators |
| Batting Average, On-Base Percentage, Slugging, OPS | Baseball Functions | Report §1 |
| wOBA (season-weighted) | Baseball Functions + `wOBA and FIP Constants.csv` | Throughout |
| xwOBA / xBA | Statcast `estimated_*_using_speedangle` | Regression argument |
| ISO | `slg − ba` | Report §1 |
| Strikeout Rate, Walk Rate | Baseball Functions | Throughout |
| Swing, Whiff (event lists `SWINGS`/`WHIFFS`) | Baseball Functions | Discipline panel |
| Chase Rate, Z-Swing, Z-Contact, O-Contact, Zone Rate | `dp_uc20` | Report §2 |
| Barrel (`launch_speed_angle == 6`) | Statcast | Contact quality |
| Hard-Hit (`launch_speed >= 95`) | Baseball Functions | Contact quality |
| Sweet Spot (`launch_angle` 8–32) | Baseball Functions | Contact quality |
| xwOBAcon | `dp_uc24` | **Load-bearing** in report §4 |
| Pitch Group (`PITCH_GROUP` map) | `dp_uc24` | AR-3 grain |
| Pulled / Oppo / Pulled-Air | `dp_uc24` | Spray receipt |
| SC-1 wRC / wRC+ approximation | `dp_uc20` | Report §1 context |
| SC-2 Pitches per Plate Appearance | `dp_uc20` | **Tests the "wild at-bats" hypothesis** |
| RF-1 Season-to-date trajectory | `dp_uc24` | Receipt `b5` |
| Bat Speed, Swing Length, Attack Angle, Fast-Swing Rate | `dp_uc24` | Report §2 |
| RE24 (via `delta_run_exp`) | Statcast | **AR-6 foundation** |

---

## 3. Report-local terms introduced (provisional — DPO ratification required)

Each is composed from locked or physical elements. Formal computational specs are in `04_architecture_and_kpi_specs.md`; this section fixes **business meaning** only.

### AR-1 · Two-Strike Survival Rate (TSSR)
**Business meaning.** The share of a hitter's two-strike plate appearances that do not end in a strikeout.
**Why it exists.** "Collects hits with two strikes" conflates two abilities: avoiding the strikeout, and doing damage afterwards. TSSR isolates the first. It answers *how often does he stay alive*, which is the ability that transfers across contexts.
**Composed from.** `strikes` (physical), Plate Appearance (locked, strict basis), Strikeout (locked).
**Promotion candidate: STRONG.** Roster-general, cheap, and it discriminates sharply between hitters on this team (.430 to .901).

### AR-2 · Two-Strike Damage Line (TSDL)
**Business meaning.** The complete slash line, wOBA, xwOBA and RE24 per plate appearance restricted to plate appearances that reached two strikes.
**Why it exists.** The necessary counterpart to AR-1. Surviving is not the same as producing. Reported together so a high survival rate cannot be mistaken for value.
**Composed from.** All locked slash components, restricted by the AR-1 population.

### AR-3 · Damage Profile by Pitch Group × Hand (DPGH)
**Business meaning.** Actual production (SLG, ISO, wOBA) set beside deserved contact quality (xwOBAcon, exit velocity, hard-hit rate) at the grain of pitch group crossed with pitcher handedness.
**Why it exists.** The consumer asked which pitches and which handedness he can slug. Slugging alone answers the question misleadingly at these sample sizes — the pairing with xwOBAcon is what makes the answer trustworthy.
**Grain caution (governance-relevant).** Slash-line denominators attribute the plate appearance to the pitch that **ended** it; contact-quality columns use **all** balls in play against that group. These are different populations and the two column families must not be arithmetically combined.
**Composed from.** Pitch Group (locked), `p_throws` (physical), locked slash components, xwOBAcon (locked).

### AR-4 · Scoring-Position Conversion Rate (SPCR)
**Business meaning.** Of the runners already standing on second or third when a hitter came to the plate, the share who scored on that plate appearance.
**Why it exists.** RISP batting average answers "did he get a hit", not "did the run score". SPCR is measured **per runner**, so a two-run double counts twice and a solo home run counts zero — the batter was never a runner in scoring position.
**Composed from.** `on_2b`, `on_3b`, `bat_score`, `post_bat_score`, Home Run (locked).
**Known limitation.** Attributes the run to the batter without apportioning credit to the runner's speed, the defence, or a subsequent error. It is a *conversion* measure, not a *value* measure.
**Promotion candidate: STRONG.** Roster-general and directly decision-relevant to lineup construction.

### AR-5 · Lineup Slot Opportunity Profile (LSOP)
**Business meaning.** The characteristics of a batting-order slot **independent of who occupies it** — plate appearances per game, and the share arriving with the bases empty, with men on, and with a runner in scoring position.
**Why it exists.** The consumer's hypothesis ("cleanup gets the most opportunities with men on") is a claim about the *slot*, not the *hitter*. LSOP tests it directly. It is confirmed: slot 4 leads at 47.8% men-on and 1.06 RISP PA per game.
**Composed from.** Derived batting slot (see 04 §3), base-state fields, game count.

### AR-6 · Slot-Projected Run Contribution (SPRC)
**Business meaning.** The run-expectancy contribution a specific hitter would be projected to add over a season if he occupied a specific lineup slot, given that slot's observed opportunity mix and his own observed production in each base context.
**Why it exists.** This is the decision the consumer asked to be modelled.
**Composed from.** AR-5 weights × locked RE24 per plate appearance by context, scaled by slot plate appearances per game × 162.
**Explicit non-claims.** (a) It does not model the feedback of re-ordering on the opportunity mix. (b) It is not a wins projection. (c) Scenario totals are pair sums, comparable only within a framing.

### AR-7 · Table-Setting Value (TSV)
**Business meaning.** Reported as **two separate quantities that are never summed**: (a) *supply* — on-base events a hitter would produce per game in a given slot; (b) *realisation* — what the two following slots historically extract per runner.
**Why it exists.** The consumer's "sets the table" intuition. A hitter's value at the top of the order is partly a function of who bats behind him, which no hitter-level metric captures.
**Units warning (governance-relevant).** The combined column is runners × a per-runner conversion rate, so it carries units of runs — but the conversion rate is estimated per runner *in scoring position* and applied to *all* baserunners. It is therefore an **upper bound** and is labelled as such everywhere. **It must not be added to AR-6**, which already values the batter's own plate-appearance outcomes; summing them double-counts.

---

## 4. Metadata mapping (`metadata-mapper`)

Physical → business term classification for all elements reaching an output.

| Classification | Count | Notes |
|---|---|---|
| **Exact** | 24 | Direct 1:1 to a locked or physical term |
| **Composed** | 7 | The AR-* family — arithmetic over exact mappings |
| **Ambiguous** | 2 | `estimated_woba_using_speedangle` (population varies by event type — §01 3.1); `launch_speed` (populated on fouls — §01 3.2). **Both surfaced to DPO, both mitigated in build, neither silently resolved** |
| **Unmapped** | 0 | — |

No new glossary terms were created by the mapper.

---

## 5. Classification & tagging (`data-tagger`)

| Dimension | Value |
|---|---|
| Domain | Baseball Operations → Player Evaluation |
| Subject area | Position-player offensive performance; lineup construction |
| Data product | `uc-pos-008-arraez-acquisition-001` |
| Value stream | `pos` |
| Sensitivity | **Internal — Restricted** |
| Retention | Retain through the 2026 season; supersede at closure re-read |
| Owner | Human DPO (Kellen Short) |

---

## 6. Privacy assessment (`privacy-watchdog`)

**Verdict: no PII beyond public identifiers. Classified Internal — Restricted. Not cleared for external publication.**

| Check | Finding |
|---|---|
| Direct PII | None. MLBAM player ids and names are public |
| Quasi-identifiers | None beyond publicly reported game events |
| Re-identification risk | Not applicable — subjects are public figures, performance is publicly broadcast |
| Sensitive combinations | **Yes — non-privacy sensitivity.** The product contains (a) a regression forecast against a current employee's headline results, (b) a comparative judgment ranking eleven current employees on two-strike and scoring-position performance, and (c) an explicit statement that the acquisition "is not defensible as an upgrade in raw offensive value" |
| Health / medical | None |
| Contract / compensation | None |

**Restriction rationale.** (b) and (c) are the binding constraints. Player-vs-player rankings and an acquisition-value judgment are ordinary internal analysis and ordinary external controversy. **Gate 5 satisfied for internal use; external publication blocked.**

**Handling note for consumers.** The persona guidance in `06_consumer_success.md` is written to be shareable with the hitting coach and manager. The comparative tables in report §3 and §5 should be presented as team-context framing, not as a leaderboard.
