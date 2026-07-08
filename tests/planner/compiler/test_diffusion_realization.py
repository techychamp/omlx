from types import MappingProxyType
from omlx.planner.compiler.engine import CompilerEngine
from omlx.planner.domains.bundle import PlanningBundle
from omlx.planner.domains.diffusion.artifacts.plan import DiffusionPlan
from omlx.planner.domains.diffusion.artifacts.descriptor import DiffusionDescriptor, LatentDescriptor, ConditioningDescriptor, TimestepDescriptor
from omlx.planner.domains.diffusion.artifacts.requirement import DiffusionRequirement
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType

def test_compiler_with_diffusion():
    desc = DiffusionDescriptor(
        architecture="stable-diffusion",
        denoiser_type="epsilon",
        latent=LatentDescriptor(channels=4, height=64, width=64),
        conditioning=ConditioningDescriptor(support_classifier_free_guidance=True, text_conditioning=True, image_conditioning=False),
    )
    req = DiffusionRequirement(
        timestep_descriptor=TimestepDescriptor(num_inference_steps=2, scheduler_type="ddim"),
        conditioning_descriptor=ConditioningDescriptor(support_classifier_free_guidance=True, text_conditioning=True, image_conditioning=False)
    )
    plan = DiffusionPlan(
        descriptor=desc,
        requirement=req,
        timestep_schedule=[2, 1]
    )
    bundle = PlanningBundle(diffusion_plan=plan)

    nodes = {
        "n1": IRNode(id="n1", node_type=IRNodeType.FORWARD, dependencies=()),
        "n2": IRNode(id="n2", node_type=IRNodeType.FORWARD, dependencies=("n1",)),
    }
    ir = ExecutionIR(
        nodes=MappingProxyType(nodes),
        roots=("n2",),
    )

    engine = CompilerEngine()

    physical_ir = engine.compile(ir, planning_bundle=bundle)

    assert "n1_ts_2" in physical_ir.operations
    assert "n2_ts_2" in physical_ir.operations
    assert "n1_ts_1" in physical_ir.operations
    assert "n2_ts_1" in physical_ir.operations
    assert "diffusion_latent_init" in physical_ir.operations
    assert "diffusion_conditioning" in physical_ir.operations

    assert physical_ir.operations["n1_ts_2"].dependencies == ('diffusion_latent_init', 'diffusion_conditioning')
    assert physical_ir.operations["n1_ts_1"].dependencies == ('n2_ts_2',)
