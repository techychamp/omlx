from verification.scripts.utils import GoldenLoader, ArtifactSerializer, ArtifactDiff, GoldenComparator

d1 = {"a": 1, "b": {"c": 2}, "d": 3}
d2 = {"a": 1, "b": {"c": 3}, "e": 4}

diff = GoldenComparator.compare(d1, d2)
assert diff.has_differences()
assert diff.added == {"d": 3}
assert diff.removed == {"e": 4}
assert diff.changed == {"b.c": {"actual": 2, "expected": 3}}
print("Tests passed!")
