from omlx.api.v1 import GenerationService, GenerateRequestBuilder

service = GenerationService()
req = GenerateRequestBuilder().with_model("my-model").with_prompt("Hello!").build()
response = service.generate(req)
print(response.text)
