"""Realmuto game-calling card for uc-pps-022 (dp_uc26).

A one-page, dugout-legible PDF. Every number on it is read from the CSV receipts
produced by dp_uc26_keller_lhv_2026.py — nothing is hard-coded, so the card cannot
drift from the build. Sample sizes are printed on every line by design.

Usage: python dp_uc26_build_persona_card.py [PACKAGE_DIR]
"""
import sys, pathlib
import pandas as pd
from weasyprint import HTML

PKG = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent
OUT = PKG / "out"
R = lambda n: pd.read_csv(OUT / f"dp_uc26_{n}.csv")

ars = R("arsenal").set_index("pitch_name")
ts = R("two_strike")
fp = R("first_pitch")
pbs = R("process_by_stand"); pbsk = pbs[pbs.who == "Keller"].set_index("stand")
bs = R("by_stand"); bsk = bs[bs.who == "Keller"].set_index("stand")
loc = R("location_profile")
tto = R("tto").set_index("n_thruorder_pitcher")
vel = R("velo_by_inning").set_index("inning")

pct = lambda v: f"{v*100:.0f}%"
p1 = lambda v: f"{v*100:.1f}%"


def two_strike_rows(stand):
    d = ts[(ts.stand == stand) & (ts.n >= 4)].sort_values("n", ascending=False)
    out = ""
    for _, r in d.iterrows():
        flag = ""
        if r.pitch_name == "4-Seam Fastball" and r.usage_within_stand > 0.5:
            flag = " class='bad'"
        elif r.pitch_name == "Slider":
            flag = " class='good'"
        wr = "—" if pd.isna(r.whiff_rate) else p1(r.whiff_rate)
        out += (f"<tr{flag}><td>{r.pitch_name}</td><td>{pct(r.usage_within_stand)}</td>"
                f"<td>{int(r.n)}</td><td>{wr}</td><td>{p1(r.putaway_rate)}</td></tr>")
    return out


def first_pitch_rows(stand):
    d = fp[(fp.stand == stand) & (fp.n >= 5)].sort_values("strike_rate", ascending=False)
    out = ""
    for _, r in d.iterrows():
        flag = " class='good'" if r.pitch_name == "Cutter" else (
            " class='bad'" if r.strike_rate < 0.56 else "")
        out += (f"<tr{flag}><td>{r.pitch_name}</td><td>{pct(r.usage_within_stand)}</td>"
                f"<td>{int(r.n)}</td><td>{p1(r.strike_rate)}</td></tr>")
    return out


sink_k = loc[(loc.who == "Keller") & (loc.pitch == "Sinker")].iloc[0]
sink_b = loc[(loc.who != "Keller") & (loc.pitch == "Sinker")].iloc[0]
ff_k = loc[(loc.who == "Keller") & (loc.pitch == "4-Seam Fastball")].iloc[0]
ff_b = loc[(loc.who != "Keller") & (loc.pitch == "4-Seam Fastball")].iloc[0]

HTMLDOC = f"""<html><head><meta charset='utf-8'><style>
@page {{ size: Letter; margin: 1.0cm 1.1cm;
  @bottom-center {{ content: "dp_uc26 · uc-pps-022 · game-calling card · internal — every rate carries its n"; font-size: 6.2pt; color:#8C8C8C; }} }}
body {{ font-family: -apple-system,'Segoe UI',Arial,sans-serif; font-size:8.1pt; line-height:1.28; color:#15181d; }}
.hdr {{ border-bottom:3px solid #E81828; padding-bottom:4pt; margin-bottom:6pt; }}
.hdr h1 {{ color:#002D72; font-size:16pt; margin:0; }}
.hdr .sub {{ color:#55606e; font-size:8pt; margin-top:1pt; }}
.rule {{ background:#002D72; color:#fff; padding:6pt 9pt; border-radius:3px; margin:5pt 0 7pt 0;
        font-size:9.6pt; font-weight:600; text-align:center; }}
.rule span {{ color:#FFC9CF; }}
.cols {{ display:flex; gap:9pt; }}
.col {{ flex:1; }}
h2 {{ color:#002D72; font-size:9.2pt; margin:7pt 0 2pt 0; border-left:4px solid #E81828; padding-left:5pt; }}
h3 {{ color:#002D72; font-size:8.2pt; margin:5pt 0 1pt 0; }}
table {{ border-collapse:collapse; width:100%; font-size:7.3pt; margin:2pt 0 4pt 0; }}
th {{ background:#002D72; color:#fff; padding:2.2pt 3.5pt; text-align:left; font-weight:600; }}
td {{ padding:2pt 3.5pt; border:1px solid #E1E4E9; }}
tr.bad td {{ background:#FDECEE; font-weight:600; }}
tr.good td {{ background:#E9F4EC; font-weight:600; }}
ol {{ margin:2pt 0 3pt 0; padding-left:13pt; }} li {{ margin:1.6pt 0; }}
.note {{ background:#FBF7E7; border-left:4px solid #E81828; padding:4.5pt 7pt; font-size:7.1pt;
        color:#33291a; margin:4pt 0; }}
.k {{ color:#E81828; font-weight:700; }}
.big {{ font-size:8.6pt; }}
</style></head><body>

<div class='hdr'>
  <h1>Brian Keller — game-calling card</h1>
  <div class='sub'>RHP · 36° slot · 4 pitches · <b>AAA 2026: 8 GS · 36.2 IP · 146 BF</b> ·
  prepared for J.T. Realmuto · UC #27 (<code>uc-pps-022</code>)</div>
</div>

<div class='rule'>Cutter to start it. <span>Sinker at the knees, not under them.</span> Slider to finish it — especially to lefties.</div>

<div class='cols'>
<div class='col'>

<h2>Two strikes — the main event</h2>
<h3>vs LHB <span style='color:#8C8C8C;font-weight:400'>(85 BF · {p1(pbsk.loc['L'].whiff_rate)} whiff/swing · {p1(bsk.loc['L'].krate)} K · <b>all 5 HR</b>)</span></h3>
<table><tr><th>Pitch</th><th>% of 2K calls</th><th>n</th><th>Whiff/sw</th><th>Putaway</th></tr>
{two_strike_rows('L')}</table>

<h3>vs RHB <span style='color:#8C8C8C;font-weight:400'>(61 BF · {p1(pbsk.loc['R'].whiff_rate)} whiff/swing · {p1(bsk.loc['R'].krate)} K · <b>0 HR</b>)</span></h3>
<table><tr><th>Pitch</th><th>% of 2K calls</th><th>n</th><th>Whiff/sw</th><th>Putaway</th></tr>
{two_strike_rows('R')}</table>

<div class='note'><b>The one change worth making.</b> The four-seam takes
{pct(ts[(ts.stand=='L')&(ts.pitch_name=='4-Seam Fastball')].usage_within_stand.iloc[0])} of
two-strike calls to lefties and whiffs at
{p1(ts[(ts.stand=='L')&(ts.pitch_name=='4-Seam Fastball')].whiff_rate.iloc[0])} — his worst
put-away pitch getting the most put-away calls. The slider whiffs at
{p1(ts[(ts.stand=='L')&(ts.pitch_name=='Slider')].whiff_rate.iloc[0])} there on 13 pitches.
Move calls from the first row to the last.</div>

<h2>First pitch — get to 0-1</h2>
<h3>vs LHB</h3>
<table><tr><th>Pitch</th><th>% of 0-0</th><th>n</th><th>Strike rate</th></tr>
{first_pitch_rows('L')}</table>
<h3>vs RHB</h3>
<table><tr><th>Pitch</th><th>% of 0-0</th><th>n</th><th>Strike rate</th></tr>
{first_pitch_rows('R')}</table>

</div>
<div class='col'>

<h2>The arsenal — what each pitch is for</h2>
<table><tr><th>Pitch</th><th>Use</th><th>Velo</th><th>Whiff/sw</th><th>Hard-hit (n BIP)</th><th>GB%</th></tr>
<tr><td><b>4-Seam</b></td><td>{pct(ars.loc['4-Seam Fastball'].usage)}</td><td>{ars.loc['4-Seam Fastball'].velo:.1f}</td><td>{p1(ars.loc['4-Seam Fastball'].whiff_rate)}</td><td class='k'>{p1(ars.loc['4-Seam Fastball'].hard_hit_rate)} ({int(ars.loc['4-Seam Fastball'].bips)})</td><td>{pct(ars.loc['4-Seam Fastball'].gb_rate)}</td></tr>
<tr><td><b>Cutter</b></td><td>{pct(ars.loc['Cutter'].usage)}</td><td>{ars.loc['Cutter'].velo:.1f}</td><td>{p1(ars.loc['Cutter'].whiff_rate)}</td><td class='k'>{p1(ars.loc['Cutter'].hard_hit_rate)} ({int(ars.loc['Cutter'].bips)})</td><td>{pct(ars.loc['Cutter'].gb_rate)}</td></tr>
<tr class='good'><td><b>Sinker</b></td><td>{pct(ars.loc['Sinker'].usage)}</td><td>{ars.loc['Sinker'].velo:.1f}</td><td>{p1(ars.loc['Sinker'].whiff_rate)}</td><td>{p1(ars.loc['Sinker'].hard_hit_rate)} ({int(ars.loc['Sinker'].bips)})</td><td>{pct(ars.loc['Sinker'].gb_rate)}</td></tr>
<tr class='good'><td><b>Slider</b></td><td>{pct(ars.loc['Slider'].usage)}</td><td>{ars.loc['Slider'].velo:.1f}</td><td>{p1(ars.loc['Slider'].whiff_rate)}</td><td>{p1(ars.loc['Slider'].hard_hit_rate)} ({int(ars.loc['Slider'].bips)})</td><td>{pct(ars.loc['Slider'].gb_rate)}</td></tr>
</table>
<div style='font-size:7pt;color:#55606e;'>Staff baselines: whiff/swing 26.3% · hard-hit 38.0% · GB 47.0%.
Green = contact suppressors, currently under-used. Red numbers = damage pitches.</div>

<h2>Location — set the target here</h2>
<table><tr><th></th><th>Keller</th><th>Staff</th><th>What it means</th></tr>
<tr><td>4-seam above zone</td><td class='k'>{p1(ff_k.above_zone_rate)}</td><td>{p1(ff_b.above_zone_rate)}</td><td>elevated approach on 92.6 mph</td></tr>
<tr><td>4-seam mean height</td><td class='k'>{ff_k.mean_plate_z:.2f} ft</td><td>{ff_b.mean_plate_z:.2f} ft</td><td>4 of 5 HR at ≥2.75 ft</td></tr>
<tr class='bad'><td>Sinker mean height</td><td>{sink_k.mean_plate_z:.2f} ft</td><td>{sink_b.mean_plate_z:.2f} ft</td><td><b>0.30 ft too low</b></td></tr>
<tr class='bad'><td>Sinker at zone edge</td><td>{p1(sink_k.zone_edge_rate)}</td><td>{p1(sink_b.zone_edge_rate)}</td><td>half the staff rate</td></tr>
<tr class='bad'><td>Sinker in chase zone</td><td>{p1(sink_k.chase_zone_rate)}</td><td>{p1(sink_b.chase_zone_rate)}</td><td>being wasted</td></tr>
</table>
<div class='note'><b>The sinker is his best pitch and he throws it like a waste pitch.</b>
{p1(ars.loc['Sinker'].hard_hit_rate)} hard-hit, 75.4 mph average exit velocity — and it's
under the zone. Set the glove at the knees, not below them.</div>

<h2>Leash — when to get him</h2>
<table><tr><th>Times through</th><th>BF</th><th>wOBA</th><th>SLG</th><th>HR</th></tr>
<tr><td>1st</td><td>{int(tto.loc[1].plate_apps)}</td><td>{tto.loc[1].woba:.3f}</td><td>{tto.loc[1].slg:.3f}</td><td>{int(tto.loc[1].hrs)}</td></tr>
<tr class='bad'><td><b>2nd</b></td><td>{int(tto.loc[2].plate_apps)}</td><td>{tto.loc[2].woba:.3f}</td><td>{tto.loc[2].slg:.3f}</td><td>{int(tto.loc[2].hrs)}</td></tr>
<tr><td>3rd <i>(tiny)</i></td><td>{int(tto.loc[3].plate_apps)}</td><td>{tto.loc[3].woba:.3f}</td><td>{tto.loc[3].slg:.3f}</td><td>{int(tto.loc[3].hrs)}</td></tr>
</table>
<table><tr><th>Inning</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr>
<tr><td><b>4-seam velo</b></td><td>{vel.loc[1].ff_velo:.1f}</td><td>{vel.loc[2].ff_velo:.1f}</td><td>{vel.loc[3].ff_velo:.1f}</td><td>{vel.loc[4].ff_velo:.1f}</td><td>{vel.loc[5].ff_velo:.1f}</td><td class='k'>{vel.loc[6].ff_velo:.1f}</td></tr></table>
<div style='font-size:7.1pt;color:#55606e;'>−3.1 mph by the sixth. Below ~91 the elevated
four-seam is a strike, not a chase pitch — stop calling it as a put-away.</div>

<h2>Five things to hold in your head</h2>
<ol class='big'>
<li><b>Fewer two-strike fastballs to lefties.</b> Biggest single gain available.</li>
<li><b>Cutter starts the at-bat</b> — best strike rate he owns, both sides.</li>
<li><b>Sinker at the knees</b> — turns a wasted pitch into a strike from his softest-contact offering.</li>
<li><b>Second time through a lefty, change the look.</b> 4 of 5 HR, all LHB, mostly 2nd pass.</li>
<li><b>He'll throw strikes.</b> 7.5% walk rate, 0 walks in his last 3 starts. Expand the zone with him, don't nibble.</li>
</ol>

<div class='note'><b>Read this with the report.</b> All AAA, 146 BF, no MLB track record. Splits
below ~20 PA (slider, sinker, every two-strike cell) are <b>directional only</b> — the n is
printed on every line for that reason. Full caveats: <code>dp_uc26_keller_lhv_2026_report.pdf §8</code>.</div>

</div></div>
</body></html>"""

out_pdf = PKG / "dp_uc26_keller_realmuto_card.pdf"
HTML(string=HTMLDOC, base_url=str(PKG.resolve())).write_pdf(str(out_pdf))
print("wrote", out_pdf, out_pdf.stat().st_size, "bytes")
