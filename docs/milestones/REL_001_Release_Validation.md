# Milestone Plan — REL-001: Release Validation

This milestone establishes the comprehensive suite of installation, upgrade, integration, and recovery tests to certify the production readiness of One releases.

---

## 1. Goals
Ensure that the installer, desktop bundle, update cycles, and runtime engine operate correctly and safely across clean, upgraded, or corrupted environments.

---

## 2. Test Cases and Scenarios

### Task 2.1: Clean Machine Install
- **Objective**: Verify app installation on a system without any existing config folders.
- **Verification**: Run the welcome wizard, specify new directories, and verify `~/.one` and settings files are generated correctly.

### Task 2.2: Upgrade Install
- **Objective**: Verify that upgrading from a legacy oMLX installation migrates the config cleanly.
- **Verification**: Ensure settings, custom profiles, models, cache, logs, and bin files are moved from `~/.omlx` to `~/.one` without data loss or duplicate migration triggers.

### Task 2.3: Uninstall & Reinstall
- **Objective**: Verify app footprint removal and reinstallation.
- **Verification**: Ensure deletion of `~/.one`, `Library/Application Support/One` and preference plists cleans up the system, and subsequent installations re-initialize correctly.

### Task 2.4: Auto-Update Flow
- **Objective**: Verify the background checker and in-app swap mechanics.
- **Verification**: Trigger a mock update download, verify DMG mount, staging of `.One-update.app`, and process swap on restart.

### Task 2.5: Downgrade Handling
- **Objective**: Verify behavior when running an older version of the app against a newer configuration file.
- **Verification**: Ensure backward compatibility of settings or graceful fallback to default parameters when new keys are encountered.

### Task 2.6: Corrupted Config Recovery
- **Objective**: Validate app robustness when settings are malformed.
- **Verification**: Write corrupted/empty JSON to `~/.one/settings.json`, launch the app, and verify it recovers by resetting or prompt-healing to stable defaults.

### Task 2.7: Edge Startup Conditions
- **No-Model Startup**: Verify the server starts and connects successfully when the models directory is empty.
- **Offline Startup**: Verify the server starts and operates without internet connectivity (skipping HuggingFace/ModelScope endpoint checkouts).
- **Low Disk**: Validate warnings or graceful load degradation when SSD capacity is below 2GB.
- **Low Memory**: Verify that memory enforcers and LRU caches aggressively evict models to respect system ceilings on lower-memory machines.
