# UC LEDGER PATCH: `uc-pps-035` (UC #51)

**PENDING PASTE** into `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\uc_ledger_AI.md`.
Collision check 2026-10-12: `dp_uc51*`: none (root, `out/`, control plane) before this build; `uc-pps-035*`: referenced only as "next" in the uc-pps-034 and uc-pos-018 patches.
Note: the ledger file still reads "Next available: UC #25". Rows #25–#50 are pending pastes too (see the `uc_ledger_AI_PATCH_*` files).

## Row to append

| UC | ID | Subject | Status | Key artifacts |
|---|---|---|---|---|
| 51 | `uc-pps-035` | **Zack Wheeler 2026 season recap: "Still Zack Wheeler"** (2026-10-12) | Delivered · READY-CONDITIONAL · verified 204/204 | `dp_uc51_*` + `uc-pps-035-Zack Wheeler 2026 Recap 20261012.md`; primary consumables `dp_uc51_wheeler_2026_recap_report.pdf` and `dp_uc51_wheeler_2026_dashboard.html` (Artifact "Still Zack Wheeler"); trail and delivered copies at `Agents for Data Products/data-products/uc-pps-035-wheeler-2026-recap-001/`. First IX-1 (source-pinned extraction) inheritance; first window identified by reconciliation to a carry-in (SR-2); OC-1 second use |

**Next available: UC #52** (pps next `uc-pps-036` · pos next `uc-pos-019`).

## Pattern inheritance map: additions

- Season recap: UC48 SR-1 → UC49 → **UC51** (client's cell-21 chain + governed columns)
- Career frame: CF-1 (UC48) → CF-2 (UC49) → **CF-2b (UC51: MLB-only, subject name, enrichment join)**
- Season card: OC-1 (UC49, October) → **UC51 (second use, 2027 card; ratify)**
- Inheritance by extraction: **IX-1 (UC51, first use)** — ER-1 from UC8, JR-1 from the library, RCI from UC28
- Outs: OU-1 (UC49) → **OU-2 (UC51)**

## Findings worth carrying

1. **MI-1:** CF-2 admits any opponent file holding the id; pitcher-keyed AAA pulls (`lhvp26`) tag rehab games `R`. 148 Wheeler pitches. Filter by club.
2. **NM-1:** CF-2 stamps UC49's `SUBJECT_NAME` on every frame.
3. **OU1-1:** OU-1's event map misses base-running outs (6 of 486 for Wheeler). Use OU-2; back-check UC49 Game Scores.
4. **SR-2:** a reported "N-start stretch with ERA x" can be verified against the log; for Wheeler only 7/27–8/24 reproduces 8.51.
5. **HP-13:** `player_name` pooled across `pos` and `pps` mixes batters into a pitcher population.
6. **Bridge:** `device_bash` heredocs over ~20 KB fail with `E2BIG`; write in chunks.

## Repo-side artefacts to file

- `uc-pps-035-Zack Wheeler 2026 Recap 20261012.md` → MLB repo root (**filed**)
- `dp_uc51_*.py` / `.md` / `.pdf` / `.html` → MLB repo root (**filed**)
- `out/dp_uc51_*` → MLB repo `out/` (**filed**, 70 files)
- Delivered copies of the report, dashboard, code and receipts → this folder (**filed**)
