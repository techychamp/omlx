with open("tests/plugins/test_plugin_architecture.py", "r") as f:
    content = f.read()

content = content.replace("from omlx.plugins.descriptor import PluginDescriptor, PluginCategory, PluginLifecycleState", "from omlx.plugins.descriptor import PluginDescriptor, PluginCategory, PluginLifecycleState, PluginPriority, PluginCapability")

with open("tests/plugins/test_plugin_architecture.py", "w") as f:
    f.write(content)
