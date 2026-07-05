import pytest
import time
import threading
from typing import Any
from dataclasses import dataclass
from omlx.compiler_perf.keys import CacheKey
from omlx.compiler_perf.entries import CacheEntry
from omlx.compiler_perf.policies import LRUPolicy, LFUPolicy, FIFOPolicy, TTLPolicy
from omlx.compiler_perf.cache import CompilerCache, CapabilityCache
from omlx.compiler_perf.manager import CacheManager
from omlx.compiler_perf.diagnostics import CacheDiagnostics
from omlx.compiler_perf.diagnostics import CacheDiagnostics
from omlx.compiler_perf.benchmark import CompilerBenchmarkSuite
from omlx.compiler_perf.profiler import Profiler

@dataclass
class MockDescriptor:
    model: str
    version: str

def test_cache_keys_deterministic():
    key1 = CacheKey(model="gpt2", flags={"a": 1, "b": 2}, desc=MockDescriptor("x", "1"))
    key2 = CacheKey(model="gpt2", desc=MockDescriptor("x", "1"), flags={"b": 2, "a": 1})
    assert key1.compute_hash() == key2.compute_hash()

def test_cache_keys_immutable_avoid_identity():
    list1 = [1, 2, 3]
    list2 = [1, 2, 3]
    key1 = CacheKey(l=list1)
    key2 = CacheKey(l=list2)
    assert key1.compute_hash() == key2.compute_hash()

def test_cache_entry_immutability():
    entry = CacheEntry(key="123", compiled_object="test")
    with pytest.raises(Exception):
        entry.hit_count = 1  # Should be frozen

def test_cache_entry_with_hit():
    entry = CacheEntry(key="123", compiled_object="test")
    hit_entry = entry.with_hit()
    assert hit_entry.hit_count == 1
    assert hit_entry.key == entry.key
    assert hit_entry.compiled_object == entry.compiled_object

def test_lru_policy():
    policy = LRUPolicy()
    entries = {
        "k1": CacheEntry("k1", "o1", last_access=100),
        "k2": CacheEntry("k2", "o2", last_access=200),
    }
    assert policy.evict(entries) == "k1"

def test_lfu_policy():
    policy = LFUPolicy()
    entries = {
        "k1": CacheEntry("k1", "o1", hit_count=5),
        "k2": CacheEntry("k2", "o2", hit_count=2),
    }
    assert policy.evict(entries) == "k2"

def test_fifo_policy():
    policy = FIFOPolicy()
    entries = {
        "k1": CacheEntry("k1", "o1", creation_timestamp=100),
        "k2": CacheEntry("k2", "o2", creation_timestamp=200),
    }
    assert policy.evict(entries) == "k1"

def test_ttl_policy():
    policy = TTLPolicy(ttl_seconds=1.0)
    now = time.time()
    entries = {
        "k1": CacheEntry("k1", "o1", creation_timestamp=now - 2.0), # expired
        "k2": CacheEntry("k2", "o2", creation_timestamp=now),       # fresh
    }
    assert policy.evict(entries) == "k1"

def test_compiler_cache_put_get():
    cache = CapabilityCache()
    cache.put("k1", "v1")
    assert cache.get("k1") == "v1"
    assert cache.get("k2") is None

def test_compiler_cache_eviction():
    cache = CapabilityCache(max_size=2, diagnostics=CacheDiagnostics())
    cache.put("k1", "v1")
    cache.put("k2", "v2")
    cache.put("k3", "v3") # Should evict k1 (LRU by default)
    assert cache.get("k1") is None
    assert cache.get("k2") == "v2"
    assert cache.get("k3") == "v3"
    assert cache.diagnostics.get_snapshot()["capability_cache"]["evictions"] == 1

def test_cache_manager():
    manager = CacheManager()
    manager.capability.put("k1", "v1")
    manager.plan.put("p1", "pv1")

    assert manager.capability.get("k1") == "v1"
    assert manager.plan.get("p1") == "pv1"

    manager.clear_all()
    assert manager.capability.get("k1") is None

def test_thread_safety():
    cache = CapabilityCache(max_size=100, diagnostics=CacheDiagnostics())

    def worker(i):
        for j in range(100):
            cache.put(f"k{i}_{j}", f"v{i}_{j}")
            cache.get(f"k{i}_{j}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert cache.diagnostics.get_snapshot()["capability_cache"]["hits"] == 1000

def test_benchmark_suite():
    suite = CompilerBenchmarkSuite()
    def mock_stage():
        time.sleep(0.01)

    suite.add_benchmark("test_stage", mock_stage, iterations=2)
    report = suite.get_report()

    assert "test_stage" in report
    assert report["test_stage"]["iterations"] == 2
    assert report["test_stage"]["avg_time_ms"] >= 10.0

def test_profiler():
    def mock_stage():
        return [i for i in range(100000)]

    result = Profiler.profile("test_stage", mock_stage)
    assert result.name == "test_stage"
    assert result.peak_memory_bytes > 0
    assert result.wall_time_ms > 0
