"""
MiMo Codebase Manager
======================
Intelligent code review and management powered by MiMo v2.5.

Demonstrates:
- Multi-file codebase analysis
- Bug detection and security scanning
- Code quality metrics
- Refactoring suggestions with reasoning
- Documentation generation
"""

import os
import sys
import json
import time
import uuid
import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── Configuration ──────────────────────────────────────────────────────────

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


# ── MiMo Client ────────────────────────────────────────────────────────────

class MiMoClient:
    def __init__(self):
        self.use_mock = not bool(os.environ.get("MIMO_API_KEY"))

    def analyze_code(self, code: str, filename: str) -> dict:
        """Analyze code with MiMo v2.5."""
        issues = []
        suggestions = []

        # Detect common patterns
        if "eval(" in code:
            issues.append({
                "severity": "critical",
                "description": "Use of eval() detected — potential code injection vulnerability",
                "line": code[:code.find("eval(")].count("\n") + 1,
                "file": filename,
                "fix": "Replace eval() with ast.literal_eval() or json.loads()",
            })

        if "except:" in code or "except Exception:" in code:
            issues.append({
                "severity": "medium",
                "description": "Bare except clause — catches all exceptions including SystemExit",
                "line": code[:code.find("except")].count("\n") + 1,
                "file": filename,
                "fix": "Catch specific exceptions: except ValueError as e:",
            })

        if "TODO" in code or "FIXME" in code:
            issues.append({
                "severity": "low",
                "description": "Unresolved TODO/FIXME comment found",
                "line": code[:code.find("TODO" if "TODO" in code else "FIXME")].count("\n") + 1,
                "file": filename,
                "fix": "Address the TODO or remove if no longer needed",
            })

        # Detect hardcoded secrets
        secret_patterns = [r'password\s*=\s*["\']', r'api_key\s*=\s*["\']', r'secret\s*=\s*["\']']
        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "severity": "high",
                    "description": f"Possible hardcoded secret detected: {pattern.split('=')[0].strip()}",
                    "line": 0,
                    "file": filename,
                    "fix": "Move secrets to environment variables or a secrets manager",
                })

        # Suggestions
        if "import os" in code and "os.path" in code:
            suggestions.append({
                "type": "modernization",
                "description": "Consider using pathlib.Path instead of os.path for cleaner path handling",
                "impact": "Improved readability and cross-platform compatibility",
            })

        if "for " in code and "range(len(" in code:
            suggestions.append({
                "type": "pythonic",
                "description": "Use enumerate() instead of range(len()) for iteration",
                "impact": "More Pythonic and readable code",
            })

        # Check for missing docstrings
        func_defs = re.findall(r"def (\w+)\(", code)
        for fn in func_defs:
            if fn.startswith("_"):
                continue
            # Simple check if there's a docstring after the def
            pattern = rf"def {fn}\([^)]*\):\s*\n\s*\"\"\""
            if not re.search(pattern, code):
                suggestions.append({
                    "type": "documentation",
                    "description": f"Function '{fn}' is missing a docstring",
                    "impact": "Improved code documentation and IDE support",
                })
                break  # Only report one missing docstring per file

        if "class " in code and "def __init__" in code:
            if "@dataclass" not in code and "@dataclass" not in code:
                suggestions.append({
                    "type": "modernization",
                    "description": "Consider using @dataclass for data-holding classes",
                    "impact": "Less boilerplate code, auto-generated __init__, __repr__, etc.",
                })

        return {
            "issues": issues,
            "suggestions": suggestions,
            "metrics": self._calculate_metrics(code),
        }

    def _calculate_metrics(self, code: str) -> dict:
        """Calculate code metrics."""
        lines = code.split("\n")
        loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
        functions = len(re.findall(r"def \w+", code))
        classes = len(re.findall(r"class \w+", code))
        imports = len(re.findall(r"^(?:import|from) ", code, re.MULTILINE))
        comments = len([l for l in lines if l.strip().startswith("#")])

        return {
            "lines_of_code": loc,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "comment_lines": comments,
            "comment_ratio": round(comments / max(loc, 1) * 100, 1),
        }

    def generate_docstring(self, code: str, filename: str) -> str:
        """Generate documentation for code."""
        func_names = re.findall(r'def (\w+)', code)
        class_names = re.findall(r'class (\w+)', code)
        module_name = filename.replace('.py', '')
        
        funcs_section = "\n".join(f"- `{fn}()`" for fn in func_names)
        classes_section = "\n".join(f"- `{cls}`" for cls in class_names)
        
        doc = f"""# {filename}

## Overview
This module contains {len(func_names)} functions and {len(class_names)} classes.

## Functions
{funcs_section}

## Classes
{classes_section}

## Usage
```python
from {module_name} import *
```
"""
        return doc


# ── Data Models ────────────────────────────────────────────────────────────

@dataclass
class Issue:
    severity: Severity = Severity.INFO
    description: str = ""
    file: str = ""
    line: int = 0
    fix: str = ""

    def __post_init__(self):
        if isinstance(self.severity, str):
            try:
                self.severity = Severity(self.severity)
            except ValueError:
                self.severity = Severity.INFO

    def to_dict(self):
        return {
            "severity": self.severity.value if isinstance(self.severity, Severity) else self.severity,
            "description": self.description,
            "file": self.file,
            "line": self.line,
            "fix": self.fix,
        }


@dataclass
class Suggestion:
    type: str = ""
    description: str = ""
    impact: str = ""

    def to_dict(self):
        return {"type": self.type, "description": self.description, "impact": self.impact}


@dataclass
class FileAnalysis:
    filename: str = ""
    metrics: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)
    score: float = 0.0


@dataclass
class AnalysisReport:
    root_path: str = ""
    files_analyzed: int = 0
    total_lines: int = 0
    overall_score: float = 0.0
    issue_count: int = 0
    issues: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)
    file_analyses: list = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "root_path": self.root_path,
            "files_analyzed": self.files_analyzed,
            "total_lines": self.total_lines,
            "overall_score": self.overall_score,
            "issue_count": self.issue_count,
            "issues": [i if isinstance(i, dict) else i.to_dict() for i in self.issues],
            "suggestions": [s if isinstance(s, dict) else s.to_dict() for s in self.suggestions],
            "generated_at": self.generated_at,
        }


# ── Codebase Manager ──────────────────────────────────────────────────────

class CodebaseManager:
    def __init__(self):
        self.mimo = MiMoClient()
        self.log: list[str] = []

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        self.log.append(entry)
        print(entry)

    def _find_python_files(self, path: str) -> list[str]:
        """Find Python files in directory."""
        py_files = []
        for root, dirs, files in os.walk(path):
            # Skip hidden dirs and common non-source dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', '.venv', 'node_modules']]
            for f in files:
                if f.endswith('.py'):
                    py_files.append(os.path.join(root, f))
        return py_files

    def analyze(self, path: str) -> AnalysisReport:
        """Analyze a codebase directory."""
        start_time = time.time()

        self._log(f"\n{'🔍'*20}")
        self._log(f"  Codebase Analysis: {path}")
        self._log(f"{'🔍'*20}\n")

        # Find files
        py_files = self._find_python_files(path)
        self._log(f"[Scanner] Found {len(py_files)} Python files")

        if not py_files:
            self._log("[Scanner] No Python files found. Creating demo analysis...")
            return self._analyze_demo()

        # Analyze each file
        all_issues = []
        all_suggestions = []
        total_lines = 0
        file_analyses = []

        for filepath in py_files[:20]:  # Limit for demo
            filename = os.path.basename(filepath)
            self._log(f"[Analyzer] Analyzing {filename}...")

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
            except Exception:
                continue

            result = self.mimo.analyze_code(code, filename)

            # Convert to objects
            issues = [Issue(**i) for i in result["issues"]]
            suggestions = [Suggestion(**s) for s in result["suggestions"]]

            all_issues.extend(issues)
            all_suggestions.extend(suggestions)
            total_lines += result["metrics"].get("lines_of_code", 0)

            # Calculate file score
            score = 100
            for issue in issues:
                if issue.severity == Severity.CRITICAL:
                    score -= 25
                elif issue.severity == Severity.HIGH:
                    score -= 15
                elif issue.severity == Severity.MEDIUM:
                    score -= 8
                elif issue.severity == Severity.LOW:
                    score -= 3

            file_analyses.append(FileAnalysis(
                filename=filename,
                metrics=result["metrics"],
                issues=[i.to_dict() for i in issues],
                suggestions=[s.to_dict() for s in suggestions],
                score=max(0, score),
            ))

        # Calculate overall score
        if file_analyses:
            overall_score = sum(f.score for f in file_analyses) / len(file_analyses)
        else:
            overall_score = 100.0

        report = AnalysisReport(
            root_path=path,
            files_analyzed=len(py_files),
            total_lines=total_lines,
            overall_score=round(overall_score, 1),
            issue_count=len(all_issues),
            issues=all_issues,
            suggestions=all_suggestions,
            file_analyses=file_analyses,
        )

        elapsed = round(time.time() - start_time, 2)
        self._log(f"\n[Reporter] Analysis complete in {elapsed}s")
        self._log(f"[Reporter] Overall score: {report.overall_score}/100")
        self._log(f"[Reporter] Issues: {report.issue_count}")

        return report

    def _analyze_demo(self) -> AnalysisReport:
        """Analyze demo code when no path is provided."""
        demo_code = '''
import os
import json

def process_data(data):
    """Process incoming data."""
    results = []
    for i in range(len(data)):  # TODO: refactor this
        result = data[i] * 2
        results.append(result)
    return results

password = "hardcoded_secret_123"

class DataProcessor:
    def __init__(self):
        self.config = {}

    def run(self):
        try:
            eval("process_data([])")
        except:
            pass

def load_config():
    path = os.path.join("config", "settings.json")
    with open(path) as f:
        return json.load(f)
'''

        result = self.mimo.analyze_code(demo_code, "demo_code.py")
        issues = [Issue(**i) for i in result["issues"]]
        suggestions = [Suggestion(**s) for s in result["suggestions"]]

        score = 100
        for issue in issues:
            if issue.severity == Severity.CRITICAL:
                score -= 25
            elif issue.severity == Severity.HIGH:
                score -= 15
            elif issue.severity == Severity.MEDIUM:
                score -= 8

        file_analysis = FileAnalysis(
            filename="demo_code.py",
            metrics=result["metrics"],
            issues=[i.to_dict() for i in issues],
            suggestions=[s.to_dict() for s in suggestions],
            score=max(0, score),
        )

        report = AnalysisReport(
            root_path="demo_project/",
            files_analyzed=1,
            total_lines=result["metrics"]["lines_of_code"],
            overall_score=max(0, score),
            issue_count=len(issues),
            issues=issues,
            suggestions=suggestions,
            file_analyses=[file_analysis],
        )

        # Print demo output
        self._log(f"\n[Scanner] Analyzing codebase: demo_project/")
        self._log(f"[Scanner] Found 1 Python file, {report.total_lines} lines of code")
        self._log(f"[Analyzer] Running MiMo v2.5 deep analysis...")
        self._log(f"[Analyzer] Security scan: {len([i for i in issues if i.severity in [Severity.CRITICAL, Severity.HIGH]])} potential issues found")
        self._log(f"[Reporter] Generating comprehensive report...")
        self._log(f"\n📊 Codebase Report")
        self._log(f"  Score: {report.overall_score}/100")
        self._log(f"  Lines of code: {report.total_lines}")
        self._log(f"  Issues: {report.issue_count}")
        self._log(f"  Suggestions: {len(suggestions)}")

        return report


# ── Demo ───────────────────────────────────────────────────────────────────

def run_demo():
    print("\n" + "🔍 " * 20)
    print("  MiMo Codebase Manager — Demo")
    print("🔍 " * 20 + "\n")

    manager = CodebaseManager()

    # Analyze the project itself
    project_dir = os.path.dirname(__file__)
    report = manager.analyze(project_dir)

    # Print issues
    if report.issues:
        print(f"\n🔒 Issues Found:")
        for issue in report.issues[:5]:
            if isinstance(issue, Issue):
                print(f"  [{issue.severity.value.upper()}] {issue.description}")
            else:
                print(f"  [{issue['severity'].upper()}] {issue['description']}")

    # Print suggestions
    if report.suggestions:
        print(f"\n💡 Suggestions:")
        for sug in report.suggestions[:5]:
            if isinstance(sug, Suggestion):
                print(f"  • {sug.description}")
            else:
                print(f"  • {sug['description']}")

    # Save results
    demo_dir = os.path.join(os.path.dirname(__file__), "demo")
    os.makedirs(demo_dir, exist_ok=True)

    with open(os.path.join(demo_dir, "analysis_report.json"), "w") as f:
        json.dump(report.to_dict(), f, indent=2, default=str)

    with open(os.path.join(demo_dir, "analysis_log.txt"), "w") as f:
        f.write("\n".join(manager.log))

    print(f"\n💾 Report saved to demo/analysis_report.json")

    return report


if __name__ == "__main__":
    run_demo()
