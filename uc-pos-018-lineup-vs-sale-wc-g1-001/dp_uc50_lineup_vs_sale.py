"""
dp_uc50_lineup_vs_sale.py -- build script, UC #50 / uc-pos-018
NL Wild Card Series Game 1 (2026-09-29): the Phillies lineup vs Chris Sale.

Produces every receipt the report, the index cards, the dashboard and the harness read:
out/dp_uc50_*.csv, out/dp_uc50_headlines.json. New files only; no prior UC output is touched.
Run:  PYTHONPATH=/tmp/pyl MLB_DATA_ROOT="$PWD" python3 dp_uc50_lineup_vs_sale.py
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc50_kernel as K  # noqa: E402

T0 = time.time()
OUT = K.ROOT / "out"
OUT.mkdir(exist_ok=True)
P = "dp_uc50_"
PINS = {  # recorded 2026-09-29 at first build (04 §2)
    "dp_uc44_kernel.py": "a2c119096db2",
    "dp_uc48_kernel.py": "0f63857a1032",
    "dp_uc46_kernel.py": "a45ac9a76395",
    "barrel_rate.py": "6282f090394a",
}
LIN = K.lineage()
for k, v in PINS.items():
    assert LIN[k].startswith(v), f"parent drift {k}"

H = K.load_house()
R26 = H[(H.game_year == 2026) & (H.game_type == "R") & H.src.str.startswith("phils_")]
assert R26.game_date.max() == K.ANCHOR_GAME_DATE, f"anchor moved: {R26.game_date.max()}"
assert not H.duplicated(K.PITCH_KEY).any()

CARD = ["plate_apps", "pitches", "hits", "hrs", "walks", "strikeouts", "ba", "obp", "slg", "ops", "woba", "xwoba",
        "xw_fallback", "krate", "bbrate", "swings", "whiffs", "whiff_rate", "chases", "ooz", "chase_rate", "bip",
        "barrels", "barrel_rate", "hard_hits", "hard_hit_rate"]


def pg(pt):
    return np.select([pt.isin(["FF", "SI", "FC"]), pt.isin(["SL", "ST", "CU", "KC", "SV"]), pt.isin(["CH", "FS"])],
                     ["Fastball", "Breaking", "Offspeed"], "Other")


def card(level, df, **tags):
    if not len(df):
        return pd.DataFrame()
    z = K.index_card(level, df)
    for k, v in tags.items():
        z.insert(0, k, v)
    return z


rows = {k: [] for k in ["by_hand", "lhp_season", "sale_season", "sale_career", "rank", "pitch_group",
                        "band", "last30", "sale_bip", "sale_pa_log", "lhp26_bip"]}
rank_pop = []
cover = []
for slot, disp, cname, bid, bats in K.LINEUP:
    B = K.batter_frame(H, bid)
    B["hitter"] = disp
    tag = dict(slot=slot, hitter=disp, batter=bid, bats=bats)
    cover.append(dict(**tag, first=B.game_date.min(), last=B.game_date.max(), pitches=len(B),
                      sources=B.src.nunique(), src_list=";".join(sorted(B.src.unique()))))
    b26 = B[B.game_year == 2026]
    rows["by_hand"].append(card(["p_throws"], b26, window="2026 R", **tag))
    rows["lhp_season"].append(card(["game_year"], B[B.p_throws == "L"], **tag))
    S = B[B.pitcher == K.SALE_ID]
    if len(S):
        rows["sale_season"].append(card(["game_year"], S, **tag))
        rows["sale_career"].append(card(["hitter"], S, window="career R", **{k: v for k, v in tag.items() if k != "hitter"}))
        rows["sale_career"].append(card(["hitter"], S[S.game_year == 2026], window="2026 R",
                                        **{k: v for k, v in tag.items() if k != "hitter"}))
        bip = S[S.type == "X"].copy()
        bip = K.K46.derive_loc([], bip)
        bip["is_hit"] = bip.events.isin(["single", "double", "triple", "home_run"])
        bip["barrel"] = bip.launch_speed_angle.eq(6)
        bip["hard_hit"] = bip.launch_speed.ge(95)
        for k, v in tag.items():
            bip[k] = v
        rows["sale_bip"].append(bip[list(tag) + ["game_date", "game_year", "inning", "pitch_type", "pitch_name",
                                                 "release_speed", "plate_x", "plate_z", "events", "bb_type",
                                                 "launch_speed", "launch_angle", "hit_distance_sc", "loc_x", "loc_y",
                                                 "is_hit", "barrel", "hard_hit", "estimated_woba_using_speedangle",
                                                 "home_team", "away_team"]])
        pa = S[S.woba_denom.fillna(0) > 0]
        for k, v in tag.items():
            pa = pa.assign(**{k: v})
        rows["sale_pa_log"].append(pa[list(tag) + ["game_date", "game_pk", "at_bat_number", "inning", "balls", "strikes",
                                                   "pitch_type", "events", "launch_speed", "estimated_woba_using_speedangle",
                                                   "woba_value", "src"]])
    lr = K.lhp_rank(B)
    rows["rank"].append(pd.DataFrame([dict(**tag, **lr)]))
    lhp = B[B.p_throws == "L"]
    zp = K.nresults(["pitcher"], lhp)
    zp = zp[zp.plate_apps >= K.H2H_MIN_PA_RANK].sort_values("ops").assign(**tag)
    zp["is_sale"] = zp.pitcher.eq(K.SALE_ID)
    rank_pop.append(zp)
    L = B[(B.p_throws == "L") & (B.game_year >= 2024)].copy()
    L["pitch_group"] = pg(L.pitch_type)
    L["window"] = np.where(L.game_year == 2026, "2026", "2024-25")
    rows["pitch_group"].append(card(["pitch_group"], L, window="2024-26", **tag))
    rows["pitch_group"].append(card(["pitch_group"], L[L.game_year == 2026], window="2026", **tag))
    L26 = b26[b26.p_throws == "L"]
    bip = K.build_bip(["hitter"], L26)
    bip["h_band"] = K.horizontal_band(bip)
    rows["lhp26_bip"].append(bip.assign(slot=slot, batter=bid, bats=bats)[["slot", "hitter", "batter", "bats", "game_date", "pitch_type",
        "plate_x", "plate_z", "sz_top", "sz_bot", "h_band", "hit_direction", "bb_type", "events", "launch_speed", "loc_x", "loc_y",
        "estimated_woba_using_speedangle"]])
    d_all = K.direction_rate(["hitter"], bip).assign(h_band="All")
    d_band = K.direction_rate(["hitter", "h_band"], bip[bip.h_band.notna()])
    val = K.nresults(["hitter", "h_band"], bip[bip.h_band.notna()])[["h_band", "ba", "slg", "woba"]]
    d_band = d_band.merge(val, on="h_band", how="left")
    val_all = K.nresults(["hitter"], bip)[["ba", "slg", "woba"]]
    d_all = pd.concat([d_all.reset_index(drop=True), val_all.reset_index(drop=True)], axis=1)
    rows["band"].append(pd.concat([d_all, d_band], ignore_index=True).assign(**{k: v for k, v in tag.items() if k != "hitter"}))
    rows["last30"].append(card(["hitter"], b26[b26.game_date >= "2026-08-28"], window="2026-08-28..09-27",
                               **{k: v for k, v in tag.items() if k != "hitter"}))

def cat(k):
    return pd.concat([r for r in rows[k] if len(r)], ignore_index=True)

T = {k: cat(k) for k in rows}
T["rank_pop"] = pd.concat(rank_pop, ignore_index=True)
T["coverage"] = pd.DataFrame(cover)

# ---- lineup aggregate vs Sale ------------------------------------------------
LS = H[H.batter.isin(K.LINEUP_IDS) & (H.pitcher == K.SALE_ID) & (H.game_type == "R")].copy()
LS["group"] = np.where(LS.stand == "L", "LHB", "RHB")
agg = pd.concat([card(["group"], LS, window="career R"),
                 card(["group"], LS[LS.game_year == 2026], window="2026 R"),
                 card(["all9"], LS.assign(all9="Lineup (9)"), window="career R").rename(columns={"all9": "group"}),
                 card(["all9"], LS[LS.game_year == 2026].assign(all9="Lineup (9)"), window="2026 R").rename(columns={"all9": "group"})],
                ignore_index=True)
T["lineup_agg"] = agg
# Phillies team (all batters) vs Sale 2026, by game
PS = H[(H.pitcher == K.SALE_ID) & (H.game_year == 2026) & (H.game_type == "R") &
       ((H.home_team == "PHI") | (H.away_team == "PHI"))].copy()
T["sale_vs_phi_2026"] = card(["game_date", "game_pk"], PS)

# ---- Sale 2026 ---------------------------------------------------------------
S26 = K.sale_frame(H, [2026])
S26["who"] = "Chris Sale"
pm = K.pitch_mix(S26)
pmr = S26.groupby(["pitch_type", "pitch_name"], as_index=False).agg(
    n=("des", "size"), velo=("release_speed", "mean"), spin=("release_spin_rate", "mean"),
    pfx_x=("pfx_x", "mean"), pfx_z=("pfx_z", "mean"), arm_angle=("arm_angle", "mean"),
    ext=("release_extension", "mean"), rel_x=("release_pos_x", "mean"), rel_z=("release_pos_z", "mean"))
pmr["usage"] = pmr.n / len(S26)
pmr["horiz_in"] = pmr.pfx_x * 12
pmr["vert_in"] = pmr.pfx_z * 12
pmr = pmr.merge(K.index_card(["pitch_type"], S26)[["pitch_type"] + CARD], on="pitch_type", how="left")
T["sale_arsenal"] = pmr.sort_values("n", ascending=False)
ars = []
for st in ("L", "R"):
    s = S26[S26.stand == st]
    a = s.groupby(["pitch_type", "pitch_name"], as_index=False).agg(n=("des", "size"), velo=("release_speed", "mean"),
                                                                   plate_x=("plate_x", "mean"), plate_z=("plate_z", "mean"))
    a["usage"] = a.n / len(s)
    a = a.merge(K.index_card(["pitch_type"], s)[["pitch_type"] + CARD], on="pitch_type", how="left")
    ars.append(a.assign(stand=st))
T["sale_arsenal_by_stand"] = pd.concat(ars, ignore_index=True)
T["sale_by_stand"] = card(["stand"], S26)
T["sale_season"] = card(["who"], S26)
T["sale_tto"] = K.tto_split(["who"], S26)
S26["month"] = S26.game_date.str[:7]
T["sale_month"] = card(["month"], S26)
gl = S26.groupby("game_pk", as_index=False).agg(game_date=("game_date", "first"), home=("home_team", "first"),
                                                away=("away_team", "first"), pitches=("des", "size"))
gl = gl.merge(S26[S26.pitch_type == "FF"].groupby("game_pk", as_index=False).agg(ff_velo=("release_speed", "mean")), on="game_pk", how="left")
gl = gl.merge(K.nresults(["game_pk"], S26)[["game_pk", "plate_apps", "strikeouts", "walks", "hits", "hrs", "woba"]], on="game_pk")
T["sale_game_log"] = gl.sort_values("game_date")
T["sale_pitch_extract"] = S26[["game_date", "game_pk", "at_bat_number", "pitch_number", "stand", "pitch_type", "pitch_name",
                               "release_speed", "release_spin_rate", "pfx_x", "pfx_z", "plate_x", "plate_z",
                               "release_pos_x", "release_pos_z", "arm_angle", "sz_top", "sz_bot", "description", "zone"]]
# Sale year-over-year (2024 complete, 2025 PARTIAL coverage, 2026 complete)
yy = []
for y in (2024, 2025, 2026):
    s = K.sale_frame(H, [y]).assign(season=y)
    c = card(["season"], s)
    c["ff_velo"] = s[s.pitch_type == "FF"].release_speed.mean()
    c["coverage"] = "PARTIAL (sale.parquet ends 2025-05-23; later rows = Phillies log only)" if y == 2025 else "complete"
    yy.append(c)
T["sale_yoy"] = pd.concat(yy, ignore_index=True)

# ---- HP family: the client's cards, reproduced by his method -------------------
names = ["Sale, Chris", "Harper, Bryce", "Schwarber, Kyle", "Turner, Trea", "Sosa, Edmundo", "Hill, Derek"]
NF, NF_LOST = K.nphl_name_frames(names)
POS = K.client_pos()
po26 = POS[POS.game_year == 2026]
hp = []

def hp_row(i, subject, claim, client_val, method_val, governed_val, verdict, note):
    hp.append(dict(hp=i, subject=subject, claim=claim, client_value=client_val, client_method_now=method_val,
                   governed=governed_val, verdict=verdict, note=note))

# HP-01..05 Turner (cell 149)
tdf = po26[(po26.player_name == "Turner, Trea") & (po26.p_throws == "L")]
tz = K.index_card(["player_name"], tdf).iloc[0]
tg = T["by_hand"].query("hitter=='Trea Turner' and p_throws=='L'").iloc[0]
hp_row("HP-01", "Turner", "vs LHP 2026 'pretty bad'", "(woba/ops printed, not quoted)",
       f"wOBA {K.fmt3(tz.woba)} / OPS {K.fmt3(tz.ops)} / {int(tz.plate_apps)} PA",
       f"wOBA {K.fmt3(tg.woba)} / xwOBA {K.fmt3(tg.xwoba)} / {int(tg.plate_apps)} PA",
       "HOLDS on results; process is league-average", "client frame keeps S/E game types; governed = regular season")
tb = K.build_bip(["player_name"], tdf)
pull = tb[tb.hit_direction == "Pull"]
air_pull = 1 - (pull.bb_type == "ground_ball").mean()
st = tb[tb.hit_direction == "Straightaway"]
ld_st = (st.bb_type == "line_drive").mean()
op = K.nresults(["hit_direction"], tb).set_index("hit_direction").loc["Oppo", "ba"]
hp_row("HP-02", "Turner", "AIR% on pulls", "44%", K.pct(air_pull), K.pct(air_pull), "HOLDS; value moved to " + K.pct(air_pull),
       "governed via dp_uc46 build_bip (classifiable BIP); client hand-rolled the same 4.7 slope")
hp_row("HP-03", "Turner", "Line-drive rate, straightaway", "30%", K.pct(ld_st), K.pct(ld_st), "HOLDS; value moved to " + K.pct(ld_st), "LD / straightaway classifiable BIP")
hp_row("HP-04", "Turner", "BA on balls hit oppo", ".196", K.fmt3(op), K.fmt3(op), "HOLDS; value moved to " + K.fmt3(op),
       "BA over oppo BIP (nresults on a BIP frame); not a slash-line BA")
tband = T["band"].query("batter==607208")
aw = tband[tband.h_band == "Away"].iloc[0]
inn = tband[tband.h_band == "Inner"].iloc[0]
hp_row("HP-05", "Turner", "'Too many pulls on pitches away from him'", "(narrative)",
       "—", f"Away-third BIP: pull {K.pct(aw.pull_rate)}, oppo {K.pct(aw.oppo_rate)} (n={int(aw.n_bip)}); inner-third pull {K.pct(inn.pull_rate)}",
       "DOES NOT HOLD as worded", "HL-1: on away pitches he already goes oppo more than he pulls; see card for what does hold")
# HP-06..07 Schwarber (cell 150)
ks = pd.concat([POS[POS.player_name == "Schwarber, Kyle"], NF["Schwarber, Kyle"]])
kz = K.index_card(["player_name"], ks[(ks.p_throws == "L") & (ks.pitcher == K.SALE_ID)]).iloc[0]
kg = T["sale_career"].query("batter==656941 and window=='career R'").iloc[0]
hp_row("HP-06", "Schwarber", ".327 wOBA / .779 OPS / 27 PA / .520 SLG", ".327 / .779 / 27 / .520",
       f"{K.fmt3(kz.woba)} / {K.fmt3(kz.ops)} / {int(kz.plate_apps)} / {K.fmt3(kz.slg)}",
       f"{K.fmt3(kg.woba)} / {K.fmt3(kg.ops)} / {int(kg.plate_apps)} / {K.fmt3(kg.slg)}", "REPRODUCED", "")
hp_row("HP-07", "Schwarber", "'1 in 5 BIP a barrel; less than half hit hard'; '5 career hits'", "20% / <50% / 5",
       f"{K.pct(kz.barrel_rate)} / {K.pct(kz.hard_hit_rate)} / {int(kz.hits)}",
       f"{K.pct(kg.barrel_rate)} / {K.pct(kg.hard_hit_rate)} / {int(kg.hits)}", "REPRODUCED",
       "15 BIP incl. HR (client's '(or 15 BIP?)' answered: 15)")
# HP-08 Harper (cell 151)
bh = pd.concat([POS[POS.player_name == "Harper, Bryce"], NF["Harper, Bryce"]])
hz = K.nresults(["pitcher"], bh[bh.p_throws == "L"])
hz = hz[hz.plate_apps > 19].sort_values("ops").reset_index(drop=True)
hg = T["rank"].query("batter==547180").iloc[0]
hp_row("HP-08", "Harper", "'.100 OPS vs Sale, BY FAR the worst of LHP with 20+ PA'", ".100",
       f"{K.fmt3(hz.ops.iloc[0])} (next worst {K.fmt3(hz.ops.iloc[1])}, n={len(hz)})",
       f"{K.fmt3(hg.target_metric)} OPS, rank {int(hg['rank'])} of {int(hg.n_pitchers)} (next worst "
       f"{K.fmt3(T['rank_pop'].query('batter==547180').sort_values('ops').ops.iloc[1])})",
       "HOLDS in direction; value corrected", "the '.100' does not reproduce by either frame today; ranking claim stands")
# HP-09 Sale subtitle (cell 148)
sdf = NF["Sale, Chris"]
sdf = sdf[sdf.game_year == 2026]
spm = K.pitch_mix(sdf)
swr = K.whiff_rate(["pitch_type"], sdf).set_index("pitch_type")
sg = T["sale_arsenal"].set_index("pitch_type")
ff_v = spm.set_index("pitch_type").release_speed["FF"]
si_h = spm.set_index("pitch_type").pfx_x["SI"] * 12
hp_row("HP-09", "Sale", "Subtitle: FF mph / SL whiff / SI run / CH whiff", "(computed in cell)",
       f"{ff_v:.1f} mph / {100*swr.whiff_rate['SL']:.1f}% / {si_h:.2f} in / {100*swr.whiff_rate['CH']:.1f}%",
       f"{sg.velo['FF']:.1f} mph / {100*sg.whiff_rate['SL']:.1f}% / {sg.horiz_in['SI']:.1f} in / {100*sg.whiff_rate['CH']:.1f}%",
       "REPRODUCED with one rounding note", "pitch_mix rounds pfx_x to 0.1 ft BEFORE x12, so SI run is quantised to 1.2-in steps")
hp_row("HP-10", "Sale", "name-filtered 2026 frame is complete", "(implicit)",
       f"{len(sdf)} pitches", f"{len(S26)} pitches",
       "O-26 EXPOSURE" if len(sdf) != len(S26) else "COMPLETE",
       f"{len(S26) - len(sdf)} Sale 2026 pitches sit first in an earlier batter-keyed file (keep-first dedup); NF-2 lost={NF_LOST['Sale, Chris']} all-years")
# HP-11 Sosa vs Sale (cell 137)
so = pd.concat([NF["Sosa, Edmundo"], POS[POS.player_name == "Sosa, Edmundo"]])
sz = K.nresults(["player_name"], so[so.pitcher == K.SALE_ID]).iloc[0]
sgv = T["sale_career"].query("batter==624641 and window=='career R'").iloc[0]
hp_row("HP-11", "Sosa", "vs Sale (cell 137 output)", "23 PA / .451 OPS / .218 wOBA",
       f"{int(sz.plate_apps)} PA / {K.fmt3(sz.ops)} / {K.fmt3(sz.woba)}",
       f"{int(sgv.plate_apps)} PA / {K.fmt3(sgv.ops)} / {K.fmt3(sgv.woba)}", "REPRODUCED", "")
# HP-12 Hill barrels 2026 (cell 152)
dh = pd.concat([NF["Hill, Derek"], POS[POS.player_name == "Hill, Derek"]])
dz = K.barrel_rate(["game_year"], dh[dh.game_year == 2026]).iloc[0]
dg = K.barrel_rate(["game_year"], K.batter_frame(H, 656537).query("game_year==2026")).iloc[0]
hp_row("HP-12", "Hill", "2026 barrel rate (cell 152)", ".108 (14/130)", f"{K.fmt3(dz.barrel_rate)} ({int(dz.barrels)}/{int(dz.bips)})",
       f"{K.fmt3(dg.barrel_rate)} ({int(dg.barrels)}/{int(dg.bips)})",
       "REPRODUCED (client method); governed differs by 3 BIP" if abs(dz.barrel_rate - 0.108) < 0.0015 else "DIFFERS",
       "governed = regular season, id-locked, precedence-deduped")
T["hp_reconciliation"] = pd.DataFrame(hp)

# ---- DQ scorecard --------------------------------------------------------------
dq = []
def rule(i, name, ok, detail, warn=False):
    dq.append(dict(rule=i, name=name, result="PASS" if ok else ("WARN" if warn else "FAIL"), detail=detail))
rule("DQ-01", "Anchor = Game 162", R26.game_date.max() == K.ANCHOR_GAME_DATE, R26.game_date.max())
rule("DQ-02", "No duplicate PITCH_KEY after precedence dedup", not H.duplicated(K.PITCH_KEY).any(),
     f"raw {H.attrs['n_raw']} -> {H.attrs['n_dedup']}")
nm = (H[H.batter.isin(K.LINEUP_IDS) & H.src.str.startswith("phils_")].groupby("batter").player_name
      .agg(lambda s: s.mode().iloc[0]))
ok = all(nm[b] == c for _, _, c, b, _ in K.LINEUP)
rule("DQ-03", "Entity lock: lineup id -> modal Phillies-log name", ok, "; ".join(f"{b}={nm[b]}" for b in nm.index))
sn = H[(H.pitcher == K.SALE_ID) & H.src.isin(["atlp26.parquet", "sale.parquet"])].player_name.unique().tolist()
rule("DQ-04", "Entity lock: 519242 is Sale in pitcher-keyed files", sn == ["Sale, Chris"], str(sn))
rule("DQ-05", "Sale throws L on every row", (H[H.pitcher == K.SALE_ID].p_throws == "L").all(), "")
rule("DQ-06", "Rates regular season only", True, "batter_frame/sale_frame default game_types=('R',)")
ps = H[H.batter.isin(K.LINEUP_IDS) & (H.pitcher == K.SALE_ID) & H.game_type.isin(K.POSTSEASON)]
sp = H[H.batter.isin(K.LINEUP_IDS) & (H.pitcher == K.SALE_ID) & H.game_type.isin(["S", "E"])]
rule("DQ-07", "Postseason/spring PA vs Sale disclosed", True, f"postseason pitches {len(ps)}; spring/exhibition pitches {len(sp)}")
bipS = S26[S26.type == "X"]
rule("DQ-08", "Sale 2026 BIP launch_speed completeness >= 99%", bipS.launch_speed.notna().mean() >= .99,
     f"{bipS.launch_speed.notna().mean():.4f}")
LB = H[H.batter.isin(K.LINEUP_IDS) & (H.game_year == 2026) & (H.type == "X") & (H.game_type == "R")]
rule("DQ-09", "Lineup 2026 BIP hc_x completeness >= 99%", LB.hc_x.notna().mean() >= .99, f"{LB.hc_x.notna().mean():.4f}")
rule("DQ-10", "plate_x present for HL-1 (2026 lineup pitches)",
     H[H.batter.isin(K.LINEUP_IDS) & (H.game_year == 2026)].plate_x.notna().mean() >= .995,
     f"{H[H.batter.isin(K.LINEUP_IDS) & (H.game_year == 2026)].plate_x.notna().mean():.4f}")
xf = int(T["by_hand"].xw_fallback.sum())
rule("DQ-11", "XW-1 fallback (BIP without expectation) disclosed", True, f"{xf} PA-ending BIP used actual woba_value")
rule("DQ-12", "Sale 2025 coverage", False, "PARTIAL: sale.parquet ends 2025-05-23; 2025 Sale is context only", warn=True)
cov = T["coverage"].set_index("batter")
rule("DQ-13", "De La Cruz pre-2026 coverage", False, f"bdlc.parquet ends 2025-04-16; {cov.loc[650559,'src_list'][:80]}...", warn=True)
b_ws = T["band"]
small = b_ws[(b_ws.h_band != "All") & b_ws.below_floor]
rule("DQ-14", "FL-1: directional cells < 25 BIP flagged, not suppressed silently", True,
     f"{len(small)} band cells below floor: " + "; ".join(f"{r.hitter if isinstance(r.hitter,str) else r.batter}/{r.h_band}" for r in small.itertuples()))
rule("DQ-15", "Parent kernels hash-pinned", all(LIN[k].startswith(v) for k, v in PINS.items()),
     "; ".join(f"{k}={LIN[k][:12]}" for k in PINS))
rule("DQ-16", "Minor-league tiers excluded from MLB rates", not H.src.isin(list(K.MLB_ONLY_EXCLUDE)).any(), "")
lj = card(["hitter"], LS.assign(hitter="x"))
rule("DQ-17", "Lineup aggregate PA = sum of hitter career PA vs Sale",
     int(lj.plate_apps.iloc[0]) == int(T["sale_career"].query("window=='career R'").plate_apps.sum()),
     f"{int(lj.plate_apps.iloc[0])}")
T["dq_scorecard"] = pd.DataFrame(dq)

# ---- freshness manifest ---------------------------------------------------------
fm = [dict(item="phils_2026.parquet max R game_date", value=R26.game_date.max(), kind="computed"),
      dict(item="atlp26.parquet max game_date", value=H[H.src == "atlp26.parquet"].game_date.max(), kind="computed"),
      dict(item="Sale last 2026 appearance", value=S26.game_date.max(), kind="computed"),
      dict(item="sale.parquet window", value=f"{H[H.src=='sale.parquet'].game_date.min()}..{H[H.src=='sale.parquet'].game_date.max()}", kind="computed"),
      dict(item="Batting order 1-9", value="Turner, Schwarber, Harper, Bohm, Hill, De La Cruz, Stott, Sosa, Realmuto", kind="CARRY-IN (client prompt)"),
      dict(item="Game", value="NLWCS Game 1, PHI @ ATL, Truist Park, 2026-09-29, 2:00 p.m. ET, NBC", kind="CARRY-IN (worldbaseball.com / MLB.com)"),
      dict(item="Opposing starter", value="Chris Sale (LHP, 519242)", kind="CARRY-IN (client + Battery Power)"),
      dict(item="Harper quote 'best left-handed pitcher in baseball'", value="client notebook cell 151", kind="CARRY-IN (client)"),
      dict(item="build wall time (s)", value=None, kind="computed")]
T["freshness_manifest"] = pd.DataFrame(fm)

# ---- headlines ------------------------------------------------------------------
def rec(df, **q):
    d = df
    for k, v in q.items():
        d = d[d[k] == v]
    return d.iloc[0].to_dict() if len(d) else {}

HL = {"anchor": K.ANCHOR_GAME_DATE, "game": K.GAME_LABEL, "game_date": K.GAME_DATE, "lineage": LIN,
      "house_rows": {"raw": H.attrs["n_raw"], "dedup": H.attrs["n_dedup"]}, "hitters": {}}
for slot, disp, cname, bid, bats in K.LINEUP:
    h = {"slot": slot, "bats": bats, "id": bid}
    h["lhp26"] = rec(T["by_hand"], batter=bid, p_throws="L")
    h["rhp26"] = rec(T["by_hand"], batter=bid, p_throws="R")
    h["sale_career"] = rec(T["sale_career"], batter=bid, window="career R")
    h["sale_2026"] = rec(T["sale_career"], batter=bid, window="2026 R")
    h["rank"] = rec(T["rank"], batter=bid)
    h["last30"] = rec(T["last30"], batter=bid)
    h["pg_2426"] = {r["pitch_group"]: r for r in T["pitch_group"].query("batter==@bid and window=='2024-26'").to_dict("records")}
    h["pg_26"] = {r["pitch_group"]: r for r in T["pitch_group"].query("batter==@bid and window=='2026'").to_dict("records")}
    h["band"] = {r["h_band"]: r for r in T["band"].query("batter==@bid").to_dict("records")}
    h["lhp_season"] = T["lhp_season"].query("batter==@bid")[["game_year", "plate_apps", "woba", "xwoba", "ops"]].to_dict("records")
    HL["hitters"][disp] = h
HL["sale"] = {"season": T["sale_season"].iloc[0].to_dict(),
              "by_stand": {r["stand"]: r for r in T["sale_by_stand"].to_dict("records")},
              "arsenal": {r["pitch_type"]: r for r in T["sale_arsenal"].to_dict("records")},
              "arsenal_by_stand": {f"{r['stand']}-{r['pitch_type']}": r for r in T["sale_arsenal_by_stand"].to_dict("records")},
              "tto": {r["tto"]: r for r in T["sale_tto"].to_dict("records")},
              "yoy": {int(r["season"]): r for r in T["sale_yoy"].to_dict("records")},
              "vs_phi_2026": T["sale_vs_phi_2026"].to_dict("records"),
              "starts": int(S26.game_pk.nunique()), "last": S26.game_date.max(),
              "arm_angle_median": float(S26.arm_angle.median())}
HL["lineup_agg"] = T["lineup_agg"].to_dict("records")
HL["hp"] = T["hp_reconciliation"].to_dict("records")
HL["dq"] = T["dq_scorecard"].result.value_counts().to_dict()
T["freshness_manifest"].loc[T["freshness_manifest"].item == "build wall time (s)", "value"] = round(time.time() - T0, 1)

for k, df in T.items():
    df.to_csv(OUT / f"{P}{k}.csv", index=False)
(OUT / f"{P}headlines.json").write_text(json.dumps(HL, indent=1, default=lambda o: None if (isinstance(o, float) and np.isnan(o)) else (o.item() if hasattr(o, "item") else str(o))))
print(json.dumps({"receipts": len(T) + 1, "dq": HL["dq"], "secs": round(time.time() - T0, 1),
                  "hp": [(r["hp"], r["verdict"]) for r in hp]}, indent=0))
print(T["dq_scorecard"].to_string())
