"""
INDEPENDENT VERIFICATION — UC #30 / uc-pps-024 / dp_uc29
=========================================================
Recomputes every headline number published in
`dp_uc29_kilian_acquisition_read_report.md` from the RAW parquet via a
SEPARATE CODE PATH (no import of the build module, no reuse of its helper
functions), then asserts against both (a) the value printed in the report and
(b) the CSV receipt the build wrote.

The point is to catch a shared-bug failure mode: if the build and the check
used the same function, a wrong function would agree with itself. Here the
rates are recomputed with plain boolean masks written independently.

Run:  python dp_uc29_verification.py
"""
from __future__ import annotations
import os
import sys
import pathlib
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"

_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    "/sessions/friendly-determined-ptolemy/mnt/MLB/data/phillies",
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies",
]
PHIL = next((p for p in _CANDIDATES if p and os.path.isdir(p)), None)
OPP = os.path.join(os.path.dirname(PHIL), "opponents")

KILIAN = 668873
SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout",
          "swinging_strike", "swinging_strike_blocked"]

RESULTS = []


def check(name, got, want, tol=0.0015):
    if want is None or got is None or (isinstance(got, float) and np.isnan(got)):
        ok = False
    elif isinstance(want, str) or isinstance(got, str):
        ok = str(got) == str(want)
    else:
        ok = abs(float(got) - float(want)) <= tol
    RESULTS.append((name, got, want, ok))
    return ok


# ---------------------------------------------------------------------------
# Independent load — deliberately NOT the build's load_kilian()
# ---------------------------------------------------------------------------
raw = pd.read_parquet(os.path.join(OPP, "kilian.parquet"))
d = raw[(raw["pitcher"] == KILIAN) & (raw["game_type"] == "R")].copy()
d = d.drop_duplicates(subset=["game_pk", "at_bat_number", "pitch_number"])
for c in ["plate_x", "plate_z", "sz_top", "sz_bot", "launch_speed", "zone",
          "strikes", "balls", "pitch_number", "release_speed", "pfx_x", "pfx_z",
          "estimated_woba_using_speedangle", "inning", "bat_score", "fld_score"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")

cur = d[d.game_year == 2026]
pri = d[d.game_year.isin([2022, 2023, 2024])]

# TRACKED populations — exclude untracked `automatic_ball` rows (pitch-timer
# violations: no pitch thrown, so pitch_name/zone/plate_x are null). Used for
# every pitch-mix / usage / location denominator. See build docstring.
TR = cur[cur["pitch_name"].notna()]
TRP = pri[pri["pitch_name"].notna()]


# ---------------------------------------------------------------------------
# Independent metric primitives (plain masks — no shared code with the build)
# ---------------------------------------------------------------------------
def n_pa(x):
    return int((~x["events"].isna() & (x["events"] != "pickoff_1b")).sum())


def k_rate(x):
    return x["events"].isin(["strikeout", "strikeout_double_play"]).sum() / n_pa(x)


def bb_rate(x):
    return (x["events"] == "walk").sum() / n_pa(x)


def whiff(x):
    sw = x["description"].isin(SWINGS).sum()
    return x["description"].isin(WHIFFS).sum() / sw if sw else np.nan


def chase(x):
    ooz = x[x["zone"] > 9]
    return ooz["description"].isin(SWINGS).sum() / len(ooz) if len(ooz) else np.nan


def zone_rate(x):
    return (x["zone"] <= 9).sum() / len(x)


def putaway(x):
    two = (x["strikes"] == 2).sum()
    return x["events"].isin(["strikeout", "strikeout_double_play"]).sum() / two


def fps(x):
    f = x[x["pitch_number"] == 1]
    return (f["type"] != "B").sum() / len(f)


def hardhit(x):
    b = x[x["type"] == "X"]
    return (b["launch_speed"] >= 95).sum() / len(b) if len(b) else np.nan


def ev(x):
    return x.loc[x["type"] == "X", "launch_speed"].mean()


def xwc(x):
    """xwOBAcon — BIP-only, per the uc-pps-021 O1 hardening."""
    b = x[x["type"] == "X"]
    return b["estimated_woba_using_speedangle"].mean() if len(b) else np.nan


def ba(x):
    ab = (~x["events"].isna() & ~x["events"].isin(
        ["pickoff_1b", "walk", "intent_walk", "hit_by_pitch", "sac_fly", "sac_bunt"])).sum()
    return x["events"].isin(["single", "double", "triple", "home_run"]).sum() / ab


print("=" * 76)
print("dp_uc29 INDEPENDENT VERIFICATION — uc-pps-024 / UC #30")
print("=" * 76)

# --- A. entity lock / integrity ---------------------------------------------
check("A1 entity lock: single pitcher id", int(d["pitcher"].nunique()), 1)
check("A2 entity lock: id == 668873", int(d["pitcher"].iloc[0]), KILIAN)
check("A3 regular season only", ";".join(sorted(d["game_type"].unique())), "R")
check("A4 zero duplicate pitches",
      int(d.duplicated(["game_pk", "at_bat_number", "pitch_number"]).sum()), 0)
check("A5 2025 absent (true gap)", int((d["game_year"] == 2025).sum()), 0)
check("A6 total pitches after filter", len(d), 1271)
check("A7 2026 tier pitches", len(cur), 736)
check("A8 prior tier pitches", len(pri), 535)
check("A9 2026 PA", n_pa(cur), 193)
check("A10 prior PA", n_pa(pri), 138)
check("A11 2026 outings", int(cur["game_pk"].nunique()), 45)
check("A12 prior outings", int(pri["game_pk"].nunique()), 8)
check("A13 cache max date", str(d["game_date"].max())[:10], "2026-08-01")

# --- B. headline conversion numbers (report "Bottom line" + era table) -------
check("B1 prior K%", k_rate(pri), 0.152)
check("B2 2026 K%", k_rate(cur), 0.275)
check("B3 prior BB%", bb_rate(pri), 0.138)
check("B4 2026 BB%", bb_rate(cur), 0.093)
check("B5 prior whiff", whiff(pri), 0.177)
check("B6 2026 whiff", whiff(cur), 0.288)
check("B7 prior chase", chase(pri), 0.211)
check("B8 2026 chase", chase(cur), 0.320)
check("B9 prior putaway", putaway(pri), 0.136)
check("B10 2026 putaway", putaway(cur), 0.243)
check("B11 prior 1st-pitch strike", fps(pri), 0.587)
check("B12 2026 1st-pitch strike", fps(cur), 0.632)
check("B13 prior hard-hit", hardhit(pri), 0.462)
check("B14 2026 hard-hit", hardhit(cur), 0.356)
check("B15 prior avg EV", ev(pri), 89.8, tol=0.06)
check("B16 2026 avg EV", ev(cur), 85.3, tol=0.06)
check("B17 prior xwOBAcon (BIP-only)", xwc(pri), 0.370, tol=0.002)
check("B18 2026 xwOBAcon (BIP-only)", xwc(cur), 0.346, tol=0.002)
check("B19 2026 BA against", ba(cur), 0.231)
check("B20 2026 zone rate (STRICT, tracked pop)", zone_rate(cur[cur['pitch_name'].notna()]), 0.481)
check("B21 2026 BIP count", int((cur["type"] == "X").sum()), 118)

# --- C. velocity / arsenal ---------------------------------------------------
ff_cur = cur[cur["pitch_name"] == "4-Seam Fastball"]
ff_pri = pri[pri["pitch_name"] == "4-Seam Fastball"]
check("C1 prior FF velo", ff_pri["release_speed"].mean(), 93.9, tol=0.06)
check("C2 2026 FF velo", ff_cur["release_speed"].mean(), 96.8, tol=0.06)
check("C3 FF velo gain", ff_cur["release_speed"].mean() - ff_pri["release_speed"].mean(),
      2.9, tol=0.06)
check("C4 2026 FF usage (tracked)", len(ff_cur) / len(TR), 0.496)
check("C5 prior FF usage (tracked)", len(ff_pri) / len(TRP), 0.323)
check("C6 2026 KC usage (tracked)", (TR["pitch_name"] == "Knuckle Curve").sum() / len(TR), 0.247)
check("C7 prior KC usage (tracked)", (TRP["pitch_name"] == "Knuckle Curve").sum() / len(TRP), 0.096)
check("C8 prior cutter usage (tracked)", (TRP["pitch_name"] == "Cutter").sum() / len(TRP), 0.276)
check("C9 2026 cutter absent", int((cur["pitch_name"] == "Cutter").sum()), 0)
check("C10 2026 arsenal size", int(cur["pitch_name"].nunique()), 4)
check("C11 prior arsenal size", int(pri["pitch_name"].nunique()), 6)
check("C12 2026 FF IVB in", ff_cur["pfx_z"].mean() * 12, 15.7, tol=0.06)
check("C13 2026 KC IVB in",
      cur.loc[cur["pitch_name"] == "Knuckle Curve", "pfx_z"].mean() * 12, -14.8, tol=0.06)
check("C14 2026 KC whiff", whiff(cur[cur["pitch_name"] == "Knuckle Curve"]), 0.423)
check("C15 2026 SL whiff", whiff(cur[cur["pitch_name"] == "Slider"]), 0.426)
check("C16 2026 FF whiff", whiff(ff_cur), 0.192)
check("C17 2026 SL home runs", int((cur[cur["pitch_name"] == "Slider"]["events"] == "home_run").sum()), 3)
check("C18 2026 total home runs", int((cur["events"] == "home_run").sum()), 5)

# --- D. platoon --------------------------------------------------------------
L = cur[cur["stand"] == "L"]
R = cur[cur["stand"] == "R"]
TL = L[L["pitch_name"].notna()]
TRr = R[R["pitch_name"].notna()]
check("D1 vs LHH PA", n_pa(L), 110)
check("D2 vs RHH PA", n_pa(R), 83)
check("D3 vs LHH K%", k_rate(L), 0.245)
check("D4 vs RHH K%", k_rate(R), 0.313)
check("D5 vs LHH BB%", bb_rate(L), 0.082)
check("D6 vs RHH BB%", bb_rate(R), 0.108)
check("D7 vs LHH whiff", whiff(L), 0.229)
check("D8 vs RHH whiff", whiff(R), 0.375)
check("D9 vs LHH chase", chase(L), 0.335)
check("D10 vs RHH chase", chase(R), 0.299)
check("D11 vs LHH hard-hit", hardhit(L), 0.315)
check("D12 vs RHH hard-hit", hardhit(R), 0.422)
check("D13 vs LHH avg EV", ev(L), 84.4, tol=0.06)
check("D14 vs RHH avg EV", ev(R), 86.8, tol=0.06)
check("D15 vs LHH xwOBAcon", xwc(L), 0.309, tol=0.002)
check("D16 vs RHH xwOBAcon", xwc(R), 0.410, tol=0.002)
check("D17 vs LHH home runs — ZERO", int((L["events"] == "home_run").sum()), 0)
check("D18 vs RHH home runs — ALL FIVE", int((R["events"] == "home_run").sum()), 5)
check("D19 vs LHH BIP", int((L["type"] == "X").sum()), 73)
check("D20 vs RHH BIP", int((R["type"] == "X").sum()), 45)
check("D21 vs LHH putaway", putaway(L), 0.201)
check("D22 vs RHH putaway", putaway(R), 0.310)
check("D23 vs LHH 1st-pitch strike", fps(L), 0.636)
check("D24 vs RHH 1st-pitch strike", fps(R), 0.627)
check("D25 vs LHH FF usage (tracked)", (TL["pitch_name"] == "4-Seam Fastball").sum() / len(TL), 0.527)
check("D26 vs LHH KC usage (tracked)", (TL["pitch_name"] == "Knuckle Curve").sum() / len(TL), 0.317)
check("D27 vs RHH FF usage (tracked)", (TRr["pitch_name"] == "4-Seam Fastball").sum() / len(TRr), 0.452)
check("D28 vs RHH SL usage (tracked)", (TRr["pitch_name"] == "Slider").sum() / len(TRr), 0.200)
check("D29 vs RHH SI usage (tracked)", (TRr["pitch_name"] == "Sinker").sum() / len(TRr), 0.197)
check("D30 vs RHH KC usage (tracked)", (TRr["pitch_name"] == "Knuckle Curve").sum() / len(TRr), 0.151)
check("D31 vs RHH KC whiff", whiff(R[R["pitch_name"] == "Knuckle Curve"]), 0.667)
check("D32 vs LHH KC whiff", whiff(L[L["pitch_name"] == "Knuckle Curve"]), 0.350)

check("D33 untracked automatic_ball rows, 2026", int(cur["pitch_name"].isna().sum()), 8)
check("D34 all untracked rows are automatic_ball",
      ";".join(sorted(cur[cur["pitch_name"].isna()]["description"].unique())), "automatic_ball")
check("D35 tracked pitch count 2026", len(TR), 728)
check("D36 launch_speed present on non-BIP foul rows",
      int(((cur["launch_speed"].notna()) & (cur["type"] != "X")).sum()), 114)

# --- E. NEW KPI: Slider Finish Rate -----------------------------------------
sl_r = R[R["pitch_name"] == "Slider"].copy()
glove = sl_r[sl_r["plate_x"] > 0.15]
arm = sl_r[sl_r["plate_x"] < -0.15]
mid = sl_r[(sl_r["plate_x"] >= -0.15) & (sl_r["plate_x"] <= 0.15)]
check("E1 SL vs RHH total", len(sl_r), 61)
check("E2 SL glove-side thrown", len(glove), 32)
check("E3 SL arm-side thrown", len(arm), 15)
check("E4 SL middle thrown", len(mid), 14)
check("E5 SL glove-side share", len(glove) / len(sl_r), 0.525)
check("E6 SL arm-side share", len(arm) / len(sl_r), 0.246)
check("E7 SL glove-side whiff", whiff(glove), 0.571)
check("E8 SL arm-side whiff", whiff(arm), 0.300)
check("E9 SL glove-side avg EV", ev(glove), 78.4, tol=0.06)
check("E10 SL arm-side avg EV", ev(arm), 98.4, tol=0.06)
check("E11 SL glove-side HR — ZERO", int((glove["events"] == "home_run").sum()), 0)
check("E12 SL arm-side HR — THREE", int((arm["events"] == "home_run").sum()), 3)
check("E13 SL glove-side BIP", int((glove["type"] == "X").sum()), 4)
check("E14 SL arm-side BIP", int((arm["type"] == "X").sum()), 5)
# vertical half (report cites this too)
sl_r["half"] = np.where(
    sl_r["plate_z"] > sl_r["sz_bot"] + (sl_r["sz_top"] - sl_r["sz_bot"]) * 0.5,
    "upper", "lower")
lo, up = sl_r[sl_r["half"] == "lower"], sl_r[sl_r["half"] == "upper"]
check("E15 SL lower-half thrown", len(lo), 47)
check("E16 SL upper-half thrown", len(up), 14)
check("E17 SL lower-half avg EV (BIP-only)", ev(lo), 86.8, tol=0.06)
check("E18 SL upper-half avg EV (BIP-only)", ev(up), 99.1, tol=0.06)
check("E19 SL lower-half HR", int((lo["events"] == "home_run").sum()), 1)
check("E20 SL upper-half HR", int((up["events"] == "home_run").sum()), 2)

# --- F. NEW KPI: Fastball Elevation Rate ------------------------------------
def thirds(x):
    x = x.dropna(subset=["plate_z", "sz_top", "sz_bot"]).copy()
    h = x["sz_top"] - x["sz_bot"]
    x["t"] = np.select([x["plate_z"] > x["sz_bot"] + h * 2 / 3,
                        x["plate_z"] < x["sz_bot"] + h / 3],
                       ["upper", "lower"], default="middle")
    return x


ffl, ffr = thirds(ff_cur[ff_cur["stand"] == "L"]), thirds(ff_cur[ff_cur["stand"] == "R"])
check("F1 FF vs LHH upper n", int((ffl["t"] == "upper").sum()), 118)
check("F2 FF vs LHH lower n", int((ffl["t"] == "lower").sum()), 54)
check("F3 FF vs LHH elevation rate", (ffl["t"] == "upper").sum() / len(ffl), 0.529)
check("F4 FF vs LHH lower-third share", (ffl["t"] == "lower").sum() / len(ffl), 0.242)
check("F5 FF vs LHH upper EV", ev(ffl[ffl["t"] == "upper"]), 81.0, tol=0.06)
check("F6 FF vs LHH lower EV", ev(ffl[ffl["t"] == "lower"]), 97.7, tol=0.06)
check("F7 FF vs RHH upper n", int((ffr["t"] == "upper").sum()), 64)
check("F8 FF vs RHH lower n", int((ffr["t"] == "lower").sum()), 46)
check("F9 FF vs RHH elevation rate", (ffr["t"] == "upper").sum() / len(ffr), 0.464)
check("F10 FF vs RHH lower-third share", (ffr["t"] == "lower").sum() / len(ffr), 0.333)
check("F11 FF vs RHH upper EV", ev(ffr[ffr["t"] == "upper"]), 85.0, tol=0.06)
check("F12 FF vs RHH lower EV", ev(ffr[ffr["t"] == "lower"]), 94.3, tol=0.06)
check("F13 FF vs LHH upper whiff", whiff(ffl[ffl["t"] == "upper"]), 0.188)
check("F14 FF vs RHH upper whiff", whiff(ffr[ffr["t"] == "upper"]), 0.324)

# --- G. sinker vs LHH (the second recommendation) ---------------------------
si_l = L[L["pitch_name"] == "Sinker"]
check("G1 SI vs LHH thrown", len(si_l), 33)
check("G2 SI vs LHH usage", len(si_l) / len(L), 0.077)
check("G3 SI vs LHH BIP", int((si_l["type"] == "X").sum()), 10)
check("G4 SI vs LHH avg EV", ev(si_l), 88.3, tol=0.06)
check("G5 SI vs LHH hard-hit", hardhit(si_l), 0.500)
check("G6 SI vs LHH BIP at 97+ mph", int((si_l.loc[si_l["type"] == "X", "launch_speed"] >= 97).sum()), 5)
si_r = R[R["pitch_name"] == "Sinker"]
check("G7 SI vs RHH avg EV", ev(si_r), 80.9, tol=0.06)
check("G8 SI vs RHH xwOBAcon", xwc(si_r), 0.232, tol=0.002)
check("G9 SI vs RHH HR — ZERO", int((si_r["events"] == "home_run").sum()), 0)

# --- H. damage log -----------------------------------------------------------
hr = cur[cur["events"] == "home_run"]
check("H1 all HR vs RHH", int((hr["stand"] == "R").sum()), 5)
check("H2 all HR on arm side (plate_x < -0.15)", int((hr["plate_x"] < -0.15).sum()), 5)
check("H3 HR by slider", int((hr["pitch_name"] == "Slider").sum()), 3)
check("H4 HR date window start", str(hr["game_date"].min())[:10], "2026-04-11")
check("H5 HR date window end", str(hr["game_date"].max())[:10], "2026-05-29")

# --- I. deployment / leash ---------------------------------------------------
cs = cur.sort_values(["game_pk", "at_bat_number", "pitch_number"])
entry = cs.groupby("game_pk", as_index=False).head(1)
outing = cur.groupby("game_pk").agg(p=("pitch_number", "size"),
                                    bf=("at_bat_number", "nunique"),
                                    inn=("inning", "nunique"))
check("I1 outings", len(outing), 45)
check("I2 mean pitches/outing", outing["p"].mean(), 16.4, tol=0.06)
check("I3 mean BF/outing", outing["bf"].mean(), 4.29, tol=0.006)
check("I4 one-inning outings", int((outing["inn"] == 1).sum()), 37)
check("I5 two-inning outings", int((outing["inn"] == 2).sum()), 8)
check("I6 longest outing pitches", int(outing["p"].max()), 35)
check("I7 max batters faced", int(outing["bf"].max()), 7)
check("I8 entries in 9th", int((entry["inning"] == 9).sum()), 20)
check("I9 entries in 8th", int((entry["inning"] == 8).sum()), 12)
ed = entry["fld_score"] - entry["bat_score"]
check("I10 entries with 1-run lead", int((ed == 1).sum()), 2)
check("I11 9th-inning entries up 2+", int(((entry["inning"] == 9) & (ed >= 2)).sum()), 13)
check("I12 inherited-runner entries",
      int(entry[["on_1b", "on_2b", "on_3b"]].notna().any(axis=1).sum()), 13)
rest = cur.groupby("game_pk")["pitcher_days_since_prev_game"].max()
check("I13 outings on 1 day rest", int((rest == 1).sum()), 8)
check("I14 outings on 2 days rest", int((rest == 2).sum()), 14)

cq = cur.copy()
cq["seq"] = cq.groupby("game_pk")["at_bat_number"].transform(lambda s: s.rank(method="dense"))
b13 = cq[cq["seq"] <= 3]
b45 = cq[(cq["seq"] > 3) & (cq["seq"] <= 5)]
check("I15 BF1-3 whiff", whiff(b13), 0.303)
check("I16 BF4-5 whiff", whiff(b45), 0.266)
check("I17 BF1-3 avg EV", ev(b13), 84.3, tol=0.06)
check("I18 BF4-5 avg EV", ev(b45), 88.1, tol=0.06)
check("I19 BF1-3 PA", n_pa(b13), 132)
check("I20 BF4-5 PA", n_pa(b45), 49)
check("I21 BF1-3 FF velo",
      b13.loc[b13["pitch_name"] == "4-Seam Fastball", "release_speed"].mean(), 96.7, tol=0.06)
check("I22 BF4-5 FF velo",
      b45.loc[b45["pitch_name"] == "4-Seam Fastball", "release_speed"].mean(), 97.0, tol=0.06)

# --- J. stability (no fade) --------------------------------------------------
cm = cur.copy()
cm["mo"] = pd.to_datetime(cm["game_date"]).dt.to_period("M").astype(str)
mv = cm[cm["pitch_name"] == "4-Seam Fastball"].groupby("mo")["release_speed"].mean()
check("J1 Apr FF velo", mv.get("2026-04"), 96.8, tol=0.06)
check("J2 May FF velo", mv.get("2026-05"), 96.5, tol=0.06)
check("J3 Jun FF velo", mv.get("2026-06"), 97.1, tol=0.06)
check("J4 Jul FF velo", mv.get("2026-07"), 96.8, tol=0.06)
multi = outing[outing["inn"] > 1].index
mm = cur[cur["game_pk"].isin(multi)].copy()
mm["ord"] = mm.groupby("game_pk")["inning"].transform(lambda s: s.rank(method="dense"))
mmf = mm[mm["pitch_name"] == "4-Seam Fastball"]
check("J5 2-inning: 1st inning FF velo", mmf[mmf["ord"] == 1]["release_speed"].mean(), 96.8, tol=0.06)
check("J6 2-inning: 2nd inning FF velo", mmf[mmf["ord"] == 2]["release_speed"].mean(), 96.2, tol=0.06)

# --- K. count usage cited in the battery card -------------------------------
def usage(x, pitch):
    return (x["pitch_name"] == pitch).sum() / len(x)


check("K1 LHH 2-strike KC usage (tracked)", usage(TL[TL["strikes"] == 2], "Knuckle Curve"), 0.366)
check("K2 RHH 2-strike KC usage (tracked)", usage(TRr[TRr["strikes"] == 2], "Knuckle Curve"), 0.333)
check("K3 RHH 0-0 sinker usage (tracked)",
      usage(TRr[(TRr["balls"] == 0) & (TRr["strikes"] == 0)], "Sinker"), 0.244)
check("K4 LHH 0-0 sinker usage (tracked)",
      usage(TL[(TL["balls"] == 0) & (TL["strikes"] == 0)], "Sinker"), 0.083)
check("K5 RHH ahead/even slider usage (tracked)",
      usage(TRr[(TRr["balls"] <= TRr["strikes"]) & ~((TRr["balls"] == 0) & (TRr["strikes"] == 0))
              & (TRr["strikes"] != 2)], "Slider"), 0.329)
check("K6 LHH 0-0 FF usage (tracked)",
      usage(TL[(TL["balls"] == 0) & (TL["strikes"] == 0)], "4-Seam Fastball"), 0.550)
check("K7 RHH 0-0 FF usage (tracked)",
      usage(TRr[(TRr["balls"] == 0) & (TRr["strikes"] == 0)], "4-Seam Fastball"), 0.524)

# --- L. receipts agree with the independent recompute ------------------------
def receipt(fn):
    p = OUT / fn
    return pd.read_csv(p) if p.exists() else None


plat = receipt("dp_uc29_platoon.csv")
if plat is not None:
    check("L1 receipt platoon LHH xwOBAcon == recompute",
          float(plat[plat["stand"] == "L"]["xwobacon"].iloc[0]), round(xwc(L), 3), tol=0.0011)
    check("L2 receipt platoon RHH xwOBAcon == recompute",
          float(plat[plat["stand"] == "R"]["xwobacon"].iloc[0]), round(xwc(R), 3), tol=0.0011)
    check("L3 receipt platoon RHH whiff == recompute",
          float(plat[plat["stand"] == "R"]["whiff_rate"].iloc[0]), round(whiff(R), 3), tol=0.0011)
sfr = receipt("dp_uc29_slider_finish.csv")
if sfr is not None:
    row = sfr[(sfr["stand"] == "R") & (sfr["h_side"] == "arm side")].iloc[0]
    check("L4 receipt SFR arm-side HR == recompute", int(row["hr"]), 3)
    check("L5 receipt SFR arm-side pitches == recompute", int(row["pitches"]), 15)
fer_r = receipt("dp_uc29_fastball_elevation.csv")
if fer_r is not None:
    row = fer_r[(fer_r["stand"] == "L") & (fer_r["v_third"] == "lower")].iloc[0]
    check("L6 receipt FER LHH lower EV == recompute", float(row["avg_ev"]), 97.7, tol=0.06)
rcd = receipt("dp_uc29_role_conversion_delta.csv")
if rcd is not None:
    check("L7 receipt RCD: all 10 KPIs improved", int(rcd["improved"].sum()), 10)
    check("L8 receipt RCD K% delta == recompute",
          float(rcd[rcd["kpi"] == "K%"]["delta"].iloc[0]),
          round(k_rate(cur) - k_rate(pri), 3), tol=0.0011)
    check("L9 receipt RCD xwOBAcon is BIP-only (matches hardened recompute)",
          float(rcd[rcd["kpi"] == "xwOBAcon"]["current_2026_relief"].iloc[0]),
          round(xwc(cur), 3), tol=0.0011)
dq = receipt("dp_uc29_dq_scorecard.csv")
check("L10 DQ scorecard emitted", dq is not None and len(dq) > 0, True)
check("L11 no DQ FAIL rows",
      int(dq["status"].astype(str).str.startswith("FAIL").sum()) if dq is not None else 1, 0)
expected_files = [
    "dp_uc29_era_summary.csv", "dp_uc29_season_log.csv", "dp_uc29_arsenal_by_era.csv",
    "dp_uc29_arsenal_2026.csv", "dp_uc29_role_conversion_delta.csv", "dp_uc29_platoon.csv",
    "dp_uc29_pitch_by_hand.csv", "dp_uc29_count_usage.csv", "dp_uc29_slider_finish.csv",
    "dp_uc29_fastball_elevation.csv", "dp_uc29_slider_vertical_half.csv",
    "dp_uc29_fps_by_hand.csv", "dp_uc29_damage_log.csv", "dp_uc29_outing_log.csv",
    "dp_uc29_deployment.csv", "dp_uc29_batter_sequence.csv", "dp_uc29_monthly_arc.csv",
    "dp_uc29_dq_scorecard.csv", "dp_uc29_freshness_manifest.csv",
    "dp_uc29_fig1_arsenal_movement.png", "dp_uc29_fig2_role_conversion.png",
    "dp_uc29_fig3_location_damage.png", "dp_uc29_fig4_deployment.png",
]
for f in expected_files:
    check(f"L12 receipt exists: {f}", (OUT / f).exists(), True)

# ---------------------------------------------------------------------------
passed = sum(1 for *_, ok in RESULTS if ok)
total = len(RESULTS)
print()
for name, got, want, ok in RESULTS:
    if not ok:
        print(f"  FAIL  {name}: got {got!r}, expected {want!r}")
print("-" * 76)
print(f"RESULT: {passed}/{total} checks passed")
print("-" * 76)
if passed == total:
    print("VERDICT: PASS — every published number independently reproduced.")
else:
    print("VERDICT: FAIL — report must not be published until resolved.")
    sys.exit(1)
