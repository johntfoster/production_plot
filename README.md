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
