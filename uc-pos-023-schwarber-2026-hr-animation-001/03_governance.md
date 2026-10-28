# 03 | Governance

**business-glossary-agent | metadata-mapper | data-dictionary | data-tagger | domain-steward-proxy**
`uc-pos-023-schwarber-2026-hr-animation-001` | UC #58 | `dp\_uc58` v1.0.0

## 0 | Inheritance Policy (Rule-1 searches run at T0)

|Searched for|Found|Decision|
|-|-|-|
|cumulative-by-PA engine|`cumulative\_metric.py` (Harper BB%, Marsh XBH, Alvarado)|**inherit by import, sha-pinned**|
|WPA sign|`dp\_uc51` pitching WPA (+dHWE home / −dHWE away)|mirror as WP-1|
|hc → feet, direction|K40 `derive\_loc` (PA-L1), `hit\_direction` (cell 24)|inherit|
|park outline|K54 `CBP\_DIMS` (cbp-spray SoT)|inherit|
|pitch group|K57 `client\_pitch\_group` (CPG-1)|inherit (the client's own map)|
|ball diameter|none in repo|define PM-1 (2.9 in)|
|HR barrel share|none (only per-BIP `barrel\_rate\_g`)|define HB-1, distinct name (alias rule)|
|prior Schwarber UCs|UC21, UC33|entity lock, NULL standard|

Pins: `dp\_uc57\_kernel.py` `601e958a…`, `cumulative\_metric.py` `a2888740…`, plus 17 through K57. **18 unique files, all PASS** (V01).

## 1 | Glossary Additions (provisional, DPO to ratify)

* **HB-1 HR barrel share**: barrels / HR. Its display label is "HR that were barrels", never "barrel rate".
* **WP-1 batter WPA**.
* **CP-1 cumulative HR by PA**.
* **HL-1 highlight rules**.
* **SP-1 / SP-2 / SP-3 spray placement**.
* **PM-1 pitch-map drawing rule**.
* **GR-1 grade bars**.
* **DH-1 game order**: a defect fix, proposed for the house (§3).
* **ST-1 copy style** (v1.0.1, from the DPO's K1 markup): Title Case titles; context-only subtitles; no method notes on screen.
* **COPY-1 copy deck** (v1.0.1): one JSON of on-screen copy, consumed by the keyframes and the prompt.

**Ratification (v1.0.1):** the DPO's approval of `00`–`07` (2026-10-27 22:53 ET) is read as ratifying the provisional rules above **for this product**. House-wide promotion is a separate decision (Release Sign-Off §5).

## 2 | Data Dictionary: published receipts (`out/dp\_uc58\_\*`)

|File|Grain|Key columns|
|-|-|-|
|`cum\_hr\_by\_pa.csv`|PA × season|game\_year, cum\_pa, cum\_num (HR), era|
|`season\_table.csv`|season|game\_year, team, pa, hr, pa\_per\_hr, hr\_rank (min-rank ties)|
|`hr\_quality\_by\_season.csv`|season|total\_hrs, max\_ev, mu\_ev, max\_dist, mu\_dist, barrels, hr\_barrel\_share (HB-1), bips, bip\_barrels, barrel\_rate, bip\_mu\_ev|
|`hand\_group\_by\_season.csv` / `rhp\_fastball\_by\_type.csv`|season × hand × group / type|HB-1 panel + call ("too few to call (EV)" under 5 HR)|
|`hr\_register\_2026.csv` / `hr\_non\_regular\_2026.csv`|HR|PITCH\_KEY, season\_hr\_no, cum\_pa, wpa (WP-1), walkoff, result, go\_ahead, tags (HL-1), pitcher\_name + source|
|`spray\_2026.csv`, `cbp\_outline.csv`|HR / bearing|bearing\_deg, x\_ft, y\_ft, approx (SP-2), field (DR-1)|
|`pitchmap\_2026.csv`|HR|plate\_x, plate\_z, pitch\_group (CPG-1), in\_drawn\_zone|
|`clip\_list.csv`|clip|game\_pk, inning, inning\_topbot, at\_bat\_number, pitch\_number (the `resolve\_play\_ids.py` keys) + scene, beat, label|
|`design\_data.json`, `brand\_tokens.json`, `keyframes\_manifest.json`, `headlines.json`|—|the prompt's DATA block; tokens; keyframe names; every headline at 6 dp|
|`hp\_grades.csv`, `dq\_scorecard.csv`, `cp1\_client\_vs\_governed\_axis.csv`, `verification.csv`|—|grades, DQ, CP-1 evidence, harness|

**Tagging (data-tagger):** public-figure performance data; domain = Phillies Offense (`pos`); sensitivity = internal (publish decision is the DPO's). No PII.

## 3 | Findings for the house (domain-steward-proxy)

1. **DH-1 (new, house-wide):** `cumulative\_metric.cumulative\_frame` sorts by (game\_date, game\_pk, at\_bat\_number), but game\_pk order is not game order on doubleheader days. On 2026-04-30, 823472 was Game 1 (MLB.com: 350th career HR off Logan Webb). Every house cumulative chart puts a DH day's PAs in the wrong order when game\_pk runs backwards. Totals are unaffected; steps move by up to one game's PAs. `sv\_id`, the natural fix, is null in 2017–26. **Proposed:** `cumulative\_metric` v1.1 accepts an `order=` column. This UC wraps it without editing the pinned file.
2. **PA-X1 (recurrence of UC57 SRC-PA):** `cumulative\_metric`'s default `pa\_exclude` drops only `truncated\_pa`. Callers that don't pass the house `NON\_PA` list count baserunning-out rows as PA (Schwarber 2021: 473 vs 470). Recommend making `NON\_PA` the default in v1.1.
3. **NA-1 (recurrence):** `(s == 6).mean()` on a nullable column drops NA rows from the denominator. The house `barrel\_rate\_g` is right (barrels / all BIP). The harness first got it wrong and fixed its own check (`05` §2).
4. **WP-1:** raw `delta\_home\_win\_exp` is home-team perspective. Any "biggest swing" ranking on it buries road heroics (6/28 at NYM ranks 45th of 45).

