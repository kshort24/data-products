(function(){
"use strict";
var D = window.__UC43__;
var $ = function(s){return document.querySelector(s);};
var frame = 'd1', stand = 'L', basis = 'average';
var CLIENT  = ['Mayza, Tim','Mayza, Tim','Holman, Grant','Holman, Grant','Raley, Brooks','Shugart, Chase','Kerkering, Orion','Alvarado, José','Duran, Jhoan'];
var REVISED = ['Mayza, Tim','Mayza, Tim','Holman, Grant','Shugart, Chase','Shugart, Chase','Kerkering, Orion','Raley, Brooks','Alvarado, José','Duran, Jhoan'];
var script = CLIENT.slice();
var selected = null;

function bfFor(arm, innings){
  var A = avgbf(), M = D.max_bf || {};
  if(basis==='ceiling' && innings>=2 && M[arm]) return {bf:M[arm], basis:'season high'};
  return {bf:A[arm]||0, basis:'mean outing'};
}
function tiers(){ var m={}; (frame==='d1'?D.availability_d1:D.availability_d2).forEach(function(r){m[r.player_name]=r;}); return m; }
function avgbf(){ var m={}; D.coverage_rows.forEach(function(r){ if(r.arm!=='— TOTAL —') m[r.arm]=r.season_avg_bf; }); return m; }
function fmt(x,d){ return (x===null||x===undefined||isNaN(x))?'—':Number(x).toFixed(d===undefined?1:d); }
function esc(s){ return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }

/* ---------------- rail ---------------- */
function renderRail(){
  var T = tiers(), A = avgbf(), rail = $('#rail'); rail.innerHTML='';
  script.forEach(function(arm,i){
    var b = document.createElement('button');
    b.type='button'; b.className='slot'; b.setAttribute('role','listitem');
    var first = arm && script.indexOf(arm)===i;
    var tier = arm && T[arm] ? T[arm].tier : '';
    b.className = 'slot ' + (tier||'') + (arm && !first ? ' cont' : '') + (arm?'':' empty');
    if(selected===i) b.style.outline='2px solid var(--red)';
    var k = arm ? script.filter(function(x){return x===arm;}).length : 0;
    var q = arm && first ? bfFor(arm, k) : null;
    b.innerHTML = '<span class="inn">Inn '+(i+1)+'</span>'
      + '<span class="arm">'+esc(arm ? arm.split(',')[0] : 'open')+'</span>'
      + '<span class="bf">'+(arm ? (first ? fmt(q.bf,2)+' BF · '+q.basis : 'same outing') : 'tap to fill')+'</span>';
    b.addEventListener('click', function(){ selected = (selected===i?null:i); renderRail(); renderPool(); });
    rail.appendChild(b);
  });
}

/* ---------------- pool ---------------- */
function renderPool(){
  var T = tiers(), A = avgbf(), pool = $('#pool'); pool.innerHTML='';
  var names = D.availability_d1.map(function(r){return r.player_name;});
  names.forEach(function(nm){
    var t = T[nm] ? T[nm].tier : 'GREEN';
    var c = document.createElement('button');
    c.type='button'; c.className='armchip';
    c.innerHTML = '<span class="dot '+t+'"></span>'+esc(nm.split(',')[0])
      + ' <span class="mono">'+(A[nm]!==undefined?fmt(A[nm],2)+' BF':'—')+'</span>';
    c.title = T[nm] ? T[nm].reason : '';
    c.addEventListener('click', function(){
      if(selected===null){ $('#railhint').textContent='Pick an inning first, then choose an arm.'; return; }
      script[selected]=nm; selected=null; render();
      $('#railhint').textContent='Assigned. Each arm still delivers one outing — give him two innings and the meter does not move.';
    });
    pool.appendChild(c);
  });
  var clr = document.createElement('button');
  clr.type='button'; clr.className='armchip'; clr.innerHTML='<span class="dot" style="background:var(--rule-2)"></span>leave open';
  clr.addEventListener('click', function(){ if(selected!==null){ script[selected]=null; selected=null; render(); } });
  pool.appendChild(clr);
}

/* ---------------- meter ---------------- */
function renderMeter(){
  var T = tiers(), A = avgbf();
  var used = script.filter(Boolean).filter(function(v,i,a){return a.indexOf(v)===i;});
  var cap = used.reduce(function(s,n){
    var k = script.filter(function(x){return x===n;}).length;
    return s + bfFor(n, k).bf; }, 0);
  var need = D.coverage.required_bf_median_regulation_game;
  var innings = script.filter(Boolean).length;
  var short = need - cap;
  $('#m-cap').textContent = fmt(cap,1);
  $('#m-cap').className = 'big ' + (short>0 ? 'short' : 'ok');
  $('#m-need').textContent = fmt(need,0);
  $('#m-arms').textContent = used.length;
  $('#m-inn').textContent = innings;
  $('#m-games').textContent = D.coverage.regulation_games_in_benchmark;
  var scale = Math.max(need*1.18, cap*1.08, 1);
  $('#fill').style.width = (100*cap/scale)+'%';
  $('#needmark').style.left = (100*need/scale)+'%';
  var nl = $('#needlbl'); nl.style.left = (100*need/scale)+'%'; nl.textContent = need+' BF needed';
  var reds = used.filter(function(n){ return T[n] && T[n].tier==='RED'; });
  var w = $('#warn');
  var msgs = [];
  if(short>0) msgs.push('Short by '+fmt(short,1)+' batters faced — about '+fmt(short/3,1)+' innings.');
  if(reds.length) msgs.push('RED arm'+(reds.length>1?'s':'')+' assigned: '+reds.map(function(n){return n.split(',')[0];}).join(', ')+'.');
  if(innings<9) msgs.push((9-innings)+' inning'+(9-innings>1?'s':'')+' unassigned.');
  var aaaStretch = used.filter(function(n){ return n==='Holman, Grant' && script.filter(function(x){return x===n;}).length>=2; });
  if(basis==='ceiling' && aaaStretch.length) msgs.push('That ceiling leans on Holman\u2019s Triple-A high of 10 batters \u2014 in his major-league debut.');
  if(msgs.length){ w.hidden=false;
    w.innerHTML='<svg width="13" height="13" viewBox="0 0 13 13" aria-hidden="true"><path d="M6.5 0.8 12.7 12H0.3z" fill="currentColor"/><path d="M6.5 4.4v3.6M6.5 9.4v1" stroke="var(--panel)" stroke-width="1.3" stroke-linecap="round"/></svg><span>'+esc(msgs.join(' '))+'</span>';
  } else { w.hidden=true; w.innerHTML=''; }
  $('#basis-note').textContent = basis==='average'
    ? 'Every arm delivers his 2026 mean outing, whatever the script asks. The conservative read.'
    : 'An arm asked for two innings delivers his season-high batters faced; one-inning arms stay at their mean. A ceiling is only as good as the evidence behind it.';
  $('#v-cap').textContent = fmt(D.coverage.expected_bf_capacity,1);
  $('#v-need').textContent = fmt(need,0);
  $('#v-short').textContent = fmt(D.coverage.shortfall_bf,1)+' batter';
  $('#v-shortinn').textContent = fmt(D.coverage.shortfall_innings,1);
}

/* ---------------- tables ---------------- */
function renderAvail(){
  var rows = frame==='d1' ? D.availability_d1 : D.availability_d2;
  $('#avail-note').textContent = frame==='d1'
    ? 'Target 2026-09-12 — the night after the last logged game. Certifiable: the log is complete to the night before.'
    : 'Target 2026-09-13 — the session date. NOT certifiable: if a 09-12 game was played it is not in the cache, so every rest figure here is one game stale.';
  var tb = $('#t-avail tbody'); tb.innerHTML='';
  rows.forEach(function(r){
    var tr = document.createElement('tr');
    tr.innerHTML = '<td>'+esc(r.player_name.split(',')[0])+'</td>'
      + '<td class="n">'+esc(r.last_outing ? String(r.last_outing).slice(5) : 'AAA 8/30')+'</td>'
      + '<td class="n">'+(r.days_of_rest===null||r.days_of_rest===undefined?'—':r.days_of_rest)+'</td>'
      + '<td class="n">'+r.pitches_last_7d+'</td>'
      + '<td class="n">'+r.appearances_last_7d+'</td>'
      + '<td><span class="tag '+r.tier+'">'+r.tier+'</span></td>';
    tr.title = r.reason; tb.appendChild(tr);
  });
}
function renderMip(){
  var tb = $('#t-mip tbody'); tb.innerHTML='';
  var rows = D.mip.filter(function(r){return r.multi_inning_rate!==null;})
                  .sort(function(a,b){return b.multi_inning_rate-a.multi_inning_rate;});
  var mx = Math.max.apply(null, rows.map(function(r){return r.multi_inning_rate;}));
  rows.forEach(function(r){
    var aaa = r.evidence_tier.indexOf('AAA')===0;
    var tr = document.createElement('tr');
    tr.innerHTML = '<td>'+esc(r.player_name.split(',')[0])+(aaa?' <span class="mono" style="color:var(--ink-3);font-size:10px">AAA</span>':'')+'</td>'
      + '<td><span class="sparkrow"><span class="track"><i class="'+(aaa?'aaa':'')+'" style="width:'+(100*r.multi_inning_rate/mx)+'%"></i></span>'
      + '<span class="mono" style="font-size:11px">'+r.multi_inning_apps+'/'+r.relief_apps+'</span></span></td>'
      + '<td class="n">'+r.max_pitches+'</td><td class="n">'+r.max_bf+'</td>';
    tb.appendChild(tr);
  });
}
function renderAnchor(){
  var tb = $('#t-anchor tbody'); tb.innerHTML='';
  D.anchor.forEach(function(r){
    var inn = r.inning_entered===r.inning_exited ? String(r.inning_entered) : r.inning_entered+'–'+r.inning_exited;
    var named = r.is_start ? '<span style="color:var(--ink-3)">starter</span>'
      : (r.client_named_as_spent ? 'yes' : '<span class="flag">no — but he pitched</span>');
    var tr = document.createElement('tr');
    tr.innerHTML = '<td>'+esc(r.player_name.split(',')[0])+'</td><td class="n">'+inn+'</td>'
      + '<td class="n">'+r.pitches+'</td><td class="n">'+r.batters_faced+'</td>'
      + '<td class="n">'+(r.days_of_rest===null?'—':r.days_of_rest)+'</td>'
      + '<td class="n">'+r.pitches_last_3d+'</td><td class="n">'+r.pitches_last_7d+'</td><td>'+named+'</td>';
    tb.appendChild(tr);
  });
}
function renderOpp(){
  var tb = $('#t-drift tbody'); tb.innerHTML='';
  D.opp_drift.forEach(function(r,i){
    var g = D.opp_games[i] || {};
    var tr = document.createElement('tr');
    tr.innerHTML = '<td>'+esc(String(r.game_date))+'</td>'
      + '<td class="n">'+(100*r.FF).toFixed(1)+'%</td>'
      + '<td class="n"><b>'+(100*r.FS).toFixed(1)+'%</b></td>'
      + '<td class="n">'+(100*r.FC).toFixed(1)+'%</td>'
      + '<td class="n">'+(g.pitches||'—')+'</td><td class="n">'+(g.last_inning||'—')+'</td>';
    tb.appendChild(tr);
  });
  var ob = $('#t-order tbody'); ob.innerHTML='';
  D.atl_order.forEach(function(r){
    var flip = r.switch_hitter ? ' <span class="mono" style="font-size:10px;color:var(--ink-3)">switch</span>' : '';
    var lhp = r.stand_vs_lhp==='L' ? '<b class="flag">L</b>' : r.stand_vs_lhp;
    var tr = document.createElement('tr');
    tr.innerHTML = '<td class="n">'+r.spot+'</td><td>'+esc(r.name)+flip+'</td><td>'+esc(r.stand_vs_rhp)+'</td><td>'+lhp+'</td>';
    ob.appendChild(tr);
  });
}
function renderDQ(){
  var tb = $('#t-dq tbody'); tb.innerHTML='';
  D.dq.forEach(function(r){
    var cls = r.status==='PASS' ? 'GREEN' : (r.status==='WARN' ? 'AMBER' : 'RED');
    var tr = document.createElement('tr');
    tr.innerHTML = '<td>'+esc(r.dimension)+'</td><td>'+esc(r.check)+'</td><td>'+esc(r.result)+'</td>'
      + '<td><span class="tag '+cls+'">'+esc(r.status)+'</span></td>';
    tb.appendChild(tr);
  });
  (D.defects||[]).forEach(function(r){
    if(String(r.defect).indexOf('NEW')<0) return;
    var tr = document.createElement('tr');
    tr.innerHTML = '<td><span class="flag">defect</span></td><td>'+esc(r.defect)+'</td><td>'+esc(r.exposure)+'</td>'
      + '<td><span class="tag AMBER">remediated</span></td>';
    tb.appendChild(tr);
  });
}

/* ---------------- Holman pitch map ---------------- */
var PX={x0:-2.2,x1:2.2,y0:0.2,y1:5.0}, W=340,H=330, PAD={l:34,r:10,t:12,b:28};
var hidden = {};
function sx(x){ return PAD.l + (x-PX.x0)/(PX.x1-PX.x0)*(W-PAD.l-PAD.r); }
function sy(y){ return H-PAD.b - (y-PX.y0)/(PX.y1-PX.y0)*(H-PAD.t-PAD.b); }
function renderLegend(){
  var types = {}; D.holman_pitches.forEach(function(p){ types[p.pitch_name]=p.pitch_type; });
  var L = $('#legend'); L.innerHTML='';
  Object.keys(types).forEach(function(nm){
    var b=document.createElement('button'); b.type='button';
    b.setAttribute('aria-pressed', hidden[nm]?'false':'true');
    b.innerHTML='<span class="sw" style="background:'+(D.pitch_colors[nm]||'#999')+'"></span>'+esc(nm);
    b.addEventListener('click',function(){ hidden[nm]=!hidden[nm]; renderLegend(); renderMap(); });
    L.appendChild(b);
  });
}
function renderMap(){
  var pts = D.holman_pitches.filter(function(p){ return p.stand===stand && !hidden[p.pitch_name]; });
  var sz = D.holman_sz, s=[];
  s.push('<rect x="0" y="0" width="'+W+'" height="'+H+'" fill="none"/>');
  for(var gx=-2;gx<=2;gx++) s.push('<line x1="'+sx(gx)+'" y1="'+PAD.t+'" x2="'+sx(gx)+'" y2="'+(H-PAD.b)+'" stroke="var(--grid)" stroke-width="1"/>');
  for(var gy=1;gy<=5;gy++) s.push('<line x1="'+PAD.l+'" y1="'+sy(gy)+'" x2="'+(W-PAD.r)+'" y2="'+sy(gy)+'" stroke="var(--grid)" stroke-width="1"/>');
  s.push('<rect x="'+sx(-0.83)+'" y="'+sy(sz.top)+'" width="'+(sx(0.83)-sx(-0.83))+'" height="'+(sy(sz.bot)-sy(sz.top))+
         '" fill="#FF5733" fill-opacity="0.13" stroke="var(--ink-2)" stroke-width="1"/>');
  pts.forEach(function(p){
    s.push('<circle cx="'+sx(p.plate_x).toFixed(1)+'" cy="'+sy(p.plate_z).toFixed(1)+'" r="3.6" fill="'+(D.pitch_colors[p.pitch_name]||'#999')+
      '" fill-opacity="0.78" stroke="var(--panel)" stroke-width="0.7"><title>'+esc(p.pitch_name)+' · '+fmt(p.release_speed,1)+' mph · '+esc(p.description)+'</title></circle>');
  });
  for(var ly=1;ly<=5;ly++) s.push('<text x="'+(PAD.l-6)+'" y="'+(sy(ly)+3.5)+'" text-anchor="end" font-size="9" fill="var(--ink-3)" font-family="IBM Plex Mono, monospace">'+ly+'</text>');
  for(var lx=-2;lx<=2;lx++) s.push('<text x="'+sx(lx)+'" y="'+(H-PAD.b+13)+'" text-anchor="middle" font-size="9" fill="var(--ink-3)" font-family="IBM Plex Mono, monospace">'+lx+'</text>');
  s.push('<text x="'+(W/2)+'" y="'+(H-4)+'" text-anchor="middle" font-size="9.5" fill="var(--ink-3)">plate_x (ft, catcher view)</text>');
  s.push('<text transform="translate(10,'+(H/2)+') rotate(-90)" text-anchor="middle" font-size="9.5" fill="var(--ink-3)">plate_z (ft)</text>');
  s.push('<text x="'+(W-PAD.r)+'" y="'+(PAD.t+9)+'" text-anchor="end" font-size="10.5" fill="var(--ink-2)" font-family="Oswald, sans-serif">vs '+(stand==='L'?'LHB':'RHB')+' · n='+pts.length+'</text>');
  $('#map').innerHTML = s.join('');
  var tb = $('#t-holman tbody'); tb.innerHTML='';
  var wc={}; D.holman_wc.forEach(function(r){ wc[r.stand+'|'+r.pitch_type]=r; });
  D.holman_mix.filter(function(r){return r.stand===stand;}).forEach(function(r){
    var w = wc[stand+'|'+r.pitch_type]||{};
    var tr=document.createElement('tr');
    tr.innerHTML='<td><span class="sw" style="display:inline-block;width:9px;height:9px;border-radius:50%;background:'
      +(D.pitch_colors[r.pitch_name]||'#999')+';margin-right:6px"></span>'+esc(r.pitch_name)+'</td>'
      +'<td class="n">'+fmt(r.usage,1)+'%</td><td class="n">'+fmt(r.release_speed,1)+'</td>'
      +'<td class="n">'+fmt(r.horiz,1)+'"</td><td class="n">'+fmt(r.vert,1)+'"</td>'
      +'<td class="n">'+(w.whiff_rate!==undefined?fmt(100*w.whiff_rate,1)+'%':'—')+'</td>'
      +'<td class="n">'+(w.chase_rate!==undefined?fmt(100*w.chase_rate,1)+'%':'—')+'</td>';
    tb.appendChild(tr);
  });
  var c = D.holman_count.filter(function(r){return r.stand===stand;})[0];
  if(c) $('#holman-count').innerHTML = '<b>'+c.pa+' PA</b> vs '+(stand==='L'?'LHB':'RHB')+' — K '+fmt(100*c.k_rate,1)
    +'%, BB '+fmt(100*c.bb_rate,1)+'%, <b'+(c.hr?' class="flag"':'')+'>'+c.hr+' home run'+(c.hr===1?'':'s')+'</b>'
    +' ('+fmt(100*c.hr_rate,1)+'% of PA). Counting outcomes only — no wOBA at the AAA tier.';
}

/* ---------------- boot ---------------- */
function render(){ renderRail(); renderPool(); renderMeter(); renderAvail(); }
function start(){
  $('#pill-anchor').textContent = 'anchor game ' + D.meta.anchor_game;
  $('#pill-log').textContent = 'PHI log → ' + D.meta.phi_log_max;
  $('#pill-aaa').textContent = 'AAA log → ' + D.meta.lhv_log_max;
  $('#holman-note').textContent = 'MLBAM 680880 · RHP · 20 appearances, 348 pitches, 104 PA, 2026-05-10 → 2026-08-30. '
    + 'No MLB pitches exist: this is a supporting tier, read for mix and shape, not for rates.';
  ['btn-d1','btn-d2'].forEach(function(id){ $('#'+id).addEventListener('click', function(){
    frame = this.dataset.frame; $('#btn-d1').setAttribute('aria-pressed', frame==='d1');
    $('#btn-d2').setAttribute('aria-pressed', frame==='d2'); render(); }); });
  var presets = {client:CLIENT, revised:REVISED, clear:[null,null,null,null,null,null,null,null,null]};
  ['btn-client','btn-revised','btn-clear'].forEach(function(id){ $('#'+id).addEventListener('click', function(){
    var p = this.dataset.preset; script = presets[p].slice(); selected = null;
    ['btn-client','btn-revised','btn-clear'].forEach(function(x){ $('#'+x).setAttribute('aria-pressed', x===id); });
    $('#railhint').textContent = p==='revised'
      ? 'Revised: same seven arms. The two-inning asks move off Holman and onto Shugart, whose 9-batter, 44-pitch high was set in the majors this season.'
      : (p==='client' ? 'Your script as written.' : 'Empty. Build one.');
    render(); }); });
  ['btn-avg','btn-max'].forEach(function(id){ $('#'+id).addEventListener('click', function(){
    basis = this.dataset.basis; $('#btn-avg').setAttribute('aria-pressed', basis==='average');
    $('#btn-max').setAttribute('aria-pressed', basis==='ceiling'); render(); }); });
  ['btn-lhb','btn-rhb'].forEach(function(id){ $('#'+id).addEventListener('click', function(){
    stand = this.dataset.stand; $('#btn-lhb').setAttribute('aria-pressed', stand==='L');
    $('#btn-rhb').setAttribute('aria-pressed', stand==='R'); renderMap(); }); });
  render(); renderMip(); renderAnchor(); renderOpp(); renderDQ(); renderLegend(); renderMap();
}
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
