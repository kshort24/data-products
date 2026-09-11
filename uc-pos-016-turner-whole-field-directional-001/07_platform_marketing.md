# 07 · Platform & Marketing — `uc-pos-016-turner-whole-field-directional-001`

**Version: v1.1.0** — the v1.0.0 text below is unchanged; the v1.1.0 delta is the amendment section appended at the end of this file.

**Agents:** `data-observability`, `cost-watchdog`, `token-economist`

## Monitors / tripwires

| ID | Condition | Why it matters |
|---|---|---|
| **TWF-1** | 2026 outside-zone BIP count crosses 100 (currently 71) | Re-run the outside-zone significance test — it may clear the noise band with more data even if the point estimate doesn't move |
| **TWF-2** | 2026 in-zone pull rate recovers to within 3pp of the 2023-25 pooled rate (48%) before season end | Would suggest the in-zone shift found here was a seasonal blip, not a durable change |
| **TWF-3** | `phils_2026.parquet` freshness lags more than 5 days behind the current date at any future re-run | Data-plane staleness check, standard across this repo's monitors |

No monitor is armed to auto-fire (this repo has no scheduled-job infrastructure for data-product monitors
yet) — these are documented conditions for a human or a future session to check against.

## Cost / efficiency audit (`cost-watchdog`)

- Kernel reuse (`derive_loc`, `hit_direction`, `in_zone` verbatim from `dp_uc40_kernel.py`) avoided
  re-deriving ~120 lines of governed logic and, more importantly, avoided re-discovering the O-7
  (`loc_x`/`loc_y` absent from schema) defect that a from-scratch build would likely have re-hit.
- The pure-Python Parquet reader (`pq_reader.py`, `04_engineering_build.md`) is a one-time environment cost
  that does not recur once `device_bash` reconnects to the data plane — it should not be treated as a
  reusable asset or budgeted into future bids at this UC's rate.
- No redundant data pulls: single concat of 4 season files, filtered to one batter before any downstream
  computation — no wasted full-league scans.

## Bid vs. actual

See `BID_2026-09-10_uc-pos-016-turner-whole-field.md` for the priced bid and the reconciliation below.

| Phase | Bid tokens in/out | Actual (approx.) | Note |
|---|---|---|---|
| T0 Intake + repo reconnaissance (conventions, prior Turner UCs, data location) | 40k / 4k | ~85k / 6k | **Over bid** — this was a cold intake into an unfamiliar project pairing (Agents-repo + MLB-repo split) with no prior session context loaded; a warm session would price this far lower next time |
| T1 Device-bridge / environment troubleshooting (device_bash failure, egress-blocked PyPI/npm/apt, building `pq_reader.py`) | *not bid — unforeseen* | ~45k / 18k | **Unbid environmental contingency**, the single largest miss in this estimate — see "what would change the bid" below |
| T2 Kernel + build + verification | 15k / 12k | ~14k / 11k | On budget — kernel reuse discount held |
| T3 Figures + PDF + dashboard | 12k / 10k | ~13k / 12k | On budget |
| T4 Governance spine 00-07 + README + BID + ledger patch | 14k / 16k | ~15k / 18k | On budget |
| **Subtotal (this file's estimate)** | **~81k / 42k** | **~172k / 65k** | |

**Calibration finding, new to this repo's bid history: environmental risk on a cold pairing was
underpriced by roughly 2x on input tokens.** Every prior bid-vs-actual calibration note in this repo's
memory (uc-pps-026, uc-pos-014) was reconciling a *warm* environment against instrumented history from a
similar prior UC. This was the first build in this project pairing to hit (a) a broken device bridge and
(b) a fully egress-locked cloud sandbox at the same time. **Recommendation for the next bid in this
pairing:** price a "cold intake + environment verification" phase explicitly and separately from the
analytical work, rather than folding it into general intake — see the BID's own note on this.

---

# v1.1.0 AMENDMENT — Platform & Marketing (`dp_uc42a`, 2026-09-10)

**Agents:** `data-observability`, `cost-watchdog`, `token-economist`, `version-controller`

## Monitors / tripwires (v1.1.0)

v1.0.0's TWF-1/2/3 stand unchanged. Three added:

| ID | Condition | Why it matters |
|---|---|---|
| **TWF-4** | In-zone `slg_bip` recovers to within .04 of the pooled 2023–25 .622 before season end | `DC-1` says the per-direction production drop is 86% of the damage loss. If that reverts and the mix does not, the mix change was never the story — and this product will have said so first. |
| **TWF-5** | `PM-1b` (in-zone attack stability) returns p < 0.05 on any future re-run | Would mean opponents finally changed the in-zone plan, which invalidates the "it was the hitter" reading of this build's central finding. This is the tripwire on the conclusion itself, not on the data. |
| **TWF-6** | Any future UC reuses `RC-1`, `PM-1`, `PM-2`, `DC-1` or `slg_bip` | Second-reuse trigger for ratification (E-1). `PM-1` should ideally be reused on a subject whose in-zone attack demonstrably *did* move, per `05` condition 4. |

No monitor auto-fires; this repo still has no scheduled-job infrastructure for data-product monitors.

## Cost / efficiency audit (`cost-watchdog`)

- **Kernel import over kernel copy.** `dp_uc42a_kernel.py` imports v1.0.0's kernel rather than duplicating it.
  The two files cannot drift, and the parent-reproduction check would fail loudly if they did — the cheapest
  possible guarantee that a revision has not quietly rewritten its parent.
- **Verbatim transcription beat re-derivation, again.** Seven `Baseball Functions.ipynb` functions transcribed
  as-is. Re-deriving `nresults`/`mcgs` from scratch would have cost more *and* silently diverged from the
  house numbers — and would have missed D-4 and O-14, which are only visible if you keep the original shape.
- **Template split.** The dashboard is assembled from `tpl/style.css` + `tpl/body.html` + `tpl/app.js` at
  build time. Editing a 600 KB generated file to change one label is the kind of recurring cost that does not
  show up in any single bid.
- **`pq_reader.py` reused unmodified** — v1.0.0 priced it as a one-time environmental cost that would not
  recur. It recurred. See the calibration finding below.
- **Payload compression.** Non-contact pitches ship as four parallel arrays rather than 7,649 JSON objects:
  968 KB → 528 KB, identical data. Relevant because the dashboard is the artifact most likely to be emailed.

## Bid vs. actual

**No bid was solicited for this revision** — it arrived as a direct improvement request against a delivered
product. Priced below as if it had been, because an unbid revision that never gets costed is how a delivery
practice loses its calibration.

| Phase | What it was | Actual (approximate) |
|---|---|---|
| R0 | Warm-ish intake: read the v1.0.0 package, project memory, the revision request and the supplied cell; two clarifying questions to the DPO before building | ~55k in / 4k out |
| R1 | Environment: `device_bash` broken again; egress locked again; folder access to the data plane requested and granted; `pq_reader.py` reused | ~15k in / 2k out |
| R2 | Data layer: seven verbatim transcriptions, six new objects, parent reproduction, context pool, PM-1, DC-1 | ~60k in / 22k out |
| R3 | Dashboard: three template files, five scenes, hand-drawn SVG, headless-browser render checks at desktop and 400 px, four correction passes | ~85k in / 30k out |
| R4 | Plotly notebook script (shipped untested — `05` condition 5) | ~15k in / 8k out |
| R5 | Verification: 155 checks across six families, including the new family F | ~25k in / 12k out |
| R6 | Governance: amendments to `00`–`07`, README, report, reissued ledger patch | ~45k in / 30k out |
| **Total** | | **~300k in / ~108k out · ~2h05m wall clock** (started 17:50 ET, delivered 19:56 ET) |

**Indicative cost at the rates used for the v1.0.0 bid: ~$9.90.** Roughly 1.7× the v1.0.0 delivery, for a
build that added a second chart family, six governed objects, a control test, a decomposition, 122 more
verification checks and a defect correction in its predecessor — but that is a comparison, not a
justification. The DPO did not authorize a number and one should be agreed before the next revision of this
size.

## Calibration findings

1. **The environmental contingency v1.0.0 priced as one-time was not one-time.** v1.0.0's cost note said
   `pq_reader.py` "does not recur once `device_bash` reconnects" and should not be budgeted into future bids.
   `device_bash` did not reconnect; it failed identically. **Correction to that note: in this project pairing,
   a broken device bridge and a fully egress-locked sandbox are the baseline, not the contingency.** Bid them
   into the base case and treat a working bridge as the upside. Two consecutive sessions is a pattern.
2. **Folder access is worth requesting on the first call.** The single `device_request_folder_access` on the
   MLB data plane is what made the context pool, the pitch frame, the widened Rule-1 search and the verbatim
   transcriptions possible. v1.0.0 worked without it and shipped a narrower product for it. **Recommend: in
   this pairing, request data-plane folder access as the first action of intake, before scoping.**
3. **Revisions need their own bid template.** Every prior calibration note in this repo prices a *new* UC. A
   revision has a different shape — parent reproduction is a fixed cost before any new work starts, and
   governance amendment is a larger share of the total (R6 was ~14% of input and ~28% of output here) because
   the amendment has to argue against the parent as well as extend it. **Recommend a distinct revision-bid
   template** with R0 (parent reproduction) and R6 (governance amendment) as named line items.
4. **Family F pays for itself immediately.** It cost roughly 4k output tokens to write and it caught V-1 —
   a wrong figure in the artifact designed to outlive the package. Recommend repo-wide adoption (`00` §9.7-5).
