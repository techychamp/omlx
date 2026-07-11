# Batch Planning Guide

1. Use `BatchPlanner.plan(request_ids, max_batch_size, max_tokens)` to create a `BatchPlan`.
2. The plan produces a `BatchDescriptor`, `BatchRequirement`, and `BatchCompatibilityReport`.
3. Include the `BatchPlan` in the `PlanningBundle`.
