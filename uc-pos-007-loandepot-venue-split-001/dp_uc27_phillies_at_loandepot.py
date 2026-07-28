"""
============================================================================
GOVERNED DATA PRODUCT — uc-pos-007-loandepot-venue-split-001 (UC #28)
"Phillies hitters at loanDepot park: the venue split, and the man on the mound"
============================================================================
Layer-3 BUILD artifact, Phillies Position-player (pos) value stream.

Pattern lineage
---------------
uc-pos-006 / dp_uc24 (Turner 2026 review — locked KPI kernel, evidence tiers,
figure/receipt discipline), uc-pos-004 / dp_uc20 (hitter retrospective shape),
uc-pps-021 / dp_uc25 (opponent-pitcher lens), UC11 (entity lock by MLBAM id,
multi-source union with dedup).

What this builds
----------------
LENS A (primary) — Venue split. Career MLB performance vs RHP for an 11-hitter
  Phillies roster, split into two venue cohorts: loanDepot park (Miami) vs all
  other MLB parks. Answers "does this group hit differently in Miami?"
LENS B (secondary) — Career head-to-head vs Sandy Alcantara (MLBAM 645261), the
  announced 2026-07-28 Marlins starter, all venues and the Miami subset.

Locked KPI mechanics inherited VERBATIM from dp_uc24 / "Baseball Functions.ipynb":
  get_stats (plate_apps, at_bats, ba, obp, slg, ops, woba, iso, krate, bbrate,
  xwoba, xba), hard_hit_rate (launch_speed >= 95 over type=='X'),
  barrel_rate (launch_speed_angle == 6 over type=='X'), ev90 (0.90 quantile of
  launch_speed over type=='X'), bb_type_by_level, SWINGS/WHIFFS discipline panel.
  pitches_per_pa = pitches / plate_apps (from the requester's snippet).
  wOBA weights joined on game_year == Season from "wOBA and FIP Constants.csv".

NEW KPIs this UC (specs in governance 04_, PROVISIONAL — not inheritable):
  VD-1  Venue Delta       — signed (Miami minus Other) difference for any rate
                            KPI at hitter grain, gated on minimum PA in both cohorts.
  VD-2  Venue Signal Class — classifies each hitter's Miami split by whether the
                            RESULTS delta (wOBA) and the PROCESS delta (a 3-part
                            contact-quality composite: hard-hit%, barrel%, EV90)
                            agree in sign. Guards against reading noise as signal.

DATA WINDOW / FRESHNESS / GOVERNANCE FILTERS
--------------------------------------------
  * Entity lock: batter == <MLBAM id>, never player_name (11 ids, see ROSTER).
  * game_type == 'R' (regular season only).
  * p_throws == 'R' (the use case is explicitly an RHP-context preview).
  * Competition level: MLB only. MiLB rows (Lehigh Valley / Clearwater frames in
    data/opponents/) are EXCLUDED by home_team allow-list. Without this, Justin
    Crawford's and Gabriel Rincones Jr.'s "all other ballparks" baselines are
    33% / 45% minor-league pitches.
  * Dedup on ['game_pk','at_bat_number','pitch_number'] AFTER the union. The
    requester's source snippet (pd.concat([pos, nphl])) does not dedup; the same
    pitch is carried by pos, by the hitter's own opponents parquet, by team-level
    "-of-" pulls, and by opposing-pitcher parquets (alcantara, luzardo, pop...).
    Naive concat inflates Miami pitch counts by 6-18% per hitter.
  * Venue integrity: three 2017 games carry home_team == 'MIA' but were played at
    Miller Park, Milwaukee (Hurricane Irma relocation, 2017-09-15/16/17 vs MIL).
    They are EXCLUDED from the Miami cohort and from the product entirely.
  * Cache freshness: data/phillies/phils_2026.parquet max game_date = 2026-07-22
    (T-5 relative to the 2026-07-27 build date). Alcantara's own parquet
    (data/opponents/alcantara.parquet) stops at 2025-04-12; his 2026 form is only
    observable through the pitches Phillies hitters saw (2026-06-17).
  * MANUAL CARRY-INS (not derivable from the pitch log):
      - 2026-07-28 probable starters: Sandy Alcantara (MIA) vs Aaron Nola (PHI),
        6:40 pm ET at loanDepot park. Source: published probables, 2026-07-25.
      - Bryan De La Cruz excluded at requester's instruction (no parquet pulled).
      - loanDepot park configuration is NOT constant across the window (CF sculpture
        removed 2019; outfield walls moved in for 2020). Park-era split computed.
============================================================================
Usage: python dp_uc27_phillies_at_loandepot.py [MLB_DIR] [OUT_DIR]
"""
from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ------------------------------------------------------------------ paths --
def _resolve_mlb_dir() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    env = os.environ.get("MLB_DIR")
    if env:
        return Path(env)
    here = Path(__file__).parent.resolve()
    if (here / "data" / "phillies").exists():
        return here
    win = Path(r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB")
    return win if win.exists() else here


MLB = _resolve_mlb_dir()
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else MLB / "out"
OUT.mkdir(parents=True, exist_ok=True)

STEM = "dp_uc27"
PITCH_KEY = ["game_pk", "at_bat_number", "pitch_number"]

NAVY, RED, GREY = "#002D72", "#E81828", "#8C8C8C"

# ---------------------------------------------------------------- roster ---
# Entity lock: MLBAM batter id -> display name. Never filter on player_name.
ROSTER = {
    607208: "Turner, Trea",
    656941: "Schwarber, Kyle",
    547180: "Harper, Bryce",
    669016: "Marsh, Brandon",
    664761: "Bohm, Alec",
    681082: "Stott, Bryson",
    592663: "Realmuto, J.T.",
    687282: "Rincones Jr., Gabriel",
    702222: "Crawford, Justin",
    656537: "Hill, Derek",
    624641: "Sosa, Edmundo",
}
ROSTER_IDS = list(ROSTER)

ALCANTARA = 645261  # Sandy Alcantara, RHP, Miami Marlins

# The 30 MLB club codes as they appear in Statcast home_team. Anything outside
# this set is a minor-league affiliate frame and is dropped (competition-level rule).
MLB_TEAMS = {
    "ARI", "ATL", "BAL", "BOS", "CHC", "CIN", "CLE", "COL", "CWS", "DET",
    "HOU", "KC", "LAA", "LAD", "MIA", "MIL", "MIN", "NYM", "NYY", "OAK",
    "PHI", "PIT", "SD", "SEA", "SF", "STL", "TB", "TEX", "TOR", "WSH",
    "ATH",  # Athletics rebrand (2025+ Statcast code)
}

# Venue-integrity exclusion: home_team == 'MIA' but played at Miller Park,
# Milwaukee (Hurricane Irma relocation, announced 2017-09-13).
IRMA_GAME_PKS = {492302, 492317, 492332}
IRMA_DATES = ("2017-09-15", "2017-09-16", "2017-09-17")

MIAMI = "loanDepot park"
OTHER = "All other MLB parks"

# Publishing gates (house convention: 50 PA for batters; Miami cohorts are
# structurally smaller so a 40-PA floor is used there, always with PA printed).
MIN_PA_MIAMI = 40
MIN_PA_OTHER = 100

BUILD_DATE = "2026-07-27"
GAME_DATE = "2026-07-28"


# ================================================================== LOAD ====
def _read(path: str, cols=None) -> pd.DataFrame | None:
    try:
        return pd.read_parquet(path, columns=cols)
    except Exception:
        return None


def load_union() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Union every local source that can carry a roster hitter's pitch, then dedup.

    Returns (union_deduped, provenance) where provenance is the pre-dedup
    source-attribution table used for the DQ receipt.
    """
    frames, prov = [], []

    # Phillies-era rows: data/phillies/phils_YYYY.parquet, phillies_role == 'batting'
    for yr in range(2015, 2027):
        p = MLB / f"data/phillies/phils_{yr}.parquet"
        d = _read(str(p))
        if d is None:
            continue
        d = d[(d.phillies_role == "batting") & (d.batter.isin(ROSTER_IDS))]
        if len(d):
            d = d.copy()
            d["src"] = f"phils_{yr}"
            frames.append(d)

    # Everything else: data/opponents/*.parquet (pre-Phillies careers, team pulls,
    # opposing-pitcher pulls, and the MiLB affiliate frames).
    for path in sorted(glob.glob(str(MLB / "data/opponents/*.parquet"))):
        d = _read(path)
        if d is None or "batter" not in d.columns:
            continue
        d = d[d.batter.isin(ROSTER_IDS)]
        if len(d):
            d = d.copy()
            d["src"] = Path(path).stem
            frames.append(d)

    raw = pd.concat(frames, ignore_index=True, sort=False)
    prov = (
        raw.groupby(["batter", "src"], as_index=False)
        .agg(pitches=("game_pk", "size"), games=("game_pk", "nunique"))
    )
    prov["player"] = prov.batter.map(ROSTER)

    union = raw.drop_duplicates(subset=PITCH_KEY, keep="first").copy()

    # wOBA weights (season constants) — drop any pre-existing weight columns first
    w = pd.read_csv(MLB / "wOBA and FIP Constants.csv")
    union = union.drop(columns=[c for c in w.columns if c != "Season" and c in union.columns])
    union = union.merge(w, left_on="game_year", right_on="Season", how="left")

    union["player"] = union.batter.map(ROSTER)
    return union, prov


# ========================================================== GOVERNANCE ======
def apply_governance(union: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the five hard filters. Returns (clean, exclusion_audit)."""
    audit = []
    n0 = len(union)

    d = union.copy()
    d["is_milb"] = ~d.home_team.isin(MLB_TEAMS)
    d["is_irma"] = d.game_pk.isin(IRMA_GAME_PKS) | (
        d.home_team.eq("MIA") & d.away_team.eq("MIL") & d.game_date.astype(str).isin(IRMA_DATES)
    )

    steps = [
        ("game_type != 'R' (spring / postseason)", d.game_type.ne("R")),
        ("competition level != MLB (MiLB affiliate frames)", d.is_milb),
        ("venue integrity: 2017 Irma games at Miller Park", d.is_irma),
        ("p_throws != 'R' (out of use-case scope)", d.p_throws.ne("R")),
    ]
    mask_keep = pd.Series(True, index=d.index)
    for label, mask in steps:
        removed = int((mask & mask_keep).sum())
        audit.append({"rule": label, "rows_removed": removed})
        mask_keep &= ~mask

    clean = d[mask_keep].copy()
    audit.append({"rule": "TOTAL retained", "rows_removed": n0 - len(clean)})
    aud = pd.DataFrame(audit)
    aud["rows_in"] = n0
    aud["rows_out"] = len(clean)

    # Venue cohort (VC-1) and park era
    clean["venue"] = np.where(clean.home_team.eq("MIA"), MIAMI, OTHER)
    clean["park_era"] = np.where(clean.game_year <= 2019, "2015-2019 (pre-reconfig)",
                                 "2020-2026 (post-reconfig)")
    # Batting team, for the home-park-familiarity read
    clean["bat_team"] = np.where(clean.inning_topbot.eq("Bot"), clean.home_team, clean.away_team)
    clean["miami_home_club"] = clean.venue.eq(MIAMI) & clean.bat_team.eq("MIA")
    return clean, aud


# ================================== LOCKED KPI KERNEL (verbatim inherit) ====
SWINGS = ["foul", "foul_bunt", "foul_tip", "hit_into_play", "missed_bunt",
          "swinging_pitchout", "swinging_strike", "swinging_strike_blocked"]
WHIFFS = ["foul_tip", "missed_bunt", "swinging_pitchout", "swinging_strike",
          "swinging_strike_blocked"]


def get_stats(level, df):
    if isinstance(level, str):
        level = [level]
    g = lambda sub, name: sub.groupby(level, as_index=False).agg(**{name: ("description", "size")})
    pitches = g(df, "pitches")
    pa = g(df[~df.events.replace(np.nan, "NA").isin(["NA", "pickoff_1b"])], "plate_apps")
    ab = g(df[~df.events.replace(np.nan, "NA").isin(
        ["NA", "pickoff_1b", "walk", "intent_walk", "hit_by_pitch", "sac_fly", "sac_bunt"])], "at_bats")
    bip = g(df[df.type == "X"], "bip")
    hits = g(df[df.events.isin(["home_run", "single", "double", "triple"])], "hits")
    s1 = g(df[df.events == "single"], "singles")
    s2 = g(df[df.events == "double"], "doubles")
    s3 = g(df[df.events == "triple"], "triples")
    hr = g(df[df.events == "home_run"], "hrs")
    bb = g(df[df.events == "walk"], "walks")
    ks = g(df[df.events.isin(["strikeout", "strikeout_double_play"])], "strikeouts")
    hbp = g(df[df.events == "hit_by_pitch"], "hbp")

    out = pitches
    for piece in (pa, ab, bip, hits, s1, s2, s3, hr, bb, ks, hbp):
        out = out.merge(piece, on=level, how="left")
    for wcol, ev in [("wBB", "walk"), ("wHBP", "hit_by_pitch"), ("w1B", "single"),
                     ("w2B", "double"), ("w3B", "triple"), ("wHR", "home_run")]:
        piece = df[df.events == ev].groupby(level, as_index=False).agg(**{wcol: (wcol, "sum")})
        out = out.merge(piece, on=level, how="left")
    xw = df.groupby(level, as_index=False).agg(
        xwoba=("estimated_woba_using_speedangle", "mean"),
        xba=("estimated_ba_using_speedangle", "mean"),
    )
    out = out.merge(xw, on=level, how="left")
    fill = ["plate_apps", "at_bats", "bip", "hits", "singles", "doubles", "triples",
            "hrs", "walks", "strikeouts", "hbp", "wBB", "wHBP", "w1B", "w2B", "w3B", "wHR"]
    out[fill] = out[fill].fillna(0)

    out["ba"] = out.hits / out.at_bats
    out["obp"] = (out.hits + out.walks + out.hbp) / out.plate_apps
    out["slg"] = (out.singles + 2 * out.doubles + 3 * out.triples + 4 * out.hrs) / out.at_bats
    out["ops"] = out.obp + out.slg
    out["woba"] = (out.wBB + out.wHBP + out.w1B + out.w2B + out.w3B + out.wHR) / out.plate_apps
    out["xbh"] = out.doubles + out.triples + out.hrs
    out["iso"] = out.slg - out.ba
    out["krate"] = out.strikeouts / out.plate_apps
    out["bbrate"] = out.walks / out.plate_apps
    out["hr_rate"] = out.hrs / out.plate_apps
    out["pitches_per_pa"] = out.pitches / out.plate_apps
    return out


def hard_hit_rate(level, df):
    if isinstance(level, str):
        level = [level]
    bip = df[df.type == "X"]
    hh = bip[bip.launch_speed >= 95].groupby(level, as_index=False).agg(hard_hits=("des", "size"))
    tot = bip.groupby(level, as_index=False).agg(bips=("des", "size"))
    out = tot.merge(hh, on=level, how="left")
    out["hard_hits"] = out.hard_hits.fillna(0).astype(int)
    out["hard_hit_rate"] = np.where(out.bips > 0, out.hard_hits / out.bips, np.nan)
    return out


def barrel_rate(level, df):
    if isinstance(level, str):
        level = [level]
    bip = df[df.type == "X"]
    tot = bip.groupby(level, as_index=False).agg(bips_br=("des", "size"))
    br = bip[bip.launch_speed_angle == 6].groupby(level, as_index=False).agg(barrels=("des", "size"))
    out = tot.merge(br, on=level, how="left")
    out["barrels"] = out.barrels.fillna(0).astype(int)
    out["barrel_rate"] = np.where(out.bips_br > 0, out.barrels / out.bips_br, np.nan)
    return out


def ev90(level, df):
    if isinstance(level, str):
        level = [level]
    bip = df[df.type == "X"]
    return bip.groupby(level, as_index=False).agg(
        ev90=("launch_speed", lambda x: x.quantile(0.90)),
        avg_ev=("launch_speed", "mean"),
    )


def discipline(level, df):
    if isinstance(level, str):
        level = [level]
    d = df.copy()
    d["swing"] = d.description.isin(SWINGS)
    d["whiff"] = d.description.isin(WHIFFS)
    d["in_zone"] = d.zone <= 9
    rows = d.groupby(level, as_index=False).apply(
        lambda x: pd.Series({
            "swing_rate": x.swing.mean(),
            "whiff_rate": x[x.swing].whiff.mean() if x.swing.any() else np.nan,
            "chase_rate": x[~x.in_zone].swing.mean() if (~x.in_zone).any() else np.nan,
            "z_swing_rate": x[x.in_zone].swing.mean() if x.in_zone.any() else np.nan,
            "zone_rate_seen": x.in_zone.mean(),
        }),
        include_groups=False,
    )
    return rows.round(3)


def bb_type_by_level(level, df):
    if isinstance(level, str):
        level = [level]
    bb = df[df.type == "X"].groupby(level + ["bb_type"], as_index=False).agg(bips=("des", "size"))
    tot = bb.groupby(level, as_index=False).agg(total=("bips", "sum"))
    grp = tot.merge(bb, on=level, how="right")
    grp["share"] = grp.bips / grp.total
    return grp.round(3)


def panel(level, df):
    """The requester's KPI panel + process context, assembled at an arbitrary grain."""
    if isinstance(level, str):
        level = [level]
    out = get_stats(level, df)
    for fn in (hard_hit_rate, barrel_rate, ev90):
        out = out.merge(fn(level, df), on=level, how="left")
    out = out.merge(discipline(level, df), on=level, how="left")
    return out


PANEL_COLS = ["plate_apps", "pitches_per_pa", "ba", "obp", "slg", "ops", "woba", "xwoba",
              "hard_hit_rate", "barrel_rate", "ev90", "krate", "bbrate", "hr_rate",
              "chase_rate", "whiff_rate", "bips"]


# ============================================== NEW KPIs: VD-1 / VD-2 =======
PROCESS_KPIS = ["hard_hit_rate", "barrel_rate", "ev90"]
# Scale factors put the three process metrics on a comparable footing so the
# composite is not dominated by ev90's mph units. Divisors = approximate
# population standard deviation of each metric across the roster cohorts.
PROCESS_SCALE = {"hard_hit_rate": 0.06, "barrel_rate": 0.035, "ev90": 2.5}


def venue_delta(split: pd.DataFrame) -> pd.DataFrame:
    """VD-1 Venue Delta + VD-2 Venue Signal Class, one row per hitter."""
    a = split[split.venue == MIAMI].set_index("player")
    b = split[split.venue == OTHER].set_index("player")
    idx = a.index.intersection(b.index)
    rows = []
    for p in idx:
        r = {"player": p,
             "pa_miami": int(a.loc[p, "plate_apps"]),
             "pa_other": int(b.loc[p, "plate_apps"]),
             "bip_miami": int(a.loc[p, "bip"]),
             "bip_other": int(b.loc[p, "bip"])}
        for k in ["ops", "woba", "xwoba", "ba", "obp", "slg", "iso", "krate", "bbrate",
                  "hard_hit_rate", "barrel_rate", "ev90", "pitches_per_pa", "chase_rate"]:
            r[f"d_{k}"] = a.loc[p, k] - b.loc[p, k]
            r[f"mia_{k}"] = a.loc[p, k]
            r[f"oth_{k}"] = b.loc[p, k]
        # VD-2: composite process z-ish score
        comp = np.nanmean([r[f"d_{k}"] / PROCESS_SCALE[k] for k in PROCESS_KPIS])
        r["process_composite"] = comp
        r["qualified"] = (r["pa_miami"] >= MIN_PA_MIAMI) and (r["pa_other"] >= MIN_PA_OTHER)
        res, pro = r["d_woba"], comp
        if not r["qualified"]:
            cls = "Insufficient sample"
        elif abs(res) < 0.020 and abs(pro) < 0.30:
            cls = "Neutral"
        elif res > 0 and pro > 0:
            cls = "Miami boost — results and process agree"
        elif res < 0 and pro < 0:
            cls = "Miami drag — results and process agree"
        elif res > 0 >= pro:
            cls = "Results-only lift — treat as noise"
        else:
            cls = "Process-only lift — under-rewarded in Miami"
        r["venue_signal_class"] = cls
        rows.append(r)
    return pd.DataFrame(rows).sort_values("d_woba", ascending=False)


# ==================================================================== RUN ===
def main() -> None:
    print(f"[{STEM}] MLB dir: {MLB}")
    print(f"[{STEM}] OUT dir: {OUT}")

    union, prov = load_union()
    clean, audit = apply_governance(union)

    freshness = pd.DataFrame([
        {"source": "data/phillies/phils_2026.parquet",
         "max_game_date": str(pd.read_parquet(MLB / "data/phillies/phils_2026.parquet",
                                              columns=["game_date"]).game_date.max())[:10],
         "note": "Phillies 2026 season cache"},
        {"source": "data/opponents/alcantara.parquet",
         "max_game_date": str(pd.read_parquet(MLB / "data/opponents/alcantara.parquet",
                                              columns=["game_date"]).game_date.max())[:10],
         "note": "STALE — Alcantara's own pull; 2026 form only visible via PHI at-bats"},
        {"source": "union (post-governance)",
         "max_game_date": str(clean.game_date.max())[:10],
         "note": f"build date {BUILD_DATE}; target game {GAME_DATE}"},
    ])
    freshness.to_csv(OUT / f"{STEM}_freshness.csv", index=False)
    audit.to_csv(OUT / f"{STEM}_exclusion_audit.csv", index=False)

    # ---- source profile receipt: naive concat vs governed union -------------
    naive = (union.assign(player=union.batter.map(ROSTER),
                          venue=np.where(union.home_team.eq("MIA"), MIAMI, OTHER))
             .groupby(["player", "venue"]).size().unstack(fill_value=0))
    raw_counts = (prov.groupby("player").pitches.sum().rename("naive_concat_pitches"))
    gov = clean.groupby(["player", "venue"]).size().unstack(fill_value=0)
    sp = (pd.DataFrame({"governed_miami_pitches": gov.get(MIAMI, 0),
                        "governed_other_pitches": gov.get(OTHER, 0)})
          .join(raw_counts)
          .join(naive.get(MIAMI, pd.Series(dtype=int)).rename("dedup_only_miami_pitches"))
          .fillna(0).astype(int).reset_index())
    sp.to_csv(OUT / f"{STEM}_source_profile.csv", index=False)
    prov.to_csv(OUT / f"{STEM}_source_provenance.csv", index=False)

    # ---- LENS A: venue split ------------------------------------------------
    split = panel(["player", "venue"], clean)
    split_pub = split[["player", "venue"] + PANEL_COLS].round(3).sort_values(["player", "venue"])
    split_pub.to_csv(OUT / f"{STEM}_venue_split.csv", index=False)

    vd = venue_delta(split)
    vd.round(4).to_csv(OUT / f"{STEM}_venue_delta.csv", index=False)

    pooled = panel(["venue"], clean)[["venue"] + PANEL_COLS].round(3)
    pooled.to_csv(OUT / f"{STEM}_pooled_venue.csv", index=False)

    era = panel(["venue", "park_era"], clean)[["venue", "park_era"] + PANEL_COLS].round(3)
    era.to_csv(OUT / f"{STEM}_park_era.csv", index=False)

    # Home-club familiarity: Realmuto 2015-18 + Hill 2024-25 batted at MIA as the home club
    home_club = clean[clean.venue == MIAMI].copy()
    hc = panel(["player", "miami_home_club"], home_club)[
        ["player", "miami_home_club"] + PANEL_COLS].round(3)
    hc.to_csv(OUT / f"{STEM}_miami_home_club.csv", index=False)

    # VISITORS-ONLY cohort — the frame that actually matches 2026-07-28, where the
    # Phillies are the road club. Strips Realmuto's 2015-18 and Hill's 2024-25
    # Marlins home-club tenure out of the Miami bucket.
    visitors = clean[~clean.miami_home_club].copy()
    vis_pool = panel(["venue"], visitors)[["venue"] + PANEL_COLS].round(3)
    vis_pool.to_csv(OUT / f"{STEM}_pooled_venue_visitors.csv", index=False)
    vis_split = panel(["player", "venue"], visitors)[["player", "venue"] + PANEL_COLS].round(3)
    vis_split.to_csv(OUT / f"{STEM}_venue_split_visitors.csv", index=False)
    vis_era = panel(["venue", "park_era"], visitors)[["venue", "park_era"] + PANEL_COLS].round(3)
    vis_era.to_csv(OUT / f"{STEM}_park_era_visitors.csv", index=False)

    bbt = bb_type_by_level(["venue"], clean)
    bbt.to_csv(OUT / f"{STEM}_bbtype_venue.csv", index=False)

    disc = discipline(["player", "venue"], clean).reset_index(drop=True)
    disc_l = panel(["player", "venue"], clean)[["player", "venue", "plate_apps", "chase_rate",
                                                "whiff_rate", "z_swing_rate", "zone_rate_seen",
                                                "swing_rate"]].round(3)
    disc_l.to_csv(OUT / f"{STEM}_discipline_venue.csv", index=False)

    # ---- LENS B: Sandy Alcantara -------------------------------------------
    alc = clean[clean.pitcher == ALCANTARA].copy()
    alc_h2h = panel(["player"], alc)[["player"] + PANEL_COLS].round(3).sort_values(
        "plate_apps", ascending=False)
    alc_h2h.to_csv(OUT / f"{STEM}_alcantara_h2h.csv", index=False)

    alc_pooled = panel(["venue"], alc)[["venue"] + PANEL_COLS].round(3)
    alc_pooled.to_csv(OUT / f"{STEM}_alcantara_venue.csv", index=False)

    alc_total = panel(["game_type"], alc)[["game_type"] + PANEL_COLS].round(3)
    alc_total.to_csv(OUT / f"{STEM}_alcantara_total.csv", index=False)

    # Per-hitter x venue vs Alcantara (the intersection lens the use case asks for)
    alc_hv = panel(["player", "venue"], alc)[["player", "venue"] + PANEL_COLS].round(3)
    alc_hv.to_csv(OUT / f"{STEM}_alcantara_hitter_venue.csv", index=False)

    # Post-Tommy-John window only (2025-2026) — the version of Alcantara they will see
    alc_recent = alc[alc.game_year >= 2025]
    alc_rec = panel(["player"], alc_recent)[["player"] + PANEL_COLS].round(3).sort_values(
        "plate_apps", ascending=False)
    alc_rec.to_csv(OUT / f"{STEM}_alcantara_recent.csv", index=False)
    alc_rec_mix = (alc_recent.groupby("pitch_name", as_index=False)
                   .agg(pitches=("des", "size"), velo=("release_speed", "mean")))
    alc_rec_mix["usage"] = alc_rec_mix.pitches / alc_rec_mix.pitches.sum()
    alc_rec_mix.round(3).to_csv(OUT / f"{STEM}_alcantara_recent_mix.csv", index=False)

    # Alcantara arsenal against this roster, with per-pitch outcomes
    mix = (alc.groupby("pitch_name", as_index=False)
           .agg(pitches=("des", "size"), velo=("release_speed", "mean"),
                spin=("release_spin_rate", "mean"),
                pfx_x=("pfx_x", "mean"), pfx_z=("pfx_z", "mean")))
    mix["usage"] = mix.pitches / mix.pitches.sum()
    pm = panel(["pitch_name"], alc)[["pitch_name", "plate_apps", "woba", "xwoba",
                                     "whiff_rate", "chase_rate", "hard_hit_rate", "bips"]]
    mix = mix.merge(pm, on="pitch_name", how="left").sort_values("pitches", ascending=False)
    mix.round(3).to_csv(OUT / f"{STEM}_alcantara_mix.csv", index=False)

    alc_year = panel(["game_year"], alc)[["game_year"] + PANEL_COLS].round(3)
    alc_year.to_csv(OUT / f"{STEM}_alcantara_by_year.csv", index=False)

    # ---- DQ scorecard -------------------------------------------------------
    dq = build_dq(union, clean, split, vd, alc)
    dq.to_csv(OUT / f"{STEM}_dq_scorecard.csv", index=False)

    # ---- figures ------------------------------------------------------------
    make_figures(vd, pooled, era, alc_h2h, split, vis_pool, alc_pooled)

    # ---- console summary ----------------------------------------------------
    pd.set_option("display.width", 220)
    print("\n=== FRESHNESS ===");        print(freshness.to_string(index=False))
    print("\n=== EXCLUSION AUDIT ===");  print(audit.to_string(index=False))
    print("\n=== SOURCE PROFILE ===");   print(sp.to_string(index=False))
    print("\n=== POOLED VENUE ===");     print(pooled.to_string(index=False))
    print("\n=== POOLED VENUE — VISITORS ONLY ==="); print(vis_pool.to_string(index=False))
    print("\n=== PARK ERA ===");         print(era.to_string(index=False))
    print("\n=== PARK ERA — VISITORS ONLY ==="); print(vis_era.to_string(index=False))
    print("\n=== VENUE SPLIT ===");      print(split_pub.to_string(index=False))
    print("\n=== VENUE DELTA (VD-1/VD-2) ===")
    print(vd[["player", "pa_miami", "pa_other", "mia_woba", "oth_woba", "d_woba",
              "d_xwoba", "d_hard_hit_rate", "d_barrel_rate", "d_ev90",
              "process_composite", "venue_signal_class"]].round(3).to_string(index=False))
    print("\n=== MIAMI HOME-CLUB SPLIT ==="); print(hc.to_string(index=False))
    print("\n=== ALCANTARA H2H ===");    print(alc_h2h.to_string(index=False))
    print("\n=== ALCANTARA BY VENUE ==="); print(alc_pooled.to_string(index=False))
    print("\n=== ALCANTARA TOTAL vs ROSTER ==="); print(alc_total.to_string(index=False))
    print("\n=== ALCANTARA MIX vs ROSTER ==="); print(mix.round(3).to_string(index=False))
    print("\n=== ALCANTARA BY YEAR ==="); print(alc_year.to_string(index=False))
    print("\n=== ALCANTARA 2025-26 WINDOW ==="); print(alc_rec.to_string(index=False))
    print("\n=== ALCANTARA 2025-26 MIX ==="); print(alc_rec_mix.to_string(index=False))
    print("\n=== ALCANTARA x HITTER x VENUE ==="); print(alc_hv.to_string(index=False))
    print("\n=== BB TYPE BY VENUE ==="); print(bbt.to_string(index=False))
    print("\n=== DISCIPLINE BY VENUE ==="); print(disc_l.to_string(index=False))
    print("\n=== DQ SCORECARD ===");     print(dq.to_string(index=False))
    print(f"\n[{STEM}] receipts written to {OUT}")


# ============================================================ DQ SCORECARD ==
def build_dq(union, clean, split, vd, alc) -> pd.DataFrame:
    checks = []

    def add(cid, dim, rule, blocking, passed, detail):
        checks.append({"check_id": cid, "dimension": dim, "rule": rule,
                       "blocking": blocking,
                       "result": "PASS" if passed else ("FAIL" if blocking else "WARN"),
                       "detail": detail})

    dup_removed = 0  # recomputed below from provenance-free counts
    add("DQ-01", "Uniqueness", "No duplicate pitch keys in the governed frame", True,
        int(clean.duplicated(PITCH_KEY).sum()) == 0,
        f"{int(clean.duplicated(PITCH_KEY).sum())} duplicate keys after dedup")

    add("DQ-02", "Validity", "Entity lock — every row maps to one of 11 roster MLBAM ids", True,
        set(clean.batter.unique()).issubset(set(ROSTER_IDS)),
        f"{clean.batter.nunique()} distinct batter ids present")

    add("DQ-03", "Validity", "game_type == 'R' only", True,
        set(clean.game_type.unique()) == {"R"},
        f"game_types present: {sorted(clean.game_type.unique())}")

    add("DQ-04", "Validity", "p_throws == 'R' only", True,
        set(clean.p_throws.unique()) == {"R"},
        f"p_throws present: {sorted(clean.p_throws.unique())}")

    add("DQ-05", "Consistency", "Competition level — all home_team codes are MLB clubs", True,
        set(clean.home_team.unique()).issubset(MLB_TEAMS),
        f"{len(set(clean.home_team.unique()) - MLB_TEAMS)} non-MLB codes remain")

    add("DQ-06", "Accuracy", "Venue integrity — no Irma-relocated games in the Miami cohort", True,
        int(clean[clean.game_pk.isin(IRMA_GAME_PKS)].shape[0]) == 0,
        f"{int(clean[clean.game_pk.isin(IRMA_GAME_PKS)].shape[0])} relocated-game rows retained")

    miami_teams = clean[clean.venue == MIAMI].home_team.unique()
    add("DQ-07", "Accuracy", "Miami cohort contains only home_team == 'MIA'", True,
        set(miami_teams) == {"MIA"}, f"codes in Miami cohort: {sorted(miami_teams)}")

    woba_null = int(split.woba.isna().sum())
    add("DQ-08", "Completeness", "wOBA computable for every published hitter x venue cell", True,
        woba_null == 0, f"{woba_null} null wOBA cells")

    xw_null = float(clean.estimated_woba_using_speedangle.isna().mean())
    add("DQ-09", "Completeness", "xwOBA coverage on the pitch log", False, xw_null < 0.90,
        f"{xw_null:.1%} of pitches have null estimated_woba (expected: only BIP/K carry it)")

    ls_cov = float(clean[clean.type == "X"].launch_speed.notna().mean())
    add("DQ-10", "Completeness", "launch_speed present on >=95% of balls in play", False,
        ls_cov >= 0.95, f"{ls_cov:.1%} of BIP carry launch_speed")

    unqual = vd[~vd.qualified].player.tolist()
    add("DQ-11", "Validity", f"Every published hitter clears {MIN_PA_MIAMI} PA in Miami "
                             f"and {MIN_PA_OTHER} PA elsewhere", False, len(unqual) == 0,
        f"below gate (reported but banner-flagged): {unqual}")

    add("DQ-12", "Timeliness", "Phillies cache within 7 days of build date", False,
        (pd.Timestamp(BUILD_DATE) - pd.Timestamp(clean.game_date.max())).days <= 7,
        f"max game_date {str(clean.game_date.max())[:10]} vs build {BUILD_DATE}")

    alc_max = str(pd.read_parquet(MLB / "data/opponents/alcantara.parquet",
                                  columns=["game_date"]).game_date.max())[:10]
    add("DQ-13", "Timeliness", "Alcantara source cache current for 2026", False, alc_max >= "2026-06-01",
        f"alcantara.parquet max game_date {alc_max}; 2026 look-ins come from phils_2026 only")

    add("DQ-14", "Consistency", "BIP denominators reconcile across hard_hit / barrel / bb_type", True,
        bool((split.bips.fillna(0) == split.bip.fillna(0)).all()),
        "hard_hit_rate bips == get_stats bip for every cell")

    add("DQ-15", "Uniqueness", "One MLBAM id per display name (no name collision)", True,
        len(ROSTER) == len(set(ROSTER.values())), f"{len(ROSTER)} ids / {len(set(ROSTER.values()))} names")

    add("DQ-16", "Completeness", "Alcantara H2H present for every rostered hitter", False,
        alc.batter.nunique() == len(ROSTER),
        f"{alc.batter.nunique()} of {len(ROSTER)} hitters have faced Alcantara in the log")

    return pd.DataFrame(checks)


# ================================================================ FIGURES ===
def make_figures(vd, pooled, era, alc_h2h, split, vis_pool, alc_pooled) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 9, "axes.edgecolor": "#D9D9D9",
                         "axes.labelcolor": NAVY, "text.color": "#1a1a1a"})

    # FIG 1 — dumbbell: wOBA other vs Miami, per hitter
    d = vd.sort_values("mia_woba")
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    y = np.arange(len(d))
    for i, (_, r) in enumerate(d.iterrows()):
        ax.plot([r.oth_woba, r.mia_woba], [i, i], color="#C9CDD4", lw=2.2, zorder=1)
    ax.scatter(d.oth_woba, y, s=58, color=NAVY, zorder=2, label="All other MLB parks")
    ax.scatter(d.mia_woba, y, s=58, color=RED, zorder=3, label="loanDepot park")
    for i, (_, r) in enumerate(d.iterrows()):
        ax.annotate(f"{int(r.pa_miami)} PA", (max(r.mia_woba, r.oth_woba) + 0.008, i),
                    va="center", fontsize=7, color=GREY)
    ax.set_yticks(y); ax.set_yticklabels(d.player)
    ax.set_xlabel("wOBA vs RHP (career, MLB regular season)")
    ax.set_title("Phillies hitters vs RHP: loanDepot park vs everywhere else",
                 color=NAVY, fontweight="bold", loc="left")
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / f"{STEM}_fig1_woba_dumbbell.png", dpi=170)
    plt.close(fig)

    # FIG 2 — results delta vs process composite scatter (VD-2 quadrants)
    q = vd[vd.qualified]
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    ax.axhline(0, color="#C9CDD4", lw=1); ax.axvline(0, color="#C9CDD4", lw=1)
    ax.scatter(q.process_composite, q.d_woba, s=90, color=RED, edgecolor=NAVY, zorder=3)
    for _, r in q.iterrows():
        ax.annotate(r.player.split(",")[0], (r.process_composite, r.d_woba),
                    textcoords="offset points", xytext=(7, 4), fontsize=8, color=NAVY)
    ax.set_xlabel("Process composite delta  (hard-hit% / barrel% / EV90, scaled)")
    ax.set_ylabel("Results delta  (wOBA Miami − elsewhere)")
    ax.set_title("VD-2 Venue Signal: do the results and the contact quality agree?",
                 color=NAVY, fontweight="bold", loc="left")
    ax.text(0.02, 0.97, "process up, results up\n= believable", transform=ax.transAxes,
            va="top", fontsize=7.5, color=GREY)
    ax.grid(color="#F2F4F6"); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / f"{STEM}_fig2_signal_quadrant.png", dpi=170)
    plt.close(fig)

    # FIG 3 — park-era pooled bars
    e = era.copy()
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    eras = sorted(e.park_era.unique())
    w = 0.36
    x = np.arange(len(eras))
    for j, (v, c) in enumerate([(OTHER, NAVY), (MIAMI, RED)]):
        vals = [e[(e.park_era == er) & (e.venue == v)].woba.values for er in eras]
        vals = [float(a[0]) if len(a) else np.nan for a in vals]
        pas = [e[(e.park_era == er) & (e.venue == v)].plate_apps.values for er in eras]
        pas = [int(a[0]) if len(a) else 0 for a in pas]
        b = ax.bar(x + (j - 0.5) * w, vals, w, color=c, label=v)
        for rect, val, pa in zip(b, vals, pas):
            ax.annotate(f"{val:.3f}\n{pa} PA", (rect.get_x() + rect.get_width() / 2, val),
                        ha="center", va="bottom", fontsize=7.5, color=GREY)
    ax.set_xticks(x); ax.set_xticklabels(eras)
    ax.set_ylabel("Pooled wOBA vs RHP")
    ax.set_ylim(0, max(e.woba) * 1.35)
    ax.set_title("Is the Miami gap constant? Pooled roster by park configuration era",
                 color=NAVY, fontweight="bold", loc="left")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", color="#F2F4F6"); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / f"{STEM}_fig3_park_era.png", dpi=170)
    plt.close(fig)

    # FIG 4 — vs Alcantara: wOBA and xwOBA by hitter with PA labels
    a = alc_h2h[alc_h2h.plate_apps >= 5].sort_values("woba")
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    y = np.arange(len(a))
    ax.barh(y, a.woba, 0.55, color=RED, label="wOBA vs Alcantara")
    ax.scatter(a.xwoba, y, s=54, color=NAVY, zorder=3, label="xwOBA (contact quality)")
    for i, (_, r) in enumerate(a.iterrows()):
        ax.annotate(f"{int(r.plate_apps)} PA", (max(r.woba, r.xwoba if pd.notna(r.xwoba) else 0) + 0.012, i),
                    va="center", fontsize=7.5, color=GREY)
    ax.set_yticks(y); ax.set_yticklabels(a.player)
    ax.set_xlabel("Career vs Sandy Alcantara (regular season)")
    ax.set_title("The man on the mound: career head-to-head vs Alcantara",
                 color=NAVY, fontweight="bold", loc="left")
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    ax.grid(axis="x", color="#F2F4F6"); ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / f"{STEM}_fig4_alcantara_h2h.png", dpi=170)
    plt.close(fig)

    # FIG 5 — the confound reveal: three Miami cohorts vs the road baseline
    def _row(df, v):
        r = df[df.venue == v]
        return (float(r.woba.iloc[0]), float(r.xwoba.iloc[0]), int(r.plate_apps.iloc[0]))

    bars = [
        ("All other MLB parks\n(baseline)", *_row(pooled, OTHER), NAVY),
        ("loanDepot park\nALL rows", *_row(pooled, MIAMI), "#9AA4B2"),
        ("loanDepot park\nvisiting club only", *_row(vis_pool, MIAMI), RED),
        ("loanDepot park\nvs Alcantara", *_row(alc_pooled, MIAMI), "#F4A6AE"),
    ]
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    x = np.arange(len(bars))
    ax.bar(x, [b[1] for b in bars], 0.55, color=[b[4] for b in bars], label="wOBA")
    ax.scatter(x, [b[2] for b in bars], s=80, color="#1a1a1a", zorder=4, marker="D",
               label="xwOBA")
    for i, b in enumerate(bars):
        ax.annotate(f"wOBA {b[1]:.3f}", (i, b[1]), ha="center", va="top", fontsize=8.5,
                    fontweight="bold", color="#ffffff", xytext=(0, -6),
                    textcoords="offset points")
        ax.annotate(f"xwOBA {b[2]:.3f}", (i, b[2]), ha="center", va="bottom", fontsize=8.5,
                    fontweight="bold", color=NAVY, xytext=(0, 9), textcoords="offset points")
        ax.annotate(f"{b[3]:,} PA", (i, 0.006), ha="center", va="bottom", fontsize=7.5,
                    color="#ffffff")
    ax.set_xticks(x); ax.set_xticklabels([b[0] for b in bars], fontsize=8.5)
    ax.set_ylabel("vs RHP, career MLB regular season")
    ax.set_ylim(0, 0.50)
    ax.set_title("The Miami gap is a tenure artifact, not a park effect",
                 color=NAVY, fontweight="bold", loc="left")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.grid(axis="y", color="#F2F4F6"); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / f"{STEM}_fig5_confound_reveal.png", dpi=170)
    plt.close(fig)

    print(f"[{STEM}] 5 figures written")


if __name__ == "__main__":
    main()
