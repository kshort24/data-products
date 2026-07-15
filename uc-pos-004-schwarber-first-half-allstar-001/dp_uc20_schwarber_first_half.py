"""
============================================================================
GOVERNED DATA PRODUCT — uc-pos-004-schwarber-first-half-allstar-001 (UC #21)
"Kyle Schwarber First-Half 2026: the approach behind the Derby runner-up"
============================================================================
Layer-3 BUILD artifact, Phillies Position-player (pos) value stream.
Pattern lineage: uc-pos-marsh-breakout-001 / dp_uc18 (hitter retrospective
shape, locked KPI kernel), uc-pps-017/018 (ASG first-half retrospective
framing), UC11 (evidence tiers, locked-KPI inheritance).

Locked KPI mechanics inherited VERBATIM from dp_uc18 / Baseball Functions:
  get_stats (ba, obp, slg, ops, woba, krate, bbrate), SWINGS/WHIFFS lists,
  discipline (swing/chase/z-swing/contact panel), batted_ball
  (barrel = launch_speed_angle==6, hard = launch_speed>=95), pulled_air,
  PITCH_GROUP. wOBA weights joined on game_year==Season.

NEW KPIs (specs in governance 03, provisional SC-1..SC-2):
  SC-1 wRC ("run creation"): wRAA = (wOBA - lgwOBA)/wOBAScale * PA;
       wRC = wRAA + lg(R/PA) * PA; wRC/600 pace. Constants: FanGraphs
       season rows in 'wOBA and FIP Constants.csv' (2026 row in-season).
  SC-2 P/PA (pitches_per_plate_app): pitches / plate_apps at season grain.

MEASURABLES (bat tracking, Statcast 2024+ only): bat_speed, swing_length,
  attack_angle, fast-swing rate (>=75 mph) on swings.

DATA WINDOW / FRESHNESS:
  * Entity lock: batter == 656941 (Kyle Schwarber), game_type == 'R'.
  * CHC/WSN/BOS era 2015-06-16 .. 2021-10-03: data/opponents/schwarber.parquet
  * PHI era 2022 .. 2026: data/phillies/phils_{2022..2026}.parquet
    (phillies_role == 'batting'). Cache fresh through 2026-07-12 =
    full 2026 first half (All-Star break).
  * Dedup on ['game_pk','at_bat_number','pitch_number'].
  * MANUAL CARRY-INS (not derivable from pitch log): 2026 All-Star
    selection; 2026 Home Run Derby runner-up (user-provided).
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
SCHWARBER = 656941
STEM = "dp_uc20_schwarber_first_half"

# ---------------------------------------------------------------- load ----
def load_schwarber() -> pd.DataFrame:
    frames = [pd.read_parquet(MLB / "data/opponents/schwarber.parquet")]
    for yr in range(2022, 2027):
        df = pd.read_parquet(MLB / f"data/phillies/phils_{yr}.parquet")
        frames.append(df[(df.phillies_role == "batting") & (df.batter == SCHWARBER)])
    m = pd.concat(frames, ignore_index=True)
    m = m[m.batter == SCHWARBER]
    m = m[m.game_type == "R"]
    m = m.drop_duplicates(subset=PITCH_KEY)
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
    """Pulled air-ball rate: spray angle from hc_x/hc_y (LHB pull = RF)."""
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

# --------------------------------------------------- NEW KPI: SC-1 wRC ----
def wrc(level, df, constants):
    """SC-1 run creation. wRAA=(wOBA-lgwOBA)/scale*PA; wRC=wRAA+lgR/PA*PA."""
    if isinstance(level, str): level = [level]
    r = get_stats(level, df)
    c = constants.rename(columns={'wOBA':'lg_woba', 'wOBAScale':'woba_scale', 'R/PA':'lg_r_pa'})
    key = 'season' if 'season' in level else level[0]
    r = r.merge(c[['Season','lg_woba','woba_scale','lg_r_pa']], left_on=key, right_on='Season', how='left')
    r['wraa'] = (r.woba - r.lg_woba) / r.woba_scale * r.plate_apps
    r['wrc'] = r.wraa + r.lg_r_pa * r.plate_apps
    r['wrc_600'] = r.wrc / r.plate_apps * 600
    return r[level + ['plate_apps','woba','lg_woba','wraa','wrc','wrc_600']].round(2)

# --------------------------------------------- NEW KPI: SC-2 P/PA ---------
def ppa(level, df):
    """SC-2 pitches per plate appearance at the given grain."""
    r = get_stats(level, df)
    r['p_pa'] = (r.pitches / r.plate_apps).round(3)
    lv = [level] if isinstance(level, str) else level
    return r[lv + ['pitches','plate_apps','p_pa']]

# ------------------------------------ measurables: bat tracking (2024+) ---
def bat_tracking(level, df):
    if isinstance(level, str): level = [level]
    d = df[df.bat_speed.notna()].copy()
    if d.empty:
        return pd.DataFrame()
    rows = d.groupby(level, as_index=False).apply(lambda x: pd.Series({
        'tracked_swings': len(x),
        'avg_bat_speed': x.bat_speed.mean(),
        'fast_swing_rate': (x.bat_speed >= 75).mean(),
        'avg_swing_length': x.swing_length.mean(),
        'avg_attack_angle': x.attack_angle.mean(),
    }), include_groups=False)
    return rows.round(3)

# ------------------------------------------------------------- figures ----
PHI_RED, PHI_NAVY, PHI_GRAY = '#E81828', '#002D72', '#8E9398'

def make_figures(res, disc, bb, pp):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    seasons = res.season.astype(str).str.replace('2026','2026-1H')

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(seasons, res.slg, color=PHI_GRAY, alpha=.45, label='SLG')
    ax.plot(seasons, res.woba, color=PHI_RED, marker='o', lw=2.5, label='wOBA')
    ax.plot(seasons, res.xwoba, color=PHI_NAVY, marker='s', ls='--', lw=1.8, label='xwOBA (BIP proxy)')
    ax.set_title('Kyle Schwarber — results by season', color=PHI_NAVY, weight='bold')
    ax.legend(frameon=False); ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig1_results.png', dpi=160); plt.close(fig)

    d = disc.copy(); ds = d.season.astype(str).str.replace('2026','2026-1H')
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(ds, d.swing_rate, color=PHI_NAVY, marker='o', lw=2, label='Swing%')
    ax.plot(ds, d.z_swing_rate, color=PHI_RED, marker='o', lw=2, label='In-zone swing%')
    ax.plot(ds, d.chase_rate, color=PHI_GRAY, marker='o', lw=2, label='Chase%')
    ax2 = ax.twinx()
    ax2.plot(ds, pp.p_pa, color='#B0B7BC', marker='D', ls=':', lw=1.6, label='P/PA (right)')
    ax2.set_ylabel('P/PA'); ax2.spines[['top']].set_visible(False)
    ax.set_title('Approach panel — swing decisions and pitches per PA', color=PHI_NAVY, weight='bold')
    h1,l1 = ax.get_legend_handles_labels(); h2,l2 = ax2.get_legend_handles_labels()
    ax.legend(h1+h2, l1+l2, frameon=False, ncol=2); ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig2_approach.png', dpi=160); plt.close(fig)

    bs = bb.season.astype(str).str.replace('2026','2026-1H')
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(bs, bb.hard_hit_rate, color=PHI_NAVY, alpha=.85, label='Hard-hit% (EV≥95)')
    ax.bar(bs, bb.barrel_rate, color=PHI_RED, label='Barrel%')
    ax.plot(bs, res.hr_600/100, color=PHI_GRAY, marker='o', lw=2, label='HR/600 (÷100)')
    ax.set_title('Damage engine — contact quality and HR pace', color=PHI_NAVY, weight='bold')
    ax.legend(frameon=False); ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig3_damage.png', dpi=160); plt.close(fig)

# ---------------------------------------------------------------- main ----
def main():
    m = load_schwarber()
    m['era'] = np.select(
        [m.game_year <= 2020, m.game_year == 2021],
        ['CHC', 'WSN/BOS'], default='PHI')
    m['season'] = m.game_year
    m['pitch_group'] = m.pitch_type.map(PITCH_GROUP).fillna('other')
    m['count_state'] = np.select(
        [m.strikes==2, m.balls > m.strikes], ['two_strike','ahead'], default='even_or_behind')
    constants = pd.read_csv(MLB / "wOBA and FIP Constants.csv")

    print(f"rows: {len(m)}  seasons: {sorted(m.season.unique())}")
    print(f"2026 window: {m[m.season==2026].game_date.min()} .. {m[m.season==2026].game_date.max()}")

    # 01 — results by season (user KPI list: HR, BA, OBP, SLG, OPS, wOBA)
    res = get_stats('season', m)
    res['hr_600'] = (res.hrs / res.plate_apps * 600).round(1)
    res_out = res[['season','pitches','plate_apps','hits','doubles','triples','hrs','xbh',
                   'walks','strikeouts','ba','obp','slg','ops','woba','xwoba','krate','bbrate','hr_600']].round(3)
    res_out.to_csv(OUT/f'{STEM}_results_by_season.csv', index=False)
    print("\n=== RESULTS BY SEASON ===\n", res_out.to_string(index=False))

    # 02 — SC-1 run creation (wRAA / wRC / wRC per 600)
    rc = wrc('season', m, constants)
    rc.to_csv(OUT/f'{STEM}_wrc_by_season.csv', index=False)
    print("\n=== RUN CREATION (SC-1) ===\n", rc.to_string(index=False))

    # 03 — SC-2 pitches per PA
    pp = ppa('season', m)
    pp.to_csv(OUT/f'{STEM}_ppa_by_season.csv', index=False)
    print("\n=== PITCHES PER PA (SC-2) ===\n", pp.to_string(index=False))

    # 04 — batted ball / contact quality (hard-hit, barrel per user list)
    bb = batted_ball('season', m)
    bb.to_csv(OUT/f'{STEM}_battedball_by_season.csv', index=False)
    print("\n=== BATTED BALL BY SEASON ===\n", bb.to_string(index=False))

    # 05 — discipline / approach panel
    disc = discipline('season', m)
    disc.to_csv(OUT/f'{STEM}_discipline_by_season.csv', index=False)
    print("\n=== DISCIPLINE BY SEASON ===\n", disc.to_string(index=False))

    # 06 — spray / pulled air
    pa_ = pulled_air(m, 'season')
    pa_.to_csv(OUT/f'{STEM}_spray_by_season.csv', index=False)
    print("\n=== SPRAY BY SEASON ===\n", pa_.to_string(index=False))

    # 07 — measurables: bat tracking (2024+)
    bt = bat_tracking('season', m)
    if not bt.empty:
        bt.to_csv(OUT/f'{STEM}_battracking_by_season.csv', index=False)
        print("\n=== BAT TRACKING (2024+) ===\n", bt.to_string(index=False))

    # 08 — platoon
    plat = get_stats(['season','p_throws'], m[m.season>=2022])
    plat = plat[['season','p_throws','plate_apps','hrs','ba','obp','slg','woba','xwoba','krate','bbrate']].round(3)
    plat.to_csv(OUT/f'{STEM}_platoon_by_season.csv', index=False)
    print("\n=== PLATOON (PHI era) ===\n", plat.to_string(index=False))

    # 09 — pitch-group splits
    pg = get_stats(['season','pitch_group'], m[m.season>=2023])
    pg = pg[['season','pitch_group','pitches','plate_apps','hrs','woba','xwoba','krate']].round(3)
    pg = pg.merge(discipline(['season','pitch_group'], m[m.season>=2023])[['season','pitch_group','whiff_rate','chase_rate']],
                  on=['season','pitch_group'])
    pg.to_csv(OUT/f'{STEM}_pitchgroup_by_season.csv', index=False)
    print("\n=== PITCH GROUP BY SEASON (23-26) ===\n", pg.to_string(index=False))

    # 10 — count leverage
    cs = get_stats(['season','count_state'], m[m.season>=2023])
    cs = cs[['season','count_state','pitches','plate_apps','hrs','woba','xwoba','krate','bbrate']].round(3)
    cs.to_csv(OUT/f'{STEM}_countstate_by_season.csv', index=False)
    print("\n=== COUNT STATE (23-26) ===\n", cs.to_string(index=False))

    # 11 — early count: first-pitch BIP quality + PA ended within 2 pitches
    fp = m[(m.balls==0)&(m.strikes==0)]
    fp_res = batted_ball('season', fp[fp.type=='X'])
    fp_res.to_csv(OUT/f'{STEM}_firstpitch_bip.csv', index=False)
    print("\n=== FIRST-PITCH BIP QUALITY ===\n", fp_res.to_string(index=False))
    m['early'] = (m.balls + m.strikes) <= 1
    ec = get_stats('season', m[m.early])[['season','plate_apps','woba','hrs','xbh']].round(3)
    ec.to_csv(OUT/f'{STEM}_earlycount_pa.csv', index=False)
    print("\n=== PA ENDED WITHIN FIRST 2 PITCHES ===\n", ec.to_string(index=False))

    # 12 — two-strike discipline
    ts = discipline('season', m[m.strikes==2])
    ts.to_csv(OUT/f'{STEM}_twostrike_discipline.csv', index=False)
    print("\n=== TWO-STRIKE DISCIPLINE ===\n", ts.to_string(index=False))

    # 13 — PA funnel / role
    pa_end = m[~m.events.replace(np.nan, 'NA').isin(['NA', 'pickoff_1b'])]
    fun = pa_end.groupby('season').size().rename('pa').to_frame()
    fun = fun.join(m[m.strikes == 2].drop_duplicates(subset=['game_pk', 'at_bat_number'])
                   .groupby('season').size().rename('pa_2strike'))
    fun['pct_2strike'] = (fun.pa_2strike / fun.pa).round(3)
    fun['lhp_pa_share'] = pa_end.groupby('season').apply(
        lambda x: (x.p_throws == 'L').mean(), include_groups=False).round(3)
    fun = fun.join(m.groupby('season').game_pk.nunique().rename('games_appeared'))
    fun.reset_index().to_csv(OUT/f'{STEM}_pa_funnel.csv', index=False)
    print("\n=== PA FUNNEL / ROLE ===\n", fun.to_string())

    # 14 — monthly 2026
    m26 = m[m.season==2026].copy()
    m26['month'] = m26.game_date.astype(str).str[:7]
    mo = get_stats('month', m26)[['month','plate_apps','hrs','xbh','ba','obp','slg','woba','xwoba','krate','bbrate']].round(3)
    mo.to_csv(OUT/f'{STEM}_2026_monthly.csv', index=False)
    print("\n=== 2026 MONTHLY ===\n", mo.to_string(index=False))

    # 15 — 2026 HR log (Derby-narrative measurables)
    hrs = m26[m26.events=='home_run'][['game_date','pitch_type','release_speed',
             'launch_speed','launch_angle','hit_distance_sc','p_throws','balls','strikes']].copy()
    hrs = hrs.sort_values('game_date')
    hrs.to_csv(OUT/f'{STEM}_2026_hr_log.csv', index=False)
    print(f"\n=== 2026 HR LOG (n={len(hrs)}) ===\n",
          hrs.describe()[['launch_speed','launch_angle','hit_distance_sc']].round(1).to_string())

    # figures
    make_figures(res_out.merge(res[['season','hr_600']], on=['season','hr_600']), disc, bb, pp)

    # DQ receipts
    dq = pd.DataFrame([{
        'rows_total': len(m),
        'dupe_pitch_keys': int(m.duplicated(subset=PITCH_KEY).sum()),
        'null_zone_rate': round(m.zone.isna().mean(),4),
        'null_launch_speed_bip': round(m[m.type=='X'].launch_speed.isna().mean(),4),
        'null_hc_bip': round(m[m.type=='X'].hc_x.isna().mean(),4),
        'null_xwoba_bip': round(m[m.type=='X'].estimated_woba_using_speedangle.isna().mean(),4),
        'woba_weight_nulls': int(m.wBB.isna().sum()),
        'bat_speed_coverage_2026': round(m[m.season==2026].bat_speed.notna().mean(),4),
        'max_game_date': str(m.game_date.max()),
    }])
    dq.to_csv(OUT/f'{STEM}_dq_receipts.csv', index=False)
    print("\n=== DQ RECEIPTS ===\n", dq.to_string(index=False))

if __name__ == '__main__':
    main()
             