"""phillies_dp.recap_viz - SD-3: shared helpers for the Tier 3 recap visual standard (built in uc-pos-024 / dp_uc60, 2026-10-29).

Standards (Pitcher Recap Visual Redesign brief, Tier 3; acceptance criteria V1-V7):
  V1 no connected lines for discrete observations (exception: cumulative-by-PA, one line per season)
  V2 context before highlight (every featured visual plotted against a named comparison set; subject = highlighted mark)
  V3 show distribution (boxes shade the middle 50%, on every metric)
  V4 trendline scatters report R^2 and n, and say whether the subject sits above or below the line
  V5 no stacked or single-bar proportion charts
  V6 time on the x axis; axis labels and units always visible; small multiples readable at PDF size
  V7 no dual-metric charts on shared axes unless the units are the same
Registries: data/_schema/comparison_sets.json (SD-1), data/_schema/eras.json (SD-2).
Additive module: nothing else in phillies_dp imports it. Self-test: python -m phillies_dp.recap_viz
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "data" / "_schema"
STANDARDS = {"V1": "no connected lines for discrete observations", "V2": "context before highlight", "V3": "show distribution (IQR)",
             "V4": "trendline reports R^2 and n", "V5": "no stacked / single-bar proportions", "V6": "time on x; labelled axes with units",
             "V7": "no dual-metric shared axes unless same units"}


def registry(name: str) -> dict:
    return json.loads((SCHEMA / f"{name}.json").read_text(encoding="utf-8"))


def comparison_set(key: str) -> dict:
    return registry("comparison_sets")[key]


def era(key: str) -> dict:
    return registry("eras")[key]


def check_asb(game_dates, key: str = "asb_2026") -> bool:
    """True when no game date falls inside the registered break window (the condition that makes the repo's ASB constants agree)."""
    import pandas as pd
    lo, hi = era(key)["break_window"]
    d = pd.to_datetime(pd.Series(list(game_dates)))
    return not d.between(pd.Timestamp(lo), pd.Timestamp(hi)).any()


def trendline_r2(x, y, w=None) -> dict:
    """OLS (optionally weighted) y = a + b x. Returns slope, intercept, r2, n. NaNs dropped."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    w_ = np.ones(m.sum()) if w is None else np.asarray(w, float)[m]
    x, y = x[m], y[m]
    if len(x) < 3:
        return dict(slope=np.nan, intercept=np.nan, r2=np.nan, n=int(len(x)))
    b, a = np.polyfit(x, y, 1, w=np.sqrt(w_))
    yhat = a + b * x
    ybar = np.average(y, weights=w_)
    ss_res, ss_tot = np.sum(w_ * (y - yhat) ** 2), np.sum(w_ * (y - ybar) ** 2)
    return dict(slope=float(b), intercept=float(a), r2=float(1 - ss_res / ss_tot) if ss_tot > 0 else np.nan, n=int(len(x)))


def above_below(fit: dict, x0: float, y0: float, tol: float = 0.0) -> str:
    """V4 wording: where a subject point sits relative to the fitted line."""
    r = y0 - (fit["intercept"] + fit["slope"] * x0)
    return "on the line" if abs(r) <= tol else ("above the line" if r > 0 else "below the line")


def dot_sizes(v, lo: float = 7, hi: float = 26):
    """Marker diameters for a sizing variable (PA, BF, pitches): area-proportional, fixed range."""
    v = np.asarray(v, float)
    if np.nanmax(v) == np.nanmin(v):
        return np.full(len(v), (lo + hi) / 2)
    a = (v - np.nanmin(v)) / (np.nanmax(v) - np.nanmin(v))
    return np.sqrt(lo ** 2 + a * (hi ** 2 - lo ** 2))


def context_box(go, x, values, name, color="#9AA3AF", **kw):
    """V2/V3: one comparison-set box (middle 50% shaded, median line), no points."""
    return go.Box(x=[x] * len(values), y=list(values), name=name, marker_color=color, fillcolor="rgba(154,163,175,0.30)",
                  line=dict(color=color, width=1.4), boxpoints=False, whiskerwidth=0.4, showlegend=False,
                  hoverinfo="y", **kw)


def discrete_dots(go, x, y, size_var, name, color, text=None, **kw):
    """V1: discrete observations as dots sized by a stated variable (never joined)."""
    return go.Scatter(x=list(x), y=list(y), mode="markers", name=name, text=text,
                      marker=dict(size=list(dot_sizes(size_var)), color=color, line=dict(color="#ffffff", width=1.2)), **kw)


def sketch_trend(go, x, y, fit: dict, name="trend", color="#5b6170"):
    """V1/V4: dotted fitted line across the observed x range."""
    xs = np.linspace(np.nanmin(x), np.nanmax(x), 20)
    return go.Scatter(x=list(xs), y=list(fit["intercept"] + fit["slope"] * xs), mode="lines", name=name,
                      line=dict(color=color, width=1.6, dash="dot"), hoverinfo="skip", showlegend=False)


def audit(fig, spec: dict) -> dict:
    """Machine check of V1-V7 on a plotly figure. spec keys: discrete (bool), cumulative (bool), context (bool),
    distribution (bool or None), trendline (bool), time_axis (bool or None). Returns {standard: PASS/FAIL/N-A}."""
    d = fig.to_dict()
    data, lay = d.get("data", []), d.get("layout", {})
    res = {}
    lines = [t for t in data if t.get("type", "scatter") == "scatter" and "lines" in (t.get("mode") or "lines")
             and (t.get("line", {}) or {}).get("dash") != "dot" and not t.get("meta", {}) == "reference"]
    res["V1"] = "PASS" if (not spec.get("discrete") or spec.get("cumulative") or not lines) else "FAIL"
    res["V2"] = "PASS" if (not spec.get("context", True) or any(t.get("type") == "box" or "context" in str(t.get("name", "")).lower()
                                                                  or t.get("legendgroup") == "context" for t in data)) else "FAIL"
    res["V3"] = "N-A" if not spec.get("distribution") else ("PASS" if any(t.get("type") == "box" for t in data) else "FAIL")
    txt = " ".join(str(a.get("text", "")) for a in lay.get("annotations", [])) + str((lay.get("title") or {}).get("text", ""))
    res["V4"] = "N-A" if not spec.get("trendline") else ("PASS" if ("R²" in txt and "n =" in txt and ("above" in txt or "below" in txt)) else "FAIL")
    bars = [t for t in data if t.get("type") == "bar"]
    res["V5"] = "PASS" if not bars or (lay.get("barmode") not in ("stack", "relative") and all(len(t.get("x", []) or []) > 1 for t in bars)) else "FAIL"
    axes = {k: v for k, v in lay.items() if k.startswith(("xaxis", "yaxis"))}
    titled = all((v.get("title") or {}).get("text") for k, v in axes.items() if v.get("visible", True) is not False) if axes else False
    res["V6"] = "PASS" if titled else "FAIL"
    res["V7"] = "PASS" if not any(v.get("overlaying") for v in axes.values()) else "FAIL"
    return res


def _selftest():
    fit = trendline_r2([1, 2, 3, 4], [2, 4, 6, 8.2])
    assert fit["n"] == 4 and fit["r2"] > 0.99 and above_below(fit, 2, 5) == "above the line"
    assert abs(dot_sizes([1, 2, 3])[0] - 7) < 1e-9
    assert set(registry("comparison_sets")) >= {"phi_hitter_seasons_200", "phi_sp_seasons", "phi_lhp_relief_seasons"}
    assert era("asb_2026")["first_half_last_date"] == "2026-07-12"
    import plotly.graph_objects as go
    f = go.Figure([context_box(go, "2026", [1, 2, 3], "context"), discrete_dots(go, ["2026"], [2], [500], "s", "#E81828")])
    f.update_layout(xaxis_title="Season", yaxis_title="wOBA")
    r = audit(f, dict(discrete=True, context=True, distribution=True))
    assert r["V1"] == r["V2"] == r["V3"] == r["V6"] == r["V7"] == "PASS", r
    bad = go.Figure([go.Scatter(x=[1, 2], y=[1, 2], mode="lines+markers")])
    assert audit(bad, dict(discrete=True, context=True))["V1"] == "FAIL"
    return "recap_viz selftest PASS"


if __name__ == "__main__":
    print(_selftest())
