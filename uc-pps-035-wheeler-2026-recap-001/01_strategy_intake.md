# 01 · Strategy & Intake: `uc-pps-035`

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`

## 1 · Ledger and ID reservation

- Ground truth for numbering: `uc_ledger_AI_PATCH_uc-pos-018-lineup-vs-sale.md` → **next UC #51, pps next `uc-pps-035`**. `uc_ledger_AI.md` still reads "next #25" (E-6 carried).
- Collision check 2026-10-12 13:05 ET: `dp_uc51*` none (MLB root, `out/`, control plane); `uc-pps-035*` referenced only as "next" in the uc-pps-034 and uc-pos-018 patches.
- Prior art for this subject: `uc-pps-020` (first half, UC #24, `dp_uc23`), `uc-pps-wheeler-scouting-001` and `dp_uc7_wheeler_mets` (pre-ledger scouting), `uc-pps-032` (elite RHP four-seam archetype: Wheeler's velocity trend), the `wheeler-scouting-report` skill. **Inherited:** uc-pps-020's six first-half figures (reproduced 6/6). **Cited, not rebuilt:** uc-pps-032's velocity finding.

## 2 · Use-case validation (gap report)

| # | Gap | Class | Resolution |
|---|---|---|---|
| V-1 | "Still Zack Wheeler" has no population or metric | Blocking | CX-1b starter-workload board (UC49) on XW-1 xwOBA and K-BB; rank printed with n |
| V-2 | "Signs of slowing down in the second half" has no window or metric | Blocking | Halves (UC49 break) + SR-2 slide window (by reconciliation) + velocity by month/season |
| V-3 | "Struggles in August" vs the reported "six starts after the break" | Non-blocking | SR-2: the unique 6-start window matching 8.51 is 7/27–8/24, not calendar August |
| V-4 | "Edge rate 42.4% per Statcast" — Savant's definition is not in the data | Non-blocking | ER-1 (UC8) published under its own name; 42.4% carried in; HP-06 |
| V-5 | "Jam rate" renamed "tied-up rate"; Savant's centered/flail need boundaries | Non-blocking | JR-1 inherited; ST-1 provisional with the client's 41 in line (E-7) |
| V-6 | The client's cell-22 frame mixes AAA rehab rows and postseason rows into 2026 | Non-blocking | CF-2b (MI-1); HP-10/11/14 |
| V-7 | ERA and IP are quoted in reporting but not computable from Statcast | Non-blocking | Carry-ins; OU-2 outs reconcile to 162.0 IP |
| V-8 | "One more year left on his deal" invites a contract-value read | Non-blocking | Not graded (no salary/WAR source, P8); the 2027 card answers the performance half |

## 3 · Source profiling

| Source | Rows for 554430 | Notes |
|---|---|---|
| `data/phillies/phils_2020…2026.parquet` (pitching role) | 17,973 R (2020–26); 1,065 postseason (2022–24, 2026) | Anchor 2026-09-27 (Game 162); WC G3 10/1 present |
| `phils_2017…2019` (batting role: he pitched against the Phillies) | 987 R | Context only |
| `data/opponents/wheeler.parquet` (pitcher-keyed) | 7,604 R, 2017–19 | 2013–14 not cached; 2015–16 missed (Tommy John) |
| `data/opponents/lhvp26.parquet` (pitcher-keyed, **Lehigh Valley**) | **148, tagged `R`** | Rehab starts 3/28, 4/3, 4/8 — **MI-1**, excluded |
| 22 other opponent files (batter-keyed) | 1,032 | `player_name` = the batter; duplicates of PHI or FILE rows |

**MI-1 (loader exposure).** CF-2 (UC49) admits every opponent file that holds the pitcher's id. A pitcher-keyed AAA file passes that test and its rows are tagged `game_type == 'R'`. For Luzardo there were none; for Wheeler, 148 rehab pitches would have entered his 2026 rates (CF-2 frame: 2,797 rows for 2026 vs 2,649 governed). CF-2b keeps only games where both clubs appear in a Phillies regular-season game (a data-derived MLB club list).

**NM-1 (loader defect).** CF-2 sets `df['player_name'] = SUBJECT_NAME` from its own module constant, so every frame it builds for any pitcher is labelled "Luzardo, Jesús". Display only, but it breaks any downstream name filter. Fixed in CF-2b.

**O-26 (second subject).** The `nphl` keep-first dedup drops 283 of Wheeler's Mets-era pitches from a name-filtered frame.

## 4 · Entity lock

MLBAM **554430**, RHP (resolved from data in uc-pps-020, not hand-keyed). Every row of CF-2b asserts `pitcher == 554430` (DQ-02), `p_throws == 'R'` (DQ-05), MLB clubs only (DQ-06).

## 5 · Client claims inventory (the human parent)

18 items from cells 16 and 21–23, graded in `out/dp_uc51_hp_reconciliation.csv` and report §9: 6 supported (HP-01, 02, 03, 04, 07, 18), 2 partly (HP-09, 17), 3 reproduced (HP-05, 10, 16), 1 adopted (HP-08), 1 definition difference (HP-06), 1 differs-explained (HP-14), 2 defects (HP-11 zw frame, HP-13 role-mixed population), 1 superseded (HP-12 draft jam_rate), 1 correct by accident (HP-15 leaked `gy`).

## 6 · Carry-ins and external lookups (logged, never computed on)

| Fact | Source | Used where |
|---|---|---|
| 2025 ended after 8/15/2025: blood clot; venous thoracic outlet syndrome; first-rib resection 9/23/2025; ~10 lb under weight in spring | Inquirer 9/19/2026; MLB.com 8/2025 | ch. 1, report §1 |
| 3-yr / $126M extension (March 2024), one year left (2027) | Inquirer 9/19/2026 | ch. 8 |
| "8.51 ERA over six starts" after the break; reported cause a mechanical flaw (dropping the glove, over-rotating), since fixed; FF ~96.5 (Jul 2025) vs ~95.5 (Sep 2026) | Inquirer 9/19/2026 | ch. 4, SR-2, DQ-30; velocity reconciles (96.5 / 95.4) |
| 2026 line: 14–5, 3.00 ERA, 28 GS, 162.0 IP, 193 K, 47 BB, 1.05 WHIP | StatMuse | DQ-16/17/18 reconcile K, BB, IP |
| Game 162 (9/27): 6 IP / 1 ER, Wild Card clinched | repo `week-ahead-2026-09-28.md` | DQ-19 |
| WC G3 (10/1, at ATL): four innings of relief, two runs; Harris 3-run HR off Nola in the 1st; Albies 2-run HR in the 4th; Braves 6–2, Phillies eliminated | FOX 29 10/1/2026; repo `week-ahead-2026-10-12.md` | DQ-20, ch. 8 |
| Savant Edge% 42.4, xwOBA .263 | client notebook (cell 21) | HP-05/06 |
