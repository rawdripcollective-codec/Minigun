"""Simple HTML dashboard served at the root path."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Minigun Console</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #0d1117; color: #c9d1d9; min-height: 100vh; }
    header { background: #161b22; border-bottom: 1px solid #30363d; padding: 1rem 2rem; display: flex; align-items: center; gap: 1rem; }
    header h1 { font-size: 1.4rem; color: #58a6ff; }
    header span { color: #8b949e; font-size: 0.85rem; }
    main { max-width: 960px; margin: 2rem auto; padding: 0 1.5rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.25rem; }
    .card h3 { font-size: 0.8rem; color: #8b949e; text-transform: uppercase; letter-spacing: .05em; margin-bottom: .5rem; }
    .card .value { font-size: 1.8rem; font-weight: 700; color: #58a6ff; }
    .card .label { font-size: 0.75rem; color: #6e7681; margin-top: .25rem; }
    .endpoint-list { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.25rem; }
    .endpoint-list h2 { color: #e6edf3; margin-bottom: 1rem; font-size: 1rem; }
    table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    th { text-align: left; padding: .5rem .75rem; color: #8b949e; border-bottom: 1px solid #21262d; font-weight: 600; }
    td { padding: .5rem .75rem; border-bottom: 1px solid #21262d; }
    .method { font-weight: 700; font-family: monospace; }
    .get { color: #3fb950; } .post { color: #d2a679; }
    .path { font-family: monospace; color: #79c0ff; }
  </style>
</head>
<body>
  <header>
    <h1>🔫 AI Minigun</h1>
    <span>Planner · Solver · Critic · Platform</span>
  </header>
  <main>
    <div class="grid">
      <div class="card"><h3>Platform</h3><div class="value">v0.1</div><div class="label">AI Minigun</div></div>
      <div class="card"><h3>Status</h3><div class="value" style="color:#3fb950">OK</div><div class="label">All systems operational</div></div>
      <div class="card"><h3>Agents</h3><div class="value">4</div><div class="label">Planner · Code · Infra · SRE · Data</div></div>
      <div class="card"><h3>MCP Tools</h3><div class="value">8</div><div class="label">Git · Docker · K8s · TF · Obs · Sec · Jira · Slack</div></div>
    </div>
    <div class="endpoint-list">
      <h2>API Endpoints</h2>
      <table>
        <thead><tr><th>Method</th><th>Path</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td class="method post">POST</td><td class="path">/v1/intents</td><td>Submit a high-level goal → returns TaskGraph</td></tr>
          <tr><td class="method get">GET</td><td class="path">/v1/tasks/{id}</td><td>Get task status</td></tr>
          <tr><td class="method get">GET</td><td class="path">/v1/graphs/{id}</td><td>Get full TaskGraph</td></tr>
          <tr><td class="method post">POST</td><td class="path">/v1/incidents</td><td>Create incident alert → remediation graph</td></tr>
          <tr><td class="method get">GET</td><td class="path">/v1/audit</td><td>List audit events</td></tr>
          <tr><td class="method get">GET</td><td class="path">/v1/health</td><td>Health check</td></tr>
          <tr><td class="method get">GET</td><td class="path">/docs</td><td>OpenAPI interactive documentation</td></tr>
        </tbody>
      </table>
    </div>
  </main>
</body>
</html>
"""
