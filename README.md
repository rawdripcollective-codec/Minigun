# Minigun

This repository hosts a FastMCP server with scoped tool permissions for exploring and operating on the repo.

## Setup
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies: `pip install -r requirements.txt`

## Running the server
Start the MCP server from the repository root:

```bash
python fastmcp_server.py
```

## Permission model
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

## Tool catalog
### Low-risk tools
- `echo(message: str) -> str` *(scope: `connectivity`)*
- `read_readme() -> str` *(scope: `read_repo`)*
- `list_files(limit: int = 100) -> str` *(scope: `inspect_repo`)*
- `read_file_chunk(path: str, start_line: int = 1, max_lines: int = 80) -> str` *(scope: `read_repo`)*
- `search_repo(pattern: str, max_results: int = 20) -> str` *(scope: `inspect_repo`)*

### High-risk tool (disabled by default)
- `run_command(command: str, timeout_seconds: int = 5) -> str` *(scope: `exec_commands`)*

Enable high-risk tools explicitly:

```bash
export MINIGUN_ENABLE_HIGH_RISK_TOOLS=1
export MINIGUN_COMMAND_ALLOWLIST='git status,python --version'
```

## Observability
Every tool invocation emits a structured JSON audit log to stdout with principal, required scopes, allow/deny decision, reason, request ID, and latency.

## Connecting via MCP clients
`mcp.json` defines how to launch this server for MCP-compatible clients. Point your client at this file or copy the `minigun-fastmcp` entry into your client configuration.

For example:
- Claude Desktop: merge the `minigun-fastmcp` block into `~/.config/anthropic/claude_desktop_config.json` under `mcpServers`.
- MCP Inspector: run it with the `--config mcp.json` flag so it can start the server with the provided command.
