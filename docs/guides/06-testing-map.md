# Test Coverage Map

This map connects major subsystems to the tests that protect them.

## Subsystem Test Mapping

| Subsystem | Responsible Tests | Coverage Confidence |
|---|---|---|
| **API Endpoints** | `tests/test_server_endpoints.py`, `tests/test_api_*.py`, `tests/test_audio_api.py`, `tests/test_status_endpoint.py` | High |
| **Scheduler** | `tests/test_scheduler*.py`, `tests/test_scheduler_chunked_prefill.py`, `tests/test_scheduler_admission.py` | High |
| **Engine / EnginePool** | `tests/test_engine_core.py`, `tests/test_engine_pool.py`, `tests/test_vlm_engine.py`, `tests/test_batched_engine.py` | High |
| **Cache (Paged/SSD)** | `tests/test_paged_cache.py`, `tests/test_paged_ssd_cache.py`, `tests/test_hybrid_cache.py`, `tests/test_vision_feature_cache.py` | High |
| **Vision (VLM)** | `tests/test_vlm_*.py`, `tests/e2e_vision_cache.py`, `tests/test_reranker_vl.py` | Medium (Complex MLX interop) |
| **Audio** | `tests/test_audio_*.py`, `tests/integration/test_audio_tts_streaming_integration.py` | Medium |
| **Settings / Config** | `tests/test_config.py`, `tests/test_settings.py` | High |
| **Model Discovery** | `tests/test_model_discovery.py`, `tests/test_model_loading.py`, `tests/test_model_registry.py` | High |
| **Experimental Diffusion** | `tests/test_experimental_diffusion.py` | Experimental (Low) |
| **Metrics** | `tests/test_server_metrics.py` | Medium |

## Analysis
* **Unprotected Areas**: Upstream MLX-LM behavioral regressions (though mitigated via `test_accuracy_benchmark.py`). Deep integrations like MCP (`test_mcp_*.py` exist, but depend heavily on client state).
* **Experimental Coverage**: Diffusion has basic unit tests but lacks full integration execution flows.
* **Regression Coverage**: High integration coverage via `tests/integration/` folder.
