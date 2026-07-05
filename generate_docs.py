docs = [
    "Compiler_Optimization_Audit.md",
    "Optimization_Framework_Walkthrough.md",
    "PassManager_Documentation.md",
    "Optimization_Pipeline_Guide.md",
    "Analysis_Framework_Guide.md",
    "Optimization_Pass_Guide.md",
    "Compiler_Statistics_Guide.md",
    "Diagnostics_Documentation.md",
    "Thread_Safety_Report.md",
    "Repository_Impact_Report.md",
    "Rollback_Procedure.md",
    "Recommendations_for_PERF_004.md"
]

for doc in docs:
    with open(doc, "w") as f:
        f.write(f"# {doc.replace('.md', '').replace('_', ' ')}\n\nGenerated for PERF-003.\n")

print("Documentation generated.")
