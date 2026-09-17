# 04 · Engineering Build — `uc-pps-031`

Agent: `data-engineer`

## 1 · Build manifest

| File | Role | SHA-256 (first 16) |
|---|---|---|
| `dp_uc45_kernel.py` | Governed kernel: A verbatim · A2 governed `edge_rate` verbatim · B access · D new | `1bde0dbc57f95072` |
| `dp_uc45_sanchez_command.py` | Build: 29 CSV receipts + payload; exit 0 = every build assertion held | `4ab56791caa36d73` |
| `dp_uc45_build_figs.py` | Six figures (Fig 3 asserts its own headline) | `940396a2faaccc01` |
| `dp_uc45_build_pdf.py` | Markdown → weasyprint (inherited from dp_uc44) | `8ff1a96c2decf32b` |
| `dp_uc45_build_dashboard.py` + `tpl/` | Self-contained dashboard | `0667501ca5299e07` |
| `dp_uc45_verification.py` | 8-family independent harness, 436 checks | `497d0e103b9bcc8e` |

Hashes are for the files as committed on 2026-09-16. The OneDrive copy is authoritative; re-hash after any edit.

## 2 · Inheritance, proven rather than claimed

- **Section A** is byte-identical to `dp_uc44_kernel.py` Section A (`get_stats` … `two_prop_z`), with one insert: `barrel_rate`, byte-identical to `Baseball Functions.ipynb` cell 58. This is its first transcription into a dp kernel; the client's cell calls it. Verified by family H.
- **Section A2** (`_dist_to_zone_edge`, `edge_rate`) is byte-identical to `dp_uc38_nola_stubbs_battery.py`. Verified by family H.
- **Section B** is copied from dp_uc44 (`apply_woba_weights`, `load_phils`, `load_pps`, `load_pos`).
- **Section C** is intentionally absent (SG family not used, `03` §1).

## 3 · Environment disclosure

- The data plane was **staged** from the MLB repo into the cloud workspace (six parquet files, wOBA constants, the notebook). `device_bash` was reachable, but the VM had no free disk for `pyarrow`, `plotly` or `weasyprint`. Outputs were committed back to both planes.
- Python 3.11, pandas 3.0.2, numpy 2.4.4, scipy 1.17.1, pyarrow (installed), matplotlib 3.10.9, weasyprint 70.0, markdown 3.10.2. **pandas 3** is newer than Kellen's 2.3.3; nothing in the kernel depends on the difference (family G ran the notebook's own code under pandas 3 and matched).
- The dashboard vendors no library: vanilla JS + inline SVG, 684 KB with 5,855 embedded pitches. This sidesteps the open F1 item (a 4.7 MB plotly bundle per product).

## 4 · Build-time assertions (the build refuses to publish if any fails)

anchor = 2026-09-15 · no duplicate PITCH_KEY · one `player_name` for 650911 · LHP only · HBP sign rule ·
LHP sinker `pfx_x > 0` · 31/31 appearances are starts · rail constancy 2026 > 95% and 2025 < 10% ·
edge twin = governed `edge_rate` · ZC-1 decomposition identity · 31 subject starts in the start distribution ·
DQ scorecard has no FAIL.

## 5 · Re-run recipe (Kellen's machine)

```bash
cd "C:\Users\Kellen\OneDrive\Documents\Agents for Data Products\data-products\uc-pps-031-sanchez-command-diagnosis-001"
set MLB_DATA_ROOT=C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB
python dp_uc45_sanchez_command.py      # receipts -> out/
python dp_uc45_build_figs.py           # figures -> out/
python dp_uc45_build_pdf.py            # needs weasyprint
python dp_uc45_build_dashboard.py
python dp_uc45_verification.py         # exit 0 == 436/436
```
After a cache refresh the anchor assertion **fails by design** (C1). Bump `ANCHOR_GAME_DATE` and treat the result as a new version.

## 6 · Reuse queries

```python
import dp_uc45_kernel as K
pps = K.load_pps((2026,))
K.shadow_profile(['player_name'], pps)                       # SZ-1..4 for the staff
K.shadow_miss_direction(['player_name'], pps)                # SZ-5
K.count_leverage(['player_name', 'game_date'], pps)          # CL-1 per start
rails = K.abs_rails(K.load_phils((2026,)))
K.shadow_profile(['game_year'], K.common_rail_rescore(K.load_pps((2025,)), rails))  # ZC-1
```

## 7 · Receipts (`out/`, 29 CSV + payload + 6 PNG + verification log)

`freshness_manifest` · `notebook_reproduction` · `season_panel` · `half_panel` · `month_panel_2026` ·
`start_log_2026` · `league_control` · `zone_rail_audit` · `peer_delta` · `peer_cohort` · `common_rail` ·
`rail_decomposition` · `by_stand` · `by_stand_half` · `by_pitch` · `by_pitch_half` · `by_pitch_stand_2026` ·
`miss_direction` · `count_state` · `count_state_league_2026` · `start_distribution` · `start_distribution_summary` ·
`geometry_crosswalk` · `premise_tests` · `split_tests` · `defect_exposure` · `dq_scorecard` · `pitch_locations` ·
`verification_results` · `payload.json` · `fig1…fig6` · `verification_log.txt`
