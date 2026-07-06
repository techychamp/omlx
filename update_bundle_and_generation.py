with open("omlx/planner/bundle.py", "r") as f:
    content = f.read()

if "from omlx.planner.domains.batch.artifacts import BatchPlan" not in content:
    content = content.replace(
        "from omlx.planner.device.artifacts import DevicePlan",
        "from omlx.planner.device.artifacts import DevicePlan\nfrom omlx.planner.domains.batch.artifacts import BatchPlan"
    )

if "batch_plan: Optional[BatchPlan] = None" not in content:
    content = content.replace(
        "verification_plan: Optional[VerificationPlan] = None",
        "verification_plan: Optional[VerificationPlan] = None\n    batch_plan: Optional[BatchPlan] = None"
    )

with open("omlx/planner/bundle.py", "w") as f:
    f.write(content)

with open("omlx/runtime/generation/__init__.py", "r") as f:
    content = f.read()

if "BatchGenerationStrategy" not in content:
    content = content.replace(
        "from .speculative import SpeculativeGenerationStrategy",
        "from .speculative import SpeculativeGenerationStrategy\nfrom .batch import BatchGenerationStrategy"
    )
    content = content.replace(
        '"SpeculativeGenerationStrategy",',
        '"SpeculativeGenerationStrategy",\n    "BatchGenerationStrategy",'
    )

with open("omlx/runtime/generation/__init__.py", "w") as f:
    f.write(content)
