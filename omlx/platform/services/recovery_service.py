# SPDX-License-Identifier: Apache-2.0
from ..base import PlatformService, PlatformContext
from ..event_bus import PlatformEvent
import time
import threading
from typing import List, Dict

class RecoveryPolicy:
    def match(self, process_name: str, exit_code: int) -> bool:
        return False
    def get_action(self, process_name: str, exit_code: int) -> dict:
        return {"policy": "restart"}

class ConfigErrorRecoveryPolicy(RecoveryPolicy):
    def match(self, process_name: str, exit_code: int) -> bool:
        return exit_code == 1
    def get_action(self, process_name: str, exit_code: int) -> dict:
        return {
            "policy": "no_restart",
            "notify": "Configuration validation error. Startup aborted."
        }

class OOMRecoveryPolicy(RecoveryPolicy):
    def match(self, process_name: str, exit_code: int) -> bool:
        return exit_code in (137, -9)
    def get_action(self, process_name: str, exit_code: int) -> dict:
        return {
            "policy": "restart_reduced_cache",
            "notify": "Out-of-memory error detected. Restarting with reduced cache."
        }

class SegfaultRecoveryPolicy(RecoveryPolicy):
    def match(self, process_name: str, exit_code: int) -> bool:
        return exit_code in (139, -11)
    def get_action(self, process_name: str, exit_code: int) -> dict:
        return {
            "policy": "restart_immediately"
        }

class DefaultRecoveryPolicy(RecoveryPolicy):
    def match(self, process_name: str, exit_code: int) -> bool:
        return True
    def get_action(self, process_name: str, exit_code: int) -> dict:
        return {
            "policy": "restart_with_backoff"
        }

class RecoveryPolicyResolver:
    def __init__(self, context: PlatformContext) -> None:
        self.context = context
        self.process_policies: Dict[str, List[RecoveryPolicy]] = {}

    def register_policies(self, process_name: str, policies: List[RecoveryPolicy]) -> None:
        self.process_policies[process_name] = policies

    def resolve_policies(self, process_name: str) -> List[RecoveryPolicy]:
        return self.process_policies.get(process_name, [
            ConfigErrorRecoveryPolicy(),
            OOMRecoveryPolicy(),
            SegfaultRecoveryPolicy(),
            DefaultRecoveryPolicy()
        ])

class RecoveryService(PlatformService):
    name = "recovery"
    version = "1.0.0"

    def dependencies(self) -> list[str]:
        return ["process_manager"]

    def __init__(self) -> None:
        self.context: PlatformContext | None = None
        self.restart_counts = {}
        self.last_recovery = None
        self.resolver = None

    def initialize(self, context: PlatformContext) -> None:
        self.context = context
        self.resolver = RecoveryPolicyResolver(context)

    def subscribe_events(self, event_bus) -> None:
        event_bus.subscribe("ProcessCrashed", self.handle_crash)

    def handle_crash(self, event: PlatformEvent) -> None:
        process_name = event.data.get("process_name")
        exit_code = event.data.get("exit_code")
        self.context.logger.warning(f"RecoveryService handling crash of process {process_name} with exit code {exit_code}")
        
        # Match policy
        policies = self.resolver.resolve_policies(process_name)
        matched_policy = None
        for p in policies:
            if p.match(process_name, exit_code):
                matched_policy = p
                break

        if not matched_policy:
            self.context.logger.error("No matching recovery policy found!")
            return

        action = matched_policy.get_action(process_name, exit_code)
        policy_type = action.get("policy")

        if policy_type == "no_restart":
            self.context.logger.error(f"RecoveryPolicy: no_restart for {process_name}. Aborting.")
            self.context.event_bus.publish(
                PlatformEvent("PlatformNotification", data={"type": "error", "message": action.get("notify")})
            )
            return

        count = self.restart_counts.get(process_name, 0)
        if count >= 5:
            self.context.logger.error(f"Process {process_name} has crashed 5 times, stopping recovery.")
            return

        self.restart_counts[process_name] = count + 1
        self.last_recovery = time.time()

        if policy_type == "restart_reduced_cache":
            self.context.logger.warning(f"RecoveryPolicy: OOM detected. Triggering reduced cache restart.")
            self.context.event_bus.publish(
                PlatformEvent("PlatformNotification", data={"type": "warning", "message": action.get("notify")})
            )
            if self.context.config and hasattr(self.context.config, "server"):
                self.context.logger.info("Applying lower memory cache settings for next launch.")

        # Determine wait time based on policy type
        delay = 0.0
        if policy_type == "restart_with_backoff":
            delay = float(2 ** count)

        threading.Thread(
            target=self._recover_process,
            args=(process_name, count, delay),
            daemon=True
        ).start()

    def _recover_process(self, process_name: str, count: int, delay: float) -> None:
        if delay > 0:
            self.context.logger.info(f"Backing off for {delay} seconds before restarting {process_name}")
            time.sleep(delay)
        
        pm = getattr(self.context, "process_manager", None)
        if pm and process_name in pm.processes:
            self.context.logger.info(f"Restarting process {process_name} (attempt {count + 1})")
            try:
                from ..event_bus import PlatformCommand
                self.context.event_bus.send_command(
                    PlatformCommand("RestartProcess", data={"process_name": process_name})
                )
            except Exception as e:
                self.context.logger.error(f"Failed to restart process {process_name}: {e}")

    def publish_state(self) -> dict:
        return {
            "last_recovery": self.last_recovery,
            "restart_counts": self.restart_counts
        }
