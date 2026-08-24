"""
dp_uc36 VERIFICATION — independent recompute of the published receipts and the
report's headline claims. Deliberately does NOT import the build module: plain
boolean masks, a separate wOBA implementation, and — for the UD family — the
human DPO's ORIGINAL notebook method (min/max at-bat double-merge) rather than
the build's min/max-inning shortcut, so agreement between the two is evidence.

Usage: python3 dp_uc36_verification.py    (exit 0 iff all checks pass)
"""
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
CORTES = 641482

_CAND = [os.environ.get("MLB_DATA_ROOT", ""), os.path.join(HERE, "data"),
         "/mnt/user-data/uploads/MLB/data",
         r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data"]
ROOT = next(p for p in _CAND if p and os.path.isdir(os.path.join(p, "opponents")))
_W = [os.path.join(HERE, "wOBA and FIP Constants.csv"),
      r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\wOBA and FIP Constants.csv"]
WOBA_CSV = next(p for p in _W if os.path.isfile(p))

raw = pd.read_parquet(os.path.join(ROOT, "opponents", "cortes.parquet"))
raw = raw[raw.pitcher == CORTES].drop_duplicates(
    ["game_pk", "at_bat_number", "pitch_number"]).copy()
raw["game_date"] = pd.to_datetime(raw.game_date)
d = raw[raw.game_type == "R"].copy()
post = raw[raw.game_type.isin(["D", "L", "W"])].copy()

W = pd.read_csv(WOBA_CSV).set_index("Season")

CHECKS = []


def check(name, got, want, tol=0.0005):
    if isinstance(want, str) or isinstance(got, str):
        ok = str(got) == str(want)
    else:
        try:
            ok = abs(float(got) - float(want)) <= tol
        except (TypeError, ValueError):
            ok = False
    CHECKS.append((name, got, want, ok))
    return ok


# ---------------------------------------------------------------------------
# independent primitives (plain masks — no kernel import)
# ---------------------------------------------------------------------------
PA_EXCL = ["pickoff_1b"]
SWG = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
       "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHF = ["foul_tip", "missed_bunt", "swinging_pitchout", "swinging_strike",
       "swinging_strike_blocked"]


def pa_mask(f):
    return f.events.notna() & ~f.events.isin(PA_EXCL)


def iwoba(f):
    """independent wOBA: FanGraphs weights, fresh implementation."""
    e = f[pa_mask(f)]
    num = 0.0
    for ev, col in [("walk", "wBB"), ("hit_by_pitch", "wHBP"), ("single", "w1B"),
                    ("double", "w2B"), ("triple", "w3B"), ("home_run", "wHR")]:
        sub = e[e.events == ev]
        num += sum(W.loc[y, col] for y in sub.game_year)
    return num / len(e)


def ikrate(f):
    e = f[pa_mask(f)]
    return e.events.isin(["strikeout", "strikeout_double_play"]).mean()


def ibbrate(f):
    e = f[pa_mask(f)]
    return (e.events == "walk").mean()


def iwhiff(f):
    s = f[f.description.isin(SWG)]
    return f.description.isin(WHF).sum() / len(s)


def ihh(f):
    b = f[f.type == "X"]
    return (b.launch_speed >= 95).mean()


def ixwcon(f):
    return f.loc[f.type == "X", "estimated_woba_using_speedangle"].mean()


def ifpsr(f):
    fp = f[f.pitch_number == 1]
    return (fp.type != "B").mean()


def izone(f):
    t = f[f.pitch_name.notna()]
    return (t.zone <= 9).mean()


def ichase(f):
    o = f[f.zone > 9]
    return o.description.isin(SWG).mean()


def npas(f):
    return int(pa_mask(f).sum())


# ---------------------------------------------------------------------------
# 0. locks
# ---------------------------------------------------------------------------
check("lock::entity single id", d.pitcher.nunique(), 1)
check("lock::hand L", ";".join(d.p_throws.unique()), "L")
check("lock::no dupes", int(d.duplicated(["game_pk", "at_bat_number",
                                          "pitch_number"]).sum()), 0)
check("lock::no 2026 rows", int((d.game_year == 2026).sum()), 0)
check("lock::R rows", len(d), 10087)
check("lock::postseason rows", len(post), 229)
check("lock::post D", int((post.game_type == "D").sum()), 153)
check("lock::post L", int((post.game_type == "L").sum()), 55)
check("lock::post W", int((post.game_type == "W").sum()), 21)

# ---------------------------------------------------------------------------
# 1. UD family via the DPO's ORIGINAL notebook method (double merge)
# ---------------------------------------------------------------------------
level = ["player_name", "game_year", "game_date", "game_pk"]
z = d.groupby(level, as_index=False).agg(
    min_ab=("at_bat_number", "min"), max_ab=("at_bat_number", "max"),
    total_pitches=("des", "size"), uq_pas=("at_bat_number", "nunique"))
g2 = d.groupby(level + ["inning", "at_bat_number"], as_index=False).agg(
    sizer=("des", "size"))
z = z.merge(g2, left_on=level + ["min_ab"], right_on=level + ["at_bat_number"],
            how="left", suffixes=("", "_ab"))
z = z.merge(g2, left_on=level + ["max_ab"], right_on=level + ["at_bat_number"],
            how="left", suffixes=("_start", "_end"))
z["innings"] = z.inning_end - z.inning_start
zagg = z[level + ["innings", "inning_start", "total_pitches", "uq_pas"]]
la = ["player_name", "game_year"]
zfig = zagg.groupby(la, as_index=False).agg(
    total_games=("game_pk", "nunique"), total_innings=("innings", "sum"),
    total_pas=("uq_pas", "sum"))
st = zagg[zagg.inning_start == 1].groupby(la, as_index=False).agg(
    starts=("game_pk", "nunique"))
bk = zagg[(zagg.inning_start > 1) & (zagg.innings > 2)].groupby(
    la, as_index=False).agg(bulks=("game_pk", "nunique"))
zfig = zfig.merge(st, on=la, how="left").merge(bk, on=la, how="left").fillna(0)
zfig["start_share"] = zfig.starts / zfig.total_games
zfig["bulk_share"] = zfig.bulks / zfig.total_games
zfig["innings_per_gm"] = zfig.total_innings / zfig.total_games
zfig["plate_apps_per_gm"] = zfig.total_pas / zfig.total_games

ud = pd.read_csv(f"{OUT}/dp_uc36_usage_by_season.csv")
for _, r in zfig.iterrows():
    y = int(r.game_year)
    pub = ud[ud.game_year == y].iloc[0]
    check(f"UD::{y} games", pub.games, r.total_games)
    check(f"UD::{y} starts", pub.starts, r.starts)
    check(f"UD::{y} bulks", pub.bulks, r.bulks)
    check(f"UD::{y} start_share", pub.start_share, round(r.start_share, 3), 0.001)
    check(f"UD::{y} bulk_share", pub.bulk_share, round(r.bulk_share, 3), 0.001)
    check(f"UD::{y} innings_per_gm", pub.innings_per_gm,
          round(r.innings_per_gm, 3), 0.001)
    check(f"UD::{y} plate_apps_per_gm", pub.plate_apps_per_gm,
          round(r.plate_apps_per_gm, 3), 0.001)

# report claims on deployment
check("report::2019 bulk games", int(zfig.loc[zfig.game_year == 2019, "bulks"].iloc[0]), 8)
a2225 = zagg[zagg.game_year >= 2022]
check("report::2022-25 appearances", a2225.game_pk.nunique(), 79)
check("report::2022-25 starts", a2225[a2225.inning_start == 1].game_pk.nunique(), 78)
p25 = zagg[zagg.game_year == 2025]
check("report::2025 mean pitches", round(p25.total_pitches.mean(), 1), 74.9, 0.05)
check("report::2025 min pitches", int(p25.total_pitches.min()), 57)
check("report::2025 max pitches", int(p25.total_pitches.max()), 90)
check("report::2025 all starts", int((p25.inning_start == 1).sum()), 8)

# ---------------------------------------------------------------------------
# 2. season log / phase / platoon claims (independent wOBA path)
# ---------------------------------------------------------------------------
season_pub = pd.read_csv(f"{OUT}/dp_uc36_season_log.csv")
for y in sorted(d.game_year.unique()):
    f = d[d.game_year == y]
    pub = season_pub[season_pub.game_year == y].iloc[0]
    check(f"season::{y} PA", pub.plate_apps, npas(f))
    check(f"season::{y} wOBA", pub.woba, round(iwoba(f), 3), 0.001)
    check(f"season::{y} K%", pub.krate, round(ikrate(f), 3), 0.001)

check("report::2022 wOBA .245", round(iwoba(d[d.game_year == 2022]), 3), 0.245, 0.001)
check("report::2025 PA 157", npas(d[d.game_year == 2025]), 157)

plat = pd.read_csv(f"{OUT}/dp_uc36_platoon_career.csv")
for h in ["L", "R"]:
    f = d[d.stand == h]
    pub = plat[plat.stand == h].iloc[0]
    check(f"platoon::career {h} PA", pub.plate_apps, npas(f))
    check(f"platoon::career {h} wOBA", pub.woba, round(iwoba(f), 3), 0.001)

claims = [(2022, "L", 0.161, 89), (2022, "R", 0.259, 527)]
for y, h, wv, pa in claims:
    f = d[(d.game_year == y) & (d.stand == h)]
    check(f"report::{y} vs {h} wOBA", round(iwoba(f), 3), wv, 0.001)
    check(f"report::{y} vs {h} PA", npas(f), pa)
f = d[d.game_year.isin([2023, 2024]) & (d.stand == "L")]
check("report::2023-24 vs L wOBA .233", round(iwoba(f), 3), 0.233, 0.001)
check("report::2023-24 vs L PA 198", npas(f), 198)
f = d[d.game_year.isin([2023, 2024]) & (d.stand == "R")]
check("report::2023-24 vs R wOBA .329", round(iwoba(f), 3), 0.329, 0.001)
check("report::2023-24 vs R PA 780", npas(f), 780)
check("report::2022 vs L K% .371", round(ikrate(d[(d.game_year == 2022) & (d.stand == "L")]), 3), 0.371, 0.001)

# ---------------------------------------------------------------------------
# 3. ED-1 era delta claims
# ---------------------------------------------------------------------------
pk, dc = d[d.game_year == 2022], d[d.game_year.isin([2023, 2024])]
check("ED1::peak HH .347", round(ihh(pk), 3), 0.347, 0.001)
check("ED1::decline HH .430", round(ihh(dc), 3), 0.430, 0.001)
check("ED1::peak FPSR .672", round(ifpsr(pk), 3), 0.672, 0.001)
check("ED1::decline FPSR .607", round(ifpsr(dc), 3), 0.607, 0.001)
check("ED1::peak xwOBAcon .321", round(ixwcon(pk), 3), 0.321, 0.001)
check("ED1::decline xwOBAcon .360", round(ixwcon(dc), 3), 0.360, 0.001)
check("ED1::peak chase .309", round(ichase(pk), 3), 0.309, 0.001)
check("ED1::decline chase .271", round(ichase(dc), 3), 0.271, 0.001)
check("ED1::peak whiff .245", round(iwhiff(pk), 3), 0.245, 0.001)
check("ED1::decline whiff .242", round(iwhiff(dc), 3), 0.242, 0.001)
check("ED1::peak zone strict .514", round(izone(pk), 3), 0.514, 0.001)
check("ED1::decline zone strict .509", round(izone(dc), 3), 0.509, 0.001)
check("ED1::peak K .265", round(ikrate(pk), 3), 0.265, 0.001)
check("ED1::decline K .234", round(ikrate(dc), 3), 0.234, 0.001)

# ---------------------------------------------------------------------------
# 4. stuff claims (FF)
# ---------------------------------------------------------------------------
ff = d[d.pitch_type == "FF"]
for y, v in [(2019, 89.61), (2021, 90.73), (2022, 91.75), (2023, 91.59),
             (2024, 92.08), (2025, 90.13)]:
    check(f"FF::velo {y}", round(ff[ff.game_year == y].release_speed.mean(), 2), v, 0.01)
for y, v in [(2022, 19.52), (2023, 19.43), (2024, 19.15), (2025, 19.31)]:
    check(f"FF::IVB {y}", round((ff[ff.game_year == y].pfx_z * 12).mean(), 2), v, 0.01)
m = ff.assign(month=ff.game_date.dt.to_period("M").astype(str))
check("FF::2024-04 velo", round(m[m.month == "2024-04"].release_speed.mean(), 2), 91.55, 0.01)
check("FF::2024-09 velo", m[m.month == "2024-09"].release_speed.mean(), 92.665, 0.01)
check("FF::2025-08 velo", round(m[m.month == "2025-08"].release_speed.mean(), 2), 90.12, 0.01)
check("FF::2025-09 velo", round(m[m.month == "2025-09"].release_speed.mean(), 2), 89.5, 0.01)
mech = d[d.pitch_name.notna()]
check("mech::arm_angle 2022", round(mech[mech.game_year == 2022].arm_angle.mean(), 1), 45.1, 0.05)
check("mech::arm_angle 2025", round(mech[mech.game_year == 2025].arm_angle.mean(), 1), 51.2, 0.05)
check("mech::rel_x 2019", round(mech[mech.game_year == 2019].release_pos_x.mean(), 2), 1.97, 0.01)
check("mech::rel_x 2025", round(mech[mech.game_year == 2025].release_pos_x.mean(), 2), 1.11, 0.01)

# LHP orientation asserts (independent)
t21 = mech[mech.game_year >= 2021]
check("orient::SI pfx_x>0", float(t21[t21.pitch_type == "SI"].pfx_x.mean() > 0), 1.0)
check("orient::CH pfx_x>0", float(t21[t21.pitch_type == "CH"].pfx_x.mean() > 0), 1.0)
check("orient::ST pfx_x<0", float(t21[t21.pitch_type == "ST"].pfx_x.mean() < 0), 1.0)

# ---------------------------------------------------------------------------
# 5. TTO / rest / terciles
# ---------------------------------------------------------------------------
starts_pk = zagg[zagg.inning_start == 1].game_pk
ds = d[d.game_pk.isin(starts_pk)].copy()
ds["bf_seq"] = ds.groupby("game_pk").at_bat_number.transform(
    lambda s: s.rank(method="dense"))
for lo, hi, name, wv, pa in [(0, 9, "1st", 0.280, 855), (9, 18, "2nd", 0.305, 814),
                             (18, 99, "3rd+", 0.334, 400)]:
    f = ds[(ds.bf_seq > lo) & (ds.bf_seq <= hi)]
    check(f"TTO::{name} wOBA", round(iwoba(f), 3), wv, 0.001)
    check(f"TTO::{name} PA", npas(f), pa)

apv = zagg.sort_values("game_date") if "game_date" in zagg else None
ap2 = zagg.sort_values(["game_year", "game_date"]).copy()
ap2["rest"] = pd.to_datetime(ap2.game_date).diff().dt.days - 1
st4 = ap2[(ap2.inning_start == 1) & (ap2.rest == 4)]
f = d[d.game_pk.isin(st4.game_pk)]
check("rest::4d starts", len(st4), 37)
check("rest::4d wOBA", round(iwoba(f), 3), 0.276, 0.001)
st6 = ap2[(ap2.inning_start == 1) & (ap2.rest >= 6)]
f = d[d.game_pk.isin(st6.game_pk)]
check("rest::6+d starts", len(st6), 18)
check("rest::6+d wOBA", round(iwoba(f), 3), 0.343, 0.001)

ap_ok = zagg[zagg.uq_pas >= 10]
per = []
for pk_ in ap_ok.game_pk:
    per.append((pk_, iwoba(d[d.game_pk == pk_])))
per = pd.DataFrame(per, columns=["game_pk", "woba"]).sort_values(
    "woba").reset_index(drop=True)
n3 = len(per) // 3
check("terc::outings total", len(per), 114)
good = d[d.game_pk.isin(per.game_pk[:n3])]
bad = d[d.game_pk.isin(per.game_pk[len(per) - n3:])]
check("terc::good wOBA", round(iwoba(good), 3), 0.173, 0.001)
check("terc::bad wOBA", round(iwoba(bad), 3), 0.462, 0.001)
check("terc::good whiff", round(iwhiff(good), 3), 0.269, 0.001)
check("terc::bad whiff", round(iwhiff(bad), 3), 0.212, 0.001)
check("terc::good zone", round(izone(good), 3), 0.517, 0.001)
check("terc::bad zone", round(izone(bad), 3), 0.486, 0.001)
check("terc::good FF velo", round(good[good.pitch_type == "FF"].release_speed.mean(), 1), 91.6, 0.05)
check("terc::bad FF velo", round(bad[bad.pitch_type == "FF"].release_speed.mean(), 1), 91.0, 0.05)

# ---------------------------------------------------------------------------
# 6. battery claims (2023-25)
# ---------------------------------------------------------------------------
rec = d[d.game_year >= 2023]
trk = rec[rec.pitch_name.notna()]
ffl = trk[(trk.stand == "L") & (trk.pitch_name == "4-Seam Fastball")]
check("bat::FF-L pitches", len(ffl), 449)
check("bat::FF-L xwOBAcon", round(ixwcon(ffl), 3), 0.457, 0.001)
check("bat::FF-L HH", round(ihh(ffl), 3), 0.614, 0.001)
check("bat::FF-L HR", int((ffl.events == "home_run").sum()), 7)
stl = trk[(trk.stand == "L") & (trk.pitch_name == "Sweeper")]
check("bat::ST-L xwOBAcon", round(ixwcon(stl), 3), 0.247, 0.001)
check("bat::ST-L whiff", round(iwhiff(stl), 3), 0.351, 0.001)
chr_ = trk[(trk.stand == "R") & (trk.pitch_name == "Changeup")]
check("bat::CH-R plate_x", round(chr_.plate_x.mean(), 2), 0.87, 0.01)
ch2 = chr_[chr_.strikes == 2]
check("bat::CH-R 2K whiff", round(iwhiff(ch2), 3), 0.327, 0.001)
lhb = trk[trk.stand == "L"]
check("bat::L glove-side share", round((lhb.plate_x < -0.15).mean(), 3), 0.685, 0.001)
# 'behind' per the receipt's count-state definition: balls > strikes AND not
# two strikes (np.select order in the build puts 3-2 in 'two strikes')
rb = trk[(trk.stand == "R") & (trk.balls > trk.strikes) & (trk.strikes < 2)]
check("bat::R behind cutter", round((rb.pitch_name == "Cutter").mean(), 3), 0.448, 0.001)
check("bat::L tracked", len(lhb), 877)
check("bat::R tracked", len(trk[trk.stand == "R"]), 3639)

# ---------------------------------------------------------------------------
# 7. postseason context
# ---------------------------------------------------------------------------
fr = post[(post.events == "home_run") & post.des.astype(str).str.contains("Freeman")]
check("post::Freeman GS exists", len(fr), 1)
check("post::Freeman inning 10", int(fr.inning.iloc[0]), 10)
check("post::Freeman pitch FF", fr.pitch_type.iloc[0], "FF")
check("post::Freeman velo 92.2", round(float(fr.release_speed.iloc[0]), 1), 92.2, 0.05)
check("post::Freeman 0-0 count", int(fr.balls.iloc[0]) + int(fr.strikes.iloc[0]), 0)
check("post::D wOBA .283", round(iwoba(post[post.game_type == "D"]), 3), 0.283, 0.001)

# cross-method sanity (informational tolerance): Statcast woba_value vs FanGraphs
sv = d[pa_mask(d)]
sc_woba = sv.woba_value.sum() / sv.woba_denom.sum()
check("xmethod::career wOBA statcast-vs-FG within .02",
      float(abs(sc_woba - iwoba(d)) < 0.02), 1.0)

# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------
fails = [c for c in CHECKS if not c[3]]
print(f"dp_uc36 verification: {len(CHECKS) - len(fails)}/{len(CHECKS)} PASS")
for name, got, want, ok in CHECKS:
    if not ok:
        print(f"  FAIL {name}: got {got} want {want}")
pd.DataFrame(CHECKS, columns=["check", "got", "want", "pass"]).to_csv(
    f"{OUT}/dp_uc36_verification_results.csv", index=False)
sys.exit(0 if not fails else 1)
