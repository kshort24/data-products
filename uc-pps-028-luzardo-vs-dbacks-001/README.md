# uc-pps-028 — Jesús Luzardo: 2026 Consistency Audit & Pre-Scout vs Arizona

**UC #39 · `dp_uc39` · Phillies Pitching (pps) · delivered 2026-09-01 · CERTIFY-READY**
**195/195 verification PASS · 0 DQ FAIL · reproduces all 17 published `uc-pps-017` first-half figures**

---

## What this is

A pre-scout for tonight's start against Arizona that doubles as a season-to-date position on the
pitcher — and, structurally, **an adjudication of the premise the request arrived with.**

The DPO asked for a pre-scout and offered two claims: *"maybe the Phillies' most consistent pitcher"*
and *"since the end of April he has been very good."* Following `uc-pps-027`'s calibration finding
**C-1** — *a harness built around a claim the client already believes will fill cleanly and be wrong*
— the design was built to break the premise before describing it.

**It did, in half.**

| Claim | Verdict |
|---|---|
| *"Very good since the end of April"* | ✅ **Supported and boundary-robust.** Best xwOBA on the staff (.257), ranked #1 at **all eight** window boundaries tested and on the full uncut season. |
| *"Most consistent"* | ⚠️ **Not as stated.** On the floor axes — blow-up rate, floor-start rate, innings per start — the title is **Cristopher Sánchez's**. Luzardo's #1 in start-to-start variation exists only in a narrow band around May 1; on the full season he is 3rd. |
| *the answer that does hold* | ✅ **Workload consistency is genuinely his** — 21 straight turns since May 1, none missed, a 90–110 pitch band (SD 5.8), tightest on the staff, at every boundary. |

Plus: every second-half watch item `uc-pps-017` left open is closed. **The 2nd-time-through-the-order
cliff — that report's headline leash concern at .368 — collapsed to .279.** One tripwire degraded
(hard-hit rate 30.5% → 38.2%) and it is the report's central conditional for tonight.

## Read in this order

1. **`dp_uc39_luzardo_vs_dbacks_report.pdf`** — the 9-page reader report. Start here.
2. **`dp_uc39_luzardo_dashboard.html`** — interactive; open it in a browser, no network needed.
   The breakpoint-scan panel is the single most useful object in the package.
3. **`00_dpo_orchestration_record.md`** — why the product is shaped this way, and the seven open escalations.

## Package contents

| | |
|---|---|
| `00`–`07` | governance spine: orchestration, intake, design, governance, build, certification, consumer, publication |
| `README.md` | this file |
| `uc-pps-028-Jesus Luzardo AZ 20260901.md` | use-case contract |
| `uc_ledger_AI_PATCH_*.md` | ledger patch, **pending human paste (E-3)** |
| `dp_uc39_luzardo_vs_dbacks.py` | Layer-3 build (1,090 lines) |
| `dp_uc39_verification.py` | independent harness — 195 checks, different code path from the build |
| `dp_uc39_package_audit.py` | artifact-completeness audit |
| `dp_uc39_build_dashboard.py` | dashboard generator (offline + published variants, one payload) |
| `dp_uc39_luzardo_vs_dbacks_report.md` / `.pdf` | reader report |
| `dp_uc39_luzardo_dashboard.html` | offline dashboard — vendors nothing |
| `dp_uc39_luzardo_dashboard_artifact.html` | published variant |
| `out/` × 30 | receipts: 24 CSV, 5 PNG, 1 JSON payload |

## Reproduce

```bash
export MLB_DATA_ROOT="/path/to/MLB/data/phillies"
export MLB_WOBA_CSV="/path/to/MLB/wOBA and FIP Constants.csv"   # optional; auto-discovered
python dp_uc39_luzardo_vs_dbacks.py        # build   -> out/, 28 DQ rules
python dp_uc39_verification.py             # verify  -> 195/195 PASS, exit 0
python dp_uc39_package_audit.py            # audit   -> package completeness
BUILD_ARTIFACT=1 python dp_uc39_build_dashboard.py
```

`pyarrow` on a space-constrained VM: `TMPDIR=/tmp/pipwork PIP_CACHE_DIR=/tmp/pipcache
pip install --target /tmp/pylibs --no-cache-dir pyarrow`, then `PYTHONPATH=/tmp/pylibs`.
The PDF step needs `weasyprint`, which needs native pango/cairo.

## What this UC contributes to the organisation

- **`G8`** — a superlative is not a finding until its metric is named and its cohort enumerated.
- **`G9`** — never publish a composite index for a contested claim. Publish the axes; let them disagree in public.
- **`CN-1…CN-6`** — variance is not level. Generalises to any reliability question about a repeated process.
- **`AR-1`** — recency tiering for entity-vs-*group* history, where the group persists and its members turn over.
- **The parent-reproduction check** — any product claiming to extend another must reproduce its published figures first.
- **Three repo-wide defects found and fixed:** `D-1` grain-relative completeness · `D-2` replay-review prose in `des` parsing · `D-3` era-mixing in team-keyed H2H.

## Caveats that travel with every number

Second half is **8 starts / 208 PA**. Arizona head-to-head is **22 PA in 2026** and **no lineup was
confirmed** — the hitter panel is candidates, not a card, and the plan is profile-driven. IP is
reconstructed from event outs; runs are score deltas while on the mound (**RA9, not ERA — no official
ERA or W–L appears anywhere in this package**). Two known kernel defects are carried openly rather
than silently patched: `O-5` (`truncated_pa` counted as a PA) and `O-8` (untracked balls in play
counted as not-hard-hit).
