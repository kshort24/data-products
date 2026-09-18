"""
dp_uc46_kernel — Directional Hitting Function Family
====================================================
UC #46 · `uc-pos-017-directional-hitting-family-001` · `dp_uc46` · v1.0.0

A LIBRARY build, not an analysis build. The deliverable is this module: the
first governed directional-hitting family in the repo, promoted from
UC-local provisionals into certifiable guidebook objects.

FIDELITY HEADER
---------------
Kernel inheritance
  * `hit_direction`        EXTRACTED VERBATIM from `Baseball Functions.ipynb`
                           cell 56 (`pull_air_rate`). The +/-4.7 slope boundary
                           and the stand-aware np.select ladder are unchanged.
                           Previously transcribed into dp_uc37 / dp_uc40 /
                           dp_uc42 kernels; those four copies collapse to this one.
  * `derive_loc`           VERBATIM PA-L1 (dp_uc37_kernel, reused dp_uc40/dp_uc42).
                           RATIFIED by the DPO 2026-09-17 -> O-7 CLOSED.
  * `direction_rate`       PROMOTED from `dp_uc42_kernel.directional_rate_table`
                           (uc-pos-016, WF-1/WF-2 provisional). Generalised from
                           game_year-only to an arbitrary `level`; floor added.
  * `bb_type_profile`      NEW. Extends the governed `bb_type_by_level`
                           (notebook cell 50) with a per-sensor data profile.
                           Share arm reproduces cell 50 exactly (verified: F-2).
  * `pull_air_rate`        PATCHED cell 56: loc derivation + classifiable-BIP
                           denominator + dead `total_pulls` removed.
                           ** BREAKING vs published v0 values ** -- see 08 manifest.

Entity lock      none (library; exercised against Phillies `pos` 2024-2026 R)
Data window      caller-supplied
Dedup key        PITCH_KEY = ['game_pk','at_bat_number','pitch_number']
Signature rule   EVERY public function is (level, df). Repo-wide, non-optional.
                 (Register Rule 2; `pulled_air(df, level)` in dp_uc24/dp_uc31/
                 marsh is the inverted legacy form -- superseded, not imported.)
Brand            Phillies Brand Center: Red #E81828, Navy #002D72, Cream #F3E5AB,
                 Neutral Gray #8C8C8C, Light Gray #D9D9D9. Arial.

DPO RATIFICATIONS CARRIED BY THIS BUILD (2026-09-17)
  O-7   PA-L1 hc->loc derivation is the governed standard. Cell 56 patched.
  DEN-1 Directional denominators are CLASSIFIABLE BIP (hc_x/hc_y notna).
  LD-1  oppo_ld_rate = oppo line drives / oppo BIP.
  FL-1  Floor = 25 classifiable BIP per published directional cell.
  DR-3  pull / straightaway / oppo publish together and sum to 1.
"""

import numpy as np
import pandas as pd

__version__ = '1.0.0'

# --------------------------------------------------------------------------
# Ratified constants -- Register Principle 1: one physical concept, one constant
# --------------------------------------------------------------------------
HC_SCALE     = 2.495671   # PA-L1 · ft per Statcast hc unit
HC_ORIGIN_X  = 125.42     # PA-L1 · home plate, hc_x
HC_ORIGIN_Y  = 198.27     # PA-L1 · home plate, hc_y
DIR_SLOPE    = 4.7        # cell 56 · wedge boundary slope, VERBATIM
BIP_FLOOR    = 25         # FL-1 · classifiable BIP per published directional cell

DIRECTIONS = ['Pull', 'Straightaway', 'Oppo']
UNGROUPED  = 'not grouped'

DIRECTION_COLORS = {          # inherited from dp_uc42a_kernel, brand-bound
    'Pull':         '#E81828',   # Phillies Red
    'Straightaway': '#8C8C8C',   # Neutral Gray
    'Oppo':         '#002D72',   # Phillies Navy
}

# Profile columns: the INCOMPLETE sensor arm of the CR-1 two-population design.
# Each carries its OWN n, because their null regimes differ from each other and
# from bb_type (which is 0.00% null on BIP -- the complete classifier arm).
PROFILE_COLS = {
    'launch_angle':    'la',
    'launch_speed':    'ev',
    'hit_distance_sc': 'dist',
}

PITCH_KEY = ['game_pk', 'at_bat_number', 'pitch_number']


# --------------------------------------------------------------------------
# DR-0 · population gate
# --------------------------------------------------------------------------
def classifiable_bip(level, df):
    """DEN-1 · The governed directional population.

    A ball in play whose hit coordinates were not recorded cannot be assigned a
    direction. Under the uc-pos-009 sensor-boundary NULL standard it is NOT
    evidence of 'not oppo', so it leaves the denominator rather than deflating
    the rate. This is the O-8 defect (`hard_hit_rate` counting untracked BIP as
    'not hard hit') refused in advance for the whole directional family.

    `level` is accepted and unused -- the (level, df) signature is repo-wide and
    non-optional, including for population gates, so that no caller has to
    remember which functions take which order.
    """
    bip = df[df.type == 'X']
    return bip[bip.hc_x.notna() & bip.hc_y.notna()].copy()


# --------------------------------------------------------------------------
# PA-L1 · coordinate derivation (RATIFIED, closes O-7)
# --------------------------------------------------------------------------
def derive_loc(level, df):
    """PA-L1 · Statcast hit coordinates (hc_x, hc_y) -> field feet (loc_x, loc_y).

    The parquet schema has NO loc_* columns. Cell 56 read them anyway, which is
    why `pull_air_rate` could not execute (O-7). Origin is home plate; loc_y is
    sign-flipped because hc_y increases toward the plate while field distance
    increases away from it. Convention is cbp-spray.

    Classification is scale-invariant -- only the sign and ratio of loc_x/loc_y
    enter `hit_direction` -- so HC_SCALE cannot change any direction assignment.
    It is retained because loc_* in feet is independently useful (spray charts,
    distance) and because publishing the derivation is what made O-7 closable.
    """
    out = df.copy()
    out['loc_x'] = HC_SCALE * (out.hc_x.astype('float64') - HC_ORIGIN_X)
    out['loc_y'] = HC_SCALE * (HC_ORIGIN_Y - out.hc_y.astype('float64'))
    return out


# --------------------------------------------------------------------------
# DR-1 · the classifier (EXTRACTED VERBATIM from cell 56)
# --------------------------------------------------------------------------
def hit_direction(level, df):
    """DR-1 · Stand-aware three-way spray classification: Pull / Straightaway / Oppo.

    VERBATIM from `Baseball Functions.ipynb` cell 56. Extracting it is the point
    of this build: it was the repo's only authority for the boundary and it lived
    INSIDE a KPI function, so every consumer had to transcribe it. Four verbatim
    copies existed (cell 56, dp_uc37, dp_uc40, dp_uc42) with no binding between
    them -- Register Principle 1 exposure with no detection mechanism.

    Returns a Series aligned to `df.index`. Requires loc_x / loc_y: call
    `derive_loc` first.

    Coordinate convention is ASSERTED, never assumed (O-15): see
    `assert_spray_convention`.
    """
    d = df
    return pd.Series(
        np.where(
            d.stand == 'R',
            np.select(
                [d.loc_y <= -DIR_SLOPE * d.loc_x,
                 (d.loc_y > -DIR_SLOPE * d.loc_x) & (d.loc_y > DIR_SLOPE * d.loc_x),
                 d.loc_y <= DIR_SLOPE * d.loc_x],
                DIRECTIONS, default=UNGROUPED),
            np.select(
                [d.loc_y <= DIR_SLOPE * d.loc_x,
                 (d.loc_y > -DIR_SLOPE * d.loc_x) & (d.loc_y > DIR_SLOPE * d.loc_x),
                 d.loc_y <= -DIR_SLOPE * d.loc_x],
                DIRECTIONS, default=UNGROUPED)),
        index=d.index, name='hit_direction')


def assert_spray_convention(level, df):
    """O-15 control · Refuse to publish on an unverified coordinate convention.

    A RHB's pulled BIP must sit on the negative-loc_x side and a LHB's on the
    positive side. If a future Statcast schema change flips hc_x, every
    directional KPI in the repo silently inverts and every rate stays plausible.
    This assertion is the only thing that would catch it. Raises on failure.
    """
    out = {}
    for stand, want in (('R', -1), ('L', +1)):
        s = df[(df.stand == stand) & (df.hit_direction == 'Pull')]
        if not len(s):
            continue
        med = float(s.loc_x.median())
        out[stand] = med
        if np.sign(med) != want:
            raise AssertionError(
                f'spray convention failed: median loc_x for {stand}HB Pull = '
                f'{med:.2f}, expected sign {want}')
    return out


def build_bip(level, df):
    """Convenience assembly: raw pitch frame -> classified, classifiable BIP frame.

    One call so that no consumer re-implements the gate/derive/classify order
    (the exact drift this build exists to stop). Asserts the spray convention
    before returning.
    """
    bip = classifiable_bip(level, df)
    bip = derive_loc(level, bip)
    bip['hit_direction'] = hit_direction(level, bip)
    assert_spray_convention(level, bip)
    return bip


# --------------------------------------------------------------------------
# DR-2 · the directional KPI family
# --------------------------------------------------------------------------
def direction_rate(level, df):
    """DR-2 · Directional rate family at `level`. Carries `oppo_rate`.

    PROMOTED from `dp_uc42_kernel.directional_rate_table` (WF-1/WF-2), which was
    hard-wired to `game_year`.

    Per DR-3 the three rates publish TOGETHER and sum to 1 by construction. There
    is deliberately no standalone `oppo_rate()` function: the wedge boundary
    splits three ways, so `1 - oppo_rate` is NOT pull rate, and a solitary oppo
    function invites exactly that subtraction.

    Accepts either a raw pitch frame or an already-built BIP frame.

    Returns, per `level` cell:
        n_bip, pull_n, straight_n, oppo_n,
        pull_rate, straight_rate, oppo_rate,          <- KPIs
        below_floor                                    <- FL-1 suppression flag
    """
    level = list(level)
    bip = df if 'hit_direction' in df.columns else build_bip(level, df)

    g = bip.groupby(level, as_index=False, dropna=False).agg(n_bip=('des', 'size'))
    for name, col in (('Pull', 'pull_n'), ('Straightaway', 'straight_n'), ('Oppo', 'oppo_n')):
        cnt = (bip[bip.hit_direction == name]
               .groupby(level, as_index=False, dropna=False)
               .agg(**{col: ('des', 'size')}))
        g = g.merge(cnt, on=level, how='left')
    count_cols = ['pull_n', 'straight_n', 'oppo_n']
    # Fill COUNT columns only. Rates are left NULL where the denominator is
    # absent -- the uc-pos-009 standard; a blanket .fillna(0) would publish
    # 'oppo_rate 0.0' for a cell that has no tracked BIP at all.
    g[count_cols] = g[count_cols].fillna(0).astype(int)

    for num, rate in (('pull_n', 'pull_rate'), ('straight_n', 'straight_rate'), ('oppo_n', 'oppo_rate')):
        g[rate] = np.where(g.n_bip > 0, g[num] / g.n_bip, np.nan)

    g['below_floor'] = g.n_bip < BIP_FLOOR
    return g


# --------------------------------------------------------------------------
# BB-1 · batted ball type shares + data profile
# --------------------------------------------------------------------------
def bb_type_profile(level, df):
    """BB-1 · `bb_type` shares at `level`, plus a data profile of each sensor column.

    CR-1 two-population design, made explicit:
      * SHARE arm   -- over `bb_type`, the COMPLETE classifier (0.00% null on
                       BIP across 2024-2026). Reproduces the governed
                       `bb_type_by_level` (cell 50) `share` exactly -- asserted
                       in verification family F-2.
      * PROFILE arm -- over launch_angle / launch_speed / hit_distance_sc, each
                       an INCOMPLETE sensor with its own null regime. Each
                       therefore carries its OWN n_*, never one shared n.
                       2026 nulls on BIP: la 0.31%, ev 0.31%, dist 0.38% --
                       three different numbers, which is the whole reason.

    `oppo_ld_rate` is materialised here, NOT by a separate function:

        prof = bb_type_profile(['player_name', 'hit_direction'], bip)
        oppo_ld_rate = prof.query("hit_direction=='Oppo' and bb_type=='line_drive'").share

    Because `total_level` is grouped at the passed `level`, adding
    `hit_direction` to the level makes the denominator oppo BIP -- LD-1 exactly.

    Column naming follows the DPO's stated convention (`mu_la`, `min_la`, ...).
    NOTE a divergence from the notebook's `inds`, which uses the reversed
    `la_mu` / `ev_mu` / `dist_mu`. Both are now in the repo. Logged as open
    item O-20 with a recommendation to align `inds` on the next pass; NOT
    silently reconciled here, because renaming `inds` output breaks 74 call
    sites across 14 files.

    Returns, per `level` x `bb_type` cell:
        bips, total_level, share, below_floor,
        n_la,   min_la,   max_la,   mu_la,   std_la,   p5_la,   p95_la,
        n_ev,   min_ev,   max_ev,   mu_ev,   std_ev,   p5_ev,   p95_ev,
        n_dist, min_dist, max_dist, mu_dist, std_dist, p5_dist, p95_dist
    """
    level = list(level)
    bip = df if 'hit_direction' in df.columns or 'loc_x' in df.columns else classifiable_bip(level, df)
    keys = level + ['bb_type']

    counts = bip.groupby(keys, as_index=False, dropna=False).agg(bips=('des', 'size'))
    totals = counts.groupby(level, as_index=False, dropna=False).agg(total_level=('bips', 'sum'))
    out = counts.merge(totals, on=level, how='left')
    out['share'] = out.bips / out.total_level
    out['below_floor'] = out.total_level < BIP_FLOOR

    for col, sfx in PROFILE_COLS.items():
        agg = bip.groupby(keys, as_index=False, dropna=False).agg(**{
            f'n_{sfx}':   (col, 'count'),          # .count() excludes NaN -> per-sensor n
            f'min_{sfx}': (col, 'min'),
            f'max_{sfx}': (col, 'max'),
            f'mu_{sfx}':  (col, 'mean'),
            f'std_{sfx}': (col, 'std'),
            f'p5_{sfx}':  (col, lambda s: s.quantile(0.05)),
            f'p95_{sfx}': (col, lambda s: s.quantile(0.95)),
        })
        out = out.merge(agg, on=keys, how='left')

    return out


# --------------------------------------------------------------------------
# PATCHED cell 56
# --------------------------------------------------------------------------
def pull_air_rate(level, df):
    """Pull AIR Rate -- PATCHED. Supersedes `Baseball Functions.ipynb` cell 56.

    Three defects closed:
      O-7  cell 56 read `bip.loc_x` / `bip.loc_y`, which do not exist in the
           parquet schema. It could not execute. Now derives them (PA-L1).
      D5   the dead `total_pulls` frame was computed and never used. Removed.
      DEN-1 the denominator was ALL BIP including untracked, so an unclassifiable
           BIP was silently scored 'not a pull air'. Now classifiable BIP.

    ** BREAKING **: published v0 values do not reproduce. The denominator
    shrinks by the untracked-BIP count (0.08% of 2026 Phillies BIP). Consumers
    must re-run. See `08_version_manifest.md`.

    Definition unchanged: pulled batted balls that are not ground balls, over
    balls in play.
    """
    level = list(level)
    bip = df if 'hit_direction' in df.columns else build_bip(level, df)

    pulls = bip[bip.hit_direction == 'Pull']
    air_pulls = (pulls[pulls.bb_type != 'ground_ball']
                 .groupby(level, as_index=False, dropna=False)
                 .agg(pull_airs=('des', 'size')))

    par = (bip.groupby(level, as_index=False, dropna=False)
              .agg(total_bips=('des', 'size'))
              .merge(air_pulls, on=level, how='left'))
    par['pull_airs'] = par.pull_airs.fillna(0).astype(int)
    par['pull_air_rate'] = np.where(par.total_bips > 0, par.pull_airs / par.total_bips, np.nan)
    par['below_floor'] = par.total_bips < BIP_FLOOR
    return par
