from omlx.api.v1 import ModelService, ModelLoadBuilder

service = ModelService()
req = ModelLoadBuilder().with_model_id("mlx-community/Llama-3").build()
service.load_model(req)
