# 03 — Glossary Alignment & KPI Specs · uc-pos-005 (dp_uc22)

**Agent roles:** business-glossary-agent + kpi-calculator · **Verdict: PASS** — all user KPIs map to locked terms except the edge family; 4 NEW KPIs specified below (provisional OZ-1..OZ-4)

## User KPI list → glossary mapping
| User term | Locked term / status | Mechanics |
|---|---|---|
| barrel rate | Barrel% (locked, dp_uc18 kernel) | `launch_speed_angle == 6` on `type=='X'` |
| hard hit | Hard-Hit% (locked) | `launch_speed >= 95` on BIP |
| platoon splits | dimension, not KPI (locked pattern) | `p_throws` at any locked grain |
| pitch groups | PITCH_GROUP map (locked, dp_uc18) | fastball / breaking / offspeed |
| chase / takes / swings | locked discipline panel | SWINGS/WHIFFS lists, `zone <= 9` in-zone |
| slash / wOBA / K% / BB% etc. | locked get_stats kernel | inherited verbatim |
| **edge take / edge punish** | **NEW → OZ-1..OZ-4** | specs below |

## Attack-region geometry (shared input to OZ-1..OZ-4)
Per-pitch, using per-pitch `sz_top`/`sz_bot`; **ball_width = 0.25 ft is DPO-provided** (intake code), close to one baseball diameter (~0.24 ft). `HALF_X = 0.83` ft (Statcast plate half-width convention). Rows with null location excluded (10 rows; 05).

- `in_zone_geo`: `|plate_x| <= 0.83` AND `sz_bot <= plate_z <= sz_top`
- **shadow_in**: in zone AND within 0.25 ft of any edge — `(0.83 − |plate_x|) <= 0.25` OR `(plate_z − sz_bot) <= 0.25` OR `(sz_top − plate_z) <= 0.25`
- **shadow_out**: NOT in zone AND `|plate_x| <= 1.08` AND `sz_bot − 0.25 <= plate_z <= sz_top + 0.25`
- **heart**: in zone, not shadow_in · **waste**: everything beyond the band

Note: geometric in-zone agrees with Statcast `zone <= 9` on 95.5% of pitches (fixed vs per-pitch rails); both are retained — locked panel keeps `zone`, OZ family keeps geometry. Documented in 05; not a defect.

## OZ-1 — Shadow-Out Take Rate — PROVISIONAL
- **Plain language:** Of borderline pitches just OFF the plate (within one ball width outside the zone), how often does he lay off? "Taking his walks."
- **Formula:** `1 − mean(swing)` over shadow_out pitches; swing = locked SWINGS list.
- **Grain:** season (or any dim); **denominator floor:** 50 shadow_out pitches.

## OZ-2 — Shadow-In Attack Rate — PROVISIONAL
- **Plain language:** Of borderline pitches just ON the plate (within one ball width inside the zone edge), how often does he swing?
- **Formula:** `mean(swing)` over shadow_in pitches. Floor 50.
- **Interpretation guardrail:** lower is not worse — pair with OZ-4. A hitter may rationally decline low-value edge strikes early in counts.

## OZ-3 — Edge Decision Differential — PROVISIONAL
- **Plain language:** One number for edge judgment: swing rate on borderline strikes minus swing rate on borderline balls. Higher = sharper separation of ball from strike at the hardest margin.
- **Formula:** `OZ-2 − (1 − OZ-1)` = `swing_rate(shadow_in) − swing_rate(shadow_out)`.
- **Edge case:** can fall while judgment improves if the hitter cuts edge swings on both sides (2026 exhibits exactly this) — report must always present OZ-3 alongside OZ-1/2/4. Never headline OZ-3 alone.

## OZ-4 — Shadow-In Damage — PROVISIONAL
- **Plain language:** When he swings at the borderline strike and puts it in play, how hard is the punishment?
- **Formula:** on shadow_in BIP from swings: `xwOBAcon = mean(estimated_woba_using_speedangle)`, `barrel = mean(launch_speed_angle==6)`, `hard-hit = mean(launch_speed>=95)`.
- **Denominator floor:** 40 BIP for xwOBAcon at season grain; splits below the floor labeled small-sample in consumables (2026 platoon: 24 BIP vs LHP — labeled).

## Duplicate/conflict scan
UC8's locked pitcher-side **Edge Rate** (pitches to the edge, pitcher intent) is a different concept and different value stream — no conflict; naming kept distinct ("OZ", batter-side). No pos-side term covers edge discipline. **Recommend promotion to locked after DPO sign-off** — geometry is the DPO's own constant; damage mechanics are the locked kernel at region grain.
