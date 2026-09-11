"""
dp_uc42_kernel.py — data loader + governed function kernel for uc-pos-016.
====================================================================
Use case  : uc-pos-016-turner-whole-field-directional-001 (Phillies Offense, Trea Turner)
Data plane: C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB

Every function here is either (a) transcribed VERBATIM from `Baseball
Functions.ipynb` — the governed authority — (b) inherited VERBATIM from
`dp_uc40_kernel.py` (uc-pos-014), or (c) NEW to this UC and marked NEW-UC42.

INHERITED (verbatim, not re-derived)
----------------------------------------------------------------------------
derive_loc()      dp_uc40_kernel.py PA-L1 — hc_x/hc_y -> loc_x/loc_y, sourced
                  from cbp-spray_AI.md Data Quality rule 1.
hit_direction()   Baseball Functions.ipynb cell 56 (`pull_air_rate`), stand-
                  aware +/-4.7-slope classification. Requester's explicit
                  instruction: reuse this, do not hardcode a new one.
in_zone()         dp_uc40_kernel.py — `zone < 10`; NULL zone excluded from
                  BOTH populations (same convention behind the D-7/O-13 fix).

NEW-UC42 (this build; provisional, pending ratification — see 03_governance.md)
----------------------------------------------------------------------------
sort_rank()          Handedness-aware facet-column ordering. No prior version
                     was found anywhere in the repo (Baseball Functions.ipynb,
                     the kernel lineage, cbp-spray_AI.md, run-spray-chart-60)
                     despite the requester referring to one with a known
                     RHB-only bug — see 01_strategy_intake.md gap G-1. Built
                     correct for both stands from the start rather than
                     reproducing an unseen, reportedly-broken prior version.
P_THROWS_COLORS      Locked brand color dict (Navy/Red), replacing implicit
                     per-call categorical color assignment (the instability
                     defect named in the request).
MARKER_SIZE          Fixed scalar; replaces `release_speed`-encoded size.
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd

DATA = os.environ.get(
    'DP_UC42_DATA',
    r'C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB')
SUBJECT = 'Turner, Trea'
SUBJECT_MLBAM = 607208              # confirmed by filter, not assumed (uc-pos-006, uc-pos-014)
AS_OF = '2026-09-09'                # max game_date in the pos frame at build

# cbp-spray_AI.md Data Quality rule 1 / dp_uc40_kernel.py PA-L1
HC_ORIGIN_X, HC_ORIGIN_Y = 125.42, 198.27
HC_SCALE = 2.495671

# Locked brand constants — NEW-UC42 (candidate for promotion to a shared
# brand-center constant; currently redefined per-script across the repo)
P_THROWS_COLORS = {'R': '#002D72', 'L': '#E81828'}   # Phillies Navy / Red
MARKER_SIZE = 22                                      # fixed area, px^2 — not release_speed-encoded


def load_turner_pos(years=range(2023, 2027)):
    """Loads Phillies-era `pos` (batting) rows for Turner only.
    Mirrors dp_uc40_kernel.py's load_frames() batting-role split; filtered to
    game_type != ('S','E') and batter == SUBJECT_MLBAM. Pre-PHI (2015-2022,
    data/opponents/turner.parquet) is out of scope for this UC — the premise
    is specifically about a 2023-2025 -> 2026 Phillies-era drift."""
    frames = []
    for y in years:
        p = f'{DATA}/data/phillies/phils_{y}.parquet'
        if os.path.exists(p):
            frames.append(pd.read_parquet(p))
    df = pd.concat(frames, ignore_index=True)
    batting = (((df.home_team == 'PHI') & (df.inning_topbot == 'Bot'))
               | ((df.away_team == 'PHI') & (df.inning_topbot == 'Top')))
    pos = df[batting].copy()
    pos = pos[~pos.game_type.isin(['S', 'E'])].copy()
    pos = pos[pos.batter == SUBJECT_MLBAM].copy()
    pos['game_date'] = pd.to_datetime(pos.game_date)
    return pos


def derive_loc(df):
    """VERBATIM — dp_uc40_kernel.py PA-L1."""
    out = df.copy()
    out['loc_x'] = HC_SCALE * (out.hc_x.astype('float64') - HC_ORIGIN_X)
    out['loc_y'] = HC_SCALE * (HC_ORIGIN_Y - out.hc_y.astype('float64'))
    return out


def hit_direction(bip):
    """VERBATIM — Baseball Functions.ipynb cell 56 (`pull_air_rate`), the
    repo's one and only governed hit_direction definition. Stand-aware,
    scale-invariant (only the sign/ratio of loc_x, loc_y matters)."""
    return np.where(
        bip.stand == 'R',
        np.select(
            [bip.loc_y <= -4.7 * bip.loc_x,
             (bip.loc_y > -4.7 * bip.loc_x) & (bip.loc_y > 4.7 * bip.loc_x),
             bip.loc_y <= 4.7 * bip.loc_x],
            ['Pull', 'Straightaway', 'Oppo'], default='not grouped'),
        np.select(
            [bip.loc_y <= 4.7 * bip.loc_x,
             (bip.loc_y > -4.7 * bip.loc_x) & (bip.loc_y > 4.7 * bip.loc_x),
             bip.loc_y <= -4.7 * bip.loc_x],
            ['Pull', 'Straightaway', 'Oppo'], default='not grouped'))


def in_zone(df):
    """VERBATIM — dp_uc40_kernel.py. `zone < 10` (zones 1-9)."""
    return df[df.zone < 10]


def sort_rank(direction: str, stand: str) -> int:
    """NEW-UC42 — handedness-aware facet-column order. Orders hit_direction
    categories so that reading the facet grid left-to-right always matches
    the physical field (negative loc_x on the left, positive on the right),
    regardless of batter side — instead of a single RHB-only ordering
    silently applied to both stands (the bug the requester flagged in his
    own unseen prior version, see 01_strategy_intake.md G-1)."""
    order_r = {'Pull': 0, 'Straightaway': 1, 'Oppo': 2}
    order_l = {'Oppo': 0, 'Straightaway': 1, 'Pull': 2}
    table = order_r if stand == 'R' else order_l
    return table.get(direction, 99)


def build_bip_frame(pos):
    """pos (pitch-level, Turner only) -> BIP frame with loc_x/loc_y,
    hit_direction, ooz flag, sort_rank. Regular season only for cross-year
    rate comparability (postseason rows are dropped upstream by the caller
    if desired; this UC restricts to game_type=='R')."""
    bip = pos[pos.type == 'X'].copy()
    bip = bip[bip.hc_x.notna() & bip.hc_y.notna()]      # untracked BIP can't be classified (D6/O-8 standard)
    bip = derive_loc(bip)
    bip['hit_direction'] = hit_direction(bip)
    bip = bip[bip.zone.notna()]                          # governed in_zone(): NULL zone excluded from BOTH populations
    bip['ooz'] = bip.zone >= 10
    bip['sort_rank'] = [sort_rank(d, s) for d, s in zip(bip.hit_direction, bip.stand)]

    # Coordinate-convention assertion (uc-pps-025 rule, reused): a RHB's
    # pulled BIP must have median loc_x < 0. Refuse to publish otherwise.
    med_pull_x = bip.loc[bip.hit_direction == 'Pull', 'loc_x'].median()
    assert med_pull_x < 0, (
        f'coordinate convention assertion failed: median loc_x for Pull = {med_pull_x}')
    return bip


def directional_rate_table(bip, zone_label, level='game_year'):
    """WF-1 / WF-2 (NEW-UC42, provisional) — pull/oppo/straightaway rate by
    `level`, for a given zone slice ('outside' | 'in_zone' | 'all')."""
    rows = []
    for yr, grp in bip.groupby(level):
        n = len(grp)
        pull = (grp.hit_direction == 'Pull').sum()
        oppo = (grp.hit_direction == 'Oppo').sum()
        straight = (grp.hit_direction == 'Straightaway').sum()
        rows.append(dict(**{level: yr}, zone=zone_label, n_bip=n,
                          pull_n=pull, oppo_n=oppo, straight_n=straight,
                          pull_rate=pull / n if n else np.nan,
                          oppo_rate=oppo / n if n else np.nan,
                          straight_rate=straight / n if n else np.nan))
    return pd.DataFrame(rows)


def pooled_two_prop_z(x1, n1, x2, n2):
    """Pooled two-proportion z, per the ST-1 convention (uc-pos-014):
    a descriptive uncertainty band on a self-selected window, never a
    hypothesis test in the inferential sense. Bands: |z|>=1.5 moderate,
    |z|>=2.5 clears noise."""
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return np.nan, p1 - p2
    return (p1 - p2) / se, p1 - p2
