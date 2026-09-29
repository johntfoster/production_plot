# scratch

A nearly empty starting point for a PGE323M repository walkthrough. There is no
assignment, starter solution, or grading workflow: just a working development
environment.

## Start

1. **Fork** this repository into your own GitHub account.
2. In your fork, select **Code → Codespaces → Create codespace on main**.
3. Wait for setup to finish, then open a terminal. Python 3.11 and pip are ready
   in the user-owned `scratch` conda environment.

The Python, GitHub Copilot, and Copilot Chat VS Code extensions install
automatically. Sign into GitHub when prompted; Copilot use requires access on
your own account. Installing the extensions does not grant a Copilot entitlement.

## Add packages as you work

Students and coding agents can install packages without `sudo`. For example:

```bash
python -m pip install numpy matplotlib
# Or use conda explicitly, including from a noninteractive agent shell:
conda install --yes --name scratch --override-channels --channel conda-forge numpy matplotlib
```

Only Python and pip are installed initially. The environment's Python is on
`PATH` for VS Code terminals and agent commands. For a tool that resets `PATH`,
use `/home/vscode/.conda/envs/scratch/bin/python -m pip install PACKAGE`.

As you add dependencies, record them in the repository so a fresh Codespace can
reproduce your work; manually installed packages alone do not survive a rebuild.

## Decline curve dashboard

`ND_production.csv` holds monthly oil/gas/water volumes for many North Dakota
wells, keyed by API number. [dashboard_server.py](dashboard_server.py) is a
Flask app that serves an interactive dashboard for exploring these wells:

- Select a well by API number from a dropdown.
- The server fits an Arps hyperbolic decline curve
  ($q(t) = q_i / (1 + bDt)^{1/b}$) to the observed data using several
  outlier-robust loss functions (`linear`, `soft_l1`, `huber`, `cauchy`,
  `arctan`) via `scipy.optimize.least_squares`, and returns the best fit.
- Sliders for `qi`, `D`, and `b` update the decline curve in the browser in
  real time.
- The **Freeze & Calculate 20-yr EUR** button locks the current parameters and
  computes the analytic 20-year estimated ultimate recovery.

Run it with:

```bash
python dashboard_server.py
```

Then open `http://localhost:8765/` in a browser.

