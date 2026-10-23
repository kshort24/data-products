"""
dp_uc54_kernel.py - governed kernel for UC #54 / uc-pos-019
"Exactly as Advertised - Justin Crawford's 2026 rookie season"

INHERITANCE POLICY (control-plane 03_governance.md §0, Rule-1):
  * Section A - INHERITED BY IMPORT, sha256-pinned, never copied:
      dp_uc40_kernel (uc-pos-014; K33 -> K34 -> K37 -> K40 `_fix` lineage): nresults_unrounded (D4-corrected),
        pa_rows, risp_rows, in_zone, whiff_rate_fix (D1), chase_rate_g, swing_rate, zone_swing_whiff, ooz_whiff_rate,
        hard_hit_rate_fix (D2), barrel_rate_g, battedball_profile (CR-1), xcontact (CR-2), derive_loc (PA-L1),
        hit_direction (DR-1), bat_tracking (BT-1), rolling_form (RF-2), breakpoint_scan (RC-5), woba_weights.
      dp_uc34_kernel (uc-pos-011, this player's YTD read): cf_context_pool (CX-1), HILL_DEBUT.
      dp_uc53_kernel (uc-pps-037) and through it K52 -> K51 / K50 / K48 / K44: load_phils_cols (LP-1), xwoba_pa (XW-1),
        woba_statcast (WB-1), house_percentile (KP-1), signature_verdict + strength_from_signatures (PA-1),
        extract (IX-1), two_prop_z, brand constants; cumulative_metric.py (CM-1) and K53's CM-1a wOBA spec.
  * Section A' - INHERITED BY IX-1 EXTRACTION (source-pinned, host never imported or run):
      dp_uc22_harper_own_the_zone.py : tag_regions, region_profile (OZ attack-region geometry, ball width 0.25 ft)
      Baseball Functions.ipynb       : find_similar_hits (the client's own neighbourhood; XO-1)
  * Section B - NON-BREAKING GENERALIZATION:
      CM-1 spec dicts (BA / OBP / SLG / wOBA-house / GB% / HH%) passed through the supported metric-dict API.
      CM-1b  (figure side, dp_uc54_build_figs) - multi-panel ghost lines over CM-1 frames.
      RF-2x  rolling_xwoba - RF-2's PA window over XW-1's per-PA atom, so xwOBA rolls on the same index.
  * Section C - NEW to this UC, PROVISIONAL (specs in 03 §2, written before code):
      TR-1  June-turn ledger - 10 signatures pre-registered in the BID (2026-10-20 23:18 ET), scored with PA-1.
      CC-1  chase cost - run value given up by out-of-zone swings vs the house take in the same count.
      XO-2  sector expected outs - CF-sector air balls with Crawford in CF, scored against the client's
            neighbourhood (XO-1) on balls other centre fielders saw. A PROXY: the log has no catch probability.

Data plane    : C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB   (parquet, parent kernels)
Control plane : C:\\Users\\Kellen\\OneDrive\\Documents\\Agents for Data Products (this file, out/, receipts)
"""
from __future__ import annotations

import ast
import hashlib
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

__version__ = "1.0.0"
HERE = Path(__file__).resolve().parent
DP = HERE.parent
UC53_DIR = DP / "uc-pps-037-alvarado-2026-recap-001"
UC40_DIR = DP / "uc-pos-014-turner-2026-recency-001"
UC34_DIR = DP / "uc-pos-011-crawford-ytd-001"
_MLB_CANDIDATES = [os.environ.get("MLB_DATA_ROOT"), str(DP.parent.parent / "Python Scripts" / "MLB"),
                   r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]
for _p in _MLB_CANDIDATES:
    if _p and (Path(_p) / "dp_uc51_kernel.py").exists():
        os.environ["MLB_DATA_ROOT"] = _p
        break
MLB = Path(os.environ["MLB_DATA_ROOT"])
os.environ.setdefault("DP_UC40_DATA", str(MLB))   # K40 / K34 read their data root from env at import
os.environ.setdefault("DP_UC34_DATA", str(MLB))
for _d in (UC53_DIR, UC40_DIR, UC34_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))
import dp_uc53_kernel as K53  # noqa: E402
import dp_uc40_kernel as K40  # noqa: E402
import dp_uc34_kernel as K34  # noqa: E402

K52, K51, K49, K50, K48, K44, CM = K53.K52, K53.K51, K53.K49, K53.K50, K53.K48, K53.K44, K53.CM
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
PIN = {
    UC53_DIR / "dp_uc53_kernel.py": "03d7e3805240c3c73feb51e2869686b82310b0d92b92c38ac1be2110a24aaead",
    UC40_DIR / "dp_uc40_kernel.py": "895c0edc70795d347903f2fde05d253e9901a6a8182ee272162e46cdd869d820",
    UC34_DIR / "dp_uc34_kernel.py": "263e57d15e038f4e80d120b6447214d0efbd7cb9ed3d83f7b99942a30f654e97",
    MLB / "dp_uc22_harper_own_the_zone.py": "530d05cdc1e4077ab7caefa4a0e383b677e32e7fcefc478e258b5a5578ec72e1",
}


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def assert_lineage() -> dict:
    out = {}
    for f, h in PIN.items():
        got = sha(f)
        assert got == h, f"{Path(f).name} drifted ({got[:12]} != {h[:12]})"
        out[Path(f).name] = got
    out.update(K53.assert_lineage())          # K52 -> K51 -> K49/K50/K48/K44/barrel_rate + cumulative_metric.py
    return out


# ---- Section A: inherited names --------------------------------------------------------------
PITCH_KEY = K53.PITCH_KEY
SWINGS, WHIFFS, NON_PA, NON_AB, HIT_EV, BB_EV, K_EV = K40.SWINGS, K40.WHIFFS, K40.NON_PA, K40.NON_AB, K40.HIT_EV, K40.BB_EV, K40.K_EV
PITCH_GROUP = K40.PITCH_GROUP
nresults_unrounded, pa_rows, risp_rows, in_zone = K40.nresults_unrounded, K40.pa_rows, K40.risp_rows, K40.in_zone
whiff_rate_fix, chase_rate_g, swing_rate, zone_swing_whiff = K40.whiff_rate_fix, K40.chase_rate_g, K40.swing_rate, K40.zone_swing_whiff
ooz_whiff_rate, hard_hit_rate_fix, barrel_rate_g = K40.ooz_whiff_rate, K40.hard_hit_rate_fix, K40.barrel_rate_g
battedball_profile, xcontact, derive_loc, hit_direction = K40.battedball_profile, K40.xcontact, K40.derive_loc, K40.hit_direction
bat_tracking, rolling_form, breakpoint_scan, woba_weights = K40.bat_tracking, K40.rolling_form, K40.breakpoint_scan, K40.woba_weights
PA_FLOOR, BIP_FLOOR = K40.PA_FLOOR, K40.BIP_FLOOR
cf_context_pool, HILL_DEBUT = K34.cf_context_pool, K34.HILL_DEBUT
xwoba_pa, woba_statcast, house_percentile = K53.xwoba_pa, K53.woba_statcast, K53.house_percentile
signature_verdict, strength_from_signatures = K53.signature_verdict, K53.strength_from_signatures
two_prop_z, extract = K44.two_prop_z, K51.extract
cumulative_frame = CM.cumulative_frame
WOBA_SC_SPEC = K53.WOBA_SC_SPEC                                   # CM-1a (Statcast basis; WB-1 endpoints)
PHILLIES_RED, PHILLIES_NAVY, PHILLIES_BLUE, PHILLIES_CREAM = K53.PHILLIES_RED, K53.PHILLIES_NAVY, K53.PHILLIES_BLUE, K53.PHILLIES_CREAM
NEUTRAL_GRAY, LIGHT_GRAY = K53.NEUTRAL_GRAY, K53.LIGHT_GRAY

# ---- Section A': IX-1 extractions ------------------------------------------------------------
_OZ = extract("dp_uc22_harper_own_the_zone.py", ["tag_regions", "region_profile"])
_UC22_SRC = (MLB / "dp_uc22_harper_own_the_zone.py").read_text(encoding="utf-8")
assert "HALF_X, BALL = 0.83, 0.25" in _UC22_SRC, "UC22 attack-region constants changed"   # tuple assign: IX-1 can't lift it
_OZ.update(HALF_X=0.83, BALL=0.25, SWINGS=SWINGS, WHIFFS=WHIFFS)                         # injected, asserted above
tag_regions, region_profile = _OZ["tag_regions"], _OZ["region_profile"]
_BF = extract("Baseball Functions.ipynb", ["find_similar_hits"])
find_similar_hits = _BF["find_similar_hits"]                      # XO-1: EV +/-2, LA +/-1, distance +/-5 ft

# ---- Subject (entity lock by MLBAM id + batting role; names only to reproduce the client frame) ----
SUBJECT_ID = 702222                     # Justin Crawford, bats L (resolved from data at bid time; uc-pos-011)
SUBJECT_NAME = "Crawford, Justin"       # client's pn
SUBJECT_DISPLAY = "Justin Crawford"
WRONG_CRAWFORD_ID = 641487              # ENT-2: data/opponents/crawford.parquet is J.P. Crawford (SEA)
AAA_FILE = "lhvb25.parquet"             # 2025 Triple-A Lehigh Valley batting pull (supporting tier, SRC-3)
SRC2_FILE = "white-sox-of-25-26.parquet"  # SRC-2: holds 3 of his 2026 MLB pitches
SEASON = 2026
DEBUT = "2026-03-26"                    # CI-1
LAST_REGULAR_GAME = "2026-09-27"
ANCHOR_GAME_DATE = "2026-10-01"         # max game_date in phils_2026.parquet at build time (pinned)
TURN_DATE = "2026-06-01"                # client's "~June 1"
POSTSEASON_TYPES = ("F", "D", "L", "W")
CLIENT_OUTS = ["double_play", "field_out", "sac_fly", "sac_fly_double_play", "triple_play"]   # client notebook, verbatim
CBP_DIMS = {-45: 329, -22.5: 374, 0: 401, 22.5: 369, 45: 330}   # cbp-spray_AI.md park-dimension SoT (ft)
EXTRA = ["hc_x", "hc_y", "hit_distance_sc", "hit_location", "fielder_7", "fielder_8", "fielder_9",
         "launch_speed_angle", "woba_value", "woba_denom", "babip_value", "bat_speed", "swing_length",
         "attack_angle", "if_fielding_alignment", "of_fielding_alignment"]
COLS = list(dict.fromkeys(K49.COLS + EXTRA))


def _prep(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["game_date"] = pd.to_datetime(d.game_date)
    d["month"] = d.game_date.dt.month
    d["pitch_group"] = d.pitch_type.map(PITCH_GROUP).fillna("other")
    return d


def load_house(years=range(2015, 2027)) -> pd.DataFrame:
    """LP-1 with K54 COLS, every game type (the build filters). Asserts the pinned anchor."""
    ph = K49.load_phils_cols(years=years, role=None, regular_only=False, cols=COLS)
    assert str(ph.game_date.max())[:10] <= ANCHOR_GAME_DATE, "anchor drift: house log runs past the pinned anchor"
    return _prep(ph)


def subject_rows(pos: pd.DataFrame, game_types=("R",)) -> pd.DataFrame:
    s = pos[(pos.batter == SUBJECT_ID) & (pos.phillies_role == "batting") & pos.game_type.isin(game_types)]
    assert s.duplicated(PITCH_KEY).sum() == 0, "EN-2 fan-out on the subject"
    return s


def aaa_rows() -> pd.DataFrame:
    a = pd.read_parquet(MLB / "data" / "opponents" / AAA_FILE)
    a = a[(a.batter == SUBJECT_ID) & (a.game_type == "R")].drop_duplicates(PITCH_KEY)
    return _prep(a)


def client_frame(pos_all: pd.DataFrame) -> pd.DataFrame:
    """The client's `jc = pd.concat([nphl[nphl.player_name == pn], pos[pos.player_name == pn]])`, reproduced:
    every opponent parquet (nphl de-dupes on PITCH_KEY within itself only), then pos with no game_type filter."""
    frames = []
    for f in sorted((MLB / "data" / "opponents").glob("*.parquet")):
        if not (pd.read_parquet(f, columns=["player_name"]).player_name == SUBJECT_NAME).any():
            continue                                   # two-pass read: name column first, full file only on a hit
        d = pd.read_parquet(f)
        frames.append(d[d.player_name == SUBJECT_NAME].assign(_src=f.name))
    nphl = pd.concat(frames, ignore_index=True).drop_duplicates(PITCH_KEY, keep="first")
    p = pos_all[pos_all.player_name == SUBJECT_NAME].assign(_src="pos")
    jc = pd.concat([nphl, p], ignore_index=True, sort=False)
    return _prep(jc)


# ---- Section B: CM-1 spec dicts (house PA rule = K40 NON_PA; IBB is a PA and in OBP, not in wOBA) --------
_ev = lambda p, s: p["events"].isin(s).astype(float)
_ab = lambda p: (~p["events"].isin(NON_AB)).astype(float)
_tb = lambda p: p["events"].map({"single": 1, "double": 2, "triple": 3, "home_run": 4}).fillna(0).astype(float)
BA_SPEC = dict(num=lambda p: _ev(p, HIT_EV), den=_ab, fmt=".3f", label="BA", min_den=25)
OBP_SPEC = dict(num=lambda p: _ev(p, HIT_EV | BB_EV | {"hit_by_pitch"}),
                den=lambda p: _ab(p) + _ev(p, BB_EV | {"hit_by_pitch", "sac_fly"}), fmt=".3f", label="OBP", min_den=25)
SLG_SPEC = dict(num=_tb, den=_ab, fmt=".3f", label="SLG", min_den=25)
GB_SPEC = dict(num=lambda p: ((p["type"] == "X") & (p["bb_type"] == "ground_ball")).astype(float),
               den=lambda p: (p["type"] == "X").astype(float), fmt=".1%", label="Ground-ball rate", min_den=25)
# CM-D2: CM.METRICS["hard_hit_rate"] raises on nullable-float launch_speed (pd.NA >= 95 cannot astype(int)).
# Same definition (hard-hit = tracked BIP >= 95 mph over ALL BIP, the inherited O-8 denominator), NA-safe:
HH_SPEC = dict(num=lambda p: ((p["type"] == "X") & p["launch_speed"].fillna(0).ge(95)).astype(float),
               den=lambda p: (p["type"] == "X").astype(float), fmt=".1%", label="Hard-hit rate", min_den=25)


def woba_house_spec(woba_w: pd.DataFrame) -> dict:
    """House wOBA (K40 weights by season; uBB in, IBB and sac bunts out of numerator and denominator)."""
    w = woba_w.set_index("Season")

    def num(p):
        out = np.zeros(len(p))
        for i, (e, y) in enumerate(zip(p["events"].to_numpy(), p["game_year"].to_numpy())):
            c = w.loc[int(y)]
            out[i] = {"walk": c.wBB, "hit_by_pitch": c.wHBP, "single": c["w1B"], "double": c["w2B"],
                      "triple": c["w3B"], "home_run": c.wHR}.get(e, 0.0)
        return pd.Series(out, index=p.index)

    # K40's denominator, verbatim: AB + unintentional BB + SF + HBP, where SF counts `sac_fly` only (finding SF-1:
    # `sac_fly_double_play` is in NON_AB but not in SF, so K40 drops it from OBP and wOBA denominators).
    den = lambda p: _ab(p) + _ev(p, {"walk", "sac_fly", "hit_by_pitch"})
    return dict(num=num, den=den, fmt=".3f", label="wOBA", min_den=25)


def cumulative_ops(cf_obp: pd.DataFrame, cf_slg: pd.DataFrame) -> pd.DataFrame:
    """OPS path = running OBP + running SLG on the same PA rows (CM-1 frames share row order)."""
    assert (cf_obp.cum_pa.values == cf_slg.cum_pa.values).all()
    out = cf_obp.copy()
    out["value"] = cf_obp["value"] + cf_slg["value"]
    out.attrs.update(cf_obp.attrs, metric="OPS", fmt=".3f")
    return out


def rolling_xwoba(df: pd.DataFrame, window_pa: int = 100) -> pd.DataFrame:
    """RF-2x. XW-1's per-PA atom (BIP expectation, else actual woba_value; woba_denom) rolled on RF-2's PA index
    (K40 pa_rows order). PA ends with woba_denom 0 contribute 0/0."""
    pa = pa_rows(df).sort_values(["game_date", "game_pk", "at_bat_number"]).copy()
    exp = pd.to_numeric(pa.estimated_woba_using_speedangle, errors="coerce")
    den = pa.woba_denom.fillna(0)
    num = np.where(pa.type.eq("X") & exp.notna(), exp, pd.to_numeric(pa.woba_value, errors="coerce").fillna(0))
    num = np.where(den > 0, num, 0.0)
    S = lambda a: pd.Series(a).rolling(window_pa, min_periods=window_pa).sum()
    r = pd.DataFrame({"pa_idx": np.arange(1, len(pa) + 1), "game_date": pa.game_date.to_numpy()})
    r["roll_xwoba"] = (S(num) / S(den.to_numpy()).replace(0, np.nan)).to_numpy()
    return r.dropna(subset=["roll_xwoba"]).reset_index(drop=True)


# ---- House hitter-season population (UC34 / K40 precedent: Phillies hitter-seasons, >= 50 PA) ----------
def hitter_seasons(pos_r: pd.DataFrame, woba_w: pd.DataFrame, min_pa: int = PA_FLOOR) -> pd.DataFrame:
    lv = ["batter", "game_year"]
    z = nresults_unrounded(lv, pos_r, woba_w)
    nm = pos_r.groupby(lv, as_index=False).agg(player_name=("player_name", "last"))
    z = z.merge(nm, on=lv, how="left")
    z = z.merge(swing_rate(lv, pos_r)[lv + ["swing_rate"]], on=lv, how="left")
    z = z.merge(chase_rate_g(lv, pos_r[pos_r.pitch_type.notna()])[lv + ["chase_rate"]], on=lv, how="left")
    z = z.merge(whiff_rate_fix(lv, pos_r)[lv + ["whiff_rate"]], on=lv, how="left")
    z = z.merge(ooz_whiff_rate(lv, pos_r[pos_r.pitch_type.notna()])[lv + ["ooz_whiff_rate"]], on=lv, how="left")
    z = z.merge(zone_swing_whiff(lv, pos_r[pos_r.pitch_type.notna()])[lv + ["swing_rate_in_zone", "whiff_rate_in_zone"]],
                on=lv, how="left")
    z = z.merge(hard_hit_rate_fix(lv, pos_r)[lv + ["hard_hit_rate"]], on=lv, how="left")
    z = z.merge(barrel_rate_g(lv, pos_r)[lv + ["barrel_rate"]], on=lv, how="left")
    z = z.merge(battedball_profile(lv, pos_r)[lv + ["gb_rate", "ld_rate", "fb_rate", "pu_rate", "mean_la", "mean_ev"]],
                on=lv, how="left")
    z = z.merge(xwoba_pa(lv, pos_r)[lv + ["xwoba"]], on=lv, how="left")
    bt = bat_tracking(lv, pos_r)
    if len(bt):
        z = z.merge(bt[lv + ["bat_speed_mu", "attack_angle_mu", "swing_length_mu"]], on=lv, how="left")
    z["contact_rate"] = 1 - z.whiff_rate
    z["ooz_contact_rate"] = 1 - z.ooz_whiff_rate
    return z[z.plate_apps >= min_pa].reset_index(drop=True)


# ---- Section C: TR-1 June-turn ledger (bars pre-registered in the BID; do not edit after build) ----------
TR_SIGNATURES = [   # (sig, family, metric, direction, bar, label, count numerator, count denominator)
    ("R1", "results", "woba", +1, 0.030, "wOBA", None, None),
    ("R2", "results", "ba", +1, 0.030, "Batting average", None, None),
    ("R3", "results", "obp", +1, 0.030, "On-base percentage", None, None),
    ("R4", "results", "slg", +1, 0.040, "Slugging", None, None),
    ("P1", "process", "xwoba", +1, 0.025, "xwOBA (XW-1)", None, None),
    ("P2", "process", "krate", -1, 0.030, "Strikeout rate", "strikeouts", "plate_apps"),
    ("P3", "process", "bbrate", +1, 0.015, "Walk rate", "walks", "plate_apps"),
    ("P4", "process", "chase_rate", -1, 0.030, "Chase rate", "chases", "ooz"),
    ("P5", "process", "hard_hit_rate", +1, 0.040, "Hard-hit rate", "hard_hits", "bips"),
    ("P6", "process", "whiff_rate", -1, 0.030, "Whiff rate", "whiffs", "swings"),
]
TR_RULE = ("results SUPPORTED/STRONG and process SUPPORTED/STRONG -> EARNED TURN | results only -> RESULTS TURN "
           "(not earned) | process only -> PROCESS TURN (results lag) | neither -> NO TURN")


def tr1_metrics(df: pd.DataFrame, woba_w: pd.DataFrame) -> dict:
    d = df.assign(_k=1)
    n = nresults_unrounded(["_k"], d, woba_w).iloc[0]
    c = chase_rate_g(["_k"], d[d.pitch_type.notna()]).iloc[0]
    h = hard_hit_rate_fix(["_k"], d).iloc[0]
    w = whiff_rate_fix(["_k"], d).iloc[0]
    x = xwoba_pa(["_k"], d).iloc[0]
    return dict(plate_apps=int(n.plate_apps), woba=n.woba, ba=n.ba, obp=n.obp, slg=n.slg, krate=n.krate,
                bbrate=n.bbrate, strikeouts=int(n.strikeouts), walks=int(n.walks), xwoba=x.xwoba,
                chase_rate=c.chase_rate, chases=int(c.chases), ooz=int(c.ooz), hard_hit_rate=h.hard_hit_rate,
                hard_hits=int(h.hard_hits), bips=int(h.bips), whiff_rate=w.whiff_rate, whiffs=int(w.whiffs),
                swings=int(w.swings), babip=n.babip, iso=n.iso)


def tr1_ledger(pre: dict, post: dict) -> tuple[pd.DataFrame, dict]:
    rows = []
    for sid, fam, key, direction, bar, label, xn, nn in TR_SIGNATURES:
        p = None
        if xn:
            _, p = two_prop_z(pre[xn], pre[nn], post[xn], post[nn])
        v = signature_verdict(pre[key], post[key], direction, bar, p)
        rows.append(dict(sig=sid, family=fam, metric=key, label=label, direction=direction, bar=bar,
                         pre=pre[key], post=post[key], delta=post[key] - pre[key], p_value=p, verdict=v))
    t = pd.DataFrame(rows)
    res = strength_from_signatures(t[t.family == "results"].verdict.tolist())
    pro = strength_from_signatures(t[t.family == "process"].verdict.tolist())
    R, P = res in ("STRONG", "SUPPORTED"), pro in ("STRONG", "SUPPORTED")
    call = "EARNED TURN" if R and P else "RESULTS TURN" if R else "PROCESS TURN" if P else "NO TURN"
    return t, dict(results=res, process=pro, call=call, rule=TR_RULE)


# ---- Section C: CC-1 chase cost --------------------------------------------------------------------
def ooz_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Out-of-zone pitches (zone 11-14) with a pitch thrown (AB-1: automatic balls/strikes carry no pitch_type)."""
    return df[(df.zone > 9) & df.pitch_type.notna() & df.delta_run_exp.notna()]


def take_reference(pos_ref: pd.DataFrame) -> pd.DataFrame:
    """E[run value of an out-of-zone TAKE | balls, strikes] over the house batting log (batting side +)."""
    o = ooz_rows(pos_ref)
    t = o[~o.description.isin(SWINGS)]
    return t.groupby(["balls", "strikes"], as_index=False).agg(take_rv=("delta_run_exp", "mean"), takes=("des", "size"))


def chase_cost(level, df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """CC-1. For every chase (out-of-zone swing): cost = E[take rv | count] - rv of the swing.
    Positive = runs given up by swinging instead of taking. Reported as total runs and per 100 chases,
    with the chase rate and out-of-zone pitches beside it."""
    level = [level] if isinstance(level, str) else list(level)
    o = ooz_rows(df).merge(ref[["balls", "strikes", "take_rv"]], on=["balls", "strikes"], how="left")
    o["_swing"] = o.description.isin(SWINGS)
    o["_cost"] = np.where(o._swing, o.take_rv - o.delta_run_exp, 0.0)
    g = o.groupby(level, as_index=False).agg(ooz_pitches=("des", "size"), chases=("_swing", "sum"),
                                             chase_cost_runs=("_cost", "sum"))
    g["chase_rate"] = g.chases / g.ooz_pitches
    g["cost_per_100_chases"] = np.where(g.chases > 0, 100 * g.chase_cost_runs / g.chases, np.nan)
    g["cost_per_100_ooz"] = 100 * g.chase_cost_runs / g.ooz_pitches
    return g


# ---- Section C: XO-1 / XO-2 centre-field expected outs ----------------------------------------------
AIR = ("fly_ball", "line_drive", "popup")
XO_SECTOR_DEG = 15.0          # centre third of fair territory (+/-15 deg of dead centre)
XO_MIN_DIST = 150.0           # outfield depth floor (ft)
# XO-2 v1.0 neighbourhood. Selection rule (03 §2, disclosed): the first variant, in order of closeness to the
# client's find_similar_hits (EV 2 / LA 1 / dist 5), that scores >= 90% of opportunities with >= 10 neighbours.
# v1 client+dir 7.5 (45%) -> v2 client, no dir (76%) -> v3 3/2/10 + dir 10 (92%, CHOSEN) -> v4 3/2/10, no dir (97%).
XO_VARIANTS = {"v1": (2, 1, 5, 7.5), "v2": (2, 1, 5, 999.0), "v3": (3, 2, 10, 10.0), "v4": (3, 2, 10, 999.0)}
XO_CHOSEN = "v3"
XO_EV_TOL, XO_LA_TOL, XO_DIST_TOL, XO_ANGLE_TOL = XO_VARIANTS[XO_CHOSEN]
XO_MIN_NEIGHBOURS = 10        # below this a ball is unscored (disclosed)
XO_MIN_COVERAGE = 0.90
XO_YEARS = tuple(range(2015, 2027))   # comparator pool = every house season (client's own frames span 2015-26)


def spray_angle(d: pd.DataFrame) -> pd.Series:
    loc = derive_loc(d)
    return pd.Series(np.degrees(np.arctan2(loc.loc_x, loc.loc_y)), index=d.index)


def cf_sector_air(d: pd.DataFrame) -> pd.DataFrame:
    b = d[(d.type == "X") & d.bb_type.isin(AIR) & d.hc_x.notna() & d.launch_speed.notna()
          & d.launch_angle.notna() & d.hit_distance_sc.notna()].copy()
    b["spray_deg"] = spray_angle(b)
    b = b[(b.spray_deg.abs() <= XO_SECTOR_DEG) & (b.hit_distance_sc >= XO_MIN_DIST)]
    b["is_out"] = b.events.isin(CLIENT_OUTS)
    return b


def xo2_score(opps: pd.DataFrame, pool: pd.DataFrame, tol=None) -> pd.DataFrame:
    """XO-2. Each opportunity's expected-out probability = out share among pool balls inside the neighbourhood
    (EV / LA / distance / direction tolerances; default XO_CHOSEN) with >= XO_MIN_NEIGHBOURS neighbours."""
    te, tl, td, ta = tol or (XO_EV_TOL, XO_LA_TOL, XO_DIST_TOL, XO_ANGLE_TOL)
    ev, la, ds, ang, out = (pool[c].to_numpy(float) for c in ("launch_speed", "launch_angle", "hit_distance_sc",
                                                              "spray_deg", "is_out"))
    xo, nn = [], []
    for r in opps.itertuples():
        m = ((np.abs(ev - r.launch_speed) <= te) & (np.abs(la - r.launch_angle) <= tl)
             & (np.abs(ds - r.hit_distance_sc) <= td) & (np.abs(ang - r.spray_deg) <= ta))
        k = int(m.sum())
        nn.append(k)
        xo.append(out[m].mean() if k >= XO_MIN_NEIGHBOURS else np.nan)
    o = opps.copy()
    o["neighbours"], o["xout"] = nn, xo
    o["scored"] = o.xout.notna()
    o["oae"] = np.where(o.scored, o.is_out.astype(float) - o.xout, np.nan)
    return o


def xo1_client(pp26: pd.DataFrame, searcher: pd.DataFrame) -> pd.DataFrame:
    """XO-1, the client's method verbatim: balls Crawford fielded (hit_location 8, fielder_8 == him, not a ground
    ball), each scored by find_similar_hits on the searcher frame (out share among similar hits)."""
    df = pp26[(pp26.hit_location == 8) & (pp26.fielder_8 == SUBJECT_ID) & (pp26.bb_type != "ground_ball")].copy()
    of = []
    for r in df.itertuples():
        sh = find_similar_hits(searcher, r.launch_speed, r.launch_angle, r.hit_distance_sc)
        aggd = sh.groupby("events", as_index=False).agg(counter=("des", "count"))
        tot = aggd.counter.sum()
        of.append(aggd[aggd.events.isin(CLIENT_OUTS)].counter.sum() / tot if tot else np.nan)
    df["out_frequency"] = of
    return df


# ---- formatting helpers (narrative + figures read receipts; these only format) ----------------------
def f3(x) -> str:
    s = f"{x:.3f}"
    return s[1:] if s.startswith("0.") else ("-" + s[2:] if s.startswith("-0.") else s)


def pct(x, d=1) -> str:
    return f"{100 * x:.{d}f}%"
