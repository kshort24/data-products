"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #39  (uc-pps-028)
"Jesus Luzardo — 2026 Consistency Audit & Pre-Scout vs ARI (2026-09-01)"
============================================================================

Layer-3 BUILD artifact for the Phillies Pitching (pps) value stream.

WHAT THIS IS. A direct extension of uc-pps-017 (UC #19, the All-Star-break
first-half assessment). That product closed with five second-half watch items;
this one closes them against 8 additional starts, then adversarially tests the
DPO's stated premise -- "maybe the Phillies' most consistent pitcher in 2026,
very good since the end of April" -- and finally applies the profile to
tonight's opponent (ARI, 2026-09-01).

Pattern lineage: UC3 (Luzardo deep dive) -> UC6 (opponent dimension) ->
UC8 (canonical flat pattern) -> UC11 (multi-level evidence) -> UC17 (this
subject's first-half assessment) -> UC38 (TR-1 travel test / TR-2 breakpoint
scan, inherited here) -> THIS (UC #39 / uc-pps-028).

GOVERNANCE LINEAGE (see 00/02/03/05 in this package folder):
  data-product-owner      : sequenced UC #39; claimed uc-pps-028 / dp_uc39
  use-case-validator      : GO with 3 non-blocking gaps (01_strategy_intake.md)
  source-system-profiler  : entity lock pitcher==666200; phils_2025+phils_2026
                            parquet; 2026 cache fresh to 2026-08-30; last
                            Luzardo start 2026-08-26
  kpi-calculator          : locked cores inherited VERBATIM from Baseball
                            Functions via dp_uc11/dp_uc17 (get_stats, nresults,
                            whiff_rate, chase_rate, putaway_rate, fpsr,
                            hard_hit_rate, csw_rate, outs_and_runs, fip).
                            NEW provisional family CN-1..CN-6 (consistency)
                            + AR-1..AR-2 (opponent lens) spec'd in 02.
  business-glossary-agent : no governed term redefined.

THE ADVERSARIAL DESIGN (why this build can falsify its own premise).
uc-pps-027 shipped calibration finding C-1: a harness built around a causal
claim the client already believes will fill cleanly and be wrong. The DPO's
premise here is a SUPERLATIVE ("most consistent") over a SELF-CHOSEN WINDOW
("since the end of April"). Both are researcher degrees of freedom. So:
  * "Consistency" is operationalised as SIX independent axes (CN-1..CN-6),
    reported separately. No composite index -- a composite invites weighting
    until the desired name wins.
  * Every axis is ranked against the whole Phillies rotation, not narrated
    about Luzardo alone.
  * The window boundary is SCANNED across 8 candidate breakpoints (TR-2,
    inherited from uc-pps-027). A rank that survives the scan is a finding;
    a rank that only exists at 2026-05-01 is a boundary artefact and is
    reported as such (guardrail G6).

DATA WINDOW / FRESHNESS:
  * MLB pitch log: phils_2025 + phils_2026 parquet, phillies_role=='pitching',
    game_type=='R', deduped on game_pk+at_bat_number+pitch_number.
  * Luzardo 2026 window: 2026-03-29 .. 2026-08-26 (27 starts).
  * Comparison seasons: 2025 full (32 starts), 2026 H1 (19 GS, the uc-pps-017
    window, closes 2026-07-09), 2026 H2 (8 GS, 2026-07-18 .. 2026-08-26).
  * MANUAL CARRY-IN: tonight's opponent (ARI) and game date (2026-09-01) are
    DPO-supplied. NO confirmed ARI lineup was available at build time -- the
    hitter panel is built from the batters Luzardo actually faced and is
    labelled UNVERIFIED throughout.
  * IP reconstructed from event outs (may differ ~1 out from official).
    Runs = score deltas while on the mound -> RA9, NOT official ERA.

OUTPUTS (NEW files only; nothing from a prior UC is overwritten) -> ./out/
============================================================================
"""
from __future__ import annotations
import os, sys, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- entity lock
LUZARDO      = 666200           # Jesus Luzardo, MLBAM pitcher id
OPPONENT     = "AZ"             # Arizona Diamondbacks (Statcast team abbr)
GAME_DATE    = "2026-09-01"     # DPO carry-in
ASB_LAST_H1  = "2026-07-09"     # his final pre-All-Star start (uc-pps-017 close)
PREMISE_BREAK = "2026-05-01"    # DPO premise: "since the end of April"
BREAK_SCAN   = ["2026-04-15","2026-04-20","2026-04-26","2026-05-01",
                "2026-05-08","2026-05-15","2026-06-01","2026-06-15"]
MIN_GS_COHORT = 8               # rotation cohort floor for consistency ranking
MIN_PA_START  = 15              # a start must reach this PA to enter dispersion

# ------------------------------------------------------------- portable paths
_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "phillies"),
    os.path.expanduser("~/mnt/MLB/data/phillies"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies",
]
PHIL_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
if PHIL_DIR is None:
    sys.exit("FATAL: data/phillies not found. Set MLB_DATA_ROOT. "
             "No number is published without the plane mounted (skill rule #1).")
REPO_ROOT = os.path.dirname(os.path.dirname(PHIL_DIR))
OPPS_DIR  = os.path.join(REPO_ROOT, "data", "opponents")
OUT_DIR   = os.path.join(HERE, "out"); os.makedirs(OUT_DIR, exist_ok=True)
_WOBA_CANDIDATES = [
    os.environ.get("MLB_WOBA_CSV", ""),
    os.path.join(REPO_ROOT, "wOBA and FIP Constants.csv"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv",
]
WOBA_CSV = next((p for p in _WOBA_CANDIDATES if p and os.path.isfile(p)), None)

def OUT(name): return os.path.join(OUT_DIR, f"dp_uc39_{name}")

# ------------------------------------------------- locked vocabulary (UC8/11)
SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]
XW = "estimated_woba_using_speedangle"

PHI_RED, PHI_NAVY, PHI_GRAY, PHI_LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
PITCH_COLORS = {"4-Seam Fastball": "#E81828", "Changeup": "#FF7F0E",
                "Slider": "#1F77B4", "Curveball": "#2CA02C",
                "Sweeper": "#9467BD", "Sinker": "#8C564B",
                "Cutter": "#17BECF", "Split-Finger": "#BCBD22"}

DQ_ROWS, FRESH_ROWS = [], []
def dq(rule, scope, result, detail=""):
    DQ_ROWS.append(dict(rule=rule, scope=scope, result=result, detail=detail))
    print(f"  [{result:4s}] {rule:38s} {detail}")
def fresh(item, value, source, note=""):
    FRESH_ROWS.append(dict(item=item, value=str(value), source=source, note=note))

# ===========================================================================
# LOADERS
# ===========================================================================
_NUM = ["plate_x","plate_z","sz_top","sz_bot","pfx_x","pfx_z","release_speed",
        "release_spin_rate","launch_speed","launch_angle","strikes","balls",
        "pitch_number","woba_value","woba_denom","zone","bat_score",
        "post_bat_score","n_thruorder_pitcher","at_bat_number","inning",
        "estimated_woba_using_speedangle","estimated_ba_using_speedangle",
        "release_extension","effective_speed"]

def _coerce(df):
    for c in _NUM:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def _join_woba(df):
    if not WOBA_CSV: return df
    w = pd.read_csv(WOBA_CSV)
    df = df.drop(columns=[c for c in w.columns if c != "Season" and c in df.columns])
    return df.merge(w, left_on="game_year", right_on="Season", how="left")

def load_staff(years=(2025, 2026)):
    """All Phillies pitching, regular season, deduped. The cohort frame."""
    frames = []
    for yr in years:
        f = os.path.join(PHIL_DIR, f"phils_{yr}.parquet")
        if not os.path.isfile(f): continue
        d = pd.read_parquet(f)
        d = d[(d.phillies_role == "pitching") & (d.game_type == "R")]
        frames.append(d)
    r = pd.concat(frames, ignore_index=True).drop_duplicates(
        ["game_pk", "at_bat_number", "pitch_number"])
    r = _coerce(r)
    r["game_date"] = pd.to_datetime(r.game_date).dt.strftime("%Y-%m-%d")
    r["opp"] = np.where(r.home_team.eq("PHI"), r.away_team, r.home_team)
    return _join_woba(r)

def load_luzardo_career():
    """2019-2024 pre-Phillies log (opponents cache) for career H2H only."""
    f = os.path.join(OPPS_DIR, "luzardo.parquet")
    if not os.path.isfile(f): return None
    d = pd.read_parquet(f)
    d = d[d.pitcher == LUZARDO]
    if "game_type" in d.columns: d = d[d.game_type == "R"]
    d = d.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    d = _coerce(d)
    d["game_date"] = pd.to_datetime(d.game_date).dt.strftime("%Y-%m-%d")
    return _join_woba(d)

# ===========================================================================
# LOCKED KPI FUNCTIONS — inherited VERBATIM from Baseball Functions via
# dp_uc11 -> dp_uc17. Do not re-derive; any change is a governance event.
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
    xwoba=df.groupby(level,as_index=False).agg(xwoba=(XW,"mean"))
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
                "ba","obp","slg","ops","woba","krate","bbrate","hr_rate","xwoba"]
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
    tracked=df[(df.type=="X")&(df.launch_speed.notna())].groupby(level,as_index=False).agg(bips_tracked=("des","size"))
    out=bips.merge(tracked,on=level,how="left").merge(hh,on=level,how="left").fillna(0)
    out["hard_hit_rate"]=out.hard_hits/out.bips            # locked (O-8 known defect)
    out["hard_hit_rate_tracked"]=out.hard_hits/out.bips_tracked.replace(0,np.nan)  # O-8 shadow
    return out.round(3)

def csw_rate(level, df):
    """PD-4 (uc-pps-017): CSW = (called strikes + whiffs) / pitches."""
    if isinstance(level, str): level=[level]
    cs = df[df.description.eq("called_strike") | df.description.isin(WHIFFS)]
    n = cs.groupby(level,as_index=False).agg(csw=("des","size"))
    tot = df.groupby(level,as_index=False).agg(pitches=("des","size"))
    out = tot.merge(n,on=level,how="left").fillna(0)
    out["csw_rate"] = out.csw/out.pitches
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

def ip_str(outs): return f"{outs//3}.{outs%3}"

def fip(df, c_fip):
    last = pa_last(df)
    hr = (last.events=="home_run").sum()
    bb = last.events.isin(["walk","intent_walk"]).sum()
    hbp = (last.events=="hit_by_pitch").sum()
    k = last.events.isin(["strikeout","strikeout_double_play"]).sum()
    outs,_ = outs_and_runs(df)
    ip = outs/3
    return (13*hr + 3*(bb+hbp) - 2*k)/ip + c_fip if ip>0 else np.nan

# ===========================================================================
# NEW PROVISIONAL KPI FAMILY — CN-1..CN-6 "Start-Level Consistency"
# Full kpi-calculator specs in 02_engineering_design.md. Provisional pending
# DPO ratification (escalation E-2). None of these redefines a governed term;
# Rule-1 grep for prior art is logged in 00_dpo_orchestration_record.md §4.
#
# DESIGN NOTE (the whole point of this family): "consistent" is a claim about
# VARIANCE, "very good" is a claim about LEVEL. They are different questions
# and a pitcher can win one and lose the other. Every axis below is reported
# on its own; there is deliberately NO composite index, because a composite is
# a weighting knob and a weighting knob is how a premise gets confirmed.
# ===========================================================================
def identify_starts(staff):
    """A 'start' = the Phillies pitcher who threw the game's first Phillies
    pitch. Derived from the log (no roster carry-in, no hand-keyed ids)."""
    o = staff.sort_values(["game_pk","inning","at_bat_number","pitch_number"])
    first = o.groupby("game_pk", as_index=False).first()[["game_pk","pitcher","game_date"]]
    first = first.rename(columns={"pitcher":"starter"})
    return first

def start_frame(df, starts_idx):
    """Per-start row set for ONE pitcher, vectorised over game_pk.
    outs, runs, PA, xwOBA, wOBA, K, BB, HR. Grain: one row per game_pk."""
    if not len(df):
        return pd.DataFrame(columns=["game_pk","game_date","opp","home","pitches","outs","ip",
                                     "runs","pa","k","bb","hr","woba","xwoba","xwoba_n",
                                     "is_start","days_rest"])
    last = pa_last(df)
    last = last.copy()
    last["_outs"] = last.events.map(OUTS_MAP).fillna(0)
    last["_runs"] = (last.post_bat_score - last.bat_score).clip(lower=0)
    last["_pa"]   = (~last.events.replace(np.nan,"NA").isin(["NA","pickoff_1b"])).astype(int)
    last["_k"]    = last.events.isin(["strikeout","strikeout_double_play"]).astype(int)
    last["_bb"]   = last.events.isin(["walk","intent_walk"]).astype(int)
    last["_hr"]   = (last.events == "home_run").astype(int)
    agg = last.groupby("game_pk", as_index=False).agg(
        outs=("_outs","sum"), runs=("_runs","sum"), pa=("_pa","sum"),
        k=("_k","sum"), bb=("_bb","sum"), hr=("_hr","sum"))
    meta = df.groupby("game_pk", as_index=False).agg(
        game_date=("game_date","min"), opp=("opp","first"),
        home_team=("home_team","first"), pitches=("pitch_number","size"))
    xw = df.copy(); xw["_xw"] = pd.to_numeric(xw[XW], errors="coerce")
    xwa = xw.groupby("game_pk", as_index=False).agg(xwoba=("_xw","mean"), xwoba_n=("_xw","count"))
    nres = nresults(["game_pk"], df)[["game_pk","woba"]]
    out = (meta.merge(agg, on="game_pk").merge(xwa, on="game_pk")
                .merge(nres, on="game_pk", how="left"))
    out["home"] = out.home_team.eq("PHI")
    out["ip"] = out.outs.astype(int).map(ip_str)
    out["is_start"] = out.game_pk.isin(set(starts_idx))
    out = out.drop(columns=["home_team"]).sort_values("game_date").reset_index(drop=True)
    for c in ("outs","runs","pa","k","bb","hr","pitches"):
        out[c] = out[c].astype(int)
    out["days_rest"] = pd.to_datetime(out.game_date).diff().dt.days
    return out

def consistency_axes(sf, label):
    """CN-1..CN-6 over a per-start frame `sf` already filtered to a window."""
    s = sf[sf.is_start & (sf.pa >= MIN_PA_START)].copy()
    n = len(s)
    if n == 0:
        return None
    xw = s.xwoba.dropna()
    # CN-4 rolling-3 range
    r3 = []
    xs = s.xwoba.tolist()
    for i in range(len(xs) - 2):
        w = [v for v in xs[i:i+3] if pd.notna(v)]
        if len(w) == 3: r3.append(max(w) - min(w))
    gaps = s.days_rest.dropna()
    return dict(
        who=label, starts=n,
        pa=int(s.pa.sum()), outs=int(s.outs.sum()), ip=ip_str(int(s.outs.sum())),
        # LEVEL (context for the variance axes — not a consistency axis)
        mean_start_xwoba=round(float(xw.mean()), 4) if len(xw) else np.nan,
        agg_xwoba=np.nan,   # filled by caller from the pooled frame
        ra9=round(s.runs.sum() / (s.outs.sum()/3) * 9, 2) if s.outs.sum() else np.nan,
        # CN-1 dispersion of start xwOBA (lower = steadier)
        cn1_xwoba_sd=round(float(xw.std(ddof=0)), 4) if len(xw) > 1 else np.nan,
        cn1_xwoba_iqr=round(float(xw.quantile(.75) - xw.quantile(.25)), 4) if len(xw) > 3 else np.nan,
        # CN-2 floor rate: >=5.0 IP AND <=3 runs
        cn2_floor_rate=round(float(((s.outs >= 15) & (s.runs <= 3)).mean()), 3),
        cn2_floor_n=int(((s.outs >= 15) & (s.runs <= 3)).sum()),
        # CN-3 blow-up rate: >=5 runs OR <4.0 IP
        cn3_blowup_rate=round(float(((s.runs >= 5) | (s.outs < 12)).mean()), 3),
        cn3_blowup_n=int(((s.runs >= 5) | (s.outs < 12)).sum()),
        # CN-4 mean rolling-3-start xwOBA range
        cn4_roll3_range=round(float(np.mean(r3)), 4) if r3 else np.nan,
        # CN-5 turn reliability
        cn5_median_days_rest=float(gaps.median()) if len(gaps) else np.nan,
        cn5_long_gaps=int((gaps >= 10).sum()),
        cn5_pitch_min=int(s.pitches.min()), cn5_pitch_max=int(s.pitches.max()),
        cn5_pitch_sd=round(float(s.pitches.std(ddof=0)), 1),
        # CN-6 length dependability
        cn6_mean_outs=round(float(s.outs.mean()), 2),
        cn6_outs_sd=round(float(s.outs.std(ddof=0)), 2),
        cn6_ip_per_start=round(float(s.outs.mean()/3), 2),
    )

def rank_cohort(rows, lower_is_better):
    """Rank each axis independently. Returns a tidy long frame."""
    df = pd.DataFrame(rows)
    out = []
    for col, lower in lower_is_better.items():
        if col not in df.columns: continue
        sub = df[["who", col]].dropna()
        if not len(sub): continue
        sub = sub.sort_values(col, ascending=lower).reset_index(drop=True)
        sub["rank"] = np.arange(1, len(sub)+1)
        sub["axis"] = col
        sub["better"] = "lower" if lower else "higher"
        out.append(sub.rename(columns={col: "value"})[["axis","who","value","rank","better"]])
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()

# ===========================================================================
# BUILD
# ===========================================================================
def main():
    print("\n=== dp_uc39 · uc-pps-028 · Luzardo consistency audit + ARI pre-scout ===\n")
    staff = load_staff((2025, 2026))
    s26 = staff[staff.game_year == 2026].copy()
    s25 = staff[staff.game_year == 2025].copy()
    wc  = pd.read_csv(WOBA_CSV).set_index("Season")

    # ---------------------------------------------------------- A. freshness
    cache_max = staff.game_date.max()
    lz = staff[staff.pitcher == LUZARDO].copy()
    lz26, lz25 = lz[lz.game_year == 2026].copy(), lz[lz.game_year == 2025].copy()
    fresh("phils_2026 parquet max game_date", s26.game_date.max(), "data/phillies/phils_2026.parquet")
    fresh("phils_2025 parquet max game_date", s25.game_date.max(), "data/phillies/phils_2025.parquet")
    fresh("Luzardo last start in log", lz26.game_date.max(), "pitch log",
          "T-6 vs the 2026-09-01 game date")
    fresh("Luzardo 2026 starts in window", lz26.game_pk.nunique(), "pitch log")
    fresh("game date / opponent", f"{GAME_DATE} vs {OPPONENT}", "DPO carry-in",
          "MANUAL — not derivable from the log")
    fresh("ARI confirmed lineup", "NOT AVAILABLE", "n/a",
          "UNVERIFIED — hitter panel is faced-batters + career H2H, labelled throughout")
    fresh("premise breakpoint", PREMISE_BREAK, "DPO prose 'since the end of April'",
          f"scanned across {len(BREAK_SCAN)} boundaries (TR-2)")
    fresh("build executed", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"), "this run")

    # --------------------------------------------------------------- B. DQ
    print("DQ scorecard:")
    dq("ENTITY-LOCK: pitcher id only", "luzardo frame",
       "PASS" if lz.pitcher.nunique() == 1 and lz.pitcher.iat[0] == LUZARDO else "FAIL",
       f"pitcher=={LUZARDO}, {lz.pitcher.nunique()} distinct id(s), no name filter used")
    nm = lz.player_name.dropna().unique().tolist()
    dq("ENTITY-LOCK: single resolved name", "luzardo frame",
       "PASS" if len(nm) == 1 else "WARN", f"{nm}")
    dupes = lz.duplicated(["game_pk","at_bat_number","pitch_number"]).sum()
    dq("DEDUP: pitch grain unique", "luzardo frame", "PASS" if dupes == 0 else "FAIL",
       f"{dupes} duplicate (game_pk, at_bat_number, pitch_number)")
    dq("GAME-TYPE: regular season only", "all frames",
       "PASS" if set(staff.game_type.unique()) == {"R"} else "FAIL",
       f"game_type values {sorted(staff.game_type.unique())}")
    # the xwOBA denominator assertion — this is the one that matters
    pl = pa_last(lz26); xw_pa = pd.to_numeric(pl[XW], errors="coerce")
    xw_pitch = pd.to_numeric(lz26[XW], errors="coerce")
    dq("XWOBA-GRAIN: field populated on PA-terminating rows only", "lz 2026",
       "PASS" if int(xw_pitch.notna().sum()) == int(xw_pa.notna().sum()) else "FAIL",
       f"{int(xw_pitch.notna().sum())} non-null pitch rows == {int(xw_pa.notna().sum())} non-null PA rows "
       f"-> pitch-level mean IS a per-PA xwOBA, not xwOBAcon")
    miss = pl[xw_pa.isna()].events.fillna("NA").value_counts().to_dict()
    dq("XWOBA-COVERAGE: PA without an xwOBA value", "lz 2026",
       "PASS" if len(pl) and (xw_pa.isna().mean() < .03) else "WARN",
       f"{int(xw_pa.isna().sum())}/{len(pl)} PA uncovered: {miss}")
    tp = int((pl.events == "truncated_pa").sum())
    dq("O-5 truncated_pa present (known open defect)", "lz 2026",
       "WARN" if tp else "PASS", f"{tp} truncated_pa counted as PA by locked get_stats")
    bip = lz26[lz26.type == "X"]
    dq("O-8 hard_hit denominator (known open defect)", "lz 2026", "WARN",
       f"{int(bip.launch_speed.isna().sum())}/{len(bip)} BIP untracked; both locked and "
       f"tracked-denominator rates emitted")
    # D-1 FIX: a CDE is only "incomplete" at the grain it is DEFINED on.
    # `events` exists once per PA; `launch_speed` once per tracked BIP. Testing
    # either at pitch grain manufactures a FAIL out of the schema's own shape.
    GRAIN = {
        "zone": ("pitch", lz26), "strikes": ("pitch", lz26), "balls": ("pitch", lz26),
        "pitch_number": ("pitch", lz26), "n_thruorder_pitcher": ("pitch", lz26),
        "description": ("pitch", lz26), "pitch_name": ("pitch", lz26),
        "stand": ("pitch", lz26), "post_bat_score": ("pitch", lz26),
        "bat_score": ("pitch", lz26), "release_speed": ("pitch", lz26),
        "events": ("PA-terminating", pl),
        "estimated_woba_using_speedangle": ("PA-terminating", pl),
        "launch_speed": ("ball-in-play", lz26[lz26.type == "X"]),
        "launch_angle": ("ball-in-play", lz26[lz26.type == "X"]),
    }
    for c, (grain, frame) in GRAIN.items():
        nn = frame[c].notna().mean() if c in frame.columns and len(frame) else 0.0
        dq(f"CDE completeness: {c} @ {grain}", "lz 2026",
           "PASS" if nn > .90 else ("WARN" if nn > .5 else "FAIL"),
           f"{nn:.1%} non-null of {len(frame)} {grain} rows")

    # ------------------------------------------- C. season / half-season line
    lz["half"] = np.where(lz.game_year == 2025, "2025 (full)",
                   np.where(lz.game_date <= ASB_LAST_H1, "2026 H1 (uc-pps-017)", "2026 H2 (new)"))
    rows = []
    for lab, d in [("2025 (full)", lz25), ("2026 (full)", lz26),
                   ("2026 H1 (uc-pps-017)", lz26[lz26.game_date <= ASB_LAST_H1]),
                   ("2026 H2 (new)", lz26[lz26.game_date > ASB_LAST_H1])]:
        if not len(d): continue
        nres = nresults(["game_year"], d)
        agg = nres.iloc[0] if len(nres) == 1 else nresults(["pitcher"], d).iloc[0]
        outs, runs = outs_and_runs(d)
        yr = int(d.game_year.iloc[0])
        hh = hard_hit_rate(["pitcher"], d).iloc[0]
        ch = chase_rate(["pitcher"], d).iloc[0]
        wf = whiff_rate(["pitcher"], d).iloc[0]
        cw = csw_rate(["pitcher"], d).iloc[0]
        fp = fpsr(["pitcher"], d).iloc[0]
        pw = putaway_rate(["pitcher"], d).iloc[0]
        xw = pd.to_numeric(d[XW], errors="coerce")
        rows.append(dict(window=lab, starts=int(d.game_pk.nunique()),
            ip=ip_str(outs), outs=outs, pitches=int(len(d)),
            pa=int(agg.plate_apps), k_rate=float(agg.krate), bb_rate=float(agg.bbrate),
            hr=int(agg.hrs), hr_rate=float(agg.hr_rate),
            woba=float(agg.woba), xwoba=round(float(xw.mean()), 3), xwoba_n=int(xw.notna().sum()),
            hard_hit_rate=float(hh.hard_hit_rate), hard_hit_rate_tracked=float(hh.hard_hit_rate_tracked),
            chase_rate=float(ch.chase_rate), in_zone_rate=float(ch.in_zone_rate),
            whiff_rate=float(wf.whiff_rate), csw_rate=float(cw.csw_rate),
            first_pitch_strike_rate=float(fp.first_pitch_strike_rate),
            putaway_rate=float(pw.putaway_rate),
            runs_on_mound=runs, ra9=round(runs/(outs/3)*9, 2) if outs else np.nan,
            fip=round(fip(d, wc.loc[yr, "cFIP"]), 2)))
    season_line = pd.DataFrame(rows)
    season_line.to_csv(OUT("season_line.csv"), index=False)
    print("\n=== SEASON / HALF LINE ===\n", season_line.to_string(index=False))

    # ------------------------------------------------------ D. per-start log
    starts_idx = identify_starts(s26)
    lz_starts = set(starts_idx[starts_idx.starter == LUZARDO].game_pk)
    sf26 = start_frame(lz26, lz_starts)
    sf26["era_premise"] = np.where(sf26.game_date >= PREMISE_BREAK, "since 5/01", "before 5/01")
    sf26["half"] = np.where(sf26.game_date <= ASB_LAST_H1, "H1", "H2")
    sf26.to_csv(OUT("start_log_2026.csv"), index=False)
    print("\n=== 2026 START LOG ===\n", sf26[["game_date","opp","home","pitches","ip","pa",
          "k","bb","hr","runs","woba","xwoba","days_rest","half"]].to_string(index=False))
    dq("START-LOG: every appearance is a start", "lz 2026",
       "PASS" if bool(sf26.is_start.all()) else "WARN",
       f"{int(sf26.is_start.sum())}/{len(sf26)} appearances were games he started")

    # ------------------------------- E. ADVERSARIAL PREMISE TEST (CN-1..CN-6)
    # Cohort = every Phillies pitcher with >= MIN_GS_COHORT starts in the window.
    # Precompute ONCE for the whole 2026 season, then window by filtering.
    all_starts_26 = identify_starts(s26)
    gs_all = all_starts_26.groupby("starter").game_pk.nunique()
    _pool = gs_all[gs_all >= MIN_GS_COHORT].index.tolist()
    _SF, _NAME, _D = {}, {}, {}
    for pid in _pool:
        own = set(all_starts_26[all_starts_26.starter == pid].game_pk)
        d = s26[(s26.pitcher == pid) & (s26.game_pk.isin(own))]
        _D[pid] = d
        _SF[pid] = start_frame(d, own)
        _NAME[pid] = (d.player_name.dropna().mode().iat[0]
                      if d.player_name.notna().any() else f"id:{pid}")
    print(f"cohort pool: {len(_pool)} pitchers with >={MIN_GS_COHORT} GS in 2026")

    def cohort_axes(break_date):
        rows = []
        for pid in _pool:
            sfp = _SF[pid]
            sfp = sfp[sfp.game_date >= break_date]
            if len(sfp) < MIN_GS_COHORT: continue
            sfp = sfp.copy(); sfp["days_rest"] = pd.to_datetime(sfp.game_date).diff().dt.days
            ax = consistency_axes(sfp, pid)
            if ax is None: continue
            dstart = _D[pid][_D[pid].game_date >= break_date]
            xw = pd.to_numeric(dstart[XW], errors="coerce")
            ax["agg_xwoba"] = round(float(xw.mean()), 4)
            ax["woba"] = float(nresults(["pitcher"], dstart).woba.iat[0])
            ax["name"] = _NAME[pid]
            rows.append(ax)
        return rows

    axes_rows = cohort_axes(PREMISE_BREAK)
    cohort_df = pd.DataFrame(axes_rows)
    cohort_df.insert(0, "window_start", PREMISE_BREAK)
    cohort_df = cohort_df.sort_values("cn1_xwoba_sd")
    cohort_df.to_csv(OUT("consistency_cohort.csv"), index=False)
    print("\n=== CONSISTENCY COHORT (since %s, >=%d GS) ===" % (PREMISE_BREAK, MIN_GS_COHORT))
    print(cohort_df[["name","starts","ip","agg_xwoba","woba","ra9","cn1_xwoba_sd",
                     "cn2_floor_rate","cn3_blowup_rate","cn4_roll3_range",
                     "cn5_pitch_sd","cn6_ip_per_start","cn6_outs_sd"]].to_string(index=False))

    LOWER = {"cn1_xwoba_sd": True, "cn1_xwoba_iqr": True, "cn2_floor_rate": False,
             "cn3_blowup_rate": True, "cn4_roll3_range": True, "cn5_pitch_sd": True,
             "cn6_outs_sd": True, "cn6_ip_per_start": False,
             "agg_xwoba": True, "woba": True, "ra9": True, "mean_start_xwoba": True}
    ranks = rank_cohort(axes_rows, LOWER)
    nmap = dict(zip(cohort_df.who, cohort_df.name))
    ranks["name"] = ranks.who.map(nmap)
    ranks["n_cohort"] = ranks.groupby("axis").who.transform("size")
    ranks.to_csv(OUT("consistency_ranking.csv"), index=False)
    lz_rank = ranks[ranks.who == LUZARDO].sort_values("axis")
    print("\n=== LUZARDO RANK BY AXIS (since %s) ===\n" % PREMISE_BREAK,
          lz_rank[["axis","value","rank","n_cohort","better"]].to_string(index=False))

    # --- TR-2 breakpoint sensitivity scan (guardrail G6) --------------------
    scan = []
    for bd in BREAK_SCAN:
        rws = cohort_axes(bd)
        if not rws: continue
        rk = rank_cohort(rws, LOWER)
        n = rk[rk.axis == "cn1_xwoba_sd"].shape[0]
        row = dict(window_start=bd, cohort_n=n)
        for ax_ in ["cn1_xwoba_sd","cn2_floor_rate","cn3_blowup_rate","cn4_roll3_range",
                    "cn6_outs_sd","agg_xwoba","woba","ra9"]:
            hit = rk[(rk.axis == ax_) & (rk.who == LUZARDO)]
            row[f"{ax_}__rank"] = int(hit["rank"].iat[0]) if len(hit) else np.nan
            row[f"{ax_}__value"] = round(float(hit["value"].iat[0]), 4) if len(hit) else np.nan
        lzr = [r for r in rws if r["who"] == LUZARDO]
        row["lz_starts"] = lzr[0]["starts"] if lzr else 0
        scan.append(row)
    scan_df = pd.DataFrame(scan)
    scan_df.to_csv(OUT("consistency_breakpoint_scan.csv"), index=False)
    print("\n=== TR-2 BREAKPOINT SCAN (Luzardo rank of cohort_n) ===\n",
          scan_df[["window_start","cohort_n","lz_starts","cn1_xwoba_sd__rank",
                   "cn2_floor_rate__rank","cn3_blowup_rate__rank","cn4_roll3_range__rank",
                   "agg_xwoba__rank","ra9__rank"]].to_string(index=False))

    # --- full-season (no window) control: does the premise need the window? -
    full_rows = cohort_axes("2026-01-01")
    full_df = pd.DataFrame(full_rows)
    full_df["name"] = full_df.who.map(nmap).fillna(full_df.who.astype(str))
    full_df.insert(0, "window_start", "2026-01-01 (full season control)")
    full_df.to_csv(OUT("consistency_full_season_control.csv"), index=False)
    full_ranks = rank_cohort(full_rows, LOWER)
    full_ranks["name"] = full_ranks.who.map(nmap)
    full_ranks.to_csv(OUT("consistency_ranking_full_season.csv"), index=False)
    print("\n=== FULL-SEASON CONTROL (Luzardo) ===\n",
          full_ranks[full_ranks.who == LUZARDO][["axis","value","rank"]].to_string(index=False))

    # ------------------------------------- F. uc-pps-017 tripwire closure H1/H2
    h1 = lz26[lz26.game_date <= ASB_LAST_H1]
    h2 = lz26[lz26.game_date >  ASB_LAST_H1]

    # arsenal
    ars = []
    for lab, d in [("2025", lz25), ("2026 H1", h1), ("2026 H2", h2)]:
        tot = len(d)
        g = d.groupby("pitch_name")
        base = g.agg(pitches=("pitch_name","size"), velo=("release_speed","mean"),
                     pfx_x=("pfx_x","mean"), pfx_z=("pfx_z","mean"),
                     spin=("release_spin_rate","mean"), ext=("release_extension","mean")).reset_index()
        base["usage"] = base.pitches/tot
        wf = whiff_rate(["pitch_name"], d); pw = putaway_rate(["pitch_name"], d)
        ch = chase_rate(["pitch_name"], d)
        xw = d.groupby("pitch_name")[XW].mean().rename("xwoba").reset_index()
        m = (base.merge(wf[["pitch_name","swings","whiffs","whiff_rate"]], on="pitch_name", how="left")
                  .merge(pw[["pitch_name","putaway_rate"]], on="pitch_name", how="left")
                  .merge(ch[["pitch_name","chase_rate","in_zone_rate"]], on="pitch_name", how="left")
                  .merge(xw, on="pitch_name", how="left"))
        m.insert(0, "window", lab)
        ars.append(m)
    arsenal = pd.concat(ars, ignore_index=True).sort_values(["window","usage"], ascending=[True, False])
    arsenal = arsenal.round(3)
    arsenal.to_csv(OUT("arsenal_h1_h2.csv"), index=False)
    print("\n=== ARSENAL 2025 / H1 / H2 ===\n", arsenal[["window","pitch_name","pitches","usage",
          "velo","whiff_rate","chase_rate","putaway_rate","xwoba"]].to_string(index=False))

    # process KPI panel (the uc-pps-017 §4 table, extended)
    proc = []
    for lab, d in [("2025", lz25), ("2026 H1", h1), ("2026 H2", h2), ("2026 full", lz26)]:
        ch = chase_rate(["pitcher"], d).iloc[0]; wf = whiff_rate(["pitcher"], d).iloc[0]
        cw = csw_rate(["pitcher"], d).iloc[0];   fp = fpsr(["pitcher"], d).iloc[0]
        pw = putaway_rate(["pitcher"], d).iloc[0]; hh = hard_hit_rate(["pitcher"], d).iloc[0]
        nr = nresults(["pitcher"], d).iloc[0]
        xw = pd.to_numeric(d[XW], errors="coerce")
        proc.append(dict(window=lab, pitches=len(d), pa=int(nr.plate_apps),
            first_pitch_strike_rate=float(fp.first_pitch_strike_rate),
            in_zone_rate=float(ch.in_zone_rate), chase_rate=float(ch.chase_rate),
            whiff_rate=float(wf.whiff_rate), csw_rate=float(cw.csw_rate),
            putaway_rate=float(pw.putaway_rate), hard_hit_rate=float(hh.hard_hit_rate),
            k_rate=float(nr.krate), bb_rate=float(nr.bbrate),
            woba=float(nr.woba), xwoba=round(float(xw.mean()), 3)))
    process = pd.DataFrame(proc)
    process.to_csv(OUT("process_kpis_h1_h2.csv"), index=False)
    print("\n=== PROCESS KPIs ===\n", process.to_string(index=False))

    # TTO
    tto = []
    for lab, d in [("2025", lz25), ("2026 H1", h1), ("2026 H2", h2)]:
        d = d.copy(); d["tto"] = d.n_thruorder_pitcher.clip(upper=3)
        nr = nresults(["tto"], d)
        xw = d.groupby("tto")[XW].mean().rename("xwoba").reset_index()
        m = nr.merge(xw, on="tto", how="left", suffixes=("","_y"))
        if "xwoba_y" in m.columns: m["xwoba"] = m["xwoba_y"]; m = m.drop(columns=["xwoba_y"])
        m.insert(0, "window", lab); tto.append(m)
    tto_df = pd.concat(tto, ignore_index=True).round(3)
    tto_df.to_csv(OUT("tto_h1_h2.csv"), index=False)
    print("\n=== TIMES THROUGH ORDER ===\n", tto_df[["window","tto","plate_apps","woba","xwoba","hrs","krate"]].to_string(index=False))

    # by stand
    stand = []
    for lab, d in [("2025", lz25), ("2026 H1", h1), ("2026 H2", h2)]:
        nr = nresults(["stand"], d)
        xw = d.groupby("stand")[XW].mean().rename("xwoba2").reset_index()
        ch = chase_rate(["stand"], d)[["stand","chase_rate","in_zone_rate"]]
        wf = whiff_rate(["stand"], d)[["stand","whiff_rate"]]
        m = nr.merge(xw, on="stand").merge(ch, on="stand").merge(wf, on="stand")
        m["xwoba"] = m.xwoba2; m = m.drop(columns=["xwoba2"])
        m.insert(0, "window", lab); stand.append(m)
    stand_df = pd.concat(stand, ignore_index=True).round(3)
    stand_df.to_csv(OUT("by_stand_h1_h2.csv"), index=False)
    print("\n=== BY STAND ===\n", stand_df[["window","stand","plate_apps","woba","xwoba","krate","bbrate","chase_rate","whiff_rate"]].to_string(index=False))

    # monthly
    lz26m = lz26.copy(); lz26m["month"] = lz26m.game_date.str[:7]
    mo = nresults(["month"], lz26m)
    mo = mo.merge(lz26m.groupby("month")[XW].mean().rename("xwoba2").reset_index(), on="month")
    mo["xwoba"] = mo.xwoba2; mo = mo.drop(columns=["xwoba2"])
    mo = mo.merge(csw_rate(["month"], lz26m)[["month","csw_rate"]], on="month")
    mo = mo.merge(chase_rate(["month"], lz26m)[["month","chase_rate","in_zone_rate"]], on="month")
    mo = mo.merge(lz26m.groupby("month").agg(starts=("game_pk","nunique")).reset_index(), on="month")
    mo.round(3).to_csv(OUT("monthly_2026.csv"), index=False)
    print("\n=== MONTHLY 2026 ===\n", mo[["month","starts","plate_apps","woba","xwoba","krate","csw_rate","chase_rate"]].round(3).to_string(index=False))

    # battery (catcher) split — catcher id is fielder_2
    def resolve_names(ids, roles=("batting",)):
        names = {}
        for yr in (2026, 2025, 2024):
            f = os.path.join(PHIL_DIR, f"phils_{yr}.parquet")
            if not os.path.isfile(f): continue
            d = pd.read_parquet(f, columns=["batter","player_name","phillies_role"])
            d = d[d.phillies_role.isin(roles)]
            for i in ids:
                if i in names: continue
                s = d[d.batter == i].player_name
                if len(s): names[i] = s.mode().iat[0]
            if all(i in names for i in ids): break
        return {i: names.get(i, f"id:{i}") for i in ids}

    if "fielder_2" in lz26.columns:
        b = lz26.copy(); b["catcher"] = pd.to_numeric(b.fielder_2, errors="coerce")
        cids = [int(x) for x in b.catcher.dropna().unique()]
        cnames = resolve_names(cids, roles=("batting",))
        bat = []
        for lab, d in [("2026 H1", b[b.game_date <= ASB_LAST_H1]), ("2026 H2", b[b.game_date > ASB_LAST_H1]),
                       ("2026 full", b)]:
            nr = nresults(["catcher"], d)
            xw = d.groupby("catcher")[XW].mean().rename("xwoba2").reset_index()
            ch = chase_rate(["catcher"], d)[["catcher","chase_rate","in_zone_rate"]]
            pw = putaway_rate(["catcher"], d)[["catcher","putaway_rate"]]
            m = nr.merge(xw, on="catcher").merge(ch, on="catcher").merge(pw, on="catcher")
            m["xwoba"] = m.xwoba2; m = m.drop(columns=["xwoba2"])
            m.insert(0, "window", lab); bat.append(m)
        battery = pd.concat(bat, ignore_index=True)
        battery["catcher_name"] = battery.catcher.astype(int).map(cnames)
        battery.round(3).to_csv(OUT("battery_2026.csv"), index=False)
        print("\n=== BATTERY 2026 ===\n", battery[["window","catcher_name","pitches","plate_apps","woba","xwoba","putaway_rate"]].round(3).to_string(index=False))

    # rest / workload panel
    wl = sf26[["game_date","opp","pitches","ip","outs","pa","runs","days_rest","half"]].copy()
    wl["cum_pitches"] = wl.pitches.cumsum()
    wl.to_csv(OUT("workload_rest_2026.csv"), index=False)

    # ---------------------------------------------- G. ARI opponent lens (AR-*)
    ari26 = lz26[lz26.opp == OPPONENT].copy()
    ari_hist = [("2026", ari26)]
    a25 = lz25[lz25.opp == OPPONENT]
    if len(a25): ari_hist.append(("2025", a25))
    career = load_luzardo_career()
    if career is not None:
        career["opp"] = np.where(career.home_team.eq(career.home_team), career.home_team, career.away_team)
        # pitcher's team varies pre-2025; opponent = the team he is NOT on.
        # inning_topbot: 'Top' -> home team is pitching
        career["pitch_team"] = np.where(career.inning_topbot.eq("Top"), career.home_team, career.away_team)
        career["opp"] = np.where(career.inning_topbot.eq("Top"), career.away_team, career.home_team)
        ac = career[career.opp.isin([OPPONENT, "ARI"])]
        if len(ac): ari_hist.append(("2019-2024 (pre-PHI)", ac))

    ari_rows = []
    for lab, d in ari_hist:
        if not len(d): continue
        nr = nresults(["opp"], d).iloc[0]
        xw = pd.to_numeric(d[XW], errors="coerce")
        outs, runs = outs_and_runs(d)
        ari_rows.append(dict(window=lab, games=int(d.game_pk.nunique()), pitches=len(d),
            pa=int(nr.plate_apps), ip=ip_str(outs), runs=runs,
            k_rate=float(nr.krate), bb_rate=float(nr.bbrate), hr=int(nr.hrs),
            woba=float(nr.woba), xwoba=round(float(xw.mean()), 3)))
    ari_line = pd.DataFrame(ari_rows)
    ari_line.to_csv(OUT("ari_history_line.csv"), index=False)
    print("\n=== ARI HISTORY ===\n", ari_line.to_string(index=False))

    # the 4/10 start replayed, pitch by pitch summary
    if len(ari26):
        mixa = ari26.groupby("pitch_name").agg(pitches=("pitch_name","size"),
            velo=("release_speed","mean")).reset_index()
        mixa["usage"] = mixa.pitches/len(ari26)
        mixa = mixa.merge(whiff_rate(["pitch_name"], ari26)[["pitch_name","swings","whiffs","whiff_rate"]],
                          on="pitch_name", how="left")
        mixa = mixa.merge(ari26.groupby("pitch_name")[XW].mean().rename("xwoba").reset_index(),
                          on="pitch_name", how="left")
        mixa.insert(0, "game_date", ari26.game_date.min())
        mixa.round(3).sort_values("usage", ascending=False).to_csv(OUT("ari_start_20260410_mix.csv"), index=False)
        print("\n=== 4/10 vs ARI — PITCH MIX ===\n", mixa.round(3).sort_values("usage", ascending=False).to_string(index=False))

    # per-batter H2H panel: every AZ batter Luzardo has faced, all sources
    h2h_src = [("2026", lz26[lz26.opp == OPPONENT]), ("2025", lz25[lz25.opp == OPPONENT])]
    if career is not None and len(ac): h2h_src.append(("2019-2024", ac))
    parts = []
    for lab, d in h2h_src:
        if not len(d): continue
        dd = d.copy(); dd["src"] = lab; parts.append(dd)
    if parts:
        h2h = pd.concat(parts, ignore_index=True)
        # batter names parsed from the log itself (UC11 rule: never hand-key ids)
        bl = pa_last(h2h)
        def modal_name(g):
            """D-2 FIX: Statcast `des` can be PREFIXED with replay-review prose
            ("Diamondbacks challenged (force play), call ... was upheld: ").
            Strip every leading review clause before parsing the batter name,
            else the modal name for that batter becomes the review text."""
            s = g.des.dropna().astype(str)
            if not len(s): return ""
            s = s.str.replace(r"^.*?(?:challenged|Review of|reviewed)[^:]*:\s*", "",
                              regex=True, case=False)
            first = s.str.split(r"\s+(singles|doubles|triples|homers|grounds|flies|lines|pops|"
                                r"strikes|walks|reaches|hit|out|called|is|steals|advances|"
                                r"struck|hits|remains|scores|intentionally)",
                                regex=True, n=1).str[0].str.strip()
            first = first[first.str.len().between(4, 34)]
            return first.mode().iat[0] if len(first) and len(first.mode()) else ""
        names = bl.groupby("batter").apply(modal_name, include_groups=False)
        nr = nresults(["batter"], h2h)
        xw = h2h.groupby("batter")[XW].mean().rename("xwoba2").reset_index()
        wf = whiff_rate(["batter"], h2h)[["batter","swings","whiffs","whiff_rate"]]
        panel = nr.merge(xw, on="batter", how="left").merge(wf, on="batter", how="left")
        panel["xwoba"] = panel.xwoba2; panel = panel.drop(columns=["xwoba2"])
        panel["batter_name"] = panel.batter.map(names)
        panel["stand"] = panel.batter.map(bl.groupby("batter").stand.agg(lambda s: s.mode().iat[0] if len(s.mode()) else ""))
        panel["last_faced"] = panel.batter.map(h2h.groupby("batter").game_date.max())
        panel["seasons"] = panel.batter.map(h2h.groupby("batter").src.agg(lambda s: "/".join(sorted(set(s)))))
        # D-3 FIX: a career H2H panel against a TEAM mixes eras -- Nick Ahmed and
        # Evan Longoria are Luzardo H2H rows against "Arizona" that have nothing
        # to do with tonight. Tag recency explicitly; the report only plans off
        # the current-era tier and says so.
        panel["tier"] = np.where(panel.last_faced >= "2025-01-01",
                                 "current-era (faced 2025-26)", "historical only (pre-2025)")
        panel = panel.sort_values(["tier","plate_apps"], ascending=[True, False])
        panel.round(3).to_csv(OUT("ari_h2h_batters.csv"), index=False)
        cur = panel[panel.tier.str.startswith("current")]
        dq("H2H-RECENCY: current-era tier isolated", "ARI batter panel", "PASS",
           f"{len(cur)}/{len(panel)} batters faced in 2025-26; the rest are historical only")
        dq("H2H-NAMES: all resolved from des (no hand-keyed ids)", "ARI batter panel",
           "PASS" if panel.batter_name.str.len().between(4, 34).all() else "WARN",
           f"{int((~panel.batter_name.str.len().between(4,34)).sum())} unresolved/anomalous names")
        print("\n=== ARI H2H BATTER PANEL ===\n", panel[["batter_name","stand","seasons","last_faced",
              "plate_apps","hits","hrs","walks","strikeouts","woba","xwoba","whiff_rate"]].head(25).round(3).to_string(index=False))

    # profile-driven attack plan inputs: by-stand x pitch, 2026 full season
    ap = []
    for st in ["L","R"]:
        d = lz26[lz26.stand == st]
        if not len(d): continue
        tot = len(d)
        g = d.groupby("pitch_name").agg(pitches=("pitch_name","size"), velo=("release_speed","mean")).reset_index()
        g["usage"] = g.pitches/tot
        g = (g.merge(whiff_rate(["pitch_name"], d)[["pitch_name","whiff_rate","swings"]], on="pitch_name", how="left")
               .merge(putaway_rate(["pitch_name"], d)[["pitch_name","putaway_rate"]], on="pitch_name", how="left")
               .merge(chase_rate(["pitch_name"], d)[["pitch_name","chase_rate","in_zone_rate"]], on="pitch_name", how="left")
               .merge(d.groupby("pitch_name")[XW].mean().rename("xwoba").reset_index(), on="pitch_name", how="left"))
        g.insert(0, "stand", st); ap.append(g)
        # two-strike usage
    plan = pd.concat(ap, ignore_index=True).round(3).sort_values(["stand","usage"], ascending=[True, False])
    plan.to_csv(OUT("attack_plan_by_stand.csv"), index=False)
    print("\n=== ATTACK PLAN INPUTS (2026, by stand) ===\n", plan.to_string(index=False))

    # two-strike arsenal by stand — the putaway menu
    ts = lz26[lz26.strikes == 2]
    ts_rows = []
    for st in ["L","R"]:
        d = ts[ts.stand == st]
        if not len(d): continue
        g = d.groupby("pitch_name").agg(pitches=("pitch_name","size")).reset_index()
        g["share_2k"] = g.pitches/len(d)
        g = g.merge(whiff_rate(["pitch_name"], d)[["pitch_name","whiff_rate"]], on="pitch_name", how="left")
        g.insert(0, "stand", st); ts_rows.append(g)
    two_strike = pd.concat(ts_rows, ignore_index=True).round(3).sort_values(["stand","share_2k"], ascending=[True, False])
    two_strike.to_csv(OUT("two_strike_menu_by_stand.csv"), index=False)
    print("\n=== TWO-STRIKE MENU ===\n", two_strike.to_string(index=False))

    # ------------------- H. uc-pps-017 REPRODUCTION + TRIPWIRE CLOSURE -------
    # Continuity check: does this build reproduce the H1 numbers uc-pps-017
    # published? If it does not, the extension is not an extension.
    UC17_PUBLISHED = {   # carry-in from dp_uc17_luzardo_first_half_report.md
        "starts": 19, "pa": 465, "woba": .295, "xwoba": .269, "hard_hit_rate": .305,
        "whiff_rate": .325, "csw_rate": .331, "first_pitch_strike_rate": .600,
        "in_zone_rate": .468, "chase_rate": .333, "putaway_rate": .241,
        "k_rate": .292, "bb_rate": .075, "hr": 9, "ip": "108.2", "ra9": 3.64, "fip": 2.84,
    }
    h1row = season_line[season_line.window == "2026 H1 (uc-pps-017)"].iloc[0]
    repro = []
    for k, v in UC17_PUBLISHED.items():
        got = h1row.get(k)
        if isinstance(v, str):
            ok = str(got) == v; delta = ""
        else:
            got = float(got); delta = round(got - float(v), 4)
            ok = abs(delta) <= (0.0015 if abs(v) < 2 else 0.02)
        repro.append(dict(metric=k, uc_pps_017_published=v, dp_uc39_recomputed=got,
                          delta=delta, match="PASS" if ok else "REVIEW"))
    repro_df = pd.DataFrame(repro)
    repro_df.to_csv(OUT("uc17_reproduction_check.csv"), index=False)
    nfail = int((repro_df.match == "REVIEW").sum())
    dq("CONTINUITY: reproduces uc-pps-017 published H1 line", "17 metrics",
       "PASS" if nfail == 0 else "WARN", f"{len(repro_df)-nfail}/{len(repro_df)} match within tolerance")
    print("\n=== uc-pps-017 REPRODUCTION CHECK ===\n", repro_df.to_string(index=False))

    def gv(df_, wsel, col):
        r = df_[df_.window == wsel]
        return float(r[col].iat[0]) if len(r) else np.nan

    trip = []
    def tw(tid, item, h1v, h2v, direction, verdict_good, note):
        mv = h2v - h1v
        trip.append(dict(tripwire=tid, watch_item=item, h1=round(h1v,3), h2=round(h2v,3),
                         delta=round(mv,3), desired_direction=direction,
                         status=verdict_good, note=note))
    p = process.set_index("window")
    fps1, fps2 = p.loc["2026 H1","first_pitch_strike_rate"], p.loc["2026 H2","first_pitch_strike_rate"]
    ch1, ch2   = p.loc["2026 H1","chase_rate"], p.loc["2026 H2","chase_rate"]
    iz1, iz2   = p.loc["2026 H1","in_zone_rate"], p.loc["2026 H2","in_zone_rate"]
    bb1, bb2   = p.loc["2026 H1","bb_rate"], p.loc["2026 H2","bb_rate"]
    hh1, hh2   = p.loc["2026 H1","hard_hit_rate"], p.loc["2026 H2","hard_hit_rate"]
    tw("T1", "first-pitch strike rate (uc-pps-017 early-warning gauge)", fps1, fps2, "up",
       "IMPROVED" if fps2 > fps1 else "DEGRADED", "gauge for whether the out-of-zone plan stays affordable")
    tw("T2", "chase rate (the identity the profile leans on)", ch1, ch2, "hold-or-up",
       "HELD" if ch2 >= ch1 - .01 else "SLIPPED", "if hitters stop chasing, zone rate must come back up")
    tw("T3", "walk rate (the price of the out-of-zone plan)", bb1, bb2, "down",
       "IMPROVED" if bb2 <= bb1 else "DEGRADED", "chase must be bought without walks")
    tw("T4", "in-zone rate", iz1, iz2, "context", "CONTEXT", "read with T1/T2")
    tw("T5", "hard-hit rate", hh1, hh2, "down", "IMPROVED" if hh2 <= hh1 else "DEGRADED", "contact-quality floor")
    t = tto_df.set_index(["window","tto"])
    for k in (1,2,3):
        try:
            a = float(t.loc[("2026 H1", k), "woba"]); bq = float(t.loc[("2026 H2", k), "woba"])
            # a zero delta is HELD, not DEGRADED — the earlier strict "<" test
            # labelled an unchanged .198 as a regression.
            tw(f"T6.{k}", f"TTO {k} wOBA (uc-pps-017 flagged the 2nd-time cliff)", a, bq, "down",
               "IMPROVED" if bq < a - .001 else ("HELD" if abs(bq - a) <= .001 else "DEGRADED"),
               f"H1 PA {int(t.loc[('2026 H1',k),'plate_apps'])} / H2 PA {int(t.loc[('2026 H2',k),'plate_apps'])}")
        except KeyError: pass
    sdx = stand_df.set_index(["window","stand"])
    for st in ("L","R"):
        try:
            tw(f"T7.{st}", f"vs {st}HB wOBA", float(sdx.loc[("2026 H1",st),"woba"]),
               float(sdx.loc[("2026 H2",st),"woba"]), "down",
               "IMPROVED" if float(sdx.loc[("2026 H2",st),"woba"]) < float(sdx.loc[("2026 H1",st),"woba"]) - .001 else "HELD",
               f"H1 PA {int(sdx.loc[('2026 H1',st),'plate_apps'])} / H2 PA {int(sdx.loc[('2026 H2',st),'plate_apps'])}")
        except KeyError: pass
    ai = arsenal.set_index(["window","pitch_name"])
    for pn in ["Sinker","Sweeper","4-Seam Fastball","Changeup"]:
        try:
            tw(f"T8.{pn}", f"{pn} usage share", float(ai.loc[("2026 H1",pn),"usage"]),
               float(ai.loc[("2026 H2",pn),"usage"]), "context", "CONTEXT",
               f"xwOBA {ai.loc[('2026 H1',pn),'xwoba']:.3f} -> {ai.loc[('2026 H2',pn),'xwoba']:.3f}; "
               f"whiff {ai.loc[('2026 H1',pn),'whiff_rate']:.3f} -> {ai.loc[('2026 H2',pn),'whiff_rate']:.3f}")
        except KeyError: pass
    trip_df = pd.DataFrame(trip)
    trip_df.to_csv(OUT("uc17_tripwire_closure.csv"), index=False)
    print("\n=== uc-pps-017 TRIPWIRE CLOSURE ===\n", trip_df.to_string(index=False))

    # ------------------------------------------------------------ I. figures
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        def brand(ax, title, sub=""):
            # pad the title clear of the plot frame; without it a chart whose
            # top gridline sits at the axis maximum (fig5, inverted rank axis)
            # renders the title straight through the data.
            ax.set_title(title, color=PHI_NAVY, fontsize=13, fontweight="bold",
                         loc="left", pad=26 if sub else 14)
            if sub: ax.text(0, 1.025, sub, transform=ax.transAxes, fontsize=8.5, color=PHI_GRAY)
            ax.spines[["top","right"]].set_visible(False)
            ax.grid(axis="y", color=PHI_LGRAY, lw=.7, alpha=.7); ax.set_axisbelow(True)

        # fig 1 — consistency ranking (CN-1 vs level)
        c = cohort_df.dropna(subset=["cn1_xwoba_sd"]).copy()
        fig, ax = plt.subplots(figsize=(8.6, 5.2))
        for _, r in c.iterrows():
            is_lz = r.who == LUZARDO
            ax.scatter(r.cn1_xwoba_sd, r.agg_xwoba, s=190 if is_lz else 110,
                       color=PHI_RED if is_lz else PHI_NAVY, zorder=3,
                       edgecolor="white", lw=1.4)
            ax.annotate(str(r["name"]).split(",")[0], (r.cn1_xwoba_sd, r.agg_xwoba),
                        textcoords="offset points", xytext=(8, 4), fontsize=9,
                        color=PHI_RED if is_lz else "#333", fontweight="bold" if is_lz else "normal")
        ax.axvline(c.cn1_xwoba_sd.median(), color=PHI_GRAY, ls="--", lw=.9)
        ax.axhline(c.agg_xwoba.median(), color=PHI_GRAY, ls="--", lw=.9)
        ax.set_xlabel("CN-1 · SD of start xwOBA  (left = steadier)")
        ax.set_ylabel("Aggregate xwOBA against  (down = better)")
        brand(ax, "Consistency is a different axis from quality",
              f"Phillies starters, {PREMISE_BREAK} onward, min {MIN_GS_COHORT} GS · dashed lines = cohort medians")
        fig.tight_layout(); fig.savefig(OUT("fig1_consistency_map.png"), dpi=160); plt.close(fig)

        # fig 2 — start trend with breakpoint
        fig, ax = plt.subplots(figsize=(10.2, 4.6))
        x = np.arange(len(sf26))
        ax.bar(x, sf26.runs, color=PHI_LGRAY, width=.62, label="runs allowed (on mound)", zorder=2)
        ax2 = ax.twinx()
        ax2.plot(x, sf26.xwoba, color=PHI_RED, marker="o", lw=2, ms=5, label="start xwOBA", zorder=4)
        ax2.axhline(float(sf26.xwoba.mean()), color=PHI_NAVY, ls=":", lw=1.2)
        bi = int((sf26.game_date < PREMISE_BREAK).sum())
        ax.axvline(bi - .5, color=PHI_NAVY, lw=1.6)
        ax.text(bi - .4, ax.get_ylim()[1]*.94, f" premise breakpoint {PREMISE_BREAK}",
                fontsize=8.5, color=PHI_NAVY)
        ax.set_xticks(x); ax.set_xticklabels([f"{d[5:]}\n{o}" for d, o in zip(sf26.game_date, sf26.opp)], fontsize=7)
        ax.set_ylabel("runs allowed"); ax2.set_ylabel("start xwOBA", color=PHI_RED)
        brand(ax, "Every 2026 start: results (bars) against contact quality (line)",
              "runs = score deltas while on the mound (RA9 basis, not earned runs)")
        fig.tight_layout(); fig.savefig(OUT("fig2_start_trend.png"), dpi=160); plt.close(fig)

        # fig 3 — arsenal H1 -> H2
        aw = arsenal[arsenal.window.isin(["2026 H1","2026 H2"])]
        pns = (aw[aw.window=="2026 H1"].sort_values("usage", ascending=False).pitch_name.tolist())
        fig, ax = plt.subplots(figsize=(8.6, 4.6))
        w = .38
        for i, wlab in enumerate(["2026 H1","2026 H2"]):
            vals = [float(aw[(aw.window==wlab)&(aw.pitch_name==pn)].usage.iat[0])
                    if len(aw[(aw.window==wlab)&(aw.pitch_name==pn)]) else 0 for pn in pns]
            ax.bar(np.arange(len(pns)) + (i-0.5)*w, vals, width=w,
                   color=PHI_NAVY if i == 0 else PHI_RED, label=wlab, zorder=3)
        ax.set_xticks(np.arange(len(pns))); ax.set_xticklabels(pns, fontsize=9)
        ax.set_ylabel("usage share"); ax.legend(frameon=False, fontsize=9)
        brand(ax, "Arsenal drift across the All-Star break", "share of all pitches thrown")
        fig.tight_layout(); fig.savefig(OUT("fig3_arsenal_drift.png"), dpi=160); plt.close(fig)

        # fig 4 — TTO
        fig, ax = plt.subplots(figsize=(8.0, 4.4))
        for i, wlab in enumerate(["2025","2026 H1","2026 H2"]):
            sub = tto_df[tto_df.window == wlab].sort_values("tto")
            ax.plot(sub.tto, sub.woba, marker="o", lw=2,
                    color=[PHI_GRAY, PHI_NAVY, PHI_RED][i], label=wlab)
            for _, r in sub.iterrows():
                ax.annotate(f"{r.woba:.3f}\n({int(r.plate_apps)} PA)", (r.tto, r.woba),
                            textcoords="offset points", xytext=(0, 9), ha="center", fontsize=7.5,
                            color=[PHI_GRAY, PHI_NAVY, PHI_RED][i])
        ax.set_xticks([1,2,3]); ax.set_xticklabels(["1st time","2nd time","3rd+ time"])
        ax.set_ylabel("wOBA against"); ax.legend(frameon=False, fontsize=9)
        brand(ax, "Times through the order — did the 2nd-time cliff survive the break?",
              "uc-pps-017 flagged 2nd TTO .368 as the leash item")
        fig.tight_layout(); fig.savefig(OUT("fig4_tto.png"), dpi=160); plt.close(fig)

        # fig 5 — breakpoint scan
        fig, ax = plt.subplots(figsize=(8.6, 4.2))
        for col, lab, cl in [("cn1_xwoba_sd__rank","CN-1 steadiness", PHI_RED),
                             ("cn2_floor_rate__rank","CN-2 floor rate", PHI_NAVY),
                             ("cn3_blowup_rate__rank","CN-3 blow-up rate", "#9467BD"),
                             ("agg_xwoba__rank","xwOBA (level)", PHI_GRAY)]:
            ax.plot(scan_df.window_start, scan_df[col], marker="o", lw=1.9, label=lab, color=cl)
        ax.invert_yaxis(); ax.set_ylabel("Luzardo's rank in cohort (1 = best)")
        ax.set_yticks(range(1, int(np.nanmax(scan_df[[c for c in scan_df.columns if c.endswith('__rank')]].values))+1))
        ax.axvline(PREMISE_BREAK, color=PHI_NAVY, ls="--", lw=1.1)
        ax.legend(frameon=False, fontsize=8.5, ncols=2)
        plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=8)
        brand(ax, "TR-2 breakpoint scan — is the ranking a finding or a boundary artefact?",
              "dashed line = the DPO's stated 'end of April' boundary")
        fig.tight_layout(); fig.savefig(OUT("fig5_breakpoint_scan.png"), dpi=160); plt.close(fig)
        dq("FIGURES: rendered", "5 figures", "PASS", "fig1..fig5 written to out/")
    except Exception as e:
        dq("FIGURES: rendered", "matplotlib", "WARN", f"{type(e).__name__}: {e}")

    # --------------------------------------------------------- J. manifests
    pd.DataFrame(DQ_ROWS).to_csv(OUT("dq_scorecard.csv"), index=False)
    pd.DataFrame(FRESH_ROWS).to_csv(OUT("freshness_manifest.csv"), index=False)
    nfail_dq = sum(1 for r in DQ_ROWS if r["result"] == "FAIL")
    print(f"\nDQ: {len(DQ_ROWS)} rules · {nfail_dq} FAIL · "
          f"{sum(1 for r in DQ_ROWS if r['result']=='WARN')} WARN")

    # JSON payload for the dashboard (single source of truth, no hand-typed numbers)
    payload = dict(
        meta=dict(uc="uc-pps-028", build="dp_uc39", subject="Jesús Luzardo", pitcher_id=LUZARDO,
                  game_date=GAME_DATE, opponent=OPPONENT, premise_break=PREMISE_BREAK,
                  cache_max=cache_max, last_start=lz26.game_date.max(),
                  built=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")),
        season_line=season_line.to_dict("records"),
        start_log=sf26.replace({np.nan: None}).to_dict("records"),
        cohort=cohort_df.replace({np.nan: None}).to_dict("records"),
        ranking=ranks.replace({np.nan: None}).to_dict("records"),
        scan=scan_df.replace({np.nan: None}).to_dict("records"),
        arsenal=arsenal.replace({np.nan: None}).to_dict("records"),
        process=process.replace({np.nan: None}).to_dict("records"),
        tto=tto_df.replace({np.nan: None}).to_dict("records"),
        stand=stand_df.replace({np.nan: None}).to_dict("records"),
        monthly=mo.round(3).replace({np.nan: None}).to_dict("records"),
        tripwires=trip_df.replace({np.nan: None}).to_dict("records"),
        repro=repro_df.replace({np.nan: None}).to_dict("records"),
        ari_line=ari_line.replace({np.nan: None}).to_dict("records"),
        plan=plan.replace({np.nan: None}).to_dict("records"),
        two_strike=two_strike.replace({np.nan: None}).to_dict("records"),
        dq=DQ_ROWS, freshness=FRESH_ROWS,
    )
    try:
        payload["h2h"] = panel.replace({np.nan: None}).to_dict("records")
    except NameError:
        payload["h2h"] = []
    try:
        payload["battery"] = battery.round(3).replace({np.nan: None}).to_dict("records")
    except NameError:
        payload["battery"] = []
    with open(OUT("payload.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, default=str)
    print(f"\nWrote {len([n for n in os.listdir(OUT_DIR)])} receipt files to {OUT_DIR}")

if __name__ == "__main__":
    main()
