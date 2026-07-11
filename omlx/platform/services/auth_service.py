# SPDX-License-Identifier: Apache-2.0
from ..base import PlatformService, PlatformContext
import secrets
from pathlib import Path

class AuthService(PlatformService):
    name = "auth"
    version = "1.0.0"

    def __init__(self):
        self.internal_token = None

    def initialize(self, context: PlatformContext) -> None:
        keys_dir = context.config.base_path / "keys"
        keys_dir.mkdir(parents=True, exist_ok=True)
        token_path = keys_dir / "internal_auth.key"

        if token_path.exists():
            try:
                self.internal_token = token_path.read_text(encoding="utf-8").strip()
            except Exception:
                self.internal_token = None

        if not self.internal_token:
            self.internal_token = secrets.token_hex(32)
            try:
                token_path.write_text(self.internal_token, encoding="utf-8")
                token_path.chmod(0o600)
            except Exception as e:
                context.logger.error("Failed to write internal token: %s", e)
        
        # Link auth to context
        context.auth = self

    def verify_token(self, token: str) -> bool:
        return token == self.internal_token

    def publish_state(self) -> dict:
        return {"status": "active" if self.internal_token else "failed"}
