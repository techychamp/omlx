from verification.scripts.reporting import generate_verification_report, generate_regression_report
import os

vp = generate_verification_report()
rp = generate_regression_report()
assert os.path.exists(vp)
assert os.path.exists(rp)
print("Reports generated successfully.")
