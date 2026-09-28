"""
dp_uc49_kernel.py — governed kernel for UC #49 / uc-pps-034
"The Chase — Jesús Luzardo 2026 Recap"

INHERITANCE POLICY (control-plane 03_governance.md §0, Rule-1):
  * Section A  — INHERITED BY IMPORT, sha256-pinned, never copied:
      dp_uc48_kernel (uc-pps-033): season_recap (SR-1, SECOND USE → ratification), runs_created,
        xwobacon, GROUP_MAP/add_pitch_group, arsenal_table (AR-2), count_state (CS-1),
        appearance_log (US-1), house_percentile (KP-1), rv100
      dp_uc44_kernel (uc-pps-030, via K48): nresults, whiff_rate, chase_rate, pitch_mix, fpsr,
        two_prop_z, apply_woba_weights, pitch_map_centroid (PM-1), SWINGS, WHIFFS
  * Section B  — NON-BREAKING GENERALIZATIONS of provisional UC48 objects:
      CF-2 career_frame(pitcher_id, subject_file, …) — CF-1 hard-codes Bowlan's id, file and display
           name; CF-2 takes them as parameters and adds the NPHL_ID source (id scan of every
           opponent file), because batter-keyed pulls also hold the subject's pitches.
      LP-1 load_phils_cols — K44.load_phils with a column projection (same filters, same weights);
           the laptop VM has 3 GB of RAM and the full 119-column log does not fit comfortably.
      KP-1b house_pitcher_seasons_from(frame) — K48.house_pitcher_seasons' logic on a supplied frame.
  * Section C  — NEW to this UC, PROVISIONAL and unratified:
      NF-1 nphl_name_frame (reproduces get_nphillies_data's global keep-first dedup exactly)
      GS-1 game_score (Tango v2 form, log-derived) · OU-1 outs_recorded
      CX-1 context_frame (the client's "Phillies pitcher-seasons, min 150 pitches")
      VB-1 first_n_velo (velocity over the first N pitches of an outing)
      OC-1 october_card (pre-registered postseason signatures + decision rule)
      BN-1 batter_names (modal des-parse, house rule: never hand-key ids)

Data plane    : C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB
Control plane : C:\\Users\\Kellen\\OneDrive\\Documents\\Agents for Data Products
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
for _p in [os.environ.get("MLB_DATA_ROOT"), str(_HERE), "/mnt/user-data/uploads/MLB",
           r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]:
    if _p and (Path(_p) / "dp_uc48_kernel.py").exists() and _p not in sys.path:
        sys.path.insert(0, _p)
import dp_uc48_kernel as K48  # noqa: E402

K44 = K48.K44
PARENT_KERNEL_SHA256 = "0f63857a103253ef2675190b383e064237a5e3d3c84be9fafdd67d55ecb21d32"       # dp_uc48_kernel
GRANDPARENT_KERNEL_SHA256 = "a2c119096db24fdbfca4ca7f79b9dcb32c379d6f1ec9566aa7376837711582e3"  # dp_uc44_kernel
ROOT = K44.ROOT
PITCH_KEY = K48.PITCH_KEY
SWINGS, WHIFFS = K44.SWINGS, K44.WHIFFS
nresults, whiff_rate, chase_rate, pitch_mix, fpsr = (K44.nresults, K44.whiff_rate, K44.chase_rate,
                                                     K44.pitch_mix, K44.fpsr)
two_prop_z, apply_woba_weights, pitch_map_centroid = K44.two_prop_z, K44.apply_woba_weights, K44.pitch_map_centroid
season_recap, runs_created, xwobacon, add_pitch_group = (K48.season_recap, K48.runs_created, K48.xwobacon,
                                                          K48.add_pitch_group)
arsenal_table, count_state, house_percentile, rv100 = (
    K48.arsenal_table, K48.count_state, K48.house_percentile, K48.rv100)


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def assert_lineage():
    assert sha(K48.__file__) == PARENT_KERNEL_SHA256, "dp_uc48_kernel drifted"
    assert sha(K44.__file__) == GRANDPARENT_KERNEL_SHA256, "dp_uc44_kernel drifted"


# ---------------------------------------------------------------------------
# House constants (brand center values, as carried by uc-pps-032/033)
# ---------------------------------------------------------------------------
PHILLIES_RED, PHILLIES_NAVY, PHILLIES_BLUE, PHILLIES_CREAM = "#E81828", "#002D72", "#284898", "#F3E5AB"
NEUTRAL_GRAY, LIGHT_GRAY = "#8C8C8C", "#D9D9D9"
PITCH_COLORS = K44.PITCH_COLORS

# Entity lock — MLBAM id, never a name filter
SUBJECT_ID = 666200                      # Jesús Luzardo, LHP
SUBJECT_NAME = "Luzardo, Jesús"          # used ONLY to reproduce the client's own frame (HP family)
SUBJECT_DISPLAY = "Jesús Luzardo"
SUBJECT_FILE = "luzardo.parquet"
RECAP_SEASON, PRIOR_SEASON = 2026, 2025
ANCHOR_GAME_DATE = "2026-09-26"          # last regular-season game in phils_2026.parquet at build time
LAST_APPEARANCE = "2026-09-07"           # Labor Day CGSO; nothing after it in the log
LABOR_DAY_GAME_PK = 823415
ALL_STAR_BREAK = "2026-07-13"            # first-half = game_date < this (uc-pps-017's cut: 19 starts)
POSTSEASON_TYPES = ("F", "D", "L", "W")
CONTEXT_MIN_PITCHES = 150                # the client's `zc.pitches > 149`
KP_MIN_PA = 100                          # KP-1 floor (uc-pps-033)

COLS = ['pitcher', 'player_name', 'batter', 'game_pk', 'game_date', 'game_year', 'game_type', 'home_team',
        'away_team', 'inning', 'inning_topbot', 'at_bat_number', 'pitch_number', 'pitch_type', 'pitch_name',
        'release_speed', 'release_spin_rate', 'release_extension', 'pfx_x', 'pfx_z', 'plate_x', 'plate_z',
        'zone', 'sz_top', 'sz_bot', 'description', 'des', 'events', 'type', 'balls', 'strikes', 'outs_when_up',
        'on_1b', 'on_2b', 'on_3b', 'bat_score', 'fld_score', 'post_bat_score', 'post_fld_score', 'stand',
        'p_throws', 'estimated_woba_using_speedangle', 'estimated_ba_using_speedangle', 'launch_speed',
        'launch_angle', 'delta_run_exp', 'n_thruorder_pitcher', 'pitcher_days_since_prev_game', 'bb_type']
OPP_DIR = ROOT / "data" / "opponents"


def _cols_in(f: Path, want=COLS) -> list:
    """Opponent pulls were cached across several Statcast schema versions; project only what exists."""
    import pyarrow.parquet as pq
    have = set(pq.read_schema(f).names)
    return [c for c in want if c in have]


# ============================================================================
# SECTION B — non-breaking generalizations
# ============================================================================
def load_phils_cols(years=range(2015, 2027), role=None, regular_only=True, cols=COLS) -> pd.DataFrame:
    """LP-1. K44.load_phils with a column projection. Filters and weights are K44's, unchanged."""
    fs = [ROOT / 'data' / 'phillies' / f'phils_{y}.parquet' for y in years]
    frames = [pd.read_parquet(f, columns=_cols_in(f, cols + ['phillies_role'])) for f in fs]   # schema varies by season
    df = pd.concat(frames, ignore_index=True)
    if regular_only:
        df = df[df.game_type == 'R']
    if role:
        df = df[df.phillies_role == role]
    return apply_woba_weights(df.copy())


def opponent_id_scan(pitcher_id: int = SUBJECT_ID, subject_name: str = SUBJECT_NAME) -> pd.DataFrame:
    """Every opponent parquet holding rows with pitcher == id (reads the id column only).
    Replaces uc-pps-033's byte search, which cannot see dictionary-compressed strings and
    cannot see batter-keyed pulls (their player_name is the batter). Finding BS-1."""
    rows = []
    for f in sorted(OPP_DIR.glob("*.parquet")):
        d = pd.read_parquet(f, columns=['pitcher', 'game_year', 'game_type', 'player_name'])
        x = d[d.pitcher == pitcher_id]
        if len(x):
            rows.append(dict(file=f.name, rows=len(x), seasons=",".join(str(y) for y in sorted(x.game_year.unique())),
                             game_types=",".join(sorted(x.game_type.unique())),
                             player_name_is_subject=bool((x.player_name == subject_name).all()),
                             player_name_modal=x.player_name.mode().iat[0]))
    return pd.DataFrame(rows)


def career_frame(pitcher_id: int = SUBJECT_ID, subject_file: str = SUBJECT_FILE, display: str = SUBJECT_DISPLAY,
                 years=range(2015, 2027), game_types=("R",), scan: pd.DataFrame | None = None,
                 ph: pd.DataFrame | None = None):
    """CF-2. Every pitch thrown by `pitcher_id` with game_type in `game_types`, de-duplicated across sources.

    Precedence (first wins on PITCH_KEY):
      PHI      phils_* rows, phillies_role == 'pitching'
      FILE     data/opponents/<subject_file>            (pitcher-keyed dedicated pull)
      NPHL_ID  every other opponent file, rows with pitcher == id (batter-keyed pulls)
      VS_PHI   phils_* rows, phillies_role == 'batting'
    Returns (frame, source_receipt)."""
    ph = ph if ph is not None else load_phils_cols(years=years, role=None, regular_only=False)
    ph = ph[(ph.pitcher == pitcher_id) & ph.game_type.isin(game_types)].copy()
    ph['src'] = np.where(ph.phillies_role == 'pitching', 'PHI', 'VS_PHI')
    parts = [ph]
    scan = scan if scan is not None else opponent_id_scan(pitcher_id)
    for f in scan.file:
        d = pd.read_parquet(OPP_DIR / f, columns=_cols_in(OPP_DIR / f))
        d = d[(d.pitcher == pitcher_id) & d.game_type.isin(game_types)].copy()
        d['src'] = 'FILE' if f == subject_file else 'NPHL_ID'
        d['src_file'] = f
        parts.append(apply_woba_weights(d))
    raw = pd.concat(parts, ignore_index=True, sort=False)
    raw['src_file'] = raw['src_file'].fillna('phils_*')
    order = {'PHI': 0, 'FILE': 1, 'NPHL_ID': 2, 'VS_PHI': 3}
    raw['_o'] = raw.src.map(order)
    receipt = raw.groupby(['game_year', 'src'], as_index=False).agg(rows=('pitch_type', 'size'))
    df = (raw.sort_values(['_o', 'src_file']).drop_duplicates(subset=PITCH_KEY, keep='first')
             .drop(columns='_o').sort_values(['game_date', 'game_pk', 'at_bat_number', 'pitch_number']))
    kept = df.groupby(['game_year', 'src'], as_index=False).agg(kept=('pitch_type', 'size'))
    receipt = receipt.merge(kept, on=['game_year', 'src'], how='left').fillna({'kept': 0})
    receipt['dropped_as_duplicate'] = receipt.rows - receipt.kept
    df = add_pitch_group(df.reset_index(drop=True))
    df['player_name'] = SUBJECT_NAME          # the level key the client's cell groups on (display only)
    df['player_name_display'] = display
    return df, receipt


def house_pitcher_seasons_from(ph: pd.DataFrame, min_pa: int = KP_MIN_PA) -> pd.DataFrame:
    """KP-1b. K48.house_pitcher_seasons' logic on a supplied (pitching-role, regular-season) frame."""
    r = nresults(['pitcher', 'game_year'], ph)
    names = ph.groupby('pitcher').player_name.agg(lambda s: s.mode().iat[0]).rename('name')
    r = r.merge(names, on='pitcher', how='left')
    r = r.merge(whiff_rate(['pitcher', 'game_year'], ph)[['pitcher', 'game_year', 'whiff_rate']],
                on=['pitcher', 'game_year'], how='left')
    r = r.merge(chase_rate(['pitcher', 'game_year'], ph)[['pitcher', 'game_year', 'chase_rate']],
                on=['pitcher', 'game_year'], how='left')
    return r[r.plate_apps >= min_pa].reset_index(drop=True)


# ============================================================================
# SECTION C — NEW (provisional)
# ============================================================================
def nphl_name_frame(name: str = SUBJECT_NAME) -> tuple[pd.DataFrame, int]:
    """NF-1. The client's `nphl[nphl.player_name == name]`, reproduced exactly.
    get_nphillies_data() concatenates every opponent parquet in sorted order and drops duplicate
    PITCH_KEY rows keep='first'. A pitch that also sits in an alphabetically earlier, batter-keyed
    file survives there (player_name = the batter) and is lost to a pitcher-name filter (O-26).
    Returns (frame, n_lost_to_dedup)."""
    files = sorted(OPP_DIR.glob("*.parquet"))
    keys = []
    for i, f in enumerate(files):
        k = pd.read_parquet(f, columns=PITCH_KEY + ['player_name'])
        k['_file_i'] = i
        k['_row'] = np.arange(len(k))
        keys.append(k)
    allk = pd.concat(keys, ignore_index=True)
    allk['_first'] = ~allk.duplicated(subset=PITCH_KEY, keep='first')
    hit = allk[allk.player_name == name]
    lost = int((~hit._first).sum())
    parts = []
    for i in sorted(hit._file_i.unique()):
        d = pd.read_parquet(files[i], columns=_cols_in(files[i]))
        keep_rows = hit[(hit._file_i == i) & hit._first]._row.values
        parts.append(d.iloc[keep_rows])
    out = apply_woba_weights(pd.concat(parts, ignore_index=True)) if parts else pd.DataFrame(columns=COLS)
    return out, lost


def kellen_frame(ph: pd.DataFrame | None = None) -> tuple[pd.DataFrame, int]:
    """The client's cell 118 frame, exactly: pd.concat([pps[pps.player_name == pn], nphl[nphl.player_name == pn]]).
    `pps` = Phillies pitching log with game_type not in ('S','E') — postseason types are KEPT."""
    ph = ph if ph is not None else load_phils_cols(years=range(2015, 2027), role=None, regular_only=False)
    ph = ph[(ph.phillies_role == 'pitching') & ~ph.game_type.isin(['S', 'E'])]
    nf, lost = nphl_name_frame(SUBJECT_NAME)
    jl = pd.concat([ph[ph.player_name == SUBJECT_NAME], nf], ignore_index=True, sort=False)
    return add_pitch_group(jl), lost


def runs_by_game(d: pd.DataFrame) -> pd.DataFrame:
    """ENV-1 fix. `runs_created(['game_pk'], d)` groups by ['game_pk', 'game_pk', 'at_bat_number'];
    pandas 3.x tolerates the duplicate key, pandas 2.3 (the laptop VM) raises. Alias the key instead."""
    return runs_created(['_gk'], d.assign(_gk=d.game_pk)).rename(columns={'_gk': 'game_pk'})


def appearance_log(df: pd.DataFrame) -> pd.DataFrame:
    """US-1b: K48 US-1 `appearance_log`, transcribed verbatim except the one ENV-1 line (runs_by_game).
    Non-breaking; recommended upstream as dp_uc48_kernel v1.0.1 (E-2)."""
    d = df.sort_values(['game_pk', 'at_bat_number', 'pitch_number'])
    first = d.groupby('game_pk', as_index=False).head(1)
    agg = d.groupby('game_pk', as_index=False).agg(
        pitches=('pitch_type', 'size'), inn_first=('inning', 'min'), inn_last=('inning', 'max'),
        batters=('at_bat_number', 'nunique'))
    rc = runs_by_game(d)
    ff = d[d.pitch_type == 'FF'].groupby('game_pk', as_index=False).agg(
        ff_n=('release_speed', 'size'), ff_velo=('release_speed', 'mean'), ff_max=('release_speed', 'max'))
    a = (first[['game_pk', 'game_date', 'game_year', 'home_team', 'away_team', 'inning', 'outs_when_up',
                'on_1b', 'on_2b', 'on_3b', 'bat_score', 'fld_score', 'pitcher_days_since_prev_game']]
         .merge(agg, on='game_pk').merge(rc, on='game_pk', how='left').merge(ff, on='game_pk', how='left'))
    a['entry_inning'] = a.inning
    a['entry_outs'] = a.outs_when_up
    a['entry_runners'] = a[['on_1b', 'on_2b', 'on_3b']].notna().sum(axis=1)
    a['entry_lead'] = a.fld_score - a.bat_score
    a['multi_inning'] = a.inn_last > a.inn_first
    a['rest_days'] = a.pitcher_days_since_prev_game
    a['back_to_back'] = a.rest_days == 1
    a['close_late'] = (a.entry_inning >= 7) & (a.entry_lead.abs() <= 2)
    return a.drop(columns=['inning', 'outs_when_up', 'on_1b', 'on_2b', 'on_3b']).sort_values('game_date')


# ---- OU-1 / GS-1 --------------------------------------------------------------
OUTS_ON_EVENT = {
    'field_out': 1, 'strikeout': 1, 'force_out': 1, 'sac_fly': 1, 'sac_bunt': 1, 'fielders_choice_out': 1,
    'grounded_into_double_play': 2, 'double_play': 2, 'strikeout_double_play': 2, 'sac_fly_double_play': 2,
    'sac_bunt_double_play': 2, 'triple_play': 3, 'caught_stealing_2b': 1, 'caught_stealing_3b': 1,
    'caught_stealing_home': 1, 'pickoff_1b': 1, 'pickoff_2b': 1, 'pickoff_3b': 1,
    'pickoff_caught_stealing_2b': 1, 'pickoff_caught_stealing_3b': 1, 'pickoff_caught_stealing_home': 1,
    'other_out': 1}


def outs_recorded(df: pd.DataFrame) -> pd.Series:
    """OU-1: outs credited on each pitch row from `events` (0 when no event). Log-derived; an out made
    on a play with no event row (rare: a runner thrown out on a non-PA-ending pitch without an event) is missed."""
    return df.events.map(OUTS_ON_EVENT).fillna(0).astype(int)


def game_score(df: pd.DataFrame) -> pd.DataFrame:
    """GS-1: one row per game. Tango's Game Score v2 form: 40 + 2*outs + K - 2*BB - 2*H - 3*R - 6*HR.
    outs = OU-1; R = runs_created (house 'runs on watch': runs scored during the PAs he threw — includes
    unearned runs, excludes inherited runners he did not put on); BB = events == 'walk' (house nresults)."""
    d = df.copy()
    d['_outs'] = outs_recorded(d)
    g = d.groupby('game_pk', as_index=False).agg(
        game_date=('game_date', 'first'), game_year=('game_year', 'first'), game_type=('game_type', 'first'),
        home_team=('home_team', 'first'), away_team=('away_team', 'first'), pitches=('pitch_type', 'size'),
        outs=('_outs', 'sum'), inn_first=('inning', 'min'), inn_last=('inning', 'max'),
        k=('events', lambda s: s.isin(['strikeout', 'strikeout_double_play']).sum()),
        bb=('events', lambda s: (s == 'walk').sum()),
        h=('events', lambda s: s.isin(['single', 'double', 'triple', 'home_run']).sum()),
        hr=('events', lambda s: (s == 'home_run').sum()),
        whiffs=('description', lambda s: s.isin(WHIFFS).sum()),
        pa=('events', lambda s: (~s.replace(np.nan, 'NA').isin(['NA', 'pickoff_1b'])).sum()))
    g = g.merge(runs_by_game(d).rename(columns={'runs_created': 'r'}), on='game_pk', how='left')
    g['started'] = g.inn_first == 1
    g['ip_display'] = (g.outs // 3).astype(str) + '.' + (g.outs % 3).astype(str)
    g['game_score'] = 40 + 2 * g.outs + g.k - 2 * g.bb - 2 * g.h - 3 * g.r - 6 * g.hr
    return g.sort_values('game_date').reset_index(drop=True)


# ---- CX-1 context frame ----------------------------------------------------------
def context_frame(ph: pd.DataFrame, key=('pitcher', 'game_year', 'p_throws'),
                  min_pitches: int = CONTEXT_MIN_PITCHES) -> pd.DataFrame:
    """CX-1: the client's "Phillies pitcher-seasons, min 150 pitches" population, governed:
    keyed by MLBAM id (not name), regular season only, in_zone_rate over TRACKED pitches (zone not null).
    Rates carry their denominators."""
    key = list(key)
    d = ph.copy()
    d['_sw'] = d.description.isin(SWINGS); d['_wh'] = d.description.isin(WHIFFS)
    d['_tr'] = d.zone.notna(); d['_iz'] = d.zone.between(1, 9); d['_ooz'] = d.zone > 9
    d['_ch'] = d._ooz & d._sw
    g = d.groupby(key, as_index=False).agg(pitches=('pitch_type', 'size'), swings=('_sw', 'sum'),
                                           whiffs=('_wh', 'sum'), tracked=('_tr', 'sum'), in_zone=('_iz', 'sum'),
                                           ooz=('_ooz', 'sum'), chases=('_ch', 'sum'),
                                           name=('player_name', lambda s: s.mode().iat[0]))
    r = nresults(key, d)[key + ['plate_apps', 'walks', 'strikeouts', 'woba']]
    g = g.merge(r, on=key, how='left')
    g['whiff_rate'] = g.whiffs / g.swings
    g['chase_rate'] = g.chases / g.ooz
    g['in_zone_rate'] = g.in_zone / g.tracked
    g['bbrate'] = g.walks / g.plate_apps
    g['krate'] = g.strikeouts / g.plate_apps
    return g[g.pitches >= min_pitches].reset_index(drop=True)


# ---- VB-1 first-N velocity ---------------------------------------------------------
def first_n_velo(df: pd.DataFrame, n: int = 15, pitch_type: str = 'FF') -> pd.DataFrame:
    """VB-1: mean `pitch_type` velocity among the first `n` pitches of each outing (all types count toward n).
    Arm-state read that is comparable between a start and a relief outing."""
    d = df.sort_values(['game_pk', 'at_bat_number', 'pitch_number']).copy()
    d['pitch_of_outing'] = d.groupby('game_pk').cumcount() + 1
    d = d[(d.pitch_of_outing <= n) & (d.pitch_type == pitch_type)]
    return d.groupby('game_pk', as_index=False).agg(game_date=('game_date', 'first'),
                                                    first_n_ff=('release_speed', 'size'),
                                                    first_n_ff_velo=('release_speed', 'mean'))


# ---- BN-1 batter names by des-parse ----------------------------------------------------
_VERB = re.compile(r"^(.+?) (strikes out|grounds|flies|lines|pops|walks|singles|doubles|triples|homers|"
                   r"hits|reaches|called out|out on|is hit|hit by|intentionally|bunts|fouls|sacrifice|"
                   r"grounded|lined|flied|popped|chopped|out)")


def batter_names(df: pd.DataFrame) -> pd.Series:
    """BN-1: modal parsed name per batter id from PA-ending `des` (house rule: never hand-key ids)."""
    d = df[df.events.notna() & df.des.notna()][['batter', 'des']].copy()
    d['nm'] = d.des.str.extract(_VERB)[0].str.strip()
    return d.dropna(subset=['nm']).groupby('batter').nm.agg(lambda s: s.mode().iat[0])


# ---- OC-1 October card --------------------------------------------------------------------
def outing_signatures(df: pd.DataFrame) -> pd.DataFrame:
    """Per-outing process signatures used by OC-1 (same definitions for a start or a relief outing)."""
    d = df.copy()
    d['_sw'] = d.description.isin(SWINGS); d['_wh'] = d.description.isin(WHIFFS)
    d['_ooz'] = d.zone > 9; d['_ch'] = d._ooz & d._sw
    g = d.groupby('game_pk', as_index=False).agg(game_date=('game_date', 'first'), pitches=('pitch_type', 'size'),
                                                 whiffs=('_wh', 'sum'), ooz=('_ooz', 'sum'), chases=('_ch', 'sum'),
                                                 bb=('events', lambda s: (s == 'walk').sum()),
                                                 pa=('events', lambda s: (~s.replace(np.nan, 'NA').isin(['NA', 'pickoff_1b'])).sum()))
    g['whiff_per_100'] = 100 * g.whiffs / g.pitches
    g['chase_rate'] = g.chases / g.ooz
    g['bb_rate'] = g.bb / g.pa
    v = first_n_velo(d)
    return g.merge(v[['game_pk', 'first_n_ff', 'first_n_ff_velo']], on='game_pk', how='left')


OC_SIGNATURES = [
    # id, column, direction (+1 = higher is the good side), threshold quantile of 2026 regular-season outings
    ('OC-A', 'first_n_ff_velo', +1, 0.25, "Arm: four-seam velocity over the first 15 pitches"),
    ('OC-B', 'chase_rate', +1, 0.25, "The chase: share of out-of-zone pitches swung at"),
    ('OC-C', 'whiff_per_100', +1, 0.25, "Swing-and-miss: whiffs per 100 pitches"),
    ('OC-D', 'bb_rate', -1, 0.75, "Control: walks per plate appearance"),
]


def october_card(season_outings: pd.DataFrame) -> pd.DataFrame:
    """OC-1: pre-registered thresholds. For each signature the bar is his OWN 2026 regular-season outing
    distribution at the stated quantile (the edge of his normal range). A postseason outing HOLDS a signature
    when it is on the good side of the bar; the outing is ON-SCRIPT when it holds >= 3 of 4."""
    rows = []
    for sid, col, direction, q, label in OC_SIGNATURES:
        s = season_outings[col].dropna()
        rows.append(dict(signature=sid, label=label, column=col, direction=('higher' if direction > 0 else 'lower'),
                         quantile=q, bar=float(s.quantile(q)), season_median=float(s.median()),
                         season_min=float(s.min()), season_max=float(s.max()), outings=int(len(s))))
    return pd.DataFrame(rows)


def grade_outing(row: pd.Series, card: pd.DataFrame) -> dict:
    out, holds = {}, 0
    for _, c in card.iterrows():
        v = row.get(c.column)
        if v is None or pd.isna(v):
            out[c.signature] = 'NO DATA'; continue
        ok = v >= c.bar if c.direction == 'higher' else v <= c.bar
        out[c.signature] = 'HOLD' if ok else 'SLIP'
        holds += int(ok)
    graded = sum(1 for k in out.values() if k != 'NO DATA')
    out['verdict'] = 'ON-SCRIPT' if graded == 4 and holds >= 3 else ('OFF-SCRIPT' if graded == 4 else 'INCOMPLETE')
    return out
