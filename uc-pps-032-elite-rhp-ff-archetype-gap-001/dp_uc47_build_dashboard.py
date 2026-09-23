"""
dp_uc47_build_dashboard.py — the Archetype Explorer (self-contained HTML).

Rules:
  * Reads ONLY out/dp_uc47_* receipts (CSV/JSON). No recomputation of any grade in
    the browser. The ONE live calculation — the weight slider — is the AF-4 formula
    (w*shape_score + (1-w)*results_score) on receipt columns; at w=0.5 it must equal
    the receipt's efc_score (asserted in dp_uc47_verification.py family D).
  * Offline: plotly.js is inlined from the installed plotly package. No CDN, no webfont.
  * Two themes: brand-center `plotly_white` (default) and the client's notebook
    `plotly_dark`, from plotly's own template objects.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import plotly
import plotly.io as pio

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC47_OUT", HERE / "out"))
DEST = HERE / "dp_uc47_archetype_explorer.html"


def csv(n):
    return json.loads(pd.read_csv(OUT / f"dp_uc47_{n}.csv").to_json(orient="records"))


data = dict(
    pop=json.loads((OUT / "dp_uc47_payload.json").read_text()),
    cand=csv("candidates"), needle=csv("needle"), staff=csv("staff_2026"), efs=csv("efs_2026"),
    scen=csv("efs_scenarios"), hp=csv("hp_reconciliation"), dq=csv("dq_scorecard"),
    sens=csv("sensitivity_matrix"), lb=csv("cohort_leaderboard"), stab=csv("stabilization"),
    trend=csv("trend_adjust"), gap=csv("gap_size"),
    H={k: v for k, v in json.loads((OUT / "dp_uc47_headlines.json").read_text()).items()
       if k in ("pop_n", "tiers", "bowlan26", "efs", "dq", "universe", "name_t2_agreement")},
    figs={k: json.loads((OUT / f"dp_uc47_{k}.json").read_text()) for k in
          ("fig2_wheeler_velo", "fig3_painter_halves", "fig7_stabilization")},
    templates={"light": json.loads(json.dumps(pio.templates["plotly_white"].to_plotly_json(), default=str)),
               "dark": json.loads(json.dumps(pio.templates["plotly_dark"].to_plotly_json(), default=str))},
)
plotly_js = (Path(plotly.__file__).parent / "package_data" / "plotly.min.js").read_text(encoding="utf-8")

CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1b1b1b;--muted:#5b6170;--line:#e3e6ec;--navy:#002D72;--red:#E81828;--chip:#eef1f6}
:root[data-theme=dark]{--bg:#111;--card:#1b1d22;--ink:#eceff4;--muted:#a8afbd;--line:#30343c;--navy:#8fb0ff;--red:#ff5a66;--chip:#262a31}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 Arial,Helvetica,sans-serif}
header{padding:18px 20px 8px;border-bottom:3px solid var(--red);background:var(--card)}
h1{margin:0;color:var(--navy);font-size:22px}header p{margin:4px 0 0;color:var(--muted)}
.wrap{max-width:1320px;margin:0 auto;padding:12px 16px 40px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin:12px 0}
.tile{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
.tile b{display:block;font-size:24px;color:var(--navy)}.tile span{color:var(--muted);font-size:12px}
nav{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}nav button{border:1px solid var(--line);background:var(--card);color:var(--ink);padding:7px 12px;border-radius:18px;cursor:pointer}
nav button.on{background:var(--navy);color:#fff;border-color:var(--navy)}
section{display:none;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px}section.on{display:block}
.ctl{display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin:0 0 10px;color:var(--muted);font-size:13px}
.ctl select,.ctl input[type=text]{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:4px 6px}
table{border-collapse:collapse;width:100%;font-size:12.5px}th{background:var(--navy);color:#fff;text-align:left;padding:6px;position:sticky;top:0}
:root[data-theme=dark] th{color:#111}td{border-bottom:1px solid var(--line);padding:5px 6px}.tw{max-height:460px;overflow:auto}
.tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;background:var(--chip)}.ELITE{background:#E81828;color:#fff}
.note{color:var(--muted);font-size:12.5px;margin:8px 0}.chart{width:100%;height:560px}
.pill{float:right}.pill button{border:1px solid var(--line);background:var(--card);color:var(--ink);padding:5px 10px;border-radius:14px;cursor:pointer}
@media(max-width:700px){.chart{height:430px}h1{font-size:18px}}
"""

HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Archetype Explorer — Elite RHP Four-Seam</title><style>__CSS__</style><script>__PLOTLY__</script></head>
<body><header><div class="pill"><button id="theme">Notebook dark</button></div>
<h1>Eleven Percent, All of It Bowlan</h1>
<p>Archetype Explorer · Elite RHP four-seam · uc-pps-032 · dp_uc47 v1.0.0 · data through 2026-09-20 · bounded frame (not MLB-wide) · aspirational (no availability data)</p></header>
<div class="wrap">
<div class="tiles" id="tiles"></div>
<nav id="nav"></nav>
<section id="s-map"><div class="ctl">
<label>Seasons <select id="y0"></select> – <select id="y1"></select></label>
<label>Tier <select id="tier"><option value="">all</option><option>ELITE</option><option>RESULTS-ONLY</option><option>SHAPE-ONLY</option><option>NOT ELITE</option></select></label>
<label>Coverage <select id="cov"><option value="">all</option><option>COMPLETE</option><option>PARTIAL</option></select></label>
<label>Find <input type="text" id="find" placeholder="pitcher name"></label></div>
<div id="map" class="chart"></div><p class="note">Every graded pitcher-season (≥50 four-seams). Population members (≥100) are solid; THIN seasons are hollow. Grades are 20–80 against 405 RHP pitcher-seasons, 2018–2026, drift-adjusted to 2026 terms. Points are jittered ±1.6 so ties are visible; hover shows the true grade.</p></section>
<section id="s-room"><div class="ctl"><label>Weight on shape <input type="range" id="w1" min="0" max="1" step="0.05" value="0.5"> <b id="w1v">0.50</b></label>
<label>Season <select id="rs"><option value="best">each arm's best</option><option value="2026">2026 only</option></select></label></div>
<div id="room" class="chart" style="height:380px"></div><div class="tw"><table id="roomt"></table></div>
<p class="note">0 = only what the pitch does · 1 = only what it looks like. The organization's composite uses 0.50. Bowlan is #1 at 0.25, 0.50 and 0.75.</p>
<div id="wv" class="chart" style="height:460px"></div><div id="ph" class="chart" style="height:460px"></div></section>
<section id="s-board"><div class="ctl"><label>Weight on shape <input type="range" id="w2" min="0" max="1" step="0.05" value="0.5"> <b id="w2v">0.50</b></label>
<label>Board <select id="bd"><option value="RANKED">ranked (≥100 FF)</option><option value="WATCH (THIN)">watch list (50–99 FF)</option><option value="">both</option></select></label>
<label>Role <select id="rl"><option value="">all</option><option>SP</option><option>RP</option></select></label></div>
<div id="board" class="chart" style="height:620px"></div><div class="tw"><table id="boardt"></table></div>
<p class="note">Not on the 2026 Phillies · most recent 2025–26 season. Dashed lines = Bowlan 2026 (65.0) and Duran 2026 (60.4) at the same weight. Coverage PARTIAL = we only see him against the Phillies or against hitters in the frame.</p></section>
<section id="s-needle"><div id="scen" class="chart" style="height:430px"></div>
<div class="tw"><table id="needlet"></table></div><h3>2026 staff four-seams</h3><div class="tw"><table id="stafft"></table></div>
<p class="note">Swap = a candidate takes a typical Phillies workload for his role (SP 669 / RP 241 four-seams) from the staff's lowest-scoring four-seam in that role. An accounting device, not a roster move. Bowlan-out is a client carry-in (9/17), not data.</p></section>
<section id="s-hp"><div class="tw"><table id="hpt"></table></div><p class="note">Your notebook claims, reproduced with your method and re-run governed.</p></section>
<section id="s-rec"><h3>Does the answer survive the method?</h3><div class="tw"><table id="senst"></table></div>
<h3>Data quality</h3><div class="tw"><table id="dqt"></table></div><div id="stabf" class="chart" style="height:420px"></div></section>
</div>
<script>
const D=__DATA__;
const ARM={"Jonathan Bowlan":"#E81828","Zack Wheeler":"#2F5DA8","Jhoan Duran":"#C97A00","Alex McFarlane":"#00919E","Andrew Painter":"#8250C4","Seranthony Domínguez":"#5E8C31"};
const TIER={"ELITE":"#E81828","SHAPE-ONLY":"#00919E","RESULTS-ONLY":"#C97A00","NOT ELITE":"#B8BCC4"};
let theme='light';
const $=id=>document.getElementById(id);
const fmt=(v,d=1)=>v==null||Number.isNaN(v)?'—':(+v).toFixed(d);
function lay(extra){return Object.assign({template:D.templates[theme],margin:{l:60,r:20,t:40,b:50},font:{family:'Arial',size:13},legend:{orientation:'h',y:-0.15}},extra||{});}
function jit(k,a){let h=0;for(const c of k)h=(h*31+c.charCodeAt(0))|0;return(((Math.abs(h)%1000)/1000)-0.5)*2*a;}
function table(el,rows,cols){const t=$(el);t.innerHTML='<tr>'+cols.map(c=>`<th>${c[0]}</th>`).join('')+'</tr>'+rows.map(r=>'<tr>'+cols.map(c=>`<td>${c[1](r)}</td>`).join('')+'</tr>').join('');}
const tag=t=>`<span class="tag ${t==='ELITE'?'ELITE':''}">${t}</span>`;
// tiles
const H=D.H;
$('tiles').innerHTML=[[fmt(H.efs.ff_elite_archetype_flag.share*100)+'%','2026 elite-four-seam share — all of it Bowlan'],
['#'+H.bowlan26.pop_rank+' of '+H.pop_n,'Bowlan 2026 in the bounded frame, 2018–26'],
[H.tiers.ELITE+' of '+H.pop_n,'pitcher-seasons plus on both axes'],
[fmt(D.gap[0].gap_points),'best ranked external minus Bowlan (score pts)'],
[H.dq.passed+' / '+H.dq.warn+' / '+H.dq.fail,'DQ pass / warn / fail']].map(t=>`<div class="tile"><b>${t[0]}</b><span>${t[1]}</span></div>`).join('');
// nav
const tabs=[['map','Archetype map'],['room','The room'],['board','Out there'],['needle','The needle'],['hp','Your notebook, graded'],['rec','Receipts']];
$('nav').innerHTML=tabs.map((t,i)=>`<button data-t="${t[0]}" class="${i?'':'on'}">${t[1]}</button>`).join('');
$('s-map').classList.add('on');
$('nav').onclick=e=>{const b=e.target.closest('button');if(!b)return;document.querySelectorAll('nav button').forEach(x=>x.classList.toggle('on',x===b));
document.querySelectorAll('section').forEach(s=>s.classList.toggle('on',s.id==='s-'+b.dataset.t));drawAll();resizeVisible();};
function resizeVisible(){document.querySelectorAll('section.on .chart').forEach(el=>{if(el.data)Plotly.Plots.resize(el);});}
window.addEventListener('resize',resizeVisible);
// map
const years=[...new Set(D.pop.map(r=>r.game_year))].sort();
for(const s of ['y0','y1'])$(s).innerHTML=years.map(y=>`<option>${y}</option>`).join('');$('y1').value=years[years.length-1];
function drawMap(){const y0=+$('y0').value,y1=+$('y1').value,t=$('tier').value,c=$('cov').value,f=$('find').value.toLowerCase();
const P=D.pop.filter(r=>r.game_year>=y0&&r.game_year<=y1&&(!t||r.archetype_tier===t)&&(!c||r.coverage===c));
const tr=[];
for(const tier of ['NOT ELITE','RESULTS-ONLY','SHAPE-ONLY','ELITE']){const d=P.filter(r=>r.archetype_tier===tier&&!r.arm);
tr.push({type:'scatter',mode:'markers',name:`${tier} (${d.length})`,x:d.map(r=>r.shape_grade+jit(r.pitcher+'x'+r.game_year,1.6)),y:d.map(r=>r.results_grade+jit(r.pitcher+'y'+r.game_year,1.6)),
marker:{size:d.map(r=>f&&r.name.toLowerCase().includes(f)?16:8),color:TIER[tier],opacity:tier==='NOT ELITE'?0.5:0.85,symbol:d.map(r=>r.pop_member?'circle':'circle-open'),line:{width:d.map(r=>f&&r.name.toLowerCase().includes(f)?3:0.5),color:'#111'}},
text:d.map(r=>`${r.name} ${r.game_year}<br>${r.n} FF · ${r.coverage} · ${r.role}<br>shape ${r.shape_grade} / results ${r.results_grade} · score ${fmt(r.efc_score)}<br>velo ${fmt(r.velo)} · ride ${fmt(r.ivb_in)} in · spin ${fmt(r.spin,0)} · whiff ${fmt(r.whiff_rate,3)}`),hovertemplate:'%{text}<extra></extra>'});}
for(const arm of Object.keys(ARM)){const d=P.filter(r=>r.arm===arm).sort((a,b)=>a.game_year-b.game_year);if(!d.length)continue;
tr.push({type:'scatter',mode:'lines+markers',name:arm,x:d.map(r=>r.shape_grade+jit(r.pitcher+'x'+r.game_year,1.6)),y:d.map(r=>r.results_grade+jit(r.pitcher+'y'+r.game_year,1.6)),
line:{color:ARM[arm],dash:'dot',width:1.5},marker:{size:12,color:ARM[arm],symbol:d.map(r=>r.pop_member?'diamond':'diamond-open'),line:{width:1,color:'#fff'}},
text:d.map(r=>`${arm} ${r.game_year}<br>${r.n} FF${r.thin?' (THIN)':''}<br>shape ${r.shape_grade} / results ${r.results_grade} · ${r.archetype_tier}`),hovertemplate:'%{text}<extra></extra>'});}
Plotly.react('map',tr,lay({xaxis:{title:'Shape grade (velo · ride · spin)',range:[17.5,82.5],dtick:10},yaxis:{title:'Results grade (whiff · run value)',range:[17.5,82.5],dtick:10},
shapes:[{type:'rect',x0:57.5,x1:82.5,y0:57.5,y1:82.5,fillcolor:'#E81828',opacity:0.08,line:{width:0},layer:'below'}],
annotations:[{x:81,y:81,text:'ELITE — plus on both',showarrow:false,xanchor:'right',font:{color:'#E81828'}}]}),{responsive:true});}
['y0','y1','tier','cov'].forEach(i=>$(i).onchange=drawMap);$('find').oninput=drawMap;
// room
function score(r,w){return w*r.shape_score+(1-w)*r.results_score;}
function drawRoom(){const w=+$('w1').value;$('w1v').textContent=w.toFixed(2);
let rows;if($('rs').value==='2026'){rows=D.pop.filter(r=>r.arm&&r.game_year===2026);}else{const best={};for(const r of D.pop.filter(r=>r.arm)){if(!best[r.arm]||r.efc_score>best[r.arm].efc_score)best[r.arm]=r;}rows=Object.values(best);}
rows=rows.map(r=>Object.assign({},r,{s:score(r,w)})).sort((a,b)=>b.s-a.s);
Plotly.react('room',[{type:'bar',orientation:'h',y:rows.map(r=>`${r.arm} ${r.game_year}${r.thin?' (THIN)':''}`).reverse(),x:rows.map(r=>r.s).reverse(),marker:{color:rows.map(r=>ARM[r.arm]).reverse()},
text:rows.map(r=>fmt(r.s)).reverse(),textposition:'outside',hovertemplate:'%{y}: %{x:.1f}<extra></extra>'}],lay({xaxis:{title:'Composite at this weight',range:[30,75]},margin:{l:210,r:30,t:20,b:50},showlegend:false}),{responsive:true});
table('roomt',rows,[['#',r=>rows.indexOf(r)+1],['Arm',r=>r.arm],['Season',r=>r.game_year],['FF',r=>r.n+(r.thin?' THIN':'')],['Velo',r=>fmt(r.velo)],['Ride (in)',r=>fmt(r.ivb_in)],['Spin',r=>fmt(r.spin,0)],['Whiff',r=>fmt(r.whiff_rate,3)],['RV/100',r=>fmt(r.rv100,2)],
['Shape',r=>r.shape_grade],['Results',r=>r.results_grade],['Score',r=>fmt(r.s)],['Tier',r=>tag(r.archetype_tier)]]);}
$('w1').oninput=drawRoom;$('rs').onchange=drawRoom;
// board
function drawBoard(){const w=+$('w2').value;$('w2v').textContent=w.toFixed(2);const b=$('bd').value,rl=$('rl').value;
let rows=D.cand.filter(r=>(!b||r.board===b)&&(!rl||r.role===rl)).map(r=>{const p=D.pop.find(x=>x.pitcher===r.pitcher&&x.game_year===r.game_year);return Object.assign({},r,{s:score(p,w)});}).sort((a,b)=>b.s-a.s);
const top=rows.slice(0,25).reverse();
const bw=score(D.pop.find(x=>x.pitcher===680742&&x.game_year===2026),w),du=score(D.pop.find(x=>x.pitcher===661395&&x.game_year===2026),w);
Plotly.react('board',[{type:'scatter',mode:'markers',y:top.map(r=>`${r.name} '${String(r.game_year).slice(2)} · ${r.n} FF`),x:top.map(r=>r.s),
marker:{size:13,color:top.map(r=>r.archetype_tier==='ELITE'?'#E81828':'#2F5DA8'),symbol:top.map(r=>r.board==='RANKED'?'circle':'circle-open'),line:{width:2,color:top.map(r=>r.archetype_tier==='ELITE'?'#E81828':'#2F5DA8')}},
text:top.map(r=>`${r.name} ${r.game_year} · ${r.board}<br>${r.games} G · ${r.n} FF · ${r.coverage} · ${r.role}<br>shape ${r.shape_grade} / results ${r.results_grade} · ${r.archetype_tier}`),hovertemplate:'%{text}<br>score %{x:.1f}<extra></extra>'}],
lay({showlegend:false,margin:{l:250,r:30,t:30,b:50},xaxis:{title:'Composite at this weight'},shapes:[{type:'line',x0:bw,x1:bw,yref:'paper',y0:0,y1:1,line:{color:'#E81828',dash:'dash'}},{type:'line',x0:du,x1:du,yref:'paper',y0:0,y1:1,line:{color:'#C97A00',dash:'dot'}}],
annotations:[{x:bw,y:1.02,yref:'paper',text:'Bowlan '+fmt(bw),showarrow:false,font:{color:'#E81828'}},{x:du,y:-0.08,yref:'paper',text:'Duran '+fmt(du),showarrow:false,font:{color:'#C97A00'}}]}),{responsive:true});
table('boardt',rows,[['#',r=>rows.indexOf(r)+1],['Arm',r=>r.name],['Season',r=>r.game_year],['Board',r=>r.board],['Role',r=>r.role],['G',r=>r.games],['FF',r=>r.n],['Coverage',r=>r.coverage],['Velo',r=>fmt(r.velo)],['Ride',r=>fmt(r.ivb_in)],['Spin',r=>fmt(r.spin,0)],['Whiff (raw→stab.)',r=>fmt(r.whiff_rate,3)+' → '+fmt(r.whiff_rate_final,3)],['Shape',r=>r.shape_grade],['Results',r=>r.results_grade],['Score',r=>fmt(r.s)],['Tier',r=>tag(r.archetype_tier)]]);}
$('w2').oninput=drawBoard;$('bd').onchange=drawBoard;$('rl').onchange=drawBoard;
// needle
function drawNeedle(){Plotly.react('scen',[{type:'bar',x:D.scen.map(r=>r.scenario),y:D.scen.map(r=>r.share*100),marker:{color:D.scen.map(r=>r.color)},text:D.scen.map(r=>fmt(r.share*100)+'%'),textposition:'outside',customdata:D.scen.map(r=>r.note),hovertemplate:'%{x}<br>%{y:.1f}%<br>%{customdata}<extra></extra>'}],
lay({showlegend:false,yaxis:{title:'Elite-four-seam share (%)',range:[0,32]},title:{text:'Phillies elite four-seam share — one arm deep, 2026'}}),{responsive:true});
const n=D.needle.filter(r=>r.board==='RANKED').sort((a,b)=>a.needle_rank-b.needle_rank).slice(0,15).concat(D.needle.filter(r=>r.board!=='RANKED').slice(0,5));
table('needlet',n,[['Arm',r=>r.name+(r.board!=='RANKED'?' <i>(watch)</i>':'')],['Role',r=>r.role_used],['Four-seams swapped',r=>r.V_role],['Replaces (ledger)',r=>r.displaced_name],['Δ staff FF score',r=>'+'+fmt(r.delta_staff_score,2)],['Δ EFS (pts)',r=>'+'+fmt(r.delta_efs*100)],['Tier',r=>tag(r.archetype_tier)]]);
table('stafft',D.staff,[['Arm',r=>r.name],['Role',r=>r.role],['PHI FF',r=>r.n_phi],['Velo',r=>fmt(r.velo)],['Ride',r=>fmt(r.ivb_in)],['Spin',r=>fmt(r.spin,0)],['Whiff',r=>fmt(r.whiff_rate,3)],['Shape',r=>r.shape_grade??'—'],['Results',r=>r.results_grade??'—'],['Score',r=>fmt(r.efc_score)],['Tier',r=>tag(r.archetype_tier)]]);}
// hp + receipts
function drawStatic(){table('hpt',D.hp,[['#',r=>r.id],['Your claim',r=>r.claim],['Your number',r=>r.client_value],['Governed',r=>r.governed_value],['Verdict',r=>`<b>${r.verdict}</b>`]]);
table('senst',D.sens,[['Variant',r=>r.variant],['Population',r=>r.pop_n],['Cohort order',r=>r.cohort_order],['Board #1',r=>r.candidate_1],['Board top 5',r=>r.candidate_top5]]);
table('dqt',D.dq,[['Rule',r=>r.rule],['Dimension',r=>r.dimension],['Description',r=>r.description],['Result',r=>`<b>${r.result}</b>`],['Observed',r=>String(r.observed).slice(0,120)]]);}
function fig(el,k,h){const f=D.figs[k];const L=Object.assign({},f.layout,{template:D.templates[theme],width:null,height:h,autosize:true});Plotly.react(el,f.data,L,{responsive:true});}
function drawAll(){drawMap();drawRoom();drawBoard();drawNeedle();fig('wv','fig2_wheeler_velo',460);fig('ph','fig3_painter_halves',460);fig('stabf','fig7_stabilization',420);}
$('theme').onclick=()=>{theme=theme==='light'?'dark':'light';document.documentElement.dataset.theme=theme;$('theme').textContent=theme==='light'?'Notebook dark':'Brand light';drawAll();resizeVisible();};
drawStatic();drawAll();
</script></body></html>"""

html = (HTML.replace("__CSS__", CSS).replace("__PLOTLY__", plotly_js)
        .replace("__DATA__", json.dumps(data, default=str).replace("</", "<\\/")))
DEST.write_text(html, encoding="utf-8")
print(f"dashboard -> {DEST.name} ({DEST.stat().st_size / 1e6:.2f} MB)")
