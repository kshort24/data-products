"""
dp_uc39_verification.py — INDEPENDENT verification harness for uc-pps-028.

Rule: every number that appears in the reader report must be recomputable here
from the raw parquet WITHOUT importing the build module's derived logic, and
must match the receipt CSV the report cites. A number that only exists in the
build script is not verified — it is asserted.

Method:
  * re-read phils_2025/phils_2026 from scratch,
  * re-derive each published figure with independently written expressions
    (different code path from the build: boolean masks / direct sums rather
    than the get_stats pipeline wherever the metric allows it),
  * compare to the receipt CSV,
  * and separately re-open every receipt to confirm the report's cited values.

Exit code 0 only when 100% of checks pass.
"""
from __future__ import annotations
import os, sys, glob
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "out")
_C = [os.environ.get("MLB_DATA_ROOT",""), os.path.join(HERE,"data","phillies"),
      os.path.expanduser("~/mnt/MLB/data/phillies"),
      r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies"]
PHIL = next((p for p in _C if p and os.path.isdir(p)), None)
if PHIL is None: sys.exit("FATAL: data plane not mounted — cannot verify.")
REPO = os.path.dirname(os.path.dirname(PHIL))
WOBA = next((p for p in [os.environ.get("MLB_WOBA_CSV",""),
             os.path.join(REPO,"wOBA and FIP Constants.csv")] if p and os.path.isfile(p)), None)

LUZARDO, XW, ASB = 666200, "estimated_woba_using_speedangle", "2026-07-09"
BREAK = "2026-05-01"
SWINGS = ["foul","foul_bunt","foul_tip","hit_into_play","missed_bunt",
          "swinging_pitchout","swinging_strike","swinging_strike_blocked"]
WHIFFS = ["foul_tip","missed_bunt","swinging_pitchout","swinging_strike","swinging_strike_blocked"]

PASS = FAILN = 0
def chk(label, got, want, tol=0.0015):
    global PASS, FAILN
    if isinstance(want, str) or isinstance(got, str):
        ok = str(got) == str(want); d = ""
    elif want is None or (isinstance(want, float) and np.isnan(want)):
        ok = got is None or (isinstance(got, float) and np.isnan(got)); d = ""
    else:
        d = float(got) - float(want); ok = abs(d) <= tol
    PASS += ok; FAILN += (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label:<62} got={got!r:>18} want={want!r:>18}"
          + (f"  d={d:+.4f}" if d != "" else ""))
    return ok

def load(years=(2025,2026)):
    fs=[]
    for y in years:
        d = pd.read_parquet(os.path.join(PHIL, f"phils_{y}.parquet"))
        fs.append(d[(d.phillies_role=="pitching") & (d.game_type=="R")])
    r = pd.concat(fs, ignore_index=True).drop_duplicates(["game_pk","at_bat_number","pitch_number"])
    for c in ["zone","strikes","pitch_number","launch_speed","bat_score","post_bat_score",
              "n_thruorder_pitcher","at_bat_number","inning",XW,"release_speed"]:
        if c in r.columns: r[c]=pd.to_numeric(r[c],errors="coerce")
    r["game_date"]=pd.to_datetime(r.game_date).dt.strftime("%Y-%m-%d")
    r["opp"]=np.where(r.home_team.eq("PHI"), r.away_team, r.home_team)
    if WOBA:
        w=pd.read_csv(WOBA); r=r.drop(columns=[c for c in w.columns if c!="Season" and c in r.columns])
        r=r.merge(w,left_on="game_year",right_on="Season",how="left")
    return r

def rc(name): return pd.read_csv(os.path.join(OUT, f"dp_uc39_{name}.csv"))

def palast(d):
    return d.sort_values(["game_pk","at_bat_number","pitch_number"]).groupby(
        ["game_pk","at_bat_number"], as_index=False).last()

# --- independent metric expressions (deliberately NOT the build's pipeline) --
def i_woba(d):
    L = palast(d)
    pa = (~L.events.fillna("NA").isin(["NA","pickoff_1b"])).sum()
    num = (L.loc[L.events=="walk","wBB"].sum() + L.loc[L.events=="hit_by_pitch","wHBP"].sum()
         + L.loc[L.events=="single","w1B"].sum() + L.loc[L.events=="double","w2B"].sum()
         + L.loc[L.events=="triple","w3B"].sum() + L.loc[L.events=="home_run","wHR"].sum())
    return num/pa, int(pa)
def i_xwoba(d):
    v = d[XW].dropna(); return float(v.sum()/len(v)), int(len(v))
def i_whiff(d):
    sw = d.description.isin(SWINGS).sum(); wh = d.description.isin(WHIFFS).sum()
    return wh/sw
def i_chase(d):
    ooz = (d.zone>9).sum(); ch = ((d.zone>9)&d.description.isin(SWINGS)).sum()
    return ch/ooz, (len(d)-ooz)/len(d)
def i_csw(d):
    return (d.description.eq("called_strike")|d.description.isin(WHIFFS)).sum()/len(d)
def i_fps(d):
    fp = d[d.pitch_number==1]; return (fp.type!="B").sum()/len(fp)
def i_putaway(d):
    two = (d.strikes==2).sum()
    k = d.events.isin(["strikeout","strikeout_double_play"]).sum()
    return k/two
def i_hardhit(d):
    b = d[d.type=="X"]; return ((b.launch_speed>=95).sum())/len(b)
def i_krate(d):
    L=palast(d); pa=(~L.events.fillna("NA").isin(["NA","pickoff_1b"])).sum()
    return L.events.isin(["strikeout","strikeout_double_play"]).sum()/pa
def i_bbrate(d):
    L=palast(d); pa=(~L.events.fillna("NA").isin(["NA","pickoff_1b"])).sum()
    return (L.events=="walk").sum()/pa
OUTS={"field_out":1,"strikeout":1,"force_out":1,"sac_fly":1,"sac_bunt":1,"fielders_choice_out":1,
 "fielders_choice":1,"other_out":1,"grounded_into_double_play":2,"double_play":2,
 "strikeout_double_play":2,"sac_fly_double_play":2,"sac_bunt_double_play":2,"triple_play":3,
 "caught_stealing_2b":1,"caught_stealing_3b":1,"caught_stealing_home":1,
 "pickoff_caught_stealing_2b":1,"pickoff_caught_stealing_3b":1,"pickoff_caught_stealing_home":1,
 "pickoff_1b":1,"pickoff_2b":1,"pickoff_3b":1}
def i_outs_runs(d):
    L=palast(d)
    return int(L.events.map(OUTS).fillna(0).sum()), int((L.post_bat_score-L.bat_score).clip(lower=0).sum())

def main():
    print("\n" + "="*84)
    print("dp_uc39 VERIFICATION — uc-pps-028 · Luzardo consistency audit + ARI pre-scout")
    print("="*84)
    staff = load()
    lz = staff[staff.pitcher==LUZARDO]
    lz25, lz26 = lz[lz.game_year==2025], lz[lz.game_year==2026]
    h1, h2 = lz26[lz26.game_date<=ASB], lz26[lz26.game_date>ASB]

    print("\n-- 1. entity lock & frame shape ---------------------------------------------")
    chk("distinct pitcher ids in locked frame", int(lz.pitcher.nunique()), 1)
    chk("resolved player_name", lz.player_name.dropna().unique()[0], "Luzardo, Jesús")
    chk("duplicate pitch rows", int(lz.duplicated(['game_pk','at_bat_number','pitch_number']).sum()), 0)
    chk("game_type values are R only", ",".join(sorted(staff.game_type.unique())), "R")
    chk("2026 starts in window", int(lz26.game_pk.nunique()), 27)
    chk("2025 starts in window", int(lz25.game_pk.nunique()), 32)
    chk("H1 + H2 == full 2026 pitches", int(len(h1)+len(h2)), int(len(lz26)))

    print("\n-- 2. season / half line vs receipt -----------------------------------------")
    sl = rc("season_line").set_index("window")
    for lab, d in [("2025 (full)",lz25),("2026 (full)",lz26),
                   ("2026 H1 (uc-pps-017)",h1),("2026 H2 (new)",h2)]:
        r = sl.loc[lab]
        w,pa = i_woba(d); xw,xn = i_xwoba(d); ch,iz = i_chase(d)
        o,ru = i_outs_runs(d)
        chk(f"{lab} · PA",            pa, int(r.pa), 0)
        chk(f"{lab} · wOBA",          round(w,3), float(r.woba))
        chk(f"{lab} · xwOBA",         round(xw,3), float(r.xwoba))
        chk(f"{lab} · xwOBA n",       xn, int(r.xwoba_n), 0)
        chk(f"{lab} · K%",            round(i_krate(d),3), float(r.k_rate))
        chk(f"{lab} · BB%",           round(i_bbrate(d),3), float(r.bb_rate))
        chk(f"{lab} · whiff%",        round(i_whiff(d),3), float(r.whiff_rate))
        chk(f"{lab} · chase%",        round(ch,3), float(r.chase_rate))
        chk(f"{lab} · in-zone%",      round(iz,3), float(r.in_zone_rate))
        chk(f"{lab} · CSW%",          round(i_csw(d),3), float(r.csw_rate))
        chk(f"{lab} · first-pitch K%",round(i_fps(d),3), float(r.first_pitch_strike_rate))
        chk(f"{lab} · putaway%",      round(i_putaway(d),3), float(r.putaway_rate))
        chk(f"{lab} · hard-hit%",     round(i_hardhit(d),3), float(r.hard_hit_rate))
        chk(f"{lab} · outs",          o, int(r.outs), 0)
        chk(f"{lab} · runs on mound", ru, int(r.runs_on_mound), 0)
        chk(f"{lab} · RA9",           round(ru/(o/3)*9,2), float(r.ra9), 0.011)

    print("\n-- 3. uc-pps-017 continuity (the extension must reproduce its parent) -------")
    UC17 = {"pa":465,"woba":.295,"xwoba":.269,"hard_hit_rate":.305,"whiff_rate":.325,
            "csw_rate":.331,"first_pitch_strike_rate":.600,"in_zone_rate":.468,
            "chase_rate":.333,"putaway_rate":.241,"k_rate":.292,"bb_rate":.075}
    w,pa = i_woba(h1); xw,_ = i_xwoba(h1); ch,iz = i_chase(h1)
    live = {"pa":pa,"woba":round(w,3),"xwoba":round(xw,3),"hard_hit_rate":round(i_hardhit(h1),3),
            "whiff_rate":round(i_whiff(h1),3),"csw_rate":round(i_csw(h1),3),
            "first_pitch_strike_rate":round(i_fps(h1),3),"in_zone_rate":round(iz,3),
            "chase_rate":round(ch,3),"putaway_rate":round(i_putaway(h1),3),
            "k_rate":round(i_krate(h1),3),"bb_rate":round(i_bbrate(h1),3)}
    for k,v in UC17.items():
        chk(f"uc-pps-017 published {k}", live[k], v, 0 if k=="pa" else 0.0015)
    o,_ = i_outs_runs(h1); chk("uc-pps-017 published IP", f"{o//3}.{o%3}", "108.2")

    print("\n-- 4. per-start log ---------------------------------------------------------")
    sfr = rc("start_log_2026").sort_values("game_date").reset_index(drop=True)
    chk("start rows", len(sfr), 27, 0)
    chk("start-log PA sums to season PA", int(sfr.pa.sum()), int(i_woba(lz26)[1]), 0)
    chk("start-log outs sums to season outs", int(sfr.outs.sum()), i_outs_runs(lz26)[0], 0)
    chk("start-log runs sums to season runs", int(sfr.runs.sum()), i_outs_runs(lz26)[1], 0)
    for gd in ["2026-04-10","2026-06-05","2026-08-26"]:
        g = lz26[lz26.game_date==gd]; r = sfr[sfr.game_date==gd].iloc[0]
        o2,r2 = i_outs_runs(g)
        chk(f"start {gd} · pitches", int(len(g)), int(r.pitches), 0)
        chk(f"start {gd} · outs",    o2, int(r.outs), 0)
        chk(f"start {gd} · runs",    r2, int(r.runs), 0)
        chk(f"start {gd} · xwOBA",   round(i_xwoba(g)[0],3), round(float(r.xwoba),3))

    print("\n-- 5. CN-* consistency axes recomputed from the start log -------------------")
    co = rc("consistency_cohort").set_index("name")
    lzr = co.loc["Luzardo, Jesús"]
    win = sfr[sfr.game_date>=BREAK]
    chk("CN · starts in window",  len(win), int(lzr.starts), 0)
    chk("CN-1 SD of start xwOBA", round(float(win.xwoba.std(ddof=0)),4), float(lzr.cn1_xwoba_sd), 0.0002)
    chk("CN-2 floor rate (>=5.0 IP & <=3 R)",
        round(float(((win.outs>=15)&(win.runs<=3)).mean()),3), float(lzr.cn2_floor_rate))
    chk("CN-3 blow-up rate (>=5 R or <4.0 IP)",
        round(float(((win.runs>=5)|(win.outs<12)).mean()),3), float(lzr.cn3_blowup_rate))
    r3=[]; xs=win.xwoba.tolist()
    for i in range(len(xs)-2):
        w3=[v for v in xs[i:i+3] if pd.notna(v)]
        if len(w3)==3: r3.append(max(w3)-min(w3))
    chk("CN-4 mean rolling-3 xwOBA range", round(float(np.mean(r3)),4), float(lzr.cn4_roll3_range), 0.0002)
    chk("CN-5 SD of pitch count", round(float(win.pitches.std(ddof=0)),1), float(lzr.cn5_pitch_sd), 0.06)
    chk("CN-6 mean IP/start", round(float(win.outs.mean()/3),2), float(lzr.cn6_ip_per_start), 0.011)
    chk("CN-6 SD of outs", round(float(win.outs.std(ddof=0)),2), float(lzr.cn6_outs_sd), 0.011)
    dwin = lz26[lz26.game_date>=BREAK]
    chk("CN · aggregate xwOBA in window", round(i_xwoba(dwin)[0],4), float(lzr.agg_xwoba), 0.0002)

    print("\n-- 6. cohort integrity ------------------------------------------------------")
    coh = rc("consistency_cohort")
    chk("cohort size", len(coh), 5, 0)
    chk("every cohort member has >=8 starts", int((coh.starts>=8).all()), 1, 0)
    rk = rc("consistency_ranking")
    lz_rk = rk[rk.name=="Luzardo, Jesús"].set_index("axis")
    for ax, better in [("cn1_xwoba_sd",True),("agg_xwoba",True),("cn3_blowup_rate",True),
                       ("cn2_floor_rate",False),("cn4_roll3_range",True)]:
        sub = rk[rk.axis==ax].sort_values("value", ascending=better).reset_index(drop=True)
        want = int(sub.index[sub.name=="Luzardo, Jesús"][0])+1
        chk(f"rank recomputed · {ax}", int(lz_rk.loc[ax,"rank"]), want, 0)

    print("\n-- 7. breakpoint scan (TR-2) ------------------------------------------------")
    sc = rc("consistency_breakpoint_scan")
    chk("scan boundaries", len(sc), 8, 0)
    chk("xwOBA rank is 1 at EVERY boundary (level claim is robust)",
        int((sc.agg_xwoba__rank==1).all()), 1, 0)
    chk("CN-1 rank is NOT 1 at every boundary (variance claim is not)",
        int((sc.cn1_xwoba_sd__rank==1).all()), 0, 0)
    for _, r in sc.iterrows():
        w = sfr[sfr.game_date>=r.window_start]
        chk(f"scan {r.window_start} · Luzardo start count", len(w), int(r.lz_starts), 0)

    print("\n-- 8. splits: TTO / stand / arsenal / monthly --------------------------------")
    tt = rc("tto_h1_h2")
    for wl, d in [("2026 H1",h1),("2026 H2",h2),("2025",lz25)]:
        dd=d.copy(); dd["tto"]=dd.n_thruorder_pitcher.clip(upper=3)
        for k in (1,2,3):
            g=dd[dd.tto==k]; row=tt[(tt.window==wl)&(tt.tto==k)]
            if not len(row) or not len(g): continue
            chk(f"TTO {wl} {k} · wOBA", round(i_woba(g)[0],3), float(row.woba.iat[0]))
            chk(f"TTO {wl} {k} · PA",   i_woba(g)[1], int(row.plate_apps.iat[0]), 0)
    st = rc("by_stand_h1_h2")
    for wl, d in [("2026 H1",h1),("2026 H2",h2)]:
        for s_ in ("L","R"):
            g=d[d.stand==s_]; row=st[(st.window==wl)&(st.stand==s_)]
            chk(f"stand {wl} {s_} · wOBA", round(i_woba(g)[0],3), float(row.woba.iat[0]))
            chk(f"stand {wl} {s_} · xwOBA", round(i_xwoba(g)[0],3), float(row.xwoba.iat[0]))
    ar = rc("arsenal_h1_h2")
    for wl, d in [("2026 H1",h1),("2026 H2",h2)]:
        chk(f"arsenal {wl} · usage sums to 1", round(float(ar[ar.window==wl].usage.sum()),2), 1.0, 0.011)
        for pn in ar[ar.window==wl].pitch_name:
            g=d[d.pitch_name==pn]; row=ar[(ar.window==wl)&(ar.pitch_name==pn)].iloc[0]
            chk(f"arsenal {wl} {pn} · pitches", int(len(g)), int(row.pitches), 0)
            chk(f"arsenal {wl} {pn} · whiff", round(i_whiff(g),3), float(row.whiff_rate))
    mo = rc("monthly_2026")
    chk("monthly PA sums to season PA", int(mo.plate_apps.sum()), int(i_woba(lz26)[1]), 0)

    print("\n-- 9. ARI opponent lens -----------------------------------------------------")
    a26 = lz26[lz26.opp=="AZ"]
    al = rc("ari_history_line").set_index("window")
    chk("ARI 2026 games", int(a26.game_pk.nunique()), int(al.loc["2026","games"]), 0)
    chk("ARI 2026 PA", i_woba(a26)[1], int(al.loc["2026","pa"]), 0)
    chk("ARI 2026 wOBA", round(i_woba(a26)[0],3), float(al.loc["2026","woba"]))
    chk("ARI 2026 xwOBA", round(i_xwoba(a26)[0],3), float(al.loc["2026","xwoba"]))
    mx = rc("ari_start_20260410_mix")
    chk("4/10 mix pitches sums to start pitches", int(mx.pitches.sum()), int(len(a26)), 0)
    h2h = rc("ari_h2h_batters")
    chk("H2H names all resolved (4-34 chars)",
        int(h2h.batter_name.astype(str).str.len().between(4,34).all()), 1, 0)
    chk("H2H tiers present", int(h2h.tier.nunique()), 2, 0)
    chk("H2H current-era rows only from 2025-26",
        int((h2h[h2h.tier.str.startswith("current")].last_faced>="2025-01-01").all()), 1, 0)
    pl = rc("attack_plan_by_stand")
    for s_ in ("L","R"):
        chk(f"attack plan {s_} · usage sums to 1", round(float(pl[pl.stand==s_].usage.sum()),2), 1.0, 0.011)
        chk(f"attack plan {s_} · pitches sums to stand pitches",
            int(pl[pl.stand==s_].pitches.sum()), int((lz26.stand==s_).sum()), 0)

    print("\n-- 10. tripwire closure table ----------------------------------------------")
    tw = rc("uc17_tripwire_closure").set_index("tripwire")
    chk("T1 first-pitch strike H1", round(i_fps(h1),3), float(tw.loc["T1","h1"]))
    chk("T1 first-pitch strike H2", round(i_fps(h2),3), float(tw.loc["T1","h2"]))
    chk("T2 chase H2", round(i_chase(h2)[0],3), float(tw.loc["T2","h2"]))
    chk("T5 hard-hit H2", round(i_hardhit(h2),3), float(tw.loc["T5","h2"]))
    chk("T6.2 TTO2 H2 wOBA", round(i_woba(h2[h2.n_thruorder_pitcher.clip(upper=3)==2])[0],3),
        float(tw.loc["T6.2","h2"]))
    rp = rc("uc17_reproduction_check")
    chk("reproduction check has zero REVIEW rows", int((rp.match=="REVIEW").sum()), 0, 0)

    print("\n-- 11. DQ scorecard & manifests ---------------------------------------------")
    dqs = rc("dq_scorecard")
    chk("DQ FAIL count", int((dqs.result=="FAIL").sum()), 0, 0)
    chk("DQ rules executed", int(len(dqs)>=25), 1, 0)
    fr = rc("freshness_manifest")
    chk("freshness manifest rows", int(len(fr)>=8), 1, 0)
    chk("ARI lineup flagged UNVERIFIED",
        int(fr.value.astype(str).str.contains("NOT AVAILABLE").any()), 1, 0)
    chk("cache max date logged", str(fr[fr.item.str.contains("phils_2026")].value.iat[0]), "2026-08-30")

    print("\n" + "="*84)
    print(f"RESULT: {PASS}/{PASS+FAILN} PASS · {FAILN} FAIL")
    print("="*84 + "\n")
    sys.exit(0 if FAILN==0 else 1)

if __name__ == "__main__":
    main()
