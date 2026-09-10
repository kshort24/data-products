# 07 · Platform & Marketing — `uc-pos-016-turner-whole-field-directional-001`

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
