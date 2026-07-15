# Token-Economist Pilot — Calibration Report · uc-pos-004 (dp_uc20) · 2026-07-14

**Status of this pilot:** first instrumented run. No live bids existed at kickoff, so T1–T2/T10 carry *retro-bids* (what the agent would have bid from Marsh/Duran precedent) — honest label, weaker evidence. T3–T9 were bid mid-run before each phase executed. From the next run, all bids precede execution.

## Headline economics
| Axis | Bid | Actual (est.) | Error |
|---|---|---|---|
| Input tokens | 54,000 | ~62,000 | **+14.8%** under-bid |
| Output tokens | 25,700 | ~25,800 | **+0.4%** — essentially calibrated |
| Wall-clock | 65 min | ~72 min | **+10.8%** under-bid |
| Accuracy | — | 18/18 verification, DQ PASS, 12/12 artifact completeness, 3 retries (all environmental) | — |

## Measurement method (and its error bars)
- **Tokens:** no native meter in the runtime. Output = artifact chars/4. Input = tool-result chars/4 plus context reconstruction for skill loads and file reads. Expect **±20% systematic error on input**; output is tighter (±5%) because artifacts are countable. This is the pilot's biggest known weakness — capture points, not arithmetic, are what future runs should improve.
- **Time:** UTC anchors from in-run `date` calls (21:56:46Z org-confirm → 22:08:27Z spine-complete observed; recon and close phases partially reconstructed). One user-side interruption (tool-permission stream drop at the intake question) excluded from all task minutes.
- **Accuracy:** three concrete measures per task where available — independent recompute (18/18), DQ scorecard (PASS), artifact-completeness checklist (12/12). Rework count: 3 retries, none semantic (mount request, figure label, dependency install).

## Calibration findings
1. **Input tokens are systematically under-bid on recon-heavy phases.** T1 ran +27% over bid: skill payloads and prior-art reads are bulkier than remembered. *Correction:* recon bids should price each skill load at ~4k and each prior-report read at ~3–4k, not round down.
2. **Reuse flags were the strongest cost predictor.** T4 (build) hit bid almost exactly *because* ~70% of the script is verbatim dp_uc18 kernel; T3 cost near-zero design because 8/10 KPIs were locked. The pattern-inheritance map in the ledger is, economically, a price list.
3. **Environmental retries are the noise floor.** All 3 retries were environment (folder mount, package installs), not agent error. Future bids should carry a flat ~3-min environment tax on cold sandboxes rather than pricing retries into task confidence.
4. **The 80/20 of output spend:** governance trail (T8) + report (T5) ≈ 35% of output tokens. Both are template-driven — the cheapest big win is tightening templates so inherited boilerplate isn't re-emitted (see economies below).

## Top-3 economies for the next run
1. **Ship a spine template** (00–07 skeletons with fixed section headers) in the skill or control plane — cuts T8 output an estimated 30–40% and removes the need to read a prior UC's spine for structure.
2. **Persist the pricing history:** this folder's ledger is the first row of the cross-run history. Next run's bids must cite it (`basis` column) — that is the difference between a bid and a guess.
3. **Batch recon reads:** T1 spent calls on sequential discovery (ledger → repo ls → exemplar → contracts). A single recon manifest per value stream (maintained by the skill) would collapse 4–5 reads into 1.

## Open design questions for the DPO (before promoting this agent past pilot)
- **Where do real token counts come from?** Options: platform usage exports, harness-level metering, or continued chars/4 estimation with stated error. The agent def deliberately allows estimation-with-method-label so the practice can start before the plumbing exists.
- **Bid granularity:** per-layer (cheap, coarse) vs per-task (this pilot, ~10 rows) vs per-tool-call (too fine; violates founding principle 5).
- **Accuracy weighting:** current ledger reports accuracy alongside cost without collapsing them into one score. Recommend keeping them separate — a composite "efficiency score" invites gaming the cheap axis.
