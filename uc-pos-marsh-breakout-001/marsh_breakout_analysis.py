"""
============================================================================
GOVERNED DATA PRODUCT — uc-pos-marsh-breakout-001  (UC #18)
"Brandon Marsh 2026 First-Half Breakout: what changed?"
============================================================================
Layer-3 BUILD artifact, Phillies Position-player (pos) value stream.
Pattern lineage: uc-pos-marsh-xbh-001 (entity), UC11 (evidence tiers,
locked-KPI inheritance), UC8 (canonical flat-file build).

Locked KPI mechanics inherited VERBATIM from Baseball Functions.ipynb:
  get_stats / measure_calcs (ba, obp, slg, ops, woba), whiff_rate,
  chase_rate (zone>9), hard_hit_rate (EV>=95 on type=='X'),
  barrel = launch_speed_angle==6. wOBA weights joined on game_year==Season.

DATA WINDOW / FRESHNESS:
  * Entity lock: batter == 669016 (Brandon Marsh), game_type == 'R'.
  * LAA era 2021-07-18 .. 2022-07-31 : data/opponents/marsh.parquet
  * PHI era 2022-08-04 .. 2026-07-12 : data/phillies/phils_{2022..2026}.parquet
    (phillies_role == 'batting'). Cache fresh through 2026-07-12 = full
    2026 first half (All-Star break).
  * Dedup on ['game_pk','at_bat_number','pitch_number'].
============================================================================
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

MLB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else MLB / "out"
OUT.mkdir(exist_ok=True)
PITCH_KEY = ["game_pk", "at_bat_number", "pitch_number"]
MARSH = 669016

# ---------------------------------------------------------------- load ----
def load_marsh() -> pd.DataFrame:
    frames = [pd.read_parquet(MLB / "data/opponents/marsh.parquet")]
    for yr in range(2022, 2027):
        df = pd.read_parquet(MLB / f"data/phillies/phils_{yr}.parquet")
        frames.append(df[(df.phillies_role == "batting") & (df.batter == MARSH)])
    m = pd.concat(frames, ignore_index=True)
    m = m[m.batter == MARSH]
    m = m[m.game_type == "R"]
    m = m.drop_duplicates(subset=PITCH_KEY)
    # wOBA weights (idempotent re-join, mirrors mlb_data._apply_woba_weights)
    w = pd.read_csv(MLB / "wOBA and FIP Constants.csv")
    m = m.drop(columns=[c for c in w.columns if c != "Season" and c in m.columns])
    m = m.merge(w, left_on="game_year", right_on="Season", suffixes=("_bad", ""), how="left")
    return m

# ------------------------------------------- locked KPI kernel (verbatim) --
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
    out['krate'] = out.strikeouts / out.plate_apps
    out['bbrate'] = out.walks / out.plate_apps
    return out

def chase_rate(level, df):
    if isinstance(level, str): level = [level]
    sw = df[(df.zone>9) & (df.description.isin(SWINGS))].groupby(level, as_index=False).agg(chases=('des','size'))
    oz = df[df.zone>9].groupby(level, as_index=False).agg(ooz=('des','size'))
    cr = sw.merge(oz, on=level, how='right')
    tot = df.groupby(level, as_index=False).agg(pitches=('des','size'))
    cr = cr.merge(tot, on=level)
    cr['chase_rate'] = cr.chases / cr.ooz
    cr['in_zone_rate'] = (cr.pitches - cr.ooz) / cr.pitches
    return cr.round(3)

def discipline(level, df):
    """Zone-aware swing/contact panel built on the locked swing/whiff lists."""
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
    return rows.round(3)

def batted_ball(level, df):
    if isinstance(level, str): level = [level]
    b = df[df.type=='X'].copy()
    b['barrel'] = b.launch_speed_angle == 6
    b['hard'] = b.launch_speed >= 95
    b['sweet'] = b.launch_angle.between(8, 32)
    b['air'] = b.bb_type.isin(['fly_ball','line_drive'])
    # pull for LHB: hc_x > 125.42 is opposite field; use spray via stand
    b['pull'] = np.where(b.stand=='L', b.hc_x > 125.42+12, b.hc_x < 125.42-12)  # placeholder, refined below
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
    }), include_groups=False)
    return rows.round(3)

def pulled_air(df, level):
    """Pulled air-ball rate for a LHB: spray angle from hc_x/hc_y."""
    if isinstance(level, str): level = [level]
    b = df[(df.type=='X') & df.hc_x.notna() & df.hc_y.notna()].copy()
    b['spray'] = np.degrees(np.arctan2(b.hc_x - 125.42, 198.27 - b.hc_y))
    # LHB pull side = right field = positive spray angle
    b['pulled'] = np.where(b.stand=='L', b.spray > 15, b.spray < -15)
    b['oppo'] = np.where(b.stand=='L', b.spray < -15, b.spray > 15)
    b['air'] = b.bb_type.isin(['fly_ball','line_drive'])
    rows = b.groupby(level, as_index=False).apply(lambda x: pd.Series({
        'bip_traced': len(x),
        'pull_rate': x.pulled.mean(),
        'oppo_rate': x.oppo.mean(),
        'pulled_air_rate': (x.pulled & x.air).mean(),
        'pulled_air_ct': (x.pulled & x.air).sum(),
        'gb_pull_rate': x[x.bb_type=='ground_ball'].pulled.mean(),
    }), include_groups=False)
    return rows.round(3)

PITCH_GROUP = {
    'FF':'fastball','SI':'fastball','FC':'fastball',
    'SL':'breaking','ST':'breaking','CU':'breaking','KC':'breaking','SV':'breaking','CS':'breaking',
    'CH':'offspeed','FS':'offspeed','FO':'offspeed','SC':'offspeed','KN':'offspeed',
}

def main():
    m = load_marsh()
    m['era'] = np.where(m.game_year < 2022, 'LAA',
                np.where((m.game_year==2022) & (m.game_date < '2022-08-02'), 'LAA', 'PHI'))
    m['season'] = m.game_year
    m['half'] = np.where(m.game_year==2026, '2026-1H', m.game_year.astype(str))
    m['pitch_group'] = m.pitch_type.map(PITCH_GROUP).fillna('other')
    m['count_state'] = np.select(
        [m.strikes==2, m.balls > m.strikes], ['two_strike','ahead'], default='even_or_behind')

    print(f"rows: {len(m)}  seasons: {sorted(m.season.unique())}")
    print(f"2026 window: {m[m.season==2026].game_date.min()} .. {m[m.season==2026].game_date.max()}")

    # 01 — results by season
    res = get_stats('season', m)
    res_out = res[['season','pitches','plate_apps','hits','doubles','triples','hrs','xbh',
                   'walks','strikeouts','ba','obp','slg','ops','woba','xwoba','krate','bbrate']].round(3)
    res_out.to_csv(OUT/'dp_uc18_marsh_breakout_results_by_season.csv', index=False)
    print("\n=== RESULTS BY SEASON ===\n", res_out.to_string(index=False))

    # 02 — discipline by season
    disc = discipline('season', m)
    disc.to_csv(OUT/'dp_uc18_marsh_breakout_discipline_by_season.csv', index=False)
    print("\n=== DISCIPLINE BY SEASON ===\n", disc.to_string(index=False))

    # 03 — batted ball by season
    bb = batted_ball('season', m)
    bb.to_csv(OUT/'dp_uc18_marsh_breakout_battedball_by_season.csv', index=False)
    print("\n=== BATTED BALL BY SEASON ===\n", bb.to_string(index=False))

    # 04 — spray / pulled air
    pa_ = pulled_air(m, 'season')
    pa_.to_csv(OUT/'dp_uc18_marsh_breakout_spray_by_season.csv', index=False)
    print("\n=== SPRAY BY SEASON ===\n", pa_.to_string(index=False))

    # 05 — platoon splits (vs LHP the historical hole)
    plat = get_stats(['season','p_throws'], m)
    plat = plat[['season','p_throws','plate_apps','ba','obp','slg','woba','xwoba','krate','bbrate','xbh']].round(3)
    plat.to_csv(OUT/'dp_uc18_marsh_breakout_platoon_by_season.csv', index=False)
    print("\n=== PLATOON BY SEASON ===\n", plat.to_string(index=False))

    disc_plat = discipline(['season','p_throws'], m[m.season.isin([2024,2025,2026])])
    disc_plat.to_csv(OUT/'dp_uc18_marsh_breakout_discipline_platoon.csv', index=False)
    print("\n=== DISCIPLINE x PLATOON (24-26) ===\n", disc_plat.to_string(index=False))

    # 06 — pitch-group splits
    pg = get_stats(['season','pitch_group'], m)
    pg = pg[['season','pitch_group','pitches','plate_apps','woba','xwoba','krate','xbh']].round(3)
    pg = pg.merge(discipline(['season','pitch_group'], m)[['season','pitch_group','whiff_rate','chase_rate']],
                  on=['season','pitch_group'])
    pg.to_csv(OUT/'dp_uc18_marsh_breakout_pitchgroup_by_season.csv', index=False)
    print("\n=== PITCH GROUP BY SEASON ===\n", pg[pg.season>=2023].to_string(index=False))

    # 07 — count leverage
    cs = get_stats(['season','count_state'], m)
    cs = cs[['season','count_state','pitches','plate_apps','woba','xwoba','krate']].round(3)
    cs.to_csv(OUT/'dp_uc18_marsh_breakout_countstate_by_season.csv', index=False)
    print("\n=== COUNT STATE BY SEASON (23-26) ===\n", cs[cs.season>=2023].to_string(index=False))

    # 08 — early count damage: swings at first pitch + results 0-0
    fp = m[(m.balls==0)&(m.strikes==0)]
    fp_res = batted_ball('season', fp[fp.type=='X'])
    fp_res.to_csv(OUT/'dp_uc18_marsh_breakout_firstpitch_bip.csv', index=False)
    print("\n=== FIRST-PITCH BIP QUALITY ===\n", fp_res.to_string(index=False))

    # 09 — monthly 2026
    m26 = m[m.season==2026].copy()
    m26['month'] = m26.game_date.astype(str).str[:7]
    mo = get_stats('month', m26)[['month','plate_apps','hrs','xbh','ba','obp','slg','woba','xwoba','krate','bbrate']].round(3)
    mo.to_csv(OUT/'dp_uc18_marsh_breakout_2026_monthly.csv', index=False)
    print("\n=== 2026 MONTHLY ===\n", mo.to_string(index=False))

    # 10 — two-strike battedball & discipline detail 2s
    ts = discipline('season', m[m.strikes==2])
    ts.to_csv(OUT/'dp_uc18_marsh_breakout_twostrike_discipline.csv', index=False)
    print("\n=== TWO-STRIKE DISCIPLINE ===\n", ts.to_string(index=False))

    # 11 — PA funnel: share of PA reaching two strikes + LHP exposure + games
    pa_end = m[~m.events.replace(np.nan, 'NA').isin(['NA', 'pickoff_1b'])]
    fun = pa_end.groupby('season').size().rename('pa').to_frame()
    fun = fun.join(m[m.strikes == 2].drop_duplicates(subset=['game_pk', 'at_bat_number'])
                   .groupby('season').size().rename('pa_2strike'))
    fun['pct_2strike'] = (fun.pa_2strike / fun.pa).round(3)
    fun['lhp_pa_share'] = pa_end.groupby('season').apply(
        lambda x: (x.p_throws == 'L').mean(), include_groups=False).round(3)
    fun = fun.join(m.groupby('season').game_pk.nunique().rename('games_appeared'))
    fun.reset_index().to_csv(OUT/'dp_uc18_marsh_breakout_pa_funnel.csv', index=False)
    print("\n=== PA FUNNEL / ROLE ===\n", fun.to_string())

    # 12 — per-600-PA pace
    res['hr_per_600'] = (res.hrs / res.plate_apps * 600).round(1)
    res['xbh_per_600'] = (res.xbh / res.plate_apps * 600).round(1)
    res[['season', 'plate_apps', 'hr_per_600', 'xbh_per_600']].to_csv(
        OUT/'dp_uc18_marsh_breakout_pace_per600.csv', index=False)
    print("\n=== PACE PER 600 PA ===\n",
          res[['season', 'plate_apps', 'hr_per_600', 'xbh_per_600']].to_string(index=False))

    # 13 — PA resolved within first two pitches (early-count damage)
    m['early'] = (m.balls + m.strikes) <= 1
    ec = get_stats('season', m[m.early])[['season', 'plate_apps', 'woba', 'hrs', 'xbh']].round(3)
    ec.to_csv(OUT/'dp_uc18_marsh_breakout_earlycount_pa.csv', index=False)
    print("\n=== PA ENDED WITHIN FIRST 2 PITCHES ===\n", ec.to_string(index=False))

    # 14 — 2025 by half (dates the shift: results moved 2H25, swing profile moved 2026)
    m25 = m[m.season == 2025].copy()
    m25['half'] = np.where(m25.game_date <= '2025-07-13', '2025-1H', '2025-2H')
    h_d = discipline('half', m25)
    h_r = get_stats('half', m25)[['half', 'plate_apps', 'hrs', 'xbh', 'ba', 'obp',
                                  'slg', 'woba', 'krate', 'bbrate']].round(3)
    h = h_r.merge(h_d, on='half')
    h.to_csv(OUT/'dp_uc18_marsh_breakout_2025_halves.csv', index=False)
    print("\n=== 2025 BY HALF ===\n", h.to_string(index=False))

    # DQ receipts
    dq = pd.DataFrame([{
        'rows_total': len(m),
        'dupe_pitch_keys': int(m.duplicated(subset=PITCH_KEY).sum()),
        'null_zone_rate': round(m.zone.isna().mean(),4),
        'null_launch_speed_bip': round(m[m.type=='X'].launch_speed.isna().mean(),4),
        'null_hc_bip': round(m[m.type=='X'].hc_x.isna().mean(),4),
        'null_xwoba_bip': round(m[m.type=='X'].estimated_woba_using_speedangle.isna().mean(),4),
        'woba_weight_nulls': int(m.wBB.isna().sum()),
        'min_pa_flag_2021': int(get_stats('season', m).set_index('season').loc[2021,'plate_apps']),
    }])
    dq.to_csv(OUT/'dp_uc18_marsh_breakout_dq_receipts.csv', index=False)
    print("\n=== DQ RECEIPTS ===\n", dq.to_string(index=False))

if __name__ == '__main__':
    main()
