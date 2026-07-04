# Rollback Procedure

If a deployed version or merged PR breaks the verification constraints (for instance, dropping Confidence below Level 4 or breaking golden assets without an ADR), the rollback process is strictly enforced:

1. Identify the failing pipeline via the Verification Report.
2. Trigger the `revert` on the pull request.
3. Validate the `revert` pull request runs the exact same Verification Pipeline and passes 100%.
4. No hotfixes are permitted inside the revert process. The system must return to the prior known-good state entirely before patches are attempted.
