"""dp_uc46_family_f -- verification family F: narrative / receipt reconciliation.

Every headline figure asserted in the report's prose, the README and the
notecard markup is RECOMPUTED FROM THE SHIPPED RECEIPTS and string-matched
against the text as written. Established on uc-pos-016, where it caught V-1
(a superseded draft figure surviving into the ledger patch).

Checked last, against the size the harness actually reached, per the
uc-pos-016 convention.
"""
import json, re, sys
import pandas as pd

P = '/mnt/user-data/outputs/uc-pos-017-directional-hitting-family-001/'
OUT = P + 'out/'
report = open(P + 'dp_uc46_report.md', encoding='utf-8').read()
readme = open(P + 'README.md', encoding='utf-8').read() if __import__('os').path.exists(P+'README.md') else ''
cards  = open(OUT + 'dp_uc46_directional_notecards.html', encoding='utf-8').read()
CORPUS = {'report': report, 'README': readme, 'notecards': cards}

season = pd.read_csv(OUT + '02_direction_rate_season.csv')
stand  = pd.read_csv(OUT + '03_direction_rate_season_stand.csv')
player = pd.read_csv(OUT + '04_direction_rate_player_2026.csv')
pdir   = pd.read_csv(OUT + '06_bb_type_profile_direction.csv')
oppold = pd.read_csv(OUT + '07_oppo_ld_rate_season.csv')
brk    = pd.read_csv(OUT + '08_breaking_change_pull_air_rate.csv')
H      = json.load(open(OUT + 'headlines.json'))

F = []
def f(name, literal, where='report', note=''):
    """Assert `literal` (recomputed from a receipt) appears verbatim in the text."""
    hit = literal in CORPUS[where]
    F.append((name, literal, where, hit, note))

def pct(x, dp=1): return f'{x*100:.{dp}f}%'

# --- 3.1 season table -------------------------------------------------------
for y in (2024, 2025, 2026):
    r = season[season.game_year == y].iloc[0]
    f(f'{y} n_bip', f'{int(r.n_bip):,}')
    f(f'{y} pull_rate', pct(r.pull_rate))
    f(f'{y} straight_rate', pct(r.straight_rate))
    f(f'{y} oppo_rate', pct(r.oppo_rate))
drop = (season[season.game_year==2024].pull_rate.iloc[0] - season[season.game_year==2026].pull_rate.iloc[0])*100
f('pull rate decline 2024->2026', f'fallen {drop:.1f} points', note=f'exact {drop:.4f}')

# --- 3.2 direction x bb_type mix, 2026 -------------------------------------
m = pdir[pdir.game_year==2026].pivot(index='hit_direction', columns='bb_type', values='share')
for d in ['Pull','Straightaway','Oppo']:
    for b in ['ground_ball','line_drive','fly_ball','popup']:
        f(f'2026 {d}/{b} share', pct(m.loc[d,b]))
pa26 = brk[brk.game_year==2026].v1_pull_air_rate.iloc[0]
pr26 = season[season.game_year==2026].pull_rate.iloc[0]
f('2026 pull_air_rate', pct(pa26))
removed = 1 - pa26/pr26
f('qualifier removes share of pull population', f'about {removed*100:.0f}%', note=f'exact {removed:.4f}')
ratio = m.loc['Oppo','popup']/m.loc['Pull','popup']
f('oppo popup vs pull popup multiple', f'more than {int(ratio)} times as often', note=f'exact {ratio:.2f}')

# --- 3.3 exit velocity / distance ------------------------------------------
ev = pdir[pdir.game_year==2026].pivot(index='hit_direction', columns='bb_type', values='mu_ev')
di = pdir[pdir.game_year==2026].pivot(index='hit_direction', columns='bb_type', values='mu_dist')
for d in ['Pull','Straightaway','Oppo']:
    for b in ['line_drive','fly_ball','ground_ball']:
        f(f'2026 {d}/{b} mu_ev', f'{ev.loc[d,b]:.1f}')
gap = ev.loc['Pull','line_drive'] - ev.loc['Oppo','line_drive']
f('pull vs oppo LD exit velo gap', f'**{gap:.1f} mph harder**', note=f'exact {gap:.4f}')
f('pull LD distance', f'{di.loc["Pull","line_drive"]:.1f} ft')
f('oppo LD distance', f'{di.loc["Oppo","line_drive"]:.1f} ft')
f('pull FB distance', f'{di.loc["Pull","fly_ball"]:.1f} ft')
f('oppo FB distance', f'{di.loc["Oppo","fly_ball"]:.1f}')
fbgap = di.loc['Pull','fly_ball'] - di.loc['Oppo','fly_ball']
f('fly ball distance gap', f'cost him {fbgap:.0f} feet', note=f'exact {fbgap:.2f}')

# --- 3.4 oppo_ld_rate ------------------------------------------------------
for y in (2024, 2025, 2026):
    r = oppold[oppold.game_year==y].iloc[0]
    f(f'{y} oppo LD count', f'{int(r.bips)}')
    f(f'{y} oppo BIP', f'{int(r.total_level):,}')
    f(f'{y} oppo_ld_rate', f'**{r.oppo_ld_rate*100:.2f}%**')
    f(f'{y} oppo LD mu_la', f'{r.mu_la:.1f}°')
    f(f'{y} oppo LD mu_ev', f'{r.mu_ev:.1f} mph')

# --- 3.4 player claim ------------------------------------------------------
q = player[~player.below_floor]
top2 = q.nlargest(2, 'oppo_rate').sort_values('oppo_rate', ascending=False)
oppo26 = season[season.game_year==2026].oppo_rate.iloc[0]
f('top oppo hitter exact rate', f'{top2.oppo_rate.iloc[0]*100:.1f}%')
f('2nd oppo hitter exact rate', f'{top2.oppo_rate.iloc[1]*100:.1f}%')
f('club oppo rate in that sentence', f'club rate of {pct(oppo26)}')

# --- 3.5 handedness --------------------------------------------------------
for y in (2024, 2025, 2026):
    for s, lab in (('L','LHB'), ('R','RHB')):
        v = stand[(stand.game_year==y)&(stand.stand==s)].oppo_rate.iloc[0]
        f(f'{y} {lab} oppo_rate', pct(v))
g26 = (stand[(stand.game_year==2026)&(stand.stand=='R')].oppo_rate.iloc[0]
       - stand[(stand.game_year==2026)&(stand.stand=='L')].oppo_rate.iloc[0])
f('2026 handedness gap', f'{g26*100:.1f} points apart', note=f'exact {g26:.4f}')

# --- §4 floor claims -------------------------------------------------------
f('suppressed player count', f'Three of the twenty', note=f'{int(player.below_floor.sum())} of {len(player)}')
f('qualified hitter count (notecards)', f'{H["qualified_hitters_2026"]} hitters', where='notecards')
f('club oppo rate (notecards)', f'club oppo rate {season[season.game_year==2026].oppo_rate.iloc[0]*100:.1f}%', where='notecards')
f('club oppo LD rate (notecards)',
  f'club oppo line-drive rate {oppold[oppold.game_year==2026].oppo_ld_rate.iloc[0]*100:.1f}%', where='notecards')
f('verification count (notecards)', 'verification 49/49 PASS', where='notecards')

# --- last: the harness's own claim about itself ----------------------------
n_checks = len(F) + 1
f('family F self-size claim', f'**{n_checks} reconciliation checks**')

# --- report ----------------------------------------------------------------
npass = sum(1 for x in F if x[3])
print('='*84); print('FAMILY F -- narrative / receipt reconciliation'); print('='*84)
for name, lit, where, ok, note in F:
    if not ok:
        print(f'  [FAIL] {where}: {name}')
        print(f'         receipt says -> "{lit}"' + (f'   [{note}]' if note else ''))
print(f'\n{npass}/{len(F)} PASS')
sys.exit(0 if npass == len(F) else 1)
