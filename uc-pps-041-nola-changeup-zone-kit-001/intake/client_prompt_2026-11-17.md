# Client prompt — 2026-11-17 16:53 ET (attachment `Aaron Nola Pitch Sequencing`, verbatim prose; code kept in full below)

> Delegating the sequencing build to my agentic data product organization and feel the output was fine. I wanted to take a deeper dive into his changeup specifically so then I did some of this myself.
>
> I am going to hand this off to the same prompt and ask for some analysis and prepared figures to be animated by Claude Design. This animation will append to the end of a video of all the called strikes on Nola's changeup in the bottom three sections of the strike zone in 2026. I definitely want to see the pitch map where I can see the home-plate view of all his changeups along with a highlight of the changeups that are in the video (called strikes in zone 7/8/9). I also want to see a few cards/notes highlighting things about his changeup whether it is some of the KPIs that I listed (e.g., usage to get ahead early in the count against LHB) or other relevant KPIs. It is a video about Aaron Nola throwing his changeup in the strike zone, I want to include an analytical visual to supplement the video that I am showing.

Chat line: "Consider the attached prompt and build the accompanying visuals that I will add to the data-products folder then share in a separate prompt to Claude Design."
Standing prompt (from UC #64): MLB repo = data plane; receipts 00–07 here; scouting-report skill for voice; bid framed as a competitive RFP, treated as won.

## Client code (notebook, as attached)
- `pn = 'Nola, Aaron'; df = nola = pps[pps.player_name == pn]; df = pitch_sequence(nola)` — the client frame (CF-M: Phillies pitching role, ALL game types).
- `#concat_mp4s_in_folder('Aaron Nola landing his changeup at the bottom of the strike zone',7)` — video folder; 7 = clip trim seconds.
- Comment: "Stubbs called for fewer back-to-back FF to LHB from Nola than JT" (carried from UC #64 §10).
- Table 1: `nresults` + `putaway_rate` at `[player_name, game_year, p_throws, stand]`, LHB rows (pitches, PA, BA, wOBA, K%, BB%, putaway).
- Figure 1/2: two-strike usage by `pitch_group` by year and stand (`lhb_pitch_mix` / `rhb_pitch_mix` on `strikes == 2`, summed by group).
- Figure 3: 2026 changeups, `plate_x` × `plate_z`, colored "Called Strike at Bottom of Zone" (`description == 'called_strike'` & `zone in 7/8/9`) vs "Other Changeups", faceted by stand, sized by `release_speed` ("Make this to be consistent for the size of a baseball"), zone rect x ±0.83, y = mean `sz_bot` / `sz_top`.
- Table 2: CH vs LHB by year — usage in even counts before two strikes (`balls == strikes & strikes < 2`) with `putaway_rate`, `whiff_rate`, `chase_rate`, `in_zone_rate` (all-count).

## T0 facts (computed this session, before the bid)
- Video folder (read-only access granted 2026-11-17): **28 raw clips** (a1–a9, b1–b9, c1–c9, d1) + 28 normalized copies + the concatenated video.
- Client definition on the client frame, 2026: **28 changeup called strikes in zones 7/8/9 = 27 regular season + 1 Wild Card (10/01)**, 25 vs LHB / 3 vs RHB; 0 in spring training. **Matches the clip count.**
- 2026 changeups in the client frame: 502 = 481 R + 8 F (Wild Card) + **13 S (spring training)**.
