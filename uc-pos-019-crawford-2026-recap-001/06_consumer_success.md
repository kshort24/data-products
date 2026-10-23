# 06 · Consumer Success
**consumer-onboarding-agent · analytics-enabler · query-builder · product-narrator**

## 1 · Product forms and readers
| Form | Reader | Use |
|---|---|---|
| `dp_uc54_crawford_2026_recap_report.pdf` (10 pp, 9 sections) | front office, player development | the decision read: six answers, caveats |
| `dp_uc54_crawford_2026_dashboard.html` / Artifact "Crawford 2026 Recap" | hitting and outfield coaches, analysts | explore the chases, spray and CF opportunities with hover |
| Player-facing excerpt (chapters 3–5) | Justin Crawford, via player development | his own approach and contact; nothing about deployment or cohorts (C3) |

## 2 · Reading paths
- **Five minutes:** Bottom line (report §1 / dashboard tiles) → F1 → F3.
- **Hitting coach:** §4 approach (F4, F5) → §6 walks (F7) → §7 righty spin (F8, F9).
- **Outfield coach:** §8 centre field (F10) with the CI-2/CI-3 carry-ins; read the sign, not the decimal.
- **Analyst:** `out/dp_uc54_headlines.json` → receipts → `03` §2 specs.

## 3 · Walkthrough: what to do with it
1. **Approach:** the chase is the lever, and it is specific. The targets are RHP breaking balls and changeups below the zone (47% and 44% chase) and elevated fastballs, the costliest by volume (14.4 CC-1 runs). Two-strike chases carry half the cost.
2. **Walks follow three-ball counts:** he reached one in 12.0% of PA (10th percentile). Fewer early chases are what move this number.
3. **Ground balls are a swing-plane question,** not exit velocity. The 1.7° attack angle (lowest of 31 tracked Phillies seasons) is the measurable to watch in 2027.
4. **Centre field:** the April read was the worst stretch (−6.3 XO-2; −3 OAA per CI-3).

## 4 · How to read TR-1 and CC-1
- **TR-1:** a signature is PRESENT only if it moved its pre-registered bar in the predicted direction (with p < .05 where a test applies). With 182 and 283 PA, WEAK means "moved, but not provably". NO TURN is the honest summary, not proof that nothing changed.
- **CC-1:** runs given up by swinging at an out-of-zone pitch instead of taking it, against the house take in that count. It is a price on the habit, not a projection of what the next pitch would have been.

## 5 · FAQ
- **Why isn't AAA in his rates?** Different level, different tracking (SRC-3). It appears only as a labelled comparison.
- **Why is his OBP .309 here and .305 in the notebook-style table?** K44's legacy OBP divides by PA (REC-2). .309 matches the published line.
- **Why does the notebook's defense read ±0 and this one −9.8?** The notebook only scores balls he fielded (DEF-3). XO-2 starts from every CF-sector air ball with him in centre.
- **Is −9.8 "outs above average"?** No. It is a ball-flight proxy against centre fielders in Phillies games since 2015. The −8 OAA (CI-2) is Statcast's number, shown beside it, never mixed in.

## 6 · Query templates (query-builder)
```python
import dp_uc54_kernel as K
ph = K.load_house(); pos = ph[(ph.phillies_role == "batting") & (ph.game_type == "R")]
s = K.subject_rows(ph[ph.phillies_role == "batting"])
ref = K.take_reference(pos[pos.game_year >= 2023])
K.chase_cost(["p_throws", "pitch_group"], s, ref)                    # CC-1 by hand x group
K.tr1_ledger(K.tr1_metrics(s[s.game_date < "2026-06-01"], K.woba_weights()),
             K.tr1_metrics(s[s.game_date >= "2026-06-01"], K.woba_weights()))   # TR-1
```

## 7 · Catalog entry
`uc-pos-019` · Justin Crawford 2026 season recap, "Exactly as Advertised" · Phillies Offense · v1.0.0 · READY-CONDITIONAL · verified 157/157 · forms: PDF, dashboard, Artifact · new objects TR-1, CC-1, XO-2 (provisional) · parent uc-pos-011.
