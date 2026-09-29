#!/usr/bin/env bash
set -euo pipefail

# Keep project packages in an environment owned by the Codespaces user.
environment="$HOME/.conda/envs/scratch"
if [[ ! -x "$environment/bin/python" ]]; then
    /opt/conda/bin/conda create --yes --prefix "$environment" \
        --override-channels --channel conda-forge python=3.11 pip
fi

# Interactive terminals and noninteractive agent commands use the same Python.
activation='source /opt/conda/etc/profile.d/conda.sh && conda activate "$HOME/.conda/envs/scratch"'
touch "$HOME/.bashrc"
if ! grep -Fxq "$activation" "$HOME/.bashrc"; then
    printf '\n%s\n' "$activation" >> "$HOME/.bashrc"
fi

"$environment/bin/python" --version
"$environment/bin/python" -m pip --version
