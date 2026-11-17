# Client prompt — 2026-11-16 22:33 ET (verbatim) + intake Q&A

> Let's get back to a good ole fashioned data product build against a use case from my Baseball repository. This time, I want to complete a 2026 season analysis of Aaron Nola. I have several data products that were already built examining Nola's performance at various points throughout the year, so definitely leverage the work already done on those. Don't necessarily tie out any narratives, but consider the holistic arc throughout the season when constructing an analysis of his performance altogether. Follow the relevant skills and similar recap reports that have been leveraged for additional context.
>
> One aspect that I would like to see explored, I have done very little analysis of this on my own, is his pitch sequencing. I have the following python code in my Baseball Functions that produces a pitch sequence.
>
> ```python
> def pitch_sequence(df):
>     seqs = df.sort_values(by=['game_date'
>                               ,'game_pk'
>                               ,'at_bat_number'
>                               ,'pitch_number'
>                              ]
>                          ).groupby(['game_pk','at_bat_number'],as_index=False).agg(seq = ('pitch_type',lambda x: '-'.join(x.astype('str'))))
>     return df.merge(seqs, on = ['game_pk','at_bat_number'])
> ```
>
> I am curious to see how he sequences against left- and right-handed batters. I want to know which sequences are effective at getting outs, strikeouts, and/or inducing weak contact i.e., the sequences that maximize run prevention. A few extra angles to potentially explore could be how his sequencing differs between batterymates (maybe this was done previously?) and how it has differed over time (e.g., he used to rely on a sequence in his younger years that has not produced the same level of success the last couple years).
>
> A potentially tricky thing to navigate will be the length of the sequence. This could vary from two pitches (i.e., he follows a four-seam fastball (FF) with a curveball (CU that turned into a knuckle curve KC later in his career). all the way up to three-pitch or four-pitch sequences. Those might need to be identified within longer sequences though. It could potentially open up a large can of worms, so don't be afraid to spend some time exploring that and asking questions to me where appropriate.
>
> [standard agentic-org prompt: MLB repo = data plane; receipts 00_–07_ in a data-products subfolder; scouting-report skill for inspiration; bid framed as a competitive RFP response, treated as won; PDF report + fully governed package; interactive dashboard if sensible; other outputs at the org's discretion]

## Intake Q&A (AskUserQuestion, 2026-11-16 ≈22:39 ET) — DPO rulings, binding on the build

| # | Question | Client answer | Becomes |
|---|---|---|---|
| Q-A | How should a sequence get credit for an outcome? | **Lift + endings** — count-adjusted setup lift scored on the follow-up pitch leads; terminal endings (last 2–3 pitches of the PA scored on out / K / weak contact) as the readable view | SQ-2 (headline), SQ-3 (endings) |
| Q-B | Definition of "weak contact" (no house glossary term existed) | **Savant launch_speed_angle 1–3** (Weak / Topped / Under); report xwOBAcon alongside | glossary term **PC-1 poor contact** (DPO-defined, not inferred) |
| Q-C | Sequence length / window scoping | **Career-wide everything** — pool all seasons for every length; 2026 shown as a highlight | pool = Nola regular season 2015–2026, all k ∈ {2,3,4} |

T0 facts shown to the client with the questions: 746 PA in 2026 (458 LHB / 288 RHB); 2,209 within-PA pitch pairs in 2026; 'FF-KC' to LHB the top 2026 pair (131); 16 LHB / 8 RHB pairs and 2 triples per side with ≥ 30 occurrences in 2026; curveball tagged CU 2015–16 and KC 2017+.
