"""
Independent verification for uc-pos-006 (dp_uc24) — Trea Turner 2026 review.
Recomputes headline KPIs from the parquet via a SEPARATE code path (no import
of the build's kernel) and asserts equality with the shipped CSV receipts and
the numbers quoted in the report. Prints a PASS/FAIL ledger.
Usage: python dp_uc24_verification.py [MLB_ROOT]
"""
import sys, pathlib
import numpy as np, pandas as pd

MLB = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
OUT = MLB / "out"; STEM = "dp_uc24_turner_2026_review"
TREA = 607208; ASB = "2026-07-16"
PK = ["game_pk","at_bat_number","pitch_number"]
checks = []
def ok(name, cond, got, exp):
    checks.append((name, bool(cond), got, exp))

# --- independent reload (different filtering order than build) ---
parts = [pd.read_parquet(MLB/"data/opponents/turner.parquet")]
for yr in range(2023,2027):
    d = pd.read_parquet(MLB/f"data/phillies/phils_{yr}.parquet")
    parts.append(d[(d.batter==TREA) & (d.phillies_role=="batting")])
m = pd.concat(parts, ignore_index=True)
m = m[(m.batter==TREA) & (m.game_type=="R")].drop_duplicates(subset=PK)
w = pd.read_csv(MLB/"wOBA and FIP Constants.csv")
m = m.drop(columns=[c for c in w.columns if c!="Season" and c in m.columns]).merge(
    w, left_on="game_year", right_on="Season", how="left")

def slash(df):
    ev = df.events
    PA = (~ev.replace(np.nan,'NA').isin(['NA','pickoff_1b'])).sum()
    AB = (~ev.replace(np.nan,'NA').isin(['NA','pickoff_1b','walk','intent_walk','hit_by_pitch','sac_fly','sac_bunt'])).sum()
    H = ev.isin(['single','double','triple','home_run']).sum()
    s1,s2,s3,hr = (ev=='single').sum(),(ev=='double').sum(),(ev=='triple').sum(),(ev=='home_run').sum()
    bb,hbp = (ev=='walk').sum(),(ev=='hit_by_pitch').sum()
    k = ev.isin(['strikeout','strikeout_double_play']).sum()
    obp=(H+bb+hbp)/PA; slg=(s1+2*s2+3*s3+4*hr)/AB
    wn = (bb*df.wBB.iloc[0]+hbp*df.wHBP.iloc[0]+s1*df.w1B.iloc[0]+s2*df.w2B.iloc[0]+s3*df.w3B.iloc[0]+hr*df.wHR.iloc[0])
    return dict(PA=PA, HR=hr, ba=round(H/AB,3), obp=round(obp,3), slg=round(slg,3),
                ops=round(obp+slg,3), woba=round(wn/PA,3), k=round(k/PA,3), bb=round(bb/PA,3))

res = pd.read_csv(OUT/f"{STEM}_results_by_season.csv").set_index("season")

# 1-4: PHI-era season slash independently vs receipt
for yr, exp_ops, exp_woba in [(2023,.773,.332),(2024,.804,.348),(2025,.807,.350),(2026,.691,.303)]:
    s = slash(m[m.game_year==yr])
    ok(f"{yr} OPS == receipt", abs(s['ops']-res.loc[yr,'ops'])<=.002, s['ops'], res.loc[yr,'ops'])
    ok(f"{yr} wOBA == receipt", abs(s['woba']-res.loc[yr,'woba'])<=.003, s['woba'], res.loc[yr,'woba'])

# 5: 2026 slash line matches report headline .246/.296/.396
s26 = slash(m[m.game_year==2026])
ok("2026 slash .246/.296/.396", (s26['ba'],s26['obp'],s26['slg'])==(.246,.296,.396), (s26['ba'],s26['obp'],s26['slg']), (.246,.296,.396))
ok("2026 HR == 14", s26['HR']==14, s26['HR'], 14)
ok("2026 K% == .224", abs(s26['k']-.224)<=.002, s26['k'], .224)

# 6: xwOBA 2026 (PA-level mean of estimated_woba, as get_stats) low & below wOBA
xw26 = round(m[m.game_year==2026].estimated_woba_using_speedangle.mean(),3)
phi_xw = [res.loc[y,'xwoba'] for y in (2023,2024,2025,2026)]
ok("2026 xwOBA == .295 receipt", abs(xw26-res.loc[2026,'xwoba'])<=.003, xw26, res.loc[2026,'xwoba'])
ok("2026 xwOBA lowest PHI era", res.loc[2026,'xwoba']==min(phi_xw), res.loc[2026,'xwoba'], "min")
ok("2026 wOBA >= xwOBA (not unlucky)", res.loc[2026,'woba']>=res.loc[2026,'xwoba'], res.loc[2026,'woba'], res.loc[2026,'xwoba'])

# 7: wRAA 2026 negative (below-average flag)
rc = pd.read_csv(OUT/f"{STEM}_wrc_by_season.csv").set_index("season")
ok("2026 wRAA < 0", rc.loc[2026,'wraa']<0, rc.loc[2026,'wraa'], "<0")
ok("2026 wRC/600 worst full season", rc.loc[2026,'wrc_600']==round(rc[rc.plate_apps>=200].wrc_600.min(),2), rc.loc[2026,'wrc_600'], "min")

# 8: engine intact — barrel up on 2025, hard-hit stable
bb = pd.read_csv(OUT/f"{STEM}_battedball_by_season.csv").set_index("season")
ok("2026 barrel > 2025 barrel", bb.loc[2026,'barrel_rate']>bb.loc[2025,'barrel_rate'], bb.loc[2026,'barrel_rate'], bb.loc[2025,'barrel_rate'])
ok("2026 hard-hit within 2pt of 2025", abs(bb.loc[2026,'hard_hit_rate']-bb.loc[2025,'hard_hit_rate'])<=.02, bb.loc[2026,'hard_hit_rate'], bb.loc[2025,'hard_hit_rate'])

# 9: shape broke — pulled-air / pull PHI-era low (report claim is "PHI-era low, lowest since 2020")
sp = pd.read_csv(OUT/f"{STEM}_spray_by_season.csv").set_index("season")
phi = sp[sp.index>=2023]
ok("2026 pulled-air PHI-era low", sp.loc[2026,'pulled_air_rate']==round(phi.pulled_air_rate.min(),3), sp.loc[2026,'pulled_air_rate'], "PHI-min")
ok("2026 pull rate PHI-era low", sp.loc[2026,'pull_rate']==round(phi.pull_rate.min(),3), sp.loc[2026,'pull_rate'], "PHI-min")
ok("honesty: 2020 pulled-air < 2026 (not a career low)", sp.loc[2020,'pulled_air_rate']<sp.loc[2026,'pulled_air_rate'], sp.loc[2020,'pulled_air_rate'], sp.loc[2026,'pulled_air_rate'])

# 10: offspeed hole
pg = pd.read_csv(OUT/f"{STEM}_pitchgroup_by_season.csv")
off26 = pg[(pg.season==2026)&(pg.pitch_group=='offspeed')].iloc[0]
ok("2026 offspeed wOBA == .184", abs(off26.woba-.184)<=.002, round(off26.woba,3), .184)
ok("2026 offspeed K% >= .35", off26.krate>=.35, round(off26.krate,3), ">=.35")

# 11: July surge & post-ASB
mo = pd.read_csv(OUT/f"{STEM}_2026_monthly.csv").set_index("month")
ok("July OPS == .980", abs(mo.loc['2026-07','ops']-.980)<=.002, mo.loc['2026-07','ops'], .980)
ok("July PA == 62", mo.loc['2026-07','plate_apps']==62, mo.loc['2026-07','plate_apps'], 62)
half = pd.read_csv(OUT/f"{STEM}_2026_half_split.csv").set_index("half")
post = m[(m.game_year==2026) & (pd.to_datetime(m.game_date)>ASB)]
ok("post-ASB games == 3", post.game_pk.nunique()==3, post.game_pk.nunique(), 3)

# 12: trajectory hero endpoints == season OPS
run = pd.read_csv(OUT/f"{STEM}_running_ops_by_game.csv")
for yr in (2023,2024,2025,2026):
    endp = run[run.game_year==yr].sort_values('gi').iloc[-1]
    ok(f"traj {yr} endpoint OPS == season OPS", abs(endp.ops_std-res.loc[yr,'ops'])<=.002, round(endp.ops_std,3), res.loc[yr,'ops'])

# 13: DQ integrity
ok("0 duplicate pitch keys", m.duplicated(subset=PK).sum()==0, int(m.duplicated(subset=PK).sum()), 0)
ok("single entity id", m.batter.nunique()==1, m.batter.nunique(), 1)
ok("freshness 2026-07-20", str(m.game_date.max())=="2026-07-20", str(m.game_date.max()), "2026-07-20")

# ---- report ----
npass = sum(c[1] for c in checks); n = len(checks)
print(f"\n{'='*64}\nVERIFICATION LEDGER — dp_uc24 · uc-pos-006 · Trea Turner 2026\n{'='*64}")
for name, passed, got, exp in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name:44s} got={got} exp={exp}")
print(f"{'='*64}\nRESULT: {npass}/{n} PASS — {'CERTIFY READY' if npass==n else 'DO NOT CERTIFY'}\n{'='*64}")
sys.exit(0 if npass==n else 1)
