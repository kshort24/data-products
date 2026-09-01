# 06 · Consumer Success — uc-pps-028 (UC #39 / dp_uc39)

**Layer 4 agents:** `analytics-enabler` · `consumer-onboarding-agent` · `query-builder` · `dashboard-specifier`

---

## 1 · What this data product answers

| Question | Where | Caveat that travels with the answer |
|---|---|---|
| Has Luzardo been good since late April? | report §1–2, dashboard tile 1 | Yes, and it survives every boundary tested |
| Is he the most consistent Phillies starter? | report §2, dashboard §2–3 | **Depends entirely on which axis you mean** — see below |
| Did the 2nd-time-through problem persist? | report §3, dashboard tripwire table | No. .368 → .279 (171 → 73 PA) |
| What changed in his arsenal? | report §5, dashboard arsenal panel | Sweeper up and better; changeup being shelved |
| How should he attack Arizona? | report §6, dashboard attack-plan panel | **Profile-driven.** 22 PA of 2026 H2H, no confirmed lineup |
| When do I go get him? | report §7 (manager) | The old TTO rule is retired; the new constraint is the K rate |

## 2 · Persona onboarding

### Human Data Product Owner
**Start at:** report Bottom Line, then §2 and the dashboard's breakpoint scan.
**What you asked for and what you got:** you offered two claims and asked me to lead. One held
completely; the other went to a different pitcher. The scan chart is the single most useful object
in the package — it shows a rank moving as the window moves, which is what "boundary-dependent"
means in a picture.
**The one sentence to carry into a meeting:** *"Luzardo has the staff's best contact quality at every
way of cutting the season; Sánchez has the better floor; and Luzardo's genuine consistency edge is
that he throws 90–110 pitches every fifth day and never misses."*
**Owed decisions:** ratify or retire CN-1…CN-6 and AR-1 (E-2); paste the ledger patch (E-3).

### Manager
**Start at:** report §7 → Manager, then §3.
**What changed for you tonight:** the `uc-pps-017` rule "the danger opens the second time through"
no longer has a number behind it. Your live constraint is workload — 109 / 110 / 104 pitches in his
last three, the three highest of his season — and the K rate, because §4 says the harder contact he
now allows is only affordable while he is missing bats at 32%.

### Pitching department
**Start at:** report §5 and §6's by-stand tables.
**Your live decision:** the sinker against right-handed hitters — .404 xwOBA, 10.8% whiff, and an
11.9% chase rate that says righties simply do not offer at it. Usage is already down to 12.1% against
that side. Arizona's current-era hitters in this record skew heavily right-handed.
**Your open question:** is the changeup being retired on purpose (20.3% → 14.3%) or drifting? It is
still 23.3% of his mix to righties, the population it performs worst against.

### Catcher
**Start at:** report §7 → Catcher and the two-strike menu in §6.
**What the numbers say about your game-calling:** first-pitch strike back to 65.4% with chase held at
33.9% and no walk-rate cost. Do not adjust. Know that the two-strike menu to righties is thinner than
it looks — sweeper 44.5%, then a 4-seam that whiffs at .197.

### Analyst
**Start at:** `out/dp_uc39_payload.json` and the receipts index in `04` §3.
**What is reusable:** the `start_frame` atom and the CN family generalise to any starter; the TR-2
scan generalises to any stated era boundary; `AR-1` generalises to any team-keyed opponent study.

## 3 · How to read a CN axis without misquoting it

**Never say "he's the most consistent."** Say *most consistent by CN-1, among 5 Phillies starters with
≥8 starts, in the window opening 2026-05-01 — a rank that does not hold if the window opens a week
earlier.* That is semantic rule **S-1** and guardrail **G8**, and it exists because this exact
sentence is how the premise arrived.

The six axes and the plain-English question each answers:

| Axis | The question it answers | Luzardo |
|---|---|---|
| CN-1 | How much does one start differ from the next? | **1st** at this boundary, 3rd on the full season |
| CN-2 | How often is the start usable (≥5 IP, ≤3 R)? | 2nd — Sánchez 81.0% vs 76.2% |
| CN-3 | How often does the start wreck the day? | tied 3 of 21 with Nola and Wheeler; Sánchez 2 |
| CN-4 | Within any three starts, how wide is the spread? | **1st** at this boundary |
| CN-5 | Does the manager know what he's getting? | **1st, at every boundary** — 90–110, SD 5.8 |
| CN-6 | Can you count on the innings? | 2nd — Sánchez 6.35 vs 6.03 |

## 4 · Query recipes

```python
import pandas as pd
OUT = "data-products/uc-pps-028-luzardo-vs-dbacks-001/out/"

# 1. The premise, adjudicated — one table
rk = pd.read_csv(OUT+"dp_uc39_consistency_ranking.csv")
rk[rk.name.str.startswith("Luzardo")].sort_values("axis")[["axis","value","rank","n_cohort"]]

# 2. Is the ranking a finding or an artefact? (the falsification receipt)
sc = pd.read_csv(OUT+"dp_uc39_consistency_breakpoint_scan.csv")
sc[["window_start","lz_starts","agg_xwoba__rank","cn1_xwoba_sd__rank"]]
#    agg_xwoba__rank is 1 in every row; cn1_xwoba_sd__rank is not -> that is the whole finding

# 3. Did the parent product's numbers survive?
pd.read_csv(OUT+"dp_uc39_uc17_reproduction_check.csv").query("match != 'PASS'")   # -> empty

# 4. Tonight's plan against right-handed hitters
pl = pd.read_csv(OUT+"dp_uc39_attack_plan_by_stand.csv")
pl[pl.stand=="R"].sort_values("usage", ascending=False)

# 5. Only the Arizona hitters who are actually current
h = pd.read_csv(OUT+"dp_uc39_ari_h2h_batters.csv")
h[h.tier.str.startswith("current")].sort_values("plate_apps", ascending=False)

# 6. Re-run the whole thing after tonight (post-game backtest)
#    python dp_uc39_luzardo_vs_dbacks.py && python dp_uc39_verification.py
```

## 5 · dashboard-specifier — what shipped and why

| Panel | Form | Why this form |
|---|---|---|
| Verdict block | prose, leading | The answer is a *judgement between two claims*; no chart states that |
| 6 stat tiles | big-number | The figures a reader needs before any chart |
| Start-by-start | bars (runs) + line (xwOBA), one x-scale | The two measures share a time axis but not a scale, so the runs bars are recessive and the xwOBA line carries the read. Window filter = the premise made adjustable |
| Consistency map | scatter, axis selector | Places *variance* against *level* on two axes — the entire argument in one picture. The selector lets a sceptic try a different definition of "consistent" |
| Breakpoint scan | rank lines, 8 boundaries | A flat line = a finding; a moving line = an artefact. Reads at a glance |
| Tripwire table | table + status chips | 16 discrete verdicts; a chart would hide the notes |
| Arsenal drift | grouped bars, faded = H1 | Direct H1→H2 comparison per pitch, with a measure selector |
| Attack plan / H2H | tables + handedness and recency toggles | Operational lookup, not a trend |

**Access.** Offline copy `dp_uc39_luzardo_dashboard.html` — one file, no CDN, opens with no network.
Published copy — a private hosted page, same payload, adds a webfont pairing the offline copy cannot
vendor. Divergence documented in `07` §3.

**Not built:** a live pitch-by-pitch tracker (no live feed in the plane) and any predictive line
(no model in scope, and `05` A-7 is served by descriptive evidence).
