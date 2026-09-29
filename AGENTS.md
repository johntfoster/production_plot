# Agent instructions

This repository uses a dedicated conda environment named `scratch`
(`/home/vscode/.conda/envs/scratch`). Always use this environment's Python for
every Python invocation, package install, and script run in this repo — never
the base conda environment or system Python.

- Interactive/login shells already have `scratch` activated via `~/.bashrc`.
- Noninteractive agent shells (where `.bashrc` may not be sourced) must call
  the interpreter directly: `/home/vscode/.conda/envs/scratch/bin/python`.
- Install packages into this environment only, e.g.:
  ```bash
  conda install --yes --name scratch --override-channels --channel conda-forge <package>
  # or
  /home/vscode/.conda/envs/scratch/bin/python -m pip install <package>
  ```
- After adding a dependency, update [requirements.txt](requirements.txt) (pin
  the installed version) so a fresh Codespace/devcontainer rebuild reproduces
  the same environment via `.devcontainer/setup.sh`.
- Do not create additional virtual environments (venv, poetry, etc.) — `scratch`
  is the single source of truth for this project's Python environment.

## Decline curve dashboard

[dashboard_server.py](dashboard_server.py) is a Flask app (port 8765) that
serves the interactive Arps decline-curve dashboard over `ND_production.csv`.
Launch it with the `scratch` environment's Python, e.g.
`/home/vscode/.conda/envs/scratch/bin/python dashboard_server.py`, and view it
at `http://localhost:8765/`. See the `launch-plot` skill for the full
launch/verify procedure.

