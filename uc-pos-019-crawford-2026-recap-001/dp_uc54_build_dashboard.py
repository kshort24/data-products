"""dp_uc54_build_dashboard.py - the 7-chapter dashboard (repo copy + Artifact body variant).
Reads only out/dp_uc54_* (figure JSON, CSVs, headlines.json, figure_specs.json) and dp_uc54_narrative; computes nothing.
Plotly.js via phillies_dp.render.plotly_script_tag() (CDN-pinned; never inlined). Shell: house dashboard_shell.md."""
from __future__ import annotations
import html, json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc54_narrative as N
from phillies_dp.render import plotly_script_tag

ROOT = Path(__file__).resolve().parent; OUT = ROOT / "out"
H, f3, pc, ordn = N.H, N.f3, N.pc, N.ordn
esc = html.escape
WIDE = {"f1_cumulative_slash", "f4_profile", "f7_chase_map_rhp", "f8_rhp_breaking", "f9_spray_rhp_breaking", "f10_centre_field", "f5_attack_regions", "f6_cumulative_gb_hh"}
TALL = {"f2_rolling_form", "f3_tr1_ledger", "f9_spray_rhp_breaking"}


def fig(k):
    j = json.loads((OUT / f"dp_uc54_{k}.json").read_text())
    j["layout"].pop("template", None)          # themed in the page
    return j


def clean(o):
    if isinstance(o, float):
        return None if (math.isnan(o) or math.isinf(o)) else o
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return o


keys = [k for _, _, _, _, figs, _ in N.CH for k in figs]
payload = {"figs": {k: fig(k) for k in keys}}
PAYLOAD_JS = json.dumps(clean(payload), allow_nan=False).replace("</", "<\\/")


def figbox(k):
    s = N.SPECS[k]
    cls = "plot" + (" tall" if k in TALL else "")
    inner = f'<div class="{cls}" id="{k}" role="img" aria-label="{esc(s["title"])}"></div>'
    if k in WIDE:
        inner = f'<div class="scroll"><div class="wide">{inner}</div></div>'
    return (f'<figure class="fig"><figcaption><h3>{esc(s["title"])}</h3><p class="sub">{esc(s["subtitle"])}</p></figcaption>{inner}'
            f'<p class="rcpt">Receipts: {", ".join("dp_uc54_" + x for x in s["source"])}</p></figure>')


chapters = []
for i, (anc, q, ttl, lede, figs, _) in enumerate(N.CH, 1):
    chapters.append(f'<section class="ch" id="{anc}"><div class="chno"><span class="q">{q}</span> Chapter {i}</div><h2>{esc(ttl)}</h2>'
                    f'<p class="lede">{lede}</p>{"".join(figbox(k) for k in figs)}</section>')
nav = "".join(f'<a href="#{a}"><span class="q">{q}</span>{esc(t)}</a>' for a, q, t, *_ in N.CH) + '<a href="#notebook">Your notebook</a><a href="#products">Products</a>'
CX, X, CC = N.CX, N.X, N.CC
tiles = [
    (N.SLASH, "Slash line", f"{int(H['plate_apps'])} PA · wOBA {f3(H['woba'])}, {ordn(CX['rank']['woba'])} of {CX['n']} Phillies CF seasons"),
    (pc(H["chase_rate"]), "Chase rate", f"better than {N.better('chase_rate')}% of {H['pool_n']} Phillies hitter-seasons; whiff better than {N.better('whiff_rate')}%"),
    (pc(H["gb_rate"]), "Ground-ball rate", f"launch angle {H['mean_la']:.1f}°, {ordn(H['la_rank_low'])}-lowest of {H['profile']['mean_la']['n']}"),
    (f"{X['oae']:+.1f}", "CF outs vs expected", f"XO-2 proxy, {ordn(X['ctx_rank'])} of {X['ctx_n']} Phillies CF seasons · −8 OAA on record"),
]
tile_html = "".join(f'<div class="tile"><div class="big">{esc(a)}</div><div class="lbl">{esc(b)}</div><div class="note">{esc(c)}</div></div>' for a, b, c in tiles)
grade_cls = {"REPRODUCED": "g-ok", "SUPPORTED": "g-ok", "PARTLY": "g-mid", "NOT SUPPORTED": "g-no"}
hp_rows = "".join(f'<tr><td class="mono">{k}</td><td>{esc(v["claim"])}</td><td class="mono">{esc(v["client"])}</td><td class="mono">{esc(v["governed"])}</td>'
                  f'<td><span class="pill {grade_cls.get(v["grade"], "")}">{esc(v["grade"])}</span></td><td class="ev">{esc(v["evidence"])}</td></tr>' for k, v in H["hp"].items())
gc = H["hp_grade_counts"]
products = [("P1", "PDF recap report", "Built", "Ten pages, nine sections: the whole story for the front office and coaching staff."),
            ("P2", "This dashboard", "Built", "Seven chapters keyed to your six questions, with hover on every chart."),
            ("P3", "Player development card", "Folded in", "Scoped to his own approach and contact numbers per the uc-pos-011 privacy ruling; lives in chapters 4 and 5, not as a separate form."),
            ("P4", "2027 projection", "Not bid", "There is no projection model in the house. TR-1 and CC-1 are the governed substitutes."),
            ("P5", "Video: chases and CF misreads", "Priced, not built", "Clip tooling exists (kr3_clip_acquisition.py). About 40k tokens for v1.1.")]
prod_html = "".join(f'<div class="prod"><div class="pid">{a}</div><div><b>{esc(b)}</b> <span class="pill {"g-ok" if c == "Built" else "g-mid"}">{esc(c)}</span><p>{esc(d)}</p></div></div>' for a, b, c, d in products)
lin = H["lineage"]
read_first = "".join(f"<li>{x}</li>" for x in N.READ_FIRST)
bottom = "".join(f"<li>{x}</li>" for x in N.BOTTOM)
caveats = "".join(f"<li>{esc(x)}</li>" for x in N.CAVEATS)

CSS = """
/* Layout: one 1120px reading column; sticky chapter rail; figures as the only cards. Scorebook feel: condensed display numerals, tabular figures. */
:root{--bg:#f7f6f2;--surface:#ffffff;--ink:#1b1b1b;--ink2:#4a4f5c;--muted:#6b7080;--rule:#e3e6ec;--rule2:#D9D9D9;--red:#E81828;--navy:#002D72;
--chip:#f1f3f6;--warn:#fff4f5;--field:#EEF1F5;--dirt:#E9DCC0;--grass:#7FA36B;--ok:#1A7F55;--mid:#9A6A00;
--display:"Barlow Condensed","Arial Narrow",Arial,sans-serif;--body:"Source Sans 3","Segoe UI",Arial,sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121315;--surface:#1b1d21;--ink:#ececec;--ink2:#c5c8d0;--muted:#9aa0ad;--rule:#2e3138;
--rule2:#3a3e46;--navy:#8FB0F0;--chip:#262a31;--warn:#2a1a1c;--field:#23272e;--dirt:#3b3428;--grass:#2f4a2a;--ok:#5fd09a;--mid:#e0b04a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121315;--surface:#1b1d21;--ink:#ececec;--ink2:#c5c8d0;--muted:#9aa0ad;--rule:#2e3138;--rule2:#3a3e46;--navy:#8FB0F0;
--chip:#262a31;--warn:#2a1a1c;--field:#23272e;--dirt:#3b3428;--grass:#2f4a2a;--ok:#5fd09a;--mid:#e0b04a;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:16px/1.55 var(--body);margin:0}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
.wrap{max-width:1120px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 48px}
header.top{border-top:6px solid var(--red);padding-block:22px 10px}
.kicker{font:600 13px/1.3 var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font:700 52px/1.0 var(--display);color:var(--navy);margin:8px 0 6px;text-wrap:balance;letter-spacing:.005em}
h1 span{color:var(--red)}
.dek{font-size:19px;color:var(--ink2);max-width:62ch;margin:0 0 12px}
.bar{display:flex;gap:8px;flex-wrap:wrap}
.bar button{font:600 13px var(--body);border:1px solid var(--rule);background:var(--surface);color:var(--ink);padding:6px 12px;border-radius:999px;cursor:pointer}
.bar button[aria-pressed="true"]{background:var(--navy);color:var(--surface);border-color:var(--navy)}
button:focus-visible,a:focus-visible{outline:2px solid var(--red);outline-offset:2px}
nav.toc{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);display:flex;gap:4px;overflow-x:auto;padding-block:10px;border-bottom:1px solid var(--rule);margin-bottom:18px;scrollbar-width:thin}
nav.toc a{white-space:nowrap;text-decoration:none;color:var(--ink2);font:600 14px var(--body);padding:5px 10px;border-radius:6px;display:flex;gap:6px;align-items:center}
nav.toc a.on{background:var(--chip);color:var(--ink)}
.q{font:700 12px var(--mono);color:var(--red);letter-spacing:.02em}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:6px 0 18px}
.tile{border-top:3px solid var(--navy);padding-top:8px;min-width:0}
.tile .big{font:700 40px/1 var(--display);color:var(--ink);font-variant-numeric:tabular-nums}
.tile .lbl{font:700 12px var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--red);margin-top:4px}
.tile .note{font-size:14px;color:var(--muted)}
.warn{background:var(--warn);border-left:3px solid var(--red);padding:10px 16px;font-size:14.5px;margin-bottom:22px}
.warn ul,.bl ol{margin:6px 0;padding-left:20px}.warn li,.bl li{margin:4px 0}
.bl{max-width:78ch}.bl h2{margin-top:0}
code,.mono{font-family:var(--mono);font-size:.86em}
section.ch{padding-block:22px 6px;border-top:1px solid var(--rule);scroll-margin-top:60px}
.chno{font:600 13px var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);display:flex;gap:8px;align-items:center}
h2{font:700 34px/1.1 var(--display);color:var(--navy);margin:4px 0 8px;text-wrap:balance}
.lede{max-width:72ch;color:var(--ink);margin:0 0 14px}
figure.fig{margin:0 0 18px;background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:14px 14px 8px;min-width:0}
figcaption h3{font:700 19px/1.25 var(--body);margin:0 0 4px;text-wrap:balance}
.sub{font-size:14px;color:var(--muted);margin:0 0 8px;max-width:95ch}
.scroll{overflow-x:auto}.wide{min-width:820px}
.plot{height:480px}.plot.tall{height:600px}
.rcpt{font:12px var(--mono);color:var(--muted);margin:4px 0 0}
.tbl{overflow-x:auto;margin:8px 0 16px}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th{background:var(--navy);color:var(--surface);text-align:left;padding:6px 8px;font-weight:600}
td{border-bottom:1px solid var(--rule);padding:6px 8px;vertical-align:top}td.ev{color:var(--muted);font-size:13px;min-width:260px}
.pill{display:inline-block;font:700 11px var(--body);letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:999px;border:1px solid currentColor;white-space:nowrap}
.g-ok{color:var(--ok)}.g-mid{color:var(--mid)}.g-no{color:var(--red)}
.prods{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.prod{display:flex;gap:12px;border-top:1px solid var(--rule);padding-top:10px}.prod p{margin:4px 0 0;color:var(--ink2);font-size:14.5px}
.pid{font:700 22px var(--display);color:var(--red);min-width:30px}
footer{margin-top:28px;border-top:1px solid var(--rule);padding-top:12px;font:12px/1.6 var(--mono);color:var(--muted);overflow-wrap:anywhere}
@media (max-width:820px){h1{font-size:38px}.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}.plot{height:420px}.plot.tall{height:520px}h2{font-size:28px}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""

JS = r"""
(function(){
const P=JSON.parse(document.getElementById('payload').textContent);
const root=document.documentElement;
const tok=n=>getComputedStyle(root).getPropertyValue(n).trim();
function dark(){const t=root.dataset.theme;return t?t==='dark':matchMedia('(prefers-color-scheme: dark)').matches;}
const MAP={'#1b1b1b':'--ink','#5b6170':'--muted','#ffffff':'--surface','#eef1f5':'--field','#d9d9d9':'--rule2','#e9dcc0':'--dirt','#7fa36b':'--grass','#002d72':'--navy','#c9a66b':'--rule2'};
function remap(o){
  if(Array.isArray(o))return o.map(remap);
  if(o&&typeof o==='object'){const r={};for(const k in o)r[k]=remap(o[k]);return r;}
  if(typeof o==='string'){const t=MAP[o.toLowerCase()];if(t)return tok(t);}
  return o;
}
function themed(f){
  const d=dark();const data=d?remap(f.data):f.data;let L=JSON.parse(JSON.stringify(f.layout));if(d)L=remap(L);
  delete L.width;delete L.height;delete L.title;L.autosize=true;
  const hasSub=(L.annotations||[]).some(a=>a.xref==='paper'&&a.yref==='paper'&&a.y>=1);
  L.margin=Object.assign({},L.margin||{},{t:hasSub?44:20});
  L.paper_bgcolor=tok('--surface');L.plot_bgcolor=tok('--surface');
  L.font=Object.assign({},L.font||{},{family:'Source Sans 3, Segoe UI, Arial, sans-serif',color:tok('--ink')});
  for(const k in L){if(/^[xy]axis/.test(k)){L[k].gridcolor=tok('--rule');L[k].linecolor=tok('--rule');L[k].zerolinecolor=tok('--rule2');}}
  if(L.legend)L.legend.font=Object.assign({},L.legend.font||{},{color:tok('--ink')});
  return {data,layout:L};
}
const drawn=new Set();
function draw(id){const el=document.getElementById(id);if(!el||!window.Plotly)return;const t=themed(P.figs[id]);
  Plotly.react(el,t.data,t.layout,{responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d']});drawn.add(id);}
function drawAll(){Object.keys(P.figs).forEach(draw);}
function setTheme(v){try{localStorage.setItem('uc54-theme',v)}catch(e){}
  if(v==='auto')delete root.dataset.theme;else root.dataset.theme=v;
  document.querySelectorAll('.bar button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===v)));drawAll();}
let saved='auto';try{saved=localStorage.getItem('uc54-theme')||'auto'}catch(e){}
document.querySelectorAll('.bar button').forEach(b=>b.addEventListener('click',()=>setTheme(b.dataset.v)));
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{if(!root.dataset.theme)drawAll();});
setTheme(saved);
const links=[...document.querySelectorAll('nav.toc a')];
const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){links.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id));}})},{rootMargin:'-40% 0px -55% 0px'});
document.querySelectorAll('section.ch').forEach(s=>io.observe(s));
})();
"""

TITLE = "Crawford 2026 Recap"
HEAD = (f"<title>{TITLE}</title>\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n"
        "<link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Mono:wght@400;700&family=Source+Sans+3:wght@400;600;700&display=swap\">\n"
        f"<style>{CSS}</style>\n{plotly_script_tag()}\n")
BODY = f"""<div class="wrap">
<header class="top">
 <div class="kicker">Phillies Offense · uc-pos-019 · dp_uc54 · regular season, data through {H['anchor']}</div>
 <h1>Justin Crawford, 2026: exactly as <span>advertised</span></h1>
 <p class="dek">A rookie centre fielder who made contact on everything, chased too much, hit the ball into the ground, and gave back outs in centre. The profile the scouts drew, start to finish.</p>
 <div class="bar" role="group" aria-label="Theme"><button data-v="auto" aria-pressed="true">Match my system</button><button data-v="light" aria-pressed="false">Brand light</button><button data-v="dark" aria-pressed="false">Notebook dark</button></div>
</header>
<nav class="toc" aria-label="Chapters">{nav}</nav>
<div class="tiles">{tile_html}</div>
<div class="warn"><b>Read this first.</b><ul>{read_first}</ul></div>
<section class="bl"><h2>Bottom line</h2><ol>{bottom}</ol></section>
{''.join(chapters)}
<section class="ch" id="notebook"><div class="chno">Appendix</div><h2>Your notebook, graded</h2>
<p class="lede">Each claim from your notebook was reproduced on your own frame (<code>jc</code>, with its spring and Wild Card rows) using your own functions, then checked against the governed regular-season build. Grades: {', '.join(f'{v} {k.lower()}' for k, v in gc.items())}.</p>
<div class="tbl"><table><thead><tr><th>#</th><th>Your claim</th><th>Your frame</th><th>Governed</th><th>Verdict</th><th>Evidence</th></tr></thead><tbody>{hp_rows}</tbody></table></div>
<h3>Candid caveats</h3><ul>{caveats}</ul></section>
<section class="ch" id="products"><div class="chno">Appendix</div><h2>Five ways to tell this story</h2><div class="prods">{prod_html}</div></section>
<footer>uc-pos-019 · dp_uc54 v1.0.0 · kernel dp_uc54_kernel.py → dp_uc40_kernel.py {lin['dp_uc40_kernel.py']} · dp_uc34_kernel.py {lin['dp_uc34_kernel.py']} · dp_uc53_kernel.py {lin['dp_uc53_kernel.py']} · cumulative_metric.py {lin['cumulative_metric.py']} · receipts out/dp_uc54_* · governance trail 00–07 in this folder · carry-ins: Wikipedia; 97.5 The Fanatic (2026-10-14); Philadelphia Inquirer (2026-06-05)</footer>
</div>
<script id="payload" type="application/json">{PAYLOAD_JS}</script>
<script>{JS}</script>
"""
full = f"<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n{HEAD}</head><body>\n{BODY}</body></html>\n"
(ROOT / "dp_uc54_crawford_2026_dashboard.html").write_text(full, encoding="utf-8")
(ROOT / "dp_uc54_crawford_2026_dashboard_artifact.html").write_text(HEAD + BODY, encoding="utf-8")
assert "NaN" not in PAYLOAD_JS and "plotly.min.js" not in full[:5000]
print("dashboard bytes", len(full), "chapters", len(N.CH), "figs", len(keys))
