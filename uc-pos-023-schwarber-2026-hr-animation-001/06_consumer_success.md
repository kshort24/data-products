# 06 | Consumer Success

**consumer-onboarding-agent | analytics-enabler | query-builder**
`uc-pos-023-schwarber-2026-hr-animation-001` | UC #58 | `dp\_uc58` v1.0.0

## 1 | Personas

|Persona|What they get|How to use it|
|-|-|-|
|**Claude Design** (first non-human consumer in the repo)|`dp\_uc58\_claude\_design\_prompt.md` (v1.0.1) + 8 keyframes + `out/dp\_uc58\_copy\_deck.json`|Paste the prompt; attach the keyframes. Everything it needs is in §0–§7: rules, tokens, transitions, scenes, segment/clip map, self-check, DATA|
|**The editor (Kellen)**|`out/dp\_uc58\_clip\_list.csv`, the segment map (prompt §5)|`python resolve\_play\_ids.py out\\dp\_uc58\_clip\_list.csv` → `python download\_clips.py out\\dp\_uc58\_clip\_list\_resolved.csv`. Files are numbered in edit order (`01\_…` = after seg03). Interleave: seg03, clip 1, seg04, clip 2, … per prompt §5; `Concat MP4s in Folder.ipynb` joins them|
|**Season-recap UC (parent)**|`hr\_quality\_by\_season.csv`, `spray\_by\_season`, HP grades|The "lost pop" chapter starts from HP-01…05 and the pull share. The back question stays open (CI-2 has no onset date)|

## 2 | Reading the Numbers (analytics-enabler)

* **"Shorter, softer, more pulled" is descriptive, not causal.** All three are true of the 45 homers, and none of them says why.
* **HB-1 vs barrel rate.** HB-1 = 91% means 41 of 45 homers were barrels. Barrel rate 15.5% means 57 of 367 balls in play were barrels. Different denominators, different questions.
* **WP-1** credits the batter. Positive is good for Schwarber at home and on the road.
* **Spray dots sit at the Statcast distance**, in the direction the ball was hit, on one outline. Where the CBP wall sits relative to a dot means nothing for road homers.

## 3 | Query Templates (query-builder)

```python
import pandas as pd
reg = pd.read\_csv("out/dp\_uc58\_hr\_register\_2026.csv")
reg\[reg.tags.str.contains("max\_ev|max\_distance|max\_wpa|walkoff", na=False)]        # the S3 stops
reg.sort\_values("wpa", ascending=False).head(5)                                        # WP-1 ranking (not raw dHWE)
reg\[(reg.p\_throws == "L") \& (reg.pitch\_group == "Fastballs")].nlargest(5, "launch\_speed")  # alternates for clip 7
```

```python
import json; d = json.load(open("out/dp\_uc58\_design\_data.json", encoding="utf-8"))
d\["s1\_s3\_curves"]\["seasons"]\["2026"]\["hr\_at\_pa"]     # PA of each 2026 homer
```

## 4 | FAQ

* **Why 701 PA when 702 rows have an event?** One `truncated\_pa` (house exclusion).
* **Why is clip 7 the same homer as clip 4?** HL-1 ranks it the second-hardest lefty-fastball homer. Swap in the next one (5/9 vs COL, 110.8 mph) if you prefer.
* **Can I add the Derby?** Not from this data. The house log holds no Derby swings.

## 5 | v1.0.1 Note

The approved video was rendered from the v1.0.0 prompt. If the DPO wants the on-screen copy to match ST-1, re-render only the title and subtitle layers from `copy\_deck.json`; no data, timing or clip changes are needed.
