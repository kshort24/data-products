# 04 · Engineering Build: `uc-pos-018`

Agent: `data-engineer`

## 1 · Manifest (MLB repo root = data plane)

| File | Role | Lines | sha256 (12) |
|---|---|---|---|
| `dp_uc50_kernel.py` | Governed kernel: Section A imports (sha-pinned), B data access (BF-1), C provisionals (XW-1, HL-1, LR-1, TT-1, IC-1, NF-2) | 420 | `8084cb172d0c` |
| `dp_uc50_lineup_vs_sale.py` | Build: every receipt, DQ scorecard, freshness manifest, HP family, headlines JSON | 374 | `08d728d51efa` |
| `dp_uc50_narratives.py` | The words on every card, bound to `headlines.json`; asserts its own superlatives | 191 | `2e2072cab5d8` |
| `dp_uc50_build_figs.py` | 13 figures from receipts only; asserts subtitles against receipts | 302 | `2c8922ebfc24` |
| `dp_uc50_build_report.py` | Reader report `.md` from receipts + narratives | 104 | `688b25481342` |
| `dp_uc50_build_pdf.py` | Markdown → HTML → weasyprint (house recipe) | 38 | `6d271de49072` |
| `dp_uc50_verification.py` | Independent harness, families A–G | 254 | `a3b64cde59c4` |
| `dp_uc50_lineup_vs_sale_report.md` / `.pdf` | Reader report (15 pp) | — | — |
| `out/dp_uc50_*` | 29 CSV/JSON receipts + 13 PNG | — | — |

## 2 · Parent pins (asserted at build, DQ-15)

`dp_uc44_kernel.py a2c119096db2` · `dp_uc46_kernel.py a45ac9a76395` (control plane, loaded by path with portable candidates: `DP_CONTROL_PLANE` → `<MLB>/../Agents for Data Products` (laptop VM) → `<MLB>/../../Agents for Data Products` (Windows) → absolute) · `dp_uc48_kernel.py 0f63857a1032` · `barrel_rate.py 6282f090394a`.

## 3 · Environment disclosure

- **Build and harness ran on the laptop VM**, where the data lives. `/sessions` had 40 MB free, so `pyarrow 25.0.1`, `scipy 1.15.3` and `plotly 7.1.0` were installed to `/tmp/pyl` (`TMPDIR=/tmp/pt pip --target /tmp/pyl`), pandas 2.3.3 and matplotlib 3.10.9 from the system. No data file was staged to the cloud.
- **Figures:** matplotlib on the VM (kaleido/Chromium absent), Liberation Sans (Arial metrics).
- **PDF:** weasyprint 70.0 in the cloud sandbox, on the staged `.md` + PNGs only; the PDF was committed back.
- **Build wall time:** 21.6 s (BF-1 load ≈ 6.5 s). The harness runs in under a minute.

## 4 · Build-time assertions (the build refuses to publish if any fails)

1. Parent kernel hashes match the pins.
2. Regular-season anchor in `phils_2026` is exactly 2026-09-27.
3. No duplicate `PITCH_KEY` after precedence dedup.
4. Sale's 2026 subtitle numbers in the figure equal the HP-09 governed receipt.
5. The lineup aggregate's PA equals the sum of the nine hitters' career PA vs Sale (DQ-17, 163).
6. Realmuto's "lowest in 12 seasons" is re-asserted by the narrative module at render time.

## 5 · Receipts

| Receipt | Grain |
|---|---|
| `by_hand` | hitter × pitcher hand, 2026 |
| `lhp_season` | hitter × season, vs LHP |
| `sale_career`, `sale_season` | hitter × {career, 2026}; hitter × season, vs Sale |
| `sale_pa_log`, `sale_bip` | every PA end / BIP vs Sale |
| `rank`, `rank_pop` | LR-1 result; every LHP ≥ 20 PA per hitter |
| `pitch_group` | hitter × window × pitch group, vs LHP |
| `band`, `lhp26_bip` | hitter × third (+ All), 2026 vs LHP; the classified BIP |
| `last30` | hitter, 2026-08-28…09-27 |
| `lineup_agg` | LHB / RHB / all × career / 2026, vs Sale |
| `sale_arsenal`, `sale_arsenal_by_stand`, `sale_by_stand`, `sale_tto`, `sale_month`, `sale_game_log`, `sale_vs_phi_2026`, `sale_yoy`, `sale_pitch_extract` | Sale 2026 |
| `hp_reconciliation` | 12 client claims |
| `coverage`, `dq_scorecard`, `freshness_manifest` | governance |
| `method_variance` | MV-1 / O-8 disclosure |
| `verification_results` | 372 checks |
| `headlines.json` | every number the prose uses |

## 6 · Reproducing this

```bash
# laptop VM: install to /tmp once per VM session (the /sessions volume is full)
TMPDIR=/tmp/pt python3 -m pip install --no-cache-dir --target /tmp/pyl pyarrow scipy plotly
cd "<MLB repo>"
export PYTHONPATH=/tmp/pyl MLB_DATA_ROOT="$PWD" PYTHONDONTWRITEBYTECODE=1
python3 dp_uc50_lineup_vs_sale.py      # 15 PASS / 2 WARN / 0 FAIL
python3 dp_uc50_build_figs.py && python3 dp_uc50_build_report.py
python3 dp_uc50_verification.py        # 372/372 expected
python3 dp_uc50_build_pdf.py .         # needs weasyprint + pango (cloud sandbox or conda env)
```

On Kellen's Windows machine (`conda env snakes`) the same commands run from the repo root without the `PYTHONPATH` line; the kernel finds the control plane at `..\..\Agents for Data Products`.

## 7 · Reuse notes for the next lineup card

Swap `SALE_ID`, `LINEUP`, `GAME_*` and `ANCHOR_GAME_DATE` in the kernel; the build, figures, report and harness are opponent-agnostic except for the narratives module, which is the part a human (or `product-narrator`) should write each time.
