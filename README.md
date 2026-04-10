# Minigun

> **Autonomous DevOps + AGI software engineer platform**

Minigun is a Python 3.11+ platform that provides a fully autonomous software engineering loop: from understanding a high-level goal to planning, critiquing, executing, and continuously improving.

---

## Architecture

```
minigun/
├── cognition/       Layer 1 – Cognition (planner, critic, memory, intent, …)
├── tools/           Layer 2 – Tool Fabric (MCP tools: browser, git, cloud, vault, code_search)
├── execution/       Layer 3 – Execution Plane (workflows, queue, sandbox, audit, approvals)
├── apps/            Layer 4 – Apps (codegen, pr_review, testing, architecture, support, compliance, workflow_automation)
├── improvement/     Layer 5 – Self-Improvement (evaluation, telemetry, dataset, reward, synthetic, refresh)
├── kernel/          Agent Kernel (task_graph, agent, executor)
└── api/             REST/OpenAPI Surface (FastAPI routers + Pydantic v2 schemas)
```

### Layer 1 – Cognition
| Module | Class | Purpose |
|---|---|---|
| `planner.py` | `TaskPlanner` | Decomposes a goal into a `TaskGraph` DAG |
| `critic.py` | `PlanCritic` | Scores feasibility/risk, returns `CritiqueReport` |
| `memory.py` | `MemoryStore` | In-memory KV store with optional JSON persistence |
| `retrieval.py` | `RetrievalEngine` | Keyword-ranked retrieval over `MemoryStore` |
| `uncertainty.py` | `UncertaintyScorer` | Aleatoric/epistemic uncertainty for `TaskNode` |
| `policy.py` | `PolicyEngine` | Allow/deny rule evaluation |
| `causal_chain.py` | `CausalChainEngine` | Causal explanation chains |
| `intent.py` | `IntentInferencer` | Classifies free-text goals |
| `hypothesis.py` | `HypothesisTester` | Generates ranked hypotheses from observations |

### Layer 2 – Tool Fabric
All tools implement `MCPTool` and auto-register on import.

| Tool | Actions |
|---|---|
| `BrowserMCP` | navigate, screenshot, extract_text |
| `GitMCP` | clone, status, diff, commit, push |
| `CloudMCP` | list_resources, create_resource, delete_resource |
| `VaultMCP` | get_secret, set_secret, list_secrets |
| `CodeSearchMCP` | search, get_file |

### Layer 3 – Execution Plane
`WorkflowEngine`, `JobQueue`, `SandboxRunner`, `PermissionManager`, `RollbackManager`, `AuditLogger`, `ApprovalGate`

### Layer 4 – Apps
`CodegenApp`, `PRReviewApp`, `TestingApp`, `ArchitectureApp`, `SupportTriageApp`, `ComplianceApp`, `WorkflowAutomationApp`

### Layer 5 – Self-Improvement
`OfflineEvaluator`, `TelemetryCollector`, `DatasetMiner`, `RewardModel`, `SyntheticTaskGenerator`, `ModelRefreshController`

### Agent Kernel
`AgentKernel.run(goal)` orchestrates: infer intent → plan → critique (≤3 loops) → execute via `WorkflowEngine` → record telemetry.

---

## Quickstart

```bash
pip install -e ".[dev]"
uvicorn minigun.api.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive OpenAPI UI.

### Run tests

```bash
pytest tests/ -v
```

---

## API Reference Overview

| Prefix | Description |
|---|---|
| `GET /health` | Health check |
| `POST /api/v1/cognition/plan` | Decompose goal into task graph |
| `POST /api/v1/cognition/critique` | Critique a task graph |
| `POST /api/v1/cognition/memory` | Add to memory store |
| `GET /api/v1/cognition/memory/{key}` | Get memory entry |
| `POST /api/v1/cognition/memory/search` | Search memory |
| `POST /api/v1/cognition/retrieve` | Retrieval engine query |
| `POST /api/v1/cognition/intent` | Infer intent from goal |
| `POST /api/v1/cognition/uncertainty` | Score node uncertainty |
| `POST /api/v1/cognition/hypothesis` | Generate hypotheses |
| `POST /api/v1/cognition/policy/rules` | Add policy rule |
| `POST /api/v1/cognition/policy/evaluate` | Evaluate action against policy |
| `POST /api/v1/cognition/causal` | Build causal chain |
| `GET /api/v1/tools/` | List available tools |
| `POST /api/v1/tools/execute` | Execute a tool |
| `POST /api/v1/execution/workflows` | Create workflow |
| `POST /api/v1/execution/workflows/{id}/run` | Run workflow |
| `POST /api/v1/execution/jobs` | Enqueue job |
| `POST /api/v1/execution/sandbox` | Run code in sandbox |
| `POST /api/v1/execution/permissions/grant` | Grant permission |
| `POST /api/v1/execution/permissions/check` | Check permission |
| `POST /api/v1/execution/rollback/checkpoint` | Create checkpoint |
| `POST /api/v1/execution/rollback/restore` | Restore checkpoint |
| `POST /api/v1/execution/audit` | Record audit entry |
| `POST /api/v1/execution/approvals` | Request approval |
| `POST /api/v1/apps/codegen` | Generate code |
| `POST /api/v1/apps/pr-review` | Review pull request diff |
| `POST /api/v1/apps/testing` | Generate test suite |
| `POST /api/v1/apps/architecture` | Synthesize architecture |
| `POST /api/v1/apps/support` | Triage support ticket |
| `POST /api/v1/apps/compliance` | Run compliance check |
| `POST /api/v1/apps/workflow-automation` | Create automation |
| `POST /api/v1/improvement/evaluate` | Evaluate task run |
| `POST /api/v1/improvement/telemetry/event` | Record telemetry event |
| `POST /api/v1/improvement/dataset/mine` | Mine dataset |
| `POST /api/v1/improvement/reward/score` | Score trajectory |
| `POST /api/v1/improvement/synthetic/generate` | Generate synthetic tasks |
| `POST /api/v1/improvement/refresh/schedule` | Schedule model refresh |
| `POST /api/v1/kernel/run` | Run agent kernel end-to-end |

---

## License

MIT