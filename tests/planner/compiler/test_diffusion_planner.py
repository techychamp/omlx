from omlx.planner.domains.diffusion import (
    DiffusionPlanner, DiffusionDescriptor, LatentDescriptor, ConditioningDescriptor,
    TimestepDescriptor, DiffusionRequirement, DiffusionPlan
)

def test_diffusion_planning_domain():
    planner = DiffusionPlanner()
    descriptor = DiffusionDescriptor(
        architecture="stable-diffusion",
        denoiser_type="epsilon",
        latent=LatentDescriptor(channels=4, height=64, width=64),
        conditioning=ConditioningDescriptor(support_classifier_free_guidance=True, text_conditioning=True, image_conditioning=False),
        supported_schedulers=["ddim", "euler"]
    )
    requirement = DiffusionRequirement(
        timestep_descriptor=TimestepDescriptor(num_inference_steps=20, scheduler_type="ddim"),
        conditioning_descriptor=descriptor.conditioning
    )
    plan = planner.plan(descriptor, requirement)
    assert isinstance(plan, DiffusionPlan)
    assert len(plan.timestep_schedule) == 20
    assert plan.validation.is_valid
