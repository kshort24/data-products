# 03 · Governance
Agents: `kpi-calculator` · `technical-lineage-builder` · `dq-rule-definer` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 0 · Rule-1 search before declaring anything new
| Candidate | Search | Hit | Decision |
|---|---|---|---|
| "wOBA as a function of K%" residual | `grep -i "resid\|k.*expected\|krate.*woba"` across `dp_uc*_kernel.py`, `Baseball Functions.ipynb`, control-plane `03_*` | 0 governed hits (client chart only, ungoverned) | **KR-1 new** |
| xwOBA vs wOBA gap | XW-1 (K50), WB-1 (K52) | found | inherited; "luck gap" is a name for WB-1 − XW-1, not a KPI |
| contract $ per inning | grep `aav\|salary\|contract` | 0 | **CE-1 new** |
| pre-registered signature ledger | PA-1 (K48), DB-1 (K53) | found (rule) | PR-1 is a new *instance* scored by the inherited PA-1 rule |
| outs / IP | OU-1 (K49), OU-2 (K51) | found | inherited |
| game score | GS-1 (K49) | found | inherited |
| pitch arsenal by season | K48 `arsenal_table` | found | inherited |

## 1 · Inheritance (`technical-lineage-builder`)
`dp_uc62_kernel.py` imports, never copies. Pins asserted at every run (`assert_lineage()`, 10 files):
`dp_uc53_kernel.py 03d7e380…` → `dp_uc52_kernel.py` → `dp_uc51_kernel.py` → `dp_uc50` / `dp_uc49` / `dp_uc48` / `dp_uc44_kernel.py` + `barrel_rate.py` + `cumulative_metric.py`; plus `phillies_dp/recap_viz.py e6c9436a…`.
**Section B (non-breaking):** KF-1 `client_frame` (K49 `kellen_frame` with the name passed in; K49 hard-binds Luzardo).

## 2 · New KPI specs (`kpi-calculator`; written into the BID at 20:19 ET, before code)
### KR-1 K-expected residual (provisional)
- **Plain language:** how much less (negative) or more (positive) a pitcher-season allowed than Phillies pitchers usually allow at the same strikeout rate.
- **Formula:** `KR-1 = woba − (a + b · krate)`; (a, b) from unweighted OLS of `woba` on `krate` over the population.
- **Population:** Phillies pitcher-seasons 2015–26, regular season, ≥ 100 PA (KP-1), **subject excluded** (n = 194). Fit: a = .414, b = −.426, R² = .344.
- **CDEs:** K44 `woba`, `krate` (both rounded to 3 dp by K44; RK-2 applies).
- **Grain:** any grain with a K% and a wOBA (season, pooled window).
- **Edge cases:** < 100 PA seasons are computed but never ranked or charted; the line is refit whenever the pool changes (version-controller: a refit is a correction, not breaking).
### CE-1 contract economics (provisional)
- **Formula:** `usd_per_ip = AAV / (outs / 3)`, `usd_per_bf = AAV / plate_apps`; the tenure row uses the contract total over the summed counts.
- **Inputs:** AAV $18M (CI-1), outs from OU-2, PA from K44. **Basis label required** ("AAV basis") wherever printed.
- **Edge cases:** no deferral, bonus timing or tax; a released player's remaining salary is still counted in the season it was owed.
### PR-1 ledger (provisional)
Ten signatures, bars and windows verbatim in the BID and `dp_uc62_kernel.PR1`. Changing a bar after publication is **breaking**.

## 3 · Lineage to the published numbers
```
walker.parquet + opponent files (pitcher id) ─┐
phils_2015..2026.parquet (pitching, R) ───────┼─ CF-2d career frame ─┬─ K44/K48/K50/K51/K52 ─ career_by_year.csv ─┐
                                              │                       ├─ window_metrics ─ windows.csv ─ PR-1 ─ pr1_ledger.csv
                                              └─ house_pitcher_seasons ─ phillies_pool_kp1.csv ─ KR-1 fit ─ kr1_fit.json
OU-2 on the full defensive log ─ outs ─ contract_economics.csv (CE-1, AAV CI-1)                               │
headlines.json ◄────────────────────────────────────────────────────────────────────────────────────────────┘
   └─ dp_uc62_narrative.py ─┬─ report .md → .pdf
                            └─ dashboard .html (+ Artifact)
```

## 4 · Defects and findings (carried to the DPO)
| ID | Finding | Status |
|---|---|---|
| **O-26 (recurrence)** | The client's `nphl[nphl.player_name == pn]` loses **483** Walker pitches to the name-dedup in `get_nphillies_data()` (2021: −160, 2022: −122, 2017: −63 …). Every client-frame pre-Phillies season undercounts him. | Known (UC49); recommend a pitcher-id loader in `Baseball Functions` |
| **SRC-1 (recurrence)** | The client's `pps` keeps postseason: the 2025 row carries 18 NLDS pitches | Known |
| **EV-1 (new)** | `inds().ev_mu` averages launch speed over every pitch with a reading. In 2015 only 16% of EV rows were non-BIP; by 2016–22 it is 39–46% (fouls, tips). The 2015 "spike" in the client CSV is a population change, not a sensor error, and `ev_mu` is not comparable across 2015 and later years. | New; recommend a BIP-only `ev_mu` or a footnote on `inds` |
| **CR-1** | `games > 3` vs a title saying "at least 3" drops 18 Phillies pitcher-seasons | Client code |
| **CR-2** | "Highlight his Career Overall" not implemented | Delivered as F1 era diamonds |
| **CR-3** | `inds` and `leadoff_walk_rate` merged then dropped | Client code |
| CR-4 | `px.scatter(subtitle=…)` claimed broken in turn 1 | **Withdrawn**: plotly 6.0.1 accepts it |
| RK-2 | K44 rounds rates to 3 dp before KR-1 consumes them | Known; harness tolerance .0005 |

## 5 · Privacy and tags (`privacy-watchdog`, `data-tagger`)
Public-figure performance data and public reporting. Contract figures are public (CI-1). No medical claim: velocity is reported, never explained (harness F checks the report for injury/surgery language). Tags: domain `pps`, subject area `player evaluation / contract review`, sensitivity **Internal**, external publish after DPO review of §5 of the report (it discusses a named player's contract value). **CLEAR** for internal.

## 6 · Version (`version-controller`)
`dp_uc62` **v1.0.0**, first release; additive (no inherited file edited). Breaking-change triggers: any PR-1 bar, the KR-1 population definition, the CE-1 basis.
