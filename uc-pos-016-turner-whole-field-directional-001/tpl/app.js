(function(){
'use strict';
var D = window.__UC42A__;
var M = D.meta, DC = M.dir_colors, SEASONS = M.seasons;
var NS='http://www.w3.org/2000/svg';
var DIRS=['Pull','Straightaway','Oppo'];

// ---------------------------------------------------------------- helpers
function el(t,a){var n=document.createElementNS(NS,t);if(a)for(var k in a)n.setAttribute(k,a[k]);return n;}
function $(s){return document.querySelector(s);}
function clear(n){while(n.firstChild)n.removeChild(n.firstChild);}
function fmt(v,d){return v==null||isNaN(v)?'—':Number(v).toFixed(d==null?3:d);}
function pct(v,d){return v==null||isNaN(v)?'—':(v*100).toFixed(d==null?1:d)+'%';}
function trim3(v){var s=fmt(v,3);return s.charAt(0)==='0'?s.slice(1):s;}
function band(z){var a=Math.abs(z);return a>=2.5?['clears','clears noise']:a>=1.5?['mod','moderate']:['noise','noise'];}
function text(p,x,y,s,cls,anchor,size){
  var t=el('text',{x:x,y:y,'text-anchor':anchor||'middle'});
  if(cls)t.setAttribute('class',cls); if(size)t.setAttribute('font-size',size);
  t.textContent=s; p.appendChild(t); return t;}

var tip=$('#tip');
function showTip(e,html){tip.innerHTML=html;tip.classList.add('on');moveTip(e);}
function moveTip(e){
  var w=tip.offsetWidth,h=tip.offsetHeight,x=e.clientX+14,y=e.clientY+14;
  if(x+w>window.innerWidth-8)x=e.clientX-w-14;
  if(y+h>window.innerHeight-8)y=e.clientY-h-14;
  tip.style.left=x+'px';tip.style.top=y+'px';}
function hideTip(){tip.classList.remove('on');}

// ---------------------------------------------------------------- state
var S={season:3, metric:'rc6', zone:'in', dir:'all', throws:'all',
       showAll:true, hover:null, playing1:false, playing2:false};

// ================================================================ SCENE 1
var ctxSvg=$('#ctx');
var CTX_W=900,CTX_H=470,CL=64,CR=872,CT=26,CB=366,RUG_T=392,RUG_B=408;

function ctxY(d){return S.metric==='rc6'?d.rc6:d.rc;}
var ctxScales=(function(){
  var xs=D.ctx.map(function(d){return d.br;});
  return {x0:0,x1:Math.max.apply(null,xs)*1.06};
})();
function yDomain(){
  var vs=D.ctx.map(ctxY); var mx=Math.max.apply(null,vs);
  return {y0:0,y1:mx*1.08};
}
function sxC(v){var s=ctxScales;return CL+(v-s.x0)/(s.x1-s.x0)*(CR-CL);}
function syC(v,dom){return CB-(v-dom.y0)/(dom.y1-dom.y0)*(CB-CT);}
function rC(g){return Math.max(3.2,Math.sqrt(g)*1.28);}

function drawCtx(){
  clear(ctxSvg);
  var dom=yDomain(), yr=SEASONS[S.season];
  var g=el('g');ctxSvg.appendChild(g);
  // grid + axes
  var i,ty,tx;
  for(i=0;i<=5;i++){
    ty=dom.y0+(dom.y1-dom.y0)*i/5;
    var yy=syC(ty,dom);
    g.appendChild(el('line',{x1:CL,x2:CR,y1:yy,y2:yy,'class':'gridline'}));
    text(g,CL-9,yy+3.5,Math.round(ty),'axlab','end');
  }
  for(i=0;i<=6;i++){
    tx=ctxScales.x0+(ctxScales.x1-ctxScales.x0)*i/6;
    var xx=sxC(tx);
    g.appendChild(el('line',{x1:xx,x2:xx,y1:CT,y2:CB,'class':'gridline'}));
    text(g,xx,CB+14,trim3(tx),'axlab');
  }
  g.appendChild(el('line',{x1:CL,x2:CR,y1:CB,y2:CB,'class':'ax'}));
  text(g,(CL+CR)/2,RUG_B+20,'Barrel rate  (barrels / balls in play)','axtitle');
  var yt=text(g,0,0,S.metric==='rc6'?'Runs created per 600 PA':'Runs created (raw count)','axtitle','middle');
  yt.setAttribute('transform','translate(18,'+((CT+CB)/2)+') rotate(-90)');

  // season stamp
  var st=text(g,CR-6,CB-14,yr,'seasonstamp','end');st.setAttribute('opacity','.6');

  // rug band label
  text(g,CL-9,RUG_T+12,'rug','axlab','end');

  // points
  var subjPts=[];
  D.ctx.forEach(function(d){
    var isTT=d.p===M.subject, isSel=isTT&&d.y===yr;
    var col=isSel?DC.Pull:(isTT?DC.Oppo:DC.Straightaway);
    var op=isSel?.95:(isTT?.55:.32);
    var c=el('circle',{cx:sxC(d.br),cy:syC(ctxY(d),dom),r:rC(d.g),
      fill:col,'fill-opacity':op,stroke:isSel?'#fff':'none','stroke-width':isSel?2:0,'class':'pt'});
    c.addEventListener('mouseenter',function(e){showTip(e,
      '<b>'+d.p+' &middot; '+d.y+'</b><br>'+
      '<span class="k">BARREL</span> '+trim3(d.br)+'  <span class="k">HARD-HIT</span> '+(d.hh==null?'—':pct(d.hh))+'<br>'+
      '<span class="k">RC</span> '+d.rc+'  <span class="k">RC/600</span> '+fmt(d.rc6,1)+'<br>'+
      '<span class="k">wOBA</span> '+trim3(d.woba)+'  <span class="k">OPS</span> '+trim3(d.ops)+'<br>'+
      '<span class="k">PA</span> '+d.pa+'  <span class="k">G</span> '+d.g);});
    c.addEventListener('mousemove',moveTip);
    c.addEventListener('mouseleave',hideTip);
    g.appendChild(c);
    // rug tick
    var rx=sxC(d.br);
    var rt=el('line',{x1:rx,x2:rx,y1:RUG_T,y2:RUG_B,
      stroke:isSel?DC.Pull:(isTT?DC.Oppo:'#aab3bd'),
      'stroke-width':isSel?3:(isTT?2:1),'stroke-opacity':isSel?1:(isTT?.85:.5)});
    g.appendChild(rt);
    if(isSel)subjPts.push({d:d,x:rx,y:syC(ctxY(d),dom),r:rC(d.g)});
  });

  // callout from rug tick to the selected point
  subjPts.forEach(function(p){
    g.appendChild(el('line',{x1:p.x,x2:p.x,y1:p.y+p.r+2,y2:RUG_T-2,
      stroke:DC.Pull,'stroke-width':1.2,'stroke-dasharray':'3 3','stroke-opacity':.75}));
    var lx=Math.min(p.x+14,CR-190), ly=Math.max(p.y-p.r-16,CT+14);
    var lab=text(g,lx,ly,M.subject.split(', ').reverse().join(' ')+" '"+String(p.d.y).slice(2),null,'start',12.5);
    lab.setAttribute('font-weight','700');lab.setAttribute('fill',DC.Pull);
    lab.setAttribute('stroke','#fff');lab.setAttribute('stroke-width','3.5');
    lab.setAttribute('paint-order','stroke fill');
    var l2=text(g,lx,ly+14,'barrel '+trim3(p.d.br)+' · '+fmt(p.d.rc6,1)+' RC/600 · '+p.d.pa+' PA',null,'start',11);
    l2.setAttribute('fill','#43505c');l2.setAttribute('font-family','var(--mono)');
    l2.setAttribute('stroke','#fff');l2.setAttribute('stroke-width','3');
    l2.setAttribute('paint-order','stroke fill');
  });
  $('#ctxTitleMetric').textContent=S.metric==='rc6'?'runs created per 600 PA':'runs created (raw)';
}

function drawTTSeasons(){
  var tb=$('#ttSeasons tbody');clear(tb);
  var yr=SEASONS[S.season];
  D.ctx.filter(function(d){return d.p===M.subject;})
    .sort(function(a,b){return a.y-b.y;})
    .forEach(function(d){
      var tr=document.createElement('tr');
      if(d.y===yr)tr.className='hi';
      [[d.y,0],[d.pa,0],[trim3(d.br),1],[pct(d.hh),1],[trim3(d.woba),1],[trim3(d.ops),1],
       [d.rc,0],[fmt(d.rc6,1),1]].forEach(function(c,i){
        var td=document.createElement('td');
        if(i>0)td.className='num';
        td.textContent=c[0];tr.appendChild(td);});
      tb.appendChild(tr);});
}

// ================================================================ SCENE 2
var spraySvg=$('#spray'), pmSvg=$('#pitchmap');
var SPRAY_HX=230, SPRAY_HY=412, SPRAY_K=0.72;
function sxS(x){return SPRAY_HX+x*SPRAY_K;}
function syS(y){return SPRAY_HY-y*SPRAY_K;}
var PM_CX=230, PM_Z0=408, PM_KX=92, PM_KZ=92;
function sxP(x){return PM_CX+x*PM_KX;}
function syP(z){return PM_Z0-z*PM_KZ;}

var nodeIndex={};   // pitch_uid -> [sprayNode, pmNode]

function filtered(){
  var yr=SEASONS[S.season];
  return D.bip.filter(function(b){
    if(b.y!==yr)return false;
    if(S.zone==='in'&&b.oz)return false;
    if(S.zone==='out'&&!b.oz)return false;
    if(S.dir!=='all'&&b.d!==S.dir)return false;
    if(S.throws!=='all'&&b.t!==S.throws)return false;
    return true;});
}

function drawFieldFrame(g){
  var i,a,pts;
  // reference outfield arc: 330 down the lines, ~400 to center (generic, not park-specific)
  pts=[];
  for(i=0;i<=40;i++){
    a=(-45+90*i/40)*Math.PI/180;
    var d=330+70*Math.cos(a*2)*0.5+70*(1-Math.abs(a)/(Math.PI/4))*0.5;
    d=330+(400-330)*Math.pow(Math.cos(a),2.2);
    pts.push(sxS(d*Math.sin(a))+','+syS(d*Math.cos(a)));
  }
  g.appendChild(el('polyline',{points:pts.join(' '),'class':'field'}));
  // foul lines
  [-1,1].forEach(function(s){
    g.appendChild(el('line',{x1:sxS(0),y1:syS(0),x2:sxS(s*233),y2:syS(233),'class':'field'}));});
  // infield diamond
  var b1=[63.6,63.6],b2=[0,127.3],b3=[-63.6,63.6];
  g.appendChild(el('polygon',{points:[sxS(0)+','+syS(0),sxS(b1[0])+','+syS(b1[1]),
    sxS(b2[0])+','+syS(b2[1]),sxS(b3[0])+','+syS(b3[1])].join(' '),'class':'field'}));
  // governed hit_direction wedge: y = ±4.7x
  [-1,1].forEach(function(s){
    var yEnd=430, xEnd=s*yEnd/4.7;
    g.appendChild(el('line',{x1:sxS(0),y1:syS(0),x2:sxS(xEnd),y2:syS(yEnd),'class':'wedge'}));});
  function halo(n,col){n.setAttribute('fill',col);n.setAttribute('stroke','#fff');
    n.setAttribute('stroke-width','3.5');n.setAttribute('paint-order','stroke fill');
    n.setAttribute('font-weight','700');return n;}
  halo(text(g,sxS(-205),syS(268),'PULL','axlab','middle',11),DC.Pull);
  halo(text(g,sxS(0),syS(352),'STRAIGHTAWAY','axlab','middle',10),DC.Straightaway);
  halo(text(g,sxS(205),syS(268),'OPPO','axlab','middle',11),DC.Oppo);
  text(g,sxS(0),SPRAY_HY+32,'home plate · dashed lines = governed ±4.7-slope hit_direction boundary','axlab');
}

function drawZoneFrame(g){
  var z=M.zone, zx=z.x_half, i;
  // 3x3 cells
  for(i=1;i<3;i++){
    var cx=-zx+2*zx*i/3;
    g.appendChild(el('line',{x1:sxP(cx),x2:sxP(cx),y1:syP(z.z_bot),y2:syP(z.z_top),'class':'zonecell'}));
    var cz=z.z_bot+(z.z_top-z.z_bot)*i/3;
    g.appendChild(el('line',{x1:sxP(-zx),x2:sxP(zx),y1:syP(cz),y2:syP(cz),'class':'zonecell'}));
  }
  g.appendChild(el('rect',{x:sxP(-zx),y:syP(z.z_top),width:sxP(zx)-sxP(-zx),
    height:syP(z.z_bot)-syP(z.z_top),'class':'zonebox'}));
  // home plate pentagon at the bottom, catcher's view
  var py=PM_Z0+8;
  g.appendChild(el('polygon',{points:[sxP(-zx)+','+py,sxP(zx)+','+py,sxP(zx)+','+(py+8),
    sxP(0)+','+(py+15),sxP(-zx)+','+(py+8)].join(' '),fill:'none',stroke:'var(--line)'}));
  text(g,sxP(-1.42),syP(3.95),'◀ INSIDE to a RHB','axlab','middle',10);
  text(g,sxP(1.36),syP(3.95),'OUTSIDE ▶','axlab','middle',10);
  text(g,sxP(0),py+30,"catcher's view · plate_x / plate_z in feet",'axlab');
  text(g,sxP(0),py+43,"box = Statcast zones 1–9 · the governed in/out authority",'axlab');
  // axis ticks
  [-2,-1,0,1,2].forEach(function(v){text(g,sxP(v),PM_Z0-4,v+'','axlab','middle',9);});
  [1,2,3,4].forEach(function(v){text(g,sxP(-2.30),syP(v)+3,v+'','axlab','end',9);});

}

function drawLinked(){
  clear(spraySvg);clear(pmSvg);nodeIndex={};
  var gs=el('g');spraySvg.appendChild(gs);
  var gp=el('g');pmSvg.appendChild(gp);
  drawFieldFrame(gs);drawZoneFrame(gp);
  var yr=SEASONS[S.season];
  var stampS=text(gs,444,50,yr,'seasonstamp','end');stampS.setAttribute('opacity','.5');
  var stampP=text(gp,444,PM_Z0-16,yr,'seasonstamp','end');stampP.setAttribute('opacity','.45');

  // faint backdrop: pitches that produced no ball in play
  if(S.showAll){
    var o=D.other, n=o.y.length, bg=el('g');
    for(var i=0;i<n;i++){
      if(o.y[i]!==yr)continue;
      if(S.zone==='in'&&o.oz[i]!==0)continue;
      if(S.zone==='out'&&o.oz[i]!==1)continue;
      if(S.throws!=='all'&&o.t[i]!==(S.throws==='L'?1:0))continue;
      bg.appendChild(el('circle',{cx:sxP(o.px[i]),cy:syP(o.pz[i]),r:2.1,'class':'ghost'}));
    }
    gp.appendChild(bg);
  }

  var rows=filtered();
  var layerS=el('g');gs.appendChild(layerS);
  var layerP=el('g');gp.appendChild(layerP);
  rows.forEach(function(b){
    var col=DC[b.d]||DC.Straightaway;
    var cs=el('circle',{cx:sxS(b.x),cy:syS(b.yy),r:3.4,fill:col,'fill-opacity':.78,'class':'pt'});
    var cp=null;
    if(b.px!=null&&b.pz!=null){
      cp=el('circle',{cx:sxP(b.px),cy:syP(b.pz),r:3.6,fill:col,'fill-opacity':.8,
        stroke:b.oz?'#101418':'none','stroke-width':b.oz?.7:0,'class':'pt'});
    }
    nodeIndex[b.u]=[cs,cp];
    function enter(e){
      link(b.u,true);
      showTip(e,'<b>'+b.d+'</b> · '+b.dt+'<br>'+
        '<span class="k">PITCH</span> '+(b.pt||'—')+' vs '+b.t+'HP, zone '+b.z+(b.oz?' (out)':' (in)')+'<br>'+
        '<span class="k">PLATE</span> x '+fmt(b.px,2)+', z '+fmt(b.pz,2)+'<br>'+
        '<span class="k">CONTACT</span> '+(b.ev==null?'EV —':b.ev+' mph')+', '+(b.la==null?'LA —':b.la+'&deg;')+
        (b.bb?' · '+b.bb.replace(/_/g,' '):'')+'<br>'+
        '<span class="k">RESULT</span> '+(b.e?b.e.replace(/_/g,' '):'—'));
    }
    function leave(){link(b.u,false);hideTip();}
    cs.addEventListener('mouseenter',enter);cs.addEventListener('mousemove',moveTip);
    cs.addEventListener('mouseleave',leave);
    layerS.appendChild(cs);
    if(cp){cp.addEventListener('mouseenter',enter);cp.addEventListener('mousemove',moveTip);
      cp.addEventListener('mouseleave',leave);layerP.appendChild(cp);}
  });

  $('#sprayN').textContent=rows.length+' balls in play';
  var withLoc=rows.filter(function(b){return b.px!=null;}).length;
  $('#pmN').textContent=withLoc+' pitches put in play'+(S.showAll?' + backdrop':'');
}

function link(u,on){
  var pair=nodeIndex[u];if(!pair)return;
  pair.forEach(function(n){if(!n)return;
    n.setAttribute('r',on?6.4:(n===pair[1]?3.6:3.4));
    n.setAttribute('fill-opacity',on?1:.78);
    n.setAttribute('stroke',on?'#101418':(n===pair[1]&&n.getAttribute('stroke-width')>0?'#101418':'none'));
    n.setAttribute('stroke-width',on?2:(n===pair[1]?0.7:0));});
}

// -------- mix bars
function drawMix(){
  var svg=$('#mixbars');clear(svg);
  var g=el('g');svg.appendChild(g);
  var L=118,R=760,T=22,rowH=34;
  var zlabel=S.zone==='in'?'in_zone':S.zone==='out'?'outside':'all';
  SEASONS.forEach(function(yr,i){
    var row=D.rates.filter(function(r){return r.game_year===yr&&r.zone===zlabel;})[0];
    if(!row)return;
    var y=T+i*rowH, x=L;
    var sel=(i===S.season);
    text(g,L-12,y+15,yr,null,'end',13).setAttribute('font-weight',sel?'700':'400');
    text(g,L-12,y+27,'n='+row.n_bip,'axlab','end',9.5);
    [['Pull',row.pull_rate],['Straightaway',row.straight_rate],['Oppo',row.oppo_rate]].forEach(function(p){
      var w=p[1]*(R-L);
      var r=el('rect',{x:x,y:y,width:Math.max(0,w),height:22,fill:DC[p[0]],
        'fill-opacity':sel?.92:.32});
      g.appendChild(r);
      if(w>44)text(g,x+w/2,y+15,(p[1]*100).toFixed(1)+'%',null,'middle',11)
        .setAttribute('fill',sel?'#fff':'#43505c');
      x+=w;
    });
    if(sel)g.appendChild(el('rect',{x:L-2,y:y-2,width:R-L+4,height:26,fill:'none',
      stroke:'#101418','stroke-width':1.2}));
  });
  var by=T+4*rowH+16;
  text(g,L,by,'Pull','axlab','start',10).setAttribute('fill',DC.Pull);
  text(g,L+60,by,'Straightaway','axlab','start',10).setAttribute('fill',DC.Straightaway);
  text(g,L+160,by,'Oppo','axlab','start',10).setAttribute('fill',DC.Oppo);
  text(g,R+14,T+14,'population:','axlab','start',10);
  text(g,R+14,T+28,zlabel,null,'start',12).setAttribute('font-family','var(--mono)');
}

// ================================================================ SCENE 3
function drawZoneShift(){
  var svg=$('#zoneshift');clear(svg);var g=el('g');svg.appendChild(g);
  var prof=D.prof, cur=prof.filter(function(p){return p.game_year===M.seasons[3];})[0];
  var base=prof.filter(function(p){return p.game_year!==M.seasons[3];});
  var wsum=base.reduce(function(a,b){return a+b.n_zone_known;},0);
  var cells=[1,2,3,4,5,6,7,8,9,11,12,13,14];
  var LBL={1:'1 up-in',2:'2 up-mid',3:'3 up-away',4:'4 mid-in',5:'5 middle',6:'6 mid-away',
           7:'7 low-in',8:'8 low-mid',9:'9 low-away',11:'11 up & in (out)',12:'12 up & away (out)',
           13:'13 down & in (out)',14:'14 down & away (out)'};
  var rows=cells.map(function(c){
    var k='z'+c+'_share';
    var pooled=base.reduce(function(a,b){return a+b[k]*b.n_zone_known;},0)/wsum;
    return {c:c,d:(cur[k]-pooled)*100,pooled:pooled,cur:cur[k]};
  }).sort(function(a,b){return b.d-a.d;});
  var mx=Math.max.apply(null,rows.map(function(r){return Math.abs(r.d);}))*1.15;
  var L=126,R=440,MID=L+(R-L)*0.5,T=18,h=20;
  g.appendChild(el('line',{x1:MID,x2:MID,y1:T-6,y2:T+rows.length*h+2,'class':'ax'}));
  rows.forEach(function(r,i){
    var y=T+i*h, w=Math.abs(r.d)/mx*(R-MID);
    var outz=r.c>=11;
    g.appendChild(el('rect',{x:r.d<0?MID-w:MID,y:y,width:w,height:h-6,
      fill:outz?DC.Oppo:'#aab3bd','fill-opacity':outz?.88:.6}));
    text(g,L-6,y+h-9,LBL[r.c],'axlab','end',9.5);
    text(g,r.d<0?MID-w-5:MID+w+5,y+h-9,(r.d>0?'+':'')+r.d.toFixed(1),'axlab',r.d<0?'end':'start',9.5);
  });
  text(g,MID,T+rows.length*h+16,'percentage points of all located pitches','axtitle');
  text(g,MID,T+rows.length*h+31,'navy = out-of-zone quadrant · grey = in-zone cell','axlab');
}

function drawStab(){
  var tb=$('#stabTable tbody');clear(tb);
  D.stability.forEach(function(r){
    var tr=document.createElement('tr');
    var nm=r.test.replace(/^PM-1[abc] /,'');
    var sig=r.p_value<0.05;
    [[nm,0],[r.n_2026,1],[r.chi2.toFixed(1),1],[r.dof,1],
     [r.p_text!=null?r.p_text:(r.p_value<0.001?r.p_value.toExponential(1):r.p_value.toFixed(3)),1],
     [(r.total_variation_distance*100).toFixed(1)+'pp',1]].forEach(function(c,i){
      var td=document.createElement('td');if(i>0)td.className='num';
      td.textContent=c[0];tr.appendChild(td);});
    if(!sig)tr.style.background='#f2f8f4';
    tb.appendChild(tr);});
  var iz=D.stability.filter(function(r){return r.test.indexOf('PM-1b')===0;})[0];
  var oz=D.stability.filter(function(r){return r.test.indexOf('PM-1c')===0;})[0];
  $('#pmNote').innerHTML='<b>The two halves disagree, and that is the finding.</b> '+
    'Inside the zone the attack plan is statistically indistinguishable from 2023–25 '+
    '(&chi;&sup2;&nbsp;='+iz.chi2.toFixed(1)+', p&nbsp;='+iz.p_text+', '+
    (iz.total_variation_distance*100).toFixed(1)+'pp of probability mass moved) — yet in-zone batted-ball '+
    'direction moved 7.4 points. Outside the zone the attack changed sharply '+
    '(&chi;&sup2;&nbsp;='+oz.chi2.toFixed(1)+', p&nbsp;='+oz.p_text+
    ', down-and-away −3.7pp, up-and-in +4.2pp) — yet his out-of-zone direction did not move at all. '+
    '<b>The premise looked at the population where the pitchers changed and he did not.</b> '+
    'Caveat: PM‑1 tests location only. It says nothing about pitch mix, sequencing, velocity, or who was on the mound.';
}

// ================================================================ SCENE 4
function drawZ(){
  var svg=$('#zchart');clear(svg);var g=el('g');svg.appendChild(g);
  var rows=[];
  D.sig.forEach(function(r){
    if(r.metric==='straightaway')return;
    rows.push({lab:(r.zone==='in_zone'?'In zone':'Out of zone')+' · '+r.metric,
      z:r.z,n:r.n_2026,r26:r.rate_2026,rb:r.rate_2023_25,
      key:r.zone+'-'+r.metric});
  });
  var L=176,R=712,T=24,h=44,mx=3.2;
  function sx(z){return L+(z+mx)/(2*mx)*(R-L);}
  [-2.5,-1.5,0,1.5,2.5].forEach(function(v){
    var x=sx(v);
    g.appendChild(el('line',{x1:x,x2:x,y1:T-8,y2:T+rows.length*h-6,
      stroke:v===0?'var(--line)':'var(--line2)','stroke-width':v===0?1.4:1,
      'stroke-dasharray':v===0?'':'3 3'}));
    text(g,x,T+rows.length*h+10,(v>0?'+':'')+v,'axlab');
  });
  text(g,(L+R)/2,T+rows.length*h+30,'pooled two-proportion z · 2026 vs pooled 2023–2025 (ST-1 band)','axtitle');
  rows.forEach(function(r,i){
    var y=T+i*h, x=sx(r.z), b=band(r.z);
    g.appendChild(el('line',{x1:sx(0),x2:x,y1:y+9,y2:y+9,
      stroke:r.z<0?DC.Pull:DC.Oppo,'stroke-width':3,'stroke-opacity':.75}));
    g.appendChild(el('circle',{cx:x,cy:y+9,r:6,fill:r.z<0?DC.Pull:DC.Oppo}));
    text(g,L-14,y+6,r.lab,null,'end',12.5).setAttribute('font-weight','600');
    text(g,L-14,y+20,pct(r.r26)+' vs '+pct(r.rb)+'  ·  n='+r.n,'axlab','end',10);
    var t=text(g,R+12,y+13,'z '+r.z.toFixed(2)+'  '+b[1],null,'start',11);
    t.setAttribute('font-family','var(--mono)');
    t.setAttribute('fill',b[0]==='clears'?'#b3101f':(b[0]==='mod'?'#8a5008':'#77848f'));
  });
}

function drawCells(){
  var tb=$('#cellTable tbody');clear(tb);
  var order=['Down','Middle','Up','Inside','Middle','Outside'];
  var rows=D.cells.filter(function(c){
    return c.metric==='pull'&&(c.dimension==='zone_row'||c.dimension==='zone_col');});
  rows.sort(function(a,b){return a.dimension===b.dimension? a.z-b.z : (a.dimension<b.dimension?-1:1);});
  rows.forEach(function(r){
    var tr=document.createElement('tr');
    var lab=(r.dimension==='zone_row'?'Zone row · ':'Zone column · ')+r.slice;
    var b=band(r.z);
    [[lab,0],[pct(r.rate_2026),1],[pct(r.rate_2023_25),1],
     [(r.diff*100).toFixed(1),1],[r.z.toFixed(2),1],[r.n_2026,1]].forEach(function(c,i){
      var td=document.createElement('td');if(i>0)td.className='num';
      if(i===4){var sp=document.createElement('span');sp.className='band '+b[0];
        sp.textContent=c[0];td.appendChild(sp);}else td.textContent=c[0];
      tr.appendChild(td);});
    tb.appendChild(tr);});
}

function drawWaterfall(){
  var svg=$('#waterfall');clear(svg);var g=el('g');svg.appendChild(g);
  var d=D.decomp.filter(function(x){return x.population==='in-zone BIP';})[0];
  var L=64,W=340,T=18,H=130,base=d.baseline_slg_bip;
  var lo=Math.min(d.current_slg_bip,base)-0.03, hi=Math.max(d.current_slg_bip,base)+0.02;
  function sy(v){return T+H-(v-lo)/(hi-lo)*H;}
  var steps=[
    {lab:'2023–25',v0:0,v1:base,abs:true,col:'#aab3bd'},
    {lab:'mix',v0:base,v1:base+d.mix_effect,col:DC.Oppo},
    {lab:'rate',v0:base+d.mix_effect,v1:base+d.mix_effect+d.rate_effect,col:DC.Pull},
    {lab:'inter.',v0:base+d.mix_effect+d.rate_effect,v1:d.current_slg_bip,col:'#c3cad3'},
    {lab:'2026',v0:0,v1:d.current_slg_bip,abs:true,col:'#43505c'}
  ];
  var bw=W/steps.length-12;
  steps.forEach(function(s,i){
    var x=L+i*(W/steps.length);
    var y0=s.abs?sy(lo):sy(s.v0), y1=sy(s.v1);
    var top=Math.min(y0,y1), hgt=Math.max(2,Math.abs(y1-y0));
    if(s.abs){top=sy(s.v1);hgt=T+H-top;}
    g.appendChild(el('rect',{x:x,y:top,width:bw,height:hgt,fill:s.col,'fill-opacity':.85}));
    text(g,x+bw/2,T+H+15,s.lab,'axlab');
    var val=s.abs?trim3(s.v1):((s.v1-s.v0>=0?'+':'')+(s.v1-s.v0).toFixed(3).replace('0.','.'));
    text(g,x+bw/2,top-5,val,'axlab','middle',10);
    if(i<steps.length-1&&!steps[i+1].abs)
      g.appendChild(el('line',{x1:x+bw,x2:x+W/steps.length,y1:y1,y2:y1,
        stroke:'var(--line)','stroke-dasharray':'2 2'}));
  });
  text(g,L+W/2,T+H+34,'total bases per in-zone ball in play','axtitle');
  var s1=text(g,L,T-4,'mix explains '+(d.mix_share_of_gap*100).toFixed(0)+'% · rate explains '+
    (d.rate_share_of_gap*100).toFixed(0)+'%',null,'start',11);
  s1.setAttribute('fill','#43505c');s1.setAttribute('font-family','var(--mono)');
}

function drawVal(){
  var svg=$('#valchart');clear(svg);var g=el('g');svg.appendChild(g);
  var L=90,R=800,T=26,H=170;
  var vals=D.value_iz;
  var mx=Math.max.apply(null,vals.map(function(v){return v.slg_bip;}))*1.12;
  function sy(v){return T+H-v/mx*H;}
  [0,.2,.4,.6,.8].forEach(function(v){
    if(v>mx)return;var y=sy(v);
    g.appendChild(el('line',{x1:L,x2:R,y1:y,y2:y,'class':'gridline'}));
    text(g,L-8,y+3.5,trim3(v),'axlab','end');});
  var gw=(R-L)/SEASONS.length;
  SEASONS.forEach(function(yr,i){
    var gx=L+i*gw;
    text(g,gx+gw/2,T+H+18,yr,null,'middle',12.5)
      .setAttribute('font-weight',i===S.season?'700':'400');
    DIRS.forEach(function(dir,j){
      var row=vals.filter(function(v){return v.game_year===yr&&v.hit_direction===dir;})[0];
      if(!row)return;
      var bw=gw/4.2, x=gx+gw*0.12+j*(bw+6), y=sy(row.slg_bip);
      g.appendChild(el('rect',{x:x,y:y,width:bw,height:T+H-y,fill:DC[dir],
        'fill-opacity':i===S.season?.92:.42}));
      text(g,x+bw/2,y-5,trim3(row.slg_bip),'axlab','middle',9.5);
      text(g,x+bw/2,T+H+31,'n='+row.n,'axlab','middle',8.5);
    });
  });
  text(g,R+10,T+12,'Pull','axlab','start',10).setAttribute('fill',DC.Pull);
  text(g,R+10,T+26,'Straight','axlab','start',10).setAttribute('fill',DC.Straightaway);
  text(g,R+10,T+40,'Oppo','axlab','start',10).setAttribute('fill',DC.Oppo);
  var yt=text(g,0,0,'total bases / BIP','axtitle');
  yt.setAttribute('transform','translate(20,'+(T+H/2)+') rotate(-90)');
}

// ================================================================ GOV
function drawGov(){
  var kv=$('#kvPos');clear(kv);
  var prof2026=D.prof.filter(function(p){return p.game_year===2026;})[0];
  var rows=[
    ['Source','data/phillies/phils_{2023..2026}.parquet — the repo\'s governed cache'],
    ['Freshness','max game_date '+M.as_of],
    ['Entity lock','batter == '+M.mlbam+' (confirmed by filter, not by name match)'],
    ['Grain','pitch-level; balls in play are type == \'X\''],
    ['Scope','regular season only (game_type == \'R\'), for cross-year rate comparability'],
    ['Volume','1,832 balls in play · 9,485 pitches · 2023–2026'],
    ['Coordinates','hc_x/hc_y → loc_x/loc_y via the governed derive_loc(); coordinate-convention assertion passes (median loc_x for Pull &lt; 0)'],
    ['Zone authority','Statcast zone; zone &lt; 10 is in-zone; NULL zone excluded from both populations'],
    ['Handedness','stand == \'R\' on 100% of rows — the L branch is implemented but never exercised'],
    ['Untracked BIP','1 of 1,832 rows has NULL launch_speed (affects hard-hit rate only; never imputed)'],
    ['Context pool','65 Phillies batter player-seasons at or above the 50-PA repo floor'],
    ['Verification','every figure on this page recomputed from the shipped extracts by dp_uc42a_verification.py']
  ];
  rows.forEach(function(r){
    var dt=document.createElement('dt');dt.textContent=r[0];
    var dd=document.createElement('dd');dd.innerHTML=r[1];
    kv.appendChild(dt);kv.appendChild(dd);});

  var tb=$('#defTable tbody');clear(tb);
  D.defects.forEach(function(d){
    var tr=document.createElement('tr');
    [d.defect,d.exposure_metric,d.value,d.affects_this_build?'yes — disclosed':'no'].forEach(function(c,i){
      var td=document.createElement('td');if(i===2)td.className='num';
      if(i<2)td.style.whiteSpace='normal';
      td.textContent=c;tr.appendChild(td);});
    tb.appendChild(tr);});
}

// ================================================================ wiring
function renderScene1(){drawCtx();drawTTSeasons();}
function renderScene2(){drawLinked();drawMix();drawVal();}
function renderAll(){renderScene1();renderScene2();drawZoneShift();drawStab();drawZ();
  drawCells();drawWaterfall();drawGov();}

function setSeason(i,src){
  S.season=Math.max(0,Math.min(3,i));
  $('#s1').value=S.season;$('#s2').value=S.season;
  $('#s1lab').textContent=SEASONS[S.season];$('#s2lab').textContent=SEASONS[S.season];
  renderScene1();renderScene2();
}
var timer=null;
function togglePlay(which){
  var on = which===1 ? !S.playing1 : !S.playing2;
  S.playing1=S.playing2=false;
  if(which===1)S.playing1=on; else S.playing2=on;
  $('#p1').setAttribute('aria-pressed',S.playing1);
  $('#p2').setAttribute('aria-pressed',S.playing2);
  $('#p1').textContent=S.playing1?'❚❚ Pause':'▶ Play seasons';
  $('#p2').textContent=S.playing2?'❚❚ Pause':'▶ Play seasons';
  if(timer){clearInterval(timer);timer=null;}
  if(on){timer=setInterval(function(){setSeason((S.season+1)%4);},1500);}
}
$('#p1').addEventListener('click',function(){togglePlay(1);});
$('#p2').addEventListener('click',function(){togglePlay(2);});
$('#s1').addEventListener('input',function(){setSeason(+this.value);});
$('#s2').addEventListener('input',function(){setSeason(+this.value);});
document.querySelectorAll('#metric button').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('#metric button').forEach(function(x){x.setAttribute('aria-pressed','false');});
    b.setAttribute('aria-pressed','true');S.metric=b.dataset.m;drawCtx();});});
document.querySelectorAll('#zoneSeg button').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('#zoneSeg button').forEach(function(x){x.setAttribute('aria-pressed','false');});
    b.setAttribute('aria-pressed','true');S.zone=b.dataset.z;renderScene2();});});
$('#dirSel').addEventListener('change',function(){S.dir=this.value;drawLinked();});
$('#thSel').addEventListener('change',function(){S.throws=this.value;drawLinked();});
$('#showAll').addEventListener('change',function(){S.showAll=this.checked;drawLinked();});

$('#asof').textContent=M.as_of;
Array.prototype.forEach.call(document.querySelectorAll('.asof2'),function(n){n.textContent=M.as_of;});
D.value_iz=D.value_iz||[];
renderAll();
})();
