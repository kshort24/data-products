"""
============================================================================
GOVERNED DATA PRODUCT — USE CASE #20 (uc-pps-018, build prefix dp_uc19)
"Jhoan Duran — First-Half 2026 All-Star Assessment: what changed, and is
 the improvement real?"
============================================================================

Layer-3 BUILD artifact for the Phillies Pitching (pps) value stream.
Retrospective shape inherited from uc-pos-marsh-breakout-001 (dp_uc18) and
uc-pps-017 (Luzardo first-half ASG); pps KPI kernel inherited from dp_uc11
(which inherited from dp_uc8). Numbering note (spec §1): pps contract ids
run through 017 and build prefixes 17 (Luzardo, pending paste) and 18
(Marsh) are taken — this UC is uc-pps-018 / dp_uc19.

Business question (Kellen, DPO): Duran has been lights-out closing for the
Phillies in the first half of 2026 — better than his late-2025 Phillies
stint and his Twins career. HAS HE DONE ANYTHING DIFFERENTLY? Saves (24)
are a MANUAL CARRY-IN (not derivable-by-agreement from pitch-level data;
DPO decision 2026-07-13) — this product carries the process receipts.

Governance lineage (see 00–07 in this folder):
  - data-product-owner     : sequenced as UC#20; depth = full package
  - use-case-validator     : intake gate — gap report (02)
  - source-system-profiler : entity lock pitcher==661395 across 3 sources;
                             ZERO game_pk overlap at the Twins/Phillies seam
                             (duran.parquet ends 2025-07-28; phils_2025
                             stint starts 2025-08-01)
  - kpi-calculator         : locked cores inherited VERBATIM from dp_uc11
                             (get_stats/nresults, whiff_rate, chase_rate,
                             putaway_rate, fpsr, hard_hit_rate). NO new KPIs.
  - data-quality-engineer  : scorecard in out/dp_uc19_dq_scorecard.csv

DATA WINDOW / FRESHNESS:
  * MIN 2022–2025: data/opponents/duran.parquet (Twins log, R games,
    2022-04-08 .. 2025-07-28 = pre-trade).
  * PHI 2025: phils_2025.parquet, phillies_role=='pitching', post-trade
    stint 2025-08-01 .. season end (308 R pitches — SMALL, flagged).
  * PHI 2026 1H: phils_2026.parquet, through cache 2026-07-12 (last
    appearance 2026-07-11). 515 R pitches / 34 games.
  * game_type=='R' everywhere. Postseason (D/F) EXCLUDED and noted.
  * MANUAL CARRY-INS: 24 saves (DPO, 2026-07-13); 2026 All-Star selection.

OUTPUTS (NEW files, none overwritten), written to <repo>/out/:
  dp_uc19_duran_era_trend.csv          nresults + process KPIs by era
  dp_uc19_duran_arsenal_by_era.csv     pitch-level arsenal evolution by era
  dp_uc19_duran_2026_arsenal_by_stand.csv  2026 arsenal split by batter stand
  dp_uc19_duran_2026_monthly.csv       2026 month-by-month (PA flagged)
  dp_uc19_duran_putaway_by_pitch.csv   2-strike weapon detail, 2026 vs prior
  dp_uc19_duran_changeup_detail.csv    the NEW pitch — usage/whiff/xwOBA
  dp_uc19_dq_scorecard.csv             data-quality-engineer scorecard
  dp_uc19_freshness_manifest.csv       source/window receipts + carry-ins
  dp_uc19_arsenal_evolution.png        fig 1 — usage by era
  dp_uc19_era_trend.png                fig 2 — wOBA/xwOBA/whiff by era
  dp_uc19_2026_arsenal_map.png         fig 3 — 2026 locations by stand
============================================================================
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

DURAN = 661395                     # Jhoan Duran, MLBAM pitcher id (entity lock)
CURRENT_YEAR = 2026
CACHE_FRESH = "2026-07-12"
SAVES_CARRY_IN = 24                # MANUAL CARRY-IN — DPO (Kellen), 2026-07-13

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "phillies"),                       # script at repo root
    os.path.abspath(os.path.join(HERE, "..", "..", "data", "phillies")),  # data-products/<uc>/
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies",
]
PHIL_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
if PHIL_DIR is None:
    raise FileNotFoundError("Could not locate data/phillies. Set MLB_DATA_ROOT.")
REPO = os.path.dirname(os.path.dirname(PHIL_DIR))
OPP_DIR = os.path.join(os.path.dirname(PHIL_DIR), "opponents")
OUT_DIR = os.path.join(REPO, "out"); os.makedirs(OUT_DIR, exist_ok=True)
_WOBA_CANDIDATES = [
    os.path.join(REPO, "wOBA and FIP Constants.csv"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv",
]
WOBA_CSV = next((p for p in _WOBA_CANDIDATES if os.path.isfile(p)), None)

SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]

PHI_RED, PHI_NAVY, PHI_GRAY, PHI_LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
PITCH_COLORS = {"Split-Finger": "#E81828", "4-Seam Fastball": "#002D72",
                "Knuckle Curve": "#2CA02C", "Sweeper": "#1F77B4",
                "Changeup": "#FF7F0E"}
PITCH_ORDER = ["Split-Finger", "4-Seam Fastball", "Knuckle Curve", "Sweeper", "Changeup"]

ERA_ORDER = ["MIN 2022", "MIN 2023", "MIN 2024", "MIN 2025",
             "PHI 2025", "PHI 2026 1H"]

# ===========================================================================
# LOADERS
# ===========================================================================
def _coerce(df):
    for c in ["plate_x","plate_z","sz_top","sz_bot","pfx_x","pfx_z","release_speed",
              "release_spin_rate","launch_speed","launch_angle","strikes","balls",
              "pitch_number","woba_value","woba_denom","zone","release_extension"]:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def _weights(df):
    if WOBA_CSV:
        w = pd.read_csv(WOBA_CSV)
        df = df.drop(columns=[c for c in w.columns if c != "Season" and c in df.columns])
        df = df.merge(w, left_on="game_year", right_on="Season", how="left")
    return df

def load_duran():
    """Full career pitch log: Twins cache + Phillies caches. Entity-locked,
    regular season only, deduped, era-labeled."""
    frames = []
    # Twins era (pre-trade). Cache verified to end 2025-07-28.
    tw = pd.read_parquet(os.path.join(OPP_DIR, "duran.parquet"))
    tw = tw[(tw.pitcher == DURAN) & (tw.game_type == "R")].copy()
    tw["era"] = "MIN " + tw.game_year.astype(int).astype(str)
    frames.append(tw)
    # Phillies era (post-trade 2025 + 2026 first half).
    for yr in (2025, 2026):
        d = pd.read_parquet(os.path.join(PHIL_DIR, f"phils_{yr}.parquet"))
        d = d[(d.phillies_role == "pitching") & (d.pitcher == DURAN) & (d.game_type == "R")].copy()
        d["era"] = f"PHI {yr}" + (" 1H" if yr == CURRENT_YEAR else "")
        frames.append(d)
    common = list(set.intersection(*[set(f.columns) for f in frames]))
    full = pd.concat([f[common] for f in frames], ignore_index=True)
    full = full.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    full = _coerce(full)
    full = _weights(full)
    return full

# ===========================================================================
# LOCKED KPI FUNCTIONS — inherited verbatim from dp_uc11 (lineage dp_uc8 /
# Baseball Functions library). Do not edit.
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
# BUILD
# ===========================================================================
def _era_sort(df, col="era"):
    df[col] = pd.Categorical(df[col], categories=ERA_ORDER, ordered=True)
    return df.sort_values(col)

def main():
    full = load_duran()
    d26 = full[full.era == "PHI 2026 1H"].copy()

    # --- 1. era trend: results + process KPIs -----------------------------
    trend = nresults(["era"], full)
    games = full.groupby("era", as_index=False).agg(games=("game_pk", "nunique"))
    trend = trend.merge(games, on="era")
    # xwOBA/xBA from the locked get_stats (same lineage; nresults doesn't emit them)
    trend = trend.merge(get_stats(["era"], full)[["era", "xba", "xwoba"]].round(3),
                        on="era", how="left")
    for fn, keep in [(whiff_rate, ["whiff_rate"]),
                     (chase_rate, ["chase_rate", "in_zone_rate"]),
                     (putaway_rate, ["putaway_rate"]),
                     (fpsr, ["first_pitch_strike_rate"]),
                     (hard_hit_rate, ["hard_hit_rate"])]:
        trend = trend.merge(fn(["era"], full)[["era"] + keep], on="era", how="left")
    trend = _era_sort(trend)
    trend.to_csv(os.path.join(OUT_DIR, "dp_uc19_duran_era_trend.csv"), index=False)

    # --- 2. arsenal evolution by era ---------------------------------------
    ars = full.groupby(["era", "pitch_name"], as_index=False).agg(
        n=("description", "size"), velo=("release_speed", "mean"),
        spin=("release_spin_rate", "mean"), pfx_x=("pfx_x", "mean"),
        pfx_z=("pfx_z", "mean"), ext=("release_extension", "mean"),
        xwoba=("estimated_woba_using_speedangle", "mean"))
    tot = ars.groupby("era", as_index=False).n.sum().rename(columns={"n": "n_era"})
    ars = ars.merge(tot, on="era"); ars["usage"] = ars.n / ars.n_era
    w = whiff_rate(["era", "pitch_name"], full)
    ars = ars.merge(w[["era", "pitch_name", "swings", "whiffs", "whiff_rate"]],
                    on=["era", "pitch_name"], how="left")
    ars = _era_sort(ars.round(3))
    ars.to_csv(os.path.join(OUT_DIR, "dp_uc19_duran_arsenal_by_era.csv"), index=False)

    # --- 3. 2026 arsenal by batter stand -----------------------------------
    st = d26.groupby(["stand", "pitch_name"], as_index=False).agg(
        n=("description", "size"), velo=("release_speed", "mean"),
        px=("plate_x", "mean"), pz=("plate_z", "mean"),
        xwoba=("estimated_woba_using_speedangle", "mean"))
    stot = st.groupby("stand", as_index=False).n.sum().rename(columns={"n": "n_stand"})
    st = st.merge(stot, on="stand"); st["usage"] = st.n / st.n_stand
    sw = whiff_rate(["stand", "pitch_name"], d26)
    st = st.merge(sw[["stand", "pitch_name", "swings", "whiffs", "whiff_rate"]],
                  on=["stand", "pitch_name"], how="left").round(3)
    st.to_csv(os.path.join(OUT_DIR, "dp_uc19_duran_2026_arsenal_by_stand.csv"), index=False)

    # --- 4. 2026 month-by-month (small PA — always shown) ------------------
    d26["month"] = d26.game_date.astype(str).str[:7]
    monthly = nresults(["month"], d26)
    mg = d26.groupby("month", as_index=False).agg(games=("game_pk", "nunique"))
    monthly = monthly.merge(mg, on="month")
    mw = whiff_rate(["month"], d26)[["month", "whiff_rate"]]
    monthly = monthly.merge(mw, on="month", how="left")
    monthly.to_csv(os.path.join(OUT_DIR, "dp_uc19_duran_2026_monthly.csv"), index=False)

    # --- 5. 2-strike weapon: putaway by pitch, 2026 vs prior eras ----------
    grp = full.assign(era_group=np.where(full.era == "PHI 2026 1H",
                                         "PHI 2026 1H", "Career pre-2026"))
    pa_pitch = putaway_rate(["era_group", "pitch_name"], grp)
    pa_pitch.to_csv(os.path.join(OUT_DIR, "dp_uc19_duran_putaway_by_pitch.csv"), index=False)

    # --- 6. the NEW pitch: changeup detail ---------------------------------
    ch = d26[d26.pitch_name == "Changeup"]
    ff_velo = d26[d26.pitch_name == "4-Seam Fastball"].release_speed.mean()
    ch_by_stand = ch.groupby("stand", as_index=False).agg(
        n=("description", "size"), velo=("release_speed", "mean"),
        xwoba=("estimated_woba_using_speedangle", "mean"))
    chw = whiff_rate(["stand"], ch) if len(ch) else pd.DataFrame()
    if len(chw):
        ch_by_stand = ch_by_stand.merge(chw[["stand", "swings", "whiffs", "whiff_rate"]],
                                        on="stand", how="left")
    ch_by_stand["ff_velo_2026"] = round(float(ff_velo), 1)
    ch_by_stand["ch_ff_sep"] = (ch_by_stand.ff_velo_2026 - ch_by_stand.velo).round(1)
    ch_by_stand = ch_by_stand.round(3)
    ch_by_stand.to_csv(os.path.join(OUT_DIR, "dp_uc19_duran_changeup_detail.csv"), index=False)

    # --- 7. DQ scorecard ----------------------------------------------------
    key_cdes = ["pitch_name", "release_speed", "plate_x", "plate_z", "zone",
                "description", "events", "stand", "woba_value", "woba_denom",
                "estimated_woba_using_speedangle"]
    tw_max = full[full.era.astype(str).str.startswith("MIN")].game_date.max()
    ph_min = full[full.era.astype(str) == "PHI 2025"].game_date.min()
    dq = [dict(check="entity_lock", detail="pitcher==661395 only, all sources",
               result="PASS" if set(full.pitcher.unique()) == {DURAN} else "FAIL"),
          dict(check="dedup", detail="game_pk+at_bat_number+pitch_number unique",
               result="PASS" if not full.duplicated(["game_pk","at_bat_number","pitch_number"]).any() else "FAIL"),
          dict(check="game_type", detail="regular season only (D/F excluded)",
               result="PASS" if set(full.game_type.unique()) == {"R"} else "FAIL"),
          dict(check="era_seam", detail=f"Twins cache max {str(tw_max)[:10]} < PHI 2025 min {str(ph_min)[:10]}",
               result="PASS" if str(tw_max) < str(ph_min) else "FAIL"),
          dict(check="woba_weights", detail="season weights joined for all rows",
               result="PASS" if full.wBB.notna().all() else "FAIL")]
    for c in key_cdes:
        nn = full[c].notna().mean() if c in full.columns else 0.0
        dq.append(dict(check=f"completeness:{c}", detail="career log non-null share",
                       result=round(float(nn), 3)))
    pd.DataFrame(dq).to_csv(os.path.join(OUT_DIR, "dp_uc19_dq_scorecard.csv"), index=False)

    # --- 8. freshness manifest (incl. manual carry-ins) ---------------------
    fresh = pd.DataFrame([
        dict(source="data/opponents/duran.parquet", window="2022-04-08..2025-07-28",
             rows=int((full.era.astype(str).str.startswith("MIN")).sum()),
             note="Twins era, pre-trade; entity-locked, R games"),
        dict(source="data/phillies/phils_2025.parquet", window="2025-08-01..2025-09-28",
             rows=int((full.era.astype(str) == "PHI 2025").sum()),
             note="post-trade Phillies stint; SMALL sample, flagged"),
        dict(source="data/phillies/phils_2026.parquet", window=f"2026 opening day..{CACHE_FRESH}",
             rows=len(d26), note="2026 first half; last appearance 2026-07-11"),
        dict(source="MANUAL CARRY-IN (DPO, 2026-07-13)", window="2026 first half",
             rows=SAVES_CARRY_IN, note="24 saves — not derived from pitch data by DPO decision"),
        dict(source="MANUAL CARRY-IN (DPO, 2026-07-13)", window="2026-07-13",
             rows=1, note="2026 NL All-Star selection"),
    ])
    fresh.to_csv(os.path.join(OUT_DIR, "dp_uc19_freshness_manifest.csv"), index=False)

    # --- 9. figures ----------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # fig 1: arsenal evolution — usage by era
    fig, ax = plt.subplots(figsize=(10, 5))
    eras = [e for e in ERA_ORDER if e in set(ars.era.astype(str))]
    x = np.arange(len(eras)); nb = len(PITCH_ORDER); bw = 0.16
    for i, p in enumerate(PITCH_ORDER):
        vals = [float(ars[(ars.era.astype(str) == e) & (ars.pitch_name == p)].usage.sum()) for e in eras]
        ax.bar(x + (i - nb/2 + .5) * bw, vals, bw, color=PITCH_COLORS[p], label=p, zorder=3)
        for xx, v in zip(x, vals):
            if v >= 0.04:
                ax.text(xx + (i - nb/2 + .5) * bw, v + .008, f"{v:.0%}",
                        ha="center", fontsize=7, color=PHI_NAVY)
    ax.set_xticks(x); ax.set_xticklabels(eras, fontsize=9)
    ax.set_ylim(0, .6); ax.grid(axis="y", color=PHI_LGRAY, zorder=0)
    ax.legend(fontsize=8, ncol=5, frameon=False, loc="upper left")
    ax.set_title("Jhoan Duran — arsenal usage by era: splitter-first, five pitches wide",
                 color=PHI_NAVY, weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dp_uc19_arsenal_evolution.png"), dpi=160)
    plt.close(fig)

    # fig 2: era trend — wOBA vs xwOBA (bars) + whiff (line)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    t = trend[trend.era.astype(str).isin(eras)]
    x = np.arange(len(t))
    ax.bar(x - .2, t.woba, .4, color=PHI_NAVY, label="wOBA against", zorder=3)
    ax.bar(x + .2, t.xwoba, .4, color=PHI_GRAY, label="xwOBA against", zorder=3)
    for xx, (wv, xv) in enumerate(zip(t.woba, t.xwoba)):
        ax.text(xx - .2, wv + .004, f"{wv:.3f}", ha="center", fontsize=8, color=PHI_NAVY)
        ax.text(xx + .2, xv + .004, f"{xv:.3f}", ha="center", fontsize=8, color=PHI_GRAY)
    ax2 = ax.twinx()
    ax2.plot(x, t.whiff_rate, color=PHI_RED, marker="o", linewidth=2, label="whiff rate")
    for xx, v in zip(x, t.whiff_rate):
        ax2.annotate(f"{v:.0%}", (xx, v), textcoords="offset points", xytext=(0, 7),
                     ha="center", fontsize=8, color=PHI_RED)
    ax.set_xticks(x); ax.set_xticklabels(t.era.astype(str), fontsize=9)
    ax.set_ylim(0, .40); ax2.set_ylim(.15, .50)
    ax.grid(axis="y", color=PHI_LGRAY, zorder=0)
    ax.legend(loc="upper left", fontsize=8); ax2.legend(loc="upper right", fontsize=8)
    ax.set_title("Results vs process by era — wOBA/xwOBA against, whiff rate",
                 color=PHI_NAVY, weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dp_uc19_era_trend.png"), dpi=160)
    plt.close(fig)

    # fig 3: 2026 arsenal map by stand (catcher's view)
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.5), sharey=True)
    for ax, stv, ttl in zip(axes, ["R", "L"], ["vs RHB", "vs LHB"]):
        sub = st[st.stand == stv].sort_values("usage", ascending=False)
        handles = []
        for _, row in sub.iterrows():
            c = PITCH_COLORS.get(row.pitch_name, PHI_GRAY)
            wtxt = f"{row.whiff_rate:.0%}" if pd.notna(row.whiff_rate) else "n/a"
            h = ax.scatter(row.px, row.pz, s=max(row.usage * 3000, 60), color=c, alpha=.75,
                           edgecolor=PHI_NAVY, linewidth=1.2, zorder=3,
                           label=f"{row.pitch_name} — {row.usage:.0%} use / {wtxt} whiff")
            handles.append(h)
        ax.legend(handles=handles, loc="lower center", fontsize=8, frameon=False,
                  scatterpoints=1, markerscale=.35)
        zt, zb = d26.sz_top.mean(), d26.sz_bot.mean()
        ax.add_patch(plt.Rectangle((-0.83, zb), 1.66, zt - zb, fill=False,
                                   edgecolor=PHI_NAVY, linewidth=1.5, zorder=2))
        ax.set_xlim(-2.2, 2.2); ax.set_ylim(0, 4.6)
        ax.set_title(f"Duran 2026 — {ttl}", color=PHI_NAVY, fontsize=11, weight="bold")
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("Jhoan Duran 2026 — average pitch location by type (catcher's view)",
                 color=PHI_NAVY, weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dp_uc19_2026_arsenal_map.png"), dpi=160)
    plt.close(fig)

    print("UC-PPS-018 (dp_uc19) build complete.")
    print(trend.to_string(index=False)); print()
    print(ars[["era","pitch_name","n","usage","velo","ext","whiff_rate","xwoba"]].to_string(index=False)); print()
    print(st[["stand","pitch_name","usage","velo","whiff_rate","xwoba"]].to_string(index=False)); print()
    print(monthly.to_string(index=False)); print()
    print(pa_pitch.to_string(index=False)); print()
    print(ch_by_stand.to_string(index=False))

if __name__ == "__main__":
    main()
