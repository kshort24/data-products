"""uc-pps-018 verification receipt — re-checks every number quoted in
dp_uc19_duran_first_half_report.md against the out/dp_uc19_*.csv receipts.
Run from repo root or out/. Last run 2026-07-13: 51 claims, 51 PASS, 0 FAIL."""
import os, pandas as pd
OUT = "out" if os.path.isdir("out") else "."
ok = []
def chk(name, got, want): ok.append((name, got, want, abs(float(got)-float(want)) < 1e-9))
t = pd.read_csv(f"{OUT}/dp_uc19_duran_era_trend.csv").set_index("era"); r26 = t.loc["PHI 2026 1H"]
for k, w in dict(woba=.227, xwoba=.229, krate=.397, bbrate=.048, whiff_rate=.396,
                 in_zone_rate=.452, putaway_rate=.325, hard_hit_rate=.464,
                 first_pitch_strike_rate=.548, chase_rate=.351, xba=.341,
                 plate_apps=126, pitches=515, games=34, hrs=1).items():
    chk(f"2026 {k}", r26[k], w)
chk("PHI25 xwoba", t.loc["PHI 2025","xwoba"], .226); chk("PHI25 PA", t.loc["PHI 2025","plate_apps"], 81)
chk("MIN22 whiff", t.loc["MIN 2022","whiff_rate"], .347); chk("MIN25 K%", t.loc["MIN 2025","krate"], .262)
a = pd.read_csv(f"{OUT}/dp_uc19_duran_arsenal_by_era.csv"); a26 = a[a.era=="PHI 2026 1H"].set_index("pitch_name")
for p, u in {"Split-Finger":.452,"4-Seam Fastball":.270,"Knuckle Curve":.107,"Sweeper":.103,"Changeup":.068}.items():
    chk(f"2026 usage {p}", a26.loc[p,"usage"], u)
chk("2026 FF velo", round(a26.loc["4-Seam Fastball","velo"],1), 100.2)
chk("2026 FF whiff", a26.loc["4-Seam Fastball","whiff_rate"], .459)
chk("2026 SW whiff", a26.loc["Sweeper","whiff_rate"], .667)
chk("MIN22 FF usage", a[(a.era=="MIN 2022")&(a.pitch_name=="4-Seam Fastball")].usage.iat[0], .493)
g = pd.read_csv(f"{OUT}/dp_uc19_duran_putaway_by_pitch.csv").set_index(["era_group","pitch_name"])
chk("FS putaway 2026", g.loc[("PHI 2026 1H","Split-Finger"),"putaway_rate"], .406)
chk("FS putaway career", g.loc[("Career pre-2026","Split-Finger"),"putaway_rate"], .249)
chk("SW putaway 2026", g.loc[("PHI 2026 1H","Sweeper"),"putaway_rate"], .360)
chk("FF putaway 2026", g.loc[("PHI 2026 1H","4-Seam Fastball"),"putaway_rate"], .327)
chk("KC putaway 2026", g.loc[("PHI 2026 1H","Knuckle Curve"),"putaway_rate"], .217)
st = pd.read_csv(f"{OUT}/dp_uc19_duran_2026_arsenal_by_stand.csv").set_index(["stand","pitch_name"])
chk("R FS usage", st.loc[("R","Split-Finger"),"usage"], .548); chk("R SW usage", st.loc[("R","Sweeper"),"usage"], .256)
chk("R FF usage", st.loc[("R","4-Seam Fastball"),"usage"], .161); chk("L FS xwoba", st.loc[("L","Split-Finger"),"xwoba"], .369)
chk("L FS whiff", st.loc[("L","Split-Finger"),"whiff_rate"], .184); chk("L CH usage", st.loc[("L","Changeup"),"usage"], .092)
chk("L KC whiff", st.loc[("L","Knuckle Curve"),"whiff_rate"], .545); chk("R FS xwoba", st.loc[("R","Split-Finger"),"xwoba"], .232)
m = pd.read_csv(f"{OUT}/dp_uc19_duran_2026_monthly.csv").set_index("month")
for mo, w in {"2026-03":.297,"2026-04":.105,"2026-05":.256,"2026-06":.216,"2026-07":.213}.items():
    chk(f"month {mo} wOBA", m.loc[mo,"woba"], w)
chk("May BB%", m.loc["2026-05","bbrate"], .114)
ch = pd.read_csv(f"{OUT}/dp_uc19_duran_changeup_detail.csv").set_index("stand")
chk("CH n LHB", ch.loc["L","n"], 29); chk("CH sep LHB", ch.loc["L","ch_ff_sep"], 11.2)
chk("CH whiff LHB", ch.loc["L","whiff_rate"], .154); chk("CH total", int(ch.n.sum()), 35)
fails = [x for x in ok if not x[3]]
print(f"{len(ok)} claims checked, {len(ok)-len(fails)} PASS, {len(fails)} FAIL")
for f in fails: print("FAIL:", f)
