# Minigun

This repository hosts a minimal FastMCP server that exposes small helper tools for exploring the repo.

## Setup
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies: `pip install -r requirements.txt`

## Running the server
Start the MCP server from the repository root:

```bash
python fastmcp_server.py
```

The server currently offers:
- `echo(message: str) -> str` for quick connectivity checks.
- `read_readme() -> str` to return the repository README contents.

## Connecting via MCP clients
`mcp.json` defines how to launch this server for MCP-compatible clients. Point your client at this file or copy the `minigun-fastmcp` entry into your client configuration. For example:
- Claude Desktop: merge the `minigun-fastmcp` block into `~/.config/anthropic/claude_desktop_config.json` under `mcpServers`.
- MCP Inspector: run it with the `--config mcp.json` flag so it can start the server with the provided command.
