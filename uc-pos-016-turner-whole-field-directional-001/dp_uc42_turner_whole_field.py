"""
dp_uc42_turner_whole_field.py — the build.
Reproduces the whole-field directional-tendency analysis and writes every
receipt into out/. Run on the data plane (needs pyarrow — Kellen's `snakes`
conda env has it; this cloud-container build session did not, see
04_engineering_build.md environment notes, and read the parquet files via a
pure-Python fallback reader instead).

Usage:
    DP_UC42_DATA="C:/Users/Kellen/OneDrive/Documents/Python Scripts/MLB" python dp_uc42_turner_whole_field.py
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from dp_uc42_kernel import (
    load_turner_pos, build_bip_frame, directional_rate_table,
    pooled_two_prop_z, sort_rank, P_THROWS_COLORS, MARKER_SIZE, AS_OF,
)

OUT = 'out'
os.makedirs(OUT, exist_ok=True)


def main():
    pos = load_turner_pos()
    pos_rs = pos[pos.game_type == 'R'].copy()   # regular season only, cross-year comparability
    bip = build_bip_frame(pos_rs)
    bip.to_csv(f'{OUT}/dp_uc42_turner_bip_extract.csv', index=False)

    tabs = [
        directional_rate_table(bip[bip.ooz], 'outside'),
        directional_rate_table(bip[~bip.ooz], 'in_zone'),
        directional_rate_table(bip, 'all'),
    ]
    full = pd.concat(tabs, ignore_index=True).sort_values(['zone', 'game_year'])
    full.to_csv(f'{OUT}/dp_uc42_kpi_directional_by_zone_year.csv', index=False)

    # significance tests: 2026 vs pooled 2023-2025, outside- and in-zone
    sig_rows = []
    for zone_label, mask in [('outside', bip.ooz), ('in_zone', ~bip.ooz)]:
        base = bip[mask & bip.game_year.isin([2023, 2024, 2025])]
        cur = bip[mask & (bip.game_year == 2026)]
        for metric, col in [('pull', 'Pull'), ('oppo', 'Oppo'), ('straightaway', 'Straightaway')]:
            x1, n1 = (cur.hit_direction == col).sum(), len(cur)
            x2, n2 = (base.hit_direction == col).sum(), len(base)
            z, diff = pooled_two_prop_z(x1, n1, x2, n2)
            sig_rows.append(dict(zone=zone_label, metric=metric,
                                  rate_2026=x1 / n1, n_2026=n1,
                                  rate_2023_25=x2 / n2, n_2023_25=n2,
                                  diff=diff, z=z))
    sig = pd.DataFrame(sig_rows)
    sig.to_csv(f'{OUT}/dp_uc42_significance_2026_vs_pooled.csv', index=False)

    ooz_share = bip.groupby('game_year').ooz.mean().reset_index()
    ooz_share.columns = ['game_year', 'ooz_share_of_bip']
    ooz_share.to_csv(f'{OUT}/dp_uc42_ooz_share_by_year.csv', index=False)

    # ---- Fig 1: facet grid ----
    col_order = (bip[['hit_direction', 'sort_rank']].drop_duplicates()
                 .sort_values('sort_rank').hit_direction.tolist())
    years = sorted(bip.game_year.unique())
    fig, axes = plt.subplots(len(years), len(col_order), figsize=(11, 13), sharex=True, sharey=True)
    fig.patch.set_facecolor('white')
    for ri, yr in enumerate(years):
        for ci, hd in enumerate(col_order):
            ax = axes[ri, ci]
            panel = bip[(bip.game_year == yr) & (bip.hit_direction == hd)]
            for throws, color in P_THROWS_COLORS.items():
                sub = panel[panel.p_throws == throws]
                iz, ooz = sub[~sub.ooz], sub[sub.ooz]
                ax.scatter(iz.loc_x, iz.loc_y, s=MARKER_SIZE, c=color, alpha=0.75, edgecolors='none')
                ax.scatter(ooz.loc_x, ooz.loc_y, s=MARKER_SIZE, c=color, alpha=0.85,
                           edgecolors='black', linewidths=0.6)
            ax.set_xlim(-350, 350); ax.set_ylim(-20, 420); ax.set_aspect('equal')
            ax.axhline(0, color='#cccccc', lw=0.5, zorder=0)
            if ri == 0:
                ax.set_title(hd, fontsize=11, fontweight='bold', color='#002D72')
            if ci == 0:
                ax.set_ylabel(f'{yr}\n(n={len(bip[bip.game_year==yr])})', fontsize=10, fontweight='bold')
            ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle('Trea Turner — Whole-Field Directional Tendency, Balls in Play by Season',
                 fontsize=14, fontweight='bold', color='#002D72', y=0.995)
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    plt.savefig(f'{OUT}/dp_uc42_fig1_facet_grid.png', dpi=170, facecolor='white')
    plt.close(fig)

    print('Build complete.')
    print(full.to_string(index=False))
    print(sig.to_string(index=False))
    return bip, full, sig


if __name__ == '__main__':
    main()
