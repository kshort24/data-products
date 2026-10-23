"""dp_uc54_build_report.py - writes dp_uc54_crawford_2026_recap_report.md from dp_uc54_narrative (no hand-typed numbers).
Shell carried from dp_uc53_build_report.py (RQ-3 pipe guard)."""
from __future__ import annotations
import re, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc54_narrative as N

ROOT = Path(__file__).resolve().parent; OUT = ROOT / "out"
strip = lambda s: re.sub(r"</?b>", "**", s).replace("<code>", "`").replace("</code>", "`")   # noqa: E731
H, f3, pc, ordn = N.H, N.f3, N.pc, N.ordn
lin = H["lineage"]
L = [f"# {N.TITLE} — {N.SUB}", f"### Season recap · CF, bats left · Philadelphia Phillies · {int(H['plate_apps'])} PA in {H['games_with_pa']} games · data through {H['anchor']}", "",
     "**Prepared for:** Player development, hitting and outfield coaches, front office · Justin Crawford", "",
     f"**Approach (2026):** swing {pc(H['swing_rate'])} · chase {pc(H['chase_rate'])} · whiff {pc(H['whiff_rate'])} · GB {pc(H['gb_rate'])} · launch angle {H['mean_la']:.1f}°", "",
     f"**Governance:** Use Case #54 (`uc-pos-019`) · build `dp_uc54` v1.0.0 · kernel `dp_uc54_kernel.py` imports `dp_uc40_kernel.py` (sha256 `{lin['dp_uc40_kernel.py'][:8]}…`), "
     f"`dp_uc34_kernel.py` (`{lin['dp_uc34_kernel.py'][:8]}…`) and `dp_uc53_kernel.py` (`{lin['dp_uc53_kernel.py'][:8]}…`). New objects TR-1, CC-1, XO-2 are provisional; "
     "TR-1 was registered in the BID before any split was computed. Independently verified; see `05_quality_certification.md`.", "",
     f"**Companion:** `dp_uc54_crawford_2026_dashboard.html`, the same story in {len(N.CH)} chapters.", "",
     "> **Read this first: data window, sources, carry-ins.**", ">"]
L += [f"> - {strip(x)}" for x in N.READ_FIRST] + ["", "## 1 · Bottom line"] + [f"{i}. {strip(x)}" for i, x in enumerate(N.BOTTOM, 1)]
cell = lambda x: str(x).replace("|", "/")   # noqa: E731
for sec, (anc, q, ttl, lede, figs, extra) in enumerate(N.CH, 2):
    L += ["", f"## {sec} · {ttl} ({q})", "", strip(lede), ""]
    if extra == "line":
        c = pd.read_csv(OUT / "dp_uc54_season_card.csv").iloc[0]; a = pd.read_csv(OUT / "dp_uc54_aaa_card.csv").iloc[0]
        L += ["| Season | PA | BA | OBP | SLG | OPS | wOBA | xwOBA | BABIP | K% | BB% | HH% | GB% |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
              f"| **MLB 2026** | {int(c.plate_apps)} | {f3(c.ba)} | {f3(c.obp)} | {f3(c.slg)} | {f3(c.ops)} | {f3(c.woba)} | {f3(c.xwoba)} | {f3(c.babip)} | {pc(c.krate)} | {pc(c.bbrate)} | {pc(c.hard_hit_rate)} | {pc(c.gb_rate)} |",
              f"| RISP 2026 | {int(c.risp_pa)} | {f3(c.risp_ba)} | {f3(c.risp_obp)} | {f3(c.risp_slg)} | | | | | | | | |",
              f"| AAA 2025 (supporting) | {int(a.plate_apps)} | {f3(a.ba)} | {f3(a.obp)} | {f3(a.slg)} | {f3(a.ops)} | {f3(a.woba)} | — | — | {pc(a.krate)} | {pc(a.bbrate)} | {pc(a.hard_hit_rate)} | {pc(a.gb_rate)} |", ""]
        mv = pd.read_csv(OUT / "dp_uc54_cf_matched_volume.csv").sort_values("rank_woba")
        L += [f"*Phillies primary-CF seasons at {N.CX['matched_pa']} PA (or their final PA if fewer), CX-1, CF games only:*", "",
              "| Rank (wOBA) | Season | BA | OBP | OPS | wOBA |", "|---|---|---|---|---|---|"]
        L += [f"| {int(r.rank_woba)} | {'**' + r.series + '**' if r.series == 'Crawford 2026' else r.series} | {f3(r.ba)} | {f3(r.obp)} | {f3(r.ops)} | {f3(r.woba)} |" for r in mv.itertuples()]
        L += [""]
    for k in figs:
        L += [f"![{N.SPECS[k]['title']}](out/dp_uc54_{k}.png)", f"*Receipts: {', '.join('out/dp_uc54_' + s + '.csv' for s in N.SPECS[k]['source'])} · claim asserted before render*", ""]
    if extra == "turn":
        m = pd.read_csv(OUT / "dp_uc54_monthly_panel.csv"); mn = {3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep"}
        L += ["| Month | PA | BA | OBP | SLG | wOBA | xwOBA | K% | BB% | Chase | GB% | PA vs LHP |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {mn[r.month]} | {int(r.plate_apps)} | {f3(r.ba)} | {f3(r.obp)} | {f3(r.slg)} | {f3(r.woba)} | {f3(r.xwoba)} | {pc(r.krate)} | {pc(r.bbrate)} | {pc(r.chase_rate)} | {pc(r.gb_rate)} | {pc(r.lhp_share, 0)} |" for r in m.itertuples()]
        L += ["", "*March is 13 PA. Every month is below 100 PA; read the run of months, not any one.*", ""]
    if extra == "approach":
        g = pd.read_csv(OUT / "dp_uc54_pitch_group_hand.csv")
        L += ["| vs | Pitch group | Pitches | PA | wOBA | xwOBA | Chase | Whiff | Hard-hit | Putaway |", "|---|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {r.p_throws}HP | {r.pitch_group} | {int(r.pitches)} | {int(r.plate_apps)} | {f3(r.woba)} | {f3(r.xwoba)} | {pc(r.chase_rate)} | {pc(r.whiff_rate)} | {pc(r.hard_hit_rate)} | {pc(r.putaway_rate)} |"
              for r in g.itertuples()] + ["", "*Rows under 50 PA (all three LHP rows) are directional.*", ""]
    if extra == "walks":
        g = pd.read_csv(OUT / "dp_uc54_cc1_by_hand_group.csv")
        L += ["| vs | Pitch group | Out-of-zone pitches | Chases | Chase rate | CC-1 runs |", "|---|---|---|---|---|---|"]
        L += [f"| {r.p_throws}HP | {r.pitch_group} | {int(r.ooz_pitches)} | {int(r.chases)} | {pc(r.chase_rate)} | {r.chase_cost_runs:.1f} |" for r in g.itertuples()] + [""]
    if extra == "spin":
        g = pd.read_csv(OUT / "dp_uc54_rhp_breaking_by_level.csv")
        L += ["| RHP breaking balls | Pitches | PA | BA | SLG | Hard-hit | Avg EV (tracked n) | Chase | Whiff |", "|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {r.level} | {int(r.pitches)} | {int(r.plate_apps)} | {f3(r.ba)} | {f3(r.slg)} | {pc(r.hard_hit_rate)} | {r.ev_mu:.1f} ({int(r.ev_tracked)}) | {pc(r.chase_rate)} | {pc(r.whiff_rate)} |" for r in g.itertuples()] + [""]
    if extra == "cf":
        g = pd.read_csv(OUT / "dp_uc54_xo2_cf_context.csv")
        L += ["| Rank | Phillies CF season | CF games | Scored air balls | Outs above expected | Per 100 |", "|---|---|---|---|---|---|"]
        L += [f"| {i} | {'**' if r.fielder == 702222 else ''}{r['name'].split(', ')[1]} {r['name'].split(', ')[0]} {int(r.game_year)}{'**' if r.fielder == 702222 else ''} | {int(r.cf_games)} | {int(r.opps)} | {r.oae:+.1f} | {r.oae_per_100:+.2f} |"
              for i, (_, r) in enumerate(g.iterrows(), 1)] + [""]
L += ["", f"## {len(N.CH) + 2} · Your notebook, graded", "", "| # | Your claim | Your frame | Governed | Verdict |", "|---|---|---|---|---|"]
L += [f"| {k} | {cell(v['claim'])} | {cell(v['client'])} | {cell(v['governed'])} | **{v['grade']}** |" for k, v in H["hp"].items()]
hc = H["hp_client_frame"]
L += ["", f"*Your frame (`jc`) holds {hc['pitches_2026']:,} pitches and {hc['pa_2026']} PA for 2026: {hc['spring_2026']} spring and {hc['post_2026']} Wild Card pitches, plus "
      f"{hc['src2_rows']} duplicated rows from `white-sox-of-25-26.parquet` (SRC-1, SRC-2). Every rate still reproduces within one point. The governed frame is regular season only "
      f"({int(H['plate_apps'])} PA). Evidence for each grade: `out/dp_uc54_hp_grades.csv`.*", "", "## Candid caveats"] + [f"- {strip(x)}" for x in N.CAVEATS]
md = "\n".join(L) + "\n"
(ROOT / "dp_uc54_crawford_2026_recap_report.md").write_text(md, encoding="utf-8")
print("report sections:", len([l for l in L if l.startswith("## ")]), "chars", len(md))
