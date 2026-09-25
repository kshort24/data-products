"""
dp_uc48_kernel.py — governed kernel for UC #48 / uc-pps-033
"The Tick and a Half — Jonathan Bowlan 2026 Recap"

INHERITANCE POLICY (see control-plane 03_governance.md §0, Rule-1):
  * Section A  — INHERITED BY IMPORT from `dp_uc44_kernel.py` (uc-pps-030), sha256-pinned:
      get_stats, measure_calcs, mcgs, nresults, SWINGS, WHIFFS, whiff_rate, chase_rate,
      pitch_mix, fpsr, putaway_rate, two_prop_z, apply_woba_weights, load_phils.
  * Section A2 — VERBATIM TRANSCRIPTIONS of already-approved house code (not re-derived):
      runs_created ........ `Baseball Functions.ipynb` cell 31 (approved term, uc-pos-012 03 §1)
      GROUP_MAP ........... `September 2026.ipynb` cell 5 (pitch_group derivation)
      xwobacon ............ uc-pps-021 open item O1 (via dp_uc30), BIP-only xwOBA
  * Section C  — NEW to this UC, PROVISIONAL and unratified:
      CF-1 career_frame · SR-1 season_recap (the client's cell, functionalized as he asked) ·
      KP-1 house_percentile · AR-2 arsenal_table · US-1 appearance_log / usage_summary ·
      VE-1 velo_by_outing_bucket · CS-1 count_state · PA-1 persona_ledger
    Run Value per 100 (`rv100`) is the uc-pps-032 glossary term (second independent use).

Data plane    : C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB
Control plane : C:\\Users\\Kellen\\OneDrive\\Documents\\Agents for Data Products
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Parent kernel (uc-pps-030) — import, never copy
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
for _p in [os.environ.get("MLB_DATA_ROOT"), str(_HERE), "/mnt/user-data/uploads/MLB",
           r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]:
    if _p and (Path(_p) / "dp_uc44_kernel.py").exists() and _p not in sys.path:
        sys.path.insert(0, _p)
import dp_uc44_kernel as K44  # noqa: E402

PARENT_KERNEL_SHA256 = "a2c119096db24fdbfca4ca7f79b9dcb32c379d6f1ec9566aa7376837711582e3"
ROOT = K44.ROOT
SWINGS, WHIFFS = K44.SWINGS, K44.WHIFFS
nresults, whiff_rate, chase_rate, pitch_mix, fpsr = (
    K44.nresults, K44.whiff_rate, K44.chase_rate, K44.pitch_mix, K44.fpsr)
two_prop_z, apply_woba_weights, load_phils = K44.two_prop_z, K44.apply_woba_weights, K44.load_phils
PITCH_KEY = ["game_pk", "at_bat_number", "pitch_number"]


def parent_kernel_hash() -> str:
    return hashlib.sha256(Path(K44.__file__).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# House constants (brand-center-mcp :: get_brand_guidelines values)
# ---------------------------------------------------------------------------
PHILLIES_RED, PHILLIES_NAVY, PHILLIES_CREAM = "#E81828", "#002D72", "#F3E5AB"
NEUTRAL_GRAY, LIGHT_GRAY = "#8C8C8C", "#D9D9D9"
PITCH_COLORS = K44.PITCH_COLORS

# Entity lock — MLBAM id, never a name filter
SUBJECT_ID = 680742                      # Jonathan Bowlan, RHP
SUBJECT_NAME = "Bowlan, Jonathan"        # used ONLY to reproduce the client's own frame (HP family)
SUBJECT_FILE = "bowlan.parquet"          # dedicated player file in data/opponents/
RECAP_SEASON = 2026
PRIOR_SEASON = 2025
ANCHOR_GAME_DATE = "2026-09-23"          # last game in phils_2026.parquet at build time
LAST_APPEARANCE = "2026-09-17"           # carry-in context: exit vs NYM (reported right groin strain, no IL)
STAFF_EXCLUDE_YEARS = (2017,)            # client's exclusion; DQ-11 measures why

# ============================================================================
# SECTION A2 — VERBATIM transcriptions of approved house code
# ============================================================================
# `Baseball Functions.ipynb` cell 31 — approved term "Runs Created" (house meaning: runs that
# scored during the plate appearances a pitcher threw; NOT Bill James RC — see 03 §1 glossary note)
def runs_created(level, df):
    if isinstance(level, str):
        level = [level]
    rdf = df.groupby(level + ['game_pk', 'at_bat_number'], as_index=False
                     ).agg(min_bs=('bat_score', 'min'),
                           max_pbs=('post_bat_score', 'max'))
    rdf['runs_created'] = rdf.max_pbs - rdf.min_bs
    return rdf.groupby(level, as_index=False).agg(runs_created=('runs_created', 'sum'))


# `September 2026.ipynb` cell 5 — pitch_group derivation
GROUP_MAP = {
    'Fastballs': ['FF', 'SI', 'FC'],
    'Offspeed': ['CH', 'FS', 'FO', 'SC'],
    'Breaking': ['KC', 'CU', 'CS', 'SL', 'ST', 'SV', 'KN'],
}
TYPE_TO_GROUP = {ptype: group for group, ptypes in GROUP_MAP.items() for ptype in ptypes}


def add_pitch_group(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['pitch_group'] = df['pitch_type'].map(TYPE_TO_GROUP).fillna('Other')
    return df


# uc-pps-021 O1 (carried in dp_uc30): the pitch-level get_stats.xwoba column is quarantined
def xwobacon(level, df):
    if isinstance(level, str):
        level = [level]
    bip = df[df.type == "X"]
    out = bip.groupby(level, as_index=False).agg(
        xwobacon=("estimated_woba_using_speedangle", "mean"),
        xwobacon_bip=("estimated_woba_using_speedangle", "size"))
    return out.round(3)


# ============================================================================
# SECTION C — NEW (provisional)
# ============================================================================
def rv100(s: pd.Series) -> float:
    """Run Value per 100 (uc-pps-032 glossary): -100 x mean(delta_run_exp), pitcher POV."""
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(-100 * s.mean()) if len(s) else np.nan


# ---- CF-1 career_frame --------------------------------------------------------
def _read_subject_file(root: Path) -> pd.DataFrame:
    f = root / "data" / "opponents" / SUBJECT_FILE
    return apply_woba_weights(pd.read_parquet(f))


def career_frame(pitcher_id: int = SUBJECT_ID, root: Path | None = None,
                 years=range(2015, 2027)) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Every regular-season pitch thrown by `pitcher_id`, de-duplicated across sources.

    Sources, in precedence order (first wins on PITCH_KEY):
      PHI     phils_* rows, phillies_role == 'pitching'   (he pitched for Philadelphia)
      FILE    data/opponents/<subject file>                (dedicated player pull)
      VS_PHI  phils_* rows, phillies_role == 'batting'     (he pitched against Philadelphia)
    Returns (frame, source_receipt).
    """
    root = root or ROOT
    ph = load_phils(years=years, role=None, regular_only=True)
    ph = ph[ph.pitcher == pitcher_id].copy()
    ph['src'] = np.where(ph.phillies_role == 'pitching', 'PHI', 'VS_PHI')
    fl = _read_subject_file(root)
    fl = fl[(fl.pitcher == pitcher_id) & (fl.game_type == 'R')].copy()
    fl['src'] = 'FILE'
    raw = pd.concat([ph, fl], ignore_index=True, sort=False)
    order = {'PHI': 0, 'FILE': 1, 'VS_PHI': 2}
    raw['_o'] = raw.src.map(order)
    receipt = raw.groupby(['game_year', 'src'], as_index=False).agg(rows=('pitch_type', 'size'))
    df = (raw.sort_values('_o').drop_duplicates(subset=PITCH_KEY, keep='first')
             .drop(columns='_o').sort_values(['game_date', 'at_bat_number', 'pitch_number']))
    kept = df.groupby(['game_year', 'src'], as_index=False).agg(kept=('pitch_type', 'size'))
    receipt = receipt.merge(kept, on=['game_year', 'src'], how='left').fillna({'kept': 0})
    receipt['dropped_as_duplicate'] = receipt.rows - receipt.kept
    df = add_pitch_group(df.reset_index(drop=True))
    df['player_name_display'] = 'Jonathan Bowlan'
    return df, receipt


def kellen_frame(root: Path | None = None) -> pd.DataFrame:
    """The client's own frame, reproduced exactly (HP family only):
       pd.concat([nphl[nphl.player_name == pn], pps[pps.player_name == pn]]).
    `nphl` for this subject is exactly the dedicated file (byte search, 01 §3). `pps` is the
    Phillies pitching log with game_type not in ('S','E') — postseason types are KEPT."""
    root = root or ROOT
    fl = _read_subject_file(root)
    ph = load_phils(years=range(2015, 2027), role='pitching', regular_only=False)
    ph = ph[~ph.game_type.isin(['S', 'E'])]
    jb = pd.concat([fl[fl.player_name == SUBJECT_NAME], ph[ph.player_name == SUBJECT_NAME]])
    return add_pitch_group(jb)


# ---- SR-1 season_recap: the client's cell, functionalized ---------------------
RECAP_KPIS = ['pitches', 'plate_apps', 'ba', 'obp', 'slg', 'ops', 'woba', 'krate', 'bbrate', 'hr_rate',
              'runs_created', 'games', 'rc_per_pa', 'rc_per_gm', 'ff_vert', 'ff_velo', 'ff_spin',
              'whiff_rate_breaking', 'whiff_rate_iz_ff']


def pitch_mix_by_season(df: pd.DataFrame, player_name: str) -> pd.DataFrame:
    """The client's `for gy in jb.game_year.unique()` loop — without leaking `gy` (HP-18)."""
    out = []
    for yr in sorted(df.game_year.unique().tolist()):
        pm = pitch_mix(df[df.game_year == yr])
        pm['game_year'] = yr
        pm['player_name'] = player_name
        out.append(pm)
    return pd.concat(out, ignore_index=True)


def season_recap(df: pd.DataFrame, level=('player_name', 'game_year', 'p_throws'),
                 governed: bool = True) -> pd.DataFrame:
    """SR-1. Reproduces the client's cell 115 table.

    governed=False → the notebook exactly (inner-join whiff merges, fillna(0), ff_* read off the
                     ROUNDED pitch_mix: vert quantized in 1.2-inch steps — O-25).
    governed=True  → same KPIs; ff_vert/ff_velo/ff_spin from UNROUNDED four-seam means, NaN kept
                     as NaN, and denominators carried beside every rate.
    """
    level = list(level)
    pn = df.player_name.mode().iat[0] if 'player_name' in level else None
    pms = pitch_mix_by_season(df, pn)
    z = (nresults(level, df)
         .merge(runs_created(level, df), on=level, how='left', suffixes=('', '_rc'))
         .merge(df.groupby(level, as_index=False).agg(games=('game_pk', 'nunique')),
                on=level, how='left', suffixes=('', '_gms'))
         .merge(pms[(pms.player_name == pn) & (pms.pitch_type == 'FF')],
                on=['player_name', 'game_year'], how='left', suffixes=('', '_ff'))
         .merge(whiff_rate(level, df), on=level, how='left', suffixes=('', '_wr'))
         .merge(chase_rate(level, df), on=level, how='left', suffixes=('', '_cr'))
         .merge(whiff_rate(level, df[df.pitch_group == 'Breaking']), on=level, how='left',
                suffixes=('', '_breaking'))
         .merge(whiff_rate(level, df[(df.pitch_type == 'FF') & (df.zone < 10)]), on=level, how='left',
                suffixes=('', '_iz_ff')))
    if not governed:
        z = z.fillna(0)
        z['ff_vert'] = round(z.pfx_z * 12, 1)
        z['ff_velo'] = round(z.release_speed, 1)
        z['ff_spin'] = round(z.release_spin_rate, 1)
    else:
        ff = df[df.pitch_type == 'FF'].groupby(level, as_index=False).agg(
            ff_n=('release_speed', 'size'), ff_velo_u=('release_speed', 'mean'),
            ff_spin_u=('release_spin_rate', 'mean'), ff_pfx_z_u=('pfx_z', 'mean'),
            ff_pfx_x_u=('pfx_x', 'mean'))
        z = z.merge(ff, on=level, how='left')
        z['ff_vert'] = z.ff_pfx_z_u * 12
        z['ff_hb'] = z.ff_pfx_x_u * 12
        z['ff_velo'] = z.ff_velo_u
        z['ff_spin'] = z.ff_spin_u
        z['ff_vert_notebook'] = round(z.pfx_z * 12, 1)       # the quantized value, kept for HP-14
    z['rc_per_pa'] = z.runs_created / z.plate_apps
    z['rc_per_gm'] = z.runs_created / z.games
    return z


# ---- KP-1 house percentile -----------------------------------------------------
def house_pitcher_seasons(years=range(2015, 2027), min_pa: int = 100) -> pd.DataFrame:
    """KP-1 population: Phillies pitcher-seasons (pitching role, regular season), >= min_pa PA."""
    ph = load_phils(years=years, role='pitching', regular_only=True)
    r = nresults(['pitcher', 'game_year'], ph)
    names = ph.groupby('pitcher').player_name.agg(lambda s: s.mode().iat[0]).rename('name')
    r = r.merge(names, on='pitcher', how='left')
    r = r.merge(whiff_rate(['pitcher', 'game_year'], ph)[['pitcher', 'game_year', 'whiff_rate']],
                on=['pitcher', 'game_year'], how='left')
    r = r.merge(chase_rate(['pitcher', 'game_year'], ph)[['pitcher', 'game_year', 'chase_rate']],
                on=['pitcher', 'game_year'], how='left')
    return r[r.plate_apps >= min_pa].reset_index(drop=True)


def house_percentile(pop: pd.DataFrame, col: str, value: float, higher_is_better: bool = True) -> dict:
    """KP-1. Percentile = share of the population strictly worse than `value` (x100, floor);
    rank = 1 + count strictly better. Ties share the better rank."""
    v = pop[col].dropna()
    worse = (v < value) if higher_is_better else (v > value)
    better = (v > value) if higher_is_better else (v < value)
    return dict(n=int(len(v)), percentile=int(np.floor(100 * worse.mean())), rank=int(better.sum() + 1))


# ---- AR-2 arsenal table ----------------------------------------------------------
def arsenal_table(df: pd.DataFrame, by=('game_year',)) -> pd.DataFrame:
    by = list(by)
    d = df.copy()
    d['_sw'] = d.description.isin(SWINGS)
    d['_wh'] = d.description.isin(WHIFFS)
    d['_ooz'] = d.zone > 9
    d['_chase'] = d._ooz & d._sw
    d['_iz'] = d.zone.between(1, 9)
    g = d.groupby(by + ['pitch_type', 'pitch_name'], as_index=False).agg(
        n=('pitch_type', 'size'), velo=('release_speed', 'mean'), spin=('release_spin_rate', 'mean'),
        pfx_z=('pfx_z', 'mean'), pfx_x=('pfx_x', 'mean'), ext=('release_extension', 'mean'),
        plate_z=('plate_z', 'mean'), swings=('_sw', 'sum'), whiffs=('_wh', 'sum'),
        ooz=('_ooz', 'sum'), chases=('_chase', 'sum'), in_zone=('_iz', 'sum'),
        rv100=('delta_run_exp', rv100))
    tot = d.groupby(by, as_index=False).agg(total=('pitch_type', 'size'))
    g = g.merge(tot, on=by)
    g['usage'] = g.n / g.total
    g['ivb_in'] = g.pfx_z * 12
    g['hb_in'] = g.pfx_x * 12
    g['whiff_rate'] = np.where(g.swings > 0, g.whiffs / g.swings.where(g.swings > 0), np.nan)
    g['chase_rate'] = np.where(g.ooz > 0, g.chases / g.ooz.where(g.ooz > 0), np.nan)
    g['zone_rate'] = g.in_zone / g.n
    x = xwobacon(by + ['pitch_type'], d)
    g = g.merge(x, on=by + ['pitch_type'], how='left')
    return g.sort_values(by + ['n'], ascending=[True] * len(by) + [False]).reset_index(drop=True)


# ---- CS-1 count state ------------------------------------------------------------
def count_state(df: pd.DataFrame) -> pd.Series:
    """CS-1: '2K' if strikes == 2 (takes precedence), else behind (balls > strikes),
    ahead (strikes > balls), even."""
    return pd.Series(np.select([df.strikes == 2, df.balls > df.strikes, df.strikes > df.balls],
                               ['2K', 'behind', 'ahead'], 'even'), index=df.index)


# ---- US-1 appearance log / usage summary -------------------------------------------
def appearance_log(df: pd.DataFrame) -> pd.DataFrame:
    """US-1. One row per appearance (game_pk). Entry state read from the FIRST pitch of the outing
    (sorted by at_bat_number, pitch_number) — never `groupby().first()` on unsorted rows."""
    d = df.sort_values(['game_pk', 'at_bat_number', 'pitch_number'])
    # head(1), NOT first(): GroupBy.first() returns the first NON-NULL value per column, which reads
    # on_1b/on_2b/on_3b from any later pitch of the outing (build-caught defect B-1, 05 §4)
    first = d.groupby('game_pk', as_index=False).head(1)
    agg = d.groupby('game_pk', as_index=False).agg(
        pitches=('pitch_type', 'size'), inn_first=('inning', 'min'), inn_last=('inning', 'max'),
        batters=('at_bat_number', 'nunique'))
    rc = runs_created(['game_pk'], d)
    ff = d[d.pitch_type == 'FF'].groupby('game_pk', as_index=False).agg(
        ff_n=('release_speed', 'size'), ff_velo=('release_speed', 'mean'), ff_max=('release_speed', 'max'))
    a = (first[['game_pk', 'game_date', 'game_year', 'home_team', 'away_team', 'inning', 'outs_when_up',
                'on_1b', 'on_2b', 'on_3b', 'bat_score', 'fld_score', 'pitcher_days_since_prev_game']]
         .merge(agg, on='game_pk').merge(rc, on='game_pk', how='left').merge(ff, on='game_pk', how='left'))
    a['entry_inning'] = a.inning
    a['entry_outs'] = a.outs_when_up
    a['entry_runners'] = a[['on_1b', 'on_2b', 'on_3b']].notna().sum(axis=1)
    a['entry_lead'] = a.fld_score - a.bat_score          # pitcher POV: + = his club leads
    a['multi_inning'] = a.inn_last > a.inn_first
    a['rest_days'] = a.pitcher_days_since_prev_game
    a['back_to_back'] = a.rest_days == 1
    a['close_late'] = (a.entry_inning >= 7) & (a.entry_lead.abs() <= 2)
    return a.drop(columns=['inning', 'outs_when_up', 'on_1b', 'on_2b', 'on_3b']).sort_values('game_date')


def usage_summary(apps: pd.DataFrame) -> pd.DataFrame:
    return apps.groupby('game_year', as_index=False).agg(
        appearances=('game_pk', 'size'), pitches_per_app=('pitches', 'mean'),
        multi_inning_share=('multi_inning', 'mean'), clean_entry_share=('entry_runners', lambda s: (s == 0).mean()),
        start_of_inning_share=('entry_outs', lambda s: (s == 0).mean()),
        late_entry_share=('entry_inning', lambda s: (s >= 7).mean()),
        close_late_share=('close_late', 'mean'), back_to_backs=('back_to_back', 'sum'),
        median_rest=('rest_days', 'median'), batters_per_app=('batters', 'mean'))


# ---- VE-1 velocity by pitch-of-outing ------------------------------------------------
def velo_by_outing_bucket(df: pd.DataFrame, pitch_type='FF', edges=(0, 10, 20, 999),
                          labels=('1-10', '11-20', '21+')) -> pd.DataFrame:
    """VE-1: separates ROLE (shorter outings) from ARM (faster at every stage of an outing)."""
    d = df.sort_values(['game_pk', 'at_bat_number', 'pitch_number']).copy()
    d['pitch_of_outing'] = d.groupby('game_pk').cumcount() + 1
    d['bucket'] = pd.cut(d.pitch_of_outing, bins=list(edges), labels=list(labels))
    d = d[d.pitch_type == pitch_type]
    return d.groupby(['game_year', 'bucket'], as_index=False, observed=True).agg(
        n=('release_speed', 'size'), velo=('release_speed', 'mean'))


# ---- PA-1 persona ledger ---------------------------------------------------------------
def signature_verdict(before: float, after: float, direction: int, threshold: float,
                      p_value: float | None = None) -> str:
    """PA-1 decision rule for one signature.
    direction=+1 means the hypothesis predicts an increase, -1 predicts a decrease.
      PRESENT   moved the predicted way by >= threshold (and p < .05 when a test applies)
      WEAK      moved the predicted way, but < threshold or p >= .05
      ABSENT    |change| < threshold/4
      CONTRA    moved the opposite way by >= threshold
    """
    if before is None or after is None or np.isnan(before) or np.isnan(after):
        return "NO DATA"
    delta = (after - before) * direction
    if abs(after - before) < threshold / 4:
        return "ABSENT"
    if delta >= threshold and (p_value is None or p_value < 0.05):
        return "PRESENT"
    if delta > 0:
        return "WEAK"
    if -delta >= threshold:
        return "CONTRA"
    return "ABSENT"


def strength_from_signatures(verdicts: list[str]) -> str:
    """Roll-up: STRONG if every signature PRESENT; SUPPORTED if majority PRESENT and none CONTRA;
    MIXED if any CONTRA alongside a PRESENT; UNSUPPORTED otherwise. 'NOT OBSERVABLE' rows are added
    by the build for actions the log cannot see."""
    n = len(verdicts)
    p = verdicts.count("PRESENT")
    c = verdicts.count("CONTRA")
    if n and p == n:
        return "STRONG"
    if c and p:
        return "MIXED"
    if p * 2 >= n and not c:
        return "SUPPORTED"
    return "UNSUPPORTED"
