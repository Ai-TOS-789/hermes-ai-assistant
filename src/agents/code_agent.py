"""AI Code Agent — code generation, review, and debugging."""
from __future__ import annotations

import re
from typing import Optional


class CodeAgent:
    """Agent specialized in code tasks."""

    def __init__(self):
        self._patterns = {
            "python": r"\.py$|\.pyi$|python",
            "javascript": r"\.js$|\.ts$|javascript|node",
            "yaml": r"\.yaml$|\.yml$",
            "toml": r"\.toml$",
        }

    def generate(self, description: str, language: str = "python") -> str:
        """Generate code based on description."""
        templates = {
            "python": f"# {description}\nimport asyncio\n\nasync def main():\n    pass\n\nif __name__ == '__main__':\n    asyncio.run(main())\n",
            "javascript": f"// {description}\nasync function main() {{\n  // TODO: implement\n}}\nmain();\n",
            "typescript": f"// {description}\ninterface Config {{}}\n\nasync function main(): Promise<void> {{\n  // TODO: implement\n}}\nmain();\n",
        }
        return templates.get(language, templates["python"])

    def review(self, code: str, language: str = "python") -> dict:
        """Review code for issues."""
        issues = []

        # Basic lint checks
        if language == "python":
            if "eval(" in code:
                issues.append({"severity": "error", "message": "Use of eval() is dangerous"})
            if "import *" in code:
                issues.append({"severity": "warning", "message": "Wildcard import — use explicit imports"})
            if len(code.split('\n')) > 500:
                issues.append({"severity": "info", "message": "File is long — consider splitting"})

        return {
            "language": language,
            "lines": len(code.split('\n')),
            "issues": issues,
            "score": max(0, 100 - len(issues) * 10),
        }

    def debug(self, code: str, error: str) -> dict:
        """Suggest fixes for code errors."""
        suggestions = []

        if "SyntaxError" in error:
            suggestions.append("Check for missing colons, parentheses, or indentation")
        if "NameError" in error:
            suggestions.append("Check variable names — undefined variable")
        if "ImportError" in error:
            suggestions.append("Check module installation and import path")
        if "TypeError" in error:
            suggestions.append("Check argument types and function signatures")

        return {
            "error": error,
            "suggestions": suggestions,
            "auto_fixable": len(suggestions) > 0,
        }

    def detect_language(self, filename: str, content: str = "") -> str:
        """Detect programming language from filename or content."""
        for lang, pattern in self._patterns.items():
            if re.search(pattern, filename, re.IGNORECASE):
                return lang
        if "def " in content or "import " in content:
            return "python"
        if "function " in content or "const " in content:
            return "javascript"
        return "unknown"
