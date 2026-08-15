# Use Case Validator — Gap Report

**Use case under review:** `uc-pos-010-stott-approach-change-001` — Bryson Stott 2026 Approach-Change Diagnostic
<br>**Submitted:** 2026-08-15 · **Reviewed:** 2026-08-15 · **Validator pass:** 1 (revised post-repo-search)
<br>**Reviewed against:** `Use Case Template.md` · `BASEBALL_FUNCTIONS_INTAKE_REGISTER_v2_2026-07-24.md` ·
`contract/uc-pps-rangel-scouting-001.contract.yaml` · `dp_uc7` · `dp_uc17` · `uc-cat-001` ·
`uc-pos-002` · `uc-pos-003` · `uc-pos-004` · `uc-pos-stott-qab-001`

> **Charter reminder.** This agent surfaces gaps. It does not fill them, does not infer business
> intent, and does not resolve ambiguity. Every issue below returns to the Data Product Owner.

> **Revision note.** This report was substantially rewritten after a repo-wide search of shipped
> artifacts. The first pass raised six blocking issues reasoning from the submitted document alone.
> **Three of those six were wrong**, and wrong in the direction that matters: they treated as
> *undefined* things the repo had already defined and, in one case, formally **approved**. The
> corrections are recorded inline rather than quietly overwritten, because the failure mode is
> instructive — *a validator that reasons only from the submitted document will manufacture gaps
> and miss duplications.* Searching the repo is not optional diligence; it is the job.

---

## Verdict

# 🔴 NO-GO

**Five blocking issues** — down from six, and materially re-shaped.

The submitted use case is unusually complete on structure: value stream unambiguous, six phased
business questions, five personas mapped to actions, sixteen CDEs across six domains, CDE-level DQ
expectations decoupled from KPI output, and eleven self-surfaced open items. That candour is worth
crediting and is why the no-go is narrow rather than sweeping.

**But the dominant finding of this pass is not incompleteness — it is duplication.** The submission
proposed three new functions. The repo already contains **two of them**:

| Proposed as new | Actually | Evidence |
|---|---|---|
| `fpsr(level, df)` — AP-1 | **Already exists and is APPROVED** | `dp_uc17` L211; inherited `dp_uc11` → `dp_uc8`; `cde.fpsr` **status: approved** in the Rangel contract; verified to ±.004 in `dp_uc17_verification.py`; reused in `dp_uc19` |
| swing classification — AP-2 | **Already exists — in three declarations, two of which disagree** | `dp_uc7` L191/L200 (8 values) vs. `dp_uc7` L437 (7 values) vs. `uc-pos-002` `_SWING_DESCS`; `uc-cat-001` cites `Baseball Functions.ipynb` cell 21 as canonical |
| 40-PA reliability floor | **Contradicts the standing 50-PA standard** | `phillies-data-analyst` data-quality standard; applied as 50 PA in `uc-pos-004` and `uc-pos-006`; `uc-pos-002`'s 20 PA is a documented *situational exception*, not the norm |

That reframes the gate. This is not a use case with a hole in its foundation. It is a use case that
**proposed to rebuild foundations that already exist** — which Intake Register §8 Principle 1 names
as a governance failure *even when every proposed definition is defensible*.

---

## Blocking Issues

### B-1 · Three conflicting canonical SWINGS lists exist in shipped code
**Field:** Data Specification → Derived Metrics → AP-2 function contract; Business Glossary → "Swing"

*Reclassified from pass 1, which held that no classifier existed anywhere. It exists. It exists
three times.*

The AP-2 contract defines its numerator as *"pitch rows whose `pitch_result_description` indicates
the batter offered."* That is circular at the point of implementation, and the submission enumerates
nothing. But the repo does — and that is the actual problem:

| Declaration | Values | Location |
|---|---|---|
| `chase_rate` / `whiff_rate` swings list | **8** — `foul`, `foul_bunt`, `foul_tip`, `hit_into_play`, `missed_bunt`, **`swinging_pitchout`**, `swinging_strike`, `swinging_strike_blocked` | `dp_uc7_wheeler_mets.py` L191, L200 |
| `is_swing` derivation | **8** — identical to above | `uc-cat-001/03_technical_lineage.json` L105 |
| `SWINGS` constant | **7** — same list, **`swinging_pitchout` absent** | `dp_uc7_wheeler_mets.py` L437 |
| `_SWING_DESCS` | third independent declaration | `uc-pos-002/risp_2out_vulnerability_index.py` L77 |

`uc-cat-001`'s lineage cites *"`Baseball Functions.ipynb` cell 21 canonical lists"* as the
authority — so a canonical list does exist upstream, and **two declarations inside a single file
have already drifted from each other.**

**Why this is blocking rather than housekeeping.** The divergence is `swinging_pitchout`, which is
vanishingly rare. The two lists will produce identical numbers in almost every dataset. **A silent
disagreement that almost never shows up is worse than a loud one**, because no value comparison
will catch it and reuse will propagate it — Intake Register §8 Principle 4 exactly: *reuse
propagates a defect; it does not detect one.*

The submission's own DQ rule — *"every distinct value must map to exactly one of {swing, take}…
under the ratified classifier; an unmapped value is a blocking DQ failure"* — is well-aimed but
currently untestable, because "the ratified classifier" resolves to three candidates.

**Compounding factor — verification independence.** House pattern requires
`dp_uc33_verification.py` to recompute headlines from inline masks without importing the build's
kernel. If build and verification each reach for a different one of these three lists, the PASS/FAIL
reflects a definitional fork rather than a build defect — assurance-shaped, but not assurance.

**This is a pre-existing repo condition, not a defect introduced by this UC.** It is raised here
because this UC is the first to require an *unconditioned* swing rate and therefore the first that
cannot route around it.

---

### B-2 · AP-1 proposes a new function that duplicates an **approved** governed term
**Field:** Data Specification → Derived Metrics → AP-1 function contract *(supersedes submission O-1)*

*Reversed from pass 1, which accepted the submission's framing that the `fpsr` numerator was an open
question. It is not open. It was settled and approved before this UC was written.*

The submission marks AP-1 as **NEW-CANDIDATE**, specifies a fresh `fpsr(level, df)` contract, and
raises numerator membership as open DPO decision 1, offering three candidate definitions.

**`fpsr` already exists, is in continuous production use, and is formally approved:**

- **Implementation:** `dp_uc17_luzardo_first_half.py` L211 — `def fpsr(level, df)`, already on the
  `(level, df)` contract, output column `first_pitch_strike_rate`.
- **Formula:** `(m.pitches − m.balls) / m.pitches` over `pitch_number == 1` — the complement of a
  ball. **That is option (a)**, the received definition the submission recommends but treats as
  undecided.
- **Provenance:** inherited `dp_uc8` → `dp_uc11` → `dp_uc17` → `dp_uc19`.
- **Governance status:** `contract/uc-pps-rangel-scouting-001.contract.yaml` records
  `cde.fpsr` — *"First-Pitch Strike Rate"* — **`status: approved`**, with a bound implementation
  hash. `uc-pps-017/03_governance.md` lists FPSR among *"locked terms… consumed as-is from the
  Baseball Functions kernel."*
- **Verification:** `dp_uc17_verification.py` asserts it to ±.004 against shipped receipts.

Building a second `fpsr` would create two implementations of an approved locked term — the exact
condition Intake Register §8 Principle 1 exists to prevent, and a materially worse instance than
the `pulled_air` / `pulled_air_rate` case still open in Register §5, because here one side is
already **contract-bound**.

**What is legitimately new, and what the submission should have said instead.** Every prior use of
`fpsr` is **pitcher-side (`pps`)** — `uc-pos-004` states plainly that *"pps UCs' FPSR/CSW are
pitcher-side."* This UC is the **first batter-side (`pos`) consumption**. The arithmetic is
identical; the subject of the sentence inverts — it now describes what pitchers did *to* Stott.
That inversion is real, it is the entire justification for RC-4's panel separation, and it warrants
a **value-stream context annotation on the existing glossary entry**. It does not warrant a
function.

**Why this remains blocking despite being a downgrade in difficulty.** Consuming an approved
cross-stream term is a governance action requiring DPO acknowledgement and a
`business-glossary-agent` annotation, and `version-controller` must record the reuse as
non-breaking. None of that has happened, and the submission is currently instructing
`data-engineer` to build a duplicate. **The cost of clearing this is minutes; the cost of not
clearing it is a forked approved term.**

---

### B-3 · `month` is a declared grain attribute with no declared derivation
**Field:** Data Specification → Analytical Grain; Business Glossary → "Month" *(submission O-4)*

`level = ['player_name','game_year','month']`. `month` is one of three attributes that define a row,
and the document does not state whether it is native to `pos` or derived from `game_date`, whether
it is calendar month or month-of-season, or whether the conventional March/April merge is applied.

**A declared grain whose attributes are not reproducibly derivable is not a declared grain.** That
is the validator's canonical blocking condition, and it applies verbatim here.

The consequence is concrete rather than theoretical. If 2026 opened in late March and those games
sit in `pos`, the frame gains a two-or-three-game "month 3" bucket. That bucket will fall below every
reliability floor in the document, will render as an axis point on the delivered figure, and — because
the AP-4 anchor is defined as *"the April bucket"* — will sit **outside the anchor and outside the
four-month window simultaneously**, belonging to neither the baseline nor the analysis. Alternatively
it folds silently into April and shifts the anchor every AP-4 delta is measured from.

Both outcomes are defensible. Only one can be true, and the document does not say which.

The DQ table's consistency rule — *"`game_month` must equal the month derived from `game_date`"* —
is well-aimed but cannot be written until this is settled: under a March/April merge convention the
rule is *expected* to fail for March rows, and the rule as stated would flag correct data.

---

### B-4 · `swing_rate` should extend `discipline()`, not stand beside it — and the check still cannot be performed
**Field:** Data Specification → Derived Metrics → open decision 2 *(submission O-2)*

`discipline(level, df)` (Intake Register B1, disposition **A** — ready for sign-off) already emits
`chase_rate` and `whiff_rate`. Neither is computable without an internal swing classifier. It simply
does not expose the **unconditioned** rate, which is the one thing AP-2 needs.

The risk is sharper than generic duplication. If a standalone `swing_rate` and `discipline()`'s
internal classifier diverge — and B-1 establishes that three candidate lists are in circulation, so
divergence is the *default* outcome, not the edge case — then **`swing_rate` and `whiff_rate` will
contradict each other inside the same delivered row of `z`**. The hitter's swing count will not
reconcile with the denominator of his own whiff rate. That is an internal-consistency defect visible
to the consumer, in a document whose entire purpose is to let a coach read the approach panel as a
coherent whole.

**The remedy is structural:** `swing_rate` should be an **additional output column of the existing
discipline family**, consuming the same classifier, rather than a parallel function. That guarantees
reconciliation by construction instead of by assertion.

The submission is transparent that `discipline()`'s body could not be read because the notebook
lives in the MLB repo, outside this folder. **That is an accurate report of a limitation, not a
resolution of it.** The check remains outstanding and is correctly assigned to
`domain-steward-proxy` in the submission's own Agent Assignments table, marked *"required to clear a
blocking issue."*

---

### B-5 · The PA floor contradicts the standing repo standard
**Field:** Data Specification → Data Quality Expectations → Reliability floors

*Re-scoped from pass 1, which compared the submission only against `uc-pos-002` and reached the
wrong reference point.*

The submission sets **40 PA**. The standing standard is **50 PA**, and `uc-pos-002`'s 20 PA — which
pass 1 treated as the competing precedent — is neither the standard nor a competitor. It is a
documented exception:

- **The standard:** the `phillies-data-analyst` data-quality reference specifies a **50-PA minimum
  for batter rate stats** (wOBA, xwOBA, barrel%), quoted as such in `uc-pos-003`'s gap report.
- **In practice:** `uc-pos-004` — *"July is soft: .336 wOBA, 2 HR in 48 PA — below the 50-PA floor,
  directional only."* `uc-pos-006` applies the same 50-PA floor to a hitter-season review at
  comparable grain.
- **The exception:** `uc-pos-002`'s 20-PA floor was raised **by its own validator** as a deviation
  from the 50-PA standard, and the DPO honored it explicitly for *situational* buckets — RISP/2-out
  slices running ~30–70 PA for an everyday hitter — with a mandated low-confidence band for 20–49
  PA. That reasoning does not extend to calendar-month buckets, which run 70–120 PA.

**So 40 PA matches nothing.** It is below the standard that governs this exact metric family at this
exact grain, and above an exception granted to a population this UC does not belong to. It is a
third value, chosen independently — Principle 1's failure mode in its purest form.

**The fix is inheritance, not adjudication:** adopt **50 PA**. This UC's population is a
full-season-slice monthly bucket, directly analogous to `uc-pos-004`'s and `uc-pos-006`'s. No new
ruling is required for the PA floor at all.

**What does still require ratification** are the three floors with no repo precedent: **190 pitches**
(derived from 50 PA × ~3.8 P/PA — a defensible derivation, but the multiplier is asserted and should
be re-derived from `ppa`, Register B7), **25 BIP**, and **40 BIP for EV90**. The EV90 floor is the
one the submission argues for explicitly — *"a 90th-percentile estimator is far more sample-sensitive
than a mean"* — and that argument is correct, which makes the silence on the other two conspicuous.

These floors determine which months a coach is permitted to read as real. They are load-bearing on
the decision, not presentational. The durable fix — and the one that would also close `uc-pos-003`'s
still-open OD-4 — is to ratify a general *"minimum denominator by metric family at a bucketed
grain"* standard rather than continue settling it per-UC.

---

### B-6 · Key Results state no target values
**Field:** Business Context → Expected Outcomes

The template is explicit: *"The Key Result must reference a specific KPI named above, with a
**baseline**, a **target**, and a **timeframe**. If a baseline isn't known yet, write 'baseline to be
established from [dataset/source]'."*

The submission complies on baselines — both use the sanctioned "to be established from `pos`"
formulation, which is the correct handling of an unknown baseline and is credited as such. It
complies on timeframe for KR-1 ("before the end of the 2026 regular season"). **It does not state a
target on any Key Result.**

- **KR-1** promises a directional move *"of a magnitude the Analyst can classify as inside or
  outside monthly noise."* That is a **procedure for evaluating a result**, not a result. It cannot
  fail. Any observed value satisfies it, because classification will always be possible.
- **KR-2** promises that AP-5 *"is reported for every month in scope with an explicit in-band /
  out-of-band call."* That is a **deliverable-completeness check**, not an outcome. It measures
  whether the report was written, not whether anything improved.
- **KR-3** is the strongest of the three — it names concrete artifacts (three `(level, df)` functions,
  a passing verification script, an Intake Register entry within one review cycle) and is genuinely
  checkable. It is, however, a **process** outcome about the data product's own construction, not a
  business outcome about Stott or the coaching decision.

The template's baseline escape hatch exists so an unknown *starting point* does not block intake.
There is no equivalent escape hatch for an unstated *target*, and the omission is not cosmetic:
`certification-agent` has nothing to audit acceptance against, and the DPO has no defined condition
under which this data product is judged to have worked.

**This is the cheapest of the six blocks to clear** — plausibly a single DPO sitting — but it cannot
be cleared by an agent, because setting a target is a statement of business intent and this agent
does not infer business intent.

---

## Non-Blocking Issues

| # | Field | Issue | Suggested assumption *(requires DPO acknowledgement)* |
|---|---|---|---|
| **N-1** ✅ | Data Spec → Semantic Mapping | **Largely closed by repo search.** Pass 1 flagged 11 of 16 CDEs as `*unmapped*`. Eight are recoverable from shipped artifacts: `events`, `pitch_number`, `launch_speed`, `launch_angle`, `game_pk`, `at_bat_number` (`uc-pos-stott-qab-001`); `description`, `zone` with the `zone <= 9` in-zone convention (`uc-cat-001` lineage); `estimated_woba_using_speedangle` restricted to `type == 'X'` (Register §4.3). | The submission's caution about not fabricating physical names was right in principle but over-applied — **these names were discoverable, not unknowable.** `metadata-mapper` should now *confirm* against the live `pos` schema rather than re-derive. Residual genuinely-unmapped: the run-creation constants key. Blocks nothing. |
| **N-2** | Derived Metrics → AP-4 | Composite index vs. independent per-metric deltas undecided. *(O-3)* | Adopt the submission's recommendation: **report independently**. Rationale is sound and matches UC-POS-002's handling of the Approach Degradation Index. A composite permits sign-cancellation — a hitter who chases less *and* swings less in the zone nets to "no change" while having changed materially. Record as a DPO ruling, not an agent default. |
| **N-3** | Derived Metrics → AP-5 | Divergence band population uncalibrated — all pos hitters, qualified hitters, or Stott's own prior seasons. *(O-5)* | Default to **Stott's own prior seasons** as the primary band with a population band reported alongside. Self-referential comparison is the established pattern from the Marsh ghost-line build and matches the self-scout framing. Ship the raw monthly `woba − xwobacon` values regardless, so the read survives a later recalibration. |
| **N-4** | Derived Metrics → AP-5 | AP-5 introduces `xwobacon`, which is **not** in the requester's supplied `kpis` list. This is a validator-visible scope addition, not a requested metric. | Accept. It is the only metric in the document that answers BQ-6, it is a ratified governed KPI (Register §4.3), and the requester's framing ("assess the facts" before interpreting) implies the process read. **But it is an addition the DPO must consciously accept, not inherit.** |
| **N-5** | Business Questions → BQ-2 | BQ-2 asks whether the improvement is *monotonic* or an endpoint artifact. **No KPI in the document tests trend shape.** BQ-2 is currently answerable only by eyeballing the figure. | Either inherit **RF-1 (`running_line`, trajectory)** from uc-pos-006 — already specified, already verified 33/33, disposition C pending one more hitter reuse, and this would *be* that reuse — or explicitly downgrade BQ-2 to a narrative observation. Do not leave it as an unanswerable question in an approved use case. |
| **N-6** | Business Questions → BQ-5 | BQ-5 asks whether the *pitcher's* approach changed; `fpsr` alone is a thin proxy. Pitch mix, zone rate, and first-pitch pitch-type would materially strengthen it. | Accept the thin read for this delivery — the document concedes it is "the cheapest available read" and labels it honestly. Record as a known scope limitation and a candidate follow-on UC. |
| **N-7** | Derived Metrics → AP-4 | Every AP-4 delta is measured from a **single month's** value. The April anchor carries the same monthly sampling noise as every month compared to it, so every delta inherits the anchor's error — and April was selected precisely *because* it was extreme, which is the textbook setup for regression-to-the-mean to masquerade as improvement. | Report AP-4 deltas against **both** the April anchor and a season-to-date-excluding-April baseline. The divergence between the two is itself the regression-to-the-mean read that assumption A-8 calls for but no metric currently delivers. |
| **N-8** | Governance → Access & Usage Controls | "Player (Bryson Stott)" is an authorized persona for a product whose stated Actions include **A-3 (adjust batting-order slot)** and **A-4 (adjust platoon deployment)** — decisions made *about* him. The document does not address the access asymmetry. | Split the delivery: a full artifact for staff personas, and the persona-specific guide from `consumer-onboarding-agent` as the Player-facing surface, scoped to his own approach metrics and excluding the deployment-decision framing. Route to `privacy-watchdog` for confirmation rather than deciding here. |
| **N-9** | Implementation → Data Flow; Canonical Datasets | Four defects in the submitted draft code: `zfig = z[level+kpis]` drops all three new KPI columns *(O-6)*; merge suffix behaviour is accidental rather than specified *(O-7)*; syntax errors — unbalanced parens, `suffixes` passed as two positional strings rather than a tuple, `px.scatter` closing `sort_values(` early *(O-8)*; figure title "wOBA by Season" contradicts a month-axis single-season encoding *(O-9)*. | All four are correctly identified in the submission and none requires a business decision. Assign to `data-architect` (explicit output column naming, replacing suffix mechanics) and `data-engineer` (syntax, title). **O-6 is the one worth watching** — it fails silently and produces a plausible-looking figure with the headline approach metrics absent. |
| **N-10** | Semantic Mapping | Ten KPIs in the `kpis` list have no display label; `month` has neither label nor formatter and will render as integers 4–8. *(O-10)* | Assign to `data-dictionary`. Note that RC-6 and the Usability Requirements both depend on this being closed, so it is not cosmetic — but it is mechanical and blocks nothing upstream. |
| **N-11** ◐ | Identity block; Process Tracking | **Half closed.** The `data-products/` listing confirms `uc-pos-009-schwarber-swing-decay-001` is the highest `pos` slug, so **`uc-pos-010` is correct and free.** The `dp_uc33` build prefix remains unverified — it lives in the MLB repo. *(O-11)* | Slug: cleared, proceed. Build prefix: still verify via `ls dp_uc*` before naming artifacts. One command; prevents a collision that is expensive to unwind after receipts are written. |
| **N-15** ⚠ | Identity block → Relationships; Business Context | **A prior use case on this exact subject player was not referenced at intake.** `uc-pos-stott-qab-001` (Quality At-Bat Rate, piloted on Bryson Stott, created 2026-06-30, **status Draft**) exists in `data-products/` with an implemented `qab_rate.py`, an engineering design, and its own gap report. The submission's `related_use_cases` listed five UCs and omitted the one about the same hitter. | Add it as a related UC and have the DPO make two calls: **(a)** whether **QAB Rate belongs in the results panel** — it is arguably the aptest "did he actually get better" metric available and is already implemented; **(b)** whether that UC's unresolved open items (notably its 810 → 1500 component-reconciliation gap) bear on anything reused here. A prior UC on the same subject is the highest-value reuse signal available at intake and should be a standing search step, not a discovery. |
| **N-12** | Derived Metrics → `runs_created` | `runs_created` depends on `wrc(level, df, constants)` — Intake Register **B6, disposition B**, blocked on a documented constants loader that is itself an open item in Register §5. The dependency is on an artifact that does not yet exist. | Accept the submission's degradation path: emit **NULL** with disclosure if the loader is unavailable. Never approximate. Retain the standing labels — **never `wRC+`**, and in-season 2026 constants carry ±2%. |
| **N-13** | Assumptions & Constraints → A-5 | A-5 names opponent quality and platoon mix as *"the single largest interpretive limitation in the document"* — but `p_throws` is optional grain and opponent identity is not a CDE, so **the caveat cannot be evidenced or inspected from the delivered dataset.** The reader is asked to trust a limitation they have no means to check. | Ship a **context-only** monthly summary — opponent-handedness mix and a coarse opposing-pitcher-quality indicator — as non-grain columns on `z`. This does not change the declared grain and it makes the document's most important caveat auditable rather than rhetorical. |
| **N-14** | Delivery → Delivery Cadence; Business Glossary → April Anchor | The product is specified for monthly re-run, but the **anchor is not pinned across re-runs**. "Last 4 months" is a date-relative window; on a September re-run it becomes Jun–Sep and April leaves the window while remaining the anchor. Nothing in the document states that April stays the anchor permanently. | Pin the anchor explicitly: **April 2026 is the anchor for every re-run of this UC**, independent of the rolling window. Generalize the glossary term to *"anchor month — the fixed baseline bucket, declared once at intake and immutable across re-runs."* |

---

## Rationale

**Structurally, this use case is among the more complete submissions to reach intake.** Every
template section is populated. The value stream is unambiguous (`pos`). Six business questions are
specific and phased, with Phase 1 (establish the facts) correctly gating Phase 2 (interpret them) —
that sequencing is a genuine strength and it mirrors the requester's own stated instruction. Five
personas are named with descriptions and mapped to specific business questions and actions. Sixteen
CDEs are identified across six domains. CDE-level DQ expectations are populated independently of KPI
output, which is exactly the decoupling the template asks for and which most submissions get wrong.
The document surfaces eleven of its own open items rather than concealing them.

**The no-go is not a judgement on that quality. It is a consequence of what the repo already
contains.**

The single most useful finding of this pass is that **the submission reasoned carefully in
isolation.** It defined `fpsr` from first principles and correctly derived — as an open question —
the very definition already shipped, verified, and contract-approved four use cases ago. It flagged
a possible collision between `swing_rate` and `discipline()` while three swing lists sat in the
repo, two of them in the same file and disagreeing. It chose a 40-PA floor while a 50-PA standard
governed the identical metric family at an analogous grain in two neighbouring UCs. Each individual
judgement was defensible. **The aggregate failure was not analytical — it was that no one searched.**

That is what Intake Register §8 Principle 1 protects against, and it is why it is worded as it is:
*two UCs independently choosing plausible values for the same quantity is a governance failure even
when both are defensible.* This submission is a clean instance, and it is worth recording as a
process finding rather than only a document finding: **the intake workflow needs a mandatory
repo-search step before any KPI may be declared new** — grep the function name, grep the term, list
`data-products/` for the subject entity. Three commands, ahead of a spec that would otherwise
instruct `data-engineer` to fork an approved term.

**What remains genuinely open** is narrower than pass 1 suggested. B-3 (`month` derivation) is a
true gap — a grain attribute with no declared derivation, and the validator's canonical blocking
condition. B-1 is a **pre-existing repo condition** this UC is simply the first to be unable to
route around, since it is the first to need an unconditioned swing rate. B-6 (no target values) is a
template-compliance gap that only the DPO can fill, because setting a target is a statement of
business intent. B-2 and B-5 are now *reuse instructions* rather than open questions — the answers
exist; the submission needs to adopt them.

**On the work that can proceed in parallel:** `source-system-profiler` can characterise the CDEs,
`metadata-mapper` can now *confirm* eight recovered physical names rather than derive them,
`privacy-watchdog` can confirm the Internal classification, and `data-dictionary` can close the
label gap. **But `kpi-calculator` cannot produce a calculation spec while three swing lists compete,
`dq-rule-definer` cannot write the rule the document itself calls blocking, and `data-engineer`
cannot build.** Layer 2 is blocked at its core even where its periphery is open.

**On why this is the cheap moment.** AP-2 and AP-3 are new and unratified with no consumers. The
submission's own Backward Compatibility note gets this right: *"breaking changes are cheap now and
expensive after promotion."* Once `swing_rate` lands in the notebook and a second hitter UC inherits
it, resolving B-1 becomes a restatement obligation across every downstream artifact — the same shape
as the `OUTS_MAP` cascade onto `uc-pps-021`. Principle 4 is the relevant warning: *reuse propagates
a defect; it does not detect one.* One DPO sitting now, or a restatement later.

**On B-5 specifically.** Pass 1 flagged the floors as blocking by comparing against `uc-pos-002`'s
20 PA and calling it a Principle 1 conflict. That was the right principle applied to the wrong
reference. `uc-pos-002`'s 20 PA is a documented DPO exception for situational buckets, raised by its
own validator as a deviation from the standard. The standard is **50 PA**, applied as such in
`uc-pos-004` and `uc-pos-006`. The submission's 40 PA matches neither — it is a third value. The
issue stays blocking, but the remedy is **inheritance, not adjudication**: adopt 50 and move on. Only
the three unprecedented floors (190 pitches, 25 BIP, 40 BIP for EV90) need a ruling.

**What this use case gets right and should be preserved through revision:**

- The separation of *hitter approach* from *pitcher intent* (RC-4) is the correct architecture for
  BQ-5's confound and should not be collapsed for presentational convenience.
- Shipping denominators alongside every rate (RC-3) directly serves the small-sample reality of a
  monthly grain.
- Naming regression-to-the-mean as the **null hypothesis** (A-8) rather than an afterthought is the
  single most important line in the document. N-7 exists only to give that assumption a metric.
- Refusing to fabricate physical column names (N-1) is correct practice and consistent with
  precedent.
- Treating the requester's "grown steadily" as a **hypothesis to test** rather than a fact to
  illustrate (BQ-2, Additional Context) is the discipline that makes this diagnostic worth building
  at all — and it is also why N-5 matters: the question deserves a metric, not an eyeball.

**Recommended path to go — one DPO session plus one notebook read:**

| # | Action | Effort |
|---|---|---|
| B-2 | **Rewrite AP-1 as inherited, not new.** Consume `fpsr` as-is; add a value-stream context annotation to the approved `cde.fpsr` entry; have `version-controller` record the cross-stream reuse as non-breaking. | minutes |
| B-5 | **Adopt the 50-PA standard.** Ratify the three unprecedented floors (190 pitches / 25 BIP / 40 BIP for EV90), ideally as a general by-metric-family rule that also closes `uc-pos-003` OD-4. | one ruling |
| B-1 | **Ratify one canonical SWINGS list** against `Baseball Functions.ipynb` cell 21; retire the two divergent declarations in `dp_uc7`. Note this is a **repo-wide** fix affecting every consumer of `chase_rate` / `whiff_rate`, not a fix scoped to this UC. | one ruling + cleanup |
| B-3 | **Declare the `month` derivation** — native vs. from `game_date`, calendar vs. season month, March/April merge convention. | one ruling |
| B-6 | **State a target on each Key Result.** Cannot be delegated: setting a target is business intent. | one sitting |
| B-4 | **Read `discipline()` in the MLB notebook**; confirm whether `swing_rate` can be an added output column rather than a parallel function. | one read |
| N-15 | Decide whether **QAB Rate** from the prior Stott UC joins the results panel. | one call |

Five of the six blocking items require **no new information — only decisions**, and two of those
decisions are simply "use what already exists."

**Resubmit for validator pass 2.**

---

## Output Contract

```json
{
  "go_no_go": "no-go",
  "validator_pass": "1 (revised after repo-wide search; three pass-1 blocking issues were incorrect and are corrected here)",
  "blocking_issues": [
    {
      "field": "Data Specification > Derived Metrics > AP-2 function contract; Business Glossary > Swing",
      "issue": "Three conflicting declarations of the canonical SWINGS list exist in shipped repo code: dp_uc7_wheeler_mets.py L191/L200 and uc-cat-001/03_technical_lineage.json use an 8-value list including swinging_pitchout; dp_uc7_wheeler_mets.py L437 (SWINGS) uses the same list WITHOUT swinging_pitchout; uc-pos-002/risp_2out_vulnerability_index.py L77 declares _SWING_DESCS independently. uc-cat-001 cites 'Baseball Functions.ipynb cell 21 canonical lists' as the authority, so two declarations in a single file have already drifted. The divergence is a rare description value, so the lists will almost always agree numerically — a silent disagreement no value comparison will catch, and Principle 4 warns that reuse propagates rather than detects it. The submission's own DQ rule tests conformance against 'the ratified classifier', which currently resolves to three candidates. Independent verification may reach for a different list than the build, producing a PASS/FAIL that reflects a definitional fork. This is a pre-existing repo condition, not a defect introduced by this UC, but this UC is the first to require an unconditioned swing rate and so the first that cannot route around it."
    },
    {
      "field": "Data Specification > Derived Metrics > AP-1 function contract",
      "issue": "AP-1 is specified as NEW-CANDIDATE with an open numerator decision. fpsr already exists and is APPROVED. Implementation: dp_uc17_luzardo_first_half.py L211, def fpsr(level, df), already on the (level, df) contract. Formula: (pitches - balls) / pitches over pitch_number == 1 — the complement of a ball, which IS the option (a) the submission recommends but treats as undecided. Provenance dp_uc8 -> dp_uc11 -> dp_uc17 -> dp_uc19. Governance: contract/uc-pps-rangel-scouting-001.contract.yaml records cde.fpsr status approved with a bound implementation hash; uc-pps-017/03_governance.md lists FPSR among locked terms consumed as-is. Verified to +/-.004 in dp_uc17_verification.py. Building a second implementation would fork a contract-bound approved term — a worse instance of the Principle 1 failure than the still-open pulled_air case, because one side here is contract-bound. What IS legitimately new: every prior use is pitcher-side (pps); uc-pos-004 states 'pps UCs FPSR/CSW are pitcher-side'. This is the first batter-side (pos) consumption. That inversion justifies RC-4's panel separation and warrants a value-stream context annotation on the existing glossary entry — not a new function. Remains blocking because cross-stream reuse of an approved term requires DPO acknowledgement, a business-glossary-agent annotation, and a version-controller non-breaking classification, none of which have occurred, while the spec currently instructs data-engineer to build a duplicate."
    },
    {
      "field": "Data Specification > Analytical Grain; Business Glossary > Month",
      "issue": "month is one of three declared grain attributes and has no declared derivation — native vs. derived from game_date, calendar month vs. month-of-season, and whether the March/April merge convention applies are all unstated. A declared grain whose attributes are not reproducibly derivable is not a declared grain. If March games exist in pos, the resulting bucket falls below every reliability floor, renders on the delivered axis, and sits outside both the April anchor and the four-month window. The DQ consistency rule (game_month must equal month derived from game_date) cannot be written until this is settled, since under a merge convention it is expected to fail for March rows. This is the one pass-1 blocking issue that survives unchanged — a true gap, not a duplication."
    },
    {
      "field": "Data Specification > Derived Metrics > open decision 2",
      "issue": "discipline(level, df) (Intake Register B1, disposition A) already emits chase_rate and whiff_rate and must already classify swings internally; it simply does not expose the unconditioned rate, which is the one thing AP-2 needs. Given B-1 establishes three competing lists, divergence between a standalone swing_rate and discipline()'s internal classifier is the default outcome rather than the edge case — in which case swing_rate and whiff_rate will contradict each other inside the same delivered row of z, with the hitter's swing count failing to reconcile against the denominator of his own whiff rate. Remedy is structural: swing_rate should be an additional output column of the existing discipline family, guaranteeing reconciliation by construction. The submission accurately reports that discipline()'s body could not be read because the notebook is outside this repo; that is a report of the limitation, not a resolution. Correctly assigned to domain-steward-proxy in the submission's own Agent Assignments table."
    },
    {
      "field": "Data Specification > Data Quality Expectations > Reliability floors",
      "issue": "The submission sets 40 PA. The standing standard is 50 PA — the phillies-data-analyst data-quality reference specifies a 50-PA minimum for batter rate stats, quoted in uc-pos-003's gap report and applied as 50 PA in uc-pos-004 ('July is soft: .336 wOBA, 2 HR in 48 PA — below the 50-PA floor, directional only') and uc-pos-006 at analogous grain. uc-pos-002's 20-PA floor is NOT a competing precedent: it was raised by its own validator as a deviation from the 50-PA standard and honored by the DPO explicitly for situational RISP/2-out buckets running ~30-70 PA, with a mandated low-confidence band for 20-49 PA. Calendar-month buckets run 70-120 PA and do not belong to that exception. So 40 PA matches nothing — a third independently chosen value, Principle 1's failure mode in pure form. Remedy is inheritance, not adjudication: adopt 50 PA; no new ruling needed for the PA floor. What DOES require ratification are the three floors with no repo precedent: 190 pitches (derived as 50 PA x ~3.8 P/PA — defensible derivation but the multiplier is asserted and should be re-derived from ppa, Register B7), 25 BIP, and 40 BIP for EV90. These floors determine which months a coach may read as real; they are load-bearing on the decision. The durable fix — which also closes uc-pos-003 OD-4 — is a general 'minimum denominator by metric family at a bucketed grain' standard rather than continued per-UC settlement."
    },
    {
      "field": "Business Context > Expected Outcomes",
      "issue": "No Key Result states a target value. The template requires baseline, target, and timeframe, and provides an escape hatch only for unknown baselines. KR-1's 'a magnitude the Analyst can classify as inside or outside monthly noise' is a procedure for evaluating a result, not a result, and cannot fail. KR-2's 'reported for every month with an explicit in-band/out-of-band call' is a deliverable-completeness check, not an outcome. KR-3 is checkable but is a process outcome about the data product's construction rather than a business outcome. certification-agent has no acceptance criteria to audit against. Cannot be cleared by an agent: setting a target is a statement of business intent."
    }
  ],
  "non_blocking_issues": [
    {
      "field": "Data Specification > Semantic Mapping",
      "issue": "LARGELY CLOSED by repo search. Pass 1 flagged 11 of 16 CDEs as unmapped. Eight are recoverable from shipped artifacts: events, pitch_number, launch_speed, launch_angle, game_pk, at_bat_number (uc-pos-stott-qab-001); description and zone with the zone <= 9 in-zone convention (uc-cat-001 lineage); estimated_woba_using_speedangle restricted to type == 'X' (Register 4.3).",
      "suggested_assumption": "The submission's caution about not fabricating physical names was right in principle but over-applied — these names were discoverable, not unknowable. metadata-mapper should now confirm against the live pos schema rather than re-derive. Residual genuinely-unmapped: the run-creation constants key. Blocks nothing."
    },
    {
      "field": "Identity block > Relationships; Business Context",
      "issue": "A prior use case on this exact subject player was not referenced at intake. uc-pos-stott-qab-001 (Quality At-Bat Rate, piloted on Bryson Stott, created 2026-06-30, status Draft) exists in data-products/ with an implemented qab_rate.py, an engineering design, and its own gap report. The submission's related_use_cases listed five UCs and omitted the one about the same hitter.",
      "suggested_assumption": "Add it as a related UC and have the DPO make two calls: (a) whether QAB Rate belongs in the results panel — it is arguably the aptest 'did he actually get better' metric available and is already implemented; (b) whether that UC's unresolved open items (notably its 810 -> 1500 component-reconciliation gap) bear on anything reused here. A prior UC on the same subject is the highest-value reuse signal available at intake and should be a standing search step, not a discovery."
    },
    {
      "field": "Data Specification > Derived Metrics > AP-4",
      "issue": "Composite index vs. independent per-metric deltas is undecided.",
      "suggested_assumption": "Report independently, per the submission's own recommendation and the uc-pos-002 precedent. A composite permits sign-cancellation: a hitter who chases less and also swings less in the zone nets to 'no change' while having changed materially. Record as a DPO ruling, not an agent default."
    },
    {
      "field": "Data Specification > Derived Metrics > AP-5",
      "issue": "Divergence band population is uncalibrated — all pos hitters, qualified hitters, or Stott's own prior seasons.",
      "suggested_assumption": "Default to Stott's own prior seasons as the primary band with a population band alongside; self-referential comparison matches the Marsh ghost-line pattern and the self-scout framing. Ship raw monthly woba-minus-xwobacon values regardless so the read survives recalibration."
    },
    {
      "field": "Data Specification > Derived Metrics > AP-5",
      "issue": "AP-5 introduces xwobacon, which is not in the requester's supplied kpis list — a validator-visible scope addition rather than a requested metric.",
      "suggested_assumption": "Accept. It is the only metric answering BQ-6, it is a ratified governed KPI per Register 4.3, and the requester's 'assess the facts first' framing implies the process read. But the DPO must consciously accept the addition rather than inherit it."
    },
    {
      "field": "Business Context > Business Questions > BQ-2",
      "issue": "BQ-2 asks whether the improvement is monotonic or an endpoint artifact, but no KPI tests trend shape. It is currently answerable only by eyeballing the figure.",
      "suggested_assumption": "Either inherit RF-1 (running_line, trajectory) from uc-pos-006 — already verified 33/33, disposition C pending one more hitter reuse, and this would be that reuse — or explicitly downgrade BQ-2 to a narrative observation. Do not approve a use case containing an unanswerable question."
    },
    {
      "field": "Business Context > Business Questions > BQ-5",
      "issue": "BQ-5 asks whether the pitcher's approach changed; fpsr alone is a thin proxy. Pitch mix, zone rate, and first-pitch pitch-type would materially strengthen it.",
      "suggested_assumption": "Accept the thin read for this delivery — the document concedes and labels it honestly. Record as a known scope limitation and a candidate follow-on UC."
    },
    {
      "field": "Data Specification > Derived Metrics > AP-4",
      "issue": "Every AP-4 delta is measured from a single month's value. April carries the same sampling noise as every month compared to it, and was selected precisely because it was extreme — the textbook setup for regression to the mean to masquerade as improvement.",
      "suggested_assumption": "Report AP-4 deltas against both the April anchor and a season-to-date-excluding-April baseline. The divergence between the two is the regression-to-the-mean read that assumption A-8 calls for but no current metric delivers."
    },
    {
      "field": "Governance > Access & Usage Controls",
      "issue": "Player (Bryson Stott) is an authorized persona for a product whose stated Actions include A-3 (adjust batting-order slot) and A-4 (adjust platoon deployment) — decisions made about him. The access asymmetry is unaddressed.",
      "suggested_assumption": "Split delivery: full artifact for staff personas; the consumer-onboarding-agent persona guide as the Player-facing surface, scoped to his own approach metrics and excluding deployment-decision framing. Route to privacy-watchdog for confirmation rather than deciding here."
    },
    {
      "field": "Implementation > Data Flow; Data Specification > Canonical Analytical Datasets",
      "issue": "Four draft-code defects: zfig = z[level+kpis] drops all three new KPI columns; merge suffix behaviour is accidental rather than specified; syntax errors (unbalanced parens, suffixes passed as two positional strings not a tuple, px.scatter closing sort_values early); figure title 'wOBA by Season' contradicts a month-axis single-season encoding.",
      "suggested_assumption": "All four are correctly self-identified and none needs a business decision. Assign explicit output column naming to data-architect and syntax/title to data-engineer. Watch the zfig defect specifically — it fails silently and produces a plausible figure with the headline approach metrics absent."
    },
    {
      "field": "Data Specification > Semantic Mapping",
      "issue": "Ten KPIs in the kpis list have no display label; month has neither label nor formatter and will render as integers 4-8.",
      "suggested_assumption": "Assign to data-dictionary. RC-6 and the Usability Requirements both depend on closure, so it is not cosmetic — but it is mechanical and blocks nothing upstream."
    },
    {
      "field": "Identity block; Process Tracking",
      "issue": "HALF CLOSED. The data-products/ listing confirms uc-pos-009-schwarber-swing-decay-001 is the highest pos slug, so uc-pos-010 is correct and free. The dp_uc33 build prefix remains unverified — it lives in the MLB repo.",
      "suggested_assumption": "Slug cleared, proceed. Build prefix: still verify via 'ls dp_uc*' before naming artifacts. One command; prevents a collision that is expensive to unwind after receipts are written."
    },
    {
      "field": "Data Specification > Derived Metrics > runs_created",
      "issue": "runs_created depends on wrc(level, df, constants) — Intake Register B6, disposition B, blocked on a documented constants loader that is itself an open Register item. The dependency is on an artifact that does not yet exist.",
      "suggested_assumption": "Accept the submission's degradation path: emit NULL with disclosure if the loader is unavailable; never approximate. Retain the standing labels — never wRC+, and in-season 2026 constants carry a plus/minus 2% label."
    },
    {
      "field": "Data Specification > Assumptions & Constraints > A-5",
      "issue": "A-5 names opponent quality and platoon mix as the single largest interpretive limitation, but p_throws is optional grain and opponent identity is not a CDE — so the caveat cannot be evidenced or inspected from the delivered dataset. The reader is asked to trust a limitation they cannot check.",
      "suggested_assumption": "Ship a context-only monthly summary (opponent-handedness mix and a coarse opposing-pitcher-quality indicator) as non-grain columns on z. Does not change the declared grain; makes the document's most important caveat auditable rather than rhetorical."
    },
    {
      "field": "Delivery & Consumption > Delivery Cadence; Business Glossary > April Anchor",
      "issue": "The product is specified for monthly re-run but the anchor is not pinned across re-runs. 'Last 4 months' is date-relative; on a September re-run it becomes Jun-Sep and April leaves the window while remaining the anchor. Nothing states that April stays the anchor permanently.",
      "suggested_assumption": "Pin explicitly: April 2026 is the anchor for every re-run of this UC, independent of the rolling window. Generalize the glossary term to 'anchor month — the fixed baseline bucket, declared once at intake and immutable across re-runs.'"
    },
    {
      "field": "PROCESS FINDING — intake workflow, not this document",
      "issue": "Three of six pass-1 blocking issues were wrong because the validator reasoned from the submitted document alone. The submission independently derived a definition that was already approved (fpsr), flagged a possible collision while three swing lists sat in the repo, and chose a PA floor while a standing standard governed the same metric family at analogous grain. Each judgement was individually defensible; the aggregate failure was that no one searched.",
      "suggested_assumption": "Add a MANDATORY repo-search step to Layer 1 intake before any KPI may be declared new: grep the proposed function name across data-products/ and contract/; grep the business term; list data-products/ for the subject entity. Three commands, executed before a spec can instruct data-engineer to fork an approved term. Recommend adding this to the use-case-validator agent definition as a hard responsibility, alongside Register 8 Principle 3 which the register itself already recommends adding to business-glossary-agent and kpi-calculator."
    }
  ],
  "rationale": "Structurally among the more complete submissions to reach intake: value stream unambiguous (pos), six phased business questions with Phase 1 correctly gating Phase 2, five personas mapped to specific questions and actions, sixteen CDEs across six domains, CDE-level DQ expectations decoupled from KPI output, and eleven self-surfaced open items. The no-go is not a judgement on that quality — it is a consequence of what the repo already contains. The dominant finding is duplication, not incompleteness: the submission proposed three new definitions and the repo already held two of them, one of them formally approved and contract-bound. It derived from first principles the exact fpsr formula shipped four UCs ago; it flagged a possible swing-classifier collision while three declarations sat in the repo, two in the same file and disagreeing; it chose a 40-PA floor while a 50-PA standard governed the identical metric family at analogous grain in two neighbouring UCs. Each judgement was individually defensible, which is precisely the condition Principle 1 names as a governance failure. What remains genuinely open is narrower than a document-only read suggests: B-3 (month derivation) is a true gap and the canonical blocking condition; B-1 is a pre-existing repo condition this UC is the first to be unable to route around; B-6 (no target values) can only be filled by the DPO because setting a target is business intent; B-2 and B-5 are now reuse instructions rather than open questions. Peripheral design work can proceed — source-system-profiler, metadata-mapper (now confirming rather than deriving), privacy-watchdog, data-dictionary — but kpi-calculator cannot spec while three swing lists compete, dq-rule-definer cannot write the rule the document itself calls blocking, and data-engineer cannot build. Blocking now is cheap: AP-2 and AP-3 are unratified with no consumers, and once swing_rate lands in the notebook and a second hitter UC inherits it, resolving B-1 becomes a restatement cascade of the same shape as the OUTS_MAP ruling onto uc-pps-021 — Principle 4: reuse propagates a defect rather than detecting it. Preserve through revision: the hitter-approach / pitcher-intent separation (RC-4), denominators shipped alongside rates (RC-3), regression to the mean named as the null hypothesis (A-8), and treating the requester's 'grown steadily' as a hypothesis to test rather than a fact to illustrate. Recommended path to go: one DPO session — rewrite AP-1 as inherited, adopt the 50-PA standard and ratify the three unprecedented floors, ratify one canonical SWINGS list (a repo-wide fix, not a UC-scoped one), declare the month derivation, state three targets — plus one read of discipline() in the MLB notebook. Five of six blocking items need no new information, only decisions, and two of those decisions are simply 'use what already exists'. Resubmit for validator pass 2."
}
```

---

*Returned to the Data Product Owner. Per the validator charter, only the DPO — in consultation with
the human in the loop — may resolve these gaps and re-submit.*
