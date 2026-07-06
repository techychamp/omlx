from typing import Any, Dict, Optional
from omlx.planner.domains.diffusion import (
    DiffusionDescriptor,
    LatentDescriptor,
    ConditioningDescriptor
)

class DiffusionCapabilityExtractor:
    """
    Model Intelligence component that identifies diffusion capabilities.
    Extracts metadata into a DiffusionDescriptor.
    """

    def extract(self, model_metadata: Dict[str, Any]) -> Optional[DiffusionDescriptor]:
        """
        Extracts diffusion capabilities from generic model metadata.
        """
        if model_metadata.get("architecture") not in ["stable-diffusion", "dit", "diffusion-gemma"]:
            return None

        latent_info = model_metadata.get("latent_info", {})
        conditioning_info = model_metadata.get("conditioning_info", {})

        return DiffusionDescriptor(
            architecture=model_metadata.get("architecture", "unknown"),
            denoiser_type=model_metadata.get("denoiser_type", "epsilon"),
            latent=LatentDescriptor(
                channels=latent_info.get("channels", 4),
                height=latent_info.get("height", 64),
                width=latent_info.get("width", 64)
            ),
            conditioning=ConditioningDescriptor(
                support_classifier_free_guidance=conditioning_info.get("cfg_supported", True),
                text_conditioning=conditioning_info.get("text_supported", True),
                image_conditioning=conditioning_info.get("image_supported", False)
            ),
            supported_schedulers=model_metadata.get("supported_schedulers", ["ddim", "euler"])
        )
