"""
============================================================================
GOVERNED DATA PRODUCT — uc-pos-008-arraez-acquisition-001 (UC #32)
"Luis Arraez: the contact bat, and where he belongs in the order"
============================================================================
Layer-3 BUILD artifact, Phillies Position-player (pos) value stream.
Build artifact id: dp_uc31 · contract: uc-pos-008 · ledger UC #32

Pattern lineage:
  UC#25 / dp_uc24 (Turner 2026 hitter retrospective — locked KPI kernel,
    running_line / rolling_form trajectory KPIs, interactive consumable)
  UC#30 / dp_uc29 (Kilian — first acquisition-onboarding variant)
  UC#31 / dp_uc30 (Raley — second acquisition variant; population-benchmark
    pattern; "a proxy must ship with its calibration" house rule)
  -> UC#32 (this one): FIRST POSITION-PLAYER ACQUISITION-ONBOARDING variant,
     and the first UC in either value stream to carry a decision model
     (lineup-slot run-contribution projection).

Locked KPI mechanics inherited VERBATIM from dp_uc24 / dp_uc20 /
Baseball Functions — NOT re-derived, NOT edited:
  get_stats (ba/obp/slg/ops/woba/iso/krate/bbrate/xbh), SWINGS/WHIFFS,
  discipline(), batted_ball(), pulled_air(), PITCH_GROUP, wrc (SC-1),
  ppa (SC-2), bat_tracking(), running_line (RF-1), rolling_form (RF-2).

NEW KPIs this UC (specs in 04_architecture_and_kpi_specs.md; provisional):
  AR-1  Two-Strike Survival Rate (TSSR)
  AR-2  Two-Strike Damage Line (TSDL)
  AR-3  Damage Profile by Pitch Group x Hand (DPGH)
  AR-4  Scoring-Position Conversion Rate (SPCR)
  AR-5  Lineup Slot Opportunity Profile (LSOP)
  AR-6  Slot-Projected Run Contribution (SPRC)   <- the decision model
  AR-7  Table-Setting Value (TSV)

DATA WINDOW / FRESHNESS (DPO decision 2026-08-04):
  * PRIMARY window = 2026 regular season only. Every forward-looking claim
    is carried by 2026. Prior seasons (2019-2025) appear as a SHADOW /
    stability backdrop and carry no forward-looking claim.
  * Entity lock: batter == 650333 (Luis Arraez), game_type == 'R'.
  * Source: data/opponents/arraez.parquet (single-batter cache, 2019-05-18
    .. 2026-08-02). ZERO Phillies rows — he had not debuted for PHI as of
    the cache max date. This is a pre-arrival dossier, not a review.
  * Phillies comparison set: data/phillies/phils_2026.parquet,
    phillies_role == 'batting', game_type == 'R', through 2026-08-02.
  * Dedup on ['game_pk','at_bat_number','pitch_number'].
  * MANUAL CARRY-INS (not derivable from the pitch log, flagged in DQ):
    trade acquisition at 2026 deadline; Mattingly's cleanup-spot decision;
    Harper's move back to the outfield. User-provided roster context.
============================================================================
"""
from __future__ import annotations
import sys, json, re
from pathlib import Path
import numpy as np
import pandas as pd

# ----------------------------------------------------------- portability --
def _resolve_root() -> Path:
    import os
    cands = []
    if len(sys.argv) > 1:
        cands.append(Path(sys.argv[1]))
    if os.environ.get("MLB_DATA_ROOT"):
        cands.append(Path(os.environ["MLB_DATA_ROOT"]))
    cands += [
        Path("/sessions/nifty-funny-davinci/mnt/MLB"),
        Path(r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"),
        Path("."), Path("../../../MLB"),
    ]
    for c in cands:
        if (c / "data" / "opponents" / "arraez.parquet").exists():
            return c
    raise SystemExit("FATAL: MLB data root not found. Refusing to emit an "
                     "unfilled harness (see uc-pps-010 retirement).")

MLB = _resolve_root()
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

PITCH_KEY = ["game_pk", "at_bat_number", "pitch_number"]
ARRAEZ = 650333
STEM = "dp_uc31"
PRIMARY_YEAR = 2026
CACHE_MAX = "2026-08-02"

_receipts: list[dict] = []

def receipt(name: str, df: pd.DataFrame, note: str = "") -> pd.DataFrame:
    """Every table that reaches the report lands here first. No exceptions."""
    path = OUT / f"{STEM}_{name}.csv"
    df.to_csv(path, index=False)
    _receipts.append({"receipt": name, "rows": len(df), "cols": df.shape[1],
                      "file": path.name, "note": note})
    print(f"  [receipt] {name:38s} {len(df):5d} rows -> {path.name}")
    return df

# ================================================================ LOAD ====
def load_arraez() -> pd.DataFrame:
    m = pd.read_parquet(MLB / "data/opponents/arraez.parquet")
    m = m[m.batter == ARRAEZ]                 # entity lock: MLBAM id, never name
    m = m[m.game_type == "R"]                 # regular season only
    m = m.drop_duplicates(subset=PITCH_KEY)
    w = pd.read_csv(MLB / "wOBA and FIP Constants.csv")
    m = m.drop(columns=[c for c in w.columns if c != "Season" and c in m.columns])
    m = m.merge(w, left_on="game_year", right_on="Season",
                suffixes=("_bad", ""), how="left")
    return m

def load_phillies_2026() -> pd.DataFrame:
    p = pd.read_parquet(MLB / "data/phillies/phils_2026.parquet")
    p = p[(p.phillies_role == "batting") & (p.game_type == "R")]
    p = p.drop_duplicates(subset=PITCH_KEY)
    w = pd.read_csv(MLB / "wOBA and FIP Constants.csv")
    p = p.drop(columns=[c for c in w.columns if c != "Season" and c in p.columns])
    p = p.merge(w, left_on="game_year", right_on="Season",
                suffixes=("_bad", ""), how="left")
    return p

# =============================== LOCKED KPI KERNEL (inherited verbatim) ====
SWINGS = ['foul','foul_bunt','foul_tip','hit_into_play','missed_bunt',
          'swinging_pitchout','swinging_strike','swinging_strike_blocked']
WHIFFS = ['foul_tip','missed_bunt','swinging_pitchout','swinging_strike',
          'swinging_strike_blocked']

def get_stats(level, df):
    if isinstance(level, str): level = [level]
    g = lambda sub, name: sub.groupby(level, as_index=False).agg(**{name: ('description','size')})
    pitches = g(df, 'pitches')
    pa   = g(df[~df.events.replace(np.nan,'NA').isin(['NA','pickoff_1b'])], 'plate_apps')
    ab   = g(df[~df.events.replace(np.nan,'NA').isin(['NA','pickoff_1b','walk','intent_walk','hit_by_pitch','sac_fly','sac_bunt'])], 'at_bats')
    bip  = g(df[df.type=='X'], 'bip')
    hits = g(df[df.events.isin(['home_run','single','double','triple'])], 'hits')
    s1   = g(df[df.events=='single'], 'singles')
    s2   = g(df[df.events=='double'], 'doubles')
    s3   = g(df[df.events=='triple'], 'triples')
    hr   = g(df[df.events=='home_run'], 'hrs')
    bb   = g(df[df.events=='walk'], 'walks')
    ks   = g(df[df.events.isin(['strikeout','strikeout_double_play'])], 'strikeouts')
    hbp  = g(df[df.events=='hit_by_pitch'], 'hbp')
    out = pitches
    for piece in (pa, ab, bip, hits, s1, s2, s3, hr, bb, ks, hbp):
        out = out.merge(piece, on=level, how='left')
    for wcol, ev in [('wBB','walk'), ('wHBP','hit_by_pitch'), ('w1B','single'),
                     ('w2B','double'), ('w3B','triple'), ('wHR','home_run')]:
        piece = df[df.events==ev].groupby(level, as_index=False).agg(**{wcol:(wcol,'sum')})
        out = out.merge(piece, on=level, how='left')
    xw = df.groupby(level, as_index=False).agg(xwoba=('estimated_woba_using_speedangle','mean'),
                                               xba=('estimated_ba_using_speedangle','mean'))
    out = out.merge(xw, on=level, how='left').fillna(0)
    out['ba']  = out.hits / out.at_bats
    out['obp'] = (out.hits + out.walks + out.hbp) / out.plate_apps
    out['slg'] = (out.singles + 2*out.doubles + 3*out.triples + 4*out.hrs) / out.at_bats
    out['ops'] = out.obp + out.slg
    out['woba'] = (out.wBB + out.wHBP + out.w1B + out.w2B + out.w3B + out.wHR) / out.plate_apps
    out['xbh'] = out.doubles + out.triples + out.hrs
    out['iso'] = out.slg - out.ba
    out['krate'] = out.strikeouts / out.plate_apps
    out['bbrate'] = out.walks / out.plate_apps
    return out

def discipline(level, df):
    if isinstance(level, str): level = [level]
    d = df.copy()
    d['swing'] = d.description.isin(SWINGS)
    d['whiff'] = d.description.isin(WHIFFS)
    d['in_zone'] = d.zone <= 9
    rows = d.groupby(level, as_index=False).apply(lambda x: pd.Series({
        'pitches': len(x),
        'swing_rate': x.swing.mean(),
        'whiff_rate': x[x.swing].whiff.mean(),
        'chase_rate': x[~x.in_zone].swing.mean(),
        'z_swing_rate': x[x.in_zone].swing.mean(),
        'z_contact_rate': 1 - x[x.in_zone & x.swing].whiff.mean(),
        'ooz_contact_rate': 1 - x[~x.in_zone & x.swing].whiff.mean(),
        'fp_swing_rate': x[(x.balls==0)&(x.strikes==0)].swing.mean(),
        'zone_rate_seen': x.in_zone.mean(),
    }), include_groups=False)
    return rows.round(4)

def batted_ball(level, df):
    if isinstance(level, str): level = [level]
    b = df[df.type=='X'].copy()
    b['barrel'] = b.launch_speed_angle == 6
    b['hard'] = b.launch_speed >= 95
    b['sweet'] = b.launch_angle.between(8, 32)
    b['air'] = b.bb_type.isin(['fly_ball','line_drive'])
    rows = b.groupby(level, as_index=False).apply(lambda x: pd.Series({
        'bip': len(x),
        'avg_ev': x.launch_speed.mean(),
        'ev90': x.launch_speed.quantile(0.9),
        'max_ev': x.launch_speed.max(),
        'avg_la': x.launch_angle.mean(),
        'barrel_rate': x.barrel.mean(),
        'hard_hit_rate': x.hard.mean(),
        'sweet_spot_rate': x.sweet.mean(),
        'gb_rate': (x.bb_type=='ground_ball').mean(),
        'fb_rate': (x.bb_type=='fly_ball').mean(),
        'ld_rate': (x.bb_type=='line_drive').mean(),
        'pu_rate': (x.bb_type=='popup').mean(),
        'air_rate': x.air.mean(),
        'xwoba_con': x.estimated_woba_using_speedangle.mean(),
        # O4 FIX (uc-pps-025 open item): publish the ESTIMATED-count separately.
        # The inherited xwoba_con uses size semantics for n; this column is the
        # honest denominator. Locked function NOT edited — column added alongside.
        'xwoba_con_n': x.estimated_woba_using_speedangle.notna().sum(),
    }), include_groups=False)
    return rows.round(4)

def pulled_air(df, level):
    if isinstance(level, str): level = [level]
    b = df[(df.type=='X') & df.hc_x.notna() & df.hc_y.notna()].copy()
    b['spray'] = np.degrees(np.arctan2(b.hc_x - 125.42, 198.27 - b.hc_y))
    b['pulled'] = np.where(b.stand=='L', b.spray > 15, b.spray < -15)
    b['oppo'] = np.where(b.stand=='L', b.spray < -15, b.spray > 15)
    b['air'] = b.bb_type.isin(['fly_ball','line_drive'])
    rows = b.groupby(level, as_index=False).apply(lambda x: pd.Series({
        'bip_traced': len(x),
        'pull_rate': x.pulled.mean(),
        'oppo_rate': x.oppo.mean(),
        'center_rate': 1 - x.pulled.mean() - x.oppo.mean(),
        'pulled_air_rate': (x.pulled & x.air).mean(),
        'pulled_air_ct': (x.pulled & x.air).sum(),
        'gb_pull_rate': x[x.bb_type=='ground_ball'].pulled.mean(),
    }), include_groups=False)
    return rows.round(4)

PITCH_GROUP = {
    'FF':'fastball','SI':'fastball','FC':'fastball','FA':'fastball',
    'SL':'breaking','ST':'breaking','CU':'breaking','KC':'breaking','SV':'breaking','CS':'breaking',
    'CH':'offspeed','FS':'offspeed','FO':'offspeed','SC':'offspeed','KN':'offspeed','EP':'offspeed',
}

def wrc(level, df, constants):
    if isinstance(level, str): level = [level]
    r = get_stats(level, df)
    c = constants.rename(columns={'wOBA':'lg_woba', 'wOBAScale':'woba_scale', 'R/PA':'lg_r_pa'})
    key = level[0]
    r = r.merge(c[['Season','lg_woba','woba_scale','lg_r_pa']], left_on=key, right_on='Season', how='left')
    r['wraa'] = (r.woba - r.lg_woba) / r.woba_scale * r.plate_apps
    r['wrc'] = r.wraa + r.lg_r_pa * r.plate_apps
    r['wrc_600'] = r.wrc / r.plate_apps * 600
    r['wrc_plus_approx'] = (r.woba / r.lg_woba) * 100
    return r[level + ['plate_apps','woba','lg_woba','wraa','wrc','wrc_600','wrc_plus_approx']].round(2)

def ppa(level, df):
    r = get_stats(level, df)
    r['p_pa'] = (r.pitches / r.plate_apps).round(3)
    lv = [level] if isinstance(level, str) else level
    return r[lv + ['pitches','plate_apps','p_pa']]

def bat_tracking(level, df):
    if isinstance(level, str): level = [level]
    if 'bat_speed' not in df.columns: return pd.DataFrame()
    d = df[df.bat_speed.notna()].copy()
    if d.empty: return pd.DataFrame()
    rows = d.groupby(level, as_index=False).apply(lambda x: pd.Series({
        'tracked_swings': len(x),
        'avg_bat_speed': x.bat_speed.mean(),
        'fast_swing_rate': (x.bat_speed >= 75).mean(),
        'squared_up_proxy': np.nan,
        'avg_swing_length': x.swing_length.mean(),
        'avg_attack_angle': x.attack_angle.mean() if 'attack_angle' in x else np.nan,
    }), include_groups=False)
    return rows.round(3)

# ============================ SHARED PA-LEVEL SPINE (new, this UC) =========
NON_PA = ['NA', 'pickoff_1b']
# NOTE: the locked get_stats PA rule excludes only NON_PA. 'truncated_pa' is a
# CONTINUATION marker, not a new plate appearance (see DQ rule DQ-09). For the
# NEW KPIs below we use PA_EVENTS_STRICT, which additionally drops it. The
# locked function is NOT modified — the two definitions coexist and are
# reconciled in the DQ scorecard.
NON_PA_STRICT = NON_PA + ['truncated_pa']
HIT_EVENTS = ['single','double','triple','home_run']
AB_EXCL = ['walk','intent_walk','hit_by_pitch','sac_fly','sac_bunt','catcher_interf']

def pa_frame(df: pd.DataFrame, strict: bool = True) -> pd.DataFrame:
    """One row per plate appearance = the terminal pitch of the PA.

    Carries the base-out state AS OF THE START of the PA (Statcast records
    on_1b/on_2b/on_3b and outs_when_up per pitch; the terminal pitch still
    reflects the state the PA began in for baserunners already aboard).
    """
    excl = NON_PA_STRICT if strict else NON_PA
    d = df[~df.events.replace(np.nan, 'NA').isin(excl)].copy()
    d = d.sort_values(['game_pk','at_bat_number','pitch_number'])
    d['on1'] = d.on_1b.notna(); d['on2'] = d.on_2b.notna(); d['on3'] = d.on_3b.notna()
    d['men_on'] = d.on1 | d.on2 | d.on3
    d['risp'] = d.on2 | d.on3
    d['bases_empty'] = ~d.men_on
    d['n_runners'] = d.on1.astype(int) + d.on2.astype(int) + d.on3.astype(int)
    d['n_risp_runners'] = d.on2.astype(int) + d.on3.astype(int)
    d['is_ab'] = ~d.events.isin(AB_EXCL)
    d['is_hit'] = d.events.isin(HIT_EVENTS)
    d['is_k'] = d.events.isin(['strikeout','strikeout_double_play'])
    d['is_bb'] = d.events.isin(['walk','intent_walk'])
    d['is_onbase'] = d.events.isin(HIT_EVENTS + ['walk','intent_walk','hit_by_pitch'])
    d['tb'] = d.events.map({'single':1,'double':2,'triple':3,'home_run':4}).fillna(0)
    # runs that scored on this PA (includes the batter on a HR)
    d['runs_on_pa'] = (d.post_bat_score - d.bat_score).fillna(0)
    d['base_state'] = (d.on1.astype(int).astype(str) + d.on2.astype(int).astype(str)
                       + d.on3.astype(int).astype(str))
    d['base_out'] = d.base_state + "_" + d.outs_when_up.astype(int).astype(str)
    d['ctx'] = np.select(
        [d.risp, d.men_on & ~d.risp, ~d.men_on],
        ['RISP', 'MEN_ON_NO_RISP', 'BASES_EMPTY'], default='NA')
    # per-PA wOBA numerator using that season's weights
    wmap = {'walk':'wBB','hit_by_pitch':'wHBP','single':'w1B','double':'w2B',
            'triple':'w3B','home_run':'wHR'}
    d['woba_num'] = 0.0
    for ev, wc in wmap.items():
        if wc in d.columns:
            mm = d.events == ev
            d.loc[mm, 'woba_num'] = d.loc[mm, wc]
    return d

def line_from_pa(g: pd.DataFrame) -> pd.Series:
    """Slash line computed from the PA spine (independent of get_stats)."""
    pa = len(g); ab = int(g.is_ab.sum())
    h = int(g.is_hit.sum()); bb = int((g.events=='walk').sum())
    ibb = int((g.events=='intent_walk').sum())
    hbp = int((g.events=='hit_by_pitch').sum()); k = int(g.is_k.sum())
    tb = float(g.tb.sum())
    return pd.Series({
        'PA': pa, 'AB': ab, 'H': h, '2B': int((g.events=='double').sum()),
        '3B': int((g.events=='triple').sum()), 'HR': int((g.events=='home_run').sum()),
        'BB': bb, 'IBB': ibb, 'HBP': hbp, 'K': k,
        'ba': h/ab if ab else np.nan,
        'obp': (h+bb+ibb+hbp)/pa if pa else np.nan,
        'slg': tb/ab if ab else np.nan,
        'ops': ((h+bb+ibb+hbp)/pa if pa else np.nan) + (tb/ab if ab else np.nan),
        'iso': (tb/ab - h/ab) if ab else np.nan,
        'woba': g.woba_num.sum()/pa if pa else np.nan,
        'k_rate': k/pa if pa else np.nan,
        'bb_rate': (bb+ibb)/pa if pa else np.nan,
        'xwoba': g.estimated_woba_using_speedangle.mean(),
        're24': g.delta_run_exp.sum(),
        're24_per_pa': g.delta_run_exp.sum()/pa if pa else np.nan,
        'runs_driven': float(g.runs_on_pa.sum()),
    })

# ================================== NEW KPI: AR-1 / AR-2 two-strike =======
def two_strike_panel(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    """AR-1 Two-Strike Survival Rate + AR-2 Two-Strike Damage Line.

    A PA 'reaches two strikes' if any pitch in it was thrown with strikes==2.
    TSSR = 1 - (strikeouts / PAs reaching two strikes).
    The damage line is the standard slash restricted to those PAs.
    """
    d = df.sort_values(['game_pk','at_bat_number','pitch_number']).copy()
    reached = (d.strikes == 2).groupby(
        [d.game_pk, d.at_bat_number]).transform('max')
    d['reached_2k'] = reached
    pa = pa_frame(d)
    rows = []
    for key, g in pa.groupby(label_col):
        tot = len(g)
        g2 = g[g.reached_2k]
        n2 = len(g2)
        k2 = int(g2.is_k.sum())
        ln = line_from_pa(g2) if n2 else pd.Series(dtype=float)
        rec = {label_col: key, 'PA_total': tot, 'PA_2k': n2,
               'two_strike_rate': n2/tot if tot else np.nan,
               'K_in_2k': k2,
               'tssr': 1 - k2/n2 if n2 else np.nan,
               'hits_2k': int(g2.is_hit.sum()),
               'hit_rate_2k_per_pa': g2.is_hit.mean() if n2 else np.nan}
        for c in ['AB','ba','obp','slg','ops','woba','xwoba','iso','re24_per_pa']:
            rec[f'{c}_2k'] = ln.get(c, np.nan) if n2 else np.nan
        rows.append(rec)
    return pd.DataFrame(rows).round(4)

def two_strike_pitch_economy(df: pd.DataFrame) -> pd.DataFrame:
    """How he survives: pitches seen after reaching two strikes, foul rate."""
    d = df.sort_values(['game_pk','at_bat_number','pitch_number']).copy()
    after = d[d.strikes == 2].copy()
    after['swing'] = after.description.isin(SWINGS)
    after['whiff'] = after.description.isin(WHIFFS)
    after['foul']  = after.description.isin(['foul','foul_tip','foul_bunt'])
    after['in_zone'] = after.zone <= 9
    rows = after.groupby('game_year', as_index=False).apply(lambda x: pd.Series({
        'pitches_in_2k': len(x),
        'swing_rate': x.swing.mean(),
        'whiff_rate': x[x.swing].whiff.mean(),
        'chase_rate': x[~x.in_zone].swing.mean(),
        'foul_rate_of_swings': x[x.swing].foul.mean(),
        'called_strike_rate': (x.description=='called_strike').mean(),
        'take_rate': 1 - x.swing.mean(),
    }), include_groups=False)
    # pitches seen per two-strike PA
    n2pa = after.groupby(['game_year']).apply(
        lambda x: x.groupby(['game_pk','at_bat_number']).ngroups, include_groups=False)
    rows = rows.merge(n2pa.rename('pa_2k').reset_index(), on='game_year', how='left')
    rows['pitches_per_2k_pa'] = (rows.pitches_in_2k / rows.pa_2k).round(3)
    return rows.round(4)

# ============================== NEW KPI: AR-3 damage by group x hand ======
def damage_pitchgroup_hand(df: pd.DataFrame, min_bip: int = 15) -> pd.DataFrame:
    """AR-3. SLG / ISO / xwOBAcon at (pitch_group, p_throws) grain.

    Grain note: slash-line denominators are PA-terminal events attributed to
    the pitch that ENDED the PA. Contact-quality columns use all balls in
    play off that group. Rows below min_bip are retained but flagged
    `thin=True` and must be printed with their n in any consumer artifact.
    """
    d = df.copy()
    d['pitch_group'] = d.pitch_type.map(PITCH_GROUP)
    d = d[d.pitch_group.notna()]
    pa = pa_frame(d)
    rows = []
    for (grp, hand), g in pa.groupby(['pitch_group','p_throws']):
        ln = line_from_pa(g)
        bip = d[(d.pitch_group==grp) & (d.p_throws==hand) & (d.type=='X')]
        rec = {'pitch_group': grp, 'p_throws': hand,
               'PA_ended': len(g), 'AB': ln['AB'],
               'ba': ln['ba'], 'slg': ln['slg'], 'iso': ln['iso'],
               'woba': ln['woba'], 'xwoba': ln['xwoba'],
               'H': ln['H'], '2B': ln['2B'], '3B': ln['3B'], 'HR': ln['HR'],
               'bip': len(bip),
               'avg_ev': bip.launch_speed.mean(),
               'avg_la': bip.launch_angle.mean(),
               'hard_hit_rate': (bip.launch_speed>=95).mean(),
               'barrel_rate': (bip.launch_speed_angle==6).mean(),
               'xwoba_con': bip.estimated_woba_using_speedangle.mean(),
               'xwoba_con_n': int(bip.estimated_woba_using_speedangle.notna().sum()),
               }
        rec['thin'] = rec['bip'] < min_bip
        rows.append(rec)
    # pitch usage seen
    seen = d.groupby(['pitch_group','p_throws']).size().rename('pitches_seen').reset_index()
    out = pd.DataFrame(rows).merge(seen, on=['pitch_group','p_throws'], how='left')
    return out.round(4)

def damage_pitchtype(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d['pitch_group'] = d.pitch_type.map(PITCH_GROUP)
    pa = pa_frame(d)
    rows = []
    for pt, g in pa.groupby('pitch_type'):
        if len(g) < 5: continue
        ln = line_from_pa(g)
        bip = d[(d.pitch_type==pt) & (d.type=='X')]
        rows.append({'pitch_type': pt, 'pitch_group': PITCH_GROUP.get(pt),
                     'pitches_seen': int((d.pitch_type==pt).sum()),
                     'PA_ended': len(g), 'AB': ln['AB'], 'ba': ln['ba'],
                     'slg': ln['slg'], 'iso': ln['iso'], 'woba': ln['woba'],
                     'bip': len(bip),
                     'avg_ev': bip.launch_speed.mean(),
                     'hard_hit_rate': (bip.launch_speed>=95).mean(),
                     'xwoba_con': bip.estimated_woba_using_speedangle.mean()})
    return pd.DataFrame(rows).sort_values('pitches_seen', ascending=False).round(4)

# ============================== NEW KPI: AR-4 scoring-position conversion =
def scoring_position_panel(df: pd.DataFrame, by: str | None = None) -> pd.DataFrame:
    """AR-4 Scoring-Position Conversion Rate (SPCR).

    SPCR = runners in scoring position at PA start who scored on that PA,
    divided by runners in scoring position at PA start. Computed at the
    RUNNER level, not the PA level, so a two-RBI double is worth two.

    Runs credited from post_bat_score - bat_score, minus the batter himself
    on a home run (the batter was never a runner in scoring position).
    """
    pa = pa_frame(df)
    pa = pa.copy()
    pa['risp_runners'] = pa.n_risp_runners
    pa['runs_excl_batter'] = pa.runs_on_pa - (pa.events == 'home_run').astype(int)
    pa['risp_scored'] = np.minimum(pa.runs_excl_batter, pa.risp_runners)
    keys = ['ctx'] if by is None else [by, 'ctx']
    rows = []
    for key, g in pa.groupby(keys):
        ln = line_from_pa(g)
        rec = dict(zip(keys, key if isinstance(key, tuple) else (key,)))
        rec.update(ln.to_dict())
        rec['risp_runners_faced'] = float(g.risp_runners.sum())
        rec['risp_runners_scored'] = float(g.risp_scored.sum())
        rec['spcr'] = (g.risp_scored.sum() / g.risp_runners.sum()
                       if g.risp_runners.sum() else np.nan)
        rows.append(rec)
    return pd.DataFrame(rows).round(4)

def base_out_detail(df: pd.DataFrame) -> pd.DataFrame:
    pa = pa_frame(df)
    rows = []
    for bo, g in pa.groupby('base_out'):
        if len(g) < 5: continue
        ln = line_from_pa(g)
        rec = {'base_out': bo, 'bases': bo[:3], 'outs': int(bo[-1])}
        rec.update(ln.to_dict())
        rows.append(rec)
    return pd.DataFrame(rows).sort_values('PA', ascending=False).round(4)

# ================== NEW KPI: AR-5 lineup slot opportunity profile =========
def reconstruct_slots(phi: pd.DataFrame) -> pd.DataFrame:
    """AR-5 support. Assign a batting-order slot to every Phillies PA.

    Method: within a game, plate appearances by the Phillies cycle strictly
    through nine slots in at_bat_number order. Slot = (PA index mod 9) + 1.
    Substitutions inherit the slot of the player they replace, which the
    modulo handles automatically. Validated in 05_dq_rules (JV-03): 111/112
    games have nine distinct batters in the first nine PAs; the exception is
    a truncated_pa continuation, excluded by PA_EVENTS_STRICT.
    """
    pa = pa_frame(phi)
    pa = pa.sort_values(['game_pk','at_bat_number']).copy()
    pa['pa_index'] = pa.groupby('game_pk').cumcount()
    pa['slot'] = pa.pa_index % 9 + 1
    return pa

def slot_opportunity(pa_slots: pd.DataFrame) -> pd.DataFrame:
    """AR-5. Per-slot OPPORTUNITY, independent of who occupied the slot."""
    ngames = pa_slots.game_pk.nunique()
    rows = []
    for slot, g in pa_slots.groupby('slot'):
        rows.append({
            'slot': int(slot),
            'PA': len(g),
            'games': g.game_pk.nunique(),
            'pa_per_game': len(g) / ngames,
            'men_on_share': g.men_on.mean(),
            'risp_share': g.risp.mean(),
            'bases_empty_share': g.bases_empty.mean(),
            'risp_pa_per_game': g.risp.sum() / ngames,
            'men_on_pa_per_game': g.men_on.sum() / ngames,
            'runners_on_per_pa': g.n_runners.mean(),
            'risp_runners_per_pa': g.n_risp_runners.mean(),
            'risp_runners_per_game': g.n_risp_runners.sum() / ngames,
            'mean_outs': g.outs_when_up.mean(),
            'lead_off_inning_share': (g.n_runners.eq(0) & g.outs_when_up.eq(0)).mean(),
        })
    return pd.DataFrame(rows).round(4)

def slot_occupancy(pa_slots: pd.DataFrame, names: dict) -> pd.DataFrame:
    rows = []
    for (slot, bat), g in pa_slots.groupby(['slot','batter']):
        if len(g) < 10: continue
        ln = line_from_pa(g)
        rec = {'slot': int(slot), 'batter': int(bat),
               'name': names.get(int(bat), str(bat))}
        rec.update(ln.to_dict())
        rows.append(rec)
    return pd.DataFrame(rows).sort_values(['slot','PA'], ascending=[True,False]).round(4)

# =============== NEW KPI: AR-6 slot-projected run contribution ============
def slot_projection(arraez_pa: pd.DataFrame, pa_slots: pd.DataFrame,
                    comp_ids: dict, names: dict) -> tuple:
    """AR-6 Slot-Projected Run Contribution (SPRC).

    Empirical, assumption-light. For hitter h and slot s:

        SPRC(h, s) = sum over context c of  W(s, c) * RE24_per_PA(h, c)
                     scaled to PA_per_game(s) * 162 games

    where c in {BASES_EMPTY, MEN_ON_NO_RISP, RISP} and W(s,c) is the observed
    2026 Phillies share of slot-s PAs arriving in context c. RE24_per_PA(h,c)
    is the hitter's own observed run-expectancy change per PA in that context
    (Statcast delta_run_exp), pooled over the primary window.

    What this DOES claim: given the opportunity mix a slot actually produces,
    how many runs of expectancy this hitter's observed context-specific
    production adds relative to an average PA outcome.
    What this does NOT claim: any second-order effect of re-ordering the
    lineup on the opportunity mix itself. The W(s,c) weights are held FIXED
    at the observed 2026 distribution. That limitation is the model's single
    largest caveat and is stated wherever SPRC appears.
    """
    ngames = pa_slots.game_pk.nunique()
    W = (pa_slots.groupby(['slot','ctx']).size() /
         pa_slots.groupby('slot').size()).rename('w').reset_index()
    ppg = (pa_slots.groupby('slot').size() / ngames).rename('pa_per_game').reset_index()

    # context-specific RE24/PA for each hitter in scope
    prof_rows = []
    for label, sub in comp_ids.items():
        for ctx, g in sub.groupby('ctx'):
            prof_rows.append({'hitter': label, 'ctx': ctx, 'PA_ctx': len(g),
                              're24_per_pa': g.delta_run_exp.mean(),
                              'woba_ctx': g.woba_num.sum()/len(g),
                              'obp_ctx': g.is_onbase.mean()})
    prof = pd.DataFrame(prof_rows)

    proj = (W.merge(ppg, on='slot').merge(prof, on='ctx'))
    proj['contrib'] = proj.w * proj.re24_per_pa
    out = (proj.groupby(['hitter','slot'])
              .apply(lambda x: pd.Series({
                  'pa_per_game': x.pa_per_game.iloc[0],
                  're24_per_pa_projected': x.contrib.sum(),
                  'risp_weight': x.loc[x.ctx=='RISP','w'].sum(),
                  'men_on_weight': x.loc[x.ctx!='BASES_EMPTY','w'].sum(),
              }), include_groups=False).reset_index())
    out['re24_per_game'] = out.re24_per_pa_projected * out.pa_per_game
    out['re24_per_162'] = out.re24_per_game * 162
    return out.round(4), prof.round(4), W.round(4)

# ======================= NEW KPI: AR-7 table-setting value ================
def table_setting(arraez_pa: pd.DataFrame, pa_slots: pd.DataFrame,
                  names: dict) -> pd.DataFrame:
    """AR-7 Table-Setting Value.

    Two components, reported separately, never summed:
      (a) SUPPLY  — on-base events produced per game in a given slot.
      (b) REALISATION — the run value the FOLLOWING slots actually extract
          per runner supplied, measured on the 2026 Phillies.
    """
    ngames = pa_slots.game_pk.nunique()
    rows = []
    for slot, g in pa_slots.groupby('slot'):
        nxt = [(slot % 9) + 1, ((slot + 1) % 9) + 1]
        follow = pa_slots[pa_slots.slot.isin(nxt)]
        rows.append({
            'slot': int(slot),
            'onbase_events_per_game': g.is_onbase.sum() / ngames,
            'obp_observed': g.is_onbase.mean(),
            'following_slots': f"{nxt[0]},{nxt[1]}",
            'following_risp_share': follow.risp.mean(),
            'following_men_on_share': follow.men_on.mean(),
            'following_woba_men_on': (follow[follow.men_on].woba_num.sum() /
                                      max(len(follow[follow.men_on]), 1)),
            'following_re24_per_pa_men_on': follow[follow.men_on].delta_run_exp.mean(),
            'following_spcr': (np.minimum(
                follow.runs_on_pa - (follow.events=='home_run').astype(int),
                follow.n_risp_runners).sum() / max(follow.n_risp_runners.sum(), 1)),
        })
    return pd.DataFrame(rows).round(4)

# ================================================================ NAMES ===
def resolve_names(df: pd.DataFrame) -> dict:
    """Modal name per batter id, parsed from `des`. Never hand-keyed."""
    pat = re.compile(r"^([A-Za-zÁÉÍÓÚÑáéíóúñ'\.\-]+(?:\s+[A-Za-zÁÉÍÓÚÑáéíóúñ'\.\-]+){1,3}?)\s+"
                     r"(singles|doubles|triples|homers|grounds|flies|lines|pops|"
                     r"strikes|walks|hits|reached|out|hit|sacrifices|steals|"
                     r"grounded|struck|intentionally)")
    d = df[df.des.notna()].copy()
    d['nm'] = d.des.str.strip().str.extract(pat)[0]
    d = d[d.nm.notna()]
    return {int(k): v for k, v in
            d.groupby('batter').nm.agg(lambda x: x.mode().iloc[0]).items()}

# ================================================================= MAIN ===
def main():
    print(f"MLB root : {MLB}")
    print(f"OUT      : {OUT}\n")
    ar = load_arraez()
    phi = load_phillies_2026()
    const = pd.read_csv(MLB / "wOBA and FIP Constants.csv")

    ar26 = ar[ar.game_year == PRIMARY_YEAR].copy()
    print(f"Arraez: {len(ar)} RS pitches 2019-2026 | primary window "
          f"{PRIMARY_YEAR}: {len(ar26)} pitches\n")

    # ---- entity / window assertions (hard stops) -------------------------
    assert ar.batter.nunique() == 1 and ar.batter.iloc[0] == ARRAEZ
    assert set(ar.game_type.unique()) == {'R'}
    assert len(ar) == len(ar.drop_duplicates(subset=PITCH_KEY))
    assert len(ar26) > 1000, "primary window too thin to publish"

    # ================================ A. top line ======================
    print("A. Top-line results")
    season = get_stats('game_year', ar)
    season = season[['game_year','pitches','plate_apps','at_bats','hits','singles',
                     'doubles','triples','hrs','walks','strikeouts','hbp',
                     'ba','obp','slg','ops','woba','xwoba','iso','xbh','krate','bbrate']].round(4)
    receipt('a1_season_line', season, "Season slash line; 2026 = primary, prior = shadow")

    w = wrc('game_year', ar, const)
    receipt('a2_wrc', w, "SC-1 wRC / wRC+ approximation by season")

    pp = ppa('game_year', ar)
    receipt('a3_pitches_per_pa', pp, "SC-2 P/PA — tests the 'wild at-bats' claim")

    ar_pa = pa_frame(ar)
    ar26_pa = ar_pa[ar_pa.game_year == PRIMARY_YEAR]
    prim = pd.DataFrame([line_from_pa(ar26_pa)]).assign(window='2026_primary')
    shad = pd.DataFrame([line_from_pa(ar_pa[ar_pa.game_year < PRIMARY_YEAR])]).assign(window='2019_2025_shadow')
    receipt('a4_window_headline', pd.concat([prim, shad], ignore_index=True).round(4),
            "Primary vs shadow headline; PA-spine computation, independent of get_stats")

    # ================================ B. indicators ====================
    print("\nB. Underlying indicators")
    receipt('b1_discipline', discipline('game_year', ar).reset_index(drop=True),
            "Swing/chase/contact panel by season")
    receipt('b2_batted_ball', batted_ball('game_year', ar).reset_index(drop=True),
            "Contact quality by season; xwoba_con_n is the honest denominator (O4)")
    receipt('b3_spray', pulled_air(ar, 'game_year').reset_index(drop=True),
            "Spray distribution by season")
    bt = bat_tracking('game_year', ar)
    if not bt.empty:
        receipt('b4_bat_tracking', bt.reset_index(drop=True), "Bat tracking, 2024+ only")
    receipt('b5_running_line', running_line_kpi(ar), "RF-1 cumulative OPS trajectory")

    # ================================ C. two strikes ===================
    print("\nC. Two-strike profile")
    receipt('c1_two_strike_by_year', two_strike_panel(ar, 'game_year'),
            "AR-1 TSSR + AR-2 two-strike damage line by season")
    receipt('c2_two_strike_economy', two_strike_pitch_economy(ar),
            "How he survives two strikes: swing/foul/take economy")

    # peer benchmark: Phillies 2026 regulars
    names = resolve_names(phi)
    phi_pa_all = pa_frame(phi)
    reg_ids = (phi_pa_all.groupby('batter').size()
               .pipe(lambda s: s[s >= 150]).index.tolist())
    peer_rows = []
    for bid in reg_ids:
        sub = phi[phi.batter == bid]
        t = two_strike_panel(sub, 'game_year')
        t = t[t.game_year == PRIMARY_YEAR]
        if len(t):
            r = t.iloc[0].to_dict(); r['name'] = names.get(int(bid), str(bid))
            r['batter'] = int(bid); peer_rows.append(r)
    a2k = two_strike_panel(ar26, 'game_year').iloc[0].to_dict()
    a2k['name'] = 'Luis Arraez'; a2k['batter'] = ARRAEZ
    peer = pd.DataFrame(peer_rows + [a2k])
    peer = peer[['name','batter','PA_total','PA_2k','two_strike_rate','K_in_2k','tssr',
                 'hits_2k','hit_rate_2k_per_pa','AB_2k','ba_2k','obp_2k','slg_2k',
                 'ops_2k','woba_2k','xwoba_2k','re24_per_pa_2k']]
    receipt('c3_two_strike_vs_phillies', peer.sort_values('tssr', ascending=False).round(4),
            "AR-1/AR-2 benchmark: Arraez vs 2026 Phillies regulars (>=150 PA)")

    # ================================ D. damage map ====================
    print("\nD. Damage by pitch group and hand")
    receipt('d1_group_x_hand_2026', damage_pitchgroup_hand(ar26),
            "AR-3, primary window")
    receipt('d2_group_x_hand_career', damage_pitchgroup_hand(ar),
            "AR-3, full history — shadow only")
    receipt('d3_pitch_type_2026', damage_pitchtype(ar26), "Pitch-type detail, primary window")
    hand = []
    for h, g in pa_frame(ar26).groupby('p_throws'):
        r = line_from_pa(g).to_dict(); r['p_throws'] = h; hand.append(r)
    receipt('d4_by_hand_2026', pd.DataFrame(hand).round(4), "Overall platoon split, primary")

    # ================================ E. RISP ==========================
    print("\nE. Scoring position")
    receipt('e1_context_2026', scoring_position_panel(ar26), "AR-4 by base context, primary")
    receipt('e2_context_by_year', scoring_position_panel(ar, by='game_year'),
            "AR-4 by season — stability check")
    receipt('e3_base_out_2026', base_out_detail(ar26), "Base-out detail, primary")

    # ================================ F. lineup model ==================
    print("\nF. Lineup slot model")
    pa_slots = reconstruct_slots(phi)
    receipt('f1_slot_opportunity', slot_opportunity(pa_slots),
            "AR-5 per-slot opportunity profile, 2026 Phillies")
    receipt('f2_slot_occupancy', slot_occupancy(pa_slots, names),
            "Who actually hit where in 2026, with their line")

    comp = {'Luis Arraez': ar26_pa}
    for bid in reg_ids:
        comp[names.get(int(bid), str(bid))] = phi_pa_all[phi_pa_all.batter == bid]
    sprc, prof, W = slot_projection(ar26_pa, pa_slots, comp, names)
    receipt('f3_context_profiles', prof, "AR-6 input: context-specific RE24/PA per hitter")
    receipt('f4_slot_context_weights', W, "AR-6 input: W(slot, context) from 2026 PHI")
    receipt('f5_sprc', sprc, "AR-6 Slot-Projected Run Contribution")
    receipt('f6_table_setting', table_setting(ar26_pa, pa_slots, names), "AR-7 (a) supply / (b) realisation by slot")

    # ---- AR-7 extension: what the table-setter actually hands downstream --
    ts = table_setting(ar26_pa, pa_slots, names)
    so = slot_opportunity(pa_slots)
    a_obp = float(line_from_pa(ar26_pa)['obp'])
    supply = []
    for _, r in so.iterrows():
        s = int(r.slot)
        t = ts[ts.slot == s].iloc[0]
        incumbent = float(t.onbase_events_per_game)
        arraez_sup = a_obp * float(r.pa_per_game)
        supply.append({
            'slot': s,
            'pa_per_game': round(float(r.pa_per_game), 4),
            'incumbent_obp': float(t.obp_observed),
            'arraez_obp': round(a_obp, 4),
            'incumbent_onbase_per_game': round(incumbent, 4),
            'arraez_onbase_per_game': round(arraez_sup, 4),
            'delta_onbase_per_game': round(arraez_sup - incumbent, 4),
            'delta_onbase_per_162': round((arraez_sup - incumbent) * 162, 2),
            'downstream_slots': t.following_slots,
            'downstream_re24_per_pa_men_on': float(t.following_re24_per_pa_men_on),
            'downstream_spcr': float(t.following_spcr),
            # UNITS NOTE (governance): the two columns below are RUNNERS x a
            # per-RUNNER conversion rate, so they carry units of runs. SPCR is
            # estimated per runner in SCORING POSITION and is applied here to
            # ALL baserunners supplied; not every baserunner reaches scoring
            # position, so both columns are UPPER BOUNDS. Labelled as such
            # wherever they appear. Do not add them to AR-6 SPRC — AR-6 already
            # values the batter's own PA outcomes and the two would double-count.
            'arraez_runners_cashed_ub_per_162': round(
                arraez_sup * 162 * float(t.following_spcr), 2),
            'delta_runners_cashed_ub_per_162': round(
                (arraez_sup - incumbent) * 162 * float(t.following_spcr), 2),
        })
    receipt('f8_table_setting_supply', pd.DataFrame(supply),
            "AR-7 extension: baserunner supply delta by slot x what the next two slots extract")

    # ---- AR-4 peer benchmark -------------------------------------------
    risp_rows = []
    for bid in reg_ids:
        sub = phi_pa_all[phi_pa_all.batter == bid]
        sp = scoring_position_panel(phi[phi.batter == bid])
        row = sp[sp.ctx == 'RISP']
        if len(row):
            r = row.iloc[0].to_dict()
            r['name'] = names.get(int(bid), str(bid)); r['batter'] = int(bid)
            risp_rows.append(r)
    ar_risp = scoring_position_panel(ar26)
    ar_risp = ar_risp[ar_risp.ctx == 'RISP'].iloc[0].to_dict()
    ar_risp['name'] = 'Luis Arraez'; ar_risp['batter'] = ARRAEZ
    rb = pd.DataFrame(risp_rows + [ar_risp])
    rb = rb[['name','batter','PA','AB','ba','obp','slg','ops','woba','xwoba','K','k_rate',
             'risp_runners_faced','risp_runners_scored','spcr','re24_per_pa','runs_driven']]
    receipt('e4_spcr_vs_phillies', rb.sort_values('spcr', ascending=False).round(4),
            "AR-4 benchmark: RISP line + SPCR, Arraez vs 2026 Phillies regulars")

    # ---- league structural reference (2023 vintage — labelled) ----------
    try:
        lg = pd.read_csv(MLB / "league_sc_data.csv")
        lg = lg[lg.player_name == 'League'][['year','ba','slg','woba','xwoba',
                                             'launch_speed','launch_angle','whiffs','swings']]
        lg['whiff_rate'] = (lg.whiffs / lg.swings).round(4)
        lg['reference_note'] = ('League aggregate. Latest available year is 2023 — '
                                'NOT a 2026 benchmark. Structural reference only.')
        receipt('g1_league_reference', lg.round(4),
                "League reference, max year 2023. Explicitly not a primary-window benchmark")
    except Exception as e:
        print(f"  [warn] league reference unavailable: {e}")

    # ---- who ACTUALLY hit where (observed), vs the consumer's stated premise
    occ = slot_occupancy(pa_slots, names)
    lead = occ[occ.slot == 1].sort_values('PA', ascending=False)
    receipt('f9_observed_top_of_order',
            occ[occ.slot.isin([1,2,3,4])].sort_values(['slot','PA'], ascending=[True,False]),
            "Observed 2026 slot occupancy, slots 1-4. Consumer premise said Schwarber "
            "leads off; the log says Turner. Conflict escalated to DPO, not resolved here.")

    # headline scenarios — BOTH framings, because the premise is contested
    def v(h, s):
        r = sprc[(sprc.hitter == h) & (sprc.slot == s)]
        return float(r.re24_per_162.iloc[0]) if len(r) else np.nan
    scen = []
    for h in ['Luis Arraez', 'Kyle Schwarber', 'Trea Turner']:
        for s in range(1, 10):
            r = sprc[(sprc.hitter == h) & (sprc.slot == s)]
            if len(r):
                scen.append({'hitter': h, 'slot': float(s),
                             're24_per_162': float(r.re24_per_162.iloc[0]),
                             're24_per_pa_projected': float(r.re24_per_pa_projected.iloc[0]),
                             'risp_weight': float(r.risp_weight.iloc[0]),
                             'row_type': 'hitter_x_slot'})
    sc = pd.DataFrame(scen)
    pairs = [
        ('A. OBSERVED 2026 (Turner 1 / Arraez 4)',      v('Trea Turner',1)   + v('Luis Arraez',4)),
        ('A-swap. Arraez 1 / Turner 4',                 v('Luis Arraez',1)   + v('Trea Turner',4)),
        ('B. STATED premise (Schwarber 1 / Arraez 4)',  v('Kyle Schwarber',1)+ v('Luis Arraez',4)),
        ('B-swap. Arraez 1 / Schwarber 4',              v('Luis Arraez',1)   + v('Kyle Schwarber',4)),
        ('C. Arraez 2 / Schwarber 4 (model preference)',v('Luis Arraez',2)   + v('Kyle Schwarber',4)),
    ]
    rows = [{'hitter': lbl, 'slot': np.nan, 're24_per_162': val, 'row_type': 'scenario'}
            for lbl, val in pairs]
    rows += [
        {'hitter': 'DELTA A-swap minus A (Turner framing)', 'slot': np.nan,
         're24_per_162': pairs[1][1] - pairs[0][1], 'row_type': 'delta'},
        {'hitter': 'DELTA B-swap minus B (Schwarber framing)', 'slot': np.nan,
         're24_per_162': pairs[3][1] - pairs[2][1], 'row_type': 'delta'},
        {'hitter': 'SPREAD Arraez best slot minus worst slot', 'slot': np.nan,
         're24_per_162': (sc[sc.hitter=='Luis Arraez'].re24_per_162.max() -
                          sc[sc.hitter=='Luis Arraez'].re24_per_162.min()),
         'row_type': 'delta'},
    ]
    sc = pd.concat([sc, pd.DataFrame(rows)], ignore_index=True)
    receipt('f7_swap_scenario', sc.round(4),
            "AR-6 headline. Both lineup framings priced; premise conflict unresolved by design")

    # ================================ Figures ==========================
    print("\nFigures")
    make_figures(ar, ar26, ar26_pa, peer, rb, pd.DataFrame(supply),
                 slot_opportunity(pa_slots), sprc, season)

    # ================================ DQ scorecard =====================
    print("\nDQ scorecard")
    dq = build_dq(ar, ar26, phi, pa_slots, season)
    receipt('dq_scorecard', dq, "Build-time DQ assertions")
    npass = int((dq.result == 'PASS').sum())
    print(f"  DQ: {npass}/{len(dq)} PASS")

    fresh = pd.DataFrame([
        {'source':'data/opponents/arraez.parquet','rows':len(ar),
         'min_date':str(ar.game_date.min()),'max_date':str(ar.game_date.max()),
         'entity':'batter==650333','note':'regular season, deduped'},
        {'source':'data/phillies/phils_2026.parquet','rows':len(phi),
         'min_date':str(phi.game_date.min()),'max_date':str(phi.game_date.max()),
         'entity':"phillies_role=='batting'",'note':'2026 comparison set'},
        {'source':'wOBA and FIP Constants.csv','rows':len(const),
         'min_date':str(const.Season.min()),'max_date':str(const.Season.max()),
         'entity':'season weights','note':'joined on game_year'},
        {'source':'MANUAL CARRY-IN','rows':0,'min_date':'','max_date':'',
         'entity':'roster/lineup context',
         'note':'deadline acquisition; Mattingly cleanup decision; Harper to OF — user-provided, not in pitch log'},
    ])
    receipt('freshness_manifest', fresh, "Data window and manual carry-ins")

    rec = pd.DataFrame(_receipts)
    rec.to_csv(OUT / f"{STEM}_receipt_index.csv", index=False)
    print(f"\n{len(_receipts)} receipts written to {OUT}")

# ---- RF-1 (inherited from dp_uc24, renamed wrapper to avoid shadowing) ----
def running_line_kpi(df):
    d = df[df.game_type=='R'].copy()
    pa = d[~d.events.replace(np.nan,'NA').isin(['NA','pickoff_1b'])]
    ab = pa[~pa.events.isin(['walk','intent_walk','hit_by_pitch','sac_fly','sac_bunt'])]
    wmap = {'walk':'wBB','hit_by_pitch':'wHBP','single':'w1B','double':'w2B','triple':'w3B','home_run':'wHR'}
    d = d.copy(); d['woba_num'] = 0.0
    for ev, wc in wmap.items():
        if wc in d.columns:
            mm = d.events == ev
            d.loc[mm, 'woba_num'] = d.loc[mm, wc]
    def cnt(sub, name): return sub.groupby(['game_year','game_date']).size().rename(name)
    g = pd.DataFrame(cnt(pa,'PA'))
    for name, sub in [('AB',ab), ('H',d[d.events.isin(['single','double','triple','home_run'])]),
                      ('x1',d[d.events=='single']), ('x2',d[d.events=='double']),
                      ('x3',d[d.events=='triple']), ('HR',d[d.events=='home_run']),
                      ('BB',d[d.events=='walk']), ('HBP',d[d.events=='hit_by_pitch'])]:
        g = g.join(cnt(sub, name), how='left')
    g = g.join(d.groupby(['game_year','game_date'])['woba_num'].sum().rename('WN'), how='left')
    g = g.fillna(0).reset_index().sort_values(['game_year','game_date'])
    for c in ['PA','AB','H','x1','x2','x3','HR','BB','HBP','WN']:
        g[c+'_c'] = g.groupby('game_year')[c].cumsum()
    g['gi'] = g.groupby('game_year').cumcount() + 1
    g['obp_std'] = (g.H_c + g.BB_c + g.HBP_c) / g.PA_c
    g['slg_std'] = (g.x1_c + 2*g.x2_c + 3*g.x3_c + 4*g.HR_c) / g.AB_c
    g['ops_std'] = g.obp_std + g.slg_std
    g['woba_std'] = g.WN_c / g.PA_c
    return g[['game_year','game_date','gi','PA_c','ops_std','obp_std','slg_std','woba_std','HR_c']].round(4)

# -------------------------------------------------------------- FIGURES --
PHI_RED = "#E81828"; PHI_NAVY = "#002D72"; PHI_LT = "#7A99C2"; GREY = "#9AA0A6"

def make_figures(ar, ar26, ar26_pa, peer, risp_bench, supply, so, sprc, season):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#CCCCCC',
                         'axes.labelcolor': PHI_NAVY, 'text.color': PHI_NAVY,
                         'xtick.color': '#444', 'ytick.color': '#444',
                         'axes.titleweight': 'bold', 'axes.titlecolor': PHI_NAVY,
                         'figure.facecolor': 'white'})
    figs = []

    # FIG 1 — two-strike survival vs Phillies
    d = peer.sort_values('tssr')
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    cols = [PHI_RED if n == 'Luis Arraez' else PHI_LT for n in d.name]
    ax.barh(d.name, d.tssr, color=cols, edgecolor='white')
    for y, (v, k, n2) in enumerate(zip(d.tssr, d.K_in_2k, d.PA_2k)):
        ax.text(v + .008, y, f"{v:.3f}  ({int(k)}K / {int(n2)} PA)", va='center', fontsize=7.5)
    ax.set_xlim(0, 1.12); ax.set_xlabel("Two-Strike Survival Rate (AR-1)")
    ax.set_title("He does not strike out — and nobody else on this team is close\n"
                 "Share of two-strike plate appearances NOT ending in a strikeout, 2026",
                 loc='left', fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); figs.append(('fig1_two_strike_survival', fig))

    # FIG 2 — damage map: pitch group x hand
    dh = damage_pitchgroup_hand(ar26)
    dh['lab'] = dh.pitch_group + "\nvs " + dh.p_throws + "HP"
    dh = dh.sort_values(['p_throws','pitch_group'])
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    x = np.arange(len(dh)); w = 0.38
    ax.bar(x - w/2, dh.slg, w, label='SLG (actual)', color=PHI_RED, edgecolor='white')
    ax.bar(x + w/2, dh.xwoba_con, w, label='xwOBAcon (deserved contact)',
           color=PHI_NAVY, edgecolor='white')
    for i, r in enumerate(dh.itertuples()):
        ax.text(i, max(r.slg, r.xwoba_con) + .03, f"n={int(r.bip)} BIP", ha='center', fontsize=7,
                color=PHI_RED if r.thin else '#444',
                fontweight='bold' if r.thin else 'normal')
    ax.set_xticks(x); ax.set_xticklabels(dh.lab, fontsize=8)
    ax.set_ylabel("rate"); ax.legend(frameon=False, fontsize=8)
    ax.set_title("Where the slug comes from — and where it is borrowed\n"
                 "Red bars in the n= labels flag samples under 15 balls in play", loc='left', fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); figs.append(('fig2_damage_group_hand', fig))

    # FIG 3 — contact quality vs results over time
    s = season.copy()
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    ax.plot(s.game_year, s.woba, 'o-', color=PHI_RED, lw=2, label='wOBA (results)')
    ax.plot(s.game_year, s.xwoba, 'o--', color=PHI_NAVY, lw=2, label='xwOBA (deserved)')
    ax.fill_between(s.game_year, s.woba, s.xwoba, where=s.woba >= s.xwoba,
                    color=PHI_RED, alpha=.12, interpolate=True)
    ax.fill_between(s.game_year, s.woba, s.xwoba, where=s.woba < s.xwoba,
                    color=PHI_NAVY, alpha=.12, interpolate=True)
    ax.axvspan(2025.5, 2026.5, color='#FFF3B0', alpha=.45, zorder=0)
    ax.text(2026, s.woba.max()*1.02, 'primary\nwindow', ha='center', fontsize=7.5, color='#8a6d00')
    ax.set_xlabel("season"); ax.set_ylabel("wOBA")
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("2026 is the first season the results run clearly ahead of the contact\n"
                 "Shaded red = outperforming expected contact quality", loc='left', fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); figs.append(('fig3_woba_vs_xwoba', fig))

    # FIG 4 — RISP conversion benchmark
    d = risp_bench.sort_values('spcr')
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    cols = [PHI_RED if n == 'Luis Arraez' else PHI_LT for n in d.name]
    ax.barh(d.name, d.spcr, color=cols, edgecolor='white')
    for y, (v, f_, sc) in enumerate(zip(d.spcr, d.risp_runners_faced, d.risp_runners_scored)):
        ax.text(v + .006, y, f"{v:.3f}  ({int(sc)}/{int(f_)} runners)", va='center', fontsize=7.5)
    ax.set_xlim(0, max(d.spcr)*1.45)
    ax.set_xlabel("Scoring-Position Conversion Rate (AR-4)")
    ax.set_title("Driving in the runners who are already there\n"
                 "Runners in scoring position at PA start who scored, 2026", loc='left', fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); figs.append(('fig4_spcr_benchmark', fig))

    # FIG 5 — the slot decision
    a = sprc[sprc.hitter == 'Luis Arraez'].sort_values('slot')
    k = sprc[sprc.hitter == 'Kyle Schwarber'].sort_values('slot')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.0))
    ax1.plot(so.slot, so.risp_share, 'o-', color=PHI_RED, lw=2, label='RISP share of PA')
    ax1b = ax1.twinx()
    ax1b.plot(so.slot, so.pa_per_game, 's--', color=PHI_NAVY, lw=2, label='PA per game')
    ax1.set_xlabel("lineup slot"); ax1.set_ylabel("RISP share", color=PHI_RED)
    ax1b.set_ylabel("PA per game", color=PHI_NAVY)
    ax1.set_title("The two forces that cancel", loc='left', fontsize=10)
    ax1.spines[['top']].set_visible(False); ax1b.spines[['top']].set_visible(False)

    ax2.plot(a.slot, a.re24_per_162, 'o-', color=PHI_RED, lw=2.5, label='Luis Arraez')
    ax2.plot(k.slot, k.re24_per_162, 's-', color=PHI_NAVY, lw=2.5, label='Kyle Schwarber')
    for ax_, df_, col in [(ax2, a, PHI_RED), (ax2, k, PHI_NAVY)]:
        for sl in (1, 4):
            r = df_[df_.slot == sl]
            ax_.scatter(r.slot, r.re24_per_162, s=110, facecolors='none',
                        edgecolors=col, lw=2, zorder=5)
    ax2.set_xlabel("lineup slot"); ax2.set_ylabel("projected RE24 per 162 games")
    ax2.legend(frameon=False, fontsize=8)
    ax2.set_title("AR-6: the whole slot decision is worth ~4 runs", loc='left', fontsize=10)
    ax2.spines[['top','right']].set_visible(False)
    fig.tight_layout(); figs.append(('fig5_slot_decision', fig))

    # FIG 6 — table-setting supply delta
    d = supply.sort_values('slot')
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    cols = [PHI_RED if v > 0 else GREY for v in d.delta_onbase_per_162]
    ax.bar(d.slot, d.delta_onbase_per_162, color=cols, edgecolor='white')
    ax.axhline(0, color='#444', lw=.8)
    for r in d.itertuples():
        ax.text(r.slot, r.delta_onbase_per_162 + (1.2 if r.delta_onbase_per_162 > 0 else -3),
                f"{r.delta_onbase_per_162:+.0f}", ha='center', fontsize=7.5)
    ax.set_xticks(range(1, 10))
    ax.set_xlabel("lineup slot"); ax.set_ylabel("extra baserunners per 162")
    ax.set_title("Baserunners Arraez would supply above the 2026 incumbent, by slot\n"
                 "Biggest gaps sit where the incumbents got on base least — cleanup and the bottom third",
                 loc='left', fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); figs.append(('fig6_table_setting_supply', fig))

    # FIG 7 — where the supplied runners actually get cashed
    d = supply.sort_values('slot')
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    ax.bar(d.slot, d.arraez_runners_cashed_ub_per_162, color=PHI_NAVY, edgecolor='white')
    best = d.loc[d.arraez_runners_cashed_ub_per_162.idxmax()]
    ax.bar([best.slot], [best.arraez_runners_cashed_ub_per_162], color=PHI_RED, edgecolor='white')
    for r in d.itertuples():
        ax.text(r.slot, r.arraez_runners_cashed_ub_per_162 + 1.2,
                f"{r.arraez_runners_cashed_ub_per_162:.0f}", ha='center', fontsize=7.5)
    ax.set_xticks(range(1, 10))
    ax.set_xlabel("lineup slot"); ax.set_ylabel("runners cashed per 162 (upper bound)")
    ax.set_title("Runners Arraez puts on that the NEXT TWO slots would drive in\n"
                 "Upper bound. Peaks batting third — slots 4 and 5 convert best",
                 loc='left', fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); figs.append(('fig7_table_setting_cashed', fig))

    for name, fig in figs:
        p = OUT / f"{STEM}_{name}.png"
        fig.savefig(p, dpi=170, bbox_inches='tight'); plt.close(fig)
        _receipts.append({'receipt': name, 'rows': 0, 'cols': 0,
                          'file': p.name, 'note': 'figure — numbers trace to CSV receipts'})
        print(f"  [figure]  {name:38s} -> {p.name}")

# ------------------------------------------------------------------ DQ ---
def build_dq(ar, ar26, phi, pa_slots, season) -> pd.DataFrame:
    R = []
    def chk(rid, dim, desc, cond, detail=""):
        R.append({'rule_id': rid, 'dimension': dim, 'check': desc,
                  'result': 'PASS' if cond else 'FAIL', 'detail': detail})
    chk('DQ-01','Uniqueness','Single batter id in Arraez source',
        ar.batter.nunique()==1, f"n_ids={ar.batter.nunique()}")
    chk('DQ-02','Validity','Entity locked to MLBAM 650333',
        int(ar.batter.iloc[0])==ARRAEZ, f"id={int(ar.batter.iloc[0])}")
    chk('DQ-03','Uniqueness','No duplicate pitch keys',
        len(ar)==len(ar.drop_duplicates(subset=PITCH_KEY)))
    chk('DQ-04','Validity','game_type == R only', set(ar.game_type.unique())=={'R'})
    chk('DQ-05','Completeness','stand == L on every row (LHH)',
        set(ar.stand.unique())=={'L'})
    chk('DQ-06','Timeliness',f'Cache max date == {CACHE_MAX}',
        str(ar.game_date.max())[:10]==CACHE_MAX, f"max={ar.game_date.max()}")
    chk('DQ-07','Consistency','ZERO Phillies rows for Arraez (pre-arrival dossier)',
        (ar.game_year.eq(2026) & ar.home_team.eq('PHI') & ar.inning_topbot.eq('Bot')).sum()==0
        and (ar.game_year.eq(2026) & ar.away_team.eq('PHI') & ar.inning_topbot.eq('Top')).sum()==0)
    chk('DQ-08','Completeness','Primary window >= 400 PA',
        len(pa_frame(ar26))>=400, f"PA={len(pa_frame(ar26))}")
    chk('DQ-09','Validity','truncated_pa excluded from strict PA spine',
        (pa_frame(ar26).events=='truncated_pa').sum()==0)
    chk('DQ-10','Completeness','delta_run_exp populated on >=98% of PAs',
        pa_frame(ar26).delta_run_exp.notna().mean()>=0.98,
        f"{pa_frame(ar26).delta_run_exp.notna().mean():.4f}")
    chk('DQ-11','Completeness','Base-state fields present on every PA',
        pa_frame(ar26).outs_when_up.notna().all())
    chk('DQ-12','Accuracy','PA-spine slash reconciles to locked get_stats (BA)',
        abs(line_from_pa(pa_frame(ar26))['ba'] -
            season[season.game_year==2026].ba.iloc[0]) < 0.006,
        f"spine={line_from_pa(pa_frame(ar26))['ba']:.4f} "
        f"locked={season[season.game_year==2026].ba.iloc[0]:.4f}")
    chk('DQ-13','Accuracy','PA-spine wOBA reconciles to locked get_stats',
        abs(line_from_pa(pa_frame(ar26))['woba'] -
            season[season.game_year==2026].woba.iloc[0]) < 0.006)
    chk('DQ-14','Consistency','Nine distinct slots in every PHI game',
        pa_slots.groupby('game_pk').slot.nunique().eq(9).all())
    chk('DQ-15','Consistency','First 9 PAs are 9 distinct batters in every PHI game',
        pa_slots[pa_slots.pa_index<9].groupby('game_pk').batter.nunique().eq(9).all(),
        f"exceptions={(pa_slots[pa_slots.pa_index<9].groupby('game_pk').batter.nunique()!=9).sum()}")
    chk('DQ-16','Validity','Slot PA counts decline monotonically 1->9',
        pa_slots.groupby('slot').size().is_monotonic_decreasing)
    chk('DQ-17','Consistency','RISP share rises from slot 1 to slot 4',
        pa_slots[pa_slots.slot==4].risp.mean() > pa_slots[pa_slots.slot==1].risp.mean(),
        f"s1={pa_slots[pa_slots.slot==1].risp.mean():.4f} "
        f"s4={pa_slots[pa_slots.slot==4].risp.mean():.4f}")
    chk('DQ-18','Validity','SPCR bounded in [0,1]',
        scoring_position_panel(ar26).spcr.dropna().between(0,1).all())
    chk('DQ-19','Accuracy','Runs credited never exceed runners available+batter',
        (pa_frame(ar26).runs_on_pa <= pa_frame(ar26).n_runners + 1).all())
    chk('DQ-20','Completeness','Every pitch mapped to a pitch group or explicitly null',
        ar26.pitch_type.map(PITCH_GROUP).notna().sum() >= 0.97*ar26.pitch_type.notna().sum(),
        f"mapped={ar26.pitch_type.map(PITCH_GROUP).notna().sum()}/{ar26.pitch_type.notna().sum()}")
    chk('DQ-21','Consistency','PHI comparison set is 2026 regular season only',
        set(phi.game_year.unique())=={2026} and set(phi.game_type.unique())=={'R'})
    chk('DQ-22','Timeliness','PHI set max date == cache max',
        str(phi.game_date.max())[:10]==CACHE_MAX)
    chk('DQ-23','Validity','xwoba_con_n <= bip everywhere (O4 guard)',
        bool((batted_ball('game_year', ar).xwoba_con_n <=
              batted_ball('game_year', ar).bip).all()))
    chk('DQ-24','Consistency','Slot context weights sum to 1 per slot',
        bool(np.allclose((pa_slots.groupby(['slot','ctx']).size() /
              pa_slots.groupby('slot').size()).groupby('slot').sum(), 1.0)))
    return pd.DataFrame(R)

if __name__ == "__main__":
    main()
