"""
dp_uc51_build_dashboard.py — narrative dashboard for UC #51 / uc-pps-035 ("Still Zack Wheeler").

Inherits the chapter template, theme bar and lazy drawing from dp_uc49_build_dashboard.py (uc-pps-034).
Reads ONLY out/dp_uc51_* receipts and the figure JSON written by dp_uc51_build_figs.py. Computes nothing.
Writes the offline repo copy (full document, plotly.js inlined) and the Artifact body variant.
"""
from __future__ import annotations

import json
import os
from html import escape as esc
from pathlib import Path

import pandas as pd
import plotly
import plotly.io as pio

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC51_OUT", HERE / "out"))
DEST = Path(os.environ.get("DP_UC51_DEST", HERE))
H = json.loads((OUT / "dp_uc51_headlines.json").read_text())
R = lambda n: pd.read_csv(OUT / f"dp_uc51_{n}.csv")        # noqa: E731
from dp_uc51_hp import HP                                   # noqa: E402  (writes the HP receipt)

pct = lambda x, d=1: f"{100 * x:.{d}f}%"                    # noqa: E731
f3 = lambda x: f"{x:.3f}".lstrip("0")                        # noqa: E731
SPECS = {s["figure"]: s for s in json.loads((OUT / "dp_uc51_figure_specs.json").read_text())}
FIGS = [s for s in SPECS]
figs = {k: json.loads((OUT / f"dp_uc51_{k}.json").read_text()) for k in FIGS}
L, P, C = H['line26'], H['periods'], H['card']

ST = R("starts_2026").sort_values("game_date")
ST['bb_pct'] = ST.bb / ST.pa
ST['date'] = ST.game_date.astype(str).str[:10]
PLAB = {'first_half': 'First half', 'opener': 'Post-break opener', 'stretch': 'The stretch', 'finish': 'The finish'}
starts = ST[['date', 'opp', 'venue', 'period', 'ip_display', 'h', 'r', 'bb', 'k', 'hr', 'pa', 'pitches', 'game_score', 'xwoba',
             'edge_rate', 'in_zone_rate', 'chase_rate', 'whiff_per_100', 'first_n_ff_velo', 'clear_miss', 'miss_arm', 'miss_glove',
             'rel_x', 'rel_z']].round(3)
payload = dict(figs=figs, starts=starts.to_dict("records"), plab=PLAB,
               dark=json.loads(json.dumps(pio.templates["plotly_dark"].to_plotly_json(), default=str)),
               light=json.loads(json.dumps(pio.templates["plotly_white"].to_plotly_json(), default=str)))


def sub(k):
    return esc(SPECS[k]["subtitle"])


def table(df, cols, heads, cls=""):
    th = "".join(f"<th>{esc(h)}</th>" for h in heads)
    rows = "".join("<tr>" + "".join(f"<td>{esc(str(r[c]))}</td>" for c in cols) + "</tr>" for _, r in df.iterrows())
    return f'<div class="tw"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'


def figbox(key, title, cls=""):
    return f'<div class="fig"><h3>{esc(title)}</h3><p class="sub">{sub(key)}</p><div class="plot {cls}" id="{key}" role="img" aria-label="{esc(title)}"></div></div>'


def chapter(no, anchor, title, lede, body):
    return f'<section class="ch" id="{anchor}"><div class="chno">Chapter {no}</div><h2>{esc(title)}</h2><p class="lede">{lede}</p>{body}</section>'


# --- tables ------------------------------------------------------------------------------------
PE = R("periods_2026").set_index("period").loc[['first_half', 'opener', 'stretch', 'finish']].reset_index()
PE = PE.assign(lab=PE.period.map(PLAB), st=PE.starts.astype(int).astype(str), bbp=PE.bbrate.map(pct), kp=PE.krate.map(pct),
               wo=PE.woba.map(f3), xw=PE.xwoba.map(f3), iz=PE.in_zone_rate.map(pct), ed=PE.edge_rate.map(pct),
               r27=PE.r27.map(lambda x: f"{x:.2f}"), arm=PE.miss_arm_share.map(lambda x: pct(x, 0)))
period_tbl = table(PE, ['lab', 'st', 'plate_apps', 'bbp', 'kp', 'wo', 'xw', 'iz', 'ed', 'arm', 'r27'],
                   ['Period', 'Starts', 'PA', 'BB%', 'K%', 'wOBA', 'xwOBA', 'In-zone', 'Edge', 'Arm-side misses', 'Runs / 27 outs'])
RG = R("recap_governed"); RG = RG[RG.era == 'PHI'].sort_values('game_year')
RGt = RG.assign(yr=RG.game_year.astype(str), wo=RG.woba.map(f3), xw=RG.xwoba.map(f3), op=RG.ops.map(f3), kp=RG.krate.map(pct),
                bbp=RG.bbrate.map(pct), hh=RG.hard_hit_rate.map(pct), br=RG.barrel_rate.map(pct), ld=RG.line_drive_rate.map(pct),
                tu=RG.jam_rate.map(lambda x: "—" if pd.isna(x) else pct(x)), v=RG.ff_velo.map(lambda x: f"{x:.1f}"))
recap_tbl = table(RGt, ['yr', 'games', 'plate_apps', 'wo', 'xw', 'op', 'kp', 'bbp', 'hh', 'br', 'ld', 'tu', 'v'],
                  ['Season', 'G', 'PA', 'wOBA', 'xwOBA', 'OPS', 'K%', 'BB%', 'Hard-hit', 'Barrel', 'Line drive', 'Tied-up', 'FF mph'])
CARD = R("still_wheeler_card")
fmt = lambda b, c: f"{b:.1f} mph" if c == "first_n_ff_velo" else (f"{b:.1f}" if c == "whiff_per_100" else pct(b))  # noqa: E731
CARDt = CARD.assign(bar_fmt=[fmt(b, c) for b, c in zip(CARD.bar, CARD.column)],
                    prime_fmt=[fmt(b, c) for b, c in zip(CARD.bar_2021_25, CARD.column)],
                    med_fmt=[fmt(b, c) for b, c in zip(CARD.season_median, CARD.column)],
                    rule=["at or above" if d == "higher" else "at or below" for d in CARD.direction])
card_tbl = table(CARDt, ['signature', 'label', 'rule', 'bar_fmt', 'med_fmt', 'prime_fmt'],
                 ['#', 'Signature', 'Holds when', '2027 bar (his 2026 edge)', 'His 2026 median', 'Same rule on 2021–25'])
PL = R("postseason_ledger")
PLt = PL.assign(date=PL.game_date.astype(str).str[:10], line=PL.ip_display.map(lambda x: f"{float(x):.1f}") + " IP, " + PL.h.astype(str)
                + " H, " + PL.r.astype(str) + " R, " + PL.bb.astype(str) + " BB, " + PL.k.astype(str) + " K, " + PL.hr.astype(str) + " HR")
post_tbl = table(PLt, ['date', 'round', 'opp', 'role', 'line', 'pitches', 'game_score'],
                 ['Date', 'Round', 'Opponent', 'Role', 'Line', 'Pitches', 'Game Score (GS-1b)'])
WC = R("wc_g3_plate_appearances")
WCt = WC.assign(ev=WC.events.str.replace('_', ' '), rn=WC.runs.astype(int).astype(str))
wc_tbl = table(WCt, ['inning', 'batter_name', 'stand', 'ev', 'rn'], ['Inning', 'Batter', 'Bats', 'Result', 'Runs'])
hp_tbl = table(HP, ['id', 'client', 'verdict', 'governed'], ['#', 'Your notebook said', 'Verdict', 'What the governed build shows'], 'hp')

products = [("Feature report", "Built", "The long read, PDF (dp_uc51_wheeler_2026_recap_report.pdf)."),
            ("Narrative dashboard", "Built", "This page: eight chapters with a start-by-start drill."),
            ("Stretch forensics", "Built", "Walks, misses and release point across the six-start slide (chapter 4)."),
            ("Swing-timing board", "Built", "Tied-up, centered and flail, with the population named (chapter 5)."),
            ("Still-Wheeler card", "Built", "2027 bars registered before a pitch is thrown (chapter 8)."),
            ("Notecard", "Built", "One image for a thread or a broadcast graphic (out/dp_uc51_fig13_notecard.png)."),
            ("Postseason ledger", "Built", "The Wild Card relief outing beside his Phillies Octobers (chapter 8)."),
            ("Contract-value board", "Not built", "Needs salary and WAR sources; the 2027 year is a carry-in.")]
prod_html = "".join(f'<div class="prod"><span class="st">{esc(s)}</span><b>{esc(n)}</b>{esc(d)}</div>' for n, s, d in products)

hero_tiles = [
    (f3(L['xwoba']), "xwOBA allowed", f"#{H['ctx_sw']['rank_xwoba']} of {H['ctx_sw']['n']} Phillies starter seasons since 2015"),
    (f"{H['carry']['ip']}", "innings in 28 starts", f"{L['strikeouts']} K · {L['walks']} BB · OU-2 outs reconcile to the box"),
    (pct(L['chase_rate']), "chase rate", f"highest of his Phillies years · {H['kp']['chase_rate']['pct']}th house percentile"),
    (pct(P['stretch']['bbrate']), "walk rate, 7/27–8/24", f"{pct(P['finish']['bbrate'])} over the last six starts"),
]
tiles = "".join(f'<div class="tile"><div class="big">{a}</div><div class="lab">{esc(b)}</div><div class="note">{esc(c)}</div></div>'
                for a, b, c in hero_tiles)

opts = "".join(f'<option value="{i}">{r.date} · {r.opp} · {PLAB[r.period]}</option>' for i, r in enumerate(starts.itertuples()))

ch = [
    chapter(1, "return", "The return",
            f"His 2025 ended after August 15 with a blood clot; surgeons removed a rib on September 23 <span class='tag'>carry-in</span>. "
            f"He came back on April 25 after three rehab starts at Lehigh Valley, and the first half was already certified: uc-pps-020 published "
            f"15 starts, a .246 wOBA and a 30.4% strikeout rate. This build recomputes those numbers before adding anything ({H['repro']} match).",
            f'<div class="panel"><h4>Season line, regular season (governed)</h4>{recap_tbl}<p class="carry">Source: out/dp_uc51_recap_governed.csv. '
            f'Published line: 14–5, 3.00 ERA, 162.0 IP, 193 K, 47 BB <span class="tag">carry-in</span>; the log reconciles 162.0 IP, 193 K and 47 BB.</p></div>'),
    chapter(2, "still", "Still Zack Wheeler",
            f"Among the {H['ctx_sw']['n']} Phillies seasons with a starter's workload since 2015, his {f3(L['xwoba'])} xwOBA is #{H['ctx_sw']['rank_xwoba']}, "
            f"and {H['ctx_sw']['wheeler_seasons_top10_xwoba']} of the top ten belong to him. The walk rate is the one line that set a Phillies-tenure high.",
            figbox("fig1_still_wheeler", "Six of the ten best") + figbox("fig2_results_by_season", "Results by season", "short")),
    chapter(3, "zone", "He stopped needing the zone",
            f"In-zone rate fell to {pct(L['in_zone_rate'])}, the lowest of his Phillies years, and hitters chased {pct(L['chase_rate'])} of what he threw "
            f"outside it, the most. Edge rate (ER-1) did not move ({pct(L['edge_rate'])}). Your Savant edge figure, 42.4%, uses a different band.",
            figbox("fig3_zone_expansion", "Zone expansion")),
    chapter(4, "stretch", "The six-start slide",
            f"From 7/27 to 8/24 he walked {pct(P['stretch']['bbrate'])} of hitters and allowed {P['stretch']['r27']:.2f} runs per 27 outs, which matches the "
            f"reported 8.51 ERA. Reporting blamed a dropped glove and over-rotation <span class='tag'>carry-in</span>. The log cannot see a glove. "
            f"It does show his misses drifting to the arm side while his release point stayed where it was. Then the finish: "
            f"{pct(P['finish']['bbrate'])} walks, {P['finish']['r27']:.2f} runs per 27 outs.",
            figbox("fig4_the_stretch", "Walks and contact by start", "tall")
            + f'<div class="two"><div class="panel"><h4>Pick a start</h4><label class="sr" for="startsel">Start</label>'
              f'<select id="startsel">{opts}</select><div id="startout"></div>'
              f'<p class="carry">Click a bar in the chart above to jump to that start. Source: out/dp_uc51_starts_2026.csv.</p></div>'
              f'<div class="panel"><h4>By period</h4>{period_tbl}</div></div>'
            + figbox("fig5_misses_and_release", "Where the misses went")),
    chapter(5, "timing", "Contact and swing timing",
            f"Hard-hit, barrel and line-drive rates all sat inside his normal range. Hitters were tied up on {pct(L['jam_rate'])} of tracked swings, "
            f"#{H['tied_pop']['rank']} of {H['tied_pop']['n']} Phillies pitcher-seasons. The sinker to righties is the signature: "
            f"{H['si_jam']['bip']} tied-up balls in play, {H['si_jam']['hits']} hits.",
            figbox("fig6_contact_quality", "Contact quality", "short") + figbox("fig7_tied_up_population", "Tied-up rate, the room")
            + figbox("fig8_swing_timing_by_pitch", "Swing timing by pitch")),
    chapter(6, "platoon", "Lefties did the damage",
            f"Right-handed hitters managed a {f3(H['platoon']['2026R']['woba'])} wOBA. Left-handed hitters got to {f3(H['platoon']['2026L']['woba'])}, "
            f"and they did it with contact: {pct(H['platoon_tests']['Hard-hit']['L'])} hard-hit against {pct(H['platoon_tests']['Hard-hit']['R'])}.",
            figbox("fig9_platoon", "Platoon by season", "short")),
    chapter(7, "arsenal", "Six pitches, the splitter second",
            f"The splitter doubled to {pct(H['ars']['2026']['FS']['usage'])} of his pitches with a {pct(H['ars']['2026']['FS']['whiff'])} whiff rate. "
            f"The four-seam averaged {H['velo']['season26']:.1f} mph, the slowest of his Phillies years (2021: {H['velo']['season21']:.1f}).",
            figbox("fig10_pitch_map", "Pitch map") + figbox("fig11_pitch_plot", "Pitch plot", "tall")),
    chapter(8, "next", "October, and 2027",
            f"Four days after Game 162 he entered Wild Card Game 3 in the 3rd, after Aaron Nola's early exit: {H['wc']['ip']} IP, {H['wc']['r']} runs, "
            f"{H['wc']['bb']} walks, the runs on Ozzie Albies' homer in the 4th. Braves 6, Phillies 2 <span class='tag'>carry-in</span>. "
            f"He has one year left on his deal <span class='tag'>carry-in</span>. The card below writes down, before a 2027 pitch, what still "
            f"being Zack Wheeler has to look like.",
            figbox("fig12_still_wheeler_card", "The Still-Wheeler card")
            + f'<div class="panel"><h4>The card</h4>{card_tbl}<p class="carry">Registered 2026-10-12. A start is on-script when ≥3 of 4 hold. '
              f'Backtest on 2026: on-script starts allowed {C["on_r27"]:.2f} runs per 27 outs, off-script {C["off_r27"]:.2f}. Wild Card G3, graded after '
              f'the fact: {C["wc_posthoc"]["verdict"]}. Changing a bar after the first 2027 pitch is a breaking change.</p></div>'
            + f'<div class="two"><div class="panel"><h4>Wild Card Game 3, plate by plate</h4>{wc_tbl}</div>'
              f'<div class="panel"><h4>His Phillies Octobers</h4>{post_tbl}</div></div>'),
]

CSS = """
:root{--bg:#fbfaf7;--surface:#ffffff;--ink:#1b1b1b;--ink2:#4a4f5c;--muted:#6b7080;--rule:#e3e6ec;--red:#E81828;--navy:#002D72;
--chip:#f1f3f6;--warn:#fff4f5;--warnrule:#E81828;--shadow:0 1px 2px rgba(0,0,0,.05)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141414;--surface:#1c1c1c;--ink:#ececec;--ink2:#c5c8d0;--muted:#9aa0ad;
--rule:#2e3138;--navy:#8FB0F0;--chip:#262a31;--warn:#2a1a1c;--shadow:none;color-scheme:dark}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#141414;--surface:#1c1c1c;--ink:#ececec;--ink2:#c5c8d0;--muted:#9aa0ad;--rule:#2e3138;--navy:#8FB0F0;
--chip:#262a31;--warn:#2a1a1c;--shadow:none}
*{box-sizing:border-box;min-width:0}code{overflow-wrap:anywhere}html,body{margin:0;background:var(--bg);color:var(--ink);font-family:Arial,Helvetica,sans-serif;line-height:1.55}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px 64px}
header.top{border-top:6px solid var(--red);padding-block:28px 8px}
.kicker{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
h1{font-size:46px;line-height:1.05;margin:6px 0 4px;color:var(--navy)}h1 span{color:var(--red)}
.dek{font-size:18px;color:var(--ink2);max-width:820px;margin:6px 0 18px}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0 18px}
.bar button{font:inherit;font-size:13px;border:1px solid var(--rule);background:var(--surface);color:var(--ink);padding:6px 12px;border-radius:999px;cursor:pointer}
.bar button:focus-visible,nav.toc a:focus-visible,select:focus-visible{outline:2px solid var(--red);outline-offset:2px}
.bar button[aria-pressed="true"]{background:var(--navy);color:var(--bg);border-color:var(--navy)}
nav.toc{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--rule);display:flex;gap:4px;overflow-x:auto;padding-block:8px}
nav.toc a{flex:0 0 auto;white-space:nowrap;font-size:13px;color:var(--ink2);text-decoration:none;padding:4px 10px;border-radius:6px}
nav.toc a:hover,nav.toc a.on{background:var(--chip);color:var(--ink)}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:10px 0 18px}
.tile{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:14px;box-shadow:var(--shadow)}
.tile .big{font-size:30px;font-weight:700;color:var(--navy);font-variant-numeric:tabular-nums}.tile .lab{font-weight:600}.tile .note{font-size:12.5px;color:var(--muted)}
.warn{background:var(--warn);border-left:4px solid var(--warnrule);padding:12px 14px;border-radius:6px;font-size:13.5px;color:var(--ink2)}
.warn ul{margin:6px 0 0;padding-left:18px}
section.ch{padding-block:30px 6px;border-bottom:1px solid var(--rule)}
.chno{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--red);font-weight:700}
h1,h2{text-wrap:balance}h2{font-size:28px;margin:4px 0 8px;color:var(--ink)}
.lede{font-size:17px;color:var(--ink2);max-width:860px}
.fig{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:10px 10px 4px;margin:14px 0;box-shadow:var(--shadow)}
.fig h3{font-size:16px;margin:4px 6px 2px}.fig .sub{font-size:13px;color:var(--muted);margin:0 6px 6px}
.plot{width:100%;height:500px;overflow:hidden}.fig{overflow:hidden}.plot.tall{height:620px}.plot.short{height:420px}
.two{display:grid;grid-template-columns:1fr 1.3fr;gap:14px;margin:14px 0}
.panel{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:14px;font-size:14px;margin:14px 0}
.two .panel{margin:0}
.panel h4{margin:0 0 6px;font-size:14px;color:var(--navy)}
select{font:inherit;width:100%;padding:6px 8px;border:1px solid var(--rule);border-radius:6px;background:var(--surface);color:var(--ink)}
.kv{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:10px 0}
.kv div{background:var(--chip);border-radius:6px;padding:6px 8px;font-size:12.5px;color:var(--muted)}.kv b{display:block;font-size:17px;color:var(--ink);font-variant-numeric:tabular-nums}
.pill{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;background:var(--chip);color:var(--ink2)}
.pill.stretch{background:var(--red);color:#ffffff}
.tw{overflow-x:auto;margin:10px 0}table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
th{background:var(--navy);color:var(--bg);text-align:left;padding:7px 9px;font-weight:600;white-space:nowrap}td{border-bottom:1px solid var(--rule);padding:7px 9px;vertical-align:top}
table.hp td:nth-child(3){font-weight:700;white-space:nowrap}
.carry{font-size:12px;color:var(--muted)}.tag{display:inline-block;font-size:11px;padding:1px 6px;border-radius:4px;background:var(--chip);color:var(--muted);margin-left:2px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
footer{font-size:12.5px;color:var(--muted);padding-block:24px}
.products{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:12px 0}
.prod{overflow-wrap:anywhere;background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:10px 12px;font-size:13px}
.prod b{display:block;color:var(--navy)}.prod .st{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
@media (max-width:820px){h1{font-size:34px}.tiles,.products{grid-template-columns:repeat(2,minmax(0,1fr))}.two{grid-template-columns:1fr}.plot{height:420px}.plot.tall{height:540px}.plot.short{height:360px}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""


def _clean(o):
    if isinstance(o, float) and o != o:
        return None
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean(x) for x in o]
    return o


PAYLOAD_JS = json.dumps(_clean(payload), default=str, allow_nan=False).replace("</", "<\\/")
BODY = f"""
<div class="wrap">
<header class="top">
 <div class="kicker">Phillies Pitching · uc-pps-035 · 2026 season recap · data through {H['anchor']} (+ Wild Card)</div>
 <h1>Still <span>Zack Wheeler</span></h1>
 <p class="dek">He came back from a rib resection, gave up the fewest expected runs of nearly any Phillies starter season on record, lost the strike zone for six starts in August,
 found it again for September, and threw four innings of relief with the season on the line. One year is left on his deal.</p>
 <div class="bar"><button id="t-auto" aria-pressed="true">Match my system</button><button id="t-light" aria-pressed="false">Brand light</button>
 <button id="t-dark" aria-pressed="false">Notebook dark</button></div>
</header>
<nav class="toc" aria-label="Chapters"><a href="#return">1 · Return</a><a href="#still">2 · Still Wheeler</a><a href="#zone">3 · The zone</a>
<a href="#stretch">4 · The slide</a><a href="#timing">5 · Contact</a><a href="#platoon">6 · Platoon</a><a href="#arsenal">7 · Arsenal</a><a href="#next">8 · October &amp; 2027</a>
<a href="#notebook">Your notebook</a><a href="#products">Products</a></nav>
<div class="tiles">{tiles}</div>
<div class="warn"><b>Read this first.</b><ul>
<li>Entity lock: MLBAM 554430, never a name filter. Regular season for every rate; the Wild Card outing and earlier Octobers live only in chapter 8.</li>
<li>Career frame CF-2b: the Phillies log plus <code>wheeler.parquet</code>, MLB games only. {H['cf2_exposure']['milb_rows']} Lehigh Valley rehab pitches are excluded; the org's own CF-2 loader would have counted them.</li>
<li>Ranks and percentiles are Phillies pitcher-seasons 2015–2026, not MLB-wide. xwOBA is XW-1 (PA-denominated, matches Savant's .263).</li>
<li>"Runs on watch" = runs scored during the plate appearances he threw; it includes unearned runs. Outs come from OU-2 (the outs sequence of the full defensive log); ERA is a carry-in.</li>
<li>Tied-up rate is a public-data proxy for Savant's swing-timing bucket (JR-1, intercept &lt; 32.5 in). Carry-ins are tagged where they appear and never computed on. The log shows where the ball went, not why.</li></ul></div>
{''.join(ch)}
<section class="ch" id="notebook"><div class="chno">Appendix</div><h2>Your notebook, graded</h2>
<p class="lede">Every claim and chart choice in <code>October 2026.ipynb</code> cells 16 and 21–23, reproduced by your method, then by the governed one.</p>{hp_tbl}</section>
<section class="ch" id="products"><div class="chno">Appendix</div><h2>Eight ways to tell this story</h2>
<p class="lede">The organization scoped eight product forms against the recap and built seven. Each owns a part of the story the others do not.</p>
<div class="products">{prod_html}</div></section>
<footer>uc-pps-035 · dp_uc51 v1.0.0 · kernel dp_uc51_kernel.py (imports dp_uc49_kernel a4ad5191…, dp_uc50_kernel 8084cb17…; extracts UC8 edge_rate, library jam_rate, UC28 release_consistency, each sha256-pinned) ·
receipts out/dp_uc51_* · governance trail: Agents for Data Products/data-products/uc-pps-035-wheeler-2026-recap-001/ · Internal: Phillies pitching and front office.
Carry-in sources: Inquirer (9/19/2026), MLB.com (8/2025), StatMuse (season totals), FOX 29 (10/1/2026), repo week-ahead briefs.</footer>
</div>
<script id="payload" type="application/json">{PAYLOAD_JS}</script>
<script>
(function(){{
const P=JSON.parse(document.getElementById('payload').textContent);
const root=document.documentElement;
function isDark(){{const t=root.getAttribute('data-theme');if(t)return t==='dark';return window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches;}}
function css(v){{return getComputedStyle(root).getPropertyValue(v).trim();}}
function lay(base){{const L=JSON.parse(JSON.stringify(base));const d=isDark();L.template=d?P.dark:P.light;delete L.width;delete L.height;L.autosize=true;
 delete L.title;const hasSub=(L.annotations||[]).some(a=>a.yref==='paper'&&a.y>=1&&!a.showarrow);L.margin=Object.assign({{}},L.margin,{{t:hasSub?44:20}});
 L.paper_bgcolor=css('--surface');L.plot_bgcolor=css('--surface');L.font=Object.assign({{}},L.font||{{}},{{color:css('--ink'),family:'Arial'}});
 if(window.innerWidth<820){{L.margin=Object.assign({{}},L.margin,{{l:56,r:12}});}}return L;}}
const drawn={{}};
function themed(f){{if(!isDark())return f;let s=JSON.stringify(f);const m={{'#1b1b1b':css('--ink'),'#5b6170':css('--muted'),'#ffffff':css('--surface'),'#002D72':'#8FB0F0','#eeeeee':css('--rule')}};
 for(const k in m)s=s.split('"'+k+'"').join('"'+m[k]+'"');return JSON.parse(s);}}
function draw(k){{const f=themed(P.figs[k]);const el=document.getElementById(k);if(!el)return;
 Plotly.react(el,f.data,lay(f.layout),{{responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d','toImage']}});
 if(!drawn[k]&&k==='fig4_the_stretch')el.on('plotly_click',ev=>{{const d=ev.points[0].x;const i=P.starts.findIndex(s=>s.date===String(d).slice(0,10));if(i>=0){{sel.value=i;showStart(i);}}}});
 drawn[k]=true;}}
const io=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting&&!drawn[e.target.id])draw(e.target.id);}}),{{rootMargin:'400px'}});
Object.keys(P.figs).forEach(k=>{{const el=document.getElementById(k);if(el)io.observe(el);}});
function setTheme(m){{if(m==='auto')root.removeAttribute('data-theme');else root.setAttribute('data-theme',m);
 ['auto','light','dark'].forEach(x=>document.getElementById('t-'+x).setAttribute('aria-pressed',String(x===m)));
 try{{localStorage.setItem('uc51-theme',m);}}catch(e){{}}Object.keys(drawn).forEach(draw);}}
['auto','light','dark'].forEach(x=>document.getElementById('t-'+x).addEventListener('click',()=>setTheme(x)));
try{{const s=localStorage.getItem('uc51-theme');if(s)setTheme(s);}}catch(e){{}}
if(window.matchMedia)matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{{if(!root.getAttribute('data-theme'))Object.keys(drawn).forEach(draw);}});
const sel=document.getElementById('startsel');
const pc=x=>(x==null?'—':(100*x).toFixed(1)+'%'),f3=x=>(x==null?'—':x.toFixed(3).replace(/^0/,''));
function showStart(i){{const s=P.starts[i];const arm=s.clear_miss?Math.round(100*s.miss_arm/s.clear_miss)+'%':'—';
 document.getElementById('startout').innerHTML='<p><span class="pill '+(s.period==='stretch'?'stretch':'')+'">'+P.plab[s.period]+'</span> '+s.date+' · '+(s.venue==='home'?'vs ':'at ')+s.opp+
 ' · '+s.ip_display+' IP, '+s.h+' H, '+s.r+' R, '+s.bb+' BB, '+s.k+' K, '+s.hr+' HR · '+s.pitches+' pitches</p><div class="kv">'+
 '<div>Walks per PA<b>'+pc(s.bb/s.pa)+'</b></div><div>xwOBA<b>'+f3(s.xwoba)+'</b></div><div>Game Score<b>'+s.game_score+'</b></div>'+
 '<div>In-zone<b>'+pc(s.in_zone_rate)+'</b></div><div>Edge (ER-1)<b>'+pc(s.edge_rate)+'</b></div><div>Chase<b>'+pc(s.chase_rate)+'</b></div>'+
 '<div>FF, first 15<b>'+(s.first_n_ff_velo==null?'—':s.first_n_ff_velo.toFixed(1))+'</b></div><div>Arm-side misses<b>'+arm+'</b></div><div>Release x / z (ft)<b>'+(s.rel_x==null?'—':s.rel_x.toFixed(2)+' / '+s.rel_z.toFixed(2))+'</b></div></div>';}}
sel.addEventListener('change',()=>showStart(+sel.value));
const first=P.starts.findIndex(s=>s.period==='stretch');sel.value=first;showStart(first);
const links=[...document.querySelectorAll('nav.toc a')];const secs=links.map(a=>document.querySelector(a.getAttribute('href')));
const so=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting){{links.forEach(l=>l.classList.toggle('on',l.getAttribute('href')==='#'+e.target.id));}}}}),{{rootMargin:'-40% 0px -55% 0px'}});
secs.forEach(x=>x&&so.observe(x));
}})();
</script>
"""

plotly_js = (Path(plotly.__file__).parent / "package_data" / "plotly.min.js").read_text(encoding="utf-8").replace("�", "\\uFFFD")
HEAD = f"<title>Still Zack Wheeler</title><meta name='viewport' content='width=device-width,initial-scale=1,viewport-fit=cover'><style>{CSS}</style><script>{plotly_js}</script>"
full = f"<!doctype html><html lang='en'><head><meta charset='utf-8'>{HEAD}</head><body>{BODY}</body></html>"
(DEST / "dp_uc51_wheeler_2026_dashboard.html").write_text(full, encoding="utf-8")
(DEST / "dp_uc51_wheeler_2026_dashboard_artifact.html").write_text(HEAD + BODY, encoding="utf-8")
print("dashboard", round(len(full) / 1e6, 2), "MB; HP rows", len(HP), "figs", len(figs))
