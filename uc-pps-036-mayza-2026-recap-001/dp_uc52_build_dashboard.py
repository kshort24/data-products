"""dp_uc52_build_dashboard.py — UC #52 dashboard (house shell). Reads only out/dp_uc52_* receipts through
dp_uc52_narrative; computes nothing published as a KPI. Writes the repo copy (full document) and the Artifact body variant."""
from __future__ import annotations
import html, json, math, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc52_narrative as N
from phillies_dp.render import plotly_script_tag

ROOT = Path(__file__).resolve().parent; OUT = ROOT / "out"
esc = html.escape
FIG = lambda k: json.loads((OUT / f"dp_uc52_{k}.json").read_text())   # noqa: E731
KEYS = [k for ch in N.CH for k in ch[3]]


def _clean(o):
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)): return None
    if isinstance(o, dict): return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list): return [_clean(v) for v in o]
    return o


def figbox(k, cls=""):
    s = N.SPECS[k]
    return f'<figure class="fig"><h3>{esc(s["title"])}</h3><p class="sub">{esc(s["subtitle"])}</p><div class="plot {cls}" id="{k}" role="img" aria-label="{esc(s["title"])}"></div></figure>'


def table(df, cols, heads, fmt, hl=None):
    th = "".join(f"<th>{h}</th>" for h in heads)
    rows = []
    for _, r in df.iterrows():
        cls = ' class="me"' if hl is not None and hl(r) else ""
        rows.append(f"<tr{cls}>" + "".join(f"<td>{fmt.get(c, str)(r[c])}</td>" for c in cols) + "</tr>")
    return f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


lrp = pd.read_csv(OUT / "dp_uc52_house_lhp_rp.csv").sort_values("woba").reset_index(drop=True)
lrp["rank"] = lrp.index + 1
me = lambda r: r["pitcher"] == 641835 and r["game_year"] == 2026          # noqa: E731
top = pd.concat([lrp.head(5), lrp[lrp.apply(me, axis=1)]]).drop_duplicates(subset=["pitcher", "game_year"])
house_tbl = table(top, ["rank", "player_name", "game_year", "plate_apps", "woba", "ops", "bbrate", "rc_per_gm"],
                  ["#", "Pitcher", "Season", "PA", "wOBA", "OPS", "BB%", "Runs on watch / G"],
                  {"woba": N.f3, "ops": N.f3, "bbrate": N.pc, "rc_per_gm": lambda x: f"{x:.2f}", "rank": lambda x: f"{int(x)}"}, hl=me)
house_tbl = f'<p class="cap">Top five of {N.HL["n"]} Phillies LHP relief seasons by wOBA allowed (2015-26, 100+ PA, starts ≤ 20% of games), plus Mayza 2026.</p>' + house_tbl
pl = pd.read_csv(OUT / "dp_uc52_platoon_2026.csv"); pl["side"] = pl.stand.map({"L": "vs LHB", "R": "vs RHB"})
xwc = [c for c in pl.columns if c.startswith("xwoba")][0]
plat_tbl = table(pl, ["side", "plate_apps", "woba", "woba_sc", xwc, "krate", "bbrate", "hard_hit_rate", "barrel_rate", "quick_ab_rate"],
                 ["Split", "PA", "wOBA (house)", "wOBA (Statcast)", "xwOBA", "K%", "BB%", "Hard-hit", "Barrel", "Quick-AB"],
                 {"woba": N.f3, "woba_sc": N.f3, xwc: N.f3, "krate": N.pc, "bbrate": N.pc, "hard_hit_rate": N.pc, "barrel_rate": N.pc, "quick_ab_rate": N.pc})
EXTRA = {"house": house_tbl, "platoon": plat_tbl}

chapters = []
for i, (anc, ttl, lede, figs, extra) in enumerate(N.CH, 1):
    body = "".join(figbox(k) for k in figs) + (EXTRA.get(extra, "") if extra else "")
    chapters.append(f'<section class="ch" id="{anc}"><div class="chno">Chapter {i}</div><h2>{esc(ttl)}</h2><p class="lede">{lede}</p>{body}</section>')
GR = {"CONFIRMED": "ok", "PARTLY": "part", "NOT CONFIRMED": "no"}
hp_rows = "".join(f'<tr><td>{r.hp}</td><td>{esc(r.claim)}</td><td><span class="pill {GR[r.grade]}">{r.grade.title()}</span></td>'
                  f'<td>{esc(str(r.governed))}</td><td class="note">{esc(str(r.note)) if str(r.note) != "nan" else ""}</td></tr>' for r in N.HP.itertuples())
hp_tbl = f'<div class="tbl"><table><thead><tr><th>#</th><th>Your claim</th><th>Verdict</th><th>Governed value</th><th>Note</th></tr></thead><tbody>{hp_rows}</tbody></table></div>'
prod = "".join(f'<div class="card"><div class="st {s.lower().replace(" ", "")}">{s}</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for t, s, d in N.PRODUCTS)
nav = "".join(f'<a href="#{c[0]}">{i} · {esc(c[1].split(":")[0])}</a>' for i, c in enumerate(N.CH, 1)) + '<a href="#notebook">Your notebook</a><a href="#products">Products</a>'
tiles = "".join(f'<div class="tile"><div class="big">{v}</div><div class="lab">{esc(l)}</div><div class="note">{esc(n)}</div></div>' for v, l, n in N.TILES)
warn = "".join(f"<li>{x}</li>" for x in N.READ_FIRST)
bottom = "".join(f"<li>{x}</li>" for x in N.BOTTOM)
cav = "".join(f"<li>{esc(x)}</li>" for x in N.CAVEATS)
lin = N.H["lineage"]

CSS = """
/* layout: one reading column (max 1120px) with a sticky chapter rail; house tokens from the uc-house-format shell */
:root{--bg:#fbfaf7;--surface:#fff;--ink:#1b1b1b;--ink2:#4a4f5c;--muted:#6b7080;--rule:#e3e6ec;--red:#E81828;--navy:#002D72;
--blue:#3B6FD8;--chip:#f1f3f6;--warn:#fff4f5;--warnrule:#E81828;--ok:#1f7a4d;--part:#9a6200;--no:#b3261e;--shadow:0 1px 2px rgba(0,0,0,.05);
--font:Arial,"Helvetica Neue",Helvetica,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141414;--surface:#1c1c1c;--ink:#ececec;--ink2:#c5c8d0;--muted:#9aa0ad;
--rule:#2e3138;--navy:#8FB0F0;--chip:#262a31;--warn:#2a1a1c;--ok:#6fd3a0;--part:#f0b860;--no:#ff8a80;--shadow:none;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#141414;--surface:#1c1c1c;--ink:#ececec;--ink2:#c5c8d0;--muted:#9aa0ad;--rule:#2e3138;--navy:#8FB0F0;
--chip:#262a31;--warn:#2a1a1c;--ok:#6fd3a0;--part:#f0b860;--no:#ff8a80;--shadow:none;color-scheme:dark}
:root[data-theme="light"]{color-scheme:light}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:15px;line-height:1.55;margin:0}
.wrap{max-width:1120px;margin:0 auto;padding-block:0 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header.top{border-top:6px solid var(--red);padding-block:22px 10px}
.kicker{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-size:44px;line-height:1.08;color:var(--navy);margin:.25em 0 .2em;text-wrap:balance}
h1 span{color:var(--red)}
.dek{font-size:18px;color:var(--ink2);max-width:62ch;margin:0 0 14px}
.bar{display:flex;gap:8px;flex-wrap:wrap}
.bar button{font:inherit;font-size:13px;border:1px solid var(--rule);background:var(--surface);color:var(--ink);padding:6px 12px;border-radius:999px;cursor:pointer}
.bar button[aria-pressed="true"]{background:var(--navy);border-color:var(--navy);color:var(--surface)}
button:focus-visible,a:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
nav.toc{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--rule);display:flex;gap:4px;
overflow-x:auto;padding-block:8px;margin-block:10px 18px;scrollbar-width:thin}
nav.toc a{white-space:nowrap;font-size:13px;color:var(--ink2);text-decoration:none;padding:4px 10px;border-radius:999px}
nav.toc a.on{background:var(--chip);color:var(--ink);font-weight:bold}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.tile{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;box-shadow:var(--shadow)}
.tile .big{font-size:34px;font-weight:bold;color:var(--navy);font-variant-numeric:tabular-nums}
.tile .lab{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.tile .note{font-size:13px;color:var(--ink2);margin-top:4px}
.warn{background:var(--warn);border-left:4px solid var(--warnrule);padding:12px 16px;margin:18px 0;font-size:14px}
.warn ul,.bl ul{margin:6px 0 0;padding-left:20px}.warn li{margin:3px 0}
.bl{margin:20px 0}.bl h2{margin-bottom:4px}.bl li{margin:8px 0;max-width:78ch}
section.ch{padding-block:22px;border-top:1px solid var(--rule)}
.chno{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--red);font-weight:bold}
h2{font-size:26px;color:var(--navy);margin:.2em 0 .3em;text-wrap:balance}
.lede{max-width:75ch;color:var(--ink2)}
figure.fig{margin:14px 0;background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:14px 14px 6px;box-shadow:var(--shadow);min-width:0}
figure.fig h3{margin:0;font-size:16px;color:var(--ink)}
.sub{margin:4px 0 6px;color:var(--muted);font-size:13px;max-width:95ch}
.plot{height:470px;width:100%}
.cap{font-size:13px;color:var(--muted);margin:14px 0 4px}
.tbl{overflow-x:auto;min-width:0}
table{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums;background:var(--surface)}
th{background:var(--navy);color:var(--surface);text-align:left;padding:7px 9px;font-weight:bold;white-space:nowrap}
td{padding:7px 9px;border-bottom:1px solid var(--rule);vertical-align:top}
tr.me td{font-weight:bold;background:var(--chip)}
td.note{color:var(--muted);font-size:12.5px;min-width:220px}
.pill{display:inline-block;font-size:12px;font-weight:bold;padding:2px 9px;border-radius:999px;border:1px solid currentColor;white-space:nowrap}
.pill.ok{color:var(--ok)}.pill.part{color:var(--part)}.pill.no{color:var(--no)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:12px 14px}
.card h3{margin:4px 0;font-size:15px}.card p{margin:0;font-size:13.5px;color:var(--ink2)}
.st{font-size:11px;letter-spacing:.06em;text-transform:uppercase;font-weight:bold;color:var(--muted)}.st.built{color:var(--ok)}
footer{margin-top:28px;padding-top:12px;border-top:1px solid var(--rule);font-size:12px;color:var(--muted);overflow-wrap:anywhere}
@media (max-width:820px){h1{font-size:32px}.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}.plot{height:400px}.tile .big{font-size:28px}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""

JS = """
(function(){
const P=JSON.parse(document.getElementById('payload').textContent);
const root=document.documentElement, drawn=new Set();
const css=v=>getComputedStyle(root).getPropertyValue(v).trim();
const dark=()=>{const t=root.dataset.theme;if(t)return t==='dark';return matchMedia('(prefers-color-scheme: dark)').matches;};
function themed(fig){
  const f=JSON.parse(JSON.stringify(fig)), L=f.layout, d=dark(), ink=css('--ink'), muted=css('--muted'), rule=css('--rule'), surf=css('--surface');
  delete L.width; delete L.height; L.autosize=true; L.title={text:''};
  L.margin=Object.assign({},L.margin||{},{t:34,l:64,r:20});
  if(d) L.template={layout:{}};
  L.paper_bgcolor=surf; L.plot_bgcolor=surf; L.font=Object.assign({},L.font||{},{color:ink,family:'Arial'});
  Object.keys(L).forEach(k=>{if(/^[xy]axis/.test(k)){const a=L[k];a.gridcolor=rule;a.linecolor=rule;a.zerolinecolor=rule;
    a.tickfont=Object.assign({},a.tickfont||{},{color:muted});if(a.title)a.title.font=Object.assign({},a.title.font||{},{color:ink});}});
  (L.annotations||[]).forEach(a=>{a.font=Object.assign({},a.font||{});const c=a.font.color;
    if(!c||c==='#1b1b1b')a.font.color=ink;else if(c==='#5b6170')a.font.color=muted;});
  (L.shapes||[]).forEach(s=>{if(d&&s.line&&s.line.color==='#D9D9D9')s.line.color=rule;});
  L.legend=Object.assign({},L.legend||{},{font:{color:ink},bgcolor:'rgba(0,0,0,0)'});
  if(d) f.data.forEach(t=>{if(t.textfont&&t.textfont.color==='#1b1b1b')t.textfont.color=ink;
    if(t.marker){if(t.marker.line&&t.marker.line.color==='#ffffff')t.marker.line.color=surf;
      if(t.marker.color==='#D9D9D9')t.marker.color='#4a4f5c';
      if(Array.isArray(t.marker.color))t.marker.color=t.marker.color.map(c=>c==='#D9D9D9'?'#4a4f5c':c);}});
  return f;}
function draw(id){const el=document.getElementById(id);if(!el||!window.Plotly)return;const f=themed(P.figs[id]);
  Plotly.react(el,f.data,f.layout,{responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d']});drawn.add(id);}
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting&&!drawn.has(e.target.id)){draw(e.target.id);io.unobserve(e.target);}}),{rootMargin:'200px'});
document.querySelectorAll('.plot').forEach(el=>io.observe(el));
const btn={auto:document.getElementById('t-auto'),light:document.getElementById('t-light'),dark:document.getElementById('t-dark')};
function setTheme(m,save){if(m==='auto')delete root.dataset.theme;else root.dataset.theme=m;
  Object.entries(btn).forEach(([k,b])=>b&&b.setAttribute('aria-pressed',String(k===m)));
  if(save){try{localStorage.setItem('uc52-theme',m);}catch(e){}}drawn.forEach(draw);}
Object.entries(btn).forEach(([k,b])=>b&&b.addEventListener('click',()=>setTheme(k,true)));
let saved='auto';try{saved=localStorage.getItem('uc52-theme')||'auto';}catch(e){}
setTheme(saved,false);
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{if(!root.dataset.theme)drawn.forEach(draw);});
const links=[...document.querySelectorAll('nav.toc a')];
const so=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){links.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id));}}),{rootMargin:'-40% 0px -55% 0px'});
document.querySelectorAll('section.ch').forEach(s=>so.observe(s));
})();
"""

payload = json.dumps(_clean({"figs": {k: FIG(k) for k in KEYS}}), allow_nan=False).replace("</", "<\\/")
TITLE_TAG = f"<title>{N.TITLE}</title>"
BODY = f"""<div class="wrap">
<header class="top">
 <div class="kicker">{esc(N.KICKER)}</div>
 <h1>The <span>Sheriff</span> of the Phillies Bullpen</h1>
 <p class="dek">{esc(N.SUB)}. {esc(N.DEK)}</p>
 <div class="bar" role="group" aria-label="Theme"><button id="t-auto" aria-pressed="true">Match my system</button><button id="t-light" aria-pressed="false">Brand light</button><button id="t-dark" aria-pressed="false">Notebook dark</button></div>
</header>
<nav class="toc" aria-label="Chapters">{nav}</nav>
<div class="tiles">{tiles}</div>
<div class="warn"><b>Read this first.</b><ul>{warn}</ul></div>
<section class="bl"><h2>Bottom line</h2><ul>{bottom}</ul></section>
{''.join(chapters)}
<section class="ch" id="notebook"><div class="chno">Appendix</div><h2>Your notebook, graded</h2>
<p class="lede">Each claim was reproduced with your own frames and functions first, then restated on the governed frame. Your claims are graded here and never overwritten.</p>{hp_tbl}
<h3>Caveats</h3><ul>{cav}</ul></section>
<section class="ch" id="products"><div class="chno">Appendix</div><h2>Five ways to tell this story</h2><div class="cards">{prod}</div></section>
<footer>uc-pps-036 · dp_uc52 v1.0.0 · kernel dp_uc52_kernel.py imports dp_uc51_kernel.py (sha256 {lin['dp_uc51_kernel.py'][:12]}…) · receipts out/dp_uc52_* ·
governance trail: Agents for Data Products/data-products/uc-pps-036-mayza-2026-recap-001/ · carry-in source: MLB Trade Rumors (mlbtraderumors.com/tim-mayza)</footer>
</div>
<script id="payload" type="application/json">{payload}</script>"""

full = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{TITLE_TAG}<style>{CSS}</style>{plotly_script_tag()}</head><body>{BODY}<script>{JS}</script></body></html>"""
art = f"""{TITLE_TAG}<meta name="claude:viewport-fit-sides" content="cover"><style>{CSS}</style>{plotly_script_tag()}
{BODY}<script>{JS}</script>"""
(ROOT / "dp_uc52_mayza_2026_dashboard.html").write_text(full, encoding="utf-8")
(ROOT / "dp_uc52_mayza_2026_dashboard_artifact.html").write_text(art, encoding="utf-8")
assert "plotly.min.js" in plotly_script_tag() and "NaN" not in payload
print("dashboard written", round(len(full) / 1e6, 2), "MB;", len(KEYS), "figures;", len(N.CH), "chapters")
