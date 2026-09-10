# 00 · DPO Orchestration Record — `uc-pos-016-turner-whole-field-directional-001`

**Orchestrator:** `data-product-owner`, on behalf of all seven departments
**Human DPO:** Kellen Short · **UC #42** · contract `uc-pos-016` · build artifact `dp_uc42`
**Delivery date:** 2026-09-10 · **Status:** READY-CONDITIONAL (see `05`)

## 1 · The ask and framing

Kellen brought a working theory, not a confirmed finding: that Trea Turner is pulling outside-zone pitches
too often in 2026 rather than going the other way — a drift from his 2023-2025 Phillies-era behavior. He was
explicit that this layer should **lead the narrative analysis against the data**, not confirm the premise on
his behalf, and he delegated three open decisions to this layer rather than asking for silent defaults
(visual layout, KPI-vs-diagnostic status, ledger ID). He also handed down five known corrections from his own
prior draft work, to be carried in rather than re-derived: source from the repo not local CSVs, reuse the
governed `hit_direction` logic, lock the `p_throws` color map, fix `sort_rank` for handedness, drop
`release_speed` as marker size in favor of a fixed baseball-diameter size, and lock the entity by MLBAM id.

Two referenced attachments (`tt_whole_field_uc.md`, a hand-sketch photo) never reached this session despite
being described as attached. This is logged as a non-blocking gap (`01` G-1) and disclosed throughout rather
than treated as a reason to halt — the prompt text itself was detailed enough to serve as the intake document
of record.

## 2 · Delivery plan (departments actually engaged)

| Order | Department | Output | Status |
|---|---|---|---|
| 1 | Strategy & Intake | `01_strategy_intake.md` — gap report, premise stress-test, source fitness, discretion log | Done |
| 2 | Engineering Design | `02_engineering_design.md` — data model, EDA, design-change note, metadata map | Done |
| 3 | Governance | `03_governance.md` — Rule-1 search, new-object register, lineage, privacy/tagging | Done |
| 4 | Engineering Build | `04_engineering_build.md` — build manifest, environment notes, assertions | Done |
| 5 | Quality & Certification | `05_quality_certification.md` — DQ scorecard, defect register, verification, cert decision | Done |
| 6 | Consumer Success | `06_consumer_success.md` — persona, how-to-read, dashboard spec, reuse patterns | Done |
| 7 | Platform & Marketing | `07_platform_marketing.md` — monitors, cost audit, bid-vs-actual | Done |
| — | Pricing | `BID_2026-09-10_uc-pos-016-turner-whole-field.md` — bid, awarded, reconciled in `07` | Done |

No Layer-1 `use-case-validator` / `source-system-profiler` / `domain-steward-proxy` / `business-glossary-agent`
formal hand-off artifacts were produced as separate files — at this diagnostic-tier scope, their outputs are
folded directly into `01_strategy_intake.md` (a `dashboard-specifier` judgment call disclosed in `06`, mirroring
how `uc-pos-014` scoped its own department set to the ask rather than running every one of the 27 agents on
every UC regardless of size).

## 3 · Governance gate checks

| Gate | Result |
|---|---|
| No CDE inference | Entity lock is MLBAM id `607208`, not a name filter — verified before any computation, per Kellen's own correction |
| No build without approved specs | Five corrections and three open decisions were logged and resolved (`01`) before `02`/`04` began; open decisions are flagged back to Kellen, not silently assumed |
| No publish without certification | `05` ran before this file — READY-CONDITIONAL, not an unqualified pass; three explicit conditions carried forward, none blocking internal delivery |
| No breaking changes without notice | New UC, no prior version — n/a, confirmed in `05` versioning |
| Privacy flags block external publish | Privacy assessment LOW (`03`) — public on-field performance data, no PII beyond a public figure's public game data |

All five gates cleared or explicitly n/a. No gate was overridden.

## 4 · Capability fulfilment

| Kellen's requirement | Fulfilled by | Note |
|---|---|---|
| Source from repo, not local CSV exports | `dp_uc42_kernel.py::load_turner_pos()` reads `phils_{2023..2026}.parquet` via the data plane | Confirmed fresh through 2026-09-09 |
| `hit_direction` from existing repo logic, not hardcoded | Verbatim from `Baseball Functions.ipynb` cell 56 / `dp_uc40_kernel.py` | Rule-1 search documented in `03` |
| Lock `p_throws` color map | `P_THROWS_COLORS = {'R': '#002D72', 'L': '#E81828'}` | Brand-consistent, fixed across every facet/loop |
| Fix `sort_rank` handedness bug | **Could not locate the referenced function anywhere in either repo** — built new, stand-aware `sort_rank(direction, stand)`, labeled NEW-UC42/provisional | Escalated below, §7 |
| Drop `release_speed` marker sizing | `MARKER_SIZE = 22` fixed constant (baseball-diameter approximation), no data-driven sizing | Applied in `fig1_facet_grid.png` |
| Entity lock via MLBAM id | `SUBJECT_MLBAM = 607208`, never a name match | Reconfirmed a third time across three Turner UCs |
| Lead the narrative against the data | See §5 below | Premise tested and found not supported |
| Resolve 3 open decisions, don't default silently | See §5/§7 | All three resolved with reasoning, all three flagged for Kellen's confirmation |
| PDF report | `dp_uc42_turner_whole_field_report.pdf` | reportlab (environment substitution, disclosed in `04`) |
| Explore interactive dashboard | `dp_uc42_turner_whole_field_dashboard.html` | Self-contained, Chart.js vendored inline, opens with no network |
| Bid framed as competitive RFP, treated as won | `BID_2026-09-10_uc-pos-016-turner-whole-field.md` | Reconciled against actuals in `07` |

## 5 · The finding, in the DPO's words

Kellen's literal premise — that Turner is pulling **outside-zone** pitches too often in 2026 — **is not
supported** by the data. The outside-zone pull rate in 2026 (39.4%, n=71) sits inside the noise band against
the pooled 2023-2025 outside-zone pull rate (36.7%, n=228); |z| < 1.5 on the pooled two-proportion test. The
2026 point estimate is not even directionally large, and the sample is thin enough that this should be read
as "not detected," not "ruled out" — that distinction is carried forward as a certification condition, not
buried.

What the data does show, and what this build surfaces instead: on pitches **inside the zone**, Turner's pull
rate has declined and his oppo rate has risen from 2023 to 2026, and this shift clears the moderate-to-strong
band (|z| > 2.5) on the same pooled test applied to the in-zone population. This is a real, measurable shift —
just not the one Kellen hypothesized, and not on the pitches he hypothesized it on. The honest headline is:
the premise as stated is wrong, but there is a related and arguably more interesting finding sitting one zone
category away from where he was looking.

This is exactly the falsify-before-describe outcome this repo's standing policy exists to produce, and it is
reported as a split verdict rather than smoothed into either "confirmed" or "nothing found."

## 6 · Where the organization argued with itself

Two points of internal friction, both resolved by disclosure rather than by picking the more convenient
answer:

1. **The premise rejection itself.** It would have been easy to report the in-zone shift as if it confirmed
   Kellen's outside-zone theory — the two effects sit in the same intuitive direction (more oppo, less pull)
   and a less careful build could have blurred the zone distinction to manufacture agreement. `02`'s EDA
   forced the zone-specific grain explicitly because pooling in/out-of-zone BIP together would have hidden
   exactly this distinction. The report states the split plainly: `01` §Premises, report §1 and §6.
2. **`sort_rank`.** Kellen described this as an existing function with a known handedness bug to fix. Rule-1
   search (`03`) found no such function anywhere in either repo. Rather than fabricate a plausible-looking
   "original" to patch, this build declared a new function, labeled it provisional, and logged the gap as
   material (`01` G-2) rather than cosmetic — because a silently invented "fix" to code that was never seen
   would misrepresent what was actually inherited versus authored fresh this session.

## 7 · Escalations to the human DPO (Kellen)

These require his confirmation before the next revision, not just his awareness:

1. **Missing attachments.** `tt_whole_field_uc.md` and the sketch photo never reached this session. If either
   contains a specific `sort_rank` definition, a different visual layout, or scope beyond what was inferred
   from the prompt text, this build should be revisited against them.
2. **`sort_rank` is unratified.** Built fresh this session (see §6), not inherited. If a version already
   exists somewhere Kellen has that this search missed, that version should supersede the one shipped here.
3. **Visual layout — his call, a recommendation was made, not defaulted.** The static facet grid
   (`hit_direction` × `game_year`, `p_throws` colored) was built and shipped, matching the notebook-sketch
   description in his prompt. The animated-frame-on-season alternative (consistent with the platform's
   Goldsberry-style animation framework) was **not** built. Recommendation: keep the static grid for this
   single-question diagnostic — animation earns its cost on season-review UCs with many more frames of
   material, not a 4-year, single-batter directional check — but this is flagged as his call to confirm, not
   decided unilaterally.
4. **KPI vs. diagnostic-only.** Shipped as **diagnostic-only** — `sort_rank`, WF-1 (oppo_rate_ooz), and WF-2
   (pull_rate_ooz) are new, single-use, and not yet ratified into the formal KPI ledger. Standard repo practice
   is to promote to APPROVED only after independent reuse in a second UC. Recommendation: leave un-ledgered
   until then; a premature ledger entry for a not-yet-reused, provisional object would misrepresent its status.
5. **Ledger ID.** UC #42 / `uc-pos-016` was reserved and used consistently across every file in this package.
   The formal patch is `uc_ledger_AI_PATCH_uc-pos-016-turner-whole-field.md`, pending paste into the ledger
   per repo convention — this is mechanical, not a decision, but is listed here since it's the one remaining
   step needed to make the reservation durable outside this package.

## 8 · Publish recommendation

**Publish internally now, as READY-CONDITIONAL.** The analysis is sound, independently verified (33/33), and
answers the question Kellen actually asked more honestly than a confirmatory read would have. Do not promote
`sort_rank`/WF-1/WF-2 to APPROVED-KPI status yet, and do not treat the outside-zone null result as a closed
question — TWF-1 (`07`) is the tripwire for revisiting it once volume grows. External/public-facing use is not
blocked by privacy (LOW assessment) but was not the ask here and is out of scope for this delivery.
