"""
dp_uc33_verification.py — independent verification for uc-pos-010
==================================================================
House pattern: reload the parquet with a DIFFERENT assembly and filter order
than the build, recompute every headline from inline `events`/`description`
masks with NO import of the build's KPI kernel, then assert against both the
shipped CSV receipts and the numbers quoted in the report.

Run:  python dp_uc33_verification.py [MLB_REPO_ROOT]
Exits non-zero on any FAIL.
"""
from __future__ import annotations

import glob
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/MLB'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
SUBJ = 'Stott, Bryson'

_p = _f = 0
def ok(label, cond, got=None, want=None):
    global _p, _f
    if cond: _p += 1
    else:    _f += 1
    print(f"{'PASS' if cond else 'FAIL'}  {label}" + ('' if cond else f"\n        got={got!r} want={want!r}"))

def near(a, b, tol=0.001):
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol

# ── independent load: read every file, concat LAST, filter in reverse order ──
files = sorted(glob.glob(os.path.join(ROOT, 'data', 'phillies', 'phils_*.parquet')))
raw = pd.concat([pd.read_parquet(f) for f in reversed(files)], ignore_index=True)
raw['game_date'] = pd.to_datetime(raw.game_date)
# filter subject FIRST (build filtered role first), then role, then game_type
d = raw[raw.player_name == SUBJ]
d = d[(((d.home_team == 'PHI') & (d.inning_topbot == 'Bot'))
       | ((d.away_team == 'PHI') & (d.inning_topbot == 'Top')))]
d = d[~d.game_type.isin(['S', 'E'])].copy()
d['mo'] = d.game_date.dt.month
d26 = d[d.game_year == 2026]

panel = pd.read_csv(os.path.join(OUT, 'dp_uc33_monthly_panel.csv'))
head = json.load(open(os.path.join(OUT, 'dp_uc33_headlines.json')))
games = pd.read_csv(os.path.join(OUT, 'dp_uc33_streak_games.csv'))

# inline masks — declared here, not imported
NONPA = ['NA','pickoff_1b','pickoff_2b','pickoff_3b','caught_stealing_2b','caught_stealing_3b',
         'caught_stealing_home','stolen_base_2b','stolen_base_3b','stolen_base_home','wild_pitch',
         'passed_ball','other_advance','runner_double_play','defensive_indiff','balk',
         'game_advisory','ejection','pickoff_caught_stealing_2b','pickoff_caught_stealing_3b',
         'pickoff_caught_stealing_home']
SW = ['foul','foul_bunt','foul_tip','hit_into_play','missed_bunt','swinging_pitchout',
      'swinging_strike','swinging_strike_blocked']
WH = ['foul_tip','missed_bunt','swinging_pitchout','swinging_strike','swinging_strike_blocked']
pa26 = d26[~d26.events.replace(np.nan, 'NA').isin(NONPA)]

print("=" * 66); print("§1  population"); print("=" * 66)
ok("2026 PA total reconciles to panel", int(len(pa26)) == int(panel.plate_apps.sum()),
   len(pa26), panel.plate_apps.sum())
ok("6 month buckets present (incl. March)", panel.month.nunique() == 6, panel.month.nunique(), 6)
ok("March bucket is small (B-3 evidence)", int(panel[panel.month == 3].plate_apps.iat[0]) < 20)
ok("data ends 2026-08-13", str(d26.game_date.max().date()) == '2026-08-13', str(d26.game_date.max().date()))

print("=" * 66); print("§2  monthly slash / rate reconstruction"); print("=" * 66)
for _, r in panel.iterrows():
    m = int(r.month); g = pa26[pa26.mo == m]
    ab = g[~g.events.isin(['walk','intent_walk','hit_by_pitch','sac_fly','sac_bunt'])]
    h  = g.events.isin(['single','double','triple','home_run']).sum()
    bb = g.events.isin(['walk','intent_walk']).sum()
    k  = g.events.isin(['strikeout','strikeout_double_play']).sum()
    hbp= (g.events == 'hit_by_pitch').sum(); sf = (g.events == 'sac_fly').sum()
    ok(f"m{m} PA",   int(len(g)) == int(r.plate_apps), len(g), r.plate_apps)
    ok(f"m{m} BA",   near(h / len(ab), r.ba), round(h/len(ab),3), r.ba)
    ok(f"m{m} OBP",  near((h+bb+hbp)/(len(ab)+bb+hbp+sf), r.obp), round((h+bb+hbp)/(len(ab)+bb+hbp+sf),3), r.obp)
    ok(f"m{m} BB%",  near(bb / len(g), r.bbrate), round(bb/len(g),3), r.bbrate)
    ok(f"m{m} K%",   near(k / len(g), r.krate),  round(k/len(g),3),  r.krate)
    ok(f"m{m} OPS == OBP+SLG", near(r.obp + r.slg, r.ops))

print("=" * 66); print("§3  approach panel — swing / chase / whiff / fpsr"); print("=" * 66)
for _, r in panel.iterrows():
    m = int(r.month); g = d26[d26.mo == m]
    sw = g.description.isin(SW).sum()
    ok(f"m{m} swing rate", near(sw / len(g), r.swing_rate), round(sw/len(g),3), r.swing_rate)
    o = g[g.zone > 9]
    ok(f"m{m} chase rate", near(o.description.isin(SW).sum() / len(o), r.chase_rate),
       round(o.description.isin(SW).sum()/len(o),3), r.chase_rate)
    ok(f"m{m} whiff rate", near(g.description.isin(WH).sum() / sw, r.whiff_rate),
       round(g.description.isin(WH).sum()/sw,3), r.whiff_rate)
    ows = o[o.description.isin(SW)]
    ok(f"m{m} OOZ whiff rate", near(ows.description.isin(WH).sum() / len(ows), r.ooz_whiff_rate),
       round(ows.description.isin(WH).sum()/len(ows),3), r.ooz_whiff_rate)
    fp = g[g.pitch_number == 1]
    ok(f"m{m} FPSR", near((len(fp) - (fp.type == 'B').sum()) / len(fp), r.fpsr),
       round((len(fp)-(fp.type=='B').sum())/len(fp),3), r.fpsr)
    fps = fp.description.isin(SW).sum()
    ok(f"m{m} first-pitch swing rate", near(fps / len(fp), r.srfp), round(fps/len(fp),3), r.srfp)

print("=" * 66); print("§4  AP-10 — the headline streak"); print("=" * 66)
seq = pa26.sort_values(['game_date','game_pk','at_bat_number'])
best = cur = 0; runs = []
for e in seq.events:
    if e in ('strikeout','strikeout_double_play'): cur = 0
    elif e in ('walk','intent_walk'): cur += 1; best = max(best, cur)
ok("longest walk run between strikeouts == 14", best == 14, best, 14)
st, en = pd.Timestamp(head['streak']['start']), pd.Timestamp(head['streak']['end'])
win = seq[(seq.game_date >= st) & (seq.game_date <= en)]
ok("window strikeouts == 0", int(win.events.isin(['strikeout','strikeout_double_play']).sum()) == 0,
   int(win.events.isin(['strikeout','strikeout_double_play']).sum()), 0)
ok("window walks == 14", int(win.events.isin(['walk','intent_walk']).sum()) == 14,
   int(win.events.isin(['walk','intent_walk']).sum()), 14)
ok("window spans 11 games (DPO said '11 game stretch')", int(win.game_pk.nunique()) == 11,
   int(win.game_pk.nunique()), 11)
ok("window PA == 46", int(len(win)) == int(head['streak']['pa']), len(win), head['streak']['pa'])
ok("streak-games receipt sums to 14 BB / 0 K",
   int(games.bb.sum()) == 14 and int(games.k.sum()) == 0, (int(games.bb.sum()), int(games.k.sum())), (14, 0))

print("=" * 66); print("§5  the DPO's OBP:K claim"); print("=" * 66)
allp = raw[(((raw.home_team=='PHI')&(raw.inning_topbot=='Bot'))|((raw.away_team=='PHI')&(raw.inning_topbot=='Top')))]
allp = allp[~allp.game_type.isin(['S','E'])]
allpa = allp[~allp.events.replace(np.nan,'NA').isin(NONPA)]
g = allpa.groupby(['player_name','game_year'])
agg = g.agg(pa=('events','size'),
            bb=('events', lambda x: x.isin(['walk','intent_walk']).sum()),
            k =('events', lambda x: x.isin(['strikeout','strikeout_double_play']).sum()),
            h =('events', lambda x: x.isin(['single','double','triple','home_run']).sum()),
            hbp=('events', lambda x: (x=='hit_by_pitch').sum()),
            sf =('events', lambda x: (x=='sac_fly').sum()),
            nab=('events', lambda x: x.isin(['walk','intent_walk','hit_by_pitch','sac_fly','sac_bunt']).sum())).reset_index()
agg['ab'] = agg.pa - agg.nab
agg['obp'] = (agg.h + agg.bb + agg.hbp) / (agg.ab + agg.bb + agg.hbp + agg.sf)
agg['krate'] = agg.k / agg.pa
agg = agg[agg.pa >= 50]
agg['obp_k'] = agg.obp / agg.krate
sm = agg[agg.player_name == SUBJ].obp_k.mean()
ok("context pool >= 200 hitter-seasons", len(agg) >= 200, len(agg))
ok("Stott OBP:K mean matches receipt", near(sm, head['context']['stott_obpk_mean'], 0.02),
   round(sm,3), head['context']['stott_obpk_mean'])
ok("Stott OBP:K exceeds the DPO's stated 3:2 (1.50)", sm > 1.5, round(sm,3), '>1.5')
ok("Stott above the Phillies-since-2015 median", sm > agg.obp_k.median(),
   round(sm,3), round(agg.obp_k.median(),3))

print("=" * 66); print("§6  governed-kernel defects (informational, not pass/fail)"); print("=" * 66)
aug = d26[d26.mo == 8]
fp8 = aug[aug.pitch_number == 1]
print(f"  D3 fpsr: August first-pitch balls = {(fp8.type=='B').sum()} of {len(fp8)} "
      f"-> group survives only because balls > 0")
zero_whiff = [int(m) for m in panel.month if d26[(d26.mo==m)].description.isin(WH).sum() == 0]
print(f"  D1 whiff_rate: months with zero whiffs (would vanish under governed inner merge): {zero_whiff or 'none'}")
print(f"  D4 nresults rounding: bbrate/krate from 3dp inputs vs from counts, August: "
      f"{round(panel[panel.month==8].bbrate.iat[0]/panel[panel.month==8].krate.iat[0],4)} vs "
      f"{round(float(panel[panel.month==8].bb_per_k.iat[0]),4)}")

print("=" * 66)
print(f"{_p} PASS / {_f} FAIL")
sys.exit(1 if _f else 0)
