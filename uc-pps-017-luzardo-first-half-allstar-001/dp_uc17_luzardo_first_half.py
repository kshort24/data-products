"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #19  (uc-pps-017)
"Jesus Luzardo — First-Half 2026 All-Star Assessment"
============================================================================

Layer-3 BUILD artifact for the Phillies Pitching (pps) value stream.
The pps mirror of uc-pos-marsh-breakout-001 (UC #18): a first-time All-Star
retrospective — results first, then the indicators that plausibly drove them,
then a persona-action narrative (manager / pitching dept / Luzardo / catcher).

Pattern lineage: UC3 (Luzardo deep dive) -> UC8 (Nola vs WAS, canonical flat
pattern) -> UC11 (Rangel vs PIT, current exemplar) -> UC18 (Marsh breakout,
first-All-Star retrospective shape) -> THIS (UC #19 / uc-pps-017).

Governance lineage (see 00/02/03/05 in the package folder):
  - data-product-owner     : sequenced as UC #19; claimed uc-pps-017
  - use-case-validator     : GO, no blocking gaps (01_strategy_intake.md)
  - source-system-profiler : entity lock pitcher==666200; phils_2025 +
                             phils_2026 parquet; 2026 cache fresh to 07-12,
                             Luzardo's last start 07-09
  - kpi-calculator         : locked cores inherited VERBATIM from Baseball
                             Functions via dp_uc11 (get_stats/nresults,
                             whiff_rate, chase_rate, putaway_rate, fpsr,
                             hard_hit_rate). NEW derived KPIs (spec'd in
                             02, provisional pending DPO ratification):
                             outs/IP-from-log, RA9-from-score-deltas, FIP,
                             CSW rate, TTO split, battery (catcher) split,
                             count-leverage funnel (PD-1..PD-7)
  - business-glossary-agent: no existing governed term redefined; PD-1..PD-7
                             provisional definitions logged in 03

DATA WINDOW / FRESHNESS:
  * MLB pitch log: phils_2025 + phils_2026 parquet, phillies_role=='pitching',
    pitcher==666200, game_type=='R', dedup on game_pk+at_bat_number+pitch_number.
  * 2026 window: 2026-03-29 .. 2026-07-09 (19 starts). Cache fresh 2026-07-12.
  * 2025 comparison season: full year, 32 starts (2025-03-29 .. 2025-09-24).
  * MANUAL CARRY-IN: 2026 All-Star selection (first career) — user-provided
    context, not derivable from the pitch log.
  * IP is reconstructed from event outs (may differ ~1 out vs official).
    Runs = score deltas while on the mound (bequeathed-runner caveat; not
    earned-run accounting — this is RA9, NOT official ERA).

OUTPUTS (NEW files, none overwritten), written to <MLB repo>/out/:
  dp_uc17_luzardo_season_line.csv       2025 vs 2026 results line (+IP, RA9, FIP)
  dp_uc17_luzardo_start_log_2026.csv    per-start log: opp, IP, K, BB, HR, runs, xwOBA
  dp_uc17_staff_benchmark_2026.csv      Phillies pitchers 2026 (>=500 pitches) context
  dp_uc17_luzardo_arsenal_yoy.csv       arsenal 2025 vs 2026: usage/velo/mvt/whiff/xwOBA
  dp_uc17_luzardo_process_kpis_yoy.csv  FPSR/chase/zone/putaway/hard-hit/CSW, 2025 vs 2026
  dp_uc17_luzardo_by_stand_yoy.csv      results by batter stand, 2025 vs 2026
  dp_uc17_luzardo_tto_yoy.csv           times-through-order splits, 2025 vs 2026
  dp_uc17_luzardo_battery_2026.csv      catcher (battery) splits, 2026
  dp_uc17_luzardo_monthly_2026.csv      monthly trend, 2026
  dp_uc17_luzardo_count_leverage_yoy.csv 2-strike funnel + first-pitch results
  dp_uc17_dq_scorecard.csv              data-quality-engineer scorecard
  dp_uc17_freshness_manifest.csv        source/window/fitness receipts
  dp_uc17_fig1_arsenal_shift.png        fig 1 — YoY usage shift x whiff
  dp_uc17_fig2_start_trend.png          fig 2 — per-start xwOBA + runs trend
  dp_uc17_fig3_tto_leash.png            fig 3 — TTO wOBA, 2025 vs 2026
============================================================================
"""
from __future__ import annotations
import os, glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

LUZARDO = 666200                   # Jesus Luzardo, MLBAM pitcher id (entity lock)
CURRENT_YEAR = 2026
ASG_NOTE = "2026 All-Star selection (first career) — user-provided carry-in"

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
PITCH_COLORS = {"4-Seam Fastball": "#E81828", "Changeup": "#FF7F0E",
                "Slider": "#1F77B4", "Curveball": "#2CA02C",
                "Sweeper": "#9467BD", "Sinker": "#8C564B"}

# ===========================================================================
# LOADERS
# ===========================================================================
def _coerce(df):
    for c in ["plate_x","plate_z","sz_top","sz_bot","pfx_x","pfx_z","release_speed",
              "release_spin_rate","launch_speed","launch_angle","strikes","balls",
              "pitch_number","woba_value","woba_denom","zone","bat_score",
              "post_bat_score","n_thruorder_pitcher"]:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def load_luzardo():
    if PHIL_DIR is None:
        raise FileNotFoundError("Could not locate data/phillies. Set MLB_DATA_ROOT.")
    frames = []
    for yr in (2025, 2026):
        f = os.path.join(PHIL_DIR, f"phils_{yr}.parquet")
        d = pd.read_parquet(f)
        d = d[(d.phillies_role == "pitching") & (d.pitcher == LUZARDO) & (d.game_type == "R")]
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
    d = d[(d.phillies_role == "pitching") & (d.game_type == "R")].drop_duplicates(
        ["game_pk", "at_bat_number", "pitch_number"])
    d = _coerce(d)
    if WOBA_CSV:
        w = pd.read_csv(WOBA_CSV)
        d = d.drop(columns=[c for c in w.columns if c != "Season" and c in d.columns])
        d = d.merge(w, left_on="game_year", right_on="Season", how="left")
    return d

# ===========================================================================
# LOCKED KPI FUNCTIONS — inherited verbatim from Baseball Functions via dp_uc11.
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

# ===========================================================================
# NEW DERIVED KPIs — kpi-calculator specs in 02_engineering_design.md
# (PD-1..PD-5, provisional pending DPO ratification). None redefines a
# governed term.
# ===========================================================================
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
    """Last pitch row of each PA (carries events + score-after)."""
    return (df.sort_values(["game_pk","at_bat_number","pitch_number"])
              .groupby(["game_pk","at_bat_number"],as_index=False).last())

def outs_and_runs(df):
    """PD-1/PD-2: outs recorded (event map) and runs while on mound
    (post_bat_score - bat_score summed over PAs). Grain: whatever slice
    df carries. Returns (outs, runs)."""
    last = pa_last(df)
    outs = last.events.map(OUTS_MAP).fillna(0).sum()
    runs = (last.post_bat_score - last.bat_score).clip(lower=0).sum()
    return int(outs), int(runs)

def ip_str(outs):
    return f"{outs//3}.{outs%3}"

def fip(df, c_fip):
    """PD-3: FIP = (13*HR + 3*(BB+HBP) - 2*K) / IP + cFIP(season)."""
    last = pa_last(df)
    hr = (last.events=="home_run").sum()
    bb = last.events.isin(["walk","intent_walk"]).sum()
    hbp = (last.events=="hit_by_pitch").sum()
    k = last.events.isin(["strikeout","strikeout_double_play"]).sum()
    outs,_ = outs_and_runs(df)
    ip = outs/3
    return (13*hr + 3*(bb+hbp) - 2*k)/ip + c_fip if ip>0 else np.nan

def csw_rate(level, df):
    """PD-4: CSW = (called strikes + whiffs) / pitches."""
    if isinstance(level, str): level=[level]
    cs = df[df.description.eq("called_strike") | df.description.isin(WHIFFS)]
    n = cs.groupby(level,as_index=False).agg(csw=("des","size"))
    tot = df.groupby(level,as_index=False).agg(pitches=("des","size"))
    out = tot.merge(n,on=level,how="left").fillna(0)
    out["csw_rate"] = out.csw/out.pitches
    return out.round(3)

def resolve_player_names(ids, phil_dir):
    """Resolve MLBAM ids to names from the data itself (batter rows) —
    no hand-keyed ids/names (UC11 rule)."""
    names = {}
    for yr in (2026, 2025, 2024):
        f = os.path.join(phil_dir, f"phils_{yr}.parquet")
        if not os.path.isfile(f): continue
        d = pd.read_parquet(f, columns=["batter","player_name","phillies_role"])
        d = d[d.phillies_role=="batting"]
        for i in ids:
            if i in names: continue
            s = d[d.batter==i].player_name
            if len(s): names[i] = s.mode().iat[0]
        if all(i in names for i in ids): break
    return {i: names.get(i, f"id:{i}") for i in ids}

# ===========================================================================
# BUILD
# ===========================================================================
def main():
    lz = load_luzardo()
    d26 = lz[lz.game_year==2026].copy()
    d25 = lz[lz.game_year==2025].copy()
    w = pd.read_csv(WOBA_CSV).set_index("Season")

    # --- 1. season results line: 2025 (full) vs 2026 (first half) --------
    line = nresults(["game_year"], lz)
    extra = []
    for yr, d in ((2025,d25),(2026,d26)):
        outs, runs = outs_and_runs(d)
        extra.append(dict(game_year=yr, starts=d.game_pk.nunique(),
                          ip=ip_str(outs), outs=outs, runs_on_mound=runs,
                          ra9=round(runs/(outs/3)*9,2),
                          fip=round(fip(d, w.loc[yr,"cFIP"]),2)))
    line = line.merge(pd.DataFrame(extra), on="game_year")
    line.to_csv(os.path.join(OUT_DIR,"dp_uc17_luzardo_season_line.csv"),index=False)

    # --- 2. per-start log 2026 -------------------------------------------
    rows=[]
    for gpk, g in d26.groupby("game_pk"):
        last = pa_last(g)
        outs, runs = outs_and_runs(g)
        opp = g.away_team.iat[0] if g.home_team.iat[0]=="PHI" else g.home_team.iat[0]
        rows.append(dict(
            game_date=str(g.game_date.max())[:10], opp=opp,
            pitches=len(g), ip=ip_str(outs),
            pa=int((~last.events.replace(np.nan,"NA").isin(["NA","pickoff_1b"])).sum()),
            k=int(last.events.isin(["strikeout","strikeout_double_play"]).sum()),
            bb=int(last.events.isin(["walk","intent_walk"]).sum()),
            hr=int((last.events=="home_run").sum()),
            runs=runs,
            xwoba=round(g.estimated_woba_using_speedangle.mean(),3),
            csw=float(csw_rate(["game_year"],g).csw_rate.iat[0])))
    slog = pd.DataFrame(rows).sort_values("game_date").reset_index(drop=True)
    slog.to_csv(os.path.join(OUT_DIR,"dp_uc17_luzardo_start_log_2026.csv"),index=False)

    # --- 3. staff benchmark 2026 (>=500 pitches) --------------------------
    staff = load_staff_2026()
    bench = nresults(["player_name"], staff)
    bench = bench[bench.pitches>=500].sort_values("woba")
    xw = staff.groupby("player_name",as_index=False).agg(
        xwoba=("estimated_woba_using_speedangle","mean")).round(3)
    bench = bench.drop(columns=[c for c in ["xwoba"] if c in bench]).merge(xw,on="player_name")
    csw_b = csw_rate(["player_name"], staff)[["player_name","csw_rate"]]
    bench = bench.merge(csw_b, on="player_name")
    bench.to_csv(os.path.join(OUT_DIR,"dp_uc17_staff_benchmark_2026.csv"),index=False)

    # --- 4. arsenal YoY ----------------------------------------------------
    ars_rows=[]
    for yr, d in ((2025,d25),(2026,d26)):
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
    ars.to_csv(os.path.join(OUT_DIR,"dp_uc17_luzardo_arsenal_yoy.csv"),index=False)

    # --- 5. process KPIs YoY ----------------------------------------------
    proc=[]
    for yr, d in ((2025,d25),(2026,d26)):
        proc.append(dict(game_year=yr,
            first_pitch_strike_rate=float(fpsr(["game_year"],d).first_pitch_strike_rate.iat[0]),
            chase_rate=float(chase_rate(["game_year"],d).chase_rate.iat[0]),
            in_zone_rate=float(chase_rate(["game_year"],d).in_zone_rate.iat[0]),
            putaway_rate=float(putaway_rate(["game_year"],d).putaway_rate.iat[0]),
            hard_hit_rate=float(hard_hit_rate(["game_year"],d).hard_hit_rate.iat[0]),
            csw_rate=float(csw_rate(["game_year"],d).csw_rate.iat[0]),
            whiff_rate=float(whiff_rate(["game_year"],d).whiff_rate.iat[0])))
    proc = pd.DataFrame(proc).round(3)
    proc.to_csv(os.path.join(OUT_DIR,"dp_uc17_luzardo_process_kpis_yoy.csv"),index=False)

    # --- 6. by stand YoY ----------------------------------------------------
    stand = nresults(["game_year","stand"], lz)
    xws = lz.groupby(["game_year","stand"],as_index=False).agg(
        xwoba=("estimated_woba_using_speedangle","mean")).round(3)
    stand = stand.merge(xws, on=["game_year","stand"])
    stand.to_csv(os.path.join(OUT_DIR,"dp_uc17_luzardo_by_stand_yoy.csv"),index=False)

    # --- 7. TTO YoY ---------------------------------------------------------
    lz_t = lz[lz.n_thruorder_pitcher.notna()].copy()
    lz_t["tto"] = lz_t.n_thruorder_pitcher.clip(upper=3).astype(int)
    tto = nresults(["game_year","tto"], lz_t)
    tto.to_csv(os.path.join(OUT_DIR,"dp_uc17_luzardo_tto_yoy.csv"),index=False)

    # --- 8. battery (catcher) splits 2026 ----------------------------------
    cids = [int(x) for x in d26.fielder_2.dropna().unique()]
    cnames = resolve_player_names(cids, PHIL_DIR)
    d26c = d26.copy(); d26c["catcher"] = d26c.fielder_2.map(cnames)
    bat = nresults(["catcher"], d26c)
    bat = bat.merge(csw_rate(["catcher"],d26c)[["catcher","csw_rate"]],on="catcher")
    bat = bat.merge(chase_rate(["catcher"],d26c)[["catcher","chase_rate","in_zone_rate"]],on="catcher")
    bat = bat.merge(putaway_rate(["catcher"],d26c)[["catcher","putaway_rate"]],on="catcher")
    xwc = d26c.groupby("catcher",as_index=False).agg(
        xwoba=("estimated_woba_using_speedangle","mean")).round(3)
    bat = bat.drop(columns=[c for c in ["xwoba"] if c in bat]).merge(xwc,on="catcher")
    bat.to_csv(os.path.join(OUT_DIR,"dp_uc17_luzardo_battery_2026.csv"),index=False)

    # --- 9. monthly trend 2026 ---------------------------------------------
    d26m = d26.copy(); d26m["month"] = d26m.game_date.astype(str).str[:7]
    mon = nresults(["month"], d26m)
    mon = mon.merge(csw_rate(["month"],d26m)[["month","csw_rate"]],on="month")
    xwm = d26m.groupby("month",as_index=False).agg(
        xwoba=("estimated_woba_using_speedangle","mean")).round(3)
    mon = mon.drop(columns=[c for c in ["xwoba"] if c in mon]).merge(xwm,on="month")
    mon.to_csv(os.path.join(OUT_DIR,"dp_uc17_luzardo_monthly_2026.csv"),index=False)

    # --- 10. count leverage YoY ---------------------------------------------
    lev=[]
    for yr, d in ((2025,d25),(2026,d26)):
        last = pa_last(d)
        pa_n = (~last.events.replace(np.nan,"NA").isin(["NA","pickoff_1b"])).sum()
        two_k = d[d.strikes==2].groupby(["game_pk","at_bat_number"]).ngroups
        ahead = d[(d.balls<d.strikes)].shape[0]/len(d)
        lev.append(dict(game_year=yr, pa=int(pa_n),
            pa_reaching_2strikes=int(two_k),
            share_pa_to_2strikes=round(two_k/pa_n,3),
            pitch_share_ahead_in_count=round(ahead,3)))
    lev = pd.DataFrame(lev)
    lev.to_csv(os.path.join(OUT_DIR,"dp_uc17_luzardo_count_leverage_yoy.csv"),index=False)

    # --- 11. DQ scorecard + freshness manifest ------------------------------
    key_cdes=["pitch_name","release_speed","plate_x","plate_z","zone","description",
              "events","stand","woba_value","woba_denom","fielder_2",
              "n_thruorder_pitcher","bat_score","post_bat_score"]
    dq=[dict(check="entity_lock",detail="pitcher==666200 only",
             result="PASS" if set(lz.pitcher.unique())=={LUZARDO} else "FAIL"),
        dict(check="dedup",detail="game_pk+at_bat_number+pitch_number unique",
             result="PASS" if not lz.duplicated(["game_pk","at_bat_number","pitch_number"]).any() else "FAIL"),
        dict(check="game_type",detail="regular season only",
             result="PASS" if set(lz.game_type.unique())=={"R"} else "FAIL"),
        dict(check="weights_join",detail="wOBA weights joined for both seasons",
             result="PASS" if lz.wBB.notna().all() else "FAIL")]
    for c in key_cdes:
        nn = lz[c].notna().mean() if c in lz.columns else 0.0
        dq.append(dict(check=f"completeness:{c}",detail="pitch log non-null share",
                       result=round(float(nn),3)))
    pd.DataFrame(dq).to_csv(os.path.join(OUT_DIR,"dp_uc17_dq_scorecard.csv"),index=False)

    fresh=pd.DataFrame([
        dict(source="data/phillies/phils_2026.parquet",
             window=f"2026-03-29..{str(d26.game_date.max())[:10]} (cache to 2026-07-12)",
             rows=len(d26), note="2026 MLB pitch log, entity-locked, R games, 19 starts"),
        dict(source="data/phillies/phils_2025.parquet",
             window="2025-03-29..2025-09-24", rows=len(d25),
             note="2025 full-season comparison, 32 starts"),
        dict(source="user-provided context", window="2026-07-13",
             rows=0, note=ASG_NOTE),
        dict(source="derived", window="n/a", rows=0,
             note="IP from event-outs map; runs=score deltas on mound (RA9, not ERA)"),
    ])
    fresh.to_csv(os.path.join(OUT_DIR,"dp_uc17_freshness_manifest.csv"),index=False)

    # --- 12. figures ---------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # fig 1: YoY usage shift x whiff
    order = ["Sweeper","4-Seam Fastball","Changeup","Sinker","Slider"]
    fig,axes=plt.subplots(1,2,figsize=(11,4.8),sharey=True)
    for ax,yr in zip(axes,(2025,2026)):
        a = ars[ars.game_year==yr].set_index("pitch_name").reindex(order)
        x=np.arange(len(order))
        ax.bar(x-.2,a.usage,.4,color=[PITCH_COLORS.get(o,PHI_GRAY) for o in order],alpha=.9,label="usage")
        ax.bar(x+.2,a.whiff_rate,.4,color=PHI_NAVY,alpha=.55,label="whiff rate")
        for xx,(m,ww) in enumerate(zip(a.usage,a.whiff_rate)):
            if pd.notna(m): ax.text(xx-.2,m+.01,f"{m:.0%}",ha="center",fontsize=8)
            if pd.notna(ww): ax.text(xx+.2,ww+.01,f"{ww:.0%}",ha="center",fontsize=8,color=PHI_NAVY)
        ax.set_xticks(x); ax.set_xticklabels(["SW","FF","CH","SI","SL"],fontsize=9)
        ax.set_title(f"{yr}" + (" (full)" if yr==2025 else " (first half)"),
                     color=PHI_NAVY,weight="bold",fontsize=10)
        ax.set_ylim(0,.55); ax.grid(axis="y",color=PHI_LGRAY,zorder=0)
    axes[0].legend(fontsize=8)
    fig.suptitle("Luzardo arsenal — the sweeper became the primary; the slider is gone",
                 color=PHI_NAVY,weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR,"dp_uc17_fig1_arsenal_shift.png"),dpi=160)
    plt.close(fig)

    # fig 2: per-start xwOBA + runs
    fig,ax=plt.subplots(figsize=(11,4.6))
    x=np.arange(len(slog))
    ax.bar(x,slog.runs,color=PHI_LGRAY,zorder=2,label="runs while on mound")
    ax2=ax.twinx()
    ax2.plot(x,slog.xwoba,color=PHI_RED,marker="o",lw=2,zorder=3,label="start xwOBA (against)")
    ax2.axhline(slog.xwoba.mean(),color=PHI_NAVY,ls="--",lw=1,
                label=f"first-half mean xwOBA {slog.xwoba.mean():.3f}")
    ax.set_xticks(x); ax.set_xticklabels(slog.game_date.str[5:]+" "+slog.opp,rotation=60,fontsize=7.5,ha="right")
    ax.set_ylabel("runs",color=PHI_GRAY); ax2.set_ylabel("xwOBA",color=PHI_RED)
    ax.set_ylim(0,max(slog.runs.max(),6)+1)
    h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
    ax2.legend(h1+h2,l1+l2,fontsize=8,loc="upper left")
    ax.set_title("Luzardo 2026, start by start — quality of contact allowed vs runs",
                 color=PHI_NAVY,weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR,"dp_uc17_fig2_start_trend.png"),dpi=160)
    plt.close(fig)

    # fig 3: TTO wOBA 2025 vs 2026
    fig,ax=plt.subplots(figsize=(8,4.4))
    t25=tto[tto.game_year==2025].set_index("tto").woba.reindex([1,2,3])
    t26=tto[tto.game_year==2026].set_index("tto").woba.reindex([1,2,3])
    pa25=tto[tto.game_year==2025].set_index("tto").plate_apps.reindex([1,2,3])
    pa26=tto[tto.game_year==2026].set_index("tto").plate_apps.reindex([1,2,3])
    x=np.arange(3)
    ax.bar(x-.2,t25,.4,color=PHI_GRAY,label="2025 (full)")
    ax.bar(x+.2,t26,.4,color=PHI_RED,label="2026 (first half)")
    for xx,(a_,b_,pa_,pb_) in enumerate(zip(t25,t26,pa25,pa26)):
        ax.text(xx-.2,a_+.005,f"{a_:.3f}\n({int(pa_)} PA)",ha="center",fontsize=8)
        ax.text(xx+.2,b_+.005,f"{b_:.3f}\n({int(pb_)} PA)",ha="center",fontsize=8,color=PHI_NAVY)
    ax.set_xticks(x); ax.set_xticklabels(["1st time thru","2nd time thru","3rd+ time thru"])
    ax.set_ylabel("wOBA against"); ax.legend(fontsize=9)
    ax.grid(axis="y",color=PHI_LGRAY,zorder=0)
    ax.set_title("Times through the order — the manager's leash question",
                 color=PHI_NAVY,weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR,"dp_uc17_fig3_tto_leash.png"),dpi=160)
    plt.close(fig)

    # --- console receipts ----------------------------------------------------
    pd.set_option("display.width", 220)
    print("UC-PPS-017 build complete.\n")
    print("SEASON LINE\n", line.to_string(index=False), "\n")
    print("START LOG 2026\n", slog.to_string(index=False), "\n")
    print("STAFF BENCHMARK\n", bench.to_string(index=False), "\n")
    print("ARSENAL YoY\n", ars[["game_year","pitch_name","usage","velo","whiff_rate","putaway_rate","xwoba"]].to_string(index=False), "\n")
    print("PROCESS KPIs\n", proc.to_string(index=False), "\n")
    print("BY STAND\n", stand.to_string(index=False), "\n")
    print("TTO\n", tto.to_string(index=False), "\n")
    print("BATTERY\n", bat.to_string(index=False), "\n")
    print("MONTHLY\n", mon.to_string(index=False), "\n")
    print("COUNT LEVERAGE\n", lev.to_string(index=False), "\n")

if __name__ == "__main__":
    main()
