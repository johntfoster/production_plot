"""Flask app serving an interactive Arps decline-curve dashboard for ND_production.csv.

Each well (identified by API number) can be selected from a dropdown. The
server groups the raw production data by API, fits an Arps hyperbolic decline
with several robust loss functions on request, and returns the observed data
plus the best-fit qi/D/b to the browser. Sliders in the browser then let the
user interactively adjust qi/D/b and freeze the curve to compute a 20-year EUR.
"""
import numpy as np
import pandas as pd
from flask import Flask, jsonify
from scipy.optimize import least_squares

app = Flask(__name__)

df = pd.read_csv("ND_production.csv", parse_dates=["date"])
df = df.dropna(subset=["date"])

# Pre-group by API so per-well lookups are O(1) instead of re-filtering the
# full dataframe on every request. Wells with no valid dates are dropped.
wells_by_api = {
    str(api): group.sort_values("date").reset_index(drop=True)
    for api, group in df.groupby("api")
    if len(group) > 0
}
well_apis = sorted(wells_by_api)


def arps_hyperbolic(t, qi, d, b):
    # b -> 0 recovers the exponential decline; b in (0, 2] gives hyperbolic/harmonic decline.
    if b == 0:
        return qi * np.exp(-d * t)
    return qi / (1 + b * d * t) ** (1 / b)


def residuals(params, t, q):
    return arps_hyperbolic(t, *params) - q


def fit_best(t, q):
    losses = ["linear", "soft_l1", "huber", "cauchy", "arctan"]
    best_params, best_sse = None, np.inf
    for loss in losses:
        result = least_squares(
            residuals,
            x0=[max(q[0], 1.0), 1e-3, 1.0],
            args=(t, q),
            loss=loss,
            f_scale=max(q.std(), 1.0),
            bounds=([0, 0, 0], [np.inf, np.inf, 2]),
        )
        sse = np.sum(residuals(result.x, t, q) ** 2)
        if sse < best_sse:
            best_sse, best_params = sse, result.x
    return best_params


@app.route("/api/wells")
def api_wells():
    return jsonify(well_apis)


@app.route("/api/well/<api>")
def api_well(api):
    well = wells_by_api[api]
    t = (well["date"] - well["date"].iloc[0]).dt.days.to_numpy()
    q = well["volume_oil_formation_bbls"].to_numpy(dtype=float)

    if len(t) >= 3:
        qi, d, b = fit_best(t, q)
    else:
        qi, d, b = float(q[0]) if len(q) else 0.0, 1e-3, 1.0

    return jsonify(
        {
            "api": api,
            "dates": well["date"].dt.strftime("%Y-%m-%d").tolist(),
            "oil": q.tolist(),
            "t": t.tolist(),
            "start_date": well["date"].iloc[0].strftime("%Y-%m-%d"),
            "qi0": qi,
            "d0": d,
            "b0": b,
        }
    )


@app.route("/")
def index():
    return INDEX_HTML


INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ND Oil Production Decline Curve Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  body { font-family: sans-serif; margin: 2rem; }
  .slider-row { margin-bottom: 1rem; }
  .slider-row label { display: inline-block; width: 12rem; }
  .slider-row output { margin-left: 1rem; font-weight: bold; }
  input[type=range] { width: 400px; }
  select { font-size: 1rem; padding: 0.25rem; }
</style>
</head>
<body>
<h2>ND Oil Production - Arps Hyperbolic Decline</h2>

<div class="slider-row">
  <label for="well-select">Well (API number)</label>
  <select id="well-select"></select>
</div>

<div id="chart" style="width: 100%; height: 600px;"></div>

<div class="slider-row">
  <label for="qi">Initial rate qi (bbls)</label>
  <input type="range" id="qi" min="0" max="100" step="0.1" value="0">
  <output id="qi-out">0</output>
</div>
<div class="slider-row">
  <label for="d">Decline rate D (1/day)</label>
  <input type="range" id="d" min="0" max="0.05" step="0.00001" value="0">
  <output id="d-out">0</output>
</div>
<div class="slider-row">
  <label for="b">Decline exponent b</label>
  <input type="range" id="b" min="0" max="2" step="0.01" value="0">
  <output id="b-out">0</output>
</div>

<button id="freeze-btn">Freeze &amp; Calculate 20-yr EUR</button>
<span id="eur-out" style="margin-left: 1rem; font-weight: bold;"></span>

<script>
let tFit = [];
let startDate = new Date();

function arpsHyperbolic(tArr, qi, d, b) {
  if (b === 0) {
    return tArr.map(ti => qi * Math.exp(-d * ti));
  }
  return tArr.map(ti => qi / Math.pow(1 + b * d * ti, 1 / b));
}

// Analytic cumulative volume (EUR) of the Arps decline from t=0 to t=days.
function arpsEur(qi, d, b, days) {
  if (d === 0) {
    return qi * days;
  }
  if (b === 0) {
    return (qi / d) * (1 - Math.exp(-d * days));
  }
  if (Math.abs(b - 1) < 1e-9) {
    return (qi / d) * Math.log(1 + d * days);
  }
  return (qi / ((1 - b) * d)) * (1 - Math.pow(1 + b * d * days, 1 - 1 / b));
}

function updateCurve() {
  const qi = parseFloat(document.getElementById("qi").value);
  const d = parseFloat(document.getElementById("d").value);
  const b = parseFloat(document.getElementById("b").value);
  document.getElementById("qi-out").textContent = qi.toFixed(1);
  document.getElementById("d-out").textContent = d.toFixed(5);
  document.getElementById("b-out").textContent = b.toFixed(2);
  Plotly.restyle("chart", {y: [arpsHyperbolic(tFit, qi, d, b)]}, [1]);
}

["qi", "d", "b"].forEach(id => {
  document.getElementById(id).addEventListener("input", updateCurve);
});

document.getElementById("freeze-btn").addEventListener("click", () => {
  const qi = parseFloat(document.getElementById("qi").value);
  const d = parseFloat(document.getElementById("d").value);
  const b = parseFloat(document.getElementById("b").value);
  ["qi", "d", "b"].forEach(id => {
    document.getElementById(id).disabled = true;
  });
  const eur = arpsEur(qi, d, b, 20 * 365.25);
  document.getElementById("eur-out").textContent =
    `Frozen: qi=${qi.toFixed(1)}, D=${d.toFixed(5)}, b=${b.toFixed(2)} -> 20-yr EUR = ${Math.round(eur).toLocaleString()} bbls`;
});

async function loadWell(api) {
  ["qi", "d", "b"].forEach(id => {
    document.getElementById(id).disabled = false;
  });
  document.getElementById("eur-out").textContent = "";

  const resp = await fetch(`/api/well/${api}`);
  const w = await resp.json();

  startDate = new Date(w.start_date);
  const tMin = Math.min(...w.t);
  const tMax = Math.max(...w.t);
  tFit = [];
  const nFit = 200;
  for (let i = 0; i < nFit; i++) {
    tFit.push(tMin + (tMax - tMin) * i / (nFit - 1));
  }
  const datesFit = tFit.map(days => {
    const dt = new Date(startDate);
    dt.setDate(dt.getDate() + days);
    return dt.toISOString().slice(0, 10);
  });

  const traceObserved = {x: w.dates, y: w.oil, mode: "markers", type: "scatter", name: "Observed"};
  const traceFit = {
    x: datesFit, y: arpsHyperbolic(tFit, w.qi0, w.d0, w.b0),
    mode: "lines", type: "scatter", name: "Arps fit", line: {color: "red"}
  };
  Plotly.react("chart", [traceObserved, traceFit], {
    xaxis: {title: "Date"}, yaxis: {title: "Oil volume (bbls)"},
    title: `API ${api}`, margin: {t: 40}
  });

  const qiSlider = document.getElementById("qi");
  const dSlider = document.getElementById("d");
  const bSlider = document.getElementById("b");
  qiSlider.max = (w.qi0 * 3).toFixed(2);
  qiSlider.value = w.qi0.toFixed(4);
  dSlider.max = Math.max(w.d0 * 3, 0.05).toFixed(5);
  dSlider.value = w.d0.toFixed(5);
  bSlider.value = w.b0.toFixed(3);
  updateCurve();
}

async function init() {
  const resp = await fetch("/api/wells");
  const apis = await resp.json();
  const select = document.getElementById("well-select");
  apis.forEach(api => {
    const opt = document.createElement("option");
    opt.value = api;
    opt.textContent = api;
    select.appendChild(opt);
  });
  select.addEventListener("change", () => loadWell(select.value));
  if (apis.length > 0) {
    loadWell(apis[0]);
  }
}

init();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765, debug=False)
