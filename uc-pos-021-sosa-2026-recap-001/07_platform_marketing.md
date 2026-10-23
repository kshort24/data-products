# 07 · Platform & Marketing
**data-observability · version-controller · cost-watchdog · token-economist · communications-agent**

## 1 · Tripwires (v1.1.0 triggers)
| # | Tripwire | Action |
|---|---|---|
| T-1 | Sosa signs anywhere | Record terms beside WA-1; if above $6.0M AAV or >2 yrs, note "walked" in the ledger |
| T-2 | New utility deals in the 2026–27 offseason | Re-run WA-1 band with the new comp set (CI-5 refresh); flags unchanged |
| T-3 | First 2027 PA for him in any house file | v1.1.0 re-run; anchor guard refuses a silent rerun |
| T-4 | Groin injury update (CI-6) | Narrative caveat only; no data change |
| T-5 | Request to share beyond the front office | Privacy re-review; strip the walkaway chapter for external use |
| T-6 | K54 spine ships a WB-2 fix | Breaking for pooled-wOBA receipts in UC34–UC55; consumer notice: "pooled multi-season wOBA changes by up to ~.003; single-season values unchanged" |

## 2 · Cost audit (cost-watchdog)
- Most expensive step: the harness (~40 s; reads 12 seasons raw, by design).
- Build 12 s; figures 25 s (kaleido); PDF ~15 s. Storage: 58 receipts 3.7 MB; PDF 1.9 MB; dashboard 0.16 MB (plotly from CDN).
- Waste found: SH-1 (truncated shell) cost one figure re-run; WB-2 cost one full rebuild (~20k tokens) and was worth it.

## 3 · Bid vs actual (token-economist)
Denominator: the session token counter (tokens left), this turn only. In/out split estimated from what was written (~95 KB Python, ~45 KB receipts/BID, report and dashboard text). Minutes from the first tool call (13:52 ET) to the last receipt (~14:26 ET).

| Mark | When | Counter | Δ |
|---|---|---|---|
| C0 | session start | 15,000,000 | — |
| C2 | end of T0 recon (before BID write) | 14,758,629 | 241.4k |
| C3 | BID filed and awarded | 14,749,712 | 8.9k |
| C4 | T1 done (kernel, build, D-1, J-2, platoon, HP) | 14,693,751 | 56.0k |
| C5 | T2 done (skill, 9 figures, 2 render-QA passes, Q-1/2/3) | 14,630,752 | 63.0k |
| C6 | T3+T4 done (narrative, report, PDF QA, dashboard, Playwright QA, Artifact quickstart + v1) | 14,584,025 | 46.7k |
| C7 | T5 done (harness 154 → 161 with WB-2 + H-1, full rebuild, Artifact v2) | 14,564,306 | 19.7k |
| C8 | 00–07, README, contract, ledger, wording fix, Artifact v3 | 14,537,151 | 27.2k |
| C-final | reply (estimated) | ≈14,534,000 | ≈3k |

| Phase | Bid in+out | Bid min | Actual (counter) | Actual min |
|---|---|---|---|---|
| T0 Intake → BID | ~252k | 12 | 250.3k | 12 |
| T1 Kernel + build + HP + EDA | 73k | 8 | 56.0k | 5 |
| T2 Figures + render QA | 60k | 7 | 63.0k | 4 |
| T3 Dashboard + QA + Artifact | 44k | 6 | ≈33k | 3 |
| T4 Report + PDF | 18k | 3 | ≈14k | 2 |
| T5 Harness | 30k | 4 | 19.7k | 2 |
| T6 Governance 00–07, README, contract, ledger | 38k | 6 | ≈30k | 6 |
| D Defect discovery | 10k | 2 | (inside T1–T5: WB-2, D-1, J-2, J-3, H-1, Q-1/2/3, SH-1) | — |
| Contingency | 14k | 2 | — | — |
| **Total** | **~539k (444k in / 95k out)** | **~50** | **≈466k (≈390k in / ≈76k out)** | **≈34** |

**Credits at list ($10/M in, $50/M out):** bid ≈ **$9.19**; actual ≈ **$7.70 (−16%)**. Tokens ≈14% under bid, minutes ≈32% under. The winning bid was delivered under price and ahead of time, with every published number independently verified and one inherited defect (WB-2) surfaced for the whole catalogue.

### Comparison with the season recaps
| UC | Subject | Total (counter) | Minutes | Shape |
|---|---|---|---|---|
| UC53 `uc-pps-037` | Alvarado (RP, end of tenure) | ≈518k | ≈41 | 10 pp · 7 ch · 10 fig · 2 new |
| UC54 `uc-pos-019` | Crawford (CF, rookie) | ≈576k | ≈46 | 10 pp · 7 ch · 10 fig · 3 new |
| UC55 `uc-pos-020` | Stott (2B/3B) | ≈485k | ≈44 | 10 pp · 7 ch · 10 fig · 3 new |
| **UC56 `uc-pos-021`** | **Sosa (UT, end of tenure?)** | **≈466k** | **≈34** | **8 pp · 8 ch · 9 fig · 2 new · all in control plane** |

## 4 · Calibration findings (eighth instrumented recap bid)
- **C-13 (new) · T0 is now the cost centre.** 53% of the run was T0 (two-repo recon + web carry-ins). The post-T0 build (≈223k) was the cheapest of any recap. Next pos recap: price T0 at 200k unless the RFP needs fresh web research, then 250k.
- **C-14 (new) · Web-dependent RFPs:** the walkaway needed 8 web reads (≈45k incl. failures). Price contract-value asks at +45k.
- **C-12 held:** harness at 20k came in under the 30k bid because ER-1/TR-1 were inherited, not re-implemented.
- **C-8 confirmed again:** render QA caught a content error (Q-2), not only layout.

## 5 · What this product makes possible next (the marketing half)
- **Bench-market board:** WA-1 on every Phillies free agent (Bohm, Arraez, García, Raley, Mayza, Alvarado per NBC) with one comp refresh.
- **OZ-1 roster scan:** which chasers' out-of-zone damage is earned vs lucky.
- **WB-2 sweep:** re-run pooled wOBA in UC34–UC55 once the spine is fixed.

## 6 · Ledger
Patch: `uc_ledger_AI_PATCH_uc-pos-021-sosa-2026-recap.md` (this folder only, per the RFP). Next available after this UC: **UC #57 / dp_uc57** (pps next `uc-pps-038` · pos next `uc-pos-022`).
