# 03 — Governance · uc-pps-017 (UC #19)

## business-glossary-agent — deltas

- No existing governed term redefined. Locked terms (wOBA, xwOBA, whiff/chase/putaway/FPSR/hard-hit) consumed as-is from the Baseball Functions kernel.
- **Provisional definitions PD-1..PD-7** (full specs in 02) registered for DPO ratification. Highest-scrutiny pair: PD-1 (IP-from-log) and PD-2 (RA9-on-mound), because they *resemble* official IP/ERA — both carry a mandatory "reconstruction, not official" label wherever surfaced. Recommendation: ratify with label requirement made permanent.
- Duplicate check: PD-4 (CSW) previously appeared informally in dp_uc12 dashboard work; this spec formalizes it. No conflict — same formula.

## metadata-mapper / data-dictionary — key physical→business links

| Physical | Business term | Class |
|---|---|---|
| `pitcher` (=666200) | Pitcher entity (MLBAM) | exact |
| `estimated_woba_using_speedangle` | xwOBA against | exact |
| `n_thruorder_pitcher` | Times through order | exact |
| `fielder_2` | Battery catcher | exact (id→name data-resolved) |
| `bat_score`/`post_bat_score` | Runs while on mound (PD-2 input) | derived — NEW |
| `events` outs map | Outs recorded (PD-1 input) | derived — NEW |

## data-tagger / privacy-watchdog

- Classification: **Internal — public-source data.** MLB Statcast is public; player identities are public figures in professional context. No PII, no quasi-identifier risk beyond public identity. Privacy gate: **PASS, not blocking.**
- Domain: Phillies Pitching (pps). Product membership: uc-pps-017. Sensitivity: none.

## version-controller

- v1.0.0 — first release. No consumers to notify; no breaking-change surface. A post-All-Star refresh (same spec, extended window) would be **non-breaking** (window extension only). Re-ratification of PD KPIs not required for refresh.
