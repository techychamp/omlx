# SPDX-License-Identifier: Apache-2.0
from ..base import PlatformService, PlatformContext
import os
import shutil
from pathlib import Path

class MigrationStep:
    def name(self) -> str:
        return ""
    def run(self, context: PlatformContext) -> bool:
        return True

class OmlxToOneMigrationStep(MigrationStep):
    def name(self) -> str:
        return "omlx_to_one"

    def run(self, context: PlatformContext) -> bool:
        home = Path.home()
        old_dir = home / ".omlx"
        new_dir = home / ".one"
        if old_dir.exists() and not (new_dir / "config").exists():
            context.logger.info("Migrating configuration from ~/.omlx to ~/.one")
            new_dir.mkdir(parents=True, exist_ok=True)
            for item in old_dir.iterdir():
                dst = new_dir / item.name
                if not dst.exists():
                    try:
                        if item.is_dir():
                            shutil.copytree(item, dst)
                        else:
                            shutil.copy2(item, dst)
                    except Exception as e:
                        context.logger.error("Error migrating %s: %s", item.name, e)
            try:
                shutil.rmtree(old_dir)
            except Exception as e:
                context.logger.warning("Failed to remove old ~/.omlx dir: %s", e)
        return True

class MigrationService(PlatformService):
    name = "migration"
    version = "1.0.0"

    def __init__(self):
        self.steps = [OmlxToOneMigrationStep()]
        self.status = "idle"

    def initialize(self, context: PlatformContext) -> None:
        self.status = "running"
        for step in self.steps:
            try:
                step.run(context)
            except Exception as e:
                context.logger.error("Migration step %s failed: %s", step.name(), e)
        self.status = "completed"

    def publish_state(self) -> dict:
        return {"status": self.status}
