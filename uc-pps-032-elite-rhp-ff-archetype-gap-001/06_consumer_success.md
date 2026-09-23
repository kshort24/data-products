# 06 · Consumer Success — `uc-pps-032`

Agents: `consumer-onboarding-agent` · `analytics-enabler` · `product-narrator`

## 1 · Personas and reading order

| Persona | Start with | Then | The one thing to take away |
|---|---|---|---|
| **DPO (Kellen)** | Report "The short version" | `00` §7 escalations; report §6 (your notebook, graded) | The gap is depth, not quality — and four decisions are yours |
| **Front office** | Report §4–§5 | Explorer → *Out there* (flip Board to "both") | No ranked arm beats Bowlan; the lever is a *starter's* elite four-seam |
| **Pitching coach** | Report §3 | Explorer → *The room* (drag the weight) | Duran and Wheeler are results-elite with average shape; Painter is the reverse problem |
| **Pitching analyst** | `03` §2 specs | `04` §5 reuse; `out/` receipts | The engine is a spec object — the next archetype is config |

## 2 · Explorer walkthrough (`dp_uc47_archetype_explorer.html`, offline)

1. **Archetype map** — every graded pitcher-season. Type "Bowlan" in *Find* to see him in the red corner; set
   Coverage = PARTIAL to see how much of the frame is incidental.
2. **The room** — drag *Weight on shape* from 0 to 1 and watch the #1 go Duran → Bowlan → McFarlane. Wheeler's
   and Painter's velocity charts sit underneath, in the client's own idiom.
3. **Out there** — Board = watch list shows Misiorowski's one start; the dashed lines are Bowlan and Duran at
   the same weight, so the comparison never goes stale when you move the slider.
4. **The needle** — scenario bars plus the swap ledger. "Replaces (ledger)" is accounting, not a roster move.
5. **Your notebook, graded** — ten claims, verdicts, and the governed number beside yours.
6. **Receipts** — the six method variants and the DQ scorecard.

*Notebook dark* flips every chart to `plotly_dark`.

## 3 · How to read a grade (one paragraph for coaches)

50 is the average right-handed four-seam in the frame; every 10 points is one standard deviation. 60 is "plus",
70 "plus-plus". A pitch's **shape** grade says how it looks leaving the hand — speed, carry, spin. Its
**results** grade says what hitters do with it — swing through it, or not, and what that costs in runs. The
two disagree more often than you'd think: 66 pitcher-seasons in the frame are results-elite with ordinary
shape, and 30 are the reverse. The archetype is the 11 that are both.

## 4 · FAQ

- **Why isn't Duran elite if he throws 100?** Velocity is one of three shape metrics; his ride and spin grade
  40 and 30. It's a 75 on results — the report's word is "brute force".
- **Why is Misiorowski not #1 on the board?** One start. The board requires the same 100-four-seam evidence as
  the population. He leads the watch list.
- **Why Ohtani?** Aspirational by design (decision 12). It's a statement about a four-seam.
- **Can I trust McFarlane's 60 shape grade?** The *shape* yes (velocity and spin are readable in a handful of
  pitches). The *results* grade on 94 pitches, less so — that's what THIN means.
- **What would change the answer?** Bowlan's health (carry-in), a full-season pull of the watch list (00 E-3),
  or a league-wide frame (00 E-4).

## 5 · Catalog entry (`product-narrator`)

| Field | Value |
|---|---|
| Product | Archetype Gap Analysis — Elite RHP Four-Seam (pilot) |
| Value stream | `pps` (scope note: external evaluation against a Phillies pitching need) |
| Purpose | Grades every right-handed four-seam in the governed house frame on what it looks like and what it does, ranks the Phillies-affiliated cohort, and measures how an external arm would change the staff's elite-four-seam share |
| KPIs | Shape grade · Results grade · `ff_elite_shape_flag` · `ff_elite_results_flag` · `ff_elite_archetype_flag` · Elite-FF composite · Elite-Four-Seam Share · needle swap |
| Grain | pitcher × season (graded); staff × season (EFS) |
| Refresh | Point-in-time, anchor 2026-09-20; a refresh is v1.1.0 |
| Owner | Kellen Short (DPO) |
| Certification | READY-CONDITIONAL (C1–C6) |

**Executive summary.** The Phillies' question was which kind of pitcher, and which pitcher, would add the most
if acquired. For the elite right-handed four-seam fastball, this product finds the club already has one of the
best in its comparison frame — Jonathan Bowlan's — and that he is the only one: 11% of the staff's four-seams
come from an elite arm, all of them his. No external pitcher with a full season of evidence grades higher. The
opportunity is a starting pitcher with an elite four-seam, because a starter's workload moves the staff almost
three times as much as a reliever's.
