"""
dp_uc48_verification.py — independent verification harness for UC #48 / uc-pps-033.

Families
  A · kernel fixtures           hand-built frames with known answers (incl. the two build-caught defects)
  B · frame invariants          the career frame rebuilt from parquet WITHOUT the kernel
  C · independent recompute     every headline KPI recomputed with plain pandas, not the kernel
  D · surface consistency       dashboard payload / figure JSON / PNGs == receipts; offline; artifact variant
  E · governance                DQ 0 FAIL, brand compliance, parent hash, package manifest
  F · narrative-to-receipt      numbers the report and dashboard assert, re-derived from receipts and
                                required to appear, formatted, in the text
Run:  MLB_DATA_ROOT=<MLB repo> python dp_uc48_verification.py   [PKG_DIR=<control-plane folder>]
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

import dp_uc48_kernel as K

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC48_OUT", HERE / "out"))
PKG = Path(os.environ.get("PKG_DIR", HERE / "pkg"))
ROOT = K.ROOT
H = json.loads((OUT / "dp_uc48_headlines.json").read_text())
R = lambda n: pd.read_csv(OUT / f"dp_uc48_{n}.csv")          # noqa: E731
LOG: list = []


def check(fam, name, ok, detail=""):
    LOG.append(dict(family=fam, check=name, result="PASS" if bool(ok) else "FAIL", detail=str(detail)[:300]))


def close(a, b, tol=1e-6):
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol


# =============================================================================
# A · kernel fixtures
# =============================================================================
toy = pd.DataFrame(dict(pid=[1] * 6, game_pk=[1, 1, 1, 2, 2, 2], at_bat_number=[1, 1, 2, 1, 2, 3],
                        bat_score=[0, 0, 1, 3, 3, 4], post_bat_score=[0, 1, 1, 3, 4, 6]))
rc = K.runs_created(['pid'], toy)
check("A", "runs_created sums max(post)-min(bat) per PA", rc.runs_created.iat[0] == 1 + 0 + 0 + 1 + 2, rc.to_dict())
check("A", "signature PRESENT on threshold move (+1)", K.signature_verdict(0.30, 0.40, 1, 0.05) == "PRESENT")
check("A", "signature WEAK when p >= .05", K.signature_verdict(0.30, 0.40, 1, 0.05, 0.2) == "WEAK")
check("A", "signature CONTRA on opposite move", K.signature_verdict(0.67, 0.60, 1, 0.03) == "CONTRA")
check("A", "signature ABSENT when |Δ| < threshold/4", K.signature_verdict(97.04, 96.92, -1, 0.5) == "ABSENT")
check("A", "signature direction −1 PRESENT", K.signature_verdict(21.4, 16.4, -1, 3) == "PRESENT")
check("A", "rollup STRONG / SUPPORTED / MIXED / UNSUPPORTED",
      [K.strength_from_signatures(v) for v in (["PRESENT"] * 3, ["PRESENT", "PRESENT", "WEAK"], ["PRESENT", "CONTRA"], ["CONTRA", "WEAK"])]
      == ["STRONG", "SUPPORTED", "MIXED", "UNSUPPORTED"])
pop = pd.DataFrame(dict(k=[.10, .20, .30, .40, .50]))
check("A", "house_percentile higher-better", K.house_percentile(pop, 'k', .40, True) == dict(n=5, percentile=60, rank=2))
check("A", "house_percentile lower-better", K.house_percentile(pop, 'k', .20, False) == dict(n=5, percentile=60, rank=2))
cs = K.count_state(pd.DataFrame(dict(balls=[0, 3, 1, 2, 3], strikes=[0, 1, 2, 1, 2])))   # (2,1) is behind
check("A", "count_state precedence (2K first)", cs.tolist() == ['even', 'behind', '2K', 'behind', '2K'], cs.tolist())
# B-1 regression: entry runners must come from the FIRST pitch, not the first non-null
ap = pd.DataFrame(dict(game_pk=[9, 9], at_bat_number=[1, 2], pitch_number=[1, 1], game_date=['2026-01-01'] * 2, game_year=[2026] * 2,
                       home_team=['PHI'] * 2, away_team=['NYM'] * 2, inning=[8, 8], outs_when_up=[0, 1], on_1b=[np.nan, 123.0],
                       on_2b=[np.nan] * 2, on_3b=[np.nan] * 2, bat_score=[0, 0], fld_score=[1, 1], post_bat_score=[0, 0],
                       pitcher_days_since_prev_game=[2, 2], pitch_type=['FF', 'SL'], release_speed=[97.0, 87.0]))
check("A", "B-1 regression: clean entry stays clean (head(1), not first())", int(K.appearance_log(ap).entry_runners.iat[0]) == 0)
# O-25: notebook quantization vs governed
q = pd.DataFrame(dict(player_name=['X'] * 2, game_year=[2026] * 2, p_throws=['R'] * 2, pitch_type=['FF'] * 2, pitch_name=['4-Seam Fastball'] * 2,
                      des=['a', 'b'], release_speed=[97, 97], release_spin_rate=[2400, 2400], zone=[5, 5], pfx_x=[-.6, -.6],
                      plate_x=[0, 0], pfx_z=[1.47, 1.47], plate_z=[3, 3]))
pm = K.pitch_mix(q)
check("A", "O-25: pitch_mix rounds pfx_z to 0.1 ft → 18.0 in (true 17.64)", round(pm.pfx_z.iat[0] * 12, 1) == 18.0 and round(1.47 * 12, 2) == 17.64)
check("A", "rv100 sign flip (pitcher POV)", close(K.rv100(pd.Series([-0.02, -0.04])), 3.0))

# =============================================================================
# B · frame invariants (no kernel)
# =============================================================================
ph = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(str(ROOT / "data" / "phillies" / "phils_*.parquet")))], ignore_index=True)
fl = pd.read_parquet(ROOT / "data" / "opponents" / "bowlan.parquet")
key = ["game_pk", "at_bat_number", "pitch_number"]
mine = ph[(ph.pitcher == 680742) & (ph.game_type == 'R')]
f_r = fl[(fl.pitcher == 680742) & (fl.game_type == 'R')]
union = pd.concat([mine[mine.phillies_role == 'pitching'], f_r, mine[mine.phillies_role == 'batting']]).drop_duplicates(key)
B, rec = K.career_frame()
check("B", "career frame rows == independent union", len(union) == len(B), (len(union), len(B)))
check("B", "rows per season match", union.game_year.value_counts().sort_index().to_dict() == B.game_year.value_counts().sort_index().to_dict(),
      union.game_year.value_counts().to_dict())
check("B", "19 cross-source duplicates dropped", int(rec.dropped_as_duplicate.sum()) == 19 == H['dup_vs_phi'])
check("B", "spring rows excluded = 47", len(ph[(ph.pitcher == 680742) & (ph.game_type == 'S')]) == 47 == H['spring_rows_excluded'])
check("B", "anchor = max R game_date in phils_2026", str(ph[(ph.game_year == 2026) & (ph.game_type == 'R')].game_date.max())[:10] == H['anchor'] == "2026-09-23")
check("B", "'Bowlan' name filter == id lock (client frame)", set(ph[ph.player_name == 'Bowlan, Jonathan'].pitcher.unique()) == {680742})
check("B", "no duplicate keys in receipt pitch table", R("bowlan_pitches").duplicated(key).sum() == 0)
check("B", "parquet sha256 of subject file stable across reads",
      hashlib.sha256((ROOT / "data" / "opponents" / "bowlan.parquet").read_bytes()).hexdigest() ==
      hashlib.sha256((ROOT / "data" / "opponents" / "bowlan.parquet").read_bytes()).hexdigest())

# =============================================================================
# C · independent recompute (plain pandas)
# =============================================================================
w = pd.read_csv(ROOT / "wOBA and FIP Constants.csv").set_index("Season")
U = union.copy()
EV = {'walk': 'wBB', 'hit_by_pitch': 'wHBP', 'single': 'w1B', 'double': 'w2B', 'triple': 'w3B', 'home_run': 'wHR'}
rec_g = R("recap_governed").set_index("game_year")
for yr in (2025, 2026):
    d = U[U.game_year == yr]
    pa = d[d.events.notna() & (d.events != 'pickoff_1b')]
    ab = pa[~pa.events.isin(['walk', 'intent_walk', 'hit_by_pitch', 'sac_fly', 'sac_bunt'])]
    k = pa.events.isin(['strikeout', 'strikeout_double_play']).sum(); bb = (pa.events == 'walk').sum()
    hits = pa.events.isin(['single', 'double', 'triple', 'home_run']).sum()
    wsum = sum(w.loc[yr, c] * (pa.events == e).sum() for e, c in EV.items())
    per_pa = d.groupby(['game_pk', 'at_bat_number']).agg(a=('bat_score', 'min'), b=('post_bat_score', 'max'))
    ff = d[d.pitch_type == 'FF']
    r = rec_g.loc[yr]
    check("C", f"{yr} PA", len(pa) == r.plate_apps, (len(pa), r.plate_apps))
    check("C", f"{yr} K rate (nresults publishes 3 dp)", close(k / len(pa), r.krate, 5e-4), (k / len(pa), r.krate))
    check("C", f"{yr} BB rate (nresults publishes 3 dp)", close(bb / len(pa), r.bbrate, 5e-4), (bb / len(pa), r.bbrate))
    check("C", f"{yr} BA", close(round(hits / len(ab), 3), r.ba, 1e-9), (hits / len(ab), r.ba))
    check("C", f"{yr} wOBA", close(round(wsum / len(pa), 3), r.woba, 1e-9), (wsum / len(pa), r.woba))
    check("C", f"{yr} games", d.game_pk.nunique() == r.games)
    check("C", f"{yr} runs created", int((per_pa.b - per_pa.a).sum()) == r.runs_created)
    check("C", f"{yr} FF velo", close(ff.release_speed.mean(), r.ff_velo, 1e-6))
    check("C", f"{yr} FF spin", close(ff.release_spin_rate.mean(), r.ff_spin, 1e-6))
    check("C", f"{yr} FF ride (unrounded)", close(12 * ff.pfx_z.mean(), r.ff_vert, 1e-6))
    sw = ff[(ff.zone < 10) & ff.description.isin(K.SWINGS)]
    check("C", f"{yr} in-zone FF whiff", close(sw.description.isin(K.WHIFFS).mean(), r.whiff_rate_iz_ff, 1e-9))
    fp = d[d.pitch_number == 1]
    check("C", f"{yr} first-pitch strike", close((fp.type != 'B').mean(), H[f'fps_{yr}'], 5e-4))
d25, d26 = U[U.game_year == 2025], U[U.game_year == 2026]
check("C", "velo delta +1.51", close(d26[d26.pitch_type == 'FF'].release_speed.mean() - d25[d25.pitch_type == 'FF'].release_speed.mean(), H['ff_velo_delta'], 5e-4))
# KP-1 K-rate percentile via plain groupby
pp = ph[(ph.phillies_role == 'pitching') & (ph.game_type == 'R')]
pa_all = pp[pp.events.notna() & (pp.events != 'pickoff_1b')]
g = pa_all.groupby(['pitcher', 'game_year']).agg(pa=('events', 'size'), k=('events', lambda s: s.isin(['strikeout', 'strikeout_double_play']).sum()))
g = g[g.pa >= 100]; g['kr'] = g.k / g.pa
bk = g.loc[(680742, 2026), 'kr']
check("C", "KP-1 population n = 198", len(g) == 198 == H['kp']['krate']['n'], len(g))
check("C", "KP-1 K percentile 92 / rank 15", int(np.floor(100 * (g.kr < bk).mean())) == 92 == H['kp']['krate']['pct'] and int((g.kr > bk).sum() + 1) == 15)
st = g.xs(2026, level='game_year').sort_values('kr', ascending=False)
check("C", "staff K rank 2 behind Duran (661395)", st.index[0] == 661395 and list(st.index).index(680742) == 1)
# staff ride rank
ffx = pp[(pp.p_throws == 'R') & (pp.pitch_type == 'FF') & (pp.game_year != 2017)]
gs = ffx.groupby(['pitcher', 'game_year']).agg(n=('pfx_z', 'size'), ivb=('pfx_z', 'mean'))
gs = gs[gs.n >= 100]
check("C", "staff ride rank #7 of 132", len(gs) == 132 and int((gs.ivb > gs.loc[(680742, 2026), 'ivb']).sum() + 1) == 7 == H['staff_ff_ivb_rank'])
iv = pp[(pp.p_throws == 'R') & (pp.pitch_type == 'FF')].groupby('game_year').pfx_z.mean() * 12
oth = iv.drop(2017)
check("C", "2017 ride level shift z > 5", (iv[2017] - oth.mean()) / oth.std() > 5, round((iv[2017] - oth.mean()) / oth.std(), 2))
# VE-1 first ten pitches
def bucket_velo(d):
    d = d.sort_values(['game_pk', 'at_bat_number', 'pitch_number']).copy()
    d['i'] = d.groupby('game_pk').cumcount() + 1
    return d[(d.i <= 10) & (d.pitch_type == 'FF')].release_speed.mean()
check("C", "VE-1 pitches 1–10: 95.2 → 96.7", close(bucket_velo(d25), H['velo_bucket']['2025_1-10']['velo'], 5e-4) and close(bucket_velo(d26), H['velo_bucket']['2026_1-10']['velo'], 5e-4))
# usage
def first_pitch(d):
    return d.sort_values(['game_pk', 'at_bat_number', 'pitch_number']).groupby('game_pk').head(1)
f26 = first_pitch(d26)
spans = d26.groupby('game_pk').inning.agg(lambda s: s.max() > s.min())
check("C", "multi-inning share 2026", close(spans.mean(), H['usage']['2026']['multi_inning_share'], 5e-4))
check("C", "7th/8th entries = 41", int(f26.inning.isin([7, 8]).sum()) == 41 == H['apps_7th_8th_2026'])
dirty = f26[f26[['on_1b', 'on_2b', 'on_3b']].notna().any(axis=1)].game_pk
per = d26.groupby(['game_pk', 'at_bat_number']).agg(a=('bat_score', 'min'), b=('post_bat_score', 'max')).reset_index()
per['r'] = per.b - per.a
check("C", "dirty entries 15 → 13 runs", len(dirty) == 15 and int(per[per.game_pk.isin(dirty)].r.sum()) == 13)
cs26 = np.select([d26.strikes == 2], ['2K'], 'x')
check("C", "FF share at 2 strikes 2026", close(((cs26 == '2K') & (d26.pitch_type == 'FF')).sum() / (cs26 == '2K').sum(), H['tests']['Four-seam share, 2K counts']['r26'], 5e-4))

# =============================================================================
# D · surface consistency
# =============================================================================
dash = (HERE / "dp_uc48_bowlan_2026_dashboard.html").read_text(encoding="utf-8")
art = (HERE / "dp_uc48_bowlan_2026_dashboard.artifact.html").read_text(encoding="utf-8")
m = re.search(r"const D = (\{.*?\});\nconst \$", dash, re.S)
P = json.loads(m.group(1).replace("<\\/", "</"))
_a, _b = pd.DataFrame(P['recap']), R("recap_governed")
_num = _b.select_dtypes('number').columns
check("D", "payload recap == receipt", list(_a.columns) == list(_b.columns) and np.allclose(_a[_num].astype(float), _b[_num].astype(float), equal_nan=True))
check("D", "payload ledger == receipt", pd.DataFrame(P['ledger']).equals(R("persona_ledger")))
check("D", "payload hp == receipt", pd.DataFrame(P['hp']).equals(R("hp_reconciliation")))
check("D", "payload headlines == headlines.json", P['H'] == H)
import base64
def arr(x):
    if isinstance(x, dict) and "bdata" in x:
        return np.frombuffer(base64.b64decode(x["bdata"]), dtype=np.dtype(x["dtype"])).tolist()
    return list(x or [])
f7 = json.loads((OUT / "dp_uc48_fig7_platoon_mix.json").read_text())
st_ = R("arsenal_by_stand")
v = st_[(st_.stand == 'R') & (st_.game_year == 2026) & (st_.pitch_type == 'ST')].usage.iat[0]
check("D", "fig7 sweeper bar == receipt", any(abs(float(x) - v) < 1e-9 for t in f7["data"] for x in arr(t.get("x")) if x == x))
check("D", "every report figure exists as PNG and JSON", all((OUT / f"dp_uc48_{k}.png").exists() and (OUT / f"dp_uc48_{k}.json").exists()
      for k in re.findall(r"out/dp_uc48_(fig\d+_[a-z_]+)\.png", (HERE / "dp_uc48_bowlan_2026_recap_report.md").read_text())))
strip = lambda h: re.sub(r"<script>.{100000,}?</script>", "<script></script>", h, count=1, flags=re.S)   # drop the inlined plotly.js  # noqa: E731
check("D", "repo dashboard is offline (no external src/href outside plotly.js)", not re.search(r'<(?:script|link)[^>]+(?:src|href)="https?://', strip(dash)))
check("D", "artifact variant has no <html>/<body> skeleton and has a <title>", "<html" not in art[:20000] and "<body" not in art[:20000] and art.startswith("<title>"))
check("D", "artifact variant only loads Google Fonts externally", set(re.findall(r'<(?:script|link)[^>]+(?:src|href)="(https?://[^/"]+)', strip(art))) <= {"https://fonts.googleapis.com", "https://fonts.gstatic.com"})
check("D", "dashboard < 16 MB", len(dash.encode()) < 16e6, len(dash.encode()))
check("D", "drill density has all arsenal pitch types", set(P['dens']) == set(H['density_pitch_types']))

# =============================================================================
# E · governance
# =============================================================================
dq = R("dq_scorecard")
check("E", "DQ 0 FAIL", (dq.result == 'FAIL').sum() == 0, dq.result.value_counts().to_dict())
bc = R("brand_compliance")
check("E", "brand compliance: no fails", (bc.status == 'fail').sum() == 0, bc.status.value_counts().to_dict())
check("E", "parent kernel hash pinned", K.parent_kernel_hash() == K.PARENT_KERNEL_SHA256)
check("E", "entity lock is an id, not a name", K.SUBJECT_ID == 680742 and "player_name ==" not in Path(K.__file__).read_text().split("def kellen_frame")[0])
need = ["00_dpo_orchestration_record.md", "01_strategy_intake.md", "02_engineering_design.md", "03_governance.md", "04_engineering_build.md",
        "05_quality_certification.md", "06_consumer_success.md", "07_platform_marketing.md", "README.md", "BID_2026-09-24_uc-pps-033-bowlan-2026-recap.md"]
missing = [n for n in need if not (PKG / n).exists()]
check("E", "control-plane package manifest (10 docs)", not missing, missing)
check("E", "carry-ins appear only as carry-ins in the report", all(s in (HERE / "dp_uc48_bowlan_2026_recap_report.md").read_text() for s in ("carry-in", "never computed on")))

# =============================================================================
# F · narrative-to-receipt
# =============================================================================
rep = (HERE / "dp_uc48_bowlan_2026_recap_report.md").read_text()
rg = R("recap_governed").set_index("game_year"); ars = R("arsenal_by_season").set_index(["game_year", "pitch_type"])
tt = R("rate_tests").set_index("metric"); us = R("usage_summary").set_index("game_year"); arch = R("archetype_inherited").set_index("game_year")
kp = R("house_percentiles").set_index("column"); mo = R("monthly_2026").set_index("month"); sbs = R("arsenal_by_stand").set_index(["game_year", "stand", "pitch_type"])
fmt3 = lambda x: f"{x:.3f}".lstrip("0")        # noqa: E731
pc1 = lambda x: f"{100 * x:.1f}%"               # noqa: E731
pc0 = lambda x: f"{100 * x:.0f}%"               # noqa: E731
claims = [
    # bottom line / buy
    ("2025 wOBA", fmt3(rg.loc[2025, 'woba'])), ("2026 wOBA", fmt3(rg.loc[2026, 'woba'])),
    ("2025 K%", pc1(rg.loc[2025, 'krate'])), ("2026 K%", pc1(rg.loc[2026, 'krate'])),
    ("2025 BB%", pc1(rg.loc[2025, 'bbrate'])), ("2026 BB%", pc1(rg.loc[2026, 'bbrate'])),
    ("games 59", f"{int(rg.loc[2026, 'games'])} appearances"), ("games 34", f"| {int(rg.loc[2025, 'games'])} | {int(rg.loc[2026, 'games'])} |"),
    ("ride grade 2025", f"graded {int(arch.loc[2025, 'g_ivb_in'])} on ride and {int(arch.loc[2025, 'g_whiff_rate'])} on whiff"),
    ("velo grade", f"velocity grade of {int(arch.loc[2025, 'g_velo'])}"),
    ("rank 2025", f"#{int(arch.loc[2025, 'rank_in_405'])} of 405"), ("rank 2026", f"#{int(arch.loc[2026, 'rank_in_405'])} of 405"),
    ("shape 55→60", f"shape went {int(arch.loc[2025, 'shape_grade'])} → {int(arch.loc[2026, 'shape_grade'])}"),
    ("results 75", f"{int(arch.loc[2026, 'shape_grade'])} / {int(arch.loc[2026, 'results_grade'])}"),
    ("FF velo", f"{rg.loc[2025, 'ff_velo']:.1f} to {rg.loc[2026, 'ff_velo']:.1f} mph (+{H['ff_velo_delta']:.2f}"),
    ("spin +65", f"{H['ff_spin_delta']:.0f} more rpm"), ("spin values", f"{rg.loc[2025, 'ff_spin']:.0f} → {rg.loc[2026, 'ff_spin']:.0f} rpm"),
    ("ride", f"{rg.loc[2025, 'ff_vert']:.1f} → {rg.loc[2026, 'ff_vert']:.1f} in"),
    ("2023 ride", f"| {rg.loc[2023, 'ff_velo']:.1f} | {rg.loc[2023, 'ff_vert']:.1f} |"), ("2024 ride", f"| {rg.loc[2024, 'ff_velo']:.1f} | {rg.loc[2024, 'ff_vert']:.1f} |"),
    ("VE-1", f"{H['velo_bucket']['2025_1-10']['velo']:.1f} to {H['velo_bucket']['2026_1-10']['velo']:.1f} mph"),
    ("lefty FF+CH", f"{pc0(sbs.loc[(2025, 'L', 'FF'), 'usage'] + sbs.loc[(2025, 'L', 'CH'), 'usage'])} to {pc0(sbs.loc[(2026, 'L', 'FF'), 'usage'] + sbs.loc[(2026, 'L', 'CH'), 'usage'])}"),
    ("sweeper vs R", f"new sweeper ({pc0(sbs.loc[(2026, 'R', 'ST'), 'usage'])})"),
    ("2K share", f"{pc1(tt.loc['Four-seam share, 2K counts', 'rate_2025'])} | {pc1(tt.loc['Four-seam share, 2K counts', 'rate_2026'])}"),
    ("behind share", f"{pc1(tt.loc['Four-seam share, behind counts', 'rate_2025'])} | {pc1(tt.loc['Four-seam share, behind counts', 'rate_2026'])}"),
    ("K p", f"p = {tt.loc['K rate (K / PA)', 'p']:.2f} and {tt.loc['BB rate (BB / PA)', 'p']:.2f}"),
    ("chase", f"{pc1(tt.loc['Chase rate (swings / out-of-zone)', 'rate_2025'])} | {pc1(tt.loc['Chase rate (swings / out-of-zone)', 'rate_2026'])} | {tt.loc['Chase rate (swings / out-of-zone)', 'p']:.2f}"),
    ("FPS", f"{pc1(tt.loc['First-pitch strike rate', 'rate_2025'])} | {pc1(tt.loc['First-pitch strike rate', 'rate_2026'])} | {tt.loc['First-pitch strike rate', 'p']:.2f}"),
    ("FPS short", f"{pc0(tt.loc['First-pitch strike rate', 'rate_2025'])} → {pc0(tt.loc['First-pitch strike rate', 'rate_2026'])}"),
    ("K pct", f"{int(kp.loc['krate', 'house_percentile'])}nd house percentile"), ("K rank", f"15th of {int(kp.loc['krate', 'population_n'])}"),
    ("ppa", f"| {us.loc[2025, 'pitches_per_app']:.1f} | {us.loc[2026, 'pitches_per_app']:.1f} |"),
    ("multi", f"| {pc0(us.loc[2025, 'multi_inning_share'])} | {pc0(us.loc[2026, 'multi_inning_share'])} |"),
    ("start inn", f"| {pc0(us.loc[2025, 'start_of_inning_share'])} | {pc0(us.loc[2026, 'start_of_inning_share'])} |"),
    ("late", f"| {pc0(us.loc[2025, 'late_entry_share'])} | {pc0(us.loc[2026, 'late_entry_share'])} |"),
    ("b2b", f"| {int(us.loc[2025, 'back_to_backs'])} | {int(us.loc[2026, 'back_to_backs'])} |"),
    ("rest", f"| {int(us.loc[2025, 'median_rest'])} | {int(us.loc[2026, 'median_rest'])} |"),
    ("7th/8th", f"({H['apps_7th_8th_2026']} began in the 7th or 8th)"), ("scoreless", f"{H['scoreless_apps_2026']} of 59 outings were scoreless"),
    ("dirty", f"{H['rc_by_entry']['2026_dirty']['apps']} outings he began with men on base produced {H['rc_by_entry']['2026_dirty']['rc']} of his 30 runs"),
    ("rc/pa", f"({fmt3(rg.loc[2025, 'rc_per_pa'])} → {fmt3(rg.loc[2026, 'rc_per_pa'])})"),
    ("last5", f"averaged {H['last5_ff_velo']:.1f} mph"), ("season velo", f"against {H['season_ff_velo_2026']:.1f} for the season"),
    ("staff ride", f"#{H['staff_ff_ivb_rank']} of {H['staff_ff_seasons_n']}"),
    ("share above", f"Only {100 * H['share_other_above_median']:.1f}% of {H['other_rhp_ff_pitches']:,} other"),
    ("2017", f"average {H['ivb_2017']:.1f} in of ride against {H['ivb_other_years_range'][0]:.1f}–{H['ivb_other_years_range'][1]:.1f} in"),
    ("2017 z", f"z = {H['ivb_2017_z']:.1f}"),
    ("FF whiff", f"{fmt3(ars.loc[(2025, 'FF'), 'whiff_rate'])} → {fmt3(ars.loc[(2026, 'FF'), 'whiff_rate'])}"),
    ("FF xwobacon", f"{fmt3(ars.loc[(2025, 'FF'), 'xwobacon'])} → {fmt3(ars.loc[(2026, 'FF'), 'xwobacon'])}"),
    ("FF rv", f"+{ars.loc[(2025, 'FF'), 'rv100']:.1f} → +{ars.loc[(2026, 'FF'), 'rv100']:.1f}"),
    ("SI whiff", f"{fmt3(ars.loc[(2025, 'SI'), 'whiff_rate'])} → {fmt3(ars.loc[(2026, 'SI'), 'whiff_rate'])}"),
    ("SI xwobacon", f"{fmt3(ars.loc[(2025, 'SI'), 'xwobacon'])} → {fmt3(ars.loc[(2026, 'SI'), 'xwobacon'])}"),
    ("ST rv", f"{ars.loc[(2026, 'ST'), 'rv100']:.1f} RV/100 on {int(ars.loc[(2026, 'ST'), 'n'])} pitches".replace("-", "−")),
    ("CH whiff", f"{fmt3(ars.loc[(2025, 'CH'), 'whiff_rate'])} → {fmt3(ars.loc[(2026, 'CH'), 'whiff_rate'])}"),
    ("CH velo", f"{ars.loc[(2025, 'CH'), 'velo']:.1f} → {ars.loc[(2026, 'CH'), 'velo']:.1f}"),
    ("SI velo", f"{ars.loc[(2025, 'SI'), 'velo']:.1f} → {ars.loc[(2026, 'SI'), 'velo']:.1f}"),
    ("SL velo", f"{ars.loc[(2025, 'SL'), 'velo']:.1f} → {ars.loc[(2026, 'SL'), 'velo']:.1f}"),
    ("usage FF", f"four-seam {100 * ars.loc[(2026, 'FF'), 'usage']:.1f}%"),
    ("prior career", f"{rg.loc[2026, 'games'] / H['prior_career_games']:.1f}×"), ("prior games", f"({H['prior_career_games']} games)"),
    ("IZ FF", f"({fmt3(rg.loc[2025, 'whiff_rate_iz_ff'])} → {fmt3(rg.loc[2026, 'whiff_rate_iz_ff'])})"),
    ("HP tally", f"{int((R('hp_reconciliation').verdict.str.startswith('HELD')).sum())} held, {int((R('hp_reconciliation').verdict == 'PARTLY').sum())} partly held"),
    ("slg", f"SLG fell {round(1000 * (rg.loc[2025, 'slg'] - rg.loc[2026, 'slg']))} points, more than OBP ({round(1000 * (rg.loc[2025, 'obp'] - rg.loc[2026, 'obp']))} points)"),
    ("spring", f"{H['spring_rows_excluded']} spring-training rows"), ("dups", f"{H['dup_vs_phi']} duplicated pitches"),
]
for name, s in claims:
    check("F", f"report: {name}", s in rep, s)
# ledger strengths in the report
for r in R("persona_ledger").itertuples():
    check("F", f"report ledger {r.hyp_id} = {r.strength}", re.search(rf"\*\*{r.hyp_id}\*\*[^\n]*\| {re.escape(r.strength)} \|", rep) is not None)
# dashboard narrative numbers (formatted by the builder from headlines) must survive into the HTML
dash_claims = [f"#{H['arch']['2026']['rank']} of {H['arch_pop_n']}", f"{H['kp']['krate']['pct']}th percentile", f"{H['apps_7th_8th_2026']} of {H['y2026']['games']}",
               f"{H['velo_bucket']['2025_1-10']['velo']:.1f} to {H['velo_bucket']['2026_1-10']['velo']:.1f} mph", f"#{H['staff_ff_ivb_rank']} of {H['staff_ff_seasons_n']}"]
for s in dash_claims:
    check("F", f"dashboard: {s}", s in dash)

# =============================================================================
LG = pd.DataFrame(LOG)
LG.to_csv(OUT / "dp_uc48_verification_log.csv", index=False)
summ = LG.groupby("family").result.apply(lambda s: f"{(s == 'PASS').sum()}/{len(s)}")
print(summ.to_string()); print("TOTAL", f"{(LG.result == 'PASS').sum()}/{len(LG)}")
print(LG[LG.result == "FAIL"][["family", "check", "detail"]].to_string() if (LG.result == "FAIL").any() else "no failures")
