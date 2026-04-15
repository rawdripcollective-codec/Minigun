# 🔫 AI Minigun

> A layered **Planner → Solver → Critic** agent platform that accepts high-level goals, plans multi-step task graphs, executes them with specialised domain agents, verifies the results, and continuously improves itself.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1 – Interface & Orchestration                            │
│  FastAPI Gateway · Bearer Auth · HTML Dashboard · Task Library  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│  Layer 2 – Agent Kernel & Memory                                │
│  PlannerAgent · CodeSolver · InfraSolver · SRESolver · Data     │
│  CriticAgent · SafetyEngine · MemoryService · WorldModel        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│  Layer 3 – MCP Tool Fabric                                      │
│  Git · Docker · Kubernetes · Terraform · Observability          │
│  Security · Jira · Slack   (MCPRegistry)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│  Layer 4 – Execution & Safety Plane                             │
│  WorkflowEngine · VerificationHub · RiskEngine                  │
│  IncidentEngine · AuditService                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│  Layer 5 – Self-Improvement & AGI R&D                           │
│  EvalHarness · TelemetryService · SelfImprovementOrchestrator   │
└─────────────────────────────────────────────────────────────────┘
```

### Key Flows

**Build Feature**
```
POST /v1/intents  →  PlannerAgent  →  TaskGraph
→  WorkflowEngine (CodeSolver)  →  VerificationHub  →  RiskEngine
→  canary deploy via KubernetesMCP  →  audit log
```

**Incident Remediation**
```
POST /v1/incidents  →  IncidentEngine.ingest  →  WorldModel.correlate
→  PlannerAgent  →  remediation TaskGraph  →  WorkflowEngine (SRESolver)
→  VerificationHub  →  RiskEngine gate  →  postmortem
```

---

## Quickstart

### Docker Compose

```bash
# Build and start
docker compose up --build

# Test the health endpoint
curl http://localhost:8000/v1/health

# Open the dashboard
open http://localhost:8000/
```

### Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run the API
uvicorn minigun.api.app:app --reload

# Run tests
pytest tests/ -v
```

---

## API Reference

All endpoints except `/`, `/v1/health`, and `/docs` require:
```
Authorization: Bearer <MINIGUN_API_SECRET_KEY>
```

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/intents` | Submit a high-level goal → returns executed `TaskGraph` |
| `GET`  | `/v1/tasks/{id}` | Get task status |
| `GET`  | `/v1/graphs/{id}` | Get full `TaskGraph` |
| `POST` | `/v1/incidents` | Create incident alert → returns remediation `TaskGraph` |
| `GET`  | `/v1/audit` | List audit events |
| `GET`  | `/v1/health` | Health check |
| `GET`  | `/` | HTML dashboard |
| `GET`  | `/docs` | OpenAPI interactive docs |

### Example – Submit an intent

```bash
curl -X POST http://localhost:8000/v1/intents \
  -H "Authorization: Bearer changeme" \
  -H "Content-Type: application/json" \
  -d '{"intent": "build feature: user authentication", "context": {"repo": "minigun"}, "priority": "high"}'
```

### Example – Create an incident

```bash
curl -X POST http://localhost:8000/v1/incidents \
  -H "Authorization: Bearer changeme" \
  -H "Content-Type: application/json" \
  -d '{"severity": "P1", "source": "prometheus", "message": "High error rate on api service", "metadata": {"service": "api"}}'
```

---

## Configuration

| Env var | Default | Description |
|---------|---------|-------------|
| `MINIGUN_API_SECRET_KEY` | `changeme` | Bearer token for API auth |
| `MINIGUN_MAX_RETRIES` | `3` | Max task retry attempts |
| `MINIGUN_LOG_LEVEL` | `INFO` | Python logging level |

---

## Project Layout

```
minigun/
├── api/            FastAPI app, routers, auth middleware
├── agents/         Planner, Solvers, Critic, Safety
├── memory/         MemoryService, WorldModelService
├── mcp/            MCP tool fabric (Git, Docker, K8s, …)
├── execution/      WorkflowEngine, VerificationHub, RiskEngine, …
├── improvement/    EvalHarness, Telemetry, SelfImprovement
├── models/         Shared Pydantic models
└── config.py       Pydantic-settings configuration
tests/              pytest test suite
```

---

## FastMCP Server

This repository also hosts a FastMCP server with scoped tool permissions for exploring and operating on the repo.

### Setup
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies: `pip install -r requirements.txt`

### Running the server
Start the MCP server from the repository root:

```bash
python fastmcp_server.py
```

### Permission model
The server enforces scope-based authorization per tool. The active principal is selected via env var:

- `MINIGUN_PRINCIPAL` (default: `anonymous`)
- `MINIGUN_POLICY_MODE`: `dev` or `hardened` (default: `hardened`)
- `MINIGUN_POLICY_PRINCIPALS`: JSON map of principal to scopes (optional)

Example:

```bash
export MINIGUN_POLICY_MODE=dev
export MINIGUN_PRINCIPAL=ci
export MINIGUN_POLICY_PRINCIPALS='{"ci": ["connectivity", "read_repo", "inspect_repo", "exec_commands"]}'
```

### Tool catalog
#### Low-risk tools
- `echo(message: str) -> str` *(scope: `connectivity`)*
- `read_readme() -> str` *(scope: `read_repo`)*
- `list_files(limit: int = 100) -> str` *(scope: `inspect_repo`)*
- `read_file_chunk(path: str, start_line: int = 1, max_lines: int = 80) -> str` *(scope: `read_repo`)*
- `search_repo(pattern: str, max_results: int = 20) -> str` *(scope: `inspect_repo`)*

#### High-risk tool (disabled by default)
- `run_command(command: str, timeout_seconds: int = 5) -> str` *(scope: `exec_commands`)*

Enable high-risk tools explicitly:

```bash
export MINIGUN_ENABLE_HIGH_RISK_TOOLS=1
export MINIGUN_COMMAND_ALLOWLIST='git status,python --version'
```

### Observability
Every tool invocation emits a structured JSON audit log to stdout with principal, required scopes, allow/deny decision, reason, request ID, and latency.

### Connecting via MCP clients
`mcp.json` defines how to launch this server for MCP-compatible clients. Point your client at this file or copy the `minigun-fastmcp` entry into your client configuration.

For example:
- Claude Desktop: merge the `minigun-fastmcp` block into `~/.config/anthropic/claude_desktop_config.json` under `mcpServers`.
- MCP Inspector: run it with the `--config mcp.json` flag so it can start the server with the provided command.
