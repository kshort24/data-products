# 04 — Architecture & KPI Specifications

**Agents:** `data-architect` → `kpi-calculator` → `eda-agent`
**Layer 2 — Design (Engineering track)** · UC #32 · `uc-pos-008` · `dp_uc31`

> **Governance principle 2.** Nothing in this document was written after the build. Every KPI below was specified — plain language, formula, grain, population, source CDEs, edge cases — **before** it appeared in any output.

---

## 1. Architecture

### 1.1 Shape

A **flat-file, single-script build** in the `dp_uc8` → `dp_uc11` → `dp_uc24` lineage. No warehouse, no orchestration; the data plane is local parquet.

```
data/opponents/arraez.parquet ─┐
data/phillies/phils_2026.parquet ─┼─> dp_uc31_arraez_acquisition_read.py ─> out/*.csv, out/*.png
wOBA and FIP Constants.csv ────┘                    │
                                                     ├─> dp_uc31_build_pdf.py       ─> report.pdf
                                                     └─> dp_uc31_build_dashboard.py ─> dashboard.html
                                    dp_uc31_verification.py ──(independent re-read)──> verification_results.csv
```

**Single source of truth.** The build script is the only place a number is computed. The PDF and dashboard renderers read CSV receipts and format them. The verification harness re-reads the **raw parquet** and never imports the build module.

### 1.2 Grain design — the central decision

Three grains coexist. Choosing them explicitly is what makes the AR-* family coherent.

| Grain | One row = | Used by | Why |
|---|---|---|---|
| **Pitch** | one pitch | discipline, contact quality, two-strike economy | Swing decisions are per-pitch events |
| **Plate appearance** (`pa_frame`) | terminal pitch of a PA | AR-1…AR-4, AR-6, AR-7, all slash lines | Outcomes, base states and run-expectancy deltas are PA-level facts |
| **Slot-game** | a PA tagged with its batting slot | AR-5, AR-6, AR-7 | The lineup question is about slots, not hitters |

**Grain-drift hazard.** Mixing PA-grain rates with pitch-grain rates is the most likely way this product could produce a wrong number. Mitigated three ways: (a) `pa_frame()` is the single constructor of PA grain; (b) contact-quality work always re-filters `type == 'X'` from pitch grain rather than reusing PA grain; (c) DQ-12/DQ-13 reconcile the PA-spine slash against the locked pitch-grain kernel.

### 1.3 The strict PA spine

```python
NON_PA_STRICT = ['NA', 'pickoff_1b', 'truncated_pa']
```
The locked `get_stats` uses `['NA', 'pickoff_1b']`. The fork is deliberate, documented (01 §3.4), reconciled (V-009), and immaterial to the primary window (0 occurrences in 2026).

**Architectural rule established:** *when a new KPI family needs a different definitional basis than a locked kernel, fork the basis explicitly and reconcile it in verification. Do not edit the locked kernel mid-build.*

### 1.4 Join strategy

| Join | Keys | Cardinality | Fan-out risk |
|---|---|---|---|
| Arraez × wOBA constants | `game_year` = `Season` | many:1 | **None** — validated, constants unique per season |
| Phillies × wOBA constants | `game_year` = `Season` | many:1 | None |
| Slot weights × context profiles | `ctx` | many:many *(intentional)* | **Managed** — this is the AR-6 cross product; row count asserted as slots × contexts × hitters |
| Receipts × renderers | filename | 1:1 | None |

No join in this build widens the subject's row count. Validated in 05 §2.

---

## 2. New KPI specifications

Format per the `kpi-calculator` contract: plain language → formula → grain → population → source CDEs → edge cases → publication gate.

---

### AR-1 · Two-Strike Survival Rate (TSSR)

**Plain language.** Of the plate appearances in which the hitter faced a two-strike count at any point, what share ended in something other than a strikeout?

**Formula.**
```
reached_2k(pa) = max(strikes) over pitches in pa >= 2
TSSR = 1 − |{pa : reached_2k(pa) ∧ events(pa) ∈ strikeouts}| / |{pa : reached_2k(pa)}|
strikeouts = {strikeout, strikeout_double_play}
```
**Grain.** Hitter × season (and hitter × window for the benchmark).
**Population.** Strict PA spine, regular season. Benchmark population: Phillies hitters with ≥150 PA in 2026 (10 qualify).
**Source CDEs.** `strikes`, `events`, `game_pk`, `at_bat_number`.
**Edge cases.**
- A PA that ends *on* the pitch that made it 0-2 → `strikes` is recorded pre-pitch, so a swinging strikeout on a 0-2 count has `strikes == 2` on its final row. Correctly captured.
- Bunt fouls with two strikes are strikeouts in `events` — no special handling needed.
- PA with no two-strike pitch → excluded from denominator, not counted as a survival.
**Publication gate.** Denominator ≥ 50 PA. All 11 benchmark rows clear it (min 110).

---

### AR-2 · Two-Strike Damage Line (TSDL)

**Plain language.** The full production line restricted to two-strike plate appearances.

**Formula.** Standard slash / wOBA / xwOBA / RE24-per-PA over the AR-1 numerator population.

**Grain / population / CDEs.** As AR-1, plus locked slash components and `delta_run_exp`.
**Edge cases.** wOBA uses the season weight matching each row's event; a two-strike population has a different event mix than the season, so the weights must be applied per-row and not averaged.
**Publication rule (mandatory).** **AR-2 must be published adjacent to AR-1 and never alone.** A high survival rate paired with a suppressed damage line is the honest reading; publishing survival alone would overstate value. Enforced in report §3 and in the dashboard's Two Strikes tab.

---

### AR-3 · Damage Profile by Pitch Group × Hand (DPGH)

**Plain language.** For each combination of pitch group and pitcher handedness, what did he actually do — and does the quality of contact support it?

**Formula.**
```
slash columns   : line_from_pa( pa_frame ∩ {pitch_group(g), p_throws(h)} )
contact columns : over {type=='X'} ∩ {pitch_group(g), p_throws(h)}
                  avg_ev, hard_hit = mean(launch_speed>=95),
                  barrel = mean(launch_speed_angle==6),
                  xwoba_con = mean(estimated_woba), n = count(notna)
thin(g,h)       : bip < 15
```
**Grain.** pitch_group × p_throws. **Population.** 2026 primary; career version published as shadow.
**Source CDEs.** `pitch_type` (via locked `PITCH_GROUP`), `p_throws`, `type`, `launch_speed`, `launch_speed_angle`, `estimated_woba_using_speedangle`, locked slash components.
**Edge cases.**
- Unclassified `pitch_type` (0.9% of 2026) → dropped, not imputed. DQ-20 asserts ≥97% mapping.
- **Two populations in one table** — see 02 §3. Never combined arithmetically.
- `PO`, `EP`, `CS` and other rarities map through `PITCH_GROUP` or drop; none exceeds 1 pitch.
**Publication gate.** Rows below 15 balls in play are **retained** but flagged `thin=True`, coloured in the figure, and must be printed with their `n` in any consumer artifact. One cell qualifies (offspeed vs LHP, 4 BIP) and is explicitly marked unusable in the report.

---

### AR-4 · Scoring-Position Conversion Rate (SPCR)

**Plain language.** Of the runners already in scoring position when he came up, what share scored on that plate appearance?

**Formula.**
```
n_risp(pa)        = [on_2b ≠ null] + [on_3b ≠ null]
runs(pa)          = post_bat_score − bat_score
runs_excl_batter  = runs − [events == home_run]
risp_scored(pa)   = min(runs_excl_batter, n_risp)
SPCR              = Σ risp_scored / Σ n_risp
```
**Grain.** Runner, aggregated to hitter × context (**not** plate appearance — a two-RBI double counts twice).
**Population.** Strict PA spine where `n_risp ≥ 1`.
**Source CDEs.** `on_2b`, `on_3b`, `bat_score`, `post_bat_score`, `events`.
**Edge cases.**
- **Solo home run with a runner on second** → batter scores himself; `runs_excl_batter` removes him; the runner from second is correctly credited.
- **Runner from first scores on a double** → `runs_excl_batter` = 1, `n_risp` = 1 (only second was occupied). `min()` caps the credit at 1, so the runner from first cannot inflate the rate. **This `min()` is the guard that makes the metric honest** and is asserted by DQ-19.
- Runner thrown out at the plate → no run, correctly counted as a non-conversion.
- Errors and wild pitches on the PA are attributed to the batter. **Known limitation, stated in 02 §3.**
**Publication gate.** ≥40 runners faced. All 11 benchmark rows clear it (min 63).

---

### AR-5 · Lineup Slot Opportunity Profile (LSOP)

**Plain language.** What does each spot in the batting order offer, regardless of who is standing in it?

**Formula.** `slot` derived per §3 below; then per slot: `PA/games`, `mean(men_on)`, `mean(risp)`, `sum(n_risp_runners)/games`, `mean(outs_when_up)`, and the share of PAs leading off an inning.
**Grain.** Batting slot (1–9). **Population.** All 2026 Phillies regular-season PAs (4,168 strict; 112 games).
**Source CDEs.** `game_pk`, `at_bat_number`, `on_1b/2b/3b`, `outs_when_up`, `events`.
**Edge cases.** Substitutions inherit the slot they replace — handled automatically by the modulo. Extra-inning and shortened games need no special handling because the modulo is per-game and unanchored to a fixed PA count.
**Publication gate.** Slot reconstruction must pass JV-03 (05 §3) — nine distinct slots per game, and nine distinct batters in the first nine PAs of every game.

---

### AR-6 · Slot-Projected Run Contribution (SPRC) — **the decision model**

**Plain language.** If this hitter batted in this slot, how many runs of expectancy would his observed production be projected to add over a full season?

**Formula.**
```
c ∈ {BASES_EMPTY, MEN_ON_NO_RISP, RISP}

W(s,c)        = |PAs in slot s with context c| / |PAs in slot s|         (observed, 2026 PHI)
RE24/PA(h,c)  = mean(delta_run_exp) over hitter h's PAs in context c     (observed)

SPRC(h,s)     = [ Σ_c W(s,c) · RE24/PA(h,c) ] × PA_per_game(s) × 162
```
**Grain.** Hitter × slot. **Population.** 11 hitters (Arraez + 10 Phillies regulars) × 9 slots = 99 rows.
**Source CDEs.** `delta_run_exp`, base-state fields, derived `slot`, `game_pk`.

**Design rationale — why this and not a simulation.** A Markov base-out simulation was considered and rejected for v1.0.0. It would require a transition matrix estimated from the same 2026 sample, introducing estimation error and a set of independence assumptions that would themselves need specs and caveats. The empirical composition uses only quantities that are **directly observed and separately receipted** (`f3` and `f4`), so a reader can audit each half independently. Offered to the DPO as a follow-on (OI-5).

**Explicit non-claims — these must accompany every publication of AR-6.**
1. **The opportunity weights `W(s,c)` are held fixed at the observed 2026 distribution.** Re-ordering the lineup would change them. The model does not capture that feedback. *This is the model's single largest limitation.*
2. Not a wins projection. RE24 is run expectancy, not runs, and not WAR.
3. Scenario totals are **pair sums**, comparable only *within* a framing. Comparing a Turner-framing total to a Schwarber-framing total is meaningless.
4. Assumes the hitter's context-specific production is a property of the hitter. At 74–301 PA per context cell this is an assumption, not a demonstration.

**Edge cases.** A hitter with zero PAs in a context contributes zero to that term rather than propagating null — checked; no hitter in scope has an empty context. Weights are asserted to sum to 1 per slot (DQ-24, V-100).
**Publication gate.** Both inputs must be published as standalone receipts (`f3`, `f4`) so the composition is auditable. Satisfied.

---

### AR-7 · Table-Setting Value (TSV)

**Plain language.** How many baserunners would he create from this slot, and what do the hitters behind him do with them?

**Formula.**
```
(a) SUPPLY
    supply(h,s)          = OBP(h) × PA_per_game(s)
    delta(h,s)           = supply(h,s) − incumbent_onbase_per_game(s)

(b) REALISATION  (over the two following slots, cyclically)
    next(s)              = {s mod 9 + 1, (s+1) mod 9 + 1}
    realisation(s)       = SPCR over next(s);  RE24/PA in men-on PAs over next(s)

(c) COMBINED — upper bound only
    cashed_ub(h,s)       = supply(h,s) × 162 × SPCR(next(s))
```
**Grain.** Hitter × slot. **Population.** 2026 Phillies.

**Units warning — mandatory disclosure.** `cashed_ub` applies a conversion rate estimated *per runner in scoring position* to *all* baserunners supplied. Not every baserunner reaches scoring position, so **`cashed_ub` is an upper bound, not a run total.** It is labelled as such in the receipt comment, the report table footnote, and the dashboard tooltip.

**Non-additivity rule (mandatory).** **AR-7 must never be summed with AR-6.** AR-6 already values the batter's own PA outcomes, which include reaching base. Adding AR-7 double-counts. Stated in 02 §3, in the report §6.4 footnote, and in the build source comment.

**Defect corrected during build.** The first implementation computed `delta_onbase × RE24_per_men_on_PA` — a count multiplied by a per-PA rate, yielding a quantity with no coherent unit. Caught in review before any figure was published, reworked onto the per-runner basis above. Recorded in 00 §What is new, item 4.

---

## 3. Batting-slot reconstruction — method and justification

**Problem.** Statcast has no lineup-slot field. The consumer's question cannot be answered without one.

**Method.**
```python
pa = pa_frame(phillies_batting)           # strict PA spine
pa = pa.sort_values(['game_pk','at_bat_number'])
pa['slot'] = pa.groupby('game_pk').cumcount() % 9 + 1
```

**Why it is exact rather than approximate.** A batting order cycles strictly: the *k*-th plate appearance a team takes in a game is always taken by lineup slot `k mod 9 + 1`, regardless of substitutions, pinch hitters, or double switches — because a substitute occupies the slot of the player he replaces. The mapping is therefore exact **provided every plate appearance is captured in order**.

**The one precondition, and how it is tested.** A missing or duplicated PA shifts every subsequent slot in that game. Two assertions catch it:
- **Nine distinct batters in the first nine PAs of every game.** A missing PA would put a repeat batter in the first cycle.
- **Nine distinct slots in every game.**

First run: **111 / 112**. The exception was root-caused to a `truncated_pa` continuation creating a duplicate PA row for the same batter (Bohm, 2026-05-26). Excluding `truncated_pa` via the strict spine resolves it: **112 / 112**. See 05 §3.

**Residual risk, disclosed.** 87.7% of (game, slot) cells contain exactly one batter; the remaining 12.3% are genuine in-game substitutions. AR-5 is a property of the *slot*, so substitutions are correct to include. AR-6 uses only slot-level weights, so it is unaffected by who occupied the slot.

---

## 4. Exploratory findings that shaped the design (`eda-agent`)

| Finding | Design consequence |
|---|---|
| `delta_run_exp` populated on 99.07% of 2026 PAs | Made AR-6 feasible without building a run-expectancy matrix. Gated at ≥98% by DQ-10 |
| `launch_speed` non-null (42.7%) far exceeds `bb_type` (24.0%) | Confirmed O3. Every contact computation gates on `type == 'X'` |
| Only 3 `truncated_pa` in 8 seasons, **0 in 2026** | Justified forking the PA basis rather than patching the locked kernel |
| Arraez 2026 K rate 4.5% vs roster median ~19% | Two-strike benchmarking would be the highest-signal comparison — prioritised AR-1 |
| Slot-1 RISP share 17.6% vs slot-4 25.0%; PA/game 4.57 vs 4.26 | The two effects nearly cancel — predicted a small SPRC spread **before** the model ran. Confirmed at 3.95 runs |
| League reference file stops at 2023 | Blocked its use as a 2026 benchmark; Phillies-internal benchmarking adopted instead (and matches the DPO's scoping decision) |
| Slot-4 incumbents (Bohm, Marsh) posted a .287 OBP | Flagged the cleanup spot as the roster's largest on-base deficit — became the AR-7 headline |
