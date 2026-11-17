# 05 · Quality & Certification

## DQ scorecard: 5 PASS / 0 WARN / 0 FAIL (2 INFO)
| Check | Result | Evidence |
|---|---|---|
| entity_lock_O26 | PASS | 31077 rows |
| DV-1 spring changeups excluded from map | INFO | 13 S rows; map n = 489 |
| REC-CLIP CZ-1 (client frame) == clips on disk | PASS | 28 vs 28 |
| REC-CLIP map highlight == client highlight | PASS | 28 vs 28 |
| CZ-1 zone + sz fields complete | PASS | nan |
| PNZ-1 + BB-1: every CZ-1 ball touches the drawn bottom third | PASS | 1.000 of 28 (centers inside: 0.714; Statcast zones count a ball that clips the edge) |
| raw plate_z vs mean zone (client form) - share of CZ-1 inside the drawn bottom third | INFO | 0.679 |

## Independent harness: 20/20 PASS
| ID | Check | Independent | Registry | Result |
|---|---|---|---|---|
| V01 | highlight count = 28 clips | 28 | 28 | PASS |
| V02 | s1.split | 27 regular season + 1 Wild Card | 27 regular season + 1 Wild Card | PASS |
| V03 | s2.population | 489 MLB changeups in 2026 · 28 in the video | 489 MLB changeups in 2026 · 28 in the video | PASS |
| V04 | s2.lhb | vs LHB · 25 of the 28 | vs LHB · 25 of the 28 | PASS |
| V05 | s2.velo | 86.0 mph average | 86.0 mph average | PASS |
| V06 | s2.edge (centered below sz_bot) | 8 of the 28 are centered just below the line — the ball only has to clip the zone | 8 of the 28 are centered just below the line — the ball only has to clip the zone | PASS |
| V07 | every one of the 28 is within one ball radius of the zone bottom or above it | 1 | 1 | PASS |
| V08 | no two-strike count among the 28 | 0 | 0 | PASS |
| V09 | s3.first | 9 on the first pitch | 9 on the first pitch | PASS |
| V10 | s3.behind | 15 with Nola behind in the count | 15 with Nola behind in the count | PASS |
| V11 | card_a.stat (EC-1) | 23.1% | 23.1% | PASS |
| V12 | card_b.stat (TS-1 offspeed = CH for Nola) | 13.0% | 13.0% | PASS |
| V13 | card_c.stat (below zone) | 48% | 48% | PASS |
| V14 | card_c.take value | 23% | 23% | PASS |
| V15 | card_d.stat (FP-1 share) | 22.1% | 22.1% | PASS |
| V16 | card_d.strike value | 40% | 40% | PASS |
| V17 | card_d career-low claim | 2026 | 2026 | PASS |
| V18 | kit manifest sha256 all match | 0 | 0 | PASS |
| V19 | every registered string appears in slide_content.md | 33 | 33 | PASS |
| V20 | visual audit all PASS / N-A | 1 | 1 | PASS |

## Visual audit (V1–V7)
| Figure | V1 | V2 | V3 | V4 | V5 | V6 | V7 |
|---|---|---|---|---|---|---|---|
| r1_pitch_map | PASS | PASS | N-A | N-A | PASS | PASS | PASS |
| r2_pitch_map_raw | PASS | PASS | N-A | N-A | PASS | PASS | PASS |
| r3_count_board | PASS | PASS | N-A | N-A | PASS | PASS | PASS |
| r4_early_count | PASS | PASS | N-A | N-A | PASS | PASS | PASS |
| r5_early_vs_late | PASS | PASS | N-A | N-A | PASS | PASS | PASS |
| r6_first_pitch | PASS | PASS | N-A | N-A | PASS | PASS | PASS |

## Code pins (sha256)
| File | sha256 |
|---|---|
| `dp_uc65_build_figs.py` | `41d4bcc83f8e6ed77d4c4fd03cd4e7e528dc421ea4f1c87d2c8e47e74a6c4762` |
| `dp_uc65_build_kit.py` | `5a9423b52a9b53927f611e042c538af250f7b9e9689aff356a1d8981afcdbc19` |
| `dp_uc65_kernel.py` | `038b5d568f23ae340c990fdf0eed4e3e5727fd9fa94cc5f1fa2357932fda7ae6` |
| `dp_uc65_nola_changeup.py` | `a7102bd45b52ef80e15652b08cf59af6df89eab8d48429e8f47cfa7f2ab3b8b6` |
| `dp_uc65_verification.py` | `cea9e3e7358adaa7444caffe83324b6d629e05009152fde1cd73f36c5208aaeb` |

## Verdict: **READY-CONDITIONAL**
- **C1** DPO confirms clip order (or edits `video_order`).
- **C2** DPO ratifies the provisional KPIs and DV-1.
- **C3** Claude Design keeps to `copy_registry.json` (any new on-screen number comes back through the org first).
