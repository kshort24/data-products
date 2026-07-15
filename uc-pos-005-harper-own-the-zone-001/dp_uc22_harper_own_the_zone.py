"""
============================================================================
GOVERNED DATA PRODUCT — uc-pos-005-harper-own-the-zone-001 (UC #23)
"Bryce Harper First-Half 2026: Own the moment. Own the zone."
============================================================================
Layer-3 BUILD artifact, Phillies Position-player (pos) value stream.
Pattern lineage: uc-pos-004/dp_uc20 (Schwarber ASG retrospective shape),
uc-pos-marsh-breakout-001/dp_uc18 (locked pos hitter KPI kernel),
UC11 (locked-KPI inheritance discipline).

Locked KPI mechanics inherited VERBATIM from dp_uc18/dp_uc20:
  get_stats (ba, obp, slg, ops, woba, krate, bbrate), SWINGS/WHIFFS lists,
  discipline (swing/chase/z-swing/contact panel, zone<=9 Statcast in-zone),
  batted_ball (barrel = launch_speed_angle==6, hard = launch_speed>=95),
  PITCH_GROUP. wOBA weights joined on game_year==Season.

NEW KPIs (specs in governance 03, provisional OZ-1..OZ-4):
  Geometric attack regions, per-pitch sz_top/sz_bot, DPO ball_width=0.25 ft:
    in-zone geo : |plate_x| <= 0.83 and sz_bot <= plate_z <= sz_top
    shadow_in   : in zone, within 0.25 ft of any zone edge
    shadow_out  : out of zone, within 0.25 ft band around the zone
    heart       : in zone, not shadow_in;  waste: beyond the shadow band
  OZ-1 Shadow-Out Take Rate  = 1 - swing_rate on shadow_out pitches
  OZ-2 Shadow-In Attack Rate = swing_rate on shadow_in pitches
  OZ-3 Edge Decision Differential = OZ-2 - swing_rate(shadow_out)
  OZ-4 Shadow-In Damage = xwOBAcon / barrel% / hard-hit% on shadow_in BIP

DATA WINDOW / FRESHNESS:
  * Entity lock: batter == 547180 (Bryce Harper), game_type == 'R'.
  * PHI tenure only, 2019..2026: data/phillies/phils_{2019..2026}.parquet
    (phillies_role == 'batting'). Cache fresh through 2026-07-12 =
    full 2026 first half (All-Star break). 96 games, 408 PA.
  * Dedup on ['game_pk','at_bat_number','pitch_number'].
  * OZ family excludes rows with null plate_x/plate_z/sz (0.06% of pitches).
  * MANUAL CARRY-INS (not derivable from pitch log): 9th All-Star selection
    (commissioner add, not fan vote); Marsh fan-voted starter; Dombrowski
    offseason "elite" discourse; contract facts (13yr/$330M, 2019, no
    opt-outs, full NMC). Appear only in report narrative, never computed.
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
HARPER = 547180
STEM = "dp_uc22_harper_own_the_zone"
HALF_X, BALL = 0.83, 0.25

# ---------------------------------------------------------------- load ----
def load_harper() -> pd.DataFrame:
    frames = []
    for yr in range(2019, 2027):
        df = pd.read_parquet(MLB / f"data/phillies/phils_{yr}.parquet")
        frames.append(df[(df.phillies_role == "batting") & (df.batter == HARPER)])
    m = pd.concat(frames, ignore_index=True)
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
        'air_rate': x.air.mean(),
        'xwoba_con': x.estimated_woba_using_speedangle.mean(),
    }), include_groups=False)
    return rows.round(3)

PITCH_GROUP = {
    'FF':'fastball','SI':'fastball','FC':'fastball',
    'SL':'breaking','ST':'breaking','CU':'breaking','KC':'breaking','SV':'breaking','CS':'breaking',
    'CH':'offspeed','FS':'offspeed','FO':'offspeed','SC':'offspeed','KN':'offspeed',
}

# ----------------------------------- NEW: OZ attack-region geometry -------
def tag_regions(df: pd.DataFrame) -> pd.DataFrame:
    """OZ family geometry. Per-pitch sz_top/sz_bot; DPO ball_width = 0.25 ft.
    Excludes rows with null location (counted in DQ receipts)."""
    d = df[df.plate_x.notna() & df.plate_z.notna()
           & df.sz_top.notna() & df.sz_bot.notna()].copy()
    ax = d.plate_x.abs()
    in_zone = (ax <= HALF_X) & (d.plate_z >= d.sz_bot) & (d.plate_z <= d.sz_top)
    near_edge_in = ((HALF_X - ax) <= BALL) | ((d.plate_z - d.sz_bot) <= BALL) \
                   | ((d.sz_top - d.plate_z) <= BALL)
    in_band_out = (ax <= HALF_X + BALL) & (d.plate_z >= d.sz_bot - BALL) \
                  & (d.plate_z <= d.sz_top + BALL) & ~in_zone
    d['region'] = np.select(
        [in_zone & near_edge_in, in_zone, in_band_out],
        ['shadow_in', 'heart', 'shadow_out'], default='waste')
    d['swing'] = d.description.isin(SWINGS)
    d['whiff'] = d.description.isin(WHIFFS)
    return d

def region_profile(level, d):
    """Pitches / swing / whiff / damage by attack region at the given grain."""
    lv = [level] if isinstance(level, str) else list(level)
    rows = d.groupby(lv + ['region'], as_index=False).apply(lambda x: pd.Series({
        'pitches': len(x),
        'swing_rate': x.swing.mean(),
        'take_rate': 1 - x.swing.mean(),
        'whiff_rate': x[x.swing].whiff.mean() if x.swing.any() else np.nan,
    }), include_groups=False)
    bip = d[d.type=='X'].copy()
    bip['barrel'] = bip.launch_speed_angle == 6
    bip['hard'] = bip.launch_speed >= 95
    dmg = bip.groupby(lv + ['region'], as_index=False).apply(lambda x: pd.Series({
        'bip': len(x),
        'xwoba_con': x.estimated_woba_using_speedangle.mean(),
        'barrel_rate': x.barrel.mean(),
        'hard_hit_rate': x.hard.mean(),
        'avg_ev': x.launch_speed.mean(),
    }), include_groups=False)
    return rows.merge(dmg, on=lv + ['region'], how='left').round(3)

def oz_kpis(level, d):
    """OZ-1..OZ-4 at the given grain from tagged regions."""
    lv = [level] if isinstance(level, str) else list(level)
    def one(x):
        si, so = x[x.region=='shadow_in'], x[x.region=='shadow_out']
        si_bip = si[(si.type=='X') & si.swing]
        return pd.Series({
            'shadow_in_pitches': len(si), 'shadow_out_pitches': len(so),
            'oz1_shadow_out_take': 1 - so.swing.mean() if len(so) else np.nan,
            'oz2_shadow_in_attack': si.swing.mean() if len(si) else np.nan,
            'oz3_edge_decision_diff': (si.swing.mean() - so.swing.mean())
                                      if len(si) and len(so) else np.nan,
            'oz4_shadow_in_xwobacon': si_bip.estimated_woba_using_speedangle.mean(),
            'oz4_shadow_in_barrel': (si_bip.launch_speed_angle==6).mean() if len(si_bip) else np.nan,
            'oz4_shadow_in_hardhit': (si_bip.launch_speed>=95).mean() if len(si_bip) else np.nan,
            'oz4_shadow_in_bip': len(si_bip),
        })
    return d.groupby(lv, as_index=False).apply(one, include_groups=False).round(3)

# ------------------------------------------------------------- figures ----
PHI_RED, PHI_NAVY, PHI_GRAY = '#E81828', '#002D72', '#8C8C8C'

def make_figures(res, bb, oz, plat_bb):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    seasons = res.season.astype(str).str.replace('2026', '2026-1H')

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(seasons, res.slg, color=PHI_GRAY, alpha=.45, label='SLG')
    ax.plot(seasons, res.woba, color=PHI_RED, marker='o', lw=2.5, label='wOBA')
    ax.plot(seasons, res.xwoba, color=PHI_NAVY, marker='s', ls='--', lw=1.8, label='xwOBA (BIP proxy)')
    ax.set_title('Bryce Harper — results by season, PHI tenure', color=PHI_NAVY, weight='bold')
    ax.legend(frameon=False); ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig1_results.png', dpi=160); plt.close(fig)

    ozs = oz.season.astype(str).str.replace('2026', '2026-1H')
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(ozs, oz.oz1_shadow_out_take, color=PHI_NAVY, marker='o', lw=2.2, label='OZ-1 shadow-out take')
    ax.plot(ozs, oz.oz2_shadow_in_attack, color=PHI_RED, marker='o', lw=2.2, label='OZ-2 shadow-in attack')
    ax.plot(ozs, oz.oz3_edge_decision_diff, color=PHI_GRAY, marker='D', ls=':', lw=1.8, label='OZ-3 decision differential')
    ax.set_title('Owning the edge — take the ball, attack the strike', color=PHI_NAVY, weight='bold')
    ax.legend(frameon=False); ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig2_edge.png', dpi=160); plt.close(fig)

    bs = bb.season.astype(str).str.replace('2026', '2026-1H')
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(bs, bb.hard_hit_rate, color=PHI_NAVY, alpha=.85, label='Hard-hit% (EV>=95)')
    ax.bar(bs, bb.barrel_rate, color=PHI_RED, label='Barrel%')
    ax.plot(bs, bb.xwoba_con, color=PHI_GRAY, marker='o', lw=2, label='xwOBAcon')
    ax.set_title('Damage engine — is he still barreling it like ever?', color=PHI_NAVY, weight='bold')
    ax.legend(frameon=False); ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig3_damage.png', dpi=160); plt.close(fig)

    p = plat_bb.pivot(index='season', columns='p_throws', values='barrel_rate')
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(len(p.index)); w = 0.38
    ax.bar(x-w/2, p.get('L'), w, color=PHI_NAVY, label='vs LHP')
    ax.bar(x+w/2, p.get('R'), w, color=PHI_RED, label='vs RHP')
    ax.set_xticks(x); ax.set_xticklabels([str(s).replace('2026','2026-1H') for s in p.index])
    ax.set_title('Barrel% platoon splits by season', color=PHI_NAVY, weight='bold')
    ax.legend(frameon=False); ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig4_platoon.png', dpi=160); plt.close(fig)

# ---------------------------------------------------------------- main ----
def main():
    m = load_harper()
    m['season'] = m.game_year
    m['pitch_group'] = m.pitch_type.map(PITCH_GROUP).fillna('other')
    m['count_state'] = np.select(
        [m.strikes==2, m.balls > m.strikes], ['two_strike','ahead'], default='even_or_behind')

    print(f"rows: {len(m)}  seasons: {sorted(m.season.unique())}")
    print(f"2026 window: {m[m.season==2026].game_date.min()} .. {m[m.season==2026].game_date.max()}")

    # 01 — results by season (locked kernel)
    res = get_stats('season', m)
    res['hr_600'] = (res.hrs / res.plate_apps * 600).round(1)
    res_out = res[['season','pitches','plate_apps','hits','doubles','triples','hrs','xbh',
                   'walks','strikeouts','ba','obp','slg','ops','woba','xwoba','krate','bbrate','hr_600']].round(3)
    res_out.to_csv(OUT/f'{STEM}_results_by_season.csv', index=False)
    print("\n=== RESULTS BY SEASON (PHI tenure) ===\n", res_out.to_string(index=False))

    # 02 — locked discipline panel by season
    disc = discipline('season', m)
    disc.to_csv(OUT/f'{STEM}_discipline_by_season.csv', index=False)
    print("\n=== DISCIPLINE BY SEASON ===\n", disc.to_string(index=False))

    # 03 — batted ball / barrel trends by season (locked)
    bb = batted_ball('season', m)
    bb.to_csv(OUT/f'{STEM}_battedball_by_season.csv', index=False)
    print("\n=== BATTED BALL BY SEASON ===\n", bb.to_string(index=False))

    # 04 — barrel by pitch group x season (locked kernel at finer grain)
    bpg = batted_ball(['season','pitch_group'], m)
    bpg = bpg[bpg.pitch_group != 'other']
    bpg.to_csv(OUT/f'{STEM}_battedball_by_pitchgroup.csv', index=False)
    print("\n=== BARREL BY PITCH GROUP ===\n",
          bpg.pivot(index='season', columns='pitch_group', values='barrel_rate').round(3).to_string())

    # 05 — barrel by pitch type, 2026 vs prior (min 25 BIP career-window)
    bpt = batted_ball(['season','pitch_name'], m)
    bpt = bpt[bpt.bip >= 15]
    bpt.to_csv(OUT/f'{STEM}_battedball_by_pitchtype.csv', index=False)

    # 06 — platoon splits: results + damage
    plat = get_stats(['season','p_throws'], m)
    plat = plat[['season','p_throws','plate_apps','hrs','ba','obp','slg','ops','woba','xwoba','krate','bbrate']].round(3)
    plat.to_csv(OUT/f'{STEM}_platoon_results.csv', index=False)
    print("\n=== PLATOON RESULTS ===\n", plat.to_string(index=False))
    plat_bb = batted_ball(['season','p_throws'], m)
    plat_bb.to_csv(OUT/f'{STEM}_platoon_battedball.csv', index=False)
    print("\n=== PLATOON BATTED BALL ===\n", plat_bb.to_string(index=False))

    # ---- OZ family (NEW, provisional) ----
    t = tag_regions(m)
    loc_null = len(m) - len(t)

    # 07 — region profile by season
    rp = region_profile('season', t)
    rp.to_csv(OUT/f'{STEM}_region_profile_by_season.csv', index=False)
    print("\n=== REGION PROFILE BY SEASON ===\n", rp.to_string(index=False))

    # 08 — OZ KPIs by season
    oz = oz_kpis('season', t)
    oz.to_csv(OUT/f'{STEM}_oz_kpis_by_season.csv', index=False)
    print("\n=== OZ KPIs BY SEASON ===\n", oz.to_string(index=False))

    # 09 — OZ 2026 splits: platoon, pitch group, count state
    for dim, name in [('p_throws','platoon'), ('pitch_group','pitchgroup'), ('count_state','countstate')]:
        z = oz_kpis(dim, t[t.season==2026])
        z.to_csv(OUT/f'{STEM}_oz_2026_by_{name}.csv', index=False)
        print(f"\n=== OZ 2026 BY {name.upper()} ===\n", z.to_string(index=False))

    # 10 — 2026 shadow-band pitch log (consumable for interactive scatter)
    band = t[(t.season==2026) & t.region.isin(['shadow_in','shadow_out'])].copy()
    band['outcome'] = np.select(
        [band.events.isin(['home_run','double','triple']),
         band.events=='single',
         band.swing],
        ['xbh','single','swing_other'], default='take')
    cols = ['game_date','p_throws','pitch_type','pitch_name','plate_x','plate_z',
            'sz_top','sz_bot','region','swing','outcome','description','events',
            'launch_speed','launch_angle','estimated_woba_using_speedangle',
            'balls','strikes','zone','release_speed']
    band[cols].to_csv(OUT/f'{STEM}_2026_shadow_band_pitchlog.csv', index=False)
    print(f"\n2026 shadow-band pitches: {len(band)} "
          f"(in {int((band.region=='shadow_in').sum())} / out {int((band.region=='shadow_out').sum())})")

    # 11 — 2026 punished-pitch log: shadow_in + heart BIP with damage
    pun = t[(t.season==2026) & (t.type=='X') & t.region.isin(['shadow_in','heart'])].copy()
    pun['barrel'] = pun.launch_speed_angle == 6
    pun = pun[pun.events.isin(['home_run','double','triple','single']) | pun.barrel]
    pun_cols = [c for c in cols if c not in ('outcome','swing')]
    pun[pun_cols].assign(barrel=pun.barrel).to_csv(
        OUT/f'{STEM}_2026_punished_log.csv', index=False)
    print(f"2026 punished pitches (hits or barrels, heart+shadow_in): {len(pun)}")

    # 12 — monthly 2026
    m26 = m[m.season==2026].copy()
    m26['month'] = m26.game_date.astype(str).str[:7]
    mo = get_stats('month', m26)[['month','plate_apps','hrs','xbh','ba','obp','slg','woba','xwoba','krate','bbrate']].round(3)
    mo.to_csv(OUT/f'{STEM}_2026_monthly.csv', index=False)
    print("\n=== 2026 MONTHLY ===\n", mo.to_string(index=False))

    # figures
    make_figures(res_out, bb, oz, plat_bb)

    # DQ receipts
    zone_cross = t.copy()
    zone_cross['zone_says_in'] = zone_cross.zone <= 9
    zone_cross['geo_says_in'] = zone_cross.region.isin(['heart','shadow_in'])
    dq = pd.DataFrame([{
        'rows_total': len(m),
        'dupe_pitch_keys': int(m.duplicated(subset=PITCH_KEY).sum()),
        'entity_ids': str(sorted(m.batter.unique())),
        'game_types': str(sorted(m.game_type.unique())),
        'null_location_rows_excluded_oz': loc_null,
        'null_zone_rate': round(m.zone.isna().mean(), 4),
        'null_launch_speed_bip': round(m[m.type=='X'].launch_speed.isna().mean(), 4),
        'null_xwoba_bip': round(m[m.type=='X'].estimated_woba_using_speedangle.isna().mean(), 4),
        'woba_weight_nulls': int(m.wBB.isna().sum()),
        'zone_vs_geo_agreement': round((zone_cross.zone_says_in == zone_cross.geo_says_in).mean(), 4),
        'max_game_date': str(m.game_date.max()),
    }])
    dq.to_csv(OUT/f'{STEM}_dq_receipts.csv', index=False)
    print("\n=== DQ RECEIPTS ===\n", dq.to_string(index=False))

if __name__ == '__main__':
    main()
