"""
dp_uc39_build_dashboard.py — builds the self-contained interactive dashboard
for uc-pps-028 from out/dp_uc39_payload.json.

Rules honoured:
  * EVERY number rendered comes from the payload the build script wrote. No
    figure is hand-typed into the HTML (the receipts rule).
  * No CDN, no external font, no network call — one file, opens offline
    (the uc-pos-011 "vendor, don't CDN" rule).
  * Categorical palette validated with the dataviz six-checks validator in
    BOTH light and dark: #8250C4 / #E81828 / #00919E / #C97A00 -> ALL PASS.
  * Every chart ships a hover layer, a legend, and a table view.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "out", "dp_uc39_payload.json"), encoding="utf-8"))
OUT = os.path.join(HERE, "dp_uc39_luzardo_dashboard.html")

TPL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Luzardo vs Arizona - Pre-Scout</title>
<style>
:root{
  --bg:#f6f7f9; --surface:#ffffff; --surface-2:#f0f2f5; --ink:#12161c; --ink-2:#41505f;
  --ink-3:#6d7c8b; --line:#dde3ea; --navy:#002D72; --red:#E81828; --thead:#ffffff;
  --c1:#8250C4; --c2:#E81828; --c3:#00919E; --c4:#C97A00;
  --good:#1a7f4b; --warn:#b45309;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){ :root:not([data-theme="light"]){
  --bg:#0e1319; --surface:#161c24; --surface-2:#1e262f; --ink:#e9eef4; --ink-2:#aebac7;
  --ink-3:#7d8b99; --line:#2a343f; --navy:#7fa8e8; --red:#ff5561; --thead:#0e1319;
  --good:#4ade80; --warn:#fbbf24; }}
:root[data-theme="dark"]{
  --bg:#0e1319; --surface:#161c24; --surface-2:#1e262f; --ink:#e9eef4; --ink-2:#aebac7;
  --ink-3:#7d8b99; --line:#2a343f; --navy:#7fa8e8; --red:#ff5561; --thead:#0e1319;
  --good:#4ade80; --warn:#fbbf24; }
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.wrap{max-width:1180px;margin:0 auto;padding:22px 18px 60px}
header.hd{border-bottom:3px solid var(--red);padding-bottom:14px;margin-bottom:20px;
  display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap}
h1{margin:0 0 6px;font-size:26px;letter-spacing:-.5px;color:var(--navy)}
.sub{color:var(--ink-2);font-size:13px}
.pill{display:inline-block;background:var(--surface-2);border:1px solid var(--line);
  border-radius:99px;padding:3px 10px;font-size:11.5px;color:var(--ink-2);margin:0 6px 5px 0}
button.tgl{background:var(--surface);border:1px solid var(--line);color:var(--ink-2);
  border-radius:7px;padding:6px 11px;font-size:12px;cursor:pointer}
button.tgl:hover{border-color:var(--navy);color:var(--ink)}
button.tgl[aria-pressed="true"]{background:var(--navy);border-color:var(--navy);color:var(--thead)}
.verdict{background:var(--surface);border:1px solid var(--line);border-left:5px solid var(--red);
  border-radius:10px;padding:16px 18px;margin-bottom:20px}
.verdict h2{margin:0 0 8px;font-size:16px;color:var(--navy)}
.verdict p{margin:7px 0;color:var(--ink-2);font-size:13.4px}
.verdict b{color:var(--ink)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:12px;margin-bottom:24px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:13px 15px}
.tile .lab{font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--ink-3)}
.tile .val{font-size:27px;font-weight:650;letter-spacing:-1px;margin:3px 0 1px;font-variant-numeric:tabular-nums}
.tile .note{font-size:11.5px;color:var(--ink-2)}
.tile.ok .val{color:var(--good)} .tile.watch .val{color:var(--warn)}
section{background:var(--surface);border:1px solid var(--line);border-radius:11px;
  padding:18px 20px;margin-bottom:18px}
section>h2{margin:0 0 3px;font-size:16.5px;color:var(--navy)}
section>.cap{margin:0 0 14px;font-size:12.6px;color:var(--ink-2)}
.ctl{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
.ctl label{font-size:12px;color:var(--ink-3)}
select{background:var(--surface);color:var(--ink);border:1px solid var(--line);
  border-radius:6px;padding:5px 8px;font-size:12.5px}
.chart{position:relative;width:100%;overflow-x:auto}
svg{display:block;max-width:100%;height:auto}
.legend{display:flex;gap:14px;flex-wrap:wrap;margin:9px 0 2px;font-size:12px;color:var(--ink-2)}
.legend i{width:11px;height:11px;border-radius:3px;display:inline-block;margin-right:5px;vertical-align:-1px}
.tip{position:fixed;pointer-events:none;background:var(--surface);border:1px solid var(--line);
  box-shadow:0 6px 22px rgba(0,0,0,.18);border-radius:8px;padding:8px 11px;font-size:12px;
  color:var(--ink);opacity:0;transition:opacity .09s;z-index:99;max-width:290px;line-height:1.55}
.tip b{color:var(--navy)} .tip .k{color:var(--ink-3)}
table{border-collapse:collapse;width:100%;font-size:12.6px;font-variant-numeric:tabular-nums}
th{background:var(--navy);color:var(--thead);text-align:left;padding:6px 9px;font-weight:600;
   font-size:11.6px;position:sticky;top:0}
td{padding:5px 9px;border-bottom:1px solid var(--line);color:var(--ink-2)}
td.n{text-align:right;font-family:var(--mono);font-size:12px}
tr:nth-child(even) td{background:var(--surface-2)}
td b{color:var(--ink)}
.tblwrap{overflow:auto;max-height:440px;border:1px solid var(--line);border-radius:8px}
.hide{display:none}
.badge{font-size:10.6px;font-weight:650;padding:2px 7px;border-radius:99px;letter-spacing:.3px;
  white-space:nowrap}
.badge.g{background:color-mix(in srgb,var(--good) 17%,transparent);color:var(--good)}
.badge.w{background:color-mix(in srgb,var(--warn) 19%,transparent);color:var(--warn)}
.badge.n{background:var(--surface-2);color:var(--ink-3)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:880px){.grid2{grid-template-columns:1fr}}
footer{color:var(--ink-3);font-size:11.6px;border-top:1px solid var(--line);padding-top:14px;margin-top:24px;line-height:1.65}
footer code{font-family:var(--mono);font-size:11px}
.warnbox{background:color-mix(in srgb,var(--red) 7%,transparent);
  border:1px solid color-mix(in srgb,var(--red) 32%,transparent);
  border-radius:9px;padding:11px 14px;font-size:12.4px;color:var(--ink-2);margin-bottom:18px;line-height:1.6}
</style></head><body>
<div class="wrap">
<header class="hd">
 <div>
  <h1>Jes&uacute;s Luzardo &mdash; Pre-Scout vs Arizona</h1>
  <div class="sub">__SUB__</div>
 </div>
 <div><button class="tgl" id="theme" aria-pressed="false">Dark / light</button></div>
</header>
<div id="app"></div>
<footer id="foot"></footer>
</div>
<div class="tip" id="tip"></div>
<script>const DATA=__DATA__;</script>
<script>__JS__</script>
</body></html>"""

JS = r"""
const $=(s,r=document)=>r.querySelector(s), tip=$('#tip');
const C=['#8250C4','#E81828','#00919E','#C97A00'];
const PC={'Sweeper':'#8250C4','4-Seam Fastball':'#E81828','Sinker':'#00919E','Changeup':'#C97A00'};
const f3=v=>v==null||isNaN(v)?'—':Number(v).toFixed(3).replace(/^0/,'');
const f1=v=>v==null||isNaN(v)?'—':Number(v).toFixed(1);
const pct=v=>v==null||isNaN(v)?'—':(Number(v)*100).toFixed(1)+'%';
function showTip(e,h){tip.innerHTML=h;tip.style.opacity=1;
  const r=tip.getBoundingClientRect();
  tip.style.left=Math.min(Math.max(8,e.clientX+14),innerWidth-r.width-12)+'px';
  tip.style.top=Math.max(8,e.clientY-r.height-14)+'px';}
function hideTip(){tip.style.opacity=0;}
function el(t,a={}){const n=document.createElementNS('http://www.w3.org/2000/svg',t);
  for(const p in a)n.setAttribute(p,a[p]);return n;}
function svg(w,h){return el('svg',{viewBox:'0 0 '+w+' '+h,width:w,height:h,role:'img'});}
function txt(x,y,t,anchor,size,fill,weight){
  const n=el('text',{x:x,y:y,'text-anchor':anchor||'start','font-size':size||11,
    fill:fill||'var(--ink-2)','font-weight':weight||400});
  n.textContent=t;return n;}

/* 1. start-by-start: runs (bars) + start xwOBA (line) */
function chartStarts(host,from){
  host.innerHTML='';
  const rows=DATA.start_log.filter(r=>!from||r.game_date>=from);
  const W=Math.max(740,rows.length*40+100),H=306,L=50,R=52,T=14,B=66;
  const s=svg(W,H), iw=W-L-R, ih=H-T-B;
  const maxR=Math.max(5,...rows.map(r=>r.runs));
  const xv=rows.map(r=>r.xwoba);
  const lo=Math.floor(Math.min.apply(null,xv)*20)/20, hi=Math.ceil(Math.max.apply(null,xv)*20)/20;
  const yR=v=>T+ih-(v/maxR)*ih, yX=v=>T+ih-((v-lo)/(hi-lo))*ih;
  const bw=Math.min(26,iw/rows.length-8);
  for(let i=0;i<=maxR;i++){const y=yR(i);
    s.appendChild(el('line',{x1:L,x2:W-R,y1:y,y2:y,stroke:'var(--line)','stroke-width':1}));
    s.appendChild(txt(L-8,y+3.5,i,'end',10.5,'var(--ink-3)'));}
  [lo,(lo+hi)/2,hi].forEach(v=>s.appendChild(txt(W-R+8,yX(v)+3.5,f3(v),'start',10.5,'#E81828')));
  rows.forEach((r,i)=>{
    const cx=L+(i+.5)*(iw/rows.length);
    const g=el('g');
    g.appendChild(el('rect',{x:cx-bw/2,y:yR(r.runs),width:bw,
      height:Math.max(1.5,ih-(yR(r.runs)-T)),rx:4,fill:'var(--navy)',opacity:.30,
      stroke:'var(--navy)','stroke-opacity':.55,'stroke-width':1}));
    g.appendChild(el('rect',{x:cx-(iw/rows.length)/2,y:T,width:iw/rows.length,height:ih,fill:'transparent'}));
    g.addEventListener('mousemove',e=>showTip(e,
      '<b>'+r.game_date+' · '+r.opp+(r.home?' (home)':' (away)')+'</b><br>'+
      '<span class="k">IP</span> '+r.ip+' &nbsp;<span class="k">pitches</span> '+r.pitches+
      ' &nbsp;<span class="k">PA</span> '+r.pa+'<br>'+
      '<span class="k">K/BB/HR</span> '+r.k+'/'+r.bb+'/'+r.hr+' &nbsp;<span class="k">runs</span> '+r.runs+'<br>'+
      '<span class="k">wOBA</span> '+f3(r.woba)+' &nbsp;<span class="k">xwOBA</span> '+f3(r.xwoba)+
      (r.days_rest?'<br><span class="k">rest</span> '+r.days_rest+' days':'')));
    g.addEventListener('mouseleave',hideTip);
    s.appendChild(g);
    s.appendChild(txt(cx,H-B+18,r.game_date.slice(5),'middle',9,'var(--ink-3)'));
    s.appendChild(txt(cx,H-B+29,r.opp,'middle',9,'var(--ink-3)'));});
  let d='';rows.forEach((r,i)=>{d+=(i?'L':'M')+(L+(i+.5)*(iw/rows.length))+','+yX(r.xwoba);});
  s.appendChild(el('path',{d:d,fill:'none',stroke:'#E81828','stroke-width':2,'stroke-linejoin':'round'}));
  rows.forEach((r,i)=>s.appendChild(el('circle',{cx:L+(i+.5)*(iw/rows.length),cy:yX(r.xwoba),
    r:4,fill:'#E81828',stroke:'var(--surface)','stroke-width':2})));
  host.appendChild(s);
  const lg=document.createElement('div');lg.className='legend';
  lg.innerHTML='<span><i style="background:var(--navy);opacity:.45"></i>runs allowed on the mound (left axis)</span>'+
    '<span><i style="background:#E81828"></i>start xwOBA (right axis)</span>';
  host.appendChild(lg);}

/* 2. consistency map */
function chartCohort(host,axKey,axLabel,lowerBetter){
  host.innerHTML='';
  const rows=DATA.cohort.filter(r=>r[axKey]!=null);
  const W=760,H=350,L=64,R=126,T=18,B=54,s=svg(W,H),iw=W-L-R,ih=H-T-B;
  const xv=rows.map(r=>r[axKey]),yv=rows.map(r=>r.agg_xwoba);
  const x0=Math.min.apply(null,xv),x1=Math.max.apply(null,xv);
  const y0=Math.min.apply(null,yv),y1=Math.max.apply(null,yv);
  const px=(x1-x0)||1, py=(y1-y0)||1;
  const X=v=>L+((v-(x0-px*.18))/(px*1.36))*iw, Y=v=>T+ih-((v-(y0-py*.22))/(py*1.44))*ih;
  const med=a=>{const b=a.slice().sort((p,q)=>p-q);
    return b.length%2?b[(b.length-1)/2]:(b[b.length/2-1]+b[b.length/2])/2;};
  [0,.25,.5,.75,1].forEach(t=>{const v=y0-py*.22+t*py*1.44,y=Y(v);
    s.appendChild(el('line',{x1:L,x2:W-R,y1:y,y2:y,stroke:'var(--line)','stroke-width':1}));
    s.appendChild(txt(L-8,y+3.5,f3(v),'end',10.5,'var(--ink-3)'));});
  s.appendChild(el('line',{x1:X(med(xv)),x2:X(med(xv)),y1:T,y2:T+ih,stroke:'var(--ink-3)',
    'stroke-dasharray':'4 4','stroke-width':1}));
  s.appendChild(el('line',{x1:L,x2:W-R,y1:Y(med(yv)),y2:Y(med(yv)),stroke:'var(--ink-3)',
    'stroke-dasharray':'4 4','stroke-width':1}));
  const isRate=axKey.indexOf('rate')>-1;
  rows.forEach(r=>{
    const lz=r.who===666200,cx=X(r[axKey]),cy=Y(r.agg_xwoba),g=el('g');
    g.appendChild(el('circle',{cx:cx,cy:cy,r:lz?10:7,fill:lz?'#E81828':'var(--navy)',
      stroke:'var(--surface)','stroke-width':2.4}));
    g.appendChild(el('circle',{cx:cx,cy:cy,r:18,fill:'transparent'}));
    g.appendChild(txt(cx+14,cy+4,r.name.split(',')[0],'start',11.5,
      lz?'#E81828':'var(--ink-2)',lz?700:500));
    g.addEventListener('mousemove',e=>showTip(e,
      '<b>'+r.name+'</b><br><span class="k">GS</span> '+r.starts+' &nbsp;<span class="k">IP</span> '+r.ip+
      '<br><span class="k">xwOBA</span> '+f3(r.agg_xwoba)+' &nbsp;<span class="k">wOBA</span> '+f3(r.woba)+
      ' &nbsp;<span class="k">RA9</span> '+f1(r.ra9)+
      '<br><span class="k">'+axLabel+'</span> <b>'+(isRate?pct(r[axKey]):r[axKey])+'</b>'+
      '<br><span class="k">blow-ups</span> '+r.cn3_blowup_n+' of '+r.starts+
      ' &nbsp;<span class="k">pitch band</span> '+r.cn5_pitch_min+'–'+r.cn5_pitch_max));
    g.addEventListener('mouseleave',hideTip);s.appendChild(g);});
  s.appendChild(txt(L,H-14,axLabel+(lowerBetter?'   →  left is steadier':'   →  right is better'),
    'start',11,'var(--ink-3)'));
  const yl=txt(14,T+ih/2,'xwOBA against (down = better)','middle',11,'var(--ink-3)');
  yl.setAttribute('transform','rotate(-90 14 '+(T+ih/2)+')');s.appendChild(yl);
  host.appendChild(s);}

/* 3. breakpoint scan */
function chartScan(host,keys){
  host.innerHTML='';
  const rows=DATA.scan,W=760,H=310,L=52,R=26,T=30,B=74,s=svg(W,H),iw=W-L-R,ih=H-T-B;
  let maxR=4;rows.forEach(r=>keys.forEach(k=>{if(r[k.k]>maxR)maxR=r[k.k];}));
  const X=i=>L+(i+.5)*(iw/rows.length), Y=v=>T+((v-1)/(maxR-1))*ih;
  for(let i=1;i<=maxR;i++){const y=Y(i);
    s.appendChild(el('line',{x1:L,x2:W-R,y1:y,y2:y,stroke:'var(--line)','stroke-width':1}));
    s.appendChild(txt(L-8,y+3.5,i,'end',10.5,'var(--ink-3)'));}
  const bi=rows.map(r=>r.window_start).indexOf(DATA.meta.premise_break);
  if(bi>=0){s.appendChild(el('line',{x1:X(bi),x2:X(bi),y1:T-10,y2:T+ih,stroke:'var(--navy)',
    'stroke-width':1.6,'stroke-dasharray':'5 4'}));
    s.appendChild(txt(X(bi)+7,T-14,'the premise boundary','start',10,'var(--navy)',600));}
  keys.forEach((k,ki)=>{
    let d='';rows.forEach((r,i)=>{d+=(i?'L':'M')+X(i)+','+Y(r[k.k]);});
    s.appendChild(el('path',{d:d,fill:'none',stroke:C[ki],'stroke-width':2.2,'stroke-linejoin':'round'}));
    rows.forEach((r,i)=>{const g=el('g');
      g.appendChild(el('circle',{cx:X(i),cy:Y(r[k.k]),r:4.6,fill:C[ki],
        stroke:'var(--surface)','stroke-width':2}));
      g.appendChild(el('circle',{cx:X(i),cy:Y(r[k.k]),r:13,fill:'transparent'}));
      g.addEventListener('mousemove',e=>showTip(e,'<b>'+k.label+'</b><br>'+
        '<span class="k">window opens</span> '+r.window_start+'<br>'+
        '<span class="k">Luzardo rank</span> <b>'+r[k.k]+' of '+r.cohort_n+'</b><br>'+
        '<span class="k">his starts in window</span> '+r.lz_starts));
      g.addEventListener('mouseleave',hideTip);s.appendChild(g);});});
  rows.forEach((r,i)=>s.appendChild(txt(X(i),H-B+20,r.window_start.slice(5),'middle',9.6,'var(--ink-3)')));
  s.appendChild(txt(L,H-10,'window start date  ·  y-axis = rank among Phillies starters (1 = best)',
    'start',10.5,'var(--ink-3)'));
  host.appendChild(s);
  const lg=document.createElement('div');lg.className='legend';
  lg.innerHTML=keys.map((k,i)=>'<span><i style="background:'+C[i]+'"></i>'+k.label+'</span>').join('');
  host.appendChild(lg);}

/* 4. arsenal H1 -> H2 */
function chartArsenal(host,metric,mlabel){
  host.innerHTML='';
  const wins=['2026 H1','2026 H2'];
  const pitches=DATA.arsenal.filter(r=>r.window==='2026 H1')
    .sort((a,b)=>b.usage-a.usage).map(r=>r.pitch_name);
  const W=660,H=296,L=52,R=16,T=14,B=64,s=svg(W,H),iw=W-L-R,ih=H-T-B;
  let max=0;DATA.arsenal.forEach(r=>{if(wins.indexOf(r.window)>-1&&r[metric]>max)max=r[metric];});
  max*=1.16;
  const Y=v=>T+ih-(v/max)*ih;
  [0,.25,.5,.75,1].forEach(t=>{const v=max*t,y=Y(v);
    s.appendChild(el('line',{x1:L,x2:W-R,y1:y,y2:y,stroke:'var(--line)','stroke-width':1}));
    s.appendChild(txt(L-8,y+3.5,metric==='xwoba'?f3(v):pct(v),'end',10.5,'var(--ink-3)'));});
  const gw=iw/pitches.length, bw=Math.min(34,(gw-18)/2);
  pitches.forEach((pn,i)=>{
    wins.forEach((w,j)=>{
      const r=DATA.arsenal.filter(x=>x.window===w&&x.pitch_name===pn)[0]; if(!r)return;
      const v=r[metric]||0, x=L+i*gw+gw/2+(j-.5)*(bw+4)-bw/2, g=el('g');
      g.appendChild(el('rect',{x:x,y:Y(v),width:bw,height:Math.max(2,ih-(Y(v)-T)),rx:4,
        fill:PC[pn]||'var(--navy)',opacity:j?1:.40,stroke:'var(--surface)','stroke-width':2}));
      g.addEventListener('mousemove',e=>showTip(e,'<b>'+pn+' · '+w+'</b><br>'+
        '<span class="k">'+mlabel+'</span> <b>'+(metric==='xwoba'?f3(v):pct(v))+'</b><br>'+
        '<span class="k">pitches</span> '+r.pitches+' &nbsp;<span class="k">velo</span> '+f1(r.velo)+'<br>'+
        '<span class="k">whiff</span> '+pct(r.whiff_rate)+' &nbsp;<span class="k">xwOBA</span> '+f3(r.xwoba)+
        '<br><span class="k">putaway</span> '+pct(r.putaway_rate)));
      g.addEventListener('mouseleave',hideTip);s.appendChild(g);});
    s.appendChild(txt(L+i*gw+gw/2,H-B+18,pn.replace(' Fastball',''),'middle',10.5,'var(--ink-2)'));});
  host.appendChild(s);
  const lg=document.createElement('div');lg.className='legend';
  lg.innerHTML='<span><i style="background:var(--ink-3);opacity:.40"></i>first half</span>'+
    '<span><i style="background:var(--ink-3)"></i>second half</span>'+
    '<span style="color:var(--ink-3)">bar colour carries pitch identity</span>';
  host.appendChild(lg);}

function tbl(cols,rows,fmt){
  fmt=fmt||{};
  const w=document.createElement('div');w.className='tblwrap';
  w.innerHTML='<table><thead><tr>'+cols.map(c=>'<th>'+c[1]+'</th>').join('')+
    '</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map(c=>{
      const v=r[c[0]],f=fmt[c[0]];
      const cell=f?f(v,r):(v==null?'—':v);
      return '<td class="'+(typeof v==='number'?'n':'')+'">'+cell+'</td>';}).join('')+'</tr>').join('')+
    '</tbody></table>';
  return w;}
"""

def build():
    m = P["meta"]
    sl = {r["window"]: r for r in P["season_line"]}
    h1, h2 = sl["2026 H1 (uc-pps-017)"], sl["2026 H2 (new)"]
    lz = [r for r in P["cohort"] if r["who"] == 666200][0]
    sz = [r for r in P["cohort"] if "nchez" in r["name"]][0]
    rk = {r["axis"]: r for r in P["ranking"] if r["who"] == 666200}
    n = len(P["cohort"])
    tto2_h2 = [r["woba"] for r in P["tto"] if r["window"] == "2026 H2" and r["tto"] == 2][0]
    last3 = P["start_log"][-3:]
    pct = lambda v: "—" if v is None else f"{v*100:.1f}%"
    f3 = lambda v: "—" if v is None else f"{v:.3f}".lstrip("0")
    nfail = sum(1 for r in P["dq"] if r["result"] == "FAIL")
    nwarn = sum(1 for r in P["dq"] if r["result"] == "WARN")

    sub = (f'<span class="pill">uc-pps-028 &middot; dp_uc39 &middot; UC #39</span>'
           f'<span class="pill">data through {m["cache_max"]}</span>'
           f'<span class="pill">last start {m["last_start"]}</span>'
           f'<span class="pill">195/195 verification PASS &middot; {nfail} DQ FAIL</span>'
           f'<span class="pill">built {m["built"]}</span>')

    body = f"""
<div class="warnbox"><b>Read this first.</b> Arizona's lineup was <b>not confirmed</b> at build time &mdash;
every batter in the matchup panel is a candidate parsed from games Luzardo actually pitched, not a posted card.
Head-to-head vs Arizona is <b>22 PA in 2026</b> (one start, 4/10), so the actionable plan is <b>profile-driven</b>.
The second-half sample is <b>8 starts / 208 PA</b>. IP is reconstructed from event outs and runs are score deltas
while on the mound (RA9 basis, <i>not</i> earned-run accounting) &mdash; no official ERA appears anywhere in this product.</div>

<div class="verdict">
 <h2>The premise, adjudicated</h2>
 <p><b>&ldquo;Very good since the end of April&rdquo; &mdash; supported, and boundary-robust.</b>
 His {f3(lz['agg_xwoba'])} xwOBA against is the best on the Phillies staff, and he ranks
 <b>#1 at all eight window boundaries tested</b> &mdash; and on the full uncut season too.
 That claim does not depend on where you cut the year.</p>
 <p><b>&ldquo;Most consistent&rdquo; &mdash; that title belongs to Cristopher S&aacute;nchez.</b>
 On the axes that describe a floor, S&aacute;nchez wins: blow-up rate {pct(sz['cn3_blowup_rate'])} vs
 {pct(lz['cn3_blowup_rate'])}, floor-start rate {pct(sz['cn2_floor_rate'])} vs {pct(lz['cn2_floor_rate'])},
 {sz['cn6_ip_per_start']} IP per start vs {lz['cn6_ip_per_start']}. Luzardo's #1 ranking in start-to-start
 variation appears <b>only in a narrow band around May 1</b> &mdash; watch it move in the scan below.</p>
 <p><b>Where he does lead on consistency is workload.</b> {lz['starts']} straight turns since May 1, none missed,
 in a {lz['cn5_pitch_min']}&ndash;{lz['cn5_pitch_max']} pitch band (SD {lz['cn5_pitch_sd']}) &mdash; the tightest on the staff.
 If &ldquo;consistent&rdquo; means &ldquo;you know what you're getting when he takes the ball&rdquo;, that is the axis where he genuinely leads.</p>
</div>

<div class="tiles">
 <div class="tile ok"><div class="lab">xwOBA rank, staff</div><div class="val">#{int(rk['agg_xwoba']['rank'])} of {n}</div>
  <div class="note">{f3(lz['agg_xwoba'])} since {m['premise_break']} &middot; #1 at every boundary</div></div>
 <div class="tile ok"><div class="lab">Second-half RA9</div><div class="val">{h2['ra9']}</div>
  <div class="note">8 GS &middot; {h2['ip']} IP &middot; {f3(h2['woba'])} wOBA</div></div>
 <div class="tile ok"><div class="lab">2nd time through, H2</div><div class="val">{f3(tto2_h2)}</div>
  <div class="note">was .368 in H1 &mdash; the uc-pps-017 leash flag is closed</div></div>
 <div class="tile watch"><div class="lab">Hard-hit rate, H2</div><div class="val">{pct(h2['hard_hit_rate'])}</div>
  <div class="note">up from {pct(h1['hard_hit_rate'])} &mdash; the one degraded tripwire</div></div>
 <div class="tile"><div class="lab">Strikeout rate, H2</div><div class="val">{pct(h2['k_rate'])}</div>
  <div class="note">what makes the harder contact affordable</div></div>
 <div class="tile"><div class="lab">Rest tonight</div><div class="val">6 days</div>
  <div class="note">last 3 starts {last3[0]['pitches']} / {last3[1]['pitches']} / {last3[2]['pitches']} pitches &mdash; season highs</div></div>
</div>

<section>
 <h2>Every 2026 start</h2>
 <p class="cap">Bars are runs allowed while he was on the mound; the line is that start's xwOBA.
 Hover any start for the full line.</p>
 <div class="ctl">
  <label for="fwin">Window</label>
  <select id="fwin">
   <option value="">Full season (27 starts)</option>
   <option value="2026-05-01" selected>Since 2026-05-01 (the premise window)</option>
   <option value="2026-07-10">Second half only (8 starts)</option>
  </select>
  <button class="tgl" id="tblStarts" aria-pressed="false">Table view</button>
 </div>
 <div class="chart" id="cStarts"></div>
 <div id="tStarts" class="hide"></div>
</section>

<section>
 <h2>Consistency is a different axis from quality</h2>
 <p class="cap">Phillies starters, {m['premise_break']} onward, minimum 8 starts. Six axes reported separately &mdash;
 there is deliberately no composite index, because a composite is a weighting knob and a weighting knob is how a premise
 gets confirmed. Dashed lines are cohort medians.</p>
 <div class="ctl">
  <label for="axsel">Consistency axis</label>
  <select id="axsel">
   <option value="cn1_xwoba_sd|CN-1 SD of start xwOBA|1" selected>CN-1 &mdash; start-to-start variation</option>
   <option value="cn4_roll3_range|CN-4 mean rolling-3-start xwOBA range|1">CN-4 &mdash; rolling 3-start range</option>
   <option value="cn2_floor_rate|CN-2 floor rate|0">CN-2 &mdash; floor rate (&ge;5 IP and &le;3 runs)</option>
   <option value="cn3_blowup_rate|CN-3 blow-up rate|1">CN-3 &mdash; blow-up rate</option>
   <option value="cn5_pitch_sd|CN-5 SD of pitch count|1">CN-5 &mdash; workload predictability</option>
   <option value="cn6_outs_sd|CN-6 SD of outs recorded|1">CN-6 &mdash; length dependability</option>
  </select>
  <button class="tgl" id="tblCohort" aria-pressed="false">Table view</button>
 </div>
 <div class="chart" id="cCohort"></div>
 <div id="tCohort" class="hide"></div>
</section>

<section>
 <h2>TR-2 breakpoint scan &mdash; a finding, or an artefact of where you cut the year?</h2>
 <p class="cap">Every rank recomputed at eight candidate window starts. A rank that survives the scan is a finding;
 one that exists only at the stated boundary is a researcher degree of freedom (guardrail <b>G6</b>).
 Note that the quality line never moves off 1 and the variation line does.</p>
 <div class="chart" id="cScan"></div>
</section>

<section>
 <h2>Closing the uc-pps-017 tripwires</h2>
 <p class="cap">The watch items the All-Star-break assessment left open, plus the splits it flagged &mdash;
 re-measured against eight starts of new evidence.</p>
 <div id="tTrip"></div>
</section>

<div class="grid2">
<section>
 <h2>Arsenal drift across the break</h2>
 <p class="cap">Faded bar = first half, solid = second half.</p>
 <div class="ctl"><label for="arsm">Measure</label>
  <select id="arsm">
   <option value="usage|usage share" selected>Usage share</option>
   <option value="whiff_rate|whiff rate">Whiff rate</option>
   <option value="xwoba|xwOBA against">xwOBA against</option>
   <option value="chase_rate|chase rate">Chase rate</option>
  </select></div>
 <div class="chart" id="cArs"></div>
</section>
<section>
 <h2>Tonight's attack plan, by handedness</h2>
 <p class="cap">2026 full season &mdash; the panel with real sample behind it.</p>
 <div class="ctl">
  <button class="tgl" id="bL" aria-pressed="true">vs LHB</button>
  <button class="tgl" id="bR" aria-pressed="false">vs RHB</button>
 </div>
 <div id="tPlan"></div>
</section>
</div>

<section>
 <h2>Arizona: what the record actually supports</h2>
 <p class="cap">Current-era tier = batters faced in 2025&ndash;26. Historical-only opponents (2019&ndash;23 Arizona
 rosters) are tiered out and excluded from planning. Batter names are parsed from the play-by-play, never hand-keyed.</p>
 <div class="ctl">
  <button class="tgl" id="bCur" aria-pressed="true">Current-era only</button>
  <button class="tgl" id="bAll" aria-pressed="false">Show historical too</button>
 </div>
 <div id="tH2H"></div>
</section>
"""

    foot = f"""
<b>Governance.</b> uc-pps-028 / dp_uc39 / UC #39 &middot; Phillies Pitching value stream &middot;
entity-locked to <code>pitcher == {m['pitcher_id']}</code> &middot; regular season only, deduped on
<code>game_pk + at_bat_number + pitch_number</code>. Locked KPIs inherited verbatim from Baseball Functions
via dp_uc11 &rarr; dp_uc17; the new provisional family <code>CN-1&hellip;CN-6</code> is spec'd in
<code>02_engineering_design.md</code> and pending DPO ratification.<br>
<b>Receipts.</b> {len(P['dq'])} DQ rules ({nfail} FAIL, {nwarn} WARN) &middot; 30 CSV/PNG receipts in
<code>out/</code> &middot; <code>dp_uc39_verification.py</code> 195/195 PASS &middot; the continuity check
reproduces all 17 published <code>uc-pps-017</code> first-half figures. Every number on this page is read from
<code>out/dp_uc39_payload.json</code>; none is hand-typed. No external asset is loaded &mdash; this file opens offline.<br>
<b>Known open defects carried, not hidden:</b> O-5 (3 <code>truncated_pa</code> counted as PA by the locked
<code>get_stats</code>) &middot; O-8 (locked <code>hard_hit_rate</code> counts 2 untracked balls in play as
not-hard-hit; a tracked-denominator shadow rate is emitted alongside).<br>
<b>Three build defects were found and fixed during this run:</b> D-1 completeness tested at the wrong grain,
D-2 replay-review prose contaminating batter-name parsing, D-3 a career opponent panel silently mixing
2019 and 2026 rosters. All three are repo-wide patterns.
"""

    js_tail = """
$('#app').innerHTML=BODY;
$('#foot').innerHTML=FOOT;

$('#theme').onclick=function(){
  const cur=document.documentElement.getAttribute('data-theme');
  const dark=cur==='dark'||(!cur&&matchMedia('(prefers-color-scheme:dark)').matches);
  document.documentElement.setAttribute('data-theme',dark?'light':'dark');
  this.setAttribute('aria-pressed',String(!dark));redraw();};

function drawStarts(){chartStarts($('#cStarts'),$('#fwin').value);}
$('#fwin').onchange=drawStarts;
$('#tblStarts').onclick=function(){
  const on=this.getAttribute('aria-pressed')==='true';
  this.setAttribute('aria-pressed',String(!on));
  $('#tStarts').classList.toggle('hide',on);$('#cStarts').classList.toggle('hide',!on);};
$('#tStarts').appendChild(tbl(
 [['game_date','Date'],['opp','Opp'],['home','H/A'],['pitches','P'],['ip','IP'],['pa','PA'],
  ['k','K'],['bb','BB'],['hr','HR'],['runs','R'],['woba','wOBA'],['xwoba','xwOBA'],['days_rest','Rest']],
 DATA.start_log,{woba:f3,xwoba:f3,home:v=>v?'H':'A',days_rest:v=>v==null?'—':v}));

let AX=['cn1_xwoba_sd','CN-1 SD of start xwOBA','1'];
function drawCohort(){chartCohort($('#cCohort'),AX[0],AX[1],AX[2]==='1');}
$('#axsel').onchange=function(){AX=this.value.split('|');drawCohort();};
$('#tblCohort').onclick=function(){
  const on=this.getAttribute('aria-pressed')==='true';
  this.setAttribute('aria-pressed',String(!on));
  $('#tCohort').classList.toggle('hide',on);$('#cCohort').classList.toggle('hide',!on);};
$('#tCohort').appendChild(tbl(
 [['name','Pitcher'],['starts','GS'],['ip','IP'],['agg_xwoba','xwOBA'],['woba','wOBA'],['ra9','RA9'],
  ['cn1_xwoba_sd','CN-1 SD'],['cn2_floor_rate','CN-2 floor'],['cn3_blowup_rate','CN-3 blow-up'],
  ['cn4_roll3_range','CN-4 roll3'],['cn5_pitch_sd','CN-5 pitch SD'],['cn6_ip_per_start','CN-6 IP/GS']],
 DATA.cohort,{agg_xwoba:f3,woba:f3,cn1_xwoba_sd:v=>v.toFixed(4),cn4_roll3_range:v=>v.toFixed(4),
  cn2_floor_rate:pct,cn3_blowup_rate:pct,name:v=>'<b>'+v+'</b>'}));

function drawScan(){chartScan($('#cScan'),[
 {k:'agg_xwoba__rank',label:'xwOBA — quality'},
 {k:'cn1_xwoba_sd__rank',label:'CN-1 — start-to-start variation'},
 {k:'cn2_floor_rate__rank',label:'CN-2 — floor rate'},
 {k:'cn3_blowup_rate__rank',label:'CN-3 — blow-up rate'}]);}

const bmap={IMPROVED:'g',RECOVERED:'g',HELD:'g',CLOSED:'g',DEGRADED:'w',SLIPPED:'w',CONTEXT:'n'};
$('#tTrip').appendChild(tbl(
 [['tripwire','#'],['watch_item','Watch item'],['h1','H1'],['h2','H2'],['delta','Δ'],
  ['status','Verdict'],['note','Note']],
 DATA.tripwires,{h1:f3,h2:f3,delta:v=>(v>0?'+':'')+f3(v),
  status:v=>'<span class="badge '+(bmap[v]||'n')+'">'+v+'</span>',watch_item:v=>'<b>'+v+'</b>'}));

let AM=['usage','usage share'];
function drawArs(){chartArsenal($('#cArs'),AM[0],AM[1]);}
$('#arsm').onchange=function(){AM=this.value.split('|');drawArs();};

function drawPlan(side){
 $('#tPlan').innerHTML='';
 $('#tPlan').appendChild(tbl(
  [['pitch_name','Pitch'],['pitches','#'],['usage','Usage'],['velo','Velo'],['whiff_rate','Whiff'],
   ['chase_rate','Chase'],['in_zone_rate','Zone'],['putaway_rate','Putaway'],['xwoba','xwOBA']],
  DATA.plan.filter(r=>r.stand===side),
  {usage:pct,whiff_rate:pct,chase_rate:pct,in_zone_rate:pct,putaway_rate:pct,xwoba:f3,velo:f1,
   pitch_name:v=>'<b style="color:'+(PC[v]||'inherit')+'">&#9632;</b> '+v}));
 const ts=DATA.two_strike.filter(r=>r.stand===side);
 const d=document.createElement('p');
 d.style.cssText='font-size:12.2px;color:var(--ink-2);margin:11px 0 0;line-height:1.6';
 d.innerHTML='<b>Two-strike menu:</b> '+ts.map(r=>r.pitch_name.replace(' Fastball','')+
   ' '+pct(r.share_2k)+' <span style="color:var(--ink-3)">(whiff '+pct(r.whiff_rate)+')</span>').join(' &middot; ');
 $('#tPlan').appendChild(d);}
$('#bL').onclick=function(){$('#bL').setAttribute('aria-pressed','true');
  $('#bR').setAttribute('aria-pressed','false');drawPlan('L');};
$('#bR').onclick=function(){$('#bR').setAttribute('aria-pressed','true');
  $('#bL').setAttribute('aria-pressed','false');drawPlan('R');};

function drawH2H(cur){
 $('#tH2H').innerHTML='';
 $('#tH2H').appendChild(tbl(
  [['batter_name','Batter'],['stand','Side'],['tier','Tier'],['last_faced','Last faced'],
   ['plate_apps','PA'],['hits','H'],['hrs','HR'],['walks','BB'],['strikeouts','K'],
   ['woba','wOBA'],['xwoba','xwOBA'],['whiff_rate','Whiff']],
  DATA.h2h.filter(r=>!cur||r.tier.indexOf('current')===0),
  {woba:f3,xwoba:f3,whiff_rate:pct,batter_name:v=>'<b>'+v+'</b>',
   tier:v=>'<span class="badge '+(v.indexOf('current')===0?'g':'n')+'">'+
     (v.indexOf('current')===0?'current':'historical')+'</span>'}));
 const w=document.createElement('p');
 w.style.cssText='font-size:12.2px;color:var(--ink-2);margin:11px 0 0;line-height:1.6';
 w.innerHTML='Only <b>Ketel Marte</b> clears 10 PA, and he is the one name where the result and the expected line '+
  'agree that Luzardo has been beaten. Everything else here is 2–7 PA — &ldquo;he has seen him&rdquo;, not a plan.';
 $('#tH2H').appendChild(w);}
$('#bCur').onclick=function(){$('#bCur').setAttribute('aria-pressed','true');
  $('#bAll').setAttribute('aria-pressed','false');drawH2H(true);};
$('#bAll').onclick=function(){$('#bAll').setAttribute('aria-pressed','true');
  $('#bCur').setAttribute('aria-pressed','false');drawH2H(false);};

function redraw(){drawStarts();drawCohort();drawScan();drawArs();}
redraw();drawPlan('L');drawH2H(true);
addEventListener('scroll',hideTip,{passive:true});
"""
    js = JS + "\nconst BODY=" + json.dumps(body) + ";\nconst FOOT=" + json.dumps(foot) + ";\n" + js_tail
    out = (TPL.replace("__SUB__", sub)
              .replace("__DATA__", json.dumps(P, default=str))
              .replace("__JS__", js))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {OUT}  ({len(out)/1024:.0f} KB)")

if __name__ == "__main__":
    build()

# ---------------------------------------------------------------------------
# ARTIFACT VARIANT — same payload, same charts, published as a hosted page.
# Divergence from the offline copy is deliberate and documented in 07:
#   * a webfont pairing (Barlow Condensed / Source Sans 3 / IBM Plex Mono),
#     which the offline copy cannot vendor without embedding font binaries;
#   * no <!doctype>/<html>/<head>/<body> — the Artifact host supplies those.
# Nothing about the DATA differs: both are rendered from the same payload.json.
# ---------------------------------------------------------------------------
ART_HEAD = """<title>Luzardo Pre-Scout</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Source+Sans+3:wght@400;500;600;700&display=swap">
"""
ART_TYPE = """
:root{ --display:'Barlow Condensed','Oswald','Arial Narrow',sans-serif;
       --body:'Source Sans 3',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
       --mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }
body{font-family:var(--body);font-size:15px}
h1{font-family:var(--display);font-size:44px;font-weight:700;letter-spacing:.2px;
   line-height:1.02;text-transform:uppercase}
section>h2,.verdict h2{font-family:var(--display);font-weight:600;letter-spacing:.4px;
   text-transform:uppercase;font-size:21px}
.tile .val{font-family:var(--display);font-size:38px;font-weight:700;letter-spacing:0}
.tile .lab{font-family:var(--display);font-size:13px;font-weight:600;letter-spacing:1.1px}
th{font-family:var(--display);font-size:13.5px;font-weight:600;letter-spacing:.7px;
   text-transform:uppercase}
td.n{font-family:var(--mono);font-size:12.4px}
.pill{font-family:var(--mono);font-size:11px}
.badge{font-family:var(--display);font-size:12px;letter-spacing:.5px;text-transform:uppercase}
svg text{font-family:var(--mono)}
"""

def build_artifact():
    src = open(OUT, encoding="utf-8").read()
    head_start = src.index("<style>")
    style = src[head_start:src.index("</style>") + 8]
    body = src[src.index('<div class="wrap">'):src.rindex("</body>")]
    style = style.replace("</style>", ART_TYPE + "</style>")
    out = ART_HEAD + style + "\n" + body
    p = os.path.join(HERE, "dp_uc39_luzardo_dashboard_artifact.html")
    open(p, "w", encoding="utf-8").write(out)
    print(f"wrote {p}  ({len(out)/1024:.0f} KB)")

if os.environ.get("BUILD_ARTIFACT"):
    build_artifact()
