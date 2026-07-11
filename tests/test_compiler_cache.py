import pytest
from omlx.planner.compiler.cache.manager import CompilerCacheManager
from omlx.planner.compiler.cache.invalidation import CacheInvalidationPolicy
from omlx.planner.compiler.dependency_tracker import DependencyTracker

def test_cache_put_get():
    manager = CompilerCacheManager(max_memory_bytes=1000)
    manager.put("key1", "value1", size_bytes=100, version="v1")

    cached = manager.get("key1")
    assert cached is not None
    assert cached.value == "value1"
    assert manager.hits == 1

def test_cache_eviction():
    manager = CompilerCacheManager(max_memory_bytes=150)
    manager.put("key1", "value1", size_bytes=100, version="v1")
    manager.put("key2", "value2", size_bytes=100, version="v1") # This should evict key1

    assert manager.get("key1") is None
    assert manager.get("key2").value == "value2"

def test_cache_invalidation_version():
    manager = CompilerCacheManager(max_memory_bytes=1000, compiler_version="v2")
    manager.put("key1", "value1", size_bytes=100, version="v1") # Different version

    assert manager.get("key1") is None # Should be invalidated
    assert manager.misses == 1

def test_dependency_tracker():
    tracker = DependencyTracker()
    tracker.record_dependency("A", "B")
    tracker.record_dependency("B", "C")

    downstream = tracker.get_downstream_dependencies("A")
    assert "B" in downstream
    assert "C" in downstream

    tracker.remove_node("B")
    downstream_after = tracker.get_downstream_dependencies("A")
    assert "B" not in downstream_after
    assert "C" not in downstream_after

def test_recursive_invalidation():
    tracker = DependencyTracker()
    manager = CompilerCacheManager(max_memory_bytes=1000, dependency_tracker=tracker)

    manager.put("A", "valA", 10, "v1")
    manager.put("B", "valB", 10, "v1")
    manager.put("C", "valC", 10, "v1")

    tracker.record_dependency("A", "B")
    tracker.record_dependency("B", "C")

    # Invalidate A, should also invalidate B and C
    manager.invalidate("A")

    assert manager.get("A") is None
    assert manager.get("B") is None
    assert manager.get("C") is None
