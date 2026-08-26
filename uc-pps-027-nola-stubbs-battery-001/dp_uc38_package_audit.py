"""
dp_uc38_package_audit.py — package-level consistency audit for uc-pps-027.

Runs WITHOUT the data plane. Asserts the governance chain is unbroken: every KPI
in the report has a spec, a glossary entry, a lineage row, a build function and a
named receipt; every receipt the report cites is actually written by a build and
asserted by a verification harness; every guardrail is enforced in code; and the
report's numeric state matches the certification verdict.

RUN 2 (2026-08-26) revision
---------------------------
The run-1 audit asserted the *unfilled* state: `«FILL» tokens > 50` and
`certification returns NOT READY`. Those were correct assertions about a blocked
delivery and are exactly wrong about a certified one. They are replaced — not
deleted — by their run-2 duals, so the audit still fails loudly if the package
drifts back into an inconsistent state:

    run 1 : many FILL tokens  AND  NOT READY
    run 2 : zero FILL tokens  AND  CERTIFY-READY
    never : a filled report with a NOT-READY verdict, or vice versa

The audit is now two-build aware (`dp_uc38_*` primary + `dp_uc38b_*` addendum).
"""
import os
import re
import sys

FAIL, OK = [], []


def chk(name, cond, detail=""):
    (OK if cond else FAIL).append(name)
    print(("[PASS] " if cond else "[FAIL] ") + name + (f"  {detail}" if detail else ""))


H = os.path.dirname(os.path.abspath(__file__))
R = lambda f: open(os.path.join(H, f), encoding="utf-8").read()

build = R("dp_uc38_nola_stubbs_battery.py")
addend = R("dp_uc38b_battery_addendum.py")
figs = R("dp_uc38b_build_figures.py")
ver = R("dp_uc38_verification.py")
ver_b = R("dp_uc38b_verification.py")
rep = R("dp_uc38_nola_stubbs_battery_report.md")
des, gov = R("02_engineering_design.md"), R("03_governance.md")
cert, bid = R("05_quality_certification.md"), R("BID_2026-08-25_uc-pps-027-nola-stubbs.md")
tel = R("telemetry/run_economics_ledger.csv")

# ---------------------------------------------------------------- receipts
rep_receipts = set(re.findall(r"dp_uc38b?_[a-z0-9_]+\.csv", rep))
code = build + addend
writes = set(re.findall(r'"(dp_uc38b?_[a-z0-9_]+\.csv)"', code))
writes |= {f"dp_uc38_{n}.csv" for n in re.findall(r'\(\s*"([a-z0-9_]+)"\s*,\s*[a-z_]+\)', build)}
writes |= {f"dp_uc38b_{n}.csv" for n in re.findall(r'"dp_uc38b_([a-z0-9_]+)\.csv"', addend)}
writes |= {"dp_uc38_verification_results.csv", "dp_uc38b_verification_results.csv",
           "dp_uc38b_verify_dpo_skeleton.csv"}
miss = sorted(rep_receipts - writes)
chk("every receipt cited in the report is written by a build", not miss,
    f"{len(rep_receipts)} cited" if not miss else str(miss))

asserted = set(re.findall(r'"(dp_uc38b?_[a-z0-9_]+\.csv)"', ver + ver_b))
asserted |= set(re.findall(r'dp_uc38b?_[a-z0-9_]+\.csv', ver + ver_b))
self_named = {"dp_uc38_verification_results.csv", "dp_uc38b_verification_results.csv",
              "dp_uc38b_verify_dpo_skeleton.csv"}
gap = sorted(rep_receipts - self_named - asserted)
chk("a verification harness asserts every report receipt", not gap,
    f"{len(asserted)} asserted" if not gap else str(gap))

chk("figures are drawn only from receipts, never recomputed",
    "read_csv" in figs and "read_parquet" not in figs)

# ---------------------------------------------------------------- KPI trace
KPIS = {"BAT-1": "mix_share", "BAT-2": "first_pitch_mix", "BAT-3": "putaway_pitch_mix",
        "BAT-4": "two_strike_fastball_rate", "BAT-5": "repeat_pitch_rate",
        "BAT-6": "arsenal_entropy", "BAT-7": "count_state_divergence",
        "BAT-8": "zone_rate_by_count_state", "BAT-9": "in_zone_whiff_rate",
        "CS-1": "count_state"}
for k, fn in KPIS.items():
    chk(f"{k} traced (spec+glossary+lineage+function)",
        k in des and k in gov and f"def {fn}(" in build, f"fn={fn}")

# run-2 method family: glossaried in 03 and named in the report
for m in ["TR-1", "TR-2", "OC-1", "LH-1", "CH-1"]:
    chk(f"{m} glossaried before use", m in gov and m in addend)
chk("TR-1 named in the report as the Q2 method", "TR-1" in rep and "travel" in rep.lower())

LOCKED = ["get_stats", "nresults", "whiff_rate", "chase_rate", "putaway_rate", "fpsr",
          "hard_hit_rate", "edge_rate", "ooz_called_strike_rate", "air_gb_rate", "xwobacon"]
m = [f for f in LOCKED if f"def {f}(" not in build]
chk("all 11 locked KPI functions present", not m,
    "verbatim block intact" if not m else str(m))

# ---------------------------------------------------------------- guardrails
chk("entity lock uses MLBAM id", "NOLA = 605400" in build and "pitcher == NOLA" in build)
chk("addendum carries the same entity lock", "NOLA = 605400" in addend and "pitcher == NOLA" in addend)
chk("no player_name equality filter on Nola anywhere",
    not re.search(r'player_name\s*==\s*["\']Nola', code + ver + ver_b + rep))
for g, tok, src in [("G3 confound panel", "def confound_panel(", build),
                    ("G4 attribution guard", "attribution_guard", build),
                    ("G5 floors as flags", "below_pitch_floor", build),
                    ("hard exit when data plane absent", "sys.exit(2)", build),
                    ("G6 breakpoint scan implemented", "BREAKPOINT_SCAN", addend),
                    ("G7 single-stratum rule implemented", "travels", addend)]:
    chk(g + " enforced in code", tok in src)
chk("G6 and G7 registered in the glossary", "G6" in gov and "G7" in gov)
chk("O-12 accent fold present in the identity cross-check",
    "unicodedata" in build and "NFKD" in build)

# ------------------------------------------------- filled/certified coherence
fills = len(re.findall(r"«FILL", rep))
ready = "CERTIFY-READY" in cert
notready = "NOT READY TO PUBLISH" in cert
chk("report and certification agree on delivery state",
    (fills == 0 and ready) or (fills > 50 and notready and not ready),
    f"{fills} FILL tokens · certify-ready={ready}")
chk("report ships filled (run-2 target state)", fills == 0, f"{fills} FILL tokens")
chk("run-1 NOT-READY verdict retained as history, not deleted",
    "NOT READY" in cert and ready, "both states present, run 2 authoritative")

chk("prior-product figures labelled with their source", "uc-pps-021" in rep)
chk("attribution limit stated in the report front matter",
    "attribution" in rep[:4000].lower() and "AT-1" in rep)
chk("small samples printed with the report's rates", "PA" in rep and "sample" in rep.lower())

# ---------------------------------------------------------------- economics
chk("bid carries token + time + credit estimate",
    all(t in bid for t in ("Tokens in", "wall clock", "$")))
chk("bid records the run-2 resumption and its overrun",
    "Award resumption" in bid and "over" in bid.lower())
chk("telemetry bid total matches the bid doc", "129000,92000,150" in tel)
chk("telemetry carries both runs", "SUBTOTAL_RUN1" in tel and "SUBTOTAL_RUN2" in tel)
chk("calibration finding C-1 (premise risk) recorded",
    "C-1" in R("telemetry/calibration_report.md") and "premise" in R("telemetry/calibration_report.md").lower())

chk("governance spine 00-07 complete",
    sum(any(f.startswith(f"0{i}_") for f in os.listdir(H)) for i in range(8)) == 8)

print("\n" + "=" * 66)
print(f"{len(OK)} PASS · {len(FAIL)} FAIL")
print("=" * 66)
sys.exit(1 if FAIL else 0)
