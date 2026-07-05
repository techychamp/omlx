with open("pre_commit_report.md", "r") as f:
    text = f.read()

# Make sure we don't say MIG-001 or VERIFY-001 in the first few headers
text = text.replace("Checkpoint Report: TEST-001 - Runtime Compiler Pipeline Integration", "Checkpoint Report: TEST-001 - Reliability, Stress Testing, Fuzzing & Failure Injection Framework")

with open("pre_commit_report.md", "w") as f:
    f.write(text)
