"""dp_uc53_build_report.py - writes dp_uc53_alvarado_2026_recap_report.md from dp_uc53_narrative (no hand-typed numbers).
Shell carried from dp_uc52_build_report.py (RQ-3 pipe guard, section cap)."""
from __future__ import annotations
import html, re, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc53_narrative as N

ROOT = Path(__file__).resolve().parent; OUT = ROOT / "out"
strip = lambda s: re.sub(r"</?b>", "**", s).replace("<code>", "`").replace("</code>", "`")   # noqa: E731
cell = lambda x: str(x).replace("|", "/")      # a pipe inside a cell splits a markdown table (RQ-3)
lin = N.H["lineage"]
L = [f"# {N.TITLE}", f"### {N.SUB} · LHP reliever · Philadelphia Phillies · {int(N.S['games'])} games in 2026 · data through {N.FR['anchor']}", "",
     "**Prepared for:** Front office, pitching department, bullpen staff · José Alvarado", "",
     f"**Arsenal (2026):** {N.ARSENAL}", "",
     f"**Governance:** Use Case #53 (`uc-pps-037`) · build `dp_uc53` v1.0.0 · kernel `dp_uc53_kernel.py` imports `dp_uc52_kernel.py` "
     f"(sha256 `{lin['dp_uc52_kernel.py'][:8]}…`) and the house `cumulative_metric.py` (`{lin['cumulative_metric.py'][:8]}…`). New objects (OD-1, DB-1) are "
     "provisional; DB-1 was registered before any 2026 rate was read. Independently verified; see `05_quality_certification.md`.", "",
     f"**Companion:** `dp_uc53_alvarado_2026_dashboard.html`, the same story in {len(N.CH)} chapters.", "",
     "> **Read this first: data window, sources, carry-ins.**", ">"]
L += [f"> - {strip(x)}" for x in N.READ_FIRST] + ["", "## 1 · Bottom line"] + [f"{i}. {strip(x)}" for i, x in enumerate(N.BOTTOM, 1)]
fmt = {"pc": N.pc, "f3": N.f3}
for sec, (anc, ttl, lede, figs, extra) in enumerate(N.CH, 2):
    L += ["", f"## {sec} · {ttl}", "", strip(lede), ""]
    for k in figs:
        L += [f"![{N.SPECS[k]['title']}](out/dp_uc53_{k}.png)", f"*Receipt: out/dp_uc53_{N.SPECS[k]['receipt']} · claim asserted before render*", ""]
    if extra == "tenure":
        t = pd.read_csv(OUT / "dp_uc53_career_by_year.csv"); t = t[t.game_year >= 2021]
        ob = pd.read_csv(OUT / "dp_uc53_outing_bands_by_year.csv").set_index("game_year")
        L += ["| Season | G | PA | wOBA (house) | wOBA (Statcast) | xwOBA | K% | BB% | Whiff | Runs on watch / G | Clean outings | House RP pct |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {'**2026**' if r.game_year == 2026 else r.game_year} | {int(r.games)} | {int(r.plate_apps)} | {N.f3(r.woba)} | {N.f3(r.woba_sc)} | {N.f3(r.xwoba)} | "
              f"{N.pc(r.krate)} | {N.pc(r.bbrate)} | {N.pc(r.whiff_rate)} | {r.rc_per_gm:.2f} | {N.pc(ob.loc[r.game_year, 'clean_rate'], 0)} | "
              f"{N.ordn(N.RP['tenure'][str(r.game_year)]['percentile'])} |" for r in t.itertuples()]
        L += ["", f"*House RP percentile = wOBA allowed among {N.RP['n']} Phillies relief seasons 2015-26 (100+ PA; higher is better).*"]
    if extra == "monthly":
        m = pd.read_csv(OUT / "dp_uc53_monthly_2026.csv"); mn = {4: "Mar-Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep"}
        L += ["| Month | G | PA | wOBA (house) | xwOBA | K% | BB% | Sinker mph | Cutter mph |", "|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {mn[r.month]} | {int(r.games)} | {int(r.plate_apps)} | {N.f3(r.woba)} | {N.f3(r.xwoba)} | {N.pc(r.krate)} | {N.pc(r.bbrate)} | {r.si_velo:.1f} | {r.fc_velo:.1f} |"
              for r in m.itertuples()]
    if extra == "db1":
        L += ["| # | Signature | Registered bar | 2022-24 | 2026 | PA-1 verdict |", "|---|---|---|---|---|---|"]
        for r in N.DB["rows"]:
            v = (lambda x: f"{x:.1f}") if "velo" in r["metric"] else (N.f3 if r["metric"] == "luck_gap" else N.pc)
            bar = (f"{r['threshold']:.1f} mph" if "velo" in r["metric"] else N.f3(r["threshold"]) if r["metric"] == "luck_gap" else f"{100 * r['threshold']:.0f} pts")
            L += [f"| {r['sig']} | {cell(r['label'])} ({r['hypothesis']}) | {'+' if r['direction'] > 0 else '−'}{bar} | {v(r['baseline'])} | {v(r['season'])} | **{r['verdict']}** |"]
        L += ["", "**The case for moving on**"] + [f"- {x}" for x in N.CASE_MOVE_ON]
        L += ["", "**The case for one more year**"] + [f"- {x}" for x in N.CASE_BLIP]
        L += ["", f"> {strip(N.VERDICT_LINE)}"]
L += ["", f"## {len(N.CH) + 2} · Your notebook, graded", "",
      "Each claim was reproduced with your own frame (`pps`, all game types, by name) and functions first, then restated on the governed frame. Claims are graded, never overwritten.", "",
      "| # | Your claim | Your method | Governed value | Verdict |", "|---|---|---|---|---|"]
L += [f"| {r.hp} | {cell(r.claim)} | {cell(r.client_method)} | {cell(r.governed)} | **{cell(r.grade_text)}** |" for r in N.HP.itertuples()]
L += ["", "### Candid caveats"] + [f"- {x}" for x in N.CAVEATS]
(ROOT / "dp_uc53_alvarado_2026_recap_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
assert sum(1 for x in L if x.startswith("## ")) <= 9, "section cap"
print("report md:", len(L), "lines;", sum(1 for x in L if x.startswith("## ")), "sections")
