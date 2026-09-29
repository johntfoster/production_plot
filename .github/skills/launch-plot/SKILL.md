---
name: launch-plot
description: 'Launch the Arps decline-curve web dashboard (dashboard_server.py) for exploring oil production by API number. Use when asked to launch, start, run, open, preview, or restart the plot/dashboard/web server/decline curve app.'
---

# Launch Plot

Starts the Flask-based decline-curve dashboard and opens it for viewing.

## Procedure

1. Free port 8765 in case a previous instance is still running:
   ```bash
   pkill -f "dashboard_server.py" 2>/dev/null; sleep 0.5
   ```
2. Start the server in the background using the `scratch` conda environment's
   Python (never system/base Python — see [AGENTS.md](../../../AGENTS.md)):
   ```bash
   cd /workspaces/production_plot && nohup /home/vscode/.conda/envs/scratch/bin/python dashboard_server.py > /tmp/flask_server.log 2>&1 &
   ```
3. Wait briefly, then verify it started:
   ```bash
   sleep 2 && cat /tmp/flask_server.log
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/ --max-time 5
   ```
   Expect a `200` response and no traceback in the log.
4. Open the dashboard in VS Code's Simple Browser at `http://localhost:8765/`
   (use the `simpleBrowser.show` VS Code command with that URL as the arg).

## Notes

- The dashboard loads `ND_production.csv` at startup (grouped by API number),
  so requests may take a moment the first time.
- `/api/wells` lists available API numbers; `/api/well/<api>` returns that
  well's data plus the best-fit Arps `qi`/`D`/`b` parameters.
- If port 8765 is already in use by an unrelated process, check
  `/tmp/flask_server.log` for the bind error and pick a different port by
  editing the `app.run(...)` call at the bottom of
  [dashboard_server.py](../../../dashboard_server.py).
