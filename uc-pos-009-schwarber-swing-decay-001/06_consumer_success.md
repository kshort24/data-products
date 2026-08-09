# 06 — Consumer Success

**Layer 4 — Launch** · Departments: Consumer Success ∥ Marketing
**Agents:** `analytics-enabler` · `consumer-onboarding-agent` · `dashboard-specifier` · `query-builder` · `semantic-modeler`
**Use case:** `uc-pos-009-schwarber-swing-decay-001` · **Build:** `dp_uc32`

---

## 1. `semantic-modeler` — the KPI semantic layer

Rules that prevent metric drift once this product is consumed.

### Aggregation constraints

| KPI | Additive? | Valid dimensions | **Invalid** |
|---|---|---|---|
| SW-1 Sweet-Spot Rate | No — ratio | season, month, phase, pitch group, velocity band, direction | Cannot average across groups. Recompute from counts |
| SW-2 Ideal-Contact Rate | No — ratio | same as SW-1 | same |
| SW-3 Fast-Swing Rate | No — ratio | season/month/phase (2024+) | **Any dimension before 2024** |
| SW-4 Squared-Up Rate | No — ratio | season/month/phase (2024+) | Any dimension before 2024 |
| SW-5 Attack-Angle Fit | No — ratio | season/month/phase (2025+) | **Any dimension before 2025** |
| SW-6 Contact Depth | No — mean | season/month/phase (2025+) | Any dimension before 2025; **any comparison to a prior phase without also showing the prior season** |
| SW-7 Coverage | No — ratio | must match its companion's grain | Cannot be reported alone |
| SW-8 Damage-Band Rate | No — ratio | season, month, phase, pitch group | Cross-player comparison without archetype validation |
| SW-9 Blast Rate | No — ratio | season/month/phase (2024+) | Any dimension before 2024 |

### Governance rules — binding on any downstream consumer

1. **Coverage travels with the metric.** No bat-tracking figure may be displayed without its SW-7 coverage at the same grain.
2. **Never fill a null in a bat-tracking column.** A null means *not measured*. Filling it violates the DPO's recorded decision and breaks DQ-10/11.
3. **Never average a rate across groups.** Recompute from numerator and denominator.
4. **SW-1 never travels alone for a power hitter.** Pair with SW-2 or SW-8. This is the report's central finding, encoded as a rule.
5. **SW-6 comparisons require a prior-season anchor.** A phase-to-phase depth change is uninterpretable without it.
6. **Sample size is displayed on every row of every split.** Non-negotiable at these denominators.
7. **SW-4 and SW-9 are provisional** pending OI-3.

---

## 2. `analytics-enabler` — how to use this data product

### What it answers

- Has Schwarber's power declined in 2026, and by how much, against his own history?
- Has it declined *within* 2026, and when?
- Is the cause physical (bat speed / swing mechanics) or behavioural (swing decisions / contact point)?
- Which pitch types, velocities, counts and field directions carry the loss?
- What should each persona in the value stream actually do?
- How should sensor-era NULLs be handled, and what would imputation have cost?

### What it does **not** answer

- Whether he will recover (no projection model).
- Whether this is age (no aging model — it reports observed bat speed only).
- Whether Citizens Bank Park or opponent quality explain part of it (no adjustment for either).
- Whether the chase-rate rise *causes* the launch-angle shift (correlation is reported; causation is not claimed).
- Anything about health, workload or fatigue (**deliberately out of scope** — see 02 §6 PW-3).

### Reading order

1. **Report §Bottom line** — 90 seconds, the whole finding.
2. **Report §1** — price the baseline before believing the decline.
3. **Report §3** — the mechanism, and why sweet-spot % misled.
4. **Report §8** — your persona's actions.
5. **Report §10** — the caveats. Read these before quoting a number.
6. Dashboard for slicing; receipts for anything you want to re-derive.

### The three numbers to remember

| | |
|---|---|
| **74.2 mph** | Bat speed, 2025 and 2026. Unchanged. Nothing physical was lost |
| **21.7% → 14.9%** | Share of contact in the 20–32° damage band. The mechanism |
| **25.5%** | Chase rate — a nine-year high, and the most actionable lever |

### Interpretation traps — read before quoting

| Trap | Correction |
|---|---|
| "Sweet-spot % is up, so contact is fine" | **No.** SW-1 rose *during* the collapse. Use SW-8 or SW-2 |
| "He lost 1.8 inches of extension" | **Misleading.** Phase B ≈ his 2025 norm. Phase A was the anomaly |
| "Barrel rate fell 59.5%, so he's finished" | **Overstated.** Phase A exceeded his career-best season. The truth is between the phases; the season line (16.9%) reflects it |
| "August shows a total collapse" | **11 balls in play.** No weight |
| "He's 80th percentile in bat speed" | **Pool n = 5.** A label, not a statistic |
| "The bat speed is flat, so nothing is wrong" | **No.** K rate 34.8% is a career high and is a real signal |

---

## 3. `consumer-onboarding-agent` — persona guides

Seven personas. Full text in report §8 and in the dashboard's **Personas & actions** tab.

| Persona | Finding for them | Lever they control | KPI to watch |
|---|---|---|---|
| **Hitting Coach** | Not a mechanics problem. Do not rebuild the swing | Contact depth and timing; breaking-ball plan | SW-8 Damage-Band Rate — target > 20% |
| **The Player** | Your bat is as fast as in your best season | Which pitches, not how hard | Chase rate, weekly — 25.5% → 21.5% |
| **Advance Scouting (own)** | Opponents found a plan and it works | Counter-plan for breaking-ball shapes | Breaking-ball barrel & whiff, by series |
| **Manager** | Season line is still top-of-lineup quality | Lineup patience; matchup protection | Rolling 60-BIP barrel rate, not the box score |
| **Front Office** | Bat speed shows zero decline — not an aging curve | Model specification; valuation inputs | K rate and chase rate over the next 200 PA |
| **Performance / Sports Science** | No fatigue signature in the tracking data | Rest justified on recovery, not power | Monthly bat speed — the falsification test |
| **Opposing Advance Scout (mirror)** | What the other side already sees | — | The three exploitable weaknesses |

**Why the mirror persona exists.** Knowing what an opponent can see is itself actionable, and it makes the counter-plan concrete. It is also the reason the product is blocked for external publication (02 §6 PW-2).

---

## 4. `dashboard-specifier` — spec, and the built artefact

**Delivered:** `dp_uc32_schwarber_swing_decay_dashboard.html` — single self-contained file, 104 KB, Chart.js from cdnjs, all data inlined as JSON. Works offline. **Computes nothing** — reads receipts only.

| Tab | Purpose | Charts | Controls |
|---|---|---|---|
| **Overview** | The verdict in eight cards + full career line + every phase delta | — | — |
| **Within-season decay** | The dissociation | Rolling contact quality; rolling bat speed; monthly combo (bar + line) | — |
| **Launch angle** | The mechanism | Grouped bar (phase shares) + xwOBAcon overlay line | — |
| **Swing path & bat speed** | Shape is unchanged | Attack-angle → barrel bar | — |
| **Where it went** | Slicing | — | **Split-by selector:** pitch group / velocity band / spray direction |
| **NULL policy** | The governance finding | Measured vs imputed line | — |
| **Personas & actions** | Seven action cards | — | — |
| **Governance** | DQ, verification, closure criteria | — | — |

### Design decisions

- **Card colour encodes verdict, not direction.** Amber is reserved for metrics that *improved while production fell* (sweet spot, hard hit) — the report's central trap, made visible at a glance.
- **Sample size is in the header pills** (`235 PA / 120 BIP vs 259 PA / 122 BIP`) so it is impossible to read a delta without seeing its denominator.
- **Thin cells are coloured red inline** (< 15 BIP) rather than footnoted.
- **`not measured` renders as grey text**, never as a blank or a zero — a blank invites a reader to assume a missing value; the words state the fact.
- **No pie charts.** Per brand guidelines.
- **Rounding follows the brand rules:** BA/OBP/SLG/OPS/xwOBA to three decimals with no leading zero; rates as percentages to one decimal.

---

## 5. `query-builder` — validated templates

Each returns the number quoted in the report. Assumes `%run "Baseball Functions.ipynb"` and `phils_sc, pos, pps = get_phillies_data()`.

```python
# --- 0. The locked frame. Every query below starts here. -------------------
SCH = 656941
PITCH_KEY = ['game_pk', 'at_bat_number', 'pitch_number']
nphl_sch = pd.read_parquet('data/opponents/schwarber.parquet')

car = pd.concat([nphl_sch[nphl_sch.batter == SCH],
                 pos[pos.batter == SCH]], ignore_index=True)
car = car.drop_duplicates(subset=PITCH_KEY)
car = car[car.game_type == 'R'].copy()
car['game_date'] = pd.to_datetime(car.game_date)

# REQUIRED: Statcast parquet uses nullable dtypes; pd.NA breaks boolean masks.
for c in ['launch_speed', 'launch_angle', 'launch_speed_angle', 'bat_speed',
          'attack_angle', 'swing_path_tilt', 'zone']:
    car[c] = pd.to_numeric(car[c], errors='coerce').astype('float64')
```

```python
# --- 1. Bat speed by season. THE CORRECT WAY: measured swings only. --------
SWINGS = ['foul','foul_bunt','foul_tip','hit_into_play','missed_bunt',
          'swinging_pitchout','swinging_strike','swinging_strike_blocked']
sw = car[car.description.isin(SWINGS)]

bs = sw.groupby('game_year').agg(
    swings=('des','size'),
    measured=('bat_speed','count'),
    bat_speed_mu=('bat_speed','mean'),
)
bs['coverage'] = (bs.measured / bs.swings).round(3)     # SW-7 — always publish this
# DO NOT .fillna() ANY COLUMN OF THIS TABLE.
# NULL means the sensor did not exist. See 02 §3.
```

```python
# --- 2. SW-8 Damage-Band Rate — the metric that should replace sweet spot --
bip = car[car.type == 'X']
damage = (bip.launch_angle.between(20, 32, inclusive='left')
             .groupby(bip.game_year).mean().round(3))
```

```python
# --- 3. SW-2 Ideal-Contact Rate -------------------------------------------
ideal = ((bip.launch_angle.between(8, 32) & (bip.launch_speed >= 95))
         .groupby(bip.game_year).mean().round(3))
```

```python
# --- 4. The phase split — data-driven, NOT calendar-driven ----------------
b26 = car[(car.game_year == 2026) & (car.type == 'X')].sort_values(
    ['game_date','game_pk','at_bat_number','pitch_number']).reset_index(drop=True)
split_date = b26.loc[len(b26)//2, 'game_date']          # equal BIP either side
d26 = car[car.game_year == 2026].copy()
d26['phase'] = np.where(d26.game_date < split_date, 'A', 'B')
```

```python
# --- 5. Launch-angle redistribution — the mechanism ------------------------
b = d26[d26.type == 'X'].copy()
b['band'] = pd.cut(b.launch_angle,
                   bins=[-90,-10,8,20,32,50,90],
                   labels=['Topped','Low drive','Ideal low','Ideal high','Under','Pop up'],
                   right=False).astype(str)             # .astype(str) avoids the
                                                        # categorical groupby defect (05 §4 B-2)
pd.crosstab(b.band, b.phase, normalize='columns').round(3)
```

```python
# --- 6. Reproduce any published number from its receipt -------------------
import pandas as pd
pd.read_csv('out/dp_uc32_b6_phase_delta.csv')          # every phase delta
pd.read_csv('out/dp_uc32_a2_bat_tracking_coverage.csv')# the coverage register
pd.read_csv('out/dp_uc32_x1_imputation_harm.csv')      # the NULL-policy evidence
```

**Anti-pattern — do not do this** (it is the original intake query, and it is wrong three ways):

```python
# WRONG: no dedup, no game_type filter, and it imputes the mean bat speed.
z = ...fillna(df.groupby('player_name').agg(mu_bs=('bat_speed','mean')).mu_bs.unique()[0])
```

1. Missing `drop_duplicates(PITCH_KEY)` after the concat.
2. Missing `game_type == 'R'` — 1,275 spring/postseason pitches leak in.
3. The `fillna` fabricates 7,021 swings across nine seasons. See report §7.
