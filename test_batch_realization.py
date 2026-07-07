from omlx.planner.domains.batch.planner import BatchPlanner
from omlx.planner.compiler.batch.realizer import BatchRealizer

def test_batch_realization():
    planner = BatchPlanner()
    plan = planner.plan(["req_1", "req_2"])

    realizer = BatchRealizer()
    report = realizer.realize(plan)

    assert report.success
    assert report.batch_execution_graph is not None
    assert report.batch_execution_graph.batch_id == "batch_0"
    assert report.statistics is not None
    assert report.statistics.batch_size == 2
    assert report.batch_execution_graph.grouping_graph is not None
    assert report.batch_execution_graph.synchronization_graph is not None

    print("Batch realization test passed!")

if __name__ == "__main__":
    test_batch_realization()
