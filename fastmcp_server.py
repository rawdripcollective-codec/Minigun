from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
import uuid
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterable

from fastmcp import FastMCP

from policy import PolicyEngine


BASE_DIR = Path(__file__).resolve().parent
MAX_FILE_CHUNK_LINES = 400
MAX_SEARCH_RESULTS = 200
MAX_LIST_FILES = 500
MAX_COMMAND_TIMEOUT = 15

policy = PolicyEngine.from_env()

mcp = FastMCP(
    name="Minigun FastMCP Server",
    instructions=(
        "Utility tools for exploring the Minigun repository with scoped permissions."
    ),
    version="1.1.0",
)


def _active_principal_name() -> str:
    return os.getenv("MINIGUN_PRINCIPAL", "anonymous").strip() or "anonymous"


def _is_high_risk_enabled() -> bool:
    return os.getenv("MINIGUN_ENABLE_HIGH_RISK_TOOLS", "0").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def _audit_log(
    *,
    request_id: str,
    tool_name: str,
    principal: str,
    required_scopes: Iterable[str],
    allowed: bool,
    reason: str,
    latency_ms: int,
) -> None:
    event = {
        "event": "tool_invocation",
        "request_id": request_id,
        "tool": tool_name,
        "principal": principal,
        "required_scopes": sorted(set(required_scopes)),
        "allowed": allowed,
        "reason": reason,
        "latency_ms": latency_ms,
    }
    print(json.dumps(event, separators=(",", ":")))


def _permission_denied(tool_name: str, reason: str, request_id: str) -> str:
    return (
        f"Permission denied for tool '{tool_name}'. "
        f"Reason: {reason}. request_id={request_id}"
    )


def require_scopes(*required_scopes: str) -> Callable[[Callable[..., str]], Callable[..., str]]:
    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> str:
            request_id = str(uuid.uuid4())
            start = time.perf_counter()
            principal_name = _active_principal_name()
            principal = policy.principal(principal_name)
            decision = policy.authorize(principal, required_scopes)

            if not decision.allowed:
                elapsed = int((time.perf_counter() - start) * 1000)
                _audit_log(
                    request_id=request_id,
                    tool_name=func.__name__,
                    principal=principal.name,
                    required_scopes=required_scopes,
                    allowed=False,
                    reason=decision.reason,
                    latency_ms=elapsed,
                )
                return _permission_denied(func.__name__, decision.reason, request_id)

            result = func(*args, **kwargs)
            elapsed = int((time.perf_counter() - start) * 1000)
            _audit_log(
                request_id=request_id,
                tool_name=func.__name__,
                principal=principal.name,
                required_scopes=required_scopes,
                allowed=True,
                reason="ok",
                latency_ms=elapsed,
            )
            return result

        return wrapper

    return decorator


def _safe_resolve_repo_path(user_path: str) -> Path:
    candidate = (BASE_DIR / user_path).resolve()
    base_resolved = BASE_DIR.resolve()
    if not str(candidate).startswith(str(base_resolved)):
        raise ValueError("Path escapes repository root.")
    return candidate


@mcp.tool(description="Echo back a message for connection testing.")
@require_scopes("connectivity")
def echo(message: str) -> str:
    return message


@mcp.tool(description="Read the repository README for quick context.")
@require_scopes("read_repo")
def read_readme() -> str:
    readme_path = BASE_DIR / "README.md"
    if not readme_path.exists():
        return "README.md not found."
    return readme_path.read_text(encoding="utf-8")


@mcp.tool(description="List repository files for discovery.")
@require_scopes("inspect_repo")
def list_files(limit: int = 100) -> str:
    effective_limit = max(1, min(limit, MAX_LIST_FILES))
    entries = []
    for path in sorted(BASE_DIR.rglob("*")):
        if any(part.startswith(".") for part in path.relative_to(BASE_DIR).parts):
            continue
        if path.is_file():
            entries.append(str(path.relative_to(BASE_DIR)))
            if len(entries) >= effective_limit:
                break
    return "\n".join(entries) if entries else "No files found."


@mcp.tool(description="Read a specific file chunk from the repository.")
@require_scopes("read_repo")
def read_file_chunk(path: str, start_line: int = 1, max_lines: int = 80) -> str:
    safe_path = _safe_resolve_repo_path(path)
    if not safe_path.exists() or not safe_path.is_file():
        return "File not found."

    effective_max_lines = max(1, min(max_lines, MAX_FILE_CHUNK_LINES))
    start = max(1, start_line)

    lines = safe_path.read_text(encoding="utf-8").splitlines()
    if start > len(lines):
        return "Start line is beyond end of file."

    selected = lines[start - 1 : start - 1 + effective_max_lines]
    numbered = [f"{idx + start}: {line}" for idx, line in enumerate(selected)]
    return "\n".join(numbered)


@mcp.tool(description="Search text across repository files.")
@require_scopes("inspect_repo")
def search_repo(pattern: str, max_results: int = 20) -> str:
    if not pattern.strip():
        return "Pattern must not be empty."

    effective_max = max(1, min(max_results, MAX_SEARCH_RESULTS))
    matches: list[str] = []

    for path in sorted(BASE_DIR.rglob("*")):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(BASE_DIR).parts):
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_no, line in enumerate(content.splitlines(), start=1):
            if pattern in line:
                rel = path.relative_to(BASE_DIR)
                matches.append(f"{rel}:{line_no}: {line}")
                if len(matches) >= effective_max:
                    return "\n".join(matches)

    return "\n".join(matches) if matches else "No matches found."


@mcp.tool(description="Run a restricted shell command (disabled by default).")
@require_scopes("exec_commands")
def run_command(command: str, timeout_seconds: int = 5) -> str:
    if not _is_high_risk_enabled():
        return "This tool is disabled. Set MINIGUN_ENABLE_HIGH_RISK_TOOLS=1 to enable."

    allowed_prefixes = [
        prefix.strip()
        for prefix in os.getenv(
            "MINIGUN_COMMAND_ALLOWLIST", "git status,python --version"
        ).split(",")
        if prefix.strip()
    ]

    command = command.strip()
    if not any(command.startswith(prefix) for prefix in allowed_prefixes):
        return "Command denied by allowlist policy."

    effective_timeout = max(1, min(timeout_seconds, MAX_COMMAND_TIMEOUT))
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return f"Invalid command: {exc}"

    if not argv:
        return "Command must not be empty."

    completed = subprocess.run(
        argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        timeout=effective_timeout,
        check=False,
    )

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    return (
        f"exit_code={completed.returncode}\n"
        f"stdout:\n{stdout or '<empty>'}\n"
        f"stderr:\n{stderr or '<empty>'}"
    )


if __name__ == "__main__":
    mcp.run()
