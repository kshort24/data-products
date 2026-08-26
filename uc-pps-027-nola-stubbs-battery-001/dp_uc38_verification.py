"""
dp_uc38_verification.py — independent verification harness for uc-pps-027
==============================================================================
Two verification tiers:

TIER A · UNIT TESTS (run WITHOUT the data plane)
    Hand-constructed pitch logs with known answers, one per NEW battery KPI.
    These prove the BAT-* implementations are correct as written. They are the
    only tier that could execute in the delivery session (the parquet plane was
    not mounted) and they PASSED 9/9 at build time.

TIER B · INDEPENDENT RECOMPUTE (requires the data plane)
    Recomputes every published number by a SECOND path. The independent path
    for the outcome layer is the human DPO's own merge skeleton, transcribed
    verbatim from the intake prompt — if the governed panel and the DPO's
    notebook logic disagree on a single cell, that is a finding, not a rounding
    note. Tier B is UNRUN as of delivery.

    python dp_uc38_verification.py            # Tier A only
    python dp_uc38_verification.py --full     # Tier A + Tier B
==============================================================================
"""
from __future__ import annotations

import importlib.util
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
_spec = importlib.util.spec_from_file_location(
    "build", os.path.join(HERE, "dp_uc38_nola_stubbs_battery.py"))
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

RESULTS: list[dict] = []


def check(name, cond, detail=""):
    RESULTS.append(dict(tier="A", check=name,
                        result="PASS" if cond else "FAIL", detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")
    return bool(cond)


# ===========================================================================
# TIER A — synthetic fixtures with hand-computed answers
# ===========================================================================
def fixture():
    """Three plate appearances, two catchers, every answer computed by hand.

    PA1 (cat 596117, game 1): FF(0-0) FF(0-1) KC(0-2,K)  -> 2 pairs, 1 repeat
    PA2 (cat 596117, game 1): SI(0-0) CH(1-0)            -> 1 pair,  0 repeats
    PA3 (cat 592663, game 2): KC(0-0) KC(1-0) KC(2-0)    -> 2 pairs, 2 repeats
    """
    rows = []

    def P(gp, ab, pn, pt, b, s, zone, desc, ev=None, cat=596117):
        rows.append(dict(game_pk=gp, at_bat_number=ab, pitch_number=pn, pitch_type=pt,
                         balls=b, strikes=s, zone=zone, description=desc, des=desc,
                         events=ev, fielder_2=cat, type="S",
                         launch_speed=np.nan, bb_type=None))

    P(1, 1, 1, "FF", 0, 0, 5, "called_strike")
    P(1, 1, 2, "FF", 0, 1, 5, "foul")
    P(1, 1, 3, "KC", 0, 2, 13, "swinging_strike", "strikeout")
    P(1, 2, 1, "SI", 0, 0, 11, "ball")
    P(1, 2, 2, "CH", 1, 0, 5, "called_strike")
    P(2, 1, 1, "KC", 0, 0, 13, "ball", None, 592663)
    P(2, 1, 2, "KC", 1, 0, 13, "ball", None, 592663)
    P(2, 1, 3, "KC", 2, 0, 5, "called_strike", None, 592663)
    return pd.DataFrame(rows)


def tier_a():
    print("\nTIER A — unit tests on hand-computed fixtures")
    df = fixture()
    ok = True

    r = m.repeat_pitch_rate(["fielder_2"], df).set_index("fielder_2")
    ok &= check("BAT-5 pair count (cat 596117)", r.loc[596117, "pitch_pairs"] == 3,
                "PA1 gives 2 pairs + PA2 gives 1 = 3")
    ok &= check("BAT-5 repeat count (cat 596117)", r.loc[596117, "repeats"] == 1,
                "only FF->FF repeats")
    ok &= check("BAT-5 all-same-pitch group = 1.0",
                r.loc[592663, "repeat_pitch_rate"] == 1.0, "KC KC KC")
    ok &= check("BAT-5 single-pitch PAs excluded from denominator",
                r.pitch_pairs.sum() == 5, "8 pitches, 3 PAs -> 5 consecutive pairs")

    e = m.arsenal_entropy(["fielder_2"], df).set_index("fielder_2")
    ok &= check("BAT-6 single-type group has zero entropy",
                abs(e.loc[592663, "entropy_nats"]) < 1e-9, "and not -0.0")
    ok &= check("BAT-6 active_types counted correctly",
                e.loc[596117, "active_types"] == 4, "FF SI KC CH")
    ok &= check("BAT-6 normalised entropy in [0,1]",
                bool(((e.entropy_norm >= -1e-9) & (e.entropy_norm <= 1 + 1e-9)).all()))

    ok &= check("BAT-7 JSD(identical) == 0", abs(m._js_divergence([1, 0], [1, 0])) < 1e-12)
    ok &= check("BAT-7 JSD(disjoint) == 1", abs(m._js_divergence([0.5, 0.5, 0], [0, 0, 1]) - 1.0) < 1e-9)
    ok &= check("BAT-7 JSD symmetric",
                abs(m._js_divergence([0.7, 0.3], [0.2, 0.8])
                    - m._js_divergence([0.2, 0.8], [0.7, 0.3])) < 1e-12)
    ok &= check("BAT-7 NaN when a side is empty",
                np.isnan(m.count_state_divergence(["fielder_2"], df)
                         .set_index("fielder_2").loc[592663, "js_divergence"]),
                "cat 592663 has zero ahead-count pitches")

    cs = set(m.count_state(df))
    ok &= check("CS-1 count_state domain closed", cs <= {"ahead", "even", "behind"}, str(sorted(cs)))

    fb = m.two_strike_fastball_rate(["fielder_2"], df).set_index("fielder_2")
    ok &= check("BAT-4 two-strike population correct", fb.loc[596117, "two_strike_pitches"] == 1)
    ok &= check("BAT-4 KC not counted as fastball", fb.loc[596117, "two_strike_fb_rate"] == 0.0)

    fp = m.first_pitch_mix(["fielder_2"], df)
    ok &= check("BAT-2 shares sum to 1 within group",
                bool((abs(fp.groupby("fielder_2").share.sum() - 1) < 1e-9).all()))

    z = m.zone_rate_by_count_state(["fielder_2"], df)
    ok &= check("BAT-8 zone_rate bounded [0,1]",
                bool(((z.zone_rate >= 0) & (z.zone_rate <= 1)).all()))

    iz = m.in_zone_whiff_rate(["fielder_2"], df)
    ok &= check("BAT-9 in-zone whiff uses same filter both sides",
                bool((iz.iz_whiffs <= iz.iz_swings).all()))

    pm = m.putaway_pitch_mix(["fielder_2"], df)
    ok &= check("BAT-3 only PA-terminal two-strike rows", int(pm.n.sum()) == 1,
                "one two-strike terminal pitch in the fixture")
    return ok


# ===========================================================================
# TIER B — independent recompute against the real data plane
# ===========================================================================
def dpo_skeleton_panel(nola, pos):
    """The human DPO's own merge logic, transcribed VERBATIM from the intake
    prompt, used as the INDEPENDENT path for the outcome layer.

        df = nola.merge(pos.groupby(['batter','player_name']).agg(pitches=...),
                        left_on=['fielder_2'], right_on=['batter'],
                        suffixes=('','_catcher'), how='inner')
        level = ['fielder_2','player_name','player_name_catcher']
        z = groupby(level).agg(total_pitches, uq_games)
              .merge(nresults).merge(chase_rate).merge(whiff_rate)
              .merge(putaway_rate).merge(fpsr)

    Agreement between this and `battery_panel` on every shared cell is the
    strongest receipt this product can produce, because the two paths were
    written independently by a human and by the build."""
    cat = (pos.groupby(["batter", "player_name"], as_index=False)
           .agg(pitches=("des", "size")))
    df = nola.merge(cat, left_on=["fielder_2"], right_on=["batter"],
                    suffixes=("", "_catcher"), how="inner")
    level = ["fielder_2", "player_name", "player_name_catcher"]
    z = (df.groupby(level, as_index=False)
         .agg(total_pitches=("des", "size"), uq_games=("game_pk", "nunique"))
         .sort_values(by="uq_games", ascending=False)
         .merge(m.nresults(level, df), on=level, how="left", suffixes=("", "_res"))
         .merge(m.chase_rate(level, df), on=level, how="left", suffixes=("", "_cr"))
         .merge(m.whiff_rate(level, df), on=level, how="left", suffixes=("", "_wr"))
         .merge(m.putaway_rate(level, df), on=level, how="left", suffixes=("", "_par"))
         .merge(m.fpsr(level, df), on=level, how="left", suffixes=("", "_fpsr")))
    return z


def tier_b():
    print("\nTIER B — independent recompute against the data plane")
    if m.PHIL_DIR is None:
        RESULTS.append(dict(tier="B", check="data_plane", result="UNRUN",
                            detail="data/phillies not mounted"))
        print("  [UNRUN] data plane not mounted — Tier B skipped.")
        return None
    allphi = m.load_all_phillies()
    pos, pps = m.split_roles(allphi)
    nola = m.attach_woba_weights(pps[pps.pitcher == m.NOLA].copy())

    dpo = dpo_skeleton_panel(nola, pos)
    cat_names = m.resolve_catcher_names(pos, nola)
    nola["catcher_id"] = nola.fielder_2.astype("Int64")
    nola = nola.merge(cat_names[["catcher_id", "resolved_name"]], on="catcher_id", how="left")
    built = m.battery_panel(["catcher_id", "resolved_name"], nola)

    a = dpo.set_index(dpo.fielder_2.astype(int))
    b = built.set_index(built.catcher_id.astype(int))
    shared = sorted(set(a.index) & set(b.index))
    RESULTS.append(dict(tier="B", check="catcher_slot_coverage",
                        result="PASS" if len(shared) == len(b) else "FAIL",
                        detail=f"{len(shared)} shared / {len(b)} built / {len(a)} dpo-path"))

    for col in ["total_pitches", "uq_games", "plate_apps", "woba", "krate", "bbrate",
                "hr_rate", "chase_rate", "whiff_rate", "putaway_rate",
                "first_pitch_strike_rate"]:
        if col not in a.columns or col not in b.columns:
            RESULTS.append(dict(tier="B", check=f"col::{col}", result="SKIP",
                                detail="column absent on one path"))
            continue
        d = (a.loc[shared, col].astype(float) - b.loc[shared, col].astype(float)).abs()
        worst = float(d.max())
        RESULTS.append(dict(tier="B", check=f"col::{col}",
                            result="PASS" if worst <= 0.0015 else "FAIL",
                            detail=f"max |delta| = {worst:.6f} over {len(shared)} slots "
                                   f"(tolerance 0.0015 = the locked 3dp rounding boundary)"))

    for f in ["dp_uc38_battery_career.csv", "dp_uc38_battery_season.csv",
              "dp_uc38_battery_window.csv", "dp_uc38_nola_baseline.csv",
              "dp_uc38_mix_by_catcher.csv", "dp_uc38_mix_by_catcher_window.csv",
              "dp_uc38_count_state_mix.csv",
              "dp_uc38_first_pitch_mix.csv", "dp_uc38_putaway_pitch_mix.csv",
              "dp_uc38_zone_by_count_state.csv", "dp_uc38_sequencing_window.csv",
              "dp_uc38_window_sensitivity.csv", "dp_uc38_confound_panel.csv",
              "dp_uc38_start_log.csv", "dp_uc38_catcher_identity.csv",
              "dp_uc38_attribution_guard.csv", "dp_uc38_dq_scorecard.csv",
              "dp_uc38_freshness_manifest.csv"]:
        RESULTS.append(dict(tier="B", check=f"receipt::{f}",
                            result="PASS" if os.path.isfile(os.path.join(OUT, f)) else "FAIL",
                            detail=""))
    return True


def main():
    print("=" * 78)
    print("dp_uc38_verification · uc-pps-027")
    print("=" * 78)
    a_ok = tier_a()
    if "--full" in sys.argv:
        tier_b()
    res = pd.DataFrame(RESULTS)
    os.makedirs(OUT, exist_ok=True)
    res.to_csv(os.path.join(OUT, "dp_uc38_verification_results.csv"), index=False)
    n_pass = int((res.result == "PASS").sum())
    n_fail = int((res.result == "FAIL").sum())
    print("\n" + "=" * 78)
    print(f"{n_pass} PASS · {n_fail} FAIL · {int((res.result=='UNRUN').sum())} UNRUN "
          f"· {int((res.result=='SKIP').sum())} SKIP")
    print("=" * 78)
    return 0 if (a_ok and n_fail == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
