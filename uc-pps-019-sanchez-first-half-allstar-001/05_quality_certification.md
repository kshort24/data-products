# 05 — Quality & Certification
## uc-pps-019 · data-quality-engineer + certification-agent

## A. Verification (independent recompute — `dp_uc21_verification.py`)
Method: headline claims recomputed WITHOUT the locked kernel (raw event masks; wOBA via Statcast `woba_value/woba_denom`, a deliberately different method). Results: `dp_uc21_verification_results.csv`.

**22/23 strict PASS.** The single flag, dispositioned:

| Claim | Kernel | Independent | Disposition |
|---|---|---|---|
| 2025 wOBA .263 | FanGraphs-weights kernel | .275 (Statcast woba_value scale) | **Accepted — method variance, not a data defect.** The same cross-method offset appears in 2026 (.292 vs .301, +.009) with consistent sign. The governed number is the locked-kernel value (inherited verbatim per governance rule); the independent method confirms magnitude, direction, and YoY delta. Tolerance was NOT widened to force a pass. |

All volume, counting, streak, QR, arsenal, chase, and KC-outing claims reproduced exactly.

## B. Certification readiness checklist
| Artifact | Present | Consistent |
|---|---|---|
| Use-case intake + gap report (01) | ✔ | ✔ GO verdict |
| Source profile & fitness (01) | ✔ | ✔ entity lock, freshness |
| KPI specs incl. new QR-1..3/SL-1 (02) | ✔ | ✔ spec'd before build |
| Glossary/tagging/privacy (03) | ✔ | ✔ no term redefined; privacy clear |
| Lineage + build record (04) | ✔ | ✔ receipts match manifest |
| DQ scorecard (`out/dp_uc21_dq_scorecard.csv`) | ✔ | ✔ all structural checks PASS |
| Freshness manifest (`out/dp_uc21_freshness_manifest.csv`) | ✔ | ✔ carry-ins logged |
| Report + PDF | ✔ | ✔ every number receipt-traceable |
| Verification results | ✔ | ✔ 22/23 + disposition above |

**Certification status: READY (conditional on human-DPO ratification of provisional KPIs QR-1..QR-3, SL-1).** Publish decision rests with the human DPO per governance principle #3.
