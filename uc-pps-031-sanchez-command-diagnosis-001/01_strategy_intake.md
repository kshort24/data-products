# 01 · Strategy & Intake — `uc-pps-031`

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy`

## 1 · The use case as submitted (condensed, client's words kept)

> Cristopher Sanchez is struggling with his command in 2026 and I want to diagnose it. … start with a high-level
> assessment of his performance across various years (combine 2021 and 2022 or ignore them). Show that his walk
> rate is up in 2026, he is in the zone less, he is getting less chase, and that he is getting ahead in the count
> less **if the data backs up those claims**. … a couple KPIs for edge rate or zone shadow rate … I want to
> understand if he is *near* the strike zone … Define the "shadow" or "edge" … as one width of the baseball. Check
> prior work and enforce semantic consistency. … Prove this out by showing changes in chase_rate when outside the
> shadow of the strike zone.

A notebook cell was attached (2026 by month + 2023–2025 by season: `nresults`, `chase_rate`, `whiff_rate`,
`barrel_rate`, `hard_hit_rate`, `fpsr`).

## 2 · Prior art retrieved (Rule-1)

| Search | Hit | Consequence |
|---|---|---|
| `ls data-products \| grep -i sanch` | `uc-pps-019-sanchez-first-half-allstar-001` (UC #22, dp_uc21) | Entity lock 650911 inherited; QR family context; the kernel-vs-Statcast wOBA disposition carried into caveats |
| `grep "def edge_rate"` | `dp_uc8`, `dp_uc25`, `dp_uc26`, `dp_uc38` | **The client's recollection is correct.** Governed, Register v2 P16 = A, BALL_FT ratified. Inherited verbatim from dp_uc38 |
| `grep -i shadow` | OZ family (`uc-pos-005`), Attack Zone (`uc-pps-022`, from UC#11), `edge_rate` docstring ("shadow band") | Three geometries. SZ must reconcile to all three (`03` §1) |
| `grep ahead / count_leverage` | PD-7 (`uc-pps-017`, `dp_uc21`); Register P8 "promote to `count_leverage(level, df)`" | "Ahead in the count" is **not new**. CL-1 = PD-7 promoted |
| `grep "def peer_delta"` | PB-1 (`uc-pos-014` v1.1.0) | Peer-netting pattern reused pitcher-side as PN-1 |
| `grep shadow_zone / shadow_miss / beyond_shadow / common_rail` | none | SZ names and ZC-1 are free |
| `grep "ABS\|53.5\|sz_top.*2026"` | none | **O-18 is undocumented anywhere in either plane** |
| Notebook `Baseball Functions.ipynb` | no `edge_rate` cell | Escalation E-2 |
| Exploratory notebooks | `June 2025` (`edge_rate(level, df, diff)`), `August 2025` (hard-coded 0.59–1.07 band), `April 2026` (`ball_width = 0.2417`) | Exploratory variants, **not** governed. Not used, but listed so nobody resurrects them |

## 3 · Gap report (use-case-validator)

| # | Gap | Severity | Resolution |
|---|---|---|---|
| G1 | "Struggling in 2026" and "demonstrably worse": which window? | Non-blocking | Test at season *and* half (ASG cut 07-13, a named cause). Both reported |
| G2 | "In the zone less": Statcast `zone` or geometry? | Non-blocking | Kernel `in_zone_rate` (`zone <= 9`) is the governed P2 number; geometric twin used only for re-scoring |
| G3 | "Shadow" collides with three existing terms | Non-blocking | Compound term Shadow Zone / Shadow Miss, crosswalk published |
| G4 | "One width of the baseball": which constant? | Resolved by ruling | `BALL_FT = 2.94/12` (Register v2 §4.1). The notebook's 0.2417 and 0.24 are retired variants |
| G5 | 2025 vs 2026 zone comparability | **Blocking until controlled** | O-18 found; ZC-1 + PN-1 built before any attribution |

## 4 · Premises stress-tested

| Premise | Bid-time read | Final |
|---|---|---|
| P1 walks up | season flat | Second half only (directional) |
| P2 zone less | raw yes, rulebook-exposed | Yes; half his own on common rails |
| P3 less chase | season **up** | Contradicted for the season; supported for 2H |
| P4 ahead less | season flat | Second half only (significant) |
| "Performance demonstrably worse" | wOBA up, xwOBA flat | Results worse (.263 → .298), expected barely (.279 → .286); 2H expected worse (.279 → .299) |

## 5 · Source fitness (source-system-profiler)

| Check | Result |
|---|---|
| F1 Coverage | 2021–2026 regular season, 281,623 pitches, all pitchers in Phillies games |
| F2 Subject | 10,986 R pitches; 1 untracked location (2025); 0 IBB; arsenal 2026 = SI/CH/SL only |
| F3 Freshness | Max `game_date` 2026-09-15 (Sánchez's 31st start) |
| F4 Zone rails | **2026 rails are a per-batter constant** (100% of 76 batters with 100+ pitches have SD < 0.01 ft; 2025 median within-batter SD 0.071 ft). Same 32 batters: median top −0.234 ft, 84% lower; bottom +0.008 |
| F5 `arm_angle` | 77.7% complete for the subject in 2026: not used (WARN) |
| F6 `player_name` | Role-dependent: it is the **batter** on batting-role rows. Pitcher names resolved from pitching-role rows only (a naive `drop_duplicates('pitcher')` mislabels opponent arms as Phillies hitters; caught in EDA) |

## 6 · External definition (domain-steward-proxy)

MLB's 2026 ABS challenge system uses a zone 17 in wide with the top at **53.5%** and the bottom at **27%** of the
batter's height (MLB.com, "ABS Challenge System: What it means for 2026 MLB season"). The data plane's 2026 rails are
consistent with a fixed height-based zone. This source **explains** O-18. It is not used in any computation; the
rails in the parquet are the authority.
