# 05 · Quality & Certification
**dq-rule-definer · data-quality-engineer · certification-agent · brand-guardian**

## 1 · DQ scorecard — 12 PASS / 5 WARN / 0 FAIL (`out/dp_uc56_dq_scorecard.csv`)
| Rule | Status | Detail |
|---|---|---|
| LIN-1 lineage pins | PASS | 16 files sha256-pinned |
| ANC-1 pinned anchor | PASS | max game_date 2026-10-01 |
| ENT-1 id lock | PASS | 624641, batting role, R: 4,223 pitches; stand R |
| SRC-4 client frame game types | WARN | 45 non-regular PHI PA incl. 19 spring + 7 WC in 2026; excluded from rates |
| SRC-5 two-team client frame | WARN | STL file in client frame; context only |
| SRC-6 2022 PHI sample | WARN | 59 PA; never a baseline |
| CM-1 endpoint reconcile | PASS | tol 1e-9 every season |
| POS-1 fielding games | WARN | late moves count at two positions; B-Ref beside it |
| SEN-1/2/3 sensor coverage | PASS | EV 99.63% BIP · OZ-xBA 98.28% · bat speed 96.6% of swings |
| GL-1 EV50 definition | WARN | client definition (median), disclosed |
| PAR-1 reconcile CI-1 | PASS | 250 PA, .247/.283/.429 both sides |
| TR-1 date fixed | PASS | 2026-07-16 from the schedule |
| OZ-1 / WA-1 bars unchanged | PASS | as pre-registered |
| RATE-1 bounds | PASS | all season rates in [0, 1] |

## 2 · Independent harness — 161 / 161 PASS (`out/dp_uc56_verification_log.csv`)
Reads raw parquet with pandas and pyarrow; takes only constants from the kernel.
| Family | Checks | What it recomputes |
|---|---|---|
| A pre-registration | 9 | OZ/DF/WA constants; ER-1 and TR-1 parameters unchanged from parents; pin count |
| B entity & sources | 9 | id, name, stand, keys, seasons, anchor, spring/WC PA, STL file |
| C slash & wOBA | 38 | PA, AVG, OBP, SLG, wOBA, BB%, K% per season (per-season weights); CI-1 slash; baseline |
| D discipline | 17 | chase, contact, OOZ contact, swing per season; 2026 chase = pool max |
| E batted ball | 27 | HH (O-8 denominator), barrel, EV50/EV90/max, pull-air (raw wedge), bat speed |
| F OZ-1 | 12 | OZ-BA, OZ-xBA, call per season |
| G cumulative | 6 | endpoints; 2026 last at 10/10 checkpoints |
| H TR-1 | 5 | schedule gap date; pre/post wOBA and PA; call |
| I pitch groups | 6 | 2026 PA and whiff for 95+, breaking, offspeed |
| J platoon | 4 | wOBA vs LHP/RHP, 2026 and 2023–25 |
| K tenure | 7 | career PA/HR/wOBA; 2026 games at LF/3B/SS/2B |
| L WA-1 | 3 | ceiling, DF count, term |
| M narrative & report | 13 | CI-1…CI-7 labelled; slash and walkaway in report; no "<NA>"; all figures embedded; brand; CDN plotly |
| N HP & client frame | 5 | 11 rows; HP-07 grade; STL + spring in client frame; HP-09 r |

**What the harness caught (the reason it exists):** first run 154/161. Three wOBA pools (baseline, career, platoon base) disagreed by ~.002–.003 → **WB-2**, an inherited weighting quirk, fixed by wrapper and re-run. Three barrel checks disagreed → **H-1**, a harness bug (nullable compare). Both resolved before certification; no published number was patched by hand.

## 3 · Brand & claim (brand-guardian) — 9 / 9
Every figure asserts its subtitle's claim before writing, uses Arial, carries title + subtitle, and passes the palette check (`out/dp_uc56_brand_checks.csv`). Render QA (all 9 PNGs viewed) caught Q-1, Q-2, Q-3 (`03` §4). PDF contact sheet: `out/dp_uc56_qa_pdf_contact.png`.

## 4 · Palette
Highlight-vs-context trio (Phillies red / gray / navy reference) as UC55. Position colours reuse the PG-1 validated trio plus navy and gray (validated UC55, light and dark).

## 5 · Certification verdict (certification-agent)
**READY-CONDITIONAL** — artifacts complete and internally consistent: BID, 00–07, README, contract, ledger patch, lineage pins, DQ scorecard, harness log, HP grades, figure specs. Conditions C1–C5 in `00` §6.
