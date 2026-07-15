# 06 — Certification Readiness (certification-agent) · uc-pps-018

| Requirement | Artifact | Present | Consistent |
|---|---|---|---|
| Use-case intake + gap resolution | 01 | ✔ | ✔ (G1 saves decision propagated to 00/02/03/report) |
| Source profile + entity lock + freshness | 02, `out/dp_uc19_freshness_manifest.csv` | ✔ | ✔ (windows match receipts) |
| Glossary approval / no-new-terms confirmation | 03 | ✔ | ✔ (no new KPIs claimed anywhere) |
| Data model + lineage | 04 | ✔ | ✔ (8 receipts ↔ 8 lineage branches) |
| Build artifact, runnable + portable | `dp_uc19_duran_first_half.py` | ✔ | ✔ (run 2026-07-13 via MLB_DATA_ROOT; new files only, no overwrites) |
| DQ scorecard, blocking checks | 05, `out/dp_uc19_dq_scorecard.csv` | ✔ | ✔ (5/5 PASS) |
| Reader deliverable | `dp_uc19_duran_first_half_report.md` / `.pdf` | ✔ | ✔ (spot-check below) |
| Manual carry-in register | freshness manifest rows 4–5 | ✔ | ✔ (report labels both as carry-ins) |
| Privacy review | public MLB performance data; no PII beyond public identity; no quasi-identifier combinations | ✔ | trivial pass |
| Acceptance criteria (accurate, disciplined, documented, defensible, PDF) | this trail | ✔ | ✔ |

**Number spot-check (report ↔ receipt):** 2026 wOBA .227 / xwOBA .229 / K% .397 / whiff .396 / in-zone .452 / putaway .325 ↔ `era_trend.csv` ✔ · splitter usage .452, FF .270, SW .103, CH .068 ↔ `arsenal_by_era.csv` ✔ · splitter 2-strike putaway .406 (32) ↔ `putaway_by_pitch.csv` ✔ · CH 29 vs LHB, 11.2 mph sep ↔ `changeup_detail.csv` ✔ · monthly wOBA .297/.105/.256/.216/.213 ↔ `2026_monthly.csv` ✔

**Status: READY.** Publish decision belongs to the DPO (Kellen). Open item for DPO: ledger rows (00 §numbering).
