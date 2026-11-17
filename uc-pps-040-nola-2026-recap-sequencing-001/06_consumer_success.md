# 06 · Consumer Success
Agents: `analytics-enabler` · `consumer-onboarding-agent` · `query-builder`

## 1 · Persona guides
| Persona | Start with | What to take | What not to take |
|---|---|---|---|
| **Pitching coach** | Report §8, dashboard "Run prevention" | Finish with back-to-back curves; to lefties use changeup → curve, retire sinker endings; to righties open with the sinker, avoid changeup → four-seam | A single sequence's lift as a rule; the list is candidates (C2) |
| **Pitching analyst** | Dashboard "Sequence explorer"; `out/dp_uc64_seq_career.csv` | SQ-2 isolates the setup from pitch quality and count; read the interval, not the point | Raw RV of a sequence (that ranks pitches, not order) |
| **Catchers** | Report §10, F9 | One book to righties; with Stubbs, fewer stacked four-seams to lefties | Who called it (G4: unknowable) |
| **Front office** | Bottom line, F1, F2 | 2026 better than the line (xwOBA 27th pct vs wOBA 5th); the problem is fastball quality, not predictability or order | 2026-only sequence ranks (no righty pair clears) |

## 2 · How to read setup lift (worked example)
Sinker → changeup vs RHB, career: the changeup after a sinker saved **+3.0 runs per 100** in raw terms; Nola's changeups to righties *in the same
counts* save less on average, and the difference is **+3.2 runs per 100** (90% interval +1.4 to +5.0, n 304). That difference is the setup's credit.
Shrunk for sample size (n/(n+100)): +2.4.

## 3 · Query patterns (`query-builder`) — run from the MLB root
```python
import pandas as pd
s = pd.read_csv("out/dp_uc64_seq_career.csv")
# best setups to lefties, any length, enough sample, interval clears zero
s[(s.stand=="L") & (s.n>=50) & (s.lift_lo90>0)].sort_values("lift_rv100_shrunk", ascending=False)
# how a specific sequence did by era
pd.read_csv("out/dp_uc64_seq_by_era.csv").query("stand=='R' and seq=='KC-KC'")
# best ways to finish righties
pd.read_csv("out/dp_uc64_endings_career.csv").query("stand=='R' and n_pa>=50").sort_values("xwoba_shrunk").head(10)
# recompute lift for a new subset (e.g. a 2027 window) with the governed kernel
import dp_uc64_kernel as K
ph = K.load_frame(); d = K.harmonize(K.subject_frame(ph).query("game_type=='R'")); d = pd.concat([d, K.outcome_cols(d)], axis=1)
w = K.add_lift(K.windows(d, 2), K.baselines(d)); K.seq_table(w, ["stand", "seq"], min_n=50)
```

## 4 · FAQ
- **Why not rank full pitch strings from `pitch_sequence()`?** 2026 had 502 distinct strings over 746 PA. The function is used verbatim to label PAs and for the short-PA table (`fullseq_short`); ranking needs windows.
- **Why do the most-used pairs have ~0 lift?** They *are* most of the baseline. Their value shows up in endings, not in surprise.
- **Does a negative lift mean "never throw it"?** No. It means the follow-up pitch did worse than usual for that count after that setup. Location and hitter are not controlled.
- **Why career-wide?** DPO ruling Q-C. Era-specific reads are in §9 / `seq_by_era` on era-internal baselines.
