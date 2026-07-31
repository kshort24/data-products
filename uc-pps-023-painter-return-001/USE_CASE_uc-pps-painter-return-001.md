```yml
# Identity
name: Andrew Painter Return Read 20260731 BAL (Away)
id: uc-pps-023-Andrew Painter BAL 20260731
description: >
  Andrew Painter returns to the majors tonight in Baltimore after being optioned
  to Triple-A Lehigh Valley following a difficult start to his 2026 rookie season.
  This use case asks whether he adjusted during the minor-league stint and what
  four decision-makers should do about it. Deep-dive angles: stuff (velocity,
  spin, movement) compared across levels; location, chase and whiff; and release
  point, extension and arm angle. The opponent dimension is formally descoped —
  no Orioles data exists in this repo — making this the first self-scout variant
  of the uc-pps pattern.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — Ready for DPO Sign-off
priority: High
expiry: 2026-07-31 first pitch (pre-game projection)

# People
personas: Pitcher (Andrew Painter), Catcher (J.T. Realmuto), Pitching Coach / Department, Manager
owner: Kellen Short
requested_by: Kellen Short (Data Product Owner)

# Relationships
parent_use_case: >
  UC#3 (Luzardo deep dive) -> UC#8 (Nola vs WAS, canonical flat-file pattern)
  -> UC#11 (Rangel vs PIT, multi-level evidence tier) -> UC#29 (this)
supersedes: _scratch_painter_lhv_scouting_20260709.md (dev scratch, never certified)
sub_use_cases: []

# Metadata
ledger_uc: 29
created: 2026-07-31
last_updated: 2026-07-31
build_artifact: dp_uc28_painter_vs_orioles.py
report: dp_uc28_painter_vs_orioles_report.md / .pdf
dashboard: dp_uc28_painter_vs_orioles_dashboard.html
verification: dp_uc28_verification.py (76/76 passed)
governance_trail: data-products/uc-pps-painter-return-001/ (00-07)

# Data References
kpis:
  - whiff_rate            # LOCKED - inherited verbatim from dp_uc11
  - chase_rate            # LOCKED
  - putaway_rate          # LOCKED
  - first_pitch_strike_rate  # LOCKED
  - hard_hit_rate         # LOCKED
  - nresults (wOBA, K%, BB%)  # LOCKED
  - csw_rate              # mechanical helper
  - strike_rate           # mechanical helper
  - release_consistency_index   # NEW
  - fastball_upper_third_rate   # NEW
  - cross_level_stuff_delta     # NEW
  - arm_spread_deg              # NEW - PROVISIONAL, correlational
data_domains:
  - Pitch Profile
  - Pitch Outcomes
  - Strike Zone
  - At-Bat Outcomes
  - Batted Ball Profile (directional only)
  - Release Mechanics
entity_lock: pitcher == 691725 (MLBAM)
tiers:
  MLB: phils_2026.parquet - 1141 pitches / 299 PA / 14 starts
  AAA: lhvp26.parquet - 396 pitches / 101 PA / 5 starts
  benchmark: 31 RHP with >=150 four-seams in 2026 Phillies games
classification: Internal - Restricted (external publish blocked)
```

# Andrew Painter — Return Read vs Baltimore, 2026-07-31

> **Document status:** Build complete. Reader report `dp_uc28_painter_vs_orioles_report.pdf` (11 pp) and interactive dashboard `dp_uc28_painter_vs_orioles_dashboard.html` in the MLB repo. Governance trail in `00`–`07` alongside this file. 23 CSV receipts and 5 figures in `out/dp_uc28_*`. Verification log `out/dp_uc28_verification_log.txt`.

## Business Context

### Problem Statement

Painter came up as one of the best pitching prospects in baseball and struggled — fourteen starts, a strikeout rate that fell off a cliff over the back half, and an option to Lehigh Valley in mid-June. He starts tonight in Baltimore.

The question everyone is going to ask in the advance meeting is "is he fixed?", and that question is useless because it isn't answerable. The answerable version is narrower and more useful: **did anything measurably change during those five Triple-A starts, and if so, what does each person in the room do differently tonight?**

Four people have four different decisions. Painter has to decide what to trust. Realmuto has to call the game. The pitching department has to pick one cue that's worth giving him between innings. The manager has to decide when to go get him. A single undifferentiated "here's the pitcher" writeup serves none of them well.

The trap is that the obvious story — *velocity is up, he must be better* — is the wrong one, and a report that leads with the radar gun would actively mislead the room.

### Business Questions — Answered

**Q1. Did his stuff change at Triple-A?**
**Essentially no.** Cross-Level Stuff Delta shows the four-seam gained 0.64 mph and lost 0.25" of ride — the velocity gain is real but the shape is unchanged. Sinker, slider, sweeper and curveball all sit within or near the measurement-noise band. **The one exception is the splitter**, which gained 2.75 mph and 2.43" of arm-side run and lost 2.11 mph of separation from the fastball. That is a materially different pitch, and not obviously a better one.

**Q2. Then what did change?**
**How he attacks.** Four-seam usage went from 33.1% to 49.2%; the slider dropped 13.1 points and the splitter 7.6, with the sweeper picking up 8.3. This is an attack-plan rebuild, not a stuff fix — and it directly addresses the failure mode, because over his final seven big-league starts he threw his fastball only 27.7% of the time and his strikeout rate fell to .150.

**Q3. What actually went wrong in the majors?**
**Hitters stopped chasing, and the fastball never missed bats.** Chase fell from .357 over his first eight starts to .265 over his last seven, while velocity stayed flat. He responded by throwing more strikes in the zone (.447 → .522) and fewer fastballs; the strikeouts left and the walks rose anyway. Underneath it: his four-seam is 55th-percentile velocity, 52nd-percentile ride, 52nd-percentile extension, 48th-percentile elevation — and **26th-percentile whiff rate**, 23rd percentile up in the zone. Average pitch, average location, half the bat-missing.

**Q4. Why doesn't the fastball miss bats?**
The best available answer, and it is a **hypothesis rather than a finding**: his arm slot varies by pitch type more than almost anyone measurable. Mean arm angle spans **13.8°** across his six pitches against a pool median of **4.25°** — the 96th percentile. His four-seam and sweeper leave his hand 6.3 inches apart. At Triple-A the spread widened to 15.0°, and his splitter dropped out of the fastball cluster entirely. This reconciles average shape with poor results better than any alternative in the data, and it is testable tonight.

**Q5. Is the delivery stable?**
**No, and this is the live risk.** Across 13 MLB starts his four-seam release sat in a 2.1-inch band; in his last MLB start and his first AAA start it jumped ~5 inches toward the middle of the rubber, then returned. A same-park control (6/28 and 7/10, both at Lehigh Valley, 5.6 inches apart) proves this is mechanical rather than camera calibration. Meanwhile extension has fallen **every single Triple-A start** — 6.451 to 6.293 ft — while velocity climbed. He is throwing harder by reaching.

**Q6. What's the biggest tonight-specific risk?**
**He shelved his best pitch against left-handed hitters.** The splitter produced a .395 whiff rate on 76 major-league swings against lefties at 21.4% usage; at Triple-A that halved to 10.6%, replaced by the sweeper (4.4% → 17.6%) — a pitch that breaks toward a lefty's barrel. His whiff rate vs LHH fell to **.150 on 65 PA**.

**Q7. How should Baltimore be attacked?**
**Not answered, by design.** There is no Orioles data in this repo and Painter has never faced them. Fabricating a lineup plan was rejected at the intake gate. This is a self-scout.

### Actions

**Battery (Painter + Realmuto)**
- Lead with the fastball; hold four-seam usage near the Triple-A 49%, not the 28% that preceded the option.
- Splitter — not the sweeper — is the two-strike pitch to lefties. Bury it down and arm-side.
- Never sequence four-seam into sweeper back-to-back to the same hitter early; break it with the sinker or slider.
- Realmuto reports the first-inning four-seam release to the dugout. Near −20 inches is the warning signature.

**Pitching department**
- One cue, highest leverage: **arm-slot uniformity**. Everything else says the fastball should work.
- Instrument the tipping hypothesis tonight — first-pitch swing rates and whiff-by-pitch after same-slot vs different-slot sequences.
- Decide on the splitter: pull the velocity back toward 87–88 and restore the slot match, or stop asking it to be a chase pitch.
- Extension is the quiet regression — 6.64 ft in April, 6.29 on 7/26.

**Manager**
- Plan 85–90 pitches, five or six innings.
- Leash markers in order: release drifting toward −20 in; chase under 25% through two; hard contact climbing.
- Someone warm before the third time through — hard-hit rate climbs on every pass at both levels.

## Data Specification (summary)

| Aspect | Value |
|---|---|
| **Grain** | one row per pitch |
| **Entity key** | `pitcher == 691725` (MLBAM), asserted at runtime |
| **Structure** | stacked union of two tiers with a `level` discriminator — **not a join** |
| **Governing rule** | no rate KPI may have a denominator spanning more than one `level`; enforced structurally |
| **Tiers** | MLB 1,141 pitches / 299 PA / 14 starts · AAA 396 / 101 / 5 |
| **Benchmark** | 31 RHP with ≥150 four-seams in 2026 Phillies games (23 for arm spread) |
| **New KPIs** | Release Consistency Index · Fastball Upper-Third Rate · Cross-Level Stuff Delta · `arm_spread_deg` (**provisional**) |
| **Barred fields** | `estimated_woba_using_speedangle`, `estimated_ba_using_speedangle` — deprecated at pitch level by UC-PPS-021 |
| **Known gaps** | 🔴 zero Orioles data (descoped, disclosed) · 🟡 AAA below the 100-BF convention · 🟡 benchmark pool small and Phillies-weighted · 🟡 cross-level spin offset unexplained · 🟡 Camden Yards notes are carry-in with no numbers |
| **Certification** | READY — 21 PASS / 3 WARN / 1 FAIL (reclassified non-blocking by descope); 76/76 verification checks |
| **Publish surface** | **Internal only** — external publish blocked by `privacy-watchdog` |
