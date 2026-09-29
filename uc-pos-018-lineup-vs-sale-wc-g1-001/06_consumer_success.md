# 06 · Consumer Success: `uc-pos-018`

Agents: `consumer-onboarding-agent` · `analytics-enabler` · `product-narrator`

## 1 · The product forms and who reads them

| Form | File | Reader | When |
|---|---|---|---|
| **Lineup notecard** (one page) | `out/dp_uc50_fig4_lineup_notecard.png` | Manager, bench coach | In the dugout; the only page most people need |
| **Index cards** (nine) | `out/dp_uc50_card_{slot}_{name}.png` | Hitting coach, each hitter | Advance meeting, cage work before the game |
| **Reader report** | `dp_uc50_lineup_vs_sale_report.pdf` (15 pp) / `.md` | Analyst, front office, broadcast prep | Before the game; the source for everything above |
| **Sale page** | report §1, `out/dp_uc50_fig2_sale_arsenal.png`, `fig3_sale_tto.png` | Hitting coach, catchers (for the reverse read) | Advance meeting |
| **Receipts** | `out/dp_uc50_*.csv`, `headlines.json` | Analyst | Anyone who wants to check a number |

## 2 · Reading paths

- **Two minutes:** the notecard. The rule at the top, then your row.
- **Ten minutes:** report Bottom line → §2 lineup table → your hitter's card.
- **The analyst's path:** §5 "Your notebook, graded" → `03` §6 → `out/dp_uc50_hp_reconciliation.csv`.

## 3 · Persona notes (`consumer-onboarding-agent`)

**Manager.** Three things the card says that change decisions. First, the lefties at 2–3 are 1-for-23 against Sale this year, so don't expect the top of the order to carry the first two innings. Second, the right side (4–6, 8) is where the platoon edge lives; protect it with late pinch-hit choices, don't give it away. Third, there is no third-time-through fade in the results, so don't hold a move waiting for one.

**Hitting coach.** One rule for all nine: make the slider a ball and the four-seam a strike. Each card's PLAN line is that rule translated for the hitter's side and habit. The four-seam for Turner and Hill, taking the slider for Schwarber and Harper, no changeups for Sosa.

**Hitter.** Your card has one number that matters most: the red SALE line. If it says THIN, the plan comes from how you've hit lefties like him, not from your history with him.

**Broadcast / content.** Safe, sourced lines: Harper vs Sale .190 OPS in 21 PA, the lowest of the 20 lefties he's seen 20+ times; Schwarber's 1-for-12 against him this year after .327 career; Bohm .365 wOBA in 25 PA. Carry-ins are labelled; the "best left-handed pitcher in baseball" quote is Harper's, via Kellen's notebook.

## 4 · FAQ (`analytics-enabler`)

**Why does Harper's number say .190 when the notebook said .100?** Both the notebook's own method and the governed frame give .190 today. The ranking claim (worst of 20) holds either way. See HP-08.

**Why is Turner's "pulling away pitches" marked as not holding?** On away-third pitches in 2026 he pulled 31% and went the other way 37%. The weak contact on those pitches (.241 wOBA) is real. The pull habit shows up on inner pitches, and it pays there.

**Why wOBA *and* xwOBA?** At these sample sizes xwOBA (how hard and at what angle he hit it) is steadier than the result. Where the two disagree (Turner, Realmuto, Hill, Sosa's last 30), the card says so.

**Why pitch groups and not Sale's actual pitches?** Most hitters have fewer than 30 PA against Sale. "Breaking balls from lefties" is a bigger sample that includes pitches like Sale's slider. It's a proxy and it's labelled as one.

**Why is Stott's Sale line almost empty?** He has 4 career PA against Sale, all in 2025, and none in 2026.

**Can I re-run this for Game 2?** Yes. Swap the starter id and lineup in the kernel (`04` §7). Everything but the narratives regenerates.

## 5 · Catalog entry

> **uc-pos-018 · Phillies lineup vs Chris Sale, NLWCS Game 1 (2026-09-29).** A pre-game offensive advance scout: one-page notecard, nine hitter index cards, a Sale 2026 page and a 15-page report. Regular season through Game 162. Verified 372/372. Internal.
