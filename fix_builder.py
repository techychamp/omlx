import re

with open("omlx/runtime/builder.py", "r") as f:
    content = f.read()

# Fix 1: temperature to sampler
content = content.replace("next_token, token_text = self._sample_token(execution_result, temperature, mx)", "next_token, token_text = self._sample_token(execution_result, sampler, mx)")

# Fix 2: track_event to observe_phase
old_except = """                except Exception as e:
                    self.streaming_controller.complete_session(session.session_id, StreamCompletion.ERROR, e)
                    get_observer().track_event("ExecutionError", {"error": str(e)})"""

new_except = """                except Exception as e:
                    self.streaming_controller.complete_session(session.session_id, StreamCompletion.ERROR, e)
                    with get_observer().observe_phase("Execution", "Runtime", "generate_error"):
                        pass
                    import logging
                    logger = logging.getLogger("omlx.runtime")
                    logger.error(f"ExecutionError in generation loop: {e}")"""
content = content.replace("    " + old_except.replace("\n", "\n    "), "    " + new_except.replace("\n", "\n    "))
content = content.replace(old_except, new_except)

with open("omlx/runtime/builder.py", "w") as f:
    f.write(content)
