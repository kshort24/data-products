# 06 · Consumer Success: `uc-pps-036`

Agents: `consumer-onboarding-agent` · `analytics-enabler` · `product-narrator`

## 1 · The product forms, and who each is for
| Form | Owns | Best reader | File |
|---|---|---|---|
| **Narrative dashboard** | the season in 8 chapters, with hover and theme | anyone; start here | `dp_uc52_mayza_2026_dashboard.html` · Artifact "The Sheriff of the Phillies Bullpen" |
| **Recap report (PDF)** | the long read with every caveat and the graded notebook | front office, pitching department | `dp_uc52_mayza_2026_recap_report.pdf` (9 pp) |
| One-page persona card (not built) | one glance for the bullpen coach | coaches | deferred, priced ~35k in the BID |
| 2027 projection (not bid) | re-sign decision | front office | no house model; CI-3 unverified |
| Video clips (not bid) | the bullet slider in motion | content | outside the comparison profile |

## 2 · Reading paths
- **Five minutes:** the hero tiles → Bottom line → ch. 2 Contact → ch. 5 The bullet slider.
- **Bullpen staff:** ch. 3 Platoon → ch. 6 Weapons (sinker to lefties, slider to righties; the slider to lefties is the soft spot).
- **Front office:** Bottom line → ch. 1 (relief table, n=32) → caveats. Contract status is a carry-in.
- **Your notebook:** report §9 or the dashboard appendix (14 claims graded).

## 3 · Dashboard walkthrough
1. **Theme bar:** Match my system (default), Brand light, Notebook dark. Remembered in this browser only.
2. **Chapter nav** stays at the top and highlights where you are.
3. **Hover** any mark for the pitcher-season, PA and value. Gray points are Phillies pitcher-seasons; red is Mayza 2026.

## 4 · How to read the new measures
- **Quick-AB rate (QA-1):** a PA counts when he reaches two strikes, or gets a ground ball, by the third pitch. 57.6% in 2026; the house median is 55.1%. It describes approach, not outcome: his career-low QA-1 came in one of his best results seasons.
- **Bullet slider (BS-1):** both breaks within 4 inches. Mayza's slider qualifies at 87.4 mph. It does NOT mean the pitch is unique: 11 other Phillies LHP slider seasons qualify.
- **Delivery distance (DS-1):** smaller = more alike on release, extension and primary-fastball shape. It says nothing about results.
- **Two wOBAs:** house wOBA (.285) ranks him; Statcast-basis wOBA (.299) is the one to set beside xwOBA (.288).

## 5 · FAQ
- **Why "runs on watch" and not ERA?** Statcast has no earned-run flag.
- **Is "#11 of 32" MLB-wide?** No. Phillies LHP relief seasons, 2015–26, 100+ PA, starts ≤ 20% of games.
- **Why does my notebook say 40% success?** Your function reads the count *before* each pitch, so it credits two strikes only when they come within two pitches. QA-1 uses the count after the pitch, which matches the definition you wrote down.
- **Why is my barrel rank different?** The name-filtered `nphl` frame lacks the barrel column for his Toronto years (HX-1). The governed frame has it: 6th-lowest of 9.

## 6 · Catalog entry (`product-narrator`)
> **The Sheriff of the Phillies Bullpen — Tim Mayza, 2026.** Mayza kept runners off with strikes and earned a .285 wOBA allowed, his third-best of nine seasons, with expected stats that say luck did not carry it. Louder contact from right-handed hitters is the watch item; a high, deep delivery and a hard bullet slider explain the profile. Internal · v1.0.0 · data through 2026-10-01 · verified 74/74.
