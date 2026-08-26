"""
dp_uc38b_verification.py
==============================================================================
UC #38 · uc-pps-027 · INDEPENDENT VERIFICATION, second path

Two jobs:

  PATH 1 — THE DPO'S OWN SKELETON.
      The use case arrived with a working pandas skeleton: merge Nola's log
      against the Phillies batting frame to resolve `fielder_2` -> catcher
      name, group at [fielder_2, player_name, player_name_catcher], and
      compute a KPI panel. It was priced in the bid as an INDEPENDENT
      VERIFICATION PATH, not as the primary build. This module honours that
      literally: the skeleton is reimplemented as written (inner merge, DPO's
      level, DPO's KPI list) and its output is reconciled cell-by-cell against
      `dp_uc38_battery_career.csv`.

      Where the two disagree, the LOCKED implementation is authoritative and
      the delta is REPORTED, never silently reconciled (bid §6).

  PATH 2 — RECOMPUTE THE ADDENDUM CLAIMS FROM RAW PARQUET.
      Every number the report cites from `dp_uc38b_*` is recomputed here by a
      separate code path with no shared helper, and compared to the receipt.

  PATH 3 — THE REMAINING CITED RECEIPTS.
      Added after `dp_uc38_package_audit.py` flagged seven report receipts that
      no harness asserted. The audit is the reason this section exists; that is
      the audit working.

Exit code 1 if any check FAILs.
==============================================================================
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np
import pandas as pd

pd.set_option("display.width", 200)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

NOLA, STUBBS = 605400, 596117
BREAKPOINT = pd.Timestamp("2026-07-05")
TOL = 5e-4

_DATA = [os.environ.get("MLB_DATA_ROOT", ""), os.path.join(HERE, "data", "phillies"),
         r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies"]
PHIL_DIR = next((p for p in _DATA if p and os.path.isdir(p)), None)
_W = [os.environ.get("MLB_WOBA_CSV", ""),   # env override (run-2 portability fix)
      os.path.join(HERE, "wOBA and FIP Constants.csv"),
      r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv"]
WOBA_CSV = next((p for p in _W if os.path.isfile(p)), None)

RESULTS: list[dict] = []


def check(name, ok, detail=""):
    RESULTS.append(dict(check=name, result="PASS" if ok else "FAIL", detail=detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {detail}")
    return ok


def close(a, b, tol=TOL):
    if a is None or b is None:
        return False
    if (a != a) and (b != b):
        return True
    return abs(float(a) - float(b)) <= tol


# --------------------------------------------------------------------------
def load_raw():
    frames = [pd.read_parquet(f) for f in sorted(glob.glob(os.path.join(PHIL_DIR, "phils_*.parquet")))]
    df = pd.concat(frames, ignore_index=True)
    df = df[df.game_type == "R"].drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    df["game_date"] = pd.to_datetime(df.game_date)
    batting = (((df.home_team == "PHI") & (df.inning_topbot == "Bot"))
               | ((df.away_team == "PHI") & (df.inning_topbot == "Top")))
    return df[batting].copy(), df[~batting].copy()


# ==========================================================================
# PATH 1 — the DPO's skeleton, reimplemented as written
# ==========================================================================
SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]


def dpo_skeleton(pos, nola):
    """The carry-in code, as supplied, with only two changes: (a) the KPI
    helper functions are written out (the DPO's live in a notebook), and
    (b) `des` -> `description` where `des` is null on non-terminal rows.
    Neither changes a denominator."""
    catcher_names = (pos.groupby(["batter", "player_name"], as_index=False)
                     .agg(pitches=("des", "size")))
    df = nola.merge(catcher_names, left_on=["fielder_2"], right_on=["batter"],
                    suffixes=("", "_catcher"), how="inner")
    level = ["fielder_2", "player_name", "player_name_catcher"]

    def nres(lvl, d):
        pa = d[~d.events.replace(np.nan, "NA").isin(["NA", "pickoff_1b"])]
        ab = pa[~pa.events.isin(["walk", "intent_walk", "hit_by_pitch", "sac_fly", "sac_bunt"])]
        g = pa.groupby(lvl, as_index=False).agg(plate_apps=("events", "size"))
        g = g.merge(ab.groupby(lvl, as_index=False).agg(at_bats=("events", "size")), on=lvl, how="left")
        g = g.merge(d[d.type == "X"].groupby(lvl, as_index=False).agg(bip=("type", "size")), on=lvl, how="left")
        for ev, nm in [(["home_run", "single", "double", "triple"], "hits"), (["single"], "singles"),
                       (["double"], "doubles"), (["triple"], "triples"), (["home_run"], "hrs"),
                       (["walk"], "walks"), (["strikeout", "strikeout_double_play"], "strikeouts"),
                       (["hit_by_pitch"], "hbp")]:
            g = g.merge(pa[pa.events.isin(ev)].groupby(lvl, as_index=False).agg(**{nm: ("events", "size")}),
                        on=lvl, how="left")
        for ev, col, nm in [("walk", "wBB", "a"), ("hit_by_pitch", "wHBP", "b"), ("single", "w1B", "c"),
                            ("double", "w2B", "d"), ("triple", "w3B", "e"), ("home_run", "wHR", "f")]:
            g = g.merge(pa[pa.events == ev].groupby(lvl, as_index=False).agg(**{nm: (col, "sum")}),
                        on=lvl, how="left")
        g = g.fillna(0)
        g["ba"] = g.hits / g.at_bats
        g["obp"] = (g.hits + g.walks + g.hbp) / g.plate_apps
        g["slg"] = (g.singles + 2 * g.doubles + 3 * g.triples + 4 * g.hrs) / g.at_bats
        g["ops"] = g.obp + g.slg
        g["woba"] = (g.a + g.b + g.c + g.d + g.e + g.f) / g.plate_apps
        g["krate"] = g.strikeouts / g.plate_apps
        g["bbrate"] = g.walks / g.plate_apps
        g["hr_rate"] = g.hrs / g.plate_apps
        return g

    def chase(lvl, d):
        ooz = d[d.zone > 9]
        t = ooz.groupby(lvl, as_index=False).agg(ooz=("zone", "size"))
        c = ooz[ooz.description.isin(SWINGS)].groupby(lvl, as_index=False).agg(chases=("zone", "size"))
        m = t.merge(c, on=lvl, how="left").fillna(0)
        m["chase_rate"] = m.chases / m.ooz
        return m

    def whiff(lvl, d):
        s = d[d.description.isin(SWINGS)].groupby(lvl, as_index=False).agg(swings=("description", "size"))
        w = d[d.description.isin(WHIFFS)].groupby(lvl, as_index=False).agg(whiffs=("description", "size"))
        m = s.merge(w, on=lvl, how="left").fillna(0)
        m["whiff_rate"] = m.whiffs / m.swings
        return m

    def putaway(lvl, d):
        z = d[d.strikes == 2].groupby(lvl, as_index=False).agg(p2=("description", "size"))
        k = d[d.events.isin(["strikeout", "strikeout_double_play"])].groupby(
            lvl, as_index=False).agg(k=("events", "size"))
        m = z.merge(k, on=lvl, how="left").fillna(0)
        m["putaway_rate"] = m.k / m.p2
        return m

    def fps(lvl, d):
        fp = d[d.pitch_number == 1]
        t = fp.groupby(lvl, as_index=False).agg(fp=("type", "size"))
        b = fp[fp.type == "B"].groupby(lvl, as_index=False).agg(balls=("type", "size"))
        m = t.merge(b, on=lvl, how="left").fillna(0)
        m["first_pitch_strike_rate"] = (m.fp - m.balls) / m.fp
        return m

    z = (df.groupby(level, as_index=False)
         .agg(total_pitches=("description", "size"), uq_games=("game_pk", "nunique"))
         .sort_values("uq_games", ascending=False)
         .merge(nres(level, df), on=level, how="left")
         .merge(chase(level, df), on=level, how="left")
         .merge(whiff(level, df), on=level, how="left")
         .merge(putaway(level, df), on=level, how="left")
         .merge(fps(level, df), on=level, how="left"))
    return z


def path1(pos, nola):
    print("\nPATH 1 — the DPO's skeleton vs the locked build")
    sk = dpo_skeleton(pos, nola)
    locked = pd.read_csv(os.path.join(OUT, "dp_uc38_battery_career.csv"))
    check("skeleton resolves the same catcher set",
          set(sk.fielder_2.astype(int)) == set(locked.catcher_id.astype(int)),
          f"skeleton {len(sk)} rows / locked {len(locked)} rows")

    cols = ["total_pitches", "uq_games", "plate_apps", "ba", "obp", "slg", "ops", "woba",
            "krate", "bbrate", "hr_rate", "chase_rate", "whiff_rate", "putaway_rate",
            "first_pitch_strike_rate"]
    m = sk.merge(locked, left_on="fielder_2", right_on="catcher_id", suffixes=("_dpo", "_lock"))
    deltas = []
    for c in cols:
        a, b = m[f"{c}_dpo"], m[f"{c}_lock"]
        d = float(np.nanmax(np.abs(a.values - b.values)))
        deltas.append(dict(kpi=c, max_abs_delta=round(d, 6),
                           agrees=bool(d <= (0.5 if c in ("total_pitches", "uq_games", "plate_apps") else 1.1e-3))))
        check(f"skeleton == locked · {c}", deltas[-1]["agrees"], f"max |Δ| = {d:.6f}")
    pd.DataFrame(deltas).to_csv(os.path.join(OUT, "dp_uc38b_verify_dpo_skeleton.csv"), index=False)

    # the one place the two designs genuinely differ, reported not reconciled
    check("skeleton inner-merge does not drop a catcher",
          len(sk) == len(locked),
          "an INNER merge on the pos frame would drop any catcher who never batted for PHI")


# ==========================================================================
# PATH 2 — recompute the addendum from raw
# ==========================================================================
def path2(nola):
    print("\nPATH 2 — addendum receipts recomputed from raw parquet")
    n26 = nola[nola.game_year == 2026].copy()
    n26["era"] = np.where(n26.game_date >= BREAKPOINT, "since", "before")
    n26["strat"] = np.where(n26.fielder_2 == STUBBS, "stubbs", "non_stubbs")
    typed = n26.dropna(subset=["pitch_type"])

    tt = pd.read_csv(os.path.join(OUT, "dp_uc38b_travel_test.csv")).set_index("metric")

    # changeup share, both strata, both eras -- fully independent arithmetic
    for strat in ["stubbs", "non_stubbs"]:
        for era in ["before", "since"]:
            g = typed[(typed.strat == strat) & (typed.era == era)]
            mine = float((g.pitch_type == "CH").sum()) / len(g)
            theirs = tt.loc["ch_share", f"{strat}_{era}"]
            check(f"TR-1 ch_share · {strat} · {era}", close(mine, theirs),
                  f"raw {mine:.4f} vs receipt {theirs:.4f} (n={len(g)})")

    # two-strike fastball rate
    FB = {"FF", "SI", "FC"}
    for strat in ["stubbs", "non_stubbs"]:
        for era in ["before", "since"]:
            g = typed[(typed.strat == strat) & (typed.era == era) & (typed.strikes == 2)]
            mine = float(g.pitch_type.isin(FB).sum()) / len(g)
            theirs = tt.loc["two_strike_fb_rate", f"{strat}_{era}"]
            check(f"TR-1 two_strike_fb_rate · {strat} · {era}", close(mine, theirs),
                  f"raw {mine:.4f} vs receipt {theirs:.4f} (n={len(g)})")

    # changeup when behind
    for strat in ["stubbs", "non_stubbs"]:
        for era in ["before", "since"]:
            g = typed[(typed.strat == strat) & (typed.era == era) & (typed.balls > typed.strikes)]
            mine = float((g.pitch_type == "CH").sum()) / len(g)
            theirs = tt.loc["behind_ch_rate", f"{strat}_{era}"]
            check(f"TR-1 behind_ch_rate · {strat} · {era}", close(mine, theirs),
                  f"raw {mine:.4f} vs receipt {theirs:.4f} (n={len(g)})")

    check("TR-1 travel count matches the report's '10 of 12'",
          int(pd.read_csv(os.path.join(OUT, "dp_uc38b_travel_test.csv")).travels.sum()) == 10,
          "")

    # TR-2 sign stability
    scan = pd.read_csv(os.path.join(OUT, "dp_uc38b_breakpoint_scan.csv"))
    check("TR-2 ch_delta positive at every scanned breakpoint", bool((scan.ch_delta > 0).all()),
          f"range {scan.ch_delta.min():.4f}–{scan.ch_delta.max():.4f}")
    check("TR-2 two_strike_fb_delta negative at every scanned breakpoint",
          bool((scan.two_strike_fb_delta < 0).all()),
          f"range {scan.two_strike_fb_delta.min():.4f}–{scan.two_strike_fb_delta.max():.4f}")

    # OC-1 -- Stubbs's slate is not softer
    oc = pd.read_csv(os.path.join(OUT, "dp_uc38b_catcher_opponent_difficulty.csv")).set_index("catcher")
    check("OC-1 Stubbs slate harder than Realmuto's",
          oc.loc["Stubbs, Garrett", "mean_opp_difficulty"] > oc.loc["Realmuto, J.T.", "mean_opp_difficulty"],
          f"{oc.loc['Stubbs, Garrett','mean_opp_difficulty']:.4f} vs "
          f"{oc.loc['Realmuto, J.T.','mean_opp_difficulty']:.4f}")

    # LH-1 tripwire, recomputed
    L = n26[n26.stand == "L"]
    trip = pd.read_csv(os.path.join(OUT, "dp_uc38b_uc_pps_021_tripwire.csv")).set_index("indicator")
    for era in ["before", "since"]:
        d = L[L.era == era]
        p = d[~d.events.replace(np.nan, "NA").isin(["NA", "pickoff_1b"])]
        mine_bb = float((p.events == "walk").sum()) / len(p)
        check(f"LH-1 LHH walk rate · {era}", close(mine_bb, trip.loc["LHH walk rate", f"{era}_bp"]),
              f"raw {mine_bb:.4f} (PA={len(p)})")
        fp = d[d.pitch_number == 1]
        mine_fps = 1 - float((fp.type == "B").sum()) / len(fp)
        check(f"LH-1 LHH first-pitch strike rate · {era}",
              close(mine_fps, trip.loc["LHH first-pitch strike rate", f"{era}_bp"]),
              f"raw {mine_fps:.4f} (first pitches={len(fp)})")
        t2 = d.dropna(subset=["pitch_type"])
        mine_ch = float((t2.pitch_type == "CH").sum()) / len(t2)
        check(f"LH-1 changeup usage vs LHH · {era}",
              close(mine_ch, trip.loc["Changeup usage vs LHH", f"{era}_bp"]), f"raw {mine_ch:.4f}")

    # CH-1 whiff, recomputed
    ch = pd.read_csv(os.path.join(OUT, "dp_uc38b_changeup_panel.csv"))
    for era in ["before", "since"]:
        g = n26[(n26.pitch_type == "CH") & (n26.era == era) & (n26.stand == "L")]
        sw = g[g.description.isin(SWINGS)]
        mine = float(g.description.isin(WHIFFS).sum()) / len(sw)
        theirs = ch[(ch.era == era) & (ch.stand == "L")].whiff_rate.iat[0]
        check(f"CH-1 changeup whiff vs LHH · {era}", close(mine, theirs),
              f"raw {mine:.4f} vs receipt {theirs:.4f} (swings={len(sw)})")

    # exposure sanity -- guards the whole travel test
    ex = pd.read_csv(os.path.join(OUT, "dp_uc38b_travel_test_exposure.csv"))
    check("exposure · Stubbs 5 starts since breakpoint",
          int(ex[(ex.stubbs_stratum == "stubbs") & (ex.era == "since")].starts.iat[0]) == 5, "")
    check("exposure · non-Stubbs 4 starts since breakpoint",
          int(ex[(ex.stubbs_stratum == "non_stubbs") & (ex.era == "since")].starts.iat[0]) == 4,
          "the travel test rests on these four games -- stated, not hidden")


def path3(nola):
    """Every remaining receipt the report cites, recomputed from raw.
    Added after `dp_uc38_package_audit.py` flagged seven report receipts that no
    harness asserted -- the same class of gap the run-1 audit caught twice."""
    print("\nPATH 3 — the remaining cited receipts")
    n26 = nola[nola.game_year == 2026].copy()
    n26["era"] = np.where(n26.game_date >= BREAKPOINT, "since", "before")
    n26["month"] = n26.game_date.dt.strftime("%Y-%m")
    typed26 = n26.dropna(subset=["pitch_type"])
    FB = {"FF", "SI", "FC"}

    # 1 — career changeup share by season
    cs = pd.read_csv(os.path.join(OUT, "dp_uc38b_changeup_by_season_career.csv")).set_index("game_year")
    for yr in [2020, 2024, 2026]:
        g = nola[nola.game_year == yr]
        mine = float((g.pitch_type == "CH").sum()) / len(g)
        check(f"career CH share · {yr}", close(mine, cs.loc[yr, "ch_share"]),
              f"raw {mine:.4f} vs receipt {cs.loc[yr,'ch_share']:.4f}")

    # 2 — monthly approach + monthly pitch-type mix
    ma = pd.read_csv(os.path.join(OUT, "dp_uc38b_monthly_approach_2026.csv")).set_index("month")
    mm = pd.read_csv(os.path.join(OUT, "dp_uc38b_monthly_pitch_type_mix.csv"))
    for mo in ["2026-03", "2026-07", "2026-08"]:
        g = typed26[typed26.month == mo]
        mine = float((g.pitch_type == "CH").sum()) / len(g)
        check(f"monthly ch_share · {mo}", close(mine, ma.loc[mo, "ch_share"]), f"raw {mine:.4f}")
        row = mm[(mm.month == mo) & (mm.pitch_type == "KC")]
        mine_kc = float((g.pitch_type == "KC").sum()) / len(g)
        check(f"monthly KC share · {mo}", close(mine_kc, row.share.iat[0]), f"raw {mine_kc:.4f}")

    # 3 — per-start approach (the two-start knuckle-curve claim rests on this)
    ps = pd.read_csv(os.path.join(OUT, "dp_uc38b_per_start_approach_2026.csv"))
    ps["game_date"] = pd.to_datetime(ps.game_date)
    for d in ["2026-07-28", "2026-08-03", "2026-08-08", "2026-08-19"]:
        g = typed26[typed26.game_date == pd.Timestamp(d)]
        mine = float((g.pitch_type == "KC").sum()) / len(g)
        theirs = ps[ps.game_date == pd.Timestamp(d)].kc_share.iat[0]
        check(f"per-start kc_share · {d}", close(mine, theirs), f"raw {mine:.4f} vs receipt {theirs:.4f}")

    # 4 — era overall
    eo = pd.read_csv(os.path.join(OUT, "dp_uc38b_era_overall.csv")).set_index("era")
    for era in ["before", "since"]:
        d = n26[n26.era == era]
        p = d[~d.events.replace(np.nan, "NA").isin(["NA", "pickoff_1b"])]
        mine_k = float(p.events.isin(["strikeout", "strikeout_double_play"]).sum()) / len(p)
        check(f"era overall K rate · {era}", close(mine_k, eo.loc[era, "k_rate"]),
              f"raw {mine_k:.4f} (PA={len(p)})")
        sw = d[d.description.isin(SWINGS)]
        mine_w = float(d.description.isin(WHIFFS).sum()) / len(sw)
        check(f"era overall whiff rate · {era}", close(mine_w, eo.loc[era, "whiff_rate"]),
              f"raw {mine_w:.4f}")

    # 5 — handedness x era (the RHH bill-coming-due claim)
    he = pd.read_csv(os.path.join(OUT, "dp_uc38b_handedness_era.csv"))
    for stand in ["L", "R"]:
        for era in ["before", "since"]:
            d = n26[(n26.stand == stand) & (n26.era == era)]
            p = d[~d.events.replace(np.nan, "NA").isin(["NA", "pickoff_1b"])]
            mine = float((p.events == "walk").sum()) / len(p)
            theirs = he[(he.stand == stand) & (he.era == era)].bb_rate.iat[0]
            check(f"handedness bb_rate · {stand} · {era}", close(mine, theirs),
                  f"raw {mine:.4f} (PA={len(p)})")

    # 6 — two-strike mix by catcher x era
    tsm = pd.read_csv(os.path.join(OUT, "dp_uc38b_two_strike_mix.csv"))
    for era in ["before", "since"]:
        g = typed26[(typed26.strikes == 2) & (typed26.era == era) & (typed26.fielder_2 == STUBBS)]
        mine = float((g.pitch_type == "CH").sum()) / len(g)
        r = tsm[(tsm.catcher == "Stubbs, Garrett") & (tsm.era == era) & (tsm.pitch_type == "CH")]
        check(f"two-strike CH share · Stubbs · {era}", close(mine, r.share.iat[0]),
              f"raw {mine:.4f} vs receipt {r.share.iat[0]:.4f} (n={len(g)})")
        mine_fb = float(g.pitch_type.isin(FB).sum()) / len(g)
        rfb = tsm[(tsm.catcher == "Stubbs, Garrett") & (tsm.era == era) & (tsm.pitch_type.isin(FB))]
        check(f"two-strike FB share · Stubbs · {era}", close(mine_fb, float(rfb.share.sum())),
              f"raw {mine_fb:.4f}")


def main():
    if PHIL_DIR is None or WOBA_CSV is None:
        print("FATAL: data plane not reachable. Set MLB_DATA_ROOT.")
        sys.exit(2)
    print("=" * 78)
    print("dp_uc38b_verification · uc-pps-027 · independent second path")
    print("=" * 78)
    pos, pps = load_raw()
    nola = pps[pps.pitcher == NOLA].copy()
    w = pd.read_csv(WOBA_CSV)
    nola = nola.drop(columns=[c for c in w.columns if c != "Season" and c in nola.columns])
    nola = nola.merge(w, left_on="game_year", right_on="Season", how="left")
    check("entity lock", nola.pitcher.nunique() == 1 and int(nola.pitcher.iat[0]) == NOLA,
          f"{len(nola):,} pitches, {nola.game_pk.nunique()} starts")

    path1(pos, nola)
    path2(nola)
    path3(nola)

    res = pd.DataFrame(RESULTS)
    res.to_csv(os.path.join(OUT, "dp_uc38b_verification_results.csv"), index=False)
    n_fail = int((res.result == "FAIL").sum())
    print("\n" + "=" * 78)
    print(f"{int((res.result=='PASS').sum())} PASS · {n_fail} FAIL")
    print("=" * 78)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
