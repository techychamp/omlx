from omlx.compiler.operators.standard import Attention

def test_attention_operator():
    op = Attention(name="attn", inputs=["x"], outputs=["y"])
    assert op.name == "attn"
    assert op.inputs == ["x"]
    assert op.outputs == ["y"]
    assert op.memory_estimate() == 0
