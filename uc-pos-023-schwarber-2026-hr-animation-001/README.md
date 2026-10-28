# uc-pos-023 · Kyle Schwarber 2026 home runs, animated: "Forty-Five and a Question Mark"
**UC #58 · build `dp_uc58` v1.0.0 · Phillies Offense (`pos`) · Human DPO: Kellen Short · Delivered 2026-10-27 · READY-CONDITIONAL (C1-C7) · harness 28/28 · DQ 10/3/0**

## The answer in five lines
1. 45 regular-season HR, tied for the MLB lead, 4th-most of his 12 seasons (56 / 47 / 46 / **45**).
2. They were the softest and shortest of his Phillies years: max EV 113.0, average 106.3 mph and 402 ft. 91% were barrels (2nd-lowest), and his barrel rate fell to 15.5% of BIP (lowest).
3. 82% were pulled, the most of any Phillies season (54–74%).
4. 30 off righties, the softest fastball homers of his tenure (105.9 mph average). 13 of 15 off lefties came on fastballs, with only 2 on breaking balls (7 in 2025).
5. The client's Python is fit as a data engine after six fixes. The worst: its x-axis counted pitches (3,026), not PA (701).

## Deliverables
| What | Where |
|---|---|
| **Claude Design prompt** (rules, tokens, transitions, 8 scenes, 16-segment / 15-clip map, self-check, DATA) | `MLB/dp_uc58_claude_design_prompt.md`; copy here |
| **Reference keyframes** S1–S8 (1920×1080) | `MLB/out/dp_uc58_k*.png`; copies in `keyframes/` |
| **Technical feasibility brief** | `MLB/dp_uc58_technical_feasibility_brief.md`; copy here |
| **Clip list** (`resolve_play_ids.py` schema, edit order) | `MLB/out/dp_uc58_clip_list.csv`; copy in `data/` |
| Data package | `MLB/out/dp_uc58_*` (27 files) · `MLB/eda/dp_uc58/`; design data, grades, DQ, harness copies in `data/` |
| Code | `MLB/dp_uc58_kernel.py`, `_build.py`, `_build_keyframes.py`, `_build_prompt.py`, `_verification.py` |
| Trail | BID, `00`–`07`, contract and ledger-patch copies (this folder) |

## Re-run
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc58_build.py && python dp_uc58_build_keyframes.py && python dp_uc58_build_prompt.py && python dp_uc58_verification.py
python resolve_play_ids.py out\dp_uc58_clip_list.csv && python download_clips.py out\dp_uc58_clip_list_resolved.csv
```

## Open items for the DPO
G1 clip direction · clip 7 duplicate · `cumulative_metric` v1.1 (DH-1, PA-X1) · ratify the provisional rules · ledger paste UC52–UC58 · delete `MLB/out/_to_delete/`.
