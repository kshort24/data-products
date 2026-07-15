# First-Half Assessment — Jhoan Duran (RHP), Phillies Closer
### 2026 All-Star break retrospective · prepared 2026-07-13 · "Has he done anything differently?"

**Prepared for:** manager / pitching department / battery / front office — All-Star break review
**Throws:** R · **Arsenal 2026:** 5 pitches (Split-Finger, 4-Seam, Knuckle Curve, Sweeper, Changeup)
**Governance:** Use Case #20 (`uc-pps-018`, build prefix `dp_uc19`) · KPIs inherited **verbatim** from the dp_uc11 kernel (lineage UC3 → UC8 → UC11 → UC17/UC18) · **no new KPIs** · saves and All-Star selection are manual carry-ins · retrospective shape per uc-pps-017 (Luzardo) / dp_uc18 (Marsh)

> ⚠️ **Read this first — data window & sample sizes.**
> • Sources: `duran.parquet` (Twins log, 2022-04-08 → 2025-07-28, pre-trade), `phils_2025` (post-trade stint, 2025-08-01 → season end), `phils_2026` (first half, cache fresh **2026-07-12**; last appearance 2026-07-11). Entity lock `pitcher == 661395`; regular season only — the 2025 postseason (96 pitches) is **excluded** throughout.
> • Zero game_pk overlap at the Twins→Phillies seam (verified: Twins cache ends 07-28, Phillies stint starts 08-01).
> • Closer samples are small by construction: **PHI 2025 stint = 81 PA**; 2026 monthly splits run **12–44 PA**; the new changeup is **35 pitches** (29 to LHB); the sweeper has been thrown to LHB **3 times**. PA/pitch counts are printed on every such line.
> • **Manual carry-ins (DPO, 2026-07-13):** 24 saves (not derived from pitch-level data by DPO decision) and the 2026 NL All-Star selection.

---

## Bottom line

1. **Yes — he is meaningfully different, and it's by design, not just results luck.** 2026 Duran is a **splitter-first, five-pitch closer**: Split-Finger 45.2% usage, 4-Seam down to a career-low **27.0%** (it was 49.3% as a 2022 rookie). The identity pitch changed.
2. **Two new looks arrived to start this year.** The sweeper became real (**10.3%** usage, **66.7% whiff**, 36.0% putaway — 53 pitches) and he added a **changeup that did not exist in his profile before 2026** (35 pitches, 83% of them to LHB, 11.2 mph off the fastball). Both counts are small; both roles are already defined.
3. **The results are career-best and the swing-and-miss backs them.** .227 wOBA / .229 xwOBA against, **39.7 K%** (career high — next best 33.7%), 4.8 BB%, one homer in 126 PA. Whiff rate **39.6%** vs 30.7% in the 2025 Phillies stint and a 30.9–35.4% Twins range.
4. **The mechanism is out-of-zone dominance plus two-strike conversion.** In-zone rate fell to a career-low **45.2%** while chase held at **35.1%** — hitters are expanding for him. Putaway rate is **32.5%** vs 24.3–26.4% across the Twins years; the splitter's putaway jumped to **40.6%** (32 two-strike pitches) vs 24.9% career.
5. **Honest read vs late 2025: the K spike is the new part, not contact quality.** xwOBA is flat vs the 81-PA Phillies stint (.226 → .229), and when hitters do connect it's loud — hard-hit **46.4%** on just 69 BIP, a career worst. The improvement case rests on strikeout frequency and walk avoidance, and those are loud and real. **24 saves** (carry-in) sit on top of that process.

---

## The results by era

| Era | G | Pitches | PA | wOBA | xwOBA | K% | BB% | HR | Whiff | Putaway | Hard-hit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MIN 2022 | 57 | 1,023 | 264 | .248 | .232 | 33.7% | 4.9% | 6 | 34.7% | 26.4% | 35.0% |
| MIN 2023 | 59 | 1,017 | 249 | .267 | .249 | 33.7% | 7.6% | 6 | 35.4% | 25.7% | 38.0% |
| MIN 2024 | 58 | 881 | 226 | .290 | .259 | 29.2% | 5.8% | 4 | 32.9% | 25.2% | 36.2% |
| MIN 2025 | 49 | 765 | 202 | .246 | .266 | 26.2% | 6.9% | 1 | 30.9% | 24.3% | 40.2% |
| PHI 2025 | 23 | 308 | 81 | .251 | .226 | 33.3% | 1.2% | 2 | 30.7% | 30.3% | 45.3% |
| **PHI 2026 1H** | **34** | **515** | **126** | **.227** | **.229** | **39.7%** | **4.8%** | **1** | **39.6%** | **32.5%** | **46.4%** |

![Results vs process by era](../../out/dp_uc19_era_trend.png)

Two stories in one table. Against his Twins career the process gain is unambiguous — whiff, putaway, and xwOBA all moved the right way after the mid-2025 trade. Against the **late-2025 Phillies stint (81 PA)** the expected-contact line is flat; what's new in 2026 is the strikeout engine: K% +6.4 points, whiff +8.9 points, and he did it while cutting the stint's untenable 1.2 BB% loose for a still-excellent 4.8%.

## The arsenal redesign — the actual answer to "what's different"

![Arsenal usage by era](../../out/dp_uc19_arsenal_evolution.png)

| Pitch | MIN 2022 | MIN 2024 | MIN 2025 | PHI 2025 | **PHI 2026 1H** | 2026 velo | 2026 whiff |
|---|---|---|---|---|---|---|---|
| Split-Finger | 16.0% | 31.4% | 37.6% | 45.5% | **45.2%** | 97.5 | 32.4% |
| 4-Seam Fastball | 49.3% | 40.7% | 34.1% | 37.7% | **27.0%** | 100.2 | 45.9% |
| Knuckle Curve | 31.4% | 27.7% | 20.5% | 15.9% | **10.7%** | 88.3 | 52.2% |
| Sweeper | — | 0.1% | 7.7% | 1.0% | **10.3%** | 88.9 | 66.7% |
| Changeup | — | — | — | — | **6.8%** | 89.0 | 14.3% |

The trend started in Minnesota (splitter share climbed every year) and the Phillies finished it: the splitter has been the primary pitch since the trade, and in 2026 the four-seam — still averaging **100.2 mph** — became a complementary weapon at 27% usage with a **45.9% whiff rate**. Throwing 100 less often made 100 harder to hit: that whiff rate is his best four-seam figure of any era in this product (career range 25.8–42.3%).

Velocity is stable, so this is not a stuff decline being managed — it's a usage choice. (Release extension reads ~0.2 ft lower in 2026 across all pitches, 5.9–6.1 vs a 6.1–6.6 career range; uniform shifts like that often reflect tracking calibration, so we note it and don't over-read it.)

## The new looks: sweeper and changeup

**Sweeper** — seeded late in Minnesota (59 pitches, 2025), nearly shelved during the 2025 Phillies stint (3 pitches), now a genuine weapon: 53 pitches, **66.7% whiff** (on 27 swings — printed because it's small), **36.0% putaway** on 25 two-strike pitches, .096 xwOBA against. It is almost exclusively a right-on-right pitch (see platoon section).

**Changeup — brand new for 2026.** No era before this one contains a single changeup. 35 pitches at 89.0 mph, an **11.2 mph** separation off the four-seam, 29 of 35 thrown to LHB. It is *not* a whiff pitch (15.4% whiff vs LHB on 13 swings) — it's a weak-contact look: .030 xwOBA against LHB on the tiny sample we have. **Directional only at 35 pitches**, but the design intent is legible: give left-handers a fourth speed band (100 / 97 / 89-CH / 88-KC) they must respect.

**Two-strike conversion, 2026 vs career** (receipt: `dp_uc19_duran_putaway_by_pitch.csv`):

| Pitch | Career pre-2026 putaway | 2026 putaway (2-strike pitches) |
|---|---|---|
| Split-Finger | 24.9% | **40.6%** (32) |
| 4-Seam Fastball | 22.4% | **32.7%** (55) |
| Sweeper | 20.0% (15 pitches) | **36.0%** (25) |
| Knuckle Curve | 30.0% | 21.7% (23) |

## Platoon plans — he's throwing two different games

![2026 arsenal map by stand](../../out/dp_uc19_2026_arsenal_map.png)

| vs | Plan | Usage | Whiff |
|---|---|---|---|
| **RHB** | Splitter-sweeper tunnel; the four-seam is a surprise | FS 54.8% · SW 25.6% · FF 16.1% | FS 50.0% · SW 66.7% · FF 56.2% |
| **LHB** | Four-pitch spread; changeup is the new wrinkle | FS 39.2% · FF 33.9% · KC 17.1% · CH 9.2% | KC 54.5% · FF 43.1% · CH 15.4% |

Right-handers see a fastball roughly one pitch in six — from a pitcher who threw it half the time as a rookie. The sweeper has effectively replaced it as the second pitch right-on-right (it's been thrown to a lefty **3 times** all year). Against lefties the splitter still leads but the knuckle curve (54.5% whiff) and the new changeup carry the secondary load. One flag: the splitter vs LHB runs a **.369 xwOBA** with an 18.4% whiff — lefties are handling it better than righties (.232) — which is presumably exactly why the changeup exists.

## Month by month — "lights out for most of the season" checks out

| Month | G | PA | wOBA | K% | BB% | Whiff |
|---|---|---|---|---|---|---|
| March | 3 | 12 | .297 | 41.7% | 0.0% | 48.1% |
| April | 4 | 12 | .105 | 25.0% | 0.0% | 24.0% |
| May | 11 | 44 | .256 | 40.9% | 11.4% | 40.7% |
| June | 12 | 42 | .216 | 42.9% | 2.4% | 42.9% |
| July | 4 | 16 | .213 | 37.5% | 0.0% | 32.4% |

Every one of these cells is a small sample (12–44 PA — that's a closer's life) and they should be read as texture, not signal. The texture is consistent: since the May walk blip (11.4 BB% in 44 PA), he's run a .216/.213 wOBA against with a 40%+ whiff rate through the heart of the season. The single home run allowed all year came in May.

## The risk paragraph — what we'd say to a skeptic

The contact-quality counterargument is real and we won't hide it: **hard-hit rate is a career-worst 46.4%**, xBA against is .341, and first-pitch strike rate fell to a career-low **54.8%**. A skeptic reads that as a pitcher living dangerously — rare contact, but loud, with more 1-0 counts. The rebuttal is in the expected numbers: xwOBA against is **.229** because the strikeouts are so frequent that 69 balls in play can't move the needle, and the walk rate (4.8%) never let the 1-0 counts compound. The results gap vs process gap framing: **wOBA .227 / xwOBA .229 — there is no gap.** This first half is not luck riding on sequencing; it's a strikeout profile carrying a knowable, monitorable contact risk.

## Second-half watch list

1. **Manager:** nothing in the pitch log argues for changing the role. 34 appearances at the break is a normal closer load (23 post-trade appearances in 2025's final two months was heavier per-week).
2. **Pitching department:** the splitter-vs-LHB xwOBA (.369) is the one number on the board that's genuinely soft. If it persists, the changeup share to lefties (9.2%) is the natural lever — its early weak-contact returns support it.
3. **Battery:** protect the two-strike splitter/sweeper conversion (40.6% / 36.0% putaway) — that's the engine. FPSR (54.8%) is the early-warning gauge; if it drops further **and** BB% rises, the out-of-zone approach is losing its credit.
4. **Duran:** the four-seam at 27% usage / 45.9% whiff is the proof that less is more. The temptation after a loud blown save will be to reach for 100 more often; the first half says don't.

## Candid data-window & freshness caveats

- **Saves (24) and the All-Star selection are manual carry-ins** logged in the freshness manifest — pitch-level Statcast does not carry an official save flag, and the DPO elected not to derive one. No save-situation split appears anywhere in this product for that reason.
- **No official IP/ERA here** — this product speaks in PA-denominated rates (wOBA, xwOBA, K%, BB%) and pitch-denominated process metrics, all computable from the locked kernel. Nothing was reconstructed.
- **PHI 2025 is 81 PA** — every comparison against the stint is directional. The Twins-era baselines (202–264 PA per season) are the sturdier reference.
- **Changeup = 35 pitches, sweeper = 53.** Roles are described; performance rates on these pitches are early reads, printed with their denominators.
- The `game_type == 'R'` filter excludes his 2025 Phillies postseason (66 pitches), the 2023 Twins postseason in the career cache (57 pitches, WC + ALDS), and 2026 spring training (42 pitches); October work is out of scope here.
- Cache freshness 2026-07-12 (T-1); last appearance 2026-07-11. If he pitches in the All-Star Game it will not be in this product.
- Receipts: `out/dp_uc19_*.csv` (8 files) · figures `out/dp_uc19_*.png` (3) · DQ scorecard 5/5 PASS (`events`/wOBA-value fields ~25.5% non-null is the expected PA-ending-pitch population, not a defect) · build `data-products/uc-pps-018-duran-first-half-allstar-001/dp_uc19_duran_first_half.py`.
