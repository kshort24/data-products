# dp_uc25 — Governance Spec · Aaron Nola vs Los Angeles Dodgers (uc-pps-021)

Build date: 2026-07-22 · Owner: Kellen Short (DPO) · Status: **Build Complete — Ready for DPO Sign-off**

---

## §1 DPO sequencing & ledger

- **Claimed:** UC #26 / **`uc-pps-021`** / build number **dp_uc25**. Verified against the repo (not the
  drifting ledger) at intake: highest `dp_uc*` on disk = **dp_uc24** (Turner, uc-pos-006, 2026-07-21);
  highest `uc-pps-*` contract = **uc-pps-020** (Wheeler ASG, 2026-07-15). This build therefore claims
  the next free slots on all three counters: script **25**, pps id **021**, ledger UC **26**.
- **Ledger drift note:** `uc_ledger_AI.md` continues to lag delivered work — several `uc_ledger_AI_PATCH_*`
  rows are already staged in the repo root (pps-015, pps-016, pps-017, pos-006, marsh) awaiting a paste.
  This UC adds one more patch file (`uc_ledger_AI_PATCH_uc-pps-021-nola-dodgers.md`, see below).
- **Ledger row Kellen needs to append to `uc_ledger_AI.md`:**

  > `| 26 | uc-pps-021 | Nola vs Dodgers (2026-07-22, PHI vs LAD @ CBP) | Build complete | dp_uc25_nola_vs_dodgers* + uc-pps-021-*.md — 3rd extension of the Nola advance file; adds recency lens (3 new starts), approach-shift tracks, and a 7-hitter H2H; inherits UC8 edge/OOZ-CS/AIR-GB KPIs |`

  …and bump "Next available" to **UC #27 / uc-pps-022** (or **uc-pos-007** on the batting track).
  The installed skill's ledger copy needs the same one-line update (flagged per skill maintenance rule).
- **Supersession / retirement decisions:** none *retired*. This UC **extends** the Nola advance line —
  `uc-pps-008` (vs WAS) and `uc-pps-014` (vs KC) remain valid opponent-specific products and are **not**
  superseded. However, for the **Nola season-to-date profile** specifically, dp_uc25's live figures
  (through 2026-07-16) **supersede the stale season lines** quoted in dp_uc8 (through 6/24) and dp_uc15
  (through 7/04, and computed on an earlier cache — see §2).
- **Pattern lineage:** UC3 → UC6 → UC8 → UC11 → UC15 → **UC26** (locked-KPI inheritance + opponent
  dimension from the pitcher's own log).

## §2 Intake gap report (use-case-validator)

| Gap | Class | Resolution |
|---|---|---|
| Confirmed LAD lineup not posted at build | Non-blocking | DPO scoped the matchup to **7 named hitters** (not a 1–9 card); labeled everywhere; confirm the actual card pre-game |
| "his last few starts" underspecified | Non-blocking | Fixed to the **3 starts since dp_uc15** (7/05, 7/10, 7/16); added a recency split + per-start game lines |
| Kyle Tucker as a Dodger / roster timeline is sandbox-specific | Non-blocking | H2H resolved **from Nola's own log** via des-parse (modal name per batter id); 7/7 named hitters found; no hand-keyed MLBAM ids |
| **xwOBA field-quality risk** | **Non-blocking (governance find)** | The locked `get_stats.xwoba` column is a **pitch-level mean contaminated by non-BIP rows** (some strikeouts carry 0.0) and is unstable year-to-year. Fixed this session by computing **`xwobacon`** = mean `estimated_woba_using_speedangle` on BIP (`type=='X'`); DQ-verified **>99% populated on BIP** every season. The contaminated column is **not cited**. |
| wOBA methodology (FanGraphs vs Statcast) | Non-blocking | Locked KPI is **FanGraphs-weighted** (2026 = .358); Statcast `woba_value/denom` reads ~.01 higher (.367). dp_uc15's **.377** was an earlier cache on the Statcast side; dp_uc25's live FanGraphs number is authoritative and labeled |
| Official IP absent from pitch-level Statcast | Non-blocking | `ip_computed` from terminal-event outs; labeled, not box-score |
| H2H samples small (8–86 PA) | Non-blocking | PA printed on every line; only Freeman (86) treated as a real sample; rest directional |
| No blocking gaps | — | Proceed |

## §3 Source profile (source-system-profiler)

| Source | Window | Filter | Fitness |
|---|---|---|---|
| `data/phillies/phils_2015..2026.parquet` | 2015-04 .. **2026-07-16** (Nola's last start) | `phillies_role=='pitching' & pitcher==605400 & game_type=='R'`, deduped on game_pk+at_bat_number+pitch_number | career log, 12 seasons / 20 GS in 2026 — fit for all angles (see `dp_uc25_freshness_manifest.csv` for exact row count) |
| `wOBA and FIP Constants.csv` | seasons 2015–2026 | joined on `game_year` | season-correct FanGraphs wOBA weights |
| DPO scope decision | 2026-07-22 | 7 named hitters | **manual carry-in**; not a posted lineup |

**Entity lock:** `pitcher == 605400` (Aaron Nola). Guards the canonical Nolan Hoffman (676510)
name-filter contamination. H2H batter ids resolved by des-parse (modal name per batter id) — no
hand-keyed MLBAM ids. **DQ scorecard confirms 7/7 named hitters resolved from the log.**

## §4 KPI specs (kpi-calculator)

**Inherited VERBATIM from the locked UC8→UC11→UC15 line** (functions copied from
`dp_uc15_nola_vs_royals.py`, mechanically identical): `get_stats`/`nresults` (wOBA, xBA-family,
K/BB/HR rates), `whiff_rate`, `chase_rate` (+ in-zone), `putaway_rate`, `fpsr`, `hard_hit_rate`.

**Inherited from UC8 (already glossary-approved there — NOT new):** `edge_rate`,
`ooz_called_strike_rate`, `air_gb_rate`. Copied verbatim with their UC8 constants (`PLATE_HALF=0.83`,
`BALL_FT=2.94/12`, `TAKES`). Re-used here to re-test the ABS question and the contact-quality engine
on fresh data — no re-derivation, no new glossary terms.

**New / report-local computed items (no new governed rate KPI):**

| Item | Definition | Grain | Population | Edge cases |
|---|---|---|---|---|
| `xwobacon` | mean `estimated_woba_using_speedangle` over BIP (`type=='X'`) | season / stand / segment / hitter | Nola career log | xwOBA **on contact**, not full xwOBA; **replaces the contaminated pitch-level `get_stats.xwoba`** (see §2); labeled to prevent drift |
| `chase_up_rate` | swings on pitches above `sz_top` ÷ pitches above `sz_top` | season | Nola career log | UC8 ABS helper; observational, not an ABS-feed signal |
| `ip_computed` | Σ terminal-event outs (EVENT_OUTS map) ÷ 3, X.Y notation | game | Nola career log | baserunning outs (CS/pickoff) not credited → can undercount vs box score; labeled |
| monthly usage / velo | pitch-share and mean velo by calendar month | month × pitch | Nola 2026 | descriptive approach-shift tracks; no rate treated as stable |

## §5 Glossary deltas (business-glossary-agent)

None required. The locked rates and the UC8 trio (edge / OOZ-CS / AIR-GB) are already approved.
**Recommendation:** `xwobacon` has now recurred across **UC15** (as an "xwOBAcon check") and **UC25**
(hardened with a BIP-completeness DQ guard). Per the skill's promotion rule (recurs in a third UC →
promote), it is a **promotion candidate for the next UC** — with the documented caveat that the
pitch-level `get_stats.xwoba` column must be deprecated for xwOBAcon reporting repo-wide.

## §6 DQ scorecard summary (data-quality-engineer)

Full receipt: `out/dp_uc25_dq_scorecard.csv`.

| Check | Result |
|---|---|
| entity_lock (605400 only; Hoffman 676510 excluded) | **PASS** |
| dedup (game_pk+ab+pitch unique) | **PASS** |
| game_type (R only) | **PASS** |
| season_coverage (2015..2026) | **PASS** |
| freshness (max game_date == 2026-07-16, Nola's last start) | **PASS** |
| h2h_coverage (7/7 named hitters resolved) | **PASS** |
| completeness — pitch_name / release_speed / plate_x / plate_z / zone / description / stand / bb_type / launch_angle / launch_speed | 1.000 on core locating/among-contact fields |
| completeness — events / woba_value / woba_denom | ~0.26 — **expected by design** (only terminal pitches carry events/wOBA values) |
| fitness — `estimated_woba_using_speedangle` on BIP | **>0.99 every season** — xwobacon is safe on contact; the pitch-level mean is not (see §2) |

No blocking DQ findings.

## §7 Lineage (technical-lineage-builder)

```
phils_2015..2026.parquet ──filter: role=pitching, pitcher=605400, game_type=R──> career log
   ├─ dedup(game_pk,ab,pitch) ── merge wOBA constants on game_year
   ├─ nresults(game_year) + xwobacon(game_year) ──────> dp_uc25_nola_season_trend.csv ─> (profile)
   ├─ nresults(stand) [2026] ─────────────────────────> dp_uc25_nola_by_stand_2026.csv
   ├─ groupby(stand,pitch_name)+whiff [2026] ─────────> dp_uc25_nola_arsenal_2026.csv ─> fig1, fig2
   ├─ game_lines(all 2026 starts) ────────────────────> dp_uc25_recency_game_lines.csv ─> fig3
   │    └─ split: >7/04 vs ≤7/04 vs full ─────────────> dp_uc25_recency_split.csv
   ├─ usage/velo by calendar month [2026] ────────────> dp_uc25_monthly_usage.csv / _velo.csv ─> fig3
   ├─ SL only, per-start since debut ─────────────────> dp_uc25_slider_arc.csv
   ├─ fpsr/chase/putaway/edge/ooz-CS/chase-up by year ─> dp_uc25_process_abs_by_year.csv ─> fig4(L)
   ├─ air_gb/hard_hit/hr/xwobacon by year ────────────> dp_uc25_contact_quality_by_year.csv ─> fig5
   ├─ process by stand (+xwobacon) [2026] ────────────> dp_uc25_process_by_stand_2026.csv ─> fig4(R)
   └─ des-parse name map × 7 named hitters ───────────> dp_uc25_dodgers_h2h.csv ─> fig6
DPO scope (manual carry-in) ───────────────────────────> HITTERS block + dp_uc25_freshness_manifest.csv
```

## §8 Certification readiness (certification-agent)

| Artifact | Present | Consistent |
|---|---|---|
| Build script `dp_uc25_nola_vs_dodgers.py` | ✅ | runs clean end-to-end this session |
| Reader report `.md` + `.pdf` (branded, 9pp) | ✅ | every number traces to an `out/dp_uc25_*` receipt |
| 14 CSV receipts + 6 branded figures | ✅ | new files only; nothing overwritten |
| Persona action card `.pdf` + interactive `.html` | ✅ | numbers pulled from the same receipts |
| Independent verification `dp_uc25_verification.py` | ✅ | separate code path; PASS/FAIL ledger (see §closure) |
| DQ scorecard | ✅ | PASS ×6, completeness + xwOBAcon fitness explained |
| Freshness manifest | ✅ | 7-hitter scope + lineup flagged as manual carry-in / projected |
| Use-case contract `uc-pps-021-*.md` | ✅ | at repo root |
| Ledger update | ⚠️ pending Kellen | one row + next-available bump (see §1); patch file staged |

**Certification: PASS (conditional on ledger append).**
**Closure step:** post-game backtest — the projected attack plan (get ahead of the 5 lefties, finish
with curve/changeup, keep the fastball down) vs actual pitch mix and results, including whether the
lefty first-pitch-strike rate climbed off 58.8% and whether the air-ball/HR damage held.
