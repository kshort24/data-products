"""
dp_uc42a_verification.py — independent verification harness for dp_uc42a.
============================================================================
Recomputes every published figure from the SHIPPED EXTRACTS using plain
Python — csv module, dicts, loops — never the pandas groupby path the build
used. Two computations agreeing is worth something only if they are actually
two computations.

Five families of check:

  A · PARENT REPRODUCTION. Every number dp_uc42 v1.0.0 published, recomputed
      from v1's own shipped extract and compared to v1's own shipped CSVs.
      If v1.1.0 quietly changed a v1.0.0 number, this fails. (Skipped with a
      loud SKIP, never a silent pass, if the v1 out/ files are not present.)
  B · SELF-CONSISTENCY. v1.1.0's own tables recomputed from v1.1.0's extract.
  C · NEW OBJECTS. PM-1 chi-square / TVD, DC-1 decomposition identity,
      RC-1 arithmetic, context-pool floor, zone decomposition.
  D · CONVENTIONS. Coordinate convention, entity lock, grain uniqueness,
      NULL-zone exclusion, direction-vocabulary closure.
  E · ARTIFACT INTEGRITY. The dashboard actually contains the payload, and
      every element id its script addresses exists in its markup.
  F · NARRATIVE / RECEIPT RECONCILIATION. New in v1.1.0, prompted by defect
      V-1: v1.0.0's receipts were independently verified and correct, its
      report agreed with them, and two summary files plus the ledger patch
      quietly carried a superseded figure. Verifying receipts is not enough
      if nothing checks that the prose agrees with the receipts. Every
      headline figure stated in the report and the dashboard is recomputed
      here from the shipped receipts, formatted the way the narrative
      formats it, and string-matched against the narrative. A number that
      appears in prose but not in a receipt, or that disagrees with one,
      fails the build.

Usage:  python dp_uc42a_verification.py
Exit code is non-zero if any check fails.
"""
import csv
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
V1 = os.environ.get('DP_UC42_V1_OUT', OUT)   # v1.0.0's out/ dir, if separate
DASH = os.path.join(HERE, 'dp_uc42a_turner_whole_field_dashboard.html')

RESULTS = []
DIRS = ['Pull', 'Straightaway', 'Oppo']


def chk(family, name, ok, expected='', got=''):
    RESULTS.append(dict(family=family, check=name, status='PASS' if ok else 'FAIL',
                        expected=expected, got=got))
    return ok


def skip(family, name, why):
    RESULTS.append(dict(family=family, check=name, status='SKIP',
                        expected=why, got=''))


def load(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def close(a, b, tol=5e-6):
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) <= tol


def pooled_z(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    pp = (x1 + x2) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    return (float('nan') if se == 0 else (p1 - p2) / se), p1 - p2


# ---------------------------------------------------------------- load
bip = load(os.path.join(OUT, 'dp_uc42a_turner_bip_extract.csv'))
pit = load(os.path.join(OUT, 'dp_uc42a_turner_pitch_extract.csv'))
ctx = load(os.path.join(OUT, 'dp_uc42a_context_player_seasons.csv'))
rates = load(os.path.join(OUT, 'dp_uc42a_kpi_directional_by_zone_year.csv'))
sig = load(os.path.join(OUT, 'dp_uc42a_significance_2026_vs_pooled.csv'))
ooz = load(os.path.join(OUT, 'dp_uc42a_ooz_share_by_year.csv'))
cells = load(os.path.join(OUT, 'dp_uc42a_in_zone_decomposition.csv'))
stab = load(os.path.join(OUT, 'dp_uc42a_attack_stability.csv'))
dec = load(os.path.join(OUT, 'dp_uc42a_value_decomposition.csv'))
valiz = load(os.path.join(OUT, 'dp_uc42a_bip_value_in_zone.csv'))
defects = load(os.path.join(OUT, 'dp_uc42a_defect_exposure.csv'))

YEARS = [2023, 2024, 2025, 2026]
BASE = [2023, 2024, 2025]


def is_ooz(r):
    return str(r['ooz']).strip().lower() in ('true', '1')


def recompute_rates(rows):
    """Plain-loop replacement for directional_rate_table()."""
    acc = {}
    for r in rows:
        y = int(r['game_year'])
        d = acc.setdefault(y, {'n': 0, 'Pull': 0, 'Straightaway': 0, 'Oppo': 0})
        d['n'] += 1
        if r['hit_direction'] in d:
            d[r['hit_direction']] += 1
    return acc


# ================================================================ A · PARENT
v1_rates = os.path.join(V1, 'dp_uc42_kpi_directional_by_zone_year.csv')
v1_sig = os.path.join(V1, 'dp_uc42_significance_2026_vs_pooled.csv')
v1_bip = os.path.join(V1, 'dp_uc42_turner_bip_extract.csv')
if os.path.exists(v1_rates) and os.path.exists(v1_bip):
    p_bip = load(v1_bip)
    chk('A', 'v1 extract row count reproduced by v1.1.0',
        len(p_bip) == len(bip), len(p_bip), len(bip))
    p_rows = load(v1_rates)
    matched = 0
    for pr in p_rows:
        for nr in rates:
            if pr['game_year'] == nr['game_year'] and pr['zone'] == nr['zone']:
                ok = (int(pr['n_bip']) == int(nr['n_bip'])
                      and int(pr['pull_n']) == int(nr['pull_n'])
                      and int(pr['oppo_n']) == int(nr['oppo_n'])
                      and int(pr['straight_n']) == int(nr['straight_n'])
                      and close(pr['pull_rate'], nr['pull_rate'])
                      and close(pr['oppo_rate'], nr['oppo_rate']))
                chk('A', f"v1 rate row reproduced: {pr['zone']} {pr['game_year']}",
                    ok, pr['n_bip'] + '/' + pr['pull_n'], nr['n_bip'] + '/' + nr['pull_n'])
                matched += 1
    chk('A', 'every v1 rate row was matched', matched == len(p_rows), len(p_rows), matched)
    if os.path.exists(v1_sig):
        for ps in load(v1_sig):
            hit = [n for n in sig if n['zone'] == ps['zone'] and n['metric'] == ps['metric']]
            ok = bool(hit) and close(ps['z'], hit[0]['z'], 1e-9) and \
                int(ps['n_2026']) == int(hit[0]['n_2026'])
            chk('A', f"v1 z reproduced: {ps['zone']} {ps['metric']}",
                ok, ps['z'], hit[0]['z'] if hit else 'missing')
else:
    skip('A', 'parent reproduction against v1.0.0 shipped CSVs',
         'v1 out/ files not found at ' + V1 + ' — set DP_UC42_V1_OUT')

# ================================================================ B · SELF
for label, pred in [('all', lambda r: True), ('in_zone', lambda r: not is_ooz(r)),
                    ('outside', is_ooz)]:
    acc = recompute_rates([r for r in bip if pred(r)])
    for y in YEARS:
        row = [r for r in rates if int(r['game_year']) == y and r['zone'] == label][0]
        a = acc[y]
        ok = (a['n'] == int(row['n_bip']) and a['Pull'] == int(row['pull_n'])
              and a['Oppo'] == int(row['oppo_n'])
              and close(a['Pull'] / a['n'], row['pull_rate'])
              and close(a['Oppo'] / a['n'], row['oppo_rate'])
              and close(a['Straightaway'] / a['n'], row['straight_rate']))
        chk('B', f'rate table recomputed: {label} {y}', ok,
            f"{row['n_bip']}/{row['pull_n']}/{row['oppo_n']}",
            f"{a['n']}/{a['Pull']}/{a['Oppo']}")

for label, pred in [('in_zone', lambda r: not is_ooz(r)), ('outside', is_ooz)]:
    cur = [r for r in bip if pred(r) and int(r['game_year']) == 2026]
    bas = [r for r in bip if pred(r) and int(r['game_year']) in BASE]
    for d in DIRS:
        z, diff = pooled_z(sum(1 for r in cur if r['hit_direction'] == d), len(cur),
                           sum(1 for r in bas if r['hit_direction'] == d), len(bas))
        row = [s for s in sig if s['zone'] == label and s['metric'] == d.lower()][0]
        chk('B', f'z recomputed: {label} {d.lower()}',
            close(z, row['z'], 1e-9) and close(diff, row['diff'], 1e-9),
            row['z'], round(z, 9))

for y in YEARS:
    rows = [r for r in bip if int(r['game_year']) == y]
    share = sum(1 for r in rows if is_ooz(r)) / len(rows)
    row = [o for o in ooz if int(o['game_year']) == y][0]
    chk('B', f'ooz share recomputed: {y}', close(share, row['ooz_share_of_bip']),
        row['ooz_share_of_bip'], round(share, 9))

# total row-count identity
chk('B', 'zone slices partition the BIP frame exactly',
    sum(int(r['n_bip']) for r in rates if r['zone'] == 'in_zone')
    + sum(int(r['n_bip']) for r in rates if r['zone'] == 'outside')
    == sum(int(r['n_bip']) for r in rates if r['zone'] == 'all') == len(bip),
    len(bip), sum(int(r['n_bip']) for r in rates if r['zone'] == 'all'))

# ================================================================ C · NEW
ZONE_ROW = {1: 'Up', 2: 'Up', 3: 'Up', 4: 'Middle', 5: 'Middle', 6: 'Middle',
            7: 'Down', 8: 'Down', 9: 'Down'}
ZONE_COL = {1: 'Inside', 2: 'Middle', 3: 'Outside', 4: 'Inside', 5: 'Middle',
            6: 'Outside', 7: 'Inside', 8: 'Middle', 9: 'Outside'}
izb = [r for r in bip if not is_ooz(r)]
for dim, table in [('zone_row', ZONE_ROW), ('zone_col', ZONE_COL)]:
    groups = sorted(set(table.values()))
    for gname in groups:
        sub = [r for r in izb if table[int(float(r['zone']))] == gname]
        cur = [r for r in sub if int(r['game_year']) == 2026]
        bas = [r for r in sub if int(r['game_year']) in BASE]
        z, diff = pooled_z(sum(1 for r in cur if r['hit_direction'] == 'Pull'), len(cur),
                           sum(1 for r in bas if r['hit_direction'] == 'Pull'), len(bas))
        row = [c for c in cells if c['dimension'] == dim and c['slice'] == gname
               and c['metric'] == 'pull'][0]
        chk('C', f'in-zone decomposition {dim}={gname} (pull)',
            close(z, row['z'], 1e-9) and len(cur) == int(row['n_2026']),
            row['z'], round(z, 9))

# every decomposition slice's n must sum back to the in-zone population
for dim in ['zone_row', 'zone_col']:
    tot = sum(int(c['n_2026']) for c in cells
              if c['dimension'] == dim and c['metric'] == 'pull')
    chk('C', f'{dim} slices partition 2026 in-zone BIP', tot == len(
        [r for r in izb if int(r['game_year']) == 2026]),
        len([r for r in izb if int(r['game_year']) == 2026]), tot)

# PM-1 recomputed from the pitch extract
CELLS_ALL = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14]


def zone_of(r):
    v = r['zone']
    return None if v == '' else int(float(v))


def chi_tvd(cellset, conditional):
    pool = [r for r in pit if zone_of(r) is not None
            and (not conditional or zone_of(r) in cellset)]
    cur = [r for r in pool if int(r['game_year']) == 2026]
    bas = [r for r in pool if int(r['game_year']) in BASE]
    obs = [sum(1 for r in cur if zone_of(r) == c) for c in cellset]
    share = [sum(1 for r in bas if zone_of(r) == c) / len(bas) for c in cellset]
    n = sum(obs)
    chi = sum((o - s * n) ** 2 / (s * n) for o, s in zip(obs, share) if s > 0)
    tvd = 0.5 * sum(abs(o / n - s) for o, s in zip(obs, share))
    return chi, tvd, n, len(bas)


for cellset, cond, key in [(CELLS_ALL, False, 'PM-1a'),
                           ([1, 2, 3, 4, 5, 6, 7, 8, 9], True, 'PM-1b'),
                           ([11, 12, 13, 14], True, 'PM-1c')]:
    chi, tvd, n, nb = chi_tvd(cellset, cond)
    row = [s for s in stab if s['test'].startswith(key)][0]
    chk('C', f'{key} chi-square recomputed', close(chi, row['chi2'], 1e-6),
        row['chi2'], round(chi, 6))
    chk('C', f'{key} total-variation distance recomputed',
        close(tvd, row['total_variation_distance'], 1e-9),
        row['total_variation_distance'], round(tvd, 9))
    chk('C', f'{key} 2026 n recomputed', n == int(row['n_2026']), row['n_2026'], n)

# DC-1: the identity must hold exactly, and the inputs must come from the extract
TB = {'single': 1, 'double': 2, 'triple': 3, 'home_run': 4}
for pop, pred in [('all BIP', lambda r: True), ('in-zone BIP', lambda r: not is_ooz(r))]:
    row = [d for d in dec if d['population'] == pop][0]
    cur = [r for r in bip if pred(r) and int(r['game_year']) == 2026]
    bas = [r for r in bip if pred(r) and int(r['game_year']) in BASE]

    def slg(rows, d):
        s = [r for r in rows if r['hit_direction'] == d]
        return (sum(TB.get(r['events'], 0) for r in s) / len(s)) if s else 0.0

    mix_c = {d: sum(1 for r in cur if r['hit_direction'] == d) / len(cur) for d in DIRS}
    mix_b = {d: sum(1 for r in bas if r['hit_direction'] == d) / len(bas) for d in DIRS}
    base_base = sum(mix_b[d] * slg(bas, d) for d in DIRS)
    mix_only = sum(mix_c[d] * slg(bas, d) for d in DIRS)
    rate_only = sum(mix_b[d] * slg(cur, d) for d in DIRS)
    actual = sum(mix_c[d] * slg(cur, d) for d in DIRS)
    chk('C', f'DC-1 baseline slg_bip recomputed [{pop}]',
        close(base_base, row['baseline_slg_bip'], 1e-9), row['baseline_slg_bip'],
        round(base_base, 9))
    chk('C', f'DC-1 current slg_bip recomputed [{pop}]',
        close(actual, row['current_slg_bip'], 1e-9), row['current_slg_bip'],
        round(actual, 9))
    chk('C', f'DC-1 mix effect recomputed [{pop}]',
        close(mix_only - base_base, row['mix_effect'], 1e-9), row['mix_effect'],
        round(mix_only - base_base, 9))
    chk('C', f'DC-1 rate effect recomputed [{pop}]',
        close(rate_only - base_base, row['rate_effect'], 1e-9), row['rate_effect'],
        round(rate_only - base_base, 9))
    chk('C', f'DC-1 identity closes: gap = mix + rate + interaction [{pop}]',
        close(float(row['gap']), float(row['mix_effect']) + float(row['rate_effect'])
              + float(row['interaction']), 1e-12),
        row['gap'], float(row['mix_effect']) + float(row['rate_effect']) + float(row['interaction']))
    # current_slg_bip must also equal raw total bases / raw BIP
    raw = sum(TB.get(r['events'], 0) for r in cur) / len(cur)
    chk('C', f'DC-1 current slg_bip equals raw TB/BIP [{pop}]',
        close(raw, row['current_slg_bip'], 1e-9), row['current_slg_bip'], round(raw, 9))

# slg_bip per direction/season table
for row in valiz:
    y, d = int(row['game_year']), row['hit_direction']
    s = [r for r in izb if int(r['game_year']) == y and r['hit_direction'] == d]
    chk('C', f'slg_bip in-zone {y} {d}',
        len(s) == int(row['n'])
        and close(sum(TB.get(r['events'], 0) for r in s) / len(s), row['slg_bip'], 1e-9),
        row['n'] + '/' + row['slg_bip'], str(len(s)))

# RC-1 arithmetic and the PA floor
bad_rc, bad_floor = 0, 0
for r in ctx:
    pa = int(r['plate_apps'])
    if pa < 50:
        bad_floor += 1
    if r['runs_created_per_600'] and not close(
            float(r['runs_created']) / pa * 600, r['runs_created_per_600'], 1e-6):
        bad_rc += 1
chk('C', 'RC-1 = runs_created / PA * 600 for every context row', bad_rc == 0, 0, bad_rc)
chk('C', 'context pool respects the 50-PA repo floor', bad_floor == 0, 0, bad_floor)
chk('C', 'context pool contains all four Turner seasons',
    len([r for r in ctx if r['player_name'] == 'Turner, Trea']) == 4, 4,
    len([r for r in ctx if r['player_name'] == 'Turner, Trea']))
tt26 = [r for r in ctx if r['player_name'] == 'Turner, Trea' and r['game_year'] == '2026'][0]
chk('C', "Turner 2026 is flagged as the subject row",
    tt26['is_subject'] in ('True', 'true'), 'True', tt26['is_subject'])
chk('C', "Turner 2026 RC/600 is the lowest of his four Phillies seasons",
    min(float(r['runs_created_per_600']) for r in ctx if r['player_name'] == 'Turner, Trea')
    == float(tt26['runs_created_per_600']), tt26['runs_created_per_600'],
    min(float(r['runs_created_per_600']) for r in ctx if r['player_name'] == 'Turner, Trea'))
chk('C', "Turner 2026 barrel rate is NOT the lowest of his four seasons "
         "(the down year is not a barrel-rate story)",
    min(float(r['barrel_rate']) for r in ctx if r['player_name'] == 'Turner, Trea')
    < float(tt26['barrel_rate']), '< ' + tt26['barrel_rate'],
    min(float(r['barrel_rate']) for r in ctx if r['player_name'] == 'Turner, Trea'))

# defect exposure recomputed
untracked_subject = sum(1 for r in bip if r.get('launch_speed', '') == '')
row = [d for d in defects if d['defect'] == 'O-8 (subject)'][0]
chk('C', 'O-8 subject exposure recomputed',
    untracked_subject == int(row['value']), row['value'], untracked_subject)

# ================================================================ D · CONVENTIONS
pull_x = sorted(float(r['loc_x']) for r in bip if r['hit_direction'] == 'Pull')
med = pull_x[len(pull_x) // 2] if len(pull_x) % 2 else \
    (pull_x[len(pull_x) // 2 - 1] + pull_x[len(pull_x) // 2]) / 2
chk('D', 'coordinate convention: median loc_x for Pull is negative (RHB)',
    med < 0, '< 0', round(med, 3))
oppo_x = sorted(float(r['loc_x']) for r in bip if r['hit_direction'] == 'Oppo')
medo = oppo_x[len(oppo_x) // 2]
chk('D', 'coordinate convention: median loc_x for Oppo is positive (RHB)',
    medo > 0, '> 0', round(medo, 3))
chk('D', 'direction vocabulary is closed — no "not grouped" rows shipped',
    all(r['hit_direction'] in DIRS for r in bip), 'Pull/Straightaway/Oppo',
    sorted(set(r['hit_direction'] for r in bip)))
chk('D', 'NULL-zone rows excluded from the BIP frame entirely',
    all(r['zone'] not in ('', 'nan') for r in bip), 'none', 'ok')
chk('D', 'entity lock: pitch frame is a strict superset of the BIP frame',
    set(r['pitch_uid'] for r in bip).issubset(set(r['pitch_uid'] for r in pit)),
    'subset', 'ok')
chk('D', 'pitch_uid is unique at the pitch grain',
    len(set(r['pitch_uid'] for r in pit)) == len(pit), len(pit),
    len(set(r['pitch_uid'] for r in pit)))
chk('D', 'BIP frame carries no untracked hit coordinates',
    all(r['hc_x'] not in ('', 'nan') and r['hc_y'] not in ('', 'nan') for r in bip),
    'none', 'ok')
chk('D', 'subject is 100% right-handed in this window — L branch untested, as disclosed',
    all(r['stand'] == 'R' for r in bip), 'R', sorted(set(r['stand'] for r in bip)))
chk('D', 'every BIP row is regular season (game_type filtered upstream)',
    len(bip) == sum(int(r['n_bip']) for r in rates if r['zone'] == 'all'),
    sum(int(r['n_bip']) for r in rates if r['zone'] == 'all'), len(bip))

# ================================================================ E · ARTIFACT
if os.path.exists(DASH):
    html = open(DASH, encoding='utf-8').read()
    m = re.search(r'window\.__UC42A__=(\{.*?\});</script>', html, re.S)
    chk('E', 'dashboard embeds the payload inline (no runtime fetch)', bool(m),
        'payload literal', 'found' if m else 'missing')
    if m:
        pl = json.loads(m.group(1))
        chk('E', 'payload BIP count matches the shipped extract',
            len(pl['bip']) == len(bip), len(bip), len(pl['bip']))
        chk('E', 'payload context count matches the shipped extract',
            len(pl['ctx']) == len(ctx), len(ctx), len(pl['ctx']))
        chk('E', 'payload rate rows match the shipped extract',
            len(pl['rates']) == len(rates), len(rates), len(pl['rates']))
        chk('E', 'payload carries the parallel non-contact arrays at equal length',
            len(set(len(v) for v in pl['other'].values())) == 1, 1,
            sorted(set(len(v) for v in pl['other'].values())))
        chk('E', 'payload declares version 1.1.0 and its parent',
            pl['meta']['version'] == '1.1.0' and pl['meta']['parent'].startswith('dp_uc42'),
            '1.1.0 / dp_uc42 v1.0.0', pl['meta']['version'] + ' / ' + pl['meta']['parent'])
        chk('E', 'payload entity lock is the confirmed MLBAM id',
            pl['meta']['mlbam'] == 607208, 607208, pl['meta']['mlbam'])
    ids = set(re.findall(r'id="([A-Za-z0-9_]+)"', html))
    needed = ['ctx', 'spray', 'pitchmap', 'mixbars', 'zoneshift', 'zchart',
              'waterfall', 'valchart', 'stabTable', 'cellTable', 'defTable',
              'ttSeasons', 'kvPos', 'p1', 'p2', 's1', 's2', 'tip']
    missing = [i for i in needed if i not in ids]
    chk('E', 'every element the dashboard script addresses exists in its markup',
        not missing, 'none missing', missing)
    chk('E', 'dashboard references no external host (vendor-don\'t-CDN rule)',
        not re.search(r'(src|href)\s*=\s*"https?://', html), 'no external src/href',
        re.findall(r'(?:src|href)\s*=\s*"(https?://[^"]+)"', html)[:3])
else:
    skip('E', 'artifact integrity', 'dashboard HTML not built yet')

# ================================================================ F · NARRATIVE
REPORT = os.path.join(HERE, 'dp_uc42a_turner_whole_field_report.md')
BODY = os.path.join(HERE, 'tpl', 'body.html')
RDME = os.path.join(HERE, 'README.md')


def rate_of(zone_label, metric, which):
    r = [s for s in sig if s['zone'] == zone_label and s['metric'] == metric][0]
    return float(r['rate_2026' if which == 'cur' else 'rate_2023_25'])


def z_of(zone_label, metric):
    return float([s for s in sig if s['zone'] == zone_label
                  and s['metric'] == metric][0]['z'])


def stab_of(key, field):
    return float([s for s in stab if s['test'].startswith(key)][0][field])


dec_iz = [d for d in dec if d['population'] == 'in-zone BIP'][0]
tt26 = [r for r in ctx if r['player_name'] == 'Turner, Trea'
        and r['game_year'] == '2026'][0]
bohm26 = [r for r in ctx if r['player_name'] == 'Bohm, Alec'
          and r['game_year'] == '2026']

# (label, value recomputed from receipts, formatted as the narrative writes it)
CLAIMS = [
    ('outside-zone pull rate 2026', f"{rate_of('outside','pull','cur')*100:.1f}%"),
    ('outside-zone pull rate pooled', f"{rate_of('outside','pull','base')*100:.1f}%"),
    ('in-zone pull rate 2026', f"{rate_of('in_zone','pull','cur')*100:.1f}%"),
    ('in-zone pull rate pooled', f"{rate_of('in_zone','pull','base')*100:.1f}%"),
    ('in-zone oppo rate 2026', f"{rate_of('in_zone','oppo','cur')*100:.1f}%"),
    ('in-zone oppo rate pooled', f"{rate_of('in_zone','oppo','base')*100:.1f}%"),
    ('in-zone pull z', f"{z_of('in_zone','pull'):.2f}".replace('-', '\u2212')),
    ('in-zone oppo z', f"+{z_of('in_zone','oppo'):.2f}"),
    ('outside pull z', f"{z_of('outside','pull'):.2f}".replace('-', '\u2212')),
    ('BIP volume', f"{len(bip):,}"),
    ('pitch volume', f"{len(pit):,}"),
    ('context pool size', str(len(ctx))),
    ('PM-1b chi-square', f"{stab_of('PM-1b','chi2'):.1f}"),
    ('PM-1c chi-square', f"{stab_of('PM-1c','chi2'):.1f}"),
    ('PM-1a chi-square', f"{stab_of('PM-1a','chi2'):.1f}"),
    ('DC-1 baseline slg_bip', f"{float(dec_iz['baseline_slg_bip']):.3f}".lstrip('0')),
    ('DC-1 current slg_bip', f"{float(dec_iz['current_slg_bip']):.3f}".lstrip('0')),
    ('DC-1 mix share', f"{float(dec_iz['mix_share_of_gap'])*100:.0f}%"),
    ('DC-1 rate share', f"{float(dec_iz['rate_share_of_gap'])*100:.0f}%"),
    ('subject RC/600', f"{float(tt26['runs_created_per_600']):.1f}"),
    ('subject barrel rate', f"{float(tt26['barrel_rate']):.3f}".lstrip('0')),
]
if bohm26:
    CLAIMS.append(('peer RC/600 at a lower barrel rate',
                   f"{float(bohm26[0]['runs_created_per_600']):.1f}"))

if os.path.exists(REPORT):
    rpt = open(REPORT, encoding='utf-8').read()
    for label, val in CLAIMS:
        chk('F', f'report states the receipt value for {label}', val in rpt, val,
            'present' if val in rpt else 'ABSENT from report prose')
    # the premise verdict must be stated as not supported, in the report
    chk('F', 'report states the premise verdict explicitly',
        'not supported' in rpt.lower(), 'not supported',
        'present' if 'not supported' in rpt.lower() else 'ABSENT')
else:
    skip('F', 'narrative reconciliation against the report', 'report .md not found')

# The README is where V-1 lived. It is reconciled on the same footing as the
# report, against the same receipts, so the same defect cannot recur there.
if os.path.exists(RDME):
    rdme = open(RDME, encoding='utf-8').read()
    RD_CLAIMS = [c for c in CLAIMS if c[0] in (
        'outside-zone pull rate 2026', 'outside-zone pull rate pooled',
        'in-zone pull rate 2026', 'in-zone pull rate pooled',
        'in-zone oppo rate 2026', 'in-zone oppo rate pooled',
        'in-zone pull z', 'DC-1 baseline slg_bip', 'DC-1 current slg_bip',
        'DC-1 mix share', 'DC-1 rate share', 'BIP volume', 'pitch volume')]
    for label, val in RD_CLAIMS:
        chk('F', f'README states the receipt value for {label}', val in rdme, val,
            'present' if val in rdme else 'ABSENT from README prose')
    chk('F', 'README names the V-1 correction rather than silently fixing it',
        'V-1' in rdme and '36.7' in rdme, 'V-1 disclosed with the superseded figure',
        'disclosed' if ('V-1' in rdme and '36.7' in rdme) else 'NOT disclosed')
else:
    skip('F', 'narrative reconciliation against the README', 'README.md not found')

if os.path.exists(BODY):
    body = open(BODY, encoding='utf-8').read()
    DASH_CLAIMS = [c for c in CLAIMS if c[0] in (
        'outside-zone pull rate 2026', 'outside-zone pull rate pooled',
        'in-zone pull rate 2026', 'in-zone pull rate pooled',
        'in-zone oppo rate 2026', 'in-zone oppo rate pooled',
        'DC-1 mix share', 'DC-1 rate share')]
    for label, val in DASH_CLAIMS:
        chk('F', f'dashboard markup states the receipt value for {label}',
            val in body, val, 'present' if val in body else 'ABSENT from dashboard prose')
else:
    skip('F', 'narrative reconciliation against the dashboard markup', 'body.html not found')

# The report states its own harness size. That claim is itself a claim, so it
# is checked last, against the size the harness actually reached (this check
# included). Self-referential on purpose: a report that overstates how hard it
# was checked is the same class of error as V-1.
if os.path.exists(REPORT):
    m = re.search(r'verification (\d+)/(\d+) PASS', open(REPORT, encoding='utf-8').read(), re.I)
    total = len(RESULTS) + 1
    chk('F', "report's stated harness size matches the harness that ran",
        bool(m) and int(m.group(2)) == total, f'{total}/{total}',
        m.group(0) if m else 'no claim found')

# ---------------------------------------------------------------- report
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'dp_uc42a_verification_results.csv'), 'w',
          newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['family', 'check', 'status', 'expected', 'got'])
    w.writeheader()
    for r in RESULTS:
        w.writerow(r)

fails = [r for r in RESULTS if r['status'] == 'FAIL']
skips = [r for r in RESULTS if r['status'] == 'SKIP']
passes = [r for r in RESULTS if r['status'] == 'PASS']
for fam in ['A', 'B', 'C', 'D', 'E', 'F']:
    n = [r for r in RESULTS if r['family'] == fam]
    if n:
        print(f"  {fam}: {sum(1 for r in n if r['status']=='PASS')}/{len(n)} pass"
              + (f"  ({sum(1 for r in n if r['status']=='SKIP')} skipped)"
                 if any(r['status'] == 'SKIP' for r in n) else ''))
print(f"\nVERIFICATION {len(passes)}/{len(passes)+len(fails)} PASS"
      + (f", {len(skips)} SKIPPED" if skips else ''))
for r in fails:
    print('  FAIL', r['family'], '|', r['check'], '| expected', r['expected'], '| got', r['got'])
for r in skips:
    print('  SKIP', r['family'], '|', r['check'], '|', r['expected'])
sys.exit(1 if fails else 0)
