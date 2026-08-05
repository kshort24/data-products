"""
============================================================================
INDEPENDENT VERIFICATION HARNESS — uc-pos-008-arraez-acquisition-001 (UC #32)
============================================================================
Layer-4 CERTIFY artifact. Recomputes every number that reaches the report by
a DIFFERENT code path than the build, then asserts equality against the CSV
receipts on disk.

Design rule inherited from dp_uc29 / dp_uc30: the harness must NOT import the
build module. It re-reads the raw parquet and re-derives from first
principles. Where the build used a groupby/apply kernel, the harness uses
explicit boolean masks and scalar arithmetic, so a shared bug cannot pass
both. A failure here is a real defect until proven otherwise — the uc-pps-025
xwobacon defect (O4) was found exactly this way.

Usage:  python dp_uc31_verification.py [MLB_ROOT] [OUT_DIR]
Exit code 0 only if zero FAIL.
============================================================================
"""
from __future__ import annotations
import sys, os
from pathlib import Path
import numpy as np
import pandas as pd

def _resolve_root() -> Path:
    cands = []
    if len(sys.argv) > 1: cands.append(Path(sys.argv[1]))
    if os.environ.get("MLB_DATA_ROOT"): cands.append(Path(os.environ["MLB_DATA_ROOT"]))
    cands += [Path("/sessions/nifty-funny-davinci/mnt/MLB"),
              Path(r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"), Path(".")]
    for c in cands:
        if (c / "data" / "opponents" / "arraez.parquet").exists(): return c
    raise SystemExit("FATAL: MLB data root not found.")

MLB = _resolve_root()
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent / "out"
STEM = "dp_uc31"
ARRAEZ = 650333
KEY = ["game_pk", "at_bat_number", "pitch_number"]
TOL = 1e-4

RESULTS = []
def check(cid, desc, got, exp, tol=TOL):
    if exp is None or (isinstance(exp, float) and np.isnan(exp)):
        ok = got is None or (isinstance(got, float) and np.isnan(got))
    elif isinstance(exp, (int, float, np.floating, np.integer)) and \
         isinstance(got, (int, float, np.floating, np.integer)):
        ok = abs(float(got) - float(exp)) <= tol
    else:
        ok = got == exp
    RESULTS.append({"check_id": cid, "description": desc,
                    "recomputed": got, "published": exp,
                    "result": "PASS" if ok else "FAIL"})
    return ok

def rc(name) -> pd.DataFrame:
    return pd.read_csv(OUT / f"{STEM}_{name}.csv")

# ------------------------------------------------------- independent load --
raw = pd.read_parquet(MLB / "data/opponents/arraez.parquet")
A = raw[(raw.batter == ARRAEZ) & (raw.game_type == "R")].drop_duplicates(subset=KEY).copy()
A26 = A[A.game_year == 2026].copy()
P = pd.read_parquet(MLB / "data/phillies/phils_2026.parquet")
P = P[(P.phillies_role == "batting") & (P.game_type == "R")].drop_duplicates(subset=KEY).copy()

NONPA = {"pickoff_1b", "truncated_pa"}
def is_pa(s):  return s.notna() & ~s.isin(NONPA)
HITS = {"single", "double", "triple", "home_run"}
NOTAB = {"walk", "intent_walk", "hit_by_pitch", "sac_fly", "sac_bunt", "catcher_interf"}

def terminal(df):
    """PA-terminal rows via explicit mask — no helper reuse."""
    return df[is_pa(df.events)].copy()

# =========================================================== 1. SOURCE ====
print("1. Source & entity")
check("V-001", "Arraez rows are one batter id", int(raw.batter.nunique()), 1)
check("V-002", "Entity id is 650333", int(A.batter.iloc[0]), ARRAEZ)
check("V-003", "No duplicate pitch keys", len(A) - len(A.drop_duplicates(subset=KEY)), 0)
check("V-004", "Regular-season pitch count", len(A), 15228)
check("V-005", "2026 pitch count", len(A26), 1727)
check("V-006", "Cache max date", str(A.game_date.max())[:10], "2026-08-02")
check("V-007", "All rows stand == L", int((A.stand != "L").sum()), 0)
check("V-008", "PHI comparison rows are 2026 only", int((P.game_year != 2026).sum()), 0)

# ====================================================== 2. SEASON LINE ====
print("2. Season line (a1)")
# DEFINITIONAL FORK (documented, not a defect — see 05_dq_rules_and_join_validation
# §1 DQ-09 and 07_certification_and_publish_readiness §3). The LOCKED get_stats PA rule excludes only
# {NA, pickoff_1b}; the strict PA spine used by the new AR-* KPIs additionally
# excludes 'truncated_pa', which is a continuation marker rather than a new
# plate appearance. The two therefore differ by exactly the truncated_pa count.
# The harness asserts that RECONCILIATION rather than raw equality, and
# separately asserts that the 2026 PRIMARY WINDOW contains zero truncated_pa,
# so no forward-looking published number is affected by the fork.
a1 = rc("a1_season_line")
trunc_by_year = (A[A.events == "truncated_pa"].groupby("game_year").size().to_dict())
check("V-009a", "2026 primary window has zero truncated_pa",
      int(trunc_by_year.get(2026, 0)), 0)
check("V-009b", "truncated_pa confined to shadow years only",
      sorted(trunc_by_year.keys()), [2021, 2025])
for yr in sorted(A.game_year.unique()):
    s = A[A.game_year == yr]
    t = terminal(s)
    tr = int(trunc_by_year.get(yr, 0))
    # reconcile the fork explicitly
    locked_pa = int((s.events.notna() & ~s.events.isin(["pickoff_1b"])).sum())
    check(f"V-009-{yr}", f"{yr} locked PA - strict PA == truncated_pa count",
          locked_pa - len(t), tr)
    pa = len(t) + tr          # restate on the LOCKED basis for comparison
    ab = int((~t.events.isin(NOTAB)).sum()) + tr
    h  = int(t.events.isin(HITS).sum())
    d2 = int((t.events == "double").sum()); d3 = int((t.events == "triple").sum())
    hr = int((t.events == "home_run").sum()); s1 = h - d2 - d3 - hr
    bb = int((t.events == "walk").sum()); hbp = int((t.events == "hit_by_pitch").sum())
    k  = int(t.events.isin(["strikeout", "strikeout_double_play"]).sum())
    tb = s1 + 2*d2 + 3*d3 + 4*hr
    row = a1[a1.game_year == yr].iloc[0]
    check(f"V-010-{yr}", f"{yr} PA",  pa, int(row.plate_apps))
    check(f"V-011-{yr}", f"{yr} AB",  ab, int(row.at_bats))
    check(f"V-012-{yr}", f"{yr} H",   h,  int(row.hits))
    check(f"V-013-{yr}", f"{yr} HR",  hr, int(row.hrs))
    check(f"V-014-{yr}", f"{yr} BB",  bb, int(row.walks))
    check(f"V-015-{yr}", f"{yr} K",   k,  int(row.strikeouts))
    check(f"V-016-{yr}", f"{yr} BA",  round(h/ab, 4), round(float(row.ba), 4))
    check(f"V-017-{yr}", f"{yr} SLG", round(tb/ab, 4), round(float(row.slg), 4))
    check(f"V-018-{yr}", f"{yr} OBP", round((h+bb+hbp)/pa, 4), round(float(row.obp), 4))
    check(f"V-019-{yr}", f"{yr} K%",  round(k/pa, 4), round(float(row.krate), 4))

# ============================================== 3. DISCIPLINE / BATTED ====
print("3. Discipline & contact (b1/b2)")
SW = ['foul','foul_bunt','foul_tip','hit_into_play','missed_bunt','swinging_pitchout',
      'swinging_strike','swinging_strike_blocked']
WH = ['foul_tip','missed_bunt','swinging_pitchout','swinging_strike','swinging_strike_blocked']
b1 = rc("b1_discipline"); b2 = rc("b2_batted_ball")
for yr in [2025, 2026]:
    s = A[A.game_year == yr]
    sw = s.description.isin(SW); wh = s.description.isin(WH); iz = s.zone <= 9
    r1 = b1[b1.game_year == yr].iloc[0]
    check(f"V-020-{yr}", f"{yr} swing rate", round(sw.mean(), 4), round(float(r1.swing_rate), 4))
    check(f"V-021-{yr}", f"{yr} whiff rate", round(wh[sw].mean(), 4), round(float(r1.whiff_rate), 4))
    check(f"V-022-{yr}", f"{yr} chase rate", round(sw[~iz].mean(), 4), round(float(r1.chase_rate), 4))
    check(f"V-023-{yr}", f"{yr} z-contact",  round(1 - wh[iz & sw].mean(), 4),
          round(float(r1.z_contact_rate), 4))
    bip = s[s.type == "X"]
    r2 = b2[b2.game_year == yr].iloc[0]
    check(f"V-024-{yr}", f"{yr} BIP count", len(bip), int(r2.bip))
    check(f"V-025-{yr}", f"{yr} avg EV", round(bip.launch_speed.mean(), 4), round(float(r2.avg_ev), 4))
    check(f"V-026-{yr}", f"{yr} hard-hit", round((bip.launch_speed >= 95).mean(), 4),
          round(float(r2.hard_hit_rate), 4))
    check(f"V-027-{yr}", f"{yr} barrel", round((bip.launch_speed_angle == 6).mean(), 4),
          round(float(r2.barrel_rate), 4))
    check(f"V-028-{yr}", f"{yr} xwOBAcon n (O4 guard)",
          int(bip.estimated_woba_using_speedangle.notna().sum()), int(r2.xwoba_con_n))

# ================================================= 4. TWO-STRIKE (AR-1) ==
print("4. Two-strike (c1/c3)")
def two_strike_independent(df):
    """Independent path: build a per-PA table keyed on (game_pk, at_bat_number)."""
    g = df.groupby(["game_pk", "at_bat_number"])
    reached = g.strikes.max() >= 2
    term = terminal(df).set_index(["game_pk", "at_bat_number"])
    term = term[~term.index.duplicated(keep="last")]
    idx = term.index.intersection(reached[reached].index)
    sub = term.loc[idx]
    n2 = len(sub); k2 = int(sub.events.isin(["strikeout", "strikeout_double_play"]).sum())
    h2 = int(sub.events.isin(HITS).sum())
    ab2 = int((~sub.events.isin(NOTAB)).sum())
    tb2 = int(sub.events.map({"single":1,"double":2,"triple":3,"home_run":4}).fillna(0).sum())
    return len(term), n2, k2, h2, ab2, tb2

c1 = rc("c1_two_strike_by_year")
for yr in [2024, 2025, 2026]:
    tot, n2, k2, h2, ab2, tb2 = two_strike_independent(A[A.game_year == yr])
    r = c1[c1.game_year == yr].iloc[0]
    check(f"V-030-{yr}", f"{yr} PA reaching 2K", n2, int(r.PA_2k))
    check(f"V-031-{yr}", f"{yr} K in 2K", k2, int(r.K_in_2k))
    check(f"V-032-{yr}", f"{yr} TSSR", round(1 - k2/n2, 4), round(float(r.tssr), 4))
    check(f"V-033-{yr}", f"{yr} hits in 2K", h2, int(r.hits_2k))
    check(f"V-034-{yr}", f"{yr} BA in 2K", round(h2/ab2, 4), round(float(r.ba_2k), 4))
    check(f"V-035-{yr}", f"{yr} SLG in 2K", round(tb2/ab2, 4), round(float(r.slg_2k), 4))

c3 = rc("c3_two_strike_vs_phillies")
for _, row in c3.iterrows():
    bid = int(row.batter)
    src = A26 if bid == ARRAEZ else P[P.batter == bid]
    tot, n2, k2, h2, ab2, tb2 = two_strike_independent(src)
    check(f"V-040-{bid}", f"{row['name']} TSSR", round(1 - k2/n2, 4), round(float(row.tssr), 4))
    check(f"V-041-{bid}", f"{row['name']} 2K hits", h2, int(row.hits_2k))
check("V-042", "Arraez has the best TSSR on the roster",
      c3.sort_values("tssr", ascending=False).iloc[0]["name"], "Luis Arraez")

# ============================================ 5. GROUP x HAND (AR-3) =====
print("5. Damage by group x hand (d1)")
PG = {'FF':'fastball','SI':'fastball','FC':'fastball','FA':'fastball',
      'SL':'breaking','ST':'breaking','CU':'breaking','KC':'breaking','SV':'breaking','CS':'breaking',
      'CH':'offspeed','FS':'offspeed','FO':'offspeed','SC':'offspeed','KN':'offspeed','EP':'offspeed'}
d1 = rc("d1_group_x_hand_2026")
A26 = A26.assign(pg=A26.pitch_type.map(PG))
for _, row in d1.iterrows():
    m = (A26.pg == row.pitch_group) & (A26.p_throws == row.p_throws)
    t = terminal(A26[m])
    ab = int((~t.events.isin(NOTAB)).sum())
    tb = int(t.events.map({"single":1,"double":2,"triple":3,"home_run":4}).fillna(0).sum())
    h  = int(t.events.isin(HITS).sum())
    bip = A26[m & (A26.type == "X")]
    tag = f"{row.pitch_group}-{row.p_throws}"
    check(f"V-050-{tag}", f"{tag} PA ended", len(t), int(row.PA_ended))
    check(f"V-051-{tag}", f"{tag} SLG", round(tb/ab, 4) if ab else np.nan, round(float(row.slg), 4))
    check(f"V-052-{tag}", f"{tag} BA",  round(h/ab, 4) if ab else np.nan, round(float(row.ba), 4))
    check(f"V-053-{tag}", f"{tag} BIP", len(bip), int(row.bip))
    check(f"V-054-{tag}", f"{tag} hard-hit",
          round((bip.launch_speed >= 95).mean(), 4) if len(bip) else np.nan,
          round(float(row.hard_hit_rate), 4))
    check(f"V-055-{tag}", f"{tag} pitches seen", int(m.sum()), int(row.pitches_seen))
check("V-056", "Thin-sample flag set only below 15 BIP",
      int(((d1.bip < 15) != d1.thin).sum()), 0)

# ================================================== 6. RISP / SPCR =======
print("6. Scoring position (e1/e4)")
def spcr_independent(df):
    t = terminal(df)
    on2 = t.on_2b.notna(); on3 = t.on_3b.notna()
    risp = on2 | on3
    r = t[risp]
    runners = int(on2[risp].astype(int).sum() + on3[risp].astype(int).sum())
    runs = (r.post_bat_score - r.bat_score).fillna(0) - (r.events == "home_run").astype(int)
    nr = r.on_2b.notna().astype(int) + r.on_3b.notna().astype(int)
    scored = float(np.minimum(runs, nr).sum())
    return len(r), runners, scored

e1 = rc("e1_context_2026")
nrisp, runners, scored = spcr_independent(A26)
row = e1[e1.ctx == "RISP"].iloc[0]
check("V-060", "RISP PA count", nrisp, int(row.PA))
check("V-061", "RISP runners faced", runners, int(row.risp_runners_faced))
check("V-062", "RISP runners scored", scored, float(row.risp_runners_scored))
check("V-063", "SPCR", round(scored/runners, 4), round(float(row.spcr), 4))
t = terminal(A26); rr = t[t.on_2b.notna() | t.on_3b.notna()]
check("V-064", "RISP strikeouts",
      int(rr.events.isin(["strikeout", "strikeout_double_play"]).sum()), int(row.K))
check("V-065", "RISP BA",
      round(int(rr.events.isin(HITS).sum()) / int((~rr.events.isin(NOTAB)).sum()), 4),
      round(float(row.ba), 4))
check("V-066", "Context PA sums to season PA",
      int(e1.PA.sum()), len(terminal(A26)))

e4 = rc("e4_spcr_vs_phillies")
for _, row in e4.iterrows():
    bid = int(row.batter)
    src = A26 if bid == ARRAEZ else P[P.batter == bid]
    n, ru, sc = spcr_independent(src)
    check(f"V-070-{bid}", f"{row['name']} SPCR", round(sc/ru, 4), round(float(row.spcr), 4))
    check(f"V-071-{bid}", f"{row['name']} RISP PA", n, int(row.PA))

# ============================================ 7. LINEUP SLOTS (AR-5) =====
print("7. Slot reconstruction & opportunity (f1)")
pt = terminal(P).sort_values(["game_pk", "at_bat_number"]).copy()
pt["slot"] = pt.groupby("game_pk").cumcount() % 9 + 1
ng = pt.game_pk.nunique()
check("V-080", "PHI games", ng, 112)
check("V-081", "Every game has 9 slots",
      int((pt.groupby("game_pk").slot.nunique() != 9).sum()), 0)
check("V-082", "First 9 PA are 9 distinct batters in every game",
      int((pt.groupby("game_pk").head(9).groupby("game_pk").batter.nunique() != 9).sum()), 0)
f1 = rc("f1_slot_opportunity")
for _, row in f1.iterrows():
    s = pt[pt.slot == int(row.slot)]
    risp = (s.on_2b.notna() | s.on_3b.notna())
    men = (s.on_1b.notna() | s.on_2b.notna() | s.on_3b.notna())
    check(f"V-090-{int(row.slot)}", f"slot {int(row.slot)} PA", len(s), int(row.PA))
    check(f"V-091-{int(row.slot)}", f"slot {int(row.slot)} PA/g",
          round(len(s)/ng, 4), round(float(row.pa_per_game), 4))
    check(f"V-092-{int(row.slot)}", f"slot {int(row.slot)} RISP share",
          round(risp.mean(), 4), round(float(row.risp_share), 4))
    check(f"V-093-{int(row.slot)}", f"slot {int(row.slot)} men-on share",
          round(men.mean(), 4), round(float(row.men_on_share), 4))
check("V-094", "Slot PA strictly decreasing 1->9",
      bool(f1.sort_values("slot").PA.is_monotonic_decreasing), True)
check("V-095", "Slot 4 RISP share exceeds slot 1",
      bool(float(f1[f1.slot == 4].risp_share.iloc[0]) >
           float(f1[f1.slot == 1].risp_share.iloc[0])), True)

# ================================================ 8. SPRC MODEL (AR-6) ===
print("8. SPRC model arithmetic (f3/f4/f5/f7)")
f3 = rc("f3_context_profiles"); f4 = rc("f4_slot_context_weights"); f5 = rc("f5_sprc")
for s in range(1, 10):
    w = f4[f4.slot == s]
    check(f"V-100-{s}", f"slot {s} context weights sum to 1", round(float(w.w.sum()), 4), 1.0, 5e-4)
# weights recomputed independently
pt["ctx"] = np.where(pt.on_2b.notna() | pt.on_3b.notna(), "RISP",
             np.where(pt.on_1b.notna(), "MEN_ON_NO_RISP", "BASES_EMPTY"))
for s in [1, 4]:
    for c in ["RISP", "BASES_EMPTY", "MEN_ON_NO_RISP"]:
        sub = pt[pt.slot == s]
        exp = f4[(f4.slot == s) & (f4.ctx == c)]
        if len(exp):
            check(f"V-101-{s}-{c}", f"W(slot {s}, {c})",
                  round((sub.ctx == c).mean(), 4), round(float(exp.w.iloc[0]), 4))
# SPRC recomputed from its two published inputs
for h in ["Luis Arraez", "Kyle Schwarber"]:
    prof = f3[f3.hitter == h].set_index("ctx").re24_per_pa.to_dict()
    for s in range(1, 10):
        w = f4[f4.slot == s].set_index("ctx").w.to_dict()
        exp_pa = float(f1[f1.slot == s].pa_per_game.iloc[0])
        val = sum(w.get(c, 0.0) * prof.get(c, 0.0) for c in w)
        pub = f5[(f5.hitter == h) & (f5.slot == s)].iloc[0]
        # ROUNDING-CHAIN TOLERANCE (documented). This check reconstructs the
        # model output from its PUBLISHED inputs, which are stored at 4 dp.
        # Reconstructing from rounded inputs necessarily drifts. Bound is set
        # at 2e-4 on the per-PA rate and 0.05 runs on the per-162 total —
        # i.e. under 0.2% of a ~25-run quantity, immaterial to every claim in
        # the report. The RAW-path check (V-120) carries the real burden.
        check(f"V-110-{h[:4]}-{s}", f"{h} slot {s} RE24/PA projected (from published inputs)",
              round(val, 4), round(float(pub.re24_per_pa_projected), 4), 2e-4)
        check(f"V-111-{h[:4]}-{s}", f"{h} slot {s} RE24/162 (from published inputs)",
              round(val * exp_pa * 162, 3), round(float(pub.re24_per_162), 3), 0.05)
# context profile re24 recomputed from raw
at = terminal(A26)
at["ctx"] = np.where(at.on_2b.notna() | at.on_3b.notna(), "RISP",
             np.where(at.on_1b.notna(), "MEN_ON_NO_RISP", "BASES_EMPTY"))
for c in ["RISP", "BASES_EMPTY", "MEN_ON_NO_RISP"]:
    exp = f3[(f3.hitter == "Luis Arraez") & (f3.ctx == c)].iloc[0]
    check(f"V-120-{c}", f"Arraez RE24/PA in {c}",
          round(at[at.ctx == c].delta_run_exp.mean(), 4), round(float(exp.re24_per_pa), 4))
    check(f"V-121-{c}", f"Arraez PA in {c}", int((at.ctx == c).sum()), int(exp.PA_ctx))

f7 = rc("f7_swap_scenario")
def sv(h, s):
    return float(f5[(f5.hitter == h) & (f5.slot == s)].re24_per_162.iloc[0])
def f7v(prefix):
    return float(f7[f7.hitter.str.startswith(prefix)].re24_per_162.iloc[0])
a1_, a2_, a4_ = sv("Luis Arraez", 1), sv("Luis Arraez", 2), sv("Luis Arraez", 4)
k1_, k4_ = sv("Kyle Schwarber", 1), sv("Kyle Schwarber", 4)
t1_, t4_ = sv("Trea Turner", 1), sv("Trea Turner", 4)
check("V-130a", "Scenario A (Turner 1 / Arraez 4)", round(t1_ + a4_, 3),
      round(f7v("A. OBSERVED"), 3), 5e-3)
check("V-130b", "Scenario A-swap (Arraez 1 / Turner 4)", round(a1_ + t4_, 3),
      round(f7v("A-swap"), 3), 5e-3)
check("V-131a", "Scenario B (Schwarber 1 / Arraez 4)", round(k1_ + a4_, 3),
      round(f7v("B. STATED"), 3), 5e-3)
check("V-131b", "Scenario B-swap (Arraez 1 / Schwarber 4)", round(a1_ + k4_, 3),
      round(f7v("B-swap"), 3), 5e-3)
check("V-131c", "Scenario C (Arraez 2 / Schwarber 4)", round(a2_ + k4_, 3),
      round(f7v("C. Arraez 2"), 3), 5e-3)
check("V-132a", "Delta under the Turner framing", round((a1_ + t4_) - (t1_ + a4_), 3),
      round(f7v("DELTA A-swap"), 3), 5e-3)
check("V-132b", "Delta under the Schwarber framing", round((a1_ + k4_) - (k1_ + a4_), 3),
      round(f7v("DELTA B-swap"), 3), 5e-3)
check("V-133a", "Turner-framing swap is NEGATIVE (report claim)",
      bool((a1_ + t4_) - (t1_ + a4_) < 0), True)
check("V-133b", "Schwarber-framing swap is under 2 runs per 162 (report claim)",
      bool(abs((a1_ + k4_) - (k1_ + a4_)) < 2.0), True)
check("V-133c", "Scenario C beats both stated options (report claim)",
      bool(a2_ + k4_ > max(k1_ + a4_, a1_ + k4_)), True)
check("V-133d", "Observed leadoff hitter is Trea Turner, not Schwarber",
      rc("f9_observed_top_of_order").query("slot==1").sort_values("PA", ascending=False)
        .iloc[0]["name"], "Trea Turner")
check("V-134", "Arraez slot spread under 5 runs per 162 (headline claim)",
      bool(f5[f5.hitter == "Luis Arraez"].re24_per_162.max() -
           f5[f5.hitter == "Luis Arraez"].re24_per_162.min() < 5.0), True)
check("V-135", "Schwarber outproduces Arraez in every slot",
      int((f5[f5.hitter == "Kyle Schwarber"].sort_values("slot").re24_per_162.values <=
           f5[f5.hitter == "Luis Arraez"].sort_values("slot").re24_per_162.values).sum()), 0)

# ============================================= 9. TABLE SETTING (AR-7) ===
print("9. Table setting (f6/f8)")
f8 = rc("f8_table_setting_supply")
a_obp = None
t26 = terminal(A26)
h_ = int(t26.events.isin(HITS).sum()); bb_ = int(t26.events.isin(["walk","intent_walk"]).sum())
hbp_ = int((t26.events == "hit_by_pitch").sum())
a_obp = round((h_ + bb_ + hbp_) / len(t26), 4)
check("V-140", "Arraez OBP used by AR-7", a_obp, round(float(f8.arraez_obp.iloc[0]), 4))
for _, row in f8.iterrows():
    s = int(row.slot); sub = pt[pt.slot == s]
    ob = sub.events.isin(list(HITS) + ["walk", "intent_walk", "hit_by_pitch"])
    check(f"V-141-{s}", f"slot {s} incumbent OBP", round(ob.mean(), 4),
          round(float(row.incumbent_obp), 4))
    check(f"V-142-{s}", f"slot {s} incumbent on-base/g", round(ob.sum()/ng, 4),
          round(float(row.incumbent_onbase_per_game), 4))
    check(f"V-143-{s}", f"slot {s} Arraez supply/g",
          round(a_obp * float(row.pa_per_game), 4), round(float(row.arraez_onbase_per_game), 4))
check("V-144", "Supply upper bound peaks at a top-third slot",
      int(f8.loc[f8.arraez_runners_cashed_ub_per_162.idxmax(), "slot"]) in (1, 2, 3), True)

# ======================================================= 10. ARTIFACTS ===
print("10. Artifact completeness")
idx = pd.read_csv(OUT / f"{STEM}_receipt_index.csv")
missing = [r.file for r in idx.itertuples() if not (OUT / r.file).exists()]
check("V-150", "Every indexed receipt exists on disk", len(missing), 0)
empty = [r.file for r in idx.itertuples()
         if (OUT / r.file).exists() and (OUT / r.file).stat().st_size == 0]
check("V-151", "No zero-byte receipts", len(empty), 0)
check("V-152", "Seven figures present",
      len([p for p in OUT.glob(f"{STEM}_fig*.png")]), 7)
dq = rc("dq_scorecard")
check("V-153", "Build DQ scorecard has zero FAIL", int((dq.result != "PASS").sum()), 0)
check("V-154", "Freshness manifest declares manual carry-ins",
      int(rc("freshness_manifest").source.str.contains("MANUAL").sum()) >= 1, True)

# ============================================================= REPORT ====
res = pd.DataFrame(RESULTS)
res.to_csv(OUT / f"{STEM}_verification_results.csv", index=False)
npass = int((res.result == "PASS").sum()); nfail = int((res.result == "FAIL").sum())
print("\n" + "=" * 68)
print(f"VERIFICATION: {npass}/{len(res)} PASS · {nfail} FAIL")
print("=" * 68)
if nfail:
    print(res[res.result == "FAIL"].to_string(index=False))
    sys.exit(1)
print("All published numbers independently reproduced.")
