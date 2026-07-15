# 06 — Consumer Success · uc-pos-marsh-breakout-001

## analytics-enabler — how to consume this product

Read `marsh_breakout_report.md` top to bottom; every table there is a rounded view of a CSV in `MLB/out/`. To slice further, load any CSV or re-run the script with a different out path. The "xwOBA" columns everywhere are the locked BIP-weighted proxy — do not quote them as Statcast xwOBA.

**Worked example:** *"Did Marsh really stop walking on purpose?"* → `marsh_breakout_discipline_by_season.csv`: zone_rate_seen flat (.466→.472) while swing_rate +12 pts and chase +14 pts → the walk collapse is hitter-initiated, not pitcher-initiated. Cross-check `_pa_funnel.csv`: fewer two-strike PA = fewer deep counts = fewer walk opportunities.

## consumer-onboarding-agent — persona guides (condensed)

**Hitting coach:** your KPIs are the discipline panel, first-pitch BIP quality, and pitch-group chase. The plan (attack early fastballs, pull-air intent) is working; the exposed flank is .446 chase vs breaking — build the 2H drill plan there. If opponents flip to spin-first sequencing, watch fp_swing_rate for whether he adjusts or keeps donating strike one.

**Manager:** the platoon removal is paying — vs-LHP SLG .413 and rising exposure share (27%). But vs-LHP whiff (36%) and expected numbers say keep leverage options behind him late in games vs elite LHP relievers. Rest days: July line (.194 in 40 PA) is a fatigue candidate; the 90-of-96 workload is new for him.

**Analyst / front office:** regression inputs are in §7 of the report — wOBA-over-proxy gap (+34 pts), June concentration, chase spike. The *structural* gains (funnel %, pulled-air, everyday role) survive regression; the .304 BA does not need to.

**Marsh (player-facing framing):** the swap of walks for early damage is net-positive as long as two-strike contact holds (.85+ zone contact). The league's counter is coming in spin away — the plan's durability is decided there, not on fastballs.
