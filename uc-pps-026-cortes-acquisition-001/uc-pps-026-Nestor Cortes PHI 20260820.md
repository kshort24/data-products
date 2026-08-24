```yml
# Identity
name: Nestor Cortes Acquisition Read 20260820 PHI
id: uc-pps-026-Nestor Cortes PHI 20260820
description: >
  Free-agent-signing onboarding read for LHP Nestor Cortes, signed 2026-08-19 while
  rehabbing from mid-Oct 2025 arm surgery (zero competitive pitches since). Establishes
  the pre-return baseline: career deployment history (the new UD family, from the DPO's
  own notebook logic), platoon splits and approach evolution, stuff trajectory with the
  pre-surgery velocity fade, and the indicators that separate his good and bad stretches —
  turned into actions for manager, battery, and pitching department. First UC delivered
  through a competitive-bid flow with bid-vs-actual telemetry.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Delivered — Ready for DPO Sign-off
priority: High

# People
personas: Manager (Don Mattingly), Pitching Coach / Department, Catchers, Pitcher, Pitching Analyst
owner: Kellen Short

# Relationships
parent_use_case: >
  UC3 (Luzardo) -> UC8 (Nola vs WAS) -> UC11 (Rangel) -> UC29 (Painter, return-from-injury) ->
  UC30 (Kilian, acquisition template) -> UC31 (Raley) -> THIS (acquisition x surgery-return hybrid)
sub_use_cases: []
sibling_use_cases: >
  Future returning-from-surgery reads inherit the RB-1 tripwire + velocity-band pattern

# Metadata
created: 2026-08-19 (bid) / 2026-08-20 (award + delivery)
last_updated: 2026-08-20
ledger_uc: 37
build_artifact: dp_uc36_cortes_acquisition_read.py
governance_trail: data-products/uc-pps-026-cortes-acquisition-001/00_ .. 07_
verification: dp_uc36_verification.py — 184/184 PASS (includes the DPO's original notebook method as the independent path)

# Data References
data_sources:
  - data/opponents/cortes.parquet   # entity lock pitcher == 641482
entity_lock: pitcher == 641482
kpis:
  locked_inherited: [get_stats/nresults, whiff_rate, chase_rate, putaway_rate,
                     fpsr, hard_hit_rate, csw_rate]
  inherited_hardened: [xwobacon, zone_rate_strict]
  new: [UD-1 Start Share, UD-2 Bulk Share, UD-3 Innings per Game, UD-4 PAs per Game,
        UD-5 Relief Share, UD-6 Season Role Label]   # DPO-supplied definitions, provisional
data_domains: [At-Bat Outcomes, Batted Ball Profile, Pitch Profile, Pitch Outcomes,
               Strike Zone, Game State]
publish_scope: Internal only
```

# Acquisition Read — Nestor Cortes (LHP)

> **Document status:** deliverables `dp_uc36_cortes_acquisition_read_report.pdf` (7pp) +
> `dp_uc36_cortes_dashboard.html` (self-contained, plotly vendored) · governance trail `00_`–`07_`
> · receipts `out/dp_uc36_*` (28 CSV + 5 figures) · verification **184/184 PASS** ·
> bid receipt `BID_2026-08-19_uc-pps-026-cortes.md` + `telemetry/` (bid-vs-actual)

## Business Context

### Problem Statement

We signed Nestor Cortes to a prorated one-year deal (Brian Keller DFA'd for the 40-man spot),
and he hasn't thrown a competitive pitch since last September — arm surgery in mid-October.
The staff is worn down and there are three different jobs he could plausibly do: sixth starter,
bulk arm behind an opener, maybe even high-leverage lefty work. Before anyone pencils him into
any of them, I want the honest baseline: how he has actually been deployed across his career,
what he throws to each side and how that's changed, where his stuff was trending before the arm
gave out, and which indicators actually separate good Nestor from bad Nestor. And the answers
should land as actions for Mattingly, for the catchers, and for the pitching department — not a
stat dump. (And yes — the Freeman thing is allowed one receipt.)

### Business Questions — Answered

**1. How has he been deployed — starter, reliever, bulk?**
All three, in sequence: relief-heavy 2018-20 with a genuine bulk season in 2019 (**24.2% bulk
share, 8 bulk outings** by my own definition, now governed as UD-2), transition in 2021 (15
starts of 22 games), then a pure starter 2022-25 (78 of 79 appearances). His 2025 starts
averaged just 75 pitches — he was already being run at bulk length before the surgery.

**2. Platoon splits and approach evolution?**
Career looks neutral (.301 vs LHB / .309 vs RHB) but since 2022 it isn't: **.161 wOBA vs LHB in
2022 (89 PA)** and **.233 across 2023-24 (198 PA)** while the decline ran through RHB (.329,
780 PA). Approach: to LHB it's FF/sweeper/cutter with 68.5% of everything glove-side away —
and the sweeper (.247 xwOBAcon, 35.1% whiff) should be doing more of the work than the
four-seam, which lefties are punishing (.457 xwOBAcon, 7 of his last 10 HR to LHB). To RHB he
adds the changeup away (his best right-handed putaway, 32.7% two-strike whiff).

**3. What does his stuff look like, and what was trending pre-injury?**
Ride is his identity and never wavered (FF IVB ~19.3 in since 2022). Velocity is the story:
climbing through 2024 (92.7 by September), then **90.1 across the injury-broken 2025** with his
final start at 89.5. The two-mph gap is the single number the return hinges on. Mechanical
drift receipt: arm angle 45°→51° and release point ~0.9 ft toward the center line since 2019 —
baseline his post-surgery slot on purpose.

**4. What drives his good and bad periods?**
Era level: the 2022→2023-24 decay was contact management (hard-hit +8.3 pts, xwOBAcon +.039)
and first pitches (FPSR −6.5 pts) — not whiff, not zone, not walks. Outing level: his bad days
show whiff and zone decay at near-normal velocity (whiff .269→.212, zone .517→.486, velo only
−0.6). Watch the swings, not the radar gun.

### Actions

**Manager** — bulk/multi-inning lefty on an 18-BF (two-pass) leash; lefty stretches on merit;
one-run ninths earned later; no rest-day scheduling advantage exists; the sixth-starter slot is
the destination if the velocity comes back, not the entry point.
**Battery** — sweeper-first to LHB away, kill the belt-high four-seam to lefties; cutter-in /
changeup-away to RHB; fix pitch one (FPSR .672→.607 is the cheapest recovery in the profile);
mind the behind-in-count cutter tell (44.8%).
**Pitching department** — velo bands green ≥91.5 / yellow 90.5-91.5 / red <90.5 on rolling
50-pitch windows; IVB floor 18.5; slot photo vs `dp_uc36_mechanics_by_season.csv` in bullpen 1;
in-game health proxy is whiff/zone, not velo.

## Data Specification (summary)

**Grain:** pitch → appearance → season → phase. **Entity:** `pitcher == 641482` (never a name
filter). **Source:** `data/opponents/cortes.parquet`, R-only rates, deduped; 10,087 R pitches,
143 appearances, 2018-03-31 → 2025-09-03. Phases (never blended): 2019 relief/bulk · 2021
transition · 2022 peak · 2023-24 decline · 2025 final (MIL→SD, directional). **2026 = true
gap** (surgery); postseason (153 D / 55 L / 21 W, incl. the 2024 WS Freeman receipt) is context
only. New KPIs: UD-1..6, specced in 02 before use, DPO definitions verbatim, promotion pending.
Known gaps: surgery type unspecified (not guessed) · no `gms_AI` (no ERA/IP) · leverage evidence
2019-21 vintage · no Phillies rows by construction.

**Closure:** RB-1 tripwire armed — first 2026 rows fail the gap assertions loudly; re-run,
grade the three falsifiable calls (velocity band decides results · lefty edge holds · FPSR leads
outing quality), publish v1.1 return read. RB-2 full re-read at 100 PHI batters faced.
