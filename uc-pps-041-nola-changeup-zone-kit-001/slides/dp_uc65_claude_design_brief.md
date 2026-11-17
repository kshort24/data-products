# Claude Design brief · UC #65 · Aaron Nola | 2026 | The changeup, in the zone

**What to build:** a 35–45 s animated closer (16:9, 1920×1080, dark) that appends to the client's video of Nola's 28 changeups taken for strikes in zones 7–9.
Five scenes in `slide_content.md`: handoff → pitch map (hero) → count board → cards → outro. Reference PNGs in `ref/` pass the house visual standard (V1–V7) and are the static fallback.

## Non-negotiables
1. **Numbers come from `copy_registry.json` or `data/` only.** If a number is not there, it does not go on screen.
2. **The 28 are the video.** Exactly the rows of `data/dp_uc65_cz1_28.csv`; never add or drop one. Land them in `video_order`.
3. **Baseball-true circles.** Diameter 0.242 ft in plate coordinates (2.9 in). Equal x/y scale. Catcher's view (`plate_x` as recorded; keep x as plotted in the reference).
4. **Use `plate_z_n` for height on the hero map** (scaled to each hitter's zone, drawn on a 1.5–3.5 ft zone). Raw `plate_z` is the alternate only.
5. **Context before highlight.** Gray first, red last, on every visual. No connected lines between seasons; no stacked bars; axis labels stay visible.
6. **No logos, photos, likenesses or team marks.** Type, shapes and data marks only.

## Data dictionary
- `pitchmap_2026.csv`: one row per 2026 MLB changeup (489). `plate_x` ft (catcher's view), `plate_z` ft, `plate_z_n` zone-scaled height, `sz_bot`/`sz_top`, `zone` (Statcast 1–14), `count`, `stand`, `cz1` (True = in the video), `release_speed` mph.
- `cz1_28.csv`: the 28, with `video_order`, `game_date`, `opp`, `count`, `zone`, coordinates, `ball_r_n` (ball radius in zone-scaled units).
- `ch_usage_by_year.csv`: changeup share by season × side; `metric` = `ch_usage_all` or `ec1_ch_usage_0-0_1-1`.
- `ts1_two_strike_groups.csv`: two-strike pitch-group shares by season × side.
- `zn1_location_by_year*.csv`: in-zone / bottom-third / below-zone shares, bottom-third take rate, called strikes in 7–9.
- `fp1_first_pitch.csv`: first-pitch changeup share and strike rate by season × side.
- `ch_pool.csv`: Phillies starter seasons since 2015 (≥ 2,000 pitches, ≥ 100 changeups) — the gray context.

## Palette
Background #0b1220 · panel #111a2c · ink #eef2f8 · muted #9aa6ba · **red #E81828 (the 28 / Nola 2026)** · gray #8a94a6 (context) · gold #f2c14e (two-strike series on card B only).
