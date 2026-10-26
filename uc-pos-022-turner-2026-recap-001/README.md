# uc-pos-022 · Trea Turner 2026 season recap: "Sounding the Alarm"
**UC #57 · build `dp_uc57` v1.0.0 · Phillies Offense (`pos`) · Human DPO: Kellen Short · Delivered 2026-10-23 · READY-CONDITIONAL (C1-C6) · harness 34/34 · DQ 10/3/0**

## The answer in five lines
1. Atrocious by his own standard: wOBA .298 / xwOBA .293 / OPS .675, last of his 10 full seasons on all three. Against the house pool: 40th percentile.
2. Not a breaking-ball recognition problem. Against righty breaking balls his chase and contact were unchanged; he has never touched them off the plate (7th percentile).
3. The recognition break is on fastballs: he took strikes. In-zone swing 73.9% → 68.9% (z −3.4), led by fastballs from both hands.
4. The real decline is against righties (xwOBA .318 → .277). Against lefties the results fell but the expected line barely moved.
5. Popups (5.0% → 8.0%) and a flatter swing (tilt net −1.4°, flattest of 12 Phillies) are both real, but breaking-ball popups were not flatter than his other contact (PP-1 PARTLY). Position change: not testable.

## Deliverables
| What | Where |
|---|---|
| Report (7 pp) | `MLB/dp_uc57_turner_2026_recap_report.pdf` (+ `.md`); copy here |
| Dashboard | `MLB/dp_uc57_turner_2026_dashboard.html` (+ `_artifact.html`); copy here; Artifact "Sounding the Alarm" |
| Code | `MLB/dp_uc57_kernel.py`, `_turner_recap.py`, `_hp.py`, `_build_figs.py`, `_narrative.py`, `_build_report.py`, `_build_pdf.py`, `_build_dashboard.py`, `_verification.py` |
| Receipts | `MLB/out/dp_uc57_*` (63 files) · `MLB/eda/dp_uc57/` |
| Trail | this folder: BID, `00`-`07`, README, contract and ledger patch copies |

## Re-run
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc57_turner_recap.py && python dp_uc57_hp.py && python dp_uc57_build_figs.py && python dp_uc57_build_report.py && python dp_uc57_build_pdf.py && python dp_uc57_build_dashboard.py && python dp_uc57_verification.py
```
Deterministic; ~31 s. The anchor guard refuses to run if the house log passes 2026-10-01.

## Open items for the DPO
1. **G2** was taken as the 2026-10-22 bat-tracking CDE read (BID default). Say so if "last night's conversation" meant something else.
2. **Tier B** (reconstructed 3D swing) waits on the pilot's Gate 2 and the PL-1 fix (house-log intercepts; O-15 on `attack_direction`).
3. **Ledger:** paste UC52-UC56 patches first, then UC57.
