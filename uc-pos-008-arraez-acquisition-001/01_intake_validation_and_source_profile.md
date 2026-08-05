# 01 — Intake Validation & Source Profile

**Agents:** `use-case-validator` → `source-system-profiler` → `domain-steward-proxy`
**Layer 1 — Intake & Discovery** · UC #32 · `uc-pos-008` · `dp_uc31`

---

## 1. Use-case validation (`use-case-validator`)

**Verdict: GO.** 0 blocking gaps, 7 non-blocking.

### 1.1 Completeness assessment

| Required element | Present? | Note |
|---|---|---|
| Business question(s) | ✅ | Six distinct questions, listed in §1.2 |
| Named decision | ✅ | Lineup slot — unusually well-specified for this repo |
| Named consumer/personas | ⚠️ partial | "personas within the Phillies batting department" — not enumerated. Gap G-1 |
| Subject entity | ✅ | Luis Arraez; resolvable to a single MLBAM id |
| Evidence window | ❌ | Not stated by the consumer. Gap G-2 — **resolved by DPO election** (2026 primary / prior shadow) |
| Success criteria | ⚠️ partial | Implied ("a fully governed package"), not measurable. Gap G-3 |
| Output format | ✅ | PDF required; interactive dashboard requested; other formats permitted |
| Data availability | ✅ | Confirmed by profiler before design began |

### 1.2 The six questions, restated testably

| # | Question as asked | Restated as testable | Answerable? |
|---|---|---|---|
| Q1 | "Analyze his top-line results" | Season slash line, wOBA/xwOBA, rate stats, 2026 vs career | ✅ |
| Q2 | "then identify underlying indicators" | Contact quality, discipline, bat tracking; do the results agree with the process? | ✅ |
| Q3 | "his proclivity to collect hits with 2 strikes" | Two-strike PA rate, strikeout avoidance in those PAs, two-strike slash, benchmarked against the roster | ✅ **AR-1, AR-2** |
| Q4 | "the pitches (maybe pitch_group) and handedness he is able to slug" | SLG and xwOBAcon at (pitch_group × p_throws) grain, with sample gates | ✅ **AR-3** |
| Q5 | "his performance with runners in scoring position" | Slash and run-conversion in RISP base states, benchmarked | ✅ **AR-4** |
| Q6 | "where to hit him... impact on run creation in the leadoff spot versus the four spot" | Per-slot opportunity mix × per-hitter context production, projected to a season | ✅ **AR-5, AR-6, AR-7** |

### 1.3 Gap register

| ID | Gap | Class | Disposition |
|---|---|---|---|
| G-1 | Personas named only as a group | Non-blocking | Product infers four: hitting coach, manager, analytics group, front office. Listed in 06 |
| G-2 | Evidence window unstated | Non-blocking | **Escalated to DPO; resolved** — 2026 primary, prior shadow |
| G-3 | No measurable success criteria | Non-blocking | Product proposes three falsifiable projections as the closure test (00 §Closure) |
| G-4 | "wild at-bats" is an untested assertion carried in the prompt | Non-blocking | Treated as a **hypothesis to test, not a premise to assume.** Test: P/PA and pitches-per-two-strike-PA. Result: **not supported** — see report §2 |
| G-5 | "barely collects [three true outcomes]... but still gets on-base at a good clip" — an assumption about walk rate | Non-blocking | Tested. Half right: TTO rate is genuinely tiny, but the on-base comes from **hits, not walks** — BB% is 4.5% and has halved since 2019 |
| G-6 | **Leadoff premise contradicts the log** | Non-blocking at intake; **escalated to BLOCKING for circulation** post-build | See OI-1. Request names Schwarber; log says Turner |
| G-7 | No park/context adjustment requested or scoped | Non-blocking | Declared out of scope; disclosed in report caveat 6 |

### 1.4 Feasibility

The stretch goal (Q6) was assessed before commitment. **Feasible without simulation**, because two facts hold in this repo's data:

- Statcast publishes `delta_run_exp` per pitch — a run-expectancy delta computed against a league base-out table. Summing it over a hitter's plate appearances yields RE24 directly, with **no need to build or assume a run-expectancy matrix.**
- Batting-order slot is **not** a Statcast field, but it is **derivable** — see §3.3.

Had either failed, Q6 would have been returned as a blocking gap rather than attempted.

---

## 2. Source profile (`source-system-profiler`)

### 2.1 Sources admitted

| Source | Rows | Window | Role |
|---|---|---|---|
| `data/opponents/arraez.parquet` | 15,481 raw → **15,228** after filters | 2019-05-18 → 2026-08-02 | Subject. Single-batter cache |
| `data/phillies/phils_2026.parquet` | 37,111 → **16,269** batting rows | 2026-03-26 → 2026-08-02 | Comparison set + lineup structure |
| `wOBA and FIP Constants.csv` | 12 seasons | includes 2026 | Season wOBA weights |
| `league_sc_data.csv` | 9 rows | **max year 2023** | Structural reference **only** — explicitly not used as a 2026 benchmark |

### 2.2 Filters applied, in order

```
batter == 650333          →  entity lock (MLBAM id, never a name filter)
game_type == 'R'          →  15,481 → 15,228  (drops 136 F + 117 D postseason)
drop_duplicates(game_pk, at_bat_number, pitch_number)  →  no change (0 dupes)
```

**Zero duplicate pitch keys in the raw file.** Unusual and worth noting — most opponent caches in this repo carry some.

### 2.3 Fitness for purpose, per requested CDE

| CDE | Physical field(s) | 2026 non-null | Fit |
|---|---|---|---|
| Plate appearance outcome | `events` | 26.9% of pitches (= terminal pitches) | ✅ |
| Count state | `balls`, `strikes` | 100% | ✅ Q3 fully supported |
| Pitch classification | `pitch_type` | 99.1% | ✅ Q4 supported; 0.9% unclassified excluded |
| Pitcher handedness | `p_throws` | 100% | ✅ |
| Base state | `on_1b`/`on_2b`/`on_3b` | 24.1% / 14.8% / 7.1% *(non-null = runner present)* | ✅ Q5 supported |
| Outs | `outs_when_up` | 100% | ✅ |
| Run expectancy delta | `delta_run_exp` | **99.07%** | ✅ Q6 supported |
| Contact quality | `launch_speed`, `launch_angle` | 42.7% of pitches | ⚠️ see §3.2 |
| Expected outcomes | `estimated_woba_using_speedangle` | 26.3% | ⚠️ see §3.1 |
| Bat tracking | `bat_speed`, `attack_angle` | 47.3% of pitches (2023+ only) | ⚠️ era-limited, disclosed |

### 2.4 Volume by season

| Season | Pitches | PA | Adequacy for splits |
|---|---|---|---|
| 2019 | 1,487 | 366 | shadow |
| 2020 | 512 | 121 | shadow — short season |
| 2021 | 1,983 | 480 | shadow |
| 2022 | 2,418 | 603 | shadow |
| 2023 | 2,203 | 617 | shadow |
| 2024 | 2,430 | 672 | shadow |
| 2025 | 2,468 | 677 | shadow |
| **2026** | **1,727** | **464** | **PRIMARY** — adequate for headline and two-strike; **thin** for RISP (89) and group × hand (one cell at 4 BIP) |

### 2.5 The finding that shaped the product

**Arraez has zero Phillies plate appearances.** His 2026 rows are all San Francisco through the cache maximum of 2026-08-02.

| 2026 month | Team | Pitches |
|---|---|---|
| March | SF | 78 |
| April | SF | 399 |
| May | SF | 414 |
| June | SF | 417 |
| July | SF | 400 |
| August (1–2) | SF | 19 |

*(The 85 rows carrying `batter == 650333` inside `phils_2026.parquet` are Arraez batting **against** the Phillies as an opponent. They are not used — the subject is sourced exclusively from `arraez.parquet` — so no double-count is possible. Asserted as DQ-07.)*

This makes the product an **onboarding dossier**, not a review. Every claim is an inference from a different team, park, and lineup context. Recorded as report caveat 6.

---

## 3. Domain steward notes (`domain-steward-proxy`)

Surfaced from repo history and prior UC governance docs. No new business meaning invented.

### 3.1 `estimated_woba_using_speedangle` is not populated for every plate appearance

It exists for balls in play **and** for strikeouts (assigned 0), but not for walks or hit-by-pitch. Any mean taken over a mixed population silently changes its denominator.

**Consequence for this build:** `xwoba` at PA grain is reported as a mean over available estimates and is used **directionally**, never as a precise expected-runs quantity. `xwOBAcon` — restricted to `type == 'X'` — is the load-bearing contact-quality metric, and its honest denominator is published as `xwoba_con_n`.

### 3.2 `launch_speed` is populated on fouls from 2023 onward

Open item **O3**, opened in `uc-pps-024` (Kilian). In 2026 `launch_speed` is non-null on 42.7% of pitches but `bb_type` on only 24.0% — the difference is largely fouls.

**Consequence:** every contact-quality computation in this build filters `type == 'X'` first. The locked `batted_ball()` already does this; the new AR-3 kernel does it explicitly. Any future analyst who filters on `launch_speed.notna()` instead will get a wrong answer.

### 3.3 Batting-order slot is derivable but not stored

Statcast has no lineup-slot field. It is recoverable because a batting order cycles strictly: within a game, order the team's plate appearances by `at_bat_number` and take `index mod 9 + 1`. Substitutions inherit the slot of the player they replace, which the modulo handles automatically.

**Precondition:** every plate appearance in the game must be captured. A missing PA shifts every subsequent slot. Validated by `join-validator` — see 05 §3.

### 3.4 `truncated_pa` is a continuation marker

Statcast emits `events == 'truncated_pa'` when a plate appearance is interrupted (typically by a third out on the bases) and resumed. It is **not** a new plate appearance.

The locked `get_stats()` kernel, inherited verbatim from `dp_uc20`/`dp_uc24`, excludes only `{NA, pickoff_1b}` and therefore **counts `truncated_pa` as a plate appearance and as an at-bat.**

| Scope | `truncated_pa` count |
|---|---|
| Arraez, all seasons | 3 (2021: 1, 2025: 2) |
| Arraez, **2026 primary window** | **0** |
| Phillies 2026 comparison set | 6 |

**Disposition:** the locked function is **not modified** — it is shared with `dp_uc20`, `dp_uc22`, `dp_uc24` and patching it mid-build would silently fork a definition across four delivered products. The new AR-* KPIs use a strict PA spine that excludes it; the fork is asserted and reconciled in verification (V-009), disclosed in report caveat 8, and logged as open item **O5**.

**Because the primary window contains none, no forward-looking number in this product is affected.**

### 3.5 Known contamination pattern

The Nola / "Nolan Hoffman" incident established the house rule: **entity lock on MLBAM id, never on a name filter.** Applied here as DQ-01/DQ-02. Player names appearing in outputs are resolved by modal parse of the `des` field, never hand-keyed.

### 3.6 Carry-forward open items

| ID | Origin | Status here |
|---|---|---|
| O2 | `uc-pps-024` — locked `in_zone_rate` | Not touched; `zone <= 9` used as inherited |
| O3 | `uc-pps-024` — `launch_speed` on fouls | Mitigated by `type == 'X'` filtering throughout |
| O4 | `uc-pps-025` — `xwobacon` size semantics | Mitigated by publishing `xwoba_con_n`; guard rule DQ-23 |
| **O5** | **opened here** — `truncated_pa` fork | Reconciled and disclosed; deferred to coordinated version bump |
