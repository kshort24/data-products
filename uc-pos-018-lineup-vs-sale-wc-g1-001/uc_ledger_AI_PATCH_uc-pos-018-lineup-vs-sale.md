# UC LEDGER PATCH: `uc-pos-018` (UC #50)

**PENDING PASTE** into `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\uc_ledger_AI.md`.
Collision check 2026-09-29: `dp_uc50*`: none (root, `out/`, control plane) before this build; `uc-pos-018*`: referenced only as "next" in the uc-pps-034 patch and the uc-pos-017 README.
Note: the ledger file still reads "Next available: UC #25". Rows #25–#49 are pending pastes too (see the `uc_ledger_AI_PATCH_*` files).

## Row to append

| UC | ID | Subject | Status | Key artifacts |
|---|---|---|---|---|
| 50 | `uc-pos-018` | **Phillies lineup vs Chris Sale, NLWCS Game 1** (2026-09-29, at ATL) | Delivered pre-game · READY-CONDITIONAL · verified 372/372 | `dp_uc50_*` + `uc-pos-018-Phillies Lineup vs Chris Sale 20260929.md`; primary consumables `out/dp_uc50_fig4_lineup_notecard.png` + nine `out/dp_uc50_card_*.png` + `dp_uc50_lineup_vs_sale_report.pdf`; trail at `Agents for Data Products/data-products/uc-pos-018-lineup-vs-sale-wc-g1-001/`. First nine-card lineup scout; first import of the certified directional family (uc-pos-017) by a product; first deadline bid (D-1) |

**Next available: UC #51** (pps next `uc-pps-035` · pos next `uc-pos-019`).

## Pattern inheritance map: additions

- Lineup vs opposing starter: `uc-pos-001` (dp_uc14) → **UC50** (nine cards + notecard + pitcher page)
- Directional family consumed by a product: **UC50 (first use of `dp_uc46` by import, control-plane path)**
- Client-card grading (HP family) across multiple subjects: UC49 → **UC50**
- One-frame loader: CF-2 (UC49, one pitcher) → **BF-1** (UC50, nine batters + one pitcher)

## Findings worth carrying

1. **D-50-1:** `get_stats` / `measure_calcs` renames a `batter` level column to `pitches`; `nresults(['batter'], df)` raises. Use a display key or fix upstream.
2. **O-26 (second exposure):** a `nphl` name filter drops 10 of Sale's 2026 pitches (469 all-years).
3. **MV-1:** Savant `woba_value` credits reached-on-error at single value; house wOBA does not. Up to .029 apart on 2026 splits.
4. **House PA ≠ `woba_denom`:** house PA includes IBB and sac bunts, and a few PA-ending rows have a null `woba_denom` in the source. Harnesses must re-implement the house definition, not Savant's.
5. **Render QA pays again (C-6):** caught an axis label that put arm side toward a RHB (it's away, E-7).

## Repo-side artefacts to file

- `uc-pos-018-Phillies Lineup vs Chris Sale 20260929.md` → MLB repo root (**filed**)
- `dp_uc50_*.py` / `.md` / `.pdf` → MLB repo root (**filed**)
- `out/dp_uc50_*` → MLB repo `out/` (**filed**)
