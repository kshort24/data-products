"""
uc-pos-005 / dp_uc22 — independent verification (certification-agent input).
Recomputes headline numbers via code paths independent of the build script
and compares against the out/ receipts. Prints PASS/FAIL per check.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

MLB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT = MLB / "out"
STEM = "dp_uc22_harper_own_the_zone"
HARPER, HALF_X, BALL = 547180, 0.83, 0.25

checks = []
def check(name, got, want, tol=0.0015):
    ok = (abs(got - want) <= tol) if isinstance(want, float) else (got == want)
    checks.append((name, ok, got, want))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got={got} want={want}")

# -- independent load (concat then filter, different order than build) -----
raw = pd.concat([pd.read_parquet(MLB/f"data/phillies/phils_{y}.parquet") for y in range(2019, 2027)],
                ignore_index=True)
h = raw[(raw.batter == HARPER) & (raw.phillies_role == 'batting') & (raw.game_type == 'R')]
h = h.drop_duplicates(subset=['game_pk','at_bat_number','pitch_number'])
h26 = h[h.game_year == 2026]

res = pd.read_csv(OUT/f'{STEM}_results_by_season.csv')
r26 = res[res.season == 2026].iloc[0]

# 1-5: counting stats 2026, event-level recompute
ev26 = h26[h26.events.notna() & (h26.events != 'pickoff_1b')]
check('2026 PA', len(ev26), int(r26.plate_apps))
check('2026 HR', int((ev26.events == 'home_run').sum()), int(r26.hrs))
check('2026 BB', int((ev26.events == 'walk').sum()), int(r26.walks))
check('2026 K', int(ev26.events.isin(['strikeout','strikeout_double_play']).sum()), int(r26.strikeouts))
check('2026 hits', int(ev26.events.isin(['single','double','triple','home_run']).sum()), int(r26.hits))

# 6: wOBA 2026 via explicit weights (independent join)
w = pd.read_csv(MLB/'wOBA and FIP Constants.csv'); w26 = w[w.Season == 2026].iloc[0]
num = (w26.wBB*(ev26.events=='walk').sum() + w26.wHBP*(ev26.events=='hit_by_pitch').sum()
       + w26.w1B*(ev26.events=='single').sum() + w26.w2B*(ev26.events=='double').sum()
       + w26.w3B*(ev26.events=='triple').sum() + w26.wHR*(ev26.events=='home_run').sum())
check('2026 wOBA', round(num/len(ev26), 3), float(r26.woba))

# 7-8: barrel & hard-hit 2026 (batted-ball receipt)
bb = pd.read_csv(OUT/f'{STEM}_battedball_by_season.csv'); b26 = bb[bb.season == 2026].iloc[0]
bip26 = h26[h26.type == 'X']
check('2026 barrel%', round((bip26.launch_speed_angle == 6).mean(), 3), float(b26.barrel_rate))
check('2026 hard-hit%', round((bip26.launch_speed >= 95).mean(), 3), float(b26.hard_hit_rate))

# 9-12: OZ family 2026, independent region logic (masks not np.select)
loc = h26.dropna(subset=['plate_x','plate_z','sz_top','sz_bot'])
inz = (loc.plate_x.abs() <= HALF_X) & loc.plate_z.between(loc.sz_bot, loc.sz_top)
edge = (loc.plate_x.abs() >= HALF_X - BALL) | (loc.plate_z <= loc.sz_bot + BALL) | (loc.plate_z >= loc.sz_top - BALL)
band = (loc.plate_x.abs() <= HALF_X + BALL) & loc.plate_z.between(loc.sz_bot - BALL, loc.sz_top + BALL)
swings = loc.description.isin(['foul','foul_bunt','foul_tip','hit_into_play','missed_bunt',
                               'swinging_pitchout','swinging_strike','swinging_strike_blocked'])
si, so = inz & edge, band & ~inz
oz = pd.read_csv(OUT/f'{STEM}_oz_kpis_by_season.csv'); o26 = oz[oz.season == 2026].iloc[0]
check('2026 shadow_in pitches', int(si.sum()), int(o26.shadow_in_pitches))
check('2026 shadow_out pitches', int(so.sum()), int(o26.shadow_out_pitches))
check('2026 OZ-1 take', round(1 - swings[so].mean(), 3), float(o26.oz1_shadow_out_take))
check('2026 OZ-2 attack', round(swings[si].mean(), 3), float(o26.oz2_shadow_in_attack))

# 13: OZ-4 xwOBAcon on shadow_in BIP
sib = loc[si & (loc.type == 'X') & swings]
check('2026 OZ-4 xwOBAcon', round(sib.estimated_woba_using_speedangle.mean(), 3), float(o26.oz4_shadow_in_xwobacon))

# 14-15: platoon 2026 wOBA vs R / vs L from receipt vs event recompute
pl = pd.read_csv(OUT/f'{STEM}_platoon_results.csv')
for hand in ['R','L']:
    evh = ev26[ev26.p_throws == hand]
    numh = (w26.wBB*(evh.events=='walk').sum() + w26.wHBP*(evh.events=='hit_by_pitch').sum()
            + w26.w1B*(evh.events=='single').sum() + w26.w2B*(evh.events=='double').sum()
            + w26.w3B*(evh.events=='triple').sum() + w26.wHR*(evh.events=='home_run').sum())
    want = float(pl[(pl.season==2026) & (pl.p_throws==hand)].woba.iloc[0])
    check(f'2026 wOBA vs {hand}HP', round(numh/len(evh), 3), want)

# 16: monthly HR sum == season HR
mo = pd.read_csv(OUT/f'{STEM}_2026_monthly.csv')
check('2026 monthly HR sum', int(mo.hrs.sum()), int(r26.hrs))

# 17: shadow-band pitchlog receipt row count == si+so
log = pd.read_csv(OUT/f'{STEM}_2026_shadow_band_pitchlog.csv')
check('shadow-band log rows', len(log), int(si.sum() + so.sum()))

# 18: freshness
check('max game_date', str(h.game_date.max())[:10], '2026-07-12')

n_ok = sum(1 for _, ok, *_ in checks if ok)
print(f"\n=== VERIFICATION: {n_ok}/{len(checks)} PASS ===")
sys.exit(0 if n_ok == len(checks) else 1)
