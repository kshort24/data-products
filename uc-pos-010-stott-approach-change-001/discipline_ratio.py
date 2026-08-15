# ============================================================================
# ⛔ DRAFT — NOT AUTHORIZED — pending human DPO sign-off
#
# uc-pos-010 is at a Layer-1 NO-GO (12 blocking items). This module is a
# Layer-3 (Build) artifact drafted at DPO request while that stop is in force.
# It follows the disclosure precedent set by
#     data-products/uc-pos-stott-qab-001/qab_rate.py
# which carries the same banner for the same reason.
#
# Do not promote to Baseball Functions.ipynb until:
#   (a) DR-1 IBB treatment is ruled (see GOVERNED DEFINITION below), and
#   (b) DR-2 zero-strikeout behaviour is ratified, and
#   (c) the DPO accepts or rejects `obp_per_k` (see §3 of AMENDMENT-3).
# ============================================================================
"""
discipline_ratio.py — Plate-Discipline Ratio family (AP-9)
===========================================================
Use case    : uc-pos-010-stott-approach-change-001 (Phillies Offense, subject: Bryson Stott)
Value stream: pos
Layer       : 3 (Build) — DRAFT, see banner.

Yields the walk-to-strikeout family at any `level`, computed from EVENT COUNTS
rather than from ratios of rounded rates.

Why counts and not rates
------------------------
BB% and K% share the same PA denominator, so (BB/PA) / (K/PA) == BB/K exactly.
The DPO's snippet `z.bbrate / z.krate` is therefore algebraically correct — but
only if neither input has been rounded first. `nresults` rounds to 3 dp; at a
K% near .150 a half-unit rounding error in the denominator is ~0.33% relative,
and it propagates directly into the headline ratio. Computing from counts is
exact and removes the dependency on upstream rounding entirely.

Governed event sets are INHERITED, not redeclared
-------------------------------------------------
    K_EV  = {'strikeout', 'strikeout_double_play'}
    BB_EV = {'walk', 'intent_walk'}
source: data-products/dp_uc7_wheeler_mets/dp_uc7_wheeler_mets.py L439.
Do not re-enumerate these here or anywhere else — import or cite.

Signature contract
------------------
`(level, df)`, per the repo-wide rule. Note that `qab_rate.py` L96 ships as
`qab_rate(df, level=...)` — inverted, and non-conforming. Do not copy that shape.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# ---- GOVERNED DEFINITION -----------------------------------------------------
# Inherited from dp_uc7_wheeler_mets.py L439 — cited, not redeclared.
K_EV  = {'strikeout', 'strikeout_double_play'}
BB_EV = {'walk', 'intent_walk'}

# ⚑ DR-1 — OPEN DPO DECISION: does an intentional walk count as plate discipline?
#   The repo already carries BOTH conventions, for different and defensible reasons:
#     - dp_uc7 L439  BB_EV includes 'intent_walk'  (a walk is a walk — PA accounting)
#     - dp_uc24 L222 running_line's wOBA weight map keys ONLY 'walk'
#                    (wOBA convention deliberately excludes IBB — it is not a
#                     batter achievement)
#   For an APPROACH metric the wOBA reasoning is the stronger one: an intentional
#   walk measures how the opposing manager feels about the hitter, not how the
#   hitter controlled the at-bat. Set UNINTENTIONAL_ONLY = True to adopt it.
#   THE VALIDATOR DOES NOT PICK. This flag exists so the choice is explicit and
#   greppable rather than buried in a mask.
UNINTENTIONAL_ONLY = False   # ← DPO sets this. False = current dp_uc7 behaviour.

# ⚑ DR-2 — OPEN DPO DECISION: behaviour when strikeouts == 0.
#   This is NOT a corner case for this use case — it is THE case. The subject
#   window ("14 walks between strikeouts") has K == 0 by construction, so the
#   headline number is 14/0. Options:
#     'null'  → NaN. Honest; the ratio is genuinely undefined. Plots as a gap.
#     'inf'   → np.inf. What the DPO's snippet currently produces. Breaks axes.
#   Recommended: 'null', paired with the `k_free` flag and the raw counts below,
#   so a consumer can render "14 BB / 0 K" instead of a number that cannot exist.
ZERO_K_BEHAVIOUR = 'null'    # 'null' | 'inf'


def _pa_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Terminal plate-appearance rows only.

    PA definition inherited from dp_uc24_turner_2026_review.py L219 and
    dp_uc22_harper_own_the_zone.py L80: a PA is any row with a non-null `events`
    that is not a `pickoff_1b`. Do not substitute a local definition.
    """
    return df[~df.events.replace(np.nan, 'NA').isin(['NA', 'pickoff_1b'])]


def discipline_ratio(level, df: pd.DataFrame) -> pd.DataFrame:
    """Walk-to-strikeout family at `level`.

    Returns one row per `level` group with:
        plate_apps      int    PA denominator (governed PA definition)
        walks           int    count of BB_EV (see DR-1 for IBB treatment)
        strikeouts      int    count of K_EV
        bbrate          float  walks / plate_apps
        krate           float  strikeouts / plate_apps
        bb_per_k        float  walks / strikeouts   — "walks per punchout"
        bb_minus_k      float  bbrate - krate       — defined even when K == 0
        k_free          bool   True when strikeouts == 0

    Denominators ship WITH the rates (RC-3). No rounding is applied — round in
    the presentation projection (`zfig`), never in the curated frame (`z`).

    Column naming: underscores, not colons. `bb:k` is legal in a pandas column
    but breaks attribute access (`z.bb:k`) and `df.query()`. Reserve the colon
    form for DISPLAY LABELS in `data_dictionary`.
    """
    pa = _pa_frame(df)

    bb_set = ({'walk'} if UNINTENTIONAL_ONLY else BB_EV)

    g = pa.groupby(level, as_index=False)
    out = g.agg(plate_apps=('events', 'size'))

    for name, evset in (('walks', bb_set), ('strikeouts', K_EV)):
        sub = (pa[pa.events.isin(evset)]
               .groupby(level, as_index=False)
               .agg(**{name: ('events', 'size')}))
        out = out.merge(sub, on=level, how='left')
        # A group with zero walks (or zero Ks) genuinely HAS zero — this is a
        # count, not a measurement, so filling 0 is correct here. Contrast with
        # rates, where a missing denominator must stay NULL (uc-pos-009
        # sensor-boundary standard). Fill named count columns only, never the
        # whole frame with .fillna(0).
        out[name] = out[name].fillna(0).astype(int)

    out['bbrate'] = out.walks / out.plate_apps
    out['krate']  = out.strikeouts / out.plate_apps

    out['k_free'] = out.strikeouts == 0

    if ZERO_K_BEHAVIOUR == 'null':
        out['bb_per_k'] = np.where(out.k_free, np.nan,
                                   out.walks / out.strikeouts.replace(0, np.nan))
    else:
        out['bb_per_k'] = out.walks / out.strikeouts   # yields inf when K == 0

    # Always defined. When K == 0 this is the metric that still carries meaning,
    # which is why it ships alongside rather than as an alternative.
    out['bb_minus_k'] = out.bbrate - out.krate

    return out[list(level) + ['plate_apps', 'walks', 'strikeouts',
                              'bbrate', 'krate', 'bb_per_k', 'bb_minus_k', 'k_free']]


def walks_between_ks(level, df: pd.DataFrame) -> pd.DataFrame:
    """AP-10 — longest run of walks between consecutive strikeouts.

    ⚠ THIS IS THE METRIC THE VIDEO TITLE CLAIMS. `discipline_ratio` is not.

    "Drawing 14 walks between strikeouts" is a RUN-LENGTH statistic over an
    ordered PA sequence. `bb_per_k` is a RATE RATIO over an unordered window.
    They are different KPIs and they can disagree in both directions:
      - a hitter can post a 2.0 bb_per_k with walks and Ks perfectly interleaved
        (longest run = 1), and
      - a hitter can post a poor bb_per_k while still owning one long K-free run.
    Neither is a substitute for the other. Ship both or ship the right one.

    Ordering is REQUIRED and must be explicit — a run-length statistic computed
    on an unsorted frame is silently wrong, and pandas will not warn.

    Returns per `level`:
        max_bb_run       int   most walks between two consecutive strikeouts
        current_bb_run   int   walks since the most recent strikeout (open run)
        run_start_date   date  game_date the max run began
        run_end_date     date  game_date the max run ended

    ⚑ DR-3 — OPEN DPO DECISION: streak KPIs have an unfavourable precedent.
      `scoreless_streak(df)` (SL-1, uc-pps-019, dp_uc21 L323) is Intake Register
      disposition **D — DO NOT PROMOTE**, recorded as "receipt-class, explicitly
      not for reuse without caveats." A walks-between-Ks streak is the same
      class of statistic. It may still be the right thing to SHIP as a receipt
      for this use case while remaining wrong to PROMOTE to the library. The DPO
      should rule explicitly rather than let AP-10 inherit SL-1's fate by
      analogy — or its exemption by silence.
    """
    pa = _pa_frame(df).sort_values(['game_date', 'game_pk', 'at_bat_number'])

    bb_set = ({'walk'} if UNINTENTIONAL_ONLY else BB_EV)

    rows = []
    for keys, grp in pa.groupby(list(level), sort=False):
        is_bb = grp.events.isin(bb_set).to_numpy()
        is_k  = grp.events.isin(K_EV).to_numpy()

        best = cur = 0
        best_start = best_end = cur_start = None
        dates = grp.game_date.to_numpy()

        for i in range(len(grp)):
            if is_k[i]:
                cur, cur_start = 0, None
            elif is_bb[i]:
                if cur == 0:
                    cur_start = dates[i]
                cur += 1
                if cur > best:
                    best, best_start, best_end = cur, cur_start, dates[i]

        rows.append(dict(zip(list(level), keys if isinstance(keys, tuple) else (keys,)))
                    | {'max_bb_run': best, 'current_bb_run': cur,
                       'run_start_date': best_start, 'run_end_date': best_end})

    return pd.DataFrame(rows)
