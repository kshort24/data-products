# UC LEDGER PATCH — `uc-pps-031` (UC #45)

**PENDING PASTE** into `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\uc_ledger_AI.md`.
Collision check 2026-09-16: `dp_uc45*` none (root, `out/`, control plane); `uc-pps-031*` none.

## Row to append

| UC | ID | Subject | Status | Key artifacts |
|---|---|---|---|---|
| 45 | `uc-pps-031` | Sánchez command diagnosis, 2021–2026 — "is he near the zone?" (2026-09-16) | Delivered · READY-CONDITIONAL · verified 436/436 | `dp_uc45_*` + `uc-pps-031-Cristopher Sanchez Command 20260916.md`; trail at `Agents for Data Products/data-products/uc-pps-031-sanchez-command-diagnosis-001/` |

**Next available: UC #46** (pps next `uc-pps-032` · pos next `uc-pos-017`).

## Pattern inheritance map — additions

- Pitcher self-diagnosis: uc-pps-019 → **UC45**
- Edge geometry: UC8 `edge_rate` → **UC45 Shadow Zone family (SZ-0…SZ-5)**, same function, same constant
- Count leverage: uc-pps-017 PD-7 (inline) → **UC45 CL-1 `count_leverage(level, df)`** (Register P8 promotion)
- Peer netting: uc-pos-014 PB-1 → **UC45 PN-1** (pitcher side; native + common-rail bases)
- **Rulebook-change control (NEW):** UC45 ZC-1 `common_rail_rescore`, the standing control for 2025↔2026 zone comparisons

## New governed objects (all PROVISIONAL)

| Object | What it does |
|---|---|
| SZ-0 `shadow_region` | heart / edge_in / edge_out / beyond, on the governed edge distance |
| SZ-1 / SZ-2 | Shadow Zone Rate / Shadow Miss Rate (+ miss depth) |
| SZ-3 | Chase beyond the shadow (the client's proof) |
| SZ-4 | Chase in the outer edge band |
| SZ-5 | Miss direction (arm/glove mirrored by hand, high/low) |
| CL-1 | `count_leverage`: PD-7 promoted, plus even/behind/three-ball shares |
| PN-1 | `peer_delta_pitcher` |
| ZC-1 | `common_rail_rescore` + `abs_rails` |

## Findings worth carrying to the next UC

1. **O-18: the 2026 zone rails are a different instrument.** `sz_top`/`sz_bot` are one constant per batter. For the same hitters the top is a median 0.234 ft lower (84% of hitters). League in-zone in Phillies games .503 → .465. **Every 2025↔2026 zone comparison needs ZC-1.**
2. **Native peer netting is biased for low-zone pitchers** because rail-change exposure depends on vertical profile. Use PN-1 on the common-rail basis.
3. **`edge_rate` is governed but not in `Baseball Functions.ipynb`** (Register P16 said to confirm this; it wasn't done).
4. **Attack Zone "shadow" = 0.33 ft** conflicts with the ratified `BALL_FT`: 5.5% of pitches reclassify.
5. **`player_name` is the batter on batting-role rows.** Name pitchers from pitching-role rows only.
6. **Sánchez:** season premises mostly false and second-half premises true. His Edge Rate is flat and his Shadow Miss is up (+.038 his own). Chase on misses fell from .333 to .260 after the break. The leak is CH to RHB.

## Repo-side artefacts to file

- `uc-pps-031-Cristopher Sanchez Command 20260916.md` → MLB repo root
- `dp_uc45_*.py` / `.md` / `.pdf` / `.html` → MLB repo root
- `out/dp_uc45_*` → MLB repo `out/`
