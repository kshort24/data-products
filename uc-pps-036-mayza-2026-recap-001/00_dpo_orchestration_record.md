# 00 · DPO Orchestration Record: `uc-pps-036-mayza-2026-recap-001`

**UC #52 · contract `uc-pps-036` · build `dp_uc52` · v1.0.0 · delivered 2026-10-14 ET**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL (C1–C5)** · independently verified **74 / 74** · DQ **12 PASS / 0 WARN / 0 FAIL** · brand 10 / 10 figures pass
Run: audit Phase 2 protocol (house-format skill loaded first; stop after BID; scope Tier A awarded 2026-10-14 00:35 ET; title changed by the DPO to "The Sheriff of the Phillies Bullpen").

---

## 1 · The ask and how we framed it
The client submitted a notebook export: a Mayza recap with code and claims, plus `tm_success_rate` from `July 2026.ipynb` cell 137. It asked what he did well, his platoon splits, his stuff and release point, sustainability, career and Phillies-LHP-reliever context, the most similar Phillies LHP, and a revisit of the "Tim Mayza Success Rate". The client asked for a PDF, a fully governed package and, if it made sense, a dashboard. The consumable must not balloon, and it must stay comparable with the UC48, UC49 and UC51 recaps.

The organization read it as **four jobs**:
1. **Find the spine before writing.** He kept runners off with strikes (BB% #6 of 32 Phillies LHP relief seasons), and the results were not borrowed: xwOBA .288 against a .299 actual on the same Statcast basis. Contact got louder (hard-hit 2nd-highest of 9 seasons), mostly from righties.
2. **Hold the comparison profile.** We scoped five forms and built two (PDF ≤10 pp / 9 sections, dashboard 8 chapters), with 10 figures and 3 new KPIs, the same shape as UC48, UC49 and UC51. The persona card is deferred; projection and video were not bid.
3. **Pre-register the client's own metric.** QA-1 implements the stated definition. The client's code is reproduced beside it (40.1%) and graded, never overwritten.
4. **Reproduce the parent before improving it.** 14 HP rows were rebuilt on the client's own frames (`pps` + `nphl` by name, game types as delivered) with the client's functions (IX-1: `inds`, `tm_success_rate`), then restated on the governed frame.

## 2 · Delivery plan (departments actually engaged)
| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 6 gaps (0 blocking) → `01` §2 |
| | `source-system-profiler` | id scan: 22 opponent files hold 641835; `mayza.parquet` is the pitcher-keyed pull; stale root `pp26.csv` found |
| | `domain-steward-proxy` | 5 carry-ins (MLBTR waiver claim, re-sign headline, 2027 status unverified, Pattison paraphrase, nickname) |
| | `business-glossary-agent` | 6 terms (QA-1, BS-1, DS-1, RP-1, WB-1, house wOBA vs Statcast-basis wOBA) |
| Engineering Design | `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier` | CF-2c frame; EDA to file; EN-2 join asserted fan-out-free; extra columns mapped; 8-chapter spec |
| Governance | `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` / `data-tagger` · `version-controller` | specs for QA-1/BS-1/DS-1/RP-1; lineage to `headlines.json`; privacy CLEAR; v1.0.0 |
| Engineering Build | `data-engineer` | everything ran on the laptop VM (render stack installed to `/tmp/pyrender`); 42 receipts in `out/` |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` · `certification-agent` | 12 DQ rules; harness families A–G, 74 checks |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` / `product-narrator` | reading paths, FAQ, catalog entry (`06`) |
| Platform & Marketing | `cost-watchdog` / `token-economist` | bid vs actual, Phase 2 audit fields (`07`) |

**Not engaged:** `machine-learning-engineer` (no projection bid) · `join-validator` beyond the EN-2 assert (single-grain frame).

## 3 · Governance gate checks
| Gate | Result |
|---|---|
| G1 · Entity locked to MLBAM id | PASS: 641835 |
| G2 · Rule-1 search before declaring anything new | PASS: table in `03` §0 (QA-1 had 0 hits) |
| G3 · Locked KPIs inherited, not re-derived | PASS: `dp_uc51_kernel.py` sha256 `4845bae2…`, which transitively pins K49, K50, K48, K44 and barrel_rate |
| G4 · No re-derivation of existing work | PASS: season recap, career frame, house percentile, runs on watch, XW-1, BR-1 all imported |
| G5 · Small samples print denominators | PASS: PA on every split; caveat on weapon cells (35–81 PA) |
| G6 · Superlatives name their population | PASS: "#n of 32 Phillies LHP relief seasons", "of 9 seasons", "of 62 Phillies LHP seasons" |
| G7 · Carry-ins labelled, sourced, never computed on | PASS: harness G (4/4) |
| G8 · Pre-registration is not prediction | n/a (no card) |
| G9 · Every published number reconciles to a receipt | PASS: harness F 16/16; narrative module formats from `headlines.json` |
| G10 · Client claims graded, not overwritten | PASS: 14 HP rows |
| G11 · Anchor pinned | PASS: 2026-10-01 (build refuses a later log) |
| G12 · No medical inference | PASS: the 2025 IL stint is a carry-in only |

## 4 · Capability fulfilment
| Asked for | Delivered as | Where |
|---|---|---|
| What did he do well? | Bottom line + results chapter | report §1–2; dashboard hero, ch. 1 |
| Platoon splits | Pitch map by side + split table (both wOBA bases) | §4; ch. 3 |
| Exceptional stuff / release point | Arsenal movement, release + extension vs house LHP, bullet slider (BS-1) | §5; ch. 4–5 |
| Sustainable? | HH/barrel by year, barrel→wOBA house line, xwOBA vs same-basis wOBA | §3; ch. 2 |
| Mayza historically; Phillies LHP relievers historically | Career wOBA/xwOBA by year; LHP relief table (n=32) | §2; ch. 1 |
| Most similar Phillies LHP | DS-1 comps (Sánchez 2021, Alvarado 2026) | §8; ch. 8 |
| Revisit the Success Rate | QA-1 vs house + client method graded (HP-13) | §7; ch. 7 |
| PDF, governed package, dashboard | 9-page PDF, Artifact dashboard, 00–07 | MLB root + this folder |

## 5 · The finding, in the DPO's words
Mayza's 2026 was real. He allowed a .285 wOBA (house basis), the third-best of his nine seasons and #11 of 32 Phillies LHP relief seasons since 2015. On Statcast's own basis he allowed .299 against a .288 expectation, so luck did not carry him. He did it by throwing strikes (5.9% walks, #6 of 32), not by finishing at-bats faster: his quick-AB rate (57.6%) beat the house median but was his career low by a hair. The risk is contact. His hard-hit rate (45.2%) trailed only his rookie year, and righties carried a .314 xwOBA. The delivery explains the profile: a high, tight slot with 6.93 ft of extension (85th percentile), a sinker with less run than most, and an 87.4 mph bullet slider that only Cristopher Sánchez matches in the house.

## 6 · Where the organization argued with itself
**Which wOBA is "his wOBA"?** `kpi-calculator` wanted to keep the house `nresults` wOBA everywhere (the client's own number, used for every rank). The harness (`data-quality-engineer`) showed the first draft compared that .285 with Statcast-basis xwOBA (.288) and called it agreement; on one basis the actual is .299. **Resolution:** two named bases. House wOBA drives ranks; xwOBA is only ever set beside WB-1 (same rows, same denominator). Three narrative claims were rewritten, F1 was rebuilt on one basis, and the platoon table now prints both.

**Is the bullet slider unique?** `product-narrator` wanted the client's "fairly unique" headline. BS-1 found 11 other house LHP bullet seasons, most of them Sánchez's. **Resolution:** "uncommon, not unique", with the velocity rank (94th percentile) as what actually sets his apart.

## 7 · Escalations to the human DPO
1. **E-1 · Ratify IX-1.** This is its second clean use (UC51 first): `inds` and `tm_success_rate` were extracted with sha256 pins and the host notebooks were never run. Recommend ratification.
2. **E-2 · Upstream WB-1 into XW-1 (non-breaking).** `xwoba_pa` returns no same-basis actual, which invites the comparison this UC first got wrong. Add `woba_sc` to K50's XW-1 output, then back-check UC48, UC49 and UC51 for any xwOBA set against `nresults` wOBA.
3. **E-3 · NF-1 projection (HX-1).** `nphl_name_frame` drops `launch_speed_angle`, so client-frame barrel rates are wrong (HP-04 could not be reproduced on the client frame). Add the column upstream.
4. **E-4 · Render pin (RQ-1).** kaleido 0.2.1 collapses string-category x on scatter traces. Use numeric x or bump kaleido in `requirements-render.txt`.
5. **E-5 · Stale `pp26.csv` at the MLB root** (134 Mayza pitches, through 2026-04-14). It cannot be deleted from here (no delete permission); recommend archiving it.
6. **E-6 · Ledger.** `uc_ledger_AI_PATCH_uc-pps-036-mayza-2026-recap.md` is a **pending paste**.

## 8 · Publish recommendation
**READY-CONDITIONAL. Internal audience (pitching department, bullpen staff, front office).**
- **C1** Ranks and percentiles are Phillies-frame (2015–26), not MLB-wide.
- **C2** Carry-ins are reported facts, never computed on; 2027 status unverified.
- **C3** QA-1, BS-1, DS-1 and RP-1 are provisional (first use).
- **C4** Relief samples are small (271 PA; splits 35–156 PA). Read direction, not decimals.
- **C5** Two wOBA bases are in use and labelled; xwOBA is compared only with Statcast-basis wOBA.

External publication: after DPO review of C2 (contract status) and C5 wording.
