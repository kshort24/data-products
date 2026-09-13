const D = window.__UC44__;
const PC = D.pitch_colors, SZ = D.zone;
let state = { window:'Post-Option', stand:'both', pitches:new Set(D.pitch_order), tab:'starts' };

const $ = s => document.querySelector(s);
const fmt3 = v => (v==null||isNaN(v)) ? '—' : v.toFixed(3).replace(/^0/,'');
const pct  = (v,d=1) => (v==null||isNaN(v)) ? '—' : (v*100).toFixed(d)+'%';
const gcol = g => g==null||isNaN(g) ? '#B9B9B9' : g>=60?'#1a7f37' : g>=55?'#5FA052' : g>=45?'#8A8A8A' : g>=40?'#D08C2E' : '#E81828';

// ---------- controls ----------
function buildControls(){
  const w = $('#winSeg');
  ['Pre-Option','Post-Option','Full 2026'].forEach(v=>{
    const b=document.createElement('button'); b.className='seg'; b.textContent=v;
    b.setAttribute('aria-pressed', v===state.window);
    b.onclick=()=>{ state.window=v; syncPitchChips(); render(); };
    w.appendChild(b);
  });
  const s = $('#standSeg');
  [['both','Both'],['L','vs LHH'],['R','vs RHH']].forEach(([v,l])=>{
    const b=document.createElement('button'); b.className='seg'; b.textContent=l;
    b.setAttribute('aria-pressed', v===state.stand);
    b.onclick=()=>{ state.stand=v; render(); }; s.appendChild(b);
  });
  syncPitchChips();
}
function syncPitchChips(){
  const holder = $('#pitchChips'); holder.innerHTML='';
  const present = new Set(D.locations.filter(r=>r.window===state.window).map(r=>r.pitch_type));
  state.pitches = new Set([...state.pitches].filter(p=>present.has(p)));
  if(state.pitches.size===0) state.pitches = new Set(present);
  D.pitch_order.filter(p=>present.has(p)).forEach(p=>{
    const b=document.createElement('button'); b.className='pchip';
    b.setAttribute('aria-pressed', state.pitches.has(p));
    b.innerHTML = `<span class="dot" style="background:${PC[p]||'#999'}"></span>${p}`;
    b.onclick=()=>{ state.pitches.has(p)?state.pitches.delete(p):state.pitches.add(p);
                    if(state.pitches.size===0) state.pitches.add(p); render(); };
    holder.appendChild(b);
  });
}

// ---------- pitch map ----------
const VX=[-2.05,2.05], VZ=[0.6,4.9], W=300, H=340;
const sx = x => (x-VX[0])/(VX[1]-VX[0])*W;
const sy = z => H - (z-VZ[0])/(VZ[1]-VZ[0])*H;

function drawMap(stand){
  const rows = D.locations.filter(r=>r.window===state.window && r.stand===stand && state.pitches.has(r.pitch_type));
  const cents = {};
  rows.forEach(r=>{ (cents[r.pitch_type] ??= {n:0,x:0,z:0}); const c=cents[r.pitch_type];
                    c.n++; c.x+=r.plate_x; c.z+=r.plate_z; });
  const total = rows.length;
  let svg = `<svg class="zone" viewBox="0 0 ${W} ${H}" role="img" aria-label="pitch locations vs ${stand}HH">`;
  svg += `<rect x="${sx(-0.83)}" y="${sy(SZ.top)}" width="${sx(0.83)-sx(-0.83)}" height="${sy(SZ.bot)-sy(SZ.top)}"
          fill="#FF5733" fill-opacity=".13" stroke="#111" stroke-width="1"/>`;
  rows.forEach(r=>{ svg += `<circle cx="${sx(r.plate_x).toFixed(1)}" cy="${sy(r.plate_z).toFixed(1)}" r="2.4"
          fill="${PC[r.pitch_type]||'#999'}" fill-opacity=".30"/>`; });
  const placed=[];
  Object.entries(cents).sort((a,b)=>b[1].n-a[1].n).forEach(([pt,c])=>{
    const u=c.n/total; if(u<0.02) return;
    let px=c.x/c.n, pz=c.z/c.n;
    placed.forEach(([qx,qz])=>{ if(Math.abs(px-qx)<0.20 && Math.abs(pz-qz)<0.20) px += px>=qx?0.26:-0.26; });
    placed.push([px,pz]);
    const r = 9 + 30*u;
    svg += `<g><title>${pt} · ${c.n} pitches · ${(u*100).toFixed(0)}% usage</title>
      <circle cx="${sx(px).toFixed(1)}" cy="${sy(pz).toFixed(1)}" r="${r.toFixed(1)}"
        fill="${PC[pt]||'#999'}" stroke="#111" stroke-width="1.3" fill-opacity=".93"/>
      <text x="${sx(px).toFixed(1)}" y="${(sy(pz)+3.4).toFixed(1)}" text-anchor="middle"
        font-size="10" font-weight="700" fill="#fff">${pt}</text></g>`;
  });
  svg += `</svg>`;
  return {svg, n:total};
}

function callout(stand){
  const p = D.platoon.find(r=>r.window===state.window && r.stand===stand);
  if(!p) return '<div class="callout"><div class="big">—</div></div>';
  return `<div class="callout"><div class="big">${fmt3(p.xwoba)}</div>
    <div class="cl">xwOBA allowed · ${p.pa} PA</div>
    <div class="cs">${pct(p.whiff_rate)} whiff · ${pct(p.krate,0)} K · ${pct(p.bbrate,0)} BB</div></div>`;
}

function renderMaps(){
  const holder = $('#maps'); holder.innerHTML='';
  const stands = state.stand==='both' ? ['L','R'] : [state.stand];
  holder.style.gridTemplateColumns = stands.length===2 ? '1fr 1fr' : '1fr';
  stands.forEach(st=>{
    const m = drawMap(st);
    const div=document.createElement('div'); div.className='mapbox';
    div.innerHTML = `<div class="mapttl">vs ${st}HH · ${m.n} pitches</div>${m.svg}${callout(st)}`;
    holder.appendChild(div);
  });
}

// ---------- grade rail ----------
function renderRail(){
  const src = state.window==='Pre-Option' ? D.grades_pre : D.grades;
  const byStand = state.stand!=='both';
  const rail = $('#rail'); rail.innerHTML='';
  src.filter(r=>state.pitches.has(r.pitch_type)).forEach(r=>{
    const ms = byStand ? D.mix_by_stand.find(m=>m.window===state.window && m.stand===state.stand && m.pitch_type===r.pitch_type) : null;
    if(byStand && !ms) return;
    const n = ms? ms.n : r.n, usage = ms? ms.usage : r.usage;
    const whiff = ms? ms.whiff_rate : r.whiff_rate, sw = ms? ms.swings : r.swings;
    const izr = ms? ms.in_zone_rate : r.in_zone_rate, xw = ms? ms.xwoba : r.xwoba;
    const el = document.createElement('div'); el.className='prow';
    const gr = byStand ? null : r;
    el.innerHTML = `
      <div class="pbar" style="background:${PC[r.pitch_type]||'#999'}"></div>
      <div class="pmain">
        <p class="pname">${r.pitch_name||r.pitch_type}</p>
        <p class="pmeta">${ms&&ms.velo?ms.velo.toFixed(0):(r.velo?r.velo.toFixed(0):'—')} mph ·
          ${pct(izr,0)} in zone · xwOBA ${fmt3(xw)}${ms&&ms.xwoba_n!=null?` (${ms.xwoba_n} PA)`:''}</p>
        <p class="pn">${n} thrown · ${pct(usage,0)} usage · ${pct(whiff)} whiff on ${sw==null?'—':sw} swings</p>
      </div>
      <div class="pgrades">
        <div class="gcell"><div class="v" style="color:${gcol(gr?gr.stuff_grade:null)}">${gr&&gr.stuff_grade!=null?gr.stuff_grade:'—'}</div><div class="k">stuff</div></div>
        <div class="gcell"><div class="v" style="color:${gcol(gr?gr.command_grade:null)}">${gr&&gr.command_grade!=null?gr.command_grade:'—'}</div><div class="k">cmd</div></div>
        <div class="gbadge" style="background:${gcol(gr?gr.pitch_grade:null)}">${gr&&gr.pitch_grade!=null?gr.pitch_grade:'—'}</div>
      </div>`;
    rail.appendChild(el);
  });
  $('#railnote').textContent = byStand
    ? 'Grades are whole-window, not split by handedness — a by-stand cell is too small to grade. The numbers above the grades are the split; the grades are the pitch.'
    : state.window==='Pre-Option'
       ? 'Grades for the arsenal that got optioned. The splitter is here; the changeup is not.'
    : state.window==='Full 2026'
       ? 'Grades shown are the POST-OPTION window — a full-season grade would average two different arsenals. The counts above them are full-season.'
       : ('50 = major-league average · 10 points = 1 SD · population = RHP pitcher-seasons in the Phillies game log, 2015-2026, >=100 of that pitch (sweeper >=50, thin).');
}

// ---------- tables ----------
function renderTable(){
  const t = $('#tbl');
  if(state.tab==='starts'){
    const rows = D.start_log.filter(r=>state.window==='Full 2026' || r.window===state.window);
    t.innerHTML = `<table><thead><tr><th>Date</th><th>Opp</th><th>BF</th><th>IP</th><th>K</th><th>BB</th><th>HR</th>
      <th>CSW</th><th>Whiff</th><th>xwOBA</th><th>xwOBAcon</th><th>Hard-hit</th><th>Pitches</th></tr></thead><tbody>${
      rows.map(r=>`<tr class="${r.xwoba>=0.40?'hot':''}"><td>${r.game_date}</td><td>${r.opponent} (${r.home_away})</td>
      <td>${r.bf}</td><td>${r.innings_reached}</td><td>${r.k}</td><td>${r.bb}</td><td>${r.hr}</td>
      <td>${pct(r.csw,1)}</td><td>${pct(r.whiff_rate,1)}</td><td>${fmt3(r.xwoba)}</td><td>${fmt3(r.xwobacon)}</td>
      <td>${r.hard_hit}/${r.bip_tracked}</td><td>${r.pitches}</td></tr>`).join('')}</tbody></table>`;
  } else if(state.tab==='lineup'){
    t.innerHTML = `<p class="note" style="margin-top:0">Atlanta bats vs <em>all</em> Phillies pitching, 2026. The head-to-head column is Painter only —
      47 PA, all of it April, against an arsenal since turned over 33%. It is printed so nobody re-derives it and believes it.</p>
      <table><thead><tr><th>Bat</th><th>S</th><th>PA</th><th>H</th><th>HR</th><th>K</th><th>Whiff</th><th>Chase</th><th>xwOBA</th><th>vs Painter</th></tr></thead><tbody>${
      D.atl_lineup.filter(r=>r.pa>=13).map(r=>{ const h=D.h2h.find(x=>x.batter===r.batter);
      return `<tr><td>${r.name}</td><td>${r.stand}</td><td>${r.pa}</td><td>${r.h}</td><td>${r.hr}</td><td>${r.k}</td>
      <td>${pct(r.whiff_rate,1)}</td><td>${pct(r.chase_rate,1)}</td><td>${fmt3(r.xwoba)}</td>
      <td>${h?`${h.pa} PA, ${h.h} H, ${h.k} K`:'—'}</td></tr>`;}).join('')}</tbody></table>`;
  } else if(state.tab==='card'){
    t.innerHTML = `<table><thead><tr><th>Card claim</th><th>Claimed</th><th>Computed</th><th>Denominator</th>
      <th>Window it describes</th><th>Verdict</th></tr></thead><tbody>${
      D.reconciliation.map(r=>{ const cls = r.verdict.includes('STALE')?'v-warn':r.verdict.includes('GRADED')?'v-ok':'v-ok';
      return `<tr><td>${r.card_claim}</td><td>${r.claimed==null?'—':r.claimed}</td><td><strong>${r.computed==null?'—':r.computed}</strong></td>
      <td>${r.n}</td><td>${r.window}</td><td><span class="verdict ${cls}">${r.verdict}</span><br><span style="font-size:11px;color:#666">${r.note}</span></td></tr>`;}).join('')}
      </tbody></table>`;
  } else {
    t.innerHTML = `<table><thead><tr><th>Check</th><th>Dimension</th><th>Rule</th><th>Result</th><th>Detail</th></tr></thead><tbody>${
      D.dq.map(r=>`<tr><td>${r.check}</td><td>${r.dimension}</td><td>${r.rule}</td>
      <td><span class="verdict ${r.result==='PASS'?'v-ok':r.result==='WARN'?'v-warn':'v-bad'}">${r.result}</span></td>
      <td style="font-size:11px">${r.detail}</td></tr>`).join('')}</tbody></table>`;
  }
}
function buildTabs(){
  const t=$('#tabs');
  [['starts','Start log'],['lineup','Atlanta lineup'],['card','Notecard check'],['dq','DQ scorecard']].forEach(([k,l])=>{
    const b=document.createElement('button'); b.textContent=l; b.setAttribute('aria-selected',k===state.tab);
    b.onclick=()=>{ state.tab=k; [...t.children].forEach(c=>c.setAttribute('aria-selected','false'));
                    b.setAttribute('aria-selected','true'); renderTable(); };
    t.appendChild(b);
  });
}

function render(){
  document.querySelectorAll('#winSeg button').forEach(b=>b.setAttribute('aria-pressed', b.textContent===state.window));
  document.querySelectorAll('#standSeg button').forEach(b=>{
    const v = b.textContent==='Both'?'both':b.textContent.includes('LHH')?'L':'R';
    b.setAttribute('aria-pressed', v===state.stand); });
  document.querySelectorAll('#pitchChips button').forEach(b=>b.setAttribute('aria-pressed', state.pitches.has(b.textContent.trim())));
  renderMaps(); renderRail(); renderTable();
}
buildControls(); buildTabs(); render();
