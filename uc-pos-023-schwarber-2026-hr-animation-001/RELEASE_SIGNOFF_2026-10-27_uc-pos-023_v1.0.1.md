# Release Sign-Off | `uc-pos-023` | `dp\_uc58` **v1.0.1**

**UC #58 | Kyle Schwarber 2026 home runs, animated: "Forty-Five and a Question Mark"**
Value stream: Phillies Offense (`pos`) | Human DPO: Kellen Short | Released 2026-10-27 ≈23:20 ET
Prepared by: `data-product-owner` (orchestration), `certification-agent`, `version-controller`, `privacy-watchdog`

## 1 | Decision

|Item|Decision|Evidence|
|-|-|-|
|BID (Tier A, ≈400k / 45 min)|**APPROVED / AWARDED for the full build**|DPO, 2026-10-27 22:53 ET: "The video looks great and the BID + supporting materials are APPROVED with edits directly in the mounted repository … The BID has been awarded for the full build"|
|Supporting materials (`00`–`07`)|**APPROVED with DPO edits**|Edits made in place 22:06–22:53 ET (`00`–`07`; K1 markup `keyframes/dp\_uc58\_k1\_pre\_phillies\_KS.png`)|
|Claude Design render (from the v1.0.0 prompt)|**Accepted**|"The video looks great"|
|Release `dp\_uc58` v1.0.1 (DPO copy edits applied)|**APPROVED for release**|This document; harness 31/31; DQ 10/3/0; certification READY-CONDITIONAL|
|External publish of the video|**APPROVED by the DPO**, conditions C1–C7 carried (§4)|privacy-watchdog clear (`07` §2)|

**DPO sign-off:** Kellen Short (DPO). Approved by session message, 2026-10-27 22:53 ET. Replace this line with a dated signature if a wet sign-off is required.

## 2 | What changed, v1.0.0 → v1.0.1 (version-controller: **non-breaking, copy only**)

|Change|Source|Effect|
|-|-|-|
|**ST-1 copy style:** every keyframe and prompt title in Title Case; subtitles carry context only (method notes removed)|DPO markup on K1|8 titles and 8 subtitles rewritten; legends now carry the mark meanings (K6 "dotted = postseason", K7 "white ring = clip")|
|**COPY-1:** one copy deck, `out/dp\_uc58\_copy\_deck.json`, feeds both the keyframes and the prompt|org response to ST-1|Keyframe and prompt copy can no longer drift; checked by V29|
|Prompt §1 rule 9 (ST-1); S3 gains a title; S6/S7 facts moved from subtitles to stat chips; S4 badge de-duplicated|follows ST-1|No number changed|
|Harness +3 checks (V29 copy deck in prompt, V30 ST-1, V31 keyframes rendered from the current deck)|certification-agent|28/28 → **31/31**|

**Data unchanged.** `design\_data.json` sha `e8de66ca…` is identical to v1.0.0. The house log is unchanged too: `phils\_2026.parquet` was rewritten at 21:45 ET, but its sha `be5d313d…` and the 2026-10-01 anchor are the same. Kernel and build are untouched (`d2621361…`, `23e2c501…`).

## 3 | Release manifest (sha256, first 16)

|Artifact|sha|Location|
|-|-|-|
|`dp\_uc58\_claude\_design\_prompt.md` (v1.0.1)|`f4b6733b5153a247`|MLB root + this folder|
|`dp\_uc58\_technical\_feasibility\_brief.md`|`944ad211814e2cb3`|MLB root + this folder|
|`out/dp\_uc58\_design\_data.json`|`e8de66ca10d8eb4c`|MLB `out/` + `data/`|
|`out/dp\_uc58\_copy\_deck.json`|`6e26b014706af913`|MLB `out/` + `data/`|
|`out/dp\_uc58\_clip\_list.csv`|`26fdbce9a4ef4969`|MLB `out/` + `data/`|
|K1–K8 keyframes|`e56d2390…` `be2f168b…` `2b52c057…` `a65335a0…` `3db3deed…` `ddb0ac26…` `3079f378…` `c8ed117b…`|MLB `out/` + `keyframes/`|
|`dp\_uc58\_kernel.py` / `\_build.py`|`d262136169db4bb1` / `23e2c5010e4b0d43`|MLB root (unchanged)|
|`dp\_uc58\_build\_keyframes.py` / `\_build\_prompt.py` / `\_verification.py`|`65b53a0c5b536239` / `1450c7fce5aea147` / `a380c76b4f64aaf9`|MLB root|

## 4 | Conditions carried into release (certification-agent, `05` §4)

C1 two approximate spray dots | C2 one CBP outline for every park | C3 DH-1 fallback on 22 of 25 DH days (none in 2026) | C4 provisional rules | C5 7 clip pitchers unnamed | C6 `play\_id`s resolve locally | C7 Claude Design export path. C7 is **closed in practice**: the DPO has the rendered video.

## 5 | Open after release (not blocking)

1. **G1 / clip 7:** the approved video used the defaults (lefty-fastball clips; clip 7 = clip 4). No change unless the DPO re-cuts.
2. **Provisional rules:** approval of the receipts is read as ratifying HB-1, WP-1, CP-1, HL-1, SP-1/2/3, PM-1, GR-1, DH-1, ST-1 and COPY-1 **for this product**. Promotion to house standards for other UCs is a separate decision.
3. **`cumulative\_metric` v1.1** (DH-1 `order=`, PA-X1 default): a separate change, breaking-by-value, needs its own acknowledgement.
4. **Ledger:** paste UC52–UC58 patches, oldest first.
5. **Housekeeping:** delete `MLB/out/\_to\_delete/` (this session cannot delete).
