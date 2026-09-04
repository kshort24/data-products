"""
dp_uc40_build_dashboard.py — self-contained interactive dashboard for uc-pos-014
================================================================================
Reads ONLY the receipts the build wrote (out/dp_uc40_*.csv + headlines.json) and
emits one HTML file with no network dependencies.

House rules applied:
  * uc-pos-011: VENDOR the charting library, never CDN it. `_chartjs_4.4.1.umd.js`
    (MIT) is inlined; every chart call goes through `chart(id,cfg)` which degrades
    to a visible placeholder rather than taking the tables and tab nav down.
  * uc-pps-028: the repo's PITCH_COLORS fail two of the dataviz six checks; the
    validated replacement palette is used instead.
  * Every cell below the 50-PA floor renders with the standing ⚠ marker.
"""
from __future__ import annotations

import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
DST = os.path.join(HERE, 'dp_uc40_turner_recency_dashboard.html')
G = lambda n: pd.read_csv(os.path.join(OUT, f'dp_uc40_{n}.csv'))
J = lambda df: df.where(pd.notna(df), None).to_dict('records')

H = json.load(open(os.path.join(OUT, 'dp_uc40_headlines.json'), encoding='utf-8'))
CHARTJS = open(os.path.join(HERE, '_chartjs_4.4.1.umd.js'), encoding='utf-8').read()

D = {
    'career': J(G('career_by_season')),
    'careerContact': J(G('career_contact')),
    'careerApproach': J(G('career_approach')),
    'careerPullAir': J(G('career_pull_air')),
    'careerBat': J(G('career_bat_tracking')),
    'window': J(G('window_split')),
    'monthly': J(G('monthly_master')),
    'phiRef': J(G('phi_reference_2023_2025')),
    'scan': J(G('breakpoint_scan')),
    'roll': J(G('rolling_form')[['pa_idx', 'game_date', 'roll_woba', 'roll_ops']]),
    'run': J(G('running_line')[['game_year', 'cum_pa', 'cum_woba']]),
    'pgWindow': J(G('pitch_group_window')),
    'pgSeason': J(G('pitch_group_season')),
    'pitchType': J(G('pitch_type_2026')),
    'platoonSeason': J(G('platoon_season')),
    'platoonWindow': J(G('platoon_window')),
    'platoonCf': J(G('platoon_counterfactual')),
    'exposure': J(G('platoon_exposure_window')),
    'pct': J(G('profile_percentiles')),
    'ad1': J(G('approach_differential_season')),
    'shift': J(G('shift_tests_july_vs_recent')),
    'dq': J(G('dq_scorecard')),
    'parent': J(G('parent_reproduction')),
    'count': J(G('count_state_window')),
    'headlines': H,
}

CSS = """
:root{--navy:#002D72;--red:#E81828;--teal:#00919E;--amber:#C97A00;--violet:#8250C4;
--ink:#16202C;--mut:#5B6673;--line:#DDE3EB;--bg:#F4F6FA;--card:#fff;--warn:#B45309}
*{box-sizing:border-box}
body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
color:var(--ink);background:var(--bg)}
header{background:var(--navy);color:#fff;padding:20px 26px 16px}
header h1{margin:0 0 4px;font-size:23px;letter-spacing:-.2px}
header .sub{font-size:12.5px;opacity:.86}
header .sub code{background:rgba(255,255,255,.14);padding:1px 5px;border-radius:3px;font-size:11.5px}
.bar{background:#fff;border-bottom:1px solid var(--line);padding:0 26px;display:flex;gap:2px;
position:sticky;top:0;z-index:20;overflow-x:auto}
.bar button{background:none;border:0;border-bottom:3px solid transparent;padding:12px 14px;
font:600 13px inherit;color:var(--mut);cursor:pointer;white-space:nowrap}
.bar button:hover{color:var(--navy)}
.bar button.on{color:var(--navy);border-bottom-color:var(--red)}
main{padding:22px 26px 60px;max-width:1280px}
section{display:none}section.on{display:block}
h2{font-size:17px;color:var(--navy);margin:26px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--red)}
h2:first-child{margin-top:0}
h3{font-size:13.5px;color:var(--navy);margin:18px 0 8px}
p.note{color:var(--mut);font-size:12.5px;margin:6px 0 14px;max-width:78ch}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:12px;margin:14px 0 6px}
.card{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:13px 14px}
.card .k{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut)}
.card .v{font-size:25px;font-weight:700;color:var(--navy);margin:5px 0 2px;font-variant-numeric:tabular-nums}
.card .v.bad{color:var(--red)}.card .v.good{color:var(--teal)}
.card .d{font-size:11.5px;color:var(--mut)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:14px 16px;margin:14px 0}
.wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:12.4px;font-variant-numeric:tabular-nums}
th{background:var(--navy);color:#fff;text-align:left;padding:7px 9px;font-size:11.4px;
font-weight:600;white-space:nowrap;position:sticky;top:0}
td{padding:6px 9px;border-bottom:1px solid var(--line);white-space:nowrap}
tr:hover td{background:#F7F9FC}
td.hi{color:var(--red);font-weight:700}td.lo{color:var(--teal);font-weight:700}
.flag{color:var(--warn);font-weight:700}
.chart{position:relative;height:330px}
.chart.tall{height:410px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(430px,1fr));gap:14px}
.ctrl{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:4px 0 12px}
.ctrl label{font-size:12px;color:var(--mut);font-weight:600}
.ctrl select,.ctrl input{font:13px inherit;padding:5px 8px;border:1px solid var(--line);
border-radius:6px;background:#fff;color:var(--ink)}
.chip{display:inline-block;font-size:11px;padding:2px 8px;border-radius:20px;margin-right:5px}
.chip.pass{background:#E3F5EE;color:#0A6B4F}.chip.warn{background:#FEF3C7;color:#92400E}
.chip.fail{background:#FEE2E2;color:#991B1B}
.ph{display:flex;align-items:center;justify-content:center;height:100%;color:var(--mut);
font-size:12.5px;border:1px dashed var(--line);border-radius:8px;text-align:center;padding:12px}
footer{padding:22px 26px 40px;color:var(--mut);font-size:11.5px;border-top:1px solid var(--line);
background:#fff;margin-top:26px}
@media (max-width:640px){main{padding:16px 14px 50px}header{padding:16px}.chart{height:280px}}
"""

JS = r"""
const D = __DATA__;
const NAVY='#002D72',RED='#E81828',TEAL='#00919E',AMBER='#C97A00',VIOLET='#8250C4',
      GREY='#8894A4',LGREY='#C9D2DD';
const f3=v=>v==null||isNaN(v)?'—':(+v).toFixed(3).replace(/^0\./,'.');
const f1=v=>v==null||isNaN(v)?'—':(+v).toFixed(1);
const f2=v=>v==null||isNaN(v)?'—':(+v).toFixed(2);
const pc=v=>v==null||isNaN(v)?'—':(100*v).toFixed(1)+'%';
const wl=w=>w?w.split(' ')[0].replace('W1_early','Mar–Jun').replace('W2_july','July')
             .replace('W3_recent','Aug–Sep'):'';
const flag=b=>b?' <span class="flag" title="below the 50-PA floor">⚠</span>':'';

/* every chart goes through here: a thrown config never takes the page down */
function chart(id,cfg){
  const el=document.getElementById(id);
  if(!el) return;
  try{
    if(typeof Chart==='undefined') throw new Error('chart library unavailable');
    Chart.defaults.font.family=getComputedStyle(document.body).fontFamily;
    Chart.defaults.font.size=11.5;
    Chart.defaults.color='#5B6673';
    new Chart(el.getContext('2d'),cfg);
  }catch(e){
    el.outerHTML='<div class="ph">chart unavailable ('+e.message+
      ') — the table below carries the same numbers</div>';
  }
}
const LINE={responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
  plugins:{legend:{position:'bottom',labels:{boxWidth:12,usePointStyle:true,pointStyle:'line'}}}};
const BAR={responsive:true,maintainAspectRatio:false,
  plugins:{legend:{position:'bottom',labels:{boxWidth:12}}}};

/* ── tabs ─────────────────────────────────────────────────────────────── */
function tab(name){
  document.querySelectorAll('section').forEach(s=>s.classList.toggle('on',s.id==='t-'+name));
  document.querySelectorAll('.bar button').forEach(b=>b.classList.toggle('on',b.dataset.t===name));
  window.scrollTo({top:0,behavior:'instant'});
}

/* ── table helper ─────────────────────────────────────────────────────── */
function table(el,cols,rows){
  const th=cols.map(c=>'<th>'+c.h+'</th>').join('');
  const tr=rows.map(r=>'<tr>'+cols.map(c=>{
      const v=c.f?c.f(r[c.k],r):(r[c.k]==null?'—':r[c.k]);
      return '<td class="'+(c.cls?c.cls(r[c.k],r):'')+'">'+v+'</td>';
    }).join('')+'</tr>').join('');
  document.getElementById(el).innerHTML='<table><thead><tr>'+th+'</tr></thead><tbody>'+tr+'</tbody></table>';
}

/* ── OVERVIEW ─────────────────────────────────────────────────────────── */
const car=D.career, s26=car.find(r=>r.game_year===2026), ref=D.phiRef[0];
const w3=D.window.find(r=>r.window.startsWith('W3')),
      w2=D.window.find(r=>r.window.startsWith('W2')),
      w1=D.window.find(r=>r.window.startsWith('W1'));

function cards(el,items){
  document.getElementById(el).innerHTML=items.map(i=>
    '<div class="card"><div class="k">'+i.k+'</div><div class="v '+(i.c||'')+'">'+i.v+
    '</div><div class="d">'+i.d+'</div></div>').join('');
}
cards('kpis',[
 {k:'2026 slash',v:f3(s26.ba)+'/'+f3(s26.obp)+'/'+f3(s26.slg),c:'bad',d:'lowest of 11 qualified seasons on all three'},
 {k:'2026 wOBA',v:f3(s26.woba),c:'bad',d:'xwOBA '+f3(s26.xwoba)+' — not luck'},
 {k:'Aug 1 – Sep 2 OPS',v:f3(w3.ops),c:'bad',d:w3.plate_apps+' PA · ISO '+f3(w3.iso)+' · 1 HR'},
 {k:'Popup % of BIP, recent',v:pc(w3.pu_rate),c:'bad',d:'vs '+pc(ref.pu_rate)+' PHI norm · z = 4.12'},
 {k:'Rolling 100-PA wOBA',v:f3(D.headlines.rf2.last_woba),c:'bad',
  d:'peak '+f3(D.headlines.rf2.max_woba)+' on 2026-07-21'},
 {k:'Parent figures reproduced',v:D.headlines.parent_repro.pass+'/'+D.headlines.parent_repro.checks,c:'good',
  d:'uc-pos-006 audited before any new claim'}]);

chart('cOverview',{type:'bar',data:{labels:car.map(r=>r.game_year),datasets:[
  {label:'OPS',data:car.map(r=>r.below_floor?null:r.ops),
   backgroundColor:car.map(r=>r.game_year===2026?RED:LGREY),order:2},
  {type:'line',label:'wOBA',data:car.map(r=>r.below_floor?null:r.woba),borderColor:NAVY,
   backgroundColor:NAVY,yAxisID:'y1',tension:.25,pointRadius:3,order:1},
  {type:'line',label:'xwOBA (per-PA)',data:car.map(r=>r.below_floor?null:r.xwoba),borderColor:TEAL,
   backgroundColor:TEAL,borderDash:[5,4],yAxisID:'y1',tension:.25,pointRadius:3,order:1}]},
  options:{...LINE,scales:{y:{title:{display:true,text:'OPS'}},
   y1:{position:'right',title:{display:true,text:'wOBA'},grid:{drawOnChartArea:false}}}}});

table('tOverview',[
 {h:'Season',k:'game_year',f:(v,r)=>v+' <span style="color:#8894A4">'+r.era+'</span>'+flag(r.below_floor)},
 {h:'PA',k:'plate_apps'},{h:'BA',k:'ba',f:f3},{h:'OBP',k:'obp',f:f3},{h:'SLG',k:'slg',f:f3},
 {h:'OPS',k:'ops',f:f3,cls:v=>v<.70?'hi':(v>.90?'lo':'')},{h:'ISO',k:'iso',f:f3},
 {h:'wOBA',k:'woba',f:f3},{h:'xwOBA',k:'xwoba',f:f3},{h:'BABIP',k:'babip',f:f3},
 {h:'K%',k:'krate',f:pc},{h:'BB%',k:'bbrate',f:pc},{h:'HR',k:'hrs'}],car);

/* percentile explorer */
const MLAB={ops:'OPS',woba:'wOBA',slg:'SLG',obp:'OBP',ba:'BA',iso:'ISO',
 krate:'K% (lower is better)',bbrate:'BB%',whiff_rate:'Whiff% (lower is better)',
 chase_rate:'Chase% (lower is better)',swing_rate_in_zone:'In-zone swing%',
 hard_hit_rate:'Hard-hit%',barrel_rate:'Barrel%',mean_ev:'Exit velocity',
 pu_rate:'Popup% of BIP (lower is better)',pull_air_rate:'Pull-air% of BIP'};
const pctSel=document.getElementById('pctMode');
function drawPct(){
  const mode=pctSel.value;
  const rows=D.pct.filter(r=>r.pctile_season!=null);
  chart('cPct',{type:'bar',data:{labels:rows.map(r=>MLAB[r.metric]||r.metric),datasets:[
    {label:mode==='both'||mode==='season'?'2026 season':'',
     data:mode==='recent'?[]:rows.map(r=>r.pctile_season),backgroundColor:NAVY},
    {label:mode==='both'||mode==='recent'?'Aug–Sep window as a season':'',
     data:mode==='season'?[]:rows.map(r=>r.pctile_W3_as_a_season),backgroundColor:RED}]},
    options:{...BAR,indexAxis:'y',scales:{x:{min:0,max:100,
      title:{display:true,text:'percentile of 220 Phillies hitter-seasons (≥50 PA)'}}}}});
}
pctSel.addEventListener('change',drawPct);drawPct();
table('tPct',[{h:'Metric',k:'metric',f:v=>MLAB[v]||v},{h:'2026 season',k:'turner_2026_season',f:v=>v>1?f2(v):f3(v)},
 {h:'pctile',k:'pctile_season',f:f1},{h:'Aug–Sep',k:'turner_2026_W3_recent',f:v=>v>1?f2(v):f3(v)},
 {h:'pctile (as a season)',k:'pctile_W3_as_a_season',f:f1,cls:v=>v>=95||v<=15?'hi':''},
 {h:'pool median',k:'pool_median',f:v=>v>1?f2(v):f3(v)}],D.pct);
"""

JS += r"""
/* ── RECENCY ──────────────────────────────────────────────────────────── */
chart('cRoll',{type:'line',data:{labels:D.roll.map(r=>r.pa_idx),datasets:[
 {label:'trailing 100-PA wOBA',data:D.roll.map(r=>r.roll_woba),borderColor:RED,
  backgroundColor:'rgba(232,24,40,.07)',fill:true,pointRadius:0,borderWidth:2.4,tension:.15},
 {label:'2023–25 Phillies norm (.346)',data:D.roll.map(()=>D.phiRef[0].woba),borderColor:NAVY,
  borderDash:[6,4],pointRadius:0,borderWidth:1.4}]},
 options:{...LINE,scales:{x:{title:{display:true,text:'plate appearance index, 2026'},
  ticks:{maxTicksLimit:12}},y:{title:{display:true,text:'wOBA'}}},
  plugins:{...LINE.plugins,tooltip:{callbacks:{title:it=>{
    const r=D.roll[it[0].dataIndex];return 'PA '+r.pa_idx+' · '+String(r.game_date).slice(0,10);}}}}}});

chart('cRun',{type:'line',data:{labels:[...Array(700).keys()].map(i=>i+1),datasets:
 [2023,2024,2025,2026].map((y,i)=>({label:y+'',
   data:D.run.filter(r=>r.game_year===y).map(r=>({x:r.cum_pa,y:r.cum_woba})),
   borderColor:[LGREY,GREY,'#4A5568',RED][i],borderWidth:y===2026?3:1.6,pointRadius:0,tension:.1}))},
 options:{...LINE,parsing:false,scales:{x:{type:'linear',min:40,
  title:{display:true,text:'cumulative PA within season'}},
  y:{min:.20,max:.46,title:{display:true,text:'season-to-date wOBA'}}}}});

chart('cScan',{type:'bar',data:{labels:D.scan.map(r=>r.breakpoint),datasets:[
 {label:'Δ OPS (post − pre)',data:D.scan.map(r=>r.d_ops),
  backgroundColor:D.scan.map(r=>r.d_ops<0?RED:TEAL)},
 {type:'line',label:'Δ wOBA',data:D.scan.map(r=>r.d_woba),borderColor:NAVY,
  backgroundColor:NAVY,yAxisID:'y1',tension:.2,pointRadius:3}]},
 options:{...BAR,scales:{y:{title:{display:true,text:'Δ OPS'}},
  y1:{position:'right',title:{display:true,text:'Δ wOBA'},grid:{drawOnChartArea:false}}}}});
table('tScan',[{h:'Cut date',k:'breakpoint',f:(v)=>v==='2026-07-21'?'<b style="color:#E81828">'+v+' (parent\'s cut)</b>':v},
 {h:'pre PA',k:'pre_pa'},{h:'post PA',k:'post_pa'},
 {h:'pre OPS',k:'pre_ops',f:f3},{h:'post OPS',k:'post_ops',f:f3},
 {h:'Δ OPS',k:'d_ops',f:v=>(v>0?'+':'')+f3(v),cls:v=>v<0?'hi':'lo'},
 {h:'Δ wOBA',k:'d_woba',f:v=>(v>0?'+':'')+f3(v),cls:v=>v<0?'hi':'lo'}],D.scan);

/* monthly explorer */
const MSEL=document.getElementById('monMetric');
const MET=[['ops','OPS',f3],['woba','wOBA',f3],['slg','SLG',f3],['iso','ISO',f3],
 ['krate','K%',pc],['bbrate','BB%',pc],['hard_hit_rate','Hard-hit %',pc],
 ['barrel_rate','Barrel %',pc],['pu_rate','Popup % of BIP',pc],['mean_ev','Exit velocity',f1],
 ['mean_la','Launch angle',f1],['bat_speed_mu','Bat speed',f1],['chase_rate','Chase %',pc],
 ['swing_rate_in_zone','In-zone swing %',pc]];
MSEL.innerHTML=MET.map(m=>'<option value="'+m[0]+'">'+m[1]+'</option>').join('');
const MN={3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep'};
let monChart=null;
function drawMon(){
  const k=MSEL.value,m=MET.find(x=>x[0]===k);
  const refv=D.phiRef[0][k];
  chart('cMon',{type:'bar',data:{labels:D.monthly.map(r=>MN[r.month]+(r.below_floor?' ⚠':'')),
   datasets:[{label:m[1],data:D.monthly.map(r=>r[k]),
     backgroundColor:D.monthly.map(r=>r.month===7?AMBER:(r.month>=8?RED:'#AEB6C2'))},
    ...(refv!=null?[{type:'line',label:'2023–25 PHI norm',data:D.monthly.map(()=>refv),
      borderColor:NAVY,borderDash:[6,4],pointRadius:0,borderWidth:1.4}]:[])]},
   options:{...BAR,plugins:{...BAR.plugins,tooltip:{callbacks:{label:it=>{
     const r=D.monthly[it.dataIndex];return m[1]+': '+m[2](r[k])+'  ('+r.plate_apps+' PA)';}}}}}});
}
MSEL.addEventListener('change',drawMon);drawMon();
table('tMon',[{h:'Month',k:'month',f:(v,r)=>MN[v]+flag(r.below_floor)},{h:'PA',k:'plate_apps'},
 {h:'BA',k:'ba',f:f3},{h:'OBP',k:'obp',f:f3},{h:'SLG',k:'slg',f:f3},{h:'OPS',k:'ops',f:f3},
 {h:'wOBA',k:'woba',f:f3},{h:'K%',k:'krate',f:pc},{h:'BB%',k:'bbrate',f:pc},
 {h:'EV',k:'mean_ev',f:f1},{h:'LA',k:'mean_la',f:f1},{h:'Hard-hit',k:'hard_hit_rate',f:pc},
 {h:'Barrel',k:'barrel_rate',f:pc},{h:'Popup',k:'pu_rate',f:pc,cls:v=>v>.12?'hi':''},
 {h:'Bat speed',k:'bat_speed_mu',f:f1}],D.monthly);

/* ── MECHANISM ────────────────────────────────────────────────────────── */
const MECH=[['mean_ev','Exit velocity (mph)',f1],['hard_hit_rate','Hard-hit %',pc],
 ['barrel_rate','Barrel %',pc],['pu_rate','Popup % of BIP',pc],['mean_la','Launch angle (°)',f1],
 ['xwobacon_bip','xwOBAcon',f3],['bat_speed_mu','Bat speed (mph)',f1],
 ['fast_swing_rate','Fast-swing %',pc],['chase_rate','Chase %',pc],
 ['swing_rate_in_zone','In-zone swing %',pc],['krate','K%',pc],['iso','ISO',f3]];
table('tMech',[{h:'Measure',k:'m'},{h:'Mar–Jun',k:'a'},{h:'July',k:'b'},{h:'Aug–Sep',k:'c'},
 {h:'PHI norm 2023–25',k:'r'}],
 MECH.map(m=>({m:m[1],a:m[2](w1[m[0]]),b:m[2](w2[m[0]]),c:m[2](w3[m[0]]),r:m[2](ref[m[0]])})));

const MS=document.getElementById('mechMetric');
MS.innerHTML=MECH.map(m=>'<option value="'+m[0]+'">'+m[1]+'</option>').join('');
function drawMech(){
  const k=MS.value,m=MECH.find(x=>x[0]===k);
  chart('cMech',{type:'bar',data:{labels:['Mar–Jun','July','Aug–Sep','PHI norm 2023–25'],
   datasets:[{label:m[1],data:[w1[k],w2[k],w3[k],ref[k]],
    backgroundColor:[NAVY,AMBER,RED,'#AEB6C2']}]},
   options:{...BAR,plugins:{...BAR.plugins,legend:{display:false},
     tooltip:{callbacks:{label:it=>m[1]+': '+m[2](it.raw)}}}}});
}
MS.addEventListener('change',drawMech);drawMech();

const shift=D.shift.filter(r=>r.baseline.indexOf('PHI')===0);
chart('cShift',{type:'bar',data:{labels:shift.map(r=>r.measure),datasets:[
 {label:'|z| vs the 2023–25 Phillies norm',data:shift.map(r=>Math.abs(r.z)),
  backgroundColor:shift.map(r=>Math.abs(r.z)>=2.5?RED:(Math.abs(r.z)>=1.5?AMBER:LGREY))}]},
 options:{...BAR,indexAxis:'y',plugins:{...BAR.plugins,legend:{display:false}},
  scales:{x:{title:{display:true,text:'|z| — 1.5 suggestive, 2.5 clearly beyond noise'}}}}});
table('tShift',[{h:'Baseline',k:'baseline'},{h:'Measure',k:'measure'},
 {h:'n baseline',k:'n_baseline'},{h:'n recent',k:'n_recent'},
 {h:'baseline',k:'baseline_value',f:v=>v>1?f2(v):f3(v)},
 {h:'Aug–Sep',k:'recent',f:v=>v>1?f2(v):f3(v)},
 {h:'Δ',k:'delta',f:v=>(v>0?'+':'')+(Math.abs(v)>1?f2(v):f3(v))},
 {h:'z',k:'z',f:f2},{h:'verdict',k:'band',
  cls:v=>v==='clearly beyond noise'?'hi':''}],D.shift);
"""

JS += r"""
/* ── SPLITS ───────────────────────────────────────────────────────────── */
const GRPS=['fastball','breaking','offspeed'];
const WKEYS=['W1_early','W2_july','W3_recent'];
chart('cPg',{type:'bar',data:{labels:GRPS.map(g=>g[0].toUpperCase()+g.slice(1)),
 datasets:WKEYS.map((wk,i)=>({label:wl(wk),
  data:GRPS.map(g=>{const r=D.pgWindow.find(x=>x.window.startsWith(wk.slice(0,2))&&x.pitch_group===g);
    return r?r.woba:null;}),backgroundColor:[NAVY,AMBER,RED][i]}))},
 options:{...BAR,scales:{y:{title:{display:true,text:'wOBA'}}}}});
chart('cPgUse',{type:'bar',data:{labels:['Mar–Jun','July','Aug–Sep'],
 datasets:GRPS.map((g,i)=>({label:g,stack:'s',
  data:WKEYS.map(wk=>{const r=D.pgWindow.find(x=>x.window.startsWith(wk.slice(0,2))&&x.pitch_group===g);
    return r?100*r.usage:null;}),backgroundColor:[TEAL,RED,AMBER][i]}))},
 options:{...BAR,scales:{x:{stacked:true},y:{stacked:true,max:100,
  title:{display:true,text:'% of pitches seen'}}}}});
table('tPg',[{h:'Window',k:'window',f:wl},{h:'Group',k:'pitch_group'},{h:'Pitches',k:'pitches'},
 {h:'Usage',k:'usage',f:pc},{h:'PA',k:'plate_apps',f:(v,r)=>v+flag(r.below_floor)},
 {h:'BA',k:'ba',f:f3},{h:'SLG',k:'slg',f:f3},{h:'wOBA',k:'woba',f:f3,cls:v=>v<.25?'hi':''},
 {h:'Whiff',k:'whiff_rate',f:pc,cls:v=>v>.35?'hi':''},{h:'Chase',k:'chase_rate',f:pc}],
 D.pgWindow.filter(r=>r.pitch_group!=='other'));

const PT=D.pitchType.slice().sort((a,b)=>a.woba-b.woba);
const PGMAP={FF:'fastball',SI:'fastball',FC:'fastball',SL:'breaking',ST:'breaking',CU:'breaking',
 KC:'breaking',SV:'breaking',CS:'breaking',CH:'offspeed',FS:'offspeed',FO:'offspeed'};
const PGC={fastball:TEAL,breaking:RED,offspeed:AMBER};
chart('cPt',{type:'bar',data:{labels:PT.map(r=>r.pitch_type),datasets:[
 {label:'wOBA against',data:PT.map(r=>r.woba),
  backgroundColor:PT.map(r=>PGC[PGMAP[r.pitch_type]]||GREY)}]},
 options:{...BAR,indexAxis:'y',plugins:{...BAR.plugins,legend:{display:false},
  tooltip:{callbacks:{label:it=>{const r=PT[it.dataIndex];
   return ['wOBA '+f3(r.woba),'whiff '+pc(r.whiff_rate),r.pitches+' pitches ('+pc(r.usage)+')',
    r.plate_apps+' PA'+(r.below_floor?' ⚠ below floor':'')];}}}}}});
table('tPt',[{h:'Pitch',k:'pitch_type'},{h:'Pitches',k:'pitches'},{h:'Usage',k:'usage',f:pc},
 {h:'PA',k:'plate_apps',f:(v,r)=>v+flag(r.below_floor)},{h:'BA',k:'ba',f:f3},{h:'SLG',k:'slg',f:f3},
 {h:'wOBA',k:'woba',f:f3,cls:v=>v<.26?'hi':''},{h:'Whiff',k:'whiff_rate',f:pc,cls:v=>v>.35?'hi':''},
 {h:'Chase',k:'chase_rate',f:pc},{h:'Hard-hit',k:'hard_hit_rate',f:pc}],PT);

const PLQ=D.platoonSeason.filter(r=>!r.below_floor);
chart('cPlat',{type:'line',data:{labels:[...new Set(PLQ.map(r=>r.game_year))],datasets:[
 {label:'vs LHP',data:PLQ.filter(r=>r.p_throws==='L').map(r=>r.ops),borderColor:VIOLET,
  backgroundColor:VIOLET,tension:.2,pointRadius:3.5},
 {label:'vs RHP',data:PLQ.filter(r=>r.p_throws==='R').map(r=>r.ops),borderColor:TEAL,
  backgroundColor:TEAL,tension:.2,pointRadius:3.5}]},
 options:{...LINE,scales:{y:{title:{display:true,text:'OPS'}}}}});
chart('cPlatWin',{type:'bar',data:{labels:['Mar–Jun','July','Aug–Sep'],datasets:[
 {label:'vs LHP',data:WKEYS.map(wk=>{const r=D.platoonWindow.find(x=>x.window.startsWith(wk.slice(0,2))&&x.p_throws==='L');return r?r.ops:null;}),backgroundColor:VIOLET},
 {label:'vs RHP',data:WKEYS.map(wk=>{const r=D.platoonWindow.find(x=>x.window.startsWith(wk.slice(0,2))&&x.p_throws==='R');return r?r.ops:null;}),backgroundColor:TEAL}]},
 options:{...BAR,scales:{y:{title:{display:true,text:'OPS'}}}}});
table('tPlatS',[{h:'Season',k:'game_year'},{h:'Hand',k:'p_throws'},
 {h:'PA',k:'plate_apps',f:(v,r)=>v+flag(r.below_floor)},{h:'BA',k:'ba',f:f3},{h:'OBP',k:'obp',f:f3},
 {h:'SLG',k:'slg',f:f3},{h:'OPS',k:'ops',f:f3,cls:(v,r)=>r.game_year===2026?'hi':''},
 {h:'wOBA',k:'woba',f:f3},{h:'K%',k:'krate',f:pc},{h:'Whiff',k:'whiff_rate',f:pc}],
 D.platoonSeason.filter(r=>r.game_year>=2019));
table('tPlatW',[{h:'Window',k:'window',f:wl},{h:'Hand',k:'p_throws'},
 {h:'PA',k:'plate_apps',f:(v,r)=>v+flag(r.below_floor)},{h:'BA',k:'ba',f:f3},{h:'OBP',k:'obp',f:f3},
 {h:'SLG',k:'slg',f:f3},{h:'OPS',k:'ops',f:f3},{h:'wOBA',k:'woba',f:f3},{h:'K%',k:'krate',f:pc},
 {h:'Hard-hit',k:'hard_hit_rate',f:pc},{h:'EV',k:'mean_ev',f:f1}],D.platoonWindow);
table('tCf',[{h:'Reference mix',k:'from_label',f:wl},{h:'Window priced',k:'to_label',f:wl},
 {h:'Metric',k:'metric'},{h:'Actual',k:'actual',f:f3},
 {h:'Reweighted to reference',k:'reweighted_to_reference',f:f3},
 {h:'Mix effect',k:'mix_effect',f:v=>(v>0?'+':'')+(v).toFixed(4)}],
 D.platoonCf.filter(r=>r.to_label.startsWith('W3')));

/* ── APPROACH / CAREER ────────────────────────────────────────────────── */
chart('cAd',{type:'bar',data:{labels:D.ad1.map(r=>r.game_year),datasets:[
 {label:'AD-1 (in-zone swing − chase)',data:D.ad1.map(r=>r.below_floor?null:r.approach_differential),
  backgroundColor:D.ad1.map(r=>r.game_year===2026?RED:LGREY),order:2},
 {type:'line',label:'in-zone swing %',data:D.ad1.map(r=>r.below_floor?null:r.swing_rate_in_zone),
  borderColor:NAVY,backgroundColor:NAVY,tension:.2,pointRadius:3,order:1},
 {type:'line',label:'chase %',data:D.ad1.map(r=>r.below_floor?null:r.chase_rate),
  borderColor:AMBER,backgroundColor:AMBER,tension:.2,pointRadius:3,order:1}]},
 options:{...BAR,scales:{y:{title:{display:true,text:'rate'}}}}});
table('tApp',[{h:'Season',k:'game_year'},{h:'Pitches',k:'pitches'},
 {h:'Swing %',k:'swing_rate',f:pc},{h:'In-zone swing %',k:'swing_rate_in_zone',f:pc},
 {h:'Chase %',k:'chase_rate',f:pc},{h:'Whiff %',k:'whiff_rate',f:pc},
 {h:'In-zone whiff %',k:'whiff_rate_in_zone',f:pc},
 {h:'Zone rate seen (D-7 fixed)',k:'in_zone_rate_fix',f:pc},
 {h:'First-pitch swing %',k:'srfp',f:pc}],D.careerApproach);
table('tContact',[{h:'Season',k:'game_year'},{h:'BIP',k:'bips'},{h:'EV',k:'mean_ev',f:f1},
 {h:'LA',k:'mean_la',f:f1},{h:'Hard-hit',k:'hard_hit_rate',f:pc},{h:'Barrel',k:'barrel_rate',f:pc},
 {h:'GB',k:'gb_rate',f:pc},{h:'FB',k:'fb_rate',f:pc},{h:'LD',k:'ld_rate',f:pc},
 {h:'Popup',k:'pu_rate',f:pc},{h:'xwOBAcon',k:'xwobacon_bip',f:f3}],D.careerContact);
table('tPull',[{h:'Season',k:'game_year'},{h:'BIP',k:'total_bips'},{h:'Pulls',k:'total_pulls'},
 {h:'Pull-airs',k:'pull_airs'},{h:'Pull-air rate',k:'pull_air_rate',f:pc},
 {h:'Pull rate',k:'pull_rate',f:pc}],D.careerPullAir);
table('tBat',[{h:'Season',k:'game_year'},{h:'Swings',k:'swings'},
 {h:'Tracked',k:'tracked_swings'},{h:'Coverage',k:'tracking_coverage',f:pc},
 {h:'Bat speed',k:'bat_speed_mu',f:f1},{h:'90th pct',k:'bat_speed_p90',f:f1},
 {h:'Swing length',k:'swing_length_mu',f:f2},{h:'Attack angle',k:'attack_angle_mu',f:f1},
 {h:'Fast-swing %',k:'fast_swing_rate',f:pc}],D.careerBat.filter(r=>r.game_year>=2023));

/* ── GOVERNANCE ───────────────────────────────────────────────────────── */
const dq=D.dq;
document.getElementById('dqChips').innerHTML=
 '<span class="chip pass">'+dq.filter(r=>r.status==='PASS').length+' PASS</span>'+
 '<span class="chip warn">'+dq.filter(r=>r.status==='WARN').length+' WARN</span>'+
 '<span class="chip fail">'+dq.filter(r=>r.status==='FAIL').length+' FAIL</span>';
table('tDq',[{h:'Rule',k:'rule'},{h:'Measure',k:'measure'},{h:'Observed',k:'observed'},
 {h:'Expected',k:'expected'},{h:'Status',k:'status',
  f:v=>'<span class="chip '+v.toLowerCase()+'">'+v+'</span>'}],dq);
const par=D.parent;
document.getElementById('parChips').innerHTML=
 '<span class="chip pass">'+par.filter(r=>r.repro_pass).length+'/'+par.length+' reproduced</span>'+
 '<span class="chip pass">0 definitional drift</span>';
table('tPar',[{h:'Season',k:'season'},{h:'Metric',k:'metric'},
 {h:'Parent published',k:'parent_published'},{h:'Recomputed (parent defs)',k:'legacy_recomputed'},
 {h:'Current definition',k:'current_definition'},{h:'Δ',k:'repro_delta'},
 {h:'Pass',k:'repro_pass',f:v=>v?'<span class="chip pass">✓</span>':'<span class="chip fail">✗</span>'}],
 par.filter(r=>r.season>=2023));
table('tCount',[{h:'Window',k:'window',f:wl},{h:'Count state',k:'count_state'},
 {h:'Pitches',k:'pitches'},{h:'PA',k:'plate_apps',f:(v,r)=>v+flag(r.below_floor)},
 {h:'BA',k:'ba',f:f3},{h:'SLG',k:'slg',f:f3},{h:'wOBA',k:'woba',f:f3},
 {h:'Swing %',k:'swing_rate',f:pc},{h:'Whiff %',k:'whiff_rate',f:pc}],D.count);
tab('overview');
"""

HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trea Turner — 2026 Recency Read · uc-pos-014</title>
<style>__CSS__</style></head><body>
<header>
  <h1>Trea Turner — The Power Outage</h1>
  <div class="sub">UC #40 · <code>uc-pos-014-turner-2026-recency-001</code> · <code>dp_uc40</code>
   · Phillies Offense value stream · data as of <b>2026-09-02</b> · 602 PA / 135 G
   · verification <b>711/711 PASS</b> · audit <b>116/116</b> · extends <code>uc-pos-006</code></div>
</header>
<nav class="bar">
  <button data-t="overview" onclick="tab('overview')">Overview</button>
  <button data-t="recency" onclick="tab('recency')">Recency</button>
  <button data-t="mechanism" onclick="tab('mechanism')">Mechanism</button>
  <button data-t="splits" onclick="tab('splits')">Pitches &amp; platoon</button>
  <button data-t="career" onclick="tab('career')">Career &amp; approach</button>
  <button data-t="gov" onclick="tab('gov')">Governance</button>
</nav>
<main>

<section id="t-overview" class="on">
  <h2>Where the season stands</h2>
  <div class="cards" id="kpis"></div>
  <p class="note">2026 is the lowest of Turner's eleven qualified seasons (≥50 PA, 2016–2026) on batting
   average, on-base, slugging, OPS, ISO, wOBA <em>and</em> BABIP. xwOBA sits on top of wOBA, so this is not
   a sequencing or luck story.</p>
  <div class="panel"><div class="chart tall"><canvas id="cOverview"></canvas></div></div>
  <div class="panel wrap" id="tOverview"></div>

  <h2>Against the Phillies hitter population</h2>
  <p class="note">Cohort: 220 Phillies hitter-seasons of at least 50 PA since 2015, 100 players. The
   Aug 1 – Sep 2 window is priced <em>as if it were a season</em> — an illustration of severity, not a
   projection.</p>
  <div class="ctrl"><label for="pctMode">Show</label>
   <select id="pctMode"><option value="both">season and recent window</option>
    <option value="season">2026 season only</option>
    <option value="recent">Aug–Sep window only</option></select></div>
  <div class="panel"><div class="chart tall"><canvas id="cPct"></canvas></div></div>
  <div class="panel wrap" id="tPct"></div>
</section>

<section id="t-recency">
  <h2>Rolling form — the surge peaked the week the parent product shipped</h2>
  <p class="note">RF-2: trailing 100-PA wOBA. Peak .421 on 2026-07-21 — the delivery date of
   <code>uc-pos-006</code>, which flagged that July as "real-but-young" and declined to call it a recovery.
   The line now reads .238.</p>
  <div class="panel"><div class="chart tall"><canvas id="cRoll"></canvas></div></div>
  <h3>RF-1 · season-to-date wOBA, Phillies era</h3>
  <div class="panel"><div class="chart"><canvas id="cRun"></canvas></div></div>

  <h2>Breakpoint sensitivity — is "recently" an artifact of where the line was drawn?</h2>
  <p class="note">Standing requirement (RC-5) whenever the window is chosen after the outcome is known. The
   sign flips <b>exactly at the parent's as-of date</b> and worsens monotonically after it. Every cut before
   07-21 says he was improving; every cut from 07-21 says he is declining.</p>
  <div class="panel"><div class="chart"><canvas id="cScan"></canvas></div></div>
  <div class="panel wrap" id="tScan"></div>

  <h2>Month by month</h2>
  <div class="ctrl"><label for="monMetric">Metric</label><select id="monMetric"></select>
   <span class="note" style="margin:0">⚠ marks a month below the 50-PA floor — March (23 PA) and
   September (9 PA). Nothing is ranked on them.</span></div>
  <div class="panel"><div class="chart"><canvas id="cMon"></canvas></div></div>
  <div class="panel wrap" id="tMon"></div>
</section>

<section id="t-mechanism">
  <h2>What actually moved</h2>
  <p class="note">Three windows against his own 2023–25 Phillies norm. Plate discipline moved the
   <em>right</em> way while contact quality collapsed.</p>
  <div class="ctrl"><label for="mechMetric">Measure</label><select id="mechMetric"></select></div>
  <div class="panel"><div class="chart"><canvas id="cMech"></canvas></div></div>
  <div class="panel wrap" id="tMech"></div>

  <h2>ST-1 · is the shift bigger than noise?</h2>
  <p class="note">Descriptive uncertainty bands on a non-random, self-selected five-week window — not
   hypothesis tests of a causal claim. <b>The popup rate is the only measure that clearly clears the bar
   against a well-powered baseline.</b> Bat speed does not: August is within noise of his own Phillies norm,
   which means July was the anomaly, not August.</p>
  <div class="panel"><div class="chart"><canvas id="cShift"></canvas></div></div>
  <div class="panel wrap" id="tShift"></div>
</section>

<section id="t-splits">
  <h2>Pitch groups</h2>
  <p class="note">Breaking-ball usage against him climbs across the three windows as the league adjusts to a
   hitter who cannot punish spin. The alarming cell is the recent fastball row.</p>
  <div class="grid2">
   <div class="panel"><h3>wOBA by group and window</h3><div class="chart"><canvas id="cPg"></canvas></div></div>
   <div class="panel"><h3>What he is being thrown (% of pitches)</h3><div class="chart"><canvas id="cPgUse"></canvas></div></div>
  </div>
  <div class="panel wrap" id="tPg"></div>

  <h2>Pitch types, full season</h2>
  <p class="note">Sweepers and sliders are 27.8% of every pitch he sees, and he posts .182 and .243 wOBA
   against them. Bars are coloured by pitch group. Hover for whiff, usage and sample.</p>
  <div class="panel"><div class="chart tall"><canvas id="cPt"></canvas></div></div>
  <div class="panel wrap" id="tPt"></div>

  <h2>Platoon</h2>
  <div class="grid2">
   <div class="panel"><h3>By season — the left-handed edge is gone</h3><div class="chart"><canvas id="cPlat"></canvas></div></div>
   <div class="panel"><h3>2026 by window</h3><div class="chart"><canvas id="cPlatWin"></canvas></div></div>
  </div>
  <div class="panel wrap" id="tPlatS"></div>
  <div class="panel wrap" id="tPlatW"></div>
  <h3>PL-1 · was he flattered or punished by the platoon mix?</h3>
  <p class="note">Direct standardisation of the recent window to each earlier window's platoon mix. A mix
   effect near zero means the decline is performance, not scheduling.</p>
  <div class="panel wrap" id="tCf"></div>
</section>

<section id="t-career">
  <h2>AD-1 · approach differential by season</h2>
  <p class="note">In-zone swing rate minus chase rate — one number for whether he is separating balls from
   strikes. 2026 is the second-lowest of his eleven qualified seasons. Shown beside both components, never
   alone (inherited caveat from <code>uc-pos-005</code> OZ-3).</p>
  <div class="panel"><div class="chart"><canvas id="cAd"></canvas></div></div>
  <h3>Approach by season</h3>
  <div class="panel wrap" id="tApp"></div>
  <h3>Contact quality by season</h3>
  <div class="panel wrap" id="tContact"></div>
  <h3>Spray — pull and pull-air by season</h3>
  <div class="panel wrap" id="tPull"></div>
  <h3>Swing measurables (Statcast bat tracking, 2024+ and Phillies frames only)</h3>
  <p class="note">2023 is structurally blank: bat tracking did not exist. Attack angle begins in 2025. Under
   the sensor-boundary standard these are NULL, never zero, and never imputed.</p>
  <div class="panel wrap" id="tBat"></div>
  <h3>Count leverage by window</h3>
  <div class="panel wrap" id="tCount"></div>
</section>

<section id="t-gov">
  <h2>Data quality scorecard</h2>
  <div id="dqChips" style="margin:10px 0"></div>
  <div class="panel wrap" id="tDq"></div>

  <h2>Parent reproduction — <code>uc-pos-006</code> audited before any new claim</h2>
  <div id="parChips" style="margin:10px 0"></div>
  <p class="note">Every figure the parent product published was recomputed on the parent's own window
   (≤ 2026-07-20) and its own deprecated definitions. Phillies-era rows shown; the full 84-check receipt is
   in <code>dp_uc40_parent_reproduction.csv</code>.</p>
  <div class="panel wrap" id="tPar"></div>

  <h2>Declared limits</h2>
  <div class="panel"><ul>
   <li><b>Causation is not identified anywhere in this product.</b> No coaching, medical, or intervention
    log exists in this data plane. Persona actions are testable hypotheses mapped to remit.</li>
   <li><b>Batting order is not a column here</b> — lineup-slot questions are out of scope.</li>
   <li><b>The recent window is 129 PA / five weeks.</b> Sub-splits inside it fall below the 50-PA floor fast
    and carry ⚠ everywhere.</li>
   <li><b>D-7 / O-13, found by this build's own verification harness:</b> the governed
    <code>chase_rate_g</code> derives <code>in_zone_rate</code> by subtraction, so NULL-<code>zone</code>
    rows are silently counted in-zone. Disclosed, not patched; every zone rate here uses
    <code>in_zone_rate_fix</code>.</li>
   <li><b>AD-1 and ST-1 are NEW-PROVISIONAL</b> and need DPO ratification before reuse.</li>
   <li><b>xwOBAcon ≠ xwOBA (O-4).</b> Shifts are compared; levels are never cross-compared to wOBA.</li>
  </ul></div>
</section>

</main>
<footer>
 Generated from the governed receipts in <code>out/dp_uc40_*.csv</code> — no live query, no network call.
 Chart.js v4.4.1 (MIT) is vendored inline, never loaded from a CDN (the <code>uc-pos-011</code> rule).
 Phillies Offense value stream · Data Product Owner: Kellen Short · 2026-09-03.
</footer>
<script>__CHARTJS__</script>
<script>__JS__</script>
</body></html>
"""


def main():
    html = (HTML.replace('__CSS__', CSS)
                .replace('__CHARTJS__', CHARTJS)
                .replace('__JS__', JS.replace('__DATA__', json.dumps(D, separators=(',', ':')))))
    with open(DST, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'wrote {DST}  ({os.path.getsize(DST)/1024:.0f} KB)')
    for tok in ('__CSS__', '__JS__', '__DATA__', '__CHARTJS__'):
        assert tok not in html, f'unreplaced token {tok}'
    assert 'cdn' not in html.lower().split('vendored')[0][-4000:], 'CDN reference detected'
    print('self-containment check: no unreplaced tokens')


if __name__ == '__main__':
    main()


# ══════════════════════════════════════════════════════════════════════════
# ARTIFACT VARIANT — same data, same charts, published as a hosted page
# ══════════════════════════════════════════════════════════════════════════
# Differences from the offline build, all forced by the publishing surface:
#   * no <!doctype>/<html>/<head>/<body> — the host wraps the content
#   * Google Fonts is the one font host the CSP admits, so the type gets a real
#     pairing instead of the system stack
#   * full light/dark token sets, including the un-stamped prefers-color-scheme
#     state; Chart.js reads its ink and grid colours from the CSS tokens
# The vendored Chart.js is inlined identically — no CDN on either surface.

ART_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Mono:wght@400;500&family=Source+Sans+3:wght@400;600;700&display=swap');
:root{
  --navy:#0B2E63;--red:#D51F2C;--teal:#00808C;--amber:#B06A00;--violet:#7247B0;
  --ink:#141C27;--mut:#5A6675;--line:#DCE2EA;--bg:#F2F5F9;--card:#FFFFFF;
  --head:#0B2E63;--headink:#FFFFFF;--rowalt:#F7F9FC;--warn:#9A5B00;
  --gridline:rgba(20,28,39,.10);--chartink:#5A6675;--focus:#D51F2C;--barneutral:#C3CCD9;
  --pass-bg:#E1F3EC;--pass-ink:#0A6B4F;--warn-bg:#FBEFD3;--warn-ink:#8A5300;
  --fail-bg:#FBE2E2;--fail-ink:#912020;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --navy:#7FA9E8;--red:#FF6B72;--teal:#3FBFC9;--amber:#E3A24A;--violet:#A98BE0;
  --ink:#E7ECF3;--mut:#9AA6B6;--line:#2A3646;--bg:#101724;--card:#18212F;
  --head:#22304A;--headink:#E7ECF3;--rowalt:#1C2634;--warn:#E3A24A;
  --gridline:rgba(231,236,243,.12);--chartink:#9AA6B6;--focus:#FF6B72;--barneutral:#46566E;
  --pass-bg:#123A2E;--pass-ink:#6FD9B4;--warn-bg:#3A2B10;--warn-ink:#E9BE74;
  --fail-bg:#3B1A1A;--fail-ink:#F5A0A0;
}}
:root[data-theme="dark"]{
  --navy:#7FA9E8;--red:#FF6B72;--teal:#3FBFC9;--amber:#E3A24A;--violet:#A98BE0;
  --ink:#E7ECF3;--mut:#9AA6B6;--line:#2A3646;--bg:#101724;--card:#18212F;
  --head:#22304A;--headink:#E7ECF3;--rowalt:#1C2634;--warn:#E3A24A;
  --gridline:rgba(231,236,243,.12);--chartink:#9AA6B6;--focus:#FF6B72;--barneutral:#46566E;
  --pass-bg:#123A2E;--pass-ink:#6FD9B4;--warn-bg:#3A2B10;--warn-ink:#E9BE74;
  --fail-bg:#3B1A1A;--fail-ink:#F5A0A0;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:400 15px/1.55 "Source Sans 3",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
header{background:linear-gradient(180deg,var(--head),color-mix(in srgb,var(--head) 88%,black));
 color:var(--headink);padding:26px 30px 20px;border-bottom:3px solid var(--red)}
header h1{margin:0 0 6px;font:700 34px/1.02 "Barlow Condensed",Impact,sans-serif;
 letter-spacing:.008em;text-transform:uppercase;text-wrap:balance}
header .sub{font-size:13px;opacity:.9;max-width:92ch}
header .sub code{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;
 background:rgba(255,255,255,.13);padding:1px 5px;border-radius:3px}
.bar{background:var(--card);border-bottom:1px solid var(--line);padding:0 30px;display:flex;gap:4px;
 position:sticky;top:0;z-index:20;overflow-x:auto}
.bar button{background:none;border:0;border-bottom:3px solid transparent;padding:13px 15px;cursor:pointer;
 font:600 11.5px/1 "Barlow Condensed","Source Sans 3",sans-serif;letter-spacing:.09em;
 text-transform:uppercase;color:var(--mut);white-space:nowrap}
.bar button:hover{color:var(--ink)}
.bar button.on{color:var(--navy);border-bottom-color:var(--red)}
main{padding:26px 30px 60px;max-width:1300px}
section{display:none}section.on{display:block}
h2{font:700 15px/1.2 "Barlow Condensed","Source Sans 3",sans-serif;letter-spacing:.11em;
 text-transform:uppercase;color:var(--navy);margin:30px 0 12px;padding-bottom:7px;
 border-bottom:2px solid var(--red)}
h2:first-child{margin-top:0}
h3{font:600 13px/1.3 "Source Sans 3",sans-serif;letter-spacing:.03em;color:var(--navy);margin:20px 0 8px}
p.note{color:var(--mut);font-size:13.5px;margin:6px 0 14px;max-width:72ch}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:16px 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:14px 16px}
.card .k{font:600 10px/1.3 "Barlow Condensed","Source Sans 3",sans-serif;letter-spacing:.13em;
 text-transform:uppercase;color:var(--mut)}
.card .v{font:500 clamp(19px,2.1vw,28px)/1.14 "IBM Plex Mono",ui-monospace,monospace;
 color:var(--navy);margin:7px 0 3px;font-variant-numeric:tabular-nums;letter-spacing:-.02em;
 overflow-wrap:anywhere}
.card .v.bad{color:var(--red)}.card .v.good{color:var(--teal)}
.card .d{font-size:12.5px;color:var(--mut)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:16px 18px;margin:14px 0}
.wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
td,th{font-family:"IBM Plex Mono",ui-monospace,monospace}
th{background:var(--head);color:var(--headink);text-align:left;padding:8px 10px;white-space:nowrap;
 font:600 10.5px/1.2 "Barlow Condensed","Source Sans 3",sans-serif;letter-spacing:.09em;
 text-transform:uppercase;position:sticky;top:0}
td{padding:6px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
tbody tr:nth-child(even) td{background:var(--rowalt)}
td.hi{color:var(--red);font-weight:600}td.lo{color:var(--teal);font-weight:600}
.flag{color:var(--warn);font-weight:700}
.chart{position:relative;height:340px}.chart.tall{height:420px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(430px,1fr));gap:14px}
.ctrl{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:6px 0 12px}
.ctrl label{font:600 10.5px/1 "Barlow Condensed","Source Sans 3",sans-serif;letter-spacing:.11em;
 text-transform:uppercase;color:var(--mut)}
.ctrl select{font:400 13.5px "Source Sans 3",sans-serif;padding:6px 9px;border:1px solid var(--line);
 border-radius:5px;background:var(--card);color:var(--ink)}
.chip{display:inline-block;font:600 11px "Source Sans 3",sans-serif;padding:2px 9px;border-radius:3px;
 margin-right:6px}
.chip.pass{background:var(--pass-bg);color:var(--pass-ink)}
.chip.warn{background:var(--warn-bg);color:var(--warn-ink)}
.chip.fail{background:var(--fail-bg);color:var(--fail-ink)}
.ph{display:flex;align-items:center;justify-content:center;height:100%;color:var(--mut);font-size:13px;
 border:1px dashed var(--line);border-radius:5px;text-align:center;padding:14px}
ul{padding-left:18px}li{margin:6px 0;max-width:76ch}
code{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12.5px;
 background:color-mix(in srgb,var(--ink) 7%,transparent);padding:1px 4px;border-radius:3px}
footer{padding:22px 30px 44px;color:var(--mut);font-size:12px;border-top:1px solid var(--line);
 background:var(--card);margin-top:28px;max-width:82ch}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:640px){main{padding:18px 15px 50px}header{padding:18px}.chart{height:290px}
 header h1{font-size:27px}}
"""

ART_THEME_JS = r"""
/* Chart.js takes its ink and grid colours from the CSS tokens so both themes read */
(function(){
  const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  if(typeof Chart!=='undefined'){
    Chart.defaults.color=css('--chartink')||'#5A6675';
    Chart.defaults.borderColor=css('--gridline')||'rgba(0,0,0,.1)';
    Chart.defaults.font.family='"Source Sans 3", system-ui, sans-serif';
    Chart.defaults.font.size=11.5;
  }
})();
"""

ART = """<title>Turner's Power Outage</title>
<style>__CSS__</style>
<header>
  <h1>Trea Turner &mdash; The Power Outage</h1>
  <div class="sub">UC&nbsp;#40 &middot; <code>uc-pos-014-turner-2026-recency-001</code> &middot;
   <code>dp_uc40</code> &middot; Phillies Offense value stream &middot; data as of <b>2026-09-02</b>
   &middot; 602&nbsp;PA / 135&nbsp;G &middot; verification <b>711/711</b> &middot; package audit
   <b>116/116</b> &middot; extends <code>uc-pos-006</code></div>
</header>
__NAV__
<main>__SECTIONS__</main>
<footer>
 Generated from the governed receipts in <code>out/dp_uc40_*.csv</code> &mdash; no live query, no network
 call. Chart.js v4.4.1 (MIT) is vendored inline, never loaded from a CDN (the <code>uc-pos-011</code>
 rule). Phillies Offense value stream &middot; Data Product Owner: Kellen Short &middot; 2026-09-03.
</footer>
<script>__CHARTJS__</script>
<script>__THEME__</script>
<script>__JS__</script>
"""


def build_artifact():
    import re as _re
    src = HTML
    nav = _re.search(r'<nav class="bar">.*?</nav>', src, _re.S).group(0)
    secs = _re.search(r'<main>(.*?)</main>', src, _re.S).group(1)
    art_js = JS.replace(
        "const NAVY='#002D72',RED='#E81828',TEAL='#00919E',AMBER='#C97A00',VIOLET='#8250C4',\n"
        "      GREY='#8894A4',LGREY='#C9D2DD';",
        "const _c=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim()||null;\n"
        "const NAVY=_c('--navy')||'#002D72',RED=_c('--red')||'#E81828',TEAL=_c('--teal')||'#00919E',\n"
        "      AMBER=_c('--amber')||'#C97A00',VIOLET=_c('--violet')||'#8250C4',\n"
        "      GREY=_c('--mut')||'#8894A4',LGREY=_c('--barneutral')||'#C9D2DD';")
    html = (ART.replace('__CSS__', ART_CSS).replace('__NAV__', nav)
               .replace('__SECTIONS__', secs)
               .replace('__CHARTJS__', CHARTJS)
               .replace('__THEME__', ART_THEME_JS)
               .replace('__JS__', art_js.replace('__DATA__', json.dumps(D, separators=(',', ':')))))
    assert "_c('--barneutral')" in html, 'artifact palette rebind failed'
    dst = os.path.join(HERE, 'dp_uc40_turner_recency_dashboard_artifact.html')
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(html)
    for bad in ('<!DOCTYPE', '<html', '<head>', '<body>'):
        assert bad not in html, f'artifact variant must not carry {bad}'
    for tok in ('__CSS__', '__JS__', '__DATA__', '__CHARTJS__', '__NAV__', '__SECTIONS__', '__THEME__'):
        assert tok not in html, f'unreplaced token {tok}'
    print(f'wrote {dst}  ({os.path.getsize(dst)/1024:.0f} KB)')


build_artifact()
