# 03 · Governance
**business-glossary-agent · data-dictionary · data-tagger · privacy-watchdog**

## Glossary — disambiguations that block silent drift

| Term | Governed meaning here | Must never be conflated with |
|---|---|---|
| **Runs Created** | Notebook cell-14 `runs_created`: Σ over the subject's PAs of (max `post_bat_score` − min `bat_score`) — "runs that scored during his plate appearances", crediting RBI *and* runs scoring by other means (WP, steal of home, error) while he bats | **SC-1 wRC** (uc-pos-004, linear-weights runs) and **Bill James RC**. Three formulas, three meanings. The DPO's snippet calls the notebook function, so it is the one consumed |
| **Pull-Air %** | Governed cell-24 logic on PA-L1 derived coordinates: pulled non-ground BIP ÷ **all** BIP | Savant's pulled-fly-ball family (different air definition) or a pulled-share-of-pulls rate (the governed function's dead `total_pulls` — shipped separately as `pull_rate`) |
| **BA (w RISP)** | BA over PAs whose **terminal pitch** had a runner on 2B/3B (DPO operator) | any-pitch-RISP or start-of-PA-RISP definitions used by public splits |
| **xwOBAcon** (`xwobacon_bip`) | mean `estimated_woba_using_speedangle` over BIP (O-4 naming) | xwOBA — different denominator; only *shifts* are compared in this product |
| **Avg. EV / Avg. LA** | tracked-BIP central tendency (CR-1) | `inds` all-rows means — foul-contaminated (O-3); shipped only in the reconciliation receipt |
| **In-Zone Swing/Whiff Rate** | ZS-1 over `zone < 10`, NULL zone excluded both sides | zone definitions built on `plate_x/plate_z` half-width conventions (open item: three half-widths in repo) |

Alias reconciliation (Rule 3): `par`, `pulled_air`, `pulled_air_rate` → **`pull_air_rate`**;
`dd`/`data_domains` → resolved in `02` §Value stream vs data domain; `z` (the snippet's master frame)
→ `window_split` / `kpi_master` output. No notebook shorthand appears in any receipt.

## Data dictionary

Column-level descriptions for every published receipt column live in the CSV headers +
`02_engineering_design.md` §Metadata mapper; all physical elements trace to the CDEs in `01`'s
fitness table. Nothing is published that lacks a glossary line: every KPI column in
`dp_uc37_window_split.csv` maps to a row in `02` §KPI calculator.

## Tagging proposal (data-tagger)

| Element | Sensitivity | Domain | Product membership |
|---|---|---|---|
| All `dp_uc37_*` receipts | **Internal — Phillies staff** | Phillies Offense VS · batting-events + tracking domains | uc-pos-013 |
| Report + dashboard | Internal — staff; §5 persona table additionally **coaching-sensitive** | same | uc-pos-013 |
| Kernel + verification code | Internal — engineering | — | uc-pos-013 |

## Privacy watchdog

**Rating: LOW** (baseline `pos` performance analytics of a public-record MLB player).
Elements reviewed: no PII beyond public identity (MLBAM id, name); no health, contract, or
biometric-beyond-Statcast content; no quasi-identifier combinations beyond public box-score joins.

Two access-asymmetry notes (below the uc-pos-011 threshold but recorded):

1. **§5 of the report maps performance changes to named staff roles** (hitting coach, manager). All
   rows are explicitly labeled hypotheses with causation disclaimed; none evaluates a named individual
   staff member. Keep it that way in any derivative.
2. The platoon section discusses deployment patterns *about* the subject. Unlike uc-pos-011 there is
   no shielding finding (his LHP exposure fell and the product argues for MORE exposure), so no
   player-facing exclusion is required. If a player-facing surface is cut later, drop §5 anyway.

**External/media distribution: not approved** — internal staff product; governance principle 5
satisfied (privacy assessment complete before any publish decision).

## Version & change classification (version-controller input)

First release of a first-touch subject: **v1.0.0**, no breaking-change surface. The `running_line_pa`
`cum_slg` extension is additive (non-breaking, minor) to a shared provisional function; flagged for
the AP-6 ratification bundle. `pull_air_rate_fix` does NOT modify the governed `pull_air_rate` —
new name, new code path, zero blast radius on prior UCs.
