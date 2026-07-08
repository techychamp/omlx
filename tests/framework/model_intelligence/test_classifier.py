from omlx.framework.model_intelligence.classifier import ModelClassifier

def test_classifier():
    classifier = ModelClassifier()

    # Test Llama
    config = {"architecture": "LlamaForCausalLM", "model_type": "llama"}
    arch = classifier.classify_architecture(config)
    assert arch == "Transformer"
    family = classifier.classify_family(config, arch)
    assert family == "Autoregressive"
    task = classifier.classify_task(config, family)
    assert task == "Text-Generation"
    modality = classifier.classify_modality(family, task)
    assert modality == "Text"

    # Test Vision
    config = {"architecture": "LlavaForCausalLM", "model_type": "llava"}
    arch = classifier.classify_architecture(config)
    family = classifier.classify_family(config, arch)
    assert family == "Vision-Language"
    task = classifier.classify_task(config, family)
    assert task == "Multimodal"
    modality = classifier.classify_modality(family, task)
    assert modality == "Text+Image"

    # Test MoE
    config = {"architecture": "MixtralForCausalLM", "model_type": "mixtral", "num_experts": 8}
    arch = classifier.classify_architecture(config)
    family = classifier.classify_family(config, arch)
    assert family == "Mixture of Experts"

    # Test Diffusion
    config = {"architecture": "UNet", "model_type": "diffusion"}
    arch = classifier.classify_architecture(config)
    assert arch == "UNet"
    family = classifier.classify_family(config, arch)
    assert family == "Diffusion"
