# SR-M1 Ratification Packet — "Mayza Success Rate" / Quick At-Bat Rate

**Standalone packet.** Pull this into the session where you ratify your other pending
functions. Everything needed to make the call is here; nothing else in `uc-pps-022` has to be
read first.

**Status:** PROVISIONAL — NOT RATIFIED — NOT INHERITABLE
**Produced by:** UC #27 (`uc-pps-022` / `dp_uc26`), `kpi-calculator` + `business-glossary-agent`
**Decision owner:** you
**Related pending ratifications:** the QR-1…QR-3 quick-recovery family from `uc-pps-019` (Sánchez) — **ratify in the same sitting**, see R5

---

## 1. What you supplied

> From his *On Pattison* interview, Tim Mayza said being a reliever with only two pitches in
> his repertoire his goal is for quick at-bats. He defines that as **getting to two strikes or
> a groundball within 3 pitches.** … in his career, which happens to be 1500 plate appearances
> as I write, he has gotten this outcome in 40% of his plate appearances.

Plus the `tm_success_rate` function, and two self-critiques.

---

## 2. Your two instincts, adjudicated

### "I could double-count PAs where he gets to two strikes and the third pitch is a grounder."

**You were right to check, and you're right that it doesn't happen.**

`np.where((z.max_strikes == 2) | (z.bips == 1), 1, 0)` evaluates to a single 0/1 per row of
`z`, and `z` is one row per `(level, game_pk, at_bat_number)` — one row per plate appearance.
A PA satisfying both legs contributes exactly 1 to `total_success`. The denominator
`total_pas = ('game_pk','size')` counts groups, not pitches. **No double-count exists.** Your
reasoning about the OR operator was correct.

### "I think this was all for naught."

**It wasn't — but the function measures something narrower than your sentence says.**

`strikes` is the **pre-pitch** count. It records what the batter walked into on that pitch,
not what the count became after it. So `max(strikes)` over `pitch_number < 4` is the count
*displayed on pitch 3*, which requires two things:

1. the second strike accrued on pitch **1 or 2** (not pitch 3), **and**
2. the plate appearance **survived to a third pitch**.

A batter who takes strike two on pitch 3 shows `strikes == 2` only on pitch 4 — excluded by
the `pitch_number < 4` filter.

**Your function measures "reached two strikes within the first *two* pitches, or a ground ball
in the first three." Your sentence says "within three pitches."** Those are different
statistics.

**Verified against Keller's 146 PA:** the second strike accrued on pitch 2 in 44 PAs, on pitch
3 in 32 more. Those 32 are exactly the PAs the literal reading would count and the function
does not.

---

## 3. The three candidate readings, on real data

Computed by `sr_m1_variants()` in `dp_uc26_keller_lhv_2026.py`, at PA grain. Strike accrual is
reconstructed independently as a cumulative count of `type != 'B'` (called strike, swinging
strike, foul, ball in play) — **it does not read the `strikes` column at all**, so agreement
with your function is evidence rather than tautology.

| Variant | Definition | Keller (146 PA) | LHV staff ex-Keller (3,714 PA) |
|---|---|---|---|
| **A — as written** | 2nd strike by pitch 2 **and** PA reached pitch 3, OR ground ball in pitches 1-3 | **.411** | **.366** |
| **B — two strikes by pitch 2** | 2nd strike on or before pitch 2 (no survival condition), OR ground ball in pitches 1-3 | **.452** | **.408** |
| **C — two strikes by pitch 3** | 2nd strike on or before pitch 3, OR ground ball in pitches 1-3. *Literal reading of your sentence* | **.637** | **.604** |

**Spread A→C: 22.6 points on the same pitcher, same data.**

The A/B gap (4.1 points) is the survival condition: a ball in play on pitch 2 after one prior
strike accrues the second strike but ends the PA, so A misses it and B catches it.

### Why the recommendation is A, not C

| | Variant A | Variant C |
|---|---|---|
| Keller | .411 | .637 |
| Staff | .366 | .604 |
| **Staff spread (min→max, ≥40 PA)** | **~.30 → .43** | compressed near a league constant |
| Matches your ~40% Mayza anchor | **yes** | no |
| Discriminates between pitchers | **yes** | barely |

60% of all plate appearances reaching two strikes within three pitches is close to a
structural property of baseball, not a pitcher skill. **A is the better instrument.** But A
should then be named for what it actually measures, rather than inheriting the interview's
"within 3 pitches" phrasing — otherwise the definition and the label disagree forever.

---

## 4. The recommended ratified spec

| Field | Value |
|---|---|
| **KPI id** | `SR-M1` |
| **Name** | Quick At-Bat Rate |
| **Column** | `qab_rate` (retire `success_rate` — unqualified and collision-prone) |
| **Definition** | Share of plate appearances in which the pitcher either reached a two-strike count within the first two pitches, or induced a ground ball within the first three pitches |
| **Formula** | `qab_rate = qab_successes / total_pa` |
| **Grain** | Plate appearance |
| **Valid levels** | `pitcher`, `player_name`, `game_pk`, `game_date`, `stand`, `p_throws`, `home_team`, `game_year`, and any other **PA-invariant** dimension |
| **INVALID levels** | `pitch_name`, `pitch_type`, `balls`, `strikes`, `zone`, `description`, `inning`, `pitch_number` — anything that varies within a PA. Grouping on these splits one PA across several rows and inflates the denominator |
| **CDEs** | `game_pk`, `at_bat_number`, `pitch_number`, `strikes`, `type`, `bb_type` |
| **Population filter** | `game_type == 'R'`, deduplicated on `(game_pk, at_bat_number, pitch_number)` |
| **Min sample to publish** | 40 PA |
| **Direction** | Higher is better |
| **Edge cases** | Intentional walks count as PAs and always fail — **recommend excluding** (R6b). HBP counts as a PA, fails. Foul balls at two strikes cannot advance the count, so no correction needed. PAs ending on pitch 1-2 without two strikes or a ground ball correctly fail |

---

## 5. Six decisions

| # | Decision | Recommendation |
|---|---|---|
| **R1** | Which variant is ratified — A, B, or C? | **A** |
| **R2** | Ratified name and column? | **Quick At-Bat Rate / `qab_rate`** |
| **R3** | Apply the code hardenings in §6? | **Yes.** #1 (level guard) is required; the rest are recommended |
| **R4** | Minimum publication sample? | **40 PA** |
| **R5** | Ratify alongside the QR-1…QR-3 family from `uc-pps-019` to avoid a namespace clash? | **Yes** |
| **R6** | Is this reliever-only, as Mayza framed it, or role-agnostic? | **Role-agnostic.** Keller is a starter and the metric behaved sensibly on him. Keep a note that the framing was reliever-specific |
| **R6b** | Exclude intentional walks from the denominator? | Your call — small effect, cleaner definition |

---

## 6. Hardened candidate function

**Behaviourally identical to yours under variant A.** Verified this session at four levels —
`who`, `['who','stand']`, `pitcher`, `game_date` — on both Keller and the full LHV staff:
successes, denominators, and rates match exactly in every cell. The changes are a guard rail,
naming compliance, and legibility. Drop-in replacement for `Baseball Functions.ipynb`.

```python
def qab_rate(level, df):
    """SR-M1 — Quick At-Bat Rate.

    Share of plate appearances in which the pitcher either reached a two-strike
    count within the first two pitches, or induced a ground ball within the
    first three pitches.

    NOTE ON THE TWO-STRIKE LEG: `strikes` is the PRE-pitch count — it records
    the state the batter walked into on that pitch. So max(strikes) over pitches
    1-3 is the count displayed on pitch 3, which fires only when the second
    strike accrued on pitch 1 or 2 AND the PA survived to a third pitch. This is
    variant A of the SR-M1 ratification packet and it is deliberate: it
    discriminates between pitchers far better than the literal
    "two strikes within three pitches" reading, which is close to a league
    constant (~.60). See uc-pps-022 / SR-M1_ratification_packet.md.

    Origin: Tim Mayza, On Pattison — a two-pitch reliever's goal is the quick
    at-bat. Ratified role-agnostic; the original framing was reliever-specific.

    Grain: plate appearance. `level` MUST be PA-invariant.
    CDEs: game_pk, at_bat_number, pitch_number, strikes, type, bb_type.
    """
    if isinstance(level, str):
        level = [level]

    # --- guard rail: a within-PA-varying level silently inflates the denominator
    WITHIN_PA = {'pitch_number', 'pitch_name', 'pitch_type', 'balls', 'strikes',
                 'zone', 'description', 'type', 'bb_type', 'events', 'des',
                 'inning', 'plate_x', 'plate_z', 'release_speed'}
    bad = WITHIN_PA.intersection(level)
    if bad:
        raise ValueError(
            f"qab_rate: level {sorted(bad)} varies within a plate appearance. "
            f"This metric is PA-grained; grouping on it splits one PA across "
            f"rows and inflates total_pas. Use a PA-invariant level "
            f"(pitcher, player_name, game_date, stand, ...)."
        )

    calc_level = ['game_pk', 'at_bat_number']
    calc_df = df[df.pitch_number < 4]

    # PAs that showed a 2-strike count within the first three pitches
    s2 = (calc_df.groupby(calc_level, as_index=False)
                 .agg(max_strikes=('strikes', 'max')))
    s2w = s2.loc[s2.max_strikes == 2, calc_level + ['max_strikes']]

    # PAs with a ground ball within the first three pitches
    gbw = (calc_df[(calc_df.type == 'X') & (calc_df.bb_type == 'ground_ball')]
           .groupby(calc_level, as_index=False)
           .agg(early_gb=('description', 'size')))

    z = (df.groupby(level + calc_level, as_index=False)
           .agg(max_pitch=('pitch_number', 'max'))
           .merge(s2w, on=calc_level, how='left')
           .merge(gbw, on=calc_level, how='left'))
    # narrow fillna — only the two merged count columns, so the function stays
    # safe if `level` ever carries nullable values
    z[['max_strikes', 'early_gb']] = z[['max_strikes', 'early_gb']].fillna(0)

    z['is_qab'] = np.where((z.max_strikes == 2) | (z.early_gb >= 1), 1, 0)

    out = (z.groupby(level, as_index=False)
             .agg(qab_successes=('is_qab', 'sum'), total_pas=('is_qab', 'size')))
    out['qab_rate'] = out.qab_successes / out.total_pas
    return out.round(3)
```

**Changes from your original, itemised:**

| # | Change | Why | Changes numbers? |
|---|---|---|---|
| 1 | Level guard rail raising `ValueError` | **The one real footgun, and it is not hypothetical.** `tm_success_rate('pitch_name', keller_df)` runs without error and returns denominators summing to **319** against a true count of **146 PA** — a 2.2× inflation, silently. The guard turns that into an exception | No |
| 2 | `success_rate` → `qab_rate`, `total_success` → `qab_successes` | Glossary naming compliance | No |
| 3 | `('des','size')` → `('description','size')` | `des` is null on ~73% of rows. Both count rows so the result is identical, but the original reads as if it were counting narratives | No |
| 4 | Ground-ball filter moved into the mask instead of `groupby(+['bb_type'])` then filter | Removes an intermediate frame and the `bb_type` column leaking into the merge | No |
| 5 | Narrow `.fillna(0)` to the two count columns | Whole-frame `fillna` is safe for *this* construction but breaks quietly if a nullable level is added later — your own comment flagged this | No |
| 6 | `total_pas` counts `is_qab` rather than `game_pk` | Same value; reads as "one row per PA" rather than "count of game ids" | No |
| 7 | Docstring carrying the pre-pitch-count semantics | So the next reader doesn't re-derive §2 | No |
| 8 | Dropped unused `max_balls` and `max_pitch` is retained only as the group anchor | `max_balls` was computed and never used | No |

---

## 7. What SR-M1 found on Keller (PROVISIONAL)

Reported under variant A. Verified three independent ways — your function, a vectorised
cumulative-sum reconstruction, and a per-PA Python loop. All three return **.411**.

| Cut | SR-M1 | Baseline | n (PA) |
|---|---|---|---|
| Overall | **.411** | .366 | 146 |
| vs LHB | .365 | .364 | 85 |
| vs RHB | **.475** | .368 | 61 |
| Starts 1-4 | .318 | — | 66 |
| Starts 5-8 | **.488** | — | 80 |

Rank: **5th of 28** LHV pitchers with ≥40 PA. Full leaderboard:
`out/dp_uc26_sr_m1_leaderboard.csv`.

**The metric earned its keep.** It independently reproduced both of UC #27's central findings
— the right-handed advantage and the mid-June approach inflection — from a completely
different construction than the whiff/chase/contact-quality panel those findings came from.
That convergence is the best argument in this packet that SR-M1 measures something real, and
the best argument that Keller's improvement is structural rather than a metric artefact.

---

## 8. Receipts

| Artefact | Path |
|---|---|
| Your function, verbatim, as executed | `dp_uc26_keller_lhv_2026.py` → `tm_success_rate()` |
| Three-variant harness | `dp_uc26_keller_lhv_2026.py` → `sr_m1_variants()` |
| Variant reconciliation | `out/dp_uc26_sr_m1_variants.csv` |
| Keller values | `out/dp_uc26_sr_m1_provisional.csv`, `_by_stand.csv`, `_by_half.csv` |
| Staff leaderboard | `out/dp_uc26_sr_m1_leaderboard.csv` |
| Triple-path verification | `dp_uc26_verification.py` → block J (checks J1-J5) |
| Full governance spec | `04_architecture_and_kpi_specs.md` §SR-M1 |
| Glossary conflict scan | `02_business_glossary_and_domains.md` §2 |
