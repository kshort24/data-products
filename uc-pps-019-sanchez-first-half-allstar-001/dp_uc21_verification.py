"""
uc-pps-019 verification harness (dp_uc20 precedent).
Independent recompute of headline report claims. Deliberately avoids the
locked get_stats/nresults kernel — wOBA is recomputed from Statcast's own
woba_value/woba_denom (different method), counting stats from raw event
masks — so agreement is evidence, not tautology.
"""
import os
import numpy as np
import pandas as pd

PHIL = os.environ.get("MLB_DATA_ROOT",
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies")
PID = 650911
checks = []

def check(name, got, want, tol=0.0):
    ok = (abs(got - want) <= tol) if isinstance(want,(int,float)) else (got == want)
    checks.append((name, got, want, "PASS" if ok else "FAIL"))

def load(yr):
    d = pd.read_parquet(os.path.join(PHIL, f"phils_{yr}.parquet"))
    d = d[(d.phillies_role=="pitching")&(d.pitcher==PID)&(d.game_type=="R")]
    return d.drop_duplicates(["game_pk","at_bat_number","pitch_number"])

d26, d25 = load(2026), load(2025)
def last(df):
    return (df.sort_values(["game_pk","at_bat_number","pitch_number"])
              .groupby(["game_pk","at_bat_number"],as_index=False).last())
l26, l25 = last(d26), last(d25)
pa26 = l26[~l26.events.replace(np.nan,"NA").isin(["NA","pickoff_1b"])]
pa25 = l25[~l25.events.replace(np.nan,"NA").isin(["NA","pickoff_1b"])]

# 1. volume
check("2026 starts", d26.game_pk.nunique(), 20)
check("2026 pitches", len(d26), 1903)
check("2026 PA", len(pa26), 525)

# 2. counting stats
check("2026 K", int(pa26.events.isin(["strikeout","strikeout_double_play"]).sum()), 144)
check("2026 BB (incl IBB)", int(pa26.events.isin(["walk","intent_walk"]).sum()), 25)
check("2026 HR", int((pa26.events=="home_run").sum()), 12)
check("2025 HR", int((pa25.events=="home_run").sum()), 12)

# 3. outs / IP / RA9 (independent: same event map re-declared, run math re-done)
OUTS = {"field_out":1,"strikeout":1,"force_out":1,"sac_fly":1,"sac_bunt":1,
    "fielders_choice_out":1,"fielders_choice":1,"other_out":1,
    "grounded_into_double_play":2,"double_play":2,"strikeout_double_play":2,
    "sac_fly_double_play":2,"sac_bunt_double_play":2,"triple_play":3,
    "caught_stealing_2b":1,"caught_stealing_3b":1,"caught_stealing_home":1,
    "pickoff_caught_stealing_2b":1,"pickoff_caught_stealing_3b":1,
    "pickoff_caught_stealing_home":1,"pickoff_1b":1,"pickoff_2b":1,"pickoff_3b":1}
outs26 = int(l26.events.map(OUTS).fillna(0).sum())
runs26 = int((l26.post_bat_score - l26.bat_score).clip(lower=0).sum())
check("2026 outs", outs26, 378)
check("2026 RA9", round(runs26/(outs26/3)*9,2), 2.79, tol=0.01)

# 4. xwOBA (raw mean, both years)
check("2026 xwOBA", round(d26.estimated_woba_using_speedangle.mean(),3), 0.279, tol=0.001)
check("2025 xwOBA", round(d25.estimated_woba_using_speedangle.mean(),3), 0.279, tol=0.001)

# 5. wOBA via Statcast woba_value/woba_denom (DIFFERENT method vs kernel; tol .010)
w26 = pd.to_numeric(pa26.woba_value,errors="coerce").sum()/pd.to_numeric(pa26.woba_denom,errors="coerce").sum()
w25 = pd.to_numeric(pa25.woba_value,errors="coerce").sum()/pd.to_numeric(pa25.woba_denom,errors="coerce").sum()
check("2026 wOBA (statcast method vs .292)", round(float(w26),3), 0.292, tol=0.010)
check("2025 wOBA (statcast method vs .263)", round(float(w25),3), 0.263, tol=0.010)

# 6. QR-1 (independent boolean math)
q26 = float((pa26.pitch_number<=3).mean()); q25 = float((pa25.pitch_number<=3).mean())
check("QR-1 2026", round(q26,3), 0.503, tol=0.001)
check("QR-1 2025", round(q25,3), 0.522, tol=0.001)

# 7. quick-bucket HR concentration
hr_quick = int(((pa26.events=="home_run")&(pa26.pitch_number<=3)).sum())
check("HR in <=3-pitch PAs, 2026", hr_quick, 10)

# 8. streak receipt: recompute max consecutive outs w/o on-mound run
seq = l26.sort_values(["game_date","game_pk","at_bat_number"])
best=cur=0
for _,r in seq.iterrows():
    if max((r.post_bat_score or 0)-(r.bat_score or 0),0) > 0: best=max(best,cur); cur=0
    else: cur += OUTS.get(r.events,0)
best=max(best,cur)
check("SL-1 streak outs", best, 155)

# 9. slider whiff 2026 (independent mask)
SW=["foul","foul_bunt","foul_tip","hit_into_play","missed_bunt",
    "swinging_pitchout","swinging_strike","swinging_strike_blocked"]
WH=["foul_tip","missed_bunt","swinging_pitchout","swinging_strike","swinging_strike_blocked"]
sl = d26[d26.pitch_name=="Slider"]
check("Slider whiff 2026", round(sl[sl.description.isin(WH)].shape[0]/sl[sl.description.isin(SW)].shape[0],3), 0.445, tol=0.001)
ch = d26[d26.pitch_name=="Changeup"]
check("Changeup xwOBA 2026", round(ch.estimated_woba_using_speedangle.mean(),3), 0.193, tol=0.001)

# 10. chase rate 2026 (independent)
z = pd.to_numeric(d26.zone,errors="coerce")
ooz = d26[z>9]
check("Chase rate 2026", round(ooz[ooz.description.isin(SW)].shape[0]/len(ooz),3), 0.386, tol=0.001)

# 11. KC start
kc = d26[(d26.game_date.astype(str).str[:10]=="2026-07-06")]
lkc = last(kc)
check("KC outs", int(lkc.events.map(OUTS).fillna(0).sum()), 9)
check("KC runs", int((lkc.post_bat_score-lkc.bat_score).clip(lower=0).sum()), 9)

# 12. staff QR median (independent pass over full 2026 staff)
d = pd.read_parquet(os.path.join(PHIL,"phils_2026.parquet"))
d = d[(d.phillies_role=="pitching")&(d.game_type=="R")].drop_duplicates(
    ["game_pk","at_bat_number","pitch_number"])
meds=[]
for pid, g in d.groupby("pitcher"):
    if len(g)<500: continue
    lg = last(g); pg = lg[~lg.events.replace(np.nan,"NA").isin(["NA","pickoff_1b"])]
    meds.append((pg.pitch_number<=3).mean())
check("staff QR-1 median (>=500p)", round(float(np.median(meds)),3), 0.426, tol=0.001)

out = pd.DataFrame(checks, columns=["claim","recomputed","report","result"])
print(out.to_string(index=False))
n_pass = (out.result=="PASS").sum()
print(f"\n{n_pass}/{len(out)} PASS")
out.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
    "dp_uc21_verification_results.csv"), index=False)
