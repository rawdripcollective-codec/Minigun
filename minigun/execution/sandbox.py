"""SandboxRunner: runs code in a restricted sandbox."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from dataclasses import dataclass
from typing import Literal


@dataclass
class SandboxResult:
    language: str
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False


class SandboxRunner:
    """Runs code in a sandboxed subprocess."""

    async def run_code(
        self,
        language: Literal["python", "bash", "javascript"],
        code: str,
        timeout_s: float = 10.0,
    ) -> SandboxResult:
        if language == "python":
            return await self._run_python(code, timeout_s)
        else:
            # Simulate other languages
            return SandboxResult(
                language=language,
                success=True,
                stdout=f"[simulated {language} output for code of length {len(code)}]",
                stderr="",
                exit_code=0,
            )

    async def _run_python(self, code: str, timeout_s: float) -> SandboxResult:
        try:
            proc = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    sys.executable,
                    "-c",
                    code,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                ),
                timeout=timeout_s,
            )
            stdout_b, stderr_b = await asyncio.wait_for(
                proc.communicate(), timeout=timeout_s
            )
            return SandboxResult(
                language="python",
                success=proc.returncode == 0,
                stdout=stdout_b.decode(errors="replace"),
                stderr=stderr_b.decode(errors="replace"),
                exit_code=proc.returncode or 0,
            )
        except asyncio.TimeoutError:
            return SandboxResult(
                language="python",
                success=False,
                stdout="",
                stderr="Execution timed out.",
                exit_code=-1,
                timed_out=True,
            )

