# 05 · Quality & Certification
**data-quality-engineer · certification-agent**

## Independent verification — **79 / 79 PASS**

`dp_uc35_verification.py` recomputes every published headline from the **raw parquet** with inline
logic (no kernel import for the arithmetic), then cross-checks receipts ↔ headlines ↔ figures.

| Block | Checks | What it proves |
|---|---|---|
| Raw load + dedup | 1–2 | frames load, S/E excluded, pitch key unique |
| Noles arithmetic | 3–10 | PA, pitches, BA, SLG, K%, runs_created, rc_per_pa recomputed independently; season-wOBA numerators reconcile against receipt counts (check 12) |
| Floor ruling | 11–13 | floor == min Noles season PA; headlines agree |
| Box population | 14–18 | floor respected; count matches; `rc_per_pa × PA = RC` and `ops = obp + slg` identities |
| Wheeler concat | 19–22 | sources disjoint; career PA = independent sum of both sources; seasons sum to career |
| Harper | 23–25 | vs-MIA PA; vs-Alcantara PA and pitches |
| Exposure ranks | 26–29 | Alcantara pitch count, rank #2, receipt agreement; Harper-vs-Alcantara rank #1 |
| DQ scorecard | 30 | no FAIL rows |
| Headlines ↔ career receipts | 31–79 | 10 KPIs × 5 entities within 5e-5 of receipt values |

## DQ scorecard (`out/dp_uc35_dq_scorecard.csv`)

| Check | Result | Value |
|---|---|---|
| Dedup (game_pk, at_bat_number, pitch_number) | PASS | 0 dups |
| Entity locks (Nola/Harper mode-of-name; Alcantara/Wheeler sole-id-in-cache) | PASS ×4 | 605400 / 547180 / 645261 / 554430 |
| Wheeler source overlap | PASS | 0 seasons |
| game_type population | PASS | S/E excluded, R + postseason retained |
| `launch_speed_angle` null rate, 2026 BIP | INFO | receipted (O-8 exposure scales with this) |
| `zone` null rate | INFO | receipted (O-2 disclosure) |
| `bat_score`/`post_bat_score` completeness | **PASS** | 0 nulls — runs_created precondition holds |

## Defect register disposition

| ID | Function | This UC |
|---|---|---|
| D1 whiff zero-numerator drop | `whiff_rate_fix` used | not triggered silently — fix variant |
| D2 hard-hit merge shape | `hard_hit_rate_fix` used | fix variant; **O-8 denominator disclosed, not changed** |
| D3 fpsr | not used | n/a |
| D4 nresults rounding | `nresults_unrounded` used | plus new standing-rule candidate from the dashboard card incident (see 04 build notes): *surfaces round once, from the receipt* |
| D5/O-7 pull_air_rate | not used | n/a |
| **New defects opened: 0.** New open item: **O-10** (pitcher name authority), which is a metadata gap, not a computational defect |

## Certification readiness

| Artifact | Present | Internally consistent |
|---|---|---|
| Lineage (04) | ✅ | ✅ column-level, KPI ← physical |
| DQ scorecard | ✅ | ✅ 0 FAIL |
| Glossary entries + deviation register (03) | ✅ | ✅ HD-1 ruling traced intake → derivation receipt → flags |
| Acceptance criteria vs capability table (00) | ✅ | ✅ RC-1..RC-7 all evidenced |
| Verification suite + result | ✅ | ✅ 79/79, separate code path |
| Report / PDF / dashboard | ✅ | ✅ all numbers trace to receipts; premise verdicts consistent across all three surfaces |
| Freshness manifest incl. manual carry-ins | ✅ | ✅ |

**CERTIFY-READY** for the internal scope defined in 00. Publish decision remains with the human DPO.
