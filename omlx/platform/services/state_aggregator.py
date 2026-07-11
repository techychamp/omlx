# SPDX-License-Identifier: Apache-2.0
import json
import os
from pathlib import Path
from ..base import PlatformService, PlatformContext
from ..event_bus import PlatformEvent

class StateAggregator(PlatformService):
    name = "state"
    version = "1.0.0"

    def dependencies(self):
        return ["registry", "process_manager"]

    def initialize(self, context: PlatformContext) -> None:
        self.context = context
        context.state = self
        self.runtime_dir = context.config.base_path / "runtime"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

    def subscribe_events(self, event_bus) -> None:
        event_bus.subscribe("RuntimeReady", self.handle_runtime_ready)
        event_bus.subscribe("*", self.handle_wildcard_event)

    def handle_runtime_ready(self, event: PlatformEvent) -> None:
        runtime_data = event.data
        runtime_file = self.runtime_dir / "runtime.json"
        try:
            runtime_file.write_text(json.dumps(runtime_data, indent=2), encoding="utf-8")
        except OSError as e:
            self.context.logger.error("Failed to write runtime.json: %s", e)

    def handle_wildcard_event(self, event: PlatformEvent) -> None:
        if not self.context or not self.context.registry or not self.context.process_manager:
            return

        state_path = self.runtime_dir / "platform.json"
        health_path = self.runtime_dir / "platform_health.json"
        manifest_path = self.runtime_dir / "platform_manifest.json"

        services = self.context.registry.services
        healths = {}
        capabilities = {}
        for s_name, s_info in services.items():
            healths[s_name] = s_info.get("health", "healthy")
            svc_caps = s_info.get("capabilities", {})
            if isinstance(svc_caps, dict):
                for cap_name, cap_info in svc_caps.items():
                    capabilities[cap_name] = cap_info
            elif isinstance(svc_caps, list):
                for cap_name in svc_caps:
                    capabilities[cap_name] = {"enabled": True}
        
        # Get launcher services state mapping
        launcher_states = {}
        launcher = getattr(self.context, "launcher", None)
        if launcher:
            for s in launcher.services:
                launcher_states[s.name] = s.publish_state()

        processes = self.context.process_manager.processes
        running_proc_info = {}
        for p_name, proc in processes.items():
            if proc.is_running():
                running_proc_info[p_name] = proc.pid

        overall_health = "healthy"
        if any(h != "healthy" for h in healths.values()):
            overall_health = "unhealthy"
        for p_name, proc in processes.items():
            if p_name == "runtime" and not proc.is_running():
                overall_health = "unhealthy"

        # Determine feature flags and settings version
        sys_config = getattr(self.context.config, "system", None)
        feature_flags = getattr(sys_config, "feature_flags", {}) if sys_config else {}

        manifest = {
            "manifest_version": 1,
            "platform_version": "1.0.0",
            "compatibility_version": "1.0.0",
            "services": services,
            "capabilities": capabilities,
            "running_processes": running_proc_info,
            "configuration_version": getattr(self.context.config, "version", "1.0.0"),
            "feature_flags": feature_flags,
            "supported_apis": ["openai/v1"],
            "overall_health": overall_health
        }

        try:
            state_path.write_text(json.dumps(launcher_states, indent=2), encoding="utf-8")
            health_path.write_text(json.dumps({"overall": overall_health, "services": healths}, indent=2), encoding="utf-8")
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        except OSError as e:
            self.context.logger.error("Failed to write platform manifest files: %s", e)

    def publish_state(self) -> dict:
        return {"status": "active"}
