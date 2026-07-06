from omlx.framework.model_intelligence.diffusion import DiffusionCapabilityExtractor

def test_diffusion_extractor():
    extractor = DiffusionCapabilityExtractor()
    sd_metadata = {
        "architecture": "stable-diffusion",
        "denoiser_type": "epsilon",
        "latent_info": {"channels": 4, "height": 64, "width": 64},
        "conditioning_info": {"cfg_supported": True, "text_supported": True, "image_supported": False},
        "supported_schedulers": ["ddim", "euler"]
    }
    descriptor = extractor.extract(sd_metadata)
    assert descriptor is not None
    assert descriptor.architecture == "stable-diffusion"

    llama_metadata = {"architecture": "LlamaForCausalLM", "model_type": "llama"}
    assert extractor.extract(llama_metadata) is None
