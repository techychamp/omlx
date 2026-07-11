# Compatibility Layer Documentation

This layer exists as a non-blocking invocation of the compiler pipeline within the existing FastApi routes.
It does not interfere with the `EnginePool`, `BatchedEngine`, or `Scheduler`.
If the pipeline fails, we catch the exception, log it, and let the legacy pipeline proceed, ensuring 100% backward compatibility during the dark launch phase.
