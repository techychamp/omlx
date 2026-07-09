# SPDX-License-Identifier: Apache-2.0
from ..base import PlatformService, PlatformContext
from ..event_bus import PlatformEvent, PlatformCommand
import subprocess
import sys
import os
import time
import logging
import threading
from typing import List, Dict

class ManagedProcess:
    def __init__(self, name: str) -> None:
        self.name = name
        self.process: subprocess.Popen | None = None
        self.state = "Stopped"

    def set_state(self, new_state: str, context: PlatformContext) -> None:
        from_state = self.state
        self.state = new_state
        if context and context.event_bus:
            context.event_bus.publish(
                PlatformEvent(
                    "ProcessStateChanged",
                    data={
                        "process_name": self.name,
                        "from_state": from_state,
                        "to_state": new_state,
                        "pid": self.pid
                    }
                )
            )
            if new_state == "Healthy" and self.name == "runtime":
                context.event_bus.publish(PlatformEvent("ClientsReconnect", data={}))

    def start(self, context: PlatformContext) -> None:
        pass

    def stop(self, context: PlatformContext) -> None:
        if self.process and self.process.poll() is None:
            self.set_state("Stopping", context)
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None
        self.set_state("Stopped", context)

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    @property
    def pid(self) -> int | None:
        return self.process.pid if self.process else None


class RuntimeProcess(ManagedProcess):
    def __init__(self) -> None:
        super().__init__("runtime")

    def start(self, context: PlatformContext) -> None:
        self.set_state("Starting", context)
        cfg = context.config
        host = cfg.server.host or "127.0.0.1"
        port = cfg.server.port or 8000
        model_dir = str(cfg.model.get_model_dir(cfg.base_path))
        
        args = [
            sys.executable, "-m", "omlx.server",
            "--host", host,
            "--port", str(port),
            "--model-dir", model_dir
        ]
        
        if cfg.mcp.config_path:
            args.extend(["--mcp-config", str(cfg.mcp.config_path)])

        context.logger.info("Spawning Runtime process: %s", " ".join(args))
        
        log_file = context.config.base_path / "logs" / "runtime.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_f = open(log_file, "a", encoding="utf-8")

        env = os.environ.copy()
        env["OMLX_PLATFORM_SOCKET"] = str(context.config.base_path / "runtime" / "platform.sock")
        if context.auth and context.auth.internal_token:
            env["OMLX_INTERNAL_TOKEN"] = context.auth.internal_token

        self.process = subprocess.Popen(
            args,
            stdout=self.log_f,
            stderr=self.log_f,
            env=env
        )
        self.set_state("Running", context)
        context.logger.info("Runtime process spawned with PID %d", self.process.pid)

    def stop(self, context: PlatformContext) -> None:
        super().stop(context)
        if hasattr(self, "log_f") and self.log_f:
            try:
                self.log_f.close()
            except Exception:
                pass


class ProcessManager(PlatformService):
    name = "process_manager"
    version = "1.0.0"

    def dependencies(self) -> List[str]:
        return ["config", "auth", "registry"]

    def __init__(self) -> None:
        self.processes: Dict[str, ManagedProcess] = {}
        self.context: PlatformContext | None = None
        self.monitor_thread = None
        self.should_monitor = False

    def initialize(self, context: PlatformContext) -> None:
        self.context = context
        context.process_manager = self
        
        # Register command handlers on the bus!
        from ..event_bus import PlatformCommand
        context.event_bus.register_command("RestartProcess", self.handle_restart_command)
        context.event_bus.register_command("MarkProcessDegraded", self.handle_mark_degraded_command)
        context.event_bus.register_command("MarkProcessHealthy", self.handle_mark_healthy_command)

        # Discover subclasses of ManagedProcess dynamically
        for cls in ManagedProcess.__subclasses__():
            proc = cls()
            self.processes[proc.name] = proc

    def subscribe_events(self, event_bus) -> None:
        event_bus.subscribe("ConfigChanged", self.handle_config_change)
        event_bus.subscribe("RuntimeReady", self.handle_runtime_ready)

    def handle_restart_command(self, cmd: PlatformCommand) -> None:
        proc_name = cmd.data.get("process_name")
        self.context.logger.info(f"Command RestartProcess received for {proc_name}")
        proc = self.processes.get(proc_name)
        if proc:
            try:
                proc.stop(self.context)
                proc.start(self.context)
            except Exception as e:
                self.context.logger.error(f"Failed to restart process {proc_name}: {e}")

    def handle_mark_degraded_command(self, cmd: PlatformCommand) -> None:
        proc_name = cmd.data.get("process_name")
        proc = self.processes.get(proc_name)
        if proc and proc.state == "Healthy":
            proc.set_state("Degraded", self.context)

    def handle_mark_healthy_command(self, cmd: PlatformCommand) -> None:
        proc_name = cmd.data.get("process_name")
        proc = self.processes.get(proc_name)
        if proc and proc.state == "Degraded":
            proc.set_state("Healthy", self.context)

    def handle_config_change(self, event: PlatformEvent) -> None:
        self.context.logger.info("ConfigChanged event received. Triggering RestartProcess command...")
        from ..event_bus import PlatformCommand
        self.context.event_bus.send_command(
            PlatformCommand("RestartProcess", data={"process_name": "runtime"})
        )

    def handle_runtime_ready(self, event: PlatformEvent) -> None:
        runtime_proc = self.processes.get("runtime")
        if runtime_proc and runtime_proc.state == "Running":
            runtime_proc.set_state("Healthy", self.context)

    def start(self) -> None:
        for name, proc in self.processes.items():
            if name == "runtime":
                proc.start(self.context)
        
        self.should_monitor = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def _monitor_loop(self) -> None:
        while self.should_monitor:
            self._check_processes()
            time.sleep(1.0)

    def _check_processes(self) -> None:
        for name, proc in list(self.processes.items()):
            if proc.process and proc.process.poll() is not None:
                exit_code = proc.process.poll()
                proc.process = None
                proc.set_state("Stopped", self.context)
                self.context.logger.warning("Process %s exited with code %s", name, exit_code)
                self.context.event_bus.publish(
                    PlatformEvent("ProcessCrashed", data={"process_name": name, "exit_code": exit_code})
                )

    def stop(self) -> None:
        self.should_monitor = False
        for name, proc in self.processes.items():
            self.context.logger.info("Stopping process: %s", name)
            proc.stop(self.context)

    def health(self) -> dict:
        health_status = {}
        overall = "healthy"
        for name, proc in self.processes.items():
            running = proc.is_running()
            health_status[name] = proc.state
            if name == "runtime" and proc.state != "Healthy":
                overall = "unhealthy"
        return {"status": overall, "details": health_status}

    def publish_state(self) -> dict:
        return {
            "status": "running",
            "active_processes": {name: p.state for name, p in self.processes.items()}
        }
