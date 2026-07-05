import pytest
from types import MappingProxyType
from omlx.planner.ir.physical.graph import PhysicalIR
from omlx.planner.ir.physical.operations import PhysicalOperation, PhysicalOperationType
from omlx.planner.ir.physical.validation import validate_physical_ir, PhysicalIRValidationError

def test_valid_physical_ir():
    ops = {
        "op1": PhysicalOperation(id="op1", operation_type=PhysicalOperationType.NOOP),
        "op2": PhysicalOperation(id="op2", operation_type=PhysicalOperationType.NOOP, dependencies=("op1",))
    }
    ir = PhysicalIR(operations=MappingProxyType(ops), roots=("op2",))
    validate_physical_ir(ir)

def test_missing_root_physical_ir():
    ops = {
        "op1": PhysicalOperation(id="op1", operation_type=PhysicalOperationType.NOOP),
    }
    ir = PhysicalIR(operations=MappingProxyType(ops), roots=("op2",))
    with pytest.raises(PhysicalIRValidationError) as exc_info:
        validate_physical_ir(ir)
    assert "Root operation 'op2' is not in operations" in str(exc_info.value)
