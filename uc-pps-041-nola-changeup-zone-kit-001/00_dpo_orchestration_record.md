# 00 · DPO Orchestration Record: `uc-pps-041-nola-changeup-zone-kit-001`

**UC #65 · contract `uc-pps-041` · build `dp_uc65` v1.0.0 · parent `uc-pps-040` (UC #64) · BID filed 2026-11-17 16:58 ET, accepted 16:59 ET**
Status: **DELIVERED ≈17:10 ET · READY-CONDITIONAL (C1–C3) · harness 20/20 · DQ 5 PASS / 0 WARN / 0 FAIL (2 INFO) · V1–V7 6/6.**
Deliverable is a **Claude Design kit** (`slides/`) for an animated closer appended to the client's video of 28 changeups taken for strikes in zones 7–9.

## 1 · The ask
The client went deeper on the changeup himself (notebook code in `intake/`) and wants the org to turn it into analysis and figures for Claude Design: the
home-plate pitch map of all his 2026 changeups with the video's pitches highlighted, plus cards on the changeup (his KPIs and others the org picks).

## 2 · Delivery (phases)
| Phase | Agents | Output |
|---|---|---|
| T0 | use-case-validator, source-system-profiler, domain-steward-proxy | clip reconciliation (28 files on disk = 27 R + 1 WC by the client's definition), frame lock, DV-1, BID |
| T1 | kpi-calculator, data-engineer | `dp_uc65_kernel.py` (K64 pinned; CZ-1, PNZ-1, BB-1, EC-1, TS-1, ZN-1, CSB-1, FP-1), `dp_uc65_nola_changeup.py`, 16 receipts |
| T2 | dashboard-specifier | 6 reference figures (16:9, dark), V1–V7, two eyeball-QA rounds |
| T4 | analytics-enabler, consumer-onboarding-agent | `slides/` kit: slide_content, copy registry (33 strings), per-scene data, refs, brief, sha256 manifest |
| T5–T6 | data-quality-engineer, certification-agent, version-controller, privacy-watchdog | harness 20/20, `01`–`07`, README, contract, ledger patch |

## 3 · Gates
| Gate | Status |
|---|---|
| Entity lock (605400, O-26) | PASS |
| **Clip reconciliation** (highlight set == 28 clips) | PASS (28 = 28; 0 spring pitches qualify) |
| No CDE inference | PASS — CZ-1 is the client's own line; new KPIs specified in the BID before code |
| Lineage (13 pins) | PASS |
| Visual standard V1–V7 | PASS 6/6, no exceptions |
| Harness | PASS 20/20 (every registry number recomputed from raw parquet) |
| Certification | READY-CONDITIONAL |
| Privacy | Clear (public performance data; no likenesses in the kit by rule) |

## 4 · Arguments the organization had
- **Raw heights or zone-scaled heights?** The client's chart draws raw `plate_z` with a mean zone. The source-system-profiler showed Statcast zones are hitter-specific: on raw heights 32% of the 28 sit outside the drawn bottom third, which would contradict the video. **Settled:** hero = PNZ-1 (zone-scaled), client's raw view shipped as the alternate (`r2`).
- **"Every one of the 28 inside the bottom third"?** Even zone-scaled, 8 of 28 are *centered* just below the zone. The kpi-calculator traced it: Statcast counts a ball that clips the edge (all 8 within one ball radius, ≤ 0.11 ft). **Settled:** the client's "size of a baseball" note became BB-1 (true 2.9 in circles), the DQ check became "every ball touches the bottom row" (PASS 28/28), and the fact became on-screen copy (`s2.edge`).
- **Spring training in "all his changeups".** The client's `pps` holds 13 spring changeups. **Settled:** DV-1 excludes them from the map (none is among the 28); cards use regular season; REC-C shows client-frame values differ by ≤ 0.5 pts.
- **Card D is unflattering** (first-pitch changeups to lefties: 40% strikes, a career low). The analytics-enabler kept it: the video shows the ones that landed, and the card tells the analyst how often that happened. Marked optional for a fan cut.
- **Titles toned to the data** at QA: "more lefties than ever" → "as often as ever" (22.1% ties 2020); "a setup pitch, not a finisher" scoped to 2026.
- **Ops slip, caught and cleaned:** the first kit run resolved the control-plane path wrong on the device VM and wrote a stray folder into the MLB root; fixed path logic (sibling mount first), rebuilt, deleted the stray folder with the DPO's permission.

## 5 · Escalations to the human DPO
1. Hand `slides/` to Claude Design (separate prompt). Brief: `slides/dp_uc65_claude_design_brief.md`.
2. Confirm the clip order: the kit lands the 28 in date order (`video_order`). If a1…d1 aren't chronological, edit `video_order` in `slides/data/dp_uc65_cz1_28.csv`.
3. Ratify CZ-1, PNZ-1, BB-1, EC-1, TS-1, ZN-1, CSB-1, FP-1 (provisional) and DV-1.
4. Ledger: paste UC52–UC65 patches.
