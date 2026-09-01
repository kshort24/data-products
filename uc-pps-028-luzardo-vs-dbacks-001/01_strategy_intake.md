# 01 · Strategy & Intake — uc-pps-028 (UC #39 / dp_uc39)

**Layer 1 agents:** `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`
**Gate:** must complete before design. **Status: ✅ PASS — GO with 3 non-blocking gaps.**

---

## 1 · The use case as received

> "I want to do a pre-scout on Jesús Luzardo before his start against the Diamondbacks tonight.
> Extend the analysis that was done on him at the All-Star break. He has been maybe the Phillies'
> most consistent pitcher in 2026? Since the end of April he has been very good. I have not done
> much inspection on my own, so I am leaning on the data-product-owner to guide the narrative here."
> — human DPO, 2026-09-01

**Value stream:** Phillies Pitching (`pps`). **Consumers:** DPO, manager, pitching department, catcher.
**Decision it serves:** tonight's game plan and leash, plus a season-to-date position on the pitcher.

## 2 · use-case-validator — gap report

| # | Gap | Class | Resolution |
|---|---|---|---|
| **G-1** | **"Most consistent" is undefined.** Consistency is a variance claim; nothing in the ask says variance *of what*, measured *how*, against *whom*. | **BLOCKING for design, resolved** | Operationalised as six independent axes **CN-1…CN-6** (`02`), ranked against the full rotation. **No composite index** — a composite is a weighting knob, and a weighting knob is how a premise gets confirmed. |
| **G-2** | **"Since the end of April" is an unfitted boundary chosen by the client.** | **BLOCKING for inference, resolved** | Stated as `2026-05-01`, then **scanned across 8 candidate boundaries** (TR-2, inherited from `uc-pps-027`) plus a full-season control. Guardrail **G6** applies. |
| **G-3** | **Two claims are bundled into one sentence** — a *level* claim ("very good") and a *variance* claim ("most consistent"). | **BLOCKING for narrative, resolved** | Adjudicated separately. They get different verdicts; bundling them would have produced one wrong answer. |
| G-4 | No confirmed Arizona lineup. | Non-blocking | Hitter panel built from batters actually faced; tiered by recency; labelled **UNVERIFIED** in the report, the dashboard and the freshness manifest. |
| G-5 | "Extend the All-Star-break analysis" does not say *which* parts. | Non-blocking | Interpreted as: close every second-half watch item `uc-pps-017` left open (T1–T8), and reproduce its published first-half line as a continuity check. |
| G-6 | Deliverable depth not stated. | Non-blocking | DPO answered in session: full governance package, PDF, interactive dashboard, opponent as a lens rather than a co-equal study. |

**The C-1 lesson from `uc-pps-027` is the governing precedent here.** That UC shipped a calibration
finding: *a harness built around a causal claim the client already believes will fill cleanly and be
wrong.* This ask contains **two** client claims and an explicit invitation to lead the narrative.
The validator's ruling was therefore that **the design must be able to falsify the premise before it
is allowed to describe it.** It could, and it partly did.

## 3 · source-system-profiler — fitness for purpose

**Entity lock:** `pitcher == 666200` (Jesús Luzardo). Name filters are forbidden — the
`Nola`/"Nolan Hoffman" contamination is the canonical failure and the accent-fold defect (`O-12`,
`uc-pps-027`) is the recent one. Resolved name in-frame: **`Luzardo, Jesús`**, 1 distinct id, 0 duplicates.

| Source | Rows in scope | Window | Fitness |
|---|---|---|---|
| `data/phillies/phils_2026.parquet` | 2,652 pitches / 673 PA / 27 GS | 2026-03-29 → 2026-08-26 | **FIT** — primary |
| `data/phillies/phils_2025.parquet` | 3,013 pitches / 759 PA / 32 GS | full 2025 | **FIT** — YoY comparison |
| `data/phillies/phils_2026.parquet` (staff) | 5 starters ≥8 GS | 2026 | **FIT** — consistency cohort |
| `data/opponents/luzardo.parquet` | 8,821 rows, 2019–2024 | pre-Phillies | **FIT for career H2H only** — tiered, never blended |
| Arizona hitter cache | **absent** | — | **NOT AVAILABLE** — opponent tier built from the pitcher's own log (the UC6 → UC8 → UC11 pattern) |

**Freshness:** 2026 cache max `game_date` = **2026-08-30**; Luzardo's last start **2026-08-26**.
T-6 relative to tonight, which is a normal turn, not staleness.

**CDE completeness** (evaluated *at the grain each element is defined on* — see defect **D-1** in `05`):
`zone`, `strikes`, `balls`, `pitch_number`, `n_thruorder_pitcher`, `description`, `pitch_name`,
`stand`, `bat_score`, `post_bat_score`, `release_speed` — **100% at pitch grain**;
`events` — **100% at PA-terminating grain**; `launch_speed` / `launch_angle` — **99.5% at ball-in-play grain**.

**The finding that unblocked the whole design:** `estimated_woba_using_speedangle` is populated on
**664 pitch rows and exactly 664 PA-terminating rows** in the 2026 frame — strikeouts carry 0.000,
walks carry `wBB`, HBP carries `wHBP`. **The pitch-level mean therefore IS a per-PA xwOBA, not
xwOBAcon.** This is asserted as a hard DQ rule rather than assumed, because `uc-pps-021` deprecated
the pitch-level `get_stats.xwoba` on the belief that it was a contact-only measure. It is not, in this
schema, at this grain. 9 of 673 PA carry no value (4 `sac_bunt`, 3 `truncated_pa`, 2 untracked) —
denominators are printed.

## 4 · domain-steward-proxy — business rules and known quirks

- **A "start" is derived, never carried in.** The Phillies pitcher who threw the game's first Phillies pitch, taken from the log. All 27 of Luzardo's 2026 appearances are starts.
- **RA9, not ERA.** Runs are score deltas while on the mound. Bequeathed runners are charged to the pitcher on the mound when they score. **No official ERA or W–L can be computed from a pitch log and none appears in any artifact.**
- **IP is reconstructed from an event→outs map** and may differ ~1 out from official.
- **`n_thruorder_pitcher`** is the governed times-through-order field; clipped at 3 (`3+`).
- **The catcher is `fielder_2`.** Realmuto caught 2,365 of 2,652 pitches (89%).
- **Switch-hitters:** `stand` records the side actually batted from, so a switch-hitter's H2H line mixes sides. Flagged in the report where it matters (Ketel Marte).
- **A team-level career H2H panel mixes eras.** Luzardo has faced "Arizona" since 2019 across three organisations; 2019–23 opponents are not tonight's opponents. Tiering is mandatory (defect **D-3**).

## 5 · business-glossary-agent — term disposition

**Rule-1 grep run before declaring anything new** (the mandatory step from the repo-search memory):

| Candidate | Prior art in repo | Disposition |
|---|---|---|
| `whiff_rate`, `chase_rate`, `putaway_rate`, `fpsr`, `hard_hit_rate`, `get_stats`, `nresults` | Baseball Functions (locked); dp_uc11 → dp_uc17 | **LOCKED — inherit verbatim, do not re-implement** |
| `csw_rate` | `PD-4`, dp_uc17 | **Inherit verbatim** |
| outs/IP-from-log, RA9-from-score-deltas, FIP | `PD-1/PD-2/PD-3`, dp_uc17 | **Inherit verbatim** |
| TTO split, battery split, count-leverage funnel | `PD-5…PD-7`, dp_uc17 | **Inherit verbatim** |
| Breakpoint sensitivity scan | `TR-2`, `uc-pps-027` | **Inherit the method** |
| Start-level xwOBA dispersion | **none** | **NEW-PROVISIONAL CN-1** |
| Start floor rate / blow-up rate | **none** (adjacent: the "quality start" concept, never implemented here) | **NEW-PROVISIONAL CN-2, CN-3** |
| Rolling-3-start range | **none** (adjacent: `RF-2` rolling form, `uc-pos-006` — a *level* smoother, not a *range*) | **NEW-PROVISIONAL CN-4** |
| Turn / workload reliability | **none** | **NEW-PROVISIONAL CN-5** |
| Length dependability | **none** | **NEW-PROVISIONAL CN-6** |
| Opponent-tier recency split | **none** | **NEW-PROVISIONAL AR-1** |

**No governed term is redefined by this UC.** `CN-1…CN-6` and `AR-1` are provisional pending DPO
ratification — escalation **E-2** in `00`.
