# Layer 1 — Business Glossary, Data Domains & CDEs, Metadata Map
### UC-PPS-021

**Provenance discipline:** every term below is either **locked** (inherited verbatim from the UC8→UC11→UC15 line and the Baseball Functions library) or **inherited-approved** (the UC8 trio, already glossary-approved in `uc-pps-008`). Nothing is inferred. The one report-local term (`xwobacon`) is defined here and flagged for glossary promotion (O1), not invented (Business Glossary Agent guardrail).

---

## A. Business Glossary (term → CDE link → status)

| Term | Definition | CDE | Status / Source |
|---|---|---|---|
| Weighted On-Base Average (against) | `Σ(wBB·BB + wHBP·HBP + w1B·1B + w2B·2B + w3B·3B + wHR·HR) / PA`, season FanGraphs weights | `woba` | **locked** (`nresults`) |
| Strikeout / Walk / HR rate | K / BB / HR ÷ PA | `krate`,`bbrate`,`hr_rate` | **locked** (`nresults`) |
| Whiff Rate | swings-and-miss ÷ swings | `whiff_rate` | **locked** |
| Chase Rate | swings at `zone>9` ÷ pitches `zone>9` | `chase_rate` | **locked** |
| Put-away Rate | K ÷ pitches thrown in 2-strike counts | `putaway_rate` | **locked** |
| First-Pitch-Strike Rate | first pitches not called a ball ÷ first pitches | `first_pitch_strike_rate` | **locked** (`fpsr`) |
| Hard-Hit Rate | BIP with `launch_speed ≥ 95` ÷ BIP | `hard_hit_rate` | **locked** |
| **Edge Rate** | pitches within one baseball (0.245 ft) of the rulebook-zone perimeter ÷ located pitches | `edge_rate` | **inherited-approved** (UC8) |
| **OOZ Called-Strike Rate** | called strikes on `zone>9` pitches ÷ `zone>9` pitches (the "stolen strike") | `ooz_called_strike_rate` | **inherited-approved** (UC8) |
| **AIR / Ground-Ball Rate** | fly+line+pop ÷ BIP; ground ÷ BIP (`bb_type`) | `air_rate`,`gb_rate` | **inherited-approved** (UC8) |
| Chase-Up Rate | swings on pitches above `sz_top` ÷ pitches above `sz_top` | `chase_up_rate` | UC8 helper (observational) |
| **xwOBAcon** | mean `estimated_woba_using_speedangle` over BIP (`type=='X'`) — xwOBA **on contact** | `xwobacon` | **report-local → promotion candidate (O1)**; replaces contaminated pitch-level `get_stats.xwoba` |
| Computed IP | Σ terminal-event outs (EVENT_OUTS map) ÷ 3 | `ip_computed` | report-local (labeled) |

---

## B. Data Domains & Critical Data Elements

| Data Domain | CDE (physical) | Purpose in analysis |
|---|---|---|
| Pitch Profile | `pitch_name`, `release_speed`, `release_spin_rate`, `pfx_x/z` | Arsenal, usage, velo tracks, movement |
| Strike Zone | `plate_x`,`plate_z`,`sz_top`,`sz_bot`,`zone` | Edge rate, chase, location maps |
| Pitch Outcomes | `description`, `type` | Whiff, chase, BIP classification |
| At-Bat Outcomes | `events`, `stand`, `woba_value/denom` | Results, L/R splits, wOBA |
| Batted Ball Profile | `bb_type`, `launch_speed`, `launch_angle`, `estimated_woba_using_speedangle` | AIR/GB, hard-hit, xwOBAcon |
| wOBA Weights | `wBB,wHBP,w1B,w2B,w3B,wHR` | Season weights (load-applied) → wOBA |

---

## C. Semantic Mapping (Metadata Mapper output)

All KPI terms map **exact** to their physical/derived CDEs; no ambiguous or unmapped elements remain for DPO resolution.

| CDE | Physical / derived | Business Term | Mapping class |
|---|---|---|---|
| woba, krate, bbrate, hr_rate | derived (`nresults`) | wOBA / K% / BB% / HR-rate | exact |
| whiff_rate, chase_rate, putaway_rate, first_pitch_strike_rate, hard_hit_rate | derived (locked) | matching glossary terms | exact |
| edge_rate, ooz_called_strike_rate, air_rate, gb_rate | derived (UC8) | Edge / OOZ-CS / AIR / GB | exact |
| xwobacon | `estimated_woba_using_speedangle` on `type=='X'` | xwOBAcon | exact (promotion pending) |

**Glossary Agent verdict:** no new business meaning inferred. One promotion candidate (`xwobacon`) returned to the DPO (O1). The pitch-level `get_stats.xwoba` column is flagged **deprecated for xwOBAcon reporting**.
