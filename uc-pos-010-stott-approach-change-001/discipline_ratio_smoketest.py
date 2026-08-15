"""
discipline_ratio_smoketest.py — synthetic-data smoke test for AP-9 / AP-10
==========================================================================
Use case : uc-pos-010-stott-approach-change-001
Purpose  : prove the LOGIC of `discipline_ratio` and `walks_between_ks` without
           the parquet layer. The MLB repo is not reachable from the governance
           plane, so this is the same pattern used for `marsh_xbh_animated.py`
           — smoke-tested against a synthetic frame here, run against live `pos`
           in the Jupyter env.

This is NOT the verification script. Per house pattern, `dp_uc33_verification.py`
must recompute every shipped headline from inline masks against the real parquet,
with no import of the build's KPI kernel. This file only asserts that the kernel
behaves as specified.

Run:  python discipline_ratio_smoketest.py     (exits non-zero on any failure)
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from discipline_ratio import discipline_ratio, walks_between_ks

LEVEL = ['player_name', 'game_year']
_fail = []


def ok(label: str, cond: bool, got=None, want=None) -> None:
    print(f"{'PASS' if cond else 'FAIL'}  {label}"
          + ('' if cond else f"   got={got!r} want={want!r}"))
    if not cond:
        _fail.append(label)


def _log() -> pd.DataFrame:
    """Synthetic terminal-PA log.

    Stott      : 14 straight walks, one strikeout, then 2 more walks + 2 outs.
    Control    : walks and strikeouts perfectly INTERLEAVED — constructed so the
                 ratio and the run length tell different stories.
    Plus two non-PA rows that the governed PA definition must exclude.
    """
    rows = []

    def pa(p, d, pk, ab, ev):
        rows.append(dict(player_name=p, game_year=2026, game_date=d,
                         game_pk=pk, at_bat_number=ab, events=ev))

    for i, e in enumerate(['walk'] * 14 + ['strikeout']
                          + ['walk', 'walk', 'single', 'field_out']):
        pa('Stott, Bryson', f'2026-08-{1 + i // 4:02d}', 700 + i // 4, i, e)

    for i, e in enumerate(['walk', 'strikeout'] * 4 + ['single', 'field_out']):
        pa('Control, Guy', f'2026-08-{1 + i // 4:02d}', 800 + i // 4, i, e)

    # must be excluded by _pa_frame
    pa('Stott, Bryson', '2026-08-01', 700, 98, 'pickoff_1b')
    pa('Stott, Bryson', '2026-08-01', 700, 99, np.nan)

    return pd.DataFrame(rows)


df = _log()

# ── 1. PA definition and count-based arithmetic ──────────────────────────────
r = discipline_ratio(LEVEL, df)
s = r[r.player_name == 'Stott, Bryson'].iloc[0]

ok("PA excludes NaN events and pickoff_1b", s.plate_apps == 19, s.plate_apps, 19)
ok("walks counted from BB_EV", s.walks == 16, s.walks, 16)
ok("strikeouts counted from K_EV", s.strikeouts == 1, s.strikeouts, 1)
ok("bb_per_k computed from counts", abs(s.bb_per_k - 16.0) < 1e-9, s.bb_per_k, 16.0)
ok("denominators ship with rates (RC-3)",
   {'plate_apps', 'walks', 'strikeouts'} <= set(r.columns))
ok("no rounding applied in the curated frame",
   abs(s.bbrate - 16 / 19) < 1e-12, s.bbrate, 16 / 19)

# counts cancel: (BB/PA)/(K/PA) == BB/K, when nothing is rounded first
ok("bbrate/krate == bb_per_k exactly (unrounded)",
   abs((s.bbrate / s.krate) - s.bb_per_k) < 1e-9)

# ── 2. THE case — the zero-strikeout window the use case is about ────────────
kfree = df[(df.player_name == 'Stott, Bryson') & (df.events == 'walk')].head(14)
z = discipline_ratio(LEVEL, kfree).iloc[0]

ok("K == 0 -> k_free flag set", bool(z.k_free))
ok("K == 0 -> bb_per_k is NaN, NOT inf", pd.isna(z.bb_per_k), z.bb_per_k, np.nan)
ok("K == 0 -> raw counts still renderable as '14 BB / 0 K'",
   (z.walks, z.strikeouts) == (14, 0), (z.walks, z.strikeouts), (14, 0))
ok("K == 0 -> bb_minus_k remains defined",
   (not pd.isna(z.bb_minus_k)) and abs(z.bb_minus_k - 1.0) < 1e-9, z.bb_minus_k, 1.0)

# ── 3. AP-10 — the statistic the video title actually claims ─────────────────
w = walks_between_ks(LEVEL, df)
st = w[w.player_name == 'Stott, Bryson'].iloc[0]
ct = w[w.player_name == 'Control, Guy'].iloc[0]

ok("max_bb_run == 14 (matches the video title)", st.max_bb_run == 14, st.max_bb_run, 14)
ok("open run after the last K is tracked separately",
   st.current_bb_run == 2, st.current_bb_run, 2)
ok("run endpoints reported", st.run_start_date is not None and st.run_end_date is not None)

# the headline finding: interleaving destroys the run while leaving BB/K intact
ct_ratio = r[r.player_name == 'Control, Guy'].iloc[0].bb_per_k
ok("interleaved hitter posts a real BB/K (1.0) but a max run of 1",
   ct.max_bb_run == 1 and abs(ct_ratio - 1.0) < 1e-9,
   (ct.max_bb_run, ct_ratio), (1, 1.0))
ok("=> streak and ratio are NOT interchangeable (B-14)",
   ct.max_bb_run != st.max_bb_run)

# ── 4. ordering is load-bearing for AP-10 ───────────────────────────────────
shuffled = df.sample(frac=1.0, random_state=0)
ok("walks_between_ks is order-independent at the INPUT (sorts internally)",
   walks_between_ks(LEVEL, shuffled)
   .set_index('player_name').loc['Stott, Bryson', 'max_bb_run'] == 14)

print()
if _fail:
    print(f"{len(_fail)} FAILED: {_fail}")
    sys.exit(1)
print(f"All {len(_fail) or 'checks'} passed — logic conforms to the AP-9 / AP-10 spec.")
print("NOTE: this proves logic only. Run dp_uc33_verification.py against live `pos` "
      "before any number reaches a report.")
