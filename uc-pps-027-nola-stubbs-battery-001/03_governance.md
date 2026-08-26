# 03 · Governance — Glossary, DQ Rules, Tagging, Privacy, Cost

Agents: `business-glossary-agent` · `dq-rule-definer` · `data-tagger` · `privacy-watchdog` · `cost-watchdog`

---

## A · Glossary entries drafted this UC

### AT-1 · Pitch-call attribution *(constraint, not a metric — registered as a term so it can be cited)*
> **Definition.** The identification of which member of a battery selected a given pitch.
> **Status.** **NOT OBSERVABLE** in the Statcast data plane. No PitchCom sender field, no
> pitch-call field, no shake-off record exists.
> **Governed consequence.** No agent, report, dashboard, or downstream consumer of this data
> product may attribute a pitch selection, mix change, or sequencing pattern to a named
> individual. The unit of analysis is **the battery**.
> **Why this is a glossary entry.** So that a future session asking "can we tell who called
> it?" finds a governed *no* instead of re-litigating it — or worse, quietly assuming yes.

### BATTERY
> The `(pitcher, catcher)` pair for a given pitch, keyed as `(pitcher, fielder_2)`. The unit
> of analysis for this data product. Not a person; not a relationship quality score.

### CATCHER
> The player recorded in `fielder_2` on a pitch row. Resolved to a name by the dual path in
> DV-2. Note a single game may carry more than one catcher for the same pitcher
> (`catcher_split`).

### COUNT STATE *(CS-1)*
> `ahead` (strikes > balls) / `behind` (balls > strikes) / `even`, from the pitcher's
> perspective. 0-0 and 3-2 are both `even`.

### RECENCY WINDOW
> `last_5` = the five most recent starts by `game_date`. `2026_prior` = current-season starts
> outside that window. `pre_2026` = everything earlier. Window size is DV-1 and is
> sensitivity-tested at 3 / 5 / 8.

### INHERITED KPI TERMS — approved elsewhere, first implementation here
| Term | Definition source | Status |
|---|---|---|
| **Two-strike fastball usage** (BAT-4) | `uc-cat-001` KPI-1, specced 2026-08-09 | **APPROVED** — definition verbatim, not restated. High = strength exploitation; low = weakness exploitation |
| **In-zone whiff rate** (BAT-9) | `uc-cat-001` KPI-3, including its B-5/B-6 label-mismatch fix | **APPROVED** — definition verbatim. Whiffs ÷ swings, identical `zone ≤ 9` filter on both sides |

*These two are listed here rather than under NEW-PROVISIONAL because they carry approved
definitions from an adjacent product. This UC contributes the **implementation**, not the
meaning — which is exactly what CLAUDE.md governance principle #1 requires.*

### NEW-PROVISIONAL KPI TERMS — pending DPO ratification (E-2)
| Term | One-line definition | Direction |
|---|---|---|
| **Repeat-pitch rate** (BAT-5) | Share of consecutive within-PA pitch pairs that are the same pitch type | neither — descriptive |
| **Arsenal entropy** (BAT-6) | Normalised Shannon entropy of the pitch-type mix, 0 = one pitch, 1 = perfectly balanced | neither — descriptive |
| **Ahead-vs-behind divergence** (BAT-7) | Jensen-Shannon divergence between the ahead-count and behind-count pitch mixes | neither — **explicitly not a quality metric** |
| **Zone rate by count state** (BAT-8) | In-zone share within each count state | higher when behind = more aggressive |
| **First-pitch group mix** (BAT-2) | Pitch-group share on `pitch_number==1` | descriptive |
| **Putaway-pitch mix** (BAT-3) | Pitch-group share on two-strike PA-terminal pitches | descriptive |

**Deliberate design note:** none of BAT-5/6/7 is given a "green flag" direction. `uc-cat-001`
gave every KPI a direction and then had to caveat several of them. A metric whose good
direction depends on context should not carry a scoreboard.

### Duplicate / conflict scan
| Candidate | Conflict? | Resolution |
|---|---|---|
| "Putaway rate" | **Yes** — `uc-cat-001` renamed its KPI-10 from "Put-Away Rate" to "2-Strike Resolution Rate" precisely to avoid colliding with the locked pps `putaway_rate` | The locked `putaway_rate` is used here unchanged; BAT-3 is named "putaway-pitch **mix**" to keep the namespace clean |
| "Chase rate" | Two variants exist (general, and `uc-cat-001` KPI-5 two-strike-restricted) | This UC uses the **locked general** `chase_rate`. The two-strike variant is not built; if wanted it must be named distinctly |
| "First-pitch strike" | `fpsr` (locked) == `uc-cat-001` KPI-4 | Same definition. Locked implementation wins; no second version created |
| "Pitch quality" | `uc-cat-001` KPI-2 | **Not built here.** Requires the velo/spin/movement normalisation family — out of scope, offered as fast-follow |

---

## B · DQ rules (`dq-rule-definer` → `data-quality-engineer`)

Executed by the build into `out/dp_uc38_dq_scorecard.csv`. Severity `FAIL` blocks publish.

| ID | Rule | Dimension | Severity |
|---|---|---|---|
| DQ-1 | `nunique(pitcher) == 1` and equals 605400 | Validity | **FAIL** |
| DQ-2 | `nunique(player_name) == 1` after entity lock (Nolan Hoffman guard) | Accuracy | **FAIL** |
| DQ-3 | Zero duplicate `(game_pk, at_bat_number, pitch_number)` | Uniqueness | **FAIL** |
| DQ-4 | `game_type == 'R'` for 100% of rows | Validity | **FAIL** |
| DQ-5 | `fielder_2` null rate < 0.1% | Completeness | WARN |
| DQ-6 | Every distinct `fielder_2` resolves to a name by at least one path | Completeness | WARN |
| DQ-7 | Catcher name cross-check: `pos`-merge vs `uc-cat-001` dict agree on all shared ids | Consistency | **FAIL** |
| DQ-8 | wOBA weights joined for every `game_year` present | Completeness | **FAIL** |
| DQ-9 | `max(game_date)` reported with T-minus vs game day | Timeliness | INFO |
| DQ-10 | All rate KPIs ∈ [0, 1] where bounded | Validity | **FAIL** |
| DQ-11 | Entropy ∈ [0, 1]; JSD ∈ [0, 1] or NaN | Validity | **FAIL** |
| DQ-12 | BAT-1/2/3 shares sum to 1.0 ± 1e-9 within each group | Consistency | **FAIL** |
| DQ-13 | `catcher_split` games counted and reported, not silently assigned | Accuracy | WARN |
| DQ-14 | Every published table has a named CSV receipt on disk | Completeness | **FAIL** |
| DQ-15 | Sample floors present as flag columns, not applied as filters (G5) | Validity | **FAIL** |

**Scorecard status at run 1:** DQ-10/11/12 verified on synthetic fixtures (18/18 Tier A);
DQ-1…9, 13, 14 UNRUN.

**Scorecard status at run 2 (2026-08-26): ALL RULES EXECUTED · 0 FAIL · 0 WARN.**
Receipts `out/dp_uc38_dq_scorecard.csv` and `out/dp_uc38b_dq_scorecard.csv`. Highlights:
entity lock PASS (1 pitcher id, 1 player name); `fielder_2` null rate **0.0000%**; catcher
identity cross-check **7/7 AGREE** after the O-12 accent-folding fix; `catcher_split` 4 of 311
starts, all pre-2026, reported not swallowed; freshness `max(game_date)` = 2026-08-19, T-7
vs game day.

### Two guardrails added in run 2

| ID | Guardrail | Why it exists |
|---|---|---|
| **G6** | An era/breakpoint boundary is a researcher **degree of freedom**. Any claim keyed to one must survive a boundary scan (TR-2) or be reported as boundary-dependent | The 7/05 breakpoint is stated, not fitted. Without the scan, a reader cannot tell the difference |
| **G7** | A delta that appears in only **one stratum** of a non-random split is a **hypothesis, never a finding** | TR-1 exists precisely to stop the report asserting a battery effect from a Stubbs-only movement. Two metrics (knuckle-curve share, chase rate) are governed by this rule in the delivered report |

### Glossary additions, run 2 (all NEW-PROVISIONAL, pending E-2)

| ID | Term | Definition |
|---|---|---|
| **TR-1** | Adjustment-travel test | For a stated time split, the change in an approach KPI computed **separately within each stratum** of a non-random assignment variable. Same-signed movement in both strata ⇒ the change is a property of the constant (here, the pitcher), not the assignment |
| **TR-2** | Breakpoint sensitivity scan | The same delta recomputed across a range of candidate era boundaries; a claim is *boundary-robust* only if the sign is stable across all of them |
| **OC-1** | Opponent-quality control | wOBA the **rest of the same staff** allowed against an opponent in the same season, used as an in-frame difficulty index. Requires no league-wide data and inherits the frame's own filters |
| **LH-1** | Handedness panel | The locked outcome layer plus the approach layer, cut by `stand` × era. Exists to re-ask a prior product's diagnosis on new data |
| **CH-1** | Pitch-performance panel | Usage, velocity, zone rate, whiff, chase and xwOBAcon for a single `pitch_type`, cut by era × `stand`. Separates *the pitch changed* from *the usage changed* |

---

## C · Tagging proposal (`data-tagger`)

| Element | Sensitivity | Domain | Subject area | Product |
|---|---|---|---|---|
| All `dp_uc38_*` receipts | **Internal — Baseball Ops** | Phillies Pitching (pps) | Pitcher performance / battery | `uc-pps-027` |
| `dp_uc38_catcher_identity.csv` | Internal | pps | Player identity | `uc-pps-027` |
| `dp_uc38_confound_panel.csv` | Internal | pps | Methodology | `uc-pps-027` |
| Report + PDF | **Internal — Restricted** (pre-game plan) | pps | Advance scouting | `uc-pps-027` |

*Proposal only. Final sensitivity determination is a DPO decision (CLAUDE.md — the tagger
does not publish tags).*

---

## D · Privacy assessment (`privacy-watchdog`)

| Check | Finding |
|---|---|
| Direct PII | **None.** MLBAM ids and public player names for professional athletes in their professional capacity |
| Quasi-identifiers | None beyond public identity |
| Re-identification risk | **N/A** — the subjects are named on purpose |
| Sensitive combinations | None. No health, contract, or personal data |
| **Reputational sensitivity** | **PRESENT and material.** The product compares batteries and could be read as ranking a named catcher's game-calling. **G4/AT-1 is the mitigation**, and it is a governance control, not a courtesy: the data cannot support person-level attribution, so publishing it would be *wrong*, not merely unkind |
| External publish | **BLOCKED.** Pre-game internal plan. Internal-only |
| **Re-assessed run 2** | Unchanged. The filled report **strengthens** the AT-1 mitigation: the travel test's finding is that the approach change is *not* attributable to the catcher, which is the opposite of a game-calling ranking |

**Verdict: LOW privacy risk · MEDIUM reputational-inference risk, mitigated by AT-1.**

---

## E · Cost note (`cost-watchdog`)

| Item | Assessment |
|---|---|
| Compute | Single-pass parquet read (~12 season files), all aggregation in-memory. Est. **< 60s**, < 2 GB RSS |
| Storage | ~15 CSV receipts + 4 PNG ≈ **< 5 MB**. No dashboard bundle (de-scoped), so no vendored-JS payload |
| Recompute waste | **One** frame load feeds every panel. `battery_panel` is called five times on subsets of an already-loaded frame — no re-read |
| Optimisation flagged | `arsenal_entropy` and `count_state_divergence` use Python-level `groupby` loops. Fine at Nola-career scale (~30k rows); **would need vectorising** before a staff-wide `uc-cat-001` run over 143k rows × 3 catchers |
| **Token cost** | See `BID_2026-08-25_*.md` and `telemetry/run_economics_ledger.csv` |
