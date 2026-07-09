# SPDX-License-Identifier: Apache-2.0
import pytest
import tempfile
import time
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from omlx.platform.event_bus import PlatformEventBus, PlatformEvent, PlatformCommand
from omlx.platform.base import PlatformContext, PlatformService
from omlx.platform.launcher import Launcher
from omlx.platform.services.auth_service import AuthService
from omlx.platform.services.config_service import ConfigService
from omlx.platform.services.service_registry import ServiceRegistry
from omlx.platform.services.migration_service import MigrationService
from omlx.platform.services.process_manager import ProcessManager
from omlx.platform.services.recovery_service import RecoveryService

def test_event_bus():
    bus = PlatformEventBus()
    
    # Test Events
    events = []
    bus.subscribe("test_event", lambda ev: events.append(ev))
    bus.publish(PlatformEvent("test_event", data={"foo": "bar"}))
    assert len(events) == 1
    assert events[0].data["foo"] == "bar"

    # Test Commands
    commands = []
    bus.register_command("test_command", lambda cmd: commands.append(cmd))
    bus.send_command(PlatformCommand("test_command", data={"action": "do"}))
    assert len(commands) == 1
    assert commands[0].data["action"] == "do"

    # Test Queries
    bus.register_query("test_query", lambda params: f"hello {params}")
    res = bus.query("test_query", "world")
    assert res == "hello world"

def test_launcher_topological_sort():
    launcher = Launcher()
    class ServiceA(PlatformService):
        pass
    class ServiceB(PlatformService):
        def dependencies(self):
            return ["ServiceA"]
    class ServiceC(PlatformService):
        def dependencies(self):
            return ["ServiceB"]

    sorted_services = launcher._topological_sort([ServiceC(), ServiceB(), ServiceA()])
    names = [s.__class__.__name__ for s in sorted_services]
    assert names == ["ServiceA", "ServiceB", "ServiceC"]

def test_launcher_circular_dependency():
    launcher = Launcher()
    class ServiceA(PlatformService):
        def dependencies(self):
            return ["ServiceB"]
    class ServiceB(PlatformService):
        def dependencies(self):
            return ["ServiceA"]

    with pytest.raises(ValueError, match="Circular dependency"):
        launcher._topological_sort([ServiceA(), ServiceB()])

def test_auth_service():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = MagicMock()
        config.base_path = base

        context = PlatformContext(
            config=config,
            event_bus=MagicMock(),
            registry=MagicMock(),
            auth=None,
            state=None,
            logger=MagicMock()
        )

        service = AuthService()
        service.initialize(context)

        assert service.internal_token is not None
        assert len(service.internal_token) == 64
        assert service.verify_token(service.internal_token) is True
        assert service.verify_token("wrong-token") is False

        key_file = base / "keys" / "internal_auth.key"
        assert key_file.exists()
        import platform
        if platform.system() != "Windows":
            assert (key_file.stat().st_mode & 0o777) == 0o600

def test_service_registry():
    registry = ServiceRegistry()
    context = MagicMock()
    registry.initialize(context)
    assert context.registry == registry

    event = PlatformEvent("RuntimeReady", data={
        "service_name": "runtime",
        "endpoint": "http://localhost:8000",
        "capabilities": {"chat": {"enabled": True}},
        "pid": 1234,
        "health": "healthy"
    })
    registry.handle_registration(event)

    info = registry.get_service("runtime")
    assert info is not None
    assert info["endpoint"] == "http://localhost:8000"
    assert info["capabilities"]["chat"]["enabled"] is True
    assert info["pid"] == 1234

def test_process_manager_and_recovery():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = MagicMock()
        config.base_path = base
        config.server.host = "127.0.0.1"
        config.server.port = 8000
        config.model.get_model_dir = MagicMock(return_value=base / "models")
        config.mcp.config_path = None

        event_bus = PlatformEventBus()
        context = PlatformContext(
            config=config,
            event_bus=event_bus,
            registry=MagicMock(),
            auth=MagicMock(),
            state=MagicMock(),
            logger=MagicMock()
        )

        pm = ProcessManager()
        pm.initialize(context)

        mock_popen = MagicMock()
        mock_popen.pid = 99999
        mock_popen.poll.return_value = None

        with patch("subprocess.Popen", return_value=mock_popen):
            pm.processes["runtime"].start(pm.context)
            assert pm.processes["runtime"].is_running() is True
            assert pm.processes["runtime"].pid == 99999

            mock_popen.poll.return_value = 1

            crashed_events = []
            event_bus.subscribe("ProcessCrashed", lambda ev: crashed_events.append(ev))

            pm._check_processes()

            assert len(crashed_events) == 1
            assert crashed_events[0].data["process_name"] == "runtime"
            assert crashed_events[0].data["exit_code"] == 1

            pm.stop()

def test_recovery_service_backoff():
    event_bus = PlatformEventBus()
    context = MagicMock()
    context.event_bus = event_bus
    context.logger = MagicMock()
    
    pm = MagicMock()
    proc = MagicMock()
    pm.processes = {"runtime": proc}
    context.process_manager = pm

    recovery = RecoveryService()
    recovery.initialize(context)
    recovery.subscribe_events(event_bus)

    # Subscribe to the command RestartProcess sent by RecoveryService
    restarts_received = []
    event_bus.register_command("RestartProcess", lambda cmd: restarts_received.append(cmd))

    event = PlatformEvent("ProcessCrashed", data={"process_name": "runtime", "exit_code": 99})
    
    recovery.handle_crash(event)
    time.sleep(1.5)
    
    assert len(restarts_received) == 1
    assert restarts_received[0].data["process_name"] == "runtime"

def test_platform_api_service():
    import socket
    import json
    from omlx.platform.api import PlatformApiService
    from omlx.platform.services.auth_service import AuthService

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = MagicMock()
        config.base_path = base

        event_bus = PlatformEventBus()
        auth = AuthService()
        pm = MagicMock()
        pm.processes = {}

        context = PlatformContext(
            config=config,
            event_bus=event_bus,
            registry=MagicMock(),
            auth=auth,
            state=None,
            logger=MagicMock(),
            process_manager=pm
        )

        auth.initialize(context)
        api_service = PlatformApiService()
        api_service.initialize(context)
        api_service.start()

        assert api_service.running is True
        assert api_service.socket_path.exists() is True

        # Send test message over socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(str(api_service.socket_path))
        payload = {
            "token": auth.internal_token,
            "method": "get_health"
        }
        sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
        resp = json.loads(sock.recv(1024).decode("utf-8").strip())
        sock.close()
        assert resp["status"] == "ok"
        assert resp["health"] == "healthy"
        
        api_service.stop()
        assert api_service.running is False
        assert api_service.socket_path.exists() is False

def test_dynamic_reconfiguration():
    from omlx.platform.services.config_service import ConfigService
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = MagicMock()
        config.base_path = base
        config.server.host = "127.0.0.1"
        config.server.port = 8000
        config.model.get_model_dir = MagicMock(return_value=base / "models")
        config.mcp.config_path = None
        
        event_bus = PlatformEventBus()
        context = PlatformContext(
            config=config,
            event_bus=event_bus,
            registry=MagicMock(),
            auth=MagicMock(),
            state=None,
            logger=MagicMock()
        )
        
        pm = ProcessManager()
        pm.initialize(context)
        pm.subscribe_events(event_bus)
        
        config_service = ConfigService()
        config_service.initialize(context)
        
        mock_popen_1 = MagicMock()
        mock_popen_1.pid = 11111
        mock_popen_1.poll.return_value = None
        
        mock_popen_2 = MagicMock()
        mock_popen_2.pid = 22222
        mock_popen_2.poll.return_value = None
        
        popens = [mock_popen_1, mock_popen_2]
        
        def fake_popen(*args, **kwargs):
            return popens.pop(0)
            
        with patch("subprocess.Popen", side_effect=fake_popen):
            pm.processes["runtime"].start(pm.context)
            assert pm.processes["runtime"].pid == 11111
            
            reloaded_config = MagicMock()
            reloaded_config.base_path = base
            reloaded_config.server.host = "127.0.0.1"
            reloaded_config.server.port = 9000
            reloaded_config.model.get_model_dir = MagicMock(return_value=base / "models")
            reloaded_config.mcp.config_path = None
            
            config.load = MagicMock(return_value=reloaded_config)
            
            config_service.reload(context)
            
            assert mock_popen_1.terminate.call_count == 1
            assert pm.processes["runtime"].pid == 22222
            assert context.config == reloaded_config
            
            pm.stop()

def test_process_state_machine_degraded():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = MagicMock()
        config.base_path = base
        config.server.host = "127.0.0.1"
        config.server.port = 8000
        config.model.get_model_dir = MagicMock(return_value=base / "models")
        config.mcp.config_path = None
        
        event_bus = PlatformEventBus()
        context = PlatformContext(
            config=config,
            event_bus=event_bus,
            registry=MagicMock(),
            auth=MagicMock(),
            state=MagicMock(),
            logger=MagicMock()
        )
        
        pm = ProcessManager()
        pm.initialize(context)
        pm.subscribe_events(event_bus)
        
        runtime_proc = pm.processes["runtime"]
        assert runtime_proc.state == "Stopped"
        
        mock_popen = MagicMock()
        mock_popen.pid = 4444
        mock_popen.poll.return_value = None
        
        with patch("subprocess.Popen", return_value=mock_popen):
            runtime_proc.start(context)
            assert runtime_proc.state == "Running"
            
            event_bus.publish(PlatformEvent("RuntimeReady", data={"service_name": "runtime"}))
            assert runtime_proc.state == "Healthy"
            
            event_bus.send_command(PlatformCommand("MarkProcessDegraded", data={"process_name": "runtime"}))
            assert runtime_proc.state == "Degraded"
            
            event_bus.send_command(PlatformCommand("MarkProcessHealthy", data={"process_name": "runtime"}))
            assert runtime_proc.state == "Healthy"
            
            runtime_proc.stop(context)
            assert runtime_proc.state == "Stopped"

def test_recovery_policies():
    event_bus = PlatformEventBus()
    context = MagicMock()
    context.event_bus = event_bus
    context.logger = MagicMock()
    
    pm = MagicMock()
    proc = MagicMock()
    pm.processes = {"runtime": proc}
    context.process_manager = pm

    recovery = RecoveryService()
    recovery.initialize(context)
    recovery.subscribe_events(event_bus)

    notification_events = []
    event_bus.subscribe("PlatformNotification", lambda ev: notification_events.append(ev))
    
    # 1. Config error -> policy no_restart
    event_1 = PlatformEvent("ProcessCrashed", data={"process_name": "runtime", "exit_code": 1})
    recovery.handle_crash(event_1)
    
    assert proc.start.call_count == 0
    assert len(notification_events) == 1
    assert "validation error" in notification_events[0].data["message"]

    # 2. OOM -> policy restart_reduced_cache
    restarts_received = []
    event_bus.register_command("RestartProcess", lambda cmd: restarts_received.append(cmd))
    
    event_2 = PlatformEvent("ProcessCrashed", data={"process_name": "runtime", "exit_code": 137})
    recovery.handle_crash(event_2)
    time.sleep(0.5)
    
    assert len(restarts_received) == 1
    assert restarts_received[0].data["process_name"] == "runtime"
    assert len(notification_events) == 2
    assert "Out-of-memory" in notification_events[1].data["message"]

def test_state_aggregator():
    from omlx.platform.services.state_aggregator import StateAggregator
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = MagicMock()
        config.base_path = base
        config.version = "1.0.0"
        config.system = None
        
        event_bus = PlatformEventBus()
        registry = MagicMock()
        registry.services = {
            "runtime": {
                "endpoint": "http://localhost:8000",
                "capabilities": {"chat": {"enabled": True}},
                "health": "healthy"
            }
        }
        
        pm = MagicMock()
        proc = MagicMock()
        proc.is_running.return_value = True
        proc.pid = 9876
        proc.state = "Healthy"
        pm.processes = {"runtime": proc}
        
        context = PlatformContext(
            config=config,
            event_bus=event_bus,
            registry=registry,
            auth=MagicMock(),
            state=None,
            logger=MagicMock(),
            process_manager=pm
        )
        
        aggregator = StateAggregator()
        aggregator.initialize(context)
        aggregator.subscribe_events(event_bus)
        
        ready_event = PlatformEvent("RuntimeReady", data={
            "service_name": "runtime",
            "endpoint": "http://localhost:8000",
            "pid": 9876,
            "capabilities": {"chat": {"enabled": True}},
            "health": "healthy"
        })
        event_bus.publish(ready_event)
        
        runtime_file = base / "runtime" / "runtime.json"
        assert runtime_file.exists()
        runtime_content = json.loads(runtime_file.read_text(encoding="utf-8"))
        assert runtime_content["pid"] == 9876
        
        event_bus.publish(PlatformEvent("SomeEvent", data={}))
        
        manifest_file = base / "runtime" / "platform_manifest.json"
        assert manifest_file.exists()
        manifest_content = json.loads(manifest_file.read_text(encoding="utf-8"))
        assert manifest_content["manifest_version"] == 1
        assert manifest_content["overall_health"] == "healthy"
        assert manifest_content["capabilities"]["chat"]["enabled"] is True
        assert manifest_content["running_processes"]["runtime"] == 9876

def test_metrics_service():
    from omlx.platform.services.metrics_service import MetricsService
    
    event_bus = PlatformEventBus()
    context = PlatformContext(
        config=MagicMock(),
        event_bus=event_bus,
        registry=MagicMock(),
        auth=MagicMock(),
        state=None,
        logger=MagicMock()
    )
    
    metrics = MetricsService()
    metrics.initialize(context)
    metrics.subscribe_events(event_bus)
    
    event_bus.publish(PlatformEvent("ProcessStateChanged", data={"process_name": "runtime", "from_state": "Stopped", "to_state": "Starting"}))
    event_bus.publish(PlatformEvent("ProcessStateChanged", data={"process_name": "runtime", "from_state": "Starting", "to_state": "Running"}))
    event_bus.publish(PlatformEvent("ProcessStateChanged", data={"process_name": "runtime", "from_state": "Running", "to_state": "Healthy"}))
    
    assert metrics.restarts["runtime"] == 1
    state = metrics.publish_state()
    assert state["health_transitions_count"] == 3

def test_recovery_resolver():
    from omlx.platform.services.recovery_service import RecoveryService, RecoveryPolicy
    
    event_bus = PlatformEventBus()
    context = MagicMock()
    context.event_bus = event_bus
    context.logger = MagicMock()
    
    pm = MagicMock()
    proc = MagicMock()
    pm.processes = {"compiler": proc}
    context.process_manager = pm
    
    recovery = RecoveryService()
    recovery.initialize(context)
    recovery.subscribe_events(event_bus)
    
    class CustomCompilerPolicy(RecoveryPolicy):
        def match(self, process_name: str, exit_code: int) -> bool:
            return process_name == "compiler" and exit_code == 42
        def get_action(self, process_name: str, exit_code: int) -> dict:
            return {"policy": "restart_immediately"}
            
    recovery.resolver.register_policies("compiler", [CustomCompilerPolicy()])
    
    restarts_received = []
    event_bus.register_command("RestartProcess", lambda cmd: restarts_received.append(cmd))
    
    event_bus.publish(PlatformEvent("ProcessCrashed", data={"process_name": "compiler", "exit_code": 42}))
    time.sleep(0.5)
    
    assert len(restarts_received) == 1
    assert restarts_received[0].data["process_name"] == "compiler"
