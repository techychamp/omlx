# RuntimeSession Queue Guide

## Overview
A `RuntimeSession` represents the execution lifecycle of an admitted request.

## Initialization
It is standard to initialize a `RuntimeSession` by consuming a `QueueSession`.
`RuntimeSession.from_queue_session(queue_session, planning_bundle)` transfers ownership of the `QueueSession` into the active execution pipeline.

## Boundaries
The `RuntimeSession` owns the execution context and the `PlanningBundle`, but it explicitly **does not** manage queue policies, priorities, or admission rules.
