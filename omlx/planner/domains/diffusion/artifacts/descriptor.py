from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass(frozen=True)
class TimestepDescriptor:
    """Describes the timesteps required for diffusion execution."""
    num_inference_steps: int
    scheduler_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class LatentDescriptor:
    """Describes the latent format for diffusion."""
    channels: int
    height: int
    width: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ConditioningDescriptor:
    """Describes the conditioning support for diffusion."""
    support_classifier_free_guidance: bool
    text_conditioning: bool
    image_conditioning: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DiffusionDescriptor:
    """Core descriptor for diffusion architecture."""
    architecture: str
    denoiser_type: str
    latent: LatentDescriptor
    conditioning: ConditioningDescriptor
    supported_schedulers: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
