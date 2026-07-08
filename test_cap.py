import logging
logging.basicConfig(level=logging.DEBUG)

from omlx.capabilities.resolver import CapabilityResolver
resolver = CapabilityResolver()
try:
    desc = resolver.resolve(model_descriptor={"model_id": "test"})
    print("Resolved:", desc)
except Exception as e:
    print("Error:", e)
