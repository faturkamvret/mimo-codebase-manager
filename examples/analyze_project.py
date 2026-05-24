# Example: Analyze a specific directory
from codebase_manager import CodebaseManager

def example_analyze_project():
    """Analyze a Python project directory."""
    manager = CodebaseManager()

    # Analyze current directory
    report = manager.analyze(".")

    print(f"Score: {report.overall_score}/100")
    print(f"Issues: {report.issue_count}")

    for issue in report.issues[:3]:
        print(f"  [{issue.severity.value}] {issue.description}")

if __name__ == "__main__":
    example_analyze_project()
