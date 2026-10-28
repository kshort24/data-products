# 04 | Engineering Build

**technical-lineage-builder | data-engineer**
`uc-pos-023-schwarber-2026-hr-animation-001` | UC #58 | `dp\_uc58` v1.0.0 | built 2026-10-27 19:52–20:04 ET

## 1 | Code (MLB root)

|File|sha256 (16)|Role|
|-|-|-|
|`dp\_uc58\_kernel.py`|`d262136169db4bb1`|Governed kernel: inheritance by import (K57 chain + `cumulative\_metric`), `load\_career`, DH-1 `game\_seq`, WP-1, CP-1 `cum\_hr`, `client\_frame\_cum` (client's cell verbatim), HB-1 `hr\_quality`, SP-1/2 `spray`, `direction`, `wall\_outline`, `walkoff`, GR-1|
|`dp\_uc58\_build.py`|`23e2c5010e4b0d43`|T1: all receipts, HP-01..HP-15, clip list, design data, DQ|
|`dp\_uc58\_build\_keyframes.py`|`ba2bf477eae9343f`|T2: 8 PNG keyframes from receipts only; `brand\_tokens.json`|
|`dp\_uc58\_build\_prompt.py`|`edca3b2abe6398b2`|T3: the Claude Design prompt, every number templated from receipts|
|`dp\_uc58\_verification.py`|`44146123ceda9ffe`|T4: independent harness (raw parquet, plain pandas)|
|`dp\_uc58\_technical\_feasibility\_brief.md`|—|T3: cell-by-cell assessment of the client's Python|

## 2 | Lineage (technical-lineage-builder): source → screen

|On screen|Receipt|Transformation|Source columns|
|-|-|-|-|
|S1–S3 step lines|`cum\_hr\_by\_pa.csv` → `design\_data.s1\_s3\_curves`|PA rows (PA-X1) → DH-1 order → running HR (CP-1)|events, game\_type, game\_date, game\_pk, at\_bat\_number, pitch\_number, sv\_id, des|
|S3 stop captions|`hr\_register\_2026.csv`|HL-1 tags; WP-1; result from all rows of the game|launch\_speed, hit\_distance\_sc, inning, inning\_topbot, delta\_home\_win\_exp, bat/fld/post scores, pitcher (+ CI-3 names)|
|S4 table|`season\_table.csv`|count by season; min-rank|events, team (inning\_topbot → home/away)|
|S5 dots|`spray\_2026.csv`|DR-1 loc → bearing; radius = distance; SP-2 fallback|hc\_x, hc\_y, hit\_distance\_sc, des|
|S5 thump cards|`hr\_quality\_by\_season.csv`, `headlines.spray\_by\_season`|client agg + HB-1 + house barrel rate; DR-1 direction|launch\_speed, hit\_distance\_sc, launch\_speed\_angle, type|
|S6–S7 balls|`pitchmap\_2026.csv`|CPG-1 group; PM-1 zone|plate\_x, plate\_z, pitch\_type, p\_throws, sz\_top, sz\_bot|
|Clip cuts|`clip\_list.csv`|HL-1 rows in scene order, `resolve\_play\_ids.py` schema|game\_pk, inning, inning\_topbot, at\_bat\_number, pitch\_number|

## 3 | Run

```
cd "C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB"
python dp\_uc58\_build.py \&\& python dp\_uc58\_build\_keyframes.py \&\& python dp\_uc58\_build\_prompt.py \&\& python dp\_uc58\_verification.py
```

Deterministic; ≈ 25 s (build 5 s, keyframes ≈ 15 s). The anchor guard refuses to run if the house log passes 2026-10-01.

## 4 | Build Log (defects found and fixed in this run)

|#|Found by|Defect|Fix|
|-|-|-|-|
|B-1|carry-in reconcile (MLB.com Game 1 = 350th HR) + DQ-13 (`des` counter)|**DH-1:** 4/30 games in game\_pk order put HR #10/#11 in the wrong order|`game\_seq()` (sv\_id → des counter → game\_pk)|
|B-2|harness V03|PA counted runner-out rows (2021 473 vs 470)|PA-X1: house `NON\_PA` passed to `cumulative\_metric`|
|B-3|build|`barrels` column collision on the barrel-rate merge|renamed `bip\_barrels`|
|B-4|build|`load\_phils\_cols` appends `phillies\_role` (duplicate column) and needs `game\_year`|column list fixed|
|B-5|device|deletes not permitted in connected folders (stray partial grades file)|moved to `out/\_to\_delete/` for the DPO|
|B-6|render QA|K5 legend over dots; K6 footer over axis title; K8 zero-lines; K7 hard-coded number|fixed; K7 templated|
|B-7|ENV-3|device `/sessions` at 100%; no pyarrow|render stack in `/tmp/pyrender`, `TMPDIR=/tmp/piptmp`|

## 5 | Client Frame (CP-1 evidence)

`cp1\_client\_vs\_governed\_axis.csv`: the client's cell on the same regular-season rows ends 2026 at **3,026** vs **701** PA (stretch 4.32×; range 4.15–5.6× across seasons). Its HR totals agree with the governed curve every season; only the x-axis is wrong.

## 6 | v1.0.1 Build (2026-10-27 23:00–23:20 ET)

|File|sha256 (16)|Change|
|-|-|-|
|`dp\_uc58\_build\_keyframes.py`|`65b53a0c5b536239`|ST-1 `tc()`; COPY-1 deck written to `out/dp\_uc58\_copy\_deck.json`; K6/K7 legends carry mark meanings|
|`dp\_uc58\_build\_prompt.py`|`1450c7fce5aea147`|reads the copy deck; rule 9 (ST-1); S3 title; S6/S7 stat chips; S4 badge de-duplicated|
|`dp\_uc58\_verification.py`|`a380c76b4f64aaf9`|V23 strings Title Case; +V29/V30/V31|
|`dp\_uc58\_kernel.py`, `dp\_uc58\_build.py`|unchanged|`d262136169db4bb1`, `23e2c5010e4b0d43`|

Environment: the render stack was re-installed to `/tmp/pyrender` (new session VM; ENV-3). Re-run as §3. The design data is byte-identical to v1.0.0.
