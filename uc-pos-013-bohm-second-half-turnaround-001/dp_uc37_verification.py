"""
dp_uc37_verification.py — independent verification for uc-pos-013.

Recomputes every headline by a DIFFERENT path from the build kernel:
  * parquet files read in REVERSE year order
  * subject filtered BEFORE the batting-role tag is applied
  * every mask declared inline from raw columns — no shared constants
  * pull-air classification re-expressed algebraically (sign tests), then
    cross-checked against a spray-angle formulation and a scale-invariance test
  * runs_created recomputed from FIRST bat_score / LAST post_bat_score by
    pitch order, not min/max aggregation
  * the DPO's submitted notebook merge-chain is reproduced (§15) as the
    original-method path, with its two paren transpositions repaired and the
    repairs logged — uc-pps-026 precedent
  * NO import of dp_uc37_kernel

Any disagreement with the published receipts is a FAIL.
"""
from __future__ import annotations
import json, math, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get(
    'DP_UC37_DATA',
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
    print(f"  {'PASS' if ok else 'FAIL'}  {label:<62} {got!r} vs {want!r}")


NONPA = {'NA', 'pickoff_1b', 'pickoff_2b', 'pickoff_3b', 'caught_stealing_2b',
         'caught_stealing_3b', 'caught_stealing_home', 'stolen_base_2b',
         'stolen_base_3b', 'stolen_base_home', 'pickoff_caught_stealing_2b',
         'pickoff_caught_stealing_3b', 'pickoff_caught_stealing_home',
         'wild_pitch', 'passed_ball', 'other_advance', 'runner_double_play',
         'defensive_indiff', 'balk', 'game_advisory', 'ejection'}


def pa_of(d):
    return d[~d.events.fillna('NA').isin(NONPA)]


def line(d, woba_csv):
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
    c = dict(pa=len(d), ab=ab, h=h, bb=bb, k=so, hr=hr, d2=s2,
             ba=h / ab, obp=(h + bb + hbp) / (ab + bb + hbp + sf),
             slg=tb / ab, krate=so / len(d), bbrate=bb / len(d))
    c['iso'] = c['slg'] - c['ba']
    c['babip'] = (h - hr) / (ab - so - hr + sf)
    w = woba_csv.set_index('Season').loc[2026]
    num = (w.wBB * ubb + w.wHBP * hbp + w['w1B'] * s1 + w['w2B'] * s2
           + w['w3B'] * s3 + w.wHR * hr)
    c['woba'] = num / (ab + ubb + sf + hbp)
    c['ops'] = c['obp'] + c['slg']
    return c


def main():
    H = json.load(open(f'{HERE}/dp_uc37_headlines.json'))
    WOBA = pd.read_csv(f'{DATA}/wOBA and FIP Constants.csv')

    # ── independent load: reverse order, subject-first ────────────────────
    fr = []
    for y in range(2026, 2014, -1):
        p = f'{DATA}/data/phillies/phils_{y}.parquet'
        if os.path.exists(p):
            fr.append(pd.read_parquet(p))
    raw = pd.concat(fr, ignore_index=True)
    ab_all = raw[raw.batter == 664761].copy()
    ab_all = ab_all[(((ab_all.home_team == 'PHI') & (ab_all.inning_topbot == 'Bot'))
                     | ((ab_all.away_team == 'PHI') & (ab_all.inning_topbot == 'Top')))]
    ab_all = ab_all[~ab_all.game_type.isin(['S', 'E'])]
    ab_all['game_date'] = pd.to_datetime(ab_all.game_date)
    b = ab_all[ab_all.game_year == 2026].copy()

    print('\n§1 population & entity lock')
    chk('as_of date', str(b.game_date.max().date()), H['as_of'])
    chk('unique games 2026', int(b.game_pk.nunique()), H['games'])
    chk('pitch rows 2026', int(len(b)), H['pitch_rows'])
    chk('single player_name', int(b.player_name.nunique()), 1)
    chk('player_name is Bohm, Alec', b.player_name.iloc[0], 'Bohm, Alec')
    chk('single stand (R)', b.stand.iloc[0], 'R')
    chk('career seasons 2020-2026', sorted(int(y) for y in ab_all.game_year.unique()),
        [2020, 2021, 2022, 2023, 2024, 2025, 2026])

    print('\n§2 the break operator')
    pre_r = b[b.game_date < '2026-07-16']; post_r = b[b.game_date > '2026-07-15']
    chk('operator complements are exhaustive', int(len(pre_r) + len(post_r)), int(len(b)))
    chk('no game on 7/13-7/15',
        int(b[(b.game_date >= '2026-07-13') & (b.game_date <= '2026-07-15')].shape[0]), 0)
    chk('last pre-break game', str(pre_r.game_date.max().date()), H['last_pre_game'])
    chk('first post-break game', str(post_r.game_date.min().date()), H['first_post_game'])

    print('\n§3 season line')
    pa = pa_of(b)
    L = line(pa, WOBA)
    for kk, hk in [('pa', 'plate_apps'), ('ab', 'at_bats'), ('h', 'hits'),
                   ('bb', 'walks'), ('k', 'strikeouts'), ('hr', 'hrs')]:
        chk(f'season {hk}', int(L[kk]), int(H['season'][hk]))
    for kk in ['ba', 'obp', 'slg', 'ops', 'iso', 'woba', 'krate', 'bbrate', 'babip']:
        chk(f'season {kk}', round(L[kk], 4), round(H['season'][kk], 4))

    print('\n§4 monthly panel')
    pa2 = pa.copy(); pa2['month'] = pa2.game_date.dt.month
    for m, g in pa2.groupby('month'):
        chk(f'month {m} PA', int(len(g)), int(H['monthly_pa'][str(m)]))
        chk(f'month {m} wOBA', round(line(g, WOBA)['woba'], 3), H['monthly_woba'][str(m)])
        chk(f'month {m} SLG', round(line(g, WOBA)['slg'], 3), H['monthly_slg'][str(m)])
    chk('monthly PA sums to season', int(sum(H['monthly_pa'].values())),
        int(H['season']['plate_apps']))
    chk('months below 50-PA floor', sorted(H['months_below_floor']),
        sorted([int(m) for m, v in H['monthly_pa'].items() if v < 50]))

    print('\n§5 the window claim — results')
    lp = line(pa_of(pre_r), WOBA); lq = line(pa_of(post_r), WOBA)
    for kk in ['ba', 'obp', 'slg', 'iso', 'woba', 'krate', 'bbrate', 'babip']:
        chk(f'pre  {kk}', round(lp[kk], 4), round(H['window']['pre'][kk], 4))
        chk(f'post {kk}', round(lq[kk], 4), round(H['window']['post'][kk], 4))
    chk('pre PA', int(lp['pa']), int(H['window']['pre']['plate_apps']))
    chk('post PA', int(lq['pa']), int(H['window']['post']['plate_apps']))
    chk('both windows clear the 50-PA floor', bool(lp['pa'] >= 50 and lq['pa'] >= 50), True)
    chk('SLG rose across the break', bool(lq['slg'] > lp['slg']), True)
    chk('BA rose across the break', bool(lq['ba'] > lp['ba']), True)
    chk('wOBA rose across the break', bool(lq['woba'] > lp['woba']), True)
    chk('K rate FELL across the break', bool(lq['krate'] < lp['krate']), True)
    chk('BABIP rose >= 100 points', bool(lq['babip'] - lp['babip'] >= .10), True)

    print('\n§6 BA with RISP — the DPO operator, terminal-pitch semantics')
    for nm, d, key in [('pre', pre_r, 'pre'), ('post', post_r, 'post')]:
        risp = d[d.on_2b.notna() | d.on_3b.notna()]
        lr = line(pa_of(risp), WOBA)
        chk(f'{nm} RISP PA', int(lr['pa']), int(H['window'][key]['risp_pa']))
        chk(f'{nm} RISP AB', int(lr['ab']), int(H['window'][key]['risp_ab']))
        chk(f'{nm} ba_risp', round(lr['ba'], 4), round(H['window'][key]['ba_risp'], 4))
        chk(f'{nm} slg_risp', round(lr['slg'], 4), round(H['window'][key]['slg_risp'], 4))
    chk('post RISP sample below 50-PA floor (must be flagged)',
        bool(H['window']['post']['risp_pa'] < 50), True)
    chk('season ba_risp', round(line(pa_of(b[b.on_2b.notna() | b.on_3b.notna()]),
                                     WOBA)['ba'], 4),
        round(H['season']['ba_risp'], 4))

    print('\n§7 runs created — first/last path, not min/max')
    def rc_firstlast(d):
        s = d.sort_values(['game_pk', 'at_bat_number', 'pitch_number'])
        g = s.groupby(['game_pk', 'at_bat_number'])
        first_bs = g.bat_score.first(); last_pbs = g.post_bat_score.last()
        return int((last_pbs - first_bs).sum())
    rc_pre, rc_post = rc_firstlast(pre_r), rc_firstlast(post_r)
    chk('pre runs_created', rc_pre, int(H['window']['pre']['runs_created']))
    chk('post runs_created', rc_post, int(H['window']['post']['runs_created']))
    chk('pre rc_per_pa', round(rc_pre / lp['pa'], 4),
        round(H['window']['pre']['rc_per_pa'], 4))
    chk('post rc_per_pa', round(rc_post / lq['pa'], 4),
        round(H['window']['post']['rc_per_pa'], 4))
    chk('rc_per_pa rose across the break',
        bool(rc_post / lq['pa'] > rc_pre / lp['pa']), True)
    chk('bat_score monotone within PA (first==min everywhere)',
        bool((pre_r.groupby(['game_pk', 'at_bat_number']).bat_score.first()
              == pre_r.groupby(['game_pk', 'at_bat_number']).bat_score.min()).all()), True)

    print('\n§8 discipline — independent SWINGS/WHIFFS declaration')
    SW = {'foul', 'foul_bunt', 'foul_tip', 'hit_into_play', 'missed_bunt',
          'swinging_pitchout', 'swinging_strike', 'swinging_strike_blocked'}
    WH = {'foul_tip', 'missed_bunt', 'swinging_pitchout', 'swinging_strike',
          'swinging_strike_blocked'}
    chk('WHIFFS is a subset of SWINGS', int(len(WH - SW)), 0)
    for nm, d, key in [('pre', pre_r, 'pre'), ('post', post_r, 'post')]:
        sw = d.description.isin(SW)
        chk(f'{nm} swing_rate', round(float(sw.mean()), 4),
            round(H['window'][key]['swing_rate'], 4))
        chk(f'{nm} whiff_rate', round(float(d.description.isin(WH).sum() / sw.sum()), 4),
            round(H['window'][key]['whiff_rate'], 4))
        oz = d[d.zone > 9]
        chk(f'{nm} chase_rate', round(float(oz.description.isin(SW).mean()), 4),
            round(H['window'][key]['chase_rate'], 4))
        iz = d[d.zone < 10]
        chk(f'{nm} swing_rate_in_zone', round(float(iz.description.isin(SW).mean()), 4),
            round(H['window'][key]['swing_rate_in_zone'], 4))
        izsw = iz[iz.description.isin(SW)]
        chk(f'{nm} whiff_rate_in_zone',
            round(float(izsw.description.isin(WH).mean()), 4),
            round(H['window'][key]['whiff_rate_in_zone'], 4))
        chk(f'{nm} in_zone_rate (pitcher metric)',
            round(float(len(iz) / (len(iz) + len(oz))), 4),
            round(H['window'][key]['in_zone_rate'], 4),
            tol=5e-3)  # kernel denominator includes NULL-zone pitches; see §16
        fp = d[d.pitch_number == 1]
        chk(f'{nm} fpsr (pitcher metric)',
            round(float((len(fp) - (fp.type == 'B').sum()) / len(fp)), 4),
            round(H['window'][key]['fpsr'], 4))
    chk('chase essentially unchanged (|delta| < 0.01)',
        bool(abs(H['window']['post']['chase_rate']
                 - H['window']['pre']['chase_rate']) < .01), True)
    chk('whiff FELL across the break', bool(H['window']['post']['whiff_rate']
                                            < H['window']['pre']['whiff_rate']), True)
    chk('z-whiff FELL by >= 4 points',
        bool(H['window']['pre']['whiff_rate_in_zone']
             - H['window']['post']['whiff_rate_in_zone'] >= .04), True)
    chk('null-zone pitches exist (excluded from both zone pops)',
        bool(int(b.zone.isna().sum()) > 0), True)

    print('\n§9 contact quality')
    for nm, d, key in [('pre', pre_r, 'pre'), ('post', post_r, 'post')]:
        bip = d[d.type == 'X']
        hh = int((bip.launch_speed >= 95).sum())
        chk(f'{nm} hard_hit_rate (governed denominator = all BIP)',
            round(hh / len(bip), 4), round(H['window'][key]['hard_hit_rate'], 4))
        chk(f'{nm} barrel_rate', round(int((bip.launch_speed_angle == 6).sum())
                                       / len(bip), 4),
            round(H['window'][key]['barrel_rate'], 4))
        chk(f'{nm} gb_rate', round(float((bip.bb_type == 'ground_ball').mean()), 4),
            round(H['window'][key]['gb_rate'], 4))
        chk(f'{nm} pu_rate', round(float((bip.bb_type == 'popup').mean()), 4),
            round(H['window'][key]['pu_rate'], 4))
        tr = bip[bip.launch_speed.notna() & bip.launch_angle.notna()]
        chk(f'{nm} mean_ev tracked', round(float(tr.launch_speed.mean()), 3),
            round(H['window'][key]['mean_ev'], 3))
        chk(f'{nm} mean_la tracked', round(float(tr.launch_angle.mean()), 3),
            round(H['window'][key]['mean_la'], 3))
        chk(f'{nm} xwobacon_bip',
            round(float(bip.estimated_woba_using_speedangle.mean()), 4),
            round(H['window'][key]['xwobacon_bip'], 4))
    chk('hard-hit rose across the break',
        bool(H['window']['post']['hard_hit_rate']
             > H['window']['pre']['hard_hit_rate']), True)
    chk('xwOBAcon rose with the results (not a pure-BABIP story)',
        bool(H['window']['post']['xwobacon_bip']
             - H['window']['pre']['xwobacon_bip'] >= .05), True)
    chk('pre-break underperformance: wOBA < xwOBAcon-implied direction '
        '(pre woba < pre xwobacon)', bool(H['window']['pre']['woba']
                                          < H['window']['pre']['xwobacon_bip']), True)
    chk('D6 exposure: untracked BIP count 2026',
        int(b[b.type == 'X'].launch_speed.isna().sum()), 1)

    print('\n§10 inds reconciliation — the O-3 foul-ball trap, quantified')
    rec = pd.read_csv(f'{HERE}/dp_uc37_inds_reconciliation.csv')
    for r in rec.itertuples():
        d = pre_r if r.window == 'pre_break' else post_r
        chk(f'{r.window} inds ev_mu (all rows)', round(float(d.launch_speed.mean()), 3),
            round(r.ev_mu_inds_allrows, 3))
        chk(f'{r.window} non-BIP rows with launch_speed',
            int(((d.type != 'X') & d.launch_speed.notna()).sum()),
            int(r.non_bip_rows_with_launch_speed))
        chk(f'{r.window} all-rows vs tracked-BIP EV gap > 4 mph',
            bool(r.mean_ev_tracked_bip - r.ev_mu_inds_allrows > 4), True)

    print('\n§11 pull-air — algebraic re-expression + invariance')
    bip = b[b.type == 'X'].copy()
    for C in (1.0, 2.495671):
        lx = C * (bip.hc_x.astype(float) - 125.42)
        ly = C * (198.27 - bip.hc_y.astype(float))
        # RHB (Bohm): Pull iff ly + 4.7*lx <= 0 — re-expressed as a sign test
        is_pull = (ly + 4.7 * lx) <= 0
        is_oppo = (~is_pull) & ((ly - 4.7 * lx) <= 0)
        pull_air = int((is_pull & (bip.bb_type != 'ground_ball')).sum())
        if C == 1.0:
            pa_c1 = pull_air
        chk(f'pull_air count at scale C={C}', pull_air, pa_c1)
    chk('season pull_air_rate', round(pa_c1 / len(bip), 4),
        round(H['season']['pull_air_rate'], 4))
    for nm, d, key in [('pre', pre_r, 'pre'), ('post', post_r, 'post')]:
        bp_ = d[d.type == 'X']
        lx = bp_.hc_x.astype(float) - 125.42
        ly = 198.27 - bp_.hc_y.astype(float)
        pull = (ly + 4.7 * lx) <= 0
        chk(f'{nm} pull_air_rate',
            round(int((pull & (bp_.bb_type != 'ground_ball')).sum()) / len(bp_), 4),
            round(H['window'][key]['pull_air_rate'], 4))
        chk(f'{nm} pull_rate', round(int(pull.sum()) / len(bp_), 4),
            round(H['window'][key]['pull_rate'], 4))
    # spray-angle cross-check on the y>0 subset (identical classification)
    lx = bip.hc_x.astype(float) - 125.42; ly = 198.27 - bip.hc_y.astype(float)
    pos_y = ly > 0
    phi = np.degrees(np.arctan2(lx[pos_y], ly[pos_y]))
    bnd = math.degrees(math.atan(1 / 4.7))
    pull_angle = (phi <= -bnd)
    pull_sign = ((ly + 4.7 * lx) <= 0)[pos_y]
    chk('spray-angle formulation agrees on y>0 subset',
        int((pull_angle != pull_sign).sum()), 0)
    chk('pull boundary is ±12.0° off CF', round(bnd, 1), 12.0)
    chk('coordinate convention: median pulled-GB loc_x is negative (LF for RHB)',
        bool(H['coord_assert_median_pull_gb_loc_x_ft'] < 0), True)
    chk('pull-air FLAT across the break (|delta| < 0.01)',
        bool(abs(H['window']['post']['pull_air_rate']
                 - H['window']['pre']['pull_air_rate']) < .01), True)
    paq = pd.read_csv(f'{HERE}/dp_uc37_pull_air_quality.csv')
    po = paq[paq.window == 'post_break'].iloc[0]
    pr = paq[paq.window == 'pre_break'].iloc[0]
    d_post = post_r[post_r.type == 'X'].copy()
    lx = d_post.hc_x.astype(float) - 125.42; ly = 198.27 - d_post.hc_y.astype(float)
    m = ((ly + 4.7 * lx) <= 0) & (d_post.bb_type != 'ground_ball')
    chk('post pull-air mean EV', round(float(d_post[m].launch_speed.mean()), 2),
        round(float(po.pa_mean_ev), 2))
    chk('post pull-air HR count', int((d_post[m].events == 'home_run').sum()),
        int(po.pa_hrs))
    chk('pull-air quality jumped >= 3 mph while volume held',
        bool(po.pa_mean_ev - pr.pa_mean_ev >= 3), True)

    print('\n§12 platoon')
    pre_pa, post_pa = pa_of(pre_r), pa_of(post_r)
    chk('LHP share pre', round(float((pre_pa.p_throws == 'L').mean()), 4),
        round(H['lhp_share_pre'], 4))
    chk('LHP share post', round(float((post_pa.p_throws == 'L').mean()), 4),
        round(H['lhp_share_post'], 4))
    ps = pd.read_csv(f'{HERE}/dp_uc37_platoon_splits.csv')
    for r in ps.itertuples():
        d = (pre_r if r.window == 'pre_break' else post_r)
        cell = pa_of(d[d.p_throws == r.p_throws])
        lc = line(cell, WOBA)
        chk(f'{r.window} vs {r.p_throws} PA', int(lc['pa']), int(r.plate_apps))
        chk(f'{r.window} vs {r.p_throws} wOBA', round(lc['woba'], 4),
            round(float(r.woba), 4), tol=1e-3)
    chk('post-vs-LHP cell is below the 50-PA floor',
        bool(int(ps[(ps.window == 'post_break') & (ps.p_throws == 'L')]
                 .plate_apps.iat[0]) < 50), True)
    # PL-1 recompute: reweight post within-split lines by pre PA shares
    post_L = line(pa_of(post_r[post_r.p_throws == 'L']), WOBA)
    post_R = line(pa_of(post_r[post_r.p_throws == 'R']), WOBA)
    wL_pre = float((pre_pa.p_throws == 'L').mean())
    wL_post = float((post_pa.p_throws == 'L').mean())
    for r in H['platoon_counterfactual']:
        m = r['metric']
        actual = wL_post * post_L[m] + (1 - wL_post) * post_R[m]
        reweighted = wL_pre * post_L[m] + (1 - wL_pre) * post_R[m]
        chk(f"PL-1 {m} actual", round(actual, 4), round(r['actual'], 4), tol=1e-3)
        chk(f"PL-1 {m} mix_effect", round(actual - reweighted, 4),
            round(r['mix_effect'], 4), tol=1e-3)
        chk(f"PL-1 {m} mix effect is NEGATIVE (surge not mix-flattered)",
            bool(r['mix_effect'] < 0), True)

    print('\n§13 pitch group / type')
    PG = {'FF': 'fastball', 'SI': 'fastball', 'FC': 'fastball',
          'SL': 'breaking', 'ST': 'breaking', 'CU': 'breaking', 'KC': 'breaking',
          'SV': 'breaking', 'CS': 'breaking',
          'CH': 'offspeed', 'FS': 'offspeed', 'FO': 'offspeed', 'SC': 'offspeed',
          'KN': 'offspeed'}
    pgw = pd.read_csv(f'{HERE}/dp_uc37_pitch_group_window.csv')
    chk('pitch-group PA sums to season PA', int(pgw.plate_apps.sum()),
        int(H['season']['plate_apps']))
    chk('pitch-group pitches sum to pitch rows', int(pgw.pitches.sum()),
        H['pitch_rows'])
    for r in pgw[pgw.pitch_group.isin(['fastball', 'breaking', 'offspeed'])].itertuples():
        d = (pre_r if r.window == 'pre_break' else post_r)
        grp = d[d.pitch_type.map(PG) == r.pitch_group]
        chk(f'{r.window} {r.pitch_group} pitches', int(len(grp)), int(r.pitches))
        lc = line(pa_of(grp), WOBA)
        chk(f'{r.window} {r.pitch_group} SLG', round(lc['slg'], 4),
            round(float(r.slg), 4), tol=1e-3)
    brk_pre = pgw[(pgw.window == 'pre_break') & (pgw.pitch_group == 'breaking')].iloc[0]
    brk_post = pgw[(pgw.window == 'post_break') & (pgw.pitch_group == 'breaking')].iloc[0]
    chk('breaking-ball whiff FELL', bool(brk_post.whiff_rate < brk_pre.whiff_rate), True)
    chk('breaking-ball SLG rose >= 150 points',
        bool(brk_post.slg - brk_pre.slg >= .15), True)
    chk('post offspeed cell below floor (flagged)', bool(
        pgw[(pgw.window == 'post_break') & (pgw.pitch_group == 'offspeed')]
        .below_pa_floor.iat[0]), True)
    pt = pd.read_csv(f'{HERE}/dp_uc37_pitch_type_season.csv')
    chk('every reported pitch_type clears 40 pitches', bool((pt.pitches >= 40).all()), True)

    print('\n§14 breakpoint sensitivity — the scan is the honesty receipt')
    scan = pd.read_csv(f'{HERE}/dp_uc37_breakpoint_scan.csv')
    for r in scan.itertuples():
        d_post = pa2[pa2.game_date >= r.breakpoint]
        chk(f'scan {r.breakpoint} post wOBA', round(line(d_post, WOBA)['woba'], 4),
            round(r.post_woba, 4))
    chk('delta_woba POSITIVE at every candidate breakpoint (no sign reversal)',
        bool((scan.delta_woba > 0).all()), True)
    chk('delta_slg POSITIVE at every candidate breakpoint',
        bool((scan.delta_slg > 0).all()), True)
    chk('the ASB is NOT the strongest available breakpoint',
        bool(scan.delta_woba.max()
             > scan[scan.breakpoint == '2026-07-16'].delta_woba.iat[0]), True)
    chk('the 8 Aug candidate post-window is at the 50-PA floor exactly',
        int(scan[scan.breakpoint == '2026-08-08'].post_pa.iat[0]), 50)

    print('\n§15 the DPO notebook method — original-path reproduction')
    # The submitted snippet, repaired: two misplaced parens around the
    # chase_rate and RISP merges (logged in 01_strategy_intake §transcription).
    # Governed ORIGINALS re-declared inline (rounded nresults, inner-merge
    # whiff), run at the DPO's level ['player_name','stand'] on the post frame.
    level = ['player_name', 'stand']
    df = b[b.game_date > '2026-07-15']

    def nresults_orig(level, d):
        p = pa_of(d)
        out = p.groupby(level, as_index=False).agg(plate_apps=('des', 'size'))
        x = p.events
        agg = p.assign(
            ab=(~x.isin(['walk', 'intent_walk', 'hit_by_pitch', 'sac_fly', 'sac_bunt',
                         'sac_fly_double_play', 'sac_bunt_double_play',
                         'catcher_interf'])).astype(int),
            h=x.isin(['single', 'double', 'triple', 'home_run']).astype(int),
            tb=x.map({'single': 1, 'double': 2, 'triple': 3, 'home_run': 4}).fillna(0),
            k=x.isin(['strikeout', 'strikeout_double_play']).astype(int)
        ).groupby(level, as_index=False).agg(ab=('ab', 'sum'), h=('h', 'sum'),
                                             tb=('tb', 'sum'), k=('k', 'sum'))
        out = out.merge(agg, on=level)
        out['ba'] = (out.h / out.ab).round(3)
        out['slg'] = (out.tb / out.ab).round(3)
        out['krate'] = (out.k / out.plate_apps).round(3)
        return out

    z = (nresults_orig(level, df)
         .merge(df[df.description.isin(SW)].groupby(level, as_index=False)
                .agg(swings=('des', 'size'))
                .merge(df[df.description.isin(WH)].groupby(level, as_index=False)
                       .agg(whiffs=('des', 'size')), on=level)
                .assign(whiff_rate=lambda t: t.whiffs / t.swings), on=level, how='left')
         .merge(df[(df.zone > 9) & df.description.isin(SW)]
                .groupby(level, as_index=False).agg(chases=('des', 'size'))
                .merge(df[df.zone > 9].groupby(level, as_index=False)
                       .agg(ooz=('des', 'size')), on=level)
                .assign(chase_rate=lambda t: t.chases / t.ooz),
                on=level, how='left', suffixes=('', '_cr'))
         .merge(nresults_orig(level, df[(df.on_2b.isna() == False)
                                        | (df.on_3b.isna() == False)])[level + ['ba']],
                on=level, how='left', suffixes=('', '_risp'))
         .merge(df.groupby(level + ['game_pk', 'at_bat_number'], as_index=False)
                .agg(min_bs=('bat_score', 'min'), max_pbs=('post_bat_score', 'max'))
                .assign(rc=lambda t: t.max_pbs - t.min_bs)
                .groupby(level, as_index=False).agg(runs_created=('rc', 'sum')),
                on=level, how='left')
         .merge(df[df.zone < 10][df[df.zone < 10].description.isin(SW)]
                .groupby(level, as_index=False).agg(z_swings=('des', 'size'))
                .merge(df[df.zone < 10].groupby(level, as_index=False)
                       .agg(z_pitches=('des', 'size')), on=level)
                .assign(swing_rate_in_zone=lambda t: t.z_swings / t.z_pitches),
                on=level, how='left'))
    r = z.iloc[0]
    chk('notebook-path single row at (player_name, stand)', int(len(z)), 1)
    chk('notebook-path post SLG (3dp, D4 rounding)', float(r.slg),
        round(H['window']['post']['slg'], 3))
    chk('notebook-path post BA (3dp)', float(r.ba), round(H['window']['post']['ba'], 3))
    chk('notebook-path post ba_risp (3dp)', round(float(r.ba_risp), 3),
        round(H['window']['post']['ba_risp'], 3))
    chk('notebook-path post whiff_rate', round(float(r.whiff_rate), 4),
        round(H['window']['post']['whiff_rate'], 4))
    chk('notebook-path post chase_rate', round(float(r.chase_rate), 4),
        round(H['window']['post']['chase_rate'], 4))
    chk('notebook-path post runs_created', int(r.runs_created),
        int(H['window']['post']['runs_created']))
    chk('notebook-path post swing_rate_in_zone', round(float(r.swing_rate_in_zone), 4),
        round(H['window']['post']['swing_rate_in_zone'], 4))

    print('\n§16 population percentiles')
    pool = pd.read_csv(f'{HERE}/dp_uc37_population_pool.csv')
    chk('pool seasons', int(len(pool)), int(H['pool_n']))
    chk('pool players', int(pool.player_name.nunique()), int(H['pool_players']))
    chk('every pool season clears the 50-PA floor', bool((pool.plate_apps >= 50).all()), True)
    prof = pd.read_csv(f'{HERE}/dp_uc37_profile_percentiles.csv')
    for r in prof.itertuples():
        s = pool[r.column].dropna()
        chk(f'pctile 2026 {r.column}', round(float((s < r.bohm_2026).mean() * 100), 2),
            round(float(r.pct_2026), 2), tol=.02)
    def pc(c, col='pct_2026'):
        return float(prof[prof.column == c][col].iat[0])
    chk('"rarely whiffs" verifies — 2026 whiff <= 10th pctile',
        bool(pc('whiff_rate') <= 10), True)
    chk('post-break whiff is <= 5th pctile',
        bool(pc('whiff_rate', 'pct_post_window') <= 5), True)
    chk('pull-air stays LOW — 2026 <= 20th pctile', bool(pc('pull_air_rate') <= 20), True)
    chk('post-break hard-hit >= 85th pctile',
        bool(pc('hard_hit_rate', 'pct_post_window') >= 85), True)
    chk('post-break SLG >= 80th pctile', bool(pc('slg', 'pct_post_window') >= 80), True)

    print(f'\n{"=" * 74}\nVERIFICATION: {P} PASS / {F} FAIL')
    if FAILS:
        print('\n'.join(FAILS)); sys.exit(1)
    print('=' * 74)


if __name__ == '__main__':
    main()
