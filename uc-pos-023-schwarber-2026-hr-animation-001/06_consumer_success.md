# 06 · Consumer Success
**consumer-onboarding-agent · analytics-enabler · query-builder**
`uc-pos-023-schwarber-2026-hr-animation-001` · UC #58 · `dp_uc58` v1.0.0

## 1 · Personas
| Persona | What they get | How to use it |
|---|---|---|
| **Claude Design** (first non-human consumer in the repo) | `dp_uc58_claude_design_prompt.md` + 8 keyframes | Paste the prompt; attach the keyframes. Everything it needs is in §0–§7: rules, tokens, transitions, scenes, segment/clip map, self-check, DATA |
| **The editor (Kellen)** | `out/dp_uc58_clip_list.csv`, the segment map (prompt §5) | `python resolve_play_ids.py out\dp_uc58_clip_list.csv` → `python download_clips.py out\dp_uc58_clip_list_resolved.csv`. Files are numbered in edit order (`01_…` = after seg03). Interleave: seg03, clip 1, seg04, clip 2, … per prompt §5; `Concat MP4s in Folder.ipynb` joins them |
| **Season-recap UC (parent)** | `hr_quality_by_season.csv`, `spray_by_season`, HP grades | The "lost pop" chapter starts from HP-01…05 and the pull share. The back question stays open (CI-2 has no onset date) |

## 2 · Reading the numbers (analytics-enabler)
- **"Shorter, softer, more pulled" is descriptive, not causal.** All three are true of the 45 homers, and none of them says why.
- **HB-1 vs barrel rate.** HB-1 = 91% means 41 of 45 homers were barrels. Barrel rate 15.5% means 57 of 367 balls in play were barrels. Different denominators, different questions.
- **WP-1** credits the batter. Positive is good for Schwarber at home and on the road.
- **Spray dots sit at the Statcast distance**, in the direction the ball was hit, on one outline. Where the CBP wall sits relative to a dot means nothing for road homers.

## 3 · Query templates (query-builder)
```python
import pandas as pd
reg = pd.read_csv("out/dp_uc58_hr_register_2026.csv")
reg[reg.tags.str.contains("max_ev|max_distance|max_wpa|walkoff", na=False)]        # the S3 stops
reg.sort_values("wpa", ascending=False).head(5)                                        # WP-1 ranking (not raw dHWE)
reg[(reg.p_throws == "L") & (reg.pitch_group == "Fastballs")].nlargest(5, "launch_speed")  # alternates for clip 7
```
```python
import json; d = json.load(open("out/dp_uc58_design_data.json", encoding="utf-8"))
d["s1_s3_curves"]["seasons"]["2026"]["hr_at_pa"]     # PA of each 2026 homer
```

## 4 · FAQ
- **Why 701 PA when 702 rows have an event?** One `truncated_pa` (house exclusion).
- **Why is clip 7 the same homer as clip 4?** HL-1 ranks it the second-hardest lefty-fastball homer. Swap in the next one (5/9 vs COL, 110.8 mph) if you prefer.
- **Can I add the Derby?** Not from this data. The house log holds no Derby swings.
