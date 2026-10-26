# 06 · Consumer Success
**consumer-onboarding-agent · analytics-enabler · query-builder**
`uc-pos-022-turner-2026-recap-001` · UC #57 · `dp_uc57` v1.0.0

## 1 · Personas
| Persona | Start here | The one thing to take away |
|---|---|---|
| Hitting coach | Dashboard ch. 2 (decision map) and ch. 5 (swing path) | He took in-zone fastballs; the plane flattened on everything. Breaking-ball recognition did not get worse |
| Front office | Bottom line + ch. 6 | Worst year of his career, the process decline is against righties, and a position move is not supported or refuted by his bat |
| Analyst | `out/dp_uc57_ct1_calls.csv`, `pr1_gaps.csv`, `hp_grades.csv` | Every cell carries its n and its pre-registered call |
| Client (DPO) | "Your notebook, graded" | 2 SUPPORTED, 8 PARTLY, 1 PLAUSIBLE, 1 NOT TESTABLE |

## 2 · Reading the calls
CHANGED = |z| ≥ 1.96 · LEANS = 1.00-1.96 · SAME < 1.00 · TOO FEW TO CALL = under 30 BIP or 50 in the rate's denominator. xwOBA on contact is shown with n and never called.

## 3 · Query patterns (notebook)
```python
import sys; sys.path.insert(0, r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB")
import dp_uc57_kernel as K
s = pos[(pos.batter == K.SUBJECT_ID) & (pos.game_type == "R")]
s = s.assign(period=np.where(s.game_year == 2026, "2026", "2023-25"))
cells = K.cell_panel(["period", "p_throws", "pitch_group"], s)          # the client panel on governed functions
ci = cells.set_index(["period", "p_throws", "pitch_group"])
K.ct1("ooz_contact_rate", ci.loc[("2023-25", "R", "breaking")], ci.loc[("2026", "R", "breaking")])
K.pr1_gap_test(ci.loc[("2023-25", "R", "fastball")], ci.loc[("2026", "R", "fastball")], "swing")
```

## 4 · FAQ
- *Why not compare to 2025 alone, like the notebook?* One season is a noisy baseline: 2025 was his lowest whiff year against lefty offspeed (21.9%), so a 2025-only comparison overstates the 2026 jump.
- *Why is HP-05 PARTLY when popups and flatness both rose?* The pre-registered rule needed popups to be flatter than his other contact. They weren't, because everything got flatter.
- *Where is the 3D swing?* Tier B. It ships after the Single-Swing Pilot's Gate 2 closes and PL-1 is fixed.
