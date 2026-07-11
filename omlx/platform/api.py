# SPDX-License-Identifier: Apache-2.0
import os
import json
import socket
import threading
import logging
from pathlib import Path
from typing import List
from .base import PlatformService, PlatformContext
from .event_bus import PlatformEvent

logger = logging.getLogger("omlx.platform.api")

class PlatformController:
    def __init__(self, context: PlatformContext) -> None:
        self.context = context

    def handle_message(self, msg: dict) -> dict:
        token = msg.get("token")
        if not self.context.auth or not self.context.auth.verify_token(token):
            return {"status": "error", "message": "Unauthorized"}

        method = msg.get("method")
        params = msg.get("params", {})

        if method == "publish_event":
            name = params.get("name")
            data = params.get("data", {})
            event = PlatformEvent(name, data=data)
            self.context.event_bus.publish(event)
            return {"status": "ok"}
        elif method == "get_health":
            # return aggregate health
            pm = getattr(self.context, "process_manager", None)
            health_status = "healthy"
            if pm:
                for p_name, p in pm.processes.items():
                    if not p.is_running():
                        health_status = "unhealthy"
            return {"status": "ok", "health": health_status}
        elif method == "get_capabilities":
            registry = getattr(self.context, "registry", None)
            caps = []
            if registry:
                for svc in registry.services.values():
                    caps.extend(svc.get("capabilities", []))
            return {"status": "ok", "capabilities": list(set(caps))}
        else:
            return {"status": "error", "message": f"Unknown method: {method}"}


class PlatformApiService(PlatformService):
    name = "api"
    version = "1.0.0"

    def dependencies(self) -> List[str]:
        return ["auth", "process_manager"]

    def __init__(self) -> None:
        self.context = None
        self.socket_path = None
        self.server_thread = None
        self.running = False
        self.sock = None
        self.controller = None

    def initialize(self, context: PlatformContext) -> None:
        self.context = context
        self.controller = PlatformController(context)
        
        runtime_dir = context.config.base_path / "runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        self.socket_path = runtime_dir / "platform.sock"

    def start(self) -> None:
        if self.running:
            return
        
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except Exception as e:
                logger.error("Failed to delete stale socket file %s: %s", self.socket_path, e)

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.sock.bind(str(self.socket_path))
            self.sock.listen(10)
        except Exception as e:
            logger.error("Failed to bind socket %s: %s", self.socket_path, e)
            return

        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, name="PlatformApiServer", daemon=True)
        self.server_thread.start()
        logger.info("Platform UDS API server listening at %s", self.socket_path)

    def _run_server(self) -> None:
        self.sock.settimeout(0.5)
        while self.running:
            try:
                conn, addr = self.sock.accept()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error("Socket accept error: %s", e)
                break

            conn_thread = threading.Thread(target=self._handle_connection, args=(conn,), daemon=True)
            conn_thread.start()

    def _handle_connection(self, conn: socket.socket) -> None:
        conn.settimeout(2.0)
        data_buffer = []
        try:
            while self.running:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data_buffer.append(chunk)
                if b"\n" in chunk:
                    break
            
            full_data = b"".join(data_buffer).decode("utf-8").strip()
            if not full_data:
                return

            try:
                msg = json.loads(full_data)
                resp = self.controller.handle_message(msg)
            except Exception as parse_err:
                resp = {"status": "error", "message": f"Invalid request format: {parse_err}"}

            conn.sendall((json.dumps(resp) + "\n").encode("utf-8"))
        except Exception as e:
            logger.error("UDS connection handling error: %s", e)
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def stop(self) -> None:
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

        if self.server_thread:
            self.server_thread.join(timeout=1.0)
            self.server_thread = None

        if self.socket_path and self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except Exception:
                pass

    def publish_state(self) -> dict:
        return {"status": "running" if self.running else "stopped"}
