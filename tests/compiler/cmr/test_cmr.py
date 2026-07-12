from omlx.compiler.cmr.models import (
    CanonicalModelRepresentation,
    TensorDescription,
    CapabilityDescription
)

def test_cmr_serialization():
    cmr = CanonicalModelRepresentation(
        architecture="llama",
        tensor_metadata=TensorDescription(layers=32, hidden_size=4096),
        capabilities=CapabilityDescription(supported_features={"chat", "embeddings"})
    )

    data = cmr.to_dict()
    assert data["architecture"] == "llama"
    assert data["tensor_metadata"]["layers"] == 32
    assert "chat" in data["capabilities"]["supported_features"]
    assert "embeddings" in data["capabilities"]["supported_features"]
    assert data["version"] == 1
    assert data["generator"] == "omlx.compiler"

    cmr2 = CanonicalModelRepresentation.from_dict(data)
    assert cmr2.architecture == "llama"
    assert cmr2.tensor_metadata.layers == 32
    assert cmr2.capabilities.supported_features == {"chat", "embeddings"}
    assert cmr2.version == 1
