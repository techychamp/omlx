# SPDX-License-Identifier: Apache-2.0
from ..base import PlatformService, PlatformContext
from ..event_bus import PlatformEvent

class ConfigService(PlatformService):
    name = "config"
    version = "1.0.0"

    def initialize(self, context: PlatformContext) -> None:
        self.config = context.config

    def reload(self, context: PlatformContext) -> None:
        context.logger.info("Reloading platform configuration...")
        new_cfg = self.config.load(self.config.base_path)
        self.config = new_cfg
        context.config = new_cfg
        context.event_bus.publish(PlatformEvent("ConfigChanged", data={}))

    def publish_state(self) -> dict:
        return {"status": "loaded"}
