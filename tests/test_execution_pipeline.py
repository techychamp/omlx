# SPDX-License-Identifier: Apache-2.0
"""
Tests for ExecutionPipeline state transitions.
"""

import pytest

from omlx.inference.execution_backend import (
    ExecutionPipeline, PipelineState, InvalidPipelineTransition
)


def test_pipeline_transitions():
    pipeline = ExecutionPipeline(stages=[])
    assert pipeline.state == PipelineState.INITIALIZED
    
    # Valid transition to PREPARED
    pipeline.transition_to(PipelineState.PREPARED)
    assert pipeline.state == PipelineState.PREPARED
    
    # Valid transition to RUNNING
    pipeline.transition_to(PipelineState.RUNNING)
    assert pipeline.state == PipelineState.RUNNING
    
    # Valid transition to SYNCING (which maps to SYNCING in the current codebase)
    # Note: In Checkpoint A5 we will rename to SYNCHRONIZING, but for Checkpoint A4 
    # we kept the existing transition map to avoid any breakage.
    pipeline.transition_to(PipelineState.SYNCING)
    assert pipeline.state == PipelineState.SYNCING
    
    pipeline.transition_to(PipelineState.FINALIZED)
    assert pipeline.state == PipelineState.FINALIZED
    
    pipeline.transition_to(PipelineState.CLEANED)
    assert pipeline.state == PipelineState.CLEANED
    
    # Invalid transition
    with pytest.raises(InvalidPipelineTransition):
        pipeline.transition_to(PipelineState.RUNNING)
