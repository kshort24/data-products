# Ledger patch: UC #64 / uc-pps-040 (PENDING PASTE into `uc_ledger_AI.md`)

Paste the row into the Tail table and replace the "Next available" line. Paste the UC52–UC63 patches first; they are still pending.

| 64 | `uc-pps-040` | **Aaron Nola 2026 season recap + career pitch-sequencing engine: "Better Process Than Results, and a Book Built on the Curve"** (2026-11-16) | Delivered · READY-CONDITIONAL (C1–C4) · harness 43/43 · DQ 21/3/0 · V1–V7 10/10 | `dp_uc64_*` + `uc-pps-040-Aaron Nola 2026 Recap 20261116.md`; consumables `dp_uc64_nola_2026_recap_report.pdf`, `dp_uc64_nola_2026_dashboard.html` (Artifact "Aaron Nola 2026", Sequence Explorer). Trail in `Agents for Data Products/data-products/uc-pps-040-nola-2026-recap-sequencing-001/`. First sequencing engine in the plane; first intake with a DPO ruling round before pricing |

Pattern inheritance additions (UC64):
- pitcher recap spine K63 → **K64** (imports K63 whole; no edits upstream)
- **SQ family** (provisional): SQ-0 client `pitch_sequence` verbatim · PT-H · SQ-1 windows · SQ-2 count-adjusted setup lift · SQ-3 terminal endings · SQ-4 shrink + PA-cluster bootstrap · SQ-5 era drift / FADED + SQ-5d decomposition · SQ-6 batterymate book (within-season permutation) · PI-1 predictability
- **PC-1 poor contact** = Savant LSA 1–3 (DPO-defined, Q-B) · **OUT-1** out PA

Next available: **UC #65 / dp_uc65** (pps next `uc-pps-041` · pos next `uc-pos-026` · cat next `uc-cat-003`) — as of 2026-11-16.

## Findings worth carrying
1. **Sequencing claims need a calibration line.** 28 of 176 rankable sequences cleared a 90% interval vs 17.6 by chance; print that beside any ranked list.
2. **Era tests must use era-internal baselines** or a stuff decline reads as a sequencing fade (SQ-5 / SQ-5d).
3. **Render env (device VM):** kaleido 0.2.1 renders once per process and cannot draw `go.Heatmap` — restart the scope per figure; draw heatmaps as square markers (RN-1/RN-2).
4. **EN-3 recurs in harnesses:** `player_name == 'Nola, Aaron'` on batting rows returns 140 opposing pitcher ids.
5. K44 `nresults` walks exclude IBB (public BB includes them).
