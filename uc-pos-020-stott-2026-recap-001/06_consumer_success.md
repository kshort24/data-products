# 06 · Consumer Success
**consumer-onboarding-agent · analytics-enabler · product-narrator · query-builder**

## 1 · Forms and readers
| Form | Reader | Where |
|---|---|---|
| PDF report, 10 pp, 8 sections | front office, coaches | `dp_uc55_stott_2026_recap_report.pdf` (MLB root + this folder) |
| Dashboard, 7 chapters + appendix | analysts, the client | `dp_uc55_stott_2026_dashboard.html`; Artifact "Stott 2026 Recap" |
| ER-1 notebook cell | the client | `out/dp_uc55_er1_notebook_cell.md` |
| Receipts | reviewers | `out/dp_uc55_*` (82) |

**Why a hand-built page and not the Dashboard Artifact type:** the house recap form (UC48–UC54) is a governed HTML page built from receipts, with every figure claim-asserted and the harness checking its payload. The Artifact is that same page's body variant, so the published page and the certified page are one build.

## 2 · Reading paths
- **Five minutes:** the bottom line (§1), F1, F3, F6.
- **The client's questions in order:** §2 → §7.
- **"Should he play third?":** §7 + HP-12/13.
- **Coaching:** §5 (contact point) and "three things for 2027" (§8).

## 3 · Walkthrough (what the product says)
1. **2026 was his best season.**
   - .256/.334/.401, with a career-high wOBA (.325) and xwOBA (.330).
   - xwOBA rose in every season: .280 → .303 → .309 → .319 → .330.
2. **The good eras are mostly noise.**
   - ER-1 finds no wOBA change point in any season.
   - None of the client's three eras clears a hindsight-corrected test.
   - Early 2023 wasn't better by wOBA; it was a BABIP run.
3. **Same hitter in good and bad stretches** (the client's read holds). Summer 2026 is the exception: walks and xwOBA really moved, alongside a BABIP spike.
4. **The real change was mechanical.**
   - After the 2025 stance change his contact point moved out front: 25.7 → 29.3 → 31.8 in.
   - His swing turned toward the pull side.
   - 2026 brought a career-high pull share and a career-low oppo share.
5. **Not velocity, not one matchup.** Good eras were fastball eras against both hands.
6. **The level left is the zone.** 2026 was his worst chase and whiff season. August, his best month, came with his lowest chase.
7. **Defense.**
   - At 2B, IO-1 has him −9 after +12/+13/+19, agreeing with DRS and not with OAA.
   - At 3B the sample is too small and unstable to decide.
   - The thump worry holds: Arraez's ISO is .090.

## 4 · FAQ
- **Why doesn't ER-1 find his hot streaks?** With about 600 PA a season, per-PA wOBA is noisy. The test catches a .080 step half the time. The streaks you remember sit inside that noise.
- **Isn't "SAME HITTER" just because results were excluded?** Results define the eras. Scoring them would be circular, so the test asks whether *process* moved. Results are shown beside it.
- **Why trust IO-1 over OAA?** You shouldn't trust either alone. IO-1 is a proxy with no positioning data. It agrees with DRS and disagrees with OAA, and all three are shown.
- **Is attack direction pull-positive?** Not in this data plane. Raw values are pull-negative (O-15). Every chart flips the sign and says so.
- **Can I rerun this for another player?** Change `SUBJECT_ID`/`SUBJECT_NAME`/`SEASONS` in `dp_uc55_kernel.py` and rerun. The ER-1 notebook cell works on any batter frame today.

## 5 · Query templates (query-builder)
```python
import dp_uc55_kernel as K
ph = K.load_house(); pos = ph[ph.phillies_role == "batting"]
s = K.subject_rows(pos)                                   # id-locked, regular season
atoms = K.pa_atoms(s, K.woba_weights(), "woba")
eras, tests = K.er1_segments(atoms, atoms.num.sum() / atoms.den.sum())          # ER-1
bp = K.swing_path_profile(["game_year"], s[s.game_year >= 2025])                 # BP-1 (pull_direction = -attack_direction)
g = K.grounders(ph); sc, v, sector = K.io1_run(g, K.SUBJECT_ID, "2B")            # IO-1
K.io1_summary(sc)
```

## 6 · Catalog entry
**Stott 2026 Recap — "Another Level?"** · UC #55 · `uc-pos-020` · `dp_uc55` v1.0.0 · Phillies Offense · READY-CONDITIONAL · verified 185/185 · new provisional KPIs ER-1, GS-1, IO-1 · internal.
