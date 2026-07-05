# SPDX-License-Identifier: Apache-2.0
"""
Backend Capability Negotiation.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any
from typing import Any
from ..descriptor import BackendDescriptor, BackendCapability
from omlx.capabilities.descriptor import CapabilityDescriptor

@dataclass(frozen=True)
class NegotiationDiagnostics:
    execution_family_match: bool
    attention_support_match: bool
    streaming_match: bool
    speculative_decoding_match: bool
    diffusion_match: bool
    moe_routing_match: bool
    verification_match: bool
    graph_execution_match: bool
    cache_layout_match: bool
    memory_model_match: bool
    hardware_topology_match: bool
    details: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

class BackendNegotiator:
    @staticmethod
    def negotiate(
        plan: Any,
        backend_desc: BackendDescriptor,
        cap_desc: CapabilityDescriptor
    ) -> NegotiationDiagnostics:

        # In a full implementation, these would inspect plan steps and capability descriptor traits
        # and match them against backend_desc capabilities.

        # Simple stubs for negotiation logic:
        execution_family_match = True
        attention_support_match = True
        streaming_match = BackendCapability.STREAMING in backend_desc.supported_optimization_capabilities or True
        speculative_decoding_match = True
        diffusion_match = True
        moe_routing_match = True
        verification_match = BackendCapability.VERIFICATION in backend_desc.supported_optimization_capabilities or True
        graph_execution_match = BackendCapability.GRAPH_EXECUTION in backend_desc.supported_optimization_capabilities or True
        cache_layout_match = True
        memory_model_match = backend_desc.memory_model != ""
        hardware_topology_match = True

        details = {
            "backend_family": backend_desc.backend_family,
            "cache_layouts": backend_desc.supported_cache_layouts,
        }

        return NegotiationDiagnostics(
            execution_family_match=execution_family_match,
            attention_support_match=attention_support_match,
            streaming_match=streaming_match,
            speculative_decoding_match=speculative_decoding_match,
            diffusion_match=diffusion_match,
            moe_routing_match=moe_routing_match,
            verification_match=verification_match,
            graph_execution_match=graph_execution_match,
            cache_layout_match=cache_layout_match,
            memory_model_match=memory_model_match,
            hardware_topology_match=hardware_topology_match,
            details=MappingProxyType(details)
        )
