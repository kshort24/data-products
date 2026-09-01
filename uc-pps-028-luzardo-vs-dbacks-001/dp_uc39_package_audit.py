"""
dp_uc39_package_audit.py — certification-agent artifact-completeness audit.

Verification proves the NUMBERS are right. This proves the PACKAGE is complete:
every governance document present and non-trivial, every receipt the report cites
actually on disk, every deliverable built, and no cross-reference dangling.
Exit 0 only when every check passes.
"""
import os, re, sys, json, csv

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "out")
P, F = 0, 0
def chk(label, ok, detail=""):
    global P, F
    P += bool(ok); F += (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label:<62} {detail}")

print("\n" + "="*86)
print("dp_uc39 PACKAGE AUDIT — uc-pps-028")
print("="*86)

print("\n-- governance spine ------------------------------------------------------------")
SPINE = ["00_dpo_orchestration_record.md","01_strategy_intake.md","02_engineering_design.md",
         "03_governance.md","04_engineering_build.md","05_quality_certification.md",
         "06_consumer_success.md","07_platform_marketing.md","README.md"]
for f in SPINE:
    p = os.path.join(HERE, f); sz = os.path.getsize(p) if os.path.isfile(p) else 0
    chk(f"{f} present and substantive", sz > 1200, f"{sz:,} bytes")

print("\n-- contract & ledger ----------------------------------------------------------")
contract = [f for f in os.listdir(HERE) if f.startswith("uc-pps-028-") and f.endswith(".md")]
chk("use-case contract present", len(contract) == 1, contract[0] if contract else "MISSING")
patch = [f for f in os.listdir(HERE) if f.startswith("uc_ledger_AI_PATCH")]
chk("ledger patch staged", len(patch) == 1, patch[0] if patch else "MISSING")

print("\n-- build & harness ------------------------------------------------------------")
for f, minsz in [("dp_uc39_luzardo_vs_dbacks.py", 30000), ("dp_uc39_verification.py", 10000),
                 ("dp_uc39_build_dashboard.py", 15000)]:
    sz = os.path.getsize(os.path.join(HERE, f)) if os.path.isfile(os.path.join(HERE, f)) else 0
    chk(f"{f}", sz > minsz, f"{sz:,} bytes")

print("\n-- reader deliverables --------------------------------------------------------")
for f, minsz in [("dp_uc39_luzardo_vs_dbacks_report.md", 15000),
                 ("dp_uc39_luzardo_vs_dbacks_report.pdf", 100000),
                 ("dp_uc39_luzardo_dashboard.html", 60000),
                 ("dp_uc39_luzardo_dashboard_artifact.html", 60000)]:
    p = os.path.join(HERE, f); sz = os.path.getsize(p) if os.path.isfile(p) else 0
    chk(f"{f}", sz > minsz, f"{sz:,} bytes")

print("\n-- receipts -------------------------------------------------------------------")
files = sorted(os.listdir(OUT))
csvs = [f for f in files if f.endswith(".csv")]
pngs = [f for f in files if f.endswith(".png")]
chk("receipt count >= 28", len(files) >= 28, f"{len(files)} files ({len(csvs)} csv, {len(pngs)} png)")
chk("all receipts namespaced dp_uc39_", all(f.startswith("dp_uc39_") for f in files),
    "no prior-UC file can be overwritten")
chk("payload.json present", "dp_uc39_payload.json" in files)
chk("5 figures rendered", len(pngs) == 5, ", ".join(p.replace("dp_uc39_","") for p in pngs))
for f in csvs:
    with open(os.path.join(OUT, f), encoding="utf-8") as fh:
        rows = sum(1 for _ in fh)
    chk(f"receipt non-empty · {f}", rows >= 2, f"{rows-1} data rows")

print("\n-- report cross-references resolve --------------------------------------------")
rpt = open(os.path.join(HERE, "dp_uc39_luzardo_vs_dbacks_report.md"), encoding="utf-8").read()
cited = set(re.findall(r"dp_uc39_[a-z0-9_]+\.(?:csv|png)", rpt))
for c in sorted(cited):
    chk(f"cited receipt exists · {c}", c in files)
chk("report cites >= 12 distinct receipts", len(cited) >= 12, f"{len(cited)} cited")
figs = set(re.findall(r"out/(dp_uc39_fig\d[a-z0-9_]*\.png)", rpt))
chk("every embedded figure exists", figs.issubset(set(pngs)), f"{len(figs)} embedded")

print("\n-- governance assertions hold -------------------------------------------------")
with open(os.path.join(OUT, "dp_uc39_dq_scorecard.csv"), encoding="utf-8") as fh:
    dq = list(csv.DictReader(fh))
chk("DQ scorecard: 0 FAIL", sum(1 for r in dq if r["result"] == "FAIL") == 0,
    f"{len(dq)} rules, {sum(1 for r in dq if r['result']=='WARN')} WARN")
with open(os.path.join(OUT, "dp_uc39_freshness_manifest.csv"), encoding="utf-8") as fh:
    fr = list(csv.DictReader(fh))
chk("freshness manifest discloses the unverified lineup",
    any("NOT AVAILABLE" in r["value"] for r in fr))
chk("freshness manifest logs the carry-in game date",
    any("2026-09-01" in r["value"] for r in fr))
with open(os.path.join(OUT, "dp_uc39_uc17_reproduction_check.csv"), encoding="utf-8") as fh:
    rp = list(csv.DictReader(fh))
chk("parent-reproduction check: zero REVIEW rows",
    sum(1 for r in rp if r["match"] == "REVIEW") == 0, f"{len(rp)} metrics checked")
with open(os.path.join(OUT, "dp_uc39_consistency_breakpoint_scan.csv"), encoding="utf-8") as fh:
    sc = list(csv.DictReader(fh))
chk("breakpoint scan covers 8 boundaries", len(sc) == 8)
chk("scan shows the level claim surviving every boundary",
    all(r["agg_xwoba__rank"] == "1" for r in sc), "xwOBA rank == 1 in all 8")
chk("scan shows the variance claim NOT surviving",
    not all(r["cn1_xwoba_sd__rank"] == "1" for r in sc),
    "CN-1 rank varies -> reported as boundary-dependent")

print("\n-- disclosure discipline ------------------------------------------------------")
for doc, needle, why in [
    ("dp_uc39_luzardo_vs_dbacks_report.md", "NOT AVAILABLE|not confirmed|No confirmed", "unverified lineup"),
    ("dp_uc39_luzardo_vs_dbacks_report.md", "O-5", "carried defect O-5"),
    ("dp_uc39_luzardo_vs_dbacks_report.md", "O-8", "carried defect O-8"),
    ("dp_uc39_luzardo_vs_dbacks_report.md", "not official|RA9 basis", "RA9-not-ERA disclosure"),
    ("dp_uc39_luzardo_dashboard.html", "not confirmed", "unverified lineup"),
    ("dp_uc39_luzardo_dashboard.html", "truncated_pa", "carried defect O-5"),
]:
    t = open(os.path.join(HERE, doc), encoding="utf-8").read()
    chk(f"{doc.split('_')[-1][:18]:<18} discloses {why}", re.search(needle, t) is not None)

t = open(os.path.join(HERE, "dp_uc39_luzardo_dashboard.html"), encoding="utf-8").read()
chk("offline dashboard vendors nothing (no external http asset)",
    not re.search(r'(src|href)\s*=\s*"https?://', t), "no CDN, no webfont, opens offline")
a = open(os.path.join(HERE, "dp_uc39_luzardo_dashboard_artifact.html"), encoding="utf-8").read()
chk("artifact variant carries no doctype/html/body wrapper",
    "<!doctype" not in a.lower() and "<body" not in a.lower())
# www.w3.org appears only as the SVG namespace URI in createElementNS — it is an
# identifier, never fetched. Exclude it before testing the network allowlist.
_hosts = set(re.findall(r'https?://([a-z0-9.]+)/', a)) - {"www.w3.org"}
chk("artifact variant only reaches allowlisted font hosts",
    _hosts <= {"fonts.googleapis.com", "fonts.gstatic.com"}, str(sorted(_hosts)))
_off = set(re.findall(r'https?://([a-z0-9.]+)/', t)) - {"www.w3.org"}
chk("offline dashboard reaches no host at all", not _off, str(sorted(_off)) if _off else "none")
chk("both dashboards embed the same payload",
    json.loads(re.search(r"const DATA=(\{.*?\});", t, re.S).group(1))["meta"] ==
    json.loads(re.search(r"const DATA=(\{.*?\});", a, re.S).group(1))["meta"])

print("\n" + "="*86)
print(f"RESULT: {P}/{P+F} PASS · {F} FAIL")
print("="*86 + "\n")
sys.exit(0 if F == 0 else 1)
