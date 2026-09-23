"""
dp_uc47_verification.py — independent verification harness, UC #47 / uc-pps-032.

Families
  A  kernel fixtures      — hand-computed expectations for SG-1 (inherited), SG-6, SG-7, AF-3/5/6
  B  universe invariants  — FR-1 on real data: keys, level gate, game type, row accounting
  C  independent recompute — cohort + staff numbers straight from parquet with plain pandas,
                             NOT through dp_uc47_kernel (a genuinely different code path),
                             plus the inherited Baseball Functions whiff_rate as a cross-check
  D  surface consistency  — dashboard / figures / payload agree with receipts; offline HTML
  E  governance           — DQ, brand-center compliance, palette validator, package manifest
  F  narrative-to-receipt — every number the report prose asserts is re-derived from a receipt
                            and must appear, formatted, in the report text

Run: MLB_DATA_ROOT=<.../MLB> python dp_uc47_verification.py   ->  out/dp_uc47_verification_log.txt
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC47_OUT", HERE / "out"))
R = lambda n: pd.read_csv(OUT / f"dp_uc47_{n}.csv")
H = json.loads((OUT / "dp_uc47_headlines.json").read_text())
REPORT = (HERE / "dp_uc47_elite_ff_archetype_gap_report.md").read_text(encoding="utf-8")
LOG = []


def check(fam, name, ok, detail=""):
    LOG.append((fam, name, bool(ok), str(detail)[:200]))


# =============================================================================
# A · kernel fixtures
# =============================================================================
import dp_uc47_kernel as K

check("A", "parent kernel sha256 pinned", K.parent_kernel_hash() == K.PARENT_KERNEL_SHA256, K.parent_kernel_hash()[:16])
pop = np.array([40., 45, 50, 55, 60] * 4)            # mean 50, sd = 7.255
sd = pop.std(ddof=1)
g = K.scouting_grade(50.0, pop)
check("A", "SG-1 mean -> 50", g["grade"] == 50 and abs(g["z"]) < 1e-12, g)
g = K.scouting_grade(50 + sd, pop)
check("A", "SG-1 +1 SD -> 60", g["grade"] == 60, g["grade"])
g = K.scouting_grade(50 + 10 * sd, pop)
check("A", "SG-1 clips at 80", g["grade"] == 80, g["grade"])
g = K.scouting_grade(50 + sd, pop, higher_is_better=False)
check("A", "SG-1 lower-is-better flips sign", g["grade"] == 40, g["grade"])
check("A", "SG-1 NaN in -> NaN out", np.isnan(K.scouting_grade(np.nan, pop)["grade"]))
check("A", "SG-1 n<5 -> NaN", np.isnan(K.scouting_grade(1.0, pop[:4])["grade"]))
check("A", "_round5 half-up 57.5 -> 60", K._round5(57.5) == 60 and K._round5(52.5) == 55 and K._round5(57.4) == 55)
check("A", "SG-5 labels", K.grade_label(60) == "plus" and K.grade_label(70) == "plus-plus" and K.grade_label(55) == "above average")
# SG-7 stabilize
s = K.stabilize(pd.Series([0.40, 0.40]), pd.Series([56.0, 5600.0]), 56.0, 0.20)
check("A", "SG-7 shrink halfway at n=k", abs(s.iloc[0] - 0.30) < 1e-12, s.iloc[0])
check("A", "SG-7 large n barely moves", abs(s.iloc[1] - (0.20 + 5600 / 5656 * 0.20)) < 1e-12, s.iloc[1])
check("A", "SG-7 NaN stays NaN", np.isnan(K.stabilize(pd.Series([np.nan]), pd.Series([100.0]), 10, 0.2).iloc[0]))
# SG-6 on synthetic data: one drifting column, one flat
rng = np.random.default_rng(7)
yrs = np.repeat(np.arange(2018, 2027), 40)
syn = pd.DataFrame({"game_year": yrs, "a": 90 + 0.5 * (yrs - 2018) + rng.normal(0, 0.5, len(yrs)),
                    "b": np.tile(np.linspace(-1, 1, 40), 9)})   # exactly zero slope
adj, rec = K.season_trend_adjust(syn, ["a", "b"], pd.Series(True, index=syn.index), ref_year=2026)
ra = rec.set_index("metric")
check("A", "SG-6 adjusts a drifting metric", bool(ra.loc["a", "adjusted"]) and abs(ra.loc["a", "slope_per_season"] - 0.5) < 0.05, ra.loc["a", "slope_per_season"])
check("A", "SG-6 leaves a flat metric alone", (not bool(ra.loc["b", "adjusted"])) and (adj.b_adj == adj.b).all())
check("A", "SG-6 ref-year rows unchanged", np.allclose(adj.loc[adj.game_year == 2026, "a_adj"], adj.loc[adj.game_year == 2026, "a"]))
# AF-3 rollup on a toy frame
spec = K.ArchetypeSpec(name="t", pitch_type="FF", throws="R", era=(2020, 2020),
                       shape=[("x", True)], results=[("y", True)], pop_floor=10, subject_floor=5, swing_floor=1)
toy = pd.DataFrame({"game_year": 2020, "pitcher": range(20), "n": [20] * 19 + [6], "swings": 30,
                    "x_final": list(np.linspace(0, 19, 20)), "y_final": list(np.linspace(0, 19, 20))})
tg = K.archetype_grades(toy, spec, value_suffix="_final")
top = tg.iloc[18]
check("A", "AF-3 archetype flag = both axes plus", bool(top.ff_elite_archetype_flag) == (top.shape_grade >= 60 and top.results_grade >= 60))
check("A", "AF-3 thin flag below pop floor", bool(tg.iloc[19].thin) and not bool(tg.iloc[0].thin))
check("A", "AF-3 thin arm excluded from population", not bool(tg.iloc[19].pop_member))
# AF-5 / AF-6 toy
st = pd.DataFrame({"pitcher": [1, 2, 3], "n": [100, 300, 600], "role": ["RP", "RP", "SP"], "efc_score": [65.0, 45.0, 40.0],
                   "ff_elite_archetype_flag": [True, False, False]})
e = K.elite_share(st)
check("A", "AF-5 share = 100/1000", abs(e["share"] - 0.1) < 1e-12, e)
cands = pd.DataFrame({"game_year": [2025], "pitcher": [9], "role": ["RP"], "efc_score": [60.0], "ff_elite_archetype_flag": [True]})
ns = K.needle_swap(cands, st, spec)
check("A", "AF-6 displaces the lowest RP", int(ns.displaced_pitcher.iloc[0]) == 2)
check("A", "AF-6 delta EFS = V/T", abs(ns.delta_efs.iloc[0] - ns.V_role.iloc[0] / 1000) < 1e-12, ns.delta_efs.iloc[0])
check("A", "AF-6 delta score = V*(60-45)/T", abs(ns.delta_staff_score.iloc[0] - ns.V_role.iloc[0] * 15 / 1000) < 1e-12)

# =============================================================================
# B · universe invariants (real data)
# =============================================================================
U, rec, keying = K.house_pitch_universe()
check("B", "no duplicate pitch keys", U.duplicated(K.PITCH_KEY).sum() == 0)
check("B", "no MiLB rows", (~U.home_team.isin(K.MLB_CLUBS)).sum() == 0 and (~U.away_team.isin(K.MLB_CLUBS)).sum() == 0)
check("B", "regular season only", set(U.game_type.unique()) == {"R"})
nphl_kept = rec["nphl_rows"] - rec["nphl_rows_milb_removed"] - rec["nphl_rows_dup_of_phils"] - rec["nphl_rows_internal_dup"]
check("B", "row accounting closes", rec["phils_rows"] + nphl_kept == rec["union_rows_all_game_types"],
      (rec["phils_rows"], nphl_kept, rec["union_rows_all_game_types"]))
ur = R("universe_receipt").set_index("step").rows
check("B", "receipt matches rebuild", all(int(ur[k]) == int(v) for k, v in rec.items()))
check("B", "15 MiLB files identified", int((keying.level == "MiLB").sum()) == 15)
kf = keying.set_index("source_file")
check("B", "team pull giants-of-rangers-of-24 is batter-keyed", not bool(kf.loc["giants-of-rangers-of-24", "pitcher_keyed"]))
check("B", "pdodgers is pitcher-keyed", bool(kf.loc["pdodgers", "pitcher_keyed"]))
# independent dedup path: concat with phils first then drop_duplicates(keep='first')
alt = pd.concat([U[U.src == "phils"], U[U.src == "nphl"]]).drop_duplicates(K.PITCH_KEY)
check("B", "independent dedup gives same row count", len(alt) == len(U))
pg = R("population_graded")
check("B", "population = 405 pitcher-seasons >=100 FF", int(pg.pop_member.sum()) == 405 == H["pop_n"])
alt_pop = U[(U.p_throws == "R") & (U.pitch_type == "FF") & U.game_year.between(2018, 2026)].groupby(["game_year", "pitcher"]).size()
check("B", "population count via plain groupby", int((alt_pop >= 100).sum()) == 405, int((alt_pop >= 100).sum()))

# =============================================================================
# C · independent recompute from parquet (no kernel)
# =============================================================================
root = K.ROOT
ph = pd.concat([pq.read_table(root / "data" / "phillies" / f"phils_{y}.parquet",
                              columns=["game_date", "game_year", "game_type", "pitcher", "p_throws", "pitch_type", "release_speed",
                                       "release_spin_rate", "pfx_z", "description", "delta_run_exp", "phillies_role",
                                       "game_pk", "at_bat_number", "pitch_number", "des", "events",
                                       "estimated_woba_using_speedangle"]).to_pandas()
                for y in (2023, 2026)])
ph = ph[(ph.game_type == "R")]
SW = {"foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"}
WH = {"foul_tip", "missed_bunt", "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"}
cs = R("cohort_seasons")
for pid, yr in [(680742, 2026), (554430, 2023), (661395, 2026), (691725, 2026), (686934, 2026)]:
    d = ph[(ph.pitcher == pid) & (ph.game_year == yr) & (ph.pitch_type == "FF") & (ph.phillies_role == "pitching")]
    r = cs[(cs.pitcher == pid) & (cs.game_year == yr)].iloc[0]
    sw, wh = d.description.isin(SW).sum(), d.description.isin(WH).sum()
    check("C", f"{pid} {yr} n", len(d) == r.n, (len(d), r.n))
    check("C", f"{pid} {yr} velo", abs(d.release_speed.mean() - r.velo) < 1e-3, (d.release_speed.mean(), r.velo))
    check("C", f"{pid} {yr} ride", abs(12 * d.pfx_z.mean() - r.ivb_in) < 1e-3)
    check("C", f"{pid} {yr} spin", abs(d.release_spin_rate.mean() - r.spin) < 1e-2)
    check("C", f"{pid} {yr} whiff", abs(wh / sw - r.whiff_rate) < 1e-3, (wh / sw, r.whiff_rate))
    check("C", f"{pid} {yr} rv100", abs(-100 * d.delta_run_exp.mean() - r.rv100) < 1e-3)
    # the inherited, governed whiff_rate (Baseball Functions via dp_uc44_kernel)
    w = K.K44.whiff_rate(["pitcher"], d.assign(des=d.des.fillna("")))
    check("C", f"{pid} {yr} whiff == Baseball Functions whiff_rate", abs(float(w.whiff_rate.iloc[0]) - r.whiff_rate) < 1e-3)
# EFS straight from the Phillies 2026 log
p26 = ph[(ph.game_year == 2026) & (ph.phillies_role == "pitching") & (ph.p_throws == "R") & (ph.pitch_type == "FF")]
check("C", "staff RHP FF total = 4,201", len(p26) == 4201 == H["efs"]["ff_elite_archetype_flag"]["total_ff"], len(p26))
check("C", "Bowlan PHI FF = 467", int((p26.pitcher == 680742).sum()) == 467)
check("C", "EFS = 467/4201", abs(H["efs"]["ff_elite_archetype_flag"]["share"] - round(467 / 4201, 4)) < 1e-9)
check("C", "anchor = 2026-09-20", str(pd.to_datetime(ph[ph.game_year == 2026].game_date).max().date()) == "2026-09-20")
# Misiorowski single start
mz = U[(U.pitcher == 694819) & (U.game_year == 2026) & (U.pitch_type == "FF")]
check("C", "Misiorowski 2026 = 1 game, 69 FF, 23/40 whiffs",
      mz.game_pk.nunique() == 1 and len(mz) == 69 and mz.description.isin(WH).sum() == 23 and mz.description.isin(SW).sum() == 40,
      (mz.game_pk.nunique(), len(mz), mz.description.isin(WH).sum(), mz.description.isin(SW).sum()))
check("C", "Misiorowski start date 2026-06-12", set(mz.game_date.astype(str).str[:10]) == {"2026-06-12"})

# =============================================================================
# D · surface consistency
# =============================================================================
pay = pd.DataFrame(json.loads((OUT / "dp_uc47_payload.json").read_text()))
check("D", "payload rows = graded receipt rows", len(pay) == len(pg), (len(pay), len(pg)))
m = pay.dropna(subset=["shape_score", "results_score", "efc_score"])
check("D", "slider formula at w=0.5 reproduces efc_score", np.allclose(0.5 * m.shape_score + 0.5 * m.results_score, m.efc_score, atol=2e-3))
ws = R("weight_sensitivity_cohort_best")
for w in (0.0, 0.25, 0.5, 0.75, 1.0):
    sc = w * ws.shape_score + (1 - w) * ws.results_score
    check("D", f"cohort ranks reproduce at w={w}", (sc.rank(ascending=False, method="min").astype(int) == ws[f"rank_w{w:.2f}"]).all())
html = (HERE / "dp_uc47_archetype_explorer.html").read_text(encoding="utf-8")
ext = re.findall(r'<(?:script|link|img)[^>]+(?:src|href)=["\']https?://', html)
check("D", "dashboard is offline (no external src/href)", len(ext) == 0, ext[:2])
check("D", "dashboard embeds plotly.js", "Plotly" in html and len(html) > 4_000_000)
for f in ("fig1_archetype_map", "fig2_wheeler_velo", "fig3_painter_halves", "fig4_external_board", "fig5_needle",
          "fig6_weight_sensitivity", "fig7_stabilization"):
    check("D", f"{f} png+json both exist", (OUT / f"dp_uc47_{f}.png").exists() and (OUT / f"dp_uc47_{f}.json").exists())
wv = R("hp_wheeler_velo_by_year")
import base64
def _arr(v):   # plotly >= 6 serialises arrays as {"dtype", "bdata"}
    return np.frombuffer(base64.b64decode(v["bdata"]), dtype=v["dtype"]) if isinstance(v, dict) else np.asarray(v, dtype=float)
f2 = json.loads((OUT / "dp_uc47_fig2_wheeler_velo.json").read_text())
check("D", "fig2 box medians == receipt", np.allclose(_arr(f2["data"][0]["median"]), wv["median"]))
cand = R("candidates")
check("D", "no RANKED candidate out-scores Bowlan 2026", (cand[cand.board == "RANKED"].efc_score < H["bowlan26"]["efc"]).all())
check("D", "ranked board all >=100 FF; watch all 50-99", (cand[cand.board == "RANKED"].n >= 100).all() and cand[cand.board != "RANKED"].n.between(50, 99).all())

# =============================================================================
# E · governance
# =============================================================================
dq = R("dq_scorecard")
check("E", "DQ: zero FAIL", (dq.result == "FAIL").sum() == 0, dq.result.value_counts().to_dict())
check("E", "DQ: 16 PASS / 3 WARN", (dq.result == "PASS").sum() == 16 and (dq.result == "WARN").sum() == 3)
bc = pd.read_csv(OUT / "dp_uc47_brand_compliance.csv", keep_default_na=False)
check("E", "brand-center: all scored checks pass", (bc[bc.status != "n/a"].status == "pass").all(), bc.status.value_counts().to_dict())
check("E", "brand-center: 7 figures x 5 checks", len(bc[bc.status != "n/a"]) == 35)
pv = (OUT / "dp_uc47_palette_validation.txt").read_text()
check("E", "palette validator: light mode passes", pv.split("## mode=dark")[0].count("ALL CHECKS PASS") == 1)
for rel in re.findall(r"\((out/[^)]+\.png)\)", REPORT):
    check("E", f"report figure exists: {rel}", (HERE / rel).exists())
check("E", "no 'ff_elite_stuff_flag' used as a live name in kernel", "ff_elite_stuff_flag`" not in (HERE / "dp_uc47_kernel.py").read_text().split("DPO alias")[0])
check("E", "entity locks are ids", all(isinstance(k, int) for k in K.COHORT))
for f in ["00_dpo_orchestration_record.md", "01_strategy_intake.md", "02_engineering_design.md", "03_governance.md",
          "04_engineering_build.md", "05_quality_certification.md", "06_consumer_success.md", "07_platform_marketing.md",
          "README.md", "BID_2026-09-22_uc-pps-032-elite-rhp-ff-archetype-gap.md",
          "uc-pps-032-Elite RHP FF Archetype Gap 20260922.md", "uc_ledger_AI_PATCH_uc-pps-032-elite-rhp-ff-archetype-gap.md",
          "dp_uc47_elite_ff_archetype_gap_report.pdf", "dp_uc47_archetype_explorer.html"]:
    check("E", f"package file present: {f}", (HERE / f).exists())

# =============================================================================
# F · narrative-to-receipt  (value from receipt -> formatted string must be in the report)
# =============================================================================
lb = R("cohort_leaderboard").set_index("arm")
st = R("stabilization").set_index("metric")
tr = R("trend_adjust").set_index("metric")
tiers = R("tier_distribution").set_index("tier").pitcher_seasons
efs = R("efs_2026").set_index("flag")
gap = R("gap_size")
nd = R("needle").set_index("name")
hp = R("hp_reconciliation").set_index("id")
staff = R("staff_2026").set_index("name")
mom = R("population_moments").set_index("metric")
sens = R("sensitivity_matrix")
fa = R("hp_client_frame_audit").set_index("measure").value
b = H["bowlan26"]
cd = cand.set_index("name")
nm = R("name_resolution")


def claim(label, text):
    check("F", label, text in REPORT, text)


claim("universe MiLB removed", f"{int(ur['nphl_rows_milb_removed']):,} minor-league rows removed")
claim("universe dup of phils", f"{int(ur['nphl_rows_dup_of_phils']):,} rows that duplicate the Phillies logs")
claim("universe internal dup", f"{int(ur['nphl_rows_internal_dup']):,} internal duplicates")
claim("union rows", f"**{int(ur['union_rows_regular_season']):,}** regular-season MLB pitches")
claim("phils rows", f"{int(ur['phils_rows']):,} Phillies-log rows")
claim("nphl rows", f"{int(ur['nphl_rows']):,} `nphl` rows")
claim("pop 405", "405 pitcher-seasons, 2018–2026")
claim("elite 11", f"Only **{int(tiers['ELITE'])}** of the 405")
claim("tier table elite", f"| **ELITE** — plus on both | **{int(tiers['ELITE'])}** | {tiers['ELITE'] / 405:.1%} |")
claim("tier results-only", f"| Results-only | {int(tiers['RESULTS-ONLY'])} | {tiers['RESULTS-ONLY'] / 405:.1%} |")
claim("tier shape-only", f"| Shape-only | {int(tiers['SHAPE-ONLY'])} | {tiers['SHAPE-ONLY'] / 405:.1%} |")
claim("tier neither", f"| Neither | {int(tiers['NOT ELITE'])} | {tiers['NOT ELITE'] / 405:.1%} |")
claim("bowlan velo", f"{b['velo']:.1f} mph, {b['ivb']:.1f} inches of ride, a {b['whiff']:.3f} whiff rate".replace("0.", ".", 1).replace(" 0.", " ."))
claim("bowlan rv", f"+{b['rv100']:.2f} runs per 100")
claim("bowlan grades", f"shape **{b['shape']:.0f}**, results **{b['results']:.0f}**, composite **{b['composite']:.0f}**")
claim("bowlan rank", f"**#{b['pop_rank']} of 405**")
claim("bowlan component grades", f"velocity {b['g_velo']:.0f}, ride {b['g_ivb']:.0f}, spin {b['g_spin']:.0f}")
claim("bowlan whiff/rv grades", f"whiff grade **{b['g_whiff']:.0f}**, run value **{b['g_rv']:.0f}**")
check("F", "Buehler 2020 is #1", R("aspirational_ceiling").iloc[0][["name", "game_year"]].tolist() == ["Walker Buehler", 2020])
claim("efs total", f"**{int(efs.loc['ff_elite_archetype_flag', 'total_ff']):,}** four-seams")
claim("efs elite", f"**{int(efs.loc['ff_elite_archetype_flag', 'elite_ff'])}** came from")
claim("efs share", f"**{efs.loc['ff_elite_archetype_flag', 'share']:.1%}**")
claim("efs shape flag", f"By the shape flag alone, {efs.loc['ff_elite_shape_flag', 'share']:.1%}")
claim("efs results flag", f"by the results flag alone, **{efs.loc['ff_elite_results_flag', 'share']:.1%}**")
claim("ohtani score", f"Shohei Ohtani's 2025 at **{cd.loc['Shohei Ohtani', 'efc_score']:.1f}**")
claim("bowlan score", f"below Bowlan's **{b['efc']:.1f}**")
claim("duran score", f"below Duran's **{staff.loc['Jhoan Duran', 'efc_score']:.1f}**")
claim("gap vs bowlan", f"grades **{abs(gap.gap_points.iloc[0]):.1f} points below** Bowlan's")
claim("gap bowlan out", f"it's **{abs(gap.gap_points.iloc[1]):.1f} below** Duran's")
claim("misiorowski velo", f"**Jacob Misiorowski, {cd.loc['Jacob Misiorowski', 'velo']:.1f} mph**")
claim("misiorowski detail", f"**69 four-seams at {cd.loc['Jacob Misiorowski', 'velo']:.1f} mph and {cd.loc['Jacob Misiorowski', 'spin']:,.0f} rpm, 23 whiffs on 40 swings.**")
claim("misiorowski stab", f"that .575 whiff rate comes back to {cd.loc['Jacob Misiorowski', 'whiff_rate_final']:.3f}".replace("0.", ".", 1))
claim("misiorowski score", f"a **{cd.loc['Jacob Misiorowski', 'efc_score']:.1f}**")
claim("misiorowski raw->gov", f"Misiorowski fell from {cd.loc['Jacob Misiorowski', 'efc_score_ungoverned']:.1f} to {cd.loc['Jacob Misiorowski', 'efc_score']:.1f}")
claim("V_SP", f"**{int(nd.loc['Shohei Ohtani', 'V_role'])}** four-seams; a reliever's is **{int(nd.loc['Ben Casparius', 'V_role'])}**")
claim("casparius efs", f"An elite reliever moves the share **+{nd.loc['Ben Casparius', 'delta_efs'] * 100:.1f} points**")
claim("elite SP efs", f"An elite starter would move it **+{nd.loc['Jacob Misiorowski', 'delta_efs'] * 100:.1f}**")
claim("rotation scores", f"score {staff.loc['Zack Wheeler', 'efc_score']:.0f} (Wheeler), {staff.loc['Alan Rangel', 'efc_score']:.0f} (Rangel), "
      f"{staff.loc['Andrew Painter', 'efc_score']:.0f} (Painter) and {staff.loc['Aaron Nola', 'efc_score']:.0f} (Nola)")
claim("nola", f"**Aaron Nola — {staff.loc['Aaron Nola', 'efc_score']:.0f}**, {staff.loc['Aaron Nola', 'velo']:.1f} mph with a {staff.loc['Aaron Nola', 'whiff_rate']:.3f} whiff rate on {int(staff.loc['Aaron Nola', 'n_phi'])} pitches".replace(" 0.", " ."))
for arm in ["Shohei Ohtani", "Dylan Cease", "Chase Burns"]:
    claim(f"needle {arm}", f"| {arm} | SP | Nola's 669 | {'**' if arm == 'Shohei Ohtani' else ''}+{nd.loc[arm, 'delta_staff_score']:.1f}")
claim("needle kopech", f"| Michael Kopech | RP | Richards' 241 | +{nd.loc['Michael Kopech', 'delta_staff_score']:.1f}")
claim("needle casparius", f"| **Ben Casparius** | RP | Richards' 241 | +{nd.loc['Ben Casparius', 'delta_staff_score']:.1f} | **+{nd.loc['Ben Casparius', 'delta_efs'] * 100:.1f}** |")
claim("needle misiorowski", f"*+{nd.loc['Jacob Misiorowski', 'delta_staff_score']:.1f}* | ***+{nd.loc['Jacob Misiorowski', 'delta_efs'] * 100:.1f}***")
claim("board size", f"**{int((cand.board == 'RANKED').sum())} ranked arms** and a **{int((cand.board != 'RANKED').sum())}-arm watch list**")
check("F", "only one ranked ELITE = Casparius", cand[(cand.board == "RANKED") & (cand.archetype_tier == "ELITE")].name.tolist() == ["Ben Casparius"])
for arm in ["Shohei Ohtani", "Michael Kopech", "Dylan Cease", "Ben Casparius", "Chase Burns", "Emmet Sheehan", "Mick Abel"]:
    r = cd.loc[arm]
    claim(f"board row {arm}", f"{int(r.games)} G · {int(r.n)} FF · {r.coverage.lower()} | {'**' if arm == 'Ben Casparius' else ''}{r.shape_grade:.0f} / {r.results_grade:.0f}{'**' if arm == 'Ben Casparius' else ''} | {r.efc_score:.1f}")
r = cd.loc["Ben Casparius"]
claim("casparius detail", f"43 games, 384 four-seams, {r.velo:.1f} mph with {r.ivb_in:.1f} inches of ride and a {r.whiff_rate:.3f} whiff rate".replace(" 0.", " ."))
claim("skenes", f"a 65 on results and a 45 on shape, because his four-seam carries only {cd.loc['Paul Skenes', 'ivb_in']:.1f} inches")
check("F", "skenes 8th", int(cd.loc["Paul Skenes", "cand_rank"]) == 8 and int(cd.loc["Mick Abel", "cand_rank"]) == 7)
# cohort table
for arm, row in lb.iterrows():
    claim(f"cohort best {arm}", f"| {int(row.best_year)} | {row.best_shape:.0f} / {row.best_results:.0f} |")
    claim(f"cohort latest {arm}", f"{int(row.latest_year)} · {'**' if row.latest_thin else ''}{int(row.latest_n)} FF")
check("F", "cohort ranks in population", [int(x) for x in lb.best_rank_in_population] == [2, 7, 14, 31, 39, 339])
csx = cs.set_index(["arm", "game_year"])
w_ = cs[cs.arm == "Zack Wheeler"]
check("F", "Wheeler 9 seasons, 0 elite, 8 results-only", len(w_) == 9 and (w_.archetype_tier == "ELITE").sum() == 0 and (w_.archetype_tier == "RESULTS-ONLY").sum() == 8)
check("F", "Wheeler shape never above 55; results 65-70 since 2021", w_.shape_grade.max() == 55 and w_[w_.game_year >= 2021].results_grade.between(65, 70).all())
d_ = cs[cs.arm == "Jhoan Duran"]
check("F", "Duran velo 75-80, ride 35-45, spin 30-40", d_.g_velo.between(75, 80).all() and d_.g_ivb_in.between(35, 45).all() and d_.g_spin.between(30, 40).all())
mc = csx.loc[("Alex McFarlane", 2026)]
claim("mcfarlane", f"{mc.velo:.2f} mph and {mc.spin:,.0f} rpm: velocity **{mc.g_velo:.0f}**, spin **{mc.g_spin:.0f}**")
pa = csx.loc[("Andrew Painter", 2026)]
claim("painter whiff", f"It still misses **{pa.whiff_rate:.1%}** of swings (grade **{pa.g_whiff_rate:.0f}**)")
claim("painter rv", f"costs **{abs(pa.rv100):.2f} runs per 100** (grade **{pa.g_rv100:.0f}**)")
sd_ = cs[cs.arm == "Seranthony Domínguez"].set_index("game_year")
check("F", "Seranthony 2022 whiff 70; 2024 55/55", sd_.loc[2022, "g_whiff_rate"] == 70 and sd_.loc[2024, "shape_grade"] == 55 and sd_.loc[2024, "results_grade"] == 55)
wins = {w: ws.loc[ws[f"rank_w{w:.2f}"] == 1, "arm"].tolist() for w in (0.0, 0.25, 0.5, 0.75, 1.0)}
check("F", "weight winners (Duran@0, Bowlan@.25-.75, McFarlane@1)", wins[0.0] == ["Jhoan Duran"] and all(wins[w] == ["Jonathan Bowlan"] for w in (0.25, 0.5, 0.75)) and wins[1.0] == ["Alex McFarlane"])
check("F", "Bowlan 2nd at both extremes", int(ws.loc[ws.arm == "Jonathan Bowlan", "rank_w0.00"].iloc[0]) == 2 and int(ws.loc[ws.arm == "Jonathan Bowlan", "rank_w1.00"].iloc[0]) == 2)
# HP
claim("HP-1a", "Median 97.0 (2020) → 95.2 (2026); −0.30 mph/season, p = .021")
check("F", "HP-1a receipt", "median 97.0 (2020) -> 95.2 (2026); slope -0.30 mph/season, p=0.021" in hp.loc["HP-1a", "governed_value"])
check("F", "HP-1b receipt", "2024 IQR 94.6-96.0 vs 2026 IQR 94.7-95.9; overlap 86%" in hp.loc["HP-1b", "governed_value"])
claim("HP-1b", "IQR 94.6–96.0 vs 94.7–95.9; **86% overlap**")
check("F", "HP-1c 2021 3.7% and 0 since 2023", "2021 3.7%" in hp.loc["HP-1c", "governed_value"] and (wv[wv.game_year >= 2023].share_99_plus == 0).all())
claim("HP-2", f"96.6 mph → grade **{pa.g_velo:.0f}**")
phh = R("hp_painter_halves").set_index("half")
claim("HP-3", f"{phh.loc['First Half', 'spin_ex_outlier']:,.0f} → {phh.loc['Second Half', 'spin_ex_outlier']:,.0f} rpm, **+{(phh.loc['Second Half', 'spin_ex_outlier'] - phh.loc['First Half', 'spin_ex_outlier']) / mom.loc['spin', 'sd']:.2f} population SD**")
claim("HP-3 prose", f"**+{phh.loc['Second Half', 'spin_ex_outlier'] - phh.loc['First Half', 'spin_ex_outlier']:.0f} rpm** harder")
claim("HP-4", f"{phh.loc['First Half', 'ivb_in']:.1f} → {phh.loc['Second Half', 'ivb_in']:.1f} in, **+{(phh.loc['Second Half', 'ivb_in'] - phh.loc['First Half', 'ivb_in']) / mom.loc['ivb_in', 'sd']:.2f} SD**")
claim("HP-4 prose", f"carried **+{phh.loc['Second Half', 'ivb_in'] - phh.loc['First Half', 'ivb_in']:.2f} inches** more")
dg = csx.loc[("Jhoan Duran", 2026)]
claim("HP-5", f"Results **{dg.results_grade:.0f}**, shape **{dg.shape_grade:.0f}**, composite **{dg.ff_elite_composite:.0f}**")
b25 = csx.loc[("Jonathan Bowlan", 2025)]
claim("HP-6a", f"Ride grade **{b25.g_ivb_in:.0f}** in 2025 and 2026")
claim("HP-6b", f"Spin grade {b25.g_spin:.0f} (2025) / {b['g_spin']:.0f} (2026)")
claim("HP-6c", f"2025: {b25.whiff_rate:.3f} on {int(b25.swings)} swings → **{b25.g_whiff_rate:.0f}**".replace("0.", ".", 1))
check("F", "HP verdicts in report match receipt", all(v.split(" ")[0].title() in REPORT for v in hp.verdict))
claim("frame dups", f"**{int(fa['kellen_frame_dup_pitch_keys']):,} duplicate pitches**")
claim("frame milb", f"**{int(fa['kellen_frame_milb_rows']):,} minor-league pitches**")
claim("frame lhp", f"**{int(fa['kellen_frame_lhp_rows']):,} left-handed pitches**")
check("F", "frame 63.6% vs 64.5%", "63.6%" in hp.loc["HP-6a", "client_value"] and "64.5%" in hp.loc["HP-6a", "governed_value"])
claim("frame pct", "**63.6%** of that frame and **64.5%** of the governed one")
claim("name agreement", f"**{H['name_t2_agreement']:.1%}** of the time on {H['name_t2_overlap']} overlapping arms")
check("F", "5 unnamed pop seasons", H["unresolved_in_pop"] == 5 and "Five population pitcher-seasons are still unnamed" in REPORT)
claim("whiff k", f"Whiff rate needs **~{st.loc['whiff_rate', 'k']:.0f} swings**")
claim("rv k", f"Run value needs **~{st.loc['rv100', 'k']:,.0f} pitches**")
claim("velo drift", f"Velocity +{tr.loc['velo', 'slope_per_season']:.2f} mph and spin +{tr.loc['spin', 'slope_per_season']:.1f} rpm per season")
claim("drift shift", f"+{tr.loc['velo', 'shift_2018_to_ref']:.1f} mph and +{tr.loc['spin', 'shift_2018_to_ref']:.0f} rpm")
check("F", "drift p-values < .01; ride/whiff/rv not adjusted", (tr.loc[["velo", "spin"], "p_value"] < .01).all() and not tr.loc[["ivb_in", "whiff_rate", "rv100"], "adjusted"].any())
check("F", "sensitivity: Bowlan #1 in all 6", (sens.cohort_1 == "Jonathan Bowlan").all() and len(sens) == 6)
check("F", "sensitivity: board #1 Ohtani x4, Kopech x2", sens.candidate_1.value_counts().to_dict() == {"Shohei Ohtani": 4, "Michael Kopech": 2})
for _, r in sens.iterrows():
    check("F", f"sensitivity row in report: {r.variant[:30]}", f"| {r.pop_n} | {r.cohort_1.split()[-1]} | {r.candidate_1.split()[-1]} |" in REPORT)
check("F", "normality: ride & rv fail p<.001; others pass", (mom.loc[["ivb_in", "rv100"], "shapiro_p"] < .001).all() and mom.loc[["velo", "spin", "whiff_rate"], "normal_at_05"].all())
claim("twin agreement", f"they agree exactly on {mom.twin_identical_share.min():.0%}–{mom.twin_identical_share.max():.0%} of pitcher-seasons".replace("%–", "–"))
check("F", "twin max div 5, skew flags 0", mom.twin_max_abs_div.max() == 5 and mom.skew_flags.sum() == 0)
claim("dq", "**16 pass, 3 warn, 0 fail.**")
claim("partial coverage", f"{int((pg.pop_member & (pg.coverage == 'PARTIAL')).sum())} of the 405 population seasons are partial coverage")
check("F", "shape-flag / results-flag seasons sum", int(tiers.sum()) == 405)

# =============================================================================
fams = pd.DataFrame(LOG, columns=["family", "check", "ok", "detail"])
summary = fams.groupby("family").ok.agg(["sum", "count"])
lines = [f"dp_uc47 verification — {int(fams.ok.sum())}/{len(fams)} PASS", ""]
lines += [f"  family {f}: {int(r['sum'])}/{int(r['count'])}" for f, r in summary.iterrows()]
lines += ["", "FAILURES:"] + [f"  [{r.family}] {r.check} :: {r.detail}" for r in fams[~fams.ok].itertuples()] + [""]
lines += [f"[{r.family}] {'PASS' if r.ok else 'FAIL'}  {r.check}" for r in fams.itertuples()]
(OUT / "dp_uc47_verification_log.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[:12 + int((~fams.ok).sum())]))
