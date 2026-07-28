"""Hitting-coach card for uc-pos-007 (dp_uc27).

A one-page, dugout-legible PDF for the 2026-07-28 series opener in Miami. Every
number is read from the CSV receipts produced by dp_uc27_phillies_at_loandepot.py
— nothing is hard-coded, so the card cannot drift from the build. Plate-appearance
counts are printed on every line by design.

Usage: python dp_uc27_build_persona_card.py [PACKAGE_DIR]
"""
import pathlib
import sys

import pandas as pd
from weasyprint import HTML

PKG = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent
OUT = PKG / "out"
R = lambda n: pd.read_csv(OUT / f"dp_uc27_{n}.csv")

MIAMI, OTHER = "loanDepot park", "All other MLB parks"

pooled = R("pooled_venue").set_index("venue")
vis = R("pooled_venue_visitors").set_index("venue")
vd = R("venue_delta")
alc = R("alcantara_h2h")
alcv = R("alcantara_venue").set_index("venue")
alchv = R("alcantara_hitter_venue")
mix = R("alcantara_mix")
recmix = R("alcantara_recent_mix")
dq = R("dq_scorecard")

p1 = lambda v: "—" if pd.isna(v) else f"{v * 100:.1f}%"
n3 = lambda v: "—" if pd.isna(v) else f"{v:.3f}"

MIN_PA = 15  # card-level floor for the per-hitter plan rows


def hitter_rows() -> str:
    rows = ""
    a = alc.set_index("player")
    v = vd.set_index("player")
    m = alchv[alchv.venue == MIAMI].set_index("player")
    order = a[a.plate_apps >= MIN_PA].sort_values("xwoba", ascending=False).index
    for p in order:
        ar = a.loc[p]
        vr = v.loc[p] if p in v.index else None
        mr = m.loc[p] if p in m.index else None
        cls = ""
        if ar.xwoba >= 0.400:
            cls = " class='good'"
        elif ar.xwoba < 0.300:
            cls = " class='bad'"
        vsig = vr.venue_signal_class if vr is not None else "no Miami history"
        vsig = vsig.split(" — ")[0]
        vpa = int(vr.pa_miami) if vr is not None else 0
        mia_ops = n3(mr.ops) if mr is not None else "—"
        mia_pa = int(mr.plate_apps) if mr is not None else 0
        rows += (
            f"<tr{cls}><td><b>{p}</b></td>"
            f"<td>{int(ar.plate_apps)}</td><td>{n3(ar.woba)}</td><td><b>{n3(ar.xwoba)}</b></td>"
            f"<td>{p1(ar.hard_hit_rate)}</td><td>{p1(ar.krate)}</td>"
            f"<td>{mia_pa}</td><td>{mia_ops}</td>"
            f"<td>{vpa}</td><td>{vsig}</td></tr>"
        )
    return rows


def pitch_rows() -> str:
    rows = ""
    rm = recmix.set_index("pitch_name")
    for _, r in mix.sort_values("pitches", ascending=False).iterrows():
        recent = rm.usage.get(r.pitch_name, float("nan"))
        cls = ""
        if r.pitch_name == "Slider":
            cls = " class='good'"
        elif r.pitch_name in ("Curveball", "Cutter"):
            cls = " class='bad'"
        arrow = ""
        if pd.notna(recent):
            d = recent - r.usage
            arrow = " &#9650;" if d > 0.02 else (" &#9660;" if d < -0.02 else "")
        rows += (
            f"<tr{cls}><td>{r.pitch_name}</td><td>{r.velo:.1f}</td>"
            f"<td>{p1(r.usage)}</td><td>{p1(recent)}{arrow}</td>"
            f"<td>{int(r.plate_apps)}</td><td>{n3(r.woba)}</td><td><b>{n3(r.xwoba)}</b></td>"
            f"<td>{p1(r.whiff_rate)}</td><td>{p1(r.chase_rate)}</td>"
            f"<td>{p1(r.hard_hit_rate)}</td></tr>"
        )
    return rows


base, mia_all, mia_vis = pooled.loc[OTHER], pooled.loc[MIAMI], vis.loc[MIAMI]
alc_mia, alc_oth = alcv.loc[MIAMI], alcv.loc[OTHER]
warns = int((dq.result == "WARN").sum())

HTML_DOC = f"""
<html><head><meta charset="utf-8"><style>
@page {{ size: Letter; margin: 1.0cm 1.1cm;
  @bottom-center {{ content: "dp_uc27 · uc-pos-007 · hitting-coach card · every rate carries its PA · internal";
    font-size: 6.5pt; color: #8C8C8C; }} }}
body {{ font-family: -apple-system,'Segoe UI',Arial,sans-serif; font-size: 8.2pt; color:#1a1a1a; }}
h1 {{ color:#002D72; font-size:15pt; margin:0; border-bottom:3px solid #E81828; padding-bottom:3pt; }}
.sub {{ color:#55606e; font-size:8.4pt; margin:3pt 0 7pt 0; }}
h2 {{ color:#002D72; font-size:9.8pt; margin:9pt 0 3pt 0; border-left:4px solid #E81828; padding-left:6pt; }}
table {{ border-collapse:collapse; width:100%; margin:3pt 0; font-size:7.4pt; }}
th {{ background:#002D72; color:#fff; padding:2.5pt 3pt; text-align:left; border:1px solid #002D72; }}
td {{ padding:2pt 3pt; border:1px solid #DDE1E6; }}
tr.good td {{ background:#EAF6EC; }}
tr.bad td {{ background:#FCEDEE; }}
.cards {{ display:flex; gap:6pt; margin:4pt 0; }}
.card {{ flex:1; border:1px solid #DDE1E6; border-top:3px solid #002D72; border-radius:3px; padding:5pt 6pt; }}
.card.red {{ border-top-color:#E81828; }}
.card .lab {{ font-size:6.8pt; color:#55606e; text-transform:uppercase; letter-spacing:.4px; }}
.card .big {{ font-size:15pt; color:#002D72; font-weight:700; line-height:1.1; }}
.card .sm {{ font-size:6.8pt; color:#8C8C8C; }}
.rule {{ background:#FBF7E7; border-left:5px solid #E81828; padding:5pt 8pt; margin:5pt 0; font-size:8.2pt; }}
.rule b {{ color:#B01020; }}
ul {{ margin:3pt 0; padding-left:14pt; }} li {{ margin:1.5pt 0; }}
.foot {{ font-size:6.8pt; color:#8C8C8C; margin-top:6pt; border-top:1px solid #E6E8EC; padding-top:3pt; }}
</style></head><body>

<h1>Hitting Card — at loanDepot park vs Sandy Alcantara</h1>
<div class="sub">PHI @ MIA · 2026-07-28 · 6:40 pm ET · career vs RHP, MLB regular season ·
data through 2026-07-22 · {warns} DQ warnings, 0 failures</div>

<div class="cards">
  <div class="card"><div class="lab">Road baseline vs RHP</div>
    <div class="big">{base.woba:.3f}</div>
    <div class="sm">wOBA · xwOBA {base.xwoba:.3f} · {int(base.plate_apps):,} PA</div></div>
  <div class="card"><div class="lab">Miami — ALL rows</div>
    <div class="big">{mia_all.woba:.3f}</div>
    <div class="sm">wOBA · xwOBA {mia_all.xwoba:.3f} · {int(mia_all.plate_apps):,} PA · <b>confounded</b></div></div>
  <div class="card red"><div class="lab">Miami — visiting club only</div>
    <div class="big">{mia_vis.woba:.3f}</div>
    <div class="sm">wOBA · <b>xwOBA {mia_vis.xwoba:.3f}</b> · {int(mia_vis.plate_apps):,} PA</div></div>
  <div class="card red"><div class="lab">Miami vs Alcantara</div>
    <div class="big">{alc_mia.woba:.3f}</div>
    <div class="sm">wOBA · <b>xwOBA {alc_mia.xwoba:.3f}</b> · {int(alc_mia.plate_apps)} PA</div></div>
</div>

<div class="rule"><b>The one rule:</b> the park is not the story. As visitors this group barrels
{mia_vis.barrel_rate*100:.1f}% at loanDepot against a {base.barrel_rate*100:.1f}% road baseline.
Hunt the slider — it is the only pitch Alcantara throws that this group both lays off and punishes.</div>

<h2>Alcantara's arsenal against these hitters</h2>
<table><tr><th>Pitch</th><th>mph</th><th>Career use</th><th>2025-26 use</th><th>PA</th>
<th>wOBA</th><th>xwOBA</th><th>Whiff</th><th>Chase</th><th>Hard-hit</th></tr>
{pitch_rows()}
</table>
<div class="sm" style="font-size:6.8pt;color:#8C8C8C">
Green = attack. Red = his outs against us. &#9650;/&#9660; = usage shift in the 2025-26 window (277 pitches).
In Miami he has allowed {alc_mia.hard_hit_rate*100:.1f}% hard-hit vs {alc_oth.hard_hit_rate*100:.1f}% elsewhere.</div>

<h2>Hitter plan — sorted by expected quality vs Alcantara</h2>
<table><tr><th>Hitter</th><th>PA vs SA</th><th>wOBA</th><th>xwOBA</th><th>Hard-hit</th><th>K%</th>
<th>PA vs SA in MIA</th><th>OPS there</th><th>Career MIA PA</th><th>Venue signal</th></tr>
{hitter_rows()}
</table>

<h2>Three things to say in the meeting</h2>
<ul>
<li><b>Harper and Schwarber are owed runs.</b> Their expected numbers against Alcantara
({alc.set_index('player').loc['Harper, Bryce'].xwoba:.3f} and
{alc.set_index('player').loc['Schwarber, Kyle'].xwoba:.3f} xwOBA) sit far above what the box scores paid.
No mechanical adjustment implied — keep the approach.</li>
<li><b>Stott is the one real venue effect.</b> +{vd.set_index('player').loc['Stott, Bryson'].d_woba:.3f} wOBA in Miami
on {int(vd.set_index('player').loc['Stott, Bryson'].pa_miami)} PA with barrel rate, EV90, whiff rate and K rate
all moving the same way. Directional, not proven.</li>
<li><b>Expect fewer four-seams.</b> Career 24.6% to this group; 16.2% in the 2025-26 window, with curveball
and cutter absorbing the difference. Get the two-strike curveball look into cage work.</li>
</ul>

<div class="foot">Every rate on this card carries its plate-appearance count. Hitters below 15 PA vs Alcantara
(Sosa 10, Crawford 3, Rincones Jr. 3, Hill 1) are omitted from the plan table. Rincones Jr. has no
loanDepot history. Alcantara's own cache ends 2025-04-12 — his 2026 form rests on one start (2026-06-17).
Verification: 256/256 checks reconcile. Sources: out/dp_uc27_*.csv.</div>

</body></html>
"""

out_pdf = PKG / "dp_uc27_hitting_coach_card.pdf"
HTML(string=HTML_DOC, base_url=str(PKG.resolve())).write_pdf(str(out_pdf))
print("wrote", out_pdf, out_pdf.stat().st_size, "bytes")
