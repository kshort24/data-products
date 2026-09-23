"""
dp_uc47_kernel.py — governed kernel for UC #47 / uc-pps-032
"Archetype Gap Analysis — pilot: the Elite RHP Four-Seamer"

INHERITANCE POLICY (see 03_governance.md §1, Rule-1):
  * Sections A and B are INHERITED BY IMPORT from `dp_uc44_kernel.py` (uc-pps-030),
    not transcribed. The verification harness asserts the sha256 of the imported
    file, so any edit to the parent is detected rather than silently absorbed.
      A: get_stats, measure_calcs, mcgs, nresults, SWINGS, WHIFFS, whiff_rate ...
      B: apply_woba_weights, data_root
      SG-1 scouting_grade, SG-3 grade_divergence_flag, SG-5 grade_label, _round5
  * Section C is NEW to this UC. Every object is PROVISIONAL and unratified.
    It is written ARCHETYPE-AGNOSTIC: the elite RHP four-seam is one instance of
    `ArchetypeSpec`, not a shape baked into the functions.

Data plane    : C:\\Users\\Kellen\\OneDrive\\Documents\\Python Scripts\\MLB
Control plane : C:\\Users\\Kellen\\OneDrive\\Documents\\Agents for Data Products
"""
from __future__ import annotations

import glob
import hashlib
import os
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Parent kernel (uc-pps-030) — import, never copy
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
for _p in [os.environ.get("MLB_DATA_ROOT"), str(_HERE), "/mnt/user-data/uploads/MLB",
           r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]:
    if _p and (Path(_p) / "dp_uc44_kernel.py").exists() and _p not in sys.path:
        sys.path.insert(0, _p)
import dp_uc44_kernel as K44  # noqa: E402

PARENT_KERNEL_SHA256 = "a2c119096db24fdbfca4ca7f79b9dcb32c379d6f1ec9566aa7376837711582e3"
ROOT = K44.ROOT
SWINGS, WHIFFS = K44.SWINGS, K44.WHIFFS
scouting_grade, grade_label, grade_divergence_flag, _round5 = (
    K44.scouting_grade, K44.grade_label, K44.grade_divergence_flag, K44._round5)
PITCH_KEY = ["game_pk", "at_bat_number", "pitch_number"]


def parent_kernel_hash() -> str:
    return hashlib.sha256(Path(K44.__file__).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# House constants (brand-center-mcp :: get_brand_guidelines, verbatim values)
# ---------------------------------------------------------------------------
PHILLIES_RED, PHILLIES_NAVY, PHILLIES_CREAM = "#E81828", "#002D72", "#F3E5AB"
NEUTRAL_GRAY, LIGHT_GRAY = "#8C8C8C", "#D9D9D9"

# Entity locks — MLBAM ids, never a name filter
COHORT = {554430: "Zack Wheeler", 691725: "Andrew Painter", 686934: "Alex McFarlane",
          661395: "Jhoan Duran", 680742: "Jonathan Bowlan", 622554: "Seranthony Domínguez"}
# Identity-only lookups (never a data source). Precedent: uc-pps-030 confirmed Grant Holmes = 656550.
EXTERNAL_IDENTITY = {694819: ("Jacob Misiorowski",
                              "baseballsavant.mlb.com/savant-player/jacob-misiorowski-694819 (web search 2026-09-22)")}
ANCHOR_DATE = "2026-09-20"          # last game in the Phillies log at build time
CURRENT_SEASON = 2026

MLB_CLUBS = {'AZ', 'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CWS', 'CIN', 'CLE', 'COL', 'DET', 'HOU',
             'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 'ATH', 'PHI', 'PIT',
             'SD', 'SF', 'SEA', 'STL', 'TB', 'TEX', 'TOR', 'WSH'}

LOAD_COLS = ['game_date', 'game_year', 'game_type', 'game_pk', 'at_bat_number', 'pitch_number',
             'pitcher', 'batter', 'player_name', 'p_throws', 'stand', 'pitch_type', 'pitch_name',
             'release_speed', 'release_spin_rate', 'pfx_x', 'pfx_z', 'release_extension',
             'description', 'events', 'type', 'zone', 'des', 'home_team', 'away_team',
             'estimated_woba_using_speedangle', 'delta_run_exp', 'plate_x', 'plate_z']


# ============================================================================
# SECTION C — NEW to UC #47 (provisional, unratified — see 03_governance.md §2)
# ============================================================================

# ---- FR-1 -------------------------------------------------------------------
def house_pitch_universe(root: Path | None = None, years=range(2015, 2027)):
    """FR-1 `house_pitch_universe` (NEW-UC47, provisional).

    The client's own comparison frame — "every four-seamer in my dataset" —
    is `pd.concat([pps, pos, nphl])`. This function builds that frame and
    governs it.

    Sources : data/phillies/phils_YYYY.parquet (both phillies_role values)
              + every data/opponents/*.parquet (the `nphl` frame, 128 files).
    Steps   : 1. tag every row with `src` ('phils'|'nphl'), `source_file`, and
                 `row_frame` (PHI | VS_PHI | FILE | TEAM | INCIDENTAL, see below)
              2. LEVEL GATE — keep a row only if home_team AND away_team are MLB
                 clubs. Level is decided by source, never by date (GT-1).
              3. DEDUP — drop nphl rows whose PITCH_KEY exists in the Phillies
                 logs (Phillies logs win), then drop nphl internal duplicates.
              4. game_type == 'R'.
    row_frame: PHI        — Phillies pitcher, Phillies log (complete season)
               VS_PHI     — opponent pitcher in a Phillies game (complete outing)
               FILE       — nphl file keyed on this single pitcher (complete season)
               TEAM       — nphl file keyed on several pitchers of one club
               INCIDENTAL — nphl file keyed on a HITTER; the pitcher appears only
                            because he faced that hitter (partial outing)
    Keying  : a file is pitcher-keyed iff every pitcher maps to exactly one
              player_name AND n_names == n_pitchers. Otherwise player_name is the
              batter (e.g. `giants-of-rangers-of-24` is batter-keyed).
    Returns : (U, receipt) — receipt is a dict of step counts, shipped as a CSV.
    """
    import pyarrow.parquet as pq
    root = Path(root or ROOT)
    rec = {}
    fr = []
    for y in years:
        f = root / 'data' / 'phillies' / f'phils_{y}.parquet'
        sch = pq.read_schema(f).names
        t = pq.read_table(f, columns=[c for c in LOAD_COLS + ['phillies_role'] if c in sch]).to_pandas()
        t['src'], t['source_file'] = 'phils', f'phils_{y}'
        t['row_frame'] = np.where(t.phillies_role == 'pitching', 'PHI', 'VS_PHI')
        fr.append(t)
    phils = pd.concat(fr, ignore_index=True)
    rec['phils_rows'] = len(phils)

    fr, keying = [], []
    for f in sorted(glob.glob(str(root / 'data' / 'opponents' / '*.parquet'))):
        sch = pq.read_schema(f).names
        t = pq.read_table(f, columns=[c for c in LOAD_COLS if c in sch]).to_pandas()
        name = Path(f).stem
        t['src'], t['source_file'] = 'nphl', name
        pk = bool((t.groupby('pitcher').player_name.nunique() == 1).all()
                  and t.player_name.nunique() == t.pitcher.nunique())
        npit = t.pitcher.nunique()
        mlb = bool((t.home_team.isin(MLB_CLUBS) & t.away_team.isin(MLB_CLUBS)).mean() > 0.5)
        keying.append(dict(source_file=name, rows=len(t), pitchers=npit, batters=t.batter.nunique(),
                           pitcher_keyed=pk, level='MLB' if mlb else 'MiLB',
                           y0=int(t.game_year.min()), y1=int(t.game_year.max())))
        t['row_frame'] = ('FILE' if npit == 1 else 'TEAM') if pk else 'INCIDENTAL'
        t['phillies_role'] = pd.NA
        fr.append(t)
    nphl = pd.concat(fr, ignore_index=True)
    keying = pd.DataFrame(keying)
    rec['nphl_files'] = len(keying)
    rec['nphl_rows'] = len(nphl)
    rec['nphl_milb_files'] = int((keying.level == 'MiLB').sum())

    lvl = nphl.home_team.isin(MLB_CLUBS) & nphl.away_team.isin(MLB_CLUBS)
    rec['nphl_rows_milb_removed'] = int((~lvl).sum())
    nphl = nphl[lvl]
    key_phils = pd.MultiIndex.from_frame(phils[PITCH_KEY])
    in_phils = pd.MultiIndex.from_frame(nphl[PITCH_KEY]).isin(key_phils)
    rec['nphl_rows_dup_of_phils'] = int(in_phils.sum())
    nphl = nphl[~in_phils]
    # precedence inside nphl: a pitcher-keyed row (FILE/TEAM) beats an INCIDENTAL copy
    order = nphl.row_frame.map({'FILE': 0, 'TEAM': 1, 'INCIDENTAL': 2})
    nphl = nphl.assign(_o=order).sort_values('_o', kind='stable')
    d = nphl.duplicated(PITCH_KEY)
    rec['nphl_rows_internal_dup'] = int(d.sum())
    nphl = nphl[~d].drop(columns='_o')

    U = pd.concat([phils, nphl], ignore_index=True)
    rec['union_rows_all_game_types'] = len(U)
    U = U[U.game_type == 'R'].copy()
    rec['union_rows_regular_season'] = len(U)
    rec['union_dup_pitch_keys'] = int(U.duplicated(PITCH_KEY).sum())
    return U, rec, keying


def kellen_frame_raw(root: Path | None = None, pitch_type='FF'):
    """The client's frame EXACTLY as his notebook builds it (for HP reconciliation):
    pd.concat([pps, pos, nphl]) with nphl de-duplicated only within itself
    (mlb_data.get_nphillies_data), no level gate, no cross-source dedup, no
    game_type filter on nphl. Used ONLY to reproduce his published claims."""
    import pyarrow.parquet as pq
    root = Path(root or ROOT)
    cols = ['game_pk', 'at_bat_number', 'pitch_number', 'pitcher', 'player_name', 'p_throws',
            'pitch_type', 'pfx_z', 'release_spin_rate', 'game_year', 'game_type', 'home_team']
    ph = pd.concat([pq.read_table(f, columns=cols).to_pandas()
                    for f in sorted(glob.glob(str(root / 'data' / 'phillies' / '*.parquet')))])
    ph = ph[ph.game_type == 'R']          # get_phillies_data serves regular season
    nf = []
    for f in sorted(glob.glob(str(root / 'data' / 'opponents' / '*.parquet'))):
        s = pq.read_schema(f).names
        nf.append(pq.read_table(f, columns=[c for c in cols if c in s]).to_pandas())
    n = pd.concat(nf).drop_duplicates(PITCH_KEY, keep='first')
    out = pd.concat([ph, n], ignore_index=True)
    return out[out.pitch_type == pitch_type]


# ---- NR-1 -------------------------------------------------------------------
def fold(s: str) -> str:
    """Accent-fold + lowercase (the O-12 normalisation)."""
    if not isinstance(s, str):
        return ''
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).lower().strip()


def resolve_pitcher_names(U: pd.DataFrame) -> pd.DataFrame:
    """NR-1 `resolve_pitcher_names` (NEW-UC47, provisional).

    `player_name` is the BATTER on Phillies batting-role rows and on every
    batter-keyed nphl file. A pitcher's name is therefore only trustworthy from
    a pitcher-keyed row (row_frame in PHI / FILE / TEAM).

    Tier 1 : modal player_name over pitcher-keyed rows ("Last, First").
    Tier 2 : `des`-parse — Statcast names the pitcher in wild-pitch, balk and
             pickoff text ("... by pitcher Chase Burns."). Modal match per id.
    Tier 3 : EXTERNAL_IDENTITY — a logged, identity-only lookup for an id that
             tiers 1-2 cannot name and that a deliverable must name.
    Gate   : Tier 2 is trusted only if, on ids that have BOTH tiers, the
             accent-folded agreement rate is >= 0.97. The measured rate ships in
             the receipt. Unresolved ids print as "MLBAM <id>" — never guessed.
    Returns: DataFrame[pitcher, pitcher_name, name_tier, name_display]
    """
    keyed = U[U.row_frame.isin(['PHI', 'FILE', 'TEAM'])]
    t1 = keyed.groupby('pitcher').player_name.agg(lambda s: s.mode().iloc[0])
    d = U[U.des.str.contains('by pitcher|, pitcher ', na=False, regex=True)]
    nm = d.des.str.extract(r"(?:by pitcher|, pitcher) ([A-Z][A-Za-zÀ-ÿ\.\'\- ]+?)(?:[\.,]| to | from|$)")[0]
    t2 = pd.Series(nm.values, index=d.pitcher.values).dropna()
    t2 = t2.groupby(level=0).agg(lambda s: s.mode().iloc[0])

    def lf_to_fl(s):
        p = s.split(', ')
        return f"{p[1]} {p[0]}" if len(p) == 2 else s
    both = t1.index.intersection(t2.index)
    agree = np.mean([fold(lf_to_fl(t1[i])) == fold(t2[i]) for i in both]) if len(both) else np.nan
    ids = pd.Index(U.pitcher.dropna().unique())
    out = pd.DataFrame({'pitcher': ids})
    out['pitcher_name'] = out.pitcher.map(t1)
    out['name_tier'] = np.where(out.pitcher_name.notna(), 'T1_keyed', None)
    use_t2 = out.pitcher_name.isna() & out.pitcher.isin(t2.index) & (agree >= 0.97)
    out.loc[use_t2, 'pitcher_name'] = out.loc[use_t2, 'pitcher'].map(t2)
    out.loc[use_t2, 'name_tier'] = 'T2_des'
    out.loc[out.pitcher_name.isna(), 'name_tier'] = 'UNRESOLVED'
    out['name_display'] = [lf_to_fl(n) if (isinstance(n, str) and ', ' in n) else
                           (n if isinstance(n, str) else f'MLBAM {int(p)}')
                           for n, p in zip(out.pitcher_name, out.pitcher)]
    for pid, (nmx, why) in EXTERNAL_IDENTITY.items():   # tier 3: logged external identity checks
        m = out.pitcher == pid
        if m.any() and out.loc[m, 'name_tier'].iloc[0] == 'UNRESOLVED':
            out.loc[m, 'name_display'] = nmx
            out.loc[m, 'name_tier'] = 'T3_external_identity'
    for pid, nmx in COHORT.items():            # entity locks win over any parse
        out.loc[out.pitcher == pid, 'name_display'] = nmx
    out.attrs['t2_agreement'] = float(agree)
    out.attrs['t2_overlap_n'] = int(len(both))
    return out


# ---- AF-1 -------------------------------------------------------------------
@dataclass
class ArchetypeSpec:
    """AF-1 `archetype_spec` (NEW-UC47, provisional).

    An archetype is a pitch, a hand, an era, two axes of metrics and a bar.
    Everything downstream reads this object, so a second archetype (an elite
    LHP sweeper, a high-spin RHP curveball) is a new instance, not new code.

    shape   : physical characteristics of the pitch — what it LOOKS like.
    results : what the pitch DOES to hitters.
    Each metric is (name, higher_is_better). Metric names resolve through
    METRIC_DEFS below; an unknown name fails loudly.
    """
    name: str
    pitch_type: str
    throws: str
    era: tuple
    shape: list
    results: list
    context: list = field(default_factory=list)
    pop_floor: int = 100          # SG-2: pitches of the type per pitcher-season, population member
    subject_floor: int = 50       # SG-2: pitches of the type to be graded at all
    swing_floor: int = 25         # SG-2: swings before a whiff grade is published
    elite_grade: float = 60.0     # SG-5 'plus'
    trend_alpha: float = 0.05     # SG-6
    display: str = ''


ELITE_RHP_FF = ArchetypeSpec(
    name='elite_rhp_ff', pitch_type='FF', throws='R', era=(2018, 2026),
    shape=[('velo', True), ('ivb_in', True), ('spin', True)],
    results=[('whiff_rate', True), ('rv100', True)],
    context=['ext', 'hb_in', 'xwoba', 'usage'],
    display='Elite RHP four-seam fastball')

# metric -> (numerator source, aggregation, denominator for stabilization)
METRIC_DEFS = {
    'velo':       dict(label='Velocity (mph)', stab_n='n'),
    'ivb_in':     dict(label='Induced vertical break (in)', stab_n='n'),
    'spin':       dict(label='Spin rate (rpm)', stab_n='n'),
    'whiff_rate': dict(label='Whiff rate', stab_n='swings'),
    'rv100':      dict(label='Run value per 100 (pitcher)', stab_n='n'),
    'ext':        dict(label='Extension (ft)', stab_n='n'),
    'hb_in':      dict(label='Horizontal break (in)', stab_n='n'),
    'xwoba':      dict(label='xwOBA, PA ending on the pitch', stab_n='pa_end'),
    'usage':      dict(label='Usage share', stab_n='pitches_all'),
}


# ---- AF-2 -------------------------------------------------------------------
def archetype_frame(U: pd.DataFrame, spec: ArchetypeSpec) -> pd.DataFrame:
    """AF-2 `archetype_frame` (NEW-UC47, provisional).

    Grain : one row per (game_year, pitcher) — a pitcher-season — for pitchers
            of hand spec.throws inside spec.era, with >= 1 pitch of spec.pitch_type.
    Cols  : n, swings, whiffs, pa_end, games, pitches_all, usage,
            velo, ivb_in (pfx_z*12), spin, ext, hb_in (pfx_x*12),
            whiff_rate (NaN when swings == 0 — never 0),
            rv100 = -100 * mean(delta_run_exp)  (PITCHER perspective: + is good),
            xwoba = mean(estimated_woba_using_speedangle) over PA-ending rows,
            frame (majority row_frame), coverage (COMPLETE|PARTIAL),
            role (SP|RP|UNK) — median pitches per observed COMPLETE outing >= 50,
            with INCIDENTAL rows excluded because they are partial outings.
    """
    y0, y1 = spec.era
    d = U[(U.p_throws == spec.throws) & U.game_year.between(y0, y1)]
    tot = d.groupby(['game_year', 'pitcher']).agg(pitches_all=('pitch_type', 'size'))
    outing_rows = d[d.row_frame != 'INCIDENTAL']
    outings = outing_rows.groupby(['game_year', 'pitcher', 'game_pk']).size().rename('pp')
    role = outings.groupby(level=[0, 1]).median().rename('med_pitches_per_outing')
    f = d[d.pitch_type == spec.pitch_type].copy()
    f['_sw'] = f.description.isin(SWINGS)
    f['_wh'] = f.description.isin(WHIFFS)
    f['_pa'] = f.estimated_woba_using_speedangle.notna()
    g = f.groupby(['game_year', 'pitcher']).agg(
        n=('pitch_type', 'size'), swings=('_sw', 'sum'), whiffs=('_wh', 'sum'),
        pa_end=('_pa', 'sum'), games=('game_pk', 'nunique'),
        velo=('release_speed', 'mean'), ivb=('pfx_z', 'mean'), spin=('release_spin_rate', 'mean'),
        ext=('release_extension', 'mean'), hb=('pfx_x', 'mean'),
        dre=('delta_run_exp', 'mean'), xwoba=('estimated_woba_using_speedangle', 'mean'),
        frame=('row_frame', lambda s: s.value_counts().index[0]))
    g = g.join(tot).join(role).reset_index()
    g['usage'] = g.n / g.pitches_all
    g['ivb_in'] = g.ivb * 12.0
    g['hb_in'] = g.hb * 12.0
    g['whiff_rate'] = np.where(g.swings > 0, g.whiffs / g.swings.where(g.swings > 0), np.nan)
    g['rv100'] = -100.0 * g.dre
    g['coverage'] = np.where(g.frame.isin(['PHI', 'FILE', 'TEAM']), 'COMPLETE', 'PARTIAL')
    g['role'] = np.select([g.med_pitches_per_outing >= 50, g.med_pitches_per_outing < 50],
                          ['SP', 'RP'], default='UNK')
    return g.drop(columns=['ivb', 'hb', 'dre'])


# ---- SG-7 -------------------------------------------------------------------
def split_half_k(F: pd.DataFrame, metric: str, min_n: int = 200, seed_col_order=None):
    """SG-7a `stabilization_k` (NEW-UC47, provisional).

    How many pitches (or swings) until a metric is half signal, half noise.
    Pitch rows of each qualifying pitcher-season are ordered (date, at-bat,
    pitch) and split odd/even. r_half = correlation of the two half-season
    values across pitcher-seasons; Spearman-Brown lifts it to the full-sample
    reliability r_full at the mean denominator n_bar, and
        k = n_bar * (1 - r_full) / r_full
    is the denominator at which reliability = 0.5. Deterministic (no RNG).
    metric in {'whiff_rate','rv100','velo','ivb_in','spin'}.
    """
    F = F.sort_values(['game_year', 'pitcher', 'game_date', 'at_bat_number', 'pitch_number'])
    if metric == 'whiff_rate':
        F = F[F.description.isin(SWINGS)].copy()
        F['_v'] = F.description.isin(WHIFFS).astype(float)
    elif metric == 'rv100':
        F = F.copy(); F['_v'] = -100.0 * F.delta_run_exp
    elif metric == 'ivb_in':
        F = F.copy(); F['_v'] = 12.0 * F.pfx_z
    else:
        src = {'velo': 'release_speed', 'spin': 'release_spin_rate'}[metric]
        F = F.copy(); F['_v'] = F[src]
    F = F.dropna(subset=['_v'])
    F['_i'] = F.groupby(['game_year', 'pitcher']).cumcount()
    F['_h'] = F._i % 2
    cnt = F.groupby(['game_year', 'pitcher']).size()
    keep = cnt[cnt >= min_n].index
    F = F.merge(pd.DataFrame(index=keep).reset_index(), on=['game_year', 'pitcher'])
    h = F.groupby(['game_year', 'pitcher', '_h'])._v.mean().unstack('_h')
    r_half = float(h[0].corr(h[1]))
    n_bar = float(cnt.loc[keep].mean())
    r_full = 2 * r_half / (1 + r_half)
    k = n_bar * (1 - r_full) / r_full if r_full > 0 else np.inf
    return dict(metric=metric, units='swings' if metric == 'whiff_rate' else 'pitches',
                seasons=int(len(keep)), n_bar=round(n_bar, 1), r_half=round(r_half, 4),
                r_full=round(r_full, 4), k=round(float(k), 1))


def stabilize(values: pd.Series, n: pd.Series, k: float, mu: float) -> pd.Series:
    """SG-7b `stabilize` (NEW-UC47, provisional) — empirical-Bayes shrinkage.
        x_s = mu + n/(n+k) * (x - mu)
    mu is the POPULATION mean (unweighted over pitcher-seasons). NaN stays NaN.
    A 2-start sample with a spectacular whiff rate is pulled most of the way
    back to the population; a 1,300-pitch season barely moves."""
    w = n / (n + k)
    return mu + w * (values - mu)


# ---- SG-6 -------------------------------------------------------------------
def season_trend_adjust(g: pd.DataFrame, cols, pop_mask, ref_year=CURRENT_SEASON, alpha=0.05):
    """SG-6 `season_trend_adjust` (NEW-UC47, provisional).

    The league throws harder every year. A 96.2 mph four-seam in 2018 and a
    96.2 in 2026 are not the same grade. For each metric, fit OLS
    value ~ game_year over the POPULATION pitcher-seasons. If (and only if)
    the slope is significant at `alpha`, express every value in ref_year
    terms:  adj = value + slope * (ref_year - game_year).
    Metrics without a significant trend are left untouched — "adjust only
    what drifts". Returns (g_with_<col>_adj, receipt DataFrame).
    """
    from scipy.stats import linregress
    rec = []
    g = g.copy()
    P = g[pop_mask]
    for c in cols:
        x = P.dropna(subset=[c])
        lr = linregress(x.game_year.astype(float), x[c].astype(float))
        adj = bool(lr.pvalue < alpha)
        g[c + '_adj'] = g[c] + (lr.slope * (ref_year - g.game_year) if adj else 0.0)
        rec.append(dict(metric=c, slope_per_season=lr.slope, p_value=lr.pvalue, r=lr.rvalue,
                        n_pop=len(x), adjusted=adj, ref_year=ref_year,
                        shift_2018_to_ref=(lr.slope * (ref_year - 2018) if adj else 0.0)))
    return g, pd.DataFrame(rec)


# ---- AF-3 -------------------------------------------------------------------
def archetype_grades(g: pd.DataFrame, spec: ArchetypeSpec, value_suffix='_final',
                     pop_mask=None, w_shape=0.5) -> pd.DataFrame:
    """AF-3 `archetype_grades` (NEW-UC47, provisional).

    Grades every pitcher-season in `g` on every shape and results metric with
    SG-1 against the declared population (pop_mask; default n >= pop_floor),
    then rolls them up:
        shape_grade   = round5( mean(component grades) )     (SG-4 semantics)
        results_grade = round5( mean(component grades) )
        ff_elite_shape_flag     = shape_grade   >= spec.elite_grade
        ff_elite_results_flag   = results_grade >= spec.elite_grade
        ff_elite_archetype_flag = both
        ff_elite_composite      = round5( mean(shape_grade, results_grade) )
        efc_score (ranking)     = w*shape_score + (1-w)*results_score, where
                                  *_score is the UNROUNDED mean of 50+10z,
                                  clipped 20..80 — ties in rounded grades are
                                  broken by the unrounded number, never by name.
    Floors: grade only if n >= subject_floor; whiff only if swings >= swing_floor.
            Below pop_floor -> 'thin' = True (graded, not a population member).
    DPO alias: the draft name `ff_elite_stuff_flag` is RETIRED in favour of
    `ff_elite_shape_flag` — in this repo "Stuff grade" already means the WHIFF
    grade (SG-4, uc-pps-030). One word, one meaning.
    """
    g = g.copy()
    if pop_mask is None:
        pop_mask = g.n >= spec.pop_floor
    P = g[pop_mask]
    gradable = g.n >= spec.subject_floor
    for axis in ('shape', 'results'):
        comps = []
        for m, hib in getattr(spec, axis):
            col = m + value_suffix
            pop_vals = P[col].values
            gr, z, sc, pct = [], [], [], []
            for v, ok, sw in zip(g[col], gradable, g.swings):
                ok2 = ok and not (m == 'whiff_rate' and sw < spec.swing_floor)
                r = scouting_grade(v if ok2 else np.nan, pop_vals, higher_is_better=hib)
                gr.append(r['grade']); z.append(r['z']); pct.append(r['pctile'])
                sc.append(np.clip(50 + 10 * r['z'], 20, 80) if not pd.isna(r['z']) else np.nan)
            g[f'g_{m}'], g[f'z_{m}'], g[f'pct_{m}'], g[f's_{m}'] = gr, z, pct, sc
            comps.append(m)
        G = g[[f'g_{m}' for m in comps]]
        S = g[[f's_{m}' for m in comps]]
        complete = G.notna().all(axis=1)
        g[f'{axis}_grade'] = np.where(complete, [(_round5(x) if not pd.isna(x) else np.nan) for x in G.mean(axis=1)], np.nan)
        g[f'{axis}_score'] = np.where(complete, S.mean(axis=1), np.nan)
    g['ff_elite_shape_flag'] = g.shape_grade >= spec.elite_grade
    g['ff_elite_results_flag'] = g.results_grade >= spec.elite_grade
    g['ff_elite_archetype_flag'] = g.ff_elite_shape_flag & g.ff_elite_results_flag
    g['ff_elite_composite'] = [(_round5((a + b) / 2) if not (pd.isna(a) or pd.isna(b)) else np.nan)
                               for a, b in zip(g.shape_grade, g.results_grade)]
    g['efc_score'] = w_shape * g.shape_score + (1 - w_shape) * g.results_score
    g['archetype_tier'] = np.select(
        [g.ff_elite_archetype_flag, g.ff_elite_shape_flag, g.ff_elite_results_flag, g.efc_score.notna()],
        ['ELITE', 'SHAPE-ONLY', 'RESULTS-ONLY', 'NOT ELITE'], default='NOT GRADED')
    g['thin'] = g.n < spec.pop_floor
    g['pop_member'] = pop_mask
    return g


# ---- AF-4 -------------------------------------------------------------------
def weight_sensitivity(g: pd.DataFrame, ids_mask, weights=(0.0, 0.25, 0.5, 0.75, 1.0),
                       key=('game_year', 'pitcher')) -> pd.DataFrame:
    """AF-4 `weight_sensitivity` (NEW-UC47, provisional) — the G9 control.

    A composite needs weights, and weights are a knob. Rather than hide the
    knob, re-rank the subjects at every weight on the shape axis and publish
    the ranks side by side. If the #1 changes hands, the report must say
    "best" depends on what you value — and name who wins under each view."""
    sub = g[ids_mask & g.shape_score.notna() & g.results_score.notna()].copy()
    for w in weights:
        sub[f'rank_w{w:.2f}'] = (w * sub.shape_score + (1 - w) * sub.results_score).rank(
            ascending=False, method='min').astype(int)
    return sub


# ---- AF-5 -------------------------------------------------------------------
def elite_share(staff: pd.DataFrame, flag='ff_elite_archetype_flag') -> dict:
    """AF-5 `elite_ff_share` (NEW-UC47, provisional).

    Of every four-seam the staff's right-handers threw, what share came from
    an arm whose four-seam is flagged elite?
        EFS = sum(n where flag) / sum(n)
    Grain: one staff-season. Denominator includes ungraded and THIN arms —
    an arm too thin to grade is, by construction, not elite."""
    T = float(staff.n.sum())
    E = float(staff.loc[staff[flag].fillna(False).astype(bool), 'n'].sum())
    return dict(flag=flag, elite_ff=E, total_ff=T, share=E / T if T else np.nan)


# ---- AF-6 -------------------------------------------------------------------
def needle_swap(cands: pd.DataFrame, staff: pd.DataFrame, spec: ArchetypeSpec) -> pd.DataFrame:
    """AF-6 `needle_swap` (NEW-UC47, provisional) — "who would move the needle".

    Aspirational by DPO decision 12: no availability, no contracts.
    For each candidate of role r in {SP, RP}:
      V_r  = median four-seam volume of this staff's graded arms of role r
             (the four-seams a typical Phillies SP / RP throws in a season)
      d_r  = the staff arm of role r with the LOWEST efc_score (the ledger's
             marginal four-seam — an accounting device, not a roster verdict)
      Δ composite = V_r * (efc_c - efc_d) / T          (staff four-seam-weighted
                                                        score, grade points)
      Δ EFS       = V_r * (elite_c - elite_d) / T
    T = total staff RHP four-seams. The candidate's own observed volume is NOT
    used: in a partial-coverage frame it measures our sampling, not his role.
    Candidates with role UNK are scored at the RP volume and flagged."""
    T = float(staff.n.sum())
    G = staff[staff.efc_score.notna()]
    out = []
    for _, c in cands.iterrows():
        r = c.role if c.role in ('SP', 'RP') else 'RP'
        pool = G[G.role == r]
        if pool.empty:
            continue
        V = float(pool[pool.n >= spec.pop_floor].n.median()) if (pool.n >= spec.pop_floor).any() else float(pool.n.median())
        d = pool.sort_values('efc_score').iloc[0]
        dc = V * (c.efc_score - d.efc_score) / T
        de = V * (float(bool(c.ff_elite_archetype_flag)) - float(bool(d.ff_elite_archetype_flag))) / T
        out.append(dict(game_year=c.game_year, pitcher=c.pitcher, role=c.role, role_used=r,
                        V_role=V, displaced_pitcher=d.pitcher, displaced_efc=d.efc_score,
                        cand_efc=c.efc_score, delta_staff_score=dc, delta_efs=de))
    return pd.DataFrame(out)
