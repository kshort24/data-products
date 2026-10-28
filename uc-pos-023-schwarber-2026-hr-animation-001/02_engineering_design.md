# 02 | Engineering Design

**data-architect | kpi-calculator | eda-agent | join-validator | dq-rule-definer | dashboard-specifier (motion spec)**
`uc-pos-023-schwarber-2026-hr-animation-001` | UC #58 | `dp\_uc58` v1.0.0

## 1 | Model (data-architect)

|Frame|Grain|Source|Key|Notes|
|-|-|-|-|-|
|`ALL`|pitch|house log 2022–26 (Phillies batting) ∪ `opponents/schwarber.parquet` 2015–21|`PITCH\_KEY` (game\_pk, at\_bat\_number, pitch\_number)|MLBAM 656941 lock on both sources; 0 duplicates across the union (EN-2 assert); era, team, CPG-1 `pitch\_group`, WP-1 `wpa`, DH-1 `game\_seq` derived|
|`REG`|pitch|`ALL` where `game\_type == 'R'`|`PITCH\_KEY`|every published number|
|PA rows|PA|`REG` with `events` not null, minus `NON\_PA` runner events and `truncated\_pa` (PA-X1)|(game\_seq, at\_bat\_number)|2026: 701 PA (702 event rows, 1 truncated)|
|`cum\_hr\_by\_pa`|PA × season|`cumulative\_metric.cumulative\_frame(\|, 'hr')`|(game\_year, cum\_pa)|DH-1 wrapper passes `game\_seq` in the game\_pk slot; `reconcile=` vs an independent HR count|
|HR register|HR|`REG` events == home\_run|`PITCH\_KEY`|45 rows 2026 + 2 non-regular (spring, WC) in their own file|
|Design data|scene|receipts only|—|`out/dp\_uc58\_design\_data.json`, embedded in the prompt|

**Join validation (join-validator):** one union, no joins on the pitch frame. The two merges (HR register ↔ PA positions on (game\_pk, at\_bat\_number); game results on game\_pk from all PHI rows of the game) are 1:1, asserted by `assert h26.cum\_pa.tolist() == curves\[2026]\['hr\_at\_pa']`.

## 2 | KPI and Rule Specs (kpi-calculator), as pre-registered in the BID

|ID|Spec|Status|
|-|-|-|
|CP-1|x = PA within season (PA-X1 exclusions), y = running HR; regular season; `PITCH\_KEY` de-dup; endpoint reconcile|rule, provisional|
|HB-1|HR barrel share = HRs with `launch\_speed\_angle == 6` / HRs|**NEW KPI, provisional**|
|WP-1|batter WPA = dHWE if bottom half else −dHWE|rule, provisional|
|HL-1|max EV (tie → longer) \| max distance \| max WP-1 \| walk-off (Bot, inning ≥ 9, `post\_bat\_score > fld\_score`) \| max HR per game \| RHP FF top-3 EV \| LHP fastball top-2 EV \| all LHP breaking \| client pick (Labor Day) labelled as such|rule, provisional|
|SP-1/2/3|bearing from DR-1 loc, radius = `hit\_distance\_sc`; `des`-sector fallback (LF −36, LCF −18, CF 0, RCF +18, RF +36), hollow; one CBP outline for every park|rules, provisional|
|PM-1|catcher's view, zone half-width 0.83 ft, 2026 mean `sz\_top/sz\_bot`, ball 2.9 in|drawing rule|
|GR-1|exact rank among 2022–26 at the client's displayed precision; ≥ 5 HR for EV cells|grade rule|
|DR-1 direction|house cell-24 ±4.7 slopes (`K40.hit\_direction`) on the SP-1 plotted point, stand L|consumed|
|DH-1|game order: sv\_id → `des` HR counter on all-HR DH days → game\_pk fallback|**defect fix found at T1** (03 §3)|

## 3 | Exploratory Data Analysis (eda-agent)

`eda/dp\_uc58/schwarber\_all\_types\_2015\_26.md` (27,135 rows × 96; written by `phillies\_dp.eda.to\_file`, never printed). Notables: bat-tracking fields \~90% null (2025–26 only; unused); `sv\_id` populated only in 2015–16 (drives DH-1); 2 null `hc\_x/hc\_y` on 2026 HRs.

## 4 | Visual and Motion Spec (dashboard-specifier)

* **Form:** step lines (counts over PA); ranked table; spray on a drawn field; true-scale pitch maps; 3-panel composite.
* **Palette** (dataviz validator, dark surface `#0B1426`):

  * hand `#4E8FD0` / `#C2820E`: **ALL CHECKS PASS**;
  * pitch group `#E81828` / `#8F74E0` / `#1A9486` (`--pairs all`): **ALL CHECKS PASS**;
  * rejected: amber `#C2820E` next to red (deutan ΔE 5.7, FAIL); light amber/teal (lightness band FAIL);
  * era grays `#5B6472` / `#9AA3AF` are muted context by design (they fail chroma on purpose, the house cumulative-chart pattern) and are always direct-labelled.
* **Segments:** 16 segments, with transition grammar T1–T4 (prompt §3).
* **Keyframes:** 8 PNGs at 1920×1080, rendered and eyeballed. Defects found and fixed in QA: legend over dots (K5), footer over axis title (K6), zero-lines on the composite maps (K8), and a hard-coded 105.9 in the K7 subtitle (now templated).
* No hover layer: these are video frames, not an interactive page.
* **v1.0.1 (DPO edit):**
  * **ST-1:** titles in Title Case (Chicago small-word rule, `tc()` in `dp\_uc58\_build\_keyframes.py`); subtitles are context only; mark meanings move to legends.
  * **COPY-1:** all on-screen titles and subtitles live in `out/dp\_uc58\_copy\_deck.json`, which both the keyframes and the prompt read.

