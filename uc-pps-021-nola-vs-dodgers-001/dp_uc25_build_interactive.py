"""Self-contained interactive HTML dashboard for uc-pps-021 (dp_uc25).
Reads receipts + base64-embeds the figures so the file opens offline anywhere.
Tabs: Overview / Arsenal / Splits & ABS / Matchup / Game Plan.
Usage: python dp_uc25_build_interactive.py [MLB_ROOT]"""
import sys, base64, pathlib
import pandas as pd

MLB = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
OUT = MLB / "out"

def b64(name):
    p = OUT / name
    if not p.exists(): return ""
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()

def fig(name, cap):
    src = b64(name)
    if not src: return ""
    return f"<figure><img src='{src}'/><figcaption>{cap}</figcaption></figure>"

# ---- receipts ----
tr = pd.read_csv(OUT/"dp_uc25_nola_season_trend.csv")
ps = pd.read_csv(OUT/"dp_uc25_process_by_stand_2026.csv")
ars = pd.read_csv(OUT/"dp_uc25_nola_arsenal_2026.csv")
py = pd.read_csv(OUT/"dp_uc25_process_abs_by_year.csv")
cq = pd.read_csv(OUT/"dp_uc25_contact_quality_by_year.csv")
h2h = pd.read_csv(OUT/"dp_uc25_dodgers_h2h.csv")
gl = pd.read_csv(OUT/"dp_uc25_recency_game_lines.csv")
rc = pd.read_csv(OUT/"dp_uc25_recency_split.csv")

r26 = tr[tr.game_year==2026].iloc[0]
L = ps[ps.stand=="L"].iloc[0]; R = ps[ps.stand=="R"].iloc[0]
last3 = rc[rc.segment.str.startswith("last-3")].iloc[0]

def pct(x): return f"{x*100:.1f}%"
def r3(x): return f"{x:.3f}"

cards = [
    ("2026 wOBA against", r3(r26.woba), f"career worst · xwOBAcon {r3(r26.xwobacon)}"),
    ("SLG / HR rate", f"{r3(r26.slg)} / {pct(r26.hr_rate)}", "both career worsts"),
    ("Walk rate vs LHB", pct(L.bb_rate), f"vs {pct(R.bb_rate)} to RHB — the leak"),
    ("xwOBAcon L / R", f"{r3(L.xwobacon)} / {r3(R.xwobacon)}", "contact identical by side"),
    ("Last 3 starts", r3(last3.woba), "trend up; 7/16 was 3 HR though"),
    ("Freshness", "2026-07-16", "20 GS · entity-locked 605400"),
]
cardhtml = "".join(f"<div class='card'><div class='cv'>{v}</div><div class='cl'>{l}</div><div class='cd'>{d}</div></div>" for l,v,d in cards)

# ---- tables ----
def table(df, cols, headers, fmts=None, rid=None):
    fmts = fmts or {}
    th = "".join(f"<th>{h}</th>" for h in headers)
    rows=[]
    for _,row in df.iterrows():
        tds=[]
        for c in cols:
            v=row[c]
            v=fmts[c](v) if c in fmts else v
            tds.append(f"<td>{v}</td>")
        rid_attr = f" data-name='{str(row['name']).lower()}'" if rid else ""
        rows.append(f"<tr{rid_attr}>{''.join(tds)}</tr>")
    return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

trend_tbl = table(tr[tr.game_year>=2022], ["game_year","games","plate_apps","woba","xwobacon","krate","bbrate","hr_rate","slg"],
    ["Season","GS","PA","wOBA","xwOBAcon","K%","BB%","HR/PA","SLG"],
    {"woba":r3,"xwobacon":r3,"krate":pct,"bbrate":pct,"hr_rate":pct,"slg":r3})

def ars_tbl(stand):
    d = ars[ars.stand==stand].sort_values("usage",ascending=False)
    return table(d, ["pitch_name","usage","velo","spin","whiff_rate"],
        ["Pitch","Usage","Velo","Spin","Whiff%"],
        {"usage":pct,"velo":lambda x:f"{x:.1f}","spin":lambda x:f"{x:.0f}","whiff_rate":pct})

ps_tbl = table(ps, ["stand","PA","woba","xwobacon","bb_rate","k_rate","first_pitch_strike_rate","putaway_rate","whiff_rate","hard_hit_rate","air_rate"],
    ["Stand","PA","wOBA","xwOBAcon","BB%","K%","1P-strike%","Putaway%","Whiff%","HardHit%","Air%"],
    {"woba":r3,"xwobacon":r3,"bb_rate":pct,"k_rate":pct,"first_pitch_strike_rate":pct,"putaway_rate":pct,"whiff_rate":pct,"hard_hit_rate":pct,"air_rate":pct})

py_tbl = table(py[py.game_year>=2022], ["game_year","first_pitch_strike_rate","chase_rate","putaway_rate","edge_rate","ooz_called_strike_rate","chase_up_rate"],
    ["Season","1P-strike%","Chase%","Putaway%","Edge%","OOZ-CS%","ChaseUp%"],
    {"first_pitch_strike_rate":pct,"chase_rate":pct,"putaway_rate":pct,"edge_rate":pct,"ooz_called_strike_rate":pct,"chase_up_rate":pct})

reads = {"Mookie Betts":"DANGER — has squared him","Freddie Freeman":"WATCH — the book, patient",
         "Shohei Ohtani":"DANGER — loud contact","Max Muncy":"EXPLOIT — 11 K / 25 PA",
         "Andy Pages":"directional — thin","Tommy Edman":"EXPLOIT — weak contact","Kyle Tucker":"directional — no book"}
h2h=h2h.copy(); h2h["read"]=h2h.name.map(reads)
h2h_tbl = table(h2h, ["name","stand_vs_nola","PA","H","HR","BB","K","whiff_rate","woba","xwobacon","read"],
    ["Hitter","Stands","PA","H","HR","BB","K","Whiff%","wOBA","xwOBAcon","Read"],
    {"whiff_rate":lambda x: pct(x) if pd.notna(x) else "—","woba":r3,"xwobacon":r3}, rid=True)

gl_tbl = table(gl.tail(6), ["game_date","opponent","venue","ip_computed","pitches","plate_apps","hrs","walks","strikeouts","woba"],
    ["Date","Opp","Venue","IP*","Pit","PA","HR","BB","K","wOBA"], {"woba":r3})

# ---- persona game plan ----
personas = [
 ("Aaron Nola","on the mound",[("Throw strike one to the lefties","58.8% 1P-strike vs LHB vs 73.5% vs RHB"),
   ("Finish with curve & change, not the heater","KC 42.5% whiff, CH 26.9% vs LHB; 4-seam only 13.8%"),
   ("Keep the fastball down","air-ball 59.7% / HR 5.1% — career highs, all in the air")]),
 ("Catcher — Realmuto / Marchan","the sequence",[("Two-strike target below the zone","putaway to LHB 18.6%; never a 4-seam middle"),
   ("Feed the changeup to lefties","26.9% whiff, up from ~16% — a real weapon now"),
   ("Pitch Betts & Ohtani backward","Betts .465/2HR/23 PA; Ohtani .450 xwOBAcon/9 PA")]),
 ("Manager","the call",[("Hook by matchup, not pitch count","3rd-time-through is where June & the 7/16 3-HR damage clustered"),
   ("Lefty warm for the L-pocket","5 Dodgers stand left — Ohtani/Freeman/Muncy stretch"),
   ("Trust the profile on no-book bats","Tucker & Pages 8 PA each — scout, don't lean on H2H")]),
 ("Pitching coach / analyst","the prep",[("Not the zone — don't coach the ump","edge .370 = career norm; OOZ-CS a decade glide"),
   ("Not the stuff — velo flat","4-seam 92.3, K% 23.8% steady; command & shape"),
   ("Reinforce change, watch the air ball","CH whiff 16%->27% vs LHB; GB rate career-low 40.3%")])]
pers_html = "".join(
  "<div class='pcard'><div class='pph'>"+t+"<span>"+tag+"</span></div><ul>"+
  "".join(f"<li><b>{a}</b><br><span class='ev'>{b}</span></li>" for a,b in items)+"</ul></div>"
  for t,tag,items in personas)

CSS = """
*{box-sizing:border-box} body{font-family:-apple-system,'Segoe UI',Arial,sans-serif;margin:0;color:#1a1a1a;background:#eef0f3;}
.wrap{max-width:1180px;margin:0 auto;background:#fff;min-height:100vh;box-shadow:0 0 26px rgba(0,0,0,.08);}
header{background:linear-gradient(110deg,#002D72,#0a3e94);color:#fff;padding:20px 26px;border-bottom:5px solid #E81828;}
header h1{margin:0;font-size:23px;} header p{margin:5px 0 0;font-size:12.5px;opacity:.9;}
nav{display:flex;gap:2px;background:#002D72;padding:0 14px;flex-wrap:wrap;}
nav button{background:none;border:none;color:#cdd8ee;padding:11px 16px;font-size:13px;cursor:pointer;border-bottom:3px solid transparent;font-weight:600;}
nav button:hover{color:#fff;} nav button.on{color:#fff;border-bottom-color:#E81828;}
main{padding:20px 26px 40px;} section{display:none;} section.on{display:block;animation:f .25s;}
@keyframes f{from{opacity:0;transform:translateY(4px)}to{opacity:1}}
h2{color:#002D72;font-size:17px;border-left:5px solid #E81828;padding-left:9px;margin:18px 0 8px;}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:11px;margin:6px 0 4px;}
.card{background:#f5f6f8;border-top:3px solid #002D72;border-radius:7px;padding:11px 13px;}
.card:nth-child(3){border-top-color:#E81828;} .cv{font-size:21px;font-weight:700;color:#002D72;} .card:nth-child(3) .cv{color:#E81828;}
.cl{font-size:10.5px;color:#55606e;text-transform:uppercase;letter-spacing:.3px;margin-top:2px;} .cd{font-size:11px;color:#33291a;margin-top:2px;}
table{border-collapse:collapse;width:100%;margin:9px 0;font-size:12.5px;}
th{background:#002D72;color:#fff;padding:7px 9px;text-align:left;position:sticky;top:0;}
td{padding:6px 9px;border:1px solid #e2e5ea;} tr:nth-child(even) td{background:#f5f6f8;}
tbody tr:hover td{background:#fdeff0;}
figure{margin:12px 0;text-align:center;} figure img{width:100%;max-width:920px;border:1px solid #e6e8ec;border-radius:6px;}
figcaption{font-size:11.5px;color:#55606e;font-style:italic;margin-top:4px;}
.toggle button{background:#e9edf4;border:1px solid #c9d3e3;color:#002D72;padding:6px 15px;cursor:pointer;font-weight:600;border-radius:5px;margin-right:6px;}
.toggle button.on{background:#002D72;color:#fff;}
#flt{padding:8px 11px;border:1px solid #c9d3e3;border-radius:6px;font-size:13px;width:260px;margin:4px 0;}
.pcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;}
.pcard{border:1px solid #e6e8ec;border-radius:8px;overflow:hidden;} .pph{background:#002D72;color:#fff;padding:9px 12px;font-weight:700;font-size:14px;display:flex;justify-content:space-between;align-items:baseline;}
.pph span{font-size:9px;opacity:.85;text-transform:uppercase;letter-spacing:.4px;font-weight:400;}
.pcard ul{list-style:none;margin:0;padding:10px 13px;} .pcard li{margin:0 0 10px;font-size:12.8px;line-height:1.34;} .pcard li b{color:#002D72;} .ev{font-size:11px;color:#55606e;}
.note{background:#FBF7E7;border-left:5px solid #E81828;padding:9px 13px;font-size:12px;color:#33291a;border-radius:0 4px 4px 0;margin:10px 0;}
footer{background:#002D72;color:#aebfe0;font-size:10.5px;padding:13px 26px;text-align:center;}
"""

JS = """
function tab(id,btn){document.querySelectorAll('section').forEach(s=>s.classList.remove('on'));
document.getElementById(id).classList.add('on');
document.querySelectorAll('nav button').forEach(b=>b.classList.remove('on'));btn.classList.add('on');}
function ars(st,btn){document.getElementById('arsL').style.display=st=='L'?'block':'none';
document.getElementById('arsR').style.display=st=='R'?'block':'none';
document.querySelectorAll('.toggle button').forEach(b=>b.classList.remove('on'));btn.classList.add('on');}
function filt(){var q=document.getElementById('flt').value.toLowerCase();
document.querySelectorAll('#h2htbl tbody tr').forEach(r=>{r.style.display=r.dataset.name.includes(q)?'':'none';});}
"""

html = f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Nola vs Dodgers — Advance Dashboard (dp_uc25)</title><style>{CSS}</style></head><body><div class='wrap'>
<header><h1>Advance Scout — Aaron Nola (RHP) vs the Dodgers</h1>
<p>Citizens Bank Park · 2026-07-22 · UC #26 (uc-pps-021) · live through his last start 2026-07-16 · entity-locked pitcher==605400</p></header>
<nav>
<button class='on' onclick="tab('ov',this)">Overview</button>
<button onclick="tab('ar',this)">Arsenal</button>
<button onclick="tab('sp',this)">Splits &amp; ABS</button>
<button onclick="tab('mu',this)">Matchup</button>
<button onclick="tab('gp',this)">Game Plan</button></nav>
<main>
<section id='ov' class='on'>
<h2>2026 at a glance</h2><div class='cards'>{cardhtml}</div>
<div class='note'>The line is the worst of his career, but velo is flat and strikeouts are steady — this is a <b>left-handed free-pass and air-ball problem</b>, not a stuff problem. Both are self-correctable.</div>
<h2>Season trend (2022–2026)</h2>{trend_tbl}
{fig('dp_uc25_contact_quality.png','The engine: ground balls down, air &amp; home runs up (career).')}
</section>
<section id='ar'>
<h2>Arsenal by batter side (2026)</h2>
<div class='toggle'><button class='on' onclick="ars('L',this)">vs LHB</button><button onclick="ars('R',this)">vs RHB</button></div>
<div id='arsL'>{ars_tbl('L')}</div><div id='arsR' style='display:none'>{ars_tbl('R')}</div>
{fig('dp_uc25_usage_whiff_2026.png','Usage vs whiff by pitch, 2026.')}
{fig('dp_uc25_nola_arsenal_map.png','Average location by pitch type (catcher POV).')}
</section>
<section id='sp'>
<h2>The left-handed problem — process split (2026)</h2>{ps_tbl}
<div class='note'>Same contact quality (xwOBAcon .382 L / .387 R) and same whiff rate both sides. The entire lefty gap is the <b>walk rate</b> and <b>first-pitch strikes</b>.</div>
{fig('dp_uc25_process_abs_panel.png','ABS re-test (edge intact, stolen strike a slow decline) and the 2026 L/R process split.')}
<h2>The ABS question, by year</h2>{py_tbl}
</section>
<section id='mu'>
<h2>The seven Dodgers — career H2H vs Nola</h2>
<input id='flt' onkeyup='filt()' placeholder='filter hitter…'>
<div id='h2htbl'>{h2h_tbl}</div>
<div class='note'>Career samples, small (8–86 PA). Only <b>Freeman (86)</b> is a real sample; the rest are directional. Most last faced Nola in April 2025.</div>
{fig('dp_uc25_dodgers_h2h_matrix.png','Career wOBA vs Nola for the seven — PA annotated.')}
<h2>Last six starts</h2>{gl_tbl}
{fig('dp_uc25_recency_approach.png','Results by start + pitch-mix tracks; the 3 starts since the last report in red.')}
</section>
<section id='gp'>
<h2>What each person can do</h2><div class='pcards'>{pers_html}</div>
<div class='note'><b>Single attack rule:</b> get ahead of the five lefties and finish them with the curve and changeup — never a fastball they can lift. Win the first pitch, keep it down, and the Dodgers are a manageable night.</div>
</section>
</main>
<footer>dp_uc25 · uc-pps-021 · Aaron Nola vs LAD 2026-07-22 · confidential internal advance · matchup = 7 named hitters (confirm the card) · locked KPIs inherited from UC8→UC11→UC15 · public Statcast data</footer>
</div><script>{JS}</script></body></html>"""

out = MLB / "dp_uc25_nola_vs_dodgers_interactive.html"
out.write_text(html, encoding="utf-8")
print("wrote", out, f"{out.stat().st_size/1024:.0f} KB")
