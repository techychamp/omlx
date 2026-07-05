from omlx.compiler.framework.manager import PassManager
from omlx.compiler.framework.passes import BasePass, PassCategory, AnalysisPass

class TestPass(AnalysisPass):
    @property
    def name(self): return "test"
    @property
    def category(self): return PassCategory.ANALYSIS
    def analyze(self, art): return {"a": 1}

pm = PassManager("LogicalIR")
pm.register(TestPass())
print(pm.schedule())
