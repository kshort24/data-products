# 07 — Platform & Marketing (persistent operations)

**Department:** Platform + Marketing · **Agents:** `data-observability` · `version-controller` ·
`cost-watchdog` · **Use Case:** `uc-pps-026-cortes-acquisition-001` · **Date:** 2026-08-20

---

## 1. data-observability — monitoring & the armed re-baseline hook

This product's freshness model is unusual: **the source cannot update until Cortes throws a
competitive pitch.** The monitoring rule is therefore a tripwire, not a schedule:

| Rule | Trigger | Action |
|---|---|---|
| **RB-1 (armed)** | any 2026 rows for `pitcher == 641482` appear in a refreshed cache (rehab MiLB cache or `pps` once he debuts) | re-run build + verification; the `gap::2026 absent` assertions fail loudly by design; grade the three falsifiable calls (velocity band determines results · lefty edge holds · FPSR leads outing quality); publish v1.1 as the return read |
| RB-2 | 100 Phillies batters faced | full re-read (the uc-pps-024 closure convention, adapted) |
| Schema | `cortes.parquet` refetch changes columns/dtypes | data-dictionary diff before any re-run |

## 2. version-controller — release manifest

`uc-pps-026-cortes-acquisition-001` **v1.0.0** (2026-08-20). New data product — no consumers to
break; locked KPI functions inherited byte-consistent from the dp_uc29/dp_uc30 chain; UD-1..6
introduced as **provisional** (glossary promotion pending DPO ratification). Planned v1.1.0 =
RB-1 return read (non-breaking, additive). The BID document in this folder is superseded as a
plan by this delivered package but retained as the pricing receipt; telemetry closes the loop.

## 3. cost-watchdog — one observation

The 4.9 MB dashboard is 96% vendored plotly.js. If the control plane accumulates many dashboard
products, a shared `_assets/plotly.min.js` next to `data-products/` (referenced relatively)
would cut ~4.7 MB per product while staying CDN-free. Recommendation only — this product ships
self-contained per the standing rule.

## 4. Manual carry-in source log (marketing/comms hygiene)

| Fact | Source |
|---|---|
| Signing, 1-yr prorated ML deal, 2026-08-19 | NBC Sports player news 2026-08-19; Philadelphia Inquirer 2026-08-19; MLB.com |
| **Brian Keller DFA'd for the 40-man spot** | **Human DPO correction, 2026-08-20 (supersedes the intake doc's Kilian/60-day-IL line)** |
| Surgery mid-Oct 2025; no pitches since | NBC Sports player news 2026-08-19 |
| Expected multi-inning relief role | NBC Sports player news 2026-08-19 |
| 2022 All-Star selection | public record carry-in (supported in-frame by the 2022 peak receipts) |

## 5. Handoff

Package committed to `Agents for Data Products/data-products/uc-pps-026-cortes-acquisition-001/`
(00–07, README, contract doc, BID, build/dashboard/pdf/verification scripts, report .md/.pdf,
dashboard .html, telemetry/, out/). Ledger patch staged to the MLB repo root as
`uc_ledger_AI_PATCH_uc-pps-026-cortes.md`. Project memory updated (bid-pending note superseded
by the delivery note).
