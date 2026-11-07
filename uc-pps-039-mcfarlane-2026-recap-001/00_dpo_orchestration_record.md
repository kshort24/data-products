# 00 · DPO Orchestration Record: `uc-pps-039-mcfarlane-2026-recap-001`

**UC #63 · contract `uc-pps-039` · build `dp_uc63` v1.0.0 · BID filed 2026-11-07 00:52 ET · awarded by RFP rule, accepted 00:53 ET**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **DELIVERED 2026-11-07 ≈01:15 ET · READY-CONDITIONAL (C1–C5, `05`) · harness 45/45 · DQ 10 PASS / 6 WARN / 0 FAIL · V1–V7 8/8 (1 registered exception).**
First recap whose commentary is the client's own narrative (copy rule **CL-1**), and first to ship slide content for an animated Claude Design build.

## 1 · The ask and how we framed it
The client pasted his notebook code and a written narrative for Alex McFarlane's 2026 and asked for: a PDF report, HTML, bid + acceptance +
governance artifacts, a stretch addition posed by the org, and slide content to be supplemented with animated visuals in Claude Design.
"Ensure data are accurate. Examine the narrative … Prefer my exact language as the commentary."

Four jobs:
1. **Reproduce the client frame exactly** before writing a word (333 pitches, 21 outings, 2 postseason; name rows = id rows).
2. **Grade every claim in the narrative** on bars filed before grading (HP-01..HP-12), and correct only what a receipt contradicts.
3. **Keep his words.** CL-1: verbatim commentary; each correction registered, marked †, listed in the ledger.
4. **Ship pieces Claude Design can't get wrong:** a slide-by-slide content file, per-slide data, reference PNGs, a copy registry (NC-1), a brief.

## 2 · Delivery plan (all phases ran)
| Phase | Departments (agents) | Output |
|---|---|---|
| T0 | use-case-validator, source-system-profiler, domain-steward-proxy, business-glossary-agent, token-economist | carry-in checks (web), entity lock, BID + acceptance, `01`, `intake/` |
| T1 | data-architect, kpi-calculator, eda-agent, join-validator, data-engineer | `dp_uc63_kernel.py`, `dp_uc63_mcfarlane_recap.py`, 52 receipts, `02`, `04` |
| T2 | dashboard-specifier | F1–F6, F5b, S1; V1–V7 audit; 2 eyeball-QA rounds |
| T3 | analytics-enabler | `dp_uc63_narrative.py` (CL-1), HP grades, report `.md` + `.pdf` (10 pp) |
| T4 | consumer-onboarding-agent, query-builder | dashboard `.html` + Artifact; slide content + Claude Design kit (39 files, sha manifest) |
| T5 | data-quality-engineer, certification-agent | DQ scorecard, harness 45/45, `05` |
| T6 | metadata-mapper, data-dictionary, data-tagger, version-controller, privacy-watchdog, data-observability, cost-watchdog | `03`, `06`, `07`, README, contract, ledger patch |

## 3 · Governance gates
| Gate | Status |
|---|---|
| Use case validated (0 blocking) | PASS (5 non-blocking, `01` §2) |
| Entity lock | PASS (686934; id frame = name frame = 333; Duran 661395; Kerkering 689147) |
| Lineage | PASS (`dp_uc62_kernel` pinned `2adc6005…`; full chain asserted, 11 files) |
| No CDE inference | PASS (all metrics inherited; FO-1 / BD-1 / ST-1 / FN-1 / BS-1r specified in the BID before code) |
| Anchor | PASS (house log max 2026-10-01) |
| Pre-registration | PASS (bars filed 00:52 ET; *seen* rows disclosed) |
| CL-1 client-language rule | PASS (5 registered corrections + 2 copy edits; no other edit to his sentences) |
| NC-1 slide copy rule | PASS (46 registered on-screen strings; harness V44) |
| Visual standard V1–V7 | PASS 8/8 (F3 registered V2 exception: client chart form, zone is the reference) |
| Harness | PASS 45/45 |
| Certification | READY-CONDITIONAL (C1–C5) |
| Privacy | Clear (public-figure performance data; no PII) |
| Publish | **DPO decision** |

## 4 · Arguments the organization had
- **Correct the client's words or leave them?** The analytics-enabler wanted the narrative untouched ("prefer my exact language"). The
  certification-agent refused to ship "out of Central Florida" and two truncated subtitle numbers. **Settled:** CL-1 — verbatim except where a
  receipt contradicts a word or digit; each edit registered with its HP row and marked †. Typos fixed silently are listed as copy edits.
- **"Very strong whiff."** 27.9% regular-season whiff is the 73rd percentile of 258 Phillies pitcher-seasons; the BID set "very strong" at the 75th.
  The domain-steward-proxy argued the postseason makes it 29.1%. **Settled:** the bar stands on the regular-season pool as filed; HP-04 is PARTLY and the
  copy keeps his phrase (it is commentary) with the percentile beside it.
- **"Bullet slider."** House BS-1 is LHP-only. Generalized to BS-1r (hand passed in, same 4.0 / 4.0 in rule). His SL misses by 0.7 in of sweep:
  "bullet-adjacent". The "hammer slider" cannot be separated from the bullet in the log (one SL tag); said plainly, not graded.
- **FO-1 names.** First pass labelled an opposing pitcher "Harper, Bryce" (batting-role rows carry the hitter's name). Caught at QA (EN-3);
  names now come from pitching-role rows only, opponents by MLBAM id. No grade moved.
- **Stretch choice.** S-1 (draft-class twins, first 21 outings each) chosen over an AAA→MLB bridge (S-2) because the client's narrative opens
  with Kerkering and the pairing was otherwise an aside. Built inside the bid.

## 5 · Escalations to the human DPO
1. **Publish** the report / dashboard / slide kit (privacy clear). The Artifact "Alex McFarlane 2026" is private until shared.
2. **Ratify** FO-1, BD-1, ST-1, FN-1 (provisional KPIs), BS-1r (generalization), CL-1 and NC-1 (copy rules). All first use except NC-1 (UC #61).
3. **Accept the five corrections** to the narrative (Kerkering's school; vs-LHB BB 2.6%; vs-RHB HH 41.9% / barrel 9.7%; FF run ≈ 9 in).
4. **Ledger:** paste UC52–UC63 patches, oldest first.
5. **RK-3:** K44 `chase_rate` returns rates rounded to .001; percentiles can shift by one at ties (74th vs 75th here). Fix in a future K44 successor or leave.

## 6 · Delivery summary
- **Headline:** "Alex McFarlane | 2026 | Nasty Stuff, Outlier Heater".
- **Findings:** client line reproduced exactly (.280 wOBA, .633 OPS, 25.9% K, 8.2% BB, 22:7); four-seam 99.4 mph / 2,544 rpm, 99th / 97th pct
  and no other RHP four-seam season in a Phillies game since 2015 at or above him on both; lefties K 33.3% with 1 walk, slider 38.1% whiff / 50.0% chase;
  righties .179 BA but 41.9% HH and 6 of 7 walks; 4 bridge-to-Duran outings, all from 8/31; four-seam 100.0 → 98.1 mph over his last three regular-season outings.
- **HP:** 11 CONFIRMED · 7 PARTLY · 1 CORRECTED · 1 NOT OBSERVABLE.
- **Bid vs actual:** ≈385k / ≈49 min bid vs ≈265k / ≈36 min actual (`07` §5).
