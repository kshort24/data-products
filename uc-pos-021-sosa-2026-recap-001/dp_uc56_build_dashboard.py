"""dp_uc56_build_dashboard.py - the recap as an 8-chapter scroll dashboard (figures = out/dp_uc56_f*.json; prose = dp_uc56_narrative).
Writes dp_uc56_sosa_2026_dashboard.html (full document, plotly via phillies_dp.render.plotly_script_tag - never inlined, MLB CLAUDE.md)
and dp_uc56_sosa_2026_dashboard_artifact.html (body-only variant for the Artifact publish; same content, same CDN pin)."""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dp_uc56_narrative as N  # noqa: E402
import dp_uc56_kernel as K  # noqa: E402  (paths only)
from phillies_dp import render  # noqa: E402

OUT = HERE / "out"
H, f3, pc = N.H, N.f3, N.pc
S26 = N.S26
b2h = lambda s: re.sub(r"<b>(.*?)</b>", r"<strong>\1</strong>", s)   # noqa: E731
FIGS = {k: json.loads((OUT / f"dp_uc56_{k}.json").read_text(encoding="utf-8")) for k in N.SPECS}   # J-3: a glob also caught figure_specs.json

CSS = """
:root{
  /* Layout: one reading column, chapter rail on wide screens; scoreboard header, charts on paper cards */
  --bg:#f4f6f9; --surface:#ffffff; --ink:#14213d; --muted:#5a6478; --line:#dde2ea; --red:#E81828; --navy:#002D72; --paper:#ffffff;
  --chip-good:#1a7a4c; --chip-bad:#b3261e; --chip-mid:#8a6d00;
  --display:'Oswald',Impact,'Arial Narrow',sans-serif; --body:'Source Sans 3','Segoe UI',Arial,sans-serif; --mono:'IBM Plex Mono',Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0d1424;--surface:#152038;--ink:#e8ecf3;--muted:#9aa6bd;--line:#26324d;--red:#ff4d5a;--navy:#8fb0ff;--paper:#ffffff;--chip-good:#5fd39a;--chip-bad:#ff8a80;--chip-mid:#f0c75e;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0d1424;--surface:#152038;--ink:#e8ecf3;--muted:#9aa6bd;--line:#26324d;--red:#ff4d5a;--navy:#8fb0ff;--paper:#ffffff;--chip-good:#5fd39a;--chip-bad:#ff8a80;--chip-mid:#f0c75e;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.55;margin:0}
.wrap{max-width:1180px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 64px}
header.board{display:grid;gap:14px;border-top:6px solid var(--red);padding-block:18px 8px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-family:var(--display);font-weight:600;font-size:clamp(34px,6vw,58px);line-height:1.02;margin:0;color:var(--ink);text-wrap:balance;letter-spacing:.01em}
h1 em{font-style:normal;color:var(--red)}
.sub{font-size:18px;color:var(--muted);margin:0;max-width:62ch}
.line{display:flex;flex-wrap:wrap;gap:0;border:1px solid var(--line);background:var(--surface);border-radius:4px;overflow:hidden;width:fit-content;max-width:100%}
.line div{padding:8px 16px;border-right:1px solid var(--line);display:grid;gap:2px;min-width:0}
.line div:last-child{border-right:0}
.line b{font-family:var(--mono);font-size:22px;font-variant-numeric:tabular-nums;font-weight:600}
.line span{font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--muted);text-transform:uppercase}
.line .hi b{color:var(--red)}
.grid{display:grid;grid-template-columns:220px minmax(0,1fr);gap:40px;margin-top:28px}
nav.rail{position:sticky;top:calc(env(safe-area-inset-top,0px) + 16px);align-self:start;display:grid;gap:4px;font-size:14px}
nav.rail a{color:var(--muted);text-decoration:none;padding:4px 8px;border-left:2px solid var(--line)}
nav.rail a:hover,nav.rail a:focus-visible{color:var(--ink);border-left-color:var(--red);outline:none}
section{display:grid;gap:14px;padding-block:24px;border-bottom:1px solid var(--line);min-width:0}
h2{font-family:var(--display);font-weight:500;font-size:30px;margin:0;line-height:1.1;text-wrap:balance}
h2 small{font-family:var(--mono);font-size:12px;color:var(--red);letter-spacing:.08em;display:block;margin-bottom:4px}
p{margin:0;max-width:72ch}
ol.bottom{display:grid;gap:10px;margin:0;padding-left:22px;max-width:76ch}
.card{background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:6px;overflow-x:auto}
.plot{width:100%;min-width:640px}
.receipt{font-family:var(--mono);font-size:11.5px;color:var(--muted)}
.callout{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--red);padding:12px 16px;max-width:76ch}
.callout ul{margin:6px 0 0;padding-left:18px;display:grid;gap:4px;font-size:14px;color:var(--muted)}
.tbl{overflow-x:auto;border:1px solid var(--line);border-radius:6px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:760px}
th{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;text-align:left;color:var(--muted);padding:8px 10px;border-bottom:1px solid var(--line)}
td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.chip{display:inline-block;font-family:var(--mono);font-size:11px;font-weight:600;padding:2px 7px;border-radius:3px;border:1px solid currentColor;white-space:nowrap}
.g{color:var(--chip-good)}.b{color:var(--chip-bad)}.m{color:var(--chip-mid)}
.walk{font-family:var(--display);font-size:44px;color:var(--red);line-height:1}
footer{margin-top:28px;font-size:13px;color:var(--muted);display:grid;gap:6px}
@media (max-width:860px){.grid{grid-template-columns:minmax(0,1fr)}nav.rail{display:none}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
html{scroll-behavior:smooth}
"""


def chip(g):
    cls = "g" if g.startswith(("SUPPORTED", "SUSTAINABLE")) else "b" if g.startswith(("CONTRADICTED", "NOT")) else "m"
    return f'<span class="chip {cls}">{html.escape(g)}</span>'


def fig_div(key):
    return (f'<div class="card"><div class="plot" id="{key}" role="img" aria-label="{html.escape(N.SPECS[key]["title"])}"></div></div>'
            f'<div class="receipt">Receipts: {", ".join("out/dp_uc56_" + s + ".csv" for s in N.SPECS[key]["source"])} · claim asserted before render</div>')


line = [("AVG", f3(S26["ba"])), ("OBP", f3(S26["obp"])), ("SLG", f3(S26["slg"])), ("wOBA", f3(S26["woba"])), ("xwOBA", f3(S26["xwoba"])),
        ("Chase", pc(S26["chase_rate"])), ("PA", str(S26["plate_apps"]))]
parts = ['<div class="wrap">', '<header class="board">',
         f'<div class="eyebrow">Season recap · uc-pos-021 · dp_uc56 v1.0.0 · data through {H["anchor"]}</div>',
         f'<h1>We really do <em>love Sosa</em></h1>',
         f'<p class="sub">Edmundo Sosa, 2026 and maybe the end of a five-season Phillies run. A results-down year on a bat that did not decline, a bench role he still fits, and a number to walk away at.</p>',
         '<div class="line" aria-label="2026 line">' + "".join(f'<div class="{"hi" if k == "xwOBA" else ""}"><b>{v}</b><span>{k}</span></div>' for k, v in line) + '</div>',
         '</header>', '<div class="grid">', '<nav class="rail" aria-label="Chapters"><a href="#bottom">Bottom line</a>' +
         "".join(f'<a href="#{c[0]}">{html.escape(c[2])}</a>' for c in N.CH) + '<a href="#graded">Your notebook, graded</a></nav>', '<main>']
parts += ['<section id="bottom"><h2><small>THE ANSWER</small>Bottom line</h2><ol class="bottom">' + "".join(f"<li>{b2h(x)}</li>" for x in N.BOTTOM) + "</ol>",
          '<div class="callout"><strong>Read this first</strong><ul>' + "".join(f"<li>{b2h(x)}</li>" for x in N.READ_FIRST) + "</ul></div></section>"]
for anc, q, ttl, lede, figs, extra in N.CH:
    sec = [f'<section id="{anc}"><h2><small>{q}</small>{html.escape(ttl)}</h2>']
    if extra == "wa":
        sec.append(f'<div class="walk">${N.WA["ceiling"]:.1f}M · {N.WA["years"]} yrs</div>')
    sec.append(f"<p>{b2h(lede)}</p>")
    sec += [fig_div(k) for k in figs]
    parts.append("".join(sec) + "</section>")
rows = "".join(f'<tr><td>{k}</td><td>{html.escape(v["claim"])}</td><td>{html.escape(v["governed"])}</td><td>{chip(v["grade"])}</td><td>{html.escape(v["note"])}</td></tr>'
               for k, v in H["hp"].items())
parts.append('<section id="graded"><h2><small>HP-01 … HP-11</small>Your notebook, graded</h2><p>Each claim was reproduced on your own frame and functions first, then graded on the governed build.</p>'
             f'<div class="tbl"><table><thead><tr><th>#</th><th>Claim</th><th>Governed evidence</th><th>Grade</th><th>Note</th></tr></thead><tbody>{rows}</tbody></table></div>'
             '<div class="callout"><strong>Candid caveats</strong><ul>' + "".join(f"<li>{b2h(x)}</li>" for x in N.CAVEATS) + "</ul></div></section>")
parts += ["</main></div>", f'<footer><div>Phillies Statcast house log through {H["anchor"]}; regular season only. Carry-ins CI-1…CI-7 (Baseball-Reference, NBC Sports Philadelphia, PhillyVoice, Spotrac, MLB.com, ESPN, AP) are quoted, never computed on.</div>'
          f'<div>Use Case #56 · uc-pos-021 · build dp_uc56 v1.0.0 · {len(H["lineage"])} sha256 lineage pins · DQ {H["dq"]["pass"]} pass / {H["dq"]["warn"]} warn / {H["dq"]["fail"]} fail.</div></footer>', "</div>"]
figjs = json.dumps({k: FIGS[k] for k in N.SPECS})
SCRIPT = """<script>
(function(){const F=__FIGS__;const cfg={displaylogo:false,responsive:true,modeBarButtonsToRemove:['lasso2d','select2d']};
for(const [k,f] of Object.entries(F)){const el=document.getElementById(k);if(!el||!window.Plotly)continue;const lay=Object.assign({},f.layout,{autosize:true,width:null});
Plotly.newPlot(el,f.data,lay,cfg);}})();
</script>""".replace("__FIGS__", figjs)
body = "\n".join(parts)
head_bits = ('<title>Love Sosa</title><meta name="claude:viewport-fit-sides" content="cover">'
             '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;600&display=swap">')
full = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">{head_bits}'
        f'<style>{CSS}</style></head><body>{body}{render.plotly_script_tag()}{SCRIPT}</body></html>')
art = f'{head_bits}<style>{CSS}</style>\n{body}\n{render.plotly_script_tag()}{SCRIPT}'
assert "plotly.min.js" in full and "Plotly.newPlot" in full and full.count("<section") == len(N.CH) + 2
assert len(FIGS) == 9 and all(k in figjs for k in N.SPECS)
(HERE / "dp_uc56_sosa_2026_dashboard.html").write_text(full, encoding="utf-8")
(HERE / "dp_uc56_sosa_2026_dashboard_artifact.html").write_text(art, encoding="utf-8")
print("dashboard", round(len(full) / 1e6, 2), "MB;", len(N.CH) + 2, "sections;", len(FIGS), "figures")
