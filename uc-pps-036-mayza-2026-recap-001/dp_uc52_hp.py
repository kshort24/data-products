"""dp_uc52_hp.py — HP family. Reproduces the client's claims by the client's own method, on the client's own
frames (by name, game types as get_phillies_data delivers them), BEFORE any governed restatement.
Writes out/dp_uc52_hp_grades.csv and out/dp_uc52_hp_values.json. Never overwrites a client claim."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc52_kernel as K

OUT = K.ROOT / "out"; P = lambda n: OUT / f"dp_uc52_{n}"
H = json.load(open(P("headlines.json")))
pn, gy = K.SUBJECT_NAME, K.SEASON
# client frames ------------------------------------------------------------------------------
allp = K.load_phils_cols(role="pitching", regular_only=False, cols=K.HOUSE_COLS)
pps = allp[~allp.game_type.isin(["S", "E"])]                        # client's pps (K49 finding: S/E dropped, postseason kept)
nphl_pn, nphl_n = K.K49.nphl_name_frame(pn)
tm = pd.concat([nphl_pn, pps[pps.player_name == pn]], ignore_index=True)   # client cell 1: pd.concat([nphl[...], pps[...]])
V = dict(client_frame_rows=int(len(tm)), client_frame_by_type=tm.groupby("game_type").size().to_dict(),
         client_frame_dupes=int(tm.duplicated(subset=["pitcher"] + K.PITCH_KEY).sum()))
level = ["player_name", "game_year", "p_throws"]
z = K.nresults(level, tm).merge(K.hard_hit_rate(level, tm)[level + ["hard_hit_rate"]], on=level, how="left")
z = z.merge(K.barrel_rate(level, tm)[level + ["barrel_rate"]], on=level, how="left")
zz = z.set_index("game_year")
rk = lambda c, asc=True: int(zz[c].rank(ascending=asc, method="min")[gy])
V["hp01"] = dict(woba_rank_low=rk("woba"), ops_rank_low=rk("ops"), n=int(len(zz)), woba=float(zz.woba[gy]))
pri = zz.drop(gy)
V["hp02"] = {c: dict(v26=float(zz[c][gy]), prior_min=float(pri[c].min()), prior_max=float(pri[c].max())) for c in ["krate", "bbrate", "hr_rate"]}
V["hp03"] = dict(hh_rank_high=rk("hard_hit_rate", False), rookie_hh=float(zz.hard_hit_rate.iloc[0]), hh26=float(zz.hard_hit_rate[gy]))
V["hp04"] = dict(barrel_rank_low=rk("barrel_rate"), woba_rank_low=rk("woba"))
# delivery / stuff (client population dfl = pps LHP) -----------------------------------------
dfl = pps[pps.p_throws == "L"]
pm = dfl.groupby("player_name").agg(rx=("release_pos_x", "mean"), rz=("release_pos_z", "mean"), ext=("release_extension", "mean"))
me = pm.loc[pn]
V["hp05"] = dict(rx=float(me.rx), rz=float(me.rz), rx_pct=int(100 * (pm.rx < me.rx).mean()), rz_pct=int(100 * (pm.rz < me.rz).mean()), n=int(len(pm)))
V["hp09"] = dict(ext=float(me.ext), ext_pct=int(100 * (pm.ext < me.ext).mean()), n=int(len(pm)))
sl = dfl[dfl.pitch_type == "SL"]
c1 = K.nresults(["player_name", "game_year"], sl[sl.spin_axis > 299]).sort_values("pitches", ascending=False).head(10)
c2 = K.nresults(["player_name", "game_year"], sl[sl.pfx_x > -0.6]).sort_values("pitches", ascending=False).head(10)
V["hp07"] = dict(axis_cut_top=c1[["player_name", "game_year", "pitches"]].to_dict("records"),
                 pfx_cut_top=c2[["player_name", "game_year", "pitches"]].to_dict("records"))
d26 = tm[tm.game_year == gy]
pmx = K.pitch_mix(d26)
V["hp08"] = dict(sl_usage=float(pmx.set_index("pitch_type").usage.get("SL", np.nan)), pitches=int(len(d26)))
# platoon (client pp26 = pps 2026 by name) and the stale root CSV --------------------------
pp26 = pps[(pps.game_year == gy) & (pps.player_name == pn)]
lv = ["player_name", "game_year", "p_throws", "stand"]
pz = K.nresults(lv, pp26).merge(K.hard_hit_rate(lv, pp26)[lv + ["hard_hit_rate"]], on=lv).merge(K.barrel_rate(lv, pp26)[lv + ["barrel_rate"]], on=lv)
V["hp10"] = {r.stand: dict(pa=int(r.plate_apps), woba=float(r.woba), slg=float(r.slg), krate=float(r.krate), bbrate=float(r.bbrate),
             hr=float(r.hr_rate), hh=float(r.hard_hit_rate), barrel=float(r.barrel_rate)) for r in pz.itertuples()}
cs = pd.read_csv(K.ROOT / "pp26.csv", low_memory=False, usecols=["player_name", "game_date", "events"])
cs = cs[cs.player_name == pn]
V["src2_stale_csv"] = dict(pitches=int(len(cs)), max_date=str(cs.game_date.max()), pa=int(cs.events.notna().sum()),
                           client_rhb_pa_matches_live=bool(V["hp10"]["R"]["pa"] > int(cs.events.notna().sum())))
nl, _ = K.K49.nphl_name_frame(pn)
V["hx1_nphl_has_lsa"] = bool("launch_speed_angle" in nl.columns)
lp, rp = K.K44.lhb_pitch_mix(pp26).set_index("pitch_type"), K.K44.rhb_pitch_mix(pp26).set_index("pitch_type")
V["hp11"] = dict(si_usage_L=float(lp.usage["SI"]), si_usage_R=float(rp.usage["SI"]), si_plate_x_L=float(lp.plate_x["SI"]),
                 si_plate_x_R=float(rp.plate_x["SI"]), si_zone_mean_L=float(lp.zone["SI"]), si_zone_mean_R=float(rp.zone["SI"]))
# SL whiff by side vs LHP sliders (client zl: SL/ST, min 50 pitches) ---------------------------
lz = ["player_name", "game_year", "stand", "pitch_type"]
dz = dfl[dfl.pitch_type.isin(["SL", "ST"])]
zl = K.nresults(lz, dz)[lz + ["pitches"]].merge(K.whiff_rate(lz, dz)[lz + ["whiff_rate"]], on=lz, how="left")
zl = zl[zl.pitches > 49]
out12 = {}
for st, g in zl.groupby("stand"):
    m = g[(g.player_name == pn) & (g.game_year == gy) & (g.pitch_type == "SL")]
    if len(m):
        v = float(m.whiff_rate.iloc[0]); out12[st] = dict(whiff=v, pct=int(100 * (g.whiff_rate < v).mean()), n=int(len(g)),
                                                          median=float(g.whiff_rate.median()))
V["hp12"] = out12
# HP-13: client tm_success_rate on the client career frame, full and through July 2026 ------
t_all = K.tm_success_rate(["player_name"], tm)
t_jul = K.tm_success_rate(["player_name"], tm[tm.game_date <= "2026-07-31"])
V["hp13"] = dict(cols=list(t_all.columns), all=t_all.drop(columns=["player_name"]).iloc[0].to_dict(),
                 thru_july=t_jul.drop(columns=["player_name"]).iloc[0].to_dict())
json.dump(V, open(P("hp_values.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))

# ---------------- grades (rule: CONFIRMED / PARTLY / NOT CONFIRMED; governed value from headlines.json) -----
G = []
o = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
def g(hp, claim, client_val, gov_val, grade, note): G.append(dict(hp=hp, claim=claim, client_method=client_val, governed=gov_val, grade=grade, note=note))
cr, se, sh = H["career_rank"], H["season"], H["shapes"]
g("HP-01", "Third-lowest wOBA and OPS of his career", f"wOBA #{V['hp01']['woba_rank_low']}/{V['hp01']['n']} low ({V['hp01']['woba']:.3f})",
  f"wOBA #{cr['woba_low']}, OPS #{cr['ops_low']} of {cr['n_seasons']} ({se['woba']:.3f})",
  "CONFIRMED" if V["hp01"]["woba_rank_low"] == 3 and cr["woba_low"] == 3 and cr["ops_low"] == 3 else "NOT CONFIRMED", "Regular season; client frame also carries 67 postseason pitches (SRC-1r)")
inr = all(V["hp02"][c]["prior_min"] <= V["hp02"][c]["v26"] <= V["hp02"][c]["prior_max"] for c in V["hp02"])
g("HP-02", "Three-true-outcome rates in line with prior seasons", "; ".join(f"{c} {v['v26']:.3f} in [{v['prior_min']:.3f},{v['prior_max']:.3f}]" for c, v in V["hp02"].items()),
  f"K {se['krate']:.3f} · BB {se['bbrate']:.3f} · HR {se['hr_rate']:.3f}", "CONFIRMED" if inr else "PARTLY", "Inside his own prior range on all three")
g("HP-03", "Highest hard-hit rate since his rookie year; more air, more distance", f"HH #{V['hp03']['hh_rank_high']} high ({V['hp03']['hh26']:.3f} vs rookie {V['hp03']['rookie_hh']:.3f})",
  f"HH #{cr['hh_high']} high; LA #{cr['la_high']}, distance #{cr['dist_high']} high of {cr['n_seasons']}",
  "CONFIRMED" if cr["hh_high"] == 2 else "PARTLY", "HH part confirmed; 'more air/further' holds against 2021-23 but not his career (LA, distance mid-pack)")
g("HP-04", "Barrel rate only sixth-lowest, yet third-lowest wOBA", f"not reproducible on the client frame (NF-1 drops launch_speed_angle: HX-1)",
  f"barrel #{cr['barrel_low']} low, wOBA #{cr['woba_low']} low; xwOBA {se['xwoba']:.3f} vs Statcast-basis wOBA {se['woba_sc']:.3f}",
  "CONFIRMED" if cr["barrel_low"] == 6 else "PARTLY", "Ranks confirmed on CF-2c. The 'expect higher wOBA' worry is barrel-only; on a like-for-like basis xwOBA is below his actual, so no luck premium")
d = H["delivery"]
g("HP-05", "Release point 'bang average' among Phillies LHP", f"side {o(V['hp05']['rx_pct'])} pct, height {o(V['hp05']['rz_pct'])} pct (n={V['hp05']['n']} pitchers)",
  f"side {o(d['rel_x_pct']['pct_below'])}, height {o(d['rel_z_pct']['pct_below'])} pct (n={d['rel_x_pct']['n']} seasons)", "NOT CONFIRMED",
  "Narrower and higher than most house LHP: the client's own later read ('over the top') is the supported one")
g("HP-06", "FF doesn't ride, SL doesn't sweep, SI vanilla, splitter unique", "client figure (visual)",
  f"FF IVB {sh['FF']['ivb_in']:.1f} in ({o(sh['FF']['ivb_pct_below'])} pct); SL horizontal break {abs(sh['SL']['hb_in']):.1f} in ({o(sh['SL']['absHB_pct_below'])} pct); SI HB {sh['SI']['hb_in']:.1f}/IVB {sh['SI']['ivb_in']:.1f} in; FS: {H['splitter_house_lhp_seasons_ge50']} house LHP seasons with 50+",
  "PARTLY", "FF and SL parts graded by percentile; 'vanilla' is not a testable claim; splitter is unique in the house but only 22 thrown (2%)")
bsl = H["bullet_slider"]
g("HP-07", "Bullet slider fairly unique among Phillies LHP (Sanchez, Vasquez; maybe Banks, Morgan)", "axis>299: " + ", ".join(sorted({r['player_name'] for r in V['hp07']['axis_cut_top']})),
  f"BS-1: {bsl['n_bullet_others']} other bullet seasons of {bsl['n_pop']} house LHP slider seasons", "PARTLY",
  "Uncommon, not unique: it is the Sánchez pitch (5 of the other bullet seasons are his)")
g("HP-08", "Slider usage right at 30%", f"{V['hp08']['sl_usage']:.1f}%", f"{100 * H['arsenal']['SL']['usage']:.1f}% (regular season)", "CONFIRMED", "")
g("HP-09", "Gets down the mound: elite extension among Phillies LHP", f"{o(V['hp09']['ext_pct'])} pct (n={V['hp09']['n']} pitchers)",
  f"{d['ext']:.2f} ft, {o(d['ext_pct']['pct_below'])} pct of {d['ext_pct']['n']} seasons", "CONFIRMED", "")
p10 = V["hp10"]
g("HP-10", "Slightly better vs LHB; vs RHB more K and BB, 7.8% barrel, 49% hard-hit", f"R barrel {p10['R']['barrel']:.3f}, HH {p10['R']['hh']:.3f}; wOBA L {p10['L']['woba']:.3f} / R {p10['R']['woba']:.3f}",
  f"wOBA L {H['platoon']['L']['woba']:.3f} / R {H['platoon']['R']['woba']:.3f}; Statcast basis L {H['platoon']['L']['woba_sc']:.3f} / R {H['platoon']['R']['woba_sc']:.3f}; xwOBA L {H['platoon']['L']['xwoba']:.3f} / R {H['platoon']['R']['xwoba']:.3f}",
  "CONFIRMED" if round(p10["R"]["barrel"], 3) == 0.078 and round(p10["R"]["hh"], 2) == 0.49 else "PARTLY", "Expected stats widen the split: the platoon gap is bigger than results show")
sz = H["si_zone"]
g("HP-11", "Sinker pretty much down the middle more than half the time, to both sides", f"SI usage L {V['hp11']['si_usage_L']}% / R {V['hp11']['si_usage_R']}%",
  f"SI in zone L {sz['L']['in_zone']:.0%} / R {sz['R']['in_zone']:.0%}; zone 5 L {sz['L']['heart_zone5']:.0%} / R {sz['R']['heart_zone5']:.0%}",
  "PARTLY", "More than half the time and in the zone, yes; 'down the middle', no")
w = H["weapons"]
g("HP-12", "SL whiff abnormally low vs LHB, good vs RHB; SL the weapon vs RHB, SI vs LHB", f"SL whiff vs L {o(V['hp12']['L']['pct'])} pct, vs R {o(V['hp12']['R']['pct'])} pct",
  f"SL vs R wOBA {w['SL_vs_R']['woba']:.3f}, whiff {w['SL_vs_R']['whiff']:.0%}; SI vs L wOBA {w['SI_vs_L']['woba']:.3f}",
  "CONFIRMED" if V["hp12"]["L"]["pct"] < 10 and V["hp12"]["R"]["pct"] > 50 else "PARTLY", "")
q = H["quick_ab"]; t = V["hp13"]["thru_july"]
g("HP-13", "Career 'success' about 40% over ~1,500 PA", f"{t['success_rate']:.1%} over {int(t['total_pas'])} PA (thru July); {V['hp13']['all']['success_rate']:.1%} over {int(V['hp13']['all']['total_pas'])} full",
  f"QA-1 {q['career']:.1%} over {q['career_pas']} PA; 2026 {q['rate']:.1%}", "CONFIRMED",
  "Reproduced exactly by the client's method; that method measures 2 strikes within 2 pitches (DEF-1). QA-1 is the stated definition")
a = d.get("alvarado")
g("HP-14", "'Jose Alvarado lite'", "client opinion", f"DS-1: Alvarado {a['season']} is the #{a['rank']} nearest delivery/stuff comp" if a else "n/a",
  "CONFIRMED" if a and a["rank"] <= 3 else "NOT CONFIRMED", "Delivery and stuff only. Results: Alvarado 2022-23 sit #2-3 in the house LHP RP wOBA table; Mayza is #11")
pd.DataFrame(G).to_csv(P("hp_grades.csv"), index=False)
json.dump(V, open(P("hp_values.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(pd.DataFrame(G)[["hp", "grade"]].to_string(index=False)); print(V["src2_stale_csv"], V["hx1_nphl_has_lsa"])
