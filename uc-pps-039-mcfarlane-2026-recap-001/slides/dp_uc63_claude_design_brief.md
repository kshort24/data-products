# Claude Design brief · UC #63 · Alex McFarlane | 2026 | Nasty Stuff, Outlier Heater

**What to build:** a 13-slide animated deck from `slide_content.md`. The slide copy is the client's own narrative; the animation is the
supplement. Reference PNGs in `ref/` pass the house visual standard (V1–V7) and are the static fallback for every animated chart.

## Non-negotiables
1. **Numbers come from `copy_registry.json` or `data/` only.** If a number is not there, it does not go on a slide.
2. **Keep the client's words.** Change nothing in the commentary except layout; keep every † (registered corrections: 'out of Central Florida' → 'out of South Florida', 'Elite Walks Rate (2%)' → 'Elite Walks Rate (2.6%)', '(41% HH, 9% Barrel)' → '(41.9% HH, 9.7% Barrel)', 'run about a foot' → 'run about 9 inches', '(2% BB Rate.)' → '(2.6% BB Rate)').
3. **Context before highlight.** Gray context draws first; McFarlane (red) lands last on every chart.
4. **No connected lines between outings or seasons** (discrete observations). No stacked bars. Axis titles with units stay visible.
5. **AAA is a muted, separate block.** Never add AAA pitches to the 333.
6. **No logos, photos, or likenesses.** Type, shapes, and data marks only.
7. **Small sample label** on slides 6–9: "85 PA · directional".

## Data dictionary (most-used columns)
- `pitches.csv`: one row per MLB pitch (333). `hb_in` / `ivb_in` = horizontal / induced vertical break in inches (catcher's view; arm side negative for this RHP); `plate_x` / `plate_z` feet; `stand` batter side.
- `pitch_map_mix.csv`: the client's `lhb_pitch_mix` / `rhb_pitch_mix` (usage %, mean location) — bubble positions and sizes for slide 8.
- `outing_ledger.csv`: one row per outing; `entry_lead` = Phillies lead at his first pitch; `bd1_bridge` = bridge to Duran; `velo_ff` mean four-seam mph.
- `fo1_pool.csv`: righty four-seam pitcher-seasons in Phillies games (≥ 100 FF); `fo1_pitch_sample.csv` = random 20,000 of the 137,203 pitches (seed 63).
- `s1_twins.csv`: first-21-outing lines for McFarlane and Kerkering.

## Palette
Red #E81828 (McFarlane) · navy #002D72 (Kerkering, structure) · gray #9AA3AF (context) · pitch colors = house `PITCH_COLORS` (4-Seam #D22D49, Sinker #FE9D00, Slider #EEE716, Sweeper #DDB33A).
