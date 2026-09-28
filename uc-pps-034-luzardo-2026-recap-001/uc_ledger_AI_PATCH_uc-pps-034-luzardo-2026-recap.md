# UC LEDGER PATCH: `uc-pps-034` (UC #49)

**PENDING PASTE** into `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\uc_ledger_AI.md`.
Collision check 2026-09-27: `dp_uc49*`: none (root, `out/`, control plane) before this build; `uc-pps-034*`: referenced only as "next" in the uc-pps-033 patch.
Note: the ledger file still reads "Next available: UC #25". Rows #25–#48 are pending pastes too (see the `uc_ledger_AI_PATCH_*` files).

## Row to append

| UC | ID | Subject | Status | Key artifacts |
|---|---|---|---|---|
| 49 | `uc-pps-034` | **Jesús Luzardo 2026 season recap: "The Chase"** (2026-09-27) | Delivered · READY-CONDITIONAL · verified 226/226 | `dp_uc49_*` + `uc-pps-034-Jesus Luzardo 2026 Recap 20260927.md`; primary consumable `dp_uc49_luzardo_2026_dashboard.html` (8 chapters, Labor Day stepper, October card); trail at `Agents for Data Products/data-products/uc-pps-034-luzardo-2026-recap-001/`. First narrative/multi-form UC; first pre-registered postseason card (OC-1); first build run entirely on the laptop VM |

**Next available: UC #50** (pps next `uc-pps-035` · pos next `uc-pos-018`).

## Pattern inheritance map: additions

- Season recap: UC48 SR-1 → **UC49 (second use; ratify)**; CF-1 → **CF-2** (subject-agnostic, id scan of `nphl`)
- Parent reproduction: uc-pps-017 first-half figures recomputed 4/4 before extension
- Pre-registration: **UC49 OC-1 (first use)** — signatures, bars from the subject's own season, published backtest
- Game story (pitch-by-pitch stepper keyed by `game_pk`): **UC49 (first use)**
- Starter-workload context cut with sensitivity: **UC49 CX-1b**

## Findings worth carrying

1. **O-26:** `get_nphillies_data()` keep-first dedup across sorted files drops pitcher-keyed rows in favour of batter-keyed ones; name-filtered pitcher frames lose pitches (230 for Luzardo).
2. **BS-1:** byte search under-counts source files (2 vs 21 by id). Profile by the id column. **Closes uc-pps-033 V-3** (Bowlan's ".269 / 60 G" = one Lehigh Valley outing via `lhvp26.parquet`).
3. **ENV-1:** `dp_uc48_kernel` US-1 groups by `game_pk` twice; pandas 2.3 raises. US-1b fix; upstream as v1.0.1.
4. **E-7:** PM-1 docstring's `plate_x` sign is backwards; + = first-base side (catcher's view).
5. **HP-10:** plotly `trendline='ols'` with `color=` fits one line per color group.
6. The laptop VM can run builds from `/tmp` installs (`pip --target /tmp/pyl`, `TMPDIR=/tmp/pt`).

## Repo-side artefacts to file

- `uc-pps-034-Jesus Luzardo 2026 Recap 20260927.md` → MLB repo root (**filed**)
- `dp_uc49_*.py` / `.md` / `.pdf` / `.html` → MLB repo root (**filed**)
- `out/dp_uc49_*` → MLB repo `out/` (**filed**, 63 files)
