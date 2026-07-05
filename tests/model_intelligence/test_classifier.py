import pytest
from omlx.framework.model_intelligence.classifier import ModelClassifier

def test_classifier():
    classifier = ModelClassifier()

    # Test Llama
    config = {"model_type": "llama"}
    family, arch, task, modality = classifier.classify(config)
    assert arch == "Transformer"
    assert family == "Autoregressive"
    assert task == "Text-Generation"
    assert modality == "Text"

    # Test Qwen2-VL
    config = {"model_type": "qwen2_vl"}
    family, arch, task, modality = classifier.classify(config)
    assert arch == "Transformer"
    assert family == "Vision-Language"
    assert task == "Multimodal"
    assert modality == "Text+Image"

    # Test Mixtral
    config = {"model_type": "mixtral"}
    family, arch, task, modality = classifier.classify(config)
    assert arch == "Transformer"
    assert family == "Mixture of Experts"

    # Test Whisper
    config = {"model_type": "whisper"}
    family, arch, task, modality = classifier.classify(config)
    assert arch == "Transformer"
    assert family == "Audio"
    assert task == "Speech-to-Text"
    assert modality == "Audio"

    # Test UNet
    config = {"architecture": "unet", "model_type": "stable-diffusion"}
    family, arch, task, modality = classifier.classify(config)
    assert arch == "UNet"
    assert family == "Diffusion"
