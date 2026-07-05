import string
import random

class RandomGenerator:
    @staticmethod
    def random_string(length: int = 10) -> str:
        return ''.join(random.choices(string.ascii_letters, k=length))

    @staticmethod
    def random_dict(keys=5, value_length=10) -> dict:
        return {RandomGenerator.random_string(5): RandomGenerator.random_string(value_length) for _ in range(keys)}

class DescriptorGenerator:
    @staticmethod
    def generate_capability_descriptor():
        from omlx.capabilities.resolver import CapabilityResolver
        # Minimal mock logic for generating descriptions if needed by testing tools
        return {"id": RandomGenerator.random_string(), "type": "mock_capability"}

class FailureInjector:
    @staticmethod
    def inject_failure(obj, method_name, exception_to_raise):
        """Replaces a method on an object with a method that always raises."""
        def failing_method(*args, **kwargs):
            raise exception_to_raise
        setattr(obj, method_name, failing_method)
        return obj

class GoldenComparator:
    @staticmethod
    def compare(actual, expected):
        # We can implement a deep recursive dictionary/list compare if we need to
        if type(actual) != type(expected):
            return False
        if isinstance(actual, dict):
            if actual.keys() != expected.keys():
                return False
            for k in actual:
                if not GoldenComparator.compare(actual[k], expected[k]):
                    return False
            return True
        elif isinstance(actual, list):
            if len(actual) != len(expected):
                return False
            for a, e in zip(actual, expected):
                if not GoldenComparator.compare(a, e):
                    return False
            return True
        else:
            return actual == expected
