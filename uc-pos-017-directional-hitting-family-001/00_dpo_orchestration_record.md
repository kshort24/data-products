# 00 · DPO Orchestration Record
**UC #46 · `uc-pos-017-directional-hitting-family-001` · `dp_uc46` · v1.0.0 · 2026-09-17**

## 1. What was requested

The DPO asked to expand the directional hitting functions in `Baseball Functions.ipynb`
— the guidebook to the repository — adding an opposite-field rate and an opposite-field
line-drive measure, plus a `bb_type` data dictionary carrying a data profile
(`min_la`, `max_la`, `mu_la`, `std_la`, and the same for `launch_speed` and
`hit_distance_sc`), rendered on a scorecard. He also asked what the certification
criteria for an accepted function are, and whether the guidebook belongs in a skill,
an MCP server, or a tool.

## 2. What intake changed

This is a **library build**, not an analysis use case. The deliverable is a module,
not a finding. That reframing came out of the mandatory Layer-1 search:

| Claim at intake | After Rule-1 search |
|---|---|
| `oppo_rate` is a new KPI | **False.** `dp_uc42_kernel.directional_rate_table` (uc-pos-016, delivered 2026-09-10) already emits `pull_rate` / `oppo_rate` / `straight_rate`. Provisional WF-1/WF-2, UC-local, never promoted. This build **promotes**, it does not invent. |
| `pull_air_rate` exists and works | **False.** Cell 56 reads `bip.loc_x` / `bip.loc_y`; the parquet has `hc_x` / `hc_y` and no `loc_*`. O-7. It has been unrunnable in the guidebook since it was written. |
| The direction boundary is governed | **Half true.** It is governed, but it lives *inside* `pull_air_rate` rather than as its own object, so four verbatim copies exist (cell 56, `dp_uc37`, `dp_uc40`, `dp_uc42`) with no binding between them. |

Search commands and evidence: `01_source_profile_and_fitness.md` §1.

## 3. DPO rulings taken at intake (2026-09-17)

| ID | Ruling | Consequence |
|---|---|---|
| **O-7** | PA-L1 `hc`→`loc` derivation is the governed standard; cell 56 patched in place | O-7 **CLOSED**. `hit_direction` extracted as its own certified object. |
| **DEN-1** | Directional denominators are **classifiable BIP** (`hc_x`/`hc_y` notna) | Extends the uc-pos-009 sensor-boundary NULL standard to direction. Refuses O-8 in advance. **Breaking** for `pull_air_rate` — see `08`. |
| **LD-1** | `oppo_ld_rate` = oppo line drives / **oppo BIP** | Answers "when he goes the other way, does he square it up?" |
| **FL-1** | Floor = **25 classifiable BIP** per published directional cell | New floor at BIP grain; the 50-PA floor stays at PA grain. |
| **DR-3** | Pull / Straightaway / Oppo publish **together** and sum to 1 | No standalone `oppo_rate()` function. |
| **N-2** | Bat-path columns **out of scope** for MVP | `attack_angle` carries the live O-14 sign defect; folding it into a foundational function would import that risk. Logged as the v1.1.0 enhancement. |
| **N-5** | `(level, df)` promoted from per-function ruling to **repo-wide lint rule** | See §4. |

## 4. N-5 — why the signature stops being a ruling and becomes a rule

Register §5 ruled the signature flip for `pulled_air` **alone**, and the ruling did not
sweep. uc-pos-010 then found `qab_rate(df, level=...)` with the same inversion; this
build's search found three more (`pulled_air(df, level)` in `dp_uc24`, `dp_uc31`,
`marsh_breakout_analysis`).

The failure is not that anyone chose badly. It is that the governance object was
**one function at a time**, so each new function is a fresh coin-flip and each
inversion needs its own ruling to find it. Five inversions across four use cases is
the rate at which a per-function model leaks.

Two properties make this worth a rule rather than a preference:

1. **It is silently wrong, not loudly wrong.** `f(df, level)` against an `f(level, df)`
   signature does not raise — pandas will happily group a frame by something, or
   filter a list. You get a plausible number.
2. **It is mechanically checkable.** Unlike a KPI definition, "first positional
   parameter is named `level`" is a one-line AST check. Anything a linter can decide
   should not be spending DPO attention.

Scope of the rule: **every public function in the governed library takes `(level, df)`**,
including population gates and helpers that ignore `level` (`classifiable_bip`,
`derive_loc`, `hit_direction` all accept and discard it in this build). That looks
redundant and is deliberate — a mixed convention is worse than a uniformly redundant
one, because it forces the caller to remember which functions are exceptions.

The three legacy `pulled_air(df, level)` copies are **superseded, not imported**.
They are not patched here: they sit inside delivered, certified packages whose
verification runs against them, and silently changing a shipped artifact's behaviour
is the failure mode `08_version_manifest.md` exists to prevent. They are logged as
deprecated in `06` §4 with a migration note.

Recommended implementation: a repo-wide `lint_signatures.py` at the MLB root, run as
gate 7 of the Function Certification Checklist (`07`). Estimated ~40 lines. **Not
built in this UC** — flagged as the highest-value next governance artifact.

## 5. Layer plan and sequencing

| Phase | Agent role | Output |
|---|---|---|
| T1 | use-case-validator, source-system-profiler | Gap report, ratifications, `01` |
| T2 | business-glossary-agent, kpi-calculator, semantic-modeler | `02`, `03` |
| T3 | data-engineer | `dp_uc46_kernel.py`, `dp_uc46_build.py`, receipts |
| T4 | data-dictionary, dq-rule-definer, data-quality-engineer, privacy-watchdog | `04`, `05` |
| T5 | dashboard-specifier | `dp_uc46_scorecard.py`, notecards |
| T6 | (independent) | `dp_uc46_verification.py` — 49/49 PASS |
| T7 | certification-agent, version-controller, token-economist | `06`, `07`, `08`, telemetry |

## 6. Acceptance criteria

1. `oppo_rate` published as a KPI of `direction_rate`, not as its own function — **met**
2. `oppo_ld_rate` materialises from `bb_type_profile` at direction grain — **met**
3. `bb_type` profile carries min/max/mu/std (+p5/p95) per sensor with per-sensor `n` — **met**
4. Scorecard renders the profile, brand-compliant, no external dependencies — **met**
5. Certification criteria stated as a reusable, generalisable gate — **met** (`07`)
6. O-7 closed and cell 56 runnable — **met**, notebook patch in `07_notebook_patch.md`
7. Every published function verified by hand-computed fixture, not by reuse — **met** (family A)
