from typing import Dict, List, Optional, Type
from pydantic import BaseModel, Field

class ModuleInfo(BaseModel):
    id: str
    name: str
    description: str
    icon: Optional[str] = None
    route: str

class WorkbenchModule:
    def __init__(self, info: ModuleInfo):
        self.info = info

    def render(self) -> str:
        return f"[{self.info.id}] {self.info.name} - {self.info.description}"

class NavigationManager:
    def __init__(self):
        self._modules: Dict[str, WorkbenchModule] = {}

    def register_module(self, module: WorkbenchModule) -> None:
        if module.info.id in self._modules:
            raise ValueError(f"Module {module.info.id} is already registered.")
        self._modules[module.info.id] = module

    def get_module(self, module_id: str) -> Optional[WorkbenchModule]:
        return self._modules.get(module_id)

    def list_modules(self) -> List[ModuleInfo]:
        return [module.info for module in self._modules.values()]
