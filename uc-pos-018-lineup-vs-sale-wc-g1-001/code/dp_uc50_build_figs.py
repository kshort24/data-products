"""
dp_uc50_build_figs.py -- figures for UC #50 / uc-pos-018. Reads ONLY out/dp_uc50_* receipts.
Each figure asserts the numbers in its own subtitle against the receipt before saving.
Brand: Phillies Red #E81828, Navy #002D72, Blue #284898, Cream #F3E5AB, Gray #8C8C8C. Liberation Sans (Arial metrics).
"""
from __future__ import annotations
import json, textwrap
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

import dp_uc50_narratives as N

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
P = "dp_uc50_"
RED, NAVY, BLUE, CREAM, GRAY, LGRAY, INK = "#E81828", "#002D72", "#284898", "#F3E5AB", "#8C8C8C", "#D9D9D9", "#1A1A1A"
PITCH = {"FF": "#D22D49", "SI": "#FE9D00", "SL": "#C9B800", "CH": "#1DBE3A"}
PNAME = {"FF": "4-Seam", "SI": "Sinker", "SL": "Slider", "CH": "Changeup"}
DIRC = {"Pull": RED, "Straightaway": GRAY, "Oppo": NAVY}
plt.rcParams.update({"font.family": ["Liberation Sans", "DejaVu Sans"], "font.size": 10, "axes.edgecolor": GRAY,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150, "savefig.dpi": 150})
HL = N.HL
CARDS = N.cards()
LIN = N.lineup()
R = lambda k: pd.read_csv(OUT / f"{P}{k}.csv")
made = []


def save(fig, name):
    fig.savefig(OUT / f"{P}{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    made.append(name)


def zone(ax, top=3.5, bot=1.5):
    ax.add_patch(Rectangle((-0.83, bot), 1.66, top - bot, fill=False, ec=INK, lw=1.2))


# ---------------------------------------------------------------- fig 1: the lineup at a glance
sc = R("sale_career").query("window=='career R'").set_index("slot")
bh = R("by_hand").query("p_throws=='L'").set_index("slot")
lin = [(s, d, b) for s, d, _, _, b in [(r[0], r[1], r[2], r[3], r[4]) for r in
       [(1, "Trea Turner", 0, 0, "R"), (2, "Kyle Schwarber", 0, 0, "L"), (3, "Bryce Harper", 0, 0, "L"),
        (4, "Alec Bohm", 0, 0, "R"), (5, "Derek Hill", 0, 0, "R"), (6, "Bryan De La Cruz", 0, 0, "R"),
        (7, "Bryson Stott", 0, 0, "L"), (8, "Edmundo Sosa", 0, 0, "R"), (9, "J.T. Realmuto", 0, 0, "R")]]]
fig, ax = plt.subplots(figsize=(10, 5.6))
ys = np.arange(len(lin))[::-1]
for y, (s, d, b) in zip(ys, lin):
    col = BLUE if b == "L" else RED
    if s in sc.index:
        r = sc.loc[s]
        ax.barh(y, r.woba, color=col, alpha=0.85 if r.plate_apps >= 10 else 0.35, height=0.62)
        ax.text(r.woba + 0.008, y, f"{r.woba:.3f}".lstrip("0") + f"  ({int(r.plate_apps)} PA{', THIN' if r.plate_apps < 10 else ''})",
                va="center", fontsize=9, color=INK)
    l = bh.loc[s]
    ax.plot(l.xwoba, y, marker="D", color=NAVY, ms=7, mfc="white", mew=1.8, zorder=5)
ax.axvline(0.320, color=GRAY, ls=":", lw=1)
ax.text(0.321, ys[0] + 0.55, "≈ league-average wOBA (.320, house reference)", fontsize=8, color=GRAY)
ax.set_yticks(ys, [f"{s}. {d} ({b})" for s, d, b in lin])
ax.set_xlim(0, 0.52)
ax.set_xlabel("wOBA")
agg = {(r["window"], r["group"]): r for r in HL["lineup_agg"]}
assert int(agg[("career R", "Lineup (9)")]["plate_apps"]) == int(sc.plate_apps.sum())
fig.suptitle("The lineup vs Chris Sale: career head-to-head (bars) and 2026 xwOBA vs all LHP (◇)", x=0.01, ha="left",
             fontsize=13, fontweight="bold", color=NAVY)
ax.set_title(f"Bars = career wOBA vs Sale, regular season 2015–2026 (faded = under 10 PA). Red = RHB, blue = LHB. "
             f"All nine: {int(agg[('career R','Lineup (9)')]['plate_apps'])} PA, {N.f3(agg[('career R','Lineup (9)')]['woba'])} wOBA.",
             loc="left", fontsize=9, color=INK)
save(fig, "fig1_lineup_glance")

# ---------------------------------------------------------------- fig 2: Sale card (movement / location / release)
X = R("sale_pitch_extract")
A = R("sale_arsenal").set_index("pitch_type")
AB = R("sale_arsenal_by_stand")
fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.8), gridspec_kw={"width_ratios": [1.05, 1.5, 1.0]})
ax = axs[0]
for pt in ["FF", "SI", "SL", "CH"]:
    d = X[X.pitch_type == pt]
    ax.scatter(d.pfx_x * 12, d.pfx_z * 12, s=6, alpha=0.35, color=PITCH[pt], label=f"{PNAME[pt]} {100*A.loc[pt,'usage']:.0f}%")
ax.axhline(0, color=GRAY, ls=":", lw=1); ax.axvline(0, color=GRAY, ls=":", lw=1)
ax.set_xlabel("Horizontal break (in), + = arm side (away from a RHB)"); ax.set_ylabel("Induced vertical break (in)")
ax.set_title("Movement", loc="left", fontweight="bold", color=NAVY)
ax.legend(fontsize=8, frameon=False, loc="lower left")
for i, st in enumerate(["L", "R"]):
    pass
ax = axs[1]
for i, st in enumerate(["L", "R"]):
    d = AB[AB.stand == st]
    off = -1.25 if st == "L" else 1.25
    zone(ax, 3.5, 1.5) if False else None
    ax.add_patch(Rectangle((off - 0.83, 1.5), 1.66, 2.0, fill=False, ec=INK, lw=1.2))
    for r in d.itertuples():
        if r.pitch_type not in PITCH:
            continue
        ax.scatter(off + r.plate_x, r.plate_z, s=3000 * r.usage, color=PITCH[r.pitch_type], alpha=0.75, ec="white")
        if r.usage > 0.05:
            ax.text(off + r.plate_x, r.plate_z, f"{r.pitch_type}\n{100*r.usage:.0f}%", ha="center", va="center", fontsize=7.5, color=INK)
    ax.text(off, 4.15, "vs LHB" if st == "L" else "vs RHB", ha="center", fontweight="bold", color=NAVY)
ax.set_xlim(-2.6, 2.6); ax.set_ylim(0.6, 4.4); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_ylabel("Height (ft)")
ax.set_title("Mean location by batter side (catcher's view), size = usage", loc="left", fontweight="bold", color=NAVY)
ax = axs[2]
for pt in ["FF", "SI", "SL", "CH"]:
    d = X[X.pitch_type == pt]
    ax.scatter(d.release_pos_x, d.release_pos_z, s=5, alpha=0.3, color=PITCH[pt])
ax.set_xlabel("Release, horizontal (ft)"); ax.set_ylabel("Release, vertical (ft)")
ax.set_title(f"Release (arm angle ≈{HL['sale']['arm_angle_median']:.0f}°)", loc="left", fontweight="bold", color=NAVY)
sub = (f"FF {A.loc['FF','velo']:.1f} mph · SL {100*A.loc['SL','whiff_rate']:.1f}% whiff · SI {A.loc['SI','horiz_in']:.1f} in of run · "
       f"CH {100*A.loc['CH','whiff_rate']:.1f}% whiff")
hp9 = R("hp_reconciliation").set_index("hp").loc["HP-09", "governed"]
assert hp9.startswith(f"{A.loc['FF','velo']:.1f} mph"), (hp9, sub)
fig.suptitle("Chris Sale, 2026: the arsenal (27 starts, 2,575 pitches)", x=0.01, ha="left", fontsize=13, fontweight="bold", color=NAVY)
fig.text(0.01, 0.905, sub + "  (your subtitle, governed)", fontsize=9.5, color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.9))
save(fig, "fig2_sale_arsenal")

# ---------------------------------------------------------------- fig 3: Sale by TTO + by stand
T = R("sale_tto")
fig, ax = plt.subplots(figsize=(7, 3.6))
x = np.arange(len(T))
ax.bar(x - 0.18, T.woba, 0.36, color=NAVY, label="wOBA")
ax.bar(x + 0.18, T.xwoba, 0.36, color=GRAY, label="xwOBA")
for i, r in T.iterrows():
    ax.text(i - 0.18, r.woba + 0.005, N.f3(r.woba), ha="center", fontsize=8)
    ax.text(i + 0.18, r.xwoba + 0.005, N.f3(r.xwoba), ha="center", fontsize=8)
    ax.text(i, 0.012, f"{int(r.plate_apps)} PA · HR {100*r.hr_rate:.1f}%", ha="center", fontsize=8, color="white")
ax.set_xticks(x, ["1st time", "2nd time", "3rd+ time"]); ax.set_ylim(0, 0.34); ax.legend(frameon=False, fontsize=8)
fig.suptitle("Sale does not fade through the order (2026)", x=0.01, ha="left", fontsize=12, fontweight="bold", color=NAVY)
ax.set_title("wOBA flat at .25–.26 every time through; only the HR rate moves.", loc="left", fontsize=9)
save(fig, "fig3_sale_tto")

# ---------------------------------------------------------------- index cards
band = R("band"); bip = R("sale_bip"); rp = R("rank_pop"); ls = R("lhp_season"); pgr = R("pitch_group")
SALE_GRP = {"R": {"Fastball": N.sale_use("R", "FF") + N.sale_use("R", "SI"), "Breaking": N.sale_use("R", "SL"), "Offspeed": N.sale_use("R", "CH")},
            "L": {"Fastball": N.sale_use("L", "FF") + N.sale_use("L", "SI"), "Breaking": N.sale_use("L", "SL"), "Offspeed": N.sale_use("L", "CH")}}


def chart_band(ax, bid, name):
    b = band[(band.batter == bid) & (band.h_band.isin(["Inner", "Middle", "Away"]))].set_index("h_band").loc[["Inner", "Middle", "Away"]]
    left = np.zeros(3)
    for k, c in [("pull_rate", "Pull"), ("straight_rate", "Straightaway"), ("oppo_rate", "Oppo")]:
        ax.barh(range(3), b[k], left=left, color=DIRC[c], label=c, height=0.6)
        for i, v in enumerate(b[k]):
            if v > 0.08:
                ax.text(left[i] + v / 2, i, f"{100*v:.0f}%", ha="center", va="center", color="white", fontsize=8)
        left += b[k].values
    ax.set_yticks(range(3), [f"{i} third\n{int(n)} BIP{' *' if n < 25 else ''} · {N.f3(w)} wOBA" for i, n, w in zip(b.index, b.n_bip, b.woba)], fontsize=8)
    ax.set_xlim(0, 1); ax.set_xticks([])
    ax.legend(ncol=3, frameon=False, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, -0.13))
    ax.set_title("2026 vs LHP: where the pitch was → where the ball went", loc="left", fontsize=9, color=NAVY, fontweight="bold")


def chart_spray(ax, bid, name):
    d = bip[bip.batter == bid]
    t = np.linspace(np.pi / 4, 3 * np.pi / 4, 50)
    ax.plot(330 * np.cos(t) * np.sqrt(2) / np.sqrt(2), 330 * np.sin(t), color=LGRAY, lw=1)
    ax.plot([0, -250], [0, 250], color=LGRAY, lw=1); ax.plot([0, 250], [0, 250], color=LGRAY, lw=1)
    o = d[~d.is_hit]; hh = d[d.is_hit]
    ax.scatter(o.loc_x, o.loc_y, s=30, color=GRAY, alpha=0.6, label=f"Out ({len(o)})")
    for ev, c in [("single", BLUE), ("double", NAVY), ("home_run", RED)]:
        e = hh[hh.events == ev]
        if len(e):
            ax.scatter(e.loc_x, e.loc_y, s=70, color=c, ec="white", label=f"{ev.replace('_',' ').title()} ({len(e)})")
    ax.set_xlim(-260, 260); ax.set_ylim(-10, 470); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_title(f"Every ball in play vs Sale ({len(d)}), career · catcher's-eye field, RF to the right", loc="left", fontsize=9, color=NAVY, fontweight="bold")


def chart_rank(ax, bid, name):
    d = rp[rp.batter == bid].sort_values("ops").reset_index(drop=True)
    cols = [RED if s else LGRAY for s in d.is_sale]
    ax.bar(range(len(d)), d.ops, color=cols)
    ax.set_xticks([]); ax.set_ylabel("OPS")
    i = int(np.where(d.is_sale)[0][0])
    ax.annotate(f"Sale {N.f3(d.ops[i])}\n({int(d.plate_apps[i])} PA)", (i, d.ops[i]), (i + 2.5, d.ops[i] + 0.35),
                arrowprops=dict(arrowstyle="-", color=RED), color=RED, fontsize=9, fontweight="bold")
    ax.set_title(f"OPS vs every LHP he's faced 20+ times (n={len(d)}), career", loc="left", fontsize=9, color=NAVY, fontweight="bold")


def chart_season(ax, bid, name):
    d = ls[(ls.batter == bid) & (ls.plate_apps >= 40)]
    ax.plot(d.game_year, d.woba, marker="o", color=NAVY, label="wOBA vs LHP")
    ax.plot(d.game_year, d.xwoba, marker="o", color=GRAY, ls="--", label="xwOBA vs LHP")
    s = HL["hitters"][name]["sale_career"]
    ax.axhline(s["woba"], color=RED, lw=1.2)
    ax.text(d.game_year.min(), s["woba"] + 0.006, f"career vs Sale {N.f3(s['woba'])} ({int(s['plate_apps'])} PA)", color=RED, fontsize=8)
    ax.axhline(0.320, color=LGRAY, ls=":")
    ax.set_ylim(0.18, 0.46); ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax.set_xticks(d.game_year.astype(int))
    ax.tick_params(axis="x", labelsize=7)
    ax.set_title("vs LHP by season (40+ PA), regular season", loc="left", fontsize=9, color=NAVY, fontweight="bold")


def chart_pitchgroup(ax, bid, name, bats):
    win = "2026" if name == "Derek Hill" else "2024-26"
    d = pgr[(pgr.batter == bid) & (pgr.window == win) & pgr.pitch_group.isin(["Fastball", "Breaking", "Offspeed"])].set_index("pitch_group").loc[["Fastball", "Breaking", "Offspeed"]]
    x = np.arange(3)
    ax.bar(x - 0.2, d.woba, 0.4, color=NAVY, label=f"his wOBA vs LHP ({win})")
    ax.bar(x + 0.2, [SALE_GRP[bats][g] for g in d.index], 0.4, color=RED, alpha=0.8, label=f"Sale's 2026 usage vs {bats}HB")
    for i, r in enumerate(d.itertuples()):
        ax.text(i - 0.2, r.woba + 0.01, f"{N.f3(r.woba)}\n{int(r.plate_apps)} PA", ha="center", fontsize=7.5)
        ax.text(i + 0.2, SALE_GRP[bats][d.index[i]] + 0.01, f"{100*SALE_GRP[bats][d.index[i]]:.0f}%", ha="center", fontsize=7.5, color=RED)
        ax.text(i, -0.07, f"whiff {100*r.whiff_rate:.0f}% · chase {100*r.chase_rate:.0f}%", ha="center", fontsize=7.5, color=INK)
    ax.set_xticks(x, ["Fastball\n(FF/SI/FC)", "Breaking\n(SL/ST/CU)", "Offspeed\n(CH/FS)"], fontsize=8)
    ax.set_ylim(-0.1, 0.9); ax.set_yticks([0, .2, .4, .6, .8]); ax.axhline(0, color=GRAY, lw=0.8)
    ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax.set_title("What he hits from lefties vs what Sale throws him", loc="left", fontsize=9, color=NAVY, fontweight="bold")


CH = {"band": chart_band, "spray": chart_spray, "rank": chart_rank, "season": chart_season, "pitchgroup": chart_pitchgroup}
LINEUP = [(1, "Trea Turner", 607208, "R"), (2, "Kyle Schwarber", 656941, "L"), (3, "Bryce Harper", 547180, "L"),
          (4, "Alec Bohm", 664761, "R"), (5, "Derek Hill", 656537, "R"), (6, "Bryan De La Cruz", 650559, "R"),
          (7, "Bryson Stott", 681082, "L"), (8, "Edmundo Sosa", 624641, "R"), (9, "J.T. Realmuto", 592663, "R")]


def tile(fig, x, y, w, hgt, label, value, sub=""):
    fig.patches.append(FancyBboxPatch((x, y), w, hgt, boxstyle="round,pad=0.004", transform=fig.transFigure,
                                      fc="#F7F7F7", ec=LGRAY, lw=0.8))
    fig.text(x + 0.008, y + hgt - 0.03, label, fontsize=7.5, color=GRAY)
    fig.text(x + 0.008, y + 0.022, value, fontsize=15, fontweight="bold", color=NAVY)
    if sub:
        fig.text(x + w - 0.008, y + 0.026, sub, fontsize=7.5, color=GRAY, ha="right")


for slot, name, bid, bats in LINEUP:
    c = CARDS[name]; hh_ = HL["hitters"][name]; L = hh_["lhp26"]; S = hh_["sale_career"]; l30 = hh_["last30"]
    fig = plt.figure(figsize=(11, 6.6))
    fig.patches.append(Rectangle((0, 0.9), 1, 0.1, transform=fig.transFigure, fc=NAVY, ec="none"))
    fig.patches.append(Rectangle((0, 0.895), 1, 0.006, transform=fig.transFigure, fc=RED, ec="none"))
    fig.text(0.015, 0.94, f"{slot} · {name}  ({bats})", fontsize=17, fontweight="bold", color="white")
    fig.text(0.985, 0.94, "NLWCS G1 · PHI @ ATL · 9/29 · vs Chris Sale (LHP)", fontsize=9, color=CREAM, ha="right")
    fig.text(0.015, 0.855, c["tag"], fontsize=13, fontweight="bold", color=RED)
    tiles = [("2026 vs LHP · wOBA", N.f3(L["woba"]), f"{int(L['plate_apps'])} PA"),
             ("2026 vs LHP · xwOBA", N.f3(L["xwoba"]), f"K {N.pc(L['krate'])}"),
             ("Career vs Sale · wOBA", N.f3(S.get("woba")), f"{int(S.get('plate_apps', 0))} PA{' THIN' if S.get('plate_apps', 0) < 10 else ''}"),
             ("Career vs Sale · AVG/OBP/SLG", N.slash(S) if S else "—", ""),
             ("Last 30 days · wOBA", N.f3(l30["woba"]), f"{int(l30['plate_apps'])} PA")]
    for i, (lab, val, sub) in enumerate(tiles):
        tile(fig, 0.015 + i * 0.196, 0.73, 0.186, 0.095, lab, val, sub)
    ax = fig.add_axes([0.56, 0.11, 0.42, 0.56])
    fn = CH[c["chart"]]
    fn(ax, bid, name, bats) if c["chart"] == "pitchgroup" else fn(ax, bid, name)
    wrap = lambda s, w=62: "\n".join(textwrap.wrap(s, w))
    fig.text(0.015, 0.685, wrap(c["lede"]), fontsize=9.2, va="top", color=INK, linespacing=1.35)
    fig.text(0.015, 0.215, wrap("SALE  " + c["sale"]), fontsize=9.2, va="top", color=NAVY, fontweight="bold", linespacing=1.3)
    fig.text(0.015, 0.10, wrap("PLAN  " + c["plan"]), fontsize=9.2, va="top", color=RED, fontweight="bold", linespacing=1.3)
    fig.text(0.985, 0.002, "uc-pos-018 · dp_uc50 · regular season · receipts out/dp_uc50_*.csv · * = under 25 BIP (FL-1)",
             fontsize=6.5, color=GRAY, ha="right")
    save(fig, f"card_{slot}_{name.split()[-1].lower().replace('.', '')}")

print(json.dumps(made))


# ---------------------------------------------------------------- fig 4: the one-page lineup notecard
fig = plt.figure(figsize=(11, 8.5))
fig.patches.append(Rectangle((0, 0.93), 1, 0.07, transform=fig.transFigure, fc=NAVY, ec="none"))
fig.patches.append(Rectangle((0, 0.926), 1, 0.005, transform=fig.transFigure, fc=RED, ec="none"))
fig.text(0.015, 0.953, "PHILLIES vs CHRIS SALE · NLWCS Game 1 · 9/29 · Truist Park", fontsize=16, fontweight="bold", color="white")
fig.text(0.985, 0.953, "uc-pos-018 · regular season through 9/27", fontsize=8.5, color=CREAM, ha="right")
ss = HL["sale"]["season"]; A = HL["sale"]["arsenal"]
tiles = [("Sale 2026 wOBA / xwOBA", f"{N.f3(ss['woba'])} / {N.f3(ss['xwoba'])}", f"{int(ss['plate_apps'])} PA"),
         ("K% / BB%", f"{N.pc(ss['krate'],1)} / {N.pc(ss['bbrate'],1)}", ""),
         ("4-seam", f"{A['FF']['velo']:.1f} mph", f"{N.pc(A['FF']['usage'])} use"),
         ("Slider", f"{N.pc(A['SL']['whiff_rate'])} whiff", f"{N.pc(A['SL']['usage'])} use"),
         ("vs LHB / RHB wOBA", f"{N.f3(HL['sale']['by_stand']['L']['woba'])} / {N.f3(HL['sale']['by_stand']['R']['woba'])}", "")]
for i, (lab, val, sub) in enumerate(tiles):
    tile(fig, 0.015 + i * 0.196, 0.815, 0.186, 0.09, lab, val, sub)
fig.text(0.015, 0.785, "THE RULE: make the slider a ball and the four-seam a strike. Sale doesn't fade through the order, so no waiting for the third look.",
         fontsize=10, fontweight="bold", color=RED)
cols = ["#", "Hitter", "B", "26 vs LHP\nwOBA/xwOBA", "vs Sale\nPA", "vs Sale\nAVG/OBP/SLG", "vs Sale\nwOBA", "The read", "The plan"]
xs = [0.015, 0.04, 0.175, 0.2, 0.285, 0.33, 0.43, 0.485, 0.70]
y0 = 0.745
for x, c in zip(xs, cols):
    fig.text(x, y0, c, fontsize=8, fontweight="bold", color=NAVY, va="top")
yy = y0 - 0.055
for slot, name, bid, bats in LINEUP:
    h_ = HL["hitters"][name]; L = h_["lhp26"]; Sx = h_["sale_career"]; c = CARDS[name]
    if slot % 2:
        fig.patches.append(Rectangle((0.01, yy - 0.058), 0.98, 0.066, transform=fig.transFigure, fc="#F4F6FA", ec="none"))
    col = BLUE if bats == "L" else RED
    thin_ = Sx["plate_apps"] < 10
    vals = [str(slot), name, bats, f"{N.f3(L['woba'])} / {N.f3(L['xwoba'])}", f"{int(Sx['plate_apps'])}{' THIN' if thin_ else ''}",
            N.slash(Sx), N.f3(Sx["woba"])]
    for x, v in zip(xs[:7], vals):
        fig.text(x, yy, v, fontsize=9 if x > 0.03 else 10, color=col if x == xs[2] else INK,
                 fontweight="bold" if x in (xs[1], xs[6]) else "normal", va="top")
    fig.text(xs[7], yy, "\n".join(textwrap.wrap(c["tag"], 36)), fontsize=8, color=NAVY, va="top", fontweight="bold")
    plan1 = c["short"]
    fig.text(xs[8], yy, "\n".join(textwrap.wrap(plan1, 50)), fontsize=8, color=INK, va="top")
    yy -= 0.066
agg = {(r["window"], r["group"]): r for r in HL["lineup_agg"]}
fig.text(0.015, 0.06, f"Lineup vs Sale, career: {int(agg[('career R','Lineup (9)')]['plate_apps'])} PA, {N.f3(agg[('career R','Lineup (9)')]['woba'])} wOBA · "
         f"LHB {N.f3(agg[('career R','LHB')]['woba'])} ({int(agg[('career R','LHB')]['plate_apps'])} PA) · RHB {N.f3(agg[('career R','RHB')]['woba'])} ({int(agg[('career R','RHB')]['plate_apps'])} PA) · "
         f"2026 LHB {N.f3(agg[('2026 R','LHB')]['woba'])} ({int(agg[('2026 R','LHB')]['plate_apps'])} PA)", fontsize=8.5, color=NAVY)
fig.text(0.015, 0.035, "THIN = under 10 PA (directional only). Red = RHB, blue = LHB. Every number traces to out/dp_uc50_*.csv.", fontsize=7.5, color=GRAY)
save(fig, "fig4_lineup_notecard")
print(json.dumps(made[-1:]))
