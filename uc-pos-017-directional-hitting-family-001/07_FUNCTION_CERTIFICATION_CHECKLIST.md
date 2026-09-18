# Function Certification Checklist
**A reusable gate for admitting a function to a governed analytical library.**
Version 1.0 · established on `uc-pos-017` / `dp_uc46` · 2026-09-17

---

## Why this exists

A governed function library — the "guidebook" to a data repository — is a data
product whose consumers are analysts and agents rather than dashboards. It
deserves the same admission gate any other data product gets.

Before this document, the criteria were implicit in precedent. The consequence is
visible in the library itself: one function's markdown opens *"I am going to let
Claude fill in the Business Glossary and Technical Lineage then. Well maybe just
the technical lineage. IDK yet,"* and that same function then shipped **unrunnable**
for weeks while three downstream builds faithfully transcribed its broken body.
That is not an author problem. It is a missing gate.

**The rule this encodes: a function is certified against artifacts, never against
its own plausibility.**

---

## The ten gates

A function is **CERTIFIED** only when all ten pass. Any gate failing with a stated,
DPO-accepted reason yields **CONDITIONALLY CERTIFIED**, with the condition recorded
and dated. Anything else is **DRAFT** and may not be referenced by a published
data product.

### Gate 1 — Prior-art search receipt
The search commands, their scope, and their results are recorded **before** any
element is described as new. Every element resolves to one of: NEW (0 matches),
PROMOTE (exists as a UC-local provisional), EXTEND (exists and is being widened),
PATCH (exists and is defective), or REUSE (exists and is being called).

> *A KPI is not new because you have not seen it. Two defensible definitions of the
> same quantity in one repository is a governance failure even when both are correct.*

**Fails if:** no receipt, or a receipt narrower than the library plus its consumers.

### Gate 2 — Business glossary entry
Term, definition, synonyms and abbreviations, for every new business term the
function introduces — **and** an explicit duplicate/conflict check against existing
terms. Terms already governed elsewhere are cited, not redefined.

**Fails if:** a term is defined twice, or a synonym in use in the repo is unlisted.

### Gate 3 — Technical lineage
Column-level: CDE → source data domain → physical column → transformation logic →
the output column it lands in. Every published column traces to a physical source
or to a named derivation.

**Fails if:** any published column has no traceable origin.

### Gate 4 — Data dictionary
Every column the function *consumes* and every column it *publishes*: type,
definition, null regime, and the cautions a consumer needs in order not to misuse
it. Order statistics are marked as order statistics. Non-re-aggregable statistics
are marked as non-re-aggregable.

**Fails if:** a published column is undocumented, or its null behaviour is unstated.

### Gate 5 — DQ rules defined **and executed**
Rules written in plain language, then executed against real data, then scored.
Coverage across completeness, uniqueness, validity, accuracy, consistency,
timeliness, conformity and traceability. A WARN is acceptable; it must be explained
and escalated.

**Fails if:** rules are defined but not run, or a FAIL is unaddressed.
*Definition and execution are separate responsibilities and should not be the same
agent.*

### Gate 6 — Function logic validation against hand-computed fixtures
A synthetic fixture whose expected values are **derived by hand in the
documentation** and then asserted. Edge cases are explicit: empty input, a single
observation, a NULL in every nullable input, and the boundary of every threshold.

> **Reuse is not verification.** A function that three downstream builds call is not
> thereby verified; reuse propagates a defect, it does not detect one. Only a
> fixture whose answer was known before the code ran can detect a wrong formula.

**Fails if:** expected values were recorded by running the code and copying its
output.

### Gate 7 — Signature and name conformance
The library's calling convention, enforced mechanically rather than per function.
The governed name is used everywhere; exploratory aliases are reconciled before any
spec, receipt or figure references them.

**Fails if:** the signature deviates, or two names for one object survive into
published artifacts.

### Gate 8 — Usage census
Where the function is already called, how many times, in how many files, and
whether any caller has redefined it inline. Inline redefinition is drift and is
reported as a defect, not a style note.

**Fails if:** the census is absent, or a drifted copy is found and not logged.

### Gate 9 — Open items and readiness verdict
Every unresolved decision named, with an owner and a recommendation. A verdict of
CERTIFIED / CONDITIONALLY CERTIFIED / DRAFT, with conditions enumerated.

**Fails if:** an open item is known and omitted, or the verdict is unstated.

### Gate 10 — Implementation binding
The certified source of truth is identified, and a content hash binds the contract
to the code. Where no mechanism exists to compute one, that gap is recorded as a
named condition — **never silently omitted**.

**Fails if:** the binding is claimed but not demonstrable.

---

## Verdict template

```
FUNCTION:      <name>(<signature>)
LIBRARY:       <library / notebook / module>
VERSION:       <semver>
GATES:         1 ✅  2 ✅  3 ✅  4 ✅  5 ✅  6 ✅  7 ✅  8 ✅  9 ✅  10 ⚠
VERDICT:       CONDITIONALLY CERTIFIED
CONDITIONS:    C-n · <condition> · owner · opened <date>
SUPERSEDES:    <prior implementations this replaces>
BREAKING:      <yes/no — if yes, version manifest reference>
```

---

## Generalisation notes

Nothing above is domain-specific. Dropped into another repository, the mapping is:

| This checklist | Typical enterprise equivalent |
|---|---|
| Gate 1 prior-art search | Metric registry / semantic layer duplicate check |
| Gate 2 glossary | Business Glossary tool entry with steward approval |
| Gate 3 lineage | Column-level lineage in the catalog |
| Gate 4 data dictionary | Catalog column descriptions |
| Gate 5 DQ | DQ platform rule suite + scorecard |
| Gate 6 fixtures | Unit tests with golden values |
| Gate 7 signature | Linter / static analysis in CI |
| Gate 8 usage census | Impact analysis / downstream dependency scan |
| Gate 9 verdict | Certification workflow status |
| Gate 10 impl binding | Artifact hash in the model/metric registry |

The two gates most often missing in practice are **1** and **6** — and they are the
two that catch the errors that survive longest, because both failures produce
plausible numbers rather than exceptions.

**Recommended agent ownership:** Gates 1 and 9 to `use-case-validator` and
`certification-agent`; Gates 2–4 to `business-glossary-agent`,
`technical-lineage-builder`, `data-dictionary`; Gate 5 split across
`dq-rule-definer` (define) and `data-quality-engineer` (execute); Gates 6–8 to the
engineering layer with independent verification; Gate 10 to `version-controller`.
