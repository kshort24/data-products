"""
dp_uc51_kernel.py — governed kernel for UC #51 / uc-pps-035
"Still Zack Wheeler — the 2026 Recap"

INHERITANCE POLICY (control-plane 03_governance.md §0, Rule-1):
  * Section A  — INHERITED BY IMPORT, sha256-pinned, never copied:
      dp_uc49_kernel (uc-pps-034): CF-2 career_frame, opponent_id_scan, load_phils_cols (LP-1),
        appearance_log (US-1b), game_score (GS-1), outs_recorded (OU-1), first_n_velo (VB-1),
        outing_signatures + october_card + grade_outing (OC-1, SECOND USE → ratification),
        context_frame (CX-1), house_pitcher_seasons_from (KP-1b), batter_names (BN-1)
        → dp_uc48_kernel: season_recap (SR-1), runs_created, xwobacon, arsenal_table (AR-2),
          house_percentile (KP-1)
        → dp_uc44_kernel: nresults, whiff_rate, chase_rate, fpsr, hard_hit_rate, bb_type_by_level,
          two_prop_z, pitch_map_centroid (PM-1), SWINGS, WHIFFS
      dp_uc50_kernel (uc-pos-018): xwoba_pa (XW-1, PA-denominated expected wOBA)
      barrel_rate.py (house module, via dp_uc50_kernel): barrel_rate (BR-1)
  * Section A2 — INHERITED BY SOURCE-PINNED EXTRACTION (IX-1, new mechanism, provisional):
      the function's source text is parsed out of its home file, its sha256 is asserted, and only
      then is it executed. Used where the home is a build script (runs on import) or a notebook.
        ER-1 edge_rate            ← dp_uc8_nola_vs_nationals.py  (uc-pps-008, UC8)
        JR-1 jam_rate             ← Baseball Functions.ipynb      (house library, 2026-10-09)
        RCI  release_consistency  ← dp_uc28_painter_vs_orioles.py (uc-pps-023)
  * Section B  — NON-BREAKING GENERALIZATION of a provisional UC49 object:
      CF-2b career_frame_mlb — CF-2 plus (a) MLB games only: CF-2 admits every opponent file by id, and
           lhvp26.parquet (Lehigh Valley, pitcher-keyed) carries 148 Wheeler rehab pitches tagged
           game_type 'R' (defect MI-1); (b) the subject's own name on `player_name` (CF-2 stamps UC49's
           SUBJECT_NAME on every frame it builds — defect NM-1); (c) enrichment columns joined by pitch
           key from the house log (EN-1) for the fields CF-2's projection does not carry.
  * Section C  — NEW to this UC, PROVISIONAL and unratified:
      ST-1 swing_timing (tied-up / centered / flail buckets; tied-up boundary is JR-1's constant)
      NC-1 clear_miss (pitch centre more than two baseballs outside the rulebook zone) + miss side
      MX-1 mechanics_by_start (four-seam release point, arm angle, extension per start; RCI attached)
      SR-2 stretch_label (first N starts after the All-Star break, N from reporting, carry-in)
      OU-2 outs_by_pa (outs from the outs_when_up sequence of the full defensive log) and GS-1b game_score_b
           (GS-1 on OU-2 outs). Built because DQ-18 failed on the first run: OU-1 gave 480 outs against the
           published 162.0 IP (486); OU-2 gives 486. OU-1's documented edge case (outs with no out-event) is
           six outs in one season for this pitcher (defect OU1-1, back-check of uc-pps-034 in 05).

Data plane    : C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB
Control plane : C:\\Users\\Kellen\\OneDrive\\Documents\\Agents for Data Products
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

__version__ = "1.0.0"
_HERE = Path(__file__).resolve().parent
for _p in [os.environ.get("MLB_DATA_ROOT"), str(_HERE), "/mnt/user-data/uploads/MLB",
           r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]:
    if _p and (Path(_p) / "dp_uc49_kernel.py").exists() and _p not in sys.path:
        sys.path.insert(0, _p)
import dp_uc49_kernel as K49  # noqa: E402
import dp_uc50_kernel as K50  # noqa: E402

K48, K44 = K49.K48, K49.K44
ROOT = K44.ROOT
PIN = {
    "dp_uc49_kernel.py": "a4ad5191a6537f3a64de8cd1e9adb4b794d24fcb3e606bc8319a08e08e795f60",
    "dp_uc50_kernel.py": "8084cb172d0cf56089ebcdbe3e7d01aa2dfdcd60db3d65e737d0cfb4a7499463",
    "dp_uc48_kernel.py": "0f63857a103253ef2675190b383e064237a5e3d3c84be9fafdd67d55ecb21d32",
    "dp_uc44_kernel.py": "a2c119096db24fdbfca4ca7f79b9dcb32c379d6f1ec9566aa7376837711582e3",
    "barrel_rate.py":    "6282f090394aaef89101085ede5fae4b77c4663da95ed4274fadbc0e455a185c",
}
# IX-1 pins: sha256 of the extracted SOURCE SEGMENT (not the host file, which changes for other reasons)
IX_PIN = {}   # filled at first extraction and asserted against IX_PIN_EXPECTED
IX_PIN_EXPECTED = {
    ("dp_uc8_nola_vs_nationals.py", "PLATE_HALF"): "8ed1a2a2c85cd03cbe76fc42d2b6847f8ee225697cb611a721d392786b5b70a4",
    ("dp_uc8_nola_vs_nationals.py", "BALL_FT"): "f14f22431b7f18c92a1bfe405a1e80ea38c0484e370cb449b65b6263a50937ec",
    ("dp_uc8_nola_vs_nationals.py", "_dist_to_zone_edge"): "0564cc8e76ee5390964079c811f3f50d7b54d9b29c54b4087f612aadb12f13ed",
    ("dp_uc8_nola_vs_nationals.py", "edge_rate"): "c8da8544f6fcc626f5c9928dc114e0b3060733311a89764e4d44c4e28e1f4c9a",
    ("Baseball Functions.ipynb", "jam_rate"): "fe08ed2608d2c09c7aacdc13fb109198a24f9cacca3f0b1997a75ea98a5f3a77",
    ("dp_uc28_painter_vs_orioles.py", "release_consistency"): "e7d58d42b85ac9c19284308e3b05bc79ac02060b71b058473939fd0ed2060022",
}


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def assert_lineage() -> dict:
    out = {}
    for f, h in PIN.items():
        got = sha(ROOT / f)
        assert got == h, f"{f} drifted ({got[:12]} != {h[:12]})"
        out[f] = got
    K49.assert_lineage()
    return out


PITCH_KEY = K48.PITCH_KEY
SWINGS, WHIFFS = K44.SWINGS, K44.WHIFFS
nresults, whiff_rate, chase_rate, fpsr = K44.nresults, K44.whiff_rate, K44.chase_rate, K44.fpsr
hard_hit_rate, bb_type_by_level, two_prop_z = K44.hard_hit_rate, K44.bb_type_by_level, K44.two_prop_z
pitch_map_centroid, apply_woba_weights = K44.pitch_map_centroid, K44.apply_woba_weights
season_recap, runs_created, xwobacon = K48.season_recap, K48.runs_created, K48.xwobacon
arsenal_table, house_percentile = K48.arsenal_table, K48.house_percentile
opponent_id_scan, load_phils_cols, appearance_log = K49.opponent_id_scan, K49.load_phils_cols, K49.appearance_log
game_score, outs_recorded, first_n_velo = K49.game_score, K49.outs_recorded, K49.first_n_velo
outing_signatures, october_card, grade_outing = K49.outing_signatures, K49.october_card, K49.grade_outing
context_frame, house_pitcher_seasons_from, runs_by_game = K49.context_frame, K49.house_pitcher_seasons_from, K49.runs_by_game
xwoba_pa = K50.xwoba_pa
barrel_rate = K50.BR.barrel_rate

# ---------------------------------------------------------------------------
# House constants
# ---------------------------------------------------------------------------
PHILLIES_RED, PHILLIES_NAVY, PHILLIES_BLUE, PHILLIES_CREAM = K49.PHILLIES_RED, K49.PHILLIES_NAVY, K49.PHILLIES_BLUE, K49.PHILLIES_CREAM
NEUTRAL_GRAY, LIGHT_GRAY = K49.NEUTRAL_GRAY, K49.LIGHT_GRAY

SUBJECT_ID = 554430                      # Zack Wheeler, RHP (resolved from data in uc-pps-020, not hand-keyed)
SUBJECT_NAME = "Wheeler, Zack"           # used ONLY to reproduce the client's own frames (HP family)
SUBJECT_DISPLAY = "Zack Wheeler"
SUBJECT_FILE = "wheeler.parquet"         # pitcher-keyed pull: Mets 2017-2019
RECAP_SEASON, PRIOR_SEASON = 2026, 2025
PHILLIES_ERA = tuple(range(2020, 2027))  # his Phillies tenure (the client's "time with the Phillies")
ANCHOR_GAME_DATE = "2026-09-27"          # Game 162 — last regular-season game in phils_2026.parquet
FIRST_APPEARANCE = "2026-04-25"
LAST_REGULAR_APPEARANCE = "2026-09-27"
WC_GAME_PK = 849844                      # NL Wild Card Game 3, 2026-10-01 at ATL (relief, innings 3-6)
GAME_162_PK = None                       # resolved from the log at build time (the 9/27 start)
ALL_STAR_BREAK = K49.ALL_STAR_BREAK      # "2026-07-13": first half = game_date < this (uc-pps-020's cut 7/12)
STRETCH_N = 6                            # carry-in (Inquirer 2026-09-19): "8.51 ERA over six starts" after the break
STRETCH_FIRST, STRETCH_LAST = "2026-07-27", "2026-08-24"   # SR-2: the ONLY six-start post-break window whose runs on
STRETCH_CARRY_IN_RA = 8.51                                   # watch per 27 outs reconcile to the reported 8.51 (build asserts)
POSTSEASON_TYPES = K49.POSTSEASON_TYPES
CONTEXT_MIN_PITCHES = K49.CONTEXT_MIN_PITCHES
KP_MIN_PA = K49.KP_MIN_PA
STARTER_WORKLOAD = 2000                  # CX-1b cut (uc-pps-034)

ENRICH_COLS = ['woba_value', 'woba_denom', 'launch_speed_angle', 'bat_speed', 'swing_length',
               'intercept_ball_minus_batter_pos_x_inches', 'intercept_ball_minus_batter_pos_y_inches',
               'release_pos_x', 'release_pos_z', 'arm_angle', 'hit_location', 'hc_x', 'hc_y',
               'api_break_x_arm', 'api_break_z_with_gravity']


# ============================================================================
# SECTION A2 — IX-1 source-pinned extraction
# ============================================================================
def _source_of(path: Path) -> str:
    if path.suffix == ".ipynb":
        nb = json.loads(path.read_text(encoding="utf-8"))
        return "\n\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    return path.read_text(encoding="utf-8")


def extract(file: str, functions: list, constants: list = ()) -> dict:
    """IX-1. Parse `file`, pull the named top-level functions and constant assignments, pin and exec them.
    The host file is never imported or run. Returns the namespace; IX_PIN records each segment's sha256."""
    path = ROOT / file
    src = _source_of(path)
    segs = {}
    # notebooks hold many cells; parse cell by cell so one bad cell cannot block extraction
    trees = []
    if path.suffix == ".ipynb":
        nb = json.loads(path.read_text(encoding="utf-8"))
        for c in nb["cells"]:
            if c["cell_type"] != "code":
                continue
            s = "".join(c["source"])
            try:
                trees.append((s, ast.parse(s)))
            except SyntaxError:
                continue          # IPython magics (%run) make some cells unparseable; they hold no target
    else:
        trees.append((src, ast.parse(src)))
    for s, tree in trees:
        for n in tree.body:
            if isinstance(n, ast.FunctionDef) and n.name in functions and n.name not in segs:
                segs[n.name] = ast.get_source_segment(s, n)
            elif isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) \
                    and n.targets[0].id in constants and n.targets[0].id not in segs:
                segs[n.targets[0].id] = ast.get_source_segment(s, n)
    missing = [x for x in list(functions) + list(constants) if x not in segs]
    assert not missing, f"IX-1: {missing} not found in {file}"
    ns = {"np": np, "pd": pd}
    for name in list(constants) + list(functions):
        h = hashlib.sha256(segs[name].encode()).hexdigest()
        IX_PIN[(file, name)] = h
        exp = IX_PIN_EXPECTED.get((file, name))
        assert exp is None or exp == h, f"IX-1: {file}:{name} drifted ({h[:12]} != {exp[:12]})"
        exec(compile(segs[name], f"{file}:{name}", "exec"), ns)
    ns["__file_sha256__"] = sha(path)
    return ns


_ER = extract("dp_uc8_nola_vs_nationals.py", ["_dist_to_zone_edge", "edge_rate"], ["PLATE_HALF", "BALL_FT"])
_JR = extract("Baseball Functions.ipynb", ["jam_rate"])
_RC = extract("dp_uc28_painter_vs_orioles.py", ["release_consistency"])
edge_rate, dist_to_zone_edge = _ER["edge_rate"], _ER["_dist_to_zone_edge"]
PLATE_HALF, BALL_FT = _ER["PLATE_HALF"], _ER["BALL_FT"]
jam_rate = _JR["jam_rate"]
release_consistency = _RC["release_consistency"]
# JR-1's tied-up boundary lives inside the function body; read it from the compiled function, never retype it
JAM_MAX_IN = float(jam_rate.__code__.co_consts[[i for i, c in enumerate(jam_rate.__code__.co_consts)
                                                 if isinstance(c, float)][0]])   # 32.5, asserted below
assert JAM_MAX_IN == 32.5, JAM_MAX_IN
JAM_SWING_FLOOR = 50                     # JR-1's published-cell floor (stated in its source; asserted in DQ)


def ix_receipt() -> pd.DataFrame:
    rows = [dict(file=f, object=n, segment_sha256=h, expected=IX_PIN_EXPECTED.get((f, n), "recorded-at-first-use"))
            for (f, n), h in IX_PIN.items()]
    return pd.DataFrame(rows)


# ============================================================================
# SECTION B — CF-2b
# ============================================================================
def mlb_teams(ph: pd.DataFrame) -> set:
    """Every club that appears in a Phillies regular-season game 2015-2026 (data-derived, not hand-keyed)."""
    r = ph[ph.game_type == 'R']
    return set(r.home_team.unique()) | set(r.away_team.unique())


def career_frame_mlb(pitcher_id: int = SUBJECT_ID, subject_file: str = SUBJECT_FILE, name: str = SUBJECT_NAME,
                     display: str = SUBJECT_DISPLAY, game_types=("R",), scan: pd.DataFrame | None = None,
                     ph: pd.DataFrame | None = None, ph_enrich: pd.DataFrame | None = None):
    """CF-2b. K49.career_frame, then (a) drop rows from non-MLB games (MI-1), (b) stamp the subject's own
    name (NM-1), (c) left-join ENRICH_COLS from the house log on (pitcher, PITCH_KEY) (EN-1).
    Returns (frame, receipt, milb_rows_dropped)."""
    df, receipt = K49.career_frame(pitcher_id, subject_file, display, game_types=game_types, scan=scan, ph=ph)
    teams = mlb_teams(ph if ph is not None else load_phils_cols(regular_only=False))
    is_mlb = df.home_team.isin(teams) & df.away_team.isin(teams)
    milb = df[~is_mlb]
    milb_receipt = milb.groupby(['game_year', 'src', 'src_file', 'game_date', 'home_team', 'away_team'],
                                as_index=False).agg(rows=('pitch_type', 'size'))
    df = df[is_mlb].copy()
    df['player_name'] = name
    if ph_enrich is not None:
        e = ph_enrich[ph_enrich.pitcher == pitcher_id][['pitcher'] + PITCH_KEY + [c for c in ENRICH_COLS if c in ph_enrich]]
        e = e.drop_duplicates(subset=['pitcher'] + PITCH_KEY)
        df = df.drop(columns=[c for c in ENRICH_COLS if c in df.columns]).merge(e, on=['pitcher'] + PITCH_KEY, how='left')
    return df.reset_index(drop=True), receipt, milb_receipt


# ============================================================================
# SECTION C — NEW (provisional)
# ============================================================================
FLAIL_MIN_IN = 41.0      # the client's second histogram line (October 2026 cell 23: add_vline(x=41))


def swing_timing(level, df: pd.DataFrame) -> pd.DataFrame:
    """ST-1. Tied-up / centered / flail shares of TRACKED swings (JR-1's swing list and denominator).
    tied-up: intercept < JAM_MAX_IN (JR-1, inherited) · flail: intercept > FLAIL_MIN_IN (provisional) ·
    centered: between. Savant's own buckets use the barrel's sweet spot; this is the public-data proxy."""
    if isinstance(level, str):
        level = [level]
    col = 'intercept_ball_minus_batter_pos_x_inches'
    sw_desc = ['foul', 'foul_tip', 'hit_into_play', 'swinging_pitchout', 'swinging_strike', 'swinging_strike_blocked']
    sw = df[df.description.isin(sw_desc) & df[col].notna()].copy()
    sw['bucket'] = np.select([sw[col] < JAM_MAX_IN, sw[col] > FLAIL_MIN_IN], ['tied_up', 'flail'], 'centered')
    g = sw.groupby(level + ['bucket'], as_index=False).agg(n=('description', 'size'))
    w = g.pivot_table(index=level, columns='bucket', values='n', fill_value=0).reset_index()
    for b in ('tied_up', 'centered', 'flail'):
        if b not in w:
            w[b] = 0
    w['tracked_swings'] = w.tied_up + w.centered + w.flail
    for b in ('tied_up', 'centered', 'flail'):
        w[f'{b}_rate'] = w[b] / w.tracked_swings
    w.columns.name = None
    return w


def clear_miss(df: pd.DataFrame, throws: str = 'R', balls: float = 2.0) -> pd.DataFrame:
    """NC-1. Flags each tracked pitch whose centre is more than `balls` baseball widths outside the rulebook
    zone (ER-1 geometry), and names the side of the miss: arm / glove (catcher view, + plate_x = first-base
    side, so a RHP's arm side is plate_x < 0), high / low. Corner misses take the axis of larger exceedance."""
    d = df.dropna(subset=['plate_x', 'plate_z', 'sz_top', 'sz_bot']).copy()
    hw = PLATE_HALF
    dx = np.maximum(np.abs(d.plate_x) - hw, 0)
    dz = np.maximum.reduce([d.sz_bot - d.plate_z, d.plate_z - d.sz_top, np.zeros(len(d))])
    dist = np.sqrt(dx ** 2 + dz ** 2)
    d['clear_miss'] = dist > balls * BALL_FT
    arm_neg = (throws == 'R')
    horiz = np.where((d.plate_x < 0) == arm_neg, 'arm', 'glove')
    vert = np.where(d.plate_z > d.sz_top, 'high', 'low')
    d['miss_side'] = np.where(~d.clear_miss, None, np.where(dx >= dz, horiz, vert))
    return d


def mechanics_by_start(df: pd.DataFrame, pitch_type: str = 'FF') -> pd.DataFrame:
    """MX-1. One row per start: four-seam release point (ft, catcher view), arm angle, extension, plus RCI
    (uc-pps-023, inherited by IX-1). Descriptive only — the log shows where the ball left the hand, not why."""
    f = df[df.pitch_type == pitch_type]
    g = f.groupby(['game_pk', 'game_date'], as_index=False).agg(
        ff_n=('release_speed', 'size'), rel_x=('release_pos_x', 'mean'), rel_z=('release_pos_z', 'mean'),
        arm_angle=('arm_angle', 'mean'), arm_angle_n=('arm_angle', 'count'), ext=('release_extension', 'mean'),
        velo=('release_speed', 'mean'), hb_in=('pfx_x', lambda s: 12 * s.mean()), ivb_in=('pfx_z', lambda s: 12 * s.mean()))
    rci = release_consistency(df.assign(pitch_name=np.where(df.pitch_type == 'FF', '4-Seam Fastball', df.pitch_name)),
                              ['game_date'])[['game_date', 'rci_in']]
    return g.merge(rci, on='game_date', how='left')


def stretch_windows(starts: pd.DataFrame, break_date: str = ALL_STAR_BREAK, n: int = STRETCH_N) -> pd.DataFrame:
    """SR-2 receipt: every run of n consecutive post-break starts with its runs on watch per 27 outs (OU-2)."""
    p = starts[starts.game_date.astype(str) >= break_date].sort_values('game_date').reset_index(drop=True)
    rows = []
    for i in range(len(p) - n + 1):
        w = p.iloc[i:i + n]
        rows.append(dict(first=str(w.game_date.iat[0])[:10], last=str(w.game_date.iat[-1])[:10], r=int(w.r.sum()),
                         outs=int(w.outs.sum()), r27=27 * w.r.sum() / w.outs.sum()))
    out = pd.DataFrame(rows)
    out['reconciles_to_carry_in'] = (out.r27 - STRETCH_CARRY_IN_RA).abs() < 0.005
    return out


def stretch_label(starts: pd.DataFrame, break_date: str = ALL_STAR_BREAK, first: str = STRETCH_FIRST,
                  last: str = STRETCH_LAST) -> pd.Series:
    """SR-2. 'first_half' before the break · 'opener' post-break starts before the stretch · 'stretch' the reported
    six-start slide (identified by reconciliation, see stretch_windows) · 'finish' everything after it."""
    d = starts.game_date.astype(str).str[:10]
    return pd.Series(np.select([d < break_date, d < first, d <= last], ['first_half', 'opener', 'stretch'], 'finish'),
                     index=starts.index)


# ---- OU-2 / GS-1b -------------------------------------------------------------------
def outs_by_pa(def_log: pd.DataFrame) -> pd.DataFrame:
    """OU-2. Outs made during each plate appearance, read from the change in `outs_when_up` to the next PA of
    the same half-inning in the FULL defensive log (every pitcher the club used), 3 at an inning's end.
    Catches what OU-1's event map cannot see: a batter thrown out stretching a single, a runner caught stealing
    during a walk, the extra out on a force play. The last PA of a game uses min(3 - outs_when_up, OU-1) so a
    walk-off or a called game is not credited a phantom third out. Grain: (game_pk, at_bat_number)."""
    d = def_log.sort_values(['game_pk', 'at_bat_number', 'pitch_number'])
    pa = d.groupby(['game_pk', 'at_bat_number'], as_index=False).head(1)[
        ['game_pk', 'game_date', 'inning', 'at_bat_number', 'outs_when_up', 'pitcher']].copy()
    ev = d[d.events.notna()].groupby(['game_pk', 'at_bat_number']).events.last().rename('pa_event').reset_index()
    pa = pa.merge(ev, on=['game_pk', 'at_bat_number'], how='left')
    pa['ou1'] = pa.pa_event.map(K49.OUTS_ON_EVENT).fillna(0).astype(int)
    pa['next_outs'] = pa.groupby(['game_pk', 'inning']).outs_when_up.shift(-1)
    pa['outs_on_pa'] = (pa.next_outs.fillna(3) - pa.outs_when_up).astype(int)
    last = pa.groupby('game_pk').at_bat_number.transform('max') == pa.at_bat_number
    pa.loc[last, 'outs_on_pa'] = np.minimum(3 - pa.loc[last, 'outs_when_up'], pa.loc[last, 'ou1']).astype(int)
    return pa


def game_score_b(df: pd.DataFrame, pa_outs: pd.DataFrame, pitcher_id: int = SUBJECT_ID) -> pd.DataFrame:
    """GS-1b. GS-1 (Tango v2 form) with outs from OU-2 instead of OU-1. GS-1's other terms are unchanged;
    the score moves by 2 points per out OU-1 missed. `outs_ou1` is kept beside `outs` for the receipt."""
    g = game_score(df)
    o2 = pa_outs[pa_outs.pitcher == pitcher_id].groupby('game_pk', as_index=False).agg(outs_ou2=('outs_on_pa', 'sum'))
    g = g.merge(o2, on='game_pk', how='left')
    g['outs_ou1'] = g.outs
    g['outs'] = g.outs_ou2.fillna(g.outs_ou1).astype(int)
    g['game_score'] = g.game_score + 2 * (g.outs - g.outs_ou1)
    g['ip_display'] = (g.outs // 3).astype(str) + '.' + (g.outs % 3).astype(str)
    return g.drop(columns='outs_ou2')
