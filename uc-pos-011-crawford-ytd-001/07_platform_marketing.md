# 07 · Platform & Marketing
**cost-watchdog · data-observability · analytics-enabler**

## Cost

Trivial. 58 MB parquet, full build under 60 s single-threaded. No warehouse spend, no scheduled
compute. The two heaviest steps are the 217-season population pool and the 9-season context rolling
frame (270,954 rows → 4,177 cumulative points); both run once per build.

The dashboard grew from 242 KB to 443 KB when the charting library was vendored. That is the entire
cost of the artifact rendering without a network, and it is worth paying.

## Observability — re-run triggers

| Signal | Threshold | Action |
|---|---|---|
| August completes | after 8/31 | **re-run — this is the important one.** August is currently 42 PA and below floor; completing it either promotes the headline to interpretable or removes it |
| BABIP | falls below .330 over a trailing 50-PA window | the correction has begun; **the size of the fall is the size of the correction to this report** |
| Mean launch angle | moves more than 2° over a 50-tracked-BIP window | **the only signal that would change the developmental conclusion.** Alert regardless of direction |
| LHP share | returns above 12% over a 50-PA window | the August shielding was situational, not policy — re-read the platoon section |
| LHP share | stays below 5% for another 40 PA | it is policy. Escalate: the evidence base for it is 23 PA and points the other way |
| Chase rate | falls below 32% over a 50-PA window | a genuine approach change would finally be visible; today there is none |
| New `description` or `pitch_type` value | any | **halt** — the governed SWINGS / `PITCH_GROUP` mappings are no longer exhaustive |
| `launch_speed` NULL rate on BIP | above 3% | **O-8 becomes material** — `hard_hit_rate` starts meaningfully understating |
| Ratification of CR-1 / CR-2 / CX-1 / PL-1 | on DPO sign-off | promote to notebook; re-baseline verification |

**Staleness rule:** any figure quoted after **2026-08-13** must state the as-of date.

## Publication note — what is publishable and what is not

**Nothing here is approved for external distribution** (`03_governance.md`). Internally, the finding
worth leading with is not the one in the request.

The request asked whether Crawford turned a corner. He did — but **the corner he turned is a
strikeout-rate corner, not a batted-ball corner**, and the two have very different shelf lives. The
contact-skill gain (whiff 20.5% → 15.9%) is the kind of thing rookies genuinely learn. The results
gain sitting on top of it is mostly a 79-point BABIP swing on ground balls he is hitting *softer* than
before. Those two facts point in opposite directions and both are true.

**Three corrections to the supporting narrative:**

1. **"OBP bouncing back" is right for the wrong reason.** OBP rose 56 points while **walk rate fell**
   6.6% → 4.6%. This is a hit-dependent OBP. If BABIP regresses, OBP goes with it — there is no
   plate-discipline floor underneath it.
2. **The Derek Hill hypothesis does not survive the exposure data as posed.** LHP share is 15.0%
   after his debut versus 15.3% before; direct standardisation puts the whole mix effect below 0.0002
   on every metric. **The instinct was right and the timing was wrong** — the shielding is real,
   severe and begins in *August*, seven weeks later. That relocation is the finding, not a footnote.
3. **The ground-ball and launch-angle concerns are not resolved and this season did not address
   them.** GB rate 56.5% (89th percentile), mean launch angle 2.26° (**2nd percentile**). Neither
   moved across the break. Any internal summary that describes 2026 as evidence the profile is
   working needs this sentence in it.

## Reuse

- **PL-1 `platoon_counterfactual`** — general to any "was he shielded / platooned into looking better"
  claim, on any hitter, any window. This class of question recurs constantly and has been answered by
  eyeballing splits; direct standardisation answers it in one number. **Strongest reuse candidate in
  this build.**
- **The breakpoint sensitivity scan** — should be a *standing requirement* whenever a requester
  supplies a date they chose after seeing the outcome. It cost nine lines and it turned "he improved
  after mid-June" into "he improved after mid-June, and the sign flips if you say mid-May." Extends
  the `uc-pos-008` both-framings precedent from premises and sample selection to **breakpoints**.
- **CX-1 `cf_context_pool`** — the `fielder_8` → `batter` join generalises to every position. A
  catcher, shortstop or corner-outfield context pool is a parameter change, not a new build.
- **CR-1 `battedball_profile`'s two-population design** — shares over the complete classifier, central
  tendency over the incomplete sensor, in one function with one floor. This is the right shape for any
  metric family that mixes derived and sensed columns.
- **Vendoring the charting library** — see `04`. The CDN pattern has a silent single point of failure
  that takes down the tables too. Every future dashboard should inline the library and wrap its chart
  calls.
- **The verdict-column premise table (report §1)** — when a requester asks for their assumptions to be
  tested, answer all of them in one table before explaining any of them. Cheap, and it makes a
  falsified premise impossible to bury.
