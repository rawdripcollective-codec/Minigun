"""TestingApp: generates test suites from code."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class TestCase:
    name: str
    code: str
    description: str


@dataclass
class TestSuite:
    language: str
    test_cases: list[TestCase]
    framework: str


_FUNCTION_RE = re.compile(r"^\s*(?:def|async def)\s+(\w+)\s*\(", re.MULTILINE)
_CLASS_RE = re.compile(r"^\s*class\s+(\w+)", re.MULTILINE)


def _python_test(func_name: str) -> TestCase:
    return TestCase(
        name=f"test_{func_name}",
        code=(
            f"def test_{func_name}():\n"
            f"    # TODO: implement test for {func_name}\n"
            f"    result = {func_name}()\n"
            f"    assert result is not None\n"
        ),
        description=f"Auto-generated test for {func_name}",
    )


class TestingApp:
    def generate_tests(self, code: str, language: str) -> TestSuite:
        lang = language.lower()
        test_cases: list[TestCase] = []

        if lang == "python":
            funcs = [m.group(1) for m in _FUNCTION_RE.finditer(code) if not m.group(1).startswith("_")]
            if not funcs:
                funcs = ["main"]
            for fn in funcs[:10]:
                test_cases.append(_python_test(fn))
            framework = "pytest"
        else:
            # Generic placeholder for other languages
            test_cases.append(
                TestCase(
                    name="test_placeholder",
                    code=f"// Test for {language} code\n// TODO: implement",
                    description="Auto-generated placeholder test",
                )
            )
            framework = "generic"

        return TestSuite(language=language, test_cases=test_cases, framework=framework)
