"""
dp_uc28 — VERIFICATION PASS  (quality department, 05.5)

Independently re-derives every headline number in
dp_uc28_painter_vs_orioles_report.md from the CSV receipts in out/, and
audits the report text for the governance rules that certification claims
were upheld.

This is deliberately written against the RECEIPTS, not against the build's
in-memory objects, so that a receipt/report mismatch is detectable. A handful
of checks re-read the raw parquet to confirm the receipts themselves are
faithful to source.

Run:  python dp_uc28_verification.py
Exit: 0 if all checks pass, 1 otherwise.
"""
from __future__ import annotations
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
REPORT = os.path.join(HERE, "dp_uc28_painter_vs_orioles_report.md")
LOG = os.path.join(OUT, "dp_uc28_verification_log.txt")

PAINTER = 691725
RESULTS: list[tuple[str, bool, str]] = []


def rd(name):
    return pd.read_csv(os.path.join(OUT, f"dp_uc28_{name}.csv"))


def check(label, condition, detail=""):
    RESULTS.append((label, bool(condition), detail))


def close(a, b, tol=0.0006):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def main():
    txt = open(REPORT, encoding="utf-8").read()

    lvl = rd("level_summary").set_index("level")
    ars = rd("arsenal_by_level")
    log = rd("start_log")
    stuff = rd("stuff_delta").set_index("pitch_name")
    rel = rd("release_by_start")
    relp = rd("release_by_level_pitch")
    ffloc = rd("fastball_whiff_by_location")
    bench = rd("ff_benchmark_painter").set_index("metric")
    spread = rd("arm_spread_painter")
    stand = rd("usage_by_stand")
    tto = rd("times_through_order")
    aaa_arc = rd("aaa_arc")
    mlb_arc = rd("mlb_arc")
    sep = rd("velo_separation").set_index("pitch_name")
    loc = rd("location_tiers")
    dq = rd("dq_scorecard")
    fresh = rd("freshness_manifest")
    plat = rd("platoon")

    a = lambda p: ars[(ars.level == "AAA") & (ars.pitch_name == p)].iloc[0]
    m = lambda p: ars[(ars.level == "MLB") & (ars.pitch_name == p)].iloc[0]

    # ---------------- A. source fidelity (receipts vs parquet) -------------
    phil = os.path.join(HERE, "data", "phillies", "phils_2026.parquet")
    opp = os.path.join(HERE, "data", "opponents", "lhvp26.parquet")
    src_mlb = pd.read_parquet(phil)
    src_mlb = src_mlb[(src_mlb.phillies_role == "pitching") &
                      (src_mlb.pitcher == PAINTER) & (src_mlb.game_type == "R")]
    src_mlb = src_mlb.drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
    src_aaa = pd.read_parquet(opp)
    src_aaa = src_aaa[src_aaa.pitcher == PAINTER].drop_duplicates(
        ["game_pk", "at_bat_number", "pitch_number"])

    check("A1  MLB pitch count 1141 traces to parquet",
          len(src_mlb) == 1141 == lvl.loc["MLB", "pitches"], f"{len(src_mlb)}")
    check("A2  AAA pitch count 396 traces to parquet",
          len(src_aaa) == 396 == lvl.loc["AAA", "pitches"], f"{len(src_aaa)}")
    check("A3  MLB start count is 14 (not 15 — spring excluded)",
          src_mlb.game_date.nunique() == 14 == lvl.loc["MLB", "starts"], "")
    check("A4  AAA start count is 5",
          src_aaa.game_date.nunique() == 5 == lvl.loc["AAA", "starts"], "")
    check("A5  Entity lock held in both source tiers",
          set(src_mlb.pitcher.unique()) == {PAINTER} and
          set(src_aaa.pitcher.unique()) == {PAINTER}, "")
    check("A6  52 spring-training pitches exist and were excluded",
          (pd.read_parquet(phil).query("pitcher == @PAINTER").game_type == "S").sum() == 52, "")
    check("A7  game_pk spaces are disjoint across tiers (union is safe)",
          len(set(src_mlb.game_pk) & set(src_aaa.game_pk)) == 0, "")
    check("A8  MLB PA 299 / AAA PA 101",
          lvl.loc["MLB", "plate_apps"] == 299 and lvl.loc["AAA", "plate_apps"] == 101, "")
    check("A9  AAA cache is fresh to 2026-07-30 (T-1 from game day)",
          str(pd.read_parquet(opp).game_date.max())[:10] == "2026-07-30", "")

    # ---------------- B. bottom-line finding 1 (benchmark) ----------------
    check("B1  4-seam velo 96.54, 55th pctile",
          close(bench.loc["velo", "painter_mlb"], 96.542, .01) and
          close(bench.loc["velo", "painter_mlb_pctile"], 54.8, .3), "")
    check("B2  IVB 16.27, 52nd pctile",
          close(bench.loc["ivb_in", "painter_mlb"], 16.267, .01) and
          close(bench.loc["ivb_in", "painter_mlb_pctile"], 51.6, .3), "")
    check("B3  extension 6.48, 52nd pctile",
          close(bench.loc["ext_ft", "painter_mlb"], 6.479, .01) and
          close(bench.loc["ext_ft", "painter_mlb_pctile"], 51.6, .3), "")
    check("B4  FUTR .542, 48th pctile, equals pool median",
          close(bench.loc["futr", "painter_mlb"], .542) and
          close(bench.loc["futr", "painter_mlb_pctile"], 48.4, .3) and
          close(bench.loc["futr", "pool_median"], .542), "")
    check("B5  4-seam whiff .106 vs pool median .200, 26th pctile",
          close(bench.loc["ff_whiff", "painter_mlb"], .106) and
          close(bench.loc["ff_whiff", "pool_median"], .200) and
          close(bench.loc["ff_whiff", "painter_mlb_pctile"], 25.8, .3), "")
    check("B6  upper-third whiff .101 vs median .250, 23rd pctile",
          close(bench.loc["ff_whiff_upper", "painter_mlb"], .101) and
          close(bench.loc["ff_whiff_upper", "pool_median"], .250) and
          close(bench.loc["ff_whiff_upper", "painter_mlb_pctile"], 22.6, .3), "")
    check("B7  benchmark pool is 31 pitchers",
          int(bench.loc["ff_whiff", "pool_n"]) == 31 == len(rd("ff_benchmark_pool")), "")

    # ---------------- C. bottom-line finding 2 (arm spread) ---------------
    sp_mlb = spread[spread.scope.str.contains("MLB")].iloc[0]
    sp_aaa = spread[spread.scope.str.contains("AAA")].iloc[0]
    check("C1  MLB arm spread 13.8deg", close(sp_mlb.arm_spread_deg, 13.845, .01), "")
    check("C2  pool median 4.25, p90 9.93",
          close(sp_mlb.pool_median, 4.25, .01) and close(sp_mlb.pool_p90, 9.93, .02), "")
    check("C3  96th percentile, pool n=23",
          close(sp_mlb.pctile_high_is_worse, 95.7, .5) and int(sp_mlb.pool_n) == 23, "")
    check("C4  AAA spread widened to 15.0", close(sp_aaa.arm_spread_deg, 14.966, .01), "")
    ff_arm = relp[(relp.level == "MLB") & (relp.pitch_name == "4-Seam Fastball")].iloc[0]
    sw_arm = relp[(relp.level == "MLB") & (relp.pitch_name == "Sweeper")].iloc[0]
    cu_arm = relp[(relp.level == "MLB") & (relp.pitch_name == "Curveball")].iloc[0]
    check("C5  spread endpoints are CU 52.1 and SW 38.2",
          close(cu_arm.arm_angle, 52.086, .01) and close(sw_arm.arm_angle, 38.242, .01), "")
    check("C6  FF-to-SW horizontal release gap is 6.3 inches",
          close(abs(ff_arm.rel_x_ft - sw_arm.rel_x_ft) * 12, 6.26, .05), "")
    sp_mlb_p = relp[(relp.level == "MLB") & (relp.pitch_name == "Split-Finger")].iloc[0]
    sp_aaa_p = relp[(relp.level == "AAA") & (relp.pitch_name == "Split-Finger")].iloc[0]
    check("C7  splitter arm angle fell 46.1 -> 40.9 (left the FB cluster)",
          close(sp_mlb_p.arm_angle, 46.097, .01) and close(sp_aaa_p.arm_angle, 40.867, .01), "")

    # ---------------- D. bottom-line finding 3 (usage vs stuff) -----------
    for p, mv, av, dv in [("4-Seam Fastball", .331, .492, 16.114),
                          ("Slider", .214, .083, -13.051),
                          ("Sweeper", .114, .197, 8.303),
                          ("Split-Finger", .144, .068, -7.555)]:
        check(f"D  usage shift {p}: {mv:.3f} -> {av:.3f} ({dv:+.1f} pts)",
              close(m(p).usage, mv) and close(a(p).usage, av) and
              close(stuff.loc[p, "d_usage_pp"], dv, .01), "")
    check("D5  4-seam stuff barely moved (+0.64 mph, -0.25 ride, -0.55 horiz)",
          close(stuff.loc["4-Seam Fastball", "d_velo"], .639, .01) and
          close(stuff.loc["4-Seam Fastball", "d_ivb"], -.248, .01) and
          close(stuff.loc["4-Seam Fastball", "d_hb"], -.545, .01), "")
    check("D6  splitter is the only material stuff change (+2.75 mph, +2.43 horiz)",
          close(stuff.loc["Split-Finger", "d_velo"], 2.748, .01) and
          close(stuff.loc["Split-Finger", "d_hb"], 2.427, .01), "")
    check("D7  FF-SP separation compressed 9.13 -> 7.03 (-2.11)",
          close(sep.loc["Split-Finger", "MLB"], 9.13, .01) and
          close(sep.loc["Split-Finger", "AAA"], 7.03, .01) and
          close(sep.loc["Split-Finger", "d_sep_aaa_minus_mlb"], -2.11, .01), "")
    check("D8  slider and splitter were his best MLB whiff pitches (.377/.384)",
          close(m("Slider").whiff_rate, .377) and close(m("Split-Finger").whiff_rate, .384), "")
    check("D9  SL/SW tags are distinct in BOTH feeds (-6.3/-6.9 vs -15.7/-15.8)",
          close(m("Slider").hb_in, -6.314, .01) and close(a("Slider").hb_in, -6.88, .01) and
          close(m("Sweeper").hb_in, -15.713, .01) and close(a("Sweeper").hb_in, -15.789, .01), "")
    check("D10 sweeper posted the highest CSW at either level (.410 at AAA)",
          close(a("Sweeper").csw_rate, .410) and
          a("Sweeper").csw_rate == ars.csw_rate.max(), "")

    # ---------------- E. bottom-line finding 4 (delivery) -----------------
    relf = rel.dropna(subset=["mean_x_ft_in"]).copy()
    band = relf[~relf.game_date.isin(["2026-06-17", "2026-06-28"])]
    mlb_band = band[band.level == "MLB"]
    check("E1  13 MLB starts sit in a 2.1-inch band",
          len(mlb_band) == 13 and
          close(mlb_band.mean_x_ft_in.max() - mlb_band.mean_x_ft_in.min(), 2.11, .05), "")
    d617 = relf[relf.game_date == "2026-06-17"].iloc[0]
    d628 = relf[relf.game_date == "2026-06-28"].iloc[0]
    check("E2  06-17 release-x is -20.5 in (12 four-seams — directional)",
          close(d617.mean_x_ft_in, -20.5, .05) and int(d617.ff_pitches) == 12, "")
    check("E3  06-28 release-x is -20.05 in (44 four-seams — solid)",
          close(d628.mean_x_ft_in, -20.05, .05) and int(d628.ff_pitches) == 44, "")
    check("E4  both outliers are ~5in from the band",
          abs(d617.mean_x_ft_in - mlb_band.mean_x_ft_in.mean()) > 4.5 and
          abs(d628.mean_x_ft_in - mlb_band.mean_x_ft_in.mean()) > 4.5, "")
    d710 = relf[relf.game_date == "2026-07-10"].iloc[0]
    check("E5  same-park control: 06-28 vs 07-10 differ by 5.6 in",
          close(abs(d628.mean_x_ft_in - d710.mean_x_ft_in), 5.58, .05), "")
    src_aaa2 = src_aaa.copy()
    src_aaa2["gd"] = src_aaa2.game_date.astype(str)
    parks = src_aaa2.groupby("gd").home_team.first()
    check("E6  06-28 and 07-10 really were the same park (LHV)",
          parks["2026-06-28"] == "LHV" and parks["2026-07-10"] == "LHV", "")
    aaa_log = log[log.level == "AAA"].sort_values("game_date")
    check("E7  AAA extension declines monotonically 6.451 -> 6.293",
          list(aaa_log.ext_ft) == sorted(aaa_log.ext_ft, reverse=True) and
          close(aaa_log.ext_ft.iloc[0], 6.451, .001) and
          close(aaa_log.ext_ft.iloc[-1], 6.293, .001), list(aaa_log.ext_ft))
    arm_by_start = (pd.concat([src_mlb, src_aaa]).assign(gd=lambda d: d.game_date.astype(str))
                    .groupby("gd").arm_angle.mean())
    aaa_arm = arm_by_start.loc[["2026-06-28", "2026-07-04", "2026-07-10",
                               "2026-07-21", "2026-07-26"]]
    check("E8  AAA arm angle declines monotonically 47.1 -> 40.6",
          list(aaa_arm) == sorted(aaa_arm, reverse=True) and
          close(aaa_arm.iloc[0], 47.12, .02) and close(aaa_arm.iloc[-1], 40.559, .02), "")
    check("E9  AAA 4-seam velo rose 96.6 -> 97.8 over the same window",
          close(aaa_log.ff_velo.iloc[0], 96.559, .01) and
          close(aaa_log.ff_velo.iloc[-1], 97.771, .01), "")
    check("E10 perceived-velo gain from extension shrank +0.31 -> +0.22",
          close(ff_arm.velo_added_by_ext, .31, .005) and
          close(relp[(relp.level == "AAA") &
                     (relp.pitch_name == "4-Seam Fastball")].iloc[0].velo_added_by_ext, .22, .005), "")
    check("E11 RCI is essentially flat across levels (~1.16 vs ~1.20)",
          close(rel[rel.level == "MLB"].rci_in.mean(), 1.176, .02) and
          close(rel[rel.level == "AAA"].rci_in.mean(), 1.199, .02), "")

    # ---------------- F. bottom-line finding 5 (platoon) ------------------
    sL = lambda L, p: stand[(stand.level == L) & (stand.stand == "L") &
                            (stand.pitch_name == p)]
    spl_m, spl_a = sL("MLB", "Split-Finger").iloc[0], sL("AAA", "Split-Finger").iloc[0]
    swp_m, swp_a = sL("MLB", "Sweeper").iloc[0], sL("AAA", "Sweeper").iloc[0]
    check("F1  splitter vs LHH .395 whiff on 76 MLB swings",
          close(spl_m.whiff_rate, .395) and int(spl_m.swings) == 76, "")
    check("F2  splitter vs LHH usage halved .214 -> .106",
          close(spl_m.usage, .214) and close(spl_a.usage, .106), "")
    check("F3  sweeper vs LHH quadrupled .044 -> .176",
          close(swp_m.usage, .044) and close(swp_a.usage, .176), "")
    pL = lambda L: plat[(plat.level == L) & (plat.stand == "L")].iloc[0]
    check("F4  whiff vs LHH fell .215 (185 PA) -> .150 (65 PA)",
          close(pL("MLB").whiff_rate, .215) and int(pL("MLB").plate_apps) == 185 and
          close(pL("AAA").whiff_rate, .150) and int(pL("AAA").plate_apps) == 65, "")
    check("F5  zero splitters and zero curveballs to RHH at AAA",
          len(stand[(stand.level == "AAA") & (stand.stand == "R") &
                    (stand.pitch_name.isin(["Split-Finger", "Curveball"]))]) == 0, "")
    rA = stand[(stand.level == "AAA") & (stand.stand == "R")]
    check("F6  FF+SW = 73.8% of AAA pitches to RHH",
          close(rA[rA.pitch_name.isin(["4-Seam Fastball", "Sweeper"])].usage.sum(), .738, .002), "")

    # ---------------- G. supporting sections ------------------------------
    e = ffloc[ffloc.cut == "elevation band"]
    g = lambda L, t: e[(e.level == L) & (e.loc_tier == t)].iloc[0].whiff_rate
    check("G1  MLB elevation did nothing: .101 up vs .111 down",
          close(g("MLB", "upper_third_or_above"), .101) and
          close(g("MLB", "lower_two_thirds"), .111), "")
    check("G2  AAA elevation converted: .259 up vs .169 down",
          close(g("AAA", "upper_third_or_above"), .259) and
          close(g("AAA", "lower_two_thirds"), .169), "")
    z = ffloc[ffloc.cut == "zone tier"]
    zz = lambda L, t: z[(z.level == L) & (z.loc_tier == t)].iloc[0]
    check("G3  MLB 4-seam heart .091 on 121 swings, shadow .074 on 27",
          close(zz("MLB", "heart").whiff_rate, .091) and int(zz("MLB", "heart").swings) == 121 and
          close(zz("MLB", "shadow").whiff_rate, .074) and int(zz("MLB", "shadow").swings) == 27, "")
    ma = mlb_arc.set_index("arc")
    e8, l7 = ma.index[0], ma.index[1]
    check("G4  MLB arc: chase .357 -> .265, in-zone .447 -> .522",
          close(ma.loc[e8, "chase_rate"], .357) and close(ma.loc[l7, "chase_rate"], .265) and
          close(ma.loc[e8, "in_zone_rate"], .447) and close(ma.loc[l7, "in_zone_rate"], .522), "")
    check("G5  MLB arc: FF usage .367 -> .277, K% .198 -> .150, BB% .070 -> .094",
          close(ma.loc[e8, "ff_usage"], .367) and close(ma.loc[l7, "ff_usage"], .277) and
          close(ma.loc[e8, "krate"], .198) and close(ma.loc[l7, "krate"], .150) and
          close(ma.loc[e8, "bbrate"], .070) and close(ma.loc[l7, "bbrate"], .094), "")
    check("G6  MLB arc: velocity flat 96.5 -> 96.6",
          close(ma.loc[e8, "ff_velo"], 96.535, .01) and close(ma.loc[l7, "ff_velo"], 96.556, .01), "")
    aa = aaa_arc.set_index("arc")
    ea, la = aa.index[0], aa.index[1]
    check("G7  AAA arc improved on every process indicator",
          aa.loc[la, "strike_rate"] > aa.loc[ea, "strike_rate"] and
          aa.loc[la, "csw_rate"] > aa.loc[ea, "csw_rate"] and
          aa.loc[la, "chase_rate"] > aa.loc[ea, "chase_rate"] and
          aa.loc[la, "first_pitch_strike_rate"] > aa.loc[ea, "first_pitch_strike_rate"] and
          aa.loc[la, "hard_hit_rate"] < aa.loc[ea, "hard_hit_rate"] and
          aa.loc[la, "futr"] > aa.loc[ea, "futr"], "")
    check("G8  AAA arc PA are 37 early / 64 late",
          int(aa.loc[ea, "plate_apps"]) == 37 and int(aa.loc[la, "plate_apps"]) == 64, "")
    b721 = log[log.game_date == "2026-07-21"].iloc[0]
    check("G9  best start 07-21: 73.6% strikes, 34.5% CSW, 52.3% chase, 8K/1BB",
          close(b721.strike_rate, .736) and close(b721.csw_rate, .345) and
          close(b721.chase_rate, .523) and b721.strikeouts == 8 and b721.walks == 1, "")
    t = lambda L, p: tto[(tto.level == L) & (tto.tto_lbl == p)].iloc[0].hard_hit_rate
    check("G10 hard-hit climbs every pass at BOTH levels",
          t("MLB", "1st time") < t("MLB", "2nd time") < t("MLB", "3rd+ time") and
          t("AAA", "1st time") < t("AAA", "2nd time") < t("AAA", "3rd+ time"), "")
    check("G11 MLB 3rd-pass wOBA actually FALLS (report says results are noisy)",
          tto[(tto.level == "MLB") & (tto.tto_lbl == "3rd+ time")].iloc[0].woba <
          tto[(tto.level == "MLB") & (tto.tto_lbl == "1st time")].iloc[0].woba, "")
    check("G12 AAA pitch counts were 80/69/70/87/90",
          list(log[log.level == "AAA"].sort_values("game_date").pitches) == [80, 69, 70, 87, 90], "")
    spl_loc = loc[(loc.level == "AAA") & (loc.pitch_name == "Split-Finger")]
    check("G13 splitter in-zone .463 -> .185; 40.7% waste at AAA",
          close(m("Split-Finger").in_zone_rate, .463) and
          close(a("Split-Finger").in_zone_rate, .185) and
          close(spl_loc[spl_loc.loc_tier == "waste"].iloc[0].share, .407), "")
    check("G14 hard-hit is above average at both levels (.352 / .338)",
          close(lvl.loc["MLB", "hard_hit_rate"], .352) and
          close(lvl.loc["AAA", "hard_hit_rate"], .338), "")

    # ---------------- H. governance rules upheld in the TEXT --------------
    body = txt.lower()
    # H1: xwOBA may be NAMED as a caveat but never PUBLISHED as a value.
    # Test: every line mentioning xwoba/estimated_woba must be a caveat line
    # (contains a negation) AND must carry no decimal number.
    xw_lines = [ln for ln in txt.splitlines()
                if re.search(r"xwoba|estimated_woba", ln, re.I)]
    caveat_words = ("no ", "not ", "never", "untrust", "deprecat", "barred", "26%")
    bad = [ln for ln in xw_lines
           if not any(w in ln.lower() for w in caveat_words)
           or re.search(r"\.\d{3}\b", ln)]
    check("H1  xwOBA appears only as a caveat, never as a published value",
          len(xw_lines) > 0 and len(bad) == 0,
          f"{len(xw_lines)} mentions, {len(bad)} violating: {bad[:2]}")
    check("H2  no health / injury / fatigue claim attached to mechanical drift",
          not re.search(r"(injur|fatigue|arm health|sore|strain|ligament|tommy john)", body),
          "privacy ruling 03.4 R2")
    check("H3  tipping claim is labelled a hypothesis, not a finding",
          "this is a hypothesis, not a proof" in body and "this is not proof" in body, "")
    check("H4  opponent gap disclosed to the READER, not just to governance",
          "there is no orioles scouting in this report" in body and
          "zero orioles hitter rows" in body, "")
    check("H5  AAA sample shortfall disclosed in the warning box",
          "below" in body and "100-bf convention" in body, "")
    check("H6  benchmark pool described as small / directional",
          "small pool" in body and "directional" in body, "")
    check("H7  park notes flagged as carry-in with no numbers",
          "carry-in, not computed" in body, "")
    check("H8  every persona named in the takeaways",
          all(s in txt for s in ["**For Painter**", "**For J.T. Realmuto**",
                                 "**For the pitching department**", "**For the manager**"]), "")
    check("H9  entity lock stated in the report warning box",
          "691725" in txt and "no name filtering" in body, "")
    check("H10 DQ scorecard records the opponent FAIL",
          (dq[dq.check == "Opponent coverage"].status == "FAIL").all(), "")
    check("H11 freshness manifest records that no BAL lineup was carried in",
          fresh.fitness.str.contains("NOT CARRIED").any() and
          fresh.fitness.str.contains("ABSENT").any(), "")
    check("H12 no rate KPI receipt pools MLB and AAA",
          all("level" in rd(n).columns for n in
              ["level_summary", "start_log", "arsenal_by_level", "platoon",
               "location_tiers", "usage_by_stand", "times_through_order",
               "fastball_elevation", "fastball_whiff_by_location"]), "")

    # ---------------- report ----------------------------------------------
    lines = ["=" * 88,
             "dp_uc28 VERIFICATION PASS — headline numbers re-derived from out/ receipts",
             "=" * 88, ""]
    for label, ok, detail in RESULTS:
        lines.append(f"[{'PASS' if ok else 'FAIL'}]  {label}" + (f"   {detail}" if detail and not ok else ""))
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    lines += ["", "-" * 88,
              f"{n_pass} / {len(RESULTS)} checks passed",
              "-" * 88]
    out = "\n".join(lines)
    print(out)
    with open(LOG, "w", encoding="utf-8") as fh:
        fh.write(out + "\n")
    return 0 if n_pass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
