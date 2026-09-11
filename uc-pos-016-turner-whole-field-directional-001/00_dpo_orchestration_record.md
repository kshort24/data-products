# 00 · DPO Orchestration Record — `uc-pos-016-turner-whole-field-directional-001`

**Version: v1.1.0** — the v1.0.0 text below is unchanged; the v1.1.0 delta is the amendment section appended at the end of this file.

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
the pooled 2023-2025 outside-zone pull rate (**43.3%, n=240** — *corrected 2026-09-10 in v1.1.0; this file originally read 36.7%, n=228, which disagreed with this build's own shipped `dp_uc42_significance_2026_vs_pooled.csv`. See §9.6, defect V-1. The verdict is unchanged*); |z| < 1.5 on the pooled two-proportion test. The
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

---

# 9 · v1.1.0 AMENDMENT (`dp_uc42a`, 2026-09-10)

*Everything above is v1.0.0 as delivered and is left unedited except for the one factual correction recorded
in §9.6 (V-1). This section is the delta. The v1.0.0 finding was reproduced before it was extended.*

## 9.1 · Why there is a revision

| # | Driver | Source |
|---|---|---|
| 1 | **Human-in-the-loop specification correction, declared by the human DPO himself.** The chart requested in v1 as a "spray chart" was specified as, and built as, a **pitch map** (`plate_x`/`plate_z`). A true balls-in-play spray chart on field coordinates was the intent. | Kellen, unprompted, in the revision request. He named it as his own error, not the build's — and it is recorded that way. |
| 2 | **Open decision §7-3 answered.** "Static facet grid vs. animated frames" was escalated in v1.0.0 rather than defaulted. | Kellen: **season frames**. The escalation did its job — the org held the decision open for eight hours rather than guessing, and the human's answer went the other way from the org's own recommendation. |
| 3 | **New context grain supplied.** A Plotly cell placing Turner-2026 among Phillies player-seasons (barrel rate × runs created, rug on the x-axis margin), with an explicit ask to animate a story about a single grain identified in the rug. | Kellen, in the revision request. |
| 4 | **Standing dissatisfaction with v1's interactivity.** "I was fairly disappointed with the first iteration… I am looking for something a little more interactive." | Kellen. Taken as a scope signal, not a defect report: v1 met its spec; the spec under-served the question. |

## 9.2 · What was reproduced before anything was added

The first thing this revision ran was a **parent-reproduction check**: every figure v1.0.0 published,
recomputed from v1.0.0's own shipped extract and compared row for row against v1.0.0's own shipped CSVs.
**20/20 PASS** — 1,832 BIP, all 12 rate rows, all 6 z-scores. The revision is built on the parent, not
alongside it. This follows the precedent set when `uc-pos-014` ran the parent-reproduction check on
`uc-pos-006` and it resolved *against* the parent; here it resolves *for* it.

## 9.3 · Governance gate checks (v1.1.0)

| Gate | Result |
|---|---|
| No CDE inference | Entity lock unchanged (`607208`). Six new objects (§9.4) are each defined explicitly, Rule-1 searched, and shipped provisional — none infers a business meaning. |
| No build without approved specs | The DPO's correction and his answer on §7-3 arrived as explicit instructions and are implemented as stated. One new gap (G-4, §9.5) was logged before build, not after. |
| No publish without certification | `05` §6 re-ran: **155/155**, up from 33. READY-CONDITIONAL retained with two conditions added. |
| **No breaking changes without notice** | **This gate is now live** — v1.0.0 exists to break. `version-controller` classification: **MINOR (v1.1.0), non-breaking.** Every v1.0.0 artifact remains present and valid; new artifacts are additive; no v1.0.0 column, file or figure was removed or redefined. The one changed *value* anywhere in the package is the V-1 correction (§9.6), which corrects prose to match receipts that never changed. |
| Privacy flags block external publish | Unchanged — LOW. The added fields (`plate_x`, `plate_z`, `pitch_uid`) are the same public Statcast feed at the same grain. |

## 9.4 · Six new provisional objects, all Rule-1 searched

`RC-1 runs_created_per_600` · `PM-1 pitch_location_profile` + stability test · `PM-2 zone_cell_direction_mix`
· `DC-1 directional_value_decomposition` · `slg_bip` · `pitch_uid`. Definitions, the Rule-1 evidence, and the
reason each is provisional rather than locked are in `03` §5. **None existed anywhere in the searched
repository** — and neither did any χ² test, making `PM-1` the first distributional test in this repo's
history and, on that basis alone, the one most in need of a second reuse before anyone trusts it.

## 9.5 · The finding, restated by the DPO

v1.0.0's finding stands: the premise is **not supported**, and the real shift is in-zone. v1.1.0 adds two
things that change what a reader should *do* with that finding.

1. **PM-1 answers "was it him or them" and the two halves disagree.** Inside the zone, where his batted-ball
   direction moved 7.4 points of pull rate, the 2026 pitch-location distribution is statistically
   indistinguishable from pooled 2023–25 (χ² = 7.3, df 8, **p = 0.51**). Outside the zone, where his
   direction did *not* move at all, the attack changed sharply (χ² = 72.8, df 3, p ≈ 1e−15; down-and-away
   −3.7 pp, up-and-in +4.2 pp). **The premise was aimed at the population where the pitchers changed and he
   did not.** That is a stronger statement than v1.0.0's "not supported, and underpowered" — but it does not
   repair the small sample, and the underpowered caveat is carried forward unchanged.
2. **DC-1 sizes the finding, and it is smaller than it looks.** In-zone total bases per ball in play fell
   .622 → .515. The directional mix change accounts for **20%** of that; **86%** is every direction producing
   less than it used to. The headline shift is real and it explains about a fifth of the down year. Reporting
   it without that number would have let a true finding do false work.

**This is the same falsify-before-describe discipline applied to the org's own previous answer.** The
temptation on a revision is to make the prior finding louder, because a louder finding justifies the
revision. DC-1 does the opposite, and it is the centre of the new report.

## 9.6 · V-1 — a defect in v1.0.0's own paperwork

The parent-reproduction check compares v1.0.0's receipts against a recomputation. Those agree exactly.
Reading across to v1.0.0's *prose*, three files do not:

| File | Stated | Shipped receipt |
|---|---|---|
| `dp_uc42_turner_whole_field_report.md` §1/§5 · `01_strategy_intake.md` P1 | 43%, n = 240 | ✅ agrees |
| `README.md` · **`00_dpo_orchestration_record.md` §5** · `uc_ledger_AI_PATCH_...md` | **36.7%, n = 228** | ❌ 43.3%, n = 240 |

A figure from an earlier draft survived into three summary files after the final receipts superseded it —
including the ledger patch, the one artifact meant to outlive the package. **No verdict changes**: 39.4% vs
43.3% is still z = −0.58, still inside the noise band, still not support for the premise.

**Corrected in this package** (`README.md`, §5 above, and a reissued ledger patch). **Classification: V-1,
narrative/receipt divergence; severity material** because the ledger patch would have propagated it. The live
MLB-repo ledger never received the v1.0.0 patch, so it has not propagated — paste the reissued patch, not the
original.

**The generalizable fix is now enforced, not recommended.** The verification harness gained family **F —
narrative/receipt reconciliation**: every headline figure in the report's prose and the dashboard's markup is
recomputed from the shipped receipts and string-matched against the narrative, including the report's claim
about how large the harness itself is. 46 such checks now run. This repo has verified its receipts for many
UCs; nothing until now checked that the prose agreed with them. **Recommend promoting family F to a
repo-wide practice.**

## 9.7 · Escalations to the human DPO (v1.1.0)

Carried forward, still open: **(1)** the two missing attachments and **(2)** `sort_rank`'s unratified status
— both unchanged from §7 items 1–2.

Newly opened:

3. **Six new provisional objects need a second reuse before ratification** (§9.4). `PM-1` specifically wants
   a subject whose in-zone attack *did* change, to confirm it detects what it claims to; a control test that
   has only ever returned "no change" on the arm it matters for has not been shown to work.
4. **RC-1 contradicts the requested chart's own title.** The supplied cell is titled *"Trea is creating runs
   for a player of his Barrel Rate Profile."* On the normalized axis that does not hold for 2026: 53.5 runs
   created per 600 PA at a .064 barrel rate, against Bohm's 87.1 at a **lower** .060. The title was left off
   the shipped chart and the chart is titled for what it shows. **Flagged rather than silently dropped** —
   if the intended claim was about a different window or a different denominator, say so and it can be
   priced properly.
5. **Family F promotion** (§9.6) is a repo-wide practice change and therefore the DPO's call, not this
   build's.
6. **Ledger patch reissue** supersedes the v1.0.0 patch. Mechanical, but listed because the original carries
   V-1.

## 9.8 · Publish recommendation (v1.1.0)

**Publish internally now, READY-CONDITIONAL.** The revision does what the escalations asked, corrects a
defect in its own predecessor's paperwork, and reports a result that makes its own headline finding smaller.
Do not ratify any of the six new objects yet. Do not treat the out-of-zone null as closed — TWF-1 remains the
tripwire.
