# 05 · Quality & Certification — uc-pps-028 (UC #39 / dp_uc39)

**Layer 4 agents:** `certification-agent` · `use-case-validator` (re-entry) · `cost-watchdog` · `version-controller`
**Status: ✅ CERTIFY-READY.**

---

## 1 · certification-agent — blocking artifact checklist

| # | Required artifact | Present | Evidence |
|---|---|---|---|
| 1 | Use-case contract | ✅ | `uc-pps-028-Jesus Luzardo AZ 20260901.md` |
| 2 | Intake validation + gap report | ✅ | `01_strategy_intake.md` — 3 blocking gaps resolved before design |
| 3 | Source fitness profile | ✅ | `01` §3 + `out/dp_uc39_freshness_manifest.csv` |
| 4 | Data model blueprint | ✅ | `02` §1 |
| 5 | KPI specifications (all NEW KPIs) | ✅ | `02` §2 — CN-1…CN-6, AR-1, each with plain language + formula + grain + population + direction + edge cases |
| 6 | Glossary disposition + Rule-1 grep | ✅ | `01` §5 |
| 7 | Column-level technical lineage | ✅ | `04` §2 |
| 8 | DQ rule specs + executed scorecard | ✅ | `03` §1, `out/dp_uc39_dq_scorecard.csv` — 28 rules, 0 FAIL |
| 9 | Data dictionary | ✅ | `03` §2 |
| 10 | Classification / tagging | ✅ | `03` §3 |
| 11 | Privacy assessment | ✅ | `03` §4 |
| 12 | Executed build + receipts | ✅ | 30 receipts in `out/` |
| 13 | Independent verification harness | ✅ | `dp_uc39_verification.py` — **195/195 PASS** |
| 14 | Package audit | ✅ | `dp_uc39_package_audit.py` |
| 15 | Reader deliverable | ✅ | report `.md` + branded `.pdf` (9pp) |
| 16 | Consumer enablement | ✅ | `06_consumer_success.md` |
| 17 | Acceptance criteria + verdict | ✅ | §3 below |

**No blocking artifact is missing. The gate opens.**

## 2 · Verification design — why 195 checks and not a spot check

The harness re-reads the parquet from scratch and recomputes every published figure with
**deliberately different code** from the build: boolean masks and direct sums rather than the
`get_stats` pipeline wherever the metric allows it. A number that only agrees with itself is
asserted, not verified.

| Block | Checks | What it proves |
|---|---|---|
| 1 · entity lock & frame shape | 7 | one id, one name, no dupes, R-only, 27+32 starts, halves partition the season |
| 2 · season / half line | 64 | 16 metrics × 4 windows, independently recomputed |
| 3 · **uc-pps-017 continuity** | 13 | this build reproduces its parent's published H1 line |
| 4 · per-start log | 16 | the log's PA/outs/runs sum to the season totals; 3 spot starts re-derived |
| 5 · CN-1…CN-6 | 10 | every consistency axis recomputed from the start log |
| 6 · cohort integrity | 7 | cohort floor honoured; **every rank re-sorted from raw values**, not read back |
| 7 · TR-2 scan | 11 | 8 boundaries; asserts xwOBA rank is 1 at **all** of them **and** that CN-1 rank is **not** |
| 8 · splits | 51 | TTO × 3 windows, stand × 2, arsenal usage sums to 1 and every pitch's whiff re-derived, monthly PA reconciles |
| 9 · ARI lens | 12 | H2H names all resolve, tiers isolate correctly, plan usage sums to 1 and reconciles to stand pitch counts |
| 10 · tripwire table | 6 | each tripwire's H1/H2 value recomputed; reproduction table has zero REVIEW rows |
| 11 · manifests | 5 | 0 DQ FAIL, ≥25 rules, lineup flagged NOT AVAILABLE, cache date logged |

**Check 7 is the one that matters most**, because it is the only check in the file written to be able
to *fail the client's premise*: it asserts that CN-1 rank is **not** 1 at every boundary. If a future
run made that assertion false, the report's central caveat would be wrong and the harness would say so.

## 3 · use-case-validator re-entry — acceptance criteria

| # | Criterion | Verdict |
|---|---|---|
| A-1 | The premise is adjudicated, not assumed | ✅ **Split verdict**: level claim supported and boundary-robust; consistency claim assigned to Sánchez on the floor axes and reported as boundary-dependent for Luzardo |
| A-2 | Every `uc-pps-017` watch item is closed with a number | ✅ 16 tripwires, H1 → H2, in `out/dp_uc39_uc17_tripwire_closure.csv` |
| A-3 | The product reproduces its parent | ✅ 17/17 |
| A-4 | Opponent sample honesty | ✅ 22 PA labelled directional everywhere; no confirmed lineup disclosed in report, dashboard and manifest; plan is profile-driven and says so |
| A-5 | Every published number traced to a receipt computed this session | ✅ 195/195 |
| A-6 | New KPIs specified before use | ✅ CN-1…CN-6, AR-1 in `02` §2 |
| A-7 | An actionable recommendation exists for tonight | ✅ the sinker-vs-RHB decision, the leash re-framing, the K-rate condition |

## 4 · Defects found and fixed during this run

All three are **repo-wide patterns**, not one-off bugs in this build.

### D-1 · CDE completeness tested at the wrong grain
The first run emitted `FAIL` for `events` (25.4% non-null) and `launch_speed` (28.5%). Both were
correct at pitch grain and meaningless: `events` exists once per **PA**, `launch_speed` once per
tracked **ball in play**. Testing them at pitch grain manufactures a failure out of the schema's own
shape. **Fix:** every completeness rule now declares its grain and is evaluated on the frame at that
grain. **Where else this bites:** any build in this repo that loops a completeness check over a
column list without declaring grain — which is most of them.

### D-2 · Replay-review prose contaminating batter-name parsing
`des` can be prefixed with review text — `"Diamondbacks challenged (force play), call on the field
was upheld: ... James McCann ..."`. The modal-name parse returned the *review clause* as James
McCann's name. **Fix:** strip any leading `challenged | Review of | reviewed ... :` clause before
parsing, and reject names outside 4–34 characters. **Where else this bites:** every `des`-parse H2H
panel since UC11 — the rule that says "resolve batter ids by name-parsing `des`" has carried this
hole since it was written. Sibling of `O-12` (accent folding): both are text-normalisation gaps in
identity resolution.

### D-3 · A team-level career H2H panel silently mixing eras
The unfiltered Arizona panel put Nick Ahmed (last faced 2023), Evan Longoria (2023) and Kole Calhoun
(2021) beside Ketel Marte as if they were tonight's lineup. **Fix:** `AR-1` recency tier, with the
current-era tier isolated for planning and the historical tier retained but visibly labelled.
**Where else this bites:** any opponent study keyed on a *team* rather than a *player* — which is
every "vs <club>" use case in the ledger.

### Also corrected
A zero delta in the tripwire table (TTO-1 wOBA, .198 → .198) was labelled `DEGRADED` by a strict
`<` comparison. Equality is now `HELD`.

## 5 · cost-watchdog

| Line | Note |
|---|---|
| Build runtime | The first implementation recomputed per-start frames inside the 8-boundary scan loop and exceeded the shell's time budget. Refactoring to compute once and window by filtering cut the run to well inside it. **Reusable rule: a sensitivity scan should be a filter over a precomputed atom, never a recomputation.** |
| Transfers | Only 8 files crossed to the cloud container, all for the one step (`weasyprint`) that cannot run on the device. Everything else was computed in place. |
| Storage | 30 receipts, ~1.4 MB. The 95 KB dashboard embeds the payload rather than re-deriving it — one read, many renders. |
| Rework | Three build re-runs (defect fixes + the tripwire-equality fix), each ~100s. Avoidable had D-1's grain rule existed as a shared helper — **candidate for promotion into the governed kernel**. |

## 6 · version-controller

**v1.0.0** — initial release of `uc-pps-028`. **Non-breaking** with respect to every prior UC:
no locked KPI was modified, no prior receipt overwritten, no glossary term redefined.

Consumers of `uc-pps-017` should note: this product **supersedes its second-half watch list**
(all items closed) but **does not supersede its first-half findings**, which it reproduces exactly.
Anyone quoting `uc-pps-017`'s 2nd-TTO .368 as a live concern should now quote `uc-pps-028`'s .279 instead.
