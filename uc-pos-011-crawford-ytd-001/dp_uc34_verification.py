"""
dp_uc34_verification.py — independent verification for uc-pos-011.

Recomputes every headline by a DIFFERENT path from the build kernel:
  * parquet files read in REVERSE year order
  * subject filtered BEFORE the batting-role tag is applied
  * every mask declared inline from raw columns — no shared constants
  * NO import of dp_uc34_kernel

Any disagreement with the published receipts is a FAIL.
"""
from __future__ import annotations
import json, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
# Data plane root. Defaults to the MLB repo on the DPO's machine; override with
# the DP_UC34_DATA environment variable (the build sandbox sets it to a staged copy).
DATA = os.environ.get(
    'DP_UC34_DATA',
    r'C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB')
P, F = 0, 0
FAILS = []


def chk(label, got, want, tol=5e-4):
    global P, F
    if isinstance(want, (str, bool, list, tuple)) or isinstance(got, (str, bool, list, tuple)):
        ok = got == want
    elif isinstance(want, (int, np.integer)) and isinstance(got, (int, np.integer)):
        ok = int(got) == int(want)
    elif want is None or (isinstance(want, float) and np.isnan(want)):
        ok = got is None or (isinstance(got, float) and np.isnan(got))
    else:
        ok = abs(float(got) - float(want)) <= tol
    if ok:
        P += 1
    else:
        F += 1; FAILS.append(f'{label}: got {got!r} want {want!r}')
    print(f"  {'PASS' if ok else 'FAIL'}  {label:<58} {got!r} vs {want!r}")


def main():
    H = json.load(open(f'{HERE}/dp_uc34_headlines.json'))

    # ── independent load: reverse order, subject-first ────────────────────
    fr = []
    for y in range(2026, 2014, -1):
        p = f'{DATA}/data/phillies/phils_{y}.parquet'
        if os.path.exists(p):
            fr.append(pd.read_parquet(p))
    raw = pd.concat(fr, ignore_index=True)
    jc = raw[raw.batter == 702222].copy()
    jc = jc[(((jc.home_team == 'PHI') & (jc.inning_topbot == 'Bot'))
             | ((jc.away_team == 'PHI') & (jc.inning_topbot == 'Top')))]
    jc = jc[~jc.game_type.isin(['S', 'E'])]
    jc['game_date'] = pd.to_datetime(jc.game_date)

    print('\n§1 population')
    chk('as_of date', str(jc.game_date.max().date()), H['as_of'])
    chk('unique games', int(jc.game_pk.nunique()), H['games'])
    chk('pitch rows', int(len(jc)), H['pitch_rows'])
    chk('single player_name', int(jc.player_name.nunique()), 1)
    chk('single stand (L)', jc.stand.iloc[0], 'L')

    NONPA = {'NA', 'pickoff_1b', 'pickoff_2b', 'pickoff_3b', 'caught_stealing_2b',
             'caught_stealing_3b', 'caught_stealing_home', 'stolen_base_2b',
             'stolen_base_3b', 'stolen_base_home', 'pickoff_caught_stealing_2b',
             'pickoff_caught_stealing_3b', 'pickoff_caught_stealing_home',
             'wild_pitch', 'passed_ball', 'other_advance', 'runner_double_play',
             'defensive_indiff', 'balk', 'game_advisory', 'ejection'}
    ev = jc.events.fillna('NA')
    pa = jc[~ev.isin(NONPA)].copy()
    e = pa.events

    # ── independent slash line, built from raw event strings ─────────────
    def line(d):
        x = d.events
        ab = int((~x.isin(['walk', 'intent_walk', 'hit_by_pitch', 'sac_fly', 'sac_bunt',
                           'sac_fly_double_play', 'sac_bunt_double_play',
                           'catcher_interf'])).sum())
        h = int(x.isin(['single', 'double', 'triple', 'home_run']).sum())
        s1 = int((x == 'single').sum()); s2 = int((x == 'double').sum())
        s3 = int((x == 'triple').sum()); hr = int((x == 'home_run').sum())
        bb = int(x.isin(['walk', 'intent_walk']).sum()); ubb = int((x == 'walk').sum())
        hbp = int((x == 'hit_by_pitch').sum()); sf = int((x == 'sac_fly').sum())
        so = int(x.isin(['strikeout', 'strikeout_double_play']).sum())
        tb = s1 + 2 * s2 + 3 * s3 + 4 * hr
        c = dict(pa=len(d), ab=ab, h=h, bb=bb, k=so, hr=hr,
                 ba=h / ab, obp=(h + bb + hbp) / (ab + bb + hbp + sf),
                 slg=tb / ab, krate=so / len(d), bbrate=bb / len(d))
        c['iso'] = c['slg'] - c['ba']
        c['babip'] = (h - hr) / (ab - so - hr + sf)
        # wOBA — 2026 constants read fresh from the CSV
        w = pd.read_csv(f'{DATA}/wOBA and FIP Constants.csv').set_index('Season').loc[2026]
        num = (w.wBB * ubb + w.wHBP * hbp + w['w1B'] * s1 + w['w2B'] * s2
               + w['w3B'] * s3 + w.wHR * hr)
        c['woba'] = num / (ab + ubb + sf + hbp)
        return c

    print('\n§2 season line')
    L = line(pa)
    for kk, hk in [('pa', 'plate_apps'), ('ab', 'at_bats'), ('h', 'hits'),
                   ('bb', 'walks'), ('k', 'strikeouts'), ('hr', 'hrs')]:
        chk(f'season {hk}', int(L[kk]), int(H['season'][hk]))
    for kk in ['ba', 'obp', 'slg', 'iso', 'woba', 'krate', 'bbrate', 'babip']:
        chk(f'season {kk}', round(L[kk], 4), round(H['season'][kk], 4))

    print('\n§3 monthly panel')
    pa['month'] = pa.game_date.dt.month
    for m, g in pa.groupby('month'):
        chk(f'month {m} PA', int(len(g)), int(H['monthly_pa'][str(m)]))
        chk(f'month {m} wOBA', round(line(g)['woba'], 3), H['monthly_woba'][str(m)])
    chk('monthly PA sums to season', int(sum(H['monthly_pa'].values())),
        int(H['season']['plate_apps']))
    chk('months below 50-PA floor', sorted(H['months_below_floor']),
        sorted([int(m) for m, v in H['monthly_pa'].items() if v < 50]))

    print('\n§4 the mid-June window claim')
    pre = pa[pa.game_date < '2026-06-15']; post = pa[pa.game_date >= '2026-06-15']
    lp, lq = line(pre), line(post)
    for kk in ['ba', 'obp', 'slg', 'iso', 'woba', 'krate', 'bbrate', 'babip']:
        chk(f'pre  {kk}', round(lp[kk], 4), round(H['window']['pre'][kk], 4))
        chk(f'post {kk}', round(lq[kk], 4), round(H['window']['post'][kk], 4))
    chk('pre PA', int(lp['pa']), int(H['window']['pre']['plate_apps']))
    chk('post PA', int(lq['pa']), int(H['window']['post']['plate_apps']))
    chk('BA rose across the break', bool(lq['ba'] > lp['ba']), True)
    chk('OBP rose across the break', bool(lq['obp'] > lp['obp']), True)
    chk('wOBA rose across the break', bool(lq['woba'] > lp['woba']), True)
    chk('BB rate FELL across the break', bool(lq['bbrate'] < lp['bbrate']), True)
    chk('ISO FELL across the break', bool(lq['iso'] < lp['iso']), True)
    chk('zero HR after the break', int(lq['hr']), 0)

    print('\n§5 discipline — independent SWINGS/WHIFFS declaration')
    SW = {'foul', 'foul_bunt', 'foul_tip', 'hit_into_play', 'missed_bunt',
          'swinging_pitchout', 'swinging_strike', 'swinging_strike_blocked'}
    WH = {'foul_tip', 'missed_bunt', 'swinging_pitchout', 'swinging_strike',
          'swinging_strike_blocked'}
    chk('no unmapped whiff outside swing set', int(len(WH - SW)), 0)
    for nm, d in [('pre', jc[jc.game_date < '2026-06-15']),
                  ('post', jc[jc.game_date >= '2026-06-15'])]:
        sw = d.description.isin(SW)
        wr = float(d.description.isin(WH).sum() / sw.sum())
        chk(f'{nm} whiff_rate', round(wr, 4), round(H['window'][nm]['whiff_rate'], 4))
        chk(f'{nm} swing_rate', round(float(sw.mean()), 4),
            round(H['window'][nm]['swing_rate'], 4))
        oz = d[d.zone > 9]
        chk(f'{nm} chase_rate', round(float(oz.description.isin(SW).mean()), 4),
            round(H['window'][nm]['chase_rate'], 4))
    chk('chase barely moved (|delta| < 0.01)',
        bool(abs(H['window']['post']['chase_rate'] - H['window']['pre']['chase_rate']) < .01), True)

    print('\n§6 batted ball — the developmental knock')
    for nm, d in [('pre', jc[jc.game_date < '2026-06-15']),
                  ('post', jc[jc.game_date >= '2026-06-15'])]:
        bip = d[d.type == 'X']
        chk(f'{nm} gb_rate', round(float((bip.bb_type == 'ground_ball').mean()), 4),
            round(H['window'][nm]['gb_rate'], 4))
        tr = bip[bip.launch_angle.notna() & bip.launch_speed.notna()]
        chk(f'{nm} mean_la', round(float(tr.launch_angle.mean()), 3),
            round(H['window'][nm]['mean_la'], 3))
        # ⚠ D6. The GOVERNED hard_hit_rate denominator is ALL balls in play,
        # including untracked ones — so an untracked BIP is silently scored as
        # "not hard hit". Verified against the governed convention (count/count),
        # NOT against a skipna mean, and the divergence is asserted below.
        hh = int((bip.launch_speed >= 95).sum())
        chk(f'{nm} hard_hit_rate (governed denominator = all BIP)',
            round(hh / len(bip), 4), round(H['window'][nm]['hard_hit_rate'], 4))
        tracked_only = round(hh / int(bip.launch_speed.notna().sum()), 4)
        chk(f'{nm} D6 divergence tracked-only vs governed < 1.0 pt',
            bool(abs(tracked_only - hh / len(bip)) < .01), True)
    chk('mean LA essentially unchanged (|delta| < 1 deg)',
        bool(abs(H['window']['post']['mean_la'] - H['window']['pre']['mean_la']) < 1.0), True)
    chk('GB rate stays above 50% after the break',
        bool(H['window']['post']['gb_rate'] > .50), True)
    # D6 exists at all: at least one untracked BIP in the season
    allbip = jc[jc.type == 'X']
    chk('D6 is live — untracked BIP exist in this season',
        bool(int(allbip.launch_speed.isna().sum()) > 0), True)

    print('\n§7 platoon — the Derek Hill hypothesis')
    dh = raw[(raw.player_name == 'Hill, Derek')].copy()
    dh = dh[(((dh.home_team == 'PHI') & (dh.inning_topbot == 'Bot'))
             | ((dh.away_team == 'PHI') & (dh.inning_topbot == 'Top')))]
    dh = dh[~dh.game_type.isin(['S', 'E'])]
    chk('Hill first PHI game', str(pd.to_datetime(dh.game_date).min().date()), H['hill_debut'])
    pre_h = pa[pa.game_date < H['hill_debut']]; post_h = pa[pa.game_date >= H['hill_debut']]
    chk('LHP share pre-Hill', round(float((pre_h.p_throws == 'L').mean()), 4),
        round(H['lhp_share_pre_hill'], 4))
    chk('LHP share post-Hill', round(float((post_h.p_throws == 'L').mean()), 4),
        round(H['lhp_share_post_hill'], 4))
    chk('LHP share did NOT fall over the full post-Hill window (|delta| < 1pt)',
        bool(abs(H['lhp_share_post_hill'] - H['lhp_share_pre_hill']) < .01), True)
    aug = pa[pa.month == 8]
    chk('August PA', int(len(aug)), H['aug_pa'])
    chk('August PA vs LHP', int((aug.p_throws == 'L').sum()), H['aug_lhp_pa'])
    chk('August LHP share below 5%', bool((aug.p_throws == 'L').mean() < .05), True)
    for r in H['platoon_counterfactual']:
        chk(f"platoon mix effect on {r['metric']} is ~0 (|e| < 0.005)",
            bool(abs(r['mix_effect']) < .005), True)

    print('\n§8 CF context layer')
    pos_all = raw[(((raw.home_team == 'PHI') & (raw.inning_topbot == 'Bot'))
                   | ((raw.away_team == 'PHI') & (raw.inning_topbot == 'Top')))]
    pos_all = pos_all[~pos_all.game_type.isin(['S', 'E'])]
    pps_all = raw[~(((raw.home_team == 'PHI') & (raw.inning_topbot == 'Bot'))
                    | ((raw.away_team == 'PHI') & (raw.inning_topbot == 'Top')))]
    pps_all = pps_all[~pps_all.game_type.isin(['S', 'E'])]
    cfg = (pps_all[pps_all.fielder_8 == 702222]
           .groupby('game_year').game_pk.nunique())
    chk('Crawford CF games 2026', int(cfg.loc[2026]), 110)
    snap = pd.read_csv(f'{HERE}/dp_uc34_cf_matched_pa_snapshot.csv')
    chk('context pool size', int(len(snap)), H['cf_pool_n'])
    chk('all comparators reach Crawford as-of PA',
        int((snap.cum_pa == H['crawford_ctx_pa']).sum()), H['cf_pool_n'])
    chk('Crawford wOBA rank at matched PA',
        int(snap[snap.season_key == 'Crawford 2026'].woba_rank.iat[0]),
        H['crawford_woba_rank'])
    chk('Crawford is not last in OBP at matched PA',
        bool(snap.cum_obp.rank(ascending=False)[snap.season_key == 'Crawford 2026'].iat[0]
             < len(snap)), True)

    print('\n§9 population benchmark')
    pool = pd.read_csv(f'{HERE}/dp_uc34_population_pool.csv')
    chk('pool seasons', int(len(pool)), H['pool_n'])
    chk('pool players', int(pool.player_name.nunique()), H['pool_players'])
    chk('every pool season clears the 50-PA floor', bool((pool.plate_apps >= 50).all()), True)
    prof = pd.read_csv(f'{HERE}/dp_uc34_profile_percentiles.csv')
    for r in prof.itertuples():
        s = pool[r.column].dropna()
        chk(f'pctile {r.column}', round(float((s < r.crawford).mean() * 100), 2),
            round(float(r.percentile), 2), tol=.02)
    def pc(c):
        return float(prof[prof.column == c].percentile.iat[0])
    chk('high-swing verifies (swing_rate >= 75th)', bool(pc('swing_rate') >= 75), True)
    chk('high-chase verifies (chase_rate >= 75th)', bool(pc('chase_rate') >= 75), True)
    chk('low-whiff verifies (whiff_rate <= 25th)', bool(pc('whiff_rate') <= 25), True)
    chk('GB knock verifies (gb_rate >= 75th)', bool(pc('gb_rate') >= 75), True)
    chk('LA knock verifies (mean_la <= 10th)', bool(pc('mean_la') <= 10), True)

    print('\n§10 pitch mix')
    pt = pd.read_csv(f'{HERE}/dp_uc34_pitch_type_season.csv')
    chk('every reported pitch_type clears 40 pitches', bool((pt.pitches >= 40).all()), True)
    pgw = pd.read_csv(f'{HERE}/dp_uc34_pitch_group_window.csv')
    chk('pitch-group PA sums to season PA', int(pgw.plate_apps.sum()),
        int(H['season']['plate_apps']))
    chk('pitch-group pitches sum to pitch rows', int(pgw.pitches.sum()), H['pitch_rows'])
    os_pre = pgw[(pgw.window == 'pre_0615') & (pgw.pitch_group == 'offspeed')].iloc[0]
    os_post = pgw[(pgw.window == 'post_0615') & (pgw.pitch_group == 'offspeed')].iloc[0]
    chk('offspeed chase fell', bool(os_post.chase_rate < os_pre.chase_rate), True)
    chk('offspeed post-window is below the 50-PA floor',
        bool(os_post.plate_apps < 50), True)

    print('\n§11 breakpoint sensitivity')
    scan = pd.read_csv(f'{HERE}/dp_uc34_breakpoint_scan.csv')
    for r in scan.itertuples():
        a = pa[pa.game_date < r.breakpoint]; b = pa[pa.game_date >= r.breakpoint]
        chk(f'scan {r.breakpoint} post wOBA', round(line(b)['woba'], 4),
            round(r.post_woba, 4))
    chk('a mid-May breakpoint would REVERSE the sign',
        bool(scan[scan.breakpoint == '2026-05-15'].delta_woba.iat[0] < 0), True)
    chk('the DPO breakpoint is not the strongest available',
        bool(scan.delta_woba.max() > scan[scan.breakpoint == '2026-06-15'].delta_woba.iat[0]),
        True)

    print(f'\n{"="*74}\nVERIFICATION: {P} PASS / {F} FAIL')
    if FAILS:
        print('\n'.join(FAILS)); sys.exit(1)
    print('='*74)


if __name__ == '__main__':
    main()
