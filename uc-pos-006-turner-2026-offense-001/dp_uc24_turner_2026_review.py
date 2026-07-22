"""
============================================================================
GOVERNED DATA PRODUCT — uc-pos-006-turner-2026-offense-001 (UC #25)
"Trea Turner 2026: the down year, and the July that argues with it"
============================================================================
Layer-3 BUILD artifact, Phillies Position-player (pos) value stream.
Pattern lineage: uc-pos-004 / dp_uc20 (Schwarber first-half hitter retrospective
shape, locked KPI kernel), uc-pos-marsh-breakout-001 / dp_uc18 (hitter
retrospective + persona narrative), uc-pos-005 / dp_uc22 (interactive.html
consumable), UC11 (evidence tiers, locked-KPI inheritance).

Locked KPI mechanics inherited VERBATIM from dp_uc20 / Baseball Functions:
  get_stats (ba, obp, slg, ops, woba, krate, bbrate, iso), SWINGS/WHIFFS,
  discipline (swing/chase/z-swing/contact panel), batted_ball
  (barrel = launch_speed_angle==6, hard = launch_speed>=95, ld/air/sweet),
  pulled_air (pulled-air rate via hc_x/hc_y spray angle), PITCH_GROUP,
  wrc (SC-1), ppa (SC-2), bat_tracking. wOBA weights on game_year==Season.

NEW KPIs this UC (specs in governance 03, provisional RF-1..RF-2):
  RF-1 Season-to-date OPS trajectory: cumulative OBP + cumulative SLG by
       game index within season. Hero visual (2026 vs prior-year shadows).
  RF-2 Rolling-form wOBA: trailing 100-PA rolling wOBA, 2026 only, to
       quantify the "heating up" claim as a process line, not a month bucket.

MEASURABLES (bat tracking, Statcast 2024+ only): bat_speed, swing_length,
  attack_angle, fast-swing rate (>=75 mph) on swings.

DATA WINDOW / FRESHNESS:
  * Entity lock: batter == 607208 (Trea Turner), game_type == 'R'.
  * WSN/LAD era 2015 .. 2022: data/opponents/turner.parquet
  * PHI era 2023 .. 2026: data/phillies/phils_{2023..2026}.parquet
    (phillies_role == 'batting'). Cache fresh through 2026-07-20 =
    2026 first half + first 3 games of the second half (post All-Star break).
  * Dedup on ['game_pk','at_bat_number','pitch_number'].
  * MANUAL CARRY-INS (not derivable from the pitch log): 2026 All-Star
    break date (2026-07-16); club/roster context (user-provided).
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
TREA = 607208
STEM = "dp_uc24_turner_2026_review"
ASB_2026 = "2026-07-16"          # manual carry-in: All-Star break date

# ---------------------------------------------------------------- load ----
def load_turner() -> pd.DataFrame:
    frames = [pd.read_parquet(MLB / "data/opponents/turner.parquet")]
    for yr in range(2023, 2027):
        df = pd.read_parquet(MLB / f"data/phillies/phils_{yr}.parquet")
        frames.append(df[(df.phillies_role == "batting") & (df.batter == TREA)])
    m = pd.concat(frames, ignore_index=True)
    m = m[m.batter == TREA]
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
    """Pulled air-ball rate: spray angle from hc_x/hc_y (RHB pull = LF, spray<0)."""
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

# --------------------------------------------------- inherited SC-1 wRC ----
def wrc(level, df, constants):
    if isinstance(level, str): level = [level]
    r = get_stats(level, df)
    c = constants.rename(columns={'wOBA':'lg_woba', 'wOBAScale':'woba_scale', 'R/PA':'lg_r_pa'})
    key = level[0]
    r = r.merge(c[['Season','lg_woba','woba_scale','lg_r_pa']], left_on=key, right_on='Season', how='left')
    r['wraa'] = (r.woba - r.lg_woba) / r.woba_scale * r.plate_apps
    r['wrc'] = r.wraa + r.lg_r_pa * r.plate_apps
    r['wrc_600'] = r.wrc / r.plate_apps * 600
    return r[level + ['plate_apps','woba','lg_woba','wraa','wrc','wrc_600']].round(2)

# --------------------------------------------- inherited SC-2 P/PA ---------
def ppa(level, df):
    r = get_stats(level, df)
    r['p_pa'] = (r.pitches / r.plate_apps).round(3)
    lv = [level] if isinstance(level, str) else level
    return r[lv + ['pitches','plate_apps','p_pa']]

# ------------------------------------ measurables: bat tracking (2024+) ---
def bat_tracking(level, df):
    if isinstance(level, str): level = [level]
    if 'bat_speed' not in df.columns:
        return pd.DataFrame()
    d = df[df.bat_speed.notna()].copy()
    if d.empty:
        return pd.DataFrame()
    rows = d.groupby(level, as_index=False).apply(lambda x: pd.Series({
        'tracked_swings': len(x),
        'avg_bat_speed': x.bat_speed.mean(),
        'fast_swing_rate': (x.bat_speed >= 75).mean(),
        'avg_swing_length': x.swing_length.mean(),
        'avg_attack_angle': x.attack_angle.mean() if 'attack_angle' in x else np.nan,
    }), include_groups=False)
    return rows.round(3)

# ---------------------------- NEW KPI RF-1: season-to-date OPS trajectory --
def running_line(df):
    """Cumulative OBP/SLG/OPS and wOBA-to-date by game index, per season.
    RF-1 hero data. One row per (season, game_date)."""
    d = df[df.game_type=='R'].copy()
    pa = d[~d.events.replace(np.nan,'NA').isin(['NA','pickoff_1b'])]
    ab = pa[~pa.events.isin(['walk','intent_walk','hit_by_pitch','sac_fly','sac_bunt'])]
    # per-row wOBA numerator = the season weight matching THAT row's event
    wmap = {'walk':'wBB','hit_by_pitch':'wHBP','single':'w1B','double':'w2B','triple':'w3B','home_run':'wHR'}
    d['woba_num'] = 0.0
    for ev, wc in wmap.items():
        if wc in d.columns:
            mm = d.events == ev
            d.loc[mm, 'woba_num'] = d.loc[mm, wc]
    def cnt(sub, name):
        return sub.groupby(['game_year','game_date']).size().rename(name)
    g = pd.DataFrame(cnt(pa,'PA'))
    for name, sub in [('AB',ab), ('H',d[d.events.isin(['single','double','triple','home_run'])]),
                      ('x1',d[d.events=='single']), ('x2',d[d.events=='double']),
                      ('x3',d[d.events=='triple']), ('HR',d[d.events=='home_run']),
                      ('BB',d[d.events=='walk']), ('HBP',d[d.events=='hit_by_pitch'])]:
        g = g.join(cnt(sub, name), how='left')
    g = g.join(d.groupby(['game_year','game_date'])['woba_num'].sum().rename('WN'), how='left')
    g = g.fillna(0).reset_index().sort_values(['game_year','game_date'])
    cum_cols = ['PA','AB','H','x1','x2','x3','HR','BB','HBP','WN']
    for c in cum_cols:
        g[c+'_c'] = g.groupby('game_year')[c].cumsum()
    g['gi'] = g.groupby('game_year').cumcount() + 1
    g['obp_std'] = (g.H_c + g.BB_c + g.HBP_c) / g.PA_c
    g['slg_std'] = (g.x1_c + 2*g.x2_c + 3*g.x3_c + 4*g.HR_c) / g.AB_c
    g['ops_std'] = g.obp_std + g.slg_std
    g['woba_std'] = g.WN_c / g.PA_c
    return g[['game_year','game_date','gi','PA_c','ops_std','obp_std','slg_std','woba_std','HR_c']].round(4)

# ------------------------ NEW KPI RF-2: rolling-form wOBA (2026 only) ------
def rolling_form(df, window_pa=100):
    """Trailing window_pa rolling wOBA + OPS across the season, PA-indexed.
    Quantifies 'heating up' as a smoothed process line."""
    d = df[df.game_type=='R'].copy().sort_values(['game_date','at_bat_number','pitch_number'])
    pa = d[~d.events.replace(np.nan,'NA').isin(['NA','pickoff_1b'])].copy()
    pa['is_ab'] = ~pa.events.isin(['walk','intent_walk','hit_by_pitch','sac_fly','sac_bunt'])
    pa['H'] = pa.events.isin(['single','double','triple','home_run']).astype(int)
    pa['TB'] = pa.events.map({'single':1,'double':2,'triple':3,'home_run':4}).fillna(0)
    pa['BB'] = (pa.events=='walk').astype(int)
    pa['HBP'] = (pa.events=='hit_by_pitch').astype(int)
    wmap = {'walk':'wBB','hit_by_pitch':'wHBP','single':'w1B','double':'w2B','triple':'w3B','home_run':'wHR'}
    pa['wnum'] = 0.0
    for ev, wc in wmap.items():
        if wc in pa.columns:
            mm = pa.events == ev
            pa.loc[mm, 'wnum'] = pa.loc[mm, wc]
    pa = pa.reset_index(drop=True)
    pa['pa_idx'] = np.arange(1, len(pa)+1)
    r = pd.DataFrame({'pa_idx': pa.pa_idx, 'game_date': pa.game_date})
    roll = lambda s: s.rolling(window_pa, min_periods=window_pa).sum()
    ab_c = roll(pa.is_ab.astype(int)); h_c = roll(pa.H); tb_c = roll(pa.TB)
    bb_c = roll(pa.BB); hbp_c = roll(pa.HBP); wn_c = roll(pa.wnum)
    r['roll_obp'] = (h_c + bb_c + hbp_c) / window_pa
    r['roll_slg'] = tb_c / ab_c
    r['roll_ops'] = r.roll_obp + r.roll_slg
    r['roll_woba'] = wn_c / window_pa
    return r.dropna().round(4)

# ------------------------------------------------------------- figures ----
PHI_RED, PHI_NAVY, PHI_GRAY, PHI_LGRAY = '#E81828', '#002D72', '#8C8C8C', '#D9D9D9'

def make_figures(res, bb, disc, run, mo26, roll26):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # fig1 — career results by season (OPS bars, wOBA + xwOBA lines)
    r = res[res.plate_apps >= 50].copy()
    seasons = r.season.astype(str)
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    ax.bar(seasons, r.ops, color=PHI_LGRAY, label='OPS')
    ax.plot(seasons, r.woba, color=PHI_RED, marker='o', lw=2.5, label='wOBA')
    ax.plot(seasons, r.xwoba, color=PHI_NAVY, marker='s', ls='--', lw=1.8, label='xwOBA (BIP proxy)')
    for x, v in zip(seasons, r.ops):
        ax.text(x, v+0.008, f'{v:.3f}', ha='center', va='bottom', fontsize=7.5, color=PHI_NAVY)
    ax.axvspan(len(seasons)-1.5, len(seasons)-0.5, color=PHI_RED, alpha=0.06)
    ax.set_title('Trea Turner — results by season (WSN → LAD → PHI)', color=PHI_NAVY, weight='bold')
    ax.set_ylabel('OPS / wOBA'); ax.legend(frameon=False, ncol=3, loc='lower left')
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig1_results.png', dpi=160); plt.close(fig)

    # fig2 — HERO: season-to-date OPS trajectory, PHI era, 2026 highlighted
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    shadow = {2023: '#B9C0CC', 2024: '#8C8C8C', 2025: '#4A5568'}
    for yr, col in shadow.items():
        s = run[run.game_year == yr]
        if len(s):
            ax.plot(s.gi, s.ops_std, color=col, lw=1.6, alpha=0.9, label=f'{yr} (.{int(round(s.ops_std.iloc[-1]*1000)):03d} final)')
            ax.text(s.gi.iloc[-1]+0.6, s.ops_std.iloc[-1], str(yr), color=col, fontsize=8, va='center')
    s26 = run[run.game_year == 2026]
    ax.plot(s26.gi, s26.ops_std, color=PHI_RED, lw=3.2, label=f'2026 (.{int(round(s26.ops_std.iloc[-1]*1000)):03d} to date)', zorder=5)
    ax.scatter(s26.gi.iloc[-1], s26.ops_std.iloc[-1], color=PHI_RED, s=45, zorder=6)
    # ASB marker on 2026 line
    asb_gi = s26[pd.to_datetime(s26.game_date) <= ASB_2026].gi.max()
    if pd.notna(asb_gi):
        ax.axvline(asb_gi, color=PHI_NAVY, ls=':', lw=1.2, alpha=0.7)
        ax.text(asb_gi, ax.get_ylim()[1], ' All-Star break', color=PHI_NAVY, fontsize=8, va='top')
    ax.set_title("Season-to-date OPS by game — 2026 vs prior Phillies years (RF-1)", color=PHI_NAVY, weight='bold')
    ax.set_xlabel('Team game number (season to date)'); ax.set_ylabel('Cumulative OPS')
    ax.legend(frameon=False, loc='upper right', fontsize=8.5)
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y', color=PHI_LGRAY, alpha=0.5)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig2_trajectory.png', dpi=160); plt.close(fig)

    # fig3 — damage engine: hard-hit%, barrel%, ISO by season (PHI era)
    b = bb.merge(res[['season','iso']], on='season').sort_values('season')
    b = b[b.season >= 2023]
    bs = b.season.astype(str)
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    x = np.arange(len(bs)); w = 0.38
    ax.bar(x - w/2, b.hard_hit_rate, w, color=PHI_NAVY, alpha=.85, label='Hard-hit% (EV≥95)')
    ax.bar(x + w/2, b.barrel_rate, w, color=PHI_RED, label='Barrel%')
    ax2 = ax.twinx()
    ax2.plot(x, b.iso, color='#C0870A', marker='D', lw=2, label='ISO (right)')
    ax2.set_ylabel('ISO')
    ax.set_xticks(x); ax.set_xticklabels(bs)
    ax.set_title('Damage engine — contact quality & isolated power (PHI era)', color=PHI_NAVY, weight='bold')
    ax.set_ylabel('Rate'); ax.spines[['top']].set_visible(False); ax2.spines[['top']].set_visible(False)
    h1,l1 = ax.get_legend_handles_labels(); h2,l2 = ax2.get_legend_handles_labels()
    ax.legend(h1+h2, l1+l2, frameon=False, ncol=3, loc='upper center')
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig3_engine.png', dpi=160); plt.close(fig)

    # fig4 — approach: chase, whiff, K% by season (PHI era)
    d = disc.merge(res[['season','krate']], on='season').sort_values('season')
    d = d[d.season >= 2023]; ds = d.season.astype(str)
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    ax.plot(ds, d.chase_rate, color=PHI_NAVY, marker='o', lw=2, label='Chase%')
    ax.plot(ds, d.whiff_rate, color=PHI_RED, marker='o', lw=2, label='Whiff%')
    ax.plot(ds, d.krate, color=PHI_GRAY, marker='s', ls='--', lw=2, label='K%')
    ax.set_title('Approach panel — chase, whiff, strikeout (PHI era)', color=PHI_NAVY, weight='bold')
    ax.set_ylabel('Rate'); ax.legend(frameon=False, ncol=3)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig4_approach.png', dpi=160); plt.close(fig)

    # fig5 — 2026 monthly OPS with July highlight + rolling-form wOBA inset line
    mo = mo26.copy()
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    colors = [PHI_RED if str(mm).endswith('07') else PHI_LGRAY for mm in mo.month]
    ax.bar(mo.month, mo.ops, color=colors)
    for xm, v, pa in zip(mo.month, mo.ops, mo.plate_apps):
        ax.text(xm, v+0.01, f'{v:.3f}\n{int(pa)} PA', ha='center', va='bottom', fontsize=7.5, color=PHI_NAVY)
    ax.set_title('2026 by month — the July surge (red), sample noted', color=PHI_NAVY, weight='bold')
    ax.set_ylabel('OPS'); ax.spines[['top','right']].set_visible(False)
    ax.set_ylim(0, max(mo.ops)*1.25)
    fig.tight_layout(); fig.savefig(OUT/f'{STEM}_fig5_monthly.png', dpi=160); plt.close(fig)

# ---------------------------------------------------------------- main ----
def main():
    m = load_turner()
    # team-per-row (robust to the 2021 midseason trade): batting team by half-inning
    m['bat_team'] = np.where(m.inning_topbot == 'Top', m.away_team, m.home_team)
    m['era'] = m.bat_team.map({'WSH':'WSN','LAD':'LAD','PHI':'PHI'}).fillna(m.bat_team)
    m['season'] = m.game_year
    m['pitch_group'] = m.pitch_type.map(PITCH_GROUP).fillna('other')
    m['count_state'] = np.select(
        [m.strikes==2, m.balls > m.strikes], ['two_strike','ahead'], default='even_or_behind')
    constants = pd.read_csv(MLB / "wOBA and FIP Constants.csv")

    print(f"rows: {len(m)}  seasons: {sorted(m.season.unique())}")
    print(f"eras: {m.groupby('season').era.agg(lambda x: x.mode().iat[0]).to_dict()}")
    print(f"2026 window: {m[m.season==2026].game_date.min()} .. {m[m.season==2026].game_date.max()}")

    # 01 — results by season (career; user KPI list: HR, BA, OBP, SLG, OPS, wOBA)
    res = get_stats('season', m)
    res = res.merge(m.groupby('season').era.agg(lambda x: x.mode().iat[0]).rename('era'), on='season', how='left')
    res['hr_600'] = (res.hrs / res.plate_apps * 600).round(1)
    res_out = res[['season','era','pitches','plate_apps','at_bats','hits','doubles','triples','hrs','xbh',
                   'walks','strikeouts','ba','obp','slg','ops','iso','woba','xwoba','krate','bbrate','hr_600']].round(3)
    res_out.to_csv(OUT/f'{STEM}_results_by_season.csv', index=False)
    print("\n=== RESULTS BY SEASON ===\n", res_out.to_string(index=False))

    # 02 — SC-1 run creation
    rc = wrc('season', m, constants)
    rc.to_csv(OUT/f'{STEM}_wrc_by_season.csv', index=False)
    print("\n=== RUN CREATION (SC-1) ===\n", rc.to_string(index=False))

    # 03 — SC-2 pitches per PA
    pp = ppa('season', m)
    pp.to_csv(OUT/f'{STEM}_ppa_by_season.csv', index=False)

    # 04 — batted ball / contact quality (user list: barrel, hard-hit, LD, + EV/LA/air/sweet)
    bb = batted_ball('season', m)
    bb.to_csv(OUT/f'{STEM}_battedball_by_season.csv', index=False)
    print("\n=== BATTED BALL BY SEASON ===\n", bb[['season','bip','avg_ev','ev90','avg_la','barrel_rate','hard_hit_rate','ld_rate','air_rate','sweet_spot_rate','gb_rate','xwoba_con']].to_string(index=False))

    # 05 — discipline / approach panel
    disc = discipline('season', m)
    disc.to_csv(OUT/f'{STEM}_discipline_by_season.csv', index=False)
    print("\n=== DISCIPLINE BY SEASON ===\n", disc.to_string(index=False))

    # 06 — spray / pulled air (user: pull air rate)
    pa_ = pulled_air(m, 'season')
    pa_.to_csv(OUT/f'{STEM}_spray_by_season.csv', index=False)
    print("\n=== SPRAY / PULLED-AIR BY SEASON ===\n", pa_.to_string(index=False))

    # 07 — measurables: bat tracking (2024+)
    bt = bat_tracking('season', m)
    if not bt.empty:
        bt.to_csv(OUT/f'{STEM}_battracking_by_season.csv', index=False)
        print("\n=== BAT TRACKING (2024+) ===\n", bt.to_string(index=False))

    # 08 — platoon (PHI era)
    plat = get_stats(['season','p_throws'], m[m.season>=2023])
    plat = plat[['season','p_throws','plate_apps','hrs','ba','obp','slg','ops','woba','xwoba','krate','bbrate']].round(3)
    plat.to_csv(OUT/f'{STEM}_platoon_by_season.csv', index=False)
    print("\n=== PLATOON (PHI era) ===\n", plat.to_string(index=False))

    # 09 — pitch-group splits (PHI era)
    pg = get_stats(['season','pitch_group'], m[m.season>=2023])
    pg = pg[['season','pitch_group','pitches','plate_apps','hrs','woba','xwoba','krate']].round(3)
    pg = pg.merge(discipline(['season','pitch_group'], m[m.season>=2023])[['season','pitch_group','whiff_rate','chase_rate']],
                  on=['season','pitch_group'])
    pg.to_csv(OUT/f'{STEM}_pitchgroup_by_season.csv', index=False)
    print("\n=== PITCH GROUP BY SEASON (23-26) ===\n", pg.to_string(index=False))

    # 10 — count leverage (PHI era)
    cs = get_stats(['season','count_state'], m[m.season>=2023])
    cs = cs[['season','count_state','pitches','plate_apps','hrs','woba','xwoba','krate','bbrate']].round(3)
    cs.to_csv(OUT/f'{STEM}_countstate_by_season.csv', index=False)

    # 11 — 2026 monthly (the "heating up" story)
    m26 = m[m.season==2026].copy()
    m26['month'] = m26.game_date.astype(str).str[:7]
    mo = get_stats('month', m26)[['month','plate_apps','hrs','xbh','ba','obp','slg','ops','iso','woba','xwoba','krate','bbrate']].round(3)
    mob = batted_ball('month', m26)[['month','barrel_rate','hard_hit_rate','ld_rate','air_rate','avg_ev']]
    mop = pulled_air(m26, 'month')[['month','pulled_air_rate','pull_rate']]
    mo = mo.merge(mob, on='month', how='left').merge(mop, on='month', how='left')
    mo.to_csv(OUT/f'{STEM}_2026_monthly.csv', index=False)
    print("\n=== 2026 MONTHLY ===\n", mo.to_string(index=False))

    # 12 — RF-1 season-to-date OPS trajectory (hero data), all seasons
    run = running_line(m)
    run.to_csv(OUT/f'{STEM}_running_ops_by_game.csv', index=False)
    print("\n=== RF-1 TRAJECTORY (final points per PHI season) ===")
    print(run[run.game_year>=2023].groupby('game_year').tail(1)[['game_year','gi','PA_c','ops_std','woba_std','HR_c']].to_string(index=False))

    # 13 — RF-2 rolling-form wOBA/OPS (2026)
    roll26 = rolling_form(m26, window_pa=100)
    roll26.to_csv(OUT/f'{STEM}_2026_rolling_form.csv', index=False)
    if len(roll26):
        print(f"\n=== RF-2 ROLLING FORM 2026 (100-PA) === n={len(roll26)} "
              f"min_ops={roll26.roll_ops.min():.3f} last_ops={roll26.roll_ops.iloc[-1]:.3f} "
              f"min_woba={roll26.roll_woba.min():.3f} last_woba={roll26.roll_woba.iloc[-1]:.3f}")

    # 14 — pre/post All-Star break 2026 split
    m26['half'] = np.where(pd.to_datetime(m26.game_date) <= ASB_2026, '1H (pre-ASB)', '2H (post-ASB)')
    half = get_stats('half', m26)[['half','plate_apps','hrs','ba','obp','slg','ops','woba','xwoba','krate','bbrate']].round(3)
    half.to_csv(OUT/f'{STEM}_2026_half_split.csv', index=False)
    print("\n=== 2026 PRE/POST ASB ===\n", half.to_string(index=False))

    # 15 — 2026 HR log
    hrs = m26[m26.events=='home_run'][['game_date','pitch_type','release_speed',
             'launch_speed','launch_angle','hit_distance_sc','p_throws','balls','strikes']].copy().sort_values('game_date')
    hrs.to_csv(OUT/f'{STEM}_2026_hr_log.csv', index=False)

    # figures
    make_figures(res_out, bb, disc, run, mo, roll26)

    # DQ receipts
    bip_all = m[m.type=='X']
    dq = pd.DataFrame([{
        'rows_total': len(m),
        'dupe_pitch_keys': int(m.duplicated(subset=PITCH_KEY).sum()),
        'entity_ids': m.batter.nunique(),
        'seasons': f"{int(m.season.min())}-{int(m.season.max())}",
        'null_zone_rate': round(m.zone.isna().mean(),4),
        'null_launch_speed_bip': round(bip_all.launch_speed.isna().mean(),4),
        'null_hc_bip': round(bip_all.hc_x.isna().mean(),4),
        'null_xwoba_bip': round(bip_all.estimated_woba_using_speedangle.isna().mean(),4),
        'woba_weight_nulls': int(m.wBB.isna().sum()),
        'bat_speed_cov_2024': round(m[m.season==2024].bat_speed.notna().mean(),4) if 'bat_speed' in m else None,
        'bat_speed_cov_2026': round(m[m.season==2026].bat_speed.notna().mean(),4) if 'bat_speed' in m else None,
        'max_game_date': str(m.game_date.max()),
        'games_2026': int(m[m.season==2026].game_pk.nunique()),
        'post_asb_games_2026': int(m26[m26.half=='2H (post-ASB)'].game_pk.nunique()),
    }])
    dq.to_csv(OUT/f'{STEM}_dq_receipts.csv', index=False)
    print("\n=== DQ RECEIPTS ===\n", dq.T.to_string())

if __name__ == '__main__':
    main()
