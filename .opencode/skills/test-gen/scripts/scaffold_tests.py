#!/usr/bin/env python3
"""
scaffold_tests.py — Analyze a source file and scaffold a test file skeleton.
Usage: python3 scaffold_tests.py <source_file>
"""

import ast
import sys
import os
import re
from pathlib import Path
from datetime import date

def detect_language(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    return {".py": "python", ".js": "javascript", ".ts": "typescript",
            ".jsx": "javascript", ".tsx": "typescript"}.get(ext, "unknown")


# ── Python AST analysis ───────────────────────────────────────────────────────

def analyze_python(source: str):
    tree = ast.parse(source)
    functions = []
    classes   = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            args = [a.arg for a in node.args.args if a.arg != "self"]
            returns = ""
            if node.returns:
                try:
                    returns = ast.unparse(node.returns)
                except Exception:
                    pass
            docstring = ast.get_docstring(node) or ""
            functions.append({"name": node.name, "args": args,
                               "returns": returns, "doc": docstring})
        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    args = [a.arg for a in item.args.args if a.arg != "self"]
                    methods.append({"name": item.name, "args": args})
            classes.append({"name": node.name, "methods": methods})

    return functions, classes


def generate_pytest(filepath: str, source: str) -> str:
    module_name = Path(filepath).stem
    functions, classes = analyze_python(source)

    lines = [
        f'"""',
        f'Tests for {Path(filepath).name}',
        f'Generated: {date.today().isoformat()}',
        f'"""',
        f'import pytest',
        f'from unittest.mock import MagicMock, patch, call',
        f'from {module_name} import {", ".join([f["name"] for f in functions[:8]] + [c["name"] for c in classes[:4]])}',
        f'',
        f'',
    ]

    for fn in functions:
        fn_name = fn["name"]
        args    = fn["args"]
        mock_args = ", ".join([f'"{a}_value"' if "str" in fn.get("doc","").lower() else "1"
                               for a in args])
        lines += [
            f'# ── {fn_name} ─────────────────────────────────────────────────',
            f'',
            f'class Test{fn_name.title().replace("_", "")}:',
            f'',
            f'    def test_{fn_name}_happy_path(self):',
            f'        """Basic usage returns expected result."""',
            f'        result = {fn_name}({mock_args})',
            f'        assert result is not None  # TODO: assert specific return value',
            f'',
            f'    def test_{fn_name}_returns_correct_type(self):',
            f'        """Return type matches expected."""',
            f'        result = {fn_name}({mock_args})',
            f'        # TODO: assert isinstance(result, expected_type)',
            f'        pass',
            f'',
            f'    def test_{fn_name}_with_empty_input(self):',
            f'        """Handles empty/None/zero input gracefully."""',
            f'        with pytest.raises((ValueError, TypeError)):',
            f'            {fn_name}({", ".join(["None"] * max(len(args), 1))})',
            f'',
            f'    def test_{fn_name}_edge_case_boundary(self):',
            f'        """Boundary values behave correctly."""',
            f'        # TODO: test min/max boundary values',
            f'        pass',
            f'',
        ]

    for cls in classes:
        lines += [
            f'# ── {cls["name"]} ─────────────────────────────────────────────────',
            f'',
            f'class Test{cls["name"]}:',
            f'',
            f'    @pytest.fixture',
            f'    def instance(self):',
            f'        """Create a fresh instance for each test."""',
            f'        return {cls["name"]}()  # TODO: add required constructor args',
            f'',
        ]
        for method in cls["methods"]:
            args = ", ".join(["self.instance"] + [f'"{a}"' for a in method["args"]])
            lines += [
                f'    def test_{method["name"]}_basic(self, instance):',
                f'        result = instance.{method["name"]}({", ".join([f\'"{a}"\' for a in method["args"]])})',
                f'        assert result is not None  # TODO: assert specific value',
                f'',
                f'    def test_{method["name"]}_error_handling(self, instance):',
                f'        with pytest.raises(Exception):',
                f'            instance.{method["name"]}({", ".join(["None"] * max(len(method["args"]), 1))})',
                f'',
            ]

    lines += [
        f'# ── Integration / parametrize examples ───────────────────────────────',
        f'',
        f'@pytest.mark.parametrize("input,expected", [',
        f'    # (input_value, expected_output),',
        f'    # TODO: fill in parametrized cases',
        f'])',
        f'def test_parametrized_example(input, expected):',
        f'    pass',
    ]

    return "\n".join(lines)


# ── JS/TS scaffold ────────────────────────────────────────────────────────────

def extract_js_functions(source: str):
    patterns = [
        r'export\s+(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)',
        r'export\s+const\s+(\w+)\s*=\s*(?:async\s+)?\(?([^)]*)\)?\s*=>',
        r'(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)',
    ]
    functions = []
    for pat in patterns:
        for m in re.finditer(pat, source):
            name = m.group(1)
            args = [a.strip().split(":")[0].strip() for a in m.group(2).split(",") if a.strip()]
            if name not in [f["name"] for f in functions]:
                functions.append({"name": name, "args": args})
    return functions


def generate_jest(filepath: str, source: str) -> str:
    module_name = Path(filepath).stem
    functions   = extract_js_functions(source)
    imports     = ", ".join([f["name"] for f in functions[:6]]) or "default"

    lines = [
        f'/**',
        f' * Tests for {Path(filepath).name}',
        f' * Generated: {date.today().isoformat()}',
        f' */',
        f"import {{ {imports} }} from './{module_name}';",
        f'',
    ]

    for fn in functions:
        fn_name  = fn["name"]
        args     = fn["args"]
        mock_args = ", ".join([f'"{a}"' for a in args])

        lines += [
            f"describe('{fn_name}', () => {{",
            f"  it('returns expected result for valid input', () => {{",
            f"    const result = {fn_name}({mock_args});",
            f"    expect(result).toBeDefined(); // TODO: assert specific value",
            f"  }});",
            f"",
            f"  it('throws on invalid input', () => {{",
            f"    expect(() => {fn_name}({', '.join(['null'] * max(len(args), 1))})).toThrow();",
            f"  }});",
            f"",
            f"  it('handles edge case: empty string', () => {{",
            f"    // TODO: test empty string / zero / empty array",
            f"    expect(true).toBe(true);",
            f"  }});",
            f"",
            f"  it.each([",
            f"    // [input, expected],",
            f"    // TODO: parametrized cases",
            f"  ])('parametrized: %s => %s', (input, expected) => {{",
            f"    // expect({fn_name}(input)).toBe(expected);",
            f"  }});",
            f"}});",
            f"",
        ]

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: scaffold_tests.py <source_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found")
        sys.exit(1)

    source   = Path(filepath).read_text()
    lang     = detect_language(filepath)
    src_path = Path(filepath)

    if lang == "python":
        output_path = src_path.parent / f"test_{src_path.stem}.py"
        content = generate_pytest(filepath, source)
    elif lang in ("javascript", "typescript"):
        ext = ".test.ts" if lang == "typescript" else ".test.js"
        output_path = src_path.parent / f"{src_path.stem}{ext}"
        content = generate_jest(filepath, source)
    else:
        print(f"Unsupported language for {filepath} — scaffold manually.")
        sys.exit(1)

    output_path.write_text(content)
    print(f"✅  Scaffolded test file → {output_path}")
    print(f"   Review and fill in TODO items before running.")


if __name__ == "__main__":
    main()
