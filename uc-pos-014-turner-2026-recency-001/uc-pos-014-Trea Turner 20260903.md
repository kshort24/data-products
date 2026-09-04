# Use Case — `uc-pos-014-turner-2026-recency-001`

**Submitted:** 2026-09-03 · **Requester:** business user / Data Product Owner (Kellen Short)
**Value stream:** Phillies Offense (`pos`) · **Subject:** Trea Turner, MLBAM 607208
**Build artifact:** `dp_uc40` · **UC ordinal:** #40 · **Parent:** `uc-pos-006` / `dp_uc24` (2026-07-21)

## 1 · Ledger row (pending paste — see `uc_ledger_AI_PATCH_uc-pos-014-turner.md`)

Recorded here per the ledger maintenance rule, in case the installed skill cannot be edited mid-session.

## 2 · The ask, as submitted

> Let's take a look at Trea Turner. What is going on with him recently and maybe this year in general?
> Start by analyzing his high-level performance, defining where he has struggled this year. Then let's dig
> in to what "good" has looked like in the past for him, both with the Phillies and in his prior career.
> Are there underlying indicators that are affecting his performance? Are there potential actions that
> could be taken by personas within the Phillies hitting department to drive better outcomes? Has his
> approach changed? Are there certain pitches or pitch groups that he is struggling against? Perhaps a
> trend against lefties or righties? Leaving a fair amount of latitude for data-product-owner to guide
> this direction.

Delivery instructions: work in the MLB repository as the data plane; governed, documented output with
receipts in `data-products/<uc-id>/` following the `00_`–`07_` convention; take inspiration from the
scouting-report skill; include a token/time estimate framed as a competitive RFP bid (treated as won);
a PDF report; and — if it makes sense — an interactive dashboard.

## 3 · Decomposition

Q1 recency · Q2 season in general · Q3 where he struggled · Q4 what "good" looked like (PHI + prior
career) · Q5 underlying indicators · Q6 hitting-department persona actions · Q7 approach change ·
Q8 pitch groups and platoon. Full acceptance criteria in `01_strategy_intake.md`.

## 4 · DPO discretion, declared before the build

1. "Recently" = **2026-08-01 → 2026-09-02**, against **Mar 26–Jun 30** and **July**, with a mandatory
   RC-5 breakpoint sensitivity scan because the window was chosen after the outcome was known.
2. "Good" = **three** reference points — his peak seasons, his 2023–25 Phillies norm, and the 220-season
   Phillies hitter population — not a single career average.
3. This is an **extension** of `uc-pos-006`, so the standing parent-reproduction check applies.

## 5 · Acceptance

All eight questions answered; Q6 answered within its declared structural limit (no causation identifiable).
Verification 711/711. DQ 23/2/0. Parent reproduction 84/84. Certification READY.

## 6 · New governed objects (ratification pending — escalations E-1…E-4)

`AD-1` approach differential · `ST-1` window-shift uncertainty band · `BT-1` swing measurables ·
`in_zone_rate_fix` (D-7 / O-13 remediation) · `RF-2` promoted to ratification candidate on second reuse.
