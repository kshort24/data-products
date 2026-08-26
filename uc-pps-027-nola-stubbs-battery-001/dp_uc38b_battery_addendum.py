"""
dp_uc38b_battery_addendum.py
==============================================================================
UC #38 · contract `uc-pps-027` · The Nola-Stubbs Battery -- ADDENDUM BUILD

WHY A SECOND SCRIPT
-------------------
`dp_uc38_nola_stubbs_battery.py` (the primary build) answers Q1/Q3/Q4 at the
`pitcher x catcher x window` grain. Running it against live data surfaced a
question the harness could not have anticipated and cannot answer at that
grain:

    The recent approach change shows up in the NON-Stubbs start too.

That single observation is the difference between "Stubbs changed the game
plan" and "Nola changed the game plan and Stubbs has caught most of it since."
Distinguishing them is the whole of Q2, so it gets its own governed build
rather than a paragraph of prose.

WHAT IS NEW HERE (all NEW-PROVISIONAL, specced in 02_engineering_design.md §C)
-----------------------------------------------------------------------------
  TR-1  Adjustment-travel test  -- does a delta appear within BOTH the Stubbs
        and the non-Stubbs strata? Battery-specific vs pitcher-level.
  TR-2  Breakpoint sensitivity scan -- the era boundary is a CHOICE; scan it.
  OC-1  Opponent-quality control  -- Nola's wOBA allowed vs an opponent minus
        the REST OF THE PHILLIES STAFF's wOBA allowed vs that same opponent,
        same season. An in-frame difficulty control that needs no league data.
  LH-1  Left-handed panel -- closes the `uc-pps-021` free-pass diagnosis.
  CH-1  Changeup performance panel -- usage, whiff, chase, zone, velo, contact.

GOVERNANCE
----------
Inherits every non-negotiable from the primary build (G1 entity lock 605400,
G2 regular season + dedup, G3 non-random catcher assignment, G4 pitch-call
attribution NOT OBSERVABLE, G5 floors are flags). Adds:

  G6  An era boundary is a researcher DEGREE OF FREEDOM. Any claim keyed to
      one must survive TR-2's scan or be reported as boundary-dependent.
  G7  A delta that appears in only ONE stratum of a non-random split is a
      HYPOTHESIS, never a finding. TR-1 exists to stop the report asserting
      otherwise.

Writes NEW files only, prefix `dp_uc38b_`. Never touches dp_uc38_* receipts.
==============================================================================
"""
from __future__ import annotations

import glob
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

NOLA = 605400
CURRENT_YEAR = 2026
GAME_DAY = "2026-08-26"

# The adjustment breakpoint. 2026-07-05 = Nola's first start after the
# All-Star-adjacent reset and the first start whose changeup share clears 19%.
# NOT a fitted breakpoint -- a stated one, scanned in TR-2 (G6).
BREAKPOINT = "2026-07-05"
BREAKPOINT_SCAN = ["2026-06-18", "2026-06-24", "2026-06-29", "2026-07-05",
                   "2026-07-10", "2026-07-16", "2026-07-22", "2026-07-28"]

STUBBS = 596117
CATCHERS = {434563: "Ruiz, Carlos", 519237: "Rupp, Cameron", 592663: "Realmuto, J.T.",
            595284: "Knapp, Andrew", 595751: "Alfaro, Jorge", 596117: "Stubbs, Garrett",
            665561: "Marchán, Rafael"}

PITCH_GROUP = {"FF": "fastball", "SI": "fastball", "FC": "fastball",
               "SL": "breaking", "ST": "breaking", "CU": "breaking", "KC": "breaking",
               "SV": "breaking", "CS": "breaking",
               "CH": "offspeed", "FS": "offspeed", "FO": "offspeed", "SC": "offspeed",
               "KN": "offspeed"}
SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]

_DATA_CANDIDATES = [os.environ.get("MLB_DATA_ROOT", ""),
                    os.path.join(HERE, "data", "phillies"),
                    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies"]
PHIL_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
_WOBA_CANDIDATES = [os.environ.get("MLB_WOBA_CSV", ""),   # env override (run-2 portability fix)
                    os.path.join(HERE, "wOBA and FIP Constants.csv"),
                    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv"]
WOBA_CSV = next((p for p in _WOBA_CANDIDATES if os.path.isfile(p)), None)

DQ: list[dict] = []


def dq(check, result, detail="", severity="INFO"):
    DQ.append(dict(check=check, result=result, detail=detail, severity=severity))
    print(f"  [{severity:<4}] {check}: {result}  {detail}")


# --------------------------------------------------------------------------
# LOAD (mirrors the primary build exactly -- G1/G2)
# --------------------------------------------------------------------------
def load():
    frames = [pd.read_parquet(f) for f in sorted(glob.glob(os.path.join(PHIL_DIR, "phils_*.parquet")))]
    df = pd.concat(frames, ignore_index=True)
    df = df[df.game_type == "R"].drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    df["game_date"] = pd.to_datetime(df.game_date)
    batting = (((df.home_team == "PHI") & (df.inning_topbot == "Bot"))
               | ((df.away_team == "PHI") & (df.inning_topbot == "Top")))
    return df[~batting].copy()          # pps = Phillies pitching


def wobaize(df):
    w = pd.read_csv(WOBA_CSV)
    df = df.drop(columns=[c for c in w.columns if c != "Season" and c in df.columns])
    return df.merge(w, left_on="game_year", right_on="Season", how="left")


# --------------------------------------------------------------------------
# PRIMITIVES (wOBA identical to the locked nresults line; recomputed here so
# this script is independently runnable -- verified equal in dp_uc38b_verify)
# --------------------------------------------------------------------------
def pa_rows(d):
    return d[~d.events.replace(np.nan, "NA").isin(["NA", "pickoff_1b"])]


def woba_panel(d, lvl):
    if isinstance(lvl, str):
        lvl = [lvl]
    p = pa_rows(d)
    out = p.groupby(lvl, as_index=False).agg(plate_apps=("events", "size"))
    for mask, col, nm in [(p.events == "walk", "wBB", "_wBB"),
                          (p.events == "hit_by_pitch", "wHBP", "_wHBP"),
                          (p.events == "single", "w1B", "_w1B"),
                          (p.events == "double", "w2B", "_w2B"),
                          (p.events == "triple", "w3B", "_w3B"),
                          (p.events == "home_run", "wHR", "_wHR")]:
        out = out.merge(p[mask].groupby(lvl, as_index=False).agg(**{nm: (col, "sum")}),
                        on=lvl, how="left")
    out = out.fillna(0)
    out["woba"] = (out._wBB + out._wHBP + out._w1B + out._w2B + out._w3B + out._wHR) / out.plate_apps
    out["walks"] = p[p.events == "walk"].groupby(lvl).size().reindex(
        pd.MultiIndex.from_frame(out[lvl]) if len(lvl) > 1 else out[lvl[0]]).fillna(0).values
    out["strikeouts"] = p[p.events.isin(["strikeout", "strikeout_double_play"])].groupby(lvl).size().reindex(
        pd.MultiIndex.from_frame(out[lvl]) if len(lvl) > 1 else out[lvl[0]]).fillna(0).values
    out["bb_rate"] = out.walks / out.plate_apps
    out["k_rate"] = out.strikeouts / out.plate_apps
    return out[lvl + ["plate_apps", "walks", "strikeouts", "woba", "bb_rate", "k_rate"]].round(4)


def approach_panel(d, lvl):
    """The composition/approach KPIs TR-1 tests for travel. Every one of these
    is a THROWN-PITCH property -- none of them requires knowing who called it."""
    if isinstance(lvl, str):
        lvl = [lvl]
    d = d.copy()
    d["grp"] = d.pitch_type.map(PITCH_GROUP)
    rows = []
    for key, g in d.groupby(lvl):
        key = key if isinstance(key, tuple) else (key,)
        typed = g.dropna(subset=["pitch_type"])
        sw, wh = g[g.description.isin(SWINGS)], g[g.description.isin(WHIFFS)]
        ooz = g[g.zone > 9]
        fp = g[g.pitch_number == 1]
        ts = g[g.strikes == 2].dropna(subset=["pitch_type"])
        beh = typed[typed.balls > typed.strikes]
        loc = g.dropna(subset=["zone"])
        rows.append(dict(zip(lvl, key)) | {
            "pitches": len(g),
            "games": int(g.game_pk.nunique()),
            "ch_share": float((typed.pitch_type == "CH").mean()) if len(typed) else np.nan,
            "kc_share": float((typed.pitch_type == "KC").mean()) if len(typed) else np.nan,
            "fb_share": float((typed.grp == "fastball").mean()) if len(typed) else np.nan,
            "offspeed_share": float((typed.grp == "offspeed").mean()) if len(typed) else np.nan,
            "breaking_share": float((typed.grp == "breaking").mean()) if len(typed) else np.nan,
            "fp_offspeed_share": float((fp.pitch_type.map(PITCH_GROUP) == "offspeed").mean()) if len(fp) else np.nan,
            "first_pitch_strike_rate": float(1 - (fp.type == "B").mean()) if len(fp) else np.nan,
            "two_strike_fb_rate": float((ts.grp == "fastball").mean()) if len(ts) else np.nan,
            "two_strike_ch_rate": float((ts.pitch_type == "CH").mean()) if len(ts) else np.nan,
            "behind_ch_rate": float((beh.pitch_type == "CH").mean()) if len(beh) else np.nan,
            "in_zone_rate": float((loc.zone <= 9).mean()) if len(loc) else np.nan,
            "whiff_rate": float(len(wh) / len(sw)) if len(sw) else np.nan,
            "chase_rate": float(ooz.description.isin(SWINGS).mean()) if len(ooz) else np.nan,
        })
    return pd.DataFrame(rows).round(4)


def main():
    if PHIL_DIR is None or WOBA_CSV is None:
        print("FATAL: data plane or wOBA constants not found. Set MLB_DATA_ROOT.")
        sys.exit(2)
    print("=" * 78)
    print("dp_uc38b · uc-pps-027 addendum · travel test + controls")
    print("=" * 78)

    pps = load()
    n = pps[pps.pitcher == NOLA].copy()
    n = wobaize(n)
    n["catcher"] = n.fielder_2.astype("Int64").map(CATCHERS)
    dq("entity_lock", "PASS", f"pitcher==605400; {n.pitcher.nunique()} id(s); {len(n):,} pitches")
    n26 = n[n.game_year == CURRENT_YEAR].copy()
    n26["era"] = np.where(n26.game_date >= pd.Timestamp(BREAKPOINT), "since", "before")
    n26["stubbs_stratum"] = np.where(n26.catcher == "Stubbs, Garrett", "stubbs", "non_stubbs")
    dq("freshness", str(n.game_date.max().date()),
       f"T-{(pd.Timestamp(GAME_DAY) - n.game_date.max()).days} vs game day {GAME_DAY}")

    # ---- monthly + per-start mix -----------------------------------------
    n26["month"] = n26.game_date.dt.strftime("%Y-%m")
    monthly = approach_panel(n26, ["month"]).sort_values("month")
    monthly.to_csv(os.path.join(OUT, "dp_uc38b_monthly_approach_2026.csv"), index=False)

    mm = (n26.dropna(subset=["pitch_type"])
          .groupby(["month", "pitch_type"], as_index=False).agg(n=("des", "size")))
    mtot = n26.dropna(subset=["pitch_type"]).groupby("month", as_index=False).agg(month_pitches=("des", "size"))
    mm = mm.merge(mtot, on="month", how="left")
    mm["share"] = (mm.n / mm.month_pitches).round(4)
    mm.sort_values(["month", "pitch_type"]).to_csv(
        os.path.join(OUT, "dp_uc38b_monthly_pitch_type_mix.csv"), index=False)

    per_start = approach_panel(n26, ["game_date", "catcher"]).sort_values("game_date")
    per_start = per_start.merge(woba_panel(n26, ["game_date"]), on="game_date", how="left")
    per_start.to_csv(os.path.join(OUT, "dp_uc38b_per_start_approach_2026.csv"), index=False)

    # ---- TR-1 adjustment-travel test -------------------------------------
    strat = approach_panel(n26, ["stubbs_stratum", "era"])
    metrics = ["ch_share", "kc_share", "fb_share", "offspeed_share", "fp_offspeed_share",
               "first_pitch_strike_rate", "two_strike_fb_rate", "two_strike_ch_rate",
               "behind_ch_rate", "in_zone_rate", "whiff_rate", "chase_rate"]
    piv = strat.pivot_table(index="stubbs_stratum", columns="era", values=metrics)
    rows = []
    for m in metrics:
        d_s = piv[(m, "since")]["stubbs"] - piv[(m, "before")]["stubbs"]
        d_n = piv[(m, "since")]["non_stubbs"] - piv[(m, "before")]["non_stubbs"]
        same = (np.sign(d_s) == np.sign(d_n)) and abs(d_n) > 0.01
        rows.append(dict(
            metric=m,
            stubbs_before=piv[(m, "before")]["stubbs"], stubbs_since=piv[(m, "since")]["stubbs"],
            stubbs_delta=d_s,
            non_stubbs_before=piv[(m, "before")]["non_stubbs"],
            non_stubbs_since=piv[(m, "since")]["non_stubbs"], non_stubbs_delta=d_n,
            travels=bool(same),
            verdict=("pitcher-level (travels across catchers)" if same else
                     "battery-specific candidate (Stubbs stratum only)"),
            share_of_stubbs_delta_seen_in_non_stubbs=(d_n / d_s if d_s not in (0,) and abs(d_s) > 1e-9 else np.nan),
        ))
    travel = pd.DataFrame(rows).round(4)
    travel.to_csv(os.path.join(OUT, "dp_uc38b_travel_test.csv"), index=False)
    dq("TR-1_travel_test", f"{int(travel.travels.sum())}/{len(travel)} metrics travel",
       "G7: a delta seen in only one stratum is a hypothesis, not a finding")

    strat_n = n26.groupby(["stubbs_stratum", "era"], as_index=False).agg(
        pitches=("des", "size"), starts=("game_pk", "nunique"))
    strat_n.to_csv(os.path.join(OUT, "dp_uc38b_travel_test_exposure.csv"), index=False)

    # ---- TR-2 breakpoint sensitivity -------------------------------------
    scan = []
    for bp in BREAKPOINT_SCAN:
        d = n26.copy()
        d["era"] = np.where(d.game_date >= pd.Timestamp(bp), "since", "before")
        a = approach_panel(d, ["era"]).set_index("era")
        if not {"before", "since"}.issubset(a.index):
            continue
        scan.append(dict(breakpoint=bp,
                         starts_since=int(d[d.era == "since"].game_pk.nunique()),
                         ch_before=a.loc["before", "ch_share"], ch_since=a.loc["since", "ch_share"],
                         ch_delta=a.loc["since", "ch_share"] - a.loc["before", "ch_share"],
                         behind_ch_delta=a.loc["since", "behind_ch_rate"] - a.loc["before", "behind_ch_rate"],
                         two_strike_fb_delta=a.loc["since", "two_strike_fb_rate"] - a.loc["before", "two_strike_fb_rate"]))
    scan = pd.DataFrame(scan).round(4)
    scan.to_csv(os.path.join(OUT, "dp_uc38b_breakpoint_scan.csv"), index=False)
    dq("TR-2_breakpoint_scan", f"{len(scan)} boundaries scanned",
       f"ch_delta sign stable: {bool((np.sign(scan.ch_delta) == np.sign(scan.ch_delta.iloc[0])).all())}")

    # ---- OC-1 opponent-quality control -----------------------------------
    p26 = wobaize(pps[pps.game_year == CURRENT_YEAR].copy())
    p26["opponent"] = np.where(p26.home_team == "PHI", p26.away_team, p26.home_team)
    nola26 = p26[p26.pitcher == NOLA]
    staff26 = p26[p26.pitcher != NOLA]
    a = woba_panel(nola26, ["opponent"])[["opponent", "plate_apps", "woba"]].rename(
        columns={"plate_apps": "nola_pa", "woba": "nola_woba"})
    b = woba_panel(staff26, ["opponent"])[["opponent", "plate_apps", "woba"]].rename(
        columns={"plate_apps": "staff_pa", "woba": "staff_woba"})
    oc = a.merge(b, on="opponent", how="left")
    oc["nola_minus_staff"] = (oc.nola_woba - oc.staff_woba).round(4)
    oc.to_csv(os.path.join(OUT, "dp_uc38b_opponent_control.csv"), index=False)

    gm = n26.groupby("game_pk", as_index=False).agg(
        game_date=("game_date", "min"), home=("home_team", "first"),
        away=("away_team", "first"))
    gm["opponent"] = np.where(gm.home == "PHI", gm.away, gm.home)
    modal = (n26.groupby(["game_pk", "catcher"], as_index=False).agg(k=("des", "size"))
             .sort_values("k", ascending=False).drop_duplicates("game_pk"))
    gm = gm.merge(modal[["game_pk", "catcher"]], on="game_pk").merge(
        oc[["opponent", "staff_woba", "nola_woba"]], on="opponent", how="left")
    diff = gm.groupby("catcher", as_index=False).agg(
        starts=("game_pk", "size"),
        mean_opp_difficulty=("staff_woba", "mean"),
        opponents=("opponent", lambda s: ",".join(sorted(s))))
    diff.to_csv(os.path.join(OUT, "dp_uc38b_catcher_opponent_difficulty.csv"), index=False)
    dq("OC-1_opponent_control", "COMPUTED",
       "mean rest-of-staff wOBA vs each catcher's opponent slate; higher = harder slate")

    # ---- LH-1 left-handed panel (closes uc-pps-021) -----------------------
    lh = []
    for stand in ["L", "R"]:
        d = n26[n26.stand == stand]
        w = woba_panel(d, ["catcher", "era"])
        ap = approach_panel(d, ["catcher", "era"])
        m = w.merge(ap, on=["catcher", "era"], how="outer")
        m.insert(0, "stand", stand)
        lh.append(m)
    lh = pd.concat(lh, ignore_index=True)
    lh.to_csv(os.path.join(OUT, "dp_uc38b_handedness_panel.csv"), index=False)

    lh_era = []
    for stand in ["L", "R"]:
        d = n26[n26.stand == stand]
        m = woba_panel(d, ["era"]).merge(approach_panel(d, ["era"]), on="era")
        m.insert(0, "stand", stand)
        lh_era.append(m)
    lh_era = pd.concat(lh_era, ignore_index=True)
    lh_era.to_csv(os.path.join(OUT, "dp_uc38b_handedness_era.csv"), index=False)

    # ---- CH-1 changeup performance panel ---------------------------------
    ch_rows = []
    for (era, stand), g in n26[n26.pitch_type == "CH"].groupby(["era", "stand"]):
        sw, wh = g[g.description.isin(SWINGS)], g[g.description.isin(WHIFFS)]
        ooz = g[g.zone > 9]
        bip = g[g.type == "X"]
        ch_rows.append(dict(era=era, stand=stand, changeups=len(g),
                            velo=g.release_speed.mean(),
                            zone_rate=(g.zone <= 9).mean(),
                            swings=len(sw), whiffs=len(wh),
                            whiff_rate=len(wh) / len(sw) if len(sw) else np.nan,
                            chase_rate=ooz.description.isin(SWINGS).mean() if len(ooz) else np.nan,
                            bip=len(bip),
                            xwobacon=bip.estimated_woba_using_speedangle.mean() if len(bip) else np.nan))
    ch = pd.DataFrame(ch_rows).round(4)
    ch.to_csv(os.path.join(OUT, "dp_uc38b_changeup_panel.csv"), index=False)

    ch_season = n.assign(is_ch=(n.pitch_type == "CH").astype(float)).groupby(
        "game_year", as_index=False).agg(pitches=("is_ch", "size"), ch_share=("is_ch", "mean")).round(4)
    ch_season.to_csv(os.path.join(OUT, "dp_uc38b_changeup_by_season_career.csv"), index=False)

    # ---- two-strike mix by catcher x era ---------------------------------
    ts = n26[(n26.strikes == 2)].dropna(subset=["pitch_type"])
    ts_mix = (ts.groupby(["catcher", "era", "pitch_type"], as_index=False).agg(n=("des", "size")))
    tot = ts.groupby(["catcher", "era"], as_index=False).agg(two_strike_pitches=("des", "size"))
    ts_mix = ts_mix.merge(tot, on=["catcher", "era"], how="left")
    ts_mix["share"] = (ts_mix.n / ts_mix.two_strike_pitches).round(4)
    ts_mix.to_csv(os.path.join(OUT, "dp_uc38b_two_strike_mix.csv"), index=False)

    # ---- count-state changeup --------------------------------------------
    d = n26.dropna(subset=["pitch_type"]).copy()
    d["count_state"] = np.where(d.strikes > d.balls, "ahead",
                                np.where(d.balls > d.strikes, "behind", "even"))
    cs = d.groupby(["era", "count_state"], as_index=False).agg(
        pitches=("des", "size"), changeups=("pitch_type", lambda s: int((s == "CH").sum())))
    cs["ch_share"] = (cs.changeups / cs.pitches).round(4)
    cs.to_csv(os.path.join(OUT, "dp_uc38b_count_state_changeup.csv"), index=False)

    # ---- uc-pps-021 tripwire ---------------------------------------------
    L = n26[n26.stand == "L"]
    def _slice(d):
        p = pa_rows(d)
        fp = d[d.pitch_number == 1]
        typed = d.dropna(subset=["pitch_type"])
        return dict(pa=len(p),
                    bb_rate=float((p.events == "walk").mean()) if len(p) else np.nan,
                    fps=float(1 - (fp.type == "B").mean()) if len(fp) else np.nan,
                    ch_share=float((typed.pitch_type == "CH").mean()) if len(typed) else np.nan,
                    woba=float(woba_panel(d, ["game_year"]).woba.iat[0]) if len(p) else np.nan)
    trip = pd.DataFrame([
        dict(indicator="LHH walk rate", source_uc="uc-pps-021 (2026-07-22)", then=0.107,
             before_bp=_slice(L[L.era == "before"])["bb_rate"], since_bp=_slice(L[L.era == "since"])["bb_rate"],
             direction_wanted="down"),
        dict(indicator="LHH first-pitch strike rate", source_uc="uc-pps-021", then=0.588,
             before_bp=_slice(L[L.era == "before"])["fps"], since_bp=_slice(L[L.era == "since"])["fps"],
             direction_wanted="up"),
        dict(indicator="Changeup usage vs LHH", source_uc="uc-pps-021", then=0.194,
             before_bp=_slice(L[L.era == "before"])["ch_share"], since_bp=_slice(L[L.era == "since"])["ch_share"],
             direction_wanted="up"),
        dict(indicator="LHH wOBA allowed", source_uc="uc-pps-021", then=np.nan,
             before_bp=_slice(L[L.era == "before"])["woba"], since_bp=_slice(L[L.era == "since"])["woba"],
             direction_wanted="down"),
    ]).round(4)
    trip.to_csv(os.path.join(OUT, "dp_uc38b_uc_pps_021_tripwire.csv"), index=False)

    # ---- era panel by catcher (the headline table) ------------------------
    era_cat = woba_panel(n26, ["catcher", "era"]).merge(
        approach_panel(n26, ["catcher", "era"]), on=["catcher", "era"], how="outer")
    era_cat.to_csv(os.path.join(OUT, "dp_uc38b_era_by_catcher.csv"), index=False)

    era_all = woba_panel(n26, ["era"]).merge(approach_panel(n26, ["era"]), on="era")
    era_all.to_csv(os.path.join(OUT, "dp_uc38b_era_overall.csv"), index=False)

    pd.DataFrame(DQ).to_csv(os.path.join(OUT, "dp_uc38b_dq_scorecard.csv"), index=False)
    head = dict(breakpoint=BREAKPOINT, game_day=GAME_DAY,
                as_of=str(n.game_date.max().date()),
                metrics_that_travel=int(travel.travels.sum()), metrics_tested=len(travel),
                stubbs_2026_starts=int(n26[n26.catcher == "Stubbs, Garrett"].game_pk.nunique()),
                attribution_constraint="pitch-call attribution NOT OBSERVABLE (G4)")
    with open(os.path.join(OUT, "dp_uc38b_headlines.json"), "w") as fh:
        json.dump(head, fh, indent=2, default=str)

    print("\n" + "=" * 78)
    print(f"DONE · addendum receipts written to ./out · "
          f"{len([d for d in DQ if d['severity']=='FAIL'])} FAIL")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
