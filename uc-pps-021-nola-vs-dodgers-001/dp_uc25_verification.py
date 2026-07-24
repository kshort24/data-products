"""
Independent verification for uc-pps-021 (dp_uc25) — Nola vs Dodgers advance scout.
Recomputes headline KPIs from the parquet via a SEPARATE code path (no import of the
build's kernel) and asserts equality with the shipped CSV receipts and the numbers
quoted in the report. Prints a PASS/FAIL ledger.
Usage: python dp_uc25_verification.py [MLB_ROOT]
"""
import sys, glob, pathlib
import numpy as np, pandas as pd

MLB = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
OUT = MLB / "out"
NOLA = 605400
PK = ["game_pk", "at_bat_number", "pitch_number"]
SWINGS = ["foul","foul_bunt","foul_tip","hit_into_play","missed_bunt","swinging_pitchout",
          "swinging_strike","swinging_strike_blocked"]
WHIFFS = ["foul_tip","missed_bunt","swinging_pitchout","swinging_strike","swinging_strike_blocked"]
checks = []
def ok(name, cond, got, exp):
    checks.append((name, bool(cond), got, exp))

# --- independent reload: game_type filter FIRST, then entity (different order than build) ---
parts = []
for f in sorted(glob.glob(str(MLB / "data/phillies/phils_*.parquet"))):
    d = pd.read_parquet(f)
    d = d[d.game_type == "R"]
    d = d[(d.phillies_role == "pitching") & (d.pitcher == NOLA)]
    if len(d): parts.append(d)
m = pd.concat(parts, ignore_index=True).drop_duplicates(subset=PK)
for c in ["plate_x","plate_z","sz_top","sz_bot","release_speed","launch_speed","strikes","zone","pitch_number"]:
    m[c] = pd.to_numeric(m[c], errors="coerce")
m["game_date"] = pd.to_datetime(m.game_date)
w = pd.read_csv(MLB / "wOBA and FIP Constants.csv")
m = m.drop(columns=[c for c in w.columns if c != "Season" and c in m.columns]).merge(
    w, left_on="game_year", right_on="Season", how="left")

def slash(df):
    ev = df.events
    PA = (~ev.replace(np.nan,'NA').isin(['NA','pickoff_1b'])).sum()
    AB = (~ev.replace(np.nan,'NA').isin(['NA','pickoff_1b','walk','intent_walk','hit_by_pitch','sac_fly','sac_bunt'])).sum()
    H = ev.isin(['single','double','triple','home_run']).sum()
    s1,s2,s3,hr = (ev=='single').sum(),(ev=='double').sum(),(ev=='triple').sum(),(ev=='home_run').sum()
    bb,hbp = (ev=='walk').sum(),(ev=='hit_by_pitch').sum()
    k = ev.isin(['strikeout','strikeout_double_play']).sum()
    # per-row wOBA weights (each event weighted by ITS OWN season) — correct for
    # multi-season H2H samples; identical to single-weight for one-season groups.
    wn = (((ev=='walk')*df.wBB + (ev=='hit_by_pitch')*df.wHBP + (ev=='single')*df.w1B
           + (ev=='double')*df.w2B + (ev=='triple')*df.w3B + (ev=='home_run')*df.wHR)).sum()
    slg = (s1+2*s2+3*s3+4*hr)/AB
    return dict(PA=int(PA), HR=int(hr), BB=int(bb), K=int(k),
                slg=round(slg,3), woba=round(wn/PA,3),
                krate=round(k/PA,3), bbrate=round(bb/PA,3), hrrate=round(hr/PA,3))

def xwobacon(df):
    b = df[df.type=="X"]
    return round(b.estimated_woba_using_speedangle.mean(), 3)
def fpsr(df):
    fp = df[df.pitch_number==1]
    return round((fp.type!="B").sum()/len(fp), 3)
def putaway(df):
    two = df[df.strikes==2]
    k = df.events.isin(['strikeout','strikeout_double_play']).sum()
    return round(k/len(two), 3)
def air_gb(df):
    bip = df[df.type=="X"]
    gb = (bip.bb_type=="ground_ball").sum()
    air = bip.bb_type.isin(["fly_ball","line_drive","popup"]).sum()
    return round(gb/len(bip),3), round(air/len(bip),3)

m26 = m[m.game_year==2026]

# ---- receipts ----
tr = pd.read_csv(OUT/"dp_uc25_nola_season_trend.csv").set_index("game_year")
ps = pd.read_csv(OUT/"dp_uc25_process_by_stand_2026.csv").set_index("stand")
cq = pd.read_csv(OUT/"dp_uc25_contact_quality_by_year.csv").set_index("game_year")
pa = pd.read_csv(OUT/"dp_uc25_process_abs_by_year.csv").set_index("game_year")
rc = pd.read_csv(OUT/"dp_uc25_recency_split.csv")
h2h = pd.read_csv(OUT/"dp_uc25_dodgers_h2h.csv")

# 1-3: 2026 season slash independent vs receipt + report headline .358/.509/5.1%
s26 = slash(m26)
ok("2026 wOBA .358 (indep==receipt)", abs(s26['woba']-tr.loc[2026,'woba'])<=.003 and s26['woba']==.358, s26['woba'], .358)
ok("2026 SLG .509", s26['slg']==.509, s26['slg'], .509)
ok("2026 HR-rate .051 & career-high", s26['hrrate']==.051 and tr.loc[2026,'hr_rate']==tr.hr_rate.max(), s26['hrrate'], .051)
ok("2026 K% .238 steady", s26['krate']==.238, s26['krate'], .238)
ok("2026 BB% .075, highest since 2019 (2019 was higher)",
   s26['bbrate']==.075 and tr.loc[2026,'bbrate']==tr.loc[tr.index>=2020,'bbrate'].max() and tr.loc[2019,'bbrate']>tr.loc[2026,'bbrate'],
   (s26['bbrate'], float(tr.loc[2019,'bbrate'])), ".075 / 2019=.091")
ok("2026 GS==20, PA==453", m26.game_pk.nunique()==20 and s26['PA']==453, (int(m26.game_pk.nunique()),s26['PA']), (20,453))

# 4-5: xwOBAcon correct (BIP mean) and stable; matches receipt
xw26 = xwobacon(m26)
ok("2026 xwOBAcon .384 (indep==receipt)", xw26==.384 and abs(xw26-tr.loc[2026,'xwobacon'])<=.002, xw26, .384)
ok("xwOBAcon field >99% populated on BIP", m[m.type=='X'].estimated_woba_using_speedangle.notna().mean()>0.99,
   round(m[m.type=='X'].estimated_woba_using_speedangle.notna().mean(),3), ">0.99")

# 6-10: THE lefty story — identical contact quality, walk-driven gap
L = m26[m26.stand=="L"]; R = m26[m26.stand=="R"]
sL, sR = slash(L), slash(R)
xwL, xwR = xwobacon(L), xwobacon(R)
ok("L/R wOBA both ~.36 (receipt)", abs(ps.loc['L','woba']-.361)<=.002 and abs(ps.loc['R','woba']-.353)<=.002, (ps.loc['L','woba'],ps.loc['R','woba']), (.361,.353))
ok("xwOBAcon identical by side (|L-R|<=.02)", abs(xwL-xwR)<=.02 and xwL==.382 and xwR==.387, (xwL,xwR), (.382,.387))
ok("BB% leak: L (.107) >> R (.028)", sL['bbrate']==.107 and sR['bbrate']==.028, (sL['bbrate'],sR['bbrate']), (.107,.028))
ok("1P-strike gap: L .588 < R .735", fpsr(L)==.588 and fpsr(R)==.735, (fpsr(L),fpsr(R)), (.588,.735))
ok("putaway gap: L .186 < R .231 (receipt)", ps.loc['L','putaway_rate']==.186 and ps.loc['R','putaway_rate']==.231, (ps.loc['L','putaway_rate'],ps.loc['R','putaway_rate']), (.186,.231))

# 11-13: contact-quality engine (career-low GB, career-high air)
gb26, air26 = air_gb(m26)
ok("2026 GB .403 (indep==receipt)", gb26==.403 and cq.loc[2026,'gb_rate']==.403, gb26, .403)
ok("2026 air .597 & career-high", air26==.597 and cq.loc[2026,'air_rate']==cq.air_rate.max(), air26, .597)
ok("2026 GB career-low (2015-26)", cq.loc[2026,'gb_rate']==cq.gb_rate.min(), cq.loc[2026,'gb_rate'], "min")

# 14-16: ABS re-test holds
ok("edge .370 ~ career norm (.36-.41)", pa.loc[2026,'edge_rate']==.370 and .36<=pa.loc[2026,'edge_rate']<=.41, pa.loc[2026,'edge_rate'], .370)
ok("OOZ called-strike decade decline (2026 < 2015)", pa.loc[2026,'ooz_called_strike_rate']==.034 and pa.loc[2026,'ooz_called_strike_rate']<pa.loc[2015,'ooz_called_strike_rate'], pa.loc[2026,'ooz_called_strike_rate'], "<2015")
ok("chase-up still high (.311)", pa.loc[2026,'chase_up_rate']==.311, pa.loc[2026,'chase_up_rate'], .311)

# 17-20: recency — trend up but 7/16 rough
last3 = m26[m26.game_date > pd.Timestamp("2026-07-04")]
s3 = slash(last3)
ok("last-3 starts == 3 games", last3.game_pk.nunique()==3, int(last3.game_pk.nunique()), 3)
ok("last-3 wOBA .313 (indep==receipt)", s3['woba']==.313 and abs(rc[rc.segment.str.startswith('last-3')].woba.iloc[0]-.313)<=.002, s3['woba'], .313)
g0705 = m26[m26.game_date==pd.Timestamp("2026-07-05")]
s0705 = slash(g0705)
ok("7/05 KC: 0 BB, 0 HR, 7 K (the plan worked)", (s0705['BB'],s0705['HR'],s0705['K'])==(0,0,7), (s0705['BB'],s0705['HR'],s0705['K']), (0,0,7))
g0716 = m26[m26.game_date==pd.Timestamp("2026-07-16")]
ok("7/16 NYM: 3 HR (the clunker)", slash(g0716)['HR']==3, slash(g0716)['HR'], 3)

# 21-25: Dodgers H2H — independent recompute vs receipt
ab_last = m.sort_values(PK).groupby(["game_pk","at_bat_number"], as_index=False).last()
def bname(des):
    if not isinstance(des,str) or not des: return None
    t = des.replace(".","").split(); return " ".join(t[:2]) if len(t)>=2 else None
ab_last["bn"] = ab_last.des.map(bname)
nm = ab_last.dropna(subset=["bn"]).groupby("batter")["bn"].agg(lambda s: s.mode().iat[0]).to_dict()
def hitter(name):
    bid = next((b for b,n in nm.items() if n.lower()==name.lower()), None)
    return slash(m[m.batter==bid]) if bid is not None else None
ok("H2H resolved 7/7 named hitters", len(h2h)==7, len(h2h), 7)
betts = hitter("Mookie Betts")
ok("Betts 23 PA / .465 / 2 HR (indep)", betts and betts['PA']==23 and betts['woba']==.465 and betts['HR']==2, betts and (betts['PA'],betts['woba'],betts['HR']), (23,.465,2))
free = hitter("Freddie Freeman")
ok("Freeman 86 PA (the only real sample)", free and free['PA']==86, free and free['PA'], 86)
muncy = hitter("Max Muncy")
ok("Muncy 11 K in 25 PA (owned)", muncy and muncy['K']==11 and muncy['PA']==25, muncy and (muncy['K'],muncy['PA']), (11,25))
ok("all 7 H2H are small samples (<=86 PA)", h2h.PA.max()<=86 and h2h.PA.min()>=8, (int(h2h.PA.min()),int(h2h.PA.max())), "8..86")

# 26-28: DQ integrity
ok("single entity id (605400)", m.pitcher.nunique()==1 and m.pitcher.iloc[0]==NOLA, int(m.pitcher.iloc[0]), NOLA)
ok("0 duplicate pitch keys", m.duplicated(subset=PK).sum()==0, int(m.duplicated(subset=PK).sum()), 0)
ok("freshness 2026-07-16 (last start)", str(m.game_date.max().date())=="2026-07-16", str(m.game_date.max().date()), "2026-07-16")

# ---- ledger ----
npass = sum(c[1] for c in checks); n = len(checks)
print(f"\n{'='*70}\nVERIFICATION LEDGER — dp_uc25 · uc-pps-021 · Aaron Nola vs LAD 2026-07-22\n{'='*70}")
for name, passed, got, exp in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name:46s} got={got} exp={exp}")
print(f"{'='*70}\nRESULT: {npass}/{n} PASS — {'CERTIFY READY' if npass==n else 'DO NOT CERTIFY'}\n{'='*70}")
sys.exit(0 if npass==n else 1)
