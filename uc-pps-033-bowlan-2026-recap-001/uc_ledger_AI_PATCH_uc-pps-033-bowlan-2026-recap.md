# UC LEDGER PATCH: `uc-pps-033` (UC #48)

**PENDING PASTE** into `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\uc_ledger_AI.md`.
Collision check 2026-09-24: `dp_uc48*`: none (root, `out/`, control plane); `uc-pps-033*`: none.
Note: the ledger file still reads "Next available: UC #25". Rows #25–#47 are pending pastes too (see the `uc_ledger_AI_PATCH_*` files).

## Row to append

| UC | ID | Subject | Status | Key artifacts |
|---|---|---|---|---|
| 48 | `uc-pps-033` | **Jonathan Bowlan 2026 season recap: "The Tick and a Half"** (2026-09-24) | Delivered · READY-CONDITIONAL · verified 153/153 | `dp_uc48_*` + `uc-pps-033-Jonathan Bowlan 2026 Recap 20260924.md`; primary consumable `dp_uc48_bowlan_2026_dashboard.html` (persona lens + drill-through); trail at `Agents for Data Products/data-products/uc-pps-033-bowlan-2026-recap-001/`. First season-recap UC; first persona action ledger (PA-1) |

**Next available: UC #49** (pps next `uc-pps-034` · pos next `uc-pos-018`).

## Pattern inheritance map: additions

- Season recap as a function: client cell 115 → **UC48 SR-1 `season_recap` + CF-1 `career_frame`** (ratify on the Luzardo recap, cell 114)
- Grade inheritance by receipt (no re-grading): **UC47 → UC48** (DQ-08 reconciles counts)
- RV/100: UC47 → **UC48 (second use; ratification recommended)**
- Persona action ledger (hypothesis → signature → decision rule → confirmation): **UC48 PA-1 (first use)**
- Arm vs role: **UC48 VE-1**

## Findings worth carrying

1. **O-25:** `pitch_mix` rounds `pfx_x`/`pfx_z` to 0.1 ft, so notebook vert/HB is quantized in 1.2-inch steps.
2. **B-1:** `GroupBy.first()` returns the first non-null value per column; never use it for "first pitch" state.
3. **HP-18:** notebook loop variables (`gy`) leak into later subtitles.
4. **Carry-in correction:** Bowlan's 9/17 exit is reported as a right groin strain with no IL (Inquirer, 2026-09-18), not an oblique.
5. The pitcher-scouting-report skill's bundled ledger is stale at UC #12. The repo patches are the ground truth.

## Repo-side artefacts to file

- `uc-pps-033-Jonathan Bowlan 2026 Recap 20260924.md` → MLB repo root
- `dp_uc48_*.py` / `.md` / `.pdf` / `.html` → MLB repo root
- `out/dp_uc48_*` → MLB repo `out/`
