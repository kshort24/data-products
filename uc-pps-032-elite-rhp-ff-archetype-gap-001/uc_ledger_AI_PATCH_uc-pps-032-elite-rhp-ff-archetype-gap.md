# UC LEDGER PATCH — `uc-pps-032` (UC #47)

**PENDING PASTE** into `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\uc_ledger_AI.md`.
Collision check 2026-09-22: `dp_uc47*` none (root, `out/`, control plane); `uc-pps-032*` none.
Note: the ledger file itself still reads "Next available: UC #25" — rows #25–#46 are all pending pastes
(see the `uc_ledger_AI_PATCH_*` files at the root and in each control-plane package).

## Row to append

| UC | ID | Subject | Status | Key artifacts |
|---|---|---|---|---|
| 47 | `uc-pps-032` | Archetype Gap Analysis, pilot: Elite RHP four-seam — six-arm cohort + bounded external gap (2026-09-22) | Delivered · READY-CONDITIONAL · verified 241/241 | `dp_uc47_*` + `uc-pps-032-Elite RHP FF Archetype Gap 20260922.md`; trail at `Agents for Data Products/data-products/uc-pps-032-elite-rhp-ff-archetype-gap-001/` |

**Next available: UC #48** (pps next `uc-pps-033` · pos next `uc-pos-018`).

## Pattern inheritance map — additions

- 20-80 grading: UC44 SG-1/SG-2 → **UC47 (second use — ratification recommended)**
- Population benchmark: uc-pps-025 → UC44 SG-2 → **UC47 FR-1 house frame (Phillies logs + governed nphl)**
- Archetype engine (NEW): **UC47 AF-1…AF-6** — a spec object; the next archetype is config
- Reliability: **UC47 SG-7** split-half stabilization (k: whiff 56 swings, RV/100 1,084 pitches, shape < 1)
- Era drift: **UC47 SG-6** (velo +0.164 mph/season, spin +8.3 rpm/season, 2018–26)
- Human-parent reconciliation: uc-pos-015 → **UC47 Part H** (10 notebook claims)

## Findings worth carrying

1. **O-23:** `get_nphillies_data()` includes 15 MiLB files and never dedups against the Phillies logs.
2. **O-24:** team pulls (`giants-of-rangers-of-24`, `marlins-of-24-25`, `nats-of-23`, `tigers-of-20-22`,
   `white-sox-of-25-26`) are batter-keyed — `player_name` is the hitter.
3. **BC-1:** `brand-center-mcp` validator key precedence masks the layout font.
4. **RV/100 is ~21% split-half reliable** at a season of four-seams — never publish it unshrunk.
5. **Bowlan 2026** = #2 RHP four-seam of 405 pitcher-seasons in the frame; the only elite arm on the 2026 staff.

## Repo-side artefacts to file

- `uc-pps-032-Elite RHP FF Archetype Gap 20260922.md` → MLB repo root
- `dp_uc47_*.py` / `.md` / `.pdf` / `.html` → MLB repo root
- `out/dp_uc47_*` → MLB repo `out/`
