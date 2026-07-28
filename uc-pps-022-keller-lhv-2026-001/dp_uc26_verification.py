"""
============================================================================
INDEPENDENT VERIFICATION HARNESS — UC #27 (uc-pps-022 / dp_uc26)
============================================================================
Convention established in UC#24 and carried forward.

PURPOSE: recompute every number the reader report publishes, by a DIFFERENT
code path than the build script used, and reconcile. The build script uses the
locked KPI kernel (groupby/merge chains inherited from dp_uc8). This harness
uses direct boolean masks and scalar arithmetic. Agreement between two
independent constructions is evidence; agreement between a function and itself
is not.

WHAT THIS DOES NOT DO: it does not re-read the build script's CSVs and check
they equal themselves. It recomputes from the parquet and compares to the CSVs.

Run:  python dp_uc26_verification.py
Exit: non-zero if any BLOCKING check fails.
============================================================================
"""
from __future__ import annotations
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out")
KELLER = 662144
BRAD_KELLER = 641745
TOL = 0.0015          # rounding tolerance: receipts are rounded to 3 dp

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "opponents"),
    "/sessions/zen-keen-goldberg/mnt/MLB/data/opponents",
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\opponents",
]
OPP_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
_WOBA = [os.path.join(HERE, "wOBA and FIP Constants.csv"),
         "/sessions/zen-keen-goldberg/mnt/MLB/wOBA and FIP Constants.csv",
         r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv"]
WOBA_CSV = next((p for p in _WOBA if p and os.path.isfile(p)), None)

SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]

LEDGER = []


def check(name, observed, expected, severity="blocking", note=""):
    if expected is None or (isinstance(expected, float) and np.isnan(expected)):
        ok = False
    elif isinstance(observed, (int, np.integer)) and isinstance(expected, (int, np.integer)):
        ok = observed == expected
    else:
        ok = abs(float(observed) - float(expected)) <= TOL
    LEDGER.append(dict(check=name, recomputed=observed, receipt=expected,
                       delta=(None if not isinstance(observed, (int, float, np.number))
                              else round(float(observed) - float(expected), 5)),
                       result="PASS" if ok else "FAIL", severity=severity, note=note))
    return ok


def main():
    print("=" * 78)
    print("dp_uc26 INDEPENDENT VERIFICATION")
    print("=" * 78)
    if OPP_DIR is None:
        print("FATAL: data layer not reachable. Verification cannot run.")
        sys.exit(2)

    # ---------- reload from source, second path ----------
    raw = pd.read_parquet(os.path.join(OPP_DIR, "lhvp26.parquet"))
    d = raw[raw.game_type == "R"].drop_duplicates(["game_pk", "at_bat_number", "pitch_number"]).copy()
    d["game_date"] = pd.to_datetime(d.game_date)
    k = d[d.pitcher == KELLER].copy()
    base = d[d.pitcher != KELLER].copy()
    if WOBA_CSV:
        w = pd.read_csv(WOBA_CSV); wr = w[w.Season == 2026].iloc[0]
    else:
        wr = None

    R = lambda n: pd.read_csv(os.path.join(OUT_DIR, f"dp_uc26_{n}.csv"))
    head = R("results_headline"); hk = head[head.who == "Keller"].iloc[0]
    hb = head[head.who != "Keller"].iloc[0]
    pk = R("process_kpis"); pkk = pk[pk.who == "Keller"].iloc[0]
    pkb = pk[pk.who != "Keller"].iloc[0]

    # ================= A. ENTITY LOCK =================
    check("A1 entity_lock_single_pitcher", int(k.pitcher.nunique()), 1)
    check("A2 brad_keller_absent", int(BRAD_KELLER in k.pitcher.unique()), 0,
          note=f"name-filter would add {len(d[d.pitcher==BRAD_KELLER])} rows")
    check("A3 single_player_name", int(k.player_name.nunique()), 1)
    check("A4 no_duplicate_pitches",
          int(k.duplicated(["game_pk", "at_bat_number", "pitch_number"]).sum()), 0)
    check("A5 regular_season_only", int((k.game_type != "R").sum()), 0)

    # ================= B. VOLUMES =================
    check("B1 pitches", int(len(k)), int(hk.pitches))
    check("B2 plate_appearances", int(k.events.notna().sum()), int(hk.plate_apps))
    check("B3 balls_in_play", int((k.type == "X").sum()), int(hk.bip))
    check("B4 games", int(k.game_pk.nunique()), int(hk.games))
    check("B5 baseline_pitches", int(len(base)), int(hb.pitches))
    check("B6 baseline_PA", int(base.events.notna().sum()), int(hb.plate_apps))

    # ================= C. RESULTS (scalar arithmetic, no groupby) =================
    ev = k.events
    hits = int(ev.isin(["single", "double", "triple", "home_run"]).sum())
    s1 = int((ev == "single").sum()); s2 = int((ev == "double").sum())
    s3 = int((ev == "triple").sum()); hr = int((ev == "home_run").sum())
    bb = int((ev == "walk").sum()); hbp = int((ev == "hit_by_pitch").sum())
    ks = int(ev.isin(["strikeout", "strikeout_double_play"]).sum())
    pa = int(ev.notna().sum())
    ab = int((~ev.replace(np.nan, "NA").isin(
        ["NA", "pickoff_1b", "walk", "intent_walk", "hit_by_pitch", "sac_fly", "sac_bunt"])).sum())
    check("C1 hits", hits, int(hk.hits))
    check("C2 home_runs", hr, int(hk.hrs))
    check("C3 walks", bb, int(hk.walks))
    check("C4 strikeouts", ks, int(hk.strikeouts))
    check("C5 batting_average", round(hits / ab, 3), float(hk.ba))
    check("C6 obp", round((hits + bb + hbp) / pa, 3), float(hk.obp))
    check("C7 slg", round((s1 + 2 * s2 + 3 * s3 + 4 * hr) / ab, 3), float(hk.slg))
    check("C8 k_rate", round(ks / pa, 3), float(hk.krate))
    check("C9 bb_rate", round(bb / pa, 3), float(hk.bbrate))
    if wr is not None:
        woba = (bb * wr.wBB + hbp * wr.wHBP + s1 * wr.w1B + s2 * wr.w2B
                + s3 * wr.w3B + hr * wr.wHR) / pa
        check("C10 woba_from_raw_weights", round(woba, 3), float(hk.woba),
              note="recomputed from FanGraphs 2026 constants, not from joined columns")
    bip = k[k.type == "X"]
    check("C11 xwobacon_bip_only", round(bip.estimated_woba_using_speedangle.mean(), 3),
          float(hk.xwobacon), note="UC#26 grain fix: mean over type=='X' only")
    check("C12 xwobacon_not_pitch_level",
          int(abs(round(k.estimated_woba_using_speedangle.mean(), 3) - float(hk.xwobacon)) > TOL), 1,
          note="asserts the pitch-level mean DIFFERS from published xwOBAcon — the fix is live")

    # ================= D. PROCESS KPIs =================
    sw = int(k.description.isin(SWINGS).sum()); wh = int(k.description.isin(WHIFFS).sum())
    check("D1 whiff_rate", round(wh / sw, 3), float(pkk.whiff_rate))
    check("D2 swstr_rate", round(wh / len(k), 3), float(pkk.swstr_rate))
    ooz = int((k.zone > 9).sum()); ch = int(((k.zone > 9) & k.description.isin(SWINGS)).sum())
    check("D3 chase_rate", round(ch / ooz, 3), float(pkk.chase_rate))
    check("D4 in_zone_rate", round((len(k) - ooz) / len(k), 3), float(pkk.in_zone_rate))
    fp = k[k.pitch_number == 1]
    check("D5 first_pitch_strike_rate", round((fp.type != "B").sum() / len(fp), 3),
          float(pkk.first_pitch_strike_rate))
    check("D6 putaway_rate", round(ks / int((k.strikes == 2).sum()), 3), float(pkk.putaway_rate))
    check("D7 hard_hit_rate", round((bip.launch_speed >= 95).sum() / len(bip), 3),
          float(pkk.hard_hit_rate))
    check("D8 gb_rate", round((bip.bb_type == "ground_ball").sum() / len(bip), 3), float(pkk.gb_rate))
    swb = int(base.description.isin(SWINGS).sum()); whb = int(base.description.isin(WHIFFS).sum())
    check("D9 baseline_whiff_rate", round(whb / swb, 3), float(pkb.whiff_rate))
    bbip = base[base.type == "X"]
    check("D10 baseline_hard_hit", round((bbip.launch_speed >= 95).sum() / len(bbip), 3),
          float(pkb.hard_hit_rate))
    check("D11 baseline_xwobacon", round(bbip.estimated_woba_using_speedangle.mean(), 3),
          float(hb.xwobacon))

    # ================= E. SPLITS SUM TO WHOLE =================
    bs = R("by_stand"); bsk = bs[bs.who == "Keller"]
    check("E1 stand_PA_sums_to_total", int(bsk.plate_apps.sum()), pa)
    gl = R("game_lines")
    check("E2 start_BF_sums_to_total", int(gl.bf.sum()), pa)
    check("E3 start_count", int(len(gl)), 8)
    ars = R("arsenal")
    check("E4 arsenal_pitches_sums_to_total", int(ars.n.sum()), len(k))
    check("E5 arsenal_bip_sums_to_total", int(ars.bips.sum()), int(len(bip)))
    tto = R("tto")
    check("E6 tto_PA_sums_to_total", int(tto.plate_apps.sum()), pa)
    rec = R("recency_split")
    check("E7 recency_PA_sums_to_total", int(rec.plate_apps.sum()), pa)
    check("E8 recency_pitches_sums_to_total", int(rec.pitches.sum()), len(k))
    check("E9 HR_receipt_count", int(len(R("home_runs"))), hr)
    check("E10 innings_reconcile", round(gl.ip.sum(), 1), round(float(hk.ip_computed), 1),
          note="per-start IP vs season IP")
    _outs = int(k.events.map({"field_out": 1, "strikeout": 1, "force_out": 1, "sac_fly": 1,
                              "sac_bunt": 1, "fielders_choice_out": 1, "fielders_choice": 1,
                              "grounded_into_double_play": 2, "double_play": 2,
                              "strikeout_double_play": 2, "sac_fly_double_play": 2,
                              "triple_play": 3, "other_out": 1}).fillna(0).sum())
    check("E11 outs_recorded", _outs, int(hk.outs_recorded))
    check("E12 ip_baseball_notation", f"{_outs//3}.{_outs%3}" == str(hk.ip_baseball), True,
          note="ip_baseball must equal outs//3 . outs%3 — guards the 36.2-vs-36.7 confusion")
    check("E13 ip_decimal_vs_baseball_consistent",
          int(abs(_outs / 3 - float(hk.ip_computed)) < 0.05), 1,
          note="the two representations must describe the same quantity")

    # ================= F. THE MECHANISM (report's central claim) =================
    dates = sorted(k.game_date.unique())
    early = k[k.game_date.isin(dates[:4])]; late = k[k.game_date.isin(dates[4:])]
    r_e = rec[rec.half.str.startswith("starts 1-4")].iloc[0]
    r_l = rec[rec.half.str.startswith("starts 5-8")].iloc[0]
    check("F1 early_bb_rate", round((early.events == "walk").sum() / early.events.notna().sum(), 3),
          float(r_e.bbrate))
    check("F2 late_bb_rate", round((late.events == "walk").sum() / late.events.notna().sum(), 3),
          float(r_l.bbrate))
    for lab, seg, row in [("early", early, r_e), ("late", late, r_l)]:
        b = seg[seg.type == "X"]
        check(f"F3_{lab}_hard_hit", round((b.launch_speed >= 95).mean(), 3), float(row.hard_hit_rate))
        check(f"F4_{lab}_xwobacon", round(b.estimated_woba_using_speedangle.mean(), 3),
              float(row.xwobacon))
        o = int((seg.zone > 9).sum())
        check(f"F5_{lab}_chase", round(((seg.zone > 9) & seg.description.isin(SWINGS)).sum() / o, 3),
              float(row.chase_rate))
    ru = R("recency_usage")
    for lab, seg, hf in [("early", early, "starts 1-4"), ("late", late, "starts 5-8")]:
        row = ru[ru.half.str.startswith(hf)].iloc[0]
        check(f"F6_{lab}_4seam_usage",
              round((seg.pitch_name == "4-Seam Fastball").mean(), 3), float(row["4-Seam Fastball"]))
        check(f"F7_{lab}_sinker_usage",
              round((seg.pitch_name == "Sinker").mean(), 3), float(row["Sinker"]))
    check("F8 mechanism_direction_4seam",
          int(round((early.pitch_name == "4-Seam Fastball").mean(), 3)
              > round((late.pitch_name == "4-Seam Fastball").mean(), 3)), 1,
          note="four-seam usage must fall early->late for the report's claim to hold")
    check("F9 mechanism_direction_sinker",
          int(round((early.pitch_name == "Sinker").mean(), 3)
              < round((late.pitch_name == "Sinker").mean(), 3)), 1,
          note="sinker usage must rise early->late")

    # ================= G. HANDEDNESS CLAIM =================
    L = k[k.stand == "L"]; Rt = k[k.stand == "R"]
    check("G1 all_HR_vs_LHB", int((k[k.events == "home_run"].stand == "L").all()), 1,
          note="report claims all 5 HR came against left-handed hitters")
    check("G2 LHB_PA", int(L.events.notna().sum()), int(bsk[bsk.stand == "L"].plate_apps.iloc[0]))
    check("G3 RHB_PA", int(Rt.events.notna().sum()), int(bsk[bsk.stand == "R"].plate_apps.iloc[0]))
    pbs = R("process_by_stand"); pbsk = pbs[pbs.who == "Keller"]
    for s, seg in [("L", L), ("R", Rt)]:
        row = pbsk[pbsk.stand == s].iloc[0]
        b = seg[seg.type == "X"]
        check(f"G4_{s}_gb_rate", round((b.bb_type == "ground_ball").mean(), 3), float(row.gb_rate))
        check(f"G5_{s}_whiff", round(seg.description.isin(WHIFFS).sum()
                                     / seg.description.isin(SWINGS).sum(), 3), float(row.whiff_rate))

    # ================= H. GAMEPLAN GRID =================
    ts = R("two_strike")
    two = k[k.strikes == 2]
    for _, row in ts.iterrows():
        seg = two[(two.stand == row.stand) & (two.pitch_name == row.pitch_name)]
        check(f"H1 2K_{row.stand}_{row.pitch_name[:6]}_n", int(len(seg)), int(row.n), "warning")
    lff = two[(two.stand == "L") & (two.pitch_name == "4-Seam Fastball")]
    check("H2 2K_LHB_4seam_share", round(len(lff) / len(two[two.stand == "L"]), 3),
          float(ts[(ts.stand == "L") & (ts.pitch_name == "4-Seam Fastball")].usage_within_stand.iloc[0]),
          note="report's central game-calling claim")
    fpr = R("first_pitch")
    for _, row in fpr.iterrows():
        seg = fp[(fp.stand == row.stand) & (fp.pitch_name == row.pitch_name)]
        check(f"H3 FP_{row.stand}_{row.pitch_name[:6]}_strike_rate",
              round((seg.type != "B").sum() / len(seg), 3), float(row.strike_rate), "warning")

    # ================= I. VELOCITY DECAY =================
    vi = R("velo_by_inning")
    ff = k[k.pitch_name == "4-Seam Fastball"]
    for _, row in vi.iterrows():
        seg = ff[ff.inning == row.inning]
        check(f"I1 ff_velo_inn{int(row.inning)}", round(seg.release_speed.mean(), 2),
              float(row.ff_velo), "warning")
    check("I2 velo_decay_monotonic",
          int(all(np.diff(vi.sort_values("inning").ff_velo.values) < 0)), 1,
          note="report claims monotonic decay innings 1-6")

    # ================= J. PROVISIONAL SR-M1 =================
    srv = R("sr_m1_variants"); srk = srv[srv.who == "Keller"].iloc[0]
    srp = R("sr_m1_provisional"); srpk = srp[srp.who == "Keller"].iloc[0]
    check("J1 srm1_A_matches_dpo_function", float(srk.rate_A_as_written),
          float(srpk.success_rate),
          note="harness variant A must reproduce the DPO's supplied function exactly")
    # third, fully manual path
    manual = []
    for (_, _), g in k.groupby(["game_pk", "at_bat_number"]):
        g = g.sort_values("pitch_number")
        mx = g[g.pitch_number < 4].strikes.max()
        gb3 = ((g.pitch_number < 4) & (g.type == "X") & (g.bb_type == "ground_ball")).any()
        manual.append(1 if (mx == 2 or gb3) else 0)
    check("J2 srm1_A_third_independent_path", round(float(np.mean(manual)), 3),
          float(srpk.success_rate))
    check("J3 srm1_denominator_is_PA", int(len(manual)), pa)
    check("J4 srm1_intent_gap_exists",
          int(abs(float(srk.rate_C_two_strike_by_p3) - float(srk.rate_A_as_written)) > 0.10), 1,
          note="asserts the intent-vs-implementation gap the ratification packet is built on")
    check("J5 srm1_status_column_present",
          int("STATUS" in srp.columns and srp.STATUS.str.contains("PROVISIONAL").all()), 1,
          note="DQ-16: provisional banner must travel with the data")

    # ================= K. FIGURE / RECEIPT PARITY =================
    for f in ["fig1_arsenal", "fig2_recency", "fig3_location", "fig4_gameplan"]:
        check(f"K1 {f}_exists", int(os.path.isfile(os.path.join(OUT_DIR, f"dp_uc26_{f}.png"))), 1)
    dq = R("dq_scorecard")
    check("K2 no_failed_dq_checks", int((dq.result == "FAIL").sum()), 0)
    check("K3 dq_blocking_all_pass",
          int((dq[dq.severity == "blocking"].result != "PASS").sum()), 0)

    # ---------- report ----------
    led = pd.DataFrame(LEDGER)
    led.to_csv(os.path.join(OUT_DIR, "dp_uc26_verification_ledger.csv"), index=False)
    fails = led[led.result == "FAIL"]
    blocking = fails[fails.severity == "blocking"]
    print(f"\nchecks run      : {len(led)}")
    print(f"passed          : {(led.result=='PASS').sum()}")
    print(f"failed          : {len(fails)}  (blocking: {len(blocking)})")
    if len(fails):
        print("\nFAILURES:")
        print(fails.to_string(index=False))
    print(f"\nledger -> out/dp_uc26_verification_ledger.csv")
    print("=" * 78)
    print("VERDICT:", "PASS — every published number reconciles" if len(blocking) == 0
          else "FAIL — blocking reconciliation errors, DO NOT PUBLISH")
    print("=" * 78)
    sys.exit(1 if len(blocking) else 0)


if __name__ == "__main__":
    main()
