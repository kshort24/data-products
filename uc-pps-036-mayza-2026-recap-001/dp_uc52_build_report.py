"""dp_uc52_build_report.py — writes dp_uc52_mayza_2026_recap_report.md from dp_uc52_narrative (no hand-typed numbers)."""
from __future__ import annotations
import html, re, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc52_narrative as N

ROOT = Path(__file__).resolve().parent; OUT = ROOT / "out"
strip = lambda s: re.sub(r"</?b>", "**", s)                 # noqa: E731
lin = N.H["lineage"]["dp_uc51_kernel.py"][:8]
L = [f"# {N.TITLE}", f"### {N.SUB} · LHP reliever · Philadelphia Phillies · {int(N.S['games'])} games · data through {N.FR['anchor']}", "",
     "**Prepared for:** Pitching department, bullpen staff, front office · Tim Mayza", "",
     f"**Arsenal (2026):** {N.ARSENAL}", "",
     f"**Governance:** Use Case #52 (`uc-pps-036`) · build `dp_uc52` v1.0.0 · kernel `dp_uc52_kernel.py` imports `dp_uc51_kernel.py` "
     f"(sha256 `{lin}…`). New objects (QA-1, BS-1, DS-1, RP-1) are provisional. Independently verified; see `05_quality_certification.md`.", "",
     f"**Companion:** `dp_uc52_mayza_2026_dashboard.html`, the same story in {len(N.CH)} chapters.", "",
     "> **Read this first: data window, sources, carry-ins.**", ">"]
L += [f"> - {strip(x)}" for x in N.READ_FIRST] + ["", "## 1 · Bottom line"] + [f"{i}. {strip(x)}" for i, x in enumerate(N.BOTTOM, 1)]
sec = 1
for anc, ttl, lede, figs, extra in N.CH:
    if anc == "slider":                      # report folds the slider chapter into Stuff (BID: 9 sections); dashboard keeps it
        L += ["", f"### {ttl}", "", lede, ""]
    else:
        sec += 1; L += ["", f"## {sec} · {ttl}", "", lede, ""]
    for k in figs:
        L += [f"![{N.SPECS[k]['title']}](out/dp_uc52_{k}.png)", f"*Receipt: out/dp_uc52_{k}.json · asserts: {html.escape(N.SPECS[k]['asserts'])}*", ""]
    if extra == "house":
        t = pd.read_csv(OUT / "dp_uc52_house_lhp_rp.csv").sort_values("woba").reset_index(drop=True)
        t["r"] = t.index + 1
        t = pd.concat([t.head(5), t[(t.pitcher == 641835) & (t.game_year == 2026)]]).drop_duplicates(subset=["pitcher", "game_year"])
        L += [f"*Top five of {N.HL['n']} Phillies LHP relief seasons by wOBA allowed (2015-26, 100+ PA), plus Mayza 2026.*", "",
              "| # | Pitcher | Season | PA | wOBA | OPS | BB% | Runs on watch / G |", "|---|---|---|---|---|---|---|---|"]
        L += [f"| {int(r.r)} | {'**' + r.player_name + '**' if r.pitcher == 641835 else r.player_name} | {r.game_year} | {r.plate_apps} | {N.f3(r.woba)} | "
              f"{N.f3(r.ops)} | {N.pc(r.bbrate)} | {r.rc_per_gm:.2f} |" for r in t.itertuples()]
    if extra == "platoon":
        L += ["| Split | PA | wOBA (house) | wOBA (Statcast) | xwOBA | K% | BB% | Hard-hit | Barrel | Quick-AB |", "|---|---|---|---|---|---|---|---|---|---|"]
        L += [f"| vs {s}HB | {int(v['plate_apps'])} | {N.f3(v['woba'])} | {N.f3(v['woba_sc'])} | {N.f3(v['xwoba'])} | {N.pc(v['krate'])} | {N.pc(v['bbrate'])} | "
              f"{N.pc(v['hard_hit_rate'])} | {N.pc(v['barrel_rate'])} | {N.pc(v['quick_ab_rate'])} |" for s, v in N.PL.items()]
L += ["", f"## {sec + 1} · Your notebook, graded", "",
      "Each claim was reproduced with your own frames and functions first, then restated on the governed frame. Claims are graded, never overwritten.", "",
      "| # | Your claim | Verdict | Governed value |", "|---|---|---|---|"]
cell = lambda x: str(x).replace("|", "/")      # a pipe inside a cell splits a markdown table (defect RQ-3)
L += [f"| {r.hp} | {cell(r.claim)} | **{r.grade.title()}** | {cell(r.governed)} |" for r in N.HP.itertuples()]
L += ["", "### Candid caveats"] + [f"- {x}" for x in N.CAVEATS]
(ROOT / "dp_uc52_mayza_2026_recap_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
assert sum(1 for x in L if x.startswith("## ")) <= 9, "section cap"
print("report md:", len(L), "lines;", sum(1 for x in L if x.startswith("## ")), "sections")
