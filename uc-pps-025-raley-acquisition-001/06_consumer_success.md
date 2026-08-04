# 06 — Consumer Success

**Layer 4 — Launch** · UC #31 · `uc-pps-025` · build `dp_uc30`
**Agents:** `analytics-enabler` → `consumer-onboarding-agent` → `query-builder`

---

## 6.1 `analytics-enabler` — how to use this data product

### What it answers

| Question | Where |
|---|---|
| What did we buy? | Report → *Bottom line*, *What he was and what he is now* |
| Are the results sustainable? | Report → *Bottom line #1*, era table (wOBA vs xwOBAcon vs hard-hit) |
| Is he healthy? | Report → monthly arc, velocity trend; `out/dp_uc30_monthly_arc.csv` |
| Is the look actually unusual? | Report → *The signature*; `out/dp_uc30_lhp_release_benchmark.csv` |
| Does the look affect tracking? | Report → *Does it actually change how hitters track him* |
| How does he attack each hand? | Report → *The approach, by batter hand* |
| What should we change? | Report → three persona sections + *Game-plan takeaways* |

### What it does **not** answer

* **Any opponent-specific matchup.** No opponent dimension exists — there is no assigned role. That is a follow-on UC.
* **Whether he will stay healthy.** The data shows stable post-surgery velocity. It cannot forecast an arm.
* **Why the sweeper flattened.** The receipts say *what* changed (+2.3 in IVB). Cause is a pitching-lab question.
* **Anything about his KBO years or pre-2020 career.**
* **Framing, catcher fit, or clubhouse factors.** Not in the data layer.

### Reading rules — non-negotiable

1. **Never quote a blended Raley number.** Every rate belongs to pre-TJ or post-TJ. If a figure has no era label, it is being misused.
2. **Post-TJ is 269 batters faced.** Read the n printed on every line. The vs-LHH split is 100 BF.
3. **RSA is a proxy** (r = 0.831 vs native `arm_angle`, residuals to ±14°). It orders pitchers low-slot to high-slot reliably; it does not reproduce a specific arm angle.
4. **Sightline Offset is geometry, not outcome.** It says where the ball starts. The tracking claim rests on miss-distance and contact-quality splits, and miss distance is 32 and 61 whiffs.
5. **RDI does not support the distinctiveness headline** and is published as a negative result. Do not cite it in support.
6. **xwOBAcon BIP counts are `size`-semantics** and run 2–5 high (open item O4). The rates are correct.

### Worked interpretation — the headline finding

> *"Sightline Offset vs LHH is 0.08 ft against a population average of 0.96 ft."*

**Means:** averaged across his post-TJ pitches, the ball leaves Raley's hand about **one inch** to the side of the centre of the left-handed batter's box — while the typical Phillies left-hander releases it about **11.5 inches** away. The ball emerges from behind the hitter's front shoulder rather than from across his body.

**Does not mean:** that left-handed hitters cannot see the ball, or that this alone makes him effective. The supporting evidence is that left-handers post a **.239 xwOBAcon against his .349 vs righties**, and that when they miss they miss by **3.76 inches vs 2.45**. The geometry is the mechanism; the splits are the effect; the samples are small.

**Act on it by:** prioritizing him into lineup segments containing left-handed hitters — *without* treating him as a specialist, because 70 of his 75 outings included at least one right-hander.

---

## 6.2 `consumer-onboarding-agent` — persona guides

### Persona A — Pitching Coach / Pitching Department

**Your decision:** what to work on first with a pitcher you have never had in your bullpen.

| Your KPI | Value | Why you care |
|---|---|---|
| Sweeper IVB, pre → post | 2.5 → **4.8 in** | The pitch lost its dive. This is the root cause |
| Sweeper whiff, pre → post | 37.2% → **23.2%** | The effect |
| Sweeper HB, pre → post | −17.6 → −16.8 in | Sweep is intact — it is depth, not sweep |
| RTD (post-TJ) | **5.3 in** vs 2.3 in noise | Sweeper release separates from the cutter |
| Velocity, pre → post | 85.4 → 85.0 mph | Fine. Do not chase it |
| RSA, pre → post | 63.6° → **60.8°** | The slot dropped. **Protect this** |

**Your section:** report → *For the pitching department*. Four actions, ordered.
**Do not:** "clean up" the delivery toward his 2021 slot. The lower, wider slot is the asset.

---

### Persona B — Catchers & Raley (the battery)

**Your decision:** what to call, pitch by pitch, by batter hand.

| vs LHH (100 BF) | vs RHH (169 BF) |
|---|---|
| Sweeper 40.3% · **27.1% whiff** · .210 xwOBAcon | Sweeper 38.9% · 20.5% whiff · **.468 xwOBAcon**, 53.7% hard-hit |
| Cutter 25.8% · .176 xwOBAcon | Cutter 24.8% · **26.7% whiff** · .277 xwOBAcon |
| Sinker 31.4% · **55.0% hard-hit** ⚠️ | Changeup 18.3% · **14.3% hard-hit** |
| Two-strike: sweeper 75% → **38.6% whiff** ✅ | Two-strike: sweeper 44.7% → **11.5% whiff** ⚠️ / cutter 20.3% → **48.0% whiff** ✅ |

**The one rule:** *sweeper is the out pitch to lefties and must finish off the plate; cutter is the out pitch to righties; never let the sweeper be the two-strike pitch to a right-hander unless it is leaving the zone.*

**Your section:** report → *For the battery*.

---

### Persona C — Manager

**Your decision:** which inning, which score state, how many hitters, how often.

| Your KPI | Value |
|---|---|
| Most common entry | **7th inning — 34 of 75 outings** |
| Highest-frequency spot | 7th, leading 1–3 — 18 outings |
| Typical outing | **median 14 pitches, 3–4 batters** |
| Entered with inherited runners | 26 of 75 |
| Faced ≥1 RHH | **70 of 75** — he is not a specialist |
| Back-to-back appearances | 12 of 75 · velo −0.9 mph · **BB rate 2.6%** |
| Expectation | **Do not plan around .239 wOBA.** Plan around ~.290–.310 |

**Your section:** report → *For the manager*.
**Watch:** right-handed contact (.349 xwOBAcon, 36.0% hard-hit) is the exposure until the sequencing changes.

---

## 6.3 `query-builder` — validated query templates

All templates assume the entity lock and dedup are applied first.

```python
import pandas as pd, numpy as np

RALEY, PRE_END, POST_START = 548384, "2024-04-19", "2025-07-19"

def load():
    d = pd.read_parquet("data/opponents/raley.parquet")
    d = d[(d.pitcher == RALEY) & (d.game_type == "R")]                 # ENTITY LOCK
    d = d.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])  # DEDUP
    d["game_date"] = pd.to_datetime(d.game_date)
    d["era"] = np.where(d.game_date <= PRE_END, "Pre-TJ",
               np.where(d.game_date >= POST_START, "Post-TJ", "REHAB GAP"))
    assert (d.era == "REHAB GAP").sum() == 0     # partition must be exhaustive
    return d

def tracked(d):
    return d[d.pitch_name.notna()]               # quarantine untracked rows
```

**Q1 — usage and whiff for a given pitch against a given hand, post-TJ**

```python
t = tracked(load())
t = t[t.era == "Post-TJ"]
p = t[(t.pitch_name == "Sweeper") & (t.stand == "R")]
SW = {"foul","foul_bunt","foul_tip","hit_into_play","missed_bunt",
      "swinging_pitchout","swinging_strike","swinging_strike_blocked"}
WH = {"foul_tip","missed_bunt","swinging_pitchout",
      "swinging_strike","swinging_strike_blocked"}
usage = len(p) / len(t[t.stand == "R"])
whiff = p.description.isin(WH).sum() / p.description.isin(SW).sum()
```

**Q2 — Sightline Offset for any pitcher** *(the reusable one)*

```python
BOX = 3.208
def sightline_offset(df):
    """Requires the coordinate convention: +x is the LHH side."""
    center = np.where(df.stand.values == "L", BOX, -BOX)
    return float(np.mean(np.abs(df.release_pos_x.values - center)))
```

**Q3 — score any pitcher against the Phillies LHP release population**

```python
import glob
lhp = pd.concat([pd.read_parquet(f) for f in glob.glob("data/phillies/phils_*.parquet")])
lhp = lhp[(lhp.phillies_role=="pitching") & (lhp.p_throws=="L") & (lhp.game_type=="R")]
lhp = lhp.drop_duplicates(["game_pk","at_bat_number","pitch_number"])
lhp = lhp[lhp.pitch_name.notna()]
pop = (lhp.groupby(["pitcher","player_name"])
          .agg(n=("release_pos_x","size"), rel_x=("release_pos_x","mean"),
               rel_z=("release_pos_z","mean")).reset_index())
pop = pop[pop.n >= 300]                       # inclusion threshold
pop["rsa"] = np.degrees(np.arctan2(pop.rel_z, pop.rel_x.abs()))
# score the subject AGAINST this population — never append him before the centroid
```

**Q4 — xwOBA on contact (the only sanctioned form)**

```python
def xwobacon(df):
    bip = df[df.type == "X"]
    s = bip.estimated_woba_using_speedangle.dropna()
    return float(s.mean()), len(s)     # returns the TRUE n, avoiding open item O4
```

⚠️ Never use `estimated_woba_using_speedangle.mean()` over all pitch rows (uc-pps-021 O1).
