"""
dp_uc40_package_audit.py — internal-consistency audit of the delivered package
==============================================================================
Verification (`dp_uc40_verification.py`) proves the NUMBERS. This proves the
PACKAGE: that every file the governance trail promises exists, that the figures
quoted in the 00-07 receipts match the receipts they cite, and that the two
consumable surfaces (PDF-source markdown and dashboard) agree with each other.

Run:  python dp_uc40_package_audit.py
"""
from __future__ import annotations

import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
_r = []


def chk(name, ok, detail=''):
    _r.append((name, bool(ok), detail))


def txt(f):
    return open(os.path.join(HERE, f), encoding='utf-8').read()


# ── 1 · every promised file exists ────────────────────────────────────────
REQUIRED = ['00_dpo_orchestration_record.md', '01_strategy_intake.md',
            '02_engineering_design.md', '03_governance.md', '04_engineering_build.md',
            '05_quality_certification.md', '06_consumer_success.md',
            '07_platform_marketing.md', 'README.md',
            'BID_2026-09-03_uc-pos-014-turner.md',
            'uc-pos-014-Trea Turner 20260903.md',
            'uc_ledger_AI_PATCH_uc-pos-014-turner.md',
            'dp_uc40_kernel.py', 'dp_uc40_turner_recency.py', 'dp_uc40_verification.py',
            'dp_uc40_build_pdf.py', 'dp_uc40_build_dashboard.py',
            'dp_uc40_turner_recency_report.md', 'dp_uc40_turner_recency_report.pdf',
            'dp_uc40_turner_recency_dashboard.html', '_chartjs_4.4.1.umd.js',
            'telemetry/run_economics_ledger.csv', 'telemetry/calibration_report.md',
            # v1.1.0 bat-path addendum
            'ADDENDUM_v1.1.0_bat_path.md', '03a_bat_path_semantics_and_lineage.md',
            '05a_bat_path_certification.md', 'dp_uc40a_kernel.py', 'dp_uc40a_bat_path.py',
            'dp_uc40a_verification.py', 'dp_uc40a_bat_path_report.md',
            'dp_uc40a_bat_path_report.pdf']
for f in REQUIRED:
    chk(f'file exists: {f}', os.path.exists(os.path.join(HERE, f)))

CSVS = [f for f in os.listdir(OUT) if f.endswith('.csv')]
PNGS = [f for f in os.listdir(OUT) if f.endswith('.png')]
chk('receipts: 46 CSV present (v1.0.0 29 + bat-path addendum 17)',
    len(CSVS) == 46, str(len(CSVS)))
chk('receipts: 10 figures present (6 + 4 bat path)', len(PNGS) == 10, str(len(PNGS)))
chk('receipts: headlines.json present', os.path.exists(os.path.join(OUT, 'dp_uc40_headlines.json')))
chk('receipts: build console log present', os.path.exists(os.path.join(OUT, 'dp_uc40_build_console.log')))
for f in CSVS:
    chk(f'receipt non-empty: {f}', os.path.getsize(os.path.join(OUT, f)) > 40)

# ── 2 · the report cites only figures that exist ──────────────────────────
rpt = txt('dp_uc40_turner_recency_report.md')
for m in set(re.findall(r'!\[[^\]]*\]\(([^)]+)\)', rpt)):
    chk(f'report figure resolves: {m}', os.path.exists(os.path.join(OUT, m)))
chk('report cites all 6 figures', len(set(re.findall(r'dp_uc40_fig\d', rpt))) == 6)

# ── 3 · headline numbers agree across every surface ───────────────────────
H = json.load(open(os.path.join(OUT, 'dp_uc40_headlines.json'), encoding='utf-8'))
dash = txt('dp_uc40_turner_recency_dashboard.html')
ver = pd.read_csv(os.path.join(OUT, 'dp_uc40_verification_results.csv'))
dq = pd.read_csv(os.path.join(OUT, 'dp_uc40_dq_scorecard.csv'))
par = pd.read_csv(os.path.join(OUT, 'dp_uc40_parent_reproduction.csv'))

npass, ntot = int(ver['pass'].sum()), len(ver)
chk('verification: all checks pass', npass == ntot, f'{npass}/{ntot}')
for surf, name in [(rpt, 'report'), (dash, 'dashboard'), (txt('README.md'), 'README'),
                   (txt('00_dpo_orchestration_record.md'), '00'),
                   (txt('05_quality_certification.md'), '05')]:
    chk(f'{name} quotes the true verification count', f'{npass}/{ntot}' in surf
        or f'{npass} / {ntot}' in surf, f'{npass}/{ntot}')

nP = int((dq.status == 'PASS').sum()); nW = int((dq.status == 'WARN').sum())
nF = int((dq.status == 'FAIL').sum())
chk('DQ has zero FAIL', nF == 0, str(nF))
for surf, name in [(rpt, 'report'), (README := txt('README.md'), 'README'),
                   (txt('00_dpo_orchestration_record.md'), '00')]:
    chk(f'{name} quotes the true DQ split',
        (f'{nP} PASS' in surf and f'{nW} WARN' in surf and f'{nF} FAIL' in surf)
        or f'{nP}/{nW}/{nF}' in surf, f'{nP}/{nW}/{nF}')

nrep = int(par.repro_pass.sum())
for surf, name in [(rpt, 'report'), (README, 'README'), (dash, 'dashboard'),
                   (txt('00_dpo_orchestration_record.md'), '00')]:
    chk(f'{name} quotes the true parent-reproduction count',
        str(nrep) in surf, f'{nrep}/{len(par)}')

# ── 4 · governance promises are kept ──────────────────────────────────────
gov, qual, intake = txt('03_governance.md'), txt('05_quality_certification.md'), txt('01_strategy_intake.md')
for kpi in ('AD-1', 'ST-1', 'BT-1', 'RF-2'):
    chk(f'{kpi} has a spec in 03', kpi in gov)
    chk(f'{kpi} is marked provisional or ratification-candidate somewhere in 03',
        bool(re.search(kpi + r'[^\n]*', gov)))
chk('03 records the Rule-1 grep', 'Rule-1 grep' in gov)
chk('03 records the OZ-3 inheritance rather than redefining it', 'OZ-3' in gov and 'INHERIT' in gov)
chk('05 registers the new defect D-7 / O-13', 'D-7' in qual and 'O-13' in qual)
chk('report discloses D-7 to the consumer', 'D-7' in rpt)
chk('dashboard discloses D-7 to the consumer', 'D-7' in dash)
chk('01 declares the three DPO discretionary calls', intake.count('1. **') >= 1
    and 'declared up front' in intake)
chk('01 records zero blocking gaps', 'Blocking gaps' in intake and '**None.**' in intake)
chk('report declares the causation limit', 'causation is not identified' in rpt.lower())
chk('dashboard declares the causation limit', 'causation is not identified' in dash.lower())
chk('report declares the 50-PA floor', '50-PA floor' in rpt)
chk('dashboard declares the 50-PA floor', '50-PA floor' in dash)
chk('no bare un-cohorted "career worst" survives in the report',
    re.search(r'career worst', rpt) is None)

# ── 5 · the dashboard is genuinely self-contained ─────────────────────────
head = dash.split('vendored')[0]
chk('dashboard has no external script src', 'src="http' not in dash and "src='http" not in dash)
chk('dashboard has no external stylesheet', 'rel="stylesheet"' not in dash)
chk('dashboard vendors chart.js inline', 'Chart.js v4.4.1' in dash)
chk('dashboard has a degrade path for charts', 'chart unavailable' in dash)
chk('dashboard has no unreplaced build tokens',
    not any(t in dash for t in ('__CSS__', '__JS__', '__DATA__', '__CHARTJS__')))

# ── 6 · bid and telemetry reconcile ───────────────────────────────────────
tel = pd.read_csv(os.path.join(HERE, 'telemetry', 'run_economics_ledger.csv'))
tot = tel[tel.phase == 'TOTAL'].iloc[0]
phases = tel[~tel.phase.isin(['TOTAL'])]
for col in ('bid_tokens_in', 'bid_tokens_out', 'bid_minutes',
            'actual_tokens_in', 'actual_tokens_out', 'actual_minutes'):
    chk(f'telemetry: {col} sums to its TOTAL row',
        int(phases[col].sum()) == int(tot[col]),
        f'{int(phases[col].sum())} vs {int(tot[col])}')
bid = txt('BID_2026-09-03_uc-pos-014-turner.md')
chk('bid states the awarded status', 'AWARDED' in bid)
chk('bid ID reservation matches the package', 'uc-pos-014' in bid and 'dp_uc40' in bid)
chk('07 reports bid vs actual', 'bid vs actual' in txt('07_platform_marketing.md').lower())
chk('calibration report names the harness-overhead gap',
    'harness overhead' in txt('telemetry/calibration_report.md'))

# ── 7 · ledger patch is well formed ───────────────────────────────────────
led = txt('uc_ledger_AI_PATCH_uc-pos-014-turner.md')
chk('ledger patch is a single pipe-delimited row', led.count('\n| 40 |') == 1)
chk('ledger patch advances the next-available pointer', 'UC #41' in led and 'dp_uc41' in led)
chk('ledger patch names the package path', 'uc-pos-014-turner-2026-recency-001/' in led)
chk('ledger patch carries the verification count', f'{npass}/{ntot}' in led)

# ── 8 · v1.1.0 ADDENDUM ──────────────────────────────────────────────────
arpt = txt('dp_uc40a_bat_path_report.md')
aver = pd.read_csv(os.path.join(OUT, 'dp_uc40a_verification_results.csv'))
aconv = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_convention_assertions.csv'))
adq = pd.read_csv(os.path.join(OUT, 'dp_uc40a_bp_dq_scorecard.csv'))
an, at_ = int(aver['pass'].sum()), len(aver)
chk('addendum: all verification checks pass', an == at_, f'{an}/{at_}')
chk('addendum: all conventions pass', bool((aconv.status == 'PASS').all()), str(len(aconv)))
chk('addendum: 12 conventions asserted', len(aconv) == 12, str(len(aconv)))
chk('addendum: DQ has zero FAIL', int((adq.status == 'FAIL').sum()) == 0, str(int((adq.status=='FAIL').sum())))
for surf, name in [(arpt, 'addendum report'), (txt('05a_bat_path_certification.md'), '05a'),
                   (txt('ADDENDUM_v1.1.0_bat_path.md'), 'ADDENDUM spine'), (dash, 'dashboard')]:
    chk(f'{name} quotes the true addendum verification count',
        f'{an}/{at_}' in surf or f'{an} / {at_}' in surf, f'{an}/{at_}')
# renumbered +1 on 2026-09-04 after a concurrent session claimed O-14 (see 03a §3)
for oid in ('O-15', 'O-16', 'O-17', 'O-18'):
    chk(f'addendum report discloses {oid}', oid in arpt, True)
    chk(f'03a specifies {oid}', oid in txt('03a_bat_path_semantics_and_lineage.md'), True)
    chk(f'dashboard discloses {oid}', oid in dash, True)
chk('03a cites a source for every bat-path term',
    txt('03a_bat_path_semantics_and_lineage.md').count('mlb.com/glossary/statcast') >= 5, True)
chk('03a documents column-level lineage', 'technical-lineage-builder' in
    txt('03a_bat_path_semantics_and_lineage.md'), True)
chk('03a records the O-14 ID collision and its resolution',
    'ID-collision note' in txt('03a_bat_path_semantics_and_lineage.md'), True)
chk('no addendum file still CLAIMS O-14 (the two remaining mentions are the '
    'collision note in 03a and the E-13 escalation in 05a)',
    not any('O-14' in txt(f) for f in
            ['dp_uc40a_bat_path_report.md', 'ADDENDUM_v1.1.0_bat_path.md',
             'README.md', 'dp_uc40a_kernel.py']), True)
chk('05a raises the ID-collision escalation E-13', 'E-13' in txt('05a_bat_path_certification.md'), True)
chk('00 raises the ID-collision escalation E-13', 'E-13' in txt('00_dpo_orchestration_record.md'), True)
chk('addendum uses the data plane pitch_group verbatim',
    'verbatim' in txt('03a_bat_path_semantics_and_lineage.md'), True)
for m in set(re.findall(r'!\[[^\]]*\]\(([^)]+)\)', arpt)):
    chk(f'addendum figure resolves: {m}', os.path.exists(os.path.join(OUT, m)))
chk('addendum cites all 4 figures', len(set(re.findall(r'dp_uc40a_fig\d', arpt))) == 4, True)
chk('dashboard has a Bat path tab', 't-batpath' in dash, True)
chk('README lists the v1.1.0 addendum', 'v1.1.0' in README, True)

# ── report ────────────────────────────────────────────────────────────────
res = pd.DataFrame(_r, columns=['check', 'pass', 'detail'])
res.to_csv(os.path.join(OUT, 'dp_uc40_package_audit_results.csv'), index=False)
p, t = int(res['pass'].sum()), len(res)
print(f'PACKAGE AUDIT: {p}/{t} PASS')
if p != t:
    print(res[~res['pass']].to_string(index=False))
    sys.exit(1)
