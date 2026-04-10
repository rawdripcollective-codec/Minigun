"""CodegenApp: generates skeleton code from a specification."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CodegenSpec:
    language: str
    description: str
    class_name: str = "GeneratedClass"
    functions: list[str] | None = None


@dataclass
class CodegenResult:
    language: str
    code: str
    warnings: list[str]


_TEMPLATES: dict[str, str] = {
    "python": '''\
"""Auto-generated Python module: {description}"""


class {class_name}:
    """Implementation for: {description}"""

    def __init__(self) -> None:
        pass

{methods}
''',
    "typescript": '''\
// Auto-generated TypeScript module: {description}

export class {class_name} {{
    constructor() {{}}
{methods}
}}
''',
    "go": '''\
// Auto-generated Go package: {description}
package generated

type {class_name} struct{{}}

{methods}
''',
    "java": '''\
// Auto-generated Java class: {description}
public class {class_name} {{
{methods}
}}
''',
}

_DEFAULT_METHOD: dict[str, str] = {
    "python": "    def {fn}(self) -> None:\n        pass\n",
    "typescript": "    {fn}(): void {{\n    }}\n",
    "go": "func (r *{class_name}) {Fn}() {{}}\n",
    "java": "    public void {fn}() {{}}\n",
}


class CodegenApp:
    def generate(self, spec: CodegenSpec) -> CodegenResult:
        lang = spec.language.lower()
        template = _TEMPLATES.get(lang, _TEMPLATES["python"])
        method_tmpl = _DEFAULT_METHOD.get(lang, _DEFAULT_METHOD["python"])

        funcs = spec.functions or ["run", "validate"]
        methods_lines = []
        for fn in funcs:
            methods_lines.append(
                method_tmpl.format(
                    fn=fn,
                    Fn=fn.capitalize(),
                    class_name=spec.class_name,
                )
            )
        methods = "\n".join(methods_lines)

        code = template.format(
            description=spec.description,
            class_name=spec.class_name,
            methods=methods,
        )

        warnings = []
        if lang not in _TEMPLATES:
            warnings.append(f"Unknown language '{spec.language}'; used Python template.")

        return CodegenResult(language=spec.language, code=code, warnings=warnings)
