# 04 · Engineering Build — `uc-pps-032`

Agent: `data-engineer`

## 1 · Build manifest

| File | Role | Reads | Writes |
|---|---|---|---|
| `dp_uc47_kernel.py` | Section C (FR-1, NR-1, AF-1…6, SG-6, SG-7); imports Sections A/B + SG-1/3/5 from `dp_uc44_kernel.py` | parquet | — |
| `dp_uc47_archetype_gap.py` | The build: universe → frame → stabilize → drift → grade → Parts A/B/H → DQ → headlines | parquet | 25 CSV + 2 JSON in `out/` |
| `dp_uc47_build_figs.py` | 7 Plotly figures (PNG + JSON), each asserting its own title; brand-center compliance | `out/` only | 7 PNG + 7 JSON + compliance CSV + scenario CSV |
| `dp_uc47_build_pdf.py` | Markdown → weasyprint, Phillies CSS | report md + PNGs | PDF |
| `dp_uc47_build_dashboard.py` | Archetype Explorer, plotly.js inlined | `out/` only | HTML (5.5 MB) |
| `dp_uc47_verification.py` | Families A–F | parquet + `out/` + report + HTML | verification log |

Run order (≈45 s end to end in the sandbox):

```bash
export MLB_DATA_ROOT="C:/Users/Kellen/OneDrive/Documents/Python Scripts/MLB"   # dp_uc44_kernel.py must be there
python dp_uc47_archetype_gap.py        # refuses to run unless the Phillies log ends 2026-09-20
python dp_uc47_build_figs.py           # needs kaleido + a Chrome/Chromium for PNG export
python dp_uc47_build_pdf.py
python dp_uc47_build_dashboard.py
python dp_uc47_verification.py         # expect 241/241
```

## 2 · Environment disclosure

- **Compute:** the cloud sandbox, not the laptop VM. `device_bash` worked this session, but the VM's `/sessions`
  volume was 100% full (43 MB free) and its interpreter has no `pyarrow` — same as uc-pos-015 E-1. All 140
  parquet files (12 Phillies seasons + 128 `nphl`) were **staged** read-only; outputs are **committed** back.
- **Libraries (sandbox):** pandas **3.0.2**, pyarrow, scipy, plotly 6 + kaleido (using the preinstalled
  Chromium), weasyprint, markdown. The client's Jupyter environment is likely pandas 2.x; nothing here depends
  on 3.x-only behaviour (checked: no `str` dtype assumptions; `.mean(axis=1)` keyword form used).
- **Egress:** PyPI reachable. The Chadwick register download (`pybaseball.playerid_reverse_lookup`) was
  **blocked at the proxy** → NR-1 resolves names from the logs.
- **MCP:** `brand-center-mcp.py` is not running as a server on this machine (no local MCP servers registered),
  so its tools were invoked **in-process** through its own `process_tool_call` router — the same code path an
  MCP client would hit.

## 3 · Build-time assertions (the build fails rather than publishing)

| Assertion | Where |
|---|---|
| Phillies log ends on the pinned anchor 2026-09-20 | build §0 |
| Governed union has 0 duplicate pitch keys | build §0 |
| Population = 405 and ELITE tier = 11 (figure 1 subtitle) | figs F1 |
| Bowlan 2026 is ELITE and #2 (figure 1 subtitle) | figs F1 |
| No 99+ mph Wheeler four-seam in 2023–26 (figure 2 subtitle) | figs F2 |
| HP-3/HP-4 verdicts SUPPORTED and Painter results grade 40 (figure 3 subtitle) | figs F3 |
| **No RANKED candidate out-scores Bowlan** (figure 4 title) | figs F4 |
| EFS = 467/4,201, Bowlan-out = 0, SP/RP volume ratio in [2.5, 3.0) ("almost 3×") | figs F5 |
| Weight winners Duran@0 / Bowlan@0.5 / McFarlane@1 (figure 6 subtitle) | figs F6 |
| RV k > 1,000 and velocity k < 1 (figure 7 subtitle) | figs F7 |
| Brand-center tool call returns `success` | figs |
| Every figure the report references exists (else the PDF build raises) | pdf |

## 4 · Receipts (`out/`)

| Receipt | Content |
|---|---|
| `universe_receipt` · `nphl_file_keying` · `name_resolution` | FR-1 step counts; per-file level/keying; NR-1 tiers |
| `stabilization` · `trend_adjust` · `population_moments` | SG-7 k values; SG-6 slopes; moments, Shapiro, twin agreement |
| `population_graded` · `tier_distribution` · `aspirational_ceiling` | every graded pitcher-season; tiers; top 15 of the era |
| `cohort_seasons` · `cohort_leaderboard` · `weight_sensitivity_cohort_best` · `weight_sensitivity_cohort_2026` | Part A |
| `staff_2026` · `efs_2026` · `efs_scenarios` · `candidates` · `needle` · `gap_size` | Part B |
| `sensitivity_matrix` | six method variants |
| `hp_reconciliation` · `hp_wheeler_velo_by_year` · `hp_painter_halves` · `hp_client_frame_audit` | Part H |
| `dq_scorecard` · `freshness_manifest` · `brand_compliance` · `palette_validation.txt` | governance |
| `fig1…fig7` (.png + .json) · `payload.json` · `headlines.json` · `verification_log.txt` | surfaces |

## 5 · Reuse queries (for the analyst persona)

```python
import dp_uc47_kernel as K
U, rec, keying = K.house_pitch_universe()                     # the governed "my dataset"
g = K.archetype_frame(U, K.ELITE_RHP_FF)                      # pitcher-season frame

# a second archetype is a new spec, not new code
ELITE_LHP_SWEEPER = K.ArchetypeSpec(
    name='elite_lhp_st', pitch_type='ST', throws='L', era=(2021, 2026),
    shape=[('velo', True), ('hb_in', True), ('spin', True)],   # add metrics to METRIC_DEFS / AF-2 as needed
    results=[('whiff_rate', True), ('rv100', True)])
```
Note: AF-2 currently aggregates the FF-relevant columns; a sweeper spec that grades horizontal break needs
`hb_in` direction handled for hand (LHP arm side is +`pfx_x`, so an LHP sweeper breaks negative — uc-pps-025 / uc-pps-029) — flagged in `07` §5 as the first
generalization task.
