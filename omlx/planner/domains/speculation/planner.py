# SPDX-License-Identifier: Apache-2.0
"""
Speculative Planning Domain.
"""

from typing import Optional, Dict, Any
from omlx.planner.domains.speculation.artifacts import SpeculativeExecutionDescriptor

class SpeculativePlanner:
    """
    Plans speculative execution strategies, creating the initial SpeculativeExecutionDescriptor.
    """

    def plan(self, descriptor: Any, execution_plan: Any, strategy_intent: Any) -> Optional[SpeculativeExecutionDescriptor]:
        """
        Creates a speculative execution plan if appropriate based on intents.
        """

        # If strategy intent asks for speculation
        if getattr(strategy_intent, 'execution_mode', '') == 'speculative' or getattr(strategy_intent, 'use_speculation', False):
            # This is mock logic for generating a SpeculativeExecutionDescriptor.
            # In real system it would extract model requirements from the execution_plan or capability descriptor.

            draft_model = getattr(strategy_intent, 'draft_model', "default_draft")
            target_model = getattr(strategy_intent, 'target_model', "default_target")
            draft_length = getattr(strategy_intent, 'draft_length', 4)

            return SpeculativeExecutionDescriptor(
                draft_model_id=draft_model,
                target_model_id=target_model,
                draft_length=draft_length
            )

        return None
