# 07 · Platform & Reuse — What This UC Contributes Back

Agents: `version-controller` · `data-observability` · `semantic-modeler`

---

## A · Version manifest

| Item | Version | Change class |
|---|---|---|
| Nola advance file | v5 (UC8 → UC11 → UC15 → UC25 → **UC38**) | **Non-breaking extension** — new dimension (catcher), no change to any prior KPI |
| Locked pps KPI set | unchanged | none — all 10 inherited verbatim |
| `uc-cat-001` KPI set | KPI-1, KPI-3 move from *specced* to *implemented* | **Non-breaking** — first implementation, definitions unmodified |
| Battery KPI family | **v1.0 NEW-PROVISIONAL** | new — requires DPO ratification (E-2) before entering the locked set |

**Consumer impact: none.** No existing product changes behaviour. Nothing is deprecated.
`uc-pps-008`, `uc-pps-021` and `uc-pos-012` remain valid and are **not** superseded — this UC
adds a lens, it does not restate their numbers.

## B · Reusable assets created

| Asset | Reuse value |
|---|---|
| `count_state` (CS-1) | Any count-conditional analysis, repo-wide |
| `repeat_pitch_rate` (BAT-5) | Any sequencing question, any pitcher |
| `arsenal_entropy` (BAT-6) | Predictability tracking; obvious use in tipping/scouting work |
| `count_state_divergence` (BAT-7) | Plan-adaptivity, any pitcher |
| `mix_share` / `mix_vector` | Generic composition utilities |
| `confound_panel` | **The template for any non-randomised split in this repo.** Venue/rest/opponent/date profile beside a treatment split — reusable for platoon, home/road, day/night, catcher, umpire |
| `resolve_catcher_names` | Dual-path id→name with a loud cross-check — the pattern for any id-resolution problem after the Nola/Nolan-Hoffman lesson |
| `dp_uc38_verification.py` Tier A | **First unit-test-on-fixtures harness in the repo.** Every prior verification needed the data plane. This one proves KPI *logic* independently of data availability |

## C · Standing rules proposed from this run

| # | Proposed rule | Origin |
|---|---|---|
| **R-1** | **Pre-flight data-plane check before bidding a build tier.** Assert the parquet path resolves before promising executed numbers | The blocker. No prior bid priced mount risk |
| **R-2** | **Non-randomised splits ship with a confound panel or do not ship.** | G3 |
| **R-3** | **Unobservable constraints get a glossary entry, not a footnote.** AT-1 is the template | G4 |
| **R-4** | **Tier-A fixture unit tests for every new KPI**, so KPI logic can be certified even when data is unavailable | This run — it is the only reason anything was verifiable |
| **R-5** | **New KPIs whose "good direction" is context-dependent get no direction flag.** | `uc-cat-001` gave all ten a direction and had to caveat several |

## D · Observability (`data-observability`) — post-publish monitoring

Applies once the build runs. Runbook:

| Signal | Rule | Action |
|---|---|---|
| Freshness | `max(game_date)` more than 2 days behind game day | Refresh the parquet cache before quoting |
| New catcher id | An id appears in `fielder_2` not in the identity receipt | Re-run `resolve_catcher_names`; if the cross-check FAILs, **stop** |
| Sample drift | `Nola × Stubbs` window PA falls below 50 | The headline reverts to directional; report must re-flag |
| Schema drift | `pitch_type` null rate > 0.5%, or a new code outside `PITCH_GROUP` | Unmapped types land in `other` — audit before publishing a mix table |
| Window staleness | Any new Nola start | The last-5 window has changed; the report is stale. Re-run |

## E · Semantic layer (`semantic-modeler`)

| Metric | Valid dimensions | **Invalid** aggregations |
|---|---|---|
| BAT-1/2/3 shares | catcher, window, season, pitch group | **Never average shares across groups** — re-aggregate from counts |
| BAT-5 repeat rate | catcher, window, season | Never average across groups; re-derive from `repeats` / `pitch_pairs` |
| BAT-6 entropy | catcher, window, season | **Never average entropies.** Entropy is not linear — recompute on the pooled distribution |
| BAT-7 divergence | catcher, window, season | Never average divergences; recompute on pooled mixes |
| Outcome layer | catcher, window, season, stand | Never average rates; re-derive from counts (the standing house rule) |

**The non-linearity warning on BAT-6/BAT-7 is the single most important line in this file.**
Averaging entropies or divergences produces a number that looks reasonable and means
nothing. It is the most likely way this KPI family gets misused downstream.

## F · Open items carried forward

| ID | Item | Owner |
|---|---|---|
| **O-11** | Ratify or retire BAT-5/6/7 | DPO |
| **O-12** | Vectorise the entropy/divergence loops before any staff-wide run | data-engineer |
| **O-13** | Complete `uc-cat-001` — seven KPIs remain unbuilt; this UC paid for the plumbing | DPO to fund |
| O-2 (inherited) | Repo-wide null-`zone` handling convention | open |
| O-10 (inherited) | Pitcher id→name authority (`uc-pos-012`) | open — partly addressed by `resolve_catcher_names` |
| **O-14** | Ledger drift: ~6 unpasted `uc_ledger_AI_PATCH_*` rows | DPO |
