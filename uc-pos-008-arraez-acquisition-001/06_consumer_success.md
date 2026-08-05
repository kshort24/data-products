# 06 — Consumer Success

**Agents:** `analytics-enabler` → `consumer-onboarding-agent` → `dashboard-specifier` → `query-builder`
**Layer 5 — Launch** · UC #32 · `uc-pos-008` · `dp_uc31`

---

## 1. Personas served

Gap G-1 recorded that the request named "personas within the Phillies batting department" without enumerating them. Four are inferred and each gets a different answer from the same product.

| Persona | Decision they own | Their entry point | What they must not do with it |
|---|---|---|---|
| **Hitting coach** | Whether and how to intervene in the approach | Report §2 and §7; dashboard *Indicators* tab | Do not read the .324 average as evidence the approach needs protecting *from* regression — it needs protecting *from coaching* |
| **Manager (Mattingly)** | Lineup slot; late-inning deployment | Report §6 and §7; dashboard *Lineup* tab | Do not act on the slot recommendation until OI-1 is resolved |
| **Analytics group** | Expectation setting; trade-value modelling | Report §2, §4, §8; all receipts | Do not reuse AR-1…AR-7 in other products until ratified (OI-2) |
| **Front office** | Public and internal messaging about the acquisition | Report bottom line and §7 final paragraph | **Internal — Restricted.** Not for external publication (02 §6) |

---

## 2. Persona guides

### 2.1 Hitting coach

**What this data product offers you.** A precise picture of a hitter whose profile sits at the extreme end of every distribution your other hitters occupy, and a specific list of what would break him.

**The three numbers that matter to you.**

| Metric | Value | What it tells you |
|---|---|---|
| Contact rate outside the zone | **89.2%** | The engine. Everything else is downstream of this |
| Bat speed / fast-swing rate | **61.6 mph / 0.0%** | He has no power gear. There is nothing to unlock |
| Attack angle, 2025 → 2026 | **3.9° → 7.6°** | An adjustment already happened, and it worked |

**Your actual decision: intervene or not.** The evidence says **not**, with one exception.

- *Do not chase launch angle.* The 2026 ISO of .117 is a career high built from doubles and triples. The adjustment that produced it is already in the swing. Pushing further trades contact for lift he has no bat speed to convert.
- *Do monitor O-contact.* It is the leading indicator. If 89.2% starts sliding, two-strike survival goes with it and the entire profile unwinds. That is your early-warning metric.
- *The one live conversation is left-handed pitching.* His .441 slugging against LHP sits on a **.256 xwOBA**. Walk rate 2.1%, strikeout rate triple his mark against righties. Frame it as matchup preparation, not a swing change — it is the only split where forcing a deeper count has a plausible payoff.

**What you should expect to see over the next month.** The batting average drifts down. This is not something you caused and not something to fix.

### 2.2 Manager

**What this data product offers you.** A priced answer to the lineup question, plus a tool the two-strike numbers unlock.

**The lineup answer, short.** The whole decision is worth **under four runs a season**. Your cleanup choice is defensible and is the better of the two options that have been discussed. Against the lineup that actually exists in the data — Turner leading off — moving Arraez up and Turner down would **cost** about 2.6 runs.

**Read §6.4 before you conclude the question is settled.** Cleanup maximises his own run creation *and* fixes the roster's worst on-base slot (+47 baserunners a season over the 2026 incumbents). Batting him second maximises what the lineup does with the runners he creates, because slots 3 and 4 convert better than slots 2 and 3 do. The gap between those two answers is about one run. Either is defensible; neither is worth an argument.

**The tool you may not have noticed.** He survives two strikes 90% of the time. Your next-best regular is at 67%; six of your ten regulars are under 63%. In a spot that needs a ball put in play — runner on third, fewer than two out, late — he is not marginally the best option on the roster, he is a different category of option.

**Before you act on the slot recommendation:** the analysis was built against a log in which Turner leads off. If your current card has Schwarber there, the sign of the recommendation changes. Confirm with the analytics group first (OI-1).

### 2.3 Analytics group

**Your entry point is the receipts, not the report.** Thirty CSVs in `out/`, indexed in `dp_uc31_receipt_index.csv`.

**Three things to know before reusing anything.**

1. **AR-1 … AR-7 are provisional.** Do not propagate them into other products until the DPO ratifies (OI-2). AR-1 and AR-4 are the strongest promotion candidates — both are roster-general.
2. **The `truncated_pa` fork.** If you compute a slash line off `get_stats` and compare it to anything built on this product's PA spine, they will differ by the `truncated_pa` count. 2026 is unaffected (zero occurrences). See 01 §3.4.
3. **`launch_speed` is populated on fouls from 2023.** Gate on `type == 'X'`. This has already bitten one prior UC.

**The regression call to hold the group to.** wOBA .337 against xwOBA .304, barrel rate 0.7%, exit velocity 86.0 mph. The projection is **.300–.310 wOBA** rest-of-season. It is falsifiable and it is written into the closure step.

### 2.4 Front office

**One paragraph.** He fixes a specific hole — the middle of the order was getting a .287 on-base percentage from the cleanup spot — and he brings a two-strike and scoring-position skill nobody else on the roster has. He is not a middle-of-the-order bat. In this model Schwarber outproduces him in **every** lineup slot by roughly 20 runs per 162 games. The acquisition is defensible on fit and on contact skill; it is not defensible as an upgrade in raw offensive value, and the .324 batting average will not hold.

---

## 3. Dashboard specification (`dashboard-specifier`)

**Artifact.** `dp_uc31_arraez_acquisition_dashboard.html` — single file, 111 KB, no build step, opens by double-click. Chart.js from CDN; all data inlined as JSON so it works offline once loaded and can be sent as one attachment.

| Tab | Answers | Controls | Charts |
|---|---|---|---|
| **Top line** | Q1 | Metric selector (BA/OBP/SLG/ISO/K%/BB%) | wOBA vs xwOBA line; slash bar; season table |
| **Indicators** | Q2 | Contact-measure selector | Contact-quality trend; discipline trend; batted-ball and bat-tracking tables |
| **Two strikes** | Q3 | Rank-by selector (survival / wOBA / SLG / RE24) | Roster benchmark bar; economy bar; own-history line |
| **Damage map** | Q4 | Metric selector; **hide thin samples** toggle | Group × hand grouped bar; platoon bar; pitch-type bar |
| **Scoring position** | Q5 | — | SPCR roster bar; context bar; own-history bar |
| **Lineup decision** | Q6 | **Two hitter selectors + two slot selectors** | Live swap verdict; SPRC by slot; slot opportunity; table-setting |
| **Governance** | — | — | DQ scorecard; freshness manifest; verification counts |

**The one interactive element that computes.** The Lineup tab's swap explorer sums two published SPRC values and reports the difference. It performs the same arithmetic as the `f7` receipt and is asserted equal to it by verification checks V-130 – V-132. Everything else on the page is a formatted receipt value.

**Design decisions worth recording.**
- **Arraez is coloured red in every benchmark chart, the roster in pale blue.** One consistent visual convention, so no legend is needed to find the subject.
- **Sample size lives in the tooltip, not the axis.** Keeps the charts readable without hiding the caveat — hovering any benchmark bar shows the underlying counts.
- **Thin samples are togglable, not hidden by default.** A reader must actively choose to remove them, so they cannot be unaware they existed.
- **The swap verdict greys out below 1 run** and prints "Inside the noise — this model cannot tell these apart." The tool refuses to imply precision it does not have.

**Deliberately not built.** No spray charts or zone plots — the analysis is about counts, contexts and order, not location, and a pretty heat map would have implied a spatial finding the product does not make.

---

## 4. Query patterns (`query-builder`)

Validated templates against the receipts. All assume `pandas` and a working directory of `out/`.

**Q: Is his two-strike skill holding up?**
```python
c1 = pd.read_csv("dp_uc31_c1_two_strike_by_year.csv")
c1[["game_year", "PA_2k", "K_in_2k", "tssr", "woba_2k"]]
# Watch tssr. Below .85 sustained = the acquisition thesis is in trouble.
```

**Q: Has the regression started?**
```python
a1 = pd.read_csv("dp_uc31_a1_season_line.csv")
a1["gap"] = a1.woba - a1.xwoba          # 2026 = +.033; 2019-25 mean ≈ .000
```

**Q: Price any lineup pair myself.**
```python
f5 = pd.read_csv("dp_uc31_f5_sprc.csv")
v  = lambda h, s: f5.query("hitter==@h and slot==@s").re24_per_162.iat[0]
swap = lambda hA, sA, hB, sB: (v(hA, sB) + v(hB, sA)) - (v(hA, sA) + v(hB, sB))
swap("Luis Arraez", 4, "Kyle Schwarber", 1)      # +0.65
swap("Luis Arraez", 4, "Trea Turner", 1)         # -2.58
# Anything under ~1 run is inside the model's noise.
```

**Q: Which pitches should we expect him to handle?**
```python
d1 = pd.read_csv("dp_uc31_d1_group_x_hand_2026.csv")
d1[~d1.thin].sort_values("xwoba_con", ascending=False)[
    ["pitch_group","p_throws","bip","slg","xwoba_con","avg_ev"]]
# Trust xwoba_con over slg. Only fastball-vs-RHP has both high.
```

---

## 5. FAQ

**Why does the report say he is not a wild at-bat hitter when the at-bats look wild?**
Because both are true of different parts of the plate appearance. Overall he sees 3.72 pitches per PA — below average. But once he has two strikes he chases 56% of the time and fouls off 42% of his swings. The endings are wild; the beginnings are efficient. Receipt `a3` and `c2`.

**How can he chase 32% of the time and still be an elite contact hitter?**
Those are not in tension. He is aggressive *and* he does not miss — 89.2% contact on pitches outside the zone. Chase rate measures swing decisions; contact rate measures what happens next.

**Is the .343 scoring-position conversion real?**
The mechanism is real and durable — he does not strike out, so the ball is in play. The *rate* is at the high end of his own seven-year range (.222 to .560). Plan on about .30.

**Why is the lineup effect so small? That contradicts what people say about lineup optimisation.**
It agrees with it. Published lineup-optimisation work generally finds a full-season spread of one to two wins between an optimal and a randomly ordered lineup, and far less between two *reasonable* orders. This model, built independently from 2026 Phillies data, reproduces that: four runs across all nine slots for one hitter.

**Can I add the AR-6 and AR-7 numbers to get a total?**
**No.** AR-6 already values his reaching base; AR-7 values what happens to the runners he creates. Adding them double-counts. See 02 §3.

**Why are Scenario A totals ~28 and Scenario B totals ~73?**
Because they contain different hitters. A prices Turner + Arraez; B prices Schwarber + Arraez, and Schwarber is far more productive in 2026. Compare within a framing only.
