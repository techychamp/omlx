import os

def test_reports_exist():
    expected_reports = [
        "docs/reports/GUI-001/GUI_Architecture_Report.md",
        "docs/reports/GUI-001/Desktop_Shell_Report.md",
        "docs/reports/GUI-001/API_Integration_Report.md",
        "docs/reports/GUI-001/Ownership_Verification_Report.md",
        "docs/reports/GUI-001/Future_Module_Compatibility_Report.md",
        "docs/reports/GUI-001/Desktop_Architecture_Guide.md",
        "docs/reports/GUI-001/SwiftUI_Architecture_Guide.md",
        "docs/reports/GUI-001/MVVM_Guide.md",
        "docs/reports/GUI-001/Navigation_Guide.md",
        "docs/reports/GUI-001/Workspace_Guide.md",
        "docs/reports/GUI-001/Dependency_Injection_Guide.md",
        "docs/reports/GUI-001/Migration_Report.md",
        "docs/reports/GUI-001/Architecture_Decision_Record.md",
    ]
    for report in expected_reports:
        assert os.path.exists(report), f"Report {report} does not exist"

def test_no_forbidden_imports_in_gui():
    for root, _, files in os.walk("apps/omlx-mac"):
        for file in files:
            if file.endswith(".swift"):
                with open(os.path.join(root, file)) as f:
                    content = f.read()
                    assert "import PythonKit" not in content, f"Forbidden import found in {file}"
