const D = window.__UC45__;
const COLS = D.pitches.cols, IDX = Object.fromEntries(COLS.map((c,i)=>[c,i]));
const P = D.pitches.rows.map(r => Object.fromEntries(COLS.map((c,i)=>[c,r[i]])));
const REG = {heart:'#002D72', edge_in:'#284898', edge_out:'#F2A33A', beyond:'#E81828'};
const REGLAB = {heart:'heart', edge_in:'edge in', edge_out:'edge out', beyond:'beyond (missed the shadow)'};
const HALF_X = D.meta.plate_half, BALL = D.meta.ball_ft;
const WINS = {'2025':r=>r.game_year===2025, '2026 1H':r=>r.game_year===2026&&r.half==='1H',
              '2026 2H':r=>r.game_year===2026&&r.half==='2H', '2026':r=>r.game_year===2026,
              '2025 1H':r=>r.game_year===2025&&r.half==='1H', '2025 2H':r=>r.game_year===2025&&r.half==='2H'};
let S = {win:'2026 2H', cmp:'2026 1H', stand:'both', pitch:'all', mapMode:'all', trend:'beyond_shadow_chase_rate'};
const $ = s => document.querySelector(s);
const f3 = v => (v==null||!isFinite(v)) ? '—' : v.toFixed(3).replace(/^(-?)0\./,'$1.');
const tip = $('#tip');
function showTip(e, html){ tip.innerHTML = html; tip.style.opacity = 1;
  tip.style.left = Math.min(e.clientX+12, innerWidth-270)+'px'; tip.style.top = (e.clientY+12)+'px'; }
function hideTip(){ tip.style.opacity = 0; }

function seg(el, opts, key, after){
  el.innerHTML='';
  opts.forEach(([v,l])=>{ const b=document.createElement('button'); b.className='seg'; b.textContent=l;
    b.setAttribute('aria-pressed', S[key]===v); b.onclick=()=>{S[key]=v; seg(el,opts,key,after); after();}; el.appendChild(b); });
}
function filt(win){
  return P.filter(r => WINS[win](r) && (S.stand==='both'||r.stand===S.stand) && (S.pitch==='all'||r.pitch_name===S.pitch));
}
function kpis(rows){
  const n=rows.length, cnt=k=>rows.filter(r=>r.region===k).length;
  const beyond=rows.filter(r=>r.region==='beyond'), eout=rows.filter(r=>r.region==='edge_out');
  const ooz=rows.filter(r=>!r.in_zone_attr), pa=rows.filter(r=>r.pa_end).length;
  return { n, pa,
    bbrate: pa? rows.filter(r=>r.walk).length/pa : NaN,
    in_zone: n? rows.filter(r=>r.in_zone_attr).length/n : NaN,
    chase: ooz.length? ooz.filter(r=>r.is_swing).length/ooz.length : NaN,
    ahead: n? rows.filter(r=>r.balls<r.strikes).length/n : NaN,
    edge: n? (cnt('edge_in')+cnt('edge_out'))/n : NaN,
    miss: n? beyond.length/n : NaN,
    bch: beyond.length? beyond.filter(r=>r.is_swing).length/beyond.length : NaN,
    n_beyond: beyond.length,
    eoch: eout.length? eout.filter(r=>r.is_swing).length/eout.length : NaN,
    whiff: (()=>{const sw=rows.filter(r=>r.is_swing); return sw.length? sw.filter(r=>r.whiff).length/sw.length:NaN;})(),
    reg: Object.fromEntries(Object.keys(REG).map(k=>[k, n? cnt(k)/n : NaN])) };
}
function tiles(){
  const a=kpis(filt(S.win)), b=kpis(filt(S.cmp));
  const T=[['Pitches','n',null,'',v=>v.toLocaleString()],['PA','pa',null,'',v=>v.toLocaleString()],
    ['Walk rate','bbrate',+1,'gov'],['In-zone','in_zone',-1,'gov'],['Chase','chase',-1,'gov'],
    ['Pitches ahead','ahead',-1,'gov'],['Edge Rate','edge',0,'gov'],['Shadow miss','miss',+1,'new'],
    ['Chase beyond shadow','bch',-1,'new'],['Whiff','whiff',-1,'gov']];
  $('#tiles').innerHTML = T.map(([k,f,bad,cls,fm])=>{
    const va=a[f], vb=b[f], fmt=fm||f3; let d='';
    if(bad!==null && isFinite(va)&&isFinite(vb)){ const dl=va-vb; const c = bad===0?'nt':(dl*bad>0.0005?'up':(dl*bad<-0.0005?'dn':'nt'));
      d=`<b class="${c}">${dl>=0?'+':''}${f3(dl)}</b> vs ${S.cmp} (${f3(vb)})`; }
    else if(bad===null) d=`${S.cmp}: ${fmt(vb)}`;
    return `<div class="tile ${cls}"><div class="k">${k}</div><div class="v">${fmt(va)}</div><div class="d">${d}</div></div>`;
  }).join('');
}
function median(a){ if(!a.length) return NaN; const s=[...a].sort((x,y)=>x-y), m=s.length>>1; return s.length%2? s[m] : (s[m-1]+s[m])/2; }
function map(){
  let rows = filt(S.win);
  const top=median(rows.map(r=>r.sz_top)), bot=median(rows.map(r=>r.sz_bot));
  const k=kpis(rows);
  if(S.mapMode==='misses') rows=rows.filter(r=>r.region==='beyond');
  if(S.mapMode==='chased') rows=rows.filter(r=>r.region==='beyond'&&r.is_swing);
  $('#mapLegend').innerHTML = Object.keys(REG).map(g=>`<span><i style="background:${REG[g]}"></i>${REGLAB[g]} ${f3(k.reg[g])}</span>`).join('');
  const W=520,H=470, X0=-2.6,X1=2.6,Y0=-0.3,Y1=4.9, sx=v=>(v-X0)/(X1-X0)*W, sy=v=>H-(v-Y0)/(Y1-Y0)*H;
  const r = BALL/(X1-X0)*W;
  let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Pitch locations coloured by shadow region">`;
  s+=`<rect x="0" y="0" width="${W}" height="${H}" fill="#fbfbfd"/>`;
  rows.forEach((p,i)=>{ const z = bot + (p.plate_z - p.sz_bot);
    s+=`<circle data-i="${i}" cx="${sx(p.plate_x).toFixed(1)}" cy="${sy(z).toFixed(1)}" r="${S.mapMode==='all'?2.6:3.6}" fill="${REG[p.region]}" fill-opacity="${S.mapMode==='all'?0.45:0.75}"/>`; });
  if(isFinite(top)){
    s+=`<rect x="${sx(-HALF_X-BALL)}" y="${sy(top+BALL)}" width="${sx(HALF_X+BALL)-sx(-HALF_X-BALL)}" height="${sy(bot-BALL)-sy(top+BALL)}" rx="${r}" fill="none" stroke="#E81828" stroke-width="1.6" stroke-dasharray="6 4"/>`;
    s+=`<rect x="${sx(-HALF_X)}" y="${sy(top)}" width="${sx(HALF_X)-sx(-HALF_X)}" height="${sy(bot)-sy(top)}" fill="none" stroke="#111" stroke-width="1.6"/>`;
  }
  s+=`<text x="8" y="18" font-size="13" fill="#002D72" font-weight="700">${S.win} · ${rows.length.toLocaleString()} pitches shown · missed the shadow ${f3(k.miss)}</text>`;
  s+=`<text x="${W-8}" y="${H-8}" font-size="11" fill="#777" text-anchor="end">1B side / arm side →</text></svg>`;
  $('#map').innerHTML=s;
  $('#map').querySelectorAll('circle').forEach(c=>{ c.addEventListener('mousemove',e=>{ const p=rows[+c.dataset.i];
    showTip(e,`${p.game_date} · ${p.pitch_name} vs ${p.stand}HB<br>${p.balls}-${p.strikes} · ${REGLAB[p.region]}<br>${p.is_swing?(p.whiff?'swing & miss':'swung'):'taken'}`); });
    c.addEventListener('mouseleave',hideTip); });
}
function bars(){
  const wins=['2025 1H','2025 2H','2026 1H','2026 2H'];
  const vals=wins.map(w=>kpis(filt(w)));
  const lg=wins.map(w=>{ const [y,h]=w.split(' '); const r=D.league.find(x=>x.population==='all pitchers in PHI games'&&x.game_year==+y&&x.half===h); return r? r.beyond_shadow_chase_rate:NaN; });
  const W=520,H=210,pad=34, bw=70, mx=0.5, sy=v=>H-24-(v/mx)*(H-50);
  let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Chase beyond the shadow by window">`;
  [0,.1,.2,.3,.4,.5].forEach(t=>{ s+=`<line x1="${pad}" x2="${W-6}" y1="${sy(t)}" y2="${sy(t)}" stroke="#eceff3"/><text x="${pad-6}" y="${sy(t)+4}" font-size="10" fill="#777" text-anchor="end">${f3(t)}</text>`; });
  wins.forEach((w,i)=>{ const x=pad+20+i*((W-pad-40)/4), v=vals[i].bch, c=w.startsWith('2026')?'#E81828':'#002D72';
    if(isFinite(v)) s+=`<rect x="${x}" y="${sy(v)}" width="${bw}" height="${sy(0)-sy(v)}" fill="${c}" rx="2"><title>${w}: ${f3(v)} on ${vals[i].n_beyond} pitches</title></rect>`;
    s+=`<text x="${x+bw/2}" y="${sy(isFinite(v)?v:0)-14}" font-size="11.5" text-anchor="middle" font-weight="700">${f3(v)}</text>`;
    s+=`<text x="${x+bw/2}" y="${sy(isFinite(v)?v:0)-3}" font-size="9.5" text-anchor="middle" fill="#666">n=${vals[i].n_beyond}</text>`;
    if(isFinite(lg[i])) s+=`<line x1="${x-6}" x2="${x+bw+6}" y1="${sy(lg[i])}" y2="${sy(lg[i])}" stroke="#555" stroke-width="2.4"><title>league ${f3(lg[i])}</title></line>`;
    s+=`<text x="${x+bw/2}" y="${H-8}" font-size="11.5" text-anchor="middle">${w}</text>`; });
  s+='</svg>'; $('#bars').innerHTML=s;
}
const TREND = {beyond_shadow_chase_rate:'Chase beyond the shadow (SZ-3)', shadow_miss_rate:'Shadow miss rate (SZ-2)',
  edge_rate:'Edge Rate (governed)', in_zone_rate:'In-zone rate', chase_rate:'Chase rate', bbrate:'Walk rate', pitch_share_ahead:'Pitches thrown ahead (CL-1)'};
function trend(){
  const sel=$('#trendSel'); if(!sel.options.length){ Object.entries(TREND).forEach(([k,l])=>{ const o=document.createElement('option'); o.value=k;o.textContent=l; sel.appendChild(o); }); sel.onchange=()=>{S.trend=sel.value; trend();}; }
  const m=D.month, W=520,H=190,pad=38, xs=i=>pad+i*((W-pad-16)/(m.length-1));
  const v=m.map(r=>r[S.trend]); const s25=D.season.find(r=>r.season==='2025')[S.trend];
  const lo=Math.min(...v,s25)-0.02, hi=Math.max(...v,s25)+0.02, sy=x=>H-22-(x-lo)/(hi-lo)*(H-40);
  const mn=['','','','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct'];
  let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${TREND[S.trend]} by month">`;
  s+=`<line x1="${pad}" x2="${W-10}" y1="${sy(s25)}" y2="${sy(s25)}" stroke="#8C8C8C" stroke-dasharray="5 4"/><text x="${W-10}" y="${sy(s25)-4}" font-size="10" fill="#666" text-anchor="end">2025 season ${f3(s25)}</text>`;
  s+=`<polyline fill="none" stroke="#E81828" stroke-width="2.4" points="${v.map((y,i)=>xs(i)+','+sy(y)).join(' ')}"/>`;
  m.forEach((r,i)=>{ s+=`<circle cx="${xs(i)}" cy="${sy(v[i])}" r="4" fill="#E81828"><title>${mn[r.month]}: ${f3(v[i])} (${r.pitches} pitches)</title></circle><text x="${xs(i)}" y="${sy(v[i])-8}" font-size="10.5" text-anchor="middle">${f3(v[i])}</text><text x="${xs(i)}" y="${H-6}" font-size="11" text-anchor="middle">${mn[r.month]}</text>`; });
  s+='</svg>'; $('#trend').innerHTML=s;
}
function premTbl(){
  const cls=v=>/^SUPPORTED/.test(v)?'s':/^CONTRADICTED/.test(v)?'c':'f';
  $('#premTbl').innerHTML='<tr><th>#</th><th>Claim</th><th>Window</th><th>Metric</th><th>Before</th><th>After</th><th>Δ</th><th>p</th><th>League Δ</th><th>Verdict</th></tr>'+
    D.premises.map(r=>`<tr><td>${r.premise}</td><td>${r.claim}</td><td>${r.window}</td><td><code>${r.metric}</code></td><td>${f3(r.v_before)}</td><td>${f3(r.v_after)}</td><td>${f3(r.delta)}</td><td>${r.p==null?'—':r.p.toFixed(3)}</td><td>${f3(r.league_delta)}</td><td class="vd ${cls(r.verdict)}">${r.verdict}</td></tr>`).join('');
}
function startTbl(){
  $('#startTbl').innerHTML='<tr><th>Date</th><th>Opp</th><th>Half</th><th>Pitches</th><th>PA</th><th>BB</th><th>K</th><th>In-zone</th><th>Edge</th><th>Shadow miss</th><th>Chase beyond</th><th>Ahead</th><th>xwOBA</th></tr>'+
    D.starts.map(r=>`<tr><td>${r.game_date}</td><td>${r.opponent}</td><td>${r.half}</td><td>${r.pitches}</td><td>${r.plate_apps}</td><td>${r.walks}</td><td>${r.strikeouts}</td><td>${f3(r.in_zone_rate)}</td><td>${f3(r.edge_rate)}</td><td style="color:${r.shadow_miss_rate>=0.45?'#E81828':'inherit'};font-weight:${r.shadow_miss_rate>=0.45?700:400}">${f3(r.shadow_miss_rate)}</td><td>${f3(r.beyond_shadow_chase_rate)}</td><td>${f3(r.pitch_share_ahead)}</td><td>${f3(r.xwoba)}</td></tr>`).join('');
}
function render(){ tiles(); map(); bars(); }
seg($('#winSeg'),[['2025','2025'],['2026 1H','2026 1H'],['2026 2H','2026 2H'],['2026','2026 full']],'win',render);
seg($('#cmpSeg'),[['2025','2025'],['2026 1H','2026 1H'],['2025 2H','2025 2H']],'cmp',render);
seg($('#standSeg'),[['both','Both'],['L','LHB'],['R','RHB']],'stand',render);
seg($('#pitchSeg'),[['all','All'],['Sinker','Sinker'],['Changeup','Changeup'],['Slider','Slider']],'pitch',render);
seg($('#mapTabs'),[['all','All pitches'],['misses','Missed the shadow'],['chased','Chased misses']],'mapMode',map);
$('#built').textContent = D.meta.built_utc + ' UTC';
render(); trend(); premTbl(); startTbl();
