"""
dp_uc42_verification.py — independent spot-verification harness for
uc-pos-016-turner-whole-field-directional-001.

Scope note (disclosed in 05_quality_certification.md): this is a
SPOT-verification harness (18 checks against every published number in the
report), not the ~200-700 check exhaustive harness a full certification-tier
hitter-season UC gets (c.f. dp_uc40_verification.py, 711 checks). Appropriate
for a single-question diagnostic build; not appropriate to cite as
certification-tier rigor.

Independence discipline: recomputes every published number from the raw BIP
extract using plain-Python loops (no pandas groupby/vectorized ops), so a bug
shared between the build script and this harness would have to be duplicated
by hand, not inherited by construction.
"""
import csv
import math
import pickle
import sys

with open('turner_bip.pkl', 'rb') as f:
    import pandas as pd
    bip = pd.read_pickle(f)

records = bip[['game_year', 'ooz', 'hit_direction']].to_dict('records')

results = []


def check(name, actual, expected, tol=1e-6):
    ok = (expected is not None) and abs(actual - expected) <= tol
    results.append((name, actual, expected, ok))
    return ok


# ---- rebuild counts with plain loops (independent of the build's pandas groupby) ----
counts = {}  # (year, zone_bucket) -> {'Pull':n,'Oppo':n,'Straightaway':n,'total':n}
for r in records:
    yr = r['game_year']
    zb = 'outside' if r['ooz'] else 'in_zone'
    key = (yr, zb)
    d = counts.setdefault(key, {'Pull': 0, 'Oppo': 0, 'Straightaway': 0, 'total': 0})
    d['total'] += 1
    hd = r['hit_direction']
    if hd in d:
        d[hd] += 1

published = {
    (2023, 'outside'): dict(n=99, pull=41, oppo=40),
    (2024, 'outside'): dict(n=70, pull=29, oppo=25),
    (2025, 'outside'): dict(n=71, pull=34, oppo=18),
    (2026, 'outside'): dict(n=71, pull=28, oppo=25),
    (2023, 'in_zone'): dict(n=391, pull=185, oppo=117),
    (2024, 'in_zone'): dict(n=338, pull=177, oppo=86),
    (2025, 'in_zone'): dict(n=413, pull=181, oppo=134),
    (2026, 'in_zone'): dict(n=379, pull=152, oppo=133),
}

for key, exp in published.items():
    got = counts.get(key, {'Pull': 0, 'Oppo': 0, 'total': 0})
    check(f'{key} n_bip', got['total'], exp['n'], tol=0)
    check(f'{key} pull_n', got['Pull'], exp['pull'], tol=0)
    check(f'{key} oppo_n', got['Oppo'], exp['oppo'], tol=0)


def pooled_z(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    pp = (x1 + x2) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    return (p1 - p2) / se if se else float('nan')


# outside-zone: 2026 vs pooled 2023-25
o26 = counts[(2026, 'outside')]
o_base = {'Pull': 0, 'Oppo': 0, 'total': 0}
for yr in (2023, 2024, 2025):
    c = counts[(yr, 'outside')]
    o_base['Pull'] += c['Pull']; o_base['Oppo'] += c['Oppo']; o_base['total'] += c['total']

z_pull_ooz = pooled_z(o26['Pull'], o26['total'], o_base['Pull'], o_base['total'])
z_oppo_ooz = pooled_z(o26['Oppo'], o26['total'], o_base['Oppo'], o_base['total'])
check('z_pull_outside_2026_vs_pooled', z_pull_ooz, -0.58, tol=0.02)
check('z_oppo_outside_2026_vs_pooled', z_oppo_ooz, 0.10, tol=0.02)

# in-zone: 2026 vs pooled 2023-25
i26 = counts[(2026, 'in_zone')]
i_base = {'Pull': 0, 'Oppo': 0, 'total': 0}
for yr in (2023, 2024, 2025):
    c = counts[(yr, 'in_zone')]
    i_base['Pull'] += c['Pull']; i_base['Oppo'] += c['Oppo']; i_base['total'] += c['total']

z_pull_iz = pooled_z(i26['Pull'], i26['total'], i_base['Pull'], i_base['total'])
z_oppo_iz = pooled_z(i26['Oppo'], i26['total'], i_base['Oppo'], i_base['total'])
check('z_pull_inzone_2026_vs_pooled', z_pull_iz, -2.52, tol=0.02)
check('z_oppo_inzone_2026_vs_pooled', z_oppo_iz, 2.04, tol=0.02)

# outside-zone BIP share by year (independent recompute)
share_published = {2023: 0.202041, 2024: 0.171569, 2025: 0.146694, 2026: 0.157778}
for yr, exp in share_published.items():
    tot = sum(v['total'] for k, v in counts.items() if k[0] == yr)
    ooz = counts.get((yr, 'outside'), {'total': 0})['total']
    check(f'{yr} ooz_share', ooz / tot, exp, tol=0.001)

# coordinate-convention assertion (re-run independently)
pull_x = bip.loc[bip.hit_direction == 'Pull', 'loc_x']
check('median_loc_x_pull_negative', 1.0 if pull_x.median() < 0 else 0.0, 1.0, tol=0)

# ---- write results ----
with open('out/dp_uc42_verification_results.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['check', 'actual', 'expected', 'pass'])
    for name, actual, expected, ok in results:
        w.writerow([name, actual, expected, ok])

n_pass = sum(1 for *_, ok in results if ok)
print(f'{n_pass}/{len(results)} PASS')
if n_pass != len(results):
    for name, actual, expected, ok in results:
        if not ok:
            print('FAIL', name, actual, expected)
    sys.exit(1)
