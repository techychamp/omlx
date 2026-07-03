import re
import sys

def main():
    with open("omlx/scheduler.py", "r") as f:
        content = f.read()

    # 1. Remove _ensure_batch_generator definition
    content = re.sub(
        r'    def _ensure_batch_generator\(self, sampling_params: SamplingParams\) -> None:\n(?:        .*?\n)+',
        '',
        content
    )

    # 2. Remove _ensure_batch_generator calls
    content = re.sub(r' *self\._ensure_batch_generator\(.*?\)\n', '', content)

    # 3. Replace `if self.batch_generator is None:` or `self.batch_generator is not None` with strategy checks
    content = content.replace("if self.batch_generator is None:", "if not self._strategy_instances:")
    content = content.replace("self.batch_generator is not None", "bool(self._strategy_instances)")
    content = content.replace("self.batch_generator", "self._strategy_instances")
    
    # We already replaced .insert, .remove, .extract_cache in the previous script.
    # Let's clean up `self._emit_request_added` -> `strategy.handle(Event(...))` if that's what's needed,
    # or just keep them as method calls and implement the methods.

    with open("omlx/scheduler.py", "w") as f:
        f.write(content)

if __name__ == "__main__":
    main()
