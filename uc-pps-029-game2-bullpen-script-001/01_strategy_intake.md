# 01 · Strategy & Intake — `uc-pps-029-game2-bullpen-script-001`

**UC #43 · contract `uc-pps-029` · build `dp_uc43` · v1.0.0 · 2026-09-13**
**Agents:** `use-case-validator`, `source-system-profiler`, `domain-steward-proxy`, `business-glossary-agent`

## The ask

A game-script note in the client's own voice, handed over as the use case. It carries four things:

1. **A correction to its own premise.** It was written about a Luzardo start; Luzardo was scratched and Mayza
   opens instead. The note says so up front. The intake treats the *revised* premise (Mayza opens) as the
   operative one and the Luzardo material as withdrawn.
2. **An availability claim.** "Last night cost four arms at an inning apiece — McFarlane, Bowlan, Shugart,
   and Raley. Duran should be ok. Mayza can give you two, hopefully."
3. **A nine-inning script**, one slot per inning, seven distinct arms, with the client's own caveat that it
   "doesn't cover extras" and "doesn't cover Mayza or Holman coming up short," and a bet that Duran is the
   arm who'd go multiple.
4. **A notebook cell** profiling Grant Holman's Lehigh Valley mix, shape and location split by batter
   handedness, ahead of a likely major-league debut.

Requested outputs: a fully governed package with receipts in the 00–07 format, a PDF report, an interactive
dashboard "if it makes sense," a token/time estimate framed as a competitive RFP bid treated as won, and
latitude for the organization to add what it judges necessary.

## Gap report (`use-case-validator`)

| # | Gap | Class | Disposition |
|---|---|---|---|
| **G-1** | **Target game date is ambiguous.** The note says "last night"; the last game in the log is 2026-09-11 and the session date is 2026-09-13. Both a D+1 (09-12) and a D+2 (09-13) target are readable. | **Blocking-if-silent** | Not blocking to delivery, blocking to *defaulting*. Both framings computed (`availability_D1` / `_D2`); D+1 adopted as the operating premise because the log is complete to the night before it and because the four arms the client names reconcile exactly to the 09-11 game. D+2 is shipped as a sensitivity and marked **not certifiable** — if a 09-12 game was played it is not in the cache. Escalated in `00` §7. |
| **G-2** | **Opposing starter has no name in the data.** Statcast carries no `player_name` for opponent pitchers (standing defect **O-10**). The client names "Mahle." | Non-blocking | Resolved to MLBAM **641816** by elimination on four constraints (see below). Labelled **inferred, not confirmed**, carried as a DQ WARN, and disclosed in the report's caveats. MLB StatsAPI is not reachable from this session's egress, so no independent confirmation was possible. |
| **G-3** | **No confirmed lineup card for the target game.** | Non-blocking | The 2026-09-11 order is used as the best available proxy and is labelled as such. Confirmed lineups are a manual carry-in the client can supply. |
| **G-4** | **Holman's promotion is asserted by the client, not visible in the log.** | Non-blocking | Accepted as a manual carry-in. The log corroborates it negatively: he has no MLB pitches and no Lehigh Valley appearance after 2026-08-30 while the AAA log runs to 09-06. |
| **G-5** | **Cause of two gaps in Holman's AAA log (44 days, then 13 days) is not in the data.** | Non-blocking | Reported as gaps; **no cause asserted**. Injury, option moves and taxi-squad time are all consistent with the pattern and the data cannot distinguish them. |
| **G-6** | **Kerkering's seven-day absence (last outing 09-04, 59 appearances before it) has no explanation in the log.** | Non-blocking | Reported as a fact with the availability implication (he is the freshest arm) and **no cause asserted**. Flagged to the client — he may know something the log does not. |
| **G-7** | **"An inning apiece" is not a measurable unit.** | Non-blocking | Replaced with measurable inputs (pitches, batters faced, rolling load, rest) — this is what BS-1 exists to do, and the substitution is itself a finding. |

## Premises stress-tested (falsify-before-describe — standing policy)

| Premise as stated | Verdict | Evidence |
|---|---|---|
| "Last night cost **four** arms" | **Not supported — it was five.** | Alvarado pitched the 7th of the 2026-09-11 game (9 pitches, 2 BF) and is absent from the client's list. `anchor_game_ledger` |
| "…at an inning apiece" | **Overstated for three of five.** | Bowlan 22p and McFarlane 15p are at or above their season averages. Alvarado, Shugart and Raley threw **9 pitches each**; Shugart's nine covered two innings. |
| "Duran should be ok" | **Partly supported, with a correction.** | He did not pitch 09-11, but he went back-to-back 09-09/09-10 (14p, 17p). GREEN at D+2, AMBER at D+1. |
| "Mayza can give you two, hopefully" | **Supported.** | Four opener starts in 2026; **three reached the second inning**; mean 25.8 pitches / 6.5 BF, high 33 pitches. And a two-inning open exposes him to no hitter twice — every one of his 987 pitches this year is `n_thruorder_pitcher == 1`. |
| "Duran's the name I'd bet on to go multiple" | **Rejected.** | 1 of 56 relief outings spanned two innings (1.8%), second-lowest on the staff. Shugart (.375), Mayza (.320) and Holman (AAA, .400) are the length. |
| Implicit: nine slots × one arm each covers nine innings | **Rejected at the average; ceiling-dependent at the maximum.** | 29.7 expected BF vs a 37-BF regulation median; 38.1 if every arm reaches his season high. |
| Implicit: the script's spare capacity is in extras | **Rejected.** | The shortfall is in regulation. |

## Source-system fitness (`source-system-profiler`, F1–F4 gate)

| Gate | MLB frame (`phils_2026`) | AAA frame (`lhvp26`) |
|---|---|---|
| **F1 Exists** | PASS — 22,021 regular-season PHI pitching rows | PASS — 20,319 regular-season rows, 348 for the subject |
| **F2 Populated** | PASS — pitch_type/velo/location null rates < 0.5%; 48 null `zone` of 22,021 | PASS — 0 nulls on velo, break, location, zone for the subject; 6 of 73 BIP lack exit velocity |
| **F3 Fit for the question** | PASS | **CONDITIONAL** — no wOBA weight columns exist, so wOBA/xwOBA are **not computable without importing MLB constants**, which would be a comparability violation (LV-1, `uc-pos-015`). Tier restricted to usage / velo / shape / location / whiff / chase / counting outcomes. |
| **F4 Timely** | PASS at D+1 (T-1). **FAIL at D+2** (T-2, one game potentially missing). | WARN — AAA log T-6; subject's last logged pitch T-13. |

## Opponent-starter resolution (`domain-steward-proxy`)

Four constraints, applied to the 2026 Phillies batting log:

1. Faced the Phillies as a **starter** — 641816 threw the first pitch to the Phillies in all three of his
   appearances, 82–94 pitches, 22–24 batters, reaching the 6th inning every time.
2. **Right-handed** — `p_throws == 'R'` on all 270 pitches.
3. **Four-seam / splitter / cutter arsenal** — FF 92.9 mph (49%), FS 86.2 (30%), FC 87.8 (16%), with trace
   sinker and slider. That shape is unusual enough to be near-identifying.
4. **Changed teams mid-season** — pitched against the Phillies for San Francisco on 04-08 and 04-28, then for
   Atlanta on 09-06.

No other pitcher in the log satisfies all four. The inference is strong but circumstantial and is recorded as
a **WARN**, not a PASS, in the DQ scorecard. If 641816 is not Mahle, the report's §8 is about the wrong
pitcher and nothing else in the package changes.

## Glossary position (`business-glossary-agent`)

No CDE was invented. Every business term used by this build either (a) already exists in the governed kernel
(`pitches`, `batters_faced`, `days_of_rest`, `innings_spanned`, `whiff_rate`, `chase_rate`, `putaway_rate`,
`First Pitch Strike Rate`, `usage`) or (b) is registered as a **new provisional object** in `03_governance.md`
with a full calculation spec. Where a definition was missing — "an arm is down" — the build did **not** infer
one silently; it registered `bullpen_availability_tier` (BS-1) as a new, provisional, unratified object and
said so in the report's caveats.

## Declared DPO discretion

Decisions this layer took rather than defaulting on, all surfaced in `00` §7 for the human DPO:

1. **D+1 adopted as the operating premise**, D+2 shipped as a priced sensitivity. Reason: the log supports
   D+1 and the client's own four names reconcile to it exactly.
2. **The AAA tier is quoted for mix, shape and counting outcomes only.** No wOBA, no xwOBA, no hard-hit rate.
3. **A second capacity mode (BS-2 ceiling) was added** after the average-outing mode produced a finding that
   was true but framed too loudly — the script is ceiling-dependent, not simply short. Sizing the finding
   before amplifying it is the `uc-pos-016` DC-1 discipline applied here.
4. **The interactive dashboard was judged to earn its place** and built. Reason: the client's question is
   "does this script hold," which is a *what-if*, and a static table cannot answer a what-if.
5. **A recommended revision was written.** The ask did not request one, but a report that falsifies a plan
   without offering the reallocation the same data implies is half a deliverable.
