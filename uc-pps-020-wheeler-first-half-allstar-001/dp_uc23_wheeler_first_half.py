"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #24  (uc-pps-020)
"Zack Wheeler — First-Half 2026 vs the All-Star First Halves (2021/2024/2025)"
============================================================================

Layer-3 BUILD artifact for the Phillies Pitching (pps) value stream.
Sibling of uc-pps-017/018/019 (ASG first-half retrospectives) — but inverted:
this is the report on the All-Star who wasn't. Results tier first, then the
indicators that plausibly drove them, then persona actions.

Pattern lineage: UC3 -> UC8 -> UC11 -> uc-pps-017 (pitcher ASG kernel) ->
uc-pps-019 / dp_uc21 (direct parent) -> THIS (UC #24 / uc-pps-020 / dp_uc23).

Governance lineage (00-07 in this package folder):
  - data-product-owner     : claimed UC #24 / dp_uc23 / uc-pps-020
                             (ledger verified: Harper consumed #23 / dp_uc22)
  - use-case-validator     : GO (01); ASG-snub framing = manual carry-in
  - source-system-profiler : entity lock pitcher==554430 (resolved from
                             player_name mode in data, not hand-keyed);
                             phils_{2021,2024,2025,2026}; 2026 cache fresh
                             to 07-12
  - kpi-calculator         : locked cores inherited VERBATIM from dp_uc21
                             (get_stats/nresults, whiff, chase, putaway,
                             fpsr, hard_hit, CSW, outs/RA9/FIP, TTO,
                             count leverage). NO new KPIs this UC —
                             velocity is reported as a measurable
                             (Statcast release_speed), not a governed KPI.
  - business-glossary-agent: no governed term redefined

DATA WINDOW / FRESHNESS:
  * phils_{2021,2024,2025,2026}.parquet, phillies_role=='pitching',
    pitcher==554430, game_type=='R', dedup game_pk+at_bat_number+pitch_number.
  * FIRST-HALF cutoffs (user-provided last game of first half):
      2021 <= 2021-07-11 | 2024 <= 2024-07-14 | 2025 <= 2025-07-13
      2026 = full cache (fresh through 2026-07-12; ASG = 2026-07-14).
  * DATA-VISIBLE context: 2025 season log ends 2025-08-15 (no Wheeler
    pitches after); 2026 debut 2026-04-25 (no April-early games).
  * MANUAL CARRY-INS: Wheeler NOT selected to 2026 NL ASG; All-Star in
    2021/2024/2025 (user-provided). The REASON for the late 2026 debut and
    the truncated 2025 season is not derivable from the pitch log — it is
    an intake gap flagged in 01, not asserted here.
  * IP from event outs (~±1 out vs official). Runs = on-mound score deltas
    (RA9, NOT official ERA).

OUTPUTS (NEW files, none overwritten) -> <MLB repo>/out/:
  dp_uc23_wheeler_firsthalf_line.csv      results by first-half year (+IP,RA9,FIP,CSW)
  dp_uc23_wheeler_process_kpis.csv        FPSR/chase/zone/putaway/whiff/CSW/HH by year
  dp_uc23_wheeler_arsenal_yoy.csv         usage/velo/spin/mvt/whiff/putaway/xwOBA
  dp_uc23_wheeler_by_stand_yoy.csv        by batter stand
  dp_uc23_wheeler_tto_yoy.csv             times-through-order
  dp_uc23_wheeler_start_log_2026.csv      per-start 2026 (+FF velo per start)
  dp_uc23_wheeler_monthly_2026.csv        monthly trend 2026
  dp_uc23_staff_benchmark_2026.csv        Phillies 2026 staff (>=500 pitches)
  dp_uc23_wheeler_count_leverage.csv      2-strike funnel + ahead-in-count
  dp_uc23_wheeler_velo_by_start.csv       FF/SI velo per start, all four halves
  dp_uc23_dq_scorecard.csv                data-quality-engineer scorecard
  dp_uc23_freshness_manifest.csv          source/window/fitness receipts
  dp_uc23_fig1_results_yoy.png            results across the four first halves
  dp_uc23_fig2_arsenal_yoy.png            usage x whiff by pitch, four panels
  dp_uc23_fig3_velo_2026.png              FF velocity by start + 2026 trend
============================================================================
"""
from __future__ import annotations
import os, shutil
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

CURRENT_YEAR = 2026
YEARS = (2021, 2024, 2025, 2026)
FH_CUTOFF = {2021: "2021-07-11", 2024: "2024-07-14",
             2025: "2025-07-13", 2026: "2026-12-31"}
CARRY_INS = ("Wheeler NL All-Star 2021/2024/2025; NOT selected 2026 "
             "(user-provided). Cause of late 2026 debut / truncated 2025 "
             "season not derivable from pitch log — intake gap, not asserted.")

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "phillies"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies",
]
PHIL_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
REPO_ROOT = os.path.dirname(os.path.dirname(PHIL_DIR)) if PHIL_DIR else HERE
OUT_DIR = os.path.join(REPO_ROOT, "out"); os.makedirs(OUT_DIR, exist_ok=True)
_WOBA_CANDIDATES = [
    os.path.join(REPO_ROOT, "wOBA and FIP Constants.csv"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv",
]
WOBA_CSV = next((p for p in _WOBA_CANDIDATES if os.path.isfile(p)), None)

SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]

PHI_RED, PHI_NAVY, PHI_GRAY, PHI_LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
PITCH_COLORS = {"4-Seam Fastball": "#E81828", "Sinker": "#8C564B",
                "Sweeper": "#17BECF", "Slider": "#1F77B4", "Curveball": "#2CA02C",
                "Cutter": "#9467BD", "Changeup": "#FF7F0E", "Split-Finger": "#BCBD22"}

# ===========================================================================
# LOADERS (adapted from dp_uc21; entity resolved from data, then locked)
# ===========================================================================
def _coerce(df):
    for c in ["plate_x","plate_z","sz_top","sz_bot","pfx_x","pfx_z","release_speed",
              "release_spin_rate","launch_speed","launch_angle","strikes","balls",
              "pitch_number","woba_value","woba_denom","zone","bat_score",
              "post_bat_score","n_thruorder_pitcher"]:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def resolve_wheeler_id():
    """Entity resolution from data (player_name mode), never hand-keyed."""
    ids = set()
    for yr in YEARS:
        d = pd.read_parquet(os.path.join(PHIL_DIR, f"phils_{yr}.parquet"),
                            columns=["pitcher","player_name","phillies_role"])
        s = d[(d.phillies_role=="pitching") & (d.player_name=="Wheeler, Zack")].pitcher
        if len(s): ids.add(int(s.mode().iat[0]))
    if len(ids) != 1:
        raise ValueError(f"Entity resolution failed — ids found: {ids}")
    return ids.pop()

def load_wheeler(wid):
    if PHIL_DIR is None:
        raise FileNotFoundError("Could not locate data/phillies. Set MLB_DATA_ROOT.")
    frames = []
    for yr in YEARS:
        d = pd.read_parquet(os.path.join(PHIL_DIR, f"phils_{yr}.parquet"))
        d = d[(d.phillies_role=="pitching") & (d.pitcher==wid) & (d.game_type=="R")]
        d = d[d.game_date.astype(str).str[:10] <= FH_CUTOFF[yr]]   # FIRST HALF ONLY
        if len(d): frames.append(d)
    r = pd.concat(frames, ignore_index=True).drop_duplicates(
        ["game_pk", "at_bat_number", "pitch_number"])
    r = _coerce(r)
    if WOBA_CSV:
        w = pd.read_csv(WOBA_CSV)
        r = r.drop(columns=[c for c in w.columns if c != "Season" and c in r.columns])
        r = r.merge(w, left_on="game_year", right_on="Season", how="left")
    return r

def load_staff_2026():
    d = pd.read_parquet(os.path.join(PHIL_DIR, "phils_2026.parquet"))
    d = d[(d.phillies_role=="pitching") & (d.game_type=="R")].drop_duplicates(
        ["game_pk", "at_bat_number", "pitch_number"])
    d = _coerce(d)
    if WOBA_CSV:
        w = pd.read_csv(WOBA_CSV)
        d = d.drop(columns=[c for c in w.columns if c != "Season" and c in d.columns])
        d = d.merge(w, left_on="game_year", right_on="Season", how="left")
    return d

# ===========================================================================
# LOCKED KPI FUNCTIONS — inherited verbatim from dp_uc21 (via dp_uc17/dp_uc11)
# ===========================================================================
def get_stats(level, df):
    if isinstance(level, str): level = [level]
    def cnt(mask, name):
        return df[mask].groupby(level, as_index=False).agg(**{name: ("description","size")})
    def wsum(mask, col, name):
        return df[mask].groupby(level, as_index=False).agg(**{name: (col,"sum")})
    base = df.groupby(level, as_index=False).agg(pitches=("description","size"))
    pa = cnt(~df.events.replace(np.nan,"NA").isin(["NA","pickoff_1b"]), "plate_apps")
    ab = cnt(~df.events.replace(np.nan,"NA").isin(
        ["NA","pickoff_1b","walk","intent_walk","hit_by_pitch","sac_fly","sac_bunt"]), "at_bats")
    bip = cnt(df.type=="X","bip")
    hits = cnt(df.events.isin(["home_run","single","double","triple"]),"hits")
    singles=cnt(df.events=="single","singles"); doubles=cnt(df.events=="double","doubles")
    triples=cnt(df.events=="triple","triples"); hrs=cnt(df.events=="home_run","hrs")
    walks=cnt(df.events=="walk","walks")
    ks=cnt(df.events.isin(["strikeout","strikeout_double_play"]),"strikeouts")
    hbp=cnt(df.events=="hit_by_pitch","hbp")
    wBB=wsum(df.events=="walk","wBB","wBB"); wHBP=wsum(df.events=="hit_by_pitch","wHBP","wHBP")
    w1B=wsum(df.events=="single","w1B","w1B"); w2B=wsum(df.events=="double","w2B","w2B")
    w3B=wsum(df.events=="triple","w3B","w3B"); wHR=wsum(df.events=="home_run","wHR","wHR")
    xba=df.groupby(level,as_index=False).agg(xba=("estimated_ba_using_speedangle","mean"))
    xwoba=df.groupby(level,as_index=False).agg(xwoba=("estimated_woba_using_speedangle","mean"))
    out=base
    for x in [pa,ab,bip,hits,singles,doubles,triples,hrs,walks,ks,hbp,
              wBB,wHBP,w1B,w2B,w3B,wHR,xba,xwoba]:
        out=out.merge(x,how="left",on=level)
    return out.fillna(0)

def nresults(level, df):
    if isinstance(level, str): level = [level]
    s = get_stats(level, df)
    s["ba"]=s.hits/s.at_bats
    s["obp"]=(s.hits+s.walks+s.hbp)/s.plate_apps
    s["slg"]=(s.singles+2*s.doubles+3*s.triples+4*s.hrs)/s.at_bats
    s["ops"]=s.obp+s.slg
    s["woba"]=(s.wBB+s.wHBP+s.w1B+s.w2B+s.w3B+s.wHR)/s.plate_apps
    s["krate"]=s.strikeouts/s.plate_apps
    s["bbrate"]=s.walks/s.plate_apps
    s["hr_rate"]=s.hrs/s.plate_apps
    cols=level+["pitches","plate_apps","bip","hits","hrs","walks","strikeouts",
                "ba","obp","slg","ops","woba","krate","bbrate","hr_rate"]
    return s[cols].round(3)

def whiff_rate(level, df):
    if isinstance(level, str): level=[level]
    u=df[df.description.isin(SWINGS)].groupby(level,as_index=False).agg(swings=("des","size"))
    v=df[df.description.isin(WHIFFS)].groupby(level,as_index=False).agg(whiffs=("des","size"))
    w=u.merge(v,on=level,how="left").fillna({"whiffs":0})
    w["whiff_rate"]=w.whiffs/w.swings
    return w.round(3)

def chase_rate(level, df):
    if isinstance(level, str): level=[level]
    chase=df[(df.zone>9)&(df.description.isin(SWINGS))]
    i=chase.groupby(level,as_index=False).agg(chases=("des","size"))
    j=df[df.zone>9].groupby(level,as_index=False).agg(ooz=("des","size"))
    tot=df.groupby(level,as_index=False).agg(pitches=("des","size"))
    cr=tot.merge(j,on=level,how="left").merge(i,on=level,how="left").fillna(0)
    cr["chase_rate"]=cr.chases/cr.ooz
    cr["in_zone_rate"]=(cr.pitches-cr.ooz)/cr.pitches
    return cr.round(3)

def putaway_rate(level, df):
    if isinstance(level, str): level=[level]
    z=df[df.strikes==2].groupby(level,as_index=False).agg(pitches2strikes=("des","size"))
    k=df[df.events.isin(["strikeout","strikeout_double_play"])].groupby(
        level,as_index=False).agg(strikeouts=("des","size"))
    z=z.merge(k,on=level,how="left").fillna(0)
    z["putaway_rate"]=z.strikeouts/z.pitches2strikes
    return z.round(3)

def fpsr(level, df):
    if isinstance(level, str): level=[level]
    fp=df[df.pitch_number==1]
    balls=fp.groupby(level+["type"],as_index=False).agg(balls=("des","size"))
    tot=fp.groupby(level,as_index=False).agg(pitches=("des","size"))
    m=tot.merge(balls[balls.type=="B"][level+["balls"]],on=level,how="left").fillna({"balls":0})
    m["first_pitch_strike_rate"]=(m.pitches-m.balls)/m.pitches
    return m.round(3)

def hard_hit_rate(level, df):
    if isinstance(level, str): level=[level]
    hh=df[(df.launch_speed>=95)&(df.type=="X")].groupby(level,as_index=False).agg(hard_hits=("des","size"))
    bips=df[df.type=="X"].groupby(level,as_index=False).agg(bips=("des","size"))
    out=bips.merge(hh,on=level,how="left").fillna(0)
    out["hard_hit_rate"]=out.hard_hits/out.bips
    return out.round(3)

OUTS_MAP = {
    "field_out":1,"strikeout":1,"force_out":1,"sac_fly":1,"sac_bunt":1,
    "fielders_choice_out":1,"fielders_choice":1,"other_out":1,
    "grounded_into_double_play":2,"double_play":2,"strikeout_double_play":2,
    "sac_fly_double_play":2,"sac_bunt_double_play":2,"triple_play":3,
    "caught_stealing_2b":1,"caught_stealing_3b":1,"caught_stealing_home":1,
    "pickoff_caught_stealing_2b":1,"pickoff_caught_stealing_3b":1,
    "pickoff_caught_stealing_home":1,"pickoff_1b":1,"pickoff_2b":1,"pickoff_3b":1,
}

def pa_last(df):
    return (df.sort_values(["game_pk","at_bat_number","pitch_number"])
              .groupby(["game_pk","at_bat_number"],as_index=False).last())

def outs_and_runs(df):
    last = pa_last(df)
    outs = last.events.map(OUTS_MAP).fillna(0).sum()
    runs = (last.post_bat_score - last.bat_score).clip(lower=0).sum()
    return int(outs), int(runs)

def ip_str(outs):
    return f"{outs//3}.{outs%3}"

def fip(df, c_fip):
    last = pa_last(df)
    hr = (last.events=="home_run").sum()
    bb = last.events.isin(["walk","intent_walk"]).sum()
    hbp = (last.events=="hit_by_pitch").sum()
    k = last.events.isin(["strikeout","strikeout_double_play"]).sum()
    outs,_ = outs_and_runs(df)
    ip = outs/3
    return (13*hr + 3*(bb+hbp) - 2*k)/ip + c_fip if ip>0 else np.nan

def csw_rate(level, df):
    if isinstance(level, str): level=[level]
    cs = df[df.description.eq("called_strike") | df.description.isin(WHIFFS)]
    n = cs.groupby(level,as_index=False).agg(csw=("des","size"))
    tot = df.groupby(level,as_index=False).agg(pitches=("des","size"))
    out = tot.merge(n,on=level,how="left").fillna(0)
    out["csw_rate"] = out.csw/out.pitches
    return out.round(3)

# ===========================================================================
# BUILD
# ===========================================================================
def main():
    wid = resolve_wheeler_id()
    print(f"entity lock: pitcher == {wid} (resolved from player_name mode)\n")
    wz = load_wheeler(wid)
    w = pd.read_csv(WOBA_CSV).set_index("Season")
    by_year = {yr: wz[wz.game_year==yr].copy() for yr in YEARS}

    # --- 1. first-half results line, all four years --------------------------
    line = nresults(["game_year"], wz)
    extra = []
    for yr in YEARS:
        d = by_year[yr]
        outs, runs = outs_and_runs(d)
        extra.append(dict(game_year=yr, starts=d.game_pk.nunique(),
                          ip=ip_str(outs), outs=outs, runs_on_mound=runs,
                          ip_per_start=round(outs/3/d.game_pk.nunique(),2),
                          pitches_per_start=round(len(d)/d.game_pk.nunique(),1),
                          ra9=round(runs/(outs/3)*9,2),
                          fip=round(fip(d, w.loc[yr,"cFIP"]),2),
                          fh_window=f"{str(d.game_date.min())[:10]}..{str(d.game_date.max())[:10]}"))
    line = line.merge(pd.DataFrame(extra), on="game_year")
    xwy = wz.groupby("game_year",as_index=False).agg(
        xwoba=("estimated_woba_using_speedangle","mean")).round(3)
    line = line.drop(columns=[c for c in ["xwoba"] if c in line]).merge(xwy,on="game_year")
    line = line.merge(hard_hit_rate(["game_year"], wz)[["game_year","hard_hit_rate"]], on="game_year")
    line = line.merge(csw_rate(["game_year"], wz)[["game_year","csw_rate"]], on="game_year")
    line.to_csv(os.path.join(OUT_DIR,"dp_uc23_wheeler_firsthalf_line.csv"),index=False)

    # --- 2. process KPIs by year ----------------------------------------------
    proc=[]
    for yr in YEARS:
        d = by_year[yr]
        proc.append(dict(game_year=yr,
            first_pitch_strike_rate=float(fpsr(["game_year"],d).first_pitch_strike_rate.iat[0]),
            chase_rate=float(chase_rate(["game_year"],d).chase_rate.iat[0]),
            in_zone_rate=float(chase_rate(["game_year"],d).in_zone_rate.iat[0]),
            putaway_rate=float(putaway_rate(["game_year"],d).putaway_rate.iat[0]),
            hard_hit_rate=float(hard_hit_rate(["game_year"],d).hard_hit_rate.iat[0]),
            csw_rate=float(csw_rate(["game_year"],d).csw_rate.iat[0]),
            whiff_rate=float(whiff_rate(["game_year"],d).whiff_rate.iat[0])))
    proc = pd.DataFrame(proc).round(3)
    proc.to_csv(os.path.join(OUT_DIR,"dp_uc23_wheeler_process_kpis.csv"),index=False)

    # --- 3. arsenal YoY --------------------------------------------------------
    ars_rows=[]
    for yr in YEARS:
        d = by_year[yr]
        a = d.groupby("pitch_name",as_index=False).agg(
            n=("description","size"), velo=("release_speed","mean"),
            spin=("release_spin_rate","mean"), pfx_x=("pfx_x","mean"),
            pfx_z=("pfx_z","mean"),
            xwoba=("estimated_woba_using_speedangle","mean"))
        a["usage"]=a.n/a.n.sum()
        wh = whiff_rate(["pitch_name"], d)[["pitch_name","swings","whiffs","whiff_rate"]]
        pw = putaway_rate(["pitch_name"], d)[["pitch_name","putaway_rate"]]
        a = a.merge(wh,on="pitch_name",how="left").merge(pw,on="pitch_name",how="left")
        a.insert(0,"game_year",yr)
        ars_rows.append(a)
    ars = pd.concat(ars_rows,ignore_index=True).round(3)
    ars.to_csv(os.path.join(OUT_DIR,"dp_uc23_wheeler_arsenal_yoy.csv"),index=False)

    # --- 4. by stand YoY -------------------------------------------------------
    stand = nresults(["game_year","stand"], wz)
    xws = wz.groupby(["game_year","stand"],as_index=False).agg(
        xwoba=("estimated_woba_using_speedangle","mean")).round(3)
    stand = stand.merge(xws, on=["game_year","stand"])
    stand.to_csv(os.path.join(OUT_DIR,"dp_uc23_wheeler_by_stand_yoy.csv"),index=False)

    # --- 5. TTO YoY ------------------------------------------------------------
    wz_t = wz[wz.n_thruorder_pitcher.notna()].copy()
    if len(wz_t):
        wz_t["tto"] = wz_t.n_thruorder_pitcher.clip(upper=3).astype(int)
        tto = nresults(["game_year","tto"], wz_t)
        tto.to_csv(os.path.join(OUT_DIR,"dp_uc23_wheeler_tto_yoy.csv"),index=False)
    else:
        tto = pd.DataFrame()

    # --- 6. per-start log 2026 (+FF velo) ---------------------------------------
    d26 = by_year[2026]
    rows=[]
    for gpk, g in d26.groupby("game_pk"):
        last = pa_last(g)
        outs, runs = outs_and_runs(g)
        opp = g.away_team.iat[0] if g.home_team.iat[0]=="PHI" else g.home_team.iat[0]
        ff = g[g.pitch_name=="4-Seam Fastball"].release_speed
        rows.append(dict(
            game_date=str(g.game_date.max())[:10], opp=opp,
            pitches=len(g), ip=ip_str(outs),
            pa=int((~last.events.replace(np.nan,"NA").isin(["NA","pickoff_1b"])).sum()),
            k=int(last.events.isin(["strikeout","strikeout_double_play"]).sum()),
            bb=int(last.events.isin(["walk","intent_walk"]).sum()),
            hr=int((last.events=="home_run").sum()),
            runs=runs,
            xwoba=round(g.estimated_woba_using_speedangle.mean(),3),
            csw=float(csw_rate(["game_year"],g).csw_rate.iat[0]),
            ff_velo=round(float(ff.mean()),1) if len(ff) else np.nan,
            ff_velo_max=round(float(ff.max()),1) if len(ff) else np.nan))
    slog = pd.DataFrame(rows).sort_values("game_date").reset_index(drop=True)
    slog.to_csv(os.path.join(OUT_DIR,"dp_uc23_wheeler_start_log_2026.csv"),index=False)

    # --- 7. monthly 2026 --------------------------------------------------------
    d26m = d26.copy(); d26m["month"] = d26m.game_date.astype(str).str[:7]
    mon = nresults(["month"], d26m)
    mon = mon.merge(csw_rate(["month"],d26m)[["month","csw_rate"]],on="month")
    xwm = d26m.groupby("month",as_index=False).agg(
        xwoba=("estimated_woba_using_speedangle","mean")).round(3)
    mon = mon.drop(columns=[c for c in ["xwoba"] if c in mon]).merge(xwm,on="month")
    mon.to_csv(os.path.join(OUT_DIR,"dp_uc23_wheeler_monthly_2026.csv"),index=False)

    # --- 8. staff benchmark 2026 (>=500 pitches) ---------------------------------
    staff = load_staff_2026()
    bench = nresults(["player_name"], staff)
    bench = bench[bench.pitches>=500].sort_values("woba")
    xw = staff.groupby("player_name",as_index=False).agg(
        xwoba=("estimated_woba_using_speedangle","mean")).round(3)
    bench = bench.drop(columns=[c for c in ["xwoba"] if c in bench]).merge(xw,on="player_name")
    bench = bench.merge(csw_rate(["player_name"], staff)[["player_name","csw_rate"]], on="player_name")
    bench.to_csv(os.path.join(OUT_DIR,"dp_uc23_staff_benchmark_2026.csv"),index=False)

    # --- 9. count leverage YoY ----------------------------------------------------
    lev=[]
    for yr in YEARS:
        d = by_year[yr]
        last = pa_last(d)
        pa_n = (~last.events.replace(np.nan,"NA").isin(["NA","pickoff_1b"])).sum()
        two_k = d[d.strikes==2].groupby(["game_pk","at_bat_number"]).ngroups
        ahead = d[(d.balls<d.strikes)].shape[0]/len(d)
        lev.append(dict(game_year=yr, pa=int(pa_n),
            pa_reaching_2strikes=int(two_k),
            share_pa_to_2strikes=round(two_k/pa_n,3),
            pitch_share_ahead_in_count=round(ahead,3)))
    lev = pd.DataFrame(lev)
    lev.to_csv(os.path.join(OUT_DIR,"dp_uc23_wheeler_count_leverage.csv"),index=False)

    # --- 10. velo measurable: FF/SI by start, all four halves ----------------------
    vrows=[]
    for yr in YEARS:
        d = by_year[yr]
        for gpk, g in d.groupby("game_pk"):
            for pt in ("4-Seam Fastball","Sinker"):
                s = g[g.pitch_name==pt].release_speed
                if len(s) >= 5:
                    vrows.append(dict(game_year=yr, game_date=str(g.game_date.max())[:10],
                                      pitch=pt, n=len(s),
                                      velo=round(float(s.mean()),2),
                                      velo_max=round(float(s.max()),1)))
    velo = pd.DataFrame(vrows).sort_values(["game_year","game_date"])
    velo.to_csv(os.path.join(OUT_DIR,"dp_uc23_wheeler_velo_by_start.csv"),index=False)

    # --- 11. DQ scorecard + freshness manifest --------------------------------------
    key_cdes=["pitch_name","release_speed","plate_x","plate_z","zone","description",
              "events","stand","woba_value","woba_denom","pitch_number",
              "n_thruorder_pitcher","bat_score","post_bat_score","launch_speed"]
    dq=[dict(check="entity_lock",detail=f"pitcher=={wid} only",
             result="PASS" if set(wz.pitcher.unique())=={wid} else "FAIL"),
        dict(check="entity_resolution",detail="id from player_name mode, consistent across 4 seasons",
             result="PASS"),
        dict(check="dedup",detail="game_pk+at_bat_number+pitch_number unique",
             result="PASS" if not wz.duplicated(["game_pk","at_bat_number","pitch_number"]).any() else "FAIL"),
        dict(check="game_type",detail="regular season only",
             result="PASS" if set(wz.game_type.unique())=={"R"} else "FAIL"),
        dict(check="first_half_windows",detail="max game_date <= cutoff per year",
             result="PASS" if all(str(by_year[y].game_date.max())[:10] <= FH_CUTOFF[y] for y in YEARS) else "FAIL"),
        dict(check="weights_join",detail="wOBA weights joined all seasons",
             result="PASS" if wz.wBB.notna().all() else "FAIL")]
    for c in key_cdes:
        nn = wz[c].notna().mean() if c in wz.columns else 0.0
        dq.append(dict(check=f"completeness:{c}",detail="pitch log non-null share",
                       result=round(float(nn),3)))
    pd.DataFrame(dq).to_csv(os.path.join(OUT_DIR,"dp_uc23_dq_scorecard.csv"),index=False)

    fresh_rows=[]
    for yr in YEARS:
        d = by_year[yr]
        fresh_rows.append(dict(source=f"data/phillies/phils_{yr}.parquet",
            window=f"{str(d.game_date.min())[:10]}..{str(d.game_date.max())[:10]} (cutoff {FH_CUTOFF[yr]})",
            rows=len(d), note=f"first half, {d.game_pk.nunique()} starts, entity-locked, R games"))
    fresh_rows.append(dict(source="user-provided context", window="2026-07-15", rows=0, note=CARRY_INS))
    fresh_rows.append(dict(source="derived", window="n/a", rows=0,
        note="IP from event-outs; runs=on-mound score deltas (RA9 not ERA); "
             "2025 full-season log ends 2025-08-15 (data-visible); 2026 debut 2026-04-25 (data-visible)"))
    pd.DataFrame(fresh_rows).to_csv(os.path.join(OUT_DIR,"dp_uc23_freshness_manifest.csv"),index=False)

    # --- 12. figures ------------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = [f"{y}-1H" for y in YEARS]

    # fig 1: results across the four first halves
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    x = np.arange(len(YEARS))
    ln = line.sort_values("game_year")
    ax.bar(x-.18, ln.woba, .36, color=PHI_RED, label="wOBA against", zorder=2)
    ax.bar(x+.18, ln.xwoba, .36, color=PHI_NAVY, alpha=.75, label="xwOBA against", zorder=2)
    for xx, (wv, xv) in enumerate(zip(ln.woba, ln.xwoba)):
        ax.text(xx-.18, wv+.004, f"{wv:.3f}", ha="center", fontsize=8)
        ax.text(xx+.18, xv+.004, f"{xv:.3f}", ha="center", fontsize=8, color=PHI_NAVY)
    ax2 = ax.twinx()
    ax2.plot(x, ln.ra9, color=PHI_GRAY, marker="D", lw=1.8, label="RA9 (right)")
    for xx, rv in zip(x, ln.ra9):
        ax2.text(xx, rv+.12, f"{rv:.2f}", ha="center", fontsize=8, color=PHI_GRAY)
    ax.set_xticks(x); ax.set_xticklabels([f"{l}\n({s} GS, {ip} IP)" for l,s,ip in
        zip(labels, ln.starts, ln.ip)], fontsize=9)
    ax.set_ylim(0, max(ln.woba.max(), ln.xwoba.max())+.05)
    ax.set_ylabel("wOBA / xwOBA against"); ax2.set_ylabel("RA9")
    h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
    ax.legend(h1+h2, l1+l2, fontsize=8, loc="upper left")
    ax.grid(axis="y", color=PHI_LGRAY, zorder=0)
    ax.set_title("Wheeler first halves — the All-Star years vs 2026",
                 color=PHI_NAVY, weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR,"dp_uc23_fig1_results_yoy.png"), dpi=160)
    plt.close(fig)

    # fig 2: arsenal usage x whiff, four panels
    order_all = (ars.groupby("pitch_name").n.sum().sort_values(ascending=False).index.tolist())
    abbr = {"4-Seam Fastball":"FF","Sinker":"SI","Sweeper":"ST","Slider":"SL",
            "Curveball":"CU","Cutter":"FC","Changeup":"CH","Split-Finger":"FS"}
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.4), sharey=True)
    for ax, yr in zip(axes, YEARS):
        a = ars[ars.game_year==yr].set_index("pitch_name").reindex(order_all)
        a = a[a.n.notna()]
        x = np.arange(len(a))
        ax.bar(x-.2, a.usage, .4, color=[PITCH_COLORS.get(o,PHI_GRAY) for o in a.index],
               alpha=.9, label="usage")
        ax.bar(x+.2, a.whiff_rate, .4, color=PHI_NAVY, alpha=.55, label="whiff")
        for xx,(m,ww) in enumerate(zip(a.usage, a.whiff_rate)):
            if pd.notna(m) and m>.02: ax.text(xx-.2, m+.01, f"{m:.0%}", ha="center", fontsize=7)
            if pd.notna(ww) and ww>.02: ax.text(xx+.2, ww+.01, f"{ww:.0%}", ha="center", fontsize=7, color=PHI_NAVY)
        ax.set_xticks(x); ax.set_xticklabels([abbr.get(o,o) for o in a.index], fontsize=8)
        ax.set_title(f"{yr} first half", color=PHI_NAVY, weight="bold", fontsize=10)
        ax.set_ylim(0, .62); ax.grid(axis="y", color=PHI_LGRAY, zorder=0)
    axes[0].legend(fontsize=8)
    fig.suptitle("Wheeler arsenal across the four first halves — usage × whiff",
                 color=PHI_NAVY, weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR,"dp_uc23_fig2_arsenal_yoy.png"), dpi=160)
    plt.close(fig)

    # fig 3: FF velo by start across all four halves
    fig, ax = plt.subplots(figsize=(11, 4.6))
    xoff = 0; ticks=[]; ticklabels=[]
    for yr in YEARS:
        v = velo[(velo.game_year==yr)&(velo.pitch=="4-Seam Fastball")].sort_values("game_date")
        if not len(v): continue
        xs = np.arange(len(v)) + xoff
        ax.plot(xs, v.velo, color=PHI_RED if yr==2026 else PHI_NAVY,
                marker="o", ms=3.5, lw=1.6, alpha=1 if yr==2026 else .55)
        m = float(v.velo.mean())
        ax.hlines(m, xs.min(), xs.max(), color=PHI_GRAY, ls="--", lw=1)
        ax.text(xs.mean(), m+.15, f"{yr}: {m:.1f}", ha="center", fontsize=8, color=PHI_NAVY)
        ticks.append(xs.mean()); ticklabels.append(f"{yr}-1H")
        xoff = xs.max() + 3
    ax.set_xticks(ticks); ax.set_xticklabels(ticklabels)
    ax.set_ylabel("4-seam velocity (mph, start avg)")
    ax.grid(axis="y", color=PHI_LGRAY, zorder=0)
    ax.set_title("Four-seam velocity by start — first halves 2021/2024/2025/2026",
                 color=PHI_NAVY, weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR,"dp_uc23_fig3_velo_2026.png"), dpi=160)
    plt.close(fig)

    for f in ["dp_uc23_fig1_results_yoy.png","dp_uc23_fig2_arsenal_yoy.png",
              "dp_uc23_fig3_velo_2026.png"]:
        try: shutil.copy(os.path.join(OUT_DIR,f), os.path.join(HERE,"out_"+f))
        except Exception as e: print("fig copy skipped:", f, e)

    # --- console receipts ----------------------------------------------------------
    pd.set_option("display.width", 240)
    print("UC-PPS-020 build complete.\n")
    print("FIRST-HALF LINE\n", line.to_string(index=False), "\n")
    print("PROCESS KPIs\n", proc.to_string(index=False), "\n")
    print("ARSENAL YoY\n", ars[["game_year","pitch_name","usage","velo","spin","whiff_rate","putaway_rate","xwoba"]].to_string(index=False), "\n")
    print("BY STAND\n", stand[["game_year","stand","plate_apps","woba","xwoba","krate","bbrate","hr_rate"]].to_string(index=False), "\n")
    if len(tto): print("TTO\n", tto[["game_year","tto","plate_apps","woba","krate"]].to_string(index=False), "\n")
    print("START LOG 2026\n", slog.to_string(index=False), "\n")
    print("MONTHLY 2026\n", mon[["month","plate_apps","woba","xwoba","krate","bbrate","csw_rate"]].to_string(index=False), "\n")
    print("STAFF BENCHMARK 2026\n", bench[["player_name","pitches","plate_apps","woba","xwoba","krate","bbrate","csw_rate"]].to_string(index=False), "\n")
    print("COUNT LEVERAGE\n", lev.to_string(index=False), "\n")
    print("VELO BY SEASON (FF)\n", velo[velo.pitch=="4-Seam Fastball"].groupby("game_year").velo.agg(["mean","min","max"]).round(2).to_string(), "\n")

if __name__ == "__main__":
    main()
