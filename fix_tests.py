import re

with open('tests/test_compiler_perf.py', 'r') as f:
    content = f.read()

# Fix 1: Pass diagnostics to CapabilityCache in test_compiler_cache_eviction
content = re.sub(
    r'cache = CapabilityCache\(max_size=2\)',
    'cache = CapabilityCache(max_size=2, diagnostics=CacheDiagnostics())',
    content
)

# Fix 2: Pass diagnostics to CapabilityCache in test_thread_safety
content = re.sub(
    r'cache = CapabilityCache\(max_size=100\)',
    'cache = CapabilityCache(max_size=100, diagnostics=CacheDiagnostics())',
    content
)

# Fix 3: Need to import CacheDiagnostics
content = re.sub(
    r'from omlx\.compiler_perf\.manager import CacheManager',
    'from omlx.compiler_perf.manager import CacheManager\nfrom omlx.compiler_perf.diagnostics import CacheDiagnostics',
    content
)

with open('tests/test_compiler_perf.py', 'w') as f:
    f.write(content)
