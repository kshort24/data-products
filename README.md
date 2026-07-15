# Data Products

This directory is the output layer of an agentified data-product organization: a defined roster of
27 agents, sequenced across four governance layers (Intake & Discovery → Design → Build →
Certify & Publish), that turns a business use case into a certified data product. The full agent
roster, roles, and governance rules live in the [root `CLAUDE.md`](../CLAUDE.md); this README covers
only what you're looking at once an agent run finishes and lands here.

Each subfolder is one completed run of that pipeline against one business use case. Every folder is
two things at once:

**A deliverable.** A packaged answer to a specific business question — a report, a KPI set, a
dashboard-ready dataset, a scouting note — written for the human who asked for it.

**A receipt.** The full evidence trail that the deliverable earned the label "certified data
product" rather than being a one-off chart someone made. Governance gate results, agent handoffs,
data-quality scorecards, and independent verification runs are all preserved alongside the
deliverable, not thrown away once the analysis shipped.

If you're publishing this repo, both halves matter: the deliverable is what a consumer reads, and
the receipts are what let a reviewer — or a future version of this same agent org — check that the
answer was actually earned and reproduce it.

## Folder naming

`uc-<value-stream>-<id>-<slug>` (some early runs predate this convention and are named more loosely
— see "Irregular folders" below).

| Prefix | Value stream |
|---|---|
| `pos` | Position player / offense |
| `pps` | Pitcher / pitching-and-defense scouting |
| `def` | Defense |
| `chk` | Cross-stream checkpoint (spans multiple value streams) |

The trailing id is either a sequential use-case number (`uc-pps-019-...`) or a descriptive slug where
the use case predates the numbered ledger (`uc-pos-marsh-xbh-001`).

## What's inside a package

Every package is built from the same governance skeleton, even though department numbering has
evolved slightly across runs (check the package's own `README.md` for its exact file map — it's the
authoritative catalog card for that folder):

| File | Layer | Contents |
|---|---|---|
| `00_*orchestration_record.md` / `00_*delivery_spine.md` | Orchestration | Sequencing, governance-gate checklist, publish recommendation |
| `01_*` | Intake & Discovery | Use-case validation, source fitness, glossary/CDE definitions |
| `02_*` | Design | Data model, KPI calculation specs, join validation |
| `03_*`–`04_*` | Build | Technical lineage, pipeline build notes, reconciliation |
| `05_*`–`06_*` | Certify | DQ scorecard, certification readiness verdict |
| `07_*` | Publish / Operations | Persona-facing consumption notes, versioning, observability runbook |
| `README.md` | Catalog card | One-page summary: what it answers, the read, publish status, file map |
| build script(s) (`dp_uc*.py`) | Receipt | The actual transformation/analysis code that produced the numbers |
| `*_verification.py` (+ results) | Receipt | Independent recompute harness — proves the reported numbers reconcile |
| reader report (`.md`/`.pdf`) | Deliverable | The consumer-facing writeup |
| `telemetry/`, `out_*` figures, CSVs | Receipt | Run economics, chart sources, intermediate outputs |

This maps directly to the four governance layers and five governance principles in the root
`CLAUDE.md`: no CDE gets defined outside the glossary agent, nothing gets built without an approved
model and lineage doc, nothing publishes without a "ready" verdict from the certification agent,
breaking changes are classified and DPO-acknowledged, and privacy review clears anything headed to
an external audience. A package's `00`/`06` file is where you'll find each gate's result recorded.

## Sibling directories referenced by these packages

- `../contract/` — registered publish contracts (YAML) for packages that have graduated to a formal
  contract, referenced from that package's `README.md`.
- `../_contract_run_inputs/` — inputs captured at contract-run time for reproducibility.

## Irregular folders

- `_layer1-batch-validation-2026-07-09/` — not a delivered product. A batch intake-validation sweep
  across multiple pending use cases; kept as a receipt of that governance pass.
- `dp_uc7_wheeler_mets/` — an early run that predates the `uc-<stream>-<id>` naming convention and
  the standardized `00`–`07` file map. Still a valid receipt trail, just in an older shape.

## Reading a package

Start with that folder's own `README.md` — it states what business question was answered, the
headline result, publish/certification status, and a table pointing to every other file in the
folder. Only open the numbered department files if you need the underlying governance detail (why a
KPI is defined the way it is, what the DQ scorecard actually checked, what the verification harness
recomputed independently).

## Before treating anything here as public-safe

Certification confirms internal consistency and completeness, not publish audience. Check the
package's privacy-watchdog result (in its `03`/`06` file) before assuming a package's data is
appropriate for an external or public audience — don't infer that from certification status alone.
