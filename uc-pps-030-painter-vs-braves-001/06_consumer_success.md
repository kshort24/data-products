# 06 · Consumer Success — `uc-pps-030-painter-vs-braves-001`

**UC #44 · `uc-pps-030` · `dp_uc44`** · Consumer Success department
Agents: `consumer-onboarding-agent`, `analytics-enabler`, `query-builder`

---

## Primary persona — Kellen, as requester and analytics owner

**What you asked for and where it is:** the index card is `out/dp_uc44_fig1_notecard.png` and page 2 of the
PDF. It is your layout — maps by stand on the left with a one-stat callout each, pitch rail on the right — with
your three descriptions carried through into the pitch names on the rail.

**Read this first:** your splitter line. It is arithmetically perfect and it describes a pitch that has not
been thrown since 17 June. That single fact reorganises the rest of the card, and it is why the package spent
its budget on the arsenal-turnover question rather than on prettier maps.

**The twist you proposed works, and it has a bill attached.** The 20-80 scale is a z-score, so proposing it
committed the shop to declaring a population and testing the normality it assumes. Both are done: SG-2 is a
reusable population constructor, and the normality test **failed on three of twelve populations** — which is
in the report body, not a footnote, because a KPI that hides its own assumption failing is worse than no KPI.
The grades did not move as a result, and the report says that too.

**Two things you will want to argue with:**
1. The grading window is the option date, not your 2026-07-21 cut. Your cut partitions the season identically
   — your numbers reproduce exactly — but a boundary should name its cause. `02` §design change.
2. The arsenal grades 50. That is *average against the arms the Phillies actually see*, and it is up from 45.
   If you want a league-relative number, that is a different population and a different UC.

## Secondary personas (not the requester — read this if the package travels)

| Persona | What they need | Where |
|---|---|---|
| **Catcher** | The single attack rule, and nothing else before first pitch | Report §6, "The single attack rule" |
| **Pitching coach** | The four-seam trade, and why the pitch count is the design rather than a warning | Report §4 + the efficiency table |
| **Manager** | How deep the start goes, and why | Report §7 item 4: plan for six innings, not seven |
| **Pitching analyst** | The population definition, the floors, and the normality test | `03` §2, `out/dp_uc44_benchmark_population_moments.csv` |
| **Painter** | One sentence: the changeup is his best pitch against both sides and he is under-throwing it to right-handers | Report §6, "What each side gets" |

## How to read the deliverables

| If you want | Open | Time |
|---|---|---|
| the card | `out/dp_uc44_fig1_notecard.png` | 30 seconds |
| the argument | `dp_uc44_painter_vs_braves_report.pdf` | 12 minutes |
| to interrogate it by side and window | `dp_uc44_painter_scouting_card.html` | as long as you like |
| what the organization decided and why | `00_dpo_orchestration_record.md` | 6 minutes |
| the six conditions on certification | `05_quality_certification.md` §5 | 1 minute |
| the KPI specs, before reusing them | `03_governance.md` §2 | 8 minutes |
| every number behind every table | `out/*.csv` | — |

**Reading order for a coach who has ten minutes:** the card, then the report's Bottom Line (five numbered
findings), then §6 "The single attack rule", then stop.

## Using the dashboard

Three controls, and they compose:

- **Window** — Pre-Option / Post-Option / Full 2026. Flip between the first two to see the splitter leave and
  the changeup arrive. This is the finding, made physical.
- **Side** — Both / vs LHH / vs RHH. Select **vs LHH** and look at the sweeper row: 65% in the zone, 20% whiff,
  .523 xwOBA on 9 PA. That is the leak, and it is invisible in the "Both" view.
- **Pitch type** — six toggles. Turn everything off except CH to see how differently he uses it by side.

**What it deliberately will not do:** when you filter to one side, the grade columns go blank. A by-stand cell
is 7–131 pitches; regrading on that silently would be the fastest way to misuse this KPI family, so the card
refuses and says why in the note under the rail. The numbers *above* the grades are the split; the grades are
the pitch.

## Worked example — re-running this for a different pitcher

```python
import dp_uc44_kernel as K

# 1. Change the subject. MLBAM id only — never a name filter.
SUBJECT = 554430                      # e.g. Wheeler
allp = K.load_phils(tuple(range(2015, 2027)))
subj = allp[(allp.phillies_role=='pitching') & (allp.pitcher==SUBJECT) & (allp.game_year==2026)]

# 2. Choose a window boundary that has a CAUSE. An injury, an option, a mechanical change.
#    If there is no cause, use the whole season and say so.
WINDOW = subj[subj.game_date >= '<date-with-a-reason>']

# 3. Grade. The population is handedness-specific — pass his hand, not the subject's opponent's.
for pt in WINDOW.pitch_type.value_counts().index:
    pop = K.benchmark_population(allp, pt, throws=subj.p_throws.iloc[0])
    d   = WINDOW[WINDOW.pitch_type == pt]
    if len(d) < K.SUBJECT_PITCH_FLOOR:          # the floor is not advisory
        continue
    sw, wh = d.description.isin(K.SWINGS).sum(), d.description.isin(K.WHIFFS).sum()
    stuff = K.scouting_grade(wh/sw, pop.whiff_rate) if sw >= K.SUBJECT_SWING_FLOOR else {'grade': float('nan')}
    cmd   = K.scouting_grade((d.zone<=9).mean(), pop.in_zone_rate)
    print(pt, K.pitch_grade(stuff['grade'], cmd['grade']), pop.thin.iloc[0] and 'THIN' or '')

# 4. If the window boundary was a roster or health event, ALWAYS run AR-1 and its control.
turn = K.arsenal_turnover_index(before, after)
#    ...then check league tag share for the same months before calling it a pitcher decision.
```

## Persona action note

The one instruction that survives compression to a single sentence, for the battery:

> **Changeup, not sweeper, to the left-handed hitters.**

Everything else in this package is the argument for why.

## Reuse patterns worth carrying forward

1. **SG-1 / SG-2 are the general objects here.** They grade any pitcher, any pitch, any window, against a
   population you declare. The next uc-pps advance gets its scouting grades for free — and ratifies the family
   by using it.
2. **AR-1 before any head-to-head table.** If the index is over ~0.20, the history does not transfer and the
   table needs a warning in the same row, not a footnote.
3. **The tag-drift control.** Any claim that a pitcher changed his arsenal must be checked against league tag
   share for the same window. It costs one crosstab and it is the difference between a finding and an artefact.
4. **Reconstructing an opponent lineup with no opponent cache** — `groupby('batter')` over your own pitchers'
   rows in the head-to-head games, names by modal `des`-parse. Works for any club the Phillies have played.
5. **The blank-grade rule in the dashboard.** When a filter makes a cell too small to grade, blank the grade
   and say why. Copy this into any future card that carries a graded KPI.
