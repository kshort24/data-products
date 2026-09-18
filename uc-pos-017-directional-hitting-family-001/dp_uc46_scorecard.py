"""dp_uc46_scorecard -- Directional Contact Notecards.
Hand-drawn SVG, no charting library, no external src/href (family E rule).
Brand Center: Red #E81828, Navy #002D72, Cream #F3E5AB, Gray #8C8C8C/#D9D9D9, Arial.
"""
import json, html
import pandas as pd, numpy as np

OUT='/home/claude/build/out/'
RED,NAVY,CREAM,GRAY,LGRAY='#E81828','#002D72','#F3E5AB','#8C8C8C','#D9D9D9'
DC={'Pull':RED,'Straightaway':GRAY,'Oppo':NAVY}
DIRS=['Pull','Straightaway','Oppo']
BB=['line_drive','fly_ball','ground_ball','popup']
BBL={'line_drive':'Line Drive','fly_ball':'Fly Ball','ground_ball':'Ground Ball','popup':'Popup'}

card=pd.read_csv(OUT+'09_scorecard_source_2026.csv')
rate=pd.read_csv(OUT+'04_direction_rate_player_2026.csv')
rate=rate[~rate.below_floor].sort_values('oppo_rate',ascending=False)
H=json.load(open(OUT+'headlines.json'))
LG_OPPO=H['2026']['oppo_rate']; LG_OPPOLD=H['2026']['oppo_ld_rate']

def nm(p):
    a=p.split(', '); return f'{a[1]} {a[0]}' if len(a)==2 else p

def dirbar(r,w=300,h=22):
    """Stacked directional share bar, drawn to scale."""
    segs=[('Pull',r.pull_rate),('Straightaway',r.straight_rate),('Oppo',r.oppo_rate)]
    x=0.0; out=[]
    for i,(d,v) in enumerate(segs):
        wd=v*w
        out.append(f'<rect x="{x:.2f}" y="0" width="{wd:.2f}" height="{h}" fill="{DC[d]}"/>')
        if wd>34:
            out.append(f'<text x="{x+wd/2:.2f}" y="{h/2+4:.1f}" text-anchor="middle" '
                       f'fill="{"#FFFFFF" if d!="Straightaway" else "#FFFFFF"}" '
                       f'font-size="11" font-weight="700">{v*100:.1f}%</text>')
        x+=wd
    return f'<svg width="{w}" height="{h}" role="img" aria-label="Directional share">{"".join(out)}</svg>'

def rangebar(mu,p5,p95,lo,hi,w=120,h=14,color=NAVY):
    """p5-p95 whisker with a mean tick, on a fixed domain so cards compare."""
    if any(pd.isna(v) for v in (mu,p5,p95)): return '<span class="na">n/a</span>'
    sc=lambda v: max(0,min(1,(v-lo)/(hi-lo)))*w
    x0,x1,xm=sc(p5),sc(p95),sc(mu)
    return (f'<svg width="{w}" height="{h}">'
            f'<rect x="0" y="{h/2-1}" width="{w}" height="2" fill="{LGRAY}"/>'
            f'<rect x="{x0:.1f}" y="{h/2-4}" width="{max(1,x1-x0):.1f}" height="8" fill="{color}" opacity="0.28"/>'
            f'<rect x="{xm-1:.1f}" y="1" width="2" height="{h-2}" fill="{color}"/></svg>')

DOM={'la':(-60,80),'ev':(45,110),'dist':(0,420)}

def block(sub,total):
    rows=[]
    for b in BB:
        m=sub[sub.bb_type==b]
        if not len(m):
            rows.append(f'<tr><td class="bb">{BBL[b]}</td><td class="sh">—</td>'
                        f'<td colspan="3" class="na">no batted balls</td></tr>'); continue
        r=m.iloc[0]
        sh=r.share*100
        shbar=(f'<svg width="52" height="12"><rect x="0" y="3" width="50" height="6" fill="{LGRAY}"/>'
               f'<rect x="0" y="3" width="{r.share*50:.1f}" height="6" fill="{NAVY}"/></svg>')
        rows.append(
            f'<tr><td class="bb">{BBL[b]}<span class="n">n={int(r.bips)}</span></td>'
            f'<td class="sh">{shbar}<b>{sh:.1f}%</b></td>'
            f'<td>{rangebar(r.mu_la,r.p5_la,r.p95_la,*DOM["la"])}<span class="v">{r.mu_la:.1f}°</span></td>'
            f'<td>{rangebar(r.mu_ev,r.p5_ev,r.p95_ev,*DOM["ev"],color=RED)}<span class="v">{r.mu_ev:.1f}</span></td>'
            f'<td>{rangebar(r.mu_dist,r.p5_dist,r.p95_dist,*DOM["dist"],color=GRAY)}<span class="v">{r.mu_dist:.0f}′</span></td></tr>')
    return ''.join(rows)

cards=[]
for r in rate.itertuples():
    sub=card[card.player_name==r.player_name]
    panes=[]
    for i,d in enumerate(DIRS):
        s=sub[sub.hit_direction==d]
        tot=int(s.total_level.iloc[0]) if len(s) else 0
        panes.append(
            f'<div class="pane" data-d="{d}" {"" if i==2 else "hidden"}>'
            f'<table><thead><tr><th>Batted ball</th><th>Share</th>'
            f'<th>Launch angle</th><th>Exit velo</th><th>Distance</th></tr></thead>'
            f'<tbody>{block(s,tot)}</tbody></table>'
            f'<p class="den">Denominator: {tot} {d.lower()} balls in play. '
            f'Shares are over <code>bb_type</code> (0.00% null). Bars are p5–p95, tick is the mean; '
            f'each statistic carries its own n.</p></div>')
    oppo_ld=sub[(sub.hit_direction=='Oppo')&(sub.bb_type=='line_drive')]
    old=float(oppo_ld.share.iloc[0]) if len(oppo_ld) else float('nan')
    dld=old-LG_OPPOLD; do=r.oppo_rate-LG_OPPO
    cards.append(f'''
<article class="card">
  <header>
    <h2>{html.escape(nm(r.player_name))}</h2>
    <span class="meta">2026 · {int(r.n_bip)} classifiable BIP</span>
  </header>
  <div class="bar">{dirbar(r)}
    <div class="legend"><i style="background:{RED}"></i>Pull
      <i style="background:{GRAY}"></i>Straight<i style="background:{NAVY}"></i>Oppo</div>
  </div>
  <div class="kpis">
    <div><span class="lab">Oppo rate</span><span class="big">{r.oppo_rate*100:.1f}%</span>
      <span class="d {'up' if do>=0 else 'dn'}">{do*100:+.1f} vs club</span></div>
    <div><span class="lab">Oppo line-drive rate</span><span class="big">{old*100:.1f}%</span>
      <span class="d {'up' if dld>=0 else 'dn'}">{dld*100:+.1f} vs club</span></div>
  </div>
  <nav class="tabs">{''.join(f'<button data-d="{d}"{" class=on" if d=="Oppo" else ""}>{d}</button>' for d in DIRS)}</nav>
  {''.join(panes)}
</article>''')

doc=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Phillies Directional Contact Notecards 2026</title><style>
:root{{--navy:{NAVY};--red:{RED};--cream:{CREAM};--gray:{GRAY};--lgray:{LGRAY};--ink:#1b1b1b;--bg:#ffffff;--line:#e6e6e6;--panel:#fafafa}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ink:#f2f2f2;--bg:#101318;--line:#2a2f37;--panel:#161a21;--lgray:#39404a}}}}
:root[data-theme="dark"]{{--ink:#f2f2f2;--bg:#101318;--line:#2a2f37;--panel:#161a21;--lgray:#39404a}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:13px/1.5 Arial,Helvetica,sans-serif;padding:0 16px 48px}}
.wrap{{max-width:1180px;margin:0 auto}}
h1{{color:var(--navy);font-size:22px;margin:28px 0 4px}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]) h1{{color:#8fb4ff}}}}
.sub{{color:var(--gray);margin:0 0 4px;font-size:13px}}
.prov{{color:var(--gray);font-size:11.5px;margin:0 0 22px;border-left:3px solid var(--cream);padding-left:10px}}
.grid{{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(520px,1fr))}}
@media(max-width:640px){{.grid{{grid-template-columns:1fr}}}}
.card{{border:1px solid var(--line);border-radius:8px;padding:14px 16px 12px;background:var(--panel)}}
header{{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap}}
h2{{font-size:16px;margin:0;color:var(--navy)}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]) h2{{color:#8fb4ff}}}}
.meta{{color:var(--gray);font-size:11.5px}}
.bar{{margin:10px 0 6px}} .bar svg{{display:block;border-radius:3px;max-width:100%}}
.legend{{font-size:11px;color:var(--gray);margin-top:5px}}
.legend i{{display:inline-block;width:9px;height:9px;border-radius:2px;margin:0 4px 0 10px}}
.legend i:first-child{{margin-left:0}}
.kpis{{display:flex;gap:26px;margin:10px 0 8px;flex-wrap:wrap}}
.lab{{display:block;font-size:11px;color:var(--gray);text-transform:uppercase;letter-spacing:.04em}}
.big{{font-size:21px;font-weight:700;color:var(--navy)}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]) .big{{color:#8fb4ff}}}}
.d{{font-size:11px;margin-left:6px}} .up{{color:var(--navy)}} .dn{{color:var(--red)}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]) .up{{color:#8fb4ff}}}}
.tabs{{display:flex;gap:4px;margin:8px 0 6px;border-bottom:1px solid var(--line)}}
.tabs button{{font:inherit;font-size:11.5px;background:none;border:0;border-bottom:2px solid transparent;
 padding:5px 9px;cursor:pointer;color:var(--gray)}}
.tabs button.on{{color:var(--navy);border-bottom-color:var(--red);font-weight:700}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]) .tabs button.on{{color:#8fb4ff}}}}
table{{width:100%;border-collapse:collapse;font-size:11.5px}}
th{{text-align:left;color:var(--gray);font-weight:400;font-size:10.5px;text-transform:uppercase;
 letter-spacing:.03em;padding:5px 6px 4px;border-bottom:1px solid var(--line)}}
td{{padding:5px 6px;border-bottom:1px solid var(--line);vertical-align:middle;white-space:nowrap}}
td svg{{vertical-align:middle}}
.bb{{font-weight:600}} .bb .n{{color:var(--gray);font-weight:400;margin-left:6px;font-size:10.5px}}
.sh b{{margin-left:6px}} .v{{margin-left:6px;color:var(--gray)}} .na{{color:var(--gray);font-style:italic}}
.den{{color:var(--gray);font-size:10.5px;margin:7px 0 0}}
code{{font-size:10.5px;background:var(--lgray);padding:1px 3px;border-radius:2px}}
footer{{margin-top:30px;color:var(--gray);font-size:11px;border-top:1px solid var(--line);padding-top:12px}}
</style></head><body><div class="wrap">
<h1>Phillies Directional Contact Notecards — 2026</h1>
<p class="sub">Every qualified Phillies hitter's spray direction and the contact quality inside each direction.</p>
<p class="prov"><b>dp_uc46 v1.0.0</b> · uc-pos-017 · Statcast regular season through 2026-09-17 ·
{H['qualified_hitters_2026']} hitters at or above the 25-BIP floor (FL-1) ·
denominators are classifiable balls in play (DEN-1) · verification {H['verification']} PASS ·
club oppo rate {LG_OPPO*100:.1f}%, club oppo line-drive rate {LG_OPPOLD*100:.1f}%</p>
<div class="grid">{''.join(cards)}</div>
<footer>Pull / Straightaway / Oppo are assigned by the governed ±4.7-slope wedge boundary
(<code>hit_direction</code>, DR-1) on coordinates derived from <code>hc_x</code>/<code>hc_y</code> (PA-L1).
Balls in play without hit coordinates cannot be assigned a direction and leave the denominator rather than
deflating the rate. Oppo line-drive rate is line drives over <em>opposite-field</em> balls in play (LD-1).</footer>
</div><script>
document.querySelectorAll('.card').forEach(function(c){{
  c.querySelectorAll('.tabs button').forEach(function(b){{
    b.addEventListener('click',function(){{
      c.querySelectorAll('.tabs button').forEach(function(x){{x.classList.remove('on');}});
      b.classList.add('on');
      c.querySelectorAll('.pane').forEach(function(p){{p.hidden = p.dataset.d !== b.dataset.d;}});
    }});
  }});
}});
</script></body></html>'''
open(OUT+'dp_uc46_directional_notecards.html','w',encoding='utf-8').write(doc)
print('written', len(doc), 'bytes ·', len(cards), 'cards')
