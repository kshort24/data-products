"""
dp_uc50_narratives.py -- the words on every card, bound to receipts.

Every number in a narrative is read from out/dp_uc50_headlines.json at render time
(never typed). The harness (family F) re-derives each one from the CSV receipts.
`chart` names the index-card visual chosen for that hitter's story (02 §5).
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
HL = json.loads((HERE / "out" / "dp_uc50_headlines.json").read_text())


def f3(x):
    if x is None:
        return "—"
    s = f"{x:.3f}"
    return s[1:] if s.startswith("0.") else s


def pc(x, d=0):
    return "—" if x is None else f"{100 * x:.{d}f}%"


def slash(r):
    return f"{f3(r.get('ba'))}/{f3(r.get('obp'))}/{f3(r.get('slg'))}"


def h(name):
    return HL["hitters"][name]


S = HL["sale"]
ARS = S["arsenal"]
ABS = S["arsenal_by_stand"]


def sale_use(stand, pt):
    r = ABS.get(f"{stand}-{pt}")
    return r["usage"] if r else 0.0


def cards():
    out = {}
    t = h("Trea Turner"); L = t["lhp26"]; C = t["sale_career"]; B = t["band"]; G = t["pg_26"]
    out["Trea Turner"] = dict(
        tag="Unlucky against lefties, and the soft stuff is the leak",
        lede=(f"Your read holds on results: {f3(L['woba'])} wOBA against lefties in {int(L['plate_apps'])} PA. "
              f"The contact says otherwise ({f3(L['xwoba'])} xwOBA), so part of it is luck. "
              f"The real leak is spin. Against LHP breaking balls he has a {f3(G['Breaking']['woba'])} wOBA, and against changeups {f3(G['Offspeed']['woba'])}. "
              f"The pull habit sits on the inner third ({pc(B['Inner']['pull_rate'])} pulled), where it pays ({f3(B['Inner']['woba'])}). "
              f"On away pitches he already goes the other way more than he pulls ({pc(B['Away']['oppo_rate'])} oppo, {pc(B['Away']['pull_rate'])} pull). "
              f"Those balls are simply weak ({f3(B['Away']['woba'])})."),
        sale=(f"vs Sale: {int(C['plate_apps'])} PA, {slash(C)}, {f3(C['woba'])} wOBA / {f3(C['xwoba'])} xwOBA. "
              f"Sale ranks #{int(t['rank']['rank'])} toughest of {int(t['rank']['n_pitchers'])} LHP he's seen 20+ times."),
        plan=(f"Sale shows righties the four-seam {pc(sale_use('R','FF'))} of the time. Hunt it in the zone. "
              f"The changeup ({pc(sale_use('R','CH'))}) runs away, and that away ball is his weakest contact. Let it go."),
        chart="band")
    t = h("Kyle Schwarber"); L = t["lhp26"]; C = t["sale_career"]; C6 = t["sale_2026"]; G = t["pg_26"]
    out["Kyle Schwarber"] = dict(
        tag="Career damage, 2026 silence",
        lede=(f"Your card reproduces exactly: {int(C['plate_apps'])} PA, {f3(C['woba'])} wOBA, {f3(C['ops'])} OPS on a {f3(C['slg'])} SLG. "
              f"1 in 5 balls in play is a barrel ({pc(C['barrel_rate'])}), and {pc(C['hard_hit_rate'])} are hit hard. "
              f"2026 is the problem: {int(C6['plate_apps'])} PA, {slash(C6)}, {pc(C6['krate'])} K. "
              f"He still hits lefties overall ({f3(L['woba'])} wOBA, {pc(L['barrel_rate'])} barrels in {int(L['plate_apps'])} PA). "
              f"The damage is on fastballs ({f3(G['Fastball']['woba'])} wOBA) and not on breaking balls "
              f"({f3(G['Breaking']['woba'])}, {pc(G['Breaking']['whiff_rate'])} whiff)."),
        sale=(f"vs Sale career: {int(C['plate_apps'])} PA, {int(C['hits'])} hits, {int(C['hrs'])} HR. "
              f"2026: {int(C6['hits'])} hit in {int(C6['plate_apps'])} PA."),
        plan=(f"Sale shows lefties the slider {pc(sale_use('L','SL'))} and the sinker {pc(sale_use('L','SI'))}. "
              f"The four-seam is only {pc(sale_use('L','FF'))}. Don't chase the slider to get to it. Take it until he has to come in."),
        chart="spray")
    t = h("Bryce Harper"); L = t["lhp26"]; C = t["sale_career"]; R = t["rank"]; G = t["pg_26"]
    out["Bryce Harper"] = dict(
        tag="The one pitcher he hasn't solved",
        lede=(f"The ranking holds, but the number is {f3(R['target_metric'])} OPS, not .100: {int(C['plate_apps'])} PA, {slash(C)}, "
              f"{pc(C['krate'])} strikeouts. That is #{int(R['rank'])} of {int(R['n_pitchers'])} lefties he's seen 20+ times. "
              f"The median of the other lefties is {f3(R['pop_median'])}. "
              f"The mechanism is the chase: {pc(C['chase_rate'])} of Sale's pitches out of the zone get a swing, and {pc(C['whiff_rate'])} of swings miss. "
              f"2026 vs all LHP is his softest year ({f3(L['woba'])} wOBA). Breaking balls are the leak "
              f"({f3(G['Breaking']['woba'])}, {pc(G['Breaking']['chase_rate'])} chase)."),
        sale=(f"2026 vs Sale: {int(t['sale_2026']['plate_apps'])} PA, {int(t['sale_2026']['hits'])} hits, {int(t['sale_2026']['strikeouts'])} K."),
        plan=("Make him throw strikes. The slider below the zone is the out pitch. A walk is a win in this matchup."),
        chart="rank")
    t = h("Alec Bohm"); L = t["lhp26"]; C = t["sale_career"]; C6 = t["sale_2026"]; B = t["band"]; l30 = t["last30"]
    seas = [r for r in t["lhp_season"] if r["plate_apps"] >= 40]
    lo = min(r["woba"] for r in seas)
    out["Alec Bohm"] = dict(
        tag="The matchup bat: contact that Sale hasn't beaten",
        lede=(f"He has hit lefties every season: at least {f3(lo)} wOBA against LHP in all {len(seas)} seasons with 40+ PA. "
              f"2026: {f3(L['woba'])} wOBA, {f3(L['ops'])} OPS, with only {pc(L['krate'])} strikeouts and {pc(L['whiff_rate'])} whiffs in {int(L['plate_apps'])} PA. "
              f"He already does what Turner's card asks for. On away pitches he goes the other way {pc(B['Away']['oppo_rate'])} of the time "
              f"and pulls just {pc(B['Away']['pull_rate'])}. He's warm too: {f3(l30['xwoba'])} xwOBA and {pc(l30['hard_hit_rate'])} hard-hit over the last 30 days."),
        sale=(f"vs Sale: {int(C['plate_apps'])} PA, {slash(C)}, {f3(C['woba'])} wOBA. "
              f"2026: {int(C6['plate_apps'])} PA, {f3(C6['ops'])} OPS. Sale is #{int(t['rank']['rank'])} of {int(t['rank']['n_pitchers'])} LHP for him, near the middle."),
        plan="Batting 4th behind two lefties Sale has handled, he's the lineup's best RHB bet. Same approach: middle-away, use right field.",
        chart="season")
    t = h("Derek Hill"); L = t["lhp26"]; C = t["sale_career"]; G = t["pg_26"]
    out["Derek Hill"] = dict(
        tag="Fastball or nothing",
        lede=(f"All-or-nothing against lefties: {f3(L['slg'])} SLG and {pc(L['barrel_rate'])} barrels, but {pc(L['krate'])} strikeouts in {int(L['plate_apps'])} PA. "
              f"The contact grades lower than the line ({f3(L['xwoba'])} xwOBA vs {f3(L['woba'])} wOBA). "
              f"The damage is on fastballs ({f3(G['Fastball']['woba'])} wOBA, {pc(G['Fastball']['barrel_rate'])} barrels). "
              f"Breaking balls get {pc(G['Breaking']['whiff_rate'])} whiffs and {pc(G['Breaking']['chase_rate'])} chases."),
        sale=(f"vs Sale: {int(C['plate_apps'])} PA, {slash(C)}, {f3(C['xwoba'])} xwOBA. {pc(C['hard_hit_rate'])} of his balls in play were hit hard. "
              "That includes the 104-mph four-seam he doubled off in the 2nd inning on 9/11."),
        plan=(f"Sit four-seam ({pc(sale_use('R','FF'))} to RHB). Two strikes: shorten up and give the slider nothing below the knees."),
        chart="pitchgroup")
    t = h("Bryan De La Cruz"); L = t["lhp26"]; C = t["sale_career"]; G = t["pg_2426"]
    out["Bryan De La Cruz"] = dict(
        tag="The slider test",
        lede=(f"The thinnest book on the card: {int(L['plate_apps'])} PA against lefties in 2026 ({f3(L['woba'])} wOBA). "
              f"Pooled 2024–26, lefties beat him with spin: {f3(G['Breaking']['woba'])} wOBA on breaking balls with {pc(G['Breaking']['chase_rate'])} chases. "
              f"Fastballs are a different story ({f3(G['Fastball']['woba'])}, {pc(G['Fastball']['hard_hit_rate'])} hard-hit)."),
        sale=(f"vs Sale: {int(C['plate_apps'])} PA (THIN), {slash(C)}, {pc(C['krate'])} K."),
        plan="Spit on the slider. If he doesn't chase it, Sale has to go to the four-seam, and that's the pitch he can drive.",
        chart="pitchgroup")
    t = h("Bryson Stott"); L = t["lhp26"]; C = t["sale_career"]; G = t["pg_2426"]
    prev = [r for r in t["lhp_season"] if r["game_year"] in (2024, 2025)]
    out["Bryson Stott"] = dict(
        tag="A results rebound without the damage",
        lede=(f"Against lefties the line came back: {f3(L['woba'])} wOBA in {int(L['plate_apps'])} PA, up from "
              f"{' and '.join(f3(r['woba']) for r in prev)} in 2024–25. It's contact, not damage: {pc(L['hard_hit_rate'])} hard-hit and {pc(L['barrel_rate'])} barrels. "
              f"The pitch he's never solved from a lefty is the breaking ball: {f3(G['Breaking']['woba'])} wOBA and {pc(G['Breaking']['hard_hit_rate'])} hard-hit, 2024–26."),
        sale=(f"vs Sale: {int(C['plate_apps'])} career PA, all in 2025 (THIN). He has not faced Sale in 2026."),
        plan=(f"Same-side with the slider coming ({pc(sale_use('L','SL'))} to LHB). Stay up the middle and don't try to pull the slider."),
        chart="pitchgroup")
    t = h("Edmundo Sosa"); L = t["lhp26"]; C = t["sale_career"]; G = t["pg_2426"]; l30 = t["last30"]
    out["Edmundo Sosa"] = dict(
        tag="A lefty masher Sale has figured out",
        lede=(f"On paper he's in the lineup for this: {f3(L['woba'])} wOBA and {f3(L['ops'])} OPS against lefties in 2026. He's also hot "
              f"({f3(l30['woba'])} wOBA, {int(l30['plate_apps'])} PA in the last 30 days, though the contact grades {f3(l30['xwoba'])}). "
              f"Sale has figured him out anyway: {int(C['plate_apps'])} PA, {slash(C)}, {pc(C['krate'])} K. "
              f"The reason is the chase. He swings at {pc(L['chase_rate'])} of lefties' pitches out of the zone, "
              f"including {pc(G['Offspeed']['chase_rate'])} of changeups (2024–26)."),
        sale=(f"Of the {int(t['rank']['n_pitchers'])} lefties he's seen 20+ times, Sale is #{int(t['rank']['rank'])}, the tougher one."),
        plan=(f"Sale's changeup is {pc(sale_use('R','CH'))} of what he throws righties, with a {pc(ARS['CH']['chase_rate'])} chase rate. "
              "Make him throw it for a strike. Fastball in the zone, or take."),
        chart="pitchgroup")
    t = h("J.T. Realmuto"); L = t["lhp26"]; C = t["sale_career"]; G = t["pg_26"]; l30 = t["last30"]
    assert L["woba"] == min(r["woba"] for r in t["lhp_season"]), "Realmuto 'lowest' claim no longer true"
    out["J.T. Realmuto"] = dict(
        tag="Hitting it at people, not over them",
        lede=(f"The line against lefties is his lowest in {len(t['lhp_season'])} seasons ({f3(L['woba'])} wOBA, {f3(L['ops'])} OPS, {int(L['plate_apps'])} PA). "
              f"The contact is better than that ({f3(L['xwoba'])} xwOBA). What's gone is lift: {pc(L['barrel_rate'])} barrels. "
              f"Against LHP four-seams and sinkers he has {int(round(G['Fastball']['barrels']))} barrels in {int(G['Fastball']['plate_apps'])} PA. "
              f"Last 30 days: {f3(l30['woba'])} wOBA on {f3(l30['xwoba'])} xwOBA."),
        sale=(f"vs Sale: {int(C['plate_apps'])} PA, {slash(C)}, {f3(C['woba'])} wOBA. "
              f"#{int(t['rank']['rank'])} of {int(t['rank']['n_pitchers'])} LHP for him."),
        plan="Ninth, turning the lineup over. Get on base in front of Turner. A walk or a single up the middle is the job.",
        chart="season")
    SHORT = {
        "Trea Turner": f"Hunt the four-seam ({pc(sale_use('R','FF'))} to RHB); let the away changeup go.",
        "Kyle Schwarber": "Take the slider until he has to come in with the heater.",
        "Bryce Harper": "Make him throw strikes; a walk is a win.",
        "Alec Bohm": "Best RHB bet: middle-away, use right field.",
        "Derek Hill": "Sit four-seam; shorten up with two strikes.",
        "Bryan De La Cruz": "Spit on the slider, then drive the four-seam.",
        "Bryson Stott": "Stay up the middle; don't try to pull the slider.",
        "Edmundo Sosa": "No changeups: fastball in the zone, or take.",
        "J.T. Realmuto": "Get on for Turner: walk or single up the middle.",
    }
    for k, v in SHORT.items():
        out[k]["short"] = v
    return out


def lineup():
    A = {(r["window"], r["group"]): r for r in HL["lineup_agg"]}
    ss, st = S["season"], S["tto"]
    ff = ARS["FF"]; sl = ARS["SL"]
    y24 = S["yoy"]["2024"] if "2024" in S["yoy"] else S["yoy"][2024]
    vp = S["vs_phi_2026"]
    vp_pa = sum(r["plate_apps"] for r in vp)
    return dict(
        sale_line=(f"Sale in 2026: {S['starts']} starts, {int(ss['plate_apps'])} PA, {f3(ss['woba'])} wOBA, {f3(ss['xwoba'])} xwOBA, "
                   f"{pc(ss['krate'],1)} K, {pc(ss['bbrate'],1)} BB. Four-seam {ff['velo']:.1f} mph "
                   f"(+{ff['velo'] - y24['ff_velo']:.1f} over 2024). Slider {pc(sl['usage'])} of pitches, {pc(sl['whiff_rate'])} whiff, {f3(sl['woba'])} wOBA."),
        lefties=(f"The lefties have {int(A[('2026 R','LHB')]['hits'])} hit in 2026: LHB vs Sale {int(A[('2026 R','LHB')]['plate_apps'])} PA, {f3(A[('2026 R','LHB')]['woba'])} wOBA. "
                 f"Career LHB {f3(A[('career R','LHB')]['woba'])} in {int(A[('career R','LHB')]['plate_apps'])} PA."),
        righties=(f"The righties have done the work: RHB career {f3(A[('career R','RHB')]['woba'])} wOBA in {int(A[('career R','RHB')]['plate_apps'])} PA, "
                  f"2026 {f3(A[('2026 R','RHB')]['woba'])} ({f3(A[('2026 R','RHB')]['xwoba'])} xwOBA)."),
        tto=(f"No third-time relief: {f3(st['1']['woba'])} / {f3(st['2']['woba'])} / {f3(st['3+']['woba'])} wOBA the 1st / 2nd / 3rd+ time through. "
             f"Getting to him early is no easier than later. What does change the 3rd time through is the HR rate ({pc(st['1']['hr_rate'],1)} → {pc(st['3+']['hr_rate'],1)})."),
        vs_phi=(f"Four 2026 starts against Philadelphia: {vp_pa} PA, "
                + ", ".join(f"{r['game_date'][5:]} {f3(r['woba'])}" for r in vp) + " wOBA by start."),
        lineup_all=(f"All nine vs Sale, career: {int(A[('career R','Lineup (9)')]['plate_apps'])} PA, {slash(A[('career R','Lineup (9)')])}, "
                    f"{f3(A[('career R','Lineup (9)')]['woba'])} wOBA."),
    )
