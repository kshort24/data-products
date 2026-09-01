# 02 · Engineering Design — uc-pps-028 (UC #39 / dp_uc39)

**Layer 2 agents:** `data-architect` · `kpi-calculator` · `metadata-mapper` · `semantic-modeler`
**Gate:** must complete before build. **Status: ✅ PASS.**

---

## 1 · data-architect — model blueprint

Single-source, pitch-grain, no joins across domains — so there is no fan-out surface and the
`join-validator` is not engaged (recorded as a deliberate descope, not an omission).

```
phils_2025.parquet ┐
phils_2026.parquet ┼─► pitch_log        grain: game_pk × at_bat_number × pitch_number
                   │   filters: phillies_role=='pitching', game_type=='R', dedup
                   │   ├─► lz_frame     + pitcher==666200          (the subject)
                   │   └─► staff_frame  all Phillies pitching      (the cohort)
                   │
                   ├─► pa_frame         grain: game_pk × at_bat_number   (last pitch of each PA)
                   │      carries events, post_bat_score-bat_score, xwOBA
                   │
                   ├─► start_frame      grain: game_pk                   (one row per start)
                   │      outs, runs, PA, K, BB, HR, wOBA, xwOBA, pitches, days_rest
                   │      ── the atom of the entire consistency family ──
                   │
                   └─► cohort_frame     grain: pitcher × window
                          CN-1..CN-6 computed from start_frame, filtered by window

luzardo.parquet (2019-24) ─► career_h2h  ── SUPPORTING TIER, never blended into 2026 rates
```

**Grain discipline.** Every KPI declares the grain it is computed at. Three grains exist and mixing
them is the defect class this UC actually hit (**D-1**): a rate whose denominator is "pitches" cannot
be sanity-checked against a field defined once per PA.

**Cohort membership is derived.** `identify_starts()` takes the pitcher who threw the game's first
Phillies pitch, per `game_pk`, from the log. No roster file, no hand-keyed ids. Cohort floor:
**≥8 starts inside the window** (`MIN_GS_COHORT`). A start enters the dispersion axes only at
**≥15 PA** (`MIN_PA_START`), so an ejection or a rain-shortened outing cannot masquerade as volatility.

**Performance note.** The first build computed the per-start frame inside the breakpoint loop
(8 boundaries × 5 pitchers × ~25 games of `nresults`) and did not finish inside the shell's time
budget. Refactored to compute each pitcher's start frame **once** and window it by filtering — the
scan is now a filter, not a recomputation.

## 2 · kpi-calculator — the NEW provisional family

> **Design principle, stated once and enforced everywhere below.**
> "Consistent" is a claim about **variance**. "Very good" is a claim about **level**. They are
> different questions and a pitcher can win one and lose the other — which is exactly what happened.
> Each axis is therefore reported and ranked **on its own**. There is deliberately **no composite
> consistency index**, because a composite requires weights, and weights are a knob that can be
> turned until the premise is confirmed.

### CN-1 · Start-to-start variation
- **Plain language:** how much a start's expected damage swings from one outing to the next.
- **Formula:** population standard deviation (ddof=0) of per-start xwOBA. IQR emitted alongside as a robustness companion.
- **Grain:** start (`game_pk`). **Population:** starts in window with ≥15 PA.
- **Direction:** lower is steadier. **Edge cases:** a start with no xwOBA-bearing PA is excluded, not zero-filled.

### CN-2 · Floor rate
- **Plain language:** how often he gives the team a usable start.
- **Formula:** share of starts with `outs ≥ 15` **and** `runs ≤ 3`. (The reconstructed analogue of a quality start; named differently because it is *not* the official statistic — outs are event-derived and runs are RA9-basis.)
- **Direction:** higher is better. **Edge case:** a start meeting only one condition fails.

### CN-3 · Blow-up rate
- **Plain language:** how often the start is the reason the bullpen gets wrecked.
- **Formula:** share of starts with `runs ≥ 5` **or** `outs < 12`.
- **Direction:** lower is better. **Note:** CN-2 and CN-3 are deliberately *not* complements — starts between the two thresholds are neither, and that middle band is real information.

### CN-4 · Rolling-3-start range
- **Plain language:** within any three consecutive starts, how far apart are his best and worst?
- **Formula:** mean over all rolling 3-start windows of `max(xwOBA) − min(xwOBA)`. Windows with a missing value are skipped, not imputed.
- **Direction:** lower is steadier. **Why it exists:** CN-1 is blind to ordering — a pitcher who alternates good/bad scores the same SD as one who has a bad month. CN-4 sees the alternation.

### CN-5 · Workload predictability
- **Plain language:** does the manager know what he is getting when he hands him the ball?
- **Formula:** SD of pitch count per start; min and max of the pitch band; median days' rest; count of gaps ≥10 days (missed-turn proxy).
- **Direction:** lower SD is more predictable. **Note:** this axis measures a *joint* pitcher-and-manager behaviour and is labelled as such in the report — it is not purely a pitcher trait.

### CN-6 · Length dependability
- **Formula:** mean outs per start, SD of outs per start, IP per start.
- **Direction:** higher mean / lower SD is better.

### AR-1 · Opponent-tier recency split
- **Plain language:** separate the opponents who are *actually on tonight's team* from the ones who happened to wear the same uniform in 2019.
- **Formula:** a career H2H panel against a team is tagged `current-era` when `last_faced >= 2025-01-01`, otherwise `historical only`. Only the current-era tier informs planning.
- **Why it is a KPI and not a filter:** it is a governed disclosure. Suppressing the historical tier silently would hide the sample; showing it un-tiered would launder 2019 Arizona into tonight's plan.

## 3 · Locked KPIs inherited verbatim (do not re-derive)

`get_stats` · `nresults` · `whiff_rate` · `chase_rate` (+ `in_zone_rate`) · `putaway_rate` ·
`fpsr` · `hard_hit_rate` · `csw_rate` · `outs_and_runs` · `ip_str` · `fip` · `pa_last` · `OUTS_MAP`

Copied character-for-character from `dp_uc17_luzardo_first_half.py`, which inherited them from
`dp_uc11_rangel_vs_pirates.py`, which inherited them from Baseball Functions. **Any change to these
is a governance event, not a code change.** Two known open defects are carried rather than silently
patched:

- **O-5** — `get_stats` counts `truncated_pa` as a plate appearance (3 occurrences here). Carried; flagged WARN.
- **O-8** — `hard_hit_rate` divides by *all* balls in play, counting untracked ones as not-hard-hit (2 occurrences here). Carried as the locked value; a `hard_hit_rate_tracked` shadow is emitted beside it. The two differ by <0.3 points at this sample.

Patching a locked function inside a use-case build is how kernels drift. Both are DPO escalations.

## 4 · semantic-modeler — consumption rules

| Rule | Statement |
|---|---|
| **S-1** | A CN axis is never quoted without its **window** and its **cohort size**. "#1 in consistency" is not a sentence this product can produce; "#1 of 5 on CN-1, window opening 2026-05-01" is. |
| **S-2** | A CN rank that does not survive the TR-2 scan is reported as **boundary-dependent** wherever it appears. |
| **S-3** | Level metrics (xwOBA, wOBA, RA9) and variance metrics (CN-1…CN-6) are never averaged together or shown in a way that implies one index. |
| **S-4** | Any split below 100 BF prints its PA count inline. |
| **S-5** | The opponent tier is never aggregated across `current-era` and `historical only`. |
| **S-6** | RA9 is never labelled ERA; reconstructed IP is never labelled official. |

## 5 · Descoped, and why

| Descoped | Reason |
|---|---|
| Arizona team hitter tier via a fresh `pybaseball` pull | DPO chose "self-scout led, ARI as a lens". A live pull also introduces a network dependency the device shell may not have, and an unpinned source into a governed build. |
| League-wide starter benchmark | The cohort question is "most consistent **Phillies** pitcher". A league pool would answer a question nobody asked and needs data not in the plane. |
| `join-validator`, `machine-learning-engineer`, `data-observability` | No cross-domain join, no prediction task, no post-publication pipeline. Recorded as deliberate. |
| Battery (catcher) as a causal frame | `uc-pps-027` established that this staff's approach changes are pitcher-level, not battery-level (TR-1). The battery split is emitted as a receipt but is not narrated as a driver. |
