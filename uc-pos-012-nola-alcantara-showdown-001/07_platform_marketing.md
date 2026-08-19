# 07 · Platform & Marketing
**data-observability · version-controller · cost-watchdog**

## Observability — monitoring rules for this product

| Signal | Rule | Action |
|---|---|---|
| Freshness | `max(game_date)` in `phils_2026.parquet` should advance within ~24h of a played game (parquet auto-refresh observed since dp_uc25) | If stale > 48h in-season, re-pull before any refresh of this product |
| **Event trigger** | The 2026-08-19 game itself | **Backtest offer (standing uc-pps closure step):** once the game syncs, re-run `kpi_family` on the two starters' game rows vs the report's falsifiable calls (§6 W1–W3). One-command path documented below |
| Floor drift | HD-1 floor is derived; a new Nola-vs-MIA start with <27 PA-against would lower it | Build recomputes automatically; verification check 11 catches receipt drift |
| Schema drift | KF-1 CDEs (`events, description, zone, type, launch_speed, launch_speed_angle, bat_score, post_bat_score, stand`) | Verification fails loudly on any rename; O-7 is the cautionary precedent |
| Population drift | Wheeler cache must stay 2017–2019-only | Overlap assert in build + verification |

**Backtest command (after the game syncs):**
`DP_UC35_DATA=<root> python dp_uc35_nola_alcantara.py && python dp_uc35_verification.py`
then compare `nola_mia_seasons.csv` (2026 row) and `alcantara_phi_seasons.csv` (2026 row) against
the pre-game copies in this folder.

## Version manifest

| Field | Value |
|---|---|
| Product | uc-pos-012-nola-alcantara-showdown-001 |
| Version | 1.0.0 (initial publication, pre-game 2026-08-19) |
| Breaking-change policy | A post-game refresh is **non-breaking** (same schema, extended window) → 1.1.0. Changing the HD-1 floor rule or the SB-1 entity definition is **breaking** → 2.0.0 with deprecation note |
| Supersedes | Nothing. Extends the Nola line (uc-pps-008 → 014 → 021) with its first *offense-side* framing; does not supersede any pps advance report |
| Consumers to notify on change | Report/dashboard holders (internal staff scope per 00) |

## Cost & efficiency notes

Single-pass build: 12 season parquets (~60 MB) read once; all 24 receipts from two in-memory
frames; figures and dashboard render from receipts, never re-touching parquet. Verification is the
only second read — by design (independence beats cheapness at certify time). No recompute waste
identified; the one flagged inefficiency is `alcantara.parquet` (1.6 MB, stale) shipping in the
data plane while contributing only an entity lock — candidate for refresh or retirement, DPO call.

## Marketing one-liner (internal)

*The first data product in the org to make a pitcher a hitter: "Noles" — the .288-wOBA batter
Aaron Nola has spent a decade making out of the Marlins — plus the receipts on who really owns the
Phillies-offense exposure record, delivered governed, verified 79/79, the night before the rematch.*

## Suggested follow-ups (not commitments)

1. **O-10 fast-follow:** a governed `mlbam_id → display name` reference asset (one-time build,
   benefits every exposure/H2H product).
2. **Post-game backtest** (see trigger above) — closes the loop the way dp_uc25 did.
3. **SB-1 generalization:** the synthetic-batter entity applied to any (pitcher, opponent) pair is
   a reusable pattern for "who owns whom" content; ratification would make it a first-class KPI
   surface.
