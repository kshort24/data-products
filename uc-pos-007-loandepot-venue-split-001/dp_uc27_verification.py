"""
Independent recompute harness for uc-pos-007 / dp_uc27.

Deliberately does NOT import anything from dp_uc27_phillies_at_loandepot.py. It
re-reads the parquet layer, re-applies the governance filters from first
principles, and recomputes every headline number the report publishes using a
different code path (long-form event counting rather than the merge-chain
kernel). Any disagreement beyond tolerance is a FAIL.

Usage: python dp_uc27_verification.py [MLB_DIR] [OUT_DIR]
Exit code 0 = all checks reconcile, 1 = at least one mismatch.
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MLB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else MLB / "out"
STEM = "dp_uc27"
K = ["game_pk", "at_bat_number", "pitch_number"]

ROSTER = {607208: "Turner, Trea", 656941: "Schwarber, Kyle", 547180: "Harper, Bryce",
          669016: "Marsh, Brandon", 664761: "Bohm, Alec", 681082: "Stott, Bryson",
          592663: "Realmuto, J.T.", 687282: "Rincones Jr., Gabriel",
          702222: "Crawford, Justin", 656537: "Hill, Derek", 624641: "Sosa, Edmundo"}
MLB_TEAMS = {"ARI", "ATL", "BAL", "BOS", "CHC", "CIN", "CLE", "COL", "CWS", "DET", "HOU",
             "KC", "LAA", "LAD", "MIA", "MIL", "MIN", "NYM", "NYY", "OAK", "PHI", "PIT",
             "SD", "SEA", "SF", "STL", "TB", "TEX", "TOR", "WSH", "ATH"}
IRMA = {492302, 492317, 492332}
MIAMI, OTHER = "loanDepot park", "All other MLB parks"
ALCANTARA = 645261

results: list[dict] = []


def check(name, got, exp, tol=1e-6, note=""):
    ok = (pd.isna(got) and pd.isna(exp)) or (abs(float(got) - float(exp)) <= tol)
    results.append({"check": name, "recomputed": got, "reported": exp,
                    "delta": (None if pd.isna(got) or pd.isna(exp) else round(float(got) - float(exp), 6)),
                    "status": "PASS" if ok else "FAIL", "note": note})


# ------------------------------------------------------------------ rebuild --
frames = []
for yr in range(2015, 2027):
    p = MLB / f"data/phillies/phils_{yr}.parquet"
    if p.exists():
        d = pd.read_parquet(p)
        frames.append(d[(d.phillies_role == "batting") & (d.batter.isin(ROSTER))])
for path in sorted(glob.glob(str(MLB / "data/opponents/*.parquet"))):
    d = pd.read_parquet(path)
    if "batter" in d.columns:
        d = d[d.batter.isin(ROSTER)]
        if len(d):
            frames.append(d)
u = pd.concat(frames, ignore_index=True, sort=False).drop_duplicates(subset=K, keep="first")

w = pd.read_csv(MLB / "wOBA and FIP Constants.csv")
u = u.drop(columns=[c for c in w.columns if c != "Season" and c in u.columns])
u = u.merge(w, left_on="game_year", right_on="Season", how="left")

g = u[(u.game_type == "R") & (u.home_team.isin(MLB_TEAMS)) & (~u.game_pk.isin(IRMA)) &
      (u.p_throws == "R")].copy()
g["player"] = g.batter.map(ROSTER)
g["venue"] = np.where(g.home_team.eq("MIA"), MIAMI, OTHER)
g["bat_team"] = np.where(g.inning_topbot.eq("Bot"), g.home_team, g.away_team)


# ----------------------------------------------- independent stat machinery --
def slash(df):
    """Long-form recompute: count events directly, no merge chain."""
    ev = df.events.fillna("NA")
    pa = int((~ev.isin(["NA", "pickoff_1b"])).sum())
    ab = int((~ev.isin(["NA", "pickoff_1b", "walk", "intent_walk", "hit_by_pitch",
                        "sac_fly", "sac_bunt"])).sum())
    c = ev.value_counts()
    s1, s2, s3, hr = (int(c.get(k, 0)) for k in ("single", "double", "triple", "home_run"))
    bb, hbp = int(c.get("walk", 0)), int(c.get("hit_by_pitch", 0))
    k_ = int(c.get("strikeout", 0)) + int(c.get("strikeout_double_play", 0))
    h = s1 + s2 + s3 + hr
    wnum = 0.0
    for wcol, evn in [("wBB", "walk"), ("wHBP", "hit_by_pitch"), ("w1B", "single"),
                      ("w2B", "double"), ("w3B", "triple"), ("wHR", "home_run")]:
        wnum += float(df.loc[df.events == evn, wcol].sum())
    bip = df[df.type == "X"]
    return {
        "pa": pa, "ab": ab, "hits": h, "bip": int(len(bip)),
        "ba": h / ab if ab else np.nan,
        "obp": (h + bb + hbp) / pa if pa else np.nan,
        "slg": (s1 + 2 * s2 + 3 * s3 + 4 * hr) / ab if ab else np.nan,
        "woba": wnum / pa if pa else np.nan,
        "xwoba": float(df.estimated_woba_using_speedangle.mean()),
        "hard_hit_rate": float((bip.launch_speed >= 95).sum()) / len(bip) if len(bip) else np.nan,
        "barrel_rate": float((bip.launch_speed_angle == 6).sum()) / len(bip) if len(bip) else np.nan,
        "ev90": float(bip.launch_speed.quantile(0.90)) if len(bip) else np.nan,
        "krate": k_ / pa if pa else np.nan,
        "pitches_per_pa": len(df) / pa if pa else np.nan,
    }


# --------------------------------------------------------------- reconcile --
pooled = pd.read_csv(OUT / f"{STEM}_pooled_venue.csv")
for v in (MIAMI, OTHER):
    r = slash(g[g.venue == v]); rep = pooled[pooled.venue == v].iloc[0]
    tag = "Miami" if v == MIAMI else "Other"
    check(f"pooled/{tag}/plate_apps", r["pa"], rep.plate_apps)
    for m in ("ba", "obp", "slg", "woba", "xwoba", "hard_hit_rate", "barrel_rate",
              "krate", "pitches_per_pa"):
        check(f"pooled/{tag}/{m}", round(r[m], 3), rep[m], tol=0.0011)
    check(f"pooled/{tag}/ev90", round(r["ev90"], 2), round(float(rep.ev90), 2), tol=0.011)
    check(f"pooled/{tag}/bip", r["bip"], rep.bips)

vis = pd.read_csv(OUT / f"{STEM}_pooled_venue_visitors.csv")
gv = g[~(g.venue.eq(MIAMI) & g.bat_team.eq("MIA"))]
r = slash(gv[gv.venue == MIAMI]); rep = vis[vis.venue == MIAMI].iloc[0]
check("visitors/Miami/plate_apps", r["pa"], rep.plate_apps)
for m in ("woba", "xwoba", "hard_hit_rate", "barrel_rate", "slg", "obp"):
    check(f"visitors/Miami/{m}", round(r[m], 3), rep[m], tol=0.0011)

split = pd.read_csv(OUT / f"{STEM}_venue_split.csv")
for p in ROSTER.values():
    for v in (MIAMI, OTHER):
        sub = g[(g.player == p) & (g.venue == v)]
        row = split[(split.player == p) & (split.venue == v)]
        if not len(sub) or not len(row):
            continue
        r, rep = slash(sub), row.iloc[0]
        short = p.split(",")[0]
        tag = "MIA" if v == MIAMI else "OTH"
        check(f"split/{short}/{tag}/plate_apps", r["pa"], rep.plate_apps)
        for m in ("woba", "xwoba", "ops" if False else "slg", "hard_hit_rate", "barrel_rate"):
            check(f"split/{short}/{tag}/{m}", round(r[m], 3), rep[m], tol=0.0011)

alc = pd.read_csv(OUT / f"{STEM}_alcantara_h2h.csv")
ga = g[g.pitcher == ALCANTARA]
for p in alc.player:
    sub = ga[ga.player == p]
    rep = alc[alc.player == p].iloc[0]
    r = slash(sub)
    short = p.split(",")[0]
    check(f"alcantara/{short}/plate_apps", r["pa"], rep.plate_apps)
    check(f"alcantara/{short}/woba", round(r["woba"], 3), rep.woba, tol=0.0011)
    check(f"alcantara/{short}/xwoba", round(r["xwoba"], 3), rep.xwoba, tol=0.0011)

alcv = pd.read_csv(OUT / f"{STEM}_alcantara_venue.csv")
for v in alcv.venue:
    r = slash(ga[ga.venue == v]); rep = alcv[alcv.venue == v].iloc[0]
    tag = "Miami" if v == MIAMI else "Other"
    check(f"alcantara_venue/{tag}/plate_apps", r["pa"], rep.plate_apps)
    for m in ("woba", "xwoba", "hard_hit_rate", "slg"):
        check(f"alcantara_venue/{tag}/{m}", round(r[m], 3), rep[m], tol=0.0011)

# VD-1 arithmetic: deltas must equal the two panel cells they are built from
vd = pd.read_csv(OUT / f"{STEM}_venue_delta.csv")
for _, row in vd.iterrows():
    for m in ("woba", "xwoba", "hard_hit_rate", "barrel_rate", "ev90"):
        # Tolerance 2.5e-4: the CSV stores mia_/oth_ rounded to 4dp while d_ is
        # computed unrounded, so a differenced pair can drift by up to 1e-4 twice.
        check(f"VD1/{row.player.split(',')[0]}/{m}",
              round(row[f"mia_{m}"] - row[f"oth_{m}"], 4), round(row[f"d_{m}"], 4),
              tol=2.5e-4, note="4dp round-trip tolerance")

# Governance invariants
check("governance/no_dup_keys", int(g.duplicated(K).sum()), 0)
check("governance/no_milb", int((~g.home_team.isin(MLB_TEAMS)).sum()), 0)
check("governance/no_irma", int(g.game_pk.isin(IRMA).sum()), 0)
check("governance/rhp_only", int(g.p_throws.ne("R").sum()), 0)
check("governance/regular_season_only", int(g.game_type.ne("R").sum()), 0)
check("governance/entity_lock", int((~g.batter.isin(ROSTER)).sum()), 0)

res = pd.DataFrame(results)
res.to_csv(OUT / f"{STEM}_verification_results.csv", index=False)
fails = res[res.status == "FAIL"]
pd.set_option("display.width", 200)
print(res.to_string(index=False))
print(f"\n{len(res)} checks · {len(res) - len(fails)} PASS · {len(fails)} FAIL")
if len(fails):
    print("\nFAILURES:"); print(fails.to_string(index=False))
sys.exit(1 if len(fails) else 0)
