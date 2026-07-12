from omlx.compiler.importers.mlx import MLXImporter
from omlx.compiler.importers.huggingface import HuggingFaceImporter
from omlx.compiler.importers.gguf import GGUFImporter
from omlx.compiler.artifacts import CompilerArtifact

def test_mlx_importer():
    importer = MLXImporter()
    artifact = CompilerArtifact(hash="abc1234")
    cmr = importer.build_cmr("dummy_path", artifact)
    assert cmr.architecture == "mlx_stub"
    assert cmr.hash == "abc1234"

    graph = importer.generate_ir("dummy_path", cmr)
    assert len(graph.nodes) == 1
    assert "embed_node" in graph.nodes
    assert graph.hash == "abc1234"

def test_hf_importer():
    importer = HuggingFaceImporter()
    cmr = importer.build_cmr("dummy_path")
    assert cmr.architecture == "hf_stub"

    graph = importer.generate_ir("dummy_path", cmr)
    assert len(graph.nodes) == 1

def test_gguf_importer():
    importer = GGUFImporter()
    cmr = importer.build_cmr("dummy_path")
    assert cmr.architecture == "gguf_stub"

    graph = importer.generate_ir("dummy_path", cmr)
    assert len(graph.nodes) == 1
