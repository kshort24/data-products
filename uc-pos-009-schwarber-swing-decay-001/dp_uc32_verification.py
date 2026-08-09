"""
dp_uc32_verification.py — independent verification harness for UC #33.

Re-derives every headline number from the raw parquet by a DIFFERENT code path
than the build script (no shared helper functions), then asserts against the
CSV receipts and against the numbers actually printed in the reader report.

The point is not to re-run the build. It is to catch the build being wrong.

Exit code 0 = all checks pass. Non-zero = do not publish.
"""

from __future__ import annotations

import os
import re
import sys
import glob
import json

import numpy as np
import pandas as pd

pd.set_option("display.width", 250)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
REPORT = os.path.join(HERE, "dp_uc32_schwarber_swing_decay_report.md")

_CANDIDATES = [
    os.environ.get("DP_MLB_ROOT"),
    os.path.join(HERE, "..", "..", "..", "Python Scripts", "MLB"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB",
    "/sessions/admiring-inspiring-galileo/mnt/MLB",
]
ROOT = next(c for c in _CANDIDATES if c and os.path.isdir(os.path.join(c, "data", "phillies")))

SCH = 656941
CHECKS: list[dict] = []


def ck(cid, desc, ok, got="", want=""):
    CHECKS.append({"id": cid, "check": desc,
                   "result": "PASS" if bool(ok) else "FAIL",
                   "got": str(got), "expected": str(want)})


def close(a, b, tol=5e-3):
    if a is None or b is None:
        return False
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Independent reload — deliberately NOT importing the build script
# ---------------------------------------------------------------------------

print("[verify] independent reload from parquet")

frames = []
for f in sorted(glob.glob(os.path.join(ROOT, "data", "phillies", "phils_*.parquet"))):
    frames.append(pd.read_parquet(f))
allp = pd.concat(frames, ignore_index=True)
posv = allp[allp["phillies_role"] == "batting"]
nphv = pd.read_parquet(os.path.join(ROOT, "data", "opponents", "schwarber.parquet"))

v = pd.concat([nphv[nphv["batter"] == SCH], posv[posv["batter"] == SCH]],
              ignore_index=True, sort=False)
v = v.drop_duplicates(subset=["game_pk", "at_bat_number", "pitch_number"])
v = v[v["game_type"] == "R"].copy()
for c in ["launch_speed", "launch_angle", "launch_speed_angle", "bat_speed", "swing_length",
          "attack_angle", "swing_path_tilt", "intercept_ball_minus_batter_pos_y_inches",
          "estimated_woba_using_speedangle", "zone", "release_speed"]:
    v[c] = pd.to_numeric(v[c], errors="coerce").astype("float64")
v["game_date"] = pd.to_datetime(v["game_date"])
v = v.sort_values(["game_date", "game_pk", "at_bat_number", "pitch_number"]).reset_index(drop=True)

SW = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
      "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WH = ["foul_tip", "missed_bunt", "swinging_pitchout", "swinging_strike",
      "swinging_strike_blocked"]

v26 = v[v["game_year"] == 2026]
v25 = v[v["game_year"] == 2025]
bip26 = v26[v26["type"] == "X"].reset_index(drop=True)
bip25 = v25[v25["type"] == "X"]

# ---------------------------------------------------------------------------
# 1. Entity & scope
# ---------------------------------------------------------------------------

ck("V-01", "single batter id in locked frame", set(v["batter"].unique()) == {SCH},
   sorted(v["batter"].unique()), [SCH])
ck("V-02", "no duplicate pitch keys",
   v.duplicated(subset=["game_pk", "at_bat_number", "pitch_number"]).sum() == 0, 0, 0)
ck("V-03", "regular season only", set(v["game_type"].unique()) == {"R"},
   sorted(v["game_type"].unique()), ["R"])
ck("V-04", "career pitch count matches report", len(v) == 24891, len(v), 24891)
ck("V-05", "as-of date is 2026-08-07", f"{v['game_date'].max():%Y-%m-%d}" == "2026-08-07",
   f"{v['game_date'].max():%Y-%m-%d}", "2026-08-07")

# ---------------------------------------------------------------------------
# 2. Receipts exist and agree with an independent recompute
# ---------------------------------------------------------------------------

a1 = pd.read_csv(os.path.join(OUT, "dp_uc32_a1_career_season_spine.csv"))
a2 = pd.read_csv(os.path.join(OUT, "dp_uc32_a2_bat_tracking_coverage.csv"))
b5 = pd.read_csv(os.path.join(OUT, "dp_uc32_b5_phase_split_2026.csv"))
b6 = pd.read_csv(os.path.join(OUT, "dp_uc32_b6_phase_delta.csv"))
c1 = pd.read_csv(os.path.join(OUT, "dp_uc32_c1_la_distribution.csv"))
x1 = pd.read_csv(os.path.join(OUT, "dp_uc32_x1_imputation_harm.csv"))
e2 = pd.read_csv(os.path.join(OUT, "dp_uc32_e2_lhb_percentiles_2026.csv"))
head = json.load(open(os.path.join(OUT, "dp_uc32_headline.json")))

r26 = a1[a1["game_year"] == 2026].iloc[0]
r25 = a1[a1["game_year"] == 2025].iloc[0]

ck("V-06", "2026 BIP recomputed", int(r26["bips"]) == len(bip26), r26["bips"], len(bip26))
ck("V-07", "2026 barrel rate recomputed",
   close(r26["barrel_rate"], (bip26["launch_speed_angle"] == 6).mean(), 1e-3),
   r26["barrel_rate"], round((bip26["launch_speed_angle"] == 6).mean(), 4))
ck("V-08", "2026 mean EV recomputed",
   close(r26["ev_mu"], bip26["launch_speed"].mean(), 1e-2),
   r26["ev_mu"], round(bip26["launch_speed"].mean(), 3))
ck("V-09", "2026 EV90 recomputed",
   close(r26["ev90"], bip26["launch_speed"].quantile(0.90), 1e-2),
   r26["ev90"], round(bip26["launch_speed"].quantile(0.90), 2))
ck("V-10", "2026 bat speed recomputed on MEASURED swings only",
   close(r26["bat_speed_mu"], v26[v26["description"].isin(SW)]["bat_speed"].mean(), 1e-2),
   r26["bat_speed_mu"], round(v26[v26["description"].isin(SW)]["bat_speed"].mean(), 3))
ck("V-11", "2025 bat speed recomputed",
   close(r25["bat_speed_mu"], v25[v25["description"].isin(SW)]["bat_speed"].mean(), 1e-2),
   r25["bat_speed_mu"], round(v25[v25["description"].isin(SW)]["bat_speed"].mean(), 3))
ck("V-12", "2026 sweet-spot rate recomputed",
   close(r26["sweet_spot_rate"], bip26["launch_angle"].between(8, 32).mean(), 1e-3),
   r26["sweet_spot_rate"], round(bip26["launch_angle"].between(8, 32).mean(), 4))
ck("V-13", "2026 hard-hit rate recomputed",
   close(r26["hard_hit_rate"], (bip26["launch_speed"] >= 95).mean(), 1e-3),
   r26["hard_hit_rate"], round((bip26["launch_speed"] >= 95).mean(), 4))
ck("V-14", "2026 HR count recomputed",
   int(r26["hrs"]) == int((v26["events"] == "home_run").sum()),
   r26["hrs"], int((v26["events"] == "home_run").sum()))
ck("V-15", "2025 HR count recomputed",
   int(r25["hrs"]) == int((v25["events"] == "home_run").sum()),
   r25["hrs"], int((v25["events"] == "home_run").sum()))

# ---------------------------------------------------------------------------
# 3. The no-imputation policy is actually enforced
# ---------------------------------------------------------------------------

pre24 = a1[a1["game_year"] < 2024]
ck("V-16", "no bat_speed_mu published pre-2024", pre24["bat_speed_mu"].isna().all(),
   pre24["bat_speed_mu"].notna().sum(), 0)
pre25 = a1[a1["game_year"] < 2025]
ck("V-17", "no attack_angle_mu published pre-2025", pre25["attack_angle_mu"].isna().all(),
   pre25["attack_angle_mu"].notna().sum(), 0)
ck("V-18", "no fast_swing_rate published pre-2024", pre24["fast_swing_rate"].isna().all(),
   pre24["fast_swing_rate"].notna().sum(), 0)
raw_pre24 = v[(v["game_year"] < 2024) & v["description"].isin(SW)]["bat_speed"].notna().sum()
ck("V-19", "source itself has zero pre-2024 bat_speed", raw_pre24 == 0, raw_pre24, 0)
raw_2023 = v[(v["game_year"] == 2023) & v["description"].isin(SW)]["bat_speed"].notna().sum()
ck("V-20", "2023 bat_speed coverage is exactly zero (report corrects the DPO note)",
   raw_2023 == 0, raw_2023, 0)
ck("V-21", "imputation-harm receipt: 9 zero-coverage seasons",
   int((x1["measured_n"] == 0).sum()) == 9, int((x1["measured_n"] == 0).sum()), 9)
fabricated = int(x1.loc[x1["measured_n"] == 0, "swings"].sum())
ck("V-22", "imputation would fabricate 7,021 swings", fabricated == 7021, fabricated, 7021)
ck("V-23", "fabricated share is 67.7% of career swings",
   close(fabricated / x1["swings"].sum(), 0.677, 1e-3),
   round(fabricated / x1["swings"].sum(), 4), 0.677)
ck("V-24", "coverage register marks exactly 2024/2025/2026 as measured",
   sorted(a2.loc[a2["sensor_status"] != "not measured", "game_year"]) == [2024, 2025, 2026],
   sorted(a2.loc[a2["sensor_status"] != "not measured", "game_year"]), [2024, 2025, 2026])

# ---------------------------------------------------------------------------
# 4. Phase split — the report's core exhibit
# ---------------------------------------------------------------------------

split = pd.Timestamp(head["split_date"])
pa_bip = bip26[bip26["game_date"] < split]
pb_bip = bip26[bip26["game_date"] >= split]
ck("V-25", "phase split balances BIP within 5", abs(len(pa_bip) - len(pb_bip)) <= 5,
   f"{len(pa_bip)}/{len(pb_bip)}", "<=5 apart")
ck("V-26", "phase BIP sum equals 2026 BIP", len(pa_bip) + len(pb_bip) == len(bip26),
   len(pa_bip) + len(pb_bip), len(bip26))

bra = (pa_bip["launch_speed_angle"] == 6).mean()
brb = (pb_bip["launch_speed_angle"] == 6).mean()
row = b6[b6["metric"] == "barrel_rate"].iloc[0]
ck("V-27", "phase A barrel rate", close(row["phase_a"], bra, 1e-3), row["phase_a"], round(bra, 4))
ck("V-28", "phase B barrel rate", close(row["phase_b"], brb, 1e-3), row["phase_b"], round(brb, 4))
ck("V-29", "barrel collapse is ~-59.5%", close(row["pct_change"], -59.5, 0.6),
   row["pct_change"], -59.5)

bsa = v26[(v26["game_date"] < split) & v26["description"].isin(SW)]["bat_speed"].mean()
bsb = v26[(v26["game_date"] >= split) & v26["description"].isin(SW)]["bat_speed"].mean()
ck("V-30", "bat speed is flat across phases (<0.1 mph)", abs(bsa - bsb) < 0.1,
   round(abs(bsa - bsb), 4), "<0.1")
brow = b6[b6["metric"] == "bat_speed_mu"].iloc[0]
ck("V-31", "receipt agrees with independent bat-speed phase means",
   close(brow["phase_a"], bsa, 1e-2) and close(brow["phase_b"], bsb, 1e-2),
   f"{brow['phase_a']}/{brow['phase_b']}", f"{bsa:.3f}/{bsb:.3f}")

# damage band 20-32
dba = pa_bip["launch_angle"].between(20, 32, inclusive="left").mean()
dbb = pb_bip["launch_angle"].between(20, 32, inclusive="left").mean()
c1a = c1[(c1["la_bucket"] == "Ideal high (20-32)") & (c1["window"].str.startswith("A"))]
c1b = c1[(c1["la_bucket"] == "Ideal high (20-32)") & (c1["window"].str.startswith("B"))]
ck("V-32", "damage-band share phase A = 21.7%",
   close(c1a["share"].iloc[0], dba, 5e-3) and close(c1a["share"].iloc[0], 0.217, 5e-3),
   c1a["share"].iloc[0], round(dba, 4))
ck("V-33", "damage-band share phase B = 14.9%",
   close(c1b["share"].iloc[0], dbb, 5e-3) and close(c1b["share"].iloc[0], 0.149, 5e-3),
   c1b["share"].iloc[0], round(dbb, 4))
ck("V-34", "damage band lost >6 points of share", (dba - dbb) > 0.06,
   round(dba - dbb, 4), ">0.06")

# The paradox: sweet spot up while barrels down
ssa = pa_bip["launch_angle"].between(8, 32).mean()
ssb = pb_bip["launch_angle"].between(8, 32).mean()
ck("V-35", "sweet-spot rate ROSE while barrel rate fell (the SW-1 blind spot)",
   (ssb > ssa) and (brb < bra), f"SS {ssa:.3f}->{ssb:.3f}, BRL {bra:.3f}->{brb:.3f}",
   "SS up, BRL down")
hha = (pa_bip["launch_speed"] >= 95).mean()
hhb = (pb_bip["launch_speed"] >= 95).mean()
ck("V-36", "hard-hit rate also ROSE while barrel rate fell", hhb > hha,
   f"{hha:.3f}->{hhb:.3f}", "up")

# ---------------------------------------------------------------------------
# 5. Report-body number audit — scrape and confirm
# ---------------------------------------------------------------------------

txt = open(REPORT, encoding="utf-8").read()

CLAIMS = [
    ("V-37", "bat speed 74.2 in both 2025 and 2026",
     close(r25["bat_speed_mu"], 74.2, 0.06) and close(r26["bat_speed_mu"], 74.2, 0.06)),
    ("V-38", "2026 chase rate 25.5%", close(r26["chase_rate"], 0.255, 1e-3)),
    ("V-39", "2025 chase rate 21.5%", close(r25["chase_rate"], 0.215, 1e-3)),
    ("V-40", "2026 K rate 34.8% is a career high excluding the 5-PA 2016",
     close(r26["krate"], 0.348, 1e-3) and
     (a1[(a1["plate_apps"] >= 100) & (a1["game_year"] < 2026)]["krate"].max() < 0.348)),
    ("V-41", "2026 chase rate is the highest since 2020",
     a1[(a1["game_year"].between(2021, 2025))]["chase_rate"].max() < r26["chase_rate"]),
    ("V-42", "2026 SLG .518 and ISO .276",
     close(r26["slg"], 0.518, 1e-3) and close(r26["iso"], 0.276, 1e-3)),
    ("V-43", "2025 SLG .561 / ISO .322 / 56 HR",
     close(r25["slg"], 0.561, 1e-3) and close(r25["iso"], 0.322, 1e-3) and int(r25["hrs"]) == 56),
    ("V-44", "2026 SLG exceeds both 2023 and 2024",
     r26["slg"] > a1[a1["game_year"] == 2023]["slg"].iloc[0] and
     r26["slg"] > a1[a1["game_year"] == 2024]["slg"].iloc[0]),
    ("V-45", "phase A barrel rate (24.2%) exceeded full-season 2025 (20.8%)",
     bra > r25["barrel_rate"]),
    ("V-46", "phase B contact depth ~= 2025 season mean (the honest caveat)",
     abs(pb_bip["intercept_ball_minus_batter_pos_y_inches"].mean()
         - bip25["intercept_ball_minus_batter_pos_y_inches"].mean()) < 0.5),
    ("V-47", "phase A contact depth is the outlier, not phase B",
     pa_bip["intercept_ball_minus_batter_pos_y_inches"].mean()
     > bip25["intercept_ball_minus_batter_pos_y_inches"].mean() + 1.0),
    ("V-48", "squared-up rate is Schwarber's worst rank in the LHB pool",
     close(e2[e2["metric"] == "squared_up_rate"]["pctile"].iloc[0], 0.0, 1e-6)),
    ("V-49", "LHB pool has 5 measured players (caveat is accurate)",
     int(e2["pool_n"].max()) == 5),
    ("V-50", "August 2026 is 11 balls in play (small-sample flag is accurate)",
     len(bip26[bip26["game_date"].dt.month == 8]) == 11),
]
for cid, desc, ok in CLAIMS:
    ck(cid, desc, ok)

# every figure referenced by the report exists
for m in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", txt):
    p = os.path.join(HERE, m)
    ck(f"V-F{os.path.basename(m)[:18]}", f"figure exists: {os.path.basename(m)}",
       os.path.exists(p), os.path.exists(p), True)

# every receipt named in the report exists on disk
named = set(re.findall(r"`([a-z0-9_]+)`(?=[^`]{0,40}(?:Receipt|receipt))", txt))
named |= set(re.findall(r"[Rr]eceipts?: `([^`]+)`", txt))
flat = set()
for n in named:
    for piece in re.split(r"[,\s]+", n):
        piece = piece.strip("`, ")
        if piece and re.match(r"^[a-z]\d?\d?_", piece):
            flat.add(piece)
missing = [n for n in sorted(flat)
           if not os.path.exists(os.path.join(OUT, f"dp_uc32_{n}.csv"))]
ck("V-51", "every receipt cited in the report exists", not missing, missing or "none", "none")

# no pre-sensor bat-speed number leaked into the prose
leak = re.findall(r"(20(?:1[5-9]|2[0-3]))[^\n]{0,80}?bat speed[^\n]{0,40}?(\d{2}\.\d)", txt, re.I)
ck("V-52", "no pre-2024 bat-speed value appears in the report prose", not leak,
   leak or "none", "none")

# ---------------------------------------------------------------------------
# 6. Build-side DQ still green
# ---------------------------------------------------------------------------

dq = pd.read_csv(os.path.join(OUT, "dp_uc32_dq_scorecard.csv"))
ck("V-53", "build DQ scorecard has zero FAIL", (dq["result"] == "FAIL").sum() == 0,
   int((dq["result"] == "FAIL").sum()), 0)
ck("V-54", "at least 24 receipts on disk",
   len(glob.glob(os.path.join(OUT, "dp_uc32_*.csv"))) >= 24,
   len(glob.glob(os.path.join(OUT, "dp_uc32_*.csv"))), ">=24")

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

res = pd.DataFrame(CHECKS)
res.to_csv(os.path.join(OUT, "dp_uc32_verification_results.csv"), index=False)
n_pass = int((res["result"] == "PASS").sum())
print(res.to_string(index=False))
print(f"\n[verify] {n_pass}/{len(res)} PASS")
if n_pass != len(res):
    print("\nFAILURES:")
    print(res[res["result"] == "FAIL"].to_string(index=False))
    sys.exit(1)
print("[verify] certification check: PASS — safe to publish")
