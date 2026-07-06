from omlx.planner.domains.diffusion import (
    DiffusionDescriptor, LatentDescriptor, ConditioningDescriptor,
    TimestepDescriptor, DiffusionRequirement, DiffusionPlan, DiffusionValidationReport
)
from omlx.runtime.generation.diffusion import DiffusionGenerationStrategy

def test_diffusion_strategy():
    descriptor = DiffusionDescriptor(
        architecture="stable-diffusion",
        denoiser_type="epsilon",
        latent=LatentDescriptor(channels=4, height=64, width=64),
        conditioning=ConditioningDescriptor(support_classifier_free_guidance=True, text_conditioning=True, image_conditioning=False),
        supported_schedulers=["ddim"]
    )
    requirement = DiffusionRequirement(
        timestep_descriptor=TimestepDescriptor(num_inference_steps=10, scheduler_type="ddim"),
        conditioning_descriptor=descriptor.conditioning
    )
    plan = DiffusionPlan(
        descriptor=descriptor,
        requirement=requirement,
        timestep_schedule=list(range(10, 0, -1)),
        denoising_plan={"type": "standard"},
        validation=DiffusionValidationReport(is_valid=True)
    )
    strategy = DiffusionGenerationStrategy(plan=plan)
    assert strategy.strategy_intent == "diffusion"
    result = strategy.generate(runtime=None, request_context=None)
    assert result["status"] == "success"
    assert result["statistics"].iteration_statistics["total_steps"] == 10
