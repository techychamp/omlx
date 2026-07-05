from omlx.plugins.descriptor import PluginDescriptor, PluginCategory, PluginCapability, PluginPermission
from omlx.plugins.context import PluginInitializationContext

def get_descriptor() -> PluginDescriptor:
    return PluginDescriptor(
        plugin_id="omlx.example.dummy_backend",
        name="Dummy Backend Plugin",
        version="1.0.0",
        author="OMLX Team",
        description="A dummy backend plugin for testing the plugin framework.",
        category=PluginCategory.BACKEND,
        capabilities=(PluginCapability.BACKEND_EXTENSION.value,),
        permissions=(PluginPermission.BACKEND_ACCESS.value,)
    )

class DummyBackendExtension:
    @property
    def extension_id(self) -> str:
        return "dummy_backend_ext"

    @property
    def capabilities(self):
        return (PluginCapability.BACKEND_EXTENSION.value,)

def initialize_plugin(context: PluginInitializationContext):
    context.register_extension(DummyBackendExtension())
