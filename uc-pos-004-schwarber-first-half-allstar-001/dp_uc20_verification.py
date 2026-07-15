"""
dp_uc20 VERIFICATION — independent spot-recompute of report headline claims.
Deliberately avoids the get_stats kernel: raw event counting + direct wOBA
arithmetic, so agreement is evidence rather than tautology.
Claims checked (report §): PA/HR/BA/OBP/SLG/wOBA 2026 (§2), wRC (§3),
P/PA (§5), in-zone swing (§5), pulled-air (§5), even-or-behind wOBA (§5),
HR log summary (§1), vs-LHP wOBA (§5).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

MLB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
KEY = ["game_pk", "at_bat_number", "pitch_number"]

df = pd.read_parquet(MLB / "data/phillies/phils_2026.parquet")
s = df[(df.phillies_role == "batting") & (df.batter == 656941) & (df.game_type == "R")]
s = s.drop_duplicates(subset=KEY)

ev = s[s.events.notna() & (s.events != "") & (s.events != "pickoff_1b")]
pa = len(ev)
hr = (ev.events == "home_run").sum()
h = ev.events.isin(["single", "double", "triple", "home_run"]).sum()
ab = (~ev.events.isin(["walk", "intent_walk", "hit_by_pitch", "sac_fly", "sac_bunt"])).sum()
bb, hbp = (ev.events == "walk").sum(), (ev.events == "hit_by_pitch").sum()
tb = (ev.events == "single").sum() + 2*(ev.events == "double").sum() \
   + 3*(ev.events == "triple").sum() + 4*hr

w = pd.read_csv(MLB / "wOBA and FIP Constants.csv").set_index("Season").loc[2026]
num = (bb*w.wBB + hbp*w.wHBP + (ev.events=="single").sum()*w.w1B
       + (ev.events=="double").sum()*w.w2B + (ev.events=="triple").sum()*w.w3B + hr*w.wHR)
woba = num / pa
wraa = (woba - w.wOBA) / w.wOBAScale * pa
wrc = wraa + w["R/PA"] * pa

SWINGS = {'foul','foul_bunt','foul_tip','hit_into_play','missed_bunt',
          'swinging_pitchout','swinging_strike','swinging_strike_blocked'}
inz = s[s.zone <= 9]
zsw = inz.description.isin(SWINGS).mean()

bip = s[(s.type == "X") & s.hc_x.notna() & s.hc_y.notna()].copy()
bip["spray"] = np.degrees(np.arctan2(bip.hc_x - 125.42, 198.27 - bip.hc_y))
bip["pulled_air"] = (bip.spray > 15) & bip.bb_type.isin(["fly_ball", "line_drive"])  # LHB
pa_rate = bip.pulled_air.mean()

eb = ev[(ev.strikes < 2) & (ev.balls >= ev.strikes)]  # even or behind pitcher's view? report def: not two-strike, balls>strikes = ahead
# report count_state: two_strike (strikes==2), ahead (balls>strikes), else even_or_behind
eob = ev[(ev.strikes != 2) & ~(ev.balls > ev.strikes)]
num_eob = ((eob.events=="walk").sum()*w.wBB + (eob.events=="hit_by_pitch").sum()*w.wHBP
           + (eob.events=="single").sum()*w.w1B + (eob.events=="double").sum()*w.w2B
           + (eob.events=="triple").sum()*w.w3B + (eob.events=="home_run").sum()*w.wHR)
woba_eob = num_eob / len(eob)

lhp = ev[ev.p_throws == "L"]
num_l = ((lhp.events=="walk").sum()*w.wBB + (lhp.events=="hit_by_pitch").sum()*w.wHBP
         + (lhp.events=="single").sum()*w.w1B + (lhp.events=="double").sum()*w.w2B
         + (lhp.events=="triple").sum()*w.w3B + (lhp.events=="home_run").sum()*w.wHR)

hrl = s[s.events == "home_run"]

checks = [
    ("PA 2026", 415, pa),
    ("HR 2026", 32, int(hr)),
    ("BA", 0.254, round(h/ab, 3)),
    ("OBP", 0.359, round((h+bb+hbp)/pa, 3)),
    ("SLG", 0.558, round(tb/ab, 3)),
    ("wOBA", 0.391, round(woba, 3)),
    ("wRC", 74.3, round(wrc, 1)),
    ("P/PA", 4.301, round(len(s)/pa, 3)),
    ("In-zone swing", 0.675, round(zsw, 3)),
    ("Pulled-air rate", 0.320, round(pa_rate, 3)),
    ("Even-or-behind wOBA", 0.663, round(woba_eob, 3)),
    ("vs LHP wOBA", 0.415, round(num_l/len(lhp), 3)),
    ("vs LHP PA", 159, len(lhp)),
    ("HR avg dist", 403.6, round(hrl.hit_distance_sc.mean(), 1)),
    ("HR max dist", 460, int(hrl.hit_distance_sc.max())),
    ("HR avg EV", 106.6, round(hrl.launch_speed.mean(), 1)),
    ("Games appeared", 93, s.game_pk.nunique()),
    ("Max game_date", "2026-07-12", str(s.game_date.max())[:10]),
]
fails = 0
for name, claimed, got in checks:
    ok = str(claimed) == str(got) or (isinstance(claimed, float) and abs(claimed - float(got)) < 0.0015)
    fails += (not ok)
    print(f"{'PASS' if ok else 'FAIL':4} | {name:22} | report {claimed} | recomputed {got}")
print(f"\n{len(checks)-fails}/{len(checks)} PASS")
sys.exit(1 if fails else 0)
