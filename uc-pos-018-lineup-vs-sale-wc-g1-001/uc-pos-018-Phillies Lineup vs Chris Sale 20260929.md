```yml
# Identity
name: Phillies Lineup vs Chris Sale 20260929 NLWCS G1 (A)
id: uc-pos-018-Phillies Lineup vs Chris Sale 20260929
description: >
  Pre-game offensive advance scout for NL Wild Card Series Game 1 at Atlanta. Nine hitter
  index cards (three client-authored cards reproduced and graded, six new), a Sale 2026
  arsenal page, and a one-page lineup notecard, each plan tied to what Sale throws that hitter's side.

# Classification
value_stream: Position player / offense
value_stream_code: pos
status: Build Complete — READY-CONDITIONAL — Awaiting DPO Sign-off
priority: High (game-day)

# People
personas: Manager, Hitting Coach, Hitters, Analyst, Broadcast/Content
owner: Kellen Short

# Relationships
parent_use_case: uc-pos-001 (Phillies vs Wacha, lineup-vs-starter) · uc-pos-017 (directional family)
sub_use_cases: []

# Metadata
created: 2026-09-29
last_updated: 2026-09-29
build_artifact: dp_uc50_lineup_vs_sale.py (+ kernel, narratives, figs, report, pdf, verification)
governance_trail: Agents for Data Products/data-products/uc-pos-018-lineup-vs-sale-wc-g1-001/

# Data References
kpis: [plate_apps, ba, obp, slg, ops, woba, xwoba (XW-1, NEW), krate, bbrate, whiff_rate, chase_rate,
       barrel_rate, hard_hit_rate, pull_rate, straight_rate, oppo_rate, pull_air_rate,
       h_band (HL-1, NEW), lhp_rank (LR-1, NEW), tto (TT-1, NEW), usage, release_speed, pfx (in)]
data_domains: At-Bat Outcomes, Batted Ball Profile, Directional Hitting, Pitch Profile, Pitch Outcomes, Strike Zone
```

# Phillies Lineup vs Chris Sale — NLWCS Game 1 (2026-09-29)

> **Document status:** Deliverables `dp_uc50_lineup_vs_sale_report.md/.pdf`, `out/dp_uc50_fig4_lineup_notecard.png`, `out/dp_uc50_card_*.png` · Trail `data-products/uc-pos-018-lineup-vs-sale-wc-g1-001/` (00–07, BID) · Receipts `out/dp_uc50_*` · Verified 372/372.

## Business Context

### Problem Statement
Game 1 of the Wild Card Series in Atlanta against Chris Sale, the pitcher Harper called "the best left-handed pitcher in baseball." Getting a jump on him matters. The Phillies need to know which of their nine have a real chance against him, what he'll throw each of them, and what each hitter should do about it, before first pitch.

### Business Questions — Answered
1. **What does Sale look like in 2026?** The same as 2024 with 1.3 more mph: .258 wOBA against, 30.8% K, four-seam 96.1, slider 40% of pitches with 38% whiff.
2. **How has this lineup hit him?** 163 PA, .258 wOBA. Lefties .217 career and 1 hit in 24 PA in 2026. Righties .278.
3. **Who has the best chance?** Bohm (.365 in 25 PA; hits lefties every season), then Turner (.323, 27 PA). Schwarber's career .327 comes with 1 hit in 12 PA in 2026.
4. **Who does he own?** Harper (.190 OPS, 21 PA, #1 of 20 LHP), Sosa (.218 wOBA, 23 PA, chase-driven), Realmuto (.194, 20 PA).
5. **Is there a third-time-through window?** No: .262 / .254 / .258 wOBA; only the HR rate rises.
6. **Do the client's three cards hold?** Schwarber exactly; Turner's KPIs hold with small drift but the "pulls away pitches" narrative does not; Harper's ranking holds at .190, not .100.

### Actions
- **Hitting coach:** one rule for all nine: make the slider a ball and the four-seam a strike. Per-hitter plans are on the cards.
- **Manager:** expect the right side (4–6, 8) to carry; protect the platoon edge late; don't wait for a third-time fade.
- **Analyst:** grade the plans after the game (v1.1.0 tripwire).

## Data Specification (summary)
- **Grain:** pitch; key `(game_pk, at_bat_number, pitch_number)`. **Entity keys:** MLBAM ids (9 batters, Sale 519242).
- **Window:** regular season 2015 → 2026-09-27; Sale profile 2026 only.
- **Sources:** Phillies logs 2015–2026 + every MLB opponent file (precedence-deduped), `atlp26` for Sale 2026, `sale.parquet` for Sale's career.
- **New KPIs:** XW-1, HL-1, LR-1, TT-1 (provisional; specs in `03` §2).
- **Known gaps:** Sale 2025 partial; De La Cruz's non-Phillies 2025 partial; head-to-head samples small (THIN < 10 PA).
