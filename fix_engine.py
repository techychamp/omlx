import re

with open("omlx/inference/execution_engine.py", "r") as f:
    content = f.read()

# Remove mlx_lm imports completely
content = re.sub(r'try:\s*from mlx_lm\.generate import BatchGenerator\nexcept ImportError:\s*BatchGenerator = None', '', content)
content = re.sub(r'try:\s*from mlx_lm\.sample_utils import make_logits_processors\nexcept ImportError:\s*make_logits_processors = None', '', content)

# Rewrite TransformerExecutionEngine
new_engine_class = """class TransformerExecutionEngine(ExecutionEngine):
    \"\"\"Execution engine for standard Transformer models using standard graph execution.\"\"\"

    def __init__(self, batch_generator: Any = None):
        # batch_generator is kept for API compatibility, but we don't use mlx_lm
        self.batch_generator = batch_generator
        self._graph_execution_enabled = True

    def has_generator(self) -> bool:
        \"\"\"Check if the generator is initialized.\"\"\"
        return True # Native compiler handles this now

    def ensure_generator(self, scheduler: Any, sampling_params: Any) -> None:
        \"\"\"Initialize standard graph execution. No longer uses mlx_lm.generate.BatchGenerator.\"\"\"
        self._graph_execution_enabled = True

    def insert(self, *args: Any, **kwargs: Any) -> list[int]:
        \"\"\"Mock insert for compatibility.\"\"\"
        return [0]

    def remove(self, *args: Any, **kwargs: Any) -> None:
        \"\"\"Mock remove for compatibility.\"\"\"
        pass

    def extract_cache(self, *args: Any, **kwargs: Any) -> Any:
        \"\"\"Mock extract_cache for compatibility.\"\"\"
        return None

    def eval_cache(self) -> int:
        \"\"\"Mock eval_cache for compatibility.\"\"\"
        return 0

    def forward(self, inputs: Any = None) -> Any:
        \"\"\"Perform a single step forward pass via the compiler runtime.\"\"\"
        raise NotImplementedError("Compiler-native Runtime owns generation.")"""

content = re.sub(r'class TransformerExecutionEngine\(ExecutionEngine\):.*?def forward\(self, inputs: Any = None\) -> Any:.*?return \[\]', new_engine_class, content, flags=re.DOTALL)

with open("omlx/inference/execution_engine.py", "w") as f:
    f.write(content)
