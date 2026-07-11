# D1.6 & D1.7: Mappings & Migration Plan

This document describes the CLI parameter parsing structure, the FastAPI REST endpoints, and the migration strategy for persistent data.

---

## D1.6: CLI & API Mappings

### 1. CLI Override Mapping

Currently, the CLI parses individual flags (like `--max-tokens` and `--port`) and directly applies them. Under the capability-driven system, runtime configuration overrides will be supplied as nested parameters mapped by capability and option identifier:

#### Standard CLI Syntax for Overrides
`omlx serve --override <capability>.<option>=<value>`

#### Examples
*   **Autoregressive Override**: `omlx serve --override autoregressive.temperature=0.85`
*   **Diffusion Refinement Override**: `omlx serve --override diffusion.refinement_steps=50`
*   **MoE Memory Override**: `omlx serve --override streaming_moe.memory_budget=24GB`

On startup, `omlx/cli.py` gathers these overrides into a flat dictionary, which is validated against the **Capability Registry** before initializing the FastAPI server or loading a model.

---

### 2. API Endpoint Mappings

To enable client applications (SwiftUI App and Web Admin Console) to render dynamic interfaces, the server exposes the following new REST endpoints:

#### A. Fetch Capability Metadata Registry
`GET /api/schema/capabilities`
*   **Response**: Lists all registered capabilities, options, data types, validation constraints, and visibility levels (advanced vs standard).

#### B. Fetch Profile Inheritance Tree
`GET /api/schema/execution-profiles`
*   **Response**: Map of profiles, showing their capability composition, parent profile names, hardware constraints, and baseline overrides.

#### C. Fetch Model Profile State
`GET /api/models/{model_id}/execution-profile`
*   **Response**:
    ```json
    {
      "model_id": "nemotron-labs-diffusion-8b",
      "selected_profile": "nemotron_diffusion",
      "active_configuration": {
        "diffusion.refinement_steps": 32,
        "diffusion.noise_schedule": "cosine",
        "diffusion.cfg": 4.5
      },
      "runtime_state": {
        "current_refinement_iteration": 0,
        "noise_schedule_active": "cosine_annealed",
        "metal_memory_allocated_bytes": 8589934592
      }
    }
    ```

#### D. Update Model Profile Configuration
`PUT /api/models/{model_id}/execution-profile`
*   **Request**:
    ```json
    {
      "selected_profile": "nemotron_diffusion",
      "configuration_overrides": {
        "diffusion.refinement_steps": 40
      }
    }
    ```
*   **Response**: Returns the updated active configuration structure.

---

## D1.7: Persistence Migration Plan

### 1. Legacy vs New JSON Structure

#### Legacy Persistence (`model_settings.json`)
Properties are flatly defined on the root:
```json
{
  "version": 1,
  "models": {
    "llama-3b": {
      "temperature": 0.7,
      "top_p": 0.95,
      "dflash_enabled": true,
      "dflash_draft_model": "llama-draft-1b",
      "is_pinned": true
    }
  }
}
```

#### New Persistence (`model_settings.json` Version 2)
Options are grouped cleanly inside execution configuration maps, separating them from model-level attributes (`is_pinned`) and referencing the active Execution Profile:
```json
{
  "version": 2,
  "models": {
    "llama-3b": {
      "selected_profile": "nemotron_triage",
      "is_pinned": true,
      "configuration": {
        "autoregressive.temperature": 0.7,
        "autoregressive.top_p": 0.95,
        "triage.draft_model": "llama-draft-1b"
      }
    }
  }
}
```

---

### 2. Migration Execution Phases

To prevent breaking user configurations during upgrades, the migration will follow these phases:

```mermaid
chronology
    title Migration Phases
    Phase 1 (Compatibility Mapping) : Python deserializer maps old flat properties into temporary capability equivalents. Writes warning logs.
    Phase 2 (File Upgrader) : Migration script executes on server boot to read Version 1 JSON files, map fields, set default profiles, and write Version 2 files.
    Phase 3 (Deprecation Cleanup) : Flat settings attributes are fully deleted from Python dataclasses. Legacy CLI flags are retired.
```

#### Step-by-Step Transition Protocol:

1.  **Backend Deserializer Upgrade**:
    *   Update `ModelSettings.from_dict` to check if `"version" == 2`.
    *   If the version is 1, instantiate a migration dictionary mapping old fields (e.g. `dflash_enabled` and `dflash_draft_model`) to new namespaces (e.g. mapping to `selected_profile: "nemotron_triage"` and `configuration: { "triage.draft_model": ... }`).
2.  **File Upgrader Engine**:
    *   Write a module `omlx/utils/migration_v2.py`.
    *   On start of `ModelSettingsManager`, read `model_settings.json`. If `version` is absent or `1`, automatically trigger the upgrader to rewrite the file on disk to the new structure, changing the version to `2`.
3.  **Client DTO Rollout**:
    *   Update the Swift DTOs to consume the dynamic key-value configuration payload and profile identifiers instead of strict struct properties.
    *   Remove hardcoded fields from `ModelSettingsScreen.swift` and update them to use the dynamic row rendering mechanism.
