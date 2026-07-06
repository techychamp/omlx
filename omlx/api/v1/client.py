from typing import Any, Dict, List, Optional, AsyncGenerator
from pydantic import BaseModel, Field
import uuid
import asyncio
import threading

from omlx.api.v1.runtime import RuntimeBuilder, RuntimeService, RuntimeConfig
from omlx.api.v1.generation import GenerateRequest, GenerateResponse, StreamRequest, StreamResponse
from omlx.api.v1.compiler import CompilerRequest, CompilerResult
from omlx.api.v1.inspection import InspectionResult, Inspector
from omlx.api.v1.verification import VerificationRequest, VerificationResult
from omlx.api.v1.observation import ObservationSummary, ObservationService
from omlx.api.v1.exceptions import ConfigurationError, OMLXRuntimeError, OmlxError

class SessionDescriptor(BaseModel):
    session_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True
    statistics: Dict[str, Any] = Field(default_factory=dict)

class OMLXClient:
    def __init__(self, runtime: Optional[RuntimeService] = None, builder_settings: Optional[Dict[str, Any]] = None):
        self._builder = RuntimeBuilder()
        if builder_settings:
            self._builder.configure(builder_settings)
        self._runtime = runtime if runtime else self._builder.build()
        self._sessions: Dict[str, SessionDescriptor] = {}
        self._config_profiles: Dict[str, RuntimeConfig] = {}
        self._lock = threading.Lock()

    def create_session(self, metadata: Dict[str, Any] = None) -> SessionDescriptor:
        session_id = str(uuid.uuid4())
        session = SessionDescriptor(session_id=session_id, metadata=metadata or {})
        with self._lock:
            self._sessions[session_id] = session

        # We need to coordinate with Runtime by using its built-in API.
        if hasattr(self._runtime, '_internal') and hasattr(self._runtime._internal, 'streaming_controller'):
            self._runtime._internal.streaming_controller.create_session() # If runtime implements a session creation logic

        return session

    def get_session(self, session_id: str) -> Optional[SessionDescriptor]:
        with self._lock:
            return self._sessions.get(session_id)

    def cancel_session(self, session_id: str):
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                 updated_session = SessionDescriptor(
                     session_id=session.session_id,
                     metadata=session.metadata,
                     active=False,
                     statistics=session.statistics
                 )
                 self._sessions[session_id] = updated_session

        # Coordinate with Runtime to actually halt operations
        if hasattr(self._runtime, '_internal') and hasattr(self._runtime._internal, 'streaming_controller'):
            self._runtime._internal.streaming_controller.cancel_session(session_id)

    def cleanup_session(self, session_id: str):
         with self._lock:
             self._sessions.pop(session_id, None)
         # Inform Runtime
         if hasattr(self._runtime, '_internal') and hasattr(self._runtime._internal, 'streaming_controller'):
             self._runtime._internal.streaming_controller.cleanup_session(session_id)

    def apply_profile(self, profile_name: str, config: RuntimeConfig):
         with self._lock:
             self._config_profiles[profile_name] = config
             self._builder.configure(config.settings)
             for flag, value in config.feature_flags.items():
                  if value:
                       self._builder.enable(flag)
                  else:
                       self._builder.disable(flag)
             # Rebuild the runtime with the new configurations
             self._runtime = self._builder.build()

    def get_profile(self, profile_name: str) -> Optional[RuntimeConfig]:
         with self._lock:
             return self._config_profiles.get(profile_name)

    # Sync operations
    def generate(self, request: GenerateRequest, session_id: Optional[str] = None) -> GenerateResponse:
        if session_id and not self.get_session(session_id):
            raise ConfigurationError(f"Session {session_id} not found")
        try:
            # We are assuming runtime might use session_id to tie statistics/observability later
            return self._runtime.generation.generate(request)
        except Exception as e:
            if isinstance(e, OmlxError):
                raise
            raise OMLXRuntimeError(f"Generation failed: {str(e)}") from e

    # Async Operations
    async def generate_async(self, request: GenerateRequest, session_id: Optional[str] = None) -> GenerateResponse:
        return await asyncio.to_thread(self.generate, request, session_id)

    async def stream(self, request: StreamRequest, session_id: Optional[str] = None) -> AsyncGenerator[StreamResponse, None]:
        if session_id and not self.get_session(session_id):
            raise ConfigurationError(f"Session {session_id} not found")
        try:
             # Runtime integration
             async for chunk in self._runtime.generation.stream(request):
                 yield chunk
        except Exception as e:
            if isinstance(e, OmlxError):
                raise
            raise OMLXRuntimeError(f"Streaming failed: {str(e)}") from e

    async def compile_async(self, request: CompilerRequest, session_id: Optional[str] = None) -> CompilerResult:
         if hasattr(self._runtime, 'compiler') and hasattr(self._runtime.compiler, 'compile'):
              return await asyncio.to_thread(self._runtime.compiler.compile, request)
         raise OMLXRuntimeError("CompilerService is not available in the current runtime.")

    async def inspect_async(self, session_id: Optional[str] = None) -> InspectionResult:
         if hasattr(self._runtime, 'inspector') and hasattr(self._runtime.inspector, 'inspect'):
             return await asyncio.to_thread(self._runtime.inspector.inspect)
         raise OMLXRuntimeError("Inspector is not available in the current runtime.")

    async def validate_async(self, request: VerificationRequest, session_id: Optional[str] = None) -> VerificationResult:
         if hasattr(self._runtime, 'verifier') and hasattr(self._runtime.verifier, 'verify'):
             return await asyncio.to_thread(self._runtime.verifier.verify, request)
         raise OMLXRuntimeError("Verifier is not available in the current runtime.")

    # Model and Quantization Introspection
    def get_model_info(self) -> Any:
         if hasattr(self._runtime, 'models') and hasattr(self._runtime.models, 'get_info'):
              return self._runtime.models.get_info()
         raise OMLXRuntimeError("ModelService get_info is not available.")

    def get_quantization_info(self) -> Any:
         if hasattr(self._runtime, 'quantization') and hasattr(self._runtime.quantization, 'get_info'):
              return self._runtime.quantization.get_info()
         raise OMLXRuntimeError("QuantizationService get_info is not available.")

    # Observation
    def get_observation_summary(self, session_id: str) -> Optional[ObservationSummary]:
         if hasattr(self._runtime, 'observation') and hasattr(self._runtime.observation, 'get_summary'):
              return self._runtime.observation.get_summary(session_id)
         raise OMLXRuntimeError("ObservationService get_summary is not available.")

    def get_tooling(self) -> Any:
         if hasattr(self._runtime, 'get_tooling'):
              return self._runtime.get_tooling()
         raise OMLXRuntimeError("Tooling registry is not available.")

    def get_plugins(self) -> Any:
         if hasattr(self._runtime, 'plugins'):
              return self._runtime.plugins
         raise OMLXRuntimeError("Plugin framework is not available.")
