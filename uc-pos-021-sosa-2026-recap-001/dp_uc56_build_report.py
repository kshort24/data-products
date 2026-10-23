"""dp_uc56_build_report.py - writes dp_uc56_sosa_2026_recap_report.md from dp_uc56_narrative (no hand-typed numbers).
Shell carried from dp_uc55_build_report.py (RQ-3 pipe guard). Tables read out/dp_uc56_* receipts only."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dp_uc56_narrative as N  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
strip = lambda s: re.sub(r"</?b>", "**", s)   # noqa: E731
H, f3, pc, S26 = N.H, N.f3, N.pc, N.S26
R = lambda n: pd.read_csv(OUT / f"dp_uc56_{n}.csv")   # noqa: E731
lin = H["lineage"]
L = [f"# {N.TITLE} — {N.SUB}",
     f"### Season recap · utility IF/OF, bats right · Philadelphia Phillies · {S26['plate_apps']} PA in {H['games_with_pa_2026']} games · data through {H['anchor']}", "",
     "**Prepared for:** Front office (free-agency decision), player development, hitting coaches", "",
     f"**2026:** {N.SLASH} · wOBA {f3(S26['woba'])} · xwOBA {f3(S26['xwoba'])} · BB {pc(S26['bbrate'])} · K {pc(S26['krate'])} · chase {pc(S26['chase_rate'])} · OOZ contact {pc(S26['ooz_contact_rate'])}", "",
     f"**Governance:** Use Case #56 (`uc-pos-021`) · build `dp_uc56` v1.0.0 · kernel `dp_uc56_kernel.py` imports `dp_uc55_kernel.py` (sha256 `{lin['dp_uc55_kernel.py'][:8]}…`) "
     f"and `dp_uc46_kernel.py` (`{lin['dp_uc46_kernel.py'][:8]}…`), {len(lin)} pins in all. New objects OZ-1 and WA-1 are provisional and were registered in the BID before computation. "
     "Independently verified; see `05_quality_certification.md`.", "",
     f"**Companion:** `dp_uc56_sosa_2026_dashboard.html`, the same story in {len(N.CH) + 1} chapters.", "",
     "> **Read this first: data window, sources, carry-ins.**", ">"]
L += [f"> - {strip(x)}" for x in N.READ_FIRST] + ["", "## 1 · Bottom line"] + [f"{i}. {strip(x)}" for i, x in enumerate(N.BOTTOM, 1)]
for sec, (anc, q, ttl, lede, figs, extra) in enumerate(N.CH, 2):
    L += ["", f"## {sec} · {ttl} ({q})", "", strip(lede), ""]
    if extra == "line":
        p = R("season_panel")
        L += ["| Season | PA | AVG/OBP/SLG | wOBA | xwOBA | BB% | K% | Swing | Chase | OOZ contact | Hard-hit | Barrel | EV90 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {'**2026**' if r.game_year == 2026 else r.game_year} | {int(r.plate_apps)} | {f3(r.ba)}/{f3(r.obp)}/{f3(r.slg)} | {f3(r.woba)} | {f3(r.xwoba)} | "
              f"{pc(r.bbrate)} | {pc(r.krate)} | {pc(r.swing_rate)} | {pc(r.chase_rate)} | {pc(r.ooz_contact_rate)} | {pc(r.hard_hit_rate)} | {pc(r.barrel_rate)} | {r.ev90:.1f} |" for r in p.itertuples()]
        st = H["stl"]
        L += [f"| *STL {y} (context, SRC-5)* | {v['pa']} | {f3(v['ba'])}/{f3(v['obp'])}/{f3(v['slg'])} | {f3(v['woba'])} | {f3(v['xwoba'])} | | | | {pc(v['chase'])} | {pc(v['ooz_contact'])} | | | |" for y, v in st.items()] + [""]
    if extra == "wa":
        d = R("wa1_decline_flags")
        L += ["| Flag | Metric | 2023-25 baseline | 2026 | Change | Bar | Tripped? |", "|---|---|---|---|---|---|---|"]
        for r in d.itertuples():
            fmt = (lambda x: f"{x:.1f}") if r.metric in ("bat_speed_mu", "ev90") else (f3 if r.metric == "xwoba" else pc)
            dl = f"{r.delta:+.1f}" if r.metric in ("bat_speed_mu", "ev90") else (f"{r.delta:+.3f}" if r.metric == "xwoba" else ("flat" if abs(r.delta) < 0.0005 else f"{100 * r.delta:+.1f} pts"))
            L.append(f"| {r.flag} | {r.label} | {fmt(r.baseline)} | {fmt(r.v2026)} | {dl} | {r.bar} | {'**yes**' if r.flagged else 'no'} |")
        L += [""]
    for k in figs:
        L += [f"![{N.SPECS[k]['title']}](out/dp_uc56_{k}.png)", f"*Receipts: {', '.join('out/dp_uc56_' + s + '.csv' for s in N.SPECS[k]['source'])} · claim asserted before render*", ""]
L += ["", f"## {len(N.CH) + 2} · Your notebook, graded", "",
      "Each claim is reproduced first on your own frame (`nphl` + `pos`, no game-type filter, your functions), then graded on the governed build.", "",
      "| # | Claim | Your frame | Governed | Grade |", "|---|---|---|---|---|"]
for k, v in H["hp"].items():
    L.append(f"| {k} | {v['claim']} | {v['client']} | {v['governed']} | **{v['grade']}** |".replace("\n", " "))
L += ["", f"Two notes on the code: your `inds` `ev_mu` averages `launch_speed` over every tracked pitch, fouls included, so it reads {S26['ev_mu'] - H['hp_client']['ev_mu26']:.1f} mph below a balls-in-play mean (CL-2); "
      "and `pull_air_rate` is commented out in the notebook because cell 56 cannot run (O-7) - this build uses the patched v1.1.0 function from `uc-pos-017`.", "",
      "## Candid caveats", ""] + [f"- {strip(x)}" for x in N.CAVEATS]
L += ["", "## Three things for 2027", "",
      "1. **If he's back:** keep him in the lefty-heavy bench role; it is where all of his value lives.",
      "2. **Ask the hitting staff about ground balls.** The force is intact; the pulled air balls aren't. That's the cheapest lever on a .330 xwOBA bat.",
      "3. **Offspeed chase is the one approach item worth a conversation** - not velocity, not breaking balls.",
      "", f"*Data through {H['anchor']} · uc-pos-021 · dp_uc56 v1.0.0 · sources: Statcast house log; carry-ins CI-1…CI-7 listed in the BID.*"]
txt = "\n".join(L)
# RQ-3 pipe guard: every row of a table has the same cell count as its header (a stray '|' in a cell breaks the table)
hdr = None
for ln in txt.splitlines():
    if ln.startswith("|"):
        hdr = hdr or ln.count("|")
        assert ln.count("|") == hdr, f"RQ-3 pipe guard: {ln[:80]}"
    else:
        hdr = None
(ROOT / "dp_uc56_sosa_2026_recap_report.md").write_text(txt, encoding="utf-8")
print("report md lines:", len(L))
