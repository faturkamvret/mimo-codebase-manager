# MiMo Codebase Manager

> 🔍 Intelligent code review and management powered by MiMo v2.5

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![MiMo](https://img.shields.io/badge/MiMo-v2.5-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

An intelligent code review system that analyzes codebases, detects issues, suggests improvements, and generates comprehensive reports using MiMo v2.5's deep reasoning capabilities.

**Key capabilities:**
- Multi-file codebase analysis
- Bug detection and security vulnerability scanning
- Code quality metrics and scoring
- Refactoring suggestions with reasoning
- Documentation generation
- Dependency analysis

## Architecture

```
┌──────────────────────────────────────────────────────┐
│              Codebase Manager                          │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Scanner  │  │ Analyzer │  │   Report Gen     │   │
│  │  Agent   │  │  (MiMo)  │  │    (MiMo)        │   │
│  └─────┬────┘  └─────┬────┘  └────────┬─────────┘   │
│        │              │                 │              │
│  ┌─────▼──────────────▼─────────────────▼────────┐   │
│  │              Code Analysis Pipeline             │   │
│  │  [Parse] → [AST] → [Metrics] → [Issues] →     │   │
│  │  [Suggestions] → [Report]                       │   │
│  └───────────────────────────────────────────────┘   │
│        │              │                 │              │
│  ┌─────▼──┐    ┌─────▼──┐    ┌────────▼────────┐   │
│  │ Syntax │    │Security│    │   Quality       │   │
│  │Checker │    │ Scanner│    │   Metrics       │   │
│  └────────┘    └────────┘    └─────────────────┘   │
└──────────────────────────────────────────────────────┘
```

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/mimo-codebase-manager.git
cd mimo-codebase-manager

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

export MIMO_API_KEY="your-api-key"  # Optional

python main.py --demo
```

## Usage

```python
from codebase_manager import CodebaseManager

manager = CodebaseManager()

# Analyze a directory
report = manager.analyze("/path/to/your/project")

print(f"Overall Score: {report.overall_score}/100")
print(f"Issues found: {report.issue_count}")
print(f"Suggestions: {len(report.suggestions)}")

# Get detailed suggestions
for suggestion in report.suggestions[:5]:
    print(f"  [{suggestion.severity}] {suggestion.description}")
```

## Demo

```bash
python main.py --demo
```

Expected output:

```
[Scanner] Analyzing codebase: demo_project/
[Scanner] Found 12 Python files, 1,847 lines of code
[Analyzer] Running MiMo v2.5 deep analysis...
[Analyzer] Security scan: 2 potential issues found
[Analyzer] Code quality analysis complete
[Reporter] Generating comprehensive report...

📊 Codebase Report
  Score: 87/100
  Files analyzed: 12
  Lines of code: 1,847
  Issues: 2 critical, 5 warnings, 8 info
  Suggestions: 15 improvements identified

🔒 Security Issues:
  1. [HIGH] SQL injection risk in db.py:42
  2. [MED] Hardcoded API key in config.py:15

💡 Top Suggestions:
  1. Extract database queries to a repository layer
  2. Add input validation to user endpoints
  3. Implement proper error handling
```

## Demo Output

<!-- ![Codebase Analysis](demo/analysis_report.png) -->

## Roadmap

- [ ] Git history analysis for code evolution
- [ ] Automated PR review integration
- [ ] Performance bottleneck detection
- [ ] Test coverage analysis

## License

MIT License — see [LICENSE](LICENSE).

---

*Powered by [Xiaomi MiMo v2.5](https://github.com/XiaomiMiMo)*
