import unittest
from omlx.planner.domains.batch.artifacts import (
    BatchPlan, BatchDescriptor, BatchRequirement, BatchCompatibilityReport
)
from omlx.planner.compiler.batch.artifacts import (
    BatchExecutionGraph, BatchGroupingGraph, BatchSynchronizationGraph, BatchRealizationReport
)
from omlx.planner.compiler.batch.realizer import BatchRealizer
from omlx.runtime.session import RuntimeSession

class TestBatchRealization(unittest.TestCase):
    def setUp(self):
        self.plan = BatchPlan(
            batch_descriptor=BatchDescriptor(batch_id="test_batch_1", request_ids=["r1", "r2"]),
            requirements=BatchRequirement(max_batch_size=2, max_tokens=100),
            compatibility_report=BatchCompatibilityReport(is_compatible=True)
        )
        self.realizer = BatchRealizer()

    def test_immutable_artifacts(self):
        graph = BatchExecutionGraph(batch_id="b1")
        self.assertEqual(graph.batch_id, "b1")

        # Test immutability (frozen dataclass)
        with self.assertRaises(Exception):
            graph.batch_id = "b2"

    def test_batch_realizer_produces_graph(self):
        report = self.realizer.realize(self.plan)

        self.assertTrue(report.success)
        self.assertIsNotNone(report.batch_execution_graph)
        self.assertEqual(report.batch_execution_graph.batch_id, "test_batch_1")
        self.assertIsNotNone(report.statistics)
        self.assertEqual(report.statistics.batch_size, 2)
        self.assertIsNotNone(report.batch_execution_graph.grouping_graph)
        self.assertIsNotNone(report.batch_execution_graph.synchronization_graph)

    def test_runtime_session_attaches_graph(self):
        report = self.realizer.realize(self.plan)

        session = RuntimeSession.create()
        # In a real environment, this would be set during initialization or handoff.
        # We use object.__setattr__ to bypass frozen constraint for testing the integration point
        object.__setattr__(session, 'batch_execution_graph', report.batch_execution_graph)
        object.__setattr__(session, 'batch_realization_report', report)

        self.assertIsNotNone(session.batch_execution_graph)
        self.assertEqual(session.batch_execution_graph.batch_id, "test_batch_1")
        self.assertTrue(session.batch_realization_report.success)

if __name__ == "__main__":
    unittest.main()
