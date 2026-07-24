"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #26  (uc-pps-021)
"Advance Scout: Aaron Nola (RHP) vs the Los Angeles Dodgers — home start,
 Citizens Bank Park, 2026-07-22. Extends the Nola advance-scout line
 (UC#8 vs WAS -> UC#15 vs KC) with three fresh starts (7/05, 7/10, 7/16)
 and a focused matchup vs seven named Dodgers hitters."
============================================================================

Layer-3 BUILD artifact for the Phillies Pitching (pps) value stream.

Pattern lineage:
  UC#8  (dp_uc8_nola_vs_nationals)  — canonical flat-file pattern; origin of
        the NEW KPIs edge_rate / ooz_called_strike_rate / air_gb_rate.
  UC#11 (dp_uc11_rangel_vs_pirates) — current best exemplar (multi-level,
        des-parse H2H id resolution).
  UC#15 (dp_uc15_nola_vs_royals)    — direct predecessor; the slider profile
        and the self-contained locked-KPI kernel are inherited from here.
  UC#24 (dp_uc24_turner)            — the current convention for an
        independent verification ledger (see dp_uc25_verification.py).

WHAT IS NEW IN UC#26 (requested by the DPO / business user):
  * KEEP IT CURRENT: season line rolled forward to 2026-07-16 (20 GS, was 17
    at UC#15). Adds a RECENCY lens — the three starts since the last report
    (7/05, 7/10, 7/16) as game lines and a last-3-vs-season split.
  * APPROACH SHIFTS: monthly pitch-usage and velo tracks; slider maturation
    arc extended through 7/16.
  * UNDERLYING INDICATORS: the previously-identified leaks (the LHB walk
    problem, the contact-quality / air-ball engine, the two-strike finish,
    and the "is it ABS?" question) are re-tested with fresh data using the
    UC#8 process KPIs inherited VERBATIM.
  * MATCHUP: career head-to-head vs SEVEN named Dodgers hitters only
    (DPO scope decision — not a posted 1-9 card): Ohtani, Freeman, Muncy,
    Betts, Tucker, Pages, Edman. Five stand LEFT vs a RHP.

GOVERNANCE: no NEW rate KPIs defined this UC. Every rate is inherited
verbatim from the locked UC8->UC11->UC15 line (get_stats/nresults, whiff,
chase, putaway, fpsr, hard_hit) plus the UC8 glossary-approved trio
(edge_rate, ooz_called_strike_rate, air_gb_rate). See
dp_uc25_nola_vs_dodgers_use_case_spec.md §4.

DATA WINDOW / FRESHNESS:
  * Game day = 2026-07-22 (home, Citizens Bank Park). PRE-GAME projection.
  * MLB pitch log: data/phillies/phils_2015..2026.parquet,
    phillies_role=='pitching', pitcher==605400 (NOT Nolan Hoffman 676510),
    game_type=='R'. Cache fresh through Nola's last start, 2026-07-16.
  * Dodgers H2H: reconstructed from Nola's OWN career log; batter ids
    resolved by name-parsing `des` (modal name per batter id) — never
    hand-keyed. Seven-hitter scope is a manual carry-in from the DPO.

OUTPUTS (NEW files, none overwritten), written to ./out/:
  dp_uc25_nola_season_trend.csv        nresults by season, career 2015-2026
  dp_uc25_nola_by_stand_2026.csv       2026 nresults by batter stand
  dp_uc25_nola_arsenal_2026.csv        2026 arsenal by stand (usage/velo/mvt/whiff)
  dp_uc25_recency_game_lines.csv       every 2026 start, game line (ip_computed)
  dp_uc25_recency_split.csv            last-3 starts vs prior-2026 combined
  dp_uc25_monthly_usage.csv            pitch usage by month, 2026 (approach shift)
  dp_uc25_monthly_velo.csv             velo by month for the arsenal, 2026
  dp_uc25_slider_arc.csv               slider usage arc by start since debut
  dp_uc25_process_abs_by_year.csv      fpsr/chase/in-zone/putaway/edge/ooz-CSR/chase-up
  dp_uc25_contact_quality_by_year.csv  air/gb/hard-hit/hr per year (the engine)
  dp_uc25_process_by_stand_2026.csv    LHB vs RHB process KPIs, 2026
  dp_uc25_dodgers_h2h.csv              career H2H vs the 7 named hitters
  dp_uc25_dq_scorecard.csv             data-quality-engineer scorecard
  dp_uc25_freshness_manifest.csv       source/window/fitness receipts
  dp_uc25_nola_arsenal_map.png         fig 1 — arsenal locations by stand
  dp_uc25_usage_whiff_2026.png         fig 2 — usage x whiff by pitch
  dp_uc25_recency_approach.png         fig 3 — per-start results + usage tracks
  dp_uc25_process_abs_panel.png        fig 4 — ABS revisit + LHB/RHB process
  dp_uc25_contact_quality.png          fig 5 — air/hard-hit/hr by year
  dp_uc25_dodgers_h2h_matrix.png       fig 6 — career wOBA vs Nola, 7 hitters
============================================================================
"""
from __future__ import annotations
import os, glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out"); os.makedirs(OUT_DIR, exist_ok=True)

NOLA = 605400                 # Aaron Nola, MLBAM pitcher id (NOT Nolan Hoffman 676510)
GAME_DAY = "2026-07-22"
CURRENT_YEAR = 2026
SLIDER_DEBUT = "2026-06-13"
LAST_REPORT_THROUGH = "2026-07-04"   # dp_uc15 cache boundary; starts after = new material

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "phillies"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies",
]
PHIL_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
_WOBA_CANDIDATES = [
    os.path.join(HERE, "wOBA and FIP Constants.csv"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv",
]
WOBA_CSV = next((p for p in _WOBA_CANDIDATES if os.path.isfile(p)), None)

# --- constants inherited verbatim from dp_uc8 / dp_uc15 ---------------------
PLATE_HALF = 0.83            # zone x in [-0.83, 0.83] (ft)
BALL_FT = 2.94 / 12.0        # one baseball width (~0.245 ft) — the edge shadow band
SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]
TAKES = ["called_strike", "ball", "blocked_ball", "ball_blocked"]

PHI_RED, PHI_NAVY, PHI_GRAY, PHI_LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
PITCH_COLORS = {"Knuckle Curve": "#2CA02C", "4-Seam Fastball": "#E81828",
                "Sinker": "#FF7F0E", "Changeup": "#9467BD",
                "Cutter": "#8C564B", "Slider": "#1F77B4"}

# ---------------------------------------------------------------------------
# SEVEN NAMED DODGERS HITTERS (DPO scope decision — not a posted lineup card).
# `bats` is the fallback label; the actual stand vs Nola is confirmed from
# his own log. Switch-hitter Edman stands LEFT vs a RHP.
# H2H matching is by parsed batter NAME from Nola's own log (no hand-keyed ids).
# ---------------------------------------------------------------------------
HITTERS = [
    dict(name="Mookie Betts",    bats="R"),
    dict(name="Shohei Ohtani",   bats="L"),
    dict(name="Freddie Freeman", bats="L"),
    dict(name="Max Muncy",       bats="L"),
    dict(name="Kyle Tucker",     bats="L"),
    dict(name="Andy Pages",      bats="R"),
    dict(name="Tommy Edman",     bats="S"),
]
def stand_vs_rhp(bats): return "L" if bats in ("S", "L") else "R"

EVENT_OUTS = {"field_out": 1, "strikeout": 1, "force_out": 1, "sac_fly": 1,
              "sac_bunt": 1, "fielders_choice_out": 1, "caught_stealing_2b": 0,
              "grounded_into_double_play": 2, "double_play": 2,
              "strikeout_double_play": 2, "sac_fly_double_play": 2,
              "triple_play": 3, "other_out": 1}

# ===========================================================================
# LOADERS
# ===========================================================================
def _coerce(df):
    for c in ["plate_x","plate_z","sz_top","sz_bot","pfx_x","pfx_z","release_speed",
              "release_spin_rate","launch_speed","launch_angle","strikes","balls",
              "pitch_number","woba_value","woba_denom","zone"]:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def load_nola_career():
    if PHIL_DIR is None:
        raise FileNotFoundError("Could not locate data/phillies. Set MLB_DATA_ROOT.")
    frames = []
    for f in sorted(glob.glob(os.path.join(PHIL_DIR, "phils_*.parquet"))):
        d = pd.read_parquet(f)
        d = d[(d.phillies_role == "pitching") & (d.pitcher == NOLA) & (d.game_type == "R")]
        if len(d): frames.append(d)
    r = pd.concat(frames, ignore_index=True).drop_duplicates(
        ["game_pk", "at_bat_number", "pitch_number"])
    r = _coerce(r)
    r["game_date"] = pd.to_datetime(r.game_date)
    if WOBA_CSV:
        w = pd.read_csv(WOBA_CSV)
        r = r.drop(columns=[c for c in w.columns if c != "Season" and c in r.columns])
        r = r.merge(w, left_on="game_year", right_on="Season", how="left")
    return r

# ===========================================================================
# LOCKED KPI FUNCTIONS — inherited VERBATIM from dp_uc15 (which inherited from
# dp_uc11 <- dp_uc8 <- Baseball Functions library; values identical).
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
                "ba","obp","slg","ops","woba","xwoba","krate","bbrate","hr_rate"]
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
# NEW-IN-UC8 KPI FUNCTIONS — inherited VERBATIM from dp_uc8 (glossary approved).
# ===========================================================================
def _dist_to_zone_edge(px, pz, sz_bot, sz_top):
    hw = PLATE_HALF
    dx_out = np.maximum.reduce([-hw - px, px - hw, np.zeros_like(px)])
    dz_out = np.maximum.reduce([sz_bot - pz, pz - sz_top, np.zeros_like(pz)])
    outside = (dx_out > 0) | (dz_out > 0)
    dist_out = np.sqrt(dx_out**2 + dz_out**2)
    dist_in = np.minimum.reduce([hw - np.abs(px), pz - sz_bot, sz_top - pz])
    return np.where(outside, dist_out, dist_in)

def edge_rate(level, df):
    if isinstance(level, str): level = [level]
    d = df.dropna(subset=["plate_x","plate_z","sz_top","sz_bot"]).copy()
    dist = _dist_to_zone_edge(d.plate_x.values, d.plate_z.values, d.sz_bot.values, d.sz_top.values)
    d["is_edge"] = dist <= BALL_FT
    tot = d.groupby(level, as_index=False).agg(located_pitches=("is_edge","size"))
    eg = d.groupby(level, as_index=False).agg(edge_pitches=("is_edge","sum"))
    out = tot.merge(eg, on=level, how="left").fillna(0)
    out["edge_rate"] = out.edge_pitches / out.located_pitches
    return out.round(3)

def ooz_called_strike_rate(level, df):
    if isinstance(level, str): level = [level]
    ooz = df[df.zone > 9]
    tot = ooz.groupby(level, as_index=False).agg(ooz_pitches=("des","size"))
    cs = ooz[ooz.description=="called_strike"].groupby(level, as_index=False).agg(ooz_called_strikes=("des","size"))
    takes = ooz[ooz.description.isin(TAKES)].groupby(level, as_index=False).agg(ooz_takes=("des","size"))
    out = tot.merge(cs, on=level, how="left").merge(takes, on=level, how="left").fillna(0)
    out["ooz_called_strike_rate"] = out.ooz_called_strikes / out.ooz_pitches
    out["ooz_csr_per_take"] = np.where(out.ooz_takes>0, out.ooz_called_strikes/out.ooz_takes, np.nan)
    return out.round(3)

def air_gb_rate(level, df):
    if isinstance(level, str): level = [level]
    bip = df[df.type=="X"].copy()
    tot = bip.groupby(level, as_index=False).agg(bip=("des","size"))
    def share(mask, name):
        return bip[mask].groupby(level, as_index=False).agg(**{name: ("des","size")})
    gb = share(bip.bb_type=="ground_ball","gb"); fb = share(bip.bb_type=="fly_ball","fb")
    ld = share(bip.bb_type=="line_drive","ld"); pu = share(bip.bb_type=="popup","pu")
    out = tot
    for x in [gb,fb,ld,pu]:
        out = out.merge(x, on=level, how="left")
    out = out.fillna(0)
    out["gb_rate"]=out.gb/out.bip; out["fb_rate"]=out.fb/out.bip
    out["ld_rate"]=out.ld/out.bip; out["pu_rate"]=out.pu/out.bip
    out["air_rate"]=(out.fb+out.ld+out.pu)/out.bip
    return out.round(3)

def chase_up_rate(level, df):
    """Swing rate on pitches ABOVE the rulebook top (plate_z > sz_top) — the
    'is he still generating chase up?' check from UC8. CDEs: plate_z, sz_top."""
    if isinstance(level, str): level = [level]
    d = df.dropna(subset=["plate_z","sz_top"]).copy()
    above = d[d.plate_z > d.sz_top]
    tot = above.groupby(level, as_index=False).agg(above_pitches=("des","size"))
    sw = above[above.description.isin(SWINGS)].groupby(level, as_index=False).agg(above_swings=("des","size"))
    out = tot.merge(sw, on=level, how="left").fillna(0)
    out["chase_up_rate"] = out.above_swings / out.above_pitches
    return out.round(3)

# ===========================================================================
# REPORTING HELPER — correct xwOBA-on-contact (NOT the locked pitch-level col)
# ===========================================================================
def xwobacon(level, df):
    """xwOBA on contact = mean estimated_woba_using_speedangle over BIP
    (type=='X'). This is the correct contact-quality read. The get_stats/
    nresults 'xwoba' column is a pitch-level mean contaminated by non-BIP rows
    (some strikeouts carry a 0.0) and must NOT be cited as xwOBAcon. Verified
    this session: the field is >99% populated on BIP for every season 2015-26.
    CDEs: estimated_woba_using_speedangle, type."""
    if isinstance(level, str): level = [level]
    b = df[df.type == "X"]
    if not len(b):
        return pd.DataFrame(columns=level+["xwobacon"])
    return b.groupby(level, as_index=False).agg(
        xwobacon=("estimated_woba_using_speedangle","mean")).round(3)

# ===========================================================================
# HELPERS — game lines
# ===========================================================================
def ip_from_events(df):
    outs = df.events.map(EVENT_OUTS).fillna(0).sum()
    whole, rem = divmod(int(outs), 3)
    return float(f"{whole}.{rem}")

def game_lines(career, game_pks):
    sub = career[career.game_pk.isin(game_pks)]
    lines = nresults(["game_pk"], sub)
    meta = (sub.groupby("game_pk")
            .agg(game_date=("game_date","first"), home=("home_team","first"),
                 away=("away_team","first")).reset_index())
    meta["opponent"] = np.where(meta.home=="PHI", meta.away, meta.home)
    meta["venue"] = np.where(meta.home=="PHI", "home (CBP)", "road @ " + meta.home)
    ips = {pk: ip_from_events(sub[sub.game_pk==pk]) for pk in game_pks}
    meta["ip_computed"] = meta.game_pk.map(ips)
    out = meta.merge(lines, on="game_pk").sort_values("game_date")
    out["game_date"] = out.game_date.dt.strftime("%Y-%m-%d")
    return out.drop(columns=["home","away"])

# ===========================================================================
# BUILD
# ===========================================================================
def main():
    career = load_nola_career()
    d26 = career[career.game_year==2026].copy()
    n_starts_26 = d26.game_pk.nunique()

    # --- 1. career season trend -------------------------------------------
    trend = nresults(["game_year"], career)
    gs = career.groupby("game_year").game_pk.nunique().rename("games").reset_index()
    trend = gs.merge(trend, on="game_year")
    trend = trend.merge(xwobacon(["game_year"], career), on="game_year", how="left").rename(
        columns={"xwoba":"xwoba_pitchlevel_do_not_cite"})
    trend.to_csv(os.path.join(OUT_DIR,"dp_uc25_nola_season_trend.csv"),index=False)

    # --- 2. 2026 by stand -------------------------------------------------
    stand = nresults(["stand"], d26)
    stand.to_csv(os.path.join(OUT_DIR,"dp_uc25_nola_by_stand_2026.csv"),index=False)

    # --- 3. arsenal by stand, 2026 ----------------------------------------
    ars = d26.groupby(["stand","pitch_name"],as_index=False).agg(
        n=("description","size"),velo=("release_speed","mean"),
        spin=("release_spin_rate","mean"),pfx_x=("pfx_x","mean"),pfx_z=("pfx_z","mean"),
        px=("plate_x","mean"),pz=("plate_z","mean"))
    tot = ars.groupby("stand",as_index=False).n.sum().rename(columns={"n":"n_stand"})
    ars = ars.merge(tot,on="stand"); ars["usage"]=ars.n/ars.n_stand
    w = whiff_rate(["stand","pitch_name"], d26)
    ars = ars.merge(w[["stand","pitch_name","swings","whiffs","whiff_rate"]],
                    on=["stand","pitch_name"],how="left").round(3)
    ars.to_csv(os.path.join(OUT_DIR,"dp_uc25_nola_arsenal_2026.csv"),index=False)

    # --- 4. RECENCY — every 2026 start + last-3 vs prior split -------------
    pk26 = list(d26.game_pk.unique())
    glines = game_lines(d26, pk26)
    glines.to_csv(os.path.join(OUT_DIR,"dp_uc25_recency_game_lines.csv"),index=False)

    d26 = d26.copy()
    new_mask = d26.game_date > pd.Timestamp(LAST_REPORT_THROUGH)
    last3 = d26[new_mask]; prior = d26[~new_mask]
    rows=[]
    for label, sub in [("last-3 starts (7/05,7/10,7/16)", last3),
                       ("prior 2026 (thru 7/04)", prior),
                       ("2026 full", d26)]:
        line = nresults(["game_year"], sub).drop(columns=["game_year","xwoba"])
        xwc = xwobacon(["game_year"], sub)
        line["xwobacon"] = float(xwc.xwobacon.iat[0]) if len(xwc) else np.nan
        line.insert(0,"segment",label)
        line.insert(1,"starts", sub.game_pk.nunique())
        rows.append(line)
    recency = pd.concat(rows, ignore_index=True)
    recency.to_csv(os.path.join(OUT_DIR,"dp_uc25_recency_split.csv"),index=False)

    # --- 5. APPROACH SHIFT — monthly usage & velo ------------------------
    d26["month"] = d26.game_date.dt.strftime("%Y-%m")
    mu = d26.groupby(["month","pitch_name"],as_index=False).agg(n=("description","size"))
    mtot = d26.groupby("month",as_index=False).agg(month_pitches=("description","size"))
    mu = mu.merge(mtot,on="month"); mu["usage"]=(mu.n/mu.month_pitches).round(3)
    mu_wide = mu.pivot(index="month",columns="pitch_name",values="usage").fillna(0).round(3).reset_index()
    mu_wide.to_csv(os.path.join(OUT_DIR,"dp_uc25_monthly_usage.csv"),index=False)
    mv = d26.groupby(["month","pitch_name"],as_index=False).agg(velo=("release_speed","mean")).round(1)
    mv_wide = mv.pivot(index="month",columns="pitch_name",values="velo").round(1).reset_index()
    mv_wide.to_csv(os.path.join(OUT_DIR,"dp_uc25_monthly_velo.csv"),index=False)

    # --- 6. slider arc since debut (extended thru 7/16) -------------------
    sl = d26[d26.pitch_name=="Slider"].copy()
    per_game = d26.groupby(d26.game_date.dt.strftime("%Y-%m-%d")).agg(
        total_pitches=("description","size")).reset_index().rename(columns={"game_date":"date"})
    slg = sl.groupby(sl.game_date.dt.strftime("%Y-%m-%d")).agg(
        sliders=("description","size")).reset_index().rename(columns={"game_date":"date"})
    arc = per_game.merge(slg,on="date",how="left").fillna({"sliders":0})
    arc = arc[arc.date >= SLIDER_DEBUT].copy()
    arc["sl_usage"] = (arc.sliders/arc.total_pitches).round(3)
    slw = whiff_rate(["game_year"], sl) if len(sl) else pd.DataFrame()
    sl_whiff = float(slw.whiff_rate.iat[0]) if len(slw) else np.nan
    arc.to_csv(os.path.join(OUT_DIR,"dp_uc25_slider_arc.csv"),index=False)

    # --- 7. process + ABS KPIs by year -----------------------------------
    def year_process(df):
        yrs = sorted(df.game_year.unique())
        rows=[]
        for y in yrs:
            g = df[df.game_year==y]
            fp = fpsr(["game_year"],g); ch = chase_rate(["game_year"],g)
            pa = putaway_rate(["game_year"],g); ed = edge_rate(["game_year"],g)
            oz = ooz_called_strike_rate(["game_year"],g); cu = chase_up_rate(["game_year"],g)
            rows.append(dict(game_year=y,
                first_pitch_strike_rate=float(fp.first_pitch_strike_rate.iat[0]),
                chase_rate=float(ch.chase_rate.iat[0]),
                in_zone_rate=float(ch.in_zone_rate.iat[0]),
                putaway_rate=float(pa.putaway_rate.iat[0]),
                edge_rate=float(ed.edge_rate.iat[0]),
                ooz_called_strike_rate=float(oz.ooz_called_strike_rate.iat[0]),
                chase_up_rate=float(cu.chase_up_rate.iat[0])))
        return pd.DataFrame(rows).round(3)
    proc_year = year_process(career)
    proc_year.to_csv(os.path.join(OUT_DIR,"dp_uc25_process_abs_by_year.csv"),index=False)

    # --- 8. contact quality by year (the engine) -------------------------
    cq_rows=[]
    for y in sorted(career.game_year.unique()):
        g = career[career.game_year==y]
        ag = air_gb_rate(["game_year"],g); hh = hard_hit_rate(["game_year"],g)
        nr = nresults(["game_year"],g); xwc = xwobacon(["game_year"],g)
        cq_rows.append(dict(game_year=y, bip=int(ag.bip.iat[0]),
            gb_rate=float(ag.gb_rate.iat[0]), air_rate=float(ag.air_rate.iat[0]),
            ld_rate=float(ag.ld_rate.iat[0]), fb_rate=float(ag.fb_rate.iat[0]),
            hard_hit_rate=float(hh.hard_hit_rate.iat[0]),
            hr_rate=float(nr.hr_rate.iat[0]),
            xwobacon=float(xwc.xwobacon.iat[0]) if len(xwc) else np.nan))
    cq = pd.DataFrame(cq_rows).round(3)
    cq.to_csv(os.path.join(OUT_DIR,"dp_uc25_contact_quality_by_year.csv"),index=False)

    # --- 9. LHB vs RHB process, 2026 (underlying indicators) -------------
    ps_rows=[]
    for st in ["L","R"]:
        g = d26[d26.stand==st]
        fp = fpsr(["stand"],g); ch = chase_rate(["stand"],g); pa = putaway_rate(["stand"],g)
        wh = whiff_rate(["stand"],g); hh = hard_hit_rate(["stand"],g); nr = nresults(["stand"],g)
        ag = air_gb_rate(["stand"],g); xwc = xwobacon(["stand"],g)
        ps_rows.append(dict(stand=st, PA=int(nr.plate_apps.iat[0]),
            woba=float(nr.woba.iat[0]),
            xwobacon=float(xwc.xwobacon.iat[0]) if len(xwc) else np.nan,
            bb_rate=float(nr.bbrate.iat[0]), k_rate=float(nr.krate.iat[0]),
            first_pitch_strike_rate=float(fp.first_pitch_strike_rate.iat[0]),
            putaway_rate=float(pa.putaway_rate.iat[0]),
            whiff_rate=float(wh.whiff_rate.iat[0]), chase_rate=float(ch.chase_rate.iat[0]),
            hard_hit_rate=float(hh.hard_hit_rate.iat[0]), air_rate=float(ag.air_rate.iat[0])))
    proc_stand = pd.DataFrame(ps_rows).round(3)
    proc_stand.to_csv(os.path.join(OUT_DIR,"dp_uc25_process_by_stand_2026.csv"),index=False)

    # --- 10. Dodgers H2H (name-parsed from Nola's own log) ---------------
    ab_last = career.sort_values(["game_pk","at_bat_number","pitch_number"]).groupby(
        ["game_pk","at_bat_number"],as_index=False).last()
    def batter_name(des):
        if not isinstance(des,str) or not des: return None
        toks = des.replace(".","").split()
        return " ".join(toks[:2]) if len(toks)>=2 else None
    ab_last["batter_name"]=ab_last.des.map(batter_name)
    name_map = (ab_last.dropna(subset=["batter_name"])
                .groupby("batter")["batter_name"]
                .agg(lambda s: s.mode().iat[0]).to_dict())
    want = {h["name"].replace("'","").lower(): h for h in HITTERS}
    h2h_rows=[]
    for bid,bname in name_map.items():
        key = bname.replace("'","").lower()
        if key in want:
            sub = career[career.batter==bid]
            nr = nresults(["batter"], sub).drop(columns=["batter"])
            wh = whiff_rate(["batter"], sub); xwc = xwobacon(["batter"], sub)
            info = want[key]
            modal_stand = sub.stand.mode().iat[0] if len(sub.stand.mode()) else stand_vs_rhp(info["bats"])
            row = dict(name=info["name"], bats=info["bats"], stand_vs_nola=modal_stand,
                       PA=int(nr.plate_apps.iat[0]), H=int(nr.hits.iat[0]), HR=int(nr.hrs.iat[0]),
                       BB=int(nr.walks.iat[0]), K=int(nr.strikeouts.iat[0]),
                       whiff_rate=float(wh.whiff_rate.iat[0]) if len(wh) else np.nan,
                       ba=float(nr.ba.iat[0]), slg=float(nr.slg.iat[0]),
                       woba=float(nr.woba.iat[0]),
                       xwobacon=float(xwc.xwobacon.iat[0]) if len(xwc) else np.nan,
                       first_seen=str(sub.game_date.min().date()),
                       last_seen=str(sub.game_date.max().date()))
            h2h_rows.append(row)
    order = {h["name"]:i for i,h in enumerate(HITTERS)}
    h2h = pd.DataFrame(h2h_rows)
    if len(h2h):
        h2h["ord"]=h2h.name.map(order); h2h=h2h.sort_values("ord").drop(columns=["ord"]).round(3)
    # note any named hitter with no H2H found
    found = set(h2h.name) if len(h2h) else set()
    missing = [h["name"] for h in HITTERS if h["name"] not in found]
    h2h.to_csv(os.path.join(OUT_DIR,"dp_uc25_dodgers_h2h.csv"),index=False)

    # --- 11. DQ scorecard + freshness manifest ---------------------------
    key_cdes=["pitch_name","release_speed","plate_x","plate_z","zone","description",
              "events","stand","bb_type","launch_angle","launch_speed","woba_value","woba_denom"]
    dq=[dict(check="entity_lock",detail="pitcher==605400 only (Nolan Hoffman 676510 excluded)",
             result="PASS" if set(career.pitcher.unique())=={NOLA} else "FAIL"),
        dict(check="dedup",detail="game_pk+at_bat_number+pitch_number unique",
             result="PASS" if not career.duplicated(["game_pk","at_bat_number","pitch_number"]).any() else "FAIL"),
        dict(check="game_type",detail="regular season only",
             result="PASS" if set(career.game_type.unique())=={"R"} else "FAIL"),
        dict(check="season_coverage",detail="career log spans 2015..2026",
             result="PASS" if career.game_year.min()==2015 and career.game_year.max()==2026 else "FAIL"),
        dict(check="freshness",detail=f"max game_date == {career.game_date.max():%Y-%m-%d} (Nola last start)",
             result="PASS" if str(career.game_date.max().date())=="2026-07-16" else "WARN"),
        dict(check="h2h_coverage",detail=f"named hitters resolved: {len(found)}/7; missing: {missing}",
             result="PASS" if len(found)>=1 else "WARN")]
    for c in key_cdes:
        nn = career[c].notna().mean() if c in career.columns else 0.0
        dq.append(dict(check=f"completeness:{c}",detail="career log non-null share",
                       result=round(float(nn),3)))
    pd.DataFrame(dq).to_csv(os.path.join(OUT_DIR,"dp_uc25_dq_scorecard.csv"),index=False)

    fresh=pd.DataFrame([
        dict(source="data/phillies/phils_2015..2026.parquet",
             window=f"2015-04..{career.game_date.max():%Y-%m-%d}",
             rows=len(career),note="career MLB pitch log, entity-locked pitcher==605400, R games only"),
        dict(source="data/phillies/phils_2026.parquet",
             window=f"2026-03-28..{d26.game_date.max():%Y-%m-%d}",
             rows=len(d26),note=f"2026 season-to-date, {n_starts_26} starts; cache through Nola's last start 7/16"),
        dict(source="DPO scope decision (manual carry-in)",window=GAME_DAY,rows=len(HITTERS),
             note="matchup restricted to 7 named Dodgers hitters; not a posted 1-9 card"),
    ])
    fresh.to_csv(os.path.join(OUT_DIR,"dp_uc25_freshness_manifest.csv"),index=False)

    # --- 12. FIGURES -----------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # fig 1: arsenal map by stand (catcher's view)
    fig,axes=plt.subplots(1,2,figsize=(11,5.5),sharey=True)
    for ax,st,ttl in zip(axes,["R","L"],["vs RHB","vs LHB"]):
        sub=ars[ars.stand==st].sort_values("usage",ascending=False)
        handles=[]
        for _,row in sub.iterrows():
            c=PITCH_COLORS.get(row.pitch_name,PHI_GRAY)
            wtxt = f"{row.whiff_rate:.0%}" if pd.notna(row.whiff_rate) else "—"
            h=ax.scatter(row.px,row.pz,s=max(row.usage*3000,60),color=c,alpha=.75,
                         edgecolor=PHI_NAVY,linewidth=1.2,zorder=3,
                         label=f"{row.pitch_name} — {row.usage:.0%} use / {wtxt} whiff")
            handles.append(h)
        ax.legend(handles=handles,loc="lower center",fontsize=7.5,frameon=False,
                  scatterpoints=1,markerscale=.35)
        zt,zb=d26.sz_top.mean(),d26.sz_bot.mean()
        ax.add_patch(plt.Rectangle((-0.83,zb),1.66,zt-zb,fill=False,edgecolor=PHI_NAVY,linewidth=1.5,zorder=2))
        ax.set_xlim(-2.2,2.2); ax.set_ylim(0,4.6)
        ax.set_title(f"Nola 2026 — {ttl}",color=PHI_NAVY,fontsize=11,weight="bold")
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("Aaron Nola — average pitch location by type (catcher's view)",color=PHI_NAVY,weight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR,"dp_uc25_nola_arsenal_map.png"),dpi=160); plt.close(fig)

    # fig 2: usage x whiff by pitch, 2026
    order_p=["Knuckle Curve","4-Seam Fastball","Sinker","Changeup","Cutter","Slider"]
    mix=d26.groupby("pitch_name").size().reindex(order_p).fillna(0); mix=mix/mix.sum()
    wh=whiff_rate(["pitch_name"],d26).set_index("pitch_name").whiff_rate.reindex(order_p)
    fig,ax=plt.subplots(figsize=(10,4.8)); x=np.arange(len(order_p))
    ax.bar(x-.2,mix,.4,color=[PITCH_COLORS[o] for o in order_p],alpha=.9,label="usage")
    ax.bar(x+.2,wh,.4,color=PHI_NAVY,alpha=.55,label="whiff rate")
    for xx,(m,ww) in enumerate(zip(mix,wh)):
        if pd.notna(m): ax.text(xx-.2,m+.008,f"{m:.0%}",ha="center",fontsize=8.5)
        if pd.notna(ww): ax.text(xx+.2,ww+.008,f"{ww:.0%}",ha="center",fontsize=8.5,color=PHI_NAVY)
    ax.set_xticks(x); ax.set_xticklabels([o.replace(" Fastball","") for o in order_p],fontsize=9)
    ax.set_ylim(0,.62); ax.grid(axis="y",color=PHI_LGRAY,zorder=0); ax.legend(fontsize=8.5)
    ax.set_title(f"Aaron Nola 2026 — usage vs whiff by pitch ({n_starts_26} starts)",color=PHI_NAVY,weight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR,"dp_uc25_usage_whiff_2026.png"),dpi=160); plt.close(fig)

    # fig 3: recency — per-start wOBA + rolling, plus usage tracks for key pitches
    gl = glines.copy(); gl["dt"]=pd.to_datetime(gl.game_date); gl=gl.sort_values("dt").reset_index(drop=True)
    gl["idx"]=np.arange(len(gl)); gl["roll"]=gl.woba.rolling(5,min_periods=1).mean()
    key_p=["Knuckle Curve","Sinker","4-Seam Fastball","Slider"]
    usage_by_start = (d26.groupby([d26.game_date.dt.strftime("%Y-%m-%d"),"pitch_name"]).size()
                      .rename("n").reset_index().rename(columns={"game_date":"date"}))
    tot_by_start = d26.groupby(d26.game_date.dt.strftime("%Y-%m-%d")).size().rename("tot")
    usage_by_start=usage_by_start.merge(tot_by_start,left_on="date",right_index=True)
    usage_by_start["u"]=usage_by_start.n/usage_by_start.tot
    fig,(axa,axb)=plt.subplots(2,1,figsize=(11,7),sharex=True,gridspec_kw=dict(height_ratios=[1.1,1]))
    axa.plot(gl.idx,gl.woba,marker="o",color=PHI_GRAY,lw=1,ms=5,label="wOBA per start")
    axa.plot(gl.idx,gl.roll,color=PHI_NAVY,lw=2.4,label="5-start rolling wOBA")
    newpos=gl[gl.dt>pd.Timestamp(LAST_REPORT_THROUGH)]
    axa.scatter(newpos.idx,newpos.woba,s=120,color=PHI_RED,zorder=5,edgecolor="white",
                label="3 starts since last report")
    axa.set_ylabel("wOBA against"); axa.grid(color=PHI_LGRAY,alpha=.6)
    axa.legend(fontsize=8,loc="upper left")
    axa.set_title(f"Aaron Nola 2026 — results by start and pitch mix over time ({n_starts_26} starts)",
                  color=PHI_NAVY,weight="bold")
    dorder=list(gl.game_date)
    for pn in key_p:
        sub=usage_by_start[usage_by_start.pitch_name==pn].set_index("date").reindex(dorder).reset_index()
        axb.plot(np.arange(len(dorder)),sub.u,marker=".",lw=1.6,
                 color=PITCH_COLORS.get(pn,PHI_GRAY),label=pn.replace(" Fastball",""))
    axb.axvline(gl[gl.dt>pd.Timestamp(LAST_REPORT_THROUGH)].idx.min()-0.5,color=PHI_RED,ls="--",alpha=.7)
    axb.set_ylabel("usage share"); axb.set_xticks(gl.idx)
    axb.set_xticklabels([d[5:] for d in gl.game_date],rotation=90,fontsize=7)
    axb.grid(color=PHI_LGRAY,alpha=.6); axb.legend(fontsize=8,ncol=4,loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR,"dp_uc25_recency_approach.png"),dpi=160); plt.close(fig)

    # fig 4: ABS revisit (edge & ooz-called-strike by year) + 2026 LHB/RHB process
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12,5))
    py=proc_year.sort_values("game_year")
    ax1.plot(py.game_year,py.edge_rate,marker="o",color=PHI_NAVY,label="edge rate")
    ax1.plot(py.game_year,py.ooz_called_strike_rate,marker="s",color=PHI_RED,label="OOZ called-strike rate")
    ax1.plot(py.game_year,py.chase_up_rate,marker="^",color=PHI_GRAY,label="chase-up rate")
    ax1.axvline(2025.5,color=PHI_LGRAY,ls=":"); ax1.set_xticks(py.game_year[::1])
    ax1.set_xticklabels(py.game_year,rotation=90,fontsize=7)
    ax1.set_title("The ABS question, re-tested\n(edge command intact; stolen strike a slow decade decline)",
                  color=PHI_NAVY,weight="bold",fontsize=10)
    ax1.grid(color=PHI_LGRAY,alpha=.5); ax1.legend(fontsize=8)
    labels=["wOBA","xwOBAcon","BB%","K%","1P-strike%","putaway%","whiff%","hard-hit%"]
    Lv=proc_stand[proc_stand.stand=="L"].iloc[0]; Rv=proc_stand[proc_stand.stand=="R"].iloc[0]
    Lvals=[Lv.woba,Lv.xwobacon,Lv.bb_rate,Lv.k_rate,Lv.first_pitch_strike_rate,Lv.putaway_rate,Lv.whiff_rate,Lv.hard_hit_rate]
    Rvals=[Rv.woba,Rv.xwobacon,Rv.bb_rate,Rv.k_rate,Rv.first_pitch_strike_rate,Rv.putaway_rate,Rv.whiff_rate,Rv.hard_hit_rate]
    xx=np.arange(len(labels))
    ax2.bar(xx-.2,Lvals,.4,color=PHI_RED,alpha=.85,label=f"vs LHB (n={int(Lv.PA)} PA)")
    ax2.bar(xx+.2,Rvals,.4,color=PHI_NAVY,alpha=.85,label=f"vs RHB (n={int(Rv.PA)} PA)")
    ax2.set_xticks(xx); ax2.set_xticklabels(labels,rotation=45,ha="right",fontsize=8)
    ax2.set_title("2026 process split by batter side\n(the leak is the free pass, not the whiff)",
                  color=PHI_NAVY,weight="bold",fontsize=10)
    ax2.grid(axis="y",color=PHI_LGRAY,alpha=.5); ax2.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR,"dp_uc25_process_abs_panel.png"),dpi=160); plt.close(fig)

    # fig 5: contact-quality engine by year
    fig,ax=plt.subplots(figsize=(10,5)); cy=cq.sort_values("game_year")
    ax.plot(cy.game_year,cy.gb_rate,marker="o",color=PHI_NAVY,label="ground-ball rate")
    ax.plot(cy.game_year,cy.air_rate,marker="s",color=PHI_GRAY,label="air-ball rate")
    ax.plot(cy.game_year,cy.hard_hit_rate,marker="^",color=PHI_RED,label="hard-hit rate (>=95)")
    ax2=ax.twinx(); ax2.bar(cy.game_year,cy.hr_rate,color=PHI_RED,alpha=.18,label="HR rate (per PA)")
    ax.set_xticks(cy.game_year); ax.set_xticklabels(cy.game_year,rotation=90,fontsize=7)
    ax.set_ylabel("batted-ball share / hard-hit"); ax2.set_ylabel("HR rate per PA",color=PHI_RED)
    ax.set_title("The real engine — ground balls down, air & hard contact up (career)",color=PHI_NAVY,weight="bold")
    ax.grid(color=PHI_LGRAY,alpha=.5)
    h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
    ax.legend(h1+h2,l1+l2,fontsize=8,loc="center left")
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR,"dp_uc25_contact_quality.png"),dpi=160); plt.close(fig)

    # fig 6: Dodgers H2H matrix — career wOBA vs Nola, PA annotated
    if len(h2h):
        hh=h2h.sort_values("woba")
        colors=[PHI_RED if wv>=.360 else (PHI_NAVY if wv<=.300 else PHI_GRAY) for wv in hh.woba]
        fig,ax=plt.subplots(figsize=(10,5.2))
        bars=ax.barh(np.arange(len(hh)),hh.woba,color=colors,alpha=.9,edgecolor=PHI_NAVY)
        ax.set_yticks(np.arange(len(hh)))
        ax.set_yticklabels([f"{n} ({s})" for n,s in zip(hh.name,hh.stand_vs_nola)],fontsize=9)
        for i,(wv,pa,hr) in enumerate(zip(hh.woba,hh.PA,hh.HR)):
            ax.text(wv+.005,i,f"{wv:.3f}  ·  {int(pa)} PA{' · '+str(int(hr))+' HR' if hr else ''}",
                    va="center",fontsize=8.5,color=PHI_NAVY)
        ax.axvline(.320,color=PHI_LGRAY,ls="--",label="~2026 season wOBA-against")
        ax.set_xlim(0,max(.75,hh.woba.max()+.15)); ax.set_xlabel("career wOBA vs Nola")
        ax.set_title("The seven Dodgers, head-to-head vs Nola (career; small samples — PA shown)",
                     color=PHI_NAVY,weight="bold",fontsize=11)
        ax.legend(fontsize=8,loc="lower right")
        fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR,"dp_uc25_dodgers_h2h_matrix.png"),dpi=160); plt.close(fig)

    # --- console receipts ------------------------------------------------
    print(f"UC-PPS-021 (dp_uc25) build complete. | 2026 starts: {n_starts_26} "
          f"| freshness: {career.game_date.max():%Y-%m-%d} | H2H found: {len(found)}/7 missing={missing}")
    print(); print("SEASON TREND (tail):"); print(trend.tail(5).to_string(index=False))
    print(); print("BY STAND 2026:"); print(stand.to_string(index=False))
    print(); print("RECENCY SPLIT:"); print(recency.to_string(index=False))
    print(); print("MONTHLY USAGE:"); print(mu_wide.to_string(index=False))
    print(); print("PROCESS/ABS BY YEAR (tail):"); print(proc_year.tail(5).to_string(index=False))
    print(); print("CONTACT QUALITY (tail):"); print(cq.tail(5).to_string(index=False))
    print(); print("PROCESS BY STAND 2026:"); print(proc_stand.to_string(index=False))
    print(); print(f"SLIDER: n={len(sl)} whiff={sl_whiff}")
    print(); print("DODGERS H2H:"); print(h2h.to_string(index=False) if len(h2h) else "NONE FOUND")

if __name__ == "__main__":
    main()
