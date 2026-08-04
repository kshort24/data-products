```yml
# Identity
name: Brooks Raley Acquisition Read 20260804 PHI
id: uc-pps-025-Brooks Raley PHI 20260804
description: >
  Trade-deadline acquisition onboarding dossier for LHP Brooks Raley, acquired
  by the Phillies at the 2026 deadline. Splits his full Statcast-era record at
  Tommy John surgery and reads the post-TJ tier as "the pitcher we bought."
  Deep-dive angles: (1) a release-point benchmark against all 28 Phillies
  left-handers with 300+ pitches since 2015, and whether that geometry changes
  how hitters track the ball; (2) approach and outcomes by batter hand;
  (3) actions for the pitching department, the battery, and the manager.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — Ready for DPO Sign-off
priority: High

# People
personas: Manager, Pitching Coach, Catcher, Pitcher, Pitching Analyst
owner: Kellen Short

# Relationships
parent_use_case: >
  uc-pps-024 (Kilian acquisition read — first acquisition-onboarding variant).
  Lineage: UC#3 Luzardo -> UC#8 Nola/WAS -> UC#11 Rangel -> UC#29 Painter
  (self-scout) -> UC#30 Kilian (acquisition) -> UC#31 (this).
sub_use_cases: []

# Metadata
created: 2026-08-04
last_updated: 2026-08-04
ledger_id: UC #31
build_artifact: dp_uc30_raley_acquisition_read.py
governance_trail: 00_ .. 07_ in data-products/uc-pps-025-raley-acquisition-001/
verification: dp_uc30_verification.py — 661/661 PASS
dq_scorecard: out/dp_uc30_dq_scorecard.csv — 38/38 PASS

# Data References
kpis: >
  wOBA, BA/OBP/SLG, K%, BB%, HR%, whiff rate, chase rate, CSW rate,
  in-zone rate (strict), putaway rate, first-pitch strike rate, hard-hit rate,
  xwOBA on contact (xwOBAcon);
  NEW: Release Slot Angle (RSA), Release Distinctiveness Index (RDI),
  Sightline Offset (SLO), Release Tipping Delta (RTD)
data_domains: >
  Pitch Profile, Pitch Outcomes, At-Bat Outcomes, Batted Ball Profile,
  Strike Zone, Bullpen Deployment
sources: >
  data/opponents/raley.parquet (subject, entity lock pitcher==548384);
  data/phillies/phils_2015..2026.parquet (benchmark, LHP >=300 pitches, n=28);
  wOBA and FIP Constants.csv
freshness: cache through 2026-08-02 (T-2 as of build)
sensitivity: Internal — Restricted. External publication blocked.
```

# Brooks Raley — Trade-Deadline Acquisition Read

> **Document status:** Build complete.
> **Deliverable:** `dp_uc30_raley_acquisition_read_report.pdf` (11 pages, Phillies-branded) + markdown source
> **Governance trail:** `00_dpo_orchestration_record.md` → `07_platform_marketing.md`
> **Receipts:** `out/` — 21 CSVs, 5 figures, DQ scorecard, freshness manifest, verification results
> **Build:** `dp_uc30_raley_acquisition_read.py` — the only place any number is computed

---

## Business Context

### Problem Statement

We just acquired Brooks Raley at the deadline and nobody in this organization has ever worked with him. He's a wily veteran and my guess is he gives you a funky look from the left side — but that's a guess, and I'd like it either confirmed or killed with numbers.

The complication is that his career has a seam in it. He had Tommy John surgery in 2024. Quoting a blended career line would describe a pitcher who no longer exists, and quoting only the post-surgery line throws away the context that tells you what the surgery cost him. I want both, kept apart.

What I actually need out of this is decisions. The pitching department gets him for the first time and needs to know what to work on. The catchers and Raley himself need a pitch-selection plan against each hand. The manager needs to know which inning, which score state, and how often he can run him out there. And I want the release-point question answered properly — not asserted, but benchmarked against every left-hander this organization has had in the Statcast era, with an honest answer on whether it actually affects how hitters pick the ball up.

### Business Questions — Answered

**Q1. What do his top-line results say?**
Post-TJ (269 BF): **.185/.257/.273, .239 wOBA**, 24.2% K, 7.4% BB, **2 home runs**. Excellent. Pre-TJ (770 BF) he was .205/.286/.320, .271 wOBA, 29.0% K.

**Q2. What do the underlying indicators say, and what should we expect?**
That the results are outrunning the contact. **Hard-hit rate rose 26.2% → 33.1%** and xwOBAcon is **.307** against a .239 wOBA. A 0.7% home-run rate on 33% hard contact is not a repeatable skill. **Expect regression toward roughly a .290–.310 wOBA** — still a useful late-inning reliever, but do not build the bullpen around the line he has posted.

Bat-missing is genuinely down: whiff **29.9% → 21.9%**, almost entirely the sweeper (**37.2% → 23.2%**), which has **gained 2.3 inches of induced vertical break** — it lost its depth. Velocity is fine and trending up (July 2026 was his hardest post-surgery month at 86.4 mph), so this is a shape problem, not a health problem.

**Q3. Is the look genuinely unusual?**
Yes, and the surgery made it more so. His release slot **dropped and widened** post-TJ (RSA 63.6° → 60.8°; release point moved 3.7 inches further arm-side). At 60.8° he has the **5th-lowest slot among 30 Phillies left-handers since 2015** — below Hamels, Suárez, Sánchez, Luzardo, Strahm and Alvarado.

Against a left-handed hitter, **Sightline Offset is 0.08 ft — about one inch** — versus a population average of **0.96 ft**. The ball leaves his hand essentially on the left-handed hitter's own eye line, emerging from behind his front shoulder. Against right-handers the same geometry yields **6.34 ft** of cross-body travel.

**Q4. Does it change how hitters track the ball?**
Partially, and the honest answer is qualified. He does **not** miss more left-handed bats (20.6% vs 22.6% whiff) — but **when left-handers miss, they miss by 53% more distance** (3.76 vs 2.45 inches), they shorten their swings, and their contact quality is far worse (**.239 xwOBAcon vs .349**). The picture is a defensive, imprecise hitter rather than an overpowered one. Caveat printed prominently: miss distance rests on 32 and 61 whiffs.

One of the four new KPIs, the Release Distinctiveness Index, **does not support this conclusion** (1.26 vs a population mean of 1.20) and is published as a negative result with an explanation — RDI is a distance and ignores direction.

**Q5. How does he attack each hand?**
**vs LHH (100 BF, .213 wOBA, .239 xwOBAcon):** sweeper 40.3%, sinker 31.4%, cutter 25.8%, no changeup. Two-strike sweeper 75% for a 38.6% whiff rate — the approach is close to right. The leak is the **sinker: 55.0% hard-hit**.
**vs RHH (169 BF, .255 wOBA, .349 xwOBAcon):** sweeper 38.9%, cutter 24.8%, changeup 18.3%, sinker 18.0%. **His most-used pitch is his worst pitch here** — the sweeper lands in the zone 60.3% of the time, is chased only 25.5%, and yields **53.7% hard contact and a .468 xwOBAcon**. Eleven of sixteen extra-base hits allowed came on it.

**Q6. Is he a specialist?**
No. **70 of 75 post-TJ outings included at least one right-hander**, and he threw 661 pitches to righties against 361 to lefties.

### Actions

**Pitching department**
1. **Restore depth to the sweeper** (+2.3 in IVB since surgery). Root cause of the whiff decline and the RHH exposure both.
2. **Fix the sequencing before anything mechanical** — free, available this week.
3. **Clean up the sweeper release** — 5.3 in of separation from the cutter against 2.3 in of natural noise. Findable.
4. **Leave the slot alone.** The lower, wider delivery is the asset. Do not correct it toward 2021.

**Battery**
- vs LHH: sweeper is the out pitch and must finish off the plate. **Cut the sinker** (55.0% hard-hit).
- vs RHH: **cutter and changeup forward, sweeper back** — especially with two strikes, where the cutter whiffs 48.0% against the sweeper's 11.5%.
- One rule: *sweeper to lefties, cutter to righties, and never a two-strike sweeper to a right-hander unless it's leaving the zone.*

**Manager**
- Deploy as a **7th-inning, 3–4 batter setup arm of both hands** — that is exactly how he was used and it transfers.
- **Back-to-back days are fine** (velo −0.9 mph, walk rate 2.6%). He is arguably *worse* with three days' rest.
- **Prioritize into lineup segments containing left-handers**; the exposure is right-handed contact until the sequencing changes.
- **Plan around ~.290–.310 wOBA, not .239.**

---

## Data Specification (summary)

| Item | Value |
|---|---|
| **Grain** | one row per tracked pitch |
| **Entity key** | `pitcher == 548384` (MLBAM id — never a name filter) |
| **Tiers** | Pre-TJ ≤ 2024-04-19 (3,162 pitches / 770 BF) · Post-TJ ≥ 2025-07-19 (1,022 / 269). **Never blended.** Rehab interval asserted as 0 rows |
| **Benchmark** | Phillies LHP 2015–2026, ≥300 tracked pitches → **n = 28**. Raley scored against, excluded from the centroid |
| **New KPIs** | RSA (proxy, calibrated r = 0.831 vs native `arm_angle`), RDI, SLO, RTD — all specified before first use |
| **Coordinate convention** | +x = LHH side = LHP arm side. **Asserted two independent ways** at runtime, not assumed |
| **Quarantined** | 18 untracked rows (automatic balls) excluded from usage/location, retained for PA outcomes |
| **Known gaps** | zero Phillies rows · KBO 2015–19 outside Statcast · native `arm_angle` 2025-26 only in Phillies files · bat-tracking 2023+ · O4 `xwobacon_bip` count semantics |
| **DQ** | 38/38 PASS |
| **Verification** | 661/661 PASS via an independent code path |
| **Freshness** | cache max `game_date` 2026-08-02; built 2026-08-04 (T-2) |
