# 01 | Strategy \& Intake

**use-case-validator | source-system-profiler | domain-steward-proxy | business-glossary-agent**
`uc-pos-023-schwarber-2026-hr-animation-001` | UC #58 | `dp\_uc58` | written at T0 (2026-10-27 19:49 ET)

## 1 | ID reservation

UC **#58**, contract `uc-pos-023`, build `dp\_uc58`, folder `uc-pos-023-schwarber-2026-hr-animation-001`.

* **Collision check:** no `dp\_uc58\*` in the MLB root, `out/`, `eda/` or the control plane before this run. The IDs appear only as "next available" in the UC57 ledger patch (MLB root and its control-plane copy).
* **Stale ledger:** `uc\_ledger\_AI.md` still reads "Next available: UC #52". UC52–UC57 patches are pending paste, oldest first.
* **Prior UCs on the subject (Rule-1 step 3):** UC21 `uc-pos-004` (first half / Derby), UC33 `uc-pos-009` (swing decay). Neither built a cumulative-HR, spray or pitch-map product to inherit; both supply the entity lock and the NULL standard.

## 2 | Gap Report (use-case-validator): 10 gaps, 0 blocking → **GO**

|#|Gap|Class|Resolution|
|-|-|-|-|
|G1|LHP clip ask conflicts: storyboard "clips … off lefty fastballs" vs code "the two homers he hit on lefty breaking balls … and likely move on"|non-blocking|Default: S6 clips = top-2-EV lefty-fastball HRs (HL-1); the two lefty breaking-ball HRs (+ the WC HR off Dylan Lee) are the "compromised" beat. **DPO can flip**|
|G2|The WC HR off Dylan Lee is "fairly relevant … need to figure out how to incorporate"|non-blocking|Postscript beat in S6 (LHP breaking) and a "+1 postseason" badge after the S4 hold. Never on a regular-season curve or table|
|G3|Source CSVs (`c:\\Users\\kshort4\\Downloads\\ks26.csv`, `ks\_pos.csv`, `ks\_nphl.csv`) are on another machine|non-blocking|Client frame reproduced from the house log with the client's code verbatim (IX-1 spirit: same operators, house rows). SRC-D logged as conditional|
|G4|`cumulative\_pa` is a pitch count (CP-1)|non-blocking|Governed x = PA via `cumulative\_metric`; client frame graded side by side|
|G5|Two 2026 HRs have no `hc\_x/hc\_y` (SP-2), one is the max-distance highlight|non-blocking|SP-2 `des`-sector bearing, hollow marker, labelled approximate|
|G6|Transitions, zooms, the clip cuts and the three-screen consolidation are motion choices the data plane cannot verify|non-blocking|Specified in the prompt (transition grammar T1–T4); checked against keyframes only|
|G7|"It was his back? Did he lose his pop?"|non-blocking|Parent recap UC. Here: carry-ins only (CI-2); no causal claim on screen|
|G8|`play\_id` (needed for the Savant clip URL) can't be resolved from the cloud (StatsAPI outside the egress allowlist)|non-blocking|Clip list ships in `resolve\_play\_ids.py` input schema; the client resolves locally|
|G9|Spray chart draws all parks on the CBP outline|non-blocking|SP-3 caption rule|
|G10|Resolution, fps, duration, theme unspecified|non-blocking|1920×1080, 30 fps, ≈ 90 s ex-clips, dark field (the client's `plotly\_dark`) in house colors|

## 3 | Source Profile (source-system-profiler)

|Check|Result|
|-|-|
|House log|`data/phillies/phils\_2022..2026.parquet`; `phils\_2026` sha `be5d313d…`, max `game\_date` 2026-10-01 (WC G2). Anchor unchanged from UC54–UC57|
|Pre-Phillies file|`data/opponents/schwarber.parquet`, 11,449 rows × 93; CHC 2015–20, WSH/BOS 2021; 0 duplicate keys; carries `delta\_home\_win\_exp`|
|Entity|MLBAM 656941, `Schwarber, Kyle`, bats L; 0 duplicate pitch keys 2022–26|
|Regular-season PA (log)|2022 667 \| 2023 716 \| 2024 689 \| 2025 719 \| 2026 702 (2022 and 2023 include 1 and 2 `NON\_PA` event rows; PA grain excludes them)|
|Regular-season HR (log)|16 \| 0 \| 30 \| 26 \| 38 \| 11 \| 32 \| 46 \| 47 \| 38 \| 56 \| **45** (2015→2026)|
|Non-regular rows|2022 D/F/L/W \| 2023 D/F/L \| 2024–25 D \| 2026 S 31, F 57 pitches; HRs 2026: S 1 (3/22), F 1 (9/30)|
|2026 HR null audit|`hc\_x/hc\_y` 2 (4/3 at COL 460 ft; 9/5 vs ATL 435 ft); all other plotted fields 0|
|Lineage|K57 `assert\_lineage()` 17/17 pins PASS at bid time|
|Render stack|`/tmp/pyrender` (ENV-3, sixth occurrence)|

Fitness: **fit for Tier A.** The only structural limit is SP-2 (two HRs without coordinates).

## 4 | Assumptions (domain-steward-proxy): quoted, never computed on

|ID|Fact|Source|
|-|-|-|
|CI-1|2026: 45 HR, tied with Pete Crow-Armstrong for the MLB lead; "followed up his career-high 56 homers from last year with 45"|[MLB.com, final 2026 stat leaders](https://www.mlb.com/news/2026-mlb-regular-season-stat-leaders)|
|CI-2|156 G, .232/.354/.503, 130 wRC+, 2.9 fWAR; 22 HR in the first 56 G; 1st half .254/.367/.560, 2nd half .199/.336/.416; "mysterious back injury" downplayed by the team, no onset date; K% 31.4%; HR Derby runner-up at CBP|[Yahoo Sports / SB Nation report card, 2026-10-21](https://sports.yahoo.com/articles/2026-phillies-report-cards-kyle-150000667.html)|
|CI-3a|6/20 vs NYM, 15-3: HRs off Freddy Peralta (3rd, 456 ft), Cionel Pérez (3rd, 457 ft; two in one inning), Tobias Myers (7th, two-run, MLB-leading 28th)|[6abc / AP](https://6abc.com/post/kyle-schwarber-hits-3-homers-bryce-harper-cycle-phillies-15-rout-mets/19342830/)|
|CI-3b|8/23 vs STL, 6-4: two-out, two-run walk-off in the 9th off Riley O'Brien, 459 ft, MLB-leading 39th, capping a six-run rally|[TSN / AP](https://www.tsn.ca/mlb/article/schwarbers-two-run-hr-in-9th-rallies-phillies-for-win-over-cardinals/)|
|CI-3c|WC Game 2 at Truist Park (Wed 9/30): 8th-inning HR off Dylan Lee; Phillies won 4-3 in 10|[MLB.com](https://www.mlb.com/braves/news/braves-lose-nl-wild-card-game-2-2026)|
|CI-4|Season HR 2015 16 \| 2017 30 \| 2018 26 \| 2019 38 \| 2021 32 (25 WSH + 7 BOS) \| 2022 46 \| 2023 47; 385 career through 2026-09-15|[Wikipedia](https://en.wikipedia.org/wiki/Kyle_Schwarber)|

**Reconciliation:** log 340 HR through 2025 + 45 in 2026 = 385 (CI-4); pitcher ids on 6/20 (642547, 672335, 668964), 8/23 (676617) and 9/30 (669276) match CI-3 innings and distances.

## 5 | Glossary (business-glossary-agent)

|Term|Status|Definition|
|-|-|-|
|**CP-1 cumulative HR by PA**|consumed (`cumulative\_metric` `hr`) + rule|Running HR count over regular-season PA within a season; PA = `events` not null minus `truncated\_pa`; de-duplicated on `PITCH\_KEY`|
|**HB-1 HR barrel share**|NEW, provisional|Barrels (`launch\_speed\_angle == 6`) / HR. The client's `Barrels/HR`. Not `barrel\_rate`|
|Barrel rate|consumed (K54 `barrel\_rate\_g`)|Barrels / BIP|
|**WP-1 batter WPA**|NEW rule, provisional|`delta\_home\_win\_exp` if `inning\_topbot == 'Bot'` else its negative; mirror of the `dp\_uc51` pitching rule|
|**HL-1 highlight rules**|NEW, provisional|As pre-registered in the BID §3|
|**SP-1 / SP-2 / SP-3**|NEW, provisional|Spray placement (bearing from DR-1, radius = `hit\_distance\_sc`), missing-coordinate fallback, one-outline caption|
|Spray bearing, carry radius|consumed (cbp-spray\_AI.md, DR-1/PA-L1)|`atan2(loc\_x, loc\_y)`; + = RF side|
|**PM-1 pitch map**|NEW drawing rule|Catcher's view; zone half-width 0.83 ft; mean `sz\_top/sz\_bot`; ball 0.242 ft|
|Pitch group|consumed (CPG-1, client map)|FF/SI/FC Fastballs \| CH/FS/FO/SC Offspeed \| CU/KC/SL/ST/SV/CS/KN Breaking \| else Other|
|"Thump", "dongs", "booms"|client terms, not defined|Reported, never used as a threshold|



